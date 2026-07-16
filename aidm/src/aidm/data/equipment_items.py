"""冒险装备数据 — PHB 2024 第六章。

来源: 玩家手册2024/装备/冒险装备.htm
提供: 60+ 冒险装备（价格、重量、效果描述）
"""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class EquipmentItem:
    """通用冒险装备数据模型。"""
    name: str
    name_en: str
    category: str           # "冒险用品", "弹药", "套组", "法器", "消耗品"
    price_gp: float
    weight_lb: float
    description: str = ""   # 详细规则文本
    effect: str = ""        # 机械效应简述


ITEMS: dict[str, EquipmentItem] = {}

def _reg(item: EquipmentItem):
    ITEMS[item.name] = item

# ═══════════════════════════════════════════════════════════════════════════
# 冒险用品 (Adventuring Gear)
# ═══════════════════════════════════════════════════════════════════════════

_reg(EquipmentItem("强酸", "Acid", "消耗品", 25, 1,
    effect="替换一次攻击：20尺内目标DC 8+敏捷调整+熟练 敏捷豁免，失败受2d6强酸伤害。",
    description="当你执行攻击动作时，你可以将你的一次攻击替换为丢出一小瓶强酸。你可以选择位于你20尺内可见的一个生物或物件作为目标。该目标必须通过一次敏捷豁免（DC等于8+你的敏捷调整值+你的熟练加值），否则承受2d6点强酸伤害。"))

_reg(EquipmentItem("炽火胶", "Alchemist's Fire", "消耗品", 50, 1,
    effect="替换一次攻击：20尺内目标DC 8+敏捷调整+熟练 敏捷豁免，失败受1d4火焰伤害并开始燃烧。",
    description="当你执行攻击动作时，你可以将你的一次攻击替换为丢出一扁瓶炽火胶。你可以选择位于你20尺内可见的一个生物或物件作为目标。该目标必须通过一次敏捷豁免（DC等于8+你的敏捷调整值+你的熟练加值），否则承受1d4点火焰伤害并开始燃烧。"))

_reg(EquipmentItem("抗毒剂", "Antitoxin", "消耗品", 50, 0,
    effect="喝下后1小时内对抗毒素的体质豁免具有优势。",
    description="一瓶混合了特殊草药精华的液体。喝下抗毒剂的生物在1小时内为抵抗毒素所作的所有体质豁免具有优势。"))

_reg(EquipmentItem("奥术法器", "Arcane Focus", "法器", 0, 0,  # 多类价格/重量
    effect="代替法术材料（无价格的材料成分）。",
    description="奥术法器是一种可以用于代替施展法术所需材料成分的特殊物品——前提是该材料成分没有标注价格且不会被法术消耗。奥术法器的类型包括：水晶、法珠、权杖、法杖、魔杖。"))

_reg(EquipmentItem("背包", "Backpack", "冒险用品", 2, 5,
    effect="容量30磅。",
    description="一个皮革背包可以容纳最多30磅的物资。如果你拥有多个背包，则只能从其中的一个背包中获益。"))

_reg(EquipmentItem("滚珠", "Ball Bearings", "消耗品", 1, 2,
    effect="1000枚滚珠覆盖10尺方形区域，经过的生物DC10敏捷豁免否则倒地。",
    description="你可以从一个包里倾倒出1000枚滚珠，复盖一片10尺方形区域。穿过这片区域的生物必须成功通过一次DC10的敏捷豁免才能保持站立。以半速穿过该区域的生物不需要进行豁免。"))

_reg(EquipmentItem("木桶", "Barrel", "冒险用品", 2, 70,
    effect="容量40加仑液体或4立方尺固体。"))

_reg(EquipmentItem("篮子", "Basket", "冒险用品", 0.4, 2,
    effect="容量2立方尺或40磅。"))

_reg(EquipmentItem("铺盖", "Bedroll", "冒险用品", 1, 7))

_reg(EquipmentItem("铃铛", "Bell", "冒险用品", 1, 0))

