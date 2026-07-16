"""职业特性引擎 — 核心战斗特性（动作如潮、狂暴、偷袭、至圣斩等）。

管理职业特性的消耗/使用/恢复周期，提供特性效应结算函数。
配合 combat.py 的回合经济和 damage.py 的伤害管线使用。

规则依据: R-CLS-001~050 (职业核心特性);
数据来源: topics/玩家手册2024/角色职业/<职业>/<职业>.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from . import dice, check


# ══════════════════════════════════════════════════════════════════════════
# 特性使用追踪器 (Feature Tracker)
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class FeatureTracker:
    """追踪一个角色的所有职业特性使用情况。

    规则: R-CLS-003 长休恢复 / R-CLS-004 短休恢复

    用法:
        tracker = FeatureTracker(char_level=5, pb=3)
        # 野蛮人: 3次狂暴
        tracker.max_uses["rage"] = 2 if char_level < 3 else 3 if char_level < 6 else 4
        tracker.uses["rage"] = tracker.max_uses["rage"]  # 长休后恢复
    """
    char_level: int
    proficiency_bonus: int                     # 熟练加值 (R-CHK-015)

    # 可用次数 (max_uses) 和已用次数 (uses)
    max_uses: dict[str, int] = field(default_factory=lambda: {
        "rage": 0,
        "action_surge": 0,
        "second_wind": 0,
        "channel_divinity": 0,
        "bardic_inspiration": 0,
        "wild_shape": 0,
        "focus_points": 0,           # 武僧气/专注点
        "sorcery_points": 0,         # 术士术法点
    })
    uses: dict[str, int] = field(default_factory=dict)

    # 状态标记
    raging: bool = False             # 狂暴激活中
    reckless: bool = False           # 鲁莽攻击（提供攻击优势但也被攻击优势）

    def has_use(self, feature: str) -> bool:
        """检查特性是否还有使用次数。"""
        if feature not in self.max_uses:
            return False
        remaining = self.max_uses[feature] - self.uses.get(feature, 0)
        return remaining > 0

    def use(self, feature: str) -> bool:
        """消耗一次特性使用。返回是否成功。"""
        if not self.has_use(feature):
            return False
        self.uses[feature] = self.uses.get(feature, 0) + 1
        return True

    def recover(self, feature: str, amount: int = -1) -> int:
        """恢复特性使用次数。amount=-1 表示恢复全部。"""
        if feature not in self.max_uses:
            return 0
        if amount < 0:
            recovered = self.uses.get(feature, 0)
            self.uses[feature] = 0
            return recovered
        recovered = min(amount, self.uses.get(feature, 0))
        self.uses[feature] = self.uses.get(feature, 0) - recovered
        return recovered

    def remaining(self, feature: str) -> int:
        """剩余可用次数。"""
        if feature not in self.max_uses:
            return 0
        return max(0, self.max_uses[feature] - self.uses.get(feature, 0))

    def on_short_rest(self):
        """短休恢复 (R-CLS-004)。
        
        恢复: 动作如潮、引导神力、荒野形态、专注点。
        """
        self.recover("action_surge")
        self.recover("channel_divinity")
        self.recover("wild_shape")
        self.recover("focus_points")

    def on_long_rest(self):
        """长休恢复 (R-CLS-003)。
        
        恢复全部特性使用次数。
        """
        for feat in self.max_uses:
            self.recover(feat)
        self.raging = False
        self.reckless = False


# ══════════════════════════════════════════════════════════════════════════
# 战士特性
# ══════════════════════════════════════════════════════════════════════════

def action_surge(tracker: FeatureTracker) -> bool:
    """动作如潮：获得一个额外动作。

    规则: R-CLS-010 动作如潮
    出处: topics/玩家手册2024/角色职业/战士/战士.htm
    等级: 战士2级
    恢复: 短休/长休

    返回: 是否成功激活
    """
    if not tracker.use("action_surge"):
        return False
    # 注意：实际动作经济由 combat.py 管理，这里只标记次数消耗
    return True


def second_wind(
    fighter_level: int,
    con_mod: int = 0,
) -> dict:
    """回气：以附赠动作恢复HP。

    规则: R-CLS-011 回气
    出处: topics/玩家手册2024/角色职业/战士/战士.htm
    等级: 战士1级
    恢复: 短休/长休

    参数:
        fighter_level: 战士等级
        con_mod: 体质调整值 (2024版不加)

    返回: {"heal": 治疗量, "dice": 骰子表达式}
    """
    # 2024版: 恢复 1d10 + fighter_level (不再加CON)
    heal_dice = dice.roll_dice(f"1d10")
    heal = heal_dice.total + fighter_level
    return {
        "heal": heal,
        "dice": "1d10",
        "rolls": heal_dice.dice_rolls,
        "level_bonus": fighter_level,
    }


# ══════════════════════════════════════════════════════════════════════════
# 野蛮人特性
# ══════════════════════════════════════════════════════════════════════════

def rage_activate(tracker: FeatureTracker, barbarian_level: int) -> dict:
    """激活狂暴。

    规则: R-CLS-020 狂暴
    出处: topics/玩家手册2024/角色职业/野蛮人/野蛮人.htm
    等级: 野蛮人1级
    持续时间: 10分钟（除非昏迷或未攻击/未受伤害一轮）

    效果:
        - 力量检定和力量豁免具有优势
        - 近战武器力量攻击伤害+狂暴伤害加值
        - 钝击/穿刺/挥砍伤害抗性

    返回: {"success": bool, "rage_damage": int, "effects": [...]}
    """
    if tracker.raging:
        return {"success": False, "error": "已在狂暴中"}

    if not tracker.use("rage"):
        return {"success": False, "error": "无可用狂暴次数"}

    # 狂暴伤害加值 (2024版)
    if barbarian_level >= 16:
        rage_damage = 4
    elif barbarian_level >= 9:
        rage_damage = 3
    else:
        rage_damage = 2

    tracker.raging = True

    return {
        "success": True,
        "rage_damage": rage_damage,
        "effects": [
            "力量检定和力量豁免具有优势",
            f"近战力量武器攻击伤害+{rage_damage}",
            "钝击/穿刺/挥砍伤害抗性",
        ],
    }


def rage_end(tracker: FeatureTracker) -> bool:
    """结束狂暴。"""
    tracker.raging = False
    tracker.reckless = False
    return True


def rage_damage_bonus(tracker: FeatureTracker, barbarian_level: int) -> int:
    """获取当前狂暴的伤害加值。"""
    if not tracker.raging:
        return 0
    if barbarian_level >= 16:
        return 4
    elif barbarian_level >= 9:
        return 3
    return 2


def reckless_attack(tracker: FeatureTracker) -> bool:
    """鲁莽攻击：本回合你的力量近战攻击具有优势，但对你攻击也具有优势。

    规则: R-CLS-021 鲁莽攻击
    出处: topics/玩家手册2024/角色职业/野蛮人/野蛮人.htm
    等级: 野蛮人2级

    返回: True（恒可用，无消耗）
    """
    tracker.reckless = True
    return True


def is_raging(tracker: FeatureTracker) -> bool:
    """是否在狂暴中。"""
    return tracker.raging


# ══════════════════════════════════════════════════════════════════════════
# 游荡者特性
# ══════════════════════════════════════════════════════════════════════════

def sneak_attack_damage(rogue_level: int) -> dict:
    """偷袭伤害骰。

    规则: R-CLS-030 偷袭
    出处: topics/玩家手册2024/角色职业/游荡者/游荡者.htm
    等级: 游荡者1级

    条件（由调用方检查）:
        1. 使用灵巧或远程武器攻击
        2. 攻击具有优势 或 目标5尺内有非失能盟友
        3. 没有劣势

    参数:
        rogue_level: 游荡者等级

    返回: {"dice_count": N, "dice_expr": "Nd6", "avg": 平均伤害}
    """
    # 偷袭伤害 = ceil(rogue_level/2) d6
    dice_count = (rogue_level + 1) // 2
    return {
        "dice_count": dice_count,
        "dice_expr": f"{dice_count}d6",
    }


def roll_sneak_attack(rogue_level: int, crit: bool = False) -> dict:
    """掷偷袭伤害。

    规则: R-CLS-030 偷袭 / R-CMB-029 重击翻倍
    """
    info = sneak_attack_damage(rogue_level)
    result = dice.roll_dice(info["dice_expr"], crit=crit)
    return {
        "dice_count": info["dice_count"],
        "dice_expr": info["dice_expr"],
        "total": result.total,
        "rolls": result.dice_rolls,
        "crit": crit,
    }


def cunning_action(tracker: FeatureTracker = None) -> list[str]:
    """灵巧动作：可用附赠动作 Dash / Disengage / Hide。

    规则: R-CLS-031 灵巧动作
    出处: topics/玩家手册2024/角色职业/游荡者/游荡者.htm
    等级: 游荡者2级

    返回: ["Dash", "Disengage", "Hide"] 可选动作列表
    """
    return ["Dash", "Disengage", "Hide"]


# ══════════════════════════════════════════════════════════════════════════
# 圣武士特性
# ══════════════════════════════════════════════════════════════════════════

def divine_smite(
    slot_level: int,
    target_is_undead_or_fiend: bool = False,
    crit: bool = False,
) -> dict:
    """至圣斩：消耗法术位造成额外光耀伤害。

    规则: R-CLS-040 至圣斩
    出处: topics/玩家手册2024/角色职业/圣武士/圣武士.htm
    等级: 圣武士2级

    伤害: 基础 2d8，每高于1环 +1d8，上限 5d8
          对不死/邪魔额外 +1d8

    参数:
        slot_level: 消耗的法术位环阶 (1-5)
        target_is_undead_or_fiend: 目标是否不死生物或邪魔
        crit: 是否重击（骰数翻倍）

    返回: {"total": 伤害, "dice_count": 骰数, "rolls": [...]}
    """
    if slot_level < 1:
        return {"total": 0, "dice_count": 0, "rolls": [], "error": "需要至少1环法术位"}

    # 基础 2d8
    base_dice = 2
    # 每环额外 +1d8 (上限5d8基础，但2024版上限改为6d8)
    # 规则: 1环=2d8, 2环=3d8, 3环=4d8, 4环=5d8, 5环=6d8
    extra_dice = max(0, slot_level - 1)
    total_dice = min(base_dice + extra_dice, 6)  # 2024上限6d8

    # 对不死/邪魔 +1d8
    if target_is_undead_or_fiend:
        total_dice += 1

    dice_expr = f"{total_dice}d8"
    result = dice.roll_dice(dice_expr, crit=crit)

    return {
        "total": result.total,
        "dice_count": total_dice,
        "dice_expr": dice_expr,
        "rolls": result.dice_rolls,
        "slot_level": slot_level,
        "bonus_vs_fiend_undead": target_is_undead_or_fiend,
        "crit": crit,
    }


def lay_on_hands(paladin_level: int, heal_amount: int) -> dict:
    """圣疗：从治疗池中分配HP。

    规则: R-CLS-041 圣疗
    出处: topics/玩家手册2024/角色职业/圣武士/圣武士.htm
    等级: 圣武士1级

    治疗池 = paladin_level × 5
    """
    max_pool = paladin_level * 5
    applied = min(heal_amount, max_pool)
    return {
        "applied": applied,
        "pool_max": max_pool,
        "pool_remaining": max_pool - applied,
    }


# ══════════════════════════════════════════════════════════════════════════
# 吟游诗人特性
# ══════════════════════════════════════════════════════════════════════════

def bardic_inspiration_die(bard_level: int) -> int:
    """诗人激励骰面值。

    规则: R-CLS-050 诗人激励
    出处: topics/玩家手册2024/角色职业/吟游诗人/吟游诗人.htm
    等级: 吟游诗人1级

    1-4级: d6, 5-9级: d8, 10-14级: d10, 15+级: d12
    """
    if bard_level >= 15:
        return 12
    elif bard_level >= 10:
        return 10
    elif bard_level >= 5:
        return 8
    return 6


def roll_bardic_inspiration(bard_level: int) -> dict:
    """掷诗人激励骰。

    返回: {"die": dN, "result": N}
    """
    die = bardic_inspiration_die(bard_level)
    result = dice.roll_die(die)
    return {"die": die, "result": result}


# ══════════════════════════════════════════════════════════════════════════
# 牧师特性
# ══════════════════════════════════════════════════════════════════════════

def channel_divinity_uses(char_level: int) -> int:
    """引导神力可用次数。

    规则: R-CLS-060 引导神力
    出处: topics/玩家手册2024/角色职业/牧师/牧师.htm
    等级: 牧师2级

    1-5级: 1次/休息, 6-17级: 2次, 18+级: 3次
    """
    if char_level >= 18:
        return 3
    elif char_level >= 6:
        return 2
    return 1


def turn_undead(
    cleric_level: int,
    wisdom_mod: int,
    prof_bonus: int,
    undead_cr: float,
    undead_wis_save: int,
) -> dict:
    """驱散不死生物：不死生物需通过感知豁免否则陷入恐慌。

    规则: R-CLS-061 驱散不死生物
    出处: topics/玩家手册2024/角色职业/牧师/牧师.htm
    等级: 牧师2级

    参数:
        cleric_level: 牧师等级
        wisdom_mod: 牧师感知调整值
        prof_bonus: 熟练加值
        undead_cr: 不死生物CR
        undead_wis_save: 不死生物感知豁免加值

    返回: {"dc": int, "save_roll": int, "turned": bool, "destroyed": bool}
    """
    dc = 8 + wisdom_mod + prof_bonus

    # 驱散判定 (不死生物的感知豁免，通常无熟练)
    sv = check.saving_throw(mod=undead_wis_save, prof=0, proficient=False, dc=dc)

    # 摧毁判定：CR ≤ 阈值则直接摧毁
    if cleric_level >= 17:
        destroy_threshold = 4.0
    elif cleric_level >= 14:
        destroy_threshold = 3.0
    elif cleric_level >= 11:
        destroy_threshold = 2.0
    elif cleric_level >= 8:
        destroy_threshold = 1.0
    elif cleric_level >= 5:
        destroy_threshold = 0.5
    else:
        destroy_threshold = 0.0

    return {
        "dc": dc,
        "save_roll": sv.d20,
        "save_total": sv.total,
        "save_success": sv.success,
        "turned": not sv.success,
        "destroyed": not sv.success and undead_cr <= destroy_threshold,
        "frightened": not sv.success,
    }


# ══════════════════════════════════════════════════════════════════════════
# 便捷：按职业初始化特性追踪
# ══════════════════════════════════════════════════════════════════════════

def init_features_for_class(
    class_name: str,
    char_level: int,
    proficiency_bonus: Optional[int] = None,
) -> FeatureTracker:
    """按职业初始化 FeatureTracker。

    参数:
        class_name: 职业中文名
        char_level: 职业等级
        proficiency_bonus: 熟练加值（不传则自动计算）
    """
    if proficiency_bonus is None:
        proficiency_bonus = dice.proficiency_bonus(char_level)

    tracker = FeatureTracker(
        char_level=char_level,
        proficiency_bonus=proficiency_bonus,
    )

    if class_name == "野蛮人":
        # R-CLS-020: 狂暴次数
        if char_level >= 20:
            tracker.max_uses["rage"] = 6
        elif char_level >= 17:
            tracker.max_uses["rage"] = 5
        elif char_level >= 12:
            tracker.max_uses["rage"] = 4
        elif char_level >= 6:
            tracker.max_uses["rage"] = 4 if char_level >= 6 else 3
        elif char_level >= 3:
            tracker.max_uses["rage"] = 3
        else:
            tracker.max_uses["rage"] = 2
        tracker.uses["rage"] = 0

    elif class_name == "战士":
        # R-CLS-010: 动作如潮
        if char_level >= 17:
            tracker.max_uses["action_surge"] = 2
        else:
            tracker.max_uses["action_surge"] = 1
        tracker.uses["action_surge"] = 0
        # 回气总是1次
        tracker.max_uses["second_wind"] = 1
        tracker.uses["second_wind"] = 0

    elif class_name == "牧师":
        tracker.max_uses["channel_divinity"] = channel_divinity_uses(char_level)
        tracker.uses["channel_divinity"] = 0

    elif class_name == "圣武士":
        tracker.max_uses["channel_divinity"] = 1
        tracker.uses["channel_divinity"] = 0

    elif class_name == "吟游诗人":
        # 激励次数 = CHA mod (由 char_create 设置，这里最小1)
        tracker.max_uses["bardic_inspiration"] = max(1, proficiency_bonus)
        tracker.uses["bardic_inspiration"] = 0

    elif class_name == "德鲁伊":
        tracker.max_uses["wild_shape"] = 2
        tracker.uses["wild_shape"] = 0

    elif class_name == "武僧":
        # 专注点 = 武僧等级（2024版）
        tracker.max_uses["focus_points"] = char_level
        tracker.uses["focus_points"] = 0

    elif class_name == "术士":
        # 术法点 = 术士等级
        tracker.max_uses["sorcery_points"] = char_level
        tracker.uses["sorcery_points"] = 0

    return tracker


# ══════════════════════════════════════════════════════════════════════════
# 自检
# ══════════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    # ── FeatureTracker 基础 ──
    ft = FeatureTracker(char_level=5, proficiency_bonus=3)
    ft.max_uses["rage"] = 3
    ft.uses["rage"] = 0
    assert ft.has_use("rage")
    assert ft.use("rage")
    assert ft.remaining("rage") == 2
    ft.recover("rage")
    assert ft.remaining("rage") == 3

    # 短休恢复 action_surge
    ft.max_uses["action_surge"] = 1
    ft.use("action_surge")
    assert ft.remaining("action_surge") == 0
    ft.on_short_rest()
    assert ft.remaining("action_surge") == 1

    # ── 狂暴 ──
    barb_tracker = init_features_for_class("野蛮人", 5)
    assert barb_tracker.max_uses["rage"] == 3
    r = rage_activate(barb_tracker, 5)
    assert r["success"]
    assert r["rage_damage"] == 2
    assert barb_tracker.raging
    assert rage_damage_bonus(barb_tracker, 5) == 2
    rage_end(barb_tracker)
    assert not barb_tracker.raging

    # ── 动作如潮 ──
    ftr_tracker = init_features_for_class("战士", 5)
    assert ftr_tracker.max_uses["action_surge"] == 1
    assert action_surge(ftr_tracker)
    assert not action_surge(ftr_tracker)  # 已用尽

    # ── 回气 ──
    sw = second_wind(5)
    assert sw["heal"] >= 5 + 1  # 1d10 + 5
    assert sw["heal"] <= 5 + 10

    # ── 偷袭 ──
    sa = sneak_attack_damage(5)
    assert sa["dice_count"] == 3  # ceil(5/2)
    assert sa["dice_expr"] == "3d6"

    sa_roll = roll_sneak_attack(9)
    assert sa_roll["dice_count"] == 5  # ceil(9/2)
    assert 5 <= sa_roll["total"] <= 30  # 5d6

    # 重击偷袭
    sa_crit = roll_sneak_attack(5, crit=True)
    assert sa_crit["dice_count"] == 3

    # ── 至圣斩 ──
    ds = divine_smite(1)
    assert ds["dice_count"] == 2  # 基础2d8
    assert 2 <= ds["total"] <= 16

    ds_undead = divine_smite(2, target_is_undead_or_fiend=True)
    assert ds_undead["dice_count"] == 4  # 3d8 + 1d8

    ds_crit = divine_smite(1, crit=True)
    assert ds_crit["crit"]

    # ── 圣疗 ──
    loh = lay_on_hands(5, 10)
    assert loh["pool_max"] == 25  # 5×5
    assert loh["applied"] == 10
    assert loh["pool_remaining"] == 15

    # ── 诗人激励 ──
    assert bardic_inspiration_die(1) == 6
    assert bardic_inspiration_die(5) == 8
    assert bardic_inspiration_die(10) == 10
    assert bardic_inspiration_die(15) == 12
    bi = roll_bardic_inspiration(5)
    assert bi["die"] == 8
    assert 1 <= bi["result"] <= 8

    # ── 引导神力 ──
    assert channel_divinity_uses(2) == 1
    assert channel_divinity_uses(6) == 2
    assert channel_divinity_uses(18) == 3

    # ── 驱散不死生物 ──
    tu = turn_undead(cleric_level=5, wisdom_mod=3, prof_bonus=3,
                     undead_cr=0.25, undead_wis_save=-1)
    assert tu["dc"] == 14  # 8+3+3
    assert "turned" in tu and "destroyed" in tu

    # ── 灵巧动作 ──
    assert len(cunning_action()) == 3

    # ── 初始化各职业 ──
    for cls_name in ["野蛮人", "战士", "牧师", "圣武士", "吟游诗人", "德鲁伊", "武僧", "术士"]:
        t = init_features_for_class(cls_name, 5)
        assert t.char_level == 5

    print("[class_features] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
