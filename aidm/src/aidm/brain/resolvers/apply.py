"""resolvers.apply — apply_node 及其辅助函数。

从 brain/graph.py 提取。包含:
  - apply_node: 状态应用 + 持久化 + 动作经济标记
  - apply_damage_to_character: 伤害施加（含死亡/过量/专注豁免）
  - apply_healing_to_character: 治疗施加（含死亡计数归零）

回合推进/怪物回合/死亡豁免已迁至 brain/combat_flow.py（服务端回合状态机，
见 docs/MULTIPLAYER_COMBAT_REDESIGN.md）：
  - 玩家行动不再隐式结束回合；单人局由 post_action_advance 保留自动推进
  - 死亡豁免时点修正为「以0HP开始回合时」（R-DMG-017）
  - run_monster_turn / render_monster_events 保留 re-export 兼容旧引用
"""

from __future__ import annotations

import logging

from ...engine import check, damage
from ...engine import combat as cmb
from ...engine import dice as engine_dice
from ...engine.entity_lifecycle import EntityLifecycleManager
from ...engine.entity_state import EntityState, EntityStateRegistry, EntityType
from ...engine.health_state import HealthStateMachine
from ...stats import store
from ..utils import _HEAL_TYPES, CLASS_CON_PROFICIENCY, combatant_view
from .actions import apply_levelup_to_character, apply_rest_to_character

_log = logging.getLogger(__name__)

# ★ STATE-001: EntityStateRegistry 作为单一权威状态源
# 所有实体状态变更通过 registry 进行，自动维护版本号（乐观锁）
_entity_registry = EntityStateRegistry()
_lifecycle_mgr = EntityLifecycleManager()


def _sync_character_to_registry(ch) -> EntityState:
    """将 Character 同步到 EntityStateRegistry。

    如果角色已在注册表中，更新其字段；
    如果不在，创建新的 EntityState 并注册。

    Returns:
        与角色关联的 EntityState
    """
    entity_id = str(ch.id)
    try:
        state = _entity_registry.get(entity_id)
    except KeyError:
        state = EntityState(
            entity_id=entity_id,
            entity_type=EntityType.CHARACTER,
            ability_scores={k: v for k, v in ch.abilities.items()},
            hp_current=ch.hp_current,
            hp_max=ch.hp_max,
            temp_hp=ch.temp_hp,
            armor_class=ch.ac,
            speed=ch.speed,
            proficiency_bonus=ch.prof(),
            conditions=list(ch.conditions_list),
            active_effects=[],
            resource_pools={},
        )
        _entity_registry.register(state)
        return state

    # 更新已有状态
    state.hp_current = ch.hp_current
    state.hp_max = ch.hp_max
    state.temp_hp = ch.temp_hp
    state.armor_class = ch.ac
    state.conditions = list(ch.conditions_list)
    state.bump_version()
    return state


def _sync_registry_to_character(ch) -> None:
    """将 EntityStateRegistry 中的状态同步回 Character。"""
    entity_id = str(ch.id)
    try:
        state = _entity_registry.get(entity_id)
    except KeyError:
        return
    ch.hp_current = state.hp_current
    ch.hp_max = state.hp_max
    ch.temp_hp = state.temp_hp
    ch.ac = state.armor_class


# 规则: R-CMB-011 一次一个动作 —— 这些 dice.kind 消耗本回合的一个动作
# 出处: topics/玩家手册2024/进行游戏/动作.htm
_ACTION_KINDS = ("attack", "cast", "dash", "dodge", "disengage", "help",
                 "hide", "search", "study", "use_item", "grapple", "shove",
                 "ready", "social")