_reg(EquipmentItem("毯子", "Blanket", "冒险用品", 0.5, 3))

_reg(EquipmentItem("滑轮组", "Block and Tackle", "冒险用品", 1, 5,
    effect="一组滑轮、绳索和挂钩，可让你提起至多四倍于平常的重量。"))

_reg(EquipmentItem("书籍", "Book", "冒险用品", 25, 5,
    effect="一本涵盖历史、传说、诗歌等内容的书籍。"))

_reg(EquipmentItem("玻璃瓶", "Glass Bottle", "冒险用品", 2, 2,
    effect="容量1.5品脱液体。"))

_reg(EquipmentItem("吊桶", "Bucket", "冒险用品", 0.05, 2,
    effect="容量3加仑液体或0.5立方尺固体。"))

_reg(EquipmentItem("窃贼套组", "Burglar's Pack", "套组", 16, 42,
    description="包含：背包、滚珠(1000枚)、10尺细绳、铃铛、5支蜡烛、撬棍、锤子、10个岩钉、附盖提灯、2瓶燃油、5天口粮、火绒盒、水袋、50尺麻绳。"))

_reg(EquipmentItem("铁蒺藜", "Caltrops", "消耗品", 1, 2,
    effect="20枚铁蒺藜覆盖5尺方形区域，经过的生物DC10敏捷豁免否则停止移动并受1穿刺伤害。",
    description="你可以将一包铁蒺藜撒开，复盖一片5尺方形的区域。任何进入该区域的生物必须成功通过一次DC10的敏捷豁免，否则将停止移动并承受1点穿刺伤害。以半速穿过该区域的生物不需要进行豁免。"))

_reg(EquipmentItem("蜡烛", "Candle", "冒险用品", 0.01, 0,
    effect="提供5尺明亮光照+额外5尺微光光照，持续1小时。"))

_reg(EquipmentItem("弩矢匣", "Case, Crossbow Bolt", "冒险用品", 1, 1,
    effect="可容纳最多20支弩矢。"))

_reg(EquipmentItem("地图或卷轴匣", "Case, Map or Scroll", "冒险用品", 1, 1,
    effect="可容纳最多10张卷轴或5张地图。"))

_reg(EquipmentItem("链条", "Chain (10 feet)", "冒险用品", 5, 10,
    effect="10尺铁链，可被破坏（AC19，10HP，免疫毒素和心灵伤害）。"))

_reg(EquipmentItem("箱子", "Chest", "冒险用品", 5, 25,
    effect="容量12立方尺或300磅。"))

_reg(EquipmentItem("攀爬工具", "Climber's Kit", "冒险用品", 25, 12,
    effect="包括岩钉、靴刺、手套和挽具。攀爬时获得特化锚点。"))

_reg(EquipmentItem("高档服装", "Clothes, Fine", "冒险用品", 15, 6))

_reg(EquipmentItem("旅行服装", "Clothes, Traveler's", "冒险用品", 2, 4))

_reg(EquipmentItem("材料包", "Component Pouch", "冒险用品", 25, 2,
    effect="代替法术材料成分。"))

_reg(EquipmentItem("戏服", "Costume", "冒险用品", 5, 4))

_reg(EquipmentItem("撬棍", "Crowbar", "冒险用品", 2, 5,
    effect="使用撬棍时，需要进行力量检定的地方可获得优势。"))

_reg(EquipmentItem("外交套组", "Diplomat's Pack", "套组", 39, 39,
    description="包含：箱子、2个地图或卷轴匣、一套高档服装、一瓶墨水、一支墨水笔、一盏油灯、10张纸张、一小瓶香水、封蜡、肥皂。"))

_reg(EquipmentItem("德鲁伊法器", "Druidic Focus", "法器", 0, 0,
    effect="代替法术材料（无价格的材料成分）。",
    description="德鲁伊法器类型：槲寄生、冬青木魔杖、紫杉木魔杖、或由紫杉木或其他特殊木材制成的权杖。"))

