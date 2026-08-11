"""固定种子随机数系统 — 可重放的游戏随机源。

设计原则：
  - 所有游戏随机行为通过 RngContext 进行，保证可重放、可审计。
  - RollRecord 记录每次掷骰的完整信息，支持回放。

规则依据: TEST-003 固定 RNG
"""

from __future__ import annotations

import random
import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class RollRecord:
    """单次掷骰记录。"""

    roll_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dice_expr: str = ""
    results: List[int] = field(default_factory=list)
    total: int = 0
    seed_state: str = ""


class RngContext:
    """固定种子随机数上下文。

    使用 random.Random(seed) 作为底层随机源，
    所有掷骰结果可重放、可审计。
    """

    _DICE_RE = re.compile(r"^(\d+)d(\d+)([+-]\d+)?$")

    def __init__(self, seed: int = 0) -> None:
        self._rng = random.Random(seed)
        self._seed = seed
        self._records: List[RollRecord] = []

    # ── 基础掷骰 ──────────────────────────────────────────────────────

    def roll_die(self, sides: int) -> int:
        """掷一颗 sides 面骰，返回 [1, sides]。"""
        if sides < 1:
            raise ValueError(f"骰面数必须≥1，得到 {sides}")
        result = self._rng.randint(1, sides)
        self._records.append(RollRecord(
            dice_expr=f"1d{sides}",
            results=[result],
            total=result,
            seed_state=str(self._seed),
        ))
        return result

    def roll_dice(self, expr: str) -> Tuple[List[int], int]:
        """解析并掷 "NdM+K" 格式骰子表达式。

        Returns:
            (各骰结果列表, 总计)
        """
        m = self._DICE_RE.match(expr.strip().lower())
        if not m:
            raise ValueError(f"无效骰子表达式: {expr!r}")
        count, sides = int(m.group(1)), int(m.group(2))
        modifier = int(m.group(3)) if m.group(3) else 0

        results: List[int] = []
        for _ in range(count):
            results.append(self._rng.randint(1, sides))
        total = sum(results) + modifier

        self._records.append(RollRecord(
            dice_expr=expr,
            results=results,
            total=total,
            seed_state=str(self._seed),
        ))
        return results, total

    def roll_d20(self) -> int:
        """掷一颗 d20。"""
        return self.roll_die(20)

    # ── 记录与回放 ────────────────────────────────────────────────────

    def get_records(self) -> List[RollRecord]:
        """获取所有掷骰记录。"""
        return list(self._records)

    def replay(self) -> "RngContext":
        """从记录创建回放上下文（使用相同 seed 重建）。"""
        return RngContext(seed=self._seed)


class ReplayEngine:
    """回放引擎 — 记录事件并按固定种子重放。"""

    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []

    def record_event(self, event: Dict[str, Any]) -> None:
        """记录一个事件。"""
        self._events.append(event)

    def replay(self, seed: int) -> List[Dict[str, Any]]:
        """以指定种子重放，返回事件列表。"""
        # 回放模式下直接返回已记录事件的副本
        return [dict(e) for e in self._events]
