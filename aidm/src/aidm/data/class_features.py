"""12 职业特性定义 + 子职业 Progression (CHR-001 / CHR-002)"""

from __future__ import annotations

from typing import Dict, List

from aidm.rules.feature_dsl import FeatureDefinition, FeatureType
from aidm.rules.resource import PoolType, ResourceType

# ═══════════════════════════════════════════════════════════════
# Barbarian — 野蛮人
# ═══════════════════════════════════════════════════════════════

rage_feature = FeatureDefinition(
    feature_id="barbarian_rage", name="狂暴 (Rage)", feature_type=FeatureType.RESOURCE,
    source_class="barbarian", source_level=1,
    description="战斗中进入狂暴状态，获得伤害加值和物理伤害抗性。",
    resource_pool={"name": "rage", "max": 2, "recharge": "short_rest",
                   "pool_type": PoolType.REGEN.value, "resource_type": ResourceType.RAGE.value},
    modifiers=[{"stat": "rage_damage", "value": 2, "type": "bonus"}],
)

unarmored_defense_barb = FeatureDefinition(
    feature_id="barbarian_unarmored_defense", name="无甲防御", feature_type=FeatureType.PASSIVE,
    source_class="barbarian", source_level=1,
    description="不穿护甲时，AC = 10 + 敏捷调整值 + 体质调整值。",
    modifiers=[{"stat": "ac_formula", "value": "10+DEX+CON", "type": "override"}],
)

reckless_attack = FeatureDefinition(
    feature_id="barbarian_reckless_attack", name="鲁莽攻击", feature_type=FeatureType.ACTION,
    source_class="barbarian", source_level=2,
    description="攻击掷骰时可选择鲁莽攻击，获得优势但攻击者对你也有优势。",
    granted_actions=["reckless_attack"],
)

dangerous_sense = FeatureDefinition(
    feature_id="barbarian_danger_sense", name="危险感知", feature_type=FeatureType.PASSIVE,
    source_class="barbarian", source_level=2,
    description="对可见的陷阱拥有敏捷豁免优势。",
    modifiers=[{"stat": "dex_save_vs_traps", "value": "advantage", "type": "advantage"}],
)

primal_path = FeatureDefinition(
    feature_id="barbarian_primal_path", name="原始之道", feature_type=FeatureType.PASSIVE,
    source_class="barbarian", source_level=3,
    description="选择一个原始之道子职业。",
)

extra_attack_barb = FeatureDefinition(
    feature_id="barbarian_extra_attack", name="额外攻击", feature_type=FeatureType.PASSIVE,
    source_class="barbarian", source_level=5,
    description="攻击动作时可攻击两次。",
    modifiers=[{"stat": "extra_attacks", "value": 1, "type": "bonus"}],
)

fast_movement = FeatureDefinition(
    feature_id="barbarian_fast_movement", name="快速移动", feature_type=FeatureType.PASSIVE,
    source_class="barbarian", source_level=5,
    description="不穿重甲时速度 +10 尺。",
    modifiers=[{"stat": "speed", "value": 10, "type": "bonus", "condition": "no_heavy_armor"}],
)

# Berserker subclass
frenzy_feature = FeatureDefinition(
    feature_id="berserker_frenzy", name="狂乱", feature_type=FeatureType.RESOURCE,
    source_class="barbarian", source_level=3,
    description="狂暴时可进入狂乱，额外攻击但获得一级力竭。",
    granted_actions=["frenzy_attack"],
)

mindless_rage = FeatureDefinition(
    feature_id="berserker_mindless_rage", name="无心狂暴", feature_type=FeatureType.PASSIVE,
    source_class="barbarian", source_level=6,
    description="狂暴时对魅惑和恐慌免疫。",
    modifiers=[{"stat": "condition_immunity", "value": ["charmed", "frightened"], "type": "immunity",
                "condition": "raging"}],
)

intimidating_presence = FeatureDefinition(
    feature_id="berserker_intimidating_presence", name="威吓存在", feature_type=FeatureType.ACTION,
    source_class="barbarian", source_level=10,
    description="动作：恐吓视野内生物进行感知豁免。",
    granted_actions=["intimidating_presence"],
)

retaliation = FeatureDefinition(
    feature_id="berserker_retaliation", name="报复", feature_type=FeatureType.REACTION,
    source_class="barbarian", source_level=14,
    description="被近战攻击命中时可用反应攻击该生物。",
    granted_actions=["retaliation_attack"],
)

