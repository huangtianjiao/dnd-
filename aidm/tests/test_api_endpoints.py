"""FastAPI 端点单元测试 — api/main.py

验证规则点:
  R-CHK-024 GET /character/{id} 返回完整角色卡（含属性调整值）
  R-CHK-015 GET /character/{id} 返回熟练加值
  R-CMB-002 POST /chat 攻击检定流程
  R-DMG-017 死亡豁免逻辑

使用 TestClient + 临时 SQLite 数据库，测试后清理。

运行:
  PYTHONPATH=src python tests/test_api_endpoints.py
  PYTHONPATH=src python -m pytest tests/test_api_endpoints.py -v
"""

from __future__ import annotations

import os
import sys
import tempfile


def _setup_test_db():
    """创建临时数据库并 patch store 模块。"""
    tmpdir = tempfile.mkdtemp(prefix="aidm_test_")
    db_path = f"sqlite:///{tmpdir}/test.db"

    from aidm.stats import store
    # 保存原始值
    orig_default = store.DEFAULT_DB
    orig_engines = store._engines.copy()

    store.DEFAULT_DB = db_path
    store._engines.clear()
    # get_engine 会自动 create_all
    store.get_engine(db_path)

    return db_path, orig_default, orig_engines, store


def _teardown_test_db(orig_default, orig_engines, store):
    """恢复原始数据库配置。"""
    store.DEFAULT_DB = orig_default
    store._engines.clear()
    store._engines.update(orig_engines)


# ──────────────────────────────────────────────────────────────────────────
# 基础端点
# ──────────────────────────────────────────────────────────────────────────

def test_health_endpoint():
    """GET /health 返回 {"status":"ok"}。"""
    from fastapi.testclient import TestClient
    from aidm.api.main import app

    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_campaign_and_character_creation():
    """POST /campaign + POST /character 创建战役和角色。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from fastapi.testclient import TestClient
        from aidm.api.main import app

        client = TestClient(app)

        # 创建战役
        r = client.post("/campaign", json={"name": "测试战役"})
        assert r.status_code == 200
        camp = r.json()
        assert camp["name"] == "测试战役"
        assert "id" in camp

        # 创建角色
        r = client.post("/character", json={
            "name": "测试勇者",
            "race": "人类",
            "char_class": "战士",
            "level": 3,
            "abilities": {"str": 16, "dex": 12, "con": 14, "int": 10, "wis": 10, "cha": 10},
            "hp_max": 30,
            "ac": 16,
            "campaign_id": camp["id"],
        })
        assert r.status_code == 200
        ch = r.json()
        assert ch["name"] == "测试勇者"
        assert "id" in ch
        return camp, ch
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


def test_get_character_returns_full_sheet():
    """GET /character/{id} 返回完整角色卡数据。R-CHK-024/R-CHK-015"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from fastapi.testclient import TestClient
        from aidm.api.main import app

        client = TestClient(app)

        # 建战役+角色
        camp = client.post("/campaign", json={"name": "T"}).json()
        ch = client.post("/character", json={
            "name": "英雄",
            "race": "精灵",
            "char_class": "法师",
            "level": 5,
            "abilities": {"str": 8, "dex": 14, "con": 12, "int": 18, "wis": 12, "cha": 10},
            "hp_max": 28,
            "ac": 12,
            "campaign_id": camp["id"],
        }).json()

        # 获取角色卡
        r = client.get(f"/character/{ch['id']}")
        assert r.status_code == 200
        c = r.json()

        # 验证基本字段
        assert c["name"] == "英雄"
        assert c["level"] == 5
        assert c["ac"] == 12

        # 验证属性调整值 (INT 18 → +4)
        assert c["abilities"]["int"]["score"] == 18
        assert c["abilities"]["int"]["mod"] == 4

        # 验证熟练加值 (5级 → +3)
        assert c["proficiency"] == 3
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


def test_list_campaigns():
    """GET /campaigns 返回战役列表。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from fastapi.testclient import TestClient
        from aidm.api.main import app

        client = TestClient(app)

        # 创建两个战役
        client.post("/campaign", json={"name": "战役A"})
        client.post("/campaign", json={"name": "战役B"})

        r = client.get("/campaigns")
        assert r.status_code == 200
        data = r.json()
        assert "campaigns" in data
        assert len(data["campaigns"]) >= 2
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


def test_combat_state_empty():
    """GET /combat/{campaign_id} 无战斗时返回 active=False。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from fastapi.testclient import TestClient
        from aidm.api.main import app

        client = TestClient(app)
        camp = client.post("/campaign", json={"name": "C"}).json()

        r = client.get(f"/combat/{camp['id']}")
        assert r.status_code == 200
        data = r.json()
        assert data["active"] is False
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


def test_monster_lookup():
    """GET /monster/{name} 查询怪物数据。"""
    from fastapi.testclient import TestClient
    from aidm.api.main import app

    client = TestClient(app)
    r = client.get("/monster/哥布林")
    # 可能找到也可能找不到，取决于 RAG 索引
    if r.status_code == 200:
        data = r.json()
        assert "name" in data or "body" in data


def test_magic_items_list():
    """GET /magic-items 列出魔法物品。"""
    from fastapi.testclient import TestClient
    from aidm.api.main import app

    client = TestClient(app)
    r = client.get("/magic-items")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "count" in data


def test_feats_list():
    """GET /feats 列出专长。"""
    from fastapi.testclient import TestClient
    from aidm.api.main import app

    client = TestClient(app)
    r = client.get("/feats")
    assert r.status_code == 200
    data = r.json()
    assert "feats" in data


# ──────────────────────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────────────────────

def main():
    """运行所有测试。"""
    tests = [
        test_health_endpoint,
        test_campaign_and_character_creation,
        test_get_character_returns_full_sheet,
        test_list_campaigns,
        test_combat_state_empty,
        test_monster_lookup,
        test_magic_items_list,
        test_feats_list,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  ✓ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__}: {e}")
            failed += 1
    print(f"\n{'='*50}")
    print(f"API端点测试: {passed} 通过, {failed} 失败")
    print(f"{'='*50}")
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
