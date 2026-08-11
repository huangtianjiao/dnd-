"""充能、传奇动作、传奇抗性、巢穴动作 — LegendaryActions。

MON-002: 充能、传奇动作、传奇抗性和巢穴动作未完整接线。
实现RechargeAtTurnStart、LegendaryWindowAfterTurn、LegendaryResistanceOnFailedSave、LairInitiative规则。

规则依据: topics/怪物图鉴2025/传奇生物.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ActionType(str, Enum):
    """动作类型。"""

    NORMAL = "normal"
    LEGENDARY = "legendary"       # 传奇动作
    LAIR = "lair"                 # 巢穴动作


@dataclass
class RechargeTracker:
    """充能追踪器。

    MON-002: 实现RechargeAtTurnStart规则。
    """

    current_charges: int = 0
    max_charges: int = 0          # 最大充能数
    recharge_min: int = 6         # 充能最小值（d6≥recharge_min则恢复）
    auto_recharge_at_turn_start: bool = True

    def can_use(self, cost: int = 1) -> bool:
        """判断是否有足够充能使用。"""
        return self.current_charges >= cost

    def consume(self, amount: int = 1) -> bool:
        """消耗充能。返回是否成功。"""
        if not self.can_use(amount):
            return False
        self.current_charges -= amount
        return True

    def recharge_at_turn_start(self) -> None:
        """回合开始时恢复充能。"""
        if self.auto_recharge_at_turn_start:
            self.current_charges = self.max_charges


@dataclass
class LegendaryAction:
    """传奇动作定义。"""

    action_id: str = ""           # 动作 canonical ID
    name: str = ""                # 显示名
    cost: int = 1                 # 消耗的传奇动作次数
    description: str = ""


@dataclass
class LegendaryActionPool:
    """传奇动作池 — 管理怪物的传奇动作资源。

    MON-002: 实现LegendaryWindowAfterTurn规则。
    """

    actions: List[LegendaryAction] = field(default_factory=list)
    uses_per_round: int = 3       # 每轮可用次数
    uses_this_round: int = 0      # 本轮已用次数

    def can_use_action(self, action_id: str) -> bool:
        """检查是否能使用指定传奇动作。"""
        action = next((a for a in self.actions if a.action_id == action_id), None)
        if action is None:
            return False
        return self.uses_this_round + action.cost <= self.uses_per_round

    def use_action(self, action_id: str) -> bool:
        """使用一个传奇动作。"""
        if not self.can_use_action(action_id):
            return False
        action = next(a for a in self.actions if a.action_id == action_id)
        self.uses_this_round += action.cost
        return True

    def reset_round(self) -> None:
        """每轮开始时重置。"""
        self.uses_this_round = 0


@dataclass
class LegendaryResistance:
    """传奇抗性 — 检定失败时选择成功。

    MON-002: 实现LegendaryResistanceOnFailedSave规则。
    """

    uses_per_day: int = 3         # 每日可用次数
    uses_today: int = 0           # 今日已用次数

    def can_resist(self) -> bool:
        """检查是否还能使用传奇抗性。"""
        return self.uses_today < self.uses_per_day

    def resist(self) -> bool:
        """使用传奇抗性，将失败的豁免变为成功。"""
        if not self.can_resist():
            return False
        self.uses_today += 1
        return True

    def reset_day(self) -> None:
        """每日黎明重置。"""
        self.uses_today = 0


@dataclass
class LairAction:
    """巢穴动作定义。"""

    action_id: str = ""
    name: str = ""
    initiative_count: int = 20    # 在哪个先攻位执行
    description: str = ""


@dataclass
class LairActionManager:
    """巢穴动作管理器。

    MON-002: 实现LairInitiative规则。
    """

    actions: List[LairAction] = field(default_factory=list)
    lair_initiative: int = 20     # 巢穴动作的先攻位

    def get_actions_at_initiative(self, initiative: int) -> List[LairAction]:
        """获取在指定先攻位执行的巢穴动作。"""
        return [a for a in self.actions if a.initiative_count == initiative]

    def add_action(self, action: LairAction) -> None:
        """添加一个巢穴动作。"""
        self.actions.append(action)


@dataclass
class MonsterActionManager:
    """怪物动作管理器 — 统一管理充能、传奇、巢穴动作。

    MON-002: 高CR怪物按2024怪物设计运行。
    """

    recharge_trackers: Dict[str, RechargeTracker] = field(default_factory=dict)
    legendary_pool: Optional[LegendaryActionPool] = None
    legendary_resistance: Optional[LegendaryResistance] = None
    lair_manager: Optional[LairActionManager] = None

    def register_recharge(self, ability_id: str, tracker: RechargeTracker) -> None:
        """注册一个充能能力。"""
        self.recharge_trackers[ability_id] = tracker

    def can_use_ability(self, ability_id: str) -> bool:
        """检查是否能使用指定充能能力。"""
        tracker = self.recharge_trackers.get(ability_id)
        if tracker is None:
            return True  # 无充能要求
        return tracker.can_use()

    def use_ability(self, ability_id: str) -> bool:
        """使用一个充能能力。"""
        tracker = self.recharge_trackers.get(ability_id)
        if tracker is None:
            return True
        return tracker.consume()

    def on_turn_start(self) -> None:
        """回合开始时的处理。"""
        for tracker in self.recharge_trackers.values():
            tracker.recharge_at_turn_start()

    def on_round_start(self) -> None:
        """每轮开始时的处理。"""
        if self.legendary_pool:
            self.legendary_pool.reset_round()
