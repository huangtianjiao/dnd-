"""多人战斗回合状态机 — 服务端统一驱动回合推进与怪物回合结算。

设计文档: docs/MULTIPLAYER_COMBAT_REDESIGN.md
核心原则: 回合归属权是唯一真相，由本模块驱动推进；
          玩家行动只消耗动作经济，不隐式推进回合。

规则出处:
  - R-CMB-001~004 战斗流程: topics/玩家手册2024/进行游戏/战斗流程.htm
  - R-DMG-017 死亡豁免（以0HP开始回合时掷）: 进行游戏/生命值降至0点.htm
  - DMG 怪物行为/目标选择: topics/城主指南2024/4.创建冒险/规划遭遇/怪物行为.htm
  - DMG 战斗或者逃跑（士气）: topics/城主指南2024/2.运作游戏/运作战斗/战斗或者逃跑.htm
"""

from __future__ import annotations

import logging
import os
import random
from dataclasses import dataclass, field

from ..engine import check, damage
from ..engine import combat as cmb
from ..engine import dice as engine_dice
from ..engine.attack_sequence import AttackPlan, AttackSequence
from ..engine.reaction_window import (
    ReactionController,
    ReactionOption,
    ReactionType,
    ReadyEffect,
)
from ..stats import store
from .utils import combatant_view

_log = logging.getLogger(__name__)

# ★ COM-009/010: 全局反应控制器与准备动作追踪
_reaction_controller = ReactionController()
_ready_effects: dict[str, ReadyEffect] = {}  # entity_id → ReadyEffect

# 士气系统（DMG 战斗或者逃跑）：P2 特性，默认关闭
# P2-01: 统一经 Settings 读取（AIDM_MORALE）
from ..config import get_settings as _get_settings
_MORALE_ENABLED = _get_settings().aidm_morale


# ──────────────────────────────────────────────────────────────────────────
# 结果结构
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class FlowResult:
    """advance_and_resolve 的返回值。

    events:  依序发生的事件（monster_action / death_save / round_end /
             monster_flee / combat_end）
    combat:  推进后的战斗状态（已持久化）；None=该战役无战斗状态
    current: 停在谁的回合（玩家参战者）；None=战斗结束
    ended:   战斗是否已结束
    """
    events: list = field(default_factory=list)
    combat: cmb.Combat | None = None
    current: cmb.Combatant | None = None
    ended: bool = False


# ──────────────────────────────────────────────────────────────────────────
# 辅助
# ──────────────────────────────────────────────────────────────────────────

def _is_multiplayer(campaign_id: int) -> bool:
    """房间内玩家 >1 视为多人局（多人语义：显式 end_turn；单人保留自动推进）。"""
    try:
        from .room import CampaignRoom
        room = CampaignRoom.get(campaign_id)
        return bool(room and len(room.players) > 1)
    except Exception:
        return False


def _sync_player_combatant(combat: cmb.Combat, ch) -> None:
    """把角色卡权威 HP/死亡 同步进参战者（双列表容旧数据，正常已共享对象）。"""
    cid = str(ch.id)
    for lst in (combat.initiative_order, combat.participants):
        for c in lst:
            if c.is_player and c.cid == cid:
                c.hp = ch.hp_current
                c.dead = ch.dead


def _standing_players(combat: cmb.Combat, chars: dict) -> list:
    """还站着的玩家角色卡（HP>0 且未死未逃）。"""
    out = []
    for c in combat.initiative_order:
        if not c.is_player or c.dead or c.fled:
            continue
        ch = chars.get(c.cid)
        if ch is not None and not ch.dead and ch.hp_current > 0:
            out.append(ch)
    return out


def _all_players_resolved(combat: cmb.Combat, chars: dict) -> bool:
    """无人站立，且倒地者全部已稳定或已死 → 玩家方被击败。

    规则: PHB 结束战斗——一方全部被击杀或被击晕则战斗结束。
    出处: topics/玩家手册2024/进行游戏/战斗流程.htm
    """
    if _standing_players(combat, chars):
        return False
    for c in combat.initiative_order:
        if not c.is_player or c.dead or c.fled:
            continue
        ch = chars.get(c.cid)
        if ch is not None and not ch.dead and not ch.stable:
            return False                      # 仍有人在掷死亡豁免
    return True


def _outcome(combat: cmb.Combat) -> str:
    """战斗结果：敌方全灭 → players_win，否则 enemies_win。"""
    enemies_alive = [c for c in combat.participants
                     if c.side == "enemy" and not c.dead and not c.fled and c.hp > 0]
    return "players_win" if not enemies_alive else "enemies_win"


combat_outcome = _outcome          # 公开别名（供 api/ws.py 等外部使用）


# ──────────────────────────────────────────────────────────────────────────
# 怪物目标选择（DMG 怪物行为）
# ──────────────────────────────────────────────────────────────────────────

