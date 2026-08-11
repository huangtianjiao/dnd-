"""聚合快照与规则定义缓存。

设计原则：
  - 命令开始时加载聚合快照，结算内使用内存对象，提交一次。
  - 规则定义缓存按 manifest 版本，避免重复解析 JSON。

规则依据: PERF-001 每次结算可能重复加载/解析 JSON 与规则数据
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

_log = logging.getLogger(__name__)


@dataclass
class AggregateSnapshot:
    """一次命令的聚合快照。

    在命令开始时一次性加载所有需要的状态，
    结算过程中在内存中操作，最后一次性提交。

    属性:
        character_id: 角色 ID
        campaign_id: 战役 ID
        character_data: 角色完整数据（从 DB 加载）
        combat_data: 战斗状态数据（如果有）
        scene_data: 场景数据
        spell_slots: 法术位快照 {slot_level: remaining}
        conditions: 状态条件快照
        inventory: 物品栏快照
        version: 快照版本号（乐观锁）
    """
    character_id: str = ""
    campaign_id: str = ""
    character_data: Dict[str, Any] = field(default_factory=dict)
    combat_data: Optional[Dict[str, Any]] = None
    scene_data: Optional[Dict[str, Any]] = None
    spell_slots: Dict[int, int] = field(default_factory=dict)
    conditions: list = field(default_factory=list)
    inventory: list = field(default_factory=list)
    version: int = 0


class RuleDefinitionCache:
    """规则定义缓存 — 按 manifest 版本缓存。

    避免每次结算都重新解析 JSON 规则文件。
    缓存键为 manifest revision，确保不同版本的规则不会混淆。

    规则依据: PERF-001 规则定义缓存按 manifest 版本
    """

    def __init__(self) -> None:
        self._cache: Dict[str, Dict[str, Any]] = {}  # revision → {key: value}
        self._hit_count: int = 0
        self._miss_count: int = 0

    def get(self, revision: str, key: str) -> Optional[Any]:
        """从缓存获取规则定义。

        Args:
            revision: manifest 版本号
            key: 规则定义的键

        Returns:
            缓存的规则定义，如果未缓存则返回 None
        """
        rev_cache = self._cache.get(revision)
        if rev_cache is None:
            self._miss_count += 1
            return None
        value = rev_cache.get(key)
        if value is not None:
            self._hit_count += 1
        else:
            self._miss_count += 1
        return value

    def put(self, revision: str, key: str, value: Any) -> None:
        """将规则定义放入缓存。

        Args:
            revision: manifest 版本号
            key: 规则定义的键
            value: 规则定义的值
        """
        if revision not in self._cache:
            self._cache[revision] = {}
        self._cache[revision][key] = value

    def invalidate(self, revision: str = "") -> None:
        """使缓存失效。

        Args:
            revision: 指定版本号失效，空字符串则清空所有缓存
        """
        if revision:
            self._cache.pop(revision, None)
        else:
            self._cache.clear()

    def stats(self) -> Dict[str, int]:
        """获取缓存统计信息。"""
        return {
            "hits": self._hit_count,
            "misses": self._miss_count,
            "revisions": len(self._cache),
            "entries": sum(len(v) for v in self._cache.values()),
        }


# 全局规则定义缓存实例
_rule_cache = RuleDefinitionCache()


def get_rule_cache() -> RuleDefinitionCache:
    """获取全局规则定义缓存实例。"""
    return _rule_cache


def load_aggregate_snapshot(
    character_id: str,
    campaign_id: str,
    db_path: str = "",
) -> AggregateSnapshot:
    """加载聚合快照。

    ★ PERF-001: 命令开始时加载聚合快照，结算内使用内存对象。

    Args:
        character_id: 角色 ID
        campaign_id: 战役 ID
        db_path: 数据库路径

    Returns:
        聚合快照
    """
    snapshot = AggregateSnapshot(
        character_id=character_id,
        campaign_id=campaign_id,
    )

    # 从 DB 加载角色数据
    try:
        from ..stats import store as _store
        ch = _store.get_character(int(character_id))
        if ch:
            snapshot.character_data = {
                "id": ch.id,
                "name": ch.name,
                "char_class": ch.char_class,
                "level": ch.level,
                "hp_current": ch.hp_current,
                "hp_max": ch.hp_max,
                "ac": ch.ac,
                "speed": ch.speed,
                "abilities": ch.abilities,
                "spell_slots": ch.spell_slots,
                "known_spells": ch.known_spells,
                "conditions_list": ch.conditions_list,
                "inventory": ch.inventory,
                "equipped_weapon": ch.equipped_weapon,
                "equipped_armor": ch.equipped_armor,
                "exhaustion": ch.exhaustion,
                "temp_hp": ch.temp_hp,
            }
            snapshot.version = ch.id  # 简化版：用 ID 作为版本
    except Exception as e:
        _log.debug("加载聚合快照失败 cid=%s: %s", character_id, e)

    return snapshot
