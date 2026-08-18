"""P6 资源/休息/生命状态测试（方案 §9.1-§9.4）。

覆盖:
  - R-RES-001: ResourcePool 持久化 — 创建即落库（战士回气公式表），
    短休/长休 recharge 后 save→reload 不漂移
  - R-RST-001: RestService 事务 — API 不再手动挑字段，HD 消耗、
    力竭、临时HP、法术位、资源池全部原子落库
  - R-HLT-001: HealthService — 临时HP吸收、0HP 濒死、死亡豁免 3 败死亡/
    3 胜稳定、治疗醒来、瞬死
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


def _client_char(S):
    from fastapi.testclient import TestClient

    from aidm.api.main import app
    client = TestClient(app)
    camp = client.post("/campaign", json={"name": "休整战役"}).json()
    r = client.post("/character", json={
        "name": "休整者", "race": "人类", "char_class": "战士",
        "background": "士兵", "skills": ["运动", "威吓"],
        "abilities": {"str": 16, "dex": 12, "con": 14,
                      "int": 10, "wis": 10, "cha": 10},
        "campaign_id": camp["id"]})
    cid = r.json()["id"]
    tok = client.post("/auth/session", json={
        "campaign_id": camp["id"], "character_id": cid}).json()["token"]
    return client, cid, {"Authorization": f"Bearer {tok}"}


# ──────────────────────────────────────────────────────────────────────────
# ResourcePool 持久化（R-RES-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-RES-001")
class TestResourcePoolPersistence:
    def test_creation_persists_pools_and_hit_dice(self):
        path, od, oe, S = _setup_db()
        try:
            client, cid, _ = _client_char(S)
            ch = S.get_character(cid)
            assert ch.resource_pools["second_wind"]["max"] == 2   # 战士 1 级公式表
            assert ch.resource_pools["second_wind"]["recharge"] == "short_rest"
            assert ch.hit_dice_max == 1 and ch.hit_dice_current == 1
            # save→reload 不丢
            reloaded = S.get_character(cid)
            assert reloaded.resource_pools == ch.resource_pools
        finally:
            _teardown(od, oe, S, path)

    def test_spend_and_reload_consistent(self):
        path, od, oe, S = _setup_db()
        try:
            client, cid, _ = _client_char(S)
            ch = S.get_character(cid)
            pools = ch.resource_pools
            pools["second_wind"]["current"] = 0   # 已消耗
            ch.set_resource_pools(pools)
            S.save_character(ch)
            assert S.get_character(cid).pool_current("second_wind") == 0
        finally:
            _teardown(od, oe, S, path)


# ──────────────────────────────────────────────────────────────────────────
# RestService 事务（R-RST-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-RST-001")
class TestRestTransaction:
    def test_short_rest_applies_hd_and_pools(self):
        path, od, oe, S = _setup_db()
        try:
            client, cid, H = _client_char(S)
            ch = S.get_character(cid)
            ch.hp_current = 5
            ch.hit_dice_current = 1
            pools = ch.resource_pools
            pools["second_wind"]["current"] = 0
            ch.set_resource_pools(pools)
            S.save_character(ch)
            r = client.post(f"/character/{cid}/rest", json={"type": "short"}, headers=H)
            assert r.status_code == 200
            d = r.json()
            assert d["hit_dice_remaining"] == 1   # 未消耗 HD（默认0）
            assert "second_wind" in d["pools_recharged"]
            reloaded = S.get_character(cid)
            assert reloaded.pool_current("second_wind") == 2
        finally:
            _teardown(od, oe, S, path)

    def test_long_rest_full_restore(self):
        path, od, oe, S = _setup_db()
        try:
            client, cid, H = _client_char(S)
            ch = S.get_character(cid)
            ch.hp_current = 3
            ch.temp_hp = 4
            ch.exhaustion = 1
            ch.hit_dice_current = 1
            ch.hit_dice_max = 1
            pools = ch.resource_pools
            pools["second_wind"]["current"] = 0
            ch.set_resource_pools(pools)
            S.save_character(ch)
            r = client.post(f"/character/{cid}/rest", json={"type": "long"}, headers=H)
            assert r.status_code == 200
            ch2 = S.get_character(cid)
            assert ch2.hp_current == ch2.hp_max
            assert ch2.hit_dice_current == ch2.hit_dice_max
            assert ch2.exhaustion == 0
            assert ch2.temp_hp == 0
            assert ch2.pool_current("second_wind") == ch2.pool_max("second_wind")
        finally:
            _teardown(od, oe, S, path)

    def test_rest_requires_conscious(self):
        path, od, oe, S = _setup_db()
        try:
            client, cid, H = _client_char(S)
            ch = S.get_character(cid)
            ch.hp_current = 0
            S.save_character(ch)
            r = client.post(f"/character/{cid}/rest", json={"type": "short"}, headers=H)
            assert r.status_code == 422
            assert r.json()["detail"]["error"] == "rest_failed"
        finally:
            _teardown(od, oe, S, path)

    def test_long_rest_full_restore_single_class_wizard_slots(self):
        """施法者长休法术位恢复落库。"""
        path, od, oe, S = _setup_db()
        try:
            from fastapi.testclient import TestClient

            from aidm.api.main import app
            client = TestClient(app)
            camp = client.post("/campaign", json={"name": "法师战役"}).json()
            r = client.post("/character", json={
                "name": "法术位者", "race": "精灵", "char_class": "法师",
                "abilities": {"str": 8, "dex": 14, "con": 12, "int": 17,
                              "wis": 12, "cha": 10},
                "campaign_id": camp["id"], "level": 5})
            cid = r.json()["id"]
            ch = S.get_character(cid)
            assert ch.spell_slots, "施法者创建时应有法术位"
            used = dict(ch.spell_slots)
            for k in used:
                used[k] = 0
            ch.set_spell_slots(used)
            S.save_character(ch)
            tok = client.post("/auth/session", json={
                "campaign_id": camp["id"], "character_id": cid}).json()["token"]
            H = {"Authorization": f"Bearer {tok}"}
            r2 = client.post(f"/character/{cid}/rest", json={"type": "long"}, headers=H)
            assert r2.status_code == 200
            ch2 = S.get_character(cid)
            assert all(v > 0 for v in ch2.spell_slots.values()), "长休后法术位应恢复"
        finally:
            _teardown(od, oe, S, path)


# ──────────────────────────────────────────────────────────────────────────
# HealthService（R-HLT-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-HLT-001")
class TestHealthService:
    def _mk(self):
        from aidm.stats.models import Character
        ch = Character(name="H", race="人类", char_class="战士", level=1)
        ch.hp_current = 12
        ch.hp_max = 12
        ch.temp_hp = 0
        return ch

    def test_temp_hp_absorbed_first(self):
        from aidm.rules.health import HealthService
        ch = self._mk()
        ch.temp_hp = 5
        ev = HealthService().apply_damage(ch, 7)
        assert ch.hp_current == 10 and ch.temp_hp == 0
        assert ev.temp_hp_delta == -5

    def test_zero_hp_enters_dying(self):
        from aidm.rules.health import HealthService, HealthState
        ch = self._mk()
        ev = HealthService().apply_damage(ch, 12)
        assert ev.state == HealthState.UNCONSCIOUS_DYING
        assert ch.death_failures == 1  # 倒下瞬间自动 1 失败（2024）

    def test_three_failures_die(self):
        from aidm.rules.health import HealthService, HealthState
        ch = self._mk()
        h = HealthService()
        h.apply_damage(ch, 12)
        h.add_death_save(ch, False)
        assert h.add_death_save(ch, False).state == HealthState.DEAD

    def test_three_successes_stabilize(self):
        from aidm.rules.health import HealthService, HealthState
        ch = self._mk()
        h = HealthService()
        h.apply_damage(ch, 12)
        h.add_death_save(ch, True)
        h.add_death_save(ch, True)
        ev = h.add_death_save(ch, True)
        assert ev.state == HealthState.STABLE and ch.stable is True

    def test_healing_wakes(self):
        from aidm.rules.health import HealthService, HealthState
        ch = self._mk()
        h = HealthService()
        h.apply_damage(ch, 12)
        ev = h.apply_healing(ch, 5)
        assert ev.state == HealthState.ALIVE
        assert ch.hp_current == 5
        assert ch.death_failures == 0 and ch.death_successes == 0

    def test_instant_death(self):
        from aidm.rules.health import HealthService, HealthState
        ch = self._mk()
        ev = HealthService().apply_damage(ch, 30)  # 溢出 18 ≥ 12 → 瞬死
        assert ev.state == HealthState.DEAD and ch.dead is True

    def test_no_instant_death_without_overflow(self):
        from aidm.rules.health import HealthService, HealthState
        ch = self._mk()
        ev = HealthService().apply_damage(ch, 20)  # 溢出 8 < 12 → 濒死
        assert ev.state == HealthState.UNCONSCIOUS_DYING and ch.dead is False

    def test_healing_does_not_exceed_max(self):
        from aidm.rules.health import HealthService
        ch = self._mk()
        ch.hp_current = 9
        HealthService().apply_healing(ch, 50)
        assert ch.hp_current == 12
