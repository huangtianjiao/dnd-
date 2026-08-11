"""魔法物品充能系统 — Charges / RechargeSpec / Activation。

ITEM-004: 魔法物品充能、每日恢复和激活动作统一。
规则依据: topics/玩家手册2024/装备/魔法物品.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class RechargeType(str, Enum):
    """充能恢复时机。"""

    DAWN = "dawn"           # 黎明恢复
    SHORT_REST = "short_rest"
    LONG_REST = "long_rest"
    NONE = "none"           # 不自动恢复


@dataclass
class RechargeSpec:
    """充能恢复规格。

    ITEM-004: 统一魔法物品充能恢复机制。
    """

    recharge_on: RechargeType = RechargeType.DAWN
    restore_amount: int = 0     # 恢复数量；0=恢复全部
    max_charges: int = 0        # 最大充能数

    def compute_restore(self, current: int) -> int:
        """计算恢复后的充能数。"""
        if self.restore_amount == 0:
            return self.max_charges
        return min(self.max_charges, current + self.restore_amount)


@dataclass
class ItemCharges:
    """单个魔法物品的充能状态。

    ITEM-004: 追踪魔法物品的充能、消耗和恢复。
    """

    item_id: str
    charges: int = 0
    max_charges: int = 0
    recharge_spec: Optional[RechargeSpec] = None
    consumed: bool = False       # 是否已永久消耗

    def can_use(self, cost: int = 1) -> bool:
        """判断是否有足够充能使用。"""
        return not self.consumed and self.charges >= cost

    def consume(self, amount: int = 1) -> bool:
        """消耗充能。返回是否成功。"""
        if not self.can_use(amount):
            return False
        self.charges -= amount
        return True

    def recharge(self, recharge_type: RechargeType) -> None:
        """按恢复时机恢复充能。"""
        if self.consumed:
            return
        if self.recharge_spec is None:
            return
        if self.recharge_spec.recharge_on == recharge_type:
            self.charges = self.recharge_spec.compute_restore(self.charges)


@dataclass
class ItemChargeRegistry:
    """魔法物品充能注册表 — 管理角色所有魔法物品的充能状态。

    ITEM-004: 统一管理魔法物品充能、每日恢复和激活动作。
    """

    _items: Dict[str, ItemCharges] = field(default_factory=dict)

    def register(self, item_id: str, charges: int, max_charges: int,
                 recharge_spec: Optional[RechargeSpec] = None) -> None:
        """注册一个魔法物品的充能状态。"""
        self._items[item_id] = ItemCharges(
            item_id=item_id,
            charges=charges,
            max_charges=max_charges,
            recharge_spec=recharge_spec,
        )

    def get(self, item_id: str) -> Optional[ItemCharges]:
        """获取指定物品的充能状态。"""
        return self._items.get(item_id)

    def can_activate(self, item_id: str, cost: int = 1) -> bool:
        """判断指定物品是否可以激活（有足够充能）。"""
        item = self._items.get(item_id)
        if item is None:
            return False
        return item.can_use(cost)

    def consume_charge(self, item_id: str, amount: int = 1) -> bool:
        """消耗指定物品的充能。"""
        item = self._items.get(item_id)
        if item is None:
            return False
        return item.consume(amount)

    def recharge_all(self, recharge_type: RechargeType) -> List[str]:
        """按恢复时机恢复所有物品的充能。返回已恢复的物品ID列表。"""
        recharged: List[str] = []
        for item_id, item in self._items.items():
            old_charges = item.charges
            item.recharge(recharge_type)
            if item.charges != old_charges:
                recharged.append(item_id)
        return recharged
