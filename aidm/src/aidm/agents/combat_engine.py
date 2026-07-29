"""Combat Engine Agent — 先攻管理、逐回合推进、攻击判定、伤害计算。

职责:
  - 执行确定性骰子检定（attack/cast/ability_check）
  - 管理战斗状态机（先政排序、回合推进、动作经济）
  - 计算伤害并应用

设计参考: ITMO AI-DM 的 Action Resolver 角色，
所有骰子计算纯代码，LLM 不参与。
"""

from __future__ import annotations

import contextlib

from ..brain.state import GameState
from ..data import equipment
from ..engine import check, conditions, damage
from ..engine import combat as cmb
from ..engine import dice as engine_dice
from ..stats import store

# 职业→施法属性（确定性，优先于 LLM 猜测）
CLASS_CAST_ABILITY = {
    "法师": "int", "术士": "cha", "吟游诗人": "cha", "魔契师": "cha",
    "牧师": "wis", "德鲁伊": "wis", "圣武士": "wis", "游侠": "wis",
}


def _target_condition_state(it) -> conditions.ConditionState:
    """从 intent 构建目标条件状态。"""
    ts = conditions.ConditionState()
    for c in it.get("target_conditions", []):
        with contextlib.suppress(ValueError):
            ts.add(c)
    return ts


def _resolve_attack(ch, it) -> dict:
    """执行攻击检定 + 伤害计算。R-CMB-017/022/023, R-DMG-001/CMB-029, R-GLS-044~058"""
    ability = it.get("ability") or "str"
    bonus = ch.ability_mod(ability) + ch.prof()
    ac = int(it.get("target_ac") or 10)
    # 条件优劣势 + 力竭惩罚
    atk_state = ch.to_condition_state()
    mods = conditions.attack_modifiers(atk_state, _target_condition_state(it),
                                       int(it.get("distance_ft") or 5))
    adv = bool(it.get("advantage")) or mods.attacker_advantage
    dis = bool(it.get("disadvantage")) or mods.attacker_disadvantage
    if it.get("target_dodging"):
        dis = True
    atk = check.attack_roll(bonus=bonus, ac=ac, advantage=adv, disadvantage=dis,
                            circ=-conditions.d20_penalty(atk_state))
    out = {"kind": "attack", "attack_total": atk.total, "d20": atk.d20,
           "hit": atk.hit, "crit": atk.crit, "rolls": atk.rolls,
           "target_ac": ac, "bonus": bonus}
    if atk.hit:
        # 武器三级回退：玩家明说 → 角色卡 equipped_weapon → 徒手(1+力量)
        # 详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段A4/B1
        wname = it.get("weapon") or getattr(ch, "equipped_weapon", "") or "徒手"
        dice_expr, dmg_type = equipment.resolve_weapon_damage(wname)
        crit = atk.crit or mods.target_auto_crit_if_hit
        dr = damage.roll_damage(damage.DamageRequest(
            dice_expr=dice_expr, damage_type=dmg_type,
            ability_mod=ch.ability_mod(ability), add_mod=True, crit=crit
        ), resistances=it.get("resistances", []),
           vulnerabilities=it.get("vulnerabilities", []),
           immunities=it.get("immunities", []))
        out.update({"damage": dr.final, "damage_type": dmg_type,
                    "damage_rolls": dr.dice_rolls, "weapon": wname,
                    "resisted": dr.resisted, "vulnerable": dr.vulnerable, "immune": dr.immune})
    return out


