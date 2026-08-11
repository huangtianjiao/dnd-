"""魔法物品可执行定义 — 充能/恢复/效果/激活 (ITEM-004)。

规则依据: DMG 2024 / 玩家手册2024 装备章
每个魔法物品包含: 充能/恢复/效果/激活方式/同调需求。
"""

from __future__ import annotations

from typing import Dict

# ──────────────────────────────────────────────────────────────────────────
# 魔法物品定义表
# ──────────────────────────────────────────────────────────────────────────

MAGIC_ITEMS_EXECUTABLE: Dict[str, dict] = {
    # ── 药水 ─────────────────────────────────────────────────────
    "potion_of_healing": {
        "item_id": "item.potion_healing",
        "name": "治疗药水 Potion of Healing",
        "rarity": "common",
        "charges": 1,
        "consumed_on_use": True,
        "effect": {"type": "heal", "dice": "2d4+2"},
        "activation": "action",
        "requires_attunement": False,
    },
    "potion_of_greater_healing": {
        "item_id": "item.potion_greater_healing",
        "name": "高等治疗药水 Potion of Greater Healing",
        "rarity": "uncommon",
        "charges": 1,
        "consumed_on_use": True,
        "effect": {"type": "heal", "dice": "4d4+4"},
        "activation": "action",
        "requires_attunement": False,
    },
    "potion_of_superior_healing": {
        "item_id": "item.potion_superior_healing",
        "name": "超强治疗药水 Potion of Superior Healing",
        "rarity": "rare",
        "charges": 1,
        "consumed_on_use": True,
        "effect": {"type": "heal", "dice": "8d4+8"},
        "activation": "action",
        "requires_attunement": False,
    },
    "potion_of_supreme_healing": {
        "item_id": "item.potion_supreme_healing",
        "name": "极致治疗药水 Potion of Supreme Healing",
        "rarity": "very_rare",
        "charges": 1,
        "consumed_on_use": True,
        "effect": {"type": "heal", "dice": "10d4+20"},
        "activation": "action",
        "requires_attunement": False,
    },
    "potion_of_fire_resistance": {
        "item_id": "item.potion_fire_resistance",
        "name": "火焰抗性药水 Potion of Fire Resistance",
        "rarity": "uncommon",
        "charges": 1,
        "consumed_on_use": True,
        "effect": {"type": "resistance", "damage_type": "fire", "duration_hours": 1},
        "activation": "action",
        "requires_attunement": False,
    },
    # ── 法杖 / 魔杖 ──────────────────────────────────────────────
    "wand_of_magic_missiles": {
        "item_id": "item.wand_magic_missiles",
        "name": "魔法飞弹魔杖 Wand of Magic Missiles",
        "rarity": "uncommon",
        "charges": 7,
        "recharge": {"type": "daily", "dice": "1d6+1", "recharge_on": "dawn"},
        "effect": {"type": "spell_cast", "spell_id": "magic_missile", "slot_level": 1},
        "activation": "action",
        "requires_attunement": False,
    },
    "wand_of_fireballs": {
        "item_id": "item.wand_fireballs",
        "name": "火球术魔杖 Wand of Fireballs",
        "rarity": "rare",
        "charges": 7,
        "recharge": {"type": "daily", "dice": "1d6+1", "recharge_on": "dawn"},
        "effect": {"type": "spell_cast", "spell_id": "fireball", "slot_level": 3},
        "activation": "action",
        "requires_attunement": False,
    },
    "wand_of_lightning_bolts": {
        "item_id": "item.wand_lightning_bolts",
        "name": "闪电束魔杖 Wand of Lightning Bolts",
        "rarity": "rare",
        "charges": 7,
        "recharge": {"type": "daily", "dice": "1d6+1", "recharge_on": "dawn"},
        "effect": {"type": "spell_cast", "spell_id": "lightning_bolt", "slot_level": 3},
        "activation": "action",
        "requires_attunement": False,
    },
    "staff_of_power": {
        "item_id": "item.staff_of_power",
        "name": "力量法杖 Staff of Power",
        "rarity": "very_rare",
        "charges": 20,
        "recharge": {"type": "daily", "amount": 2, "recharge_on": "dawn"},
        "effect": {"type": "multiple_spells", "spells": ["cone_of_cold", "fireball", "hold_monster", "levitate", "lightning_bolt", "wall_of_force"]},
        "activation": "action",
        "requires_attunement": True,
        "attunement_requires": {"class": ["sorcerer", "warlock", "wizard"]},
    },
    "staff_of_healing": {
        "item_id": "item.staff_of_healing",
        "name": "治疗法杖 Staff of Healing",
        "rarity": "uncommon",
        "charges": 10,
        "recharge": {"type": "daily", "dice": "1d6+4", "recharge_on": "dawn"},
        "effect": {"type": "heal_spell", "spells": ["cure_wounds_1", "cure_wounds_2", "cure_wounds_3", "cure_wounds_4"]},
        "activation": "action",
        "requires_attunement": True,
        "attunement_requires": {"class": ["bard", "cleric", "druid"]},
    },
    # ── 武器 ─────────────────────────────────────────────────────
    "flame_tongue": {
        "item_id": "item.flame_tongue",
        "name": "焰舌剑 Flame Tongue",
        "rarity": "rare",
        "charges": -1,  # 无限
        "effect": {"type": "damage_bonus", "damage_type": "fire", "dice": "2d6", "activation": "bonus_action"},
        "activation": "bonus_action",
        "requires_attunement": True,
    },
    "frost_brand": {
        "item_id": "item.frost_brand",
        "name": "霜之印记 Frost Brand",
        "rarity": "very_rare",
        "charges": -1,
        "effect": {"type": "damage_bonus", "damage_type": "cold", "dice": "1d6", "passive": True,
                   "resistance": "fire"},
        "activation": "passive",
        "requires_attunement": True,
    },
    "vorpal_sword": {
        "item_id": "item.vorpal_sword",
        "name": "斩首剑 Vorpal Sword",
        "rarity": "legendary",
        "charges": -1,
        "effect": {"type": "critical_effect", "damage_type": "slashing", "decapitate_on_nat20": True},
        "activation": "passive",
        "requires_attunement": True,
    },
    "weapon_of_warning": {
        "item_id": "item.weapon_of_warning",
        "name": "警戒武器 Weapon of Warning",
        "rarity": "uncommon",
        "charges": -1,
        "effect": {"type": "passive", "initiative_advantage": True, "surprise_immune": True},
        "activation": "passive",
        "requires_attunement": True,
    },
    # ── 护甲 ─────────────────────────────────────────────────────
    "adamantine_armor": {
        "item_id": "item.adamantine_armor",
        "name": "精金护甲 Adamantine Armor",
        "rarity": "uncommon",
        "charges": -1,
        "effect": {"type": "passive", "critical_to_miss_against": True},
        "activation": "passive",
        "requires_attunement": False,
    },
    "mithral_armor": {
        "item_id": "item.mithral_armor",
        "name": "秘银护甲 Mithral Armor",
        "rarity": "uncommon",
        "charges": -1,
        "effect": {"type": "passive", "no_stealth_disadvantage": True, "no_str_requirement": True},
        "activation": "passive",
        "requires_attunement": False,
    },
    "armor_of_resistance": {
        "item_id": "item.armor_of_resistance",
        "name": "抗性护甲 Armor of Resistance",
        "rarity": "rare",
        "charges": -1,
        "effect": {"type": "passive", "resistance_type": "choice"},
        "activation": "passive",
        "requires_attunement": True,
    },
    "cloak_of_protection": {
        "item_id": "item.cloak_of_protection",
        "name": "防护斗篷 Cloak of Protection",
        "rarity": "uncommon",
        "charges": -1,
        "effect": {"type": "passive", "ac_bonus": 1, "save_bonus": 1},
        "activation": "passive",
        "requires_attunement": True,
    },
    # ── 戒指 / 饰品 ──────────────────────────────────────────────
    "ring_of_protection": {
        "item_id": "item.ring_of_protection",
        "name": "防护戒指 Ring of Protection",
        "rarity": "uncommon",
        "charges": -1,
        "effect": {"type": "passive", "ac_bonus": 1, "save_bonus": 1},
        "activation": "passive",
        "requires_attunement": True,
    },
    "ring_of_invisibility": {
        "item_id": "item.ring_of_invisibility",
        "name": "隐形戒指 Ring of Invisibility",
        "rarity": "legendary",
        "charges": -1,
        "effect": {"type": "action", "spell": "invisibility", "duration": "concentration"},
        "activation": "action",
        "requires_attunement": True,
    },
    "ring_of_regeneration": {
        "item_id": "item.ring_of_regeneration",
        "name": "再生戒指 Ring of Regeneration",
        "rarity": "very_rare",
        "charges": -1,
        "effect": {"type": "passive", "heal_per_round": "1d6", "condition": "hp > 0"},
        "activation": "passive",
        "requires_attunement": True,
    },
    "amulet_of_health": {
        "item_id": "item.amulet_of_health",
        "name": "健康护符 Amulet of Health",
        "rarity": "uncommon",
        "charges": -1,
        "effect": {"type": "passive", "con_set_to": 19},
        "activation": "passive",
        "requires_attunement": True,
    },
    "periapt_of_wound_closure": {
        "item_id": "item.periapt_wound_closure",
        "name": "伤口闭合胸针 Periapt of Wound Closure",
        "rarity": "uncommon",
        "charges": -1,
        "effect": {"type": "passive", "death_save_advantage": True, "healing_doubled": True},
        "activation": "passive",
        "requires_attunement": True,
    },
    # ── 奇物 ─────────────────────────────────────────────────────
    "bag_of_holding": {
        "item_id": "item.bag_of_holding",
        "name": "次元袋 Bag of Holding",
        "rarity": "uncommon",
        "charges": -1,
        "effect": {"type": "passive", "extra_storage": "500 pounds, 64 cubic feet"},
        "activation": "passive",
        "requires_attunement": False,
    },
    "portable_hole": {
        "item_id": "item.portable_hole",
        "name": "便携洞 Portable Hole",
        "rarity": "rare",
        "charges": -1,
        "effect": {"type": "action", "creates": "10ft deep, 6ft diameter hole"},
        "activation": "action",
        "requires_attunement": False,
    },
    "rope_of_climbing": {
        "item_id": "item.rope_of_climbing",
        "name": "攀爬绳 Rope of Climbing",
        "rarity": "uncommon",
        "charges": -1,
        "effect": {"type": "action", "animates": "60ft rope, climbs on command"},
        "activation": "action",
        "requires_attunement": False,
    },
    "cloak_of_elvenkind": {
        "item_id": "item.cloak_of_elvenkind",
        "name": "精灵斗篷 Cloak of Elvenkind",
        "rarity": "uncommon",
        "charges": -1,
        "effect": {"type": "passive", "stealth_advantage": True, "hard_to_see_in_dim": True},
        "activation": "passive",
        "requires_attunement": True,
    },
    "boots_of_elvenkind": {
        "item_id": "item.boots_of_elvenkind",
        "name": "精灵靴 Boots of Elvenkind",
        "rarity": "uncommon",
        "charges": -1,
        "effect": {"type": "passive", "silent_steps": True, "stealth_advantage_on_footsteps": True},
        "activation": "passive",
        "requires_attunement": True,
    },
    "gauntlets_of_ogre_power": {
        "item_id": "item.gauntlets_of_ogre_power",
        "name": "食人魔力护手 Gauntlets of Ogre Power",
        "rarity": "uncommon",
        "charges": -1,
        "effect": {"type": "passive", "str_set_to": 19},
        "activation": "passive",
        "requires_attunement": True,
    },
    "headband_of_intellect": {
        "item_id": "item.headband_of_intellect",
        "name": "智力头环 Headband of Intellect",
        "rarity": "uncommon",
        "charges": -1,
        "effect": {"type": "passive", "int_set_to": 19},
        "activation": "passive",
        "requires_attunement": True,
    },
    "bracers_of_defense": {
        "item_id": "item.bracers_of_defense",
        "name": "防御护腕 Bracers of Defense",
        "rarity": "rare",
        "charges": -1,
        "effect": {"type": "passive", "ac_bonus": 2, "condition": "no_armor"},
        "activation": "passive",
        "requires_attunement": True,
    },
}


