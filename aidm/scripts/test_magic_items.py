"""魔法物品系统 — 综合自检测试。

测试覆盖:
  1. 魔法物品数据库 (data/magic_items.py)
  2. Character模型扩展 (stats/models.py attuned_items_json)
  3. 战利品系统 (brain/loot.py)
  4. API端点逻辑 (api/main.py)

运行方式:
  PYTHONPATH=src python scripts/test_magic_items.py
"""

import os
import sys
import tempfile

# 确保使用项目src目录
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_magic_items_database():
    """测试魔法物品数据库。"""
    from aidm.data import magic_items as mi

    # 1. 数据量：至少20个物品
    assert len(mi.MAGIC_ITEMS) >= 20, f"物品数不足: {len(mi.MAGIC_ITEMS)}"
    print(f"  物品总数: {len(mi.MAGIC_ITEMS)}")

    # 2. 名称唯一性
    names = [item.name for item in mi._MAGIC_ITEMS_LIST]
    assert len(names) == len(set(names)), "存在重复物品名称"
    assert len(mi.MAGIC_ITEMS) == len(mi._MAGIC_ITEMS_LIST), "索引字典大小不匹配"

    # 3. 每个物品都有必填字段
    for item in mi._MAGIC_ITEMS_LIST:
        assert item.name, f"物品缺少名称: {item}"
        assert item.name_en, f"物品缺少英文名: {item.name}"
        assert isinstance(item.rarity, mi.Rarity), f"{item.name} 稀有度类型错误"
        assert isinstance(item.item_type, mi.ItemType), f"{item.name} 类别类型错误"
        assert item.description, f"{item.name} 缺少描述"
        assert item.source, f"{item.name} 缺少出处"
        if item.attunement_req:
            assert item.attunement, f"{item.name} 有同调要求但attunement=False"

    # 4. 查询函数
    sword = mi.get_magic_item("触月剑")
    assert sword is not None and sword.rarity == mi.Rarity.COMMON
    assert sword.item_type == mi.ItemType.WEAPON

    cursed = mi.list_magic_items(cursed_only=True)
    assert len(cursed) >= 1, "应至少有1个诅咒物品"
    assert all(item.cursed for item in cursed), "cursed_only结果包含非诅咒物品"

    weapons = mi.items_by_type(mi.ItemType.WEAPON)
    assert len(weapons) >= 5, f"武器物品不足: {len(weapons)}"
    assert all(item.item_type == mi.ItemType.WEAPON for item in weapons)

    common_items = mi.items_by_rarity(mi.Rarity.COMMON)
    assert len(common_items) >= 10, f"普通物品不足: {len(common_items)}"
    assert all(item.rarity == mi.Rarity.COMMON for item in common_items)

    # 5. 价格计算
    # 普通武器：100gp基础
    assert sword.price_gp == 100, f"触月剑价格应为100gp，实际{sword.price_gp}"
    # 药水是消耗品，价格减半：攀爬药水(普通)=100/2=50gp
    potion = mi.get_magic_item("攀爬药水")
    assert potion.price_gp == 50, f"攀爬药水价格应为50gp，实际{potion.price_gp}"
    # 珍稀药水：4000/2=2000gp
    invis_potion = mi.get_magic_item("隐身药水")
    assert invis_potion.price_gp == 2000, f"隐身药水价格应为2000gp，实际{invis_potion.price_gp}"

    # 6. 随机抽取
    random_items = mi.random_magic_items(count=3, seed=42)
    assert len(random_items) == 3, "随机抽取数量不符"
    assert len(set(item.name for item in random_items)) == 3, "随机抽取不应有重复"

    # 可复现性
    random_items2 = mi.random_magic_items(count=3, seed=42)
    assert [item.name for item in random_items] == [item.name for item in random_items2], \
        "相同种子应产生相同结果"

    # 稀有度筛选
    common_random = mi.random_magic_items(count=5, max_rarity=mi.Rarity.COMMON, seed=123)
    assert all(item.rarity == mi.Rarity.COMMON for item in common_random), \
        "max_rarity=COMMON应只返回普通物品"

    # 7. 序列化
    d = sword.to_dict()
    assert d["name"] == "触月剑"
    assert d["rarity"] == "普通"
    assert d["item_type"] == "武器"
    assert d["price_gp"] == 100
    assert "武器/普通.htm" in d["source"]

    # 8. 稀有度枚举属性
    assert mi.Rarity.COMMON.base_price_gp == 100
    assert mi.Rarity.LEGENDARY.base_price_gp == 200000
    assert mi.Rarity.ARTIFACT.base_price_gp == 0
    assert mi.Rarity.COMMON.sort_order < mi.Rarity.ARTIFACT.sort_order

    # 9. 类别覆盖：至少覆盖武器/护甲/药水/戒指/法杖/奇物
    covered_types = set(item.item_type for item in mi._MAGIC_ITEMS_LIST)
    expected_types = {mi.ItemType.WEAPON, mi.ItemType.ARMOR, mi.ItemType.POTION,
                      mi.ItemType.RING, mi.ItemType.STAFF, mi.ItemType.WONDROUS_ITEM}
    missing = expected_types - covered_types
    assert not missing, f"缺少类别覆盖: {[t.value for t in missing]}"

    # 10. 稀有度覆盖：至少覆盖普通/非普通/珍稀
    covered_rarities = set(item.rarity for item in mi._MAGIC_ITEMS_LIST)
    expected_rarities = {mi.Rarity.COMMON, mi.Rarity.UNCOMMON, mi.Rarity.RARE}
    missing_r = expected_rarities - covered_rarities
    assert not missing_r, f"缺少稀有度覆盖: {[r.value for r in missing_r]}"

    print("  [OK] 魔法物品数据库")


