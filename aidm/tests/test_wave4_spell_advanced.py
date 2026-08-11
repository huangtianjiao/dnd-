"""Wave 4 高级施法功能测试。

覆盖:
  - SPL-011: 成分/材料真实持握判断（EquipmentSlotsManager）
  - SPL-012: 有价/消耗材料真实扣除
  - SPL-015: 时机型法术专用窗口
  - SPL-016: 召唤/变形/创造物实体生命周期
  - DATA-001: 法术置信度标注
"""

import pytest

# ── SPL-011/012 imports ──
from aidm.engine.spellcasting import (
    CasterState,
    can_cast_with_equipment_slots,
    check_material_availability,
    create_material_consumed_event,
)
from aidm.engine.equipment_slots import (
    EquipmentSlotsManager,
    ItemInstance,
    SlotType,
)
from aidm.data.spells import get_spell

# ── SPL-015 imports ──
from aidm.engine.reaction_window import (
    COUNTERSPELL_REACTION,
    DISPEL_MAGIC,
    LEGENDARY_RESISTANCE_WINDOW,
    SHIELD_REACTION,
    TIMING_SPELL_REGISTRY,
    ReactionController,
    ReactionType,
    get_timing_spell_window,
    open_timing_window,
)

# ── SPL-016 imports ──
from aidm.engine.entity_lifecycle import (
    EntityLifecycleManager,
    FormOverride,
    SummonedEntity,
)

# ── DATA-001 imports ──
from aidm.data.spell_confidence import (
    SpellConfidence,
    SpellConfidenceRegistry,
)


# ════════════════════════════════════════════════════════════════════════
# SPL-011: 成分/材料真实持握判断
# ════════════════════════════════════════════════════════════════════════

class TestCanCastWithEquipmentSlots:
    """SPL-011 成分校验使用 EquipmentSlotsManager 测试。"""

    def test_empty_hands_can_cast_s_component(self):
        """双手空闲时可以完成 S 成分。"""
        spell = get_spell("火球术")  # V, S, M
        slots = EquipmentSlotsManager()
        assert can_cast_with_equipment_slots(
            spell, slots, has_material_pouch=True
        ) is True

    def test_shield_blocks_s_component(self):
        """装备盾牌且无空闲手时无法完成 S 成分。"""
        spell = get_spell("火球术")  # V, S, M
        slots = EquipmentSlotsManager()
        # 主手装备剑，副手装备盾
        slots.equip(ItemInstance(item_id="sword", name="长剑", properties={"is_weapon": True}), SlotType.MAIN_HAND)
        slots.equip(ItemInstance(item_id="shield", name="盾牌", properties={"is_shield": True}), SlotType.OFF_HAND)
        # 无空闲手，无材料包，无法器
        assert can_cast_with_equipment_slots(
            spell, slots, has_material_pouch=False
        ) is False

    def test_focus_allows_s_and_m_together(self):
        """持有法器时同一只手可同时处理 S+M。"""
        spell = get_spell("火球术")  # V, S, M
        slots = EquipmentSlotsManager()
        # 主手持有法器
        slots.equip(ItemInstance(item_id="staff", name="法杖", properties={"is_focus": True}), SlotType.MAIN_HAND)
        # 副手空
        # 有法器 → S 和 M 都满足
        assert can_cast_with_equipment_slots(
            spell, slots, has_material_pouch=False
        ) is True

    def test_focus_slot_satisfies_m(self):
        """focus 槽位的法器可满足 M 成分。"""
        spell = get_spell("火球术")  # V, S, M
        slots = EquipmentSlotsManager()
        # focus 槽位有法器
        slots.equip(ItemInstance(item_id="orb", name="水晶球", properties={"is_focus": True}), SlotType.FOCUS)
        # 双手空闲
        assert can_cast_with_equipment_slots(
            spell, slots, has_material_pouch=False
        ) is True

    def test_material_pouch_satisfies_m(self):
        """材料包可满足无价不消耗的 M 成分。"""
        spell = get_spell("火球术")  # V, S, M (无特殊材料)
        slots = EquipmentSlotsManager()
        # 双手持武器（无法器）
        slots.equip(ItemInstance(item_id="sword", name="长剑", properties={"is_weapon": True}), SlotType.MAIN_HAND)
        # 有材料包
        assert can_cast_with_equipment_slots(
            spell, slots, has_material_pouch=True
        ) is True

    def test_specific_material_required_for_costly(self):
        """有价材料必须实际持有，法器/材料包不可替代。"""
        # 寻找一个有材料价格的法术，或使用复活术类
        # 这里用一个假定的有价材料法术测试
        spell = get_spell("火球术")
        # 模拟一个有价材料法术
        from aidm.data.spells import Spell
        costly_spell = Spell(
            name="测试有价法术",
            en_name="test_costly",
            level=1,
            school="防护",
            casting_time="1 动作",
            casting_time_type="ACTION",
            range="30尺",
            components=frozenset({"V", "S", "M"}),
            material_desc="一颗价值100gp的黑珍珠",
            material_cost_gp=100.0,
            material_consumed=False,
        )
        slots = EquipmentSlotsManager()
        # 有法器但无特定材料
        slots.equip(ItemInstance(item_id="orb", name="水晶球", properties={"is_focus": True}), SlotType.FOCUS)
        assert can_cast_with_equipment_slots(
            costly_spell, slots, has_specific_material=False
        ) is False
        # 有特定材料
        assert can_cast_with_equipment_slots(
            costly_spell, slots, has_specific_material=True
        ) is True

    def test_silenced_blocks_v_component(self):
        """沉默状态阻止 V 成分。"""
        spell = get_spell("火球术")  # 有 V 成分
        slots = EquipmentSlotsManager()
        assert can_cast_with_equipment_slots(
            spell, slots, silenced=True, has_material_pouch=True
        ) is False

    def test_no_components_needed(self):
        """无法术成分需求时总是可以通过。"""
        from aidm.data.spells import Spell
        no_comp_spell = Spell(
            name="测试无成分法术",
            en_name="test_no_comp",
            level=1,
            school="防护",
            casting_time="1 动作",
            casting_time_type="ACTION",
            range="30尺",
            components=frozenset(),  # 无成分
        )
        slots = EquipmentSlotsManager()
        # 即使双手持满也可
        slots.equip(ItemInstance(item_id="sword", name="长剑", properties={"is_weapon": True}), SlotType.MAIN_HAND)
        slots.equip(ItemInstance(item_id="shield", name="盾牌", properties={"is_shield": True}), SlotType.OFF_HAND)
        assert can_cast_with_equipment_slots(no_comp_spell, slots) is True


