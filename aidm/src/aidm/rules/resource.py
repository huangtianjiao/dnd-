"""ResourcePool — 资源池管理（气、狂暴、吟唱激励等）"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PoolType(str, Enum):
    """资源池类型"""

    REGEN = "regen"  # 可回复（如气、狂暴次数）
    CONSUMABLE = "consumable"  # 消耗型（如治疗真言次数）


class ResourceType(str, Enum):
    """资源用途类型"""

    RAGE = "rage"
    KI = "ki"
    BARDIC_INSPIRATION = "bardic_inspiration"
    CHANNEL_DIVINITY = "channel_divinity"
    SORCERY_POINTS = "sorcery_points"
    LAY_ON_HANDS = "lay_on_hands"
    SECOND_WIND = "second_wind"
    ACTION_SURGE = "action_surge"
    SUPERIORITY_DICE = "superiority_dice"
    WILD_SHAPE = "wild_shape"
    ARCANE_RECOVERY = "arcane_recovery"
    GENERAL = "general"


@dataclass
class SpendResult:
    """spend() 操作的返回结果"""

    success: bool
    remaining: int
    spent: int = 0
    message: str = ""


@dataclass
class ResourcePool:
    """资源池"""

    name: str
    max_value: int
    current_value: int
    recharge_on: str = ""  # "short_rest" / "long_rest" / "dawn"
    source_feature_id: str = ""
    pool_type: str = PoolType.REGEN.value  # "regen" / "consumable"
    resource_type: str = ResourceType.GENERAL.value  # 资源用途类型

    def spend(self, amount: int = 1) -> SpendResult:
        """消耗资源，返回 SpendResult"""
        if amount <= 0:
            return SpendResult(success=False, remaining=self.current_value, message="消耗量必须大于0")
        if self.current_value < amount:
            return SpendResult(
                success=False,
                remaining=self.current_value,
                message=f"资源不足: 需要 {amount}, 剩余 {self.current_value}",
            )
        self.current_value -= amount
        return SpendResult(success=True, remaining=self.current_value, spent=amount)

    def restore(self, amount: int = -1) -> int:
        """恢复资源。-1 表示完全恢复。返回实际恢复量"""
        if amount < 0:
            restored = self.max_value - self.current_value
            self.current_value = self.max_value
        else:
            restored = min(amount, self.max_value - self.current_value)
            self.current_value += restored
        return restored

    def reset(self) -> None:
        """重置为满"""
        self.current_value = self.max_value

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "max_value": self.max_value,
            "current_value": self.current_value,
            "recharge_on": self.recharge_on,
            "source_feature_id": self.source_feature_id,
            "pool_type": self.pool_type,
            "resource_type": self.resource_type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResourcePool":
        return cls(
            name=data["name"],
            max_value=data["max_value"],
            current_value=data.get("current_value", data["max_value"]),
            recharge_on=data.get("recharge_on", ""),
            source_feature_id=data.get("source_feature_id", ""),
            pool_type=data.get("pool_type", PoolType.REGEN.value),
            resource_type=data.get("resource_type", ResourceType.GENERAL.value),
        )


class ResourceManager:
    """管理所有实体的资源池"""

    def __init__(self) -> None:
        self._pools: Dict[str, Dict[str, ResourcePool]] = {}  # entity_id -> {pool_name -> pool}

    def create_pool(self, entity_id: str, pool: ResourcePool) -> None:
        """为实体创建一个资源池"""
        self._pools.setdefault(entity_id, {})
        self._pools[entity_id][pool.name] = pool

    def remove_pool(self, entity_id: str, pool_name: str) -> bool:
        """移除资源池"""
        pools = self._pools.get(entity_id, {})
        return pools.pop(pool_name, None) is not None

    def spend(self, entity_id: str, pool_name: str, amount: int = 1) -> SpendResult:
        """消耗资源"""
        pool = self.get_pool(entity_id, pool_name)
        if pool is None:
            return SpendResult(success=False, remaining=0, message=f"资源池 '{pool_name}' 不存在")
        return pool.spend(amount)

    def restore(self, entity_id: str, pool_name: str, amount: int = -1) -> int:
        """恢复资源"""
        pool = self.get_pool(entity_id, pool_name)
        if pool is None:
            return 0
        return pool.restore(amount)

    def recharge_all(self, entity_id: str, recharge_type: str) -> List[str]:
        """按休息类型回复所有匹配的资源池，返回被回复的池名列表"""
        recharged: List[str] = []
        for name, pool in self._pools.get(entity_id, {}).items():
            if pool.recharge_on == recharge_type:
                pool.reset()
                recharged.append(name)
        return recharged

    def get_pool(self, entity_id: str, pool_name: str) -> Optional[ResourcePool]:
        """获取指定资源池"""
        return self._pools.get(entity_id, {}).get(pool_name)

    def get_pools(self, entity_id: str) -> Dict[str, ResourcePool]:
        """获取实体所有资源池"""
        return dict(self._pools.get(entity_id, {}))

    def get_pools_by_type(self, entity_id: str, resource_type: str) -> List[ResourcePool]:
        """按 resource_type 获取资源池列表"""
        return [
            p
            for p in self._pools.get(entity_id, {}).values()
            if p.resource_type == resource_type
        ]

    def clear(self, entity_id: str) -> None:
        """清除实体所有资源池"""
        self._pools.pop(entity_id, None)
