"""法术持续时间调度 — DurationSpec / Scheduler。

SPL-009: 持续时间和结束条件没有时间调度。
DurationSpec支持instant/rounds/minutes/hours/until_rest/permanent；
Scheduler在TimingPoint触发tick与expire。

规则依据: topics/玩家手册2024/法术/持续时间.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class DurationType(str, Enum):
    """持续时间类型。"""

    INSTANT = "instant"           # 瞬间（立即结算）
    ROUNDS = "rounds"             # N 轮
    MINUTES = "minutes"           # N 分钟（战斗外）
    HOURS = "hours"               # N 小时
    UNTIL_REST = "until_rest"     # 直到短休/长休
    PERMANENT = "permanent"       # 永久


@dataclass
class DurationSpec:
    """持续时间规格。

    SPL-009: 支持多种时间类型。
    """

    duration_type: DurationType = DurationType.INSTANT
    value: int = 0                # 总持续时间（轮/分钟/小时）
    remaining: int = 0            # 剩余时间

    def is_expired(self) -> bool:
        """判断效果是否已过期。"""
        if self.duration_type == DurationType.PERMANENT:
            return False
        if self.duration_type == DurationType.INSTANT:
            return True
        return self.remaining <= 0

    def tick(self) -> bool:
        """推进一个时间单位，返回是否已过期。"""
        if self.duration_type not in (DurationType.ROUNDS, DurationType.MINUTES, DurationType.HOURS):
            return self.is_expired()
        self.remaining = max(0, self.remaining - 1)
        return self.is_expired()


@dataclass
class ScheduledEffect:
    """已调度的持续效果。"""

    effect_id: str                          # 效果实例 ID
    spell_id: str                           # 来源法术 ID
    target_entity_id: str                   # 目标实体 ID
    duration: DurationSpec = field(default_factory=DurationSpec)
    tick_damage_dice: str = ""              # 每轮伤害骰（如中毒）
    end_save_ability: str = ""              # 结束时豁免属性
    end_save_dc: int = 10                   # 结束时豁免 DC


@dataclass
class DurationScheduler:
    """持续时间调度器。

    SPL-009: Scheduler在TimingPoint触发tick与expire。
    """

    _effects: Dict[str, ScheduledEffect] = field(default_factory=dict)

    def schedule(self, effect: ScheduledEffect) -> str:
        """调度一个持续效果，返回 effect_id。"""
        self._effects[effect.effect_id] = effect
        return effect.effect_id

    def cancel(self, effect_id: str) -> bool:
        """取消一个持续效果。"""
        return self._effects.pop(effect_id, None) is not None

    def tick_round(self) -> List[dict]:
        """每轮推进所有持续效果，返回事件列表。"""
        events: List[dict] = []
        expired_ids: List[str] = []

        for eid, eff in self._effects.items():
            if eff.duration.duration_type != DurationType.ROUNDS:
                continue
            if eff.duration.tick():
                expired_ids.append(eid)
                events.append({
                    "type": "effect_expired",
                    "effect_id": eid,
                    "spell_id": eff.spell_id,
                    "target": eff.target_entity_id,
                })

        for eid in expired_ids:
            del self._effects[eid]

        return events

    def expire_all_on_rest(self) -> List[dict]:
        """休息时过期所有 until_rest 效果。"""
        events: List[dict] = []
        expired_ids: List[str] = []

        for eid, eff in self._effects.items():
            if eff.duration.duration_type == DurationType.UNTIL_REST:
                expired_ids.append(eid)
                events.append({
                    "type": "effect_expired_on_rest",
                    "effect_id": eid,
                    "spell_id": eff.spell_id,
                    "target": eff.target_entity_id,
                })

        for eid in expired_ids:
            del self._effects[eid]

        return events
