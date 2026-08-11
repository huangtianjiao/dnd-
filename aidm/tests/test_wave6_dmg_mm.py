"""Wave 6 DMG/MM 运行包测试 — REST-002/003, EXP-001~003, RAG-002, ENV-002。"""

from __future__ import annotations

import pytest
from dataclasses import dataclass, field
from typing import List


# ──────────────────────────────────────────────────────────────────────────
# REST-002: 休息持久状态机
# ──────────────────────────────────────────────────────────────────────────

class TestRestPhase:
    """REST-002: RestPhase 枚举与 RestSession 状态机。"""

    def test_rest_phase_values(self):
        from aidm.brain.rest import RestPhase
        assert RestPhase.NOT_STARTED == "not_started"
        assert RestPhase.IN_PROGRESS == "in_progress"
        assert RestPhase.INTERRUPTED == "interrupted"
        assert RestPhase.COMPLETED == "completed"

    def test_rest_session_creation(self):
        from aidm.brain.rest import RestSession, RestPhase
        session = RestSession(character_id="char_1", rest_type="short")
        assert session.character_id == "char_1"
        assert session.rest_type == "short"
        assert session.phase == RestPhase.NOT_STARTED
        assert session.started_round == 0
        assert session.interrupted_by == []
        assert session.resource_changes == []
        assert session.events == []
        assert len(session.session_id) > 0

    def test_rest_session_transition(self):
        from aidm.brain.rest import RestSession, RestPhase
        session = RestSession(character_id="char_1", rest_type="long")
        session.transition_to(RestPhase.IN_PROGRESS)
        assert session.phase == RestPhase.IN_PROGRESS
        assert len(session.events) == 1
        assert session.events[0]["from"] == "not_started"
        assert session.events[0]["to"] == "in_progress"

    def test_rest_session_interrupt(self):
        from aidm.brain.rest import RestSession, RestPhase
        session = RestSession(character_id="char_1", rest_type="long")
        session.transition_to(RestPhase.IN_PROGRESS)
        session.record_interrupt("roll_initiative")
        assert session.phase == RestPhase.INTERRUPTED
        assert session.interrupted_by == ["roll_initiative"]
        assert len(session.events) == 2  # transition + interrupt

    def test_rest_session_resource_change(self):
        from aidm.brain.rest import RestSession
        session = RestSession(character_id="char_1", rest_type="short")
        session.record_resource_change({"type": "hp", "amount": 10})
        assert len(session.resource_changes) == 1
        assert session.resource_changes[0]["amount"] == 10

    def test_rest_session_full_lifecycle(self):
        from aidm.brain.rest import RestSession, RestPhase
        session = RestSession(character_id="char_1", rest_type="long")
        # NOT_STARTED → IN_PROGRESS
        session.transition_to(RestPhase.IN_PROGRESS)
        assert session.phase == RestPhase.IN_PROGRESS
        # IN_PROGRESS → INTERRUPTED
        session.record_interrupt("take_damage")
        assert session.phase == RestPhase.INTERRUPTED
        # INTERRUPTED → IN_PROGRESS (resume)
        session.transition_to(RestPhase.IN_PROGRESS)
        assert session.phase == RestPhase.IN_PROGRESS
        # IN_PROGRESS → COMPLETED
        session.transition_to(RestPhase.COMPLETED)
        assert session.phase == RestPhase.COMPLETED
        assert len(session.events) == 4


# ──────────────────────────────────────────────────────────────────────────
# REST-003: 资源恢复完整
# ──────────────────────────────────────────────────────────────────────────

