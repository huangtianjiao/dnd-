"""P1-10 Mutation Guard — 确定性规则核心的边界行为测试。

专门针对变异测试中存活的边界分支（操作符边界/优劣势抵消/伤害管线/死亡豁免），
确保 `>=`/`>`、`==`/`!=`、`and`/`or` 翻转会被守护测试击杀。
"""

from __future__ import annotations

import pytest


# ── check.py: 优劣势解析 / 被动检定 / 豁免DC ──────────────────────

@pytest.mark.rule("engine.check")
class TestCheckBoundaries:
    def test_resolve_advantage_advantage_only(self):
        from aidm.engine.check import resolve_advantage
        assert resolve_advantage(1, 0) == (True, False)
        assert resolve_advantage(3, 0) == (True, False)   # 多优不叠加

    def test_resolve_advantage_disadvantage_only(self):
        from aidm.engine.check import resolve_advantage
        assert resolve_advantage(0, 1) == (False, True)
        assert resolve_advantage(0, 2) == (False, True)

    def test_resolve_advantage_cancel(self):
        """R-CHK-005: 优劣势同时存在 → 抵消（两者皆 False）。"""
        from aidm.engine.check import resolve_advantage
        assert resolve_advantage(1, 1) == (False, False)
        assert resolve_advantage(2, 2) == (False, False)

    def test_resolve_advantage_none(self):
        from aidm.engine.check import resolve_advantage
        assert resolve_advantage(0, 0) == (False, False)

    def test_passive_check_base(self):
        from aidm.engine.check import passive_check
        assert passive_check([2, 3]) == 15

    def test_passive_check_advantage(self):
        from aidm.engine.check import passive_check
        assert passive_check([2], advantage=True) == 17  # 10+2+5

    def test_passive_check_disadvantage(self):
        from aidm.engine.check import passive_check
        assert passive_check([2], disadvantage=True) == 7  # 10+2-5

    def test_passive_check_cancel(self):
        """优劣势同时存在 → 抵消，不加不减。"""
        from aidm.engine.check import passive_check
        assert passive_check([2], advantage=True, disadvantage=True) == 12

    def test_calc_save_dc(self):
        from aidm.engine.check import calc_save_dc
        assert calc_save_dc(3, 2) == 13  # 8 + 3 + 2
        assert calc_save_dc(0, 6) == 14

    def test_dc_by_label_boundary(self):
        from aidm.engine.check import dc_by_label
        assert dc_by_label("中等") == 15
        assert dc_by_label("困难") == 20

    def test_attack_roll_natural_20_crit(self):
        """R-CMB-022: 天然20 必命中且重击（固定 RNG）。"""
        from aidm.engine import dice as engine_dice
        from aidm.engine.check import attack_roll

        class _Rng:
            def __init__(self, v):
                self._v = v
            def randbelow(self, exclusive_upper):
                return self._v - 1

        orig = engine_dice.get_active_rng()
        try:
            engine_dice.set_active_rng(_Rng(20))
            r = attack_roll(bonus=0, ac=100)   # AC 极高也必中
            _act = engine_dice.get_active_rng()
            assert r.hit is True and r.crit is True, (
                f"d20={r.d20} active={type(_act).__name__} "
                f"v={getattr(_act, '_v', None)} "
                f"mod={getattr(_act, 'seed', None)}")
            engine_dice.set_active_rng(_Rng(1))
            r2 = attack_roll(bonus=100, ac=1)  # 加值极高也必失手
            assert r2.hit is False and r2.crit is False
        finally:
            engine_dice.set_active_rng(orig)

    def test_attack_roll_normal_boundary(self):
        """R-CMB-017: total ≥ AC 命中（含等于）。"""
        from aidm.engine import dice as engine_dice
        from aidm.engine.check import attack_roll

        class _Rng:
            def __init__(self, v):
                self._v = v
            def randbelow(self, exclusive_upper):
                return self._v - 1

        orig = engine_dice.get_active_rng()
        try:
            # d20=10 + bonus 5 = 15；AC=15 → 命中（等于）
            engine_dice.set_active_rng(_Rng(10))
            r = attack_roll(bonus=5, ac=15)
            assert r.hit is True
            # AC=16 → 未中
            engine_dice.set_active_rng(_Rng(10))
            r2 = attack_roll(bonus=5, ac=16)
            assert r2.hit is False
        finally:
            engine_dice.set_active_rng(orig)

    def test_attack_roll_circ_penalty(self):
        """circ（力竭等）计入修正。"""
        from aidm.engine import dice as engine_dice
        from aidm.engine.check import attack_roll

        class _Rng:
            def randbelow(self, exclusive_upper):
                return 9  # d10

        orig = engine_dice.get_active_rng()
        try:
            engine_dice.set_active_rng(_Rng())
            r = attack_roll(bonus=5, ac=20, circ=-2)
            assert r.total == 10 + 5 - 2
            assert r.modifier == 3
        finally:
            engine_dice.set_active_rng(orig)

    def test_is_natural_20_and_1(self):
        from aidm.engine.check import is_natural_20, is_natural_1
        assert is_natural_20(20) is True
        assert is_natural_20(19) is False
        assert is_natural_1(1) is True
        assert is_natural_1(2) is False