# ════════════════════════════════════════════════════════════════════════
# SPL-012: 有价/消耗材料真实扣除
# ════════════════════════════════════════════════════════════════════════

class TestMaterialAvailability:
    """SPL-012 材料可用性检查测试。"""

    def test_no_material_component(self):
        """无法术材料成分时总是可提供。"""
        spell = get_spell("魔法飞弹")  # V only
        result = check_material_availability(spell, False, False, False)
        assert result["can_provide"] is True
        assert result["needs_specific"] is False
        assert result["will_consume"] is False

    def test_focus_substitution(self):
        """法器可替代无价不消耗的材料。"""
        spell = get_spell("火球术")  # M: 蝙蝠粪和硫磺（无价）
        result = check_material_availability(
            spell, has_material_pouch=False, has_focus=True, has_specific_material=False
        )
        assert result["can_provide"] is True
        assert result["substituted_by"] == "focus"
        assert result["will_consume"] is False

    def test_pouch_substitution(self):
        """材料包可替代无价不消耗的材料。"""
        spell = get_spell("火球术")
        result = check_material_availability(
            spell, has_material_pouch=True, has_focus=False, has_specific_material=False
        )
        assert result["can_provide"] is True
        assert result["substituted_by"] == "pouch"

    def test_specific_material_needed_for_costly(self):
        """有价材料不可由法器/材料包替代。"""
        from aidm.data.spells import Spell
        costly_spell = Spell(
            name="测试有价法术",
            en_name="test_costly",
            level=1,
            school="防护",
            casting_time="1 动作",
            casting_time_type="ACTION",
            range="30尺",
            components=frozenset({"V", "S", "M"}),
            material_desc="价值100gp的黑珍珠",
            material_cost_gp=100.0,
        )
        result = check_material_availability(
            costly_spell, has_material_pouch=True, has_focus=True, has_specific_material=False
        )
        assert result["can_provide"] is False
        assert result["needs_specific"] is True

    def test_consumed_material_will_consume(self):
        """消耗性材料标记 will_consume=True。"""
        from aidm.data.spells import Spell
        consumed_spell = Spell(
            name="测试消耗法术",
            en_name="test_consumed",
            level=1,
            school="防护",
            casting_time="1 动作",
            casting_time_type="ACTION",
            range="30尺",
            components=frozenset({"V", "S", "M"}),
            material_desc="钻石（消耗）",
            material_consumed=True,
        )
        result = check_material_availability(
            consumed_spell, has_material_pouch=False, has_focus=False, has_specific_material=True
        )
        assert result["can_provide"] is True
        assert result["will_consume"] is True
        assert result["substituted_by"] == "specific"


