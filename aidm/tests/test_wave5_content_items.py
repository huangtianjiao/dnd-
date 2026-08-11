"""Wave 5 内容数据与物品系统测试 — CHR-003~006, CHAR-008, ITEM-001/003/004。"""

from __future__ import annotations

import pytest


# ═══════════════════════════════════════════════════════════════
# CHR-003 — 74 专长可执行定义
# ═══════════════════════════════════════════════════════════════


class TestFeatsExecutable:
    """CHR-003: 74 专长可执行定义测试"""

    def test_total_count(self):
        """应有 74 个专长定义"""
        from aidm.data.feats_executable import EXECUTABLE_FEATS
        assert len(EXECUTABLE_FEATS) == 74

    def test_all_have_feature_id(self):
        """所有专长都有 feature_id"""
        from aidm.data.feats_executable import EXECUTABLE_FEATS
        for key, feat in EXECUTABLE_FEATS.items():
            assert feat.feature_id, f"{key} 缺少 feature_id"
            assert feat.name, f"{key} 缺少 name"

    def test_origin_feats_present(self):
        """10 个起源专长全覆盖"""
        from aidm.data.feats_executable import EXECUTABLE_FEATS
        origin_keys = ["alert", "crafter", "healer", "lucky", "magic_initiate",
                       "musician", "savage_attacker", "skilled", "tavern_brawler", "tough"]
        for key in origin_keys:
            assert key in EXECUTABLE_FEATS, f"缺少起源专长: {key}"

    def test_fighting_style_feats(self):
        """9 个战斗风格专长全覆盖"""
        from aidm.data.feats_executable import EXECUTABLE_FEATS
        fs_keys = ["archery", "blind_fighting", "defense", "dueling",
                   "great_weapon_fighting", "interception", "protection",
                   "thrown_weapon_fighting", "two_weapon_fighting"]
        for key in fs_keys:
            assert key in EXECUTABLE_FEATS, f"缺少战斗风格专长: {key}"

    def test_epic_boon_feats(self):
        """12 个传奇恩惠全覆盖"""
        from aidm.data.feats_executable import EXECUTABLE_FEATS
        boon_keys = [k for k in EXECUTABLE_FEATS if k.startswith("boon_")]
        assert len(boon_keys) == 12

    def test_lucky_has_resource_pool(self):
        """幸运专长有资源池"""
        from aidm.data.feats_executable import EXECUTABLE_FEATS
        lucky = EXECUTABLE_FEATS["lucky"]
        assert lucky.resource_pool is not None
        assert lucky.resource_pool["name"] == "luck_points"

    def test_alert_has_modifier(self):
        """警戒专长有先攻修正"""
        from aidm.data.feats_executable import EXECUTABLE_FEATS
        alert = EXECUTABLE_FEATS["alert"]
        assert len(alert.modifiers) > 0

    def test_tough_hp_bonus(self):
        """健壮专长有 HP 加值"""
        from aidm.data.feats_executable import EXECUTABLE_FEATS
        tough = EXECUTABLE_FEATS["tough"]
        assert any(m.get("field") == "hp_per_level" for m in tough.modifiers)

    def test_get_executable_feat(self):
        """get_executable_feat 函数可用"""
        from aidm.data.feats_executable import get_executable_feat
        assert get_executable_feat("alert") is not None
        assert get_executable_feat("nonexistent") is None

    def test_feat_validate(self):
        """所有专长定义通过 validate()"""
        from aidm.data.feats_executable import EXECUTABLE_FEATS
        for key, feat in EXECUTABLE_FEATS.items():
            errors = feat.validate()
            assert not errors, f"{key} 校验失败: {errors}"


# ═══════════════════════════════════════════════════════════════
# CHR-004 — 10 物种结构化特质
# ═══════════════════════════════════════════════════════════════