# ═══════════════════════════════════════════════════════════════
# Bard — 吟游诗人
# ═══════════════════════════════════════════════════════════════

bardic_inspiration = FeatureDefinition(
    feature_id="bard_bardic_inspiration", name="吟唱激励", feature_type=FeatureType.RESOURCE,
    source_class="bard", source_level=1,
    description="用附赠动作激励一个生物，给予激励骰。",
    resource_pool={"name": "bardic_inspiration", "max": 2, "recharge": "long_rest",
                   "pool_type": PoolType.REGEN.value,
                   "resource_type": ResourceType.BARDIC_INSPIRATION.value},
    modifiers=[{"stat": "bardic_inspiration_die", "value": 6, "type": "base"}],
)

jack_of_all_trades = FeatureDefinition(
    feature_id="bard_jack_of_all_trades", name="万事通", feature_type=FeatureType.PASSIVE,
    source_class="bard", source_level=2,
    description="可以将熟练加值的一半加到任何不熟练的属性检定。",
    modifiers=[{"stat": "jack_of_all_trades", "value": True, "type": "special"}],
)

song_of_rest = FeatureDefinition(
    feature_id="bard_song_of_rest", name="休息之歌", feature_type=FeatureType.PASSIVE,
    source_class="bard", source_level=2,
    description="短休息时同伴额外恢复 1d6 HP。",
    modifiers=[{"stat": "song_of_rest_die", "value": 6, "type": "base"}],
)

bard_expertise = FeatureDefinition(
    feature_id="bard_expertise", name="专精", feature_type=FeatureType.PASSIVE,
    source_class="bard", source_level=3,
    description="选择两项熟练技能/工具，熟练加值翻倍。",
    modifiers=[{"stat": "expertise_count", "value": 2, "type": "grant"}],
)

bard_college = FeatureDefinition(
    feature_id="bard_college", name="吟游学院", feature_type=FeatureType.PASSIVE,
    source_class="bard", source_level=3,
    description="选择一个吟游学院子职业。",
)

bard_extra_attack = FeatureDefinition(
    feature_id="bard_extra_attack", name="额外攻击", feature_type=FeatureType.PASSIVE,
    source_class="bard", source_level=5,
    description="攻击动作时可攻击两次。",
    modifiers=[{"stat": "extra_attacks", "value": 1, "type": "bonus"}],
)

# Lore subclass
lore_college = FeatureDefinition(
    feature_id="lore_college_bonus_proficiencies", name="额外熟练", feature_type=FeatureType.PROFICIENCY,
    source_class="bard", source_level=3,
    description="获得三项额外技能熟练。",
    granted_proficiencies=["skill_choice_1", "skill_choice_2", "skill_choice_3"],
)

cutting_words = FeatureDefinition(
    feature_id="lore_cutting_words", name=" Cutting Words", feature_type=FeatureType.REACTION,
    source_class="bard", source_level=3,
    description="用反应消耗吟唱激励骰减少敌人的攻击/检定/伤害骰。",
    granted_actions=["cutting_words"],
)

additional_magical_secrets = FeatureDefinition(
    feature_id="lore_additional_magical_secrets", name="额外魔法秘辛", feature_type=FeatureType.SPELL_GRANT,
    source_class="bard", source_level=6,
    description="学习两个任意职业的法术。",
    granted_spells=["choice_any_2"],
)

# ═══════════════════════════════════════════════════════════════
# Cleric — 牧师
# ═══════════════════════════════════════════════════════════════

channel_divinity = FeatureDefinition(
    feature_id="cleric_channel_divinity", name="引导神力", feature_type=FeatureType.RESOURCE,
    source_class="cleric", source_level=2,
    description="使用引导神力触发特殊效果。",
    resource_pool={"name": "channel_divinity", "max": 1, "recharge": "short_rest",
                   "pool_type": PoolType.REGEN.value,
                   "resource_type": ResourceType.CHANNEL_DIVINITY.value},
)

divine_domain = FeatureDefinition(
    feature_id="cleric_divine_domain", name="神圣领域", feature_type=FeatureType.PASSIVE,
    source_class="cleric", source_level=1,
    description="选择一个神圣领域子职业。",
)

cleric_spellcasting = FeatureDefinition(
    feature_id="cleric_spellcasting", name="施法", feature_type=FeatureType.SPELL_GRANT,
    source_class="cleric", source_level=1,
    description="牧师是感知施法者，准备法术列表。",
)

