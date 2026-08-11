"""10 物种结构化特质 — 将 races.py 文本数据映射为结构化定义。

规则依据: PHB 2024 第二章「物种」
每个物种包含: 体型/速度/属性加成/感官/特性/语言/子族。
"""

from __future__ import annotations

from typing import Dict, List, Optional

# ──────────────────────────────────────────────────────────────────────────
# 物种定义表
# ──────────────────────────────────────────────────────────────────────────

SPECIES_DEFINITIONS: Dict[str, dict] = {
    "human": {
        "species_id": "species.human",
        "name": "人类 Human",
        "size": ["Medium", "Small"],  # 创建时选择
        "speed_ft": 30,
        "ability_bonuses": {},  # 2024人类无固定属性加成，通过背景/专长获得
        "features": ["resourceful", "skillful", "versatile"],
        "senses": {},
        "condition_immunities": [],
        "languages": ["common", "choice"],
        "subraces": None,
        "feature_details": {
            "resourceful": {"type": "passive", "description": "完成长休时获得英雄激励"},
            "skillful": {"type": "proficiency", "grants": ["skill_choice_1"]},
            "versatile": {"type": "feat_grant", "grants": ["origin_feat_choice"]},
        },
    },
    "dwarf": {
        "species_id": "species.dwarf",
        "name": "矮人 Dwarf",
        "size": ["Medium"],
        "speed_ft": 30,
        "ability_bonuses": {},  # 2024无固定，通过背景获得
        "features": ["darkvision_120", "dwarven_resilience", "dwarven_toughness", "stonecunning"],
        "senses": {"darkvision": 120},
        "condition_immunities": [],
        "damage_resistances": ["poison"],
        "languages": ["common", "dwarvish"],
        "subraces": None,
        "feature_details": {
            "darkvision_120": {"type": "sense", "range": 120},
            "dwarven_resilience": {
                "type": "passive",
                "damage_resistance": ["poison"],
                "save_advantage": ["poisoned"],
            },
            "dwarven_toughness": {
                "type": "modifier",
                "hp_bonus_at_1": 1,
                "hp_bonus_per_level": 1,
            },
            "stonecunning": {
                "type": "resource",
                "grants": ["tremorsense_60"],
                "uses": "proficiency_bonus",
                "recharge": "long_rest",
            },
        },
    },
    "elf": {
        "species_id": "species.elf",
        "name": "精灵 Elf",
        "size": ["Medium"],
        "speed_ft": 30,
        "ability_bonuses": {},
        "features": ["darkvision_60", "elven_lineage"],
        "senses": {"darkvision": 60},
        "condition_immunities": ["charmed_magical_sleep"],
        "languages": ["common", "elvish"],
        "subraces": ["drow", "high_elf", "wood_elf"],
        "feature_details": {
            "darkvision_60": {"type": "sense", "range": 60},
            "elven_lineage": {
                "type": "choice",
                "options": ["drow", "high_elf", "wood_elf"],
                "description": "选择血系获得对应1/3/5级法术",
            },
        },
    },
    "halfling": {
        "species_id": "species.halfling",
        "name": "半身人 Halfling",
        "size": ["Small"],
        "speed_ft": 30,
        "ability_bonuses": {},
        "features": ["brave", "halfling_nimbleness", "lucky", "naturally_stealthy"],
        "senses": {},
        "condition_immunities": [],
        "languages": ["common", "halfling"],
        "subraces": None,
        "feature_details": {
            "brave": {"type": "passive", "save_advantage": ["frightened"]},
            "halfling_nimbleness": {"type": "passive", "can_move_through_larger_creature": True},
            "lucky": {"type": "passive", "reroll_on_1": True},
            "naturally_stealthy": {"type": "passive", "can_hide_behind_larger_creature": True},
        },
    },
    "gnome": {
        "species_id": "species.gnome",
        "name": "侏儒 Gnome",
        "size": ["Small"],
        "speed_ft": 30,
        "ability_bonuses": {},
        "features": ["darkvision_60", "gnome_cunning", "gnome_lineage"],
        "senses": {"darkvision": 60},
        "condition_immunities": [],
        "languages": ["common", "gnomish"],
        "subraces": ["forest_gnome", "rock_gnome"],
        "feature_details": {
            "darkvision_60": {"type": "sense", "range": 60},
            "gnome_cunning": {
                "type": "passive",
                "save_advantage": ["int", "wis", "cha"],
            },
            "gnome_lineage": {
                "type": "choice",
                "options": ["forest_gnome", "rock_gnome"],
                "description": "选择血系获得对应法术",
            },
        },
    },
    "goliath": {
        "species_id": "species.goliath",
        "name": "歌利亚 Goliath",
        "size": ["Medium"],
        "speed_ft": 35,
        "ability_bonuses": {},
        "features": ["giant_ancestry", "large_form", "powerful_build"],
        "senses": {},
        "condition_immunities": [],
        "languages": ["common", "giant"],
        "subraces": None,
        "feature_details": {
            "giant_ancestry": {
                "type": "choice",
                "options": ["cloud", "fire", "frost", "hill", "stone", "storm"],
                "uses": "proficiency_bonus",
                "recharge": "long_rest",
            },
            "large_form": {
                "type": "action",
                "available_from_level": 5,
                "duration_minutes": 10,
                "effects": ["str_check_advantage", "speed_plus_10"],
                "recharge": "long_rest",
            },
            "powerful_build": {
                "type": "passive",
                "grapple_escape_advantage": True,
                "carry_count_as_larger": True,
            },
        },
    },
    "orc": {
        "species_id": "species.orc",
        "name": "兽人 Orc",
        "size": ["Medium"],
        "speed_ft": 30,
        "ability_bonuses": {},
        "features": ["adrenaline_rush", "darkvision_120", "relentless_endurance"],
        "senses": {"darkvision": 120},
        "condition_immunities": [],
        "languages": ["common", "orc"],
        "subraces": None,
        "feature_details": {
            "adrenaline_rush": {
                "type": "bonus_action",
                "grants": ["dash", "temp_hp_equals_proficiency"],
                "uses": "proficiency_bonus",
                "recharge": "short_rest",
            },
            "darkvision_120": {"type": "sense", "range": 120},
            "relentless_endurance": {
                "type": "passive",
                "hp_drop_to_1_instead_of_0": True,
                "recharge": "long_rest",
            },
        },
    },
    "tiefling": {
        "species_id": "species.tiefling",
        "name": "提夫林 Tiefling",
        "size": ["Medium", "Small"],
        "speed_ft": 30,
        "ability_bonuses": {},
        "features": ["darkvision_60", "fiendish_legacy"],
        "senses": {"darkvision": 60},
        "condition_immunities": [],
        "languages": ["common", "infernal"],
        "subraces": ["abyssal", "chthonic", "infernal"],
        "feature_details": {
            "darkvision_60": {"type": "sense", "range": 60},
            "fiendish_legacy": {
                "type": "choice",
                "options": ["abyssal", "chthonic", "infernal"],
                "description": "选择遗赠获得对应1/3/5级法术",
            },
        },
    },
    "dragonborn": {
        "species_id": "species.dragonborn",
        "name": "龙裔 Dragonborn",
        "size": ["Medium"],
        "speed_ft": 30,
        "ability_bonuses": {},
        "features": ["draconic_ancestry", "breath_weapon", "damage_resistance"],
        "senses": {"darkvision": 60},
        "condition_immunities": [],
        "languages": ["common", "draconic"],
        "subraces": None,
        "feature_details": {
            "draconic_ancestry": {
                "type": "choice",
                "options": ["white", "black", "green", "blue", "red",
                            "brass", "copper", "bronze", "silver", "gold"],
            },
            "breath_weapon": {
                "type": "action",
                "area": "15ft_cone_or_30x5ft_line",
                "save_dc": "8+CON+PB",
                "damage_dice_by_level": {1: "1d10", 5: "2d10", 11: "3d10", 17: "4d10"},
                "uses": "proficiency_bonus",
                "recharge": "long_rest",
            },
            "damage_resistance": {
                "type": "passive",
                "resistance_type": "matches_draconic_ancestry",
            },
        },
    },
    "aasimar": {
        "species_id": "species.aasimar",
        "name": "阿斯莫 Aasimar",
        "size": ["Medium", "Small"],
        "speed_ft": 30,
        "ability_bonuses": {},
        "features": ["celestial_resistance", "darkvision_60", "healing_hands", "light_bearer", "celestial_revelation"],
        "senses": {"darkvision": 60},
        "condition_immunities": [],
        "damage_resistances": ["radiant", "necrotic"],
        "languages": ["common", "celestial"],
        "subraces": None,
        "feature_details": {
            "celestial_resistance": {
                "type": "passive",
                "damage_resistance": ["radiant", "necrotic"],
            },
            "darkvision_60": {"type": "sense", "range": 60},
            "healing_hands": {
                "type": "action",
                "healing_dice": "proficiency_bonus d4",
                "recharge": "long_rest",
            },
            "light_bearer": {
                "type": "spell_grant",
                "spells": ["light"],
                "spellcasting_ability": "cha",
            },
            "celestial_revelation": {
                "type": "transformation",
                "available_from_level": 3,
                "options": ["celestial_wings", "inner_radiance", "necrotic_shroud"],
                "recharge": "long_rest",
            },
        },
    },
}


def get_species(key: str) -> dict | None:
    """按英文 key 取物种定义"""
    return SPECIES_DEFINITIONS.get(key)


def all_species_keys() -> list[str]:
    """返回所有物种 key"""
    return list(SPECIES_DEFINITIONS.keys())


def get_species_speed(key: str) -> int:
    """获取物种速度"""
    sp = SPECIES_DEFINITIONS.get(key)
    return sp["speed_ft"] if sp else 30


def get_species_senses(key: str) -> dict:
    """获取物种感官"""
    sp = SPECIES_DEFINITIONS.get(key)
    return sp.get("senses", {}) if sp else {}


def get_species_darkvision(key: str) -> int:
    """获取物种黑暗视觉（尺）"""
    senses = get_species_senses(key)
    return senses.get("darkvision", 0)


def get_species_resistances(key: str) -> list[str]:
    """获取物种伤害抗性"""
    sp = SPECIES_DEFINITIONS.get(key)
    return sp.get("damage_resistances", []) if sp else []
