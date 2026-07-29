"""resolvers.cast — 施法检定 + 伤害/效果计算。

从 brain/graph.py 提取。包含:
  - resolve_cast: 施法资格校验 + 法术位消耗 + 法术攻击/豁免/自动命中/治疗分支
"""

from __future__ import annotations

import json

from ...engine import check, conditions, damage
from ...engine import dice as engine_dice
from ...engine.spellcasting import check_casting_components
from ..utils import CLASS_CAST_ABILITY, target_condition_state


def resolve_cast(ch, it) -> dict:
    """施法检定 + 伤害/效果掷骰。R-DMG-002/R-SPL-021/022/CHK-011/014"""
    # 施法资格校验：非施法职业不能施法（R-SPL-001 施法者前提）
    if ch.char_class not in CLASS_CAST_ABILITY:
        return {"kind": "cast", "error": f"{ch.char_class} 不会施法，无法施展法术"}
    # 先查 spells 数据表取权威值（优先于 LLM 猜测）：level/spell_dice/damage_type/
    # effect_type/save_ability/concentration/half_on_save。表未收录（get_spell 抛 KeyError）
    # 则回退 LLM 猜测，不硬性报错——因 spells 表条目有限，报错会阻断多数施法。
    # 详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段B2
    spell_name = it.get("spell_name", "")
    # 拥有性门控：只能施展已学会的法术（R-SPL-036 职业法术列表）。
    # 历史角色 known_spells 为空 → 动态回退职业默认表（不落盘，仅供校验）
    if spell_name:
        from ...data import spells as _sp_mod
        _known = ch.known_spells or _sp_mod.default_known_spells(ch.char_class, ch.level)
        if spell_name not in _known:
            return {"kind": "cast",
                    "error": f"尚未学会法术「{spell_name}」，无法施展（职业法术列表内且环阶可及的法术才可用）"}
    _spell = None
    if spell_name:
        try:
            from ...data import spells as _sp
            _spell = _sp.get_spell(spell_name)
        except Exception:
            _spell = None

    # —— 施法成分 V/S/M 校验 (R-SPL-010~013) ——
    # 返回结构化数据供叙述节点描述，不直接返回面向玩家的错误文本
    component_check = None
    if _spell:
        # 构建法术成分输入
        spell_comp_input = {
            "V": "V" in _spell.components,
            "S": "S" in _spell.components,
            "M": _spell.material_desc if "M" in _spell.components else "",
            "material_cost_gp": _spell.material_cost_gp,
            "material_consumed": _spell.material_consumed,
        }
        # 从角色状态推导校验输入
        _conds = ch.conditions_list if hasattr(ch, "conditions_list") else []
        _free_hands = _estimate_free_hands(ch)
        _inv = ch.inventory if hasattr(ch, "inventory") else []
        char_state_input = {
            "conditions": _conds,
            "free_hands": _free_hands,
            "has_material_pouch": _has_component_pouch(_inv),
            "has_focus": _has_spell_focus(_inv, ch.char_class),
            "has_specific_material": it.get("has_specific_material", False),
        }
        component_check = check_casting_components(spell_comp_input, char_state_input)
        if not component_check["can_cast"]:
            # 成分不满足：返回结构化数据，由叙述节点生成描述
            return {
                "kind": "cast",
                "spell_name": spell_name,
                "component_check": component_check,
                "component_failed": True,
            }

    # 法术位校验（戏法 level<=0 不耗位）R-SPL-002
    # level 取权威：表内法术用 _spell.level；表外回退 LLM 猜测 it.spell_level。
    # 注意用 dict.get(key, default) 而非 `or`——`0 or 1` 会把戏法(level=0)误判为 1，
    # 导致戏法被当作 1 环法术消耗法术位（BUG-D）。LLM 对戏法环阶猜测不稳定
    # （圣火术时而报 0 时而报 1），故表内法术必须以表为准。
    level = int(_spell.level) if _spell else int(it.get("spell_level", 1))
    if level >= 1:
        try:
            _sd = json.loads(ch.spell_slots_json) if ch.spell_slots_json else {}
        except Exception:
            _sd = {}
        if _sd.get(str(level), 0) <= 0:
            return {"kind": "cast", "error": f"无 {level} 环法术位"}
    cast_ability = CLASS_CAST_ABILITY.get(ch.char_class) or it.get("casting_ability") or "int"
    cast_mod = ch.ability_mod(cast_ability)
    prof = ch.prof()
    save_dc = check.calc_save_dc(cast_mod, prof)            # R-DMG-002/R-SPL-021
    atk_bonus = cast_mod + prof                              # R-SPL-022
    # 目标抗性/易伤/免疫
    resists = it.get("resistances", [])
    vulns = it.get("vulnerabilities", [])
    immuns = it.get("immunities", [])
    out = {"kind": "cast", "spell_save_dc": save_dc, "spell_attack_bonus": atk_bonus,
           "spell_level": level}

    # 法术字段：表内取权威 damage_dice/damage_type/effect_type/save_ability/concentration；
    # 表外回退 LLM 猜测。
    if _spell:
        if _spell.concentration:
            out["concentrating_on"] = _spell.name
        spell_dice = _spell.damage_dice or it.get("spell_dice") or ""
        dmg_type = damage.normalize_damage_type(_spell.damage_type or it.get("damage_type") or "力场")
        _etype = _spell.effect_type
        if _spell.save_ability:
            out["save_ability"] = _spell.save_ability.lower()
    else:
        spell_dice = it.get("spell_dice") or ""
        dmg_type = damage.normalize_damage_type(it.get("damage_type") or "力场")
        _etype = None
    out["spell_name"] = spell_name
    out["spell_dice"] = spell_dice or "1d8"   # 输出展示用（无伤害骰时保守占位）
    has_damage = bool(spell_dice)             # 无伤害骰 → buff/utility/护盾，不走伤害结算

    if _etype == "automatic" or it.get("auto_hit"):
        # 自动命中型（魔法飞弹）：不掷攻击/豁免，直接伤害（抗性/易伤/免疫仍走管线）
        if has_damage:
            dr = damage.roll_damage(damage.DamageRequest(dice_expr=spell_dice, damage_type=dmg_type, add_mod=False),
                                    resistances=resists, vulnerabilities=vulns, immunities=immuns)
            out.update({"hit": True, "auto_hit": True, "damage": dr.final, "damage_type": dmg_type,
                        "damage_rolls": dr.dice_rolls, "resisted": dr.resisted,
                        "vulnerable": dr.vulnerable, "immune": dr.immune})
        else:
            out.update({"hit": True, "auto_hit": True, "damage": 0})
    elif it.get("spell_attack") or _etype == "attack_roll":  # 法术攻击检定型
        ac = int(it.get("target_ac") or 10)
        # 条件优劣势
        atk_state = ch.to_condition_state()
        mods = conditions.attack_modifiers(atk_state, target_condition_state(it),
                                           int(it.get("distance_ft") or 5))
        adv = bool(it.get("advantage")) or mods.attacker_advantage
        dis = bool(it.get("disadvantage")) or mods.attacker_disadvantage or bool(it.get("target_dodging"))
        atk = check.attack_roll(bonus=atk_bonus, ac=ac, advantage=adv, disadvantage=dis,
                                 circ=-conditions.d20_penalty(atk_state))  # R-SPL-022 + R-CMB-017
        out.update({"spell_attack_total": atk.total, "d20": atk.d20, "hit": atk.hit, "crit": atk.crit, "target_ac": ac})
        if atk.hit and has_damage:
            crit = atk.crit or mods.target_auto_crit_if_hit
            dr = damage.roll_damage(damage.DamageRequest(dice_expr=spell_dice, damage_type=dmg_type,
                                                          add_mod=False, crit=crit),
                                     resistances=resists, vulnerabilities=vulns, immunities=immuns)
            out.update({"damage": dr.final, "damage_type": dmg_type, "damage_rolls": dr.dice_rolls,
                        "resisted": dr.resisted, "vulnerable": dr.vulnerable, "immune": dr.immune})
    elif _etype == "heal" or (it.get("damage_type", "") or "").lower() in ("heal", "healing", "治疗"):
        # 治疗法术（疗伤术/治愈真言等）：掷治疗骰（spell_dice 已含+施法属性调整值），
        # 无攻击检定、无豁免——治疗始终生效。BUG-G：原走豁免分支致「豁免成功=0治疗」。
        # 输出统一 damage_type="治疗"，供 apply_node step2.9 确定性应用。
        if has_damage:
            dr = damage.roll_damage(damage.DamageRequest(dice_expr=spell_dice, damage_type="heal", add_mod=False),
                                    resistances=[], vulnerabilities=[], immunities=[])
            out.update({"hit": True, "damage_type": "治疗", "raw_damage": dr.final,
                        "damage": dr.final, "damage_rolls": dr.dice_rolls})
        else:
            out.update({"hit": True, "damage_type": "治疗", "damage": 0})
    else:  # 豁免型法术 / 无伤害 buff·utility
        if has_damage:
            save_bonus = int(it.get("target_save_bonus") or 0)
            sv = check.saving_throw(mod=save_bonus, prof=0, proficient=False, dc=save_dc)  # R-CHK-011
            dr = damage.roll_damage(damage.DamageRequest(dice_expr=spell_dice, damage_type=dmg_type, add_mod=False),
                                    resistances=resists, vulnerabilities=vulns, immunities=immuns)
            piped = dr.final  # 经管线后的全额伤害（已处理抗性/易伤/免疫）
            # R-CHK-014 豁免成功伤害：按法术属性 half_on_save 决定——
            # 火球术等「成功减半」半伤；圣火术/毒素喷吐等「成功不受伤害」0伤。
            # 法术表未收录（回退 LLM 猜测）时默认 0 伤（多数单目标豁免法术如此）。
            half = bool(_spell.half_on_save) if _spell else False
            final = (engine_dice.round_down(piped / 2) if half else 0) if sv.success else piped
            out.update({"save_success": sv.success, "save_total": sv.total, "raw_damage": piped,
                        "damage": final, "damage_type": dmg_type, "damage_rolls": dr.dice_rolls,
                        "resisted": dr.resisted, "vulnerable": dr.vulnerable, "immune": dr.immune})
        else:
            out.update({"hit": True, "damage": 0})  # 无伤害法术默认生效
    return out


