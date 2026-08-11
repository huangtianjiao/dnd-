"""生产链路自动覆盖测试 — 补充被生产代码引用但缺直接测试的引擎模块。

覆盖模块:
  - unit_of_work（STATE-003 幂等/事务）
  - proficiency_service（CHK-001 熟练派生）
  - spell_sources（SPL-003 法术来源）
  - effect_dsl（SPL-008 效果DSL）
  - levelup_plan（CHR-007 升级计划）
  - opportunity_attack（COM-009 借机攻击）
  - performance_cache（PERF-001 聚合快照）
  - choice_record（CHAR-008 选择轨迹）
  - travel（EXP-002 旅行）
  - triggers（COM-013 触发）
  - vision（ENV-001 视觉）
  - aoe（SPL-007 区域）
  - encumbrance（负重）
  - hazards（危害）
  - core_loop（核心循环）
"""

from __future__ import annotations

import pytest


# ── STATE-003: unit_of_work ─────────────────────────────────────

class TestUnitOfWork:
    def test_idempotency_store(self):
        from aidm.engine.unit_of_work import CommandResult, IdempotencyStore
        store = IdempotencyStore()
        store.record(CommandResult(command_id="c1", idempotency_key="k1",
                                   success=True, result_data={"ok": True}))
        cached = store.check("k1")
        assert cached is not None
        assert cached.result_data == {"ok": True}
        assert store.check("k2") is None

    def test_execute_command_idempotent(self):
        from aidm.engine.unit_of_work import execute_command
        from aidm.engine.command import Command

        calls = {"n": 0}

        def handler(uow):
            calls["n"] += 1
            uow.add_event({"type": "test"})
            return {"result": calls["n"]}

        cmd = Command.create(campaign_id=1, actor_id="a1",
                             command_type="Test", payload={},
                             idempotency_key="session:seq1")
        r1 = execute_command(cmd, handler)
        r2 = execute_command(cmd, handler)
        assert r1.success
        assert calls["n"] == 1  # 重复提交不重执行

    def test_rollback_on_error(self):
        from aidm.engine.unit_of_work import execute_command
        from aidm.engine.command import Command

        def handler(uow):
            raise ValueError("boom")

        cmd = Command.create(campaign_id=1, actor_id="a1",
                             command_type="Test", payload={})
        result = execute_command(cmd, handler)
        assert not result.success
        assert "boom" in result.error


# ── CHK-001: proficiency_service ────────────────────────────────

class TestProficiencyService:
    def test_skill_modifier(self):
        from aidm.engine.proficiency_service import (
            CheckService, ProficiencyGrant, ProficiencyLevel,
            ProficiencyRegistry, ProficiencyType,
        )
        reg = ProficiencyRegistry()
        reg.add(ProficiencyGrant(grant_type=ProficiencyType.SKILL,
                                 item="察觉", level=ProficiencyLevel.PROFICIENT))
        svc = CheckService(registry=reg, proficiency_bonus=2)
        assert svc.is_skill_proficient("察觉")
        assert svc.get_skill_modifier("察觉", 3) == 5  # 3+2
        assert not svc.is_skill_proficient("运动")
        assert svc.get_skill_modifier("运动", 3) == 3  # 无熟练

    def test_expertise_double(self):
        from aidm.engine.proficiency_service import (
            CheckService, ProficiencyGrant, ProficiencyLevel,
            ProficiencyRegistry, ProficiencyType,
        )
        reg = ProficiencyRegistry()
        reg.add(ProficiencyGrant(grant_type=ProficiencyType.SKILL,
                                 item="潜行", level=ProficiencyLevel.EXPERT))
        svc = CheckService(registry=reg, proficiency_bonus=2)
        assert svc.get_skill_modifier("潜行", 3) == 7  # 3+2*2


# ── SPL-003: spell_sources ──────────────────────────────────────

