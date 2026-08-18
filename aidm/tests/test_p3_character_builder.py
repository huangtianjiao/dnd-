"""P3 CharacterBuilder 接线 + P2 invariant 锁定测试（方案 §6.1/§6.3/§5.1/§3.4）。

覆盖:
  - R-BLD-001: 所有创建入口共用 CharacterBuilder 校验；非法选择 422
  - R-BLD-001: 创建后 Grant/Choice provenance 持久化（species/background/class/skills）
  - R-CHC-001: pending choices API（未解决选择可见/非法值 422/幂等 409）
  - invariant: Character 不变量校验（hp/力竭/生命状态/class_levels/abilities）
"""

from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path

import pytest

_RULE = "R-BLD-001"


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


def _teardown(orig_default, orig_engines, S, path=None):
    S.DEFAULT_DB = orig_default
    S._engines.clear()
    S._engines.update(orig_engines)
    if path:
        with contextlib.suppress(OSError):
            Path(path).unlink()


def _client():
    from fastapi.testclient import TestClient

    from aidm.api.main import app
    return TestClient(app)


def _campaign(client):
    return client.post("/campaign", json={"name": "测试战役"}).json()


_ABILITIES = {"str": 15, "dex": 10, "con": 14, "int": 10, "wis": 10, "cha": 10}


# ──────────────────────────────────────────────────────────────────────────
# 唯一构建服务（R-BLD-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule(_RULE)
class TestBuilderWiring:
    def test_create_rejects_invalid_background(self):
        path, od, oe, S = _setup_db()
        try:
            client = _client()
            camp = _campaign(client)
            r = client.post("/character", json={
                "name": "非法背景", "race": "人类", "char_class": "战士",
                "background": "不存在的背景", "abilities": _ABILITIES,
                "campaign_id": camp["id"]})
            assert r.status_code == 422
            assert r.json()["detail"]["error"] == "invalid_character_build"
        finally:
            _teardown(od, oe, S, path)

    def test_create_rejects_invalid_class(self):
        path, od, oe, S = _setup_db()
        try:
            client = _client()
            camp = _campaign(client)
            r = client.post("/character", json={
                "name": "非法职业", "race": "人类", "char_class": "异界战士",
                "abilities": _ABILITIES, "campaign_id": camp["id"]})
            assert r.status_code == 422
        finally:
            _teardown(od, oe, S, path)

    def test_create_rejects_ability_out_of_range(self):
        path, od, oe, S = _setup_db()
        try:
            client = _client()
            camp = _campaign(client)
            bad = dict(_ABILITIES, str=25)
            r = client.post("/character", json={
                "name": "属性越界", "race": "人类", "char_class": "战士",
                "abilities": bad, "campaign_id": camp["id"]})
            assert r.status_code == 422
        finally:
            _teardown(od, oe, S, path)

    def test_create_persists_provenance(self):
        """创建落库后 grants/choices 完整（species/background/class/skills）。"""
        path, od, oe, S = _setup_db()
        try:
            client = _client()
            camp = _campaign(client)
            r = client.post("/character", json={
                "name": "阿尔", "race": "人类", "char_class": "战士",
                "background": "士兵", "skills": ["运动", "威吓"],
                "abilities": _ABILITIES, "campaign_id": camp["id"]})
            assert r.status_code == 200
            cid = r.json()["id"]
            grants = S.list_character_grants(cid)
            choices = S.list_character_choices(cid)
            gtypes = {g.grant_type for g in grants}
            assert gtypes == {"species", "background", "class"}
            cids = {c.choice_id for c in choices}
            assert {"choice.species", "choice.background", "choice.class",
                    "choice.skills"} <= cids
            assert any(c.selected_values == ["运动", "威吓"] for c in choices
                       if c.choice_id == "choice.skills")
        finally:
            _teardown(od, oe, S, path)

    def test_join_persists_provenance(self):
        path, od, oe, S = _setup_db()
        try:
            client = _client()
            camp = _campaign(client)
            r = client.post("/join", json={
                "name": "加入者", "race": "精灵", "char_class": "法师",
                "abilities": {"str": 8, "dex": 14, "con": 12, "int": 17,
                              "wis": 12, "cha": 10},
                "campaign_id": camp["id"]})
            assert r.status_code == 200
            cid = r.json()["character_id"]
            grants = S.list_character_grants(cid)
            assert {g.grant_type for g in grants} == {"species", "background", "class"}
            # 精灵 → human? 应为 elf
            assert any(g.grant_type == "species" and g.granted_item_id == "精灵"
                       for g in grants)
        finally:
            _teardown(od, oe, S, path)

    def test_fighter_resource_pools_formula_driven(self):
        """战士资源上限来自 classes 公式表（方案 §9.1）——1 级回气 2 次，无动作如潮/不屈。"""
        from aidm.build.character_builder import CharacterBuilder, CharacterBuildPlan
        from aidm.data.classes import FIGHTER_SECOND_WIND_BY_LEVEL
        from aidm.rules.choice import ChoiceManager
        from aidm.rules.grant import GrantManager
        from aidm.rules.resource import ResourceManager
        b = CharacterBuilder(GrantManager(), ChoiceManager(), ResourceManager())
        plan = CharacterBuildPlan(entity_id="f1", species_choice="human",
                                  background_choice="", class_choice="fighter",
                                  ability_scores=dict(_ABILITIES))
        b.build_character(plan)
        pools = b.resources.get_pools("f1")
        assert pools["second_wind"].max_value == FIGHTER_SECOND_WIND_BY_LEVEL[1]
        assert pools["second_wind"].recharge_on == "short_rest"
        assert "action_surge" not in pools   # 2 级才获得
        assert "indomitable" not in pools    # 9 级才获得


