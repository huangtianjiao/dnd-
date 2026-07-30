"""resolvers.actions — 其余 resolve 函数 + 遭遇系统 + 时间推进。

从 brain/graph.py 提取。包含:
  - 属性检定/技能检定（ability_check, hide, search, grapple, shove, study）
  - 休息/社交/升级/探索/旅行
  - 战斗开始 + 突袭判定
  - 遭遇前置判定（场景过滤/时钟/类型）
  - 目标确定性包装
  - 游戏内时间推进
"""

from __future__ import annotations

import dataclasses
import logging

from ...brain import exploration as exploration_mod
from ...brain import levelup as levelup_mod
from ...brain import rest as rest_mod
from ...brain import social as social_mod
from ...engine import check, conditions
from ...engine import combat as cmb
from ...engine import dice as engine_dice
from ...stats import models, store
from ..utils import CLASS_CAST_ABILITY

_log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────
# CR → XP 映射表（D&D 5E 标准）
# ──────────────────────────────────────────────────────────────────────────

CR_XP_TABLE: dict[float, int] = {
    0: 10, 0.125: 25, 0.25: 50, 0.5: 100,
    1: 200, 2: 450, 3: 700, 4: 1100, 5: 1800,
    6: 2300, 7: 2900, 8: 3900, 9: 5000, 10: 5900,
    11: 7200, 12: 8400, 13: 10000, 14: 11500, 15: 13000,
    16: 15000, 17: 18000, 18: 20000, 19: 22000, 20: 25000,
    21: 33000, 22: 41000, 23: 50000, 24: 62000, 25: 75000,
    26: 90000, 27: 105000, 28: 120000, 29: 135000, 30: 155000,
}


def cr_to_xp(cr: float) -> int:
    """根据 CR 查表返回 XP。未找到时按最近 CR 向下取档。"""
    if cr in CR_XP_TABLE:
        return CR_XP_TABLE[cr]
    # 向下取最近的已知 CR
    known = sorted(CR_XP_TABLE.keys())
    for k in reversed(known):
        if k <= cr:
            return CR_XP_TABLE[k]
    return 10  # CR<0 兆底


def award_combat_xp(campaign_id: int, character_id: int,
                    defeated_enemies: list[dict]) -> dict:
    """战斗结束后根据击败敌人的 CR 计算 XP 并持久化。

    defeated_enemies: [{"name": str, "cr": float}, ...]
    返回: {"total_xp": int, "new_xp": int}
    """
    total_xp = 0
    for e in defeated_enemies:
        cr = float(e.get("cr", 0))
        total_xp += cr_to_xp(cr)
    if total_xp > 0 and character_id:
        new_xp = store.add_character_xp(character_id, total_xp)
        _log.info("XP奖励 campaign=%s char=%d xp=+%d total=%d",
                  campaign_id, character_id, total_xp, new_xp)
        return {"total_xp": total_xp, "new_xp": new_xp}
    return {"total_xp": total_xp, "new_xp": 0}


# ──────────────────────────────────────────────────────────────────────────
# 属性/技能检定
# ──────────────────────────────────────────────────────────────────────────

# 技能名→属性映射（LLM 未给 ability 时按 skill 推断，避免察觉/调查误用力量的 +3）
_SKILL_ABILITY = {
    "察觉": "wis", "求生": "wis", "医药": "wis", "洞悉": "wis", "驯兽": "wis", "感知": "wis",
    "调查": "int", "奥秘": "int", "历史": "int", "自然": "int", "宗教": "int",
    "运动": "str", "特技": "dex", "潜行": "dex", "手上功夫": "dex",
    "表演": "cha", "威吓": "cha", "欺瞒": "cha", "说服": "cha",
}


def _infer_ability(skill, action_type: str) -> str:
    """从 skill 名推断属性；explore→wis, study→int，其余兜底 str。"""
    if skill:
        s = str(skill)
        for k, ab in _SKILL_ABILITY.items():
            if k in s:
                return ab
    if action_type == "explore":
        return "wis"
    if action_type == "study":
        return "int"
    return "str"