class TestSpellSources:
    def test_registry_castable(self):
        from aidm.engine.spell_sources import (
            SpellAcquisition, SpellSource, SpellSourceRegistry,
        )
        reg = SpellSourceRegistry()
        reg.add(SpellAcquisition(spell_name="火球术",
                                 source_type=SpellSource.KNOWN))
        assert reg.can_cast("火球术")
        assert not reg.can_cast("流星爆")

    def test_prepared_spell(self):
        from aidm.engine.spell_sources import (
            SpellAcquisition, SpellSource, SpellSourceRegistry,
        )
        reg = SpellSourceRegistry()
        reg.add(SpellAcquisition(spell_name="光亮术",
                                 source_type=SpellSource.PREPARED,
                                 can_prepare=True))
        assert not reg.can_cast("光亮术")  # 未准备
        assert reg.prepare_spell("光亮术")
        assert reg.can_cast("光亮术")  # 已准备


# ── SPL-008: effect_dsl ─────────────────────────────────────────

class TestEffectDsl:
    def test_executor_damage(self):
        from aidm.engine.effect_dsl import (
            EffectDefinition, EffectOpType, EffectOperation, EffectExecutor,
        )
        eff = EffectDefinition(
            name="火焰伤害",
            operations=[EffectOperation(op=EffectOpType.DEAL_DAMAGE,
                                         params={"amount": 10, "damage_type": "fire"})],
        )
        events = EffectExecutor().execute(eff, {"target_id": "t1"})
        assert events[0]["event_type"] == "damage_dealt"
        assert events[0]["amount"] == 10

    def test_executor_condition(self):
        from aidm.engine.effect_dsl import (
            EffectDefinition, EffectOpType, EffectOperation, EffectExecutor,
        )
        eff = EffectDefinition(
            name="中毒",
            operations=[EffectOperation(op=EffectOpType.APPLY_CONDITION,
                                         params={"condition": "中毒"})],
        )
        events = EffectExecutor().execute(eff, {"target_id": "t1"})
        assert events[0]["event_type"] == "condition_applied"
        assert events[0]["condition"] == "中毒"


# ── CHR-007: levelup_plan ───────────────────────────────────────

class TestLevelupPlan:
    def test_hp_gain(self):
        from aidm.engine.levelup_plan import LevelUpPlan
        plan = LevelUpPlan(hit_die=10, hp_gain_avg=6, con_modifier=3)
        assert plan.compute_hp_gain() == 9  # 6+3

    def test_feat_validation(self):
        from aidm.engine.levelup_plan import LevelUpPlan
        plan = LevelUpPlan(feat_available=True, feat_choices=["幸运", "警戒"])
        assert plan.validate_feat_selection("幸运")
        assert not plan.validate_feat_selection("不存在")


# ── COM-009: opportunity_attack ─────────────────────────────────

class TestOpportunityAttack:
    def test_can_make(self):
        from aidm.engine.combat import Combatant
        from aidm.engine.opportunity_attack import can_make_opportunity_attack
        attacker = Combatant(cid="a1", name="战士", dex_mod=2, side="player",
                             is_player=True, hp=30, hp_max=30)
        target = Combatant(cid="t1", name="哥布林", dex_mod=1, side="enemy",
                           hp=7, hp_max=7)
        # 目标离开触及范围且未撤离 → 可借机攻击
        assert can_make_opportunity_attack(attacker, target,
                                           target_leaving_reach=True)
        # 撤离（disengage_active=True）→ 不可借机攻击
        disengaging = Combatant(cid="t2", name="哥布林2", dex_mod=1, side="enemy",
                                hp=7, hp_max=7, disengage_active=True)
        assert not can_make_opportunity_attack(attacker, disengaging,
                                               target_leaving_reach=True)
        # 传送 → 不可借机攻击
        assert not can_make_opportunity_attack(attacker, target,
                                               movement_type="teleport")


# ── PERF-001: performance_cache ─────────────────────────────────

class TestPerformanceCache:
    def test_rule_cache_versioning(self):
        from aidm.engine.performance_cache import RuleDefinitionCache
        cache = RuleDefinitionCache()
        cache.set_version("2024.1")
        cache.set("fireball", {"dice": "8d6"})
        assert cache.get("fireball") == {"dice": "8d6"}
        cache.set_version("2024.2")  # 版本变更 → 清空
        assert cache.get("fireball") is None


