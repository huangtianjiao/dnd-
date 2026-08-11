"""Feature DSL — 特性定义框架"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class FeatureType(str, Enum):
    """特性类型枚举"""

    PASSIVE = "passive"  # 被动修正（如 +2 AC）
    RESOURCE = "resource"  # 资源池（如气、狂暴次数）
    ACTION = "action"  # 授予动作（如额外攻击）
    REACTION = "reaction"  # 授予反应
    TRIGGER = "trigger"  # 触发器（如危急时刻加血）
    PROFICIENCY = "proficiency"  # 熟练/精通授予
    SPELL_GRANT = "spell_grant"  # 法术授予
    MODIFIER = "modifier"  # 数值修正


@dataclass
class FeatureDefinition:
    """特性定义 — 描述一个职业特性/种族特性/专长等的完整信息"""

    feature_id: str
    name: str
    feature_type: FeatureType
    source_class: str = ""  # 来源职业
    source_level: int = 0  # 授予等级
    description: str = ""

    # 效果
    modifiers: List[dict] = field(default_factory=list)
    resource_pool: Optional[dict] = None  # {name, max, recharge, pool_type, resource_type}
    granted_actions: List[str] = field(default_factory=list)
    granted_proficiencies: List[str] = field(default_factory=list)
    granted_spells: List[str] = field(default_factory=list)
    triggers: List[dict] = field(default_factory=list)

    # 先决条件
    prerequisites: List[dict] = field(default_factory=list)

    def validate(self) -> List[str]:
        """校验特性定义的合法性，返回错误列表（空列表 = 合法）"""
        errors: List[str] = []
        if not self.feature_id:
            errors.append("feature_id 不能为空")
        if not self.name:
            errors.append("name 不能为空")
        if self.source_level < 0:
            errors.append("source_level 不能为负数")
        if self.resource_pool is not None:
            rp = self.resource_pool
            if "name" not in rp:
                errors.append("resource_pool 缺少 name 字段")
            if "max" not in rp:
                errors.append("resource_pool 缺少 max 字段")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "feature_id": self.feature_id,
            "name": self.name,
            "feature_type": self.feature_type.value,
            "source_class": self.source_class,
            "source_level": self.source_level,
            "description": self.description,
            "modifiers": self.modifiers,
            "resource_pool": self.resource_pool,
            "granted_actions": self.granted_actions,
            "granted_proficiencies": self.granted_proficiencies,
            "granted_spells": self.granted_spells,
            "triggers": self.triggers,
            "prerequisites": self.prerequisites,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeatureDefinition":
        """从字典反序列化"""
        ft = data.get("feature_type", "passive")
        if isinstance(ft, str):
            ft = FeatureType(ft)
        return cls(
            feature_id=data["feature_id"],
            name=data["name"],
            feature_type=ft,
            source_class=data.get("source_class", ""),
            source_level=data.get("source_level", 0),
            description=data.get("description", ""),
            modifiers=data.get("modifiers", []),
            resource_pool=data.get("resource_pool"),
            granted_actions=data.get("granted_actions", []),
            granted_proficiencies=data.get("granted_proficiencies", []),
            granted_spells=data.get("granted_spells", []),
            triggers=data.get("triggers", []),
            prerequisites=data.get("prerequisites", []),
        )
