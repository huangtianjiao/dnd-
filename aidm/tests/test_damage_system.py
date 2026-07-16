"""伤害结算系统单元测试 — engine/damage.py

验证规则点:
  R-QCK-002 伤害管线顺序: 免疫→0 → 数值修正 → 抗性减半 → 易伤翻倍 → 下限0
  R-DMG-006 免疫 → 0
  R-DMG-003 抗性减半(向下取整) / 易伤翻倍
  R-DMG-002 伤害下限为0
  R-CMB-029 重击骰数翻倍(常数不加倍)
  R-DMG-009 临时HP优先扣除
  R-DMG-010 临时HP不叠加(取较大者)
  R-DMG-020 治疗不超过上限
  R-DMG-014 过量伤害致死
  R-DMG-017 死亡豁免检定 (≥10成功, 天然1两次失败, 天然20恢复1HP, 3成功稳定/3失败死亡)

运行:
  PYTHONPATH=src python tests/test_damage_system.py
  PYTHONPATH=src python -m pytest tests/test_damage_system.py -v
"""

from __future__ import annotations

import os
import sys

_SRC = os.path.join(os.path.dirname(__file__), "..", "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from aidm.engine import damage, dice


# ──────────────────────────────────────────────────────────────────────────
# 伤害管线
# ──────────────────────────────────────────────────────────────────────────

def test_apply_damage_pipeline_immunity():
    """免疫 → 0。R-DMG-006"""
    r = damage.apply_damage_pipeline(28, "fire", immunities={"fire"})
    assert r.final == 0
    assert r.immune is True


def test_apply_damage_pipeline_wildcard_immunity():
    """通配免疫 '*' → 0。"""
    r = damage.apply_damage_pipeline(28, "fire", immunities={"*"})
    assert r.final == 0


def test_apply_damage_pipeline_resistance():
    """抗性减半(向下取整)。R-DMG-003"""
    # 10 火焰，火焰抗性 → floor(10/2) = 5
    r = damage.apply_damage_pipeline(10, "fire", resistances={"fire"})
    assert r.final == 5
    # 11 火焰 → floor(11/2) = 5
    r = damage.apply_damage_pipeline(11, "fire", resistances={"fire"})
    assert r.final == 5


def test_apply_damage_pipeline_vulnerability():
    """易伤翻倍。R-DMG-003"""
    r = damage.apply_damage_pipeline(10, "fire", vulnerabilities={"fire"})
    assert r.final == 20


def test_apply_damage_pipeline_flat_modifier():
    """数值修正(加值/减值)。R-QCK-002 step2"""
    # 28 - 5 = 23
    r = damage.apply_damage_pipeline(28, "fire", flat_modifiers=[-5])
    assert r.final == 23


def test_apply_damage_pipeline_full_example():
    """官方算例: 28火焰 -5灵光 全抗 火易伤 → 22。
    (28-5)=23 → floor(23/2)=11 → 11×2=22
    """
    r = damage.apply_damage_pipeline(
        28, "fire",
        flat_modifiers=[-5],
        resistances={"*"},
        vulnerabilities={"fire"},
    )
    assert r.final == 22


def test_apply_damage_pipeline_floor_zero():
    """伤害下限为0。R-DMG-002"""
    # 3 - 10 = -7 → max(0, -7) = 0
    r = damage.apply_damage_pipeline(3, "fire", flat_modifiers=[-10])
    assert r.final == 0


# ──────────────────────────────────────────────────────────────────────────
# roll_damage
# ──────────────────────────────────────────────────────────────────────────

def test_roll_damage_range():
    """匕首 1d4+力3 → 4~7。"""
    req = damage.DamageRequest(
        dice_expr="1d4",
        damage_type="piercing",
        ability_mod=3,
        add_mod=True,
    )
    rd = damage.roll_damage(req)
    assert 4 <= rd.final <= 7
    assert len(rd.dice_rolls) == 1


def test_roll_damage_crit_doubles():
    """重击骰翻倍(常数不加倍)。R-CMB-029"""
    req = damage.DamageRequest(
        dice_expr="2d6",
        damage_type="slashing",
        crit=True,
    )
    rc = damage.roll_damage(req)
    assert len(rc.dice_rolls) == 4   # 2d6 翻倍为 4d6


# ──────────────────────────────────────────────────────────────────────────
# HP / 临时HP / 治疗
# ──────────────────────────────────────────────────────────────────────────

def test_apply_damage_to_hp_temp_first():
    """临时HP优先扣: 5临时HP 受7伤 → 失5临时再失2HP。R-DMG-009"""
    hp, temp = damage.apply_damage_to_hp(hp=10, temp_hp=5, max_hp=20, dmg=7)
    assert hp == 8
    assert temp == 0


def test_apply_damage_to_hp_small_damage():
    """小伤害只扣临时HP: 5临时 受3伤 → 临时剩2。"""
    hp, temp = damage.apply_damage_to_hp(hp=10, temp_hp=5, max_hp=20, dmg=3)
    assert hp == 10
    assert temp == 2


def test_grant_temp_hp_take_larger():
    """临时HP不叠加，取较大者。R-DMG-010"""
    assert damage.grant_temp_hp(10, 12) == 12
    assert damage.grant_temp_hp(15, 10) == 15
    assert damage.grant_temp_hp(0, 8) == 8


def test_apply_healing_capped():
    """治疗不超过上限。R-DMG-020"""
    # cur14 heal8 max20 → min(20,22)=20
    assert damage.apply_healing(14, 20, 8) == 20
    # cur18 heal5 max20 → min(20,23)=20
    assert damage.apply_healing(18, 20, 5) == 20
    # cur5 heal3 max20 → 8
    assert damage.apply_healing(5, 20, 3) == 8


# ──────────────────────────────────────────────────────────────────────────
# 过量伤害致死
# ──────────────────────────────────────────────────────────────────────────

def test_check_massive_damage_true():
    """过量伤害致死: max12 cur6 dmg18 → overflow=12 ≥ 12 → 死亡。R-DMG-014"""
    assert damage.check_massive_damage(current_hp=6, max_hp=12, dmg=18) is True


def test_check_massive_damage_false():
    """未达致死阈值。"""
    # overflow=4 < 12
    assert damage.check_massive_damage(current_hp=6, max_hp=12, dmg=10) is False


def test_check_hp_max_zero_death():
    """HP上限归0则死亡。R-DMG-013"""
    assert damage.check_hp_max_zero_death(0) is True
    assert damage.check_hp_max_zero_death(-5) is True
    assert damage.check_hp_max_zero_death(1) is False


# ──────────────────────────────────────────────────────────────────────────
# 死亡豁免
# ──────────────────────────────────────────────────────────────────────────

def _fake_die(value):
    return lambda s: value


def test_death_save_success():
    """≥10 → 一次成功。R-DMG-017"""
    orig = dice.roll_die
    dice.roll_die = _fake_die(15)
    t = damage.DeathTracker()
    result = damage.death_save(t)
    assert t.successes == 1
    assert result["roll"] == 15
    dice.roll_die = orig


def test_death_save_failure():
    """<10 → 一次失败。R-DMG-017"""
    orig = dice.roll_die
    dice.roll_die = _fake_die(5)
    t = damage.DeathTracker()
    damage.death_save(t)
    assert t.failures == 1
    dice.roll_die = orig


def test_death_save_natural_1():
    """天然1 → 两次失败。R-DMG-017"""
    orig = dice.roll_die
    dice.roll_die = _fake_die(1)
    t = damage.DeathTracker()
    damage.death_save(t)
    assert t.failures == 2
    dice.roll_die = orig


def test_death_save_natural_20():
    """天然20 → 恢复1HP，计数归零。R-DMG-017"""
    orig = dice.roll_die
    dice.roll_die = _fake_die(20)
    t = damage.DeathTracker()
    result = damage.death_save(t)
    assert result["regain_hp"] == 1
    assert t.successes == 0
    assert t.failures == 0
    dice.roll_die = orig


def test_death_save_three_successes_stable():
    """3次成功 → 稳定。R-DMG-017"""
    orig = dice.roll_die
    t = damage.DeathTracker()
    dice.roll_die = _fake_die(15)
    damage.death_save(t)  # 1 success
    damage.death_save(t)  # 2 successes
    result = damage.death_save(t)  # 3 successes → stable
    assert t.stable is True
    assert result.get("stable") is True or t.successes >= 3
    dice.roll_die = orig


def test_death_save_three_failures_dead():
    """3次失败 → 死亡。R-DMG-017"""
    orig = dice.roll_die
    t = damage.DeathTracker()
    dice.roll_die = _fake_die(5)
    damage.death_save(t)  # 1 failure
    damage.death_save(t)  # 2 failures
    damage.death_save(t)  # 3 failures → dead
    assert t.dead is True
    dice.roll_die = orig


def test_death_tracker_reset():
    """reset() 归零成功和失败计数。"""
    t = damage.DeathTracker()
    t.successes = 2
    t.failures = 1
    t.reset()
    assert t.successes == 0
    assert t.failures == 0


def test_damage_at_zero_hp():
    """HP0受伤害记失败(重击记两次)；≥上限死。R-DMG-018"""
    t = damage.DeathTracker()
    res = damage.damage_at_zero_hp(t, dmg=5, is_crit=False, max_hp=20)
    assert res["failures_added"] == 1
    assert t.failures == 1

    # 重击记两次
    t2 = damage.DeathTracker()
    res2 = damage.damage_at_zero_hp(t2, dmg=5, is_crit=True, max_hp=20)
    assert res2["failures_added"] == 2
    assert t2.failures == 2


def test_damage_at_zero_hp_lethal():
    """伤害≥上限 → 死亡。R-DMG-018"""
    t = damage.DeathTracker()
    res = damage.damage_at_zero_hp(t, dmg=25, is_crit=False, max_hp=20)
    assert res["dead"] is True
    assert t.dead is True


def test_reset_death_counts_on_recovery():
    """恢复HP时死亡豁免计数归零。R-ADD-008"""
    t = damage.DeathTracker()
    t.successes = 2
    t.failures = 1
    t.stable = True
    damage.reset_death_counts_on_recovery(t)
    assert t.successes == 0
    assert t.failures == 0
    assert t.stable is False
    assert t.dead is False


# ──────────────────────────────────────────────────────────────────────────
# 数据卡记法
# ──────────────────────────────────────────────────────────────────────────

def test_resolve_stat_block_fixed():
    """数据卡固定值: '4(1d4+2)' fixed → 4。R-GLS-086"""
    assert damage.resolve_stat_block("4(1d4+2)", mode="fixed") == 4


def test_resolve_stat_block_roll():
    """数据卡掷骰: '4(1d4+2)' roll → 1d4+2 的结果。"""
    r = damage.resolve_stat_block("4(1d4+2)", mode="roll")
    assert 3 <= r <= 6   # 1d4(1-4) + 2 = 3-6


def test_resolve_stat_block_plain():
    """无括号表达式直接掷骰。"""
    r = damage.resolve_stat_block("1d6", mode="roll")
    assert 1 <= r <= 6


# ──────────────────────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────────────────────

def main():
    """运行所有测试。"""
    tests = [
        test_apply_damage_pipeline_immunity,
        test_apply_damage_pipeline_wildcard_immunity,
        test_apply_damage_pipeline_resistance,
        test_apply_damage_pipeline_vulnerability,
        test_apply_damage_pipeline_flat_modifier,
        test_apply_damage_pipeline_full_example,
        test_apply_damage_pipeline_floor_zero,
        test_roll_damage_range,
        test_roll_damage_crit_doubles,
        test_apply_damage_to_hp_temp_first,
        test_apply_damage_to_hp_small_damage,
        test_grant_temp_hp_take_larger,
        test_apply_healing_capped,
        test_check_massive_damage_true,
        test_check_massive_damage_false,
        test_check_hp_max_zero_death,
        test_death_save_success,
        test_death_save_failure,
        test_death_save_natural_1,
        test_death_save_natural_20,
        test_death_save_three_successes_stable,
        test_death_save_three_failures_dead,
        test_death_tracker_reset,
        test_damage_at_zero_hp,
        test_damage_at_zero_hp_lethal,
        test_reset_death_counts_on_recovery,
        test_resolve_stat_block_fixed,
        test_resolve_stat_block_roll,
        test_resolve_stat_block_plain,
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
    print(f"伤害系统测试: {passed} 通过, {failed} 失败")
    print(f"{'='*50}")
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
