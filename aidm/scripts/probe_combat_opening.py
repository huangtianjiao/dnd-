# -*- coding: utf-8 -*-
"""B3 探针：战斗开场突袭+先攻叙述对齐（FLOW_ALIGNMENT 矩阵#7）。

断言:
  1. 显式 surprise="player" → 玩家 Combatant.surprised=True，dice.surprise 输出，
     initiative_order 玩家条目带 surprised 标记
  2. 显式 surprise="none" → 无突袭标记
  3. 自动判定：隐匿高→玩家被突袭；隐匿低→无突袭（monkeypatch roll_die）
  4. 遇敌联动：_with_encounter 触发开战后 dice.encounter 含 surprise 与 initiative_order
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
    ch = models.Character(name="探针武僧", race="人类", char_class="战士", level=3,
                          campaign_id=camp_id)
    ch.set_abilities({"str": 16, "dex": 14, "con": 14, "int": 10, "wis": 12, "cha": 10})
    ch.hp_max = 28
    ch.hp_current = 28
    ch.ac = 16
    return store.save_character(ch)


def _start(camp_id, ch, it_extra=None):
    it = {"action_type": "start_combat",
          "enemies": [{"name": "探针兽人", "dex_mod": 1, "hp_max": 15}]}
    it.update(it_extra or {})
    state = {"character_id": ch.id, "campaign_id": camp_id}
    return g._resolve_start_combat(state, ch, it)


def main():
    passed = []

    # ── 用例1：显式玩家被突袭 ─────────────────────────────────────────
    camp = store.create_campaign("探针_开场_显式突袭")
    ch = _mk_char(camp.id)
    r = _start(camp.id, ch, {"surprise": "player"})
    sp = r["dice"].get("surprise", {})
    assert sp.get("surprised_side") == "player", f"用例1a失败: {sp}"
    order = r["dice"].get("initiative_order", [])
    pc_view = next(c for c in order if c["side"] == "player")
    assert pc_view.get("surprised") is True, f"用例1b失败: {pc_view}"
    mob_view = next(c for c in order if c["side"] == "enemy")
    assert mob_view.get("surprised") is False, f"用例1c失败: {mob_view}"
    # 持久化 Combatant 也带 surprised
    persisted = store.load_combat(camp.id)
    pc = next(c for c in persisted.participants if c.is_player)
    assert pc.surprised is True, "用例1d失败: 持久化未带 surprised"
    passed.append("1.显式玩家突袭(标记+输出+持久化)")

    # ── 用例2：显式无突袭 ─────────────────────────────────────────────
    camp2 = store.create_campaign("探针_开场_无突袭")
    ch2 = _mk_char(camp2.id)
    r2 = _start(camp2.id, ch2, {"surprise": "none"})
    sp2 = r2["dice"].get("surprise", {})
    assert sp2.get("surprised_side") is None, f"用例2失败: {sp2}"
    order2 = r2["dice"].get("initiative_order", [])
    assert all(not c.get("surprised") for c in order2), f"用例2失败: {order2}"
    passed.append("2.显式无突袭")

    # ── 用例3：自动判定（monkeypatch roll_die 控制隐匿骰）──────────────
    orig_roll = engine_dice.roll_die
    try:
        # 隐匿 20+dex1=21 ≥ 被动察觉 11 → 玩家被突袭
        engine_dice.roll_die = lambda n: 20
        camp3 = store.create_campaign("探针_开场_自动高")
        ch3 = _mk_char(camp3.id)
        r3 = _start(camp3.id, ch3)
        sp3 = r3["dice"].get("surprise", {})
        assert sp3.get("surprised_side") == "player", f"用例3a失败: {sp3}"
        assert "隐匿" in sp3.get("note", ""), f"用例3a失败: {sp3}"

        # 隐匿 1+1=2 < 11 → 无突袭
        engine_dice.roll_die = lambda n: 1
        camp4 = store.create_campaign("探针_开场_自动低")
        ch4 = _mk_char(camp4.id)
        r4 = _start(camp4.id, ch4)
        sp4 = r4["dice"].get("surprise", {})
        assert sp4.get("surprised_side") is None, f"用例3b失败: {sp4}"
        assert "互相察觉" in sp4.get("note", ""), f"用例3b失败: {sp4}"
    finally:
        engine_dice.roll_die = orig_roll
    passed.append("3.自动突袭判定(隐匿vs被动察觉)")

    # ── 用例4：遇敌联动（dice.encounter 含 surprise 与先攻序列）────────
    import dataclasses as _dc

    @_dc.dataclass
    class _Enc:
        triggered: bool = True
        roll: int = 19
        threshold: int = 18

    orig_check = exploration_mod.random_encounter_check
    orig_roll2 = engine_dice.roll_die
    exploration_mod.random_encounter_check = lambda threshold=18: _Enc()
    # B4 新增遭遇类型骰：强制 d20=5 → combat 类型（选怪/突袭骰取 1）
    engine_dice.roll_die = lambda n: 5 if n == 20 else 1
    try:
        camp5 = store.create_campaign("探针_开场_遇敌")
        ch5 = _mk_char(camp5.id)
        sc = store.get_scene(camp5.id)
        if sc is None:
            sc = models.Scene(campaign_id=camp5.id)
        sc.location = "幽暗森林"
        store.save_scene(sc)
        st5 = {"player_input": "我继续前进", "campaign_id": camp5.id,
               "character_id": ch5.id, "combat": {"active": False}}
        out5 = g._with_encounter(st5, ch5, {"kind": "travel"})
        enc5 = out5["dice"].get("encounter", {})
        assert enc5.get("combat_started") is True, f"用例4a失败: {enc5}"
        assert "surprise" in enc5, f"用例4b失败: encounter缺surprise {list(enc5)}"
        assert len(enc5.get("initiative_order", [])) >= 2, f"用例4c失败: {enc5}"
        assert all("surprised" in c for c in enc5["initiative_order"]), f"用例4d失败: {enc5}"
    finally:
        exploration_mod.random_encounter_check = orig_check
        engine_dice.roll_die = orig_roll2
    passed.append("4.遇敌联动(encounter含surprise+先攻)")

    print("\n".join(f"  PASS {p}" for p in passed))
    print(f"\nB3 探针全部通过（{len(passed)}/4）")


if __name__ == "__main__":
    main()
