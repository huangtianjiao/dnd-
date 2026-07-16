"""专长数据表 — PHB 2024 第五章「专长」。

数据来源（L0 原始权威）:
  - topics/玩家手册2024/专长/专长概述.htm        （分类总览 + 专长列表）
  - topics/玩家手册2024/专长/起源专长.htm        （10 个起源专长）
  - topics/玩家手册2024/专长/战斗风格专长.htm    （9 个战斗风格专长）
  - topics/玩家手册2024/专长/通用专长.htm        （通用专长详述）
  - topics/玩家手册2024/专长/传奇恩惠专长.htm    （12 个传奇恩惠专长）

专长结构（见 专长概述.htm「专长的组成部分」）:
  - name_zh / name_en: 中英文名
  - category: 起源 / 通用 / 战斗风格 / 传奇恩惠
  - prerequisite: 先决条件（无则空串）
  - repeatable: 是否可复选（名字带 * 的）
  - description: 整体描述
  - effects: 增益条目列表 [{name, text}]
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────
# 起源专长 Origin Feats — 出处: 起源专长.htm
# ──────────────────────────────────────────────────────────────────────────

_ALERT = {
    "name_zh": "警戒",
    "name_en": "Alert",
    "category": "起源",
    "prerequisite": "",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "先攻熟练 Initiative Proficiency",
         "text": "当你投掷先攻时，你可以将你的熟练加值加入结果。"},
        {"name": "先攻互换 Initiative Swap",
         "text": "当你掷完先攻，你可以立即与处于同一场战斗中的一名自愿的盟友交换先攻。如果你或那个盟友正处于失能状态，则不能进行交换。"},
    ],
}

_CRAFTER = {
    "name_zh": "巧匠",
    "name_en": "Crafter",
    "category": "起源",
    "prerequisite": "",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "工具熟练 Tool Proficiency",
         "text": "你从快速制作表中自选三项不同的工匠工具并获得其熟练。"},
        {"name": "折扣 Discount",
         "text": "你在购买非魔法物品时具有20%的折扣。"},
        {"name": "快速制作 Fast Crafting",
         "text": "当你完成一次长休时，你可以制作一件快速制作栏中的装备。你必须拥有与该物品对应的工匠工具以及与这些工具对应的工具熟练才能尝试制作。造出的物品会持续存在到你下次完成长休，随后该物品解体坏损。"},
    ],
}

_HEALER = {
    "name_zh": "医疗师",
    "name_en": "Healer",
    "category": "起源",
    "prerequisite": "",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "战地医师 Battle Medic",
         "text": "如果你有医疗包，以一个操作动作，你可以消耗医疗包的一次使用次数来救治一个位于你5尺内的生物。该生物可以消耗一枚生命骰，然后由你来投掷它，令该生物恢复等于所掷出的点数+你的熟练加值点生命值。"},
        {"name": "治疗重掷 Healing Rerolls",
         "text": "当你掷骰以决定用法术或此专长的战地医师增益所恢复的生命值时，你可以重掷其中掷出1的骰子，但你必须使用重掷的结果。"},
    ],
}

_LUCKY = {
    "name_zh": "幸运",
    "name_en": "Lucky",
    "category": "起源",
    "prerequisite": "",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "幸运点 Lucky Point",
         "text": "你拥有一些幸运点，其数量等同于你的熟练加值。你可以将点数花在下列的增益上。你在完成一次长休时重新获得所有已消耗的幸运点。"},
        {"name": "优势 Advantage",
         "text": "当你为了一次D20检定而投掷d20时，你可以花费一个幸运点来给予这次检定优势。"},
        {"name": "劣势 Disadvantage",
         "text": "当一个生物为了一次对你发动的攻击检定而投掷d20时，你可以花费一个幸运点来为这次检定施加劣势。"},
    ],
}

_MAGIC_INITIATE = {
    "name_zh": "魔法学徒",
    "name_en": "Magic Initiate",
    "category": "起源",
    "prerequisite": "",
    "repeatable": True,
    "description": "你获得以下增益：复选：你可多次选择本专长，但是你每次都必须选择一个不同的法术列表。",
    "effects": [
        {"name": "两道戏法 Two Cantrips",
         "text": "从牧师法术列表、德鲁伊法术列表、法师法术列表中选择一个列表，你从该法术列表中选择两道戏法并习得之。再从智力、感知、魅力中选择一项属性，你从这个专长中习得的法术使用该属性作为施法属性。"},
        {"name": "一环法术 Level 1 Spell",
         "text": "你从前面所选的法术列表中再选择一道一环法术，并始终准备着这道法术。你可以无需法术位地施展该法术一次，并在完成长休后重获以此法施展该法术的能力。你也可以使用你拥有的任何法术位来施展该法术。"},
        {"name": "改变法术 Spell Change",
         "text": "每当你获得一级新等级，你都能将通过本专长习得的一道法术替换为同法术列表中同环阶的另一道法术。"},
    ],
}

_MUSICIAN = {
    "name_zh": "音乐家",
    "name_en": "Musician",
    "category": "起源",
    "prerequisite": "",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "乐器训练 Instrument Training",
         "text": "你获得三种自选的乐器的熟练。"},
        {"name": "鼓舞之歌 Encouraging Song",
         "text": "作为你完成短休或长休的一部分，你可以用你熟练的乐器演奏一首歌曲，并令听到这首乐歌的盟友获得英雄激励。以这种方式所能影响的盟友数量最多等于你的熟练加值。"},
    ],
}

_SAVAGE_ATTACKER = {
    "name_zh": "凶蛮打手",
    "name_en": "Savage Attacker",
    "category": "起源",
    "prerequisite": "",
    "repeatable": False,
    "description": "你专门训练过如何做出更具破坏性的进攻。每回合一次，当你使用武器命中目标时，你可以掷两次武器的伤害骰，并自选其中一次应用在目标上。",
    "effects": [],
}

_SKILLED = {
    "name_zh": "熟习",
    "name_en": "Skilled",
    "category": "起源",
    "prerequisite": "",
    "repeatable": True,
    "description": "你获得共计三项自选的技能和工具熟练。复选：你可多次选择本专长。",
    "effects": [],
}

_TAVERN_BRAWLER = {
    "name_zh": "酒馆斗殴者",
    "name_en": "Tavern Brawler",
    "category": "起源",
    "prerequisite": "",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "强化徒手打击 Enhanced Unarmed Strike",
         "text": "当你使用徒手打击命中并造成伤害时，你可以造成1d4+你力量调整值的钝击伤害，而非徒手打击的原本伤害。"},
        {"name": "伤害重掷 Damage Rerolls",
         "text": "当你为徒手打击掷伤害骰时，你可以重掷其中掷出1的骰子，但你必须使用重掷的结果。"},
        {"name": "临时武器专家 Improvised Weaponry",
         "text": "你拥有临时武器的熟练。"},
        {"name": "推离 Push",
         "text": "在你的回合内，如果你用攻击动作中的一次徒手打击命中了一个生物，你可以在对目标造成伤害的同时将它推离5尺。你每回合只能使用这个增益一次。"},
    ],
}

_TOUGH = {
    "name_zh": "健壮",
    "name_en": "Tough",
    "category": "起源",
    "prerequisite": "",
    "repeatable": False,
    "description": "获得该专长时，你的生命值上限提升你当前角色等级两倍的数值。并且在你随后每次升级时，你的生命值上限都会额外提升2。",
    "effects": [],
}

# ──────────────────────────────────────────────────────────────────────────
# 战斗风格专长 Fighting Style Feats — 出处: 战斗风格专长.htm
# 先决均为「战斗风格特性」
# ──────────────────────────────────────────────────────────────────────────

_ARCHERY = {
    "name_zh": "箭术",
    "name_en": "Archery",
    "category": "战斗风格",
    "prerequisite": "战斗风格特性",
    "repeatable": False,
    "description": "你使用远程武器进行的攻击检定获得+2加值。",
    "effects": [],
}

_BLIND_FIGHTING = {
    "name_zh": "盲斗",
    "name_en": "Blind Fighting",
    "category": "战斗风格",
    "prerequisite": "战斗风格特性",
    "repeatable": False,
    "description": "你具有10尺盲视。",
    "effects": [],
}

_DEFENSE = {
    "name_zh": "防御",
    "name_en": "Defense",
    "category": "战斗风格",
    "prerequisite": "战斗风格特性",
    "repeatable": False,
    "description": "着装轻甲、中甲或重甲期间，你的护甲等级获得+1加值。",
    "effects": [],
}

_DUELING = {
    "name_zh": "对决",
    "name_en": "Dueling",
    "category": "战斗风格",
    "prerequisite": "战斗风格特性",
    "repeatable": False,
    "description": "当你单手持用一把近战武器且没有持用其他武器时，你使用那把武器进行的伤害掷骰获得+2加值。",
    "effects": [],
}

_GREAT_WEAPON_FIGHTING = {
    "name_zh": "巨武器战斗",
    "name_en": "Great Weapon Fighting",
    "category": "战斗风格",
    "prerequisite": "战斗风格特性",
    "repeatable": False,
    "description": "当你用双手持握的一把近战武器发动了一次攻击并为其进行伤害掷骰时，若该武器具有双手或多用词条，那么你便可以将伤害骰投出的1和2都视为3。",
    "effects": [],
}

_INTERCEPTION = {
    "name_zh": "拦截",
    "name_en": "Interception",
    "category": "战斗风格",
    "prerequisite": "战斗风格特性",
    "repeatable": False,
    "description": "当一名你可见的生物用攻击检定命中了另一生物，且被命中的生物位于你5尺内，你可以用反应减少来袭伤害，使该次攻击对其目标的伤害降低1d10+你的熟练加值点。你必须持握着一面盾牌或者一把简易/军用武器才能使用这个反应。",
    "effects": [],
}

_PROTECTION = {
    "name_zh": "守护",
    "name_en": "Protection",
    "category": "战斗风格",
    "prerequisite": "战斗风格特性",
    "repeatable": False,
    "description": "当一名你可见的生物以一名位于你5尺内的、除你以外的生物为目标发动攻击，如果你正持握着一面盾牌，你可以用反应将你的盾牌挡在其面前。你对触发反应的攻击检定施加劣势，并且直到你的下一回合开始为止，只要你还处于被守护的目标5尺范围内，其他的任何对守护目标进行的所有攻击检定也都将具有劣势。",
    "effects": [],
}

_THROWN_WEAPON_FIGHTING = {
    "name_zh": "投掷武器战斗",
    "name_en": "Thrown Weapon Fighting",
    "category": "战斗风格",
    "prerequisite": "战斗风格特性",
    "repeatable": False,
    "description": "当你使用具有投掷词条的武器进行远程攻击检定并命中时，你在该次伤害掷骰中获得+2加值。",
    "effects": [],
}

_TWO_WEAPON_FIGHTING = {
    "name_zh": "双武器战斗",
    "name_en": "Two-Weapon Fighting",
    "category": "战斗风格",
    "prerequisite": "战斗风格特性",
    "repeatable": False,
    "description": "当你因使用具有轻型词条的武器而得以发动额外的攻击时，若此次额外的攻击的伤害本来无法加入你的属性调整值，你可以加入你的属性调整值。",
    "effects": [],
}

# ──────────────────────────────────────────────────────────────────────────
# 通用专长 General Feats — 出处: 通用专长.htm
# 多数先决为「等级4+」加属性要求；此处按原文逐条录入
# ──────────────────────────────────────────────────────────────────────────

_ASI = {
    "name_zh": "属性值提升",
    "name_en": "Ability Score Improvement",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": True,
    "description": "你选择的一项属性提升2，或者你选择的两项属性各提升1。你无法依靠本专长令某个属性值超出20。复选：你可多次选择本专长。",
    "effects": [],
}

_ACTOR = {
    "name_zh": "演员",
    "name_en": "Actor",
    "category": "通用",
    "prerequisite": "等级4+，魅力13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的魅力提升1，至多提升至20。"},
        {"name": "伪装 Impersonation",
         "text": "伪装成某个虚构或真实的个体的情况下，你为使别人相信你就是那个个体所做的魅力（欺瞒或表演）检定具有优势。"},
        {"name": "拟声 Mimicry",
         "text": "你可以模仿出另一个生物的语音，甚至包括它的说话方式。听见你的拟声的生物必须通过一次感知（洞悉）检定才能发觉这种拟声是由他人伪造的（DC等于8+你的魅力调整值+你的熟练加值）。"},
    ],
}

_ATHLETE = {
    "name_zh": "运动精英",
    "name_en": "Athlete",
    "category": "通用",
    "prerequisite": "等级4+，力量或敏捷13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或敏捷提升1，至多提升至20。"},
        {"name": "攀爬速度 Climb Speed",
         "text": "你获得等同于你速度的攀爬速度。"},
        {"name": "鲤鱼打挺 Hop Up",
         "text": "处于倒地状态的情况下，你可以仅消耗5尺移动力来站起来。"},
        {"name": "跳跃 Jumping",
         "text": "你只需移动5尺距离便能进行一次助跑跳远或一次助跑跳高。"},
    ],
}

_CHARGER = {
    "name_zh": "冲锋手",
    "name_en": "Charger",
    "category": "通用",
    "prerequisite": "等级4+，力量或敏捷13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或敏捷提升1，至多提升至20。"},
        {"name": "进阶疾走 Improved Dash",
         "text": "当你执行疾走动作时，对该动作而言，你的速度提升了10尺。"},
        {"name": "冲锋攻击 Charge Attack",
         "text": "使用攻击动作中的近战攻击检定命中目标时，若你在此次攻击前立即向着目标直线移动了10+尺，你可以为这次攻击增添以下其中一个效应：此次攻击的伤害掷骰获得1d8的加值；将目标推离10尺，前提是目标体型不比你大超过一级。你只能在每个你自己的回合使用一次此增益。"},
    ],
}

_CHEF = {
    "name_zh": "大厨",
    "name_en": "Chef",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的体质或感知提升1，至多提升至20。"},
        {"name": "厨师工具 Cook's Utensils",
         "text": "如果你没有厨师工具的熟练，你获得之。"},
        {"name": "大补食膳 Replenishing Meal",
         "text": "作为短休的一部分，只要你手上有食材和厨师工具，你就可以烹饪一顿特别的美食。你可以为数个生物准备足够的此类食物，其数量等于4+你的熟练加值。在这一次短休结束时，任何吃了这些食物且花费了生命骰来恢复生命值的生物都能额外恢复1d8的生命值。"},
        {"name": "应急零嘴 Bolstering Treats",
         "text": "如果你手上有食材和厨师工具，你可以花费一小时的时间，或在完成一次长休时，烹饪出一定份数的零嘴，其数量等于你熟练加值。这些特别的小零嘴在做好后能保存八小时。一个生物可以使用一个附赠动作来吃掉其中一份零嘴，并获得等同于你熟练加值的临时生命值。"},
    ],
}

_CROSSBOW_EXPERT = {
    "name_zh": "强弩专家",
    "name_en": "Crossbow Expert",
    "category": "通用",
    "prerequisite": "等级4+，敏捷13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的敏捷提升1，至多提升至20。"},
        {"name": "无视装填 Ignore Loading",
         "text": "你无视手弩、重弩和轻弩的装填词条（在这个专长里统称弩）。如果你正手持着一把弩，你即使没有空手也能够为它装填一发弹药。"},
        {"name": "抵近射击 Firing in Melee",
         "text": "你用弩进行的攻击检定不会因你在敌人的5尺内而具有劣势。"},
        {"name": "双持射击 Dual Wielding",
         "text": "当你发动由轻型词条所提供的额外的攻击时，如果这次追加攻击是由一把具有轻型词条的弩所发动的，且你原本无法在伤害中加入属性调整值，你就可以改为可以将你的属性调整值加入本次伤害中。"},
    ],
}

_CRUSHER = {
    "name_zh": "粉碎者",
    "name_en": "Crusher",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或体质提升1，至多提升至20。"},
        {"name": "推动 Push",
         "text": "每回合一次，当你以造成钝击伤害的一次攻击命中了一个生物时，只要这个生物的体型不比你大超过一级，你就能将它移动5尺至一处未占据空间中。"},
        {"name": "强化重击 Enhanced Critical",
         "text": "当你掷出一次重击命中一名生物并对其造成钝击伤害后，直到你的下个回合开始前，任何以该生物为目标的攻击检定都会具有优势。"},
    ],
}

_DEFENSIVE_DUELIST = {
    "name_zh": "防御式决斗",
    "name_en": "Defensive Duelist",
    "category": "通用",
    "prerequisite": "等级4+，敏捷13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的敏捷提升1，至多提升至20。"},
        {"name": "招架 Parry",
         "text": "如果其他生物的近战攻击命中你时你正握着一把灵巧武器，则你可以执行反应来将你的熟练加值加入到你的护甲等级中，此举可能导致本次攻击变为未命中。那之后，直到你的下一回合开始前，你的AC在面对近战攻击时都将具有相同的加值。"},
    ],
}

_DUAL_WIELDER = {
    "name_zh": "双持客",
    "name_en": "Dual Wielder",
    "category": "通用",
    "prerequisite": "等级4+，力量或敏捷13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或敏捷提升1，至多提升至20。"},
        {"name": "强化双持 Enhanced Dual Wielding",
         "text": "当你在自己的回合中执行了攻击动作，并使用具有轻型词条的武器发动了一次攻击后，你可以在同一回合中，以一个附赠动作发动一次额外的攻击。这次额外的攻击必须由另一把不具有双手词条的近战武器发动。额外的攻击的伤害无法加入你的属性调整值（除非该调整值为负数）。"},
        {"name": "快速拔刀 Quick Draw",
         "text": "拔出或入鞘武器时，你可以同时拔出或入鞘两把不具有双手词条的武器，而非通常情况下的一把。"},
    ],
}

_DURABLE = {
    "name_zh": "耐性",
    "name_en": "Durable",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的体质提升1，至多提升至20。"},
        {"name": "悍不畏死 Defy Death",
         "text": "你进行的死亡豁免具有优势。"},
        {"name": "高速恢复 Speedy Recovery",
         "text": "以一个附赠动作，你可以消耗并投掷一枚生命骰，来恢复与投掷结果相等的生命值。"},
    ],
}

_ELEMENTAL_ADEPT = {
    "name_zh": "元素掌控",
    "name_en": "Elemental Adept",
    "category": "通用",
    "prerequisite": "等级4+，施法或契约魔法特性",
    "repeatable": True,
    "description": "你获得以下增益：复选：你可多次选取本专长，但每次选取时都必须为能量掌控增益选择一个不同的伤害类型。",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的智力、感知或魅力提升1点，至多提升至20。"},
        {"name": "能量掌控 Energy Mastery",
         "text": "选择以下伤害类型之一：强酸、寒冷、火焰、闪电、雷鸣。你施展的法术无视所选伤害类型的抗性。此外，当你为你施展的造成该类型伤害的法术投掷伤害时，你可以将伤害骰中骰出的1都视为2。"},
    ],
}

_FEY_TOUCHED = {
    "name_zh": "妖精触碰",
    "name_en": "Fey-Touched",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "暴露在妖精荒野 Feywild 的魔法之下给予你以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的智力、感知或魅力提升1，至多提升至20。"},
        {"name": "妖精魔法 Fey Magic",
         "text": "选择一道预言或惑控学派的一环法术。你始终准备着你选择的这道法术与迷踪步 Misty Step。你可以无需法术位地施展每道法术各一次，当你完成长休时，你重获以此法施展这些法术的能力。你也能够以你拥有的合适环阶的法术位施展这些法术。你这些法术的施法属性是你以此专长提升的属性。"},
    ],
}

_GRAPPLER = {
    "name_zh": "擒抱者",
    "name_en": "Grappler",
    "category": "通用",
    "prerequisite": "等级4+，力量或敏捷13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或敏捷提升1，至多提升至20。"},
        {"name": "连擒带打 Punch and Grab",
         "text": "你的回合中，当你用攻击动作中的一次徒手打击命中了一个生物，你可以同时进行擒抱和造成伤害两个选项。你每回合只能使用这个增益一次。"},
        {"name": "优势攻击 Attack Advantage",
         "text": "你攻击受擒于你的生物时进行的攻击检定具有优势。"},
        {"name": "高速拖行 Fast Wrestler",
         "text": "你无需为移动受擒于你的生物而花费额外的移动力，前提是这名生物的体型与你相同或更小。"},
    ],
}

_GREAT_WEAPON_MASTER = {
    "name_zh": "巨武器大师",
    "name_en": "Great Weapon Master",
    "category": "通用",
    "prerequisite": "等级4+，力量13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量提升1，至多提升至20。"},
        {"name": "重武器掌握 Heavy Weapon Master",
         "text": "在你的回合内，你的攻击动作中，当你用具有重型词条的武器命中了一名生物时，你可以让这把武器对目标额外造成一定的伤害，额外伤害等同于你的熟练加值。"},
        {"name": "顺势斩 Hew",
         "text": "当你使用近战武器掷出一次重击时，或当你用其将一个生物的生命值降低至0时，你可以立即使用你的附赠动作用同一把武器发动一次攻击。"},
    ],
}

_HEAVILY_ARMORED = {
    "name_zh": "重甲运用",
    "name_en": "Heavily Armored",
    "category": "通用",
    "prerequisite": "等级4+，中甲受训",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的体质或力量提升1，至多提升至20。"},
        {"name": "护甲受训 Armor Training",
         "text": "你获得重甲受训。"},
    ],
}

_HEAVY_ARMOR_MASTER = {
    "name_zh": "重甲大师",
    "name_en": "Heavy Armor Master",
    "category": "通用",
    "prerequisite": "等级4+，重甲受训",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的体质或力量提升1，至多提升至20。"},
        {"name": "伤害减免 Damage Reduction",
         "text": "穿着重甲期间，当你被一次攻击命中时，该次攻击对你造成的任何钝击伤害、穿刺伤害与挥砍伤害均减去你的熟练加值。"},
    ],
}

_INSPIRING_LEADER = {
    "name_zh": "领袖之证",
    "name_en": "Inspiring Leader",
    "category": "通用",
    "prerequisite": "等级4+，感知或魅力13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的感知或魅力提升1，至多提升至20。"},
        {"name": "激励演出 Bolstering Performance",
         "text": "每当你的短休/长休结束时，你可以做一场激励人心的表演：一次演讲、一首歌曲或一支舞蹈。当你这么做时，选择至多6名在周围30尺内观看你表演的盟友（亦可包括你自己）。每个被选中的生物都可以获得一定临时生命值，其数值等于你的角色等级+你用本专长提升的属性的调整值。"},
    ],
}

_KEEN_MIND = {
    "name_zh": "敏锐心灵",
    "name_en": "Keen Mind",
    "category": "通用",
    "prerequisite": "等级4+，智力13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的智力提升1，至多提升至20。"},
        {"name": "轶闻知识 Lore Knowledge",
         "text": "选择下列技能之一：奥秘、历史、调查、自然、宗教。如果你不具有所选技能的熟练，则你获得其熟练；如果你已有熟练，则你获得其专精。"},
        {"name": "快速研究 Quick Study",
         "text": "你可以用附赠动作执行研究动作。"},
    ],
}

_LIGHTLY_ARMORED = {
    "name_zh": "轻甲运用",
    "name_en": "Lightly Armored",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或敏捷提升1点，至多提升至20。"},
        {"name": "护甲受训 Armor Training",
         "text": "你获得轻甲和盾牌受训。"},
    ],
}

_MAGE_SLAYER = {
    "name_zh": "巫师杀手",
    "name_en": "Mage Slayer",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或敏捷提升1，至多提升至20。"},
        {"name": "专注中断手 Concentration Breaker",
         "text": "当你对一名正处于专注中的生物造成伤害时，该生物为维持本次专注所做的豁免检定时具有劣势。"},
        {"name": "审慎护心 Guarded Mind",
         "text": "当你的智力、感知或魅力豁免失败时，你可以将其改为成功。此增益一经使用，直到完成短休或长休前你都无法再次使用。"},
    ],
}

_MARTIAL_WEAPON_TRAINING = {
    "name_zh": "军用武器训练",
    "name_en": "Martial Weapon Training",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或敏捷提升1，至多提升至20。"},
        {"name": "武器熟练 Weapon Proficiency",
         "text": "你获得军用武器熟练。"},
    ],
}

_MEDIUM_ARMOR_MASTER = {
    "name_zh": "中甲大师",
    "name_en": "Medium Armor Master",
    "category": "通用",
    "prerequisite": "等级4+，中甲受训",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或敏捷提升1，至多提升至20。"},
        {"name": "灵敏着装 Dexterous Wearer",
         "text": "穿着中甲期间，若你的敏捷在16或更高，你可以在AC中加入3点敏捷调整值，而非原本的2点。"},
    ],
}

_MODERATELY_ARMORED = {
    "name_zh": "中甲运用",
    "name_en": "Moderately Armored",
    "category": "通用",
    "prerequisite": "等级4+，轻甲受训",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或敏捷提升1，至多提升至20。"},
        {"name": "护甲受训 Armor Training",
         "text": "你获得中甲受训。"},
    ],
}

_MOUNTED_COMBATANT = {
    "name_zh": "骑乘战斗",
    "name_en": "Mounted Combatant",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量、敏捷或感知提升1，至多提升至20。"},
        {"name": "骑乘突击 Mounted Strike",
         "text": "骑乘期间，你对位于你坐骑5尺内的、体型比你坐骑至少小一级的、且未被骑乘的生物所进行的攻击检定具有优势。"},
        {"name": "侧跃躲闪 Leap Aside",
         "text": "当你的坐骑受某效应影响而需要进行敏捷豁免时，如果此次豁免成功只受到一半伤害，那么它豁免成功时不受伤害，豁免失败只承受一半伤害。为享受此增益，你必须骑乘着你的坐骑，且你与坐骑均不能处于失能状态。"},
        {"name": "我身作盾 Veer",
         "text": "当你骑乘时，只要你不处于失能状态，你就可以强制让命中了你的坐骑的攻击改为命中你自己。"},
    ],
}

_OBSERVANT = {
    "name_zh": "观察力",
    "name_en": "Observant",
    "category": "通用",
    "prerequisite": "等级4+，智力或感知13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的智力或感知提升1，至多提升至20。"},
        {"name": "敏锐观察 Keen Observer",
         "text": "选择以下技能之一：洞悉、调查或察觉。如果你不具有所选技能的熟练，则你获得其熟练；如果你已有熟练，则你获得其专精。"},
        {"name": "快速搜索 Quick Search",
         "text": "你可以用附赠动作进行搜索动作。"},
    ],
}

_PIERCER = {
    "name_zh": "穿刺者",
    "name_en": "Piercer",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或敏捷提升1，至多提升至20。"},
        {"name": "穿透伤 Puncture",
         "text": "每回合一次，当你用造成穿刺伤害的攻击命中一个生物时，你可以重投这次攻击伤害的其中一枚伤害骰。但你必须采用新的掷骰结果。"},
        {"name": "强化重击 Enhanced Critical",
         "text": "当你用造成穿刺伤害的攻击命中一个生物并且掷出重击时，你可以在计算额外的穿刺伤害时多投一个伤害骰。"},
    ],
}

_POISONER = {
    "name_zh": "毒师",
    "name_en": "Poisoner",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的敏捷或智力提升1，至多提升至20。"},
        {"name": "强效毒素 Potent Poison",
         "text": "你造成毒素伤害的伤害掷骰无视对方的毒素伤害抗性。"},
        {"name": "酿毒 Brew Poison",
         "text": "你获得毒药工具的熟练。你可以花费一小时的时间与价值50GP的材料，来使用毒药工具制造一定数量的毒药，其剂数等同于你的熟练加值。你能够以一个附赠动作为一把武器或一枚弹药涂上一剂毒药。涂用后，此种毒药的毒性能维持一分钟，毒性也会在你用此涂毒物品造成伤害后会被消耗。当一名生物受到来自此种涂毒物品的伤害时，该生物必须成功通过一次体质豁免（DC等于8+你以本专长提升的属性的调整值+你的熟练加值），否则将受到2d8毒素伤害并陷入中毒状态，持续至你的下回合结束。"},
    ],
}

_POLEARM_MASTER = {
    "name_zh": "长柄武器大师",
    "name_en": "Polearm Master",
    "category": "通用",
    "prerequisite": "等级4+，力量或敏捷13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的敏捷或力量提升1，至多提升至20。"},
        {"name": "长柄打击 Pole Strike",
         "text": "在你执行攻击动作并使用长棍、矛或同时具有重型词条与触及词条的武器攻击后，你可以立刻用附赠动作，使用该武器的另一端发动一次近战攻击。在这次攻击中，该武器的伤害骰改为d4，其伤害类型改为钝击伤害。"},
        {"name": "反应打击 Reactive Strike",
         "text": "在你持握长棍、矛或同时具有重型词条与触及词条的武器期间，生物进入你触及范围时，你能够以反应，使用该武器对该生物发动一次近战攻击。"},
    ],
}

_RESILIENT = {
    "name_zh": "强健身心",
    "name_en": "Resilient",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "选择你不具有其豁免熟练的一项属性，该属性提升1，至多提升至20。"},
        {"name": "豁免熟练 Saving Throw Proficiency",
         "text": "你获得所选属性的豁免熟练。"},
    ],
}

_RITUAL_CASTER = {
    "name_zh": "仪式施法者",
    "name_en": "Ritual Caster",
    "category": "通用",
    "prerequisite": "等级4+，智力、感知或魅力13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的智力、感知或魅力提升1，至多提升至20。"},
        {"name": "仪式魔法 Ritual Spells",
         "text": "你选择数道具有仪式标签的一环法术，其具体数量等于你的熟练加值。你始终准备着这几道法术，并可以用你拥有的任何法术位去施展它们。施展它们的施法属性为你用此专长提升的属性。此后，每当你的熟练加值提升时，你可以通过这个特性多获得一道始终准备的、带有仪式标签的一环法术。"},
        {"name": "快速仪式 Quick Ritual",
         "text": "你可以用通常的施法时间来施展一道仪式法术，而不需要仪式的延长施法时间。这么做不会花费你的法术位。一旦你通过这种方式施展了一道法术，直到完成一次长休前你都不能再使用这个增益。"},
    ],
}

_SENTINEL = {
    "name_zh": "哨兵",
    "name_en": "Sentinel",
    "category": "通用",
    "prerequisite": "等级4+，力量或敏捷13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或敏捷提升1，至多提升至20。"},
        {"name": "守护者 Guardian",
         "text": "当位于你5尺范围内的生物执行撤离动作后，或当它的攻击命中了除你以外的目标后，你可以立刻对该生物进行一次借机攻击。"},
        {"name": "阻拦 Halt",
         "text": "你的借机攻击命中一名生物时，该生物的速度在当前回合剩余时间内变为0。"},
    ],
}

_SHADOW_TOUCHED = {
    "name_zh": "影界触碰",
    "name_en": "Shadow-Touched",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "暴露在堕影冥界 Shadowfell 的魔法之下给予你以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的智力、感知或魅力提升1，至多提升至20。"},
        {"name": "暗影魔法 Shadow Magic",
         "text": "选择一道幻术或死灵学派的一环法术。你始终准备着你选择的这道法术与隐形术 Invisibility。你可以无需法术位地施展每道法术各一次，当你完成长休时，你重获以此法施展这些法术的能力。你也能够以你拥有的合适环阶的法术位施展这些法术。这些法术的施法属性是你以此专长提升的属性。"},
    ],
}

_SHARPSHOOTER = {
    "name_zh": "神射手",
    "name_en": "Sharpshooter",
    "category": "通用",
    "prerequisite": "等级4+，敏捷13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的敏捷提升1，至多提升至20。"},
        {"name": "绕过掩体 Bypass Cover",
         "text": "你使用武器发动的远程攻击无视半身掩护和四分之三掩护。"},
        {"name": "抵近射击 Firing in Melee",
         "text": "位于一个敌人5尺范围内的情况下，你使用远程武器发动的攻击检定不会因此具有劣势。"},
        {"name": "百步穿杨 Long Shots",
         "text": "使用远程武器攻击超出常规射程的目标时，你的攻击检定不会因此具有劣势。"},
    ],
}

_SHIELD_MASTER = {
    "name_zh": "盾牌大师",
    "name_en": "Shield Master",
    "category": "通用",
    "prerequisite": "等级4+，盾牌受训",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量提升1，至多提升至20。"},
        {"name": "盾击 Shield Bash",
         "text": "当你通过攻击动作中的、由近战武器发动的一次攻击命中了位于你5尺内的生物时，如果你装备着盾牌，你就可以立即使用它来击打目标，迫使目标进行一次力量豁免检定（DC等于8+你的力量调整值+你的熟练加值）。如果豁免失败，目标将被你推离5尺远或因此陷入倒地状态（由你选择）。在每个你的回合中，此增益只能被使用一次。"},
        {"name": "介入盾牌 Interpose Shield",
         "text": "当你受某效应影响而需要进行敏捷豁免来只受一半伤害时，若你豁免检定成功并正持握着一面盾牌，你就可以用反应来使你自己免受此次伤害。"},
    ],
}

_SKILL_EXPERT = {
    "name_zh": "技艺专家",
    "name_en": "Skill Expert",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你选择的一项属性提升1，至多提升至20。"},
        {"name": "技能熟练 Skill Proficiency",
         "text": "你自选一个技能并获得其熟练。"},
        {"name": "专精 Expertise",
         "text": "你选择一个拥有其熟练但不具备相应专精的技能，并获得其专精。"},
    ],
}

_SKULKER = {
    "name_zh": "隐伏者",
    "name_en": "Skulker",
    "category": "通用",
    "prerequisite": "等级4+，敏捷13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的敏捷提升1，至多提升至20。"},
        {"name": "盲视 Blindsight",
         "text": "你获得10尺距离的盲视。"},
        {"name": "战争迷雾 Fog of War",
         "text": "你善于利用战斗中的混乱。你在战斗中通过执行躲藏动作时所做的任何敏捷（隐匿）检定都具有优势。"},
        {"name": "狙击手 Sniper",
         "text": "如果你在躲藏中进行了攻击检定，但该次攻击未命中时，这次攻击将不会暴露你的位置。"},
    ],
}

_SLASHER = {
    "name_zh": "劈砍者",
    "name_en": "Slasher",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或敏捷提升1，至多提升至20。"},
        {"name": "伤筋 Hamstring",
         "text": "每回合一次，当你用造成挥砍伤害的攻击命中一个生物时，你可以使其速度降低10尺，持续至你的下回合开始。"},
        {"name": "强化重击 Enhanced Critical",
         "text": "当你掷出重击并对一个生物造成挥砍伤害时，该生物进行的所有攻击检定都将具有劣势，持续至你的下回合开始为止。"},
    ],
}

_SPEEDY = {
    "name_zh": "飙速跑者",
    "name_en": "Speedy",
    "category": "通用",
    "prerequisite": "等级4+，敏捷或体质13+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的敏捷或体质提升1，至多提升至20。"},
        {"name": "速度提升 Speed Increase",
         "text": "你的速度提升10尺。"},
        {"name": "险地疾行 Dash Over Difficult Terrain",
         "text": "当你在自己的回合执行疾走动作时，在这个回合余下的时间里，困难地形不再会额外消耗你的移动力。"},
        {"name": "灵活移动 Agile Movement",
         "text": "对你发动的借机攻击都具有劣势。"},
    ],
}

_SPELL_SNIPER = {
    "name_zh": "法术射手",
    "name_en": "Spell Sniper",
    "category": "通用",
    "prerequisite": "等级4+，施法或契约魔法特性",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的智力、感知或魅力提升1，至多提升至20。"},
        {"name": "绕过掩体 Bypass Cover",
         "text": "你为法术进行的攻击检定无视半身掩护和四分之三掩护。"},
        {"name": "抵近施法 Casting in Melee",
         "text": "位于一个敌人5尺范围内的情况下，你用法术进行的攻击检定不会因此具有劣势。"},
        {"name": "法术增距 Increased Range",
         "text": "当你施展一道具有至少10尺施法距离，且需要你进行一次攻击检定的法术时，这道法术的施法距离增加60尺。"},
    ],
}

_TELEKINETIC = {
    "name_zh": "念动力",
    "name_en": "Telekinetic",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的智力、感知或魅力提升1，至多提升至20。"},
        {"name": "次级心灵遥控 Minor Telekinesis",
         "text": "你习得戏法法师之手 Mage Hand。你施展这道戏法时，你无需言语成分与姿势成分，且可以让这只灵体手隐形，还可以令它的施法距离以及其可远离你的最大距离均提升30尺。你该法术的施法属性是你以此专长提升的属性。"},
        {"name": "念力推撞 Telekinetic Shove",
         "text": "以一个附赠动作，你可以尝试以念动力推撞一个位于你30尺内的你可见的生物。当你这样做时，目标必须通过一次力量豁免（DC等于8+你用此专长提升的属性的调整值+你的熟练加值）否则将被你拉近或推离5尺。"},
    ],
}

_TELEPATHIC = {
    "name_zh": "心灵感应",
    "name_en": "Telepathic",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的智力、感知或魅力提升1，至多提升至20。"},
        {"name": "传心呢喃 Telepathic Utterance",
         "text": "你可以和位于你60尺内任何你可见的生物用心灵感应进行交流。你的传心呢喃以一种你已知的语言进行，且该生物必须懂得这门语言才能理解你。你的主动沟通并不会给予该生物以心灵感应的形式回复你的能力。"},
        {"name": "侦测思想 Detect Thoughts",
         "text": "你始终准备着法术侦测思想 Detect Thoughts。你可以无需法术位且无需法术成分地施展该法术。当你完成长休时，你重获以此法施展该法术的能力。你也能够以你拥有的合适环阶的法术位施展该法术。你这些法术的施法属性是你以此专长提升的属性。"},
    ],
}

_WAR_CASTER = {
    "name_zh": "战地施法者",
    "name_en": "War Caster",
    "category": "通用",
    "prerequisite": "等级4+，施法或契约魔法特性",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的智力、感知或魅力提升1，至多提升至20。"},
        {"name": "专注 Concentration",
         "text": "你为维持专注的所做的体质豁免具有优势。"},
        {"name": "响应法术 Reactive Spell",
         "text": "当一个生物因离开你的触及范围而引发你的借机攻击时，你能使用你的反应来对这个生物施展一道法术，而非发动一次借机攻击。这道法术的施法时间必须为动作，且必须将该生物选为法术的唯一目标。"},
        {"name": "姿势成分 Somatic Components",
         "text": "即使你的一只手或双手上都有武器/盾牌，你也能满足法术的姿势成分要求。"},
    ],
}

_WEAPON_MASTER = {
    "name_zh": "武器大师",
    "name_en": "Weapon Master",
    "category": "通用",
    "prerequisite": "等级4+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或敏捷提升1，至多提升至20。"},
        {"name": "精通词条 Mastery Property",
         "text": "你对武器的训练让你能够使用你自选的一种简单或军用武器的精通词条，前提是你熟练于该种武器。每当你完成一次长休，你能将所选的武器种类替换为你熟练的另一种武器。"},
    ],
}

# ──────────────────────────────────────────────────────────────────────────
# 传奇恩惠专长 Epic Boon Feats — 出处: 传奇恩惠专长.htm
# 先决均为「等级19+」
# ──────────────────────────────────────────────────────────────────────────

_BOON_COMBAT_PROWESS = {
    "name_zh": "英勇战斗之恩惠",
    "name_en": "Boon of Combat Prowess",
    "category": "传奇恩惠",
    "prerequisite": "等级19+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你选择的一项属性提升1，至多提升至30。"},
        {"name": "无双锁定 Peerless Aim",
         "text": "当你的一次攻击检定失手时，你可以将其改为命中。该增益一经使用，下个你的回合开始后你才能再次使用它。"},
    ],
}

_BOON_DIMENSIONAL_TRAVEL = {
    "name_zh": "次元旅行之恩惠",
    "name_en": "Boon of Dimensional Travel",
    "category": "传奇恩惠",
    "prerequisite": "等级19+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你选择的一项属性提升1，至多提升至30。"},
        {"name": "闪烁步 Blink Steps",
         "text": "当你执行攻击动作或魔法动作后，你可以立即传送至多30尺的距离到一处你可见的未占据空间内。"},
    ],
}

_BOON_ENERGY_RESISTANCE = {
    "name_zh": "能量抗性之恩惠",
    "name_en": "Boon of Energy Resistance",
    "category": "传奇恩惠",
    "prerequisite": "等级19+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你选择的一项属性提升1，至多提升至30。"},
        {"name": "能量抗性 Energy Resistances",
         "text": "从下列伤害类型中选择两种：强酸、寒冷、火焰、闪电、暗蚀、毒素、心灵、光耀或雷鸣。你获得所选伤害类型的抗性。每当你完成长休时，你都可以改变此处选择的伤害类型。"},
        {"name": "能量重导 Energy Redirection",
         "text": "当你受到伤害时，若该伤害的伤害类型是你能量抗性增益中所选类型之一，你能够以反应来将一次相同类型的伤害传导给你60尺内的、可见的另一名生物（不能是对你而言处于全身掩护下的生物）。若你如此做，该生物必须通过一次敏捷豁免（DC等于8+你的体质调整值+你的熟练加值），否则其受到2d12+你的体质调整值伤害。"},
    ],
}

_BOON_FATE = {
    "name_zh": "扭曲命运之恩惠",
    "name_en": "Boon of Fate",
    "category": "传奇恩惠",
    "prerequisite": "等级19+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你选择的一项属性提升1，至多提升至30。"},
        {"name": "时来运转 Improve Fate",
         "text": "当你或位于你60尺内的另一名生物的D20检定中成功时或失败时，你可以投掷2d4，并将掷骰结果作为加值或减值附加到d20掷骰中。该增益一经使用，直至你投掷先攻、完成短休或完成长休你都无法再次使用。"},
    ],
}

_BOON_FORTITUDE = {
    "name_zh": "超凡强韧之恩惠",
    "name_en": "Boon of Fortitude",
    "category": "传奇恩惠",
    "prerequisite": "等级19+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你选择的一项属性提升1，至多提升至30。"},
        {"name": "身强体壮 Fortified Health",
         "text": "你的生命值上限增加40。此外，每当你恢复生命值时，你可以恢复等于你体质调整值的额外生命值。以此恢复了额外生命值后，直至下个你的回合开始后你才能再次受益于此效果。"},
    ],
}

_BOON_IRRESISTIBLE_OFFENSE = {
    "name_zh": "无敌攻势之恩惠",
    "name_en": "Boon of Irresistible Offense",
    "category": "传奇恩惠",
    "prerequisite": "等级19+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的力量或敏捷提升1，至多提升至30。"},
        {"name": "摧坚破甲 Overcome Defenses",
         "text": "你造成的钝击、挥砍与穿刺伤害始终无视抗性。"},
        {"name": "无阻打击 Overwhelming Strike",
         "text": "当你为一次攻击检定投掷的d20骰出了20时，你可以对目标造成额外伤害，你造成的额外伤害等于你以此专长提升的属性的属性值，伤害类型与这次攻击的伤害类型相同。"},
    ],
}

_BOON_RECOVERY = {
    "name_zh": "强力恢复之恩惠",
    "name_en": "Boon of Recovery",
    "category": "传奇恩惠",
    "prerequisite": "等级19+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你选择的一项属性提升1，至多提升至30。"},
        {"name": "背水一战 Last Stand",
         "text": "当你的生命值将要降至0时，你可以改为降至1并恢复等于你生命值上限一半的生命值。该增益一经使用，直到完成长休你都无法再次被使用。"},
        {"name": "重获生机 Recover Vitality",
         "text": "你获得一个有着十枚d10的治疗池。以一个附赠动作，你可以消耗治疗池中任意枚骰子来恢复你的生命值。投掷全部你消耗的骰子，将掷骰结果相加，即是你以此恢复的生命值。当你完成长休时，你的治疗池重获所有被消耗的骰子。"},
    ],
}

_BOON_SKILL = {
    "name_zh": "博学多才之恩惠",
    "name_en": "Boon of Skill",
    "category": "传奇恩惠",
    "prerequisite": "等级19+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你选择的一项属性提升1，至多提升至30。"},
        {"name": "全能专家 All-Around Adept",
         "text": "你获得所有技能的熟练。"},
        {"name": "专精 Expertise",
         "text": "选择一项你不具有专精的技能，你获得该技能的专精。"},
    ],
}

_BOON_SPEED = {
    "name_zh": "神行无拘之恩惠",
    "name_en": "Boon of Speed",
    "category": "传奇恩惠",
    "prerequisite": "等级19+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你选择的一项属性提升1，至多提升至30。"},
        {"name": "逃脱大师 Escape Artist",
         "text": "你能够以一个附赠动作执行撤离动作，并结束你陷入的受擒状态。"},
        {"name": "风驰电掣 Quickness",
         "text": "你的速度提升30尺。"},
    ],
}

_BOON_SPELL_RECALL = {
    "name_zh": "法术溯回之恩惠",
    "name_en": "Boon of Spell Recall",
    "category": "传奇恩惠",
    "prerequisite": "等级19+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你的智力、感知或魅力提升1，至多提升至30。"},
        {"name": "免费施法 Free Casting",
         "text": "每当你使用一环到四环的法术位施展法术时，投掷1d4。若掷骰结果与你消耗的法术位环阶一致，则该法术位不会被消耗。"},
    ],
}

_BOON_NIGHT_SPIRIT = {
    "name_zh": "暗夜精魂之恩惠",
    "name_en": "Boon of the Night Spirit",
    "category": "传奇恩惠",
    "prerequisite": "等级19+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你选择的一项属性提升1，至多提升至30。"},
        {"name": "融身入影 Merge with Shadows",
         "text": "身处微光光照或黑暗期间，你可以用附赠动作令你获得隐形状态。隐形状态将在你执行动作/附赠动作/反应后立即结束。"},
        {"name": "幽影化身 Shadowy Form",
         "text": "身处微光光照或黑暗期间，你具有除心灵和光耀伤害外所有伤害的抗性。"},
    ],
}

_BOON_TRUESIGHT = {
    "name_zh": "真实视觉之恩惠",
    "name_en": "Boon of Truesight",
    "category": "传奇恩惠",
    "prerequisite": "等级19+",
    "repeatable": False,
    "description": "你获得以下增益：",
    "effects": [
        {"name": "属性值提升 Ability Score Increase",
         "text": "你选择的一项属性提升1，至多提升至30。"},
        {"name": "真实视觉 Truesight",
         "text": "你获得60尺真实视觉。"},
    ],
}


# ──────────────────────────────────────────────────────────────────────────
# 汇总表 — 按 专长概述.htm 的「专长列表」顺序排列
# ──────────────────────────────────────────────────────────────────────────

FEATS: list[dict] = [
    # 起源专长（10）
    _ALERT, _CRAFTER, _HEALER, _LUCKY, _MAGIC_INITIATE,
    _MUSICIAN, _SAVAGE_ATTACKER, _SKILLED, _TAVERN_BRAWLER, _TOUGH,
    # 通用专长
    _ASI, _ACTOR, _ATHLETE, _CHARGER, _CHEF, _CROSSBOW_EXPERT,
    _CRUSHER, _DEFENSIVE_DUELIST, _DUAL_WIELDER, _DURABLE,
    _ELEMENTAL_ADEPT, _FEY_TOUCHED, _GRAPPLER, _GREAT_WEAPON_MASTER,
    _HEAVILY_ARMORED, _HEAVY_ARMOR_MASTER, _INSPIRING_LEADER, _KEEN_MIND,
    _LIGHTLY_ARMORED, _MAGE_SLAYER, _MARTIAL_WEAPON_TRAINING,
    _MEDIUM_ARMOR_MASTER, _MODERATELY_ARMORED, _MOUNTED_COMBATANT,
    _OBSERVANT, _PIERCER, _POISONER, _POLEARM_MASTER, _RESILIENT,
    _RITUAL_CASTER, _SENTINEL, _SHADOW_TOUCHED, _SHARPSHOOTER,
    _SHIELD_MASTER, _SKILL_EXPERT, _SKULKER, _SLASHER, _SPEEDY,
    _SPELL_SNIPER, _TELEKINETIC, _TELEPATHIC, _WAR_CASTER, _WEAPON_MASTER,
    # 战斗风格专长（9）
    _ARCHERY, _BLIND_FIGHTING, _DEFENSE, _DUELING, _GREAT_WEAPON_FIGHTING,
    _INTERCEPTION, _PROTECTION, _THROWN_WEAPON_FIGHTING, _TWO_WEAPON_FIGHTING,
    # 传奇恩惠专长（12）
    _BOON_COMBAT_PROWESS, _BOON_DIMENSIONAL_TRAVEL, _BOON_ENERGY_RESISTANCE,
    _BOON_FATE, _BOON_FORTITUDE, _BOON_IRRESISTIBLE_OFFENSE, _BOON_RECOVERY,
    _BOON_SKILL, _BOON_SPEED, _BOON_SPELL_RECALL, _BOON_NIGHT_SPIRIT,
    _BOON_TRUESIGHT,
]

# 按中文名索引，便于 O(1) 查找
FEATS_BY_NAME: dict[str, dict] = {f["name_zh"]: f for f in FEATS}


def list_feats(category: str | None = None) -> list[dict]:
    """返回专长列表。

    Args:
        category: 可选分类过滤。取值: 起源 / 通用 / 战斗风格 / 传奇恩惠。
                  传 None 返回全部。

    Returns:
        专长字典列表（浅拷贝，调用方可安全修改）。
    """
    if category is None:
        return [dict(f) for f in FEATS]
    return [dict(f) for f in FEATS if f["category"] == category]


def get_feat(name_zh: str) -> dict | None:
    """按中文名取专长条目。不存在返回 None。"""
    f = FEATS_BY_NAME.get(name_zh)
    return dict(f) if f else None


def feat_categories() -> list[str]:
    """返回专长分类列表（按出现顺序去重）。"""
    seen: list[str] = []
    for f in FEATS:
        if f["category"] not in seen:
            seen.append(f["category"])
    return seen


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 分类计数（出处: 专长概述.htm 专长列表）
    cats = {f["category"] for f in FEATS}
    assert cats == {"起源", "通用", "战斗风格", "传奇恩惠"}, f"分类异常: {cats}"

    by_cat: dict[str, int] = {}
    for f in FEATS:
        by_cat[f["category"]] = by_cat.get(f["category"], 0) + 1
    # 起源 10 / 战斗风格 9 / 传奇恩惠 12
    assert by_cat["起源"] == 10, f"起源专长应有10个，实有{by_cat['起源']}"
    assert by_cat["战斗风格"] == 9, f"战斗风格专长应有9个，实有{by_cat['战斗风格']}"
    assert by_cat["传奇恩惠"] == 12, f"传奇恩惠专长应有12个，实有{by_cat['传奇恩惠']}"
    # 通用专长：专长列表中通用分类条目数
    # 列表: ASI, Actor, Athlete, Charger, Chef, CrossbowExpert, Crusher,
    #       DefensiveDuelist, DualWielder, Durable, ElementalAdept, FeyTouched,
    #       Grappler, GreatWeaponMaster, HeavilyArmored, HeavyArmorMaster,
    #       InspiringLeader, KeenMind, LightlyArmored, MageSlayer,
    #       MartialWeaponTraining, MediumArmorMaster, ModeratelyArmored,
    #       MountedCombatant, Observant, Piercer, Poisoner, PolearmMaster,
    #       Resilient, RitualCaster, Sentinel, ShadowTouched, Sharpshooter,
    #       ShieldMaster, SkillExpert, Skulker, Slasher, Speedy, SpellSniper,
    #       Telekinetic, Telepathic, WarCaster, WeaponMaster = 44
    assert by_cat["通用"] == 43, f"通用专长应有43个，实有{by_cat['通用']}"

    # 中文名唯一
    names = [f["name_zh"] for f in FEATS]
    assert len(names) == len(set(names)), "存在重复中文名"

    # 每条必有完整字段
    required = {"name_zh", "name_en", "category", "prerequisite",
                "repeatable", "description", "effects"}
    for f in FEATS:
        missing = required - set(f.keys())
        assert not missing, f"{f['name_zh']} 缺字段 {missing}"
        assert isinstance(f["effects"], list), f"{f['name_zh']} effects 非列表"

    # 抽查关键条目（出处: 各专长 .htm）
    alert = get_feat("警戒")
    assert alert is not None and alert["category"] == "起源"
    assert alert["effects"][0]["name"].startswith("先攻熟练")

    tough = get_feat("健壮")
    assert tough is not None and tough["category"] == "起源"
    assert tough["effects"] == []  # 健壮无分项增益，整体描述

    gwm = get_feat("巨武器大师")
    assert gwm is not None and gwm["prerequisite"] == "等级4+，力量13+"
    assert any(e["name"].startswith("重武器掌握") for e in gwm["effects"])

    boon = get_feat("超凡强韧之恩惠")
    assert boon is not None and boon["category"] == "传奇恩惠"
    assert boon["prerequisite"] == "等级19+"

    archery = get_feat("箭术")
    assert archery is not None and archery["category"] == "战斗风格"
    assert archery["prerequisite"] == "战斗风格特性"

    # 复选标志抽查
    assert get_feat("魔法学徒")["repeatable"] is True
    assert get_feat("元素掌控")["repeatable"] is True
    assert get_feat("熟习")["repeatable"] is True
    assert get_feat("属性值提升")["repeatable"] is True
    # 非复选
    assert get_feat("警戒")["repeatable"] is False

    # 分类过滤
    origin = list_feats("起源")
    assert len(origin) == 10
    all_feats = list_feats()
    assert len(all_feats) == len(FEATS)

    print(f"[feats] 自检通过 ✓ 共 {len(FEATS)} 个专长 "
          f"(起源{by_cat['起源']}/通用{by_cat['通用']}/"
          f"战斗风格{by_cat['战斗风格']}/传奇恩惠{by_cat['传奇恩惠']})")


if __name__ == "__main__":
    _self_test()
