"""反应窗口系统 — ReactionWindow / ReactionController / ReadyEffect。

设计原则：
  - ReactionWindow 封装一次反应窗口的完整生命周期（开启/选择/关闭）。
  - ReactionController 管理反应窗口的创建和调度。
  - ReadyEffect 实现准备动作的触发条件匹配与执行。

规则依据:
  COM-009 ReactionWindow 统一反应系统
  COM-010 准备动作完整触发规则
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ──────────────────────────────────────────────────────────────────────────
# 反应类型枚举
# ──────────────────────────────────────────────────────────────────────────

class ReactionType(str, Enum):
    """反应类型枚举。"""

    OPPORTUNITY_ATTACK = "opportunity_attack"      # 借机攻击
    SHIELD_SPELL = "shield_spell"                  # 护盾术
    COUNTERSPELL = "counterspell"                  # 反制法术
    LEGENDARY_RESISTANCE = "legendary_resistance"  # 传奇抗性
    PROTECTIVE_SPIRIT = "protective_spirit"        # 保护之灵（如 Cutting Words）
    CUSTOM = "custom"                              # 自定义


# ──────────────────────────────────────────────────────────────────────────
# 反应选项
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class ReactionOption:
    """一个可用的反应选项。"""

    reaction_type: ReactionType
    entity_id: str          # 可反应者 ID
    ability_name: str = ""  # 如 "Shield", "Counterspell"
    cost: str = "reaction"  # reaction / legendary_action
    callback: Optional[Callable] = None
    metadata: dict = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────────
# 反应窗口（COM-009）
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class ReactionWindow:
    """通用反应窗口 — 管理一次反应机会的完整生命周期。

    规则: R-CMB-013 每回合1反应
          R-CMB-007 撤离不触发借机攻击
    出处: topics/玩家手册2024/进行游戏/战斗流程.htm
    """

    window_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger_event: str = ""            # 触发事件类型
    trigger_context: dict = field(default_factory=dict)
    eligible_reactors: List[str] = field(default_factory=list)
    available_reactions: List[ReactionOption] = field(default_factory=list)
    is_open: bool = False
    controller_id: str = ""            # 谁做选择（DM/玩家）
    deadline: str = ""                 # 截止时间点描述
    _selected: Optional[ReactionOption] = field(default=None, repr=False)
    _events: List[dict] = field(default_factory=list)

    def open_window(
        self,
        trigger_event: str,
        context: dict,
        eligible: List[str],
        reactions: List[ReactionOption],
    ) -> None:
        """打开反应窗口。"""
        self.trigger_event = trigger_event
        self.trigger_context = context
        self.eligible_reactors = list(eligible)
        self.available_reactions = list(reactions)
        self.is_open = True
        self._selected = None
        self._events = []

    def select_reaction(
        self,
        entity_id: str,
        reaction_type: ReactionType,
    ) -> Optional[ReactionOption]:
        """选择一个反应。返回选中的 ReactionOption 或 None。"""
        if not self.is_open:
            return None
        if entity_id not in self.eligible_reactors:
            return None
        for opt in self.available_reactions:
            if opt.entity_id == entity_id and opt.reaction_type == reaction_type:
                self._selected = opt
                return opt
        return None

    def add_available_reaction(self, option: ReactionOption) -> None:
        """向窗口添加一个可用反应选项。"""
        self.available_reactions.append(option)

    def close_window(self) -> List[dict]:
        """关闭反应窗口，返回结算事件列表。"""
        events: List[dict] = []
        if self._selected is not None and self._selected.callback is not None:
            result = self._selected.callback(self.trigger_context)
            if isinstance(result, dict):
                events.append(result)
            elif isinstance(result, list):
                events.extend(r for r in result if isinstance(r, dict))
        events.append({
            "type": "reaction_window_closed",
            "window_id": self.window_id,
            "trigger_event": self.trigger_event,
            "selected": (self._selected.reaction_type.value
                         if self._selected else None),
        })
        self.is_open = False
        self._events = events
        return events


# ──────────────────────────────────────────────────────────────────────────
# 反应控制器（COM-009）
# ──────────────────────────────────────────────────────────────────────────

class ReactionController:
    """管理反应窗口的创建和调度。"""

    def __init__(self) -> None:
        self._current_window: Optional[ReactionWindow] = None
        self._history: List[ReactionWindow] = []

    @property
    def current_window(self) -> Optional[ReactionWindow]:
        """当前打开的反应窗口。"""
        return self._current_window

    @property
    def history(self) -> List[ReactionWindow]:
        """历史反应窗口列表。"""
        return list(self._history)

    def open(
        self,
        trigger_event: str,
        context: dict,
        eligible_reactors: List[str],
        reactions: Optional[List[ReactionOption]] = None,
        controller_id: str = "",
    ) -> ReactionWindow:
        """创建并打开一个新的反应窗口。

        若已有窗口打开，先关闭旧窗口（跳过选择）。
        """
        if self._current_window is not None and self._current_window.is_open:
            self._current_window.close_window()
            self._history.append(self._current_window)

        window = ReactionWindow(controller_id=controller_id)
        window.open_window(
            trigger_event=trigger_event,
            context=context,
            eligible=eligible_reactors,
            reactions=reactions or [],
        )
        self._current_window = window
        return window

    def resolve(
        self,
        entity_id: str,
        reaction_type: ReactionType,
    ) -> List[dict]:
        """在当前窗口中选择一个反应并结算关闭。"""
        if self._current_window is None or not self._current_window.is_open:
            return []
        self._current_window.select_reaction(entity_id, reaction_type)
        events = self._current_window.close_window()
        self._history.append(self._current_window)
        self._current_window = None
        return events

    def skip(self) -> List[dict]:
        """跳过当前反应窗口（无人反应）。"""
        if self._current_window is None or not self._current_window.is_open:
            return []
        events = self._current_window.close_window()
        self._history.append(self._current_window)
        self._current_window = None
        return events


# ──────────────────────────────────────────────────────────────────────────
# 准备动作（COM-010）
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class ReadyEffect:
    """准备动作 — 设定触发条件，条件满足时用反应执行。

    规则: 术语汇编/动作.txt「预备」
          - 消耗动作设定触发条件
          - 触发时用反应执行一个动作或移动等于速度的距离
          - 预备法术需维持专注
          - 下回合开始时未触发则失效
    出处: topics/玩家手册2024/术语汇编/动作.htm
    """

    entity_id: str
    prepared_action: str              # 准备的动作类型（attack/move/spell/...）
    prepared_payload: dict = field(default_factory=dict)
    trigger_predicate: str = ""       # 触发条件描述
    trigger_callback: Optional[Callable] = None
    requires_concentration: bool = True
    expires_round: int = 0            # 下回合开始过期（由上层设置）
    is_active: bool = False

    def activate(self, current_round: int) -> None:
        """激活准备动作，设定过期轮次。"""
        self.is_active = True
        self.expires_round = current_round + 1

    def matches_trigger(self, event: str, context: dict) -> bool:
        """判断当前事件是否匹配准备动作的触发条件。

        若有 trigger_callback 则使用回调判定；否则按事件名简单匹配。
        """
        if not self.is_active:
            return False
        if self.trigger_callback is not None:
            return bool(self.trigger_callback(event, context))
        # 简单字符串匹配
        return self.trigger_predicate.lower() in event.lower()

    def execute(self, context: dict) -> List[dict]:
        """执行准备动作，返回事件列表。

        执行后自动失效（一次性）。
        """
        events: List[dict] = []
        if not self.is_active:
            return events

        events.append({
            "type": "ready_triggered",
            "entity_id": self.entity_id,
            "prepared_action": self.prepared_action,
            "trigger_predicate": self.trigger_predicate,
            "payload": self.prepared_payload,
        })

        # 标记失效（一次性触发）
        self.is_active = False
        return events

    def expire(self) -> dict:
        """使准备动作过期。"""
        self.is_active = False
        return {
            "type": "ready_expired",
            "entity_id": self.entity_id,
            "prepared_action": self.prepared_action,
        }


# ──────────────────────────────────────────────────────────────────────────
# SPL-015: 时机型法术专用窗口
# ──────────────────────────────────────────────────────────────────────────

# 护盾术 Shield — 命中后伤害前
SHIELD_REACTION = {
    "trigger": "on_hit_before_damage",
    "spell_id": "shield",
    "effect": "+5 AC until start of next turn",
    "cost": "reaction",
}

# 法术反制 Counterspell — 看见施法开始
COUNTERSPELL_REACTION = {
    "trigger": "spell_cast_started",
    "spell_id": "counterspell",
    "effect": "negate target spell",
    "cost": "reaction",
}

# 解除魔法 Dispel Magic — 对活动效果
DISPEL_MAGIC = {
    "trigger": "any_time",  # 不需要反应窗口
    "spell_id": "dispel_magic",
    "effect": "end one spell effect on target",
    "cost": "action",
}

# 传奇抗性 Legendary Resistance — 豁免失败时
LEGENDARY_RESISTANCE_WINDOW = {
    "trigger": "saving_throw_failed",
    "ability_id": "legendary_resistance",
    "effect": "turn failed save into success",
    "cost": "legendary_action",
}

# 时机型法术注册表
TIMING_SPELL_REGISTRY: Dict[str, dict] = {
    "on_hit_before_damage": SHIELD_REACTION,
    "spell_cast_started": COUNTERSPELL_REACTION,
    "saving_throw_failed": LEGENDARY_RESISTANCE_WINDOW,
    "any_time": DISPEL_MAGIC,
}


def get_timing_spell_window(trigger_event: str) -> Optional[dict]:
    """获取指定触发事件对应的时机型法术窗口定义 (SPL-015)。

    Args:
        trigger_event: 触发事件类型
            - "on_hit_before_damage": 护盾术窗口
            - "spell_cast_started": 法术反制窗口
            - "saving_throw_failed": 传奇抗性窗口

    Returns:
        时机型法术窗口定义字典，若无匹配则返回 None
    """
    return TIMING_SPELL_REGISTRY.get(trigger_event)


def open_timing_window(
    controller: ReactionController,
    trigger_event: str,
    context: dict,
    eligible_reactors: List[str],
    controller_id: str = "",
) -> Optional[ReactionWindow]:
    """为时机型法术开启专用反应窗口 (SPL-015)。

    根据触发事件自动创建对应的反应窗口，并添加相应的反应选项。

    Args:
        controller: ReactionController 实例
        trigger_event: 触发事件类型
        context: 触发上下文（如攻击者、目标等信息）
        eligible_reactors: 可反应的实体 ID 列表
        controller_id: 做选择的实体 ID

    Returns:
        创建的 ReactionWindow，若该触发事件无对应窗口则返回 None
    """
    timing_def = get_timing_spell_window(trigger_event)
    if timing_def is None:
        return None

    # 构建反应选项
    reactions: List[ReactionOption] = []
    spell_id = timing_def.get("spell_id", "")
    ability_id = timing_def.get("ability_id", "")

    for reactor_id in eligible_reactors:
        if spell_id:
            reactions.append(ReactionOption(
                reaction_type=ReactionType.SHIELD_SPELL if spell_id == "shield"
                    else ReactionType.COUNTERSPELL,
                entity_id=reactor_id,
                ability_name=spell_id,
                cost=timing_def["cost"],
                metadata={"spell_id": spell_id, "trigger": trigger_event},
            ))
        elif ability_id:
            reactions.append(ReactionOption(
                reaction_type=ReactionType.LEGENDARY_RESISTANCE,
                entity_id=reactor_id,
                ability_name=ability_id,
                cost=timing_def["cost"],
                metadata={"ability_id": ability_id, "trigger": trigger_event},
            ))

    window = controller.open(
        trigger_event=trigger_event,
        context=context,
        eligible_reactors=eligible_reactors,
        reactions=reactions,
        controller_id=controller_id,
    )
    return window