class TestMaterialConsumedEvent:
    """SPL-012 材料消耗事件测试。"""

    def test_create_consumed_event(self):
        """创建材料消耗事件。"""
        event = create_material_consumed_event(
            spell_name="复活术",
            material_desc="价值300gp的钻石",
            material_cost_gp=300.0,
        )
        assert event["type"] == "ItemConsumed"
        assert event["spell_name"] == "复活术"
        assert event["material_cost_gp"] == 300.0
        assert event["quantity"] == 1


# ════════════════════════════════════════════════════════════════════════
# SPL-015: 时机型法术专用窗口
# ════════════════════════════════════════════════════════════════════════

class TestTimingSpellRegistry:
    """SPL-015 时机型法术注册表测试。"""

    def test_shield_reaction_definition(self):
        """护盾术反应窗口定义正确。"""
        assert SHIELD_REACTION["trigger"] == "on_hit_before_damage"
        assert SHIELD_REACTION["spell_id"] == "shield"
        assert SHIELD_REACTION["cost"] == "reaction"

    def test_counterspell_reaction_definition(self):
        """法术反制反应窗口定义正确。"""
        assert COUNTERSPELL_REACTION["trigger"] == "spell_cast_started"
        assert COUNTERSPELL_REACTION["spell_id"] == "counterspell"
        assert COUNTERSPELL_REACTION["cost"] == "reaction"

    def test_dispel_magic_definition(self):
        """解除魔法定义正确（不需要反应窗口）。"""
        assert DISPEL_MAGIC["trigger"] == "any_time"
        assert DISPEL_MAGIC["cost"] == "action"

    def test_legendary_resistance_definition(self):
        """传奇抗性窗口定义正确。"""
        assert LEGENDARY_RESISTANCE_WINDOW["trigger"] == "saving_throw_failed"
        assert LEGENDARY_RESISTANCE_WINDOW["cost"] == "legendary_action"

    def test_get_timing_spell_window_shield(self):
        """获取护盾术窗口。"""
        window_def = get_timing_spell_window("on_hit_before_damage")
        assert window_def is not None
        assert window_def["spell_id"] == "shield"

    def test_get_timing_spell_window_counterspell(self):
        """获取法术反制窗口。"""
        window_def = get_timing_spell_window("spell_cast_started")
        assert window_def is not None
        assert window_def["spell_id"] == "counterspell"

    def test_get_timing_spell_window_unknown(self):
        """未知触发事件返回 None。"""
        window_def = get_timing_spell_window("unknown_trigger")
        assert window_def is None

    def test_registry_has_all_timing_spells(self):
        """注册表包含所有时机型法术。"""
        assert "on_hit_before_damage" in TIMING_SPELL_REGISTRY
        assert "spell_cast_started" in TIMING_SPELL_REGISTRY
        assert "saving_throw_failed" in TIMING_SPELL_REGISTRY


class TestOpenTimingWindow:
    """SPL-015 开启时机窗口测试。"""

    def test_open_shield_window(self):
        """开启护盾术反应窗口。"""
        controller = ReactionController()
        window = open_timing_window(
            controller=controller,
            trigger_event="on_hit_before_damage",
            context={"attacker": "goblin", "target": "fighter"},
            eligible_reactors=["fighter"],
            controller_id="fighter",
        )
        assert window is not None
        assert window.is_open is True
        assert window.trigger_event == "on_hit_before_damage"
        assert len(window.available_reactions) == 1
        assert window.available_reactions[0].ability_name == "shield"

    def test_open_counterspell_window(self):
        """开启法术反制反应窗口。"""
        controller = ReactionController()
        window = open_timing_window(
            controller=controller,
            trigger_event="spell_cast_started",
            context={"caster": "enemy_mage"},
            eligible_reactors=["player_mage"],
            controller_id="player_mage",
        )
        assert window is not None
        assert window.is_open is True
        assert window.available_reactions[0].ability_name == "counterspell"

    def test_open_unknown_window_returns_none(self):
        """未知触发事件返回 None。"""
        controller = ReactionController()
        window = open_timing_window(
            controller=controller,
            trigger_event="unknown_trigger",
            context={},
            eligible_reactors=["fighter"],
        )
        assert window is None

    def test_open_legendary_resistance_window(self):
        """开启传奇抗性窗口。"""
        controller = ReactionController()
        window = open_timing_window(
            controller=controller,
            trigger_event="saving_throw_failed",
            context={"target": "dragon", "save_type": "DEX"},
            eligible_reactors=["dragon"],
            controller_id="dm",
        )
        assert window is not None
        assert window.available_reactions[0].reaction_type == ReactionType.LEGENDARY_RESISTANCE


