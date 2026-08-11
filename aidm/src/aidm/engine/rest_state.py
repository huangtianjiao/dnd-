"""休息状态机 — RestState 持久化。

REST-002: RestState成为正常游戏流程的持久状态机。
规则依据: topics/玩家手册2024/进行游戏/休息.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RestPhase(str, Enum):
    """休息阶段。"""

    IDLE = "idle"               # 未在休息
    RESTING = "resting"         # 正在休息
    INTERRUPTED = "interrupted"  # 被打断
    COMPLETED = "completed"     # 已完成


@dataclass
class RestSession:
    """一次休息会话。

    REST-002: StartRest创建RestSession，
    时间推进和活动发布RestInterrupted/RestCompleted事件。
    """

    character_id: str
    rest_type: str = "short"        # "short" / "long"
    phase: RestPhase = RestPhase.IDLE
    started_at_minutes: int = 0     # 游戏内分钟
    duration_minutes: int = 0       # 已休息时长
    target_duration: int = 60       # 目标时长（短休60分钟，长休480分钟）
    interrupted_by: str = ""        # 打断原因

    def start(self, game_minutes: int) -> None:
        """开始休息。"""
        self.phase = RestPhase.RESTING
        self.started_at_minutes = game_minutes
        self.duration_minutes = 0

    def advance(self, minutes: int) -> None:
        """推进休息时间。"""
        if self.phase != RestPhase.RESTING:
            return
        self.duration_minutes += minutes
        if self.duration_minutes >= self.target_duration:
            self.phase = RestPhase.COMPLETED

    def interrupt(self, reason: str = "") -> None:
        """打断休息。"""
        if self.phase == RestPhase.RESTING:
            self.phase = RestPhase.INTERRUPTED
            self.interrupted_by = reason

    def is_beneficial(self) -> bool:
        """判断本次休息是否产生收益（已完成且未被有效打断）。"""
        return self.phase in (RestPhase.COMPLETED, RestPhase.INTERRUPTED)

    def get_benefit_multiplier(self) -> float:
        """获取收益比例（基于已完成的休息时长）。"""
        if self.phase == RestPhase.COMPLETED:
            return 1.0
        if self.phase == RestPhase.INTERRUPTED:
            ratio = self.duration_minutes / max(1, self.target_duration)
            return min(1.0, ratio)
        return 0.0


@dataclass
class RestStateRegistry:
    """休息状态注册表 — 管理所有角色的休息状态。"""

    _sessions: dict[str, RestSession] = field(default_factory=dict)

    def start_rest(self, character_id: str, rest_type: str,
                   game_minutes: int) -> RestSession:
        """开始一次休息。"""
        session = RestSession(
            character_id=character_id,
            rest_type=rest_type,
            target_duration=60 if rest_type == "short" else 480,
        )
        session.start(game_minutes)
        self._sessions[character_id] = session
        return session

    def get(self, character_id: str) -> Optional[RestSession]:
        """获取角色当前的休息状态。"""
        return self._sessions.get(character_id)

    def clear(self, character_id: str) -> None:
        """清除角色的休息状态。"""
        self._sessions.pop(character_id, None)
