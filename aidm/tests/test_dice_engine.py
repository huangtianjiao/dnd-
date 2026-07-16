"""骰子引擎单元测试 — engine/dice.py

验证规则点:
  R-CHK-024 属性调整值公式 floor((score-10)/2)
  R-CHK-015 熟练加值表 (1-4级+2, 5-8级+3, ..., 17-20级+6)
  R-CHK-025 骰子表达式解析 NdM+K
  R-CMB-029 重击骰数翻倍（常数不加倍）
  R-CHK-004 优势与劣势掷骰（取高/取低）
  R-CHK-005 优势劣势抵消（同时存在只掷一d20）
  R-CHK-026 百分骰 d100
  R-CHK-027 D3 骰换算
  R-CHK-029 百分比概率判定
  R-GLS-005 向下取整

运行:
  PYTHONPATH=src python tests/test_dice_engine.py
  PYTHONPATH=src python -m pytest tests/test_dice_engine.py -v
"""

from __future__ import annotations

import os
import sys

_SRC = os.path.join(os.path.dirname(__file__), "..", "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from aidm.engine import dice


# ──────────────────────────────────────────────────────────────────────────
# 基础数值
# ──────────────────────────────────────────────────────────────────────────

def test_roll_die_range():
    """roll_die(sides) 结果在 [1, sides] 范围内。"""
    for sides in [4, 6, 8, 10, 12, 20, 100]:
        for _ in range(200):
            r = dice.roll_die(sides)
            assert 1 <= r <= sides, f"roll_die({sides})={r} 超出范围"


def test_roll_die_invalid():
    """roll_die(0) 和 roll_die(-1) 应抛 ValueError。"""
    try:
        dice.roll_die(0)
        assert False, "应抛 ValueError"
    except ValueError:
        pass


def test_round_down():
    """向下取整：即使小数>0.5也向下。"""
    assert dice.round_down(3.7) == 3
    assert dice.round_down(3.5) == 3
    assert dice.round_down(3.0) == 3
    assert dice.round_down(2.9) == 2
    assert dice.round_down(0.9) == 0
    assert dice.round_down(-1.5) == -2  # floor(-1.5) = -2


def test_ability_modifier():
    """属性调整值 = floor((score-10)/2)。"""
    # 边界值
    assert dice.ability_modifier(1) == -5    # 最小玩家属性
    assert dice.ability_modifier(2) == -4
    assert dice.ability_modifier(3) == -4
    assert dice.ability_modifier(8) == -1
    assert dice.ability_modifier(9) == -1
    assert dice.ability_modifier(10) == 0    # 中线
    assert dice.ability_modifier(11) == 0
    assert dice.ability_modifier(12) == 1
    assert dice.ability_modifier(14) == 2
    assert dice.ability_modifier(18) == 4
    assert dice.ability_modifier(20) == 5    # 最大未魔法提升属性
    assert dice.ability_modifier(30) == 10   # 怪物最高


def test_proficiency_bonus():
    """熟练加值表: 1-4级+2, 5-8级+3, 9-12级+4, 13-16级+5, 17-20级+6。"""
    # T1 新手冒险者 (1-4级)
    assert dice.proficiency_bonus(1) == 2
    assert dice.proficiency_bonus(4) == 2
    # T2 成熟冒险者 (5-8级)
    assert dice.proficiency_bonus(5) == 3
    assert dice.proficiency_bonus(8) == 3
    # T3 力量超凡 (9-12级)
    assert dice.proficiency_bonus(9) == 4
    assert dice.proficiency_bonus(12) == 4
    # T4 英雄典范 (13-16级)
    assert dice.proficiency_bonus(13) == 5
    assert dice.proficiency_bonus(16) == 5
    # 传奇 (17-20级)
    assert dice.proficiency_bonus(17) == 6
    assert dice.proficiency_bonus(20) == 6
    # CR 小数
    assert dice.proficiency_bonus(0.5) == 2   # CR 1/2 → floor=0 → max(1,0)=1 → +2
    assert dice.proficiency_bonus(0.125) == 2  # CR 1/8
    # 高等级外推
    assert dice.proficiency_bonus(29) == 9
    assert dice.proficiency_bonus(30) == 9


# ──────────────────────────────────────────────────────────────────────────
# 骰子表达式解析
# ──────────────────────────────────────────────────────────────────────────

def test_parse_dice_expression_basic():
    """基本表达式解析。"""
    terms, const = dice.parse_dice_expression("3d8+5")
    assert terms == [(3, 8, 1)]
    assert const == 5


def test_parse_dice_expression_implicit_count():
    """d6 隐式 N=1。"""
    terms, _ = dice.parse_dice_expression("d6")
    assert terms == [(1, 6, 1)]


def test_parse_dice_expression_no_modifier():
    """2d6 无常数。"""
    terms, const = dice.parse_dice_expression("2d6")
    assert terms == [(2, 6, 1)]
    assert const == 0


def test_parse_dice_expression_subtraction():
    """1d4-1 减法。"""
    terms, const = dice.parse_dice_expression("1d4-1")
    assert terms == [(1, 4, 1)]
    assert const == -1


def test_parse_dice_expression_multiple_dice():
    """1d8+1d6+3 多骰组合。"""
    terms, const = dice.parse_dice_expression("1d8+1d6+3")
    assert terms == [(1, 8, 1), (1, 6, 1)]
    assert const == 3


def test_parse_dice_expression_constant():
    """纯定值 '1'。"""
    terms, const = dice.parse_dice_expression("1")
    assert terms == []
    assert const == 1


def test_parse_dice_expression_spaces():
    """表达式含空格应正确解析。"""
    terms, const = dice.parse_dice_expression("  2d6 + 3  ")
    assert terms == [(2, 6, 1)]
    assert const == 3


# ──────────────────────────────────────────────────────────────────────────
# 掷骰
# ──────────────────────────────────────────────────────────────────────────

def test_roll_dice_range():
    """3d8+5 结果在 [8, 29] 范围内。"""
    for _ in range(200):
        r = dice.roll_dice("3d8+5")
        assert 8 <= r.total <= 29, f"total={r.total} 超出范围"
        assert len(r.dice_rolls) == 3
        assert r.modifier == 5


def test_roll_dice_crit_doubles_dice():
    """重击时骰数翻倍，常数不加倍。R-CMB-029"""
    rc = dice.roll_dice("1d6+3", crit=True)
    assert len(rc.dice_rolls) == 2     # 1d6 翻倍为 2d6
    assert rc.modifier == 3             # 常数不变


def test_roll_dice_crit_multi_dice():
    """重击多骰翻倍。"""
    rc = dice.roll_dice("2d6", crit=True)
    assert len(rc.dice_rolls) == 4     # 2d6 翻倍为 4d6


# ──────────────────────────────────────────────────────────────────────────
# d20 与优劣势
# ──────────────────────────────────────────────────────────────────────────

def test_roll_d20_normal():
    """普通 d20 掷骰。"""
    r = dice.roll_d20()
    assert 1 <= r.used <= 20
    assert len(r.rolls) == 1
    assert r.mode == "normal"


def test_roll_d20_advantage():
    """优势取最大值。R-CHK-004"""
    r = dice.roll_d20(advantage=True)
    assert len(r.rolls) == 2
    assert r.used == max(r.rolls)
    assert r.mode == "advantage"


def test_roll_d20_disadvantage():
    """劣势取最小值。R-CHK-004"""
    r = dice.roll_d20(disadvantage=True)
    assert len(r.rolls) == 2
    assert r.used == min(r.rolls)
    assert r.mode == "disadvantage"


def test_roll_d20_advantage_and_disadvantage_cancels():
    """优势劣势同时存在→抵消，只掷一d20。R-CHK-005"""
    r = dice.roll_d20(advantage=True, disadvantage=True)
    assert len(r.rolls) == 1
    assert r.mode == "cancelled"


# ──────────────────────────────────────────────────────────────────────────
# 派生骰
# ──────────────────────────────────────────────────────────────────────────

def test_roll_d100_range():
    """d100 结果在 [1, 100] 范围内。"""
    for _ in range(200):
        r = dice.roll_d100()
        assert 1 <= r <= 100


def test_roll_d3_range():
    """d3 结果在 {1, 2, 3} 中。"""
    for _ in range(200):
        r = dice.roll_d3()
        assert r in (1, 2, 3)


def test_roll_percent_chance():
    """百分比概率判定。"""
    # 100% 必发生
    ok, roll = dice.roll_percent_chance(100)
    assert ok is True
    assert 1 <= roll <= 100
    # 0% 必不发生
    ok, _ = dice.roll_percent_chance(0)
    assert ok is False


def test_roll_random_table():
    """随机表掷骰查表。"""
    tbl = {(1, 50): "A", (51, 100): "B"}
    res, roll = dice.roll_random_table(tbl, "1d100")
    assert res in ("A", "B")
    assert 1 <= roll <= 100


# ──────────────────────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────────────────────

def main():
    """运行所有测试。"""
    tests = [
        test_roll_die_range,
        test_roll_die_invalid,
        test_round_down,
        test_ability_modifier,
        test_proficiency_bonus,
        test_parse_dice_expression_basic,
        test_parse_dice_expression_implicit_count,
        test_parse_dice_expression_no_modifier,
        test_parse_dice_expression_subtraction,
        test_parse_dice_expression_multiple_dice,
        test_parse_dice_expression_constant,
        test_parse_dice_expression_spaces,
        test_roll_dice_range,
        test_roll_dice_crit_doubles_dice,
        test_roll_dice_crit_multi_dice,
        test_roll_d20_normal,
        test_roll_d20_advantage,
        test_roll_d20_disadvantage,
        test_roll_d20_advantage_and_disadvantage_cancels,
        test_roll_d100_range,
        test_roll_d3_range,
        test_roll_percent_chance,
        test_roll_random_table,
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
    print(f"骰子引擎测试: {passed} 通过, {failed} 失败")
    print(f"{'='*50}")
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
