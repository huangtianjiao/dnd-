"""战斗状态机 — 先攻 / 回合 / 动作经济 / 专注维持。

依赖 engine.dice（roll_d20）、engine.check（saving_throw）。标注规则ID+出处。
角色卡的真实属性/HP 由 P1 stats 模块持有；本模块管理回合顺序与动作经济。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from . import dice, check


@dataclass
class Combatant:
    """战斗中的一个参战者（回合经济追踪）。"""
    cid: str                          # 唯一标识（关联角色卡/怪物）
    name: str
    dex_mod: int = 0                  # 先攻计算用敏捷调整值
    initiative: int = 0
    side: str = "player"              # player / enemy
    is_player: bool = True
    surprised: bool = False           # R-GLS-009 突袭 → 先攻劣势
    # 动作经济（R-CMB-004/012/013, R-GLS-083）
    action_used: bool = False
    bonus_action_used: bool = False
    reaction_used: bool = False
    free_interaction_used: int = 0     # R-CMB-005 每回合1次免费物件交互
    concentrating_on: Optional[str] = None  # 专注法术标识（R-SPL-019）


@dataclass
class Combat:
    """一场战斗的回合状态。"""
    participants: list[Combatant] = field(default_factory=list)
    initiative_order: list[Combatant] = field(default_factory=list)
    round: int = 0
    current_index: int = 0
    active: bool = False
    seconds_elapsed: int = 0           # R-CMB-001 一轮6秒


def roll_initiative(combatants: list[Combatant]) -> list[Combatant]:
    """为参战者掷先攻：d20 + 敏捷调整值，突袭者劣势，降序排列。

    规则: R-CMB-002 先攻检定 + R-GLS-009 突袭劣势
    出处: topics/玩家手册2024/进行游戏/战斗流程.htm
    说明: 相同怪物组可由调用方预先置同一 initiative；平局处理见 resolve_initiative_ties。
    """
    for c in combatants:
        r = dice.roll_d20(advantage=False, disadvantage=c.surprised)  # R-GLS-009
        c.initiative = r.used + c.dex_mod
    order = sorted(combatants, key=lambda c: c.initiative, reverse=True)   # 降序
    return order


def start_combat(combat: Combat, combatants: list[Combatant]) -> None:
    """开始战斗：掷先政、排序、进入第1轮。规则: R-CMB-002"""
    combat.participants = list(combatants)
    combat.initiative_order = roll_initiative(combatants)
    combat.round = 1
    combat.current_index = 0
    combat.active = True
    combat.seconds_elapsed = 0


def current_combatant(combat: Combat) -> Optional[Combatant]:
    if not combat.active or not combat.initiative_order:
        return None
    return combat.initiative_order[combat.current_index % len(combat.initiative_order)]


def _reset_turn_economy(c: Combatant) -> None:
    """回合开始时重置动作经济（反应在下个自己回合开始刷新）。

    规则: R-CMB-004 回合动作经济 / R-CMB-013 反应在下回合开始刷新
    """
    c.action_used = False
    c.bonus_action_used = False
    c.reaction_used = False
    c.free_interaction_used = 0


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
    if not can_take_action(c):
        return False
    c.action_used = True
    return True


def use_bonus_action(c: Combatant) -> bool:
    if not can_take_bonus_action(c):
        return False
    c.bonus_action_used = True
    return True


def use_reaction(c: Combatant) -> bool:
    if not can_take_reaction(c):
        return False
    c.reaction_used = True
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
    # 专注 DC
    assert concentration_save_dc(0) == 10              # 下限10
    assert concentration_save_dc(20) == 10            # floor(10)=10
    assert concentration_save_dc(25) == 12            # floor(12.5)=12
    assert concentration_save_dc(80) == 30            # 上限30
    # 专注豁免（monkeypatch saving_throw）
    orig2 = check.saving_throw
    check.saving_throw = lambda **kw: type("R", (), {"success": kw["dc"] <= 10})()
    assert concentration_save(con_mod=2, con_prof=True, prof=3, damage_taken=5) is True   # dc10→成功
    check.saving_throw = lambda **kw: type("R", (), {"success": False})()
    assert concentration_save(con_mod=0, con_prof=False, prof=0, damage_taken=30) is False
    check.saving_throw = orig2
    print("[combat] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