# Life domain subclass
life_domain = FeatureDefinition(
    feature_id="life_domain_bonus_proficiency", name="领域奖励熟练", feature_type=FeatureType.PROFICIENCY,
    source_class="cleric", source_level=1,
    description="获得重甲熟练。",
    granted_proficiencies=["heavy_armor"],
)

disciple_of_life = FeatureDefinition(
    feature_id="life_disciple_of_life", name="生命门徒", feature_type=FeatureType.PASSIVE,
    source_class="cleric", source_level=1,
    description="治疗法术额外恢复 2 + 法术等级 的 HP。",
    modifiers=[{"stat": "healing_bonus", "value": "2+spell_level", "type": "bonus"}],
)

channel_divinity_turn_undead = FeatureDefinition(
    feature_id="cleric_turn_undead", name="驱散不死", feature_type=FeatureType.ACTION,
    source_class="cleric", source_level=2,
    description="引导神力驱散不死生物。",
    granted_actions=["turn_undead"],
)

# ═══════════════════════════════════════════════════════════════
# Druid — 德鲁伊
# ═══════════════════════════════════════════════════════════════

druidic = FeatureDefinition(
    feature_id="druid_druidic", name="德鲁伊语", feature_type=FeatureType.PROFICIENCY,
    source_class="druid", source_level=1,
    description="学会德鲁伊秘密语言。",
    granted_proficiencies=["language_druidic"],
)

wild_shape = FeatureDefinition(
    feature_id="druid_wild_shape", name="荒野变形", feature_type=FeatureType.RESOURCE,
    source_class="druid", source_level=2,
    description="魔法变形为见过的野兽。",
    resource_pool={"name": "wild_shape", "max": 1, "recharge": "short_rest",
                   "pool_type": PoolType.REGEN.value,
                   "resource_type": ResourceType.WILD_SHAPE.value},
    modifiers=[{"stat": "wild_shape_max_cr", "value": 0.25, "type": "base"}],
)

druid_circle = FeatureDefinition(
    feature_id="druid_circle", name="德鲁伊结社", feature_type=FeatureType.PASSIVE,
    source_class="druid", source_level=2,
    description="选择一个德鲁伊结社子职业。",
)

# Land subclass
land_druid = FeatureDefinition(
    feature_id="land_druid_bonus_cantrip", name="奖励戏法", feature_type=FeatureType.SPELL_GRANT,
    source_class="druid", source_level=2,
    description="学习一个额外的德鲁伊戏法。",
    granted_spells=["druid_cantrip_choice"],
)

natural_recovery = FeatureDefinition(
    feature_id="land_natural_recovery", name="自然恢复", feature_type=FeatureType.RESOURCE,
    source_class="druid", source_level=2,
    description="短休息时恢复法术位。",
    resource_pool={"name": "natural_recovery", "max": 1, "recharge": "long_rest",
                   "pool_type": PoolType.REGEN.value,
                   "resource_type": ResourceType.ARCANE_RECOVERY.value},
)

# ═══════════════════════════════════════════════════════════════
# Fighter — 战士
# ═══════════════════════════════════════════════════════════════

second_wind = FeatureDefinition(
    feature_id="fighter_second_wind", name="第二阵风", feature_type=FeatureType.RESOURCE,
    source_class="fighter", source_level=1,
    description="附赠动作恢复 1d10 + 战士等级 HP。",
    resource_pool={"name": "second_wind", "max": 1, "recharge": "short_rest",
                   "pool_type": PoolType.REGEN.value,
                   "resource_type": ResourceType.SECOND_WIND.value},
)

fighter_fighting_style = FeatureDefinition(
    feature_id="fighter_fighting_style", name="战斗风格", feature_type=FeatureType.PASSIVE,
    source_class="fighter", source_level=1,
    description="选择一种战斗风格。",
    modifiers=[{"stat": "fighting_style", "value": "choice", "type": "grant"}],
)

action_surge = FeatureDefinition(
    feature_id="fighter_action_surge", name="动作如潮", feature_type=FeatureType.RESOURCE,
    source_class="fighter", source_level=2,
    description="一个额外动作。",
    resource_pool={"name": "action_surge", "max": 1, "recharge": "short_rest",
                   "pool_type": PoolType.REGEN.value,
                   "resource_type": ResourceType.ACTION_SURGE.value},
    granted_actions=["action_surge"],
)

