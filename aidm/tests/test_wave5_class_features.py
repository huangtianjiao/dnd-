"""Wave 5 — 职业特性框架 / Grant / Choice / ResourcePool / LevelUpService 测试"""

from __future__ import annotations

import pytest

from aidm.rules.feature_dsl import FeatureDefinition, FeatureType
from aidm.rules.grant import Grant, GrantManager
from aidm.rules.choice import ChoiceManager, ChoiceRecord, ChoiceRequest
from aidm.rules.resource import PoolType, ResourcePool, ResourceManager, ResourceType, SpendResult
from aidm.data.class_features import CLASS_FEATURES, SUBCLASS_FEATURES
from aidm.build.level_up_service import LevelUpPlan, LevelUpService


# ═══════════════════════════════════════════════════════════════
# FeatureDefinition 测试
# ═══════════════════════════════════════════════════════════════

class TestFeatureDefinition:
    """FeatureDefinition 基础测试"""

    def test_create_basic_feature(self):
        feat = FeatureDefinition(
            feature_id="test_feat", name="Test Feature",
            feature_type=FeatureType.PASSIVE,
        )
        assert feat.feature_id == "test_feat"
        assert feat.feature_type == FeatureType.PASSIVE
        assert feat.validate() == []

    def test_validate_missing_id(self):
        feat = FeatureDefinition(feature_id="", name="Test", feature_type=FeatureType.PASSIVE)
        errors = feat.validate()
        assert any("feature_id" in e for e in errors)

    def test_validate_missing_name(self):
        feat = FeatureDefinition(feature_id="x", name="", feature_type=FeatureType.PASSIVE)
        errors = feat.validate()
        assert any("name" in e for e in errors)

    def test_validate_resource_pool_missing_name(self):
        feat = FeatureDefinition(
            feature_id="x", name="Test", feature_type=FeatureType.RESOURCE,
            resource_pool={"max": 5},
        )
        errors = feat.validate()
        assert any("name" in e for e in errors)

    def test_validate_resource_pool_missing_max(self):
        feat = FeatureDefinition(
            feature_id="x", name="Test", feature_type=FeatureType.RESOURCE,
            resource_pool={"name": "pool"},
        )
        errors = feat.validate()
        assert any("max" in e for e in errors)

    def test_to_dict_and_from_dict_roundtrip(self):
        feat = FeatureDefinition(
            feature_id="test", name="Test", feature_type=FeatureType.RESOURCE,
            source_class="fighter", source_level=5,
            resource_pool={"name": "pool", "max": 3},
            granted_actions=["action1"],
        )
        d = feat.to_dict()
        restored = FeatureDefinition.from_dict(d)
        assert restored.feature_id == feat.feature_id
        assert restored.feature_type == feat.feature_type
        assert restored.source_class == feat.source_class
        assert restored.resource_pool == feat.resource_pool
        assert restored.granted_actions == feat.granted_actions

    def test_feature_type_enum_values(self):
        assert FeatureType.PASSIVE.value == "passive"
        assert FeatureType.RESOURCE.value == "resource"
        assert FeatureType.ACTION.value == "action"
        assert FeatureType.PROFICIENCY.value == "proficiency"
        assert FeatureType.SPELL_GRANT.value == "spell_grant"


# ═══════════════════════════════════════════════════════════════
# GrantManager 测试
# ═══════════════════════════════════════════════════════════════