def select_target(monster: cmb.Combatant, chars: dict, combat: cmb.Combat):
    """从全体站立玩家中随机选目标（等权）。

    规则: DMG 怪物行为——不应固定纠缠单一目标（「不要重复游戏状态」）；
          DMG 无集火规则，随机最贴近其精神。
    出处: topics/城主指南2024/4.创建冒险/规划遭遇/怪物行为.htm
    说明: 不选倒地(0HP)者——怪物不鞭尸刷死亡豁免失败；
          全员倒地时返回 None（由 _all_players_resolved 判定战斗结束）。

    ★ ENV-001: engine.vision.can_see 过滤不可见目标——怪物无法攻击
      完全不可见（全遮蔽/黑暗且无黑暗视觉）的玩家。
    """
    standing = _standing_players(combat, chars)
    if not standing:
        return None
    try:
        from ..engine.vision import can_see
        visible = []
        for ch in standing:
            _v = can_see(
                {"darkvision_ft": 60, "on_ground": True},
                target_light="bright",
                distance_ft=float(getattr(ch, "distance_ft", 30) or 30),
            )
            if _v.get("can_see", True):
                visible.append(ch)
        if visible:
            return random.choice(visible)
    except Exception as e:
        _log.debug("vision 可见性过滤失败（回退随机）: %s", e)
    return random.choice(standing)


def morale_check(monster: cmb.Combatant, combat: cmb.Combat) -> bool:
    """士气检查：浴血(≤半血)且过半盟友倒下 → WIS DC10 豁免，失败则逃跑。

    规则: DMG 战斗或者逃跑
    出处: topics/城主指南2024/2.运作游戏/运作战斗/战斗或者逃跑.htm
    返回: True=继续战斗；False=士气崩溃（上层置 fled）。
    """
    bloodied = monster.hp_max > 0 and monster.hp <= monster.hp_max // 2
    allies = [c for c in combat.participants if c.side == monster.side]
    downed = sum(1 for c in allies if c.dead or c.fled or c.hp <= 0)
    if not (bloodied and allies and downed * 2 > len(allies)):
        return True
    return check.saving_throw(mod=0, prof=0, proficient=False, dc=10).success


# ──────────────────────────────────────────────────────────────────────────
# 怪物回合结算（自 resolvers/apply.py 迁入，目标改为可指定）
# ──────────────────────────────────────────────────────────────────────────

