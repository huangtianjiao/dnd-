"""P5 升级/专长/多职业统一测试（方案 §8.1-§8.4）。

覆盖:
  - R-FTR-001: FeatEntitlementService — 战士 6/14 额外节点、游荡者 10、
    泛型职业无额外节点；levelup/feat 路由生产路径不再依赖全局 FEAT_LEVELS
  - R-PRE-001: PrerequisiteEvaluator — 原子条件与 ANY/ALL/NOT 嵌套
  - R-MC-001: MulticlassService 收敛 — levelup 兼职委托 engine 权威实现，
    Pact Magic 独立（魔契师不参与合并）、不额外授予豁免
  - R-LVL-001: level-up 事务管线 — XP 门禁、逐级升级、hp/class_levels 落库、
    feat entitlement 落 pending choices、兼职先决 422
"""

from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path

import pytest


def _setup_db():
    from aidm.stats import store as S
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    Path(path).unlink()
    orig_default, orig_engines = S.DEFAULT_DB, S._engines.copy()
    S.DEFAULT_DB = f"sqlite:///{path}"
    S._engines.clear()
    S.get_engine(S.DEFAULT_DB)
    return path, orig_default, orig_engines, S


def _teardown(od, oe, S, path):
    S.DEFAULT_DB = od
    S._engines.clear()
    S._engines.update(oe)
    with contextlib.suppress(OSError):
        Path(path).unlink()


# ──────────────────────────────────────────────────────────────────────────
# FeatEntitlementService（R-FTR-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-FTR-001")
class TestFeatEntitlement:
    def test_standard_and_epic_nodes(self):
        from aidm.rules.feat_entitlement import entitled_asi_levels
        nodes = entitled_asi_levels({}, 8)
        assert nodes == {4, 8}
        assert 19 in entitled_asi_levels({}, 19)

    def test_fighter_extra_nodes_by_class_level(self):
        from aidm.rules.feat_entitlement import entitled_asi_levels
        assert 6 in entitled_asi_levels({"fighter": 6}, 6)
        assert 14 in entitled_asi_levels({"fighter": 14}, 14)
        # 职业等级不足 → 不授予
        assert 6 not in entitled_asi_levels({"fighter": 5}, 6)

    def test_rogue_extra_node_10(self):
        from aidm.rules.feat_entitlement import entitled_asi_levels
        assert 10 in entitled_asi_levels({"rogue": 10}, 10)
        assert 10 not in entitled_asi_levels({"fighter": 10}, 10)

    def test_chinese_class_key_supported(self):
        from aidm.rules.feat_entitlement import entitled_asi_levels
        assert 6 in entitled_asi_levels({"战士": 6}, 6)

    def test_pending_asi_choice(self):
        from aidm.rules.feat_entitlement import pending_asi_choice
        assert pending_asi_choice(4, {"fighter": 4}) is not None
        assert pending_asi_choice(3, {"fighter": 3}) is None


# ──────────────────────────────────────────────────────────────────────────
# PrerequisiteEvaluator（R-PRE-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-PRE-001")
class TestPrerequisiteEvaluator:
    def test_atomic_conditions(self):
        from aidm.rules.prerequisite import ability, class_level, evaluate, has_feature, level
        ok, fail = evaluate(level(4), level=4)
        assert ok and not fail
        ok, fail = evaluate(level(4), level=3)
        assert not ok and fail
        ok, _ = evaluate(class_level("fighter", 4), level=1, class_levels={"fighter": 4})
        assert ok
        ok, _ = evaluate(ability("str", 13), abilities={"str": 15})
        assert ok
        ok, _ = evaluate(has_feature("fighter_second_wind"),
                         features=["fighter_second_wind"])
        assert ok

    def test_nested_logic(self):
        from aidm.rules.prerequisite import ability, all_of, any_of, evaluate, not_of
        pre = all_of(ability("str", 13), ability("con", 13))
        ok, fail = evaluate(pre, abilities={"str": 15, "con": 10})
        assert not ok and len(fail) == 1
        ok2, _ = evaluate(pre, abilities={"str": 15, "con": 14})
        assert ok2
        pre_any = any_of(ability("str", 13), ability("dex", 13))
        assert evaluate(pre_any, abilities={"str": 8, "dex": 14})[0] is True
        pre_not = not_of(ability("str", 20))
        assert evaluate(pre_not, abilities={"str": 16})[0] is True


