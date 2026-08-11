"""74 专长可执行定义 — 将 feats.py 文本数据映射为 FeatureDefinition。

规则依据: PHB 2024 第五章「专长」
每个专长对应一个 FeatureDefinition，核心 20+ 专长有完整 modifiers/resource_pool，
其余用简化 PASSIVE 定义。
"""

from __future__ import annotations

from typing import Dict

from ..rules.feature_dsl import FeatureDefinition, FeatureType

# ──────────────────────────────────────────────────────────────────────────
# 起源专长 (10)
# ──────────────────────────────────────────────────────────────────────────

_FEAT_ALERT = FeatureDefinition(
    feature_id="feat.alert", name="警戒 Alert",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "initiative", "value": "proficiency", "type": "bonus"}],
    granted_actions=["initiative_swap"],
)

_FEAT_CRAFTER = FeatureDefinition(
    feature_id="feat.crafter", name="巧匠 Crafter",
    feature_type=FeatureType.PROFICIENCY,
    granted_proficiencies=["tool_choice_3_crafter"],
    modifiers=[{"field": "purchase_discount", "value": 0.20, "type": "bonus"}],
    granted_actions=["fast_crafting"],
)

_FEAT_HEALER = FeatureDefinition(
    feature_id="feat.healer", name="医疗师 Healer",
    feature_type=FeatureType.ACTION,
    granted_actions=["battle_medic", "healing_rerolls"],
)

_FEAT_LUCKY = FeatureDefinition(
    feature_id="feat.lucky", name="幸运 Lucky",
    feature_type=FeatureType.RESOURCE,
    resource_pool={"name": "luck_points", "max": 2, "recharge": "long_rest",
                   "pool_type": "regen", "resource_type": "general"},
    granted_actions=["lucky_advantage", "lucky_disadvantage"],
)

_FEAT_MAGIC_INITIATE = FeatureDefinition(
    feature_id="feat.magic_initiate", name="魔法学徒 Magic Initiate",
    feature_type=FeatureType.SPELL_GRANT,
    granted_spells=["cantrip_choice_2", "level_1_spell_choice_1"],
)

_FEAT_MUSICIAN = FeatureDefinition(
    feature_id="feat.musician", name="音乐家 Musician",
    feature_type=FeatureType.PROFICIENCY,
    granted_proficiencies=["instrument_choice_3"],
    granted_actions=["encouraging_song"],
)

_FEAT_SAVAGE_ATTACKER = FeatureDefinition(
    feature_id="feat.savage_attacker", name="凶蛮打手 Savage Attacker",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "weapon_damage_reroll", "value": True, "type": "special"}],
)

_FEAT_SKILLED = FeatureDefinition(
    feature_id="feat.skilled", name="熟习 Skilled",
    feature_type=FeatureType.PROFICIENCY,
    granted_proficiencies=["skill_or_tool_choice_3"],
)

_FEAT_TAVERN_BRAWLER = FeatureDefinition(
    feature_id="feat.tavern_brawler", name="酒馆斗殴者 Tavern Brawler",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "unarmed_strike_damage", "value": "1d4", "type": "override"}],
    granted_proficiencies=["improvised_weapons"],
    granted_actions=["improved_unarmed_strike", "push"],
)

_FEAT_TOUGH = FeatureDefinition(
    feature_id="feat.tough", name="健壮 Tough",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "hp_per_level", "value": 2, "type": "bonus"}],
)

# ──────────────────────────────────────────────────────────────────────────
# 通用专长 (43)
# ──────────────────────────────────────────────────────────────────────────

_FEAT_ASI = FeatureDefinition(
    feature_id="feat.asi", name="属性值提升 Ability Score Improvement",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "ability_score", "value": "choice", "type": "bonus"}],
)

_FEAT_ACTOR = FeatureDefinition(
    feature_id="feat.actor", name="演员 Actor",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "cha", "value": 1, "type": "bonus"},
               {"field": "deception_performance_vs_impersonation", "value": "advantage", "type": "advantage"}],
    prerequisites=[{"type": "level", "value": 4}, {"type": "ability", "ability": "cha", "value": 13}],
)