class TestSpeciesExecutable:
    """CHR-004: 10 物种结构化特质测试"""

    def test_total_count(self):
        """应有 10 个物种"""
        from aidm.data.species_executable import SPECIES_DEFINITIONS
        assert len(SPECIES_DEFINITIONS) == 10

    def test_all_have_required_fields(self):
        """所有物种都有必需字段"""
        from aidm.data.species_executable import SPECIES_DEFINITIONS
        required = ["species_id", "name", "size", "speed_ft", "features", "languages"]
        for key, sp in SPECIES_DEFINITIONS.items():
            for field in required:
                assert field in sp, f"{key} 缺少字段 {field}"

    def test_human_speed(self):
        """人类速度 30"""
        from aidm.data.species_executable import get_species_speed
        assert get_species_speed("human") == 30

    def test_goliath_speed(self):
        """歌利亚速度 35"""
        from aidm.data.species_executable import get_species_speed
        assert get_species_speed("goliath") == 35

    def test_dwarf_darkvision(self):
        """矮人黑暗视觉 120"""
        from aidm.data.species_executable import get_species_darkvision
        assert get_species_darkvision("dwarf") == 120

    def test_elf_darkvision(self):
        """精灵黑暗视觉 60"""
        from aidm.data.species_executable import get_species_darkvision
        assert get_species_darkvision("elf") == 60

    def test_dwarf_has_poison_resistance(self):
        """矮人有毒素抗性"""
        from aidm.data.species_executable import get_species_resistances
        assert "poison" in get_species_resistances("dwarf")

    def test_aasimar_resistances(self):
        """阿斯莫有光耀和暗蚀抗性"""
        from aidm.data.species_executable import get_species_resistances
        resists = get_species_resistances("aasimar")
        assert "radiant" in resists
        assert "necrotic" in resists

    def test_elf_has_subraces(self):
        """精灵有子族"""
        from aidm.data.species_executable import get_species
        elf = get_species("elf")
        assert elf["subraces"] is not None
        assert len(elf["subraces"]) == 3


# ═══════════════════════════════════════════════════════════════
# CHR-005 — 16 背景约束定义
# ═══════════════════════════════════════════════════════════════


class TestBackgroundsExecutable:
    """CHR-005: 16 背景约束定义测试"""

    def test_total_count(self):
        """应有 16 个背景"""
        from aidm.data.backgrounds_executable import BACKGROUND_DEFINITIONS
        assert len(BACKGROUND_DEFINITIONS) == 16

    def test_all_have_required_fields(self):
        """所有背景都有必需字段"""
        from aidm.data.backgrounds_executable import BACKGROUND_DEFINITIONS
        required = ["background_id", "name", "ability_scores", "skill_choices", "origin_feat_options"]
        for key, bg in BACKGROUND_DEFINITIONS.items():
            for field in required:
                assert field in bg, f"{key} 缺少字段 {field}"

    def test_acolyte_skills(self):
        """侍僧技能选择"""
        from aidm.data.backgrounds_executable import get_background_skills
        skills = get_background_skills("acolyte")
        assert "insight" in skills
        assert "religion" in skills

    def test_soldier_feat(self):
        """士兵起源专长"""
        from aidm.data.backgrounds_executable import get_background_feat
        feat = get_background_feat("soldier")
        assert "savage_attacker" in feat

    def test_get_background(self):
        """get_background 函数可用"""
        from aidm.data.backgrounds_executable import get_background
        assert get_background("acolyte") is not None
        assert get_background("nonexistent") is None


# ═══════════════════════════════════════════════════════════════
# CHR-006 — MulticlassService
# ═══════════════════════════════════════════════════════════════