class TestGrantManager:
    """Grant 系统测试"""

    def setup_method(self):
        self.gm = GrantManager()

    def test_add_and_get_grant(self):
        g = Grant(grant_id="g1", source_feature_id="feat1", grant_type="proficiency", target="stealth")
        self.gm.add_grant("char1", g)
        grants = self.gm.get_grants("char1")
        assert len(grants) == 1
        assert grants[0].target == "stealth"

    def test_get_grants_by_type(self):
        self.gm.add_grant("c1", Grant("g1", "f1", "proficiency", "stealth"))
        self.gm.add_grant("c1", Grant("g2", "f1", "spell", "fireball"))
        profs = self.gm.get_grants("c1", "proficiency")
        assert len(profs) == 1
        assert profs[0].target == "stealth"

    def test_remove_grant(self):
        self.gm.add_grant("c1", Grant("g1", "f1", "proficiency", "stealth"))
        assert self.gm.remove_grant("c1", "g1") is True
        assert self.gm.get_grants("c1") == []

    def test_remove_grant_not_found(self):
        assert self.gm.remove_grant("c1", "nonexistent") is False

    def test_remove_by_source(self):
        self.gm.add_grant("c1", Grant("g1", "feat_rage", "proficiency", "heavy_armor"))
        self.gm.add_grant("c1", Grant("g2", "feat_rage", "modifier", "damage"))
        self.gm.add_grant("c1", Grant("g3", "feat_other", "spell", "fireball"))
        removed = self.gm.remove_by_source("c1", "feat_rage")
        assert removed == 2
        assert len(self.gm.get_grants("c1")) == 1

    def test_has_proficiency(self):
        self.gm.add_grant("c1", Grant("g1", "f1", "proficiency", "stealth"))
        assert self.gm.has_proficiency("c1", "stealth") is True
        assert self.gm.has_proficiency("c1", "athletics") is False

    def test_has_spell(self):
        self.gm.add_grant("c1", Grant("g1", "f1", "spell", "fireball"))
        assert self.gm.has_spell("c1", "fireball") is True
        assert self.gm.has_spell("c1", "lightning_bolt") is False

    def test_get_proficiencies(self):
        self.gm.add_grant("c1", Grant("g1", "f1", "proficiency", "stealth"))
        self.gm.add_grant("c1", Grant("g2", "f2", "proficiency", "athletics"))
        self.gm.add_grant("c1", Grant("g3", "f3", "spell", "fireball"))
        profs = self.gm.get_proficiencies("c1")
        assert set(profs) == {"stealth", "athletics"}

    def test_get_granted_spells(self):
        self.gm.add_grant("c1", Grant("g1", "f1", "spell", "fireball"))
        self.gm.add_grant("c1", Grant("g2", "f2", "spell", "lightning_bolt"))
        spells = self.gm.get_granted_spells("c1")
        assert set(spells) == {"fireball", "lightning_bolt"}

    def test_get_modifier(self):
        self.gm.add_grant("c1", Grant("g1", "f1", "modifier", "ac", 2))
        assert self.gm.get_modifier("c1", "ac") == 2
        assert self.gm.get_modifier("c1", "speed") is None

    def test_clear(self):
        self.gm.add_grant("c1", Grant("g1", "f1", "proficiency", "stealth"))
        self.gm.clear("c1")
        assert self.gm.get_grants("c1") == []

    def test_empty_entity(self):
        assert self.gm.get_grants("nonexistent") == []
        assert self.gm.has_proficiency("nonexistent", "stealth") is False
        assert self.gm.get_proficiencies("nonexistent") == []
        assert self.gm.get_granted_spells("nonexistent") == []


# ═══════════════════════════════════════════════════════════════
# ChoiceManager 测试
# ═══════════════════════════════════════════════════════════════