# ── damage.py: 伤害管线 / HP 边界 / 死亡豁免 ──────────────────────

@pytest.mark.rule("engine.damage")
class TestDamageBoundaries:
    def test_apply_damage_to_hp_temp_first(self):
        from aidm.engine.damage import apply_damage_to_hp
        # 临时生命值优先吸收
        hp, temp = apply_damage_to_hp(hp=10, temp_hp=5, max_hp=20, dmg=3)
        assert (hp, temp) == (10, 2)

    def test_apply_damage_to_hp_overflow(self):
        from aidm.engine.damage import apply_damage_to_hp
        hp, temp = apply_damage_to_hp(hp=10, temp_hp=5, max_hp=20, dmg=8)
        assert (hp, temp) == (7, 0)   # temp 吸收 5，剩余 3 扣除 HP

    def test_grant_temp_hp_max_cap(self):
        from aidm.engine.damage import grant_temp_hp
        assert grant_temp_hp(current_temp=2, new_temp=5) == 5
        assert grant_temp_hp(current_temp=7, new_temp=5) == 7  # 不覆盖更高值

    def test_apply_healing_capped_at_max(self):
        from aidm.engine.damage import apply_healing
        assert apply_healing(hp=18, max_hp=20, heal=5) == 20
        assert apply_healing(hp=10, max_hp=20, heal=5) == 15

    def test_check_massive_damage_boundary(self):
        """巨量伤害判定：overflow ≥ 最大HP 即死亡（含等于）。"""
        from aidm.engine.damage import check_massive_damage
        # overflow = dmg - current_hp；≥ max_hp 才死亡
        assert check_massive_damage(current_hp=10, max_hp=20, dmg=29) is False
        assert check_massive_damage(current_hp=10, max_hp=20, dmg=30) is True   # 等于
        assert check_massive_damage(current_hp=10, max_hp=20, dmg=31) is True

    def test_check_hp_max_zero_death(self):
        from aidm.engine.damage import check_hp_max_zero_death
        assert check_hp_max_zero_death(max_hp=0) is True
        assert check_hp_max_zero_death(max_hp=1) is False

    def test_damage_at_zero_hp_boundary(self):
        """0HP 受击：非重击 1 次失败；重击 2 次失败；≥上限死亡。"""
        from aidm.engine.damage import DeathTracker, damage_at_zero_hp
        t = DeathTracker()
        r = damage_at_zero_hp(t, dmg=5, is_crit=False, max_hp=20)
        assert r["failures"] == 1
        t2 = DeathTracker()
        r2 = damage_at_zero_hp(t2, dmg=5, is_crit=True, max_hp=20)
        assert r2["failures"] == 2
        t3 = DeathTracker()
        r3 = damage_at_zero_hp(t3, dmg=25, is_crit=False, max_hp=20)
        assert r3["dead"] is True

    def test_death_save_boundary(self):
        """死亡豁免：<10 失败；≥10 成功；20 复苏（固定 RNG 确定性）。"""
        from aidm.engine import dice as engine_dice
        from aidm.engine.damage import DeathTracker, death_save

        class _Rng:
            def __init__(self, value):
                self._v = value
            def randbelow(self, exclusive_upper):
                return self._v - 1  # roll = value

        orig = engine_dice.get_active_rng()
        try:
            engine_dice.set_active_rng(_Rng(9))
            t = DeathTracker()
            r = death_save(t)
            assert r["failures"] == 1 and r["successes"] == 0

            engine_dice.set_active_rng(_Rng(10))
            t2 = DeathTracker()
            r2 = death_save(t2)
            assert r2["successes"] == 1

            engine_dice.set_active_rng(_Rng(20))
            t3 = DeathTracker()
            r3 = death_save(t3)
            assert r3["regain_hp"] == 1
        finally:
            engine_dice.set_active_rng(orig)


