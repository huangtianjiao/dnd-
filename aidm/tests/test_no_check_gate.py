"""免检定门槛单元测试 — DMG「骰子的角色」：仅结果不确定且失败有实质后果才掷骰。

验证规则点:
  DMG 骰子的角色 — needs_check=false 的技能/社交/旅行动作自动成功，不掷 d20
  R-DM-037 导航检定 — 沿已知道路/有向导旅行免导航检定
  DMG 运作交涉 — 友好/冷漠 NPC 合理请求免魅力检定；敌对 NPC 不免（误判防护）
  对抗动作（hide 等）不受 needs_check 影响，总是掷骰

运行:
  PYTHONPATH=src python -m pytest tests/test_no_check_gate.py -v
"""

from __future__ import annotations

import json
import os
import sys
import tempfile


def _setup_test_db():
    tmpdir = tempfile.mkdtemp(prefix="aidm_test_")
    db_path = f"sqlite:///{tmpdir}/test.db"
    from aidm.stats import store
    orig_default = store.DEFAULT_DB
    orig_engines = store._engines.copy()
    store.DEFAULT_DB = db_path
    store._engines.clear()
    store.get_engine(db_path)
    return db_path, orig_default, orig_engines, store


def _teardown_test_db(orig_default, orig_engines, store):
    store.DEFAULT_DB = orig_default
    store._engines.clear()
    store._engines.update(orig_engines)


def _make_char(char_class="战士", level=5):
    from aidm.stats import models
    ch = models.Character(name="免检定测试者", race="人类", char_class=char_class, level=level)
    ch.hp_max = 30
    ch.hp_current = 30
    return ch


# ──────────────────────────────────────────────────────────────────────────
# 技能类动作：needs_check=false → 自动成功不掷骰；缺省 → 照常掷骰
# ──────────────────────────────────────────────────────────────────────────

def test_ability_check_auto_success_when_no_check_needed():
    """needs_check=false 的属性检定 → auto_success，无 d20。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from aidm.brain.graph import resolve

        ch = store.save_character(_make_char())
        state = {"intent": {"action_type": "ability_check", "skill": "运动",
                            "needs_check": False},
                 "character_id": ch.id, "player_input": "我爬上结实的梯子"}
        out = resolve(state)
        d = out["dice"]
        assert d.get("auto_success") is True and d.get("success") is True
        assert "d20" not in d and "check_total" not in d
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


def test_ability_check_still_rolls_by_default():
    """未给 needs_check（或为 true）→ 照常掷骰（有 d20/check_total）。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from aidm.brain.graph import resolve

        ch = store.save_character(_make_char())
        for it in ({"action_type": "ability_check", "skill": "运动", "dc": 15},
                   {"action_type": "ability_check", "skill": "运动", "dc": 15,
                    "needs_check": True}):
            out = resolve({"intent": it, "character_id": ch.id,
                           "player_input": "我攀爬悬崖"})
            d = out["dice"]
            assert 1 <= d.get("d20", 0) <= 20 and "check_total" in d
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


def test_hide_ignores_needs_check():
    """对抗动作（hide）不受 needs_check=false 影响，总是掷骰。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from aidm.brain.graph import resolve

        ch = store.save_character(_make_char())
        out = resolve({"intent": {"action_type": "hide", "needs_check": False},
                       "character_id": ch.id, "player_input": "我躲起来"})
        d = out["dice"]
        assert d.get("kind") == "hide" and 1 <= d.get("d20", 0) <= 20
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


# ──────────────────────────────────────────────────────────────────────────
# R-DM-037 旅行：无迷路风险 → 免导航检定（被动察觉照常）
# ──────────────────────────────────────────────────────────────────────────

def test_travel_skips_nav_check_on_known_route():
    """needs_check=false 的旅行 → 免导航检定且不迷路；被动察觉仍在输出中。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from aidm.brain.resolvers.actions import resolve_travel

        ch = store.save_character(_make_char())
        state = {"player_input": "我们沿官道返回镇上"}
        d = resolve_travel(state, ch, {"needs_check": False, "terrain": "草原"})
        assert d["nav_check_skipped"] is True
        assert d["nav_check_total"] is None
        assert d["nav_result"]["lost"] is False
        assert d["nav_result"]["length_multiplier"] == 1.0
        assert "perception_result" in d          # 被动察觉不掷骰，照常计算

        d2 = resolve_travel(state, ch, {"terrain": "草原"})
        assert d2["nav_check_skipped"] is False and d2["nav_check_total"] is not None
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


# ──────────────────────────────────────────────────────────────────────────
# DMG 运作交涉：友好/冷漠 NPC 合理请求免掷；敌对 NPC 不免
# ──────────────────────────────────────────────────────────────────────────

def _scene_with_npc(store, camp_id, name, attitude):
    from aidm.stats import models
    sc = models.Scene(campaign_id=camp_id,
                      npcs_json=json.dumps([{"name": name, "attitude": attitude}]))
    return store.save_scene(sc)


def test_social_auto_success_for_friendly_npc():
    """友好 NPC + needs_check=false → 免掷自动成功，态度不变。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from aidm.brain.resolvers.actions import resolve_social

        camp = store.create_campaign("社交免检定")
        ch = _make_char()
        ch.campaign_id = camp.id
        ch = store.save_character(ch)
        _scene_with_npc(store, camp.id, "旅店老板", "friendly")

        state = {"campaign_id": camp.id, "player_input": "向老板打听矿坑的方向"}
        d = resolve_social(state, ch, {"npc_name": "旅店老板", "needs_check": False})
        assert d.get("auto_success") is True and d.get("success") is True
        assert d.get("npc_attitude") == "friendly"
        assert d.get("new_attitude") == "friendly"
        assert "d20" not in d
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


def test_social_hostile_npc_still_rolls():
    """存盘敌对 NPC：即使 LLM 给 needs_check=false 也照常掷骰（误判防护）。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from aidm.brain.resolvers.actions import resolve_social

        camp = store.create_campaign("社交敌对")
        ch = _make_char()
        ch.campaign_id = camp.id
        ch = store.save_character(ch)
        _scene_with_npc(store, camp.id, "匪首", "hostile")

        state = {"campaign_id": camp.id, "player_input": "劝匪首放我们过去"}
        d = resolve_social(state, ch, {"npc_name": "匪首", "needs_check": False})
        assert "auto_success" not in d
        assert 1 <= d.get("d20", 0) <= 20 and "check_total" in d
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


if __name__ == "__main__":
    for fn in sorted(k for k in dir() if k.startswith("test_")):
        print(f"-- {fn}")
        globals()[fn]()
    print("ALL OK")
