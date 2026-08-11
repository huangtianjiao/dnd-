"""Grant 系统 — 管理特性授予的熟练、法术、修正等"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Grant:
    """一条授予记录"""

    grant_id: str
    source_feature_id: str
    grant_type: str  # "proficiency" / "spell" / "resource" / "action" / "modifier"
    target: str  # 授予目标（技能名 / 法术名 / 资源名等）
    value: Any = None  # 授予的值

    def to_dict(self) -> dict:
        return {
            "grant_id": self.grant_id,
            "source_feature_id": self.source_feature_id,
            "grant_type": self.grant_type,
            "target": self.target,
            "value": self.value,
        }


class GrantManager:
    """管理实体的所有授予记录"""

    def __init__(self) -> None:
        self._grants: Dict[str, List[Grant]] = {}  # entity_id -> grants

    # ── 基本 CRUD ──────────────────────────────────────────────

    def add_grant(self, entity_id: str, grant: Grant) -> None:
        """为实体添加一条授予"""
        self._grants.setdefault(entity_id, [])
        self._grants[entity_id].append(grant)

    def remove_grant(self, entity_id: str, grant_id: str) -> bool:
        """按 grant_id 移除一条授予，返回是否成功"""
        grants = self._grants.get(entity_id, [])
        for i, g in enumerate(grants):
            if g.grant_id == grant_id:
                grants.pop(i)
                return True
        return False

    def remove_by_source(self, entity_id: str, feature_id: str) -> int:
        """移除来自指定特性的所有授予，返回移除数量"""
        grants = self._grants.get(entity_id, [])
        original = len(grants)
        self._grants[entity_id] = [g for g in grants if g.source_feature_id != feature_id]
        return original - len(self._grants[entity_id])

    def get_grants(self, entity_id: str, grant_type: str = "") -> List[Grant]:
        """获取实体的授予列表，可按类型过滤"""
        grants = self._grants.get(entity_id, [])
        if grant_type:
            return [g for g in grants if g.grant_type == grant_type]
        return list(grants)

    # ── 便捷查询 ───────────────────────────────────────────────

    def has_proficiency(self, entity_id: str, skill: str) -> bool:
        """检查实体是否拥有某项熟练"""
        return any(
            g.target == skill
            for g in self._grants.get(entity_id, [])
            if g.grant_type == "proficiency"
        )

    def has_spell(self, entity_id: str, spell_id: str) -> bool:
        """检查实体是否已学会某法术"""
        return any(
            g.target == spell_id
            for g in self._grants.get(entity_id, [])
            if g.grant_type == "spell"
        )

    def get_proficiencies(self, entity_id: str) -> List[str]:
        """获取实体所有熟练项列表"""
        return [
            g.target
            for g in self._grants.get(entity_id, [])
            if g.grant_type == "proficiency"
        ]

    def get_granted_spells(self, entity_id: str) -> List[str]:
        """获取实体所有已授予法术列表"""
        return [
            g.target
            for g in self._grants.get(entity_id, [])
            if g.grant_type == "spell"
        ]

    def get_modifier(self, entity_id: str, target: str) -> Optional[Any]:
        """获取指定 modifier 的值"""
        for g in self._grants.get(entity_id, []):
            if g.grant_type == "modifier" and g.target == target:
                return g.value
        return None

    def clear(self, entity_id: str) -> None:
        """清除实体的所有授予"""
        self._grants.pop(entity_id, None)
