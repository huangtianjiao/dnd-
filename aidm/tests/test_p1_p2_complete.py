"""P1/P2 完整实现验证测试。

覆盖规格包中的关键 P1/P2 项：
  - MON-002: 充能/传奇动作/传奇抗性/巢穴动作
  - SPL-006: 多射线与多目标分配
  - SPL-007: 目标、范围、区域与视线合法性
  - SPL-009: 持续时间和结束条件时间调度
  - SPL-011: 姿势/材料/法器判断
  - SPL-012: 有价/消耗材料真实扣除
  - SPL-015: 时机型法术触发窗口
  - SPL-016: 召唤/变形/创造物实体生命周期
  - ITEM-001: 物品实例化
  - ITEM-004: 魔法物品充能
  - CHR-002: 子职进度
  - REST-002: 休息状态机
  - REST-003: 通用资源恢复
  - TEST-003: RngContext 可重放
  - EXP-003: 停工期制作
  - OBS-001: 修正来源解释
  - INT-002: 目标解析消歧
  - ITEM-003: 同调先决条件
"""

from __future__ import annotations

import pytest


# ── MON-002: 充能/传奇动作/传奇抗性/巢穴动作 ─────────────────────

class TestMonsterActions:
    def test_recharge_tracker(self):
        from aidm.engine.legendary_actions import RechargeTracker
        t = RechargeTracker(current_charges=1, max_charges=1)
        assert t.can_use()
        assert t.consume()
        assert not t.can_use()
        t.recharge_at_turn_start()
        assert t.can_use()  # 回合开始恢复

    def test_legendary_pool(self):
        from aidm.engine.legendary_actions import LegendaryAction, LegendaryActionPool
        pool = LegendaryActionPool(
            actions=[LegendaryAction(action_id="bite", name="Bite", cost=1)],
            uses_per_round=3,
        )
        assert pool.can_use_action("bite")
        assert pool.use_action("bite")
        assert pool.uses_this_round == 1
        pool.reset_round()
        assert pool.uses_this_round == 0

    def test_legendary_resistance(self):
        from aidm.engine.legendary_actions import LegendaryResistance
        lr = LegendaryResistance(uses_per_day=3)
        assert lr.can_resist()
        assert lr.resist()
        assert lr.uses_today == 1
        lr.reset_day()
        assert lr.uses_today == 0

    def test_lair_actions(self):
        from aidm.engine.legendary_actions import LairAction, LairActionManager
        mgr = LairActionManager()
        mgr.add_action(LairAction(action_id="lair1", name="地陷", initiative_count=20))
        acts = mgr.get_actions_at_initiative(20)
        assert len(acts) == 1


# ── SPL-006: 多射线与多目标分配 ─────────────────────────────────

class TestMultiRaySpell:
    def test_ray_distribution(self):
        from aidm.engine.multiray_spell import resolve_multi_ray_spell
        result = resolve_multi_ray_spell(
            spell_name="Eldritch Blast",
            num_rays=3,
            target_assignments=["goblin1", "goblin2", "goblin1"],
            target_acs={"goblin1": 15, "goblin2": 12},
            damage_per_ray=5,
        )
        assert result.total_rays == 3
        assert len(result.rays) == 3
        # 目标A承受第1、3枚射线
        assert len(result.get_rays_for_target("goblin1")) == 2


# ── SPL-007: 目标/范围/区域/视线合法性 ──────────────────────────

class TestSpellTargeting:
    def test_out_of_range_excluded(self):
        from aidm.engine.spell_targeting_ext import (
            RangeSpec, TargetSpec, validate_spell_targets,
        )
        result = validate_spell_targets(
            range_spec=RangeSpec(range_ft=30.0),
            target_spec=TargetSpec(target_count=1),
            area_spec=None,
            caster_pos=(0.0, 0.0),
            candidate_positions={"a": (10, 0), "b": (100, 0)},
        )
        assert "a" in result.valid_targets
        assert "b" in result.out_of_range

    def test_invisible_excluded(self):
        from aidm.engine.spell_targeting_ext import (
            RangeSpec, TargetSpec, validate_spell_targets,
        )
        result = validate_spell_targets(
            range_spec=RangeSpec(range_ft=30.0),
            target_spec=TargetSpec(target_count=1, requires_visibility=True),
            area_spec=None,
            caster_pos=(0.0, 0.0),
            candidate_positions={"a": (10, 0)},
            is_visible={"a": False},
        )
        assert "a" in result.invisible
        assert result.valid_targets == []