def _resolve_cast(ch, it) -> dict:
    """执行施法检定。R-DMG-002/R-SPL-021/022/CHK-011/014"""
    cast_ability = CLASS_CAST_ABILITY.get(ch.char_class, it.get("casting_ability", "int"))
    cast_mod = ch.ability_mod(cast_ability)
    prof = ch.prof()
    save_dc = check.calc_save_dc(cast_mod, prof)
    atk_bonus = cast_mod + prof
    spell_dice = it.get("spell_dice") or "1d8"
    dmg_type = it.get("damage_type") or "力场"
    level = int(it.get("spell_level") or 1)
    resists = it.get("resistances", [])
    vulns = it.get("vulnerabilities", [])
    immuns = it.get("immunities", [])
    out = {"kind": "cast", "spell_save_dc": save_dc,
           "spell_attack_bonus": atk_bonus, "spell_level": level,
           "spell_dice": spell_dice}
    if it.get("spell_attack"):  # 法术攻击检定型
        ac = int(it.get("target_ac") or 10)
        atk_state = ch.to_condition_state()
        mods = conditions.attack_modifiers(atk_state, _target_condition_state(it),
                                           int(it.get("distance_ft") or 5))
        adv = bool(it.get("advantage")) or mods.attacker_advantage
        dis = bool(it.get("disadvantage")) or mods.attacker_disadvantage or bool(it.get("target_dodging"))
        atk = check.attack_roll(bonus=atk_bonus, ac=ac, advantage=adv, disadvantage=dis,
                                circ=-conditions.d20_penalty(atk_state))
        out.update({"spell_attack_total": atk.total, "d20": atk.d20,
                    "hit": atk.hit, "crit": atk.crit, "target_ac": ac})
        if atk.hit:
            crit = atk.crit or mods.target_auto_crit_if_hit
            dr = damage.roll_damage(damage.DamageRequest(
                dice_expr=spell_dice, damage_type=dmg_type,
                add_mod=False, crit=crit
            ), resistances=resists, vulnerabilities=vulns, immunities=immuns)
            out.update({"damage": dr.final, "damage_type": dmg_type,
                        "damage_rolls": dr.dice_rolls,
                        "resisted": dr.resisted, "vulnerable": dr.vulnerable, "immune": dr.immune})
    else:  # 豁免型法术
        save_bonus = int(it.get("target_save_bonus") or 0)
        sv = check.saving_throw(mod=save_bonus, prof=0, proficient=False, dc=save_dc)
        dr = damage.roll_damage(damage.DamageRequest(
            dice_expr=spell_dice, damage_type=dmg_type, add_mod=False
        ), resistances=resists, vulnerabilities=vulns, immunities=immuns)
        piped = dr.final
        final = engine_dice.round_down(piped / 2) if sv.success else piped
        out.update({"save_success": sv.success, "save_total": sv.total,
                    "raw_damage": piped, "damage": final, "damage_type": dmg_type,
                    "damage_rolls": dr.dice_rolls,
                    "resisted": dr.resisted, "vulnerable": dr.vulnerable, "immune": dr.immune})
    return out


def _resolve_ability_check(ch, it) -> dict:
    """执行属性检定。R-CHK-010"""
    ability = it.get("ability") or "str"
    dc = int(it.get("dc") or 10)
    proficient = bool(it.get("proficient"))
    r = check.ability_check(mod=ch.ability_mod(ability), prof=ch.prof(),
                            proficient=proficient, dc=dc)
    return {"kind": "ability_check", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "margin": r.margin}


def resolve(state: GameState) -> dict:
    """Combat Engine Agent: 硬性骰子分派（纯代码，LLM 不参与）。

    根据 intent.action_type 分派到对应的确定性检定函数。
    """
    it = state["intent"]
    at = it.get("action_type")
    cid = state.get("character_id")
    ch = store.get_character(cid) if cid else None

    if ch is None and at not in ("start_combat", "end_combat"):
        return {"dice": {}, "error": "角色卡不存在"}

    if at == "attack":
        return {"dice": _resolve_attack(ch, it)}
    if at == "cast":
        return {"dice": _resolve_cast(ch, it)}
    if at in ("ability_check", "explore"):
        return {"dice": _resolve_ability_check(ch, it)}
    if at == "start_combat":
        return _resolve_start_combat(state, ch, it)
    if at == "end_combat":
        return {"dice": {"kind": "end_combat"}, "combat": {"active": False}}
    # —— 战术动作（不掷骰，仅标记状态）——
    if at == "dash":
        return {"dice": {"kind": "dash", "extra_movement_ft": ch.speed}}
    if at == "dodge":
        return {"dice": {"kind": "dodge", "effect": "对本角色的攻击具有劣势"}}
    if at == "disengage":
        return {"dice": {"kind": "disengage", "effect": "本回合移动不引发借机攻击"}}
    if at == "help":
        return {"dice": {"kind": "help",
                         "target": it.get("target_name", ""),
                         "effect": f"使{it.get('target_name', '盟友')}的下次检定具有优势"}}
    if at == "ready":
        return {"dice": {"kind": "ready",
                         "trigger": it.get("trigger_condition", ""),
                         "action": it.get("readied_action", "")}}
    # —— 技能动作（需要检定）——
    if at == "hide":
        return {"dice": _resolve_hide(ch, it)}
    if at == "search":
        return {"dice": _resolve_search(ch, it)}
    if at == "use_item":
        return {"dice": {"kind": "use_item",
                         "item": it.get("item_name", ""),
                         "effect": it.get("item_effect", "")}}
    if at == "grapple":
        return {"dice": _resolve_grapple(ch, it)}
    if at == "shove":
        return {"dice": _resolve_shove(ch, it)}
    if at == "study":
        return {"dice": _resolve_study(ch, it)}
    if at == "opportunity_attack":
        return {"dice": _resolve_opportunity_attack(ch, it)}
    return {"dice": {}}  # other → 仅叙事


# ── 技能动作的确定性检定 ──────────────────────────────────────

def _resolve_hide(ch, it) -> dict:
    """躲藏：敏捷(潜行)检定 vs 对手被动察觉。R-GLS-009"""
    stealth_mod = ch.ability_mod("dex")
    prof = ch.prof()
    r = check.ability_check(mod=stealth_mod, prof=prof,
                            proficient=True, dc=int(it.get("dc") or 15))
    return {"kind": "hide", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": int(it.get("dc") or 15),
            "effect": "隐蔽成功" if r.success else "被发现"}


