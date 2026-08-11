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
# 兼职熟练授予规则
# ──────────────────────────────────────────────────────────────────────────

MULTICLASS_PROFICIENCIES: dict[str, dict[str, list[str]]] = {
    "野蛮人": {"armor": [], "weapons": ["simple", "martial"], "tools": [], "saves": ["str", "con"]},
    "吟游诗人": {"armor": ["light"], "weapons": ["simple", "hand_crossbow", "longsword", "rapier", "shortsword"], "tools": ["musical_instrument_choice_3"], "saves": ["dex", "cha"]},
    "牧师": {"armor": ["light", "medium", "shields"], "weapons": ["simple"], "tools": [], "saves": ["wis", "cha"]},
    "德鲁伊": {"armor": ["light", "medium", "shields"], "weapons": ["club", "dagger", "dart", "javelin", "mace", "quarterstaff", "scimitar", "sickle", "spear"], "tools": ["herbalism_kit"], "saves": ["int", "wis"]},
    "战士": {"armor": ["light", "medium", "shields"], "weapons": ["simple", "martial"], "tools": [], "saves": ["str", "con"]},  # 或 dex 代替 str
    "武僧": {"armor": ["light"], "weapons": ["simple", "shortsword"], "tools": ["artisan_tools_choice_1"], "saves": ["str", "dex"]},
    "圣武士": {"armor": ["light", "medium", "shields"], "weapons": ["simple", "martial"], "tools": [], "saves": ["str", "cha"]},
    "游侠": {"armor": ["light", "medium", "shields"], "weapons": ["simple", "martial"], "tools": [], "saves": ["str", "dex"]},
    "游荡者": {"armor": ["light"], "weapons": ["simple", "hand_crossbow", "longsword", "rapier", "shortsword"], "tools": ["thieves_tools"], "saves": ["dex", "int"]},
    "术士": {"armor": [], "weapons": ["dagger", "dart", "sling", "quarterstaff", "light_crossbow"], "tools": [], "saves": ["con", "cha"]},
    "魔契师": {"armor": ["light"], "weapons": ["simple"], "tools": [], "saves": ["wis", "cha"]},
    "法师": {"armor": [], "weapons": ["dagger", "dart", "sling", "quarterstaff", "light_crossbow"], "tools": [], "saves": ["int", "wis"]},
}

# Extra Attack 来源列表（同名不叠加）
EXTRA_ATTACK_FEATURES = frozenset({
    "barbarian_extra_attack",
    "bard_extra_attack",
    "fighter_extra_attack",
    "monk_extra_attack",
    "paladin_extra_attack",
    "ranger_extra_attack",
})


class MulticlassService:
    """兼职服务 — 完整校验兼职合法性、熟练授予、Extra Attack 去重、施法位合并。"""

    def __init__(self) -> None:
        pass

    def validate_multiclass(
        self,
        current_classes: dict[str, int],
        new_class: str,
        abilities: dict[str, int],
    ) -> dict:
        """校验能否兼职到新职业。

        规则: R-MC-001 兼职前置属性值
        返回: {"valid": bool, "reason": str|None}
        """
        result = can_multiclass(current_classes, new_class, abilities)
        return {"valid": result["can_multiclass"], "reason": result.get("reason")}

    def get_proficiencies_granted(
        self,
        new_class: str,
        existing_proficiencies: set[str],
    ) -> dict:
        """计算兼职新职业获得的熟练项（去重后）。

        规则: R-MC-003 兼职获得的熟练
        返回: {"armor": [...], "weapons": [...], "tools": [...], "saves": [...]}
        """
        profs = MULTICLASS_PROFICIENCIES.get(new_class, {})
        result = {"armor": [], "weapons": [], "tools": [], "saves": []}

        # 护甲熟练
        for armor in profs.get("armor", []):
            if armor not in existing_proficiencies:
                result["armor"].append(armor)

        # 武器熟练
        for weapon in profs.get("weapons", []):
            if weapon not in existing_proficiencies:
                result["weapons"].append(weapon)

        # 工具熟练
        for tool in profs.get("tools", []):
            if tool not in existing_proficiencies:
                result["tools"].append(tool)

        # 豁免熟练（兼职不给新豁免）
        # 规则: 兼职时不获得新的豁免熟练

        return result

    def calculate_extra_attacks(self, features: list[str],
                                class_levels: dict[str, int] | None = None) -> int:
        """计算额外攻击次数（Extra Attack 同名不叠加）。

        规则: Extra Attack 特性不叠加
        战士特殊: 11级获得第2次额外攻击，20级获得第3次。
        其他职业: 有 Extra Attack 特性就 +1 次。
        返回: 额外攻击次数（0、1、2 或 3）
        """
        has_extra_attack = any(
            feat in EXTRA_ATTACK_FEATURES for feat in features
        )
        if not has_extra_attack:
            return 0

        # 基础: 1 次额外攻击
        extra = 1

        # 战士多重攻击: 11级 +1, 20级 +1
        if class_levels:
            fighter_lvl = class_levels.get("战士", 0)
            if fighter_lvl >= 20:
                extra += 2  # 11级+1, 20级+1
            elif fighter_lvl >= 11:
                extra += 1  # 11级+1

        return extra

    def get_spell_slots(self, classes: dict[str, int]) -> dict[int, int]:
        """计算兼职合并法术位。

        规则: R-MC-002 兼职法术位合并
        说明: 魔契师独立计算，不参与合并。
        """
        return multiclass_spell_slots(classes)

    def get_pact_slots(self, warlock_level: int) -> dict[int, int]:
        """获取魔契师独立法术位。

        规则: 魔契师法术位独立于多职业合并
        返回: {环阶: 法术位数量}
        """
        if warlock_level <= 0:
            return {}
        # 魔契师法术位表
        pact_slots = {
            1: {1: 1}, 2: {1: 2}, 3: {2: 2}, 4: {2: 2}, 5: {3: 2},
            6: {3: 2}, 7: {4: 2}, 8: {4: 2}, 9: {5: 2}, 10: {5: 2},
            11: {5: 3}, 12: {5: 3}, 13: {5: 3}, 14: {5: 3}, 15: {5: 3},
            16: {5: 3}, 17: {5: 4}, 18: {5: 4}, 19: {5: 4}, 20: {5: 4},
        }
        return dict(pact_slots.get(warlock_level, {}))


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
