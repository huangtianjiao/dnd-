"""子职进度系统 — SubclassProgression。

CHR-002: 建立SubclassProgression与FeatureDefinition，按等级自动授予并支持选项。
规则依据: topics/玩家手册2024/职业/子职.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SubclassFeature:
    """子职特性定义。"""

    name: str
    level: int
    description: str = ""
    grants: List[str] = field(default_factory=list)
    choices: List[dict] = field(default_factory=list)


@dataclass
class SubclassProgression:
    """子职进度表 — 按等级管理子职特性。

    CHR-002: 子职从3级开始获得特性，按等级自动授予。
    """

    subclass_name: str
    base_class: str
    features_by_level: Dict[int, List[SubclassFeature]] = field(default_factory=dict)

    def add_feature(self, feature: SubclassFeature) -> None:
        """添加一个子职特性。"""
        if feature.level not in self.features_by_level:
            self.features_by_level[feature.level] = []
        self.features_by_level[feature.level].append(feature)

    def get_features_at_level(self, level: int) -> List[SubclassFeature]:
        """获取指定等级解锁的所有子职特性。"""
        return self.features_by_level.get(level, [])

    def get_all_features_up_to(self, level: int) -> List[SubclassFeature]:
        """获取从1级到指定等级的所有已解锁子职特性。"""
        result: List[SubclassFeature] = []
        for lvl in sorted(self.features_by_level.keys()):
            if lvl <= level:
                result.extend(self.features_by_level[lvl])
        return result


# ── 子职注册表 ──────────────────────────────────────────────────

@dataclass
class SubclassRegistry:
    """子职注册表 — 管理所有职业的子职进度。"""

    _progressions: Dict[str, SubclassProgression] = field(default_factory=dict)

    def register(self, progression: SubclassProgression) -> None:
        """注册一个子职进度表。"""
        key = f"{progression.base_class}:{progression.subclass_name}"
        self._progressions[key] = progression

    def get(self, base_class: str, subclass_name: str) -> Optional[SubclassProgression]:
        """获取指定职业和子职的进度表。"""
        key = f"{base_class}:{subclass_name}"
        return self._progressions.get(key)

    def list_subclasses(self, base_class: str) -> List[str]:
        """列出指定职业的所有已注册子职。"""
        result: List[str] = []
        for key in self._progressions:
            bc, sc = key.split(":", 1)
            if bc == base_class:
                result.append(sc)
        return result