# ════════════════════════════════════════════════════════════════════════
# SPL-016: 召唤/变形/创造物实体生命周期
# ════════════════════════════════════════════════════════════════════════

class TestSummonedEntity:
    """SPL-016 召唤物实体测试。"""

    def test_create_summoned_entity(self):
        """创建召唤物实体。"""
        mgr = EntityLifecycleManager()
        entity = mgr.summon(
            summoner_id="wizard_1",
            spell_id="summon_familiar",
            stat_block={"hp": 10, "ac": 13, "name": "猫头鹰"},
            duration=10,
        )
        assert entity.summoner_id == "wizard_1"
        assert entity.spell_id == "summon_familiar"
        assert entity.hp_max == 10
        assert entity.ac == 13
        assert entity.active is True
        assert entity.duration_rounds == 10

    def test_despawn_summoned_entity(self):
        """移除召唤物实体。"""
        mgr = EntityLifecycleManager()
        entity = mgr.summon("wizard_1", "summon_familiar", {"hp": 10}, 10)
        events = mgr.despawn(entity.entity_id)
        assert len(events) == 1
        assert events[0]["type"] == "entity_despawned"
        assert events[0]["entity_id"] == entity.entity_id
        assert mgr.get_summoned(entity.entity_id) is None

    def test_despawn_by_concentration(self):
        """专注打断时移除关联召唤物。"""
        mgr = EntityLifecycleManager()
        entity1 = mgr.summon("wizard_1", "summon_familiar", {"hp": 10}, -1, concentration_id="conc_1")
        entity2 = mgr.summon("wizard_1", "conjure_animals", {"hp": 20}, -1, concentration_id="conc_1")
        entity3 = mgr.summon("wizard_1", "another_spell", {"hp": 15}, -1, concentration_id="conc_2")

        events = mgr.despawn_by_concentration("conc_1")
        assert len(events) == 2
        assert mgr.get_summoned(entity1.entity_id) is None
        assert mgr.get_summoned(entity2.entity_id) is None
        assert mgr.get_summoned(entity3.entity_id) is not None

    def test_despawn_all_by_summoner(self):
        """移除某召唤者的所有召唤物。"""
        mgr = EntityLifecycleManager()
        e1 = mgr.summon("wizard_1", "spell_1", {"hp": 10}, 5)
        e2 = mgr.summon("wizard_1", "spell_2", {"hp": 20}, 5)
        e3 = mgr.summon("wizard_2", "spell_3", {"hp": 15}, 5)

        events = mgr.despawn_all_by_summoner("wizard_1")
        assert len(events) == 2
        assert mgr.get_summoned(e1.entity_id) is None
        assert mgr.get_summoned(e3.entity_id) is not None

    def test_get_all_summoned_by(self):
        """获取某召唤者的所有召唤物。"""
        mgr = EntityLifecycleManager()
        mgr.summon("wizard_1", "spell_1", {"hp": 10}, 5)
        mgr.summon("wizard_1", "spell_2", {"hp": 20}, 5)
        mgr.summon("wizard_2", "spell_3", {"hp": 15}, 5)

        summoned = mgr.get_all_summoned_by("wizard_1")
        assert len(summoned) == 2