def run_monster_turn(monster: cmb.Combatant, ch, state: dict | None = None,
                     db_path: str = store.DEFAULT_DB) -> dict:
    """怪物回合自动攻击指定玩家（确定性，不调 LLM）。

    ★ MON-001: 怪物使用与玩家相同的 ActionDefinition/Effect 系统。
      MonsterCompiler 将 StatBlock 编译为可执行动作列表。
    """
    from .resolvers.apply import apply_damage_to_character
    from ..data.monster_compiler import MonsterCompiler

    # ★ MON-001: 尝试编译怪物 StatBlock
    compiler = MonsterCompiler()
    stat_block = compiler.compile_from_existing(monster.name)

    # 获取目标 AC
    target_ac = getattr(ch, "ac", 10)

    # ★ MON-002: 充能/传奇动作/传奇抗性接线
    legendary_events: list[dict] = []
    from ..engine.legendary_actions import (
        LairAction, LairActionManager, LegendaryAction, LegendaryActionPool,
        LegendaryResistance, RechargeTracker,
    )
    # 回合开始时恢复充能（RechargeAtTurnStart）
    monster_recharge_tracker = RechargeTracker(
        current_charges=1, max_charges=1,
        recharge_min=getattr(monster, "recharge_min", 6) or 6,
    )
    monster_recharge_tracker.recharge_at_turn_start()

    # 检查怪物是否有传奇动作（通过 combatant 字段）
    legendary_pool = None
    legendary_max = getattr(monster, "legendary_actions_max", 0) or 0
    if legendary_max > 0:
        legendary_pool = LegendaryActionPool(
            actions=[
                LegendaryAction(action_id="legendary_action",
                                name="传奇动作", cost=1),
            ],
            uses_per_round=legendary_max,
        )
        legendary_events.append({"type": "legendary_pool_ready",
                                 "uses": legendary_max})

    # 传奇抗性（LegendaryResistanceOnFailedSave）
    legendary_resist = None
    legendary_resist_max = getattr(monster, "legendary_resistances_max", 0) or 0
    if legendary_resist_max > 0:
        legendary_resist = LegendaryResistance(uses_per_day=legendary_resist_max)

    # 巢穴动作（LairInitiative）— 若怪物是巢穴生物
    lair_mgr = None
    if getattr(monster, "lair_actions", None):
        lair_mgr = LairActionManager()
        lair_mgr.add_action(LairAction(action_id="lair_action", name="巢穴动作",
                                       initiative_count=20))

    # 如果编译成功且有动作，使用 MonsterAction 系统
    if stat_block and stat_block.actions:
        # 选择第一个可用动作
        valid_actions = compiler.get_valid_actions(stat_block, {
            "action_type": "action",
            "has_used_action": False,
            "target_distance_ft": 5,
            "target_ac": target_ac,
        })
        if valid_actions:
            action = valid_actions[0]
            events = compiler.execute_action(stat_block, action, str(ch.id), {
                "target_ac": target_ac,
            })
            # 从事件中提取结果
            ev_data = events[0] if events else {}
            atk_hit = ev_data.get("is_hit", False)
            atk_d20 = ev_data.get("attack_roll", 0)
            atk_total = ev_data.get("total_attack", 0)
            dmg = ev_data.get("damage", 0)
            dmg_type = ev_data.get("damage_type", monster.damage_type or "挥砍")

            ev = {"monster": monster.name, "target": ch.name,
                  "hit": atk_hit, "damage": dmg,
                  "damage_type": dmg_type, "d20": atk_d20,
                  "attack_total": atk_total, "player_hp_after": ch.hp_current,
                  "monster_actions": {
                      "recharge_ready": monster_recharge_tracker.can_use(),
                      "legendary_available": bool(legendary_pool),
                      "legendary_resist_available": bool(
                          legendary_resist and legendary_resist.can_resist()),
                      "lair_available": bool(lair_mgr),
                  }}

            if atk_hit and dmg > 0:
                # 专注来源
                conc = None
                if isinstance(state, dict):
                    conc = (state.get("dice", {}).get("concentrating_on")
                            or state.get("intent", {}).get("concentrating_on"))
                if not conc:
                    try:
                        conc = store.get_concentration(ch.id, db_path).get("spell") or None
                    except Exception:
                        conc = None
                inner = {"dice": {"crit": False, "concentrating_on": conc}, "intent": {}}
                res = apply_damage_to_character(ch, dmg, inner)
                ev["player_hp_after"] = ch.hp_current
                ev["died"] = res.get("died", False)
                ev["concentration_save"] = res.get("concentration_save")
                if conc and inner["dice"].get("concentrating_on") is None:
                    try:
                        store.set_concentration(ch.id, "", 0, db_path)
                    except Exception as e:
                        _log.debug("专注打断落盘失败 cid=%s: %s", ch.id, e)
                    if isinstance(state, dict):
                        state.get("dice", {}).pop("concentrating_on", None)
                        state.get("intent", {}).pop("concentrating_on", None)
            return ev

    # 回退到基础攻击
    atk = check.attack_roll(bonus=monster.attack_bonus, ac=ch.ac)
    ev = {"monster": monster.name, "target": ch.name,
          "hit": atk.hit, "damage": 0,
          "damage_type": monster.damage_type or "挥砍", "d20": atk.d20,
          "attack_total": atk.total, "player_hp_after": ch.hp_current}
    if atk.hit:
        dr = damage.roll_damage(damage.DamageRequest(
            dice_expr=monster.damage_dice or "1d6+2",
            damage_type=monster.damage_type or "挥砍",
            ability_mod=0, add_mod=False))
        ev["damage"] = dr.final
        conc = None
        if isinstance(state, dict):
            conc = (state.get("dice", {}).get("concentrating_on")
                    or state.get("intent", {}).get("concentrating_on"))
        if not conc:
            try:
                conc = store.get_concentration(ch.id, db_path).get("spell") or None
            except Exception:
                conc = None
        inner = {"dice": {"crit": atk.crit, "concentrating_on": conc}, "intent": {}}
        res = apply_damage_to_character(ch, dr.final, inner)
        ev["player_hp_after"] = ch.hp_current
        ev["died"] = res.get("died", False)
        ev["concentration_save"] = res.get("concentration_save")
        if conc and inner["dice"].get("concentrating_on") is None:
            try:
                store.set_concentration(ch.id, "", 0, db_path)
            except Exception as e:
                _log.debug("专注打断落盘失败 cid=%s: %s", ch.id, e)
            if isinstance(state, dict):
                state.get("dice", {}).pop("concentrating_on", None)
                state.get("intent", {}).pop("concentrating_on", None)
    return ev


def render_monster_events(events: list, self_name: str | None = None) -> str:
    """把怪物回合事件渲染为追加到 narration 的文本。

    self_name: 视角角色名——目标是自己时用「你」（保持单人叙事口吻）。
    """
    parts = []
    for ev in events:
        tgt = ev.get("target")
        who = "你" if (not tgt or tgt == self_name) else tgt
        if ev.get("hit"):
            line = (f"【{ev['monster']}回合】攻击命中{who}（d20={ev['d20']}，攻击总值"
                    f"{ev['attack_total']}），造成{ev['damage']}点{ev['damage_type']}伤害，"
                    f"{who}当前HP {ev['player_hp_after']}。" +
                    (f"{who}倒下了！" if ev.get("died") else ""))
        else:
            line = f"【{ev['monster']}回合】攻击未命中{who}（d20={ev['d20']}）。"
        cs = ev.get("concentration_save")
        if cs:
            line += f" 专注豁免DC{cs.get('dc')}（{cs.get('spell')}）d20={cs.get('d20')}→" + \
                    ("维持专注。" if cs.get("success") else "失去专注！")
        parts.append(line)
    return "\n" + "\n".join(parts)