def resolve_ability_check(ch, it) -> dict:
    ability = it.get("ability") or _infer_ability(it.get("skill"),
                                                  it.get("action_type", "ability_check"))
    dc = int(it.get("dc") or 10)
    proficient = bool(it.get("proficient"))
    # R-GLS-047 力竭 d20 惩罚（等级×2）
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())
    r = check.ability_check(mod=ch.ability_mod(ability), prof=ch.prof(),
                            proficient=proficient, dc=dc, circ=exh_penalty)    # R-CHK-010
    return {"kind": "ability_check", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "margin": r.margin, "ability": ability}


def resolve_hide(ch, it) -> dict:
    """躲藏：敏捷(潜行)检定 vs 对手被动察觉。R-GLS-009"""
    stealth_mod = ch.ability_mod("dex")
    prof = ch.prof()
    dc = int(it.get("dc") or 15)
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())  # R-GLS-047
    r = check.ability_check(mod=stealth_mod, prof=prof,
                            proficient=True, dc=dc, circ=exh_penalty)
    return {"kind": "hide", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc,
            "effect": "隐蔽成功" if r.success else "被发现"}


def resolve_search(ch, it) -> dict:
    """搜索：感知(察觉)或智力(调查)检定 vs DC。R-CHK-010"""
    ability = it.get("ability") or "wis"
    mod = ch.ability_mod(ability)
    prof = ch.prof()
    dc = int(it.get("dc") or 15)
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())  # R-GLS-047
    r = check.ability_check(mod=mod, prof=prof, proficient=True, dc=dc, circ=exh_penalty)
    return {"kind": "search", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "ability": ability}


def resolve_grapple(ch, it) -> dict:
    """擒抱：力量或敏捷竞技检定 vs 目标力量/敏捷竞技。R-CMB-017"""
    ability = it.get("ability") or "str"
    mod = ch.ability_mod(ability)
    prof = ch.prof()
    dc = int(it.get("dc") or 10)
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())  # R-GLS-047
    r = check.ability_check(mod=mod, prof=prof, proficient=True, dc=dc, circ=exh_penalty)
    return {"kind": "grapple", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "ability": ability,
            "effect": "擒抱成功" if r.success else "擒抱失败"}


def resolve_shove(ch, it) -> dict:
    """推撞：力量或敏捷竞技检定,让目标倒地或移开。R-CMB-017"""
    ability = it.get("ability") or "str"
    mod = ch.ability_mod(ability)
    prof = ch.prof()
    dc = int(it.get("dc") or 10)
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())  # R-GLS-047
    r = check.ability_check(mod=mod, prof=prof, proficient=True, dc=dc, circ=exh_penalty)
    shove_type = it.get("shove_type", "prone")
    return {"kind": "shove", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "ability": ability,
            "shove_type": shove_type,
            "effect": f"推撞成功({shove_type})" if r.success else "推撞失败"}


def resolve_study(ch, it) -> dict:
    """研究：智力(奥秘/历史/调查/自然/宗教) 检定 vs DC。R-CHK-010"""
    ability = it.get("ability") or "int"
    mod = ch.ability_mod(ability)
    prof = ch.prof()
    dc = int(it.get("dc") or 15)
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())  # R-GLS-047
    r = check.ability_check(mod=mod, prof=prof, proficient=True, dc=dc, circ=exh_penalty)
    return {"kind": "study", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "ability": ability}


# ──────────────────────────────────────────────────────────────────────────
# 休息
# ──────────────────────────────────────────────────────────────────────────

