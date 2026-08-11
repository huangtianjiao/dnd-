"""探索时钟 — 统一世界模拟时钟（旅行/遭遇/补给/行军/饥渴）。

规则依据:
  - EXP-002 探索时钟
  - R-TRV-001 旅行速度（按速度/地形）
  - R-TRV-002 遭遇检定（按地形/天数）
  - R-TRV-003 补给消耗（每人每天1单位）
  - R-TRV-004 强行军（超过8小时/天需体质豁免）
  - R-TRV-005 脱水/饥饿（力竭等级）
出处: topics/城主指南2024/2.运作游戏/运作交涉/旅行.htm
      topics/玩家手册2024/装备/旅行.htm
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ──────────────────────────────────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────────────────────────────────

# 每日正常旅行小时数（超过则为强行军）
NORMAL_TRAVEL_HOURS_PER_DAY = 8

# 遭遇检定 DC（按地形类型）
# 规则: R-TRV-002 旅行遭遇检定
ENCOUNTER_DC_BY_TERRAIN: dict[str, int] = {
    "urban": 15,
    "normal": 12,
    "wilderness": 10,
    "dangerous": 8,
}

# 旅行速度修正（按地形）
# 规则: R-TRV-001 旅行速度
TERRAIN_SPEED_MULTIPLIER: dict[str, float] = {
    "easy": 1.0,
    "normal": 0.75,
    "difficult": 0.5,
    "hazardous": 0.25,
}

# 补给消耗：每人每天1单位
SUPPLY_PER_CREATURE_PER_DAY = 1

# 脱水/饥饿造成的力竭等级
EXHAUSTION_FROM_DEHYDRATION_STARVATION = 1


# ──────────────────────────────────────────────────────────────────────────
# ExplorationClock
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class ExplorationClock:
    """统一世界模拟时钟。

    规则: EXP-002 探索时钟
    出处: topics/城主指南2024/2.运作游戏/运作交涉/旅行.htm

    属性:
        current_time: 当前时间（24小时制 HH:MM）
        current_day: 当前天数（从1开始）
        travel_distance_miles: 累计旅行距离（英里）
        supplies_remaining: 剩余补给单位数
        exhaustion_levels: 各实体的力竭等级 {entity_id: level}
        hours_traveled_today: 今日已旅行小时数
        encounter_check_pending: 是否需要遭遇检定
    """
    current_time: str = "06:00"
    current_day: int = 1
    travel_distance_miles: float = 0.0
    supplies_remaining: int = 0
    exhaustion_levels: Dict[str, int] = field(default_factory=dict)
    hours_traveled_today: float = 0.0
    encounter_check_pending: bool = False

    # ── 时间推进 ────────────────────────────────────────────────────────

    def advance_hours(self, hours: int) -> dict:
        """推进指定小时数，更新时间与天数。

        规则: EXP-002 探索时钟
        出处: topics/城主指南2024/2.运作游戏/运作交涉/旅行.htm

        返回:
            dict: {old_time, new_time, old_day, new_day, days_advanced}
        """
        old_time = self.current_time
        old_day = self.current_day

        h, m = map(int, self.current_time.split(":"))
        total_minutes = h * 60 + m + hours * 60
        days_advanced = total_minutes // (24 * 60)
        remaining_minutes = total_minutes % (24 * 60)
        new_h = remaining_minutes // 60
        new_m = remaining_minutes % 60

        self.current_time = f"{new_h:02d}:{new_m:02d}"
        self.current_day += days_advanced

        # 新的一天重置旅行小时数
        if days_advanced > 0:
            self.hours_traveled_today = 0.0

        return {
            "old_time": old_time,
            "new_time": self.current_time,
            "old_day": old_day,
            "new_day": self.current_day,
            "days_advanced": days_advanced,
        }

    # ── 旅行 ────────────────────────────────────────────────────────────

    def travel_day(self, distance_miles: float, terrain: str = "normal") -> dict:
        """执行一天的旅行。

        规则: R-TRV-001 旅行速度 / R-TRV-002 遭遇检定
        出处: topics/城主指南2024/2.运作游戏/运作交涉/旅行.htm

        参数:
            distance_miles: 实际旅行距离（英里）
            terrain: 地形类型 "easy"/"normal"/"difficult"/"hazardous"

        返回:
            dict: {distance, terrain, effective_distance, encounter_check}
        """
        multiplier = TERRAIN_SPEED_MULTIPLIER.get(terrain, 0.75)
        effective_distance = distance_miles * multiplier

        self.travel_distance_miles += distance_miles
        self.hours_traveled_today += NORMAL_TRAVEL_HOURS_PER_DAY
        self.encounter_check_pending = True

        # 推进一天
        result = self.advance_hours(NORMAL_TRAVEL_HOURS_PER_DAY)

        return {
            "distance": distance_miles,
            "terrain": terrain,
            "speed_multiplier": multiplier,
            "effective_distance": effective_distance,
            "total_distance": self.travel_distance_miles,
            "encounter_check": True,
            "day_advanced": result["days_advanced"],
        }

    def check_encounter(self, rng=None) -> bool:
        """执行遭遇检定。

        规则: R-TRV-002 旅行遭遇检定
        出处: topics/城主指南2024/2.运作游戏/运作交涉/旅行.htm

        参数:
            rng: 可选的随机数生成器（需有 roll(sides) 方法）；
                 为 None 时使用默认 d20。

        返回:
            bool: 是否触发遭遇
        """
        if not self.encounter_check_pending:
            return False

        self.encounter_check_pending = False
        return True  # 默认触发（实际由 DM 按 DC 决定）

    def check_encounter_with_dc(self, terrain: str = "normal",
                                 rng=None) -> dict:
        """执行带 DC 的遭遇检定。

        规则: R-TRV-002 旅行遭遇检定
        出处: topics/城主指南2024/2.运作游戏/运作交涉/旅行.htm

        返回:
            dict: {triggered, dc, roll, terrain}
        """
        dc = ENCOUNTER_DC_BY_TERRAIN.get(terrain, 12)
        roll = rng.roll_die(20) if rng and hasattr(rng, "roll_die") else 10
        triggered = roll >= dc
        return {
            "triggered": triggered,
            "dc": dc,
            "roll": roll,
            "terrain": terrain,
        }

    # ── 补给 ────────────────────────────────────────────────────────────

    def consume_supplies(self, num_creatures: int) -> bool:
        """消耗一天的补给。

        规则: R-TRV-003 补给消耗
        出处: topics/城主指南2024/2.运作游戏/运作交涉/旅行.htm

        参数:
            num_creatures: 消耗补给的生物数量

        返回:
            bool: 补给是否充足（True=充足，False=不足）
        """
        needed = num_creatures * SUPPLY_PER_CREATURE_PER_DAY
        if self.supplies_remaining >= needed:
            self.supplies_remaining -= needed
            return True
        # 补给不足：消耗剩余部分
        self.supplies_remaining = max(0, self.supplies_remaining - needed)
        return False

    # ── 强行军 ──────────────────────────────────────────────────────────

    def apply_forced_march(self, hours_beyond_8: int,
                           entity_ids: List[str]) -> List[dict]:
        """应用强行军规则。

        规则: R-TRV-004 强行军
        出处: topics/城主指南2024/2.运作游戏/运作交涉/旅行.htm

        每超过8小时旅行1小时，需进行体质豁免（DC=10+超出小时数）。
        失败则获得1级力竭。

        参数:
            hours_beyond_8: 超过8小时的小时数
            entity_ids: 受影响的实体 ID 列表

        返回:
            每个实体的结果列表 [{entity_id, save_dc, failed, exhaustion}]
        """
        results: List[dict] = []
        for eid in entity_ids:
            save_dc = 10 + hours_beyond_8
            # 此处仅记录 DC，实际豁免由上层掷骰
            current_exhaustion = self.exhaustion_levels.get(eid, 0)
            results.append({
                "entity_id": eid,
                "save_dc": save_dc,
                "hours_beyond_8": hours_beyond_8,
                "current_exhaustion": current_exhaustion,
                "note": f"需进行 DC{save_dc} 体质豁免，失败则+1级力竭",
            })
            self.hours_traveled_today += hours_beyond_8
        return results

    def apply_forced_march_failure(self, entity_id: str) -> dict:
        """应用强行军豁免失败的效果。

        返回:
            dict: {entity_id, old_exhaustion, new_exhaustion}
        """
        old = self.exhaustion_levels.get(entity_id, 0)
        new_level = old + EXHAUSTION_FROM_DEHYDRATION_STARVATION
        self.exhaustion_levels[entity_id] = new_level
        return {
            "entity_id": entity_id,
            "old_exhaustion": old,
            "new_exhaustion": new_level,
        }

    # ── 脱水/饥饿 ──────────────────────────────────────────────────────

    def apply_dehydration_starvation(self, entity_ids: List[str]) -> List[dict]:
        """应用脱水或饥饿效果。

        规则: R-TRV-005 脱水/饥饿
        出处: topics/城主指南2024/2.运作游戏/运作交涉/旅行.htm

        缺少食物或水一天 → 1级力竭（已有力竭则+1级）

        参数:
            entity_ids: 受影响的实体 ID 列表

        返回:
            每个实体的结果列表 [{entity_id, old_exhaustion, new_exhaustion}]
        """
        results: List[dict] = []
        for eid in entity_ids:
            old = self.exhaustion_levels.get(eid, 0)
            new_level = old + EXHAUSTION_FROM_DEHYDRATION_STARVATION
            self.exhaustion_levels[eid] = new_level
            results.append({
                "entity_id": eid,
                "old_exhaustion": old,
                "new_exhaustion": new_level,
                "cause": "dehydration_or_starvation",
            })
        return results

    # ── 辅助 ────────────────────────────────────────────────────────────

    def get_time_tuple(self) -> tuple[int, int]:
        """返回当前时间的 (小时, 分钟) 元组。"""
        h, m = map(int, self.current_time.split(":"))
        return (h, m)

    def is_night(self) -> bool:
        """判断当前是否为夜间（18:00-06:00）。"""
        h, _ = self.get_time_tuple()
        return h >= 18 or h < 6

    def snapshot(self) -> dict:
        """返回时钟当前状态的快照字典。"""
        return {
            "current_time": self.current_time,
            "current_day": self.current_day,
            "travel_distance_miles": self.travel_distance_miles,
            "supplies_remaining": self.supplies_remaining,
            "exhaustion_levels": dict(self.exhaustion_levels),
            "hours_traveled_today": self.hours_traveled_today,
        }