_reg(EquipmentItem("地城套组", "Dungeoneer's Pack", "套组", 12, 55,
    description="包含：背包、撬棍、锤子、10个岩钉、10支火把、火绒盒、10天口粮、水袋、50尺麻绳。"))

_reg(EquipmentItem("艺人套组", "Entertainer's Pack", "套组", 40, 58.5,
    description="包含：背包、睡袋、2套戏服、5支蜡烛、5天口粮、水袋、易容工具。"))

_reg(EquipmentItem("探索套组", "Explorer's Pack", "套组", 10, 55,
    description="包含：背包、睡袋、一套餐具、火绒盒、10支火把、10天口粮、水袋、50尺麻绳。"))

_reg(EquipmentItem("扁瓶", "Flask", "冒险用品", 0.02, 1,
    effect="容量1品脱液体。"))

_reg(EquipmentItem("爪钩", "Grappling Hook", "冒险用品", 2, 4))

_reg(EquipmentItem("医疗包", "Healer's Kit", "冒险用品", 5, 3,
    effect="有10次使用次数。以一个动作消耗一次使用来稳定一个0HP的生物，无需进行感知(医药)检定。"))

_reg(EquipmentItem("圣徽", "Holy Symbol", "法器", 0, 0,
    effect="代替法术材料（无价格的材料成分）。",
    description="圣徽类型：护符、圣徽浮雕、圣物匣。"))

_reg(EquipmentItem("圣水", "Holy Water", "消耗品", 25, 1,
    effect="替换一次攻击：20尺内邪魔或不死生物DC 8+敏捷调整+熟练 敏捷豁免，否则受2d6光耀伤害。",
    description="你可以将一次攻击替换为投掷圣水瓶。目标须通过DC 8+敏捷调整值+熟练加值的敏捷豁免，邪魔和不死生物豁免失败受2d6光耀伤害。"))

_reg(EquipmentItem("捕猎陷阱", "Hunting Trap", "冒险用品", 5, 25,
    effect="设置后DC10察觉发现，踩中的生物DC10敏捷豁免否则受1d4穿刺伤害并停止移动。挣脱需DC10力量检定。"))

_reg(EquipmentItem("墨水", "Ink (1 ounce bottle)", "冒险用品", 10, 0))

_reg(EquipmentItem("墨水笔", "Ink Pen", "冒险用品", 0.02, 0))

_reg(EquipmentItem("壶", "Jug", "冒险用品", 0.02, 4,
    effect="容量1加仑液体。"))

_reg(EquipmentItem("梯子", "Ladder (10 foot)", "冒险用品", 0.1, 25))

_reg(EquipmentItem("油灯", "Lamp", "冒险用品", 0.5, 1,
    effect="提供15尺明亮光照+额外30尺微光光照，燃烧6小时每品脱油。"))

_reg(EquipmentItem("牛眼提灯", "Lantern, Bullseye", "冒险用品", 10, 2,
    effect="60尺锥形明亮光照+额外60尺微光光照，燃烧6小时每品脱油。"))

_reg(EquipmentItem("附盖提灯", "Lantern, Hooded", "冒险用品", 5, 2,
    effect="30尺明亮光照+额外30尺微光光照。放下遮罩可将光照降至5尺微光。燃烧6小时每品脱油。"))

_reg(EquipmentItem("锁", "Lock", "冒险用品", 10, 1,
    effect="附带一把钥匙。DC15敏捷(巧手)撬锁。"))

_reg(EquipmentItem("放大镜", "Magnifying Glass", "冒险用品", 100, 0,
    effect="仔细检查小型物件的检定具有优势。也可用作生火工具。"))

_reg(EquipmentItem("镣铐", "Manacles", "冒险用品", 2, 6,
    effect="可束缚小型或中型生物。DC20敏捷(巧手)挣脱，DC20力量检定破坏。"))

_reg(EquipmentItem("地图", "Map", "冒险用品", 1, 0))

