"""聚合快照与规则缓存测试。

★ PERF-001: 每次结算可能重复加载/解析 JSON 与规则数据
"""

from __future__ import annotations

import pytest

from aidm.engine.aggregate_cache import (
    AggregateSnapshot,
    RuleDefinitionCache,
    load_aggregate_snapshot,
)


class TestAggregateSnapshot:
    """PERF-001: 聚合快照。"""

    def test_snapshot_creation(self):
        """快照可以创建并包含所有字段。"""
        snapshot = AggregateSnapshot(
            character_id="123",
            campaign_id="456",
            character_data={"name": "测试角色"},
            spell_slots={1: 2, 2: 0},
            conditions=["中毒"],
            inventory=["长剑", "盾牌"],
        )

        assert snapshot.character_id == "123"
        assert snapshot.campaign_id == "456"
        assert snapshot.character_data["name"] == "测试角色"
        assert snapshot.spell_slots[1] == 2
        assert "中毒" in snapshot.conditions
        assert "长剑" in snapshot.inventory


class TestRuleDefinitionCache:
    """PERF-001: 规则定义缓存按 manifest 版本。"""

    def test_cache_hit_and_miss(self):
        """缓存命中和未命中统计正确。"""
        cache = RuleDefinitionCache()
        cache.put("2024.1", "fireball", {"damage": "8d6"})

        # 命中
        result = cache.get("2024.1", "fireball")
        assert result is not None
        assert result["damage"] == "8d6"

        # 未命中（不存在的 key）
        cache.get("2024.1", "nonexistent")

        stats = cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] >= 1

    def test_different_revisions_isolated(self):
        """不同版本的缓存相互隔离。"""
        cache = RuleDefinitionCache()
        cache.put("2024.1", "fireball", {"damage": "8d6"})
        cache.put("2024.2", "fireball", {"damage": "10d6"})

        v1 = cache.get("2024.1", "fireball")
        v2 = cache.get("2024.2", "fireball")

        assert v1["damage"] == "8d6"
        assert v2["damage"] == "10d6"

    def test_invalidate_specific_revision(self):
        """使特定版本缓存失效。"""
        cache = RuleDefinitionCache()
        cache.put("2024.1", "key1", "value1")
        cache.put("2024.2", "key2", "value2")

        cache.invalidate("2024.1")

        assert cache.get("2024.1", "key1") is None
        assert cache.get("2024.2", "key2") is not None

    def test_invalidate_all(self):
        """清空所有缓存。"""
        cache = RuleDefinitionCache()
        cache.put("2024.1", "key1", "value1")
        cache.put("2024.2", "key2", "value2")

        cache.invalidate()

        assert cache.get("2024.1", "key1") is None
        assert cache.get("2024.2", "key2") is None