# ──────────────────────────────────────────────────────────────────────────
# MulticlassService 收敛（R-MC-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-MC-001")
class TestMulticlassConvergence:
    def test_levelup_delegates_to_engine(self):
        """brain/levelup 兼职接口委托 engine 权威实现（魔契师不参与合并）。"""
        from aidm.brain.levelup import check_multiclass_prerequisite, multiclass_spell_slots
        assert multiclass_spell_slots({"魔契师": 6}) == {}, "Pact Magic 必须独立"
        assert multiclass_spell_slots({"法师": 5}) == {1: 4, 2: 3, 3: 2}
        r = check_multiclass_prerequisite({"scores": {"INT": 12}}, "法师")
        assert r["eligible"] is False

    def test_no_duplicate_rule_tables(self):
        """levelup 不再维护重复的兼职数据表（收敛后仅剩委托壳）。"""
        import inspect

        from aidm.brain import levelup
        src = inspect.getsource(levelup)
        assert "_MULTICLASS_PREREQ =" not in src
        assert "_MULTICLASS_SPELL_SLOTS =" not in src
        assert "_MULTICLASS_PROFICIENCIES =" not in src

    def test_multiclass_no_extra_saves(self):
        from aidm.engine.multiclass import MulticlassService
        granted = MulticlassService().get_proficiencies_granted("法师", set())
        assert granted["saves"] == []


# ──────────────────────────────────────────────────────────────────────────
# Level-up 事务管线（R-LVL-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-LVL-001")
class TestLevelUpPipeline:
    def _client_and_char(self):
        from fastapi.testclient import TestClient

        from aidm.api.main import app
        from aidm.stats import store as S
        client = TestClient(app)
        camp = client.post("/campaign", json={"name": "升级战役"}).json()
        r = client.post("/character", json={
            "name": "升级者", "race": "人类", "char_class": "战士",
            "background": "士兵", "skills": ["运动", "威吓"],
            "abilities": {"str": 16, "dex": 12, "con": 14,
                          "int": 10, "wis": 10, "cha": 10},
            "campaign_id": camp["id"]})
        cid = r.json()["id"]
        tok = client.post("/auth/session", json={
            "campaign_id": camp["id"], "character_id": cid}).json()["token"]
        return client, cid, {"Authorization": f"Bearer {tok}"}, S

    def test_xp_gate_and_multiclass_gate(self):
        path, od, oe, S = _setup_db()
        try:
            client, cid, H, S = self._client_and_char()
            # XP 不足 → 422
            r = client.post(f"/character/{cid}/level-up", json={}, headers=H)
            assert r.status_code == 422
            # 兼职先决不满足 → 422
            S.add_character_xp(cid, 300)
            r2 = client.post(f"/character/{cid}/level-up",
                             json={"new_class": "法师"}, headers=H)
            assert r2.status_code == 422
            assert "int" in r2.json()["detail"]["message"]
        finally:
            _teardown(od, oe, S, path)

    def test_full_level_up_to_6_with_feat_pending(self):
        """1→6 逐级升级：4 级与 6 级（战士额外节点）生成 pending choice。"""
        path, od, oe, S = _setup_db()
        try:
            client, cid, H, S = self._client_and_char()
            S.add_character_xp(cid, 14000)
            feats_at = []
            for _ in range(5):
                rr = client.post(f"/character/{cid}/level-up", json={}, headers=H)
                assert rr.status_code == 200
                feats_at.append((rr.json()["new_level"], rr.json()["feat_available"]))
            got = [lv for lv, fa in feats_at if fa]
            assert got == [4, 6], f"feat 节点应为 [4, 6]，实际 {got}"
            ch = S.get_character(cid)
            assert ch.level == 6
            assert ch.class_levels == {"战士": 6}
            assert ch.hp_max > 44
            pend = client.get(f"/character/{cid}/pending-choices", headers=H).json()
            ids = {c["choice_id"] for c in pend["pending_choices"]}
            assert {"choice.asi_or_feat.lv4", "choice.asi_or_feat.lv6"} <= ids
        finally:
            _teardown(od, oe, S, path)

    def test_level_up_persists_grant(self):
        path, od, oe, S = _setup_db()
        try:
            client, cid, H, S = self._client_and_char()
            S.add_character_xp(cid, 300)
            client.post(f"/character/{cid}/level-up", json={}, headers=H)
            grants = S.list_character_grants(cid)
            assert any(g.grant_id == "levelup.战士.2" for g in grants)
        finally:
            _teardown(od, oe, S, path)