# ──────────────────────────────────────────────────────────────────────────
# 施法成分辅助：从角色装备推导空闲手/材料包/法器
# ──────────────────────────────────────────────────────────────────────────

# 已知法器/圣徽关键词（用于从物品栏匹配）
_FOCUS_KEYWORDS = ("法器", "圣徽", "奥术法器", "德鲁伊法器")
_POUCH_KEYWORDS = ("材料包", "材料组件包", "施法材料包")


def _estimate_free_hands(ch) -> int:
    """从角色装备粗略估算空闲手数量。

    规则: R-SPL-012 姿势成分需空闲手
    简化模型：无武器=2空手；单手武器=1空手；双手武器=0空手。
    """
    weapon = getattr(ch, "equipped_weapon", "") or ""
    if not weapon:
        return 2
    # 常见双手武器关键词（简化判断）
    _two_handed = ("巨剑", "巨斧", "长矛", "长棍", "战棍", "弩", "大锤",
                   "长弓", "重弩", "戟", "砍刀", "大剑")
    for kw in _two_handed:
        if kw in weapon:
            return 0
    # 有盾牌时武器占一手，盾占一手 → 0空手
    _inv = ch.inventory if hasattr(ch, "inventory") else []
    has_shield = any("盾牌" in item for item in _inv)
    if has_shield:
        return 0
    # 默认单手武器 → 1空手
    return 1


def _has_component_pouch(inventory: list[str]) -> bool:
    """物品栏是否包含材料包。"""
    for item in inventory:
        for kw in _POUCH_KEYWORDS:
            if kw in item:
                return True
    return False


def _has_spell_focus(inventory: list[str], char_class: str) -> bool:
    """物品栏是否包含该职业可用的法器/圣徽。

    规则: R-SPL-013 法器职业限制
    """
    from ...engine.spellcasting import can_use_focus
    for item in inventory:
        # 直接匹配材料包关键词 → 不算法器
        if any(kw in item for kw in _POUCH_KEYWORDS):
            continue
        # 匹配法器类型
        for focus_type in ("奥术法器", "德鲁伊法器", "圣徽"):
            if focus_type in item and can_use_focus(char_class, focus_type):
                return True
        # 通用"法器"关键词
        if "法器" in item:
            for ft in ("奥术法器", "德鲁伊法器"):
                if can_use_focus(char_class, ft):
                    return True
    return False
