"""战斗状态机单元测试 — engine/combat.py

验证规则点:
  R-CMB-002 先攻检定 (d20+敏捷调整值)
  R-GLS-009 突袭劣势
  R-CMB-001 一轮6秒
  R-CMB-004 回合动作经济
  R-CMB-005 免费物件交互(每回合1次)
  R-CMB-011 一次一个动作
  R-CMB-012 每回合至多1附赠动作
  R-CMB-013 反应经济
  R-CMB-030 回合移动上限=速度
  R-CMB-031 困难地形移动力消耗
  R-CMB-032 方格地图尺度(每格5尺) / 速度转格
  R-CMB-033 方格进入移动力
  R-CMB-037 生物体型与占据空间
  R-CMB-038 穿过其他生物的空间
  R-CMB-036 俯卧倒地
  R-GLS-013 专注维持检定DC = max(10, floor(dmg/2)) 上限30

运行:
  PYTHONPATH=src python tests/test_combat_flow.py
  PYTHONPATH=src python -m pytest tests/test_combat_flow.py -v
"""

from __future__ import annotations

import os
import sys

from aidm.engine import combat, dice, check


# ──────────────────────────────────────────────────────────────────────────
# 辅助
# ──────────────────────────────────────────────────────────────────────────

class _FakeRoll:
    """模拟 roll_d20 返回。"""
    def __init__(self, used):
        self.used = used
        self.rolls = [used]
        self.mode = "normal"


def _fake_d20(value):
    return lambda advantage=False, disadvantage=False: _FakeRoll(value)


# ──────────────────────────────────────────────────────────────────────────
# 先攻
# ──────────────────────────────────────────────────────────────────────────

def test_roll_initiative_basic():
    """先攻 = d20 + 敏捷调整值，降序排列。R-CMB-002"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(10)
    cs = [
        combat.Combatant(cid="a", name="A", dex_mod=2),
        combat.Combatant(cid="b", name="B", dex_mod=3, side="enemy", is_player=False),
    ]
    order = combat.roll_initiative(cs)
    # A: 10+2=12, B: 10+3=13 → B在前
    assert order[0].cid == "b"
    assert order[1].cid == "a"
    dice.roll_d20 = orig


def test_roll_initiative_surprised():
    """突袭者先攻劣势(取低)。R-GLS-009"""
    orig = dice.roll_d20
    # 正常掷15，劣势掷5
    dice.roll_d20 = lambda advantage=False, disadvantage=False: _FakeRoll(15 if not disadvantage else 5)
    surp = combat.Combatant(cid="s", name="S", dex_mod=0, surprised=True)
    combat.roll_initiative([surp])
    assert surp.initiative == 5   # 劣势取低
    dice.roll_d20 = orig


def test_roll_initiative_group_shared():
    """同组怪物共用先攻。R-CMB-002"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(10)
    g1 = combat.Combatant(cid="g1", name="Goblin", dex_mod=2, side="enemy",
                          is_player=False, group_id="gob")
    g2 = combat.Combatant(cid="g2", name="Goblin", dex_mod=2, side="enemy",
                          is_player=False, group_id="gob")
    combat.roll_initiative([g1, g2])
    assert g1.initiative == g2.initiative == 12   # 10+2=12
    dice.roll_d20 = orig


# ──────────────────────────────────────────────────────────────────────────
# 战斗流程
# ──────────────────────────────────────────────────────────────────────────

def test_start_combat():
    """开始战斗：掷先攻、排序、第1轮。R-CMB-001/002/004"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(10)
    cs = [
        combat.Combatant(cid="a", name="A", dex_mod=2),
        combat.Combatant(cid="b", name="B", dex_mod=3, side="enemy", is_player=False),
    ]
    combat_obj = combat.Combat()
    combat.start_combat(combat_obj, cs)
    assert combat_obj.round == 1
    assert combat_obj.active is True
    assert len(combat_obj.initiative_order) == 2
    cur = combat.current_combatant(combat_obj)
    assert cur is combat_obj.initiative_order[0]
    dice.roll_d20 = orig


def test_advance_turn():
    """推进回合：重置动作经济。R-CMB-004"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(10)
    cs = [
        combat.Combatant(cid="a", name="A", dex_mod=2),
        combat.Combatant(cid="b", name="B", dex_mod=3, side="enemy", is_player=False),
    ]
    combat_obj = combat.Combat()
    combat.start_combat(combat_obj, cs)
    cur = combat.current_combatant(combat_obj)
    # 消耗动作
    assert combat.use_action(cur) is True
    assert combat.can_take_action(cur) is False
    # 推进到下一参战者
    nxt = combat.advance_turn(combat_obj)
    assert nxt is combat_obj.initiative_order[1]
    # 新参战者动作经济已重置
    assert combat.can_take_action(nxt) is True
    dice.roll_d20 = orig


