"""resolvers.apply — apply_node 及其辅助函数。

从 brain/graph.py 提取。包含:
  - apply_node: 状态应用 + 持久化 + 战斗轮次推进 + 死亡豁免
  - apply_damage_to_character: 伤害施加（含死亡/过量/专注豁免）
  - apply_healing_to_character: 治疗施加（含死亡计数归零）
  - run_monster_turn: 怪物回合自动攻击
  - render_monster_events: 怪物回合叙述渲染
"""

from __future__ import annotations

import json
import logging

from ...engine import check, damage
from ...engine import combat as cmb
from ...engine import dice as engine_dice
from ...stats import store
from ..utils import CLASS_CON_PROFICIENCY, _HEAL_TYPES, combatant_view
from .actions import apply_levelup_to_character, apply_rest_to_character

_log = logging.getLogger(__name__)


def apply_damage_to_character(ch, dmg: int, state) -> dict:
    """对角色施加伤害，含死亡/过量致死/专注豁免判定。
    R-DMG-007/009/014/017/018 + R-SPL-020 专注维持
    """
    result = {"dmg": dmg, "died": False, "death_failures_added": 0,
              "concentration_save": None}
    old_hp = ch.hp_current

    nhp, ntemp = damage.apply_damage_to_hp(ch.hp_current, ch.temp_hp, ch.hp_max, dmg)
    ch.hp_current = nhp
    ch.temp_hp = ntemp

    if ch.hp_current == 0 and damage.check_massive_damage(old_hp, ch.hp_max, dmg):
        ch.dead = True
        result["died"] = True
        result["death_reason"] = "过量伤害"
        return result
    if ch.hp_current == 0 and damage.check_hp_max_zero_death(ch.hp_max):
        ch.dead = True
        result["died"] = True
        result["death_reason"] = "HP上限归零"
        return result

    if old_hp == 0 and ch.hp_current == 0 and not ch.dead:
        tracker = ch.to_death_tracker()
        is_crit = bool(state.get("dice", {}).get("crit"))
        ds = damage.damage_at_zero_hp(tracker, dmg, is_crit, ch.hp_max)
        ch.apply_death_tracker(tracker)
        result["death_failures_added"] = ds.get("failures_added", 0)
        if ds.get("dead"):
            ch.dead = True
            result["died"] = True

    conc_on = state.get("dice", {}).get("concentrating_on") or state.get("intent", {}).get("concentrating_on")
    if conc_on and not ch.dead:
        conc_dc = cmb.concentration_save_dc(dmg)
        con_proficient = ch.char_class in CLASS_CON_PROFICIENCY
        sv = check.saving_throw(mod=ch.ability_mod("con"), prof=ch.prof(),
                                proficient=con_proficient, dc=conc_dc)
        result["concentration_save"] = {
            "spell": conc_on, "dc": conc_dc, "success": sv.success, "d20": sv.d20}
        if not sv.success:
            state.get("dice", {})["concentrating_on"] = None
            state.get("intent", {})["concentrating_on"] = None

    return result


def apply_healing_to_character(ch, heal: int) -> dict:
    """对角色施加治疗，含死亡计数归零。R-DMG-020 + R-ADD-008"""
    was_dying = ch.hp_current == 0 and not ch.dead
    ch.hp_current = damage.apply_healing(ch.hp_current, ch.hp_max, heal)
    result = {"heal": heal, "hp_after": ch.hp_current}
    if was_dying and ch.hp_current > 0:
        tracker = ch.to_death_tracker()
        damage.reset_death_counts_on_recovery(tracker)
        ch.apply_death_tracker(tracker)
        result["death_counts_reset"] = True
    return result


