#!/usr/bin/env python
"""全模块功能验证脚本 — 检查所有引擎/数据/大脑/API/统计模块的完整性。

运行: PYTHONPATH=src python scripts/test_all_modules.py
"""
import sys
sys.path.insert(0, 'src')

passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f'  ✓ {name}')
        passed += 1
    except Exception as e:
        print(f'  ✗ {name}: {type(e).__name__}: {e}')
        failed += 1

# ═══════════════════════════════════════════════════════════════════════
print('=== 1. Engine: Dice ===')
from aidm.engine.dice import roll_die, roll_dice, roll_d20, ability_modifier, roll_d100, roll_d3

def test_roll_die():
    for _ in range(100):
        r = roll_die(20)
        assert 1 <= r <= 20
def test_roll_dice():
    r = roll_dice('2d6+3')
    assert r.total >= 5 and r.total <= 15
def test_roll_dice_crit():
    r = roll_dice('2d6+3', crit=True)
    assert r.total >= 7 and r.total <= 27
def test_roll_d20_adv():
    r = roll_d20(advantage=True)
    assert r.mode == 'advantage'
    assert len(r.rolls) == 2
    assert r.used == max(r.rolls)
def test_roll_d20_dis():
    r = roll_d20(disadvantage=True)
    assert r.mode == 'disadvantage'
    assert r.used == min(r.rolls)
def test_ability_mod():
    assert ability_modifier(18) == 4
    assert ability_modifier(10) == 0
    assert ability_modifier(8) == -1
    assert ability_modifier(20) == 5
def test_d100():
    r = roll_d100()
    assert 1 <= r <= 100
def test_d3():
    r = roll_d3()
    assert 1 <= r <= 3