# ── SPL-009: 持续时间调度 ───────────────────────────────────────

class TestSpellDuration:
    def test_scheduler_tick(self):
        from aidm.engine.spell_duration import (
            DurationScheduler, DurationSpec, DurationType, ScheduledEffect,
        )
        sched = DurationScheduler()
        eff = ScheduledEffect(
            effect_id="e1", spell_id="bless", target_entity_id="c1",
            duration=DurationSpec(duration_type=DurationType.ROUNDS, value=2, remaining=2),
        )
        sched.schedule(eff)
        events = sched.tick_round()
        assert events == []  # 还剩1轮
        events = sched.tick_round()
        assert len(events) == 1  # 过期
        assert events[0]["type"] == "effect_expired"

    def test_until_rest_expire(self):
        from aidm.engine.spell_duration import (
            DurationScheduler, DurationSpec, DurationType, ScheduledEffect,
        )
        sched = DurationScheduler()
        sched.schedule(ScheduledEffect(
            effect_id="e2", spell_id="aid", target_entity_id="c1",
            duration=DurationSpec(duration_type=DurationType.UNTIL_REST),
        ))
        events = sched.expire_all_on_rest()
        assert len(events) == 1


# ── SPL-011/012: 成分与材料 ─────────────────────────────────────

class TestComponents:
    def test_free_hands(self):
        from aidm.engine.component_check import (
            ComponentType, EquipmentSlotState, check_casting_components,
        )
        # 单手持武器 + 材料包 → S+M 可行
        result = check_casting_components(
            components={ComponentType.SOMATIC, ComponentType.MATERIAL},
            equipment=EquipmentSlotState(main_hand="匕首"),
            inventory=["材料包"],
        )
        assert result.can_cast
        assert result.free_hands == 1

    def test_missing_focus(self):
        from aidm.engine.component_check import (
            ComponentType, EquipmentSlotState, check_casting_components,
        )
        # 无法器无材料包且双手占用 → M 成分失败
        result = check_casting_components(
            components={ComponentType.MATERIAL},
            equipment=EquipmentSlotState(main_hand="巨剑", off_hand="盾牌"),
            inventory=[],
        )
        assert not result.can_cast

    def test_material_consumed(self):
        from aidm.engine.material_cost import MaterialRequirement, MaterialTracker
        tracker = MaterialTracker()
        tracker.add_material("硫磺", 5)
        req = MaterialRequirement(item_tag="硫磺", quantity=1, consumed=True)
        assert tracker.has_material(req)
        assert tracker.consume_material(req)
        assert tracker.get_quantity("硫磺") == 4


# ── SPL-015: 触发窗口 ───────────────────────────────────────────

class TestTriggerWindow:
    def test_find_reactions(self):
        from aidm.engine.spell_trigger_window import (
            PendingTrigger, TriggerPoint, TriggerWindow, TriggerWindowRegistry,
        )
        reg = TriggerWindowRegistry()
        reg.register(TriggerWindow(
            spell_id="shield", trigger_point=TriggerPoint.ATTACK_HIT_BEFORE_DAMAGE,
        ))
        matches = reg.find_reactions(PendingTrigger(
            trigger_point=TriggerPoint.ATTACK_HIT_BEFORE_DAMAGE,
            source_entity_id="enemy1",
        ))
        assert len(matches) == 1
        assert matches[0].spell_id == "shield"


# ── SPL-016: 实体生命周期 ───────────────────────────────────────

class TestEntityLifecycle:
    def test_summon_despawn(self):
        from aidm.engine.entity_lifecycle_ext import EntityLifecycleManager
        mgr = EntityLifecycleManager()
        entity = mgr.summon(
            summoner_id="wizard1", spell_id="summon_familiar",
            stat_block={"hp": 10}, duration=10, concentration_id="conc1",
        )
        assert entity.active
        despawned = mgr.despawn_by_concentration("conc1")
        assert len(despawned) == 1
        assert not entity.active


