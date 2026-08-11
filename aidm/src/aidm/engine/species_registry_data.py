"""物种注册表 PHB2024 数据 — CHR-004。

从 data.races.RACES 数据表构建 SpeciesDefinition 并注册到全局 SpeciesRegistry。
每个物种的 traits 转换为可执行的 SpeciesFeature。

规则依据: CHR-004 物种特质统一可执行定义
出处: topics/玩家手册2024/角色创建/物种.htm
"""

from __future__ import annotations

from .species_def import (
    DamageAffinity,
    MovementType,
    Sense,
    SpeciesDefinition,
    SpeciesFeature,
    SpeciesRegistry,
)

# 全局物种注册表单例
_registry: SpeciesRegistry | None = None


def _build_species(species_id: str, name: str, raw: dict) -> SpeciesDefinition:
    """从 RACES 原始数据构建 SpeciesDefinition。"""
    traits = raw.get("traits", [])
    size_raw = raw.get("size", ["中型"])
    # 物种 traits 中是否含黑暗视觉
    dv = int(raw.get("darkvision", 0) or 0)

    senses = []
    if dv > 0:
        senses.append(Sense(sense_type="darkvision", range_ft=dv))

    affinities = []
    trait_text = " ".join(traits)
    if "毒素伤害抗性" in trait_text or "毒" in trait_text and "抗性" in trait_text:
        affinities.append(DamageAffinity(damage_type="毒素", affinity="resistance"))
    if "光耀伤害与暗蚀伤害的抗性" in trait_text:
        affinities.append(DamageAffinity(damage_type="光耀", affinity="resistance"))
        affinities.append(DamageAffinity(damage_type="暗蚀", affinity="resistance"))

    features = [
        SpeciesFeature(
            name=trait.split("：")[0][:24],
            description=trait,
            granted_features=[],
        )
        for trait in traits
    ]

    return SpeciesDefinition(
        species_id=species_id,
        name=name,
        size=size_raw[0],
        base_speed=int(raw.get("speed", 30) or 30),
        senses=senses,
        movement_types=[MovementType(movement_type="walk",
                                     speed_ft=int(raw.get("speed", 30) or 30))],
        damage_affinities=affinities,
        features=features,
    )


def load_species_registry() -> SpeciesRegistry:
    """加载全局物种注册表（幂等，重复调用返回同一实例）。

    返回: 填充了 PHB2024 全部物种的 SpeciesRegistry。
    """
    global _registry
    if _registry is not None:
        return _registry

    from ..data.races import RACES

    registry = SpeciesRegistry()
    for zh_name, raw in RACES.items():
        species_id = f"species.{zh_name}"
        registry.register(_build_species(species_id, zh_name, raw))

    _registry = registry
    return _registry


def get_species_registry() -> SpeciesRegistry:
    """获取全局物种注册表。"""
    return load_species_registry()