_FEAT_ATHLETE = FeatureDefinition(
    feature_id="feat.athlete", name="运动精英 Athlete",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"},
               {"field": "climb_speed", "value": "walking_speed", "type": "override"},
               {"field": "stand_up_cost", "value": 5, "type": "override"}],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_CHARGER = FeatureDefinition(
    feature_id="feat.charger", name="冲锋手 Charger",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"},
               {"field": "dash_speed_bonus", "value": 10, "type": "bonus"}],
    granted_actions=["charge_attack"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_CHEF = FeatureDefinition(
    feature_id="feat.chef", name="大厨 Chef",
    feature_type=FeatureType.PROFICIENCY,
    granted_proficiencies=["cooks_utensils"],
    granted_actions=["replenishing_meal", "bolstering_treats"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_CROSSBOW_EXPERT = FeatureDefinition(
    feature_id="feat.crossbow_expert", name="强弩专家 Crossbow Expert",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "dex", "value": 1, "type": "bonus"},
               {"field": "crossbow_loading_ignore", "value": True, "type": "special"},
               {"field": "crossbow_melee_no_disadvantage", "value": True, "type": "special"}],
    prerequisites=[{"type": "level", "value": 4}, {"type": "ability", "ability": "dex", "value": 13}],
)

_FEAT_CRUSHER = FeatureDefinition(
    feature_id="feat.crusher", name="粉碎者 Crusher",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_con", "value": 1, "type": "bonus"}],
    granted_actions=["crusher_push", "enhanced_critical_bludgeoning"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_DEFENSIVE_DUELIST = FeatureDefinition(
    feature_id="feat.defensive_duelist", name="防御式决斗 Defensive Duelist",
    feature_type=FeatureType.REACTION,
    modifiers=[{"field": "dex", "value": 1, "type": "bonus"}],
    granted_actions=["parry"],
    prerequisites=[{"type": "level", "value": 4}, {"type": "ability", "ability": "dex", "value": 13}],
)

_FEAT_DUAL_WIELDER = FeatureDefinition(
    feature_id="feat.dual_wielder", name="双持客 Dual Wielder",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"}],
    granted_actions=["enhanced_dual_wielding", "quick_draw"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_DURABLE = FeatureDefinition(
    feature_id="feat.durable", name="耐性 Durable",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "con", "value": 1, "type": "bonus"},
               {"field": "death_save_advantage", "value": True, "type": "advantage"}],
    granted_actions=["speedy_recovery"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_ELEMENTAL_ADEPT = FeatureDefinition(
    feature_id="feat.elemental_adept", name="元素掌控 Elemental Adept",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "int_or_wis_or_cha", "value": 1, "type": "bonus"},
               {"field": "elemental_damage_min", "value": 2, "type": "override"}],
    prerequisites=[{"type": "level", "value": 4}, {"type": "spellcasting_or_pact"}],
)

_FEAT_FEY_TOUCHED = FeatureDefinition(
    feature_id="feat.fey_touched", name="妖精触碰 Fey-Touched",
    feature_type=FeatureType.SPELL_GRANT,
    modifiers=[{"field": "int_or_wis_or_cha", "value": 1, "type": "bonus"}],
    granted_spells=["misty_step", "level_1_divination_or_enchantment_choice"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_GRAPPLER = FeatureDefinition(
    feature_id="feat.grappler", name="擒抱者 Grappler",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"}],
    granted_actions=["punch_and_grab", "attack_grappled_advantage", "fast_wrestler"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_GREAT_WEAPON_MASTER = FeatureDefinition(
    feature_id="feat.great_weapon_master", name="巨武器大师 Great Weapon Master",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str", "value": 1, "type": "bonus"}],
    granted_actions=["heavy_weapon_master", "hew"],
    prerequisites=[{"type": "level", "value": 4}, {"type": "ability", "ability": "str", "value": 13}],
)

_FEAT_HEAVILY_ARMORED = FeatureDefinition(
    feature_id="feat.heavily_armored", name="重甲运用 Heavily Armored",
    feature_type=FeatureType.PROFICIENCY,
    modifiers=[{"field": "str_or_con", "value": 1, "type": "bonus"}],
    granted_proficiencies=["heavy_armor"],
    prerequisites=[{"type": "level", "value": 4}, {"type": "proficiency", "target": "medium_armor"}],
)

_FEAT_HEAVY_ARMOR_MASTER = FeatureDefinition(
    feature_id="feat.heavy_armor_master", name="重甲大师 Heavy Armor Master",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_con", "value": 1, "type": "bonus"},
               {"field": "physical_damage_reduction", "value": "proficiency", "type": "reduction"}],
    prerequisites=[{"type": "level", "value": 4}, {"type": "proficiency", "target": "heavy_armor"}],
)

_FEAT_INSPIRING_LEADER = FeatureDefinition(
    feature_id="feat.inspiring_leader", name="领袖之证 Inspiring Leader",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "wis_or_cha", "value": 1, "type": "bonus"}],
    granted_actions=["bolstering_performance"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_KEEN_MIND = FeatureDefinition(
    feature_id="feat.keen_mind", name="敏锐心灵 Keen Mind",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "int", "value": 1, "type": "bonus"}],
    granted_proficiencies=["knowledge_skill_choice"],
    granted_actions=["quick_study"],
    prerequisites=[{"type": "level", "value": 4}, {"type": "ability", "ability": "int", "value": 13}],
)

_FEAT_LIGHTLY_ARMORED = FeatureDefinition(
    feature_id="feat.lightly_armored", name="轻甲运用 Lightly Armored",
    feature_type=FeatureType.PROFICIENCY,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"}],
    granted_proficiencies=["light_armor", "shields"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_MAGE_SLAYER = FeatureDefinition(
    feature_id="feat.mage_slayer", name="巫师杀手 Mage Slayer",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"}],
    granted_actions=["concentration_breaker", "guarded_mind"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_MARTIAL_WEAPON_TRAINING = FeatureDefinition(
    feature_id="feat.martial_weapon_training", name="军用武器训练 Martial Weapon Training",
    feature_type=FeatureType.PROFICIENCY,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"}],
    granted_proficiencies=["martial_weapons"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_MEDIUM_ARMOR_MASTER = FeatureDefinition(
    feature_id="feat.medium_armor_master", name="中甲大师 Medium Armor Master",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"},
               {"field": "medium_armor_dex_cap", "value": 3, "type": "override"}],
    prerequisites=[{"type": "level", "value": 4}, {"type": "proficiency", "target": "medium_armor"}],
)

_FEAT_MODERATELY_ARMORED = FeatureDefinition(
    feature_id="feat.moderately_armored", name="中甲运用 Moderately Armored",
    feature_type=FeatureType.PROFICIENCY,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"}],
    granted_proficiencies=["medium_armor"],
    prerequisites=[{"type": "level", "value": 4}, {"type": "proficiency", "target": "light_armor"}],
)

_FEAT_MOUNTED_COMBATANT = FeatureDefinition(
    feature_id="feat.mounted_combatant", name="骑乘战斗 Mounted Combatant",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_dex_or_wis", "value": 1, "type": "bonus"}],
    granted_actions=["mounted_strike", "leap_aside", "veer"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_OBSERVANT = FeatureDefinition(
    feature_id="feat.observant", name="观察力 Observant",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "int_or_wis", "value": 1, "type": "bonus"}],
    granted_proficiencies=["keen_observer_skill"],
    granted_actions=["quick_search"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_PIERCER = FeatureDefinition(
    feature_id="feat.piercer", name="穿刺者 Piercer",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"}],
    granted_actions=["puncture", "enhanced_critical_piercing"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_POISONER = FeatureDefinition(
    feature_id="feat.poisoner", name="毒师 Poisoner",
    feature_type=FeatureType.PROFICIENCY,
    modifiers=[{"field": "dex_or_int", "value": 1, "type": "bonus"}],
    granted_proficiencies=["poisoners_kit"],
    granted_actions=["potent_poison", "brew_poison"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_POLEARM_MASTER = FeatureDefinition(
    feature_id="feat.polearm_master", name="长柄武器大师 Polearm Master",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"}],
    granted_actions=["pole_strike", "reactive_strike"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_RESILIENT = FeatureDefinition(
    feature_id="feat.resilient", name="强健身心 Resilient",
    feature_type=FeatureType.PROFICIENCY,
    modifiers=[{"field": "ability_choice", "value": 1, "type": "bonus"}],
    granted_proficiencies=["saving_throw_choice"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_RITUAL_CASTER = FeatureDefinition(
    feature_id="feat.ritual_caster", name="仪式施法者 Ritual Caster",
    feature_type=FeatureType.SPELL_GRANT,
    modifiers=[{"field": "int_or_wis_or_cha", "value": 1, "type": "bonus"}],
    granted_spells=["ritual_spells_choice"],
    granted_actions=["quick_ritual"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_SENTINEL = FeatureDefinition(
    feature_id="feat.sentinel", name="哨兵 Sentinel",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"}],
    granted_actions=["guardian", "halt"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_SHADOW_TOUCHED = FeatureDefinition(
    feature_id="feat.shadow_touched", name="影界触碰 Shadow-Touched",
    feature_type=FeatureType.SPELL_GRANT,
    modifiers=[{"field": "int_or_wis_or_cha", "value": 1, "type": "bonus"}],
    granted_spells=["invisibility", "level_1_illusion_or_necromancy_choice"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_SHARPSHOOTER = FeatureDefinition(
    feature_id="feat.sharpshooter", name="神射手 Sharpshooter",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "dex", "value": 1, "type": "bonus"},
               {"field": "ranged_cover_ignore", "value": True, "type": "special"},
               {"field": "ranged_melee_no_disadvantage", "value": True, "type": "special"},
               {"field": "ranged_no_long_range_disadvantage", "value": True, "type": "special"}],
    prerequisites=[{"type": "level", "value": 4}, {"type": "ability", "ability": "dex", "value": 13}],
)

_FEAT_SHIELD_MASTER = FeatureDefinition(
    feature_id="feat.shield_master", name="盾牌大师 Shield Master",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str", "value": 1, "type": "bonus"}],
    granted_actions=["shield_bash", "interpose_shield"],
    prerequisites=[{"type": "level", "value": 4}, {"type": "proficiency", "target": "shields"}],
)

_FEAT_SKILL_EXPERT = FeatureDefinition(
    feature_id="feat.skill_expert", name="技艺专家 Skill Expert",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "ability_choice", "value": 1, "type": "bonus"}],
    granted_proficiencies=["skill_choice_1"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_SKULKER = FeatureDefinition(
    feature_id="feat.skulker", name="隐伏者 Skulker",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "dex", "value": 1, "type": "bonus"},
               {"field": "blindsight", "value": 10, "type": "grant"}],
    prerequisites=[{"type": "level", "value": 4}, {"type": "ability", "ability": "dex", "value": 13}],
)

_FEAT_SLASHER = FeatureDefinition(
    feature_id="feat.slasher", name="劈砍者 Slasher",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"}],
    granted_actions=["hamstring", "enhanced_critical_slashing"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_SPEEDY = FeatureDefinition(
    feature_id="feat.speedy", name="飙速跑者 Speedy",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "dex_or_con", "value": 1, "type": "bonus"},
               {"field": "speed", "value": 10, "type": "bonus"},
               {"field": "opportunity_attacks_against", "value": "disadvantage", "type": "special"}],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_SPELL_SNIPER = FeatureDefinition(
    feature_id="feat.spell_sniper", name="法术射手 Spell Sniper",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "int_or_wis_or_cha", "value": 1, "type": "bonus"},
               {"field": "spell_cover_ignore", "value": True, "type": "special"},
               {"field": "spell_range_bonus", "value": 60, "type": "bonus"}],
    prerequisites=[{"type": "level", "value": 4}, {"type": "spellcasting_or_pact"}],
)

_FEAT_TELEKINETIC = FeatureDefinition(
    feature_id="feat.telekinetic", name="念动力 Telekinetic",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "int_or_wis_or_cha", "value": 1, "type": "bonus"}],
    granted_spells=["mage_hand_enhanced"],
    granted_actions=["telekinetic_shove"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_TELEPATHIC = FeatureDefinition(
    feature_id="feat.telepathic", name="心灵感应 Telepathic",
    feature_type=FeatureType.SPELL_GRANT,
    modifiers=[{"field": "int_or_wis_or_cha", "value": 1, "type": "bonus"}],
    granted_spells=["detect_thoughts"],
    granted_actions=["telepathic_utterance"],
    prerequisites=[{"type": "level", "value": 4}],
)

_FEAT_WAR_CASTER = FeatureDefinition(
    feature_id="feat.war_caster", name="战地施法者 War Caster",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "int_or_wis_or_cha", "value": 1, "type": "bonus"},
               {"field": "concentration_save_advantage", "value": True, "type": "advantage"},
               {"field": "somatic_components_with_weapons", "value": True, "type": "special"}],
    granted_actions=["reactive_spell"],
    prerequisites=[{"type": "level", "value": 4}, {"type": "spellcasting_or_pact"}],
)

_FEAT_WEAPON_MASTER = FeatureDefinition(
    feature_id="feat.weapon_master", name="武器大师 Weapon Master",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"}],
    granted_actions=["mastery_property_choice"],
    prerequisites=[{"type": "level", "value": 4}],
)

# ──────────────────────────────────────────────────────────────────────────
# 战斗风格专长 (9) — 先决: 战斗风格特性
# ──────────────────────────────────────────────────────────────────────────

_FEAT_ARCHERY = FeatureDefinition(
    feature_id="feat.archery", name="箭术 Archery",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "ranged_attack_bonus", "value": 2, "type": "bonus"}],
    prerequisites=[{"type": "fighting_style_feature"}],
)

_FEAT_BLIND_FIGHTING = FeatureDefinition(
    feature_id="feat.blind_fighting", name="盲斗 Blind Fighting",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "blindsight", "value": 10, "type": "grant"}],
    prerequisites=[{"type": "fighting_style_feature"}],
)

_FEAT_DEFENSE = FeatureDefinition(
    feature_id="feat.defense", name="防御 Defense",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "ac_armor_bonus", "value": 1, "type": "bonus"}],
    prerequisites=[{"type": "fighting_style_feature"}],
)

_FEAT_DUELING = FeatureDefinition(
    feature_id="feat.dueling", name="对决 Dueling",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "one_handed_weapon_damage", "value": 2, "type": "bonus"}],
    prerequisites=[{"type": "fighting_style_feature"}],
)

_FEAT_GREAT_WEAPON_FIGHTING = FeatureDefinition(
    feature_id="feat.great_weapon_fighting", name="巨武器战斗 Great Weapon Fighting",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "two_handed_damage_min", "value": 3, "type": "override"}],
    prerequisites=[{"type": "fighting_style_feature"}],
)

_FEAT_INTERCEPTION = FeatureDefinition(
    feature_id="feat.interception", name="拦截 Interception",
    feature_type=FeatureType.REACTION,
    granted_actions=["interception_reaction"],
    prerequisites=[{"type": "fighting_style_feature"}],
)

_FEAT_PROTECTION = FeatureDefinition(
    feature_id="feat.protection", name="守护 Protection",
    feature_type=FeatureType.REACTION,
    granted_actions=["protection_reaction"],
    prerequisites=[{"type": "fighting_style_feature"}],
)

_FEAT_THROWN_WEAPON_FIGHTING = FeatureDefinition(
    feature_id="feat.thrown_weapon_fighting", name="投掷武器战斗 Thrown Weapon Fighting",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "thrown_weapon_damage", "value": 2, "type": "bonus"}],
    prerequisites=[{"type": "fighting_style_feature"}],
)

_FEAT_TWO_WEAPON_FIGHTING = FeatureDefinition(
    feature_id="feat.two_weapon_fighting", name="双武器战斗 Two-Weapon Fighting",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "off_hand_add_ability_mod", "value": True, "type": "special"}],
    prerequisites=[{"type": "fighting_style_feature"}],
)

# ──────────────────────────────────────────────────────────────────────────
# 传奇恩惠专长 (12) — 先决: 等级 19+
# ──────────────────────────────────────────────────────────────────────────

_BOON_PREREQ = [{"type": "level", "value": 19}]


def _boon(fid: str, name: str, **kwargs) -> FeatureDefinition:
    """快捷创建传奇恩惠"""
    return FeatureDefinition(feature_id=fid, name=name, prerequisites=list(_BOON_PREREQ), **kwargs)


_FEAT_BOON_COMBAT_PROWESS = _boon(
    "feat.boon_combat_prowess", "英勇战斗之恩惠 Boon of Combat Prowess",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "ability_choice", "value": 1, "type": "bonus"}],
    granted_actions=["peerless_aim"],
)

_FEAT_BOON_DIMENSIONAL_TRAVEL = _boon(
    "feat.boon_dimensional_travel", "次元旅行之恩惠 Boon of Dimensional Travel",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "ability_choice", "value": 1, "type": "bonus"}],
    granted_actions=["blink_steps"],
)

