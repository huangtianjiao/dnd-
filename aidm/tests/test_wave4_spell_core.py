"""Wave 4 测试 — 施法核心机制。

覆盖:
  - SPL-004: SpellSlotCalculator 法术位进度表（全/半/1/3/魔契）
  - SPL-005: SaveOutcome 豁免结果声明制
  - SPL-006: resolve_multi_ray_spell 多射线/多目标分配
  - SPL-007: SpellTargetingService 目标/范围/区域验证
  - SPL-009: DurationScheduler 持续时间调度
"""

import pytest

# ── SPL-004 imports ──
from aidm.engine.spell_slots import (
    FULL_CASTER_SLOTS,
    FULL_CASTERS,
    HALF_CASTER_SLOTS,
    HALF_CASTERS,
    PATRON_SLOTS,
    PACT_CASTERS,
    SpellSlotCalculator,
    THIRD_CASTERS,
    get_combined_slots,
    get_max_slots,
)

# ── SPL-005 imports ──
from aidm.engine.spellcasting import (
    SaveOutcome,
    resolve_save_outcome,
)
from aidm.data.spells import get_spell

# ── SPL-006 imports ──
from aidm.engine.spellcasting import (
    CasterState,
    MultiTargetSpellResult,
    SpellTarget,
    resolve_multi_ray_spell,
)

# ── SPL-007 imports ──
from aidm.engine.spell_targeting import (
    AreaShape,
    AreaSpec,
    RangeSpec,
    SpellTargetingService,
    TargetSpec,
    TargetType,
    get_spell_target_spec,
)

# ── SPL-009 imports ──
from aidm.engine.scheduler import (
    DurationScheduler,
    RepeatSave,
    ScheduledEffect,
    SchedulerDurationType,
)


# ════════════════════════════════════════════════════════════════════════
# SPL-004: 法术位进度表
# ════════════════════════════════════════════════════════════════════════