def resolve_rest(state, ch, it) -> dict:
    """休息机制：短休消耗生命骰恢复HP+恢复职业特性；长休恢复全部HP+所有法术位+力竭-1。
    R-GLS-014/R-GLS-015
    """
    pi = state.get("player_input", "") or ""
    rest_type = it.get("rest_type") or (
        "long" if ("长休" in pi or "long rest" in pi.lower() or "long" in pi.lower() and "休" in pi) else "short")
    if rest_type == "short":
        hit_dice_to_spend = int(it.get("hit_dice_to_spend", 0))
        result = rest_mod.short_rest(ch, hit_dice_to_spend=hit_dice_to_spend)
    else:  # long
        camp_id = state.get("campaign_id")
        if camp_id:
            try:
                c = store.get_campaign(camp_id)
                flags = c.world_flags if c else {}
                last = flags.get(f"last_long_rest_min_{ch.id}")
                now_min = int(flags.get("game_minutes", 8 * 60))
                cd_min = rest_mod.LONG_REST_COOLDOWN_HOURS * 60
                if last is not None and now_min - int(last) < cd_min:
                    remain = cd_min - (now_min - int(last))
                    return {"kind": "rest",
                            "error": f"距上次长休不足{rest_mod.LONG_REST_COOLDOWN_HOURS}小时，"
                                     f"还需等待约{max(1, remain // 60)}小时才能再次长休（可先短休）"}
            except Exception as e:
                _log.debug("长休冷却检查失败 camp=%s: %s", camp_id, e)
        result = rest_mod.long_rest(ch)
    result["kind"] = "rest"
    return result


def apply_rest_to_character(ch, result: dict) -> None:
    """将休息收益落盘到 Character（在 apply_node 中调用）。R-GLS-014 短休 / R-GLS-015 长休"""
    if not result.get("success"):
        return
    rtype = result.get("type", "short")
    hp_restored = int(result.get("hp_restored", 0))
    if hp_restored:
        ch.hp_current = min(ch.hp_max, ch.hp_current + hp_restored)
    if rtype == "short":
        spent = int(result.get("hit_dice_spent", 0))
        remaining = int(result.get("hit_dice_remaining", 0))
        if hasattr(ch, "hit_dice_current"):
            ch.hit_dice_current = max(0, remaining)
    if rtype == "long":
        exh = int(result.get("exhaustion_reduced", 0))
        if exh:
            ch.exhaustion = max(0, ch.exhaustion - exh)
        if result.get("temp_hp_cleared"):
            ch.temp_hp = 0
        if result.get("spell_slots_restored") and ch.char_class in CLASS_CAST_ABILITY:
            try:
                from ...data import spells as _sp
                ch.set_spell_slots(_sp.max_spell_slots(ch.level))
            except Exception as e:
                _log.debug("长休恢复法术位失败 cid=%s: %s", getattr(ch, "id", "?"), e)
        if hasattr(ch, "hit_dice_current"):
            ch.hit_dice_current = ch.level


# ──────────────────────────────────────────────────────────────────────────
# 社交
# ──────────────────────────────────────────────────────────────────────────

# NPC 态度同义词归一化表（LLM 可能返回中文/非标准串）
_ATTITUDE_ALIASES = {
    "friendly": "friendly", "friend": "friendly", "友善": "friendly", "友好": "friendly",
    "indifferent": "indifferent", "neutral": "indifferent", "normal": "indifferent",
    "中立": "indifferent", "冷漠": "indifferent", "一般": "indifferent", "普通": "indifferent",
    "hostile": "hostile", "enemy": "hostile", "angry": "hostile",
    "敌对": "hostile", "敌意": "hostile", "愤怒": "hostile", "仇视": "hostile",
}


def _normalize_attitude(raw) -> str:
    """把 LLM 返回的态度串归一化为 {friendly, indifferent, hostile}。"""
    if not isinstance(raw, str):
        return "indifferent"
    return _ATTITUDE_ALIASES.get(raw.strip().lower(), "indifferent")