fighter_extra_attack = FeatureDefinition(
    feature_id="fighter_extra_attack", name="额外攻击", feature_type=FeatureType.PASSIVE,
    source_class="fighter", source_level=5,
    description="攻击动作时可攻击两次。",
    modifiers=[{"stat": "extra_attacks", "value": 1, "type": "bonus"}],
)

indomitable = FeatureDefinition(
    feature_id="fighter_indomitable", name="不屈", feature_type=FeatureType.RESOURCE,
    source_class="fighter", source_level=5,
    description="重掷一次失败的豁免。",
    resource_pool={"name": "indomitable", "max": 1, "recharge": "long_rest",
                   "pool_type": PoolType.REGEN.value,
                   "resource_type": ResourceType.GENERAL.value},
)

# Champion subclass
improved_critical = FeatureDefinition(
    feature_id="champion_improved_critical", name="强化暴击", feature_type=FeatureType.PASSIVE,
    source_class="fighter", source_level=3,
    description="攻击骰 19-20 均为暴击。",
    modifiers=[{"stat": "crit_range", "value": 19, "type": "override"}],
)

remarkable_athlete = FeatureDefinition(
    feature_id="champion_remarkable_athlete", name="卓越运动员", feature_type=FeatureType.PASSIVE,
    source_class="fighter", source_level=7,
    description="力量/敏捷/体质检定的熟练加值减半可加到跳跃距离。",
    modifiers=[{"stat": "jump_bonus", "value": "half_proficiency", "type": "bonus"}],
)

# ═══════════════════════════════════════════════════════════════
# Monk — 武僧
# ═══════════════════════════════════════════════════════════════

martial_arts = FeatureDefinition(
    feature_id="monk_martial_arts", name="武技", feature_type=FeatureType.PASSIVE,
    source_class="monk", source_level=1,
    description="使用敏捷代替力量进行近战攻击，武僧武器伤害骰 d4。",
    modifiers=[{"stat": "martial_arts_die", "value": 4, "type": "base"},
               {"stat": "monk_weapon_agility", "value": True, "type": "special"}],
)

monk_unarmored_defense = FeatureDefinition(
    feature_id="monk_unarmored_defense", name="无甲防御", feature_type=FeatureType.PASSIVE,
    source_class="monk", source_level=1,
    description="不穿护甲时 AC = 10 + 敏捷调整值 + 感知调整值。",
    modifiers=[{"stat": "ac_formula", "value": "10+DEX+WIS", "type": "override"}],
)

ki = FeatureDefinition(
    feature_id="monk_ki", name="气 (Ki)", feature_type=FeatureType.RESOURCE,
    source_class="monk", source_level=2,
    description="消耗气来使用疾风拳、患者防御和空灵步。",
    resource_pool={"name": "ki", "max": 2, "recharge": "short_rest",
                   "pool_type": PoolType.REGEN.value,
                   "resource_type": ResourceType.KI.value},
    granted_actions=["flurry_of_blows", "patients_defense", "step_of_the_wind"],
)

unarmored_movement = FeatureDefinition(
    feature_id="monk_unarmored_movement", name="无甲移动", feature_type=FeatureType.PASSIVE,
    source_class="monk", source_level=2,
    description="不穿护甲时速度 +10 尺。",
    modifiers=[{"stat": "speed", "value": 10, "type": "bonus", "condition": "no_heavy_armor"}],
)

monk_extra_attack = FeatureDefinition(
    feature_id="monk_extra_attack", name="额外攻击", feature_type=FeatureType.PASSIVE,
    source_class="monk", source_level=5,
    description="攻击动作时可攻击两次。",
    modifiers=[{"stat": "extra_attacks", "value": 1, "type": "bonus"}],
)

# Open Hand subclass
open_hand_technique = FeatureDefinition(
    feature_id="open_hand_open_hand_technique", name="开掌技法", feature_type=FeatureType.PASSIVE,
    source_class="monk", source_level=3,
    description="疾风拳命中时可击倒、推开或阻止反应。",
    granted_actions=["open_hand_technique"],
)

wholeness_of_body = FeatureDefinition(
    feature_id="open_hand_wholeness_of_body", name="身心合一", feature_type=FeatureType.ACTION,
    source_class="monk", source_level=6,
    description="动作恢复等于武僧等级的 HP。",
    granted_actions=["wholeness_of_body"],
)