# ── CHAR-008: choice_record ─────────────────────────────────────

class TestChoiceRecord:
    def test_grant_log(self):
        from aidm.engine.choice_record import (
            CharacterBuildLog, ChoiceRecord, Grant, GrantType,
        )
        log = CharacterBuildLog(character_id="c1")
        log.add_grant(Grant(grant_type=GrantType.SKILL, source_id="background.侍僧",
                            granted_item="洞悉", level=1))
        log.add_choice(ChoiceRecord(choice_type="skill", selected_value="洞悉",
                                    validated=True))
        grants = log.get_grants_by_type(GrantType.SKILL)
        assert len(grants) == 1
        d = log.to_dict()
        assert d["character_id"] == "c1"
        assert len(d["grants"]) == 1


# ── EXP-002: travel ─────────────────────────────────────────────

class TestTravel:
    def test_travel_distance(self):
        from aidm.engine.travel import travel_daily_distance, travel_distance
        dist = travel_distance("normal", hours=8)
        assert dist > 0
        daily = travel_daily_distance("normal")
        assert daily > 0


# ── ENV-001: vision ─────────────────────────────────────────────

class TestVision:
    def test_vision_mechanics(self):
        from aidm.engine.vision import can_see, darkvision_effective_light
        # 黑暗视觉 60尺，目标距离 30尺，黑暗中（darkness）→ 有效光照变为微光
        light = darkvision_effective_light("darkness", darkvision_range_ft=60,
                                           distance_ft=30)
        assert light == "dim"  # 黑暗视为微光
        # 综合判定：有黑暗视觉且距离在范围内 → 可见
        result = can_see(
            observer_senses={"darkvision_ft": 60},
            target_light="darkness",
            distance_ft=30,
        )
        assert result["can_see"] is True


# ── SPL-007: aoe ────────────────────────────────────────────────

class TestAoe:
    def test_sphere_targets(self):
        from aidm.engine.aoe import targets_in_sphere
        targets = targets_in_sphere(
            origin=(0, 0), radius_ft=20,
            all_positions={"a": (0, 0), "b": (5, 0), "c": (50, 0)},
        )
        assert "a" in targets
        assert "b" in targets
        assert "c" not in targets


# ── COM-013: triggers ───────────────────────────────────────────

class TestTriggers:
    def test_reaction_trigger_match(self):
        from aidm.engine.triggers import KNOWN_REACTION_TRIGGERS, check_trigger
        trigger = KNOWN_REACTION_TRIGGERS["护盾术"]
        # 被攻击命中事件 → 匹配（护盾术无距离限制）
        assert check_trigger(trigger, {"type": "hit_by_attack",
                                       "distance_ft": 30}) is True
        # 其他事件 → 不匹配
        assert check_trigger(trigger, {"type": "creature_cast_spell",
                                       "distance_ft": 30}) is False

    def test_counter_spell_range(self):
        from aidm.engine.triggers import KNOWN_REACTION_TRIGGERS, check_trigger
        trigger = KNOWN_REACTION_TRIGGERS["法术反制"]
        # 60尺内施法 → 匹配
        assert check_trigger(trigger, {"type": "creature_cast_spell",
                                       "distance_ft": 30}) is True
        # 超60尺 → 不匹配
        assert check_trigger(trigger, {"type": "creature_cast_spell",
                                       "distance_ft": 100}) is False


# ── 负重 / 危害 / 核心循环 ─────────────────────────────────────

class TestMiscEngine:
    def test_encumbrance(self):
        from aidm.engine.encumbrance import carrying_capacity
        cap = carrying_capacity(strength_score=16)
        assert cap >= 200  # 16*15 = 240

    def test_hazards(self):
        from aidm.engine.hazards import fall_damage, burning_damage
        d = fall_damage(20)
        assert d["dice_count"] == 2  # 20尺 → 2d6
        assert d["damage_type"] == "钝击"
        b = burning_damage()
        assert b["damage_dice"] == "1d4"

    def test_core_loop(self):
        from aidm.engine.core_loop import dc_by_difficulty
        assert dc_by_difficulty("中等") == 15
