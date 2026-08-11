"""物品实例 — ItemInstance / ItemStack。

ITEM-001: 物品栏只有不重复字符串列表。
ItemInstance/ItemStack分离定义与实例，支持quantity、charges、attunement、container、equipped。

规则依据: topics/玩家手册2024/装备/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ItemInstance:
    """单个物品实例。

    ITEM-001: 分离定义与实例。
    """

    instance_id: str = ""                # 唯一实例 ID
    item_id: str = ""                    # 物品定义 canonical ID
    name: str = ""                       # 显示名
    quantity: int = 1                    # 堆叠数量
    charges: int = 0                     # 充能数（魔法物品）
    max_charges: int = 0                 # 最大充能数
    equipped: bool = False               # 是否已装备
    slot: str = ""                       # 装备槽位
    attuned: bool = False                # 是否已同调
    container_id: str = ""               # 容器实例 ID（如背包）
    value_gp: float = 0.0                # 单价（GP）
    weight_lb: float = 0.0               # 单个重量（磅）

    def total_value(self) -> float:
        """总价值。"""
        return self.value_gp * self.quantity

    def total_weight(self) -> float:
        """总重量。"""
        return self.weight_lb * self.quantity


@dataclass
class ItemStack:
    """物品堆栈 — 管理同一物品的多个实例。

    ITEM-001: 支持堆叠和拆分。
    """

    item_id: str                         # 物品定义 ID
    instances: List[ItemInstance] = field(default_factory=list)

    def add_instance(self, inst: ItemInstance) -> None:
        """添加一个实例。"""
        self.instances.append(inst)

    def total_quantity(self) -> int:
        """获取总数量。"""
        return sum(i.quantity for i in self.instances)

    def split(self, count: int) -> Optional[ItemInstance]:
        """从堆栈中拆分出指定数量的新实例。"""
        if count <= 0 or count > self.total_quantity():
            return None
        for inst in self.instances:
            if inst.quantity >= count:
                inst.quantity -= count
                return ItemInstance(
                    item_id=self.item_id,
                    name=inst.name,
                    quantity=count,
                    value_gp=inst.value_gp,
                    weight_lb=inst.weight_lb,
                )
        return None


@dataclass
class InventoryManager:
    """物品栏管理器 — 统一管理角色所有物品实例。

    ITEM-001: 消耗品、弹药、堆叠和魔法物品实例可正确追踪。
    """

    _items: Dict[str, ItemInstance] = field(default_factory=dict)  # instance_id → ItemInstance

    def add_item(self, inst: ItemInstance) -> None:
        """添加一个物品实例。"""
        self._items[inst.instance_id] = inst

    def remove_item(self, instance_id: str) -> bool:
        """移除一个物品实例。"""
        return self._items.pop(instance_id, None) is not None

    def get_item(self, instance_id: str) -> Optional[ItemInstance]:
        """获取指定物品实例。"""
        return self._items.get(instance_id)

    def consume_charge(self, instance_id: str, amount: int = 1) -> bool:
        """消耗指定物品的充能。"""
        inst = self._items.get(instance_id)
        if inst is None or inst.charges < amount:
            return False
        inst.charges -= amount
        return True

    def equip(self, instance_id: str, slot: str) -> bool:
        """装备物品到指定槽位。"""
        inst = self._items.get(instance_id)
        if inst is None:
            return False
        inst.equipped = True
        inst.slot = slot
        return True

    def unequip(self, instance_id: str) -> bool:
        """卸下物品。"""
        inst = self._items.get(instance_id)
        if inst is None:
            return False
        inst.equipped = False
        inst.slot = ""
        return True

    def list_all(self) -> List[ItemInstance]:
        """列出所有物品实例。"""
        return list(self._items.values())