class TestMulticlassService:
    """CHR-006: MulticlassService 完整测试"""

    def test_validate_multiclass_success(self):
        """兼职法师成功（INT>=13）"""
        from aidm.engine.multiclass import MulticlassService
        svc = MulticlassService()
        result = svc.validate_multiclass({}, "法师", {"int": 13})
        assert result["valid"] is True

    def test_validate_multiclass_fail(self):
        """兼职法师失败（INT<13）"""
        from aidm.engine.multiclass import MulticlassService
        svc = MulticlassService()
        result = svc.validate_multiclass({}, "法师", {"int": 12})
        assert result["valid"] is False

    def test_proficiencies_granted(self):
        """兼职战士获得护甲和武器熟练"""
        from aidm.engine.multiclass import MulticlassService
        svc = MulticlassService()
        result = svc.get_proficiencies_granted("战士", set())
        assert "light" in result["armor"]
        assert "simple" in result["weapons"]

    def test_proficiencies_dedup(self):
        """已有熟练不重复授予"""
        from aidm.engine.multiclass import MulticlassService
        svc = MulticlassService()
        result = svc.get_proficiencies_granted("战士", {"light", "simple"})
        assert "light" not in result["armor"]
        assert "simple" not in result["weapons"]

    def test_extra_attack_no_stack(self):
        """Extra Attack 同名不叠加"""
        from aidm.engine.multiclass import MulticlassService
        svc = MulticlassService()
        # 战士5+野蛮人5 都有 Extra Attack，但只算 1 次
        features = ["fighter_extra_attack", "barbarian_extra_attack"]
        assert svc.calculate_extra_attacks(features) == 1

    def test_extra_attack_none(self):
        """无 Extra Attack"""
        from aidm.engine.multiclass import MulticlassService
        svc = MulticlassService()
        assert svc.calculate_extra_attacks([]) == 0

    def test_pact_slots(self):
        """魔契师独立法术位"""
        from aidm.engine.multiclass import MulticlassService
        svc = MulticlassService()
        slots = svc.get_pact_slots(1)
        assert slots == {1: 1}
        slots = svc.get_pact_slots(5)
        assert slots == {3: 2}

    def test_spell_slots_merge(self):
        """多职业法术位合并"""
        from aidm.engine.multiclass import MulticlassService
        svc = MulticlassService()
        slots = svc.get_spell_slots({"法师": 3, "牧师": 2})
        assert slots[3] == 2  # 5 级施法者有 3 环 2 位


# ═══════════════════════════════════════════════════════════════
# CHAR-008 — CharacterBuilder
# ═══════════════════════════════════════════════════════════════


class TestCharacterBuilder:
    """CHAR-008: CharacterBuilder 测试"""

    def test_validate_valid_build(self):
        """合法角色创建无错误"""
        from aidm.build.character_builder import CharacterBuilder, CharacterBuildPlan
        from aidm.rules.grant import GrantManager
        from aidm.rules.choice import ChoiceManager
        from aidm.rules.resource import ResourceManager

        builder = CharacterBuilder(GrantManager(), ChoiceManager(), ResourceManager())
        plan = CharacterBuildPlan(
            entity_id="test_char",
            species_choice="human",
            background_choice="acolyte",
            class_choice="fighter",
            ability_scores={"str": 15, "dex": 13, "con": 14, "int": 10, "wis": 12, "cha": 8},
            skill_choices=["insight", "religion"],
        )
        errors = builder.validate_build(plan)
        assert errors == []

    def test_validate_invalid_species(self):
        """无效物种报错"""
        from aidm.build.character_builder import CharacterBuilder, CharacterBuildPlan
        from aidm.rules.grant import GrantManager
        from aidm.rules.choice import ChoiceManager
        from aidm.rules.resource import ResourceManager

        builder = CharacterBuilder(GrantManager(), ChoiceManager(), ResourceManager())
        plan = CharacterBuildPlan(
            entity_id="test_char",
            species_choice="invalid_species",
            background_choice="acolyte",
            class_choice="fighter",
            ability_scores={"str": 15, "dex": 13, "con": 14, "int": 10, "wis": 12, "cha": 8},
            skill_choices=["insight", "religion"],
        )
        errors = builder.validate_build(plan)
        assert any("物种" in e for e in errors)

    def test_build_character_basic(self):
        """基本角色创建"""
        from aidm.build.character_builder import CharacterBuilder, CharacterBuildPlan
        from aidm.rules.grant import GrantManager
        from aidm.rules.choice import ChoiceManager
        from aidm.rules.resource import ResourceManager

        builder = CharacterBuilder(GrantManager(), ChoiceManager(), ResourceManager())
        plan = CharacterBuildPlan(
            entity_id="test_char",
            species_choice="human",
            background_choice="acolyte",
            class_choice="fighter",
            ability_scores={"str": 15, "dex": 13, "con": 14, "int": 10, "wis": 12, "cha": 8},
            skill_choices=["insight", "religion"],
        )
        result = builder.build_character(plan)
        assert result["char_class"] == "fighter"
        assert result["level"] == 1
        assert result["hp_max"] > 0
        assert result["ac"] > 0

    def test_calculate_starting_hp(self):
        """HP 计算正确"""
        from aidm.build.character_builder import CharacterBuilder, CharacterBuildPlan
        from aidm.rules.grant import GrantManager
        from aidm.rules.choice import ChoiceManager
        from aidm.rules.resource import ResourceManager

        builder = CharacterBuilder(GrantManager(), ChoiceManager(), ResourceManager())
        plan = CharacterBuildPlan(
            entity_id="test_char",
            species_choice="human",
            background_choice="acolyte",
            class_choice="fighter",
            ability_scores={"str": 15, "dex": 13, "con": 14, "int": 10, "wis": 12, "cha": 8},
            skill_choices=["insight", "religion"],
        )
        char_data = {"abilities": plan.ability_scores}
        starting = builder.calculate_starting_values(plan, char_data)
        # 战士 HP = 10 (d10) + 2 (CON mod) = 12
        assert starting["hp_max"] == 12


