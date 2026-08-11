"""RngContext — 可注入的随机数生成器。

TEST-003: 随机结算不可稳定回放。
每个Command使用注入的RngContext；事件记录seed/roll_id/results；回放不重新掷骰。

规则依据: topics/城主指南2024/2.运作游戏/
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RollRecord:
    """单次掷骰记录。

    TEST-003: 事件记录seed/roll_id/results。
    """

    roll_id: str = ""             # 唯一掷骰 ID
    dice_expr: str = ""           # 骰子表达式（如 "1d20"）
    results: List[int] = field(default_factory=list)  # 每个骰子的结果
    total: int = 0                # 总计
    modifier: int = 0             # 调整值
    final: int = 0                # 最终值（total + modifier）


@dataclass
class RngContext:
    """可注入的随机数上下文。

    TEST-003: 每个Command使用注入的RngContext。
    """

    seed: int = 0
    _rng: random.Random = field(default=None, repr=False)
    _rolls: List[RollRecord] = field(default_factory=list, repr=False)
    _initialized: bool = False

    def __post_init__(self) -> None:
        if not self._initialized:
            self._rng = random.Random(self.seed)
            self._initialized = True

    def randbelow(self, exclusive_upper: int) -> int:
        """返回 [0, exclusive_upper)。

        TEST-003: 供 engine.dice 注入使用，保证确定性。
        """
        return self._rng.randrange(exclusive_upper)

    def roll_d20(self, advantage: bool = False,
                 disadvantage: bool = False) -> RollRecord:
        """掷 d20。"""
        import uuid

        rolls: List[int] = []
        num_dice = 2 if (advantage or disadvantage) else 1

        for _ in range(num_dice):
            rolls.append(self._rng.randint(1, 20))

        if advantage and len(rolls) == 2:
            used = max(rolls[0], rolls[1])
        elif disadvantage and len(rolls) == 2:
            used = min(rolls[0], rolls[1])
        else:
            used = rolls[0] if rolls else 1

        record = RollRecord(
            roll_id=str(uuid.uuid4()),
            dice_expr="1d20",
            results=rolls,
            total=used,
            modifier=0,
            final=used,
        )
        self._rolls.append(record)
        return record

    def roll_dice(self, dice_expr: str) -> RollRecord:
        """掷骰子。"""
        import re
        import uuid

        match = re.match(r"(\d+)d(\d+)", dice_expr)
        if not match:
            return RollRecord(
                roll_id=str(uuid.uuid4()),
                dice_expr=dice_expr,
                results=[],
                total=0,
                modifier=0,
                final=0,
            )

        num_dice = int(match.group(1))
        dice_sides = int(match.group(2))

        rolls: List[int] = []
        for _ in range(num_dice):
            rolls.append(self._rng.randint(1, dice_sides))

        total = sum(rolls)

        record = RollRecord(
            roll_id=str(uuid.uuid4()),
            dice_expr=dice_expr,
            results=rolls,
            total=total,
            modifier=0,
            final=total,
        )
        self._rolls.append(record)
        return record

    def get_all_rolls(self) -> List[RollRecord]:
        """获取所有掷骰记录。"""
        return list(self._rolls)

    def replay(self) -> "RngContext":
        """创建一个可重放的副本。"""
        return RngContext(seed=self.seed)


def create_rng_context(seed: int = 0) -> RngContext:
    """创建一个 RngContext 实例。"""
    return RngContext(seed=seed)