# ── combat.py: 回合推进边界 ───────────────────────────────────────

@pytest.mark.rule("engine.combat")
class TestCombatTurnBoundaries:
    def _combat(self):
        from aidm.engine import combat as cmb
        c = cmb.Combat()
        c.active = True
        c.initiative_order = [
            cmb.Combatant(cid="p1", name="A", side="player", is_player=True),
            cmb.Combatant(cid="e1", name="B", side="enemy", is_player=False),
        ]
        return c

    def test_advance_turn_round_boundary(self):
        """轮次边界：最后一名参战者后推进 → round+1、current_index 归零。"""
        from aidm.engine import combat as cmb
        c = self._combat()
        c.current_index = 1
        c.round = 1
        nxt = cmb.advance_turn(c)
        assert nxt is not None
        assert c.round == 2
        assert c.current_index == 0

    def test_advance_turn_skips_dead(self):
        from aidm.engine import combat as cmb
        c = self._combat()
        c.initiative_order[1].dead = True
        nxt = cmb.advance_turn(c)
        assert nxt is not None and nxt.cid == "p1"

    def test_advance_turn_all_dead_returns_none(self):
        from aidm.engine import combat as cmb
        c = self._combat()
        for p in c.initiative_order:
            p.dead = True
        assert cmb.advance_turn(c) is None
        assert c.active is False

    def test_current_combatant_inactive(self):
        from aidm.engine import combat as cmb
        c = self._combat()
        c.active = False
        assert cmb.current_combatant(c) is None

    def test_cannot_act_dead_or_fled(self):
        from aidm.engine import combat as cmb
        c = self._combat()
        assert cmb._cannot_act(c.initiative_order[0]) is False
        c.initiative_order[0].dead = True
        assert cmb._cannot_act(c.initiative_order[0]) is True
        c.initiative_order[0].dead = False
        c.initiative_order[0].fled = True
        assert cmb._cannot_act(c.initiative_order[0]) is True

    def test_begin_turn_death_save_flag(self):
        """begin_turn: 0HP 未死玩家 → needs_death_save=True + auto_end=True。"""
        from aidm.engine import combat as cmb
        c = cmb.Combat()
        c.initiative_order = [cmb.Combatant(
            cid="p1", name="濒死", side="player", is_player=True,
            hp=0, hp_max=20)]
        ev = cmb.begin_turn(c, c.initiative_order[0])
        assert ev["needs_death_save"] is True
        assert ev["auto_end"] is True

    def test_begin_turn_alive_no_death_save(self):
        from aidm.engine import combat as cmb
        c = cmb.Combat()
        c.initiative_order = [cmb.Combatant(
            cid="p1", name="健康", side="player", is_player=True,
            hp=10, hp_max=20)]
        ev = cmb.begin_turn(c, c.initiative_order[0])
        assert ev["needs_death_save"] is False

    def test_begin_turn_dead_player_no_save(self):
        """已死亡的玩家不再掷死亡豁免。"""
        from aidm.engine import combat as cmb
        c = cmb.Combat()
        c.initiative_order = [cmb.Combatant(
            cid="p1", name="阵亡", side="player", is_player=True,
            hp=0, hp_max=20, dead=True)]
        ev = cmb.begin_turn(c, c.initiative_order[0])
        assert ev["needs_death_save"] is False

    def test_action_economy_gates(self):
        """动作经济：已用动作/失能者不能动作；反应/附赠独立计数。"""
        from aidm.engine import combat as cmb
        from aidm.engine.conditions import ConditionState
        c = cmb.Combatant(cid="p1", name="A", side="player", is_player=True)
        assert cmb.can_take_action(c) is True
        c.action_used = True
        assert cmb.can_take_action(c) is False
        c.action_used = False
        c.conditions = ConditionState(conditions=["昏迷"])
        assert cmb.can_take_action(c) is False
        assert cmb.can_take_bonus_action(c) is False
        assert cmb.can_take_reaction(c) is False

    def test_use_action_consumes(self):
        from aidm.engine import combat as cmb
        c = cmb.Combatant(cid="p1", name="A", side="player", is_player=True)
        assert cmb.use_action(c) is True
        assert c.action_used is True
        assert cmb.use_action(c) is False  # 每回合一次动作

    def test_roll_initiative_group_shares(self):
        """同组怪物共用先攻（只掷一次）。"""
        from aidm.engine import combat as cmb
        g1 = cmb.Combatant(cid="e1", name="哥布林1", side="enemy",
                           is_player=False, group_id="g1")
        g2 = cmb.Combatant(cid="e2", name="哥布林2", side="enemy",
                           is_player=False, group_id="g1")
        p = cmb.Combatant(cid="p1", name="玩家", side="player", is_player=True)
        order = cmb.roll_initiative([g1, g2, p])
        assert g2.initiative == g1.initiative  # 同组共用
        assert order  # 有排序结果