def run_monster_turn(monster, ch, state) -> dict:
    """怪物回合自动攻击玩家（确定性，不调 LLM）。"""
    atk = check.attack_roll(bonus=monster.attack_bonus, ac=ch.ac)
    ev = {"monster": monster.name, "hit": atk.hit, "damage": 0,
          "damage_type": monster.damage_type or "挥砍", "d20": atk.d20,
          "attack_total": atk.total, "player_hp_after": ch.hp_current}
    if atk.hit:
        dr = damage.roll_damage(damage.DamageRequest(
            dice_expr=monster.damage_dice or "1d6+2",
            damage_type=monster.damage_type or "挥砍",
            ability_mod=0, add_mod=False))
        ev["damage"] = dr.final
        res = apply_damage_to_character(ch, dr.final, state)
        ev["player_hp_after"] = ch.hp_current
        ev["died"] = res.get("died", False)
        ev["concentration_save"] = res.get("concentration_save")
    return ev


def render_monster_events(events: list) -> str:
    """把怪物回合事件渲染为追加到 narration 的文本。"""
    parts = []
    for ev in events:
        if ev.get("hit"):
            line = (f"【{ev['monster']}回合】攻击命中你（d20={ev['d20']}，攻击总值"
                    f"{ev['attack_total']}），造成{ev['damage']}点{ev['damage_type']}伤害，"
                    f"你当前HP {ev['player_hp_after']}。" +
                    ("你倒下了！" if ev.get("died") else ""))
        else:
            line = f"【{ev['monster']}回合】攻击未命中你（d20={ev['d20']}）。"
        cs = ev.get("concentration_save")
        if cs:
            line += f" 专注豁免DC{cs.get('dc')}（{cs.get('spell')}）d20={cs.get('d20')}→" + \
                    ("维持专注。" if cs.get("success") else "失去专注！")
        parts.append(line)
    return "\n" + "\n".join(parts)


