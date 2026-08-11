"""魔法物品调谐引擎 — 调谐上限 / 前置条件 / 调谐与结束。

规则依据:
  - R-ITM-020 调谐上限（3件）
  - R-ITM-021 调谐需短休
  - R-ITM-022 调谐前置条件（职业/等级/属性）
  - R-ITM-023 结束调谐（无需动作）
出处: topics/玩家手册2024/装备/魔法物品.htm
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────────────────────────────────

MAX_ATTUNED = 3  # R-ITM-020 调谐上限

# ──────────────────────────────────────────────────────────────────────────
# 调谐判定
# ──────────────────────────────────────────────────────────────────────────


def can_attune(
    current_attuned: list[str],
    item_name: str,
    *,
    item_requires: dict | None = None,
    char_class: str = "",
    char_level: int = 1,
    char_abilities: dict | None = None,
) -> dict:
    """校验角色能否与指定魔法物品调谐。

    规则: R-ITM-020 调谐上限3件 / R-ITM-022 前置条件
    出处: topics/玩家手册2024/装备/魔法物品.htm

    参数:
      current_attuned: 当前已调谐物品名称列表
      item_name: 待调谐物品名称
      item_requires: 物品前置条件 {"class": [...], "level": int, "ability": {"str":13}}
      char_class/char_level/char_abilities: 角色信息

    返回:
      {"can_attune": bool, "reason": str|None}
    """
    # 已调谐该物品
    if item_name in current_attuned:
        return {"can_attune": False, "reason": "already_attuned"}

    # 调谐上限
    if len(current_attuned) >= MAX_ATTUNED:
        return {"can_attune": False,
                "reason": f"调谐上限已满（{MAX_ATTUNED}件）"}

    # 前置条件校验
    if item_requires:
        # 职业限制
        req_classes = item_requires.get("class")
        if req_classes and char_class not in req_classes:
            return {"can_attune": False,
                    "reason": f"需要职业: {req_classes}"}
        # 等级限制
        req_level = item_requires.get("level", 0)
        if req_level and char_level < req_level:
            return {"can_attune": False,
                    "reason": f"需要等级≥{req_level}，当前{char_level}"}
        # 属性限制
        req_abilities = item_requires.get("ability", {})
        if req_abilities and char_abilities:
            for ab, min_val in req_abilities.items():
                if char_abilities.get(ab, 0) < min_val:
                    return {"can_attune": False,
                            "reason": f"需要{ab}≥{min_val}"}

    return {"can_attune": True, "reason": None}


def attune(current_attuned: list[str], item_name: str) -> list[str]:
    """执行调谐（前提：已通过 can_attune 校验；需短休完成）。

    规则: R-ITM-021 调谐需短休
    出处: topics/玩家手册2024/装备/魔法物品.htm
    返回: 新的已调谐列表
    """
    if item_name in current_attuned:
        return list(current_attuned)
    result = list(current_attuned)
    result.append(item_name)
    return result


def end_attunement(current_attuned: list[str], item_name: str) -> list[str]:
    """结束调谐（无需动作，立即生效）。

    规则: R-ITM-023 结束调谐
    出处: topics/玩家手册2024/装备/魔法物品.htm
    返回: 新的已调谐列表
    """
    result = list(current_attuned)
    if item_name in result:
        result.remove(item_name)
    return result


# ──────────────────────────────────────────────────────────────────────────
# 同调服务 (ITEM-003) — 与 GrantManager 集成
# ──────────────────────────────────────────────────────────────────────────


class AttunementService:
    """同调服务 — 同调时授予物品效果，解除同调时撤销所有关联 Grant。"""

    def __init__(self, grant_manager=None) -> None:
        self._grant_manager = grant_manager

    def attune_with_effects(
        self,
        entity_id: str,
        current_attuned: list[str],
        item_name: str,
        item_effects: dict | None = None,
        *,
        item_requires: dict | None = None,
        char_class: str = "",
        char_level: int = 1,
        char_abilities: dict | None = None,
    ) -> dict:
        """与物品同调并授予效果。

        规则: R-ITM-020/021/022
        返回: {"success": bool, "reason": str|None, "new_attuned": list, "grants": list}
        """
        # 1. 校验同调合法性
        check = can_attune(
            current_attuned, item_name,
            item_requires=item_requires,
            char_class=char_class,
            char_level=char_level,
            char_abilities=char_abilities,
        )
        if not check["can_attune"]:
            return {"success": False, "reason": check["reason"], "new_attuned": current_attuned, "grants": []}

        # 2. 执行同调
        new_attuned = attune(current_attuned, item_name)

        # 3. 授予物品效果
        granted = []
        if self._grant_manager and item_effects:
            for effect_type, effect_data in item_effects.items():
                grant_id = f"attune_{item_name}_{effect_type}"
                from ..rules.grant import Grant
                g = Grant(
                    grant_id=grant_id,
                    source_feature_id=f"item.{item_name}",
                    grant_type=effect_type,
                    target=effect_data.get("target", ""),
                    value=effect_data.get("value"),
                )
                self._grant_manager.add_grant(entity_id, g)
                granted.append(grant_id)

        return {"success": True, "reason": None, "new_attuned": new_attuned, "grants": granted}

    def end_attunement_with_effects(
        self,
        entity_id: str,
        current_attuned: list[str],
        item_name: str,
    ) -> dict:
        """结束同调并撤销所有关联 Grant。

        规则: R-ITM-023
        返回: {"success": bool, "new_attuned": list, "removed_grants": int}
        """
        new_attuned = end_attunement(current_attuned, item_name)

        # 撤销所有来自该物品的授予
        removed = 0
        if self._grant_manager:
            removed = self._grant_manager.remove_by_source(entity_id, f"item.{item_name}")

        return {"success": True, "new_attuned": new_attuned, "removed_grants": removed}


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 基本调谐
    assert can_attune([], "火焰剑")["can_attune"] is True
    attuned = attune([], "火焰剑")
    assert attuned == ["火焰剑"]

    # 上限3件
    full = ["A", "B", "C"]
    assert can_attune(full, "D")["can_attune"] is False
    assert "上限" in can_attune(full, "D")["reason"]

    # 已调谐
    assert can_attune(["X"], "X")["can_attune"] is False

    # 前置条件：职业
    r = can_attune([], "圣剑", item_requires={"class": ["圣武士"]},
                   char_class="法师")
    assert r["can_attune"] is False and "职业" in r["reason"]
    r = can_attune([], "圣剑", item_requires={"class": ["圣武士"]},
                   char_class="圣武士")
    assert r["can_attune"] is True

    # 前置条件：等级
    r = can_attune([], "X", item_requires={"level": 5}, char_level=3)
    assert r["can_attune"] is False

    # 结束调谐
    assert end_attunement(["A", "B"], "A") == ["B"]
    assert end_attunement(["A"], "X") == ["A"]  # 不存在的物品无影响

    print("[attunement] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
