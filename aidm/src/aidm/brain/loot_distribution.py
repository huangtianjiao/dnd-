"""多人战利品分配系统。

击败怪物后按 CR 生成战利品池，再按分配策略分发物品/金币给玩家。

规则出处:
  - D&D 5E 没有官方"自动战利品分配"规则；本模块实现常见的桌上约定。
  - 战利品表参考: 城主指南 (DMG) §7 宝藏 / 遭遇奖励阈值。
    - 金币: 按 CR 查表（此处用简化公式）。
    - 物品: 低 CR 掉落消耗品/普通魔法物品；高 CR 掉落稀有/传说。
  - 分配策略为社区常见做法：
    - NEED_FIRST: 需求优先——声明需要的玩家优先获得。
    - ROUND_ROBIN: 轮流拾取——按先攻顺序轮流选择物品。
    - ROLL_OFF: 点数分配——掷骰决定优先权。
    - DM_ASSIGN: DM指定——DM直接指定归属。
  - 金币分配: 平均分配（向下取整，余数给先攻第一人）。

设计:
  - LootItem: 一件物品的元数据（名称/类型/稀有度/价值/数量）。
  - LootPool: 一场战斗的战利品池（金币/物品列表）。
  - DistributionRecord: 一次分配的完整记录（谁拿了什么）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..engine import dice

# ──────────────────────────────────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────────────────────────────────

class Rarity(str, Enum):
    """物品稀有度（DMG §7）。"""
    COMMON = "普通"
    UNCOMMON = "非普通"
    RARE = "稀有"
    VERY_RARE = "极稀有"
    LEGENDARY = "传说"


class DistributionMode(str, Enum):
    """战利品分配策略。"""
    NEED_FIRST = "NEED_FIRST"     # 需求优先
    ROUND_ROBIN = "ROUND_ROBIN"   # 轮流拾取
    ROLL_OFF = "ROLL_OFF"         # 点数分配
    DM_ASSIGN = "DM_ASSIGN"       # DM指定


@dataclass
class LootItem:
    """一件战利品物品。"""
    item_id: str                          # 唯一标识
    name: str                             # 物品名称
    item_type: str = "misc"               # weapon/armor/potion/scroll/misc
    rarity: str = "普通"                  # Rarity.value
    value_gp: int = 0                     # 价值（金币）
    quantity: int = 1                     # 数量
    description: str = ""                 # 描述
    assigned_to: str | None = None     # 已分配给的玩家名


@dataclass
class LootPool:
    """一场战斗的战利品池。"""
    pool_id: str
    campaign_id: int
    combat_round: int = 0                 # 触发战斗的轮次（追溯用）
    gold: int = 0                         # 金币总量
    items: list[LootItem] = field(default_factory=list)
    distributed: bool = False             # 是否已分配完毕


@dataclass
class DistributionRecord:
    """一次分配的完整记录。"""
    record_id: str
    pool_id: str
    campaign_id: int
    mode: str                             # DistributionMode.value
    gold_distribution: dict = field(default_factory=dict)   # {player_name: gold}
    item_distribution: dict = field(default_factory=dict)   # {item_id: player_name}
    timestamp: str = ""


# ──────────────────────────────────────────────────────────────────────────
# 战利品池生成
# ──────────────────────────────────────────────────────────────────────────

# CR → 金币范围（简化版 DMG 遭遇奖励）
# 出处: 城主指南 §7 宝藏阈值（数值为近似简化）
_GOLD_BY_CR = {
    0: (5, 15),        # CR 0: 5-15 gp
    1: (10, 30),
    2: (20, 50),
    3: (30, 80),
    4: (50, 120),
    5: (80, 180),
    6: (100, 250),
    7: (150, 350),
    8: (200, 500),
    9: (300, 700),
    10: (400, 900),
}

# CR → 物品掉落概率与稀有度权重
# 出处: 城主指南 §7 魔法物品（B/X/Y/Z 表的简化合并）
_ITEM_TABLE_BY_CR = {
    # low CR (0-4): 多为消耗品，偶尔非普通
    "low": [
        (0.30, "药水", "普通", 25, "治疗药水"),
        (0.20, "卷轴", "普通", 15, "法术卷轴"),
        (0.15, "杂项", "非普通", 50, "不灭烛火"),
        (0.10, "武器", "非普通", 100, "+1 武器"),
        (0.05, "护甲", "非普通", 100, "+1 护甲"),
    ],
    # mid CR (5-10): 稀有物品开始出现
    "mid": [
        (0.25, "药水", "普通", 50, "高级治疗药水"),
        (0.20, "卷轴", "非普通", 80, "法术卷轴"),
        (0.15, "武器", "稀有", 500, "+2 武器"),
        (0.10, "护甲", "稀有", 500, "+2 护甲"),
        (0.05, "饰品", "稀有", 800, "稀有戒指"),
    ],
}


def _cr_bucket(cr: float) -> str:
    """CR → low/mid 桶。"""
    if cr <= 4:
        return "low"
    return "mid"


def generate_loot_pool(campaign_id: int, monster_crs: list[float],
                       combat_round: int = 0) -> LootPool:
    """根据击败怪物的 CR 列表生成战利品池。

    规则: 城主指南 §7 宝藏阈值（简化）
    说明:
      - 金币: 每个 CR 查表掷一次区间随机值。
      - 物品: 每个 CR 按概率表掷一次是否掉落及掉什么。
      - 高 CR (>10) 按 CR 10 处理（保守上限）。
      - 小数 CR（如 0.5）向下取整后查表（0.5 按 CR 0）。
    """
    import secrets as _sec
    pool_id = f"pool_{campaign_id}_{combat_round}_{_sec.token_hex(3)}"
    total_gold = 0
    items: list[LootItem] = []

    for cr in monster_crs:
        # 金币
        clamped = int(max(0, min(cr, 10)))
        lo, hi = _GOLD_BY_CR[clamped]
        # 区间内均匀随机
        gold_roll = lo + (_sec.randbelow(hi - lo + 1) if hi > lo else 0)
        total_gold += gold_roll

        # 物品
        bucket = _cr_bucket(clamped)
        table = _ITEM_TABLE_BY_CR.get(bucket, [])
        roll = _sec.randbelow(100) / 100.0   # 0.00-0.99
        cumulative = 0.0
        for prob, itype, rarity, val, desc in table:
            cumulative += prob
            if roll < cumulative:
                iid = f"item_{len(items)}_{_sec.token_hex(2)}"
                items.append(LootItem(
                    item_id=iid, name=desc, item_type=itype,
                    rarity=rarity, value_gp=val, quantity=1,
                    description=f"{rarity}级{itype}",
                ))
                break

    return LootPool(
        pool_id=pool_id, campaign_id=campaign_id,
        combat_round=combat_round, gold=total_gold,
        items=items, distributed=False,
    )


# ──────────────────────────────────────────────────────────────────────────
# 金币分配
# ──────────────────────────────────────────────────────────────────────────

def distribute_gold(pool: LootPool, player_names: list[str]) -> dict:
    """平均分配金币（向下取整，余数给第一人）。

    规则: 桌上约定——平分金币，余数归先政第一人或房主。
    返回: {player_name: gold_amount}
    """
    if not player_names or pool.gold <= 0:
        return {name: 0 for name in player_names}

    n = len(player_names)
    base = pool.gold // n
    remainder = pool.gold % n

    result = {}
    for i, name in enumerate(player_names):
        result[name] = base + (1 if i < remainder else 0)
    return result


# ──────────────────────────────────────────────────────────────────────────
# 物品分配
# ──────────────────────────────────────────────────────────────────────────

def distribute_items_need_first(
    pool: LootPool,
    needs: dict[str, list[str]],   # {player_name: [item_id, ...]}
    player_names: list[str],
) -> dict[str, str]:
    """需求优先分配：声明需要的玩家优先获得该物品。

    规则: 社区常见做法——"谁能用谁拿"，多人需要则 ROLL_OFF。
    说明: 若多个玩家需要同一物品，按 player_names 顺序第一个获得
          （简化处理；完整版应触发 ROLL_OFF）。
    返回: {item_id: player_name}
    """
    assignment: dict[str, str] = {}
    for item in pool.items:
        if item.assigned_to:
            assignment[item.item_id] = item.assigned_to
            continue
        # 找出声明需要该物品的玩家
        needers = [name for name in player_names
                   if name in needs and item.item_id in needs[name]]
        if needers:
            winner = needers[0]   # 简化：第一个声明的
            item.assigned_to = winner
            assignment[item.item_id] = winner
        # 无人需要 → 不分配（留在池中）
    return assignment


def distribute_items_round_robin(
    pool: LootPool,
    initiative_order: list[str],   # 按先攻排序的玩家名列表
) -> dict[str, str]:
    """轮流拾取：按先攻顺序轮流选择物品。

    规则: 社区常见做法——"一人挑一件"，避免独占。
    说明: 物品按池中顺序分配，玩家按先政顺序循环。
    返回: {item_id: player_name}
    """
    if not initiative_order or not pool.items:
        return {}

    assignment: dict[str, str] = {}
    for i, item in enumerate(pool.items):
        if item.assigned_to:
            assignment[item.item_id] = item.assigned_to
            continue
        player = initiative_order[i % len(initiative_order)]
        item.assigned_to = player
        assignment[item.item_id] = player
    return assignment


def distribute_items_roll_off(
    pool: LootPool,
    player_names: list[str],
    rng=dice.roll_d20,
) -> dict[str, str]:
    """点数分配：每个物品所有感兴趣玩家掷 d20，最高者获得。

    规则: 社区常见做法——"掷骰定归属"，d20 高者得，平局重掷。
    说明: 此处简化为所有玩家都参与每个物品的争夺。
    返回: {item_id: player_name}
    """
    if not player_names or not pool.items:
        return {}

    assignment: dict[str, str] = {}
    for item in pool.items:
        if item.assigned_to:
            assignment[item.item_id] = item.assigned_to
            continue
        # 所有玩家掷 d20
        rolls = {name: rng().used for name in player_names}
        max_roll = max(rolls.values())
        # 取第一个达到最大值的玩家（平局简化）
        winners = [name for name, r in rolls.items() if r == max_roll]
        winner = winners[0]
        item.assigned_to = winner
        assignment[item.item_id] = winner
    return assignment


def distribute_items_dm_assign(
    pool: LootPool,
    assignments: dict[str, str],   # {item_id: player_name}
) -> dict[str, str]:
    """DM指定分配：DM直接指定每件物品归属。

    规则: DM拥有最终裁决权——可绕过任何分配策略手动指定。
    返回: {item_id: player_name}
    """
    result: dict[str, str] = {}
    for item in pool.items:
        target = assignments.get(item.item_id)
        if target:
            item.assigned_to = target
            result[item.item_id] = target
    return result


# ──────────────────────────────────────────────────────────────────────────
# 完整分配流程
# ──────────────────────────────────────────────────────────────────────────

def distribute_loot(
    pool: LootPool,
    player_names: list[str],
    mode: DistributionMode = DistributionMode.ROUND_ROBIN,
    initiative_order: list[str] | None = None,
    needs: dict[str, list[str]] | None = None,
    dm_assignments: dict[str, str] | None = None,
) -> DistributionRecord:
    """执行完整的战利品分配流程。

    参数:
      pool: 战利品池
      player_names: 参与分配的玩家名列表
      mode: 分配策略
      initiative_order: 先攻顺序（ROUND_ROBIN 需要）
      needs: 需求声明（NEED_FIRST 需要），{player_name: [item_id]}
      dm_assignments: DM指定（DM_ASSIGN 需要），{item_id: player_name}

    返回: DistributionRecord
    """
    import datetime
    import secrets as _sec

    # 金币分配
    gold_dist = distribute_gold(pool, player_names)

    # 物品分配
    if mode == DistributionMode.NEED_FIRST:
        item_dist = distribute_items_need_first(
            pool, needs or {}, player_names)
    elif mode == DistributionMode.ROUND_ROBIN:
        order = initiative_order or player_names
        item_dist = distribute_items_round_robin(pool, order)
    elif mode == DistributionMode.ROLL_OFF:
        item_dist = distribute_items_roll_off(pool, player_names)
    elif mode == DistributionMode.DM_ASSIGN:
        item_dist = distribute_items_dm_assign(
            pool, dm_assignments or {})
    else:
        item_dist = {}

    pool.distributed = True

    return DistributionRecord(
        record_id=f"rec_{_sec.token_hex(4)}",
        pool_id=pool.pool_id,
        campaign_id=pool.campaign_id,
        mode=mode.value,
        gold_distribution=gold_dist,
        item_distribution=item_dist,
        timestamp=datetime.datetime.now().isoformat(),
    )


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 战利品池生成
    pool = generate_loot_pool(
        campaign_id=1, monster_crs=[1, 2, 3], combat_round=5)
    assert pool.campaign_id == 1
    assert pool.combat_round == 5
    assert pool.gold > 0   # 至少有一些金币
    # 物品可能为空（概率性），但若有则结构正确
    for item in pool.items:
        assert item.item_id and item.name
        assert item.rarity in [r.value for r in Rarity]

    # 金币分配：平均+余数
    pool2 = generate_loot_pool(2, [5])
    pool2.gold = 100   # 固定便于断言
    gd = distribute_gold(pool2, ["A", "B", "C"])
    assert gd["A"] == 34 and gd["B"] == 33 and gd["C"] == 33   # 100/3

    # 余数给前几个
    pool2.gold = 10
    gd = distribute_gold(pool2, ["A", "B", "C"])
    assert gd["A"] == 4 and gd["B"] == 3 and gd["C"] == 3

    # 空玩家
    assert distribute_gold(pool2, []) == {}

    # ROUND_ROBIN 分配
    pool3 = generate_loot_pool(3, [1])
    # 手动塞3个物品
    pool3.items = [
        LootItem(item_id="i1", name="剑", item_type="weapon"),
        LootItem(item_id="i2", name="盾", item_type="armor"),
        LootItem(item_id="i3", name="弓", item_type="weapon"),
    ]
    order = ["Alice", "Bob", "Carol"]
    dist = distribute_items_round_robin(pool3, order)
    assert dist["i1"] == "Alice"
    assert dist["i2"] == "Bob"
    assert dist["i3"] == "Carol"
    assert pool3.items[0].assigned_to == "Alice"

    # NEED_FIRST 分配
    pool4 = generate_loot_pool(4, [1])
    pool4.items = [
        LootItem(item_id="i1", name="法杖", item_type="weapon"),
        LootItem(item_id="i2", name="铠甲", item_type="armor"),
    ]
    needs = {"Alice": ["i1"], "Bob": ["i2"]}
    dist = distribute_items_need_first(pool4, needs, ["Alice", "Bob"])
    assert dist["i1"] == "Alice"
    assert dist["i2"] == "Bob"

    # 无人需要 → 不分配
    pool5 = generate_loot_pool(5, [1])
    pool5.items = [LootItem(item_id="i1", name="杂物")]
    dist = distribute_items_need_first(pool5, {}, ["A"])
    assert "i1" not in dist

    # ROLL_OFF 分配（固定骰子）
    class _FixedRoll:
        def __init__(self, vals): self._vals = vals; self._i = 0
        def __call__(self): v = self._vals[self._i]; self._i += 1; return type("R",(),{"used":v})()
    pool6 = generate_loot_pool(6, [1])
    pool6.items = [LootItem(item_id="i1", name="宝物")]
    # Alice 掷 18，Bob 掷 12 → Alice 赢
    dist = distribute_items_roll_off(
        pool6, ["Alice", "Bob"],
        rng=_FixedRoll([18, 12]))
    assert dist["i1"] == "Alice"

    # DM_ASSIGN 分配
    pool7 = generate_loot_pool(7, [1])
    pool7.items = [
        LootItem(item_id="i1", name="戒指"),
        LootItem(item_id="i2", name="项链"),
    ]
    dm_assigns = {"i1": "Alice", "i2": "Bob"}
    dist = distribute_items_dm_assign(pool7, dm_assigns)
    assert dist["i1"] == "Alice" and dist["i2"] == "Bob"
    assert pool7.items[0].assigned_to == "Alice"

    # 完整流程
    pool8 = generate_loot_pool(8, [3, 4])
    pool8.items = [
        LootItem(item_id="x1", name="长剑"),
        LootItem(item_id="x2", name="板甲"),
    ]
    rec = distribute_loot(
        pool8, ["Alice", "Bob"],
        mode=DistributionMode.ROUND_ROBIN,
        initiative_order=["Alice", "Bob"],
    )
    assert rec.mode == "ROUND_ROBIN"
    assert rec.pool_id == pool8.pool_id
    assert pool8.distributed
    assert rec.item_distribution["x1"] == "Alice"
    assert rec.item_distribution["x2"] == "Bob"
    # 金币分配存在
    assert "Alice" in rec.gold_distribution

    print("[loot] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