class TestChoiceManager:
    """Choice 系统测试"""

    def setup_method(self):
        self.cm = ChoiceManager()

    def test_create_request(self):
        req = self.cm.create_request("c1", "skill", ["stealth", "athletics"], 1, "feat1")
        assert req.entity_id == "c1"
        assert req.choice_type == "skill"
        assert req.num_to_choose == 1
        assert len(req.options) == 2

    def test_validate_choice_valid(self):
        req = self.cm.create_request("c1", "skill", ["stealth", "athletics"], 1)
        assert self.cm.validate_choice(req, ["stealth"]) is True

    def test_validate_choice_wrong_count(self):
        req = self.cm.create_request("c1", "skill", ["stealth", "athletics"], 1)
        assert self.cm.validate_choice(req, ["stealth", "athletics"]) is False

    def test_validate_choice_invalid_option(self):
        req = self.cm.create_request("c1", "skill", ["stealth", "athletics"], 1)
        assert self.cm.validate_choice(req, ["acrobatics"]) is False

    def test_validate_choice_duplicate(self):
        req = self.cm.create_request("c1", "skill", ["stealth", "athletics"], 2)
        assert self.cm.validate_choice(req, ["stealth", "stealth"]) is False

    def test_record_choice(self):
        req = self.cm.create_request("c1", "skill", ["stealth", "athletics"], 1, "feat1")
        rec = self.cm.record_choice(req, ["stealth"])
        assert rec is not None
        assert rec.validated is True
        assert rec.chosen == ["stealth"]

    def test_record_choice_invalid(self):
        req = self.cm.create_request("c1", "skill", ["stealth"], 1)
        rec = self.cm.record_choice(req, ["invalid_option"])
        assert rec is None

    def test_get_pending_requests(self):
        req1 = self.cm.create_request("c1", "skill", ["stealth"], 1, "f1")
        req2 = self.cm.create_request("c1", "language", ["elvish"], 1, "f2")
        pending = self.cm.get_pending_requests("c1")
        assert len(pending) == 2
        # 完成一个
        self.cm.record_choice(req1, ["stealth"])
        pending = self.cm.get_pending_requests("c1")
        assert len(pending) == 1

    def test_get_chosen(self):
        req = self.cm.create_request("c1", "skill", ["stealth", "athletics"], 1, "f1")
        self.cm.record_choice(req, ["stealth"])
        chosen = self.cm.get_chosen("c1")
        assert "stealth" in chosen

    def test_get_chosen_by_type(self):
        req1 = self.cm.create_request("c1", "skill", ["stealth"], 1, "f1")
        req2 = self.cm.create_request("c1", "language", ["elvish"], 1, "f2")
        self.cm.record_choice(req1, ["stealth"])
        self.cm.record_choice(req2, ["elvish"])
        assert self.cm.get_chosen("c1", "skill") == ["stealth"]
        assert self.cm.get_chosen("c1", "language") == ["elvish"]


# ═══════════════════════════════════════════════════════════════
# ResourcePool 测试
# ═══════════════════════════════════════════════════════════════

class TestResourcePool:
    """ResourcePool 测试"""

    def test_create_pool(self):
        pool = ResourcePool(name="ki", max_value=5, current_value=5, resource_type=ResourceType.KI.value)
        assert pool.current_value == 5
        assert pool.max_value == 5

    def test_spend_success(self):
        pool = ResourcePool(name="ki", max_value=5, current_value=5)
        result = pool.spend(2)
        assert result.success is True
        assert result.remaining == 3
        assert result.spent == 2

    def test_spend_insufficient(self):
        pool = ResourcePool(name="ki", max_value=5, current_value=1)
        result = pool.spend(3)
        assert result.success is False
        assert result.remaining == 1
        assert result.spent == 0

    def test_spend_zero(self):
        pool = ResourcePool(name="ki", max_value=5, current_value=5)
        result = pool.spend(0)
        assert result.success is False

    def test_restore_full(self):
        pool = ResourcePool(name="ki", max_value=5, current_value=2)
        restored = pool.restore(-1)
        assert restored == 3
        assert pool.current_value == 5

    def test_restore_partial(self):
        pool = ResourcePool(name="ki", max_value=5, current_value=2)
        restored = pool.restore(2)
        assert restored == 2
        assert pool.current_value == 4

    def test_restore_cap(self):
        pool = ResourcePool(name="ki", max_value=5, current_value=4)
        restored = pool.restore(10)
        assert restored == 1
        assert pool.current_value == 5

    def test_reset(self):
        pool = ResourcePool(name="ki", max_value=5, current_value=0)
        pool.reset()
        assert pool.current_value == 5

    def test_to_dict_and_from_dict(self):
        pool = ResourcePool(
            name="rage", max_value=3, current_value=2,
            recharge_on="short_rest", resource_type=ResourceType.RAGE.value,
        )
        d = pool.to_dict()
        restored = ResourcePool.from_dict(d)
        assert restored.name == pool.name
        assert restored.max_value == pool.max_value
        assert restored.current_value == pool.current_value
        assert restored.resource_type == ResourceType.RAGE.value

    def test_pool_type_default(self):
        pool = ResourcePool(name="test", max_value=5, current_value=5)
        assert pool.pool_type == PoolType.REGEN.value

    def test_spend_result_message(self):
        pool = ResourcePool(name="ki", max_value=5, current_value=1)
        result = pool.spend(3)
        assert "资源不足" in result.message


