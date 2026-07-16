"""从 5echm_web 怪物图鉴2025 自动提取的怪物数据。
共 408 只怪物。
由 scripts/extract_monsters.py 自动生成，请勿手动编辑。
"""

from typing import Any

_MONSTERS_LIST: list[dict[str, Any]] = [
  {
    "name": "半巫妖",
    "en_name": "Demilich",
    "type_line": "微型亡灵，中立邪恶",
    "size": "Tiny",
    "creature_type": "亡灵",
    "alignment": "中立邪恶",
    "ac": 20,
    "initiative_bonus": 17,
    "initiative_total": 27,
    "hp": 180,
    "hp_formula": "72d4",
    "speed": {
      "walk": "5尺，飞行30尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "敏捷": {
        "score": 20,
        "mod": 5,
        "save": 11
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 6
      },
      "智力": {
        "score": 20,
        "mod": 5,
        "save": 11
      },
      "感知": {
        "score": 17,
        "mod": 3,
        "save": 9
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 5
      }
    },
    "damage_resistances": [
      "钝击",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "暗蚀",
      "毒素",
      "心灵"
    ],
    "condition_immunities": [
      "魅惑",
      "耳聋",
      "力竭",
      "恐慌",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "震慑"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 13
    },
    "languages": "无",
    "cr": 18,
    "xp": 20000,
    "pb": 6,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "半巫妖豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      },
      {
        "name": "亡者再生",
        "en_name": "Undead Restoration",
        "description": "若半巫妖被摧毁，除非其遗骸被施展祈愿术Wish，其在1d10天后重获生命并恢复全部生命值，"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "半巫妖发动3次暗能爆裂攻击。"
      },
      {
        "name": "暗能爆裂",
        "en_name": "Necrotic Burst",
        "description": "近战或远程攻击检定：+11，触及5尺或射程120尺。命中：24（7d6）暗蚀伤害。"
      },
      {
        "name": "尖啸",
        "en_name": "Howl",
        "description": "体质豁免检定：DC19，源自半巫妖的30尺光环区域内的每名生物。失败：70（20d6）心灵伤害。失败或成功：目标陷入恐慌状态，直至半巫妖的下个回合开始。",
        "params": "充能5~6"
      }
    ],
    "legendary_actions": [
      {
        "name": "能量汲取",
        "en_name": "Energy Drain",
        "description": "体质豁免检定：DC19，单一120尺内半巫妖可见的生物。失败：目标的生命值上限降低14（4d6）。",
        "max_uses": 3
      },
      {
        "name": "坟土飞扬",
        "en_name": "Grave-Dust Flight",
        "description": "半巫妖飞行至多等于其飞行速度的距离，向周围播撒墓穴之尘。在半巫妖移动过程中，位于半巫妖5尺内的每名生物都会被选为一次以下效应的目标。体质豁免检定：DC19。失败：目标陷入目盲状态，直至半巫妖的下个回合结束。失败或成功：半巫妖直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "腐坏",
        "en_name": "Necrosis",
        "description": "半巫妖发动一次暗能爆裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "亡灵\\半巫妖.htm"
  },
  {
    "name": "尸妖",
    "en_name": "Wight",
    "type_line": "中型亡灵，中立邪恶",
    "size": "Medium",
    "creature_type": "亡灵",
    "alignment": "中立邪恶",
    "ac": 14,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 82,
    "hp_formula": "11d8+33",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 3,
      "隐匿": 4
    },
    "damage_resistances": [
      "暗蚀"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "中毒"
    ],
    "equipment": "镶钉皮甲",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 13
    },
    "languages": "通用语以及一门其他语言",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "日照敏感",
        "en_name": "Sunlight Sensitivity",
        "description": "若尸妖身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "尸妖使用死灵剑或死灵弓发动攻击两次攻击。其可以将其中一次攻击替换为使用吸取生命。"
      },
      {
        "name": "死灵剑",
        "en_name": "Necrotic Sword",
        "description": "近战攻击检定：+4，触及5尺。命中：6（1d8+2）挥砍伤害，外加4（1d8）暗蚀伤害。"
      },
      {
        "name": "死灵弓",
        "en_name": "Necrotic Bow",
        "description": "远程攻击检定：+4，射程150/600尺。命中：6（1d8+2）穿刺伤害，外加4（1d8）暗蚀伤害。"
      },
      {
        "name": "吸取生命",
        "en_name": "Life Drain",
        "description": "体质豁免：DC13，单一5尺内生物。"
      },
      {
        "name": "丧尸",
        "en_name": "Zombie",
        "description": "，除非该生物被复活或其尸体被摧毁。尸妖以此法同时能控制的丧尸数上限为十二。"
      }
    ],
    "source_file": "亡灵\\尸妖.htm"
  },
  {
    "name": "巫妖",
    "en_name": "Lich",
    "type_line": "中型亡灵（法师），中立邪恶",
    "size": "Medium",
    "creature_type": "亡灵（法师）",
    "alignment": "中立邪恶",
    "ac": 20,
    "initiative_bonus": 17,
    "initiative_total": 27,
    "hp": 315,
    "hp_formula": "42d8+126",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 10
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 10
      },
      "智力": {
        "score": 21,
        "mod": 5,
        "save": 12
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 9
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "奥秘": 19,
      "历史": 12,
      "洞悉": 9,
      "察觉": 9
    },
    "damage_resistances": [
      "寒冷",
      "闪电"
    ],
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "麻痹",
      "中毒"
    ],
    "equipment": "材料包",
    "senses": {
      "真实视觉": 120,
      "被动察觉": 19
    },
    "languages": "全部",
    "cr": 21,
    "xp": 33000,
    "pb": 7,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "巫妖豁免失败时，可以将其改为豁免成功。",
        "params": "4/日，或巢穴内5/日"
      },
      {
        "name": "命匣",
        "en_name": "Spirit Jar",
        "description": "只要保有命匣，被摧毁的巫妖就可以在1d10日内重新成型，以满生命值复活。新的躯体将出现在巫妖巢穴内的一处未占据空间。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "巫妖使用魔能迸裂或麻痹之触发动共计三次攻击。"
      },
      {
        "name": "魔能迸裂",
        "en_name": "Eldritch Burst",
        "description": "近战或远程攻击检定：+12，触及5尺或射程120尺。命中：31（4d12+5）力场伤害。"
      },
      {
        "name": "麻痹之触",
        "en_name": "Paralyzing Touch",
        "description": "近战攻击检定：+12，触及5尺。命中：15（3d6+5）寒冷伤害，且目标陷入麻痹状态直至巫妖的下个回合开始。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "巫妖施展以下一道法术，使用智力作为施法属性（法术豁免DC20）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，侦测思想Detect Thoughts，解除魔法Dispel Magic，火球术Fireball（五环版本），    隐形术Invisibility，闪电束Lightning Bolt（五环版本），    法师之手Mage Hand，魔法伎俩Prestidigitation"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "活化死尸Animate Dead，任意门Dimension Door，位面转移Plane Shift"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "连锁闪电Chain Lightning，死亡一指Finger of Death，律令死亡Power Word Kill，探知术Scrying"
      }
    ],
    "reactions": [
      {
        "name": "护身魔法",
        "en_name": "Protective Magic",
        "description": "巫妖施展法术反制Counterspell或护盾术Shield（触发条件见这些法术），使用与施法动作相同的施法属性。"
      }
    ],
    "legendary_actions": [
      {
        "name": "蚀命传送",
        "en_name": "Deathly Teleport",
        "description": "巫妖传送至多60尺至一处其可见的未占据空间，位于其离开的空间10尺内的每名生物受到11（2d10）暗蚀伤害。",
        "max_uses": 3
      },
      {
        "name": "扰乱生命",
        "en_name": "Disrupt Life",
        "description": "体质豁免检定：DC20，源自巫妖的20尺光环区域内的每名非亡灵生物。失败：31（9d6）暗蚀伤害。成功：半伤。失败或成功：巫妖直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "恐惧凝视",
        "en_name": "Frightful Gaze",
        "description": "巫妖施展恐惧术Fear，使用与施法动作相同的施法属性。巫妖直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      }
    ],
    "source_file": "亡灵\\巫妖.htm"
  },
  {
    "name": "幽影",
    "en_name": "Shadow",
    "type_line": "中型亡灵，混乱邪恶",
    "size": "Medium",
    "creature_type": "亡灵",
    "alignment": "混乱邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 27,
    "hp_formula": "5d8+5",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "隐匿": 6
    },
    "damage_vulnerabilities": [
      "光耀"
    ],
    "damage_resistances": [
      "强酸",
      "寒冷",
      "火焰",
      "闪电",
      "雷鸣"
    ],
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "恐慌",
      "受擒",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚",
      "昏迷"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "无",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "无定形",
        "en_name": "Amorphous",
        "description": "幽影可以移动穿过最窄1寸宽的空间而无需消耗额外的移动力。"
      },
      {
        "name": "日照弱点",
        "en_name": "Sunlight Weakness",
        "description": "若幽影身处阳光下，其进行的D20检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "汲命击",
        "en_name": "Draining Swipe",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）暗蚀伤害。且目标的力量值降低1d4。若目标的力量值以此法降至0，则其立即死亡。若一名类人生物死于该攻击，则一只幽影在1d4小时后从其尸体上唤起。"
      }
    ],
    "bonus_actions": [
      {
        "name": "幽影隐匿",
        "en_name": "Shadow Stealth",
        "description": "若幽影身处微光光照或黑暗，其执行躲藏动作。"
      }
    ],
    "source_file": "亡灵\\幽影.htm"
  },
  {
    "name": "幽魂",
    "en_name": "Ghost",
    "type_line": "中型亡灵，中立",
    "size": "Medium",
    "creature_type": "亡灵",
    "alignment": "中立",
    "ac": 11,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 45,
    "hp_formula": "10d8",
    "speed": {
      "walk": "5尺，飞行40尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 17,
        "mod": 3,
        "save": 3
      }
    },
    "damage_resistances": [
      "强酸",
      "钝击",
      "寒冷",
      "火焰",
      "闪电",
      "穿刺",
      "挥砍",
      "雷鸣"
    ],
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "受擒",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "通用语，以及一门其他语言",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "traits": [
      {
        "name": "以太视界",
        "en_name": "Ethereal Sight",
        "description": "若幽魂身处物质位面，其能够看见60尺内的以太位面。"
      },
      {
        "name": "虚体移动",
        "en_name": "Incorporeal Movement",
        "description": "幽魂可以移动穿过其他生物或物件，如同穿过困难地形一般。在其回合结束时，若幽魂还处于物件内，其受到5（1d10）力场伤害"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "幽魂发动两次凋零之触攻击。"
      },
      {
        "name": "凋零之触",
        "en_name": "Withering Touch",
        "description": "近战攻击检定：+5，触及5尺。命中：19（3d10+3）暗蚀伤害。"
      },
      {
        "name": "以太化",
        "en_name": "Etherealness",
        "description": "幽魂施展法术以太化Etheralness，无需法术成分，并使用魅力作为施法属性。当幽魂处于边界以太时，仍可以在物质位面被观测到，反之亦然。但另一位面的任何事物不能对其施加影响或被其影响。"
      },
      {
        "name": "恐惧面容",
        "en_name": "Horrifying Visage",
        "description": "魅力豁免：DC13，60尺锥状区域内能看见幽魂的每名非亡灵生物。失败：10（2d6+3）心灵伤害，目标陷入恐慌状态，直至幽魂的下个回合的开始。成功：目标在24小时内免疫此幽魂的恐惧面容。"
      },
      {
        "name": "附身",
        "en_name": "Possession",
        "description": "魅力豁免：DC13，单一5尺内幽魂可见的类人生物。\n失败：目标被幽魂附身。幽魂消失，目标陷入失能 \n状态并失去对身体的控制。现在由幽魂控制身体，但目标仍然保留自我意识。幽魂不能成为任意攻击、法术或其他效应的目标，针对亡灵的效应除外。幽魂仍然保留自己的游戏数据，但是使用附身目标的速度，以及力量、敏捷与体质调整值。",
        "params": "充能6"
      }
    ],
    "source_file": "亡灵\\幽魂.htm"
  },
  {
    "name": "恶灵",
    "en_name": "Specter",
    "type_line": "中型亡灵，混乱邪恶",
    "size": "Medium",
    "creature_type": "亡灵",
    "alignment": "混乱邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 22,
    "hp_formula": "5d8",
    "speed": {
      "walk": "30尺，飞行50尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "damage_resistances": [
      "强酸",
      "钝击",
      "寒冷",
      "火焰",
      "闪电",
      "穿刺",
      "挥砍",
      "雷鸣"
    ],
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "受擒",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚",
      "昏迷"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "理解通用语以及一门其他语言，但不会说",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "虚体移动",
        "en_name": "Incorporeal Movement",
        "description": "恶灵可以移动穿过其他生物或物件，如同穿过困难地形一般。在其回合结束时，若恶灵还处于物件内，其受到5（1d10）力场伤害"
      },
      {
        "name": "日照敏感",
        "en_name": "Sunlight Sensitivity",
        "description": "若恶灵身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "吸取生命",
        "en_name": "Life Drain",
        "description": "近战攻击检定：+4，触及5尺。命中：7（2d6）暗蚀伤害。若目标为生物，目标的生命值上限减少等于其受到伤害的数值。"
      }
    ],
    "source_file": "亡灵\\恶灵.htm"
  },
  {
    "name": "报丧妖",
    "en_name": "Banshee",
    "type_line": "中型亡灵，混乱邪恶",
    "size": "Medium",
    "creature_type": "亡灵",
    "alignment": "混乱邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 54,
    "hp_formula": "12d8",
    "speed": {
      "walk": "5尺，飞行40尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 17,
        "mod": 3,
        "save": 3
      }
    },
    "damage_resistances": [
      "强酸",
      "钝击",
      "火焰",
      "闪电",
      "穿刺",
      "挥砍",
      "雷鸣"
    ],
    "damage_immunities": [
      "寒冷",
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "受擒",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "通用语，精灵语",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "traits": [
      {
        "name": "侦测生命",
        "en_name": "Detect Life",
        "description": "报丧妖可以魔法性地感知到其1里之内非亡灵非构装生物的位置。"
      },
      {
        "name": "虚体移动",
        "en_name": "Incorporeal Movement",
        "description": "报丧妖可以移动穿过其他生物或物件，如同穿过困难地形一般。在其回合结束时，若报丧妖还处于物件内，其受到5（1d10）力场伤害"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "报丧妖发动两次腐化触击攻击。"
      },
      {
        "name": "腐化触击",
        "en_name": "Corrupting Touch",
        "description": "近战攻击检定：+5，触及5尺。命中：7（1d8+3）暗蚀伤害。"
      },
      {
        "name": "恐惧",
        "en_name": "Horrifying",
        "description": "感知豁免检定：DC13，单一60尺内报丧妖可见且能看见其的生物。失败：目标陷入恐慌状态，直至报丧妖的下个回合开始。成功：目标在24小时内免疫此报丧妖的恐惧。"
      },
      {
        "name": "死亡哀嚎",
        "en_name": "Deathly Wail",
        "description": "若报丧妖未身处阳光下，其发出一阵悲恸的哀嚎。体质豁免检定：DC13，30尺内能听到哀嚎的非亡灵且非构装的每名生物。失败：若目标的生命值为25或更低，其生命值降至0；否则，目标受到10（3d6）心灵伤害。",
        "params": "1/日"
      }
    ],
    "source_file": "亡灵\\报丧妖.htm"
  },
  {
    "name": "燃焰之颅",
    "en_name": "Flameskull",
    "type_line": "微型亡灵，中立邪恶",
    "size": "Tiny",
    "creature_type": "亡灵",
    "alignment": "中立邪恶",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 40,
    "hp_formula": "9d4+18",
    "speed": {
      "walk": "5尺，飞行40尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "奥秘": 5,
      "察觉": 2
    },
    "damage_immunities": [
      "火焰",
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "麻痹",
      "中毒",
      "倒地"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 12
    },
    "languages": "通用语以及两门其他语言",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "traits": [
      {
        "name": "照明",
        "en_name": "Illumination",
        "description": "燃焰之颅散发出半径15尺明亮光照以及额外15尺的微光光照。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "燃焰之颅对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "不死再造",
        "en_name": "Undead Restoration",
        "description": "若燃焰之颅被摧毁，其在1小时后恢复所有生命值，除非对其残骸泼洒圣水或施展驱逐善恶Dispel Evil \nand Good。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "燃焰之颅发动两次火焰射线攻击。"
      },
      {
        "name": "火焰射线",
        "en_name": "Fire Ray",
        "description": "近战或远程攻击检定：+5，触及5尺，或射程60尺。命中：13（3d6+3）火焰伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "燃焰之颅施展以下一道法术，无需姿势或材料成分并使用智力作为施法属性（法术豁免DC13）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "法师之手Mage Hand"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "魔法飞弹Magic Missile（二环版本）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "火球术Fireball"
      }
    ],
    "source_file": "亡灵\\燃焰之颅.htm"
  },
  {
    "name": "邪灵",
    "en_name": "Wraith",
    "type_line": "中型或小型亡灵，混乱邪恶",
    "size": "Medium",
    "creature_type": "或小型亡灵",
    "alignment": "混乱邪恶",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 67,
    "hp_formula": "9d8+27",
    "speed": {
      "walk": "5尺，飞行60尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "damage_resistances": [
      "强酸",
      "钝击",
      "寒冷",
      "火焰",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "受擒",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚",
      "昏迷"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 12
    },
    "languages": "通用语以及两门其他语言",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "虚体移动",
        "en_name": "Incorporeal Movement",
        "description": "邪灵可以移动穿过其他生物或物件，如同穿过困难地形一般。在其回合结束时，若邪灵还处于物件内，其受到5（1d10）力场伤害"
      },
      {
        "name": "日照敏感",
        "en_name": "Sunlight Sensitivity",
        "description": "若邪灵身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "吸取生命",
        "en_name": "Life Drain",
        "description": "近战攻击检定：+6，触及5尺。命中：21（4d8+3）暗蚀伤害。若目标为生物，其生命值上限减少等于其受到伤害的数值。"
      },
      {
        "name": "生成恶灵",
        "en_name": "Create Specter",
        "description": "邪灵指定10尺内一具死亡不超过1分钟的类人生物尸体为目标。目标的灵体将被复生为一个恶灵Specter出现在尸体所处的空间或最近的一处未占据空间。恶灵受邪灵的控制，邪灵以此发同时能控制的恶灵数上限为七。"
      }
    ],
    "source_file": "亡灵\\邪灵.htm"
  },
  {
    "name": "食尸水鬼",
    "en_name": "Lacedon Ghoul",
    "type_line": "中型亡灵，混乱邪恶",
    "size": "Medium",
    "creature_type": "亡灵",
    "alignment": "混乱邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 22,
    "hp_formula": "5d8",
    "speed": {
      "walk": "30尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "damage_resistances": [
      "寒冷"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "通用语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "食尸鬼发动两次阴寒啃咬攻击。"
      },
      {
        "name": "阴寒啃咬",
        "en_name": "Icy Bite",
        "description": "近战攻击检定：+4，触及5尺。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+4，触及5尺。命中：4（1d4+2）挥砍伤害。如果目标为非亡灵生物或非精灵，其承受下述效应。体质豁免检定：DC10。失败：目标陷入麻痹状态，直至其下个回合的结束。"
      }
    ],
    "bonus_actions": [
      {
        "name": "蹿腾水中",
        "en_name": "Watery Rush",
        "description": "若身处水中，食尸鬼移动至多等于其游泳速度一半的距离，且不会引发借机攻击。"
      }
    ],
    "source_file": "亡灵\\食尸水鬼.htm"
  },
  {
    "name": "骚灵",
    "en_name": "Poltergeist",
    "type_line": "中型或小型亡灵，混乱中立",
    "size": "Medium",
    "creature_type": "或小型亡灵",
    "alignment": "混乱中立",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 22,
    "hp_formula": "5d8",
    "speed": {
      "walk": "5尺，飞行50尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "damage_resistances": [
      "强酸",
      "钝击",
      "寒冷",
      "火焰",
      "闪电",
      "穿刺",
      "挥砍",
      "雷鸣"
    ],
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "受擒",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚",
      "昏迷"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "通用语以及一门其他语言",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "虚体移动",
        "en_name": "Incorporeal Movement",
        "description": "骚灵可以移动穿过其他生物或物件，如同穿过困难地形一般。在其回合结束时，若骚灵还处于物件内，其受到5（1d10）力场伤害"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "骚灵发动一次掷物猛击攻击，并使用一次念力猛推。"
      },
      {
        "name": "掷物猛击",
        "en_name": "Object Slam",
        "description": "近战或远程攻击检定：+4，触及5尺或射程30尺。命中：7（2d4+2）钝击伤害。"
      },
      {
        "name": "念力猛推",
        "en_name": "Telekinetic Thrust",
        "description": "力量豁免：DC12，单一30尺内骚灵可见的生物。失败：9（2d6+2）力场伤害，且骚灵将目标推离至多30尺。"
      }
    ],
    "bonus_actions": [
      {
        "name": "消失",
        "en_name": "Vanish",
        "description": "骚灵获得隐形状态，或将之解除。"
      }
    ],
    "source_file": "亡灵\\骚灵.htm"
  },
  {
    "name": "鬼火Will-o’-",
    "en_name": "Wisp",
    "type_line": "微型亡灵，混乱邪恶",
    "size": "Tiny",
    "creature_type": "亡灵",
    "alignment": "混乱邪恶",
    "ac": 19,
    "initiative_bonus": 9,
    "initiative_total": 19,
    "hp": 27,
    "hp_formula": "11d4",
    "speed": {
      "walk": "5尺，飞行50尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "敏捷": {
        "score": 28,
        "mod": 9,
        "save": 9
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "damage_resistances": [
      "强酸",
      "钝击",
      "寒冷",
      "火焰",
      "暗蚀",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "闪电",
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "受擒",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚",
      "昏迷"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 12
    },
    "languages": "通用语以及一门其他语言",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "转瞬即逝",
        "en_name": "Ephemeral",
        "description": "鬼火无法着装或携带任何东西。"
      },
      {
        "name": "照明",
        "en_name": "Illumination",
        "description": "鬼火散发出半径20尺明亮光照以及额外20尺的微光光照。"
      },
      {
        "name": "虚体移动",
        "en_name": "Incorporeal Movement",
        "description": "鬼火可以移动穿过其他生物或物件，如同穿过困难地形一般。在其回合结束时，若鬼火还处于物件内，其受到5（1d10）力场伤害"
      }
    ],
    "actions": [
      {
        "name": "电击",
        "en_name": "Shock",
        "description": "近战攻击检定：+4，触及5尺。命中：11（2d8+2）闪电伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "摄食生命",
        "en_name": "Consume Life",
        "description": "体质豁免：DC10，单一5尺内鬼火可见的生命值为0的生物。\n失败：目标死亡，鬼火恢复10（3d6）生命值。"
      },
      {
        "name": "消失",
        "en_name": "Vanish",
        "description": "鬼火及其光照获得隐形状态，持续至其专注终止。隐形状态在鬼火发动攻击或使用摄食生命后立即结束。"
      }
    ],
    "source_file": "亡灵\\鬼火.htm"
  },
  {
    "name": "龙巫妖",
    "en_name": "Dracolich",
    "type_line": "巨型或超巨型亡灵，守序邪恶",
    "size": "Huge",
    "creature_type": "或超巨型亡灵",
    "alignment": "守序邪恶",
    "ac": 20,
    "initiative_bonus": 12,
    "initiative_total": 22,
    "hp": 225,
    "hp_formula": "18d12+108",
    "speed": {
      "walk": "40尺，掘穴30尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 6
      },
      "体质": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "智力": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 8
      },
      "魅力": {
        "score": 21,
        "mod": 5,
        "save": 5
      }
    },
    "skills": {
      "察觉": 14,
      "隐匿": 6
    },
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "麻痹",
      "中毒"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 24
    },
    "languages": "通用语，龙语",
    "cr": 17,
    "xp": 18000,
    "pb": 6,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "龙巫妖豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      },
      {
        "name": "生机抑止",
        "en_name": "Life Suppression",
        "description": "位于龙巫妖60尺内的生物无法恢复生命值。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "龙巫妖对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "灵魂宝石",
        "en_name": "Soul Gem",
        "description": "龙巫妖拥有一颗魔法宝石。若龙巫妖被摧毁时，这颗宝石与其位于同一存在位面，则龙巫妖在1d20日内获得一具新的身体，恢复其全部生命值并出现在宝石5尺内。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "龙巫妖发动三次撕裂攻击。其可以将其中一次攻击替换为使用施法施展致病射线Ray \nof Sickness  （二环版本）。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+13，触及10尺。命中：18（2d10+7）挥砍伤害外加4（1d8）暗蚀伤害。"
      },
      {
        "name": "暗蚀吐息",
        "en_name": "Necrotic Breath",
        "description": "体质豁免检定：DC20，60尺锥状区域内的每名生物。失败：52（8d12）暗蚀伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "龙巫妖施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC19，法术攻击命中+11）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，致病射线Ray of Sickness（二环版本）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "唤起亡灵Create Undead（八环版本）， 死亡一指Finger of Death"
      }
    ],
    "legendary_actions": [
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "龙巫妖移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      },
      {
        "name": "灾疫射线",
        "en_name": "Sickening Ray",
        "description": "龙巫妖使用施法施展致病射线Ray of \nSickness  （二环版本）。此后龙巫妖不能再执行此动作，直至其下一回合开始。",
        "max_uses": 3
      },
      {
        "name": "骇惧威仪",
        "en_name": "Terrifying Presence",
        "description": "感知豁免检定：DC19，源自龙巫妖的30尺光环区域内的每名生物。失败：11（2d10）心灵伤害，且目标陷入恐慌状态直至其下个回合结束。失败或成功：龙巫妖直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      }
    ],
    "source_file": "亡灵\\龙巫妖.htm"
  },
  {
    "name": "水诡",
    "en_name": "Water Weird",
    "type_line": "大型元素，中立",
    "size": "Large",
    "creature_type": "元素",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 65,
    "hp_formula": "10d10+10",
    "speed": {
      "walk": "5尺，游泳60尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "damage_resistances": [
      "火焰"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "力竭、受擒、麻痹、石化、中毒、倒地、束缚、昏迷"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 10
    },
    "languages": "理解原初语，但不会说",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "水融一体",
        "en_name": "Invisible in Water",
        "description": "若完全浸入水中，水诡处于隐形状态。"
      },
      {
        "name": "水体绑定",
        "en_name": "Water Bound",
        "description": "水诡与某处水体绑定，若水诡离开了那处水体或是那处水体被摧毁，水诡死亡。"
      }
    ],
    "actions": [
      {
        "name": "浪涌",
        "en_name": "Surge",
        "description": "近战攻击检定：+5，触及10尺。命中：13（3d6+3）点寒冷伤害。若目标生物体型不超过中型，则其陷入受擒状态（逃脱DC13），且目标陷入束缚状态，直至擒抱结束。"
      }
    ],
    "source_file": "元素\\水诡.htm"
  },
  {
    "name": "火童",
    "en_name": "Magmin",
    "type_line": "小型元素, 混乱中立",
    "size": "Small",
    "creature_type": "元素, 混乱中立",
    "alignment": "",
    "ac": 14,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 13,
    "hp_formula": "3d6+3",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "原初语（火族语）",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "自爆",
        "en_name": "Death Burst",
        "description": "火童在死亡时爆炸。敏捷豁免检定：DC11，源自火童的10尺光环区域内的每名生物。失败：7（2d6）点火焰伤害。成功：半伤。"
      }
    ],
    "actions": [
      {
        "name": "触碰",
        "en_name": "Touch",
        "description": "近战攻击检定：+4，触及5尺。"
      }
    ],
    "bonus_actions": [
      {
        "name": "燃火照明",
        "en_name": "Ignited Illumination",
        "description": "火童让自己变得炽热或是熄灭自己的火焰。变得炽热期间，火童散发出半径10尺的明亮光照以及额外10尺的微光光照"
      }
    ],
    "source_file": "元素\\火童.htm"
  },
  {
    "name": "石人",
    "en_name": "Galeb Duhr",
    "type_line": "中型元素, 中立",
    "size": "Medium",
    "creature_type": "元素, 中立",
    "alignment": "",
    "ac": 16,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 123,
    "hp_formula": "13d8+65",
    "speed": {
      "walk": "15尺（滚动时30尺, 滚动下坡则60尺）"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑、力竭、恐慌、麻痹、石化、中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "原初语（土族语）",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "actions": [
      {
        "name": "岩崩猛击",
        "en_name": "Avalanche Slam",
        "description": "近战攻击检定：+8，触及5尺命中：12（2d6 + 5）点钝击伤害。若石人在此次攻击前立即向着目标直线移动了30+尺，且目标生物体型不超过大型，则额外受到7（2d6）点钝击伤害并陷入倒地状态。"
      },
      {
        "name": "活化石头",
        "en_name": "Animate Boulders",
        "description": "石人用魔法活化60尺内其可见的至多两块大石头boulder。每块被活化的石头均使用石人Galeb \nDuhr的数据，的数据卡，但有以下区别：石头的智力和魅力值为1且无法说话，并缺少活化石头动作。石头服从石人的命令，使用与石人一样的先攻并在其回合结束后立即执行回合。石头的活化持续1分钟，或在以下情况提前结束：其死亡时、该石人死亡时。",
        "params": "1/日"
      }
    ],
    "source_file": "元素\\石人.htm"
  },
  {
    "name": "石像鬼",
    "en_name": "Gargoyle",
    "type_line": "中型元素，混乱邪恶",
    "size": "Medium",
    "creature_type": "元素",
    "alignment": "混乱邪恶",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 67,
    "hp_formula": "9d8+27",
    "speed": {
      "walk": "30尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "隐匿": 4
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "石化",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "原初语（土族语）",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "飞掠",
        "en_name": "Flyby",
        "description": "石像鬼飞行离开敌人的触及范围时不会引发借机攻击。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "石像鬼发动两次爪击攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+4，触及5尺。命中：7（2d4+2）挥砍伤害。"
      }
    ],
    "source_file": "元素\\石像鬼.htm"
  },
  {
    "name": "石鼎兽",
    "en_name": "Xorn",
    "type_line": "中型元素生物，中立",
    "size": "Medium",
    "creature_type": "元素生物",
    "alignment": "中立",
    "ac": 19,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 84,
    "hp_formula": "8d8+48",
    "speed": {
      "walk": "20尺、掘穴20尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 6
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "麻痹、石化、中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 16
    },
    "languages": "原初语（土族语）",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "遁地",
        "en_name": "Earth Glide",
        "description": "石鼎兽可以掘穴穿过非魔法且未经加工的泥土及岩石。遁地期间，石鼎兽不会破坏其穿过的任何材质。"
      },
      {
        "name": "财宝感知",
        "en_name": "Treasure Sense",
        "description": "石鼎兽可以定位其60尺内贵金属与贵重岩石的位置。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "石鼎兽发动一次啃咬攻击与三次爪攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+6，触及5尺。命中：17（4d6+3）点穿刺伤害。"
      },
      {
        "name": "爪",
        "en_name": "Claw",
        "description": "近战攻击检定：+6，触及5尺。命中：8（1d10+3）点挥砍伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "冲锋",
        "en_name": "Charge",
        "description": "石鼎兽向一名其可以感知的敌人直线移动至多等于其速度或掘穴速度的距离。"
      }
    ],
    "source_file": "元素\\石鼎兽.htm"
  },
  {
    "name": "隐形追猎者",
    "en_name": "Invisible Stalker",
    "type_line": "大型元素生物，中立",
    "size": "Large",
    "creature_type": "元素生物",
    "alignment": "中立",
    "ac": 14,
    "initiative_bonus": 7,
    "initiative_total": 22,
    "hp": 97,
    "hp_formula": "13d10+26",
    "speed": {
      "walk": "50尺、飞行50尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 8
    },
    "damage_resistances": [
      "钝击、穿刺、挥砍"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "力竭、受擒、麻痹、石化、中毒、倒地、束缚、昏迷"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 18
    },
    "languages": "通用语、原初语（气族）",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "traits": [
      {
        "name": "空气形态",
        "en_name": "Air Form",
        "description": "追猎者可以进入并停留在一名敌人所处的空间。其可以移动穿过最窄1寸宽的空间而无需消耗额外的移动力。"
      },
      {
        "name": "隐形",
        "en_name": "Invisibility",
        "description": "追猎者处于隐形状态。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "追猎者发动两次风袭攻击。其可以将其中一次攻击替换为使用涡流。"
      },
      {
        "name": "风袭",
        "en_name": "Wind Swipe",
        "description": "近战攻击检定：命中+7，触及5尺。\n命中：11（2d6+4）力场伤害。"
      },
      {
        "name": "涡流",
        "en_name": "Vortex",
        "description": "体质豁免检定：DC14，单一位于追猎者空间内体型不超过大型的生物。\n失败：7（1d8+3）雷鸣伤害，且目标陷入受擒状态（逃脱DC13）。目标无法施展需要言语成分的法术，且在追猎者的回合开始时受到7（2d6）雷鸣伤害，直至擒抱结束。"
      }
    ],
    "source_file": "元素\\隐形追猎者.htm"
  },
  {
    "name": "兽主",
    "en_name": "Animal Lord",
    "type_line": "中型天族，中立",
    "size": "Medium",
    "creature_type": "天族",
    "alignment": "中立",
    "ac": 19,
    "initiative_bonus": 19,
    "initiative_total": 29,
    "hp": 323,
    "hp_formula": "34d8+170",
    "speed": {
      "walk": "60尺，飞行60尺（悬浮），游泳60尺"
    },
    "abilities": {
      "力量": {
        "score": 24,
        "mod": 7,
        "save": 7
      },
      "敏捷": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 11
      },
      "智力": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 23,
        "mod": 6,
        "save": 12
      },
      "魅力": {
        "score": 22,
        "mod": 6,
        "save": 6
      }
    },
    "skills": {
      "特技": 13,
      "运动": 13,
      "察觉": 18,
      "隐匿": 13
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "暗蚀",
      "心灵",
      "光耀"
    ],
    "damage_immunities": [
      "魅惑",
      "恐慌",
      "震慑"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 28
    },
    "languages": "全部",
    "cr": 20,
    "xp": 25000,
    "pb": 6,
    "traits": [
      {
        "name": "万兽之主",
        "en_name": "Animal Lordship",
        "description": "兽主代表着觅兽、猎兽、睿兽中的一种（由DM选择），这会决定此数据卡中的特定特质。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "兽主豁免失败时，可以将其改为豁免成功。",
        "params": "4/日"
      },
      {
        "name": "兽主威仪",
        "en_name": "Lordly Presence",
        "description": "感知豁免检定：DC20，在源自兽主的30尺光环区域内开始其回合的任意敌人。失败：目标承受以下一道效应："
      },
      {
        "name": "迷醉",
        "en_name": "Captivated",
        "description": "目标陷入魅惑状态直至其下个回合结束。魅惑期间，目标陷入失能状态。",
        "params": "仅觅兽"
      },
      {
        "name": "畏惧",
        "en_name": "Fearful",
        "description": "目标陷入恐慌状态直至其下个回合结束。",
        "params": "仅猎兽"
      },
      {
        "name": "困扰",
        "en_name": "Mired",
        "description": "目标受到10（3d6）心灵伤害，且被魔法所扰乱直至其下个回合结束。被扰乱期间，目标进行的豁免检定承受1d4减值。",
        "params": "仅睿兽"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "兽主对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "兽主使用撕裂或光耀射线发动共计两次攻击，并使用兽灵之力。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+13，触及5尺。命中：14（2d6+7）挥砍伤害外加7（2d6）力场伤害。"
      },
      {
        "name": "光耀射线",
        "en_name": "Radiant Ray",
        "description": "远程攻击检定：+12，射程120尺。命中：20（4d6+6）光耀伤害。"
      },
      {
        "name": "兽灵之力",
        "en_name": "Animal Spirit",
        "description": "兽主咒唤一道兽之灵体，袭向一名生物并随即消失。敏捷豁免检定：DC20，单一120尺内兽主可见的生物。失败：28（4d10+6）光耀伤害。成功：半伤。失败或成功：出现以下一道效应："
      },
      {
        "name": "卫戍之力",
        "en_name": "Fortify",
        "description": "兽主获得20临时生命值。",
        "params": "仅觅兽"
      },
      {
        "name": "标定猎物",
        "en_name": "Marked as \nPrey",
        "description": "兽主对目标进行的攻击检定具有优势，直至兽主的下个回合开始。",
        "params": "仅猎兽"
      },
      {
        "name": "恼人兽群",
        "en_name": "Pesky \nSwarm",
        "description": "目标进行攻击检定和属性检定时具有劣势，直至其下个回合结束。",
        "params": "仅睿兽"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "兽主施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC20）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "化兽为友Animal Friendship，动物信使Animal Messenger，动物交谈Speak with Animals"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "启蒙术Awaken，高等复原术Greater Restoration"
      },
      {
        "name": "每项1/日（仅睿兽）：",
        "en_name": "",
        "description": "动物形态Animal \nShapes，阳炎爆Sunburst"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "兽主变形为其所代表的动物的巨型或更小的版本，或是中型或小型的类人，或是变回其真实形态。除体型以外，其各形态下游戏数据均相同。兽主着装或携带的任何装备都不会随之变化。"
      }
    ],
    "legendary_actions": [
      {
        "name": "野性打击",
        "en_name": "Feral Strike",
        "description": "兽主移动至多等于其速度的距离且不会引发借机攻击，并发动一次撕裂攻击。",
        "max_uses": 3
      },
      {
        "name": "光耀打击",
        "en_name": "Radiant Strike",
        "description": "兽主发动一次光耀射线攻击",
        "max_uses": 3
      }
    ],
    "source_file": "天族\\兽主.htm"
  },
  {
    "name": "天马",
    "en_name": "Pegasus",
    "type_line": "大型天族，混乱善良",
    "size": "Large",
    "creature_type": "天族",
    "alignment": "混乱善良",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 59,
    "hp_formula": "7d10+21",
    "speed": {
      "walk": "60尺，飞行90尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 4
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 5
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 4
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 3
      }
    },
    "skills": {
      "察觉": 6
    },
    "senses": {
      "被动察觉": 16
    },
    "languages": "理解天界语、通用语、精灵语和木族语，但不会说",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "蹄击",
        "en_name": "Hooves",
        "description": "近战攻击检定：+6，触及5尺。命中：7（1d6+4）钝击伤害外加5（2d4）光耀伤害。"
      }
    ],
    "source_file": "天族\\天马.htm"
  },
  {
    "name": "独角兽",
    "en_name": "Unicorn",
    "type_line": "大型天族，守序善良",
    "size": "Large",
    "creature_type": "天族",
    "alignment": "守序善良",
    "ac": 12,
    "initiative_bonus": 8,
    "initiative_total": 18,
    "hp": 97,
    "hp_formula": "13d10+26",
    "speed": {
      "walk": "50尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "麻痹",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 13
    },
    "languages": "天界语，精灵语，木族语；心灵感应120尺",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "独角兽豁免失败时，可以将其改为豁免成功。",
        "params": "3/日"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "独角兽对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "独角兽发动一次蹄击攻击和一次光耀角击攻击。"
      },
      {
        "name": "蹄击",
        "en_name": "Hooves",
        "description": "近战攻击检定：+7，触及5尺。命中：11（2d6+4）钝击伤害。"
      },
      {
        "name": "光耀角击",
        "en_name": "Radiant Horn",
        "description": "近战攻击检定：+7，触及5尺。命中：9（1d10+4）光耀伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "独角兽施展以下一道法术，无需法术成分并使用魅力作为施法属性（法术豁免DC14）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测善恶Detect Evil and Good，德鲁伊伎俩Druidcraft"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "安定心神Calm Emotion，驱逐善恶Dispel Evil and Good，纠缠术Entangle，行动无踪Pass without Trace，回返真言Word of Recall"
      }
    ],
    "bonus_actions": [
      {
        "name": "独角兽祝福",
        "en_name": "Unicorn",
        "description": "独角兽使用其角触碰另一生物并对该生物施展疗伤术Cure Wounds或次等复原术Lesser Restoration，使用与施法动作相同的施法属性。"
      }
    ],
    "legendary_actions": [
      {
        "name": "冲锋角击",
        "en_name": "Charging Horn",
        "description": "独角兽移动至多等于其速度一半的距离且不会引发借机攻击，并发动一次光耀角击攻击。",
        "max_uses": 3
      },
      {
        "name": "闪光护盾",
        "en_name": "Shimmering Shield",
        "description": "独角兽以自身或单一其60尺内其可见的生物为目标。目标获得10（3d6）临时生命值，且其AC提升2直至独角兽的下个回合结束。独角兽直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      }
    ],
    "source_file": "天族\\独角兽.htm"
  },
  {
    "name": "羽蛇",
    "en_name": "Couatl",
    "type_line": "中型天族，守序善良",
    "size": "Medium",
    "creature_type": "天族",
    "alignment": "守序善良",
    "ac": 19,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 60,
    "hp_formula": "8d8+24",
    "speed": {
      "walk": "30尺，飞行90尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 5
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 20,
        "mod": 5,
        "save": 7
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "damage_resistances": [
      "钝击",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "心灵",
      "光耀"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 15
    },
    "languages": "全部；心灵感应120尺",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "traits": [
      {
        "name": "心灵防护",
        "en_name": "Shielded Mind",
        "description": "羽蛇的思想无法以任何方式被探测，并且其他生物仅有在羽蛇允许的情况下才能通过心灵感应与其交流。"
      }
    ],
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+7，触及5尺。\n命中：11（1d12+5）穿刺伤害，且目标陷入中毒状态，持续至羽蛇的下个回合结束。"
      },
      {
        "name": "绞缠",
        "en_name": "Constrict",
        "description": "力量豁免检定：DC15，单一5尺内羽蛇可见的不超过中型的生物。\n失败： 8（1d6+5）钝击伤害。目标陷入受擒状态（逃脱DC13），且目标陷入束缚状态直至擒抱结束。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "羽蛇施展以下一道法术，无需法术成分并使用感知作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测善恶Detect Evil and Good，侦测魔法Detect Magic，侦测思想Detect Thoughts，形体变化Shapechange（仅野兽与类人形态，不会因此法术获得临时生命值，但无需为维持此法术而保有临时生命值或维持专注）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "造粮术Create Food and Water，托梦术Dream，高等复原术Greater Restoration，探知Scrying，睡眠术Sleep"
      }
    ],
    "bonus_actions": [
      {
        "name": "至圣援护",
        "en_name": "Divine Aid",
        "description": "羽蛇施展祝福术Bless，次等复原术Lesser \nRestoration或庇护术Sanctuary，使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "天族\\羽蛇.htm"
  },
  {
    "name": "小仙灵",
    "en_name": "Sprite",
    "type_line": "微型妖精, 中立善良",
    "size": "Tiny",
    "creature_type": "妖精, 中立善良",
    "alignment": "",
    "ac": 15,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 10,
    "hp_formula": "4d4",
    "speed": {
      "walk": "10尺、飞行40尺"
    },
    "abilities": {
      "力量": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 3
    },
    "senses": {
      "被动察觉": 13
    },
    "languages": "通用语，精灵语，木族语",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "actions": [
      {
        "name": "针剑",
        "en_name": "Needle Sword",
        "description": "近战攻击检定：+6，触及5尺。\n命中：6（1d4+4）点穿刺伤害。"
      },
      {
        "name": "惑控之弓",
        "en_name": "Enchanting Bow",
        "description": "远程攻击检定：+6，射程40/160尺。\n命中：1穿刺伤害，且目标陷入魅惑状态，直至小仙灵的下个回合开始。"
      },
      {
        "name": "真心视界",
        "en_name": "Heart Sight",
        "description": "魅力豁免检定：DC10，单一5尺内小仙灵可见的生物（此豁免天族、邪魔、亡灵自动失败）。\n失败：小仙灵获悉目标的情绪与阵营。"
      },
      {
        "name": "隐形",
        "en_name": "Invisibility",
        "description": "小仙灵对自身施展隐形术Invisibility，无需法术成分并使用魅力作为施法属性。"
      }
    ],
    "source_file": "妖精\\小仙灵.htm"
  },
  {
    "name": "树精",
    "en_name": "Dryad",
    "type_line": "中型妖精，中立",
    "size": "Medium",
    "creature_type": "妖精",
    "alignment": "中立",
    "ac": 16,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 22,
    "hp_formula": "5d8",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 5
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 14
    },
    "languages": "精灵语，木族语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "树精对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "动植物交谈",
        "en_name": "Speak with Beasts and Plants",
        "description": "树精可以与野兽和植物进行交流，如同共享同一门语言。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "树精发动一次藤鞭抽击或荆棘迸裂攻击，并使用施法施展魅惑怪物Charm \nMonster 。"
      },
      {
        "name": "藤鞭抽击",
        "en_name": "Vine Lash",
        "description": "近战攻击检定：+6，触及10尺。命中：8（1d8+4）挥砍伤害"
      },
      {
        "name": "荆棘迸裂",
        "en_name": "Thorn Burst",
        "description": "远程攻击检定：+6，射程60尺。命中：7（1d6+4）穿刺伤害"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "该树精施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC14）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "化兽为友Animal Friendship， 魅惑怪物Charm Monster（持续24小时；于树精再次释放该法术时提前结束），  德鲁伊伎俩Druidcraft"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "纠缠术Entangle，行动无踪Pass Without Trace"
      }
    ],
    "bonus_actions": [
      {
        "name": "林间飞跃",
        "en_name": "Tree Stride",
        "description": "如果树精位于一颗不小于大型的树的5尺内，则可以传送至该树60尺内的，另一颗不小于大型的树的5尺内的未占据空间。"
      }
    ],
    "source_file": "妖精\\树精.htm"
  },
  {
    "name": "闪现犬",
    "en_name": "Blink Dog",
    "type_line": "中型妖精，守序善良",
    "size": "Medium",
    "creature_type": "妖精",
    "alignment": "守序善良",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 22,
    "hp_formula": "4d8+4",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 5,
      "隐匿": 5
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 15
    },
    "languages": "闪现犬语；理解精灵语和木族语，但不会说",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：5（1d4+3）穿刺伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "传送",
        "en_name": "Teleport",
        "description": "闪现犬传送至多40尺至一处其可见的未占据空间中。",
        "params": "充能4~6"
      }
    ],
    "source_file": "妖精\\闪现犬.htm"
  },
  {
    "name": "双头巨人",
    "en_name": "Ettin",
    "type_line": "大型巨人，混乱邪恶",
    "size": "Large",
    "creature_type": "巨人",
    "alignment": "混乱邪恶",
    "ac": 12,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 85,
    "hp_formula": "10d10+30",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 4
    },
    "equipment": "战斧，钉头锤",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 14
    },
    "languages": "巨人语",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "双头巨人发动一次战斧攻击和一次钉头锤攻击。"
      },
      {
        "name": "战斧",
        "en_name": "Battleaxe",
        "description": "近战攻击检定：+7，触及5尺。命中：14（2d8+5）挥砍伤害。如果目标生物体型不超过大型，则其陷入倒地状态。"
      },
      {
        "name": "钉头锤",
        "en_name": "Morningstar",
        "description": "近战攻击检定：+7，触及5尺。命中：14（2d8+5）穿刺伤害，并且在在目标的下个回合结束前，其进行的下次攻击检定具有劣势。"
      }
    ],
    "source_file": "巨人\\双头巨人.htm"
  },
  {
    "name": "废陋巨人",
    "en_name": "Fomorian",
    "type_line": "巨型巨人，混乱邪恶",
    "size": "Huge",
    "creature_type": "巨人",
    "alignment": "混乱邪恶",
    "ac": 14,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 172,
    "hp_formula": "15d12+75",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 8,
      "隐匿": 3
    },
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 18
    },
    "languages": "巨人语，地底通用语",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "废陋巨人发动两次石槌攻击，其可以将其中一次攻击替换为使用扭曲恶咒（若条件允许）。"
      },
      {
        "name": "石棒",
        "en_name": "Stone Club",
        "description": "近战攻击检定：+9，触及15尺。命中：24（4d8+6）钝击伤害。"
      },
      {
        "name": "扭曲恶咒",
        "en_name": "Warping Hex",
        "description": "感知豁免检定：DC16，单一120尺内废陋巨人可见的生物。失败： 21（6d6）心灵伤害，且目标获得1级力竭。成功：仅半伤。",
        "params": "充能4~6"
      }
    ],
    "source_file": "巨人\\废陋巨人.htm"
  },
  {
    "name": "呋噜",
    "en_name": "Flumph",
    "type_line": "小型异怪，守序善良",
    "size": "Small",
    "creature_type": "异怪",
    "alignment": "守序善良",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 7,
    "hp_formula": "2d6",
    "speed": {
      "walk": "5尺，飞行30尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "奥秘": 4,
      "历史": 4,
      "宗教": 4
    },
    "damage_vulnerabilities": [
      "心灵"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 12
    },
    "languages": "理解地底通用语，但不会说；心灵感应60尺",
    "cr": "1/8",
    "xp": 25,
    "pb": 2,
    "traits": [
      {
        "name": "增强心灵感应",
        "en_name": "Advanced Telepathy",
        "description": "呋噜可以感知到其60尺内的任何心灵感应交流的内容。"
      },
      {
        "name": "倒地缺陷",
        "en_name": "Prone Deciency",
        "description": "若呋噜陷入倒地状态，掷一枚骰子。若结果为奇数，其陷入失能状态。呋噜在其每个回合结束时进行一次DC10的敏捷豁免，成功则结束失能状态。"
      },
      {
        "name": "心灵屏蔽",
        "en_name": "Telepathic Shroud",
        "description": "呋噜的思维无法以任何方式被阅读，且法术无法在远程观测其或侦测其位置。"
      }
    ],
    "actions": [
      {
        "name": "触须",
        "en_name": "Tentacle",
        "description": "近战攻击检定：+4，触及5尺。命中：4（1d4+2）强酸伤害。"
      },
      {
        "name": "恶臭喷射",
        "en_name": "Stench Spray",
        "description": "敏捷豁免检定：DC10，单一15尺内呋噜可见的生物。\n失败：目标被一种恶臭难闻的液体包裹，在1d4小时内持续散发恶臭，并在恶臭持续期间陷入中毒状态。其他生物在身处源自被恶臭包裹生物的5尺光环区域内期间，也陷入中毒状态。目标可以在短休或长休期间通过洗澡来去除身上的恶臭。",
        "params": "1/天"
      }
    ],
    "source_file": "异怪\\呋噜.htm"
  },
  {
    "name": "呓语之口",
    "en_name": "Gibbering Mouther",
    "type_line": "中型异怪，混乱中立",
    "size": "Medium",
    "creature_type": "异怪",
    "alignment": "混乱中立",
    "ac": 9,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 52,
    "hp_formula": "7d8+21",
    "speed": {
      "walk": "20尺，游泳20尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "damage_immunities": [
      "倒地"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "无",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "异变丛生",
        "en_name": "Aberrant Ground",
        "description": "源自呓语之口的10尺光环区域内的地面视为困难地形。"
      },
      {
        "name": "呓语",
        "en_name": "Gibbering",
        "description": "只要未陷入失能状态，呓语之口会喋喋不休无序之词。\n感知豁免检定：DC10，呓语之口胡言期间，在其20尺内开始自己的回合的任意生物。\n失败：目标掷1d8以决定当前回合其执行什么行动："
      },
      {
        "name": "1~4",
        "en_name": "",
        "description": "目标什么都不做。"
      },
      {
        "name": "5~6",
        "en_name": "",
        "description": "目标无法执行动作或附赠动作，并消耗其全部移动力向一个随机方向移动。"
      },
      {
        "name": "7~8",
        "en_name": "",
        "description": "目标随机选择其触及范围内一名的生物，对其发动一次近战攻击。若其无法发动此攻击，则什么都不做。"
      }
    ],
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+2，触及5尺。命中：7（2d6）穿刺伤害。若目标生物体型不超过中型，则其陷入倒地状态。若目标因此伤害生命值降至0，目标死亡。然后其肉体被呓语之口吸收，仅留下装备。"
      },
      {
        "name": "致盲唾液",
        "en_name": "Blinding Spittle",
        "description": "敏捷豁免检定：DC10，以30尺内一点为中心，半径10尺球状区域内的每名生物。失败：7（2d6）光耀伤害，且目标陷入目盲状态直至呓语之口的下个回合结束。",
        "params": "充能5~6"
      }
    ],
    "source_file": "异怪\\呓语之口.htm"
  },
  {
    "name": "噬脑怪",
    "en_name": "Intellect Devourer",
    "type_line": "微型异怪，守序邪恶",
    "size": "Tiny",
    "creature_type": "异怪",
    "alignment": "守序邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 28,
    "hp_formula": "8d4+8",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 2,
      "隐匿": 4
    },
    "damage_resistances": [
      "心灵"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 12
    },
    "languages": "理解深潜语，但不会说；心灵感应60尺",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "侦测智能",
        "en_name": "Detect Intelligence",
        "description": "噬脑怪可以魔法性地感知到位于它300尺内任何智力不低于3的生物的位置，无论二者之间有什么障碍。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "噬脑怪发动一次爪击攻击并使用吞食智力。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+4，触及5尺。\n命中：7（2d4+2）挥砍伤害。"
      },
      {
        "name": "吞食智力",
        "en_name": "Devour Intellect",
        "description": "智力豁免检定：DC12，单一5尺内噬脑怪可见的生物。\n失败：11（2d10）心灵伤害，且目标陷入震慑状态，直至噬脑怪的下个回合结束。"
      },
      {
        "name": "窃取身体",
        "en_name": "Steal Body",
        "description": "智力豁免检定：DC12，单一5尺内的陷入失能状态的小型或中型生物，为类人或野兽，且生命值为不高于10。\n失败：噬脑怪附身目标，吞食其大脑，并传送进入其头颅内。在噬脑怪位于目标头颅内期间，对宿主体外的攻击和其他效应而言处于全身掩护 \n。噬脑怪保留其智力、感知和魅力属性值，其仍理解深潜语，并保留其心灵感应和侦测智能特质。噬脑怪的其他部分将继承目标的游戏数据。其将获悉目标所知的一切，包括法术和语言。"
      }
    ],
    "source_file": "异怪\\噬脑怪.htm"
  },
  {
    "name": "幽邃盲族",
    "en_name": "Grimlock",
    "type_line": "中型异怪，中立邪恶",
    "size": "Medium",
    "creature_type": "异怪",
    "alignment": "中立邪恶",
    "ac": 11,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 11,
    "hp_formula": "2d8+2",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "运动": 5,
      "察觉": 3,
      "隐匿": 5
    },
    "senses": {
      "盲视": 30,
      "被动察觉": 13
    },
    "languages": "无",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "actions": [
      {
        "name": "骨棒",
        "en_name": "Bone Cudgel",
        "description": "近战攻击检定：+5，触及5尺。命中：6（1d6+3）钝击伤害，外加2（1d4）心灵伤害。"
      }
    ],
    "source_file": "异怪\\幽邃盲族.htm"
  },
  {
    "name": "底栖魔鱼",
    "en_name": "Aboleth",
    "type_line": "大型异怪，守序邪恶",
    "size": "Large",
    "creature_type": "异怪",
    "alignment": "守序邪恶",
    "ac": 17,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 150,
    "hp_formula": "20d10+40",
    "speed": {
      "walk": "10尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 9,
        "mod": -1,
        "save": 3
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 6
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 8
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 6
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "历史": 12,
      "察觉": 10
    },
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 20
    },
    "languages": "深潜语，心灵感应120尺",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "底栖魔鱼可以在空气和水中呼吸。"
      },
      {
        "name": "魔能重塑",
        "en_name": "Eldritch Restoration",
        "description": "底栖魔鱼被摧毁后会在5d10天内在遥远国度或DM选择的某处其他地点获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "底栖魔鱼豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      },
      {
        "name": "粘液之云",
        "en_name": "Mucus Cloud",
        "description": "若身处水下，底栖魔鱼被粘液包围。体质豁免检定：DC14，底栖魔鱼回合结束时位于源自底栖魔鱼的5尺光环区域内的每名生物。失败：目标被诅咒。目标的皮肤变得滑腻，目标可以在空气和水中呼吸，并且目标无法恢复生命值除非其身处水下，直至诅咒结束。"
      },
      {
        "name": "探查感应",
        "en_name": "Probing Telepathy",
        "description": "若一名底栖魔鱼可见的生物与其进行心灵感应，则底栖魔鱼将知晓该生物最强烈的渴望。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "底栖魔鱼发动两次触须攻击并使用吞噬记忆或是支配意志（若条件允许）。"
      },
      {
        "name": "触须",
        "en_name": "Tentacle",
        "description": "近战攻击检定：+9，触及15尺。命中：12（2d6+5）钝击伤害。若目标生物体型不超过大型，则其会被四条触须之一擒抱，陷入受擒状态（逃脱DC14）。"
      },
      {
        "name": "吞噬记忆",
        "en_name": "Consume Memories",
        "description": "智力豁免检定：DC16，单一30尺内魅惑或受擒于底栖魔鱼的生物。失败：10（3d6）心灵伤害。成功：半伤。失败或成功：若目标为类人且因该动作生命值降至0，则底栖魔鱼获得目标的记忆。"
      },
      {
        "name": "支配意志",
        "en_name": "Dominate Mind",
        "description": "感知豁免检定：DC16，单一30尺内底栖魔鱼可见的生物。失败：目标陷入魅惑状态，直至底栖魔鱼死亡或移动至目标所在位面外的另一存在位面。魅惑期间，目标将如底栖魔鱼的盟友一般行动，且若身处底栖魔鱼60尺内则受其操控。此外，底栖魔鱼和目标可以在任意距离内通过心灵感应交流。",
        "params": "2/天"
      }
    ],
    "legendary_actions": [
      {
        "name": "鞭笞",
        "en_name": "Lash",
        "description": "底栖魔鱼发动一次触须攻击。",
        "max_uses": 3
      },
      {
        "name": "心灵吸取",
        "en_name": "Psychic Drain",
        "description": "若至少有一名生物魅惑或受擒于底栖魔鱼，其使用吞噬记忆并恢复5（1d10）生命值。",
        "max_uses": 3
      }
    ],
    "source_file": "异怪\\底栖魔鱼.htm"
  },
  {
    "name": "斗篷怪",
    "en_name": "Cloaker",
    "type_line": "大型异怪，混乱中立",
    "size": "Large",
    "creature_type": "异怪",
    "alignment": "混乱中立",
    "ac": 14,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 91,
    "hp_formula": "14d10+14",
    "speed": {
      "walk": "10尺，飞行40尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "隐匿": 5
    },
    "damage_immunities": [
      "恐慌"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 12
    },
    "languages": "深潜语，地底通用语",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "traits": [
      {
        "name": "光照敏感",
        "en_name": "Light Sensitivity",
        "description": "若斗篷怪身处明亮光照中，其攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "斗篷怪发动一次吸附攻击和两次尾击攻击。"
      },
      {
        "name": "吸附",
        "en_name": "Attach",
        "description": "近战攻击检定：+6，触及5 尺。 \n命中：13（3d6+3）穿刺伤害。若目标生物体型不超过大型，斗篷怪会吸附在其身上。斗篷怪吸附期间，目标陷入目盲状态，且斗篷怪无法对其他生物发动吸附攻击。此外，斗篷怪所受的伤害减半（向下取整），且目标承受等额的伤害。"
      },
      {
        "name": "尾击",
        "en_name": "Tail",
        "description": "近战攻击检定：+6，触及10尺。\n命中：8（1d10+3）挥砍伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "呼嚎",
        "en_name": "Moan",
        "description": "感知豁免检定：DC13，源自斗篷怪60尺光环区域内的每名生物。 \n失败：目标陷入恐慌状态，直到斗篷怪的下个回合结束。\n成功：目标在24小时内免疫此斗篷怪的呼嚎。"
      },
      {
        "name": "幻象",
        "en_name": "Phantasms",
        "description": "斗篷怪施展法术镜影术Mirror \nImage\n ，无需法术成分并使用感知作为施法属性。若斗篷怪在明亮光照中开始或结束其回合，法术会提前结束。",
        "params": "短休或长休后充能"
      }
    ],
    "source_file": "异怪\\斗篷怪.htm"
  },
  {
    "name": "暗幕魔兽",
    "en_name": "Darkmantle",
    "type_line": "小型异怪，无阵营",
    "size": "Small",
    "creature_type": "异怪",
    "alignment": "无阵营",
    "ac": 11,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 22,
    "hp_formula": "5d6+5",
    "speed": {
      "walk": "10尺，飞行30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "skills": {
      "隐匿": 3
    },
    "senses": {
      "盲视": 60,
      "被动察觉": 10
    },
    "languages": "无",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "actions": [
      {
        "name": "碾压",
        "en_name": "Crush",
        "description": "近战攻击检定：+5，触及5尺。\n命中：6（1d6+3）钝击伤害，且暗幕魔兽会吸附在目标身上。若目标生物体型不超过中型且暗幕魔兽的此次攻击检定具有优势，暗幕魔兽将会覆盖目标，令暗幕魔兽以此法吸附期间，该生物陷入目盲状态且窒息。"
      },
      {
        "name": "暗幕灵光",
        "en_name": "Darkness Aura",
        "description": "魔法黑暗充斥在源自暗幕魔兽的15尺光环区域内。此效应在暗幕魔兽维持专注期间持续，持续至多10分钟。黑暗视觉无法看透该区域，且光照无法照亮之。",
        "params": "1/日"
      }
    ],
    "source_file": "异怪\\暗幕魔兽.htm"
  },
  {
    "name": "甲伏怪",
    "en_name": "Chuul",
    "type_line": "大型异怪，混乱邪恶",
    "size": "Large",
    "creature_type": "异怪",
    "alignment": "混乱邪恶",
    "ac": 16,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 76,
    "hp_formula": "9d10+27",
    "speed": {
      "walk": "30尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "skills": {
      "察觉": 4
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 14
    },
    "languages": "理解深潜语，但不会说",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "甲伏怪可以在空气和水中呼吸。"
      },
      {
        "name": "感知魔法",
        "en_name": "Sense Magic",
        "description": "甲伏怪可以探知120尺内的魔法。此特质如同法术侦测魔法detect \nmagic ，但本身不是魔法。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "甲伏怪发动两次钳击攻击并使用麻痹触须。"
      },
      {
        "name": "钳击",
        "en_name": "Pincer",
        "description": "近战攻击检定：+6，触及10尺。命中：9（1d10+4）钝击伤害。若目标生物体型不超过大型，则其被两个巨钳之一擒抱，陷入受擒状态。"
      },
      {
        "name": "麻痹触须",
        "en_name": "Paralyzing Tentacles",
        "description": "体质豁免检定：DC13，单一受擒于甲伏怪的生物。失败：目标陷入中毒状态并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。 中毒期间，目标陷入麻痹状态。"
      }
    ],
    "source_file": "异怪\\甲伏怪.htm"
  },
  {
    "name": "石绳怪",
    "en_name": "Roper",
    "type_line": "大型异怪，中立邪恶",
    "size": "Large",
    "creature_type": "异怪",
    "alignment": "中立邪恶",
    "ac": 20,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 93,
    "hp_formula": "11d10+33",
    "speed": {
      "walk": "10尺，攀爬20尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 6,
      "隐匿": 5
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 16
    },
    "languages": "无",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "蛛行",
        "en_name": "Spider Climb",
        "description": "石绳怪可以在难以攀爬的表面上攀爬，包括沿着天花板移动，且无需为此进行属性检定。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "石绳怪发动两次触须攻击，使用拖拽，并发动两次啃咬攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+7，触及5尺。\n命中：17（3d8+4）穿刺伤害。"
      },
      {
        "name": "触须",
        "en_name": "Tentacle",
        "description": "近战攻击检定：+7，触及60尺。命中：目标被六条触须之一擒抱，陷入受擒状态（逃脱DC14），且目标陷入中毒状态直至擒抱结束。"
      },
      {
        "name": "拖拽",
        "en_name": "Reel",
        "description": "石绳怪将受擒于其的每名生物直线拉近至多30尺。"
      }
    ],
    "source_file": "异怪\\石绳怪.htm"
  },
  {
    "name": "石锥怪",
    "en_name": "Piercer",
    "type_line": "中型异怪，无阵营",
    "size": "Medium",
    "creature_type": "异怪",
    "alignment": "无阵营",
    "ac": 15,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 22,
    "hp_formula": "3d8+9",
    "speed": {
      "walk": "5尺，攀爬15尺"
    },
    "abilities": {
      "力量": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "魅力": {
        "score": 3,
        "mod": -4,
        "save": -4
      }
    },
    "skills": {
      "隐匿": 5
    },
    "senses": {
      "盲视": 30,
      "被动察觉": 8
    },
    "languages": "无",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "蛛行",
        "en_name": "Spider Climb",
        "description": "石锥怪可以在难以攀爬的表面上攀爬，包括沿着天花板移动，且无需为此进行属性检定。"
      }
    ],
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+3，触及5尺。命中：5（1d8+1）穿刺伤害。"
      },
      {
        "name": "坠落",
        "en_name": "Drop",
        "description": "石锥怪落下。敏捷豁免检定：DC11，单一位于石锥怪正下方的生物。失败：10（3d6）穿刺伤害。失败或成功：石锥怪因坠落受到的伤害减少20。"
      }
    ],
    "source_file": "异怪\\石锥怪.htm"
  },
  {
    "name": "触须怪",
    "en_name": "Grell",
    "type_line": "中型异怪，中立邪恶",
    "size": "Medium",
    "creature_type": "异怪",
    "alignment": "中立邪恶",
    "ac": 12,
    "initiative_bonus": 6,
    "initiative_total": 16,
    "hp": 55,
    "hp_formula": "10d8+10",
    "speed": {
      "walk": "10尺，飞行30尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 4
    },
    "damage_immunities": [
      "闪电、倒地"
    ],
    "senses": {
      "盲视": 60
    },
    "languages": "深潜语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "劫持",
        "en_name": "Abduct",
        "description": "触须怪移动一名正被其擒抱的生物时无需额外消耗移动力。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "触须怪发动一次喙啄和一次麻痹触须攻击。"
      },
      {
        "name": "喙啄",
        "en_name": "Beak",
        "description": "近战攻击检定：+4，触及5尺。命中：11（2d8+2）穿刺伤害。"
      },
      {
        "name": "麻痹触须",
        "en_name": "Paralyzing Tentacles",
        "description": "近战攻击检定：+4，触及10尺。命中：7（1d10+2）穿刺伤害。若目标生物体型不超过中型，则其被触须怪十条触手之二擒抱，陷入受擒状态（逃脱DC12）。目标还将承受以下效应：体质豁免检定：DC11。失败：目标陷入中毒状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。 中毒期间，目标陷入麻痹状态。"
      }
    ],
    "source_file": "异怪\\触须怪.htm"
  },
  {
    "name": "诺斯怪",
    "en_name": "Nothic",
    "type_line": "中型异怪，中立邪恶",
    "size": "Medium",
    "creature_type": "异怪",
    "alignment": "中立邪恶",
    "ac": 15,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 45,
    "hp_formula": "6d8+18",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "奥秘": 3,
      "洞悉": 4,
      "察觉": 4,
      "隐匿": 5
    },
    "senses": {
      "真实视觉": 120,
      "被动察觉": 14
    },
    "languages": "地底通用语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "诺斯怪发动2次爪击攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+5，触及5尺。命中：8（1d10+3）挥砍伤害。"
      },
      {
        "name": "腐朽凝视",
        "en_name": "Rotting Gaze",
        "description": "体质豁免检定：DC13，单一120尺内诺斯怪可见的生物。失败：17（5d6）暗蚀伤害。成功：半伤。"
      }
    ],
    "bonus_actions": [
      {
        "name": "怪异洞悉",
        "en_name": "Weird Insight",
        "description": "感知豁免检定：DC14，单一120尺内诺斯怪可见的生物。失败：诺斯怪魔法性的得知一件与目标相关的事实或秘密。",
        "params": "充能6"
      }
    ],
    "source_file": "异怪\\诺斯怪.htm"
  },
  {
    "name": "食腐兽",
    "en_name": "Otyugh",
    "type_line": "大型异怪，中立",
    "size": "Large",
    "creature_type": "异怪",
    "alignment": "中立",
    "ac": 14,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 104,
    "hp_formula": "11d10+44",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 19,
        "mod": 4,
        "save": 7
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 11
    },
    "languages": "食腐兽语；心灵感应120尺（接收者无法以心灵感应回应）",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "食腐兽发动一次啃咬攻击和两次触须攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+6，触及5尺。命中：12（2d8+3）穿刺伤害，且目标陷入中毒状态。每当中毒生物完成长休时，其承受以下效应。体质豁免检定：DC15。失败：目标的生命值上限减少5（1d10），并且其生命值上限无法恢复直至中毒状态结束。"
      },
      {
        "name": "触须",
        "en_name": "Tentacle",
        "description": "近战攻击检定：+6，触及10尺。命中：12（2d8+3）穿刺伤害。若目标生物体型不超过中型，其被两条触须之一擒抱，陷入受擒状态（逃脱DC13）。"
      },
      {
        "name": "触须猛击",
        "en_name": "Tentacle Slam",
        "description": "体质豁免检定：DC14，受擒于食腐兽的每名生物。失败：16（3d8+3）钝击伤害，且目标陷入震慑状态直至食腐兽的下个回合开始。成功：仅半伤。"
      }
    ],
    "source_file": "异怪\\食腐兽.htm"
  },
  {
    "name": "亡命恶犬",
    "en_name": "Death Dog",
    "type_line": "中型怪兽，中立邪恶",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "中立邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 39,
    "hp_formula": "6d8+12",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 5,
      "隐匿": 4
    },
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 15
    },
    "languages": "无",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "亡命恶犬发动两次啃咬攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+4，触及5尺。命中：4（1d4+2）穿刺伤害。若目标生物体型不超过大型，其承受以下效应。体质豁免检定：DC12。首次失败：目标陷入中毒状态。中毒期间，目标的生命值上限在完成长休时无法恢复。此后每24小时目标重复豁免，成功则终止其身上的该效应。后续失败：中毒目标的生命值上限减少5（1d10）。"
      }
    ],
    "source_file": "怪兽\\亡命恶犬.htm"
  },
  {
    "name": "伊特怪",
    "en_name": "Ettercap",
    "type_line": "中型怪兽，中立邪恶",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "中立邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 44,
    "hp_formula": "8d8+8",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 3,
      "隐匿": 4,
      "求生": 3
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 13
    },
    "languages": "无",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "蛛行",
        "en_name": "Spider Climb",
        "description": "伊特怪可以在难以攀爬的表面上攀爬，包括沿着天花板移动，且不需要为此进行属性检定。"
      },
      {
        "name": "蛛网行者",
        "en_name": "Web Walker",
        "description": "伊特怪在蛛网上移动时无视蛛网造成的移动限制，且与蛛网接触期间，伊特怪可以知道其他与该蛛网接触生物的准确位置。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "伊特怪发动一次啃咬攻击和一次爪击攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）穿刺伤害外加2（1d4）毒素伤害，且目标陷入中毒状态，持续至伊特怪的下个回合开始。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+4，触及5尺。\n命中：7（2d4+2）挥砍伤害。"
      },
      {
        "name": "绞网",
        "en_name": "Web Strand",
        "description": ""
      }
    ],
    "bonus_actions": [
      {
        "name": "收网",
        "en_name": "Reel",
        "description": "伊特怪将30尺内因其绞网动作陷入束缚的一名生物向直线拉近至多25尺。"
      }
    ],
    "source_file": "怪兽\\伊特怪.htm"
  },
  {
    "name": "冬狼",
    "en_name": "Winter Wolf",
    "type_line": "大型怪兽，中立邪恶",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "中立邪恶",
    "ac": 13,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 75,
    "hp_formula": "10d10+20",
    "speed": {
      "walk": "50尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 5,
      "隐匿": 5
    },
    "damage_immunities": [
      "寒冷"
    ],
    "senses": {
      "被动察觉": 15
    },
    "languages": "通用语，巨人语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "集群战术",
        "en_name": "Pack Tactics",
        "description": "若冬狼的攻击目标生物5尺内存在有至少一名冬狼未失能的盟友，则冬狼对该生物进行的攻击检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+6，触及5尺。\n命中：11（2d6+4）穿刺伤害，若目标生物体型不超过大型，则其陷入倒地状态。"
      },
      {
        "name": "极寒吐息",
        "en_name": "Cold Breath",
        "description": "体质豁免检定：DC12，15尺锥状区域内的每名生物。\n失败：18（4d8）寒冷伤害。\n成功：半伤。",
        "params": "充能 5~6"
      }
    ],
    "source_file": "怪兽\\冬狼.htm"
  },
  {
    "name": "刺尾狮",
    "en_name": "Manticore",
    "type_line": "大型怪兽，守序邪恶",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "守序邪恶",
    "ac": 14,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 68,
    "hp_formula": "8d10+24",
    "speed": {
      "walk": "30尺，飞行50尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "通用语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "刺尾狮使用撕裂或尾钉发动共计三次攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+5，触及5尺。\n命中：7（1d8+3）挥砍伤害。"
      },
      {
        "name": "尾钉",
        "en_name": "Tail Spike",
        "description": "远程攻击检定：+5，射程100/200尺。\n命中：7（1d8+3）穿刺伤害。"
      }
    ],
    "source_file": "怪兽\\刺尾狮.htm"
  },
  {
    "name": "变形怪",
    "en_name": "Doppelganger",
    "type_line": "中型怪兽，中立",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "中立",
    "ac": 14,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 52,
    "hp_formula": "8d8+16",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "欺瞒": 6,
      "洞悉": 3
    },
    "damage_immunities": [
      "魅惑"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "通用语，外加三门其他语言",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "变形怪使用两次猛击攻击，并使用诡异面容（若条件允许）。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+6（在每场战斗的第一轮中具有优势），触及5尺。命中：11（2d6+4）钝击伤害。"
      },
      {
        "name": "读心",
        "en_name": "Ready Thoughts",
        "description": "变形怪施展侦测思想Detect \nThoughts ，无需法术成分并使用魅力作为施法属性（法术豁免DC12）。"
      },
      {
        "name": "诡异面容",
        "en_name": "Unsettling Visage",
        "description": "感知豁免检定：DC12，源自变形怪的15尺光环区域内的每名能看见变形怪的生物。失败：目标陷入恐慌状态，并在其每个回合结束时重复豁免，成功则终止其身上的此效应。1分钟后，其豁免自动成功。",
        "params": "充能6"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "变形怪变形为小型或中型的类人生物，或变回其真实形态。除体型以外，其各形态下游戏数据均相同。变形怪着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "怪兽\\变形怪.htm"
  },
  {
    "name": "多头蛇",
    "en_name": "Hydra",
    "type_line": "巨型怪兽，无阵营",
    "size": "Huge",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 15,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 184,
    "speed": {
      "walk": "40尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 6
    },
    "damage_immunities": [
      "目盲",
      "魅惑",
      "耳聋",
      "恐慌",
      "震慑",
      "昏迷"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 16
    },
    "languages": "无",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "traits": [
      {
        "name": "屏息",
        "en_name": "Hold Breath",
        "description": "多头蛇可以屏息一小时。"
      },
      {
        "name": "万首",
        "en_name": "Multiple Heads",
        "description": "多头蛇具有五个头颅。每当多头蛇在一回合中受到至少25伤害时，其中一个头颅死亡。所有头颅死亡则多头蛇死亡。 在多头蛇的回合结束时，只要其还有至少一个头颅活着且自其上个回合开始未受到火焰伤害，则自其上个回合开始，其每死亡一个头颅就长出两个新的头颅。多头蛇长出新的头颅时，恢复20生命值。"
      },
      {
        "name": "多头反射",
        "en_name": "Reactive Heads",
        "description": "多头蛇超过一个的每个头颅，均令其获得一个额外的反应，该反应只能用于借机攻击。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "多头蛇发动与头颅数相等次啃咬攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+8，触及10尺。\n命中：10（1d10+5）穿刺伤害。"
      }
    ],
    "source_file": "怪兽\\多头蛇.htm"
  },
  {
    "name": "天狗",
    "en_name": "Kenku",
    "type_line": "中型怪兽，中立",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 13,
    "hp_formula": "3d8",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "欺瞒": 4,
      "察觉": 2,
      "隐匿": 5
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 12
    },
    "languages": "通用语，原初语（气族语）",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "traits": [
      {
        "name": "拟声",
        "en_name": "Mimicry",
        "description": "天狗可以模仿其听过的任何声音，包括声线。听到该声音的生物可以成功通过一次DC14的感知（洞悉）检定来发现其是模仿。"
      }
    ],
    "actions": [
      {
        "name": "影之刃",
        "en_name": "Shadow Blade",
        "description": "近战或远程攻击检定：+5，触及5尺或射程60尺。命中：6（1d6+3）暗蚀伤害。命中或失手：影之刃会在被用于一次远程攻击后立即魔法性地回到天狗手中。"
      }
    ],
    "bonus_actions": [
      {
        "name": "魔能提灯",
        "en_name": "Eldritch Lantern",
        "description": "天狗施展妖火Faerie \nFire，并使用智力作为施法属性（法术豁免DC10）。",
        "params": "充能4~6"
      }
    ],
    "source_file": "怪兽\\天狗.htm"
  },
  {
    "name": "奇美拉",
    "en_name": "Chimera",
    "type_line": "大型怪兽，混乱邪恶",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "混乱邪恶",
    "ac": 14,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 114,
    "speed": {
      "walk": "30尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 8
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 18
    },
    "languages": "理解龙语，但不会说",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "奇美拉发动一次角撞攻击，一次啃咬攻击，一次利爪攻击。其可以将利爪攻击替换为使用火焰吐息（若条件允许）。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+7，触及5尺。\n命中：11（2d6+4）穿刺伤害，若奇美拉此次攻击具有优势，改为18（4d6+4）穿刺伤害。"
      },
      {
        "name": "利爪",
        "en_name": "Claw",
        "description": "近战攻击检定：+7，触及5尺。\n命中：7（1d6+4）挥砍伤害。"
      },
      {
        "name": "角撞",
        "en_name": "Ram",
        "description": "近战攻击检定：+7，触及5尺。\n命中：10（1d12+4）钝击伤害，若目标生物体型不超过中型，其陷入倒地状态。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC15，15尺锥状区域内的每名生物。\n失败：31（7d8）火焰伤害。\n成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "source_file": "怪兽\\奇美拉.htm"
  },
  {
    "name": "巴弗灭的牛头人",
    "en_name": "Minotaur of Baphomet",
    "type_line": "大型怪兽，混乱邪恶",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "混乱邪恶",
    "ac": 14,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 85,
    "hp_formula": "10d10+30",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 7,
      "求生": 7
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 17
    },
    "languages": "深渊语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "actions": [
      {
        "name": "深渊长柄刀",
        "en_name": "Abyssal Glaive",
        "description": "近战攻击检定：+6，触及10尺。命中：10（1d12+4）挥砍伤害外加10（3d6）暗蚀伤害。"
      },
      {
        "name": "顶撞",
        "en_name": "Gore",
        "description": "近战攻击检定：+6，触及5尺。命中：18（4d6+4）穿刺伤害。若牛头人在此次攻击前立即向着目标直线移动了10+尺，且目标生物体型不超过大型，则目标额外受到10（3d6）穿刺伤害并陷入倒地状态。",
        "params": "充能5~6"
      }
    ],
    "source_file": "怪兽\\巴弗灭的牛头人.htm"
  },
  {
    "name": "恐爪怪",
    "en_name": "Hook Horror",
    "type_line": "大型怪兽，中立",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "中立",
    "ac": 15,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 75,
    "hp_formula": "10d10+20",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 4
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 5
    },
    "senses": {
      "盲视": 60,
      "被动察觉": 15
    },
    "languages": "恐爪语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "恐爪怪发动两次钩爪攻击。"
      },
      {
        "name": "钩爪",
        "en_name": "Hook",
        "description": "近战攻击检定：+6，触及10尺。命中：11（2d6+4）穿刺伤害。若目标生物体型不超过大型，恐爪怪将目标向靠近或远离自己的方向直线移动5尺。"
      }
    ],
    "source_file": "怪兽\\恐爪怪.htm"
  },
  {
    "name": "拟身怪",
    "en_name": "Mimic",
    "type_line": "中型怪兽，中立",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "中立",
    "ac": 12,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 58,
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "隐匿": 5
    },
    "damage_immunities": [
      "强酸"
    ],
    "condition_immunities": [
      "倒地"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "无",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "粘附",
        "en_name": "Adhesive",
        "description": "拟身怪粘附在任何触碰到其的东西上。体型不超过巨型的被粘附生物陷入受擒状态（逃脱DC13）。为逃脱此擒抱进行的属性检定具有劣势。",
        "params": "仅物件形态"
      }
    ],
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5（若目标因该拟身怪受擒则具有优势），触及5尺。\n命中：7（1d8+3）穿刺伤害（若目标因该拟身怪受擒则改为12（2d8+3）穿刺伤害）外加4（1d8）强酸伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "拟身怪变形为如同中型或小型物件，并保留其游戏数据；或拟身怪变回其真实斑点形态。拟身怪着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "怪兽\\拟身怪.htm"
  },
  {
    "name": "掘土巨怪",
    "en_name": "Umber Hulk",
    "type_line": "大型怪兽，混乱邪恶",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "混乱邪恶",
    "ac": 18,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 93,
    "hp_formula": "11d10+33",
    "speed": {
      "walk": "30尺，掘穴20尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 10
    },
    "languages": "掘土巨怪语",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "掘道者",
        "en_name": "Tunneler",
        "description": "掘土巨怪能够以其一半的掘穴速度掘穴通过坚硬的岩石，并在其身后留下直径10尺的地道。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "掘土巨怪发动三次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+8，触及10尺。命中：12（2d6+5）挥砍伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "困惑凝视",
        "en_name": "Confusing Gaze",
        "description": "感知豁免检定：DC14，30尺锥状区域内的每名生物。失败：目标无法使用反应直至掘土巨怪的下个回合结束。此外，目标的下个回合中，其投掷1d8来决定自己执行什么行动：",
        "params": "充能5~6"
      },
      {
        "name": "1~4",
        "en_name": "",
        "description": "目标什么都不做。"
      },
      {
        "name": "5~6",
        "en_name": "",
        "description": "目标无法执行动作或附赠动作，并消耗其全部移动力向一个随机方向移动。"
      },
      {
        "name": "7~8",
        "en_name": "",
        "description": "目标对其触及范围内随机一名生物发动一次近战攻击。若其无法发动此攻击，则什么都不做。"
      }
    ],
    "source_file": "怪兽\\掘土巨怪.htm"
  },
  {
    "name": "掘地虫",
    "en_name": "Ankheg",
    "type_line": "大型怪兽，无阵营",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 14,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 45,
    "hp_formula": "6d10+12",
    "speed": {
      "walk": "30尺，掘穴10尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "无",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "掘道者",
        "en_name": "Tunneler",
        "description": "掘地虫能够以其一半的掘穴速度掘穴通过坚硬的岩石，并在其身后留下直径10尺的地道。"
      }
    ],
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5（若目标受擒于掘地虫则具有优势），触及5尺。命中：10（2d6+3）挥砍伤害，外加3（1d6）强酸伤害。若目标生物体型不超过大型，则其陷入受擒状态（逃脱DC13）。"
      },
      {
        "name": "酸液喷射",
        "en_name": "Acid Spray",
        "description": "敏捷豁免检定：DC12，30尺长，5尺宽的线状区域内的每名生物。失败：14（4d6）强酸伤害。成功：半伤。",
        "params": "充能6"
      }
    ],
    "source_file": "怪兽\\掘地虫.htm"
  },
  {
    "name": "梅洛人鱼",
    "en_name": "Merrow",
    "type_line": "大型怪兽，混乱邪恶",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "混乱邪恶",
    "ac": 13,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 45,
    "hp_formula": "6d10+12",
    "speed": {
      "walk": "10尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "深渊语，原初语（水族语）",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "梅洛人鱼可以在空气和水中呼吸。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "梅洛人鱼使用啃咬、爪击或鱼叉发动共计两次攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+6，触及5尺。命中：6（1d4+4）穿刺伤害，并且目标陷入中毒状态，持续至梅洛人鱼的下个回合结束。"
      },
      {
        "name": "爪击",
        "en_name": "Claws",
        "description": "近战攻击检定：+6，触及5尺。命中：9（2d4+4）挥砍伤害。"
      },
      {
        "name": "鱼叉",
        "en_name": "Harpoon",
        "description": "近战或远程攻击检定：+6，触及5尺或射程20/60尺。命中：11（2d6+4）穿刺伤害。若目标生物体型不超过大型，则梅洛人鱼将目标直线拉近至多15尺。"
      }
    ],
    "source_file": "怪兽\\梅洛人鱼.htm"
  },
  {
    "name": "狮鹫",
    "en_name": "Griffon",
    "type_line": "大型怪兽，无阵营",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 59,
    "speed": {
      "walk": "30尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 5
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 15
    },
    "languages": "无",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "狮鹫发动两次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+6，触及5尺。"
      }
    ],
    "source_file": "怪兽\\狮鹫.htm"
  },
  {
    "name": "相位蜘蛛",
    "en_name": "Phase Spider",
    "type_line": "大型怪兽，无阵营",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 14,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 45,
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "隐匿": 7
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "无",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "以太视界",
        "en_name": "Trait Name",
        "description": "若相位蜘蛛身处物质位面，其能够看见60尺内的以太位面，反之亦然。"
      },
      {
        "name": "蛛行",
        "en_name": "Spider Climb",
        "description": "相位蜘蛛可以在难以攀爬的表面上攀爬，包括沿着天花板移动，且无需为此进行属性检定。"
      },
      {
        "name": "蛛网行者",
        "en_name": "Web Walker",
        "description": "相位蜘蛛在蛛网上移动时无视蛛网造成的移动限制，且与蛛网接触期间，相位蜘蛛可以知道其他与该蛛网接触生物的准确位置。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "相位蜘蛛发动两次啃咬攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。\n命中：8（1d10+3）穿刺伤害外加9（2d8）毒素伤害。若目标因此伤害生命值降至0，目标伤势稳定，并陷入中毒状态，持续1小时。中毒期间，目标还会陷入麻痹状态。"
      }
    ],
    "bonus_actions": [
      {
        "name": "以太漫游",
        "en_name": "Ethereal Jaunt",
        "description": "相位蜘蛛自物质位面传送至以太位面，或反之。"
      }
    ],
    "source_file": "怪兽\\相位蜘蛛.htm"
  },
  {
    "name": "石化蜥蜴",
    "en_name": "Basilisk",
    "type_line": "中型怪兽，无阵营",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 15,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 52,
    "hp_formula": "8d8+16",
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "无",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：10（2d6+3）穿刺伤害外加7（2d6）毒素伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "石化凝视",
        "en_name": "Petrifying Gaze",
        "description": "体质豁免检定：DC12，30尺锥状区域内的每名生物。若石化蜥蜴在锥形区域内看到自己的倒影，其也必须进行此豁免。首次失败：目标陷入束缚状态，目标在下个回合结束时仍处于束缚则重复豁免，成功则终止其身上的该效应。再次失败：目标陷入石化状态替代其束缚状态。",
        "params": "充能4~6"
      }
    ],
    "source_file": "怪兽\\石化蜥蜴.htm"
  },
  {
    "name": "移位兽",
    "en_name": "Displacer Beast",
    "type_line": "大型怪兽，守序邪恶",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "守序邪恶",
    "ac": 13,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 76,
    "hp_formula": "9d10+27",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "理解木族语但不会说",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "神避",
        "en_name": "Avoidance",
        "description": "当移位兽受到一个允许其进行豁免来只承受一半伤害的效应影响时，其豁免成功时不受伤害，豁免失败时只承受一半伤害。其无法在失能期间使用此特质。"
      },
      {
        "name": "移影换位",
        "en_name": "Displacement",
        "description": "移位兽投射的魔法幻象使自己看上去位于真实位置附近的另一个位置，导致所有对其进行的攻击检定具有劣势。移位兽失能期间该特质失效。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "移位兽发动一次撕裂攻击和一次触手攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+6，触及5尺。\n命中：9（1d10+4）挥砍伤害，若目标生物体型不超过大型，则其陷入倒地状态。"
      },
      {
        "name": "触手",
        "en_name": "Tentacle",
        "description": "近战攻击检定：+6，触及10尺。\n命中：11（2d6+4）穿刺伤害。"
      }
    ],
    "source_file": "怪兽\\移位兽.htm"
  },
  {
    "name": "穴蜥人",
    "en_name": "Troglodyte",
    "type_line": "中型怪兽，混乱邪恶",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "混乱邪恶",
    "ac": 11,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 13,
    "hp_formula": "2d8+4",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "隐匿": 4
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "穴蜥人语",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "traits": [
      {
        "name": "恶臭",
        "en_name": "Stench",
        "description": "体质豁免检定：DC12，在源自穴蜥人的5尺光环区域内开始其回合的每名非穴蜥人生物。失败：目标陷入中毒状态，直至其下个回合开始。成功：目标在1小时内免疫所有穴蜥人的恶臭。"
      },
      {
        "name": "日照敏感",
        "en_name": "Sunlight Sensitivity",
        "description": "若穴蜥人身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+4，触及5尺命中：5（1d6+2）挥砍伤害。"
      }
    ],
    "source_file": "怪兽\\穴蜥人.htm"
  },
  {
    "name": "紫虫",
    "en_name": "Purple Worm",
    "type_line": "超巨型怪兽，无阵营",
    "size": "Gargantuan",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 18,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 247,
    "hp_formula": "15d20+90",
    "speed": {
      "walk": "50尺，掘地50尺"
    },
    "abilities": {
      "力量": {
        "score": 28,
        "mod": 9,
        "save": 9
      },
      "敏捷": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "体质": {
        "score": 22,
        "mod": 6,
        "save": 11
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": 4
      },
      "魅力": {
        "score": 4,
        "mod": -3,
        "save": -3
      }
    },
    "senses": {
      "盲视": 30,
      "被动察觉": 9
    },
    "languages": "无",
    "cr": 15,
    "xp": 13000,
    "pb": 5,
    "traits": [
      {
        "name": "掘道者",
        "en_name": "Tunneler",
        "description": "紫虫能够以其一半的掘穴速度掘穴通过坚硬的岩石，并在其身后留下直径10尺的地道。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "紫虫发动一次啃咬攻击和一次尾刺攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+14，触及10尺。\n命中：22（3d8+9）穿刺伤害，若目标生物体型不超过大型，其陷入受擒状态（逃脱DC19），且目标陷入束缚状态直至擒抱结束。"
      },
      {
        "name": "尾刺",
        "en_name": "Tail Stinger",
        "description": "近战攻击检定：+14，触及10尺。\n命中：16（2d6+9）穿刺伤害外加35（10d6）毒素伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "吞咽",
        "en_name": "Swallow",
        "description": "敏捷豁免检定：DC19，单一不超过大型的正受擒于紫虫的生物（紫虫同时能吞咽的生物数上限为三）。\n失败：紫虫吞咽目标，并结束其受擒状态。被吞咽期间，目标陷入目盲和束缚状态，对紫虫体外的攻击或其他效应而言处于全身掩护\n，并在紫虫的回合开始时受到17（5d6）强酸伤害。若一回合内紫虫体内的一名生物对紫虫造成至少30伤害，紫虫在该回合结束时必须成功通过一次DC21的体质豁免，否则将吐出所有生物，使其落在紫虫5尺内的空间并陷入倒地状态。若紫虫死亡，被吞咽生物不再被束缚并可以使用20尺移动力以倒地状态脱离尸体。"
      }
    ],
    "source_file": "怪兽\\紫虫.htm"
  },
  {
    "name": "美杜莎",
    "en_name": "Medusa",
    "type_line": "中型怪兽，守序邪恶",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "守序邪恶",
    "ac": 15,
    "initiative_bonus": 6,
    "initiative_total": 16,
    "hp": 127,
    "hp_formula": "17d8+51",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 4
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "欺瞒": 5,
      "察觉": 4,
      "隐匿": 6
    },
    "senses": {
      "黑暗视觉": 150,
      "被动察觉": 14
    },
    "languages": "通用语以及一门其他语言",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "美杜莎发动两次爪击和一次蛇发攻击，或是发动三次毒素射线攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+6，触及5尺。命中：10（2d6+3）挥砍伤害。"
      },
      {
        "name": "蛇发",
        "en_name": "Snake Hair",
        "description": "近战攻击检定：+6，触及5尺。命中：5（1d4+3）穿刺伤害外加14（4d6）毒素伤害。"
      },
      {
        "name": "毒素射线",
        "en_name": "Poison Ray",
        "description": "远程攻击检定：+5，射程150尺。命中：11（2d8+2）毒素伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "石化凝视",
        "en_name": "Petrifying Gaze",
        "description": "体质豁免检定：DC13，30尺锥状区域内的每名生物。若美杜莎在锥形区域内看到自己的倒影，其也必须进行此豁免。首次失败：目标陷入束缚状态，目标在下个回合结束时仍处于束缚则重复豁免，成功则终止其身上的该效应。再次失败：目标陷入石化状态替代其束缚状态。",
        "params": "充能5~6"
      }
    ],
    "source_file": "怪兽\\美杜莎.htm"
  },
  {
    "name": "蛛化卓尔",
    "en_name": "Drider",
    "type_line": "大型怪兽，混乱邪恶",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "混乱邪恶",
    "ac": 19,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 123,
    "hp_formula": "13d10+52",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "察觉": 6,
      "隐匿": 10
    },
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 16
    },
    "languages": "精灵语，地底通用语",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "traits": [
      {
        "name": "蛛行",
        "en_name": "Spider Climb",
        "description": "蛛化卓尔可以在难以攀爬的表面上攀爬，包括沿着天花板移动，且无需为此进行属性检定。"
      },
      {
        "name": "日光敏感",
        "en_name": "Sunlight Sensitivity",
        "description": "若蛛化卓尔身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      },
      {
        "name": "蛛网行者",
        "en_name": "Sunlight Sensitivity",
        "description": "蛛化卓尔在蛛网上移动时无视蛛网造成的移动限制，且与蛛网接触期间，蛛化卓尔可以知道其他与该蛛网接触生物的准确位置。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蛛化卓尔使用前肢或毒素迸发发动共计三次攻击。"
      },
      {
        "name": "前肢",
        "en_name": "Foreleg",
        "description": "近战攻击检定：+7，触及10尺。命中：13（2d8+4）穿刺伤害。"
      },
      {
        "name": "毒素迸发",
        "en_name": "Poison Burst",
        "description": "远程攻击检定：+6，射程120尺。命中：13（3d6+3）毒素伤害"
      }
    ],
    "bonus_actions": [
      {
        "name": "蜘蛛女王之魔法",
        "en_name": "Magic of the Spider Queen",
        "description": "蛛化卓尔施展黑暗术Darkness，妖火Faerie \nFire或蛛网术Web，无需材料成分并使用感知作为施法属性（法术豁免DC \n14）。",
        "params": "充能5~6"
      }
    ],
    "source_file": "怪兽\\蛛化卓尔.htm"
  },
  {
    "name": "锈蚀怪",
    "en_name": "Rust Monster",
    "type_line": "中型怪兽，无阵营",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 14,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 33,
    "hp_formula": "6d8+6",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "无",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "嗅铁",
        "en_name": "Iron Scent",
        "description": "锈蚀怪可以精准定位30尺内的含铁金属。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "锈蚀怪发动一次啃咬攻击并使用两次触角。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+3，触及5尺。\n命中：5（1d8+1）穿刺伤害。"
      },
      {
        "name": "触角",
        "en_name": "Antennae",
        "description": "锈蚀怪从位于其5尺内的一名生物身上，选择一件其着装或携带的非魔法金属物件（护甲或武器）为目标。\n敏捷豁免检定：DC11，着装或携带此物件的生物。\n失败：物件提供的AC（护甲）或进行的攻击检定（武器）获得-1减值。护甲AC降至10、武器减值达到-5时，物件被摧毁。对护甲和武器施展法术修复术Mending可以移除该减值。"
      },
      {
        "name": "摧毁金属",
        "en_name": "Destroy Metal",
        "description": "锈蚀怪触碰一件位于其5尺内的未被着装或携带的非魔法金属物件。此触碰将摧毁该物件上一处1尺立方区域内的部分。"
      }
    ],
    "reactions": [
      {
        "name": "自发触角",
        "en_name": "Reflexive Antennae",
        "description": "触发：锈蚀怪被一次攻击检定命中。\n响应：锈蚀怪使用触角。"
      }
    ],
    "source_file": "怪兽\\锈蚀怪.htm"
  },
  {
    "name": "青足龙蛇",
    "en_name": "Behir",
    "type_line": "巨型怪兽，中立邪恶",
    "size": "Huge",
    "creature_type": "怪兽",
    "alignment": "中立邪恶",
    "ac": 17,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 168,
    "hp_formula": "16d12+64",
    "speed": {
      "walk": "50尺，攀爬50尺"
    },
    "abilities": {
      "力量": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "察觉": 6,
      "隐匿": 7
    },
    "damage_immunities": [
      "闪电"
    ],
    "senses": {
      "黑暗视觉": 90,
      "被动察觉": 16
    },
    "languages": "龙语",
    "cr": 11,
    "xp": 7200,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "青足龙蛇发动一次啃咬攻击并使用绞缠。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+10，触及10尺。\n命中：19（2d12+6）穿刺伤害外加11（2d10）闪电伤害。"
      },
      {
        "name": "绞缠",
        "en_name": "Constrict",
        "description": "力量豁免检定：DC18，单一5尺内体型不超过大型且青足龙蛇可见的生物。\n失败：28（5d8+6）钝击伤害，目标陷入受擒状态（逃脱DC16），且目标陷入束缚状态直至擒抱结束。"
      },
      {
        "name": "闪电吐息",
        "en_name": "Lighting Breath",
        "description": "敏捷豁免检定：DC16，90尺长、5尺宽的线状区域内的每名生物。\n失败：66（12d10）闪电伤害。\n成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "bonus_actions": [
      {
        "name": "吞咽",
        "en_name": "Swallow",
        "description": "敏捷豁免检定：DC18，单一不超过大型的正受擒于青足龙蛇的生物（青足龙蛇同时能吞咽的生物数上限为一）。\n失败：青足龙蛇吞咽目标，并结束其受擒状态。被吞咽期间，目标陷入目盲和束缚状态，对青足龙蛇体外的攻击或其他效应而言处于全身掩护\n，并在青足龙蛇的回合开始时受到21（6d6）强酸伤害。若一回合内青足龙蛇体内的一名生物对青足龙蛇造成至少30伤害，青足龙蛇在该回合结束时必须成功通过一次DC14的体质豁免，否则将吐出那名生物，使其落在青足龙蛇10尺内的空间并陷入倒地状态。若青足龙蛇死亡，被吞咽生物不再被束缚并可以使用15尺移动力逃离尸体，以倒地状态脱离。"
      }
    ],
    "source_file": "怪兽\\青足龙蛇.htm"
  },
  {
    "name": "食腐虫",
    "en_name": "Carrion Crawler",
    "type_line": "大型怪兽，无阵营",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 13,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 51,
    "hp_formula": "6d10+18",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "skills": {
      "察觉": 5
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 15
    },
    "languages": "无",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "蛛行",
        "en_name": "Spider Climb",
        "description": "食腐虫可以在难以攀爬的表面上攀爬，包括沿着天花板移动，且不需要为此进行属性检定。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "食腐虫使用麻痹触须并发动一次啃咬攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+4，触及5尺。命中：7（2d4+2）穿刺伤害，外加3（1d6）毒素伤害。"
      },
      {
        "name": "麻痹触须",
        "en_name": "Paralyzing Tentacles",
        "description": "体质豁免检定：DC12，单一10尺内食腐虫可见的生物。"
      }
    ],
    "source_file": "怪兽\\食腐虫.htm"
  },
  {
    "name": "骏鹰",
    "en_name": "Hippogriff",
    "type_line": "大型怪兽，无阵营",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 11,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 26,
    "speed": {
      "walk": "40尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 5
    },
    "senses": {
      "被动察觉": 15
    },
    "languages": "无",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "飞掠",
        "en_name": "Flyby",
        "description": "骏鹰飞行离开敌人的触及范围时不会引发借机攻击。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "骏鹰发动两次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+5，触及5尺。\n命中：7（1d8+3）挥砍伤害。"
      }
    ],
    "source_file": "怪兽\\骏鹰.htm"
  },
  {
    "name": "鸟妖",
    "en_name": "Harpy",
    "type_line": "中型怪兽, 混乱邪恶",
    "size": "Medium",
    "creature_type": "怪兽, 混乱邪恶",
    "alignment": "",
    "ac": 11,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 38,
    "hp_formula": "7d8+7",
    "speed": {
      "walk": "20尺、飞行40尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "senses": {
      "被动察觉": 10
    },
    "languages": "通用语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "actions": [
      {
        "name": "利爪",
        "en_name": "Claw",
        "description": "近战攻击检定：+3，触及5尺。命中：6（2d4+1）点挥砍伤害。"
      },
      {
        "name": "诱惑之歌",
        "en_name": "Luring Song",
        "description": "鸟妖唱出一段魔法的旋律，歌声持续至鸟妖对其的专注终止。感知豁免检定：DC11，歌声开始时位于源自鸟妖的300尺光环区域内的每名类人生物与巨人生物。\n失败：目标陷入魅惑状态，直至歌声结束。目标在其回合结束时重复豁免。魅惑期间，目标陷入失能状态并无视其他鸟妖的诱惑之歌动作。若目标与鸟妖之间的距离大于5尺，其会在自己回合中以最直接的路径向鸟妖移动，尝试到达鸟妖5尺内。此移动不会避免借机攻击；不过每当其将要移动到伤害性地形（例如岩浆或坑陷），或是每当其受到来源于魅惑其的鸟妖以外的伤害时，其都能重复豁免。\n成功：目标在24小时内免疫此鸟妖的诱惑之歌。"
      }
    ],
    "source_file": "怪兽\\鸟妖.htm"
  },
  {
    "name": "鹏鸟",
    "en_name": "Roc",
    "type_line": "超巨型怪兽，无阵营",
    "size": "Gargantuan",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 15,
    "initiative_bonus": 8,
    "initiative_total": 18,
    "hp": 248,
    "speed": {
      "walk": "20尺，飞行120尺"
    },
    "abilities": {
      "力量": {
        "score": 28,
        "mod": 9,
        "save": 9
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 4
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 4
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 8
    },
    "senses": {
      "被动察觉": 18
    },
    "languages": "无",
    "cr": 11,
    "xp": 7200,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鹏鸟发动两次喙啄攻击。其可以将其中一次攻击替换为禽爪攻击。"
      },
      {
        "name": "喙啄",
        "en_name": "Beak",
        "description": "近战攻击检定：+13，触及10尺\n。命中：28（3d12+9）穿刺伤害。"
      },
      {
        "name": "禽爪",
        "en_name": "Talons",
        "description": "近战攻击检定：+13，触及5尺。\n命中：24（4d6+9）挥砍伤害，若目标生物体型不超过巨型，其被鹏鸟的两只禽爪擒抱，陷入受擒状态（逃脱DC19），且其受擒期间陷入束缚状态。"
      }
    ],
    "bonus_actions": [
      {
        "name": "鹏落",
        "en_name": "Swoop",
        "description": "若鹏鸟已令一名生物陷入受擒，鹏鸟飞行至多等于其飞行速度一半的距离并丢下此生物，此移动不会引发借机攻击。",
        "params": "充能5~6"
      }
    ],
    "source_file": "怪兽\\鹏鸟.htm"
  },
  {
    "name": "鹿鹰",
    "en_name": "Peryton",
    "type_line": "中型怪兽，混乱邪恶",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "混乱邪恶",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 33,
    "speed": {
      "walk": "20尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 5,
      "隐匿": 3
    },
    "senses": {
      "被动察觉": 15
    },
    "languages": "理解通用语和精灵语，但不会说",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "飞掠",
        "en_name": "Flyby",
        "description": "鹿鹰飞行离开敌人的触及时不会引发借机攻击。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鹿鹰发动一次角刺攻击和一次禽爪攻击。"
      },
      {
        "name": "角刺",
        "en_name": "Gore",
        "description": "近战攻击检定：+5，触及5尺。\n命中：7（1d8+3）穿刺伤害，若鹿鹰在此次攻击前立即向着目标直线移动了30+尺，则目标额外受到9（2d8）穿刺伤害。"
      },
      {
        "name": "禽爪",
        "en_name": "Talons",
        "description": "近战攻击检定：+5，触及5尺。\n命中：8（2d4+3）挥砍伤害。若类人目标因此伤害生命值降至0，鹿鹰掏出目标的心脏来杀死目标。"
      }
    ],
    "source_file": "怪兽\\鹿鹰.htm"
  },
  {
    "name": "人工生命体",
    "en_name": "Homunculus",
    "type_line": "微型构装，中立",
    "size": "Tiny",
    "creature_type": "构装",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 4,
    "speed": {
      "walk": "20尺，飞行40尺"
    },
    "abilities": {
      "力量": {
        "score": 4,
        "mod": -3,
        "save": -3
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": 0
      }
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑、中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "理解通用语以及一门其他语言，但不会说",
    "cr": 0,
    "xp": 10,
    "pb": 2,
    "traits": [
      {
        "name": "心灵连结",
        "en_name": "Telepathic Bond",
        "description": "只要人工生命体与其主人处于同一位面，双方就可以通过心灵感应交流。"
      }
    ],
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+4，触及5尺。\n命中：1点穿刺伤害，且目标受以下效果影响。体质豁免检定：DC12。\n失败：目标陷入中毒状态，直至人工生命体的下个回合结束。失败差值5或更多：\n目标陷入中毒状态，持续1分钟。中毒期间，目标陷入昏迷状态，昏迷在其受到伤害时提前结束。"
      }
    ],
    "source_file": "构装\\人工生命体.htm"
  },
  {
    "name": "恐怖铠甲",
    "en_name": "Helmed Horror",
    "type_line": "中型构装，中立",
    "size": "Medium",
    "creature_type": "构装",
    "alignment": "中立",
    "ac": 20,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 67,
    "hp_formula": "9d8+27",
    "speed": {
      "walk": "30尺，飞行30尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "languages": "理解通用语以及一门其他语言，但不会说",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "恐怖铠甲对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "法术免疫",
        "en_name": "Spell Immunity",
        "description": "恐怖铠甲免疫由其创造者所选择的三种法术。典型的选择包括灼热金属Heat Metal，闪电束Lightning Bolt和魔法飞弹Magic Missile。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "恐怖铠甲发动两次奥能利剑攻击。"
      },
      {
        "name": "奥能利剑",
        "en_name": "Arcane Sword",
        "description": "近战攻击检定：+6，触及5尺。命中：8（1d8+4）挥砍伤害外加5（1d10）力场伤害。"
      }
    ],
    "source_file": "构装\\恐怖铠甲.htm"
  },
  {
    "name": "盾卫",
    "en_name": "Shield Guardian",
    "type_line": "大型构装，无阵营",
    "size": "Large",
    "creature_type": "构装",
    "alignment": "无阵营",
    "ac": 17,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 142,
    "hp_formula": "15d10+60",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 3,
        "mod": -4,
        "save": -4
      }
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "麻痹",
      "石化",
      "中毒"
    ],
    "senses": {
      "盲视": 10,
      "被动察觉": 10
    },
    "languages": "理解用任何语言下达的命令，但不会说",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "traits": [
      {
        "name": "连接",
        "en_name": "Bound",
        "description": "盾卫与一个命令护符魔法性地相连。在盾卫和其命令护符位于同一存在位面期间，命令护符的佩戴者可以心灵感应般的呼唤盾卫来到自己的位置，并且盾卫知晓自己与命令护符的距离及其位置。如果盾卫位于命令护符佩戴者60尺范围内，佩戴者所承受到的任何伤害的一半（向上取整）都会转移给盾卫。"
      },
      {
        "name": "再生",
        "en_name": "Regeneration",
        "description": "若盾卫至少拥有1生命值，则其在自己回合开始时回复10生命值。"
      },
      {
        "name": "法术储存",
        "en_name": "Spell Storing",
        "description": "一名携带着盾卫命令护符的施法者可以让盾卫储存一道四环及以下的法术。为此，护符携带者必须在盾卫5尺内施展那道法术。此时该法术不会产生任何效应，而是被储存在盾卫之中。新法术储存时先前储存的旧法术将会消失。盾卫可以在法术储存者预先设定的条件满足时将其施展，无需法术成分并使用法术储存者的施法属性。储存其内的法术随后消失。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "盾卫发动两次拳击攻击。"
      },
      {
        "name": "拳击",
        "en_name": "Fist",
        "description": "近战攻击检定：+7，触及10尺。命中：11（2d6+4）钝击伤害外加7（2d6）力场伤害。"
      }
    ],
    "reactions": [
      {
        "name": "守护",
        "en_name": "Protection",
        "description": "触发：盾卫的护符携带者在盾卫的5尺内被一次攻击检定命中。响应：携带者的AC获得+5的加值，持续至盾卫的下个回合开始，这包括了对抗触发攻击的AC，并可能令那次攻击改为失手。"
      }
    ],
    "source_file": "构装\\盾卫.htm"
  },
  {
    "name": "稻草人",
    "en_name": "Scarecrow",
    "type_line": "中型构装，混乱邪恶",
    "size": "Medium",
    "creature_type": "构装",
    "alignment": "混乱邪恶",
    "ac": 11,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 27,
    "hp_formula": "6d8",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "damage_vulnerabilities": [
      "火焰"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑、力竭、恐慌、麻痹、石化、中毒、昏迷"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "通用语以及一门其他语言",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "actions": [
      {
        "name": "惧怖爪",
        "en_name": "Fearsome Claw",
        "description": "近战攻击检定：+3，触及5尺。命中：6（2d4+1）点挥砍伤害，且目标陷入恐慌状态，持续至稻草人的下个回合结束。"
      },
      {
        "name": "惊惧凝视",
        "en_name": "Terrifying Glare",
        "description": "感知豁免检定：DC11，单一30尺内稻草人可见的生物。失败：目标陷入恐慌状态，持续至稻草人的下个回合结束。恐慌期间，目标陷入麻痹状态。"
      }
    ],
    "source_file": "构装\\稻草人.htm"
  },
  {
    "name": "树人",
    "en_name": "Treant",
    "type_line": "巨型植物，混乱善良",
    "size": "Huge",
    "creature_type": "植物",
    "alignment": "混乱善良",
    "ac": 16,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 138,
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "damage_vulnerabilities": [
      "火焰"
    ],
    "damage_resistances": [
      "钝击",
      "穿刺"
    ],
    "senses": {
      "被动察觉": 13
    },
    "languages": "通用语，德鲁伊语，精灵语，木族语",
    "cr": 9,
    "xp": 5000,
    "pb": 4,
    "traits": [
      {
        "name": "攻城怪物",
        "en_name": "Siege Monster",
        "description": "树人对物件和建筑物造成双倍伤害。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "树人发动两次猛击攻击。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": ""
      },
      {
        "name": "碎木飞刺",
        "en_name": "Hail of Bark",
        "description": "远程攻击检定：+10，射程180尺。\n命中： 28 \n（4d10 + 6）穿刺伤害。"
      },
      {
        "name": "活化树木",
        "en_name": "Animate \nTrees",
        "description": "树人用魔法活化60尺内其可见的至多两棵树木。每颗被活化的树木均使用树人Treant的数据卡，但有以下区别：树木的智力和魅力值为1且无法说话，并缺少活化树木动作。树木服从树人的命令，使用与树人一样的先攻并在其回合结束后立即执行回合。树木的活化持续1日，或在以下情况提前结束：其死亡时、该树人死亡时或其与该树人之间的距离超过120尺时。解除活化后，若条件允许，树木重新扎根。",
        "params": "1/日"
      }
    ],
    "source_file": "植物\\树人.htm"
  },
  {
    "name": "蔓生怪",
    "en_name": "Shambling Mound",
    "type_line": "大型植物，无阵营",
    "size": "Large",
    "creature_type": "植物",
    "alignment": "无阵营",
    "ac": 15,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 110,
    "hp_formula": "13d10+39",
    "speed": {
      "walk": "30尺，游泳20尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "skills": {
      "隐匿": 3
    },
    "damage_resistances": [
      "寒冷",
      "火焰"
    ],
    "damage_immunities": [
      "闪电"
    ],
    "condition_immunities": [
      "耳聋",
      "力竭"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 10
    },
    "languages": "无",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "闪电吸收",
        "en_name": "Lightning Absorption",
        "description": "每当蔓生怪将受闪电伤害时，其恢复等于闪电伤害数值的生命值。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蔓生怪发动三次带电卷须攻击。其可以将其中一次攻击替换为使用吞没。"
      },
      {
        "name": "带电卷须",
        "en_name": "Charged Tendril",
        "description": "近战攻击检定：+7，触及10尺。"
      },
      {
        "name": "吞没",
        "en_name": "Engulf",
        "description": "力量豁免检定：DC15，单一5尺内不超过中型的生物。\n失败：目标被拉入蔓生怪所在空间并陷入受擒状态（逃脱DC14）。且目标陷入目盲和束缚状态，并在其回合开始时受到10（3d6）闪电伤害，直至擒抱解除。当蔓生怪移动时，受擒目标也会随之移动，且蔓生怪无需额外消耗移动力。蔓生怪以此动作同时令其陷入受擒状态的生物数上限为一。"
      }
    ],
    "source_file": "植物\\蔓生怪.htm"
  },
  {
    "name": "凝胶方块",
    "en_name": "Gelatinous Cube",
    "type_line": "大型泥怪，无阵营",
    "size": "Large",
    "creature_type": "泥怪",
    "alignment": "无阵营",
    "ac": 6,
    "initiative_bonus": -4,
    "initiative_total": 6,
    "hp": 63,
    "hp_formula": "6d10+30",
    "speed": {
      "walk": "15尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "damage_immunities": [
      "强酸"
    ],
    "condition_immunities": [
      "目盲、魅惑、耳聋、力竭、恐慌、倒地"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 8
    },
    "languages": "无",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "泥怪方块",
        "en_name": "Ooze Cube",
        "description": "方块会占满所处的整个空间且完全透明。其他生物可以进入此空间，但如此做的生物会承受方块的吞没影响，且其因此进行的豁免具有劣势。"
      },
      {
        "name": "透明",
        "en_name": "Transparent",
        "description": "即使凝胶方块处于生物的视野中，只要该生物未曾见到此方块的移动或其他行动，该生物必须成功通过一次DC \n15的感知（察觉）检定来察觉到凝胶方块。"
      }
    ],
    "actions": [
      {
        "name": "伪肢",
        "en_name": "Pseudopod",
        "description": "近战攻击检定：+4，触及5尺。命中：12（3d6+2）强酸伤害。"
      },
      {
        "name": "吞没",
        "en_name": "Engulf",
        "description": "凝胶方块移动至多等于其速度的距离且不会引发借机攻击。若方块体内有空间足以承载其（见泥怪方块特质），方块可以移动进入体型不超过大型的其他生物所处的空间。"
      }
    ],
    "source_file": "泥怪\\凝胶方块.htm"
  },
  {
    "name": "赭果冻",
    "en_name": "Ochre Jelly",
    "type_line": "大型泥怪，无阵营",
    "size": "Large",
    "creature_type": "泥怪",
    "alignment": "无阵营",
    "ac": 8,
    "initiative_bonus": -2,
    "initiative_total": 8,
    "hp": 52,
    "hp_formula": "7d10+14",
    "speed": {
      "walk": "20尺、攀爬20尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "damage_resistances": [
      "强酸"
    ],
    "damage_immunities": [
      "闪电、挥砍"
    ],
    "condition_immunities": [
      "魅惑、耳聋、力竭、恐慌、受擒、倒地、束缚"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 8
    },
    "languages": "无",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "无定形",
        "en_name": "Amorphous",
        "description": "果冻可以移动穿过最窄1寸宽的空间而无需消耗额外的移动力。"
      },
      {
        "name": "蛛行",
        "en_name": "Spider Climb",
        "description": "果冻可以在难以攀爬的表面上攀爬，包括沿着天花板移动，且无需为此进行属性检定。"
      }
    ],
    "actions": [
      {
        "name": "伪肢",
        "en_name": "Pseudopod",
        "description": "近战攻击检定：+4，触及5尺。命中：12（3d6+2）强酸伤害。"
      }
    ],
    "reactions": [
      {
        "name": "分裂",
        "en_name": "Split",
        "description": "触发：若果冻体型为大型或中型且具有10+生命值，当果冻进入浴血或其受闪电伤害或挥砍伤害时。响应：果冻分裂为两个全新的赭果冻Ochre \nJelly。每个新的果冻的体型都比原先的果冻小一级，且使用原果冻的先攻行动。原果冻的生命值将平均分配给新的果冻（向下取整）。"
      }
    ],
    "source_file": "泥怪\\赭果冻.htm"
  },
  {
    "name": "黑布丁",
    "en_name": "Black Pudding",
    "type_line": "大型泥怪，无阵营",
    "size": "Large",
    "creature_type": "泥怪",
    "alignment": "无阵营",
    "ac": 7,
    "initiative_bonus": -3,
    "initiative_total": 7,
    "hp": 68,
    "hp_formula": "8d10+24",
    "speed": {
      "walk": "20尺、攀爬20尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "damage_immunities": [
      "强酸、寒冷、闪电、挥砍"
    ],
    "condition_immunities": [
      "魅惑、耳聋、力竭、恐慌、受擒、倒地、束缚"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 8
    },
    "languages": "无",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "traits": [
      {
        "name": "无定形",
        "en_name": "Amorphous",
        "description": "布丁可以移动穿过最窄1寸宽的空间而无需消耗额外的移动力。"
      },
      {
        "name": "腐蚀形态",
        "en_name": "Corrosive Form",
        "description": "生物以近战攻击检定命中布丁时，其受到4（1d8）强酸伤害。非魔法弹药在命中布丁并造成伤害后立即被摧毁。非魔法武器在对布丁造成伤害后将积累-1的攻击检定减值。若武器的减值累计达到-5则其被摧毁。对武器施展修复术Mending可以移除这一减值。"
      },
      {
        "name": "蛛行",
        "en_name": "Spider Climb",
        "description": "布丁可以在难以攀爬的表面上攀爬，包括沿着天花板移动，且无需为此进行属性检定。"
      }
    ],
    "actions": [
      {
        "name": "消化伪肢",
        "en_name": "Dissolving Pseudopod",
        "description": "近战攻击检定：+5，触及10尺。命中：17（4d6+3）强酸伤害。目标着装的非魔法护甲提供的AC将承受-1的减值。若护甲的AC因减值降至10则其被摧毁。对护甲施展修复术Mending可以移除这一减值。"
      }
    ],
    "reactions": [
      {
        "name": "分裂",
        "en_name": "Split",
        "description": "触发：若布丁体型为大型或中型且具有10+生命值，当布丁进入浴血或是其将受闪电伤害或挥砍伤害时。响应：布丁分裂为两块全新的黑布丁Black Pudding。每块新的布丁的体型都比原先的布丁小一级，且使用原布丁的先攻行动。原布丁的生命值将平均分配给新的布丁（向下取整）。"
      }
    ],
    "source_file": "泥怪\\黑布丁.htm"
  },
  {
    "name": "刺客",
    "en_name": "Assassin",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 16,
    "initiative_bonus": 10,
    "initiative_total": 20,
    "hp": 97,
    "hp_formula": "15d8+30",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "特技": 7,
      "察觉": 6,
      "隐匿": 10
    },
    "damage_resistances": [
      "毒素"
    ],
    "equipment": "轻弩，短剑，镶钉皮甲",
    "senses": {
      "被动察觉": 16
    },
    "languages": "通用语，盗贼黑话",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "traits": [
      {
        "name": "反射闪避",
        "en_name": "Evasion",
        "description": "当刺客受到一个允许其进行敏捷豁免来只承受一半伤害的效应影响时，其豁免成功时不受伤害，豁免失败时只承受一半伤害。其无法在失能期间使用此特质。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "刺客使用短剑或轻弩发动共计三次攻击。"
      },
      {
        "name": "短剑",
        "en_name": "Shortsword",
        "description": "近战攻击检定：+7，触及5尺。命中：7（1d6+4）穿刺伤害外加17（5d6）毒素伤害，且目标陷入中毒状态直至刺客的下个回合开始。"
      },
      {
        "name": "轻弩",
        "en_name": "Light Crossbow",
        "description": "远程攻击检定：+7，射程80/320尺。命中：8（1d8+4）穿刺伤害外加21（6d6）毒素伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "灵巧动作",
        "en_name": "Cunning Action",
        "description": "刺客执行疾走、撤离或躲藏动作。"
      }
    ],
    "source_file": "类人\\刺客.htm"
  },
  {
    "name": "平民",
    "en_name": "Commoner",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 10,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 4,
    "hp_formula": "1d8",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "equipment": "短棒",
    "senses": {
      "被动察觉": 10
    },
    "languages": "通用语",
    "cr": 0,
    "xp": 10,
    "pb": 2,
    "traits": [
      {
        "name": "技艺受训",
        "en_name": "Training",
        "description": "平民具有某项技能熟练（由DM选择），且在进行使用该技能的属性检定时具有优势。"
      }
    ],
    "actions": [
      {
        "name": "短棒",
        "en_name": "Club",
        "description": "近战攻击检定：+2，触及5尺。命中：2（1d4）钝击伤害。"
      }
    ],
    "source_file": "类人\\平民.htm"
  },
  {
    "name": "德鲁伊",
    "en_name": "Druid",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 44,
    "hp_formula": "8d8+8",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "医药": 5,
      "自然": 3,
      "察觉": 5
    },
    "equipment": "镶钉皮甲",
    "senses": {
      "被动察觉": 15
    },
    "languages": "通用语，德鲁伊语，木族语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "德鲁伊使用荆藤法杖或苍翠之力发动共计两次攻击。"
      },
      {
        "name": "荆藤法杖",
        "en_name": "Vine Staff",
        "description": "近战攻击检定：+5，触及5尺。命中：7（1d8+3）钝击伤害外加2（1d4）毒素伤害。"
      },
      {
        "name": "苍翠之力",
        "en_name": "Verdant Wisp",
        "description": "远程攻击检定：+5，射程90尺。命中：10（3d6）光耀伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "德鲁伊施展以下一道法术，使用感知作为施法属性（法术豁免DC13）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "德鲁伊伎俩Druidcraft，动物交谈Speak with Animal"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "纠缠术Entangle，雷鸣波Thunderwave"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "动物信使Animal Messenger，大步奔行Longstrider，月华之光Moonbeam"
      }
    ],
    "source_file": "类人\\德鲁伊.htm"
  },
  {
    "name": "角斗士",
    "en_name": "Gladiator",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 16,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 112,
    "hp_formula": "15d8+45",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 5
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 4
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "运动": 10,
      "表演": 5
    },
    "equipment": "盾牌，矛（3），镶钉皮甲",
    "senses": {
      "被动察觉": 11
    },
    "languages": "通用语",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "角斗士发动三次矛攻击。其可以将其中一次攻击替换为使用盾击。"
      },
      {
        "name": "矛",
        "en_name": "Spear",
        "description": "近战或远程攻击检定：+7，触及5尺或射程20/60尺。命中：11（2d6+4）穿刺伤害。"
      },
      {
        "name": "盾击",
        "en_name": "Shield Bash",
        "description": "力量豁免检定：DC15，单一5尺内角斗士可见的生物。失败：9（2d4+4）钝击伤害。若目标生物体型不超过中型，则其陷入倒地状态。"
      }
    ],
    "reactions": [
      {
        "name": "格挡",
        "en_name": "Parry",
        "description": "触发：角斗士在持握武器期间因近战攻击检定被命中。响应：角斗士令其对抗那次攻击的AC+3，可能令那次攻击改为失手。"
      }
    ],
    "source_file": "类人\\角斗士.htm"
  },
  {
    "name": "化形胡狼",
    "en_name": "Jackalwere",
    "type_line": "小型邪魔，混乱邪恶",
    "size": "Small",
    "creature_type": "邪魔",
    "alignment": "混乱邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 18,
    "hp_formula": "4d6+4",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "欺瞒": 4,
      "察觉": 4,
      "隐匿": 4
    },
    "senses": {
      "黑暗视觉": 90,
      "被动察觉": 14
    },
    "languages": "通用语",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "集群战术",
        "en_name": "Pack Tactics",
        "description": "若化形胡狼的攻击目标生物5尺内存在有至少一名化形胡狼未失能的盟友，则化形胡狼对该生物进行的攻击检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "化形胡狼发动两次撕裂攻击或猛击攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）穿刺伤害。",
        "params": "仅胡狼或混合形态"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+4，触及5尺。命中：4（1d4+2）钝击伤害。",
        "params": "仅人类或混合形态"
      },
      {
        "name": "昏睡凝视",
        "en_name": "Sleep Gaze",
        "description": "感知豁免检定：DC10，单一30尺内化形胡狼可见的生物（此豁免构装和亡灵自动成功）。失败：目标陷入昏迷状态，持续10分钟，目标身上的此效应在其受到伤害或被目标5尺内的另一生物用一个动作摇醒时提前结束。 成功：目标在24小时内免疫此化形胡狼的昏睡凝视。",
        "params": "充能5~6"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "化形胡狼变形为中型的人类或类人与胡狼的混合形态（中型），或变回其真实形态（即小型胡狼）。除体型以外，其各形态下游戏数据均相同化形胡狼着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "邪魔\\化形胡狼.htm"
  },
  {
    "name": "地狱犬",
    "en_name": "Hell Hound",
    "type_line": "中型邪魔，守序邪恶",
    "size": "Medium",
    "creature_type": "邪魔",
    "alignment": "守序邪恶",
    "ac": 15,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 58,
    "hp_formula": "9d8+18",
    "speed": {
      "walk": "50尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 5
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 15
    },
    "languages": "理解炼狱语，但不会说",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "集群战术",
        "en_name": "Pack Tactics",
        "description": "若地狱犬的攻击目标生物5尺内存在有至少一名地狱犬未失能的盟友，则地狱犬对该生物进行的攻击检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "地狱犬发动两次啃咬攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：7（1d8+3）穿刺伤害外加3（1d6）火焰伤害。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC12，15尺锥状区域内的每名生物。失败：17（5d6）火焰伤害。成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "source_file": "邪魔\\地狱犬.htm"
  },
  {
    "name": "坎比翁",
    "en_name": "Cambion",
    "type_line": "中型邪魔，中立邪恶",
    "size": "Medium",
    "creature_type": "邪魔",
    "alignment": "中立邪恶",
    "ac": 19,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 105,
    "hp_formula": "14d8+42",
    "speed": {
      "walk": "30尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 6
      }
    },
    "skills": {
      "欺瞒": 6,
      "察觉": 4,
      "隐匿": 7
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电",
      "毒素"
    ],
    "damage_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 14
    },
    "languages": "深渊语，通用语，炼狱语",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "坎比翁使用爪击或火焰射线发动共计两次攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+7，触及5尺。命中：8（1d8+4）挥砍伤害，外加7（2d6）火焰伤害。"
      },
      {
        "name": "火焰射线",
        "en_name": "Fire Ray",
        "description": "远程攻击检定：+7，射程120尺。命中：13（3d6+3）火焰伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "坎比翁施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC14）："
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "变身术Alter Self，命令术Command（三环版本）， 侦测魔法Detect Magic"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "支配人类Dominate Person（八环版本）， 位面转移Plane Shift（仅自身）"
      }
    ],
    "source_file": "邪魔\\坎比翁.htm"
  },
  {
    "name": "恶鬼",
    "en_name": "Oni",
    "type_line": "大型邪魔，守序邪恶",
    "size": "Large",
    "creature_type": "邪魔",
    "alignment": "守序邪恶",
    "ac": 17,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 119,
    "hp_formula": "14d10+42",
    "speed": {
      "walk": "30尺、飞行30尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 3
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 4
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 5
      }
    },
    "skills": {
      "奥秘": 5
    },
    "damage_resistances": [
      "寒冷"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 14
    },
    "languages": "通用语、巨人语",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "traits": [
      {
        "name": "再生",
        "en_name": "Regeneration",
        "description": "若恶鬼至少拥有1生命值，则其在自己回合开始时回复10生命值。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "恶鬼发动两次爪击或噩梦射线攻击。其可以将其中一次攻击替换为使用施法。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+7，触及10尺。命中：10（1d12+4）挥砍伤害，外加9（2d8）点暗蚀伤害。"
      },
      {
        "name": "噩梦射线",
        "en_name": "Nightmare Ray",
        "description": "远程攻击检定：+5，射程60尺。命中：9（2d6+2）心灵伤害，且目标陷入恐慌状态，直至恶鬼的下个回合开始。"
      },
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "恶鬼变形为小型或中型的类人生物或大型的巨人生物，或变回其真实形态。除体型以外，其各形态下游戏数据均相同。恶鬼着装或携带的任何装备都不会随之变化。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "恶鬼施展以下一道法术，无需材料成分且使用魅力作为施法属性（法术豁免DC13）："
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "魅惑人类Charm Person（二环版本）、 黑暗术Darkness、气化形体Gaseous Form、睡眠术Sleep"
      }
    ],
    "bonus_actions": [
      {
        "name": "隐形",
        "en_name": "Invisibility",
        "description": "恶鬼对自身施展隐形术Invisibility，无需法术成分并使用与施法动作相同的施法属性。"
      }
    ],
    "source_file": "邪魔\\恶鬼.htm"
  },
  {
    "name": "拉迷亚",
    "en_name": "Lamia",
    "type_line": "大型邪魔，混乱邪恶",
    "size": "Large",
    "creature_type": "邪魔",
    "alignment": "混乱邪恶",
    "ac": 13,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 97,
    "hp_formula": "13d10+26",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "欺瞒": 7,
      "洞悉": 4,
      "隐匿": 5
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 12
    },
    "languages": "深渊语，通用语",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "拉迷亚发动两次爪击攻击。其可以将其中一次攻击替换为使用腐败之触。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+5，触及5尺。命中：7（1d8+3）挥砍伤害，外加7（2d6）心灵伤害。"
      },
      {
        "name": "腐败之触",
        "en_name": "Corrupting Touch",
        "description": "感知豁免检定：DC13，单一5尺内拉迷亚可见的生物。失败：13（3d8）心灵伤害，且目标被诅咒，持续1小时。目标陷入魅惑和中毒状态，直至诅咒结束。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "拉迷亚施展以下一道法术，无需任材料成分并使用魅力作为施法属性（法术豁免DC13）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "易容术Disguise Self（可易容为大型或中型两足动物）， 次级幻象Minor Illusion"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "指使术Geas，高级幻影Major Image，探知Scrying"
      }
    ],
    "bonus_actions": [
      {
        "name": "跳跃",
        "en_name": "Leap",
        "description": "拉迷亚消耗10尺移动力跳跃至多30尺。"
      }
    ],
    "source_file": "邪魔\\拉迷亚.htm"
  },
  {
    "name": "梦魇",
    "en_name": "Nightmare",
    "type_line": "大型邪魔，中立邪恶",
    "size": "Large",
    "creature_type": "邪魔",
    "alignment": "中立邪恶",
    "ac": 13,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 68,
    "hp_formula": "8d10+24",
    "speed": {
      "walk": "60尺，飞行90尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "被动察觉": 11
    },
    "languages": "理解深渊语，通用语和炼狱语，但不会说",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "赋予火焰抗性",
        "en_name": "Confer Fire Resistance",
        "description": "骑乘梦魇期间，梦魇可以赋予一名骑手对火焰伤害的抗性。"
      },
      {
        "name": "照明",
        "en_name": "Illumination",
        "description": "梦魇散发出半径10尺的明亮光照以及额外10尺的微光光照。"
      }
    ],
    "actions": [
      {
        "name": "蹄击",
        "en_name": "Hooves",
        "description": "近战攻击检定：+6，触及5尺。命中：13（2d8+4）钝击伤害外加10（3d6）火焰伤害。"
      },
      {
        "name": "以太折跃",
        "en_name": "Ethereal Stride",
        "description": "梦魇和其5尺内至多三名自愿的生物一起从物质位面传送至以太位面，或反之。"
      }
    ],
    "source_file": "邪魔\\梦魇.htm"
  },
  {
    "name": "梦魔",
    "en_name": "Incubus",
    "type_line": "中型邪魔，中立邪恶",
    "size": "Medium",
    "creature_type": "邪魔",
    "alignment": "中立邪恶",
    "ac": 15,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 66,
    "hp_formula": "12d8+12",
    "speed": {
      "walk": "30尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 5
      }
    },
    "skills": {
      "欺瞒": 9,
      "洞悉": 5,
      "察觉": 5,
      "游说": 9,
      "隐匿": 7
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "毒素",
      "心灵"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 15
    },
    "languages": "深渊语，通用语，炼狱语；心灵感应60尺",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "traits": [
      {
        "name": "化身魅魔",
        "en_name": "Succubus Form",
        "description": "梦魔在完成一次长休时可以变形为魅魔Succubus，并使用魅魔的游戏数据替代其原来的数据。梦魔着装或携带的任何装备都不会随之变化。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "梦魔发动两次毁梦之触攻击。"
      },
      {
        "name": "毁梦之触",
        "en_name": "Restless Touch",
        "description": "近战攻击：+7，触及5尺。命中：15（3d6+5）心灵伤害，且目标被诅咒，持续24小时或在梦魔死亡时提前结束。受诅咒期间，目标无法从完成短休中获益。。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "梦魔施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "易容术Disguise Self，以太化Etherealness"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "托梦术Dream，催眠图纹Hypnotic"
      }
    ],
    "bonus_actions": [
      {
        "name": "噩梦",
        "en_name": "Nightmare",
        "description": "感知豁免检定：DC15，单一60尺内梦魔可见的生物。失败：若目标的生命值为20或更低，则其陷入昏迷状态，持续1小时并在其受到伤害或被目标5尺内的另一生物用一个动作摇醒时提前结束；否则，目标受到18（4d8）心灵伤害。",
        "params": "充能6"
      }
    ],
    "source_file": "邪魔\\梦魔.htm"
  },
  {
    "name": "罗刹",
    "en_name": "Rakshasa",
    "type_line": "中型邪魔，守序邪恶",
    "size": "Medium",
    "creature_type": "邪魔",
    "alignment": "守序邪恶",
    "ac": 17,
    "initiative_bonus": 8,
    "initiative_total": 18,
    "hp": 221,
    "hp_formula": "26d8+104",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 5
      }
    },
    "skills": {
      "欺瞒": 10,
      "洞悉": 8,
      "察觉": 8
    },
    "damage_vulnerabilities": [
      "受法术祝福术Bless效应影响的生物所持握的武器造成的穿刺伤害"
    ],
    "damage_immunities": [
      "魅惑",
      "恐慌"
    ],
    "senses": {
      "真实视觉": 60,
      "被动察觉": 18
    },
    "languages": "通用语，炼狱语",
    "cr": 13,
    "xp": 10000,
    "pb": 5,
    "traits": [
      {
        "name": "高等魔法抗性",
        "en_name": "Greater Magic Resistance",
        "description": "罗刹对抗法术和其他魔法效应时进行的豁免检定自动成功，且法术的攻击检定对其自动失手。没有罗刹的允许，任何法术都无法远程探查罗刹或是侦测其思想、生物类型或阵营。"
      },
      {
        "name": "邪魔复苏",
        "en_name": "Fiendish Restoration",
        "description": "若罗刹于九层地狱之外死去，其身躯会化为脓水，并立即在九层地狱某处获得一具新的身体，以满生命值复活。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "罗刹发动三次诅咒之触攻击。"
      },
      {
        "name": "诅咒之触",
        "en_name": "Cursed Touch",
        "description": "近战攻击检定：+10，触及5尺。命中：12（2d6+5）挥砍伤害外加19（3d12）暗蚀伤害。若目标为生物，则其被诅咒。被诅咒期间，目标无法从完成短休或长休中获益。"
      },
      {
        "name": "恶毒命令",
        "en_name": "Baleful Command",
        "description": "感知豁免检定：DC18，源自罗刹的30尺光环区域内的每名敌人。失败： 28（8d6）心灵伤害，且目标陷入恐慌与失能状态，持续至罗刹的下个回合开始。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "罗刹施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC18）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，侦测思想Detect Thoughts，易容术Disguise Self，法师之手Mage Hand，次级幻象Minor Illusion"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "飞行术Fly，隐形术Invisibility，高级幻影Major Image，位面转移Plane Shift"
      }
    ],
    "source_file": "邪魔\\罗刹.htm"
  },
  {
    "name": "魅魔",
    "en_name": "Succubus",
    "type_line": "中型邪魔，中立邪恶",
    "size": "Medium",
    "creature_type": "邪魔",
    "alignment": "中立邪恶",
    "ac": 15,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 71,
    "hp_formula": "13d8+13",
    "speed": {
      "walk": "30尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 5
      }
    },
    "skills": {
      "欺瞒": 9,
      "洞悉": 5,
      "察觉": 5,
      "游说": 9,
      "隐匿": 7
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "毒素",
      "心灵"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 15
    },
    "languages": "深渊语，通用语，炼狱语；心灵感应60尺",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "traits": [
      {
        "name": "化身梦魔",
        "en_name": "Incubus Form",
        "description": "魅魔在完成一次长休时可以变形为梦魔Incubus，并使用梦魔的游戏数据替代其原来的数据。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "魅魔发动一次魔性之触攻击并使用魅惑或汲命之吻。"
      },
      {
        "name": "魔性之触",
        "en_name": "Fiendish Touch",
        "description": "近战攻击：+7，触及5尺。命中：16（2d10+5）心灵伤害。"
      },
      {
        "name": "魅惑",
        "en_name": "Charm",
        "description": "魅魔施展支配类人Dominate \nPerson （八环版本），无需法术成分并使用魅力作为施法属性（法术豁免DC15）。"
      },
      {
        "name": "汲命之吻",
        "en_name": "Draining Kiss",
        "description": "体质豁免：DC15，单一5尺内魅惑于魅魔的生物。失败：13（3d8）心灵伤害。成功：半伤。失败或成功：目标的生命值上限减少等于其受到伤害的数值"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "魅魔变形为小型或中型的类人生物，或变回其真实形态。除飞行速度仅其真实形态可用以外，其各形态下游戏数据均相同。魅魔着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "邪魔\\魅魔.htm"
  },
  {
    "name": "伪龙",
    "en_name": "Pseudodragon",
    "type_line": "微型龙类，中立善良",
    "size": "Tiny",
    "creature_type": "龙类",
    "alignment": "中立善良",
    "ac": 14,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 10,
    "hp_formula": "3d4+3",
    "speed": {
      "walk": "15尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 5,
      "隐匿": 4
    },
    "senses": {
      "盲视": 10,
      "被动察觉": 15
    },
    "languages": "理解通用语和龙语，但不会说",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "伪龙对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "伪龙发动两次啃咬攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+4，触及5尺。命中：4（1d4+2）穿刺伤害。"
      },
      {
        "name": "蛰刺",
        "en_name": "Sting",
        "description": "体质豁免检定：DC12，单一5尺内伪龙可见的生物。失败：5（2d4）毒素伤害，且目标陷入中毒状态，持续1小时。失败差值5或更多：目标在中毒期间还会陷入昏迷状态，昏迷在其受到伤害或被目标5尺内的一名生物用一个动作摇醒时提前结束。"
      }
    ],
    "source_file": "龙类\\伪龙.htm"
  },
  {
    "name": "半龙",
    "en_name": "Half-Dragon",
    "type_line": "中型龙类，中立",
    "size": "Medium",
    "creature_type": "龙类",
    "alignment": "中立",
    "ac": 18,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 105,
    "hp_formula": "14d8+42",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 5
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "运动": 7,
      "察觉": 5,
      "隐匿": 5
    },
    "damage_resistances": [
      "下文中龙族起源特质所选的伤害类型"
    ],
    "senses": {
      "盲视": 10
    },
    "languages": "通用语，龙语",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "龙族起源",
        "en_name": "Draconic Origin",
        "description": "半龙和某种龙类的联系令其与下列伤害类型中的一种相关联（由DM选择）：强酸、寒冷、火焰、闪电、毒素。这一选择会影响数据卡的其他部分。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "半龙发动两次爪击攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+7，触及10尺。命中：6（1d4+4）挥砍伤害外加7（2d6）伤害，类型为龙族起源特质所选的伤害类型。"
      },
      {
        "name": "龙之吐息",
        "en_name": "Dragon",
        "description": "敏捷豁免检定：DC14，30尺锥状区域内的每名生物。失败：28（8d6）伤害，类型为龙族起源特质所选的伤害类型。成功：半伤。"
      }
    ],
    "bonus_actions": [
      {
        "name": "跳跃",
        "en_name": "Leap",
        "description": "半龙消耗10尺移动力跳跃至多30尺。"
      }
    ],
    "source_file": "龙类\\半龙.htm"
  },
  {
    "name": "飞龙",
    "en_name": "Wyvern",
    "type_line": "大型龙类，无阵营",
    "size": "Large",
    "creature_type": "龙类",
    "alignment": "无阵营",
    "ac": 14,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 127,
    "hp_formula": "15d10+45",
    "speed": {
      "walk": "30尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 4
    },
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 14
    },
    "languages": "无",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "飞龙发动一次啃咬攻击和一次刺针攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+7，触及5尺。命中：13（2d8+4）穿刺伤害。"
      },
      {
        "name": "刺针",
        "en_name": "Sting",
        "description": "近战攻击检定：+7，触及10尺。命中：11（2d6+4）穿刺伤害外加24（7d6）毒素伤害，且目标陷入中毒状态，直至飞龙的下个回合开始。"
      }
    ],
    "source_file": "龙类\\飞龙.htm"
  },
  {
    "name": "龙龟",
    "en_name": "Dragon Turtle",
    "type_line": "超巨型龙类，中立",
    "size": "Gargantuan",
    "creature_type": "龙类",
    "alignment": "中立",
    "ac": 20,
    "initiative_bonus": 6,
    "initiative_total": 16,
    "hp": 356,
    "hp_formula": "23d20+115",
    "speed": {
      "walk": "20尺，游泳50尺"
    },
    "abilities": {
      "力量": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 11
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 7
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "damage_resistances": [
      "火焰"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 11
    },
    "languages": "龙语，原初语（水族语）",
    "cr": 17,
    "xp": 18000,
    "pb": 6,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "龙龟可以在空气和水中呼吸。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "龙龟发动三次啃咬攻击。其可以将其中一次攻击替换为一次尾击攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+13，触及15尺。"
      },
      {
        "name": "尾击",
        "en_name": "Tail",
        "description": "近战攻击检定：+13，触及15尺。命中：18（2d10+7）钝击伤害。若目标生物体型不超过巨型，则其陷入倒地状态。"
      },
      {
        "name": "蒸汽吐息",
        "en_name": "Steam Breath",
        "description": "体质豁免检定：DC19，60尺锥状区域内的每名生物。失败：56（16d6）火焰伤害。成功：半伤。失败或成功：受此火焰伤害者不会因身处水下而具有此火焰伤害的抗性。",
        "params": "充能5~6"
      }
    ],
    "source_file": "龙类\\龙龟.htm"
  },
  {
    "name": "妖精龙成体",
    "en_name": "Faerie Dragon Adult",
    "type_line": "微型龙类，混乱善良",
    "size": "Tiny",
    "creature_type": "龙类",
    "alignment": "混乱善良",
    "ac": 15,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 35,
    "hp_formula": "10d4+10",
    "speed": {
      "walk": "10尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "敏捷": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "奥秘": 4,
      "察觉": 3,
      "隐匿": 7
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 13
    },
    "languages": "龙语，木族语，心灵感应60尺（仅限妖精龙）",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "妖精龙对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+7，触及5尺。命中：7（1d4+5）穿刺伤害外加3（1d6）心灵伤害。"
      },
      {
        "name": "欢愉吐息",
        "en_name": "Euphoria Breath",
        "description": "感知豁免检定：DC13，15尺锥状区域内的每名生物。失败：目标陷入失能状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。 失能期间，目标在其回合必须消耗其全部移动力向一个随机方向移动。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "妖精龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC13）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "舞光术Dancing Lights，法师之手Mage Hand，次级幻象Minor Illusion"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "幻景Hallucinatory Terrain，变形术Polymorph"
      }
    ],
    "bonus_actions": [
      {
        "name": "进阶隐形",
        "en_name": "Superior Invisibility",
        "description": "妖精龙对自身施展高等隐形术Greater \nInvisibility \n，无需法术成分并使用与施法动作相同的施法属性。"
      }
    ],
    "source_file": "龙类\\妖精龙\\妖精龙成体.htm"
  },
  {
    "name": "妖精龙青年体",
    "en_name": "Faerie Dragon Youth",
    "type_line": "微型龙类，混乱善良",
    "size": "Tiny",
    "creature_type": "龙类",
    "alignment": "混乱善良",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 21,
    "hp_formula": "6d4+6",
    "speed": {
      "walk": "10尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "奥秘": 3,
      "察觉": 3,
      "隐匿": 5
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 13
    },
    "languages": "龙语，木族语，心灵感应60尺（仅妖精龙）",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "妖精龙对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：5（1d4+3）穿刺伤害外加2（1d4）心灵伤害。"
      },
      {
        "name": "欢愉吐息",
        "en_name": "Euphoria Breath",
        "description": "感知豁免检定：DC12，15尺锥状区域内的每名生物。失败：目标陷入失能状态直至其下个回合结束，且目标在那个回合必须消耗其全部移动力向一个随机方向移动。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "妖精龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC12）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "舞光术Dancing Lights，法师之手Mage Hand，次级幻象Minor Illusion"
      }
    ],
    "bonus_actions": [
      {
        "name": "进阶隐形",
        "en_name": "Superior Invisibility",
        "description": "妖精龙对自身施展高等隐形术Greater \nInvisibility，无需法术成分并使用与施法动作相同的施法属性。"
      }
    ],
    "source_file": "龙类\\妖精龙\\妖精龙青年体.htm"
  },
  {
    "name": "少年幽影龙",
    "en_name": "Juvenile Shadow Dragon",
    "type_line": "中型龙类，混乱邪恶",
    "size": "Medium",
    "creature_type": "龙类",
    "alignment": "混乱邪恶",
    "ac": 15,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 45,
    "hp_formula": "6d8+18",
    "speed": {
      "walk": "30尺，攀爬30尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 4
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 6
    },
    "damage_resistances": [
      "见活体幽影特质"
    ],
    "damage_immunities": [
      "暗蚀"
    ],
    "senses": {
      "盲视": 10,
      "被动察觉": 14
    },
    "languages": "通用语，龙语",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "traits": [
      {
        "name": "活体幽影",
        "en_name": "Living Shadow",
        "description": "若幽影龙身处微光光照或黑暗中，其具有对除力场、心灵、光耀外所有伤害的抗性。"
      },
      {
        "name": "日照敏感",
        "en_name": "Sunlight Sensitivity",
        "description": "若幽影龙身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "幽影龙发动两次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+5，触及10尺。命中：7（1d8+3）挥砍伤害外加3（1d6）暗蚀伤害。"
      },
      {
        "name": "幽影吐息",
        "en_name": "Shadow Breath",
        "description": "敏捷豁免检定：DC13，30尺锥状区域内的每名生物。失败：17（5d6）暗蚀伤害。成功：半伤。失败或成功：因此伤害生命值降至0的类人生物死亡，且从其尸体中浮现一只幽影Shadow。该幽影受幽影龙控制，使用与幽影龙一样的先攻并在其回合结束后立即执行回合。",
        "params": "充能5~6"
      }
    ],
    "bonus_actions": [
      {
        "name": "幽影隐匿",
        "en_name": "Shadow Steath",
        "description": "若幽影龙身处微光光照或黑暗，其执行躲藏动作。"
      }
    ],
    "source_file": "龙类\\幽影龙\\少年幽影龙.htm"
  },
  {
    "name": "幽影龙",
    "en_name": "Shadow Dragon",
    "type_line": "大型或巨型龙类，混乱邪恶",
    "size": "Large",
    "creature_type": "或巨型龙类",
    "alignment": "混乱邪恶",
    "ac": 16,
    "initiative_bonus": 14,
    "initiative_total": 24,
    "hp": 189,
    "hp_formula": "18d12+72",
    "speed": {
      "walk": "40尺，攀爬40尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 19,
        "mod": 4,
        "save": 9
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 6
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "察觉": 11,
      "隐匿": 14
    },
    "damage_resistances": [
      "见活体幽影特质"
    ],
    "damage_immunities": [
      "暗蚀"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 21
    },
    "languages": "通用语，龙语",
    "cr": 13,
    "xp": 10000,
    "pb": 5,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "幽影龙豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      },
      {
        "name": "活体幽影",
        "en_name": "Living Shadow",
        "description": "若幽影龙身处微光光照或黑暗中，其具有对除力场、心灵、光耀外所有伤害的抗性。"
      },
      {
        "name": "日照敏感",
        "en_name": "Sunlight Sensitivity",
        "description": "若幽影龙身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "幽影龙发动三次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+10，触及10尺。命中：12（2d6+5）挥砍伤害外加3（1d6）暗蚀伤害。"
      },
      {
        "name": "幽影吐息",
        "en_name": "Shadow Breath",
        "description": "敏捷豁免检定：DC17，60尺锥状区域内的每名生物。失败：35（10d6）暗蚀伤害。成功：半伤。失败或成功：因此伤害生命值降至0的类人生物死亡，且从其尸体中浮现一只幽影Shadow。该幽影受幽影龙控制，使用与幽影龙一样的先攻在其回合结束后立即执行回合。",
        "params": "充能5~6"
      }
    ],
    "bonus_actions": [
      {
        "name": "幽影隐匿",
        "en_name": "Shadow \nSteath",
        "description": "若幽影龙身处微光光照或黑暗中，其执行躲藏动作。"
      }
    ],
    "legendary_actions": [
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "幽影龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      },
      {
        "name": "幽影纱幕",
        "en_name": "Veil of Shadow",
        "description": "幽影龙使用幽影隐匿，且10尺内的一名其可见的生物受到10（3d6）暗蚀伤害。幽影龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\幽影龙\\幽影龙.htm"
  },
  {
    "name": "带翼狗头人",
    "en_name": "Winged Kobold",
    "type_line": "小型龙类，中立",
    "size": "Small",
    "creature_type": "龙类",
    "alignment": "中立",
    "ac": 15,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 10,
    "speed": {
      "walk": "30尺，飞行30尺"
    },
    "abilities": {
      "力量": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 8
    },
    "languages": "通用语，龙语",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "traits": [
      {
        "name": "集群战术",
        "en_name": "Pack Tactics",
        "description": "若狗头人的攻击目标生物5尺内存在有至少一名狗头人未失能的盟友，则狗头人对该生物进行的攻击检定具有优势。"
      },
      {
        "name": "日照敏感",
        "en_name": "Sunlight Sensitivity",
        "description": "若狗头人身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "龙牙之刃",
        "en_name": "Dragon-Tooth Blade",
        "description": "近战攻击检定：命中+5，触及5尺，单一目标。命中：6 （1d6 + 3） 点穿刺伤害。"
      },
      {
        "name": "繁彩飞沫",
        "en_name": "Chromatic Spittle",
        "description": "远程攻击检定：+5，射程30尺。命中：6（1d6 \n+ 3）点伤害，伤害类型由狗头人从下列选项中选择一种：强酸，寒冷，火焰，闪电，毒素。"
      }
    ],
    "source_file": "龙类\\狗头人\\带翼狗头人.htm"
  },
  {
    "name": "狗头人武者",
    "en_name": "Kobold Warrior",
    "type_line": "小型龙类，中立",
    "size": "Small",
    "creature_type": "龙类",
    "alignment": "中立",
    "ac": 14,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 7,
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "equipment": "匕首（3）",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 8
    },
    "languages": "通用语，龙语",
    "cr": "1/8",
    "xp": 25,
    "pb": 2,
    "traits": [
      {
        "name": "集群战术",
        "en_name": "Pack Tactics",
        "description": "若狗头人的攻击目标生物5尺内存在有至少一名狗头人未失能的盟友，则狗头人对该生物进行的攻击检定具有优势。"
      },
      {
        "name": "日照敏感",
        "en_name": "Sunlight Sensitivity",
        "description": "若狗头人身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "匕首",
        "en_name": "Dagger",
        "description": "近战或远程攻击检定：+4，触及5尺或射程20/60尺。命中：4 （1d4 + 2）点穿刺伤害。"
      }
    ],
    "source_file": "龙类\\狗头人\\狗头人武者.htm"
  },
  {
    "name": "成年白龙",
    "en_name": "Adult White Dragon",
    "type_line": "巨型龙类（色彩龙），混乱邪恶",
    "size": "Huge",
    "creature_type": "龙类（色彩龙）",
    "alignment": "混乱邪恶",
    "ac": 18,
    "initiative_bonus": 10,
    "initiative_total": 20,
    "hp": 200,
    "hp_formula": "16d12+96",
    "speed": {
      "walk": "40尺，掘穴30尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 5
      },
      "体质": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 6
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "察觉": 11,
      "隐匿": 5
    },
    "damage_immunities": [
      "寒冷"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 21
    },
    "languages": "通用语，龙语",
    "cr": 13,
    "xp": 10000,
    "pb": 5,
    "traits": [
      {
        "name": "冰上行走",
        "en_name": "Ice Walk",
        "description": "白龙可以在冰面上移动和攀爬而无需为此进行属性检定。此外，其不会因由冰或雪组成的困难地形额外消耗移动力。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "白龙豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "白龙发动三次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+11，触及10尺。命中：13（2d6+6）挥砍伤害外加4（1d8）寒冷伤害。"
      },
      {
        "name": "寒冷吐息",
        "en_name": "Cold Breath",
        "description": "体质豁免检定：DC19，60尺锥状区域内的每名生物。失败：54（12d8）寒冷伤害。成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "legendary_actions": [
      {
        "name": "极寒冰暴",
        "en_name": "Freezing Burst",
        "description": "体质豁免检定：DC14，以120尺内白龙可见一点为中心，半径30尺球状区域内的每名生物。失败：7（2d6）寒冷伤害，且目标的速度降至0，直至目标的下个回合结束。失败或成功：白龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "骇人威仪",
        "en_name": "Frightful Presence",
        "description": "白龙施展恐惧术Fear，无需材料成分并使用魅力作为施法属性（法术豁免DC14）。白龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "白龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\白龙\\成年白龙.htm"
  },
  {
    "name": "白龙雏龙",
    "en_name": "White Dragon Wyrmling",
    "type_line": "中型龙类（色彩龙），混乱邪恶",
    "size": "Medium",
    "creature_type": "龙类（色彩龙）",
    "alignment": "混乱邪恶",
    "ac": 16,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 32,
    "hp_formula": "5d8+10",
    "speed": {
      "walk": "30尺，掘穴15尺，飞行60尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 2
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 2
    },
    "damage_immunities": [
      "寒冷"
    ],
    "senses": {
      "盲视": 10,
      "被动察觉": 14
    },
    "languages": "龙语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "冰上行走",
        "en_name": "Ice Walk",
        "description": "白龙可以在冰面上移动和攀爬而无需为此进行属性检定。此外，其不会因由冰或雪组成的困难地形额外消耗移动力。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "白龙发动两次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+4，触及5尺。命中：6（1d8+2）挥砍伤害外加2（1d4）寒冷伤害。"
      },
      {
        "name": "寒冷吐息",
        "en_name": "Cold Breath",
        "description": "体质豁免检定：DC12，15尺锥状区域内的每名生物。失败：22（5d8）寒冷伤害。成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "source_file": "龙类\\白龙\\白龙雏龙.htm"
  },
  {
    "name": "远古白龙",
    "en_name": "Ancient White Dragon",
    "type_line": "超巨型龙类（色彩龙），混乱邪恶",
    "size": "Gargantuan",
    "creature_type": "龙类（色彩龙）",
    "alignment": "混乱邪恶",
    "ac": 20,
    "initiative_bonus": 12,
    "initiative_total": 22,
    "hp": 333,
    "hp_formula": "18d20+144",
    "speed": {
      "walk": "40尺，掘穴40尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 26,
        "mod": 8,
        "save": 8
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 6
      },
      "体质": {
        "score": 26,
        "mod": 8,
        "save": 8
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 7
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "察觉": 13,
      "隐匿": 6
    },
    "damage_immunities": [
      "寒冷"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 23
    },
    "languages": "通用语，龙语",
    "cr": 20,
    "xp": 25000,
    "pb": 6,
    "traits": [
      {
        "name": "冰上行走",
        "en_name": "Ice Walk",
        "description": "白龙可以在冰面上移动和攀爬而无需为此进行属性检定。此外，其不会因由冰或雪组成的困难地形额外消耗移动力。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "白龙豁免失败时，可以将其改为豁免成功。",
        "params": "4/日，或巢穴内5/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "白龙发动三次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+14，触及15尺。命中：17（2d8+8）挥砍伤害外加7（2d6）寒冷伤害。"
      },
      {
        "name": "寒冷吐息",
        "en_name": "Cold Breath",
        "description": "体质豁免检定：DC22，90尺锥状区域内的每名生物。失败：63（14d8）寒冷伤害。成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "legendary_actions": [
      {
        "name": "极寒冰暴",
        "en_name": "Freezing Burst",
        "description": "体质豁免检定：DC20，以120尺内白龙可见一点为中心，半径30尺球状区域内的每名生物。失败：14（4d6）寒冷伤害，且目标的速度降至0，直至目标的下个回合结束。失败或成功：白龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "骇人威仪",
        "en_name": "Frightful Presence",
        "description": "白龙施展恐惧术Fear，无需材料成分并使用魅力作为施法属性（法术豁免DC18）。白龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "白龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\白龙\\远古白龙.htm"
  },
  {
    "name": "青年白龙",
    "en_name": "Young White Dragon",
    "type_line": "大型龙类（色彩龙），混乱邪恶",
    "size": "Large",
    "creature_type": "龙类（色彩龙）",
    "alignment": "混乱邪恶",
    "ac": 17,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 123,
    "hp_formula": "13d10+52",
    "speed": {
      "walk": "40尺，掘穴20尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 3
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 3
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "察觉": 6,
      "隐匿": 3
    },
    "damage_immunities": [
      "寒冷"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 16
    },
    "languages": "通用语，龙语",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "traits": [
      {
        "name": "冰上行走",
        "en_name": "Ice Walk",
        "description": "白龙可以在冰面上移动和攀爬而无需为此进行属性检定。此外，其不会因由冰或雪组成的困难地形额外消耗移动力。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "白龙发动三次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+7，触及10尺。命中：9（2d4+4）挥砍伤害外加2（1d4）寒冷伤害。"
      },
      {
        "name": "寒冷吐息",
        "en_name": "Cold Breath",
        "description": "体质豁免检定：DC15，30尺锥状区域内的每名生物。失败：40（9d8）寒冷伤害。成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "source_file": "龙类\\白龙\\青年白龙.htm"
  },
  {
    "name": "成年红龙",
    "en_name": "Adult Red Dragon",
    "type_line": "巨型龙类（色彩龙），混乱邪恶",
    "size": "Huge",
    "creature_type": "龙类（色彩龙）",
    "alignment": "混乱邪恶",
    "ac": 19,
    "initiative_bonus": 12,
    "initiative_total": 22,
    "hp": 256,
    "hp_formula": "19d12+133",
    "speed": {
      "walk": "40尺，攀爬40尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 27,
        "mod": 8,
        "save": 8
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 6
      },
      "体质": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 7
      },
      "魅力": {
        "score": 23,
        "mod": 6,
        "save": 6
      }
    },
    "skills": {
      "察觉": 13,
      "隐匿": 6
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 23
    },
    "languages": "通用语，龙语",
    "cr": 17,
    "xp": 18000,
    "pb": 6,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "红龙豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "红龙发动三次撕裂攻击，其可以将其中一次攻击替换为使用施法施展灼热射线Scorching \nRay 。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+14，触及10尺。命中：13（1d10+8）挥砍伤害外加5（2d4）火焰伤害。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC21，60尺锥状区域内的每名生物。失败：59（17d6）火焰伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "红龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC20，法术攻击命中+12）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "命令术Command（二环版本），侦测魔法Detect Magic，灼热射线Scorching Ray"
      },
      {
        "name": "1/日：",
        "en_name": "",
        "description": "火球术Fireball"
      }
    ],
    "legendary_actions": [
      {
        "name": "霸者威仪",
        "en_name": "Commanding Presence",
        "description": "红龙使用施法施展命令术Command（二环版本）。红龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "炽炎射线",
        "en_name": "Fiery Rays",
        "description": "红龙使用施法施展灼热射线Scorching Ray。红龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "红龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\红龙\\成年红龙.htm"
  },
  {
    "name": "红龙雏龙",
    "en_name": "Red Dragon Wyrmling",
    "type_line": "中型龙类（色彩龙），混乱邪恶",
    "size": "Medium",
    "creature_type": "龙类（色彩龙）",
    "alignment": "混乱邪恶",
    "ac": 17,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 75,
    "hp_formula": "10d8+30",
    "speed": {
      "walk": "30尺，攀爬30尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 2
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 2
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "盲视": 10,
      "被动察觉": 14
    },
    "languages": "龙语",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "红龙发动两次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+6，触及5尺。命中：9（1d10+4）挥砍伤害外加3（1d6）火焰伤害。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC13，15尺锥状区域内的每名生物。失败：24（7d6）火焰伤害。成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "source_file": "龙类\\红龙\\红龙雏龙.htm"
  },
  {
    "name": "远古红龙",
    "en_name": "Ancient Red Dragon",
    "type_line": "超巨型龙类（色彩龙），混乱邪恶",
    "size": "Gargantuan",
    "creature_type": "龙类（色彩龙）",
    "alignment": "混乱邪恶",
    "ac": 22,
    "initiative_bonus": 14,
    "initiative_total": 24,
    "hp": 507,
    "hp_formula": "26d20+234",
    "speed": {
      "walk": "40尺，攀爬40尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 30,
        "mod": 10,
        "save": 10
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 7
      },
      "体质": {
        "score": 29,
        "mod": 9,
        "save": 9
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 9
      },
      "魅力": {
        "score": 27,
        "mod": 8,
        "save": 8
      }
    },
    "skills": {
      "察觉": 16,
      "隐匿": 7
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 26
    },
    "languages": "通用语，龙语",
    "cr": 24,
    "xp": 62000,
    "pb": 7,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "红龙豁免失败时，可以将其改为豁免成功。",
        "params": "4/日，或巢穴内5/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "红龙发动三次撕裂攻击，其可以将其中一次攻击替换为使用施法施展灼热射线Scorching \nRay （三环版本）。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+17，触及15尺。命中：19（2d8+10）挥砍伤害外加10（3d6）火焰伤害。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC24，90尺锥状区域内的每名生物。失败：91（26d6）火焰伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "红龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC23，法术攻击命中+15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "命令术Command（二环版本），侦测魔法Detect Magic，灼热射线Scorching Ray（三环版本）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "火球术Fireball（六环版本），探知Scrying"
      }
    ],
    "legendary_actions": [
      {
        "name": "霸者威仪",
        "en_name": "Commanding Presence",
        "description": "红龙使用施法施展命令术Command（二环版本）。红龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "炽炎射线",
        "en_name": "Fiery Rays",
        "description": "红龙使用施法施展灼热射线Scorching \nRay （三环版本）。红龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "红龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\红龙\\远古红龙.htm"
  },
  {
    "name": "青年红龙",
    "en_name": "Young Red Dragon",
    "type_line": "大型龙类（色彩龙），混乱邪恶",
    "size": "Large",
    "creature_type": "龙类（色彩龙）",
    "alignment": "混乱邪恶",
    "ac": 18,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 178,
    "hp_formula": "17d10+85",
    "speed": {
      "walk": "40尺，攀爬40尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 4
      },
      "体质": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 4
      },
      "魅力": {
        "score": 19,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "察觉": 8,
      "隐匿": 4
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 18
    },
    "languages": "通用语，龙语",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "红龙发动三次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+10，触及10尺。命中：13（2d6+6）挥砍伤害外加3（1d6）火焰伤害。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC17，30尺锥状区域内的每名生物。失败：56（16d6）火焰伤害。成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "source_file": "龙类\\红龙\\青年红龙.htm"
  },
  {
    "name": "成年绿龙",
    "en_name": "Adult Green Dragon",
    "type_line": "巨型龙类（色彩龙），守序邪恶",
    "size": "Huge",
    "creature_type": "龙类（色彩龙）",
    "alignment": "守序邪恶",
    "ac": 19,
    "initiative_bonus": 11,
    "initiative_total": 21,
    "hp": 207,
    "hp_formula": "18d12+90",
    "speed": {
      "walk": "40尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 6
      },
      "体质": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 7
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "欺瞒": 9,
      "察觉": 12,
      "游说": 9,
      "隐匿": 6
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 22
    },
    "languages": "通用语，龙语",
    "cr": 15,
    "xp": 13000,
    "pb": 5,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "绿龙可以在空气和水中呼吸。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "绿龙豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "绿龙发动三次撕裂攻击，其可以将其中一次攻击替换为使用施法施展心灵尖刺Mind \nSpike （三环版本）。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+11，触及10尺。命中：15（2d8+6）挥砍伤害外加7（2d6）毒素伤害。"
      },
      {
        "name": "毒性吐息",
        "en_name": "Poison Breath",
        "description": "体质豁免检定：DC18，60尺锥状区域内的每名生物。失败：56（16d6）毒素伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "绿龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC17）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，心灵尖刺Mind Spike（三环版本）"
      },
      {
        "name": "1/日：",
        "en_name": "",
        "description": "指使术Geas"
      }
    ],
    "legendary_actions": [
      {
        "name": "心灵入侵",
        "en_name": "Mind Invasion",
        "description": "绿龙使用施法施展心灵尖刺Mind Spike （三环版本）。",
        "max_uses": 3
      },
      {
        "name": "毒烟雾瘴",
        "en_name": "Noxious Miasma",
        "description": "体质豁免检定：DC17，以90尺内绿龙可见一点为中心，半径20尺球状区域内的每名生物。失败：7（2d6）毒素伤害，且目标的AC将承受-2的减值直至其下个回合结束。失败或成功：绿龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "绿龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\绿龙\\成年绿龙.htm"
  },
  {
    "name": "绿龙雏龙",
    "en_name": "Green Dragon Wyrmling",
    "type_line": "中型龙类（色彩龙），守序邪恶",
    "size": "Medium",
    "creature_type": "龙类（色彩龙）",
    "alignment": "守序邪恶",
    "ac": 17,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 38,
    "hp_formula": "7d8+7",
    "speed": {
      "walk": "30尺，飞行60尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 3
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 3
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "盲视": 10,
      "被动察觉": 14
    },
    "languages": "龙语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "绿龙可以在空气和水中呼吸。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "绿龙发动两次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+4，触及5尺。命中：7（1d10+2）挥砍伤害外加3（1d6）毒素伤害。"
      },
      {
        "name": "毒性吐息",
        "en_name": "Poison Breath",
        "description": "体质豁免检定：DC11，15尺锥状区域内的每名生物。失败：21（6d6）毒素伤害。成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "source_file": "龙类\\绿龙\\绿龙雏龙.htm"
  },
  {
    "name": "远古绿龙",
    "en_name": "Ancient Green Dragon",
    "type_line": "超巨型龙类（色彩龙），守序邪恶",
    "size": "Gargantuan",
    "creature_type": "龙类（色彩龙）",
    "alignment": "守序邪恶",
    "ac": 21,
    "initiative_bonus": 15,
    "initiative_total": 25,
    "hp": 402,
    "hp_formula": "23d20+161",
    "speed": {
      "walk": "40尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 27,
        "mod": 8,
        "save": 8
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 8
      },
      "体质": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "智力": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "感知": {
        "score": 17,
        "mod": 3,
        "save": 10
      },
      "魅力": {
        "score": 22,
        "mod": 6,
        "save": 6
      }
    },
    "skills": {
      "欺瞒": 13,
      "察觉": 17,
      "游说": 13,
      "隐匿": 8
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 27
    },
    "languages": "通用语，龙语",
    "cr": 22,
    "xp": 41000,
    "pb": 7,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "绿龙可以在空气和水中呼吸。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "绿龙豁免失败时，可以将其改为豁免成功。",
        "params": "4/日，或巢穴内5/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "绿龙发动三次撕裂攻击，其可以将其中一次攻击替换为使用施法施展心灵尖刺Mind \nSpike （五环版本）。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+15，触及15尺。命中：17（2d8+8）挥砍伤害外加10（3d6）毒素伤害。"
      },
      {
        "name": "毒性吐息",
        "en_name": "Poison Breath",
        "description": "体质豁免检定：DC22，90尺锥状区域内的每名生物。失败：77（22d6）毒素伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "绿龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC21）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，心灵尖刺Mind Spike（五环版本）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "指使术Geas，篡改记忆Modify Memory"
      }
    ],
    "legendary_actions": [
      {
        "name": "心灵入侵",
        "en_name": "Mind Invasion",
        "description": "绿龙使用施法施展心灵尖刺Mind Spike （五环版本）。",
        "max_uses": 3
      },
      {
        "name": "毒烟雾瘴",
        "en_name": "Noxious Miasma",
        "description": "体质豁免检定：DC21，以90尺内绿龙可见一点为中心，半径30尺球状区域内的所有生物。失败：17（5d6）毒素伤害，且目标的AC将承受-2的减值直至其下个回合结束。失败或成功：绿龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "绿龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\绿龙\\远古绿龙.htm"
  },
  {
    "name": "青年绿龙",
    "en_name": "Young Green Dragon",
    "type_line": "大型龙类（色彩龙），守序邪恶",
    "size": "Large",
    "creature_type": "龙类（色彩龙）",
    "alignment": "守序邪恶",
    "ac": 18,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 136,
    "hp_formula": "16d10+48",
    "speed": {
      "walk": "40尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 4
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 4
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "欺瞒": 5,
      "察觉": 7,
      "隐匿": 4
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 17
    },
    "languages": "通用语，龙语",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "绿龙可以在空气和水中呼吸。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "绿龙发动三次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+7，触及10尺。命中：11（2d6+4）挥砍伤害外加7（2d6）毒素伤害。"
      },
      {
        "name": "毒性吐息",
        "en_name": "Poison Breath",
        "description": "体质豁免检定：DC14，30尺锥状区域内的每名生物。失败：42（12d6）毒素伤害。成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "source_file": "龙类\\绿龙\\青年绿龙.htm"
  },
  {
    "name": "成年蓝龙",
    "en_name": "Adult Blue Dragon",
    "type_line": "巨型龙类（色彩龙），守序邪恶",
    "size": "Huge",
    "creature_type": "龙类（色彩龙）",
    "alignment": "守序邪恶",
    "ac": 19,
    "initiative_bonus": 10,
    "initiative_total": 20,
    "hp": 212,
    "hp_formula": "17d12+102",
    "speed": {
      "walk": "40尺，掘穴30尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 5
      },
      "体质": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 7
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 5
      }
    },
    "skills": {
      "察觉": 12,
      "隐匿": 5
    },
    "damage_immunities": [
      "闪电"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 22
    },
    "languages": "通用语，龙语",
    "cr": 16,
    "xp": 15000,
    "pb": 5,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "蓝龙豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蓝龙发动三次撕裂攻击，其可以将其中一次攻击替换为使用施法施展粉碎音波Shatter。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+12，触及10尺。命中：16（2d8+7）挥砍伤害外加5（1d10）闪电伤害。"
      },
      {
        "name": "闪电吐息",
        "en_name": "Lightning Breath",
        "description": "敏捷豁免检定：DC19，90尺长、5尺宽的线状区域内的每名生物。失败：60（11d10）闪电伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "蓝龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC18）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，隐形术Invisibility，法师之手Mage Hand，粉碎音波Shatter"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "探知Scrying，短讯术Sending"
      }
    ],
    "legendary_actions": [
      {
        "name": "翔空无影",
        "en_name": "Cloaked Flight",
        "description": "蓝龙使用施法施展隐形术Invisibility，并飞行至多等于其飞行速度一半的距离。蓝龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "音爆",
        "en_name": "Sonic Boom",
        "description": "蓝龙使用施法施展粉碎音波Shatter。蓝龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "尾扫",
        "en_name": "Tail Swipe",
        "description": "蓝龙发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\蓝龙\\成年蓝龙.htm"
  },
  {
    "name": "蓝龙雏龙",
    "en_name": "Blue Dragon Wyrmling",
    "type_line": "中型龙类（色彩龙），守序邪恶",
    "size": "Medium",
    "creature_type": "龙类（色彩龙）",
    "alignment": "守序邪恶",
    "ac": 17,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 65,
    "hp_formula": "10d8+20",
    "speed": {
      "walk": "30尺，掘穴15尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 2
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 2
    },
    "damage_immunities": [
      "闪电"
    ],
    "senses": {
      "盲视": 10,
      "被动察觉": 14
    },
    "languages": "龙语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蓝龙发动两次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+5，触及5尺。命中：8（1d10+3）挥砍伤害外加3（1d6）闪电伤害。"
      },
      {
        "name": "闪电吐息",
        "en_name": "Lightning Breath",
        "description": "敏捷豁免检定：DC12，30尺长、5尺宽的线状区域内的每名生物。失败：21（6d6）闪电伤害。成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "source_file": "龙类\\蓝龙\\蓝龙雏龙.htm"
  },
  {
    "name": "远古蓝龙",
    "en_name": "Ancient Blue Dragon",
    "type_line": "超巨型龙类（色彩龙），守序邪恶",
    "size": "Gargantuan",
    "creature_type": "龙类（色彩龙）",
    "alignment": "守序邪恶",
    "ac": 22,
    "initiative_bonus": 14,
    "initiative_total": 24,
    "hp": 481,
    "hp_formula": "26d20+208",
    "speed": {
      "walk": "40尺，掘穴40尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 29,
        "mod": 9,
        "save": 9
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 7
      },
      "体质": {
        "score": 27,
        "mod": 8,
        "save": 8
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 17,
        "mod": 3,
        "save": 10
      },
      "魅力": {
        "score": 25,
        "mod": 7,
        "save": 7
      }
    },
    "skills": {
      "察觉": 17,
      "隐匿": 7
    },
    "damage_immunities": [
      "闪电"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 27
    },
    "languages": "通用语，龙语",
    "cr": 23,
    "xp": 50000,
    "pb": 7,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "蓝龙豁免失败时，可以将其改为豁免成功。",
        "params": "4/日，或巢穴内5/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蓝龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用施法施展粉碎音波Shatter（三环版本）。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+16，触及15尺。命中：18（2d8+9）挥砍伤害外加11（2d10）闪电伤害。"
      },
      {
        "name": "闪电吐息",
        "en_name": "Lightning Breath",
        "description": "敏捷豁免检定：DC23，120尺长、10尺宽的线状区域内的每名生物。失败：88（16d10）闪电伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "蓝龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC22）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，隐形术Invisibility，法师之手Mage Hand，粉碎音波Shatter（三环版本）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "探知Scrying，短讯术Sending"
      }
    ],
    "legendary_actions": [
      {
        "name": "翔空无影",
        "en_name": "Cloaked Flight",
        "description": "蓝龙使用施法施展隐形术Invisibility，并飞行至多等于其飞行速度一半的距离。蓝龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "音爆",
        "en_name": "Sonic Boom",
        "description": "蓝龙使用施法施展粉碎音波Shatter（三环版本）。蓝龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "尾扫",
        "en_name": "Tail Swipe",
        "description": "蓝龙发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\蓝龙\\远古蓝龙.htm"
  },
  {
    "name": "青年蓝龙",
    "en_name": "Young Blue Dragon",
    "type_line": "大型龙类（色彩龙），守序邪恶",
    "size": "Large",
    "creature_type": "龙类（色彩龙）",
    "alignment": "守序邪恶",
    "ac": 18,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 152,
    "hp_formula": "16d10+64",
    "speed": {
      "walk": "40尺，掘穴20尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 4
      },
      "体质": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 5
      },
      "魅力": {
        "score": 17,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "察觉": 9,
      "隐匿": 4
    },
    "damage_immunities": [
      "闪电"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 19
    },
    "languages": "通用语，龙语",
    "cr": 9,
    "xp": 5000,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蓝龙发动三次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+9，触及10尺。命中：12（2d6+5）挥砍伤害外加5（1d10）闪电伤害。"
      },
      {
        "name": "闪电吐息",
        "en_name": "Lightning Breath",
        "description": "敏捷豁免检定：DC16，60尺长、5尺宽的线状区域内的每名生物。失败：55（10d10）闪电伤害。成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "source_file": "龙类\\蓝龙\\青年蓝龙.htm"
  },
  {
    "name": "成年赤铜龙",
    "en_name": "Adult Copper Dragon",
    "type_line": "巨型龙类（金属龙），混乱善良",
    "size": "Huge",
    "creature_type": "龙类（金属龙）",
    "alignment": "混乱善良",
    "ac": 18,
    "initiative_bonus": 11,
    "initiative_total": 21,
    "hp": 184,
    "hp_formula": "16d12+80",
    "speed": {
      "walk": "40尺，攀爬40尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 6
      },
      "体质": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 7
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "欺瞒": 9,
      "察觉": 12,
      "隐匿": 6
    },
    "damage_immunities": [
      "强酸"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 22
    },
    "languages": "通用语，龙语",
    "cr": 14,
    "xp": 11500,
    "pb": 5,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "赤铜龙豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "赤铜龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用（A）缓速吐息或（B）施法施展心灵尖刺Mind \nSpike （四环版本）。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+11，触及10尺。命中：17（2d10+6）挥砍伤害外加4（1d8）强酸伤害。"
      },
      {
        "name": "强酸吐息",
        "en_name": "Acid Breath",
        "description": "敏捷豁免检定：DC18，60尺长、5尺宽的线状区域内的每名生物。失败：54（12d8）强酸伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "缓速吐息",
        "en_name": "Slowing Breath",
        "description": "体质豁免检定：DC18，60尺锥状区域内的每名生物。失败：直至目标的下个回合结束，目标速度减半，无法执行反应，且目标在其回合中仅可以执行一个动作或一个附赠动作，但不能同时执行二者。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "赤铜龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC17）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，心灵尖刺Mind Spike（四环版本），  次级幻象Minor Illusion，形体变化Shapechange（仅野兽与类人形态，不会因此法术获得临时生命值，但无需为维持此法术而保有临时生命值或维持专注）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "高等复原术Greater Restoration，高级幻影Major Image"
      }
    ],
    "legendary_actions": [
      {
        "name": "带来笑容的魔法",
        "en_name": "Giggling Magic",
        "description": "魅力豁免检定：DC17，单一90尺内赤铜龙可见的生物。失败：24（7d6）心灵伤害，且每当目标进行一次属性检定和攻击检定时，其必须掷1d6并在那次D20检定中承受等量减值，直至其下个回合结束。失败或成功： 赤铜龙无法再执行此动作，直至其下个回合开始。",
        "max_uses": 3
      },
      {
        "name": "心灵震荡",
        "en_name": "Mind Jolt",
        "description": "赤铜龙使用施法施展心灵尖刺Mind \nSpike （四环版本）。赤铜龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "赤铜龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\赤铜龙\\成年赤铜龙.htm"
  },
  {
    "name": "赤铜龙雏龙",
    "en_name": "Copper Dragon Wyrmling",
    "type_line": "中型龙类（金属龙），混乱善良",
    "size": "Medium",
    "creature_type": "龙类（金属龙）",
    "alignment": "混乱善良",
    "ac": 16,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 22,
    "hp_formula": "4d8+4",
    "speed": {
      "walk": "30尺，攀爬30尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 3
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 3
    },
    "damage_immunities": [
      "强酸"
    ],
    "senses": {
      "盲视": 10,
      "被动察觉": 14
    },
    "languages": "龙语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "actions": [
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+4，触及5尺。命中：7（1d10+2）挥砍伤害。"
      },
      {
        "name": "强酸吐息",
        "en_name": "Acid Breath",
        "description": "敏捷豁免检定：DC11，20尺长、5尺宽的线状区域内的每名生物。失败：18（4d8）强酸伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "缓速吐息",
        "en_name": "Slowing Breath",
        "description": "体质豁免检定：DC11，15尺锥状区域内的每名生物。失败：直至目标的下个回合结束，目标速度减半，无法执行反应，且目标在其回合中仅可以执行一个动作或一个附赠动作，但不能同时执行二者。"
      }
    ],
    "source_file": "龙类\\赤铜龙\\赤铜龙雏龙.htm"
  },
  {
    "name": "远古赤铜龙",
    "en_name": "Ancient Copper Dragon",
    "type_line": "超巨型龙类（金属龙），混乱善良",
    "size": "Gargantuan",
    "creature_type": "龙类（金属龙）",
    "alignment": "混乱善良",
    "ac": 21,
    "initiative_bonus": 15,
    "initiative_total": 25,
    "hp": 367,
    "hp_formula": "21d20+147",
    "speed": {
      "walk": "40尺，攀爬40尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 27,
        "mod": 8,
        "save": 8
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 8
      },
      "体质": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "智力": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "感知": {
        "score": 17,
        "mod": 3,
        "save": 10
      },
      "魅力": {
        "score": 22,
        "mod": 6,
        "save": 6
      }
    },
    "skills": {
      "欺瞒": 13,
      "察觉": 17,
      "隐匿": 8
    },
    "damage_immunities": [
      "强酸"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 27
    },
    "languages": "通用语，龙语",
    "cr": 21,
    "xp": 33000,
    "pb": 7,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "赤铜龙豁免失败时，可以将其改为豁免成功。",
        "params": "4/日，或巢穴内5/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "赤铜龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用（A）缓速吐息或（B）施法施展心灵尖刺Mind \nSpike （五环版本）。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+15，触及15尺。命中：19（2d10+8）挥砍伤害外加9（2d8）强酸伤害。"
      },
      {
        "name": "强酸吐息",
        "en_name": "Acid Breath",
        "description": "敏捷豁免检定：DC22，90尺长、10尺宽的线状区域内的每名生物。失败：63（14d8）强酸伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "缓速吐息",
        "en_name": "Slowing Breath",
        "description": "体质豁免检定：DC22，90尺锥状区域内的每名生物。失败：直至目标的下个回合结束，目标速度减半，无法执行反应，且目标在其回合中仅可以执行一个动作或一个附赠动作，但不能同时执行二者。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "赤铜龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC21）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，心灵尖刺Mind Spike（五环版本），  次级幻象Minor Illusion，形体变化Shapechange（仅野兽与类人形态，不会因此法术获得临时生命值，但无需为维持此法术而保有临时生命值或维持专注）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "高等复原术Greater Restoration，高级幻影Major Image，投影术Project Image"
      }
    ],
    "legendary_actions": [
      {
        "name": "带来笑容的魔法",
        "en_name": "Giggling Magic",
        "description": "魅力豁免检定：DC21，单一120尺内赤铜龙可见的生物。失败：31（9d6）心灵伤害，且每当目标进行一次属性检定和攻击检定时，其必须掷1d8并在那次D20检定中承受等量减值，直至其下个回合结束。失败或成功：赤铜龙无法再执行此动作，直至其下个回合开始。",
        "max_uses": 3
      },
      {
        "name": "心灵震荡",
        "en_name": "Mind Jolt",
        "description": "赤铜龙使用施法施展心灵尖刺Mind \nSpike \n（五环版本）。赤铜龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "赤铜龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\赤铜龙\\远古赤铜龙.htm"
  },
  {
    "name": "青年赤铜龙",
    "en_name": "Young Copper Dragon",
    "type_line": "大型龙类（金属龙），混乱善良",
    "size": "Large",
    "creature_type": "龙类（金属龙）",
    "alignment": "混乱善良",
    "ac": 17,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 119,
    "hp_formula": "14d10+42",
    "speed": {
      "walk": "40尺，攀爬40尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 4
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 4
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "欺瞒": 5,
      "察觉": 7,
      "隐匿": 4
    },
    "damage_immunities": [
      "强酸"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 17
    },
    "languages": "通用语，龙语",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "赤铜龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用缓速吐息。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+7，触及10尺。命中：15（2d10+4）挥砍伤害。"
      },
      {
        "name": "强酸吐息",
        "en_name": "Acid Breath",
        "description": "敏捷豁免检定：DC14，40尺长、5尺宽的线状区域内的每名生物。失败：40（9d8）强酸伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "缓速吐息",
        "en_name": "Slowing Breath",
        "description": "体质豁免检定：DC14，30尺锥状区域内的每名生物。失败：直至目标的下个回合结束，目标速度减半，无法执行反应，且目标在其回合中仅可以执行一个动作或一个附赠动作，但不能同时执行二者。"
      }
    ],
    "source_file": "龙类\\赤铜龙\\青年赤铜龙.htm"
  },
  {
    "name": "金龙雏龙",
    "en_name": "Gold Dragon Wyrmling",
    "type_line": "中型龙类（金属龙），守序善良",
    "size": "Medium",
    "creature_type": "龙类（金属龙）",
    "alignment": "守序善良",
    "ac": 17,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 60,
    "hp_formula": "8d8+24",
    "speed": {
      "walk": "30尺，飞行60尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 4
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 4
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "盲视": 10,
      "被动察觉": 14
    },
    "languages": "龙语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "金龙可以在空气和水中呼吸。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "金龙发动两次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+6，触及5尺。命中：9（1d10+4）挥砍伤害。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC13，15尺锥状区域内的每名生物。失败：22（4d10）火焰伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "弱化吐息",
        "en_name": "Weakening Breath",
        "description": "力量豁免检定：DC13，15尺锥状区域内未被此吐息影响的每名生物。失败：目标进行基于力量的D20检定时具有劣势，且其伤害掷骰承受2（1d4）减值。目标在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。"
      }
    ],
    "source_file": "龙类\\金龙\\New_Item.htm"
  },
  {
    "name": "成年金龙",
    "en_name": "Adult Gold Dragon",
    "type_line": "巨型龙类（金属龙），守序善良",
    "size": "Huge",
    "creature_type": "龙类（金属龙）",
    "alignment": "守序善良",
    "ac": 19,
    "initiative_bonus": 14,
    "initiative_total": 24,
    "hp": 243,
    "hp_formula": "18d12+126",
    "speed": {
      "walk": "40尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 27,
        "mod": 8,
        "save": 8
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 8
      },
      "体质": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 8
      },
      "魅力": {
        "score": 24,
        "mod": 7,
        "save": 7
      }
    },
    "skills": {
      "洞悉": 8,
      "察觉": 14,
      "游说": 13,
      "隐匿": 8
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 24
    },
    "languages": "通用语，龙语",
    "cr": 17,
    "xp": 18000,
    "pb": 6,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "金龙可以在空气和水中呼吸。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "金龙豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "金龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用（A）施法施展光导箭Guiding \nBolt （二环版本）或（B）弱化吐息。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+14，触及10尺。命中：17（2d8+8）挥砍伤害外加4（1d8）火焰伤害。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC21，60尺锥状区域内的每名生物。失败：66（12d10）火焰伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "金龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC21，法术攻击命中+13）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，光导箭Guiding Bolt（二环版本），形体变化Shapechange（仅野兽与类人形态，不会因此法术获得临时生命值，但无需为维持此法术而保有临时生命值或维持专注）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "焰击术Flame Strike，诚实之域Zone of Truth"
      },
      {
        "name": "弱化吐息",
        "en_name": "Weakening Breath",
        "description": "力量豁免检定：DC21，60尺锥状区域内未被此吐息影响的每名生物。失败：目标进行基于力量的D20检定时具有劣势，且其伤害掷骰承受3（1d6）减值。目标在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。"
      }
    ],
    "legendary_actions": [
      {
        "name": "放逐",
        "en_name": "Banish",
        "description": "魅力豁免检定：DC21，单一120尺内金龙可见的生物。失败：10（3d6）力场伤害，且目标陷入失能状态并被转移至一处无害的半位面直至金龙的下个回合开始，此时其将重新出现在位于金龙120尺内由金龙选择的一处未占据空间。失败或成功：金龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "明光道标",
        "en_name": "Guiding Light",
        "description": "金龙使用施法施展光导箭Guiding Bolt （二环版本）。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "金龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\金龙\\成年金龙.htm"
  },
  {
    "name": "远古金龙",
    "en_name": "Ancient Gold Dragon",
    "type_line": "超巨型龙类（金属龙），守序善良",
    "size": "Gargantuan",
    "creature_type": "龙类（金属龙）",
    "alignment": "守序善良",
    "ac": 22,
    "initiative_bonus": 16,
    "initiative_total": 26,
    "hp": 546,
    "hp_formula": "28d20+252",
    "speed": {
      "walk": "40尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 30,
        "mod": 10,
        "save": 10
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 9
      },
      "体质": {
        "score": 29,
        "mod": 9,
        "save": 9
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 17,
        "mod": 3,
        "save": 10
      },
      "魅力": {
        "score": 28,
        "mod": 9,
        "save": 9
      }
    },
    "skills": {
      "洞悉": 10,
      "察觉": 17,
      "游说": 16,
      "隐匿": 9
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 27
    },
    "languages": "通用语，龙语",
    "cr": 24,
    "xp": 62000,
    "pb": 7,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "金龙可以在空气和水中呼吸。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "金龙豁免失败时，可以将其改为豁免成功。",
        "params": "4/日，或巢穴内5/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "金龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用（A）施法施展光导箭Guiding \nBolt （四环版本）或（B）弱化吐息。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+17，触及15尺。命中：19（2d8+10）挥砍伤害外加9（2d8）火焰伤害。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC24，90尺锥状区域内的每名生物。失败：71（13d10）火焰伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "金龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC24，法术攻击命中+16）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，光导箭Guiding Bolt（四环版本），形体变化Shapechange（仅野兽与类人形态，不会因此法术获得临时生命值，但无需为维持此法术而保有临时生命值或维持专注）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "焰击术Flame Strike（六环版本），回返真言Word of Recall，诚实之域Zone of Truth"
      },
      {
        "name": "弱化吐息",
        "en_name": "Weakening Breath",
        "description": "力量豁免检定：DC24，90尺锥状区域内未被此吐息影响的每名生物。失败：目标进行基于力量的D20检定时具有劣势，且其伤害掷骰承受5（1d10）减值。目标在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。"
      }
    ],
    "legendary_actions": [
      {
        "name": "放逐",
        "en_name": "Banish",
        "description": "魅力豁免检定：DC24，单一120尺内金龙可见的生物。\n失败：24（7d6）力场伤害，且目标陷入失能状态并被转移至一处无害的半位面直至金龙的下个回合开始，此时其将重新出现在位于金龙120尺内由金龙选择的一处未占据空间。失败或成功：金龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "明光道标",
        "en_name": "Guiding Light",
        "description": "金龙使用施法施展光导箭Guiding \nBolt （四环版本）。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "金龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\金龙\\远古金龙.htm"
  },
  {
    "name": "青年金龙",
    "en_name": "Young Gold Dragon",
    "type_line": "大型龙类（金属龙），守序善良",
    "size": "Large",
    "creature_type": "龙类（金属龙）",
    "alignment": "守序善良",
    "ac": 18,
    "initiative_bonus": 6,
    "initiative_total": 16,
    "hp": 178,
    "hp_formula": "17d10+85",
    "speed": {
      "walk": "40尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 6
      },
      "体质": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 5
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 5
      }
    },
    "skills": {
      "洞悉": 5,
      "察觉": 9,
      "游说": 9,
      "隐匿": 6
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 19
    },
    "languages": "通用语，龙语",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "金龙可以在空气和水中呼吸。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "金龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用弱化吐息。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+10，触及10尺。命中：17（2d10+6）挥砍伤害。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC17，30尺锥状区域内的每名生物。失败：55（10d10）火焰伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "弱化吐息",
        "en_name": "Weakening Breath",
        "description": "力量豁免检定：DC17，30尺锥状区域内未被此吐息影响的每名生物。失败：目标进行基于力量的D20检定时具有劣势，且其伤害掷骰承受2（1d4）减值。目标在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。"
      }
    ],
    "source_file": "龙类\\金龙\\青年金龙.htm"
  },
  {
    "name": "成年银龙",
    "en_name": "Adult Silver Dragon",
    "type_line": "巨型龙类（金属龙），守序善良",
    "size": "Huge",
    "creature_type": "龙类（金属龙）",
    "alignment": "守序善良",
    "ac": 19,
    "initiative_bonus": 10,
    "initiative_total": 20,
    "hp": 216,
    "hp_formula": "16d12+112",
    "speed": {
      "walk": "40尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 27,
        "mod": 8,
        "save": 8
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 5
      },
      "体质": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 6
      },
      "魅力": {
        "score": 22,
        "mod": 6,
        "save": 6
      }
    },
    "skills": {
      "历史": 8,
      "察觉": 11,
      "隐匿": 5
    },
    "damage_immunities": [
      "寒冷"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 21
    },
    "languages": "通用语，龙语",
    "cr": 16,
    "xp": 15000,
    "pb": 5,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "银龙豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "银龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用（A）麻痹吐息或（B）施法施展冰刃Ice Knife。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+13，触及10尺。命中：17（2d8+8）挥砍伤害外加4（1d8）寒冷伤害。"
      },
      {
        "name": "寒冷吐息",
        "en_name": "Cold Breath",
        "description": "体质豁免检定：DC20，60尺锥状区域内的每名生物。失败：54（12d8）寒冷伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "麻痹吐息",
        "en_name": "Paralyzing Breath",
        "description": "体质豁免检定：DC20，60尺锥状区域内的每名生物。首次失败：目标陷入失能状态直至其下个回合结束，此时目标重复豁免。再次失败：目标陷入麻痹状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "银龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC19，法术攻击命中+11）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，定身怪物Hold Monster，冰刃Ice Knife，形体变化Shapechange（仅野兽与类人形态，不会因此法术获得临时生命值，但无需为维持此法术而保有临时生命值或维持专注）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "冰风暴Ice Storm（五环版本）， 诚实之域Zone of Truth"
      }
    ],
    "legendary_actions": [
      {
        "name": "彻骨冻寒",
        "en_name": "Chill",
        "description": "银龙使用施法施展定身怪物Hold \nMonster 。银龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "寒风掠",
        "en_name": "Cold Gale",
        "description": "敏捷豁免检定：DC19，60尺长、10尺宽的线状区域内的每名生物。失败：14（4d6）寒冷伤害，且银龙将目标直线推离至多30尺。成功：仅半伤。失败或成功：银龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "银龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\银龙\\成年银龙.htm"
  },
  {
    "name": "远古银龙",
    "en_name": "Ancient Silver Dragon",
    "type_line": "超巨型龙类（金属龙），守序善良",
    "size": "Gargantuan",
    "creature_type": "龙类（金属龙）",
    "alignment": "守序善良",
    "ac": 22,
    "initiative_bonus": 14,
    "initiative_total": 24,
    "hp": 468,
    "hp_formula": "24d20+216",
    "speed": {
      "walk": "40尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 30,
        "mod": 10,
        "save": 10
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 7
      },
      "体质": {
        "score": 29,
        "mod": 9,
        "save": 9
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 9
      },
      "魅力": {
        "score": 26,
        "mod": 8,
        "save": 8
      }
    },
    "skills": {
      "历史": 11,
      "察觉": 16,
      "隐匿": 7
    },
    "damage_immunities": [
      "寒冷"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 26
    },
    "languages": "通用语，龙语",
    "cr": 23,
    "xp": 50000,
    "pb": 7,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "银龙豁免失败时，可以将其改为豁免成功。",
        "params": "4/日，或巢穴内5/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "银龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用（A）麻痹吐息或（B）施法施展冰刃Ice Knife （二环版本）。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+17，触及15尺。命中：19（2d8+10）挥砍伤害外加9（2d8）寒冷伤害。"
      },
      {
        "name": "寒冷吐息",
        "en_name": "Cold Breath",
        "description": "体质豁免检定：DC24，90尺锥状区域内的每名生物。失败：67（15d8）寒冷伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "麻痹吐息",
        "en_name": "Paralyzing Breath",
        "description": "体质豁免检定：DC24，90尺锥状区域内的每名生物。首次失败：目标陷入失能状态直至其下个回合结束，此时目标重复豁免。再次失败：目标陷入麻痹状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "银龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC23，法术攻击命中+15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，定身怪物Hold Monster，冰刃Ice Knife（二环版本），   形体变化Shapechange（仅野兽与类人形态，不会因此法术获得临时生命值，但无需为维持此法术而保有临时生命值或维持专注）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "操控天气Control Weather，冰风暴Ice Storm（七环版本），  传送术Teleport，诚实之域Zone of Truth"
      }
    ],
    "legendary_actions": [
      {
        "name": "彻骨冻寒",
        "en_name": "Chill",
        "description": "银龙使用施法施展定身怪物Hold \nMonster 。银龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "寒风掠",
        "en_name": "Cold Gale",
        "description": "敏捷豁免检定：DC23，60尺长、10尺宽的线状区域内的每个生物。失败：14（4d6）寒冷伤害，且银龙将目标直线推离至多30尺。成功：仅半伤。失败或成功：银龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "银龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\银龙\\远古银龙.htm"
  },
  {
    "name": "银龙雏龙",
    "en_name": "Silver Dragon Wyrmling",
    "type_line": "中型龙类（金属龙），守序善良",
    "size": "Medium",
    "creature_type": "龙类（金属龙）",
    "alignment": "守序善良",
    "ac": 17,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 45,
    "hp_formula": "6d8+18",
    "speed": {
      "walk": "30尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 2
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 2
    },
    "damage_immunities": [
      "寒冷"
    ],
    "senses": {
      "盲视": 10,
      "被动察觉": 14
    },
    "languages": "龙语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "银龙发动两次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+6，触及5尺。命中：9（1d10+4）穿刺伤害。"
      },
      {
        "name": "寒冷吐息",
        "en_name": "Cold Breath",
        "description": "体质豁免检定：DC13，15尺锥状区域内的每名生物。失败：18（4d8）寒冷伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "麻痹吐息",
        "en_name": "Paralyzing Breath",
        "description": "体质豁免检定：DC13，15尺锥状区域内的每名生物。首次失败：目标陷入失能状态直至其下个回合结束，此时目标重复豁免。再次失败：目标陷入麻痹状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。"
      }
    ],
    "source_file": "龙类\\银龙\\银龙雏龙.htm"
  },
  {
    "name": "青年银龙",
    "en_name": "Young Silver Dragon",
    "type_line": "大型龙类（金属龙），守序善良",
    "size": "Large",
    "creature_type": "龙类（金属龙）",
    "alignment": "守序善良",
    "ac": 18,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 168,
    "hp_formula": "16d10+80",
    "speed": {
      "walk": "40尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 4
      },
      "体质": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 4
      },
      "魅力": {
        "score": 19,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "历史": 6,
      "察觉": 8,
      "隐匿": 4
    },
    "damage_immunities": [
      "寒冷"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 18
    },
    "languages": "通用语，龙语",
    "cr": 9,
    "xp": 5000,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "银龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用其麻痹吐息。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+10，触及10尺。命中：15（2d8+6）挥砍伤害。"
      },
      {
        "name": "寒冷吐息",
        "en_name": "Cold Breath",
        "description": "体质豁免检定：DC17，30尺锥状区域内的每名生物。失败：49（11d8）寒冷伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "麻痹吐息",
        "en_name": "Paralyzing Breath",
        "description": "体质豁免检定：DC17，30尺锥状区域内的每名生物。首次失败：目标陷入失能状态直至其下个回合结束，此时目标重复豁免。再次失败：目标陷入麻痹状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。"
      }
    ],
    "source_file": "龙类\\银龙\\青年银龙.htm"
  },
  {
    "name": "成年青铜龙",
    "en_name": "Adult Bronze Dragon",
    "type_line": "巨型龙类（金属龙），守序善良",
    "size": "Huge",
    "creature_type": "龙类（金属龙）",
    "alignment": "守序善良",
    "ac": 18,
    "initiative_bonus": 10,
    "initiative_total": 20,
    "hp": 212,
    "hp_formula": "17d12+102",
    "speed": {
      "walk": "40尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 5
      },
      "体质": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 7
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 5
      }
    },
    "skills": {
      "洞悉": 7,
      "察觉": 12,
      "隐匿": 5
    },
    "damage_immunities": [
      "闪电"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 22
    },
    "languages": "通用语，龙语",
    "cr": 15,
    "xp": 13000,
    "pb": 5,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "青铜龙可以在空气和水中呼吸。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "青铜龙豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "青铜龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用（A）斥力吐息或（B）施法施展光导箭Guiding \nBolt （二环版本）。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+12，触及10尺。命中：16（2d8+7）挥砍伤害外加5（1d10）闪电伤害。"
      },
      {
        "name": "闪电吐息",
        "en_name": "Lightning Breath",
        "description": "敏捷豁免检定：DC19，90尺长、5尺宽的线状区域内的每个生物。失败：55（10d10）闪电伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "斥力吐息",
        "en_name": "Repulsion Breath",
        "description": "力量豁免检定：DC19，30尺锥状区域内的每名生物。失败：目标被青铜龙直线推离至多60尺并陷入倒地状态。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "青铜龙施展以下一道法术，无需任何材料成分并使用魅力作为施法属性（法术豁免DC17，法术攻击命中+10）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，光导箭Guiding Bolt（二环版本），    形体变化Shapechange（仅野兽与类人形态，不会因此法术获得临时生命值，但无需为维持此法术而保有临时生命值或维持专注），  动物交谈Speak with Animal，奇术Thaumaturgy"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "侦测思想Detect Thoughts，水下呼吸Water Breathing"
      }
    ],
    "legendary_actions": [
      {
        "name": "明光道标",
        "en_name": "Guiding Light",
        "description": "青铜使用施法施展光导箭Guiding Bolt （二环版本）。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "青铜龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      },
      {
        "name": "鸣雷霆爆",
        "en_name": "Thunderclap",
        "description": "体质豁免检定：DC17，以120尺内青铜龙可见一点为中心，半径20尺球状区域内的每个生物。失败：10（3d6）雷鸣伤害，且目标陷入耳聋状态直至其下个回合结束。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\青铜龙\\成年青铜龙.htm"
  },
  {
    "name": "远古青铜龙",
    "en_name": "Ancient Bronze Dragon",
    "type_line": "超巨型龙类（金属龙），守序善良",
    "size": "Gargantuan",
    "creature_type": "龙类（金属龙）",
    "alignment": "守序善良",
    "ac": 22,
    "initiative_bonus": 14,
    "initiative_total": 24,
    "hp": 444,
    "hp_formula": "24d20+192",
    "speed": {
      "walk": "40尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 29,
        "mod": 9,
        "save": 9
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 7
      },
      "体质": {
        "score": 27,
        "mod": 8,
        "save": 8
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 17,
        "mod": 3,
        "save": 10
      },
      "魅力": {
        "score": 25,
        "mod": 7,
        "save": 7
      }
    },
    "skills": {
      "洞悉": 10,
      "察觉": 17,
      "隐匿": 7
    },
    "damage_immunities": [
      "闪电"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 27
    },
    "languages": "通用语，龙语",
    "cr": 22,
    "xp": 41000,
    "pb": 7,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "青铜龙可以在空气和水中呼吸。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "青铜龙豁免失败时，可以将其改为豁免成功。",
        "params": "4/日，或巢穴内5/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "青铜龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用（A）斥力吐息或（B）施法施展光导箭Guiding \nBolt （二环版本）。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+16，触及15尺。命中：18（2d8+9）挥砍伤害外加9（2d8）闪电伤害。"
      },
      {
        "name": "闪电吐息",
        "en_name": "Lightning Breath",
        "description": "敏捷豁免检定：DC23，120尺长、10尺宽的线状区域内的每个生物。失败：82（15d10）闪电伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "斥力吐息",
        "en_name": "Repulsion Breath",
        "description": "力量豁免检定：DC23，30尺锥状区域内的每名生物。失败：目标被青铜龙直线推离至多60尺并陷入倒地状态。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "青铜龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC22，法术攻击命中+14）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，光导箭Guiding \nBolt（二环版本），   \n   \n形体变化Shapechange（仅野兽与类人形态，不会因此法术获得临时生命值，但无需为维持此法术而保有临时生命值或维持专注）， \n动物交谈Speak with Animal，奇术Thaumaturgy"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "侦测思想Detect Thoughts，操控水体Control \nWater，水下呼吸Water Breathing"
      }
    ],
    "legendary_actions": [
      {
        "name": "明光道标",
        "en_name": "Guiding Light",
        "description": "青铜使用施法施展光导箭Guiding Bolt （二环版本）。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "青铜龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      },
      {
        "name": "鸣雷霆爆",
        "en_name": "Thunderclap",
        "description": "体质豁免检定：DC22，以120尺内青铜龙可见一点为中心，半径20尺球状区域内的每名生物。失败：13（3d8）雷鸣伤害，且目标陷入耳聋状态直至其下个回合结束。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\青铜龙\\远古青铜龙.htm"
  },
  {
    "name": "青年青铜龙",
    "en_name": "Young Bronze Dragon",
    "type_line": "大型龙类（金属龙），守序善良",
    "size": "Large",
    "creature_type": "龙类（金属龙）",
    "alignment": "守序善良",
    "ac": 17,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 142,
    "hp_formula": "15d10+60",
    "speed": {
      "walk": "40尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 3
      },
      "体质": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 4
      },
      "魅力": {
        "score": 17,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "洞悉": 4,
      "察觉": 7,
      "隐匿": 3
    },
    "damage_immunities": [
      "闪电"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 17
    },
    "languages": "通用语，龙语",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "青铜龙可以在空气和水中呼吸。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "青铜龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用斥力吐息。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+8，触及10尺。命中：16（2d10+5）挥砍伤害。"
      },
      {
        "name": "闪电吐息",
        "en_name": "Lightning Breath",
        "description": "敏捷豁免检定：DC15，60尺长、5尺宽的线状区域内的每个生物。失败：49（9d10）闪电伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "斥力吐息",
        "en_name": "Repulsion Breath",
        "description": "力量豁免检定：DC15，30尺锥状区域内的每个生物。失败：目标被青铜龙直线推离至多40尺并陷入倒地状态。"
      }
    ],
    "source_file": "龙类\\青铜龙\\青年青铜龙.htm"
  },
  {
    "name": "青铜龙雏龙",
    "en_name": "Bronze Dragon Wyrmling",
    "type_line": "中型龙类（金属龙），守序善良",
    "size": "Medium",
    "creature_type": "龙类（金属龙）",
    "alignment": "守序善良",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 39,
    "hp_formula": "6d8+12",
    "speed": {
      "walk": "30尺，飞行60尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 2
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 2
    },
    "damage_immunities": [
      "闪电"
    ],
    "senses": {
      "盲视": 10,
      "被动察觉": 14
    },
    "languages": "龙语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "青铜龙可以在空气和水中呼吸。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "青铜龙发动两次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+5，触及5尺。命中：8（1d10+3）挥砍伤害。"
      },
      {
        "name": "闪电吐息",
        "en_name": "Lightning Breath",
        "description": "敏捷豁免检定：DC12，40尺长、5尺宽的线状区域内的每名生物。失败：16（3d10）闪电伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "斥力吐息",
        "en_name": "Repulsion Breath",
        "description": "力量豁免检定：DC12，30尺锥状区域内的每名生物。失败：目标被青铜龙直线推离至多30尺并陷入倒地状态。"
      }
    ],
    "source_file": "龙类\\青铜龙\\青铜龙雏龙.htm"
  },
  {
    "name": "成年黄铜龙",
    "en_name": "Adult Brass Dragon",
    "type_line": "巨型龙类（金属龙），混乱善良",
    "size": "Huge",
    "creature_type": "龙类（金属龙）",
    "alignment": "混乱善良",
    "ac": 18,
    "initiative_bonus": 10,
    "initiative_total": 20,
    "hp": 172,
    "hp_formula": "15d12+75",
    "speed": {
      "walk": "40尺，掘穴30尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 5
      },
      "体质": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 6
      },
      "魅力": {
        "score": 17,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "历史": 7,
      "察觉": 11,
      "游说": 8,
      "隐匿": 5
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 21
    },
    "languages": "通用语，龙语",
    "cr": 13,
    "xp": 10000,
    "pb": 5,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "黄铜龙豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "黄铜龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用（A）睡眠吐息或（B）施法施展灼热射线Scorching \nRay 。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+11，触及10尺。命中：17（2d10+6）挥砍伤害外加4（1d8）火焰伤害。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC18，60尺长、5尺宽的线状区域内的每名生物。失败：45（10d8）火焰伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "睡眠吐息",
        "en_name": "Sleep Breath",
        "description": "体质豁免检定：DC18，60尺锥状区域内的每名生物。首次失败：目标陷入失能状态，直至其下个回合结束，此时目标重复豁免。再次失败：目标陷入昏迷状态，持续1分钟。目标身上的此效应在其受到伤害或被目标5尺内的另一生物用一个动作摇醒时提前结束。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "黄铜龙施展以下一道法术，无需任何材料成分并使用魅力作为施法属性（法术豁免DC16）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，次级幻象Minor Illusion，灼热射线Scorching Ray，形体变化Shapechange（仅野兽与类人形态，不会因此法术获得临时生命值，但无需为维持此法术而保有临时生命值或维持专注），   动物交谈Speak with Animals"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "侦测思想Detect Thoughts，操控天气Control Weather"
      }
    ],
    "legendary_actions": [
      {
        "name": "光炎烧却",
        "en_name": "Blazing Light",
        "description": "黄铜龙使用施法施展灼热射线Scorching Ray 。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "黄铜龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      },
      {
        "name": "尘沙灼",
        "en_name": "Scorching Sands",
        "description": "敏捷豁免检定：DC16，单一120尺内黄铜龙可见的生物。失败：27（6d8）火焰伤害，且目标速度减半直至其下个回合结束。失败或成功：黄铜龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\黄铜龙\\成年黄铜龙.htm"
  },
  {
    "name": "远古黄铜龙",
    "en_name": "Ancient Brass Dragon",
    "type_line": "超巨型龙类（金属龙），混乱善良",
    "size": "Gargantuan",
    "creature_type": "龙类（金属龙）",
    "alignment": "混乱善良",
    "ac": 20,
    "initiative_bonus": 12,
    "initiative_total": 22,
    "hp": 332,
    "hp_formula": "19d20+133",
    "speed": {
      "walk": "40尺，掘穴40尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 27,
        "mod": 8,
        "save": 8
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 6
      },
      "体质": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 8
      },
      "魅力": {
        "score": 22,
        "mod": 6,
        "save": 6
      }
    },
    "skills": {
      "历史": 9,
      "察觉": 14,
      "游说": 12,
      "隐匿": 6
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 24
    },
    "languages": "通用语，龙语",
    "cr": 20,
    "xp": 25000,
    "pb": 6,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "黄铜龙豁免失败时，可以将其改为豁免成功。",
        "params": "4/日，或巢穴内5/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "黄铜龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用（A）睡眠吐息或（B）施法施展灼热射线Scorching \nRay （三环版本）。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+14，触及15尺。命中：19（2d10+8）挥砍伤害外加7（2d6）火焰伤害。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC21，90尺长、5尺宽的线状区域内的每名生物。失败：58（13d8）火焰伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "睡眠吐息",
        "en_name": "Sleep Breath",
        "description": "体质豁免检定：DC21，90尺锥状区域内的每名生物。首次失败：目标陷入失能状态，直至其下个回合结束，此时目标重复豁免。再次失败：目标陷入昏迷状态，持续1分钟。目标身上的此效应在其受到伤害或被目标5尺内的另一生物用一个动作摇醒时提前结束。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "黄铜龙施展以下一道法术，无需任何材料成分并使用魅力作为施法属性（法术豁免DC20）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，次级幻象Minor Illusion，灼热射线Scorching Ray（三环版本），     形体变化Shapechange（仅野兽与类人形态，不会因此法术获得临时生命值，但无需为维持此法术而保有临时生命值或维持专注），   动物交谈Speak with Animals"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "操控天气Control Weather，侦测思想Detect Thoughts"
      }
    ],
    "legendary_actions": [
      {
        "name": "光炎烧却",
        "en_name": "Blazing Light",
        "description": "黄铜龙使用施法施展灼热射线Scorching Ray （三环版本）。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "黄铜龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      },
      {
        "name": "尘沙灼",
        "en_name": "Scorching Sands",
        "description": "敏捷豁免检定：DC20，单一120尺内黄铜龙可见的生物。失败：36（8d8）火焰伤害，且目标速度减半直至其下个回合结束。失败或成功：黄铜龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\黄铜龙\\远古黄铜龙.htm"
  },
  {
    "name": "青年黄铜龙",
    "en_name": "Young Brass Dragon",
    "type_line": "大型龙类（金属龙），混乱善良",
    "size": "Large",
    "creature_type": "龙类（金属龙）",
    "alignment": "混乱善良",
    "ac": 17,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 110,
    "hp_formula": "13d10+39",
    "speed": {
      "walk": "40尺，掘穴20尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 3
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 3
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 6,
      "游说": 5,
      "隐匿": 3
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 16
    },
    "languages": "通用语，龙语",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "黄铜龙发动三次撕裂攻击。其可以将其中两次攻击替换为使用睡眠吐息。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+7，触及10尺。命中：15（2d10+4）挥砍伤害。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC14，40尺长、5尺宽的线状区域内的每名生物。失败：38（11d6）火焰伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "睡眠吐息",
        "en_name": "Sleep Breath",
        "description": "体质豁免检定：DC14，30尺锥状区域内的每名生物。首次失败：目标陷入失能状态，直至其下个回合结束，此时目标重复豁免。再次失败：目标陷入昏迷状态，持续1分钟。目标身上的此效应在其受到伤害或被目标5尺内的另一生物用一个动作摇醒时提前结束。"
      }
    ],
    "source_file": "龙类\\黄铜龙\\青年黄铜龙.htm"
  },
  {
    "name": "黄铜龙雏龙",
    "en_name": "Brass Dragon Wyrmling",
    "type_line": "中型龙类（金属龙），混乱善良",
    "size": "Medium",
    "creature_type": "龙类（金属龙）",
    "alignment": "混乱善良",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 22,
    "hp_formula": "4d8+4",
    "speed": {
      "walk": "30尺，掘穴15尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 2
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 2
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "盲视": 10,
      "被动察觉": 14
    },
    "languages": "龙语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "actions": [
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+4，触及5尺。命中：7（1d10+2）挥砍伤害。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC11，20尺长、5尺宽的线状区域内的每名生物。失败：14（4d6）火焰伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "睡眠吐息",
        "en_name": "Sleep Breath",
        "description": "体质豁免检定：DC11，15尺锥状区域内的每名生物。首次失败：目标陷入失能状态，直至其下个回合结束，此时目标重复豁免。再次失败：目标陷入昏迷状态，持续1分钟。目标身上的此效应在其受到伤害或被目标5尺内的另一生物用一个动作摇醒时提前结束。"
      }
    ],
    "source_file": "龙类\\黄铜龙\\黄铜龙雏龙.htm"
  },
  {
    "name": "成年黑龙",
    "en_name": "Adult Black Dragon",
    "type_line": "巨型龙类（色彩龙），混乱邪恶",
    "size": "Huge",
    "creature_type": "龙类（色彩龙）",
    "alignment": "混乱邪恶",
    "ac": 19,
    "initiative_bonus": 12,
    "initiative_total": 22,
    "hp": 195,
    "hp_formula": "17d12+85",
    "speed": {
      "walk": "40尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 7
      },
      "体质": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 6
      },
      "魅力": {
        "score": 19,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "察觉": 11,
      "隐匿": 7
    },
    "damage_immunities": [
      "强酸"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 21
    },
    "languages": "通用语，龙语",
    "cr": 14,
    "xp": 11500,
    "pb": 5,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "黑龙可以在空气和水中呼吸。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "黑龙豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "黑龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用施法施展马友夫强酸箭Melf‘s \nAcid Arrow  （三环版本）。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+11，触及10尺。命中：13（2d6+6）挥砍伤害外加4（1d8）强酸伤害。"
      },
      {
        "name": "强酸吐息",
        "en_name": "Acid Breath",
        "description": "敏捷豁免检定：DC18，60尺长、5尺宽的线状区域内的每名生物。失败：54（12d8）强酸伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "黑龙施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC17，法术攻击命中+9）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，恐惧术Fear，马友夫强酸箭Melf‘s Acid Arrow（三环版本）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "死者交谈Speak with Dead，浓酸球Vitriolic Sphere"
      }
    ],
    "legendary_actions": [
      {
        "name": "虫群云聚",
        "en_name": "Cloud of Insects",
        "description": "敏捷豁免检定：DC17，单一120尺内黑龙可见的生物。失败：22（4d10）毒素伤害，且目标为维持专注进行的体质豁免具有劣势，持续至其下个回合结束。失败或成功：黑龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "骇人威仪",
        "en_name": "Frightful Presence",
        "description": "黑龙使用施法施展恐惧术Fear。黑龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "黑龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\黑龙\\成年黑龙.htm"
  },
  {
    "name": "远古黑龙",
    "en_name": "Ancient Black Dragon",
    "type_line": "超巨型龙类（色彩龙），混乱邪恶",
    "size": "Gargantuan",
    "creature_type": "龙类（色彩龙）",
    "alignment": "混乱邪恶",
    "ac": 22,
    "initiative_bonus": 16,
    "initiative_total": 26,
    "hp": 367,
    "hp_formula": "21d20+147",
    "speed": {
      "walk": "40尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 27,
        "mod": 8,
        "save": 8
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 9
      },
      "体质": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 9
      },
      "魅力": {
        "score": 22,
        "mod": 6,
        "save": 6
      }
    },
    "skills": {
      "察觉": 16,
      "隐匿": 9
    },
    "damage_immunities": [
      "强酸"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 26
    },
    "languages": "通用语，龙语",
    "cr": 21,
    "xp": 33000,
    "pb": 7,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "黑龙可以在空气和水中呼吸。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "黑龙豁免失败时，可以将其改为豁免成功。",
        "params": "4/日，或巢穴内5/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "黑龙发动三次撕裂攻击。其可以将其中一次攻击替换为使用施法施展马友夫强酸箭Melf‘s \nAcid Arrow  （四环版本）。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+15，触及15尺。命中：17（2d8+8）挥砍伤害外加9（2d8）强酸伤害。"
      },
      {
        "name": "强酸吐息",
        "en_name": "Acid Breath",
        "description": "敏捷豁免检定：DC22，90尺长、5尺宽的线状区域内的每名生物。失败：67（15d8）强酸伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "黑龙施展以下一道法术，无需任何材料成分并使用魅力作为施法属性（法术豁免DC21，法术攻击命中+13）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，恐惧术Fear，马友夫强酸箭Melf‘s Acid Arrow（四环版本）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "唤起亡灵Create Undead，死者交谈Speak with Dead，浓酸球Vitriolic Sphere（五环版本）"
      }
    ],
    "legendary_actions": [
      {
        "name": "虫群云聚",
        "en_name": "Cloud of Insects",
        "description": "敏捷豁免检定：DC21，单一120尺内黑龙可见的生物。失败：33（6d10）毒素伤害，且目标为维持专注进行的体质豁免具有劣势，持续至其下个回合结束。失败或成功：黑龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "骇人威仪",
        "en_name": "Frightful Presence",
        "description": "黑龙使用施法施展恐惧术Fear。黑龙直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "扑杀",
        "en_name": "Pounce",
        "description": "黑龙移动至多等于其速度一半的距离并发动一次撕裂攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "龙类\\黑龙\\远古黑龙.htm"
  },
  {
    "name": "青年黑龙",
    "en_name": "Young Black Dragon",
    "type_line": "大型龙类（色彩龙），混乱邪恶",
    "size": "Large",
    "creature_type": "龙类（色彩龙）",
    "alignment": "混乱邪恶",
    "ac": 18,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 127,
    "hp_formula": "15d10+45",
    "speed": {
      "walk": "40尺，飞行80尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 3
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 6,
      "隐匿": 5
    },
    "damage_immunities": [
      "强酸"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 16
    },
    "languages": "通用语，龙语",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "黑龙可以在空气和水中呼吸。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "黑龙发动三次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+7，触及10尺。命中：9（2d4+4）挥砍伤害外加3（1d6）强酸伤害。"
      },
      {
        "name": "强酸吐息",
        "en_name": "Acid Breath",
        "description": "敏捷豁免检定：DC11，30尺长、5尺宽的线状区域内的每名生物。失败：46（14d6）强酸伤害。成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "source_file": "龙类\\黑龙\\青年黑龙.htm"
  },
  {
    "name": "黑龙雏龙",
    "en_name": "Black Dragon Wyrmling",
    "type_line": "中型龙类（色彩龙），混乱邪恶",
    "size": "Medium",
    "creature_type": "龙类（色彩龙）",
    "alignment": "混乱邪恶",
    "ac": 17,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 33,
    "hp_formula": "6d8+6",
    "speed": {
      "walk": "30尺，飞行60尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 4
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 4
    },
    "damage_immunities": [
      "强酸"
    ],
    "senses": {
      "盲视": 10,
      "被动察觉": 14
    },
    "languages": "龙语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "黑龙可以在空气和水中呼吸。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "黑龙发动两次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）挥砍伤害外加2（1d4）强酸伤害。"
      },
      {
        "name": "强酸吐息",
        "en_name": "Acid Breath",
        "description": "敏捷豁免检定：DC11，15尺长、5尺宽的线状区域内的每名生物。失败：22（5d8）强酸伤害。成功：半伤。",
        "params": "充能5~6"
      }
    ],
    "source_file": "龙类\\黑龙\\黑龙雏龙.htm"
  },
  {
    "name": "奥法罗斯魔",
    "en_name": "Arcanaloth",
    "type_line": "中型邪魔（尤格罗斯魔），中立邪恶",
    "size": "Medium",
    "creature_type": "邪魔（尤格罗斯魔）",
    "alignment": "中立邪恶",
    "ac": 18,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 175,
    "hp_formula": "27d8+54",
    "speed": {
      "walk": "30尺，飞行速度60尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 5
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 6
      },
      "智力": {
        "score": 20,
        "mod": 5,
        "save": 9
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "魅力": {
        "score": 17,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "奥秘": 9,
      "欺瞒": 7,
      "洞悉": 7,
      "察觉": 7
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "强酸",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "中毒"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 17
    },
    "languages": "所有；心灵感应120尺",
    "cr": 12,
    "xp": 8400,
    "pb": 4,
    "traits": [
      {
        "name": "邪魔复苏",
        "en_name": "Fiendish Restoration",
        "description": "若奥法罗斯魔于焦炎火狱之外死去，其身躯将会溶解成脓水，并立即在焦炎火狱某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "奥法罗斯魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "灵魂秘典",
        "en_name": "Soul Tome",
        "description": "奥法罗斯魔持有一本魔法秘典。持有或携带此秘典期间，奥法罗斯魔可以使用其放逐利爪动作。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "奥法罗斯魔发动三次邪能爆攻击。其可以将一次攻击替换为放逐利爪攻击。"
      },
      {
        "name": "邪能爆",
        "en_name": "Fiendish Burst",
        "description": "近战或远程攻击检定：+9，触及5尺或射程120尺。命中：31（4d12+5）暗蚀伤害。"
      },
      {
        "name": "放逐利爪（需灵魂秘典）",
        "en_name": "Banishing Claw",
        "description": "近战攻击检定：+9，触及5尺。命中：10（2d4+5）点挥砍伤害外加19（3d12）点心灵伤害。若目标为生物，则目标承受以下效应。魅力豁免检定：DC17。失败：目标被困在灵魂秘典内的半位面中。受困期间，目标陷入失能状态。目标在其回合结束时重复豁免，成功则逃出秘典。当目标逃出时，目标出现在其消失的空间。若该空间被占据，则其将出现在最近的未占据空间。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "奥法罗斯魔施展以下一道法术，无需材料成分并使用智力作为施法属性（法术豁免DC17）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "变身术Alter Self，侦测魔法Detect Magic，鉴定术Identify，法师之手Mage Hand，魔法伎俩Prestidigitation"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "异界探知Contact Other Plane，侦测思想Detect Thoughts，任意门Dimension Door，心灵屏障Mind Blank"
      }
    ],
    "bonus_actions": [
      {
        "name": "传送",
        "en_name": "Teleport",
        "description": "奥法罗斯魔传送至多30尺至一处其可见的未占据空间。"
      }
    ],
    "reactions": [
      {
        "name": "法术反制",
        "en_name": "Counterspell",
        "description": "奥法罗斯魔施展法术反制Counterspell（触发条件见该法术），使用与施法动作相同的施法属性。"
      }
    ],
    "source_file": "邪魔\\尤格罗斯魔\\奥法罗斯魔.htm"
  },
  {
    "name": "征伐罗斯魔",
    "en_name": "Nycaloth",
    "type_line": "大型邪魔（尤格罗斯魔），中立邪恶",
    "size": "Large",
    "creature_type": "邪魔（尤格罗斯魔）",
    "alignment": "中立邪恶",
    "ac": 18,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 152,
    "hp_formula": "16d10+64",
    "speed": {
      "walk": "40尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 4
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "强酸",
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 14
    },
    "languages": "深渊语，炼狱语；心灵感应60尺",
    "cr": 9,
    "xp": 5000,
    "pb": 4,
    "traits": [
      {
        "name": "邪魔复苏",
        "en_name": "Fiendish Restoration",
        "description": "若征伐罗斯魔于焦炎火狱之外死去，其身躯将会溶解成脓水，并立即在焦炎火狱某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "征伐罗斯魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "征伐罗斯魔发动两次变幻巨斧攻击。"
      },
      {
        "name": "变幻巨斧",
        "en_name": "Mercurial Axe",
        "description": "近战或远程攻击检定：+9，触及10尺或射程30/90尺。命中：18（2d12+5）点挥砍伤害外加10（3d6）点力场伤害。命中或失手：巨斧在远程攻击后立即魔法地回到征伐罗斯魔手中。"
      }
    ],
    "bonus_actions": [
      {
        "name": "蔽影传送",
        "en_name": "Shadowy Teleport",
        "description": "征伐罗斯魔获得隐形状态，持续1分钟，并且其传送至多30尺至一处其可见的未占据空间。隐形状态在征伐罗斯魔造成伤害后立即提前结束。"
      }
    ],
    "source_file": "邪魔\\尤格罗斯魔\\征伐罗斯魔.htm"
  },
  {
    "name": "毒虫罗斯魔",
    "en_name": "Mezzoloth",
    "type_line": "中型邪魔（尤格罗斯魔），中立邪恶",
    "size": "Medium",
    "creature_type": "邪魔（尤格罗斯魔）",
    "alignment": "中立邪恶",
    "ac": 18,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 75,
    "hp_formula": "10d8+30",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 5
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "强酸",
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 15
    },
    "languages": "深渊语，炼狱语；心灵感应60尺",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "邪魔复苏",
        "en_name": "Fiendish Restoration",
        "description": "若毒虫罗斯魔于焦炎火狱之外死去，其身躯将会溶解成脓水，并立即在焦炎火狱某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "毒虫罗斯魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "毒虫罗斯魔使用爪击或变幻三叉戟发动共计两次攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claws",
        "description": "近战攻击检定：+7，触及5尺。命中：9（2d4+4）挥砍伤害，若目标生物体型不超过大型，则其被四爪之二擒抱，陷入受擒状态（逃脱DC14），且目标陷入束缚状态直至擒抱结束。"
      },
      {
        "name": "变幻三叉戟",
        "en_name": "Mercurial Trident",
        "description": "近战或远程攻击检定：+7，触及5尺或射程20/60尺。命中：8（1d8+4）穿刺伤害外加10（3d6）力场伤害。命中或失手：三叉戟在远程攻击后立即魔法地回到毒虫罗斯魔爪中。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "毒虫罗斯魔施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC13）："
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "死云术Cloudkill，黑暗术Darkness，解除魔法Dispel Magic"
      }
    ],
    "bonus_actions": [
      {
        "name": "传送",
        "en_name": "Teleport",
        "description": "毒虫罗斯魔传送至多60尺至一处其可见的未占据空间中。其可以将一名正被其擒抱的生物传送至目标空间5尺内的未占据空间。",
        "params": "充能 5–6"
      }
    ],
    "source_file": "邪魔\\尤格罗斯魔\\毒虫罗斯魔.htm"
  },
  {
    "name": "超等罗斯魔",
    "en_name": "Ultroloth",
    "type_line": "中型邪魔（尤格罗斯魔），中立邪恶",
    "size": "Medium",
    "creature_type": "邪魔（尤格罗斯魔）",
    "alignment": "中立邪恶",
    "ac": 19,
    "initiative_bonus": 8,
    "initiative_total": 18,
    "hp": 221,
    "hp_formula": "26d8+104",
    "speed": {
      "walk": "30尺，飞行速度60尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "欺瞒": 9,
      "察觉": 7,
      "隐匿": 8
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "强酸",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "恐慌",
      "中毒"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 17
    },
    "languages": "深渊语，炼狱语；心灵感应120尺",
    "cr": 13,
    "xp": 10000,
    "pb": 5,
    "traits": [
      {
        "name": "邪魔复苏",
        "en_name": "Fiendish Restoration",
        "description": "若超等罗斯魔于焦炎火狱之外死去，其身躯将会溶解成脓水，并立即在焦炎火狱某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "超等罗斯魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "超等罗斯魔使用催眠凝视并发动两次变幻长鞭攻击。"
      },
      {
        "name": "变幻长鞭",
        "en_name": "Mercurial Whip",
        "description": "近战攻击检定：+9，触及15尺。命中：25（6d6+4）力场伤害，并且超等罗斯魔可以将目标传送至多10尺至一处超等罗斯魔可见且不在空中的未占据空间。"
      },
      {
        "name": "催眠凝视",
        "en_name": "Hypnotic Gaze",
        "description": "感知豁免检定：DC17，30尺锥状区域内的每名生物。失败： 10（3d6）心灵伤害，且目标陷入震慑状态直至超等罗斯魔的下个回合开始。成功：目标在24小时内免疫此超等罗斯魔的催眠凝视。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "超等罗斯魔施展以下一道法术，无需材料成分并使用智力作为施法属性（法术豁免DC17）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "变身术Alter Self，鹰眼术Clairvoyance，侦测魔法Detect Magic"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "任意门Dimension Door，火球术Fireball（五环版本）， 火墙术Wall of Fire"
      }
    ],
    "bonus_actions": [
      {
        "name": "邪魔诡计",
        "en_name": "Fiendish Guile",
        "description": "超等罗斯魔施展解除魔法Dispel \nMagic，隐形术Invisibility（仅自身），迷踪步Misty \nStep或暗示术Suggestion，无需材料成分且使用与施法动作相同的施法属性。",
        "params": "充能4~6"
      }
    ],
    "source_file": "邪魔\\尤格罗斯魔\\超等罗斯魔.htm"
  },
  {
    "name": "幼虫魔",
    "en_name": "Larva",
    "type_line": "中型邪魔，中立邪恶",
    "size": "Medium",
    "creature_type": "邪魔",
    "alignment": "中立邪恶",
    "ac": 9,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 9,
    "hp_formula": "2d8",
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 2,
        "mod": -4,
        "save": -4
      }
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "理解通用语以及一门其他语言，但不会说",
    "cr": 0,
    "xp": 10,
    "pb": 2,
    "actions": [
      {
        "name": "啮咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+1，触及5尺。命中：1（1d4-1）暗蚀伤害。"
      }
    ],
    "source_file": "邪魔\\幼虫魔\\幼虫魔.htm"
  },
  {
    "name": "幼虫魔集群",
    "en_name": "Swarm of Larvae",
    "type_line": "中型邪魔的大型集群，中立邪恶",
    "size": "Medium",
    "creature_type": "邪魔的大型集群",
    "alignment": "中立邪恶",
    "ac": 13,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 22,
    "hp_formula": "3d10+6",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 2,
        "mod": -4,
        "save": -4
      }
    },
    "damage_resistances": [
      "钝击",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "魅惑",
      "恐慌",
      "受擒",
      "麻痹",
      "石化",
      "倒地",
      "束缚",
      "震慑"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "理解所有语言但不会说",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "集群",
        "en_name": "Swarm",
        "description": "集群可以进驻另一生物身处的空间，反之亦然。而且集群可以通过任何足够一只中型幼虫魔通过的通道。集群不能恢复生命值也不能获得临时生命值 。"
      }
    ],
    "actions": [
      {
        "name": "啮咬",
        "en_name": "Bites",
        "description": "近战攻击检定：+4，触及5尺。命中：9（2d6+2）暗蚀伤害，若集群浴血则为7（2d4+2）暗蚀伤害。"
      }
    ],
    "source_file": "邪魔\\幼虫魔\\幼虫魔集群.htm"
  },
  {
    "name": "六臂蛇魔",
    "en_name": "Marilith",
    "type_line": "大型邪魔（恶魔），混乱邪恶",
    "size": "Large",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 16,
    "initiative_bonus": 10,
    "initiative_total": 20,
    "hp": 220,
    "hp_formula": "21d10+105",
    "speed": {
      "walk": "40尺，攀爬40尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 9
      },
      "敏捷": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 10
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 8
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 10
      }
    },
    "skills": {
      "察觉": 8
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 18
    },
    "languages": "深渊语；心灵感应120尺",
    "cr": 16,
    "xp": 15000,
    "pb": 5,
    "traits": [
      {
        "name": "恶魔复苏",
        "en_name": "Demonic Restoration",
        "description": "若六臂蛇魔于无底深渊之外死去，其身躯会化为灰烬，并立即在无底深渊某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "六臂蛇魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "机敏反应",
        "en_name": "Reactive",
        "description": "六臂蛇魔在战斗中的每个回合均可执行一个反应。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "六臂蛇魔发动六次契约魔刃攻击并使用绞缠。"
      },
      {
        "name": "契约魔刃",
        "en_name": "Pact Blade",
        "description": "近战攻击检定：+10，触及5尺。命中：10（1d10+5）挥砍伤害外加7（2d6）暗蚀伤害。"
      },
      {
        "name": "绞缠",
        "en_name": "Constrict",
        "description": "力量豁免：DC17，单一5尺内六臂蛇魔可见的体型不超过中型的生物。失败：15（2d10+4）钝击伤害。目标陷入受擒状态（逃脱DC14），且目标陷入束缚状态直至擒抱结束。"
      }
    ],
    "bonus_actions": [
      {
        "name": "传送",
        "en_name": "Teleport",
        "description": "六臂蛇魔传送至多120尺至一处其可见的未占据空间。",
        "params": "充能5~6"
      }
    ],
    "reactions": [
      {
        "name": "格挡",
        "en_name": "Parry",
        "description": "触发：六臂蛇魔在持握武器期间因近战攻击检定被命中。响应：六臂蛇魔令其对抗那次攻击的AC+5，可能令那次攻击改为失手。"
      }
    ],
    "source_file": "邪魔\\恶魔\\六臂蛇魔.htm"
  },
  {
    "name": "判魂魔",
    "en_name": "Nalfeshnee",
    "type_line": "大型邪魔（恶魔），混乱邪恶",
    "size": "Large",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 18,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 184,
    "hp_formula": "16d10+96",
    "speed": {
      "walk": "20尺，飞行30尺"
    },
    "abilities": {
      "力量": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 22,
        "mod": 6,
        "save": 11
      },
      "智力": {
        "score": 19,
        "mod": 4,
        "save": 9
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 6
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 7
      }
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "恐慌",
      "中毒"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 11
    },
    "languages": "深渊语；心灵感应120尺",
    "cr": 13,
    "xp": 10000,
    "pb": 5,
    "traits": [
      {
        "name": "恶魔复苏",
        "en_name": "Demonic Restoration",
        "description": "若判魂魔于无底深渊之外死去，其身躯会化为灰烬，并立即在无底深渊某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "判魂魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "判魂魔发动两次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+10，触及10尺。命中：16（2d10+5）挥砍伤害外加11（2d10）力场伤害。"
      },
      {
        "name": "传送",
        "en_name": "Teleport",
        "description": "判魂魔传送至多120尺至一处其可见的未占据空间。"
      }
    ],
    "bonus_actions": [
      {
        "name": "恐惧灵气",
        "en_name": "Horror Nimbus",
        "description": "感知豁免：DC15，源自判魂魔的15尺光环区域内的每名生物。失败：28（8d6）心灵伤害，且目标陷入恐慌状态，持续1分钟，或在其受到伤害或其结束回合时判魂魔不在其视线中时提前结束。成功：目标在24小时内免疫此判魂魔的恐惧灵气。",
        "params": "充能5~6"
      }
    ],
    "reactions": [
      {
        "name": "追击",
        "en_name": "Pursuit",
        "description": "触发：另一名判魂魔可见的生物在判魂魔120尺内结束其移动时。响应：判魂魔使用传送，但目标空间必须位于触发生物10尺内。"
      }
    ],
    "source_file": "邪魔\\恶魔\\判魂魔.htm"
  },
  {
    "name": "喀嘶魔",
    "en_name": "Chasme",
    "type_line": "大型邪魔（恶魔），混乱邪恶",
    "size": "Large",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 15,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 78,
    "hp_formula": "12d10+12",
    "speed": {
      "walk": "20尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 5
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 5
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "盲视": 10,
      "被动察觉": 15
    },
    "languages": "深渊语，心灵感应120尺。",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "traits": [
      {
        "name": "恶魔复苏",
        "en_name": "Demonic Restoration",
        "description": "若喀嘶魔于无底深渊之外死去，其身躯会化为灰烬，并立即在无底深渊某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "喀嘶魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "蛛行",
        "en_name": "Spider Climb",
        "description": "喀嘶魔可以在难以攀爬的表面上攀爬，包括沿着天花板移动，且无需为此进行属性检定。"
      }
    ],
    "actions": [
      {
        "name": "刺喙",
        "en_name": "Proboscis",
        "description": "近战攻击检定：+5，触及5尺。命中：16（4d6+2）穿刺伤害外加21（6d6）暗蚀伤害。若目标为生物，其生命值上限减少等于其受到暗蚀伤害的数值。"
      }
    ],
    "bonus_actions": [
      {
        "name": "嗡鸣",
        "en_name": "Drone",
        "description": "体质豁免：DC12，源自喀嘶魔的30尺光环区域内的每名生物（此豁免恶魔自动成功）。失败：目标陷入昏迷状态，并在其回合结束时重复豁免。10分钟后，目标受到伤害时或其5尺内的生物以动作向目标泼洒一瓶圣水时，其豁免自动成功。成功：目标在24小时内免疫此喀嘶魔的嗡鸣。"
      }
    ],
    "source_file": "邪魔\\恶魔\\喀嘶魔.htm"
  },
  {
    "name": "小恶魔",
    "en_name": "Quasit",
    "type_line": "微型邪魔（恶魔），混乱邪恶",
    "size": "Tiny",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 25,
    "hp_formula": "10d4",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "隐匿": 5
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 10
    },
    "languages": "深渊语，通用语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "小恶魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+5，触及5尺。命中：5（1d4+3）挥砍伤害，且目标陷入中毒状态直至小恶魔的下个回合开始。"
      },
      {
        "name": "隐形",
        "en_name": "Invisibility",
        "description": "小恶魔对自身施展隐形术Invisbility，无需法术成分，并使用魅力作为施法属性。"
      },
      {
        "name": "惊吓",
        "en_name": "Scare",
        "description": "感知豁免：DC10，单一20尺内的生物。失败：目标陷入恐慌状态。目标在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。",
        "params": "1/日"
      },
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "小恶魔变形为蝙蝠（速度10尺，飞行40尺）、蜈蚣（40尺，攀爬40尺）、蟾蜍（40尺，游泳40尺）的形态，或变回其真实形态。除速度外，其各形态下游戏数据均相同。小恶魔着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "邪魔\\恶魔\\小恶魔.htm"
  },
  {
    "name": "巨牛魔",
    "en_name": "Goristro",
    "type_line": "巨型邪魔（恶魔），混乱邪恶",
    "size": "Huge",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 19,
    "initiative_bonus": 6,
    "initiative_total": 16,
    "hp": 310,
    "hp_formula": "23d12+161",
    "speed": {
      "walk": "50尺"
    },
    "abilities": {
      "力量": {
        "score": 25,
        "mod": 7,
        "save": 13
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 6
      },
      "体质": {
        "score": 25,
        "mod": 7,
        "save": 13
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 7
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 7,
      "求生": 7
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 17
    },
    "languages": "深渊语",
    "cr": 17,
    "xp": 18000,
    "pb": 6,
    "traits": [
      {
        "name": "恶魔复苏",
        "en_name": "Demonic Restoration",
        "description": "若巨牛魔于无底深渊之外死去，其身躯会化为灰烬，并立即在无底深渊某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "巨牛魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "攻城巨兽",
        "en_name": "Siege Monster",
        "description": "巨牛魔对物件和建筑造成双倍伤害。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "巨牛魔发动一次凶蛮犄角攻击和两次猛击。"
      },
      {
        "name": "凶蛮犄角",
        "en_name": "Brutal Gore",
        "description": "近战攻击检定：+13，触及10尺。命中：40（6d10+7）穿刺伤害。若目标生物体型不超过巨型，其被直线推离至多20尺并陷入倒地状态。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+13，触及10尺。命中：29（4d10+7）钝击伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "冲锋",
        "en_name": "Charge",
        "description": "巨牛魔向一名其可见的敌人直线移动至多等于其速度一半的距离。"
      }
    ],
    "source_file": "邪魔\\恶魔\\巨牛魔.htm"
  },
  {
    "name": "幽影恶魔",
    "en_name": "Shadow Demon",
    "type_line": "中型邪魔（恶魔），混乱邪恶",
    "size": "Medium",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 14,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 66,
    "hp_formula": "12d8+12",
    "speed": {
      "walk": "30尺，飞行30尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 5
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 4
      }
    },
    "skills": {
      "隐匿": 7
    },
    "damage_vulnerabilities": [
      "光耀"
    ],
    "damage_resistances": [
      "强酸",
      "钝击",
      "寒冷",
      "火焰",
      "闪电",
      "穿刺",
      "挥砍",
      "雷鸣"
    ],
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "受擒",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 11
    },
    "languages": "深渊语，心灵感应120尺。",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "traits": [
      {
        "name": "恶魔复苏",
        "en_name": "Demonic Restoration",
        "description": "若恶魔于无底深渊之外死去，其身躯会化为灰烬，并立即在无底深渊某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "虚体移动",
        "en_name": "Incorporeal Movement",
        "description": "恶魔可以移动穿过其他生物或物件，如同穿过困难地形一般。在其回合结束时，若恶魔还处于物件内，其受到5（1d10）力场伤害"
      },
      {
        "name": "光照敏感light",
        "en_name": "Sensitivity",
        "description": "若恶魔身处明亮光照，其属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "暗影之爪",
        "en_name": "Umbral Claw",
        "description": "近战攻击检定：+5，触及5尺。命中：16（3d8+3）心灵伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "幽影隐匿",
        "en_name": "Shadow Stealth",
        "description": "若恶魔身处微光光照或黑暗中，其执行躲藏动作。"
      }
    ],
    "source_file": "邪魔\\恶魔\\幽影恶魔.htm"
  },
  {
    "name": "恶猿魔",
    "en_name": "Barlgura",
    "type_line": "大型邪魔（恶魔），混乱邪恶",
    "size": "Large",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 85,
    "hp_formula": "10d10+30",
    "speed": {
      "walk": "40尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 5
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 5,
      "隐匿": 5
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 15
    },
    "languages": "深渊语，心灵感应120尺。",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "恶魔复苏",
        "en_name": "Demonic Restoration",
        "description": "若恶猿魔于无底深渊之外死去，其身躯会化为灰烬，并立即在无底深渊某处获得一具新的身体，以满生命值复活。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "恶猿魔发动一次折磨之咬攻击与两次猛砸攻击。"
      },
      {
        "name": "折磨之咬",
        "en_name": "Tormenting Bite",
        "description": "近战攻击检定：+7，触及5尺。命中：11（2d6+4）穿刺伤害外加13（2d12）心灵伤害。"
      },
      {
        "name": "猛砸",
        "en_name": "Thrash",
        "description": "近战攻击检定：+7，触及5尺。命中：9（1d10+4）钝击伤害。若目标生物体型不超过大型，则其陷入倒地状态。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "恶猿魔施展以下以下法术中，无需材料成分并使用感知作为施法属性（法术豁免DC13）："
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "易容术Disguise Self，隐形术Invisiblity（仅自身）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "纠缠术Entangle，魅影杀手Phantasmal Killer（六环版本）"
      }
    ],
    "bonus_actions": [
      {
        "name": "跳跃",
        "en_name": "Leap",
        "description": "恶猿魔消耗10尺移动力跳跃至多40尺。"
      }
    ],
    "source_file": "邪魔\\恶魔\\恶猿魔.htm"
  },
  {
    "name": "炎魔",
    "en_name": "Balor",
    "type_line": "巨型邪魔（恶魔），混乱邪恶",
    "size": "Huge",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 19,
    "initiative_bonus": 14,
    "initiative_total": 24,
    "hp": 287,
    "hp_formula": "23d12+138",
    "speed": {
      "walk": "40尺，飞行80尺"
    },
    "abilities": {
      "力量": {
        "score": 26,
        "mod": 8,
        "save": 8
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 22,
        "mod": 6,
        "save": 12
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 9
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 9
      },
      "魅力": {
        "score": 22,
        "mod": 6,
        "save": 6
      }
    },
    "skills": {
      "察觉": 9
    },
    "damage_resistances": [
      "寒冷",
      "闪电"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "恐慌",
      "中毒"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 19
    },
    "languages": "深渊语；心灵感应120尺",
    "cr": 19,
    "xp": 22000,
    "pb": 6,
    "traits": [
      {
        "name": "焚身爆",
        "en_name": "Death Throes",
        "description": "炎魔在死亡时爆炸。敏捷豁免：DC20，源自炎魔的30尺光环区域内的每名生物。失败：31（9d6）火焰伤害外加31（9d6）力场伤害。成功：半伤。失败或成功：若炎魔于无底深渊之外死去，其立即在无底深渊某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "火焰灵光",
        "en_name": "Fire Aura",
        "description": "炎魔回合结束时位于源自炎魔5尺光环区域内的每名生物受到13（3d8）火焰伤害。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary \nResistance",
        "description": "炎魔豁免失败时，可以将其改为豁免成功。",
        "params": "3/日"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic \nResistance",
        "description": "炎魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "炎魔发动一次火舌长鞭攻击与一次闪电剑攻击。"
      },
      {
        "name": "火舌长鞭",
        "en_name": "Flame Whip",
        "description": "近战攻击检定：+14，触及30尺。命中：18（3d6+8）力场伤害外加17（5d6）火焰伤害。若目标生物体型不超过巨型，炎魔将目标直线拉近至多25尺，且目标陷入倒地状态。"
      },
      {
        "name": "闪电剑",
        "en_name": "Lightning Blade",
        "description": "近战攻击检定：+14，触及10尺。命中：21（3d8+8）力场伤害外加22（4d10）闪电伤害，且目标无法执行反应直至炎魔的下个回合开始。"
      }
    ],
    "bonus_actions": [
      {
        "name": "传送",
        "en_name": "Teleport",
        "description": "炎魔将其自身或位于其10尺内的一名自愿恶魔传送至多60尺至一处炎魔可见的未占据空间。"
      }
    ],
    "source_file": "邪魔\\恶魔\\炎魔.htm"
  },
  {
    "name": "狂蟾魔",
    "en_name": "Hezrou",
    "type_line": "大型邪魔（恶魔），混乱邪恶",
    "size": "Large",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 18,
    "initiative_bonus": 6,
    "initiative_total": 16,
    "hp": 157,
    "hp_formula": "15d10+75",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 7
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 8
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 4
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 11
    },
    "languages": "深渊语，心灵感应120尺。",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "traits": [
      {
        "name": "恶魔复苏",
        "en_name": "Demonic Restoration",
        "description": "若狂蟾魔于无底深渊之外死去，其身躯会化为灰烬，并立即在无底深渊某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "狂蟾魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "恶臭stench",
        "en_name": "",
        "description": "体质豁免：DC16，任何在源自狂蟾魔的10尺光环区域内开始其回合的生物。失败：目标陷入中毒状态，持续至下个回合开始。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "狂蟾魔发动三次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+7，触及5尺。命中：6（1d4+4）挥砍伤害外加9（2d8）毒素伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "跳跃",
        "en_name": "Leap",
        "description": "狂蟾魔消耗10尺移动力跳跃至多30尺。"
      }
    ],
    "source_file": "邪魔\\恶魔\\狂蟾魔.htm"
  },
  {
    "name": "蜡融妖",
    "en_name": "Yochlol",
    "type_line": "中型邪魔（恶魔），混乱邪恶",
    "size": "Medium",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 15,
    "initiative_bonus": 8,
    "initiative_total": 18,
    "hp": 153,
    "hp_formula": "18d8+72",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 19,
        "mod": 4,
        "save": 8
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 5
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 6
      },
      "魅力": {
        "score": 17,
        "mod": 3,
        "save": 7
      }
    },
    "skills": {
      "欺瞒": 11,
      "洞悉": 6
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 12
    },
    "languages": "深渊语，精灵语，地底通用语",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "traits": [
      {
        "name": "恶魔复苏",
        "en_name": "Demonic Restoration",
        "description": "若蜡融妖于无底深渊之外死去，其身躯会化为灰烬，并立即在无底深渊某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "蜡融妖对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "蛛行",
        "en_name": "Spider Climb",
        "description": "蜡融妖可以在难以攀爬的表面上攀爬，包括沿着天花板移动，且无需为此进行属性检定。"
      },
      {
        "name": "蛛网行者",
        "en_name": "Web Walker",
        "description": "蜡融妖在蛛网上移动时无视蛛网造成的移动限制。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蜡融妖发动两次苛性鞭笞攻击，并使用施法施展蛛网术Web或支配类人Dominate \nPerson（若条件允许）。"
      },
      {
        "name": "苛性鞭笞",
        "en_name": "Caustic Lash",
        "description": "近战或远程攻击检定：+8，触及10尺或射程120尺。命中：25（6d6+4）强酸伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "蜡融妖施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测思想Detect Thoughts， 气化形体Gaseous Form（仅自身），  蛛网术Web"
      },
      {
        "name": "1/日：",
        "en_name": "",
        "description": "支配类人Dominate Person"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "蜡融妖变形为中型类人生物或中型蜘蛛，或变回其真实形态。其各形态下游戏数据均相同，且其着装或携带的任何装备都不会随之变化。"
      }
    ],
    "reactions": [
      {
        "name": "毒性逃脱",
        "en_name": "Toxi Escape",
        "description": "触发：蜡融妖被一次攻击检定命中。响应：蜡融妖令此次攻击对其造成的伤害减半（向下取整），并传送至30尺内一处其可见的未占据空间。体质豁免：DC15，蜡融妖目标空间5尺内的每名生物。失败：目标陷入中毒状态，持续至其下个回合结束。中毒期间，目标陷入失能状态。"
      }
    ],
    "source_file": "邪魔\\恶魔\\蜡融妖.htm"
  },
  {
    "name": "迷诱魔",
    "en_name": "Glabrezu",
    "type_line": "大型邪魔（恶魔），混乱邪恶",
    "size": "Large",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 17,
    "initiative_bonus": 6,
    "initiative_total": 16,
    "hp": 189,
    "hp_formula": "18d10+90",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 9
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 21,
        "mod": 5,
        "save": 9
      },
      "智力": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 17,
        "mod": 3,
        "save": 7
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 7
      }
    },
    "skills": {
      "欺瞒": 7,
      "察觉": 7
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 17
    },
    "languages": "深渊语，心灵感应120尺。",
    "cr": 9,
    "xp": 5000,
    "pb": 4,
    "traits": [
      {
        "name": "恶魔复苏",
        "en_name": "Demonic Restoration",
        "description": "若迷诱魔于无底深渊之外死去，其身躯会化为灰烬，并立即在无底深渊某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "迷诱魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "迷诱魔发动两次巨钳攻击，并使用猛砸或施法。"
      },
      {
        "name": "巨钳",
        "en_name": "Pincer",
        "description": "近战攻击检定：+9，触及10尺。命中：16（2d10+5）挥砍伤害。若目标生物体型不超过中型，则其将被双钳之一擒抱，陷入受擒状态（逃脱DC15）。"
      },
      {
        "name": "猛砸",
        "en_name": "Pummel",
        "description": "敏捷豁免：DC17，单一正受擒于迷诱魔的生物。失败：15（3d6+5）钝击伤害。成功：半伤。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "迷诱魔施展以下一道法术，无需材料成分并使用智力作为施法属性（法术豁免DC16）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "黑暗术Darkness，侦测魔法Detect Magic，解除魔法Dispel Magic"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "困惑术Confusion，飞行术Fly，律令震慑Power Word Stun"
      }
    ],
    "source_file": "邪魔\\恶魔\\迷诱魔.htm"
  },
  {
    "name": "鹫魔",
    "en_name": "Vrock",
    "type_line": "大型邪魔（恶魔），混乱邪恶",
    "size": "Large",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 152,
    "hp_formula": "16d10+64",
    "speed": {
      "walk": "40尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 5
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 4
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": 2
      }
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 11
    },
    "languages": "深渊语，心灵感应120尺。",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "traits": [
      {
        "name": "恶魔复苏",
        "en_name": "Demonic Restoration",
        "description": "若鹫魔于无底深渊之外死去，其身躯会化为灰烬，并立即在无底深渊某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "鹫魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鹫魔发动两次撕扯攻击。"
      },
      {
        "name": "撕扯",
        "en_name": "Shred",
        "description": "近战攻击检定：+6，触及5尺。命中：10（2d6+3）穿刺伤害外加10（3d6）毒素伤害。"
      },
      {
        "name": "孢子",
        "en_name": "Spores",
        "description": "体质豁免：DC15，源自鹫魔的20尺光环区域内的每名生物。失败：目标陷入中毒状态，并在其回合结束重复豁免，成功则终止其身上的该效应。中毒期间，目标在其回合开始时受到5（1d10）毒素伤害。向目标泼洒一瓶圣水将提前终止该效应。",
        "params": "充能6"
      },
      {
        "name": "震慑尖啸",
        "en_name": "Stunning Screech",
        "description": "体质豁免：DC15，源自鹫魔的20尺光环区域内的每名生物（此豁免恶魔成功）。失败：10（3d6）雷鸣伤害，且目标陷入震慑状态，直至鹫魔的下个回合结束。",
        "params": "1/日"
      }
    ],
    "source_file": "邪魔\\恶魔\\鹫魔.htm"
  },
  {
    "name": "鬣狗人头目",
    "en_name": "Gnoll Pack Lord",
    "type_line": "中型邪魔，混乱邪恶",
    "size": "Medium",
    "creature_type": "邪魔",
    "alignment": "混乱邪恶",
    "ac": 15,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 49,
    "hp_formula": "9d8+9",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "鬣狗人语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鬣狗人使用骸骨长鞭或骸骨标枪发动共计两次攻击，并使用煽动横行（若条件允许）。"
      },
      {
        "name": "骸骨长鞭",
        "en_name": "Bone Whip",
        "description": "近战攻击检定：+5，触及10尺。命中：8（2d4+3）挥砍伤害。"
      },
      {
        "name": "骸骨标枪",
        "en_name": "Bone Javelin",
        "description": "远程攻击检定：+5，射程30/120尺。命中：7（1d8+3）穿刺伤害。"
      },
      {
        "name": "煽动横行",
        "en_name": "Incite Rampage",
        "description": "鬣狗人指定其60尺内其可见的另一名拥有横行附赠动作的生物。目标能够以反应发动一次近战攻击。",
        "params": "充能5~6"
      }
    ],
    "bonus_actions": [
      {
        "name": "横行",
        "en_name": "Rampage",
        "description": "鬣狗人对一名已浴血的生物造成伤害后，立即移动至多等于其速度一半的距离，并发动一次骨鞭攻击。",
        "params": "2/日"
      }
    ],
    "source_file": "邪魔\\鬣狗人\\鬣狗人头目.htm"
  },
  {
    "name": "鬣狗人武者",
    "en_name": "Gnoll Warrior",
    "type_line": "中型邪魔，混乱邪恶",
    "size": "Medium",
    "creature_type": "邪魔",
    "alignment": "混乱邪恶",
    "ac": 15,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 27,
    "hp_formula": "6d8",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "鬣狗人语",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "actions": [
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）穿刺伤害。"
      },
      {
        "name": "骸骨弓",
        "en_name": "Bone Bow",
        "description": "远程攻击检定：+3，射程150/600尺。命中：6（1d10+1）穿刺伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "横行",
        "en_name": "Rampage",
        "description": "鬣狗人对一名已浴血的生物造成伤害后，立即移动至多等于其速度一半的距离，并发动一次撕裂攻击。",
        "params": "1/日"
      }
    ],
    "source_file": "邪魔\\鬣狗人\\鬣狗人武者.htm"
  },
  {
    "name": "鬣狗人耶诺古之牙",
    "en_name": "Gnoll Fang of Yeenoghu",
    "type_line": "中型邪魔，混乱邪恶",
    "size": "Medium",
    "creature_type": "邪魔",
    "alignment": "混乱邪恶",
    "ac": 14,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 71,
    "hp_formula": "11d8+22",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 4
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 3
      }
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "深渊语，鬣狗人语",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鬣狗人进行一次啃咬攻击和两次骸骨链枷攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：6（1d6+3）穿刺伤害，外加7（2d6）毒素伤害，且目标陷入中毒状态，直至鬣狗人的下个回合开始。"
      },
      {
        "name": "骸骨链枷",
        "en_name": "Bone Flail",
        "description": "近战攻击检定：+5，触及10尺。命中：7（1d8+3）穿刺伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "横行",
        "en_name": "Rampage",
        "description": "鬣狗人对一名已浴血的生物造成伤害后，立即移动至多等于其速度一半的距离，并发动一次啃咬攻击。",
        "params": "2/日"
      }
    ],
    "source_file": "邪魔\\鬣狗人\\鬣狗人耶诺古之牙.htm"
  },
  {
    "name": "鬣狗人魔头",
    "en_name": "Gnoll Demoniac",
    "type_line": "中型邪魔，混乱邪恶",
    "size": "Medium",
    "creature_type": "邪魔",
    "alignment": "混乱邪恶",
    "ac": 16,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 135,
    "hp_formula": "18d8+54",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 6
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 5
      },
      "魅力": {
        "score": 17,
        "mod": 3,
        "save": 6
      }
    },
    "skills": {
      "察觉": 5
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 15
    },
    "languages": "深渊语，通用语，鬣狗人语",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鬣狗人发动两次深渊打击攻击。"
      },
      {
        "name": "深渊打击",
        "en_name": "Abyssal Strike",
        "description": "近战或远程攻击检定：+6，触及5尺或射程60尺。命中：20（5d6+3）毒素伤害。"
      },
      {
        "name": "耶诺古之欲",
        "en_name": "Hunger of Yeenoghu",
        "description": "鬣狗人以60尺内其可见的一点为源点，30尺立方区域内咒唤魔法黑暗，持续1分钟或在鬣狗人专注终止时提前结束。该区域为困难地形。敏捷豁免检定：DC14，在某个回合中首次进入该区域或是在其中开始回合的每名生物。失败：28（8d6）暗蚀伤害，且鬣狗人或一名由其选择且其可见的生物获得10临时生命值。成功：仅半伤。",
        "params": "充能5~6"
      }
    ],
    "bonus_actions": [
      {
        "name": "横行",
        "en_name": "Rampage",
        "description": "鬣狗人对一名已浴血的生物造成伤害后，立即移动至多等于其速度一半的距离，并发动一次深渊打击攻击。",
        "params": "2/日"
      }
    ],
    "source_file": "邪魔\\鬣狗人\\鬣狗人魔头.htm"
  },
  {
    "name": "冰魔",
    "en_name": "Ice Devil",
    "type_line": "大型邪魔（魔鬼），守序邪恶",
    "size": "Large",
    "creature_type": "邪魔（魔鬼）",
    "alignment": "守序邪恶",
    "ac": 18,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 228,
    "hp_formula": "24d10+96",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 7
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 9
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 7
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 9
      }
    },
    "skills": {
      "洞悉": 7,
      "察觉": 7,
      "游说": 9
    },
    "damage_immunities": [
      "寒冷",
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "盲视": 120,
      "被动察觉": 17
    },
    "languages": "炼狱语，心灵感应120尺",
    "cr": 14,
    "xp": 11500,
    "pb": 5,
    "traits": [
      {
        "name": "魔鬼复苏",
        "en_name": "Diabolical Restoration",
        "description": "若冰魔于九层地狱之外死去，其身躯会化为硫磺烟雾消失，并立即在九层地狱某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "冰魔在对抗法术和其他魔法效应的豁免中具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "冰魔发动三次冰矛攻击。其可以将其中一次攻击替换为一次尾击攻击。"
      },
      {
        "name": "冰矛",
        "en_name": "Ice Spear",
        "description": "近战或远程攻击检定：+10，触及5尺或射程30/120尺。命中：14（2d8+5）穿刺伤害外加10（3d6）寒冷伤害。直至目标的下个回合结束，其无法执行附赠动作或反应，其速度降低10尺，且目标在其回合中仅可以执行一个动作或移动，但不能同时执行二者。\n命中或失手：冰矛在远程攻击后立即魔法性地回到冰魔手中。"
      },
      {
        "name": "尾击",
        "en_name": "Tail",
        "description": "近战攻击检定：+10，触及10尺。命中：15（3d6+5）钝击伤害外加18（4d8）寒冷伤害。"
      },
      {
        "name": "冰墙",
        "en_name": "Ice Wall",
        "description": "冰魔施展冰墙术Ice \nWall（八环版本），无需法术成分并使用智力作为施法属性（法术豁免DC17）。",
        "params": "充能6"
      }
    ],
    "source_file": "邪魔\\魔鬼\\冰魔.htm"
  },
  {
    "name": "小魔鬼",
    "en_name": "Imp",
    "type_line": "微型邪魔（魔鬼），守序邪恶",
    "size": "Tiny",
    "creature_type": "邪魔（魔鬼）",
    "alignment": "守序邪恶",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 21,
    "hp_formula": "6d4+6",
    "speed": {
      "walk": "20尺，飞行40尺"
    },
    "abilities": {
      "力量": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "欺瞒": 4,
      "洞悉": 3,
      "隐匿": 5
    },
    "damage_resistances": [
      "寒冷"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 11
    },
    "languages": "通用语，炼狱语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "小魔鬼对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "钉刺",
        "en_name": "Sting",
        "description": "近战攻击检定：+5，触及5尺。命中：6（1d6+3）穿刺伤害外加7（2d6）毒素伤害。"
      },
      {
        "name": "隐形术",
        "en_name": "Invisibility",
        "description": "小魔鬼对自身施展隐形术Invisibility，无需法术成分并使用魅力作为施法属性。"
      },
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "小魔鬼变形为老鼠（速度20尺）、渡鸦（速度20尺，飞行速度60尺）、蜘蛛（速度20尺，攀爬速度20尺），或变回其真实形态。除速度外，其各形态下游戏数据均相同。小魔鬼着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "邪魔\\魔鬼\\小魔鬼.htm"
  },
  {
    "name": "棘魔",
    "en_name": "Spined Devil",
    "type_line": "小型邪魔（魔鬼），守序邪恶",
    "size": "Small",
    "creature_type": "邪魔（魔鬼）",
    "alignment": "守序邪恶",
    "ac": 13,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 45,
    "hp_formula": "10d6+10",
    "speed": {
      "walk": "20尺，飞行40尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "damage_resistances": [
      "寒冷"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 12
    },
    "languages": "炼狱语，心灵感应120尺",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "飞掠",
        "en_name": "Flyby",
        "description": "棘魔飞行离开敌人的触及范围时不会引发借机攻击。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "棘魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "棘魔使用地狱叉刺或尾刺发动共计两次攻击。"
      },
      {
        "name": "灼热叉刺",
        "en_name": "Searing Folk",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）穿刺伤害外加3（1d6）火焰伤害。"
      },
      {
        "name": "地狱尾刺",
        "en_name": "Tail Spine",
        "description": "远程攻击检定：+4，射程20/80尺。命中：4（1d4+2）穿刺伤害外加3（1d6）火焰伤害。"
      }
    ],
    "source_file": "邪魔\\魔鬼\\棘魔.htm"
  },
  {
    "name": "深狱炼魔",
    "en_name": "Pit Fiend",
    "type_line": "大型邪魔（魔鬼），守序邪恶",
    "size": "Large",
    "creature_type": "邪魔（魔鬼）",
    "alignment": "守序邪恶",
    "ac": 21,
    "initiative_bonus": 14,
    "initiative_total": 24,
    "hp": 337,
    "hp_formula": "27d10+189",
    "speed": {
      "walk": "30尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 26,
        "mod": 8,
        "save": 8
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 8
      },
      "体质": {
        "score": 24,
        "mod": 7,
        "save": 7
      },
      "智力": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "感知": {
        "score": 18,
        "mod": 4,
        "save": 10
      },
      "魅力": {
        "score": 24,
        "mod": 7,
        "save": 7
      }
    },
    "skills": {
      "察觉": 10,
      "游说": 19
    },
    "damage_resistances": [
      "寒冷"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 20
    },
    "languages": "炼狱语，心灵感应120尺",
    "cr": 20,
    "xp": 25000,
    "pb": 6,
    "traits": [
      {
        "name": "魔鬼复苏",
        "en_name": "Diabolical Restoration",
        "description": "若深狱炼魔于九层地狱之外死去，其身躯会化为硫磺烟雾消失，并立即在九层地狱某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "恐惧灵光",
        "en_name": "Fear Aura",
        "description": "只要未陷入失能状态，深狱炼魔在20尺光环区域内散发灵光。感知豁免检定：DC21，在光环区域内开始其回合的任意敌人。失败：目标陷入恐慌状态直至其下个回合开始。成功：目标在24小时内免疫此深狱炼魔的恐惧灵光。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "深狱炼魔豁免失败时，可以将其改为豁免成功。",
        "params": "4/日"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "深狱炼魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "深狱炼魔发动一次啃咬攻击，两次魔鬼之爪攻击以及一次烈焰重锤攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+14，触及10尺。命中：18（3d6+8）穿刺伤害。若目标为生物，则其必须进行以下豁免：体质豁免检定：DC21。失败：目标陷入中毒状态。中毒期间，目标无法恢复生命值，且在其回合开始时受到21（6d6）毒素伤害。陷入中毒的目标在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。"
      },
      {
        "name": "魔鬼之爪",
        "en_name": "Devilish Claw",
        "description": "近战攻击检定：+14，触及10尺。命中：26（4d8+8）暗蚀伤害。"
      },
      {
        "name": "烈焰重锤",
        "en_name": "Fiery Mace",
        "description": "近战攻击检定：+14，触及10尺。命中：22（3d8+8）力场伤害外加21（6d6）火焰伤害。"
      },
      {
        "name": "狱火施法",
        "en_name": "Hellfire Spellcasting",
        "description": "深狱炼魔施展两次火球术Fireball（五环版本），无需材料成分并使用魅力作为施法属性（法术豁免DC21）。其可以将其中一次火球术替换为定身怪物Hold \nMonster（七环版本）或火墙术Wall of Fire。",
        "params": "充能4~6"
      }
    ],
    "source_file": "邪魔\\魔鬼\\深狱炼魔.htm"
  },
  {
    "name": "猬魔",
    "en_name": "Barbed Devil",
    "type_line": "中型邪魔（魔鬼），守序邪恶",
    "size": "Medium",
    "creature_type": "邪魔（魔鬼）",
    "alignment": "守序邪恶",
    "ac": 15,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 110,
    "hp_formula": "13d8+52",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 5
      }
    },
    "skills": {
      "欺瞒": 5,
      "洞悉": 5,
      "察觉": 8
    },
    "damage_resistances": [
      "寒冷"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 18
    },
    "languages": "炼狱语，心灵感应120尺",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "猬皮",
        "en_name": "Barbed Hide",
        "description": "在猬魔的回合开始时，其对擒抱自己的生物或被其擒抱的生物造成5（1d10）穿刺伤害。"
      },
      {
        "name": "魔鬼复苏",
        "en_name": "Diabolical Restoration",
        "description": "若猬魔于九层地狱之外死去，其身躯会化为硫磺烟雾消失，并立即在九层地狱某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "猬魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "猬魔发动一次爪击攻击和一次尾击攻击，或者发动两次投掷烈焰攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claws",
        "description": "近战攻击检定：+6，触及5尺。命中：10（2d6+3）穿刺伤害，如果目标生物体型不超过大型，则其被双爪擒抱，陷入受擒状态（逃脱DC13）。"
      },
      {
        "name": "尾击",
        "en_name": "Tail",
        "description": "近战攻击检定：+6，触及10尺。命中：14（2d10+3）挥砍伤害。"
      },
      {
        "name": "投掷烈焰",
        "en_name": "Hurl Flame",
        "description": "远程攻击检定：+6，射程150尺。命中：17（5d6）火焰伤害，若目标为未被着装或携带的可燃物件，则目标开始燃烧。"
      }
    ],
    "source_file": "邪魔\\魔鬼\\猬魔.htm"
  },
  {
    "name": "罪魔",
    "en_name": "Erinyes",
    "type_line": "中型邪魔（魔鬼），守序邪恶",
    "size": "Medium",
    "creature_type": "邪魔（魔鬼）",
    "alignment": "守序邪恶",
    "ac": 18,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 178,
    "hp_formula": "21d8+84",
    "speed": {
      "walk": "30尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 8
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 8
      }
    },
    "skills": {
      "察觉": 6,
      "游说": 8
    },
    "damage_resistances": [
      "寒冷"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 16
    },
    "languages": "炼狱语，心灵感应120尺",
    "cr": 12,
    "xp": 8400,
    "pb": 4,
    "traits": [
      {
        "name": "魔鬼复苏",
        "en_name": "Diabolical Restoration",
        "description": "若罪魔于九层地狱之外死去，其身躯会化为硫磺烟雾消失，并立即在九层地狱某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "罪魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "魔法绳索",
        "en_name": "Magic Rope",
        "description": "罪魔持有一根魔法绳索。只要携带魔绳，罪魔就能够使用其纠缠绳动作。魔绳具有AC20，HP90，免疫毒素和心灵伤害。若魔绳生命值降至0、罪魔死亡或魔绳离开罪魔身边5+尺超过1小时，魔绳化为尘埃。若魔绳受到伤害或被摧毁，罪魔可以在完成一次短休或长休时将其完全恢复。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "罪魔发动三次凋零之刃攻击并使用纠缠绳。"
      },
      {
        "name": "凋零之刃",
        "en_name": "Withering Sword",
        "description": "近战攻击检定：+8，触及5尺。命中：13（2d8+4）挥砍伤害外加11（2d10）暗蚀伤害。"
      },
      {
        "name": "纠缠绳",
        "en_name": "Entangling Rope",
        "description": "力量豁免检定：DC16，单一120尺内罪魔可见的生物。失败：14（4d6）力场伤害，且目标陷入束缚状态，持续直至绳索被摧毁、罪魔使用附赠动作释放该生物，或罪魔再次使用纠缠绳动作。"
      }
    ],
    "reactions": [
      {
        "name": "格挡",
        "en_name": "Parry",
        "description": "触发：罪魔在持握武器期间因近战攻击检定被命中。响应：罪魔令其对抗那次攻击的AC+4，可能令那次攻击改为失手。"
      }
    ],
    "source_file": "邪魔\\魔鬼\\罪魔.htm"
  },
  {
    "name": "角魔",
    "en_name": "Horned Devil",
    "type_line": "大型邪魔（魔鬼），守序邪恶",
    "size": "Large",
    "creature_type": "邪魔（魔鬼）",
    "alignment": "守序邪恶",
    "ac": 18,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 199,
    "hp_formula": "19d10+95",
    "speed": {
      "walk": "30尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 22,
        "mod": 6,
        "save": 10
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 7
      },
      "体质": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 8
      }
    },
    "damage_resistances": [
      "寒冷"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 150,
      "被动察觉": 13
    },
    "languages": "炼狱语，心灵感应120尺",
    "cr": 11,
    "xp": 7200,
    "pb": 4,
    "traits": [
      {
        "name": "魔鬼复苏",
        "en_name": "Diabolical Restoration",
        "description": "若角魔于九层地狱之外死去，其身躯会化为硫磺烟雾消失，并立即在九层地狱某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "角魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "角魔使用灼热叉刺和投掷烈焰发动共计三次攻击。其可以将其中一次攻击替换为使用地狱尾击。"
      },
      {
        "name": "灼热叉刺",
        "en_name": "Searing Folk",
        "description": "近战攻击检定：+10，触及10尺。命中：15（2d8+6）穿刺伤害外加9（2d8）火焰伤害。"
      },
      {
        "name": "投掷烈焰",
        "en_name": "Hurl Flame",
        "description": "远程攻击检定：+8，射程150尺。命中：26（5d8+4）火焰伤害，若目标为未被着装或携带的可燃物件，则目标开始燃烧。"
      },
      {
        "name": "地狱尾击",
        "en_name": "Inferno Tail",
        "description": "敏捷豁免检定：DC17，单一10尺内角魔可见的生物。失败：10（1d8+6）暗蚀伤害，若目标未获得地狱创口，其获得地狱创口。具有地狱创口期间，目标在其回合开始时失去10（3d6）生命值。地狱创口在1分钟后合拢或在目标被法术恢复后提前合拢。目标或其5尺内的生物可以用动作来尝试缝合创口，这么做需要成功通过一次DC17的感知（医药）检定。"
      }
    ],
    "source_file": "邪魔\\魔鬼\\角魔.htm"
  },
  {
    "name": "链魔",
    "en_name": "Chain Devil",
    "type_line": "中型邪魔（魔鬼），守序邪恶",
    "size": "Medium",
    "creature_type": "邪魔（魔鬼）",
    "alignment": "守序邪恶",
    "ac": 15,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 85,
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 4
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "damage_resistances": [
      "钝击",
      "寒冷",
      "挥砍",
      "穿刺"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 11
    },
    "languages": "炼狱语，心灵感应120尺",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "traits": [
      {
        "name": "魔鬼复苏",
        "en_name": "Diabolical Restoration",
        "description": "若链魔于九层地狱之外死去，其身躯会化为硫磺烟雾消失，并立即在九层地狱某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "链魔在对抗法术和其他魔法效应的豁免中具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "链魔发动两次锁链攻击并使用咒唤地狱锁链。"
      },
      {
        "name": "锁链",
        "en_name": "Chain",
        "description": "近战攻击检定：+7，触及10尺。命中：11（2d6+4）挥砍伤害。若目标生物体型不超过大型，则其被两条锁链之一所擒抱，陷入受擒状态（逃脱DC14）。目标陷入束缚状态直至擒抱结束。"
      },
      {
        "name": "咒唤地狱锁链",
        "en_name": "Conjure Infernal Chain",
        "description": "链魔咒唤出一条炽热的锁链来捆缚某名生物。敏捷豁免检定：DC15，单一60尺内链魔可见的生物。失败：9（2d4+4）火焰伤害，且目标陷入束缚状态，直至链魔的下个回合开始，此时锁链消失。若目标生物体型不超过大型，链魔将其向自身方向直线移动至多30尺。成功：锁链直接消失。"
      }
    ],
    "reactions": [
      {
        "name": "可怖凝视",
        "en_name": "Unnerving Gaze",
        "description": "触发：一名链魔可见的生物在链魔30尺内开始其回合。响应-感知豁免检定：DC15，触发生物。失败：目标陷入恐慌状态，直至其回合结束。成功：目标在24小时内免疫此链魔的可怖凝视。"
      }
    ],
    "source_file": "邪魔\\魔鬼\\链魔.htm"
  },
  {
    "name": "须魔",
    "en_name": "Bearded Devil",
    "type_line": "中型邪魔（魔鬼），守序邪恶",
    "size": "Medium",
    "creature_type": "邪魔（魔鬼）",
    "alignment": "守序邪恶",
    "ac": 13,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 58,
    "hp_formula": "9d8+18",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 5
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 4
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 4
      }
    },
    "damage_resistances": [
      "寒冷"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "恐慌",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 10
    },
    "languages": "炼狱语，心灵感应120尺",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "须魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "须魔发动一次须刺攻击和一次长柄刀攻击。"
      },
      {
        "name": "须刺",
        "en_name": "Beard",
        "description": "近战攻击检定：+5，触及5尺。命中：7（1d8+3）穿刺伤害，且目标陷入中毒状态，直至须魔的下个回合开始。以此法中毒的生物在中毒期间无法恢复生命值。"
      },
      {
        "name": "地狱砍刀",
        "en_name": "Infernal Glaive",
        "description": "近战攻击检定：+5，触及10尺。命中：8（1d10+3）挥砍伤害。若目标是生物且其未获得地狱创口，承受以下效应。体质豁免检定：DC12。失败：目标获得地狱创口。具有地狱创口期间，目标在其回合开始时失去5（1d10）生命值。地狱创口在1分钟后合拢或在目标被法术恢复后提前合拢。目标或其5尺内的生物可以用动作来尝试缝合创口，这么做需要成功通过一次DC12的感知（医药）检定。"
      }
    ],
    "source_file": "邪魔\\魔鬼\\须魔.htm"
  },
  {
    "name": "骨魔",
    "en_name": "Bone Devil",
    "type_line": "大型邪魔（魔鬼），守序邪恶",
    "size": "Large",
    "creature_type": "邪魔（魔鬼）",
    "alignment": "守序邪恶",
    "ac": 16,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 161,
    "hp_formula": "17d10+68",
    "speed": {
      "walk": "40尺，飞行40尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 8
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 5
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 6
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 7
      }
    },
    "skills": {
      "欺瞒": 7,
      "洞悉": 6
    },
    "damage_resistances": [
      "寒冷"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 12
    },
    "languages": "炼狱语，心灵感应120尺",
    "cr": 9,
    "xp": 5000,
    "pb": 4,
    "traits": [
      {
        "name": "魔鬼复苏",
        "en_name": "Diabolical Restoration",
        "description": "若骨魔于九层地狱之外死去，其身躯会化为硫磺烟雾消失，并立即在九层地狱某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "骨魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "骨魔发动两次爪击攻击和一次地狱钉刺攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+8，触及10尺。命中：13（2d8+4）挥砍伤害。"
      },
      {
        "name": "地狱钉刺",
        "en_name": "Infernal Sting",
        "description": "近战攻击检定：+8，触及10尺。命中：15（2d10+4）穿刺伤害外加18（4d8）毒素伤害，且目标陷入中毒状态，直至骨魔的下个回合开始。中毒期间，目标无法恢复生命值。"
      }
    ],
    "source_file": "邪魔\\魔鬼\\骨魔.htm"
  },
  {
    "name": "鲨华武者",
    "en_name": "Sahuagin Warrior",
    "type_line": "中型邪魔，守序邪恶",
    "size": "Medium",
    "creature_type": "邪魔",
    "alignment": "守序邪恶",
    "ac": 12,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 22,
    "hp_formula": "4d8+4",
    "speed": {
      "walk": "30尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 5
    },
    "damage_resistances": [
      "强酸",
      "寒冷"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 15
    },
    "languages": "鲨华鱼人语",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "血腥狂怒",
        "en_name": "Blood Frenzy",
        "description": "鲨华鱼人对生命值未满的生物进行攻击检定时具有优势。"
      },
      {
        "name": "有限两栖",
        "en_name": "Limited Amphibiousness",
        "description": "鲨华鱼人可以在空气和水中呼吸，但必须至少每4小时浸入水中一次，以避免离开水后窒息。"
      },
      {
        "name": "鲨心感应",
        "en_name": "Shark Telepathy",
        "description": "鲨华鱼人能使用一种特殊的心灵感应，魔法性地控制其120尺内的鲨鱼。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鲨华鱼人发动两次爪击攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+3，触及5尺。命中：4（1d6+1）挥砍伤害"
      }
    ],
    "bonus_actions": [
      {
        "name": "水下冲锋",
        "en_name": "Aquatic Charge",
        "description": "鲨华鱼人向一名其可见的敌人直线游动至多等于其游泳速度的距离。"
      }
    ],
    "source_file": "邪魔\\鲨华鱼人\\鲨华武者.htm"
  },
  {
    "name": "鲨华男爵",
    "en_name": "Sahuagin Baron",
    "type_line": "大型邪魔，守序邪恶",
    "size": "Large",
    "creature_type": "邪魔",
    "alignment": "守序邪恶",
    "ac": 16,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 76,
    "hp_formula": "9d10+27",
    "speed": {
      "walk": "30尺，游泳50尺。"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 4
      },
      "魅力": {
        "score": 17,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "察觉": 7
    },
    "damage_resistances": [
      "强酸",
      "寒冷"
    ],
    "equipment": "胸甲Breastplate，三叉戟Trident",
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 17
    },
    "languages": "鲨华鱼人语",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "血腥狂怒",
        "en_name": "Blood Frenzy",
        "description": "鲨华鱼人对生命值未满的生物进行攻击检定时具有优势。"
      },
      {
        "name": "有限两栖",
        "en_name": "Limited Amphibiousness",
        "description": "鲨华鱼人可以在空气和水中呼吸，但必须至少每4小时浸入水中一次，以避免离开水后窒息。"
      },
      {
        "name": "鲨心感应",
        "en_name": "Shark Telepathy",
        "description": "鲨华鱼人能使用一种特殊的心灵感应，魔法性地控制其120尺内的鲨鱼。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鲨华鱼人发动三次三叉戟攻击。"
      },
      {
        "name": "三叉戟",
        "en_name": "Trident",
        "description": "近战或远程攻击检定：+7，触及5尺或射程20/60尺。命中：13（2d8+4）穿刺伤害。"
      }
    ],
    "reactions": [
      {
        "name": "邪魔之血",
        "en_name": "Fiendish Blood",
        "description": "触发：鲨华鱼人受到穿刺或挥砍伤害。响应：体质豁免检定：DC14，源自鲨华鱼人的5尺光环区域内由其选择的每名生物。失败：目标受到10（3d6）强酸伤害并被诅咒，持续至目标完成一次短休或长休。受诅咒期间，目标无法从隐形状态中获益，其速度降低10尺，且位于目标120尺内的所有邪魔都能感知其位置，无论是否存在障碍物。"
      }
    ],
    "source_file": "邪魔\\鲨华鱼人\\鲨华男爵.htm"
  },
  {
    "name": "鲨华祭司",
    "en_name": "Sahuagin Priest",
    "type_line": "中型邪魔，守序邪恶",
    "size": "Medium",
    "creature_type": "邪魔",
    "alignment": "守序邪恶",
    "ac": 12,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 38,
    "hp_formula": "7d8+7",
    "speed": {
      "walk": "30尺，游泳40尺。"
    },
    "abilities": {
      "力量": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "察觉": 6,
      "宗教": 3
    },
    "damage_resistances": [
      "强酸",
      "寒冷"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 16
    },
    "languages": "鲨华鱼人语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "血腥狂怒",
        "en_name": "Blood Frenzy",
        "description": "鲨华鱼人对生命值未满的生物进行攻击检定时具有优势。"
      },
      {
        "name": "有限两栖",
        "en_name": "Limited Amphibiousness",
        "description": "鲨华鱼人可以在空气和水中呼吸，但必须至少每4小时浸入水中一次，以避免离开水后窒息。"
      },
      {
        "name": "鲨心感应",
        "en_name": "Shark Telepathy",
        "description": "鲨华鱼人能使用一种特殊的心灵感应，魔法性地控制其120尺内的鲨鱼。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鲨华鱼人发动两次灵体鲨颚攻击。"
      },
      {
        "name": "灵体鲨颚",
        "en_name": "Spectral Jaws",
        "description": "近战或远程攻击检定：+4，触及5尺或射程120尺。命中：11（2d8 + 2）力场伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "鲨华鱼人施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC12）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "奇术Thaumaturgy"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "定身类人Hold Person，巧言术Tongues"
      }
    ],
    "bonus_actions": [
      {
        "name": "邪魔支援",
        "en_name": "Fiendish Aid",
        "description": "鲨华鱼人施展祝福术Bless或治愈真言Healing \nWord，使用与施法动作相同的施法属性。",
        "params": "2/天"
      }
    ],
    "source_file": "邪魔\\鲨华鱼人\\鲨华祭司.htm"
  },
  {
    "name": "劣魔",
    "en_name": "Lemure",
    "type_line": "中型邪魔（魔鬼），守序邪恶",
    "size": "Medium",
    "creature_type": "邪魔（魔鬼）",
    "alignment": "守序邪恶",
    "ac": 9,
    "initiative_bonus": -3,
    "initiative_total": 7,
    "hp": 9,
    "hp_formula": "2d8",
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 3,
        "mod": -4,
        "save": -4
      }
    },
    "damage_resistances": [
      "寒冷"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "恐慌",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 10
    },
    "languages": "理解炼狱语，但不会说",
    "cr": 0,
    "xp": 10,
    "pb": 2,
    "traits": [
      {
        "name": "地狱复苏",
        "en_name": "Hellish Restoration",
        "description": "若劣魔于九层地狱中死去，除非其是被一名处于祝福术Bless效应下的生物杀死或是其尸体被泼洒了圣水，否则其将在1d10天后以满生命值复活。"
      }
    ],
    "actions": [
      {
        "name": "肮脏软泥",
        "en_name": "Vile Slime",
        "description": "近战攻击检定：+2，触及5尺。命中：2（1d4）毒素伤害。"
      }
    ],
    "source_file": "邪魔\\魔鬼\\劣魔\\劣魔.htm"
  },
  {
    "name": "劣魔集群",
    "en_name": "Swarm of Lemures",
    "type_line": "中型邪魔的大型集群（魔鬼），守序邪恶",
    "size": "Medium",
    "creature_type": "邪魔的大型集群（魔鬼）",
    "alignment": "守序邪恶",
    "ac": 12,
    "initiative_bonus": -2,
    "initiative_total": 8,
    "hp": 45,
    "hp_formula": "6d10+12",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 3,
        "mod": -4,
        "save": -4
      }
    },
    "damage_resistances": [
      "钝击",
      "寒冷",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "恐慌",
      "受擒",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚",
      "震慑"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 11
    },
    "languages": "理解炼狱语，但不会说",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "地狱复苏",
        "en_name": "Hellish \nRestoration",
        "description": "若劣魔集群于九层地狱中死去，除非其是被一名处于祝福术Bless效应下的生物杀死或是其尸体被泼洒了圣水，否则其将在1d10天后以满生命值复活。"
      },
      {
        "name": "集群",
        "en_name": "Swarm",
        "description": "劣魔集群可以进驻另一生物身处的空间，反之亦然。而且劣魔集群可以通过任何足够一名中型生物通过的通道。劣魔集群不能恢复生命值也不能获得临时生命值 \n。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "劣魔集群发动两次肮脏软泥攻击。"
      },
      {
        "name": "肮脏软泥",
        "en_name": "Vile Slime",
        "description": "近战攻击检定：+4，触及5尺。命中：11（2d8+2）毒素伤害，若劣魔集群处于浴血则改为9（2d6+2）毒素伤害。"
      }
    ],
    "source_file": "邪魔\\魔鬼\\劣魔\\劣魔集群.htm"
  },
  {
    "name": "原魔",
    "en_name": "Manes",
    "type_line": "小型邪魔（恶魔），混乱邪恶",
    "size": "Small",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 9,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 9,
    "hp_formula": "2d6+2",
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 4,
        "mod": -3,
        "save": -3
      }
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "恐慌",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "理解深渊语，但不会说",
    "cr": "1/8",
    "xp": 25,
    "pb": 2,
    "actions": [
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+2，触及5尺。命中：5（2d4）挥砍伤害。"
      }
    ],
    "source_file": "邪魔\\恶魔\\原魔\\原魔.htm"
  },
  {
    "name": "原魔汽化体",
    "en_name": "Manes Vaporspawn",
    "type_line": "中型邪魔（恶魔），混乱邪恶",
    "size": "Medium",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 13,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 19,
    "hp_formula": "3d8+6",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 3,
        "mod": -4,
        "save": -4
      }
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "受擒",
      "中毒",
      "束缚"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "理解深渊语，但不会说",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "擅曲之物",
        "en_name": "Contortionist",
        "description": "原魔可以移动穿过最窄1寸宽的空间而无需消耗额外的移动力。"
      },
      {
        "name": "致病蒸汽",
        "en_name": "Sickening \nVapors",
        "description": "体质豁免：DC12，原魔回合结束时位于源自原魔的5尺光环内的每名生物。失败：目标陷入失能状态，持续至其下个回合结束。成功：目标在24小时内免疫此原魔的致病蒸汽。"
      }
    ],
    "actions": [
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）挥砍伤害外加5（2d4）暗蚀伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "幽影隐匿",
        "en_name": "Shadow Stealth",
        "description": "若原魔身处微光光照或黑暗中，其执行躲藏动作。"
      }
    ],
    "source_file": "邪魔\\恶魔\\原魔\\原魔汽化体.htm"
  },
  {
    "name": "怯魔",
    "en_name": "Dretch",
    "type_line": "小型邪魔（恶魔），混乱邪恶",
    "size": "Small",
    "creature_type": "邪魔（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 11,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 18,
    "hp_formula": "4d6+4",
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 3,
        "mod": -4,
        "save": -4
      }
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "闪电"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "深渊语；心灵感应60尺（只对理解深渊语的生物生效）",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "actions": [
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+3，触及5尺。命中：4（1d6+1）挥砍伤害。"
      },
      {
        "name": "污臭之云",
        "en_name": "Fetid Cloud",
        "description": "体质豁免：DC11，源自怯魔的10尺光环区域内的每名生物。失败：目标陷入中毒状态，持续至其下个回合结束。中毒期间，该生物在其回合中可以执行一个动作或一个附赠动作，但不能同时执行二者，且其无法执行反应。",
        "params": "1/日"
      }
    ],
    "source_file": "邪魔\\恶魔\\怯魔\\怯魔.htm"
  },
  {
    "name": "怯魔集群",
    "en_name": "Swarm of Dretch",
    "type_line": "小型邪魔的大型集群（恶魔），混乱邪恶",
    "size": "Small",
    "creature_type": "邪魔的大型集群（恶魔）",
    "alignment": "混乱邪恶",
    "ac": 12,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 45,
    "hp_formula": "6d10+12",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 3,
        "mod": -4,
        "save": -4
      }
    },
    "damage_resistances": [
      "钝击",
      "寒冷",
      "火焰",
      "闪电",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "恐慌",
      "受擒",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚",
      "震慑"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "深渊语；心灵感应60尺（只对理解深渊语的生物生效）",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "traits": [
      {
        "name": "污臭灵光",
        "en_name": "Fetid Aura",
        "description": "体质豁免：DC12，任何在源自怯魔集群的10尺光环区域内开始其回合的生物。失败：目标陷入中毒状态，持续至其下个回合开始。中毒期间，该该生物在其回合中可以执行一个动作或一个附赠动作，但不能同时执行二者，且其无法执行反应。"
      },
      {
        "name": "集群",
        "en_name": "Swarm",
        "description": "怯魔集群可以进驻另一生物身处的空间，反之亦然。而且集群可以通过任何足够一名小型生物通过的通道。怯魔集群不能恢复生命值也不能获得临时生命值 \n。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "怯魔集群发动两次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+4，触及5尺。命中：12（3d6+2）挥砍伤害，若怯魔集群处于浴血则改为9（3d4+2）挥砍伤害。"
      }
    ],
    "source_file": "邪魔\\恶魔\\怯魔\\怯魔集群.htm"
  },
  {
    "name": "匪帮欺诈师",
    "en_name": "Bandit Deceiver",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 16,
    "initiative_bonus": 6,
    "initiative_total": 16,
    "hp": 130,
    "hp_formula": "20d8+40",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 17,
        "mod": 3,
        "save": 6
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "特技": 6,
      "察觉": 4,
      "隐匿": 9
    },
    "equipment": "匕首（6），魔杖",
    "senses": {
      "被动察觉": 14
    },
    "languages": "通用语，盗贼黑话",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "匪帮欺诈师发动三次匕首攻击。"
      },
      {
        "name": "匕首",
        "en_name": "Dagger",
        "description": "近战或远程攻击检定：+6，触及5尺或射程20/60尺。命中：8（2d4+3）穿刺伤害外加10（3d6）毒素伤害"
      },
      {
        "name": "致盲闪",
        "en_name": "Blinding Flash",
        "description": "体质豁免检定：DC14，以120尺内匪帮欺诈师可见一点为中心，半径10尺的球状区域内的每名生物。失败：13（3d6+3）光耀伤害，且目标陷入目盲状态直至匪帮欺诈师的下个回合开始。成功：仅半伤。",
        "params": "充能4~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "匪帮欺诈师施展以下一道法术，使用智力作为施法属性（法术豁免DC14）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "易容术Disguise Self，法师之手Mage Hand，次级幻象Minor Illusion"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "定身类人Hold Person（四环版本），  法师护甲Mage Armor（已计入AC）， 高级幻影Major Image"
      }
    ],
    "source_file": "类人\\匪徒\\匪帮欺诈师.htm"
  },
  {
    "name": "匪帮祸首",
    "en_name": "Bandit Crime Lord",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 17,
    "initiative_bonus": 9,
    "initiative_total": 19,
    "hp": 169,
    "hp_formula": "26d8+52",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 20,
        "mod": 5,
        "save": 9
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 6
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "特技": 9,
      "察觉": 10,
      "隐匿": 13
    },
    "equipment": "手铳（2），弯刀，镶钉皮甲",
    "senses": {
      "被动察觉": 20
    },
    "languages": "通用语，盗贼黑话",
    "cr": 11,
    "xp": 7200,
    "pb": 4,
    "traits": [
      {
        "name": "反射闪避",
        "en_name": "Evasion",
        "description": "当匪帮祸首受到一个允许其进行敏捷豁免来只承受一半伤害的效应影响时，其豁免成功时不受伤害，豁免失败时只承受一半伤害。其无法在失能期间使用此特质。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "匪帮祸首使用弯刀或手铳发动共计三次攻击。"
      },
      {
        "name": "弯刀",
        "en_name": "Scimitar",
        "description": "近战攻击检定：+9，触及5尺。命中：12（2d6+5）挥砍伤害外加14（4d6）毒素伤害。"
      },
      {
        "name": "手铳",
        "en_name": "Pistol",
        "description": "远程攻击检定：+9，射程30/90尺。命中：10（1d10+5）穿刺伤害外加14（4d6）毒素伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "致命瞄准",
        "en_name": "Deadly Aim",
        "description": "匪帮祸首令其在当前回合中进行的下次攻击检定具有优势。且若那次攻击检定命中，其目标额外受到28（8d6）毒素伤害。"
      }
    ],
    "source_file": "类人\\匪徒\\匪帮祸首.htm"
  },
  {
    "name": "匪帮队长",
    "en_name": "Bandit Captain",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 15,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 52,
    "hp_formula": "8d8+16",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 4
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 5
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "运动": 4,
      "欺瞒": 4
    },
    "equipment": "手铳，弯刀，镶钉皮甲",
    "senses": {
      "被动察觉": 10
    },
    "languages": "通用语，盗贼黑话",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "匪帮队长使用弯刀或手铳发动共计两次攻击。"
      },
      {
        "name": "弯刀",
        "en_name": "Scimitar",
        "description": "近战攻击检定：+5，触及5尺。命中：6（1d6+3）挥砍伤害。"
      },
      {
        "name": "手铳",
        "en_name": "Pistol",
        "description": "远程攻击检定：+5，射程30/90尺。命中：8（1d10+3）穿刺伤害。"
      }
    ],
    "reactions": [
      {
        "name": "格挡",
        "en_name": "Parry",
        "description": "触发：匪帮队长在持握武器期间因近战攻击检定被命中。响应：匪帮队长令其对抗那次攻击的AC+2，可能令那次攻击改为失手。"
      }
    ],
    "source_file": "类人\\匪徒\\匪帮队长.htm"
  },
  {
    "name": "匪徒",
    "en_name": "Bandit",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 12,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 11,
    "hp_formula": "2d8+2",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "equipment": "皮甲，轻弩，弯刀",
    "senses": {
      "被动察觉": 10
    },
    "languages": "通用语，盗贼黑话",
    "cr": "1/8",
    "xp": 25,
    "pb": 2,
    "actions": [
      {
        "name": "弯刀",
        "en_name": "Scimitar",
        "description": "近战攻击检定：+3，触及5尺。命中：4（1d6+1）挥砍伤害。"
      },
      {
        "name": "轻弩",
        "en_name": "Light Crossbow",
        "description": "远程攻击检定：+3，射程80/320尺。命中：5（1d8+1）穿刺伤害。"
      }
    ],
    "source_file": "类人\\匪徒\\匪徒.htm"
  },
  {
    "name": "打手",
    "en_name": "Tough",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 12,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 32,
    "hp_formula": "5d8+10",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "equipment": "重弩，皮甲，硬头锤",
    "senses": {
      "被动察觉": 10
    },
    "languages": "通用语",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "集群战术",
        "en_name": "Pack Tactics",
        "description": "若打手的攻击目标生物5尺内存在有至少一名打手未失能的盟友，则打手对该生物进行的攻击检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "硬头锤",
        "en_name": "Mace",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）钝击伤害。"
      },
      {
        "name": "重弩",
        "en_name": "Heavy Crossbow",
        "description": "远程攻击检定：+3，射程100/400尺。命中：6（1d10+1）穿刺伤害。"
      }
    ],
    "source_file": "类人\\打手\\打手.htm"
  },
  {
    "name": "打手老大",
    "en_name": "Tough Boss",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 16,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 82,
    "hp_formula": "11d8+33",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 5
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 5
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 2
      }
    },
    "equipment": "链甲，重弩，战锤",
    "senses": {
      "被动察觉": 10
    },
    "languages": "通用语以及两门其他语言",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "traits": [
      {
        "name": "集群战术",
        "en_name": "Pack Tactics",
        "description": "若打手老大的攻击目标生物5尺内存在有至少一名打手老大未失能的盟友，则打手老大对该生物进行的攻击检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "打手老大使用战锤或重弩发动共计两次攻击。"
      },
      {
        "name": "战锤",
        "en_name": "Warhammer",
        "description": "近战攻击：+5，触及5尺。命中：12（2d8+3）钝击伤害。若目标生物体型不超过大型，则打手老大将其直线推离至多10尺。"
      },
      {
        "name": "重弩",
        "en_name": "Heavy Crossbow",
        "description": "远程攻击：+4，射程100/400尺。命中：13（2d10+2）穿刺伤害。"
      }
    ],
    "source_file": "类人\\打手\\打手老大.htm"
  },
  {
    "name": "斥候",
    "en_name": "Scout",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 16,
    "hp_formula": "3d8+3",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "自然": 4,
      "察觉": 5,
      "隐匿": 6,
      "求生": 5
    },
    "equipment": "皮甲，长弓，短剑",
    "senses": {
      "被动察觉": 15
    },
    "languages": "通用语以及两门其他语言",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "斥候使用短剑或长弓发动共计两次攻击。"
      },
      {
        "name": "短剑",
        "en_name": "Short sword",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）穿刺伤害。"
      },
      {
        "name": "长弓",
        "en_name": "Longbow",
        "description": "远程攻击检定：+4，射程150/600尺。命中：6（1d8+2）穿刺伤害。"
      }
    ],
    "source_file": "类人\\斥候\\斥候.htm"
  },
  {
    "name": "斥候队长",
    "en_name": "Scout Captain",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 15,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 66,
    "hp_formula": "12d8+12",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 5
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 4
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 6,
      "隐匿": 7,
      "求生": 6
    },
    "equipment": "长弓，短剑，镶钉皮甲",
    "senses": {
      "被动察觉": 16
    },
    "languages": "通用语以及两门其他语言",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "斥候队长使用短剑或长弓发动共计两次攻击。"
      },
      {
        "name": "短剑",
        "en_name": "Short sword",
        "description": "近战攻击检定：+5，触及5尺。命中：6（1d6+3）穿刺伤害，若本次攻击具有优势，则外加10（3d6）穿刺伤害。"
      },
      {
        "name": "长弓",
        "en_name": "Longbow",
        "description": "远程攻击检定：+5，射程150/600尺。命中：7（1d8+3）穿刺伤害，若本次攻击具有优势，则外加10（3d6）穿刺伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "瞄准",
        "en_name": "Aim",
        "description": "斥候队长令其在当前回合中进行的下次攻击检定具有优势。"
      }
    ],
    "reactions": [
      {
        "name": "直觉闪避",
        "en_name": "Uncanny Dodge",
        "description": "触发：斥候队长被一次攻击检定命中。响应：斥候队长因此次攻击受到的伤害减半（向下取整）。"
      }
    ],
    "source_file": "类人\\斥候\\斥候队长.htm"
  },
  {
    "name": "历战武者",
    "en_name": "Warrior Veteran",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 17,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 65,
    "hp_formula": "10d8+20",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "运动": 5,
      "察觉": 2
    },
    "equipment": "巨剑，重弩，板条甲",
    "senses": {
      "被动察觉": 12
    },
    "languages": "通用语以及一门其他语言",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "历战武者发动两次巨剑或重弩攻击。"
      },
      {
        "name": "巨剑",
        "en_name": "Greatsword",
        "description": "近战攻击检定：+5，触及5尺。命中：10（2d6+3）挥砍伤害。"
      },
      {
        "name": "重弩",
        "en_name": "Heavy Crossbow",
        "description": "远程攻击检定：+3，射程100/400尺。命中：12（2d10+1）穿刺伤害。"
      }
    ],
    "reactions": [
      {
        "name": "格挡",
        "en_name": "Parry",
        "description": "触发：武者在持握武器期间因近战攻击检定被命中。响应：武者令其对抗那次攻击的AC+2，可能令那次攻击改为失手。"
      }
    ],
    "source_file": "类人\\武者\\历战武者.htm"
  },
  {
    "name": "新晋武者",
    "en_name": "Warrior Infantry",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 9,
    "hp_formula": "2d8",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "equipment": "链甲衫，矛",
    "senses": {
      "被动察觉": 10
    },
    "languages": "通用语",
    "cr": "1/8",
    "xp": 25,
    "pb": 2,
    "traits": [
      {
        "name": "集群战术",
        "en_name": "Pack Tactics",
        "description": "若武者的攻击目标生物5尺内存在有至少一名武者未失能的盟友，则武者对该生物进行的攻击检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "矛",
        "en_name": "Spear",
        "description": "近战或远程攻击检定：+3，触及5尺或射程20/60尺。命中：4（1d6+1）穿刺伤害。"
      }
    ],
    "source_file": "类人\\武者\\新晋武者.htm"
  },
  {
    "name": "武将",
    "en_name": "Warrior Commander",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 18,
    "initiative_bonus": 9,
    "initiative_total": 19,
    "hp": 161,
    "hp_formula": "19d8+76",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 21,
        "mod": 5,
        "save": 9
      },
      "敏捷": {
        "score": 20,
        "mod": 5,
        "save": 9
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 8
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "运动": 9,
      "洞悉": 7,
      "察觉": 7
    },
    "equipment": "巨剑，长弓，板甲",
    "senses": {
      "被动察觉": 17
    },
    "languages": "通用语以及一门其他语言",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "武将使用巨剑或长弓发动共计三次攻击。"
      },
      {
        "name": "巨剑",
        "en_name": "Greatsword",
        "description": "近战攻击检定：+9，触及5尺。命中：19（4d6+5）挥砍伤害。武将还将造成下列效应之一："
      },
      {
        "name": "削弱",
        "en_name": "Sap",
        "description": "直至武将的下个回合开始，目标的下次攻击检定具有劣势。"
      },
      {
        "name": "机动",
        "en_name": "Maneuver",
        "description": "一名能看见或听见武将的盟友能以其反应移动至多等于其速度一半的距离且不会引发借机攻击。"
      },
      {
        "name": "长弓",
        "en_name": "Longbow",
        "description": "远程攻击检定：+9，射程150/600尺。命中：18（3d8+5）穿刺伤害，且目标的速度降低10尺直至其下个回合结束。"
      }
    ],
    "bonus_actions": [
      {
        "name": "战术突进",
        "en_name": "Tactical Charge",
        "description": "武将向一名其可见的敌人直线移动至多等于其速度一半的距离。"
      }
    ],
    "reactions": [
      {
        "name": "反制攻击",
        "en_name": "Counterattack",
        "description": "触发：武将被一次攻击检定命中。响应：武将令其对抗那次攻击的AC+4，可能令那次攻击改为失手。 \n若那次攻击失手，则武将可以对攻击者发动一次巨剑或长弓攻击。"
      }
    ],
    "source_file": "类人\\武者\\武将.htm"
  },
  {
    "name": "海盗",
    "en_name": "Pirate",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 14,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 33,
    "hp_formula": "6d8+6",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 5
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 4
      }
    },
    "equipment": "匕首（6），皮甲",
    "senses": {
      "被动察觉": 11
    },
    "languages": "通用语以及一门其他语言",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "海盗发动两次匕首攻击。其可以将其中一次攻击替换为使用华丽炫技。"
      },
      {
        "name": "匕首",
        "en_name": "Dagger",
        "description": "近战或远程攻击：+5，触及5尺或射程20/60尺。命中：5（1d4+3）穿刺伤害。"
      },
      {
        "name": "华丽炫技",
        "en_name": "Enthralling Panache",
        "description": "感知豁免：DC12，单一30尺内海盗可见的生物。失败：目标陷入魅惑状态直至海盗的下个回合开始。"
      }
    ],
    "source_file": "类人\\海盗\\海盗.htm"
  },
  {
    "name": "海盗将军",
    "en_name": "Pirate Admiral",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 20,
    "initiative_bonus": 10,
    "initiative_total": 20,
    "hp": 182,
    "hp_formula": "28d8+56",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 6
      },
      "敏捷": {
        "score": 22,
        "mod": 6,
        "save": 10
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 6
      },
      "魅力": {
        "score": 19,
        "mod": 4,
        "save": 8
      }
    },
    "skills": {
      "特技": 10,
      "运动": 6,
      "察觉": 6
    },
    "equipment": "手铳，弯刀",
    "senses": {
      "被动察觉": 16
    },
    "languages": "通用语以及一门其他语言",
    "cr": 12,
    "xp": 8400,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "海盗将军使用弯刀或手铳发动共计三次攻击。"
      },
      {
        "name": "弯刀",
        "en_name": "Scimitar",
        "description": "近战攻击检定：+10，触及5尺。命中：16（3d6+6）挥砍伤害外加7（2d6）毒素伤害，且目标承受以下效应之一（由海盗将军选择）："
      },
      {
        "name": "敬惧",
        "en_name": "Awestruck",
        "description": "目标陷入魅惑状态直至海盗将军的下个回合开始。"
      },
      {
        "name": "毒杀",
        "en_name": "Poison",
        "description": "目标陷入中毒状态直至海盗将军的下个回合开始。"
      },
      {
        "name": "手铳",
        "en_name": "Pistol",
        "description": "远程攻击检定：+10，射程30/90尺。命中：28（4d10+6）穿刺伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "给我上！",
        "en_name": "Rally",
        "description": "海盗将军选择30尺内至多三名其他生物。目标的攻击检定和豁免检定具有优势，直至海盗将军的下个回合开始。",
        "params": "1/日"
      }
    ],
    "reactions": [
      {
        "name": "防守架势",
        "en_name": "Defensive Stance",
        "description": "触发：海盗将军在持握武器期间因近战攻击检定被命中。响应：直至海盗将军的下个回合开始，海盗将军令其对抗近战攻击检定（包括触发攻击）的AC+4，可能令那次攻击改为失手。"
      }
    ],
    "source_file": "类人\\海盗\\海盗将军.htm"
  },
  {
    "name": "海盗船长",
    "en_name": "Pirate Captain",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 17,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 84,
    "hp_formula": "13d8+26",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 3
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "魅力": {
        "score": 17,
        "mod": 3,
        "save": 6
      }
    },
    "skills": {
      "特技": 7,
      "察觉": 5
    },
    "equipment": "手铳，刺剑",
    "senses": {
      "被动察觉": 15
    },
    "languages": "通用语以及一门其他语言",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "海盗船长使用刺剑或手铳发动共计三次攻击。"
      },
      {
        "name": "刺剑",
        "en_name": "Rapier",
        "description": "近战攻击：+7，触及5尺。命中：13（2d8+4）穿刺伤害，且海盗船长在本回合结束前进行的下次攻击检定具有优势。"
      },
      {
        "name": "手铳",
        "en_name": "Pistol",
        "description": "远程攻击：+7，射程30/90尺。命中：15（2d10+4）穿刺伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "领袖魅力",
        "en_name": "Captain",
        "description": "感知豁免：DC14，单一30尺内海盗船长可见的生物。失败：目标陷入魅惑状态直至海盗船长的下个回合开始。"
      }
    ],
    "reactions": [
      {
        "name": "弹反",
        "en_name": "Riposte",
        "description": "触发：海盗船长在持握武器期间因近战攻击检定被命中。响应：海盗船长令其对抗那次攻击的AC+3，可能令那次攻击改为失手。若那次攻击失手，且触发生物位于船长的触及范围内，则船长对该生物发动一次刺剑攻击。"
      }
    ],
    "source_file": "类人\\海盗\\海盗船长.htm"
  },
  {
    "name": "演艺传奇",
    "en_name": "Performer Legend",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 20,
    "initiative_bonus": 9,
    "initiative_total": 19,
    "hp": 162,
    "hp_formula": "25d8+50",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 20,
        "mod": 5,
        "save": 9
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 15,
        "mod": 2,
        "save": 6
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 9
      }
    },
    "skills": {
      "特技": 13,
      "运动": 5,
      "察觉": 7,
      "表演": 13,
      "隐匿": 9
    },
    "senses": {
      "被动察觉": 17
    },
    "languages": "通用语以及两门其他语言",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "演艺传奇发动三次镶玉指挥杖攻击。"
      },
      {
        "name": "镶玉指挥杖",
        "en_name": "Bejeweled Baton",
        "description": "近战攻击检定：+9，触及5尺。命中：10（2d4+5）钝击伤害外加10（3d6）心灵伤害。"
      },
      {
        "name": "庄严之歌",
        "en_name": "Majestic Song",
        "description": "感知豁免检定：DC17，以120尺内一点为中心半径20尺的球状区域内的每个生物。失败：22（4d8+4）心灵伤害，且目标陷入魅惑或恐慌状态（由演艺传奇选择），直至演艺传奇的下个回合结束。成功：仅半伤。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "演艺传奇施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC17）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "法师之手Mage Hand，次级幻象Minor Illusion，魔法伎俩Prestidigitation"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "高级幻影Major Image，投影术Project Image"
      }
    ],
    "reactions": [
      {
        "name": "魅力之佑",
        "en_name": "Warding Charm",
        "description": "触发：一名生物对演艺者进行攻击检定并命中。响应-感知豁免检定：DC17，触发生物。失败：此次攻击检定改为失手，且目标陷入魅惑状态直至演艺传奇的下个回合结束。"
      }
    ],
    "source_file": "类人\\演艺者\\演艺传奇.htm"
  },
  {
    "name": "演艺尊师",
    "en_name": "Performer Maestro",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 18,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 110,
    "hp_formula": "17d8+34",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 19,
        "mod": 4,
        "save": 7
      }
    },
    "skills": {
      "特技": 10,
      "运动": 4,
      "察觉": 5,
      "表演": 10,
      "隐匿": 7
    },
    "equipment": "刺剑",
    "senses": {
      "被动察觉": 15
    },
    "languages": "通用语以及一门其他语言",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "演艺尊师发动三次刺剑攻击。"
      },
      {
        "name": "刺剑",
        "en_name": "Rapier",
        "description": "近战攻击检定：+7，触及5尺。命中：8（1d8+4）穿刺伤害外加7（2d6）心灵伤害。"
      },
      {
        "name": "迷魅之歌",
        "en_name": "Beguiling Song",
        "description": "感知豁免检定：DC15，以120尺内一点为中心半径20尺的球状区域内的每个生物。失败：20（3d10+4）心灵伤害，且目标陷入魅惑状态直至演艺尊师的下个回合结束。成功：仅半伤。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "演艺尊师施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "次级幻象Minor Illusion，魔法伎俩Prestidigitation"
      },
      {
        "name": "1/日：",
        "en_name": "",
        "description": "塔莎狂笑术Tasha’s Hideous Laughter（三环版本）"
      }
    ],
    "source_file": "类人\\演艺者\\演艺尊师.htm"
  },
  {
    "name": "演艺者",
    "en_name": "Performer",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 27,
    "hp_formula": "5d8+5",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 5
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 5
      }
    },
    "skills": {
      "特技": 5,
      "运动": 3,
      "表演": 7
    },
    "equipment": "短剑",
    "senses": {
      "被动察觉": 12
    },
    "languages": "通用语以及一门其他语言",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "actions": [
      {
        "name": "短剑",
        "en_name": "Shortsword",
        "description": "近战攻击检定：+5，触及5尺。命中：6（1d6+3）穿刺伤害。"
      }
    ],
    "reactions": [
      {
        "name": "直觉闪避",
        "en_name": "Uncanny Dodge",
        "description": "触发：演艺者被一次攻击检定命中。响应：演艺者因此次攻击受到的伤害减半（向下取整）。"
      }
    ],
    "source_file": "类人\\演艺者\\演艺者.htm"
  },
  {
    "name": "狂战士",
    "en_name": "Berserker",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 67,
    "hp_formula": "9d8+27",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "equipment": "巨斧，兽皮甲",
    "senses": {
      "被动察觉": 10
    },
    "languages": "通用语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "浴血狂怒",
        "en_name": "Bloodied Fury",
        "description": "狂战士在浴血期间进行的攻击检定与豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "巨斧",
        "en_name": "Greataxe",
        "description": "近战攻击检定：+5，触及5尺。命中：9（1d12+3）挥砍伤害。"
      }
    ],
    "source_file": "类人\\狂战士\\狂战士.htm"
  },
  {
    "name": "狂战将",
    "en_name": "Berserker Commander",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 16,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 136,
    "hp_formula": "16d8+64",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 7
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 19,
        "mod": 4,
        "save": 7
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "运动": 7,
      "察觉": 5
    },
    "damage_immunities": [
      "魅惑",
      "恐慌"
    ],
    "equipment": "巨斧，标枪（6）",
    "senses": {
      "被动察觉": 15
    },
    "languages": "通用语",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "traits": [
      {
        "name": "浴血狂怒",
        "en_name": "Bloodied Fury",
        "description": "狂战将在浴血期间进行的攻击检定与豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "狂战将使用巨斧或标枪发动共计三次攻击。"
      },
      {
        "name": "巨斧",
        "en_name": "Greataxe",
        "description": "近战攻击检定：+7，触及5尺。命中：10（1d12+4）挥砍伤害，且目标或其5尺内的另一生物受到10（3d6）雷鸣伤害。"
      },
      {
        "name": "标枪",
        "en_name": "Javelin",
        "description": "近战或远程攻击检定：+7，触及5尺或射程30/120尺。命中：18（4d6+4）穿刺伤害，且目标速度降低5尺直至狂战将的下个回合开始。"
      }
    ],
    "bonus_actions": [
      {
        "name": "狂怒冲杀",
        "en_name": "Frenzied Rush",
        "description": "狂战将30尺内的每名盟友都能够以其反应移动至多等于其自身速度一半的距离，且不会引发借机攻击。同时，狂战将也可以移动至多等于自身速度一半的距离，且不会引发借机攻击。"
      }
    ],
    "source_file": "类人\\狂战士\\狂战将.htm"
  },
  {
    "name": "侍祭僧侣",
    "en_name": "Priest Acolyte",
    "type_line": "中型或小型类人（牧师），中立",
    "size": "Medium",
    "creature_type": "或小型类人（牧师）",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 11,
    "hp_formula": "2d8+2",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "医药": 4,
      "宗教": 2
    },
    "equipment": "链甲衫，圣徽，硬头锤",
    "senses": {
      "被动察觉": 12
    },
    "languages": "通用语",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "actions": [
      {
        "name": "硬头锤",
        "en_name": "Mace",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）钝击伤害外加2（1d4）光耀伤害。"
      },
      {
        "name": "光焰",
        "en_name": "Radiant Flame",
        "description": "远程攻击检定：+4，射程60尺。命中：7（2d6）光耀伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "侍祭僧侣施展以下一道法术，使用感知作为施法属性："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "光亮术Light，奇术Thaumanturgy"
      }
    ],
    "bonus_actions": [
      {
        "name": "至圣援护",
        "en_name": "Divine Aid",
        "description": "侍祭僧侣施展祝福术Bless、治愈真言Healing Word或庇护术Sanctuary，使用与施法动作相同的施法属性。",
        "params": "1/日"
      }
    ],
    "source_file": "类人\\祭司\\侍祭僧侣.htm"
  },
  {
    "name": "大祭司",
    "en_name": "Archpriest",
    "type_line": "中型或小型类人（牧师），中立",
    "size": "Medium",
    "creature_type": "或小型类人（牧师）",
    "alignment": "中立",
    "ac": 16,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 240,
    "hp_formula": "32d8+96",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 7
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 6
      },
      "感知": {
        "score": 21,
        "mod": 5,
        "save": 9
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "洞悉": 9,
      "医药": 9,
      "察觉": 9,
      "宗教": 10
    },
    "equipment": "链甲，圣徽",
    "senses": {
      "被动察觉": 19
    },
    "languages": "通用语以及两门其他语言",
    "cr": 12,
    "xp": 8400,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "大祭司发动三次圣光惩灭攻击。"
      },
      {
        "name": "圣光惩灭",
        "en_name": "Radiant Burst",
        "description": "近战或远程攻击检定：+9，触及5尺或射程60尺。命中：27（4d10+5）光耀伤害。"
      },
      {
        "name": "至圣真言",
        "en_name": "Holy Word",
        "description": "感知豁免检定：DC17，源自大祭司的20尺光环区域内的所有敌人。失败：21（6d6）光耀伤害，且目标陷入震慑状态直至大祭司的下个回合结束。成功：仅半伤。",
        "params": "充能4~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "祭司施展以下一道法术，无需任何材料成分并使用感知作为施法属性："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "光亮术Light，奇术Thaumanturgy"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "焰击术Flame Strike（六环版本）， 高等复原术Greater Restoration，死者复活Raise Dead，诚实之域Zone of Truth"
      }
    ],
    "bonus_actions": [
      {
        "name": "至圣援护",
        "en_name": "Divine Aid",
        "description": "大祭司施展祝福术Bless、解除魔法Dispel \nMagic、治愈真言Healing Word或次等复原术Lesser \nRestoration，使用与施法动作相同的施法属性。",
        "params": "3/日"
      }
    ],
    "source_file": "类人\\祭司\\大祭司.htm"
  },
  {
    "name": "祭司",
    "en_name": "Priest",
    "type_line": "中型或小型类人（牧师），中立",
    "size": "Medium",
    "creature_type": "或小型类人（牧师）",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 38,
    "hp_formula": "7d8+7",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "医药": 7,
      "察觉": 5,
      "宗教": 5
    },
    "equipment": "链甲衫，圣徽，硬头锤",
    "senses": {
      "被动察觉": 15
    },
    "languages": "通用语以及一门其他语言",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "祭司使用硬头锤或光焰发动共计两次攻击。"
      },
      {
        "name": "硬头锤",
        "en_name": "Mace",
        "description": "近战攻击检定：+5，触及5尺。命中：6（1d6+3）钝击伤害外加5（2d4）光耀伤害。"
      },
      {
        "name": "光焰",
        "en_name": "Radiant Flame",
        "description": "远程攻击检定：+5，射程60尺。命中：11（2d10）光耀伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "祭司施展以下一道法术，使用感知作为施法属性："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "光亮术Light，奇术Thaumanturgy"
      },
      {
        "name": "1/日：",
        "en_name": "",
        "description": "灵体卫士Spirit Guardians"
      }
    ],
    "bonus_actions": [
      {
        "name": "至圣援护",
        "en_name": "Divine Aid",
        "description": "祭司施展祝福术Bless、解除魔法Dispel Magic、治愈真言Healing Word或次等复原术Lesser Restoration，使用与施法动作相同的施法属性。",
        "params": "3/日"
      }
    ],
    "source_file": "类人\\祭司\\祭司.htm"
  },
  {
    "name": "警卫",
    "en_name": "Guard",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 16,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 11,
    "hp_formula": "2d8+2",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 2
    },
    "equipment": "链甲衫，盾牌，矛",
    "senses": {
      "被动察觉": 12
    },
    "languages": "通用语",
    "cr": "1/8",
    "xp": 25,
    "pb": 2,
    "actions": [
      {
        "name": "矛",
        "en_name": "Spear",
        "description": "近战或远程攻击检定：+3，触及5尺或射程20/60尺。命中：4（1d6+1）穿刺伤害。"
      }
    ],
    "source_file": "类人\\警卫\\警卫.htm"
  },
  {
    "name": "警卫队长",
    "en_name": "Guard Captain",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 18,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 75,
    "hp_formula": "10d8+30",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "运动": 6,
      "察觉": 4
    },
    "equipment": "胸甲，标枪（6），长剑，盾牌",
    "senses": {
      "被动察觉": 14
    },
    "languages": "通用语",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "警卫队长使用标枪或长剑发动共计两次攻击。"
      },
      {
        "name": "标枪",
        "en_name": "Javelin",
        "description": "近战或远程攻击检定：+6，触及5尺或射程30/120尺。命中：14（3d6+4）穿刺伤害。"
      },
      {
        "name": "长剑",
        "en_name": "Longsword",
        "description": "近战攻击检定：+6，触及5尺。命中：15（2d10+4）挥砍伤害。"
      }
    ],
    "source_file": "类人\\警卫\\警卫队长.htm"
  },
  {
    "name": "贵族",
    "en_name": "Noble",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 15,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 9,
    "hp_formula": "2d8",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "欺瞒": 5,
      "洞悉": 4,
      "游说": 5
    },
    "equipment": "胸甲，刺剑",
    "senses": {
      "被动察觉": 12
    },
    "languages": "通用语以及两门其他语言",
    "cr": "1/8",
    "xp": 25,
    "pb": 2,
    "actions": [
      {
        "name": "刺剑",
        "en_name": "Rapier",
        "description": "近战攻击检定：+3，触及5尺。命中：5（1d8+1）穿刺伤害。"
      }
    ],
    "reactions": [
      {
        "name": "格挡",
        "en_name": "Parry",
        "description": "触发：贵族在持握武器期间因近战攻击检定被命中。响应：贵族令其对抗那次攻击的AC+2，可能令那次攻击改为失手。"
      }
    ],
    "source_file": "类人\\贵族\\贵族.htm"
  },
  {
    "name": "贵血天骄",
    "en_name": "Noble Prodigy",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 16,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 148,
    "hp_formula": "27d8+27",
    "speed": {
      "walk": "30"
    },
    "abilities": {
      "力量": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 5
      },
      "智力": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 6
      },
      "魅力": {
        "score": 19,
        "mod": 4,
        "save": 8
      }
    },
    "skills": {
      "察觉": 6,
      "说服": 8
    },
    "senses": {
      "被动察觉": 16
    },
    "languages": "通用语以及两门其他语言",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "贵血天骄发动三次迷魅惑心攻击。"
      },
      {
        "name": "迷魅惑心",
        "en_name": "Beguiling Strike",
        "description": "近战或远程攻击检定：+8，触及5尺或射程60尺。命中：18（4d6+4）心灵伤害，且目标陷入魅惑状态直至贵血天骄的下个回合开始。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "贵血天骄施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC16）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "法师护甲Mage Armor（已计入AC）， 法师之手Mage Hand，次级幻象Minor Illusion"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "摧心术Befuddlement，侦测思想Detect Thoughts，飞行术Fly，探知Scrying，粉碎音波Shatter（七环版本）"
      }
    ],
    "reactions": [
      {
        "name": "护盾术",
        "en_name": "Shield",
        "description": "贵血天骄施展护盾术Shield（触发条件见该法术），使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "类人\\贵族\\贵族天骄.htm"
  },
  {
    "name": "贵血天骄",
    "en_name": "Noble Prodigy",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 16,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 148,
    "hp_formula": "27d8+27",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 5
      },
      "智力": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 6
      },
      "魅力": {
        "score": 19,
        "mod": 4,
        "save": 8
      }
    },
    "skills": {
      "察觉": 6,
      "游说": 8
    },
    "senses": {
      "被动察觉": 16
    },
    "languages": "通用语以及两门其他语言",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "贵血天骄发动三次迷魅惑心攻击。"
      },
      {
        "name": "迷魅惑心",
        "en_name": "Beguiling Strike",
        "description": "近战或远程攻击检定：+8，触及5尺或射程60尺。命中：18（4d6+4）心灵伤害，且目标陷入魅惑状态直至贵血天骄的下个回合开始。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "贵血天骄施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC16）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "法师护甲Mage Armor（已计入AC）， 法师之手Mage Hand，次级幻象Minor Illusion"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "摧心术Befuddlement，侦测思想Detect Thoughts，飞行术Fly，探知Scrying，粉碎音波Shatter（七环版本）"
      }
    ],
    "reactions": [
      {
        "name": "护盾术",
        "en_name": "Shield",
        "description": "贵血天骄施展护盾术Shield（触发条件见该法术），使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "类人\\贵族\\贵血天骄.htm"
  },
  {
    "name": "元素邪教徒",
    "en_name": "Elemental Cultist",
    "type_line": "中型或小型类人，混乱邪恶",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "混乱邪恶",
    "ac": 16,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 135,
    "hp_formula": "18d8+54",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "奥秘": 5,
      "察觉": 7,
      "宗教": 5
    },
    "equipment": "链甲衫",
    "senses": {
      "被动察觉": 17
    },
    "languages": "通用语，原初语",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "邪教徒使用元素链枷或元素巨爪共计三次攻击。"
      },
      {
        "name": "元素链枷",
        "en_name": "Elemental Flail",
        "description": "近战攻击检定：+7，触及5尺。命中：25（6d6+4）点伤害，伤害类型由邪教徒从下列选项中选择一种：强酸，寒冷，火焰，闪电或雷鸣。"
      },
      {
        "name": "元素巨爪",
        "en_name": "Elemental Claw",
        "description": "远程攻击检定：+7，射程120尺。命中：22（4d10）点伤害，伤害类型由邪教徒由邪教徒从下列选项中选择一种：强酸，寒冷，火焰，闪电或雷鸣。若目标生物体型不超过中型，则邪教徒将其直线拉近或推离至多10尺。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "邪教徒施展以下一道法术，使用感知作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "四象法门Elementalism，法师之手Mage Hand"
      }
    ],
    "reactions": [
      {
        "name": "元素吸收",
        "en_name": "Elemental Absorption",
        "description": "触发：邪教徒受到强酸、寒冷、火焰、闪电或雷鸣伤害。响应：邪教徒对该次伤害实例的具有抗性并获得10临时生命值。",
        "params": "1/日"
      }
    ],
    "source_file": "类人\\邪教徒\\元素邪教徒.htm"
  },
  {
    "name": "异怪邪教徒",
    "en_name": "Aberrant Cultist",
    "type_line": "中型或小型类人，中立邪恶",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立邪恶",
    "ac": 14,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 137,
    "hp_formula": "25d8+25",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "感知": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "奥秘": 6,
      "察觉": 7,
      "宗教": 6
    },
    "senses": {
      "黑暗视觉": 90,
      "被动察觉": 17
    },
    "languages": "通用语，深潜语，心灵感应30尺",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "邪教徒发动两次触手鞭笞攻击。其可以将其中一次攻击替换为使用心智腐坏。"
      },
      {
        "name": "触手鞭笞",
        "en_name": "Tentacle Lash",
        "description": "近战攻击检定：+7，触及10尺。命中：7（1d6+4）挥砍伤害外加14（4d6）心灵伤害。若目标生物体型不超过大型，则其被两条触手之一擒抱，陷入受擒状态（逃脱DC14），且目标陷入束缚状态直至擒抱结束。"
      },
      {
        "name": "心智腐坏",
        "en_name": "Mind Rot",
        "description": "感知豁免检定：DC15，单一90尺内邪教徒可见的生物。失败：27（6d8）心灵伤害，且目标陷入中毒状态直至邪教徒的下个回合开始。成功：仅半伤。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "邪教徒施展以下一道法术，使用感知作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测思想Detect Thoughts，次级幻象Minor Illusion"
      }
    ],
    "reactions": [
      {
        "name": "法术反制",
        "en_name": "Counterspell",
        "description": "邪教徒施展法术反制Counterspell（触发条件见该法术），使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "类人\\邪教徒\\异怪邪教徒.htm"
  },
  {
    "name": "死亡邪教徒",
    "en_name": "Death Cultist",
    "type_line": "中型或小型类人，中立邪恶",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立邪恶",
    "ac": 17,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 127,
    "hp_formula": "15d8+60",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "洞悉": 6,
      "察觉": 6,
      "宗教": 4
    },
    "equipment": "板条甲",
    "senses": {
      "被动察觉": 16
    },
    "languages": "通用语",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "邪教徒使用惊怖巨镰或亡命射线发动共计三次攻击。"
      },
      {
        "name": "惊怖巨镰",
        "en_name": "Dread Scythe",
        "description": "近战攻击检定：+7，触及10尺。命中：9（1d10+4）挥砍伤害外加11（2d10）暗蚀伤害，且目标将无法回复生命值，直至其下一回合结束。"
      },
      {
        "name": "亡命射线",
        "en_name": "Deathly Ray",
        "description": "远程攻击检定：+6，射程120尺。命中：22（4d10）暗蚀伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "邪教徒施展以下一道法术，使用感知作为施法属性（法术豁免DC14）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "死者交谈Speak with Dead，奇术Thaumaturgy"
      }
    ],
    "bonus_actions": [
      {
        "name": "魂灵惊嚎",
        "en_name": "Spirit Wail",
        "description": "感知豁免检定：DC14，源自邪教徒的20尺光环区域内的所有生物。失败：14（4d6）心灵伤害，且目标陷入恐慌状态直至其下个回合结束。成功：仅半伤。",
        "params": "充能5~6"
      }
    ],
    "source_file": "类人\\邪教徒\\死亡邪教徒.htm"
  },
  {
    "name": "邪教徒",
    "en_name": "Cultist",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 12,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 9,
    "hp_formula": "2d8",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "欺瞒": 2,
      "宗教": 2
    },
    "equipment": "皮甲，镰刀",
    "senses": {
      "被动察觉": 10
    },
    "languages": "通用语",
    "cr": "1/8",
    "xp": 25,
    "pb": 2,
    "actions": [
      {
        "name": "仪典小镰刀",
        "en_name": "Ritual Sickle",
        "description": "近战攻击：+3，触及5尺。命中：3（1d4+1）挥砍伤害外加1暗蚀伤害。"
      }
    ],
    "source_file": "类人\\邪教徒\\邪教徒.htm"
  },
  {
    "name": "邪教教宗",
    "en_name": "Cultist Hierophant",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 16,
    "initiative_bonus": 8,
    "initiative_total": 18,
    "hp": 144,
    "hp_formula": "17d8+68",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 9
      }
    },
    "skills": {
      "察觉": 7,
      "游说": 9,
      "宗教": 5
    },
    "equipment": "胸甲，圣徽",
    "senses": {
      "被动察觉": 17
    },
    "languages": "天界语，通用语",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "邪教教宗使用契约魔刃或光耀射线发动共计三次攻击。"
      },
      {
        "name": "契约魔刃",
        "en_name": "Pact Blade",
        "description": "近战攻击：+9，触及5尺。命中：12（2d6+5）挥砍伤害外加18（4d8）光耀伤害。"
      },
      {
        "name": "光耀射线",
        "en_name": "Radiant Ray",
        "description": "远程攻击：+9，射程120尺。命中：31（4d12+5）光耀伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "邪教教宗施展以下一道法术，使用魅力作为施法属性（法术豁免DC17）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "奇术Thaumaturgy"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "贾拉兹光辉风暴Jailarzi's Storm of Radiance（七环版本），   群体暗示术Mass Suggestion"
      }
    ],
    "source_file": "类人\\邪教徒\\邪教教宗.htm"
  },
  {
    "name": "邪教狂信者",
    "en_name": "Cultist Fanatic",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 44,
    "hp_formula": "8d8+8",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 4
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "欺瞒": 3,
      "游说": 3,
      "宗教": 2
    },
    "equipment": "圣徽，皮甲",
    "senses": {
      "被动察觉": 12
    },
    "languages": "通用语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "契约魔刃",
        "en_name": "Pact Blade",
        "description": "近战攻击：+4，触及5尺。命中：6（1d8+2）挥砍伤害外加7（2d6）暗蚀伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "邪教狂信者施展以下一道法术，使用感知作为施法属性（法术豁免DC12，法术攻击命中+4）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "光亮术Light，奇术Thaumaturgy"
      },
      {
        "name": "2/日：",
        "en_name": "",
        "description": "命令术Command"
      },
      {
        "name": "1/日：",
        "en_name": "",
        "description": "定身类人Hold Person"
      }
    ],
    "bonus_actions": [
      {
        "name": "灵体武器",
        "en_name": "Spiritual Weapon",
        "description": "邪教狂信者施展法术灵体武器Spiritual Weapon，使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "类人\\邪教徒\\邪教狂信者.htm"
  },
  {
    "name": "邪魔邪教徒",
    "en_name": "Fiend Cultist",
    "type_line": "中型或小型类人，中立邪恶",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立邪恶",
    "ac": 16,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 127,
    "hp_formula": "17d8+51",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 7,
      "宗教": 4
    },
    "equipment": "胸甲",
    "senses": {
      "黑暗视觉": 90,
      "被动察觉": 17
    },
    "languages": "深渊语，通用语，炼狱语",
    "cr": 8,
    "xp": 3900,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "邪教徒发动三次契约魔斧攻击。"
      },
      {
        "name": "契约魔斧",
        "en_name": "Pact Axe",
        "description": "近战攻击检定：+7，触及5尺。命中：10（1d12+4）挥砍伤害外加13（3d8）火焰伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "邪教徒施展以下一道法术，使用感知作为施法属性（法术豁免DC15，法术攻击命中+7）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "灼热射线Scorching（五环版本），奇术Thaumatutgy"
      },
      {
        "name": "2/日：",
        "en_name": "",
        "description": "火球术Fireball（六环版本）"
      }
    ],
    "reactions": [
      {
        "name": "炼狱叱喝",
        "en_name": "Hellish Rebuke",
        "description": "邪教徒施展炼狱叱喝Hellish \nRebuke（触发条件见该法术），使用与施法动作相同的施法属性。"
      }
    ],
    "source_file": "类人\\邪教徒\\邪魔邪教徒.htm"
  },
  {
    "name": "间谍",
    "en_name": "Spy",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 12,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 27,
    "hp_formula": "6d8",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "欺瞒": 5,
      "洞悉": 4,
      "调查": 5,
      "察觉": 6,
      "巧手": 4,
      "隐匿": 6
    },
    "equipment": "手弩，短剑，盗贼工具",
    "senses": {
      "被动察觉": 16
    },
    "languages": "通用语以及一门其他语言",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "actions": [
      {
        "name": "短剑",
        "en_name": "Shortsword",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）穿刺伤害外加7（2d6）毒素伤害。"
      },
      {
        "name": "手弩",
        "en_name": "Hand Crossbow",
        "description": "远程攻击检定：+4，射程30/120尺。命中：5（1d6+2）穿刺伤害外加7（2d6）毒素伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "灵巧动作",
        "en_name": "Cunning Action",
        "description": "间谍执行疾走、撤离或躲藏动作。"
      }
    ],
    "source_file": "类人\\间谍\\间谍.htm"
  },
  {
    "name": "间谍大师",
    "en_name": "Spy Master",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 19,
    "initiative_bonus": 9,
    "initiative_total": 19,
    "hp": 137,
    "hp_formula": "25d8+25",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 20,
        "mod": 5,
        "save": 9
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 5
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 8
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "欺瞒": 7,
      "洞悉": 7,
      "调查": 8,
      "察觉": 11,
      "巧手": 9,
      "隐匿": 13
    },
    "equipment": "手弩，刺剑，盗贼工具",
    "senses": {
      "被动察觉": 21
    },
    "languages": "通用语以及两门其他语言",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "间谍大师使用刺剑或手弩发动共计三次攻击。"
      },
      {
        "name": "刺剑",
        "en_name": "Rapier",
        "description": "近战攻击检定：+9，触及5尺。命中：14（2d8+5）穿刺伤害外加7（2d6）毒素伤害。"
      },
      {
        "name": "手弩",
        "en_name": "Hand Crossbow",
        "description": "远程攻击检定：+9，射程30/120尺。命中：12（2d6+5）穿刺伤害外加9（2d8）毒素伤害。"
      },
      {
        "name": "毒烟炸弹",
        "en_name": "Smoke Bomb",
        "description": "间谍大师向30尺内其可见的一点掷出一枚炸弹。体质豁免检定：DC16，以该点为中心，半径20尺的球状区域内的每名生物。失败：28（8d6）毒素伤害，且目标陷入目盲状态直至间谍大师的下个回合结束。成功：仅半伤。",
        "params": "1/日"
      }
    ],
    "bonus_actions": [
      {
        "name": "灵巧动作",
        "en_name": "Cunning Action",
        "description": "间谍大师执行疾走、撤离或躲藏动作。"
      }
    ],
    "source_file": "类人\\间谍\\间谍大师.htm"
  },
  {
    "name": "天命骑士",
    "en_name": "Questing Knight",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 18,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 202,
    "hp_formula": "27d8+81",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 9
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 5
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 8
      }
    },
    "skills": {
      "运动": 9,
      "察觉": 5,
      "游说": 8
    },
    "damage_immunities": [
      "魅惑",
      "恐慌"
    ],
    "equipment": "巨剑，长弓，板甲",
    "senses": {
      "被动察觉": 15
    },
    "languages": "通用语以及两门其他语言",
    "cr": 12,
    "xp": 8400,
    "pb": 4,
    "traits": [
      {
        "name": "勇毅灵光",
        "en_name": "Aura of Bravery",
        "description": "位于源自天命骑士的30尺光环区域内的、由天命骑士选择的生物，若身处该区域内，则其对魅惑与恐慌状态免疫。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "天命骑士使用巨剑或长弓发动共计三次攻击。"
      },
      {
        "name": "巨剑",
        "en_name": "Greatsword",
        "description": "近战攻击检定：+9，触及5尺。命中：12（2d6+5）挥砍伤害外加22（5d8）光耀伤害。"
      },
      {
        "name": "长弓",
        "en_name": "Longbow",
        "description": "远程攻击检定：+7，射程150/600尺。命中：12（2d8+3）穿刺伤害外加22（5d8）光耀伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "天命骑士施展以下一道法术，使用魅力作为施法属性（法术豁免DC16）："
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "昼明术Daylight，驱逐善恶Dispel Evil and Good，高等复原术Greater Restoration，魅影驹Phantom Steed"
      }
    ],
    "source_file": "类人\\骑士\\天命骑士.htm"
  },
  {
    "name": "骑士",
    "en_name": "Knight",
    "type_line": "中型或小型类人，中立",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立",
    "ac": 18,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 52,
    "hp_formula": "8d8+16",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 4
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "damage_immunities": [
      "恐慌"
    ],
    "equipment": "巨剑，重弩，板甲",
    "senses": {
      "被动察觉": 10
    },
    "languages": "通用语以及一门其他语言",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "骑士使用巨剑或重弩发动共计两次攻击。"
      },
      {
        "name": "巨剑",
        "en_name": "Greatsword",
        "description": "近战攻击：+5，触及5尺。命中：10（2d6+3）挥砍伤害外加4（1d8）光耀伤害。"
      },
      {
        "name": "重弩",
        "en_name": "Heavy Crossbow",
        "description": "远程攻击：+2，射程100/400尺。命中：11（2d10）穿刺伤害外加4（1d8）光耀伤害。"
      }
    ],
    "reactions": [
      {
        "name": "格挡",
        "en_name": "Parry",
        "description": "触发：骑士在持握武器期间因近战攻击检定被命中。响应：骑士令其对抗那次攻击的AC+2，可能令那次攻击改为失手。"
      }
    ],
    "source_file": "类人\\骑士\\骑士.htm"
  },
  {
    "name": "大法师",
    "en_name": "Archmage",
    "type_line": "中型或小型类人（法师），中立",
    "size": "Medium",
    "creature_type": "或小型类人（法师）",
    "alignment": "中立",
    "ac": 17,
    "initiative_bonus": 6,
    "initiative_total": 16,
    "hp": 170,
    "hp_formula": "31d8+31",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 20,
        "mod": 5,
        "save": 9
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 6
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "奥秘": 13,
      "历史": 9,
      "察觉": 6
    },
    "damage_immunities": [
      "心灵"
    ],
    "condition_immunities": [
      "魅惑（心灵屏障Mind Blank 期间）"
    ],
    "equipment": "魔杖",
    "senses": {
      "被动察觉": 16
    },
    "languages": "通用语以及五门其他语言",
    "cr": 12,
    "xp": 8000,
    "pb": 4,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "大法师对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "大法师发动四次奥能爆发攻击。"
      },
      {
        "name": "奥能爆发",
        "en_name": "Arcane Burst",
        "description": "近战或远程攻击：+9，触及5尺或射程150尺。命中：27（4d10+5）力场伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "大法师施展以下一道法术，使用智力作为施法属性（法术豁免DC17）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，侦测思想Detect Thoughts，易容术Disguise，隐形术Invisibility，光亮术Light，法师护甲Mage Armor（已计入AC），   法师之手Mage Hand，魔法伎俩Prestidigitation"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "飞行术Fly，闪电束Lightening Bolt（七环版本）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "寒冰锥Cone of Cold（九环版本），  心灵屏障Mind Blank（于战斗前施展），   探知Scrying，传送术Teleport"
      }
    ],
    "bonus_actions": [
      {
        "name": "迷踪步",
        "en_name": "Mistry Step",
        "description": "大法师施展迷踪步Misty Step，使用与施法动作相同的施法属性。",
        "params": "3/日"
      }
    ],
    "reactions": [
      {
        "name": "护身魔法",
        "en_name": "Protective Magic",
        "description": "大法师施展法术反制Counterspell或护盾术Shield（触发条件见这些法术），使用与施法动作相同的施法属性。",
        "params": "3/日"
      }
    ],
    "source_file": "类人\\魔法师\\大法师.htm"
  },
  {
    "name": "魔法学徒",
    "en_name": "Mage Apprentice",
    "type_line": "中型或小型类人（法师），中立",
    "size": "Medium",
    "creature_type": "或小型类人（法师）",
    "alignment": "中立",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 49,
    "hp_formula": "9d8+9",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 5
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 3
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "奥秘": 5,
      "察觉": 3
    },
    "equipment": "材料包",
    "senses": {
      "被动察觉": 13
    },
    "languages": "通用语以及一门其他语言",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "奥能爆发",
        "en_name": "Arcane Burst",
        "description": "近战或远程攻击检定：+5，触及5尺或射程120尺。命中：14（2d10+3）力场伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "魔法学徒施展以下一道法术，使用智力作为施法属性（法术豁免DC13，法术攻击命中+5）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "法师之手Mage Hand，魔法伎俩Prestidigitation"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "易容术Disguise Self，冰刃Ice Knife，法师护甲Mage Armor（已计入AC），   雷鸣波Thunderwave"
      }
    ],
    "source_file": "类人\\魔法师\\魔法学徒.htm"
  },
  {
    "name": "魔法师",
    "en_name": "Mage",
    "type_line": "中型或小型类人（法师），中立",
    "size": "Medium",
    "creature_type": "或小型类人（法师）",
    "alignment": "中立",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 81,
    "hp_formula": "18d8",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 17,
        "mod": 3,
        "save": 6
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 4
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "奥秘": 6,
      "历史": 6,
      "察觉": 4
    },
    "equipment": "魔杖",
    "senses": {
      "被动察觉": 14
    },
    "languages": "通用语以及三门其他语言",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "魔法师发动三次奥能爆发攻击。"
      },
      {
        "name": "奥能爆发",
        "en_name": "Arcane Burst",
        "description": "近战或远程攻击：+6，触及5尺或射程120尺。命中：16（3d8+3）力场伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "魔法师施展以下一道法术，使用智力作为施法属性（法术豁免DC14）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，光亮术Light，法师护甲Mage Armor（已计入AC），  法师之手Mage Hand，魔法伎俩Prestidigitation"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "火球术Fireball（四环版本），隐形术Invisibility"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "寒冰锥Cone of Cold，飞行术Fly"
      }
    ],
    "bonus_actions": [
      {
        "name": "迷踪步",
        "en_name": "Mistry Step",
        "description": "魔法师施展迷踪步Misty Step，使用与施法动作相同的施法属性。",
        "params": "3/日"
      }
    ],
    "reactions": [
      {
        "name": "护身魔法",
        "en_name": "Protective Magic",
        "description": "魔法师施展法术反制Counterspell或护盾术Shield（触发条件见这些法术），使用与施法动作相同的施法属性。",
        "params": "3/日"
      }
    ],
    "source_file": "类人\\魔法师\\魔法师.htm"
  },
  {
    "name": "心能灰泥怪",
    "en_name": "Psychic Gray Ooze",
    "type_line": "中型泥怪，无阵营",
    "size": "Medium",
    "creature_type": "泥怪",
    "alignment": "无阵营",
    "ac": 9,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 37,
    "hp_formula": "5d8+15",
    "speed": {
      "walk": "10尺，攀爬10尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "魅力": {
        "score": 2,
        "mod": -4,
        "save": -4
      }
    },
    "skills": {
      "隐匿": 3
    },
    "damage_resistances": [
      "强酸、寒冷、火焰、心灵"
    ],
    "damage_immunities": [
      "目盲、魅惑、耳聋、力竭、恐慌、受擒、倒地、束缚"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 8
    },
    "languages": "无",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "无定形",
        "en_name": "Amorphous",
        "description": "灰泥怪可以移动穿过最窄1寸宽的空间而无需消耗额外的移动力。"
      }
    ],
    "actions": [
      {
        "name": "伪肢",
        "en_name": "Pseudopod",
        "description": "近战攻击检定：+3，触及5尺。命中：11（3d6+1）点强酸伤害，且目标的智力豁免具有劣势直至灰泥怪的下个回合结束。"
      },
      {
        "name": "心能粉碎",
        "en_name": "Psythic Crush",
        "description": "智力豁免检定：DC10，单一60尺内泥怪可见的生物。失败：13（3d8）点心灵伤害。"
      }
    ],
    "reactions": [
      {
        "name": "心灵反侵",
        "en_name": "Mind Corrosion",
        "description": "触发：灰泥怪对抗生物的法术和其他魔法效应时进行的豁免失败。\n响应：触发生物受到3（1d6）心灵伤害。"
      }
    ],
    "source_file": "泥怪\\灰泥怪\\心能灰泥怪.htm"
  },
  {
    "name": "灰泥怪",
    "en_name": "Gray Ooze",
    "type_line": "中型泥怪，无阵营",
    "size": "Medium",
    "creature_type": "泥怪",
    "alignment": "无阵营",
    "ac": 9,
    "initiative_bonus": -2,
    "initiative_total": 8,
    "hp": 22,
    "hp_formula": "3d8+9",
    "speed": {
      "walk": "10尺，攀爬10尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "魅力": {
        "score": 2,
        "mod": -4,
        "save": -4
      }
    },
    "skills": {
      "隐匿": 2
    },
    "damage_resistances": [
      "强酸、寒冷、火焰"
    ],
    "damage_immunities": [
      "目盲、魅惑、耳聋、力竭、恐慌、受擒、倒地、束缚"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 8
    },
    "languages": "无",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "无定形",
        "en_name": "Amorphous",
        "description": "灰泥怪可以移动穿过最窄1寸宽的空间而无需消耗额外的移动力。"
      },
      {
        "name": "腐蚀形态",
        "en_name": "Corrosive Form",
        "description": "非魔法弹药在命中灰泥怪并造成伤害后立即被摧毁。非魔法武器在对灰泥怪造成任意伤害后将积累-1的攻击检定减值。若武器的减值累计达到-5则其被摧毁。对武器施展修复术Mending可以移除这一减值。"
      }
    ],
    "actions": [
      {
        "name": "伪肢",
        "en_name": "Pseudopod",
        "description": "近战攻击检定：+3，触及5尺。命中：10（2d8+1）点强酸伤害。目标着装的非魔法护甲提供的AC将承受-1的减值。若护甲的AC因减值降至10则其被摧毁。对护甲施展修复术Mending可以移除这一减值。"
      }
    ],
    "source_file": "泥怪\\灰泥怪\\灰泥怪.htm"
  },
  {
    "name": "启蒙大树",
    "en_name": "Awakened Tree",
    "type_line": "巨型植物，中立",
    "size": "Huge",
    "creature_type": "植物",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": -2,
    "initiative_total": 8,
    "hp": 59,
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "damage_vulnerabilities": [
      "火焰"
    ],
    "damage_resistances": [
      "钝击",
      "穿刺"
    ],
    "senses": {
      "被动察觉": 10
    },
    "languages": "通用语以及一门其他语言",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "粗枝猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+6，触及10尺 命中：14（3d6+4）钝击伤害。"
      }
    ],
    "source_file": "植物\\启蒙植物\\启蒙大树.htm"
  },
  {
    "name": "启蒙灌木",
    "en_name": "Awakened Shrub",
    "type_line": "小型植物，中立",
    "size": "Small",
    "creature_type": "植物",
    "alignment": "中立",
    "ac": 9,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 10,
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "damage_vulnerabilities": [
      "火焰"
    ],
    "damage_resistances": [
      "穿刺"
    ],
    "senses": {
      "被动察觉": 10
    },
    "languages": "通用语以及一门其他语言",
    "cr": 0,
    "xp": 10,
    "pb": 2,
    "actions": [
      {
        "name": "枝叶刮擦",
        "en_name": "Rake",
        "description": "近战攻击检定：+1，触及5尺 命中：1挥砍伤害。"
      }
    ],
    "source_file": "植物\\启蒙植物\\启蒙灌木.htm"
  },
  {
    "name": "枯枝怪",
    "en_name": "Twig Blight",
    "type_line": "小型植物，中立邪恶",
    "size": "Small",
    "creature_type": "植物",
    "alignment": "中立邪恶",
    "ac": 14,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 7,
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 4,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 3,
        "mod": -4,
        "save": -4
      }
    },
    "skills": {
      "隐匿": 4
    },
    "damage_vulnerabilities": [
      "火焰"
    ],
    "damage_immunities": [
      "耳聋"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 9
    },
    "languages": "理解通用语，但不会说",
    "cr": "1/8",
    "xp": 25,
    "pb": 2,
    "traits": [
      {
        "name": "集群战术",
        "en_name": "Pack Tactics",
        "description": "若枯枝怪的攻击目标生物5尺内存在有至少一名枯枝怪未失能的盟友，则枯枝怪对该生物进行的攻击检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "枯枝爪击",
        "en_name": "Claw",
        "description": ""
      }
    ],
    "source_file": "植物\\枯萎怪\\枯枝怪.htm"
  },
  {
    "name": "枯树怪",
    "en_name": "Tree Blight",
    "type_line": "巨型植物，中立邪恶",
    "size": "Huge",
    "creature_type": "植物",
    "alignment": "中立邪恶",
    "ac": 15,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 115,
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 3,
        "mod": -4,
        "save": -4
      }
    },
    "damage_immunities": [
      "耳聋"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 10
    },
    "languages": "理解通用语和德鲁伊语，但不会说",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "枯树怪发动两次枯枝撞击攻击并使用一次根系缠绕。"
      },
      {
        "name": "枯枝撞击",
        "en_name": "Branch",
        "description": "近战攻击检定：+9，触及15尺 命中：16（3d6+6）钝击伤害"
      },
      {
        "name": "根系缠绕",
        "en_name": "Grasping Root",
        "description": "力量豁免检定：DC17，单一15尺内枯树怪可见的不超过大型的生物。\n失败：目标被枯树怪拉近至多10尺，并被其六条树根之一缠绕，陷入受擒状态（逃脱DC16）。目标在其回合开始时受到13（2d6+6）钝击伤害，直至擒抱结束。"
      }
    ],
    "bonus_actions": [
      {
        "name": "朽躯啮咬",
        "en_name": "Gnash",
        "description": "敏捷豁免检定：DC17，单一受擒于枯树怪的生物。失败：19（3d8+6）穿刺伤害。成功：半伤。"
      }
    ],
    "source_file": "植物\\枯萎怪\\枯树怪.htm"
  },
  {
    "name": "枯藤怪",
    "en_name": "Vine Blight",
    "type_line": "中型植物，中立邪恶",
    "size": "Medium",
    "creature_type": "植物",
    "alignment": "中立邪恶",
    "ac": 12,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 19,
    "hp_formula": "3d8+6",
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 3,
        "mod": -4,
        "save": -4
      }
    },
    "skills": {
      "隐匿": 1
    },
    "damage_immunities": [
      "耳聋"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 10
    },
    "languages": "通用语",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "actions": [
      {
        "name": "藤蔓绞缠",
        "en_name": "Constricting Vine",
        "description": "近战攻击检定：+4，触及10尺 命中：6（1d8+2）钝击伤害。若目标生物体型不超过大型，则其陷入受擒状态（逃脱DC12）。目标在其回合开始时受到4（1d8）钝击伤害，且枯藤怪无法再发动藤蔓绞缠攻击，直至擒抱结束。"
      },
      {
        "name": "植物缠绕",
        "en_name": "Entangling Plants",
        "description": "枯藤怪施展纠缠术Entangle\n，使用体质作为施法属性（法术豁免DC12）。",
        "params": "充能5~6"
      }
    ],
    "source_file": "植物\\枯萎怪\\枯藤怪.htm"
  },
  {
    "name": "枯针怪",
    "en_name": "Needle Blight",
    "type_line": "中型植物，中立邪恶",
    "size": "Medium",
    "creature_type": "植物",
    "alignment": "中立邪恶",
    "ac": 12,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 16,
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 4,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 3,
        "mod": -4,
        "save": -4
      }
    },
    "damage_immunities": [
      "耳聋"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 9
    },
    "languages": "理解通用语，但不会说",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "actions": [
      {
        "name": "枯枝爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+3，触及5尺 命中：6（2d4+1）挥砍伤害。"
      },
      {
        "name": "枯针射击",
        "en_name": "Needles",
        "description": "远程攻击检定：+3，射程30/60尺 命中：6（2d4+1）穿刺伤害。"
      }
    ],
    "source_file": "植物\\枯萎怪\\枯针怪.htm"
  },
  {
    "name": "甘提亚斯枯殖巨树",
    "en_name": "Gulthias Blight",
    "type_line": "超巨型植物，中立邪恶",
    "size": "Gargantuan",
    "creature_type": "植物",
    "alignment": "中立邪恶",
    "ac": 20,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 264,
    "speed": {
      "walk": "50尺"
    },
    "abilities": {
      "力量": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "察觉": 9
    },
    "damage_resistances": [
      "火焰",
      "暗蚀"
    ],
    "damage_immunities": [
      "耳聋"
    ],
    "senses": {
      "盲视": 120,
      "被动察觉": 19
    },
    "languages": "通用语，德鲁伊语",
    "cr": 16,
    "xp": 15000,
    "pb": 5,
    "traits": [
      {
        "name": "枯萎之种",
        "en_name": "Blight Seeds",
        "description": "当甘提亚斯枯殖巨树完成长休时，其会把1d6颗种子播撒到其30尺内的未占据空间的地面上。24小时后，这些种子会成长为受甘提亚斯枯殖巨树控制的生物。为每颗种子掷1d8，以决定其变为什么生物：1~4，枯枝怪Twig Blight ；5~6，枯针怪Needle \n      Blight；7~8，枯藤怪Vine Blight。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "甘提亚斯枯殖巨树使用巨木崩槌或荆棘暴雨发动共计两次攻击，并使用一次饮命邪根。"
      },
      {
        "name": "巨木崩槌",
        "en_name": "Slam",
        "description": "近战攻击检定：+12，触及10尺 命中：25（4d8+7）钝击伤害。"
      },
      {
        "name": "荆棘暴雨",
        "en_name": "Thorn Volley",
        "description": "远程攻击检定：+12，射程60/180尺。命中：20（3d8+7）穿刺伤害。"
      },
      {
        "name": "饮命邪根",
        "en_name": "Life-Draining Root",
        "description": "体质豁免检定：DC20，单一30尺内甘提亚斯枯殖巨树可见的一名不超过巨型的生物。\n失败：14（2d6+7）暗蚀伤害，且目标被六条根茎之一缠绕，陷入受擒状态（逃脱DC17）。目标陷入束缚状态并在其回合开始时受到14（4d6）暗蚀伤害，直至擒抱结束。目标的生命值上限减少等于其受到暗蚀伤害的值，且甘提亚斯枯殖巨树恢复等量的生命值。"
      }
    ],
    "source_file": "植物\\枯萎怪\\甘提亚斯枯殖巨树.htm"
  },
  {
    "name": "尖叫菌",
    "en_name": "Shrieker Fungus",
    "type_line": "中型植物，无阵营",
    "size": "Medium",
    "creature_type": "植物",
    "alignment": "无阵营",
    "ac": 5,
    "initiative_bonus": -5,
    "initiative_total": 5,
    "hp": 13,
    "hp_formula": "3d8",
    "speed": {
      "walk": "5尺"
    },
    "abilities": {
      "力量": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "敏捷": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "damage_immunities": [
      "目盲",
      "魅惑",
      "耳聋",
      "恐慌"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 6
    },
    "languages": "无",
    "cr": 0,
    "xp": 0,
    "pb": 2,
    "reactions": [
      {
        "name": "尖叫",
        "en_name": "Shriek",
        "description": "触发：生物或明亮光照的光源移动至尖叫菌的30尺内。\n响应：尖叫菌发出300尺内都能听见的尖叫，持续1分钟或在尖叫菌死亡时提前结束。"
      }
    ],
    "source_file": "植物\\真菌\\尖叫菌.htm"
  },
  {
    "name": "气孢菌",
    "en_name": "Gas Spore Fungus",
    "type_line": "大型植物，无阵营",
    "size": "Large",
    "creature_type": "植物",
    "alignment": "无阵营",
    "ac": 8,
    "initiative_bonus": -5,
    "initiative_total": 5,
    "hp": 13,
    "hp_formula": "9d10-36",
    "speed": {
      "walk": "5尺，飞行10尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "敏捷": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "体质": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "目盲",
      "魅惑",
      "耳聋",
      "恐慌",
      "麻痹",
      "中毒",
      "倒地"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 5
    },
    "languages": "无",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "自爆",
        "en_name": "Death Burst",
        "description": "气孢菌在死亡时爆炸。体质豁免检定：DC10，源自气孢菌的20尺光环区域内的每名生物。"
      }
    ],
    "actions": [
      {
        "name": "卷须",
        "en_name": "Tendril",
        "description": "近战攻击检定：+0，触及5尺。\n命中：3（1d6）毒素伤害，且目标陷入中毒状态，持续至其下个回合结束。"
      }
    ],
    "source_file": "植物\\真菌\\气孢菌.htm"
  },
  {
    "name": "紫腐菌",
    "en_name": "Violet Fungus",
    "type_line": "中型植物，无阵营",
    "size": "Medium",
    "creature_type": "植物",
    "alignment": "无阵营",
    "ac": 5,
    "initiative_bonus": -5,
    "initiative_total": 5,
    "hp": 18,
    "hp_formula": "4d8",
    "speed": {
      "walk": "5尺"
    },
    "abilities": {
      "力量": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "敏捷": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "damage_immunities": [
      "目盲",
      "魅惑",
      "耳聋",
      "恐慌"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 6
    },
    "languages": "无",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "紫腐菌发动两次腐烂触碰攻击。"
      },
      {
        "name": "腐烂触碰",
        "en_name": "Rotting Touch",
        "description": "近战攻击检定：+2，触及10尺。"
      }
    ],
    "source_file": "植物\\真菌\\紫腐菌.htm"
  },
  {
    "name": "紫腐菌尸聚怪",
    "en_name": "Violet Fungus Necrohulk",
    "type_line": "大型植物，中立邪恶",
    "size": "Large",
    "creature_type": "植物",
    "alignment": "中立邪恶",
    "ac": 17,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 123,
    "hp_formula": "13d10+52",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "目盲",
      "魅惑",
      "耳聋",
      "恐慌",
      "中毒"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 12
    },
    "languages": "无",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "尸聚怪发动两次腐烂猛击攻击。"
      },
      {
        "name": "腐烂猛击",
        "en_name": "Rotting Slam",
        "description": "近战攻击检定：+7，触及10尺。"
      },
      {
        "name": "蕈孢炸弹",
        "en_name": "Spore Bomb",
        "description": "体质豁免检定：DC15，以60尺内尸聚怪可见一点为中心，半径20尺球状区域内的每名生物。",
        "params": "充能5~6"
      }
    ],
    "bonus_actions": [
      {
        "name": "吞吃躯体",
        "en_name": "Absorb Body",
        "description": "力量豁免检定：DC15，单一5尺内体型不超过中型且尸聚怪可见的生物。\n失败：目标被拉入尸聚怪所在的空间，并被嫁接到尸聚怪身上。尸聚怪同时能嫁接的生物数上限为一。被嫁接期间，目标陷入束缚\n状态且其进行的体质豁免具有劣势。当尸聚怪移动时，被嫁接目标也将一并移动。若目标在被嫁接期间死亡，其遗体将被摧毁，且尸聚怪恢复10生命值。被嫁接目标自身或位于尸聚怪5尺内的生物，都能够以动作进行一次DC15的力量（运动）检定。检定成功则目标不再被嫁接，并移动至尸聚怪5尺内的一处未占据空间。"
      }
    ],
    "source_file": "植物\\真菌\\紫腐菌尸聚怪.htm"
  },
  {
    "name": "蕈人孢子奴仆",
    "en_name": "Myconid Spore Servant",
    "type_line": "中型或小型植物，无阵营",
    "size": "Medium",
    "creature_type": "或小型植物",
    "alignment": "无阵营",
    "ac": 13,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 37,
    "hp_formula": "5d8+15",
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "目盲",
      "魅惑",
      "恐慌",
      "麻痹",
      "中毒"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 8
    },
    "languages": "心灵感应30尺",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "actions": [
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+5，触及5尺。\n命中：6（1d6+3）钝击伤害外加2（1d4）毒素伤害。"
      }
    ],
    "source_file": "植物\\蕈人\\蕈人孢子奴仆.htm"
  },
  {
    "name": "蕈人幼体",
    "en_name": "Myconid Sprout",
    "type_line": "小型植物，守序中立",
    "size": "Small",
    "creature_type": "植物",
    "alignment": "守序中立",
    "ac": 10,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 3,
    "hp_formula": "1d6",
    "speed": {
      "walk": "10尺"
    },
    "abilities": {
      "力量": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 10
    },
    "languages": "心灵感应240尺",
    "cr": 0,
    "xp": 10,
    "pb": 2,
    "traits": [
      {
        "name": "厌日症",
        "en_name": "Sun Sickness",
        "description": "若蕈人身处阳光下，其D20检定具有劣势。蕈人待在阳光下超过1小时就会死亡。"
      }
    ],
    "actions": [
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+1，触及5尺。"
      },
      {
        "name": "通念孢子",
        "en_name": "Rapport Spores",
        "description": "孢子被释放在源自蕈人的30尺光环区域内。区域内任何智力值不低于2且非构装非元素非亡灵的生物获得30尺心灵感应，持续1小时。"
      }
    ],
    "source_file": "植物\\蕈人\\蕈人幼体.htm"
  },
  {
    "name": "蕈人成体",
    "en_name": "Myconid Adult",
    "type_line": "中型植物，守序中立",
    "size": "Medium",
    "creature_type": "植物",
    "alignment": "守序中立",
    "ac": 12,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 16,
    "hp_formula": "3d8+3",
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 11
    },
    "languages": "心灵感应240尺",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "厌日症",
        "en_name": "",
        "description": "Sun \nSickness。若蕈人身处阳光下，其D20检定具有劣势。蕈人待在阳光下超过1小时就会死亡。"
      }
    ],
    "actions": [
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+2，触及5尺。\n命中：4（1d8）钝击伤害外加3（1d6）毒素伤害。"
      },
      {
        "name": "安抚孢子",
        "en_name": "Pacifying Spores",
        "description": "体质豁免检定：DC11，单一10尺内蕈人可见的生物。",
        "params": "1/日"
      },
      {
        "name": "通念孢子",
        "en_name": "Rapport Spores",
        "description": "孢子被释放在源自蕈人的30尺光环区域内。区域内任何智力值不低于2且非构装非元素非亡灵的生物获得30尺心灵感应，持续1小时。"
      }
    ],
    "source_file": "植物\\蕈人\\蕈人成体.htm"
  },
  {
    "name": "蕈人王",
    "en_name": "Myconid Sovereign",
    "type_line": "大型植物，守序中立",
    "size": "Large",
    "creature_type": "植物",
    "alignment": "守序中立",
    "ac": 13,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 45,
    "hp_formula": "6d10+12",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 12
    },
    "languages": "心灵感应240尺",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "厌日症",
        "en_name": "",
        "description": "Sun \nSickness。若蕈人身处阳光下，其D20检定具有劣势。蕈人待在阳光下超过1小时就会死亡。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蕈人发动一次猛击攻击并使用安抚孢子。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+3，触及5尺。\n命中：6（2d4+1）钝击伤害外加5（2d4）毒素伤害。"
      },
      {
        "name": "活化孢子",
        "en_name": "Animating Spores",
        "description": "蕈人向5尺内一具非构装非亡灵的中型或小型尸体释放孢子。尸体会在24小时后活化为蕈人孢子奴仆Myconid \nSpore Servant。尸体会保持活化状态1d4+1周或直至被摧毁。曾以此法活化过的尸体无法再次以此法活化。",
        "params": "3/日"
      },
      {
        "name": "安抚孢子",
        "en_name": "Pacifying Spores",
        "description": "体质豁免检定：DC12，单一10尺内蕈人可见的生物。\n失败：目标陷入震慑状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。"
      },
      {
        "name": "通念孢子",
        "en_name": "Rapport Spores",
        "description": "孢子被释放在源自蕈人的30尺光环区域内。区域内任何智力值不低于2且非构装非元素非亡灵的生物获得30尺心灵感应，持续1小时。"
      }
    ],
    "source_file": "植物\\蕈人\\蕈人王.htm"
  },
  {
    "name": "活化凌空剑",
    "en_name": "Animated Flying Sword",
    "type_line": "小型构装，无阵营",
    "size": "Small",
    "creature_type": "构装",
    "alignment": "无阵营",
    "ac": 17,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 14,
    "hp_formula": "4d6",
    "speed": {
      "walk": "5尺，飞行50尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 4
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "damage_immunities": [
      "毒素",
      "心灵"
    ],
    "condition_immunities": [
      "魅惑",
      "耳聋",
      "力竭",
      "恐慌",
      "麻痹",
      "石化",
      "中毒"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 7
    },
    "languages": "无",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "actions": [
      {
        "name": "斩击",
        "en_name": "Slash",
        "description": "近战攻击检定：+4，触及5尺。命中：6（1d8+2）挥砍伤害。"
      }
    ],
    "source_file": "构装\\活化物件\\活化凌空剑.htm"
  },
  {
    "name": "活化扫帚",
    "en_name": "Animated Broom",
    "type_line": "小型构装，无阵营",
    "size": "Small",
    "creature_type": "构装",
    "alignment": "无阵营",
    "ac": 15,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 14,
    "hp_formula": "4d6",
    "speed": {
      "walk": "5尺，飞行50尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "damage_immunities": [
      "毒素",
      "心灵"
    ],
    "condition_immunities": [
      "魅惑",
      "耳聋",
      "力竭",
      "恐慌",
      "麻痹",
      "石化",
      "中毒"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 7
    },
    "languages": "无",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "traits": [
      {
        "name": "飞掠",
        "en_name": "Flyby",
        "description": "扫帚飞行离开敌人的触及范围时不会引发借机攻击。"
      }
    ],
    "actions": [
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+5，触及5尺。命中：5（1d4+3）钝击伤害。"
      }
    ],
    "source_file": "构装\\活化物件\\活化扫帚.htm"
  },
  {
    "name": "活化盔甲",
    "en_name": "Animated Armor",
    "type_line": "中型构装，无阵营",
    "size": "Medium",
    "creature_type": "构装",
    "alignment": "无阵营",
    "ac": 18,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 33,
    "hp_formula": "6d8+6",
    "speed": {
      "walk": "25尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "damage_immunities": [
      "毒素",
      "心灵"
    ],
    "condition_immunities": [
      "魅惑",
      "耳聋",
      "力竭",
      "恐慌",
      "麻痹",
      "石化",
      "中毒"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 6
    },
    "languages": "无",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "活化盔甲发动两次猛击攻击。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）钝击伤害。"
      }
    ],
    "source_file": "构装\\活化物件\\活化盔甲.htm"
  },
  {
    "name": "活化闷人毯",
    "en_name": "Animated Rug of Smothering",
    "type_line": "大型构装，无阵营",
    "size": "Large",
    "creature_type": "构装",
    "alignment": "无阵营",
    "ac": 12,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 27,
    "hp_formula": "5d10",
    "speed": {
      "walk": "10尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "damage_immunities": [
      "毒素",
      "心灵"
    ],
    "condition_immunities": [
      "魅惑",
      "耳聋",
      "力竭",
      "恐慌",
      "麻痹",
      "石化",
      "中毒"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 6
    },
    "languages": "无",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "卷紧",
        "en_name": "Smother",
        "description": "近战攻击检定：+5，触及5尺。\n命中：10（2d6+3）钝击伤害。若目标生物体型不超过中型，地毯可使其陷入受擒状态（逃脱DC13）替代造成伤害。直至擒抱结束，目标陷入目盲和束缚状态，且窒息，并在其回合开始时受到10（2d6+3）钝击伤害。地毯同时能卷紧的生物数上限为一。"
      }
    ],
    "source_file": "构装\\活化物件\\活化闷人毯.htm"
  },
  {
    "name": "焚化铜牛",
    "en_name": "Brazen Gorgon",
    "type_line": "大型构装，无阵营",
    "size": "Large",
    "creature_type": "构装",
    "alignment": "无阵营",
    "ac": 19,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 161,
    "hp_formula": "17d10+68",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 14,
        "mod": 4,
        "save": 4
      },
      "体质": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 10
    },
    "damage_immunities": [
      "火焰"
    ],
    "condition_immunities": [
      "力竭",
      "石化"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 20
    },
    "languages": "无",
    "cr": 9,
    "xp": 5000,
    "pb": 4,
    "traits": [
      {
        "name": "烈火灵光",
        "en_name": "Flame Aura",
        "description": "铜牛回合结束时位于源自铜牛的5尺光环区域内的每名生物受到13（3d8）火焰伤害。"
      },
      {
        "name": "照明",
        "en_name": "Illumination",
        "description": "铜牛散发出半径10尺的明亮光照以及额外10尺的微光光照。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "铜牛发动两次顶撞攻击。"
      },
      {
        "name": "顶撞",
        "en_name": "Gore",
        "description": "近战攻击检定：+8，触及5尺。命中：11（2d6+4）穿刺伤害，外加10（3d6）火焰伤害。"
      },
      {
        "name": "熔焰冲锋",
        "en_name": "Smelting Charge",
        "description": "铜牛移动至多等于其速度的距离且不会引发借机攻击，并且可以移动穿过中型或小型生物所处的空间。所处空间被铜牛进入的每名生物都会被选为一次以下效应的目标。敏捷豁免检定：DC16。失败：13（2d8+4）穿刺伤害外加13（3d8）火焰伤害，且目标被拖入铜牛所处空间并陷入受擒状态（逃脱DC14）。若铜牛已经令一名生物陷入受擒，目标改为陷入倒地状态。目标陷入束缚状态直至擒抱结束。当铜牛移动时，受擒目标也将一并移动，且铜牛无需额外消耗移动力。",
        "params": "充能5~6"
      }
    ],
    "source_file": "构装\\石化铁牛\\焚化铜牛.htm"
  },
  {
    "name": "石化铁牛",
    "en_name": "Gorgon",
    "type_line": "大型构装，无阵营",
    "size": "Large",
    "creature_type": "构装",
    "alignment": "无阵营",
    "ac": 19,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 114,
    "hp_formula": "12d10+48",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 7
    },
    "damage_immunities": [
      "力竭",
      "石化"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 17
    },
    "languages": "无",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "actions": [
      {
        "name": "顶撞",
        "en_name": "Gore",
        "description": "近战攻击检定：+8，触及5尺。命中：18（2d12+5）穿刺伤害。若铁牛在此次攻击前立即向着目标直线移动了20+尺，且目标生物体型不超过大型，则其陷入倒地状态"
      },
      {
        "name": "石化吐息",
        "en_name": "Petrifying Breath",
        "description": "体质豁免检定：DC15，30尺锥状区域内的每名生物。失败：目标陷入束缚状态，在其下个回合结束时目标若仍处于束缚则重复豁免，成功则终止其身上的该效应。再次失败：目标陷入石化状态替代其束缚状态。",
        "params": "充能5~6"
      }
    ],
    "bonus_actions": [
      {
        "name": "践踏",
        "en_name": "Trample",
        "description": "敏捷豁免检定：DC16，单一5尺内处于倒地状态的生物。失败：16（2d10+5）钝击伤害。成功：半伤。"
      }
    ],
    "source_file": "构装\\石化铁牛\\石化铁牛.htm"
  },
  {
    "name": "石魔像",
    "en_name": "Stone Golem",
    "type_line": "大型构装，无阵营",
    "size": "Large",
    "creature_type": "构装",
    "alignment": "无阵营",
    "ac": 18,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 220,
    "hp_formula": "21d10+105",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "damage_immunities": [
      "毒素",
      "心灵"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "麻痹",
      "石化",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 10
    },
    "languages": "理解通用语以及两门其他语言，但不会说",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "traits": [
      {
        "name": "不变形态",
        "en_name": "Immutable Form",
        "description": "魔像无法变形。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "魔像对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "魔像使用猛击或力场箭发动共计两次攻击。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+10，触及5尺。命中：15（2d8+6）钝击伤害外加9（2d8）力场伤害。"
      },
      {
        "name": "力场箭",
        "en_name": "Force Bolt",
        "description": "远程攻击检定：+9，射程120尺。命中：22（4d10）力场伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "缓慢",
        "en_name": "Slow",
        "description": "魔像施展法术缓慢术Slow，无需法术成分并使用体质作为施法属性（法术豁免DC17）。",
        "params": "充能5~6"
      }
    ],
    "source_file": "构装\\魔像\\石魔像.htm"
  },
  {
    "name": "血肉魔像",
    "en_name": "Flesh Golem",
    "type_line": "中型构装，中立",
    "size": "Medium",
    "creature_type": "构装",
    "alignment": "中立",
    "ac": 9,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 127,
    "hp_formula": "15d8+60",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "damage_immunities": [
      "闪电",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "麻痹",
      "石化",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "理解通用语以及一门其他语言，但不会说",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "厌火",
        "en_name": "Aversion to Fire",
        "description": "若魔像受到火焰伤害，直至其下个回合结束，其进行的攻击检定和属性检定具有劣势。"
      },
      {
        "name": "失心狂怒",
        "en_name": "Berserk",
        "description": "若魔像在回合开始时浴血，掷1d6。骰值为6时，魔像开始失心狂怒。魔像狂怒期间，其在其回合内攻击距其最近的其可见的生物。若没有生物位于其能够移动并攻击到的范围内，则魔像攻击物件。一旦魔像开始失心狂怒，狂怒持续至其被摧毁或其不再浴血。"
      },
      {
        "name": "不变形态",
        "en_name": "Immutable Form",
        "description": "魔像无法变形。"
      },
      {
        "name": "闪电吸收",
        "en_name": "Lightning Absorption",
        "description": "每当魔像将受闪电伤害时，其恢复等于闪电伤害数值的生命值。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "魔像对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "魔像发动两次猛击攻击。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+7，触及5尺。\n命中：13（2d8+4）钝击伤害外加4（1d8）闪电伤害。"
      }
    ],
    "source_file": "构装\\魔像\\血肉魔像.htm"
  },
  {
    "name": "铁魔像",
    "en_name": "Iron Golem",
    "type_line": "大型构装，无阵营",
    "size": "Large",
    "creature_type": "构装",
    "alignment": "无阵营",
    "ac": 20,
    "initiative_bonus": 9,
    "initiative_total": 19,
    "hp": 252,
    "hp_formula": "24d10+120",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 24,
        "mod": 7,
        "save": 7
      },
      "敏捷": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "damage_immunities": [
      "火焰",
      "毒素",
      "心灵"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "麻痹",
      "石化",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 10
    },
    "languages": "理解通用语以及两门其他语言，但不会说",
    "cr": 16,
    "xp": 15000,
    "pb": 5,
    "traits": [
      {
        "name": "火焰吸收",
        "en_name": "Fire Absorption",
        "description": "每当魔像将受火焰伤害时，其恢复等于火焰伤害数值的生命值。"
      },
      {
        "name": "不变形态",
        "en_name": "Immutable \nForm",
        "description": "魔像无法变形  。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "魔像对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "魔像使用利刃铁臂或火炎箭发动共计两次攻击。"
      },
      {
        "name": "利刃铁臂",
        "en_name": "Bladed Arm",
        "description": "近战攻击检定：+12，触及10尺。\n命中：20（3d8+7）挥砍伤害外加10（3d6）火焰伤害。"
      },
      {
        "name": "火炎箭",
        "en_name": "Fiery Bolt",
        "description": "远程攻击检定：+10，射程120尺。\n命中：36（8d8）火焰伤害。"
      },
      {
        "name": "毒素吐息",
        "en_name": "Poison Breath",
        "description": "体质豁免检定：DC18，60尺锥状区域内的每名生物。\n失败：55（10d10）毒素伤害。\n成功：半伤。",
        "params": "充能6"
      }
    ],
    "source_file": "构装\\魔像\\铁魔像.htm"
  },
  {
    "name": "黏土魔像",
    "en_name": "Clay Golem",
    "type_line": "大型构装，无阵营",
    "size": "Large",
    "creature_type": "构装",
    "alignment": "无阵营",
    "ac": 14,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 123,
    "hp_formula": "13d10+52",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "damage_resistances": [
      "钝击",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "强酸",
      "毒素",
      "心灵"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "麻痹",
      "石化",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "通用语以及一门其他语言",
    "cr": 9,
    "xp": 5000,
    "pb": 4,
    "traits": [
      {
        "name": "强酸吸收",
        "en_name": "Acid Absorption",
        "description": "每当魔像将受强酸伤害时，其不受伤害，改为恢复等于强酸伤害数值的生命值。"
      },
      {
        "name": "失心狂怒",
        "en_name": "Berserk",
        "description": "若魔像在回合开始时浴血，掷1d6。骰值为6时，魔像开始失心狂怒。魔像狂怒期间，其在其回合内攻击距其最近的其可见的生物。若没有生物位于其能够移动并攻击到的范围内，则魔像攻击物件。一旦魔像开始失心狂怒，狂怒持续至其被摧毁或其不再浴血。"
      },
      {
        "name": "不变形态",
        "en_name": "Immutable Form",
        "description": "魔像无法变形。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "魔像对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "魔像发动两次猛击攻击，若其本回合使用了加速则发动三次猛击攻击。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+9，触及5尺。命中：10（1d10+5）钝击伤害外加6（1d12）强酸伤害，且目标的生命值上限减少等于其受到强酸伤害的数值。"
      }
    ],
    "bonus_actions": [
      {
        "name": "加速",
        "en_name": "Hasten",
        "description": "魔像执行疾走和撤离动作。",
        "params": "充能5~6"
      }
    ],
    "source_file": "构装\\魔像\\黏土魔像.htm"
  },
  {
    "name": "魔冢·三元冢",
    "en_name": "Modron Tridrone",
    "type_line": "中型构装，守序中立",
    "size": "Medium",
    "creature_type": "构装",
    "alignment": "守序中立",
    "ac": 15,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 16,
    "hp_formula": "3d8+3",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "damage_immunities": [
      "魅惑"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 10
    },
    "languages": "魔冢语",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "解体",
        "en_name": "Disintergration",
        "description": "若魔冢死亡，其解体为尘埃，留下其着装或携带的任何东西。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "魔冢发动三次时械之矛攻击。"
      },
      {
        "name": "时械之矛",
        "en_name": "Clockwork Spear",
        "description": "近战或远程攻击检定：+3，触及5尺或射程120尺。命中：4（1d6+1）力场伤害。命中或失手：矛会在被用于一次远程攻击后立即魔法性地回到魔冢手中。"
      }
    ],
    "source_file": "构装\\魔冢\\魔冢·三元冢.htm"
  },
  {
    "name": "魔冢·二元冢",
    "en_name": "Modron Duodrone",
    "type_line": "中型构装，守序中立",
    "size": "Medium",
    "creature_type": "构装",
    "alignment": "守序中立",
    "ac": 15,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 11,
    "hp_formula": "2d8+2",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "damage_immunities": [
      "魅惑"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 10
    },
    "languages": "魔冢语",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "traits": [
      {
        "name": "解体",
        "en_name": "Disintergration",
        "description": "若魔冢死亡，其解体为尘埃，留下其着装或携带的任何东西。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "魔冢发动两次时械剑刃攻击。"
      },
      {
        "name": "时械剑刃",
        "en_name": "Clockwork Blade",
        "description": "近战或远程攻击检定：+3，触及5尺或射程30尺。命中：4（1d6+1）力场伤害。命中或失手：剑刃会在被用于一次远程攻击后立即魔法性地回到魔冢手中。"
      }
    ],
    "source_file": "构装\\魔冢\\魔冢·二元冢.htm"
  },
  {
    "name": "魔冢·五元冢",
    "en_name": "Modron Quadrone",
    "type_line": "大型构装，守序中立",
    "size": "Large",
    "creature_type": "构装",
    "alignment": "守序中立",
    "ac": 16,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 32,
    "hp_formula": "5d10+5",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "察觉": 4
    },
    "damage_immunities": [
      "魅惑"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 14
    },
    "languages": "魔冢语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "解体",
        "en_name": "Disintergration",
        "description": "若魔冢死亡，其解体为尘埃，留下其着装或携带的任何东西。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "魔冢发动五次猛击攻击或五次电能释放攻击。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）力场伤害。"
      },
      {
        "name": "电能释放",
        "en_name": "Electrical Discharge",
        "description": "远程攻击检定：+4，射程120尺。命中：5（1d6+2）闪电伤害。"
      },
      {
        "name": "麻痹气体",
        "en_name": "Paralysis Gas",
        "description": "体质豁免检定：DC11，30尺锥状区域内的每名生物。失败：目标陷入麻痹状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。",
        "params": "充能5~6"
      }
    ],
    "source_file": "构装\\魔冢\\魔冢·五元冢.htm"
  },
  {
    "name": "魔冢·单元冢",
    "en_name": "Modron Monodrone",
    "type_line": "中型构装，守序中立",
    "size": "Medium",
    "creature_type": "构装",
    "alignment": "守序中立",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 5,
    "hp_formula": "1d8+1",
    "speed": {
      "walk": "30尺，飞行30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 4,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "damage_immunities": [
      "魅惑"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 10
    },
    "languages": "魔冢语",
    "cr": "1/8",
    "xp": 25,
    "pb": 2,
    "traits": [
      {
        "name": "解体",
        "en_name": "Disintergration",
        "description": "若魔冢死亡，其解体为尘埃，留下其着装或携带的任何东西。"
      }
    ],
    "actions": [
      {
        "name": "齿轮机关",
        "en_name": "Gear",
        "description": "近战攻击检定：+4，触及5尺。命中：6（1d8+2）力场伤害。"
      },
      {
        "name": "齿轮投射器",
        "en_name": "Gear Flinger",
        "description": "远程攻击检定：+4，射程120尺。命中：6（1d8+2）力场伤害。"
      }
    ],
    "source_file": "构装\\魔冢\\魔冢·单元冢.htm"
  },
  {
    "name": "魔冢·四元冢",
    "en_name": "Modron Quadrone",
    "type_line": "中型构装，守序中立",
    "size": "Medium",
    "creature_type": "构装",
    "alignment": "守序中立",
    "ac": 16,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 22,
    "hp_formula": "4d8+4",
    "speed": {
      "walk": "30尺，飞行30尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 2
    },
    "damage_immunities": [
      "魅惑"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 12
    },
    "languages": "魔冢语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "解体",
        "en_name": "Disintergration",
        "description": "若魔冢死亡，其解体为尘埃，留下其着装或携带的任何东西。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "魔冢发动四次猛击攻击或四次齿轮发射器攻击。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+4，触及5尺。命中：4（1d4+2）力场伤害。"
      },
      {
        "name": "齿轮发射器",
        "en_name": "Gears Launcher",
        "description": "远程攻击检定：+4，射程320尺。命中：4（1d4+2）力场伤害。"
      }
    ],
    "source_file": "构装\\魔冢\\魔冢·四元冢.htm"
  },
  {
    "name": "熊人",
    "en_name": "Werebear",
    "type_line": "中型或小型怪兽（兽化人），中立善良",
    "size": "Medium",
    "creature_type": "或小型怪兽（兽化人）",
    "alignment": "中立善良",
    "ac": 15,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 135,
    "hp_formula": "18d8+54",
    "speed": {
      "walk": "30尺，40尺（仅熊形态），攀爬30尺（仅熊形态）"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "察觉": 7
    },
    "equipment": "手斧（4）",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 17
    },
    "languages": "通用语（熊形态不能说话）",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "熊人使用撕裂或手斧发动共计两次攻击。其可以将其中一次攻击替换为一次啃咬攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+7，触及5尺。命中：17（2d12+4）穿刺伤害。若目标是类人生物，则其承受以下效应。",
        "params": "仅熊与混合形态"
      },
      {
        "name": "熊人",
        "en_name": "Werebear",
        "description": "成功：目标在24小时内免疫此熊人的诅咒。"
      },
      {
        "name": "手斧",
        "en_name": "Handaxe",
        "description": "近战或远程攻击检定：+7，触及5尺或射程20/60尺。命中：14（3d6+4）挥砍伤害。",
        "params": "仅类人与混合形态"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+7，触及5尺。命中：13（2d8+4）挥砍伤害。",
        "params": "仅熊与混合形态"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "熊人变形为类人与熊的混合形态（大型），或熊形态（大型），或变回其真实的人形态。除体型以外，其各形态下游戏数据均相同。熊人着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "怪兽\\兽化人\\熊人.htm"
  },
  {
    "name": "狼人",
    "en_name": "Werewolf",
    "type_line": "中型或小型怪兽（兽化人），混乱邪恶",
    "size": "Medium",
    "creature_type": "或小型怪兽（兽化人）",
    "alignment": "混乱邪恶",
    "ac": 15,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 71,
    "hp_formula": "11d8+22",
    "speed": {
      "walk": "30尺，40尺（仅狼形态）"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 4
    },
    "equipment": "长弓",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 14
    },
    "languages": "通用语（狼形态不能说话）",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "集群战术",
        "en_name": "Pack Tactics",
        "description": "若狼人的攻击目标生物5尺内存在有至少一名狼人未失能的盟友，则狼人对该生物进行的攻击检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "狼人使用抓挠或长弓发动共计两次攻击。其可以将其中一次攻击替换为一次啃咬攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：12（2d8+3）穿刺伤害。若目标是类人生物，则其承受以下效应。",
        "params": "仅狼与混合形态"
      },
      {
        "name": "狼人",
        "en_name": "Werewolf",
        "description": "成功：目标在24小时内免疫此狼人的诅咒。"
      },
      {
        "name": "抓挠",
        "en_name": "Scratch",
        "description": "近战攻击检定：+5，触及5尺。命中：10（2d6+3）挥砍伤害。"
      },
      {
        "name": "长弓",
        "en_name": "Longbow",
        "description": "远程攻击检定：+4，射程150/600尺。命中：11（2d8+2）穿刺伤害。",
        "params": "仅类人与混合形态"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "狼人变形为类人与狼的混合形态（大型），或狼形态（中型），或变回其真实的类人形态。除体型以外，其各形态下游戏数据均相同。狼人着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "怪兽\\兽化人\\狼人.htm"
  },
  {
    "name": "虎人",
    "en_name": "Weretiger",
    "type_line": "中型或小型怪兽（兽化人），中立",
    "size": "Medium",
    "creature_type": "或小型怪兽（兽化人）",
    "alignment": "中立",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 120,
    "hp_formula": "16d8+48",
    "speed": {
      "walk": "30尺，40尺（仅虎形态）"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 5,
      "隐匿": 4
    },
    "equipment": "长弓",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 15
    },
    "languages": "通用语（虎形态不能说话）",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "虎人使用抓挠或长弓发动共计两次攻击。其可以将其中一次攻击替换为一次啃咬攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：12（2d8+3）穿刺伤害，若目标是类人生物，则其受到下述效应。",
        "params": "仅虎与混合形态"
      },
      {
        "name": "虎人",
        "en_name": "Weretiger",
        "description": "成功：目标在24小时内免疫此虎人的诅咒。"
      },
      {
        "name": "抓挠",
        "en_name": "Scratch",
        "description": "近战攻击检定：+5，触及5尺。命中：10（2d6+3）挥砍伤害。"
      },
      {
        "name": "长弓",
        "en_name": "Longbow",
        "description": "远程攻击检定：+4，射程150/600尺。命中：11（2d8+2）穿刺伤害。",
        "params": "仅类人与混合形态"
      }
    ],
    "bonus_actions": [
      {
        "name": "潜步",
        "en_name": "Prowl",
        "description": "虎人移动至多等于其速度一半的距离且不会引发借机攻击。虎人可以在此次移动结束时执行躲藏动作。"
      },
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "虎人变形为类人与虎的混合形态（大型），或虎形态（大型），或变回其真实的类人形态。除体型以外，其各形态下游戏数据均相同。虎人着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "怪兽\\兽化人\\虎人.htm"
  },
  {
    "name": "野猪人",
    "en_name": "Wereboar",
    "type_line": "中型或小型怪兽（兽化人），中立邪恶",
    "size": "Medium",
    "creature_type": "或小型怪兽（兽化人）",
    "alignment": "中立邪恶",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 97,
    "hp_formula": "15d8+30",
    "speed": {
      "walk": "30尺，40尺（仅野猪形态）"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 2
    },
    "equipment": "标枪（6）",
    "senses": {
      "被动察觉": 12
    },
    "languages": "通用语（野猪形态不能说话）",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "野猪人使用标枪或獠牙发动共计两次攻击。其可以将其中一次攻击替换为一次抵刺攻击。"
      },
      {
        "name": "抵刺",
        "en_name": "Gore",
        "description": "近战攻击检定：+5，触及5尺。命中：12（2d8+3）穿刺伤害。若目标是类人生物，则其承受以下效应。",
        "params": "仅野猪与混合形态"
      },
      {
        "name": "野猪人",
        "en_name": "Wereboar",
        "description": "成功：目标在24小时内免疫此野猪人的诅咒。"
      },
      {
        "name": "标枪",
        "en_name": "Javelin",
        "description": "近战或远程攻击检定：+5，触及5尺或射程30/120尺。命中：13（3d6+3）穿刺伤害。",
        "params": "仅类人与混合形态"
      },
      {
        "name": "獠牙",
        "en_name": "Tusk",
        "description": "近战攻击检定：+5，触及5尺。命中：10（2d6+3）穿刺伤害。若野猪人在此次攻击前立即向着目标直线移动了20+尺，且目标生物体型不超过中型，则目标额外受到7（2d6）穿刺伤害且陷入倒地状态。",
        "params": "仅野猪与混合形态"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "野猪人变形为类人与猪的混合形态（中型），或野猪形态（小型），或变回其真实的类人形态。除体型以外，其各形态下游戏数据均相同。野猪人着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "怪兽\\兽化人\\野猪人.htm"
  },
  {
    "name": "鼠人",
    "en_name": "Wererat",
    "type_line": "中型或小型怪兽（兽化人），中立邪恶",
    "size": "Medium",
    "creature_type": "或小型怪兽（兽化人）",
    "alignment": "中立邪恶",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 60,
    "hp_formula": "11d8+11",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 5
    },
    "equipment": "手弩",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 14
    },
    "languages": "通用语（鼠形态不能说话）",
    "cr": 2,
    "xp": 250,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鼠人使用抓挠或手弩发动共计两次攻击。其可以将其中一次攻击替换为一次啃咬攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：8（2d4+3）穿刺伤害。若目标是类人生物，则其承受以下效应。",
        "params": "仅鼠与混合形态"
      },
      {
        "name": "抓挠",
        "en_name": "Scratch",
        "description": "近战攻击检定：+5，触及5尺。命中：6（1d6+3）挥砍伤害。"
      },
      {
        "name": "手弩",
        "en_name": "Hand Crossbow",
        "description": "远程攻击检定：+5，射程30/120尺。命中：6（1d6+3）穿刺伤害。",
        "params": "仅限类人与混合形态"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "鼠人变形为类人与鼠的混合形态（中型），或鼠形态（小型），或变回其真实的类人形态。除体型以外，其各形态下游戏数据均相同。鼠人着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "怪兽\\兽化人\\鼠人.htm"
  },
  {
    "name": "幽邃熊怪",
    "en_name": "Quaggoth",
    "type_line": "中型怪兽，混乱邪恶",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "混乱邪恶",
    "ac": 13,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 45,
    "hp_formula": "6d8+18",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "运动": 5
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 11
    },
    "languages": "地底通用语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "浴血狂怒",
        "en_name": "Bloodied Fury",
        "description": "幽邃熊怪在浴血期间进行的攻击检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "幽邃熊怪发动两次爪击攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+5，触及5尺。命中：6（1d6+3）挥砍伤害，若幽邃熊怪处于浴血则改为13（3d6+3）挥砍伤害。"
      }
    ],
    "source_file": "怪兽\\幽邃熊怪\\幽邃熊怪.htm"
  },
  {
    "name": "幽邃熊怪脑头",
    "en_name": "Quaggoth Thonot",
    "type_line": "中型怪兽，混乱邪恶",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "混乱邪恶",
    "ac": 15,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 67,
    "hp_formula": "9d8+27",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "运动": 5
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 12
    },
    "languages": "地底通用语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "浴血狂怒",
        "en_name": "Bloodied Fury",
        "description": "幽邃熊怪在浴血期间进行的攻击检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "幽邃熊怪发动两次爪击攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+5，触及5尺。命中：6（1d6+3）挥砍伤害外加5（2d4）心灵伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "幽邃熊怪施展以下一道法术，无需法术成分并使用感知作为施法属性（法术豁免DC12）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "法师之手Mage Hand（手是隐形的）， 次级幻象Minor Illusion"
      },
      {
        "name": "2/日：",
        "en_name": "",
        "description": "心灵尖刺Mind Spike"
      }
    ],
    "reactions": [
      {
        "name": "灵能防守（3/日）",
        "en_name": "Psionic Defense",
        "description": "幽邃熊怪施展羽落术Feather \n或护盾术Shield（触发条件见这些法术），无需任术成分并使用与施法动作相同的施法属性。"
      }
    ],
    "source_file": "怪兽\\幽邃熊怪\\幽邃熊怪脑头.htm"
  },
  {
    "name": "巨斧嘴鸟",
    "en_name": "Giant Axe Beak",
    "type_line": "巨型怪兽，无阵营",
    "size": "Huge",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 15,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 84,
    "hp_formula": "8d12+32",
    "speed": {
      "walk": "50尺"
    },
    "abilities": {
      "力量": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "skills": {
      "察觉": 4
    },
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "斧嘴鸟发动一次锋喙攻击和一次禽爪攻击。"
      },
      {
        "name": "锋喙",
        "en_name": "Sharpened Beak",
        "description": "近战攻击检定：+8，触及10尺。命中：18（2d12+5）挥砍伤害，且位于目标5尺内的由斧嘴鸟选择的一名生物受到6（1d12）挥砍伤害。"
      },
      {
        "name": "禽爪",
        "en_name": "Talons",
        "description": "近战攻击检定：+8，触及5尺。命中：14（2d8+5）挥砍伤害。若目标生物体型不超过大型，则其陷入倒地状态。"
      }
    ],
    "source_file": "怪兽\\斧嘴鸟\\巨斧嘴鸟.htm"
  },
  {
    "name": "斧嘴鸟",
    "en_name": "Axe Beak",
    "type_line": "大型怪兽，无阵营",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 11,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 19,
    "hp_formula": "3d10+3",
    "speed": {
      "walk": "50尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "senses": {
      "被动察觉": 10
    },
    "languages": "无",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "actions": [
      {
        "name": "喙击",
        "en_name": "Beak",
        "description": "近战攻击检定：+4，触及5尺。命中：6（1d8+2）挥砍伤害。"
      }
    ],
    "source_file": "怪兽\\斧嘴鸟\\斧嘴鸟.htm"
  },
  {
    "name": "原初枭熊",
    "en_name": "Primeval Owlbear",
    "type_line": "巨型怪兽，无阵营",
    "size": "Huge",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 16,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 126,
    "hp_formula": "12d12+48",
    "speed": {
      "walk": "40尺，攀爬 40尺，飞行5尺"
    },
    "abilities": {
      "力量": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 19,
        "mod": 4,
        "save": 7
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 5
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 8
    },
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 18
    },
    "languages": "无",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "枭熊对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "枭熊发动两次蹂躏攻击。"
      },
      {
        "name": "蹂躏",
        "en_name": "Ravage",
        "description": "近战攻击检定：+9，触及5尺。\n命中：15（2d8+6）挥砍伤害。若枭熊在此次攻击前立即向着目标直线移动了20+尺，且目标生物体型不超过巨型，则目标额外受到9（2d8）挥砍伤害并陷入倒地状态。"
      },
      {
        "name": "戾啸",
        "en_name": "Screech",
        "description": "体质豁免检定：DC15，源自枭熊的30尺光环区域内的每名生物。\n失败：27（6d8）雷鸣伤害，目标陷入失能状态直至其下个回合结束。\n成功：仅半伤。",
        "params": "充能5~6"
      }
    ],
    "source_file": "怪兽\\枭熊\\原初枭熊.htm"
  },
  {
    "name": "枭熊",
    "en_name": "Owlbear",
    "type_line": "大型怪兽，无阵营",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 13,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 59,
    "hp_formula": "7d10+21",
    "speed": {
      "walk": "40尺，攀爬 40尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 5
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 15
    },
    "languages": "无",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "枭熊发动两次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+7，触及5尺。\n命中：14（2d8+5）挥砍伤害。"
      }
    ],
    "source_file": "怪兽\\枭熊\\枭熊.htm"
  },
  {
    "name": "百足魔兽",
    "en_name": "Remorhaz",
    "type_line": "巨型怪兽，无阵营",
    "size": "Huge",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 17,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 195,
    "hp_formula": "17d12+85",
    "speed": {
      "walk": "40尺，掘穴30尺"
    },
    "abilities": {
      "力量": {
        "score": 24,
        "mod": 7,
        "save": 7
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 4,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "damage_immunities": [
      "寒冷、火焰"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "无",
    "cr": 11,
    "xp": 7200,
    "pb": 4,
    "traits": [
      {
        "name": "炽热灵光",
        "en_name": "Heat Aura",
        "description": "百足魔兽回合结束时，位于源自百足魔兽5尺光环区域内的每名生物均受到16（3d10）火焰伤害。"
      }
    ],
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+11，触及10尺。命中：18（2d10+7）穿刺伤害外加14（4d6）火焰伤害。若目标生物体型不超过大型，其陷入受擒状态（逃脱DC17），且目标陷入束缚状态直至擒抱结束。"
      }
    ],
    "bonus_actions": [
      {
        "name": "吞咽",
        "en_name": "Swallow",
        "description": "敏捷豁免检定：DC19，单一不超过大型的正受擒于百足魔兽的生物（百足魔兽同时能吞咽的生物数上限为二）。失败：百足魔兽吞咽目标，并结束其受擒状态。被吞咽期间，目标陷入目盲和束缚状态，对百足魔兽体外的攻击或其他效应而言处于全身掩护，并在百足魔兽的回合开始时受到10（3d6）强酸伤害加10（3d6）火焰伤害。"
      }
    ],
    "source_file": "怪兽\\百足魔兽\\百足魔兽.htm"
  },
  {
    "name": "青年百足魔兽",
    "en_name": "Young Remorhaz",
    "type_line": "大型怪兽，无阵营",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 14,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 93,
    "hp_formula": "11d10+33",
    "speed": {
      "walk": "30尺，掘穴20尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 4,
        "mod": -3,
        "save": -3
      }
    },
    "damage_immunities": [
      "寒冷、火焰"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "无",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "炽热灵光",
        "en_name": "Heat Aura",
        "description": "百足魔兽回合结束时，位于源自百足魔兽5尺光环区域内的每名生物均受到11（2d10）火焰伤害。"
      }
    ],
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+7，触及5尺。命中：15（2d10+4）穿刺伤害外加13（3d8）火焰伤害。"
      }
    ],
    "source_file": "怪兽\\百足魔兽\\青年百足魔兽.htm"
  },
  {
    "name": "蚊蝠",
    "en_name": "Stirge",
    "type_line": "微型怪兽，无阵营",
    "size": "Tiny",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 5,
    "hp_formula": "2d4",
    "speed": {
      "walk": "10尺，飞行40尺"
    },
    "abilities": {
      "力量": {
        "score": 4,
        "mod": -3,
        "save": -3
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "无",
    "cr": "1/8",
    "xp": 25,
    "pb": 2,
    "actions": [
      {
        "name": "长喙",
        "en_name": "Proboscis",
        "description": "近战攻击检定：+5，触及5尺。命中：6（1d6+3）穿刺伤害，且蚊蝠会吸附在目标身上。蚊蝠吸附期间，其无法发动长喙攻击，且目标在蚊蝠回合开始时受到5（2d4）暗蚀伤害。"
      }
    ],
    "source_file": "怪兽\\蚊蝠\\蚊蝠.htm"
  },
  {
    "name": "蚊蝠集群",
    "en_name": "Swarm of Stirges",
    "type_line": "微型怪兽的中型集群，无阵营",
    "size": "Tiny",
    "creature_type": "怪兽的中型集群",
    "alignment": "无阵营",
    "ac": 14,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 36,
    "hp_formula": "8d8",
    "speed": {
      "walk": "10尺，飞行40尺"
    },
    "abilities": {
      "力量": {
        "score": 4,
        "mod": -3,
        "save": -3
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "damage_resistances": [
      "钝击",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "魅惑",
      "恐慌",
      "受擒",
      "麻痹",
      "石化",
      "倒地",
      "束缚",
      "震慑"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "无",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "集群",
        "en_name": "Swarm",
        "description": "蚊蝠集群可以进驻另一生物身处的空间，反之亦然。而且蚊蝠集群可以通过任何足够一只微型生物通过的通道。蚊蝠集群不能恢复生命值也不能获得临时生命值。"
      }
    ],
    "actions": [
      {
        "name": "喙群",
        "en_name": "Swarm of Proboscises",
        "description": "近战攻击检定：+5，触及5尺。命中：14（2d10+3）穿刺伤害，若蚊蝠集群处于浴血则改为8（1d10+3）穿刺伤害。若目标生物体型不超过中型且位于蚊蝠集群所在空间，则目标陷入受擒状态（逃脱DC13）。目标在其回合结束时受到7（2d6）暗蚀伤害，直至擒抱结束。"
      }
    ],
    "source_file": "怪兽\\蚊蝠\\蚊蝠集群.htm"
  },
  {
    "name": "恶咒蛇人（1型）Yuan-ti Malison （Type 1）",
    "en_name": "",
    "type_line": "中型怪兽，中立邪恶",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "中立邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 66,
    "hp_formula": "12d8+12",
    "speed": {
      "walk": "30尺，攀爬30尺（仅蛇形态）"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "隐匿": 4
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 13
    },
    "languages": "深渊语，通用语，龙语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "蛇人对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蛇人使用啃咬或毒素射线发动共计两次攻击，并使用施法施展暗示术Suggestion（若条件允许）。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：5（1d4+3）穿刺伤害外加7（2d6）毒素伤害。"
      },
      {
        "name": "毒素射线",
        "en_name": "Poison Ray",
        "description": "远程攻击检定：+5，射程120尺。命中：12（2d8+3）毒素伤害。",
        "params": "仅蛇人形态"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "蛇人施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC13）：",
        "params": "仅蛇人形态"
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "化兽为友Animal Friendship（仅蛇）"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "暗示术Suggestion"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "蛇人变形为中型的蛇，或变回其真实形态。若其死亡，则其保持在当前的形态不变。除注明部分外，其各形态下游戏数据均相同。蛇人着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "怪兽\\蛇人\\恶咒蛇人（1型）.htm"
  },
  {
    "name": "恶咒蛇人（2型）Yuan-ti Malison （Type 2）",
    "en_name": "",
    "type_line": "中型怪兽，中立邪恶",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "中立邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 66,
    "hp_formula": "12d8+12",
    "speed": {
      "walk": "30尺，攀爬30尺（仅蛇形态）"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "隐匿": 4
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 13
    },
    "languages": "深渊语，通用语，龙语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "蛇人对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蛇人发动两次啃咬攻击，并使用施法施展暗示术Suggestion（若条件允许）。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：7（1d8+3）穿刺伤害外加7（2d6）毒素伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "蛇人施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC13）：",
        "params": "仅蛇人形态"
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "化兽为友Animal Friendship（仅蛇）"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "暗示术Suggestion"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "蛇人变形为中型的蛇，或变回其真实形态。若其死亡，则其保持在当前的形态不变。除注明部分外，其各形态下游戏数据均相同。蛇人着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "怪兽\\蛇人\\恶咒蛇人（2型）.htm"
  },
  {
    "name": "恶咒蛇人（3型）Yuan-ti Malison （Type 3）",
    "en_name": "",
    "type_line": "中型怪兽，中立邪恶",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "中立邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 66,
    "hp_formula": "12d8+12",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "隐匿": 4
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 13
    },
    "languages": "深渊语，通用语，龙语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "蛇人对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蛇人发动两次毒素迸发攻击，并使用施法施展暗示术Suggestion（若条件允许）。"
      },
      {
        "name": "毒素迸发",
        "en_name": "Poison Burst",
        "description": "近战或远程攻击检定：+5，触及5尺或射程120尺。命中：12（2d8+3）毒素伤害。",
        "params": "仅蛇人形态"
      },
      {
        "name": "绞缠",
        "en_name": "Constrict",
        "description": "力量豁免检定：DC13，单一5尺内不超过中型的生物。失败：21（4d8+3）钝击伤害。目标陷入受擒状态（逃脱DC13），且目标陷入束缚状态直至擒抱结束。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "该蛇人施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC13）：",
        "params": "仅蛇人形态"
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "化兽为友Animal Friendship（仅蛇）"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "暗示术Suggestion"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "蛇人变形为中型的蛇，或变回其真实形态。若其死亡，则其保持在当前的形态不变。除注明部分外，其各形态下游戏数据均相同。蛇人着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "怪兽\\蛇人\\恶咒蛇人（3型）.htm"
  },
  {
    "name": "憎恶蛇人",
    "en_name": "Yuan-ti Abomination",
    "type_line": "大型怪兽，中立邪恶",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "中立邪恶",
    "ac": 15,
    "initiative_bonus": 6,
    "initiative_total": 16,
    "hp": 127,
    "hp_formula": "15d10+45",
    "speed": {
      "walk": "40尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 7,
      "隐匿": 6
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 17
    },
    "languages": "深渊语，通用语，龙语",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "蛇人对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蛇人发动两次啃咬攻击，并使用施法施展暗示术Suggestion（若条件允许）。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+7，触及5尺。命中：11（2d6+4）穿刺伤害加10（3d6）毒素伤害。"
      },
      {
        "name": "绞缠",
        "en_name": "Constrict",
        "description": "力量豁免检定：DC15，单一5尺内不超过大型的生物。失败：28（7d6+4）钝击伤害。目标陷入受擒状态（逃脱DC14），且目标陷入束缚状态直至擒抱结束。成功：仅半伤。"
      },
      {
        "name": "毒气喷涌",
        "en_name": "Poison Spray",
        "description": "体质豁免检定：DC14，30尺锥状区域内的每名生物。失败：21（6d6）毒素伤害，且目标陷入中毒状态直至蛇人的下个回合结束。中毒期间，目标陷入目盲状态。成功：仅半伤。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "该人施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC15）：",
        "params": "仅蛇人形态"
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "化兽为友Animal Friendship（仅蛇）"
      },
      {
        "name": "每项3/日：",
        "en_name": "",
        "description": "暗示术Suggestion"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "蛇人变形为大型的蛇，或变回其真实形态。若其死亡，则其保持在当前的形态不变。除注明部分外，其各形态下游戏数据均相同。蛇人着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "怪兽\\蛇人\\憎恶蛇人.htm"
  },
  {
    "name": "渗蚀蛇人",
    "en_name": "Yuan-ti Infiltrator",
    "type_line": "中型怪兽，中立邪恶",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "中立邪恶",
    "ac": 11,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 40,
    "hp_formula": "9d8",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "欺瞒": 5,
      "察觉": 4,
      "隐匿": 3
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "equipment": "弯刀",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 14
    },
    "languages": "深渊语，通用语，龙语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "蛇人对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蛇人发动两次弯刀攻击。"
      },
      {
        "name": "弯刀",
        "en_name": "Scimitar",
        "description": "近战攻击检定：+3，触及5尺。命中：4（1d6+1）挥砍伤害。"
      },
      {
        "name": "毒素射线",
        "en_name": "Poison Ray",
        "description": "远程攻击检定：+4，射程120尺。命中：9（2d6+2）毒素伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "蛇人施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC12）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "化兽为友Animal Friendship（仅蛇）"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "暗示术Suggestion"
      }
    ],
    "source_file": "怪兽\\蛇人\\渗蚀蛇人.htm"
  },
  {
    "name": "蛇鸡",
    "en_name": "Cockatrice",
    "type_line": "小型怪兽，无阵营",
    "size": "Small",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 11,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 22,
    "speed": {
      "walk": "20尺，飞行40尺"
    },
    "abilities": {
      "力量": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "damage_immunities": [
      "石化"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "无",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "actions": [
      {
        "name": "石化啄咬",
        "en_name": "Petrifying Bite",
        "description": "近战攻击检定：+3，触及5尺"
      }
    ],
    "source_file": "怪兽\\蛇鸡\\蛇鸡.htm"
  },
  {
    "name": "蛇鸡王",
    "en_name": "Cockatrice Regent",
    "type_line": "大型怪兽，无阵营",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 136,
    "speed": {
      "walk": "30尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "damage_immunities": [
      "石化"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 13
    },
    "languages": "无",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "traits": [
      {
        "name": "飞掠",
        "en_name": "Flyby",
        "description": "蛇鸡王飞行离开敌人的触及范围时不会引发借机攻击。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蛇鸡王发动一次石化啄咬攻击和两次禽爪攻击。"
      },
      {
        "name": "石化啄咬",
        "en_name": "Petrifying Bite",
        "description": "近战攻击检定：+7，触及5尺。\n命中：13（2d8+4）穿刺伤害，若目标为生物，承受以下效应。"
      },
      {
        "name": "禽爪",
        "en_name": "Talons",
        "description": "近战攻击检定：+7，触及5尺。\n命中：18（4d6+4）挥砍伤害。"
      }
    ],
    "reactions": [
      {
        "name": "魔法反弹",
        "en_name": "Magical Backlash",
        "description": "触发：一名位于蛇鸡王120尺内的生物对其造成伤害。响应-敏捷豁免检定：DC14，触发生物。\n失败：13（3d6+3）力场伤害。"
      }
    ],
    "source_file": "怪兽\\蛇鸡\\蛇鸡王.htm"
  },
  {
    "name": "螳螂人劫掠者",
    "en_name": "Thri-kreen Marauder",
    "type_line": "中型怪兽，中立",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "中立",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 33,
    "hp_formula": "6d8+6",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 3,
      "隐匿": 4,
      "求生": 3
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 13
    },
    "languages": "螳螂人语；心灵感应60尺",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "螳螂人使用螳螂戟或三刃镖发动共计两次攻击。"
      },
      {
        "name": "螳螂戟",
        "en_name": "Gythka",
        "description": "近战攻击检定：+3，触及5尺。命中：5（1d8+1）挥砍伤害外加2（1d4）毒素伤害。"
      },
      {
        "name": "三刃镖",
        "en_name": "Chatkcha",
        "description": "远程攻击检定：+4，射程30/120尺。命中：5（1d6+2）挥砍伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "飞跃",
        "en_name": "Leap",
        "description": "螳螂人消耗5尺移动力跳跃至多15尺。"
      }
    ],
    "source_file": "怪兽\\螳螂人\\螳螂人劫掠者.htm"
  },
  {
    "name": "螳螂人灵能使",
    "en_name": "Thri-kreen Psion",
    "type_line": "中型怪兽，中立",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "中立",
    "ac": 16,
    "initiative_bonus": 6,
    "initiative_total": 16,
    "hp": 149,
    "hp_formula": "23d8+46",
    "speed": {
      "walk": "40尺，飞行20尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 5
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "智力": {
        "score": 19,
        "mod": 4,
        "save": 7
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 8
    },
    "damage_resistances": [
      "心灵"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 14
    },
    "languages": "螳螂人语；心灵感应120尺",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "螳螂人发动三次灵能长枪攻击。"
      },
      {
        "name": "灵能长枪",
        "en_name": "Psionic Lance",
        "description": "近战或远程攻击检定：+7，触及5尺或射程120尺。命中：18（4d6+4）心灵伤害"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "螳螂人施展以下一道法术，无需法术成分并使用智力作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "法师之手Mage Hand（手是隐形的）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "侦测思想Detect Thought，短讯术Sending，突触静止Synaptic Static"
      }
    ],
    "source_file": "怪兽\\螳螂人\\螳螂人灵能使.htm"
  },
  {
    "name": "巨恶雪怪",
    "en_name": "Abominable Yeti",
    "type_line": "巨型怪兽，混乱邪恶",
    "size": "Huge",
    "creature_type": "怪兽",
    "alignment": "混乱邪恶",
    "ac": 15,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 137,
    "hp_formula": "11d12+66",
    "speed": {
      "walk": "40尺，攀爬40尺"
    },
    "abilities": {
      "力量": {
        "score": 24,
        "mod": 7,
        "save": 7
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 9,
      "隐匿": 8
    },
    "damage_immunities": [
      "寒冷"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 19
    },
    "languages": "雪怪语",
    "cr": 9,
    "xp": 5000,
    "pb": 4,
    "traits": [
      {
        "name": "畏火",
        "en_name": "Fear of Fire",
        "description": "若雪怪受到火焰伤害，直至其下个回合结束，其进行的攻击检定和属性检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "雪怪使用寒颤凝视并使用爪击或投掷冰块发动共计两次攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+11，触及5尺。命中：14（2d6+7）挥砍伤害外加7（2d6）寒冷伤害。"
      },
      {
        "name": "投掷冰块",
        "en_name": "Ice Throw",
        "description": "远程攻击检定：+11，射程60/240尺。命中：12（2d4+7）钝击伤害外加7（2d6）寒冷伤害。"
      },
      {
        "name": "寒颤凝视",
        "en_name": "Chilling Gaze",
        "description": "体质豁免检定：DC18，单一30尺内雪怪可见的生物。失败： 21（6d6）寒冷伤害，且目标陷入麻痹状态（除非目标对寒冷伤害免疫），直至雪怪的下个回合开始。成功：目标在1小时内免疫此雪怪的寒颤凝视。"
      },
      {
        "name": "寒气吐息",
        "en_name": "Cold Breath",
        "description": "体质豁免检定：DC18，30尺锥状区域内的每名生物。失败： 45（10d8）寒冷伤害。成功：半伤。",
        "params": "充能6"
      }
    ],
    "source_file": "怪兽\\雪怪\\巨恶雪怪.htm"
  },
  {
    "name": "雪怪",
    "en_name": "Yeti",
    "type_line": "大型怪兽，混乱邪恶",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "混乱邪恶",
    "ac": 12,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 51,
    "hp_formula": "6d10+18",
    "speed": {
      "walk": "40尺，攀爬40尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 5,
      "隐匿": 5
    },
    "damage_immunities": [
      "寒冷"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 15
    },
    "languages": "雪怪语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "畏火",
        "en_name": "Fear of Fire",
        "description": "若雪怪受到火焰伤害，直至其下个回合结束，其进行的攻击检定和属性检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "雪怪使用寒颤凝视并使用爪击或投掷冰块发动共计两次攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+6，触及5尺。命中：7（1d6+4）挥砍伤害外加3（1d6）寒冷伤害。"
      },
      {
        "name": "投掷冰块",
        "en_name": "Ice Throw",
        "description": "远程攻击检定：+6，射程30/120尺。命中：6（1d4+4）钝击伤害外加2（1d4）寒冷伤害。"
      },
      {
        "name": "寒颤凝视",
        "en_name": "Chilling Gaze",
        "description": "体质豁免检定：DC13，单一30尺内雪怪可见的生物。失败： 5（2d4）寒冷伤害，且目标陷入麻痹状态（除非目标对寒冷伤害免疫），直至雪怪的下个回合开始。成功：目标在1小时内免疫所有雪怪（除巨恶雪怪外）的寒颤凝视。"
      }
    ],
    "source_file": "怪兽\\雪怪\\雪怪.htm"
  },
  {
    "name": "鲨蜥",
    "en_name": "Bulette",
    "type_line": "大型怪兽，无阵营",
    "size": "Large",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 17,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 94,
    "speed": {
      "walk": "40尺，掘地40尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "skills": {
      "察觉": 6
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 16
    },
    "languages": "无",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鲨蜥发动两次啃咬攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+7，触及5尺。命中：17（2d12+4）穿刺伤害。"
      },
      {
        "name": "鲨戮强跃",
        "en_name": "Deadly Leap",
        "description": "鲨蜥消耗5尺移动力跳跃至15尺内的一处空间，空间内需包含至少一名体型不超过大型的生物。敏捷豁免检定：DC15，鲨蜥目标空间内的每名生物。失败：19（3d12）钝击伤害，目标陷入倒地状态。成功：半伤，目标被推离鲨蜥5尺。"
      }
    ],
    "bonus_actions": [
      {
        "name": "强跃",
        "en_name": "Leap",
        "description": "鲨蜥消耗10尺移动力跳跃至多30尺。"
      }
    ],
    "source_file": "怪兽\\鲨蜥\\鲨蜥.htm"
  },
  {
    "name": "鲨蜥仔",
    "en_name": "Bulette Pup",
    "type_line": "中型怪兽，无阵营",
    "size": "Medium",
    "creature_type": "怪兽",
    "alignment": "无阵营",
    "ac": 16,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 45,
    "speed": {
      "walk": "30尺，掘地20尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 4,
        "mod": -3,
        "save": -3
      }
    },
    "skills": {
      "察觉": 4
    },
    "senses": {
      "黑暗视觉": 30,
      "被动察觉": 14
    },
    "languages": "无",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：14（2d10+3）穿刺伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "强跃",
        "en_name": "Leap",
        "description": "鲨蜥消耗10尺移动力跳跃至多30尺。"
      }
    ],
    "source_file": "怪兽\\鲨蜥\\鲨蜥仔.htm"
  },
  {
    "name": "史拉亡蟾",
    "en_name": "Death Slaad",
    "type_line": "中型异怪，混乱邪恶",
    "size": "Medium",
    "creature_type": "异怪",
    "alignment": "混乱邪恶",
    "ac": 18,
    "initiative_bonus": 10,
    "initiative_total": 20,
    "hp": 178,
    "hp_formula": "21d8+84",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 19,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "奥秘": 6,
      "察觉": 8
    },
    "damage_resistances": [
      "强酸",
      "寒冷",
      "火焰",
      "闪电",
      "雷鸣"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 18
    },
    "languages": "通用语，史拉蟾语；心灵感应60尺",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic \nResistance",
        "description": "史拉蟾对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "再生",
        "en_name": "Regeneration",
        "description": "若史拉蟾至少拥有1生命值，则其在自己回合开始时回复10生命值。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "史拉蟾发动两次混沌刃锋攻击。"
      },
      {
        "name": "混沌刃锋",
        "en_name": "Chaos Blade",
        "description": "近战攻击检定：+9，触及10尺。命中：11（1d12+5）挥砍伤害外加10（3d6）暗蚀伤害。目标陷入某种状态直至史拉蟾的下个回合开始，掷1d4决定：1，魅惑；2，恐慌；3，中毒；4，失能。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "史拉蟾施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC16）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，侦测思想Detect Thoughts，隐形术Invisibility（仅自身），  法师之手Mage Hand，高级幻影Major Image"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "枯萎术Blight（八环版本）， 死云术Cloudkill（八环版本），飞行术Fly，位面转移Plane Shift，巧言术Tongues"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "史拉蟾变形为小型或中型的类人生物，或变回其真实形态。除体型以外，其各形态下游戏数据均相同。史拉蟾着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "异怪\\史拉蟾\\史拉亡蟾.htm"
  },
  {
    "name": "史拉灰蟾",
    "en_name": "Gray Slaad",
    "type_line": "中型异怪，混乱中立",
    "size": "Medium",
    "creature_type": "异怪",
    "alignment": "混乱中立",
    "ac": 18,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 150,
    "hp_formula": "20d8+60",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "奥秘": 5,
      "察觉": 7
    },
    "damage_resistances": [
      "强酸",
      "寒冷",
      "火焰",
      "闪电",
      "雷鸣"
    ],
    "senses": {
      "盲视": 60,
      "被动察觉": 17
    },
    "languages": "通用语，史拉蟾语；心灵感应60尺",
    "cr": 9,
    "xp": 5000,
    "pb": 4,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic \nResistance",
        "description": "史拉蟾对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "再生",
        "en_name": "Regeneration",
        "description": "若史拉蟾至少拥有1生命值，则其在自己回合开始时回复10生命值。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "史拉蟾发动两次混沌爪击攻击。"
      },
      {
        "name": "混沌爪击",
        "en_name": "Chaos Claw",
        "description": "近战攻击检定：+8，触及10尺。命中：9（1d10+4）挥砍伤害外加11（2d10）暗蚀伤害。目标陷入某种状态直至史拉蟾的下个回合开始，掷1d4决定：1，魅惑；2，恐慌；3，中毒；4，失能。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "史拉蟾施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC16）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，侦测思想Detect Thoughts，隐形术Invisibility（仅自身），  法师之手Mage Hand，高级幻影Major Image"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "死云术Cloudkill，飞行术Fly，位面转移Plane Shift（仅自身）， 巧言术Tongues"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "史拉蟾变形为小型或中型的类人生物，或变回其真实形态。除体型以外，其各形态下游戏数据均相同。史拉蟾着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "异怪\\史拉蟾\\史拉灰蟾.htm"
  },
  {
    "name": "史拉红蟾",
    "en_name": "Red Slaad",
    "type_line": "大型异怪，混乱中立",
    "size": "Large",
    "creature_type": "异怪",
    "alignment": "混乱中立",
    "ac": 14,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 93,
    "hp_formula": "11d10+33",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 1
    },
    "damage_resistances": [
      "强酸",
      "寒冷",
      "火焰",
      "闪电",
      "雷鸣"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "史拉蟾语；心灵感应60尺",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "史拉蟾对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "再生",
        "en_name": "Regeneration",
        "description": "若史拉蟾至少拥有1生命值，则其在自己回合开始时回复10生命值。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "该史拉蟾发动三次寄生爪击攻击。"
      },
      {
        "name": "寄生爪击",
        "en_name": "Injecting Claw",
        "description": "近战攻击检定：+6，触及10尺。命中：10（2d6+3）穿刺伤害。若目标为类人且未被史拉蟾诅咒，承受以下效应。体质豁免检定：DC14。失败：目标在不知不觉间被诅咒，且一颗史拉蟾微卵被植入其肉体。移除该诅咒将会摧毁这颗卵。"
      },
      {
        "name": "史拉蟾蝌蚪",
        "en_name": "Slaad \nTadpole",
        "description": "，从宿主的体内啮食而出并将其杀死。"
      }
    ],
    "source_file": "异怪\\史拉蟾\\史拉红蟾.htm"
  },
  {
    "name": "史拉绿蟾",
    "en_name": "Green Slaad",
    "type_line": "大型异怪，混乱中立",
    "size": "Large",
    "creature_type": "异怪",
    "alignment": "混乱中立",
    "ac": 16,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 144,
    "hp_formula": "17d10+51",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "奥秘": 3,
      "察觉": 2
    },
    "damage_resistances": [
      "强酸",
      "寒冷",
      "火焰",
      "闪电",
      "雷鸣"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 12
    },
    "languages": "通用语，史拉蟾语；心灵感应60尺",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic \nResistance",
        "description": "史拉蟾对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "再生",
        "en_name": "Regeneration",
        "description": "若史拉蟾至少拥有1生命值，则其在自己回合开始时回复10生命值。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "史拉蟾发动三次混沌法杖攻击。"
      },
      {
        "name": "混沌法杖",
        "en_name": "Chaos Staff",
        "description": "近战或远程攻击检定：+7，触及10尺或射程60尺。命中：8（1d8+4）力场伤害。目标陷入某种状态直至史拉蟾的下个回合开始，掷1d4决定：1，魅惑；2，恐慌；3，中毒；4，失能。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "史拉蟾施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC14，法术攻击命中+6）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，侦测思想Detect Thoughts，法师之手Mage Hand"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "火球术Fireball，隐形术Invisibility（仅自身）"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "史拉蟾变形为小型或中型的类人生物，或变回其真实形态。除体型以外，其各形态下游戏数据均相同。史拉蟾着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "异怪\\史拉蟾\\史拉绿蟾.htm"
  },
  {
    "name": "史拉蓝蟾",
    "en_name": "Blue Slaad",
    "type_line": "大型异怪，混乱中立",
    "size": "Large",
    "creature_type": "异怪",
    "alignment": "混乱中立",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 133,
    "hp_formula": "14d10+56",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 1
    },
    "damage_resistances": [
      "强酸",
      "寒冷",
      "火焰",
      "闪电",
      "雷鸣"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "史拉蟾语；心灵感应60尺",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic \nResistance",
        "description": "史拉蟾对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "再生",
        "en_name": "Regeneration",
        "description": "若史拉蟾至少拥有1生命值，则其在自己回合开始时回复10生命值。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "该史拉蟾发动三次孽变爪击攻击。"
      },
      {
        "name": "孽变爪击",
        "en_name": "Mutating Claw",
        "description": "近战攻击检定：+8，触及10尺。命中：12（2d6+5）挥砍伤害外加3（1d6）毒素伤害。若目标为类人且未被史拉蟾诅咒，承受以下效应。体质豁免检定：DC15。失败：目标被诅咒。被诅咒的目标无法恢复生命值，且其生命值上限每过24小时便减少10（3d6），完成长休时也无法复原。若该诅咒使目标的生命值上限降至0则诅咒终止，此时目标不会死亡，而是立即转化为一只史拉红蟾Red \nSlaad。若目标可以施展三环或更高环阶的法术，则会转化为一只史拉绿蟾Green \nSlaad。只有法术祈愿术Wish法术可以逆转该变化。"
      }
    ],
    "source_file": "异怪\\史拉蟾\\史拉蓝蟾.htm"
  },
  {
    "name": "史拉蟾蝌蚪",
    "en_name": "Slaad Tadpole",
    "type_line": "微型异怪，混乱中立",
    "size": "Tiny",
    "creature_type": "异怪",
    "alignment": "混乱中立",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 7,
    "hp_formula": "3d4",
    "speed": {
      "walk": "30尺，掘穴10尺"
    },
    "abilities": {
      "力量": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "魅力": {
        "score": 3,
        "mod": -4,
        "save": -4
      }
    },
    "skills": {
      "隐匿": 4
    },
    "damage_resistances": [
      "强酸",
      "寒冷",
      "火焰",
      "闪电",
      "雷鸣"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 7
    },
    "languages": "理解史拉蟾语，但不会说",
    "cr": "1/8",
    "xp": 25,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "史拉蟾对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）穿刺伤害。"
      }
    ],
    "source_file": "异怪\\史拉蟾\\史拉蟾蝌蚪.htm"
  },
  {
    "name": "吉斯泽莱武僧",
    "en_name": "Githzerai Monk",
    "type_line": "中型异怪（吉斯人），守序中立",
    "size": "Medium",
    "creature_type": "异怪（吉斯人）",
    "alignment": "守序中立",
    "ac": 14,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 38,
    "hp_formula": "7d8+7",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 3
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 4
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 3
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 4
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "洞悉": 4,
      "察觉": 4
    },
    "senses": {
      "被动察觉": 14
    },
    "languages": "通用语、吉斯语",
    "cr": 2,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "吉斯泽莱人发动两次灵能打击攻击。"
      },
      {
        "name": "灵能打击",
        "en_name": "Psi Strike",
        "description": "近战攻击检定：+4，触及5尺。命中：6（1d8+2）钝击伤害外加9（2d8）心灵伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "吉斯泽莱人施展以下一道法术，无需法术成分并使用感知作为施法属性："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "法师之手Mage Hand（手是隐形的）"
      },
      {
        "name": "1/日：",
        "en_name": "",
        "description": "识破隐形See Invisibility"
      }
    ],
    "bonus_actions": [
      {
        "name": "灵能跃迁",
        "en_name": "Psi-Powered Leap",
        "description": "吉斯泽莱人施展跳跃术Jump，无需法术成分并使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "reactions": [
      {
        "name": "灵能防御",
        "en_name": "Psionic Defense",
        "description": "吉斯泽莱人施展羽落术Feather \nFall或护盾术Shield \n（触发条件见这些法术），无需法术成分并使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "异怪\\吉斯人\\吉斯泽莱武僧.htm"
  },
  {
    "name": "吉斯泽莱泽锡修士",
    "en_name": "Githzerai Zerth",
    "type_line": "中型异怪（吉斯人），守序中立",
    "size": "Medium",
    "creature_type": "异怪（吉斯人）",
    "alignment": "守序中立",
    "ac": 17,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 84,
    "hp_formula": "13d8+26",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 13,
        "mod": 1,
        "save": 4
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "感知": {
        "score": 17,
        "mod": 3,
        "save": 6
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "奥秘": 6,
      "洞悉": 6,
      "察觉": 6
    },
    "senses": {
      "被动察觉": 16
    },
    "languages": "通用语、吉斯语",
    "cr": 6,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "吉斯泽莱人发动两次灵能打击攻击。"
      },
      {
        "name": "灵能打击",
        "en_name": "Psi Strike",
        "description": "近战攻击检定：+7，触及5尺。命中：11（2d6+4）钝击伤害外加13（3d8）心灵伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "吉斯泽莱人施展以下一道法术，无需法术成分并使用感知作为施法属性（法术豁免DC14）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "法师之手Mage Hand（手是隐形的）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "幻影杀手Phantasmal Killer（六环版本），  位面转移Plane Shift，  识破隐形See Invisibility"
      }
    ],
    "bonus_actions": [
      {
        "name": "灵能跃迁",
        "en_name": "Psi-Powered Leap",
        "description": "吉斯泽莱人施展跳跃术Jump，无需法术成分并使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "reactions": [
      {
        "name": "灵能防御",
        "en_name": "Psionic Defense",
        "description": "吉斯泽莱人施展羽落术Feather \nFall或护盾术Shield（触发条件见这些法术），无需法术成分并使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "异怪\\吉斯人\\吉斯泽莱泽锡修士.htm"
  },
  {
    "name": "吉斯泽莱灵能使",
    "en_name": "Githzerai Psion",
    "type_line": "中型异怪（吉斯人），守序中立",
    "size": "Medium",
    "creature_type": "异怪（吉斯人）",
    "alignment": "守序中立",
    "ac": 18,
    "initiative_bonus": 8,
    "initiative_total": 18,
    "hp": 169,
    "hp_formula": "26d8+52",
    "speed": {
      "walk": "40尺，飞行40尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 5
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 8
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 19,
        "mod": 4,
        "save": 8
      },
      "感知": {
        "score": 18,
        "mod": 4,
        "save": 8
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "奥秘": 8,
      "洞悉": 8,
      "察觉": 8
    },
    "senses": {
      "被动察觉": 18
    },
    "languages": "通用语、吉斯语",
    "cr": 12,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "吉斯泽莱人发动三次心灵扭曲攻击。"
      },
      {
        "name": "心灵扭曲",
        "en_name": "Psychic Warp",
        "description": "近战或远程攻击检定：+8，触及5尺或射程120尺。命中：26（4d10+4）心灵伤害，目标陷入某种由吉斯泽莱人选择的状态：(A)目标陷入魅惑状态直至吉斯泽莱人的下个回合开始；(B)若目标生物体型不超过大型，其陷入倒地状态。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "吉斯泽莱人施展以下一道法术，无需法术成分并使用智力作为施法属性（法术豁免DC16）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "法师之手Mage Hand（手是隐形的）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "位面转移Plane Shift、识破隐形See Invisibility"
      }
    ],
    "reactions": [
      {
        "name": "灵能防御",
        "en_name": "Psionic Defense",
        "description": "吉斯泽莱人施展羽落术Feather \nFall或护盾术Shield（触发条件见这些法术），无需法术成分并使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "异怪\\吉斯人\\吉斯泽莱灵能使.htm"
  },
  {
    "name": "吉斯洋基武者",
    "en_name": "Githyanki Warrior",
    "type_line": "中型异怪（吉斯人），守序邪恶",
    "size": "Medium",
    "creature_type": "异怪（吉斯人）",
    "alignment": "守序邪恶",
    "ac": 17,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 49,
    "hp_formula": "9d8+9",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 3
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 3
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 3
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "equipment": "半身板甲",
    "senses": {
      "被动察觉": 11
    },
    "languages": "通用语、吉斯语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "吉斯洋基人发动两次灵佑刀锋攻击。"
      },
      {
        "name": "灵佑刀锋",
        "en_name": "Psi Blade",
        "description": "近战攻击检定：+4，触及5尺。命中：9（2d6+2）挥砍伤害外加7（2d6）心灵伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "吉斯洋基人施展以下一道法术，无需法术成分并使用智力作为施法属性："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "法师之手Mage Hand（手是隐形的）"
      },
      {
        "name": "2/日：",
        "en_name": "",
        "description": "回避侦测Nondetection（仅自身）"
      }
    ],
    "bonus_actions": [
      {
        "name": "迷踪步",
        "en_name": "Misty Step",
        "description": "吉斯洋基人施展迷踪步Misty \nStep，无需法术成分并使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "异怪\\吉斯人\\吉斯洋基武者.htm"
  },
  {
    "name": "吉斯洋基骑士",
    "en_name": "Githyanki Knight",
    "type_line": "中型异怪（吉斯人），守序邪恶",
    "size": "Medium",
    "creature_type": "异怪（吉斯人）",
    "alignment": "守序邪恶",
    "ac": 18,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 117,
    "hp_formula": "18d8+36",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 5
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "equipment": "板甲",
    "senses": {
      "被动察觉": 12
    },
    "languages": "通用语、吉斯语",
    "cr": 8,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "吉斯洋基人发动三次银剑攻击。其可以将其中一次攻击替换为使用施法施展心灵遥控Telekinesis （若条件允许）。"
      },
      {
        "name": "银剑",
        "en_name": "Silver Sword",
        "description": "近战攻击检定：+6，触及5尺。命中：10（2d6+3）挥砍伤害外加14（4d6）心灵伤害。重击：若目标处于星界躯体状态（如受星界投影Astral \nProjection 影响），吉斯洋基人可切断其连接物质躯体的银线而非造成伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "吉斯洋基人施展以下一道法术，无需法术成分并使用智力作为施法属性（法术豁免DC13）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "法师之手Mage Hand（手是隐形的）"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "回避侦测Nondetection（仅自身）、 巧言术Tongues"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "位面转移Plane Shift、  心灵遥控Telekinesis"
      }
    ],
    "bonus_actions": [
      {
        "name": "迷踪步",
        "en_name": "Misty Step",
        "description": "吉斯洋基人施展迷踪步Misty \nStep，无需法术成分并使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "异怪\\吉斯人\\吉斯洋基骑士.htm"
  },
  {
    "name": "吉斯洋基龙巫",
    "en_name": "Githyanki Dracomancer",
    "type_line": "中型异怪（吉斯人），守序邪恶",
    "size": "Medium",
    "creature_type": "异怪（吉斯人）",
    "alignment": "守序邪恶",
    "ac": 18,
    "initiative_bonus": 8,
    "initiative_total": 18,
    "hp": 255,
    "hp_formula": "30d8 + 120",
    "speed": {
      "walk": "30尺，飞行30尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 8
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 9
      },
      "智力": {
        "score": 20,
        "mod": 5,
        "save": 10
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 8
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "奥秘": 10,
      "察觉": 8
    },
    "senses": {
      "盲视": 30,
      "被动察觉": 18
    },
    "languages": "通用语、龙语、吉斯语",
    "cr": 16,
    "pb": 5,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "吉斯洋基人发动三次拟龙炎袭攻击。"
      },
      {
        "name": "拟龙炎袭",
        "en_name": "Draconic Strike",
        "description": "近战或远程攻击检定：+10，触及10尺或射程120尺。命中：12（2d6+5）挥砍伤害外加17（5d6）火焰伤害，目标陷入恐慌状态直至吉斯洋基人的下个回合开始。"
      },
      {
        "name": "咒唤龙息",
        "en_name": "Conjured Dragon",
        "description": "敏捷豁免检定：DC18，90尺锥状区域内的每名生物。失败：27（6d8）火焰伤害外加27（6d8）力场伤害。成功：半伤。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "吉斯洋基人施展以下一道法术，无需法术成分并使用智力作为施法属性（法术豁免DC18，法术攻击命中+10）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "法师之手 Mage Hand（手是隐形的）"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "回避侦测 Nondetection（仅自身），   位面转移 Plane Shift，    巧言术 Tongues"
      }
    ],
    "bonus_actions": [
      {
        "name": "迷踪步",
        "en_name": "Misty Step",
        "description": "吉斯洋基人施展迷踪步Misty Step \n，无需法术成分并使用与施法动作相同的施法属性。",
        "params": "3/日"
      }
    ],
    "source_file": "异怪\\吉斯人\\吉斯洋基龙巫.htm"
  },
  {
    "name": "夺心魔",
    "en_name": "Mind Flayer",
    "type_line": "中型异怪，守序邪恶",
    "size": "Medium",
    "creature_type": "异怪",
    "alignment": "守序邪恶",
    "ac": 15,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 99,
    "hp_formula": "18d8+18",
    "speed": {
      "walk": "30尺，飞行15尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 4
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 19,
        "mod": 4,
        "save": 7
      },
      "感知": {
        "score": 17,
        "mod": 3,
        "save": 6
      },
      "魅力": {
        "score": 17,
        "mod": 3,
        "save": 6
      }
    },
    "skills": {
      "奥秘": 7,
      "洞悉": 6,
      "察觉": 6,
      "隐匿": 4
    },
    "damage_resistances": [
      "心灵"
    ],
    "equipment": "胸甲",
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 16
    },
    "languages": "深潜语，地底通用语；心灵感应120尺",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "夺心魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "触须",
        "en_name": "Tentacles",
        "description": "近战攻击检定：+7，触及5尺。\n命中：22（4d8+4）心灵伤害。若目标生物体型不超过中型，则其被夺心魔的全部触须擒抱，陷入受擒状态（逃脱DC14），且目标陷入震慑状态直至擒抱结束。"
      },
      {
        "name": "采脑",
        "en_name": "Extract Brain",
        "description": "体质豁免检定：DC15，单一正受擒于夺心魔触须的生物。\n失败：55（10d10）穿刺伤害。\n成功：半伤。\n失败或成功：若目标因此伤害生命值降至0，夺心魔杀死目标并吞食其大脑。"
      },
      {
        "name": "心灵震爆",
        "en_name": "Mind Blast",
        "description": "智力豁免检定：DC15，60尺锥形区域内的每名生物。\n失败：31（6d8+4）心灵伤害，且目标陷入震慑状态直至夺心魔的下个回合结束。\n成功：仅半伤。",
        "params": "充能5–6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "夺心魔施展以下一道法术，无需法术成分并使用智力作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测思想Detect Thoughts"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "支配怪物Dominate Monster，位面转移Plane Shift（仅自身）"
      }
    ],
    "source_file": "异怪\\夺心魔\\夺心魔.htm"
  },
  {
    "name": "夺心魔奥术师",
    "en_name": "Mind Flayer Arcanist",
    "type_line": "中型异怪，守序邪恶",
    "size": "Medium",
    "creature_type": "异怪",
    "alignment": "守序邪恶",
    "ac": 16,
    "initiative_bonus": 6,
    "initiative_total": 16,
    "hp": 143,
    "hp_formula": "26d8+26",
    "speed": {
      "walk": "30尺，飞行30尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 6
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 20,
        "mod": 5,
        "save": 9
      },
      "感知": {
        "score": 17,
        "mod": 3,
        "save": 7
      },
      "魅力": {
        "score": 17,
        "mod": 3,
        "save": 7
      }
    },
    "skills": {
      "奥秘": 13,
      "洞悉": 7,
      "察觉": 7,
      "隐匿": 6
    },
    "damage_immunities": [
      "心灵"
    ],
    "condition_immunities": [
      "魅惑",
      "恐慌"
    ],
    "equipment": "胸甲",
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 17
    },
    "languages": "深潜语，地底通用语；心灵感应120尺",
    "cr": 11,
    "xp": 7200,
    "pb": 4,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "夺心魔对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "夺心魔发动三次奥术触须攻击。"
      },
      {
        "name": "奥术触须",
        "en_name": "Arcane Tentacles",
        "description": "近战或远程攻击检定：+9，触及5尺或射程120尺。\n命中：27（4d10+5）心灵伤害，且夺心魔可以将目标传送至多30尺至一处夺心魔可见的、有足以支撑目标的表面或液体的未占据空间中。若目标因此伤害生命值降至0，夺心魔杀死目标并以魔法吞食其大脑。"
      },
      {
        "name": "心灵爆裂",
        "en_name": "Mind Burst",
        "description": "智力豁免检定：DC17，源自夺心魔的40尺光环区域内的每名生物。\n失败：41（8d8+5）心灵伤害，且目标陷入震慑状态直至夺心魔的下个回合结束。\n成功：仅半伤。",
        "params": "充能5–6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "夺心魔施展以下一道法术，无需法术成分并使用智力作为施法属性（法术豁免DC17）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，   侦测思想Detect Thoughts，   易容术Disguise Self，   法师之手Mage Hand（手是隐形的）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "鹰眼术Clairvoyance，  任意门Dimension Door，   火球术Fireball（五环版本），  闪电束Lightning Bolt（五环版本），  位面转移Plane Shift（仅自身），   短讯术Sending"
      }
    ],
    "reactions": [
      {
        "name": "护盾术",
        "en_name": "Shield",
        "description": "夺心魔施展护盾术Shield\n（触发条件见该法术），使用与施法动作相同的施法属性。",
        "params": "2/天"
      }
    ],
    "source_file": "异怪\\夺心魔\\夺心魔奥术师.htm"
  },
  {
    "name": "寇涛",
    "en_name": "Kuo-toa",
    "type_line": "中型异怪，中立邪恶",
    "size": "Medium",
    "creature_type": "异怪",
    "alignment": "中立邪恶",
    "ac": 13,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 18,
    "hp_formula": "4d8",
    "speed": {
      "walk": "30尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 4
    },
    "equipment": "矛",
    "senses": {
      "黑暗视觉": 120,
      "真实视觉": 30,
      "被动察觉": 14
    },
    "languages": "地底通用语",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "寇涛可以在空气和水中呼吸。"
      },
      {
        "name": "日照敏感",
        "en_name": "Sunlight Sensitivity",
        "description": "若寇涛身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "矛",
        "en_name": "Spear",
        "description": "近战或远程攻击检定：+3，触及5尺或射程20/60尺。命中：5（1d8+1）穿刺伤害。"
      },
      {
        "name": "粘性捕网",
        "en_name": "Sticky Net",
        "description": "敏捷豁免检定：DC10，单一15尺内寇涛可见的不超过大型的生物。失败：目标陷入束缚状态直至捕网被摧毁（AC10，HP5；免疫钝击，毒素和心灵伤害）。一名生物物能够以动作进行一次DC10的力量（运动）检定来尝试解救自身或位于自身5尺内困在捕网中的其他生物，成功则摧毁捕网。",
        "params": "1/日"
      }
    ],
    "reactions": [
      {
        "name": "粘性盾牌",
        "en_name": "Sticky Shield",
        "description": "触发：一名生物以武器进行的近战攻击检定对寇涛失手。响应-力量豁免检定：DC11，触发生物。失败：攻击者的该武器粘在寇涛的盾牌上。若目标不放开武器，则该武器被粘住期间目标陷入受擒状态（逃脱DC11）。该武器被粘住期间无法被使用。目标能够以动作进行一次DC11的力量（运动）检定，成功则该武器被解放。"
      }
    ],
    "source_file": "异怪\\寇涛\\寇涛.htm"
  },
  {
    "name": "寇涛大祭司",
    "en_name": "Kuo-toa Archpriest",
    "type_line": "中型异怪，中立邪恶",
    "size": "Medium",
    "creature_type": "异怪",
    "alignment": "中立邪恶",
    "ac": 13,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 105,
    "hp_formula": "14d8+42",
    "speed": {
      "walk": "30尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 9,
      "宗教": 4
    },
    "senses": {
      "黑暗视觉": 120,
      "真实视觉": 30,
      "被动察觉": 19
    },
    "languages": "地底通用语",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "寇涛可以在空气和水中呼吸。"
      },
      {
        "name": "日照敏感",
        "en_name": "Sunlight Sensitivity",
        "description": "若寇涛身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "寇涛发动三次怪异圣杖攻击。"
      },
      {
        "name": "怪异圣杖",
        "en_name": "Strange Scepter",
        "description": "近战或远程攻击检定：+6，触及5尺或射程120尺。命中：20（5d6+3）闪电伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "寇涛施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC14）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，奇术Thaumaturgy"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "湮灭波Destructive Wave，预言术Divination，定身怪物Hold Monster（六环版本），  探知Scrying，巧言术Tongues"
      }
    ],
    "bonus_actions": [
      {
        "name": "虔诚护盾",
        "en_name": "Shield of Faith",
        "description": "寇涛施展虔诚护盾Shield of Faith  ，使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "异怪\\寇涛\\寇涛大祭司.htm"
  },
  {
    "name": "寇涛监察者",
    "en_name": "Kuo-toa Monitor",
    "type_line": "中型异怪，中立邪恶",
    "size": "Medium",
    "creature_type": "异怪",
    "alignment": "中立邪恶",
    "ac": 13,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 65,
    "hp_formula": "10d8+20",
    "speed": {
      "walk": "30尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 6,
      "宗教": 3
    },
    "senses": {
      "黑暗视觉": 120,
      "真实视觉": 30,
      "被动察觉": 16
    },
    "languages": "地底通用语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "寇涛可以在空气和水中呼吸。"
      },
      {
        "name": "日照敏感",
        "en_name": "Sunlight Sensitivity",
        "description": "若寇涛身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "寇涛发动两次骨鞭攻击。"
      },
      {
        "name": "骨鞭",
        "en_name": "Bone Whip",
        "description": "近战攻击检定：+5，触及10尺。命中：6（1d6+3）挥砍伤害外加7（2d6）闪电伤害，且直至寇涛的下个回合开始，目标无法发动借机攻击。"
      }
    ],
    "source_file": "异怪\\寇涛\\寇涛监察者.htm"
  },
  {
    "name": "寇涛驱策者",
    "en_name": "Kuo-toa Whip",
    "type_line": "中型异怪，中立邪恶",
    "size": "Medium",
    "creature_type": "异怪",
    "alignment": "中立邪恶",
    "ac": 11,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 45,
    "hp_formula": "7d8+14",
    "speed": {
      "walk": "30尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 6,
      "宗教": 3
    },
    "senses": {
      "黑暗视觉": 120,
      "真实视觉": 30,
      "被动察觉": 16
    },
    "languages": "地底通用语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "寇涛可以在空气和水中呼吸。"
      },
      {
        "name": "日照敏感",
        "en_name": "Sunlight Sensitivity",
        "description": "若寇涛身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "钳杖",
        "en_name": "Pincer Staff",
        "description": "近战攻击检定：+4，触及10尺。命中：9（2d6+2）穿刺伤害。若目标生物体型不超过中型，则其陷入受擒状态（逃脱DC12）。且寇涛无法再次发动钳杖攻击，直至擒抱结束。"
      },
      {
        "name": "咒唤粘液之球",
        "en_name": "Conjure Slimy Glob",
        "description": "远程攻击检定：+4，射程60尺。命中：9（3d4+2）强酸伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "虔诚护盾",
        "en_name": "Shield of Faith",
        "description": "寇涛施展虔诚护盾Shield of \nFaith，使用感知作为施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "异怪\\寇涛\\寇涛驱策者.htm"
  },
  {
    "name": "穴居攫怪",
    "en_name": "Grick",
    "type_line": "中型异怪，无阵营",
    "size": "Medium",
    "creature_type": "异怪",
    "alignment": "无阵营",
    "ac": 14,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 54,
    "hp_formula": "12d8",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "skills": {
      "隐匿": 4
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 12
    },
    "languages": "无",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "穴居攫怪发动一次喙啄攻击和一次触须攻击。"
      },
      {
        "name": "喙啄",
        "en_name": "Beak",
        "description": "近战攻击检定：+4，触及5尺。\n命中：9（2d6+2）穿刺伤害。"
      },
      {
        "name": "触须",
        "en_name": "Tentacles",
        "description": "近战攻击检定：+4，触及5尺。\n命中：7（1d10+2）挥砍伤害。若目标生物体型不超过中型，则其被全部四条触须擒抱，陷入受擒状态（逃脱DC12）。"
      }
    ],
    "source_file": "异怪\\穴居攫怪\\穴居攫怪.htm"
  },
  {
    "name": "远古穴居攫怪",
    "en_name": "Grick Ancient",
    "type_line": "大型异怪，无阵营",
    "size": "Large",
    "creature_type": "异怪",
    "alignment": "无阵营",
    "ac": 18,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 135,
    "hp_formula": "18d10+36",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 4,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "隐匿": 6
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 12
    },
    "languages": "无",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "穴居攫怪发动一次喙啄攻击，一次猛击攻击和一次触须攻击。"
      },
      {
        "name": "喙啄",
        "en_name": "Beak",
        "description": "近战攻击检定：+7，触及10尺。\n命中：22（4d8+4）穿刺伤害。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+7，触及10尺。\n命中：7（1d6+4）钝击伤害。若目标生物的体型不超过中型，其陷入倒地状态。"
      },
      {
        "name": "触须",
        "en_name": "Tentacles",
        "description": "近战攻击检定：+7，触及10尺。\n命中：15（2d10+4）挥砍伤害。若目标生物的体型不超过中型，则其被全部四条触须擒抱，陷入受擒状态（逃脱DC14）。"
      }
    ],
    "source_file": "异怪\\穴居攫怪\\远古穴居攫怪.htm"
  },
  {
    "name": "巨魔",
    "en_name": "Troll",
    "type_line": "大型巨人，混乱邪恶",
    "size": "Large",
    "creature_type": "巨人",
    "alignment": "混乱邪恶",
    "ac": 15,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 94,
    "hp_formula": "9d10+45",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 5
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 15
    },
    "languages": "巨人语",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "扰人断肢",
        "en_name": "Loathsome Limbs",
        "description": "若巨魔在任意回合结束时浴血，并且曾在此回合中受到15+挥砍伤害，巨魔的其中一条肢体会被切断，落到巨魔所在的空间中，成为一条巨魔断肢Troll \nLimb 。断肢在巨魔的回合结束后立即行动。巨魔每有一条失去的肢体，其便获得1级力竭，巨魔会在下次恢复生命值时长出失去的肢体。",
        "params": "4/日"
      },
      {
        "name": "再生",
        "en_name": "Regeneration",
        "description": "巨魔在其回合开始时恢复15生命值。若巨魔受到强酸或火焰伤害，则该特质在其下个回合开始时无法生效。巨魔只有以0生命值开始其回合且无法再生时，才会死亡。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "巨魔发动三次撕裂攻击。"
      },
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+7，触及10尺。命中：11（2d6+4）挥砍伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "冲锋",
        "en_name": "Charge",
        "description": "巨魔向一名其可见的敌人直线移动至多等于其速度一半的距离。"
      }
    ],
    "source_file": "巨人\\巨魔\\巨魔.htm"
  },
  {
    "name": "巨魔断肢",
    "en_name": "Troll Limb",
    "type_line": "小型巨人，混乱邪恶",
    "size": "Small",
    "creature_type": "巨人",
    "alignment": "混乱邪恶",
    "ac": 13,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 14,
    "hp_formula": "4d6",
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "感知": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 1,
        "mod": -5,
        "save": -5
      }
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "无",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "再生",
        "en_name": "Regeneration",
        "description": "断肢在其回合开始时恢复15生命值。若断肢受到强酸或火焰伤害，则该特质在其下个回合开始时无法生效。断肢只有以0生命值开始其回合且无法再生时，才会死亡。"
      },
      {
        "name": "巨魔孽生",
        "en_name": "Troll \nSpawn",
        "description": "断肢不可思议地有着如同整只巨魔的感官。若断肢未在24小时内被摧毁，掷1d12。骰值为12时，断肢长成一头巨魔Troll。否则，断肢萎缩死去。"
      }
    ],
    "actions": [
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+6，触及5尺。命中：9（2d4+4）挥砍伤害。"
      }
    ],
    "source_file": "巨人\\巨魔\\巨魔断肢.htm"
  },
  {
    "name": "云巨人",
    "en_name": "Cloud Giant",
    "type_line": "巨型巨人，中立",
    "size": "Huge",
    "creature_type": "巨人",
    "alignment": "中立",
    "ac": 14,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 200,
    "speed": {
      "walk": "40尺，飞行20尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 27,
        "mod": 8,
        "save": 8
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 22,
        "mod": 6,
        "save": 10
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "洞悉": 7,
      "察觉": 11
    },
    "senses": {
      "被动察觉": 21
    },
    "languages": "通用语，巨人语",
    "cr": 9,
    "xp": 5000,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "云巨人使用雷鸣重锤或雷云发动共计两次攻击。其可以将其中一次攻击替换为使用施法施展云雾术Fog Cloud。"
      },
      {
        "name": "雷鸣重锤",
        "en_name": "Thunderous Mace",
        "description": "近战攻击检定：+12，触及10尺。命中：21（3d8 + 8）钝击伤害外加7（2d6）雷鸣伤害。"
      },
      {
        "name": "雷云",
        "en_name": "Thundercloud",
        "description": "远程攻击检定：+12，射程240尺。命中：18（3d6 + 8）雷鸣伤害，且目标陷入失能状态直至其下个回合结束。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "云巨人施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，云雾术Fog \nCloud，光亮术Light"
      },
      {
        "name": "1/日：",
        "en_name": "",
        "description": "操控天气Control Weather，气化形体Gaseous Form，心灵遥控Telekinesis"
      }
    ],
    "bonus_actions": [
      {
        "name": "迷踪步",
        "en_name": "Misty Step",
        "description": "云巨人施展迷踪步Misty \nStep，使用与施法动作相同的施法属性。"
      }
    ],
    "source_file": "巨人\\序位巨人\\云巨人.htm"
  },
  {
    "name": "山丘巨人",
    "en_name": "Hill Giant",
    "type_line": "巨型巨人，混乱邪恶",
    "size": "Huge",
    "creature_type": "巨人",
    "alignment": "混乱邪恶",
    "ac": 13,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 105,
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "察觉": 2
    },
    "senses": {
      "被动察觉": 12
    },
    "languages": "巨人语",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "山丘巨人使用树棍或投掷垃圾发动共计两次攻击。"
      },
      {
        "name": "树棍",
        "en_name": "Tree Club",
        "description": "近战攻击检定：+8，触及10尺。命中：18（3d8 + 5）钝击伤害。若目标生物体型不超过大型，则其陷入倒地状态。"
      },
      {
        "name": "投掷垃圾",
        "en_name": "Trash Lob",
        "description": "远程攻击检定：+8，射程：60/240 尺。命中：16（2d10 + 5）钝击伤害，目标陷入中毒状态直至其下个回合结束。"
      }
    ],
    "source_file": "巨人\\序位巨人\\山丘巨人.htm"
  },
  {
    "name": "火巨人",
    "en_name": "Fire Giant",
    "type_line": "巨型巨人，守序邪恶",
    "size": "Huge",
    "creature_type": "巨人",
    "alignment": "守序邪恶",
    "ac": 18,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 162,
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "敏捷": {
        "score": 9,
        "mod": -1,
        "save": 3
      },
      "体质": {
        "score": 23,
        "mod": 6,
        "save": 10
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 5
      }
    },
    "skills": {
      "运动": 11,
      "察觉": 6
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "被动察觉": 16
    },
    "languages": "巨人语",
    "cr": 9,
    "xp": 5000,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "火巨人使用火焰之剑或投掷炎锤发动共计两次攻击。"
      },
      {
        "name": "火焰之剑",
        "en_name": "Flame Sword",
        "description": "近战攻击检定：+11，触及10尺。命中：21（4d6+7）挥砍伤害外加10（3d6）火焰伤害。"
      },
      {
        "name": "投掷炎锤",
        "en_name": "Hammer Throw",
        "description": "远程攻击检定：+11，射程60/240尺。命中：23（3d10+7）钝击伤害外加4（1d8）火焰伤害，目标被火巨人直线推离至多15尺。目标下个回合结束前进行的下次攻击检定具有劣势。"
      }
    ],
    "source_file": "巨人\\序位巨人\\火巨人.htm"
  },
  {
    "name": "石巨人",
    "en_name": "Stone Giant",
    "type_line": "巨型巨人，中立",
    "size": "Huge",
    "creature_type": "巨人",
    "alignment": "中立",
    "ac": 17,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 126,
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 5
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 8
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 4
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "运动": 12,
      "察觉": 4,
      "隐匿": 5
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 14
    },
    "languages": "巨人语",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "石巨人使用石棒或投石发动共计两次攻击。"
      },
      {
        "name": "石棒",
        "en_name": "Stone Club",
        "description": "近战攻击检定：+9，触及15尺。命中：22 （3d10 + 6）钝击伤害。"
      },
      {
        "name": "投石",
        "en_name": "Boulder",
        "description": "远程攻击检定：+9，射程：60/240 尺。命中：15 （2d8 + 6）钝击伤害，若目标生物体型不超过大型，则其陷入倒地状态。"
      }
    ],
    "reactions": [
      {
        "name": "偏转飞弹",
        "en_name": "Deflect Missile",
        "description": "触发：石巨人因远程攻击检定被命中，并因此受到钝击、穿刺或挥砍伤害时。响应：石巨人受到的此次攻击的伤害减少11（1d10 \n+ 6）。若该伤害因此降至0，石巨人可以重定向此次攻击的部分力量。敏捷豁免检定：   DC17，单一60尺内石巨人可见的生物。失败：11（1d10 + 6）力场伤害。",
        "params": "充能5–6"
      }
    ],
    "source_file": "巨人\\序位巨人\\石巨人.htm"
  },
  {
    "name": "霜巨人",
    "en_name": "Frost Giant",
    "type_line": "巨型巨人，中立邪恶",
    "size": "Huge",
    "creature_type": "巨人",
    "alignment": "中立邪恶",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 149,
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 21,
        "mod": 5,
        "save": 8
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 3
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 4
      }
    },
    "skills": {
      "运动": 9,
      "察觉": 3
    },
    "damage_immunities": [
      "寒冷"
    ],
    "senses": {
      "被动察觉": 13
    },
    "languages": "巨人语",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "霜巨人使用寒霜之斧或巨弓发动共计两次攻击。"
      },
      {
        "name": "寒霜之斧",
        "en_name": "Frost Axe",
        "description": "近战攻击检定：+9，触及10尺。命中：19（2d12 + 6）挥砍伤害外加9（2d8）寒冷伤害。"
      },
      {
        "name": "巨弓",
        "en_name": "Great Bow",
        "description": "远程攻击检定：+9，射程150/600尺。命中：17（2d10 + \n6）穿刺伤害外加7（2d6）寒冷伤害，且目标的速度降低10尺直至其下个回合结束。"
      }
    ],
    "bonus_actions": [
      {
        "name": "战吼",
        "en_name": "War Cry",
        "description": "霜巨人或其选择的一名可以看见或听见其的生物获得16（2d10 + \n5）临时生命值，且目标进行攻击检定时具有优势，直至霜巨人的下个回合开始。",
        "params": "充能5~6"
      }
    ],
    "source_file": "巨人\\序位巨人\\霜巨人.htm"
  },
  {
    "name": "风暴巨人",
    "en_name": "Storm Giant",
    "type_line": "巨型巨人，混乱善良",
    "size": "Huge",
    "creature_type": "巨人",
    "alignment": "混乱善良",
    "ac": 16,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 230,
    "speed": {
      "walk": "50尺，飞行25尺（悬浮），游泳50尺"
    },
    "abilities": {
      "力量": {
        "score": 29,
        "mod": 9,
        "save": 14
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 10
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 20,
        "mod": 5,
        "save": 10
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 9
      }
    },
    "skills": {
      "奥秘": 8,
      "运动": 14,
      "历史": 8,
      "察觉": 10
    },
    "damage_resistances": [
      "寒冷"
    ],
    "damage_immunities": [
      "闪电",
      "雷鸣"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 20
    },
    "languages": "通用语，巨人语",
    "cr": 13,
    "xp": 10000,
    "pb": 5,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "风暴巨人可以在空气和水中呼吸。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "风暴巨人使用风暴之剑或雷霆轰击发动共计两次攻击。"
      },
      {
        "name": "风暴之剑",
        "en_name": "Storm Sword",
        "description": "近战攻击检定：+14，触及10尺。命中：23（4d6+9）挥砍伤害外加13（3d8）闪电伤害。"
      },
      {
        "name": "雷霆轰击",
        "en_name": "Thunderbolt",
        "description": "远程攻击检定：+14，射程500尺。命中：22（2d12+9）闪电伤害，且目标陷入目盲和耳聋状态，直至风暴巨人的下个回合开始。"
      },
      {
        "name": "闪电风暴",
        "en_name": "Lightning Storm",
        "description": "敏捷豁免检定：DC18，以500尺内风暴巨人可见一点为源点，半径10尺、高40尺的柱状区域内的每名生物。失败：55（10d10）闪电伤害。成功：半伤。",
        "params": "充能5–6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "风暴巨人施展以下一道法术，其无需材料成分并使用感知作为施法属性（法术豁免DC18）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，光亮术Light"
      },
      {
        "name": "1/日：",
        "en_name": "",
        "description": "操控天气Control Weather"
      }
    ],
    "source_file": "巨人\\序位巨人\\风暴巨人.htm"
  },
  {
    "name": "独眼巨人先知",
    "en_name": "Cyclops Oracle",
    "type_line": "巨型巨人，混乱中立",
    "size": "Huge",
    "creature_type": "巨人",
    "alignment": "混乱中立",
    "ac": 16,
    "initiative_bonus": 8,
    "initiative_total": 18,
    "hp": 207,
    "hp_formula": "18d12+90",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 9
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 18,
        "mod": 4,
        "save": 8
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "历史": 11,
      "察觉": 12
    },
    "senses": {
      "真实视觉": 30
    },
    "languages": "巨人语",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "独眼巨人先知使用耀闪袭或流光发动共计三次攻击。"
      },
      {
        "name": "耀闪袭",
        "en_name": "Radiant Strike",
        "description": "近战攻击检定：+10，触及10尺。命中：22（3d10+6）光耀伤害。"
      },
      {
        "name": "流光",
        "en_name": "Flash of Light",
        "description": "远程攻击检定：+10，射程120尺。命中：17（2d10+6）光耀伤害，且直至独眼巨人先知的下个回合结束，目标进行的攻击检定具有劣势，。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "独眼巨人先知施展以下一道法术，无需任何材料成分并使用感知作为施法属性（法术豁免DC16）："
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "秘法眼Arcane Eye，侦测魔法Detect Magic，物件定位术Locate Object"
      },
      {
        "name": "1/日：",
        "en_name": "",
        "description": "通晓传奇Legend Lore"
      }
    ],
    "reactions": [
      {
        "name": "预兆",
        "en_name": "Portent",
        "description": "触发：独眼巨人先知或其可见的一名盟友进行一次D20检定。响应：独眼巨人掷1d20，随后选择是否用此d20替换此次检定的d20。",
        "params": "充能4~6"
      }
    ],
    "source_file": "巨人\\独眼巨人\\独眼巨人先知.htm"
  },
  {
    "name": "独眼巨人哨卫",
    "en_name": "Cyclops Sentry",
    "type_line": "巨型巨人，混乱中立",
    "size": "Huge",
    "creature_type": "巨人",
    "alignment": "混乱中立",
    "ac": 14,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 138,
    "hp_formula": "12d12+60",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "senses": {
      "被动察觉": 8
    },
    "languages": "巨人语",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "独眼巨人哨卫使用石棒或掷石发动共计两次攻击。"
      },
      {
        "name": "石棒",
        "en_name": "Stone Club",
        "description": "近战攻击检定：+9，触及10尺。命中：16（3d6+6）钝击伤害，若目标生物体型不超过巨型，则其陷入倒地状态。"
      },
      {
        "name": "掷石",
        "en_name": "Rock",
        "description": "远程攻击检定：+9，射程30/120尺。\n命中：22（3d10+6）钝击伤害。"
      }
    ],
    "reactions": [
      {
        "name": "有限未来视",
        "en_name": "Limited Foresight",
        "description": "触发：一名独眼巨人哨卫可见的生物对其进行攻击检定。响应：独眼巨人哨卫令此次检定具有劣势，且直至其下个回合结束，其对目标发动的攻击检定具有优势。",
        "params": "充能6"
      }
    ],
    "source_file": "巨人\\独眼巨人\\独眼巨人哨卫.htm"
  },
  {
    "name": "半食人魔",
    "en_name": "Ogrillon Ogre",
    "type_line": "大型巨人，混乱邪恶",
    "size": "Large",
    "creature_type": "巨人",
    "alignment": "混乱邪恶",
    "ac": 12,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 52,
    "hp_formula": "7d10+14",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "equipment": "战斧，标枪（3）",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "通用语，巨人语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "actions": [
      {
        "name": "战斧",
        "en_name": "Battleaxe",
        "description": "近战攻击检定：+5，触及5尺。命中：7（1d8+3）挥砍伤害。"
      },
      {
        "name": "标枪",
        "en_name": "Javelin",
        "description": "近战或远程攻击检定：+5，触及5尺或射程30/120尺。命中：6（1d6+3）穿刺伤害。"
      }
    ],
    "source_file": "巨人\\食人魔\\半食人魔.htm"
  },
  {
    "name": "食人魔",
    "en_name": "Ogre",
    "type_line": "大型巨人，混乱邪恶",
    "size": "Large",
    "creature_type": "巨人",
    "alignment": "混乱邪恶",
    "ac": 11,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 68,
    "hp_formula": "8d10+24",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "equipment": "巨棒，标枪（3）",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 8
    },
    "languages": "通用语，巨人语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "巨棒",
        "en_name": "Greatclub",
        "description": "近战攻击检定：+6，触及5尺。命中：13（2d8+4）钝击伤害。"
      },
      {
        "name": "标枪",
        "en_name": "Javelin",
        "description": "近战或远程攻击检定：+6，触及5尺或射程30/120尺。命中：11（2d6+4）穿刺伤害。"
      }
    ],
    "source_file": "巨人\\食人魔\\食人魔.htm"
  },
  {
    "name": "人马守望者",
    "en_name": "Centaur Warden",
    "type_line": "大型妖精，中立善良",
    "size": "Large",
    "creature_type": "妖精",
    "alignment": "中立善良",
    "ac": 16,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 105,
    "hp_formula": "14d10+28",
    "speed": {
      "walk": "50尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "运动": 7,
      "自然": 5,
      "察觉": 7
    },
    "senses": {
      "被动察觉": 17
    },
    "languages": "德鲁伊语，精灵语，木族语",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "人马使用森林之杖或烈阳射线发动共计两次攻击。"
      },
      {
        "name": "森林之杖",
        "en_name": "Forest Staff",
        "description": "近战攻击检定：+7，触及5尺。命中：13（2d8+4）钝击伤害外加14（4d6）毒素伤害。"
      },
      {
        "name": "烈阳射线",
        "en_name": "Sun Ray",
        "description": "远程攻击检定：+7，射程90尺。命中：14（3d6+4）光耀伤害，且目标陷入目盲状态，直至人马的下个回合开始。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "人马施展以下一道法术，使用感知作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "德鲁伊伎俩Druidcraft，动物交谈Speak with Animals"
      }
    ],
    "bonus_actions": [
      {
        "name": "藤缠行迹",
        "en_name": "Entangling Trail",
        "description": "人马移动至多等于其速度的距离且不会引发借机攻击。在人马移动过程中，位于人马5尺内的每名生物都会被选为一次以下效应的目标。力量豁免检定：DC15。失败：11（2d6+4）钝击伤害，且目标陷入束缚状态，直至其下个回合结束。",
        "params": "充能5~6"
      }
    ],
    "source_file": "妖精\\人马\\人马守望者.htm"
  },
  {
    "name": "人马骠骑",
    "en_name": "Centaur Trooper",
    "type_line": "大型妖精，中立善良",
    "size": "Large",
    "creature_type": "妖精",
    "alignment": "中立善良",
    "ac": 16,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 45,
    "hp_formula": "6d10+12",
    "speed": {
      "walk": "50尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 14,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "运动": 6,
      "察觉": 3
    },
    "equipment": "胸甲，长弓，长枪",
    "senses": {
      "被动察觉": 13
    },
    "languages": "精灵语，木族语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "人马使用长枪或长弓发动共计两次攻击。"
      },
      {
        "name": "长枪",
        "en_name": "Pike",
        "description": "近战攻击检定：+6，触及10尺。命中：9（1d10+4）穿刺伤害。"
      },
      {
        "name": "长弓",
        "en_name": "Longbow",
        "description": "远程攻击检定：+4，射程150/600尺。命中：6（1d8+2）穿刺伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "践踏冲锋",
        "en_name": "Trampling Charge",
        "description": "人马移动至多等于其速度的距离且不会引发借机攻击，并且可以移动穿过中型或小型生物所处的空间。所处空间被人马进入的每名生物都会被选为一次以下效应的目标。力量豁免检定：DC14。失败：7（1d6+4）钝击伤害，且目标陷入倒地状态。",
        "params": "充能5~6"
      }
    ],
    "source_file": "妖精\\人马\\人马骠骑.htm"
  },
  {
    "name": "半羊人",
    "en_name": "Satyr",
    "type_line": "中型妖精，混乱中立",
    "size": "Medium",
    "creature_type": "妖精",
    "alignment": "混乱中立",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 31,
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 2
    },
    "senses": {
      "被动察觉": 12
    },
    "languages": "通用语，精灵语，木族语",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "半羊人对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "蹄",
        "en_name": "Hooves",
        "description": "近战攻击检定：+5，触及5尺。\n命中：5（1d4+3）钝击伤害。若目标生物体型不超过中型，半羊人还能将其直线推离至多10尺距离。"
      },
      {
        "name": "嘲讽",
        "en_name": "Mockery",
        "description": "感知豁免检定：DC12，单一90尺内半羊人可见的生物。\n失败：5（1d6+2）心灵伤害。"
      }
    ],
    "source_file": "妖精\\半羊人\\半羊人.htm"
  },
  {
    "name": "半羊人欢庆之主",
    "en_name": "Satyr Revelmaster",
    "type_line": "中型妖精，混乱中立",
    "size": "Medium",
    "creature_type": "妖精",
    "alignment": "混乱中立",
    "ac": 17,
    "initiative_bonus": 7,
    "initiative_total": 17,
    "hp": 82,
    "hp_formula": "15d8+15",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "魅力": {
        "score": 17,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "特技": 7
    },
    "senses": {
      "被动察觉": 15
    },
    "languages": "通用语，精灵语，木族语",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "半羊人对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "半羊人发动三次欢腾羊跃攻击。"
      },
      {
        "name": "欢腾羊跃",
        "en_name": "Prance",
        "description": "近战攻击检定：+7，触及5尺。\n命中：13（2d8+4）钝击伤害，且目标陷入魅惑状态，持续至半羊人的下个回合开始。"
      },
      {
        "name": "妖精旋律",
        "en_name": "Fey Melody",
        "description": "半羊人奏唤出一段魅惑或恐慌之音。感知豁免检定：DC14，源自半羊人的60尺光环区域内的每名敌人。\n失败：目标将受到歌曲的效应影响：",
        "params": "充能4~6"
      },
      {
        "name": "魅惑之音",
        "en_name": "Charming",
        "description": "目标陷入魅惑状态，持续1分钟。魅惑期间，目标陷入失能状态且会用尽自身的移动力来在原地跳舞。目标身上的该效应会在其受到任意伤害时结束。"
      },
      {
        "name": "恐慌之音",
        "en_name": "Frightening",
        "description": "10（2d6+3）心灵伤害，且目标陷入恐慌状态，持续1分钟。如果目标结束自己回合时并不处于半羊人的视线内，目标身上的该状态将提前结束。"
      }
    ],
    "source_file": "妖精\\半羊人\\半羊人欢庆之主.htm"
  },
  {
    "name": "啵灵蛙武者",
    "en_name": "Bullywug Warrior",
    "type_line": "中型妖精，中立",
    "size": "Medium",
    "creature_type": "妖精",
    "alignment": "中立",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 11,
    "hp_formula": "2d8+2",
    "speed": {
      "walk": "30尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "隐匿": 4
    },
    "senses": {
      "被动察觉": 10
    },
    "languages": "啵灵蛙语，通用语",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "啵灵蛙可以在空气和水中呼吸。"
      },
      {
        "name": "蛙类交谈",
        "en_name": "Speak with Frogs and Toads",
        "description": "啵灵蛙可以使用啵灵蛙语来与蛙和蟾蜍进行简单交流。"
      }
    ],
    "actions": [
      {
        "name": "虫刺",
        "en_name": "Insectile Rapier",
        "description": "近战攻击：+4，触及5尺。命中：6（1d8+2）穿刺伤害外加2（1d4）毒素伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "跳跃",
        "en_name": "Leap",
        "description": "啵灵蛙消耗10尺移动力跳跃至多30尺。"
      }
    ],
    "source_file": "妖精\\啵灵蛙\\啵灵蛙武者.htm"
  },
  {
    "name": "啵灵蛙沼地大贤",
    "en_name": "Bullywug Bog Sage",
    "type_line": "中型妖精，中立",
    "size": "Medium",
    "creature_type": "妖精",
    "alignment": "中立",
    "ac": 16,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 52,
    "hp_formula": "8d8+16",
    "speed": {
      "walk": "30尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 4
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 5
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "自然": 4,
      "隐匿": 5
    },
    "equipment": "材料包",
    "senses": {
      "被动察觉": 13
    },
    "languages": "啵灵蛙语，通用语，木族语",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "啵灵蛙可以在空气和水中呼吸。"
      },
      {
        "name": "蛙类交谈",
        "en_name": "Speak with Frogs and Toads",
        "description": "啵灵蛙可以使用啵灵蛙语来与蛙和蟾蜍进行简单交流。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "啵灵蛙发动两次沼地大杖攻击。其可以将其中任意次攻击替换为使用施法施展致病射线Ray \nof Sickness  。"
      },
      {
        "name": "沼地大杖",
        "en_name": "Bog Staff",
        "description": "近战攻击：+5，触及5尺。命中：7（1d8+3）钝击伤害外加10（3d6）毒素伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "啵灵蛙施展以下一道法术，使用感知作为施法属性（法术豁免DC13，法术攻击命中+5）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "舞光术Dancing Lights，德鲁伊伎俩Druidcraft，致病射线Ray of Sickness"
      },
      {
        "name": "1/日：",
        "en_name": "",
        "description": "植物交谈Speak with Plants，浓酸球Vitriolic Sphere"
      }
    ],
    "bonus_actions": [
      {
        "name": "跳跃",
        "en_name": "Leap",
        "description": "啵灵蛙消耗10尺移动力跳跃至多30尺。"
      }
    ],
    "source_file": "妖精\\啵灵蛙\\啵灵蛙沼地大贤.htm"
  },
  {
    "name": "地精咒术师",
    "en_name": "Goblin Hexer",
    "type_line": "小型妖精（类地精），混乱中立",
    "size": "Small",
    "creature_type": "妖精（类地精）",
    "alignment": "混乱中立",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 45,
    "hp_formula": "10d6+10",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "巧手": 5,
      "隐匿": 7
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "通用语，地精语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "地精发动两次咒术棍攻击。其可以将其中一次攻击替换为使用施法。"
      },
      {
        "name": "咒术棍",
        "en_name": "Hex Stick",
        "description": "近战或远程攻击检定：+5，触及5尺或射程60尺。命中：12（2d8+3）心灵伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "地精施展以下一道法术，使用智力作为施法属性（法术豁免DC13）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "次级幻象Minor Illusion"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "目盲术/耳聋术Blindness/Deafness，妖火Faerie Fire，油腻术Grease"
      }
    ],
    "reactions": [
      {
        "name": "倒霉",
        "en_name": "Jinx",
        "description": "触发：一名地精可见的生物对其进行攻击检定并命中。响应-感知豁免检定：DC13。失败：此次攻击改为失手。"
      }
    ],
    "source_file": "妖精\\地精\\地精咒术师.htm"
  },
  {
    "name": "地精喽啰",
    "en_name": "Goblin Minion",
    "type_line": "小型妖精（类地精），混乱中立",
    "size": "Small",
    "creature_type": "妖精（类地精）",
    "alignment": "混乱中立",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 7,
    "hp_formula": "2d6",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "隐匿": 6
    },
    "equipment": "匕首（3）",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "通用语，地精语",
    "cr": "1/8",
    "xp": 25,
    "pb": 2,
    "actions": [
      {
        "name": "匕首",
        "en_name": "Dagger",
        "description": "近战或远程攻击检定：+4，触及5尺或射程20/60尺。命中：4（1d4+2）穿刺伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "迅捷逃逸",
        "en_name": "Nimble Escape",
        "description": "地精执行撤离或躲藏动作。"
      }
    ],
    "source_file": "妖精\\地精\\地精喽啰.htm"
  },
  {
    "name": "地精武者",
    "en_name": "Goblin Warrior",
    "type_line": "小型妖精（类地精），混乱中立",
    "size": "Small",
    "creature_type": "妖精（类地精）",
    "alignment": "混乱中立",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 10,
    "hp_formula": "3d6",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "隐匿": 6
    },
    "equipment": "皮甲，弯刀，盾牌，短弓",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "通用语，地精语",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "actions": [
      {
        "name": "弯刀",
        "en_name": "Scimitar",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）挥砍伤害，若本次攻击具有优势，则再加2（1d4）挥砍伤害。"
      },
      {
        "name": "短弓",
        "en_name": "Shortbow",
        "description": "远程攻击检定：+4，射程80/320尺。命中：5（1d6+2）穿刺伤害，若本次攻击具有优势，则再加2（1d4）穿刺伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "迅捷逃逸",
        "en_name": "Nimble Escape",
        "description": "地精执行撤离或躲藏动作。"
      }
    ],
    "source_file": "妖精\\地精\\地精武者.htm"
  },
  {
    "name": "地精老大",
    "en_name": "Goblin Boss",
    "type_line": "小型妖精（类地精），混乱中立",
    "size": "Small",
    "creature_type": "妖精（类地精）",
    "alignment": "混乱中立",
    "ac": 17,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 21,
    "hp_formula": "6d6",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "隐匿": 6
    },
    "equipment": "链甲衫，弯刀，盾牌，短弓",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "通用语，地精语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "地精使用弯刀或短弓发动共计两次攻击。"
      },
      {
        "name": "弯刀",
        "en_name": "Scimitar",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）挥砍伤害，若本次攻击具有优势，则再加2（1d4）挥砍伤害。"
      },
      {
        "name": "短弓",
        "en_name": "Shortbow",
        "description": "远程攻击检定：+4，射程80/320尺。命中：5（1d6+2）穿刺伤害，若本次攻击具有优势，则再加2（1d4）穿刺伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "迅捷逃逸",
        "en_name": "Nimble Escape",
        "description": "地精执行撤离或躲藏动作。"
      }
    ],
    "reactions": [
      {
        "name": "挡刀",
        "en_name": "Redirect Attack",
        "description": "触发：一名地精可见的生物对其进行攻击检定。响应：地精选择一名位于其5尺内的小型或中型盟友。地精和该盟友交换位置，并且盟友成为这次攻击的目标。"
      }
    ],
    "source_file": "妖精\\地精\\地精老大.htm"
  },
  {
    "name": "大地精军阀",
    "en_name": "Hobgoblin Warlord",
    "type_line": "中型妖精（类地精），守序邪恶",
    "size": "Medium",
    "creature_type": "妖精（类地精）",
    "alignment": "守序邪恶",
    "ac": 20,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 112,
    "hp_formula": "15d8+45",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 3
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 5
      }
    },
    "equipment": "标枪（9），长剑，板甲，盾牌",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "通用语，地精语",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "traits": [
      {
        "name": "威权灵光",
        "en_name": "Aura of Authority",
        "description": "只要大地精未陷入失能状态，则其与其身处源自大地精的10尺光环区域内的盟友进行攻击检定与豁免时具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "大地精使用标枪或长剑发动共计三次攻击。"
      },
      {
        "name": "标枪",
        "en_name": "Javelin",
        "description": "近战或远程攻击检定：+6，触及5尺或射程30/120尺。\n命中：11（2d6+4）穿刺伤害，且直至大地精的下个回合开始，目标速度降低10尺。"
      },
      {
        "name": "长剑",
        "en_name": "Longsword",
        "description": "近战攻击检定：+6，触及5尺。\n命中：12（2d8+3）挥砍伤害。"
      }
    ],
    "reactions": [
      {
        "name": "格挡",
        "en_name": "Parry",
        "description": "触发：大地精在持握武器期间因近战攻击检定被命中。\n响应：大地精令其对抗那次攻击的AC+3，可能令那次攻击改为失手。"
      }
    ],
    "source_file": "妖精\\大地精\\大地精军阀.htm"
  },
  {
    "name": "大地精武者",
    "en_name": "Hobgoblin Warrior",
    "type_line": "中型妖精（类地精），守序邪恶",
    "size": "Medium",
    "creature_type": "妖精（类地精）",
    "alignment": "守序邪恶",
    "ac": 18,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 11,
    "hp_formula": "2d8+2",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "equipment": "半身板甲，长弓，长剑，盾牌",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "通用语，地精语",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "集群战术",
        "en_name": "Pack \nTactics",
        "description": "若大地精的攻击目标生物5尺内存在有至少一名大地精未失能的盟友，则大地精对该生物进行的攻击检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "长剑",
        "en_name": "Longsword",
        "description": "近战攻击检定：+3，触及5尺。\n命中：12（2d10+1）挥砍伤害。"
      },
      {
        "name": "长弓",
        "en_name": "Longbow",
        "description": "远程攻击检定：+3，射程150/600尺。\n命中：5（1d8+1）穿刺伤害外加7（3d4）毒素伤害。"
      }
    ],
    "source_file": "妖精\\大地精\\大地精武者.htm"
  },
  {
    "name": "大地精长官",
    "en_name": "Hobgoblin Captain",
    "type_line": "中型妖精（类地精），守序邪恶",
    "size": "Medium",
    "creature_type": "妖精（类地精）",
    "alignment": "守序邪恶",
    "ac": 17,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 58,
    "hp_formula": "9d8+18",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "equipment": "巨剑，半身板甲，长弓",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "通用语，地精语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "威权灵光",
        "en_name": "Aura of Authority",
        "description": "只要大地精未陷入失能状态，则其与其身处源自大地精的10尺光环区域内的盟友进行攻击检定与豁免时具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "大地精使用巨剑或长弓发动共计两次攻击。"
      },
      {
        "name": "巨剑",
        "en_name": "Greatsword",
        "description": "近战攻击检定：+4，触及5尺。\n命中：9（2d6+2）挥砍伤害外加3（1d6）毒素伤害。"
      },
      {
        "name": "长弓",
        "en_name": "Longbow",
        "description": "远程攻击检定：+4，射程150/600尺。\n命中：6（1d8+2）穿刺伤害外加5（2d4）毒素伤害。"
      }
    ],
    "source_file": "妖精\\大地精\\大地精长官.htm"
  },
  {
    "name": "座狼",
    "en_name": "Worg",
    "type_line": "大型妖精，中立邪恶",
    "size": "Large",
    "creature_type": "妖精",
    "alignment": "中立邪恶",
    "ac": 13,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 26,
    "hp_formula": "4d10+4",
    "speed": {
      "walk": "50尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 4
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 14
    },
    "languages": "地精语，座狼语",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：7（1d8+3）穿刺伤害，并且在座狼的下个回合开始前，对目标进行的下次攻击检定具有优势。"
      }
    ],
    "source_file": "妖精\\座狼\\座狼.htm"
  },
  {
    "name": "恐座狼",
    "en_name": "Dire Worg",
    "type_line": "巨型妖精，中立邪恶",
    "size": "Huge",
    "creature_type": "妖精",
    "alignment": "中立邪恶",
    "ac": 16,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 147,
    "hp_formula": "14d12+56",
    "speed": {
      "walk": "50尺"
    },
    "abilities": {
      "力量": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 6
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "察觉": 11
    },
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 21
    },
    "languages": "地精语，木族语，座狼语",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "座狼对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "座狼发动三次啃咬攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+10，触及5尺。命中：15（2d8+6）穿刺伤害外加7（2d6）毒素伤害，并且目标陷入中毒状态，持续至座狼的下个回合开始。中毒期间，目标无法恢复生命值。"
      },
      {
        "name": "恐惧嚎叫",
        "en_name": "Dreadful Howl",
        "description": "感知豁免检定：DC16，30尺内非座狼的每名生物。失败：36（8d8）心灵伤害，并且目标陷入恐慌状态，持续至座狼的下个回合开始。成功：仅半伤。",
        "params": "充能5~6"
      }
    ],
    "bonus_actions": [
      {
        "name": "扭曲步",
        "en_name": "Warp Step",
        "description": "座狼，连同一名其选择的位于其5尺内的自愿生物，传送至多30尺至一处其可见的未占据空间。"
      }
    ],
    "source_file": "妖精\\座狼\\恐座狼.htm"
  },
  {
    "name": "熊地精武者",
    "en_name": "Bugbear Warrior",
    "type_line": "中型妖精（类地精），混乱邪恶",
    "size": "Medium",
    "creature_type": "妖精（类地精）",
    "alignment": "混乱邪恶",
    "ac": 14,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 33,
    "hp_formula": "6d8+6",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "隐匿": 6,
      "求生": 2
    },
    "equipment": "兽皮甲，轻锤（3）",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "通用语，地精语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "劫持",
        "en_name": "Abduct",
        "description": "熊地精移动一名正被其擒抱的生物时无需额外消耗移动力。"
      }
    ],
    "actions": [
      {
        "name": "擒拿",
        "en_name": "Grab",
        "description": "近战攻击检定：+4，触及10尺。命中：9（2d6+2）钝击伤害，若目标生物体型不超过中型，则其陷入受擒状态（逃脱DC12）。"
      },
      {
        "name": "轻锤",
        "en_name": "Light Hammer",
        "description": "近战或远程攻击检定：+4（若目标因该熊地精而受擒则具有优势），触及10尺或射程20/60尺。命中：9（3d4+2）钝击伤害。"
      }
    ],
    "source_file": "妖精\\熊地精\\熊地精武者.htm"
  },
  {
    "name": "熊地精追猎者",
    "en_name": "Bugbear Stalker",
    "type_line": "中型妖精（类地精），混乱邪恶",
    "size": "Medium",
    "creature_type": "妖精（类地精）",
    "alignment": "混乱邪恶",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 65,
    "hp_formula": "10d8+20",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 4
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 3
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "隐匿": 6,
      "求生": 3
    },
    "equipment": "链甲衫，标枪（6），钉头锤",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "通用语，地精语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "劫持",
        "en_name": "Abduct",
        "description": "熊地精移动一名正被其擒抱的生物时无需额外消耗移动力。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "熊地精使用标枪或钉头锤发动共计两次攻击。"
      },
      {
        "name": "标枪",
        "en_name": "Javelin",
        "description": "近战或远程攻击检定：+5，触及10尺或射程30/120尺。命中：13（3d6+3）穿刺伤害。"
      },
      {
        "name": "钉头锤",
        "en_name": "Morningstar",
        "description": "近战攻击检定：+5（若目标因该熊地精而受擒则具有优势），触及10尺。命中：12（2d8+3）穿刺伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "快速擒抱",
        "en_name": "Quick Grapple",
        "description": "敏捷豁免检定：DC13，单一10尺内体型不超过中型且熊地精可见的生物。失败：目标陷入受擒状态（逃脱DC13）。"
      }
    ],
    "source_file": "妖精\\熊地精\\熊地精追猎者.htm"
  },
  {
    "name": "皮克妙妙精",
    "en_name": "Pixie Wonderbringer",
    "type_line": "微型妖精, 中立善良",
    "size": "Tiny",
    "creature_type": "妖精, 中立善良",
    "alignment": "",
    "ac": 15,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 60,
    "hp_formula": "24d4",
    "speed": {
      "walk": "10尺、飞行30尺"
    },
    "abilities": {
      "力量": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "敏捷": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "奥秘": 3
    },
    "senses": {
      "被动察觉": 15
    },
    "languages": "通用语，精灵语，木族语",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "皮克精对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "皮克精发动两次妖精尘攻击。"
      },
      {
        "name": "妖精尘",
        "en_name": "Faerie Dust",
        "description": "近战或远程攻击检定：+7，触及5尺或射程60尺。\n命中：15（2d10+4）光耀伤害，且目标陷入魅惑或中毒状态（由皮克精选择），持续至皮克精的下个回合开始。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "皮克精施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "舞光术Dancing Lights、德鲁伊伎俩Druidcraft、隐形术Invisibility（仅自身）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "侦测思想Detect Thoughts、飞行术Fly、高级幻影Major Image"
      }
    ],
    "bonus_actions": [
      {
        "name": "奇妙尘爆",
        "en_name": "Burst of Wonder",
        "description": "皮克精施展纠缠术Entangle、变形术Polymorph或塔莎狂笑术Tasha's \nHideous Laughter，无需材料成分并使用与施法动作相同的施法属性。",
        "params": "充能5~6"
      }
    ],
    "source_file": "妖精\\皮克精\\皮克妙妙精.htm"
  },
  {
    "name": "皮克精",
    "en_name": "Pixie",
    "type_line": "微型妖精, 中立善良",
    "size": "Tiny",
    "creature_type": "妖精, 中立善良",
    "alignment": "",
    "ac": 15,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 9,
    "hp_formula": "6d4-6",
    "speed": {
      "walk": "10尺、飞行30尺"
    },
    "abilities": {
      "力量": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "敏捷": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "体质": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 4
    },
    "senses": {
      "被动察觉": 14
    },
    "languages": "木族语",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "皮克精对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "妖精尘",
        "en_name": "Faerie Dust",
        "description": "近战或远程攻击检定：+4，触及5尺或射程60尺。\n命中：1光耀伤害，且目标陷入魅惑或中毒状态（由皮克精选择），持续至皮克精的下个回合开始。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "皮克精施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC12）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "舞光术Dancing Lights、德鲁伊伎俩Druidcraft、隐形术Invisibility（仅自身）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "侦测思想Detect Thoughts、飞行术Fly、睡眠术Sleep"
      }
    ],
    "source_file": "妖精\\皮克精\\皮克精.htm"
  },
  {
    "name": "天神使徒",
    "en_name": "Deva",
    "type_line": "中型天族（天使），守序善良",
    "size": "Medium",
    "creature_type": "天族（天使）",
    "alignment": "守序善良",
    "ac": 17,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 229,
    "hp_formula": "27d8+108",
    "speed": {
      "walk": "30尺，飞行90尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 20,
        "mod": 5,
        "save": 9
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 9
      }
    },
    "skills": {
      "洞悉": 9,
      "察觉": 9
    },
    "damage_resistances": [
      "光耀"
    ],
    "damage_immunities": [
      "魅惑",
      "力竭",
      "恐慌"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 19
    },
    "languages": "全部；心灵感应120尺",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "traits": [
      {
        "name": "圣灵复苏",
        "en_name": "Exalted Restoration",
        "description": "若天神使徒于天界山之外死去，其身体会消失，并立即在天界山处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "天神使徒对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "天神使徒发动两次圣锤攻击。"
      },
      {
        "name": "圣锤",
        "en_name": "Holy Mace",
        "description": "近战攻击检定：+8，触及5尺。命中：7（1d6+4）钝击伤害外加18（4d8）光耀伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "天神使徒施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC17）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测善恶Detect Evil and Good，形体变化Shapechange（仅野兽与类人形态，不会因此法术获得临时生命值，但无需为维持此法术而保有临时生命值或维持专注）"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "通神术Commune，死者复活Raise Dead"
      }
    ],
    "bonus_actions": [
      {
        "name": "至圣援护",
        "en_name": "Divine Aid",
        "description": "天神使徒施展疗伤术Cure Wound、次等复原术Lesser \nRestoration或移除诅咒Remove Curse \n，使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "天族\\天使\\天神使徒.htm"
  },
  {
    "name": "星天神使",
    "en_name": "Planetar",
    "type_line": "大型天族（天使），守序善良",
    "size": "Large",
    "creature_type": "天族（天使）",
    "alignment": "守序善良",
    "ac": 19,
    "initiative_bonus": 10,
    "initiative_total": 20,
    "hp": 262,
    "hp_formula": "21d10+147",
    "speed": {
      "walk": "40尺，飞行120尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 24,
        "mod": 7,
        "save": 12
      },
      "敏捷": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "体质": {
        "score": 24,
        "mod": 7,
        "save": 12
      },
      "智力": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 22,
        "mod": 6,
        "save": 11
      },
      "魅力": {
        "score": 25,
        "mod": 7,
        "save": 12
      }
    },
    "skills": {
      "察觉": 11
    },
    "damage_resistances": [
      "光耀"
    ],
    "damage_immunities": [
      "魅惑",
      "力竭",
      "恐慌"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 21
    },
    "languages": "全部，心灵感应120尺",
    "cr": 16,
    "xp": 15000,
    "pb": 5,
    "traits": [
      {
        "name": "神性警觉",
        "en_name": "Divine Awareness",
        "description": "星天神使可以辨别听见的谎言。"
      },
      {
        "name": "圣灵复苏",
        "en_name": "Exalted Restoration",
        "description": "若星天神使于天界山之外死去，其身体会消失，并立即在天界山处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "星天神使对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "星天神使发动三次光之剑攻击或使用两次圣光暴。"
      },
      {
        "name": "光之剑",
        "en_name": "Radiant Sword",
        "description": "近战攻击检定：+12，触及10尺。命中：14（2d6+7）挥砍伤害外加18（4d8）光耀伤害。"
      },
      {
        "name": "圣光爆",
        "en_name": "Holy Burst",
        "description": "敏捷豁免检定：DC20，以120尺内星天神使可见一点为中心，半径20尺球状区域内的每名敌人。失败：24（7d6）光耀伤害。成功：半伤。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "星天神使施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC20）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测善恶Detect Evil and Good"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "通神术Commune，操控天气Control Weather，驱逐善恶Dispel Evil and Good，死者复活Raise Dead"
      }
    ],
    "bonus_actions": [
      {
        "name": "至圣援护",
        "en_name": "Divine Aid",
        "description": "星天神使施展疗伤术Cure Wound、隐形术Invisibility、次等复原术Lesser \nRestoration或移除诅咒Remove \nCurse，使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "天族\\天使\\星天神使.htm"
  },
  {
    "name": "炽天神使",
    "en_name": "Solar",
    "type_line": "大型天族（天使），守序善良",
    "size": "Large",
    "creature_type": "天族（天使）",
    "alignment": "守序善良",
    "ac": 21,
    "initiative_bonus": 20,
    "initiative_total": 30,
    "hp": 297,
    "hp_formula": "22d10+176",
    "speed": {
      "walk": "50尺，飞行150尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 26,
        "mod": 8,
        "save": 8
      },
      "敏捷": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "体质": {
        "score": 26,
        "mod": 8,
        "save": 8
      },
      "智力": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "感知": {
        "score": 25,
        "mod": 7,
        "save": 7
      },
      "魅力": {
        "score": 30,
        "mod": 10,
        "save": 10
      }
    },
    "skills": {
      "察觉": 14
    },
    "damage_immunities": [
      "毒素",
      "光耀"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "中毒"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 24
    },
    "languages": "全部；心灵感应120尺",
    "cr": 21,
    "xp": 33000,
    "pb": 7,
    "traits": [
      {
        "name": "神性警觉",
        "en_name": "Divine Awareness",
        "description": "炽天神使可以辨别听见的谎言。"
      },
      {
        "name": "圣灵复苏",
        "en_name": "Exalted Restoration",
        "description": "若炽天神使于天界山之外死去，其身体会消失，并立即在天界山处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "炽天神使豁免失败时，可以将其改为豁免成功。",
        "params": "4/日"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "炽天神使对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "炽天神使发动两次翔天神剑攻击。其可以将其中一次攻击替换为使用杀戮神弓。"
      },
      {
        "name": "翔天神剑",
        "en_name": "Flying Sword",
        "description": "近战或远程攻击检定：+15，触及10尺或射程120尺。命中：22（4d6+8）挥砍伤害外加36（8d8）光耀伤害。命中或失手：翔天神剑会在被用于一次远程攻击后立即魔法性地回到炽天神使手中或悬浮在其5尺内。"
      },
      {
        "name": "杀戮神弓",
        "en_name": "Slaying Bow",
        "description": "敏捷豁免检定：DC21，单一600尺内炽天神使可见的生物。失败：若该生物的生命值为100或更低，则其立即死亡；否则，该生物受到24（4d8+6）穿刺伤害外加36（8d8）光耀伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "炽天神使施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC25）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测善恶Detect Evil and Good"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "通神术Commune，操控天气Control Weather，驱逐善恶Dispel Evil and Good，复生术Resurrection"
      }
    ],
    "bonus_actions": [
      {
        "name": "至圣援护",
        "en_name": "Divine Aid",
        "description": "炽天神使施展疗伤术Cure Wound（二环版本）、次等复原术Lesser \nRestoration或移除诅咒Remove Curse   ，使用与施法动作相同的施法属性。",
        "params": "3/日"
      }
    ],
    "legendary_actions": [
      {
        "name": "致盲凝视",
        "en_name": "Blinding Gaze",
        "description": "体质豁免检定：DC25，单一120尺内炽天神使可见的生物。失败：目标陷入目盲状态，持续1分钟。失败或成功：炽天神使直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "光耀传送",
        "en_name": "Radiant Teleport",
        "description": "炽天神使传送至多60尺至一处其可见的未占据空间。敏捷豁免检定：DC25，源自炽天神使目标空间10尺光环区域内的每名生物。失败：11（2d10）光耀伤害。成功：半伤。",
        "max_uses": 3
      }
    ],
    "source_file": "天族\\天使\\炽天神使.htm"
  },
  {
    "name": "勇气斯芬克斯",
    "en_name": "Sphinx of Valor",
    "type_line": "大型天族，守序中立",
    "size": "Large",
    "creature_type": "天族",
    "alignment": "守序中立",
    "ac": 17,
    "initiative_bonus": 12,
    "initiative_total": 22,
    "hp": 199,
    "hp_formula": "19d10+95",
    "speed": {
      "walk": "40尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 6
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 11
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 9
      },
      "感知": {
        "score": 23,
        "mod": 6,
        "save": 12
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "奥秘": 9,
      "察觉": 12,
      "宗教": 15
    },
    "damage_resistances": [
      "暗蚀",
      "光耀"
    ],
    "damage_immunities": [
      "心灵"
    ],
    "condition_immunities": [
      "魅惑",
      "恐慌"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 22
    },
    "languages": "天界语，通用语",
    "cr": 17,
    "xp": 18000,
    "pb": 6,
    "traits": [
      {
        "name": "神秘莫测",
        "en_name": "Inscrutable",
        "description": "没有魔法可以不经斯芬克斯允许远程探查斯芬克斯或探测其思想。为确定斯芬克斯意图和诚心进行的感知（洞悉）检定具有劣势。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "斯芬克斯豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "斯芬克斯发动两次利爪攻击并使用咆哮。"
      },
      {
        "name": "利爪",
        "en_name": "Claw",
        "description": "近战攻击检定：+12，触及5尺。"
      },
      {
        "name": "咆哮",
        "en_name": "Roar",
        "description": "斯芬克斯发出魔法咆哮。每当其咆哮时，咆哮具有不同的效应，详述见下（当斯芬克斯完成长休时，咆哮顺序重置）：",
        "params": "3/日"
      },
      {
        "name": "第一吼",
        "en_name": "First Roar",
        "description": "感知豁免检定：DC20，源自斯芬克斯的500尺光环区域内的每名敌人。\n失败：目标陷入恐慌状态，持续一分钟。"
      },
      {
        "name": "第二吼",
        "en_name": "Second Roar",
        "description": "感知豁免检定：DC20，源自斯芬克斯的500尺光环区域内的每名敌人。\n失败：目标陷入麻痹状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。"
      },
      {
        "name": "第三吼",
        "en_name": "Third Roar",
        "description": "体质豁免检定：DC20，源自斯芬克斯的500尺光环区域内的每名敌人。\n失败：44（8d10）雷鸣伤害，目标陷入倒地状态。\n成功：仅半伤。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "斯芬克斯施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC20）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测善恶Detect Evil and Good，奇术Thaumaturgy"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，解除魔法Dispel Magic，高等复原术Greater Restoration，英雄宴Heroes' Feast，诚实之域Zone of Truth"
      }
    ],
    "legendary_actions": [
      {
        "name": "奥术潜步",
        "en_name": "Arcane Prowl",
        "description": "斯芬克斯传送至多30尺至其可见的未占据空间，然后发动一次利爪攻击。",
        "max_uses": 3
      },
      {
        "name": "岁月之重",
        "en_name": "Weight of Years",
        "description": "体质豁免检定：DC16，单一120尺内斯芬克斯可见的生物。\n失败：目标获得1级力竭。目标具有任意力竭等级期间，其容貌衰老3d10岁。\n失败或成功：斯芬克斯直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      }
    ],
    "source_file": "天族\\斯芬克斯\\勇气斯芬克斯.htm"
  },
  {
    "name": "晓谕斯芬克斯",
    "en_name": "Sphinx of Lore",
    "type_line": "大型天族，守序中立",
    "size": "Large",
    "creature_type": "天族",
    "alignment": "守序中立",
    "ac": 17,
    "initiative_bonus": 10,
    "initiative_total": 20,
    "hp": 170,
    "hp_formula": "20d10+69",
    "speed": {
      "walk": "40尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "奥秘": 12,
      "历史": 12,
      "察觉": 8,
      "宗教": 12
    },
    "damage_resistances": [
      "暗蚀",
      "光耀"
    ],
    "damage_immunities": [
      "心灵"
    ],
    "condition_immunities": [
      "魅惑",
      "恐慌"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 18
    },
    "languages": "天界语，通用语",
    "cr": 11,
    "xp": 7200,
    "pb": 4,
    "traits": [
      {
        "name": "神秘莫测",
        "en_name": "Inscrutable",
        "description": "没有魔法可以不经斯芬克斯允许远程探查斯芬克斯或探测其思想。为确定斯芬克斯意图和诚心进行的感知（洞悉）检定具有劣势。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "斯芬克斯豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "斯芬克斯发动三次利爪攻击。"
      },
      {
        "name": "利爪",
        "en_name": "Claw",
        "description": "近战攻击检定：+8，触及5尺。\n命中：14（3d6+4）挥砍伤害。"
      },
      {
        "name": "碎心咆哮",
        "en_name": "Mind-Rending Roar",
        "description": "感知豁免检定：DC16，源自斯芬克斯的300尺光环区域内的每名敌人。\n失败：35（10d6）心灵伤害，并且目标陷入失能直至斯芬克斯下个回合开始。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "斯芬克斯施展以下一道法术，无需材料成分并使用智力作为施法属性（法术豁免DC16）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，鉴定术Identify，法师之手Mage Hand，次级幻象Minor Illusion，魔法伎俩Prestidigitation"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "解除魔法Dispel Magic，通晓传奇Legend Lore，物件定位术Locate Object，位面转移Plane Shift，解除诅咒Remove Curse，巧言术Tongues"
      }
    ],
    "legendary_actions": [
      {
        "name": "奥术潜步",
        "en_name": "Arcane Prowl",
        "description": "斯芬克斯传送至多30尺至其可见的未占据空间，然后发动一次利爪攻击。",
        "max_uses": 3
      },
      {
        "name": "岁月之重",
        "en_name": "Weight of Years",
        "description": "体质豁免检定：DC16，单一120尺内斯芬克斯可见的生物。\n失败：目标获得1级力竭。目标具有任意力竭等级期间，其容貌衰老3d10岁。\n失败或成功：斯芬克斯直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      }
    ],
    "source_file": "天族\\斯芬克斯\\晓谕斯芬克斯.htm"
  },
  {
    "name": "求索斯芬克斯",
    "en_name": "Sphinx of Wonder",
    "type_line": "微型天族，守序中立",
    "size": "Tiny",
    "creature_type": "天族",
    "alignment": "守序中立",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 24,
    "hp_formula": "7d4+7",
    "speed": {
      "walk": "20尺，飞行40尺"
    },
    "abilities": {
      "力量": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "奥秘": 4,
      "宗教": 4,
      "隐匿": 5
    },
    "damage_resistances": [
      "暗蚀",
      "心灵",
      "光耀"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "天界语，通用语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic \nResistance",
        "description": "斯芬克斯对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "撕裂",
        "en_name": "Rend",
        "description": "近战攻击检定：+5，触及5尺。命中：5（1d4+3）挥砍伤害外加7（2d6）光耀伤害。"
      }
    ],
    "reactions": [
      {
        "name": "灵光乍现",
        "en_name": "Burst of \nIngenuity",
        "description": "触发：斯芬克斯或其30尺内另一生物进行一次属性检定或豁免检定。响应：  \n斯芬克斯令其结果+2。",
        "params": "2/日"
      }
    ],
    "source_file": "天族\\斯芬克斯\\求索斯芬克斯.htm"
  },
  {
    "name": "隐秘斯芬克斯",
    "en_name": "Sphinx of Secrets",
    "type_line": "大型天族，守序中立",
    "size": "Large",
    "creature_type": "天族",
    "alignment": "守序中立",
    "ac": 16,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 136,
    "hp_formula": "16d10+48",
    "speed": {
      "walk": "40尺，飞行60尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "历史": 7,
      "察觉": 7,
      "宗教": 7
    },
    "damage_resistances": [
      "暗蚀",
      "光耀"
    ],
    "damage_immunities": [
      "心灵"
    ],
    "condition_immunities": [
      "魅惑",
      "恐慌"
    ],
    "senses": {
      "真实视觉": 60,
      "被动察觉": 17
    },
    "languages": "天界语，通用语",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "traits": [
      {
        "name": "神秘莫测",
        "en_name": "Inscrutable",
        "description": "没有魔法可以不经斯芬克斯允许远程探查斯芬克斯或探测其思想。为确定斯芬克斯意图和诚心进行的感知（洞悉）检定具有劣势。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "斯芬克斯对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "斯芬克斯发动三次利爪攻击。其可以将其中一次攻击替换为谜题诅咒。"
      },
      {
        "name": "利爪",
        "en_name": "Claw",
        "description": "近战攻击检定：+7，触及5尺。\n命中：13（2d8+4）挥砍伤害外加7（2d6）光耀伤害。"
      },
      {
        "name": "谜题诅咒",
        "en_name": "Curse of the Riddle",
        "description": "智力豁免检定：DC15，单一60尺内斯芬克斯可见的生物。\n失败：21（6d6）心灵伤害，并且目标将被谜题诅咒。被诅咒的生物的属性检定和攻击检定具有劣势。此外，若被诅咒的生物执行魔法动作，其必须成功通过一次DC15的智力豁免，否则动作被浪费。被诅咒的目标可以执行研究动作来进行一次DC15的智力检定以解决谜题，成功则诅咒结束。斯芬克斯诅咒另一名生物时，诅咒提前结束。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "斯芬克斯施展以下一道法术，无需材料成分并使用智力作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：侦测魔法",
        "en_name": "Detect Magic",
        "description": ""
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "物件定位术Locate Object，解除诅咒Remove Curse"
      }
    ],
    "source_file": "天族\\斯芬克斯\\隐秘斯芬克斯.htm"
  },
  {
    "name": "初生吸血鬼",
    "en_name": "Vampire Spawn",
    "type_line": "中型或小型亡灵，中立邪恶",
    "size": "Medium",
    "creature_type": "或小型亡灵",
    "alignment": "中立邪恶",
    "ac": 16,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 90,
    "hp_formula": "12d8+36",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 3
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "察觉": 3,
      "隐匿": 6
    },
    "damage_resistances": [
      "暗蚀"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 13
    },
    "languages": "通用语以及一门其他语言",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "蛛行",
        "en_name": "Spider Climb",
        "description": "吸血鬼可以在难以攀爬的表面上攀爬，包括沿着天花板移动，且无需为此进行属性检定。"
      },
      {
        "name": "吸血鬼弱点",
        "en_name": "Vampire Weakness",
        "description": "吸血鬼拥有以下弱点："
      },
      {
        "name": "禁入",
        "en_name": "Forbiddance",
        "description": "吸血鬼未得到一位居住者的邀请时无法进入相应的民宅。"
      },
      {
        "name": "流水",
        "en_name": "Running \nWater",
        "description": "若吸血鬼在流水中结束回合，其受到20强酸伤害。"
      },
      {
        "name": "桩刺",
        "en_name": "Stake to the Heart",
        "description": "吸血鬼陷入失能状态期间，若用一把造成穿刺伤害的武器钉入其心脏，则吸血鬼被摧毁。"
      },
      {
        "name": "日照",
        "en_name": "Sunlight",
        "description": "若吸血鬼在阳光下开始其回合，其受到20光耀伤害。若其身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "吸血鬼发动两次爪击攻击并使用啃咬。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+6，触及5尺。命中：8（2d4+3）挥砍伤害，且若目标生物体型不超过中型，则其被双爪之一擒抱，陷入受擒状态（逃脱DC13）"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "体质豁免检定：DC14，单一5尺内的自愿或陷入受擒、失能或束缚状态的生物。\n失败：5（1d4+3）穿刺伤害外加10（3d6）暗蚀伤害。目标的生命值上限减少等于其受到暗蚀伤害的数值，且吸血鬼恢复等量生命值。"
      }
    ],
    "bonus_actions": [
      {
        "name": "不死者机敏",
        "en_name": "Deathless Agility",
        "description": "吸血鬼执行疾走或撤离动作。"
      }
    ],
    "source_file": "多类型\\吸血鬼\\初生吸血鬼.htm"
  },
  {
    "name": "吸血夜魇",
    "en_name": "Vampire Nightbringer",
    "type_line": "中型或小型亡灵，中立邪恶",
    "size": "Medium",
    "creature_type": "或小型亡灵",
    "alignment": "中立邪恶",
    "ac": 16,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 142,
    "hp_formula": "19d8+57",
    "speed": {
      "walk": "30尺，飞行30尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 5,
      "隐匿": 7
    },
    "damage_immunities": [
      "暗蚀",
      "寒冷"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 15
    },
    "languages": "通用语以及两门其他语言",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "traits": [
      {
        "name": "日照超敏",
        "en_name": "Sunlight Hypersensitivity",
        "description": "若吸血夜魇在阳光下开始其回合，其受到10光耀伤害。若其身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "吸血夜魇发动一次啃咬攻击和一次幽影袭攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+7，触及5尺。命中：7（1d6+4）穿刺伤害外加10（3d6）暗蚀伤害。目标的生命值上限减少等于其受到暗蚀伤害的数值，且吸血夜魇恢复等量生命值。"
      },
      {
        "name": "幽影袭",
        "en_name": "Shadow Strike",
        "description": "近战攻击检定：+7，触及5尺。命中：7（1d6+4）挥砍伤害外加14（4d6）寒冷伤害。"
      }
    ],
    "bonus_actions": [
      {
        "name": "幽影隐匿",
        "en_name": "Shadow Steath",
        "description": "若吸血夜魇身处微光光照或黑暗中，其执行躲藏动作。"
      }
    ],
    "source_file": "多类型\\吸血鬼\\吸血夜魇.htm"
  },
  {
    "name": "吸血鬼",
    "en_name": "Vampire",
    "type_line": "中型或小型亡灵，守序邪恶",
    "size": "Medium",
    "creature_type": "或小型亡灵",
    "alignment": "守序邪恶",
    "ac": 16,
    "initiative_bonus": 14,
    "initiative_total": 24,
    "hp": 195,
    "hp_formula": "23d8+92",
    "speed": {
      "walk": "40尺，攀爬40尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 9
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 9
      },
      "智力": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 7
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 9
      }
    },
    "skills": {
      "察觉": 7,
      "隐匿": 9
    },
    "damage_resistances": [
      "暗蚀"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 17
    },
    "languages": "通用语以及两门其他语言",
    "cr": 13,
    "xp": 10000,
    "pb": 5,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "吸血鬼豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      },
      {
        "name": "雾隐遁行",
        "en_name": "Misty \nEscape",
        "description": "若吸血鬼在其休眠地之外生命值降至0，其立即使用变形动作（无需动作）。若此时其无法使用变形，则其被摧毁。当吸血鬼处于迷雾形态且具有0生命值时，其无法变回其吸血鬼形态，且必须在2小时内返回其休眠地，否则亦会被摧毁。一旦返回其休眠地，其变回吸血鬼形态并陷入麻痹状态直至其恢复任意生命值，吸血鬼在此地停留1小时后恢复1生命值。"
      },
      {
        "name": "吸血鬼弱点",
        "en_name": "Vampire Weakness",
        "description": "吸血鬼拥有以下弱点："
      },
      {
        "name": "禁入",
        "en_name": "Forbiddance",
        "description": "吸血鬼未得到一位居住者的邀请时无法进入相应的民宅。"
      },
      {
        "name": "流水",
        "en_name": "Running \nWater",
        "description": "若吸血鬼在流水中结束回合，其受到20强酸伤害。"
      },
      {
        "name": "桩刺",
        "en_name": "Stake to the Heart",
        "description": "吸血鬼位于其休眠地且陷入失能状态期间，若用一把造成穿刺伤害的武器钉入其心脏，其陷入麻痹状态直至该武器被移除。"
      },
      {
        "name": "日照",
        "en_name": "Sunlight",
        "description": "若吸血鬼在阳光下开始其回合，其受到20光耀伤害。若其身处阳光下，其进行的属性检定和攻击检定具有劣势。\n动作Actions\n\n多重攻击Multiattack（仅吸血鬼形态）。吸血鬼发动两次葬送打击攻击并使用啃咬。"
      },
      {
        "name": "葬送打击",
        "en_name": "Grave Strike",
        "description": "近战攻击检定：+9，触及5尺。命中：8（1d8+4）钝击伤害外加7（2d6）暗蚀伤害。若目标生物不超过中型，则其被双手之一擒抱，陷入受擒状态（逃脱DC14）",
        "params": "仅吸血鬼形态"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "体质豁免检定：DC17，单一5尺内的自愿或陷入受擒、失能或束缚状态的生物。失败：6（1d4+4）穿刺伤害外加13（3d8）暗蚀伤害。目标的生命值上限减少等于其受到暗蚀伤害的数值，且吸血鬼恢复等量生命值。",
        "params": "仅蝙蝠或吸血鬼形态"
      },
      {
        "name": "初生吸血鬼",
        "en_name": "Vampire \nSpawn",
        "description": ""
      }
    ],
    "bonus_actions": [
      {
        "name": "魅惑",
        "en_name": "Charm",
        "description": "吸血鬼施展魅惑类人Charm \nPerson ，无需法术成分并使用魅力作为施法属性（法术豁免DC17），且其持续时间变为24小时。以此被魅惑的生物即吸血鬼啃咬的自愿目标，此时造成的伤害不会结束该法术。法术结束后，目标不会意识到自己被吸血鬼魅惑过。",
        "params": "充能5~6"
      },
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "若吸血鬼未身处阳光下或流水中，其变形为微型蝙蝠（速度5尺，飞行速度30尺）或中型迷雾（速度5尺，飞行20尺【悬浮】），或是变回其吸血鬼形态。其携带的任何事物都会随之变化。"
      }
    ],
    "legendary_actions": [
      {
        "name": "诱骗",
        "en_name": "Beguile",
        "description": "吸血鬼施展命令术Command，无需法术成分并使用魅力作为施法属性（法术豁免DC17）。吸血鬼直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "不死者打击",
        "en_name": "Deathless \nStrike",
        "description": "吸血鬼移动等于其速度一半的距离，并发动一次葬送打击攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "多类型\\吸血鬼\\吸血鬼.htm"
  },
  {
    "name": "吸血鬼暗影尊主",
    "en_name": "Vampire Umbral Lord",
    "type_line": "中型或小型亡灵，守序邪恶",
    "size": "Medium",
    "creature_type": "或小型亡灵",
    "alignment": "守序邪恶",
    "ac": 16,
    "initiative_bonus": 14,
    "initiative_total": 24,
    "hp": 187,
    "hp_formula": "22d8+88",
    "speed": {
      "walk": "40尺，攀爬40尺，飞行40尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 10
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 9
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 8
      },
      "魅力": {
        "score": 21,
        "mod": 5,
        "save": 10
      }
    },
    "skills": {
      "奥秘": 9,
      "察觉": 13,
      "隐匿": 9
    },
    "damage_immunities": [
      "寒冷",
      "暗蚀"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭"
    ],
    "senses": {
      "盲视": 120,
      "被动察觉": 23
    },
    "languages": "通用语以及三门其他语言",
    "cr": 15,
    "xp": 13000,
    "pb": 5,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "吸血鬼豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      },
      {
        "name": "幽影遁行",
        "en_name": "Shadow Escape",
        "description": "若吸血鬼在其休眠地之外生命值降至0，其立即传送回其休眠地；但若此时吸血鬼身处阳光光下或流水中，则其将被摧毁。吸血鬼一旦返回其休眠地，其陷入麻痹状态，持续1小时，其在此后恢复1生命值。"
      },
      {
        "name": "吸血鬼弱点",
        "en_name": "Vampire Weakness",
        "description": "吸血鬼拥有以下弱点："
      },
      {
        "name": "禁入",
        "en_name": "Forbiddance",
        "description": "吸血鬼未得到一位居住者的邀请时无法进入相应的民宅。"
      },
      {
        "name": "流水",
        "en_name": "Running \nWater",
        "description": "若吸血鬼在流水中结束回合，其受到20强酸伤害。"
      },
      {
        "name": "桩刺",
        "en_name": "Stake to the Heart",
        "description": "吸血鬼位于其休眠地且陷入失能状态期间，若用一把造成穿刺伤害的武器钉入其心脏，其陷入麻痹状态直至该武器被移除。"
      },
      {
        "name": "日照",
        "en_name": "Sunlight",
        "description": "若吸血鬼在阳光下开始其回合，其受到20光耀伤害。若其身处阳光下，其进行的属性检定和攻击检定具有劣势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "吸血鬼使用葬送打击或灾疫射线发动共计两次攻击。"
      },
      {
        "name": "葬送打击",
        "en_name": "Grave Strike",
        "description": "近战攻击检定：+10，触及5尺。命中：9（1d8+5）挥砍伤害外加13（3d8）暗蚀伤害。"
      },
      {
        "name": "灾疫射线",
        "en_name": "Sickening Ray",
        "description": "远程攻击检定：+10，射程120尺。命中：16（2d10+5）暗蚀伤害，且目标陷入中毒状态直至吸血鬼的下个回合开始。"
      },
      {
        "name": "哈达之欲",
        "en_name": "Hunger of Hadar",
        "description": "吸血鬼施展哈达之欲Hunger \nof Hadar（五环版本） \n  ，无需法术成分并使用魅力作为施法属性（法术豁免DC18）。",
        "params": "充能5~6"
      }
    ],
    "bonus_actions": [
      {
        "name": "猩红征收",
        "en_name": "Sanguine Drain",
        "description": "体质豁免检定：DC18，单一30尺内吸血鬼可见的非构装非亡灵生物。失败：14（4d6）暗蚀伤害。目标的生命值上限减少等于其受到暗蚀伤害的数值，且吸血鬼恢复等量生命值。"
      }
    ],
    "legendary_actions": [
      {
        "name": "诱骗",
        "en_name": "Beguile",
        "description": "吸血鬼施展命令术Command，无需法术成分并使用魅力作为施法属性（法术豁免DC18）。吸血鬼直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "暗影袭",
        "en_name": "Umbral Strike",
        "description": "吸血鬼移动至多等于其速度一半的距离，并发动一次葬送打击或灾疫射线攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "多类型\\吸血鬼\\吸血鬼暗影尊主.htm"
  },
  {
    "name": "血仆",
    "en_name": "Vampire Familiar",
    "type_line": "中型或小型类人，中立邪恶",
    "size": "Medium",
    "creature_type": "或小型类人",
    "alignment": "中立邪恶",
    "ac": 15,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 65,
    "hp_formula": "10d8+20",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 5
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 4,
      "游说": 4,
      "隐匿": 7
    },
    "damage_resistances": [
      "暗蚀"
    ],
    "damage_immunities": [
      "魅惑（对其吸血鬼尊长无效）"
    ],
    "equipment": "匕首（10）",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 14
    },
    "languages": "通用语以及一门其他语言",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "血裔连结",
        "en_name": "Vampiric Connection",
        "description": "若血仆与其吸血鬼尊长身处同一位面，该吸血鬼就能用心灵感应与血仆交流，亦能用血仆的感官感知事物。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "血仆发动两次暗影匕首攻击。"
      },
      {
        "name": "暗影匕首",
        "en_name": "Umbral Dagger",
        "description": "近战或远程攻击检定：+5，触及5尺或射程20/60尺命中：5（1d4+3）穿刺伤害外加7（3d4）暗蚀伤害。若目标因该攻击生命值降至0，则目标伤势稳定但陷入中毒状态1小时。以此法中毒期间，目标还会陷入麻痹状态。"
      }
    ],
    "bonus_actions": [
      {
        "name": "不死者机敏",
        "en_name": "Deathless Agility",
        "description": "血仆执行疾走或撤离动作。"
      }
    ],
    "source_file": "多类型\\吸血鬼\\血仆.htm"
  },
  {
    "name": "元初天劫",
    "en_name": "Elemental Cataclysm",
    "type_line": "超巨型元素（泰坦），混乱邪恶",
    "size": "Gargantuan",
    "creature_type": "元素（泰坦）",
    "alignment": "混乱邪恶",
    "ac": 20,
    "initiative_bonus": 18,
    "initiative_total": 28,
    "hp": 370,
    "hp_formula": "20d20+160",
    "speed": {
      "walk": "60尺，掘穴60尺，飞行80尺（悬浮），游泳80尺"
    },
    "abilities": {
      "力量": {
        "score": 26,
        "mod": 8,
        "save": 8
      },
      "敏捷": {
        "score": 19,
        "mod": 4,
        "save": 11
      },
      "体质": {
        "score": 27,
        "mod": 8,
        "save": 15
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 9
      },
      "魅力": {
        "score": 9,
        "mod": -1,
        "save": 6
      }
    },
    "traits": [
      {
        "name": "遁地",
        "en_name": "Earth Glide",
        "description": "天劫可以掘穴穿过非魔法且未经加工的泥土及岩石。遁地期间，天劫不会破坏其穿过的任何材质。"
      },
      {
        "name": "攻城怪物",
        "en_name": "Siege Monster",
        "description": "天劫对物件和建筑造成双倍伤害。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "天劫发动两次元能爆发攻击。"
      },
      {
        "name": "元能爆发",
        "en_name": "Elemental Burst",
        "description": "近战或远程攻击检定：+15，触及30尺或射程150尺。命中：25（5d6+8）点伤害，伤害类型由天劫从下列选项中选择一种：强酸、寒冷、火焰、闪电、雷鸣。"
      },
      {
        "name": "操控天气",
        "en_name": "Control Weather",
        "description": "天劫施展法术操控天气Control Weather，无需法术成分并使用体质作为施法属性。"
      },
      {
        "name": "大灾变",
        "en_name": "Cataclysmic Event",
        "description": "元初天劫从下列效应中随机制造一种（掷1d4）：",
        "params": "充能4~6"
      }
    ],
    "legendary_actions": [
      {
        "name": "天灾爆发",
        "en_name": "Eruptions",
        "description": "天劫发动一次元能爆发攻击。",
        "max_uses": 3
      },
      {
        "name": "震地神行",
        "en_name": "Rumbling Movement",
        "description": "天劫移动至多等于其速度、飞行速度或游泳速度的距离且不会引发借机攻击。在天劫移动过程中，位于天劫5尺内的每名生物都会被选为一次以下效应的目标。体质豁免检定：DC23。失败：目标陷入倒地状态。失败或成功：天劫直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      }
    ],
    "source_file": "多类型\\泰坦\\元初天劫.htm"
  },
  {
    "name": "克拉肯",
    "en_name": "Kraken",
    "type_line": "超巨型怪兽（泰坦），混乱邪恶",
    "size": "Gargantuan",
    "creature_type": "怪兽（泰坦）",
    "alignment": "混乱邪恶",
    "ac": 18,
    "initiative_bonus": 14,
    "initiative_total": 24,
    "hp": 481,
    "hp_formula": "26d20+208",
    "speed": {
      "walk": "30尺，游泳120尺"
    },
    "abilities": {
      "力量": {
        "score": 30,
        "mod": 10,
        "save": 17
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 7
      },
      "体质": {
        "score": 26,
        "mod": 8,
        "save": 15
      },
      "智力": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "感知": {
        "score": 18,
        "mod": 4,
        "save": 11
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 5
      }
    },
    "skills": {
      "历史": 13,
      "察觉": 11
    },
    "damage_immunities": [
      "寒冷",
      "闪电"
    ],
    "condition_immunities": [
      "恐慌",
      "受擒",
      "麻痹",
      "束缚"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 21
    },
    "languages": "理解深渊语、天界语、炼狱语、原初语，但不会说；心灵感应120尺",
    "cr": 23,
    "xp": 50000,
    "pb": 7,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "克拉肯可以在空气和水中呼吸。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "克拉肯豁免失败时，可以将其改为豁免成功。",
        "params": "4/日，或巢穴内5/日"
      },
      {
        "name": "攻城怪物",
        "en_name": "Siege Monster",
        "description": "克拉肯对物件和建筑物造成双倍伤害。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "克拉肯发动两次触须攻击，并使用抛投、闪电打击、吞咽三者之一。"
      },
      {
        "name": "触须",
        "en_name": "Tentacle",
        "description": "近战攻击检定：+17，触及30尺。命中：24（4d6+10）钝击伤害。目标被十条触须之一擒抱，陷入受擒状态（逃脱DC20），且目标陷入束缚状态直至擒抱结束。"
      },
      {
        "name": "抛投",
        "en_name": "Fling",
        "description": "克拉肯将一名受擒于其的不超过大型的生物投至其60尺内一处其可见且不在空中的空间。敏捷豁免检定：DC25，被投出的生物以及目标空间内的每名生物。失败：18（4d8）钝击伤害，且目标陷入倒地状态。成功：仅半伤。"
      },
      {
        "name": "闪电打击",
        "en_name": "Lightning Strike",
        "description": "敏捷豁免检定：DC23，单一120尺内克拉肯可见的生物。失败：33（6d10）闪电伤害。成功：半伤。"
      },
      {
        "name": "吞咽",
        "en_name": "Swallow",
        "description": "敏捷豁免检定：DC25，单一正受擒于克拉肯的生物（克拉肯同时能吞咽的生物数上限为四）。失败：23（3d8+10）穿刺伤害。若目标体型不超过大型，克拉肯吞下目标，并结束其受擒状态。被吞咽期间，目标陷入束缚状态，对克拉肯体外的攻击或其他效应而言处于全身掩护 \n，并在每个克拉肯蛇的回合开始时受到24（7d6）强酸伤害。"
      }
    ],
    "legendary_actions": [
      {
        "name": "风暴束",
        "en_name": "Storm Bolt",
        "description": "克拉肯使用闪电打击。",
        "max_uses": 3
      },
      {
        "name": "剧毒墨云",
        "en_name": "Toxic Ink",
        "description": "体质豁免检定：DC23，源自克拉肯的15尺光环区域内的每名生物。失败：目标陷入目盲和中毒状态，直至克拉肯的下个回合结束。然后克拉肯移动等于其速度的距离。失败或成功：克拉肯直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      }
    ],
    "source_file": "多类型\\泰坦\\克拉肯.htm"
  },
  {
    "name": "吞世黏浆",
    "en_name": "Blob of Annihilation",
    "type_line": "超巨型泥怪（泰坦），中立邪恶",
    "size": "Gargantuan",
    "creature_type": "泥怪（泰坦）",
    "alignment": "中立邪恶",
    "ac": 18,
    "initiative_bonus": 16,
    "initiative_total": 26,
    "hp": 448,
    "hp_formula": "23d20+207",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 27,
        "mod": 8,
        "save": 8
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 9
      },
      "体质": {
        "score": 28,
        "mod": 9,
        "save": 16
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "traits": [
      {
        "name": "星界内爆",
        "en_name": "Astral Implosion",
        "description": "若黏浆生命值降至0，则其内爆并将其吞入体内的一切生物和物件喷进星界海。黏浆随即消失，只在原地留下一滩覆盖600尺的粘液。黏浆会在1d20年内于物质位面中的某个随机世界重组。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "黏浆豁免失败时，可以将其改为豁免成功。",
        "params": "4/日"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "黏浆对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "黏浆发动两次伪足攻击并使用吞没。其可以将其中一次攻击替换为使用缚体黏浆。"
      },
      {
        "name": "伪足",
        "en_name": "Pseudopod",
        "description": "近战攻击检定：+15，触及30尺。命中：24（3d10+8）力场伤害。"
      },
      {
        "name": "吞没",
        "en_name": "Engulf",
        "description": "黏浆移动至多等于其速度的距离，并且可以移动穿过不超过巨型的生物或物件所处的空间。力量豁免检定：DC23，在黏浆移动过程中，所处空间首次被黏浆经过的每个生物或物件。失败：目标被黏浆吞没。被吞没期间，目标对黏浆体外的攻击或其他效应而言处于全身掩护，且当黏浆移动时，被吞没目标也将一并移动。非魔法物件被吞没1分钟后被摧毁。"
      },
      {
        "name": "缚体黏浆",
        "en_name": "Restraining Glob",
        "description": "黏浆向600尺内的一名不超过大型的生物射出一团粘液。敏捷豁免检定：DC23，被指定的生物。失败：18（3d6+8）强酸伤害。粘液令目标向黏浆直线滚动60尺，且目标陷入束缚状态直至其下个回合结束，此时目标身上的粘液无害地溶解。成功：仅半伤。"
      }
    ],
    "legendary_actions": [
      {
        "name": "衰竭",
        "en_name": "Decay",
        "description": "黏浆对被其吞没的每名生物造成14（4d6）暗蚀伤害。黏浆直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "攫抓黏浆",
        "en_name": "Grasping \nGlob",
        "description": "黏浆使用缚体黏浆。黏浆直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "黏肢挥打",
        "en_name": "Lashing \nGoop",
        "description": "黏浆发动一次伪足攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "多类型\\泰坦\\吞世黏浆.htm"
  },
  {
    "name": "巨神兵",
    "en_name": "Colossus",
    "type_line": "超巨型构装（泰坦），无阵营",
    "size": "Gargantuan",
    "creature_type": "构装（泰坦）",
    "alignment": "无阵营",
    "ac": 23,
    "initiative_bonus": 16,
    "initiative_total": 26,
    "hp": 553,
    "hp_formula": "27d20+270",
    "speed": {
      "walk": "60尺"
    },
    "abilities": {
      "力量": {
        "score": 30,
        "mod": 10,
        "save": 10
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 8
      },
      "体质": {
        "score": 30,
        "mod": 10,
        "save": 10
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 8
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "damage_resistances": [
      "暗蚀",
      "光耀"
    ],
    "damage_immunities": [
      "毒素",
      "心灵"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "麻痹",
      "石化",
      "中毒",
      "震慑",
      "昏迷"
    ],
    "senses": {
      "真实视觉": 300,
      "被动察觉": 10
    },
    "languages": "理解天界语和通用语，但不会说",
    "cr": 25,
    "xp": 75000,
    "pb": 8,
    "traits": [
      {
        "name": "不变形态",
        "en_name": "Immutable Form",
        "description": "巨神兵无法变形。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "巨神兵豁免失败时，可以将其改为豁免成功。",
        "params": "4/日"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "巨神兵对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "攻城怪物",
        "en_name": "Siege \nMonster",
        "description": "巨神兵对物件和建筑造成双倍伤害。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "巨神兵使用猛击或光耀射线发动共计三次攻击。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+18，触及20尺。命中：32（4d10+10）钝击伤害，且巨神兵将目标直线推离至多20尺。"
      },
      {
        "name": "光耀射线",
        "en_name": "Radiant Ray",
        "description": "远程攻击检定：+18，射程300尺。命中：22（4d10）光耀伤害。若目标生物体型不超过大型，则其陷入倒地状态。"
      },
      {
        "name": "神能光束炮",
        "en_name": "Divine Beam",
        "description": "敏捷豁免检定：DC26，300尺长、5尺宽的线状区域内的每名生物。失败：65（10d12）光耀伤害。成功：半伤。失败或成功：若生物因光束炮生命值降至0，则其被解离为尘埃，留下其着装或携带的任意魔法物品。",
        "params": "充能5~6"
      }
    ],
    "legendary_actions": [
      {
        "name": "圣裁",
        "en_name": "Smite",
        "description": "巨神兵发动一次光耀射线攻击。",
        "max_uses": 3
      },
      {
        "name": "践踏",
        "en_name": "Stomp",
        "description": "巨神兵移动至多等于其速度一半的距离且不会引发借机攻击，且移动过程中其可以在任意时刻发动一次猛击攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "多类型\\泰坦\\巨神兵.htm"
  },
  {
    "name": "泰拉斯奎",
    "en_name": "Tarrasque",
    "type_line": "超巨型怪兽（泰坦），无阵营",
    "size": "Gargantuan",
    "creature_type": "怪兽（泰坦）",
    "alignment": "无阵营",
    "ac": 25,
    "initiative_bonus": 18,
    "initiative_total": 28,
    "hp": 697,
    "hp_formula": "34d20+340",
    "speed": {
      "walk": "60尺，掘穴40尺，攀爬60尺"
    },
    "abilities": {
      "力量": {
        "score": 30,
        "mod": 10,
        "save": 10
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 9
      },
      "体质": {
        "score": 30,
        "mod": 10,
        "save": 10
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": 5
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 9
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 9
      }
    },
    "skills": {
      "察觉": 9
    },
    "damage_resistances": [
      "钝击",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "耳聋",
      "恐慌",
      "麻痹",
      "中毒"
    ],
    "senses": {
      "盲视": 120,
      "被动察觉": 19
    },
    "languages": "无",
    "cr": 30,
    "xp": 155000,
    "pb": 9,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "泰拉斯奎豁免失败时，可以将其改为豁免成功。",
        "params": "6/日"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "泰拉斯奎对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "反弹甲壳",
        "en_name": "Reflective Carapace",
        "description": "当泰拉斯奎被指定为法术魔法飞弹Magic \nMissile 或一道需要远程攻击检定的法术的目标时，掷1d6。骰值为1-5时，泰拉斯奎不受其影响。骰值为6时，泰拉斯奎不受其影响并反弹该法术，将法术目标改为其施展者。"
      },
      {
        "name": "攻城怪物",
        "en_name": "Siege Monster",
        "description": "泰拉斯奎对物件和建筑造成双倍伤害。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "泰拉斯奎发动一次啃咬攻击，并使用爪击或尾击发动共计三次攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+19，触及15尺。命中：36（4d12+10）穿刺伤害，且目标陷入受擒状态（逃脱DC20）。目标陷入束缚状态且无法传送，直至擒抱结束。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+19，触及15尺。命中：28（4d8+10）挥砍伤害。"
      },
      {
        "name": "尾击",
        "en_name": "Tail",
        "description": "近战攻击检定：+19，触及30尺。命中：23（3d8+10）钝击伤害。若目标生物体型不超过巨型，则其陷入倒地状态。"
      },
      {
        "name": "雷霆怒号",
        "en_name": "Thunderous Bellow",
        "description": "体质豁免检定：DC27，150尺锥状区域内的每名生物及未被着装或携带的每个物件。失败：78（12d12）雷鸣伤害，且目标陷入耳聋和恐慌状态直至其下个回合结束。成功：仅半伤。",
        "params": "充能5~6"
      }
    ],
    "bonus_actions": [
      {
        "name": "吞咽",
        "en_name": "Swallow",
        "description": "力量豁免检定：DC27，单一不超过大型的正受擒于泰拉斯奎的生物（泰拉斯奎同时能吞咽的生物数上限为六）。失败：泰拉斯奎吞咽目标，并结束其受擒状态。被吞咽期间，目标陷入目盲和束缚状态，且无法传送，其对泰拉斯奎体外的攻击或其他效应而言处于全身掩护，并在泰拉斯奎的回合开始时受56（16d6）强酸伤害。"
      }
    ],
    "legendary_actions": [
      {
        "name": "突击",
        "en_name": "Onslaught",
        "description": "泰拉斯奎移动至多等于其速度一半的距离并发动一次爪击或尾击攻击。",
        "max_uses": 3
      },
      {
        "name": "撼世神行",
        "en_name": "World-Shaking Movement",
        "description": "泰拉斯奎移动至多等于其速度的距离。在此次移动结束时，泰拉斯奎制造一道骤然爆发的震波，覆盖源自其的60尺光环区域。位于该区域内的生物失去其专注，且若其不超过中型，则其陷入倒地状态。泰拉斯奎直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      }
    ],
    "source_file": "多类型\\泰坦\\泰拉斯奎.htm"
  },
  {
    "name": "至高天",
    "en_name": "Empyrean",
    "type_line": "巨型天族或邪魔（泰坦），绝对中立",
    "size": "Huge",
    "creature_type": "天族或邪魔（泰坦）",
    "alignment": "绝对中立",
    "ac": 22,
    "initiative_bonus": 19,
    "initiative_total": 29,
    "hp": 346,
    "hp_formula": "21d12+210",
    "speed": {
      "walk": "50尺，飞行50尺（悬浮），游泳50尺"
    },
    "abilities": {
      "力量": {
        "score": 30,
        "mod": 10,
        "save": 17
      },
      "敏捷": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "体质": {
        "score": 30,
        "mod": 10,
        "save": 10
      },
      "智力": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "感知": {
        "score": 22,
        "mod": 6,
        "save": 13
      },
      "魅力": {
        "score": 27,
        "mod": 8,
        "save": 8
      }
    },
    "skills": {
      "洞悉": 13,
      "察觉": 13
    },
    "damage_resistances": [
      "钝击",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "暗蚀",
      "光耀"
    ],
    "senses": {
      "真实视觉": 120,
      "被动察觉": 23
    },
    "languages": "全部",
    "cr": 23,
    "xp": 50000,
    "pb": 7,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "至高天豁免失败时，可以将其改为豁免成功。",
        "params": "4/日"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "至高天对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "至高天使用圣洁武器或神力射线发动共计两次攻击。"
      },
      {
        "name": "圣洁武器",
        "en_name": "Scared Weapon",
        "description": "近战攻击检定：+17，触及10尺。命中：31（6d6+10）力场伤害，且目标陷入震慑状态直至至高天的下个回合开始。目标可以选择不受震慑，改为额外受到21点无视抗性或免疫的力场伤害。"
      },
      {
        "name": "神力射线",
        "en_name": "Divine Ray",
        "description": "远程攻击检定：+15，射程600尺。命中：35（6d8+8）暗蚀或光耀伤害（由至高天选择）。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "至高天施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC23）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "安定心神Calm Emotions，高等复原术Greater Restoration，行动无踪Pass without Trance，水下呼吸Water Breathing"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "通神术Commune，驱逐善恶Dispel Evil and Good，位面转移Plane Shift"
      }
    ],
    "legendary_actions": [
      {
        "name": "鼓舞",
        "en_name": "Bolster",
        "description": "至高天获得10临时生命值，且直至至高天的下个回合结束，至高天及其30尺内的盟友进行的D20检定具有优势。至高天直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "荣光撼天",
        "en_name": "Shockwave \nof Glory",
        "description": "体质豁免检定：DC23，源自至高天的30尺光环区域内的每名生物。失败：27（6d8）力场伤害，且目标陷入倒地状态。成功：仅半伤。失败或成功：至高天直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "圣裁",
        "en_name": "Smite",
        "description": "至高天发动一次神力射线攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "多类型\\泰坦\\至高天.htm"
  },
  {
    "name": "至高天微尘",
    "en_name": "Empyrean Iota",
    "type_line": "中型天族或邪魔（泰坦），中立",
    "size": "Medium",
    "creature_type": "天族或邪魔（泰坦）",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 22,
    "hp_formula": "5d8",
    "speed": {
      "walk": "5尺，飞行30尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 1,
        "mod": -5,
        "save": -5
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "历史": 4,
      "洞悉": 5,
      "察觉": 5
    },
    "damage_resistances": [
      "钝击",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "倒地"
    ],
    "senses": {
      "真实视觉": 30,
      "被动察觉": 15
    },
    "languages": "全部",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "虚体移动",
        "en_name": "Incorporeal Movement",
        "description": "至高天微尘可以移动穿过其他生物或物件，如同穿过困难地形一般。在其回合结束时，若至高天微尘还处于物件内，其受到5（1d10）力场伤害。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "至高天微尘对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "异界打击",
        "en_name": "Otherworldly Strike",
        "description": "近战或远程攻击检定：+5，触及5尺或射程30尺。\n命中：7（1d8+3）暗蚀或光耀伤害（由至高天微尘选择）"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "至高天微尘施展以下一道法术，无需材料成分并使用感知作为施法属性："
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "祝福术Bless，次等复原术Lesser Restoration（以动作施展）"
      }
    ],
    "bonus_actions": [
      {
        "name": "治愈真言",
        "en_name": "Healing Word",
        "description": "至高天微尘施展治愈真言Healing \nWord，使用与施法动作相同的施法属性。",
        "params": "1/日"
      }
    ],
    "source_file": "多类型\\泰坦\\至高天微尘.htm"
  },
  {
    "name": "亡眼暴君",
    "en_name": "Death Tyrant",
    "type_line": "大型亡灵（眼魔），守序邪恶",
    "size": "Large",
    "creature_type": "亡灵（眼魔）",
    "alignment": "守序邪恶",
    "ac": 19,
    "initiative_bonus": 12,
    "initiative_total": 22,
    "hp": 195,
    "hp_formula": "26d10+52",
    "speed": {
      "walk": "5尺，飞行40尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 7
      },
      "智力": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 7
      },
      "魅力": {
        "score": 19,
        "mod": 4,
        "save": 4
      }
    },
    "skills": {
      "察觉": 12
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "麻痹",
      "石化",
      "中毒",
      "倒地"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 22
    },
    "languages": "深潜语，地底通用语",
    "cr": 14,
    "xp": 11500,
    "pb": 5,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "亡眼暴君豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "亡眼暴君使用三次眼波射线。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+9，触及5尺。命中：13（2d8+4）穿刺伤害。"
      },
      {
        "name": "眼波射线",
        "en_name": "Eye Rays",
        "description": "亡眼暴君向一名位于其120尺内的其可见的目标从下列魔法射线中随机射出一道（掷1d10，如果亡眼暴君在本回合已经使用过该射线则重新掷骰）："
      },
      {
        "name": "1. 魅惑射线",
        "en_name": "Charm Ray",
        "description": "感知豁免检定：DC17。失败：13（3d8）心灵伤害，目标陷入魅惑状态，持续1小时或在其受到伤害时提前结束。成功：仅半伤。"
      },
      {
        "name": "2",
        "en_name": "",
        "description": ". \n麻痹射线Paralyzing Ray。体质豁免检定：DC17。失败：目标陷入麻痹状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。"
      },
      {
        "name": "3. 恐惧射线",
        "en_name": "Fear Ray",
        "description": "感知豁免检定：DC17。失败：10（3d6）心灵伤害，目标陷入恐慌状态直至其下个回合结束。成功：仅半伤。"
      },
      {
        "name": "4. 缓慢射线",
        "en_name": "Slowing Ray",
        "description": "体质豁免检定：DC17。失败：18（4d8）暗蚀伤害。直至目标的下个回合结束，目标速度减半，无法执行反应，且目标在其回合中仅可以执行一个动作或一个附赠动作，但不能同时执行二者。成功：仅半伤。"
      },
      {
        "name": "5. 汲能射线",
        "en_name": "Enervation Ray",
        "description": "体质豁免检定：DC17。失败：16（3d10）毒素伤害，目标陷入中毒状态直至其下个回合结束。中毒期间，目标无法恢复生命值。成功：仅半伤。"
      },
      {
        "name": "6. 念力射线",
        "en_name": "Telekinetic Ray",
        "description": "力量豁免检定：DC17（此豁免超巨型自动成功） 。 失败：眼魔将目标向任意方向移动至多30尺。目标陷入束缚状态直至眼魔的下个回合开始，或在眼魔陷入失能状态时提前结束。眼魔还可以利用此射线对物件进行精细控制，例如操作工具、打开一扇门或打开容器。"
      },
      {
        "name": "7. 睡眠射线",
        "en_name": "Sleep Ray",
        "description": "感知豁免检定：DC17（此豁免构装或亡灵自动成功）。 失败：目标陷入昏迷状态，持续1分钟。若目标受到伤害或一名目标5尺内的生物以一个动作唤醒其，则状态结束。"
      },
      {
        "name": "8. 石化射线",
        "en_name": "Petrication \n  Ray",
        "description": "体质豁免检定：DC17。"
      },
      {
        "name": "9. 解离射线",
        "en_name": "Disintegration Ray",
        "description": "敏捷豁免检定：DC17。"
      },
      {
        "name": "10. 死亡射线",
        "en_name": "Death Ray",
        "description": "敏捷豁免检定：DC17。失败：55（10d10）暗蚀伤害。成功：半伤。成功或失败：若射线将目标生命值降至0，则目标死亡。"
      }
    ],
    "bonus_actions": [
      {
        "name": "负能量锥域",
        "en_name": "Antimagic Cone",
        "description": "亡眼暴君的主眼向150尺的锥状区域内发出一道无法察觉的暗能量魔法波。直至亡眼暴君的下个回合开始，该区域内的生物无法恢复生命值。一具完整的类人生物尸体会立刻站起化为一具丧尸Zombie，该丧尸受亡眼暴君控制，使用与亡眼暴君一样的先攻并在其回合结束后立即执行回合。"
      }
    ],
    "legendary_actions": [
      {
        "name": "切齿",
        "en_name": "Chomp",
        "description": "亡眼暴君发动两次啃咬攻击。",
        "max_uses": 3
      },
      {
        "name": "怒视",
        "en_name": "Glare",
        "description": "亡眼暴君使用眼波射线。",
        "max_uses": 3
      }
    ],
    "source_file": "多类型\\眼魔\\亡眼暴君.htm"
  },
  {
    "name": "眼魔",
    "en_name": "Beholder",
    "type_line": "大型异怪，守序邪恶",
    "size": "Large",
    "creature_type": "异怪",
    "alignment": "守序邪恶",
    "ac": 18,
    "initiative_bonus": 12,
    "initiative_total": 22,
    "hp": 190,
    "hp_formula": "20d10+80",
    "speed": {
      "walk": "5尺，飞行40尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 9
      },
      "智力": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 7
      },
      "魅力": {
        "score": 17,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "察觉": 12
    },
    "damage_immunities": [
      "倒地"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 22
    },
    "languages": "深潜语，地底通用语",
    "cr": 13,
    "xp": 10000,
    "pb": 5,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "眼魔豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "眼魔使用三次眼波射线。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+8，触及5尺。\n命中：13（3d6+3）穿刺伤害。"
      },
      {
        "name": "眼波射线",
        "en_name": "Eye Rays",
        "description": "眼魔向一名位于其120尺内的其可见的目标从下列魔法射线中随机射出一道（掷1d10，如果眼魔在本回合已经使用过该射线则重新掷骰）："
      },
      {
        "name": "1. 魅惑射线",
        "en_name": "Charm Ray",
        "description": "感知豁免检定：DC16。\n失败：13（3d8）心灵伤害，目标陷入魅惑状态，持续1小时或在其受到伤害时提前结束。\n成功：仅半伤。"
      },
      {
        "name": "2. 麻痹射线",
        "en_name": "Paralyzing Ray",
        "description": "体质豁免检定：DC16。\n失败：目标陷入麻痹状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。"
      },
      {
        "name": "3. 恐惧射线",
        "en_name": "Fear Ray",
        "description": "感知豁免检定：\n  DC16。\n失败：14（4d6）心灵伤害，目标陷入恐慌状态直至其下个回合结束。\n成功：仅半伤。"
      },
      {
        "name": "4. 缓慢射线",
        "en_name": "Slowing \n  Ray",
        "description": "体质豁免检定：\n  DC16。\n失败：18（4d8）暗蚀伤害。直至目标的下个回合结束，目标速度减半，无法执行反应，且目标在其回合中仅可以执行一个动作或一个附赠动作，但不能同时执行二者。\n成功：仅半伤。"
      },
      {
        "name": "5. 汲能射线",
        "en_name": "Enervation \n  Ray",
        "description": "体质豁免检定：\n  DC16。\n失败：13（3d8）毒素伤害，目标陷入中毒状态直至其下个回合结束。中毒期间，目标无法恢复生命值。\n成功：仅半伤。"
      },
      {
        "name": "6. 念力射线",
        "en_name": "Telekinetic \n  Ray",
        "description": "力量豁免检定：\n  DC16（此豁免超巨型自动成功）\n。\n失败：眼魔将目标向任意方向移动至多30尺。目标陷入束缚状态直至眼魔的下个回合开始，或在眼魔陷入失能状态时提前结束。眼魔还可以利用此射线对物件进行精细控制，例如操作工具、打开一扇门或打开容器。"
      },
      {
        "name": "7. 睡眠射线",
        "en_name": "Sleep \n  Ray",
        "description": "感知豁免检定：\n  DC16（此豁免构装或亡灵自动成功）。\n失败：目标陷入昏迷状态，持续1分钟。若目标受到伤害或一名目标5尺内的生物以一个动作唤醒其，则状态结束。"
      },
      {
        "name": "8. 石化射线",
        "en_name": "Petrication \n  Ray",
        "description": "体质豁免检定：DC16。 \n首次失败：目标陷入束缚状态，在其下个回合结束时目标若仍处于束缚则重复豁免，成功则终止其身上的该效应。再次失败：目标陷入石化状态替代其束缚状态"
      },
      {
        "name": "9. 解离射线",
        "en_name": "Disintegration \n  Ray",
        "description": "敏捷豁免检定：DC16。 \n失败：36（8d8）力场伤害。若目标是一件非魔法物件或魔法力场造物，则其上一处10尺立方区域内的部分被解离为尘埃。\n成功：半伤。成功或失败：若目标为生物且因此伤害生命值降至0，则该生物被解离为尘埃。"
      },
      {
        "name": "10. 死亡射线",
        "en_name": "Death Ray",
        "description": "敏捷豁免检定：DC16。失败：55（10d10）暗蚀伤害。\n成功：半伤。\n成功或失败：若射线将目标生命值降至0，则目标死亡。"
      }
    ],
    "bonus_actions": [
      {
        "name": "反魔法锥域",
        "en_name": "Antimagic Cone",
        "description": "眼魔的主眼向150尺锥状区域内发出一道反魔法能量波。此区域内如同反魔法场Antimagic \nField\n ，且此区域同样反制眼魔自己的眼波射线，直至眼魔的下个回合开始。"
      }
    ],
    "legendary_actions": [
      {
        "name": "切齿",
        "en_name": "Chomp",
        "description": "眼魔发动两次啃咬攻击。",
        "max_uses": 3
      },
      {
        "name": "怒视",
        "en_name": "Glare",
        "description": "眼魔使用眼波射线。",
        "max_uses": 3
      }
    ],
    "source_file": "多类型\\眼魔\\眼魔.htm"
  },
  {
    "name": "观察者眼魔",
    "en_name": "Spectator",
    "type_line": "中型异怪（眼魔），守序中立",
    "size": "Medium",
    "creature_type": "异怪（眼魔）",
    "alignment": "守序中立",
    "ac": 14,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 45,
    "hp_formula": "7d8+14",
    "speed": {
      "walk": "5尺，飞行30尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 6
    },
    "damage_immunities": [
      "力竭",
      "倒地"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 16
    },
    "languages": "深潜语，地底通用语；心灵感应120尺",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "观察者眼魔发动两次眼波射线。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+4，触及5尺。\n命中：5（1d6+2）穿刺伤害。"
      },
      {
        "name": "眼波射线",
        "en_name": "Eye Rays",
        "description": "观察者眼魔向一名位于其90尺内的其可见的目标从下列魔法射线中随机射出一道（掷1d4，如果观察者眼魔在本回合已经使用过该射线则重新掷骰）："
      },
      {
        "name": "1. \n困惑射线Confusion Ray",
        "en_name": "",
        "description": "感知豁免检定：DC12。\n失败：5（2d4）心灵伤害，目标无法执行反应直至其下个回合结束。目标在其下个回合内无法移动，并使用动作对一名射程内的随机生物发动一次近战或远程攻击。若目标无法攻击，则其在该回合什么也不做。\n成功：仅半伤。"
      },
      {
        "name": "2. 麻痹射线",
        "en_name": "Paralyzing \n  Ray",
        "description": "体质豁免检定：DC12。\n失败：目标陷入麻痹状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，豁免自动成功。"
      },
      {
        "name": "3. \n恐惧射线Fear \n  Ray",
        "en_name": "",
        "description": "感知豁免检定：DC12。\n失败：5（2d4）心灵伤害，且目标陷入恐慌状态直至其下个回合结束。"
      },
      {
        "name": "4. 致伤射线",
        "en_name": "Wounding Ray",
        "description": "体质豁免检定：DC12。\n失败：16（3d10）暗蚀伤害。\n成功：\n半伤。"
      }
    ],
    "reactions": [
      {
        "name": "法术反射",
        "en_name": "Spell Reflection",
        "description": "触发：观察者眼魔对抗法术时进行的豁免检定成功或法术的攻击检定对观察者眼魔失手。 \n响应-敏捷豁免检定：DC12，单一120尺内观察者眼魔可见的生物。\n失败：10（3d6）力场伤害。"
      }
    ],
    "source_file": "多类型\\眼魔\\观察者眼魔.htm"
  },
  {
    "name": "守秘纳迦",
    "en_name": "Guardian Naga",
    "type_line": "大型天族，守序善良",
    "size": "Large",
    "creature_type": "天族",
    "alignment": "守序善良",
    "ac": 18,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 136,
    "hp_formula": "16d10+48",
    "speed": {
      "walk": "40尺，攀爬40尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 8
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "感知": {
        "score": 19,
        "mod": 4,
        "save": 8
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 8
      }
    },
    "skills": {
      "奥秘": 11,
      "历史": 11,
      "宗教": 11
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "麻痹",
      "中毒",
      "束缚"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 14
    },
    "languages": "天界语，通用语",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "traits": [
      {
        "name": "天界复苏",
        "en_name": "Celestial Restoration",
        "description": "若纳迦死亡，则除非其遗骸被施展驱逐善恶Dispel Evil and \nGood   ，其在1d6天后重获生命并恢复全部生命值。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "该纳迦发动两次啃咬攻击。其可以将其中一次攻击替换为使用剧毒蛇涎。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+8，触及10尺。命中：17（2d12+4）穿刺伤害加22（4d10）毒素伤害。"
      },
      {
        "name": "剧毒蛇涎",
        "en_name": "Poisonous Spittle",
        "description": "体质豁免检定：DC16，单一60尺内纳迦可见的生物。失败：31（7d8）毒素伤害，且目标陷入目盲状态直至纳迦的下个回合开始。成功：仅半伤。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "该纳迦施展以下一道法术，无需姿势或材料成分并使感知作为施法属性（法术豁免DC16）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "奇术Thaumaturgy"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "鹰眼术Clairvoyance，疗伤术Cure Wounds（六环版本），  焰击术Flame Strike（六环版本），  指使术Geas，真知术True Seeing"
      }
    ],
    "source_file": "多类型\\纳迦\\守秘纳迦.htm"
  },
  {
    "name": "阴魂纳迦",
    "en_name": "Spirit Naga",
    "type_line": "大型邪魔，混乱邪恶",
    "size": "Large",
    "creature_type": "邪魔",
    "alignment": "混乱邪恶",
    "ac": 17,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 135,
    "hp_formula": "18d10+36",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 6
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 5
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 6
      }
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 12
    },
    "languages": "深渊语，通用语",
    "cr": 8,
    "xp": 3900,
    "pb": 3,
    "traits": [
      {
        "name": "邪魔复苏",
        "en_name": "Fiendish Restoration",
        "description": "若纳迦死亡，则其在1d6天后重获生命并恢复全部生命值。只有法术祈愿术Wish能阻止该特质生效。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "纳迦使用啃咬或暗蚀射线发动共计三次攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+7，触及10尺。命中：7（1d6+4）穿刺伤害加14（4d6）毒素伤害。"
      },
      {
        "name": "暗蚀射线",
        "en_name": "Necrotic Ray",
        "description": "远程攻击检定：+6，射程60尺。命中：21（6d6）暗蚀伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "该纳迦施展以下一道法术，无需姿势和材料成分并使用智力作为施法属性（法术豁免DC14）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，法师之手Mage Hand，次级幻象Minor Illusion，水下呼吸Water Breathing"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "侦测思想Detect Thoughts，任意门Dimension Door，定身类人Hold Person（三环版本），   闪电束Lightning Bolt（四环版本）"
      }
    ],
    "source_file": "多类型\\纳迦\\阴魂纳迦.htm"
  },
  {
    "name": "骸骨纳迦",
    "en_name": "Bone Naga",
    "type_line": "大型亡灵，中立邪恶",
    "size": "Large",
    "creature_type": "亡灵",
    "alignment": "中立邪恶",
    "ac": 15,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 65,
    "hp_formula": "10d10+10",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "麻痹",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 12
    },
    "languages": "通用语以及一门其他语言",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "纳迦发动两次啃咬攻击。其可以将其中一次攻击替换为使用蛇灵凝视。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及10尺。命中：10（2d6+3）穿刺伤害外加7（2d6）暗蚀伤害。"
      },
      {
        "name": "蛇灵凝视",
        "en_name": "Serpentine Gaze",
        "description": "感知豁免检定：DC13，单一60尺内纳迦可见生物。失败：13（3d6+3）心灵伤害，且目标陷入魅惑状态直至纳迦的下个回合开始。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "该纳迦施展以下一道法术，无需材料成分并使用智力作为施法属性（法术豁免DC13）"
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "法师之手Mage Hand，奇术Thaumaturgy"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "命令术Command，侦测思想Detect Thoughts，闪电束Lightning Bolt"
      }
    ],
    "source_file": "多类型\\纳迦\\骸骨纳迦.htm"
  },
  {
    "name": "夜鬼婆",
    "en_name": "Night Hag",
    "type_line": "中型邪魔，中立邪恶",
    "size": "Medium",
    "creature_type": "邪魔",
    "alignment": "中立邪恶",
    "ac": 17,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 112,
    "hp_formula": "15d8+45",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "欺瞒": 6,
      "洞悉": 5,
      "察觉": 5,
      "隐匿": 5
    },
    "damage_resistances": [
      "寒冷",
      "火焰"
    ],
    "damage_immunities": [
      "魅惑"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 15
    },
    "languages": "深渊语，通用语，炼狱语，原初语",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "集会魔法",
        "en_name": "Coven Magic",
        "description": "在30尺内有至少两个鬼婆盟友的情况下，鬼婆可以施展以下一道法术，无需材料成分，使用法术的原本施法时间，并使用智力作为施法属性（法术豁免DC14）：卜筮术Augury，寻获魔宠Find \nFamiliar，鉴定术Identify，物件定位术Locate \nObject，探知术Scrying或隐形仆役Unseen \nServant 。鬼婆必须完成一次长休后才能再次用此特质施展其所选的法术。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "鬼婆对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "灵魂袋",
        "en_name": "Soul Bag",
        "description": "鬼婆有一只灵魂袋。只要持握或携带灵魂袋，鬼婆就能够使用其噩梦缠身动作。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鬼婆发动两次爪击攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+7，触及5尺。命中：13（2d8+4）挥砍伤害。"
      },
      {
        "name": "噩梦缠身",
        "en_name": "Nightmare Hautnting",
        "description": "若鬼婆身处以太位面，其施展托梦术Dream，使用与施法动作相同的施法属性。只有鬼婆能作为法术的信使，并且目标必须是一名鬼婆可见的身处物质位面的生物。若目标处于法术防护善恶Protection \nfrom Evil and Good效应下或身处法术防护法阵Magic Circle      中，法术失败并被浪费。",
        "params": "1/日；需灵魂袋"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "鬼婆施展以下一道法术，无需材料成分并使用智力作为施法属性（法术豁免DC14）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，以太化Etherealness，魔法飞弹Magic Missile（四环版本）"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "魅影杀手Phantasmal Killer，位面转移Plane Shift（仅自身）"
      }
    ],
    "bonus_actions": [
      {
        "name": "变形",
        "en_name": "Shape-Shift",
        "description": "鬼婆变形为小型或中型的类人生物，或变回其真实形态。除体型外，其各形态下游戏数据均相同。鬼婆着装或携带的任何装备都不会随之变化。"
      }
    ],
    "source_file": "多类型\\鬼婆\\夜鬼婆.htm"
  },
  {
    "name": "大鬼婆",
    "en_name": "Arch-hag",
    "type_line": "大型妖精，中立邪恶",
    "size": "Large",
    "creature_type": "妖精",
    "alignment": "中立邪恶",
    "ac": 20,
    "initiative_bonus": 16,
    "initiative_total": 26,
    "hp": 333,
    "hp_formula": "29d10+174",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 24,
        "mod": 7,
        "save": 7
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 9
      },
      "体质": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "智力": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 19,
        "mod": 4,
        "save": 11
      },
      "魅力": {
        "score": 25,
        "mod": 7,
        "save": 7
      }
    },
    "skills": {
      "欺瞒": 14,
      "察觉": 11,
      "游说": 21
    },
    "damage_resistances": [
      "寒冷",
      "火焰",
      "心灵"
    ],
    "damage_immunities": [
      "魅惑",
      "力竭",
      "恐慌"
    ],
    "senses": {
      "真实视觉": 60,
      "被动察觉": 21
    },
    "languages": "所有",
    "cr": 21,
    "xp": 33000,
    "pb": 7,
    "traits": [
      {
        "name": "集会魔法",
        "en_name": "Coven Magic",
        "description": "在30尺内有至少两个鬼婆盟友的情况下，鬼婆可以施展以下一道法术，无需材料成分，使用法术的原本施法时间，并使用智力作为施法属性（法术豁免DC19）：卜筮术Augury，寻获魔宠Find \nFamiliar，鉴定术Identify，物件定位术Locate \nObject，探知术Scrying或隐形仆役Unseen \nServant。 鬼婆必须完成一次长休后才能再次用此特质施展其所选的法术。"
      },
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "鬼婆豁免失败时，可以将其改为豁免成功。",
        "params": "4/日，或巢穴内5/日"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "鬼婆对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "改日算账",
        "en_name": "Spiteful Escape",
        "description": "当鬼婆的生命值降至0时，只有在其位于自己的克星（一件鬼婆最厌恶的事物，由DM选择）30尺内时才会死亡。否则，鬼婆的生命值会改为降至1并传送到一个无害的半位面，并且在2d6日内无法回到自己离开的位面。当鬼婆传送离开时，位于它离开空间60尺内的每名生物都会被诅咒。被诅咒的生物进行的属性检定和豁免检定具有劣势，并且鬼婆总会知晓其在多元宇宙中的位置，直至此诅咒结束。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鬼婆发动两次幽魂利爪攻击并使用巫咒霹雳。"
      },
      {
        "name": "幽魂利爪",
        "en_name": "Spectral Claw",
        "description": "近战或远程攻击检定：+14，触及10尺或射程60尺。命中：17（3d6+7）力场伤害。如果目标生物体型不超过大型，则其陷入倒地状态。"
      },
      {
        "name": "巫咒霹雳",
        "en_name": "Crackling Wave",
        "description": "敏捷豁免检定：DC22， 60尺锥状区域内的每名生物。失败：32（5d12）闪电伤害。成功：半伤。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "鬼婆施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC22）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测思想Detect Thoughts，任意门Dimension Door，解除魔法Dispel Magic，催眠图纹Hypnotic Pattern"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "群体暗示术Mass Suggestion，纂改记忆Modify Memory，位面转移Plane Shift"
      }
    ],
    "bonus_actions": [
      {
        "name": "巫术雷击",
        "en_name": "Witch Strike",
        "description": "位于鬼婆60尺内的被鬼婆诅咒的每名生物受到14（4d6）闪电伤害。"
      }
    ],
    "reactions": [
      {
        "name": "扭曲言语",
        "en_name": "Tongue Twister",
        "description": "鬼婆施展法术反制Counterspell（触发条件见该法术），使用与施法动作相同的施法属性。若目标豁免失败，直至其下个回合结束，其会被诅咒。目标无法施展具有言语成分的法术，并且当其说话时，会说出和想要表达的意思相反的话，直至此诅咒结束。"
      }
    ],
    "legendary_actions": [
      {
        "name": "鬼婆猛打",
        "en_name": "Hag",
        "description": "鬼婆发动一次幽魂利爪攻击。",
        "max_uses": 3
      },
      {
        "name": "恶毒魔法",
        "en_name": "Malicious Maigic",
        "description": "鬼婆使用施法动作来施展任意门Dimension Door或催眠图纹Hypnotic \nPattern。鬼婆直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      }
    ],
    "source_file": "多类型\\鬼婆\\大鬼婆.htm"
  },
  {
    "name": "海鬼婆",
    "en_name": "Sea Hag",
    "type_line": "中型妖精，混乱邪恶",
    "size": "Medium",
    "creature_type": "妖精",
    "alignment": "混乱邪恶",
    "ac": 14,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 52,
    "hp_formula": "7d8+21",
    "speed": {
      "walk": "30尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "通用语，巨人语，原初语（水族语）",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "鬼婆可以在空气和水中呼吸。"
      },
      {
        "name": "集会魔法",
        "en_name": "Coven Magic",
        "description": "若30尺内有至少两名鬼婆盟友，鬼婆可以施展以下法术之一，无需材料成分，使用法术的原本施法时间，并使用智力作为施法属性（法术豁免DC11）：卜筮术Augury，寻获魔宠Find \nFamiliar，鉴定术Identify，物件定位术Locate \nObject，探知术Scrying或隐形仆役Unseen \nServant。 鬼婆必须完成一次长休后才能再次用此特质施展其所选的法术。"
      },
      {
        "name": "丑恶容貌",
        "en_name": "Vile Appearance",
        "description": "感知豁免检定：DC11，任何在鬼婆30尺内开始其回合，并且能够看到海鬼婆的真实形态的野兽和类人生物。失败：目标陷入恐慌状态，直至其下个回合开始。成功：目标在24小时内免疫此鬼婆的丑恶容貌特质。"
      }
    ],
    "actions": [
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+5，触及5尺。命中：10（2d6+3）挥砍伤害。"
      },
      {
        "name": "死亡凝视",
        "en_name": "Death Glare",
        "description": "感知豁免检定：DC11，单一30尺内鬼婆可见的恐慌生物。失败：若目标的生命值为20及以下，其生命值降至0。否则，目标受到13（3d8）心灵伤害。",
        "params": "充能5~6"
      },
      {
        "name": "幻形",
        "en_name": "Illusion Appearance",
        "description": "鬼婆施展易容术Disguise \nSelf，并使用体质作为施法属性（法术豁免DC13）。该法术的持续时间为24小时。"
      }
    ],
    "source_file": "多类型\\鬼婆\\海鬼婆.htm"
  },
  {
    "name": "绿鬼婆",
    "en_name": "Green Hag",
    "type_line": "中型妖精，中立邪恶",
    "size": "Medium",
    "creature_type": "妖精",
    "alignment": "中立邪恶",
    "ac": 17,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 82,
    "hp_formula": "11d8+33",
    "speed": {
      "walk": "30尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 14,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "奥秘": 5,
      "欺瞒": 4,
      "察觉": 4,
      "隐匿": 3
    },
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 14
    },
    "languages": "通用语，精灵语，木族语",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "鬼婆可以在空气和水中呼吸。"
      },
      {
        "name": "集会魔法",
        "en_name": "Coven Magic",
        "description": "在30尺内有至少两个鬼婆盟友的情况下，鬼婆可以施展以下一道法术，无需材料成分，使用法术的原本施法时间，并使用智力作为施法属性（法术豁免DC11）：卜筮术Augury，寻获魔宠Find \nFamiliar，鉴定术Identify，物件定位术Locate \nObject，探知术Scrying或隐形仆役Unseen \nServant。 鬼婆必须完成一次长休后才能再次用此特质施展其所选的法术。"
      },
      {
        "name": "拟声",
        "en_name": "Mimicry",
        "description": "鬼婆可以模仿动物的声音和类人生物的语音。听到该声音的生物可以成功通过一次DC14的感知（洞悉 \n）检定来发现其是模仿。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鬼婆发动两次爪击攻击。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+6，触及5尺。命中：8（1d8+4）挥砍伤害外加3（1d6）毒素伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "鬼婆施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC12，法术攻击命中+4）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "舞光术Dancing Lights，易容术Disguise Seelf（持续24小时），     隐身术Invisiblity（仅自身，并且鬼婆在隐形期间不会留下任何踪迹），    次级幻象Minor Illusion，   致病射线Ray of Sickness（三环版本）"
      }
    ],
    "source_file": "多类型\\鬼婆\\绿鬼婆.htm"
  },
  {
    "name": "巡海人鱼",
    "en_name": "Merfolk Skirmisher",
    "type_line": "中型元素，中立",
    "size": "Medium",
    "creature_type": "元素",
    "alignment": "中立",
    "ac": 11,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 11,
    "hp_formula": "2d8+2",
    "speed": {
      "walk": "10尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "senses": {
      "被动察觉": 12
    },
    "languages": "通用语，原初语（水族语）",
    "cr": "1/8",
    "xp": 25,
    "pb": 2,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "人鱼可以在空气和水中呼吸。"
      }
    ],
    "actions": [
      {
        "name": "瀚海之矛",
        "en_name": "Ocean Spear",
        "description": "近战或远程攻击检定：+2，触及5尺或射程20/60尺。命中：3（1d6）穿刺伤害外加2（1d4）寒冷伤害。若目标为生物，则其速度降低10尺直至其下个回合结束。命中或失手：瀚海之矛会在被用于一次远程攻击后立即魔法性地回到人鱼手中。"
      }
    ],
    "source_file": "元素\\人鱼\\巡海人鱼.htm"
  },
  {
    "name": "御浪人鱼",
    "en_name": "Merfolk Wavebender",
    "type_line": "中型元素，中立",
    "size": "Medium",
    "creature_type": "元素",
    "alignment": "中立",
    "ac": 14,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 97,
    "hp_formula": "15d8+30",
    "speed": {
      "walk": "10尺，游泳40尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 19,
        "mod": 4,
        "save": 7
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 5
      }
    },
    "skills": {
      "察觉": 7
    },
    "damage_resistances": [
      "寒冷"
    ],
    "senses": {
      "被动察觉": 17
    },
    "languages": "通用语，原初语（水族语）",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "人鱼可以在空气和水中呼吸。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "人鱼发动两次洋流冲刷攻击。"
      },
      {
        "name": "洋流冲刷",
        "en_name": "Aquatic Burst",
        "description": "近战或远程攻击检定：+7，触及5尺或射程60尺。命中：20（3d10+4）寒冷伤害。若目标生物体型不超过大型，则其陷入倒地状态。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "人鱼施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "四象法门Elementalism，光亮术Light"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "操控水体Control Water，造水术/枯水术Create or Destroy Water"
      }
    ],
    "reactions": [
      {
        "name": "潮浪反斥",
        "en_name": "Watery Rebuke",
        "description": "触发：一名人鱼可见的敌人进入人鱼5尺内的空间。响应-力量豁免检定：DC15，触发敌人。失败：14（4d6）寒冷伤害。若目标体型不超过大型，则其被人鱼咒唤的水流直线推离至多30尺。"
      }
    ],
    "source_file": "元素\\人鱼\\御浪人鱼.htm"
  },
  {
    "name": "土元素",
    "en_name": "Earth Elemental",
    "type_line": "大型元素，中立",
    "size": "Large",
    "creature_type": "元素",
    "alignment": "中立",
    "ac": 17,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 147,
    "hp_formula": "14d10+70",
    "speed": {
      "walk": "30尺，掘穴30尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "damage_vulnerabilities": [
      "雷鸣。"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "麻痹",
      "石化",
      "中毒",
      "昏迷。"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "原初语（土族语）",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "遁地",
        "en_name": "Earth Glide",
        "description": "土元素可以掘穴穿过非魔法且未经加工的泥土及岩石。遁地期间，土元素不会破坏其穿过的任何材质。"
      },
      {
        "name": "攻城怪物",
        "en_name": "Siege Monster",
        "description": "土元素对物件和建筑造成双倍伤害。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "土元素使用猛击或岩石射击发动共计两次攻击。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+8，触及10尺。命中：14（2d8+5）钝击伤害。"
      },
      {
        "name": "岩石射击",
        "en_name": "Rock Launch",
        "description": "远程攻击检定：+8，射程60尺。命中：8（1d6+5）钝击伤害。若目标生物体型不超过大型，则其陷入倒地状态。"
      }
    ],
    "source_file": "元素\\四元素\\土元素.htm"
  },
  {
    "name": "气元素",
    "en_name": "Air Elemental",
    "type_line": "大型元素，中立",
    "size": "Large",
    "creature_type": "元素",
    "alignment": "中立",
    "ac": 15,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 90,
    "hp_formula": "12d10+24",
    "speed": {
      "walk": "10尺，飞行90尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "damage_resistances": [
      "钝击",
      "闪电",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "毒素",
      "雷鸣"
    ],
    "condition_immunities": [
      "力竭",
      "受擒",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚",
      "昏迷。"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "原初语（气族语）",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "空气形态",
        "en_name": "Air Form",
        "description": "气元素可以进入并停留在一名生物所处的空间。其可以移动穿过最窄1寸宽的空间而无需消耗额外的移动力。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "气元素发动两次雷鸣猛击攻击。"
      },
      {
        "name": "雷鸣猛击",
        "en_name": "Thunderous Slam",
        "description": "近战攻击检定：+8，触及10尺。命中：14（2d8+5）雷鸣伤害。"
      },
      {
        "name": "旋风",
        "en_name": "Whirlwind",
        "description": "力量豁免检定：DC13，单一位于气元素空间的不超过中型的生物。失败：24（4d10+2）雷鸣伤害，且目标被气元素直线推离至多20尺，并陷入倒地状态。成功：仅半伤。",
        "params": "充能4~6"
      }
    ],
    "source_file": "元素\\四元素\\气元素.htm"
  },
  {
    "name": "水元素",
    "en_name": "Water Elemental",
    "type_line": "大型元素，中立",
    "size": "Large",
    "creature_type": "元素",
    "alignment": "中立",
    "ac": 14,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 114,
    "hp_formula": "12d10+48",
    "speed": {
      "walk": "30尺，游泳90尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "damage_resistances": [
      "强酸",
      "火焰"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "受擒",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚",
      "昏迷。"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "原初语（水族语）",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "冻结",
        "en_name": "Freeze",
        "description": "若水元素受到寒冷伤害，其速度降低20尺，直至其下个回合结束。"
      },
      {
        "name": "流水形态",
        "en_name": "Water Form",
        "description": "水元素可以进入并停留在一名生物所处的空间。其可以移动穿过最窄1寸宽的空间而无需消耗额外的移动力。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "水元素发动两次猛击攻击。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+7，触及5尺。命中：13（2d8+4）钝击伤害。若目标生物体型不超过大型，则其陷入倒地状态"
      },
      {
        "name": "淹没",
        "en_name": "Whelm",
        "description": "力量豁免检定：DC15，位于水元素空间内的每名生物。失败：22（4d8+4）钝击伤害，若目标生物体型不超过大型，则其陷入受擒状态（逃脱DC14）。直至擒抱结束，目标陷入束缚状态，目标窒息除非其能在水中呼吸，且目标在水元素的回合开始时受到9（2d8）点钝击伤害。水元素同时能通过淹没擒抱的大型生物数上限为一，若生物不超过中型则上限为二。以一个动作，水元素5尺内的生物可以通过一次成功的DC14的力量（运动）检定将一名生物拉出来。成功：仅半伤。",
        "params": "充能4~6"
      }
    ],
    "source_file": "元素\\四元素\\水元素.htm"
  },
  {
    "name": "火元素",
    "en_name": "Fire Elemental",
    "type_line": "大型元素，中立",
    "size": "Large",
    "creature_type": "元素",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 93,
    "hp_formula": "11d10 + 33",
    "speed": {
      "walk": "50尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "damage_resistances": [
      "钝击",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "受擒",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚",
      "昏迷"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "原初语（火族语）",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "火焰灵光",
        "en_name": "Fire Aura",
        "description": "火元素回合结束时位于源自火元素的10尺光环区域内的每名生物受到5（1d10）点火焰伤害。光环内的生物和易燃物件开始燃烧。"
      },
      {
        "name": "火焰形态",
        "en_name": "Fire Form",
        "description": "火元素可以移动穿过最窄1寸宽的空间而无需消耗额外的移动力，且其可以进入并停留在一名生物所处的空间。当火元素在某个回合中首次进入某生物所处的空间时，该生物受到5（1d10）火焰伤害。"
      },
      {
        "name": "照明",
        "en_name": "Illumination",
        "description": "火元素散发出半径30尺的明亮光照以及额外30尺的微光光照。"
      },
      {
        "name": "水体易感",
        "en_name": "Water \nSusceptibility",
        "description": "每在水中移动5尺或每被泼一加仑水，火元素受到3（1d6）寒冷伤害。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "火元素发动两次燃烧攻击。"
      },
      {
        "name": "燃烧",
        "en_name": "Burn",
        "description": "近战攻击检定：+6，触及5尺。命中：10（2d6+3）火焰伤害。若目标为生物或易燃物件，则其开始燃烧。"
      }
    ],
    "source_file": "元素\\四元素\\火元素.htm"
  },
  {
    "name": "土巨灵",
    "en_name": "Dao",
    "type_line": "大型元素（巨灵），中立",
    "size": "Large",
    "creature_type": "元素（巨灵）",
    "alignment": "中立",
    "ac": 18,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 200,
    "speed": {
      "walk": "30尺，掘穴30尺，飞行30尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 23,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 5
      },
      "体质": {
        "score": 24,
        "mod": 7,
        "save": 7
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 5
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "damage_immunities": [
      "石化"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 11
    },
    "languages": "原初语（土族语）",
    "cr": 11,
    "xp": 7200,
    "pb": 4,
    "traits": [
      {
        "name": "遁地",
        "en_name": "Earth Glide",
        "description": "土巨灵可以掘穴穿过非魔法且未经加工的泥土及岩石。遁地期间，土巨灵不会破坏其穿过的任何材质。"
      },
      {
        "name": "元素重生",
        "en_name": "Elemental Restoration",
        "description": "若土巨灵于土元素位面之外死去，其身躯会化为尘土，并在1d4天后于土元素位面某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "祈愿",
        "en_name": "Wishes",
        "description": "每个土巨灵都有30%概率知晓法术祈愿术Wish。若知晓，则土巨灵可以但仅能在有非巨灵生物向其许愿（以土巨灵能理解的方式）时为那名生物施展此法术。土巨灵为该生物施展祈愿术将不会承受祈愿术的负担。一旦此土巨灵施展过三次祈愿术，其在365天内无法再次施展此法术。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "土巨灵发动三次大地重锤或两次地能爆发攻击。"
      },
      {
        "name": "大地重锤",
        "en_name": "Earthen Maul",
        "description": "近战攻击检定：+10，触及5尺。命中：20（4d6+6）钝击伤害，若目标生物体型不超过大型，则其陷入倒地状态。"
      },
      {
        "name": "地能爆发",
        "en_name": "Earth Burst",
        "description": "远程攻击检定：+10，射程120尺。命中：15（2d8+6）钝击伤害。命中或失手：目标所处空间处将爆发岩爆，产生以下效应。敏捷豁免检定：DC16，源自目标且包括目标自身的10尺光环区域内的每名生物。失败：10（3d6）雷鸣伤害"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "土巨灵施展以下一道法术，无需任何材料成分并使用魅力作为施法属性（法术豁免DC16）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测善恶Detect Evil and Good,侦测魔法 Detect Magic, 塑石术Stone Shape"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "气化形体Gaseous Form,  隐形术Invisibility, 地动术Move Earth，穿墙术 Passwall，位面转移Plane Shift,，巧言术Tongues, 石墙术Wall of Stone"
      }
    ],
    "source_file": "元素\\巨灵\\土巨灵.htm"
  },
  {
    "name": "气巨灵",
    "en_name": "Djinni",
    "type_line": "大型元素（巨灵），混乱中立",
    "size": "Large",
    "creature_type": "元素（巨灵）",
    "alignment": "混乱中立",
    "ac": 17,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 218,
    "speed": {
      "walk": "30尺,飞行90尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 21,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 6
      },
      "体质": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "智力": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 7
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 5
      }
    },
    "damage_immunities": [
      "闪电",
      "雷鸣"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 13
    },
    "languages": "原初语（气族语）",
    "cr": 11,
    "xp": 7200,
    "pb": 4,
    "traits": [
      {
        "name": "元素重生",
        "en_name": "Elemental Restoration",
        "description": "若气巨灵于气元素位面之外死去，其身躯会化为薄雾，并在1d4天后于气元素位面某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "气巨灵对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "祈愿",
        "en_name": "Wishes",
        "description": "每个气巨灵都有30%概率知晓法术祈愿术Wish。若知晓，则气巨灵可以但仅能在有非巨灵生物向其许愿（以气巨灵能理解的方式）时为那个生物施展此法术。气巨灵为该生物施展祈愿术将不会承受祈愿术的负担。一旦此气巨灵施展过三次祈愿术，其在365天内无法再次施展此法术。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "气巨灵使用风暴之刃或风暴轰击发动共计三次攻击。"
      },
      {
        "name": "风暴之刃",
        "en_name": "Storm Blade",
        "description": "近战攻击检定：+9，触及5尺。命中：12（2d6+5）挥砍伤害外加7（2d6）闪电伤害。"
      },
      {
        "name": "风暴轰击",
        "en_name": "Storm Bolt",
        "description": "远程攻击检定：+9，射程120尺。命中：13（3d8）雷鸣伤害。若目标生物体型不超过大型，则其陷入倒地状态。"
      },
      {
        "name": "引动龙卷旋风",
        "en_name": "Create Whirlwind",
        "description": "气巨灵在120尺内其可见的一点，咒唤出一道龙卷风。龙卷风会覆盖半径20尺、高60尺的柱状区域，并持续至气巨灵专注终止。气巨灵在其回合开始时可以将龙卷风向任意方向移动至多20尺。每当龙卷风进入生物所处空间或生物进入龙卷风时，该生物承受以下效应。力量豁免检定：DC 17（每名生物每回合仅需进行一次此豁免，气巨灵不受影响）失败：\n目标在身处龙卷风内期间陷入束缚状态，并随龙卷风一并移动。束缚目标在其回合开始时受到21（6d6）雷鸣伤害。目标在其回合结束时重复豁免，成功则终止其身上的该效应。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "气巨灵施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC17）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测善恶Detect Evil and Good，侦测魔法Detect Magic"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "造粮术Create Food and Water（可以将水替换为创造美酒），巧言术Tongues，御风而行Wind Walk"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "造物术Creation，气化形体Gaseous Form，隐形术Invisibility，高等幻影Major Image，位面转移Plane Shift"
      }
    ],
    "source_file": "元素\\巨灵\\气巨灵.htm"
  },
  {
    "name": "水巨灵",
    "en_name": "Marid",
    "type_line": "大型元素（巨灵），混乱中立",
    "size": "Large",
    "creature_type": "元素（巨灵）",
    "alignment": "混乱中立",
    "ac": 17,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 229,
    "speed": {
      "walk": "30尺，飞行60尺，游泳90尺"
    },
    "abilities": {
      "力量": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 5
      },
      "体质": {
        "score": 26,
        "mod": 8,
        "save": 8
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 8
      }
    },
    "damage_resistances": [
      "强酸",
      "寒冷",
      "闪电"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 13
    },
    "languages": "原初语（水族语）",
    "cr": 11,
    "xp": 7200,
    "pb": 4,
    "traits": [
      {
        "name": "水陆两栖",
        "en_name": "Amphibious",
        "description": "水巨灵可以在空气和水中呼吸。"
      },
      {
        "name": "元素重生",
        "en_name": "Elemental Restoration",
        "description": "若水巨灵于水元素位面之外死去，其身躯会化为海水，并在1d4天后于水元素位面某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "祈愿",
        "en_name": "Wishes",
        "description": "每个水巨灵都有30%概率知晓法术祈愿术Wish。若知晓，则水巨灵可以但仅能在有非巨灵生物向其许愿（以水巨灵能理解的方式）时为那名生物施展此法术。水巨灵为该生物施展祈愿术将不会承受祈愿术的负担。一旦此水巨灵施展过三次祈愿术，其在365天内无法再次施展此法术。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "水巨灵发动三次水鞭攻击。"
      },
      {
        "name": "水鞭之击",
        "en_name": "Aquatic Lash",
        "description": "近战攻击检定：+10，触及15尺。命中：15（2d8 + 6）挥砍伤害外加9（2d8）寒冷伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "水巨灵施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC16）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "造水术/枯水术Create or Destroy Water，侦测善恶Detect Evil and Good，侦测魔法Detect Magic，净化饮食Purify Food and Drink"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "操控水体Control Water，气化形体Gaseous Form，隐形术Invisibility，位面转移Plane Shift，巧言术Tongues"
      },
      {
        "name": "水柱喷射",
        "en_name": "Water Jet",
        "description": "敏捷豁免检定：DC 18，60尺长、10尺宽的线状区域内的每名生物。失败：31（9d6）寒冷伤害。若目标生物体型不超过巨型，则其被水巨灵直线推离至多20尺并陷入倒地状态。成功：仅半伤。"
      }
    ],
    "bonus_actions": [
      {
        "name": "迷雾之幕",
        "en_name": "Misty Veil",
        "description": "水巨灵施放云雾术Fog \nCloud，使用与施法动作相同的施法属性。",
        "params": "充能5~6"
      }
    ],
    "source_file": "元素\\巨灵\\水巨灵.htm"
  },
  {
    "name": "火巨灵",
    "en_name": "Efreeti",
    "type_line": "大型元素（巨灵），中立",
    "size": "Large",
    "creature_type": "元素（巨灵）",
    "alignment": "中立",
    "ac": 17,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 212,
    "speed": {
      "walk": "40尺,飞行60尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 22,
        "mod": 6,
        "save": 6
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 24,
        "mod": 7,
        "save": 7
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 6
      },
      "魅力": {
        "score": 19,
        "mod": 4,
        "save": 8
      }
    },
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 12
    },
    "languages": "原初语（火族语）",
    "cr": 11,
    "xp": 7200,
    "pb": 4,
    "traits": [
      {
        "name": "元素重生",
        "en_name": "Elemental Restoration",
        "description": "若火巨灵于火元素位面之外死去，其身躯会化为燃尘，并在1d4天后于火元素位面某处获得一具新的身体，以满生命值复活。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "火巨灵对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "祈愿",
        "en_name": "Wishes",
        "description": "每个火巨灵都有30%概率知晓法术祈愿术Wish。若知晓，则火巨灵可以但仅能在有非巨灵生物向其许愿（以火巨灵能理解的方式）时为那名生物施展此法术。火巨灵为该生物施展祈愿术将不会承受祈愿术的负担。一旦此火巨灵施展过三次祈愿术，其在365天内无法再次施展此法术。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "火巨灵使用炽热之刃或投掷烈焰发动共计三次攻击。"
      },
      {
        "name": "炽热之刃",
        "en_name": "Heated Blade",
        "description": "近战攻击检定：+10，触及5尺。命中：13（2d6 + 6）挥砍伤害外加13（2d12）火焰伤害。"
      },
      {
        "name": "投掷烈焰",
        "en_name": "Hurl Flame",
        "description": "远程攻击检定：+8，射程120尺。命中：24（7d6）火焰伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": ""
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "侦测魔法Detect Magic，四象法门Elementalism"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "气化形体Gaseous Form, 隐形术Invisibility, 高等幻影Major Image, 位面转移Plane Shift, 巧言术Tongues, 火墙术Wall of Fire（七环版本）"
      }
    ],
    "source_file": "元素\\巨灵\\火巨灵.htm"
  },
  {
    "name": "火矮人哨兵",
    "en_name": "Azer Sentinel",
    "type_line": "中型元素，守序中立",
    "size": "Medium",
    "creature_type": "元素",
    "alignment": "守序中立",
    "ac": 17,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 39,
    "hp_formula": "6d8+12",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 4
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "被动察觉": 11
    },
    "languages": "原初语（火族语）",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "炽焰灵光",
        "en_name": "Fire Aura",
        "description": "火矮人回合结束时，除非其陷入失能状态，否则位于源自火矮人的5尺光环区域内的每名生物受到5（1d10）火焰伤害。"
      },
      {
        "name": "照明",
        "en_name": "Illumination",
        "description": "火矮人散发出半径10尺的明亮光照以及额外10尺的微光光照。"
      }
    ],
    "actions": [
      {
        "name": "燃烧之锤",
        "en_name": "Burning Hammer",
        "description": "近战攻击检定：+5，触及5尺。命中：8（1d10+3）钝击伤害外加3（1d6）火焰伤害。"
      }
    ],
    "source_file": "元素\\火矮人\\火矮人哨兵.htm"
  },
  {
    "name": "火矮人烈炎术师",
    "en_name": "Azer Pyromancer",
    "type_line": "中型元素，守序中立",
    "size": "Medium",
    "creature_type": "元素",
    "alignment": "守序中立",
    "ac": 18,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 97,
    "hp_formula": "13d8+39",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "魅力": {
        "score": 13,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "奥秘": 4,
      "察觉": 7
    },
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "中毒"
    ],
    "senses": {
      "被动察觉": 17
    },
    "languages": "原初语（火族语）",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "traits": [
      {
        "name": "炽焰灵光",
        "en_name": "Fire Aura",
        "description": "火矮人回合结束时，除非其陷入失能状态，否则位于源自火矮人的5尺光环区域内的每名生物受到11（2d10）火焰伤害。"
      },
      {
        "name": "照明",
        "en_name": "Illumination",
        "description": "火矮人散发出半径10尺的明亮光照以及额外10尺的微光光照。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "火矮人发动两次炎爆攻击。"
      },
      {
        "name": "炎爆",
        "en_name": "Flame Burst",
        "description": "近战或远程攻击检定：+7，触及5尺或射程120尺。命中：15（2d10+4）火焰伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "火矮人施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "四象法门Elementalism，法师之手Mage Hand"
      },
      {
        "name": "1/日：",
        "en_name": "",
        "description": "火球术Fireball"
      }
    ],
    "reactions": [
      {
        "name": "炼狱叱喝",
        "en_name": "Hellish Rebuke",
        "description": "火矮人施展炼狱叱喝Hellish \nRebuke （触发条件见该法术），使用与施法动作相同的施法属性。",
        "params": "2/日"
      }
    ],
    "source_file": "元素\\火矮人\\火矮人烈炎术士.htm"
  },
  {
    "name": "火蜥蜴",
    "en_name": "Salamander",
    "type_line": "大型元素，中立邪恶",
    "size": "Large",
    "creature_type": "元素",
    "alignment": "中立邪恶",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 90,
    "hp_formula": "12d10+24",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "damage_vulnerabilities": [
      "寒冷"
    ],
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "原初语（火族语）",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "火焰灵光",
        "en_name": "Fire Aura",
        "description": "火蜥蜴回合结束时位于源自火蜥蜴的5尺光环区域内的由其选择的每名生物受到7（2d6）火焰伤害。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "火蜥蜴发动两次烈焰长矛攻击。其可以将其中一次攻击替换为使用绞缠。"
      },
      {
        "name": "烈焰长矛",
        "en_name": "Flame Spear",
        "description": "近战或远程攻击检定：+7，触及5尺或射程20/60尺。命中：13（2d8+4）穿刺伤害，外加7（2d6）火焰伤害。\n命中或失手：长矛会在被用于一次远程攻击后立即魔法性地回到火蜥蜴手中。"
      },
      {
        "name": "绞缠",
        "en_name": "Constrict",
        "description": "力量豁免检定：DC15，单一10尺内火蜥蜴可见的不超过大型的生物。失败：11（2d6+4）钝击伤害外加7（2d6）火焰伤害。目标陷入受擒状态（逃脱DC14），且目标陷入束缚状态直至擒抱结束。"
      }
    ],
    "source_file": "元素\\火蜥蜴\\火蜥蜴.htm"
  },
  {
    "name": "火蜥蜴火蛇",
    "en_name": "Salamander Fire Snake",
    "type_line": "中型元素，中立邪恶",
    "size": "Medium",
    "creature_type": "元素",
    "alignment": "中立邪恶",
    "ac": 14,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 27,
    "hp_formula": "6d8",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "damage_vulnerabilities": [
      "寒冷"
    ],
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "理解原初语，但不会说",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "traits": [
      {
        "name": "火焰灵光",
        "en_name": "Fire Aura",
        "description": "火蜥蜴回合结束时位于源自火蜥蜴的5尺光环区域内的由其选择的每名生物受到3（1d6）火焰伤害。"
      }
    ],
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+4，触及5尺。命中：6（1d8+2）穿刺伤害，外加3（1d6）火焰伤害。"
      }
    ],
    "source_file": "元素\\火蜥蜴\\火蜥蜴火蛇.htm"
  },
  {
    "name": "火蜥蜴炎狱之主",
    "en_name": "Salamander Inferno Master",
    "type_line": "大型元素，中立邪恶",
    "size": "Large",
    "creature_type": "元素",
    "alignment": "中立邪恶",
    "ac": 18,
    "initiative_bonus": 8,
    "initiative_total": 18,
    "hp": 256,
    "hp_formula": "27d10+108",
    "speed": {
      "walk": "40尺，攀爬40尺"
    },
    "abilities": {
      "力量": {
        "score": 24,
        "mod": 7,
        "save": 7
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 8
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 5
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 5
      }
    },
    "damage_vulnerabilities": [
      "寒冷"
    ],
    "damage_immunities": [
      "火焰"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 10
    },
    "languages": "原初语（火族语）",
    "cr": 15,
    "xp": 13000,
    "pb": 5,
    "traits": [
      {
        "name": "火焰灵光",
        "en_name": "Fire Aura",
        "description": "火蜥蜴回合结束时位于源自火蜥蜴的10尺光环区域内的由其选择的每名生物受到10（3d6）火焰伤害。"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "火蜥蜴对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "火蜥蜴发动两次烈焰三叉戟攻击。"
      },
      {
        "name": "烈焰三叉戟",
        "en_name": "Flame Trident",
        "description": "近战或远程攻击检定：+12，触及5尺或射程30/90尺。命中：16（2d8+7）穿刺伤害，外加14（4d6）火焰伤害。命中或失手：三叉戟会在被用于一次远程攻击后立即魔法性地回到火蜥蜴手中。"
      },
      {
        "name": "炎狱爆裂",
        "en_name": "Inferno Blast",
        "description": "敏捷豁免检定：DC18，以120尺内火蜥蜴可见的一点为中心，半径30尺球状区域内的每名生物。\n失败：35（10d6）火焰伤害，且目标开始燃烧，目标在其回合开始时受到5（1d10）火焰伤害，而非普通的燃烧伤害。每当目标承受此燃烧伤害，目标获得1级力竭。\n成功：仅半伤。",
        "params": "充能5~6"
      }
    ],
    "bonus_actions": [
      {
        "name": "炽烈移动",
        "en_name": "Blazing Movement",
        "description": "火蜥蜴移动至多等于其速度的距离且不会引发借机攻击。在火蜥蜴移动过程中，火焰会充斥于源自火蜥蜴的5尺光环区域内。当光环进入一个生物所处空间时，该生物受到7（2d6）火焰伤害。每名生物每回合仅受一次此伤害。"
      }
    ],
    "source_file": "元素\\火蜥蜴\\火蜥蜴炎狱之主.htm"
  },
  {
    "name": "蜥蜴人地脉术师",
    "en_name": "Lizardfolk Geomancer",
    "type_line": "中型元素，中立",
    "size": "Medium",
    "creature_type": "元素",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 33,
    "hp_formula": "6d8+6",
    "speed": {
      "walk": "30尺，掘穴20尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "skills": {
      "自然": 2,
      "察觉": 4,
      "隐匿": 4
    },
    "senses": {
      "被动察觉": 14
    },
    "languages": "龙语，原初语（土族语）",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蜥蜴人发动两次地脉迸发攻击。"
      },
      {
        "name": "地脉迸发",
        "en_name": "Earth Burst",
        "description": "近战或远程攻击检定：+4，触及5尺或射程60尺。命中：9（2d6+2）钝击伤害。"
      },
      {
        "name": "土石洪流",
        "en_name": "Hail of Stone",
        "description": "体质豁免检定：DC12，以60尺内蜥蜴人可见一点为中心，半径20尺、高40尺的柱状区域内的每名生物。失败：15（6d4）钝击伤害，且目标陷入倒地状态。成功：仅半伤。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "蜥蜴人施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC12）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "四象法门Elementalism"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "融身入石Meld into Stone，植物交谈Speak with Plants，荆棘丛生Spike Growth"
      }
    ],
    "source_file": "元素\\蜥蜴人\\蜥蜴人地脉术师.htm"
  },
  {
    "name": "蜥蜴人大王",
    "en_name": "Lizardfolk Sovereign",
    "type_line": "中型元素，中立",
    "size": "Medium",
    "creature_type": "元素",
    "alignment": "中立",
    "ac": 15,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 78,
    "hp_formula": "12d8+24",
    "speed": {
      "walk": "30尺，掘穴20尺，游泳30尺"
    },
    "abilities": {
      "力量": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 4
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 15,
        "mod": 2,
        "save": 2
      }
    },
    "skills": {
      "察觉": 4,
      "隐匿": 5
    },
    "damage_immunities": [
      "恐慌"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 14
    },
    "languages": "龙语，原初语（土族语）",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "蜥蜴人大王发动一次啃咬攻击和一次大地重锤攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：8（1d10+3）穿刺伤害。若目标生物非构装且非亡灵，则蜥蜴人获得等于以此造成的伤害的临时生命值。"
      },
      {
        "name": "大地重锤",
        "en_name": "Earthen Maul",
        "description": "近战攻击检定：+5，触及5尺。命中：10（2d6+3）钝击伤害。若目标生物体型不超过中型，则其陷入倒地状态。"
      }
    ],
    "bonus_actions": [
      {
        "name": "冲锋",
        "en_name": "Charge",
        "description": "蜥蜴人向一名其可见的敌人直线移动至多等于其速度或其游泳速度的距离。"
      }
    ],
    "source_file": "元素\\蜥蜴人\\蜥蜴人大王.htm"
  },
  {
    "name": "冰魔蝠",
    "en_name": "Ice Mephit",
    "type_line": "小型元素，中立邪恶",
    "size": "Small",
    "creature_type": "元素",
    "alignment": "中立邪恶",
    "ac": 11,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 21,
    "hp_formula": "6d6",
    "speed": {
      "walk": "30尺，飞行30尺"
    },
    "abilities": {
      "力量": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "察觉": 2,
      "隐匿": 3
    },
    "damage_vulnerabilities": [
      "火焰"
    ],
    "damage_immunities": [
      "寒冷",
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 12
    },
    "languages": "原初语（水族语，气族语）",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "自爆",
        "en_name": "Death Burst",
        "description": "魔蝠在死亡时爆炸。体质豁免检定：DC10，源自魔蝠的5尺光环区域内的每名生物。失败：5（2d4）寒冷伤害。成功：半伤。"
      }
    ],
    "actions": [
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+3，触及5尺。命中：3（1d4+1）挥砍伤害外加2（1d4）寒冷伤害。"
      },
      {
        "name": "云雾术",
        "en_name": "Fog Cloud",
        "description": "魔蝠施展法术云雾术Fog Cloud ，无需法术成分并使用魅力作为施法属性。",
        "params": "1/日"
      },
      {
        "name": "冷冻吐息",
        "en_name": "Frost Breath",
        "description": "体质豁免检定：DC10，15尺锥状区域内的每名生物。失败：7（3d4）寒冷伤害。成功：半伤",
        "params": "充能6"
      }
    ],
    "source_file": "元素\\魔蝠\\冰魔蝠.htm"
  },
  {
    "name": "尘魔蝠",
    "en_name": "Dust Mephit",
    "type_line": "小型元素，中立邪恶",
    "size": "Small",
    "creature_type": "元素",
    "alignment": "中立邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 17,
    "hp_formula": "5d6",
    "speed": {
      "walk": "30尺，飞行30尺"
    },
    "abilities": {
      "力量": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 2,
      "隐匿": 4
    },
    "damage_vulnerabilities": [
      "火焰"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 12
    },
    "languages": "原初语（气族语，土族语）",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "自爆",
        "en_name": "Death Burst",
        "description": "魔蝠在死亡时爆炸。敏捷豁免检定：DC10，源自魔蝠的5尺光环区域内的每名生物。\n失败：5（2d4）钝击伤害。\n成功：半伤。"
      }
    ],
    "actions": [
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+4，触及5尺。\n命中：4（1d4+2）挥砍伤害。"
      },
      {
        "name": "致盲吐息",
        "en_name": "Blinding Breath",
        "description": "敏捷豁免检定：DC10，15尺锥状区域内的每名生物。\n失败：目标陷入目盲状态，持续至魔蝠的下个回合结束。",
        "params": "充能6"
      },
      {
        "name": "睡眠术",
        "en_name": "Sleep",
        "description": "魔蝠施展法术睡眠术Sleep，无需法术成分并使用魅力作为施法属性（法术豁免DC10）。",
        "params": "1/日"
      }
    ],
    "source_file": "元素\\魔蝠\\尘魔蝠.htm"
  },
  {
    "name": "泥魔蝠",
    "en_name": "Mud Mephit",
    "type_line": "小型元素，中立邪恶",
    "size": "Small",
    "creature_type": "元素",
    "alignment": "中立邪恶",
    "ac": 11,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 13,
    "hp_formula": "3d6+3",
    "speed": {
      "walk": "20尺，飞行20尺，游泳20尺"
    },
    "abilities": {
      "力量": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 9,
        "mod": -1,
        "save": -1
      },
      "感知": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 7,
        "mod": -2,
        "save": -2
      }
    },
    "skills": {
      "隐匿": 3
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "原初语（水族语，土族语）",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "traits": [
      {
        "name": "自爆",
        "en_name": "Death Burst",
        "description": "魔蝠在死亡时爆炸。敏捷豁免检定：DC11，源自魔蝠的5尺光环区域内的每名生物。\n失败：目标陷入束缚状态，持续至魔蝠的下个回合结束。"
      }
    ],
    "actions": [
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+3，触及5尺。\n命中：4（1d6+1）钝击伤害。"
      },
      {
        "name": "泥泞吐息",
        "en_name": "Mud Breath",
        "description": "敏捷豁免检定：DC11，单一15尺内魔蝠可见的生物。\n失败：目标陷入束缚状态，持续至魔蝠的下个回合结束。",
        "params": "充能6"
      }
    ],
    "source_file": "元素\\魔蝠\\泥魔蝠.htm"
  },
  {
    "name": "烟魔蝠",
    "en_name": "Smoke Mephit",
    "type_line": "小型元素，中立邪恶",
    "size": "Small",
    "creature_type": "元素",
    "alignment": "中立邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 13,
    "hp_formula": "3d6+3",
    "speed": {
      "walk": "30尺，飞行30尺"
    },
    "abilities": {
      "力量": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 2,
      "隐匿": 4
    },
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 12
    },
    "languages": "原初语（气族语，火族语）",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "traits": [
      {
        "name": "自爆",
        "en_name": "Death Burst",
        "description": "魔蝠在死亡时爆炸。体质豁免检定：DC11，源自魔蝠的5尺光环区域内的每名生物。"
      }
    ],
    "actions": [
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+4，触及5尺。\n命中：4（1d4+2）挥砍伤害。"
      },
      {
        "name": "燃烬吐息",
        "en_name": "Cinder Breath",
        "description": "敏捷豁免检定：DC11，单一15尺内魔蝠可见的生物。\n失败：目标陷入目盲状态，持续至魔蝠的下个回合结束。",
        "params": "充能6"
      }
    ],
    "source_file": "元素\\魔蝠\\烟魔蝠.htm"
  },
  {
    "name": "熔岩魔蝠",
    "en_name": "Magma Mephit",
    "type_line": "小型元素，中立邪恶",
    "size": "Small",
    "creature_type": "元素",
    "alignment": "中立邪恶",
    "ac": 11,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 18,
    "hp_formula": "4d6+4",
    "speed": {
      "walk": "30尺，飞行30尺"
    },
    "abilities": {
      "力量": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 10,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "隐匿": 3
    },
    "damage_vulnerabilities": [
      "寒冷"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "原初语（火族语，土族语）",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "traits": [
      {
        "name": "自爆",
        "en_name": "Death Burst",
        "description": "魔蝠在死亡时爆炸。敏捷豁免检定：DC11，源自魔蝠的5尺光环区域内的每名生物。\n失败：7（2d6）火焰伤害。\n成功：半伤。"
      }
    ],
    "actions": [
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+3，触及5尺。\n命中：3（1d4+1）挥砍伤害外加3（1d6）火焰伤害。"
      },
      {
        "name": "火焰吐息",
        "en_name": "Fire Breath",
        "description": "敏捷豁免检定：DC11，15尺锥状区域内的每名生物。\n失败：7（2d6）火焰伤害。\n成功：半伤",
        "params": "充能6"
      }
    ],
    "source_file": "元素\\魔蝠\\熔岩魔蝠.htm"
  },
  {
    "name": "蒸汽魔蝠",
    "en_name": "Steam Mephit",
    "type_line": "小型元素，中立邪恶",
    "size": "Small",
    "creature_type": "元素",
    "alignment": "中立邪恶",
    "ac": 10,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 17,
    "hp_formula": "5d6",
    "speed": {
      "walk": "30尺，飞行30尺"
    },
    "abilities": {
      "力量": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "隐匿": 2
    },
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "原初语（水族语，火族语）",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "traits": [
      {
        "name": "朦胧形态",
        "en_name": "Blurred Form",
        "description": "除非魔蝠陷入失能状态，否则对其进行的攻击检定具有劣势。"
      },
      {
        "name": "自爆",
        "en_name": "Death Burst",
        "description": "魔蝠在死亡时爆炸。体质豁免检定：DC10，源自魔蝠的5尺光环区域内的每名生物。\n失败：5（2d4）火焰伤害。\n成功：半伤。"
      }
    ],
    "actions": [
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+2，触及5尺。\n命中：2（1d4）挥砍伤害外加2（1d4）火焰伤害。"
      },
      {
        "name": "蒸汽吐息",
        "en_name": "Steam Breath",
        "description": "体质豁免检定：DC10，15尺锥状区域内的每名生物。\n失败：5（2d4）火焰伤害，且目标的速度降低10尺，持续至魔蝠的下个回合结束。\n成功：仅半伤。 失败或成功：无法因身处水下获得对此火焰伤害的抗性。",
        "params": "充能6"
      }
    ],
    "source_file": "元素\\魔蝠\\蒸汽魔蝠.htm"
  },
  {
    "name": "鸟羽人翔空士",
    "en_name": "Aarakocra Skirmisher",
    "type_line": "中型元素，中立",
    "size": "Medium",
    "creature_type": "元素",
    "alignment": "中立",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 11,
    "hp_formula": "2d8+2",
    "speed": {
      "walk": "20尺，飞行50尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "魅力": {
        "score": 11,
        "mod": 0,
        "save": 0
      }
    },
    "skills": {
      "察觉": 5
    },
    "senses": {
      "被动察觉": 15
    },
    "languages": "鸟羽人语，原初语（气族语）",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "actions": [
      {
        "name": "禽爪",
        "en_name": "Talons",
        "description": "近战攻击检定：+4，触及5尺。命中：4（1d4+2）挥砍伤害，若鸟羽人在此次攻击前立即向着目标直线移动了30+尺，则改为9（3d4+2）挥砍伤害。"
      },
      {
        "name": "风之标枪",
        "en_name": "Wind Javalin",
        "description": "近战或远程攻击检定：+4，触及5尺或射程30/120尺。命中：5（1d6+2）挥砍伤害穿刺伤害外加2（1d4）雷鸣伤害。命中或失手：标枪会在被用于一次远程攻击后立即魔法性地回到鸟羽人手中。"
      }
    ],
    "source_file": "元素\\鸟羽人\\鸟羽人翔空士.htm"
  },
  {
    "name": "鸟羽人风舞术师",
    "en_name": "Aarakocra Aeromancer",
    "type_line": "中型元素，中立",
    "size": "Medium",
    "creature_type": "元素",
    "alignment": "中立",
    "ac": 16,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 66,
    "hp_formula": "12d8+12",
    "speed": {
      "walk": "20尺，飞行50尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 5
      },
      "体质": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 17,
        "mod": 5,
        "save": 5
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "skills": {
      "奥秘": 3,
      "自然": 5,
      "察觉": 7
    },
    "senses": {
      "被动察觉": 17
    },
    "languages": "鸟羽人语，原初语（气族语）",
    "cr": 4,
    "xp": 1100,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "鸟羽人发动两次风之法杖攻击，并使用施法施展造风术Gust \nof Wind  。"
      },
      {
        "name": "风之法杖",
        "en_name": "Wind Staff",
        "description": "近战或远程攻击：+5，触及5尺或射程120尺。命中：7（1d8+3）钝击伤害外加11（2d10）闪电伤害。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "鸟羽人施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC13）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "四象法门Elementalism，造风术Gust of Wind，法师之手Mage Hand，传讯术Message"
      },
      {
        "name": "1/日：",
        "en_name": "",
        "description": "闪电束Lightning Bolt"
      }
    ],
    "reactions": [
      {
        "name": "羽落术",
        "en_name": "Feather Fall",
        "description": "鸟羽人施展羽落术Feather \nFall（触发条件见该法术），使用与施法动作相同的施法属性。",
        "params": "1/日"
      }
    ],
    "source_file": "元素\\鸟羽人\\鸟羽人风舞术士.htm"
  },
  {
    "name": "丧尸",
    "en_name": "Zombie",
    "type_line": "中型亡灵，中立邪恶",
    "size": "Medium",
    "creature_type": "亡灵",
    "alignment": "中立邪恶",
    "ac": 8,
    "initiative_bonus": -2,
    "initiative_total": 8,
    "hp": 15,
    "hp_formula": "2d8+6",
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 8
    },
    "languages": "理解通用语以及一门其他语言，但不会说",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "traits": [
      {
        "name": "不死坚韧",
        "en_name": "Undead Fortitude",
        "description": "当丧尸因非光耀非重击伤害生命值降至0时，其进行一次体质豁免（DC为5+所受伤害）。豁免成功则改为将生命值降至1。"
      }
    ],
    "actions": [
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+3，触及5尺。命中：5（1d8+1）钝击伤害。"
      }
    ],
    "source_file": "亡灵\\丧尸\\丧尸.htm"
  },
  {
    "name": "眼魔丧尸",
    "en_name": "Beholder Zombie",
    "type_line": "大型亡灵，中立邪恶",
    "size": "Large",
    "creature_type": "亡灵",
    "alignment": "中立邪恶",
    "ac": 15,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 93,
    "hp_formula": "11d10+33",
    "speed": {
      "walk": "5尺，飞行20尺（悬浮）"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "理解深潜语和地底通用语，但不会说",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "不死坚韧",
        "en_name": "Undead Fortitude",
        "description": "当丧尸因非光耀非重击伤害生命值降至0时，其进行一次体质豁免（DC为5+所受伤害）。豁免成功则改为将生命值降至1。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "丧尸发动两次眼波射线攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：16（4d6+2）穿刺伤害。"
      },
      {
        "name": "眼波射线",
        "en_name": "Eye \nRays",
        "description": "丧尸向一名位于其120尺内其可见的目标从下列魔法射线中随机射出一道（掷1d4，如果丧尸在本回合已经使用过该射线则重新掷骰）："
      },
      {
        "name": "1. 麻痹射线",
        "en_name": "Paralyzing \nRay",
        "description": "体质豁免检定：DC14。失败：目标陷入麻痹状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。"
      },
      {
        "name": "2. 恐惧射线",
        "en_name": "Fear Ray",
        "description": "感知豁免检定：DC14。失败：13（3d8）心灵伤害，目标陷入恐慌状态，直至其下个回合结束。"
      },
      {
        "name": "3. 汲能射线",
        "en_name": "Enervation \nRay",
        "description": "体质豁免检定：DC14。失败：10（3d6）暗蚀伤害，目标陷入中毒状态，直至其下个回合结束。中毒期间，目标无法恢复生命值。\n成功：仅半伤。"
      },
      {
        "name": "4. 解离射线",
        "en_name": "Disintegration \nRay",
        "description": "敏捷豁免检定：DC14。失败：27（5d10）力场伤害。若目标是一件非魔法物件或魔法力场造物，则其上一处10尺立方区域内的部分被解离为尘埃。成功：半伤。成功或失败：若目标为生物且因此伤害生命值降至0，则该生物被解离为尘埃。"
      }
    ],
    "source_file": "亡灵\\丧尸\\眼魔丧尸.htm"
  },
  {
    "name": "食人魔丧尸",
    "en_name": "Ogre Zombie",
    "type_line": "大型亡灵，中立邪恶",
    "size": "Large",
    "creature_type": "亡灵",
    "alignment": "中立邪恶",
    "ac": 8,
    "initiative_bonus": -2,
    "initiative_total": 8,
    "hp": 85,
    "hp_formula": "9d10+36",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 19,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 3,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 8
    },
    "languages": "理解通用语和巨人语，但不会说",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "不死坚韧",
        "en_name": "Undead Fortitude",
        "description": "当丧尸因非光耀非重击伤害生命值降至0时，其进行一次体质豁免（DC为5+所受伤害）。豁免成功则改为将生命值降至1。"
      }
    ],
    "actions": [
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+6，触及5尺。命中：13（2d8+4）钝击伤害。"
      }
    ],
    "source_file": "亡灵\\丧尸\\食人魔丧尸.htm"
  },
  {
    "name": "妖鬼",
    "en_name": "Ghast",
    "type_line": "中型亡灵，混乱邪恶",
    "size": "Medium",
    "creature_type": "亡灵",
    "alignment": "混乱邪恶",
    "ac": 13,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 36,
    "hp_formula": "8d8",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 2
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "damage_resistances": [
      "暗蚀"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "通用语",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "traits": [
      {
        "name": "恶臭",
        "en_name": "Stench",
        "description": "体质豁免检定：DC10，在源自妖鬼的5尺光环区域内开始其回合的每名生物。失败：目标陷入中毒状态，直至其下个回合开始。成功：目标在24小时内免疫此妖鬼的恶臭。"
      }
    ],
    "actions": [
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+5，触及5尺。命中：7（1d8+3）穿刺伤害外加9（2d8）暗蚀伤害。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+5，触及5尺。命中：10（2d6+3）挥砍伤害。若目标为非亡灵生物，承受以下效应。体质豁免检定：DC10。失败：目标陷入麻痹状态，直至其下个回合结束。"
      }
    ],
    "source_file": "亡灵\\妖鬼\\妖鬼.htm"
  },
  {
    "name": "妖鬼坟语者",
    "en_name": "Ghast Gravecaller",
    "type_line": "中型亡灵，混乱邪恶",
    "size": "Medium",
    "creature_type": "亡灵",
    "alignment": "混乱邪恶",
    "ac": 16,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 97,
    "hp_formula": "15d8+30",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "智力": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "感知": {
        "score": 14,
        "mod": 2,
        "save": 5
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 12
    },
    "languages": "深渊语，通用语",
    "cr": 6,
    "xp": 2300,
    "pb": 3,
    "traits": [
      {
        "name": "恶臭",
        "en_name": "Stench",
        "description": "体质豁免检定：DC10，在源自妖鬼的5尺光环区域内开始其回合的每名生物。失败：目标陷入中毒状态，直至其下个回合开始。成功：目标在24小时内免疫此妖鬼的恶臭。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "妖鬼发动两次骇怖坏灭攻击，其可以将其中一次攻击替换为爪击。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+6，触及5尺。命中：13（3d6+3）挥砍伤害。若目标为非亡灵生物，则其陷入麻痹状态，直至其下个回合结束。"
      },
      {
        "name": "骇怖坏灭",
        "en_name": "Horrific Necrosis",
        "description": "近战或远程攻击检定：+7，触及5尺或射程120尺。命中：15（2d10+4）暗蚀伤害，且目标陷入恐慌状态，直至其下个回合结束。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "妖鬼施展以下一道法术，无需材料成分并使用智力作为施法属性："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "死者交谈Speak with Dead，奇术Thaumaturgy"
      }
    ],
    "source_file": "亡灵\\妖鬼\\妖鬼坟语者.htm"
  },
  {
    "name": "木乃伊",
    "en_name": "Mummy",
    "type_line": "中型或小型亡灵，守序邪恶",
    "size": "Medium",
    "creature_type": "或小型亡灵",
    "alignment": "守序邪恶",
    "ac": 11,
    "initiative_bonus": -1,
    "initiative_total": 9,
    "hp": 58,
    "hp_formula": "9d8+18",
    "speed": {
      "walk": "20尺"
    },
    "abilities": {
      "力量": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "敏捷": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 3
      },
      "魅力": {
        "score": 12,
        "mod": 1,
        "save": 1
      }
    },
    "damage_vulnerabilities": [
      "火焰"
    ],
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "麻痹",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 11
    },
    "languages": "通用语以及两门任意语言",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "木乃伊发动两次腐朽拳击攻击，并使用恐怖怒视。"
      },
      {
        "name": "腐朽拳击",
        "en_name": "Rotting Fist",
        "description": "近战攻击检定：+5，触及5尺。命中：8（1d10+3）钝击伤害，外加10（3d6）暗蚀伤害。若目标为生物，则其被诅咒。受诅咒期间，目标无法恢复生命值，也无法在完成长休时恢复生命值上限，并且诅咒每持续24小时，其生命值上限降低10（3d6）。若生物因此攻击生命值降至0，则其立即死亡并化为尘土。"
      },
      {
        "name": "恐怖怒视",
        "en_name": "Dreadful Glare",
        "description": "感知豁免：DC11，单一60尺内木乃伊可见的生物。失败：目标陷入恐慌状态，直至木乃伊的下个回合结束。成功：目标在24小时内免疫此木乃伊的恐怖怒视。"
      }
    ],
    "source_file": "亡灵\\木乃伊\\木乃伊.htm"
  },
  {
    "name": "木乃伊领主",
    "en_name": "Mummy Lord",
    "type_line": "中型或小型亡灵（牧师），守序邪恶",
    "size": "Medium",
    "creature_type": "或小型亡灵（牧师）",
    "alignment": "守序邪恶",
    "ac": 17,
    "initiative_bonus": 10,
    "initiative_total": 20,
    "hp": 187,
    "hp_formula": "25d8+75",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 17,
        "mod": 3,
        "save": 3
      },
      "智力": {
        "score": 11,
        "mod": 0,
        "save": 5
      },
      "感知": {
        "score": 19,
        "mod": 4,
        "save": 9
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "skills": {
      "历史": 5,
      "察觉": 9,
      "宗教": 5
    },
    "damage_vulnerabilities": [
      "火焰"
    ],
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "麻痹",
      "中毒"
    ],
    "senses": {
      "真实视觉": 60,
      "被动察觉": 19
    },
    "languages": "通用语，外加三门其他语言",
    "cr": 15,
    "xp": 13000,
    "pb": 5,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "木乃伊的豁免失败时，可以将其改为豁免成功。",
        "params": "3/日，或巢穴内4/日"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "木乃伊对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "不死再造",
        "en_name": "Undead Restoration",
        "description": "若木乃伊被摧毁且其心脏完好无损，则在24小时后获得一副新的身体并恢复全部生命值。新身体会出现在木乃伊巢穴内一处未占据空间。心脏是一个AC17，HP10且免疫所有非火焰伤害的物件。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "木乃伊发动一次腐朽拳击或引导负能量攻击，并使用恐怖怒视。"
      },
      {
        "name": "腐朽拳击",
        "en_name": "Rotting Fist",
        "description": "近战攻击检定：+9，触及5尺。命中：15（2d10+4）钝击伤害，外加10（3d6）暗蚀伤害。若目标为生物，则其被诅咒。目标无法恢复生命值，也无法在完成长休时恢复生命值上限，并且诅咒每持续24小时，其生命值上限降低10（3d6）。若生物因此攻击生命值降至0，则其立即死亡并化为尘土。"
      },
      {
        "name": "引导负能量",
        "en_name": "Channel Negative Energy",
        "description": "远程攻击检定：+9，射程60尺。命中：25（6d6+4）暗蚀伤害。"
      },
      {
        "name": "恐怖怒视",
        "en_name": "Dreadful Glare",
        "description": "感知豁免：DC17，单一60尺内木乃伊可见的生物。失败：25（6d6+4）心灵伤害，且目标陷入麻痹状态，直至木乃伊的下个回合结束。"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "木乃伊施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC17，法术攻击检定+9）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "解除魔法Dispel Magic，奇术Thaumaturgy"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "活化死尸Animate Dead，重伤术Harm，疫病虫群Insect Plague（7环版本）"
      }
    ],
    "reactions": [
      {
        "name": "沙旋风",
        "en_name": "Whirlwind of Sand",
        "description": "触发：木乃伊被一次攻击检定命中。"
      }
    ],
    "legendary_actions": [
      {
        "name": "震怖命令",
        "en_name": "Dread Command",
        "description": "木乃伊施展命令术Command（二环版本），使用与施法动作相同的施法属性。木乃伊直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "怒视",
        "en_name": "Glare",
        "description": "木乃伊使用恐怖怒视。木乃伊直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "死灵打击",
        "en_name": "Necrotic Strike",
        "description": "木乃伊发动一次腐朽拳击或引导负能量攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "亡灵\\木乃伊\\木乃伊领主.htm"
  },
  {
    "name": "死亡骑士",
    "en_name": "Death Knight",
    "type_line": "中型或小型亡灵，混乱邪恶",
    "size": "Medium",
    "creature_type": "或小型亡灵",
    "alignment": "混乱邪恶",
    "ac": 20,
    "initiative_bonus": 12,
    "initiative_total": 22,
    "hp": 199,
    "hp_formula": "21d8+105",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 6
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "智力": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 9
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 4
      }
    },
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "恐慌",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 13
    },
    "languages": "深渊语，通用语",
    "cr": 17,
    "xp": 18000,
    "pb": 6,
    "traits": [
      {
        "name": "传奇抗性",
        "en_name": "Legendary Resistance",
        "description": "死亡骑士豁免失败时，可以将其改为豁免成功。",
        "params": "3/日"
      },
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "死亡骑士对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "不死统帅",
        "en_name": "Marshal Undead",
        "description": "只要死亡骑士未陷入失能状态，位于源自死亡骑士的60尺光环区域内的由其选择的（除其自身外的）任意亡灵进行攻击检定和豁免检定时具有优势。"
      },
      {
        "name": "亡灵复苏",
        "en_name": "Undead Restoration",
        "description": "若死亡骑士在赎罪前被消灭，其在1d10天后获得一副新的躯体，以满生命值复活。新躯体会出现在对死亡骑士来说意义重大的位置。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "死亡骑士发动三次恐怖之刃攻击。"
      },
      {
        "name": "恐怖之刃",
        "en_name": "Dread Blade",
        "description": "近战攻击检定：+11，触及5尺。命中：12（2d6+5）挥砍伤害外加13（3d8）暗蚀伤害。"
      },
      {
        "name": "地狱火珠",
        "en_name": "Hellfire Orb",
        "description": "敏捷豁免检定：DC18，以120尺内死亡骑士可见一点为中心，半径20尺球状区域内的每名生物。失败：35（10d6）火焰伤害外加35（10d6）的暗蚀伤害。成功：半伤。",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "死亡骑士施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC18）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "命令术Command，魅影驹Phantom Steed"
      },
      {
        "name": "每项2/日：",
        "en_name": "",
        "description": "湮灭波Destructive Wave（暗蚀），解除魔法Dispel Magic"
      }
    ],
    "reactions": [
      {
        "name": "格挡",
        "en_name": "Parry",
        "description": "触发：死亡骑士在持握武器期间因近战攻击检定被命中。响应：死亡骑士令其对抗那次攻击的AC+6，可能令那次攻击改为失手。"
      }
    ],
    "legendary_actions": [
      {
        "name": "恐怖权威",
        "en_name": "Dread Authority",
        "description": "死亡骑士使用施法施展命令术Command。此后死亡骑士不能再执行此动作，直至其下一回合开始。",
        "max_uses": 3
      },
      {
        "name": "堕落真言",
        "en_name": "Fell Word",
        "description": "体质豁免检定：DC18，单一120尺内死亡骑士可见的生物。失败：17（5d6）暗蚀伤害，目标的生命值上限减少等于其受到伤害的数值。失败或成功：死亡骑士直至其下个回合开始都无法再执行此动作。",
        "max_uses": 3
      },
      {
        "name": "猛冲",
        "en_name": "Lunge",
        "description": "死亡骑士移动至多等于其速度一半的距离，并发动一次恐怖之刃攻击。",
        "max_uses": 3
      }
    ],
    "source_file": "亡灵\\死亡骑士\\死亡骑士.htm"
  },
  {
    "name": "死亡骑士志从",
    "en_name": "Death Knight Aspirant",
    "type_line": "中型或小型亡灵，混乱邪恶",
    "size": "Medium",
    "creature_type": "或小型亡灵",
    "alignment": "混乱邪恶",
    "ac": 20,
    "initiative_bonus": 4,
    "initiative_total": 14,
    "hp": 178,
    "hp_formula": "21d8+84",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 10,
        "mod": 0,
        "save": 4
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 12,
        "mod": 1,
        "save": 5
      },
      "魅力": {
        "score": 16,
        "mod": 3,
        "save": 3
      }
    },
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "恐慌",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 11
    },
    "languages": "深渊语，通用语",
    "cr": 11,
    "xp": 7200,
    "pb": 4,
    "traits": [
      {
        "name": "魔法抗性",
        "en_name": "Magic Resistance",
        "description": "死亡骑士志从对抗法术和其他魔法效应时进行的豁免检定具有优势。"
      },
      {
        "name": "不死统帅",
        "en_name": "Marshal Undead",
        "description": "只要死亡骑士志从未陷入失能状态，位于源自死亡骑士志从的60尺光环区域内的由其选择的（除其自身外的）任意亡灵进行攻击检定和豁免检定时具有优势。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "死亡骑士志从发动三次恐怖之刃攻击。"
      },
      {
        "name": "恐怖之刃",
        "en_name": "Dread Blade",
        "description": "近战攻击检定：+9，触及5尺。命中：14（2d8+5）挥砍伤害外加10（3d6）暗蚀伤害。"
      },
      {
        "name": "地狱火珠",
        "en_name": "Hellre Orb",
        "description": "敏捷豁免检定：DC15，以120尺内死亡骑士志从可见一点为中心，半径20尺球状区域内的每名生物。失败：21（6d6）火焰伤害外加21（6d6）的暗蚀伤害。成功：半伤",
        "params": "充能5~6"
      },
      {
        "name": "施法",
        "en_name": "Spellcasting",
        "description": "死亡骑士志从施展以下一道法术，无需材料成分并使用魅力作为施法属性（法术豁免DC15）："
      },
      {
        "name": "随意：",
        "en_name": "",
        "description": "魅影驹Phantom Steed"
      },
      {
        "name": "每项1/日：",
        "en_name": "",
        "description": "湮灭波Destructive Wave（暗蚀），解除魔法Dispel Magic"
      }
    ],
    "reactions": [
      {
        "name": "格挡",
        "en_name": "Parry",
        "description": "死亡骑士在持握武器期间因近战攻击检定被命中。响应：死亡骑士令其对抗那次攻击的AC+4，可能令那次攻击改为失手。"
      }
    ],
    "source_file": "亡灵\\死亡骑士\\死亡骑士志从.htm"
  },
  {
    "name": "蠕行之爪",
    "en_name": "Crawling Claw",
    "type_line": "微型亡灵，中立邪恶",
    "size": "Tiny",
    "creature_type": "亡灵",
    "alignment": "中立邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 2,
    "hp_formula": "1d4",
    "speed": {
      "walk": "20尺，攀爬20尺"
    },
    "abilities": {
      "力量": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 4,
        "mod": -3,
        "save": -3
      }
    },
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "失能",
      "中毒"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 10
    },
    "languages": "理解通用语，但不会说",
    "cr": 0,
    "xp": 10,
    "pb": 2,
    "actions": [
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+3，触及5尺。命中：2暗蚀伤害。"
      }
    ],
    "source_file": "亡灵\\蠕行之爪\\蠕行之爪.htm"
  },
  {
    "name": "蠕行之爪集群",
    "en_name": "Swarm of Crawling Claw",
    "type_line": "微型亡灵的中型集群，中立邪恶",
    "size": "Tiny",
    "creature_type": "亡灵的中型集群",
    "alignment": "中立邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 49,
    "hp_formula": "11d8",
    "speed": {
      "walk": "30尺，攀爬30尺"
    },
    "abilities": {
      "力量": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 5,
        "mod": -3,
        "save": -3
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 4,
        "mod": -3,
        "save": -3
      }
    },
    "damage_resistances": [
      "钝击",
      "穿刺",
      "挥砍"
    ],
    "damage_immunities": [
      "暗蚀",
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "受擒",
      "失能",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚",
      "震慑"
    ],
    "senses": {
      "盲视": 30,
      "被动察觉": 10
    },
    "languages": "理解通用语，但不会说",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "集群",
        "en_name": "Swarm",
        "description": "集群可以进驻另一生物身处的空间，反之亦然。而且集群可以通过任何足够一只微型生物通过的通道。集群不能恢复生命值也不能获得临时生命值 。"
      }
    ],
    "actions": [
      {
        "name": "集群擒拿手",
        "en_name": "Swarm of Grasping Hands",
        "description": "近战攻击检定：+4，触及5尺。\n命中：20（4d8+2）暗蚀伤害。若集群处于浴血则改为11（2d8+2）暗蚀伤害。若目标生物体型不超过中型，则其陷入倒地状态。"
      }
    ],
    "source_file": "亡灵\\蠕行之爪\\蠕行之爪集群.htm"
  },
  {
    "name": "还魂尸山",
    "en_name": "Graveyard Revenant",
    "type_line": "巨型亡灵，中立",
    "size": "Huge",
    "creature_type": "亡灵",
    "alignment": "中立",
    "ac": 14,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 161,
    "hp_formula": "14d12+70",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 8
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 20,
        "mod": 5,
        "save": 8
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 7
      }
    },
    "damage_resistances": [
      "暗蚀",
      "心灵"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "麻痹",
      "石化",
      "中毒",
      "震慑",
      "昏迷"
    ],
    "senses": {
      "黑暗视觉": 120,
      "被动察觉": 13
    },
    "languages": "通用语以及两门其他语言",
    "cr": 7,
    "xp": 2900,
    "pb": 3,
    "traits": [
      {
        "name": "亡灵复苏",
        "en_name": "Undead Restoraton",
        "description": "若还魂尸山死亡，除非对其遗留物施展驱逐善恶Dispel Evil or \nGood   ，否则其在24小时后复生。还魂尸山复生后会活化同一存在位面中的另一群尸体；这会改变其外形，但不会改变其游戏数据，且还魂尸山以满生命值复活。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "还魂尸山发动两次窒灭攻击。"
      },
      {
        "name": "窒灭",
        "en_name": "Suffocate",
        "description": "近战攻击检定：+8，触及10尺。命中：10（1d10+5）钝击伤害外加10（3d6）暗蚀伤害。若目标生物不超过大型，则其陷入受擒状态（逃脱DC15）。受擒期间，目标窒息。还魂尸山以此法同时能擒抱的生物数上限为二。"
      },
      {
        "name": "缠魂怒视",
        "en_name": "Haunting Glare",
        "description": "感知豁免检定：DC15，源自还魂尸山的30尺光环区域内的每名生物。失败：目标陷入麻痹状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。",
        "params": "充能5~6"
      }
    ],
    "source_file": "亡灵\\还魂鬼\\还魂尸山.htm"
  },
  {
    "name": "还魂巨构",
    "en_name": "Haunting Revenant",
    "type_line": "超巨型亡灵，中立",
    "size": "Gargantuan",
    "creature_type": "亡灵",
    "alignment": "中立",
    "ac": 20,
    "initiative_bonus": 5,
    "initiative_total": 15,
    "hp": 203,
    "hp_formula": "14d20+56",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 20,
        "mod": 5,
        "save": 5
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 8
      },
      "智力": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "感知": {
        "score": 18,
        "mod": 4,
        "save": 8
      },
      "魅力": {
        "score": 20,
        "mod": 5,
        "save": 5
      }
    },
    "damage_resistances": [
      "暗蚀",
      "心灵"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "受擒",
      "麻痹",
      "石化",
      "中毒",
      "倒地",
      "束缚",
      "昏迷"
    ],
    "senses": {
      "真实视觉": 60,
      "被动察觉": 14
    },
    "languages": "通用语以及两门其他语言",
    "cr": 10,
    "xp": 5900,
    "pb": 4,
    "traits": [
      {
        "name": "缠魂之地",
        "en_name": "Haunted Zone",
        "description": "体质豁免检定：DC17，在还魂巨构的空间中施展法术的每名生物。失败：该法术失败并被浪费。"
      },
      {
        "name": "亡灵复苏",
        "en_name": "Undead Restoraton",
        "description": "若还魂巨构死亡，除非对其遗留物施展驱逐善恶Dispel Evil or \nGood   ，否则其在24小时后复生。还魂巨构复生后会活化同一存在位面中的另一个超巨型物件或建筑；这会改变其外形，但不会改变其游戏数据，且归来时还魂巨构具有全部生命值。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "还魂巨构发动两次物件猛袭攻击并使用请君入瓮。"
      },
      {
        "name": "物件猛袭",
        "en_name": "Object Slam",
        "description": "近战或远程攻击检定：+9（若目标位于还魂巨构所处的空间内则具有优势），触及10尺或射程30/90尺。命中：27（5d8+5）钝击伤害。"
      },
      {
        "name": "请君入瓮",
        "en_name": "Invitation",
        "description": "魅力豁免检定：DC17，60尺锥状区域内的每名生物。失败：目标被传送至还魂巨构所处的空间内并被吞下。被吞下生物对还魂巨构体外的攻击或其他效应而言处于全身掩护。"
      }
    ],
    "source_file": "亡灵\\还魂鬼\\还魂巨构.htm"
  },
  {
    "name": "还魂鬼",
    "en_name": "Revenant",
    "type_line": "中型亡灵，中立",
    "size": "Medium",
    "creature_type": "亡灵",
    "alignment": "中立",
    "ac": 13,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 127,
    "hp_formula": "15d8+60",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 18,
        "mod": 4,
        "save": 7
      },
      "智力": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "感知": {
        "score": 16,
        "mod": 3,
        "save": 6
      },
      "魅力": {
        "score": 18,
        "mod": 4,
        "save": 7
      }
    },
    "damage_resistances": [
      "暗蚀",
      "心灵"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "恐慌",
      "麻痹",
      "中毒",
      "震慑"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 13
    },
    "languages": "通用语以及两门其他语言",
    "cr": 5,
    "xp": 1800,
    "pb": 3,
    "traits": [
      {
        "name": "再生",
        "en_name": "Regeneration",
        "description": "还魂鬼在其回合开始时恢复10生命值。若还魂鬼受到火焰或光耀伤害，则该特质在其下个回合开始时无法生效。还魂鬼的躯体只有以0生命值开始其回合且无法再生时，才会被摧毁。"
      },
      {
        "name": "亡灵复苏",
        "en_name": "Undead Restoraton",
        "description": "若还魂鬼死亡，除非对其遗体施展驱逐善恶Dispel Evil or \nGood，否则其在24小时后于另一躯体上复生 \n   。还魂鬼复生后会活化同一存在位面中的另一具类人遗体，这会改变其外形，但不会改变其游戏数据，且还魂鬼以满生命值复活。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "还魂鬼使用复仇怒视并发动两次猛击攻击。"
      },
      {
        "name": "猛击攻击",
        "en_name": "Slam",
        "description": "近战攻击检定：+7，触及5尺。命中：11（2d6+4）暗蚀伤害。"
      },
      {
        "name": "复仇怒视",
        "en_name": "Vengeful Glare",
        "description": "感知豁免检定：DC15，单一30尺内还魂鬼可见的生物。失败：目标陷入恐慌状态，并在其回合结束时重复豁免，成功则终止其身上的该效应。1分钟后，其豁免自动成功。 若恐慌目标被还魂鬼诅咒（见死仇誓言），则目标还会在此期间陷入麻痹状态。"
      }
    ],
    "bonus_actions": [
      {
        "name": "死仇誓言",
        "en_name": "Vow of Revenge",
        "description": "还魂鬼诅咒其30尺内一名其可见的生物。还魂鬼将知晓自身与受诅咒目标之间的距离与方向，即使双方不在同一存在位面中亦是如此。该诅咒在还魂鬼对另一名生物使用此附赠动作时结束。",
        "params": "1/日"
      }
    ],
    "source_file": "亡灵\\还魂鬼\\还魂鬼.htm"
  },
  {
    "name": "食尸鬼",
    "en_name": "Ghoul",
    "type_line": "中型亡灵，混乱邪恶",
    "size": "Medium",
    "creature_type": "亡灵",
    "alignment": "混乱邪恶",
    "ac": 12,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 22,
    "hp_formula": "5d8",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 13,
        "mod": 1,
        "save": 1
      },
      "敏捷": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "智力": {
        "score": 7,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "魅力": {
        "score": 6,
        "mod": -2,
        "save": -2
      }
    },
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "魅惑",
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 10
    },
    "languages": "通用语",
    "cr": 1,
    "xp": 200,
    "pb": 2,
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "食尸鬼发动两次啃咬攻击。"
      },
      {
        "name": "啃咬",
        "en_name": "Bite",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）穿刺伤害，外加3（1d6）暗蚀伤害。"
      },
      {
        "name": "爪击",
        "en_name": "Claw",
        "description": "近战攻击检定：+4，触及5尺。命中：4（1d4+2）挥砍伤害。若目标非亡灵且非精灵，其承受以下效应。体质豁免：DC10。失败：目标陷入麻痹状态，直至其下个回合结束。"
      }
    ],
    "source_file": "亡灵\\食尸鬼\\食尸鬼.htm"
  },
  {
    "name": "燃火骷髅",
    "en_name": "Flaming Skeleton",
    "type_line": "中型亡灵，守序邪恶",
    "size": "Medium",
    "creature_type": "亡灵",
    "alignment": "守序邪恶",
    "ac": 15,
    "initiative_bonus": 2,
    "initiative_total": 12,
    "hp": 65,
    "hp_formula": "10d8+20",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 14,
        "mod": 2,
        "save": 2
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "感知": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "魅力": {
        "score": 8,
        "mod": -1,
        "save": -1
      }
    },
    "damage_vulnerabilities": [
      "钝击"
    ],
    "damage_immunities": [
      "火焰",
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 12
    },
    "languages": "理解通用语以及一门其他语言，但不会说",
    "cr": 3,
    "xp": 700,
    "pb": 2,
    "traits": [
      {
        "name": "自爆",
        "en_name": "Death Burst",
        "description": "骷髅在死亡时爆炸。敏捷豁免：DC12，源自骷髅的10尺光环区域内的每名生物。失败：14（4d6）火焰伤害。成功：半伤。"
      },
      {
        "name": "照明",
        "en_name": "Illumination",
        "description": "骷髅散发出半径15尺明亮光照以及额外15尺的微光光照。"
      }
    ],
    "actions": [
      {
        "name": "多重攻击",
        "en_name": "Multiattack",
        "description": "骷髅使用火焰节杖或投掷烈焰发动共计两次攻击。"
      },
      {
        "name": "火焰节杖",
        "en_name": "Fire Scepter",
        "description": "近战攻击检定：+4，触及5尺。命中：5（1d6+2）钝击伤害外加3（1d6）火焰伤害。"
      },
      {
        "name": "投掷烈焰",
        "en_name": "Hurl Flame",
        "description": "远程攻击检定：+4，射程60尺。命中：7（1d10+2）火焰伤害。"
      }
    ],
    "source_file": "亡灵\\骷髅\\燃火骷髅.htm"
  },
  {
    "name": "骷髅",
    "en_name": "Skeleton",
    "type_line": "中型亡灵，守序邪恶",
    "size": "Medium",
    "creature_type": "亡灵",
    "alignment": "守序邪恶",
    "ac": 14,
    "initiative_bonus": 3,
    "initiative_total": 13,
    "hp": 13,
    "hp_formula": "2d8+4",
    "speed": {
      "walk": "30尺"
    },
    "abilities": {
      "力量": {
        "score": 10,
        "mod": 0,
        "save": 0
      },
      "敏捷": {
        "score": 16,
        "mod": 3,
        "save": 3
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "damage_vulnerabilities": [
      "钝击"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "中毒"
    ],
    "equipment": "短弓，短剑",
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "理解通用语以及一门其他语言，但不会说",
    "cr": "1/4",
    "xp": 50,
    "pb": 2,
    "actions": [
      {
        "name": "短剑",
        "en_name": "Shortsword",
        "description": "近战攻击检定：+5，触及5尺。命中：6（1d6+3）穿刺伤害。"
      },
      {
        "name": "短弓",
        "en_name": "Shortbow",
        "description": "远程攻击检定：+5，射程80/320尺。命中：6（1d6+3）穿刺伤害。"
      }
    ],
    "source_file": "亡灵\\骷髅\\骷髅.htm"
  },
  {
    "name": "骷髅战马",
    "en_name": "Warhorse Skeleton",
    "type_line": "大型亡灵，守序邪恶",
    "size": "Large",
    "creature_type": "亡灵",
    "alignment": "守序邪恶",
    "ac": 13,
    "initiative_bonus": 1,
    "initiative_total": 11,
    "hp": 22,
    "hp_formula": "3d10+6",
    "speed": {
      "walk": "60尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 12,
        "mod": 1,
        "save": 1
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 2,
        "mod": -4,
        "save": -4
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "damage_vulnerabilities": [
      "钝击"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "无",
    "cr": "1/2",
    "xp": 100,
    "pb": 2,
    "actions": [
      {
        "name": "蹄击",
        "en_name": "Hooves",
        "description": "近战攻击检定：+6，触及5尺。命中：7（1d6+4）钝击伤害。如果骷髅在此次攻击前立即向着目标直线移动了20+尺，且目标生物体型不超过大型，则目标陷入倒地状态。"
      }
    ],
    "source_file": "亡灵\\骷髅\\骷髅战马.htm"
  },
  {
    "name": "骷髅牛头人",
    "en_name": "Minotaur Skeleton",
    "type_line": "大型亡灵，守序邪恶",
    "size": "Large",
    "creature_type": "亡灵",
    "alignment": "守序邪恶",
    "ac": 12,
    "initiative_bonus": 0,
    "initiative_total": 10,
    "hp": 45,
    "hp_formula": "6d10+12",
    "speed": {
      "walk": "40尺"
    },
    "abilities": {
      "力量": {
        "score": 18,
        "mod": 4,
        "save": 4
      },
      "敏捷": {
        "score": 11,
        "mod": 0,
        "save": 0
      },
      "体质": {
        "score": 15,
        "mod": 2,
        "save": 2
      },
      "智力": {
        "score": 6,
        "mod": -2,
        "save": -2
      },
      "感知": {
        "score": 8,
        "mod": -1,
        "save": -1
      },
      "魅力": {
        "score": 5,
        "mod": -3,
        "save": -3
      }
    },
    "damage_vulnerabilities": [
      "钝击"
    ],
    "damage_immunities": [
      "毒素"
    ],
    "condition_immunities": [
      "力竭",
      "中毒"
    ],
    "senses": {
      "黑暗视觉": 60,
      "被动察觉": 9
    },
    "languages": "理解深渊语，但不会说",
    "cr": 2,
    "xp": 450,
    "pb": 2,
    "actions": [
      {
        "name": "顶撞",
        "en_name": "Gore",
        "description": "近战攻击检定：+6，触及5尺。命中：11（2d6+4）穿刺伤害。如果骷髅在此次攻击前立即向着目标直线移动了20+尺，且目标生物体型不超过大型，则目标额外受到9（2d8）穿刺伤害陷入倒地状态。"
      },
      {
        "name": "猛击",
        "en_name": "Slam",
        "description": "近战攻击检定：+6，触及5尺。命中：15（2d10+4）钝击伤害。"
      }
    ],
    "source_file": "亡灵\\骷髅\\骷髅牛头人.htm"
  }
]

MONSTERS: dict[str, dict] = {m["name"]: m for m in _MONSTERS_LIST}
EN_MONSTERS: dict[str, dict] = {m["en_name"]: m for m in _MONSTERS_LIST if m.get("en_name")}
CR_MONSTERS: dict[str, list[dict]] = {}
for m in _MONSTERS_LIST:
    cr_key = str(m.get("cr", "?"))
    CR_MONSTERS.setdefault(cr_key, []).append(m)
