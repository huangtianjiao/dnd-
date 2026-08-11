"""Wave 3B 测试 — 攻击序列 / 伤害包 / 健康状态机 / 武器精通集成。

覆盖:
  - COM-007: AttackSequence 多攻击序列
  - DMG-001: DamagePacket 多组件伤害包
  - DMG-002: HealthStateMachine 0HP/非致命/死亡状态机
  - COM-004: MasteryGrant + resolve_mastery_with_grant
"""

import pytest
from unittest.mock import patch

from aidm.engine.attack_sequence import AttackPlan, AttackResult, AttackSequence
from aidm.engine.damage import (
    DamageComponent,
    DamagePacket,
    apply_damage_pipeline,
)
from aidm.engine.health_state import (
    DeathSaveState,
    HealthStateMachine,
    KnockoutState,
)
from aidm.engine.mastery import (
    MasteryEffect,
    MasteryGrant,
    resolve_mastery,
    resolve_mastery_with_grant,
)


# ═══════════════════════════════════════════════════════════════════════════
# COM-007: AttackSequence
# ═══════════════════════════════════════════════════════════════════════════

class TestAttackPlan:
    """AttackPlan 数据类测试。"""

    def test_default_values(self):
        plan = AttackPlan(attacker_id="a1", target_id="t1")
        assert plan.ability_used == "str"
        assert plan.target_ac == 10
        assert plan.damage_dice == "1d6"
        assert plan.damage_type == "slashing"
        assert plan.has_advantage is False

    def test_custom_plan(self):
        plan = AttackPlan(
            attacker_id="fighter",
            target_id="goblin",
            weapon_name="longsword",
            ability_used="str",
            attack_modifier=7,
            target_ac=15,
            damage_dice="1d8",
            damage_modifier=4,
            damage_type="slashing",
        )
        assert plan.attack_modifier == 7
        assert plan.target_ac == 15


class TestAttackSequence:
    """AttackSequence 多攻击序列测试。"""

    def test_initial_state(self):
        seq = AttackSequence(sequence_id="seq1", attacker_id="fighter")
        assert seq.remaining_attacks == 1
        assert seq.can_continue() is True

    def test_use_attack_opportunity(self):
        seq = AttackSequence(remaining_attacks=2)
        assert seq.remaining_attacks == 2
        seq.use_attack_opportunity()
        assert seq.remaining_attacks == 1
        seq.use_attack_opportunity()
        assert seq.remaining_attacks == 0
        assert seq.can_continue() is False

    def test_build_attack_plan(self):
        seq = AttackSequence()
        attacker = {
            "id": "fighter",
            "abilities": {"str": 16, "dex": 12},
            "proficiency_bonus": 3,
        }
        target = {"id": "goblin", "ac": 15}
        weapon = {
            "id": "longsword",
            "name": "Longsword",
            "ability": "str",
            "proficient": True,
            "damage_dice": "1d8",
            "damage_type": "slashing",
        }
        plan = seq.build_attack_plan(attacker, target, weapon)
        assert plan.attacker_id == "fighter"
        assert plan.target_id == "goblin"
        # str 16 → mod +3, prof +3 → total +6
        assert plan.attack_modifier == 6
        assert plan.proficiency_applied is True

    @patch("aidm.engine.dice.roll_d20")
    @patch("aidm.engine.dice.roll_die")
    def test_execute_sub_attack_hit(self, mock_roll_die, mock_roll_d20):
        """命中场景。"""
        # d20 返回 15
        class FakeD20:
            used = 15
            rolls = [15]
            mode = "normal"
        mock_roll_d20.return_value = FakeD20()
        # 伤害骰返回 5
        mock_roll_die.return_value = 5

        seq = AttackSequence()
        plan = AttackPlan(
            attacker_id="a",
            target_id="t",
            attack_modifier=3,
            target_ac=15,
            damage_dice="1d8",
            damage_modifier=2,
            damage_type="slashing",
        )
        result = seq.execute_sub_attack(plan)
        assert result.is_hit is True  # 15+3=18 >= 15
        assert result.attack_roll == 15
        assert result.total_attack == 18
        assert result.damage_total > 0
        assert len(seq.results) == 1

    @patch("aidm.engine.dice.roll_d20")
    def test_execute_sub_attack_miss(self, mock_roll_d20):
        """失手场景。"""
        class FakeD20:
            used = 5
            rolls = [5]
            mode = "normal"
        mock_roll_d20.return_value = FakeD20()

        seq = AttackSequence()
        plan = AttackPlan(
            attacker_id="a",
            target_id="t",
            attack_modifier=3,
            target_ac=20,
            damage_dice="1d8",
        )
        result = seq.execute_sub_attack(plan)
        assert result.is_hit is False  # 5+3=8 < 20
        assert result.damage_total == 0

    @patch("aidm.engine.dice.roll_d20")
    def test_natural_20_crit(self, mock_roll_d20):
        """天然 20 重击。"""
        class FakeD20:
            used = 20
            rolls = [20]
            mode = "normal"
        mock_roll_d20.return_value = FakeD20()

        seq = AttackSequence()
        plan = AttackPlan(
            attacker_id="a", target_id="t",
            attack_modifier=5, target_ac=15,
            damage_dice="1d8", damage_modifier=3,
        )
        result = seq.execute_sub_attack(plan)
        assert result.is_hit is True
        assert result.is_crit is True

    @patch("aidm.engine.dice.roll_d20")
    def test_natural_1_fumble(self, mock_roll_d20):
        """天然 1 失手。"""
        class FakeD20:
            used = 1
            rolls = [1]
            mode = "normal"
        mock_roll_d20.return_value = FakeD20()

        seq = AttackSequence()
        plan = AttackPlan(
            attacker_id="a", target_id="t",
            attack_modifier=100, target_ac=5,
            damage_dice="1d8",
        )
        result = seq.execute_sub_attack(plan)
        assert result.is_hit is False
        assert result.is_fumble is True

    def test_reset_turn(self):
        seq = AttackSequence(remaining_attacks=0, loading_used=True)
        seq.results.append(AttackResult(attack_index=0))
        seq.reset_turn(base_attacks=2)
        assert seq.remaining_attacks == 2
        assert seq.loading_used is False
        assert len(seq.results) == 0

    def test_feature_usage_tracking(self):
        seq = AttackSequence()
        assert seq.record_feature_usage("cleave", max_per_turn=1) is True
        assert seq.record_feature_usage("cleave", max_per_turn=1) is False