_FEAT_BOON_ENERGY_RESISTANCE = _boon(
    "feat.boon_energy_resistance", "能量抗性之恩惠 Boon of Energy Resistance",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "ability_choice", "value": 1, "type": "bonus"},
               {"field": "damage_resistance", "value": "choice_2", "type": "resistance"}],
    granted_actions=["energy_redirection"],
)

_FEAT_BOON_FATE = _boon(
    "feat.boon_fate", "扭曲命运之恩惠 Boon of Fate",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "ability_choice", "value": 1, "type": "bonus"}],
    granted_actions=["improve_fate"],
)

_FEAT_BOON_FORTITUDE = _boon(
    "feat.boon_fortitude", "超凡强韧之恩惠 Boon of Fortitude",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "ability_choice", "value": 1, "type": "bonus"},
               {"field": "hp_max", "value": 40, "type": "bonus"}],
)

_FEAT_BOON_IRRESISTIBLE_OFFENSE = _boon(
    "feat.boon_irresistible_offense", "无敌攻势之恩惠 Boon of Irresistible Offense",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "str_or_dex", "value": 1, "type": "bonus"}],
    granted_actions=["overcome_defenses", "overwhelming_strike"],
)

_FEAT_BOON_RECOVERY = _boon(
    "feat.boon_recovery", "强力恢复之恩惠 Boon of Recovery",
    feature_type=FeatureType.RESOURCE,
    modifiers=[{"field": "ability_choice", "value": 1, "type": "bonus"}],
    resource_pool={"name": "healing_pool", "max": 10, "recharge": "long_rest"},
    granted_actions=["last_stand"],
)

