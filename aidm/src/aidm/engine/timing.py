"""时序系统 — TimingPoint 枚举 + 同时效应排序。

设计原则：
  - TimingPoint 定义战斗中所有可能的时序点（数值越小越先执行）。
  - TimingHandler 绑定到某个时序点的回调。
  - TimingQueue 管理同一时点的多个 handler 并按优先级排序执行。
  - TimingController 统一管理所有时序点的注册、触发和清除。

规则依据: COM-013 TimingPoint 同时效应排序
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Callable, Dict, List, Optional


class TimingPoint(IntEnum):
    """时序点枚举 — 数值越小越先执行。"""

    COMBAT_START = 0
    INITIATIVE_BEFORE_ROLL = 10
    INITIATIVE_AFTER_ROLL = 20
    TURN_START_BEFORE_EFFECTS = 100
    TURN_START = 110
    BEFORE_ACTION = 200
    BEFORE_ATTACK_ROLL = 210
    AFTER_ATTACK_ROLL = 220
    ON_HIT_BEFORE_DAMAGE = 230
    AFTER_DAMAGE = 240
    BEFORE_SAVE = 250
    AFTER_SAVE = 260
    BEFORE_MOVEMENT_STEP = 300
    LEAVE_REACH = 310
    ENTER_AREA = 320
    AFTER_MOVEMENT = 330
    SPELL_CAST_STARTED = 400
    SPELL_CAST_RESOLVED = 410
    TURN_END = 500
    ROUND_END = 600
    COMBAT_END = 700
    REST_STARTED = 800
    REST_INTERRUPTED = 810
    REST_COMPLETED = 820


@dataclass
class TimingHandler:
    """绑定到某一时序点的回调处理器。"""

    timing: TimingPoint
    handler_id: str
    callback: Optional[Callable] = None
    priority: int = 0  # 同一点内的优先级（越大越先执行）

    def __lt__(self, other: "TimingHandler") -> bool:
        """排序用：优先级大的排前面。"""
        return self.priority > other.priority


@dataclass
class TimingQueue:
    """同一时点的多个效果排序队列。"""

    timing: TimingPoint
    handlers: List[TimingHandler] = field(default_factory=list)

    def add(self, handler: TimingHandler) -> None:
        """添加一个 handler 到队列。"""
        self.handlers.append(handler)
        self.handlers.sort()  # 按 priority 降序

    def remove(self, handler_id: str) -> bool:
        """移除指定 handler。"""
        before = len(self.handlers)
        self.handlers = [h for h in self.handlers if h.handler_id != handler_id]
        return len(self.handlers) < before

    def execute_all(self, context: dict) -> List[dict]:
        """按优先级执行所有 handler，返回事件列表。"""
        events: List[dict] = []
        for handler in list(self.handlers):
            if handler.callback is not None:
                result = handler.callback(context)
                if isinstance(result, dict):
                    result.setdefault("handler_id", handler.handler_id)
                    result.setdefault("timing", self.timing.name)
                    events.append(result)
                elif isinstance(result, list):
                    for r in result:
                        if isinstance(r, dict):
                            r.setdefault("handler_id", handler.handler_id)
                            r.setdefault("timing", self.timing.name)
                            events.append(r)
        return events


class TimingController:
    """管理所有时序点的 handler 注册和触发。"""

    def __init__(self) -> None:
        self._queues: Dict[TimingPoint, TimingQueue] = {}

    def register(self, handler: TimingHandler) -> None:
        """注册一个 handler 到对应的时序点。"""
        timing = handler.timing
        if timing not in self._queues:
            self._queues[timing] = TimingQueue(timing=timing)
        self._queues[timing].add(handler)

    def unregister(self, handler_id: str) -> bool:
        """按 handler_id 移除 handler，返回是否找到并移除。"""
        for queue in self._queues.values():
            if queue.remove(handler_id):
                return True
        return False

    def trigger(self, timing: TimingPoint, context: dict) -> List[dict]:
        """触发某个时序点的所有 handler，返回事件列表。"""
        queue = self._queues.get(timing)
        if queue is None:
            return []
        return queue.execute_all(context)

    def clear(self) -> None:
        """清除所有注册的 handler。"""
        self._queues.clear()

    def get_handlers(self, timing: TimingPoint) -> List[TimingHandler]:
        """查询某时点的所有 handler（只读）。"""
        queue = self._queues.get(timing)
        if queue is None:
            return []
        return list(queue.handlers)