# ═══════════════════════════════════════════════════════════════════════════
# DMG-001: DamagePacket
# ═══════════════════════════════════════════════════════════════════════════

class TestDamageComponent:
    """DamageComponent 数据类测试。"""

    def test_default_values(self):
        comp = DamageComponent(source_id="sword", dice_expr="1d8", damage_type="slashing")
        assert comp.flat_modifier == 0
        assert comp.crit_dice == ""


class TestDamagePacket:
    """DamagePacket 多组件伤害包测试。"""

    def test_add_component(self):
        packet = DamagePacket()
        packet.add_component("sword", "1d8", "slashing", flat_mod=4)
        packet.add_component("hunters_mark", "1d6", "force")
        assert len(packet.components) == 2
        assert packet.components[0].source_id == "sword"
        assert packet.components[1].source_id == "hunters_mark"

    @patch("aidm.engine.dice.roll_dice")
    def test_resolve_basic(self, mock_roll_dice):
        """基础解析：两个组件，无敌对关系。"""
        # 模拟掷骰结果
        class FakeRoll:
            def __init__(self, total, rolls):
                self.total = total
                self.dice_rolls = rolls
        mock_roll_dice.side_effect = [FakeRoll(5, [5]), FakeRoll(4, [4])]

        packet = DamagePacket()
        packet.add_component("sword", "1d8", "slashing", flat_mod=3)
        packet.add_component("fire", "1d6", "fire")

        result = packet.resolve({})
        assert result["total_damage"] == (5 + 3) + 4  # 8 + 4 = 12
        assert len(result["breakdown"]) == 2
        assert result["breakdown"][0]["source"] == "sword"
        assert result["breakdown"][0]["after_affinity"] == 8

    @patch("aidm.engine.dice.roll_dice")
    def test_resolve_with_resistance(self, mock_roll_dice):
        """抗性测试。"""
        class FakeRoll:
            def __init__(self, total, rolls):
                self.total = total
                self.dice_rolls = rolls
        mock_roll_dice.return_value = FakeRoll(10, [10])

        packet = DamagePacket()
        packet.add_component("sword", "1d10", "slashing")

        result = packet.resolve({"resistances": ["slashing"]})
        # 10 slashing, resisted → floor(10/2) = 5
        assert result["total_damage"] == 5
        assert result["breakdown"][0]["after_affinity"] == 5

    @patch("aidm.engine.dice.roll_dice")
    def test_resolve_with_immunity(self, mock_roll_dice):
        """免疫测试。"""
        class FakeRoll:
            def __init__(self, total, rolls):
                self.total = total
                self.dice_rolls = rolls
        mock_roll_dice.return_value = FakeRoll(10, [10])

        packet = DamagePacket()
        packet.add_component("fire", "1d10", "fire")

        result = packet.resolve({"immunities": ["fire"]})
        assert result["total_damage"] == 0

    @patch("aidm.engine.dice.roll_dice")
    def test_resolve_with_vulnerability(self, mock_roll_dice):
        """易伤测试。"""
        class FakeRoll:
            def __init__(self, total, rolls):
                self.total = total
                self.dice_rolls = rolls
        mock_roll_dice.return_value = FakeRoll(6, [6])

        packet = DamagePacket()
        packet.add_component("fire", "1d6", "fire")

        result = packet.resolve({"vulnerabilities": ["fire"]})
        # 6 fire, vulnerable → 6*2 = 12
        assert result["total_damage"] == 12

    @patch("aidm.engine.dice.roll_dice")
    def test_resolve_merge_same_type(self, mock_roll_dice):
        """合并同类型伤害。"""
        class FakeRoll:
            def __init__(self, total, rolls):
                self.total = total
                self.dice_rolls = rolls
        mock_roll_dice.side_effect = [FakeRoll(5, [5]), FakeRoll(3, [3])]

        packet = DamagePacket()
        packet.add_component("sword", "1d8", "slashing")
        packet.add_component("enhancement", "1d4", "slashing")

        result = packet.resolve({})
        assert result["total_damage"] == 8  # 5 + 3
        assert result["type_totals"]["挥砍"] == 8  # 中文标准化