class TestSpellSlotCalculator:
    """SPL-004 法术位进度表测试。"""

    def test_full_caster_level_1(self):
        """1级全施法者有2个1环位。"""
        slots = SpellSlotCalculator.slots_for_class_level("法师", 1)
        assert slots == {1: 2}

    def test_full_caster_level_5(self):
        """5级全施法者有 4/3/2 个法术位。"""
        slots = SpellSlotCalculator.slots_for_class_level("法师", 5)
        assert slots == {1: 4, 2: 3, 3: 2}

    def test_full_caster_level_20(self):
        """20级全施法者有9环位。"""
        slots = SpellSlotCalculator.slots_for_class_level("术士", 20)
        assert slots[9] == 1
        assert slots[1] == 4

    def test_full_caster_all_classes(self):
        """所有全施法者职业均可查表。"""
        for cls in FULL_CASTERS:
            slots = SpellSlotCalculator.slots_for_class_level(cls, 10)
            assert 1 in slots

    def test_half_caster_level_1(self):
        """1级半施法者无法术位。"""
        slots = SpellSlotCalculator.slots_for_class_level("圣武士", 1)
        assert slots == {}

    def test_half_caster_level_2(self):
        """2级半施法者有2个1环位。"""
        slots = SpellSlotCalculator.slots_for_class_level("圣武士", 2)
        assert slots == {1: 2}

    def test_half_caster_level_5(self):
        """5级半施法者有 4/2 个法术位。"""
        slots = SpellSlotCalculator.slots_for_class_level("游侠", 5)
        assert slots == {1: 4, 2: 2}

    def test_half_caster_level_9(self):
        """9级半施法者有3环位。"""
        slots = SpellSlotCalculator.slots_for_class_level("圣武士", 9)
        assert 3 in slots
        assert slots[3] == 2

    def test_pact_caster_level_1(self):
        """1级魔契师有1个1环位。"""
        slots = SpellSlotCalculator.slots_for_class_level("魔契师", 1)
        assert slots == {1: 1}

    def test_pact_caster_level_4(self):
        """4级魔契师有2个2环位。"""
        slots = SpellSlotCalculator.slots_for_class_level("魔契师", 4)
        assert slots == {2: 2}

    def test_pact_caster_level_11(self):
        """11级魔契师有2个3环位。"""
        slots = SpellSlotCalculator.slots_for_class_level("魔契师", 11)
        assert slots == {3: 2}

    def test_pact_slot_level(self):
        """魔契师法术位环阶随等级提升。"""
        assert SpellSlotCalculator.pact_slot_level(1) == 1
        assert SpellSlotCalculator.pact_slot_level(4) == 2
        assert SpellSlotCalculator.pact_slot_level(11) == 3
        assert SpellSlotCalculator.pact_slot_level(17) == 4

    def test_non_caster_returns_empty(self):
        """非施法职业返回空法术位。"""
        slots = SpellSlotCalculator.slots_for_class_level("战士", 5)
        assert slots == {}

    def test_multiclass_caster_level_full(self):
        """兼职全施法者等级相加。"""
        assert SpellSlotCalculator.multiclass_caster_level({"法师": 5}) == 5
        assert SpellSlotCalculator.multiclass_caster_level({"法师": 3, "牧师": 2}) == 5

    def test_multiclass_caster_level_half(self):
        """半施法者等级÷2。"""
        assert SpellSlotCalculator.multiclass_caster_level({"圣武士": 6}) == 3
        assert SpellSlotCalculator.multiclass_caster_level({"法师": 3, "圣武士": 4}) == 5

    def test_multiclass_pact_excluded(self):
        """魔契师不参与合并。"""
        assert SpellSlotCalculator.multiclass_caster_level({"魔契师": 5}) == 0
        assert SpellSlotCalculator.multiclass_caster_level({"法师": 3, "魔契师": 5}) == 3

    def test_calculate_slots_combined(self):
        """合并法术位计算。"""
        slots = SpellSlotCalculator.calculate_slots({"法师": 5})
        assert slots == {1: 4, 2: 3, 3: 2}

    def test_calculate_slots_multiclass(self):
        """兼职合并法术位。"""
        slots = SpellSlotCalculator.calculate_slots({"法师": 3, "圣武士": 4})
        assert slots[3] == 2  # 5级施法者

    def test_convenience_functions(self):
        """便捷函数等价于计算器方法。"""
        assert get_max_slots("法师", 5) == {1: 4, 2: 3, 3: 2}
        assert get_combined_slots({"法师": 3, "牧师": 2})[3] == 2

    def test_full_table_coverage(self):
        """全施法者表覆盖1-20级。"""
        for level in range(1, 21):
            assert level in FULL_CASTER_SLOTS

    def test_half_table_coverage(self):
        """半施法者表覆盖1-20级。"""
        for level in range(1, 21):
            assert level in HALF_CASTER_SLOTS

    def test_pact_table_coverage(self):
        """魔契师表覆盖1-20级。"""
        for level in range(1, 21):
            assert level in PATRON_SLOTS


# ════════════════════════════════════════════════════════════════════════
# SPL-005: 豁免结果声明制
# ════════════════════════════════════════════════════════════════════════

class TestSaveOutcome:
    """SPL-005 豁免结果声明制测试。"""

    def test_enum_values(self):
        """SaveOutcome 有四种值。"""
        assert SaveOutcome.NONE == "none"
        assert SaveOutcome.HALF == "half"
        assert SaveOutcome.ALTERNATE == "alternate"
        assert SaveOutcome.NEGATE == "negate"

    def test_fireball_half(self):
        """火球术: half_on_save=True → HALF。"""
        spell = get_spell("火球术")
        assert resolve_save_outcome(spell) == SaveOutcome.HALF

    def test_sacred_flame_none(self):
        """圣火术: half_on_save=False + 有伤害 → NONE。"""
        spell = get_spell("圣火术")
        assert resolve_save_outcome(spell) == SaveOutcome.NONE

    def test_lightning_bolt_half(self):
        """闪电束: half_on_save=True → HALF。"""
        spell = get_spell("闪电束")
        assert resolve_save_outcome(spell) == SaveOutcome.HALF

    def test_enum_is_str(self):
        """SaveOutcome 是 str 枚举。"""
        assert isinstance(SaveOutcome.HALF, str)
        assert SaveOutcome.HALF == "half"


# ════════════════════════════════════════════════════════════════════════
# SPL-006: 多射线/多目标分配
# ════════════════════════════════════════════════════════════════════════