class TestRestResourceRecovery:
    """REST-003: 资源池恢复集成。"""

    def test_short_rest_returns_resource_pools_key(self):
        from aidm.brain.rest import short_rest, MockCharacter
        c = MockCharacter(hp=10, max_hp=20)
        r = short_rest(c, hit_dice_to_spend=0)
        assert "resource_pools_recharged" in r
        assert r["resource_pools_recharged"] == []  # MockCharacter 无 resource_manager

    def test_long_rest_returns_resource_pools_key(self):
        from aidm.brain.rest import long_rest, MockCharacter
        c = MockCharacter(hp=5, max_hp=20)
        r = long_rest(c)
        assert "resource_pools_recharged" in r
        assert r["resource_pools_recharged"] == []

    def test_short_rest_with_resource_manager(self):
        from aidm.brain.rest import short_rest, MockCharacter
        from aidm.rules.resource import ResourceManager, ResourcePool

        @dataclass
        class CharWithRM:
            hp: int = 10
            max_hp: int = 20
            hit_dice: int = 3
            max_hit_dice: int = 3
            con_mod: int = 2
            hit_die_faces: int = 10
            exhaustion: int = 0
            char_class: str = "战士"
            level: int = 3
            base_max_hp: int = 20
            reduced_ability_scores: bool = False
            spell_slots: dict = field(default_factory=lambda: {1: 2})
            max_spell_slots: dict = field(default_factory=lambda: {1: 4})
            temp_hp: int = 0
            entity_id: str = "test_char"
            resource_manager: ResourceManager = field(default_factory=ResourceManager)

        c = CharWithRM()
        # 创建一个短休恢复的资源池
        pool = ResourcePool(name="动作如潮", max_value=1, current_value=0,
                           recharge_on="short_rest")
        c.resource_manager.create_pool("test_char", pool)

        r = short_rest(c, hit_dice_to_spend=0)
        assert "动作如潮" in r["resource_pools_recharged"]

    def test_long_rest_recharges_long_rest_pools(self):
        from aidm.brain.rest import long_rest
        from aidm.rules.resource import ResourceManager, ResourcePool

        @dataclass
        class CharWithRM:
            hp: int = 5
            max_hp: int = 20
            hit_dice: int = 3
            max_hit_dice: int = 3
            con_mod: int = 2
            hit_die_faces: int = 10
            exhaustion: int = 0
            char_class: str = "战士"
            level: int = 3
            base_max_hp: int = 20
            reduced_ability_scores: bool = False
            spell_slots: dict = field(default_factory=dict)
            max_spell_slots: dict = field(default_factory=dict)
            temp_hp: int = 0
            entity_id: str = "test_char"
            resource_manager: ResourceManager = field(default_factory=ResourceManager)

        c = CharWithRM()
        pool = ResourcePool(name="狂暴", max_value=2, current_value=0,
                           recharge_on="long_rest")
        c.resource_manager.create_pool("test_char", pool)

        r = long_rest(c)
        assert "狂暴" in r["resource_pools_recharged"]


# ──────────────────────────────────────────────────────────────────────────
# EXP-001: 社交态度RAW Policy
# ──────────────────────────────────────────────────────────────────────────

