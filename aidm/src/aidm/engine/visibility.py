"""统一可见性服务 — 综合光照、遮蔽、感官、距离和效果判定可见性。

设计原则：
  - VisibilityService 整合 vision.py 的底层概念，提供统一的可见性判定接口。
  - 同时处理可见性等级和掩护等级。

规则依据: ENV-001 VisibilityService 统一可见性
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .vision import (
    LIGHT_BRIGHT,
    LIGHT_DARK,
    LIGHT_DIM,
    OBSCURE_HEAVY,
    OBSCURE_LIGHT,
    can_see,
    obscurement_from_light,
    darkvision_effective_light,
)


class VisibilityLevel(str, Enum):
    """可见性等级。"""

    VISIBLE = "visible"           # 完全可见
    LOCATED = "located"           # 知道位置但看不见（如盲视/颤动感知）
    CONCEALED = "concealed"       # 被遮蔽（轻度遮蔽 → 攻击劣势）
    HIDDEN = "hidden"             # 完全不可见（重度遮蔽/隐形）


class CoverLevel(str, Enum):
    """掩护等级。"""

    NONE = "none"                          # 无掩护
    HALF = "half"                          # +2 AC / DEX save
    THREE_QUARTERS = "three_quarters"      # +5 AC / DEX save
    FULL = "full"                          # 不可选为目标


@dataclass
class VisibilityResult:
    """可见性判定结果。"""

    level: VisibilityLevel = VisibilityLevel.VISIBLE
    cover: CoverLevel = CoverLevel.NONE
    line_of_sight: bool = True
    line_of_effect: bool = True
    reasons: List[str] = field(default_factory=list)

    # ── 便捷方法 ──────────────────────────────────────────────────────

    @property
    def attack_disadvantage(self) -> bool:
        """是否因可见性导致攻击劣势。"""
        return self.level in (VisibilityLevel.CONCEALED,)

    @property
    def cannot_target(self) -> bool:
        """是否因掩护无法选为目标。"""
        return self.cover == CoverLevel.FULL


class VisibilityService:
    """统一可见性判定服务。

    综合光照、遮蔽、感官、距离和效果线进行判定。
    """

    def check_visibility(
        self,
        observer: Dict[str, Any],
        target: Dict[str, Any],
        battle_map: Any = None,
        conditions: Optional[List[str]] = None,
    ) -> VisibilityResult:
        """综合判定可见性。

        Args:
            observer: 观察者信息 dict，需包含:
                - position: (x, y) 网格坐标
                - senses: {darkvision_ft, blindsight_ft, truesight_ft, tremorsense_ft, on_ground}
                - conditions: List[str] 状态列表（如 "blinded"）
            target: 目标信息 dict，需包含:
                - position: (x, y) 网格坐标
                - light_level: 目标位置光照等级
            battle_map: 可选 BattleMap 实例
            conditions: 可选额外条件列表

        Returns:
            VisibilityResult
        """
        result = VisibilityResult()
        conditions = conditions or []

        # 检查观察者是否失明
        if "blinded" in conditions or "blinded" in observer.get("conditions", []):
            result.level = VisibilityLevel.HIDDEN
            result.line_of_sight = False
            result.line_of_effect = False
            result.reasons.append("观察者处于失明状态")
            return result

        obs_pos = observer.get("position", (0, 0))
        tgt_pos = target.get("position", (0, 0))
        senses = observer.get("senses", {})

        # 计算距离
        distance_ft = 0.0
        if battle_map is not None:
            distance_ft = battle_map.get_distance_ft(obs_pos, tgt_pos)
        else:
            dx = abs(obs_pos[0] - tgt_pos[0])
            dy = abs(obs_pos[1] - tgt_pos[1])
            distance_ft = max(dx, dy) * 5.0

        # 使用 vision.py 的 can_see 进行基础视觉判定
        target_light = target.get("light_level", LIGHT_BRIGHT)
        if battle_map is not None:
            tgt_cell = battle_map.get_cell(*tgt_pos)
            target_light = tgt_cell.light_level

        vision_result = can_see(senses, target_light, distance_ft)

        # 映射到 VisibilityLevel
        if not vision_result["can_see"]:
            # 检查是否通过非视觉感官感知
            sense = vision_result.get("sense_used", "")
            if sense in ("blindsight", "tremorsense"):
                result.level = VisibilityLevel.LOCATED
                result.reasons.append(f"通过{sense}感知到目标位置")
            else:
                result.level = VisibilityLevel.HIDDEN
                result.reasons.append("无法看见目标")
        elif vision_result.get("disadvantage_perception"):
            result.level = VisibilityLevel.CONCEALED
            result.reasons.append("目标处于轻度遮蔽中")
        else:
            result.level = VisibilityLevel.VISIBLE

        # 视线检查
        if battle_map is not None:
            result.line_of_sight = battle_map.line_of_sight(obs_pos, tgt_pos)
            result.line_of_effect = battle_map.line_of_effect(obs_pos, tgt_pos)
            if not result.line_of_sight:
                result.reasons.append("视线被阻挡")

        # 掩护判定
        if battle_map is not None:
            cover_str = battle_map.get_cover_level(obs_pos, tgt_pos)
            result.cover = self._parse_cover(cover_str)
        else:
            result.cover = CoverLevel.NONE

        return result

    def check_cover(
        self,
        observer: Dict[str, Any],
        target: Dict[str, Any],
        battle_map: Any = None,
    ) -> CoverLevel:
        """判定掩护等级。

        Args:
            observer: 观察者信息（需含 position）
            target: 目标信息（需含 position）
            battle_map: BattleMap 实例

        Returns:
            CoverLevel
        """
        if battle_map is None:
            return CoverLevel.NONE

        obs_pos = observer.get("position", (0, 0))
        tgt_pos = target.get("position", (0, 0))
        cover_str = battle_map.get_cover_level(obs_pos, tgt_pos)
        return self._parse_cover(cover_str)

    def check_line_of_sight(
        self,
        observer: Dict[str, Any],
        target: Dict[str, Any],
        battle_map: Any = None,
    ) -> bool:
        """视线检查。"""
        if battle_map is None:
            return True
        obs_pos = observer.get("position", (0, 0))
        tgt_pos = target.get("position", (0, 0))
        return battle_map.line_of_sight(obs_pos, tgt_pos)

    def check_line_of_effect(
        self,
        observer: Dict[str, Any],
        target: Dict[str, Any],
        battle_map: Any = None,
    ) -> bool:
        """效应线检查。"""
        if battle_map is None:
            return True
        obs_pos = observer.get("position", (0, 0))
        tgt_pos = target.get("position", (0, 0))
        return battle_map.line_of_effect(obs_pos, tgt_pos)

    # ── 内部辅助 ──────────────────────────────────────────────────────

    @staticmethod
    def _parse_cover(cover_str: str) -> CoverLevel:
        """将字符串掩护等级映射为枚举。"""
        mapping = {
            "none": CoverLevel.NONE,
            "half": CoverLevel.HALF,
            "three_quarters": CoverLevel.THREE_QUARTERS,
            "full": CoverLevel.FULL,
        }
        return mapping.get(cover_str, CoverLevel.NONE)