class TestMultiRaySpell:
    """SPL-006 多射线/多目标分配测试。"""

    def _make_caster(self, level: int = 5) -> CasterState:
        return CasterState(
            caster_id="test_caster",
            class_name="法师",
            level=level,
            ability_scores={"INT": 16, "STR": 10, "DEX": 14, "CON": 12, "WIS": 10, "CHA": 8},
            spell_slots={1: 4, 2: 3, 3: 2},
            max_spell_slots={1: 4, 2: 3, 3: 2},
        )

    def test_spell_target_dataclass(self):
        """SpellTarget 数据结构。"""
        st = SpellTarget(target_id="goblin_1", attack_roll=15, is_hit=True, damage=10)
        assert st.target_id == "goblin_1"
        assert st.is_hit is True
        assert st.damage == 10

    def test_multi_target_spell_result(self):
        """MultiTargetSpellResult 数据结构。"""
        result = MultiTargetSpellResult(spell_id="灼热射线", spell_name="灼热射线")
        result.targets.append(SpellTarget(target_id="g1", damage=7))
        d = result.to_dict()
        assert d["spell"] == "灼热射线"
        assert len(d["targets"]) == 1

    def test_resolve_multi_ray_empty_targets(self):
        """空目标列表返回空结果。"""
        caster = self._make_caster()
        result = resolve_multi_ray_spell("灼热射线", caster, [])
        assert len(result.targets) == 0

    def test_resolve_multi_ray_single_target(self):
        """单目标多射线 — 所有射线指向同一目标。"""
        caster = self._make_caster()
        result = resolve_multi_ray_spell(
            "灼热射线", caster, ["goblin_1"],
        )
        # 灼热射线基础3道射线
        assert len(result.targets) == 3
        for t in result.targets:
            assert t.target_id == "goblin_1"

    def test_resolve_multi_ray_multiple_targets(self):
        """多目标分配 — 射线分配到不同目标。"""
        caster = self._make_caster()
        result = resolve_multi_ray_spell(
            "灼热射线", caster, ["goblin_1", "goblin_2", "goblin_3"],
        )
        assert len(result.targets) == 3
        target_ids = {t.target_id for t in result.targets}
        assert target_ids == {"goblin_1", "goblin_2", "goblin_3"}

    def test_resolve_multi_ray_events(self):
        """每道射线产生独立事件。"""
        caster = self._make_caster()
        result = resolve_multi_ray_spell(
            "灼热射线", caster, ["g1", "g2"],
        )
        assert len(result.events) == 3
        for ev in result.events:
            assert ev["type"] == "ray_attack"

    def test_resolve_multi_ray_upcast(self):
        """升环增加射线数。"""
        caster = self._make_caster(level=9)
        result = resolve_multi_ray_spell(
            "灼热射线", caster, ["g1"],
            context={"slot_level": 3},  # 升1环 → 3+1=4道射线
        )
        assert len(result.targets) == 4


# ════════════════════════════════════════════════════════════════════════
# SPL-007: 目标/范围/区域合法性验证
# ════════════════════════════════════════════════════════════════════════