def resolve_social(state, ch, it) -> dict:
    """社交流程：NPC态度系统/四步社交互动/态度转换阈值。R-CON-012/R-DM-047"""
    npc_name = it.get("npc_name", "NPC")
    llm_attitude = _normalize_attitude(it.get("npc_attitude", "indifferent"))
    skill = it.get("skill", "persuasion")
    dc = int(it.get("dc", 15))

    camp_id = state.get("campaign_id")
    stored_attitude = llm_attitude
    consec_success = 0
    consec_failure = 0
    sc = None
    if camp_id:
        try:
            sc = store.get_scene(camp_id)
        except Exception as e:
            _log.debug("社交读取场景失败 campaign=%s: %s", camp_id, e)
    if sc:
        for n in sc.npcs:
            if n.get("name") == npc_name:
                stored_attitude = _normalize_attitude(n.get("attitude", llm_attitude))
                consec_success = int(n.get("success_count", 0))
                consec_failure = int(n.get("failure_count", 0))
                break

    # 免检定（DMG「运作交涉」：友好/冷漠 NPC 面对合理、不损其利益的请求
    # 无需魅力检定）。needs_check 由 Director 判断请求合理性；存盘态度为敌对时
    # 不信任该判断，仍走掷骰（LLM 误判防护）。
    if it.get("needs_check") is False and stored_attitude != social_mod.ATTITUDE_HOSTILE:
        return {"kind": "social", "skill": skill, "auto_success": True, "success": True,
                "npc_name": npc_name, "npc_attitude": stored_attitude,
                "new_attitude": stored_attitude,
                "note": "NPC态度非敌对且请求合理，无需检定（DMG：仅在结果不确定时掷骰）"}

    npc = social_mod.NPC(name=npc_name, attitude=stored_attitude)
    dc_modifier = social_mod.check_social_dc(npc.attitude)
    final_dc = max(1, dc + dc_modifier)

    ability = "cha" if skill in ("persuasion", "deception", "intimidation", "performance") else "wis"
    r = check.ability_check(mod=ch.ability_mod(ability), prof=ch.prof(),
                            proficient=True, dc=final_dc)

    if r.success:
        consec_success += 1
        consec_failure = 0
    else:
        consec_failure += 1
        consec_success = 0
    new_attitude = social_mod.update_attitude(npc, consec_success, consec_failure)

    return {"kind": "social", "skill": skill, "dc": final_dc,
            "check_total": r.total, "d20": r.d20,
            "success": r.success, "margin": r.margin,
            "npc_name": npc_name, "npc_attitude": stored_attitude,
            "new_attitude": new_attitude if new_attitude else stored_attitude,
            "consec_success": consec_success, "consec_failure": consec_failure,
            "dc_modifier": dc_modifier}


# ──────────────────────────────────────────────────────────────────────────
# 升级
# ──────────────────────────────────────────────────────────────────────────

def _character_to_levelup_dict(ch) -> dict:
    """把 Character 桥接为 level_up() 期望的角色字典。"""
    next_level = min(ch.level + 1, levelup_mod.MAX_LEVEL)
    return {
        "level": ch.level,
        "xp": levelup_mod.XP_TABLE.get(next_level, 0),
        "class_name": ch.char_class,
        "scores": {k.upper(): v for k, v in ch.abilities.items()},
        "hp_max": ch.hp_max,
        "hp_current": ch.hp_current,
        "features": list(ch.feats),
        "asi_taken": False,
    }


def resolve_levelup(ch, it) -> dict:
    """升级与成长。R-DM-041~045"""
    current_level = ch.level
    new_level = current_level + 1
    if new_level > levelup_mod.MAX_LEVEL:
        return {"kind": "levelup", "error": "已达最高等级20"}
    char_dict = _character_to_levelup_dict(ch)
    try:
        result = levelup_mod.level_up(
            char_dict, new_class=None, new_features=None,
            ability_improvements=None, hit_die_roll=None,
        )
    except ValueError as e:
        return {"kind": "levelup", "error": str(e)}
    return {"kind": "levelup", "old_level": current_level,
            "new_level": result.get("new_level", new_level),
            "hp_gained": result.get("hp_gained", 0),
            "pb_changed": result.get("pb_changed", False),
            "new_pb": result.get("new_proficiency_bonus", 0),
            "tier": result.get("tier", levelup_mod.get_tier(new_level))}