def apply_node(state) -> dict:
    """应用状态变更 + 持久化（HP/法术位/日志/summary + 战斗轮次推进 + 死亡豁免/专注）。"""
    cid = state.get("character_id")
    camp = state.get("campaign_id")
    ch = store.get_character(cid) if cid else None
    combat_active = state.get("combat", {}).get("active")
    monster_events: list = []
    narration_changed = False

    # 玩家主动结束战斗 → 持久化 active=False
    if camp and state.get("dice", {}).get("kind") == "end_combat":
        try:
            _c = store.load_combat(camp)
            _c.active = False
            store.save_combat(camp, _c)
        except Exception as e:
            _log.warning("结束战斗持久化失败 campaign=%s: %s", camp, e)
    narration_changed = False

    # 1) 结构化状态变更：玩家角色 HP / temp_hp / conditions
    for chg in state.get("state_changes", []):
        target = str(chg.get("target"))
        field = chg.get("field")
        try:
            delta = int(chg.get("delta", 0))
        except (ValueError, TypeError):
            continue
        if (target != str(cid) and (not ch or target != ch.name)) or not ch:
            continue
        _dice = state.get("dice", {})
        _is_heal_sc = (field == "hp" and delta > 0
                       and (_dice.get("kind") == "use_item"
                            or (_dice.get("kind") == "cast"
                                and _dice.get("damage_type") in ("治疗", "heal", "healing"))))
        if _is_heal_sc:
            continue
        if field == "hp":
            _cap = max(1, 2 * int(ch.hp_max or 1))
            delta = max(-_cap, min(_cap, delta))
            if delta < 0:
                apply_damage_to_character(ch, -delta, state)
            elif delta > 0:
                apply_healing_to_character(ch, delta)
        elif field == "temp_hp" and delta > 0:
            ch.temp_hp = damage.grant_temp_hp(ch.temp_hp, min(delta, int(ch.hp_max or 1)))

    # 2) 施法消耗法术位 R-SPL-002
    if ch and state.get("dice", {}).get("kind") == "cast":
        lvl = state["dice"].get("spell_level", 1)
        import json as _j
        try:
            sd = _j.loads(ch.spell_slots_json)
        except Exception as e:
            _log.debug("法术位 JSON 解析失败 cid=%s，回退为空: %s", cid, e)
            sd = {}
        if lvl >= 1 and sd.get(str(lvl), 0) > 0:
            sd[str(lvl)] -= 1
        ch.spell_slots_json = _j.dumps(sd)

    # 2.5) 休息收益落盘
    if ch and state.get("dice", {}).get("kind") == "rest":
        apply_rest_to_character(ch, state["dice"])
        if (camp and state["dice"].get("type") == "long"
                and state["dice"].get("success")):
            try:
                _c_camp = store.get_campaign(camp)
                if _c_camp:
                    _fl = _c_camp.world_flags
                    _fl[f"last_long_rest_min_{ch.id}"] = int(_fl.get("game_minutes", 8 * 60))
                    _c_camp.set_world_flags(_fl)
                    store.save_campaign(_c_camp)
            except Exception as e:
                _log.warning("长休时刻记录失败 camp=%s: %s", camp, e)

    # 2.6) 升级收益落盘
    if ch and state.get("dice", {}).get("kind") == "levelup":
        apply_levelup_to_character(ch, state["dice"])

    # 2.7) 社交态度持久化
    if camp and state.get("dice", {}).get("kind") == "social":
        ds_social = state["dice"]
        try:
            sc = store.get_scene(camp)
            if sc:
                npcs = sc.npcs
                name = ds_social.get("npc_name")
                new_att = ds_social.get("new_attitude") or ds_social.get("npc_attitude")
                cs = ds_social.get("consec_success", 0)
                cf = ds_social.get("consec_failure", 0)
                updated = False
                for n in npcs:
                    if n.get("name") == name:
                        n["attitude"] = new_att
                        n["success_count"] = cs
                        n["failure_count"] = cf
                        updated = True
                        break
                if not updated and name:
                    npcs.append({"name": name, "attitude": new_att, "role": "",
                                 "success_count": cs, "failure_count": cf})
                sc.set_npcs(npcs)
                store.save_scene(sc)
        except Exception as e:
            _log.warning("社交态度持久化失败 campaign=%s: %s", camp, e)

    # 2.8) use_item 治疗物品落盘
    if ch and state.get("dice", {}).get("kind") == "use_item":
        heal = int(state["dice"].get("heal", 0) or 0)
        if heal > 0:
            apply_healing_to_character(ch, heal)
        _consumed = state["dice"].get("consumed_item")
        if _consumed:
            _inv2 = ch.inventory
            if _consumed in _inv2:
                _inv2.remove(_consumed)
                ch.set_inventory(_inv2)

    # 2.9) 施法治疗法术落盘
    if ch and state.get("dice", {}).get("kind") == "cast" and state["dice"].get("damage_type") in ("治疗", "heal", "healing"):
        _cast_heal = int(state["dice"].get("damage", 0) or 0)
        if _cast_heal > 0:
            apply_healing_to_character(ch, _cast_heal)

    if ch:
        if not ch.dead and ch.exhaustion >= 6:
            ch.dead = True
            state["narration"] = (state.get("narration", "") or "") + "\n【力竭】力竭达到 6 级，你死了。"
            narration_changed = True
        store.save_character(ch)

    # 3) 战斗轮次推进 + 死亡豁免 + 怪物 HP 应用
    if combat_active and camp:
        try:
            combat = store.load_combat(camp)
            _enemy_damaged = False
            # 3a-target) BUG#5/B2 确定性扣血
            _det_cid = None
            _det_name = None
            _dr0 = state.get("dice", {})
            if (combat.active and _dr0.get("kind") in ("attack", "opportunity_attack", "cast")
                    and _dr0.get("damage_type") not in _HEAL_TYPES
                    and int(_dr0.get("damage") or 0) > 0 and _dr0.get("target_cid")):
                _want = _dr0["target_cid"]
                for _lst in (combat.participants, combat.initiative_order):
                    for _c in _lst:
                        if _c.cid == _want and not _c.is_player and not _c.dead:
                            _det_cid = _c.cid
                            _det_name = _c.name
                if _det_cid:
                    _dmg_val = int(_dr0["damage"])
                    for _lst in (combat.participants, combat.initiative_order):
                        for _c in _lst:
                            if _c.cid == _det_cid:
                                _c.hp = max(0, _c.hp - _dmg_val)
                                if _c.hp <= 0:
                                    _c.dead = True
                    _enemy_damaged = True
            for chg in state.get("state_changes", []):
                tgt = str(chg.get("target")); field = chg.get("field")
                try:
                    delta = int(chg.get("delta", 0))
                except (ValueError, TypeError):
                    continue
                if field != "hp" or delta == 0 or tgt == str(cid):
                    continue
                if _det_cid and delta < 0:
                    if _dr0.get("kind") in ("attack", "opportunity_attack"):
                        continue
                    if tgt in (_det_cid, _det_name):
                        continue
                target_cid = None
                for _lst in (combat.participants, combat.initiative_order):
                    for _c in _lst:
                        if _c.cid == tgt and not _c.is_player:
                            target_cid = _c.cid; break
                    if target_cid: break
                if target_cid is None:
                    for _lst in (combat.participants, combat.initiative_order):
                        for _c in _lst:
                            if not _c.is_player and _c.name == tgt and not _c.dead:
                                target_cid = _c.cid; break
                        if target_cid: break
                if target_cid:
                    for _lst in (combat.participants, combat.initiative_order):
                        for _c in _lst:
                            if _c.cid == target_cid:
                                _c.hp = max(0, _c.hp + delta)
                                if _c.hp <= 0:
                                    _c.dead = True
                    if delta < 0:
                        _enemy_damaged = True
            # 3a-deterministic) 伤害应用兜底
            _dk = state.get("dice", {}).get("kind")
            _dr = state.get("dice", {})
            if (combat.active and not _enemy_damaged
                    and _dk in ("attack", "opportunity_attack", "cast")
                    and _dr.get("damage_type") not in _HEAL_TYPES
                    and int(_dr.get("damage") or 0) > 0):
                _dmg_val = int(_dr["damage"])
                _tgt_name = state.get("intent", {}).get("target_name", "")
                _fallback = None
                for _lst in (combat.participants, combat.initiative_order):
                    for _c in _lst:
                        if (not _c.is_player and not _c.dead and _c.hp > 0
                                and _tgt_name and _c.name == _tgt_name):
                            _fallback = _c.cid; break
                    if _fallback: break
                if _fallback is None:
                    for _lst in (combat.participants, combat.initiative_order):
                        for _c in _lst:
                            if not _c.is_player and not _c.dead and _c.hp > 0:
                                _fallback = _c.cid; break
                        if _fallback: break
                if _fallback:
                    for _lst in (combat.participants, combat.initiative_order):
                        for _c in _lst:
                            if _c.cid == _fallback:
                                _c.hp = max(0, _c.hp - _dmg_val)
                                if _c.hp <= 0:
                                    _c.dead = True
            # 3b) 同步玩家参战者 HP
            if ch:
                for _lst in (combat.participants, combat.initiative_order):
                    for _c in _lst:
                        if _c.is_player and _c.cid == str(cid):
                            _c.hp = ch.hp_current; _c.dead = ch.dead
            # 3c) 判战斗结束
            cmb.check_combat_end(combat)
            # 3d) 死亡豁免
            if (combat.active and ch and ch.hp_current == 0
                    and not ch.dead and not ch.stable):
                tracker = ch.to_death_tracker()
                ds = damage.death_save(tracker)
                ch.apply_death_tracker(tracker)
                regain = int(ds.get("regain_hp", 0))
                if regain:
                    ch.hp_current = max(ch.hp_current, regain)
                roll = ds.get("roll", 0)
                if regain:
                    ds_text = f"【死亡豁免】d20={roll}，天然20！恢复1HP并苏醒。"
                elif ds.get("stable"):
                    ds_text = f"【死亡豁免】d20={roll}，累计3次成功，伤势稳定。"
                elif ds.get("dead"):
                    ds_text = f"【死亡豁免】d20={roll}，累计3次失败，你死了。"
                elif roll >= 10:
                    ds_text = f"【死亡豁免】d20={roll}≥10成功（成功{tracker.successes}/失败{tracker.failures}）。"
                else:
                    ds_text = f"【死亡豁免】d20={roll}<10失败（成功{tracker.successes}/失败{tracker.failures}）。"
                state["narration"] = (state.get("narration", "") or "") + "\n" + ds_text
                narration_changed = True
                store.save_character(ch)
                for _lst in (combat.participants, combat.initiative_order):
                    for _c in _lst:
                        if _c.is_player and _c.cid == str(cid):
                            _c.hp = ch.hp_current; _c.dead = ch.dead
            # 3e) 推进回合 + 自动结算连续怪物回合
            _dk = state.get("dice", {}).get("kind")
            if combat.active and _dk in ("disengage", "dash") and ch and ch.hp_current > 0:
                _alive_e = sum(1 for c in combat.participants
                               if c.side == "enemy" and not c.dead and c.hp > 0)
                _flee_dc = 10 + _alive_e * 2
                _flee_roll = engine_dice.roll_die(20)
                if _flee_roll + ch.ability_mod("dex") >= _flee_dc:
                    combat.active = False
                    state["narration"] = (state.get("narration", "") or "") + \
                        f"\n【脱战】你成功摆脱追击逃离战斗（d20={_flee_roll}+dex vs DC{_flee_dc}）！"
                    narration_changed = True
                    store.save_combat(camp, combat)
            _just_started = bool(state.get("dice", {}).get("encounter", {}).get("combat_started"))
            if combat.active and not _just_started:
                cmb.advance_turn(combat)
            monster_events = []
            _skip_guard = 0
            while combat.active and ch:
                cur = cmb.current_combatant(combat)
                if cur is None or cur.is_player:
                    break
                if cur.dead or cur.hp <= 0:
                    _skip_guard += 1
                    if _skip_guard > len(combat.initiative_order) + 2:
                        break
                    cmb.advance_turn(combat)
                    continue
                if ch.hp_current > 0 and not ch.dead:
                    ev = run_monster_turn(cur, ch, state)
                    monster_events.append(ev)
                    for _lst in (combat.participants, combat.initiative_order):
                        for _c in _lst:
                            if _c.is_player and _c.cid == str(cid):
                                _c.hp = ch.hp_current; _c.dead = ch.dead
                if ch.hp_current <= 0 or ch.dead:
                    cmb.check_combat_end(combat)
                    break
                cmb.check_combat_end(combat)
                if not combat.active:
                    break
                cmb.advance_turn(combat)
            if ch:
                store.save_character(ch)
            store.save_combat(camp, combat)
            if monster_events:
                state["narration"] = (state.get("narration") or "") + render_monster_events(monster_events)
            state["combat"] = {
                "active": combat.active, "combat_id": None, "round": combat.round,
                "current_index": combat.current_index,
                "combatants": [combatant_view(_c) for _c in combat.initiative_order]}
        except Exception as e:
            _log.warning("战斗轮次推进/死亡豁免失败 campaign=%s cid=%s: %s", camp, cid, e)

    # 4) 持久化日志
    if camp:
        store.append_log(camp, player_input=state.get("player_input", ""),
                         dm_output=state.get("narration", ""),
                         dice_rolls=[state.get("dice", {})])

    # 5) 场景推进
    scene_update = state.get("scene_update", "")
    if scene_update and camp:
        sc = store.get_scene(camp)
        if sc:
            sc.situation = scene_update
            store.save_scene(sc)

    # 5b) 地点迁移
    loc_change = (state.get("location_change") or "").strip()
    if loc_change and camp:
        sc = store.get_scene(camp)
        if sc and loc_change not in (sc.location or ""):
            sc.location = loc_change
            sc.environment = ""
            sc.set_npcs([])
            store.save_scene(sc)

    # 6) 记忆处理已移至 API 层异步执行
    if narration_changed or monster_events:
        return {"narration": state.get("narration", ""), "combat": state.get("combat", {})}
    if combat_active:
        return {"combat": state.get("combat", {})}
    return {}