def _resolve_search(ch, it) -> dict:
    """搜索：感知(察觉)或智力(调查)检定 vs DC。R-CHK-010"""
    ability = it.get("ability") or "wis"
    mod = ch.ability_mod(ability)
    prof = ch.prof()
    dc = int(it.get("dc") or 15)
    r = check.ability_check(mod=mod, prof=prof, proficient=True, dc=dc)
    return {"kind": "search", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "ability": ability}


def _resolve_grapple(ch, it) -> dict:
    """擒抱：力量或敏捷竞技检定 vs 目标力量/敏捷竞技。R-CMB-017"""
    ability = it.get("ability") or "str"
    mod = ch.ability_mod(ability)
    prof = ch.prof()
    dc = int(it.get("dc") or 10)
    r = check.ability_check(mod=mod, prof=prof, proficient=True, dc=dc)
    return {"kind": "grapple", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "ability": ability,
            "effect": "擒抱成功" if r.success else "擒抱失败"}


def _resolve_shove(ch, it) -> dict:
    """推撞：力量或敏捷竞技检定,让目标倒地或移开。R-CMB-017"""
    ability = it.get("ability") or "str"
    mod = ch.ability_mod(ability)
    prof = ch.prof()
    dc = int(it.get("dc") or 10)
    r = check.ability_check(mod=mod, prof=prof, proficient=True, dc=dc)
    shove_type = it.get("shove_type", "prone")
    return {"kind": "shove", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "ability": ability,
            "shove_type": shove_type,
            "effect": f"推撞成功({shove_type})" if r.success else "推撞失败"}


def _resolve_study(ch, it) -> dict:
    """研究：智力检定(奥秘/历史/调查/自然/宗教)。PHB 2024 Study action"""
    ability = it.get("ability") or "int"
    mod = ch.ability_mod(ability)
    prof = ch.prof()
    dc = int(it.get("dc") or 15)
    skill = it.get("skill", "调查")
    r = check.ability_check(mod=mod, prof=prof, proficient=True, dc=dc)
    return {"kind": "study", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "ability": ability,
            "skill": skill,
            "effect": "获得信息" if r.success else "未能回忆起有用信息"}


def _resolve_opportunity_attack(ch, it) -> dict:
    """借机攻击：反应动作,目标离开触及范围时发动近战攻击。PHB Opportunity Attack"""
    ability = it.get("ability") or "str"
    bonus = ch.ability_mod(ability) + ch.prof()
    ac = int(it.get("target_ac") or 10)
    atk = check.attack_roll(bonus=bonus, ac=ac)
    out = {"kind": "opportunity_attack",
           "attack_total": atk.total, "d20": atk.d20,
           "hit": atk.hit, "crit": atk.crit,
           "target_ac": ac, "bonus": bonus,
           "weapon": it.get("weapon", "徒手打击")}
    if atk.hit:
        # 武器三级回退：玩家明说 → 角色卡 equipped_weapon → 徒手(1+力量)
        wname = it.get("weapon") or getattr(ch, "equipped_weapon", "") or "徒手"
        dice_expr, dmg_type = equipment.resolve_weapon_damage(wname)
        dr = damage.roll_damage(damage.DamageRequest(
            dice_expr=dice_expr, damage_type=dmg_type,
            ability_mod=ch.ability_mod(ability), add_mod=True, crit=atk.crit
        ))
        out.update({"damage": dr.final, "damage_type": dmg_type,
                    "damage_rolls": dr.dice_rolls})
    return out


def _resolve_start_combat(state, ch, it) -> dict:
    """开始战斗：roll_initiative + persist。R-CMB-002"""
    enemies = it.get("enemies") or [{"name": "敌人", "dex_mod": 1, "side": "enemy"}]
    combatants = [cmb.Combatant(cid=str(state["character_id"]), name=ch.name,
                                dex_mod=ch.ability_mod("dex"), side="player", is_player=True)]
    for i, e in enumerate(enemies):
        combatants.append(cmb.Combatant(cid=f"e{i}", name=e.get("name", f"敌人{i}"),
                                        dex_mod=int(e.get("dex_mod", 0)),
                                        side="enemy", is_player=False))
    combat = cmb.Combat()
    order = cmb.roll_initiative(combatants)
    combat.participants = combatants
    combat.initiative_order = order
    combat.round = 1
    combat.current_index = 0
    combat.active = True
    cs = store.save_combat(state["campaign_id"], combat)
    return {"dice": {"kind": "start_combat",
                     "initiative_order": [{"name": c.name, "init": c.initiative, "side": c.side}
                                          for c in order]},
            "combat": {"active": True, "combat_id": cs.id, "round": 1,
                       "current_index": 0,
                       "combatants": [{"name": c.name, "init": c.initiative, "side": c.side}
                                      for c in order]}}
