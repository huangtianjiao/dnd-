"""P7 Spellcasting 重构测试（方案 §10.1-§10.4）。

覆盖:
  - R-SPL-101: 来源分离 — 已知制(knowledged)/法术书制(spellbook)/准备制(prepared)
    初始化各归其位；角色不会自动掌握整张职业表
  - R-SPL-102: GET 不再 fallback 职业列表（空即空）
  - R-SPL-103: prepare-spell 唯一写入路径 — 准备制校验/环阶门控/数量上限/幂等
  - R-SPL-104: 数量表 — known/prepared 计数（2024 PHB）
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


def _make_char(client, name, cls, abilities, camp_id):
    r = client.post("/character", json={
        "name": name, "race": "人类", "char_class": cls,
        "abilities": abilities, "campaign_id": camp_id})
    assert r.status_code == 200, r.text
    cid = r.json()["id"]
    tok = client.post("/auth/session", json={
        "campaign_id": camp_id, "character_id": cid}).json()["token"]
    return cid, {"Authorization": f"Bearer {tok}"}


# ──────────────────────────────────────────────────────────────────────────
# 来源分离（R-SPL-101 / R-SPL-102）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-SPL-101")
class TestSpellSourceSeparation:
    def test_wizard_spellbook_not_auto_prepared(self):
        """法师：seed 进法术书，known/prepared 不自动全表（方案 §10.1）。"""
        path, od, oe, S = _setup_db()
        try:
            from fastapi.testclient import TestClient

            from aidm.api.main import app
            client = TestClient(app)
            camp = client.post("/campaign", json={"name": "施法战役"}).json()
            cid, H = _make_char(client, "法书", "法师",
                                {"str": 8, "dex": 14, "con": 12, "int": 17,
                                 "wis": 12, "cha": 10}, camp["id"])
            ch = S.get_character(cid)
            assert ch.known_spells == []
            assert len(ch.spellbook_spells) > 0
            assert ch.prepared_spells == []
            # GET 不 fallback
            r = client.get(f"/character/{cid}", headers=H)
            assert r.json()["known_spells"] == []
        finally:
            _teardown(od, oe, S, path)

    def test_known_caster_seeded_to_known(self):
        path, od, oe, S = _setup_db()
        try:
            from fastapi.testclient import TestClient

            from aidm.api.main import app
            client = TestClient(app)
            camp = client.post("/campaign", json={"name": "施法战役"}).json()
            cid, _ = _make_char(client, "吟者", "吟游诗人",
                                {"str": 8, "dex": 14, "con": 12, "int": 10,
                                 "wis": 10, "cha": 17}, camp["id"])
            ch = S.get_character(cid)
            assert len(ch.known_spells) > 0
            assert ch.prepared_spells == []
        finally:
            _teardown(od, oe, S, path)

    def test_prepared_caster_seeded_to_prepared(self):
        path, od, oe, S = _setup_db()
        try:
            from fastapi.testclient import TestClient

            from aidm.api.main import app
            client = TestClient(app)
            camp = client.post("/campaign", json={"name": "施法战役"}).json()
            cid, _ = _make_char(client, "牧者", "牧师",
                                {"str": 10, "dex": 10, "con": 12, "int": 10,
                                 "wis": 17, "cha": 14}, camp["id"])
            ch = S.get_character(cid)
            assert ch.known_spells == []
            assert len(ch.prepared_spells) > 0
        finally:
            _teardown(od, oe, S, path)


# ──────────────────────────────────────────────────────────────────────────
# prepare-spell 唯一路径（R-SPL-103）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-SPL-103")
class TestPrepareSpell:
    def test_ring_gate_rejects_high_ring(self):
        path, od, oe, S = _setup_db()
        try:
            from fastapi.testclient import TestClient

            from aidm.api.main import app
            client = TestClient(app)
            camp = client.post("/campaign", json={"name": "门禁战役"}).json()
            cid, H = _make_char(client, "环阶者", "法师",
                                {"str": 8, "dex": 14, "con": 12, "int": 17,
                                 "wis": 12, "cha": 10}, camp["id"])
            r = client.post(f"/character/{cid}/prepare-spell",
                            json={"spell_name": "火球术"}, headers=H)
            assert r.status_code == 422
            assert "超过当前最高可用环" in r.json()["detail"]["message"]
        finally:
            _teardown(od, oe, S, path)

    def test_count_limit_enforced(self):
        """1 级法师（INT 17→+3）：准备上限 = 3 + 1 = 4。"""
        path, od, oe, S = _setup_db()
        try:
            from fastapi.testclient import TestClient

            from aidm.api.main import app
            client = TestClient(app)
            camp = client.post("/campaign", json={"name": "数量战役"}).json()
            cid, H = _make_char(client, "数限者", "法师",
                                {"str": 8, "dex": 14, "con": 12, "int": 17,
                                 "wis": 12, "cha": 10}, camp["id"])
            for name in ("魔法飞弹", "护盾术", "燃烧之手", "法师护甲"):
                r = client.post(f"/character/{cid}/prepare-spell",
                                json={"spell_name": name}, headers=H)
                assert r.status_code == 200, (name, r.text)
            # 第 5 个 → 超限
            r5 = client.post(f"/character/{cid}/prepare-spell",
                             json={"spell_name": "睡眠术"}, headers=H)
            assert r5.status_code == 422
            assert "上限" in r5.json()["detail"]["message"]
            # 幂等：重复准备已准备好的法术 → 200 不叠加
            r6 = client.post(f"/character/{cid}/prepare-spell",
                             json={"spell_name": "魔法飞弹"}, headers=H)
            assert r6.status_code == 200
            assert r6.json()["count"] == 4
        finally:
            _teardown(od, oe, S, path)

    def test_non_prepared_caster_rejected(self):
        path, od, oe, S = _setup_db()
        try:
            from fastapi.testclient import TestClient

            from aidm.api.main import app
            client = TestClient(app)
            camp = client.post("/campaign", json={"name": "非准备战役"}).json()
            cid, H = _make_char(client, "吟唱者", "吟游诗人",
                                {"str": 8, "dex": 14, "con": 12, "int": 10,
                                 "wis": 10, "cha": 17}, camp["id"])
            r = client.post(f"/character/{cid}/prepare-spell",
                            json={"spell_name": "魔法飞弹"}, headers=H)
            assert r.status_code == 422
            assert "不是准备制施法者" in r.json()["detail"]["message"]
        finally:
            _teardown(od, oe, S, path)

    def test_unprepare_removes(self):
        path, od, oe, S = _setup_db()
        try:
            from fastapi.testclient import TestClient

            from aidm.api.main import app
            client = TestClient(app)
            camp = client.post("/campaign", json={"name": "删除战役"}).json()
            cid, H = _make_char(client, "撤法者", "法师",
                                {"str": 8, "dex": 14, "con": 12, "int": 17,
                                 "wis": 12, "cha": 10}, camp["id"])
            client.post(f"/character/{cid}/prepare-spell",
                        json={"spell_name": "魔法飞弹"}, headers=H)
            r = client.delete(f"/character/{cid}/prepare-spell?spell_name=魔法飞弹",
                              headers=H)
            assert r.status_code == 200
            assert r.json()["count"] == 0
        finally:
            _teardown(od, oe, S, path)


# ──────────────────────────────────────────────────────────────────────────
# 数量表（R-SPL-104）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-SPL-104")
class TestSpellCountTables:
    def test_known_counts_2024(self):
        from aidm.rules.spellcasting import known_spells_count
        assert known_spells_count("吟游诗人", 1) == 4
        assert known_spells_count("术士", 5) == 9
        assert known_spells_count("魔契师", 2) == 5

    def test_prepared_counts(self):
        from aidm.rules.spellcasting import prepared_spells_count
        # 牧师 1 级 WIS 17(+3): 3 + 1 = 4
        assert prepared_spells_count("牧师", 1, 3) == 4
        # 圣武士 2 级 CHA 16(+3): 3 + max(1, 1) = 4
        assert prepared_spells_count("圣武士", 2, 3) == 4
        # 圣武士 6 级: 3 + 3 = 6
        assert prepared_spells_count("圣武士", 6, 3) == 6
        # 非施法职业
        assert prepared_spells_count("战士", 5, 2) == 0