def apply_levelup_to_character(ch, dice: dict) -> None:
    """把升级结果落盘到 Character。R-DM-043"""
    new_level = dice.get("new_level")
    if new_level:
        ch.level = new_level
    gained = int(dice.get("hp_gained", 0))
    if gained:
        ch.hp_max += gained
        ch.hp_current += gained


# ──────────────────────────────────────────────────────────────────────────
# 探索/旅行
# ──────────────────────────────────────────────────────────────────────────

def _resolve_terrain(state, it) -> str:
    """地形解析。详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段B3。"""
    terrain = it.get("terrain")
    if terrain and terrain in exploration_mod.TERRAIN_TABLE:
        return terrain
    camp_id = state.get("campaign_id")
    if camp_id:
        try:
            sc = store.get_scene(camp_id)
            if sc and sc.environment:
                for t in exploration_mod.TERRAIN_TABLE:
                    if t in sc.environment:
                        return t
        except Exception:
            pass
    return terrain or "森林"


def resolve_travel(state, ch, it) -> dict:
    """探索流程：旅行步调/导航检定/被动察觉/随机遭遇/资源追踪。
    R-DM-026~040 / R-GLS-048
    """
    pace_raw = str(it.get("pace", "中速")).strip().lower()
    _PACE_ALIASES = {
        "fast": "快速", "快速": "快速",
        "normal": "中速", "中速": "中速", "medium": "中速",
        "slow": "慢速", "慢速": "慢速",
    }
    pace = _PACE_ALIASES.get(pace_raw, "中速")
    terrain = _resolve_terrain(state, it)
    try:
        _tp = exploration_mod.terrain_params(terrain)
        nav_dc = _tp.nav_dc
        perception_dc = _tp.search_dc
    except ValueError:
        nav_dc = int(it.get("nav_dc", 15))
        perception_dc = 15

    pace_info = exploration_mod.get_travel_pace(pace)
    # 导航检定仅在有迷路风险时掷（R-DM-037；沿已知道路/有向导→免检定，
    # 由 Director 的 needs_check 判断）；被动察觉本就不掷骰，照常计算。
    if it.get("needs_check") is False:
        nav_check = None
        nav_result = exploration_mod.NavigationResult(success=True, lost=False,
                                                      length_multiplier=1.0)
    else:
        nav_check = check.ability_check(mod=ch.ability_mod("wis"), prof=ch.prof(),
                                        proficient=True, dc=nav_dc)
        nav_result = exploration_mod.navigation(survival_total=nav_check.total, nav_dc=nav_dc)

    passive_perception = 10 + ch.ability_mod("wis")
    perception_result = exploration_mod.check_passive_perception(
        party_passive_scores=[(ch.name, passive_perception)],
        dc=perception_dc,
    )

    return {"kind": "travel", "pace": pace,
            "per_minute_ft": pace_info.per_minute_ft,
            "per_hour_miles": pace_info.per_hour_miles,
            "per_day_miles": pace_info.per_day_miles,
            "stealth_disadvantage": pace_info.stealth_disadvantage,
            "perception_disadvantage": pace_info.perception_disadvantage,
            "perception_advantage": pace_info.perception_advantage,
            "nav_result": dataclasses.asdict(nav_result),
            "nav_check_total": nav_check.total if nav_check else None,
            "nav_check_success": nav_result.success,
            "nav_check_skipped": nav_check is None,
            "perception_result": dataclasses.asdict(perception_result),
            "nav_dc": nav_dc,
            "perception_dc": perception_dc,
            "terrain": terrain}


# ──────────────────────────────────────────────────────────────────────────
# 战斗开始 + 突袭
# ──────────────────────────────────────────────────────────────────────────