class TestFormOverride:
    """SPL-016 变形效果测试。"""

    def test_apply_form_override(self):
        """应用变形效果。"""
        mgr = EntityLifecycleManager()
        override = mgr.apply_form_override(
            target_id="creature_1",
            new_stats={"hp": 50, "ac": 15, "type": "beast"},
            spell_id="polymorph",
            duration=10,
            original_stats={"hp": 20, "ac": 12, "type": "humanoid"},
        )
        assert override.target_id == "creature_1"
        assert override.new_stats["hp"] == 50
        assert override.original_stats["hp"] == 20

    def test_remove_form_override(self):
        """移除变形效果恢复原属性。"""
        mgr = EntityLifecycleManager()
        mgr.apply_form_override(
            target_id="creature_1",
            new_stats={"hp": 50},
            spell_id="polymorph",
            duration=10,
            original_stats={"hp": 20},
        )
        result = mgr.remove_form_override("creature_1")
        assert result["type"] == "form_restored"
        assert result["original_stats"]["hp"] == 20
        assert mgr.get_form_override("creature_1") is None

    def test_remove_nonexistent_override(self):
        """移除不存在的变形效果返回空。"""
        mgr = EntityLifecycleManager()
        result = mgr.remove_form_override("nonexistent")
        assert result == {}


class TestEntityLifecycleRoundTracking:
    """SPL-016 轮次追踪测试。"""

    def test_on_round_end_expires_summon(self):
        """轮次结束时到期召唤物消失。"""
        mgr = EntityLifecycleManager()
        entity = mgr.summon("wizard_1", "spell_1", {"hp": 10}, 2)

        events = mgr.on_round_end(1)
        assert len(events) == 0  # 还有 1 轮

        events = mgr.on_round_end(2)
        assert len(events) == 1
        assert events[0]["reason"] == "duration_expired"
        assert mgr.get_summoned(entity.entity_id) is None

    def test_on_round_end_expires_form_override(self):
        """轮次结束时到期变形效果移除。"""
        mgr = EntityLifecycleManager()
        mgr.apply_form_override(
            target_id="creature_1",
            new_stats={"hp": 50},
            spell_id="polymorph",
            duration=1,
            original_stats={"hp": 20},
        )

        events = mgr.on_round_end(1)
        assert len(events) == 1
        assert events[0]["type"] == "form_restored"
        assert events[0]["reason"] == "duration_expired"

    def test_permanent_summon_not_expired(self):
        """永久召唤物不会因轮次到期消失。"""
        mgr = EntityLifecycleManager()
        entity = mgr.summon("wizard_1", "spell_1", {"hp": 10}, -1)

        for i in range(100):
            events = mgr.on_round_end(i)
        assert mgr.get_summoned(entity.entity_id) is not None

    def test_on_concentration_broken(self):
        """专注被打断时清理所有关联实体。"""
        mgr = EntityLifecycleManager()
        summon = mgr.summon("wizard_1", "spell_1", {"hp": 10}, -1, concentration_id="conc_1")
        mgr.apply_form_override(
            target_id="creature_1",
            new_stats={"hp": 50},
            spell_id="polymorph",
            duration=-1,
            concentration_id="conc_1",
            original_stats={"hp": 20},
        )

        events = mgr.on_concentration_broken("conc_1")
        assert len(events) == 2  # 1 summon + 1 form override
        assert mgr.get_summoned(summon.entity_id) is None
        assert mgr.get_form_override("creature_1") is None


# ════════════════════════════════════════════════════════════════════════
# DATA-001: 法术置信度标注
# ════════════════════════════════════════════════════════════════════════