# ═══════════════════════════════════════════════════════════════
# ITEM-001 — 物品栏结构化
# ═══════════════════════════════════════════════════════════════


class TestItemStructured:
    """ITEM-001: 物品栏结构化测试"""

    def test_items_structured_field_exists(self):
        """Character 模型有 items_structured_json 字段"""
        from aidm.stats.models import Character
        char = Character(name="Test", hp_current=10, hp_max=10)
        assert hasattr(char, "items_structured_json")

    def test_add_structured_item(self):
        """添加结构化物品"""
        from aidm.stats.models import Character
        char = Character(name="Test", hp_current=10, hp_max=10)
        item = {"item_id": "item.sword", "name": "长剑", "quantity": 1}
        char.add_structured_item(item)
        items = char.items_structured
        assert len(items) == 1
        assert items[0]["item_id"] == "item.sword"

    def test_remove_structured_item(self):
        """移除结构化物品"""
        from aidm.stats.models import Character
        char = Character(name="Test", hp_current=10, hp_max=10)
        char.add_structured_item({"item_id": "item.sword", "name": "长剑"})
        char.add_structured_item({"item_id": "item.shield", "name": "盾牌"})
        assert char.remove_structured_item("item.sword") is True
        items = char.items_structured
        assert len(items) == 1
        assert items[0]["item_id"] == "item.shield"

    def test_migrate_inventory(self):
        """从字符串迁移到结构化"""
        from aidm.stats.models import Character
        char = Character(name="Test", hp_current=10, hp_max=10)
        char.set_inventory(["火焰剑", "治疗药水"])
        migrated = char.migrate_inventory_to_structured()
        assert migrated == 2
        items = char.items_structured
        assert len(items) == 2


# ═══════════════════════════════════════════════════════════════
# ITEM-003 — 同调效果授予/撤销
# ═══════════════════════════════════════════════════════════════


