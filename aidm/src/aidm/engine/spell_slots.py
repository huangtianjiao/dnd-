"""法术位进度表 — 全施法者/半施法者/三分之一施法者/魔契术士。

提供统一的法术位计算入口，支持单职业与兼职合并。

规则依据:
  - R-SPL-002 法术位消耗
  - R-SPL-003 长休恢复
  - R-MC-002 兼职法术位合并表（全/半/1/3施法者）
出处: topics/玩家手册2024/法术/法术环阶.htm ; 创建角色/兼职.htm
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional


# ──────────────────────────────────────────────────────────────────────────
# 职业施法者类型分类
# ──────────────────────────────────────────────────────────────────────────

FULL_CASTERS: frozenset[str] = frozenset({
    "吟游诗人", "牧师", "德鲁伊", "术士", "法师",
})
"""全施法者 — 等级直接查表。"""

HALF_CASTERS: frozenset[str] = frozenset({"圣武士", "游侠"})
"""半施法者 — 等级÷2（向下取整）查表。"""

THIRD_CASTERS: frozenset[str] = frozenset(set())
"""三分之一施法者 — 等级÷3（向下取整）查表。
2024 核心职业中无此类（奥术骗子/战刃为子职，非独立职业）。"""

PACT_CASTERS: frozenset[str] = frozenset({"魔契师"})
"""魔契术士 — 独立法术位表，短休恢复。"""

ALL_CASTER_TYPES: frozenset[str] = FULL_CASTERS | HALF_CASTERS | THIRD_CASTERS | PACT_CASTERS
"""所有施法职业合集。"""


# ──────────────────────────────────────────────────────────────────────────
# 全施法者法术位进度表 (1-20 级)
# 规则: R-SPL-002 法术位消耗
# 出处: topics/玩家手册2024/法术/法术环阶.htm
# ──────────────────────────────────────────────────────────────────────────

FULL_CASTER_SLOTS: Dict[int, Dict[int, int]] = {
    1:  {1: 2},
    2:  {1: 3},
    3:  {1: 4, 2: 2},
    4:  {1: 4, 2: 3},
    5:  {1: 4, 2: 3, 3: 2},
    6:  {1: 4, 2: 3, 3: 3},
    7:  {1: 4, 2: 3, 3: 3, 4: 1},
    8:  {1: 4, 2: 3, 3: 3, 4: 2},
    9:  {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
}


# ──────────────────────────────────────────────────────────────────────────
# 半施法者法术位进度表 (1-20 级)
# 规则: 圣武士/游侠 — 等级÷2 查表（向下取整）
# 出处: topics/玩家手册2024/角色职业/圣武士/施法.htm
# ──────────────────────────────────────────────────────────────────────────

HALF_CASTER_SLOTS: Dict[int, Dict[int, int]] = {
    1:  {},
    2:  {1: 2},
    3:  {1: 3},
    4:  {1: 3},
    5:  {1: 4, 2: 2},
    6:  {1: 4, 2: 2},
    7:  {1: 4, 2: 3},
    8:  {1: 4, 2: 3},
    9:  {1: 4, 2: 3, 3: 2},
    10: {1: 4, 2: 3, 3: 2},
    11: {1: 4, 2: 3, 3: 3},
    12: {1: 4, 2: 3, 3: 3},
    13: {1: 4, 2: 3, 3: 3, 4: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 2},
    16: {1: 4, 2: 3, 3: 3, 4: 2},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
}


# ──────────────────────────────────────────────────────────────────────────
# 三分之一施法者法术位进度表 (1-20 级)
# 规则: 等级÷3 查表（向下取整）
# 出处: 2024 核心职业中无此类，预留扩展
# ──────────────────────────────────────────────────────────────────────────

THIRD_CASTER_SLOTS: Dict[int, Dict[int, int]] = {
    1:  {},
    2:  {},
    3:  {1: 2},
    4:  {1: 2},
    5:  {1: 3},
    6:  {1: 3},
    7:  {1: 3, 2: 2},
    8:  {1: 3, 2: 2},
    9:  {1: 4, 2: 2},
    10: {1: 4, 2: 2},
    11: {1: 4, 2: 3},
    12: {1: 4, 2: 3},
    13: {1: 4, 2: 3, 3: 1},
    14: {1: 4, 2: 3, 3: 1},
    15: {1: 4, 2: 3, 3: 2},
    16: {1: 4, 2: 3, 3: 2},
    17: {1: 4, 2: 3, 3: 3, 4: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 2},
    20: {1: 4, 2: 3, 3: 3, 4: 2},
}


# ──────────────────────────────────────────────────────────────────────────
# 魔契术士独立法术位 (Pact Magic)
# 规则: 魔契师法术位独立于合并施法者等级，短休恢复
# 出处: topics/玩家手册2024/角色职业/魔契师/契约魔法.htm
# ──────────────────────────────────────────────────────────────────────────

PATRON_SLOTS: Dict[int, Dict[int, int]] = {
    1:  {1: 1},
    2:  {1: 2},
    3:  {1: 2},
    4:  {2: 2},
    5:  {2: 2},
    6:  {2: 2},
    7:  {2: 2},
    8:  {2: 2},
    9:  {2: 2},
    10: {2: 2},
    11: {3: 2},
    12: {3: 2},
    13: {3: 2},
    14: {3: 2},
    15: {3: 2},
    16: {3: 2},
    17: {4: 2},
    18: {4: 2},
    19: {4: 2},
    20: {4: 2},
}

# 魔契术士法术环阶上限（随等级提升）
_PACT_SLOT_LEVEL_BY_TIER: Dict[int, int] = {
    # level: max_slot_level
    1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 2,
    11: 3, 12: 3, 13: 3, 14: 3, 15: 3, 16: 3,
    17: 4, 18: 4, 19: 4, 20: 4,
}


# ──────────────────────────────────────────────────────────────────────────
# SpellSlotCalculator
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class SpellSlotCalculator:
    """法术位计算器（SPL-004）。

    规则: R-SPL-002 法术位消耗 / R-MC-002 兼职法术位合并
    出处: topics/玩家手册2024/法术/法术环阶.htm ; 创建角色/兼职.htm
    """

    @staticmethod
    def slots_for_class_level(class_name: str, level: int) -> Dict[int, int]:
        """单职业单等级法术位查询。

        规则: R-SPL-002 法术位消耗
        参数:
            class_name: 职业名
            level: 职业等级 (1-20)
        返回: {环阶: 法术位数量}
        """
        level = max(1, min(20, level))
        if class_name in FULL_CASTERS:
            return dict(FULL_CASTER_SLOTS.get(level, {}))
        if class_name in HALF_CASTERS:
            return dict(HALF_CASTER_SLOTS.get(level, {}))
        if class_name in THIRD_CASTERS:
            return dict(THIRD_CASTER_SLOTS.get(level, {}))
        if class_name in PACT_CASTERS:
            return dict(PATRON_SLOTS.get(level, {}))
        return {}

    @staticmethod
    def multiclass_caster_level(
        class_levels: Dict[str, int],
        class_types: Dict[str, str] | None = None,
    ) -> int:
        """兼职合并施法者等级。

        规则: R-MC-002 兼职法术位合并
        出处: topics/玩家手册2024/创建角色/兼职.htm
        说明:
          - 全施法者: 等级全加
          - 半施法者: 等级÷2（向下取整）
          - 三分之一: 等级÷3（向下取整）
          - 魔契师: 不参与合并（独立法术位）
        参数:
            class_levels: {"法师": 5, "圣武士": 4}
            class_types: 可选，覆盖自动检测 {"法师": "full", "圣武士": "half"}
        返回: 合并施法者等级
        """
        total = 0
        for cls, lvl in class_levels.items():
            if cls in PACT_CASTERS:
                continue  # 魔契师不参与合并
            caster_type = _resolve_caster_type(cls, class_types)
            if caster_type == "full":
                total += lvl
            elif caster_type == "half":
                total += math.floor(lvl / 2)
            elif caster_type == "third":
                total += math.floor(lvl / 3)
        return total

    @staticmethod
    def calculate_slots(
        class_levels: Dict[str, int],
        class_types: Dict[str, str] | None = None,
    ) -> Dict[int, int]:
        """计算合并法术位。

        规则: R-MC-002 兼职法术位合并
        参数:
            class_levels: {"法师": 5, "牧师": 3} 各职业等级
            class_types: 可选覆盖 {"法师": "full"}
        返回: {环阶: 法术位数量}
        """
        caster_lvl = SpellSlotCalculator.multiclass_caster_level(
            class_levels, class_types,
        )
        if caster_lvl <= 0:
            return {}
        caster_lvl = min(20, caster_lvl)
        return dict(FULL_CASTER_SLOTS.get(caster_lvl, {}))

    @staticmethod
    def pact_slots(warlock_level: int) -> Dict[int, int]:
        """魔契师独立法术位。

        规则: 契约魔法 — 魔契师法术位独立，短休恢复
        出处: topics/玩家手册2024/角色职业/魔契师/契约魔法.htm
        参数:
            warlock_level: 魔契师等级 (1-20)
        返回: {环阶: 法术位数量}
        """
        warlock_level = max(1, min(20, warlock_level))
        return dict(PATRON_SLOTS.get(warlock_level, {}))

    @staticmethod
    def pact_slot_level(warlock_level: int) -> int:
        """魔契师当前法术位环阶。

        出处: topics/玩家手册2024/角色职业/魔契师/契约魔法.htm
        """
        warlock_level = max(1, min(20, warlock_level))
        return _PACT_SLOT_LEVEL_BY_TIER.get(warlock_level, 0)


# ──────────────────────────────────────────────────────────────────────────
# 内部辅助
# ──────────────────────────────────────────────────────────────────────────

def _resolve_caster_type(
    class_name: str,
    class_types: Dict[str, str] | None,
) -> str:
    """解析职业的施法者类型。

    返回: "full" / "half" / "third" / "pact" / "none"
    """
    if class_types and class_name in class_types:
        return class_types[class_name]
    if class_name in FULL_CASTERS:
        return "full"
    if class_name in HALF_CASTERS:
        return "half"
    if class_name in THIRD_CASTERS:
        return "third"
    if class_name in PACT_CASTERS:
        return "pact"
    return "none"


# ──────────────────────────────────────────────────────────────────────────
# 便捷函数
# ──────────────────────────────────────────────────────────────────────────

def get_max_slots(class_name: str, level: int) -> Dict[int, int]:
    """单职业最大法术位（便捷函数）。

    参数:
        class_name: 职业名
        level: 职业等级
    返回: {环阶: 法术位数量}
    """
    return SpellSlotCalculator.slots_for_class_level(class_name, level)


def get_combined_slots(class_levels: Dict[str, int]) -> Dict[int, int]:
    """兼职合并法术位（便捷函数）。

    参数:
        class_levels: {"法师": 5, "圣武士": 4}
    返回: {环阶: 法术位数量}
    """
    return SpellSlotCalculator.calculate_slots(class_levels)


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    calc = SpellSlotCalculator

    # 全施法者单职业
    assert calc.slots_for_class_level("法师", 1) == {1: 2}
    assert calc.slots_for_class_level("法师", 5) == {1: 4, 2: 3, 3: 2}
    assert calc.slots_for_class_level("牧师", 20)[9] == 1
    assert calc.slots_for_class_level("术士", 9)[5] == 1

    # 半施法者
    assert calc.slots_for_class_level("圣武士", 1) == {}
    assert calc.slots_for_class_level("圣武士", 2) == {1: 2}
    assert calc.slots_for_class_level("游侠", 5) == {1: 4, 2: 2}
    assert calc.slots_for_class_level("圣武士", 9) == {1: 4, 2: 3, 3: 2}

    # 魔契师独立
    assert calc.slots_for_class_level("魔契师", 1) == {1: 1}
    assert calc.slots_for_class_level("魔契师", 4) == {2: 2}
    assert calc.slots_for_class_level("魔契师", 11) == {3: 2}
    assert calc.pact_slot_level(1) == 1
    assert calc.pact_slot_level(4) == 2
    assert calc.pact_slot_level(11) == 3
    assert calc.pact_slot_level(17) == 4

    # 兼职合并
    assert calc.multiclass_caster_level({"法师": 5}) == 5
    assert calc.multiclass_caster_level({"法师": 3, "牧师": 2}) == 5
    assert calc.multiclass_caster_level({"圣武士": 6}) == 3
    assert calc.multiclass_caster_level({"法师": 3, "圣武士": 4}) == 5
    assert calc.multiclass_caster_level({"魔契师": 5}) == 0  # 不参与合并

    # 合并法术位
    slots = calc.calculate_slots({"法师": 5})
    assert slots == {1: 4, 2: 3, 3: 2}
    slots = calc.calculate_slots({"法师": 3, "圣武士": 4})
    assert slots[3] == 2  # 5级施法者

    # 便捷函数
    assert get_max_slots("法师", 5) == {1: 4, 2: 3, 3: 2}
    assert get_combined_slots({"法师": 3, "牧师": 2})[3] == 2

    print("[spell_slots] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
