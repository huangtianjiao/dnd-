"""规则书审计修复回归测试 — 2026-07 对照玩家手册2024源文审计发现的差异。

覆盖修复:
  1. R-ITM-015 武器精通第8词条「侵扰 Vex」(engine/mastery.py)
  2. R-SPL-002 法术位进度表 18-20 级 (data/spells.py，与 multiclass.py 对齐)
  3. R-ITM-015「迅击 Nick」双武器额外攻击不消耗附赠动作 (engine/actions.py)
  4. R-GLS-014 短休生命骰总恢复量至少1 (brain/rest.py)
  5. R-GLS-051 隐形可见性条件（见 test_conditions.py 补充用例）

运行:
  PYTHONPATH=src python -m pytest tests/test_rule_fixes.py -v
"""

from __future__ import annotations

import os
import sys

from aidm.brain import rest
from aidm.data import spells
from aidm.engine import actions, dice, mastery, multiclass
from aidm.engine.actions import WeaponProfile
from aidm.engine.combat import Combatant

# ──────────────────────────────────────────────────────────────────────────
# 1. 侵扰 Vex（R-ITM-015 第8精通词条）
# ──────────────────────────────────────────────────────────────────────────

def test_mastery_vex_on_hit():
    """侵扰：命中造成伤害 → 下次对该生物攻击优势（至下回合结束）。"""
    r = mastery.resolve_mastery("侵扰", hit=True)
    assert r["applied"] is True
    assert r["target_effect"] == "next_attack_against_target_advantage"
    assert r["duration"] == "until_next_turn_end"


def test_mastery_vex_on_miss():
    """侵扰：未命中不生效。"""
    r = mastery.resolve_mastery("侵扰", hit=False)
    assert r["applied"] is False


def test_all_equipment_masteries_resolvable():
    """equipment.py 武器表中出现的所有精通词条均能被 mastery 引擎识别。"""
    from aidm.data import equipment
    for name, entry in equipment.WEAPONS.items():
        m = entry.get("mastery", "")
        if not m:
            continue
        r = mastery.resolve_mastery(m, hit=True, attacker_ability_mod=3,
                                    attacker_prof=2, target_size="medium")
        assert r["effect"] != "unknown", f"武器 {name!r} 的精通 {m!r} 未被识别"


# ──────────────────────────────────────────────────────────────────────────
# 2. 法术位表 18-20 级（R-SPL-002，PHB2024 标准施法者表）
# ──────────────────────────────────────────────────────────────────────────

def test_spell_slots_level_18():
    """18级：5环=3。"""
    assert spells.max_spell_slots(18) == {1: 4, 2: 3, 3: 3, 4: 3, 5: 3,
                                          6: 1, 7: 1, 8: 1, 9: 1}


def test_spell_slots_level_19():
    """19级：6环=2。"""
    assert spells.max_spell_slots(19) == {1: 4, 2: 3, 3: 3, 4: 3, 5: 3,
                                          6: 2, 7: 1, 8: 1, 9: 1}


def test_spell_slots_level_20():
    """20级：7环=2。"""
    assert spells.max_spell_slots(20) == {1: 4, 2: 3, 3: 3, 4: 3, 5: 3,
                                          6: 2, 7: 2, 8: 1, 9: 1}


def test_spell_slots_consistent_with_multiclass_table():
    """spells.py 与 multiclass.py 的法术位表必须逐级一致（1-20级）。"""
    for lv in range(1, 21):
        assert spells.max_spell_slots(lv) == multiclass._SPELL_SLOTS_BY_LEVEL[lv], \
            f"{lv}级法术位表不一致"


# ──────────────────────────────────────────────────────────────────────────
# 3. 迅击 Nick 双武器（R-ITM-015：额外攻击并入攻击动作）
# ──────────────────────────────────────────────────────────────────────────

def _fixed_dice(monkeypatch, d20=15, dmg_total=4):
    """固定骰值，保证命中且伤害可断言。"""
    class _R20:
        def __init__(self):
            self.used, self.rolls, self.mode = d20, [d20], "normal"

    class _RD:
        def __init__(self, expr, crit):
            self.total, self.dice_rolls = dmg_total, [dmg_total]
            self.expression, self.modifier = expr, 0
            self.crit, self.notes = crit, ""

    monkeypatch.setattr(dice, "roll_d20",
                        lambda advantage=False, disadvantage=False: _R20())
    monkeypatch.setattr(dice, "roll_dice",
                        lambda expr, *, crit=False: _RD(expr, crit))