def test_character_model_extension():
    """测试Character模型的attuned_items_json字段。"""
    from aidm.stats import models

    # 创建临时数据库
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = f"sqlite:///{tmp.name}"

    try:
        from aidm.stats import store
        store.get_engine(db)

        # 创建角色
        ch = models.Character(name="测试法师", race="人类", char_class="法师", level=5)
        ch = store.save_character(ch, db)
        cid = ch.id

        # 默认值应为空列表
        loaded = store.get_character(cid, db)
        assert loaded.attuned_items == [], f"默认应为空列表，实际{loaded.attuned_items}"

        # 设置已同调物品
        loaded.set_attuned_items(["跳跃戒指", "心灵护盾戒指"])
        store.save_character(loaded, db)

        # 重载验证
        reloaded = store.get_character(cid, db)
        assert reloaded.attuned_items == ["跳跃戒指", "心灵护盾戒指"], \
            f"同调物品持久化失败: {reloaded.attuned_items}"

        # 上限检查：超过3件应报错
        try:
            reloaded.set_attuned_items(["a", "b", "c", "d"])
            assert False, "设置超过3件同调物品应抛出ValueError"
        except ValueError:
            pass  # 预期行为

        print("  [OK] Character模型扩展")
    finally:
        try:
            os.unlink(tmp.name)
        except PermissionError:
            pass