_reg(EquipmentItem("镜子", "Mirror", "冒险用品", 5, 0.5,
    effect="小型钢制或银制镜子。"))

_reg(EquipmentItem("捕网", "Net", "消耗品", 1, 3,
    effect="投掷5尺内大型或更小生物：目标DC8+熟练+敏捷 敏捷豁免，失败陷入束缚。AC10，5HP（对钝击易伤），挣脱需DC10力量检定。"))

_reg(EquipmentItem("燃油", "Oil", "消耗品", 0.1, 1,
    effect="1品脱。倒出覆盖5尺方形区域，点燃后燃烧2轮，每轮5火焰伤害。也可作为油灯燃料燃烧6小时。"))

_reg(EquipmentItem("纸张", "Paper (one sheet)", "冒险用品", 0.2, 0))

_reg(EquipmentItem("羊皮纸", "Parchment (one sheet)", "冒险用品", 0.1, 0))

_reg(EquipmentItem("香水", "Perfume (vial)", "冒险用品", 5, 0))

_reg(EquipmentItem("基础毒药", "Basic Poison", "消耗品", 100, 0,
    effect="涂抹在武器或弹药上，命中后目标DC10体质豁免否则受1d4毒素伤害（维持1分钟或至多3次命中）。"))

_reg(EquipmentItem("长杆", "Pole (10-foot)", "冒险用品", 0.05, 7))

_reg(EquipmentItem("铁壶", "Pot, Iron", "冒险用品", 2, 10,
    effect="容量1加仑液体。"))

_reg(EquipmentItem("治疗药水", "Potion of Healing", "消耗品", 50, 0.5,
    effect="喝下后回复2d4+2HP。",
    description="魔法液体，喝下后恢复2d4+2生命值。"))

_reg(EquipmentItem("小包", "Pouch", "冒险用品", 0.5, 1,
    effect="容量6磅或1/5立方尺物品。"))

_reg(EquipmentItem("祭司套组", "Priest's Pack", "套组", 33, 29,
    description="包含：背包、毯子、10支蜡烛、火绒盒、募捐盒、2块熏香、香炉、祭袍、2天口粮、水袋。"))

_reg(EquipmentItem("箭袋", "Quiver", "冒险用品", 1, 1,
    effect="可容纳最多20支箭矢。"))

_reg(EquipmentItem("便携式攻城锤", "Ram, Portable", "冒险用品", 4, 35,
    effect="破门时力量检定+4加值，另一名协助角色可再为此检定提供优势。"))

_reg(EquipmentItem("口粮", "Rations (1 day)", "冒险用品", 0.5, 2,
    effect="一天的脱水干粮。"))

_reg(EquipmentItem("长袍", "Robes", "冒险用品", 1, 4))

_reg(EquipmentItem("绳索", "Rope, Hempen (50 feet)", "冒险用品", 1, 5,
    effect="AC11，2HP。DC10力量检定挣断。"))

_reg(EquipmentItem("麻袋", "Sack", "冒险用品", 0.01, 0.5,
    effect="容量1立方尺或30磅。"))

_reg(EquipmentItem("学者套组", "Scholar's Pack", "套组", 40, 22,
    description="包含：背包、一本关于当下学科书籍、10张纸张、一瓶墨水、一支墨水笔、10张羊皮纸、一小袋沙、一把小刀。"))

_reg(EquipmentItem("铲子", "Shovel", "冒险用品", 2, 5))

_reg(EquipmentItem("信号笛", "Signal Whistle", "冒险用品", 0.05, 0))

_reg(EquipmentItem("戏法卷轴", "Spell Scroll (Cantrip)", "消耗品", 30, 0,
    effect="戏法卷轴。施法攻击+5，豁免DC13。"))

_reg(EquipmentItem("一环卷轴", "Spell Scroll (Level 1)", "消耗品", 50, 0,
    effect="1环卷轴。施法攻击+5，豁免DC13。"))

