# -*- coding: utf-8 -*-
"""B1 探针：遇敌前移 + 场景过滤 + 单次检定（FLOW_ALIGNMENT 矩阵#1/#2/#6，BUG#6）。

断言:
  1. 镇内场景探索 → dice.encounter.suppressed == "safe_scene"，不开战（场景过滤）
  2. 野外场景+强制触发 → dice.encounter.combat_started，combat 快照 active，已持久化（前移）
  3. 野外未触发 → dice.encounter.triggered False，无 combat 键
  4. _resolve_travel 不再含 encounter_result（消除双重检定）
  5. 开战回合 apply：玩家先攻首位 → current_index 保持 0，怪物不行动
  6. 开战回合 apply：怪物先攻首位 → 怪物立即行动（玩家受伤），回合推进给玩家
"""
import dataclasses
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")

from aidm.brain import graph as g
from aidm.brain import exploration as exploration_mod
from aidm.stats import store, models
from aidm.engine import combat as cmb
from aidm.engine import dice as engine_dice


def _mk_campaign(name):
    return store.create_campaign(name)


def _mk_char(camp_id, name="探针战士"):
    ch = models.Character(name=name, race="人类", char_class="战士", level=3,
                          campaign_id=camp_id)
    ch.set_abilities({"str": 16, "dex": 14, "con": 14, "int": 10, "wis": 12, "cha": 10})
    ch.hp_max = 28
    ch.hp_current = 28
    ch.ac = 16
    return store.save_character(ch)


def _set_scene(camp_id, location, environment=""):
    sc = store.get_scene(camp_id)
    if sc is None:
        sc = models.Scene(campaign_id=camp_id)
    sc.location = location
    sc.environment = environment
    store.save_scene(sc)


def _base_state(camp_id, cid):
    return {"player_input": "我环顾四周", "campaign_id": camp_id, "character_id": cid,
            "hitl": False, "intent": {}, "evidence": [], "verification": {},
            "confirmed": False, "dice": {}, "narration": "", "state_changes": [],
            "scene_update": "", "action_options": [],
            "combat": {"active": False}, "error": "", "summary": ""}


@dataclasses.dataclass
class _FakeEnc:
    triggered: bool
    roll: int = 5
    threshold: int = 18

    def __init__(self, triggered):
        self.triggered = triggered
        self.roll = 19 if triggered else 5
        self.threshold = 18


