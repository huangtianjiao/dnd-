"""性能缓存 — AggregateCache。

PERF-001: 每次结算可能重复加载/解析JSON与规则数据。
命令开始加载聚合快照，结算内使用内存对象，提交一次；规则定义缓存按manifest版本。

规则依据: topics/城主指南2024/2.运作游戏/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class CharacterSnapshot:
    """角色聚合快照 — 包含结算所需的全部数据。

    PERF-001: 命令开始加载聚合快照，结算内使用内存对象。
    """

    character_id: str = ""
    name: str = ""
    level: int = 1
    char_class: str = ""
    subclass: str = ""

    # 属性
    abilities: Dict[str, int] = field(default_factory=dict)

    # HP
    hp_current: int = 0
    hp_max: int = 0
    temp_hp: int = 0

    # AC
    ac: int = 10

    # 法术位
    spell_slots: Dict[int, int] = field(default_factory=dict)

    # 已知法术
    known_spells: list[str] = field(default_factory=list)

    # 物品栏
    inventory: list[str] = field(default_factory=list)
    equipped_weapon: str = ""
    equipped_armor: str = ""

    # 状态
    conditions: list[str] = field(default_factory=list)
    exhaustion: int = 0

    # 专注
    concentration_spell: str = ""

    # 装备槽
    equipment_slots: Dict[str, str] = field(default_factory=dict)


@dataclass
class CombatSnapshot:
    """战斗聚合快照。"""

    campaign_id: str = ""
    active: bool = False
    round: int = 1
    current_index: int = 0
    combatants: list[dict] = field(default_factory=list)


@dataclass
class SceneSnapshot:
    """场景聚合快照。"""

    campaign_id: str = ""
    location: str = ""
    environment: str = ""
    time: str = ""
    npcs: list[dict] = field(default_factory=list)
    situation: str = ""


@dataclass
class AggregateSnapshot:
    """完整聚合快照 — 角色卡 + 战斗 + 场景。

    PERF-001: 结算内使用内存对象，提交一次。
    """

    character: Optional[CharacterSnapshot] = None
    combat: Optional[CombatSnapshot] = None
    scene: Optional[SceneSnapshot] = None
    campaign_id: str = ""
    ruleset_id: str = "dnd5e_2024_core"
    ruleset_revision: str = "2024.1"


class RuleDefinitionCache:
    """规则定义缓存 — 按 manifest 版本缓存。

    PERF-001: 规则定义缓存按manifest版本。
    """

    def __init__(self) -> None:
        self._cache: Dict[str, Any] = {}
        self._version: str = ""

    def set_version(self, version: str) -> None:
        """设置当前规则集版本。"""
        if version != self._version:
            self._cache.clear()
            self._version = version

    def get(self, key: str) -> Any:
        """获取缓存的规则定义。"""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """缓存一个规则定义。"""
        self._cache[key] = value

    def clear(self) -> None:
        """清空缓存。"""
        self._cache.clear()


# ── 全局缓存单例 ──────────────────────────────────────────────

_rule_cache = RuleDefinitionCache()


def get_rule_cache() -> RuleDefinitionCache:
    """获取全局规则定义缓存。"""
    return _rule_cache