# ── spellcasting.py: 法术位 / 成分边界 ───────────────────────────

@pytest.mark.rule("engine.spellcasting")
class TestSpellcastingBoundaries:
    def _caster(self, slots=None):
        from aidm.engine.spellcasting import CasterState
        return CasterState(
            caster_id="c1", class_name="法师", level=5,
            ability_scores={"int": 16}, spell_slots=slots or {1: 2, 2: 1},
            max_spell_slots={}, spells_cast_with_slot_this_turn=0,
            current_turn_key=None, concentrating_on=None)

    def test_has_spell_slot_boundary(self):
        from aidm.engine.spellcasting import has_spell_slot
        c = self._caster(slots={1: 1, 2: 0})
        assert has_spell_slot(c, 1) is True
        assert has_spell_slot(c, 2) is False  # 0 个 → False
        assert has_spell_slot(c, 5) is False  # 不存在的环阶 → False

    def test_consume_spell_slot(self):
        from aidm.engine.spellcasting import consume_spell_slot
        c = self._caster(slots={1: 1})
        assert consume_spell_slot(c, 1) is True
        assert c.spell_slots[1] == 0
        assert consume_spell_slot(c, 1) is False  # 已空

    def test_restore_slots_on_long_rest(self):
        from aidm.engine.spellcasting import (
            CasterState,
            restore_slots_on_long_rest,
        )
        c = CasterState(
            caster_id="c1", class_name="法师", level=5,
            ability_scores={"int": 16}, spell_slots={1: 0, 2: 0},
            max_spell_slots={1: 4, 2: 3},
            spells_cast_with_slot_this_turn=0, current_turn_key=None,
            concentrating_on=None)
        restore_slots_on_long_rest(c)
        assert c.spell_slots == {1: 4, 2: 3}

    def _spell(self, comps="VSM", cost=0.0, consumed=False):
        from aidm.data.spells import Spell
        return Spell(
            name="测试术", en_name="Test", level=1, school="塑能",
            casting_time="1动作", casting_time_type="ACTION",
            range="60尺", components=set(comps),
            material_cost_gp=cost, material_consumed=consumed,
            damage_dice="3d8", save_ability="dex",
        )

    def test_can_cast_by_components_verbal_blocked(self):
        """R-SPL-011: 沉默/禁言 → V 失败。"""
        from aidm.engine.spellcasting import can_cast_by_components
        from aidm.engine.spellcasting import CasterState
        c = CasterState(caster_id="c1", class_name="法师", level=1,
                        ability_scores={"int": 16})
        assert can_cast_by_components(self._spell("V"), c, muted=True) is False
        assert can_cast_by_components(self._spell("V"), c, silenced=True) is False
        assert can_cast_by_components(self._spell("V"), c) is True

    def test_can_cast_by_components_somatic_hands(self):
        """R-SPL-012: 姿势成分需空手。"""
        from aidm.engine.spellcasting import can_cast_by_components, CasterState
        c = CasterState(caster_id="c1", class_name="法师", level=1,
                        ability_scores={"int": 16})
        assert can_cast_by_components(self._spell("S"), c, free_hands=0) is False
        assert can_cast_by_components(self._spell("S"), c, free_hands=1) is True

    def test_can_cast_by_components_material_substitution(self):
        """R-SPL-013: 普通材料可用材料包/法器替代；有价材料须实备。"""
        from aidm.engine.spellcasting import can_cast_by_components, CasterState
        c = CasterState(caster_id="c1", class_name="法师", level=1,
                        ability_scores={"int": 16})
        # 普通材料：无包无法施
        assert can_cast_by_components(
            self._spell("M"), c, free_hands=1,
            has_material_pouch=False, has_focus=False) is False
        # 有材料包 → 可施
        assert can_cast_by_components(
            self._spell("M"), c, free_hands=1,
            has_material_pouch=True) is True
        # 有价材料：材料包不可替代，须实备
        assert can_cast_by_components(
            self._spell("M", cost=100), c, free_hands=1,
            has_material_pouch=True, has_specific_material=False) is False
        assert can_cast_by_components(
            self._spell("M", cost=100), c, free_hands=1,
            has_material_pouch=True, has_specific_material=True) is True

    def test_resolve_upcast_effective_level(self):
        """R-SPL-004: effectiveLevel = max(法术环阶, 使用环阶)。"""
        from aidm.engine.spellcasting import resolve_upcast
        r = resolve_upcast(self._spell(), slot_level=3, caster_level=5)
        assert r["effective_level"] == 3
        r2 = resolve_upcast(self._spell(), slot_level=1, caster_level=5)
        assert r2["effective_level"] == 1
        r3 = resolve_upcast(self._spell(), slot_level=0, caster_level=5)
        assert r3["effective_level"] == 1  # 不低于法术环阶