_reg(EquipmentItem("铁钉", "Spike, Iron", "冒险用品", 1, 5,  # 10个
    effect="每包10个。"))

_reg(EquipmentItem("望远镜", "Spyglass", "冒险用品", 1000, 1,
    effect="通过望远镜观察，物体放大2倍。"))

_reg(EquipmentItem("细线", "String (10 feet)", "冒险用品", 0.1, 0))

_reg(EquipmentItem("帐篷", "Tent", "冒险用品", 2, 20,
    effect="两人用帐篷，12小时搭建时间。"))

_reg(EquipmentItem("火绒盒", "Tinderbox", "冒险用品", 0.5, 1,
    effect="包含火石、火镰和火绒。以动作生火需要1分钟。"))

_reg(EquipmentItem("火把", "Torch", "冒险用品", 0.01, 1,
    effect="提供20尺明亮光照+额外20尺微光光照，燃烧1小时。近战攻击命中后造成1火焰伤害。"))

_reg(EquipmentItem("小瓶", "Vial", "冒险用品", 1, 0,
    effect="容量4盎司液体。"))

_reg(EquipmentItem("水袋", "Waterskin", "冒险用品", 0.2, 5,
    effect="容量4品脱液体（满时重5磅）。"))


# ═══════════════════════════════════════════════════════════════════════════
# 弹药 (Ammunition)
# ═══════════════════════════════════════════════════════════════════════════

_reg(EquipmentItem("箭矢", "Arrows (20)", "弹药", 1, 1,
    effect="20支，需箭袋存放。"))

_reg(EquipmentItem("吹矢", "Blowgun Needles (50)", "弹药", 1, 1,
    effect="50支，需弩矢匣存放。"))

_reg(EquipmentItem("弩矢", "Crossbow Bolts (20)", "弹药", 1, 1.5,
    effect="20支，需弩矢匣存放。"))

_reg(EquipmentItem("枪械子弹", "Firearm Bullets (10)", "弹药", 3, 2,  # PHB2014价格
    effect="10发，需小包存放。"))

_reg(EquipmentItem("投石索子弹", "Sling Bullets (20)", "弹药", 0.04, 1.5,
    effect="20枚，需小包存放。"))


# ═══════════════════════════════════════════════════════════════════════════
# 容器 (Containers)
# ═══════════════════════════════════════════════════════════════════════════

_reg(EquipmentItem("箭囊", "Quiver", "容器", 1, 1,
    effect="可存放20支箭矢。"))

_reg(EquipmentItem("弩矢匣", "Case, Crossbow Bolt", "容器", 1, 1,
    effect="可存放20支弩矢。"))

_reg(EquipmentItem("地图或卷轴匣", "Case, Map or Scroll", "容器", 1, 1,
    effect="可存放10张卷轴或5张地图。"))


# ═══════════════════════════════════════════════════════════════════════════
# 查询函数
# ═══════════════════════════════════════════════════════════════════════════

def get_item(name: str) -> Optional[EquipmentItem]:
    return ITEMS.get(name)

def items_by_category(category: str) -> list[EquipmentItem]:
    return [i for i in ITEMS.values() if i.category == category]

def search_items(query: str) -> list[EquipmentItem]:
    q = query.lower()
    return [i for i in ITEMS.values() if q in i.name or q in i.name_en.lower()]


# ═══════════════════════════════════════════════════════════════════════════
# 自检
# ═══════════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    assert len(ITEMS) >= 55, f"物品数量不足: {len(ITEMS)}"

    # 强酸存在
    acid = get_item("强酸")
    assert acid is not None and acid.price_gp == 25

    # 套组
    packs = items_by_category("套组")
    assert len(packs) >= 6, f"套组不足: {len(packs)}"

    # 治疗药水
    potion = get_item("治疗药水")
    assert potion is not None and "2d4+2" in potion.effect

    print(f"[equipment_items] 自检通过 ✓ ({len(ITEMS)}件装备)")


if __name__ == "__main__":
    _self_test()