_FEAT_BOON_SKILL = _boon(
    "feat.boon_skill", "博学多才之恩惠 Boon of Skill",
    feature_type=FeatureType.PROFICIENCY,
    modifiers=[{"field": "ability_choice", "value": 1, "type": "bonus"}],
    granted_proficiencies=["all_skills"],
)

_FEAT_BOON_SPEED = _boon(
    "feat.boon_speed", "神行无拘之恩惠 Boon of Speed",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "ability_choice", "value": 1, "type": "bonus"},
               {"field": "speed", "value": 30, "type": "bonus"}],
    granted_actions=["escape_artist"],
)

_FEAT_BOON_SPELL_RECALL = _boon(
    "feat.boon_spell_recall", "法术溯回之恩惠 Boon of Spell Recall",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "int_or_wis_or_cha", "value": 1, "type": "bonus"}],
    granted_actions=["free_casting"],
)

_FEAT_BOON_NIGHT_SPIRIT = _boon(
    "feat.boon_night_spirit", "暗夜精魂之恩惠 Boon of the Night Spirit",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "ability_choice", "value": 1, "type": "bonus"}],
    granted_actions=["merge_with_shadows"],
)

_FEAT_BOON_TRUESIGHT = _boon(
    "feat.boon_truesight", "真实视觉之恩惠 Boon of Truesight",
    feature_type=FeatureType.MODIFIER,
    modifiers=[{"field": "ability_choice", "value": 1, "type": "bonus"},
               {"field": "truesight", "value": 60, "type": "grant"}],
)


