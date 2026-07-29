# -*- coding: utf-8 -*-
"""B4 探针：遭遇时钟 + 非战斗遭遇 + 时间推进 + 浴血叙述（矩阵#4/#5/#8/#12）。

断言:
  1. travel 推进游戏内时间 60 分钟（world_flags.game_minutes），dice.time 含 day/clock
  2. 遭遇时钟：4 游戏小时内第 2 次探索 → encounter.suppressed=="clock"；拨钟后放行
  3. 非战斗遭遇（类型骰 15→environment）：encounter_type 正确、不开战、含 prompt_hint
  4. 战斗遭遇类型（类型骰 5→combat）：正常开战
  5. 浴血叙述：敌方半血时 narrate prompt 含【伤势叙述】
  6. 长休推进 480 分钟
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")

from aidm.brain import graph as g
from aidm.brain import exploration as exploration_mod
from aidm.engine import dice as engine_dice
from aidm.stats import store, models


def _mk_char(camp_id):
    ch = models.Character(name="探针游侠", race="人类", char_class="游侠", level=3,
                          campaign_id=camp_id)
    ch.set_abilities({"str": 14, "dex": 16, "con": 14, "int": 10, "wis": 14, "cha": 10})
    ch.hp_max = 26
    ch.hp_current = 26
    ch.ac = 14
    return store.save_character(ch)


def _set_wild_scene(camp_id):
    sc = store.get_scene(camp_id)
    if sc is None:
        sc = models.Scene(campaign_id=camp_id)
    sc.location = "幽暗森林小径"
    sc.environment = "密林"
    store.save_scene(sc)


def _flags(camp_id):
    return store.get_campaign(camp_id).world_flags


def _st(camp_id, ch):
    return {"player_input": "我沿小径前进", "campaign_id": camp_id, "character_id": ch.id,
            "hitl": False, "intent": {}, "evidence": [], "verification": {},
            "confirmed": False, "dice": {}, "narration": "", "state_changes": [],
            "scene_update": "", "action_options": [],
            "combat": {"active": False}, "error": "", "summary": ""}


import dataclasses as _dc


@_dc.dataclass
class _EncNo:
    triggered: bool = False
    roll: int = 5
    threshold: int = 18


@_dc.dataclass
class _EncYes:
    triggered: bool = True
    roll: int = 19
    threshold: int = 18


def main():
    orig_check = exploration_mod.random_encounter_check
    orig_roll = engine_dice.roll_die
    orig_chat = g.llm.chat
    passed = []

    # ── 用例1+2：时间推进 + 遭遇时钟 ──────────────────────────────────
    camp = store.create_campaign("探针_时钟_推进")
    ch = _mk_char(camp.id)
    _set_wild_scene(camp.id)
    exploration_mod.random_encounter_check = lambda threshold=18: _EncNo()
    try:
        out1 = g._with_encounter(_st(camp.id, ch), ch, {"kind": "travel"})
        t1 = out1["dice"].get("time", {})
        assert t1.get("advanced") == 60 and t1.get("minutes_after") == 540, f"用例1a失败: {t1}"
        assert t1.get("day") == 1 and t1.get("clock") == "上午", f"用例1b失败: {t1}"  # 540min=09:00
        assert _flags(camp.id)["game_minutes"] == 540, "用例1c失败: world_flags 未写回"
        # 第一次到点已检定（encounter_last_check_min 记录）；第二次仅 30 分钟后 → clock 抑制
        out2 = g._with_encounter(_st(camp.id, ch), ch, {"kind": "explore"})
        enc2 = out2["dice"].get("encounter", {})
        assert enc2.get("suppressed") == "clock" and enc2.get("next_check_in_min", 0) > 0, \
            f"用例2a失败: {enc2}"
        # 拨钟：把上次检定时间拨回 240 分钟前 → 放行检定
        c = store.get_campaign(camp.id)
        fl = c.world_flags
        fl["encounter_last_check_min"] = int(fl["game_minutes"]) - 240
        c.set_world_flags(fl)
        store.save_campaign(c)
        out3 = g._with_encounter(_st(camp.id, ch), ch, {"kind": "explore"})
        enc3 = out3["dice"].get("encounter", {})
        assert enc3.get("suppressed") != "clock", f"用例2b失败: {enc3}"
    finally:
        exploration_mod.random_encounter_check = orig_check
    passed.append("1+2.时间推进+遭遇时钟(抑制/放行)")

    # ── 用例3：非战斗遭遇（environment）───────────────────────────────
    camp3 = store.create_campaign("探针_遭遇_非战斗")
    ch3 = _mk_char(camp3.id)
    _set_wild_scene(camp3.id)
    exploration_mod.random_encounter_check = lambda threshold=18: _EncYes()
    engine_dice.roll_die = lambda n: 15 if n == 20 else 1
    try:
        out4 = g._with_encounter(_st(camp3.id, ch3), ch3, {"kind": "travel"})
        enc4 = out4["dice"].get("encounter", {})
        assert enc4.get("triggered") is True and enc4.get("encounter_type") == "environment", \
            f"用例3a失败: {enc4}"
        assert enc4.get("combat_started") is False, f"用例3b失败: {enc4}"
        assert enc4.get("prompt_hint"), f"用例3c失败: {enc4}"
        assert "combat" not in out4, "用例3d失败: 非战斗遭遇不应开战"
    finally:
        exploration_mod.random_encounter_check = orig_check
        engine_dice.roll_die = orig_roll
    passed.append("3.非战斗遭遇(environment不开战)")

    # ── 用例4：战斗遭遇类型 → 正常开战 ────────────────────────────────
    camp4 = store.create_campaign("探针_遭遇_战斗型")
    ch4 = _mk_char(camp4.id)
    _set_wild_scene(camp4.id)
    exploration_mod.random_encounter_check = lambda threshold=18: _EncYes()
    engine_dice.roll_die = lambda n: 5 if n == 20 else 1  # 类型=combat；选怪取第1只
    try:
        out5 = g._with_encounter(_st(camp4.id, ch4), ch4, {"kind": "travel"})
        enc5 = out5["dice"].get("encounter", {})
        assert enc5.get("encounter_type") == "combat" and enc5.get("combat_started") is True, \
            f"用例4a失败: {enc5}"
        assert out5.get("combat", {}).get("active") is True, "用例4b失败: 未开战"
    finally:
        exploration_mod.random_encounter_check = orig_check
        engine_dice.roll_die = orig_roll
    passed.append("4.战斗遭遇类型正常开战")

    # ── 用例5：浴血叙述提示（narrate prompt 注入）─────────────────────
    captured = {}

    def _fake_chat(system, prompt, temperature=0.4):
        captured["prompt"] = prompt
        return '{"narration":"测试叙述","state_changes":[],"scene_update":"","action_options":[]}'

    camp5 = store.create_campaign("探针_浴血")
    ch5 = _mk_char(camp5.id)
    _set_wild_scene(camp5.id)
    g.llm.chat = _fake_chat
    try:
        st5 = _st(camp5.id, ch5)
        st5["combat"] = {"active": True, "round": 2, "current_index": 0,
                         "combatants": [
                             {"name": ch5.name, "cid": str(ch5.id), "side": "player",
                              "hp": 20, "hp_max": 26, "dead": False},
                             {"name": "半血兽人", "cid": "e0", "side": "enemy",
                              "hp": 5, "hp_max": 15, "dead": False},
                             {"name": "满血兽人", "cid": "e1", "side": "enemy",
                              "hp": 15, "hp_max": 15, "dead": False}]}
        st5["dice"] = {"kind": "other"}
        g.narrate(st5)
        p = captured.get("prompt", "")
        assert "伤势叙述" in p and "半血兽人" in p, f"用例5a失败: prompt无浴血提示"
        assert "满血兽人" not in p.split("伤势叙述")[-1][:80], f"用例5b失败: 满血不应列入"
    finally:
        g.llm.chat = orig_chat
    passed.append("5.浴血叙述prompt注入")

    # ── 用例6：长休推进 480 分钟 ──────────────────────────────────────
    camp6 = store.create_campaign("探针_长休_时间")
    ch6 = _mk_char(camp6.id)
    before = int(_flags(camp6.id).get("game_minutes", 480))
    st6 = _st(camp6.id, ch6)
    st6["player_input"] = "我要长休"
    st6["intent"] = {"action_type": "rest", "rest_type": "long"}
    r6 = g.resolve(st6)
    t6 = r6["dice"].get("time", {})
    assert t6.get("advanced") == 480, f"用例6a失败: {t6}"
    assert int(_flags(camp6.id)["game_minutes"]) == before + 480, "用例6b失败: 未写回"
    passed.append("6.长休推进480分钟")

    print("\n".join(f"  PASS {p}" for p in passed))
    print(f"\nB4 探针全部通过（{len(passed)}/6）")


if __name__ == "__main__":
    main()