def test_loot_system():
    """测试战利品系统。"""
    from aidm.brain import loot
    from aidm.data.magic_items import Rarity

    # ═══ 1. CR映射 ═══
    assert loot.cr_to_loot_tier(0) == "low"
    assert loot.cr_to_loot_tier(0.5) == "low"
    assert loot.cr_to_loot_tier(4) == "low"
    assert loot.cr_to_loot_tier(5) == "mid"
    assert loot.cr_to_loot_tier(10) == "mid"
    assert loot.cr_to_loot_tier(11) == "high"
    assert loot.cr_to_loot_tier(17) == "top"

    # ═══ 2. 战利品生成 ═══
    low_pool = loot.generate_loot(cr=2, seed=42)
    assert low_pool.source_tier == "low"
    assert low_pool.gold > 0, "金币应大于0"
    assert low_pool.gold >= 50, f"低级金币应≥50，实际{low_pool.gold}"
    for item in low_pool.magic_items:
        assert item.rarity.sort_order <= Rarity.UNCOMMON.sort_order, \
            f"低级战利品不应有高于非普通的物品: {item.name}({item.rarity.value})"

    top_pool = loot.generate_loot(cr=20, seed=42)
    assert top_pool.source_tier == "top"
    assert top_pool.gold >= 3000, f"顶级金币应≥3000，实际{top_pool.gold}"

    pool1 = loot.generate_loot(cr=5, seed=100)
    pool2 = loot.generate_loot(cr=5, seed=100)
    assert pool1.gold == pool2.gold, "相同种子应产生相同金币"
    assert len(pool1.magic_items) == len(pool2.magic_items), "相同种子应产生相同物品数"

    no_mi_pool = loot.generate_loot(cr=10, include_magic_items=False, seed=42)
    assert len(no_mi_pool.magic_items) == 0, "include_magic_items=False不应有魔法物品"

    single = loot.generate_loot(cr=5, seed=42)
    multi = loot.generate_loot(cr=5, count_enemies=5, seed=42)
    assert multi.gold > single.gold, "多敌人应增加金币"

    # ═══ 3. 战利品池属性 ═══
    pool = loot.generate_loot(cr=8, seed=42)
    assert pool.total_value_gp >= pool.gold, "总价值应≥金币"
    assert isinstance(pool.to_dict(), dict)
    assert "gold" in pool.to_dict()
    assert "magic_items" in pool.to_dict()

    # ═══ 4. 战利品分配 ═══
    players = ["阿拉贡", "莱戈拉斯", "吉姆利"]

    from aidm.data.magic_items import get_magic_item
    test_pool = loot.LootPool(
        gold=300,
        magic_items=[
            get_magic_item("触月剑"),
            get_magic_item("跳跃戒指"),
            get_magic_item("闪烁甲"),
        ],
    )
    needs = {
        "阿拉贡": ["触月剑"],
        "莱戈拉斯": ["跳跃戒指", "闪烁甲"],
    }
    dist = loot.distribute_loot(test_pool, players, method="need_priority",
                                needs=needs, seed=42)
    assert "触月剑" in dist.assignments.get("阿拉贡", []), "阿拉贡应获得触月剑"
    assert "跳跃戒指" in dist.assignments.get("莱戈拉斯", []), "莱戈拉斯应获得跳跃戒指"

    dist_rr = loot.distribute_loot(test_pool, players, method="round_robin", seed=42)
    all_assigned = []
    for items in dist_rr.assignments.values():
        all_assigned.extend(items)
    assert len(all_assigned) == 3, f"轮流拾取应分配全部3件物品，实际{len(all_assigned)}"
    assert len(set(all_assigned)) == 3, "不应有重复分配"

    dist_pb = loot.distribute_loot(test_pool, players, method="point_bid", seed=42)
    all_assigned_pb = []
    for items in dist_pb.assignments.values():
        all_assigned_pb.extend(items)
    assert len(all_assigned_pb) == 3, "点数分配应分配全部物品"

    dm_assigns = {"吉姆利": ["触月剑", "闪烁甲"], "莱戈拉斯": ["跳跃戒指"]}
    dist_dm = loot.distribute_loot(test_pool, players, method="dm_assign",
                                   dm_assignments=dm_assigns, seed=42)
    assert "触月剑" in dist_dm.assignments.get("吉姆利", [])
    assert "跳跃戒指" in dist_dm.assignments.get("莱戈拉斯", [])

    dist_empty = loot.distribute_loot(test_pool, [], method="round_robin", seed=42)
    assert len(dist_empty.unassigned_items) == 3, "无玩家时应全部未分配"

    d = dist.to_dict()
    assert d["method"] == "need_priority"
    assert d["method_name"] == "需求优先"

    # ═══ 5. 金币分配 ═══
    gold_dist = loot.distribute_gold(300, players, method="equal")
    assert sum(gold_dist.values()) == 300, "金币总和应等于总量"
    assert gold_dist["阿拉贡"] == 100, f"300/3=100，实际{gold_dist['阿拉贡']}"

    gold_dist2 = loot.distribute_gold(301, players, method="equal")
    assert sum(gold_dist2.values()) == 301, "金币总和应等于总量"
    assert gold_dist2["阿拉贡"] == 101, "余数应给第一个玩家"

    contribs = {"阿拉贡": 50, "莱戈拉斯": 30, "吉姆利": 20}
    gold_dist3 = loot.distribute_gold(1000, players, method="contribution",
                                      contributions=contribs)
    assert sum(gold_dist3.values()) == 1000, "金币总和应等于总量"
    assert gold_dist3["阿拉贡"] > gold_dist3["吉姆利"], "贡献高的应分更多"

    gold_dist4 = loot.distribute_gold(300, players, method="contribution")
    assert gold_dist4["阿拉贡"] == 100, "无贡献数据应退回平均分配"

    assert loot.distribute_gold(0, players) == {"阿拉贡": 0, "莱戈拉斯": 0, "吉姆利": 0}
    assert loot.distribute_gold(100, []) == {}

    # ═══ 6. 同调管理 ═══
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = f"sqlite:///{tmp.name}"
    try:
        from aidm.stats import store, models
        store.get_engine(db)

        ch = models.Character(name="测试法师", race="人类", char_class="法师", level=5)
        ch = store.save_character(ch, db)
        cid = ch.id

        result = loot.attune_magic_item(cid, "跳跃戒指", db)
        assert result["success"], f"同调应成功: {result['message']}"
        assert "跳跃戒指" in result["attuned_items"]

        result2 = loot.attune_magic_item(cid, "触月剑", db)
        assert not result2["success"], "触月剑不需要同调，应失败"

        result3 = loot.attune_magic_item(cid, "不存在的物品", db)
        assert not result3["success"], "未知物品应失败"

        loot.attune_magic_item(cid, "心灵护盾戒指", db)
        loot.attune_magic_item(cid, "温暖戒指", db)
        ch_reload = store.get_character(cid, db)
        assert len(ch_reload.attuned_items) == 3, "应达到3件同调上限"

        result4 = loot.attune_magic_item(cid, "巫术帽", db)
        assert not result4["success"], "超过上限应失败"
        assert "上限" in result4["message"], f"消息应含'上限': {result4['message']}"

        result5 = loot.break_attunement(cid, "跳跃戒指", db)
        assert result5["success"], f"解除同调应成功: {result5['message']}"
        assert "跳跃戒指" not in result5["attuned_items"]
        assert len(result5["attuned_items"]) == 2

        result6 = loot.break_attunement(cid, "跳跃戒指", db)
        assert not result6["success"], "解除未同调物品应失败"

        loot.attune_magic_item(cid, "善泳戒指", db)
        result7 = loot.attune_magic_item(cid, "善泳戒指", db)
        assert not result7["success"], "重复同调应失败"
    finally:
        try:
            os.unlink(tmp.name)
        except PermissionError:
            pass

    print("  [OK] 战利品系统")