# ── ITEM-001: 物品实例化 ────────────────────────────────────────

class TestItemInstance:
    def test_quantity_and_value(self):
        from aidm.engine.item_instance import ItemInstance
        inst = ItemInstance(instance_id="i1", item_id="arrows", name="箭矢",
                            quantity=20, value_gp=0.05, weight_lb=0.05)
        assert inst.quantity == 20
        assert inst.total_value() == pytest.approx(1.0)
        assert inst.total_weight() == pytest.approx(1.0)

    def test_inventory_manager(self):
        from aidm.engine.item_instance import InventoryManager, ItemInstance
        mgr = InventoryManager()
        potion = ItemInstance(instance_id="p1", item_id="potion", name="治疗药水", quantity=3)
        mgr.add_item(potion)
        assert mgr.get_item("p1").quantity == 3
        assert mgr.list_all() == [potion]


# ── ITEM-004: 魔法物品充能 ──────────────────────────────────────

class TestItemCharges:
    def test_recharge(self):
        from aidm.engine.item_charges import (
            ItemChargeRegistry, RechargeSpec, RechargeType,
        )
        reg = ItemChargeRegistry()
        reg.register("wand1", charges=3, max_charges=3,
                     recharge_spec=RechargeSpec(recharge_on=RechargeType.DAWN, max_charges=3))
        assert reg.can_activate("wand1")
        assert reg.consume_charge("wand1")
        assert reg.get("wand1").charges == 2
        recharged = reg.recharge_all(RechargeType.DAWN)
        assert "wand1" in recharged
        assert reg.get("wand1").charges == 3


# ── CHR-002: 子职进度 ───────────────────────────────────────────

class TestSubclassProgression:
    def test_feature_granting(self):
        from aidm.engine.subclass_progression import (
            SubclassFeature, SubclassProgression, SubclassRegistry,
        )
        prog = SubclassProgression(subclass_name="龙脉术士", base_class="术士")
        prog.add_feature(SubclassFeature(name="龙族血统", level=3))
        prog.add_feature(SubclassFeature(name="龙翼", level=14))
        assert len(prog.get_features_at_level(3)) == 1
        assert len(prog.get_all_features_up_to(14)) == 2

        reg = SubclassRegistry()
        reg.register(prog)
        assert reg.get("术士", "龙脉术士") is prog


# ── REST-002: 休息状态机 ────────────────────────────────────────

class TestRestState:
    def test_short_rest_complete(self):
        from aidm.engine.rest_state import RestPhase, RestStateRegistry
        reg = RestStateRegistry()
        session = reg.start_rest("char1", "short", game_minutes=100)
        assert session.phase == RestPhase.RESTING
        session.advance(60)  # 短休60分钟
        assert session.phase == RestPhase.COMPLETED
        assert session.is_beneficial()

    def test_rest_interrupted(self):
        from aidm.engine.rest_state import RestPhase, RestStateRegistry
        reg = RestStateRegistry()
        session = reg.start_rest("char2", "long", game_minutes=100)
        session.advance(30)
        session.interrupt(reason="战斗")
        assert session.phase == RestPhase.INTERRUPTED
        assert session.get_benefit_multiplier() < 1.0


# ── REST-003: 通用资源恢复 ──────────────────────────────────────

class TestResourceRecharge:
    def test_resource_pool_recharge(self):
        from aidm.engine.recharge_spec import (
            RechargeSpec, RechargeTrigger, ResourceManager, ResourcePool,
        )
        mgr = ResourceManager()
        mgr.register_pool("char1", ResourcePool(
            name="狂暴", current=0, max_value=2,
            recharge_spec=RechargeSpec(
                recharge_on=RechargeTrigger.SHORT_REST, restore_amount=0, max_value=2),
        ))
        events = mgr.recharge_all(RechargeTrigger.SHORT_REST)
        assert len(events) == 1
        pool = mgr.get_pool("char1", "狂暴")
        assert pool.current == 2


# ── TEST-003: RngContext 可重放 ─────────────────────────────────

