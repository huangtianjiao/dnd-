"""效果 DSL — 可组合效果原语与执行器。

设计原则：
  - 每种游戏效果分解为一组 EffectOperation 操作。
  - EffectDefinition 描述一个完整效果（含操作序列、目标、区域、持续时间）。
  - EffectExecutor 按序执行操作，产出事件列表。

规则依据: SPL-008 Effect DSL 可组合效果原语
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .rng import RngContext


class EffectOpType(str, Enum):
    """效果操作类型枚举。"""

    # 伤害/治疗
    DEAL_DAMAGE = "deal_damage"
    HEAL = "heal"
    TEMP_HP = "temp_hp"

    # 条件
    APPLY_CONDITION = "apply_condition"
    REMOVE_CONDITION = "remove_condition"

    # 修正
    ADD_MODIFIER = "add_modifier"
    OVERRIDE_VALUE = "override_value"
    GRANT_ADVANTAGE = "grant_advantage"
    GRANT_DISADVANTAGE = "grant_disadvantage"

    # 资源
    SPEND_RESOURCE = "spend_resource"
    RESTORE_RESOURCE = "restore_resource"

    # 移动
    MOVE = "move"
    PUSH = "push"
    PULL = "pull"
    TELEPORT = "teleport"

    # 区域
    CREATE_ZONE = "create_zone"
    DESTROY_ZONE = "destroy_zone"

    # 实体
    SUMMON = "summon"
    DESPAWN = "despawn"
    TRANSFORM = "transform"

    # 动作
    GRANT_ACTION = "grant_action"

    # 信息
    REVEAL = "reveal"
    CONCEAL = "conceal"

    # 调度
    SCHEDULE_TICK = "schedule_tick"
    REPEAT_SAVE = "repeat_save"

    # 控制流
    CHOICE = "choice"
    BRANCH = "branch"
    CONDITIONAL = "conditional"


@dataclass
class EffectOperation:
    """单个效果操作。"""

    op: EffectOpType
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EffectDefinition:
    """效果定义 — 描述一个完整效果。"""

    definition_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    operations: List[EffectOperation] = field(default_factory=list)
    target_spec: Dict[str, Any] = field(default_factory=dict)
    area_spec: Dict[str, Any] = field(default_factory=dict)
    duration_spec: Dict[str, Any] = field(default_factory=dict)
    save_spec: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        """校验效果定义，返回错误列表（空列表=合法）。"""
        errors: List[str] = []
        if not self.name:
            errors.append("效果名称不能为空")
        if not self.operations:
            errors.append("操作列表不能为空")
        for i, op in enumerate(self.operations):
            if not isinstance(op.op, EffectOpType):
                errors.append(f"操作[{i}]的类型无效: {op.op}")
        return errors


class EffectExecutor:
    """效果执行器 — 按序执行效果定义中的操作，产出事件列表。"""

    def __init__(self, rng: Optional[RngContext] = None) -> None:
        self._rng = rng or RngContext()

    def execute(self, definition: EffectDefinition, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行效果定义，返回事件列表。

        Args:
            definition: 效果定义
            context: 执行上下文（含 caster, targets, round 等信息）

        Returns:
            事件列表，每个事件是 dict，含 event_type 和相关数据
        """
        events: List[Dict[str, Any]] = []
        for op in definition.operations:
            handler = getattr(self, f"_op_{op.op.value}", None)
            if handler is None:
                events.append({
                    "event_type": "error",
                    "message": f"未实现的操作类型: {op.op.value}",
                })
                continue
            result = handler(op.params, context)
            if isinstance(result, list):
                events.extend(result)
            elif result:
                events.append(result)
        return events

    # ── 伤害/治疗 ─────────────────────────────────────────────────────

    def _op_deal_damage(self, params: Dict, ctx: Dict) -> Dict:
        amount = params.get("amount", 0)
        damage_type = params.get("damage_type", "unspecified")
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "damage_dealt",
            "target_id": target,
            "amount": amount,
            "damage_type": damage_type,
        }

    def _op_heal(self, params: Dict, ctx: Dict) -> Dict:
        amount = params.get("amount", 0)
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "healing_applied",
            "target_id": target,
            "amount": amount,
        }

    def _op_temp_hp(self, params: Dict, ctx: Dict) -> Dict:
        amount = params.get("amount", 0)
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "temp_hp_granted",
            "target_id": target,
            "amount": amount,
        }

    # ── 条件 ──────────────────────────────────────────────────────────

    def _op_apply_condition(self, params: Dict, ctx: Dict) -> Dict:
        condition = params.get("condition", "")
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "condition_applied",
            "target_id": target,
            "condition": condition,
        }

    def _op_remove_condition(self, params: Dict, ctx: Dict) -> Dict:
        condition = params.get("condition", "")
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "condition_removed",
            "target_id": target,
            "condition": condition,
        }

    # ── 修正 ──────────────────────────────────────────────────────────

    def _op_add_modifier(self, params: Dict, ctx: Dict) -> Dict:
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "modifier_added",
            "target_id": target,
            "modifier": params,
        }

    def _op_override_value(self, params: Dict, ctx: Dict) -> Dict:
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "value_overridden",
            "target_id": target,
            "field": params.get("field", ""),
            "value": params.get("value"),
        }

    def _op_grant_advantage(self, params: Dict, ctx: Dict) -> Dict:
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "advantage_granted",
            "target_id": target,
            "on": params.get("on", ""),
        }

    def _op_grant_disadvantage(self, params: Dict, ctx: Dict) -> Dict:
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "disadvantage_granted",
            "target_id": target,
            "on": params.get("on", ""),
        }

    # ── 资源 ──────────────────────────────────────────────────────────

    def _op_spend_resource(self, params: Dict, ctx: Dict) -> Dict:
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "resource_spent",
            "target_id": target,
            "resource": params.get("resource", ""),
            "amount": params.get("amount", 1),
        }

    def _op_restore_resource(self, params: Dict, ctx: Dict) -> Dict:
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "resource_restored",
            "target_id": target,
            "resource": params.get("resource", ""),
            "amount": params.get("amount", 1),
        }

    # ── 移动 ──────────────────────────────────────────────────────────

    def _op_move(self, params: Dict, ctx: Dict) -> Dict:
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "entity_moved",
            "target_id": target,
            "destination": params.get("destination", {}),
        }

    def _op_push(self, params: Dict, ctx: Dict) -> Dict:
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "entity_pushed",
            "target_id": target,
            "distance": params.get("distance", 0),
            "direction": params.get("direction", ""),
        }

    def _op_pull(self, params: Dict, ctx: Dict) -> Dict:
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "entity_pulled",
            "target_id": target,
            "distance": params.get("distance", 0),
            "direction": params.get("direction", ""),
        }

    def _op_teleport(self, params: Dict, ctx: Dict) -> Dict:
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "entity_teleported",
            "target_id": target,
            "destination": params.get("destination", {}),
        }

    # ── 区域 ──────────────────────────────────────────────────────────

    def _op_create_zone(self, params: Dict, ctx: Dict) -> Dict:
        return {
            "event_type": "zone_created",
            "zone_id": str(uuid.uuid4()),
            "zone_type": params.get("zone_type", ""),
            "center": params.get("center", {}),
            "radius": params.get("radius", 0),
        }

    def _op_destroy_zone(self, params: Dict, ctx: Dict) -> Dict:
        return {
            "event_type": "zone_destroyed",
            "zone_id": params.get("zone_id", ""),
        }

    # ── 实体 ──────────────────────────────────────────────────────────

    def _op_summon(self, params: Dict, ctx: Dict) -> Dict:
        return {
            "event_type": "entity_summoned",
            "entity_id": str(uuid.uuid4()),
            "entity_type": params.get("entity_type", ""),
            "position": params.get("position", {}),
        }

    def _op_despawn(self, params: Dict, ctx: Dict) -> Dict:
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "entity_despawned",
            "target_id": target,
        }

    def _op_transform(self, params: Dict, ctx: Dict) -> Dict:
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "entity_transformed",
            "target_id": target,
            "into": params.get("into", ""),
        }

    # ── 动作 ──────────────────────────────────────────────────────────

    def _op_grant_action(self, params: Dict, ctx: Dict) -> Dict:
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "action_granted",
            "target_id": target,
            "action": params.get("action", ""),
        }

    # ── 信息 ──────────────────────────────────────────────────────────

    def _op_reveal(self, params: Dict, ctx: Dict) -> Dict:
        return {
            "event_type": "info_revealed",
            "info_type": params.get("info_type", ""),
            "to": params.get("to", ctx.get("target_id", "")),
        }

    def _op_conceal(self, params: Dict, ctx: Dict) -> Dict:
        return {
            "event_type": "info_concealed",
            "info_type": params.get("info_type", ""),
            "from": params.get("from", ctx.get("target_id", "")),
        }

    # ── 调度 ──────────────────────────────────────────────────────────

    def _op_schedule_tick(self, params: Dict, ctx: Dict) -> Dict:
        return {
            "event_type": "tick_scheduled",
            "effect_id": params.get("effect_id", ""),
            "at_round": params.get("at_round", 0),
        }

    def _op_repeat_save(self, params: Dict, ctx: Dict) -> Dict:
        target = params.get("target", ctx.get("target_id", ""))
        return {
            "event_type": "repeat_save_scheduled",
            "target_id": target,
            "dc": params.get("dc", 10),
            "ability": params.get("ability", ""),
            "on_success": params.get("on_success", "end"),
        }

    # ── 控制流 ────────────────────────────────────────────────────────

    def _op_choice(self, params: Dict, ctx: Dict) -> Dict:
        return {
            "event_type": "choice_presented",
            "options": params.get("options", []),
            "prompt": params.get("prompt", ""),
        }

    def _op_branch(self, params: Dict, ctx: Dict) -> Dict:
        return {
            "event_type": "branch_evaluated",
            "condition": params.get("condition", ""),
            "true_branch": params.get("true_branch", []),
            "false_branch": params.get("false_branch", []),
        }

    def _op_conditional(self, params: Dict, ctx: Dict) -> Dict:
        return {
            "event_type": "conditional_evaluated",
            "condition": params.get("condition", ""),
            "result": params.get("result", None),
        }
