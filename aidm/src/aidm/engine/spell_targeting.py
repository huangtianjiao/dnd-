"""法术目标验证服务 — 射程/视线/掩护/目标类型/区域合法性。

提供法术施放前的目标合法性验证、区域验证、合法目标枚举。
整合 VisibilityService、BattleMap、AoE 引擎进行综合判定。

规则依据:
  - R-SPL-014 施法距离（射程校验）
  - R-SPL-010~013 法术成分（视线/掩护对目标选择的影响）
  - R-AOE-001~007 效应区域六种形状 + 全身掩护阻挡
  - R-GLS-014 目标选择（你看见的生物 / 自愿生物等）
出处: topics/玩家手册2024/法术/法术成分.htm ; 术语汇编/效应区域.htm
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ──────────────────────────────────────────────────────────────────────────
# 枚举定义
# ──────────────────────────────────────────────────────────────────────────

class TargetType(str, Enum):
    """法术目标类型。"""
    SELF = "self"
    CREATURE = "creature"
    WILLING_CREATURE = "willing_creature"
    OBJECT = "object"
    POINT = "point"
    AREA = "area"
    CREATURES_IN_AREA = "creatures_in_area"
    VISIBLE_CREATURE = "visible_creature"


class AreaShape(str, Enum):
    """效应区域形状（与 aoe.py 对齐）。"""
    SPHERE = "sphere"
    CONE = "cone"
    LINE = "line"
    CUBE = "cube"
    CYLINDER = "cylinder"
    EMANATION = "emanation"


# ──────────────────────────────────────────────────────────────────────────
# 规格数据类
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class TargetSpec:
    """法术目标规格。

    规则: R-GLS-014 目标选择 / R-SPL-014 施法距离
    """
    target_type: TargetType = TargetType.CREATURE
    max_targets: int = 1
    requires_sight: bool = False          # 需要看见目标（如治愈真言）
    self_targetable: bool = False         # 可以选择自己
    blocked_by_full_cover: bool = True    # 全身掩护阻挡目标选择


@dataclass
class AreaSpec:
    """效应区域规格。

    规则: R-AOE-001~006 效应区域六种形状
    """
    shape: AreaShape = AreaShape.SPHERE
    size_ft: float = 0.0
    origin_rule: str = "target_point"     # "caster" / "target_point" / "touch_point"


@dataclass
class RangeSpec:
    """施法距离规格。

    规则: R-SPL-014 施法距离
    出处: topics/玩家手册2024/法术/法术成分.htm
    """
    range_ft: float = 0.0       # 0 = 自身
    is_touch: bool = False      # 触碰距离
    is_self: bool = False       # 自身距离


# ──────────────────────────────────────────────────────────────────────────
# 法术数据 → 规格解析
# ──────────────────────────────────────────────────────────────────────────

def _parse_range_from_spell(spell: Any) -> RangeSpec:
    """从法术数据解析施法距离。

    规则: R-SPL-014 施法距离
    出处: topics/玩家手册2024/法术详述/{0..9}环.htm
    """
    range_str = getattr(spell, "range", "") or ""
    if "自身" in range_str or range_str.lower() in ("self",):
        return RangeSpec(range_ft=0, is_self=True)
    if "触碰" in range_str or range_str.lower() in ("touch",):
        return RangeSpec(range_ft=5, is_touch=True)
    # 解析 "XX尺" 格式
    import re
    m = re.search(r"(\d+)\s*尺", range_str)
    if m:
        return RangeSpec(range_ft=float(m.group(1)))
    # 默认 30 尺
    return RangeSpec(range_ft=30)


def _parse_target_spec_from_spell(spell: Any) -> TargetSpec:
    """从法术数据推断目标规格。

    规则: R-GLS-014 目标选择
    """
    desc = (getattr(spell, "description", "") or "").lower()
    range_str = getattr(spell, "range", "") or ""
    effect_type = getattr(spell, "effect_type", "") or ""
    aoe_shape = getattr(spell, "aoe_shape", "") or ""

    # 自身法术
    if "自身" in range_str:
        return TargetSpec(target_type=TargetType.SELF, max_targets=1, self_targetable=True)

    # 有 AoE 形状 → 区域内生物
    if aoe_shape:
        return TargetSpec(
            target_type=TargetType.CREATURES_IN_AREA,
            max_targets=99,
            blocked_by_full_cover=True,
        )

    # 从描述推断
    if "自愿" in desc or "自愿生物" in desc:
        return TargetSpec(
            target_type=TargetType.WILLING_CREATURE,
            max_targets=_infer_max_targets(desc),
            requires_sight="看见" in desc,
        )
    if "物件" in desc and "生物" not in desc:
        return TargetSpec(target_type=TargetType.OBJECT, max_targets=1)
    if "你能看见" in desc or "你看见" in desc:
        return TargetSpec(
            target_type=TargetType.VISIBLE_CREATURE,
            max_targets=_infer_max_targets(desc),
            requires_sight=True,
        )

    # 默认：生物目标
    return TargetSpec(
        target_type=TargetType.CREATURE,
        max_targets=_infer_max_targets(desc),
    )


def _infer_max_targets(desc: str) -> int:
    """从描述推断最大目标数（简化启发式）。"""
    import re
    # "至多N个" / "至多 N 个"
    m = re.search(r"至多\s*(\d+)\s*(个|名)", desc)
    if m:
        return int(m.group(1))
    if "一个" in desc or "一名" in desc or "一个你" in desc:
        return 1
    if "六个" in desc:
        return 6
    if "三个" in desc:
        return 3
    return 1


def _parse_area_spec_from_spell(spell: Any) -> Optional[AreaSpec]:
    """从法术数据解析区域规格。"""
    aoe_shape = getattr(spell, "aoe_shape", "") or ""
    if not aoe_shape:
        return None
    aoe_size = getattr(spell, "aoe_size_ft", 0) or 0
    try:
        shape = AreaShape(aoe_shape)
    except ValueError:
        shape = AreaShape.SPHERE
    return AreaSpec(shape=shape, size_ft=float(aoe_size))


# ──────────────────────────────────────────────────────────────────────────
# SpellTargetingService
# ──────────────────────────────────────────────────────────────────────────

class SpellTargetingService:
    """法术目标验证服务（SPL-007）。

    整合 VisibilityService、BattleMap、AoE 引擎进行综合合法性判定。
    纯计算层，不产生面向玩家的文本。
    """

    def __init__(
        self,
        visibility_service: Any = None,
        battle_map: Any = None,
    ) -> None:
        self._vis = visibility_service
        self._map = battle_map

    # ── 目标验证 ────────────────────────────────────────────────────

    def validate_target(
        self,
        spell_id: str,
        caster: Dict[str, Any],
        target: Dict[str, Any],
        battle_map: Any = None,
    ) -> dict:
        """验证单个目标合法性：射程/视线/掩护/目标类型。

        规则: R-SPL-014 施法距离 / R-GLS-014 目标选择 /
              R-AOE-007 全身掩护阻挡
        出处: topics/玩家手册2024/法术/法术成分.htm

        参数:
            spell_id: 法术中文名
            caster: 施法者信息 dict
                - position: (x, y) 网格坐标
                - senses: {...}
                - conditions: List[str]
            target: 目标信息 dict
                - entity_id: str
                - position: (x, y)
                - is_willing: bool (可选)
                - is_creature: bool (默认 True)
                - is_object: bool (默认 False)
            battle_map: 可选 BattleMap 实例

        返回 dict:
            valid: bool
            reasons: List[str] — 不合法原因列表
            distance_ft: float — 实际距离
            cover: str — 掩护等级
        """
        from ..data.spells import get_spell
        try:
            spell = get_spell(spell_id)
        except KeyError:
            return {"valid": False, "reasons": [f"未知法术 {spell_id!r}"],
                    "distance_ft": 0, "cover": "none"}

        bmap = battle_map or self._map
        reasons: list[str] = []
        range_spec = _parse_range_from_spell(spell)
        target_spec = _parse_target_spec_from_spell(spell)

        # 距离计算
        caster_pos = caster.get("position", (0, 0))
        target_pos = target.get("position", (0, 0))
        distance_ft = self._calc_distance(caster_pos, target_pos, bmap)

        # 射程校验 (R-SPL-014)
        if range_spec.is_self:
            # 自身法术只能以自己为目标
            if target.get("entity_id", "") != caster.get("entity_id", ""):
                reasons.append("自身法术只能以自身为目标")
        elif not range_spec.is_touch:
            if distance_ft > range_spec.range_ft:
                reasons.append(
                    f"目标距离 {distance_ft:.0f} 尺超出射程 {range_spec.range_ft:.0f} 尺"
                )

        # 视线/可见性校验 (R-GLS-014)
        if target_spec.requires_sight:
            if self._vis is not None:
                vis_result = self._vis.check_visibility(
                    caster, target, bmap,
                )
                if vis_result.level.name == "HIDDEN":
                    reasons.append("无法看见目标")

        # 掩护校验 (R-AOE-007)
        cover_level = "none"
        if target_spec.blocked_by_full_cover and bmap is not None:
            cover_str = bmap.get_cover_level(caster_pos, target_pos)
            cover_level = cover_str
            if cover_str == "full":
                reasons.append("目标处于全身掩护后")

        # 目标类型校验
        is_willing = target.get("is_willing", False)
        is_creature = target.get("is_creature", True)
        is_object = target.get("is_object", False)

        if target_spec.target_type == TargetType.WILLING_CREATURE:
            if not is_willing:
                reasons.append("该法术需要自愿生物作为目标")
        elif target_spec.target_type == TargetType.OBJECT:
            if not is_object:
                reasons.append("该法术需要物件作为目标")

        return {
            "valid": len(reasons) == 0,
            "reasons": reasons,
            "distance_ft": distance_ft,
            "cover": cover_level,
        }

    # ── 区域验证 ────────────────────────────────────────────────────

    def validate_area(
        self,
        spell_id: str,
        origin_point: tuple[float, float],
        caster: Dict[str, Any] | None = None,
        battle_map: Any = None,
    ) -> dict:
        """验证区域放置合法性：射程/区域形状/尺寸。

        规则: R-AOE-001~006 效应区域 / R-SPL-014 施法距离
        出处: topics/玩家手册2024/术语汇编/效应区域.htm

        返回 dict:
            valid: bool
            reasons: List[str]
            area_spec: AreaSpec | None
        """
        from ..data.spells import get_spell
        try:
            spell = get_spell(spell_id)
        except KeyError:
            return {"valid": False, "reasons": [f"未知法术 {spell_id!r}"],
                    "area_spec": None}

        bmap = battle_map or self._map
        area_spec = _parse_area_spec_from_spell(spell)
        if area_spec is None:
            return {"valid": False, "reasons": ["该法术无效应区域"],
                    "area_spec": None}

        reasons: list[str] = []
        range_spec = _parse_range_from_spell(spell)

        # 区域原点射程校验
        if caster is not None and not range_spec.is_self:
            caster_pos = caster.get("position", (0, 0))
            dist = self._calc_distance(caster_pos, origin_point, bmap)
            if dist > range_spec.range_ft:
                reasons.append(
                    f"区域原点距离 {dist:.0f} 尺超出射程 {range_spec.range_ft:.0f} 尺"
                )

        return {
            "valid": len(reasons) == 0,
            "reasons": reasons,
            "area_spec": area_spec,
        }

    # ── 合法目标枚举 ────────────────────────────────────────────────

    def get_valid_targets(
        self,
        spell_id: str,
        caster: Dict[str, Any],
        all_entities: Dict[str, Dict[str, Any]] | None = None,
        battle_map: Any = None,
    ) -> List[str]:
        """获取所有合法目标 ID 列表。

        规则: R-SPL-014 / R-GLS-014
        参数:
            spell_id: 法术名
            caster: 施法者信息 dict (含 position, senses, entity_id)
            all_entities: {entity_id: {position, is_creature, is_willing, ...}}
            battle_map: BattleMap 实例
        返回: 合法目标 ID 列表
        """
        if all_entities is None:
            return []

        valid_ids: list[str] = []
        for eid, info in all_entities.items():
            # 排除自身（非自身法术时）
            result = self.validate_target(spell_id, caster, info, battle_map)
            if result["valid"]:
                valid_ids.append(eid)
        return valid_ids

    # ── 内部工具 ────────────────────────────────────────────────────

    @staticmethod
    def _calc_distance(
        pos_a: tuple[float, float],
        pos_b: tuple[float, float],
        bmap: Any = None,
    ) -> float:
        """计算两点间距离（尺）。

        有 BattleMap 时用其距离计算（网格×5尺），否则用欧氏距离×5。
        """
        if bmap is not None:
            try:
                return bmap.get_distance_ft(pos_a, pos_b)
            except Exception:
                pass
        dx = abs(pos_a[0] - pos_b[0])
        dy = abs(pos_a[1] - pos_b[1])
        return max(dx, dy) * 5.0


# ──────────────────────────────────────────────────────────────────────────
# 便捷函数
# ──────────────────────────────────────────────────────────────────────────

def get_spell_target_spec(spell_id: str) -> dict:
    """获取法术的目标/射程/区域规格（纯数据查询）。

    返回 dict:
        range_spec: RangeSpec
        target_spec: TargetSpec
        area_spec: AreaSpec | None
    """
    from ..data.spells import get_spell
    spell = get_spell(spell_id)
    return {
        "range_spec": _parse_range_from_spell(spell),
        "target_spec": _parse_target_spec_from_spell(spell),
        "area_spec": _parse_area_spec_from_spell(spell),
    }