class TestSpellConfidence:
    """DATA-001 法术置信度测试。"""

    def test_min_confidence(self):
        """最低置信度计算。"""
        sc = SpellConfidence(
            spell_id="fireball",
            field_confidences={"damage": 0.95, "save_ability": 1.0, "effect_type": 0.7},
        )
        assert sc.min_confidence == 0.7

    def test_avg_confidence(self):
        """平均置信度计算。"""
        sc = SpellConfidence(
            spell_id="fireball",
            field_confidences={"damage": 0.8, "save_ability": 1.0},
        )
        assert sc.avg_confidence == 0.9

    def test_is_publishable_reviewed(self):
        """已审校的法术可发布。"""
        sc = SpellConfidence(
            spell_id="fireball",
            field_confidences={"damage": 0.5},
            reviewed=True,
        )
        assert sc.is_publishable is True

    def test_is_publishable_high_confidence(self):
        """高置信度法术可发布。"""
        sc = SpellConfidence(
            spell_id="fireball",
            field_confidences={"damage": 0.95, "save_ability": 1.0},
        )
        assert sc.is_publishable is True

    def test_not_publishable_low_confidence(self):
        """低置信度未审校法术不可发布。"""
        sc = SpellConfidence(
            spell_id="fireball",
            field_confidences={"damage": 0.5, "effect_type": 0.6},
        )
        assert sc.is_publishable is False

    def test_empty_confidences_not_publishable(self):
        """无置信度数据且未审校不可发布。"""
        sc = SpellConfidence(spell_id="fireball")
        assert sc.is_publishable is False
        assert sc.min_confidence == 0.0

    def test_get_low_confidence_fields(self):
        """获取低置信度字段列表。"""
        sc = SpellConfidence(
            spell_id="fireball",
            field_confidences={"damage": 0.95, "effect_type": 0.6, "range": 0.7},
        )
        low = sc.get_low_confidence_fields(0.8)
        assert "effect_type" in low
        assert "range" in low
        assert "damage" not in low

    def test_mark_reviewed(self):
        """标记为已审校。"""
        sc = SpellConfidence(
            spell_id="fireball",
            field_confidences={"damage": 0.5},
        )
        assert sc.is_publishable is False
        sc.mark_reviewed("reviewer_1")
        assert sc.reviewed is True
        assert sc.reviewer == "reviewer_1"
        assert sc.is_publishable is True

    def test_update_field_confidence(self):
        """更新字段置信度。"""
        sc = SpellConfidence(
            spell_id="fireball",
            field_confidences={"damage": 0.5},
        )
        sc.update_field_confidence("damage", 0.95)
        assert sc.field_confidences["damage"] == 0.95


class TestSpellConfidenceRegistry:
    """DATA-001 法术置信度注册表测试。"""

    def test_register_and_get(self):
        """注册并获取置信度。"""
        registry = SpellConfidenceRegistry()
        registry.register("fireball", {"damage": 0.95, "save_ability": 1.0})
        sc = registry.get("fireball")
        assert sc is not None
        assert sc.field_confidences["damage"] == 0.95

    def test_is_publishable(self):
        """判断法术是否可发布。"""
        registry = SpellConfidenceRegistry()
        registry.register("fireball", {"damage": 0.95, "save_ability": 1.0})
        registry.register("unstable_spell", {"damage": 0.5, "effect_type": 0.6})
        assert registry.is_publishable("fireball") is True
        assert registry.is_publishable("unstable_spell") is False

    def test_unregistered_spell_is_publishable(self):
        """未注册的法术默认可发布。"""
        registry = SpellConfidenceRegistry()
        assert registry.is_publishable("unknown_spell") is True

    def test_get_unreviewed(self):
        """获取未审校法术列表。"""
        registry = SpellConfidenceRegistry()
        registry.register("fireball", {"damage": 0.95}, reviewed=True)
        registry.register("unstable_spell", {"damage": 0.5})
        unreviewed = registry.get_unreviewed()
        assert "unstable_spell" in unreviewed
        assert "fireball" not in unreviewed

    def test_get_low_confidence_spells(self):
        """获取低置信度法术列表。"""
        registry = SpellConfidenceRegistry()
        registry.register("fireball", {"damage": 0.95})
        registry.register("unstable_spell", {"damage": 0.5, "effect_type": 0.6})
        low = registry.get_low_confidence_spells(0.8)
        assert "unstable_spell" in low
        assert "fireball" not in low

    def test_mark_reviewed(self):
        """标记法术为已审校。"""
        registry = SpellConfidenceRegistry()
        registry.register("fireball", {"damage": 0.5})
        assert registry.is_publishable("fireball") is False
        registry.mark_reviewed("fireball", "reviewer_1")
        assert registry.is_publishable("fireball") is True

    def test_count(self):
        """注册表法术数量。"""
        registry = SpellConfidenceRegistry()
        registry.register("fireball", {"damage": 0.95})
        registry.register("unstable_spell", {"damage": 0.5})
        assert registry.count() == 2

    def test_count_publishable(self):
        """可发布法术数量。"""
        registry = SpellConfidenceRegistry()
        registry.register("fireball", {"damage": 0.95})
        registry.register("unstable_spell", {"damage": 0.5})
        assert registry.count_publishable() == 1

    def test_update_existing_registration(self):
        """更新已有注册的置信度。"""
        registry = SpellConfidenceRegistry()
        registry.register("fireball", {"damage": 0.5})
        registry.register("fireball", {"damage": 0.95, "effect_type": 0.9})
        sc = registry.get("fireball")
        assert sc.field_confidences["damage"] == 0.95
        assert sc.field_confidences["effect_type"] == 0.9
        assert registry.count() == 1
