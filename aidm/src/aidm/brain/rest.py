"""休息机制 — 短休 / 长休 / 打断休息。

依据玩家手册术语汇编「短休 Short Rest」「长休 Long Rest」与
城主指南第10章「运作游戏」的休息规则。规则点 R-GLS-014(短休)、
R-GLS-015(长休)，补遗 R-ADD-015(长休打断与部分休整)、
R-ADD-016(长休恢复HP上限)、R-ADD-017(短休特性恢复钩子)。

设计原则（ARCHITECTURE §4）：LLM 只在 classify(意图) 与 narrate(叙事)
两端活动，中间 retrieve→verify→resolve(骰子) 全代码。本模块为纯代码实现，
不依赖 LLM。角色卡的真实属性/HP 由 stats 模块持有；本模块管理休息状态机。

规则出处:
  - topics/玩家手册2024/术语汇编/常见规则词汇.htm （短休/长休/生命值骰）
  - topics/城主指南2024/2.运作游戏/运作交涉/态度.htm （休息打断条件）

注意: 不修改 engine/dice.py、engine/check.py、engine/damage.py。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..engine import dice

# ──────────────────────────────────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────────────────────────────────

# 短休时长：至少1小时
# 规则: R-GLS-014 短休  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
SHORT_REST_DURATION_HOURS = 1

# 长休时长：至少8小时（其中至少6小时睡眠，至多2小时轻度活动）
# 规则: R-GLS-015 长休  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
LONG_REST_DURATION_HOURS = 8
LONG_REST_SLEEP_MIN_HOURS = 6
LONG_REST_LIGHT_ACTIVITY_MAX_HOURS = 2

# 长休冷却：完成后须等待至少16小时才能再次长休
# 规则: R-GLS-015 长休  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
LONG_REST_COOLDOWN_HOURS = 16

# 打断休息的原因
# 规则: R-ADD-015 长休打断与部分休整  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
#   - 投掷先攻 (roll_initiative)
#   - 施展一道非戏法的法术 (cast_non_cantrip_spell)
#   - 受到任何伤害 (take_damage)
#   - 1小时的行走或其他的体力劳动 (1hr_travel_or_labor) —— 仅长休
INTERRUPT_ROLL_INITIATIVE = "roll_initiative"
INTERRUPT_CAST_NON_CANTRIP_SPELL = "cast_non_cantrip_spell"
INTERRUPT_TAKE_DAMAGE = "take_damage"
INTERRUPT_1HR_TRAVEL_OR_LABOR = "1hr_travel_or_labor"

# 短休打断原因（3项）
SHORT_REST_INTERRUPTS = frozenset({
    INTERRUPT_ROLL_INITIATIVE,
    INTERRUPT_CAST_NON_CANTRIP_SPELL,
    INTERRUPT_TAKE_DAMAGE,
})

# 长休打断原因（4项，比短休多"1小时行走或体力劳动"）
LONG_REST_INTERRUPTS = frozenset({
    INTERRUPT_ROLL_INITIATIVE,
    INTERRUPT_CAST_NON_CANTRIP_SPELL,
    INTERRUPT_TAKE_DAMAGE,
    INTERRUPT_1HR_TRAVEL_OR_LABOR,
})


# ──────────────────────────────────────────────────────────────────────────
# 休息状态
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class RestState:
    """一次休息的状态跟踪。

    规则: R-GLS-014 短休 / R-GLS-015 长休
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm

    属性:
        type: 休息类型 "short" | "long"
        duration: 已休息时长（小时）
        start_time: 休息开始的世界时间戳（小时为单位，可选）
        interrupted: 是否被打断
        completed: 是否完成
        interrupt_count: 被打断次数（长休每打断一次需额外休息1小时）
        elapsed_at_interrupt: 打断时已休息时长（小时），用于判断是否≥1h可获短休增益
    """
    type: str = "short"               # "short" | "long"
    duration: float = 0.0             # 已休息时长（小时）
    start_time: float | None = None  # 世界时间戳（小时）
    interrupted: bool = False
    completed: bool = False
    interrupt_count: int = 0          # 长休打断计数
    elapsed_at_interrupt: float = 0.0  # 打断时刻已休息时长

    def required_duration(self) -> float:
        """本次休息完成所需的总时长（小时）。

        长休每被打断一次需额外休息1小时。
        规则: R-ADD-015  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
        """
        base = LONG_REST_DURATION_HOURS if self.type == "long" else SHORT_REST_DURATION_HOURS
        extra = self.interrupt_count if self.type == "long" else 0
        return base + extra


# ──────────────────────────────────────────────────────────────────────────
# 角色协议（鸭子类型）
# ──────────────────────────────────────────────────────────────────────────

# 本模块对"角色"的最低要求（鸭子类型协议）：
#   hp: int                 — 当前生命值
#   max_hp: int             — 生命值上限
#   hit_dice: int           — 可用生命骰数量
#   max_hit_dice: int       — 生命骰上限
#   con_mod: int            — 体质调整值
#   hit_die_faces: int      — 生命骰面数
#   base_max_hp: int        — 未被减少的原始HP上限
#   exhaustion: int         — 力竭等级（0..6）
#   spell_slots: dict       — {环阶: 剩余}（施法者）
#   max_spell_slots: dict   — {环阶: 上限}（施法者）
#
# MockCharacter（自检用）直接具备上述字段。而 stats/models.py 的
# Character(SQLModel) 字段名为 hp_current/hp_max/level/char_class/abilities 等，
# 并未直接提供 hp/max_hit_dice/con_mod/hit_die_faces/base_max_hp。
# 故 _get 在直接属性缺失时，按 Character 模型推导这些值（适配层）：
#   hp          → hp_current
#   max_hp      → hp_max
#   base_max_hp → hp_max（Character 不追踪HP上限减少，以当前上限为准）
#   con_mod     → ability_mod("con")
#   hit_die_faces → CLASSES[char_class]["hit_die"]
#   hit_dice / max_hit_dice → level（假定全部生命骰可用，上限=等级）
# rest 函数返回结构化结果字典，不直接修改角色卡——
# 由上层编排（graph.py）应用 state_changes。


def _derive_for_character(character: Any, attr: str, default: Any) -> Any:
    """为 Character(SQLModel) 推导 rest 协议所需但未直接提供的字段。

    仅当直接属性缺失时调用。出处见上方鸭子类型协议注释。
    """
    # hp → 当前生命值
    if attr == "hp":
        return getattr(character, "hp_current", default)
    # max_hp / base_max_hp → hp_max（Character 不追踪HP上限的临时减少）
    if attr in ("max_hp", "base_max_hp"):
        return getattr(character, "hp_max", default)
    # con_mod → 体质调整值
    if attr == "con_mod":
        if hasattr(character, "ability_mod"):
            return character.ability_mod("con")
        return default
    # hit_die_faces → 职业生命骰面数
    if attr == "hit_die_faces":
        cls_name = getattr(character, "char_class", "") or getattr(character, "class_name", "")
        try:
            from aidm.data.classes import get_class
            return get_class(cls_name)["hit_die"]
        except Exception:
            return default
    # hit_dice → 可用生命骰数量（Character.hit_dice_current，默认回退到等级）
    if attr == "hit_dice":
        hd = getattr(character, "hit_dice_current", None)
        if hd is not None and hd > 0:
            return hd
        # 回退：未初始化时按等级处理
        return getattr(character, "level", default)
    # max_hit_dice → 生命骰上限（=等级）
    if attr == "max_hit_dice":
        return getattr(character, "level", default)
    # max_spell_slots → Character 无上限追踪；以当前 spell_slots 非空判定施法者
    if attr == "max_spell_slots":
        if hasattr(character, "spell_slots"):
            slots = character.spell_slots
            return slots if slots else default
        return default
    return default


def _get(character: Any, attr: str, default: Any = 0) -> Any:
    """安全取角色属性，缺失时按 Character 模型推导，再不行返回默认值。"""
    direct = getattr(character, attr, None)
    if direct is not None:
        return direct
    # 直接属性缺失 → 为 Character(SQLModel) 推导适配字段
    return _derive_for_character(character, attr, default)


# ──────────────────────────────────────────────────────────────────────────
# 短休
# ──────────────────────────────────────────────────────────────────────────

def short_rest(
    character: Any,
    hit_dice_to_spend: int = 0,
) -> dict:
    """执行一次短休。

    规则: R-GLS-014 短休
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm

    条件:
        - 时长至少1小时（由调用方保证时间流逝）
        - 必须具有至少1点生命值才能开始短休

    收益:
        - 消耗生命骰恢复HP：投掷任意枚生命骰，加上等于投掷次数倍的体质调整值。
          每次投掷后可决定是否继续消耗（此处由 hit_dice_to_spend 参数一次性指定）。
          恢复量至少为1（每枚骰子的恢复不低于1）。
        - 特殊特性恢复：某些职业特性在短休时恢复使用次数。

    参数:
        character: 角色对象（鸭子类型，见上方协议）
        hit_dice_to_spend: 本次短休要消耗的生命骰数量（0=不消耗）

    返回 dict:
        success: bool — 是否成功完成短休
        type: "short"
        hp_restored: int — 通过生命骰恢复的HP
        hit_dice_spent: int — 实际消耗的生命骰数
        hit_dice_remaining: int — 剩余可用生命骰
        features_recharged: list[str] — 本次恢复的职业特性名
        feature_recharge_amounts: dict[str, int|str] — 特性→短休恢复次数
            （int=固定次数，"all"=恢复全部；野蛮人狂暴=1）
        errors: list[str] — 失败原因列表
    """
    errors: list[str] = []

    # 条件检查：必须至少1 HP
    # 规则: R-GLS-014  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    current_hp = _get(character, "hp", 0)
    if current_hp < 1:
        errors.append(f"短休需要至少1点生命值，当前HP={current_hp}")
        return _fail_short(errors)

    # 校验 hit_dice_to_spend
    if hit_dice_to_spend < 0:
        errors.append(f"hit_dice_to_spend 不能为负，得到 {hit_dice_to_spend}")
        return _fail_short(errors)

    available_hd = _get(character, "hit_dice", 0)
    if hit_dice_to_spend > available_hd:
        errors.append(
            f"生命骰不足：请求消耗 {hit_dice_to_spend} 枚，"
            f"但仅有 {available_hd} 枚可用"
        )
        return _fail_short(errors)

    # 消耗生命骰恢复HP
    # 规则: R-GLS-014  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    #   投掷任意枚生命骰，加上等于投掷次数倍的体质调整值。
    #   恢复量至少为1。
    hp_restored = 0
    hd_rolls: list[int] = []
    con_mod = _get(character, "con_mod", 0)
    hit_die_faces = _get(character, "hit_die_faces", 8)  # 生命骰面数

    if hit_dice_to_spend > 0:
        total_roll = 0
        for _ in range(hit_dice_to_spend):
            roll = dice.roll_die(hit_die_faces)
            hd_rolls.append(roll)
            total_roll += roll
        # 恢复量 = 骰点总和 + 体质调整值 × 投掷次数，至少1
        hp_restored = total_roll + con_mod * hit_dice_to_spend
        if hp_restored < 1:
            hp_restored = 1

    # 恢复职业特性（短休恢复的特性）
    # 规则: R-ADD-017 短休特性恢复钩子
    # 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    features_recharged = recharge_features_on_short_rest(character)
    # 各特性短休恢复次数（野蛮人狂暴=1，其余默认"all"）
    feature_recharge_amounts = {
        f: short_rest_recharge_amount(f) for f in features_recharged
    }

    return {
        "success": True,
        "type": "short",
        "hp_restored": hp_restored,
        "hit_dice_spent": hit_dice_to_spend,
        "hit_dice_remaining": available_hd - hit_dice_to_spend,
        "hd_rolls": hd_rolls,
        "con_mod": con_mod,
        "features_recharged": features_recharged,
        "feature_recharge_amounts": feature_recharge_amounts,
        "errors": [],
    }


def _fail_short(errors: list[str]) -> dict:
    """构造短休失败结果。"""
    return {
        "success": False,
        "type": "short",
        "hp_restored": 0,
        "hit_dice_spent": 0,
        "hit_dice_remaining": 0,
        "hd_rolls": [],
        "con_mod": 0,
        "features_recharged": [],
        "feature_recharge_amounts": {},
        "errors": errors,
    }


# ──────────────────────────────────────────────────────────────────────────
# 长休
# ──────────────────────────────────────────────────────────────────────────

def long_rest(character: Any) -> dict:
    """执行一次长休。

    规则: R-GLS-015 长休
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm

    要求:
        - 时长至少8小时（其中至少6小时睡眠，至多2小时轻度活动）
        - 至少6小时睡眠 + 至多2小时轻度活动（站岗、阅读）
        - 必须具有至少1点生命值才能开始长休

    冷却:
        - 完成后须等待至少16小时才能再次长休

    收益:
        - 恢复全部HP（若HP上限被减少则恢复原状）
        - 恢复全部已消耗的生命骰
        - 被减少的属性值恢复原状
        - 力竭等级减少1层
        - 恢复所有法术位（除邪务师外的施法者——邪务师法术位在短休时恢复）
        - 特殊特性在长休时恢复

    参数:
        character: 角色对象（鸭子类型，见上方协议）

    返回 dict:
        success: bool — 是否成功完成长休
        type: "long"
        hp_restored: int — 恢复的HP（到max_hp）
        hit_dice_restored: int — 恢复的生命骰数（到max_hit_dice）
        exhaustion_reduced: int — 力竭减少的层数（0或1）
        spell_slots_restored: bool — 是否恢复了法术位
        ability_scores_restored: bool — 是否恢复了被减少的属性值
        max_hp_restored: bool — 是否恢复了被减少的HP上限
        features_recharged: list[str] — 本次恢复的职业特性名
        temp_hp_cleared: bool — 是否清空了临时生命值（长休后消失）
        temp_hp_before: int — 长休前的临时生命值（信息性）
        temp_hp: int — 长休后的临时生命值（恒为0）
        errors: list[str] — 失败原因列表
    """
    errors: list[str] = []

    # 条件检查：必须至少1 HP
    # 规则: R-GLS-015  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    current_hp = _get(character, "hp", 0)
    if current_hp < 1:
        errors.append(f"长休需要至少1点生命值，当前HP={current_hp}")
        return _fail_long(errors)

    # 记录恢复前的状态
    max_hp = _get(character, "max_hp", 0)
    base_max_hp = _get(character, "base_max_hp", max_hp)  # 原始HP上限（未被减少的）
    max_hit_dice = _get(character, "max_hit_dice", 0)
    exhaustion_before = _get(character, "exhaustion", 0)

    # 收益1: 恢复全部HP（若HP上限被减少则恢复原状）
    # 规则: R-ADD-016 长休恢复HP上限
    # 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    max_hp_restored = False
    if base_max_hp > max_hp:
        # HP上限被减少了，恢复原状
        max_hp_restored = True
        # 注意：实际修改由上层应用，这里仅记录

    hp_restored = max_hp - current_hp  # 恢复到当前max_hp的量
    if base_max_hp > max_hp:
        hp_restored = base_max_hp - current_hp  # 如果上限恢复，则恢复到原始上限

    # 收益2: 恢复全部已消耗的生命骰
    # 规则: R-GLS-015  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    current_hit_dice = _get(character, "hit_dice", 0)
    hit_dice_restored = max_hit_dice - current_hit_dice

    # 收益3: 被减少的属性值恢复原状
    # 规则: R-GLS-015  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    ability_scores_restored = bool(_get(character, "reduced_ability_scores", False))

    # 收益4: 力竭等级减少1层（降至0结束）
    # 规则: R-GLS-015 / R-GLS-047  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    exhaustion_reduced = 1 if exhaustion_before > 0 else 0

    # 收益5: 恢复所有法术位
    # 规则: R-SPL-003 法术位长休恢复  出处: topics/玩家手册2024/法术/法术环阶.htm
    # 邪术师（Warlock）的契约魔法（Pact Magic）法术位通过短休的"魔法回复"
    # 特性恢复，由短休流程中的专用钩子处理；此处长休恢复覆盖所有施法者，
    # 邪术师长休时同样恢复全部法术位。
    spell_slots_restored = False
    max_spell_slots = _get(character, "max_spell_slots", {})
    if max_spell_slots:
        spell_slots_restored = True

    # 收益6: 特殊特性在长休时恢复
    features_recharged = recharge_features_on_long_rest(character)

    # 收益7: 临时生命值清空
    # 规则: 临时生命值持续直至被消耗或完成一次长休
    # 出处: 进行游戏/临时生命值.txt（持续时间 Duration）
    temp_hp_before = _get(character, "temp_hp", 0)
    temp_hp_cleared = temp_hp_before > 0  # 仅有临时生命值时才标记为"已清空"

    return {
        "success": True,
        "type": "long",
        "hp_restored": hp_restored,
        "max_hp_restored": max_hp_restored,
        "hit_dice_restored": hit_dice_restored,
        "exhaustion_reduced": exhaustion_reduced,
        "exhaustion_before": exhaustion_before,
        "exhaustion_after": max(0, exhaustion_before - 1),
        "spell_slots_restored": spell_slots_restored,
        "ability_scores_restored": ability_scores_restored,
        "features_recharged": features_recharged,
        "temp_hp_cleared": temp_hp_cleared,  # 长休清空临时生命值（仅原有值>0时）
        "temp_hp_before": temp_hp_before,    # 长休前的临时生命值（信息性）
        "temp_hp": 0,                        # 长休后临时生命值归零
        "errors": [],
    }


def _fail_long(errors: list[str]) -> dict:
    """构造长休失败结果。"""
    return {
        "success": False,
        "type": "long",
        "hp_restored": 0,
        "max_hp_restored": False,
        "hit_dice_restored": 0,
        "exhaustion_reduced": 0,
        "exhaustion_before": 0,
        "exhaustion_after": 0,
        "spell_slots_restored": False,
        "ability_scores_restored": False,
        "features_recharged": [],
        "temp_hp_cleared": False,  # 失败时不清空临时生命值
        "temp_hp_before": 0,
        "temp_hp": 0,
        "errors": errors,
    }


# ──────────────────────────────────────────────────────────────────────────
# 打断休息
# ──────────────────────────────────────────────────────────────────────────

def interrupt_rest(rest_state: RestState, cause: str) -> dict:
    """打断一次进行中的休息。

    规则: R-ADD-015 长休打断与部分休整
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm

    打断条件:
        | 打断条件              | 短休 | 长休 |
        |----------------------|------|------|
        | 投掷先攻              | 打断 | 打断 |
        | 施展非戏法法术         | 打断 | 打断 |
        | 受到任何伤害           | 打断 | 打断 |
        | 1小时行走或体力劳动     | —   | 打断 |

    短休被打断：一次被打断的短休不会提供任何增益。

    长休被打断的处理：
        - 如果在长休被打断前已休息至少1小时，可获得一次短休的增益。
        - 可以在被打断后立刻继续长休，但每被打断一次需额外休息1小时才能完成。

    参数:
        rest_state: 当前休息状态（会被原地修改）
        cause: 打断原因（见 INTERRUPT_* 常量）

    返回 dict:
        interrupted: bool — 是否成功判定为打断
        cause: str — 打断原因
        rest_type: str — "short" | "long"
        elapsed_at_interrupt: float — 打断时已休息时长（小时）
        grants_short_rest_benefit: bool — 是否获得短休增益（仅长休且已休≥1h）
        short_rest_benefit_lost: bool — 短休增益丢失（短休被打断时）
        needs_extra_hours: int — 完成长休还需额外的小时数（长休）
        can_continue: bool — 是否可以继续长休（True）
        errors: list[str] — 失败原因列表
    """
    errors: list[str] = []

    if rest_state.completed:
        errors.append("休息已完成，无法打断")
        return _fail_interrupt(errors, cause)

    if rest_state.interrupted:
        errors.append("休息已被打断")
        return _fail_interrupt(errors, cause)

    # 验证打断原因是否适用于当前休息类型
    # 规则: R-ADD-015  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    valid_causes = (
        LONG_REST_INTERRUPTS if rest_state.type == "long" else SHORT_REST_INTERRUPTS
    )
    if cause not in valid_causes:
        errors.append(
            f"打断原因 {cause!r} 不适用于 {rest_state.type} 休"
            f"（适用原因: {sorted(valid_causes)}）"
        )
        return _fail_interrupt(errors, cause)

    # 记录打断时刻
    elapsed = rest_state.duration
    rest_state.elapsed_at_interrupt = elapsed
    rest_state.interrupted = True

    result: dict[str, Any] = {
        "interrupted": True,
        "cause": cause,
        "rest_type": rest_state.type,
        "elapsed_at_interrupt": elapsed,
        "errors": [],
    }

    if rest_state.type == "short":
        # 短休被打断：不提供任何增益
        # 规则: R-GLS-014  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
        result["grants_short_rest_benefit"] = False
        result["short_rest_benefit_lost"] = True
        result["needs_extra_hours"] = 0
        result["can_continue"] = False  # 短休被打断后不能"继续"，需重新开始

    elif rest_state.type == "long":
        # 长休被打断：如果已休息至少1小时，可获得一次短休的增益
        # 规则: R-ADD-015  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
        grants_benefit = elapsed >= 1.0
        result["grants_short_rest_benefit"] = grants_benefit
        result["short_rest_benefit_lost"] = False

        # 每被打断一次需额外休息1小时才能完成
        rest_state.interrupt_count += 1
        result["needs_extra_hours"] = rest_state.interrupt_count
        result["can_continue"] = True  # 长休被打断后可以立刻继续

    return result


def _fail_interrupt(errors: list[str], cause: str) -> dict:
    """构造打断失败结果。"""
    return {
        "interrupted": False,
        "cause": cause,
        "rest_type": "",
        "elapsed_at_interrupt": 0,
        "grants_short_rest_benefit": False,
        "short_rest_benefit_lost": False,
        "needs_extra_hours": 0,
        "can_continue": False,
        "errors": errors,
    }


# ──────────────────────────────────────────────────────────────────────────
# 职业特性恢复钩子
# ──────────────────────────────────────────────────────────────────────────

# 短休恢复的特性映射：职业名 → 特性名列表
# 规则: R-ADD-017 短休特性恢复钩子
# 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
# 说明: 以下特性在短休完成时恢复使用次数（按各自职业页描述，2026-07-27 逐条核对原文）。
#   - 野蛮人狂暴（短休恢复1次/长休恢复全部）
#     出处: 野蛮人.htm「1级：狂暴」
#   - 魔契师契约魔法法术位：完成短休或长休时重获全部（与长休恢复不冲突，两者都恢复）
#     出处: 魔契师.htm「1级：契约魔法」
#   - 战士动作如潮（Action Surge）：完成短休或长休后才能再次使用
#     出处: 战士.htm「2级：动作如潮」
#   - 武僧功力（Focus Points）：完成短休或长休时重获全部
#     出处: 武僧.htm「2级：武僧武功」
#   - 吟游诗人激励（Bardic Inspiration）：1-4级仅长休恢复；
#     5级特性「激励之源」后短休/长休均恢复全部（等级门槛在函数内处理）
#     出处: 吟游诗人.htm「1级：吟游诗人激励」「5级：激励之源」
#   - 德鲁伊荒野变形（Wild Shape）：短休恢复1次/长休恢复全部
#     出处: 德鲁伊.htm「2级：荒野变形」
SHORT_REST_RECHARGE_FEATURES: dict[str, list[str]] = {
    "野蛮人": ["狂暴"],          # 短休：恢复1次已消耗的狂暴使用次数
    "战士": ["动作如潮"],
    "武僧": ["功力"],
    "吟游诗人": ["吟游诗人激励"],  # 仅5级及以上（激励之源），见函数内等级门槛
    "德鲁伊": ["荒野变形"],        # 短休仅恢复1次
    "魔契师": ["契约魔法法术位"],  # 契约魔法法术位短休亦恢复
}

# 诗人激励短休恢复所需的最低等级（激励之源）
# 出处: 吟游诗人.htm「5级：激励之源」
BARD_SHORT_REST_MIN_LEVEL = 5

# 短休部分恢复表：特性名 → 短休恢复的使用次数。
# 不在此表中的特性默认短休恢复全部使用次数（"all"）。
# 规则出处: 玩家手册2024/角色职业/野蛮人/野蛮人.htm「1级：狂暴」
#   "当你完成一次短休时，你重获一次已消耗的使用次数；
#    当你完成一次长休时，你重获所有已消耗的使用次数。"
# 规则出处: 玩家手册2024/角色职业/德鲁伊/德鲁伊.htm「2级：荒野变形」
#   "你在完成短休后重获一次已消耗的使用次数，
#    当你完成一次长休时，你重获全部已消耗的使用次数。"
SHORT_REST_PARTIAL_RECHARGE: dict[str, int] = {
    "狂暴": 1,      # 野蛮人狂暴：短休仅恢复1次
    "荒野变形": 1,  # 德鲁伊荒野变形：短休仅恢复1次
}

# 长休恢复的特性映射：职业名 → 特性名列表
# 规则: R-GLS-015 长休的增益  出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
# 说明: 以下特性在长休完成时恢复使用次数（按各自职业页描述）。
#   - 所有施法者的法术位（含魔契师——契约魔法短休/长休均恢复）
#   - 战士动作如潮（也在短休恢复）
#   - 武僧功力（也在短休恢复）
#   - 吟游诗人激励（任意等级长休恢复；5级后也可短休恢复）
#   - 德鲁伊荒野变形（也在短休恢复，短休仅1次）
#   - 野蛮人狂暴（长休恢复全部）
LONG_REST_RECHARGE_FEATURES: dict[str, list[str]] = {
    "野蛮人": ["狂暴"],
    "战士": ["动作如潮"],
    "武僧": ["功力"],
    "吟游诗人": ["吟游诗人激励"],
    "德鲁伊": ["荒野变形"],
    # 施法者法术位恢复由 long_rest 单独处理（spell_slots_restored）
}


def recharge_features_on_short_rest(character: Any) -> list[str]:
    """短休完成时恢复职业特性使用次数。

    规则: R-ADD-017 短休特性恢复钩子
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm

    恢复的特性（按各自职业页描述，2026-07-27 核对原文）：
        - 野蛮人狂暴：短休恢复1次已消耗的使用次数
          （出处: 野蛮人.htm「1级：狂暴」）
        - 契约魔法法术位（魔契师）：短休时恢复全部
          （出处: 魔契师.htm「1级：契约魔法」）
        - 战士动作如潮：短休或长休后恢复
          （出处: 战士.htm「2级：动作如潮」）
        - 武僧功力：短休或长休时恢复全部
          （出处: 武僧.htm「2级：武僧武功」）
        - 吟游诗人激励：仅5级及以上短休恢复全部（激励之源）；
          1-4级短休不恢复（仅长休恢复）
          （出处: 吟游诗人.htm「1级：吟游诗人激励」「5级：激励之源」）
        - 德鲁伊荒野变形：短休恢复1次
          （出处: 德鲁伊.htm「2级：荒野变形」）

    参数:
        character: 角色对象，需有 char_class 或 class_name 属性；
        吟游诗人需 level 属性以判定激励之源门槛

    返回:
        恢复的特性名列表。
        每个特性短休恢复的使用次数由 short_rest_recharge_amount(feature) 查询：
        默认恢复全部("all")，除非在 SHORT_REST_PARTIAL_RECHARGE 中指定固定次数。
    """
    class_name = (
        _get(character, "char_class", None)
        or _get(character, "class_name", None)
        or ""
    )
    level = _get(character, "level", 1) or 1
    recharged: list[str] = []
    features = SHORT_REST_RECHARGE_FEATURES.get(class_name, [])
    for feature in features:
        # 吟游诗人激励：5级「激励之源」后短休才能恢复
        # 出处: 吟游诗人.htm「1级：吟游诗人激励」（长休恢复）/「5级：激励之源」（短休恢复）
        if class_name == "吟游诗人" and feature == "吟游诗人激励" and level < BARD_SHORT_REST_MIN_LEVEL:
            continue
        recharged.append(feature)
    return recharged


def short_rest_recharge_amount(feature: str) -> Any:
    """查询某特性在短休时恢复的使用次数。

    返回:
        int — 固定恢复次数（如野蛮人狂暴=1）
        "all" — 恢复全部已消耗的使用次数（默认）

    规则出处: 玩家手册2024/角色职业/野蛮人/野蛮人.htm:85
        短休恢复1次、长休恢复全部。
    """
    return SHORT_REST_PARTIAL_RECHARGE.get(feature, "all")


def recharge_features_on_long_rest(character: Any) -> list[str]:
    """长休完成时恢复职业特性使用次数。

    规则: R-GLS-015 长休的增益
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm

    恢复的特性（按各自职业页描述）：
        - 野蛮人狂暴：长休后恢复全部
        - 战士动作如潮：长休后恢复
        - 武僧功力：长休后恢复
        - 吟游诗人激励：长休后恢复（任意等级）
        - 德鲁伊荒野变形：长休后恢复全部

    注意：契约魔法法术位短休与长休均恢复（出处: 魔契师.htm「1级：契约魔法」），
    短休分支由 recharge_features_on_short_rest 处理。
    施法者法术位恢复由 long_rest 单独处理（spell_slots_restored 字段）。

    参数:
        character: 角色对象，需有 char_class 或 class_name 属性

    返回:
        恢复的特性名列表
    """
    class_name = (
        _get(character, "char_class", None)
        or _get(character, "class_name", None)
        or ""
    )
    recharged: list[str] = []
    features = LONG_REST_RECHARGE_FEATURES.get(class_name, [])
    for feature in features:
        recharged.append(feature)
    return recharged


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class MockCharacter:
    """自检用的模拟角色。"""
    hp: int = 10
    max_hp: int = 20
    hit_dice: int = 3
    max_hit_dice: int = 3
    con_mod: int = 2
    hit_die_faces: int = 10
    exhaustion: int = 0
    char_class: str = "战士"
    base_max_hp: int = 20
    reduced_ability_scores: bool = False
    spell_slots: dict = field(default_factory=lambda: {1: 2})
    max_spell_slots: dict = field(default_factory=lambda: {1: 4})
    temp_hp: int = 0


def _self_test() -> None:
    """休息机制自检。"""

    # === 短休测试 ===

    # 短休：不消耗生命骰
    c = MockCharacter(hp=10, max_hp=20)
    r = short_rest(c, hit_dice_to_spend=0)
    assert r["success"] is True
    assert r["type"] == "short"
    assert r["hp_restored"] == 0
    assert r["hit_dice_spent"] == 0
    assert r["hit_dice_remaining"] == 3

    # 短休：消耗1枚生命骰
    c = MockCharacter(hp=10, max_hp=20, con_mod=2, hit_die_faces=10)
    r = short_rest(c, hit_dice_to_spend=1)
    assert r["success"] is True
    assert r["hit_dice_spent"] == 1
    assert r["hit_dice_remaining"] == 2
    # 恢复量 = d10 + CON×1 ∈ [3, 12]
    assert 3 <= r["hp_restored"] <= 12
    assert len(r["hd_rolls"]) == 1

    # 短休：消耗2枚生命骰
    c = MockCharacter(hp=5, max_hp=20, con_mod=3, hit_die_faces=8)
    r = short_rest(c, hit_dice_to_spend=2)
    assert r["success"] is True
    assert r["hit_dice_spent"] == 2
    assert r["hit_dice_remaining"] == 1
    # 恢复量 = 2d8 + CON×2 ∈ [8, 22]
    assert 8 <= r["hp_restored"] <= 22
    assert len(r["hd_rolls"]) == 2

    # 短休：HP不足1点
    c = MockCharacter(hp=0, max_hp=20)
    r = short_rest(c, hit_dice_to_spend=1)
    assert r["success"] is False
    assert "至少1点生命值" in r["errors"][0]

    # 短休：生命骰不足
    c = MockCharacter(hp=10, max_hp=20, hit_dice=1)
    r = short_rest(c, hit_dice_to_spend=2)
    assert r["success"] is False
    assert "生命骰不足" in r["errors"][0]

    # 短休：负数参数
    c = MockCharacter(hp=10, max_hp=20)
    r = short_rest(c, hit_dice_to_spend=-1)
    assert r["success"] is False
    assert "不能为负" in r["errors"][0]

    # 短休：恢复职业特性（战士动作如潮）
    c = MockCharacter(hp=10, max_hp=20, char_class="战士")
    r = short_rest(c, hit_dice_to_spend=0)
    assert r["success"] is True
    assert "动作如潮" in r["features_recharged"]

    # 短休：恢复职业特性（武僧功力）
    c = MockCharacter(hp=10, max_hp=20, char_class="武僧")
    r = short_rest(c, hit_dice_to_spend=0)
    assert r["success"] is True
    assert "功力" in r["features_recharged"]

    # 短休：恢复职业特性（魔契师契约魔法法术位）
    c = MockCharacter(hp=10, max_hp=20, char_class="魔契师")
    r = short_rest(c, hit_dice_to_spend=0)
    assert r["success"] is True
    assert "契约魔法法术位" in r["features_recharged"]

    # 短休：德鲁伊荒野变形仅恢复1次（出处: 德鲁伊.htm「2级：荒野变形」）
    c = MockCharacter(hp=10, max_hp=20, char_class="德鲁伊")
    r = short_rest(c, hit_dice_to_spend=0)
    assert r["success"] is True
    assert "荒野变形" in r["features_recharged"]
    assert r["feature_recharge_amounts"]["荒野变形"] == 1

    # 短休：1-4级诗人激励不恢复（仅长休）；5级起短休恢复（激励之源）
    c = MockCharacter(hp=10, max_hp=20, char_class="吟游诗人", level=3)
    r = short_rest(c, hit_dice_to_spend=0)
    assert r["success"] is True
    assert "吟游诗人激励" not in r["features_recharged"]
    c = MockCharacter(hp=10, max_hp=20, char_class="吟游诗人", level=5)
    r = short_rest(c, hit_dice_to_spend=0)
    assert r["success"] is True
    assert "吟游诗人激励" in r["features_recharged"]

    # 短休：恢复职业特性（野蛮人狂暴——仅恢复1次）
    # 规则: 玩家手册2024/角色职业/野蛮人/野蛮人.htm:85
    #   短休恢复1次已消耗的使用次数；长休恢复全部。
    c = MockCharacter(hp=10, max_hp=20, char_class="野蛮人")
    r = short_rest(c, hit_dice_to_spend=0)
    assert r["success"] is True
    assert "狂暴" in r["features_recharged"]
    assert r["feature_recharge_amounts"]["狂暴"] == 1  # 短休仅恢复1次

    # 短休：默认特性恢复全部使用次数（"all"）
    c = MockCharacter(hp=10, max_hp=20, char_class="战士")
    r = short_rest(c, hit_dice_to_spend=0)
    assert r["feature_recharge_amounts"]["行动涌动"] == "all"

    # === 长休测试 ===

    # 长休：基本恢复
    c = MockCharacter(hp=5, max_hp=20, hit_dice=1, max_hit_dice=3, exhaustion=2)
    r = long_rest(c)
    assert r["success"] is True
    assert r["type"] == "long"
    assert r["hp_restored"] == 15  # 20 - 5
    assert r["hit_dice_restored"] == 2  # 3 - 1
    assert r["exhaustion_reduced"] == 1
    assert r["exhaustion_before"] == 2
    assert r["exhaustion_after"] == 1

    # 长休：力竭为0时不减少
    c = MockCharacter(hp=5, max_hp=20, exhaustion=0)
    r = long_rest(c)
    assert r["success"] is True
    assert r["exhaustion_reduced"] == 0
    assert r["exhaustion_after"] == 0

    # 长休：HP不足1点
    c = MockCharacter(hp=0, max_hp=20)
    r = long_rest(c)
    assert r["success"] is False
    assert "至少1点生命值" in r["errors"][0]

    # 长休：HP上限被减少时恢复原状
    c = MockCharacter(hp=3, max_hp=15, base_max_hp=20)
    r = long_rest(c)
    assert r["success"] is True
    assert r["max_hp_restored"] is True
    assert r["hp_restored"] == 17  # base_max_hp(20) - current_hp(3)

    # 长休：HP上限未被减少
    c = MockCharacter(hp=3, max_hp=20, base_max_hp=20)
    r = long_rest(c)
    assert r["success"] is True
    assert r["max_hp_restored"] is False

    # 长休：恢复法术位
    c = MockCharacter(hp=5, max_hp=20, spell_slots={1: 1}, max_spell_slots={1: 4})
    r = long_rest(c)
    assert r["success"] is True
    assert r["spell_slots_restored"] is True

    # 长休：无施法能力
    c = MockCharacter(hp=5, max_hp=20, char_class="战士", spell_slots={}, max_spell_slots={})
    r = long_rest(c)
    assert r["success"] is True
    assert r["spell_slots_restored"] is False

    # 长休：恢复被减少的属性值
    c = MockCharacter(hp=5, max_hp=20, reduced_ability_scores=True)
    r = long_rest(c)
    assert r["success"] is True
    assert r["ability_scores_restored"] is True

    # 长休：恢复职业特性（野蛮人狂暴）
    c = MockCharacter(hp=5, max_hp=20, char_class="野蛮人", exhaustion=1)
    r = long_rest(c)
    assert r["success"] is True
    assert "狂暴" in r["features_recharged"]

    # 长休：恢复职业特性（战士行动涌动）
    c = MockCharacter(hp=5, max_hp=20, char_class="战士")
    r = long_rest(c)
    assert r["success"] is True
    assert "行动涌动" in r["features_recharged"]

    # 长休：清空临时生命值（长休后临时HP消失）
    # 规则: 临时生命值持续至被消耗或完成一次长休
    # 出处: 进行游戏/临时生命值.txt
    c = MockCharacter(hp=5, max_hp=20, temp_hp=8)
    r = long_rest(c)
    assert r["success"] is True
    assert r["temp_hp_cleared"] is True
    assert r["temp_hp_before"] == 8
    assert r["temp_hp"] == 0

    # 长休：无临时生命值时不报"已清空"
    c = MockCharacter(hp=5, max_hp=20, temp_hp=0)
    r = long_rest(c)
    assert r["success"] is True
    assert r["temp_hp_cleared"] is False
    assert r["temp_hp"] == 0

    # 长休失败：不清空临时生命值
    c = MockCharacter(hp=0, max_hp=20, temp_hp=5)
    r = long_rest(c)
    assert r["success"] is False
    assert r["temp_hp_cleared"] is False

    # === 打断休息测试 ===

    # 打断短休：投掷先攻
    rs = RestState(type="short", duration=0.5)
    r = interrupt_rest(rs, INTERRUPT_ROLL_INITIATIVE)
    assert r["interrupted"] is True
    assert r["cause"] == INTERRUPT_ROLL_INITIATIVE
    assert r["rest_type"] == "short"
    assert r["short_rest_benefit_lost"] is True
    assert r["grants_short_rest_benefit"] is False
    assert r["can_continue"] is False
    assert rs.interrupted is True
    assert rs.elapsed_at_interrupt == 0.5

    # 打断短休：施展非戏法法术
    rs = RestState(type="short", duration=0.8)
    r = interrupt_rest(rs, INTERRUPT_CAST_NON_CANTRIP_SPELL)
    assert r["interrupted"] is True
    assert r["short_rest_benefit_lost"] is True

    # 打断短休：受到伤害
    rs = RestState(type="short", duration=0.3)
    r = interrupt_rest(rs, INTERRUPT_TAKE_DAMAGE)
    assert r["interrupted"] is True
    assert r["short_rest_benefit_lost"] is True

    # 打断短休：1小时行走不适用于短休
    rs = RestState(type="short", duration=0.5)
    r = interrupt_rest(rs, INTERRUPT_1HR_TRAVEL_OR_LABOR)
    assert r["interrupted"] is False
    assert "不适用于" in r["errors"][0]

    # 打断长休：投掷先攻，已休0.5h（<1h，不获短休增益）
    rs = RestState(type="long", duration=0.5)
    r = interrupt_rest(rs, INTERRUPT_ROLL_INITIATIVE)
    assert r["interrupted"] is True
    assert r["rest_type"] == "long"
    assert r["grants_short_rest_benefit"] is False  # <1h
    assert r["can_continue"] is True
    assert r["needs_extra_hours"] == 1  # 第一次打断
    assert rs.interrupt_count == 1

    # 打断长休：已休1.5h（≥1h，获短休增益）
    rs = RestState(type="long", duration=1.5)
    r = interrupt_rest(rs, INTERRUPT_TAKE_DAMAGE)
    assert r["interrupted"] is True
    assert r["grants_short_rest_benefit"] is True  # ≥1h
    assert r["can_continue"] is True
    assert r["needs_extra_hours"] == 1

    # 打断长休：1小时行走适用于长休
    rs = RestState(type="long", duration=2.0)
    r = interrupt_rest(rs, INTERRUPT_1HR_TRAVEL_OR_LABOR)
    assert r["interrupted"] is True
    assert r["grants_short_rest_benefit"] is True  # ≥1h

    # 打断长休：多次打断累加额外小时
    rs = RestState(type="long", duration=1.0)
    r1 = interrupt_rest(rs, INTERRUPT_TAKE_DAMAGE)
    assert r1["needs_extra_hours"] == 1
    assert rs.interrupt_count == 1
    # 继续休息后再次打断
    rs.interrupted = False  # 重置打断标记以继续
    rs.duration = 2.0
    r2 = interrupt_rest(rs, INTERRUPT_ROLL_INITIATIVE)
    assert r2["needs_extra_hours"] == 2  # 第二次打断
    assert rs.interrupt_count == 2

    # 打断已完成的长休应失败
    rs = RestState(type="long", duration=8.0, completed=True)
    r = interrupt_rest(rs, INTERRUPT_TAKE_DAMAGE)
    assert r["interrupted"] is False
    assert "已完成" in r["errors"][0]

    # 打断已打断的长休应失败
    rs = RestState(type="long", duration=1.0, interrupted=True)
    r = interrupt_rest(rs, INTERRUPT_TAKE_DAMAGE)
    assert r["interrupted"] is False
    assert "已被打断" in r["errors"][0]

    # === RestState.required_duration 测试 ===

    # 短休：基础1小时
    rs = RestState(type="short")
    assert rs.required_duration() == 1.0

    # 长休：基础8小时
    rs = RestState(type="long")
    assert rs.required_duration() == 8.0

    # 长休：打断1次后需9小时
    rs = RestState(type="long", interrupt_count=1)
    assert rs.required_duration() == 9.0

    # 长休：打断2次后需10小时
    rs = RestState(type="long", interrupt_count=2)
    assert rs.required_duration() == 10.0

    print("[rest] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
