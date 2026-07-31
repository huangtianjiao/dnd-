"""停工期活动与制作装备引擎 — 制作时间/花费 / 停工期活动表。

规则依据:
  - R-DT-001 制作普通物品（每天 25gp 进度）
  - R-DT-002 制作魔法物品（按稀有度查表）
  - R-DT-003 停工期活动（训练/研究/康复）
出处: topics/玩家手册2024/装备/制作装备.htm ; topics/城主指南2024/6.宝藏/制作魔法物品.htm
"""

from __future__ import annotations

import math

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
                      "description": "学习新语言或工具熟练"},
    "research":      {"time_days_per_question": 7, "cost_gp_per_day": 50,
                      "description": "研究特定问题（每个问题 7 天）"},
    "recuperating":  {"time_days": 3, "cost_gp": 0,
                      "description": "康复：结束一个阻碍恢复的效应（如疾病/诅咒）"},
    "crafting":      {"description": "制作物品（见 crafting_time_days）"},
}


def downtime_cost(activity: str, days: int = 0) -> dict:
    """计算停工期活动的时间与金币花费。

    规则: R-DT-003 停工期活动
    出处: topics/城主指南2024/2.运作游戏/运作交涉/停工期活动.htm
    """
    entry = DOWNTIME_ACTIVITIES.get(activity)
    if entry is None:
        raise ValueError(f"未知停工期活动 {activity!r}，可选: {list(DOWNTIME_ACTIVITIES)}")
    if "time_days" in entry:
        return {"days": entry["time_days"], "cost_gp": entry.get("cost_gp", 0)}
    if "time_days_per_question" in entry:
        d = days or entry["time_days_per_question"]
        return {"days": d, "cost_gp": d * entry["cost_gp_per_day"]}
    return {"days": days, "cost_gp": 0}


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