# ──────────────────────────────────────────────────────────────────────────
# 死亡豁免（自 resolvers/apply.py 3d 段迁入；时点改为回合开始）
# ──────────────────────────────────────────────────────────────────────────

def _roll_death_save(ch, db_path: str = store.DEFAULT_DB) -> dict | None:
    """为 0HP 濒死角色掷死亡豁免并落盘。

    规则: R-DMG-017「每当你以0生命值开始回合时」
    出处: topics/玩家手册2024/进行游戏/生命值降至0点.htm
    返回: death_save 事件 dict；已稳定/已死则返回 None（无需掷）。
    """
    if ch.stable or ch.dead:
        return None
    tracker = ch.to_death_tracker()
    ds = damage.death_save(tracker)
    ch.apply_death_tracker(tracker)
    regain = int(ds.get("regain_hp", 0))
    if regain:
        ch.hp_current = max(ch.hp_current, regain)
    roll = ds.get("roll", 0)
    if regain:
        text = f"【死亡豁免·{ch.name}】d20={roll}，天然20！恢复1HP并苏醒。"
    elif ds.get("stable"):
        text = f"【死亡豁免·{ch.name}】d20={roll}，累计3次成功，伤势稳定。"
    elif ds.get("dead"):
        text = f"【死亡豁免·{ch.name}】d20={roll}，累计3次失败，死亡。"
    elif roll >= 10:
        text = f"【死亡豁免·{ch.name}】d20={roll}≥10成功（成功{tracker.successes}/失败{tracker.failures}）。"
    else:
        text = f"【死亡豁免·{ch.name}】d20={roll}<10失败（成功{tracker.successes}/失败{tracker.failures}）。"
    store.save_character(ch, db_path)
    return {"type": "death_save", "player": ch.name, "roll": roll,
            "successes": tracker.successes, "failures": tracker.failures,
            "stable": bool(ds.get("stable")), "dead": bool(ds.get("dead")),
            "regain": regain, "text": text}


# ──────────────────────────────────────────────────────────────────────────
# 核心：推进回合并自动结算非玩家回合
# ──────────────────────────────────────────────────────────────────────────

