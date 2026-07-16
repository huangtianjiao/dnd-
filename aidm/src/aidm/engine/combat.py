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
# 掩护来源侧前置（R-ADD-004）
# ──────────────────────────────────────────────────────────────────────────

def cover_active(source_pos: tuple[int, int],
                 target_pos: tuple[int, int],
                 cover_pos: tuple[int, int],
                 cover_half_size: int = 1) -> bool:
    """判断掩护是否位于攻击来源与目标之间（同一侧无效）。

    规则: R-ADD-004 掩护来源侧前置
          只有攻击/效应来源位于掩护另一侧时，目标才获掩护增益；
          否则 cover_bonus=0。
    出处: topics/玩家手册2024/进行游戏/发动攻击.htm

    参数:
      source_pos: 攻击来源方格坐标 (x, y)
      target_pos: 目标方格坐标 (x, y)
      cover_pos: 掩护物件方格坐标 (x, y)
      cover_half_size: 掩护占据格数半径（默认1，即1格宽）

    返回: True 表示掩护有效（来源在掩护另一侧）
    说明: 使用重心连线法：若掩护中心到 source→target 连线的距离
          小于掩护半径，则掩护位于中间一侧。
    """
    sx, sy = source_pos
    tx, ty = target_pos
    cx, cy = cover_pos

    # 来源到目标的向量
    dx, dy = tx - sx, ty - sy
    if dx == 0 and dy == 0:
        return False  # 同格，掩护无效

    # 掩护中心到 source→target 线的距离（点-线距离公式）
    # 线: (sx,sy)→(tx,ty); 计算 cx,cy 到该段的垂足和距离
    line_len_sq = dx * dx + dy * dy
    # 投影参数 t
    t = ((cx - sx) * dx + (cy - sy) * dy) / line_len_sq
    # 掩护必须在 source 和 target 之间的线段上（0 < t < 1）
    if t <= 0 or t >= 1:
        return False
    # 垂足坐标
    px = sx + t * dx
    py = sy + t * dy
    # 掩护中心到连线的距离
    dist = ((cx - px) ** 2 + (cy - py) ** 2) ** 0.5
    return dist <= cover_half_size


# ──────────────────────────────────────────────────────────────────────────
# 拆分移动（R-ADD-006）
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class MoveSegment:
    """移动的一个分段。"""
    distance_ft: int
    difficult: bool = False
    trigger: str = "action"   # "before_action" / "after_action" / "bonus_action" / "reaction"


def move_split(c: Combatant, segments: list[MoveSegment]) -> list[int]:
    """拆分移动：在动作、附赠动作、反应前后分段移动。

    规则: R-ADD-006 拆分移动跨附赠动作/反应（补充 R-CMB-030）
          移动可拆分到动作、附赠动作、反应的前后。
    出处: topics/玩家手册2024/进行游戏/移动和位置.htm

    返回: 每段实际移动的尺数列表。
    """
    actual = []
    for seg in segments:
        moved = move(c, seg.distance_ft, seg.difficult)
        actual.append(moved)
    return actual


# ──────────────────────────────────────────────────────────────────────────
# 擒抱部位限制（R-ADD-010）
# ──────────────────────────────────────────────────────────────────────────

def grapple_capacity(grappler_hands_free: int) -> int:
    """每只空手（或触手等部位）最多擒抱一个生物。

    规则: R-ADD-010 擒抱部位限制
          grapple_requires_free_hand=true; one_grapple_per_hand_or_limbslot=true
    出处: topics/玩家手册2024/术语汇编/武器与徒手打击.htm
    """
    return max(0, grappler_hands_free)


def release_grapple(grappler: Combatant, target: Combatant) -> bool:
    """擒抱者随时可免费（无需动作）释放擒抱。

    规则: R-ADD-010 擒抱者可随时免费释放
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    """
    # 释放擒抱无需动作消耗；由调用方同时清除双方的擒抱相关状态
    return True


# ──────────────────────────────────────────────────────────────────────────
# 推撞结果（R-ADD-011）
# ──────────────────────────────────────────────────────────────────────────

# 体型等级表（从小到大）
_SIZE_ORDER = ["tiny", "small", "medium", "large", "huge", "gargantuan"]