# ═══════════════════════════════════════════════════════════════
# ResourceManager 测试
# ═══════════════════════════════════════════════════════════════

class TestResourceManager:
    """ResourceManager 测试"""

    def setup_method(self):
        self.rm = ResourceManager()

    def test_create_and_get_pool(self):
        pool = ResourcePool(name="ki", max_value=5, current_value=5)
        self.rm.create_pool("c1", pool)
        got = self.rm.get_pool("c1", "ki")
        assert got is not None
        assert got.max_value == 5

    def test_spend(self):
        self.rm.create_pool("c1", ResourcePool(name="ki", max_value=5, current_value=5))
        result = self.rm.spend("c1", "ki", 2)
        assert result.success is True
        assert result.remaining == 3

    def test_spend_nonexistent_pool(self):
        result = self.rm.spend("c1", "nonexistent")
        assert result.success is False

    def test_restore(self):
        self.rm.create_pool("c1", ResourcePool(name="ki", max_value=5, current_value=2))
        restored = self.rm.restore("c1", "ki", 2)
        assert restored == 2

    def test_restore_nonexistent(self):
        restored = self.rm.restore("c1", "nonexistent")
        assert restored == 0

    def test_recharge_all_short_rest(self):
        self.rm.create_pool("c1", ResourcePool(name="ki", max_value=5, current_value=0, recharge_on="short_rest"))
        self.rm.create_pool("c1", ResourcePool(name="rage", max_value=3, current_value=0, recharge_on="short_rest"))
        self.rm.create_pool("c1", ResourcePool(name="lay_on_hands", max_value=10, current_value=0, recharge_on="long_rest"))
        recharged = self.rm.recharge_all("c1", "short_rest")
        assert set(recharged) == {"ki", "rage"}
        assert self.rm.get_pool("c1", "ki").current_value == 5
        assert self.rm.get_pool("c1", "lay_on_hands").current_value == 0

    def test_get_pools(self):
        self.rm.create_pool("c1", ResourcePool(name="ki", max_value=5, current_value=5))
        self.rm.create_pool("c1", ResourcePool(name="rage", max_value=3, current_value=3))
        pools = self.rm.get_pools("c1")
        assert len(pools) == 2

    def test_get_pools_by_type(self):
        self.rm.create_pool("c1", ResourcePool(name="rage", max_value=3, current_value=3, resource_type=ResourceType.RAGE.value))
        self.rm.create_pool("c1", ResourcePool(name="ki", max_value=5, current_value=5, resource_type=ResourceType.KI.value))
        rage_pools = self.rm.get_pools_by_type("c1", ResourceType.RAGE.value)
        assert len(rage_pools) == 1
        assert rage_pools[0].name == "rage"

    def test_remove_pool(self):
        self.rm.create_pool("c1", ResourcePool(name="ki", max_value=5, current_value=5))
        assert self.rm.remove_pool("c1", "ki") is True
        assert self.rm.get_pool("c1", "ki") is None

    def test_remove_pool_not_found(self):
        assert self.rm.remove_pool("c1", "nonexistent") is False

    def test_clear(self):
        self.rm.create_pool("c1", ResourcePool(name="ki", max_value=5, current_value=5))
        self.rm.clear("c1")
        assert self.rm.get_pools("c1") == {}


# ═══════════════════════════════════════════════════════════════
# CLASS_FEATURES 数据完整性测试 (CHR-001)
# ═══════════════════════════════════════════════════════════════