def main():
    orig_check = exploration_mod.random_encounter_check
    passed = []

    # ── 用例1：镇内场景过滤 ────────────────────────────────────────────
    camp = _mk_campaign("探针_遇敌_镇内")
    ch = _mk_char(camp.id)
    _set_scene(camp.id, "灰羽镇·铜壶酒馆", "热闹的酒馆内")
    st = _base_state(camp.id, ch.id)
    out = g._with_encounter(st, ch, {"kind": "explore"})
    enc = out["dice"].get("encounter", {})
    assert enc.get("suppressed") == "safe_scene" and not enc.get("triggered"), f"用例1失败: {enc}"
    assert "combat" not in out, "用例1失败: 镇内不应开战"
    passed.append("1.镇内场景过滤(safe_scene)")

    # ── 用例2：野外强制触发 → 前移开战 ────────────────────────────────
    camp2 = _mk_campaign("探针_遇敌_野外")
    ch2 = _mk_char(camp2.id)
    _set_scene(camp2.id, "幽暗森林小径", "密林深处，雾气弥漫")
    exploration_mod.random_encounter_check = lambda threshold=18: _FakeEnc(True)
    # B4 新增遭遇类型骰：强制 d20=5 → combat 类型（选怪骰取 1 号位）
    orig_roll = engine_dice.roll_die
    engine_dice.roll_die = lambda n: 5 if n == 20 else 1
    try:
        st2 = _base_state(camp2.id, ch2.id)
        out2 = g._with_encounter(st2, ch2, {"kind": "travel"})
        enc2 = out2["dice"].get("encounter", {})
        assert enc2.get("combat_started") is True, f"用例2失败: {enc2}"
        assert enc2.get("enemy_count") >= 1 and enc2.get("enemy_name"), f"用例2失败: {enc2}"
        assert out2.get("combat", {}).get("active") is True, "用例2失败: combat 快照未激活"
        persisted = store.load_combat(camp2.id)
        assert persisted.active is True, "用例2失败: 战斗未持久化"
        assert len(enc2.get("initiative_order", [])) >= 2, f"用例2失败: {enc2}"
    finally:
        exploration_mod.random_encounter_check = orig_check
        engine_dice.roll_die = orig_roll
    passed.append("2.野外遇敌前移开战+持久化")

    # ── 用例3：野外未触发 ──────────────────────────────────────────────
    exploration_mod.random_encounter_check = lambda threshold=18: _FakeEnc(False)
    try:
        camp3 = _mk_campaign("探针_遇敌_未触发")
        ch3 = _mk_char(camp3.id)
        _set_scene(camp3.id, "荒野山道", "")
        st3 = _base_state(camp3.id, ch3.id)
        out3 = g._with_encounter(st3, ch3, {"kind": "explore"})
        enc3 = out3["dice"].get("encounter", {})
        assert enc3.get("triggered") is False and not enc3.get("combat_started"), f"用例3失败: {enc3}"
        assert "combat" not in out3, "用例3失败: 未触发不应有 combat"
    finally:
        exploration_mod.random_encounter_check = orig_check
    passed.append("3.野外未触发不开战")

    # ── 用例4：travel 单检定（无 encounter_result）─────────────────────
    st4 = _base_state(camp2.id, ch2.id)
    dice4 = g._resolve_travel(st4, ch2, {"pace": "中速", "terrain": "森林"})
    assert "encounter_result" not in dice4, "用例4失败: travel 仍含 encounter_result（双重检定）"
    assert dice4.get("kind") == "travel", f"用例4失败: {dice4.get('kind')}"
    passed.append("4.travel消除双重检定")

    # ── 用例5：开战回合玩家先攻首位 → 不 advance，怪物不动 ─────────────
    camp5 = _mk_campaign("探针_开战_玩家先")
    ch5 = _mk_char(camp5.id)
    pc = cmb.Combatant(cid=str(ch5.id), name=ch5.name, dex_mod=2, side="player",
                       is_player=True, hp=28, hp_max=28)
    mo = cmb.Combatant(cid="e0", name="探针狼", dex_mod=0, side="enemy",
                       is_player=False, hp=10, hp_max=10,
                       attack_bonus=20, damage_dice="1d4+1", damage_type="挥砍")
    pc.initiative = 20
    mo.initiative = 5
    combat = cmb.Combat()
    combat.participants = [pc, mo]
    combat.initiative_order = [pc, mo]
    combat.round = 1
    combat.current_index = 0
    combat.active = True
    store.save_combat(camp5.id, combat)
    st5 = _base_state(camp5.id, ch5.id)
    st5["dice"] = {"kind": "explore",
                   "encounter": {"triggered": True, "combat_started": True,
                                 "enemy_name": "探针狼", "enemy_count": 1}}
    st5["combat"] = {"active": True, "round": 1, "current_index": 0,
                     "combatants": [{"name": pc.name, "cid": pc.cid},
                                    {"name": mo.name, "cid": mo.cid}]}
    g.apply_node(st5)
    after5 = store.load_combat(camp5.id)
    ch5_after = store.get_character(ch5.id)
    assert after5.current_index == 0, f"用例5失败: current_index={after5.current_index}（首位玩家回合被跳过）"
    assert ch5_after.hp_current == 28, f"用例5失败: 玩家受伤 {ch5_after.hp_current}/28（玩家先攻怪物不应行动）"
    passed.append("5.开战回合玩家先攻不advance")

    # ── 用例6：开战回合怪物先攻首位 → 怪物立即行动 ─────────────────────
    camp6 = _mk_campaign("探针_开战_怪先")
    ch6 = _mk_char(camp6.id)
    ch6.ac = 10  # 怪物 attack_bonus+20 必中
    store.save_character(ch6)
    pc6 = cmb.Combatant(cid=str(ch6.id), name=ch6.name, dex_mod=2, side="player",
                        is_player=True, hp=28, hp_max=28)
    mo6 = cmb.Combatant(cid="e0", name="探针狼王", dex_mod=5, side="enemy",
                        is_player=False, hp=10, hp_max=10,
                        attack_bonus=20, damage_dice="1d4+1", damage_type="挥砍")
    pc6.initiative = 5
    mo6.initiative = 20
    combat6 = cmb.Combat()
    combat6.participants = [pc6, mo6]
    combat6.initiative_order = [mo6, pc6]
    combat6.round = 1
    combat6.current_index = 0
    combat6.active = True
    store.save_combat(camp6.id, combat6)
    st6 = _base_state(camp6.id, ch6.id)
    st6["dice"] = {"kind": "explore",
                   "encounter": {"triggered": True, "combat_started": True,
                                 "enemy_name": "探针狼王", "enemy_count": 1}}
    st6["combat"] = {"active": True, "round": 1, "current_index": 0,
                     "combatants": [{"name": mo6.name, "cid": mo6.cid},
                                    {"name": pc6.name, "cid": pc6.cid}]}
    g.apply_node(st6)
    ch6_after = store.get_character(ch6.id)
    after6 = store.load_combat(camp6.id)
    assert ch6_after.hp_current < 28, f"用例6失败: 先攻怪物未行动 {ch6_after.hp_current}/28"
    cur6 = cmb.current_combatant(after6)
    assert cur6 is not None and cur6.is_player, "用例6失败: 怪物行动后应轮到玩家"
    passed.append("6.开战回合先攻怪物立即行动")

    print("\n".join(f"  PASS {p}" for p in passed))
    print(f"\nB1 探针全部通过（{len(passed)}/6）")


if __name__ == "__main__":
    main()
