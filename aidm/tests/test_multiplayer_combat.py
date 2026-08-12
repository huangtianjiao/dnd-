"""多人战斗回合状态机测试 — brain/combat_flow.py

验证设计文档 docs/MULTIPLAYER_COMBAT_REDESIGN.md §6 的测试计划:
  1. 死锁回归: end_turn 后怪物回合由服务端自动结算，停在下一个玩家
  2. 跳过死者: 死亡参战者不再获得回合；全怪物死 → combat_end
  3. 死亡豁免时点: 受伤当下不掷；轮到濒死者回合开始才掷 (R-DMG-017)
  4. 目标选择: 怪物目标覆盖全体站立玩家；倒地者不被选中
  5. 序列化往返: 全字段（conditions/移动力/group_id）存取一致；旧格式可加载
  7. 动作经济: 同回合第二次动作收到 turn_hint 提示（P0 宽松版）

运行:
  PYTHONPATH=src python tests/test_multiplayer_combat.py
  PYTHONPATH=src python -m pytest tests/test_multiplayer_combat.py -v
"""

from __future__ import annotations

import os
import sys
import tempfile

from aidm.brain import combat_flow
from aidm.engine import combat as cmb
from aidm.engine import dice
from aidm.stats import models as M
from aidm.stats import store

CAMP = 9901


# ──────────────────────────────────────────────────────────────────────────
# 辅助
# ──────────────────────────────────────────────────────────────────────────

class _FakeRoll:
    def __init__(self, used):
        self.used = used
        self.rolls = [used]
        self.mode = "normal"


def _tmp_db() -> str:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    return f"sqlite:///{path}"


def _mk_char(db, name, hp=10, ac=20) -> M.Character:
    ch = M.Character(name=name, campaign_id=CAMP, hp_current=hp, hp_max=hp, ac=ac)
    return store.save_character(ch, db)


def _pc(ch: M.Character, init: int) -> cmb.Combatant:
    return cmb.Combatant(cid=str(ch.id), name=ch.name, initiative=init,
                         side="player", is_player=True,
                         hp=ch.hp_current, hp_max=ch.hp_max)


def _monster(cid, name, init, hp=7, atk=4, dice_expr="1d6+2") -> cmb.Combatant:
    return cmb.Combatant(cid=cid, name=name, initiative=init, side="enemy",
                         is_player=False, hp=hp, hp_max=hp,
                         attack_bonus=atk, damage_dice=dice_expr)


def _save_combat(db, order, current_index=0, active=True, rnd=1) -> cmb.Combat:
    c = cmb.Combat(participants=list(order), initiative_order=list(order),
                   round=rnd, current_index=current_index, active=active)
    store.save_combat(CAMP, c, db)
    return c


# ──────────────────────────────────────────────────────────────────────────
# 1. 死锁回归
# ──────────────────────────────────────────────────────────────────────────

def test_deadlock_regression():
    """[玩家A, 哥布林, 玩家B]: A end_turn → 哥布林自动结算 → 停在 B。"""
    db = _tmp_db()
    a = _mk_char(db, "A", ac=30)     # AC30 + 固定d20=10 → 怪物必未命中
    b = _mk_char(db, "B", ac=30)
    gob = _monster("m1", "哥布林", 15)
    _save_combat(db, [_pc(a, 20), gob, _pc(b, 10)], current_index=0)

    orig = dice.roll_d20
    dice.roll_d20 = lambda advantage=False, disadvantage=False: _FakeRoll(10)
    try:
        flow = combat_flow.advance_and_resolve(CAMP, db_path=db)
    finally:
        dice.roll_d20 = orig

    assert not flow.ended
    assert flow.current is not None and flow.current.cid == str(b.id), \
        f"应停在玩家B，实际 {flow.current}"
    m_events = [e for e in flow.events if e["type"] == "monster_action"]
    assert len(m_events) == 1 and m_events[0]["monster"] == "哥布林"
    assert m_events[0]["hit"] is False              # d20=10+4 < AC30
    # 持久化的回合位置与内存一致
    c2 = store.load_combat(CAMP, db)
    assert cmb.current_combatant(c2).cid == str(b.id)


# ──────────────────────────────────────────────────────────────────────────
# 2. 跳过死者 / 全灭结束
# ──────────────────────────────────────────────────────────────────────────

def test_skip_dead_and_combat_end():
    """哥布林死后 A end_turn 直达 B；全怪物死 → combat_end players_win。"""
    db = _tmp_db()
    a = _mk_char(db, "A")
    b = _mk_char(db, "B")
    gob = _monster("m1", "哥布林", 15)
    gob.hp = 0
    gob.dead = True
    _save_combat(db, [_pc(a, 20), gob, _pc(b, 10)], current_index=0)

    flow = combat_flow.advance_and_resolve(CAMP, db_path=db)
    # 全怪物已死 → 入口 check_combat_end 直接判 players_win
    assert flow.ended
    assert any(e["type"] == "combat_end" and e["outcome"] == "players_win"
               for e in flow.events)