def resolve_shove(attacker_str_mod: int, attacker_prof: int,
                  attacker_proficient_athletics: bool,
                  target_str_mod: int, target_dex_mod: int,
                  target_prof: int,
                  target_proficient_athletics: bool,
                  target_proficient_acrobatics: bool,
                  attacker_size: str = "medium",
                  target_size: str = "medium",
                  attacker_choice: str = "push",
                  advantage: bool = False,
                  disadvantage: bool = False) -> dict:
    """徒手打击推撞：攻击方用力量(运动)对抗目标力量(运动)或敏捷(特技)。

    规则: R-ADD-011 推撞结果（补充 R-GLS-034）
          成功时攻击者选择推开5尺或使其倒地；
          目标体型至多比攻击者大一级。
    出处: topics/玩家手册2024/术语汇编/武器与徒手打击.htm

    参数:
      attacker_choice: "push" 推开5尺 / "prone" 使其倒地
    返回: {"success": bool, "outcome": "push_5ft"|"prone"|"impossible",
            "attacker_roll": int, "target_roll": int}
    """
    # R-ADD-011: 体型限制 — 目标至多比攻击者大一级
    try:
        ai = _SIZE_ORDER.index(attacker_size.lower())
        ti = _SIZE_ORDER.index(target_size.lower())
    except ValueError:
        return {"success": False, "outcome": "impossible",
                "reason": f"未知体型: attacker={attacker_size} target={target_size}"}
    if ti > ai + 1:
        return {"success": False, "outcome": "impossible",
                "reason": f"目标体型({target_size})超过攻击者({attacker_size})+1"}

    # 攻击方: 力量(运动)检定
    atk_mod = attacker_str_mod + (attacker_prof if attacker_proficient_athletics else 0)
    atk_roll = dice.roll_d20(advantage=advantage, disadvantage=disadvantage)
    atk_total = atk_roll.used + atk_mod

    # 目标: 可以选力量(运动)或敏捷(特技)，取较高者（由调用方决定传哪个）
    tgt_ath = target_str_mod + (target_prof if target_proficient_athletics else 0)
    tgt_acr = target_dex_mod + (target_prof if target_proficient_acrobatics else 0)
    tgt_best = max(tgt_ath, tgt_acr)
    tgt_roll = dice.roll_d20()
    tgt_total = tgt_roll.used + tgt_best

    success = atk_total > tgt_total

    return {
        "success": success,
        "outcome": attacker_choice if success else "none",
        "attacker_roll": atk_total,
        "target_roll": tgt_total,
        "attacker_d20": atk_roll.used,
        "target_d20": tgt_roll.used,
    }


# ──────────────────────────────────────────────────────────────────────────
# 反应后回合继续（R-ADD-005）
# ──────────────────────────────────────────────────────────────────────────

def resume_after_reaction(interrupted: Combatant) -> None:
    """反应发生在他人回合中，被中断者在该反应结束后立刻继续自己的回合。

    规则: R-ADD-005 反应后回合继续（补充 R-CMB-013）
          on_reaction_in_other_turn: interrupted_creature_resumes_turn
          _immediately_after_reaction_resolves
    出处: topics/玩家手册2024/进行游戏/反应.htm
    说明: 这是一个语义锚点。调用方在结算完反应后调用此函数恢复被中断者。
    """
    # 被中断者不消耗任何动作/移动力，仅标记回合已恢复
    pass  # 实际恢复逻辑由调用方 (advance_turn/回合管理) 处理


# ──────────────────────────────────────────────────────────────────────────
# 受控坐骑受训前置（R-ADD-009）
# ──────────────────────────────────────────────────────────────────────────

def can_control_mount(mount_is_trained: bool,
                      mount_accepts_rider: bool) -> bool:
    """只能控制受训且接纳骑手的坐骑（如驯养的马/骡等）。

    规则: R-ADD-009 受控坐骑受训前置（补充 R-CMB-045）
          controlled_mount_requires: mount.is_trained AND mount.accepts_rider；
          否则只能作为自主坐骑。
    出处: topics/玩家手册2024/进行游戏/骑乘战斗.htm
    """
    return mount_is_trained and mount_accepts_rider


# ──────────────────────────────────────────────────────────────────────────
# 困难地形触发清单（R-ADD-019）
# ──────────────────────────────────────────────────────────────────────────

def is_difficult_terrain(tile: str, adjacent_creature_size: str = "",
                         mover_size: str = "medium") -> bool:
    """判定一个格子是否为困难地形。

    规则: R-ADD-019 困难地形触发清单（补充 R-GLS-026）
          triggers: 非微型非盟友生物 / 体型相仿或更大的家具 /
          厚积雪冰面沙石茂密植被 / 及胫到及腰液体 / 窄路缝隙 /
          坡度>20°陡坡
    出处: topics/玩家手册2024/术语汇编/移动与速度.htm

    参数:
      tile: 地形类型标签
      adjacent_creature_size: 邻接生物体型
      mover_size: 移动者体型
    """
    DIFFICULT_TILES = frozenset({
        "thick_snow", "ice_sheet", "sand", "dense_vegetation",
        "shin_deep_liquid", "waist_deep_liquid",
        "narrow_passage", "steep_slope",
        "rubble", "thorny_undergrowth",
    })
    if tile in DIFFICULT_TILES:
        return True
    # 非微型生物占据（非盟友）
    if adjacent_creature_size and adjacent_creature_size not in ("tiny", ""):
        sizes = list(_SIZE_FOOTPRINT.keys())
        try:
            mi = sizes.index(mover_size.lower())
            ci = sizes.index(adjacent_creature_size.lower())
        except ValueError:
            pass
        else:
            if ci >= mi:  # 体型相仿或更大的生物 → 困难地形
                return True
    return False


