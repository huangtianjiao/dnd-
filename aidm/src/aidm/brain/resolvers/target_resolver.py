"""目标解析消歧 — INT-002。

当玩家指定目标时，如果有多个同名敌人，返回候选列表要求消歧。
不可见目标和超出射程的目标排除在候选之外。

★ 整合：复用 engine.target_query.TargetQuery / CandidateTarget 作为统一底层原语
  （TargetType 枚举、射程/可见性过滤、ClarificationRequired 语义），
  brain 层负责从 combat_state 构建候选并适配返回格式。

规则依据: INT-002 目标解析消歧
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ...engine.target_query import (
    CandidateTarget as _EngineCandidate,
    TargetQuery as _EngineQuery,
    TargetType,
    resolve_target as _resolve_engine_target,
)


@dataclass
class TargetCandidate:
    """目标候选。"""
    entity_id: str
    name: str
    distance_ft: float = 0.0
    visibility: str = "visible"  # visible/hidden/invisible
    is_valid: bool = True
    reason_invalid: str = ""


@dataclass
class TargetResolutionResult:
    """目标解析结果。"""
    candidates: List[TargetCandidate] = field(default_factory=list)
    ambiguous: bool = False
    error: str = ""
    resolved_target: Optional[str] = None  # 如果唯一确定，直接返回目标 ID

    def to_dict(self) -> dict:
        return {
            "candidates": [
                {
                    "entity_id": c.entity_id,
                    "name": c.name,
                    "distance_ft": c.distance_ft,
                    "visibility": c.visibility,
                    "is_valid": c.is_valid,
                    "reason_invalid": c.reason_invalid,
                }
                for c in self.candidates
            ],
            "ambiguous": self.ambiguous,
            "error": self.error,
            "resolved_target": self.resolved_target,
        }


def _build_engine_candidates(
    combat_state: Any,
    target_name: str,
    attacker_position: Optional[tuple],
    max_range_ft: float,
) -> tuple[Optional[str], List[_EngineCandidate]]:
    """从 combat_state 构建 engine 候选列表。

    Returns:
        (attacker_id, candidates) — attacker_id 为 None 表示攻击者不在战斗中
    """
    participants = getattr(combat_state, "participants", [])
    attacker_id_found = None
    candidates: List[_EngineCandidate] = []

    for p in participants:
        pid = getattr(p, "id", None) or getattr(p, "cid", "")
        if not attacker_id_found and _is_attacker(p):
            attacker_id_found = pid
        if getattr(p, "dead", False):
            continue
        p_name = getattr(p, "name", "")
        if not target_name or target_name.lower() in p_name.lower() or p_name.lower() in target_name.lower():
            distance = _compute_distance(attacker_position or getattr(p, "position", None),
                                         getattr(p, "position", None), max_range_ft)
            candidates.append(_EngineCandidate(
                target_id=pid,
                name=p_name,
                target_type=TargetType.ENEMY,
                distance_ft=distance,
                is_visible=True,
            ))
    return attacker_id_found, candidates


def _is_attacker(p) -> bool:
    """是否为攻击者（非敌对方参战者）。"""
    side = getattr(p, "side", "")
    return side == "player" or (not side and not getattr(p, "is_player", False) is False)


def _compute_distance(attacker_position, entity_position, max_range_ft: float) -> float:
    """计算两点距离（每格 5 尺）。"""
    if attacker_position and entity_position:
        dx = attacker_position[0] - entity_position[0]
        dy = attacker_position[1] - entity_position[1]
        return (dx * dx + dy * dy) ** 0.5 * 5
    return 5.0


def resolve_target(
    target_name: str,
    attacker_id: str,
    combat_state: Any,
    *,
    max_range_ft: float = 0,  # 0 = 仅近战
    attacker_position: Optional[tuple] = None,
    visibility_service: Any = None,
) -> TargetResolutionResult:
    """解析目标，处理同名消歧。

    Args:
        target_name: 玩家指定的目标名称
        attacker_id: 攻击者 ID
        combat_state: 战斗状态（engine.combat.Combat 或类似结构）
        max_range_ft: 最大射程（0 = 仅近战，5尺）
        attacker_position: 攻击者位置 (x, y)
        visibility_service: 可见性服务（可选）

    Returns:
        TargetResolutionResult: 包含候选列表、是否歧义、错误信息
    """
    result = TargetResolutionResult()

    if not combat_state or not getattr(combat_state, "active", False):
        result.error = "战斗未激活"
        return result

    # 获取攻击者
    participants = getattr(combat_state, "participants", [])
    attacker = None
    for p in participants:
        if getattr(p, "id", None) == attacker_id or getattr(p, "cid", None) == attacker_id:
            attacker = p
            break

    if attacker is None:
        result.error = "攻击者不在战斗中"
        return result

    # 获取攻击者位置
    if attacker_position is None:
        attacker_position = getattr(attacker, "position", None)

    # ★ 整合：构建 engine 候选并复用 TargetQuery 过滤（射程/可见性）
    effective_range = max_range_ft if max_range_ft > 0 else 5
    engine_candidates = []
    for p in participants:
        if getattr(p, "id", None) == attacker_id or getattr(p, "cid", None) == attacker_id:
            continue
        if getattr(p, "dead", False):
            continue
        p_name = getattr(p, "name", "")
        if target_name and not (target_name.lower() in p_name.lower()
                                or p_name.lower() in target_name.lower()):
            continue
        distance = _compute_distance(attacker_position, getattr(p, "position", None),
                                     effective_range)
        engine_candidates.append(_EngineCandidate(
            target_id=getattr(p, "id", None) or getattr(p, "cid", ""),
            name=p_name,
            target_type=TargetType.ENEMY,
            distance_ft=distance,
            is_visible=True,
        ))

    if not engine_candidates:
        result.error = f"找不到名为 '{target_name}' 的目标"
        return result

    # 使用 engine.target_query 的查询语义做过滤
    query = _EngineQuery(
        raw_text=target_name,
        target_type=TargetType.ENEMY,
        max_range_ft=effective_range,
        require_visibility=False,  # 可见性由 visibility_service 单独检查
    )
    filtered = query.filter_candidates(engine_candidates)

    # 可见性过滤（保留原有 visibility_service 逻辑）
    valid_candidates: List[TargetCandidate] = []
    for cand in filtered:
        entity_id = cand.target_id
        visibility = "visible"
        if visibility_service is not None:
            try:
                vis_result = visibility_service.check_visibility(attacker_id, entity_id)
                visibility = getattr(vis_result, "level", "visible")
            except Exception:
                pass
        if visibility in ("invisible", "hidden"):
            result.candidates.append(TargetCandidate(
                entity_id=entity_id,
                name=cand.name,
                distance_ft=cand.distance_ft,
                visibility=visibility,
                is_valid=False,
                reason_invalid=f"目标不可见 ({visibility})",
            ))
            continue
        tc = TargetCandidate(
            entity_id=entity_id,
            name=cand.name,
            distance_ft=cand.distance_ft,
            visibility=visibility,
            is_valid=True,
        )
        valid_candidates.append(tc)
        result.candidates.append(tc)

    # 判断结果
    if not valid_candidates:
        result.error = "没有有效的目标（所有候选均超出射程或不可见）"
        return result

    if len(valid_candidates) == 1:
        # 唯一目标
        result.resolved_target = valid_candidates[0].entity_id
        result.ambiguous = False
    else:
        # 多个有效候选，需要消歧
        result.ambiguous = True
        result.error = f"找到 {len(valid_candidates)} 个同名目标，请指定具体目标"

    return result


def resolve_target_by_id(
    target_id: str,
    attacker_id: str,
    combat_state: Any,
    *,
    max_range_ft: float = 0,
    attacker_position: Optional[tuple] = None,
    visibility_service: Any = None,
) -> TargetResolutionResult:
    """通过 ID 直接解析目标（无需消歧）。

    仍然检查射程和可见性。
    """
    result = TargetResolutionResult()

    if not combat_state or not getattr(combat_state, "active", False):
        result.error = "战斗未激活"
        return result

    participants = getattr(combat_state, "participants", [])
    attacker = None
    target = None

    for p in participants:
        pid = getattr(p, "id", None) or getattr(p, "cid", "")
        if pid == attacker_id:
            attacker = p
        if pid == target_id:
            target = p

    if attacker is None:
        result.error = "攻击者不在战斗中"
        return result

    if target is None:
        result.error = f"目标 {target_id} 不在战斗中"
        return result

    if getattr(target, "dead", False):
        result.error = "目标已死亡"
        return result

    # 计算距离
    if attacker_position is None:
        attacker_position = getattr(attacker, "position", None)
    entity_position = getattr(target, "position", None)
    distance = 5.0
    if attacker_position and entity_position:
        dx = attacker_position[0] - entity_position[0]
        dy = attacker_position[1] - entity_position[1]
        distance = (dx * dx + dy * dy) ** 0.5 * 5

    # 检查射程
    effective_range = max_range_ft if max_range_ft > 0 else 5
    if distance > effective_range:
        result.error = f"目标超出射程 ({distance:.0f}尺 > {effective_range:.0f}尺)"
        return result

    # 检查可见性
    visibility = "visible"
    if visibility_service is not None:
        try:
            vis_result = visibility_service.check_visibility(attacker_id, target_id)
            visibility = getattr(vis_result, "level", "visible")
            if visibility in ("invisible", "hidden"):
                result.error = f"目标不可见 ({visibility})"
                return result
        except Exception:
            pass

    result.resolved_target = target_id
    result.candidates.append(TargetCandidate(
        entity_id=target_id,
        name=getattr(target, "name", ""),
        distance_ft=distance,
        visibility=visibility,
        is_valid=True,
    ))
    return result