class TestSpellTargetingService:
    """SPL-007 法术目标验证服务测试。"""

    def test_target_type_enum(self):
        """TargetType 枚举值。"""
        assert TargetType.SELF == "self"
        assert TargetType.CREATURE == "creature"
        assert TargetType.WILLING_CREATURE == "willing_creature"
        assert TargetType.VISIBLE_CREATURE == "visible_creature"

    def test_area_shape_enum(self):
        """AreaShape 枚举值。"""
        assert AreaShape.SPHERE == "sphere"
        assert AreaShape.CONE == "cone"
        assert AreaShape.LINE == "line"
        assert AreaShape.CUBE == "cube"

    def test_range_spec_defaults(self):
        """RangeSpec 默认值。"""
        rs = RangeSpec()
        assert rs.range_ft == 0
        assert rs.is_touch is False
        assert rs.is_self is False

    def test_target_spec_defaults(self):
        """TargetSpec 默认值。"""
        ts = TargetSpec()
        assert ts.target_type == TargetType.CREATURE
        assert ts.max_targets == 1
        assert ts.blocked_by_full_cover is True

    def test_area_spec_defaults(self):
        """AreaSpec 默认值。"""
        aspec = AreaSpec()
        assert aspec.shape == AreaShape.SPHERE
        assert aspec.size_ft == 0.0

    def test_get_spell_target_spec_fireball(self):
        """火球术规格解析。"""
        spec = get_spell_target_spec("火球术")
        assert spec["range_spec"].range_ft == 150
        assert spec["area_spec"] is not None
        assert spec["area_spec"].shape == AreaShape.SPHERE
        assert spec["area_spec"].size_ft == 20

    def test_get_spell_target_spec_shield(self):
        """护盾术规格 — 自身法术。"""
        spec = get_spell_target_spec("护盾术")
        assert spec["range_spec"].is_self is True
        assert spec["target_spec"].target_type == TargetType.SELF

    def test_get_spell_target_spec_healing_word(self):
        """治愈真言 — 需要看见目标。"""
        spec = get_spell_target_spec("治愈真言")
        assert spec["range_spec"].range_ft == 60

    def test_validate_target_unknown_spell(self):
        """未知法术返回 invalid。"""
        svc = SpellTargetingService()
        result = svc.validate_target("不存在的法术", {"position": (0, 0)}, {"position": (0, 0)})
        assert result["valid"] is False
        assert "未知法术" in result["reasons"][0]

    def test_validate_target_self_spell_other(self):
        """自身法术以他人为目标 → 不合法。"""
        svc = SpellTargetingService()
        caster = {"entity_id": "caster1", "position": (0, 0)}
        target = {"entity_id": "other1", "position": (1, 0)}
        result = svc.validate_target("护盾术", caster, target)
        assert result["valid"] is False

    def test_validate_target_self_spell_self(self):
        """自身法术以自己为目标 → 合法。"""
        svc = SpellTargetingService()
        caster = {"entity_id": "caster1", "position": (0, 0)}
        target = {"entity_id": "caster1", "position": (0, 0)}
        result = svc.validate_target("护盾术", caster, target)
        assert result["valid"] is True

    def test_validate_target_out_of_range(self):
        """超出射程 → 不合法。"""
        svc = SpellTargetingService()
        caster = {"entity_id": "c1", "position": (0, 0)}
        target = {"entity_id": "t1", "position": (100, 0)}  # 500尺
        result = svc.validate_target("治愈真言", caster, target)
        assert result["valid"] is False
        assert any("超出射程" in r for r in result["reasons"])

    def test_validate_target_in_range(self):
        """射程内 → 合法。"""
        svc = SpellTargetingService()
        caster = {"entity_id": "c1", "position": (0, 0)}
        target = {"entity_id": "t1", "position": (5, 0)}  # 25尺
        result = svc.validate_target("治愈真言", caster, target)
        assert result["valid"] is True

    def test_validate_area_no_aoe(self):
        """非区域法术验证 → 不合法。"""
        svc = SpellTargetingService()
        result = svc.validate_area("火焰箭", (5, 0))
        assert result["valid"] is False
        assert "无效应区域" in result["reasons"][0]

    def test_validate_area_fireball(self):
        """火球术区域验证。"""
        svc = SpellTargetingService()
        caster = {"position": (0, 0)}
        result = svc.validate_area("火球术", (10, 0), caster=caster)
        assert result["valid"] is True
        assert result["area_spec"].shape == AreaShape.SPHERE

    def test_validate_area_out_of_range(self):
        """区域原点超出射程 → 不合法。"""
        svc = SpellTargetingService()
        caster = {"position": (0, 0)}
        result = svc.validate_area("火球术", (200, 0), caster=caster)
        assert result["valid"] is False

    def test_get_valid_targets(self):
        """获取合法目标列表。"""
        svc = SpellTargetingService()
        caster = {"entity_id": "c1", "position": (0, 0)}
        entities = {
            "t1": {"entity_id": "t1", "position": (2, 0)},
            "t2": {"entity_id": "t2", "position": (100, 0)},  # 太远
        }
        valid = svc.get_valid_targets("治愈真言", caster, entities)
        assert "t1" in valid
        assert "t2" not in valid

    def test_get_valid_targets_empty(self):
        """无实体 → 空列表。"""
        svc = SpellTargetingService()
        caster = {"entity_id": "c1", "position": (0, 0)}
        valid = svc.get_valid_targets("治愈真言", caster, None)
        assert valid == []


# ════════════════════════════════════════════════════════════════════════
# SPL-009: DurationScheduler 持续时间调度
# ════════════════════════════════════════════════════════════════════════

