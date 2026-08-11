"""16 背景约束定义 — 将 backgrounds.py 文本数据映射为结构化定义。

规则依据: PHB 2024 第一章「背景」
每个背景包含: 属性选项/技能熟练/工具熟练/语言/起源专长/装备。
"""

from __future__ import annotations

from typing import Dict, List, Optional

# ──────────────────────────────────────────────────────────────────────────
# 背景定义表
# ──────────────────────────────────────────────────────────────────────────

BACKGROUND_DEFINITIONS: Dict[str, dict] = {
    "acolyte": {
        "background_id": "bg.acolyte",
        "name": "侍僧 Acolyte",
        "ability_scores": ["int", "wis", "cha"],  # +1/+1/+1 或 +2 选择
        "skill_choices": {"options": ["insight", "religion"], "choose": 2},
        "tool_choices": {"options": ["calligrapher_supplies"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.magic_initiate"],
        "equipment": ["holy_symbol", "prayer_book", "5_tincense", "priest_vestments"],
        "starting_gold": 8,
    },
    "guard": {
        "background_id": "bg.guard",
        "name": "警卫 Guard",
        "ability_scores": ["str", "int", "wis"],
        "skill_choices": {"options": ["athletics", "perception"], "choose": 2},
        "tool_choices": {"options": ["gaming_set_choice"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.alert"],
        "equipment": ["spear", "light_crossbow", "20_bolts", "hooded_lantern", "manacles", "quiver", "travelers_clothes"],
        "starting_gold": 12,
    },
    "sailor": {
        "background_id": "bg.sailor",
        "name": "水手 Sailor",
        "ability_scores": ["str", "dex", "wis"],
        "skill_choices": {"options": ["acrobatics", "perception"], "choose": 2},
        "tool_choices": {"options": ["navigators_tools"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.tavern_brawler"],
        "equipment": ["dagger", "navigators_tools", "rope", "travelers_clothes"],
        "starting_gold": 20,
    },
    "artisan": {
        "background_id": "bg.artisan",
        "name": "工匠 Artisan",
        "ability_scores": ["str", "dex", "int"],
        "skill_choices": {"options": ["investigation", "persuasion"], "choose": 2},
        "tool_choices": {"options": ["artisan_tools_choice"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.crafter"],
        "equipment": ["artisan_tools_choice", "2_pouches", "travelers_clothes"],
        "starting_gold": 32,
    },
    "guide": {
        "background_id": "bg.guide",
        "name": "向导 Guide",
        "ability_scores": ["dex", "con", "wis"],
        "skill_choices": {"options": ["stealth", "survival"], "choose": 2},
        "tool_choices": {"options": ["cartographers_tools"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.magic_initiate"],
        "equipment": ["shortbow", "20_arrows", "cartographers_tools", "bedroll", "quiver", "tent", "travelers_clothes"],
        "starting_gold": 3,
    },
    "scribe": {
        "background_id": "bg.scribe",
        "name": "抄写员 Scribe",
        "ability_scores": ["dex", "int", "wis"],
        "skill_choices": {"options": ["investigation", "perception"], "choose": 2},
        "tool_choices": {"options": ["calligrapher_supplies"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.skilled"],
        "equipment": ["calligrapher_supplies", "fine_clothes", "lamp", "3_oil", "12_parchment"],
        "starting_gold": 23,
    },
    "charlatan": {
        "background_id": "bg.charlatan",
        "name": "骗子 Charlatan",
        "ability_scores": ["dex", "con", "cha"],
        "skill_choices": {"options": ["deception", "sleight_of_hand"], "choose": 2},
        "tool_choices": {"options": ["forgery_kit"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.skilled"],
        "equipment": ["forgery_kit", "costume", "fine_clothes"],
        "starting_gold": 15,
    },
    "hermit": {
        "background_id": "bg.hermit",
        "name": "隐士 Hermit",
        "ability_scores": ["con", "wis", "cha"],
        "skill_choices": {"options": ["medicine", "religion"], "choose": 2},
        "tool_choices": {"options": ["herbalism_kit"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.healer"],
        "equipment": ["quarterstaff", "herbalism_kit", "bedroll", "book_philosophy", "lamp", "3_oil", "travelers_clothes"],
        "starting_gold": 16,
    },
    "soldier": {
        "background_id": "bg.soldier",
        "name": "士兵 Soldier",
        "ability_scores": ["str", "dex", "con"],
        "skill_choices": {"options": ["athletics", "intimidation"], "choose": 2},
        "tool_choices": {"options": ["gaming_set_choice"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.savage_attacker"],
        "equipment": ["spear", "shortbow", "20_arrows", "gaming_set", "healers_kit", "quiver", "travelers_clothes"],
        "starting_gold": 14,
    },
    "criminal": {
        "background_id": "bg.criminal",
        "name": "罪犯 Criminal",
        "ability_scores": ["dex", "con", "int"],
        "skill_choices": {"options": ["sleight_of_hand", "stealth"], "choose": 2},
        "tool_choices": {"options": ["thieves_tools"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.alert"],
        "equipment": ["2_daggers", "thieves_tools", "crowbar", "2_pouches", "travelers_clothes"],
        "starting_gold": 16,
    },
    "merchant": {
        "background_id": "bg.merchant",
        "name": "商人 Merchant",
        "ability_scores": ["con", "int", "cha"],
        "skill_choices": {"options": ["animal_handling", "persuasion"], "choose": 2},
        "tool_choices": {"options": ["navigators_tools"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.lucky"],
        "equipment": ["navigators_tools", "2_pouches", "travelers_clothes"],
        "starting_gold": 22,
    },
    "wayfarer": {
        "background_id": "bg.wayfarer",
        "name": "流浪者 Wayfarer",
        "ability_scores": ["dex", "wis", "cha"],
        "skill_choices": {"options": ["insight", "stealth"], "choose": 2},
        "tool_choices": {"options": ["thieves_tools"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.lucky"],
        "equipment": ["2_daggers", "thieves_tools", "gaming_set_any", "bedroll", "2_pouches", "travelers_clothes"],
        "starting_gold": 16,
    },
    "entertainer": {
        "background_id": "bg.entertainer",
        "name": "艺人 Entertainer",
        "ability_scores": ["str", "dex", "cha"],
        "skill_choices": {"options": ["acrobatics", "performance"], "choose": 2},
        "tool_choices": {"options": ["musical_instrument_choice"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.musician"],
        "equipment": ["musical_instrument", "2_costumes", "mirror", "perfume", "travelers_clothes"],
        "starting_gold": 11,
    },
    "noble": {
        "background_id": "bg.noble",
        "name": "贵族 Noble",
        "ability_scores": ["str", "int", "cha"],
        "skill_choices": {"options": ["history", "persuasion"], "choose": 2},
        "tool_choices": {"options": ["gaming_set_choice"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.skilled"],
        "equipment": ["gaming_set", "fine_clothes", "perfume"],
        "starting_gold": 29,
    },
    "farmer": {
        "background_id": "bg.farmer",
        "name": "农民 Farmer",
        "ability_scores": ["str", "con", "wis"],
        "skill_choices": {"options": ["animal_handling", "nature"], "choose": 2},
        "tool_choices": {"options": ["carpenters_tools"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.tough"],
        "equipment": ["sickle", "carpenters_tools", "healers_kit", "iron_pot", "shovel", "travelers_clothes"],
        "starting_gold": 30,
    },
    "sage": {
        "background_id": "bg.sage",
        "name": "智者 Sage",
        "ability_scores": ["con", "int", "wis"],
        "skill_choices": {"options": ["arcana", "history"], "choose": 2},
        "tool_choices": {"options": ["calligrapher_supplies"], "choose": 1},
        "languages": 0,
        "origin_feat_options": ["feat.magic_initiate"],
        "equipment": ["quarterstaff", "calligrapher_supplies", "book_history", "8_parchment", "robe"],
        "starting_gold": 8,
    },
}


def get_background(key: str) -> dict | None:
    """按英文 key 取背景定义"""
    return BACKGROUND_DEFINITIONS.get(key)


def all_background_keys() -> list[str]:
    """返回所有背景 key"""
    return list(BACKGROUND_DEFINITIONS.keys())


def get_background_skills(key: str) -> list[str]:
    """获取背景技能熟练选项"""
    bg = BACKGROUND_DEFINITIONS.get(key)
    if not bg:
        return []
    return bg["skill_choices"]["options"]


def get_background_feat(key: str) -> str:
    """获取背景起源专长"""
    bg = BACKGROUND_DEFINITIONS.get(key)
    if not bg:
        return ""
    opts = bg.get("origin_feat_options", [])
    return opts[0] if opts else ""