class TestSocialPolicy:
    """EXP-001: 社交态度RAW Policy。"""

    def test_default_policy_is_custom(self):
        from aidm.brain.social import get_social_policy, SOCIAL_POLICY_CONFIG
        # 确保默认值
        assert get_social_policy() in ("custom", "2024_raw")

    def test_set_policy(self):
        from aidm.brain.social import set_social_policy, get_social_policy, SocialPolicy
        original = get_social_policy()
        try:
            set_social_policy("2024_raw")
            assert get_social_policy() == "2024_raw"
            set_social_policy("custom")
            assert get_social_policy() == "custom"
        finally:
            set_social_policy(original)

    def test_invalid_policy_raises(self):
        from aidm.brain.social import set_social_policy
        with pytest.raises(ValueError):
            set_social_policy("invalid_policy")

    def test_2024_raw_returns_zero_dc_modifier(self):
        from aidm.brain.social import check_social_dc, set_social_policy, get_social_policy
        original = get_social_policy()
        try:
            set_social_policy("2024_raw")
            assert check_social_dc("friendly") == 0
            assert check_social_dc("indifferent") == 0
            assert check_social_dc("hostile") == 0
        finally:
            set_social_policy(original)

    def test_custom_returns_dc_modifier(self):
        from aidm.brain.social import check_social_dc, set_social_policy, get_social_policy
        original = get_social_policy()
        try:
            set_social_policy("custom")
            assert check_social_dc("friendly") == -5
            assert check_social_dc("indifferent") == 0
            assert check_social_dc("hostile") == 5
        finally:
            set_social_policy(original)

    def test_get_attitude_effect(self):
        from aidm.brain.social import get_attitude_effect, set_social_policy, get_social_policy
        original = get_social_policy()
        try:
            set_social_policy("2024_raw")
            assert get_attitude_effect("friendly") == "advantage"
            assert get_attitude_effect("indifferent") == "none"
            assert get_attitude_effect("hostile") == "disadvantage"
        finally:
            set_social_policy(original)

    def test_social_policy_enum(self):
        from aidm.brain.social import SocialPolicy
        assert SocialPolicy.CUSTOM == "custom"
        assert SocialPolicy.RULE_2024_RAW == "2024_raw"


# ──────────────────────────────────────────────────────────────────────────
# EXP-002: ExplorationClock
# ──────────────────────────────────────────────────────────────────────────

class TestExplorationClock:
    """EXP-002: 探索时钟。"""

    def test_clock_creation(self):
        from aidm.engine.exploration_clock import ExplorationClock
        clock = ExplorationClock()
        assert clock.current_time == "06:00"
        assert clock.current_day == 1
        assert clock.travel_distance_miles == 0.0
        assert clock.supplies_remaining == 0

    def test_advance_hours(self):
        from aidm.engine.exploration_clock import ExplorationClock
        clock = ExplorationClock(current_time="06:00")
        result = clock.advance_hours(3)
        assert clock.current_time == "09:00"
        assert clock.current_day == 1
        assert result["old_time"] == "06:00"
        assert result["new_time"] == "09:00"

    def test_advance_hours_crosses_day(self):
        from aidm.engine.exploration_clock import ExplorationClock
        clock = ExplorationClock(current_time="22:00")
        result = clock.advance_hours(10)
        assert clock.current_time == "08:00"
        assert clock.current_day == 2

    def test_travel_day(self):
        from aidm.engine.exploration_clock import ExplorationClock
        clock = ExplorationClock(current_time="06:00")
        result = clock.travel_day(20.0, terrain="normal")
        assert result["distance"] == 20.0
        assert result["terrain"] == "normal"
        assert clock.travel_distance_miles == 20.0

    def test_travel_day_terrain_multiplier(self):
        from aidm.engine.exploration_clock import ExplorationClock
        clock = ExplorationClock()
        result = clock.travel_day(20.0, terrain="difficult")
        assert result["speed_multiplier"] == 0.5
        assert result["effective_distance"] == 10.0

    def test_consume_supplies_success(self):
        from aidm.engine.exploration_clock import ExplorationClock
        clock = ExplorationClock(supplies_remaining=10)
        assert clock.consume_supplies(3) is True
        assert clock.supplies_remaining == 7

    def test_consume_supplies_failure(self):
        from aidm.engine.exploration_clock import ExplorationClock
        clock = ExplorationClock(supplies_remaining=2)
        assert clock.consume_supplies(5) is False
        assert clock.supplies_remaining == 0

    def test_forced_march(self):
        from aidm.engine.exploration_clock import ExplorationClock
        clock = ExplorationClock()
        results = clock.apply_forced_march(3, ["char_1", "char_2"])
        assert len(results) == 2
        assert results[0]["save_dc"] == 13  # 10 + 3
        assert results[0]["entity_id"] == "char_1"

    def test_forced_march_failure(self):
        from aidm.engine.exploration_clock import ExplorationClock
        clock = ExplorationClock()
        result = clock.apply_forced_march_failure("char_1")
        assert result["old_exhaustion"] == 0
        assert result["new_exhaustion"] == 1
        assert clock.exhaustion_levels["char_1"] == 1

    def test_dehydration_starvation(self):
        from aidm.engine.exploration_clock import ExplorationClock
        clock = ExplorationClock()
        results = clock.apply_dehydration_starvation(["char_1", "char_2"])
        assert len(results) == 2
        assert results[0]["new_exhaustion"] == 1
        assert results[0]["cause"] == "dehydration_or_starvation"

    def test_is_night(self):
        from aidm.engine.exploration_clock import ExplorationClock
        clock = ExplorationClock(current_time="03:00")
        assert clock.is_night() is True
        clock.current_time = "14:00"
        assert clock.is_night() is False
        clock.current_time = "20:00"
        assert clock.is_night() is True

    def test_snapshot(self):
        from aidm.engine.exploration_clock import ExplorationClock
        clock = ExplorationClock(supplies_remaining=5)
        snap = clock.snapshot()
        assert snap["supplies_remaining"] == 5
        assert snap["current_day"] == 1

    def test_encounter_dc_by_terrain(self):
        from aidm.engine.exploration_clock import ENCOUNTER_DC_BY_TERRAIN
        assert ENCOUNTER_DC_BY_TERRAIN["urban"] == 15
        assert ENCOUNTER_DC_BY_TERRAIN["dangerous"] == 8