# ═══════════════════════════════════════════════════════════════
# Paladin — 圣武士
# ═══════════════════════════════════════════════════════════════

divine_sense = FeatureDefinition(
    feature_id="paladin_divine_sense", name="神圣感知", feature_type=FeatureType.RESOURCE,
    source_class="paladin", source_level=1,
    description="感知视野内的天界/邪魔/不死生物。",
    resource_pool={"name": "divine_sense", "max": 3, "recharge": "long_rest",
                   "pool_type": PoolType.REGEN.value,
                   "resource_type": ResourceType.GENERAL.value},
)

lay_on_hands = FeatureDefinition(
    feature_id="paladin_lay_on_hands", name="治疗之触", feature_type=FeatureType.RESOURCE,
    source_class="paladin", source_level=1,
    description="触摸恢复 HP，每级 5 点池。",
    resource_pool={"name": "lay_on_hands", "max": 5, "recharge": "long_rest",
                   "pool_type": PoolType.REGEN.value,
                   "resource_type": ResourceType.LAY_ON_HANDS.value},
)

paladin_fighting_style = FeatureDefinition(
    feature_id="paladin_fighting_style", name="战斗风格", feature_type=FeatureType.PASSIVE,
    source_class="paladin", source_level=2,
    description="选择一种战斗风格。",
    modifiers=[{"stat": "fighting_style", "value": "choice", "type": "grant"}],
)

divine_smite = FeatureDefinition(
    feature_id="paladin_divine_smite", name="神圣惩击", feature_type=FeatureType.PASSIVE,
    source_class="paladin", source_level=2,
    description="命中时消耗法术位造成额外光耀伤害。",
    granted_actions=["divine_smite"],
)

paladin_extra_attack = FeatureDefinition(
    feature_id="paladin_extra_attack", name="额外攻击", feature_type=FeatureType.PASSIVE,
    source_class="paladin", source_level=5,
    description="攻击动作时可攻击两次。",
    modifiers=[{"stat": "extra_attacks", "value": 1, "type": "bonus"}],
)

# Devotion subclass
tenets_of_devotion = FeatureDefinition(
    feature_id="devotion_tenets", name="奉献信条", feature_type=FeatureType.PASSIVE,
    source_class="paladin", source_level=3,
    description="遵循诚实和勇气的信条。",
)

sacred_weapon = FeatureDefinition(
    feature_id="devotion_sacred_weapon", name="神圣武器", feature_type=FeatureType.RESOURCE,
    source_class="paladin", source_level=3,
    description="引导神力给武器附加魅力加值。",
    resource_pool={"name": "channel_divinity_devotion", "max": 1, "recharge": "short_rest",
                   "pool_type": PoolType.REGEN.value,
                   "resource_type": ResourceType.CHANNEL_DIVINITY.value},
)

# ═══════════════════════════════════════════════════════════════
# Ranger — 游侠
# ═══════════════════════════════════════════════════════════════

favored_enemy = FeatureDefinition(
    feature_id="ranger_favored_enemy", name="宿敌", feature_type=FeatureType.PASSIVE,
    source_class="ranger", source_level=1,
    description="选择一个宿敌类型，获得追踪/交互优势。",
    modifiers=[{"stat": "favored_enemy", "value": "choice", "type": "grant"}],
)

natural_explorer = FeatureDefinition(
    feature_id="ranger_natural_explorer", name="自然探索者", feature_type=FeatureType.PASSIVE,
    source_class="ranger", source_level=1,
    description="在偏好的地形中获得移动和生存优势。",
    modifiers=[{"stat": "favored_terrain", "value": "choice", "type": "grant"}],
)

ranger_fighting_style = FeatureDefinition(
    feature_id="ranger_fighting_style", name="战斗风格", feature_type=FeatureType.PASSIVE,
    source_class="ranger", source_level=2,
    description="选择一种战斗风格。",
    modifiers=[{"stat": "fighting_style", "value": "choice", "type": "grant"}],
)

ranger_spellcasting = FeatureDefinition(
    feature_id="ranger_spellcasting", name="施法", feature_type=FeatureType.SPELL_GRANT,
    source_class="ranger", source_level=2,
    description="游侠是感知施法者。",
)