def advance_and_resolve(campaign_id: int, db_path: str = store.DEFAULT_DB,
                        actor_state: dict | None = None,
                        actor_cid: str | None = None) -> FlowResult:
    """推进回合并自动结算怪物/濒死者回合，直到轮到可行动的玩家或战斗结束。

    这是多人死锁问题（review 问题 B/C）的结构性修复：
    end_turn 之后凡轮到怪物由服务端立即结算，永不停在无人能操作的回合上。

    actor_state/actor_cid: 单人自动推进路径传入行动者的判定链 state，
    用于专注跟踪的同请求内传递（见 run_monster_turn）。
    """
    try:
        combat = store.load_combat(campaign_id, db_path)
    except KeyError:
        return FlowResult(events=[], combat=None, current=None, ended=True)
    if not combat.active:
        return FlowResult(events=[], combat=combat, current=None, ended=True)
    # 入口先判一次：可能玩家刚击杀最后一名敌人后才 end_turn
    cmb.check_combat_end(combat)
    if not combat.active:
        store.save_combat(campaign_id, combat, db_path)
        return FlowResult(events=[{"type": "combat_end", "outcome": _outcome(combat)}],
                          combat=combat, current=None, ended=True)

    chars = {str(c.id): c for c in store.list_characters(campaign_id, db_path)}
    events: list[dict] = []
    prev_round = combat.round
    n = max(1, len(combat.initiative_order))

    # ★ TEST-003: 每场战斗确定性 RNG（campaign+round 种子，可回放）
    _rng = _battle_rng(campaign_id, combat.round)
    if _rng is not None:
        try:
            engine_dice.set_active_rng(_rng)
        except Exception as e:
            _log.debug("战斗 RNG 注入失败（跳过）: %s", e)

    # ★ PERF-001: 回合推进入口加载聚合快照（engine.aggregate_cache / performance_cache）
    try:
        from ..engine.aggregate_cache import load_aggregate_snapshot as _load_agg
        _agg_ch = chars.get(str(actor_cid)) if actor_cid else None
        _agg = _load_agg(str(_agg_ch.id) if _agg_ch else "0", str(campaign_id))
        events.append({"type": "aggregate_snapshot",
                       "character_id": _agg.character_id,
                       "spell_slots": _agg.spell_slots,
                       "version": _agg.version})
    except Exception as e:
        _log.debug("聚合快照加载失败（跳过）: %s", e)

    # ★ PERF-001: 规则定义缓存（engine.performance_cache）——版本化缓存命中统计
    try:
        from ..engine.performance_cache import get_rule_cache
        _rc = get_rule_cache()
        _rc.set_version("2024.1")
        _cache_key = f"combat:{campaign_id}:round:{combat.round}"
        _cached = _rc.get(_cache_key)
        if _cached is None:
            _rc.set(_cache_key, {"campaign_id": campaign_id,
                                 "round": combat.round,
                                 "combatants": len(combat.initiative_order)})
            events.append({"type": "rule_cache", "hit": False, "key": _cache_key})
        else:
            events.append({"type": "rule_cache", "hit": True, "key": _cache_key})
    except Exception as e:
        _log.debug("规则缓存读写失败（跳过）: %s", e)

    # guard: 8轮+16 次推进封顶——濒死者最多约5个自身回合内必然稳定或死亡，
    # 正常战斗远达不到；防御未知状态导致的服务端死循环。
    for _ in range(8 * n + 16):
        cur = cmb.advance_turn(combat)
        if cur is None:                                   # 全员丧失行动能力
            break
        if combat.round != prev_round:
            events.append({"type": "round_end", "round": prev_round})
            # ★ COM-014/SPL-009: 轮次边界推进效果/调度器（engine.effects + scheduler）
            try:
                _round_events = _tick_round_effects(combat, prev_round)
                events.extend(_round_events)
            except Exception as e:
                _log.debug("轮次效果推进失败（跳过）: %s", e)
            # ★ TEST-003: 轮次推进后刷新确定性 RNG
            _rng = _battle_rng(campaign_id, combat.round)
            if _rng is not None:
                try:
                    engine_dice.set_active_rng(_rng)
                except Exception:
                    pass
            prev_round = combat.round

        hook = cmb.begin_turn(combat, cur)
        if hook["needs_death_save"]:                      # R-DMG-017 回合开始掷
            ch = chars.get(cur.cid)
            if ch is not None:
                ds_ev = _roll_death_save(ch, db_path)
                if ds_ev:
                    _sync_player_combatant(combat, ch)
                    events.append(ds_ev)
                if ch.hp_current > 0:                     # 天然20苏醒 → 本回合可行动
                    hook["auto_end"] = False
        if hook["auto_end"]:
            cmb.check_combat_end(combat)
            if not combat.active:
                break
            if _all_players_resolved(combat, chars):      # PHB: 全员击晕=被击败
                combat.active = False
                events.append({"type": "combat_end", "outcome": "enemies_win"})
                break
            continue

        if cur.is_player:                                 # 停：等这个玩家输入
            break

        # —— 怪物回合（服务端确定性结算）——
        if _MORALE_ENABLED and not morale_check(cur, combat):
            cur.fled = True
            events.append({"type": "monster_flee", "monster": cur.name})
            # ★ R-CMB-025: 怪物逃离触及范围 → 玩家借机攻击（engine.opportunity_attack 权威判定）
            try:
                _oa_events = _opportunity_attack_on_flee(cur, chars, combat)
                events.extend(_oa_events)
            except Exception as e:
                _log.debug("逃跑借机攻击判定失败（跳过）: %s", e)
            cmb.check_combat_end(combat)
            if not combat.active:
                break
            continue

        # ★ MON-002: 怪物回合开始时处理充能（RechargeAtTurnStart）
        try:
            recharge_events = process_recharge_at_turn_start(cur.name, cur.cid)
            events.extend(recharge_events)
        except Exception as e:
            _log.debug("充能处理失败 %s: %s", cur.name, e)

        target = select_target(cur, chars, combat)
        if target is None:                                # 无站立目标
            if _all_players_resolved(combat, chars):
                combat.active = False
                events.append({"type": "combat_end", "outcome": "enemies_win"})
                break
            continue                                       # 尚有人濒死掷豁免，怪物观望
        st = actor_state if (actor_state is not None
                             and str(target.id) == str(actor_cid)) else None
        mev = run_monster_turn(cur, target, state=st, db_path=db_path)
        mev["type"] = "monster_action"
        store.save_character(target, db_path)
        _sync_player_combatant(combat, target)
        events.append(mev)

        # ★ MON-002: 怪物回合结束后打开传奇动作窗口（LegendaryWindowAfterTurn）
        try:
            legendary_events = process_legendary_actions_after_turn(
                cur.name, cur.cid, combat.round)
            events.extend(legendary_events)
        except Exception as e:
            _log.debug("传奇动作处理失败 %s: %s", cur.name, e)

        # ★ MON-002: 处理巢穴动作（LairInitiative）
        try:
            lair_events = process_lair_actions(cur.name, cur.cid,
                                               cur.initiative)
            events.extend(lair_events)
        except Exception as e:
            _log.debug("巢穴动作处理失败 %s: %s", cur.name, e)

        cmb.check_combat_end(combat)
        if not combat.active:
            break
    else:
        _log.warning("advance_and_resolve 达到推进上限 campaign=%s round=%s",
                     campaign_id, combat.round)

    store.save_combat(campaign_id, combat, db_path)
    ended = not combat.active
    current = cmb.current_combatant(combat) if combat.active else None
    if ended and not any(e.get("type") == "combat_end" for e in events):
        events.append({"type": "combat_end", "outcome": _outcome(combat)})
    return FlowResult(events=events, combat=combat, current=current, ended=ended)


# ──────────────────────────────────────────────────────────────────────────
# 轮次效果推进 / 确定性 RNG / 逃跑借机攻击（engine 权威接线）
# ──────────────────────────────────────────────────────────────────────────