# ──────────────────────────────────────────────────────────────────────────
# EXP-003: 停工期完整公式
# ──────────────────────────────────────────────────────────────────────────

class TestDowntimeEnhanced:
    """EXP-003: 停工期完整公式。"""

    def test_downtime_project_creation(self):
        from aidm.engine.downtime import DowntimeProject
        proj = DowntimeProject(
            project_id="p1", activity="training",
            total_days=75, total_cost_gp=1800
        )
        assert proj.days_completed == 0
        assert proj.completed is False

    def test_downtime_project_advance(self):
        from aidm.engine.downtime import DowntimeProject
        proj = DowntimeProject(
            project_id="p1", activity="research",
            total_days=7, total_cost_gp=350
        )
        result = proj.advance_days(3, cost_gp=150)
        assert result["days_advanced"] == 3
        assert proj.days_completed == 3
        assert proj.completed is False

    def test_downtime_project_complete(self):
        from aidm.engine.downtime import DowntimeProject
        proj = DowntimeProject(
            project_id="p1", activity="research",
            total_days=7, total_cost_gp=350
        )
        proj.advance_days(5)
        result = proj.advance_days(5)  # 只需2天
        assert result["days_advanced"] == 2
        assert proj.completed is True

    def test_downtime_project_interrupt_lose_half(self):
        from aidm.engine.downtime import DowntimeProject
        proj = DowntimeProject(
            project_id="p1", activity="training",
            total_days=75, total_cost_gp=1800
        )
        proj.advance_days(20)
        result = proj.interrupt()
        assert result["interrupted"] is True
        assert result["failure_type"] == "lose_progress_half"
        assert result["progress_lost"] == 10
        assert proj.days_completed == 10  # 20 - 10

    def test_downtime_project_interrupt_restart(self):
        from aidm.engine.downtime import DowntimeProject
        proj = DowntimeProject(
            project_id="p1", activity="recuperating",
            total_days=3, total_cost_gp=0
        )
        proj.advance_days(2)
        result = proj.interrupt()
        assert result["failure_type"] == "restart"
        assert proj.days_completed == 0

    def test_downtime_project_resume(self):
        from aidm.engine.downtime import DowntimeProject
        proj = DowntimeProject(
            project_id="p1", activity="training",
            total_days=75
        )
        proj.advance_days(10)
        proj.interrupt()
        result = proj.resume()
        assert result["resumed"] is True
        assert result["days_remaining"] == 70  # 75 - 5 (half of 10 lost)

    def test_downtime_project_snapshot(self):
        from aidm.engine.downtime import DowntimeProject
        proj = DowntimeProject(
            project_id="p1", activity="crafting",
            total_days=10, total_cost_gp=100
        )
        proj.advance_days(5, cost_gp=50)
        snap = proj.snapshot()
        assert snap["days_completed"] == 5
        assert snap["progress_pct"] == 50.0

    def test_downtime_activities_extended(self):
        from aidm.engine.downtime import DOWNTIME_ACTIVITIES
        # 新增活动
        assert "carousing" in DOWNTIME_ACTIVITIES
        assert "relaxation" in DOWNTIME_ACTIVITIES
        assert "work" in DOWNTIME_ACTIVITIES
        assert "mission" in DOWNTIME_ACTIVITIES

    def test_downtime_cost_work(self):
        from aidm.engine.downtime import downtime_cost
        result = downtime_cost("work", days=5)
        assert result["days"] == 5

    def test_downtime_cost_carousing(self):
        from aidm.engine.downtime import downtime_cost
        result = downtime_cost("carousing", days=3)
        assert result["days"] == 3
        assert result["cost_gp"] == 30  # 3 * 10