# ═══════════════════════════════════════════════════════════════════════════
# DMG-002: HealthStateMachine
# ═══════════════════════════════════════════════════════════════════════════

class TestDeathSaveState:
    """DeathSaveState 测试。"""

    def test_initial(self):
        ds = DeathSaveState()
        assert ds.successes == 0
        assert ds.failures == 0
        assert ds.is_stable() is False
        assert ds.is_dead() is False

    def test_stable(self):
        ds = DeathSaveState(successes=3)
        assert ds.is_stable() is True

    def test_dead(self):
        ds = DeathSaveState(failures=3)
        assert ds.is_dead() is True

    def test_reset(self):
        ds = DeathSaveState(successes=2, failures=1)
        ds.reset()
        assert ds.successes == 0
        assert ds.failures == 0


class TestKnockoutState:
    """KnockoutState 枚举测试。"""

    def test_values(self):
        assert KnockoutState.CONSCIOUS == "conscious"
        assert KnockoutState.UNCONSCIOUS == "unconscious"
        assert KnockoutState.STABILIZED == "stabilized"
        assert KnockoutState.DEAD == "dead"


class TestHealthStateMachine:
    """HealthStateMachine 完整状态机测试。"""

    def test_initial_state(self):
        sm = HealthStateMachine(entity_id="hero", hp_current=30, hp_max=30)
        assert sm.knockout_state == KnockoutState.CONSCIOUS
        assert sm.hp_current == 30

    def test_damage_reduces_hp(self):
        sm = HealthStateMachine(entity_id="hero", hp_current=30, hp_max=30)
        events = sm.on_damage_applied(10)
        assert sm.hp_current == 20
        assert any(e["type"] == "hp_changed" for e in events)

    def test_temp_hp_absorbed_first(self):
        sm = HealthStateMachine(entity_id="hero", hp_current=20, hp_max=20, temp_hp=5)
        sm.on_damage_applied(7)
        # 7 damage: 5 temp + 2 real
        assert sm.temp_hp == 0
        assert sm.hp_current == 18

    def test_massive_damage_death(self):
        sm = HealthStateMachine(entity_id="hero", hp_current=10, hp_max=20)
        events = sm.on_damage_applied(30)  # 30 >= 10, overflow=20 >= 20
        assert sm.knockout_state == KnockoutState.DEAD
        assert any(e["type"] == "massive_damage_death" for e in events)

    def test_drop_to_zero_unconscious(self):
        sm = HealthStateMachine(entity_id="hero", hp_current=10, hp_max=30)
        events = sm.on_damage_applied(10)
        assert sm.hp_current == 0
        assert sm.knockout_state == KnockoutState.UNCONSCIOUS
        assert any(e["type"] == "dropped_to_zero" for e in events)

    def test_drop_to_zero_with_crit(self):
        sm = HealthStateMachine(entity_id="hero", hp_current=10, hp_max=30)
        events = sm.on_damage_applied(10, is_crit=True)
        assert sm.knockout_state == KnockoutState.UNCONSCIOUS
        # 重击 = 2 failures
        assert sm.death_saves.failures == 2

    def test_healing_restores_hp(self):
        sm = HealthStateMachine(entity_id="hero", hp_current=10, hp_max=30)
        events = sm.on_healing(15)
        assert sm.hp_current == 25
        assert any(e["type"] == "healed" for e in events)

    def test_healing_resets_death_saves(self):
        sm = HealthStateMachine(
            entity_id="hero", hp_current=0, hp_max=30,
            knockout_state=KnockoutState.UNCONSCIOUS,
        )
        sm.death_saves.failures = 2
        events = sm.on_healing(5)
        assert sm.hp_current == 5
        assert sm.knockout_state == KnockoutState.CONSCIOUS
        assert sm.death_saves.failures == 0
        assert any(e["type"] == "regained_consciousness" for e in events)

    def test_healing_capped_at_max(self):
        sm = HealthStateMachine(entity_id="hero", hp_current=25, hp_max=30)
        sm.on_healing(20)
        assert sm.hp_current == 30

    @patch("aidm.engine.dice.roll_die")
    def test_death_save_success(self, mock_roll_die):
        mock_roll_die.return_value = 12  # >= 10 → success
        sm = HealthStateMachine(
            entity_id="hero", hp_current=0, hp_max=30,
            knockout_state=KnockoutState.UNCONSCIOUS,
        )
        events = sm.at_turn_start()
        assert sm.death_saves.successes == 1
        assert any(e["type"] == "death_save_success" for e in events)

    @patch("aidm.engine.dice.roll_die")
    def test_death_save_failure(self, mock_roll_die):
        mock_roll_die.return_value = 5  # < 10 → failure
        sm = HealthStateMachine(
            entity_id="hero", hp_current=0, hp_max=30,
            knockout_state=KnockoutState.UNCONSCIOUS,
        )
        events = sm.at_turn_start()
        assert sm.death_saves.failures == 1
        assert any(e["type"] == "death_save_failure" for e in events)

    @patch("aidm.engine.dice.roll_die")
    def test_death_save_natural_1_two_failures(self, mock_roll_die):
        mock_roll_die.return_value = 1  # natural 1 → 2 failures
        sm = HealthStateMachine(
            entity_id="hero", hp_current=0, hp_max=30,
            knockout_state=KnockoutState.UNCONSCIOUS,
        )
        events = sm.at_turn_start()
        assert sm.death_saves.failures == 2
        assert any(e["type"] == "death_save_natural_1" for e in events)

    @patch("aidm.engine.dice.roll_die")
    def test_death_save_natural_20_revive(self, mock_roll_die):
        mock_roll_die.return_value = 20  # natural 20 → 1 HP, conscious
        sm = HealthStateMachine(
            entity_id="hero", hp_current=0, hp_max=30,
            knockout_state=KnockoutState.UNCONSCIOUS,
        )
        events = sm.at_turn_start()
        assert sm.hp_current == 1
        assert sm.knockout_state == KnockoutState.CONSCIOUS
        assert any(e["type"] == "death_save_natural_20" for e in events)

    @patch("aidm.engine.dice.roll_die")
    def test_three_successes_stabilize(self, mock_roll_die):
        mock_roll_die.return_value = 15  # success
        sm = HealthStateMachine(
            entity_id="hero", hp_current=0, hp_max=30,
            knockout_state=KnockoutState.UNCONSCIOUS,
        )
        sm.death_saves.successes = 2
        events = sm.at_turn_start()
        assert sm.knockout_state == KnockoutState.STABILIZED
        assert any(e["type"] == "stabilized" for e in events)

    @patch("aidm.engine.dice.roll_die")
    def test_three_failures_dead(self, mock_roll_die):
        mock_roll_die.return_value = 3  # failure
        sm = HealthStateMachine(
            entity_id="hero", hp_current=0, hp_max=30,
            knockout_state=KnockoutState.UNCONSCIOUS,
        )
        sm.death_saves.failures = 2
        events = sm.at_turn_start()
        assert sm.knockout_state == KnockoutState.DEAD
        assert any(e["type"] == "dead_by_failures" for e in events)

    def test_damage_at_zero_increments_failures(self):
        sm = HealthStateMachine(
            entity_id="hero", hp_current=0, hp_max=30,
            knockout_state=KnockoutState.UNCONSCIOUS,
        )
        events = sm.on_damage_at_zero(5, is_crit=False)
        assert sm.death_saves.failures == 1
        assert any(e["type"] == "damage_at_zero_hp" for e in events)

    def test_damage_at_zero_crit_two_failures(self):
        sm = HealthStateMachine(
            entity_id="hero", hp_current=0, hp_max=30,
            knockout_state=KnockoutState.UNCONSCIOUS,
        )
        events = sm.on_damage_at_zero(5, is_crit=True)
        assert sm.death_saves.failures == 2

    def test_damage_at_zero_ge_max_hp_death(self):
        sm = HealthStateMachine(
            entity_id="hero", hp_current=0, hp_max=20,
            knockout_state=KnockoutState.UNCONSCIOUS,
        )
        events = sm.on_damage_at_zero(20, is_crit=False)
        assert sm.knockout_state == KnockoutState.DEAD

    def test_stabilize(self):
        sm = HealthStateMachine(
            entity_id="hero", hp_current=0, hp_max=30,
            knockout_state=KnockoutState.UNCONSCIOUS,
        )
        events = sm.stabilize()
        assert sm.knockout_state == KnockoutState.STABILIZED
        assert any(e["type"] == "stabilized" for e in events)

    def test_choose_knockout_one_hp_rule(self):
        sm = HealthStateMachine(entity_id="hero", hp_current=0, hp_max=30)
        result = sm.choose_knockout(use_1hp_rule=True)
        assert result["choice"] == "one_hp_rule"
        assert sm.hp_current == 1
        assert sm.knockout_state == KnockoutState.CONSCIOUS

    def test_choose_knockout_unconscious(self):
        sm = HealthStateMachine(entity_id="hero", hp_current=0, hp_max=30)
        result = sm.choose_knockout(use_1hp_rule=False)
        assert result["choice"] == "unconscious"
        assert sm.knockout_state == KnockoutState.UNCONSCIOUS

    def test_grant_temp_hp(self):
        sm = HealthStateMachine(entity_id="hero", hp_current=20, hp_max=20, temp_hp=3)
        events = sm.grant_temp_hp(5)
        assert sm.temp_hp == 5  # 取较大者
        assert any(e["type"] == "temp_hp_granted" for e in events)

    def test_nonlethal_knockout(self):
        sm = HealthStateMachine(entity_id="hero", hp_current=5, hp_max=30, is_nonlethal=True)
        events = sm.on_damage_applied(10)
        assert sm.hp_current == 0
        assert sm.knockout_state == KnockoutState.UNCONSCIOUS
        assert any(e["type"] == "nonlethal_knockout" for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# COM-004: MasteryGrant + Integration
# ═══════════════════════════════════════════════════════════════════════════

class TestMasteryGrant:
    """MasteryGrant 精通授权追踪测试。"""

    def test_grant_and_has(self):
        grant = MasteryGrant(entity_id="fighter")
        assert grant.has_mastery("削弱") is False
        grant.grant("削弱")
        assert grant.has_mastery("削弱") is True

    def test_revoke(self):
        grant = MasteryGrant(entity_id="fighter", granted_masteries=["推离"])
        assert grant.has_mastery("推离") is True
        grant.revoke("推离")
        assert grant.has_mastery("推离") is False

    def test_can_use_with_limit(self):
        grant = MasteryGrant(entity_id="fighter", granted_masteries=["横扫"])
        assert grant.can_use("横扫") is True
        grant.record_use("横扫")
        assert grant.can_use("横扫") is False  # 每回合 1 次

    def test_can_use_unlimited(self):
        grant = MasteryGrant(entity_id="fighter", granted_masteries=["削弱"])
        for _ in range(10):
            assert grant.can_use("削弱") is True
            grant.record_use("削弱")

    def test_reset_turn(self):
        grant = MasteryGrant(entity_id="fighter", granted_masteries=["横扫"])
        grant.record_use("横扫")
        assert grant.can_use("横扫") is False
        grant.reset_turn()
        assert grant.can_use("横扫") is True

    def test_cannot_use_ungranted(self):
        grant = MasteryGrant(entity_id="fighter")
        assert grant.can_use("削弱") is False
        assert grant.record_use("削弱") is False


class TestResolveMasteryWithGrant:
    """resolve_mastery_with_grant 集成测试。"""

    def test_basic_hit_sap(self):
        grant = MasteryGrant(entity_id="fighter", granted_masteries=["削弱"])
        effect = resolve_mastery_with_grant("削弱", grant, hit=True)
        assert effect.applied is True
        assert effect.target_disadvantage is True

    def test_hit_push(self):
        grant = MasteryGrant(entity_id="fighter", granted_masteries=["推离"])
        effect = resolve_mastery_with_grant("推离", grant, hit=True, target_size="medium")
        assert effect.applied is True
        assert effect.push_distance_ft == 10

    def test_graze_on_miss(self):
        grant = MasteryGrant(entity_id="fighter", granted_masteries=["擦掠"])
        effect = resolve_mastery_with_grant("擦掠", grant, hit=False, attacker_ability_mod=4)
        assert effect.applied is True
        assert effect.graze_damage == 4

    def test_cleave_extra_attack(self):
        grant = MasteryGrant(entity_id="fighter", granted_masteries=["横扫"])
        effect = resolve_mastery_with_grant("横扫", grant, hit=True)
        assert effect.applied is True
        assert effect.extra_attack_available is True
        # 使用次数记录
        assert grant.per_turn_usage.get("横扫") == 1

    def test_cleave_once_per_turn(self):
        grant = MasteryGrant(entity_id="fighter", granted_masteries=["横扫"])
        effect1 = resolve_mastery_with_grant("横扫", grant, hit=True)
        assert effect1.applied is True
        effect2 = resolve_mastery_with_grant("横扫", grant, hit=True)
        assert effect2.applied is False  # 已用完

    def test_nick_active(self):
        grant = MasteryGrant(entity_id="fighter", granted_masteries=["迅击"])
        effect = resolve_mastery_with_grant("迅击", grant, hit=True)
        assert effect.nick_active is True

    def test_vex_advantage(self):
        grant = MasteryGrant(entity_id="fighter", granted_masteries=["侵扰"])
        effect = resolve_mastery_with_grant("侵扰", grant, hit=True)
        assert effect.attacker_advantage is True

    def test_slow_speed_reduction(self):
        grant = MasteryGrant(entity_id="fighter", granted_masteries=["缓速"])
        effect = resolve_mastery_with_grant("缓速", grant, hit=True)
        assert effect.speed_reduction_ft == 10

    def test_not_granted(self):
        grant = MasteryGrant(entity_id="fighter")
        effect = resolve_mastery_with_grant("削弱", grant, hit=True)
        assert effect.applied is False
        assert effect.effect_type == "not_available"

    @patch("aidm.engine.dice.roll_d20")
    def test_topple_with_save(self, mock_roll_d20):
        """失衡：目标豁免成功不倒地。"""
        class FakeD20:
            used = 18
            rolls = [18]
            mode = "normal"
        mock_roll_d20.return_value = FakeD20()

        grant = MasteryGrant(entity_id="fighter", granted_masteries=["失衡"])
        effect = resolve_mastery_with_grant(
            "失衡", grant, hit=True,
            attacker_ability_mod=3, attacker_prof=3,
            target_con_mod=4, target_con_prof=True, target_prof=3,
        )
        # DC = 8+3+3 = 14, save = 18+4+3 = 25 >= 14 → 不倒
        assert effect.applied is True
        assert effect.target_prone is False
        assert effect.dc == 14


# ═══════════════════════════════════════════════════════════════════════════
# 导入测试
# ═══════════════════════════════════════════════════════════════════════════

class TestEngineImports:
    """验证所有新类可从 engine 包导入。"""

    def test_import_attack_sequence(self):
        from aidm.engine import AttackPlan, AttackResult, AttackSequence
        assert AttackPlan is not None

    def test_import_damage_packet(self):
        from aidm.engine import DamageComponent, DamagePacket
        assert DamagePacket is not None

    def test_import_health_state(self):
        from aidm.engine import DeathSaveState, HealthStateMachine, KnockoutState
        assert HealthStateMachine is not None

    def test_import_mastery_grant(self):
        from aidm.engine import MasteryEffect, MasteryGrant, resolve_mastery_with_grant
        assert MasteryGrant is not None
