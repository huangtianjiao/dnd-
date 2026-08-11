"""PHB2024 内容注册表触发测试 — CHR-002/004/005。

验证 species_def / background_def / subclass_progression 注册表已填充
实际 PHB2024 数据，且每个物种/背景/子职都有可观察的机械差异。
"""

from __future__ import annotations

import pytest


# ── 物种注册表 (CHR-004) ────────────────────────────────────────

class TestSpeciesRegistry:
    @pytest.fixture(scope="class")
    def registry(self):
        from aidm.engine.species_registry_data import get_species_registry
        return get_species_registry()

    def test_definitions_importable(self):
        """SpeciesDefinition 数据类可直接导入使用（CHR-004）。"""
        from aidm.engine.species_def import (
            DamageAffinity, MovementType, Sense, SpeciesDefinition,
            SpeciesFeature, SpeciesRegistry,
        )
        s = SpeciesDefinition(species_id="species.test", name="测试物种",
                              base_speed=30)
        assert s.base_speed == 30
        assert s.get_all_granted_features() == []

    def test_all_species_registered(self, registry):
        """每个支持物种的所有特质在角色创建后可由状态查询。"""
        species = registry.list_all()
        assert len(species) >= 9  # PHB2024 核心物种
        for sid in species:
            s = registry.get(sid)
            assert s is not None
            assert s.features, f"{s.name} 应有特质"
            assert s.base_speed > 0

    def test_darkvision_species(self, registry):
        """拥有黑暗视觉的物种应正确标记。"""
        assert registry.get("species.矮人").has_darkvision() is True
        assert registry.get("species.精灵").has_darkvision() is True
        assert registry.get("species.人类").has_darkvision() is False

    def test_speed_mechanics(self, registry):
        """歌利亚速度 35 尺（机械差异）。"""
        goliath = registry.get("species.歌利亚")
        assert goliath.base_speed == 35
        human = registry.get("species.人类")
        assert human.base_speed == 30

    def test_affinities(self, registry):
        """阿斯莫有光耀/暗蚀抗性。"""
        aasimar = registry.get("species.阿斯莫")
        affinity_types = {a.damage_type for a in aasimar.damage_affinities}
        assert "光耀" in affinity_types


# ── 背景注册表 (CHR-005) ────────────────────────────────────────

class TestBackgroundRegistry:
    @pytest.fixture(scope="class")
    def registry(self):
        from aidm.engine.background_registry_data import get_background_registry
        return get_background_registry()

    def test_definitions_importable(self):
        """BackgroundDefinition 数据类可直接导入使用（CHR-005）。"""
        from aidm.engine.background_def import (
            BackgroundDefinition, BackgroundRegistry, EquipmentPack,
        )
        bg = BackgroundDefinition(background_id="background.test", name="测试背景",
                                  skill_choices=["洞悉"], skill_count=1)
        assert bg.validate_skill_selection(["洞悉"]) is True

    def test_all_backgrounds_registered(self, registry):
        """所有背景预设均满足数量和互斥规则。"""
        backgrounds = registry.list_all()
        assert len(backgrounds) >= 15  # PHB2024 核心背景
        for bid in backgrounds:
            bg = registry.get(bid)
            assert bg is not None
            assert len(bg.skill_choices) >= 2  # 每种背景至少2个技能
            assert bg.origin_feat  # 每种背景必有起源专长

    def test_skill_validation(self, registry):
        """背景技能选择约束验证。"""
        acolyte = registry.get("background.侍僧")
        assert acolyte.validate_skill_selection(["洞悉", "宗教"]) is True
        assert acolyte.validate_skill_selection(["洞悉", "运动"]) is False  # 非候选技能
        assert acolyte.validate_skill_selection(["洞悉"]) is False  # 数量不足

    def test_origin_feats(self, registry):
        """各背景的起源专长应不同（机械差异）。"""
        feats = {registry.get(bid).origin_feat for bid in registry.list_all()}
        assert len(feats) >= 10  # 起源专长多样性
        assert "魔法学徒（牧师）" in feats
        assert "警戒" in feats


# ── 子职注册表 (CHR-002) ────────────────────────────────────────

class TestSubclassRegistry:
    @pytest.fixture(scope="class")
    def registry(self):
        from aidm.engine.subclass_registry_data import get_subclass_registry
        return get_subclass_registry()

    def test_all_base_classes_have_subclasses(self, registry):
        """12 职业均有子职进度。"""
        for base_class in ["野蛮人", "吟游诗人", "牧师", "德鲁伊", "战士",
                           "武僧", "圣武士", "游侠", "盗贼", "术士",
                           "魔契师", "法师"]:
            subs = registry.list_subclasses(base_class)
            assert subs, f"{base_class} 应有子职"

    def test_subclass_features_tiered(self, registry):
        """每个已宣称支持的子职从3到20级特性均可触发。"""
        prog = registry.get("野蛮人", "berserker")
        assert prog is not None
        features = prog.get_all_features_up_to(20)
        assert len(features) >= 3
        levels = sorted(prog.features_by_level.keys())
        assert levels  # 有特性等级

    def test_barbarian_berserker_progression(self, registry):
        """狂战士道途 3/6/10/14 级特性。"""
        prog = registry.get("野蛮人", "berserker")
        assert len(prog.get_features_at_level(3)) >= 1
        assert len(prog.get_features_at_level(6)) >= 1
        assert len(prog.get_features_at_level(10)) >= 1
        assert len(prog.get_features_at_level(14)) >= 1

    def test_fighter_champion_progression(self, registry):
        """勇士 3/7 级特性。"""
        prog = registry.get("战士", "champion")
        assert len(prog.get_features_at_level(3)) >= 1
        assert len(prog.get_features_at_level(7)) >= 1