def apply_damage_to_character(ch, dmg: int, state) -> dict:
    """对角色施加伤害，含死亡/过量致死/专注豁免判定。
    R-DMG-007/009/014/017/018 + R-SPL-020 专注维持

    ★ STATE-001: 通过 EntityStateRegistry 作为单一权威状态源。
      所有 HP 变更先写入 registry，再同步回 Character。
    ★ DMG-002: 使用 HealthStateMachine 统一 0HP / 非致命击倒 / 死亡流程。
    """
    result = {"dmg": dmg, "died": False, "death_failures_added": 0,
              "concentration_save": None}

    # ★ STATE-001: 同步到 registry 作为权威状态源
    entity_state = _sync_character_to_registry(ch)

    # 从 registry 读取当前 HP（权威值）
    old_hp = entity_state.hp_current

    # 计算新 HP（通过 registry 的权威值）
    nhp, ntemp = damage.apply_damage_to_hp(
        entity_state.hp_current, entity_state.temp_hp, entity_state.hp_max, dmg
    )

    # 将新 HP 写入 registry（权威更新）
    entity_state.hp_current = nhp
    entity_state.temp_hp = ntemp
    entity_state.bump_version()

    # 同步回 Character（保持兼容性）
    ch.hp_current = nhp
    ch.temp_hp = ntemp

    if ch.hp_current == 0 and damage.check_massive_damage(old_hp, ch.hp_max, dmg):
        ch.dead = True
        result["died"] = True
        result["death_reason"] = "过量伤害"
        _sync_character_to_registry(ch)
        return result
    if ch.hp_current == 0 and damage.check_hp_max_zero_death(ch.hp_max):
        ch.dead = True
        result["died"] = True
        result["death_reason"] = "HP上限归零"
        _sync_character_to_registry(ch)
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
        # R-GLS-047 力竭适用于含豁免在内的所有 d20 检定（每级 −2）
        exh_penalty = -conditions.d20_penalty(ch.to_condition_state())
        sv = check.saving_throw(mod=ch.ability_mod("con"), prof=ch.prof(),
                                proficient=con_proficient, dc=conc_dc,
                                circ=exh_penalty)
        result["concentration_save"] = {
            "spell": conc_on, "dc": conc_dc, "success": sv.success, "d20": sv.d20}
        if not sv.success:
            state.get("dice", {})["concentrating_on"] = None
            state.get("intent", {})["concentrating_on"] = None

    return result


def apply_healing_to_character(ch, heal: int) -> dict:
    """对角色施加治疗，含死亡计数归零。R-DMG-020 + R-ADD-008

    ★ STATE-001: 通过 EntityStateRegistry 作为单一权威状态源。
    """
    # ★ STATE-001: 同步到 registry
    entity_state = _sync_character_to_registry(ch)

    was_dying = entity_state.hp_current == 0 and not ch.dead
    new_hp = damage.apply_healing(entity_state.hp_current, entity_state.hp_max, heal)

    # 将新 HP 写入 registry（权威更新）
    entity_state.hp_current = new_hp
    entity_state.bump_version()

    # 同步回 Character
    ch.hp_current = new_hp

    result = {"heal": heal, "hp_after": new_hp}
    if was_dying and new_hp > 0:
        tracker = ch.to_death_tracker()
        damage.reset_death_counts_on_recovery(tracker)
        ch.apply_death_tracker(tracker)
        result["death_counts_reset"] = True
    return result


def run_monster_turn(monster, ch, state=None) -> dict:
    """已迁至 brain/combat_flow.py；此处保留兼容包装供旧引用。"""
    from ..combat_flow import run_monster_turn as _impl
    return _impl(monster, ch, state)


def render_monster_events(events: list, self_name: str | None = None) -> str:
    """已迁至 brain/combat_flow.py；此处保留兼容包装供旧引用。"""
    from ..combat_flow import render_monster_events as _impl
    return _impl(events, self_name=self_name)


