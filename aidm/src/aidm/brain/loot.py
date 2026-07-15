"""战利品系统 — DMG 第七章 宝藏。

规则依据: 城主指南2024/7.宝藏/
  - 宝藏.htm              战利品生成总论
  - 钱币.htm / 宝石.htm / 艺术品.htm / 贸易金属条.htm  金币与贵重物
  - 随机魔法物品/         5张随机生成表（器具/圣物/奥秘/武备）
  - 魔法物品详述/         按稀有度分类的详细物品列表

本模块提供:
  - generate_loot():     按怪物CR生成战利品池
  - distribute_loot():   分配战利品（需求优先/轮流拾取/点数分配/DM指定）
  - distribute_gold():   金币分配（平均/按贡献）
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass, field
from typing import Optional

from ..data.magic_items import (
    MagicItem, Rarity, ItemType,
    MAGIC_ITEMS, get_magic_item, random_magic_items,
)


# ──────────────────────────────────────────────────────────────────────────
# CR → 战利品等级映射
# 规则依据: 城主指南2024/7.宝藏/宝藏.htm（按挑战等级分级的宝藏表）
# ──────────────────────────────────────────────────────────────────────────

def cr_to_loot_tier(cr: float) -> str:
    """将怪物挑战等级(CR)映射到战利品等级。

    规则: 城主指南2024/7.宝藏/宝藏.htm
      CR 0-4   → 低级（普通/非普通为主）
      CR 5-10  → 中级（非普通/珍稀为主）
      CR 11-16 → 高级（珍稀/极珍稀为主）
      CR 17+   → 顶级（极珍稀/传说为主）

    Args:
        cr: 挑战等级（支持小数如0.5）

    Returns:
        战利品等级字符串: "low" / "mid" / "high" / "top"
    """
    if cr < 5:
        return "low"
    elif cr < 11:
        return "mid"
    elif cr < 17:
        return "high"
    else:
        return "top"


# CR → 金币范围映射（GP）
# 规则依据: 城主指南2024/7.宝藏/钱币.htm 与 宝藏.htm 中的金币掷骰表
CR_GOLD_RANGES: dict[str, tuple[int, int]] = {
    "low":  (50, 200),     # CR 0-4
    "mid":  (200, 800),    # CR 5-10
    "high": (800, 3000),   # CR 11-16
    "top":  (3000, 10000), # CR 17+
}

# CR → 魔法物品数量范围
# 规则依据: 城主指南2024/7.宝藏/宝藏.htm
CR_MAGIC_ITEM_COUNTS: dict[str, tuple[int, int]] = {
    "low":  (0, 1),
    "mid":  (1, 2),
    "high": (1, 3),
    "top":  (2, 4),
}

# CR → 最大稀有度
# 规则依据: 城主指南2024/7.宝藏/宝藏.htm
CR_MAX_RARITY: dict[str, Rarity] = {
    "low":  Rarity.UNCOMMON,
    "mid":  Rarity.RARE,
    "high": Rarity.VERY_RARE,
    "top":  Rarity.LEGENDARY,
}


# ──────────────────────────────────────────────────────────────────────────
# 战利品数据结构
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class LootPool:
    """一个战利品池：金币 + 魔法物品 + 杂物。

    规则依据: 城主指南2024/7.宝藏/宝藏.htm
    """
    gold: int = 0                           # 金币总量(GP)
    magic_items: list[MagicItem] = field(default_factory=list)
    gems: list[dict] = field(default_factory=list)       # 宝石 [{name, value_gp}]
    art_objects: list[dict] = field(default_factory=list) # 艺术品 [{name, value_gp}]
    source_cr: float = 0.0                  # 生成时的CR
    source_tier: str = ""                   # 生成时的战利品等级

    @property
    def total_value_gp(self) -> int:
        """战利品总价值（GP）。"""
        item_value = sum(item.price_gp for item in self.magic_items)
        gem_value = sum(g["value_gp"] for g in self.gems)
        art_value = sum(a["value_gp"] for a in self.art_objects)
        return self.gold + item_value + gem_value + art_value

    def to_dict(self) -> dict:
        """序列化为可JSON化的字典。"""
        return {
            "gold": self.gold,
            "magic_items": [item.to_dict() for item in self.magic_items],
            "gems": self.gems,
            "art_objects": self.art_objects,
            "total_value_gp": self.total_value_gp,
            "source_cr": self.source_cr,
            "source_tier": self.source_tier,
        }


# ──────────────────────────────────────────────────────────────────────────
# 战利品生成
# ──────────────────────────────────────────────────────────────────────────

# 宝石模板（按价值分级）
# 规则依据: 城主指南2024/7.宝藏/宝石.htm
GEM_TEMPLATES: list[dict] = [
    {"name": "红玉", "value_gp": 10},
    {"name": "蓝玉", "value_gp": 10},
    {"name": "黑珍珠", "value_gp": 50},
    {"name": "星彩蓝宝石", "value_gp": 100},
    {"name": "钻石", "value_gp": 500},
]

# 艺术品模板
# 规则依据: 城主指南2024/7.宝藏/艺术品.htm
ART_TEMPLATES: list[dict] = [
    {"name": "银质酒杯", "value_gp": 25},
    {"name": "金质雕像", "value_gp": 100},
    {"name": "精美术画", "value_gp": 250},
    {"name": "象牙梳", "value_gp": 50},
]


def generate_loot(cr: float,
                  count_enemies: int = 1,
                  include_magic_items: bool = True,
                  seed: Optional[int] = None) -> LootPool:
    """按怪物CR生成战利品池。

    规则: 城主指南2024/7.宝藏/宝藏.htm
      - CR越高，金币越多、魔法物品越多越珍稀
      - 多个敌人时金币按比例增加

    Args:
        cr: 怪物挑战等级
        count_enemies: 敌人数量（影响金币总量）
        include_magic_items: 是否包含魔法物品
        seed: 随机种子（测试用）

    Returns:
        LootPool 战利品池
    """
    rng = random.Random(seed) if seed is not None else random.Random()

    tier = cr_to_loot_tier(cr)
    pool = LootPool(source_cr=cr, source_tier=tier)

    # 1. 金币
    gold_min, gold_max = CR_GOLD_RANGES[tier]
    base_gold = rng.randint(gold_min, gold_max)
    # 多敌人加成：每个额外敌人+20%金币
    enemy_multiplier = 1.0 + 0.2 * max(0, count_enemies - 1)
    pool.gold = int(base_gold * enemy_multiplier)

    # 2. 魔法物品
    if include_magic_items:
        mi_min, mi_max = CR_MAGIC_ITEM_COUNTS[tier]
        mi_count = rng.randint(mi_min, mi_max)
        max_rarity = CR_MAX_RARITY[tier]
        pool.magic_items = random_magic_items(
            count=mi_count, max_rarity=max_rarity, seed=rng.randint(0, 99999)
        )

    # 3. 宝石（50%概率）
    if rng.random() < 0.5:
        gem_count = rng.randint(1, 3)
        # 根据tier选择宝石价值层级
        if tier == "low":
            gem_pool = [g for g in GEM_TEMPLATES if g["value_gp"] <= 10]
        elif tier == "mid":
            gem_pool = [g for g in GEM_TEMPLATES if g["value_gp"] <= 50]
        elif tier == "high":
            gem_pool = [g for g in GEM_TEMPLATES if g["value_gp"] <= 100]
        else:
            gem_pool = GEM_TEMPLATES

        if gem_pool:
            for _ in range(gem_count):
                template = rng.choice(gem_pool)
                pool.gems.append({
                    "name": template["name"],
                    "value_gp": template["value_gp"],
                })

    # 4. 艺术品（30%概率）
    if rng.random() < 0.3:
        art_count = rng.randint(1, 2)
        for _ in range(art_count):
            template = rng.choice(ART_TEMPLATES)
            pool.art_objects.append({
                "name": template["name"],
                "value_gp": template["value_gp"],
            })

    return pool


# ──────────────────────────────────────────────────────────────────────────
# 战利品分配
# ──────────────────────────────────────────────────────────────────────────

# 分配方式枚举
DISTRIBUTION_METHODS = {
    "need_priority": "需求优先",
    "round_robin": "轮流拾取",
    "point_bid": "点数分配",
    "dm_assign": "DM指定",
}


@dataclass
class LootDistribution:
    """战利品分配结果。

    规则依据: 城主指南2024/7.宝藏/宝藏主题.htm（宝藏分配主题）
    """
    method: str                                   # 分配方式key
    assignments: dict[str, list[str]] = field(default_factory=dict)  # {玩家名: [物品名]}
    gold_distribution: dict[str, int] = field(default_factory=dict)  # {玩家名: 金币}
    unassigned_items: list[str] = field(default_factory=list)        # 未分配的物品名
    remainder_gold: int = 0                       # 无法均分的余数金币

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "method_name": DISTRIBUTION_METHODS.get(self.method, self.method),
            "assignments": self.assignments,
            "gold_distribution": self.gold_distribution,
            "unassigned_items": self.unassigned_items,
            "remainder_gold": self.remainder_gold,
        }


def distribute_loot(pool: LootPool,
                    players: list[str],
                    method: str = "need_priority",
                    needs: Optional[dict[str, list[str]]] = None,
                    dm_assignments: Optional[dict[str, list[str]]] = None,
                    seed: Optional[int] = None) -> LootDistribution:
    """分配战利品（魔法物品部分）。

    规则依据: 城主指南2024/7.宝藏/宝藏主题.htm

    Args:
        pool: 战利品池
        players: 参与分配的玩家名列表
        method: 分配方式 ("need_priority"/"round_robin"/"point_bid"/"dm_assign")
        needs: 需求优先模式下的需求表 {玩家名: [物品名]}
        dm_assignments: DM指定模式下的分配表 {玩家名: [物品名]}
        seed: 随机种子

    Returns:
        LootDistribution 分配结果
    """
    rng = random.Random(seed) if seed is not None else random.Random()
    result = LootDistribution(method=method)

    if not players:
        result.unassigned_items = [item.name for item in pool.magic_items]
        return result

    item_names = [item.name for item in pool.magic_items]

    if method == "need_priority":
        # 需求优先：每个物品分配给声明需求的第一个玩家
        needs = needs or {}
        assigned_set = set()
        for item_name in item_names:
            assigned = False
            for player in players:
                player_needs = needs.get(player, [])
                if item_name in player_needs and item_name not in assigned_set:
                    result.assignments.setdefault(player, []).append(item_name)
                    assigned_set.add(item_name)
                    assigned = True
                    break
            if not assigned:
                result.unassigned_items.append(item_name)

    elif method == "round_robin":
        # 轮流拾取：按玩家顺序依次分配
        player_order = list(players)
        rng.shuffle(player_order)
        for i, item_name in enumerate(item_names):
            player = player_order[i % len(player_order)]
            result.assignments.setdefault(player, []).append(item_name)

    elif method == "point_bid":
        # 点数分配：每个玩家随机获得点数，最高点数的玩家优先选择
        # 简化实现：按随机点数排序分配
        bids = {p: rng.randint(1, 100) for p in players}
        sorted_players = sorted(players, key=lambda p: bids[p], reverse=True)
        for i, item_name in enumerate(item_names):
            player = sorted_players[i % len(sorted_players)]
            result.assignments.setdefault(player, []).append(item_name)

    elif method == "dm_assign":
        # DM指定：使用dm_assignments参数
        dm_assignments = dm_assignments or {}
        assigned_set = set()
        for player, assigned_items in dm_assignments.items():
            for item_name in assigned_items:
                if item_name in item_names and item_name not in assigned_set:
                    result.assignments.setdefault(player, []).append(item_name)
                    assigned_set.add(item_name)
        # 未被DM指定的物品放入未分配
        for item_name in item_names:
            if item_name not in assigned_set:
                result.unassigned_items.append(item_name)

    else:
        raise ValueError(f"未知分配方式: {method}，可选: {list(DISTRIBUTION_METHODS)}")

    return result


def distribute_gold(total_gold: int,
                    players: list[str],
                    method: str = "equal",
                    contributions: Optional[dict[str, float]] = None) -> dict[str, int]:
    """分配金币。

    规则依据: 城主指南2024/7.宝藏/钱币.htm

    Args:
        total_gold: 金币总量
        players: 参与分配的玩家名列表
        method: 分配方式 ("equal"=平均分配 / "contribution"=按贡献分配)
        contributions: 按贡献分配模式下的贡献表 {玩家名: 贡献值}

    Returns:
        {玩家名: 金币} 字典
    """
    if not players or total_gold <= 0:
        return {p: 0 for p in players}

    if method == "equal":
        # 平均分配，余数给第一个玩家
        per_player = total_gold // len(players)
        remainder = total_gold - per_player * len(players)
        result = {p: per_player for p in players}
        result[players[0]] += remainder
        return result

    elif method == "contribution":
        # 按贡献比例分配
        contributions = contributions or {}
        total_contribution = sum(contributions.get(p, 0) for p in players)
        if total_contribution <= 0:
            # 无贡献数据，退回平均分配
            return distribute_gold(total_gold, players, method="equal")

        result = {}
        allocated = 0
        for i, player in enumerate(players):
            ratio = contributions.get(player, 0) / total_contribution
            if i == len(players) - 1:
                # 最后一个玩家拿走所有余数
                share = total_gold - allocated
            else:
                share = int(total_gold * ratio)
                allocated += share
            result[player] = share
        return result

    else:
        raise ValueError(f"未知金币分配方式: {method}，可选: 'equal' / 'contribution'")


# ──────────────────────────────────────────────────────────────────────────
# 同调管理
# ──────────────────────────────────────────────────────────────────────────

def attune_magic_item(character_id: int,
                      item_name: str,
                      db_path: str = "sqlite:///D:/game/dnd/aidm/data/saves/save.db") -> dict:
    """为角色同调一件魔法物品。

    规则: 玩家手册 同调Attunement
      - 物品必须需要同调（attunement=True）
      - 一个生物最多同时与3件魔法物品同调
      - 同调需要一个短休

    Args:
        character_id: 角色ID
        item_name: 魔法物品名称
        db_path: 数据库路径

    Returns:
        {"success": bool, "message": str, "attuned_items": list}
    """
    from ..stats import store

    # 1. 验证物品存在且需要同调
    item = get_magic_item(item_name)
    if item is None:
        return {"success": False, "message": f"未知魔法物品: {item_name}",
                "attuned_items": []}
    if not item.attunement:
        return {"success": False,
                "message": f"{item_name}不需要同调，可直接使用",
                "attuned_items": []}

    # 2. 加载角色
    ch = store.get_character(character_id, db_path)
    if ch is None:
        return {"success": False, "message": f"角色不存在: {character_id}",
                "attuned_items": []}

    # 3. 检查同调上限
    current = ch.attuned_items
    if len(current) >= ch.MAX_ATTUNED_ITEMS:
        return {"success": False,
                "message": f"已达同调上限({ch.MAX_ATTUNED_ITEMS}件)，需先解除一件",
                "attuned_items": current}

    # 4. 检查是否已同调
    if item_name in current:
        return {"success": False, "message": f"已同调该物品: {item_name}",
                "attuned_items": current}

    # 5. 执行同调
    current.append(item_name)
    ch.set_attuned_items(current)
    store.save_character(ch, db_path)

    return {"success": True,
            "message": f"成功与{item_name}同调",
            "attuned_items": current}


def break_attunement(character_id: int,
                     item_name: str,
                     db_path: str = "sqlite:///D:/game/dnd/aidm/data/saves/save.db") -> dict:
    """解除角色的同调物品。

    规则: 玩家手册 同调Attunement — 解除同调需要一个短休

    Args:
        character_id: 角色ID
        item_name: 要解除同调的物品名称
        db_path: 数据库路径

    Returns:
        {"success": bool, "message": str, "attuned_items": list}
    """
    from ..stats import store

    ch = store.get_character(character_id, db_path)
    if ch is None:
        return {"success": False, "message": f"角色不存在: {character_id}",
                "attuned_items": []}

    current = ch.attuned_items
    if item_name not in current:
        return {"success": False, "message": f"未同调该物品: {item_name}",
                "attuned_items": current}

    current.remove(item_name)
    ch.set_attuned_items(current)
    store.save_character(ch, db_path)

    return {"success": True,
            "message": f"已解除与{item_name}的同调",
            "attuned_items": current}


def identify_magic_item(character_id: int,
                        item_name: str,
                        method: str = "short_rest",
                        db_path: str = "sqlite:///D:/game/dnd/aidm/data/saves/save.db") -> dict:
    """鉴定魔法物品。

    规则依据: 城主指南2024/7.宝藏/魔法物品详述/ — 鉴定魔法物品
      - 鉴定术(Identify): 1个长休或短休内可鉴定（此处简化为瞬间）
      - 短休集中接触: 在短休期间集中接触该物品，可鉴定其属性
      - 诅咒物品: 鉴定时不一定揭示诅咒效应

    Args:
        character_id: 角色ID
        item_name: 要鉴定的魔法物品名称
        method: 鉴定方式 ("identify_spell"=鉴定术 / "short_rest"=短休接触)
        db_path: 数据库路径

    Returns:
        {
            "success": bool,
            "method": str,
            "item": dict (MagicItem.to_dict),
            "reveals_curse": bool,  # 是否揭示诅咒
            "message": str
        }
    """
    from ..stats import store

    # 1. 验证物品存在
    item = get_magic_item(item_name)
    if item is None:
        return {"success": False, "method": method, "item": None,
                "reveals_curse": False, "message": f"未知魔法物品: {item_name}"}

    # 2. 加载角色，检查物品是否在物品栏中
    ch = store.get_character(character_id, db_path)
    if ch is None:
        return {"success": False, "method": method, "item": None,
                "reveals_curse": False, "message": f"角色不存在: {character_id}"}

    inv = ch.inventory
    if item_name not in inv:
        return {"success": False, "method": method, "item": None,
                "reveals_curse": False,
                "message": f"{item_name} 不在角色物品栏中，无法鉴定"}

    # 3. 校验鉴定方式
    valid_methods = {"identify_spell", "short_rest"}
    if method not in valid_methods:
        return {"success": False, "method": method, "item": None,
                "reveals_curse": False,
                "message": f"未知鉴定方式: {method}，可选: {sorted(valid_methods)}"}

    # 4. 鉴定术揭示诅咒；短休接触不揭示诅咒（DMG规则）
    reveals_curse = (method == "identify_spell") and item.cursed

    method_desc = {
        "identify_spell": "鉴定术",
        "short_rest": "短休集中接触",
    }[method]

    curse_note = ""
    if item.cursed and reveals_curse:
        curse_note = " 鉴定揭示了该物品的诅咒效应。"
    elif item.cursed and not reveals_curse:
        curse_note = " 该物品带有诅咒，但当前鉴定方式未能揭示。"

    return {
        "success": True,
        "method": method,
        "method_desc": method_desc,
        "item": item.to_dict(),
        "reveals_curse": reveals_curse,
        "message": f"成功鉴定{item_name}（{method_desc}）。{curse_note}".strip(),
    }


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    """战利品系统自检。"""
    import tempfile

    # ═══ 1. CR映射 ═══
    assert cr_to_loot_tier(0) == "low"
    assert cr_to_loot_tier(0.5) == "low"
    assert cr_to_loot_tier(4) == "low"
    assert cr_to_loot_tier(5) == "mid"
    assert cr_to_loot_tier(10) == "mid"
    assert cr_to_loot_tier(11) == "high"
    assert cr_to_loot_tier(17) == "top"
    print("[loot] CR→tier映射 ✓")

    # ═══ 2. 战利品生成 ═══
    # 低级战利品
    low_pool = generate_loot(cr=2, seed=42)
    assert low_pool.source_tier == "low"
    assert low_pool.gold > 0, "金币应大于0"
    assert low_pool.gold >= 50, f"低级金币应≥50，实际{low_pool.gold}"
    # 低级战利品的魔法物品不应超过非普通
    for item in low_pool.magic_items:
        assert item.rarity.sort_order <= Rarity.UNCOMMON.sort_order, \
            f"低级战利品不应有高于非普通的物品: {item.name}({item.rarity.value})"

    # 顶级战利品应有更多金币
    top_pool = generate_loot(cr=20, seed=42)
    assert top_pool.source_tier == "top"
    assert top_pool.gold >= 3000, f"顶级金币应≥3000，实际{top_pool.gold}"

    # 可复现性
    pool1 = generate_loot(cr=5, seed=100)
    pool2 = generate_loot(cr=5, seed=100)
    assert pool1.gold == pool2.gold, "相同种子应产生相同金币"
    assert len(pool1.magic_items) == len(pool2.magic_items), "相同种子应产生相同物品数"

    # 不含魔法物品
    no_mi_pool = generate_loot(cr=10, include_magic_items=False, seed=42)
    assert len(no_mi_pool.magic_items) == 0, "include_magic_items=False不应有魔法物品"

    # 多敌人加成
    single = generate_loot(cr=5, seed=42)
    multi = generate_loot(cr=5, count_enemies=5, seed=42)
    assert multi.gold > single.gold, "多敌人应增加金币"
    print("[loot] 战利品生成 ✓")

    # ═══ 3. 战利品池属性 ═══
    pool = generate_loot(cr=8, seed=42)
    assert pool.total_value_gp >= pool.gold, "总价值应≥金币"
    assert isinstance(pool.to_dict(), dict)
    assert "gold" in pool.to_dict()
    assert "magic_items" in pool.to_dict()
    print("[loot] 战利品池属性 ✓")

    # ═══ 4. 战利品分配 ═══
    players = ["阿拉贡", "莱戈拉斯", "吉姆利"]

    # 需求优先
    test_pool = LootPool(
        gold=300,
        magic_items=[
            get_magic_item("触月剑"),
            get_magic_item("跳跃戒指"),
            get_magic_item("闪烁甲"),
        ],
    )
    needs = {
        "阿拉贡": ["触月剑"],
        "莱戈拉斯": ["跳跃戒指", "闪烁甲"],
    }
    dist = distribute_loot(test_pool, players, method="need_priority", needs=needs, seed=42)
    assert "触月剑" in dist.assignments.get("阿拉贡", []), "阿拉贡应获得触月剑"
    assert "跳跃戒指" in dist.assignments.get("莱戈拉斯", []), "莱戈拉斯应获得跳跃戒指"

    # 轮流拾取
    dist_rr = distribute_loot(test_pool, players, method="round_robin", seed=42)
    all_assigned = []
    for items in dist_rr.assignments.values():
        all_assigned.extend(items)
    assert len(all_assigned) == 3, f"轮流拾取应分配全部3件物品，实际{len(all_assigned)}"
    assert len(set(all_assigned)) == 3, "不应有重复分配"

    # 点数分配
    dist_pb = distribute_loot(test_pool, players, method="point_bid", seed=42)
    all_assigned_pb = []
    for items in dist_pb.assignments.values():
        all_assigned_pb.extend(items)
    assert len(all_assigned_pb) == 3, "点数分配应分配全部物品"

    # DM指定
    dm_assigns = {"吉姆利": ["触月剑", "闪烁甲"], "莱戈拉斯": ["跳跃戒指"]}
    dist_dm = distribute_loot(test_pool, players, method="dm_assign",
                              dm_assignments=dm_assigns, seed=42)
    assert "触月剑" in dist_dm.assignments.get("吉姆利", [])
    assert "跳跃戒指" in dist_dm.assignments.get("莱戈拉斯", [])

    # 空玩家列表
    dist_empty = distribute_loot(test_pool, [], method="round_robin", seed=42)
    assert len(dist_empty.unassigned_items) == 3, "无玩家时应全部未分配"

    # 序列化
    d = dist.to_dict()
    assert d["method"] == "need_priority"
    assert d["method_name"] == "需求优先"
    print("[loot] 战利品分配 ✓")

    # ═══ 5. 金币分配 ═══
    # 平均分配
    gold_dist = distribute_gold(300, players, method="equal")
    assert sum(gold_dist.values()) == 300, "金币总和应等于总量"
    assert gold_dist["阿拉贡"] == 100, f"300/3=100，实际{gold_dist['阿拉贡']}"

    # 有余数的平均分配
    gold_dist2 = distribute_gold(301, players, method="equal")
    assert sum(gold_dist2.values()) == 301, "金币总和应等于总量"
    assert gold_dist2["阿拉贡"] == 101, "余数应给第一个玩家"

    # 按贡献分配
    contribs = {"阿拉贡": 50, "莱戈拉斯": 30, "吉姆利": 20}
    gold_dist3 = distribute_gold(1000, players, method="contribution", contributions=contribs)
    assert sum(gold_dist3.values()) == 1000, "金币总和应等于总量"
    assert gold_dist3["阿拉贡"] > gold_dist3["吉姆利"], "贡献高的应分更多"

    # 无贡献数据退回平均
    gold_dist4 = distribute_gold(300, players, method="contribution")
    assert gold_dist4["阿拉贡"] == 100, "无贡献数据应退回平均分配"

    # 边界情况
    assert distribute_gold(0, players) == {"阿拉贡": 0, "莱戈拉斯": 0, "吉姆利": 0}
    assert distribute_gold(100, []) == {}
    print("[loot] 金币分配 ✓")

    # ═══ 6. 同调管理 ═══
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = f"sqlite:///{tmp.name}"
    try:
        from ..stats import store, models
        store.get_engine(db)

        # 创建角色
        ch = models.Character(name="测试法师", race="人类", char_class="法师", level=5)
        ch = store.save_character(ch, db)
        cid = ch.id

        # 同调需要同调的物品
        result = attune_magic_item(cid, "跳跃戒指", db)
        assert result["success"], f"同调应成功: {result['message']}"
        assert "跳跃戒指" in result["attuned_items"]

        # 同调不需要同调的物品应失败
        result2 = attune_magic_item(cid, "触月剑", db)
        assert not result2["success"], "触月剑不需要同调，应失败"

        # 同调未知物品应失败
        result3 = attune_magic_item(cid, "不存在的物品", db)
        assert not result3["success"], "未知物品应失败"

        # 再同调两件达到上限
        attune_magic_item(cid, "心灵护盾戒指", db)
        attune_magic_item(cid, "温暖戒指", db)
        ch_reload = store.get_character(cid, db)
        assert len(ch_reload.attuned_items) == 3, "应达到3件同调上限"

        # 第四件应失败（使用需要同调的巫术帽）
        result4 = attune_magic_item(cid, "巫术帽", db)
        assert not result4["success"], "超过上限应失败"
        assert "上限" in result4["message"], f"消息应含'上限': {result4['message']}"

        # 解除同调
        result5 = break_attunement(cid, "跳跃戒指", db)
        assert result5["success"], f"解除同调应成功: {result5['message']}"
        assert "跳跃戒指" not in result5["attuned_items"]
        assert len(result5["attuned_items"]) == 2

        # 解除未同调的物品应失败
        result6 = break_attunement(cid, "跳跃戒指", db)
        assert not result6["success"], "解除未同调物品应失败"

        # 重叠同调同一物品应失败
        attune_magic_item(cid, "善泳戒指", db)
        result7 = attune_magic_item(cid, "善泳戒指", db)
        assert not result7["success"], "重复同调应失败"

        print("[loot] 同调管理 ✓")

        # ═══ 7. 战利品生成→分配→物品栏更新 ═══
        # 规则依据: 城主指南2024/7.宝藏/宝藏.htm
        ch2 = models.Character(name="战利品测试角色", race="人类",
                               char_class="战士", level=3)
        ch2 = store.save_character(ch2, db)
        cid2 = ch2.id

        # 生成战利品池
        loot_pool = generate_loot(cr=5, seed=42)
        assert loot_pool.gold > 0, "战利品金币应大于0"
        assert len(loot_pool.magic_items) >= 1, "应有至少1件魔法物品"

        # 将战利品中的魔法物品加入角色物品栏
        ch2_reload = store.get_character(cid2, db)
        for mi in loot_pool.magic_items:
            ch2_reload.add_to_inventory(mi.name)
        # 金币累加到角色（此处简化：直接记录物品）
        store.save_character(ch2_reload, db)

        # 验证物品栏已更新
        ch2_final = store.get_character(cid2, db)
        inv = ch2_final.inventory
        assert len(inv) == len(loot_pool.magic_items), \
            f"物品栏数量({len(inv)})应等于战利品物品数({len(loot_pool.magic_items)})"
        for mi in loot_pool.magic_items:
            assert mi.name in inv, f"{mi.name} 应在物品栏中"

        # 幂等性：重复添加不应增加
        ch2_final.add_to_inventory(loot_pool.magic_items[0].name)
        assert len(ch2_final.inventory) == len(loot_pool.magic_items), \
            "重复添加同一物品不应增加物品栏数量"

        print("[loot] 战利品→物品栏 ✓")

        # ═══ 8. 鉴定魔法物品 ═══
        # 规则依据: 城主指南2024/7.宝藏/ — 鉴定术或短休接触
        ch3 = models.Character(name="鉴定测试角色", race="人类",
                               char_class="法师", level=3)
        ch3 = store.save_character(ch3, db)
        cid3 = ch3.id

        # 先将物品加入物品栏
        ch3_reload = store.get_character(cid3, db)
        ch3_reload.add_to_inventory("触月剑")
        ch3_reload.add_to_inventory("复仇之剑")  # 诅咒物品
        store.save_character(ch3_reload, db)

        # 短休接触鉴定普通物品
        id_result = identify_magic_item(cid3, "触月剑", method="short_rest", db_path=db)
        assert id_result["success"], f"鉴定应成功: {id_result['message']}"
        assert id_result["item"]["name"] == "触月剑"
        assert id_result["method_desc"] == "短休集中接触"

        # 鉴定术鉴定诅咒物品——应揭示诅咒
        curse_result = identify_magic_item(cid3, "复仇之剑", method="identify_spell", db_path=db)
        assert curse_result["success"], f"鉴定诅咒物品应成功: {curse_result['message']}"
        assert curse_result["reveals_curse"], "鉴定术应揭示诅咒"

        # 短休接触鉴定诅咒物品——不应揭示诅咒
        curse_result2 = identify_magic_item(cid3, "复仇之剑", method="short_rest", db_path=db)
        assert curse_result2["success"], f"短休鉴定应成功: {curse_result2['message']}"
        assert not curse_result2["reveals_curse"], "短休接触不应揭示诅咒"

        # 鉴定不在物品栏中的物品应失败
        not_in_inv = identify_magic_item(cid3, "跳跃戒指", method="short_rest", db_path=db)
        assert not not_in_inv["success"], "鉴定不在物品栏的物品应失败"
        assert "物品栏" in not_in_inv["message"]

        # 鉴定未知物品应失败
        unknown = identify_magic_item(cid3, "不存在的物品", method="short_rest", db_path=db)
        assert not unknown["success"], "鉴定未知物品应失败"

        # 未知鉴定方式应失败
        bad_method = identify_magic_item(cid3, "触月剑", method="invalid_method", db_path=db)
        assert not bad_method["success"], "未知鉴定方式应失败"

        print("[loot] 鉴定魔法物品 ✓")
    finally:
        try:
            os.unlink(tmp.name)
        except PermissionError:
            pass

    print("[loot] 自检通过 ✓")


if __name__ == "__main__":
    import os
    _self_test()
