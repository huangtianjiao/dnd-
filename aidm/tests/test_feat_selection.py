"""专长选择集成测试 — PHB 2024 第五章「专长」。

验证:
  1. 等级4时能获取可选专长列表（available_feats）
  2. 选择专长后 Character.feats_json 更新（select_feat + 持久化）
  3. 不可重复选择非复选专长
  4. 复选专长可多次选取但不追加重复条目
  5. API 端点 GET /character/{id}/available-feats 与
     POST /character/{id}/select-feat 端到端可用

运行:
  PYTHONPATH=src python tests/test_feat_selection.py
"""

from __future__ import annotations

import os
import sys
import tempfile

# 确保 src 在路径中
_SRC = os.path.join(os.path.dirname(__file__), "..", "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from aidm.brain import levelup as lu
from aidm.data import feats as F
from aidm.stats import store, models


def _make_char(level: int = 4) -> models.Character:
    """创建一个指定等级的测试角色并持久化。"""
    ch = models.Character(name=f"测试角色_Lv{level}",
                          race="人类",
                          char_class="战士",
                          level=level,
                          campaign_id=None)
    ch.set_abilities({"str": 16, "dex": 12, "con": 14,
                      "int": 10, "wis": 10, "cha": 10})
    ch.hp_max = 30; ch.hp_current = 30; ch.ac = 16; ch.speed = 30
    ch = store.save_character(ch)
    return ch


def test_available_feats_at_level_4():
    """等级4角色应能获取可选专长列表。"""
    print("\n[Test 1] 等级4获取可选专长...")
    char = {"level": 4, "feats": []}
    avail = lu.available_feats(char)

    assert len(avail) > 0, "等级4应有可选专长"
    # 不含起源专长（起源专长仅在角色创建时由背景给予）
    assert all(f["category"] != "起源" for f in avail), \
        "可选列表不应包含起源专长"
    # 不含传奇恩惠（需19级）
    assert all(f["category"] != "传奇恩惠" for f in avail), \
        "等级4不应出现传奇恩惠专长"
    # 含通用与战斗风格两类
    cats = {f["category"] for f in avail}
    assert "通用" in cats, "应包含通用专长"
    assert "战斗风格" in cats, "应包含战斗风格专长"

    print(f"  等级4可选专长数: {len(avail)}")
    print(f"  分类: {cats}")
    print("  PASS")


def test_select_feat_updates_feats_json():
    """选择专长后 Character.feats_json 应更新。"""
    print("\n[Test 2] 选择专长后 feats_json 更新...")

    # 使用临时数据库
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = f"sqlite:///{tmp.name}"
    try:
        # 直接用模型创建角色（绕过 store 的默认 DB 路径）
        ch = models.Character(name="专长测试角色",
                              race="人类",
                              char_class="战士",
                              level=4,
                              campaign_id=None)
        ch.set_abilities({"str": 16, "dex": 12, "con": 14,
                          "int": 10, "wis": 10, "cha": 10})
        ch.hp_max = 30; ch.hp_current = 30; ch.ac = 16; ch.speed = 30
        ch = store.save_character(ch, db)
        cid = ch.id

        # 初始 feats_json 应为空列表
        loaded_before = store.get_character(cid, db)
        assert loaded_before.feats == [], \
            f"初始专长列表应为空，实为{loaded_before.feats}"

        # 通过 select_feat 选择「演员」（通用，非复选）
        char_dict = {"level": loaded_before.level,
                     "feats": list(loaded_before.feats)}
        result = lu.select_feat(char_dict, "演员")
        assert result["feat"] == "演员"
        assert "演员" in result["feats"]

        # 同步回 Character 并持久化
        loaded_before.set_feats(result["feats"])
        store.save_character(loaded_before, db)

        # 重新加载验证 feats_json 已更新
        loaded_after = store.get_character(cid, db)
        assert "演员" in loaded_after.feats, \
            f"feats_json 未更新，实为{loaded_after.feats_json}"
        assert loaded_after.feats == ["演员"], \
            f"专长列表应为['演员']，实为{loaded_after.feats}"

        print(f"  选择前 feats_json: {loaded_before.feats_json}")
        print(f"  选择后 feats_json: {loaded_after.feats_json}")
        print("  PASS")
    finally:
        eng = store._engines.pop(db, None)
        if eng is not None:
            eng.dispose()
        try:
            os.unlink(tmp.name)
        except PermissionError:
            pass


def test_no_duplicate_non_repeatable_feat():
    """非复选专长不可重复选择。"""
    print("\n[Test 3] 非复选专长不可重复选择...")

    # 「演员」是通用专长，repeatable=False
    char = {"level": 4, "feats": []}

    # 第一次选择成功
    r1 = lu.select_feat(char, "演员")
    assert r1["feat"] == "演员"
    assert char["feats"] == ["演员"]

    # 第二次选择同一非复选专长应报错
    try:
        lu.select_feat(char, "演员")
        assert False, "非复选专长重复选择应抛出 ValueError"
    except ValueError as e:
        assert "不可重复选择" in str(e) or "重复" in str(e), \
            f"错误信息应提及不可重复，实为: {e}"

    print(f"  角色专长列表: {char['feats']}")
    print("  PASS")


def test_repeatable_feat_can_be_reselected():
    """复选专长可被标记为已选但仍允许查询（不追加重复条目）。"""
    print("\n[Test 4] 复选专长处理...")

    # 「属性值提升」是通用专长，repeatable=True
    char = {"level": 4, "feats": ["属性值提升"]}

    # 复选专长已被选取 → already_taken=True，不追加
    r = lu.select_feat(char, "属性值提升")
    assert r["already_taken"] is True
    assert char["feats"].count("属性值提升") == 1, \
        "复选专长不应追加重复条目"

    print(f"  角色专长列表: {char['feats']}")
    print("  PASS")


def test_api_endpoints_e2e():
    """API 端点端到端测试。"""
    print("\n[Test 5] API 端点端到端测试...")

    from fastapi.testclient import TestClient
    from aidm.api.main import app

    # 使用临时数据库
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = f"sqlite:///{tmp.name}"
    try:
        # Monkey-patch store 的默认 DB 路径
        original_default = store.DEFAULT_DB
        store.DEFAULT_DB = db
        # 清除引擎缓存以使用新的 DB
        store._engines.clear()

        client = TestClient(app)

        # 创建一个4级角色
        resp = client.post("/character", json={
            "name": "API测试角色",
            "race": "人类",
            "char_class": "战士",
            "level": 4,
            "abilities": {"str": 16, "dex": 12, "con": 14,
                          "int": 10, "wis": 10, "cha": 10},
            "hp_max": 30,
            "ac": 16,
            "speed": 30,
        })
        assert resp.status_code == 200, f"创建角色失败: {resp.text}"
        cid = resp.json()["id"]
        print(f"  创建角色 id={cid}")

        # GET available-feats
        resp2 = client.get(f"/character/{cid}/available-feats")
        assert resp2.status_code == 200, f"获取可选专长失败: {resp2.text}"
        data2 = resp2.json()
        assert data2["level"] == 4
        assert data2["feat_available"] is True
        assert data2["count"] > 0
        print(f"  可选专长数: {data2['count']}")

        # POST select-feat
        resp3 = client.post(f"/character/{cid}/select-feat", json={
            "feat_name": "演员"
        })
        assert resp3.status_code == 200, f"选择专长失败: {resp3.text}"
        data3 = resp3.json()
        assert data3["feat"] == "演员"
        assert "演员" in data3["feats"]
        print(f"  选择后专长列表: {data3['feats']}")

        # 再次选择同一非复选专长应返回 error
        resp4 = client.post(f"/character/{cid}/select-feat", json={
            "feat_name": "演员"
        })
        assert resp4.status_code == 200
        assert "error" in resp4.json(), "重复选择非复选专长应返回 error"
        print(f"  重复选择返回: {resp4.json()['error']}")

        # 恢复 store 默认值
        store.DEFAULT_DB = original_default
        store._engines.clear()
        print("  PASS")
    finally:
        eng = store._engines.pop(db, None)
        if eng is not None:
            eng.dispose()
        try:
            os.unlink(tmp.name)
        except PermissionError:
            pass


def main():
    print("=" * 60)
    print("专长选择集成测试 — PHB 2024 第五章「专长」")
    print("=" * 60)

    test_available_feats_at_level_4()
    test_select_feat_updates_feats_json()
    test_no_duplicate_non_repeatable_feat()
    test_repeatable_feat_can_be_reselected()
    test_api_endpoints_e2e()

    print("\n" + "=" * 60)
    print("全部测试通过 ✓")
    print("=" * 60)


if __name__ == "__main__":
    main()