# ──────────────────────────────────────────────────────────────────────────
# Pending Choices API（R-CHC-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-CHC-001")
class TestPendingChoicesApi:
    def _char_with_pending(self, S):
        """创建角色 + 人为挂一条未解决选择。"""
        client = _client()
        camp = _campaign(client)
        r = client.post("/character", json={
            "name": "选择者", "race": "人类", "char_class": "战士",
            "background": "士兵", "skills": ["运动", "威吓"],
            "abilities": _ABILITIES, "campaign_id": camp["id"]})
        cid = r.json()["id"]
        from aidm.stats.models import CharacterChoice
        pc = CharacterChoice(choice_id="choice.test_waiting",
                             choice_type="test", source_id="class.fighter.lv1",
                             ruleset_revision="2024.1", validated=False)
        pc.set_selected_values([])
        pc.set_legal_options(["A", "B", "C"])
        S.add_character_choice(S.get_character(cid), pc)
        tok = client.post("/auth/session", json={
            "campaign_id": camp["id"], "character_id": cid}).json()["token"]
        return client, cid, {"Authorization": f"Bearer {tok}"}

    def test_pending_choices_listed(self):
        path, od, oe, S = _setup_db()
        try:
            client, cid, H = self._char_with_pending(S)
            r = client.get(f"/character/{cid}/pending-choices", headers=H)
            assert r.status_code == 200
            data = r.json()
            assert data["count"] == 1
            assert data["pending_choices"][0]["choice_id"] == "choice.test_waiting"
            assert data["pending_choices"][0]["legal_options_snapshot"] == ["A", "B", "C"]
        finally:
            _teardown(od, oe, S, path)

    def test_submit_invalid_value_rejected(self):
        path, od, oe, S = _setup_db()
        try:
            client, cid, H = self._char_with_pending(S)
            r = client.post(f"/character/{cid}/choices/choice.test_waiting",
                            json={"value": "Z"}, headers=H)
            assert r.status_code == 422
            assert r.json()["detail"]["error"] == "invalid_choice"
        finally:
            _teardown(od, oe, S, path)

    def test_submit_valid_then_idempotent_409(self):
        path, od, oe, S = _setup_db()
        try:
            client, cid, H = self._char_with_pending(S)
            r = client.post(f"/character/{cid}/choices/choice.test_waiting",
                            json={"value": "B"}, headers=H)
            assert r.status_code == 200
            assert r.json()["resolved"] is True
            # 再次提交 → 409（已解决）
            r2 = client.post(f"/character/{cid}/choices/choice.test_waiting",
                             json={"value": "C"}, headers=H)
            assert r2.status_code == 409
            # pending 清空
            pend = client.get(f"/character/{cid}/pending-choices", headers=H).json()
            assert pend["count"] == 0
        finally:
            _teardown(od, oe, S, path)


# ──────────────────────────────────────────────────────────────────────────
# Character 不变量（方案 §3.4/§5.2）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-DRV-001")
class TestCharacterInvariants:
    def _m(self):
        from aidm.stats.models import Character
        ch = Character(name="I", race="人类", char_class="战士", level=1)
        ch.set_abilities(dict(_ABILITIES))
        return ch

    def test_valid_character_passes(self):
        from aidm.build.derive_stats import apply_server_stats, validate_character_invariants
        ch = self._m()
        apply_server_stats(ch, "战士", "人类", 1, ch.abilities)
        assert validate_character_invariants(ch) == []

    def test_hp_overflow_detected(self):
        from aidm.build.derive_stats import apply_server_stats, validate_character_invariants
        ch = self._m()
        apply_server_stats(ch, "战士", "人类", 1, ch.abilities)
        ch.hp_current = ch.hp_max + 5
        errs = validate_character_invariants(ch)
        assert any("hp_current" in e for e in errs)

    def test_exhaustion_range_detected(self):
        from aidm.build.derive_stats import apply_server_stats, validate_character_invariants
        ch = self._m()
        apply_server_stats(ch, "战士", "人类", 1, ch.abilities)
        ch.exhaustion = 7
        assert any("exhaustion" in e for e in validate_character_invariants(ch))

    def test_death_saves_with_positive_hp_detected(self):
        from aidm.build.derive_stats import apply_server_stats, validate_character_invariants
        ch = self._m()
        apply_server_stats(ch, "战士", "人类", 1, ch.abilities)
        ch.death_failures = 2  # hp>0 时不允许死亡豁免计数
        assert any("死亡豁免" in e for e in validate_character_invariants(ch))

    def test_class_levels_mismatch_detected(self):
        from aidm.build.derive_stats import apply_server_stats, validate_character_invariants
        ch = self._m()
        apply_server_stats(ch, "战士", "人类", 1, ch.abilities)
        ch.set_class_levels({"战士": 6})  # level=1 不一致
        assert any("class_levels" in e for e in validate_character_invariants(ch))