def apply_node(state) -> dict:
    """应用状态变更 + 持久化（HP/法术位/日志/summary + 战斗轮次推进 + 死亡豁免/专注）。

    ★ STATE-001: EntityStateRegistry 作为单一权威状态源。
      开始时将 Character 同步到 registry，
      所有伤害/治疗通过 registry 路由，
      结束时将 registry 状态同步回 Character 并持久化。
    """
    cid = state.get("character_id")
    camp = state.get("campaign_id")
    ch = store.get_character(cid) if cid else None
    # ★ STATE-003: 幂等键检查——重复提交相同 key 只返回原结果，不重复执行
    idempotency_key = state.get("idempotency_key") or ""
    if idempotency_key:
        try:
            from ...engine.unit_of_work import get_idempotency_store
            cached = get_idempotency_store().check(idempotency_key)
            if cached is not None:
                _log.info("幂等命中 key=%s，跳过重复结算", idempotency_key)
                return {"idempotent": True, "result": cached.result_data}
        except Exception as e:
            _log.debug("幂等检查失败（跳过）: %s", e)
    # ★ STATE-001: 同步到 registry 作为权威状态源
    if ch:
        _sync_character_to_registry(ch)
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

    # 2) 施法消耗法术位 R-SPL-002 / SPL-014
    #    法术位只由 cast_spell 的 Commit 阶段标记消耗（slot_consumed=True）。
    #    失败施法、戏法、仪式均不产生 slot_consumed，apply 不扣法术位。
    if ch and state.get("dice", {}).get("kind") == "cast":
        _dice = state["dice"]
        _slot_consumed = _dice.get("slot_consumed", False)
        if _slot_consumed:
            lvl = _dice.get("spell_level", 1)
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

    # 2.6b) ★ ENT-002: 召唤/变形效果生命周期追踪（engine.entity_lifecycle_ext 权威实现）
    if ch and state.get("dice", {}).get("kind") == "cast":
        _dice = state["dice"]
        _spell = _dice.get("spell_name", "")
        if any(k in _spell for k in ("召唤", "造物", "魔法兽", "Conjure")):
            try:
                from ...engine.entity_lifecycle_ext import EntityLifecycleManager as ExtLifecycle
                _ext_mgr = ExtLifecycle()
                _sv = _ext_mgr.summon(
                    summoner_id=str(ch.id),
                    spell_id=_spell,
                    stat_block={"name": _spell, "hp": 10, "ac": 10},
                    duration=10,
                )
                _dice["summoned_entity_id"] = _sv.entity_id
                _dice["summoned_by"] = "entity_lifecycle_ext"
            except Exception as e:
                _log.debug("召唤实体注册失败（跳过）: %s", e)

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
        # ★ STATE-001: 将 registry 权威状态同步回 Character 并持久化
        _sync_registry_to_character(ch)
        _sync_character_to_registry(ch)
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
            # 3d) 动作经济标记（R-CMB-011 一次一个动作；P0 宽松版：只标记不硬拒，
            #     避免 LLM 意图分类误伤；P1 收紧为硬约束）
            #     死亡豁免已迁至 combat_flow（回合开始时掷，R-DMG-017）。
            _dk = state.get("dice", {}).get("kind")
            if combat.active:
                _cur = cmb.current_combatant(combat)
                if _cur is not None and _cur.is_player and _cur.cid == str(cid):
                    if _dk in _ACTION_KINDS:
                        if not cmb.use_action(_cur):
                            state["narration"] = (state.get("narration", "") or "") + \
                                "\n（本回合动作已用完，可结束回合。）"
                            narration_changed = True
                        if not cmb.can_take_action(_cur):
                            state["turn_hint"] = "action_exhausted"
                    elif _dk == "opportunity_attack":
                        cmb.use_reaction(_cur)                    # R-CMB-013
            # 玩家主动脱战（disengage/dash 逃跑检定）
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
            if ch:
                store.save_character(ch)
            store.save_combat(camp, combat)
            # 3e) 回合推进：多人局由 ws.on_end_turn 显式推进（服务端回合状态机）；
            #     单人局由 post_action_advance 保留旧「行动即结束回合」体验。
            from ..combat_flow import post_action_advance
            monster_events = post_action_advance(camp, cid, state)
            if not monster_events:
                state["combat"] = {
                    "active": combat.active, "combat_id": None, "round": combat.round,
                    "current_index": combat.current_index,
                    "combatants": [combatant_view(_c) for _c in combat.initiative_order]}
        except Exception as e:
            _log.warning("战斗状态应用/推进失败 campaign=%s cid=%s: %s", camp, cid, e)

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
    out: dict = {}
    if state.get("turn_hint"):
        out["turn_hint"] = state["turn_hint"]
    if narration_changed or monster_events:
        out["narration"] = state.get("narration", "")
        out["combat"] = state.get("combat", {})
    elif combat_active:
        out["combat"] = state.get("combat", {})

    # ★ STATE-003: 记录幂等键 → 结果，防止重试重复结算
    if idempotency_key:
        try:
            from ...engine.unit_of_work import get_idempotency_store, CommandResult
            get_idempotency_store().record(CommandResult(
                command_id=idempotency_key,
                idempotency_key=idempotency_key,
                success=True,
                result_data=out,
            ))
        except Exception as e:
            _log.debug("幂等记录失败（跳过）: %s", e)

    return out
