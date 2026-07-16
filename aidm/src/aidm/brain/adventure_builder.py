"""冒险创建工具 — DMG 第四章「创建冒险」+ 第五章「创作战役」。

规则依据: 城主指南2024/4.创建冒险/
  - 冒险的设计步骤.htm        四步设计法（布置背景→导入玩家→规划遭遇→结束冒险）
  - 导入玩家/(赞助者/巧合/超自然).htm  三类引子表
  - 布置背景/(不同等级的冒险情景/冒险冲突/冒险设定).htm  按等级梯队的情景表
  - 规划遭遇/(战斗/交涉/探索)遭遇.htm   遭遇类型 + 人均XP预算表
  - 结束冒险/(收尾/结束冒险).htm       冒险高潮表

规则依据: 城主指南2024/5.创作战役/
  - 一步步建立战役.htm        战役四步设计法
  - 开始战役.htm              第零回 Session Zero
  - 你的战役日志.htm          战役日志维护
  - 战役背景/(奇幻风格/战役冲突/战役设定).htm  奇幻风格 + D&D设定表
  - 规划冒险/(单元剧和连续剧/让玩家投入/战役中的时间).htm  冒险间关联表

本模块提供:
  - create_adventure()      创建冒险（DMG 第四章四步法）
  - add_encounter()         添加遭遇（战斗/交涉/探索）
  - add_npc()               添加NPC
  - import_players()        生成引子（赞助者/巧合/超自然）
  - set_background()        设置背景与冲突
  - end_adventure()         结束冒险（高潮表 + 收尾）
  - generate_rewards()      生成冒险奖励（调用 loot.py）
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional

from . import loot as loot_mod


# ═══════════════════════════════════════════════════════════════════════════
# 数据表 — 从 DMG 第四五章 HTML 原文提取
# ═══════════════════════════════════════════════════════════════════════════

# ── 冒险设计四步法 ──────────────────────────────────────────────────────
# 规则依据: 城主指南2024/4.创建冒险/冒险的设计步骤.htm
ADVENTURE_STEPS = [
    {"step": 1, "name": "布置背景", "en": "Lay Out the Premise",
     "desc": "确定致使冒险发生的情景或冲突，考虑冒险的设定背景及其特色。"},
    {"step": 2, "name": "导入玩家", "en": "Draw In the Players",
     "desc": "想想角色将如何被卷入你所设定的情境中，将冒险与各个角色的目标结合。"},
    {"step": 3, "name": "规划遭遇", "en": "Plan Encounters",
     "desc": "确定角色们从冒险开始到结束期间经历的遭遇或事件。"},
    {"step": 4, "name": "结束冒险", "en": "Bring It to an End",
     "desc": "预想冒险的结局，以及将要给予角色们的奖励。"},
]

# ── 赞助者引子表 (d6) ───────────────────────────────────────────────────
# 规则依据: 城主指南2024/4.创建冒险/导入玩家/冒险赞助者.htm
PATRON_HOOKS = {
    1: "一个城镇布告员宣布有人正希望雇佣冒险者。",
    2: "角色们想要示好或需要寻求帮助的对象要求他们处理一个冒险情景。",
    3: "当角色们来到一个新城市时，他们找到一个招聘栏，上面发布着征集冒险者的消息。",
    4: "一个了解到冒险者们的功绩的富有赞助者给他们写了一份信，愿意为他们的才能买单。",
    5: "一个需要帮助的市民在了解到冒险者们的功绩和善举后，不远千里来找到他们，寻求他们的帮助。",
    6: "冒险者们被捕（罪名可以成立或捏造），并有机会通过完成一项任务来逃脱责罚。",
}

# ── 巧合引子表 (d6) ─────────────────────────────────────────────────────
# 规则依据: 城主指南2024/4.创建冒险/导入玩家/巧合引子.htm
HAPPENSTANCE_HOOKS = {
    1: "角色们找到一封信，信中描述了冒险的情况。",
    2: "角色们正在执行一项毫不相干的任务，例如正在搜索一件魔法物品，然后这个任务带领他们进入了冒险情景。",
    3: "冒险情景扰乱了角色们正在参与的节庆或仪式。",
    4: "一场魔法事故将角色们直接置于冒险情景之中。",
    5: "在商队或船上旅行时，角色们会结识一位了解一些冒险情景的NPC角色。",
    6: "角色们因为被误认为是另一群冒险者，而遭到了袭击。他们从袭击者留下的线索中了解到冒险情景。",
}

# ── 超自然引子表 (d6) ───────────────────────────────────────────────────
# 规则依据: 城主指南2024/4.创建冒险/导入玩家/超自然引子.htm
SUPERNATURAL_HOOKS = {
    1: "角色们都做了一个逼真的梦，梦境预示了冒险的内容。",
    2: "在准备法术时，一个角色收到了来自神明或赞助者的委托。",
    3: "一个占卜术算出其中一名角色的未来将会指向一项任务，同时他也提供了一些关于前路上挑战的提示。",
    4: "火焰、云层、烟雾或是庞大的鸟群表现出怪异的形状，预示着冒险的情景。",
    5: "动物或活化的物件向冒险者们口吐人言，清晰地把他们引向一个冒险情景。",
    6: "某个已死之人以鬼魂的形态回到现世并在角色们身边作祟。它的出现导致角色们前去调查它的死因并让它得以安息。",
}

# 引子方法 → 表映射
HOOK_TABLES = {
    "sponsor": PATRON_HOOKS,
    "coincidence": HAPPENSTANCE_HOOKS,
    "supernatural": SUPERNATURAL_HOOKS,
}

# ── 不同等级的冒险情景表 ─────────────────────────────────────────────────
# 规则依据: 城主指南2024/4.创建冒险/布置背景/不同等级的冒险情景.htm

# 等级1-4：小城英雄 (d20)
LOCAL_HERO_SITUATIONS = {
    1: "一头雏龙召集了一群狗头人来为它囤积秘宝。",
    2: "一群栖身于城市下水道中的鼠人密谋要接管城市理事会。",
    3: "强盗近期的活动揭示出一个早已被赶出该地区的邪恶教团即将卷土重来。",
    4: "一群危险的鬣狗人正在当地的农田附近肆虐。",
    5: "一对商贾世家竞争对手的矛盾从小打小闹升级为了一场骚乱。",
    6: "一个新坑洞的出现带出了一个埋藏已久的地城，据说里面埋藏着宝藏。",
    7: "一群发现了一座地下废墟的矿工被栖息在那里的怪物抓走了。",
    8: "一个无辜之人被一只变形生物嫁祸陷害。",
    9: "一群食尸鬼在夜里爬出了墓穴。",
    10: "一个臭名昭著的罪犯为了逃避法律的制裁，藏身在了一个古老的废墟或废弃的矿井中。",
    11: "一种肆虐于森林中的疫病正在将蜘蛛们变得巨大且极具攻击性。",
    12: "一个死灵师为了报复村里人对他的轻视，正在将村庄墓地中的尸体活化。",
    13: "一个邪教组织正在一个村庄里兴风作浪。那些忤逆他们的人都被当做了祭品。",
    14: "一栋小镇边陲的废弃房屋正在因屋内的一件诅咒物品而受到亡灵的侵扰。",
    15: "来自妖精荒野的生物闯入了这个世界，给许多村民和牲畜招致了灾祸和不幸。",
    16: "一个鬼婆的诅咒正在将动物们变得异常具有攻击性。",
    17: "一群恶棍自封为村里的民兵，正在向村民勒索钱财和食物。",
    18: "在一个当地渔民将一尊诡异雕像拉上岸后，水生的怪物们就开始在夜间袭击海岸。",
    19: "小镇旁山丘上的废墟正处于诅咒之中，因此人们不会前往那里——除了一位打算研究遗迹的学者。",
    20: "一个新领袖接管了一群海盗或强盗，他们正在更加频繁地发动袭击。",
}

# 等级5-10：全境英雄 (d20)
REALM_HERO_SITUATIONS = {
    1: "一群邪教徒召唤了一只恶魔，并在城市中制造混乱。",
    2: "反叛军引来了怪物，意图掠夺王之宝库。",
    3: "一件邪恶的神器将一片森林变为了一片死气沉沉、充满恐怖怪物的沼泽。",
    4: "一只栖息在幽暗地域的异怪将它的仆从送上地表，并在地表捕捉普通人，将他们变为自己新的仆从。",
    5: "一只怪物（也许是一只魔鬼，史拉蟾，或者鬼婆）假冒成了一名声名显赫的贵族，以将它所在的国家推入内战。",
    6: "一名窃贼大师打算盗走皇家徽章。",
    7: "一个本该作为守卫存在的魔像突然暴走并挟持了它的制作者。",
    8: "一群间谍、刺客和死灵师正在合谋推翻一位统治者。",
    9: "一头建立了巢穴的青年龙试图向居住在周边地区的生物散播恐惧并收获敬畏。",
    10: "一个孤单的巨人的到来惊动了小镇上的人们，但这个巨人其实只是在寻找一个安居之所。",
    11: "一头被圈养起来的巨大怪物挣脱了樊笼并陷入了暴走。",
    12: "一群鬼婆偷走了很多旅行者的珍贵记忆。",
    13: "一个反派在一座古老的遗迹中寻找强大的魔法，妄图利用它征服整个国家。",
    14: "一位富于心计的贵族举办了一场化妆舞会，许多宾客都将这个舞会视为实现自己野心的契机。但是在这场舞会中也出席了至少一只变形怪。",
    15: "一艘运载着一件珍贵宝藏或邪恶神器的船在一场风暴或怪物的袭击中沉没了。",
    16: "一种实则由出错的魔法或邪教徒的邪恶计划所引发的自然灾害正在肆虐。",
    17: "一个秘密邪教利用间谍在两个对立国家间挑拨矛盾，妄图引发战争并削弱两国的力量。",
    18: "一支叛军或敌国军队绑架了一位重要的贵族。",
    19: "一群背井离乡的族裔后代想要夺回他们祖先的城市，而这座城市现在已经被怪物所占据。",
    20: "一群声名远扬的冒险者在前往了一处知名遗迹后再也没回来。",
}

# 等级11-16：全境至尊 (d12)
MASTER_REALM_SITUATIONS = {
    1: "通往深渊的传送门于诅咒之地开启，恶魔从中倾巢而出。",
    2: "一群狩猎中的巨人把它们的猎物——一群无比巨大的野兽——赶入了一个牧场。",
    3: "一头成年龙的巢穴正在将一大块地区变成一个环境恶劣、对其他生物来说难以生存的地方。",
    4: "一本失落已久的日志中记录着一段奇妙的旅程，那是一个隐秘的地底国度，其中充满了魔法奇迹。",
    5: "邪教徒妄图说服一头龙接受他们的仪式，并将其变为一个龙巫妖。",
    6: "国度的统治者正在派遣使者前往敌对的邻国商谈停战事宜，而这位大使需要有人来保护他。",
    7: "一座城堡或城市被拖入了另一个存在位面。",
    8: "一场风暴席卷了大地，而在风暴的中心有一座神秘的飞行城堡。",
    9: "一个魔法物品的两个部件落在了一对仇敌手里，而第三个部件则遗失了。",
    10: "邪恶的教徒从全世界聚集到一起，想要召唤一个恐怖神明或异域存在的实体。",
    11: "一位暴君禁止魔法在未经官方批准的情况下使用。而一个由施法者组成的秘密组织正在试图推翻这位暴君。",
    12: "在一场大旱期间，一个水位降低的湖泊揭露出了一座不为人知的古代遗迹，其中蕴藏着强大的邪恶力量。",
}

# 等级17-20：世界至尊 (d10)
MASTER_WORLD_SITUATIONS = {
    1: "一头远古龙正在暗中计划毁灭一位神明，并取代他在神系中的位置。巨龙的爪牙正在寻找能够召唤和削弱这位神明的神器。",
    2: "一群巨人赶走了一头金属龙，占领了它的巢穴，而巨龙想要夺回巢穴。",
    3: "一位远古时期的英雄从死亡中归来，他在为世界做好准备，来迎接一个和他同样古老的怪物的归来。",
    4: "一件上古神器拥有着足以击败或囚禁一个暴走的泰坦的力量。",
    5: "一位农业之神陷入了愤怒，致使河流干涸、作物枯萎。",
    6: "一件原本属于一位神明的神器落入了一个凡人的手中。",
    7: "一个被囚禁于幽暗地域中的泰坦正在挣脱束缚，这引发了剧烈的地震，如果他被释放出来，这将只是泰坦会造成的破坏中的九牛一毛。",
    8: "一个巫妖在试图消灭任何接近他实力的施法者。",
    9: "从前有一座圣殿被建在了通往一个下层位面的传送门周围，它是被用来防止任何邪恶力量从任一位面穿过传送门而存在的。而现在，圣殿已经受到了来自双向的围攻。",
    10: "有五条古老的金属龙在创生之柱中筑巢。如果这些龙被杀死，世界将真正地崩溃，陷入混沌。而现在其中一头已经被杀。",
}

# 等级梯队 → 情景表映射
LEVEL_TIER_SITUATIONS = {
    "local_hero": LOCAL_HERO_SITUATIONS,       # 等级1-4
    "realm_hero": REALM_HERO_SITUATIONS,       # 等级5-10
    "master_realm": MASTER_REALM_SITUATIONS,   # 等级11-16
    "master_world": MASTER_WORLD_SITUATIONS,   # 等级17-20
}

# ── 冒险高潮表 (d10) ─────────────────────────────────────────────────────
# 规则依据: 城主指南2024/4.创建冒险/结束冒险/结束冒险.htm
ADVENTURE_CLIMAXES = {
    1: "冒险者们和大反派以及他手下的爪牙展开最终决战。",
    2: "冒险者们一边追逐大反派，一边躲避着企图阻挠他们的障碍，最终他们在反派的基地里展开了最终决战。",
    3: "冒险者们或者大反派的行动最终导致了一场灾难的发生，冒险者们必须逃离这场灾难。",
    4: "冒险者们争分夺秒地赶向了一个地点，而大反派正在那里实施他计划的最后一步，当冒险者们抵达时，这个计划已经临近完成。",
    5: "大反派和他的两或三名副手正在一个大房间里分头举行仪式。冒险者必须破坏每个仪式。",
    6: "就在冒险者们将要完成他们的目标时，一个盟友背叛了他们。（谨慎地使用这个高潮，切忌滥用。）",
    7: "一个通向另一存在位面的传送门开启了。另一位面的生物倾巢而出，迫使冒险者们一边关闭传送门，一边处理大反派。",
    8: "地下城开始坍塌而大反派则企图在一片混乱中逃走。",
    9: "冒险者们必须选择去追赶一个正在逃跑的反派还是拯救一个他们所关心的NPC或一群无辜者。",
    10: "就在冒险者们以为主要威胁已经被击败的时候，它变为了另一头怪物或者一个更强大的形态。",
}

# ── 人均经验值预算表 ─────────────────────────────────────────────────────
# 规则依据: 城主指南2024/4.创建冒险/规划遭遇/战斗遭遇.htm
# 格式: {角色等级: {"low": XP, "moderate": XP, "high": XP}}
XP_BUDGET_PER_CHARACTER = {
    1:  {"low": 50,    "moderate": 75,    "high": 100},
    2:  {"low": 100,   "moderate": 150,   "high": 200},
    3:  {"low": 150,   "moderate": 225,   "high": 400},
    4:  {"low": 250,   "moderate": 375,   "high": 500},
    5:  {"low": 500,   "moderate": 750,   "high": 1100},
    6:  {"low": 600,   "moderate": 1000,  "high": 1400},
    7:  {"low": 750,   "moderate": 1300,  "high": 1700},
    8:  {"low": 1000,  "moderate": 1700,  "high": 2100},
    9:  {"low": 1300,  "moderate": 2000,  "high": 2600},
    10: {"low": 1600,  "moderate": 2300,  "high": 3100},
    11: {"low": 1900,  "moderate": 2900,  "high": 4100},
    12: {"low": 2200,  "moderate": 3700,  "high": 4700},
    13: {"low": 2600,  "moderate": 4200,  "high": 5400},
    14: {"low": 2900,  "moderate": 4900,  "high": 6200},
    15: {"low": 3300,  "moderate": 5400,  "high": 7800},
    16: {"low": 3800,  "moderate": 6100,  "high": 9800},
    17: {"low": 4500,  "moderate": 7200,  "high": 11700},
    18: {"low": 5000,  "moderate": 8700,  "high": 14200},
    19: {"low": 5500,  "moderate": 10700, "high": 17200},
    20: {"low": 6400,  "moderate": 13200, "high": 22000},
}

# ── 随机个体宝藏表 ───────────────────────────────────────────────────────
# 规则依据: 城主指南2024/4.创建冒险/冒险奖励.htm
INDIVIDUAL_TREASURE_TABLE = {
    "0-4":   {"dice": "3d6",    "avg": 10,    "unit": "GP"},
    "5-10":  {"dice": "2d8x10", "avg": 90,    "unit": "GP"},
    "11-16": {"dice": "2d10x10","avg": 110,   "unit": "PP"},
    "17+":   {"dice": "2d8x100","avg": 900,   "unit": "PP"},
}

# ── 随机库藏宝藏表 ───────────────────────────────────────────────────────
# 规则依据: 城主指南2024/4.创建冒险/冒险奖励.htm
TREASURE_HOARD_TABLE = {
    "0-4":   {"dice": "2d4x100",   "avg": 500,    "magic_items": "1d4-1"},
    "5-10":  {"dice": "8d10x100",  "avg": 4400,   "magic_items": "1d3"},
    "11-16": {"dice": "8d8x1000",  "avg": 36000,  "magic_items": "1d4"},
    "17+":   {"dice": "6d10x10000","avg": 330000, "magic_items": "1d6"},
}

# ── 冒险间的关联表 (d6) ──────────────────────────────────────────────────
# 规则依据: 城主指南2024/5.创作战役/规划冒险/单元剧和连续剧.htm
ADVENTURE_CONNECTIONS = {
    1: "引入某个人物、某个物件、或是某条信息；角色们需要将这一事物安全转运到涉及新的冒险的地点。",
    2: "让一个主要反派逃到会在新的冒险中出现的一处地点。角色们也许能直接追到这个地点去和这位反派对峙，亦或是必须先想办法弄清楚它逃到了哪里。",
    3: "给出一些线索，让角色们意识到当前冒险中的某位反派或其他NPC其实属于某个更大的团体——一个将在新的冒险中活跃的团体。",
    4: "通过派出特工监视或干扰角色们的行动，来让他们意识到一个将在新的冒险中活跃的反派组织的存在。",
    5: "旅行者带来关于其他地方发生的事情的新消息，引导玩家进入新的冒险。",
    6: "给予角色们一件被谜团包裹的宝藏，而这些谜团需要在新的冒险中解开。",
}


# ═══════════════════════════════════════════════════════════════════════════
# 数据结构
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Hook:
    """冒险引子 — DMG 第四章「导入玩家」。

    规则依据: 城主指南2024/4.创建冒险/导入玩家/导入玩家.htm
      - sponsor:     赞助者引子（冒险赞助者.htm）
      - coincidence: 巧合引子（巧合引子.htm）
      - supernatural:超自然引子（超自然引子.htm）
    """
    method: str           # sponsor / coincidence / supernatural
    description: str      # 引子文本
    roll: int = 0         # 骰点结果

    def to_dict(self) -> dict:
        return {"method": self.method, "description": self.description, "roll": self.roll}


@dataclass
class Background:
    """冒险背景 — DMG 第四章「布置背景」。

    规则依据: 城主指南2024/4.创建冒险/布置背景/布置背景.htm
      - conflict: 冒险冲突（冒险冲突.htm）
      - setting:  冒险设定（冒险设定.htm）
    """
    premise: str = ""          # 冒险前提
    conflict: str = ""         # 冒险冲突
    setting: str = ""          # 冒险设定（地下城/荒野/聚落）
    situation: str = ""        # 按等级梯队掷出的冒险情景
    tier: str = ""             # 等级梯队 key

    def to_dict(self) -> dict:
        return {
            "premise": self.premise, "conflict": self.conflict,
            "setting": self.setting, "situation": self.situation, "tier": self.tier,
        }


@dataclass
class NPC:
    """非玩家角色 — DMG 第四章「布置背景/栖身于冒险地点中的生物」。"""
    name: str
    role: str = ""             # 赞助者/反派/盟友/中立
    description: str = ""
    location: str = ""

    def to_dict(self) -> dict:
        return {"name": self.name, "role": self.role, "description": self.description,
                "location": self.location}


@dataclass
class Encounter:
    """遭遇 — DMG 第四章「规划遭遇」。

    规则依据: 城主指南2024/4.创建冒险/规划遭遇/规划遭遇.htm
      - combat:     战斗遭遇（战斗遭遇.htm）
      - social:     交涉遭遇（交涉遭遇.htm）
      - exploration:探索遭遇（探索遭遇.htm）
    """
    encounter_type: str       # combat / social / exploration
    difficulty: str = ""      # low / moderate / high（仅战斗遭遇）
    description: str = ""
    monsters: list[dict] = field(default_factory=list)  # [{name, cr, xp, count}]
    xp_budget: int = 0        # 经验值预算（战斗遭遇）
    xp_spent: int = 0         # 已花费XP

    def to_dict(self) -> dict:
        return {
            "encounter_type": self.encounter_type, "difficulty": self.difficulty,
            "description": self.description, "monsters": self.monsters,
            "xp_budget": self.xp_budget, "xp_spent": self.xp_spent,
        }


@dataclass
class Ending:
    """冒险结局 — DMG 第四章「结束冒险」。

    规则依据: 城主指南2024/4.创建冒险/结束冒险/结束冒险.htm
      - climax:    冒险高潮（冒险高潮表 d10）
      - denouement:收尾（收尾.htm）
    """
    method: str               # resolution / cliffhanger
    climax: str = ""          # 高潮描述
    denouement: str = ""      # 收尾描述
    rewards: Optional[dict] = None  # 冒险奖励

    def to_dict(self) -> dict:
        return {
            "method": self.method, "climax": self.climax,
            "denouement": self.denouement, "rewards": self.rewards,
        }


@dataclass
class Adventure:
    """冒险 — DMG 第四章「创建冒险」。

    规则依据: 城主指南2024/4.创建冒险/创建冒险.htm
      创作一场冒险需要将探索、社交和战斗融合为一个迎合玩家和战役需求的整体。
    """
    id: str                              # 冒险唯一标识
    name: str                            # 冒险名称
    level_range: tuple[int, int] = (1, 4)# 角色等级范围
    setting: str = ""                    # 冒险设定
    hook: Optional[Hook] = None          # 导入玩家引子
    background: Optional[Background] = None  # 布置背景
    npcs: list[NPC] = field(default_factory=list)      # NPC列表
    encounters: list[Encounter] = field(default_factory=list)  # 遭遇列表
    ending: Optional[Ending] = None      # 结束冒险
    rewards: Optional[dict] = None       # 冒险奖励
    design_steps: list[dict] = field(default_factory=lambda: [s for s in ADVENTURE_STEPS])

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name,
            "level_range": list(self.level_range),
            "setting": self.setting,
            "hook": self.hook.to_dict() if self.hook else None,
            "background": self.background.to_dict() if self.background else None,
            "npcs": [n.to_dict() for n in self.npcs],
            "encounters": [e.to_dict() for e in self.encounters],
            "ending": self.ending.to_dict() if self.ending else None,
            "rewards": self.rewards,
            "design_steps": self.design_steps,
        }


# ═══════════════════════════════════════════════════════════════════════════
# 核心函数
# ═══════════════════════════════════════════════════════════════════════════

def _level_to_tier(level: int) -> str:
    """将角色等级映射到等级梯队。

    规则依据: 城主指南2024/4.创建冒险/布置背景/不同等级的冒险情景.htm
      等级1-4:   local_hero  （小城英雄）
      等级5-10:  realm_hero  （全境英雄）
      等级11-16: master_realm（全境至尊）
      等级17-20: master_world（世界至尊）

    Args:
        level: 角色等级 (1-20)

    Returns:
        等级梯队 key

    Raises:
        ValueError: 等级超出 1-20 范围
    """
    if level < 1 or level > 20:
        raise ValueError(f"角色等级必须在1-20之间，实际: {level}")
    if level <= 4:
        return "local_hero"
    elif level <= 10:
        return "realm_hero"
    elif level <= 16:
        return "master_realm"
    else:
        return "master_world"


def _roll_table(table: dict[int, str], rng: random.Random) -> tuple[int, str]:
    """从 dN 表中随机掷一条。

    Args:
        table: {骰点: 文本} 字典
        rng:   随机数生成器

    Returns:
        (骰点, 文本)
    """
    roll = rng.randint(1, len(table))
    return roll, table[roll]


def create_adventure(name: str,
                     level_range: tuple[int, int] = (1, 4),
                     setting: str = "",
                     seed: Optional[int] = None) -> Adventure:
    """创建冒险 — DMG 第四章四步设计法第1步「布置背景」。

    规则依据: 城主指南2024/4.创建冒险/冒险的设计步骤.htm
      第1步：布置背景 — 确定致使冒险发生的情景或冲突。

    流程:
      1. 生成冒险ID
      2. 根据等级范围掷出冒险情景（不同等级的冒险情景表）
      3. 设置冒险设定（地下城/荒野/聚落）
      4. 返回 Adventure 对象（hook/background 待后续填充）

    Args:
        name:       冒险名称
        level_range: 角色等级范围 (min, max)
        setting:    冒险设定描述
        seed:       随机种子（测试用）

    Returns:
        Adventure 对象
    """
    rng = random.Random(seed) if seed is not None else random.Random()

    # 生成冒险ID
    adv_id = f"adv_{rng.randint(10000, 99999)}"

    # 根据等级范围的中位数确定梯队
    avg_level = (level_range[0] + level_range[1]) // 2
    tier = _level_to_tier(avg_level)

    # 掷出冒险情景
    situation_table = LEVEL_TIER_SITUATIONS[tier]
    _, situation = _roll_table(situation_table, rng)

    # 创建背景
    background = Background(
        premise=f"{name}的冒险前提",
        conflict="待设定",
        setting=setting or "地下城",
        situation=situation,
        tier=tier,
    )

    return Adventure(
        id=adv_id,
        name=name,
        level_range=level_range,
        setting=setting,
        background=background,
    )


def import_players(method: str = "sponsor",
                   seed: Optional[int] = None) -> Hook:
    """生成导入玩家引子 — DMG 第四章四步设计法第2步「导入玩家」。

    规则依据: 城主指南2024/4.创建冒险/导入玩家/导入玩家.htm
      - sponsor:      赞助者引子（冒险赞助者.htm，d6表）
      - coincidence:  巧合引子（巧合引子.htm，d6表）
      - supernatural: 超自然引子（超自然引子.htm，d6表）

    Args:
        method: 引子方法 (sponsor/coincidence/supernatural)
        seed:   随机种子（测试用）

    Returns:
        Hook 对象

    Raises:
        ValueError: 未知引子方法
    """
    if method not in HOOK_TABLES:
        raise ValueError(f"未知引子方法: {method}，可选: {list(HOOK_TABLES)}")

    rng = random.Random(seed) if seed is not None else random.Random()
    table = HOOK_TABLES[method]
    roll, desc = _roll_table(table, rng)

    return Hook(method=method, description=desc, roll=roll)


def set_background(adventure: Adventure,
                   conflict: str = "",
                   setting: str = "",
                   premise: str = "") -> Background:
    """设置冒险背景与冲突 — DMG 第四章「布置背景」。

    规则依据: 城主指南2024/4.创建冒险/布置背景/冒险冲突.htm
      背景可以为冒险创造一个很好的起点，但在将其转变为一场冒险之前，
      还需要一个值得英雄们关注的冲突。

    规则依据: 城主指南2024/4.创建冒险/布置背景/冒险设定.htm
      许多D&D冒险都是通过地下城空间展开的……当然，并不是所有冒险都会发生于地下城。

    Args:
        adventure: 冒险对象
        conflict:  冒险冲突描述
        setting:   冒险设定（地下城/荒野/聚落）
        premise:   冒险前提描述

    Returns:
        更新后的 Background 对象
    """
    if adventure.background is None:
        adventure.background = Background()

    bg = adventure.background
    if premise:
        bg.premise = premise
    if conflict:
        bg.conflict = conflict
    if setting:
        bg.setting = setting
        adventure.setting = setting

    return bg


def add_encounter(adventure: Adventure,
                  encounter_type: str,
                  difficulty: str = "moderate",
                  description: str = "",
                  party_level: int = 1,
                  party_size: int = 4,
                  monsters: Optional[list[dict]] = None) -> Encounter:
    """添加遭遇到冒险 — DMG 第四章四步设计法第3步「规划遭遇」。

    规则依据: 城主指南2024/4.创建冒险/规划遭遇/规划遭遇.htm
      遭遇就是一个设有障碍的目标。它起到以下一个或多个作用：
      让角色们更接近于实现目标 / 阻碍角色们实现目标 / 揭示新的信息。

    规则依据: 城主指南2024/4.创建冒险/规划遭遇/战斗遭遇.htm
      - 第1步：选择难度（low/moderate/high）
      - 第2步：决定XP预算（人均XP预算表 × 角色数）
      - 第3步：花费预算（每个生物在其资料板中都有一个XP价值）

    Args:
        adventure:       冒险对象
        encounter_type:  遭遇类型 (combat/social/exploration)
        difficulty:      难度 (low/moderate/high)，仅战斗遭遇
        description:     遭遇描述
        party_level:     小队等级（用于计算XP预算）
        party_size:      小队人数（用于计算XP预算）
        monsters:        怪物列表 [{name, cr, xp, count}]

    Returns:
        Encounter 对象

    Raises:
        ValueError: 未知遭遇类型或难度
    """
    valid_types = {"combat", "social", "exploration"}
    if encounter_type not in valid_types:
        raise ValueError(f"未知遭遇类型: {encounter_type}，可选: {sorted(valid_types)}")

    valid_diffs = {"low", "moderate", "high"}
    if encounter_type == "combat" and difficulty not in valid_diffs:
        raise ValueError(f"未知难度: {difficulty}，可选: {sorted(valid_diffs)}")

    enc = Encounter(
        encounter_type=encounter_type,
        difficulty=difficulty if encounter_type == "combat" else "",
        description=description,
        monsters=monsters or [],
    )

    # 战斗遭遇：计算XP预算
    if encounter_type == "combat":
        if party_level < 1 or party_level > 20:
            raise ValueError(f"小队等级必须在1-20之间，实际: {party_level}")

        budget_table = XP_BUDGET_PER_CHARACTER.get(party_level)
        if budget_table is None:
            raise ValueError(f"不支持的小队等级: {party_level}")

        per_char_xp = budget_table[difficulty]
        enc.xp_budget = per_char_xp * party_size

        # 计算已花费XP
        for m in enc.monsters:
            xp = m.get("xp", 0)
            count = m.get("count", 1)
            enc.xp_spent += xp * count

    adventure.encounters.append(enc)
    return enc


def add_npc(adventure: Adventure,
            name: str,
            role: str = "",
            description: str = "",
            location: str = "") -> NPC:
    """添加NPC到冒险 — DMG 第四章「布置背景/栖身于冒险地点中的生物」。

    规则依据: 城主指南2024/4.创建冒险/布置背景/冒险设定.htm
      任何栖身于冒险地点中的怪物都不会仅是碰巧在附近生活的随机生物集群。
      ……智慧生物也可以通过协商和地位统治的方式来共享生存空间。

    Args:
        adventure:    冒险对象
        name:         NPC名称
        role:         NPC角色（赞助者/反派/盟友/中立）
        description:  NPC描述
        location:     NPC所在位置

    Returns:
        NPC 对象
    """
    npc = NPC(
        name=name,
        role=role,
        description=description,
        location=location,
    )
    adventure.npcs.append(npc)
    return npc


def end_adventure(adventure: Adventure,
                  method: str = "resolution",
                  climax_roll: Optional[int] = None,
                  seed: Optional[int] = None) -> Ending:
    """结束冒险 — DMG 第四章四步设计法第4步「结束冒险」。

    规则依据: 城主指南2024/4.创建冒险/结束冒险/结束冒险.htm
      冒险的高潮收尾是对此前所经历的所有承诺的兑现。
      最完美的高潮是可以让玩家所预料到的。
      使用冒险高潮表(d10)提供塑造冒险结尾的建议。

    规则依据: 城主指南2024/4.创建冒险/结束冒险/收尾.htm
      收尾(Denouement)：在故事的高潮过去之后仍会衔接一段内容，
      期间，原本分散的情节和线索会被串联起来，最终让故事中发生的一切都得到解释。

    Args:
        adventure:    冒险对象
        method:       结束方式 (resolution=圆满收尾 / cliffhanger=悬念结尾)
        climax_roll:  手动指定高潮骰点(1-10)，None则随机
        seed:         随机种子（测试用）

    Returns:
        Ending 对象

    Raises:
        ValueError: 未知结束方式或高潮骰点越界
    """
    valid_methods = {"resolution", "cliffhanger"}
    if method not in valid_methods:
        raise ValueError(f"未知结束方式: {method}，可选: {sorted(valid_methods)}")

    rng = random.Random(seed) if seed is not None else random.Random()

    # 掷冒险高潮表
    if climax_roll is not None:
        if climax_roll < 1 or climax_roll > 10:
            raise ValueError(f"高潮骰点必须在1-10之间，实际: {climax_roll}")
        roll = climax_roll
    else:
        roll = rng.randint(1, 10)

    climax = ADVENTURE_CLIMAXES[roll]

    # 收尾描述
    if method == "resolution":
        denouement = (
            "冒险的高潮过后，原本分散的情节和线索被串联起来，"
            "故事中发生的一切都得到了解释。角色们清剿宝藏、"
            "参加授勋仪式，或悼念未能幸存的同伴。"
        )
    else:
        denouement = (
            "冒险以悬念结尾：一条未解的线索指向下一场冒险，"
            "角色们在高潮中发现了更深层的阴谋。"
        )

    ending = Ending(
        method=method,
        climax=climax,
        denouement=denouement,
    )

    adventure.ending = ending
    return ending


def generate_rewards(cr_list: list[float],
                     include_magic_items: bool = True,
                     seed: Optional[int] = None) -> dict:
    """生成冒险奖励 — DMG 第四章「冒险奖励」。

    规则依据: 城主指南2024/4.创建冒险/冒险奖励.htm
      - 个体宝藏(Individual Treasure): 角色们可能会在单个怪物的口袋、
        杂物小包或是其私下的藏宝处发现少量宝藏。
      - 库藏宝藏(Treasure Hoards): 有时冒险者们会发现大量宝藏，
        例如一大群生物积累的财富、或是某个强大生物所囤积的珍贵宝山。
      - 任务奖励(Quest Rewards): 若要为玩家设定合适的任务奖励，
        请掷一次随机库藏宝藏表，此时使用角色的等级代替表中所需的Cr。

    本函数对每个Cr调用 loot.generate_loot() 生成个体宝藏，
    并汇总为冒险奖励池。

    Args:
        cr_list:               怪物CR列表
        include_magic_items:   是否包含魔法物品
        seed:                  随机种子（测试用）

    Returns:
        {
            "total_gold": int,
            "individual_treasures": [LootPool.to_dict(), ...],
            "magic_item_count": int,
            "cr_summary": {str(cr): int count},
        }
    """
    rng = random.Random(seed) if seed is not None else random.Random()

    total_gold = 0
    individual_treasures = []
    magic_item_count = 0
    cr_summary: dict[str, int] = {}

    for cr in cr_list:
        cr_key = str(cr)
        cr_summary[cr_key] = cr_summary.get(cr_key, 0) + 1

        # 调用 loot.generate_loot() 生成个体宝藏
        pool = loot_mod.generate_loot(
            cr=cr,
            count_enemies=1,
            include_magic_items=include_magic_items,
            seed=rng.randint(0, 99999),
        )

        total_gold += pool.gold
        magic_item_count += len(pool.magic_items)
        individual_treasures.append(pool.to_dict())

    return {
        "total_gold": total_gold,
        "individual_treasures": individual_treasures,
        "magic_item_count": magic_item_count,
        "cr_summary": cr_summary,
    }


def get_xp_budget(party_level: int,
                  difficulty: str,
                  party_size: int = 4) -> int:
    """计算遭遇XP预算 — DMG 第四章「战斗遭遇难度」。

    规则依据: 城主指南2024/4.创建冒险/规划遭遇/战斗遭遇.htm
      第2步：决定你的经验值预算。
      使用人均经验值预算表，对照小队等级和遭遇难度。
      用表中的数字乘以小队中的角色数，以获得这场战斗的经验值预算。

    Args:
        party_level: 小队等级 (1-20)
        difficulty:  难度 (low/moderate/high)
        party_size:  小队人数

    Returns:
        XP预算总值

    Raises:
        ValueError: 等级或难度越界
    """
    if party_level < 1 or party_level > 20:
        raise ValueError(f"小队等级必须在1-20之间，实际: {party_level}")

    valid_diffs = {"low", "moderate", "high"}
    if difficulty not in valid_diffs:
        raise ValueError(f"未知难度: {difficulty}，可选: {sorted(valid_diffs)}")

    budget_table = XP_BUDGET_PER_CHARACTER.get(party_level)
    if budget_table is None:
        raise ValueError(f"不支持的小队等级: {party_level}")

    per_char_xp = budget_table[difficulty]
    return per_char_xp * party_size


def roll_adventure_connection(seed: Optional[int] = None) -> tuple[int, str]:
    """掷冒险间的关联表 — DMG 第五章「单元剧和连续剧」。

    规则依据: 城主指南2024/5.创作战役/规划冒险/单元剧和连续剧.htm
      连结冒险：你需要在连续剧战役中的各次冒险的之间建立起连结，
      让它们感觉起来像是一整个相互关联的故事。
      使用冒险间的关联表(d6)获得关于将一个冒险和下一个冒险连结起来的灵感。

    Args:
        seed: 随机种子（测试用）

    Returns:
        (骰点, 关联描述)
    """
    rng = random.Random(seed) if seed is not None else random.Random()
    return _roll_table(ADVENTURE_CONNECTIONS, rng)


# ═══════════════════════════════════════════════════════════════════════════
# 自检
# ═══════════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    """冒险创建工具自检。"""
    import os

    # ═══ 1. 等级梯队映射 ═══
    assert _level_to_tier(1) == "local_hero"
    assert _level_to_tier(4) == "local_hero"
    assert _level_to_tier(5) == "realm_hero"
    assert _level_to_tier(10) == "realm_hero"
    assert _level_to_tier(11) == "master_realm"
    assert _level_to_tier(16) == "master_realm"
    assert _level_to_tier(17) == "master_world"
    assert _level_to_tier(20) == "master_world"
    print("[adventure_builder] 等级梯队映射 ✓")

    # ═══ 2. 创建冒险 ═══
    adv = create_adventure("失落的矿坑", level_range=(1, 4), setting="地下城", seed=42)
    assert adv.name == "失落的矿坑"
    assert adv.level_range == (1, 4)
    assert adv.setting == "地下城"
    assert adv.background is not None
    assert adv.background.tier == "local_hero"
    assert adv.background.situation != ""
    assert adv.id.startswith("adv_")
    assert len(adv.design_steps) == 4
    print("[adventure_builder] 创建冒险 ✓")

    # ═══ 3. 导入玩家引子 ═══
    # 赞助者引子
    hook_sponsor = import_players("sponsor", seed=42)
    assert hook_sponsor.method == "sponsor"
    assert hook_sponsor.description in PATRON_HOOKS.values()
    assert 1 <= hook_sponsor.roll <= 6

    # 巧合引子
    hook_coin = import_players("coincidence", seed=42)
    assert hook_coin.method == "coincidence"
    assert hook_coin.description in HAPPENSTANCE_HOOKS.values()

    # 超自然引子
    hook_super = import_players("supernatural", seed=42)
    assert hook_super.method == "supernatural"
    assert hook_super.description in SUPERNATURAL_HOOKS.values()

    # 可复现性
    h1 = import_players("sponsor", seed=100)
    h2 = import_players("sponsor", seed=100)
    assert h1.roll == h2.roll
    assert h1.description == h2.description

    # 未知方法应抛异常
    try:
        import_players("unknown", seed=42)
        assert False, "应抛出ValueError"
    except ValueError:
        pass
    print("[adventure_builder] 导入玩家引子 ✓")

    # ═══ 4. 设置背景 ═══
    bg = set_background(adv, conflict="邪教徒召唤恶魔", setting="城市", premise="城市陷入混乱")
    assert bg.conflict == "邪教徒召唤恶魔"
    assert bg.setting == "城市"
    assert bg.premise == "城市陷入混乱"
    assert adv.setting == "城市"
    print("[adventure_builder] 设置背景 ✓")

    # ═══ 5. 添加遭遇 ═══
    # 战斗遭遇
    enc_combat = add_encounter(
        adv, encounter_type="combat", difficulty="low",
        description="遭遇一群哥布林", party_level=1, party_size=4,
        monsters=[{"name": "哥布林", "cr": 0.25, "xp": 50, "count": 4}],
    )
    assert enc_combat.encounter_type == "combat"
    assert enc_combat.difficulty == "low"
    # 等级1低难度: 50 * 4 = 200
    assert enc_combat.xp_budget == 200
    # 4只哥布林各50XP = 200
    assert enc_combat.xp_spent == 200
    assert len(enc_combat.monsters) == 1

    # 交涉遭遇
    enc_social = add_encounter(
        adv, encounter_type="social", description="与酒馆老板交谈",
    )
    assert enc_social.encounter_type == "social"
    assert enc_social.difficulty == ""
    assert enc_social.xp_budget == 0

    # 探索遭遇
    enc_explore = add_encounter(
        adv, encounter_type="exploration", description="搜索隐藏的门",
    )
    assert enc_explore.encounter_type == "exploration"

    # 未知遭遇类型应抛异常
    try:
        add_encounter(adv, encounter_type="unknown")
        assert False, "应抛出ValueError"
    except ValueError:
        pass

    # 未知难度应抛异常
    try:
        add_encounter(adv, encounter_type="combat", difficulty="impossible")
        assert False, "应抛出ValueError"
    except ValueError:
        pass

    assert len(adv.encounters) == 3
    print("[adventure_builder] 添加遭遇 ✓")

    # ═══ 6. 添加NPC ═══
    npc = add_npc(adv, name="格罗姆", role="赞助者", description="矮人商人", location="酒馆")
    assert npc.name == "格罗姆"
    assert npc.role == "赞助者"
    assert len(adv.npcs) == 1

    npc2 = add_npc(adv, name="暗影领主", role="反派", description="神秘的黑袍法师")
    assert len(adv.npcs) == 2
    print("[adventure_builder] 添加NPC ✓")

    # ═══ 7. 结束冒险 ═══
    # 圆满收尾
    ending_res = end_adventure(adv, method="resolution", seed=42)
    assert ending_res.method == "resolution"
    assert ending_res.climax in ADVENTURE_CLIMAXES.values()
    assert ending_res.denouement != ""

    # 悬念结尾
    ending_cliff = end_adventure(adv, method="cliffhanger", climax_roll=6, seed=42)
    assert ending_cliff.method == "cliffhanger"
    assert ending_cliff.climax == ADVENTURE_CLIMAXES[6]

    # 手动指定骰点
    ending_manual = end_adventure(adv, method="resolution", climax_roll=1)
    assert ending_manual.climax == ADVENTURE_CLIMAXES[1]

    # 未知方式应抛异常
    try:
        end_adventure(adv, method="unknown")
        assert False, "应抛出ValueError"
    except ValueError:
        pass

    # 骰点越界应抛异常
    try:
        end_adventure(adv, method="resolution", climax_roll=11)
        assert False, "应抛出ValueError"
    except ValueError:
        pass
    print("[adventure_builder] 结束冒险 ✓")

    # ═══ 8. 生成冒险奖励 ═══
    rewards = generate_rewards([1, 2, 3], seed=42)
    assert rewards["total_gold"] > 0
    assert len(rewards["individual_treasures"]) == 3
    assert rewards["cr_summary"] == {"1": 1, "2": 1, "3": 1}

    # 不含魔法物品
    rewards_no_mi = generate_rewards([5], include_magic_items=False, seed=42)
    assert rewards_no_mi["magic_item_count"] == 0

    # 空CR列表
    rewards_empty = generate_rewards([], seed=42)
    assert rewards_empty["total_gold"] == 0
    assert len(rewards_empty["individual_treasures"]) == 0
    print("[adventure_builder] 生成冒险奖励 ✓")

    # ═══ 9. XP预算计算 ═══
    # 等级1低难度4人: 50*4=200
    assert get_xp_budget(1, "low", 4) == 200
    # 等级5中等难度5人: 750*5=3750
    assert get_xp_budget(5, "moderate", 5) == 3750
    # 等级20高难度6人: 22000*6=132000
    assert get_xp_budget(20, "high", 6) == 132000

    # 越界应抛异常
    try:
        get_xp_budget(0, "low")
        assert False, "应抛出ValueError"
    except ValueError:
        pass
    try:
        get_xp_budget(1, "unknown")
        assert False, "应抛出ValueError"
    except ValueError:
        pass
    print("[adventure_builder] XP预算计算 ✓")

    # ═══ 10. 冒险间关联表 ═══
    roll, desc = roll_adventure_connection(seed=42)
    assert 1 <= roll <= 6
    assert desc in ADVENTURE_CONNECTIONS.values()
    print("[adventure_builder] 冒险间关联表 ✓")

    # ═══ 11. 序列化 ═══
    adv_dict = adv.to_dict()
    assert adv_dict["name"] == "失落的矿坑"
    assert adv_dict["level_range"] == [1, 4]
    assert adv_dict["hook"] is None  # 未设置hook
    assert adv_dict["background"] is not None
    assert len(adv_dict["npcs"]) == 2
    assert len(adv_dict["encounters"]) == 3
    assert adv_dict["ending"] is not None
    print("[adventure_builder] 序列化 ✓")

    # ═══ 12. 完整流程集成 ═══
    # 模拟DMG第四章四步设计法的完整流程
    adv2 = create_adventure("北风舞会", level_range=(5, 10), setting="城堡", seed=100)
    assert adv2.background.tier == "realm_hero"

    # 第2步：导入玩家
    adv2.hook = import_players("supernatural", seed=100)
    assert adv2.hook.method == "supernatural"

    # 第3步：规划遭遇
    add_encounter(adv2, "combat", "moderate", "舞会遭袭", 5, 4,
                  [{"name": "吸血鬼", "cr": 5, "xp": 1800, "count": 1}])
    add_encounter(adv2, "social", description="与神秘贵族交谈")
    add_encounter(adv2, "exploration", description="搜索密室")
    assert len(adv2.encounters) == 3

    # 第4步：结束冒险 + 奖励
    end_adventure(adv2, method="resolution", seed=100)
    adv2.rewards = generate_rewards([5, 5, 8], seed=100)
    assert adv2.ending is not None
    assert adv2.rewards["total_gold"] > 0

    # 验证完整序列化
    adv2_dict = adv2.to_dict()
    assert adv2_dict["hook"] is not None
    assert adv2_dict["ending"] is not None
    assert adv2_dict["rewards"] is not None
    print("[adventure_builder] 完整流程集成 ✓")

    print("[adventure_builder] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
