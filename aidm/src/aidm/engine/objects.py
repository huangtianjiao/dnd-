"""物件属性引擎 — 物件 AC / HP / 破坏 DC / 地形特征。

规则依据:
  - R-OBJ-001 物件 AC（按材质）
  - R-OBJ-002 物件 HP（按材质与厚度）
  - R-OBJ-003 破坏物件（力量检定 DC）
  - R-OBJ-004 物件免疫（毒素/心灵伤害免疫）
  - ENV-002 物件与地形结构化
出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm ; 进行游戏/与物件交互.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ──────────────────────────────────────────────────────────────────────────
# 物件材质属性表
# ──────────────────────────────────────────────────────────────────────────

OBJECT_STATS: dict[str, dict] = {
    "cloth":       {"ac": 11, "hp_per_inch": 1},
    "paper":       {"ac": 11, "hp_per_inch": 1},
    "rope":        {"ac": 11, "hp_per_inch": 1},
    "crystal":     {"ac": 13, "hp_per_inch": 2},
    "glass":       {"ac": 13, "hp_per_inch": 2},
    "ice":         {"ac": 13, "hp_per_inch": 2},
    "wood":        {"ac": 15, "hp_per_inch": 3},
    "bone":        {"ac": 15, "hp_per_inch": 3},
    "stone":       {"ac": 17, "hp_per_inch": 5},
    "iron":        {"ac": 19, "hp_per_inch": 6},
    "steel":       {"ac": 19, "hp_per_inch": 6},
    "mithral":     {"ac": 21, "hp_per_inch": 8},
    "adamantine":  {"ac": 23, "hp_per_inch": 10},
}

# 破坏 DC 按材质/体积（简化分档：小型物件/中型/大型）
_BREAK_DC: dict[str, dict[str, int]] = {
    "cloth":      {"small": 5,  "medium": 5,  "large": 5},
    "paper":      {"small": 5,  "medium": 5,  "large": 5},
    "rope":       {"small": 10, "medium": 15, "large": 17},
    "crystal":    {"small": 10, "medium": 13, "large": 15},
    "glass":      {"small": 5,  "medium": 10, "large": 13},
    "ice":        {"small": 10, "medium": 13, "large": 15},
    "wood":       {"small": 13, "medium": 15, "large": 17},
    "bone":       {"small": 13, "medium": 15, "large": 17},
    "stone":      {"small": 17, "medium": 20, "large": 23},
    "iron":       {"small": 19, "medium": 23, "large": 25},
    "steel":      {"small": 19, "medium": 23, "large": 25},
    "mithral":    {"small": 21, "medium": 25, "large": 27},
    "adamantine": {"small": 23, "medium": 27, "large": 30},
}

# 物件免疫的伤害类型
OBJECT_IMMUNITIES = frozenset({"毒素", "心灵"})


# ──────────────────────────────────────────────────────────────────────────
# 核心函数
# ──────────────────────────────────────────────────────────────────────────

def object_ac(material: str) -> int:
    """物件 AC（按材质）。

    规则: R-OBJ-001 物件 AC
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    """
    entry = OBJECT_STATS.get(material.lower())
    if entry is None:
        raise ValueError(f"未知物件材质 {material!r}，可选: {list(OBJECT_STATS)}")
    return entry["ac"]


def object_hp(material: str, thickness_inches: float = 1.0) -> int:
    """物件 HP = hp_per_inch × 厚度（英寸），至少 1。

    规则: R-OBJ-002 物件 HP
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    """
    entry = OBJECT_STATS.get(material.lower())
    if entry is None:
        raise ValueError(f"未知物件材质 {material!r}")
    return max(1, int(entry["hp_per_inch"] * thickness_inches))


def break_dc(material: str, size: str = "medium") -> int:
    """破坏物件所需的力量检定 DC。

    规则: R-OBJ-003 破坏物件
    出处: topics/玩家手册2024/进行游戏/与物件交互.htm
    参数:
      size: "small"/"medium"/"large"
    """
    entry = _BREAK_DC.get(material.lower())
    if entry is None:
        raise ValueError(f"未知物件材质 {material!r}")
    return entry.get(size.lower(), entry.get("medium", 15))


def object_damage_immunities() -> frozenset[str]:
    """物件的伤害免疫集合（毒素/心灵）。

    规则: R-OBJ-004 物件免疫
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    """
    return OBJECT_IMMUNITIES


# ──────────────────────────────────────────────────────────────────────────
# ENV-002: 物件与地形结构化
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class ObjectEntity:
    """结构化物件实体。

    规则: ENV-002 物件与地形结构化
    出处: topics/玩家手册2024/进行游戏/与物件交互.htm

    属性:
        object_id: 物件唯一 ID
        name: 物件名称
        material: 材质 (wood/stone/metal/cloth 等)
        ac: 护甲等级
        hp: 生命值
        damage_threshold: 伤害阈值（低于此值不受伤）
        is_flammable: 是否可燃
        provides_cover: 是否提供掩护
        size: 尺寸 (Tiny/Small/Medium/Large/Huge/Gargantuan)
    """
    object_id: str = ""
    name: str = ""
    material: str = ""
    ac: int = 10
    hp: int = 10
    damage_threshold: int = 0
    is_flammable: bool = False
    provides_cover: bool = False
    size: str = "Medium"

    def take_damage(self, damage: int) -> dict:
        """物件受伤。

        规则: ENV-002 伤害阈值
        返回: dict {damage_dealt, hp_remaining, destroyed}
        """
        if damage <= self.damage_threshold:
            return {"damage_dealt": 0, "hp_remaining": self.hp, "destroyed": False}
        actual = damage
        self.hp = max(0, self.hp - actual)
        return {
            "damage_dealt": actual,
            "hp_remaining": self.hp,
            "destroyed": self.hp <= 0,
        }

    @classmethod
    def from_material(cls, object_id: str, name: str, material: str,
                      thickness_inches: float = 1.0,
                      size: str = "Medium") -> "ObjectEntity":
        """从材质创建物件（自动计算 AC/HP）。"""
        ac_val = object_ac(material)
        hp_val = object_hp(material, thickness_inches)
        flammable = material.lower() in ("wood", "cloth", "paper", "rope", "bone")
        provides = size.lower() in ("medium", "large", "huge", "gargantuan")
        return cls(
            object_id=object_id,
            name=name,
            material=material,
            ac=ac_val,
            hp=hp_val,
            damage_threshold=0,
            is_flammable=flammable,
            provides_cover=provides,
            size=size,
        )


@dataclass
class TerrainFeature:
    """地形特征。

    规则: ENV-002 物件与地形结构化
    出处: topics/城主指南2024/2.运作游戏/运作交涉/旅行.htm

    属性:
        terrain_id: 地形唯一 ID
        terrain_type: 地形类型 (difficult/hazardous/water/elevation)
        cost_multiplier: 移动消耗倍率（difficult terrain = 2.0）
        hazard_damage: 危害伤害（如 "1d6 fire"）
        description: 描述文本
    """
    terrain_id: str = ""
    terrain_type: str = "difficult"
    cost_multiplier: float = 2.0
    hazard_damage: str = ""
    description: str = ""

    def movement_cost(self, base_cost: float = 5.0) -> float:
        """计算通过此地形的实际移动消耗。

        参数:
            base_cost: 基础移动消耗（默认 5ft）
        返回:
            实际移动消耗
        """
        return base_cost * self.cost_multiplier

    def is_difficult(self) -> bool:
        """是否为困难地形。"""
        return self.terrain_type in ("difficult", "hazardous")

    def has_hazard(self) -> bool:
        """是否有危害伤害。"""
        return bool(self.hazard_damage)


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # AC
    assert object_ac("wood") == 15
    assert object_ac("iron") == 19
    assert object_ac("adamantine") == 23

    # HP
    assert object_hp("wood", 1) == 3
    assert object_hp("iron", 2) == 12
    assert object_hp("cloth", 0.5) == 1  # 至少1

    # 破坏 DC
    assert break_dc("wood", "medium") == 15
    assert break_dc("iron", "small") == 19
    assert break_dc("stone", "large") == 23

    # 免疫
    assert "毒素" in object_damage_immunities()
    assert "心灵" in object_damage_immunities()
    assert "火焰" not in object_damage_immunities()

    print("[objects] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
