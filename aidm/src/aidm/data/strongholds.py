"""据点系统数据表 — DMG 第八章 据点。

规则依据: 城主指南2024/8.据点/
  - 据点.htm                    据点总论
  - 1.建立一个据点.htm          建立流程（5级获得据点）
  - 2.据点回合.htm              据点回合机制（每7天一次）
  - 3.据点地图/基础设施.htm     基础设施（卧室/餐厅/客厅/庭院/厨房/储藏室）
  - 3.据点地图/据点地图.htm     据点地图总论（防御墙/合并据点/设施空间）
  - 3.据点地图/特色设施/        25种特色设施
  - 4.据点事件.htm              据点随机事件表
  - 5.失去据点.htm              失去据点条件

本模块提供:
  - StrongholdType 枚举: 据点类型（塔楼/城堡/神殿/公会会所/要塞）
  - FacilitySpace 枚举: 设施空间大小（狭窄/宽敞/庞大）
  - OrderType 枚举: 据点指令类型（制造/增强/收获/维护/招募/调查/贸易）
  - Facility dataclass: 特色设施数据
  - FACILITIES dict: 25种特色设施
  - BASIC_FACILITIES list: 6种基础设施
  - STRONGHOLD_EVENTS list: 据点随机事件表
  - SPECIAL_FACILITY_ACQUISITION: 等级→特色设施数量映射
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ──────────────────────────────────────────────────────────────────────────
# 枚举定义
# ──────────────────────────────────────────────────────────────────────────

class StrongholdType(str, Enum):
    """据点类型 — 规则: DMG第八章 §1 建立一个据点"""
    TOWER = "塔楼"           # 法师塔楼
    CASTLE = "城堡"          # 战士城堡
    TEMPLE = "神殿"          # 牧师神龛
    GUILDHOUSE = "公会会所"  # 游荡者集会所
    KEEP = "要塞"            # 坚固要塞


class FacilitySpace(str, Enum):
    """设施空间大小 — 规则: DMG第八章 §3 设施空间"""
    CRAMPED = "狭窄"         # 最大4方格
    SPACIOUS = "宽敞"        # 最大16方格
    VAST = "庞大"            # 最大36方格


class OrderType(str, Enum):
    """据点指令类型 — 规则: DMG第八章 §3 指令"""
    CRAFT = "制造"           # 制作物品
    EMPOWER = "增强"         # 施加临时增益
    HARVEST = "收获"         # 采收资源
    MAINTAIN = "维护"        # 维护整个据点（特殊指令）
    RECRUIT = "招募"         # 招募生物/卫兵
    RESEARCH = "调查"        # 收集信息
    TRADE = "贸易"           # 买卖货物/服务


# ──────────────────────────────────────────────────────────────────────────
# 特色设施数据结构
# ──────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Facility:
    """特色设施数据 — 规则: DMG第八章 §3 特色设施

    Attributes:
        name: 设施中文名
        name_en: 设施英文名
        level: 获取该设施所需的最低角色等级
        space: 设施空间大小
        hirelings: 雇员数量
        order: 可下达的据点指令类型
        prerequisite: 先决条件描述（无先决条件则为空字符串）
        description: 设施描述
        effects: 设施效果详述（列表，每项为一条效果说明）
        can_enlarge: 是否可以扩大设施（花费2000GP扩大为庞大）
        multiple_allowed: 是否允许拥有多个同种设施
    """
    name: str
    name_en: str
    level: int
    space: FacilitySpace
    hirelings: int
    order: OrderType
    prerequisite: str = ""
    description: str = ""
    effects: list[str] = field(default_factory=list)
    can_enlarge: bool = False
    multiple_allowed: bool = False


# ──────────────────────────────────────────────────────────────────────────
# 25种特色设施
# 规则: DMG第八章 §3 特色设施详述
# 来源: topics/城主指南2024/8.据点/3.据点地图/特色设施/*.htm
# ──────────────────────────────────────────────────────────────────────────

FACILITIES: dict[str, Facility] = {

    # ── 5级设施 ──
    "奥术研究室": Facility(
        name="奥术研究室", name_en="Arcane Study", level=5,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.CRAFT,
        prerequisite="可以使用奥术法器或可以将工具作为施法法器",
        description="奥术研究室是一个安静的实验场所，包含一台或更多的书桌与书架。",
        effects=[
            "秘学护咒：在据点内长休后获得护咒，可施展一次鉴定术(Identify)，无需消耗法术位也无需材料成分。持续7天或至使用为止。",
            "制造选项：制造奥术法器(7天免费)、制造书卷(7天10GP)、9级+可制造普通/非普通奥秘魔法物品。",
        ],
    ),

    "军械库": Facility(
        name="军械库", name_en="Armory", level=5,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.TRADE,
        prerequisite="无",
        description="军械库包含展示盔甲的假人、悬挂盾牌的挂钩、存放武器的架子以及储存弹药的箱子。",
        effects=[
            "贸易：补充军械库。花费100GP基础费用，据点内每有一个据点卫兵额外花费100GP。若有铁匠铺则总价减半。",
            "补充后据点卫兵更难被杀死：决定卫兵损失的掷骰改用d8而非d6。事件结束后装备被消耗，需再次补货。",
        ],
    ),

    "兵营": Facility(
        name="兵营", name_en="Barrack", level=5,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.RECRUIT,
        prerequisite="无",
        description="每个兵营都安置了家具，可以作为至多十二名据点卫兵的宿舍。",
        effects=[
            "招募：据点卫兵。每次招募指令可招募至多四位据点卫兵，不花费金钱。兵营满员时不可再招募。",
            "记录每个兵营中的据点卫兵。损失卫兵时从名单中划掉。",
        ],
        can_enlarge=True,
        multiple_allowed=True,
    ),

    "种植园": Facility(
        name="种植园", name_en="Garden", level=5,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.HARVEST,
        prerequisite="无",
        description="每个据点可以拥有多个种植园。当一座种植园被加入据点时，从种植园类型表格中选择该种植园的类型。",
        effects=[
            "收获：种植园产物。委托雇员采收种植园的作物，需要7天且无需花费金钱。",
            "种植园类型：花园(花束/香水/蜡烛)、菜园(100天口粮)、草药园(急救包/治疗药水)、毒药园(抗毒剂/基础毒药)。",
            "扩大设施：花费2000GP将种植园扩大为庞大设施，功能等同于两个宽敞种植园，并获得一个额外雇员。",
        ],
        can_enlarge=True,
        multiple_allowed=True,
    ),

    "图书馆": Facility(
        name="图书馆", name_en="Library", level=5,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.RESEARCH,
        prerequisite="无",
        description="图书馆包含了一系列书籍收藏以及若干桌椅。",
        effects=[
            "调查：专题报告。委托雇员针对某个主题进行研究，需要7天时间。完成后获取三条之前不知道的有关该主题的信息。",
        ],
    ),

    "圣坛": Facility(
        name="圣坛", name_en="Sanctuary", level=5,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.CRAFT,
        prerequisite="可以将圣徽或德鲁伊法器作为施法法器",
        description="圣坛提供了一个安静的敬拜场所，你宗教的标志挂在圣坛的墙壁上。",
        effects=[
            "圣坛护咒：在据点内完成长休后获得护咒，可施展一次治愈真言(Healing Word)，无需消耗法术位。持续7天或至使用为止。",
            "制造：神圣法器。委托雇员制造德鲁伊法器(木杖)或圣徽，需要7天且无需花费金钱。",
        ],
    ),

    "铁匠铺": Facility(
        name="铁匠铺", name_en="Smithy", level=5,
        space=FacilitySpace.SPACIOUS, hirelings=2, order=OrderType.CRAFT,
        prerequisite="无",
        description="铁匠铺包含一座熔炉、一个铁砧、以及其他用于制造武器、盔甲等装备的工具。",
        effects=[
            "制造选项：制造铁匠工具(用铁匠工具制造的物品)、9级+可制造普通/非普通武具魔法物品。",
        ],
    ),

    "仓库": Facility(
        name="仓库", name_en="Storehouse", level=5,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.TRADE,
        prerequisite="无",
        description="仓库是一个凉爽而阴暗的空间，用于存放贸易物品。",
        effects=[
            "贸易：商品。委托雇员购买总价不超过500GP的非魔法物品(9级提升至2000GP，13级提升至5000GP)，或花费7天卖出储存的商品。",
            "出售商品时买家额外支付10%酬金(9级20%、13级50%、17级100%)。",
        ],
    ),

    "工坊": Facility(
        name="工坊", name_en="Workshop", level=5,
        space=FacilitySpace.SPACIOUS, hirelings=3, order=OrderType.CRAFT,
        prerequisite="无",
        description="工坊是充满创意的地方，许多有用的东西都能在这里制造。",
        effects=[
            "工匠工具：工坊被加入据点时，其内有六种工匠工具可供使用。",
            "制造选项：制造冒险装备(用工坊内已有的工匠工具)、9级+可制造普通/非普通器具魔法物品。",
            "灵感之源：在工坊内完成一次完整的短休后获得英雄激励(Heroic Inspiration)。完成长休前不能再次获得。",
            "扩大设施：花费2000GP将工坊扩大为庞大设施，获得额外两位雇员及额外三种工匠工具。",
        ],
        can_enlarge=True,
    ),

    # ── 9级设施 ──
    "游戏厅": Facility(
        name="游戏厅", name_en="Gaming Hall", level=9,
        space=FacilitySpace.VAST, hirelings=4, order=OrderType.TRADE,
        prerequisite="无",
        description="游戏厅提供娱乐活动，例如象棋、飞镖、卡牌或骰子。",
        effects=[
            "贸易：赌场。委托雇员将游戏厅变为赌场，持续7天。第七天结束时掷d100决定庄家赚取的钱：01-50得1d6*10GP，51-85得2d6*10GP，86-95得4d6*10GP，96-100得10d6*10GP。",
        ],
    ),

    "温室": Facility(
        name="温室", name_en="Greenhouse", level=9,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.HARVEST,
        prerequisite="无",
        description="温室是在受控气候下培育稀有真菌和植物的场所。",
        effects=[
            "复原之果：温室里的一株植物上长有三颗魔法果实。吃下果实的生物将获得次等复原术(Lesser Restoration)的增益。果实摘下后24小时内未食用则失去魔力。每天黎明重新长出被摘走的果实。",
            "收获选项：收获治疗草药(制作一瓶治疗药水(高等)，7天免费)、收获毒药(从稀有植物提取一剂毒药，7天免费)。",
        ],
    ),

    "实验室": Facility(
        name="实验室", name_en="Laboratory", level=9,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.CRAFT,
        prerequisite="无",
        description="实验室包含了存放炼金材料的储藏间以及制造各类调和物的工作间。",
        effects=[
            "制造选项：制造炼金工具(用炼金工具Alchemist's Supplies制造的物品)、制造毒药(焦引熏烟/乙醚精/蒙汗药，7天，支付毒药价格一半的成本)。",
        ],
    ),

    "圣器室": Facility(
        name="圣器室", name_en="Sacristy", level=9,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.CRAFT,
        prerequisite="可以将圣徽或德鲁伊法器作为施法法器",
        description="圣器室是圣物和宗教长袍的存放室和准备室。",
        effects=[
            "制造选项：制造圣水(7天免费，可额外花费最多500GP每100GP增加1d8伤害)、9级+可制造普通/非普通圣物魔法物品。",
            "法术刷新：建造圣器室后，若在整个短休期间待在据点内，可恢复一个五环或更低环阶的法术位。完成长休前不能再次获得。",
        ],
    ),

    "抄写室": Facility(
        name="抄写室", name_en="Scriptorium", level=9,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.CRAFT,
        prerequisite="无",
        description="抄写室包含桌子和书写工具。",
        effects=[
            "制造选项：制造书卷抄本(需一本空白的书，7天)、制造法术卷轴(包含一道牧师或法师法术，环位不超过3环，按制作装备规则的时间和金钱)、制造文书工作(最多50份单幅大报纸/纸质小册子，7天，每份1GP)。",
        ],
    ),

    "马厩": Facility(
        name="马厩", name_en="Stable", level=9,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.TRADE,
        prerequisite="无",
        description="每个据点可以拥有多个马厩，马厩在加入据点时默认带有一匹骑用马或骆驼，外加两匹矮种马或骡子。",
        effects=[
            "贸易：动物。委托雇员以常规价格购买或贩卖一只或更多坐骑，需要7天。出售坐骑时买家额外支付20%酬金(13级50%、17级100%)。",
            "扩大设施：花费2000GP将马厩扩大为庞大设施，可容纳六只大型动物。",
        ],
        can_enlarge=True,
        multiple_allowed=True,
    ),

    "传送法阵": Facility(
        name="传送法阵", name_en="Teleportation Circle", level=9,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.RECRUIT,
        prerequisite="无",
        description="一个由法术传送法阵(Teleportation Circle)制造的永久法阵铭刻在这个房间的地板上。",
        effects=[
            "招募：施法者。委托雇员向一位友善的非玩家角色发出邀请。掷一次骰，偶数则拒绝邀请，奇数则接受邀请并使用传送法阵来到据点。",
            "在你位于据点内时，可请求这位施法者为你施展一个不超过4环的法师法术(17级后提高到8环)。施法者会在14天后或为你施展一个法术后离开。",
        ],
    ),

    "剧场": Facility(
        name="剧场", name_en="Theater", level=9,
        space=FacilitySpace.VAST, hirelings=4, order=OrderType.EMPOWER,
        prerequisite="无",
        description="剧场包含一座舞台、一个用于存放道具和布景的后台区域、以及为一小群观众准备的观众席。",
        effects=[
            "增强：剧场演出。委托雇员编排一场戏剧或音乐会，排练需要14天，演出持续至少7天。",
            "参与方式：作曲家/作家(14天创作)、指挥家/导演(全程待在据点)、演奏家/演员(领衔主演)。",
            "排练结束时每个参与的角色进行DC15魅力(表演)检定。成功人数多于失败人数时，所有参与者获得一枚剧院骰(Theater die)。13级提升为d8，17级提升为d10。可在进行d20检定后立刻投掷剧院骰，将其结果加到检定结果上。",
        ],
    ),

    "训练场": Facility(
        name="训练场", name_en="Training Area", level=9,
        space=FacilitySpace.VAST, hirelings=4, order=OrderType.EMPOWER,
        prerequisite="无",
        description="每个据点可以拥有多个训练场。训练场可以是开放式庭院、体育场、歌舞厅、亦或是精心打造的充满陷阱和危险的试炼场。",
        effects=[
            "增强：训练。委托雇员开展7天训练课程。任何角色只要在这7天内每天花费至少8小时训练，即可在课程结束时获得增益。增益持续7天。",
            "专业教练类型：战斗专家(受到武器/徒手打击伤害时反应减少1d4)、技能专家(获得一项技能熟练)、工具专家(获得一项工具熟练)、徒手战斗专家(徒手打击命中额外1d4伤害)、武器专家(获得一种武器熟练或精通词条)。",
        ],
        multiple_allowed=True,
    ),

    "陈列室": Facility(
        name="陈列室", name_en="Trophy Room", level=9,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.RESEARCH,
        prerequisite="无",
        description="这个房间存放着一系列纪念品，譬如来自旧日战争的武器、猎物装裱好的头颅、在地城里捡到的小饰品、以及先祖流传下来的战利品。",
        effects=[
            "调查选项：调查学识(委托雇员针对某个主题进行研究，7天，获取三条之前不知道的信息)、调查饰品收藏(委托雇员寻找一件可能对你有用的饰品，7天，掷骰偶数则无所获，奇数则在第七章器具—普通表格中掷骰决定获得的物品)。",
        ],
    ),

    # ── 13级设施 ──
    "档案馆": Facility(
        name="档案馆", name_en="Archive", level=13,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.RESEARCH,
        prerequisite="无",
        description="档案馆是储存书籍，地图和卷轴的地方。它通常连接着一座图书馆，隔着一扇上锁的门或密门。",
        effects=[
            "调查：有益学识。委托雇员搜索档案馆，寻找需要的知识，需要7天。雇员将如同施展了通晓传奇(Legend Lore)法术那样获得相关知识。",
            "参考书：档案馆中存放了某本参考书的抄本，当你和这本书都位于据点内时赋予好处。可选：毕格比之手边奥术原典、库若尼普斯编年史、调查员的调查报告、对于世界本质的物质性思考、旧日信仰和其他宗教。",
            "扩大设施：花费2000GP将档案馆扩大为庞大设施，获得额外两本参考书。",
        ],
        can_enlarge=True,
    ),

    "冥想间": Facility(
        name="冥想间", name_en="Meditating Chamber", level=13,
        space=FacilitySpace.CRAMPED, hirelings=1, order=OrderType.EMPOWER,
        prerequisite="无",
        description="冥想间是一个让人放空心灵的地方，能帮助你心身合一，锻神定灵。",
        effects=[
            "增强：内心宁静。委托雇员使用冥想间获取内心的宁静。当你下次掷骰决定据点事件时，可以掷两次并选择其中一个结果。",
            "自我强化：在连续7天时间里在此设施内进行冥想。若在此期间离开了据点则不会获得增益。反之，在第七天结束时，于之后7天内在两种属性豁免上获得优势。掷d6两次随机决定获得哪两种属性豁免的优势(力量1/敏捷2/体质3/智力4/感知5/魅力6)，出现重复结果则重投。",
        ],
    ),

    "兽栏": Facility(
        name="兽栏", name_en="Menagerie", level=13,
        space=FacilitySpace.VAST, hirelings=2, order=OrderType.RECRUIT,
        prerequisite="无",
        description="兽栏有着足以容纳四只大型生物的围墙。每四只中型或小型生物在这里占据的空间等同于一只大型生物。",
        effects=[
            "招募：生物。委托雇员向兽栏内加入一只生物，从兽栏生物表格中选择。这项工作需要7天时间，所需金钱如表格所示。",
            "兽栏内的生物算作据点卫兵。如果它们遭受任何损失，便将损失的生物从据点卫兵名单中划去。你可以选择不将一只或更多生物视为据点卫兵。",
            "兽栏生物价格表：猿(中型)500GP、黑熊(中型)500GP、棕熊(大型)1000GP、蟒蛇(大型)250GP、鳄鱼(大型)500GP、恐狼(大型)1000GP、巨秃鹫(大型)1000GP、鬣狗(中型)50GP、豺狼(小型)50GP、狮子(大型)1000GP、枭熊(大型)3500GP、豹(中型)250GP、老虎(大型)1000GP。",
        ],
    ),

    "天文台": Facility(
        name="天文台", name_en="Observatory", level=13,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.EMPOWER,
        prerequisite="可以使用施法法器",
        description="天文台坐落在你据点的最高处，其中包含一座直指夜空的望远镜。",
        effects=[
            "天文护咒：可以用天文台观察到荒宇和星光位面的遥远角落。在据点内完成长休后获得护咒，可施展一次异界探知(Contact Other Plane)，无需消耗法术位。持续7天或至使用为止。",
            "增强：奇异发现。让自己或雇员在连续7天夜里探索星空之秘。结束后掷骰，偶数则一无所获，奇数则获得一个护咒(黑暗视觉护咒/英雄气概护咒/活力护咒之一)。",
        ],
    ),

    "酒馆": Facility(
        name="酒馆", name_en="Pub", level=13,
        space=FacilitySpace.SPACIOUS, hirelings=1, order=OrderType.RESEARCH,
        prerequisite="无",
        description="人们来到酒馆，饮用美酒，参与社交。你的酒馆可以是一个小酒吧、咖啡厅、或茶室。",
        effects=[
            "调查：情报收集。委托酒馆的酒保从情报网的间谍处收集情报。这些间谍对未来7天中将在据点周围10里内发生的重大事件了如指掌；也掌握未来7天内任何你熟知的生物的具体位置(只要该生物位于据点50里以内且未被魔法隐藏)。",
            "酒馆特饮：毕格比之重(喝下一品脱获得变大/缩小术中'变大'效应，持续24小时，无法豁免)、蛛后之吻(喝下一品脱获得蛛行术效应，持续24小时)。",
        ],
    ),

    # ── 17级设施 ──
    "圣物库": Facility(
        name="圣物库", name_en="Reliquary", level=17,
        space=FacilitySpace.CRAMPED, hirelings=1, order=OrderType.HARVEST,
        prerequisite="可以将圣徽或德鲁伊法器作为施法法器",
        description="这个宝库存放着神圣物件。",
        effects=[
            "圣物护咒：在据点内完成长休后获得护咒，可施展一次高等复原术(Greater Restoration)，无需消耗法术位也无需材料成分。持续7天或至使用为止。",
            "收获：护符。委托雇员对一枚护符进行祝圣然后交付给你，需要7天且不花费金钱。可用该护符替代任何一个法术的材料成分(价格不超过1000GP)。使用一次后不能再次使用，直至送回圣物库并重新下达收获指令。",
        ],
    ),

    "半位面": Facility(
        name="半位面", name_en="Demiplane", level=17,
        space=FacilitySpace.VAST, hirelings=1, order=OrderType.EMPOWER,
        prerequisite="可以使用奥术法器或可以将工具作为施法法器",
        description="一个至多5尺宽、10尺高的门出现在你据点里某个设施内的一个平坦、坚硬的表面。其位置由你选择。",
        effects=[
            "只有你和据点的雇员可以打开这扇门，它通往一个半位面，其形式类似于一个石质房间。半位面位于超维空间中，因此不在物理上与据点的其他部分相连。半位面本身和通往它的门都不能被解消。",
            "增强：奥术活力。委托雇员使魔法符文在半位面的墙壁上浮现，持续7天。在符文消失前，若在半位面内进行了一整个长休，将获得等同于等级5倍的临时生命值。",
            "造物：位于半位面内时，可以用一个魔法动作凭空创造一个非魔法物件(至多5尺长，价值不超过5GP，由木头/石头/黏土/陶瓷/纸张/无价值的水晶或非贵重金属构成)。完成长休前不能再次使用。",
        ],
    ),

    "公会大厅": Facility(
        name="公会大厅", name_en="GuildHall", level=17,
        space=FacilitySpace.VAST, hirelings=1, order=OrderType.RECRUIT,
        prerequisite="专精于一项技能",
        description="建立公会大厅意味着一个公会的成立，而你就是公会的会长。此设施是你公会的会议室。",
        effects=[
            "招募：公会任务。每当对此设施下达招募指令时，委托雇员招募公会成员执行一项特别任务。",
            "范例公会：冒险者公会(点燃的火炬，追捕CR不高于2的野兽，1d6+1天内杀死或捕获)、烘培师公会(甜点，为7天内的重要活动烘培食品，500GP报酬或人情)、酿酒师公会(冒泡的酒杯，7天内将50桶麦酒送到据点，每桶40加仑售价10GP)、石匠公会(石制面具，免费为据点建造防御墙，每5尺方格1天)、造船师公会(交叉的船桨，建造载具，每1000GP成本1天)、盗贼公会(白色的钥匙，渗透到据点50里内的地点偷窃一件非魔法物件，1d6+1天内送达)。",
        ],
    ),

    "圣所": Facility(
        name="圣所", name_en="Sanctum", level=17,
        space=FacilitySpace.SPACIOUS, hirelings=4, order=OrderType.EMPOWER,
        prerequisite="可以将圣徽或德鲁伊法器作为施法法器",
        description="圣所是提供抚慰和治愈的地方。",
        effects=[
            "圣所护咒：在据点内完成长休后获得护咒，可施展一次医疗术(Heal)，无需消耗法术位。持续7天或至使用为止。",
            "增强：韧性仪式。委托雇员每日进行祈祷仪式，增幅你或另一个生物的体魄。在仪式持续进行时，即使受益者不在据点内也能获得增益。在之后7天内，每当受益者完成一次长休，都会获得等同于等级的临时生命值。",
            "圣所回返：只要圣所仍然屹立，你便总是准备了法术回返真言(Word of Recall)。施展时可选择圣所作为目的地，并可选择由该法术传送到圣所的生物之一使其获得医疗术(Heal)的增益。",
        ],
    ),

    "作战指挥室": Facility(
        name="作战指挥室", name_en="War Room", level=17,
        space=FacilitySpace.VAST, hirelings=2, order=OrderType.RECRUIT,
        prerequisite="战斗风格特性或无甲防御特性",
        description="作战指挥室是你和你忠诚的副官们一起商讨作战计划的地方。每位副官都是身经百战的历战武者。",
        effects=[
            "招募选项：招募副官(获得一位新副官，最多同时拥有十名)、招募士兵(委托一位或更多副官集结一支小型军队，每位副官可在7天内召集最多100名守卫，或20名配备骑用马的骑兵)。",
            "你每天需要为军队内的每位士兵与每只马匹花费1GP以满足粮草供应。军队在任何时候都必须由你本人或至少一位副官领导着，没有领导者的军队会立即解散。在1天时间里没有获得粮草供应的军队也会立即解散。",
            "副官是雇员而非据点卫兵，但若据点遭受攻击，每位副官将使决定据点卫兵损失数量的掷骰中需要投掷的骰子数量减少1。",
        ],
    ),
}


# ──────────────────────────────────────────────────────────────────────────
# 基础设施
# 规则: DMG第八章 §3 基础设施
# 来源: topics/城主指南2024/8.据点/3.据点地图/基础设施.htm
# ──────────────────────────────────────────────────────────────────────────

BASIC_FACILITIES: list[str] = [
    "卧室",
    "餐厅",
    "客厅",
    "庭院",
    "厨房",
    "储藏室",
]

# 增添基础设施价格表
# 规则: DMG第八章 §3 增添基础设施
ADD_BASIC_FACILITY_COST: dict[FacilitySpace, tuple[int, int]] = {
    # (价格GP, 所需天数)
    FacilitySpace.CRAMPED:  (500, 20),
    FacilitySpace.SPACIOUS: (1000, 45),
    FacilitySpace.VAST:     (3000, 125),
}

# 扩大基础设施价格表
# 规则: DMG第八章 §3 扩大基础设施
ENLARGE_BASIC_FACILITY_COST: dict[tuple[FacilitySpace, FacilitySpace], tuple[int, int]] = {
    # (当前空间, 目标空间): (价格GP, 所需天数)
    (FacilitySpace.CRAMPED, FacilitySpace.SPACIOUS): (500, 25),
    (FacilitySpace.SPACIOUS, FacilitySpace.VAST):    (2000, 80),
}

# 扩大特色设施价格
# 规则: DMG第八章 §3 各特色设施描述中的"扩大设施"
ENLARGE_FACILITY_COST_GP = 2000


# ──────────────────────────────────────────────────────────────────────────
# 特色设施获取表
# 规则: DMG第八章 §3 特色设施获取
# 来源: topics/城主指南2024/8.据点/3.据点地图/特色设施/特色设施.htm
# ──────────────────────────────────────────────────────────────────────────

SPECIAL_FACILITY_ACQUISITION: dict[int, int] = {
    5:  2,   # 5级时拥有2个特色设施
    9:  4,   # 9级时拥有4个特色设施
    13: 5,   # 13级时拥有5个特色设施
    17: 6,   # 17级时拥有6个特色设施
}


def get_facility_count_for_level(level: int) -> int:
    """根据角色等级返回应拥有的特色设施数量。

    规则: DMG第八章 §3 特色设施获取表
      5级 → 2个
      9级 → 4个
      13级 → 5个
      17级 → 6个

    Args:
        level: 角色等级

    Returns:
        该等级应拥有的特色设施总数
    """
    if level < 5:
        return 0
    elif level < 9:
        return 2
    elif level < 13:
        return 4
    elif level < 17:
        return 5
    else:
        return 6


# ──────────────────────────────────────────────────────────────────────────
# 据点事件表
# 规则: DMG第八章 §4 据点事件
# 来源: topics/城主指南2024/8.据点/4.据点事件.htm
# ──────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class StrongholdEvent:
    """据点随机事件 — 规则: DMG第八章 §4 据点事件表

    Attributes:
        roll_min: d100最小值(含)
        roll_max: d100最大值(含)
        name: 事件名称
        name_en: 事件英文名
        description: 事件描述
    """
    roll_min: int
    roll_max: int
    name: str
    name_en: str
    description: str


STRONGHOLD_EVENTS: list[StrongholdEvent] = [
    StrongholdEvent(
        roll_min=1, roll_max=50,
        name="一切顺利", name_en="All Is Well",
        description="没什么大事发生。掷d8决定具体情况：1事故报告正在减少/2天花板上的漏水处被修复了/3没有发现鼠患的痕迹/4'那家伙'又把眼镜弄丢了/5你的一位雇员收养了一只流浪狗/6你收到了朋友写来的一封令人欣喜的信件/7某些爱开玩笑的人一直在往人们的鞋子里放臭鸡蛋/8有人声称自己看见了鬼魂。",
    ),
    StrongholdEvent(
        roll_min=51, roll_max=55,
        name="攻击", name_en="Attack",
        description="一股敌对势力袭击了据点，但是被打败了。投掷6d6；每有一个骰子丢出1，便有一位据点卫兵死亡。从据点卫兵名单中移除死亡的卫兵。如果据点内没有据点卫兵，那么据点的一个特色设施(随机决定)将遭受损害并被迫关闭。被关闭的特色设施在下个据点回合中无法使用，之后会被修复并重新开始运作，不花费任何金钱。",
    ),
    StrongholdEvent(
        roll_min=56, roll_max=58,
        name="罪犯雇员", name_en="Criminal Hireling",
        description="你据点的一位雇员以前犯下过罪行，但直到执法人员或者赏金猎人带着他的通缉令出现在据点门口时，大家才知道这件事。你可以贿赂他们1d6*100GP来保下这位雇员，否则这位雇员会被逮捕。如果这导致你的某个特色设施完全没有雇员在工作，那么该特色设施在下个据点回合中无法使用。之后，新的雇员会来接手工作，不花费任何金钱。",
    ),
    StrongholdEvent(
        roll_min=59, roll_max=63,
        name="机不可失", name_en="Extraordinary Opportunity",
        description="你的据点有机会承办一个重要的节目或庆典、资助一位强大施法者的研究、或者安抚一位蛮横的贵族。如果你抓住这次机会，必须花费500GP作为成本。作为回报，DM重新为你投掷一次据点事件(再次出现此结果则重投)。如果拒绝，无需花费金钱，无事发生。",
    ),
    StrongholdEvent(
        roll_min=64, roll_max=72,
        name="友好的来访者", name_en="Friendly Visitors",
        description="友好的来访者造访了你的据点，他们希望借用你据点的一个特色设施。他们愿意为此支付1d6*100GP。他们对特色设施的借用不会影响这些设施执行你下达的指令。",
    ),
    StrongholdEvent(
        roll_min=73, roll_max=76,
        name="客人", name_en="Guest",
        description="一位友好的客人来暂住在你的据点。掷d4决定来的是怎样的客人：1非常有名的人，暂住7天后给予你一封推荐信/2寻求庇护的客人，7天后离开前赠予你1d6*100GP作为礼物/3雇佣兵客人，给予你一位额外的据点卫兵，会一直待在这里直至被杀或直至你主动送他离开/4友善的怪物客人(如黄铜龙或树人)，若据点遭受攻击怪物会保护你的据点而你不会损失任何据点卫兵，怪物会一直呆在这里直至他保护一次你的据点或直至你主动送他离开。",
    ),
    StrongholdEvent(
        roll_min=77, roll_max=79,
        name="失去雇员", name_en="Lost Hirelings",
        description="你据点的其中一个特色设施(随机决定)失去了它的所有雇员。雇员离开的原因由你决定。该特色设施在下个据点回合中无法使用。之后，新的雇员会来接手工作，不花费任何金钱。",
    ),
    StrongholdEvent(
        roll_min=80, roll_max=83,
        name="魔法发现", name_en="Magical Discovery",
        description="你的雇员找到或意外创造了一件非普通(Uncommon)魔法物品。这不花费你任何金钱。该魔法物品由你选择，但必须是某种药剂(Potion)或卷轴(Scroll)。",
    ),
    StrongholdEvent(
        roll_min=84, roll_max=91,
        name="难民", name_en="Refugees",
        description="2d4名难民正在逃离怪物攻击、自然灾害、或其他灾难。他们希望在你的据点避难。如果你的据点没有足以容纳他们的基础设施，他们会在据点外扎营。难民们向你支付1d6*100GP作为你接纳并保护他们的报酬。他们会一直待在这里，直至你为他们找到新家，或直至敌对势力袭击你的据点。",
    ),
    StrongholdEvent(
        roll_min=92, roll_max=98,
        name="援助请求", name_en="Request for Aid",
        description="一位当地领导者号召你的据点为他提供助力。如果你选择帮助他，必须派出一位或更多据点卫兵。你每派出一名据点卫兵便投掷1d6。如果掷骰总和大于等于10，则问题被解决了，你获得1d6*100GP作为报酬。如果掷骰总和小于10，那么虽然问题仍然被解决了，但你获得的报酬减半，并且其中一位被派出的据点卫兵被杀死了。将该卫兵从你的据点卫兵名单中移除。",
    ),
    StrongholdEvent(
        roll_min=99, roll_max=100,
        name="宝藏", name_en="Treasure",
        description="你的据点获得了一件艺术品或一件魔法物品。掷d100决定类别：01-40投掷25GP艺术品表格/41-63投掷250GP艺术品表格/64-73投掷750GP艺术品表格/74-75投掷2500GP艺术品表格/76-90选择一张普通魔法物品表格(奥秘/武具/器具/圣物)并投掷/91-98选择一张非普通魔法物品表格并投掷/99-100选择一张珍稀魔法物品表格并投掷。据点获得这件物品的方式由你决定。如果你在据点里，立刻获得该物品。反之，该物品会被存放在储藏室，直至你前来获取它。",
    ),
]


def get_event_by_roll(d100_roll: int) -> StrongholdEvent:
    """根据d100掷骰结果返回对应的据点事件。

    规则: DMG第八章 §4 据点事件表

    Args:
        d100_roll: 1-100之间的整数

    Returns:
        对应的StrongholdEvent

    Raises:
        ValueError: 如果掷骰结果不在1-100范围内
    """
    if not 1 <= d100_roll <= 100:
        raise ValueError(f"d100掷骰结果必须在1-100范围内，得到: {d100_roll}")
    for event in STRONGHOLD_EVENTS:
        if event.roll_min <= d100_roll <= event.roll_max:
            return event
    # 理论上不会到达这里，因为事件表覆盖了1-100
    return STRONGHOLD_EVENTS[0]


def get_facility(name: str) -> Facility:
    """根据名称获取特色设施。

    Args:
        name: 设施中文名

    Returns:
        对应的Facility对象

    Raises:
        KeyError: 如果设施名称不存在
    """
    if name not in FACILITIES:
        raise KeyError(f"未知特色设施 {name!r}，可选: {list(FACILITIES)}")
    return FACILITIES[name]


def list_facilities_by_level(level: int) -> list[Facility]:
    """列出角色当前等级可获取的所有特色设施。

    规则: DMG第八章 §3 特色设施详述（每个设施标注所需等级）

    Args:
        level: 角色等级

    Returns:
        该等级可获取的特色设施列表
    """
    return [f for f in FACILITIES.values() if f.level <= level]