# ── spell_slots.py: 职业法术位表边界 ─────────────────────────────

@pytest.mark.rule("engine.spell_slots")
class TestSpellSlotsBoundaries:
    def test_slots_for_class_level(self):
        from aidm.engine.spell_slots import SpellSlotCalculator
        # 1级法师：1环 2 个（2024）
        s1 = SpellSlotCalculator.slots_for_class_level("法师", 1)
        assert s1.get(1) == 2
        s5 = SpellSlotCalculator.slots_for_class_level("法师", 5)
        assert s5.get(3) >= 2  # 5级有 3 环

    def test_multiclass_combined_slots(self):
        from aidm.engine.spell_slots import (
            SpellSlotCalculator,
            get_combined_slots,
        )
        # 纯单职业
        a = SpellSlotCalculator.calculate_slots({"法师": 5})
        assert a.get(3, 0) >= 2
        b = get_combined_slots({"法师": 5})
        assert b.get(3, 0) >= 2

    def test_pact_slots(self):
        from aidm.engine.spell_slots import SpellSlotCalculator
        p = SpellSlotCalculator.pact_slots(5)
        assert sum(p.values()) > 0  # 5级魔契师有契约法术位


# ── brain/rest.py: 休息边界 ─────────────────────────────────────

@pytest.mark.rule("engine.rest_state")
class TestRestBoundaries:
    class _Ch:
        hp_current = 10
        hp_max = 20
        hit_dice_current = 2
        hit_dice_max = 2
        exhaustion = 2
        temp_hp = 0
        char_class = "战士"
        level = 1
        spell_slots = {"1": 0}
        max_spell_slots = {"1": 2}
        abilities = {"con": 14}
        resource_manager = None
        entity_id = "c1"
        features = []
        conditions_list = []

        def ability_mod(self, ab):
            return (self.abilities[ab] - 10) // 2

    def test_short_rest_spends_hit_dice(self):
        from aidm.brain.rest import short_rest
        ch = self._Ch()
        r = short_rest(ch, hit_dice_to_spend=1)
        assert r["success"] is True
        assert r["hp_restored"] > 0
        assert r["hit_dice_spent"] == 1

    def test_long_rest_restores_hp_and_lowers_exhaustion(self):
        from aidm.brain.rest import long_rest
        ch = self._Ch()
        r = long_rest(ch)
        assert r["success"] is True
        assert r["hp_restored"] == ch.hp_max - ch.hp_current
        assert r["exhaustion_reduced"] == 1
        assert r["spell_slots_restored"] is True

    def test_short_rest_no_hit_dice(self):
        from aidm.brain.rest import short_rest
        ch = self._Ch()
        ch.hit_dice_current = 0
        r = short_rest(ch, hit_dice_to_spend=1)
        assert r["success"] is False  # 无生命骰不能短休恢复