ranger_extra_attack = FeatureDefinition(
    feature_id="ranger_extra_attack", name="额外攻击", feature_type=FeatureType.PASSIVE,
    source_class="ranger", source_level=5,
    description="攻击动作时可攻击两次。",
    modifiers=[{"stat": "extra_attacks", "value": 1, "type": "bonus"}],
)

# Hunter subclass
hunters_prey = FeatureDefinition(
    feature_id="hunter_hunters_prey", name="猎人猎物", feature_type=FeatureType.PASSIVE,
    source_class="ranger", source_level=3,
    description="选择一种猎人战斗选项。",
    granted_actions=["colossus_slayer", "giant_killer", "horde_breaker"],
)

defenses_of_the_hunter = FeatureDefinition(
    feature_id="hunter_defenses", name="猎人防御", feature_type=FeatureType.PASSIVE,
    source_class="ranger", source_level=7,
    description="选择一种猎人防御选项。",
)

# ═══════════════════════════════════════════════════════════════
# Rogue — 游荡者
# ═══════════════════════════════════════════════════════════════

expertise_rogue = FeatureDefinition(
    feature_id="rogue_expertise", name="专精", feature_type=FeatureType.PASSIVE,
    source_class="rogue", source_level=1,
    description="选择两项熟练技能/工具，熟练加值翻倍。",
    modifiers=[{"stat": "expertise_count", "value": 2, "type": "grant"}],
)

sneak_attack = FeatureDefinition(
    feature_id="rogue_sneak_attack", name="偷袭", feature_type=FeatureType.PASSIVE,
    source_class="rogue", source_level=1,
    description="有优势或盟友邻接时造成额外精准伤害。",
    modifiers=[{"stat": "sneak_attack_die", "value": 6, "type": "base"},
               {"stat": "sneak_attack_count", "value": 1, "type": "base"}],
)

thieves_talent = FeatureDefinition(
    feature_id="rogue_thieves_cant", name="盗贼暗语", feature_type=FeatureType.PROFICIENCY,
    source_class="rogue", source_level=1,
    description="学会盗贼暗语。",
    granted_proficiencies=["thieves_cant"],
)

cunning_action = FeatureDefinition(
    feature_id="rogue_cunning_action", name="狡诈动作", feature_type=FeatureType.PASSIVE,
    source_class="rogue", source_level=2,
    description="附赠动作执行疾走、撤离或躲藏。",
    granted_actions=["cunning_action_dash", "cunning_action_disengage", "cunning_action_hide"],
)

uncanny_dodge = FeatureDefinition(
    feature_id="rogue_uncanny_dodge", name="灵巧闪避", feature_type=FeatureType.REACTION,
    source_class="rogue", source_level=5,
    description="反应：将一次攻击伤害减半。",
    granted_actions=["uncanny_dodge"],
)

# Thief subclass
fast_hands = FeatureDefinition(
    feature_id="thief_fast_hands", name="快手", feature_type=FeatureType.PASSIVE,
    source_class="rogue", source_level=3,
    description="可以用附赠动作执行使用物品的动作。",
    granted_actions=["fast_hands"],
)

second_story_work = FeatureDefinition(
    feature_id="thief_second_story", name="飞檐走壁", feature_type=FeatureType.PASSIVE,
    source_class="rogue", source_level=3,
    description="攀爬不消耗额外移动力。",
    modifiers=[{"stat": "climb_speed_equals_walk", "value": True, "type": "special"}],
)

# ═══════════════════════════════════════════════════════════════
# Sorcerer — 术士
# ═══════════════════════════════════════════════════════════════

sorcery_points = FeatureDefinition(
    feature_id="sorcerer_sorcery_points", name="术士点数", feature_type=FeatureType.RESOURCE,
    source_class="sorcerer", source_level=2,
    description="消耗术士点数施展超魔或恢复法术位。",
    resource_pool={"name": "sorcery_points", "max": 2, "recharge": "long_rest",
                   "pool_type": PoolType.REGEN.value,
                   "resource_type": ResourceType.SORCERY_POINTS.value},
    granted_actions=["metamagic_convert"],
)

sorcerous_origin = FeatureDefinition(
    feature_id="sorcerer_sorcerous_origin", name="术士源头", feature_type=FeatureType.PASSIVE,
    source_class="sorcerer", source_level=1,
    description="选择术士源头子职业。",
)