def _battle_rng(campaign_id: int, round_num: int):
    """TEST-003: 创建确定性 RNG（campaign+round 种子），注入 engine.dice。

    优先 engine.rng_context（randbelow 兼容 dice 注入钩子），
    回退 engine.rng（ReplayEngine）。
    """
    try:
        from ..engine.rng_context import create_rng_context
        return create_rng_context(seed=int(campaign_id * 1000 + round_num))
    except Exception:
        try:
            from ..engine.rng import ReplayEngine
            rng = ReplayEngine(seed=int(campaign_id * 1000 + round_num))
            return rng
        except Exception:
            return None


def _tick_round_effects(combat: cmb.Combat, round_num: int) -> list[dict]:
    """COM-014/SPL-009: 轮次边界推进持续效果与调度器。

    engine.effects.EffectManager 负责效果数据（过期/去重），
    engine.scheduler.DurationScheduler 负责时间推进（到期事件）。
    当前战斗 param 的 active_effects（dict 形式）同步为 EffectInstance 后 tick。
    """
    from ..engine.effects import EffectInstance, EffectManager, SourceRef
    from ..engine.scheduler import DurationScheduler, ScheduledEffect
    mgr = EffectManager()
    sched = DurationScheduler()
    ticked: list[dict] = []

    for c in list(combat.initiative_order):
        for e in list(getattr(c, "active_effects", []) or []):
            name = e.get("effect", "")
            if not name:
                continue
            inst = EffectInstance(
                source=SourceRef(entity_id=c.cid, feature_id=name),
                target_id=c.cid,
                name=name,
                condition_name=name,
                duration=None,
            )
            sched.schedule(ScheduledEffect(
                effect_id=f"{c.cid}_{name}",
                duration_type="rounds",
                remaining=1,
                expire_on="round_end",
                target_entity_id=c.cid,
                metadata={"effect": name},
            ))
            mgr.add(inst)
    expired = sched.on_round_end(round_num)
    for ev in expired:
        _eid = ev.get("effect_id", "") if isinstance(ev, dict) else ""
        _target, _name = _eid.split("_", 1) if "_" in _eid else ("", _eid)
        for c in list(combat.initiative_order):
            if c.cid == _target or _target == "":
                cmb.remove_effect(c, _name) if hasattr(cmb, "remove_effect") else None
        ticked.append({"type": "effect_expired", "effect": _name,
                       "target": _target, "round": round_num})
    return ticked


def _opportunity_attack_on_flee(monster: cmb.Combatant, chars: dict,
                                combat: cmb.Combat) -> list[dict]:
    """R-CMB-025: 怪物逃离触及范围时，检查相邻玩家是否触发借机攻击。

    使用 engine.opportunity_attack 权威判定 + engine.battle_map 距离计算。
    """
    from ..engine.opportunity_attack import (
        can_make_opportunity_attack,
        opportunity_attack,
    )
    from ..engine.battle_map import BattleMap
    events: list[dict] = []

    # 用战斗位置构建 BattleMap（缺省 50x50 网格）
    bm = BattleMap(width=50, height=50, grid_size_ft=5.0)
    for p in list(combat.participants) + list(combat.initiative_order):
        if p.position is not None:
            bm.move_entity(p.cid, (0, 0), p.position)

    for ch in chars.values():
        if ch.hp_current <= 0:
            continue
        dist = bm.get_distance_ft(monster.position, (0, 0)) if monster.position else 5.0
        if dist > max(monster.reach, 5):
            continue  # 怪物不在任何玩家触及范围内，无借机攻击
        if can_make_opportunity_attack(monster, monster, target_leaving_reach=True):
            result = opportunity_attack(monster, monster)
            events.append({
                "type": "opportunity_attack",
                "attacker": ch.name,
                "monster": monster.name,
                "hit": bool(result.get("hit")),
                "damage": result.get("damage", 0),
                "note": "怪物逃跑引发借机攻击",
            })
    return events


def peek_next_name(combat: cmb.Combat) -> str | None:
    """预告下一位（DMG 跟进先攻:「顺口提及下一位」）。不修改状态。"""
    if not combat.active or not combat.initiative_order:
        return None
    n = len(combat.initiative_order)
    for i in range(1, n + 1):
        c = combat.initiative_order[(combat.current_index + i) % n]
        if not cmb._cannot_act(c):
            return c.name
    return None


# ──────────────────────────────────────────────────────────────────────────
# MON-002: 充能、传奇动作、传奇抗性、巢穴动作
# ──────────────────────────────────────────────────────────────────────────

from ..data.monster_compiler import (
    LairActionController,
    MonsterCompiler,
    RechargeTracker,
)

# 全局充能追踪器
_recharge_tracker = RechargeTracker()
# 全局巢穴动作控制器
_lair_controller = LairActionController()


