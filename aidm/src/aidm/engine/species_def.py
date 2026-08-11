"""物种定义 — SpeciesDefinition。

CHR-004: 物种特质缺少统一可执行定义。
SpeciesDefinition授予Sense/Movement/DamageAffinity/Feature/Choice；全部进入统一效果系统。

规则依据: topics/玩家手册2024/角色创建/物种.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Sense:
    """感官。"""

    sense_type: str = "normal"     # normal/darkvision/blindsight/truesight/tremorsense
    range_ft: int = 0


@dataclass
class MovementType:
    """移动类型。"""

    movement_type: str = "walk"    # walk/climb/swim/fly/burrow
    speed_ft: int = 30


@dataclass
class DamageAffinity:
    """伤害抗性/免疫/易伤。"""

    damage_type: str = ""
    affinity: str = "resistance"   # resistance/immunity/vulnerability


@dataclass
class SpeciesFeature:
    """物种特性。"""

    name: str
    description: str = ""
    granted_features: List[str] = field(default_factory=list)
    granted_spells: List[str] = field(default_factory=list)
    choices: List[dict] = field(default_factory=list)


@dataclass
class SpeciesDefinition:
    """物种完整定义。

    CHR-004: 统一可执行的物种定义。
    """

    species_id: str                    # canonical ID
    name: str                          # 中文名
    size: str = "medium"               # tiny/small/medium/large/huge/gargantuan
    base_speed: int = 30
    senses: List[Sense] = field(default_factory=list)
    movement_types: List[MovementType] = field(default_factory=list)
    damage_affinities: List[DamageAffinity] = field(default_factory=list)
    features: List[SpeciesFeature] = field(default_factory=list)

    def get_all_granted_features(self) -> List[str]:
        """获取所有特性授予的 feature ID。"""
        result: List[str] = []
        for f in self.features:
            result.extend(f.granted_features)
        return result

    def get_all_granted_spells(self) -> List[str]:
        """获取所有特性授予的法术。"""
        result: List[str] = []
        for f in self.features:
            result.extend(f.granted_spells)
        return result

    def has_darkvision(self) -> bool:
        """是否有黑暗视觉。"""
        return any(s.sense_type == "darkvision" for s in self.senses)


# ── 物种注册表 ──────────────────────────────────────────────────

@dataclass
class SpeciesRegistry:
    """物种注册表 — 管理所有已定义物种。"""

    _species: Dict[str, SpeciesDefinition] = field(default_factory=dict)

    def register(self, species: SpeciesDefinition) -> None:
        """注册一个物种定义。"""
        self._species[species.species_id] = species

    def get(self, species_id: str) -> SpeciesDefinition | None:
        """获取指定物种的定义。"""
        return self._species.get(species_id)

    def list_all(self) -> List[str]:
        """列出所有已注册物种 ID。"""
        return list(self._species.keys())
