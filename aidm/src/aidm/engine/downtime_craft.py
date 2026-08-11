"""停工期制作系统 — DowntimeCrafting。

EXP-003: 制作和停工期只覆盖少量简化公式。
将DMG模块定义为独立里程碑；使用ProjectDefinition与ProgressEvent实现。

规则依据: topics/城主指南2024/停工期/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ProjectStatus(str, Enum):
    """项目状态。"""

    PLANNED = "planned"           # 已规划
    IN_PROGRESS = "in_progress"   # 进行中
    COMPLETED = "completed"       # 已完成
    ABANDONED = "abandoned"       # 已放弃
    FAILED = "failed"             # 失败


@dataclass
class CraftingRequirement:
    """制作材料需求。"""

    item_tag: str = ""              # 物品标签
    quantity: int = 1               # 数量
    consumed: bool = True           # 是否消耗


@dataclass
class ProjectDefinition:
    """停工期项目定义。

    EXP-003: 使用ProjectDefinition实现。
    """

    project_id: str                       # canonical ID
    name: str                             # 项目名称
    project_type: str = "crafting"        # crafting/research/training/travel
    description: str = ""

    # 工时需求
    total_work_days: float = 1.0          # 总工时（天）
    work_completed: float = 0.0           # 已完成工时

    # 成本
    cost_gp: float = 0.0                  # 金币成本
    requirements: List[CraftingRequirement] = field(default_factory=list)

    # 技能检定
    check_ability: str = "int"            # 检定属性
    check_dc: int = 15                    # 检定 DC
    check_interval_days: float = 5.0      # 每隔多少天检定一次

    # 状态
    status: ProjectStatus = ProjectStatus.PLANNED
    started_at_day: float = 0.0           # 开始时的游戏天数
    completed_at_day: float = 0.0         # 完成时的游戏天数

    def progress_percent(self) -> float:
        """获取进度百分比。"""
        if self.total_work_days <= 0:
            return 100.0
        return min(100.0, (self.work_completed / self.total_work_days) * 100.0)

    def is_complete(self) -> bool:
        """判断项目是否已完成。"""
        return self.work_completed >= self.total_work_days

    def advance(self, days: float) -> None:
        """推进项目工时。"""
        self.work_completed += days
        if self.is_complete():
            self.status = ProjectStatus.COMPLETED


@dataclass
class ProgressEvent:
    """项目进度事件。"""

    event_type: str = ""          # work_done/check_passed/check_failed/completed/abandoned
    project_id: str = ""
    day: float = 0.0
    details: str = ""


@dataclass
class DowntimeManager:
    """停工期管理器 — 统一管理所有停工期项目。

    EXP-003: 将DMG模块定义为独立里程碑。
    """

    _projects: Dict[str, ProjectDefinition] = field(default_factory=dict)
    _events: List[ProgressEvent] = field(default_factory=list)

    def start_project(self, project: ProjectDefinition,
                      game_day: float = 0.0) -> None:
        """开始一个停工期项目。"""
        project.status = ProjectStatus.IN_PROGRESS
        project.started_at_day = game_day
        self._projects[project.project_id] = project

    def advance_project(self, project_id: str, days: float,
                        game_day: float = 0.0) -> Optional[ProgressEvent]:
        """推进指定项目的工时。"""
        project = self._projects.get(project_id)
        if project is None or project.status != ProjectStatus.IN_PROGRESS:
            return None

        project.advance(days)

        if project.is_complete():
            project.completed_at_day = game_day
            event = ProgressEvent(
                event_type="completed",
                project_id=project_id,
                day=game_day,
                details=f"项目「{project.name}」已完成",
            )
            self._events.append(event)
            return event

        event = ProgressEvent(
            event_type="work_done",
            project_id=project_id,
            day=game_day,
            details=f"项目「{project.name}」进度 {project.progress_percent():.0f}%",
        )
        self._events.append(event)
        return event

    def get_project(self, project_id: str) -> Optional[ProjectDefinition]:
        """获取指定项目。"""
        return self._projects.get(project_id)

    def list_active_projects(self) -> List[ProjectDefinition]:
        """列出所有进行中的项目。"""
        return [p for p in self._projects.values()
                if p.status == ProjectStatus.IN_PROGRESS]

    def get_events(self) -> List[ProgressEvent]:
        """获取所有进度事件。"""
        return list(self._events)
