"""P8 精通授权门控 + ResolutionTrace 测试（方案 §11.2/§11.4）。

覆盖:
  - R-MAS-001: MasteryGrant 持久化 — 战士 1 级创建获授权（公式表数量），
    save→reload 不丢；其他职业无授权
  - R-MAS-002: 战斗解析只认角色授权 — 武器词条 ≠ 自动会用；
    授权角色触发精通，无授权角色不触发
  - R-TRC-001: 攻击结算产出动作级 ResolutionTrace（Narrator 输入）
"""

from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path

import pytest


def _setup_db():
    from aidm.stats import store as st
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    Path(path).unlink()
    orig_default, orig_engines = st.DEFAULT_DB, st._engines.copy()
    st.DEFAULT_DB = f"sqlite:///{path}"
    st._engines.clear()
    st.get_engine(st.DEFAULT_DB)
    return path, orig_default, orig_engines, st


def _teardown(od, oe, st, path):
    st.DEFAULT_DB = od
    st._engines.clear()
    st._engines.update(oe)
    with contextlib.suppress(OSError):
        Path(path).unlink()


# ──────────────────────────────────────────────────────────────────────────
# MasteryGrant 持久化（R-MAS-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-MAS-001")
class TestMasteryGrantPersistence:
    def test_fighter_creation_grants_masteries(self):
        path, od, oe, st = _setup_db()
        try:
            from fastapi.testclient import TestClient

            from aidm.api.main import app
            client = TestClient(app)
            camp = client.post("/campaign", json={"name": "精通战役"}).json()
            r = client.post("/character", json={
                "name": "精官兵", "race": "人类", "char_class": "战士",
                "abilities": {"str": 16, "dex": 12, "con": 14,
                              "int": 10, "wis": 10, "cha": 10},
                "campaign_id": camp["id"]})
            cid = r.json()["id"]
            ch = st.get_character(cid)
            grants = ch.mastery_grants
            assert len(grants) == 3          # 战士 1 级精通数量（公式表）
            assert grants[0]["source_id"] == "class.fighter.level1"
            assert ch.has_mastery(grants[0]["mastery_name"])
            # save→reload 不丢
            reloaded = st.get_character(cid)
            assert reloaded.mastery_grants == grants
        finally:
            _teardown(od, oe, st, path)

    def test_non_fighter_no_grants(self):
        path, od, oe, st = _setup_db()
        try:
            from fastapi.testclient import TestClient

            from aidm.api.main import app
            client = TestClient(app)
            camp = client.post("/campaign", json={"name": "无精通"}).json()
            r = client.post("/character", json={
                "name": "无精通者", "race": "人类", "char_class": "法师",
                "abilities": {"str": 8, "dex": 14, "con": 12, "int": 17,
                              "wis": 12, "cha": 10},
                "campaign_id": camp["id"]})
            ch = st.get_character(r.json()["id"])
            assert ch.mastery_grants == []
        finally:
            _teardown(od, oe, st, path)

    def test_add_mastery_idempotent(self):
        path, od, oe, st = _setup_db()
        try:
            from fastapi.testclient import TestClient

            from aidm.api.main import app
            client = TestClient(app)
            camp = client.post("/campaign", json={"name": "幂等"}).json()
            r = client.post("/character", json={
                "name": "幂等者", "race": "人类", "char_class": "战士",
                "abilities": {"str": 16, "dex": 12, "con": 14,
                              "int": 10, "wis": 10, "cha": 10},
                "campaign_id": camp["id"]})
            ch = st.get_character(r.json()["id"])
            ch.add_mastery_grant("迅击", source_id="class.fighter.level1")
            ch.add_mastery_grant("迅击", source_id="class.fighter.level1")
            ch.add_mastery_grant("迅击", source_id="class.fighter.level1")
            # 初始 3 个 seed + '迅击' 1 条（重复添加不叠加）→ 4 条
            assert len(ch.mastery_grants) == 4
        finally:
            _teardown(od, oe, st, path)


# ──────────────────────────────────────────────────────────────────────────
# 战斗解析授权门控（R-MAS-002）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-MAS-002")
class TestMasteryAuthorizationGate:
    def _fighter(self):
        from aidm.stats.models import Character
        ch = Character(name="战", race="人类", char_class="战士", level=1)
        ch.set_abilities({"str": 16, "dex": 12, "con": 14,
                          "int": 10, "wis": 10, "cha": 10})
        ch.hp_max = 12
        ch.hp_current = 12
        ch.add_mastery_grant("缓速", source_id="class.fighter.level1")
        ch.equipped_weapon = "短棒"   # 短棒 mastery=缓速
        return ch

    def test_authorized_fighter_triggers_mastery(self):
        from aidm.brain.resolvers import attack as atk_mod
        from aidm.engine import dice as engine_dice

        class _FixedRng:
            def randbelow(self, exclusive_upper):
                return 19  # d20=20 → 必中

        orig = engine_dice.get_active_rng()
        engine_dice.set_active_rng(_FixedRng())
        try:
            ch = self._fighter()
            out = atk_mod.resolve_attack(
                ch, {"weapon": "短棒", "target_ac": 8, "distance_ft": 5})
            assert out.get("mastery", {}).get("mastery") == "缓速"
        finally:
            engine_dice.set_active_rng(orig)

    def test_unauthorized_caster_no_mastery(self):
        from aidm.brain.resolvers import attack as atk_mod
        from aidm.stats.models import Character
        ch = Character(name="法", race="人类", char_class="法师", level=1)
        ch.set_abilities({"str": 8, "dex": 14, "con": 12,
                          "int": 17, "wis": 12, "cha": 10})
        ch.hp_max = 6
        ch.hp_current = 6
        ch.equipped_weapon = "短棒"
        out = atk_mod.resolve_attack(
            ch, {"weapon": "短棒", "target_ac": 8, "distance_ft": 5})
        # 武器词条存在但角色无授权 → 不触发（方案 §11.2）
        assert out.get("mastery") is None


# ──────────────────────────────────────────────────────────────────────────
# ResolutionTrace（R-TRC-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-TRC-001")
class TestResolutionTrace:
    def test_attack_outputs_action_trace(self):
        from aidm.brain.resolvers import attack as atk_mod
        from aidm.stats.models import Character
        ch = Character(name="战", race="人类", char_class="战士", level=1)
        ch.set_abilities({"str": 16, "dex": 12, "con": 14,
                          "int": 10, "wis": 10, "cha": 10})
        ch.hp_max = 12
        ch.hp_current = 12
        ch.equipped_weapon = "长剑"
        out = atk_mod.resolve_attack(
            ch, {"weapon": "长剑", "target_ac": 10, "distance_ft": 5})
        trace = out.get("action_trace")
        assert trace is not None
        assert trace["action"] == "attack:长剑"
        assert "attack_roll" in trace
        assert "target_ac" in trace and trace["target_ac"] == 10
        assert "hit" in trace
        assert "damage" in trace
        assert trace["damage"] == out.get("damage", 0)

    def test_trace_dict_roundtrip(self):
        from aidm.rules.combat_trace import attack_trace, trace_from_dict
        t = attack_trace(weapon="长剑", attack_roll=17, attack_bonus=6,
                         target_ac=15, hit=True, damage_roll="1d8+4",
                         damage=9, mastery="sap")
        d = t.to_dict()
        assert d["mastery"] == "sap" and d["damage"] == 9
        t2 = trace_from_dict(d)
        assert t2.action == t.action and t2.hit is True
