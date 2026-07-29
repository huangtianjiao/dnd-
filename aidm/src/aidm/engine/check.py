"""D20 检定引擎 — 属性检定 / 豁免 / 攻击命中。

依赖 engine.dice（骰子）。本模块负责"掷 d20 → 加调整值 → 比 DC/AC"的判定，
不含伤害结算（见 damage.py）。天然 20/1 的特殊效果仅对攻击检定（本模块）
和死亡豁免（damage.py）生效；属性检定与豁免检定的天然 20/1 无特殊效果
（R-DM-010）。

标注约定：每条规则实现处标注 RULE_SPEC.md 规则点 ID + 原文出处路径。
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from . import dice

# ──────────────────────────────────────────────────────────────────────────
# DC 设定
# ──────────────────────────────────────────────────────────────────────────

# R-CHK-009 范例难度等级 DC 表
# 出处: topics/玩家手册2024/进行游戏/属性检定.htm
_DC_BY_LABEL = {
    "非常容易": 5, "容易": 10, "中等": 15,
    "困难": 20, "非常困难": 25, "近乎不可能": 30,
}


def dc_by_label(label: str) -> int:
    """按难度描述返回范例 DC。

    规则: R-CHK-009 范例难度等级DC表
    出处: topics/玩家手册2024/进行游戏/属性检定.htm
    """
    if label not in _DC_BY_LABEL:
        raise ValueError(f"未知难度描述 {label!r}，可选: {list(_DC_BY_LABEL)}")
    return _DC_BY_LABEL[label]


def calc_save_dc(ability_mod: int, prof: int) -> int:
    """施法/特殊能力的豁免 DC = 8 + 属性调整值 + 熟练加值。

    规则: R-DM-002 计算DC公式（=R-CHK-012/R-SPL-021 法术豁免DC）
    出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/难度等级.htm
    说明: 此为公式算出的 DC，不受 R-DM-003 的 clamp(10,20) 约束（该 clamp 仅限 DM 即兴 DC）。
    """
    return 8 + ability_mod + prof


# ──────────────────────────────────────────────────────────────────────────
# 优劣势解析 / 被动检定
# ──────────────────────────────────────────────────────────────────────────

def resolve_advantage(adv_count: int, dis_count: int) -> tuple[bool, bool]:
    """统计优劣势来源数 → 解析为 (advantage, disadvantage) 布尔。

    规则: R-CHK-005 优势劣势不叠加与抵消（同时存在则抵消→只掷一d20）
          R-DM-006 优势与劣势抵消（无论数量多寡）
    出处: topics/玩家手册2024/进行游戏/优势_劣势.htm
    说明: 多个优势仍只掷两 d20（不叠加）；优劣势同时存在→抵消。
    """
    has_adv = adv_count > 0
    has_dis = dis_count > 0
    if has_adv and has_dis:        # R-CHK-005 抵消
        return (False, False)
    return (has_adv, has_dis)


def passive_check(modifiers: Iterable[int]) -> int:
    """被动检定值 = 10 + 所有适用调整值（被动察觉/被动洞悉/先攻定值）。

    规则: R-DM-012 被动检定（=R-GLS-010 被动察觉=10+感知(察觉)加值,优+5/劣-5）
    出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/属性检定.htm
    """
    return 10 + sum(modifiers)


# ──────────────────────────────────────────────────────────────────────────
# 检定结果
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class CheckResult:
    """一次 D20 检定的完整结果。"""
    success: bool               # 是否成功
    total: int                  # d20 + 调整值的总计
    d20: int                    # 实际采用的天然 d20
    rolls: list[int]            # 所有掷出的 d20（优劣势为2个）
    mode: str                   # normal/advantage/disadvantage/cancelled
    target: int                 # 目标数值（DC 或 AC）
    margin: int                 # total - target（成功为正/0，失败为负）
    modifier: int               # 调整值合计（total - d20）


def _d20_check_core(mod, prof, proficient, target, advantage, disadvantage, circ=0,
                     auto_success_on_nat20: bool = False,
                     auto_fail_on_nat1: bool = False) -> CheckResult:
    """R-CHK-001 D20 检定三步流程的内部实现。

    2024 PHB 规则: 天然 20/1 仅对攻击检定和死亡豁免有自动成功/失败效果，
    普通属性检定与豁免检定的天然 20/1 无特殊效果（R-DM-010）。
    通过 auto_success_on_nat20 / auto_fail_on_nat1 参数控制是否启用。
    """
    r = dice.roll_d20(advantage, disadvantage)        # R-CHK-004/005 优劣势
    prof_add = prof if proficient else 0              # R-CHK-016 熟练只加一次
    mod_total = mod + prof_add + circ                 # 属性调整值 + 熟练加值 + 临时加值
    total = r.used + mod_total                        # R-CHK-001 step2: 加调整值

    # 天然 20/1 自动成功/失败：仅攻击检定与死亡豁免启用
    if auto_success_on_nat20 and r.used == 20:
        success = True
    elif auto_fail_on_nat1 and r.used == 1:
        success = False
    else:
        success = total >= target                     # R-CHK-001 step3: 比目标数值（≥则成功）

    return CheckResult(
        success=success, total=total, d20=r.used,
        rolls=list(r.rolls), mode=r.mode,
        target=target, margin=total - target, modifier=mod_total,
    )


# ──────────────────────────────────────────────────────────────────────────
# 属性检定 / 豁免
# ──────────────────────────────────────────────────────────────────────────

def ability_check(mod: int, prof: int, proficient: bool, dc: int,
                  advantage: bool = False, disadvantage: bool = False,
                  circ: int = 0) -> CheckResult:
    """属性检定：d20 + 属性调整值 + (熟练加值 if 熟练) ≥ DC 则成功。

    规则: R-CHK-010 属性检定（=R-CHK-001 三步的属性检定实例）
    出处: topics/玩家手册2024/进行游戏/属性检定.htm
    """
    return _d20_check_core(mod, prof, proficient, dc, advantage, disadvantage, circ)


def saving_throw(mod: int, prof: int, proficient: bool, dc: int,
                 advantage: bool = False, disadvantage: bool = False,
                 waive: bool = False, circ: int = 0) -> CheckResult:
    """豁免检定：抵抗危险时进行；可主动放弃掷骰直接判失败。

    规则: R-CHK-011 豁免检定（可放弃 waive→直接失败）
    出处: topics/玩家手册2024/进行游戏/豁免检定.htm
    """
    # R-CHK-011: 可主动放弃掷骰 → 直接判为失败
    if waive:
        return CheckResult(success=False, total=0, d20=0, rolls=[], mode="waived",
                           target=dc, margin=-dc, modifier=0)
    return _d20_check_core(mod, prof, proficient, dc, advantage, disadvantage, circ)


# ──────────────────────────────────────────────────────────────────────────
# 攻击命中
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class AttackResult(CheckResult):
    """攻击检定结果（额外含命中/重击标志）。"""
    hit: bool = False           # 是否命中
    crit: bool = False          # 是否重击（天然 20）


def attack_roll(bonus: int, ac: int,
                advantage: bool = False, disadvantage: bool = False,
                circ: int = 0) -> AttackResult:
    """攻击检定：d20 + 命中加值 vs AC；天然 20 必出且重击，天然 1 必失手。

    规则:
      - R-CMB-017 攻击检定命中判定（≥AC则命中）
      - R-CMB-022 天然20必命中与重击（无论AC/调整值）
      - R-CMB-023 天然1必失手
      - R-DM-010 攻击天然20/1（属性/豁免天然20/1无特殊）
    出处: topics/玩家手册2024/进行游戏/攻击检定.htm
    说明: 优劣势下天然 20/1 判定基于"实际采用的骰值"（r.used）：
          优势取max→有一骰20则必出；劣势取min→两骰皆20才必出。
    """
    r = dice.roll_d20(advantage, disadvantage)        # R-CHK-004 优劣势
    nat = r.used                                       # 实际采用的 d20
    mod_total = bonus + circ
    total = nat + mod_total

    # R-CMB-022 天然 20：必命中 + 重击（忽略 AC/调整值）
    if nat == 20:
        return AttackResult(success=True, total=total, d20=nat, rolls=list(r.rolls),
                             mode=r.mode, target=ac, margin=total - ac,
                             modifier=mod_total, hit=True, crit=True)
    # R-CMB-023 天然 1：必失手（忽略 AC/调整值）
    if nat == 1:
        return AttackResult(success=False, total=total, d20=nat, rolls=list(r.rolls),
                            mode=r.mode, target=ac, margin=total - ac,
                            modifier=mod_total, hit=False, crit=False)
    # R-CMB-017 普通：total ≥ AC 则命中
    hit = total >= ac
    return AttackResult(success=hit, total=total, d20=nat, rolls=list(r.rolls),
                        mode=r.mode, target=ac, margin=total - ac,
                        modifier=mod_total, hit=hit, crit=False)


def is_natural_20(d20: int) -> bool:
    """是否天然 20（重击/必出）。规则: R-CMB-022  出处: 攻击检定.htm"""
    return d20 == 20


def is_natural_1(d20: int) -> bool:
    """是否天然 1（必失）。规则: R-CMB-023  出处: 攻击检定.htm"""
    return d20 == 1


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    assert dc_by_label("中等") == 15
    assert dc_by_label("近乎不可能") == 30
    assert calc_save_dc(3, 3) == 14          # 8+3+3
    assert resolve_advantage(0, 0) == (False, False)
    assert resolve_advantage(3, 0) == (True, False)    # 多个优势仍只掷2骰
    assert resolve_advantage(0, 2) == (False, True)
    assert resolve_advantage(1, 1) == (False, False)   # 抵消
    assert passive_check([3, 2]) == 15

    # 属性检定：固定让 d20=15（猴子补丁）
    orig = dice.roll_d20
    class _Fake:
        def __init__(s, used, rolls, mode): s.used, s.rolls, s.mode = used, rolls, mode
    dice.roll_d20 = lambda adv=False, dis=False: _Fake(15, [15], "normal")
    r = ability_check(mod=3, prof=2, proficient=True, dc=18)  # 15+3+2=20≥18
    assert r.success and r.total == 20 and r.margin == 2
    dice.roll_d20 = orig

    # 豁免放弃
    r = saving_throw(mod=0, prof=0, proficient=False, dc=15, waive=True)
    assert r.success is False and r.mode == "waived"

    # 攻击：天然20必出+重击
    dice.roll_d20 = lambda adv=False, dis=False: _Fake(20, [20], "normal")
    a = attack_roll(bonus=5, ac=30)
    assert a.hit and a.crit and a.success
    # 天然1必失
    dice.roll_d20 = lambda adv=False, dis=False: _Fake(1, [1], "normal")
    a = attack_roll(bonus=50, ac=5)
    assert not a.hit and not a.success
    # 普通：10+5=15 vs AC15 → 命中(≥)
    dice.roll_d20 = lambda adv=False, dis=False: _Fake(10, [10], "normal")
    a = attack_roll(bonus=5, ac=15)
    assert a.hit and not a.crit
    # 10+5=15 vs AC16 → 未中
    a = attack_roll(bonus=5, ac=16)
    assert not a.hit
    dice.roll_d20 = orig
    print("[check] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