def _determine_surprise(state, ch, it, combatants) -> dict:
    """B3 突袭判定。R-CMB-002 + R-GLS-009（2024 突袭=先攻劣势，不跳回合）"""
    explicit = str(it.get("surprise") or "").strip().lower()
    if explicit in ("player", "enemy", "none"):
        surprised_side = None if explicit == "none" else explicit
        note = "DM/系统指定"
    else:
        enemies = [c for c in combatants if not c.is_player]
        surprised_side = None
        note = "无敌方，无突袭"
        if enemies:
            stealth_best = max(int(getattr(c, "dex_mod", 0) or 0) for c in enemies)
            stealth_roll = engine_dice.roll_die(20) + stealth_best
            passive_perc = 10 + ch.ability_mod("wis")
            if stealth_roll >= passive_perc:
                surprised_side = "player"
                note = f"敌方隐匿{stealth_roll}≥你的被动察觉{passive_perc}，你被突袭"
            else:
                note = f"敌方隐匿{stealth_roll}<你的被动察觉{passive_perc}，双方互相察觉"
    if surprised_side:
        for c in combatants:
            if surprised_side == "player" and c.is_player or surprised_side == "enemy" and not c.is_player:
                c.surprised = True
    return {"surprised_side": surprised_side, "note": note}


def resolve_start_combat(state, ch, it) -> dict:
    """开始战斗：突袭判定 + roll_initiative + persist。R-CMB-002"""
    enemies = it.get("enemies") or [{"name": "敌人", "dex_mod": 1, "side": "enemy"}]
    combatants = [cmb.Combatant(cid=str(state["character_id"]), name=ch.name,
                                dex_mod=ch.ability_mod("dex"), side="player",
                                is_player=True, hp=ch.hp_current, hp_max=ch.hp_max)]
    for i, e in enumerate(enemies):
        _ename = e.get("name", f"敌人{i}")
        base: dict = {}
        try:
            from ...data import monsters as _mon
            _m = _mon.get_monster(_ename)
            if _m:
                base = _m.to_combatant_dict()
        except Exception:
            pass
        base.update({k: e[k] for k in ("hp_max", "hp", "attack_bonus", "damage_dice",
                     "damage_type", "dex_mod", "speed") if k in e})
        ehp = int(base.get("hp_max", base.get("hp", 7)) or 7)
        eab = int(base.get("attack_bonus", 4) or 4)
        edd = base.get("damage_dice") or "1d6+2"
        edt = base.get("damage_type") or "挥砍"
        edex = int(base.get("dex_mod", 0))
        espd = int(base.get("speed", 30))
        combatants.append(cmb.Combatant(cid=f"e{i}", name=_ename, dex_mod=edex,
                                        side="enemy", is_player=False,
                                        hp=ehp, hp_max=ehp,
                                        attack_bonus=eab, damage_dice=edd, damage_type=edt,
                                        speed=espd))
    surprise_info = _determine_surprise(state, ch, it, combatants)
    combat = cmb.Combat()
    order = cmb.roll_initiative(combatants)
    combat.participants = combatants
    combat.initiative_order = order
    combat.round = 1; combat.current_index = 0; combat.active = True
    cs = store.save_combat(state["campaign_id"], combat)
    return {"dice": {"kind": "start_combat",
                     "surprise": surprise_info,
                     "initiative_order": [{"name": c.name, "init": c.initiative,
                                           "side": c.side,
                                           "surprised": bool(getattr(c, "surprised", False))}
                                          for c in order]},
            "combat": {"active": True, "combat_id": cs.id, "round": 1,
                       "current_index": 0,
                       "combatants": [{"name": c.name, "init": c.initiative, "side": c.side,
                                       "cid": c.cid, "hp": c.hp, "hp_max": c.hp_max} for c in order]}}


# ──────────────────────────────────────────────────────────────────────────
# 目标确定性包装
# ──────────────────────────────────────────────────────────────────────────

