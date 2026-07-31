"""施法引擎 — cast_spell / 法术位消耗 / 成分校验 / 效应结算。

依赖 engine.dice、engine.check，以及 data.spells。
标注规则ID+出处。规则依据 R-SPL-001~036。

注意: 不修改 engine/dice.py、engine/check.py、engine/damage.py。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..data.spells import Spell, get_casting_ability, get_spell, is_cantrip
from . import check, combat, damage, dice

# ──────────────────────────────────────────────────────────────────────────
# 施法者状态
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class CasterState:
    """施法者的运行时状态（持久化于角色卡）。

    规则: R-SPL-002 法术位消耗 / R-SPL-003 长休恢复 /
          R-SPL-007 每回合一法术位法术 /
          R-SPL-019 专注维持
    出处: topics/玩家手册2024/法术/法术环阶.htm ; 第七章/施法.htm
    """
    caster_id: str
    class_name: str                       # 职业名 (法师/牧师/...)
    level: int                            # 职业等级
    ability_scores: dict[str, int]        # 属性值 {"STR":10,"INT":16,...}
    spell_slots: dict[int, int] = field(default_factory=dict)  # {slot_level: remaining}
    max_spell_slots: dict[int, int] = field(default_factory=dict)
    spells_cast_with_slot_this_turn: int = 0   # R-SPL-007
    current_turn_key: str | None = None        # R-SPL-007 当前回合标识（任意回合）
    concentrating_on: str | None = None     # R-SPL-019 当前集中的法术实例ID

    def ability_mod(self, ability: str) -> int:
        """取属性调整值 = floor((score-10)/2)。

        规则: R-CHK-024 属性调整值公式
        出处: topics/玩家手册2024/进行游戏/六项属性.htm
        """
        score = self.ability_scores.get(ability, 10)
        return dice.ability_modifier(score)

    @property
    def casting_ability(self) -> str:
        """该职业的施法属性缩写。

        规则: R-SPL-021/R-SPL-022 施法属性
        出处: topics/玩家手册2024/法术/法术效应.htm
        """
        return get_casting_ability(self.class_name)

    @property
    def casting_ability_mod(self) -> int:
        """施法属性调整值。

        规则: R-SPL-021 法术豁免DC用到施法属性调整值
        出处: topics/玩家手册2024/法术/法术效应.htm
        """
        return self.ability_mod(self.casting_ability)

    @property
    def proficiency_bonus(self) -> int:
        """熟练加值（按等级查表）。

        规则: R-CHK-015 熟练加值表
        出处: topics/玩家手册2024/进行游戏/熟练.htm
        """
        return dice.proficiency_bonus(self.level)


# ──────────────────────────────────────────────────────────────────────────
# 公式：法术豁免DC / 法术攻击加值
# ──────────────────────────────────────────────────────────────────────────

def compute_spell_save_dc(caster: CasterState) -> int:
    """法术豁免 DC = 8 + 施法属性调整值 + 熟练加值。

    规则: R-SPL-021 法术豁免DC
    出处: topics/玩家手册2024/法术/法术效应.htm
    """
    return 8 + caster.casting_ability_mod + caster.proficiency_bonus


def compute_spell_attack_bonus(caster: CasterState) -> int:
    """法术攻击加值 = 施法属性调整值 + 熟练加值。

    规则: R-SPL-022 法术攻击调整值
    出处: topics/玩家手册2024/法术/法术效应.htm
    """
    return caster.casting_ability_mod + caster.proficiency_bonus


# ──────────────────────────────────────────────────────────────────────────
# 法术位消耗
# ──────────────────────────────────────────────────────────────────────────

def has_spell_slot(caster: CasterState, slot_level: int) -> bool:
    """是否有指定环阶的可用法术位。

    规则: R-SPL-002 法术位消耗
    出处: topics/玩家手册2024/法术/法术环阶.htm
    """
    return caster.spell_slots.get(slot_level, 0) > 0


def consume_spell_slot(caster: CasterState, slot_level: int) -> bool:
    """消耗一个指定环阶的法术位。

    规则: R-SPL-002 法术位消耗（spellSlots[l]-=1）
    出处: topics/玩家手册2024/法术/法术环阶.htm
    返回: 是否成功消耗
    """
    if not has_spell_slot(caster, slot_level):
        return False
    caster.spell_slots[slot_level] -= 1
    return True


def restore_slots_on_long_rest(caster: CasterState) -> None:
    """长休恢复所有已消耗的法术位。

    规则: R-SPL-003 法术位长休恢复
    出处: topics/玩家手册2024/法术/法术环阶.htm
    """
    for lvl, mx in caster.max_spell_slots.items():
        caster.spell_slots[lvl] = mx


def reset_turn_spell_count(caster: CasterState) -> None:
    """回合边界重置本回合已施展的"消耗法术位的法术"计数。

    规则: R-SPL-007 每回合一法术位法术
    出处: topics/玩家手册2024/法术/施法时间.htm
          「每个回合中，你通过施展法术的方式至多只能消耗一个法术位。」
    说明: 限制以「回合」为粒度——任何生物的回合都是新回合（在自己回合用
          法术位施法后，在敌人回合用法术位施展护盾术是合法的）。
          故应在每个回合边界（而非仅施法者自己回合开始）为所有施法者
          调用本函数；或在 cast_spell 传入 turn_key（回合唯一标识）由其
          自动在回合变更时重置。仪式施法与戏法不计入此计数。
    """
    caster.spells_cast_with_slot_this_turn = 0


# ──────────────────────────────────────────────────────────────────────────
# 成分校验（详细版）
# ──────────────────────────────────────────────────────────────────────────

# 阻止言语成分(V)的状态
_V_BLOCKING_CONDITIONS = frozenset({"沉默", "石化", "昏迷", "麻痹", "震慑"})
# 阻止姿势成分(S)的状态（失能性状态）
# 注: 束缚（Restrained）不阻止施法——其效应仅为速度0/攻击劣势/敏豁劣势，
#     被蜘蛛网缠住仍可施展有姿势成分的法术（术语汇编/状态.htm「束缚」）。
_S_BLOCKING_CONDITIONS = frozenset({"石化", "昏迷", "麻痹", "震慑", "失能"})


def check_casting_components(
    spell_components: dict,
    character_state: dict,
) -> dict:
    """校验施法成分 V/S/M 是否满足，返回结构化数据供叙述节点使用。

    规则: R-SPL-010 法术成分类型 / R-SPL-011 言语成分限制 /
          R-SPL-012 姿势成分限制 / R-SPL-013 材料成分限制与替代
    出处: topics/玩家手册2024/法术/法术成分.htm

    本函数为纯数据层，不生成面向玩家的文本。返回结构化结果由叙述节点
    （narrate）决定如何描述。

    Args:
        spell_components: 法术成分信息
            {
                "V": bool,          # 是否需要言语成分
                "S": bool,          # 是否需要姿势成分
                "M": str,           # 材料描述（"" 表示无材料成分）
                "material_cost_gp": float,  # 材料价值(>0 须实备)
                "material_consumed": bool,  # 材料是否被消耗
            }
        character_state: 角色状态
            {
                "conditions": list[str],    # 当前状态列表（如["沉默","束缚"]）
                "free_hands": int,          # 空闲手数量 (0-2)
                "has_material_pouch": bool, # 拥有材料包
                "has_focus": bool,          # 拥有法器/圣徽
                "has_specific_material": bool,  # 拥有法术指定的具体材料
            }

    Returns:
        {
            "can_cast": bool,
            "component_results": {
                "V": {"required": bool, "satisfied": bool,
                      "blocking_conditions": [...]},
                "S": {"required": bool, "satisfied": bool,
                      "blocking_conditions": [...], "free_hands": int},
                "M": {"required": bool, "satisfied": bool,
                      "material_desc": str, "needs_specific": bool,
                      "has_pouch": bool, "has_focus": bool,
                      "has_specific": bool},
            },
            "materials_needed": [str],  # 缺少的材料描述列表
        }
    """
    conditions = set(character_state.get("conditions", []))
    free_hands = character_state.get("free_hands", 2)
    component_results: dict = {}
    materials_needed: list[str] = []

    # --- V（言语）校验 ---
    # 规则: R-SPL-011 言语成分限制 — 施法者必须能说话
    v_required = bool(spell_components.get("V"))
    if v_required:
        blocking_v = sorted(conditions & _V_BLOCKING_CONDITIONS)
        v_satisfied = len(blocking_v) == 0
    else:
        blocking_v = []
        v_satisfied = True
    component_results["V"] = {
        "required": v_required,
        "satisfied": v_satisfied,
        "blocking_conditions": blocking_v,
    }

    # --- S（姿势）校验 ---
    # 规则: R-SPL-012 姿势成分限制 — 至少一只空闲的手
    s_required = bool(spell_components.get("S"))
    if s_required:
        blocking_s = sorted(conditions & _S_BLOCKING_CONDITIONS)
        if blocking_s:
            s_satisfied = False
        elif free_hands < 1:
            s_satisfied = False
            blocking_s = ["双手被占用"]
        else:
            s_satisfied = True
    else:
        blocking_s = []
        s_satisfied = True
    component_results["S"] = {
        "required": s_required,
        "satisfied": s_satisfied,
        "blocking_conditions": blocking_s,
        "free_hands": free_hands,
    }

    # --- M（材料）校验 ---
    # 规则: R-SPL-013 材料成分限制与替代
    m_desc = spell_components.get("M", "")
    m_required = bool(m_desc)
    if m_required:
        material_cost = spell_components.get("material_cost_gp", 0)
        material_consumed = spell_components.get("material_consumed", False)
        needs_specific = material_cost > 0 or material_consumed
        has_pouch = character_state.get("has_material_pouch", False)
        has_focus = character_state.get("has_focus", False)
        has_specific = character_state.get("has_specific_material", False)

        if needs_specific:
            m_satisfied = has_specific
        else:
            m_satisfied = has_pouch or has_focus

        if not m_satisfied:
            materials_needed.append(m_desc)
    else:
        needs_specific = False
        has_pouch = False
        has_focus = False
        m_satisfied = True

    component_results["M"] = {
        "required": m_required,
        "satisfied": m_satisfied,
        "material_desc": m_desc,
        "needs_specific": needs_specific,
        "has_pouch": has_pouch,
        "has_focus": has_focus,
        "has_specific": character_state.get("has_specific_material", False),
    }

    can_cast = v_satisfied and s_satisfied and m_satisfied

    return {
        "can_cast": can_cast,
        "component_results": component_results,
        "materials_needed": materials_needed,
    }


# ──────────────────────────────────────────────────────────────────────────
# 成分校验（布尔版，供 cast_spell 内部使用）
# ──────────────────────────────────────────────────────────────────────────

def can_cast_by_components(spell: Spell, caster: CasterState,
                           *, muted: bool = False, silenced: bool = False,
                           free_hands: int = 2,
                           has_material_pouch: bool = False,
                           has_focus: bool = False,
                           has_specific_material: bool = False) -> bool:
    """校验施法者是否满足法术全部成分需求。

    规则: R-SPL-010 法术成分类型 / R-SPL-011 言语成分限制 /
          R-SPL-012 姿势成分限制 / R-SPL-013 材料成分限制与替代
    出处: topics/玩家手册2024/法术/法术成分.htm

    参数:
        muted/silenced: 不能说话/处于沉默区域 → V 失败
        free_hands: 空手数量 → S/M 各需一只空手
        has_material_pouch: 拥有材料包
        has_focus: 拥有法器（且具有使用法器的特性）
        has_specific_material: 实际持有法术所指定的具体材料
            （对有指定价格或被消耗的材料是必需的——材料包/法器不可替代）
    """
    comps = spell.components

    # R-SPL-011 言语成分限制
    if "V" in comps and (muted or silenced):
        return False

    # R-SPL-012 姿势成分限制：至少空出一只手
    if "S" in comps and free_hands < 1:
        return False

    # R-SPL-013 材料成分限制与替代
    if "M" in comps:
        # 有指定价格或被消耗的材料须实备，材料包/法器不可替代
        needs_specific = spell.material_cost_gp > 0 or spell.material_consumed
        if needs_specific:
            # 必须实际持有该具体材料（有价/消耗材料不可由材料包或法器替代）
            if not has_specific_material:
                return False
        else:
            # 可用材料包或法器替代
            if not (has_material_pouch or has_focus):
                return False
        # 材料成分同样需要一只空手
        if free_hands < 1:
            return False

    return True


# ──────────────────────────────────────────────────────────────────────────
# 升环效应解析
# ──────────────────────────────────────────────────────────────────────────

def resolve_upcast(spell: Spell, slot_level: int, caster_level: int) -> dict:
    """根据施展用的法术位环阶解析升环效应。

    规则: R-SPL-004 升环施法（effectiveLevel=chosenSlotLevel）
    出处: topics/玩家手册2024/法术/法术环阶.htm

    返回 dict 含：
        effective_level: 实际生效环阶
        damage_dice: 伤害骰表达式（含升环加骰）
        heal_dice: 治疗骰表达式（含升环加骰）
        num_attacks: 攻击次数（灼热射线）
        num_darts: 飞镖数（魔法飞弹）
    """
    eff_level = max(spell.level, slot_level)
    levels_above = eff_level - spell.level

    result = {
        "effective_level": eff_level,
        "damage_dice": spell.damage_dice,
        "heal_dice": spell.heal_dice,
        "num_attacks": 1,
        "num_darts": 0,
        "num_targets": 1,
    }

    uc = spell.upcast or {}

    # 戏法随等级提升伤害（火焰箭）
    if "cantrip_scaling" in uc:
        bonus_dice = ""
        for threshold, dice_expr in uc["cantrip_scaling"]:
            if caster_level >= threshold:
                bonus_dice = dice_expr
        if bonus_dice:
            result["damage_dice"] = f"{spell.damage_dice}+{bonus_dice}"

    # 魔能爆型戏法：5/11/17级射线数递增
    if "beam_scaling" in uc:
        for threshold, count in uc["beam_scaling"]:
            if caster_level >= threshold:
                result["num_attacks"] = count

    # 魔法飞弹：每升一环多一支飞镖
    if uc.get("base_darts") is not None:
        result["num_darts"] = uc["base_darts"] + levels_above * uc.get("darts_per_level", 1)

    # 灼热射线：每升一环多一道射线
    if uc.get("base_rays") is not None:
        result["num_attacks"] = uc["base_rays"] + levels_above * uc.get("rays_per_level", 1)

    # 升环多目标（隐形术等）：每升一环多 N 个目标
    # 规则: R-SPL-004 升环施法（targets_per_level 字段）
    if uc.get("targets_per_level"):
        base_targets = uc.get("base_targets", 1)
        result["num_targets"] = base_targets + levels_above * uc["targets_per_level"]

    # 火球术/闪电束：每升一环多 1d6
    if uc.get("per_level_above_base") == "+1d6" and levels_above > 0:
        base = spell.damage_dice  # e.g. "8d6"
        # 解析基础骰数
        import re as _re
        m = _re.match(r"(\d+)d(\d+)", base)
        if m:
            count = int(m.group(1)) + levels_above
            sides = int(m.group(2))
            result["damage_dice"] = f"{count}d{sides}"

    # 治疗法术升环加骰
    pl = uc.get("per_level_above_base", "")
    if spell.heal_dice and levels_above > 0:
        if pl == "+2d4":
            result["heal_dice"] = f"{spell.heal_dice}+{2*levels_above}d4"
        elif pl == "+2d8":
            result["heal_dice"] = f"{spell.heal_dice}+{2*levels_above}d8"
        elif pl == "+1d4":
            result["heal_dice"] = f"{spell.heal_dice}+{levels_above}d4"

    # 通用升环加骰（自动解析表法术的 "+1d8"/"+2d6" 等非特判格式）
    # 规则: R-SPL-004 升环施法 — 每高一环伤害/治疗增加 NdM
    import re as _re2
    if (levels_above > 0 and pl and pl not in ("+1d6", "+2d4", "+2d8", "+1d4")
            and _re2.fullmatch(r"\+\d+d\d+", pl)):
        _um = _re2.match(r"\+(\d+)d(\d+)", pl)
        _n, _s = int(_um.group(1)), int(_um.group(2))
        if spell.damage_dice:
            _bm = _re2.match(r"(\d+)d(\d+)", spell.damage_dice)
            if _bm and int(_bm.group(2)) == _s:
                result["damage_dice"] = f"{int(_bm.group(1)) + _n*levels_above}d{_s}"
            else:
                result["damage_dice"] = f"{spell.damage_dice}+{_n*levels_above}d{_s}"
        if spell.heal_dice:
            result["heal_dice"] = f"{spell.heal_dice}+{_n*levels_above}d{_s}"

    return result


# ──────────────────────────────────────────────────────────────────────────
# cast_spell 主函数
# ──────────────────────────────────────────────────────────────────────────

def cast_spell(
    caster: CasterState,
    spell_name: str,
    slot_level: int | None = None,
    targets: list[dict] | None = None,
    *,
    concentration_mgr: Any | None = None,
    component_kwargs: dict | None = None,
    ritual: bool = False,
    combatant: Any | None = None,
    has_reaction_available: bool = True,
    turn_key: str | None = None,
) -> dict:
    """施展一道法术，返回完整结果字典。

    规则: R-SPL-001~036 施法全流程
    出处: topics/玩家手册2024/第七章/施法.htm ; 法术详述/{0..3}环.htm

    参数:
        caster: 施法者状态
        spell_name: 法术中文名
        slot_level: 使用的法术位环阶（戏法传 None 或 0）
        targets: 目标列表 [{"ac":15,"save_bonus":3,"save_prof":True,...}, ...]
        concentration_mgr: ConcentrationManager 实例（用于集中管理）
        component_kwargs: 成分校验参数（muted/free_hands 等）
        ritual: 是否作为仪式施展（R-SPL-005）。当 ritual=True 且
            spell.ritual=True 时不消耗法术位，但施法时间+10分钟。
        combatant: 战斗参战者（combat.Combatant），用于反应施法时
            通过 combat.use_reaction 真正扣减反应（R-SPL-006）。
        has_reaction_available: 反应是否可用（无 combatant 时校验用，
            默认 True）。反应法术在反应不可用时被拒绝。
        turn_key: 当前回合的唯一标识（如 "r3:goblin1"）。R-SPL-007 的
            「每回合一法术位」限制以任意回合为粒度；传入后若与上次
            施法的回合不同则自动重置计数（支持在敌人回合用法术位
            施展反应法术）。不传则沿用 reset_turn_spell_count 手动重置。

    返回 dict:
        success: bool — 是否成功施展并产生效应
        spell: str — 法术名
        slot_level: int — 消耗的法术位环阶（0=戏法）
        slot_consumed: bool — 是否消耗了法术位
        ritual: bool — 是否以仪式方式施展
        ritual_time_extra: int — 仪式额外施法时间（秒）。仪式时为 600（10分钟），
            非仪式时为 0。调用方可据此计算总施法时间。
        effect_type: str — 效应类型
        save_dc: int — 法术豁免DC（如有）
        attack_bonus: int — 法术攻击加值（如有）
        results: list — 每个目标的效应结果
        concentration_set: bool — 是否设置了集中
        errors: list — 失败原因列表
    """
    spell = get_spell(spell_name)
    targets = targets or []
    comp_kw = component_kwargs or {}

    errors: list[str] = []

    # —— 戏法处理 ——
    if is_cantrip(spell):
        slot_level = 0

    # —— 仪式施法 (R-SPL-005) ——
    # 可仪式施展的法术：施法时间+10分钟、不消耗法术位（亦不计入每回合计数）
    ritual_cast = False
    ritual_time_extra = 0  # 仪式额外施法时间（秒），10分钟=600秒
    if ritual:
        if not spell.ritual:
            errors.append("该法术不具备仪式标签，不可仪式施法")
            return _fail(spell, slot_level, errors, ritual=False)
        ritual_cast = True
        ritual_time_extra = 600  # R-SPL-005 仪式施法额外时间：10分钟（600秒）

    if not ritual_cast and not is_cantrip(spell):
        # 非仪式法术：非戏法必须指定法术位环阶
        if slot_level is None:
            errors.append("非戏法必须指定 slot_level")
            return _fail(spell, slot_level, errors)
        if slot_level < spell.level:
            errors.append(f"法术位环阶 {slot_level} 低于法术环阶 {spell.level}")
            return _fail(spell, slot_level, errors)

    # —— 成分校验 (R-SPL-010~013) ——
    if not can_cast_by_components(spell, caster, **comp_kw):
        errors.append("成分不满足（V/S/M）")
        return _fail(spell, slot_level, errors, ritual=ritual_cast)

    # —— 反应施法 (R-SPL-006) ——
    # 施法时间为反应的法术须消耗一个反应
    if spell.casting_time_type == "REACTION":
        if combatant is not None:
            # 真正扣减反应（combat.use_reaction）
            if not combat.use_reaction(combatant):
                errors.append("反应已消耗，不可施展反应法术")
                return _fail(spell, slot_level, errors, ritual=ritual_cast)
        elif not has_reaction_available:
            errors.append("反应不可用，不可施展反应法术")
            return _fail(spell, slot_level, errors, ritual=ritual_cast)

    # —— 法术位消耗 (R-SPL-002) + 每回合一法术位法术 (R-SPL-007) ——
    slot_consumed = False
    if not ritual_cast and not is_cantrip(spell):
        # R-SPL-007 回合切换自动重置：turn_key 变更说明已进入新回合
        # （任意生物的回合都是新回合，反应法术在敌方回合施展不受
        # 自己回合已用法术位的限制）
        if turn_key is not None and turn_key != caster.current_turn_key:
            caster.spells_cast_with_slot_this_turn = 0
            caster.current_turn_key = turn_key
        # R-SPL-007 强制检查：本回合已施展过消耗法术位的法术则拒绝
        if caster.spells_cast_with_slot_this_turn > 0:
            errors.append("本回合已施展过消耗法术位的法术（每回合一法术位法术）")
            return _fail(spell, slot_level, errors, ritual=ritual_cast)
        if not has_spell_slot(caster, slot_level):
            errors.append(f"无可用 {slot_level} 环法术位")
            return _fail(spell, slot_level, errors, ritual=ritual_cast)
        consume_spell_slot(caster, slot_level)
        slot_consumed = True
        # R-SPL-007 每回合一法术位法术计数
        caster.spells_cast_with_slot_this_turn += 1

    # —— 升环效应解析 (R-SPL-004) ——
    upcast_info = resolve_upcast(spell, slot_level or 0, caster.level)

    save_dc = compute_spell_save_dc(caster) if spell.effect_type == "saving_throw" else 0
    attack_bonus = compute_spell_attack_bonus(caster) if spell.effect_type == "attack_roll" else 0

    # —— 结算法术效应 ——
    results: list[dict] = []

    if spell.effect_type == "attack_roll":
        # 攻击检定型法术（火焰箭、灼热射线）
        num_attacks = upcast_info.get("num_attacks", 1)
        dmg_expr = upcast_info.get("damage_dice", spell.damage_dice)
        for tgt in targets:
            ac = tgt.get("ac", 10)
            atk = check.attack_roll(bonus=attack_bonus, ac=ac)
            tgt_result = {
                "target_index": targets.index(tgt),
                "attack_roll": atk.d20,
                "attack_total": atk.total,
                "hit": atk.hit,
                "crit": atk.crit,
                "damage": None,
            }
            if atk.hit:
                # 经伤害管线：抗性→修正→易伤→免疫（R-DMG-004~009），目标抗性从 tgt 取
                dr = damage.roll_damage(
                    damage.DamageRequest(
                        dice_expr=dmg_expr,
                        damage_type=spell.damage_type,
                        ability_mod=0,
                        add_mod=False,
                        crit=atk.crit,
                    ),
                    resistances=tgt.get("resistances", []),
                    vulnerabilities=tgt.get("vulnerabilities", []),
                    immunities=tgt.get("immunities", []),
                )
                tgt_result["damage"] = {
                    "dice": dmg_expr,
                    "rolls": dr.dice_rolls,
                    "total": dr.final,
                    "type": spell.damage_type,
                    "crit": atk.crit,
                    "resisted": dr.resisted,
                    "vulnerable": dr.vulnerable,
                    "immune": dr.immune,
                }
            results.append(tgt_result)

    elif spell.effect_type == "saving_throw":
        # 豁免型法术（火球术、闪电束）—— 区域法术对全体目标一次掷骰、共享伤害
        dmg_expr = upcast_info.get("damage_dice", spell.damage_dice)
        base_roll = dice.roll_dice(dmg_expr)  # 全体共享的一次掷骰
        for tgt in targets:
            save_bonus = tgt.get("save_bonus", 0)
            save_prof = tgt.get("save_prof", False)
            prof_bonus = tgt.get("prof_bonus", caster.proficiency_bonus)
            sv = check.saving_throw(
                mod=save_bonus,
                prof=prof_bonus,
                proficient=save_prof,
                dc=save_dc,
            )
            # 经伤害管线（抗性→修正→易伤→免疫）后，再按豁免成败全/半效。
            # 抗性 + 豁免成功 = 1/4（管线先减半，豁免再减半）。
            piped = damage.apply_damage_pipeline(
                raw=base_roll.total,
                damage_type=spell.damage_type,
                resistances=tgt.get("resistances", []),
                vulnerabilities=tgt.get("vulnerabilities", []),
                immunities=tgt.get("immunities", []),
            )
            applied = dice.round_down(piped.final / 2) if sv.success else piped.final

            tgt_result = {
                "target_index": targets.index(tgt),
                "save_roll": sv.d20,
                "save_total": sv.total,
                "save_success": sv.success,
                "dc": save_dc,
                "damage": {
                    "dice": dmg_expr,
                    "rolls": base_roll.dice_rolls,
                    "total": applied,
                    "type": spell.damage_type,
                    "halved": sv.success,
                    "resisted": piped.resisted,
                    "vulnerable": piped.vulnerable,
                    "immune": piped.immune,
                },
            }
            results.append(tgt_result)

    elif spell.effect_type == "automatic":
        # 自动命中型法术（魔法飞弹）
        if spell.name == "魔法飞弹":
            num_darts = upcast_info.get("num_darts", 3)
            per_dart = dice.roll_dice(spell.damage_dice)  # 1d4+1
            total_dmg = per_dart.total * num_darts
            results.append({
                "num_darts": num_darts,
                "per_dart_damage": per_dart.total,
                "damage": {
                    "dice": spell.damage_dice,
                    "rolls": [per_dart.total] * num_darts,
                    "total": total_dmg,
                    "type": spell.damage_type,
                },
            })
        else:
            # 其他自动型法术（光亮术等）—— 仅产生效应标记
            results.append({"effect": "applied", "description": spell.description[:80]})

    elif spell.effect_type == "heal":
        # 治疗型法术（治愈真言、治疗伤势）
        heal_expr = upcast_info.get("heal_dice", spell.heal_dice)
        add_mod = spell.add_casting_mod_to_heal
        for tgt in targets:
            heal_roll = dice.roll_dice(heal_expr)
            heal_total = heal_roll.total
            if add_mod:
                heal_total += caster.casting_ability_mod
            tgt_result = {
                "target_index": targets.index(tgt),
                "heal": {
                    "dice": heal_expr,
                    "rolls": heal_roll.dice_rolls,
                    "total": max(0, heal_total),
                    "added_mod": caster.casting_ability_mod if add_mod else 0,
                },
            }
            results.append(tgt_result)

    elif spell.effect_type == "shield":
        # 护盾术：反应 +5 AC
        results.append({
            "ac_bonus": spell.ac_bonus,
            "duration": spell.duration,
            "effect": "shield_active",
        })

    # —— 集中设置 (R-SPL-019) ——
    concentration_set = False
    if spell.concentration:
        if concentration_mgr is not None:
            concentration_mgr.set_concentration(caster.caster_id, f"{spell.name}_{caster.caster_id}")
            concentration_set = True
        else:
            # 无管理器时直接设置施法者字段
            caster.concentrating_on = f"{spell.name}_{caster.caster_id}"
            concentration_set = True

    return {
        "success": True,
        "spell": spell.name,
        "level": spell.level,
        "slot_level": slot_level,
        "slot_consumed": slot_consumed,
        "ritual": ritual_cast,
        "ritual_time_extra": ritual_time_extra,  # R-SPL-005 仪式额外施法时间（秒），非仪式时为0
        "effect_type": spell.effect_type,
        "save_dc": save_dc,
        "attack_bonus": attack_bonus,
        "effective_level": upcast_info.get("effective_level", spell.level),
        "results": results,
        "concentration_set": concentration_set,
        "errors": [],
    }


def _fail(spell: Spell, slot_level: int | None, errors: list[str],
          *, ritual: bool = False) -> dict:
    """构造失败结果。"""
    return {
        "success": False,
        "spell": spell.name,
        "level": spell.level,
        "slot_level": slot_level or 0,
        "slot_consumed": False,
        "ritual": ritual,
        "ritual_time_extra": 0,
        "effect_type": spell.effect_type,
        "save_dc": 0,
        "attack_bonus": 0,
        "effective_level": spell.level,
        "results": [],
        "concentration_set": False,
        "errors": errors,
    }


# ──────────────────────────────────────────────────────────────────────────
# 法器职业限制
# ──────────────────────────────────────────────────────────────────────────

# 法器类型 → 可使用该法器的职业集合
# 规则: R-SPL-013 法器职业限制（奥术/德鲁伊/圣徽/乐器）
# 出处: topics/玩家手册2024/装备/冒险装备.htm ; 吟游诗人.htm
#   - 奥术法器 Arcane Focus: 术士、魔契师、法师
#   - 德鲁伊法器 Druidic Focus: 德鲁伊、游侠
#   - 圣徽 Holy Symbol: 牧师、圣武士
#   - 乐器 Musical Instrument: 吟游诗人（可用乐器作为施法法器）
_FOCUS_CLASS_ACCESS: dict[str, frozenset[str]] = {
    "奥术法器": frozenset({"术士", "魔契师", "法师"}),
    "德鲁伊法器": frozenset({"德鲁伊", "游侠"}),
    "圣徽": frozenset({"牧师", "圣武士"}),
    "乐器": frozenset({"吟游诗人"}),
}


def can_use_focus(char_class: str, focus_type: str) -> bool:
    """校验职业能否使用该类法器。

    规则: R-SPL-013 法器职业限制（奥术/德鲁伊/圣徽/乐器）
    出处: topics/玩家手册2024/装备/冒险装备.htm ; 职业/吟游诗人.htm
          - 奥术法器: 术士、魔契师、法师
          - 德鲁伊法器: 德鲁伊、游侠
          - 圣徽: 牧师、圣武士
          - 乐器: 吟游诗人

    参数:
        char_class: 职业名（法师/牧师/德鲁伊/术士/魔契师/圣武士/游侠/吟游诗人）
        focus_type: 法器类型（"奥术法器"/"德鲁伊法器"/"圣徽"/"乐器"）
    返回: 该职业是否可使用该类法器作为材料成分替代。
    """
    classes = _FOCUS_CLASS_ACCESS.get(focus_type)
    if classes is None:
        return False
    return char_class in classes


# ──────────────────────────────────────────────────────────────────────────
# 长时间施展（施法时间≥1分钟）
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class LongCastProgress:
    """长时间施法进度（施法时间≥1分钟）。

    规则: R-SPL-006 长时间施展
    出处: topics/玩家手册2024/法术/施法时间.htm
          「施法时间为1分钟或更久时，必须在施法期间每个自己的回合
            执行魔法动作并保持专注；失去专注则法术失败但不耗法术位。」
    """
    caster_id: str
    spell_name: str
    slot_level: int                       # 完成时消耗的法术位环阶
    total_turns: int                      # 所需总回合数（按施法时间换算）
    turns_done: int = 0                   # 已完成的回合数
    concentration_lost: bool = False      # 是否因失去专注而失败

    @property
    def completed(self) -> bool:
        return self.turns_done >= self.total_turns

    @property
    def failed(self) -> bool:
        return self.concentration_lost


def cast_long_spell(
    caster: CasterState,
    spell_name: str,
    slot_level: int | None = None,
    *,
    casting_turns: int = 10,
    concentration_mgr: Any | None = None,
    component_kwargs: dict | None = None,
) -> dict:
    """开始一道长时间施法（施法时间≥1分钟）。

    规则: R-SPL-006 长时间施展
    出处: topics/玩家手册2024/法术/施法时间.htm
          施法时间为1分钟或更久时，必须在施法期间每个自己的回合执行
          魔法动作并保持专注；失去专注则法术失败，但不消耗法术位。

    参数:
        caster: 施法者状态
        spell_name: 法术中文名
        slot_level: 完成时消耗的法术位环阶（默认取法术本身环阶）
        casting_turns: 所需回合数（1分钟≈10轮，由调用方按施法时间换算）
        concentration_mgr: 集中管理器（长施法需保持专注）
        component_kwargs: 成分校验参数

    返回 dict:
        success: bool — 是否成功开始长施法
        spell: str — 法术名
        progress: LongCastProgress — 进度状态（每回合由 advance_long_spell 推进）
        errors: list
    说明: 本函数仅开始施法并设置专注；法术位在完成时（advance_long_spell）
          才消耗。每回合的魔法动作消耗应由调用方在动作经济中扣减。
    """
    spell = get_spell(spell_name)
    comp_kw = component_kwargs or {}
    errors: list[str] = []

    # 成分校验 (R-SPL-010~013)
    if not can_cast_by_components(spell, caster, **comp_kw):
        errors.append("成分不满足（V/S/M）")
        return {"success": False, "spell": spell.name, "progress": None, "errors": errors}

    eff_slot = slot_level if slot_level is not None else spell.level

    progress = LongCastProgress(
        caster_id=caster.caster_id,
        spell_name=spell.name,
        slot_level=eff_slot,
        total_turns=casting_turns,
    )

    # 长施法需保持专注 (R-SPL-006)
    if concentration_mgr is not None:
        concentration_mgr.set_concentration(caster.caster_id, f"{spell.name}_{caster.caster_id}")
    else:
        caster.concentrating_on = f"{spell.name}_{caster.caster_id}"

    return {"success": True, "spell": spell.name, "progress": progress, "errors": []}


def advance_long_spell(
    caster: CasterState,
    progress: LongCastProgress,
    *,
    concentration_broken: bool = False,
    concentration_mgr: Any | None = None,
    targets: list[dict] | None = None,
    component_kwargs: dict | None = None,
) -> dict:
    """推进长时间施法一个回合。

    规则: R-SPL-006 长时间施展
          每回合需执行魔法动作（由调用方在动作经济中扣减）+ 保持专注。
          专注失败 → 法术失败，不消耗法术位。
          完成全部回合 → 消耗法术位并结算法术效应（转入 cast_spell）。

    参数:
        caster: 施法者状态
        progress: 长施法进度（cast_long_spell 返回）
        concentration_broken: 本回合是否失去专注
        concentration_mgr: 集中管理器
        targets: 完成时结算法术的目标列表
        component_kwargs: 完成时结算法术的成分校验参数

    返回 dict:
        completed: bool — 是否已完成全部回合
        failed: bool — 是否因专注失败而中断
        slot_consumed: bool — 是否在本回合消耗了法术位（完成时）
        result: dict — 完成时 cast_spell 的结果（未完成为 None）
    """
    # 专注失败 → 法术失败，不耗法术位 (R-SPL-006)
    if concentration_broken:
        progress.concentration_lost = True
        if concentration_mgr is not None:
            concentration_mgr.break_concentration(caster.caster_id)
        else:
            caster.concentrating_on = None
        return {"completed": False, "failed": True, "slot_consumed": False, "result": None}

    progress.turns_done += 1
    if progress.turns_done < progress.total_turns:
        return {"completed": False, "failed": False, "slot_consumed": False, "result": None}

    # 完成：消耗法术位并结算法术效应
    r = cast_spell(
        caster, progress.spell_name, progress.slot_level,
        targets=targets,
        concentration_mgr=concentration_mgr,
        component_kwargs=component_kwargs,
    )
    return {
        "completed": True,
        "failed": False,
        "slot_consumed": r.get("slot_consumed", False),
        "result": r,
    }


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    from .concentration import ConcentrationManager

    # 构造一个 3级法师 INT16
    wiz = CasterState(
        caster_id="wiz1",
        class_name="法师",
        level=3,
        ability_scores={"STR": 10, "DEX": 14, "CON": 12, "INT": 16, "WIS": 10, "CHA": 10},
        spell_slots={1: 4, 2: 2},
        max_spell_slots={1: 4, 2: 2},
    )

    # 施法属性 (R-SPL-021)
    assert wiz.casting_ability == "INT"
    assert wiz.casting_ability_mod == 3  # (16-10)/2=3
    assert wiz.proficiency_bonus == 2    # 3级 → +2

    # 法术豁免DC = 8 + 3 + 2 = 13 (R-SPL-021)
    assert compute_spell_save_dc(wiz) == 13
    # 法术攻击加值 = 3 + 2 = 5 (R-SPL-022)
    assert compute_spell_attack_bonus(wiz) == 5

    # —— 火焰箭（戏法，攻击检定，1d10 fire）——
    r = cast_spell(wiz, "火焰箭", slot_level=0,
                   targets=[{"ac": 12}],
                   component_kwargs={"free_hands": 2})
    assert r["success"] is True
    assert r["slot_consumed"] is False       # 戏法不消耗法术位
    assert r["effect_type"] == "attack_roll"
    assert r["attack_bonus"] == 5
    assert len(r["results"]) == 1
    # 命中则有伤害
    if r["results"][0]["hit"]:
        assert r["results"][0]["damage"]["type"] == "fire"

    # —— 魔法飞弹（1环，自动命中，3×1d4+1 force）——
    reset_turn_spell_count(wiz)              # 每回合仅一法术位法术：新回合
    r = cast_spell(wiz, "魔法飞弹", slot_level=1,
                   targets=[{"ac": 20}],  # 高AC但自动命中
                   component_kwargs={"free_hands": 2})
    assert r["success"] is True
    assert r["slot_consumed"] is True        # 消耗1环法术位
    assert wiz.spell_slots[1] == 3           # 4-1=3
    assert r["effect_type"] == "automatic"
    mm_res = r["results"][0]
    assert mm_res["num_darts"] == 3
    # 每发 1d4+1 ∈ [2,5]，总伤害 ∈ [6,15]
    assert 6 <= mm_res["damage"]["total"] <= 15
    assert mm_res["damage"]["type"] == "force"

    # —— 火球术（3环，DEX豁免，8d6 fire）——
    # 先给法师3环法术位
    wiz.spell_slots[3] = 1
    wiz.max_spell_slots[3] = 1
    reset_turn_spell_count(wiz)              # 新回合
    r = cast_spell(wiz, "火球术", slot_level=3,
                   targets=[{"ac": 15, "save_bonus": 2, "save_prof": True, "prof_bonus": 2}],
                   component_kwargs={"free_hands": 2, "has_material_pouch": True})
    assert r["success"] is True
    assert r["slot_consumed"] is True
    assert r["effect_type"] == "saving_throw"
    assert r["save_dc"] == 13
    fb_res = r["results"][0]
    assert fb_res["dc"] == 13
    # 8d6 ∈ [8,48]
    assert 8 <= fb_res["damage"]["total"] <= 48
    assert fb_res["damage"]["type"] == "fire"
    # 成功豁免则伤害减半
    if fb_res["save_success"]:
        assert fb_res["damage"]["halved"] is True

    # —— 治愈真言（1环，附赠动作，治疗 2d4+施法属性）——
    # 用牧师 WIS16
    cle = CasterState(
        caster_id="cle1",
        class_name="牧师",
        level=3,
        ability_scores={"STR": 10, "DEX": 10, "CON": 14, "INT": 10, "WIS": 16, "CHA": 12},
        spell_slots={1: 4, 2: 2},
        max_spell_slots={1: 4, 2: 2},
    )
    r = cast_spell(cle, "治愈真言", slot_level=1,
                   targets=[{}],
                   component_kwargs={"free_hands": 2})
    assert r["success"] is True
    assert r["effect_type"] == "heal"
    hw_res = r["results"][0]
    # 2d4 ∈ [2,8]，+WIS3 → 总治疗 ∈ [5,11]
    assert 5 <= hw_res["heal"]["total"] <= 11
    assert hw_res["heal"]["added_mod"] == 3

    # —— 护盾术（1环，反应，+5 AC）——
    reset_turn_spell_count(wiz)              # 新回合
    r = cast_spell(wiz, "护盾术", slot_level=1,
                   targets=[{}],
                   component_kwargs={"free_hands": 2})
    assert r["success"] is True
    assert r["effect_type"] == "shield"
    assert r["results"][0]["ac_bonus"] == 5

    # —— 隐形术（2环，专注）—— 需要集中管理
    reset_turn_spell_count(wiz)              # 新回合
    mgr = ConcentrationManager()
    r = cast_spell(wiz, "隐形术", slot_level=2,
                   targets=[{}],
                   concentration_mgr=mgr,
                   component_kwargs={"free_hands": 2, "has_material_pouch": True})
    assert r["success"] is True
    assert r["concentration_set"] is True
    assert mgr.get_active_concentration("wiz1") is not None

    # —— 成分不足应失败 ——
    # 言语成分被堵嘴
    r = cast_spell(wiz, "火焰箭", slot_level=0,
                   targets=[{"ac": 12}],
                   component_kwargs={"free_hands": 2, "muted": True})
    assert r["success"] is False
    assert "成分不满足" in r["errors"][0]

    # 法术位不足应失败
    wiz_low = CasterState(
        caster_id="low", class_name="法师", level=1,
        ability_scores={"INT": 16, "STR": 10, "DEX": 10, "CON": 10, "WIS": 10, "CHA": 10},
        spell_slots={1: 0}, max_spell_slots={1: 2},
    )
    r = cast_spell(wiz_low, "魔法飞弹", slot_level=1,
                   targets=[{"ac": 20}],
                   component_kwargs={"free_hands": 2})
    assert r["success"] is False
    assert "无可用" in r["errors"][0]

    # —— 升环施法 (R-SPL-004) ——
    # 用3环法术位施展火球术 → 8d6；用4环 → 9d6
    wiz4 = CasterState(
        caster_id="w4", class_name="法师", level=7,
        ability_scores={"INT": 18, "STR": 10, "DEX": 10, "CON": 14, "WIS": 10, "CHA": 10},
        spell_slots={1: 4, 2: 3, 3: 3, 4: 1},
        max_spell_slots={1: 4, 2: 3, 3: 3, 4: 1},
    )
    # 3环位
    reset_turn_spell_count(wiz4)             # 新回合
    r3 = cast_spell(wiz4, "火球术", slot_level=3,
                    targets=[{"save_bonus": 0, "save_prof": False, "prof_bonus": 0, "ac": 10}],
                    component_kwargs={"free_hands": 2, "has_material_pouch": True})
    assert r3["effective_level"] == 3
    # 4环位升环
    reset_turn_spell_count(wiz4)             # 新回合
    r4 = cast_spell(wiz4, "火球术", slot_level=4,
                    targets=[{"save_bonus": 0, "save_prof": False, "prof_bonus": 0, "ac": 10}],
                    component_kwargs={"free_hands": 2, "has_material_pouch": True})
    assert r4["effective_level"] == 4
    # 4环伤害骰应为 9d6
    assert r4["results"][0]["damage"]["dice"] == "9d6"

    # —— 长休恢复法术位 (R-SPL-003) ——
    restore_slots_on_long_rest(wiz4)
    assert wiz4.spell_slots[4] == 1  # 恢复满

    # —— 每回合一法术位法术 强制检查 (R-SPL-007) ——
    reset_turn_spell_count(wiz4)             # 新回合
    r = cast_spell(wiz4, "魔法飞弹", slot_level=1,
                   targets=[{"ac": 20}],
                   component_kwargs={"free_hands": 2})
    assert r["success"] is True
    # 同回合再施展一道消耗法术位的法术 → 被拒
    r2 = cast_spell(wiz4, "魔法飞弹", slot_level=1,
                    targets=[{"ac": 20}],
                    component_kwargs={"free_hands": 2})
    assert r2["success"] is False
    assert "本回合" in r2["errors"][0]
    # 戏法不受此限制（仍可施展）
    r_cantrip = cast_spell(wiz4, "火焰箭", slot_level=0,
                           targets=[{"ac": 12}],
                           component_kwargs={"free_hands": 2})
    assert r_cantrip["success"] is True
    # 回合重置后又可施展消耗法术位的法术
    reset_turn_spell_count(wiz4)
    r3 = cast_spell(wiz4, "魔法飞弹", slot_level=1,
                    targets=[{"ac": 20}],
                    component_kwargs={"free_hands": 2})
    assert r3["success"] is True

    # —— 仪式施法 (R-SPL-005) —— 鉴定术可仪式施展，不耗法术位
    reset_turn_spell_count(wiz4)
    slots_before = dict(wiz4.spell_slots)
    r = cast_spell(wiz4, "鉴定术", ritual=True,
                   component_kwargs={"free_hands": 2, "has_specific_material": True})
    assert r["success"] is True
    assert r["slot_consumed"] is False
    assert r["ritual"] is True
    assert wiz4.spell_slots == slots_before          # 仪式施法不消耗法术位
    assert wiz4.spells_cast_with_slot_this_turn == 0  # 仪式不计入每回合计数
    # 非仪式法术不可作为仪式施展
    r_bad = cast_spell(wiz4, "魔法飞弹", slot_level=1, ritual=True,
                       targets=[{"ac": 20}],
                       component_kwargs={"free_hands": 2})
    assert r_bad["success"] is False
    assert "仪式" in r_bad["errors"][0]

    # —— 材料成分有价/消耗校验 (R-SPL-013) ——
    # 鉴定术有价材料(100gp)：材料包不可替代，必须 has_specific_material
    r = cast_spell(wiz4, "鉴定术", slot_level=1,
                   component_kwargs={"free_hands": 2, "has_material_pouch": True})
    assert r["success"] is False
    assert "成分不满足" in r["errors"][0]
    # 提供具体材料则可通过成分校验（以法术位施展）
    reset_turn_spell_count(wiz4)
    r = cast_spell(wiz4, "鉴定术", slot_level=1,
                   component_kwargs={"free_hands": 2, "has_specific_material": True})
    assert r["success"] is True
    assert r["slot_consumed"] is True

    # —— 反应施法 (R-SPL-006) —— 护盾术消耗反应
    from . import combat as _combat
    reset_turn_spell_count(wiz4)
    com = _combat.Combatant(cid="wiz_c", name="Wiz")
    assert _combat.can_take_reaction(com) is True
    r = cast_spell(wiz4, "护盾术", slot_level=1, targets=[{}],
                   combatant=com,
                   component_kwargs={"free_hands": 2})
    assert r["success"] is True
    assert com.reaction_used is True
    # 反应已消耗 → 再次施展反应法术被拒（即使新回合放开法术位计数）
    reset_turn_spell_count(wiz4)
    r2 = cast_spell(wiz4, "护盾术", slot_level=1, targets=[{}],
                    combatant=com,
                    component_kwargs={"free_hands": 2})
    assert r2["success"] is False
    assert "反应" in r2["errors"][0]
    # 无 combatant 时 has_reaction_available=False 也拒绝
    reset_turn_spell_count(wiz4)
    r3 = cast_spell(wiz4, "护盾术", slot_level=1, targets=[{}],
                    has_reaction_available=False,
                    component_kwargs={"free_hands": 2})
    assert r3["success"] is False
    assert "反应" in r3["errors"][0]

    # —— 升环多目标 (R-SPL-004) —— 隐形术每升一环多1目标
    inv2 = resolve_upcast(get_spell("隐形术"), 2, 7)
    assert inv2["num_targets"] == 1
    inv3 = resolve_upcast(get_spell("隐形术"), 3, 7)
    assert inv3["num_targets"] == 2
    inv4 = resolve_upcast(get_spell("隐形术"), 4, 7)
    assert inv4["num_targets"] == 3

    # —— 法器职业限制 (R-SPL-013) ——
    assert can_use_focus("法师", "奥术法器") is True
    assert can_use_focus("术士", "奥术法器") is True
    assert can_use_focus("魔契师", "奥术法器") is True
    assert can_use_focus("牧师", "奥术法器") is False
    assert can_use_focus("德鲁伊", "德鲁伊法器") is True
    assert can_use_focus("游侠", "德鲁伊法器") is True
    assert can_use_focus("法师", "德鲁伊法器") is False
    assert can_use_focus("牧师", "圣徽") is True
    assert can_use_focus("圣武士", "圣徽") is True
    assert can_use_focus("德鲁伊", "圣徽") is False
    assert can_use_focus("吟游诗人", "乐器") is True
    assert can_use_focus("法师", "乐器") is False
    assert can_use_focus("法师", "未知法器") is False

    # —— turn_key 回合切换自动重置 (R-SPL-007) ——
    # 自己回合用法术位施法后，敌人回合（新 turn_key）用法术位施展
    # 反应法术应合法；同一回合内第二个法术位法术仍被拒。
    wiz_tk = CasterState(
        caster_id="wtk", class_name="法师", level=5,
        ability_scores={"INT": 16, "STR": 10, "DEX": 10, "CON": 14, "WIS": 10, "CHA": 10},
        spell_slots={1: 4}, max_spell_slots={1: 4},
    )
    r = cast_spell(wiz_tk, "魔法飞弹", slot_level=1, targets=[{"ac": 20}],
                   component_kwargs={"free_hands": 2}, turn_key="r1:wtk")
    assert r["success"] is True
    # 同回合再施法术位法术 → 拒绝
    r = cast_spell(wiz_tk, "魔法飞弹", slot_level=1, targets=[{"ac": 20}],
                   component_kwargs={"free_hands": 2}, turn_key="r1:wtk")
    assert r["success"] is False and "本回合" in r["errors"][0]
    # 敌人回合（新 turn_key）施展护盾术（法术位反应法术）→ 合法
    r = cast_spell(wiz_tk, "护盾术", slot_level=1, targets=[{}],
                   component_kwargs={"free_hands": 2}, turn_key="r1:goblin")
    assert r["success"] is True, r["errors"]

    # —— 长时间施展骨架 (R-SPL-006) ——
    wiz_long = CasterState(
        caster_id="wl", class_name="法师", level=5,
        ability_scores={"INT": 16, "STR": 10, "DEX": 10, "CON": 14, "WIS": 10, "CHA": 10},
        spell_slots={1: 4, 2: 3, 3: 2},
        max_spell_slots={1: 4, 2: 3, 3: 2},
    )
    long_r = cast_long_spell(wiz_long, "鉴定术", slot_level=1, casting_turns=3,
                             component_kwargs={"free_hands": 2, "has_specific_material": True})
    assert long_r["success"] is True
    prog = long_r["progress"]
    assert prog.total_turns == 3 and prog.turns_done == 0
    assert prog.failed is False and prog.completed is False
    # 推进2回合仍未完成，不耗法术位
    a1 = advance_long_spell(wiz_long, prog,
                            component_kwargs={"free_hands": 2, "has_specific_material": True})
    assert a1["completed"] is False and a1["slot_consumed"] is False
    a2 = advance_long_spell(wiz_long, prog,
                            component_kwargs={"free_hands": 2, "has_specific_material": True})
    assert a2["completed"] is False
    # 第3回合完成 → 消耗法术位
    slots_before = dict(wiz_long.spell_slots)
    a3 = advance_long_spell(wiz_long, prog,
                            component_kwargs={"free_hands": 2, "has_specific_material": True})
    assert a3["completed"] is True
    assert a3["slot_consumed"] is True
    assert wiz_long.spell_slots[1] == slots_before[1] - 1
    # 专注失败 → 法术失败且不耗法术位
    long_r2 = cast_long_spell(wiz_long, "鉴定术", slot_level=1, casting_turns=2,
                              component_kwargs={"free_hands": 2, "has_specific_material": True})
    prog2 = long_r2["progress"]
    slots_before2 = dict(wiz_long.spell_slots)
    fb = advance_long_spell(wiz_long, prog2, concentration_broken=True)
    assert fb["failed"] is True and fb["slot_consumed"] is False
    assert wiz_long.spell_slots == slots_before2          # 失败不耗法术位

    print("[spellcasting] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