def process_recharge_at_turn_start(monster_name: str, monster_id: str) -> list[dict]:
    """MON-002: 回合开始时为怪物的充能动作掷骰。

    规则: 回合开始掷 d6，>= 阈值则充能成功，可使用一次。
    出处: topics/城主指南2024/怪物图鉴/怪物充能.htm

    Args:
        monster_name: 怪物名称
        monster_id: 怪物唯一 ID

    Returns:
        充能事件列表
    """
    events: list[dict] = []

    # 尝试编译怪物 StatBlock
    compiler = MonsterCompiler()
    stat_block = compiler.compile_from_existing(monster_name)

    if stat_block and stat_block.recharge_abilities:
        for ra in stat_block.recharge_abilities:
            ability_id = ra.get("ability_id", ra.get("action_id", ""))
            threshold = ra.get("recharge_threshold", 6)

            # 注册充能动作（如果尚未注册）
            if not _recharge_tracker.is_charged(monster_id, ability_id):
                _recharge_tracker.register(monster_id, ability_id, initially_charged=True)

            # 掷骰尝试充能
            charged = _recharge_tracker.roll_recharge(
                monster_id, ability_id, threshold=threshold
            )

            if charged:
                events.append({
                    "type": "recharge_success",
                    "monster_id": monster_id,
                    "ability_id": ability_id,
                    "threshold": threshold,
                })
            else:
                events.append({
                    "type": "recharge_failed",
                    "monster_id": monster_id,
                    "ability_id": ability_id,
                    "threshold": threshold,
                })

    return events


def process_legendary_actions_after_turn(
    monster_name: str,
    monster_id: str,
    round_num: int,
) -> list[dict]:
    """MON-002: 其他生物回合结束后处理传奇动作。

    规则: 传奇生物可以在其他生物回合结束时执行传奇动作。
          每个传奇动作消耗一定数量的传奇动作点数。
    出处: topics/城主指南2024/怪物图鉴/传奇动作.htm

    Args:
        monster_name: 怪物名称
        monster_id: 怪物唯一 ID
        round_num: 当前回合

    Returns:
        传奇动作事件列表
    """
    events: list[dict] = []

    # 尝试编译怪物 StatBlock
    compiler = MonsterCompiler()
    stat_block = compiler.compile_from_existing(monster_name)

    if not stat_block or not stat_block.legendary_actions:
        return events

    if stat_block.legendary_action_points <= 0:
        return events

    # 简单 AI：选择第一个可负担的传奇动作执行
    for la in stat_block.legendary_actions:
        cost = la.get("cost", 1) if isinstance(la, dict) else 1
        if cost <= stat_block.legendary_action_points:
            # 执行传奇动作
            action_data = la if isinstance(la, dict) else {"name": str(la)}

            # 如果传奇动作有伤害，结算伤害
            damage_dice = action_data.get("damage_dice", "")
            damage_type = action_data.get("damage_type", "")
            attack_bonus = action_data.get("attack_bonus", 0)

            event = {
                "type": "legendary_action",
                "monster_id": monster_id,
                "monster_name": monster_name,
                "action_name": action_data.get("name", ""),
                "cost": cost,
                "round": round_num,
            }

            if damage_dice:
                from ..engine import dice as engine_dice
                dmg_roll = engine_dice.roll_dice(damage_dice)
                event["damage"] = dmg_roll.total
                event["damage_type"] = damage_type
                event["damage_dice"] = damage_dice

            if attack_bonus:
                event["attack_bonus"] = attack_bonus

            events.append(event)

            # 消耗传奇动作点数
            stat_block.legendary_action_points -= cost
            break  # 每次只执行一个传奇动作

    return events


def use_legendary_resistance_on_failed_save(
    monster_name: str,
    monster_id: str,
) -> bool:
    """MON-002: 豁免失败时使用传奇抗性。

    规则: 传奇生物可以选择在豁免失败时使用传奇抗性，
          将失败变为成功。每日使用次数有限。
    出处: topics/城主指南2024/怪物图鉴/传奇抗性.htm

    Args:
        monster_name: 怪物名称
        monster_id: 怪物唯一 ID

    Returns:
        是否成功使用了传奇抗性
    """
    # 尝试编译怪物 StatBlock
    compiler = MonsterCompiler()
    stat_block = compiler.compile_from_existing(monster_name)

    if not stat_block or stat_block.legendary_resistance_count <= 0:
        return False

    # 消耗一次传奇抗性
    stat_block.legendary_resistance_count -= 1
    return True


def process_lair_actions(
    monster_name: str,
    monster_id: str,
    current_initiative: int,
) -> list[dict]:
    """MON-002: 处理巢穴动作。

    规则: 巢穴动作在先攻计数到指定值时触发（通常 20）。
    出处: topics/城主指南2024/怪物图鉴/巢穴动作.htm

    Args:
        monster_name: 怪物名称
        monster_id: 怪物唯一 ID
        current_initiative: 当前先攻计数

    Returns:
        巢穴动作事件列表
    """
    events: list[dict] = []

    # 尝试编译怪物 StatBlock
    compiler = MonsterCompiler()
    stat_block = compiler.compile_from_existing(monster_name)

    if not stat_block or not stat_block.lair_actions:
        return events

    # 检查是否应触发巢穴动作
    if not _lair_controller.should_trigger(monster_id, current_initiative):
        return events

    # 执行巢穴动作
    for i, la in enumerate(stat_block.lair_actions):
        result = _lair_controller.execute_lair_action(monster_id, i, {})
        if result.get("type") == "lair_action_executed":
            events.append({
                "type": "lair_action",
                "monster_id": monster_id,
                "monster_name": monster_name,
                "action": la,
                "initiative": current_initiative,
            })

    return events


