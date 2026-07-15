"""战斗状态机 — 先攻 / 回合 / 动作经济 / 移动 / 专注维持。

依赖 engine.dice（roll_d20）、engine.check（saving_throw）。标注规则ID+出处。
角色卡的真实属性/HP 由 P1 stats 模块持有；本模块管理回合顺序与动作经济。

规则出处:
  - topics/玩家手册2024/进行游戏/战斗流程.htm
  - topics/玩家手册2024/进行游戏/移动和位置.htm
  - topics/玩家手册2024/进行游戏/动作.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from . import dice, check


# ──────────────────────────────────────────────────────────────────────────
# 战斗参战者
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class Combatant:
    """战斗中的一个参战者（回合经济 + 位置追踪）。

    规则: R-CMB-004 回合动作经济 / R-CMB-013 反应经济
    出处: topics/玩家手册2024/进行游戏/战斗流程.htm
    """
    cid: str                          # 唯一标识（关联角色卡/怪物）
    name: str
    dex_mod: int = 0                  # 先攻计算用敏捷调整值
    initiative: int = 0
    side: str = "player"              # player / enemy
    is_player: bool = True
    surprised: bool = False           # R-GLS-009 突袭 → 先攻劣势
    # 同组怪物共用先攻：同组标记后由 roll_initiative 只掷一次
    group_id: Optional[str] = None

    # ── 动作经济（R-CMB-004/012/013, R-GLS-083）──
    action_used: bool = False
    bonus_action_used: bool = False
    reaction_used: bool = False
    free_interaction_used: int = 0     # R-CMB-005 每回合1次免费物件交互

    # ── 移动（R-CMB-030~039）──
    speed: int = 30                    # 速度（尺）；R-CMB-030 回合移动上限=速度
    speed_remaining: int = 0           # 本回合剩余移动力（尺）
    position: tuple[int, int] = (0, 0) # 方格坐标 (x, y)；R-CMB-032 每格5尺
    reach: int = 5                     # 近战触及范围（尺）；R-CMB-024 默认5尺

    # ── 专注（R-SPL-019 / R-GLS-013）──
    concentrating_on: Optional[str] = None

    # ── 动作增益状态（持续至下回合开始或条件失效）──
    disengage_active: bool = False     # R-CMB-007 撤离：本回合移动不引发借机攻击
    dodge_active: bool = False         # R-CMB-008 回避：对你攻击具有劣势
    hidden: bool = False               # R-CMB-009 躲藏成功 → 隐形状态


# ──────────────────────────────────────────────────────────────────────────
# 战斗实例
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class Combat:
    """一场战斗的回合状态。"""
    participants: list[Combatant] = field(default_factory=list)
    initiative_order: list[Combatant] = field(default_factory=list)
    round: int = 0
    current_index: int = 0
    active: bool = False
    seconds_elapsed: int = 0           # R-CMB-001 一轮6秒


# ──────────────────────────────────────────────────────────────────────────
# 先攻
# ──────────────────────────────────────────────────────────────────────────

def roll_initiative(combatants: list[Combatant]) -> list[Combatant]:
    """为参战者掷先攻：d20 + 敏捷调整值，突袭者劣势，降序排列。

    规则: R-CMB-002 先攻检定 + R-GLS-009 突袭劣势
    出处: topics/玩家手册2024/进行游戏/战斗流程.htm
    说明:
      - 相同怪物组（group_id 相同且非玩家）只掷一次，全组共用先攻。
      - 平局处理见 resolve_initiative_ties。
    """
    rolled_groups: set[str] = set()
    group_initiative: dict[str, int] = {}   # group_id -> 该组的先政值
    for c in combatants:
        # 同组怪物共用先政：已掷过则沿用组内第一个成员的先政值
        if (c.group_id is not None and not c.is_player
                and c.group_id in rolled_groups):
            c.initiative = group_initiative[c.group_id]
            continue
        r = dice.roll_d20(advantage=False, disadvantage=c.surprised)  # R-GLS-009
        c.initiative = r.used + c.dex_mod
        if c.group_id is not None and not c.is_player:
            rolled_groups.add(c.group_id)
            group_initiative[c.group_id] = c.initiative
    order = sorted(combatants, key=lambda c: c.initiative, reverse=True)   # 降序
    return order


def resolve_initiative_ties(tied_combatants: list[Combatant]) -> list[Combatant]:
    """先政平局处理：怪物间由DM决定、玩家间自行决定、玩家与怪物相同由DM裁定。

    规则: R-CMB-003 先政平局处理
    出处: topics/玩家手册2024/进行游戏/战斗流程.htm
    说明: 本函数保持传入顺序不变（由调用方/DM预先排好），仅作为语义锚点。
          若需自动稳定排序，可附加 cid 作为次序键。
    """
    # 保持稳定：调用方负责 DM 决策顺序；这里仅返回原序列
    return list(tied_combatants)


# ──────────────────────────────────────────────────────────────────────────
# 战斗流程控制
# ──────────────────────────────────────────────────────────────────────────

def start_combat(combat: Combat, combatants: list[Combatant]) -> None:
    """开始战斗：掷先政、排序、进入第1轮。

    规则: R-CMB-001 一轮6秒 / R-CMB-002 先政 / R-CMB-004 回合开始
    出处: topics/玩家手册2024/进行游戏/战斗流程.htm
    """
    combat.participants = list(combatants)
    combat.initiative_order = roll_initiative(combatants)
    combat.round = 1
    combat.current_index = 0
    combat.active = True
    combat.seconds_elapsed = 0
    # 第一个参战者回合开始：重置移动力与动作经济
    cur = current_combatant(combat)
    if cur is not None:
        _reset_turn_economy(cur)


def current_combatant(combat: Combat) -> Optional[Combatant]:
    """当前回合的参战者。规则: R-CMB-004"""
    if not combat.active or not combat.initiative_order:
        return None
    return combat.initiative_order[combat.current_index % len(combat.initiative_order)]


def _reset_turn_economy(c: Combatant) -> None:
    """回合开始时重置动作经济与移动力。

    规则: R-CMB-004 回合动作经济 / R-CMB-013 反应在下回合开始刷新
          R-CMB-030 回合移动上限=速度
    出处: topics/玩家手册2024/进行游戏/战斗流程.htm ; 移动和位置.htm
    说明: 反应在"自己的下个回合开始"时刷新（R-CMB-013）。
    """
    c.action_used = False
    c.bonus_action_used = False
    c.reaction_used = False
    c.free_interaction_used = 0
    c.speed_remaining = c.speed                       # R-CMB-030
    # 持续到下回合开始的增益在此清除
    c.disengage_active = False                        # R-CMB-007 仅本回合
    c.dodge_active = False                            # R-CMB-008 至下回合开始


def advance_turn(combat: Combat) -> Optional[Combatant]:
    """推进到下一参战者回合：重置该回合动作经济；轮次结束则进入下一轮（+6秒）。

    规则: R-CMB-001 一轮约6秒 / R-CMB-004 回合开始
    出处: topics/玩家手册2024/进行游戏/战斗流程.htm
    """
    if not combat.active:
        return None
    combat.current_index += 1
    if combat.current_index >= len(combat.initiative_order):     # 一轮结束
        combat.current_index = 0
        combat.round += 1
        combat.seconds_elapsed += 6                               # R-CMB-001
    cur = current_combatant(combat)
    if cur is not None:
        _reset_turn_economy(cur)
    return cur


# ──────────────────────────────────────────────────────────────────────────
# 动作经济查询 / 消耗
# ──────────────────────────────────────────────────────────────────────────

def can_take_action(c: Combatant) -> bool:
    """是否还能执行动作。规则: R-CMB-011 一次一个动作；R-GLS-050 失能则不能"""
    return not c.action_used


def can_take_bonus_action(c: Combatant) -> bool:
    """每回合至多1附赠动作（须有特性启用）。规则: R-CMB-012 / R-GLS-083"""
    return not c.bonus_action_used


def can_take_reaction(c: Combatant) -> bool:
    """每回合1反应，用后至下回合开始不可再用。规则: R-CMB-013 / R-GLS-083"""
    return not c.reaction_used


def use_action(c: Combatant) -> bool:
    """消耗一个动作。规则: R-CMB-011 / R-CMB-004"""
    if not can_take_action(c):
        return False
    c.action_used = True
    return True


def use_bonus_action(c: Combatant) -> bool:
    """消耗一个附赠动作。规则: R-CMB-012"""
    if not can_take_bonus_action(c):
        return False
    c.bonus_action_used = True
    return True


def use_reaction(c: Combatant) -> bool:
    """消耗一个反应。规则: R-CMB-013"""
    if not can_take_reaction(c):
        return False
    c.reaction_used = True
    return True


def use_free_interaction(c: Combatant) -> bool:
    """消耗本回合的免费物件交互（每回合1次）。

    规则: R-CMB-005 免费物件交互  出处: 战斗流程.htm
    返回: True=成功消耗免费交互；False=本回合免费交互已用（需 Utilize 动作）。
    """
    if c.free_interaction_used >= 1:
        return False
    c.free_interaction_used += 1
    return True


# ──────────────────────────────────────────────────────────────────────────
# 移动与位置（R-CMB-030~039）
# ──────────────────────────────────────────────────────────────────────────

FT_PER_SQUARE = 5  # R-CMB-032 每格5尺


def speed_to_squares(speed_ft: int) -> int:
    """速度（尺）转格数：speed / 5。

    规则: R-CMB-032 方格地图尺度与速度转格
    出处: topics/玩家手册2024/进行游戏/移动和位置.htm
    """
    return dice.round_down(speed_ft / FT_PER_SQUARE)


def move_cost(distance_ft: int, difficult: bool = False) -> int:
    """计算移动消耗的移动力（尺）。

    规则: R-CMB-031 困难地形移动力消耗
          困难地形上每移动1尺需额外消耗1尺移动力（即每尺2尺）。
    出处: topics/玩家手册2024/进行游戏/移动和位置.htm
    """
    per_ft = 2 if difficult else 1
    return distance_ft * per_ft


def move(c: Combatant, distance_ft: int, difficult: bool = False) -> int:
    """消耗移动力移动指定距离；返回实际移动的距离（尺）。

    规则: R-CMB-030 回合移动上限 / R-CMB-031 困难地形消耗
    出处: topics/玩家手册2024/进行游戏/移动和位置.htm
    说明: 移动力不足时按可承受的最大距离移动（向下取整到整尺）。
    """
    cost = move_cost(distance_ft, difficult)
    if cost > c.speed_remaining:
        # 计算在剩余移动力下能移动多少尺
        per_ft = 2 if difficult else 1
        actual = dice.round_down(c.speed_remaining / per_ft)
        c.speed_remaining -= actual * per_ft
        return max(0, actual)
    c.speed_remaining -= cost
    return distance_ft


def enter_square(c: Combatant, difficult: bool = False) -> int:
    """进入一个邻接格子，消耗相应移动力（格）；返回消耗的格数。

    规则: R-CMB-033 方格进入移动力
          进入未占据邻接格需1格移动力；困难地形的格子需2格。
    出处: topics/玩家手册2024/进行游戏/移动和位置.htm
    """
    cost_sq = 2 if difficult else 1
    cost_ft = cost_sq * FT_PER_SQUARE
    if cost_ft > c.speed_remaining:
        return 0  # 移动力不足，无法进入
    c.speed_remaining -= cost_ft
    return cost_sq


# ──────────────────────────────────────────────────────────────────────────
# 生物体型与空间（R-CMB-037）
# ──────────────────────────────────────────────────────────────────────────

# 规则: R-CMB-037 生物体型与占据空间
# 出处: topics/玩家手册2024/进行游戏/移动和位置.htm
_SIZE_FOOTPRINT = {
    "tiny":       (2.5, 0.25),   # 微型 2.5尺 1/4格
    "small":      (5.0, 1.0),    # 小型 5尺 1格
    "medium":     (5.0, 1.0),    # 中型 5尺 1格
    "large":      (10.0, 4.0),   # 大型 10尺 4格(2x2)
    "huge":       (15.0, 9.0),   # 巨型 15尺 9格(3x3)
    "gargantuan": (20.0, 16.0),  # 超巨型 20尺 16格(4x4)
}


def get_size_footprint(size: str) -> tuple[float, float]:
    """返回 (空间尺, 占据格数)。

    规则: R-CMB-037 生物体型与占据空间
    出处: topics/玩家手册2024/进行游戏/移动和位置.htm
    """
    key = size.lower()
    if key not in _SIZE_FOOTPRINT:
        raise ValueError(f"未知体型 {size!r}，可选: {list(_SIZE_FOOTPRINT)}")
    return _SIZE_FOOTPRINT[key]


# ──────────────────────────────────────────────────────────────────────────
# 穿过其他生物的空间（R-CMB-038）
# ──────────────────────────────────────────────────────────────────────────

def can_pass_through(mover_size: str, creature_size: str,
                     is_ally: bool = False, is_incapacitated: bool = False) -> bool:
    """是否能穿过某生物的空间。

    规则: R-CMB-038 穿过其他生物的空间
          可穿过：盟友 / 失能生物 / 微型生物 / 体型相差两级以上的生物。
    出处: topics/玩家手册2024/进行游戏/移动和位置.htm
    """
    if is_ally or is_incapacitated:
        return True
    # 体型相差两级以上
    sizes = list(_SIZE_FOOTPRINT.keys())
    try:
        i_m = sizes.index(mover_size.lower())
        i_c = sizes.index(creature_size.lower())
    except ValueError:
        return False
    return abs(i_m - i_c) >= 2


def pass_cost_multiplier(mover_size: str, creature_size: str,
                         is_ally: bool = False, is_incapacitated: bool = False) -> int:
    """穿过某生物空间的移动力倍率。

    规则: R-CMB-038 除微型和盟友外，其他生物的空间对你而言均为困难地形。
    出处: topics/玩家手册2024/进行游戏/移动和位置.htm
    返回: 1=正常（无额外消耗），2=困难地形（每尺双倍消耗）。
    """
    # 微型生物或盟友：正常通过
    if mover_size.lower() == "tiny" or is_ally:
        return 1
    # 其他生物空间视为困难地形（若可通过）
    if can_pass_through(mover_size, creature_size, is_ally, is_incapacitated):
        return 2
    return 1  # 无法穿过时不应调用此函数


# ──────────────────────────────────────────────────────────────────────────
# 俯卧倒地（R-CMB-036）
# ──────────────────────────────────────────────────────────────────────────

def drop_prone(c: Combatant) -> bool:
    """令自身进入倒地状态；无需动作或速度，但速度为0时不能。

    规则: R-CMB-036 俯卧倒地
          cost = 0; precondition: speed > 0
    出处: topics/玩家手册2024/进行游戏/移动和位置.htm
    """
    if c.speed <= 0:
        return False
    # prone 状态由 conditions 模块管理；此处仅返回是否可执行
    return True


# ──────────────────────────────────────────────────────────────────────────
# 专注维持
# ──────────────────────────────────────────────────────────────────────────

def concentration_save_dc(damage_taken: int) -> int:
    """专注伤害豁免 DC = max(10, floor(damage/2))，至高 30。

    规则: R-GLS-013 专注维持检定（=R-SPL-020）  出处: 术语汇编/常见规则词汇.htm
    """
    return min(30, max(10, dice.round_down(damage_taken / 2)))


def concentration_save(con_mod: int, con_prof: bool, prof: int, damage_taken: int) -> bool:
    """专注者受伤时进行体质豁免维持专注。

    规则: R-GLS-013 专注维持检定（DC=max(10,dmg/2) 上限30）
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    返回: 是否维持专注（True=维持，False=失去）。
    """
    dc = concentration_save_dc(damage_taken)
    res = check.saving_throw(mod=con_mod, prof=prof, proficient=con_prof, dc=dc)
    return res.success


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 先政：固定 d20
    orig = dice.roll_d20
    class _R:
        def __init__(s, u): s.used, s.rolls, s.mode = u, [u], "normal"
    dice.roll_d20 = lambda advantage=False, disadvantage=False: _R(10)
    cs = [Combatant(cid="a", name="A", dex_mod=2),
          Combatant(cid="b", name="B", dex_mod=3, side="enemy", is_player=False)]
    order = roll_initiative(cs)
    assert all(c.initiative == 10 + getattr(c, "dex_mod", 0) for c in order)
    # 战斗推进
    combat = Combat()
    start_combat(combat, cs)
    assert combat.round == 1 and combat.active
    cur = current_combatant(combat)
    assert cur is order[0]
    # 动作经济
    assert can_take_action(cur) and can_take_bonus_action(cur) and can_take_reaction(cur)
    use_action(cur); use_bonus_action(cur); use_reaction(cur)
    assert not can_take_action(cur) and not can_take_bonus_action(cur) and not can_take_reaction(cur)
    # 下一回合：重置经济
    nxt = advance_turn(combat)
    assert nxt is order[1]
    assert can_take_action(nxt)                      # 新回合动作经济已重置
    # 轮次推进：第二轮 +6秒
    advance_turn(combat)                              # 回到 order[0]，第二轮
    assert combat.round == 2 and combat.seconds_elapsed == 6
    # 突袭劣势
    dice.roll_d20 = lambda advantage=False, disadvantage=False: _R(15 if not disadvantage else 5)
    surp = Combatant(cid="s", name="S", dex_mod=0, surprised=True)
    roll_initiative([surp])
    assert surp.initiative == 5                       # 劣势取低 5
    dice.roll_d20 = orig

    # 免费物件交互（R-CMB-005）
    c = Combatant(cid="t", name="T")
    assert use_free_interaction(c) is True
    assert use_free_interaction(c) is False           # 第二个需 Utilize 动作

    # 移动力消耗（R-CMB-030/031）
    c2 = Combatant(cid="m", name="M", speed=30)
    c2.speed_remaining = c2.speed
    moved = move(c2, 10, difficult=False)
    assert moved == 10 and c2.speed_remaining == 20
    # 困难地形：每尺2尺消耗
    moved = move(c2, 5, difficult=True)
    assert moved == 5 and c2.speed_remaining == 10    # 5*2=10 消耗
    # 移动力不足：剩余10，困难地形走10尺只能走5尺
    moved = move(c2, 10, difficult=True)
    assert moved == 5 and c2.speed_remaining == 0

    # 速度转格（R-CMB-032）
    assert speed_to_squares(30) == 6
    assert speed_to_squares(25) == 5

    # 进入格子（R-CMB-033）
    c3 = Combatant(cid="e", name="E", speed=30)
    c3.speed_remaining = 30
    assert enter_square(c3, difficult=False) == 1     # 消耗1格=5尺
    assert c3.speed_remaining == 25
    assert enter_square(c3, difficult=True) == 2      # 困难地形2格=10尺
    assert c3.speed_remaining == 15

    # 体型占据空间（R-CMB-037）
    assert get_size_footprint("tiny") == (2.5, 0.25)
    assert get_size_footprint("medium") == (5.0, 1.0)
    assert get_size_footprint("large") == (10.0, 4.0)
    assert get_size_footprint("gargantuan") == (20.0, 16.0)

    # 穿过生物空间（R-CMB-038）
    assert can_pass_through("medium", "huge", is_ally=False) is True   # 相差两级
    assert can_pass_through("medium", "large", is_ally=False) is False # 相差一级
    assert can_pass_through("medium", "medium", is_ally=True) is True  # 盟友
    assert pass_cost_multiplier("medium", "huge", is_ally=False) == 2  # 困难地形
    assert pass_cost_multiplier("tiny", "medium", is_ally=False) == 1  # 微型正常

    # 俯卧倒地（R-CMB-036）
    assert drop_prone(Combatant(cid="p", name="P", speed=30)) is True
    assert drop_prone(Combatant(cid="z", name="Z", speed=0)) is False

    # 专注 DC
    assert concentration_save_dc(0) == 10              # 下限10
    assert concentration_save_dc(20) == 10            # floor(10)=10
    assert concentration_save_dc(25) == 12            # floor(12.5)=12
    assert concentration_save_dc(80) == 30            # 上限30
    # 专注豁免（monkeypatch saving_throw）
    orig2 = check.saving_throw
    check.saving_throw = lambda **kw: type("R", (), {"success": kw["dc"] <= 10})()
    assert concentration_save(con_mod=2, con_prof=True, prof=3, damage_taken=5) is True
    check.saving_throw = orig2

    # 同组怪物共用先攻
    g1 = Combatant(cid="g1", name="Goblin", dex_mod=2, side="enemy",
                   is_player=False, group_id="gob")
    g2 = Combatant(cid="g2", name="Goblin", dex_mod=2, side="enemy",
                   is_player=False, group_id="gob")
    dice.roll_d20 = lambda advantage=False, disadvantage=False: _R(10)
    roll_initiative([g1, g2])
    assert g1.initiative == g2.initiative == 12       # 同组共用
    dice.roll_d20 = orig

    print("[combat] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