def test_skip_dead_monster_mid_order():
    """两只怪一死一活: 死的被跳过、活的结算，停在 B。"""
    db = _tmp_db()
    a = _mk_char(db, "A", ac=30)
    b = _mk_char(db, "B", ac=30)
    dead_gob = _monster("m1", "死哥布林", 18)
    dead_gob.hp = 0
    dead_gob.dead = True
    live_gob = _monster("m2", "活哥布林", 15)
    _save_combat(db, [_pc(a, 20), dead_gob, live_gob, _pc(b, 10)], current_index=0)

    orig = dice.roll_d20
    dice.roll_d20 = lambda advantage=False, disadvantage=False: _FakeRoll(10)
    try:
        flow = combat_flow.advance_and_resolve(CAMP, db_path=db)
    finally:
        dice.roll_d20 = orig

    assert flow.current is not None and flow.current.cid == str(b.id)
    m_events = [e for e in flow.events if e["type"] == "monster_action"]
    assert [e["monster"] for e in m_events] == ["活哥布林"]   # 死者无回合


# ──────────────────────────────────────────────────────────────────────────
# 3. 死亡豁免时点（R-DMG-017: 以0HP开始回合时掷）
# ──────────────────────────────────────────────────────────────────────────

def test_death_save_at_turn_start():
    """B 倒地(0HP): A end_turn → B 回合开始掷豁免 → 自动结束 → 怪物回合 → 回到 A。"""
    db = _tmp_db()
    a = _mk_char(db, "A", ac=30)
    b = _mk_char(db, "B", hp=10)
    b.hp_current = 0
    store.save_character(b, db)
    pb = _pc(b, 10)
    pb.hp = 0
    gob = _monster("m1", "哥布林", 5)             # 需有活敌人，否则入口即判胜利
    _save_combat(db, [_pc(a, 20), pb, gob], current_index=0)

    orig_die, orig_d20 = dice.roll_die, dice.roll_d20
    dice.roll_die = lambda sides: 12                 # 死亡豁免走 roll_die：≥10 成功
    dice.roll_d20 = lambda advantage=False, disadvantage=False: _FakeRoll(10)  # 攻击 10+4 < AC30
    try:
        flow = combat_flow.advance_and_resolve(CAMP, db_path=db)
    finally:
        dice.roll_die, dice.roll_d20 = orig_die, orig_d20

    ds = [e for e in flow.events if e["type"] == "death_save"]
    assert len(ds) == 1 and ds[0]["player"] == "B" and ds[0]["roll"] == 12
    assert ds[0]["successes"] == 1 and ds[0]["failures"] == 0
    # B 昏迷自动结束回合 → 哥布林回合 → 停回 A（新一轮）
    assert flow.current is not None and flow.current.cid == str(a.id)
    assert any(e["type"] == "round_end" for e in flow.events)
    b2 = store.get_character(b.id, db)
    assert b2.death_successes == 1


def test_death_save_three_failures_then_skipped():
    """连续3次失败 → 死亡；之后该玩家不再有回合（被跳过）。"""
    db = _tmp_db()
    a = _mk_char(db, "A", ac=30)
    b = _mk_char(db, "B", hp=10)
    b.hp_current = 0
    store.save_character(b, db)
    pb = _pc(b, 10)
    pb.hp = 0
    gob = _monster("m1", "哥布林", 5)
    _save_combat(db, [_pc(a, 20), pb, gob], current_index=0)

    orig_die, orig_d20 = dice.roll_die, dice.roll_d20
    dice.roll_die = lambda sides: 3                  # 死亡豁免走 roll_die：<10 失败
    dice.roll_d20 = lambda advantage=False, disadvantage=False: _FakeRoll(10)  # 攻击必未命中
    try:
        combat_flow.advance_and_resolve(CAMP, db_path=db)        # 失败1
        combat_flow.advance_and_resolve(CAMP, db_path=db)        # 失败2
        f3 = combat_flow.advance_and_resolve(CAMP, db_path=db)   # 失败3 → 死亡
        f4 = combat_flow.advance_and_resolve(CAMP, db_path=db)   # B 已死应被跳过
    finally:
        dice.roll_die, dice.roll_d20 = orig_die, orig_d20

    assert any(e["type"] == "death_save" and e["dead"] for e in f3.events)
    b2 = store.get_character(b.id, db)
    assert b2.dead is True
    # 不死锁：推进继续停回 A，且 f4 不再产生 B 的死亡豁免
    assert f4.current is not None and f4.current.cid == str(a.id)
    assert not any(e["type"] == "death_save" for e in f4.events)


