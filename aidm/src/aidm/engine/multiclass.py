"""兼职规则引擎 — 前置条件 / 法术位合并 / 兼职熟练。

规则依据:
  - R-MC-001 兼职前置属性值
  - R-MC-002 兼职法术位合并表（全/半/1/3施法者）
  - R-MC-003 兼职获得的熟练
出处: topics/玩家手册2024/创建角色/兼职.htm
"""

from __future__ import annotations

import math

# ──────────────────────────────────────────────────────────────────────────
# 兼职前置条件
# ──────────────────────────────────────────────────────────────────────────

MULTICLASS_PREREQUISITES: dict[str, dict[str, int]] = {
    "野蛮人": {"str": 13},
    "吟游诗人": {"cha": 13},
    "牧师": {"wis": 13},
    "德鲁伊": {"wis": 13},
    "战士": {"str": 13},       # 或 dex≥13
    "武僧": {"dex": 13, "wis": 13},
    "圣武士": {"str": 13, "cha": 13},
    "游侠": {"dex": 13, "wis": 13},
    "游荡者": {"dex": 13},
    "术士": {"cha": 13},
    "魔契师": {"cha": 13},
    "法师": {"int": 13},
}

# 施法者类型：全/半/第三
_FULL_CASTERS = frozenset({"吟游诗人", "牧师", "德鲁伊", "术士", "法师"})
_HALF_CASTERS = frozenset({"圣武士", "游侠"})
_THIRD_CASTERS = frozenset(set())  # 2024无第三施法者核心职业（奥术骗子/战刃为子职）
_PACT_CASTERS = frozenset({"魔契师"})  # 契约魔法独立

# 合并法术位表（全施法者等级→法术位）
_SPELL_SLOTS_BY_LEVEL: dict[int, dict[int, int]] = {
    1: {1:2}, 2: {1:3}, 3: {1:4,2:2}, 4: {1:4,2:3}, 5: {1:4,2:3,3:2},
    6: {1:4,2:3,3:3}, 7: {1:4,2:3,3:3,4:1}, 8: {1:4,2:3,3:3,4:2},
    9: {1:4,2:3,3:3,4:3,5:1}, 10: {1:4,2:3,3:3,4:3,5:2},
    11: {1:4,2:3,3:3,4:3,5:2,6:1}, 12: {1:4,2:3,3:3,4:3,5:2,6:1},
    13: {1:4,2:3,3:3,4:3,5:2,6:1,7:1}, 14: {1:4,2:3,3:3,4:3,5:2,6:1,7:1},
    15: {1:4,2:3,3:3,4:3,5:2,6:1,7:1,8:1}, 16: {1:4,2:3,3:3,4:3,5:2,6:1,7:1,8:1},
    17: {1:4,2:3,3:3,4:3,5:2,6:1,7:1,8:1,9:1}, 18: {1:4,2:3,3:3,4:3,5:3,6:1,7:1,8:1,9:1},
    19: {1:4,2:3,3:3,4:3,5:3,6:2,7:1,8:1,9:1}, 20: {1:4,2:3,3:3,4:3,5:3,6:2,7:2,8:1,9:1},
}


def can_multiclass(current_classes: dict[str, int], new_class: str,
                   abilities: dict[str, int]) -> dict:
    """校验能否兼职到新职业。

    规则: R-MC-001 兼职前置属性值
    出处: topics/玩家手册2024/创建角色/兼职.htm
    参数:
      current_classes: {"战士": 5, "法师": 3} 当前职业等级
      new_class: 要兼入的新职业名
      abilities: {"str":15,"dex":14,...} 属性值
    """
    prereqs = MULTICLASS_PREREQUISITES.get(new_class)
    if prereqs is None:
        return {"can_multiclass": False, "reason": f"未知职业 {new_class!r}"}
    # 战士特殊：str≥13 或 dex≥13
    if new_class == "战士":
        if abilities.get("str", 0) < 13 and abilities.get("dex", 0) < 13:
            return {"can_multiclass": False, "reason": "需要力量≥13或敏捷≥13"}
    else:
        for ab, min_val in prereqs.items():
            if abilities.get(ab, 0) < min_val:
                return {"can_multiclass": False,
                        "reason": f"需要{ab}≥{min_val}，当前{abilities.get(ab,0)}"}
    return {"can_multiclass": True, "reason": None}


def multiclass_caster_level(classes: dict[str, int]) -> int:
    """计算兼职合并施法者等级。

    规则: R-MC-002 兼职法术位合并
    出处: topics/玩家手册2024/创建角色/兼职.htm
    说明: 全施法者等级全加；半施法者等级÷2（向下取整）；第三施法者÷3。
          契约魔法（魔契师）不参与合并。
    """
    total = 0
    for cls, lvl in classes.items():
        if cls in _FULL_CASTERS:
            total += lvl
        elif cls in _HALF_CASTERS:
            total += math.floor(lvl / 2)
        elif cls in _THIRD_CASTERS:
            total += math.floor(lvl / 3)
        # 魔契师不参与合并
    return total


def multiclass_spell_slots(classes: dict[str, int]) -> dict[int, int]:
    """兼职合并法术位表。

    规则: R-MC-002 兼职法术位合并
    出处: topics/玩家手册2024/创建角色/兼职.htm
    返回: {环阶: 法术位数量}
    """
    caster_lvl = multiclass_caster_level(classes)
    if caster_lvl <= 0:
        return {}
    caster_lvl = min(20, caster_lvl)
    return dict(_SPELL_SLOTS_BY_LEVEL.get(caster_lvl, {}))


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 前置条件
    assert can_multiclass({}, "法师", {"int": 13})["can_multiclass"] is True
    assert can_multiclass({}, "法师", {"int": 12})["can_multiclass"] is False
    # 战士特殊：str 或 dex
    assert can_multiclass({}, "战士", {"str": 13, "dex": 8})["can_multiclass"] is True
    assert can_multiclass({}, "战士", {"str": 10, "dex": 13})["can_multiclass"] is True
    assert can_multiclass({}, "战士", {"str": 10, "dex": 10})["can_multiclass"] is False

    # 施法者等级
    assert multiclass_caster_level({"法师": 5}) == 5
    assert multiclass_caster_level({"法师": 3, "牧师": 2}) == 5
    assert multiclass_caster_level({"圣武士": 6}) == 3  # 半施法者÷2
    assert multiclass_caster_level({"法师": 3, "圣武士": 4}) == 5  # 3+floor(4/2)=5
    assert multiclass_caster_level({"魔契师": 5}) == 0  # 契约不参与

    # 法术位合并
    slots = multiclass_spell_slots({"法师": 5})
    assert slots == {1: 4, 2: 3, 3: 2}  # 5级全施法者
    slots = multiclass_spell_slots({"法师": 3, "牧师": 2})
    assert slots[3] == 2  # 5级施法者有3环位

    print("[multiclass] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