# ──────────────────────────────────────────────────────────────────────────
# 汇总表 — key 为英文 snake_case
# ──────────────────────────────────────────────────────────────────────────

EXECUTABLE_FEATS: Dict[str, FeatureDefinition] = {
    # 起源 (10)
    "alert": _FEAT_ALERT,
    "crafter": _FEAT_CRAFTER,
    "healer": _FEAT_HEALER,
    "lucky": _FEAT_LUCKY,
    "magic_initiate": _FEAT_MAGIC_INITIATE,
    "musician": _FEAT_MUSICIAN,
    "savage_attacker": _FEAT_SAVAGE_ATTACKER,
    "skilled": _FEAT_SKILLED,
    "tavern_brawler": _FEAT_TAVERN_BRAWLER,
    "tough": _FEAT_TOUGH,
    # 通用 (43)
    "asi": _FEAT_ASI,
    "actor": _FEAT_ACTOR,
    "athlete": _FEAT_ATHLETE,
    "charger": _FEAT_CHARGER,
    "chef": _FEAT_CHEF,
    "crossbow_expert": _FEAT_CROSSBOW_EXPERT,
    "crusher": _FEAT_CRUSHER,
    "defensive_duelist": _FEAT_DEFENSIVE_DUELIST,
    "dual_wielder": _FEAT_DUAL_WIELDER,
    "durable": _FEAT_DURABLE,
    "elemental_adept": _FEAT_ELEMENTAL_ADEPT,
    "fey_touched": _FEAT_FEY_TOUCHED,
    "grappler": _FEAT_GRAPPLER,
    "great_weapon_master": _FEAT_GREAT_WEAPON_MASTER,
    "heavily_armored": _FEAT_HEAVILY_ARMORED,
    "heavy_armor_master": _FEAT_HEAVY_ARMOR_MASTER,
    "inspiring_leader": _FEAT_INSPIRING_LEADER,
    "keen_mind": _FEAT_KEEN_MIND,
    "lightly_armored": _FEAT_LIGHTLY_ARMORED,
    "mage_slayer": _FEAT_MAGE_SLAYER,
    "martial_weapon_training": _FEAT_MARTIAL_WEAPON_TRAINING,
    "medium_armor_master": _FEAT_MEDIUM_ARMOR_MASTER,
    "moderately_armored": _FEAT_MODERATELY_ARMORED,
    "mounted_combatant": _FEAT_MOUNTED_COMBATANT,
    "observant": _FEAT_OBSERVANT,
    "piercer": _FEAT_PIERCER,
    "poisoner": _FEAT_POISONER,
    "polearm_master": _FEAT_POLEARM_MASTER,
    "resilient": _FEAT_RESILIENT,
    "ritual_caster": _FEAT_RITUAL_CASTER,
    "sentinel": _FEAT_SENTINEL,
    "shadow_touched": _FEAT_SHADOW_TOUCHED,
    "sharpshooter": _FEAT_SHARPSHOOTER,
    "shield_master": _FEAT_SHIELD_MASTER,
    "skill_expert": _FEAT_SKILL_EXPERT,
    "skulker": _FEAT_SKULKER,
    "slasher": _FEAT_SLASHER,
    "speedy": _FEAT_SPEEDY,
    "spell_sniper": _FEAT_SPELL_SNIPER,
    "telekinetic": _FEAT_TELEKINETIC,
    "telepathic": _FEAT_TELEPATHIC,
    "war_caster": _FEAT_WAR_CASTER,
    "weapon_master": _FEAT_WEAPON_MASTER,
    # 战斗风格 (9)
    "archery": _FEAT_ARCHERY,
    "blind_fighting": _FEAT_BLIND_FIGHTING,
    "defense": _FEAT_DEFENSE,
    "dueling": _FEAT_DUELING,
    "great_weapon_fighting": _FEAT_GREAT_WEAPON_FIGHTING,
    "interception": _FEAT_INTERCEPTION,
    "protection": _FEAT_PROTECTION,
    "thrown_weapon_fighting": _FEAT_THROWN_WEAPON_FIGHTING,
    "two_weapon_fighting": _FEAT_TWO_WEAPON_FIGHTING,
    # 传奇恩惠 (12)
    "boon_combat_prowess": _FEAT_BOON_COMBAT_PROWESS,
    "boon_dimensional_travel": _FEAT_BOON_DIMENSIONAL_TRAVEL,
    "boon_energy_resistance": _FEAT_BOON_ENERGY_RESISTANCE,
    "boon_fate": _FEAT_BOON_FATE,
    "boon_fortitude": _FEAT_BOON_FORTITUDE,
    "boon_irresistible_offense": _FEAT_BOON_IRRESISTIBLE_OFFENSE,
    "boon_recovery": _FEAT_BOON_RECOVERY,
    "boon_skill": _FEAT_BOON_SKILL,
    "boon_speed": _FEAT_BOON_SPEED,
    "boon_spell_recall": _FEAT_BOON_SPELL_RECALL,
    "boon_night_spirit": _FEAT_BOON_NIGHT_SPIRIT,
    "boon_truesight": _FEAT_BOON_TRUESIGHT,
}


def get_executable_feat(key: str) -> FeatureDefinition | None:
    """按英文 key 取专长 FeatureDefinition"""
    return EXECUTABLE_FEATS.get(key)


def all_executable_feat_keys() -> list[str]:
    """返回所有专长 key"""
    return list(EXECUTABLE_FEATS.keys())