def test_no_death_save_on_damage():
    """受伤当下（apply_damage_to_character 首次降至0）不掷死亡豁免。"""
    from aidm.brain.resolvers.apply import apply_damage_to_character
    db = _tmp_db()
    b = _mk_char(db, "B", hp=10)
    res = apply_damage_to_character(b, 10, {"dice": {}, "intent": {}})
    assert b.hp_current == 0 and not b.dead
    assert res.get("death_failures_added", 0) == 0   # 降至0本身不记失败不掷骰
    assert b.death_successes == 0 and b.death_failures == 0


# ──────────────────────────────────────────────────────────────────────────
# 4. 怪物目标选择（DMG 怪物行为）
# ──────────────────────────────────────────────────────────────────────────

def test_target_selection_covers_all_standing():
    """3 玩家站立: 多次选择应覆盖全部；倒地者不被选中。"""
    db = _tmp_db()
    a = _mk_char(db, "A")
    b = _mk_char(db, "B")
    c = _mk_char(db, "C", hp=10)
    c.hp_current = 0                                 # C 倒地
    store.save_character(c, db)
    gob = _monster("m1", "哥布林", 15)
    pcs = [_pc(a, 20), _pc(b, 18), _pc(c, 12)]
    pcs[2].hp = 0
    combat = cmb.Combat(participants=pcs + [gob], initiative_order=pcs + [gob],
                        round=1, current_index=0, active=True)
    chars = {str(x.id): x for x in (a, b, c)}

    picked = {combat_flow.select_target(gob, chars, combat).name
              for _ in range(100)}
    assert picked == {"A", "B"}, f"应只在站立者中选择，实际 {picked}"


def test_target_selection_none_when_all_downed():
    """全员倒地 → select_target 返回 None（战斗由状态机判定结束）。"""
    db = _tmp_db()
    a = _mk_char(db, "A", hp=10)
    a.hp_current = 0
    store.save_character(a, db)
    gob = _monster("m1", "哥布林", 15)
    pa = _pc(a, 20)
    pa.hp = 0
    combat = cmb.Combat(participants=[pa, gob], initiative_order=[pa, gob],
                        round=1, current_index=0, active=True)
    assert combat_flow.select_target(gob, {str(a.id): a}, combat) is None


def test_all_downed_and_stable_ends_combat():
    """全员倒地且已稳定 → 战斗结束 enemies_win（PHB: 被击晕=被击败）。"""
    db = _tmp_db()
    a = _mk_char(db, "A", hp=10)
    a.hp_current = 0
    a.stable = True
    store.save_character(a, db)
    gob = _monster("m1", "哥布林", 15)
    pa = _pc(a, 20)
    pa.hp = 0
    _save_combat(db, [pa, gob], current_index=1)     # 当前哥布林，推进→A回合

    flow = combat_flow.advance_and_resolve(CAMP, db_path=db)
    assert flow.ended
    assert any(e["type"] == "combat_end" and e["outcome"] == "enemies_win"
               for e in flow.events)


# ──────────────────────────────────────────────────────────────────────────
# 5. 序列化往返
# ──────────────────────────────────────────────────────────────────────────

def test_serialization_roundtrip_full_fields():
    """conditions/移动力/group_id/position/fled 全字段存取一致。"""
    db = _tmp_db()
    a = _mk_char(db, "A")
    p = _pc(a, 20)
    p.conditions.add("中毒")
    p.conditions.add("倒地")
    p.conditions.add("力竭")
    p.speed_remaining = 15
    p.position = (3, 4)
    p.dodge_active = True
    gob = _monster("m1", "哥布林", 15)
    gob.group_id = "gob"
    gob.fled = True
    c = cmb.Combat(participants=[p, gob], initiative_order=[p, gob],
                   round=2, current_index=1, active=True)
    c.seconds_elapsed = 12
    store.save_combat(CAMP, c, db)

    c2 = store.load_combat(CAMP, db)
    p2 = c2.initiative_order[0]
    assert p2.conditions.has("中毒") and p2.conditions.has("倒地")
    assert p2.conditions.exhaustion == 1
    assert p2.speed_remaining == 15
    assert p2.position == (3, 4)
    assert p2.dodge_active is True
    g2 = c2.initiative_order[1]
    assert g2.group_id == "gob" and g2.fled is True
    assert c2.seconds_elapsed == 12
    # participants 与 initiative_order 共享同一对象（cid 合并）
    assert c2.participants[0] is c2.initiative_order[0]
    assert c2.participants[1] is c2.initiative_order[1]


