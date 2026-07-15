"""施法引擎 — cast_spell / 法术位消耗 / 成分校验 / 效应结算。

依赖 engine.dice、engine.check，以及 data.spells。
标注规则ID+出处。规则依据 R-SPL-001~036。

注意: 不修改 engine/dice.py、engine/check.py、engine/damage.py。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Optional

from . import dice, check
from ..data.spells import Spell, get_spell, is_cantrip, get_casting_ability


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
    concentrating_on: Optional[str] = None     # R-SPL-019 当前集中的法术实例ID

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


# ──────────────────────────────────────────────────────────────────────────
# 成分校验
# ──────────────────────────────────────────────────────────────────────────

def can_cast_by_components(spell: Spell, caster: CasterState,
                           *, muted: bool = False, silenced: bool = False,
                           free_hands: int = 2,
                           has_material_pouch: bool = False,
                           has_focus: bool = False) -> bool:
    """校验施法者是否满足法术全部成分需求。

    规则: R-SPL-010 法术成分类型 / R-SPL-011 言语成分限制 /
          R-SPL-012 姿势成分限制 / R-SPL-013 材料成分限制与替代
    出处: topics/玩家手册2024/法术/法术成分.htm

    参数:
        muted/silenced: 不能说话/处于沉默区域 → V 失败
        free_hands: 空手数量 → S/M 各需一只空手
        has_material_pouch: 拥有材料包
        has_focus: 拥有法器（且具有使用法器的特性）
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
        # 有指定价格或被消耗的材料须实备
        needs_specific = spell.material_cost_gp > 0 or spell.material_consumed
        if needs_specific:
            # 必须实际持有该具体材料（此处简化为检查材料包）
            if not has_material_pouch:
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

    # 魔法飞弹：每升一环多一支飞镖
    if uc.get("base_darts") is not None:
        result["num_darts"] = uc["base_darts"] + levels_above * uc.get("darts_per_level", 1)

    # 灼热射线：每升一环多一道射线
    if uc.get("base_rays") is not None:
        result["num_attacks"] = uc["base_rays"] + levels_above * uc.get("rays_per_level", 1)

    # 火球术/闪电束：每升一环多 1d6
    if uc.get("per_level_above_base") == "+1d6":
        if levels_above > 0:
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

    return result


# ──────────────────────────────────────────────────────────────────────────
# cast_spell 主函数
# ──────────────────────────────────────────────────────────────────────────

def cast_spell(
    caster: CasterState,
    spell_name: str,
    slot_level: Optional[int] = None,
    targets: Optional[list[dict]] = None,
    *,
    concentration_mgr: Optional[Any] = None,
    component_kwargs: Optional[dict] = None,
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

    返回 dict:
        success: bool — 是否成功施展并产生效应
        spell: str — 法术名
        slot_level: int — 消耗的法术位环阶（0=戏法）
        slot_consumed: bool — 是否消耗了法术位
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
    else:
        # 非戏法必须指定法术位环阶
        if slot_level is None:
            errors.append("非戏法必须指定 slot_level")
            return _fail(spell, slot_level, errors)
        if slot_level < spell.level:
            errors.append(f"法术位环阶 {slot_level} 低于法术环阶 {spell.level}")
            return _fail(spell, slot_level, errors)

    # —— 成分校验 (R-SPL-010~013) ——
    if not can_cast_by_components(spell, caster, **comp_kw):
        errors.append("成分不满足（V/S/M）")
        return _fail(spell, slot_level, errors)

    # —— 法术位消耗 (R-SPL-002) ——
    slot_consumed = False
    if not is_cantrip(spell):
        if not has_spell_slot(caster, slot_level):
            errors.append(f"无可用 {slot_level} 环法术位")
            return _fail(spell, slot_level, errors)
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
                dmg = dice.roll_dice(dmg_expr, crit=atk.crit)
                tgt_result["damage"] = {
                    "dice": dmg_expr,
                    "rolls": dmg.dice_rolls,
                    "total": dmg.total,
                    "type": spell.damage_type,
                    "crit": atk.crit,
                }
            results.append(tgt_result)

    elif spell.effect_type == "saving_throw":
        # 豁免型法术（火球术、闪电束）
        dmg_expr = upcast_info.get("damage_dice", spell.damage_dice)
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
            # 计算伤害：失败全效，成功半效
            full_dmg = dice.roll_dice(dmg_expr)
            if sv.success:
                # 成功减半（向下取整）
                half = dice.round_down(full_dmg.total / 2)
                applied = half
            else:
                applied = full_dmg.total

            tgt_result = {
                "target_index": targets.index(tgt),
                "save_roll": sv.d20,
                "save_total": sv.total,
                "save_success": sv.success,
                "dc": save_dc,
                "damage": {
                    "dice": dmg_expr,
                    "rolls": full_dmg.dice_rolls,
                    "total": applied,
                    "type": spell.damage_type,
                    "halved": sv.success,
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
        "effect_type": spell.effect_type,
        "save_dc": save_dc,
        "attack_bonus": attack_bonus,
        "effective_level": upcast_info.get("effective_level", spell.level),
        "results": results,
        "concentration_set": concentration_set,
        "errors": [],
    }


def _fail(spell: Spell, slot_level: Optional[int], errors: list[str]) -> dict:
    """构造失败结果。"""
    return {
        "success": False,
        "spell": spell.name,
        "level": spell.level,
        "slot_level": slot_level or 0,
        "slot_consumed": False,
        "effect_type": spell.effect_type,
        "save_dc": 0,
        "attack_bonus": 0,
        "effective_level": spell.level,
        "results": [],
        "concentration_set": False,
        "errors": errors,
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
    r = cast_spell(wiz, "护盾术", slot_level=1,
                   targets=[{}],
                   component_kwargs={"free_hands": 2})
    assert r["success"] is True
    assert r["effect_type"] == "shield"
    assert r["results"][0]["ac_bonus"] == 5

    # —— 隐形术（2环，专注）—— 需要集中管理
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
    r3 = cast_spell(wiz4, "火球术", slot_level=3,
                    targets=[{"save_bonus": 0, "save_prof": False, "prof_bonus": 0, "ac": 10}],
                    component_kwargs={"free_hands": 2, "has_material_pouch": True})
    assert r3["effective_level"] == 3
    # 4环位升环
    r4 = cast_spell(wiz4, "火球术", slot_level=4,
                    targets=[{"save_bonus": 0, "save_prof": False, "prof_bonus": 0, "ac": 10}],
                    component_kwargs={"free_hands": 2, "has_material_pouch": True})
    assert r4["effective_level"] == 4
    # 4环伤害骰应为 9d6
    assert r4["results"][0]["damage"]["dice"] == "9d6"

    # —— 长休恢复法术位 (R-SPL-003) ——
    restore_slots_on_long_rest(wiz4)
    assert wiz4.spell_slots[4] == 1  # 恢复满

    print("[spellcasting] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