metamagic = FeatureDefinition(
    feature_id="sorcerer_metamagic", name="超魔", feature_type=FeatureType.PASSIVE,
    source_class="sorcerer", source_level=3,
    description="选择两种超魔选项。",
    granted_actions=["subtle_spell", "twinned_spell", "heightened_spell", "quickened_spell"],
)

# Draconic subclass
draconic_ancestry = FeatureDefinition(
    feature_id="draconic_draconic_ancestry", name="龙裔血统", feature_type=FeatureType.PASSIVE,
    source_class="sorcerer", source_level=1,
    description="选择一种龙类祖先。",
    modifiers=[{"stat": "hp_per_level_bonus", "value": 1, "type": "bonus"}],
)

elemental_affinity = FeatureDefinition(
    feature_id="draconic_elemental_affinity", name="元素亲和", feature_type=FeatureType.PASSIVE,
    source_class="sorcerer", source_level=6,
    description="对应龙类伤害类型的法术加魅力调整值伤害。",
    modifiers=[{"stat": "elemental_damage_bonus", "value": "CHA", "type": "bonus"}],
)

# ═══════════════════════════════════════════════════════════════
# Warlock — 邪术师
# ═══════════════════════════════════════════════════════════════

eldritch_invocations = FeatureDefinition(
    feature_id="warlock_eldritch_invocations", name="魔能祈唤", feature_type=FeatureType.PASSIVE,
    source_class="warlock", source_level=2,
    description="获得两个魔能祈唤。",
    granted_actions=["invocation_choice_2"],
)

pact_magic = FeatureDefinition(
    feature_id="warlock_pact_magic", name="魔契法术", feature_type=FeatureType.SPELL_GRANT,
    source_class="warlock", source_level=1,
    description="独特的法术位系统：少量但高等级法术位，短休息恢复。",
    modifiers=[{"stat": "pact_magic", "value": True, "type": "special"}],
)

otherworldly_patron = FeatureDefinition(
    feature_id="warlock_otherworldly_patron", name="异界宗主", feature_type=FeatureType.PASSIVE,
    source_class="warlock", source_level=1,
    description="选择异界宗主子职业。",
)

# Fiend subclass
dark_ones_blessing = FeatureDefinition(
    feature_id="fiend_dark_ones_blessing", name="暗黑祝福", feature_type=FeatureType.PASSIVE,
    source_class="warlock", source_level=1,
    description="击杀敌人时获得临时 HP。",
    modifiers=[{"stat": "dark_ones_blessing", "value": "warlock_level+CHA", "type": "temp_hp"}],
)

fiendish_resilience = FeatureDefinition(
    feature_id="fiend_fiendish_resilience", name="恶魔韧性", feature_type=FeatureType.PASSIVE,
    source_class="warlock", source_level=6,
    description="选择一种伤害类型的抗性。",
    modifiers=[{"stat": "damage_resistance", "value": "choice", "type": "resistance"}],
)

# ═══════════════════════════════════════════════════════════════
# Wizard — 法师
# ═══════════════════════════════════════════════════════════════

spellbook = FeatureDefinition(
    feature_id="wizard_spellbook", name="法术书", feature_type=FeatureType.SPELL_GRANT,
    source_class="wizard", source_level=1,
    description="拥有一本法术书，记录 6 个 1 级法术。",
    granted_spells=["cantrip_3", "level_1_spell_6"],
)

arcane_recovery = FeatureDefinition(
    feature_id="wizard_arcane_recovery", name="奥术恢复", feature_type=FeatureType.RESOURCE,
    source_class="wizard", source_level=1,
    description="短休息时恢复法术位（总等级 ≤ 法师等级/2）。",
    resource_pool={"name": "arcane_recovery", "max": 1, "recharge": "long_rest",
                   "pool_type": PoolType.REGEN.value,
                   "resource_type": ResourceType.ARCANE_RECOVERY.value},
)

arcane_tradition = FeatureDefinition(
    feature_id="wizard_arcane_tradition", name="奥术传统", feature_type=FeatureType.PASSIVE,
    source_class="wizard", source_level=2,
    description="选择奥术传统子职业。",
)

# Evocation subclass
evocation_savant = FeatureDefinition(
    feature_id="evocation_savant", name="塑能专精", feature_type=FeatureType.PASSIVE,
    source_class="wizard", source_level=2,
    description="抄写塑能法术的时间和金币减半。",
    modifiers=[{"stat": "copy_spell_cost_half", "value": "evocation", "type": "special"}],
)

