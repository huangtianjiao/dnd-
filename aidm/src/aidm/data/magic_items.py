"""魔法物品数据库 — DMG 第七章 宝藏。

规则依据: 城主指南2024/7.宝藏/魔法物品/
  - 魔法物品的稀有度.htm   稀有度与价格表
  - 魔法物品的类别.htm     9大类别（护甲/药水/戒指/权杖/卷轴/法杖/魔杖/武器/奇物）
  - 魔法物品详述/         按类别+稀有度组织的详细物品列表

本模块提供:
  - Rarity 枚举: COMMON / UNCOMMON / RARE / VERY_RARE / LEGENDARY / ARTIFACT
  - ItemType 枚举: WEAPON / ARMOR / WONDROUS_ITEM / RING / SCROLL / POTION / STAFF / ROD / WAND
  - MagicItem dataclass: name, rarity, type, attunement, cursed, description, properties
  - MAGIC_ITEMS 字典: 20+ 常见魔法物品，数据从 HTML 原文提取
  - 查询函数: get_magic_item / list_magic_items / items_by_rarity / items_by_type
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────

class Rarity(Enum):
    """魔法物品稀有度。

    出处: 城主指南2024/7.宝藏/魔法物品/魔法物品的稀有度.htm
    价格表: 普通100gp / 非普通400gp / 珍稀4000gp / 极珍稀40000gp / 传说200000gp / 神器无价之宝
    """
    COMMON = "普通"
    UNCOMMON = "非普通"
    RARE = "珍稀"
    VERY_RARE = "极珍稀"
    LEGENDARY = "传说"
    ARTIFACT = "神器"

    @property
    def base_price_gp(self) -> int:
        """该稀有度的基础价格（GP）。消耗品减半（卷轴除外）。

        规则: 魔法物品稀有度与价格表
        """
        return {
            Rarity.COMMON: 100,
            Rarity.UNCOMMON: 400,
            Rarity.RARE: 4000,
            Rarity.VERY_RARE: 40000,
            Rarity.LEGENDARY: 200000,
            Rarity.ARTIFACT: 0,  # 无价之宝
        }[self]

    @property
    def sort_order(self) -> int:
        """稀有度排序权重（普通最低，神器最高）。"""
        return {
            Rarity.COMMON: 0,
            Rarity.UNCOMMON: 1,
            Rarity.RARE: 2,
            Rarity.VERY_RARE: 3,
            Rarity.LEGENDARY: 4,
            Rarity.ARTIFACT: 5,
        }[self]


class ItemType(Enum):
    """魔法物品类别（9大类）。

    出处: 城主指南2024/7.宝藏/魔法物品/魔法物品的类别.htm
    """
    WEAPON = "武器"
    ARMOR = "护甲"
    WONDROUS_ITEM = "奇物"
    RING = "戒指"
    SCROLL = "卷轴"
    POTION = "药水"
    STAFF = "法杖"
    ROD = "权杖"
    WAND = "魔杖"


# ──────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class MagicItem:
    """单个魔法物品的数据条目。

    Attributes:
        name: 物品名称（中文）
        name_en: 英文名称
        rarity: 稀有度枚举
        item_type: 类别枚举
        attunement: 是否需要同调
        attunement_req: 同调先决条件描述（如"需法师同调"），无则为空字符串
        cursed: 是否为诅咒物品
        description: 物品效果描述（从HTML原文提取并清洗）
        properties: 额外属性字典（如 weapon_type, charges, price_override 等）
        source: 规则出处（HTML文件路径）

    规则依据: 城主指南2024/7.宝藏/魔法物品/
    """
    name: str
    name_en: str
    rarity: Rarity
    item_type: ItemType
    attunement: bool = False
    attunement_req: str = ""
    cursed: bool = False
    description: str = ""
    properties: dict = field(default_factory=dict)
    source: str = ""

    @property
    def price_gp(self) -> int:
        """该物品的建议售价（GP）。

        规则: 魔法物品稀有度与价格表
          - 消耗品（药水/卷轴/弹药等）价格减半，但法术卷轴按抄写成本两倍计
          - 若内含PHB物品（如武器/护甲），加上该基础物品价格
        """
        if "price_override" in self.properties:
            return self.properties["price_override"]
        base = self.rarity.base_price_gp
        consumable = self.item_type in (ItemType.POTION, ItemType.SCROLL) or \
                     self.properties.get("consumable", False)
        if consumable:
            base = base // 2
        # 加上内含基础物品价格（如+1护甲(板甲)=4000+1500）
        base_item_price = self.properties.get("base_item_price_gp", 0)
        return base + base_item_price

    def to_dict(self) -> dict:
        """序列化为可JSON化的字典。"""
        return {
            "name": self.name,
            "name_en": self.name_en,
            "rarity": self.rarity.value,
            "rarity_key": self.rarity.name,
            "item_type": self.item_type.value,
            "item_type_key": self.item_type.name,
            "attunement": self.attunement,
            "attunement_req": self.attunement_req,
            "cursed": self.cursed,
            "description": self.description,
            "properties": self.properties,
            "price_gp": self.price_gp,
            "source": self.source,
        }


# ──────────────────────────────────────────────────────────────────────────
# 魔法物品数据库
# 数据来源: 城主指南2024/7.宝藏/魔法物品详述/ 下各HTML文件
# ──────────────────────────────────────────────────────────────────────────

_SRC = "城主指南2024/7.宝藏/魔法物品详述/"

_MAGIC_ITEMS_LIST: list[MagicItem] = [
    # ═══════════ 武器 ═══════════
    MagicItem(
        name="触月剑", name_en="Moon-Touched Sword",
        rarity=Rarity.COMMON, item_type=ItemType.WEAPON,
        description="在黑暗中，这把剑出鞘的刃锋将泄出月光，创造半径15尺的明亮光照以及其外15尺的微光光照。",
        properties={"weapon_type": "长柄刀、巨剑、长剑、刺剑、弯刀、短剑"},
        source=_SRC + "武器/普通.htm",
    ),
    MagicItem(
        name="镀银武器", name_en="Silvered Weapon",
        rarity=Rarity.COMMON, item_type=ItemType.WEAPON,
        description="这件魔法武器使用炼金工艺镀上了一层银。当你用该武器对一个变形的生物造成一次重击时，该武器令该次伤害在计算时额外掷一颗骰子。",
        properties={"weapon_type": "任意简易武器或军用武器"},
        source=_SRC + "武器/普通.htm",
    ),
    MagicItem(
        name="冲击弹", name_en="Walloping Ammunition",
        rarity=Rarity.COMMON, item_type=ItemType.WEAPON,
        description="任何被这枚弹药命中的生物都必须成功通过一次DC10的力量豁免，豁免失败则会陷入倒地状态。",
        properties={"weapon_type": "任意弹药", "consumable": True},
        source=_SRC + "武器/普通.htm",
    ),
    MagicItem(
        name="精金武器", name_en="Adamantine Weapon",
        rarity=Rarity.UNCOMMON, item_type=ItemType.WEAPON,
        description="构成这把武器或这枚弹药的材料乃是精金——世界上最坚硬的物质。每当这把武器或这枚弹药命中物件时，其命中均为重击命中。",
        properties={"weapon_type": "任意弹药或近战武器"},
        source=_SRC + "武器/非普通.htm",
    ),
    MagicItem(
        name="闪电标枪", name_en="Javelin of Lightning",
        rarity=Rarity.UNCOMMON, item_type=ItemType.WEAPON,
        description="当你用该武器发动的攻击检定命中时，你可以选择令其造成闪电伤害而非穿刺伤害。闪电束：当你向至多120尺内的一个目标投掷该武器时，你可以选择不进行远程攻击检定，而是将该武器变为一道闪电束，形成5尺线状区域，目标及区域内每个生物须进行DC13敏捷豁免，失败受4d6闪电伤害，成功减半。该武器会在造成伤害后立即回到你手中。直到次日黎明前无法再次使用。",
        properties={"weapon_type": "标枪", "charges": 1, "recharge": "每日黎明"},
        source=_SRC + "武器/非普通.htm",
    ),
    MagicItem(
        name="复仇之剑", name_en="Sword of Vengeance",
        rarity=Rarity.UNCOMMON, item_type=ItemType.WEAPON,
        attunement=True, cursed=True,
        description="你用此魔法武器进行的攻击检定和伤害掷骰获得+1加值。诅咒：这把武器被寄宿在武器内的一道渴望复仇的魂灵所诅咒。只要诅咒还在生效，你总是会把剑带在身上，不愿与它分开。你在用其他武器进行的攻击检定和伤害掷骰具有劣势。每当你在战斗中受到其他生物造成的伤害时，你必须成功通过一次DC15感知豁免，否则必须持续攻击对你造成伤害的生物。",
        properties={"weapon_type": "长柄刀、巨剑、长剑、刺剑、弯刀、短剑", "attack_bonus": 1},
        source=_SRC + "武器/非普通.htm",
    ),
    MagicItem(
        name="警戒武器", name_en="Weapon of Warning",
        rarity=Rarity.UNCOMMON, item_type=ItemType.WEAPON,
        attunement=True,
        description="在同调该武器后，只要这把武器在你的触及范围内，你和你30尺内的盟友便获得以下增益。警报：这把武器能魔法性地在战斗开始时唤醒处于自然睡眠中的受益者。超然备战：每名受益者在投掷先攻时都具有优势。",
        properties={"weapon_type": "任意简易武器或军用武器"},
        source=_SRC + "武器/非普通.htm",
    ),

    # ═══════════ 护甲 ═══════════
    MagicItem(
        name="闪烁甲", name_en="Armor of Gleaming",
        rarity=Rarity.COMMON, item_type=ItemType.ARMOR,
        description="这件护甲永远不会脏。",
        properties={"armor_type": "任意轻甲、中甲或重甲"},
        source=_SRC + "护甲/普通.htm",
    ),
    MagicItem(
        name="速脱甲", name_en="Cast-Off Armor",
        rarity=Rarity.COMMON, item_type=ItemType.ARMOR,
        description="你只用一个魔法动作便可脱下这套护甲。",
        properties={"armor_type": "任意轻甲、中甲或重甲"},
        source=_SRC + "护甲/普通.htm",
    ),
    MagicItem(
        name="表情盾", name_en="Shield of Expression",
        rarity=Rarity.COMMON, item_type=ItemType.ARMOR,
        description="这面盾牌的正面呈现出一张脸的形状。携带这面盾牌期间，你可以使用一个附赠动作来改变这张脸的表情。",
        properties={"armor_type": "盾牌"},
        source=_SRC + "护甲/普通.htm",
    ),
    MagicItem(
        name="焖燃护甲", name_en="Smoldering Armor",
        rarity=Rarity.COMMON, item_type=ItemType.ARMOR,
        description="这件护甲被着装期间，一缕缕无害无味的烟雾会不断从护甲中升起。",
        properties={"armor_type": "任意重甲、中甲或轻甲"},
        source=_SRC + "护甲/普通.htm",
    ),

    # ═══════════ 药水 ═══════════
    MagicItem(
        name="治疗药水", name_en="Potion of Healing",
        rarity=Rarity.COMMON, item_type=ItemType.POTION,
        description="当你饮下这瓶药水时，你恢复2d4+2点生命值。无论饮用还是喷洒，这瓶药水的红色液体都会微微发光。",
        properties={"consumable": True, "heal_dice": "2d4+2"},
        source=_SRC + "药水/普通.htm",
    ),
    MagicItem(
        name="高级治疗药水", name_en="Potion of Greater Healing",
        rarity=Rarity.UNCOMMON, item_type=ItemType.POTION,
        description="当你饮下这瓶药水时，你恢复4d4+4点生命值。",
        properties={"consumable": True, "heal_dice": "4d4+4"},
        source=_SRC + "药水/非普通.htm",
    ),
    MagicItem(
        name="攀爬药水", name_en="Potion of Climbing",
        rarity=Rarity.COMMON, item_type=ItemType.POTION,
        description="当你饮下这瓶药水时，你获得等同于你速度的攀爬速度，持续1小时。这段时间内，你在为攀爬进行的力量（运动）检定中具有优势。这瓶药水会分离成类似岩层的褐、银、灰三层颜色。",
        properties={"consumable": True, "duration": "1小时"},
        source=_SRC + "药水/普通.htm",
    ),
    MagicItem(
        name="通晓药水", name_en="Potion of Comprehension",
        rarity=Rarity.COMMON, item_type=ItemType.POTION,
        description="当你饮下这瓶药水时，你获得法术通晓语言的效应，持续1小时。这瓶药水的药液是透明的调配物，一些盐粒和烟尘在里面旋转。",
        properties={"consumable": True, "duration": "1小时", "grants_spell": "通晓语言"},
        source=_SRC + "药水/普通.htm",
    ),
    MagicItem(
        name="健康灵药", name_en="Elixir of Health",
        rarity=Rarity.RARE, item_type=ItemType.POTION,
        description="当你饮下这瓶药水时，你身上的所有魔法性疫病都会被治愈。此外，你身上的目盲、耳聋、麻痹与中毒状态都会结束。这瓶清澈的红色液体中有着发光的微小气泡。",
        properties={"consumable": True, "cures_conditions": ["目盲", "耳聋", "麻痹", "中毒"]},
        source=_SRC + "药水/珍稀.htm",
    ),
    MagicItem(
        name="隐身药水", name_en="Potion of Invisibility",
        rarity=Rarity.RARE, item_type=ItemType.POTION,
        description="这瓶药水的容器看上去像是空的，但感觉上像是装着药液。当你饮下这瓶药水时，你获得隐形状态，持续1小时。效应将在你进行攻击检定、造成伤害或施展法术时提前结束。",
        properties={"consumable": True, "duration": "1小时", "grants_condition": "隐形"},
        source=_SRC + "药水/珍稀.htm",
    ),
    MagicItem(
        name="英勇药水", name_en="Potion of Heroism",
        rarity=Rarity.RARE, item_type=ItemType.POTION,
        description="当你饮下这瓶药水时，你获得10临时生命值，持续1小时。在相同持续时间内，你将受到法术祝福术的效应影响（无需专注）。这瓶药水的蓝色药液如同沸腾一般冒着气泡与蒸汽。",
        properties={"consumable": True, "duration": "1小时", "temp_hp": 10, "grants_spell": "祝福术"},
        source=_SRC + "药水/珍稀.htm",
    ),

    # ═══════════ 戒指 ═══════════
    MagicItem(
        name="跳跃戒指", name_en="Ring of Jumping",
        rarity=Rarity.UNCOMMON, item_type=ItemType.RING,
        attunement=True,
        description="着装此戒指期间，你可以从中施展跳跃术，但只能以自身为目标。",
        properties={"grants_spell": "跳跃术", "spell_target": "仅自身"},
        source=_SRC + "戒指/非普通.htm",
    ),
    MagicItem(
        name="心灵护盾戒指", name_en="Ring of Mind Shielding",
        rarity=Rarity.UNCOMMON, item_type=ItemType.RING,
        attunement=True,
        description="着装此戒指期间，你免疫能让其他生物阅读你的思想、辨别你在说谎、知晓你阵营或生物类型的魔法。只有在你允许时，生物才能与你进行心灵感应交流。你可以执行魔法动作让戒指变得无法被察觉。如果你在着装戒指期间死亡，你的灵魂将进入戒指中。",
        properties={"immunities": ["思想读取", "谎言辨别", "阵营探知", "生物类型探知"]},
        source=_SRC + "戒指/非普通.htm",
    ),
    MagicItem(
        name="善泳戒指", name_en="Ring of Swimming",
        rarity=Rarity.UNCOMMON, item_type=ItemType.RING,
        attunement=False,
        description="着装此戒指期间，你获得40尺游泳速度。",
        properties={"swim_speed": 40},
        source=_SRC + "戒指/非普通.htm",
    ),
    MagicItem(
        name="温暖戒指", name_en="Ring of Warmth",
        rarity=Rarity.UNCOMMON, item_type=ItemType.RING,
        attunement=True,
        description="着装此戒指期间，当你受到寒冷伤害时，戒指将你所受的伤害减少2d8。此外，你以及你着装和携带的任何东西都不会被0华氏度及以下的温度所伤害。",
        properties={"cold_resistance_dice": "2d8", "cold_immunity_threshold_f": 0},
        source=_SRC + "戒指/非普通.htm",
    ),
    MagicItem(
        name="水上行走戒指", name_en="Ring of Water Walking",
        rarity=Rarity.UNCOMMON, item_type=ItemType.RING,
        attunement=False,
        description="着装此戒指期间，你可以从中施展水上行走，但目标只能为自身。",
        properties={"grants_spell": "水上行走", "spell_target": "仅自身"},
        source=_SRC + "戒指/非普通.htm",
    ),

    # ═══════════ 法杖 ═══════════
    MagicItem(
        name="蝰蛇法杖", name_en="Staff of the Adder",
        rarity=Rarity.UNCOMMON, item_type=ItemType.STAFF,
        attunement=True,
        description="以一个附赠动作，你可以将法杖的头部变为一条会动的毒蛇，持续一分钟，或直至你执行附赠动作将法杖还原。当你执行攻击动作时，你可以使用触及5尺的活化蛇头来发动其中一次攻击检定。这次攻击检定使用你的熟练加值与感知调整值。命中时，目标将受到1d6穿刺伤害与3d6毒素伤害。蛇头在活化期间可以被攻击，具有AC15，HP20，免疫毒素与心灵伤害。蛇头的生命值降为0时法杖将被摧毁。",
        properties={"snake_head_ac": 15, "snake_head_hp": 20, "damage": "1d6穿刺+3d6毒素"},
        source=_SRC + "法杖/非普通.htm",
    ),
    MagicItem(
        name="蟒蛇法杖", name_en="Staff of the Python",
        rarity=Rarity.UNCOMMON, item_type=ItemType.STAFF,
        attunement=True,
        description="以一个魔法动作，你可以将法杖扔到你周边10尺内一处未占据空间的地面上，并让其变为一条巨蟒蛇。这条蛇将受你所控，其先攻值与你相同，并在你的回合结束后立即进行其回合。以一个附赠动作，你可以命令蛇在当前的空间还原回法杖形态，之后你无法在1小时内再次使用法杖的词条。如果蛇的生命值被降为0，它将死亡并还原回法杖形态，随后法杖破碎并被摧毁。",
        properties={"summons": "巨蟒蛇", "cooldown_hours": 1},
        source=_SRC + "法杖/非普通.htm",
    ),

    # ═══════════ 奇物（着装品） ═══════════
    MagicItem(
        name="伪迹之靴", name_en="Boots of False Tracks",
        rarity=Rarity.COMMON, item_type=ItemType.WONDROUS_ITEM,
        attunement=True,
        description="着装这双靴子期间，你可以令其留下与你体型相同的一种类人相似的足迹。",
        properties={"slot": "足部"},
        source=_SRC + "奇物/着装品/普通.htm",
    ),
    MagicItem(
        name="飘扬斗篷", name_en="Cloak of Billowing",
        rarity=Rarity.COMMON, item_type=ItemType.WONDROUS_ITEM,
        attunement=False,
        description="着装这件斗篷期间，你可以用一个附赠动作令它大幅度地飘扬起来，持续1分钟。",
        properties={"slot": "肩部", "action_type": "附赠动作"},
        source=_SRC + "奇物/着装品/普通.htm",
    ),
    MagicItem(
        name="万众时尚斗篷", name_en="Cloak of Many Fashions",
        rarity=Rarity.COMMON, item_type=ItemType.WONDROUS_ITEM,
        attunement=False,
        description="着装此斗篷期间，你可以用一个附赠动作改变它的样式、颜色及外表品质。这件斗篷的重量不会因此改变，且不论它的外观如何，这件斗篷永远只能是一件斗篷而不是别的东西。",
        properties={"slot": "肩部", "action_type": "附赠动作"},
        source=_SRC + "奇物/着装品/普通.htm",
    ),
    MagicItem(
        name="修补之衣", name_en="Clothes of Mending",
        rarity=Rarity.COMMON, item_type=ItemType.WONDROUS_ITEM,
        attunement=False,
        description="这套优雅的服饰会魔法性地修复自己的日常磨损。不过它被损毁的部分无法以此自我修复。",
        properties={"slot": "身体"},
        source=_SRC + "奇物/着装品/普通.htm",
    ),
    MagicItem(
        name="恐怖头盔", name_en="Dread Helm",
        rarity=Rarity.COMMON, item_type=ItemType.WONDROUS_ITEM,
        attunement=False,
        description="佩戴这顶头盔期间，这个惊悚的钢铁头盔会使你的眼睛亮起着红色的光芒，你脸部的其他部分则隐藏在阴影中。",
        properties={"slot": "头部"},
        source=_SRC + "奇物/着装品/普通.htm",
    ),
    MagicItem(
        name="害兽帽", name_en="Hat of Vermin",
        rarity=Rarity.COMMON, item_type=ItemType.WONDROUS_ITEM,
        attunement=False,
        description="这顶帽子有3充能。持握此帽期间，你可以用一个魔法动作消耗1充能，召唤你选择的下述三种生物之一：一只蝙蝠、一只青蛙或一只鼠。召唤出的生物魔法性地出现在帽子中，并且会试图尽快远离你。此生物对你和其他生物的态度是冷漠，且不在你的控制之下。它会如其种类的普通生物一般行动，且会在1小时或者生命值降至0点时消失。此帽在每日黎明时恢复所有已消耗的充能。",
        properties={"slot": "头部", "charges": 3, "recharge": "每日黎明全部恢复",
                    "summons": ["蝙蝠", "青蛙", "鼠"]},
        source=_SRC + "奇物/着装品/普通.htm",
    ),
    MagicItem(
        name="巫术帽", name_en="Hat of Wizardry",
        rarity=Rarity.COMMON, item_type=ItemType.WONDROUS_ITEM,
        attunement=True, attunement_req="需法师同调",
        description="这顶锥形帽上点缀着星月。你着装此帽期间，你获得下述增益。施法法器：你可以将其作为你施展法师法术的施法法器。未知法术：你可以用一个魔法动作尝试施展一道你并未已知的戏法。所选戏法必须位于法师法表中，并且其施法时间必须为动作。你进行一次DC10的智力（奥秘）检定。检定成功，则你施展那道法术。检定失败，则你施法失败，用于施法的动作被浪费。无论检定成功与否，此词条一经使用，直到你完成一次长休之前不能再次使用。",
        properties={"slot": "头部", "focus_class": "法师", "daily_use": True},
        source=_SRC + "奇物/着装品/普通.htm",
    ),
    # ── 极珍稀 ──────────────────────────────────────────────
    MagicItem(
        name="焰舌", name_en="Flame Tongue",
        rarity=Rarity.VERY_RARE, item_type=ItemType.WEAPON,
        attunement=True, attunement_req="",
        description="你着装此武器并用附赠动作说出命令词，可使其绽放火焰或熄灭火焰。绽放火焰时，你的攻击检定和伤害掷骰获得+2火焰伤害加值。此武器发射明亮火光10尺、微光10尺。",
        properties={"bonus": 2, "damage_type": "火焰", "command_word": True},
        source=_SRC + "武器/极珍稀.htm",
    ),
    MagicItem(
        name="移位斗篷", name_en="Cloak of Displacement",
        rarity=Rarity.VERY_RARE, item_type=ItemType.WONDROUS_ITEM,
        attunement=True, attunement_req="",
        description="你着装此斗篷期间，所有对你进行的攻击检定具有劣势。若你受到伤害，此词条在下一回合开始前失效。",
        properties={"slot": "斗篷", "effect": "攻击劣势"},
        source=_SRC + "奇物/着装品/极珍稀.htm",
    ),
    MagicItem(
        name="隐身戒指", name_en="Ring of Invisibility",
        rarity=Rarity.LEGENDARY, item_type=ItemType.RING,
        attunement=True, attunement_req="",
        description="你着装此戒指期间，你可以在任何时刻作为附赠动作隐形。你持续隐形至你攻击、施法或用一个动作取消隐形。",
        properties={"slot": "戒指", "action": "附赠动作", "condition": "攻击/施法取消"},
        source=_SRC + "戒指/传说.htm",
    ),
    MagicItem(
        name="治愈法杖", name_en="Staff of Healing",
        rarity=Rarity.VERY_RARE, item_type=ItemType.STAFF,
        attunement=True, attunement_req="需施法者",
        description="你着装此法杖期间，它可作为施法法器。法杖含10发充能。施展法术消耗充能：治疗伤势(1环,1发)、群体治疗伤势(3环,3发)、复原术(2环,2发)、活力术(4环,4发)。每日黎明恢复1d6+4发充能。",
        properties={"charges": 10, "recharge": "1d6+4/黎明", "focus": True},
        source=_SRC + "法杖/极珍稀.htm",
    ),
    MagicItem(
        name="变形魔杖", name_en="Wand of Polymorph",
        rarity=Rarity.VERY_RARE, item_type=ItemType.WAND,
        attunement=True, attunement_req="",
        description="此魔杖含7发充能。用动作消耗1发施展变形术(4环)。每日黎明恢复1d6+1发充能。",
        properties={"charges": 7, "recharge": "1d6+1/黎明", "spell": "变形术", "spell_level": 4},
        source=_SRC + "魔杖/极珍稀.htm",
    ),
    MagicItem(
        name="魔契法杖", name_en="Rod of the Pact Keeper",
        rarity=Rarity.VERY_RARE, item_type=ItemType.ROD,
        attunement=True, attunement_req="需魔契师",
        description="你着装此权杖期间，用它施展魔契师法术时攻击检定和豁免DC获得+2加值。长休时你可以恢复1环~5环法术位各1个（须已消耗）。每日黎明恢复1d8+2发充能。",
        properties={"bonus": 2, "class": "魔契师", "recharge": "1d8+2/黎明"},
        source=_SRC + "权杖/极珍稀.htm",
    ),
    MagicItem(
        name="六环法术卷轴", name_en="Scroll of 6th-Level Spell",
        rarity=Rarity.VERY_RARE, item_type=ItemType.SCROLL,
        attunement=False, attunement_req="",
        description="此卷轴含一道六环法术。施展者可用动作阅读卷轴施展该法术，无需法术位或材料成分。施展后卷轴毁灭。",
        properties={"consumable": True, "spell_level": 6},
        source=_SRC + "卷轴/极珍稀.htm",
    ),
    # ── 传说 ────────────────────────────────────────────────
    MagicItem(
        name="神圣复仇者", name_en="Holy Avenger",
        rarity=Rarity.LEGENDARY, item_type=ItemType.WEAPON,
        attunement=True, attunement_req="需圣武士",
        description="你着装此武器期间获得+3攻击和伤害加值。着装者在10尺灵光内时，你与灵光内盟友对法术的豁免检定具有优势。用附赠动作可展开灵光。",
        properties={"bonus": 3, "aura": "法术豁免优势", "aura_radius": 10, "base_item_price_gp": 0},
        source=_SRC + "武器/传说.htm",
    ),
    MagicItem(
        name="阳刃", name_en="Sun Blade",
        rarity=Rarity.LEGENDARY, item_type=ItemType.WEAPON,
        attunement=True, attunement_req="",
        description="此剑刃发出明亮日光10尺、微光10尺。用附赠动作可点燃/熄灭。点燃时获得+2攻击和伤害加值。对不死生物额外造成1d8光耀伤害。",
        properties={"bonus": 2, "damage_type": "光耀", "bonus_damage_dice": "1d8",
                   "bonus_damage_target": "不死生物", "light": "明亮10/微光10"},
        source=_SRC + "武器/传说.htm",
    ),
    MagicItem(
        name="无敌护甲", name_en="Armor of Invulnerability",
        rarity=Rarity.LEGENDARY, item_type=ItemType.ARMOR,
        attunement=True, attunement_req="",
        description="你着装此护甲期间，你对非魔法武器的钝击、穿刺和挥砍伤害具有抗性。用附赠动作可进入无敌状态10分钟（非魔法武器伤害免疫），每日1次，长休恢复。",
        properties={"resistance": True, "immune_daily": True, "base_item_price_gp": 1500},
        source=_SRC + "护甲/传说.htm",
    ),
    MagicItem(
        name="三愿戒指", name_en="Ring of Three Wishes",
        rarity=Rarity.LEGENDARY, item_type=ItemType.RING,
        attunement=True, attunement_req="",
        description="此戒指含3发充能。用动作消耗1发施展愿望术(9环)。施展后戒指消失（用尽3发时）。",
        properties={"charges": 3, "spell": "愿望术", "spell_level": 9, "consumable_charges": True},
        source=_SRC + "戒指/传说.htm",
    ),
    MagicItem(
        name="力量法杖", name_en="Staff of Power",
        rarity=Rarity.VERY_RARE, item_type=ItemType.STAFF,
        attunement=True, attunement_req="需法师、术士或魔契师",
        description="着装期间+2攻击检定、+2法术豁免DC、+2AC。法杖含20发充能，可施展多种法术（魔法飞弹/火球/闪电束等）。破毁时半径30尺爆炸，16d6力场伤害DC17敏捷豁免半伤。",
        properties={"charges": 20, "bonus_attack": 2, "bonus_dc": 2, "bonus_ac": 2,
                   "recharge": "1d6+10/黎明", "retaliate_dice": "16d6"},
        source=_SRC + "法杖/极珍稀.htm",
    ),
    MagicItem(
        name="六面门", name_en="Cubic Gate",
        rarity=Rarity.LEGENDARY, item_type=ItemType.WONDROUS_ITEM,
        attunement=True, attunement_req="",
        description="此六面立方体可将你和至多8名生物传送到其他位面。用动作按压一面，所有人传送到对应位面。每日3次使用机会。",
        properties={"daily_uses": 3, "effect": "位面传送", "max_creatures": 8},
        source=_SRC + "奇物/传说.htm",
    ),
    MagicItem(
        name="变形魔杖（传说）", name_en="Wand of True Polymorph",
        rarity=Rarity.LEGENDARY, item_type=ItemType.WAND,
        attunement=True, attunement_req="",
        description="此魔杖含3发充能。用动作消耗1发施展真实变形术(8环)。每日黎明恢复1发充能。",
        properties={"charges": 3, "recharge": "1/黎明", "spell": "真实变形术", "spell_level": 8},
        source=_SRC + "魔杖/传说.htm",
    ),
    # ── 神器 ────────────────────────────────────────────────
    MagicItem(
        name="雷霆战锤", name_en="Hammer of Thunderbolts",
        rarity=Rarity.ARTIFACT, item_type=ItemType.WEAPON,
        attunement=True, attunement_req="需力量属性值高于18",
        description="这把传奇战锤着装期间获得+3攻击和伤害。着装者力量提升至29(若已更高则不变)。攻击命中时可发出雷鸣波，目标须DC17体质豁免否则被震慑。需配合巨力腰带和铁手套方可发挥全力。",
        properties={"bonus": 3, "set_str": 29, "stun_dc": 17, "set_items": ["巨力腰带", "铁手套"]},
        source=_SRC + "武器/神器.htm",
    ),
    MagicItem(
        name="万象命运牌", name_en="Deck of Many Things",
        rarity=Rarity.ARTIFACT, item_type=ItemType.WONDROUS_ITEM,
        attunement=False, attunement_req="",
        description="抽牌者必须在抽牌前声明抽牌数量（至多不可超过你声明的数量）。抽出的每张牌立刻产生魔法效果（如获得等级、失去所有财产、被异界生物追杀等），然后牌消失。",
        properties={"cards": 22, "draw_rule": "声明数量"},
        source=_SRC + "奇物/神器.htm",
    ),
    MagicItem(
        name="黑锐剑", name_en="Blackrazor",
        rarity=Rarity.ARTIFACT, item_type=ItemType.WEAPON,
        attunement=True, attunement_req="需施法者",
        description="这把 sentient 黑色巨剑着装期间+3攻击和伤害。攻击命中时吸取目标生命力（额外3d6暗蚀伤害），击杀时恢复你2d6+ wielder等级HP。可吸收灵魂并增强自身。",
        properties={"bonus": 3, "bonus_damage_dice": "3d6", "bonus_damage_type": "暗蚀",
                   "sentient": True, "heal_on_kill": "2d6+level"},
        source=_SRC + "武器/神器.htm",
    ),
    MagicItem(
        name="龙晶宝珠", name_en="Orb of Dragonkind",
        rarity=Rarity.ARTIFACT, item_type=ItemType.WONDROUS_ITEM,
        attunement=True, attunement_req="需施法者",
        description="古老宝珠，持有者可感知1000尺内龙的存在，对龙的法术豁免优势。每日3次施展龙息术(7环)。但持有者逐渐被龙之意志腐蚀。",
        properties={"daily_uses": 3, "spell": "龙息术", "spell_level": 7,
                   "sense": "龙1000尺", "corruption": True},
        source=_SRC + "奇物/神器.htm",
    ),
    MagicItem(
        name="万灭魔杖", name_en="Wand of Orcus",
        rarity=Rarity.ARTIFACT, item_type=ItemType.WAND,
        attunement=True, attunement_req="",
        description="奥喀斯之杖。着装期间+3攻击和伤害。你召唤的不死生物获得额外生命值。每日可施展枯萎术、死亡一指等。着装者逐渐被奥喀斯意志支配。",
        properties={"bonus": 3, "summon_bonus_hp": True, "daily_spells": ["枯萎术", "死亡一指"],
                   "corruption": True},
        source=_SRC + "魔杖/神器.htm",
    ),
    MagicItem(
        name="七环法术卷轴", name_en="Scroll of 7th-Level Spell",
        rarity=Rarity.VERY_RARE, item_type=ItemType.SCROLL,
        attunement=False, attunement_req="",
        description="此卷轴含一道七环法术。施展者可用动作阅读卷轴施展该法术，无需法术位或材料成分。施展后卷轴毁灭。",
        properties={"consumable": True, "spell_level": 7},
        source=_SRC + "卷轴/极珍稀.htm",
    ),
    MagicItem(
        name="九环法术卷轴", name_en="Scroll of 9th-Level Spell",
        rarity=Rarity.LEGENDARY, item_type=ItemType.SCROLL,
        attunement=False, attunement_req="",
        description="此卷轴含一道九环法术。施展者可用动作阅读卷轴施展该法术，无需法术位或材料成分。施展后卷轴毁灭。",
        properties={"consumable": True, "spell_level": 9},
        source=_SRC + "卷轴/传说.htm",
    ),
    MagicItem(
        name="万魔权杖", name_en="Rod of Lordly Might",
        rarity=Rarity.LEGENDARY, item_type=ItemType.ROD,
        attunement=True, attunement_req="",
        description="此权杖含10发充能。可变形成武器（长剑/短矛/长矛），每日各功能消耗不同充能：恐惧术(2发)、灵体仆从(3发)、超惑术(4发)。+3攻击加值。",
        properties={"charges": 10, "bonus": 3, "shapechange": True, "recharge": "1d6+4/黎明"},
        source=_SRC + "权杖/传说.htm",
    ),
]


# 构建名称索引字典
MAGIC_ITEMS: dict[str, MagicItem] = {item.name: item for item in _MAGIC_ITEMS_LIST}


# ──────────────────────────────────────────────────────────────────────────
# 查询函数
# ──────────────────────────────────────────────────────────────────────────

def get_magic_item(name: str) -> Optional[MagicItem]:
    """按名称查询魔法物品。

    Args:
        name: 物品中文名（精确匹配）

    Returns:
        MagicItem 或 None（未找到时）

    规则依据: 城主指南2024/7.宝藏/魔法物品详述/
    """
    return MAGIC_ITEMS.get(name)


def list_magic_items(rarity: Optional[Rarity] = None,
                     item_type: Optional[ItemType] = None,
                     cursed_only: bool = False) -> list[MagicItem]:
    """列出魔法物品，支持按稀有度/类别/诅咒筛选。

    Args:
        rarity: 按稀有度筛选（None=不限）
        item_type: 按类别筛选（None=不限）
        cursed_only: 仅返回诅咒物品

    Returns:
        匹配的 MagicItem 列表，按稀有度升序排列

    规则依据: 城主指南2024/7.宝藏/魔法物品详述/
    """
    result = []
    for item in _MAGIC_ITEMS_LIST:
        if rarity is not None and item.rarity != rarity:
            continue
        if item_type is not None and item.item_type != item_type:
            continue
        if cursed_only and not item.cursed:
            continue
        result.append(item)
    result.sort(key=lambda x: (x.rarity.sort_order, x.name))
    return result


def items_by_rarity(rarity: Rarity) -> list[MagicItem]:
    """获取指定稀有度的所有物品。"""
    return list_magic_items(rarity=rarity)


def items_by_type(item_type: ItemType) -> list[MagicItem]:
    """获取指定类别的所有物品。"""
    return list_magic_items(item_type=item_type)


def random_magic_items(count: int = 1,
                       max_rarity: Optional[Rarity] = None,
                       min_rarity: Optional[Rarity] = None,
                       seed: Optional[int] = None) -> list[MagicItem]:
    """随机抽取N个魔法物品（不放回）。

    用于战利品生成与随机魔法物品表。

    Args:
        count: 抽取数量
        max_rarity: 稀有度上限（含）
        min_rarity: 稀有度下限（含）
        seed: 随机种子（测试用）

    Returns:
        随机选取的 MagicItem 列表

    规则依据: 城主指南2024/7.宝藏/随机魔法物品/
    """
    import random
    rng = random.Random(seed) if seed is not None else random.Random()

    pool = []
    for item in _MAGIC_ITEMS_LIST:
        if max_rarity is not None and item.rarity.sort_order > max_rarity.sort_order:
            continue
        if min_rarity is not None and item.rarity.sort_order < min_rarity.sort_order:
            continue
        pool.append(item)

    if not pool:
        return []

    n = min(count, len(pool))
    return rng.sample(pool, n)


# ──────────────────────────────────────────────────────────────────────────
# 同调 / 鉴定 / 着装限制
# ──────────────────────────────────────────────────────────────────────────

# 规则: 装备/魔法物品.txt「同调」— 同时同调不超过 3 件；需短休建立；
#       不可同调多个同一物品；结束条件（条件不满足/100尺外24小时/死亡/他人同调）；
#       附诅咒者不可自愿解除。
MAX_ATTUNED = 3


def attune_item(attuned_list: list[str], item_name: str,
                cursed_items: Optional[set[str]] = None) -> dict:
    """尝试与魔法物品建立同调。

    规则: 装备/魔法物品.txt「同调」— 需短休并保持物理接触；
          同时同调不超过 3 件；不可同调多个同一物品。
    出处: topics/玩家手册2024/装备/魔法物品.htm

    参数:
      attuned_list: 当前已同调物品名列表
      item_name: 要同调的物品名
      cursed_items: 已知诅咒物品名集合（用于后续不可自愿解除判定）

    返回: {"success": bool, "reason": str, "attuned_list": list}
    """
    item = MAGIC_ITEMS.get(item_name)
    if item is None:
        return {"success": False, "reason": "未知物品", "attuned_list": attuned_list}
    if not item.attunement:
        return {"success": False, "reason": "该物品无需同调", "attuned_list": attuned_list}
    if item_name in attuned_list:
        return {"success": False, "reason": "已同调该物品，不可重复", "attuned_list": attuned_list}
    if len(attuned_list) >= MAX_ATTUNED:
        return {"success": False, "reason": f"同调上限{MAX_ATTUNED}件已达", "attuned_list": attuned_list}
    attuned_list = list(attuned_list) + [item_name]
    if cursed_items is not None and item.cursed:
        cursed_items.add(item_name)
    return {"success": True, "reason": "同调成功（需短休保持接触）", "attuned_list": attuned_list}


def unattune_item(attuned_list: list[str], item_name: str,
                 cursed_items: Optional[set[str]] = None) -> dict:
    """尝试解除魔法物品同调。

    规则: 装备/魔法物品.txt — 附诅咒物品不可自愿解除同调。
    出处: topics/玩家手册2024/装备/魔法物品.htm
    """
    if item_name not in attuned_list:
        return {"success": False, "reason": "未同调该物品", "attuned_list": attuned_list}
    if cursed_items and item_name in cursed_items:
        return {"success": False, "reason": "诅咒物品不可自愿解除同调", "attuned_list": attuned_list}
    attuned_list = [n for n in attuned_list if n != item_name]
    return {"success": True, "reason": "解除同调成功", "attuned_list": attuned_list}


def check_attunement_end(attuned_list: list[str], item_name: str,
                        reason: str) -> dict:
    """检查同调结束条件。

    规则: 装备/魔法物品.txt — 条件不满足/100尺外超过24小时/死亡/他人同调该物品 → 结束。
    reason: "condition_lost" / "distance_24h" / "death" / "stolen"
    """
    if item_name not in attuned_list:
        return {"ended": False, "reason": "未同调", "attuned_list": attuned_list}
    # 诅咒物品也因这些条件结束（非自愿解除）
    attuned_list = [n for n in attuned_list if n != item_name]
    return {"ended": True, "reason": reason, "attuned_list": attuned_list}


def identify_magic_item(item_name: str, use_identify_spell: bool = False) -> dict:
    """鉴定魔法物品。

    规则: 装备/魔法物品.txt「鉴定」— 短休专注可鉴定（不含诅咒）；
          鉴定术法术也可鉴定（不含诅咒）。
    出处: topics/玩家手册2024/装备/魔法物品.htm
    """
    item = MAGIC_ITEMS.get(item_name)
    if item is None:
        return {"identified": False, "reason": "未知物品"}
    method = "鉴定术" if use_identify_spell else "短休专注"
    return {
        "identified": True,
        "method": method,
        "name": item.name,
        "rarity": item.rarity.value,
        "item_type": item.item_type.value,
        "attunement_required": item.attunement,
        "attunement_req": item.attunement_req,
        "description": item.description,
        "curse_revealed": False,  # 鉴定不揭示诅咒
        "cursed": item.cursed,     # 但数据层仍可查询（DM层面）
    }


def check_worn_item_limits(attuned_list: list[str],
                           new_item_type: ItemType) -> dict:
    """检查着装同类限制。

    规则: 装备/魔法物品.txt — 不可同时着装多件同类魔法物品；
          成对物品须成对着装。
    出处: topics/玩家手册2024/装备/魔法物品.htm
    """
    # 统计已同调物品中同类型的数量
    same_type_count = 0
    for name in attuned_list:
        item = MAGIC_ITEMS.get(name)
        if item and item.item_type == new_item_type:
            same_type_count += 1
    # 同类型最多着装1件（除非是成对物品，此处简化）
    can_wear = same_type_count == 0
    return {"can_wear": can_wear, "same_type_count": same_type_count,
            "reason": "" if can_wear else f"已着装{same_type_count}件同类物品"}


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    """魔法物品数据库自检。"""
    # 1. 数据完整性：至少20个物品
    assert len(_MAGIC_ITEMS_LIST) >= 20, f"物品数不足: {len(_MAGIC_ITEMS_LIST)}"
    print(f"[magic_items] 物品总数: {len(_MAGIC_ITEMS_LIST)}")

    # 2. 名称唯一性
    names = [item.name for item in _MAGIC_ITEMS_LIST]
    assert len(names) == len(set(names)), "存在重复物品名称"
    assert len(MAGIC_ITEMS) == len(_MAGIC_ITEMS_LIST), "索引字典大小不匹配"

    # 3. 每个物品都有必填字段
    for item in _MAGIC_ITEMS_LIST:
        assert item.name, f"物品缺少名称: {item}"
        assert item.name_en, f"物品缺少英文名: {item.name}"
        assert isinstance(item.rarity, Rarity), f"{item.name} 稀有度类型错误"
        assert isinstance(item.item_type, ItemType), f"{item.name} 类别类型错误"
        assert item.description, f"{item.name} 缺少描述"
        assert item.source, f"{item.name} 缺少出处"
        # 同调物品应有标记
        if item.attunement_req:
            assert item.attunement, f"{item.name} 有同调要求但attunement=False"

    # 4. 查询函数
    sword = get_magic_item("触月剑")
    assert sword is not None and sword.rarity == Rarity.COMMON
    assert sword.item_type == ItemType.WEAPON

    cursed = list_magic_items(cursed_only=True)
    assert len(cursed) >= 1, "应至少有1个诅咒物品"
    assert all(item.cursed for item in cursed), "cursed_only结果包含非诅咒物品"

    weapons = items_by_type(ItemType.WEAPON)
    assert len(weapons) >= 5, f"武器物品不足: {len(weapons)}"
    assert all(item.item_type == ItemType.WEAPON for item in weapons)

    common_items = items_by_rarity(Rarity.COMMON)
    assert len(common_items) >= 10, f"普通物品不足: {len(common_items)}"
    assert all(item.rarity == Rarity.COMMON for item in common_items)

    # 5. 价格计算
    # 普通武器：100gp基础
    assert sword.price_gp == 100, f"触月剑价格应为100gp，实际{sword.price_gp}"
    # 药水是消耗品，价格减半：攀爬药水(普通)=100/2=50gp
    potion = get_magic_item("攀爬药水")
    assert potion.price_gp == 50, f"攀爬药水价格应为50gp，实际{potion.price_gp}"
    # 珍稀药水：4000/2=2000gp
    invis_potion = get_magic_item("隐身药水")
    assert invis_potion.price_gp == 2000, f"隐身药水价格应为2000gp，实际{invis_potion.price_gp}"

    # 6. 随机抽取
    random_items = random_magic_items(count=3, seed=42)
    assert len(random_items) == 3, "随机抽取数量不符"
    assert len(set(item.name for item in random_items)) == 3, "随机抽取不应有重复"

    # 可复现性
    random_items2 = random_magic_items(count=3, seed=42)
    assert [item.name for item in random_items] == [item.name for item in random_items2], \
        "相同种子应产生相同结果"

    # 稀有度筛选
    common_random = random_magic_items(count=5, max_rarity=Rarity.COMMON, seed=123)
    assert all(item.rarity == Rarity.COMMON for item in common_random), \
        "max_rarity=COMMON应只返回普通物品"

    # 7. 序列化
    d = sword.to_dict()
    assert d["name"] == "触月剑"
    assert d["rarity"] == "普通"
    assert d["item_type"] == "武器"
    assert d["price_gp"] == 100
    assert "武器/普通.htm" in d["source"]

    # 8. 稀有度枚举属性
    assert Rarity.COMMON.base_price_gp == 100
    assert Rarity.LEGENDARY.base_price_gp == 200000
    assert Rarity.ARTIFACT.base_price_gp == 0
    assert Rarity.COMMON.sort_order < Rarity.ARTIFACT.sort_order

    # 9. 类别覆盖：至少覆盖武器/护甲/药水/戒指/法杖/奇物
    covered_types = set(item.item_type for item in _MAGIC_ITEMS_LIST)
    expected_types = {ItemType.WEAPON, ItemType.ARMOR, ItemType.POTION,
                      ItemType.RING, ItemType.STAFF, ItemType.WONDROUS_ITEM}
    missing = expected_types - covered_types
    assert not missing, f"缺少类别覆盖: {[t.value for t in missing]}"

    # 10. 稀有度覆盖：至少覆盖普通/非普通/珍稀
    covered_rarities = set(item.rarity for item in _MAGIC_ITEMS_LIST)
    expected_rarities = {Rarity.COMMON, Rarity.UNCOMMON, Rarity.RARE}
    missing_r = expected_rarities - covered_rarities
    assert not missing_r, f"缺少稀有度覆盖: {[r.value for r in missing_r]}"

    print("[magic_items] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