class TestAttunementService:
    """ITEM-003: 同调效果授予/撤销测试"""

    def test_attune_with_effects(self):
        """同调授予效果"""
        from aidm.engine.attunement import AttunementService
        from aidm.rules.grant import GrantManager

        gm = GrantManager()
        svc = AttunementService(gm)
        result = svc.attune_with_effects(
            entity_id="char1",
            current_attuned=[],
            item_name="火焰剑",
            item_effects={
                "modifier": {"target": "fire_damage", "value": "1d6"},
            },
        )
        assert result["success"] is True
        assert "火焰剑" in result["new_attuned"]
        assert len(result["grants"]) == 1
        # 验证 Grant 已添加
        grants = gm.get_grants("char1")
        assert len(grants) == 1

    def test_end_attunement_removes_effects(self):
        """解除同调撤销效果"""
        from aidm.engine.attunement import AttunementService
        from aidm.rules.grant import GrantManager

        gm = GrantManager()
        svc = AttunementService(gm)
        # 先同调
        svc.attune_with_effects(
            entity_id="char1",
            current_attuned=[],
            item_name="火焰剑",
            item_effects={"modifier": {"target": "fire_damage", "value": "1d6"}},
        )
        # 解除同调
        result = svc.end_attunement_with_effects("char1", ["火焰剑"], "火焰剑")
        assert result["success"] is True
        assert "火焰剑" not in result["new_attuned"]
        assert result["removed_grants"] == 1
        # 验证 Grant 已移除
        grants = gm.get_grants("char1")
        assert len(grants) == 0

    def test_attune_limit_3(self):
        """同调上限 3 件"""
        from aidm.engine.attunement import AttunementService

        svc = AttunementService()
        result = svc.attune_with_effects(
            entity_id="char1",
            current_attuned=["A", "B", "C"],
            item_name="D",
        )
        assert result["success"] is False
        assert "上限" in result["reason"]

    def test_attune_prerequisite_check(self):
        """同调先决条件检查"""
        from aidm.engine.attunement import AttunementService

        svc = AttunementService()
        result = svc.attune_with_effects(
            entity_id="char1",
            current_attuned=[],
            item_name="圣剑",
            item_requires={"class": ["圣武士"]},
            char_class="法师",
        )
        assert result["success"] is False
        assert "职业" in result["reason"]


# ═══════════════════════════════════════════════════════════════
# ITEM-004 — 魔法物品充能/恢复
# ═══════════════════════════════════════════════════════════════


class TestMagicItemsExecutable:
    """ITEM-004: 魔法物品充能/恢复测试"""

    def test_total_items(self):
        """应有多个魔法物品定义"""
        from aidm.data.magic_items_executable import MAGIC_ITEMS_EXECUTABLE
        assert len(MAGIC_ITEMS_EXECUTABLE) >= 20

    def test_potion_consumed(self):
        """治疗药水使用后消耗"""
        from aidm.data.magic_items_executable import use_charges
        result = use_charges("potion_of_healing", 1)
        assert result["success"] is True
        assert result["consumed"] is True
        assert result["remaining"] == 0

    def test_wand_charges(self):
        """魔杖充能使用"""
        from aidm.data.magic_items_executable import use_charges
        result = use_charges("wand_of_magic_missiles", 7, 1)
        assert result["success"] is True
        assert result["remaining"] == 6
        assert result["consumed"] is False

    def test_wand_insufficient_charges(self):
        """魔杖充能不足"""
        from aidm.data.magic_items_executable import use_charges
        result = use_charges("wand_of_magic_missiles", 0, 1)
        assert result["success"] is False

    def test_infinite_charges_item(self):
        """无限充能物品"""
        from aidm.data.magic_items_executable import use_charges
        result = use_charges("flame_tongue", -1, 1)
        assert result["success"] is True
        assert result["remaining"] == -1

    def test_requires_attunement(self):
        """同调需求检查"""
        from aidm.data.magic_items_executable import requires_attunement
        assert requires_attunement("flame_tongue") is True
        assert requires_attunement("potion_of_healing") is False

    def test_get_item_charges(self):
        """获取物品充能数"""
        from aidm.data.magic_items_executable import get_item_charges
        assert get_item_charges("wand_of_magic_missiles") == 7
        assert get_item_charges("flame_tongue") == -1

    def test_get_item_recharge(self):
        """获取物品恢复规则"""
        from aidm.data.magic_items_executable import get_item_recharge
        recharge = get_item_recharge("wand_of_magic_missiles")
        assert recharge is not None
        assert recharge["type"] == "daily"
