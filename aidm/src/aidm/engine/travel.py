"""旅行配速引擎 — 行进速度 / 距离计算 / 配速效果。

规则依据:
  - R-TRV-001 旅行配速表（快速/正常/缓慢）
  - R-TRV-002 困难地形减半
  - R-TRV-003 快速→被动察觉−5 / 缓慢→可潜行
出处: topics/玩家手册2024/进行游戏/旅行.htm
"""

from __future__ import annotations

import math

from . import dice

# ──────────────────────────────────────────────────────────────────────────
# 旅行配速表
# ──────────────────────────────────────────────────────────────────────────

TRAVEL_PACE: dict[str, dict] = {
    "fast":   {"mph": 4, "mpd": 30, "perception_penalty": -5, "can_stealth": False},
    "normal": {"mph": 3, "mpd": 24, "perception_penalty": 0,  "can_stealth": False},
    "slow":   {"mph": 2, "mpd": 18, "perception_penalty": 0,  "can_stealth": True},
}


# ──────────────────────────────────────────────────────────────────────────
# 距离计算
# ──────────────────────────────────────────────────────────────────────────

def travel_distance(pace: str, hours: float, difficult_terrain: bool = False) -> float:
    """计算行进距离（英里）。

    规则: R-TRV-001 旅行配速 / R-TRV-002 困难地形减半
    出处: topics/玩家手册2024/进行游戏/旅行.htm
    参数:
      pace: "fast"/"normal"/"slow"
      hours: 行进时长（小时）
      difficult_terrain: 是否困难地形（距离减半）
    """
    entry = TRAVEL_PACE.get(pace)
    if entry is None:
        raise ValueError(f"未知旅行配速 {pace!r}，可选: fast/normal/slow")
    distance = entry["mph"] * hours
    if difficult_terrain:
        distance /= 2
    return distance


def travel_daily_distance(pace: str, difficult_terrain: bool = False) -> float:
    """一天（8小时行进）的行进距离（英里）。

    规则: R-TRV-001 旅行配速（每日英里数）
    出处: topics/玩家手册2024/进行游戏/旅行.htm
    """
    entry = TRAVEL_PACE.get(pace)
    if entry is None:
        raise ValueError(f"未知旅行配速 {pace!r}")
    mpd = entry["mpd"]
    return mpd / 2 if difficult_terrain else mpd


def travel_perception_penalty(pace: str) -> int:
    """旅行配速对被动察觉的惩罚。

    规则: R-TRV-003 快速配速→被动察觉−5
    出处: topics/玩家手册2024/进行游戏/旅行.htm
    """
    entry = TRAVEL_PACE.get(pace)
    return entry["perception_penalty"] if entry else 0


def can_stealth_while_traveling(pace: str) -> bool:
    """该配速是否允许潜行。

    规则: R-TRV-003 缓慢配速→可潜行
    出处: topics/玩家手册2024/进行游戏/旅行.htm
    """
    entry = TRAVEL_PACE.get(pace)
    return entry["can_stealth"] if entry else False


def travel_encounter_check() -> bool:
    """随机遭遇检查：掷 d20，≥18 则遭遇。

    规则: DMG 随机遭遇频率（每小时约 1/18 概率，简化为 d20≥18）
    出处: topics/城主指南2024/2.运作游戏/运作交涉/随机遭遇.htm
    说明: 每小时调用一次；DM 可按环境调整频率（此处用默认值）。
    """
    return dice.roll_die(20) >= 18


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 距离计算
    assert travel_distance("fast", 1) == 4.0
    assert travel_distance("normal", 2) == 6.0
    assert travel_distance("slow", 1, difficult_terrain=True) == 1.0  # 2/2=1

    # 每日距离
    assert travel_daily_distance("fast") == 30
    assert travel_daily_distance("normal") == 24
    assert travel_daily_distance("slow", difficult_terrain=True) == 9.0  # 18/2

    # 配速效果
    assert travel_perception_penalty("fast") == -5
    assert travel_perception_penalty("normal") == 0
    assert can_stealth_while_traveling("slow") is True
    assert can_stealth_while_traveling("fast") is False

    # 遭遇检查（只验证返回布尔）
    r = travel_encounter_check()
    assert isinstance(r, bool)

    print("[travel] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