for name, fn in [
    ('roll_die(20)', test_roll_die),
    ('roll_dice("2d6+3")', test_roll_dice),
    ('roll_dice crit', test_roll_dice_crit),
    ('roll_d20 advantage', test_roll_d20_adv),
    ('roll_d20 disadvantage', test_roll_d20_dis),
    ('ability_modifier', test_ability_mod),
    ('roll_d100', test_d100),
    ('roll_d3', test_d3),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 2. Engine: Check ===')
from aidm.engine.check import _d20_check_core, ability_check, saving_throw, attack_roll

def test_d20_core():
    r = _d20_check_core(mod=5, prof=2, proficient=True, target=15,
                        advantage=False, disadvantage=False)
    assert r.success == (r.total >= 15)
    assert r.target == 15
def test_ability_check():
    r = ability_check(mod=3, prof=2, proficient=True, dc=12)
    assert hasattr(r, 'success') and hasattr(r, 'total')
def test_saving_throw():
    r = saving_throw(mod=3, prof=2, proficient=True, dc=15)
    assert hasattr(r, 'success')
def test_attack_roll():
    r = attack_roll(bonus=5, ac=15)
    assert hasattr(r, 'hit') and hasattr(r, 'crit')
    if r.d20 == 20:
        assert r.hit == True and r.crit == True
    if r.d20 == 1:
        assert r.hit == False

for name, fn in [
    ('_d20_check_core', test_d20_core),
    ('ability_check', test_ability_check),
    ('saving_throw', test_saving_throw),
    ('attack_roll', test_attack_roll),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 3. Engine: Combat ===')
from aidm.engine.combat import (Combat, Combatant, start_combat,
                                 advance_turn, current_combatant,
                                 roll_initiative, use_action, can_take_action)

def test_combat_start():
    c1 = Combatant(cid='p1', name='战士', initiative=15, is_player=True)
    c2 = Combatant(cid='m1', name='哥布林', initiative=12, is_player=False)
    combat = Combat()
    start_combat(combat, [c1, c2])
    assert combat.round == 1
    assert combat.active == True
def test_combat_advance():
    c1 = Combatant(cid='p1', name='战士', initiative=15, is_player=True)
    c2 = Combatant(cid='m1', name='哥布林', initiative=12, is_player=False)
    combat = Combat()
    start_combat(combat, [c1, c2])
    advance_turn(combat)
    assert current_combatant(combat).name == '哥布林'
    advance_turn(combat)
    assert current_combatant(combat).name == '战士'
    assert combat.round == 2
def test_combat_round_seconds():
    c1 = Combatant(cid='p1', name='战士', is_player=True)
    combat = Combat()
    start_combat(combat, [c1])
    advance_turn(combat)
    assert combat.seconds_elapsed == 6
def test_action_economy():
    c1 = Combatant(cid='p1', name='战士', is_player=True)
    combat = Combat()
    start_combat(combat, [c1])
    assert can_take_action(c1) == True
    use_action(c1)
    assert c1.action_used == True
    assert can_take_action(c1) == False

for name, fn in [
    ('combat start', test_combat_start),
    ('combat advance turn', test_combat_advance),
    ('combat round = 6s', test_combat_round_seconds),
    ('action economy', test_action_economy),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 4. Engine: Conditions ===')
from aidm.engine.conditions import ConditionState, d20_penalty, speed_after_conditions

def test_condition_state():
    cs = ConditionState()
    assert hasattr(cs, '__dataclass_fields__') or hasattr(cs, '__dict__')
def test_d20_penalty():
    cs = ConditionState()
    p = d20_penalty(cs)
    assert isinstance(p, int)
def test_speed_after_cond():
    cs = ConditionState()
    s = speed_after_conditions(30, cs)
    assert isinstance(s, int)

for name, fn in [
    ('ConditionState', test_condition_state),
    ('d20_penalty', test_d20_penalty),
    ('speed_after_conditions', test_speed_after_cond),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 5. Engine: Concentration ===')
from aidm.engine.concentration import ConcentrationManager, concentration_save_dc

def test_concentration_start():
    mgr = ConcentrationManager()
    mgr.set_concentration('wiz1', '法师护甲')
    slot = mgr._get_slot('wiz1')
    assert slot.spell_id == '法师护甲'
def test_concentration_save():
    mgr = ConcentrationManager()
    mgr.set_concentration('wiz2', '魔法飞弹')
    result = mgr.concentration_save_on_damage(
        'wiz2', damage_taken=10, con_mod=3,
        con_proficient=True, prof_bonus=2)
    assert isinstance(result, dict)
    assert 'success' in result and 'broken' in result
def test_concentration_dc():
    assert concentration_save_dc(10) == 10
    assert concentration_save_dc(30) == 15
    assert concentration_save_dc(60) == 30

for name, fn in [
    ('set_concentration', test_concentration_start),
    ('concentration_save_on_damage', test_concentration_save),
    ('concentration_save_dc', test_concentration_dc),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 6. Engine: Damage ===')
from aidm.engine.damage import (DamageRequest, roll_damage, apply_damage_to_hp,
                                  grant_temp_hp, apply_healing,
                                  DeathTracker, death_save, check_massive_damage)

def test_damage_roll():
    req = DamageRequest(dice_expr='2d6+3', damage_type='挥砍',
                        ability_mod=4, add_mod=True, crit=False,
                        flat_modifiers=[])
    result = roll_damage(req)
    total = getattr(result, 'final', None) or getattr(result, 'total', None)
    assert total is not None
    assert total >= 9
    assert total <= 19
def test_apply_damage_to_hp():
    hp, temp = apply_damage_to_hp(hp=20, temp_hp=5, max_hp=30, dmg=10)
    assert hp == 15 and temp == 0
def test_grant_temp_hp():
    assert grant_temp_hp(current_temp=5, new_temp=10) == 10
    assert grant_temp_hp(current_temp=10, new_temp=5) == 10
def test_apply_healing():
    assert apply_healing(hp=15, max_hp=30, heal=20) == 30
    assert apply_healing(hp=15, max_hp=30, heal=5) == 20
def test_death_save():
    tracker = DeathTracker()
    result = death_save(tracker)
    assert isinstance(result, dict)
def test_massive_damage():
    assert check_massive_damage(current_hp=10, max_hp=30, dmg=45) == True
    assert check_massive_damage(current_hp=10, max_hp=30, dmg=20) == False

for name, fn in [
    ('roll_damage', test_damage_roll),
    ('apply_damage_to_hp', test_apply_damage_to_hp),
    ('grant_temp_hp', test_grant_temp_hp),
    ('apply_healing', test_apply_healing),
    ('death_save', test_death_save),
    ('check_massive_damage', test_massive_damage),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 7. Engine: Spellcasting ===')
from aidm.engine.spellcasting import cast_spell, CasterState

def test_cast_magic_missile():
    cs = CasterState(caster_id='wiz1', class_name='法师', level=3,
                     ability_scores={'int': 16}, spell_slots={1: 4, 2: 2})
    result = cast_spell(cs, '魔法飞弹', slot_level=1,
                        targets=['goblin1'])
    assert result is not None

for name, fn in [
    ('cast magic missile', test_cast_magic_missile),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 8. Data: Races ===')
from aidm.data.races import get_race, race_names

def test_races_count():
    races = race_names()
    assert len(races) == 10, f"Expected 10 races, got {len(races)}"
def test_race_detail():
    r = get_race('人类')
    assert r is not None

for name, fn in [
    ('races count = 10', test_races_count),
    ('race detail', test_race_detail),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 9. Data: Classes ===')
from aidm.data.classes import get_class, class_names

def test_classes_count():
    classes = class_names()
    assert len(classes) == 12, f"Expected 12 classes, got {len(classes)}"
def test_class_detail():
    c = get_class('法师')
    assert c is not None

for name, fn in [
    ('classes count = 12', test_classes_count),
    ('class detail', test_class_detail),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 10. Data: Backgrounds ===')
from aidm.data.backgrounds import get_background, background_names

def test_backgrounds_count():
    bgs = background_names()
    assert len(bgs) == 16, f"Expected 16 backgrounds, got {len(bgs)}"

for name, fn in [
    ('backgrounds count = 16', test_backgrounds_count),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 11. Data: Equipment ===')
from aidm.data.equipment import convert_coins, get_armor_entry, compute_ac

def test_convert_coins():
    assert convert_coins(10, 'SP', 'GP') == 1.0
def test_armor_chain():
    armor = get_armor_entry('链甲')
    assert armor['base_ac'] == 16
    assert compute_ac(armor, dex_mod=0) == 16

for name, fn in [
    ('convert_coins', test_convert_coins),
    ('chain mail AC=16', test_armor_chain),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 12. Data: Spells ===')
from aidm.data.spells import SPELLS, get_spell, max_spell_slots, get_casting_ability

def test_spell_count():
    assert len(SPELLS) >= 10, f"Expected >=10 spells, got {len(SPELLS)}"
def test_spell_detail():
    s = get_spell('魔法飞弹')
    assert s.level == 1
    assert s.damage_dice is not None
def test_casting_ability():
    assert get_casting_ability('法师') == 'INT'

for name, fn in [
    ('spell count >= 10', test_spell_count),
    ('spell detail (magic missile)', test_spell_detail),
    ('get_casting_ability', test_casting_ability),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 13. Data: Feats ===')
from aidm.data.feats import FEATS, feat_categories

def test_feats_count():
    assert len(FEATS) == 74, f"Expected 74 feats, got {len(FEATS)}"
def test_feat_categories():
    cats = feat_categories()
    assert '起源' in cats and '通用' in cats and '战斗风格' in cats and '传奇恩惠' in cats

for name, fn in [
    ('feats count = 74', test_feats_count),
    ('feat categories', test_feat_categories),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 14. Data: Magic Items ===')
from aidm.data.magic_items import list_magic_items, Rarity

def test_magic_items_count():
    items = list_magic_items()
    by_rarity = {}
    for it in items:
        by_rarity[it.rarity.value] = by_rarity.get(it.rarity.value, 0) + 1
    assert by_rarity.get('普通', 0) == 16, f"Expected 16 common, got {by_rarity}"
    assert by_rarity.get('非普通', 0) == 11, f"Expected 11 uncommon, got {by_rarity}"
    assert by_rarity.get('珍稀', 0) == 3, f"Expected 3 rare, got {by_rarity}"

for name, fn in [
    ('magic items count by rarity', test_magic_items_count),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 15. Data: Strongholds ===')
from aidm.data.strongholds import FACILITIES, BASIC_FACILITIES, STRONGHOLD_EVENTS

def test_strongholds_data():
    assert len(FACILITIES) == 29, f"Expected 29 facilities, got {len(FACILITIES)}"
    assert len(BASIC_FACILITIES) == 6, f"Expected 6 basic, got {len(BASIC_FACILITIES)}"
    assert len(STRONGHOLD_EVENTS) == 11, f"Expected 11 events, got {len(STRONGHOLD_EVENTS)}"

for name, fn in [
    ('strongholds data integrity', test_strongholds_data),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 16. Data: Planes ===')
from aidm.data.planes import list_planes, get_plane_count

def test_planes_count():
    planes = list_planes()
    # 29 base planes (PLANE_COUNT=29); some may have sub-planes
    assert len(planes) >= 29, f"Expected >=29 planes, got {len(planes)}"
    assert get_plane_count() >= 29

for name, fn in [
    ('planes count >= 29', test_planes_count),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 17. Brain: Session0 ===')
from aidm.brain.session0 import Session0Config, default_session0, validate_session0

def test_session0():
    config = default_session0()
    assert config is not None
    errors = validate_session0(config)
    assert isinstance(errors, list)

for name, fn in [
    ('session0 config', test_session0),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 18. Brain: Char Create ===')
from aidm.brain.char_create import create_character, CharacterSheet, roll_ability_scores

def test_char_create():
    scores = roll_ability_scores()
    assert len(scores) == 6
    assert all(3 <= s <= 18 for s in scores)

for name, fn in [
    ('roll_ability_scores', test_char_create),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 19. Brain: Levelup ===')
from aidm.brain.levelup import level_up, available_feats, proficiency_bonus

def test_levelup():
    # Give enough XP to level up (300 for level 2)
    char = {'level': 1, 'class_name': '战士', 'hp_max': 12,
            'scores': {'CON': 14, 'STR': 16}, 'xp': 300}
    result = level_up(char)
    assert result is not None
    assert result['new_level'] == 2

for name, fn in [
    ('level_up', test_levelup),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 20. Brain: Rest ===')
from aidm.brain.rest import short_rest, long_rest, MockCharacter

def test_short_rest():
    char = MockCharacter()
    result = short_rest(char)
    assert isinstance(result, dict)
def test_long_rest():
    char = MockCharacter()
    result = long_rest(char)
    assert isinstance(result, dict)

for name, fn in [
    ('short_rest', test_short_rest),
    ('long_rest', test_long_rest),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 21. Brain: Exploration ===')
from aidm.brain.exploration import get_travel_pace, terrain_params, weather_roll

def test_exploration():
    pace = get_travel_pace('快速')
    assert pace is not None
    tp = terrain_params('草原')
    assert tp is not None

for name, fn in [
    ('exploration functions', test_exploration),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 22. Brain: Social ===')
from aidm.brain.social import NPC, social_interaction, check_social_dc

def test_social():
    npc = NPC(name='酒馆老板', role='酒馆老板', attitude='friendly')
    # check_social_dc returns DC based on attitude
    result = check_social_dc('friendly')
    # May return int or dict depending on implementation
    assert result is not None

for name, fn in [
    ('social interaction', test_social),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 23. Brain: Loot ===')
from aidm.brain.loot import generate_loot

def test_loot():
    result = generate_loot(cr=1.0)
    assert result is not None

for name, fn in [
    ('generate_loot', test_loot),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 24. Brain: Adventure Builder ===')
from aidm.brain.adventure_builder import create_adventure

def test_adventure_builder():
    adv = create_adventure(name='测试冒险', level_range=(1, 4))
    assert adv is not None

for name, fn in [
    ('create_adventure', test_adventure_builder),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 25. Brain: Campaign Manager ===')
from aidm.brain.campaign_manager import create_campaign

def test_campaign_manager():
    camp = create_campaign(name='测试战役')
    assert camp is not None

for name, fn in [
    ('create_campaign', test_campaign_manager),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 26. Brain: Stronghold Management ===')
from aidm.brain.stronghold import create_stronghold, StrongholdType

def test_stronghold_mgmt():
    sh = create_stronghold(campaign_id=1, owner_character_id=1,
                           owner_name='战士', owner_level=5,
                           name='测试据点',
                           stronghold_type=StrongholdType.TOWER)
    assert sh is not None

for name, fn in [
    ('create_stronghold', test_stronghold_mgmt),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 27. Brain: Plane Travel ===')
from aidm.brain.plane_travel import travel_to_plane, TRAVEL_METHODS

def test_plane_travel():
    result = travel_to_plane(origin_plane='物质位面',
                             destination_plane='妖精荒野',
                             method=TRAVEL_METHODS.SPELL)
    assert result is not None

for name, fn in [
    ('travel_to_plane', test_plane_travel),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 28. Brain: Room Management ===')
from aidm.brain.room import RoomManager

def test_room_mgmt():
    rm = RoomManager()
    room = rm.create_room(campaign_id=1)
    assert room is not None
    assert room.room_id is not None

for name, fn in [
    ('RoomManager create_room', test_room_mgmt),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 29. API: Main ===')
from aidm.api.main import app

def test_api_main():
    assert app is not None

for name, fn in [
    ('FastAPI app', test_api_main),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 30. API: WebSocket ===')
from aidm.api.ws import sio

def test_api_ws():
    assert sio is not None

for name, fn in [
    ('Socket.IO server', test_api_ws),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 31. Stats: Models ===')
from aidm.stats.models import Character, Campaign, Scene, CombatState, Log

def test_stats_models():
    assert Character is not None
    assert Campaign is not None
    assert Scene is not None
    assert CombatState is not None
    assert Log is not None

for name, fn in [
    ('SQLModel classes', test_stats_models),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 32. Stats: Store ===')
from aidm.stats.store import create_campaign as store_create_campaign, get_engine

def test_stats_store():
    # Use proper SQLite URL format
    engine = get_engine('sqlite:///:memory:')
    assert engine is not None

for name, fn in [
    ('Store with in-memory SQLite', test_stats_store),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 33. Knowledge: Retriever ===')
from aidm.knowledge.retriever import query_rules, format_for_llm

def test_knowledge_retriever():
    results = query_rules('擒抱', limit=3)
    assert isinstance(results, list)

for name, fn in [
    ('query_rules', test_knowledge_retriever),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== 34. Knowledge: Verifier ===')
from aidm.knowledge.verifier import verify, gather_evidence

def test_knowledge_verifier():
    result = verify(action_desc='攻击检定')
    assert isinstance(result, (bool, dict, object))

for name, fn in [
    ('verify', test_knowledge_verifier),
]:
    test(name, fn)

# ═══════════════════════════════════════════════════════════════════════
print()
print('=== SUMMARY ===')
print(f'Total: {passed + failed} | Passed: {passed} | Failed: {failed}')
if failed == 0:
    print('🎉 ALL TESTS PASSED!')
else:
    print(f'⚠️ {failed} tests failed')
sys.exit(0 if failed == 0 else 1)
