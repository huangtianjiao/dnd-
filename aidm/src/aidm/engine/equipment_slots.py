"""引擎层装备槽管理 — EquipmentSlotsManager。

设计原则：
  - 引擎层的装备管理，与 stats/models.py 的持久化层互补。
  - 管理实体的装备槽位（主手、副手、护甲、法器、穿戴）。
  - 提供施法成分检查、手部空闲检测等功能。

规则依据: COM-006 引擎层装备槽
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SlotType(str, Enum):
    """装备槽类型。"""

    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    ARMOR = "armor"
    FOCUS = "focus"
    WORN = "worn"


@dataclass
class ItemInstance:
    """物品实例。"""

    item_id: str
    name: str = ""
    quantity: int = 1
    charges: int = -1               # -1 = unlimited
    attuned: bool = False
    equipped_slot: Optional[SlotType] = None
    weight: float = 0.0
    properties: Dict[str, Any] = field(default_factory=dict)

    # ── 便捷方法 ──────────────────────────────────────────────────────

    def is_weapon(self) -> bool:
        """是否为武器。"""
        return self.properties.get("is_weapon", False)

    def is_shield(self) -> bool:
        """是否为盾牌。"""
        return self.properties.get("is_shield", False)

    def is_focus(self) -> bool:
        """是否为法器。"""
        return self.properties.get("is_focus", False)

    def is_two_handed(self) -> bool:
        """是否为双手武器。"""
        return "two_handed" in self.properties.get("weapon_properties", [])


@dataclass
class EquipmentSlotsManager:
    """管理实体的装备槽位。

    槽位:
      - main_hand: 主手
      - off_hand: 副手
      - armor: 护甲
      - focus: 法器
      - worn: 穿戴物品（可多个）
    """

    main_hand: Optional[ItemInstance] = None
    off_hand: Optional[ItemInstance] = None
    armor: Optional[ItemInstance] = None
    focus: Optional[ItemInstance] = None
    worn: List[ItemInstance] = field(default_factory=list)

    # ── 装备/卸下 ─────────────────────────────────────────────────────

    def equip(self, item: ItemInstance, slot: SlotType) -> bool:
        """装备物品到指定槽位。

        Returns:
            是否装备成功
        """
        if slot == SlotType.MAIN_HAND:
            if self.main_hand is not None:
                return False
            # 双手武器占用两只手
            if item.is_two_handed():
                if self.off_hand is not None:
                    return False
            self.main_hand = item
            item.equipped_slot = slot
            return True

        if slot == SlotType.OFF_HAND:
            if self.off_hand is not None:
                return False
            # 若主手是双手武器，副手不能装备
            if self.main_hand is not None and self.main_hand.is_two_handed():
                return False
            self.off_hand = item
            item.equipped_slot = slot
            return True

        if slot == SlotType.ARMOR:
            if self.armor is not None:
                return False
            self.armor = item
            item.equipped_slot = slot
            return True

        if slot == SlotType.FOCUS:
            if self.focus is not None:
                return False
            self.focus = item
            item.equipped_slot = slot
            return True

        if slot == SlotType.WORN:
            self.worn.append(item)
            item.equipped_slot = slot
            return True

        return False

    def unequip(self, slot: SlotType) -> Optional[ItemInstance]:
        """卸下指定槽位的物品。

        Returns:
            卸下的物品，若槽位为空则返回 None
        """
        if slot == SlotType.MAIN_HAND:
            item = self.main_hand
            if item is not None:
                item.equipped_slot = None
            self.main_hand = None
            return item

        if slot == SlotType.OFF_HAND:
            item = self.off_hand
            if item is not None:
                item.equipped_slot = None
            self.off_hand = None
            return item

        if slot == SlotType.ARMOR:
            item = self.armor
            if item is not None:
                item.equipped_slot = None
            self.armor = None
            return item

        if slot == SlotType.FOCUS:
            item = self.focus
            if item is not None:
                item.equipped_slot = None
            self.focus = None
            return item

        if slot == SlotType.WORN:
            # 卸下最后一件穿戴物品
            if self.worn:
                item = self.worn.pop()
                item.equipped_slot = None
                return item
            return None

        return None

    # ── 查询 ──────────────────────────────────────────────────────────

    def get_free_hands(self) -> int:
        """获取空闲的手数量（0/1/2）。"""
        hands = 2
        if self.main_hand is not None:
            hands -= 1
            if self.main_hand.is_two_handed():
                hands -= 1
        if self.off_hand is not None:
            hands -= 1
        return max(0, hands)

    def is_shield_equipped(self) -> bool:
        """是否装备了盾牌。"""
        return self.off_hand is not None and self.off_hand.is_shield()

    def get_weapon_in_hand(self, hand: str = "main") -> Optional[ItemInstance]:
        """获取指定手的武器。

        Args:
            hand: "main" 或 "off"
        """
        if hand == "main":
            item = self.main_hand
            if item is not None and item.is_weapon():
                return item
        elif hand == "off":
            item = self.off_hand
            if item is not None and item.is_weapon():
                return item
        return None

    def has_focus_available(self) -> bool:
        """是否有法器可用。

        法器可以在 main_hand、off_hand 或 focus 槽位。
        """
        if self.focus is not None and self.focus.is_focus():
            return True
        if self.main_hand is not None and self.main_hand.is_focus():
            return True
        if self.off_hand is not None and self.off_hand.is_focus():
            return True
        return False

    def can_cast_with_components(
        self,
        has_v: bool,
        has_s: bool,
        has_m: bool,
    ) -> bool:
        """判断当前装备状态是否满足施法成分。

        规则:
          - V (语言): 总是可以满足
          - S (姿势): 需要至少一只空闲手
          - M (材料): 需要法器或对应材料组件

        Args:
            has_v: 法术是否需要语言成分
            has_s: 法术是否需要姿势成分
            has_m: 法术是否需要材料成分

        Returns:
            是否满足所有成分要求
        """
        # 语言成分：总是可以
        # 姿势成分：需要空闲手
        if has_s and self.get_free_hands() < 1:
            return False

        # 材料成分：需要法器或空闲手持有材料
        if has_m:
            if not self.has_focus_available() and self.get_free_hands() < 1:
                return False

        return True