def test_advance_turn_new_round():
    """一轮结束→进入下一轮(+6秒)。R-CMB-001"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(10)
    cs = [
        combat.Combatant(cid="a", name="A", dex_mod=2),
        combat.Combatant(cid="b", name="B", dex_mod=3, side="enemy", is_player=False),
    ]
    combat_obj = combat.Combat()
    combat.start_combat(combat_obj, cs)
    # A的回合 → 推进到B
    combat.advance_turn(combat_obj)
    # B的回合 → 推进回A，第二轮
    combat.advance_turn(combat_obj)
    assert combat_obj.round == 2
    assert combat_obj.seconds_elapsed == 6
    dice.roll_d20 = orig


# ──────────────────────────────────────────────────────────────────────────
# 动作经济
# ──────────────────────────────────────────────────────────────────────────

def test_action_economy():
    """动作经济: 1动作 + 0-1附赠 + 0-1反应。R-CMB-011/012/013"""
    c = combat.Combatant(cid="t", name="T")
    assert combat.can_take_action(c) is True
    assert combat.can_take_bonus_action(c) is True
    assert combat.can_take_reaction(c) is True

    combat.use_action(c)
    combat.use_bonus_action(c)
    combat.use_reaction(c)

    assert combat.can_take_action(c) is False
    assert combat.can_take_bonus_action(c) is False
    assert combat.can_take_reaction(c) is False


def test_free_interaction_once_per_turn():
    """免费物件交互每回合1次。R-CMB-005"""
    c = combat.Combatant(cid="t", name="T")
    assert combat.use_free_interaction(c) is True   # 第一次免费
    assert combat.use_free_interaction(c) is False  # 第二个需 Utilize 动作


# ──────────────────────────────────────────────────────────────────────────
# 移动
# ──────────────────────────────────────────────────────────────────────────

def test_move_normal():
    """正常移动消耗移动力。R-CMB-030"""
    c = combat.Combatant(cid="m", name="M", speed=30)
    c.speed_remaining = c.speed
    moved = combat.move(c, distance_ft=10, difficult=False)
    assert moved == 10
    assert c.speed_remaining == 20


def test_move_difficult_terrain():
    """困难地形每尺双倍消耗。R-CMB-031"""
    c = combat.Combatant(cid="m", name="M", speed=30)
    c.speed_remaining = c.speed
    moved = combat.move(c, distance_ft=5, difficult=True)
    assert moved == 5
    assert c.speed_remaining == 20   # 5*2=10 消耗


def test_move_insufficient_speed():
    """移动力不足时按可承受最大距离移动。R-CMB-030"""
    c = combat.Combatant(cid="m", name="M", speed=30)
    c.speed_remaining = 10
    # 困难地形走10尺需要20移动力，只有10→走5尺
    moved = combat.move(c, distance_ft=10, difficult=True)
    assert moved == 5
    assert c.speed_remaining == 0


def test_speed_to_squares():
    """速度转格数: 30尺=6格, 25尺=5格。R-CMB-032"""
    assert combat.speed_to_squares(30) == 6
    assert combat.speed_to_squares(25) == 5
    assert combat.speed_to_squares(5) == 1


def test_enter_square_normal():
    """进入普通格子消耗1格(5尺)。R-CMB-033"""
    c = combat.Combatant(cid="e", name="E", speed=30)
    c.speed_remaining = 30
    assert combat.enter_square(c, difficult=False) == 1
    assert c.speed_remaining == 25


def test_enter_square_difficult():
    """进入困难格子消耗2格(10尺)。R-CMB-033"""
    c = combat.Combatant(cid="e", name="E", speed=30)
    c.speed_remaining = 30
    assert combat.enter_square(c, difficult=True) == 2
    assert c.speed_remaining == 20


# ──────────────────────────────────────────────────────────────────────────
# 体型与空间
# ──────────────────────────────────────────────────────────────────────────

def test_get_size_footprint():
    """体型占据空间。R-CMB-037"""
    assert combat.get_size_footprint("tiny") == (2.5, 0.25)
    assert combat.get_size_footprint("small") == (5.0, 1.0)
    assert combat.get_size_footprint("medium") == (5.0, 1.0)
    assert combat.get_size_footprint("large") == (10.0, 4.0)
    assert combat.get_size_footprint("huge") == (15.0, 9.0)
    assert combat.get_size_footprint("gargantuan") == (20.0, 16.0)


def test_can_pass_through_two_sizes_apart():
    """体型相差两级以上可穿过。R-CMB-038"""
    assert combat.can_pass_through("medium", "huge") is True   # 相差两级
    assert combat.can_pass_through("medium", "large") is False # 相差一级


def test_can_pass_through_ally():
    """盟友可穿过。R-CMB-038"""
    assert combat.can_pass_through("medium", "medium", is_ally=True) is True


def test_pass_cost_multiplier_tiny():
    """微型生物正常通过。R-CMB-038"""
    assert combat.pass_cost_multiplier("tiny", "medium") == 1


def test_pass_cost_multiplier_normal():
    """非微型非盟友→困难地形(2)。R-CMB-038"""
    assert combat.pass_cost_multiplier("medium", "huge", is_ally=False) == 2


# ──────────────────────────────────────────────────────────────────────────
# 俯卧倒地
# ──────────────────────────────────────────────────────────────────────────

def test_drop_prone_with_speed():
    """有速度时可俯卧。R-CMB-036"""
    assert combat.drop_prone(combat.Combatant(cid="p", name="P", speed=30)) is True


def test_drop_prone_no_speed():
    """速度为0时不能俯卧。R-CMB-036"""
    assert combat.drop_prone(combat.Combatant(cid="z", name="Z", speed=0)) is False


# ──────────────────────────────────────────────────────────────────────────
# 专注维持
# ──────────────────────────────────────────────────────────────────────────

def test_concentration_save_dc_min_10():
    """专注DC下限10。R-GLS-013"""
    assert combat.concentration_save_dc(0) == 10
    assert combat.concentration_save_dc(5) == 10   # floor(2.5)=2 < 10 → 10


def test_concentration_save_dc_normal():
    """正常专注DC。R-GLS-013"""
    assert combat.concentration_save_dc(20) == 10   # floor(10)=10
    assert combat.concentration_save_dc(25) == 12   # floor(12.5)=12


def test_concentration_save_dc_max_30():
    """专注DC上限30。R-GLS-013"""
    assert combat.concentration_save_dc(80) == 30   # floor(40)=40 > 30 → 30


# ──────────────────────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────────────────────

def main():
    """运行所有测试。"""
    tests = [
        test_roll_initiative_basic,
        test_roll_initiative_surprised,
        test_roll_initiative_group_shared,
        test_start_combat,
        test_advance_turn,
        test_advance_turn_new_round,
        test_action_economy,
        test_free_interaction_once_per_turn,
        test_move_normal,
        test_move_difficult_terrain,
        test_move_insufficient_speed,
        test_speed_to_squares,
        test_enter_square_normal,
        test_enter_square_difficult,
        test_get_size_footprint,
        test_can_pass_through_two_sizes_apart,
        test_can_pass_through_ally,
        test_pass_cost_multiplier_tiny,
        test_pass_cost_multiplier_normal,
        test_drop_prone_with_speed,
        test_drop_prone_no_speed,
        test_concentration_save_dc_min_10,
        test_concentration_save_dc_normal,
        test_concentration_save_dc_max_30,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  ✓ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__}: {e}")
            failed += 1
    print(f"\n{'='*50}")
    print(f"战斗流程测试: {passed} 通过, {failed} 失败")
    print(f"{'='*50}")
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
