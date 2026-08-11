"""姿势/材料/法器判断 — ComponentCheck。

SPL-011: 姿势/材料/法器判断依赖名称猜测。
从EquipmentSlots和ItemDefinition判断手、法器类型与施法来源；实现同一只手处理S+M的规则。

规则依据: topics/玩家手册2024/法术/法术成分.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class ComponentType(str, Enum):
    """法术成分类型。"""

    VERBAL = "V"           # 言语
    SOMATIC = "S"          # 姿势
    MATERIAL = "M"         # 材料


@dataclass
class EquipmentSlotState:
    """装备槽位状态。

    SPL-011: 从EquipmentSlots推导空闲手。
    """

    main_hand: str = ""       # 主手物品 ID
    off_hand: str = ""        # 副手物品 ID
    armor: str = ""           # 护甲
    focus: str = ""           # 法器槽


@dataclass
class ComponentCheckResult:
    """成分检查结果。"""

    can_cast: bool = True
    missing_components: List[str] = field(default_factory=list)
    free_hands: int = 2
    has_focus: bool = False
    has_material_pouch: bool = False
    hands_used_for_s_m: bool = False


def check_casting_components(
    components: Set[ComponentType],
    equipment: EquipmentSlotState,
    inventory: List[str],
    material_cost_gp: float = 0.0,
    material_consumed: bool = False,
) -> ComponentCheckResult:
    """检查施法成分是否满足。

    SPL-011: 同一只手处理S+M的规则。
    """
    result = ComponentCheckResult()

    needs_v = ComponentType.VERBAL in components
    needs_s = ComponentType.SOMATIC in components
    needs_m = ComponentType.MATERIAL in components

    if needs_v:
        pass

    result.free_hands = _count_free_hands(equipment)
    result.has_focus = _check_has_focus(equipment, inventory)
    result.has_material_pouch = _check_has_material_pouch(inventory)

    if needs_s and needs_m:
        if result.free_hands >= 2:
            result.hands_used_for_s_m = True
        elif result.free_hands >= 1 and result.has_focus:
            result.hands_used_for_s_m = True
        elif result.free_hands < 1:
            result.can_cast = False
            result.missing_components.append("需要空闲手执行 S+M")

    elif needs_s:
        if result.free_hands < 1:
            result.can_cast = False
            result.missing_components.append("需要空闲手执行 S")

    elif needs_m:
        if not result.has_focus and not result.has_material_pouch:
            result.can_cast = False
            result.missing_components.append("需要法器或材料包")

    return result


def _count_free_hands(equipment: EquipmentSlotState) -> int:
    """计算空闲手数量。

    SPL-011: 盾牌在背包不占手。
    """
    used = 0
    if equipment.main_hand:
        used += 1
    if equipment.off_hand:
        used += 1
    return max(0, 2 - used)


_FOCUS_KEYWORDS = ("法器", "圣徽", "奥术法器", "德鲁伊法器")
_POUCH_KEYWORDS = ("材料包", "材料组件包", "施法材料包")


def _check_has_focus(equipment: EquipmentSlotState, inventory: List[str]) -> bool:
    """检查是否拥有可用法器。"""
    for item in inventory:
        for kw in _FOCUS_KEYWORDS:
            if kw in item:
                return True
    return False


def _check_has_material_pouch(inventory: List[str]) -> bool:
    """检查是否拥有材料包。"""
    for item in inventory:
        for kw in _POUCH_KEYWORDS:
            if kw in item:
                return True
    return False