def test_old_format_dict_loadable():
    """旧存档 dict（旧字段清单、无 conditions/fled）可加载，缺失字段用默认值。"""
    old = {"cid": "1", "name": "A", "dex_mod": 2, "initiative": 12,
           "side": "player", "is_player": True, "surprised": False,
           "action_used": True, "bonus_action_used": False,
           "reaction_used": False, "free_interaction_used": 0,
           "concentrating_on": None, "hp": 8, "hp_max": 10, "dead": False,
           "attack_bonus": 0, "damage_dice": "", "damage_type": "挥砍"}
    c = store._dict_to_combatant(old)
    assert c.hp == 8 and c.action_used is True
    assert c.fled is False                            # 新字段默认值
    assert c.conditions.to_dict() == {"conditions": [], "exhaustion": 0}
    assert c.group_id is None


# ──────────────────────────────────────────────────────────────────────────
# 7. 动作经济标记（P0 宽松版）
# ──────────────────────────────────────────────────────────────────────────

def test_action_economy_hint_multiplayer():
    """多人局（不自动推进）: 同回合第二次攻击收到 action_exhausted 提示。"""
    import functools as _ft

    from aidm.brain.resolvers.apply import apply_node
    db = _tmp_db()
    a = _mk_char(db, "A")
    gob = _monster("m1", "哥布林", 15)
    _save_combat(db, [_pc(a, 20), gob], current_index=0)

    # 强制多人语义（禁用单人自动推进）；把 apply_node 内部的 store 调用
    # 重定向到测试库（db_path 默认值在 def 时绑定，改 DEFAULT_DB 无效）
    orig_mp = combat_flow._is_multiplayer
    combat_flow._is_multiplayer = lambda cid: True
    patched = {}
    for fname in ("get_character", "save_character", "load_combat",
                  "save_combat", "append_log"):
        patched[fname] = getattr(store, fname)
        setattr(store, fname, _ft.partial(patched[fname], db_path=db))
    try:
        def _state():
            return {"character_id": a.id, "campaign_id": CAMP,
                    "combat": {"active": True},
                    "dice": {"kind": "attack", "damage": 0},
                    "intent": {}, "state_changes": [], "narration": ""}
        s1 = _state()
        out1 = apply_node(s1)
        assert out1.get("turn_hint") == "action_exhausted"    # 动作已用
        c1 = store.load_combat(CAMP)
        assert cmb.current_combatant(c1).action_used is True  # 已标记且未推进回合
        assert c1.current_index == 0
        s2 = _state()
        apply_node(s2)
        assert "动作已用完" in (s2.get("narration") or "")     # 第二次动作 → 提示
    finally:
        combat_flow._is_multiplayer = orig_mp
        for fname, fn in patched.items():
            setattr(store, fname, fn)


# ──────────────────────────────────────────────────────────────────────────
# 附: 单人局自动推进保持旧体验
# ──────────────────────────────────────────────────────────────────────────

def test_solo_post_action_advance():
    """单人局: 行动后自动结束回合并结算怪物回合，narration 追加怪物事件。"""
    db = _tmp_db()
    a = _mk_char(db, "A", ac=30)
    gob = _monster("m1", "哥布林", 15)
    _save_combat(db, [_pc(a, 20), gob], current_index=0)

    orig = dice.roll_d20
    dice.roll_d20 = lambda advantage=False, disadvantage=False: _FakeRoll(10)
    try:
        state = {"narration": "你挥剑攻击。", "dice": {"kind": "attack"}}
        events = combat_flow.post_action_advance(CAMP, a.id, state, db_path=db)
    finally:
        dice.roll_d20 = orig

    assert any(e["type"] == "monster_action" for e in events)
    assert "哥布林回合" in state["narration"]
    assert "你" in state["narration"]                 # 单人视角仍用"你"
    c2 = store.load_combat(CAMP, db)
    assert cmb.current_combatant(c2).cid == str(a.id)  # 停回玩家回合


# ──────────────────────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────────────────────

def main():
    tests = [
        test_deadlock_regression,
        test_skip_dead_and_combat_end,
        test_skip_dead_monster_mid_order,
        test_death_save_at_turn_start,
        test_death_save_three_failures_then_skipped,
        test_no_death_save_on_damage,
        test_target_selection_covers_all_standing,
        test_target_selection_none_when_all_downed,
        test_all_downed_and_stable_ends_combat,
        test_serialization_roundtrip_full_fields,
        test_old_format_dict_loadable,
        test_action_economy_hint_multiplayer,
        test_solo_post_action_advance,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓ {t.__name__}")
            passed += 1
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"  ✗ {t.__name__}: {e}")
            failed += 1
    print(f"\n{'='*50}\n多人战斗状态机测试: {passed} 通过, {failed} 失败\n{'='*50}")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