class TestClassFeaturesData:
    """12 职业特性数据完整性"""

    EXPECTED_CLASSES = [
        "barbarian", "bard", "cleric", "druid", "fighter", "monk",
        "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard",
    ]

    def test_all_12_classes_present(self):
        for cls in self.EXPECTED_CLASSES:
            assert cls in CLASS_FEATURES, f"缺少职业: {cls}"

    def test_all_classes_have_level_1_features(self):
        for cls in self.EXPECTED_CLASSES:
            assert 1 in CLASS_FEATURES[cls], f"{cls} 缺少 1 级特性"
            assert len(CLASS_FEATURES[cls][1]) > 0, f"{cls} 1 级特性为空"

    def test_all_classes_have_level_2_features(self):
        for cls in self.EXPECTED_CLASSES:
            assert 2 in CLASS_FEATURES[cls], f"{cls} 缺少 2 级特性"

    def test_all_classes_have_level_5_features(self):
        for cls in self.EXPECTED_CLASSES:
            assert 5 in CLASS_FEATURES[cls], f"{cls} 缺少 5 级特性"

    def test_all_features_validate(self):
        for cls, levels in CLASS_FEATURES.items():
            for level, features in levels.items():
                for feat in features:
                    errors = feat.validate()
                    assert errors == [], f"{cls} Lv{level} {feat.feature_id}: {errors}"

    def test_barbarian_rage_has_resource_pool(self):
        rage = CLASS_FEATURES["barbarian"][1][0]
        assert rage.feature_id == "barbarian_rage"
        assert rage.feature_type == FeatureType.RESOURCE
        assert rage.resource_pool is not None
        assert rage.resource_pool["resource_type"] == ResourceType.RAGE.value

    def test_monk_ki_has_resource_pool(self):
        ki_feat = CLASS_FEATURES["monk"][2][0]
        assert ki_feat.feature_id == "monk_ki"
        assert ki_feat.resource_pool is not None
        assert ki_feat.resource_pool["resource_type"] == ResourceType.KI.value

    def test_bard_inspiration_has_resource_pool(self):
        insp = CLASS_FEATURES["bard"][1][0]
        assert insp.feature_id == "bard_bardic_inspiration"
        assert insp.resource_pool is not None
        assert insp.resource_pool["resource_type"] == ResourceType.BARDIC_INSPIRATION.value

    def test_fighter_extra_attack_at_level_5(self):
        features = CLASS_FEATURES["fighter"][5]
        extra_attack = [f for f in features if f.feature_id == "fighter_extra_attack"]
        assert len(extra_attack) == 1
        assert any(m.get("stat") == "extra_attacks" for m in extra_attack[0].modifiers)

    def test_rogue_sneak_attack_at_level_1(self):
        features = CLASS_FEATURES["rogue"][1]
        sneak = [f for f in features if f.feature_id == "rogue_sneak_attack"]
        assert len(sneak) == 1
        assert sneak[0].feature_type == FeatureType.PASSIVE


# ═══════════════════════════════════════════════════════════════
# SUBCLASS_FEATURES 数据完整性测试 (CHR-002)
# ═══════════════════════════════════════════════════════════════

class TestSubclassFeaturesData:
    """子职业数据完整性"""

    def test_all_12_classes_have_subclass(self):
        for cls in TestClassFeaturesData.EXPECTED_CLASSES:
            assert cls in SUBCLASS_FEATURES, f"{cls} 缺少子职业数据"
            assert len(SUBCLASS_FEATURES[cls]) >= 1, f"{cls} 没有子职业"

    def test_subclass_features_validate(self):
        for cls, subs in SUBCLASS_FEATURES.items():
            for sub_name, levels in subs.items():
                for level, features in levels.items():
                    for feat in features:
                        errors = feat.validate()
                        assert errors == [], f"{cls}/{sub_name} Lv{level} {feat.feature_id}: {errors}"

    def test_berserker_has_frenzy_at_3(self):
        berserker = SUBCLASS_FEATURES["barbarian"]["berserker"]
        assert 3 in berserker
        feat_ids = [f.feature_id for f in berserker[3]]
        assert "berserker_frenzy" in feat_ids

    def test_champion_has_improved_critical_at_3(self):
        champion = SUBCLASS_FEATURES["fighter"]["champion"]
        assert 3 in champion
        feat_ids = [f.feature_id for f in champion[3]]
        assert "champion_improved_critical" in feat_ids

    def test_life_domain_has_disciple_of_life(self):
        life = SUBCLASS_FEATURES["cleric"]["life"]
        all_feats = []
        for feats in life.values():
            all_feats.extend(feats)
        feat_ids = [f.feature_id for f in all_feats]
        assert "life_disciple_of_life" in feat_ids


