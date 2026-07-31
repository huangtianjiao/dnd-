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
from ..stats import store
from .utils import combatant_view

_log = logging.getLogger(__name__)

# 士气系统（DMG 战斗或者逃跑）：P2 特性，默认关闭
_MORALE_ENABLED = os.getenv("AIDM_MORALE", "0").lower() in ("1", "true")


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
    """
    standing = _standing_players(combat, chars)
    return random.choice(standing) if standing else None


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

    与旧版唯一区别: 目标 ch 由 select_target 决定，不再固定为最后行动者；
    事件含 target 字段。0HP 受重击记 2 次死亡豁免失败用怪物自己的 crit。
    """
    from .resolvers.apply import apply_damage_to_character

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
        # 专注来源：行动者自身 state（同请求内刚施法）优先，否则读角色卡持久化值
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
        # 专注被打断：落盘 + 回写行动者 state（保持旧行为）
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

    # guard: 8轮+16 次推进封顶——濒死者最多约5个自身回合内必然稳定或死亡，
    # 正常战斗远达不到；防御未知状态导致的服务端死循环。
    for _ in range(8 * n + 16):
        cur = cmb.advance_turn(combat)
        if cur is None:                                   # 全员丧失行动能力
            break
        if combat.round != prev_round:
            events.append({"type": "round_end", "round": prev_round})
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
            cmb.check_combat_end(combat)
            if not combat.active:
                break
            continue
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