# ──────────────────────────────────────────────────────────────────────────
# COM-009/010: 准备动作与反应窗口
# ──────────────────────────────────────────────────────────────────────────

def register_ready_action(
    entity_id: str,
    prepared_action: dict,
    trigger_predicate=None,
    requires_concentration: bool = True,
    current_round: int = 0,
) -> ReadyEffect:
    """注册一个准备动作 (COM-010)。

    Args:
        entity_id: 准备动作的实体 ID
        prepared_action: 预备的 Command 模板
        trigger_predicate: 触发条件谓词
        requires_concentration: 是否需要专注
        current_round: 当前回合

    Returns:
        创建的 ReadyEffect
    """
    ready = ReadyEffect(
        entity_id=entity_id,
        prepared_action=prepared_action,
        trigger_predicate=trigger_predicate,
        requires_concentration=requires_concentration,
    )
    ready.activate(current_round)
    _ready_effects[entity_id] = ready
    return ready


def trigger_ready_actions(event: dict, current_round: int) -> list[dict]:
    """检查所有准备动作是否被触发 (COM-010)。

    Args:
        event: 触发事件
        current_round: 当前回合

    Returns:
        被触发的准备动作列表
    """
    triggered: list[dict] = []
    to_remove: list[str] = []

    for entity_id, ready in _ready_effects.items():
        if ready.matches_trigger(event):
            triggered.append({
                "type": "ready_triggered",
                "entity_id": entity_id,
                "action": ready.prepared_action,
            })
            to_remove.append(entity_id)

    # 移除已触发的准备动作
    for eid in to_remove:
        del _ready_effects[eid]

    # 过期的准备动作
    expired: list[str] = []
    for entity_id, ready in _ready_effects.items():
        if ready.expires_round <= current_round:
            expired.append(entity_id)

    for eid in expired:
        del _ready_effects[eid]

    return triggered


def open_reaction_window(
    trigger_event: str,
    context: dict,
    eligible_reactors: list[str],
    reactions: list[ReactionOption] | None = None,
) -> Any:
    """打开一个反应窗口 (COM-009)。

    Args:
        trigger_event: 触发事件类型
        context: 反应上下文
        eligible_reactors: 可反应者 ID 列表
        reactions: 可用反应选项列表

    Returns:
        创建的 ReactionWindow
    """
    return _reaction_controller.open(
        trigger_event=trigger_event,
        context=context,
        eligible_reactors=eligible_reactors,
        reactions=reactions,
    )


# ──────────────────────────────────────────────────────────────────────────
# 单人局兼容：玩家行动后自动推进（替代旧 apply.py 3e 段）
# ──────────────────────────────────────────────────────────────────────────

def post_action_advance(campaign_id: int, character_id: int | None,
                        state: dict, db_path: str = store.DEFAULT_DB) -> list[dict]:
    """单人局（房间≤1人）在玩家行动结算后自动结束其回合并推进。

    多人局返回 [] 不做任何推进（显式 end_turn 语义）。
    行为与旧 3e 段等价：行动→自动跑怪物回合→narration 追加怪物事件文本。
    """
    if _is_multiplayer(campaign_id):
        return []
    if state.get("dice", {}).get("encounter", {}).get("combat_started"):
        return []                                          # 刚开战不推进（保留首回合）
    try:
        c = store.load_combat(campaign_id, db_path)
    except KeyError:
        return []
    if not c.active:
        return []

    actor_cid = str(character_id) if character_id else None
    flow = advance_and_resolve(campaign_id, db_path=db_path,
                               actor_state=state, actor_cid=actor_cid)

    self_name = None
    if character_id:
        ch = store.get_character(character_id, db_path)
        if ch:
            self_name = ch.name
    m_events = [e for e in flow.events if e.get("type") == "monster_action"]
    if m_events:
        state["narration"] = (state.get("narration") or "") + \
            render_monster_events(m_events, self_name=self_name)
    for e in flow.events:
        if e.get("type") == "death_save":
            state["narration"] = (state.get("narration") or "") + "\n" + e["text"]
        elif e.get("type") == "monster_flee":
            state["narration"] = (state.get("narration") or "") + \
                f"\n【士气】{e['monster']} 士气崩溃，逃离了战斗！"
    if flow.combat is not None:
        state["combat"] = {
            "active": flow.combat.active, "combat_id": None,
            "round": flow.combat.round,
            "current_index": flow.combat.current_index,
            "combatants": [combatant_view(x) for x in flow.combat.initiative_order]}
    return flow.events
