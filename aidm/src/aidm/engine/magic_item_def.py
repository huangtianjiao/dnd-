"""魔法物品定义 — MagicItemDefinition / AttunementService。

ITEM-003: 同调只有名称上限，没有效果与先决条件。
MagicItemDefinition复用Feature DSL；AttunementService验证条件、占用槽并授予/撤销效果。

规则依据: topics/玩家手册2024/装备/魔法物品.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AttunementRequirement:
    """同调先决条件。"""

    min_level: int = 0
    required_class: str = ""        # 特定职业才能同调
    required_alignment: str = ""    # 特定阵营
    required_feature: str = ""      # 需要拥有特定特性


@dataclass
class MagicItemDefinition:
    """魔法物品定义 — 复用 Feature DSL。

    ITEM-003: 统一魔法物品效果模型。
    """

    item_id: str                    # 稳定 canonical ID
    name: str                       # 中文名
    rarity: str = "common"          # common/uncommon/rare/very_rare/legendary/artifact
    requires_attunement: bool = False
    attunement_requirements: AttunementRequirement = field(default_factory=AttunementRequirement)
    max_charges: int = 0            # 充能数（0=无充能机制）
    recharge_on: str = ""           # dawn/short_rest/long_rest
    granted_features: List[str] = field(default_factory=list)  # 授予的特性 ID 列表
    granted_spells: List[str] = field(default_factory=list)    # 授予的法术列表
    ac_bonus: int = 0               # AC 加值
    description: str = ""

    def can_attune(self, character_level: int, character_class: str,
                   character_alignment: str = "",
                   character_features: List[str] | None = None) -> bool:
        """检查角色是否满足同调先决条件。"""
        if not self.requires_attunement:
            return True
        req = self.attunement_requirements
        if character_level < req.min_level:
            return False
        if req.required_class and character_class != req.required_class:
            return False
        if req.required_alignment and character_alignment != req.required_alignment:
            return False
        if req.required_feature:
            features = character_features or []
            if req.required_feature not in features:
                return False
        return True


@dataclass
class AttunementService:
    """同调服务 — 验证条件、占用槽并授予/撤销效果。

    ITEM-003: 同调/解除后效果即时一致；第四件同调被拒绝。
    """

    MAX_ATTUNED = 3

    _attuned: Dict[str, List[str]] = field(default_factory=dict)  # entity_id → [item_id]

    def attune(self, entity_id: str, item_id: str,
               item_def: MagicItemDefinition,
               character_level: int = 1,
               character_class: str = "",
               character_alignment: str = "",
               character_features: List[str] | None = None) -> bool:
        """尝试同调一个魔法物品。"""
        current = self._attuned.get(entity_id, [])
        if len(current) >= self.MAX_ATTUNED:
            return False
        if item_id in current:
            return True  # 已同调
        if not item_def.can_attune(character_level, character_class,
                                    character_alignment, character_features):
            return False
        current.append(item_id)
        self._attuned[entity_id] = current
        return True

    def break_attunement(self, entity_id: str, item_id: str) -> bool:
        """解除同调。"""
        current = self._attuned.get(entity_id, [])
        if item_id not in current:
            return False
        current.remove(item_id)
        return True

    def get_attuned_items(self, entity_id: str) -> List[str]:
        """获取已同调物品列表。"""
        return list(self._attuned.get(entity_id, []))

    def is_attuned(self, entity_id: str, item_id: str) -> bool:
        """检查物品是否已同调。"""
        return item_id in self._attuned.get(entity_id, [])
