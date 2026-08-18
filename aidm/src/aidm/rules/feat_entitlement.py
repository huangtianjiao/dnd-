"""FeatEntitlementService — 专长/属性提升（ASI）资格的唯一判定（方案 §8.2）。

职责:
  - 替代全局 FEAT_LEVELS={4,8,12,16,19} 作为唯一 feat opportunity 判断；
  - ASI/专长节点由「角色总等级 + 各职业职业等级」联合生成 entitlement：
      * 标准节点 4/8/12/16（所有职业，按总等级）
      * 传奇恩惠 19（按总等级）
      * 职业额外节点按职业等级（Fighter 6/14；Rogue 10——2024 PHB）
  - Feat 路由/升级流程只消费 entitlement，不再自行拼等级集合。

规则依据:
  PHB 2024 第五章「专长」+ 各职业特性表（战士 6/14 额外 ASI；游荡者 10 级额外 ASI）
  改造方案 §8.2 FeatEntitlementService
"""

from __future__ import annotations

# 标准 ASI/专长节点（所有职业，按总等级判定）
STANDARD_ASI_LEVELS: frozenset[int] = frozenset({4, 8, 12, 16})
# 传奇恩惠等级（PHB 2024 第四章）
EPIC_BOON_LEVEL: int = 19

# 职业额外 ASI 节点（按对应职业的职业等级判定）
# 战士: 2024 在 6 级与 14 级各获一次额外 ASI
# 游荡者: 2024 在 10 级获一次额外 ASI
CLASS_EXTRA_ASI_LEVELS: dict[str, tuple[int, ...]] = {
    "fighter": (6, 14),
    "rogue": (10,),
}

# 中文职业名 → 内部 key（与 CLASS_NAME_MAP 同源，避免循环导入）
_CLASS_ZH_EN: dict[str, str] = {
    "野蛮人": "barbarian", "吟游诗人": "bard", "牧师": "cleric",
    "德鲁伊": "druid", "战士": "fighter", "武僧": "monk",
    "圣武士": "paladin", "游侠": "ranger", "游荡者": "rogue",
    "术士": "sorcerer", "魔契师": "warlock", "法师": "wizard",
}


def class_key(name_or_key: str) -> str:
    """中文/英文职业名 → 内部英文 key（未知原样返回）。"""
    return _CLASS_ZH_EN.get(name_or_key, name_or_key)


def class_extra_asi_levels(class_level: int, class_key_or_name: str) -> list[int]:
    """某职业在给定职业等级下已解锁的额外 ASI 节点（按职业等级判定）。"""
    key = class_key(class_key_or_name)
    return [lv for lv in CLASS_EXTRA_ASI_LEVELS.get(key, ()) if class_level >= lv]


def entitled_asi_levels(class_levels: dict[str, int],
                        total_level: int | None = None) -> set[int]:
    """计算角色当前已获得的全部 ASI/专长 entitlement 节点。

    Args:
        class_levels: {职业(key/中文): 该职业等级}——多职业时逐职业判定额外节点
        total_level: 角色总等级；缺省时取 class_levels 总和

    Returns:
        已满足的节点等级集合（标准节点 + 传奇恩惠 + 职业额外节点）。
    """
    if total_level is None:
        total_level = sum(int(v) for v in class_levels.values())
    nodes: set[int] = set()
    for lv in STANDARD_ASI_LEVELS:
        if total_level >= lv:
            nodes.add(lv)
    if total_level >= EPIC_BOON_LEVEL:
        nodes.add(EPIC_BOON_LEVEL)
    for name, lv in class_levels.items():
        nodes.update(class_extra_asi_levels(int(lv), name))
    return nodes


def is_entitled_at(level: int, class_levels: dict[str, int],
                   total_level: int | None = None) -> bool:
    """该等级是否构成当前角色的 ASI/专长 entitlement（创建/升级判定用）。"""
    return level in entitled_asi_levels(class_levels, total_level)


def pending_asi_choice(total_level: int, class_levels: dict[str, int]) -> dict | None:
    """角色升级后是否有未解决的 ASI/专长选择（供 pending choices 消费）。

    Returns:
        {choice_id, levels}；无未决 → None
    """
    nodes = entitled_asi_levels(class_levels, total_level)
    if not nodes:
        return None
    return {"choice_id": "choice.asi_or_feat", "levels": sorted(nodes)}