# ── conditions.py: 状态/速度/豁免边界 ─────────────────────────────

@pytest.mark.rule("engine.conditions")
class TestConditionsBoundaries:
    def test_speed_after_conditions(self):
        from aidm.engine.conditions import ConditionState, speed_after_conditions
        cs = ConditionState(conditions=[], exhaustion=0)
        assert speed_after_conditions(30, cs) == 30
        cs2 = ConditionState(conditions=[], exhaustion=1)
        assert speed_after_conditions(30, cs2) == 25  # 力竭-5尺/层

    def test_d20_penalty_exhaustion(self):
        from aidm.engine.conditions import ConditionState, d20_penalty
        cs = ConditionState(conditions=[], exhaustion=2)
        assert d20_penalty(cs) == 4  # 力竭等级×2（调用方 negate）

    def test_add_no_stack(self):
        from aidm.engine.conditions import ConditionState
        cs = ConditionState()
        assert cs.add("麻痹") is True
        assert cs.add("麻痹") is False  # 不叠加
        assert cs.has("麻痹")

    def test_add_ko_applies_prone(self):
        from aidm.engine.conditions import ConditionState
        cs = ConditionState()
        cs.add("昏迷")
        assert cs.has("倒地")  # 昏迷 → 自动倒地

    def test_add_exhaustion_stacks_capped(self):
        from aidm.engine.conditions import ConditionState
        cs = ConditionState()
        for _ in range(7):
            cs.add("力竭")
        assert cs.exhaustion == 6  # 上限 6

    def test_remove_exhaustion(self):
        from aidm.engine.conditions import ConditionState
        cs = ConditionState(exhaustion=2)
        assert cs.remove("力竭") is True
        assert cs.exhaustion == 1
        assert cs.remove("力竭") is True
        assert cs.remove("力竭") is False  # 已为 0

    def test_has_exhaustion(self):
        from aidm.engine.conditions import ConditionState
        assert ConditionState(exhaustion=1).has("力竭") is True
        assert ConditionState(exhaustion=0).has("力竭") is False

    def test_is_incapacitated(self):
        from aidm.engine.conditions import ConditionState
        for c in ("昏迷", "麻痹", "震慑", "石化"):
            assert ConditionState(conditions={c}).is_incapacitated()

    def test_is_dead_from_exhaustion_boundary(self):
        from aidm.engine.conditions import ConditionState
        assert ConditionState(exhaustion=5).is_dead_from_exhaustion() is False
        assert ConditionState(exhaustion=6).is_dead_from_exhaustion() is True

    def test_attack_modifiers_advantage_on_helpless(self):
        """攻击麻痹/昏迷目标 → 优势；5尺内 → 自动重击。"""
        from aidm.engine.conditions import (
            ConditionState,
            attack_modifiers,
        )
        attacker = ConditionState()
        target = ConditionState(conditions={"昏迷"})
        m = attack_modifiers(attacker, target, distance_ft=5)
        assert m.attacker_advantage is True
        assert m.target_auto_crit_if_hit is True
        m2 = attack_modifiers(attacker, target, distance_ft=30)
        assert m2.target_auto_crit_if_hit is False

    def test_attack_modifiers_prone_distance(self):
        """倒地：5尺内优势，5尺外劣势。"""
        from aidm.engine.conditions import (
            ConditionState,
            attack_modifiers,
        )
        attacker = ConditionState()
        target = ConditionState(conditions={"倒地"})
        m = attack_modifiers(attacker, target, distance_ft=5)
        assert m.attacker_advantage is True
        m2 = attack_modifiers(attacker, target, distance_ft=10)
        assert m2.attacker_disadvantage is True

