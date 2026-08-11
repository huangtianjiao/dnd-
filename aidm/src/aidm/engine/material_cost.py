"""有价/消耗材料真实扣除 — MaterialCost。

SPL-012: 有价/消耗材料不会真实扣除。
材料需求引用item/tag、最低价值、数量、是否消耗；验证与扣除在同一事务。

规则依据: topics/玩家手册2024/法术/法术成分.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MaterialRequirement:
    """施法材料需求。

    SPL-012: 材料需求引用 item/tag、最低价值、数量、是否消耗。
    """

    item_tag: str = ""              # 物品标签（如"硫磺"）
    min_value_gp: float = 0.0      # 最低价值（GP）
    quantity: int = 1               # 所需数量
    consumed: bool = False          # 是否消耗


@dataclass
class MaterialTracker:
    """材料追踪器 — 管理角色的施法材料。

    SPL-012: 验证与扣除在同一事务。
    """

    _inventory: Dict[str, int] = field(default_factory=dict)  # item_tag → quantity

    def add_material(self, item_tag: str, quantity: int = 1) -> None:
        """添加材料。"""
        self._inventory[item_tag] = self._inventory.get(item_tag, 0) + quantity

    def has_material(self, req: MaterialRequirement) -> bool:
        """检查是否拥有所需材料。

        SPL-012: 支持精确匹配与子串匹配——
        材料需求可能引用完整材料描述（如"一颗珍珠（价值100gp）与一根猫头鹰羽毛"），
        而库存中存储的是短 tag（如"珍珠"）。任一方向子串匹配即视为持有。
        """
        if not req.item_tag:
            return True  # 无材料需求
        need = req.item_tag
        # 精确匹配
        if self._inventory.get(need, 0) >= req.quantity:
            return True
        # 子串匹配：库存中的任一 tag 是需求描述的子串，或需求描述是 tag 的子串
        for tag, qty in self._inventory.items():
            if tag and qty >= req.quantity:
                if need in tag or tag in need:
                    return True
        return False

    def consume_material(self, req: MaterialRequirement) -> bool:
        """消耗材料（原子操作）。

        SPL-012: 验证与扣除在同一事务；子串匹配到的库存项被扣减。
        """
        if not req.consumed:
            return True  # 不消耗
        if not self.has_material(req):
            return False
        # 优先精确匹配，其次子串匹配
        if self._inventory.get(req.item_tag, 0) >= req.quantity:
            self._inventory[req.item_tag] -= req.quantity
            return True
        for tag in self._inventory:
            if tag and (req.item_tag in tag or tag in req.item_tag) \
                    and self._inventory[tag] >= req.quantity:
                self._inventory[tag] -= req.quantity
                return True
        return False

    def get_quantity(self, item_tag: str) -> int:
        """获取指定材料的数量。"""
        return self._inventory.get(item_tag, 0)
