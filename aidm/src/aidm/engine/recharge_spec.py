"""通用资源恢复规格 — RechargeSpec。

REST-003: 所有ResourcePool声明recharge_on与恢复量；
RestCompleted按规则查询并生成事件。
规则依据: topics/玩家手册2024/进行游戏/休息.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class RechargeTrigger(str, Enum):
    """资源恢复时机。"""

    SHORT_REST = "short_rest"
    LONG_REST = "long_rest"
    DAWN = "dawn"          # 黎明（通常等于长休后）
    ROUND_START = "round_start"
    TURN_START = "turn_start"
    NEVER = "never"


@dataclass
class RechargeSpec:
    """单个资源的恢复规格。

    REST-003: 统一资源恢复机制。
    """

    recharge_on: RechargeTrigger = RechargeTrigger.NEVER
    restore_amount: int = 0       # 恢复数量；0=恢复全部
    max_value: int = 0            # 最大值上限

    def compute_restore(self, current: int) -> int:
        """计算恢复后的值。"""
        if self.restore_amount == 0:
            return self.max_value
        return min(self.max_value, current + self.restore_amount)


@dataclass
class ResourcePool:
    """资源池 — 管理可消耗能力。

    REST-003: 所有ResourcePool声明recharge_on与恢复量。
    """

    name: str                     # 资源名（如"狂暴"、"气"）
    current: int = 0              # 当前剩余
    max_value: int = 0            # 最大值
    recharge_spec: RechargeSpec = field(default_factory=RechargeSpec)

    def can_spend(self, amount: int = 1) -> bool:
        """判断是否有足够资源。"""
        return self.current >= amount

    def spend(self, amount: int = 1) -> bool:
        """消耗资源。返回是否成功。"""
        if not self.can_spend(amount):
            return False
        self.current -= amount
        return True

    def restore(self) -> None:
        """按恢复规格恢复资源。"""
        self.current = self.recharge_spec.compute_restore(self.current)

    def to_dict(self) -> dict:
        """序列化为字典。"""
        return {
            "name": self.name,
            "current": self.current,
            "max": self.max_value,
            "recharge_on": self.recharge_spec.recharge_on.value,
            "restore_amount": self.recharge_spec.restore_amount,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResourcePool":
        """从字典反序列化。"""
        spec = RechargeSpec(
            recharge_on=RechargeTrigger(data.get("recharge_on", "never")),
            restore_amount=data.get("restore_amount", 0),
            max_value=data.get("max", 0),
        )
        return cls(
            name=data.get("name", ""),
            current=data.get("current", 0),
            max_value=data.get("max", 0),
            recharge_spec=spec,
        )


@dataclass
class ResourceManager:
    """资源管理器 — 统一管理角色所有可消耗资源。

    REST-003: RestCompleted按规则查询并生成事件。
    """

    _pools: Dict[str, Dict[str, ResourcePool]] = field(default_factory=dict)

    def register_pool(self, entity_id: str, pool: ResourcePool) -> None:
        """注册一个资源池。"""
        if entity_id not in self._pools:
            self._pools[entity_id] = {}
        self._pools[entity_id][pool.name] = pool

    def get_pool(self, entity_id: str, pool_name: str) -> ResourcePool | None:
        """获取指定实体的资源池。"""
        return self._pools.get(entity_id, {}).get(pool_name)

    def spend(self, entity_id: str, pool_name: str, amount: int = 1) -> bool:
        """消耗资源。"""
        pool = self.get_pool(entity_id, pool_name)
        if pool is None:
            return False
        return pool.spend(amount)

    def recharge_all(self, trigger: RechargeTrigger) -> List[dict]:
        """按恢复时机恢复所有实体的所有资源池。

        Returns:
            恢复事件列表
        """
        events: List[dict] = []
        for entity_id, pools in self._pools.items():
            for pool_name, pool in pools.items():
                if pool.recharge_spec.recharge_on == trigger:
                    old = pool.current
                    pool.restore()
                    if pool.current != old:
                        events.append({
                            "type": "resource_restored",
                            "entity_id": entity_id,
                            "pool": pool_name,
                            "old": old,
                            "new": pool.current,
                        })
        return events
