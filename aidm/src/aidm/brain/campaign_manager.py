"""战役管理工具 — DMG 第五章「创作战役」。

规则依据: 城主指南2024/5.创作战役/
  - 一步步建立战役.htm        战役四步设计法（与第四章冒险设计法对应）
  - 开始战役.htm              第零回 Session Zero + 起始地点 + 第一次冒险
  - 你的战役日志.htm          战役日志维护（更新日志/使用日志/伏笔/冒险储备）
  - 结束战役.htm              结束战役（提前结束/天降结局）
  - 战役背景/(奇幻风格/战役冲突/战役设定).htm  奇幻风格表 + D&D设定表 + 冲突弧线
  - 规划冒险/(单元剧和连续剧/让玩家投入/战役中的时间).htm  单元剧/连续剧 + 关联表

本模块提供:
  - create_campaign()      创建战役（DMG 第五章四步法）
  - add_session()          添加一次团（Session）
  - log_campaign_event()   记录战役日志事件
  - get_campaign_timeline()获取战役时间线
  - end_campaign()         结束战役
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════
# 数据表 — 从 DMG 第五章 HTML 原文提取
# ═══════════════════════════════════════════════════════════════════════════

# ── 战役设计四步法 ──────────────────────────────────────────────────────
# 规则依据: 城主指南2024/5.创作战役/一步步建立战役.htm
CAMPAIGN_STEPS = [
    {"step": 1, "name": "布置背景", "en": "Lay Out the Premise",
     "desc": "设计驱动战役推进的核心冲突，并选择一个合适的战役设定。"},
    {"step": 2, "name": "导入玩家", "en": "Draw In the Players",
     "desc": "战役需要一个令人印象深刻的开端。思考角色们是如何被卷入一系列事件中的。"},
    {"step": 3, "name": "规划冒险", "en": "Plan Adventures",
     "desc": "战役中的大冲突是由更多细化的小冲突组成的，设计各种有趣的任务。"},
    {"step": 4, "name": "步入终局", "en": "Bring It to an End",
     "desc": "考虑你的战役会以何种方式结束，以及在战役结束时角色们会升至几级。"},
]

# ── D&D 设定表 ─────────────────────────────────────────────────────────
# 规则依据: 城主指南2024/5.创作战役/战役背景/战役设定.htm
DND_SETTINGS = {
    "dark_sun":       "英雄们在一片被魔法污染、被众神抛弃的后启示录世界中冒险。",
    "dragonlance":    "善之阵营与邪龙女王及其爪牙之间的长枪战争撼动着整个世界。",
    "eberron":        "在致命的热战结束之后，魔法发达的各国之间重新结成了新的冷战局势。",
    "exandria":       "英雄们在直播跑团节目《Critical Role》的世界中留下属于自己的名字。",
    "forgotten_realms":"传奇般的英雄与反派不断争夺着决定世界之命运的权力。",
    "greyhawk":       "国与国之间的战事不断升温，角色们搜刮地下城，寻求所需的魔法和力量。",
    "planescape":     "印记城，众门之城，亦将是英雄们探索D&D多元宇宙之奇景的开端。",
    "ravenloft":      "英雄们堕入了残酷不堪的恐惧领域：被邪恶领主们支配的遭诅之地。",
    "ravnica":        "在这座覆盖了全世界的宏伟巨城内，十大互相对立的派系将英雄们卷入危险之中。",
    "spelljammer":    "乘坐法驱舰船在群星间漫游，探访浮于荒宇的浩瀚星海之上的无数世界。",
    "strixhaven":     "斯翠海文，一座魔法学院，亦是角色们学习与冒险的中轴。",
    "theros":         "灵感来自古希腊神话的战役设定，其中有许多英雄天命等待着角色们去实现。",
}

# ── 奇幻风格表 ─────────────────────────────────────────────────────────
# 规则依据: 城主指南2024/5.创作战役/战役背景/奇幻风格.htm
FANTASY_STYLES = {
    "heroic": {
        "name": "英雄奇幻",
        "en": "Heroic Fantasy",
        "desc": "英雄奇幻着眼于利用魔法之力抵抗怪物之威胁的冒险者们——此即是D&D规则默认的基本型。",
        "conflicts": [
            "邪教团体：邪恶的秘教团渗透了一片祥和的国度，企图解放一位被缚于此地的古老邪恶存在。",
            "真菌感染：为了保护原始森林免受猎人和殖民者的破坏，德鲁伊们释放了真菌瘟疫——随后失控。",
            "昔日敌手：一位曾于几年前和角色们交锋过的狡猾反派重新现身。",
        ],
    },
    "sword_and_sorcery": {
        "name": "剑与巫术",
        "en": "Sword and Sorcery",
        "desc": "剑与巫术风格的战役往往发生在一处残酷的世界，其中充斥着邪恶的施法者与衰颓的城市。",
        "conflicts": [
            "邪恶冒险者：一队经验丰富的邪恶冒险者依靠其威能与影响力欺压凄惨的民众。",
            "邪恶武器：被一柄邪恶智能武器影响的一位骑士残害着一片曾经祥和的国度。",
            "失落王朝：一个长久以来被人遗忘的王朝的城市从汪洋深处或沙海之下升起，重见天日。",
        ],
    },
    "epic": {
        "name": "史诗奇幻",
        "en": "Epic Fantasy",
        "desc": "史诗奇幻战役以强调善恶冲突为其游戏中不变的元素，而冒险者们或多或少偏向善良一方。",
        "conflicts": [
            "末日预言：一位先知预言了这个世界的终结——而角色们可以阻止末日的到来。",
            "巨龙暴政：一条邪恶而又强大的巨龙进入了一处地区，破坏了这里的环境，并要求周围的聚落献上贡品。",
            "沉于昔日之敌：一位被认为早在无数年岁之前便已死去的邪恶存在自妖精荒野中完好归来。",
        ],
    },
    "mythic": {
        "name": "神话奇幻",
        "en": "Mythic Fantasy",
        "desc": "神话奇幻战役的主题和故事基于古老的神话与传说。冒险者们试图完成传奇般的伟大功绩。",
        "conflicts": [
            "神圣试炼：为了得到诸神的赠礼或青睐，冒险者们接下了一系列试炼。",
            "神怒之日：由于一座神殿被毁，某位记仇的神灵向一处王国降下一系列越来越严重的灾祸。",
            "巨人！：一座极为高耸的云上巨城悬于大地之上。角色们可以选择与其中的巨人死战，或是于双方之间促成长久的和平。",
        ],
    },
    "horror": {
        "name": "超自然恐怖",
        "en": "Supernatural Horror",
        "desc": "超自然恐怖主题的战役通常涉及远超凡人的亡灵和魔族大反派。",
        "conflicts": [
            "无面领主：朱庇莱克斯，无面领主，已经从深渊中涌出，不断渗入幽暗地域。",
            "死灵学院：吸血鬼们创办了一座研习死灵术的学院，吸引需要新鲜尸体进行研究的死灵师们加入。",
            "不死魔君：一位受人尊敬的君主将信仰转投向奥喀斯，以此攫取力量，化作一位巫妖。",
        ],
    },
    "intrigue": {
        "name": "阴谋",
        "en": "Intrigue",
        "desc": "政治阴谋、谍报活动、干扰破坏以及其他'匕首&斗篷'风格的活动都可以作为一场惊心动魄的战役背景。",
        "conflicts": [
            "双城之战：两座封国或聚落之间常年不和。在出手帮助了其中一方后，角色们亦被卷入了双方的对峙之中。",
            "僭王者：一处王国因为其元首的突然死亡而深陷混乱，而合法的王国继承人正在受到的敌对势力的威胁。",
            "顾问的阴谋：角色们引起了一位君王的兴趣，然而君王身边最受信任的顾问却将角色们看作了目标。",
        ],
    },
    "swashbuckling": {
        "name": "历险",
        "en": "Swashbuckling",
        "desc": "海盗与火枪手式的历险记型冒险是一种节奏明快的战役。",
        "conflicts": [
            "继承'遗产'：一名角色从一位逝去的亲人处继承了一件魔法物品——然而这位亲人的敌对者同样在追查这件物品的踪迹。",
            "海盗与私掠：一位新上任的君主向海军及私掠船发放委托，让它们猎杀海盗船以打击海盗行为。",
            "渊海觉醒：沉眠于大洋深处的一只渊海魔怪苏醒了，它派出自己的爪牙袭击着海上的船只。",
        ],
    },
    "war": {
        "name": "战争",
        "en": "War",
        "desc": "一场战争型的战役着眼于扭转战事的英雄角色。",
        "conflicts": [
            "自由战士：缺乏武装、组织混乱的穷苦之人向暴君掀起了反旗。",
            "侵略战争：一个军国主义国家入侵了其爱好和平的邻国。",
            "棋盘上的弃子：一场大战持续了数十年，其最初爆发的原因早已被遗忘。",
        ],
    },
}

# ── 冲突弧线里程碑 ─────────────────────────────────────────────────────
# 规则依据: 城主指南2024/5.创作战役/战役背景/战役冲突.htm
#   第5、11、17级是划分角色强度与实力的里程碑——同样也可以是划分战役弧线的里程碑。
CONFLICT_ARC_MILESTONES = [5, 11, 17]

# ── 队伍汇合方式 ───────────────────────────────────────────────────────
# 规则依据: 城主指南2024/5.创作战役/开始战役.htm
PARTY_BONDING_METHODS = {
    "event": "活动事件：一些活动（如婚礼、节日庆典、葬礼）让角色们得以相聚，而他们很快发现了一种共同的目标感。",
    "chance": "偶然结识：有人招募冒险者完成任务，角色们恰好都接下了这个任务；亦或是，角色们在路上偶然相遇。",
    "acquaintance": "共同熟人：角色们都信任共一位熟人NPC，它将大家介绍给彼此。",
    "history": "共同过去：角色们在同一个地方长大，彼此相识多年。",
    "tavern": "酒馆相会：角色们在小酒馆里相遇，喝着几杯麦芽酒，决定一起踏上冒险生涯。",
}


# ═══════════════════════════════════════════════════════════════════════════
# 数据结构
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class LogEntry:
    """战役日志条目 — DMG 第五章「你的战役日志」。

    规则依据: 城主指南2024/5.创作战役/你的战役日志.htm
      战役日志记录了战役的进度，从第一回团一直到最新的那回团。
      在跑完新一回团后，你需要使用日志记录那些可能对未来的团产生影响的重要事物。
    """
    session_number: int           # 第几回团
    timestamp: str                # ISO格式时间戳
    event_type: str               # 事件类型 (combat/social/exploration/story/reward/death)
    description: str              # 事件描述
    npcs_involved: list[str] = field(default_factory=list)  # 涉及的NPC
    loot_gained: int = 0          # 获得的金币
    xp_gained: int = 0            # 获得的经验值

    def to_dict(self) -> dict:
        return {
            "session_number": self.session_number,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "description": self.description,
            "npcs_involved": self.npcs_involved,
            "loot_gained": self.loot_gained,
            "xp_gained": self.xp_gained,
        }


@dataclass
class Session:
    """一次跑团（Session）— DMG 第五章「开始战役」。

    规则依据: 城主指南2024/5.创作战役/开始战役.htm
      第零回(Session Zero)：在战役开始时，你可以给玩家们开一回特殊的团——即，
      第零回（因为它在正式的第一次团之前进行）来确立期望、分享点子、讨论房规。
    """
    session_number: int                    # 回次编号（0=第零回）
    adventure_id: str | None = None     # 关联的冒险ID
    summary: str = ""                      # 本次团的摘要
    log_entries: list[LogEntry] = field(default_factory=list)  # 日志条目
    date_played: str = ""                  # 游玩日期

    def to_dict(self) -> dict:
        return {
            "session_number": self.session_number,
            "adventure_id": self.adventure_id,
            "summary": self.summary,
            "log_entries": [e.to_dict() for e in self.log_entries],
            "date_played": self.date_played,
        }


@dataclass
class Milestone:
    """战役里程碑 — DMG 第五章「冲突弧线」。

    规则依据: 城主指南2024/5.创作战役/战役背景/战役冲突.htm
      第5、11、17级是划分角色强度与实力的里程碑——同样也可以是划分战役弧线的里程碑。
      游戏阶段的提升，是结束战役中的旧冲突并引入影响更深、威胁更大的新冲突的理想时机。
    """
    level: int                   # 角色等级里程碑
    conflict_resolved: str = ""  # 已解决的冲突
    new_conflict: str = ""       # 新引入的冲突
    reached: bool = False        # 是否已达到

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "conflict_resolved": self.conflict_resolved,
            "new_conflict": self.new_conflict,
            "reached": self.reached,
        }


@dataclass
class Campaign:
    """战役 — DMG 第五章「创作战役」。

    规则依据: 城主指南2024/5.创作战役/创作战役.htm
      如果说遭遇是用来搭建D&D冒险的基础单元，那么冒险本则身同样是用来搭建D&D战役的基础单元
      ——将复数个冒险串联在一起，便成了一场战役。
    """
    id: str                                    # 战役唯一标识
    name: str                                  # 战役名称
    tone: str = ""                             # 战役基调/风格 (heroic/epic/horror/...)
    setting: str = ""                          # 战役设定 (homebrew/greyhawk/forgotten_realms/...)
    world_state: dict = field(default_factory=dict)  # 世界状态快照
    sessions: list[Session] = field(default_factory=list)  # 所有回次
    milestones: list[Milestone] = field(default_factory=list)  # 里程碑列表
    campaign_steps: list[dict] = field(default_factory=lambda: [s for s in CAMPAIGN_STEPS])
    current_level: int = 1                     # 当前角色等级
    ended: bool = False                        # 是否已结束

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "tone": self.tone,
            "setting": self.setting,
            "world_state": self.world_state,
            "sessions": [s.to_dict() for s in self.sessions],
            "milestones": [m.to_dict() for m in self.milestones],
            "current_level": self.current_level,
            "ended": self.ended,
        }


# ═══════════════════════════════════════════════════════════════════════════
# 核心函数
# ═══════════════════════════════════════════════════════════════════════════

def create_campaign(name: str,
                    tone: str = "heroic",
                    setting: str = "homebrew",
                    seed: int | None = None) -> Campaign:
    """创建战役 — DMG 第五章四步设计法第1步「布置背景」。

    规则依据: 城主指南2024/5.创作战役/一步步建立战役.htm
      第一步：布置背景。设计驱动战役推进的核心冲突，
      并选择一个合适的战役设定，最好要贴合你想展现的基调与风格。

    规则依据: 城主指南2024/5.创作战役/战役背景/战役设定.htm
      DM在选择战役设定时有两种选项：使用出版物中的战役设定，或创作自己的战役设定。

    规则依据: 城主指南2024/5.创作战役/战役背景/奇幻风格.htm
      你的D&D战役也许是受了某种特定奇幻风格的启发。

    Args:
        name:    战役名称
        tone:    战役基调/风格 key (见 FANTASY_STYLES)
        setting: 战役设定 key (见 DND_SETTINGS) 或 "homebrew"
        seed:    随机种子（测试用）

    Returns:
        Campaign 对象

    Raises:
        ValueError: 未知基调或设定
    """
    if tone not in FANTASY_STYLES:
        raise ValueError(f"未知战役基调: {tone}，可选: {sorted(FANTASY_STYLES)}")

    if setting != "homebrew" and setting not in DND_SETTINGS:
        raise ValueError(f"未知战役设定: {setting}，可选: {sorted(DND_SETTINGS)} + 'homebrew'")

    rng = random.Random(seed) if seed is not None else random.Random()
    camp_id = f"camp_{rng.randint(10000, 99999)}"

    # 初始化里程碑
    milestones = [Milestone(level=lv) for lv in CONFLICT_ARC_MILESTONES]

    # 世界状态初始快照
    style_info = FANTASY_STYLES[tone]
    world_state = {
        "tone": tone,
        "tone_name": style_info["name"],
        "setting": setting,
        "active_conflicts": [],
        "resolved_conflicts": [],
        "key_npcs": [],
        "key_locations": [],
    }

    return Campaign(
        id=camp_id,
        name=name,
        tone=tone,
        setting=setting,
        world_state=world_state,
        milestones=milestones,
    )


def add_session(campaign: Campaign,
                adventure_id: str | None = None,
                summary: str = "",
                is_session_zero: bool = False) -> Session:
    """添加一次团（Session）到战役 — DMG 第五章「开始战役」。

    规则依据: 城主指南2024/5.创作战役/开始战役.htm
      第零回(Session Zero)：在战役开始时，你可以给玩家们开一回特殊的团——即，
      第零回（因为它在正式的第一次团之前进行）来确立期望、分享点子、讨论房规。

    Args:
        campaign:        战役对象
        adventure_id:    关联的冒险ID
        summary:         本次团的摘要
        is_session_zero: 是否为第零回

    Returns:
        Session 对象
    """
    if is_session_zero:
        session_number = 0
    else:
        # 计算下一个回次编号
        existing_numbers = [s.session_number for s in campaign.sessions]
        session_number = max(existing_numbers, default=0) + 1

    session = Session(
        session_number=session_number,
        adventure_id=adventure_id,
        summary=summary,
        date_played=datetime.now().isoformat(),
    )

    campaign.sessions.append(session)
    return session


def log_campaign_event(campaign: Campaign,
                       event_type: str,
                       description: str,
                       npcs_involved: list[str] | None = None,
                       loot_gained: int = 0,
                       xp_gained: int = 0) -> LogEntry:
    """记录战役日志事件 — DMG 第五章「你的战役日志」。

    规则依据: 城主指南2024/5.创作战役/你的战役日志.htm
      更新日志：战役日志上记录了战役的进度，从第一回团一直到最新的那回团。
      使用日志：在跑完新一回团后，你需要使用日志记录那些可能对未来的团产生影响的重要事物，
      例如您即兴创作出的NPC的名字，或是角色们拿到的关键线索。

    Args:
        campaign:       战役对象
        event_type:     事件类型 (combat/social/exploration/story/reward/death)
        description:    事件描述
        npcs_involved:  涉及的NPC名称列表
        loot_gained:    获得的金币
        xp_gained:      获得的经验值

    Returns:
        LogEntry 对象

    Raises:
        ValueError: 无可用回次或未知事件类型
    """
    valid_types = {"combat", "social", "exploration", "story", "reward", "death"}
    if event_type not in valid_types:
        raise ValueError(f"未知事件类型: {event_type}，可选: {sorted(valid_types)}")

    if not campaign.sessions:
        raise ValueError("战役中尚无回次，请先调用 add_session()")

    # 取最后一个回次
    session = campaign.sessions[-1]

    entry = LogEntry(
        session_number=session.session_number,
        timestamp=datetime.now().isoformat(),
        event_type=event_type,
        description=description,
        npcs_involved=npcs_involved or [],
        loot_gained=loot_gained,
        xp_gained=xp_gained,
    )

    session.log_entries.append(entry)

    # 更新世界状态：任何获得金币的事件都累加到 total_loot
    if loot_gained > 0:
        campaign.world_state.setdefault("total_loot", 0)
        campaign.world_state["total_loot"] += loot_gained

    if npcs_involved:
        existing_npcs = set(campaign.world_state.get("key_npcs", []))
        for npc in npcs_involved:
            existing_npcs.add(npc)
        campaign.world_state["key_npcs"] = sorted(existing_npcs)

    return entry


def get_campaign_timeline(campaign: Campaign) -> list[Session]:
    """获取战役时间线 — DMG 第五章「你的战役日志」。

    规则依据: 城主指南2024/5.创作战役/你的战役日志.htm
      战役日志最好依照日期或团次来归档整理。
      你也可以在带团的过程中使用战役日志。

    Args:
        campaign: 战役对象

    Returns:
        按回次排序的 Session 列表
    """
    return sorted(campaign.sessions, key=lambda s: s.session_number)


def end_campaign(campaign: Campaign,
                 method: str = "grand_finale",
                 final_level: int = 20) -> dict:
    """结束战役 — DMG 第五章「结束战役」。

    规则依据: 城主指南2024/5.创作战役/结束战役.htm
      在战役步入尾声时，最后的主要冲突亦应结束，
      并在这个过程中收束开端和中端埋下的大部分线索（但你也可以留下一些开放性的结局）。
      提前结束：玩家参与 / 换个人带 / 换个团跑 / 天降结局。

    Args:
        campaign:    战役对象
        method:      结束方式 (grand_finale/player_input/switch_dm/transport/grand_finale)
        final_level: 战役结束时的角色等级

    Returns:
        {
            "ended": True,
            "method": str,
            "final_level": int,
            "total_sessions": int,
            "total_log_entries": int,
        }

    Raises:
        ValueError: 未知结束方式
    """
    valid_methods = {"grand_finale", "player_input", "switch_dm", "transport"}
    if method not in valid_methods:
        raise ValueError(f"未知结束方式: {method}，可选: {sorted(valid_methods)}")

    campaign.ended = True
    campaign.current_level = final_level

    total_log_entries = sum(len(s.log_entries) for s in campaign.sessions)

    return {
        "ended": True,
        "method": method,
        "final_level": final_level,
        "total_sessions": len(campaign.sessions),
        "total_log_entries": total_log_entries,
    }


def get_fantasy_style(style_key: str) -> dict:
    """获取奇幻风格详情 — DMG 第五章「奇幻风格」。

    规则依据: 城主指南2024/5.创作战役/战役背景/奇幻风格.htm

    Args:
        style_key: 风格 key (见 FANTASY_STYLES)

    Returns:
        风格详情字典

    Raises:
        ValueError: 未知风格
    """
    if style_key not in FANTASY_STYLES:
        raise ValueError(f"未知奇幻风格: {style_key}，可选: {sorted(FANTASY_STYLES)}")
    return FANTASY_STYLES[style_key]


def list_fantasy_styles() -> list[dict]:
    """列出所有奇幻风格 — DMG 第五章「奇幻风格」。

    规则依据: 城主指南2024/5.创作战役/战役背景/奇幻风格.htm

    Returns:
        [{key, name, en, desc}, ...]
    """
    return [
        {"key": k, "name": v["name"], "en": v["en"], "desc": v["desc"]}
        for k, v in FANTASY_STYLES.items()
    ]


def list_dnd_settings() -> list[dict]:
    """列出所有D&D设定 — DMG 第五章「战役设定」。

    规则依据: 城主指南2024/5.创作战役/战役背景/战役设定.htm

    Returns:
        [{key, desc}, ...]
    """
    return [{"key": k, "desc": v} for k, v in DND_SETTINGS.items()]


# ═══════════════════════════════════════════════════════════════════════════
# 自检
# ═══════════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    """战役管理工具自检。"""

    # ═══ 1. 创建战役 ═══
    camp = create_campaign("灰鹰编年史", tone="heroic", setting="greyhawk", seed=42)
    assert camp.name == "灰鹰编年史"
    assert camp.tone == "heroic"
    assert camp.setting == "greyhawk"
    assert camp.id.startswith("camp_")
    assert len(camp.milestones) == 3
    assert camp.milestones[0].level == 5
    assert camp.milestones[1].level == 11
    assert camp.milestones[2].level == 17
    assert camp.world_state["tone"] == "heroic"
    assert camp.world_state["setting"] == "greyhawk"
    print("[campaign_manager] 创建战役 ✓")

    # ═══ 2. 未知基调/设定应抛异常 ═══
    try:
        create_campaign("test", tone="unknown", seed=42)
        assert False, "应抛出ValueError"
    except ValueError:
        pass

    try:
        create_campaign("test", setting="unknown", seed=42)
        assert False, "应抛出ValueError"
    except ValueError:
        pass

    # homebrew 设定应该可以
    camp_hb = create_campaign("自制世界", tone="epic", setting="homebrew", seed=42)
    assert camp_hb.setting == "homebrew"
    print("[campaign_manager] 参数校验 ✓")

    # ═══ 3. 添加回次 ═══
    # 第零回
    s0 = add_session(camp, is_session_zero=True, summary="第零回：创建角色，讨论房规")
    assert s0.session_number == 0
    assert s0.summary == "第零回：创建角色，讨论房规"

    # 第一回
    s1 = add_session(camp, adventure_id="adv_12345", summary="第一回：进入地下城")
    assert s1.session_number == 1
    assert s1.adventure_id == "adv_12345"

    # 第二回
    s2 = add_session(camp, summary="第二回：击败哥布林王")
    assert s2.session_number == 2

    assert len(camp.sessions) == 3
    print("[campaign_manager] 添加回次 ✓")

    # ═══ 4. 记录战役日志 ═══
    entry1 = log_campaign_event(
        camp, event_type="combat", description="与哥布林战斗",
        npcs_involved=["哥布林王"], loot_gained=50, xp_gained=200,
    )
    assert entry1.event_type == "combat"
    assert entry1.loot_gained == 50
    assert entry1.xp_gained == 200
    assert "哥布林王" in entry1.npcs_involved

    # 验证世界状态更新
    assert camp.world_state.get("total_loot") == 50
    assert "哥布林王" in camp.world_state.get("key_npcs", [])

    entry2 = log_campaign_event(
        camp, event_type="reward", description="找到宝箱",
        loot_gained=100,
    )
    assert camp.world_state.get("total_loot") == 150

    # 未知事件类型应抛异常
    try:
        log_campaign_event(camp, event_type="unknown", description="test")
        assert False, "应抛出ValueError"
    except ValueError:
        pass

    # 无回次时应抛异常
    empty_camp = create_campaign("空战役", seed=42)
    try:
        log_campaign_event(empty_camp, event_type="story", description="test")
        assert False, "应抛出ValueError"
    except ValueError:
        pass
    print("[campaign_manager] 记录战役日志 ✓")

    # ═══ 5. 获取战役时间线 ═══
    timeline = get_campaign_timeline(camp)
    assert len(timeline) == 3
    # 按回次排序
    assert timeline[0].session_number == 0
    assert timeline[1].session_number == 1
    assert timeline[2].session_number == 2
    # 最后一个回次应该有日志条目
    assert len(timeline[-1].log_entries) == 2
    print("[campaign_manager] 获取战役时间线 ✓")

    # ═══ 6. 结束战役 ═══
    result = end_campaign(camp, method="grand_finale", final_level=15)
    assert result["ended"] is True
    assert result["method"] == "grand_finale"
    assert result["final_level"] == 15
    assert result["total_sessions"] == 3
    assert result["total_log_entries"] == 2
    assert camp.ended is True
    assert camp.current_level == 15

    # 未知结束方式应抛异常
    try:
        end_campaign(camp, method="unknown")
        assert False, "应抛出ValueError"
    except ValueError:
        pass
    print("[campaign_manager] 结束战役 ✓")

    # ═══ 7. 奇幻风格查询 ═══
    styles = list_fantasy_styles()
    assert len(styles) == 8  # heroic/sword_and_sorcery/epic/mythic/horror/intrigue/swashbuckling/war

    heroic = get_fantasy_style("heroic")
    assert heroic["name"] == "英雄奇幻"
    assert len(heroic["conflicts"]) == 3

    # 未知风格应抛异常
    try:
        get_fantasy_style("unknown")
        assert False, "应抛出ValueError"
    except ValueError:
        pass
    print("[campaign_manager] 奇幻风格查询 ✓")

    # ═══ 8. D&D设定查询 ═══
    settings = list_dnd_settings()
    assert len(settings) == 12  # dark_sun/dragonlance/eberron/exandria/forgotten_realms/greyhawk/planescape/ravenloft/ravnica/spelljammer/strixhaven/theros

    greyhawk_desc = DND_SETTINGS.get("greyhawk", "")
    assert "地下城" in greyhawk_desc or "搜刮" in greyhawk_desc
    print("[campaign_manager] D&D设定查询 ✓")

    # ═══ 9. 序列化 ═══
    camp_dict = camp.to_dict()
    assert camp_dict["name"] == "灰鹰编年史"
    assert camp_dict["tone"] == "heroic"
    assert camp_dict["setting"] == "greyhawk"
    assert camp_dict["ended"] is True
    assert camp_dict["current_level"] == 15
    assert len(camp_dict["sessions"]) == 3
    assert len(camp_dict["milestones"]) == 3
    print("[campaign_manager] 序列化 ✓")

    # ═══ 10. 完整流程集成 ═══
    # 模拟DMG第五章四步设计法的完整流程
    camp2 = create_campaign("北风舞会战役", tone="intrigue", setting="homebrew", seed=200)

    # 第1步已完成（布置背景）
    # 第2步：导入玩家 → 添加第零回
    add_session(camp2, is_session_zero=True, summary="第零回：角色创建，确立阴谋基调")

    # 第3步：规划冒险 → 添加多个回次
    for i in range(1, 4):
        add_session(camp2, adventure_id=f"adv_{i}", summary=f"第{i}回：推进阴谋剧情")

    # 记录关键事件
    log_campaign_event(camp2, "story", "角色们收到了神秘邀请函", ["神秘贵族"])
    log_campaign_event(camp2, "combat", "舞会遭到吸血鬼袭击", ["吸血鬼领主"], loot_gained=200)
    log_campaign_event(camp2, "social", "与间谍头目谈判", ["间谍大师"])

    # 第4步：步入终局
    end_result = end_campaign(camp2, method="grand_finale", final_level=10)

    # 验证完整状态
    assert camp2.tone == "intrigue"
    assert len(camp2.sessions) == 4  # 第零回 + 3回
    timeline2 = get_campaign_timeline(camp2)
    assert timeline2[0].session_number == 0
    assert timeline2[-1].session_number == 3
    assert end_result["total_sessions"] == 4
    assert end_result["total_log_entries"] == 3
    assert camp2.world_state.get("total_loot") == 200
    assert "吸血鬼领主" in camp2.world_state.get("key_npcs", [])
    print("[campaign_manager] 完整流程集成 ✓")

    print("[campaign_manager] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