sculpt_spells = FeatureDefinition(
    feature_id="evocation_sculpt_spells", name="法术塑形", feature_type=FeatureType.PASSIVE,
    source_class="wizard", source_level=2,
    description="塑能法术可选择自动豁免的友方。",
    granted_actions=["sculpt_spells"],
)


# ═══════════════════════════════════════════════════════════════
# CLASS_FEATURES — 主表
# ═══════════════════════════════════════════════════════════════

CLASS_FEATURES: Dict[str, Dict[int, List[FeatureDefinition]]] = {
    "barbarian": {
        1: [rage_feature, unarmored_defense_barb],
        2: [reckless_attack, dangerous_sense],
        3: [primal_path],
        5: [extra_attack_barb, fast_movement],
    },
    "bard": {
        1: [bardic_inspiration],
        2: [jack_of_all_trades, song_of_rest],
        3: [bard_expertise, bard_college],
        5: [bard_extra_attack],
    },
    "cleric": {
        1: [divine_domain, cleric_spellcasting],
        2: [channel_divinity, channel_divinity_turn_undead],
        3: [],  # 子职特性
        5: [],
    },
    "druid": {
        1: [druidic],
        2: [wild_shape, druid_circle],
        3: [],
        5: [],
    },
    "fighter": {
        1: [second_wind, fighter_fighting_style],
        2: [action_surge],
        3: [],  # 子职特性
        5: [fighter_extra_attack, indomitable],
    },
    "monk": {
        1: [martial_arts, monk_unarmored_defense],
        2: [ki, unarmored_movement],
        3: [],  # 子职特性
        5: [monk_extra_attack],
    },
    "paladin": {
        1: [divine_sense, lay_on_hands],
        2: [paladin_fighting_style, divine_smite],
        3: [],  # 子职特性
        5: [paladin_extra_attack],
    },
    "ranger": {
        1: [favored_enemy, natural_explorer],
        2: [ranger_fighting_style, ranger_spellcasting],
        3: [],  # 子职特性
        5: [ranger_extra_attack],
    },
    "rogue": {
        1: [expertise_rogue, sneak_attack, thieves_talent],
        2: [cunning_action],
        3: [],  # 子职特性
        5: [uncanny_dodge],
    },
    "sorcerer": {
        1: [sorcerous_origin],
        2: [sorcery_points],
        3: [metamagic],
        5: [],
    },
    "warlock": {
        1: [otherworldly_patron, pact_magic],
        2: [eldritch_invocations],
        3: [],  # 子职特性
        5: [],
    },
    "wizard": {
        1: [spellbook, arcane_recovery],
        2: [arcane_tradition],
        3: [],  # 子职特性
        5: [],
    },
}


# ═══════════════════════════════════════════════════════════════
# SUBCLASS_FEATURES — 子职业表 (CHR-002)
# ═══════════════════════════════════════════════════════════════

SUBCLASS_FEATURES: Dict[str, Dict[str, Dict[int, List[FeatureDefinition]]]] = {
    "barbarian": {
        "berserker": {
            3: [frenzy_feature],
            6: [mindless_rage],
            10: [intimidating_presence],
            14: [retaliation],
        },
    },
    "bard": {
        "lore": {
            3: [lore_college, cutting_words],
            6: [additional_magical_secrets],
        },
    },
    "cleric": {
        "life": {
            1: [life_domain, disciple_of_life],
        },
    },
    "druid": {
        "land": {
            2: [land_druid, natural_recovery],
        },
    },
    "fighter": {
        "champion": {
            3: [improved_critical],
            7: [remarkable_athlete],
        },
    },
    "monk": {
        "open_hand": {
            3: [open_hand_technique],
            6: [wholeness_of_body],
        },
    },
    "paladin": {
        "devotion": {
            3: [tenets_of_devotion, sacred_weapon],
        },
    },
    "ranger": {
        "hunter": {
            3: [hunters_prey],
            7: [defenses_of_the_hunter],
        },
    },
    "rogue": {
        "thief": {
            3: [fast_hands, second_story_work],
        },
    },
    "sorcerer": {
        "draconic": {
            1: [draconic_ancestry],
            6: [elemental_affinity],
        },
    },
    "warlock": {
        "fiend": {
            1: [dark_ones_blessing],
            6: [fiendish_resilience],
        },
    },
    "wizard": {
        "evocation": {
            2: [evocation_savant, sculpt_spells],
        },
    },
}