def test_two_weapon_nick_skips_bonus_action(monkeypatch):
    """有武器精通 + 副手匕首（精通=迅击）→ 额外攻击不消耗附赠动作。"""
    _fixed_dice(monkeypatch)
    a = Combatant(cid="n1", name="游侠", side="player")
    t = Combatant(cid="n1T", name="哥布林", side="enemy")
    main_w = WeaponProfile(name="弯刀", attack_bonus=5, damage_dice="1d6",
                           damage_type="挥砍", ability_mod=3)
    off_w = WeaponProfile(name="匕首", attack_bonus=5, damage_dice="1d4",
                          damage_type="穿刺", ability_mod=3)
    r = actions.action_two_weapon_attack(a, t, main_w, off_w, target_ac=10,
                                         has_weapon_mastery=True)
    assert r.success and r.extra["off_hand"]["attempted"]
    assert r.extra["nick_applied"] is True
    assert r.extra["bonus_action_used"] is False
    assert a.bonus_action_used is False        # 附赠动作仍可用于其他用途


def test_two_weapon_no_mastery_uses_bonus_action(monkeypatch):
    """无武器精通特性 → 副手攻击照常消耗附赠动作（即使武器精通词条为迅击）。"""
    _fixed_dice(monkeypatch)
    a = Combatant(cid="n2", name="平民", side="player")
    t = Combatant(cid="n2T", name="哥布林2", side="enemy")
    main_w = WeaponProfile(name="弯刀", attack_bonus=5, damage_dice="1d6",
                           damage_type="挥砍", ability_mod=3)
    off_w = WeaponProfile(name="匕首", attack_bonus=5, damage_dice="1d4",
                          damage_type="穿刺", ability_mod=3)
    r = actions.action_two_weapon_attack(a, t, main_w, off_w, target_ac=10)
    assert r.success and r.extra["off_hand"]["attempted"]
    assert r.extra.get("nick_applied") is False
    assert r.extra["bonus_action_used"] is True
    assert a.bonus_action_used is True


def test_two_weapon_mastery_but_offhand_not_nick(monkeypatch):
    """有武器精通但副手武器精通非迅击（短剑=侵扰）→ 仍消耗附赠动作。"""
    _fixed_dice(monkeypatch)
    a = Combatant(cid="n3", name="盗贼", side="player")
    t = Combatant(cid="n3T", name="哥布林3", side="enemy")
    main_w = WeaponProfile(name="匕首", attack_bonus=5, damage_dice="1d4",
                           damage_type="穿刺", ability_mod=3)
    off_w = WeaponProfile(name="短剑", attack_bonus=5, damage_dice="1d6",
                          damage_type="穿刺", ability_mod=3)
    r = actions.action_two_weapon_attack(a, t, main_w, off_w, target_ac=10,
                                         has_weapon_mastery=True)
    assert r.success and r.extra["off_hand"]["attempted"]
    assert r.extra.get("nick_applied") is False
    assert r.extra["bonus_action_used"] is True


# ──────────────────────────────────────────────────────────────────────────
# 4. 短休生命骰恢复总量至少1（R-GLS-014「至少1」）
# ──────────────────────────────────────────────────────────────────────────

class _Char:
    """短休测试用最小角色（鸭子类型）。"""

    def __init__(self, hp=5, hit_dice=3, con_mod=0, hit_die_faces=8):
        self.hp = hp
        self.hit_dice = hit_dice
        self.con_mod = con_mod
        self.hit_die_faces = hit_die_faces


def test_short_rest_minimum_one_hp(monkeypatch):
    """负体质：掷1 + con_mod(-3) = -2 → 总恢复量仍至少1。"""
    monkeypatch.setattr(dice, "roll_die", lambda faces: 1)
    c = _Char(con_mod=-3)
    r = rest.short_rest(c, hit_dice_to_spend=1)
    assert r["success"] is True
    assert r["hp_restored"] == 1


def test_short_rest_normal_restore(monkeypatch):
    """正常情况：掷5 + con_mod(+2) = 7/骰。"""
    monkeypatch.setattr(dice, "roll_die", lambda faces: 5)
    c = _Char(con_mod=2)
    r = rest.short_rest(c, hit_dice_to_spend=2)
    assert r["hp_restored"] == 14


def test_short_rest_zero_dice_no_minimum():
    """不消耗生命骰 → 恢复0（下限1仅在消耗生命骰时适用）。"""
    c = _Char()
    r = rest.short_rest(c, hit_dice_to_spend=0)
    assert r["success"] is True
    assert r["hp_restored"] == 0
