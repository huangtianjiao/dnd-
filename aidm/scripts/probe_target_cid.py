# -*- coding: utf-8 -*-
"""B2 探针：攻击目标确定性 target_cid（FLOW_ALIGNMENT 矩阵#3，BUG#5）。

断言:
  1. classify 目标匹配：name精确/子串/唯一敌人自动 → target_cid
  2. resolve 预判：命中且伤害≥目标HP → target_killed；不足 → False；治疗法术不预判
  3. apply 确定性扣血：按 target_cid 扣目标，LLM 错目标的 state_changes 被跳过
  4. apply 防双扣：LLM 正确复述同目标 → 只扣一次
  5. apply 治疗不误伤：cast 治疗不扣敌方血（含无 target_cid 时兜底也不触发）
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")

from aidm.agents import director
from aidm.brain import graph as g
from aidm.stats import store, models
from aidm.engine import combat as cmb


def _mk_campaign(name):
    return store.create_campaign(name)


def _mk_char(camp_id):
    ch = models.Character(name="探针游侠", race="人类", char_class="战士", level=3,
                          campaign_id=camp_id)
    ch.set_abilities({"str": 16, "dex": 14, "con": 14, "int": 10, "wis": 12, "cha": 10})
    ch.hp_max = 28
    ch.hp_current = 28
    ch.ac = 16
    return store.save_character(ch)


def _mk_combat(camp_id, ch, enemies):
    """enemies: [(cid, name, hp)]；返回持久化后的 Combat。"""
    pc = cmb.Combatant(cid=str(ch.id), name=ch.name, dex_mod=2, side="player",
                       is_player=True, hp=ch.hp_current, hp_max=ch.hp_max)
    combatants = [pc]
    for ecid, ename, ehp in enemies:
        e = cmb.Combatant(cid=ecid, name=ename, dex_mod=0, side="enemy",
                          is_player=False, hp=ehp, hp_max=ehp,
                          attack_bonus=4, damage_dice="1d6+2", damage_type="挥砍")
        combatants.append(e)
    pc.initiative = 20
    for i, c in enumerate(combatants[1:]):
        c.initiative = 10 - i
    combat = cmb.Combat()
    combat.participants = combatants
    combat.initiative_order = sorted(combatants, key=lambda c: -c.initiative)
    combat.round = 1
    combat.current_index = 0
    combat.active = True
    store.save_combat(camp_id, combat)
    return combat


def _combat_state_view(combat):
    return {"active": True, "round": combat.round, "current_index": 0,
            "combatants": [{"name": c.name, "init": c.initiative, "side": c.side,
                            "cid": c.cid, "hp": c.hp, "hp_max": c.hp_max,
                            "dead": c.dead}
                           for c in combat.initiative_order]}


def _base_state(camp_id, ch, combat):
    return {"player_input": "我攻击", "campaign_id": camp_id, "character_id": ch.id,
            "hitl": False, "intent": {}, "evidence": [], "verification": {},
            "confirmed": False, "dice": {}, "narration": "", "state_changes": [],
            "scene_update": "", "action_options": [],
            "combat": _combat_state_view(combat), "error": "", "summary": ""}


def _apply_state(camp_id, ch, dice, state_changes):
    st = _base_state(camp_id, ch, store.load_combat(camp_id))
    st["dice"] = dice
    st["state_changes"] = state_changes
    return st


def main():
    passed = []

    # ── 用例1：classify 目标匹配 ───────────────────────────────────────
    camp = _mk_campaign("探针_目标_匹配")
    ch = _mk_char(camp.id)
    combat = _mk_combat(camp.id, ch, [("e0", "哥布林甲", 7), ("e1", "哥布林乙", 9)])
    st = _base_state(camp.id, ch, combat)

    it1 = {"action_type": "attack", "target_name": "哥布林乙"}
    director._resolve_target_cid(it1, st)
    assert it1.get("target_cid") == "e1", f"用例1a失败: {it1}"

    it2 = {"action_type": "attack", "target_name": "哥布林甲"}  # 精确
    director._resolve_target_cid(it2, st)
    assert it2.get("target_cid") == "e0", f"用例1b失败: {it2}"

    it3 = {"action_type": "attack", "target_name": "布林乙"}  # 子串互含
    director._resolve_target_cid(it3, st)
    assert it3.get("target_cid") == "e1", f"用例1c失败: {it3}"

    # 唯一存活敌人自动匹配
    combat.initiative_order[1].dead = True  # e0 死亡（视图层模拟）
    st_single = _base_state(camp.id, ch, combat)
    st_single["combat"]["combatants"][1]["dead"] = True
    st_single["combat"]["combatants"][1]["hp"] = 0
    it4 = {"action_type": "attack", "target_name": ""}
    director._resolve_target_cid(it4, st_single)
    assert it4.get("target_cid") == "e1" and it4.get("target_name") == "哥布林乙", f"用例1d失败: {it4}"

    # 非战斗中不填
    it5 = {"action_type": "attack", "target_name": "哥布林"}
    st_nc = _base_state(camp.id, ch, combat)
    st_nc["combat"] = {"active": False}
    director._resolve_target_cid(it5, st_nc)
    assert "target_cid" not in it5, f"用例1e失败: {it5}"
    passed.append("1.classify目标匹配(精确/子串/唯一/非战斗)")

    # ── 用例2：resolve 预判击杀/未击杀/治疗不预判 ─────────────────────
    st2 = _base_state(camp.id, ch, store.load_combat(camp.id))
    st2["intent"] = {"action_type": "attack", "target_cid": "e1"}
    r = g._with_target_outcome(st2, {"kind": "attack", "hit": True, "damage": 10, "d20": 15})
    d = r["dice"]
    assert d.get("target_killed") is True and d.get("target_hp_before") == 9, f"用例2a失败: {d}"
    r2 = g._with_target_outcome(st2, {"kind": "attack", "hit": True, "damage": 5, "d20": 15})
    assert r2["dice"].get("target_killed") is False, f"用例2b失败: {r2['dice']}"
    r3 = g._with_target_outcome(st2, {"kind": "attack", "hit": False, "damage": 0, "d20": 3})
    assert "target_killed" not in r3["dice"], f"用例2c失败: {r3['dice']}"
    st2h = _base_state(camp.id, ch, store.load_combat(camp.id))
    st2h["intent"] = {"action_type": "cast", "target_cid": "e0"}
    r4 = g._with_target_outcome(st2h, {"kind": "cast", "hit": True, "damage": 8,
                                       "damage_type": "治疗"})
    assert "target_killed" not in r4["dice"], f"用例2d失败: 治疗法术不应预判"
    passed.append("2.resolve预判(击杀/未击杀/未命中/治疗)")

    # ── 用例3：apply 确定性扣血 + LLM 错目标被跳过 ────────────────────
    camp3 = _mk_campaign("探针_目标_扣血")
    ch3 = _mk_char(camp3.id)
    _mk_combat(camp3.id, ch3, [("e0", "哥布林甲", 20), ("e1", "哥布林乙", 9)])
    dice3 = {"kind": "attack", "hit": True, "damage": 10, "d20": 15,
             "target_cid": "e1", "target_name": "哥布林乙",
             "target_hp_before": 9, "target_killed": True}
    # LLM 错误地把伤害复述到哥布林甲（BUG#5 场景）
    sc3 = [{"target": "哥布林甲", "field": "hp", "delta": -10}]
    g.apply_node(_apply_state(camp3.id, ch3, dice3, sc3))
    after3 = store.load_combat(camp3.id)
    e0 = next(c for c in after3.participants if c.cid == "e0")
    e1 = next(c for c in after3.participants if c.cid == "e1")
    assert e1.hp == 0 and e1.dead, f"用例3失败: e1={e1.hp}/{e1.dead}"
    assert e0.hp == 20, f"用例3失败: LLM错目标被错误应用 e0={e0.hp}"
    passed.append("3.apply确定性扣血+LLM错目标跳过")

    # ── 用例4：防双扣（LLM 正确复述同目标）────────────────────────────
    camp4 = _mk_campaign("探针_目标_双扣")
    ch4 = _mk_char(camp4.id)
    _mk_combat(camp4.id, ch4, [("e0", "兽人", 20)])
    dice4 = {"kind": "attack", "hit": True, "damage": 6, "d20": 15,
             "target_cid": "e0", "target_name": "兽人",
             "target_hp_before": 20, "target_killed": False}
    sc4 = [{"target": "兽人", "field": "hp", "delta": -6}]
    g.apply_node(_apply_state(camp4.id, ch4, dice4, sc4))
    after4 = store.load_combat(camp4.id)
    e0_4 = next(c for c in after4.participants if c.cid == "e0")
    assert e0_4.hp == 14, f"用例4失败: 双扣或未扣 e0={e0_4.hp}（应20-6=14）"
    passed.append("4.apply防双扣")

    # ── 用例5：治疗法术不误伤（有/无 target_cid 都不扣敌方）────────────
    camp5 = _mk_campaign("探针_目标_治疗")
    ch5 = _mk_char(camp5.id)
    ch5.hp_current = 10  # 受伤待治疗
    ch5.ac = 30          # 怪物 +4 必不命中（隔离 3e 怪物回合干扰）
    store.save_character(ch5)
    _mk_combat(camp5.id, ch5, [("e0", "骷髅兵", 13)])
    dice5 = {"kind": "cast", "hit": True, "damage": 8, "damage_type": "治疗",
             "spell_name": "疗伤术", "target_cid": "e0"}
    g.apply_node(_apply_state(camp5.id, ch5, dice5, []))
    after5 = store.load_combat(camp5.id)
    e0_5 = next(c for c in after5.participants if c.cid == "e0")
    ch5_after = store.get_character(ch5.id)
    assert e0_5.hp == 13, f"用例5a失败: 治疗误伤敌方 e0={e0_5.hp}"
    assert ch5_after.hp_current == 18, f"用例5a失败: 自疗未生效 {ch5_after.hp_current}"
    # 无 target_cid + state_changes 空 → 兜底也不应触发
    ch5.hp_current = 10
    store.save_character(ch5)
    dice5b = {"kind": "cast", "hit": True, "damage": 8, "damage_type": "治疗",
              "spell_name": "疗伤术"}
    g.apply_node(_apply_state(camp5.id, ch5, dice5b, []))
    after5b = store.load_combat(camp5.id)
    e0_5b = next(c for c in after5b.participants if c.cid == "e0")
    assert e0_5b.hp == 13, f"用例5b失败: 兜底误伤敌方 e0={e0_5b.hp}"
    passed.append("5.治疗法术不误伤(确定性+兜底)")

    print("\n".join(f"  PASS {p}" for p in passed))
    print(f"\nB2 探针全部通过（{len(passed)}/5）")


if __name__ == "__main__":
    main()