# ═══════════════════════════════════════════════════════════════
# LevelUpService 测试 (CHR-007)
# ═══════════════════════════════════════════════════════════════

class TestLevelUpService:
    """升级服务测试"""

    def setup_method(self):
        self.gm = GrantManager()
        self.cm = ChoiceManager()
        self.rm = ResourceManager()
        self.svc = LevelUpService(self.gm, self.cm, self.rm)

    def test_plan_level_1_barbarian(self):
        plan = self.svc.plan_level_up("c1", "barbarian", 1, {"con_mod": 3})
        assert plan.hp_increase == 15  # 12 + 3
        assert len(plan.new_features) >= 2  # rage + unarmored defense
        assert plan.new_level == 1

    def test_plan_level_1_hp_with_con(self):
        plan = self.svc.plan_level_up("c1", "wizard", 1, {"con_mod": 2})
        assert plan.hp_increase == 8  # 6 + 2

    def test_plan_level_5_avg_hp(self):
        plan = self.svc.plan_level_up("c1", "fighter", 5, {"con_mod": 2})
        # fighter hit die = 10, avg = (10//2) + 1 + 2 = 8
        assert plan.hp_increase == 8

    def test_plan_level_1_min_hp(self):
        plan = self.svc.plan_level_up("c1", "wizard", 1, {"con_mod": -2})
        # 6 + (-2) = 4, still positive
        assert plan.hp_increase == 4

    def test_plan_level_5_negative_con_min_1(self):
        plan = self.svc.plan_level_up("c1", "fighter", 5, {"con_mod": -4})
        # avg = 5 + 1 + (-4) = 2, still >= 1
        assert plan.hp_increase >= 1

    def test_execute_level_1_grants_proficiency(self):
        plan = self.svc.plan_level_up("c1", "rogue", 1, {})
        log = self.svc.execute_level_up(plan)
        # rogue level 1 has thieves_talent which grants thieves_cant proficiency
        assert self.gm.has_proficiency("c1", "thieves_cant")

    def test_execute_level_1_creates_resource_pool(self):
        plan = self.svc.plan_level_up("c1", "barbarian", 1, {})
        self.svc.execute_level_up(plan)
        rage_pool = self.rm.get_pool("c1", "rage")
        assert rage_pool is not None
        assert rage_pool.max_value == 2
        assert rage_pool.current_value == 2

    def test_execute_level_2_monk_creates_ki(self):
        plan = self.svc.plan_level_up("c1", "monk", 2, {})
        self.svc.execute_level_up(plan)
        ki_pool = self.rm.get_pool("c1", "ki")
        assert ki_pool is not None
        assert ki_pool.max_value == 2

    def test_plan_generates_choice_requests(self):
        plan = self.svc.plan_level_up("c1", "fighter", 1, {})
        # fighter level 1 has fighting style choice
        assert len(plan.choice_requests) >= 1
        choice_types = [r.choice_type for r in plan.choice_requests]
        assert "fighting_style" in choice_types

    def test_plan_with_subclass(self):
        plan = self.svc.plan_level_up("c1", "barbarian", 3, {"subclass": "berserker"})
        feat_ids = [f.feature_id for f in plan.new_features]
        assert "berserker_frenzy" in feat_ids

    def test_execute_returns_log(self):
        plan = self.svc.plan_level_up("c1", "barbarian", 1, {})
        log = self.svc.execute_level_up(plan)
        assert any(e["type"] == "level_up" for e in log)
        level_event = [e for e in log if e["type"] == "level_up"][0]
        assert level_event["new_level"] == 1
        assert level_event["class_name"] == "barbarian"

    def test_plan_level_up_bard_inspiration(self):
        plan = self.svc.plan_level_up("c1", "bard", 1, {})
        self.svc.execute_level_up(plan)
        pool = self.rm.get_pool("c1", "bardic_inspiration")
        assert pool is not None
        assert pool.resource_type == ResourceType.BARDIC_INSPIRATION.value

    def test_plan_level_up_paladin_lay_on_hands(self):
        plan = self.svc.plan_level_up("c1", "paladin", 1, {})
        self.svc.execute_level_up(plan)
        pool = self.rm.get_pool("c1", "lay_on_hands")
        assert pool is not None
        assert pool.resource_type == ResourceType.LAY_ON_HANDS.value

    def test_plan_to_dict(self):
        plan = self.svc.plan_level_up("c1", "fighter", 1, {})
        d = plan.to_dict()
        assert d["entity_id"] == "c1"
        assert d["new_level"] == 1
        assert isinstance(d["new_features"], list)
        assert isinstance(d["choice_requests"], list)

    def test_execute_grants_spells(self):
        plan = self.svc.plan_level_up("c1", "wizard", 1, {})
        self.svc.execute_level_up(plan)
        # wizard gets spellbook with cantrip and level 1 spells
        spells = self.gm.get_granted_spells("c1")
        assert len(spells) >= 1

    def test_sorcery_points_resource_type(self):
        plan = self.svc.plan_level_up("c1", "sorcerer", 2, {})
        self.svc.execute_level_up(plan)
        pool = self.rm.get_pool("c1", "sorcery_points")
        assert pool is not None
        assert pool.resource_type == ResourceType.SORCERY_POINTS.value

    def test_channel_divinity_resource_type(self):
        plan = self.svc.plan_level_up("c1", "cleric", 2, {})
        self.svc.execute_level_up(plan)
        pool = self.rm.get_pool("c1", "channel_divinity")
        assert pool is not None
        assert pool.resource_type == ResourceType.CHANNEL_DIVINITY.value


