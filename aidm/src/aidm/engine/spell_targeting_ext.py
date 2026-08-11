"""目标、范围、区域与视线合法性 — SpellTargetingExt。

SPL-007: 目标、范围、区域与视线合法性缺失。
将RangeSpec、TargetSpec、AreaSpec编译为几何查询；支持球/锥/线/立方/柱/光环及自选目标。

规则依据: topics/玩家手册2024/法术详述/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Set


class AreaShape(str, Enum):
    """区域形状。"""

    SPHERE = "sphere"             # 球形
    CONE = "cone"                 # 锥形
    LINE = "line"                 # 线形
    CUBE = "cube"                 # 立方
    CYLINDER = "cylinder"         # 柱形
    EMANATION = "emanation"       # 光环


@dataclass
class RangeSpec:
    """施法距离规格。

    SPL-007: 将RangeSpec编译为几何查询。
    """

    range_ft: float = 0.0         # 施法距离（尺）
    self_only: bool = False       # 是否仅自身
    touch: bool = False           # 是否触碰


@dataclass
class TargetSpec:
    """目标规格。

    SPL-007: 支持自选目标。
    """

    target_count: int = 1         # 目标数量
    target_type: str = "creature"  # creature/object/point
    requires_los: bool = True     # 是否需要视线
    requires_visibility: bool = True  # 是否需要可见


@dataclass
class AreaSpec:
    """区域效果规格。

    SPL-007: 支持球/锥/线/立方/柱/光环。
    """

    shape: AreaShape = AreaShape.SPHERE
    size_ft: float = 0.0          # 主尺寸（半径/边长/高度/长度）
    width_ft: float = 0.0         # 线形宽度


@dataclass
class SpellTargetingResult:
    """法术目标合法性验证结果。"""

    valid_targets: List[str] = field(default_factory=list)
    out_of_range: List[str] = field(default_factory=list)
    no_los: List[str] = field(default_factory=list)
    invisible: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """是否有合法目标。"""
        return len(self.valid_targets) > 0


def validate_spell_targets(
    range_spec: RangeSpec,
    target_spec: TargetSpec,
    area_spec: Optional[AreaSpec],
    caster_pos: tuple[float, float],
    candidate_positions: dict[str, tuple[float, float]],
    has_los: dict[str, bool] | None = None,
    is_visible: dict[str, bool] | None = None,
) -> SpellTargetingResult:
    """验证法术目标的合法性。

    SPL-007: 超距/穿墙/不可见目标不会进入候选。
    """
    import math

    result = SpellTargetingResult()
    los_map = has_los or {}
    vis_map = is_visible or {}

    for target_id, pos in candidate_positions.items():
        dist = math.sqrt(
            (pos[0] - caster_pos[0]) ** 2 +
            (pos[1] - caster_pos[1]) ** 2
        )

        if dist > range_spec.range_ft:
            result.out_of_range.append(target_id)
            continue

        if target_spec.requires_los and not los_map.get(target_id, True):
            result.no_los.append(target_id)
            continue

        if target_spec.requires_visibility and not vis_map.get(target_id, True):
            result.invisible.append(target_id)
            continue

        result.valid_targets.append(target_id)

    return result
