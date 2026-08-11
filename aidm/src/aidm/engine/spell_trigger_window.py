"""法术触发窗口 — TriggerWindow。

SPL-015: 法术反制、解除魔法、护盾等时机型法术缺少专用窗口。
TriggerWindow支持spell_cast_started、attack_hit_before_damage等；
法术定义声明响应窗口。

规则依据: topics/玩家手册2024/法术/反应.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class TriggerPoint(str, Enum):
    """触发时序点。"""

    SPELL_CAST_STARTED = "spell_cast_started"       # 法术开始施放
    SPELL_CAST_COMPLETED = "spell_cast_completed"   # 法术完成施放
    ATTACK_HIT_BEFORE_DAMAGE = "attack_hit_before_damage"  # 命中后伤害前
    ATTACK_MISSED = "attack_missed"                 # 攻击未命中
    DAMAGE_DEALT = "damage_dealt"                   # 伤害造成后
    TURN_STARTED = "turn_started"                   # 回合开始
    TURN_ENDED = "turn_ended"                       # 回合结束
    MOVEMENT_LEAVES_REACH = "movement_leaves_reach" # 离开触及范围
    CONDITION_APPLIED = "condition_applied"         # 状态被施加
    HP_REACHED_ZERO = "hp_reached_zero"             # HP 归零


@dataclass
class TriggerWindow:
    """触发窗口 — 描述一个反应法术的触发条件。

    SPL-015: 法术定义声明响应窗口。
    """

    spell_id: str                          # 法术 canonical ID
    trigger_point: TriggerPoint            # 触发时序点
    range_ft: float = float("inf")         # 有效范围
    requires_visibility: bool = True       # 是否需要看见触发源
    condition: str = ""                    # 额外条件描述


@dataclass
class PendingTrigger:
    """待处理的触发事件。"""

    trigger_point: TriggerPoint
    source_entity_id: str                  # 触发源实体 ID
    target_entity_id: str = ""             # 触发目标实体 ID
    context: dict = field(default_factory=dict)


@dataclass
class TriggerWindowRegistry:
    """触发窗口注册表 — 管理所有反应法术的触发窗口。

    SPL-015: 关键反应法术无法合法使用。
    """

    _windows: Dict[str, List[TriggerWindow]] = field(default_factory=dict)

    def register(self, window: TriggerWindow) -> None:
        """注册一个触发窗口。"""
        if window.spell_id not in self._windows:
            self._windows[window.spell_id] = []
        self._windows[window.spell_id].append(window)

    def get_windows_for_spell(self, spell_id: str) -> List[TriggerWindow]:
        """获取指定法术的所有触发窗口。"""
        return self._windows.get(spell_id, [])

    def find_reactions(self, trigger: PendingTrigger) -> List[TriggerWindow]:
        """查找匹配触发条件的反应法术窗口。"""
        matches: List[TriggerWindow] = []
        for spell_id, windows in self._windows.items():
            for w in windows:
                if w.trigger_point != trigger.trigger_point:
                    continue
                matches.append(w)
        return matches
