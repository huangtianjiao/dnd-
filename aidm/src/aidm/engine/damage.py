"""伤害结算引擎 — 伤害掷骰 / 抗性·易伤·免疫 / HP / 死亡豁免 / 治疗。

依赖 engine.dice（roll_dice/round_down/roll_die）。不含检定（见 check.py）。
标注规则ID+出处。
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field

from . import dice

# ──────────────────────────────────────────────────────────────────────────
# 伤害类型（统一中文，与规则书原文一致）
# ──────────────────────────────────────────────────────────────────────────

# 规则: 术语汇编/伤害与治疗.txt + DM速查/伤害类型.txt — 共 13 种伤害类型
# 出处: topics/玩家手册2024/进行游戏/伤害类型.htm
DAMAGE_TYPES = frozenset({
    "强酸", "钝击", "寒冷", "火焰", "力场", "闪电",
    "暗蚀", "穿刺", "毒素", "心灵", "光耀", "挥砍", "雷鸣",
})

# 英文→中文映射（兼容旧代码/外部输入用英文的情况）
_EN_TO_ZH = {
    "acid": "强酸", "bludgeoning": "钝击", "cold": "寒冷", "fire": "火焰",
    "force": "力场", "lightning": "闪电", "necrotic": "暗蚀",
    "piercing": "穿刺", "poison": "毒素", "psychic": "心灵",
    "radiant": "光耀", "slashing": "挥砍", "thunder": "雷鸣",
}


def normalize_damage_type(dt: str) -> str:
    """将伤害类型标准化为中文。英文输入自动转中文，已中文则原样返回。

    规则: 术语汇编/伤害与治疗.txt（13 种伤害类型）
    """
    if not dt:
        return ""
    dt = dt.strip().lower()
    return _EN_TO_ZH.get(dt, dt)


# ──────────────────────────────────────────────────────────────────────────
# 伤害管线
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class DamageRequest:
    """一次伤害掷骰请求。"""
    dice_expr: str                       # 骰子部分，如 "1d8"（武器）或 "8d6"（火球术）
    damage_type: str                     # 伤害类型，如 "piercing"/"fire"
    ability_mod: int = 0                 # 武器伤害加的属性调整值（R-DMG-001）
    add_mod: bool = False               # 是否加 ability_mod（武器 True，法术按其说明）
    crit: bool = False                  # 重击：骰数翻倍（R-CMB-029）
    flat_modifiers: list[int] = field(default_factory=list)  # 数值加/减（如灵光 -5）


@dataclass
class DamageResult:
    raw: int                            # 骰子（+属性调整值）原始合计
    final: int                          # 经管线后的最终伤害
    damage_type: str
    immune: bool = False
    resisted: bool = False
    vulnerable: bool = False
    dice_rolls: list[int] = field(default_factory=list)
    modifier: int = 0
    crit: bool = False


def apply_damage_pipeline(
    raw: int,
    damage_type: str,
    flat_modifiers: Iterable[int] = (),
    resistances: Iterable[str] = (),
    vulnerabilities: Iterable[str] = (),
    immunities: Iterable[str] = (),
) -> DamageResult:
    """按固定顺序结算伤害：免疫→数值修正→一项抗性→一项易伤→下限0。

    规则: R-QCK-002 顺序（=R-DMG-005）+ R-DMG-006免疫 + R-DMG-003抗性易伤 +
          R-DMG-004 抗性易伤不叠加（各只一项）+ R-DMG-002 下限0
    出处: topics/玩家手册2024/进行游戏/抗性和易伤.htm ; topics/速查/DM速查/抗性与易伤.htm
    官方算例: 28火焰, -5灵光, 全伤害抗性, 火焰易伤 → (28-5)=23 → floor(23/2)=11 → 11×2=22
    说明: resistances/vulnerabilities/immunities 中 "*" 代表"全伤害"（通配）。
          伤害类型自动标准化为中文（见 normalize_damage_type）。
    """
    damage_type = normalize_damage_type(damage_type)
    resistances = {normalize_damage_type(r) for r in resistances}
    vulnerabilities = {normalize_damage_type(v) for v in vulnerabilities}
    immunities = {normalize_damage_type(i) for i in immunities}

    # R-DMG-006 / R-QCK-002 step1: 免疫 → 0
    if damage_type in immunities or "*" in immunities:
        return DamageResult(raw=raw, final=0, damage_type=damage_type, immune=True)

    # R-QCK-002 step2: 数值修正（加值/减值）
    flat_sum = sum(flat_modifiers)
    dmg = raw + flat_sum

    # R-DMG-003 / R-QCK-002 step3: 一项抗性（减半，向下取整）
    resisted = damage_type in resistances or "*" in resistances
    if resisted:
        dmg = dice.round_down(dmg / 2)

    # R-DMG-003 / R-QCK-002 step4: 一项易伤（翻倍）
    vulnerable = damage_type in vulnerabilities or "*" in vulnerabilities
    if vulnerable:
        dmg = dmg * 2

    # R-DMG-002 伤害下限为 0
    dmg = max(0, dmg)
    return DamageResult(raw=raw, final=dmg, damage_type=damage_type,
                        resisted=resisted, vulnerable=vulnerable, modifier=flat_sum)


def roll_damage(
    req: DamageRequest,
    *,
    resistances: Iterable[str] = (),
    vulnerabilities: Iterable[str] = (),
    immunities: Iterable[str] = (),
) -> DamageResult:
    """掷伤害骰并跑管线。

    规则: R-DMG-001 伤害掷骰构成（武器=sum(dice)+属性调整值；法术按说明；定值不加属性）
          R-CMB-029 重击骰数翻倍（常数不加倍，由 dice.roll_dice 的 crit 处理）
    出处: topics/玩家手册2024/进行游戏/伤害掷骰.htm ; 重击.htm
    """
    roll = dice.roll_dice(req.dice_expr, crit=req.crit)   # R-CHK-025 + R-CMB-029
    mod = req.ability_mod if req.add_mod else 0            # R-DMG-001 武器加属性调整值
    raw = roll.total + mod
    res = apply_damage_pipeline(raw, req.damage_type,
                                req.flat_modifiers, resistances, vulnerabilities, immunities)
    res.dice_rolls = roll.dice_rolls
    res.modifier = mod + sum(req.flat_modifiers)
    res.crit = req.crit
    return res


def resolve_stat_block(notation: str, mode: str = "roll") -> int:
    """数据卡伤害记法 "4(1d4+2)"：DM 择一使用固定值或掷骰，不可并用。

    规则: R-GLS-086 数据卡固定值/掷骰表达式
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    mode: "fixed" → 取括号前固定值；"roll" → 掷括号内表达式。
    """
    m = re.match(r"^\s*(\d+)\s*\(([^)]+)\)\s*$", notation)
    if not m:
        # 无括号 → 当作普通表达式
        return dice.roll_dice(notation).total if mode == "roll" else int(notation)
    fixed, expr = int(m.group(1)), m.group(2)
    if mode == "fixed":
        return fixed
    return dice.roll_dice(expr).total


# ──────────────────────────────────────────────────────────────────────────
# HP / 临时HP / 死亡
# ──────────────────────────────────────────────────────────────────────────

def apply_damage_to_hp(hp: int, temp_hp: int, max_hp: int, dmg: int) -> tuple[int, int]:
    """受伤害：先扣临时HP，余下扣真正HP（不低于0）。

    返回 (new_hp, new_temp_hp)。
    规则: R-DMG-009 临时HP优先扣除 + R-DMG-007 HP扣除 + R-GLS-085 HP边界[0,max]
    出处: topics/玩家手册2024/进行游戏/临时生命值.htm ; 生命值.htm
    算例: 5临时HP 受7伤 → 失5临时再失2HP
    """
    remaining = dmg
    if temp_hp > 0:                                    # R-DMG-009 临时HP先扣
        absorbed = min(temp_hp, remaining)
        temp_hp -= absorbed
        remaining -= absorbed
    hp = max(0, hp - remaining)                        # R-DMG-007 + R-GLS-085 不低于0
    return hp, temp_hp


def grant_temp_hp(current_temp: int, new_temp: int) -> int:
    """临时HP不叠加，取较大者。

    规则: R-DMG-010 临时HP不叠加  出处: 临时生命值.htm
    """
    return max(current_temp, new_temp)


def apply_healing(hp: int, max_hp: int, heal: int) -> int:
    """治疗：加到当前HP，不超过上限。

    规则: R-DMG-020 治疗与生命值上限  出处: 治疗.htm
    算例: cur14 heal8 max20 → min(20,22)=20
    """
    return min(max_hp, hp + heal)


def check_massive_damage(current_hp: int, max_hp: int, dmg: int) -> bool:
    """过量伤害致死：伤害将HP降至0且余量≥HP上限则立即死亡。

    规则: R-DMG-014 即刻毙命-过量伤害  出处: 生命值降至0点.htm
    算例: max12 cur6 dmg18 → 18≥6, overflow=12, 12≥12 → 死亡
    """
    if dmg >= current_hp:
        overflow = dmg - current_hp
        if overflow >= max_hp:
            return True
    return False


def check_hp_max_zero_death(max_hp: int) -> bool:
    """HP上限归0则死亡。规则: R-DMG-013  出处: 生命值降至0点.htm"""
    return max_hp <= 0


@dataclass
class DeathTracker:
    """死亡豁免计数器（持久化于角色卡）。"""
    successes: int = 0
    failures: int = 0
    stable: bool = False
    dead: bool = False

    def reset(self) -> None:
        self.successes = 0
        self.failures = 0


def death_save(tracker: DeathTracker) -> dict:
    """死亡豁免检定：1d20（无属性）；≥10记成功，否则失败；3成功稳定/3失败死亡；
    天然1记两次失败，天然20恢复1HP并归零。

    规则: R-DMG-017 死亡豁免检定（R-GLS-020 触发：回合开始HP=0）
    出处: topics/玩家手册2024/进行游戏/生命值降至0点.htm
    """
    if tracker.stable or tracker.dead:
        return {"roll": None, "skipped": True, "stable": tracker.stable, "dead": tracker.dead}
    roll = dice.roll_die(20)
    result = {"roll": roll, "regain_hp": 0, "stable": False, "dead": False}
    if roll == 1:                                     # R-DMG-017 天然1 → 两次失败
        tracker.failures += 2
    elif roll == 20:                                   # R-DMG-017 天然20 → 恢复1HP，计数归零
        result["regain_hp"] = 1
        tracker.reset()
    elif roll >= 10:                                  # ≥10 → 一次成功
        tracker.successes += 1
    else:                                             # 否则 → 一次失败
        tracker.failures += 1
    if tracker.successes >= 3:                         # R-DMG-017 3成功 → 稳定（计数归零）
        tracker.stable = True
        tracker.reset()
        result["stable"] = True
    if tracker.failures >= 3:                           # R-DMG-017 3失败 → 死亡（保留计数供审计）
        tracker.dead = True
        result["dead"] = True
    result["successes"] = tracker.successes
    result["failures"] = tracker.failures
    return result


def damage_at_zero_hp(tracker: DeathTracker, dmg: int, is_crit: bool, max_hp: int) -> dict:
    """HP为0时受伤害：记死亡豁免失败（重击记两次）；伤害≥上限则死亡。

    规则: R-DMG-018 生命值0时受伤害  出处: 生命值降至0点.htm
    """
    if tracker.stable:                                # 受伤害则失去稳定
        tracker.stable = False
    if dmg >= max_hp:                                  # R-DMG-018 ≥上限 → 死亡
        tracker.dead = True
        return {"dead": True, "failures_added": 0}
    added = 2 if is_crit else 1                        # R-DMG-018 重击记两次失败
    tracker.failures += added
    if tracker.failures >= 3:
        tracker.dead = True
    return {"dead": tracker.dead, "failures_added": added, "failures": tracker.failures}


def reset_death_counts_on_recovery(tracker: DeathTracker) -> None:
    """恢复任意HP（含他人治疗）时死亡豁免计数归零并解除昏迷。

    规则: R-ADD-008（审计补遗）死亡豁免计数受治疗归零  出处: 生命值降至0点.htm
    """
    tracker.reset()
    tracker.stable = False
    tracker.dead = False


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 伤害类型标准化
    assert normalize_damage_type("fire") == "火焰"
    assert normalize_damage_type("piercing") == "穿刺"
    assert normalize_damage_type("火焰") == "火焰"
    assert len(DAMAGE_TYPES) == 13
    # R-QCK-002 官方算例: 28火焰 -5灵光 全抗 火易伤 → 22
    r = apply_damage_pipeline(28, "fire", [-5], resistances={"*"}, vulnerabilities={"fire"})
    assert r.final == 22, r  # 英文输入也能正确匹配抗性/易伤
    # 免疫 → 0
    assert apply_damage_pipeline(28, "火焰", immunities={"火焰"}).final == 0
    # 抗性减半向下取整
    assert apply_damage_pipeline(10, "火焰", resistances={"火焰"}).final == 5
    assert apply_damage_pipeline(11, "火焰", resistances={"火焰"}).final == 5  # floor(5.5)=5
    # 易伤翻倍
    assert apply_damage_pipeline(10, "火焰", vulnerabilities={"火焰"}).final == 20
    # 下限0
    assert apply_damage_pipeline(3, "火焰", [-10]).final == 0
    # roll_damage 范围（匕首1d4+力3）
    rd = roll_damage(DamageRequest("1d4", "穿刺", ability_mod=3, add_mod=True))
    assert 4 <= rd.final <= 7 and len(rd.dice_rolls) == 1
    # 重击骰翻倍（R-CMB-029）
    rc = roll_damage(DamageRequest("2d6", "挥砍", crit=True))
    assert len(rc.dice_rolls) == 4
    # 临时HP优先扣（R-DMG-009）
    assert apply_damage_to_hp(10, 5, 20, 7) == (8, 0)   # 失5临时再失2HP → 8,0
    assert apply_damage_to_hp(10, 5, 20, 3) == (10, 2)
    # 临时HP取大（R-DMG-010）
    assert grant_temp_hp(10, 12) == 12
    # 治疗（R-DMG-020）
    assert apply_healing(14, 20, 8) == 20
    # 过量伤害致死（R-DMG-014）
    assert check_massive_damage(6, 12, 18) is True
    assert check_massive_damage(6, 12, 10) is False
    # 死亡豁免（monkeypatch roll）
    orig = dice.roll_die
    t = DeathTracker()
    dice.roll_die = lambda s: 15
    death_save(t); assert t.successes == 1
    dice.roll_die = lambda s: 5
    death_save(t); assert t.failures == 1
    dice.roll_die = lambda s: 20
    res = death_save(t); assert res["regain_hp"] == 1 and t.successes == 0 and t.failures == 0
    dice.roll_die = lambda s: 1
    death_save(t); assert t.failures == 2
    dice.roll_die = lambda s: 5
    death_save(t); assert t.failures >= 3 and t.dead is True
    dice.roll_die = orig
    # HP0受伤害（R-DMG-018）
    t2 = DeathTracker()
    res = damage_at_zero_hp(t2, 5, False, 20); assert res["failures_added"] == 1
    res = damage_at_zero_hp(t2, 5, True, 20); assert res["failures_added"] == 2  # 重击两次
    assert damage_at_zero_hp(DeathTracker(), 25, False, 20)["dead"] is True     # ≥上限死
    # 数据卡记法（R-GLS-086）
    assert resolve_stat_block("4(1d4+2)", "fixed") == 4
    dice.roll_dice = lambda expr, *, crit=False: type("R", (), {"total": 6, "dice_rolls": []})()
    assert resolve_stat_block("4(1d4+2)", "roll") == 6
    print("[damage] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
