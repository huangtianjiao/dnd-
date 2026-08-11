"""实体状态 — EntityState 唯一权威状态与注册表。

设计原则：
  - EntityState 作为游戏中实体（角色/怪物/NPC）的唯一权威状态。
  - 所有状态变更通过 EntityStateRegistry 进行，自动维护版本号（乐观锁）。

规则依据: STATE-001 EntityState 唯一权威
"""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EntityType(str, Enum):
    """实体类型。"""

    CHARACTER = "character"
    MONSTER = "monster"
    NPC = "npc"


@dataclass
class EntityState:
    """实体唯一权威状态。

    所有游戏实体的当前状态由此对象唯一表示，
    版本号 version 用于乐观并发控制。
    """

    entity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: EntityType = EntityType.CHARACTER
    ability_scores: Dict[str, int] = field(default_factory=lambda: {
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10,
    })
    hp_current: int = 10
    hp_max: int = 10
    temp_hp: int = 0
    armor_class: int = 10
    speed: int = 30
    proficiency_bonus: int = 2
    conditions: List[str] = field(default_factory=list)
    active_effects: List[str] = field(default_factory=list)
    resource_pools: Dict[str, Any] = field(default_factory=dict)
    version: int = 0

    # ── 方法 ──────────────────────────────────────────────────────────

    def bump_version(self) -> None:
        """递增版本号（乐观锁）。"""
        self.version += 1

    def is_alive(self) -> bool:
        """判断实体是否存活（hp_current > 0）。"""
        return self.hp_current > 0

    def get_ability_modifier(self, ability: str) -> int:
        """获取属性调整值: floor((score - 10) / 2)。

        Args:
            ability: 属性名（strength/dexterity/...）

        Returns:
            属性调整值
        """
        score = self.ability_scores.get(ability)
        if score is None:
            raise ValueError(f"未知属性: {ability!r}")
        return (score - 10) // 2


class EntityStateRegistry:
    """实体状态注册表 — 管理所有 EntityState。"""

    def __init__(self) -> None:
        self._states: Dict[str, EntityState] = {}

    def get(self, entity_id: str) -> EntityState:
        """获取指定实体的状态。

        Raises:
            KeyError: 实体不存在
        """
        if entity_id not in self._states:
            raise KeyError(f"实体不存在: {entity_id}")
        return self._states[entity_id]

    def register(self, state: EntityState) -> None:
        """注册一个新实体状态。

        Raises:
            ValueError: 实体已存在
        """
        if state.entity_id in self._states:
            raise ValueError(f"实体已存在: {state.entity_id}")
        self._states[state.entity_id] = state

    def update(self, entity_id: str, **changes: Any) -> EntityState:
        """更新实体状态字段，自动 bump_version。

        Args:
            entity_id: 实体 ID
            **changes: 要更新的字段及新值

        Returns:
            更新后的 EntityState

        Raises:
            KeyError: 实体不存在
        """
        state = self.get(entity_id)
        for key, value in changes.items():
            if not hasattr(state, key):
                raise AttributeError(f"EntityState 无字段: {key}")
            setattr(state, key, value)
        state.bump_version()
        return state

    def snapshot(self, entity_id: str) -> Dict[str, Any]:
        """获取实体状态的不可变快照（深拷贝 dict）。

        Raises:
            KeyError: 实体不存在
        """
        state = self.get(entity_id)
        return copy.deepcopy(state.__dict__)