# ═══════════════════════════════════════════════════════════════
# 集成测试 — 完整升级流程
# ═══════════════════════════════════════════════════════════════

class TestLevelUpIntegration:
    """集成测试：完整升级流程"""

    def test_barbarian_1_to_5_full_progression(self):
        gm = GrantManager()
        cm = ChoiceManager()
        rm = ResourceManager()
        svc = LevelUpService(gm, cm, rm)

        # Level 1
        plan1 = svc.plan_level_up("barb1", "barbarian", 1, {"con_mod": 2})
        svc.execute_level_up(plan1)
        assert rm.get_pool("barb1", "rage") is not None

        # Level 2
        plan2 = svc.plan_level_up("barb1", "barbarian", 2, {"con_mod": 2})
        svc.execute_level_up(plan2)
        assert gm.get_grants("barb1", "action")  # reckless attack

        # Level 3 with subclass
        plan3 = svc.plan_level_up("barb1", "barbarian", 3, {"con_mod": 2, "subclass": "berserker"})
        svc.execute_level_up(plan3)

        # Level 5
        plan5 = svc.plan_level_up("barb1", "barbarian", 5, {"con_mod": 2})
        svc.execute_level_up(plan5)
        # extra attacks
        mods = [g for g in gm.get_grants("barb1", "modifier") if g.target == "extra_attacks"]
        assert len(mods) >= 1

    def test_monk_1_to_5_with_ki(self):
        gm = GrantManager()
        cm = ChoiceManager()
        rm = ResourceManager()
        svc = LevelUpService(gm, cm, rm)

        # Level 1
        svc.execute_level_up(svc.plan_level_up("monk1", "monk", 1, {}))
        # Level 2 — ki pool created
        svc.execute_level_up(svc.plan_level_up("monk1", "monk", 2, {}))
        ki = rm.get_pool("monk1", "ki")
        assert ki is not None
        # spend ki
        result = rm.spend("monk1", "ki", 1)
        assert result.success is True
        # short rest recharge
        rm.recharge_all("monk1", "short_rest")
        assert rm.get_pool("monk1", "ki").current_value == 2

    def test_rogue_proficiency_grant(self):
        gm = GrantManager()
        cm = ChoiceManager()
        rm = ResourceManager()
        svc = LevelUpService(gm, cm, rm)

        svc.execute_level_up(svc.plan_level_up("rogue1", "rogue", 1, {}))
        assert gm.has_proficiency("rogue1", "thieves_cant")