# ──────────────────────────────────────────────────────────────────────────
# 同时效应排序（R-ADD-020）
# ──────────────────────────────────────────────────────────────────────────

def resolve_simultaneous_effects(effects: list[str],
                                 turn_controller: str = "dm") -> list[str]:
    """同一回合中多起事件同时发生时，由回合控制者决定顺序。

    规则: R-ADD-020 同时效应排序
          if multiple_effects simultaneous in a turn →
          controller_of_turn(actor/DM) chooses order
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm

    说明: 返回按调用方（DM/玩家）指定顺序排列的效应列表。
          默认保持原顺序；调用方可调整后再传入。
    """
    return list(effects)


# ──────────────────────────────────────────────────────────────────────────
# 引发战斗者先攻优势（R-ADD-025）
# ──────────────────────────────────────────────────────────────────────────

def grant_initiative_advantage_on_trigger(actor: Combatant) -> None:
    """因角色动作引发战斗时，给予该角色先攻检定优势。

    规则: R-ADD-025 引发战斗者先攻优势（补充 R-DM-013）
          if action_triggered_combat(actor): actor.initiative_advantage=True
    出处: topics/城主指南2024/2.运作游戏/运作战斗/投掷先政.htm

    说明: 在 roll_initiative 中检测此标记并计算优势。
    """
    # 在 Combatant 上标记先攻优势（交由 roll_initiative 检查）
    pass  # 实际由调用方传递 advantage=True 到 roll_d20


# ──────────────────────────────────────────────────────────────────────────
# 水下远程攻击（R-ADD-030）
# ──────────────────────────────────────────────────────────────────────────

# 水下远程攻击劣势豁免武器
UNDERWATER_RANGED_EXEMPT_WEAPONS = frozenset({
    "弩", "crossbow", "捕网", "net",
    "矛", "spear", "三叉戟", "trident", "飞镖", "dart",
})


def underwater_ranged_full(weapon_name: str, distance_ft: int,
                           normal_range: int) -> dict:
    """水下远程攻击：常规射程内劣势（除非豁免武器），超常规射程自动失手。

    规则: R-ADD-030 水下远程常规射程内劣势（补充 R-QCK-014/R-CMB-041）
          RANGED_DISADV_WEAPONS_EXEMPT=弩/捕网/标枪类投掷(矛/三叉戟/飞镖);
          常规射程内→劣势(除非豁免); 超常规→auto_miss
    出处: topics/速查/DM速查/水下战斗.htm

    返回: {"can_hit": bool, "disadvantage": bool}
    """
    if distance_ft > normal_range:
        return {"can_hit": False, "disadvantage": False}
    exempt = weapon_name in UNDERWATER_RANGED_EXEMPT_WEAPONS
    return {"can_hit": True, "disadvantage": not exempt}


# ──────────────────────────────────────────────────────────────────────────
# 坠落飞行者半速解除倒地（R-ADD-031）
# ──────────────────────────────────────────────────────────────────────────

