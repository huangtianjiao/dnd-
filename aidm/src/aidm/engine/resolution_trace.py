"""结算结果追踪 — ResolutionTrace 记录公式树、规则ID、来源实体和被抵消修正。

设计原则：
  - 每次结算产生完整的 ResolutionTrace，UI 可展开显示。
  - 所有加值/惩罚都有来源规则ID和来源实体。
  - 被抵消的修正也保留记录（用于审计）。

规则依据: OBS-001 结算结果缺少完整修正来源解释
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ModifierSource:
    """单个修正来源。

    属性:
        source_type: 来源类型 (ABILITY/PROFICIENCY/CIRCUMSTANCE/EFFECT/CONDITION/ITEM)
        source_name: 来源名称 (如 "STR", "Bless", "力竭")
        value: 修正值 (正=加值, 负=惩罚)
        rule_id: 关联的规则ID (如 "PHB24.SPELL.BLESS")
        source_entity_id: 产生该修正的实体ID
        active: 是否生效 (False=被抵消或条件不满足)
    """
    source_type: str = ""
    source_name: str = ""
    value: int = 0
    rule_id: str = ""
    source_entity_id: str = ""
    active: bool = True


@dataclass
class RollTrace:
    """单次掷骰的追踪记录。

    属性:
        roll_id: 唯一标识
        dice_expr: 骰式 (如 "1d20+5")
        dice_rolls: 各骰结果
        modifiers: 修正来源列表
        total: 最终总计
        seed: RNG种子 (用于回放)
    """
    roll_id: str = ""
    dice_expr: str = ""
    dice_rolls: List[int] = field(default_factory=list)
    modifiers: List[ModifierSource] = field(default_factory=list)
    total: int = 0
    seed: Optional[int] = None


@dataclass
class ResolutionTrace:
    """一次完整结算的追踪记录。

    ★ OBS-001: UI可展开显示完整轨迹。
      格式示例: "d20(15) + STR(3) + PROF(2) - exhaustion(2) = 18 vs DC 15 → 成功"

    属性:
        trace_id: 唯一标识
        action_type: 动作类型 (attack/cast/check/save)
        actor_id: 执行者ID
        target_ids: 目标ID列表
        rolls: 掷骰追踪列表
        rule_ids: 涉及的规则ID列表
        cancelled_modifiers: 被抵消的修正列表 (用于审计)
        final_result: 最终结果摘要
    """
    trace_id: str = ""
    action_type: str = ""
    actor_id: str = ""
    target_ids: List[str] = field(default_factory=list)
    rolls: List[RollTrace] = field(default_factory=list)
    rule_ids: List[str] = field(default_factory=list)
    cancelled_modifiers: List[ModifierSource] = field(default_factory=list)
    final_result: Dict[str, Any] = field(default_factory=dict)

    def add_roll(self, roll: RollTrace) -> None:
        """添加一次掷骰记录。"""
        self.rolls.append(roll)

    def add_rule(self, rule_id: str) -> None:
        """添加涉及的规则ID。"""
        if rule_id and rule_id not in self.rule_ids:
            self.rule_ids.append(rule_id)

    def cancel_modifier(self, mod: ModifierSource) -> None:
        """记录被抵消的修正。"""
        mod.active = False
        self.cancelled_modifiers.append(mod)

    def to_display_string(self) -> str:
        """生成可展示的完整轨迹字符串。"""
        parts: List[str] = []
        for roll in self.rolls:
            dice_str = "+".join(str(d) for d in roll.dice_rolls)
            mod_strs = []
            for m in roll.modifiers:
                if m.active:
                    sign = "+" if m.value >= 0 else ""
                    mod_strs.append(f"{sign}{m.value}({m.source_name})")
            parts.append(f"d20({dice_str}) {' '.join(mod_strs)} = {roll.total}")
        return " | ".join(parts)
