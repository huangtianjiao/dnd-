"""持续时间调度器 — DurationScheduler。

管理所有有时限效果的到期判定、回合边界触发、休息恢复、重复豁免等。
与 effects.py 的 EffectInstance/DurationSpec 互补：EffectManager 管理效果
的增删查改，DurationScheduler 管理时间维度的推进与到期事件。

规则依据:
  - R-SPL-017 持续时间类型（立即/轮/分钟/小时/直到休息/永久）
  - R-SPL-019 专注维持（持续法术在回合边界过期）
  - R-GLS-013 重复豁免（回合结束时再次豁免以结束效果）
出处: topics/玩家手册2024/法术/法术成分.htm ; 术语汇编/常见规则词汇.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from . import check as _check
from . import dice as _dice


# ──────────────────────────────────────────────────────────────────────────
# 枚举 & 数据类
# ──────────────────────────────────────────────────────────────────────────

class SchedulerDurationType(str, Enum):
    """调度器持续时间类型。

    与 effects.DurationType 对齐，此处独立定义以便调度器内部逻辑使用。
    """
    INSTANT = "instant"
    ROUNDS = "rounds"
    MINUTES = "minutes"
    HOURS = "hours"
    UNTIL_REST = "until_rest"
    PERMANENT = "permanent"


@dataclass
class RepeatSave:
    """重复豁免配置（R-GLS-013）。

    某些效果允许目标在每回合结束时重复豁免以结束效果。
    """
    ability: str = "wis"            # 豁免属性
    dc: int = 10                    # 豁免 DC
    end_on_success: bool = True     # 豁免成功则结束效果


@dataclass
class ScheduledEffect:
    """调度器中的一个已调度效果。

    规则: R-SPL-017 持续时间 / R-GLS-013 重复豁免
    """
    effect_id: str
    duration_type: SchedulerDurationType = SchedulerDurationType.INSTANT
    remaining: int = 0                      # 剩余时间单位（轮/分钟/小时）
    expire_on: str = ""                     # 到期触发点:
                                            # "source_turn_start" / "target_turn_end" /
                                            # "round_start" / "round_end"
    target_entity_id: str = ""              # 效果关联的实体 ID
    repeat_save: Optional[RepeatSave] = None
    on_expire: Optional[Callable] = None    # 到期时回调
    on_tick: Optional[Callable] = None      # 每时间单位回调
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """是否已到期（remaining <= 0 且非永久/立即）。"""
        if self.duration_type in (SchedulerDurationType.PERMANENT, SchedulerDurationType.INSTANT):
            return False
        return self.remaining <= 0


# ──────────────────────────────────────────────────────────────────────────
# DurationScheduler
# ──────────────────────────────────────────────────────────────────────────

class DurationScheduler:
    """持续时间调度器（SPL-009）。

    管理所有已调度效果的时间推进、到期判定、重复豁免。
    与 EffectManager 协作：EffectManager 管效果数据，本调度器管时间。
    """

    def __init__(self) -> None:
        self._scheduled: Dict[str, ScheduledEffect] = {}

    # ── 调度 / 取消 ─────────────────────────────────────────────────

    def schedule(self, effect: ScheduledEffect) -> str:
        """注册一个待调度效果。

        规则: R-SPL-017 持续时间
        返回: effect_id
        """
        self._scheduled[effect.effect_id] = effect
        return effect.effect_id

    def cancel(self, effect_id: str) -> bool:
        """取消一个已调度效果。

        规则: R-SPL-019 主动终止专注
        返回: 是否确实取消了（存在且被移除）
        """
        if effect_id not in self._scheduled:
            return False
        eff = self._scheduled.pop(effect_id)
        if eff.on_expire:
            eff.on_expire(effect_id, "cancelled")
        return True

    # ── 时间推进 ────────────────────────────────────────────────────

    def on_round_start(self, round_num: int) -> List[dict]:
        """轮开始时推进所有以 round 为单位的效果。

        规则: R-SPL-017 持续时间（轮）
        返回: 到期事件列表 [{"effect_id": ..., "reason": "expired"}, ...]
        """
        expired: list[dict] = []
        for eid, eff in list(self._scheduled.items()):
            if eff.duration_type == SchedulerDurationType.ROUNDS:
                # 轮开始时 tick
                if eff.expire_on in ("", "round_start"):
                    eff.remaining -= 1
                    if eff.on_tick:
                        eff.on_tick(eid, round_num)
                    if eff.is_expired:
                        expired.append({"effect_id": eid, "reason": "expired"})
                        self._remove_and_callback(eid, "expired")
        return expired

    def on_round_end(self, round_num: int) -> List[dict]:
        """轮结束时推进以 round_end 为到期点的效果。

        返回: 到期事件列表
        """
        expired: list[dict] = []
        for eid, eff in list(self._scheduled.items()):
            if eff.duration_type == SchedulerDurationType.ROUNDS:
                if eff.expire_on == "round_end":
                    eff.remaining -= 1
                    if eff.on_tick:
                        eff.on_tick(eid, round_num)
                    if eff.is_expired:
                        expired.append({"effect_id": eid, "reason": "expired"})
                        self._remove_and_callback(eid, "expired")
        return expired

    def on_turn_start(self, entity_id: str, round_num: int) -> List[dict]:
        """某实体回合开始时推进效果。

        规则: R-SPL-017 / R-SPL-019
        处理: expire_on="source_turn_start" 的效果减 1。
        返回: 到期事件列表
        """
        expired: list[dict] = []
        for eid, eff in list(self._scheduled.items()):
            if eff.duration_type == SchedulerDurationType.ROUNDS:
                if eff.expire_on == "source_turn_start" and eff.target_entity_id == entity_id:
                    eff.remaining -= 1
                    if eff.on_tick:
                        eff.on_tick(eid, round_num)
                    if eff.is_expired:
                        expired.append({"effect_id": eid, "reason": "expired"})
                        self._remove_and_callback(eid, "expired")
        return expired

    def on_turn_end(self, entity_id: str, round_num: int) -> List[dict]:
        """某实体回合结束时推进效果 + 处理重复豁免。

        规则: R-SPL-017 / R-GLS-013 重复豁免
        处理:
          1. expire_on="target_turn_end" 的效果减 1
          2. 有 repeat_save 的效果进行豁免检定
        返回: 到期事件 + 重复豁免事件列表
        """
        events: list[dict] = []

        # 1. 推进回合结束到期的效果
        for eid, eff in list(self._scheduled.items()):
            if eff.duration_type == SchedulerDurationType.ROUNDS:
                if eff.expire_on == "target_turn_end" and eff.target_entity_id == entity_id:
                    eff.remaining -= 1
                    if eff.on_tick:
                        eff.on_tick(eid, round_num)
                    if eff.is_expired:
                        events.append({"effect_id": eid, "reason": "expired"})
                        self._remove_and_callback(eid, "expired")

        # 2. 重复豁免 (R-GLS-013)
        repeat_events = self.tick_repeat_saves(entity_id)
        events.extend(repeat_events)

        return events

    def on_rest(self, rest_type: str) -> List[dict]:
        """休息时处理 until_rest 类型效果的到期。

        规则: R-SPL-003 长休恢复 / R-SPL-017 持续时间
        参数:
            rest_type: "short" 或 "long"
        返回: 到期事件列表
        """
        expired: list[dict] = []
        for eid, eff in list(self._scheduled.items()):
            if eff.duration_type == SchedulerDurationType.UNTIL_REST:
                # 短休或长休都结束 until_rest 效果
                rest_match = eff.metadata.get("rest_type", "long")
                if rest_match == "long" and rest_type == "short":
                    continue  # 需要长休的效果不因短休结束
                expired.append({"effect_id": eid, "reason": f"rest_{rest_type}"})
                self._remove_and_callback(eid, f"rest_{rest_type}")
        return expired

    # ── 重复豁免 ────────────────────────────────────────────────────

    def tick_repeat_saves(
        self,
        entity_id: str,
        rng: Any = None,
    ) -> List[dict]:
        """对指定实体执行所有关联效果的重复豁免检定。

        规则: R-GLS-013 重复豁免
              目标在每回合结束时进行豁免，成功则结束效果。
        参数:
            entity_id: 进行豁免的实体 ID
            rng: 可选随机数生成器（测试用）
        返回: 豁免事件列表
        """
        events: list[dict] = []
        for eid, eff in list(self._scheduled.items()):
            if eff.target_entity_id != entity_id:
                continue
            if eff.repeat_save is None:
                continue
            rs = eff.repeat_save
            # 进行豁免检定
            sv = _check.saving_throw(
                mod=0,
                prof=0,
                proficient=False,
                dc=rs.dc,
            )
            event = {
                "effect_id": eid,
                "type": "repeat_save",
                "ability": rs.ability,
                "dc": rs.dc,
                "roll": sv.d20,
                "total": sv.total,
                "success": sv.success,
            }
            if sv.success and rs.end_on_success:
                event["ended"] = True
                events.append(event)
                self._remove_and_callback(eid, "repeat_save_success")
            else:
                event["ended"] = False
                events.append(event)
        return events

    # ── 查询 ────────────────────────────────────────────────────────

    def get_active(self) -> List[ScheduledEffect]:
        """获取所有活跃（未到期）的已调度效果。"""
        return [e for e in self._scheduled.values() if not e.is_expired]

    def get_for_entity(self, entity_id: str) -> List[ScheduledEffect]:
        """获取指定实体的所有活跃已调度效果。"""
        return [
            e for e in self._scheduled.values()
            if e.target_entity_id == entity_id and not e.is_expired
        ]

    def has_effect(self, effect_id: str) -> bool:
        """指定 effect_id 是否仍在调度中。"""
        return effect_id in self._scheduled

    def count(self) -> int:
        """当前调度中的效果总数。"""
        return len(self._scheduled)

    # ── 内部 ────────────────────────────────────────────────────────

    def _remove_and_callback(self, effect_id: str, reason: str) -> None:
        """移除效果并触发回调。"""
        eff = self._scheduled.pop(effect_id, None)
        if eff is not None and eff.on_expire:
            eff.on_expire(effect_id, reason)
