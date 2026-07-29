"""D20 检定系统单元测试 — engine/check.py

验证规则点:
  R-CHK-009 范例难度等级DC表 (5/10/15/20/25/30)
  R-DM-002 豁免DC公式 (8+属性调整值+熟练加值)
  R-CHK-005 优势劣势抵消
  R-CHK-010 属性检定
  R-CHK-011 豁免检定 (waive=放弃→直接失败)
  R-CMB-017 攻击检定命中判定 (≥AC则命中)
  R-CMB-022 天然20必命中与重击
  R-CMB-023 天然1必失手

运行:
  PYTHONPATH=src python tests/test_check_system.py
  PYTHONPATH=src python -m pytest tests/test_check_system.py -v
"""

from __future__ import annotations

import os
import sys

_SRC = os.path.join(os.path.dirname(__file__), "..", "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from aidm.engine import check, dice


# ──────────────────────────────────────────────────────────────────────────
# DC 设定
# ──────────────────────────────────────────────────────────────────────────

def test_dc_by_label():
    """范例DC表: 非常容易5/容易10/中等15/困难20/非常困难25/近乎不可能30。"""
    assert check.dc_by_label("非常容易") == 5
    assert check.dc_by_label("容易") == 10
    assert check.dc_by_label("中等") == 15
    assert check.dc_by_label("困难") == 20
    assert check.dc_by_label("非常困难") == 25
    assert check.dc_by_label("近乎不可能") == 30


def test_dc_by_label_unknown():
    """未知难度描述应抛 ValueError。"""
    try:
        check.dc_by_label("超级难")
        assert False, "应抛 ValueError"
    except ValueError:
        pass


def test_calc_save_dc():
    """豁免DC = 8 + 属性调整值 + 熟练加值。R-DM-002"""
    # 3级法师 INT16(+3) 熟练+2 → DC = 8+3+2 = 13
    assert check.calc_save_dc(ability_mod=3, prof=2) == 13
    # 1级牧师 WIS16(+3) 熟练+2 → DC = 8+3+2 = 13
    assert check.calc_save_dc(ability_mod=3, prof=2) == 13
    # 5级圣武士 CHA16(+3) 熟练+3 → DC = 8+3+3 = 14
    assert check.calc_save_dc(ability_mod=3, prof=3) == 14


# ──────────────────────────────────────────────────────────────────────────
# 优劣势解析
# ──────────────────────────────────────────────────────────────────────────

def test_resolve_advantage_no_sources():
    """无优劣势来源 → (False, False)。"""
    assert check.resolve_advantage(0, 0) == (False, False)


def test_resolve_advantage_multiple_advantage():
    """多个优势仍只掷两d20（不叠加）。R-CHK-005"""
    assert check.resolve_advantage(3, 0) == (True, False)


def test_resolve_advantage_disadvantage():
    """劣势存在。"""
    assert check.resolve_advantage(0, 2) == (False, True)


def test_resolve_advantage_cancels():
    """优劣势同时存在→抵消。R-CHK-005"""
    assert check.resolve_advantage(1, 1) == (False, False)
    assert check.resolve_advantage(5, 3) == (False, False)


# ──────────────────────────────────────────────────────────────────────────
# 被动检定
# ──────────────────────────────────────────────────────────────────────────

def test_passive_check():
    """被动检定 = 10 + 所有适用调整值。R-DM-012"""
    # 被动察觉 = 10 + 感知(察觉)加值
    assert check.passive_check([3]) == 13     # WIS16(+3) → 被动察觉 13
    assert check.passive_check([5]) == 15     # 熟练+属性
    assert check.passive_check([3, 2]) == 15  # 多个修正
    assert check.passive_check([]) == 10      # 无修正


# ──────────────────────────────────────────────────────────────────────────
# 属性检定
# ──────────────────────────────────────────────────────────────────────────

def _fake_d20(value):
    """Monkeypatch roll_d20 返回固定值。"""
    class _R:
        used = value
        rolls = [value]
        mode = "normal"
    return lambda advantage=False, disadvantage=False: _R()


def test_ability_check_success():
    """属性检定成功: d20+修正 ≥ DC。R-CHK-010"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(15)
    r = check.ability_check(mod=3, prof=2, proficient=True, dc=18)
    # 15 + 3 + 2 = 20 ≥ 18 → 成功
    assert r.success is True
    assert r.total == 20
    assert r.margin == 2
    dice.roll_d20 = orig


def test_ability_check_failure():
    """属性检定失败: d20+修正 < DC。"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(5)
    r = check.ability_check(mod=3, prof=2, proficient=True, dc=15)
    # 5 + 3 + 2 = 10 < 15 → 失败
    assert r.success is False
    assert r.total == 10
    assert r.margin == -5
    dice.roll_d20 = orig


def test_ability_check_not_proficient():
    """非熟练检定不加熟练加值。"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(10)
    r = check.ability_check(mod=3, prof=2, proficient=False, dc=12)
    # 10 + 3 = 13 ≥ 12 → 成功
    assert r.success is True
    assert r.total == 13
    dice.roll_d20 = orig


def test_ability_check_exact_dc():
    """恰好达到DC也算成功 (≥)。"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(10)
    r = check.ability_check(mod=0, prof=0, proficient=False, dc=10)
    assert r.success is True
    assert r.margin == 0
    dice.roll_d20 = orig


# ──────────────────────────────────────────────────────────────────────────
# 豁免检定
# ──────────────────────────────────────────────────────────────────────────

def test_ability_check_nat20_no_auto_success():
    """属性检定天然20不再自动成功（仅攻击/死亡豁免有此规则）。R-DM-010"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(20)
    # 调整值 -5, DC 20 → total = 20 + (-5) = 15 < 20 → 失败（即使天然20）
    r = check.ability_check(mod=-5, prof=0, proficient=False, dc=20)
    assert r.success is False
    assert r.d20 == 20
    assert r.total == 15
    dice.roll_d20 = orig


def test_ability_check_nat1_no_auto_fail():
    """属性检定天然1不再自动失败（仅攻击/死亡豁免有此规则）。R-DM-010"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(1)
    # 调整值 +15, DC 10 → total = 1 + 15 = 16 ≥ 10 → 成功（即使天然1）
    r = check.ability_check(mod=15, prof=0, proficient=False, dc=10)
    assert r.success is True
    assert r.d20 == 1
    assert r.total == 16
    dice.roll_d20 = orig


def test_saving_throw_nat20_no_auto_success():
    """豁免检定天然20不再自动成功。R-DM-010"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(20)
    # 调整值 -5, DC 20 → total = 15 < 20 → 失败
    r = check.saving_throw(mod=-5, prof=0, proficient=False, dc=20)
    assert r.success is False
    assert r.d20 == 20
    dice.roll_d20 = orig


def test_saving_throw_nat1_no_auto_fail():
    """豁免检定天然1不再自动失败。R-DM-010"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(1)
    # 调整值 +15, DC 10 → total = 16 ≥ 10 → 成功
    r = check.saving_throw(mod=15, prof=0, proficient=False, dc=10)
    assert r.success is True
    assert r.d20 == 1
    dice.roll_d20 = orig


def test_saving_throw_success():
    """豁免成功。R-CHK-011"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(12)
    r = check.saving_throw(mod=3, prof=2, proficient=True, dc=15)
    # 12 + 3 + 2 = 17 ≥ 15 → 成功
    assert r.success is True
    dice.roll_d20 = orig


def test_saving_throw_waive():
    """主动放弃豁免→直接失败。R-CHK-011"""
    r = check.saving_throw(mod=5, prof=3, proficient=True, dc=10, waive=True)
    assert r.success is False
    assert r.mode == "waived"


# ──────────────────────────────────────────────────────────────────────────
# 攻击检定
# ──────────────────────────────────────────────────────────────────────────

def test_attack_roll_hit():
    """攻击命中: d20+bonus ≥ AC。R-CMB-017"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(10)
    a = check.attack_roll(bonus=5, ac=15)
    # 10 + 5 = 15 ≥ 15 → 命中
    assert a.hit is True
    assert a.crit is False
    assert a.success is True
    dice.roll_d20 = orig


def test_attack_roll_miss():
    """攻击未命中: d20+bonus < AC。"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(5)
    a = check.attack_roll(bonus=5, ac=15)
    # 5 + 5 = 10 < 15 → 未中
    assert a.hit is False
    assert a.success is False
    dice.roll_d20 = orig


def test_attack_roll_natural_20():
    """天然20必命中+重击。R-CMB-022"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(20)
    a = check.attack_roll(bonus=0, ac=30)
    # 即使 AC=30，天然20必出
    assert a.hit is True
    assert a.crit is True
    assert a.success is True
    dice.roll_d20 = orig


def test_attack_roll_natural_1():
    """天然1必失手。R-CMB-023"""
    orig = dice.roll_d20
    dice.roll_d20 = _fake_d20(1)
    a = check.attack_roll(bonus=50, ac=5)
    # 即使 bonus=50，天然1必失
    assert a.hit is False
    assert a.crit is False
    assert a.success is False
    dice.roll_d20 = orig


def test_is_natural_20():
    assert check.is_natural_20(20) is True
    assert check.is_natural_20(19) is False


def test_is_natural_1():
    assert check.is_natural_1(1) is True
    assert check.is_natural_1(2) is False


# ──────────────────────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────────────────────

def main():
    """运行所有测试。"""
    tests = [
        test_dc_by_label,
        test_dc_by_label_unknown,
        test_calc_save_dc,
        test_resolve_advantage_no_sources,
        test_resolve_advantage_multiple_advantage,
        test_resolve_advantage_disadvantage,
        test_resolve_advantage_cancels,
        test_passive_check,
        test_ability_check_success,
        test_ability_check_failure,
        test_ability_check_not_proficient,
        test_ability_check_exact_dc,
        test_ability_check_nat20_no_auto_success,
        test_ability_check_nat1_no_auto_fail,
        test_saving_throw_nat20_no_auto_success,
        test_saving_throw_nat1_no_auto_fail,
        test_saving_throw_success,
        test_saving_throw_waive,
        test_attack_roll_hit,
        test_attack_roll_miss,
        test_attack_roll_natural_20,
        test_attack_roll_natural_1,
        test_is_natural_20,
        test_is_natural_1,
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
    print(f"检定系统测试: {passed} 通过, {failed} 失败")
    print(f"{'='*50}")
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
