"""停工期活动与制作装备引擎 — 制作时间/花费 / 停工期活动表。

规则依据:
  - R-DT-001 制作普通物品（每天 25gp 进度）
  - R-DT-002 制作魔法物品（按稀有度查表）
  - R-DT-003 停工期活动（训练/研究/康复）
  - EXP-003 停工期完整公式（中断/失败/资源消耗）
出处: topics/玩家手册2024/装备/制作装备.htm ; topics/城主指南2024/6.宝藏/制作魔法物品.htm
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional

# ──────────────────────────────────────────────────────────────────────────
# 制作普通物品
# ──────────────────────────────────────────────────────────────────────────

CRAFTING_PROGRESS_GP_PER_DAY = 25  # R-DT-001: 每天 25gp 进度


def crafting_time_days(item_value_gp: float, is_magical: bool = False) -> int:
    """制作物品所需天数。

    规则: R-DT-001 普通物品: ceil(价值 / 25) 天
          R-DT-002 魔法物品: 按稀有度查表（此处简化为价值/25，最少 1 天）
    出处: topics/玩家手册2024/装备/制作装备.htm
    """
    if item_value_gp <= 0:
        return 1
    days = math.ceil(item_value_gp / CRAFTING_PROGRESS_GP_PER_DAY)
    return max(1, days)


def crafting_cost(item_value_gp: float) -> float:
    """制作花费 = 物品价值的一半（原材料费用）。

    规则: R-DT-001 制作花费
    出处: topics/玩家手册2024/装备/制作装备.htm
    """
    return item_value_gp / 2


# ──────────────────────────────────────────────────────────────────────────
# 魔法物品制作（按稀有度）
# ──────────────────────────────────────────────────────────────────────────

MAGIC_ITEM_CRAFTING: dict[str, dict] = {
    "普通":   {"min_level": 1,  "cost_gp": 50,     "days": 5},
    "非凡":   {"min_level": 3,  "cost_gp": 200,    "days": 10},
    "稀有":   {"min_level": 6,  "cost_gp": 2000,   "days": 25},
    "非常稀有": {"min_level": 11, "cost_gp": 20000,  "days": 50},
    "传说":   {"min_level": 17, "cost_gp": 100000,  "days": 100},
}


def magic_item_crafting_requirements(rarity: str) -> dict:
    """魔法物品制作需求（等级/花费/天数）。

    规则: R-DT-002 制作魔法物品
    出处: topics/城主指南2024/6.宝藏/制作魔法物品.htm
    """
    entry = MAGIC_ITEM_CRAFTING.get(rarity)
    if entry is None:
        raise ValueError(f"未知稀有度 {rarity!r}，可选: {list(MAGIC_ITEM_CRAFTING)}")
    return dict(entry)


# ──────────────────────────────────────────────────────────────────────────
# 停工期活动
# ──────────────────────────────────────────────────────────────────────────

DOWNTIME_ACTIVITIES: dict[str, dict] = {
    "training":      {"time_days": 75, "cost_gp": 1800,
                      "description": "学习新语言或工具熟练",
                      "interruptible": True,
                      "failure_on_interrupt": "lose_progress_half"},
    "research":      {"time_days_per_question": 7, "cost_gp_per_day": 50,
                      "description": "研究特定问题（每个问题 7 天）",
                      "interruptible": True,
                      "failure_on_interrupt": "retry"},
    "recuperating":  {"time_days": 3, "cost_gp": 0,
                      "description": "康复：结束一个阻碍恢复的效应（如疾病/诅咒）",
                      "interruptible": True,
                      "failure_on_interrupt": "restart"},
    "crafting":      {"description": "制作物品（见 crafting_time_days）",
                      "interruptible": True,
                      "failure_on_interrupt": "lose_progress_half"},
    "carousing":     {"time_days": 1, "cost_gp_per_day": 10,
                      "description": "饮酒作乐，收集情报",
                      "interruptible": False,
                      "failure_on_interrupt": "none"},
    "relaxation":    {"time_days": 7, "cost_gp_per_day": 0,
                      "description": "放松恢复，降低力竭等级",
                      "interruptible": False,
                      "failure_on_interrupt": "none"},
    "work":          {"time_days": 1, "cost_gp_per_day": 0,
                      "earn_gp_per_day": 2,
                      "description": "工作赚钱（每天 2gp）",
                      "interruptible": False,
                      "failure_on_interrupt": "none"},
    "mission":       {"time_days": 0, "cost_gp": 0,
                      "description": "执行派系任务（按任务定义）",
                      "interruptible": True,
                      "failure_on_interrupt": "mission_fail"},
}


def downtime_cost(activity: str, days: int = 0) -> dict:
    """计算停工期活动的时间与金币花费。

    规则: R-DT-003 停工期活动 / EXP-003 停工期完整公式
    出处: topics/城主指南2024/2.运作游戏/运作交涉/停工期活动.htm

    当调用方显式传入 days (>0) 时，使用该天数覆盖默认值；
    否则使用活动定义中的默认天数。
    """
    entry = DOWNTIME_ACTIVITIES.get(activity)
    if entry is None:
        raise ValueError(f"未知停工期活动 {activity!r}，可选: {list(DOWNTIME_ACTIVITIES)}")

    # 显式传入 days 时优先使用
    if days > 0:
        cost_per_day = entry.get("cost_gp_per_day", 0)
        return {"days": days, "cost_gp": days * cost_per_day}

    if "time_days" in entry:
        return {"days": entry["time_days"], "cost_gp": entry.get("cost_gp", 0)}
    if "time_days_per_question" in entry:
        d = entry["time_days_per_question"]
        return {"days": d, "cost_gp": d * entry["cost_gp_per_day"]}
    if "cost_gp_per_day" in entry:
        d = 1
        return {"days": d, "cost_gp": d * entry["cost_gp_per_day"]}
    return {"days": days, "cost_gp": 0}


# ──────────────────────────────────────────────────────────────────────────
# EXP-003: 停工期活动追踪器
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class DowntimeProject:
    """一个停工期项目的追踪记录。

    规则: EXP-003 停工期完整公式
    出处: topics/城主指南2024/2.运作游戏/运作交涉/停工期活动.htm

    属性:
        project_id: 项目唯一 ID
        activity: 活动类型
        total_days: 总需天数
        days_completed: 已完成天数
        total_cost_gp: 总花费
        cost_paid_gp: 已支付花费
        interrupted: 是否被中断
        interrupt_count: 中断次数
        completed: 是否完成
        failed: 是否失败
        resource_log: 资源消耗记录
    """
    project_id: str = ""
    activity: str = ""
    total_days: int = 0
    days_completed: int = 0
    total_cost_gp: float = 0.0
    cost_paid_gp: float = 0.0
    interrupted: bool = False
    interrupt_count: int = 0
    completed: bool = False
    failed: bool = False
    resource_log: List[dict] = field(default_factory=list)

    def advance_days(self, days: int = 1, cost_gp: float = 0.0) -> dict:
        """推进指定天数。

        返回:
            dict: {days_advanced, total_completed, completed, cost_paid}
        """
        if self.completed or self.failed:
            return {"days_advanced": 0, "total_completed": self.days_completed,
                    "completed": self.completed, "cost_paid": 0.0}

        actual_days = min(days, self.total_days - self.days_completed)
        self.days_completed += actual_days
        self.cost_paid_gp += cost_gp
        self.resource_log.append({
            "type": "advance",
            "days": actual_days,
            "cost_gp": cost_gp,
        })

        if self.days_completed >= self.total_days:
            self.completed = True

        return {
            "days_advanced": actual_days,
            "total_completed": self.days_completed,
            "completed": self.completed,
            "cost_paid": cost_gp,
        }

    def interrupt(self) -> dict:
        """中断项目。

        规则: EXP-003 中断/失败规则
        返回:
            dict: {interrupted, failure_type, progress_lost}
        """
        if self.completed or self.failed:
            return {"interrupted": False, "failure_type": "none", "progress_lost": 0}

        self.interrupted = True
        self.interrupt_count += 1

        entry = DOWNTIME_ACTIVITIES.get(self.activity, {})
        failure_type = entry.get("failure_on_interrupt", "none")
        progress_lost = 0

        if failure_type == "lose_progress_half":
            # 失去一半进度
            progress_lost = self.days_completed // 2
            self.days_completed = max(0, self.days_completed - progress_lost)
        elif failure_type == "restart":
            # 完全重新开始
            progress_lost = self.days_completed
            self.days_completed = 0
        elif failure_type == "mission_fail":
            self.failed = True
            progress_lost = self.days_completed

        return {
            "interrupted": True,
            "failure_type": failure_type,
            "progress_lost": progress_lost,
            "days_remaining": self.total_days - self.days_completed,
        }

    def resume(self) -> dict:
        """恢复被中断的项目。"""
        if not self.interrupted or self.failed:
            return {"resumed": False}
        self.interrupted = False
        return {
            "resumed": True,
            "days_remaining": self.total_days - self.days_completed,
        }

    def snapshot(self) -> dict:
        """返回项目状态快照。"""
        return {
            "project_id": self.project_id,
            "activity": self.activity,
            "total_days": self.total_days,
            "days_completed": self.days_completed,
            "total_cost_gp": self.total_cost_gp,
            "cost_paid_gp": self.cost_paid_gp,
            "interrupted": self.interrupted,
            "interrupt_count": self.interrupt_count,
            "completed": self.completed,
            "failed": self.failed,
            "progress_pct": (self.days_completed / self.total_days * 100
                             if self.total_days > 0 else 0),
        }


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 制作时间
    assert crafting_time_days(50) == 2        # 50/25=2
    assert crafting_time_days(100) == 4       # 100/25=4
    assert crafting_time_days(10) == 1        # 10/25→ceil=1
    assert crafting_time_days(0) == 1

    # 制作花费
    assert crafting_cost(100) == 50.0

    # 魔法物品
    r = magic_item_crafting_requirements("稀有")
    assert r["min_level"] == 6 and r["cost_gp"] == 2000 and r["days"] == 25

    # 停工期活动
    r = downtime_cost("training")
    assert r["days"] == 75 and r["cost_gp"] == 1800
    r = downtime_cost("research", days=14)
    assert r["days"] == 14 and r["cost_gp"] == 700  # 14*50

    print("[downtime] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