def test_api_endpoints_logic():
    """测试API端点的核心逻辑（不启动HTTP服务）。"""
    from aidm.data import magic_items as mi

    # 模拟 GET /magic-items 的逻辑
    items = mi.list_magic_items(rarity=mi.Rarity.COMMON)
    result = {"items": [item.to_dict() for item in items], "count": len(items)}
    assert result["count"] == len(items)
    assert all(item["rarity"] == "普通" for item in result["items"])

    # 模拟 GET /magic-items/{name} 的逻辑
    item = mi.get_magic_item("触月剑")
    assert item is not None
    assert item.to_dict()["name"] == "触月剑"

    # 模拟 POST /loot/generate 的逻辑
    from aidm.brain import loot
    pool = loot.generate_loot(cr=5, seed=42)
    pool_dict = pool.to_dict()
    assert "gold" in pool_dict
    assert "magic_items" in pool_dict
    assert "total_value_gp" in pool_dict

    # 模拟 POST /loot/distribute 的逻辑
    test_pool = loot.LootPool(
        gold=300,
        magic_items=[mi.get_magic_item("触月剑")],
    )
    dist = loot.distribute_loot(
        pool=test_pool,
        players=["阿拉贡", "莱戈拉斯"],
        method="round_robin",
        seed=42,
    )
    gold_dist = loot.distribute_gold(
        total_gold=300,
        players=["阿拉贡", "莱戈拉斯"],
        method="equal",
    )
    assert sum(gold_dist.values()) == 300
    assert dist.method == "round_robin"

    print("  [OK] API端点逻辑")


def main():
    """运行所有测试。"""
    print("=" * 60)
    print("魔法物品系统 — 综合自检测试")
    print("=" * 60)

    tests = [
        ("魔法物品数据库", test_magic_items_database),
        ("Character模型扩展", test_character_model_extension),
        ("战利品系统", test_loot_system),
        ("API端点逻辑", test_api_endpoints_logic),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        print(f"\n[{name}]")
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"结果: {passed}/{passed + failed} 通过")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