def with_target_outcome(state, dice_out: dict) -> dict:
    """BUG#5/B2：攻击/单体法术造成伤害时，把目标与预计结果写入 dice。"""
    from ..utils import _HEAL_TYPES
    out: dict = {"dice": dice_out}
    if dice_out.get("error") or dice_out.get("damage_type") in _HEAL_TYPES:
        return out
    dmg = int(dice_out.get("damage") or 0)
    tcid = (state.get("intent", {}) or {}).get("target_cid")
    if not tcid or dmg <= 0:
        return out
    kind = dice_out.get("kind")
    if kind in ("attack", "opportunity_attack") and not dice_out.get("hit"):
        return out
    if kind == "cast":
        if not dice_out.get("hit", True) and not dice_out.get("auto_hit"):
            return out
        if dice_out.get("save_success") and dmg <= 0:
            return out
    for c in (state.get("combat", {}) or {}).get("combatants", []):
        if c.get("cid") == tcid:
            hp_before = int(c.get("hp") or 0)
            dice_out["target_cid"] = tcid
            dice_out["target_name"] = c.get("name", "")
            dice_out["target_hp_before"] = hp_before
            dice_out["target_killed"] = dmg >= hp_before > 0
            break
    return out


# ──────────────────────────────────────────────────────────────────────────
# 遭遇系统 + 时间推进
# ──────────────────────────────────────────────────────────────────────────

# 野外/危险场景关键词
_WILD_SCENE_KEYWORDS = (
    "野", "林", "山", "洞", "地城", "沼泽", "荒", "路", "径", "谷", "废墟",
    "forest", "dungeon", "cave", "wild", "road", "mountain", "swamp", "ruin",
)
# 镇内/室内等安全场景关键词
_SAFE_SCENE_KEYWORDS = (
    "镇", "村", "城", "市", "酒馆", "旅舍", "旅店", "客栈", "庙", "神殿", "教堂",
    "商店", "店铺", "家", "屋内", "室内", "书房", "大厅", "王宫", "城堡",
    "tavern", "inn", "town", "village", "city", "indoor", "shop", "temple",
)

# 动作→时间推进（分钟）
_ACTION_MINUTES = {"travel": 60, "explore": 30, "search": 10, "study": 10, "ability_check": 10}
# 遭遇时钟：每 4 游戏小时允许 1 次遭遇检定
_ENCOUNTER_CHECK_INTERVAL_MIN = 240
# 非战斗遭遇叙述提示
_ENCOUNTER_HINTS = {
    "environment": "环境事件：天气骤变/地形阻碍/自然奇观等，呈现为旅途插曲",
    "omen": "痕迹预兆：生物足迹/营地残骸/远处烟火等，暗示附近有威胁但未遭遇",
    "npc": "NPC相遇：旅人/商人/巡逻队等友善或中立角色，可互动",
}


def _scene_blocks_encounter(camp) -> bool:
    """场景过滤（矩阵#2）：镇内/室内等安全场景不刷野外战斗遭遇。"""
    try:
        sc = store.get_scene(camp)
    except Exception:
        return False
    if not sc:
        return False
    text = f"{sc.location or ''} {sc.environment or ''}".lower()
    if not text.strip():
        return False
    if any(k in text for k in _WILD_SCENE_KEYWORDS):
        return False
    return any(k in text for k in _SAFE_SCENE_KEYWORDS)


def _pick_encounter_enemies(ch) -> tuple:
    """按角色等级(CR段)从 monsters 表选遭遇怪。"""
    n = 1 if engine_dice.roll_die(2) == 1 else 2
    try:
        from ...data import monsters as _mon
        _pool = _mon.pick_encounter_pool(ch.level)
        if n >= 2:
            _low = [m for m in _pool if getattr(m, "cr", 1) <= 0.5]
            _sel = _low if _low else _pool
        else:
            _sel = _pool
        _m = _sel[engine_dice.roll_die(len(_sel)) - 1] if _sel else None
    except Exception:
        _m = None
    if _m:
        _md = _m.to_combatant_dict()
        return [dict(_md) for _ in range(n)], _m.name
    return ([{"name": "哥布林", "dex_mod": 2, "side": "enemy", "hp_max": 7,
              "attack_bonus": 4, "damage_dice": "1d6+2", "damage_type": "挥砍"}
             for _ in range(n)], "哥布林")