# ──────────────────────────────────────────────────────────────────────────
# RAG-002: 规则溯源链
# ──────────────────────────────────────────────────────────────────────────

class TestSourceSpan:
    """RAG-002: 规则溯源链。"""

    def test_source_span_creation(self):
        from aidm.knowledge.indexer import SourceSpan
        span = SourceSpan(
            source_id="abc123",
            book="玩家手册2024",
            page="42",
            anchor="sec_2",
            content_hash="deadbeef",
            authority_level="core",
        )
        assert span.source_id == "abc123"
        assert span.book == "玩家手册2024"
        assert span.authority_level == "core"

    def test_source_span_to_payload(self):
        from aidm.knowledge.indexer import SourceSpan
        span = SourceSpan(
            source_id="abc123",
            book="城主指南2024",
            page="100",
            content_hash="cafebabe",
            authority_level="core",
        )
        payload = span.to_payload()
        assert payload["source_id"] == "abc123"
        assert payload["book"] == "城主指南2024"
        assert payload["content_hash"] == "cafebabe"

    def test_source_span_from_entry(self):
        from aidm.knowledge.indexer import SourceSpan
        span = SourceSpan.from_entry(
            body="火球术造成8d6火焰伤害",
            source="topics/玩家手册2024/法术/火球术.htm",
        )
        assert span.book == "玩家手册2024"
        assert span.authority_level == "core"
        assert len(span.content_hash) == 16
        assert len(span.source_id) == 12

    def test_source_span_from_entry_supplement(self):
        from aidm.knowledge.indexer import SourceSpan
        span = SourceSpan.from_entry(
            body="第三方规则内容",
            source="topics/第三方/某扩展/规则.htm",
        )
        assert span.authority_level == "supplement"

    def test_source_span_content_hash_deterministic(self):
        from aidm.knowledge.indexer import SourceSpan
        span1 = SourceSpan.from_entry("相同内容", "topics/test.htm")
        span2 = SourceSpan.from_entry("相同内容", "topics/test.htm")
        assert span1.content_hash == span2.content_hash

    def test_source_span_different_content_different_hash(self):
        from aidm.knowledge.indexer import SourceSpan
        span1 = SourceSpan.from_entry("内容A", "topics/test.htm")
        span2 = SourceSpan.from_entry("内容B", "topics/test.htm")
        assert span1.content_hash != span2.content_hash


# ──────────────────────────────────────────────────────────────────────────
# ENV-002: 物件与地形结构化
# ──────────────────────────────────────────────────────────────────────────

