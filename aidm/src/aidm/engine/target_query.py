"""目标查询与消歧 — TargetQuery / CandidateTarget。

INT-002: 自然语言目标解析不具备消歧与权限边界。
建立TargetQuery与CandidateTarget列表；需要玩家选择时返回ClarificationRequired。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class TargetType(str, Enum):
    """目标类型。"""

    ENEMY = "enemy"
    ALLY = "ally"
    SELF = "self"
    OBJECT = "object"
    AREA = "area"


@dataclass
class CandidateTarget:
    """候选目标。"""

    target_id: str
    name: str
    target_type: TargetType
    distance_ft: float = 0.0
    is_visible: bool = True
    hp_current: int = 0
    hp_max: int = 0
    conditions: List[str] = field(default_factory=list)


@dataclass
class TargetQuery:
    """目标查询 — 从自然语言构建的查询对象。

    INT-002: 需要玩家选择时返回ClarificationRequired，不得猜测。
    """

    raw_text: str = ""
    target_type: TargetType = TargetType.ENEMY
    max_range_ft: float = float("inf")
    require_visibility: bool = True
    require_los: bool = True          # 视线
    exclude_self: bool = True

    def filter_candidates(self, candidates: List[CandidateTarget]) -> List[CandidateTarget]:
        """根据查询条件过滤候选目标。"""
        result: List[CandidateTarget] = []
        for c in candidates:
            if c.target_type != self.target_type and self.target_type != TargetType.SELF:
                continue
            if self.require_visibility and not c.is_visible:
                continue
            if c.distance_ft > self.max_range_ft:
                continue
            result.append(c)
        return result


@dataclass
class TargetResolutionResult:
    """目标解析结果。"""

    resolved_targets: List[CandidateTarget] = field(default_factory=list)
    needs_clarification: bool = False
    clarification_prompt: str = ""
    error: str = ""

    @property
    def is_resolved(self) -> bool:
        """是否已解析到唯一目标。"""
        return len(self.resolved_targets) == 1

    @property
    def target(self) -> Optional[CandidateTarget]:
        """获取解析到的唯一目标。"""
        if self.is_resolved:
            return self.resolved_targets[0]
        return None


def resolve_target(query: TargetQuery,
                   candidates: List[CandidateTarget]) -> TargetResolutionResult:
    """解析目标查询。

    INT-002: 两个同名敌人时系统要求选择；不可见/超距目标不会进入候选。

    解析逻辑:
      1. 按查询条件过滤候选
      2. 如果只剩一个候选 → 直接返回
      3. 如果有多个候选 → 返回ClarificationRequired
      4. 如果没有候选 → 返回错误
    """
    filtered = query.filter_candidates(candidates)

    if len(filtered) == 0:
        return TargetResolutionResult(
            error="未找到符合条件的目标",
        )

    if len(filtered) == 1:
        return TargetResolutionResult(resolved_targets=filtered)

    # 多个候选 → 需要消歧
    names = [c.name for c in filtered]
    return TargetResolutionResult(
        resolved_targets=filtered,
        needs_clarification=True,
        clarification_prompt=f"存在多个目标({', '.join(names)})，请指定具体目标。",
    )
