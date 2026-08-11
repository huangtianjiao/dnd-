"""结算结果修正来源解释 — ResolutionTraceExt。

OBS-001: 结算结果缺少完整修正来源解释。
ResolutionTrace记录公式树、规则ID、来源实体和被抵消修正。

规则依据: topics/城主指南2024/2.运作游戏/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ModifierSource:
    """单个修正来源。

    OBS-001: 记录每个加值/惩罚的来源和数值。
    """

    source_type: str = ""           # ability/proficiency/condition/item/feat/spell/circumstance
    source_id: str = ""             # 来源实体 ID（属性名/状态名/物品ID等）
    source_name: str = ""           # 来源显示名
    value: int = 0                  # 修正值（正=加值，负=惩罚）
    active: bool = True             # 是否生效
    suppressed_by: str = ""         # 被哪个修正抵消


@dataclass
class FormulaNode:
    """公式树节点。

    OBS-001: UI可展开显示完整轨迹。
    """

    node_type: str = ""             # roll/base/modifier/total/result
    label: str = ""                 # 显示标签
    value: int = 0                  # 节点值
    children: List["FormulaNode"] = field(default_factory=list)
    rule_id: str = ""               # 关联规则 ID
    source_entity: str = ""         # 来源实体


@dataclass
class ResolutionTrace:
    """结算追踪 — 完整修正来源解释。

    OBS-001: 结算结果缺少完整修正来源解释。
    """

    action_type: str = ""           # attack/cast/check/save
    entity_id: str = ""             # 执行实体
    target_id: str = ""             # 目标实体

    # 基础值
    d20_roll: int = 0               # 天然骰
    base_modifier: int = 0          # 基础调整值（属性）

    # 所有修正来源
    modifiers: List[ModifierSource] = field(default_factory=list)

    # 最终结果
    total: int = 0                  # 总计
    success: bool = False           # 是否成功
    margin: int = 0                 # 差值

    # 规则溯源
    rule_ids: List[str] = field(default_factory=list)

    def add_modifier(self, source_type: str, source_id: str,
                     source_name: str, value: int) -> None:
        """添加一个修正来源。"""
        self.modifiers.append(ModifierSource(
            source_type=source_type,
            source_id=source_id,
            source_name=source_name,
            value=value,
        ))

    def get_active_modifiers(self) -> List[ModifierSource]:
        """获取所有生效的修正。"""
        return [m for m in self.modifiers if m.active]

    def get_suppressed_modifiers(self) -> List[ModifierSource]:
        """获取所有被抵消的修正。"""
        return [m for m in self.modifiers if not m.active]

    def build_formula_tree(self) -> FormulaNode:
        """构建公式树。"""
        root = FormulaNode(
            node_type="result",
            label=f"总计: {self.total}",
            value=self.total,
        )

        # d20
        root.children.append(FormulaNode(
            node_type="roll",
            label=f"d20: {self.d20_roll}",
            value=self.d20_roll,
        ))

        # 基础调整值
        if self.base_modifier != 0:
            root.children.append(FormulaNode(
                node_type="base",
                label=f"属性: {self.base_modifier:+d}",
                value=self.base_modifier,
            ))

        # 所有修正
        for mod in self.get_active_modifiers():
            root.children.append(FormulaNode(
                node_type="modifier",
                label=f"{mod.source_name}: {mod.value:+d}",
                value=mod.value,
                source_entity=mod.source_id,
            ))

        return root

    def to_dict(self) -> dict:
        """序列化为字典。"""
        return {
            "action_type": self.action_type,
            "entity_id": self.entity_id,
            "target_id": self.target_id,
            "d20_roll": self.d20_roll,
            "base_modifier": self.base_modifier,
            "modifiers": [
                {
                    "type": m.source_type,
                    "id": m.source_id,
                    "name": m.source_name,
                    "value": m.value,
                    "active": m.active,
                }
                for m in self.modifiers
            ],
            "total": self.total,
            "success": self.success,
            "margin": self.margin,
            "rule_ids": list(self.rule_ids),
        }