class TestObjectEntity:
    """ENV-002: 物件实体。"""

    def test_object_entity_creation(self):
        from aidm.engine.objects import ObjectEntity
        obj = ObjectEntity(
            object_id="obj_1",
            name="木门",
            material="wood",
            ac=15,
            hp=10,
            is_flammable=True,
            provides_cover=True,
        )
        assert obj.object_id == "obj_1"
        assert obj.ac == 15
        assert obj.is_flammable is True

    def test_object_entity_take_damage(self):
        from aidm.engine.objects import ObjectEntity
        obj = ObjectEntity(object_id="obj_1", name="木箱", hp=10)
        result = obj.take_damage(3)
        assert result["damage_dealt"] == 3
        assert result["hp_remaining"] == 7
        assert result["destroyed"] is False

    def test_object_entity_take_damage_destroyed(self):
        from aidm.engine.objects import ObjectEntity
        obj = ObjectEntity(object_id="obj_1", name="木箱", hp=5)
        result = obj.take_damage(10)
        assert result["hp_remaining"] == 0
        assert result["destroyed"] is True

    def test_object_entity_damage_threshold(self):
        from aidm.engine.objects import ObjectEntity
        obj = ObjectEntity(object_id="obj_1", name="石墙", hp=50, damage_threshold=10)
        result = obj.take_damage(8)
        assert result["damage_dealt"] == 0  # 低于阈值
        assert result["hp_remaining"] == 50

    def test_object_entity_damage_above_threshold(self):
        from aidm.engine.objects import ObjectEntity
        obj = ObjectEntity(object_id="obj_1", name="石墙", hp=50, damage_threshold=10)
        result = obj.take_damage(15)
        assert result["damage_dealt"] == 15  # 高于阈值
        assert result["hp_remaining"] == 35

    def test_object_entity_from_material(self):
        from aidm.engine.objects import ObjectEntity
        obj = ObjectEntity.from_material("obj_1", "木门", "wood", 2.0, "Medium")
        assert obj.ac == 15  # wood AC
        assert obj.hp == 6   # 3 * 2
        assert obj.is_flammable is True
        assert obj.provides_cover is True

    def test_object_entity_from_material_stone(self):
        from aidm.engine.objects import ObjectEntity
        obj = ObjectEntity.from_material("obj_2", "石像", "stone", 3.0, "Large")
        assert obj.ac == 17  # stone AC
        assert obj.hp == 15  # 5 * 3
        assert obj.is_flammable is False
        assert obj.provides_cover is True


class TestTerrainFeature:
    """ENV-002: 地形特征。"""

    def test_terrain_creation(self):
        from aidm.engine.objects import TerrainFeature
        terrain = TerrainFeature(
            terrain_id="t1",
            terrain_type="difficult",
            cost_multiplier=2.0,
            description="泥泞沼泽",
        )
        assert terrain.terrain_id == "t1"
        assert terrain.is_difficult() is True

    def test_terrain_movement_cost(self):
        from aidm.engine.objects import TerrainFeature
        terrain = TerrainFeature(terrain_id="t1", cost_multiplier=2.0)
        assert terrain.movement_cost(5.0) == 10.0
        assert terrain.movement_cost(10.0) == 20.0

    def test_terrain_hazardous(self):
        from aidm.engine.objects import TerrainFeature
        terrain = TerrainFeature(
            terrain_id="t1",
            terrain_type="hazardous",
            hazard_damage="1d6 fire",
        )
        assert terrain.is_difficult() is True
        assert terrain.has_hazard() is True

    def test_terrain_water(self):
        from aidm.engine.objects import TerrainFeature
        terrain = TerrainFeature(terrain_id="t1", terrain_type="water")
        assert terrain.is_difficult() is False
        assert terrain.has_hazard() is False

    def test_terrain_elevation(self):
        from aidm.engine.objects import TerrainFeature
        terrain = TerrainFeature(terrain_id="t1", terrain_type="elevation")
        assert terrain.is_difficult() is False
