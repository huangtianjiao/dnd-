"""法术置信度标注 — 法术字段置信度标注与审校门禁。

设计原则：
  - SpellConfidence 记录每个法术各字段的自动解析置信度。
  - SpellConfidenceRegistry 管理所有法术的置信度注册表。
  - is_publishable 判断法术是否达到发布标准（已审校 或 最低置信度 >= 0.9）。

规则依据:
  DATA-001 法术置信度标注
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ──────────────────────────────────────────────────────────────────────────
# 法术置信度
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class SpellConfidence:
    """单个法术的字段置信度标注 (DATA-001)。

    属性:
        spell_id: 法术 ID（中文名或英文 ID）
        field_confidences: 各字段置信度映射
            如 {"damage": 0.95, "save_ability": 1.0, "effect_type": 0.7}
        reviewed: 是否已人工审校
        reviewer: 审校者标识
    """

    spell_id: str
    field_confidences: Dict[str, float] = field(default_factory=dict)
    reviewed: bool = False
    reviewer: str = ""

    @property
    def min_confidence(self) -> float:
        """最低字段置信度。

        Returns:
            所有字段中最低的置信度值；若无字段则为 0.0
        """
        return min(self.field_confidences.values()) if self.field_confidences else 0.0

    @property
    def avg_confidence(self) -> float:
        """平均字段置信度。

        Returns:
            所有字段的平均置信度；若无字段则为 0.0
        """
        if not self.field_confidences:
            return 0.0
        return sum(self.field_confidences.values()) / len(self.field_confidences)

    @property
    def is_publishable(self) -> bool:
        """是否达到发布标准。

        发布条件:
          - 已人工审校 (reviewed=True)，或
          - 最低字段置信度 >= 0.9

        Returns:
            是否可发布
        """
        return self.reviewed or self.min_confidence >= 0.9

    def get_low_confidence_fields(self, threshold: float = 0.8) -> List[str]:
        """获取低于指定阈值的字段列表。

        Args:
            threshold: 置信度阈值

        Returns:
            低于阈值的字段名列表
        """
        return [
            field_name
            for field_name, conf in self.field_confidences.items()
            if conf < threshold
        ]

    def mark_reviewed(self, reviewer: str = "") -> None:
        """标记为已审校。

        Args:
            reviewer: 审校者标识
        """
        self.reviewed = True
        self.reviewer = reviewer

    def update_field_confidence(self, field_name: str, confidence: float) -> None:
        """更新单个字段的置信度。

        Args:
            field_name: 字段名
            confidence: 置信度值 (0.0-1.0)
        """
        self.field_confidences[field_name] = max(0.0, min(1.0, confidence))


# ──────────────────────────────────────────────────────────────────────────
# 法术置信度注册表
# ──────────────────────────────────────────────────────────────────────────

class SpellConfidenceRegistry:
    """法术置信度注册表 (DATA-001)。

    管理所有法术的置信度信息，提供查询和审校门禁功能。
    """

    def __init__(self) -> None:
        self._confidences: Dict[str, SpellConfidence] = {}

    def register(
        self,
        spell_id: str,
        confidences: Dict[str, float],
        reviewed: bool = False,
        reviewer: str = "",
    ) -> SpellConfidence:
        """注册或更新法术的置信度信息。

        Args:
            spell_id: 法术 ID
            confidences: 各字段置信度映射
            reviewed: 是否已人工审校
            reviewer: 审校者标识

        Returns:
            创建或更新的 SpellConfidence 实例
        """
        if spell_id in self._confidences:
            # 更新已有记录
            existing = self._confidences[spell_id]
            existing.field_confidences.update(confidences)
            if reviewed:
                existing.mark_reviewed(reviewer)
            return existing
        else:
            # 创建新记录
            sc = SpellConfidence(
                spell_id=spell_id,
                field_confidences=dict(confidences),
                reviewed=reviewed,
                reviewer=reviewer,
            )
            self._confidences[spell_id] = sc
            return sc

    def get(self, spell_id: str) -> Optional[SpellConfidence]:
        """获取法术的置信度信息。

        Args:
            spell_id: 法术 ID

        Returns:
            SpellConfidence 实例，若未注册则返回 None
        """
        return self._confidences.get(spell_id)

    def is_publishable(self, spell_id: str) -> bool:
        """判断法术是否达到发布标准。

        Args:
            spell_id: 法术 ID

        Returns:
            是否可发布（未注册的法术默认可发布）
        """
        sc = self._confidences.get(spell_id)
        if sc is None:
            # 未注册置信度的法术默认可发布（视为已有足够信心）
            return True
        return sc.is_publishable

    def get_unreviewed(self) -> List[str]:
        """获取所有未审校的法术 ID 列表。

        Returns:
            未审校的法术 ID 列表
        """
        return [
            spell_id
            for spell_id, sc in self._confidences.items()
            if not sc.reviewed
        ]

    def get_low_confidence_spells(self, threshold: float = 0.8) -> List[str]:
        """获取所有存在低置信度字段的法术 ID 列表。

        Args:
            threshold: 置信度阈值

        Returns:
            存在低置信度字段的法术 ID 列表
        """
        return [
            spell_id
            for spell_id, sc in self._confidences.items()
            if sc.min_confidence < threshold
        ]

    def get_all(self) -> Dict[str, SpellConfidence]:
        """获取所有已注册的置信度信息。

        Returns:
            法术 ID 到 SpellConfidence 的映射
        """
        return dict(self._confidences)

    def count(self) -> int:
        """已注册法术数量。"""
        return len(self._confidences)

    def count_publishable(self) -> int:
        """可发布法术数量。"""
        return sum(1 for sc in self._confidences.values() if sc.is_publishable)

    def mark_reviewed(self, spell_id: str, reviewer: str = "") -> bool:
        """标记指定法术为已审校。

        Args:
            spell_id: 法术 ID
            reviewer: 审校者标识

        Returns:
            是否成功标记（未注册的法术返回 False）
        """
        sc = self._confidences.get(spell_id)
        if sc is None:
            return False
        sc.mark_reviewed(reviewer)
        return True