def get_magic_item(key: str) -> dict | None:
    """按英文 key 取魔法物品定义"""
    return MAGIC_ITEMS_EXECUTABLE.get(key)


def all_magic_item_keys() -> list[str]:
    """返回所有魔法物品 key"""
    return list(MAGIC_ITEMS_EXECUTABLE.keys())


def get_item_charges(key: str) -> int:
    """获取物品充能数（-1 = 无限）"""
    item = MAGIC_ITEMS_EXECUTABLE.get(key)
    return item.get("charges", -1) if item else -1


def get_item_recharge(key: str) -> dict | None:
    """获取物品恢复规则"""
    item = MAGIC_ITEMS_EXECUTABLE.get(key)
    return item.get("recharge") if item else None


def requires_attunement(key: str) -> bool:
    """判断物品是否需要同调"""
    item = MAGIC_ITEMS_EXECUTABLE.get(key)
    return item.get("requires_attunement", False) if item else False


def get_attunement_requirements(key: str) -> dict | None:
    """获取物品同调先决条件"""
    item = MAGIC_ITEMS_EXECUTABLE.get(key)
    return item.get("attunement_requires") if item else None


def use_charges(key: str, current_charges: int, amount: int = 1) -> dict:
    """使用物品充能。

    返回: {"success": bool, "remaining": int, "consumed": bool}
    """
    item = MAGIC_ITEMS_EXECUTABLE.get(key)
    if not item:
        return {"success": False, "remaining": current_charges, "consumed": False}

    # 无限充物品
    if item.get("charges", -1) == -1:
        return {"success": True, "remaining": -1, "consumed": False}

    # 消耗型物品
    if item.get("consumed_on_use", False):
        return {"success": True, "remaining": 0, "consumed": True}

    # 充能型物品
    if current_charges < amount:
        return {"success": False, "remaining": current_charges, "consumed": False}

    return {"success": True, "remaining": current_charges - amount, "consumed": False}