def _encounter_type(roll: int) -> str:
    """遭遇类型分布（d20）。"""
    if roll <= 10:
        return "combat"
    if roll <= 15:
        return "environment"
    if roll <= 19:
        return "omen"
    return "npc"


def advance_game_time(camp: int, minutes: int) -> dict:
    """推进战役游戏内时间（矩阵#8）。"""
    info: dict = {"advanced": minutes}
    try:
        c = store.get_campaign(camp)
        if not c:
            return info
        flags = c.world_flags
        before = int(flags.get("game_minutes", 8 * 60))
        after = before + max(0, int(minutes))
        flags["game_minutes"] = after
        c.set_world_flags(flags)
        store.save_campaign(c)
        day = after // 1440 + 1
        hour = (after % 1440) // 60
        clock = ("凌晨" if hour < 6 else "早晨" if hour < 9 else
                 "上午" if hour < 12 else "午后" if hour < 14 else
                 "下午" if hour < 17 else "黄昏" if hour < 20 else "夜晚")
        info.update({"minutes_before": before, "minutes_after": after,
                     "day": day, "clock": clock})
    except Exception as e:
        _log.debug("游戏时间推进失败 campaign=%s: %s", camp, e)
    return info


def _encounter_clock_allows(camp: int, now_min: int) -> tuple:
    """遭遇时钟（矩阵#4）：每 4 游戏小时最多 1 次遭遇检定。"""
    try:
        c = store.get_campaign(camp)
        if not c:
            return True, 0
        flags = c.world_flags
        last = int(flags.get("encounter_last_check_min", -10 ** 9))
        wait = _ENCOUNTER_CHECK_INTERVAL_MIN - (now_min - last)
        if wait > 0:
            return False, wait
        flags["encounter_last_check_min"] = now_min
        c.set_world_flags(flags)
        store.save_campaign(c)
        return True, 0
    except Exception:
        return True, 0


def with_encounter(state, ch, dice_out: dict) -> dict:
    """探索类动作统一处理（矩阵#1/#2/#4/#5/#6/#8，BUG#6 修复）。"""
    out: dict = {"dice": dice_out}
    camp = state.get("campaign_id")
    if not camp or not ch or ch.dead or dice_out.get("error"):
        return out
    if state.get("combat", {}).get("active"):
        return out
    time_info = advance_game_time(camp, _ACTION_MINUTES.get(dice_out.get("kind"), 10))
    if time_info.get("day"):
        dice_out["time"] = time_info
    if _scene_blocks_encounter(camp):
        dice_out["encounter"] = {"triggered": False, "suppressed": "safe_scene"}
        return out
    allowed, wait = _encounter_clock_allows(camp, int(time_info.get("minutes_after", 0)))
    if not allowed:
        dice_out["encounter"] = {"triggered": False, "suppressed": "clock",
                                 "next_check_in_min": wait}
        return out
    enc = exploration_mod.random_encounter_check()
    enc_info = dataclasses.asdict(enc)
    if not enc.triggered:
        dice_out["encounter"] = enc_info
        return out
    enc_type = _encounter_type(engine_dice.roll_die(20))
    enc_info["encounter_type"] = enc_type
    if enc_type != "combat":
        enc_info.update({"combat_started": False,
                         "prompt_hint": _ENCOUNTER_HINTS.get(enc_type, "")})
        dice_out["encounter"] = enc_info
        return out
    enemies, enc_name = _pick_encounter_enemies(ch)
    enc_state = {"character_id": state.get("character_id"), "campaign_id": camp}
    enc_dice = resolve_start_combat(enc_state, ch,
                                    {"action_type": "start_combat", "enemies": enemies})
    enc_info.update({"combat_started": True, "enemy_name": enc_name,
                     "enemy_count": len(enemies),
                     "surprise": enc_dice.get("dice", {}).get("surprise", {}),
                     "initiative_order": enc_dice.get("dice", {}).get("initiative_order", [])})
    dice_out["encounter"] = enc_info
    out["combat"] = enc_dice.get("combat", {})
    return out