# ── review 修复回归: RngContext 优劣势抵消 / contextvars 隔离 ─────

@pytest.mark.rule("engine.rng_context")
class TestRngReviewFixes:
    def test_rng_context_adv_dis_cancel(self):
        """review#3: 优劣势同时存在 → 抵消只掷一骰（R-CHK-005）。"""
        from aidm.engine.rng_context import create_rng_context
        rng = create_rng_context(seed=42)
        # 固定随机源：randbelow 返回 0 → roll=1
        class _Fixed:
            def __init__(self, vals):
                self._v = iter(vals)
            def randint(self, a, b):
                return next(self._v)
        rng._rng = _Fixed([5])  # 抵消 → 只消费一个值
        rec = rng.roll_d20(advantage=True, disadvantage=True)
        assert len(rec.results) == 1, "优劣势抵消必须只掷一骰"
        assert rec.results[0] == 5

    def test_adv_only_two_dice_max(self):
        from aidm.engine.rng_context import create_rng_context
        rng = create_rng_context(seed=1)
        class _Fixed:
            def __init__(self, vals):
                self._v = iter(vals)
            def randint(self, a, b):
                return next(self._v)
        rng._rng = _Fixed([4, 10])
        rec = rng.roll_d20(advantage=True)
        assert len(rec.results) == 2
        assert rec.results[0] == 4 and rec.results[1] == 10
        assert rec.total == 10  # 取高

    def test_contextvars_rng_isolation(self):
        """review#9: RNG 注入按上下文隔离，互不污染。"""
        import contextvars
        from aidm.engine import dice
        orig = dice.get_active_rng()
        try:
            ctx_a = contextvars.copy_context()
            ctx_b = contextvars.copy_context()

            def set_a():
                dice.set_active_rng(_FixedRngForCtx(20))
            ctx_a.run(set_a)

            def set_b():
                dice.set_active_rng(_FixedRngForCtx(1))
            ctx_b.run(set_b)

            # 各自上下文内读取各自 RNG（互不相同，且与主上下文无关）
            ra = ctx_a.run(dice.get_active_rng)
            rb = ctx_b.run(dice.get_active_rng)
            assert ra is not None and rb is not None
            assert type(ra).__name__ == type(rb).__name__ == "_FixedRngForCtx"
            assert ra._v != rb._v, "两个上下文必须持有不同 RNG"
            # 主上下文不受 ctx_a/ctx_b 注入影响（保持原值）
            assert dice.get_active_rng() is orig
        finally:
            dice.set_active_rng(orig)


class _FixedRngForCtx:
    def __init__(self, v):
        self._v = v
    def randbelow(self, upper):
        return self._v - 1
    def __repr__(self):
        return f"_FixedRngForCtx({self._v})"
