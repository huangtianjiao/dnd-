"""Wave 3 战斗基础设施测试 — battle_map / visibility / weapon_rules / equipment_slots。"""

import pytest


# ── BattleMap ─────────────────────────────────────────────────────────

class TestBattleMap:
    def test_create_default(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap()
        assert bm.width == 50
        assert bm.height == 50
        assert bm.grid_size_ft == 5.0

    def test_get_cell_auto_create(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap()
        cell = bm.get_cell(3, 4)
        assert cell.x == 3
        assert cell.y == 4
        assert cell.terrain_cost == 1.0

    def test_is_valid_position(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap(width=10, height=10)
        assert bm.is_valid_position(0, 0)
        assert bm.is_valid_position(9, 9)
        assert not bm.is_valid_position(10, 0)
        assert not bm.is_valid_position(-1, 0)

    def test_distance_ft(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap()
        # 直线 3 格 = 15 尺
        assert bm.get_distance_ft((0, 0), (3, 0)) == 15.0
        # 对角 3 格 = 15 尺（切比雪夫）
        assert bm.get_distance_ft((0, 0), (3, 3)) == 15.0

    def test_distance_grid(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap()
        assert bm.get_distance_grid((0, 0), (3, 4)) == 4

    def test_find_path_simple(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap()
        path = bm.find_path((0, 0), (3, 0), speed_ft=30)
        assert len(path) > 0
        assert path[0] == (0, 0)
        assert path[-1] == (3, 0)

    def test_find_path_blocked_by_speed(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap()
        # 速度只有 5 尺（1 格），无法到达 5 格远
        path = bm.find_path((0, 0), (5, 0), speed_ft=5)
        assert path == []

    def test_move_entity(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap()
        bm.get_cell(0, 0).occupant_id = "e1"
        bm.get_cell(0, 0).is_occupied = True
        assert bm.move_entity("e1", (0, 0), (1, 0))
        assert bm.get_cell(0, 0).occupant_id is None
        assert bm.get_cell(1, 0).occupant_id == "e1"

    def test_move_entity_occupied_target(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap()
        bm.get_cell(0, 0).occupant_id = "e1"
        bm.get_cell(0, 0).is_occupied = True
        bm.get_cell(1, 0).occupant_id = "e2"
        bm.get_cell(1, 0).is_occupied = True
        assert not bm.move_entity("e1", (0, 0), (1, 0))

    def test_line_of_sight_clear(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap()
        assert bm.line_of_sight((0, 0), (5, 0))

    def test_line_of_sight_blocked(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap()
        bm.get_cell(3, 0).provides_cover = True
        assert not bm.line_of_sight((0, 0), (6, 0))

    def test_get_cover_level_none(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap()
        assert bm.get_cover_level((0, 0), (5, 0)) == "none"

    def test_get_cover_level_full(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap()
        bm.get_cell(3, 0).provides_cover = True
        assert bm.get_cover_level((0, 0), (6, 0)) == "full"

    def test_get_creatures_in_reach(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap()
        bm.get_cell(0, 0).occupant_id = "attacker"
        bm.get_cell(0, 0).is_occupied = True
        bm.get_cell(1, 0).occupant_id = "target"
        bm.get_cell(1, 0).is_occupied = True
        results = bm.get_creatures_in_reach("attacker", reach_ft=5)
        assert "target" in results

    def test_get_creatures_in_area(self):
        from aidm.engine.battle_map import BattleMap
        bm = BattleMap()
        bm.get_cell(2, 2).occupant_id = "t1"
        bm.get_cell(2, 2).is_occupied = True
        bm.get_cell(10, 10).occupant_id = "t2"
        bm.get_cell(10, 10).is_occupied = True
        results = bm.get_creatures_in_area((2, 2), shape="circle", size=10)
        assert "t1" in results
        assert "t2" not in results


# ── VisibilityService ────────────────────────────────────────────────

class TestVisibilityService:
    def test_visible_in_bright_light(self):
        from aidm.engine.visibility import VisibilityLevel, VisibilityService
        svc = VisibilityService()
        observer = {"position": (0, 0), "senses": {"darkvision_ft": 0}}
        target = {"position": (3, 0), "light_level": "bright"}
        result = svc.check_visibility(observer, target)
        assert result.level == VisibilityLevel.VISIBLE

    def test_concealed_in_dim_light(self):
        from aidm.engine.visibility import VisibilityLevel, VisibilityService
        svc = VisibilityService()
        observer = {"position": (0, 0), "senses": {"darkvision_ft": 0}}
        target = {"position": (3, 0), "light_level": "dim"}
        result = svc.check_visibility(observer, target)
        assert result.level == VisibilityLevel.CONCEALED

    def test_hidden_in_darkness(self):
        from aidm.engine.visibility import VisibilityLevel, VisibilityService
        svc = VisibilityService()
        observer = {"position": (0, 0), "senses": {"darkvision_ft": 0}}
        target = {"position": (3, 0), "light_level": "darkness"}
        result = svc.check_visibility(observer, target)
        assert result.level == VisibilityLevel.HIDDEN

    def test_blinded_observer(self):
        from aidm.engine.visibility import VisibilityLevel, VisibilityService
        svc = VisibilityService()
        observer = {"position": (0, 0), "senses": {}, "conditions": ["blinded"]}
        target = {"position": (3, 0), "light_level": "bright"}
        result = svc.check_visibility(observer, target, conditions=["blinded"])
        assert result.level == VisibilityLevel.HIDDEN

    def test_cover_level(self):
        from aidm.engine.battle_map import BattleMap
        from aidm.engine.visibility import CoverLevel, VisibilityService
        svc = VisibilityService()
        bm = BattleMap()
        observer = {"position": (0, 0)}
        target = {"position": (5, 0)}
        cover = svc.check_cover(observer, target, battle_map=bm)
        assert cover == CoverLevel.NONE

    def test_line_of_sight_with_map(self):
        from aidm.engine.battle_map import BattleMap
        from aidm.engine.visibility import VisibilityService
        svc = VisibilityService()
        bm = BattleMap()
        bm.get_cell(3, 0).provides_cover = True
        observer = {"position": (0, 0)}
        target = {"position": (6, 0)}
        assert not svc.check_line_of_sight(observer, target, battle_map=bm)

    def test_line_of_effect_with_map(self):
        from aidm.engine.battle_map import BattleMap
        from aidm.engine.visibility import VisibilityService
        svc = VisibilityService()
        bm = BattleMap()
        observer = {"position": (0, 0)}
        target = {"position": (5, 0)}
        assert svc.check_line_of_effect(observer, target, battle_map=bm)


# ── WeaponRuleHandler ────────────────────────────────────────────────

class TestWeaponRuleHandler:
    def setup_method(self):
        from aidm.engine.weapon_rules import WeaponRuleContext, WeaponRuleHandler
        self.handler = WeaponRuleHandler()
        self.ctx = WeaponRuleContext(attacker_str=16, attacker_dex=14)

    def test_ammunition_has_ammo(self):
        result = self.handler.ammunition(self.ctx, ammo_count=10)
        assert result.allowed
        assert result.ammo_consumed

    def test_ammunition_no_ammo(self):
        result = self.handler.ammunition(self.ctx, ammo_count=0)
        assert not result.allowed

    def test_finesse_choose_dex(self):
        result = self.handler.finesse(self.ctx, chosen_ability="dex")
        assert result.ability_used == "dex"
        assert result.attack_modifier == 2  # DEX 14 → +2

    def test_finesse_choose_str(self):
        result = self.handler.finesse(self.ctx, chosen_ability="str")
        assert result.ability_used == "str"
        assert result.attack_modifier == 3  # STR 16 → +3

    def test_finesse_invalid_ability(self):
        result = self.handler.finesse(self.ctx, chosen_ability="con")
        assert not result.allowed

    def test_heavy_small_creature(self):
        from aidm.engine.weapon_rules import WeaponRuleContext
        ctx = WeaponRuleContext(attacker_str=16, attacker_size="Small")
        result = self.handler.heavy(ctx)
        assert result.has_disadvantage

    def test_heavy_low_str(self):
        from aidm.engine.weapon_rules import WeaponRuleContext
        ctx = WeaponRuleContext(attacker_str=10, weapon_str_required=15)
        result = self.handler.heavy(ctx)
        assert result.has_disadvantage

    def test_heavy_ok(self):
        result = self.handler.heavy(self.ctx)
        assert not result.has_disadvantage

    def test_light(self):
        result = self.handler.light(self.ctx)
        assert result.allowed

    def test_loading_first_shot(self):
        result = self.handler.loading(self.ctx, used_this_action=False)
        assert result.allowed

    def test_loading_second_shot(self):
        result = self.handler.loading(self.ctx, used_this_action=True)
        assert not result.allowed

    def test_range_normal(self):
        from aidm.engine.weapon_rules import WeaponRuleContext
        ctx = WeaponRuleContext(target_distance_ft=60)
        result = self.handler.range(ctx, normal_range=80, long_range=320)
        assert result.allowed
        assert not result.has_disadvantage

    def test_range_long_disadvantage(self):
        from aidm.engine.weapon_rules import WeaponRuleContext
        ctx = WeaponRuleContext(target_distance_ft=200)
        result = self.handler.range(ctx, normal_range=80, long_range=320)
        assert result.allowed
        assert result.has_disadvantage

    def test_range_beyond_max(self):
        from aidm.engine.weapon_rules import WeaponRuleContext
        ctx = WeaponRuleContext(target_distance_ft=400)
        result = self.handler.range(ctx, normal_range=80, long_range=320)
        assert not result.allowed

    def test_reach(self):
        from aidm.engine.weapon_rules import WeaponRuleContext
        ctx = WeaponRuleContext(target_distance_ft=10)
        result = self.handler.reach(ctx, base_reach=5)
        assert result.allowed  # 5 + 5 = 10

    def test_reach_too_far(self):
        from aidm.engine.weapon_rules import WeaponRuleContext
        ctx = WeaponRuleContext(target_distance_ft=15)
        result = self.handler.reach(ctx, base_reach=5)
        assert not result.allowed

    def test_thrown(self):
        result = self.handler.thrown(self.ctx, is_melee=True)
        assert result.ability_used == "str"
        assert result.attack_modifier == 3  # STR 16 → +3

    def test_two_handed_ok(self):
        result = self.handler.two_handed(self.ctx, hands_available=2)
        assert result.allowed

    def test_two_handed_one_hand(self):
        result = self.handler.two_handed(self.ctx, hands_available=1)
        assert not result.allowed

    def test_versatile_one_handed(self):
        result = self.handler.versatile(self.ctx, mode="one_handed")
        assert result.allowed

    def test_versatile_two_handed(self):
        result = self.handler.versatile(self.ctx, mode="two_handed")
        assert result.allowed

    def test_versatile_invalid_mode(self):
        result = self.handler.versatile(self.ctx, mode="invalid")
        assert not result.allowed

    def test_validate_attack_finesse_light(self):
        result = self.handler.validate_attack(
            ["finesse", "light"], self.ctx, chosen_ability="dex"
        )
        assert result.allowed
        assert result.ability_used == "dex"

    def test_validate_attack_heavy_small(self):
        from aidm.engine.weapon_rules import WeaponRuleContext
        ctx = WeaponRuleContext(attacker_str=16, attacker_dex=14, attacker_size="Small")
        result = self.handler.validate_attack(["heavy"], ctx)
        assert result.has_disadvantage

    def test_validate_attack_default_str(self):
        result = self.handler.validate_attack(["light"], self.ctx)
        assert result.ability_used == "str"


# ── EquipmentSlotsManager ────────────────────────────────────────────

class TestEquipmentSlotsManager:
    def _make_weapon(self, item_id: str, two_handed: bool = False) -> "ItemInstance":
        from aidm.engine.equipment_slots import ItemInstance
        props = {"is_weapon": True}
        if two_handed:
            props["weapon_properties"] = ["two_handed"]
        return ItemInstance(item_id=item_id, name=item_id, properties=props)

    def _make_shield(self) -> "ItemInstance":
        from aidm.engine.equipment_slots import ItemInstance
        return ItemInstance(item_id="shield", name="Shield", properties={"is_shield": True})

    def _make_focus(self) -> "ItemInstance":
        from aidm.engine.equipment_slots import ItemInstance
        return ItemInstance(item_id="focus", name="Arcane Focus", properties={"is_focus": True})

    def test_equip_main_hand(self):
        from aidm.engine.equipment_slots import EquipmentSlotsManager, SlotType
        mgr = EquipmentSlotsManager()
        sword = self._make_weapon("sword")
        assert mgr.equip(sword, SlotType.MAIN_HAND)
        assert mgr.main_hand is sword

    def test_equip_main_hand_occupied(self):
        from aidm.engine.equipment_slots import EquipmentSlotsManager, SlotType
        mgr = EquipmentSlotsManager()
        sword = self._make_weapon("sword")
        axe = self._make_weapon("axe")
        mgr.equip(sword, SlotType.MAIN_HAND)
        assert not mgr.equip(axe, SlotType.MAIN_HAND)

    def test_two_handed_blocks_off_hand(self):
        from aidm.engine.equipment_slots import EquipmentSlotsManager, SlotType
        mgr = EquipmentSlotsManager()
        greatsword = self._make_weapon("greatsword", two_handed=True)
        shield = self._make_shield()
        mgr.equip(greatsword, SlotType.MAIN_HAND)
        assert not mgr.equip(shield, SlotType.OFF_HAND)

    def test_unequip(self):
        from aidm.engine.equipment_slots import EquipmentSlotsManager, SlotType
        mgr = EquipmentSlotsManager()
        sword = self._make_weapon("sword")
        mgr.equip(sword, SlotType.MAIN_HAND)
        removed = mgr.unequip(SlotType.MAIN_HAND)
        assert removed is sword
        assert mgr.main_hand is None

    def test_get_free_hands_empty(self):
        from aidm.engine.equipment_slots import EquipmentSlotsManager
        mgr = EquipmentSlotsManager()
        assert mgr.get_free_hands() == 2

    def test_get_free_hands_one_weapon(self):
        from aidm.engine.equipment_slots import EquipmentSlotsManager, SlotType
        mgr = EquipmentSlotsManager()
        mgr.equip(self._make_weapon("sword"), SlotType.MAIN_HAND)
        assert mgr.get_free_hands() == 1

    def test_get_free_hands_two_handed(self):
        from aidm.engine.equipment_slots import EquipmentSlotsManager, SlotType
        mgr = EquipmentSlotsManager()
        mgr.equip(self._make_weapon("gs", two_handed=True), SlotType.MAIN_HAND)
        assert mgr.get_free_hands() == 0

    def test_is_shield_equipped(self):
        from aidm.engine.equipment_slots import EquipmentSlotsManager, SlotType
        mgr = EquipmentSlotsManager()
        assert not mgr.is_shield_equipped()
        mgr.equip(self._make_shield(), SlotType.OFF_HAND)
        assert mgr.is_shield_equipped()

    def test_get_weapon_in_hand(self):
        from aidm.engine.equipment_slots import EquipmentSlotsManager, SlotType
        mgr = EquipmentSlotsManager()
        sword = self._make_weapon("sword")
        mgr.equip(sword, SlotType.MAIN_HAND)
        assert mgr.get_weapon_in_hand("main") is sword
        assert mgr.get_weapon_in_hand("off") is None

    def test_has_focus_available(self):
        from aidm.engine.equipment_slots import EquipmentSlotsManager, SlotType
        mgr = EquipmentSlotsManager()
        assert not mgr.has_focus_available()
        mgr.equip(self._make_focus(), SlotType.FOCUS)
        assert mgr.has_focus_available()

    def test_can_cast_with_components_v_only(self):
        from aidm.engine.equipment_slots import EquipmentSlotsManager
        mgr = EquipmentSlotsManager()
        assert mgr.can_cast_with_components(has_v=True, has_s=False, has_m=False)

    def test_can_cast_with_s_no_free_hand(self):
        from aidm.engine.equipment_slots import EquipmentSlotsManager, SlotType
        mgr = EquipmentSlotsManager()
        mgr.equip(self._make_weapon("sword"), SlotType.MAIN_HAND)
        mgr.equip(self._make_shield(), SlotType.OFF_HAND)
        # 0 空闲手，需要 S 成分
        assert not mgr.can_cast_with_components(has_v=True, has_s=True, has_m=False)

    def test_can_cast_with_focus_for_m(self):
        from aidm.engine.equipment_slots import EquipmentSlotsManager, SlotType
        mgr = EquipmentSlotsManager()
        mgr.equip(self._make_focus(), SlotType.FOCUS)
        mgr.equip(self._make_shield(), SlotType.OFF_HAND)
        # 有法器，可以满足 M 成分
        assert mgr.can_cast_with_components(has_v=True, has_s=False, has_m=True)

    def test_worn_slot(self):
        from aidm.engine.equipment_slots import EquipmentSlotsManager, ItemInstance, SlotType
        mgr = EquipmentSlotsManager()
        cloak = ItemInstance(item_id="cloak", name="Cloak of Protection")
        assert mgr.equip(cloak, SlotType.WORN)
        assert len(mgr.worn) == 1
        removed = mgr.unequip(SlotType.WORN)
        assert removed is cloak
        assert len(mgr.worn) == 0


# ── 导入测试 ──────────────────────────────────────────────────────────

class TestImports:
    def test_engine_init_exports(self):
        from aidm.engine import (
            BattleMap,
            CoverLevel,
            EquipmentSlotsManager,
            GridCell,
            ItemInstance,
            SlotType,
            VisibilityLevel,
            VisibilityResult,
            VisibilityService,
            WeaponRuleContext,
            WeaponRuleHandler,
            WeaponRuleResult,
        )
        # 确保所有类可导入
        assert BattleMap is not None
        assert CoverLevel is not None
        assert EquipmentSlotsManager is not None
        assert VisibilityService is not None
        assert WeaponRuleHandler is not None