class TestDurationScheduler:
    """SPL-009 持续时间调度器测试。"""

    def test_duration_type_enum(self):
        """SchedulerDurationType 枚举值。"""
        assert SchedulerDurationType.INSTANT == "instant"
        assert SchedulerDurationType.ROUNDS == "rounds"
        assert SchedulerDurationType.MINUTES == "minutes"
        assert SchedulerDurationType.UNTIL_REST == "until_rest"
        assert SchedulerDurationType.PERMANENT == "permanent"

    def test_schedule_and_count(self):
        """调度效果后 count 增加。"""
        sched = DurationScheduler()
        eff = ScheduledEffect(effect_id="e1", duration_type=SchedulerDurationType.ROUNDS, remaining=3)
        sched.schedule(eff)
        assert sched.count() == 1
        assert sched.has_effect("e1")

    def test_cancel(self):
        """取消效果后 count 减少。"""
        sched = DurationScheduler()
        eff = ScheduledEffect(effect_id="e1", duration_type=SchedulerDurationType.ROUNDS, remaining=3)
        sched.schedule(eff)
        assert sched.cancel("e1") is True
        assert sched.count() == 0
        assert not sched.has_effect("e1")

    def test_cancel_nonexistent(self):
        """取消不存在的效果返回 False。"""
        sched = DurationScheduler()
        assert sched.cancel("nonexistent") is False

    def test_on_round_start_expires(self):
        """轮开始时效果到期。"""
        sched = DurationScheduler()
        eff = ScheduledEffect(
            effect_id="e1",
            duration_type=SchedulerDurationType.ROUNDS,
            remaining=1,
            expire_on="round_start",
        )
        sched.schedule(eff)
        expired = sched.on_round_start(1)
        assert len(expired) == 1
        assert expired[0]["effect_id"] == "e1"
        assert expired[0]["reason"] == "expired"
        assert sched.count() == 0

    def test_on_round_start_decrements(self):
        """轮开始时 remaining 递减。"""
        sched = DurationScheduler()
        eff = ScheduledEffect(
            effect_id="e1",
            duration_type=SchedulerDurationType.ROUNDS,
            remaining=3,
            expire_on="round_start",
        )
        sched.schedule(eff)
        sched.on_round_start(1)
        assert sched.get_active()[0].remaining == 2

    def test_on_round_end_expires(self):
        """轮结束时效果到期。"""
        sched = DurationScheduler()
        eff = ScheduledEffect(
            effect_id="e1",
            duration_type=SchedulerDurationType.ROUNDS,
            remaining=1,
            expire_on="round_end",
        )
        sched.schedule(eff)
        expired = sched.on_round_end(1)
        assert len(expired) == 1

    def test_on_turn_start(self):
        """回合开始时 source_turn_start 效果递减。"""
        sched = DurationScheduler()
        eff = ScheduledEffect(
            effect_id="e1",
            duration_type=SchedulerDurationType.ROUNDS,
            remaining=2,
            expire_on="source_turn_start",
            target_entity_id="caster1",
        )
        sched.schedule(eff)
        expired = sched.on_turn_start("caster1", 1)
        assert len(expired) == 0  # remaining=1, not expired yet
        assert sched.get_active()[0].remaining == 1

    def test_on_turn_end(self):
        """回合结束时 target_turn_end 效果递减。"""
        sched = DurationScheduler()
        eff = ScheduledEffect(
            effect_id="e1",
            duration_type=SchedulerDurationType.ROUNDS,
            remaining=1,
            expire_on="target_turn_end",
            target_entity_id="target1",
        )
        sched.schedule(eff)
        expired = sched.on_turn_end("target1", 1)
        assert len(expired) >= 1
        assert any(e["effect_id"] == "e1" for e in expired)

    def test_on_rest_long(self):
        """长休结束 until_rest 效果。"""
        sched = DurationScheduler()
        eff = ScheduledEffect(
            effect_id="e1",
            duration_type=SchedulerDurationType.UNTIL_REST,
            metadata={"rest_type": "long"},
        )
        sched.schedule(eff)
        expired = sched.on_rest("long")
        assert len(expired) == 1
        assert expired[0]["reason"] == "rest_long"

    def test_on_rest_short_not_affect_long(self):
        """短休不结束需要长休的效果。"""
        sched = DurationScheduler()
        eff = ScheduledEffect(
            effect_id="e1",
            duration_type=SchedulerDurationType.UNTIL_REST,
            metadata={"rest_type": "long"},
        )
        sched.schedule(eff)
        expired = sched.on_rest("short")
        assert len(expired) == 0
        assert sched.count() == 1

    def test_on_rest_short_affects_short(self):
        """短休结束只需短休的效果。"""
        sched = DurationScheduler()
        eff = ScheduledEffect(
            effect_id="e1",
            duration_type=SchedulerDurationType.UNTIL_REST,
            metadata={"rest_type": "short"},
        )
        sched.schedule(eff)
        expired = sched.on_rest("short")
        assert len(expired) == 1

    def test_get_active_filters_expired(self):
        """get_active 不返回已到期效果。"""
        sched = DurationScheduler()
        eff1 = ScheduledEffect(
            effect_id="e1",
            duration_type=SchedulerDurationType.ROUNDS,
            remaining=5,
        )
        eff2 = ScheduledEffect(
            effect_id="e2",
            duration_type=SchedulerDurationType.ROUNDS,
            remaining=0,
        )
        sched.schedule(eff1)
        sched.schedule(eff2)
        active = sched.get_active()
        assert len(active) == 1
        assert active[0].effect_id == "e1"

    def test_get_for_entity(self):
        """按实体查询效果。"""
        sched = DurationScheduler()
        sched.schedule(ScheduledEffect(
            effect_id="e1",
            duration_type=SchedulerDurationType.ROUNDS,
            remaining=3,
            target_entity_id="hero1",
        ))
        sched.schedule(ScheduledEffect(
            effect_id="e2",
            duration_type=SchedulerDurationType.ROUNDS,
            remaining=3,
            target_entity_id="hero2",
        ))
        for_hero1 = sched.get_for_entity("hero1")
        assert len(for_hero1) == 1
        assert for_hero1[0].effect_id == "e1"

    def test_is_expired_property(self):
        """ScheduledEffect.is_expired 属性。"""
        eff = ScheduledEffect(
            effect_id="e1",
            duration_type=SchedulerDurationType.ROUNDS,
            remaining=0,
        )
        assert eff.is_expired is True

        eff2 = ScheduledEffect(
            effect_id="e2",
            duration_type=SchedulerDurationType.PERMANENT,
            remaining=0,
        )
        assert eff2.is_expired is False

    def test_on_expire_callback(self):
        """到期时触发回调。"""
        callback_log = []

        def on_expire(eid, reason):
            callback_log.append((eid, reason))

        sched = DurationScheduler()
        eff = ScheduledEffect(
            effect_id="e1",
            duration_type=SchedulerDurationType.ROUNDS,
            remaining=1,
            expire_on="round_start",
            on_expire=on_expire,
        )
        sched.schedule(eff)
        sched.on_round_start(1)
        assert len(callback_log) == 1
        assert callback_log[0] == ("e1", "expired")

    def test_cancel_callback(self):
        """取消时触发回调。"""
        callback_log = []

        def on_expire(eid, reason):
            callback_log.append((eid, reason))

        sched = DurationScheduler()
        eff = ScheduledEffect(
            effect_id="e1",
            duration_type=SchedulerDurationType.ROUNDS,
            remaining=5,
            on_expire=on_expire,
        )
        sched.schedule(eff)
        sched.cancel("e1")
        assert len(callback_log) == 1
        assert callback_log[0][1] == "cancelled"

    def test_on_tick_callback(self):
        """每轮触发 on_tick 回调。"""
        tick_log = []

        def on_tick(eid, round_num):
            tick_log.append((eid, round_num))

        sched = DurationScheduler()
        eff = ScheduledEffect(
            effect_id="e1",
            duration_type=SchedulerDurationType.ROUNDS,
            remaining=3,
            expire_on="round_start",
            on_tick=on_tick,
        )
        sched.schedule(eff)
        sched.on_round_start(1)
        assert len(tick_log) == 1
        assert tick_log[0] == ("e1", 1)

    def test_repeat_save_dataclass(self):
        """RepeatSave 数据类。"""
        rs = RepeatSave(ability="wis", dc=15, end_on_success=True)
        assert rs.ability == "wis"
        assert rs.dc == 15

    def test_multiple_effects_round(self):
        """多效果同时推进。"""
        sched = DurationScheduler()
        for i in range(3):
            sched.schedule(ScheduledEffect(
                effect_id=f"e{i}",
                duration_type=SchedulerDurationType.ROUNDS,
                remaining=i + 1,
                expire_on="round_start",
            ))
        expired = sched.on_round_start(1)
        # e0 (remaining=1) should expire
        assert any(e["effect_id"] == "e0" for e in expired)
        # e1 and e2 should still be active
        assert sched.count() == 2
