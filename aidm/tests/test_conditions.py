"""状态条件引擎单元测试 — engine/conditions.py

验证规则点:
  R-GLS-043 状态不叠加原则（力竭例外）
  R-GLS-047 力竭等级累加 (0..6)
  R-GLS-050 失能性状态
  R-GLS-049/052/053/056/058 速度归0的状态
  R-GLS-044 目盲 / R-GLS-051 隐形 / R-GLS-055 倒地 / R-GLS-052 麻痹 / R-GLS-058 昏迷
  R-GLS-047 力竭 d20惩罚(等级×2) / 速度减少(等级×5)

运行:
  PYTHONPATH=src python tests/test_conditions.py
  PYTHONPATH=src python -m pytest tests/test_conditions.py -v
"""

from __future__ import annotations

import os
import sys

_SRC = os.path.join(os.path.dirname(__file__), "..", "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from aidm.engine import conditions


# ──────────────────────────────────────────────────────────────────────────
# ConditionState 增删查
# ──────────────────────────────────────────────────────────────────────────

def test_condition_add_new():
    """施加新状态 → True。R-GLS-043"""
    s = conditions.ConditionState()
    assert s.add("中毒") is True
    assert s.has("中毒") is True


def test_condition_add_duplicate():
    """重复施加同状态 → False（不叠加）。R-GLS-043"""
    s = conditions.ConditionState()
    s.add("中毒")
    assert s.add("中毒") is False


def test_condition_remove():
    """移除状态。"""
    s = conditions.ConditionState()
    s.add("中毒")
    assert s.remove("中毒") is True
    assert s.has("中毒") is False
    # 移除不存在的状态
    assert s.remove("中毒") is False


def test_condition_unknown_raises():
    """未知状态应抛 ValueError。"""
    s = conditions.ConditionState()
    try:
        s.add("不存在的状态")
        assert False, "应抛 ValueError"
    except ValueError:
        pass


# ──────────────────────────────────────────────────────────────────────────
# 力竭累加
# ──────────────────────────────────────────────────────────────────────────

def test_exhaustion_accumulates():
    """力竭可叠加，每次+1。R-GLS-047"""
    s = conditions.ConditionState()
    s.add("力竭"); assert s.exhaustion == 1
    s.add("力竭"); assert s.exhaustion == 2
    s.add("力竭"); assert s.exhaustion == 3


def test_exhaustion_capped_at_6():
    """力竭上限6级。R-GLS-047 / R-QCK-004"""
    s = conditions.ConditionState()
    for _ in range(10):
        s.add("力竭")
    assert s.exhaustion == 6


def test_exhaustion_death_at_6():
    """力竭6级即死。R-GLS-047 / R-QCK-004"""
    s = conditions.ConditionState()
    for _ in range(6):
        s.add("力竭")
    assert s.is_dead_from_exhaustion() is True


def test_exhaustion_remove():
    """力竭 remove → 等级-1。"""
    s = conditions.ConditionState()
    s.add("力竭"); s.add("力竭")
    assert s.remove("力竭") is True
    assert s.exhaustion == 1


def test_long_rest_reduce_exhaustion():
    """长休力竭-1级。R-GLS-047/R-QCK-004"""
    s = conditions.ConditionState()
    s.add("力竭"); s.add("力竭"); s.add("力竭")
    assert s.exhaustion == 3
    conditions.long_rest_reduce_exhaustion(s)
    assert s.exhaustion == 2


# ──────────────────────────────────────────────────────────────────────────
# 失能性状态
# ──────────────────────────────────────────────────────────────────────────

def test_is_incapacitated_by_paralysis():
    """麻痹 → 失能。R-GLS-050/052"""
    s = conditions.ConditionState({"麻痹"})
    assert s.is_incapacitated() is True


def test_is_incapacitated_by_stun():
    """震慑 → 失能。"""
    s = conditions.ConditionState({"震慑"})
    assert s.is_incapacitated() is True


def test_is_incapacitated_by_unconscious():
    """昏迷 → 失能。"""
    s = conditions.ConditionState({"昏迷"})
    assert s.is_incapacitated() is True


def test_not_incapacitated_by_poison():
    """中毒 → 不失能。"""
    s = conditions.ConditionState({"中毒"})
    assert s.is_incapacitated() is False


# ──────────────────────────────────────────────────────────────────────────
# d20 惩罚与速度
# ──────────────────────────────────────────────────────────────────────────

def test_d20_penalty_exhaustion():
    """力竭 d20惩罚 = 等级×2。R-GLS-047"""
    s = conditions.ConditionState()
    s.add("力竭"); s.add("力竭")
    assert conditions.d20_penalty(s) == 4   # 2级→-4


def test_speed_after_exhaustion():
    """力竭 速度 = base - 等级×5。R-GLS-047"""
    s = conditions.ConditionState()
    s.add("力竭"); s.add("力竭")
    assert conditions.speed_after_conditions(30, s) == 20   # 30-10


def test_speed_zero_states():
    """速度归0的状态: 受擒/麻痹/石化/束缚/昏迷。R-GLS-049/052/053/056/058"""
    for cond in ["受擒", "麻痹", "石化", "束缚", "昏迷"]:
        s = conditions.ConditionState({cond})
        assert conditions.speed_after_conditions(30, s) == 0, f"{cond} 应使速度归0"


# ──────────────────────────────────────────────────────────────────────────
# 攻击修饰符
# ──────────────────────────────────────────────────────────────────────────

def test_attack_modifiers_attacker_blinded():
    """攻击者目盲 → 劣势。R-GLS-044"""
    attacker = conditions.ConditionState({"目盲"})
    target = conditions.ConditionState()
    m = conditions.attack_modifiers(attacker, target)
    assert m.attacker_disadvantage is True


def test_attack_modifiers_attacker_poisoned():
    """攻击者中毒 → 劣势。R-GLS-054"""
    attacker = conditions.ConditionState({"中毒"})
    target = conditions.ConditionState()
    m = conditions.attack_modifiers(attacker, target)
    assert m.attacker_disadvantage is True


def test_attack_modifiers_target_blinded():
    """目标目盲 → 攻击优势。R-GLS-044"""
    attacker = conditions.ConditionState()
    target = conditions.ConditionState({"目盲"})
    m = conditions.attack_modifiers(attacker, target)
    assert m.attacker_advantage is True


def test_attack_modifiers_target_prone_close():
    """目标倒地 5尺内 → 优势。R-GLS-055"""
    attacker = conditions.ConditionState()
    target = conditions.ConditionState({"倒地"})
    m = conditions.attack_modifiers(attacker, target, distance_ft=5)
    assert m.attacker_advantage is True


def test_attack_modifiers_target_prone_far():
    """目标倒地 5尺外 → 劣势。R-GLS-055"""
    attacker = conditions.ConditionState()
    target = conditions.ConditionState({"倒地"})
    m = conditions.attack_modifiers(attacker, target, distance_ft=15)
    assert m.attacker_disadvantage is True


def test_attack_modifiers_target_paralyzed_auto_crit():
    """目标麻痹 5尺内 → 命中即重击。R-GLS-052"""
    attacker = conditions.ConditionState()
    target = conditions.ConditionState({"麻痹"})
    m = conditions.attack_modifiers(attacker, target, distance_ft=5)
    assert m.target_auto_crit_if_hit is True
    assert m.attacker_advantage is True


def test_attack_modifiers_target_unconscious_auto_crit():
    """目标昏迷 5尺内 → 命中即重击。R-GLS-058"""
    attacker = conditions.ConditionState()
    target = conditions.ConditionState({"昏迷"})
    m = conditions.attack_modifiers(attacker, target, distance_ft=5)
    assert m.target_auto_crit_if_hit is True


def test_attack_modifiers_attacker_invisible():
    """攻击者隐形 → 优势。R-GLS-051"""
    attacker = conditions.ConditionState({"隐形"})
    target = conditions.ConditionState()
    m = conditions.attack_modifiers(attacker, target)
    assert m.attacker_advantage is True


def test_attack_modifiers_target_invisible():
    """目标隐形 → 劣势。R-GLS-051"""
    attacker = conditions.ConditionState()
    target = conditions.ConditionState({"隐形"})
    m = conditions.attack_modifiers(attacker, target)
    assert m.attacker_disadvantage is True


def test_attack_modifiers_invisible_attacker_seen_no_advantage():
    """隐形攻击者被目标看见（如真实视觉）→ 不获得优势。R-GLS-051 2024隐形可见性条件"""
    attacker = conditions.ConditionState({"隐形"})
    target = conditions.ConditionState()
    m = conditions.attack_modifiers(attacker, target, attacker_visible_to_target=True)
    assert m.attacker_advantage is False


def test_attack_modifiers_invisible_target_seen_no_disadvantage():
    """隐形目标被攻击者看见（如盲视）→ 攻击其无劣势。R-GLS-051 2024隐形可见性条件"""
    attacker = conditions.ConditionState()
    target = conditions.ConditionState({"隐形"})
    m = conditions.attack_modifiers(attacker, target, target_visible_to_attacker=True)
    assert m.attacker_disadvantage is False


# ──────────────────────────────────────────────────────────────────────────
# 专注打断
# ──────────────────────────────────────────────────────────────────────────

def test_concentration_broken_on_unconscious():
    """陷入昏迷 → 打断专注。R-GLS-050"""
    s = conditions.ConditionState({"昏迷"})
    assert conditions.concentration_broken_on_state_change(s) is True


def test_concentration_not_broken_on_poison():
    """中毒不打断专注。"""
    s = conditions.ConditionState({"中毒"})
    assert conditions.concentration_broken_on_state_change(s) is False


# ──────────────────────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────────────────────

def main():
    """运行所有测试。"""
    tests = [
        test_condition_add_new,
        test_condition_add_duplicate,
        test_condition_remove,
        test_condition_unknown_raises,
        test_exhaustion_accumulates,
        test_exhaustion_capped_at_6,
        test_exhaustion_death_at_6,
        test_exhaustion_remove,
        test_long_rest_reduce_exhaustion,
        test_is_incapacitated_by_paralysis,
        test_is_incapacitated_by_stun,
        test_is_incapacitated_by_unconscious,
        test_not_incapacitated_by_poison,
        test_d20_penalty_exhaustion,
        test_speed_after_exhaustion,
        test_speed_zero_states,
        test_attack_modifiers_attacker_blinded,
        test_attack_modifiers_attacker_poisoned,
        test_attack_modifiers_target_blinded,
        test_attack_modifiers_target_prone_close,
        test_attack_modifiers_target_prone_far,
        test_attack_modifiers_target_paralyzed_auto_crit,
        test_attack_modifiers_target_unconscious_auto_crit,
        test_attack_modifiers_attacker_invisible,
        test_attack_modifiers_target_invisible,
        test_concentration_broken_on_unconscious,
        test_concentration_not_broken_on_poison,
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
    print(f"状态条件测试: {passed} 通过, {failed} 失败")
    print(f"{'='*50}")
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
