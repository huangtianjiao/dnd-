"""魔法物品数据库 — DMG 2024 + DMG 2014 全部宝藏。

规则依据:
  - 城主指南2024/7.宝藏/魔法物品详述/ (348件)
  - 城主指南/宝藏/魔法物品/ (115件 DMG 2014)

本模块提供:
  - Rarity 枚举: COMMON / UNCOMMON / RARE / VERY_RARE / LEGENDARY / ARTIFACT
  - ItemType 枚举: WEAPON / ARMOR / WONDROUS_ITEM / RING / SCROLL / POTION / STAFF / ROD / WAND
  - MagicItem dataclass: 完整物品数据模型
  - MAGIC_ITEMS 字典: 463件魔法物品 (去重后)
  - 查询函数: get / list / by_rarity / by_type / random / search
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from aidm.data._magic_items_data import _MAGIC_ITEMS_LIST


# ──────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────

class Rarity(Enum):
    """魔法物品稀有度。

    出处: 城主指南2024/7.宝藏/魔法物品/魔法物品的稀有度.htm
    价格表: 普通100gp / 非普通400gp / 珍稀4000gp / 极珍稀40000gp / 传说200000gp / 神器无价之宝
    """
    COMMON = "普通"
    UNCOMMON = "非普通"
    RARE = "珍稀"
    VERY_RARE = "极珍稀"
    LEGENDARY = "传说"
    ARTIFACT = "神器"

    @property
    def base_price_gp(self) -> int:
        return {
            Rarity.COMMON: 100,
            Rarity.UNCOMMON: 400,
            Rarity.RARE: 4000,
            Rarity.VERY_RARE: 40000,
            Rarity.LEGENDARY: 200000,
            Rarity.ARTIFACT: 0,
        }[self]

    @property
    def sort_order(self) -> int:
        return {
            Rarity.COMMON: 0,
            Rarity.UNCOMMON: 1,
            Rarity.RARE: 2,
            Rarity.VERY_RARE: 3,
            Rarity.LEGENDARY: 4,
            Rarity.ARTIFACT: 5,
        }[self]

    @classmethod
    def from_cn(cls, cn: str) -> "Rarity":
        """从中文稀有度名称创建枚举。"""
        for r in cls:
            if r.value == cn:
                return r
        return cls.COMMON


class ItemType(Enum):
    """魔法物品类别（9大类）。

    出处: 城主指南2024/7.宝藏/魔法物品/魔法物品的类别.htm
    """
    WEAPON = "武器"
    ARMOR = "护甲"
    WONDROUS_ITEM = "奇物"
    RING = "戒指"
    SCROLL = "卷轴"
    POTION = "药水"
    STAFF = "法杖"
    ROD = "权杖"
    WAND = "魔杖"

    @classmethod
    def from_key(cls, key: str) -> "ItemType":
        """从英文键名创建枚举。"""
        mapping = {
            "WEAPON": cls.WEAPON, "ARMOR": cls.ARMOR,
            "WONDROUS": cls.WONDROUS_ITEM, "WONDROUS_WORN": cls.WONDROUS_ITEM,
            "WONDROUS_ORNAMENT": cls.WONDROUS_ITEM,
            "RING": cls.RING, "SCROLL": cls.SCROLL,
            "POTION": cls.POTION, "STAFF": cls.STAFF,
            "ROD": cls.ROD, "WAND": cls.WAND,
        }
        return mapping.get(key, cls.WONDROUS_ITEM)


# ──────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class MagicItem:
    """单个魔法物品的数据条目。"""
    name: str
    name_en: str
    rarity: Rarity
    item_type: ItemType
    attunement: bool = False
    attunement_req: str = ""
    cursed: bool = False
    description: str = ""
    properties: dict = field(default_factory=dict)
    source: str = ""

    @property
    def price_gp(self) -> int:
        if "price_override" in self.properties:
            return self.properties["price_override"]
        base = self.rarity.base_price_gp
        consumable = self.item_type in (ItemType.POTION, ItemType.SCROLL) or \
                     self.properties.get("consumable", False)
        if consumable:
            base = base // 2
        base_item_price = self.properties.get("base_item_price_gp", 0)
        return base + base_item_price

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "name_en": self.name_en,
            "rarity": self.rarity.value,
            "rarity_key": self.rarity.name,
            "item_type": self.item_type.value,
            "item_type_key": self.item_type.name,
            "attunement": self.attunement,
            "attunement_req": self.attunement_req,
            "cursed": self.cursed,
            "description": self.description,
            "properties": self.properties,
            "price_gp": self.price_gp,
            "source": self.source,
        }


# ──────────────────────────────────────────────────────────────────────────
# 从自动生成的数据构建数据列表
# ──────────────────────────────────────────────────────────────────────────

def _build_from_raw(raw_items: list[dict]) -> list[MagicItem]:
    """将 extract_magic_items.py 输出的原始字典转换为 MagicItem 列表。"""
    result = []
    for raw in raw_items:
        # 映射类别
        item_type = ItemType.from_key(raw["type"])

        # 映射稀有度
        rarity = Rarity.from_cn(raw.get("rarity_cn", "普通"))

        # 构建物品
        item = MagicItem(
            name=raw["name"],
            name_en=raw.get("en_name", ""),
            rarity=rarity,
            item_type=item_type,
            attunement=raw.get("attunement", False),
            attunement_req=raw.get("attunement_class", ""),
            cursed="诅咒" in raw.get("description", ""),
            description=raw.get("description", ""),
            source=raw.get("source", ""),
        )
        result.append(item)
    return result


_MAGIC_ITEMS_LIST: list[MagicItem] = _build_from_raw(_MAGIC_ITEMS_LIST)

# 构建名称索引字典
MAGIC_ITEMS: dict[str, MagicItem] = {item.name: item for item in _MAGIC_ITEMS_LIST}


# ──────────────────────────────────────────────────────────────────────────
# 查询函数
# ──────────────────────────────────────────────────────────────────────────

def get_magic_item(name: str) -> Optional[MagicItem]:
    """按名称查询魔法物品（精确匹配）。"""
    return MAGIC_ITEMS.get(name)


def search_magic_items(query: str) -> list[MagicItem]:
    """按名称模糊搜索魔法物品。

    Args:
        query: 搜索关键词（匹配中文名和英文名）

    Returns:
        匹配的物品列表，按稀有度排序
    """
    q = query.lower()
    result = []
    for item in _MAGIC_ITEMS_LIST:
        if q in item.name or q in item.name_en.lower():
            result.append(item)
    result.sort(key=lambda x: (x.rarity.sort_order, x.name))
    return result


def list_magic_items(rarity: Optional[Rarity] = None,
                     item_type: Optional[ItemType] = None,
                     cursed_only: bool = False,
                     attunement_only: bool = False) -> list[MagicItem]:
    """列出魔法物品，支持多条件筛选。

    Args:
        rarity: 按稀有度筛选
        item_type: 按类别筛选
        cursed_only: 仅返回诅咒物品
        attunement_only: 仅返回需同调物品

    Returns:
        匹配的物品列表，按稀有度升序排列
    """
    result = []
    for item in _MAGIC_ITEMS_LIST:
        if rarity is not None and item.rarity != rarity:
            continue
        if item_type is not None and item.item_type != item_type:
            continue
        if cursed_only and not item.cursed:
            continue
        if attunement_only and not item.attunement:
            continue
        result.append(item)
    result.sort(key=lambda x: (x.rarity.sort_order, x.name))
    return result


def items_by_rarity(rarity: Rarity) -> list[MagicItem]:
    """获取指定稀有度的所有物品。"""
    return list_magic_items(rarity=rarity)


def items_by_type(item_type: ItemType) -> list[MagicItem]:
    """获取指定类别的所有物品。"""
    return list_magic_items(item_type=item_type)


def item_count() -> int:
    """返回物品总数。"""
    return len(_MAGIC_ITEMS_LIST)


def random_magic_items(count: int = 1,
                       max_rarity: Optional[Rarity] = None,
                       min_rarity: Optional[Rarity] = None,
                       seed: Optional[int] = None) -> list[MagicItem]:
    """随机抽取N个魔法物品（不放回）。"""
    import random
    rng = random.Random(seed) if seed is not None else random.Random()

    pool = []
    for item in _MAGIC_ITEMS_LIST:
        if max_rarity is not None and item.rarity.sort_order > max_rarity.sort_order:
            continue
        if min_rarity is not None and item.rarity.sort_order < min_rarity.sort_order:
            continue
        pool.append(item)

    if not pool:
        return []

    n = min(count, len(pool))
    return rng.sample(pool, n)


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    """魔法物品数据库自检。"""
    # 1. 数据完整性
    n = len(_MAGIC_ITEMS_LIST)
    assert n >= 400, f"物品数不足: {n}"
    assert len(MAGIC_ITEMS) == n, "索引字典大小不匹配"
    print(f"[magic_items] 物品总数: {n}")

    # 2. 名称唯一性
    names = [item.name for item in _MAGIC_ITEMS_LIST]
    assert len(names) == len(set(names)), f"存在{len(names) - len(set(names))}个重复名称"

    # 3. 必填字段检查
    issues = []
    for item in _MAGIC_ITEMS_LIST:
        if not item.name:
            issues.append("缺少名称")
        if not item.description or len(item.description) < 5:
            issues.append(f"{item.name}: 描述过短")
        if not isinstance(item.rarity, Rarity):
            issues.append(f"{item.name}: 稀有度类型错误")
        if not isinstance(item.item_type, ItemType):
            issues.append(f"{item.name}: 类别类型错误")
    assert not issues, f"数据问题: {issues[:5]}"

    # 4. 类别和稀有度覆盖
    covered_types = set(item.item_type for item in _MAGIC_ITEMS_LIST)
    missing_t = set(ItemType) - covered_types
    assert not missing_t, f"缺少类别: {[t.value for t in missing_t]}"

    covered_rarities = set(item.rarity for item in _MAGIC_ITEMS_LIST)
    missing_r = {Rarity.COMMON, Rarity.UNCOMMON, Rarity.RARE,
                 Rarity.VERY_RARE, Rarity.LEGENDARY} - covered_rarities
    assert not missing_r, f"缺少稀有度: {[r.value for r in missing_r]}"

    # 5. 查询函数
    # 搜索测试
    dragon_items = search_magic_items("龙")
    assert len(dragon_items) > 0, "应能搜到龙相关物品"

    # 稀有度筛选
    legendary = items_by_rarity(Rarity.LEGENDARY)
    assert len(legendary) >= 5, f"传说物品不足: {len(legendary)}"

    # 类别筛选
    weapons = items_by_type(ItemType.WEAPON)
    assert len(weapons) >= 30, f"武器物品不足: {len(weapons)}"

    # 随机抽取
    random_items = random_magic_items(count=3, seed=42)
    assert len(random_items) == 3
    assert len(set(item.name for item in random_items)) == 3

    # 可复现性
    random_items2 = random_magic_items(count=3, seed=42)
    assert [item.name for item in random_items] == [item.name for item in random_items2]

    # 6. 价格
    potions = items_by_type(ItemType.POTION)
    common_potions = [p for p in potions if p.rarity == Rarity.COMMON]
    if common_potions:
        assert common_potions[0].price_gp == 50, \
            f"普通药水价格应为50gp，实际{common_potions[0].price_gp}"

    print(f"[magic_items] 自检通过 ✓ "
          f"(类别{len(covered_types)}/9, "
          f"传说{len(legendary)}, 神器{len(items_by_rarity(Rarity.ARTIFACT))})")


if __name__ == "__main__":
    _self_test()