class TestRngContext:
    def test_deterministic(self):
        from aidm.engine.rng_context import create_rng_context
        rng1 = create_rng_context(seed=42)
        rng2 = create_rng_context(seed=42)
        assert rng1.roll_d20().total == rng2.roll_d20().total
        assert rng1.roll_dice("2d6").total == rng2.roll_dice("2d6").total

    def test_roll_recording(self):
        from aidm.engine.rng_context import create_rng_context
        rng = create_rng_context(seed=7)
        rng.roll_d20()
        rng.roll_dice("1d8")
        assert len(rng.get_all_rolls()) == 2


# ── EXP-003: 停工期制作 ─────────────────────────────────────────

class TestDowntimeCraft:
    def test_project_progress(self):
        from aidm.engine.downtime_craft import (
            DowntimeManager, ProjectDefinition, ProjectStatus,
        )
        mgr = DowntimeManager()
        proj = ProjectDefinition(project_id="p1", name="锻造长剑", total_work_days=5.0)
        mgr.start_project(proj, game_day=10)
        assert proj.status == ProjectStatus.IN_PROGRESS
        mgr.advance_project("p1", days=5.0, game_day=15)
        assert proj.is_complete()
        assert proj.status == ProjectStatus.COMPLETED


# ── OBS-001: 修正来源解释 ───────────────────────────────────────

class TestResolutionTrace:
    def test_formula_tree(self):
        from aidm.engine.resolution_trace_ext import ResolutionTrace
        trace = ResolutionTrace(action_type="attack")
        trace.d20_roll = 15
        trace.base_modifier = 3
        trace.add_modifier("proficiency", "prof", "熟练加值", 2)
        trace.add_modifier("condition", "exhaustion", "力竭", -2)
        trace.total = 18
        tree = trace.build_formula_tree()
        assert tree.value == 18
        assert len(trace.get_active_modifiers()) == 2


# ── INT-002: 目标解析消歧 ───────────────────────────────────────

class TestTargetQuery:
    def test_clarification_required(self):
        from aidm.engine.target_query import (
            CandidateTarget, TargetQuery, TargetType, resolve_target,
        )
        query = TargetQuery(raw_text="goblin", target_type=TargetType.ENEMY, max_range_ft=30)
        candidates = [
            CandidateTarget(target_id="g1", name="Goblin A", target_type=TargetType.ENEMY, distance_ft=15),
            CandidateTarget(target_id="g2", name="Goblin B", target_type=TargetType.ENEMY, distance_ft=20),
        ]
        result = resolve_target(query, candidates)
        assert result.needs_clarification
        assert not result.is_resolved

    def test_unique_target(self):
        from aidm.engine.target_query import (
            CandidateTarget, TargetQuery, TargetType, resolve_target,
        )
        query = TargetQuery(raw_text="goblin", target_type=TargetType.ENEMY, max_range_ft=30)
        candidates = [CandidateTarget(target_id="g1", name="Goblin A",
                                      target_type=TargetType.ENEMY, distance_ft=15)]
        result = resolve_target(query, candidates)
        assert result.is_resolved
        assert result.target.target_id == "g1"


# ── ITEM-003: 同调先决条件 ─────────────────────────────────────

class TestAttunement:
    def test_attunement_requires_level(self):
        from aidm.engine.magic_item_def import (
            AttunementRequirement, AttunementService, MagicItemDefinition,
        )
        item = MagicItemDefinition(
            item_id="item.legendary_sword", name="传说之剑", rarity="legendary",
            requires_attunement=True,
            attunement_requirements=AttunementRequirement(min_level=17),
        )
        svc = AttunementService()
        # 等级不足 → 拒绝
        assert not svc.attune("char1", "item.legendary_sword", item, character_level=5)
        # 等级足够 → 成功
        assert svc.attune("char1", "item.legendary_sword", item, character_level=17)

    def test_max_attuned(self):
        from aidm.engine.magic_item_def import (
            AttunementService, MagicItemDefinition,
        )
        svc = AttunementService()
        for i in range(3):
            item = MagicItemDefinition(item_id=f"item.wand{i}", name=f"魔杖{i}", requires_attunement=True)
            assert svc.attune("char2", f"item.wand{i}", item)
        # 第4件 → 拒绝
        item4 = MagicItemDefinition(item_id="item.wand3", name="魔杖3", requires_attunement=True)
        assert not svc.attune("char2", "item.wand3", item4)