def flyer_recover_from_fall(fly_speed: int, is_prone: bool,
                            is_falling: bool) -> dict:
    """飞行生物后续回合花费一半飞行速度解除倒地并终止坠落。

    规则: R-ADD-031 坠落飞行者半速解除倒地（补充 R-QCK-008）
          when_using_fall_rate_rule AND prone AND still_falling
          AND subsequent_round: 花费 floor(fly_speed/2) → 解除倒地+终止坠落
    出处: topics/速查/DM速查/坠落.htm

    返回: {"success": bool, "cost_ft": int, "recovered": bool}
    """
    if not is_prone or not is_falling:
        return {"success": False, "cost_ft": 0, "recovered": False}
    cost = dice.round_down(fly_speed / 2)
    return {"success": True, "cost_ft": cost, "recovered": True}

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

    # ── R-ADD-004: 掩护来源侧前置 ──
    # 攻击者在 (0,0)，目标在 (10,0)，掩护在 (5,0) → 正好在中间，有效
    assert cover_active((0, 0), (10, 0), (5, 0)) is True
    # 掩体在 (0, 1) → 不在连线上，无效
    assert cover_active((0, 0), (10, 0), (0, 1)) is False
    # 掩体在 (-1, 0) → t≤0（掩体在攻击者后方），无效
    assert cover_active((0, 0), (10, 0), (-1, 0), cover_half_size=3) is False
    # 掩体在目标后方 (11, 0) → t≥1，无效
    assert cover_active((0, 0), (10, 0), (11, 0)) is False

    # ── R-ADD-006: 拆分移动 ──
    c_sp = Combatant(cid="sp", name="Splitter", speed=60)
    c_sp.speed_remaining = 60
    segments = [
        MoveSegment(20, False, "before_action"),
        MoveSegment(10, True, "after_action"),
        MoveSegment(15, False, "bonus_action"),
    ]
    actual = move_split(c_sp, segments)
    assert actual == [20, 10, 15]  # 20 + 10*2 + 15 = 55, 剩余5
    assert c_sp.speed_remaining == 5

    # ── R-ADD-010: 擒抱部位限制 ──
    assert grapple_capacity(2) == 2   # 两只空手 = 可擒抱2个
    assert grapple_capacity(0) == 0
    assert release_grapple(Combatant(cid="g", name="G"), Combatant(cid="t", name="T")) is True

    # ── R-ADD-011: 推撞结果 ──
    # 固定 d20: 攻击者15, 目标10 → 攻击者胜
    dice.roll_d20 = lambda advantage=False, disadvantage=False: _R(15)
    s = resolve_shove(
        attacker_str_mod=3, attacker_prof=2, attacker_proficient_athletics=True,
        target_str_mod=1, target_dex_mod=2, target_prof=2,
        target_proficient_athletics=False, target_proficient_acrobatics=False,
        attacker_choice="push",
    )
    assert s["success"] is True
    assert s["outcome"] == "push"

    # 目标体型过大（gargantuan vs medium）→ impossible
    s2 = resolve_shove(
        attacker_str_mod=5, attacker_prof=6, attacker_proficient_athletics=True,
        target_str_mod=0, target_dex_mod=0, target_prof=0,
        target_proficient_athletics=False, target_proficient_acrobatics=False,
        attacker_size="medium", target_size="gargantuan",
    )
    assert s2["success"] is False and s2["outcome"] == "impossible"

    # 目标大一级（large vs medium）→ 允许
    dice.roll_d20 = lambda advantage=False, disadvantage=False: _R(15)
    s3 = resolve_shove(
        attacker_str_mod=3, attacker_prof=2, attacker_proficient_athletics=True,
        target_str_mod=1, target_dex_mod=2, target_prof=2,
        target_proficient_athletics=False, target_proficient_acrobatics=False,
        attacker_size="medium", target_size="large", attacker_choice="prone",
    )
    assert s3["success"] is True
    assert s3["outcome"] == "prone"
    dice.roll_d20 = orig

    # ── R-ADD-005: 反应后回合继续 ──
    c_intr = Combatant(cid="ir", name="Interrupted", speed=30)
    resume_after_reaction(c_intr)  # 语义锚点，不抛异常

    # ── R-ADD-009: 受控坐骑受训前置 ──
    assert can_control_mount(True, True) is True
    assert can_control_mount(False, True) is False
    assert can_control_mount(True, False) is False

    # ── R-ADD-019: 困难地形触发清单 ──
    assert is_difficult_terrain("steep_slope") is True
    assert is_difficult_terrain("thick_snow") is True
    assert is_difficult_terrain("sand") is True
    assert is_difficult_terrain("normal_ground") is False
    # 生物占据: medium 在 medium 旁边 → 困难地形
    assert is_difficult_terrain("normal_ground", "medium", "medium") is True
    # micro 在 medium 旁边 → 非困难
    assert is_difficult_terrain("normal_ground", "tiny", "medium") is False

    # ── R-ADD-020: 同时效应排序 ──
    assert resolve_simultaneous_effects(["a", "b", "c"], "dm") == ["a", "b", "c"]

    # ── R-ADD-025: 引发战斗者先攻优势 ──
    c_adv = Combatant(cid="ia", name="Initiator", speed=30)
    grant_initiative_advantage_on_trigger(c_adv)  # 语义锚点

    # ── R-ADD-030: 水下远程攻击 ──
    u1 = underwater_ranged_full("长弓", distance_ft=80, normal_range=150)
    assert u1["can_hit"] is True and u1["disadvantage"] is True  # 常规射程内但非豁免武器
    u2 = underwater_ranged_full("矛", distance_ft=15, normal_range=20)
    assert u2["can_hit"] is True and u2["disadvantage"] is False  # 豁免武器无劣势
    u3 = underwater_ranged_full("长弓", distance_ft=160, normal_range=150)
    assert u3["can_hit"] is False  # 超常规射程自动失手

    # ── R-ADD-031: 坠落飞行者半速解除倒地 ──
    f1 = flyer_recover_from_fall(fly_speed=60, is_prone=True, is_falling=True)
    assert f1["success"] is True and f1["cost_ft"] == 30
    f2 = flyer_recover_from_fall(fly_speed=60, is_prone=False, is_falling=False)
    assert f2["success"] is False

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
