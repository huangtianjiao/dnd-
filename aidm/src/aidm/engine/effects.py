"""效果系统 — EffectInstance 效果生命周期与 EffectManager。

设计原则：
  - 每个效果（buff/debuff/持续区域等）都是 EffectInstance，有明确的来源、持续时间、堆叠策略。
  - EffectManager 统一管理所有活跃效果的增删、过期判定、修正收集。

规则依据: STATE-002 EffectInstance 效果生命周期
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class DurationType(str, Enum):
    """效果持续时间类型。"""

    INSTANT = "instant"           # 瞬间（立即结算）
    ROUNDS = "rounds"             # N 轮
    MINUTES = "minutes"           # N 分钟（战斗外）
    HOURS = "hours"               # N 小时
    UNTIL_REST = "until_rest"     # 直到短休/长休
    PERMANENT = "permanent"       # 永久


class StackPolicyType(str, Enum):
    """效果堆叠策略。"""

    NO_STACK = "no_stack"         # 不堆叠，已存在则忽略
    STACK = "stack"               # 可堆叠，各自独立
    OVERRIDE = "override"         # 覆盖，新效果替换旧效果


class TriggerSpec:
    """触发规格 — 描述效果的触发条件和时机。

    STATE-002: 效果生命周期模型。
    用于回合开始/结束、受伤时、攻击命中时等触发点。
    """

    def __init__(
        self,
        trigger_type: str = "",
        timing_point: str = "",
        condition: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.trigger_type = trigger_type      # on_turn_start/on_turn_end/on_damage_taken/on_attack_hit
        self.timing_point = timing_point      # before/after
        self.condition = condition or {}


class SaveEndSpec:
    """回合末豁免规格 — 描述持续效果的结束时豁免。

    STATE-002: 效果生命周期模型。
    用于中毒、束缚等状态的回合末重复豁免。
    """

    def __init__(
        self,
        save_ability: str = "",
        save_dc: int = 10,
        save_frequency: str = "end_of_turn",  # end_of_turn/start_of_turn
        on_success: str = "remove",           # remove/reduce_duration
        on_failure: str = "persist",          # persist/reduce_duration
    ) -> None:
        self.save_ability = save_ability
        self.save_dc = save_dc
        self.save_frequency = save_frequency
        self.on_success = on_success
        self.on_failure = on_failure


@dataclass
class SourceRef:
    """效果来源引用。"""

    entity_id: str = ""
    spell_id: str = ""
    feature_id: str = ""
    item_id: str = ""
    rule_id: str = ""


@dataclass
class DurationSpec:
    """持续时间规格。"""

    duration_type: DurationType = DurationType.INSTANT
    value: int = 0                # 总持续时间（轮/分钟/小时）
    remaining: int = 0            # 剩余时间
    expire_on: Optional[int] = None   # 到期回合号
    start_round: Optional[int] = None
    start_turn: Optional[int] = None


@dataclass
class EffectInstance:
    """效果实例 — 一个活跃的效果。

    STATE-002: 效果生命周期模型。
    包含来源、持续时间、触发规格、堆叠策略、回合末豁免等完整元数据。
    """

    source: SourceRef = field(default_factory=SourceRef)
    target_id: str = ""
    name: str = ""
    condition_name: str = ""
    duration: DurationSpec = field(default_factory=DurationSpec)
    stack_policy: StackPolicyType = StackPolicyType.NO_STACK
    modifiers: List[Dict[str, Any]] = field(default_factory=list)
    concentration_link_id: str = ""
    active: bool = True
    effect_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    # ★ STATE-002: 触发规格与回合末豁免
    trigger_spec: Optional[TriggerSpec] = None
    save_end_spec: Optional[SaveEndSpec] = None

    # ── 方法 ──────────────────────────────────────────────────────────

    def is_expired(self) -> bool:
        """判断效果是否已过期。"""
        if not self.active:
            return True
        if self.duration.duration_type == DurationType.PERMANENT:
            return False
        if self.duration.duration_type == DurationType.INSTANT:
            return True  # 瞬间效果立即过期
        return self.duration.remaining <= 0

    def tick(self) -> bool:
        """推进一个时间单位，返回是否已过期。

        对于 ROUNDS 类型，remaining - 1；
        其他时间类型暂不在此 tick（由外部管理）。
        """
        if self.duration.duration_type == DurationType.ROUNDS:
            self.duration.remaining = max(0, self.duration.remaining - 1)
        if self.is_expired():
            self.active = False
            return True
        return False

    def end(self) -> None:
        """立即结束效果。"""
        self.active = False
        self.duration.remaining = 0


class EffectManager:
    """效果管理器 — 统一管理所有活跃效果。"""

    def __init__(self) -> None:
        self._effects: Dict[str, EffectInstance] = {}

    def add(self, effect: EffectInstance) -> str:
        """添加效果，返回 effect_id。

        根据 stack_policy 处理堆叠：
        - no_stack: 若同名效果已存在于目标，忽略
        - override: 若同名效果已存在，移除旧的
        - stack: 直接添加
        """
        target_effects = [
            e for e in self._effects.values()
            if e.target_id == effect.target_id and e.name == effect.name and e.active
        ]

        if effect.stack_policy == StackPolicyType.NO_STACK and target_effects:
            return target_effects[0].effect_id

        if effect.stack_policy == StackPolicyType.OVERRIDE:
            for old in target_effects:
                old.end()

        self._effects[effect.effect_id] = effect
        return effect.effect_id

    def remove(self, effect_id: str) -> None:
        """移除指定效果。"""
        if effect_id in self._effects:
            self._effects[effect_id].end()
            del self._effects[effect_id]

    def remove_by_source(self, entity_id: str, source_id: str) -> None:
        """按来源批量移除效果。

        Args:
            entity_id: 来源实体 ID
            source_id: 来源标识（spell_id/feature_id/item_id）
        """
        to_remove = []
        for eid, eff in self._effects.items():
            if eff.source.entity_id != entity_id:
                continue
            source_ids = [
                eff.source.spell_id,
                eff.source.feature_id,
                eff.source.item_id,
            ]
            if source_id in source_ids:
                to_remove.append(eid)
        for eid in to_remove:
            self.remove(eid)

    def get_active(self, target_id: str) -> List[EffectInstance]:
        """获取目标的所有活跃效果。"""
        return [
            e for e in self._effects.values()
            if e.target_id == target_id and e.active and not e.is_expired()
        ]

    def tick_all(self, current_round: int, current_turn: int) -> List[str]:
        """推进所有效果一个时间单位，返回过期效果 ID 列表。"""
        expired: List[str] = []
        for eid, eff in list(self._effects.items()):
            if eff.active and eff.duration.duration_type == DurationType.ROUNDS:
                if eff.tick():
                    expired.append(eid)
        return expired

    def get_modifiers(self, target_id: str, category: str = "") -> List[Dict[str, Any]]:
        """获取目标的所有活跃效果的修正值。

        Args:
            target_id: 目标实体 ID
            category: 可选，按修正类别过滤
        """
        mods: List[Dict[str, Any]] = []
        for eff in self.get_active(target_id):
            for mod in eff.modifiers:
                if category and mod.get("category") != category:
                    continue
                mods.append(mod)
        return mods
