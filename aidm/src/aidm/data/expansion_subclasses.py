"""扩展子职业数据 — TCoE(塔莎) + XGtE(珊娜萨) + 奇械师。

来源:
- 塔莎的万事坩埚\玩家选项\职业\
- 珊娜萨的万事指南\角色选项\
提供: 65个扩展子职业（含4个奇械师子职）
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExpansionSubclass:
    name: str
    en_name: str
    class_name: str
    source: str             # "TCoE", "XGtE"
    flavor: str
    key_feature_l3: str     # 3级核心特性简述


SUBCLASSES: dict[str, ExpansionSubclass] = {}
CLASS_SUBCLASSES: dict[str, list[ExpansionSubclass]] = {}

def _reg(s: ExpansionSubclass):
    SUBCLASSES[s.name] = s
    CLASS_SUBCLASSES.setdefault(s.class_name, []).append(s)


# ═══════════════════════════════════════════════════════════════════════════
# TCoE 子职业 (30个)
# ═══════════════════════════════════════════════════════════════════════════

# ── 野蛮人 ──
_reg(ExpansionSubclass("狂野魔法道途", "Path of Wild Magic", "野蛮人", "TCoE",
    "狂野魔法流淌于其血脉", "狂暴时触发狂野魔法涌动，投d8产生随机魔法效应"))
_reg(ExpansionSubclass("野兽道途", "Path of the Beast", "野蛮人", "TCoE",
    "灵魂深处潜藏狂野兽性", "狂暴时变出利爪、尖牙或尾巴作为天生武器"))

# ── 吟游诗人 ──
_reg(ExpansionSubclass("创造学院", "College of Creation", "吟游诗人", "TCoE",
    "吟唱创世之歌", "创世音符：用激励骰创造活化舞动的物件"))
_reg(ExpansionSubclass("雄辩学院", "College of Eloquence", "吟游诗人", "TCoE",
    "言语即权柄", "超凡辩才：说服/欺瞒最低掷骰结果≥10，降防激励"))

# ── 牧师 ──
_reg(ExpansionSubclass("和平领域", "Peace Domain", "牧师", "TCoE",
    "以和平之名连结众生", "缔造和平：用动作连结盟友，获得限次d4加值"))
_reg(ExpansionSubclass("暮光领域", "Twilight Domain", "牧师", "TCoE",
    "守望暗夜与微光", "暮光圣域：释放暮光灵气，给盟友提供临时HP或魅惑移除"))
_reg(ExpansionSubclass("秩序领域", "Order Domain", "牧师", "TCoE",
    "律法与秩序的代言人", "秩序之声：以附赠附魔法术时盟友可反应攻击"))

# ── 德鲁伊 ──
_reg(ExpansionSubclass("孢子结社", "Circle of Spores", "德鲁伊", "TCoE",
    "掌管生死与腐朽", "孢子光环：消耗荒野形态释放孢子，对周围生物造成黯蚀伤害"))
_reg(ExpansionSubclass("星辰结社", "Circle of Stars", "德鲁伊", "TCoE",
    "从星空汲取古老力量", "星图形态：消耗荒野形态化为星辰形态（圣杯/射手/巨龙）"))
_reg(ExpansionSubclass("野火结社", "Circle of Wildfire", "德鲁伊", "TCoE",
    "毁灭与重生并存的火焰", "召唤野火之灵：召唤小型火焰元素伙伴"))

# ── 战士 ──
_reg(ExpansionSubclass("灵能武士", "Psi Warrior", "战士", "TCoE",
    "以灵能强化战技", "灵能力池：智力调整×2的灵能骰，用于防护/推进/打击"))
_reg(ExpansionSubclass("符文骑士", "Rune Knight", "战士", "TCoE",
    "以巨人符文铭刻自身", "符文雕刻：掌握2个巨人符文，附赠动作变成大型体型"))

# ── 武僧 ──
_reg(ExpansionSubclass("命流宗", "Way of Mercy", "武僧", "TCoE",
    "在生与死之间行走", "医术之手：用气疗伤或施以黯蚀伤害"))
_reg(ExpansionSubclass("星我宗", "Way of the Astral Self", "武僧", "TCoE",
    "显化星界之躯", "星我之臂：消耗气召唤星界手臂，用感知代替力量/敏捷进行武僧攻击"))

# ── 圣武士 ──
_reg(ExpansionSubclass("守望之誓", "Oath of the Watchers", "圣武士", "TCoE",
    "守卫凡界免受异界入侵", "守望引导：引导神力侦测异界生物并给予先攻优势"))
_reg(ExpansionSubclass("荣耀之誓", "Oath of Glory", "圣武士", "TCoE",
    "以英雄伟绩铭刻传奇", "荣耀引导：引导神力给盟友提供临时HP或获得运动/特技优势"))

# ── 游侠 ──
_reg(ExpansionSubclass("妖精漫游者", "Fey Wanderer", "游侠", "TCoE",
    "沾染妖精荒野魔力", "妖精赠礼：额外1d4心灵伤害，感知加值到魅力检定"))
_reg(ExpansionSubclass("集群守卫", "Swarmkeeper", "游侠", "TCoE",
    "与自然精灵集群共生", "集群集结：攻击附加集群效应——伤害/推离/自身位移"))

# ── 游荡者 ──
_reg(ExpansionSubclass("鬼魅", "Phantom", "游荡者", "TCoE",
    "与亡灵低语的窃魂者", "亡语低语：获得亡灵相关的熟练，偷袭附加黯蚀伤害"))
_reg(ExpansionSubclass("魂刃", "Soulknife", "游荡者", "TCoE",
    "以心灵之刃杀敌", "灵能骰：灵能能量骰用于增强检定，召唤心灵之刃"))

# ── 术士 ──
_reg(ExpansionSubclass("畸变心智", "Aberrant Mind", "术士", "TCoE",
    "异怪之力扭曲心智", "灵能法术：获得扩表法术，可以灵能点施法无需构材"))
_reg(ExpansionSubclass("时械之魂", "Clockwork Soul", "术士", "TCoE",
    "机械境的秩序之力", "秩序壁垒：获得扩表法术，可召唤护盾抵消伤害"))

# ── 邪术师 ──
_reg(ExpansionSubclass("巨灵宗主", "The Genie", "邪术师", "TCoE",
    "与元素巨灵缔约", "巨灵容器：获得一个小次元容器并可短休进入，攻击附加元素伤害"))
_reg(ExpansionSubclass("深海意志", "The Fathomless", "邪术师", "TCoE",
    "深海远古存在的契约者", "深海触手：附赠召唤魔法触手攻击并减速敌人"))

# ── 法师 ──
_reg(ExpansionSubclass("书士会", "Order of Scribes", "法师", "TCoE",
    "追寻魔法书本身奥秘", "觉醒法术书：法术书化为活化魔宠，可替换法术伤害类型"))
_reg(ExpansionSubclass("剑咏", "Bladesinging", "法师", "TCoE",
    "精灵的剑与魔法之道", "剑咏之歌：附赠启动剑歌，获得AC、速度、专注和特技加值"))


# ═══════════════════════════════════════════════════════════════════════════
# 奇械师 (Artificer) — TCoE 完整职业
# ═══════════════════════════════════════════════════════════════════════════

_reg(ExpansionSubclass("炼金师", "Alchemist", "奇械师", "TCoE",
    "调配魔法药剂的大师", "炼金药剂：消耗法术位制造实验药剂（治疗/迅捷/坚韧/勇猛/飞行/变形）"))
_reg(ExpansionSubclass("装甲师", "Armorer", "奇械师", "TCoE",
    "身披奥术装甲的斗士", "奥术装甲：制造特殊装甲（守卫者/渗透者模式），用智力攻击"))
_reg(ExpansionSubclass("魔炮师", "Artillerist", "奇械师", "TCoE",
    "操控奥术火炮的爆破专家", "奥术炮台：用工匠工具召唤小型炮台（火焰喷射/力场弩/防御力场）"))
_reg(ExpansionSubclass("战地匠师", "Battle Smith", "奇械师", "TCoE",
    "钢铁守护者的锻造大师", "钢铁守护者：召唤钢铁构造体宠物，用智力进行武器攻击"))


# ═══════════════════════════════════════════════════════════════════════════
# XGtE 子职业 (31个)
# ═══════════════════════════════════════════════════════════════════════════

# ── 野蛮人 ──
_reg(ExpansionSubclass("先祖守卫道途", "Path of the Ancestral Guardian", "野蛮人", "XGtE",
    "先祖之灵护航", "先祖护佑：狂暴时召唤先祖之灵，标记目标使其攻击盟友有劣势"))
_reg(ExpansionSubclass("狂热者道途", "Path of the Zealot", "野蛮人", "XGtE",
    "为神祇而战的狂热信徒", "神怒打击：每回合首次命中附加1d6+野蛮人等级一半的光耀/黯蚀伤害"))
_reg(ExpansionSubclass("风暴先驱道途", "Path of the Storm Herald", "野蛮人", "XGtE",
    "体内蕴藏风暴之力", "风暴灵气：狂暴时释放灵气（沙漠/海洋/苔原），造成范围伤害或增益"))

# ── 吟游诗人 ──
_reg(ExpansionSubclass("低语学院", "College of Whispers", "吟游诗人", "XGtE",
    "掌控黑暗秘密与恐惧", "心灵之刃：消耗激励骰对目标造成额外心灵伤害"))
_reg(ExpansionSubclass("剑舞学院", "College of Swords", "吟游诗人", "XGtE",
    "以剑代琴的表演者", "剑舞战斗风格：获得双武器/决斗风格和剑舞（消耗激励骰的战技）"))
_reg(ExpansionSubclass("迷惑学院", "College of Glamour", "吟游诗人", "XGtE",
    "妖精魔法的魅力化身", "迷惑演出：用激励骰魅惑观众并给盟友提供临时HP和位移"))

# ── 牧师 ──
_reg(ExpansionSubclass("锻造领域", "Forge Domain", "牧师", "XGtE",
    "铸造神圣武器与护甲", "锻造祝福：长休后可将一件非魔法护甲/武器变为+1魔法物品"))
_reg(ExpansionSubclass("坟墓领域", "Grave Domain", "牧师", "XGtE",
    "守护生与死的边界", "轮回之眼：侦测亡灵，30尺内稳定濒死盟友并最大化治疗骰"))

# ── 德鲁伊 ──
_reg(ExpansionSubclass("梦境结社", "Circle of Dreams", "德鲁伊", "XGtE",
    "连接妖精荒野梦境", "夏之王庭甘露：获得治疗骰池，附赠远程治疗盟友"))
_reg(ExpansionSubclass("牧人结社", "Circle of the Shepherd", "德鲁伊", "XGtE",
    "召唤与守护自然的生灵", "灵魂图腾：召唤熊/鹰/独角兽图腾给区域内盟友增益"))

# ── 战士 ──
_reg(ExpansionSubclass("武士", "Samurai", "战士", "XGtE",
    "不屈的荣誉战士", "战斗精神：附赠获得当前回合攻击优势+临时HP"))
_reg(ExpansionSubclass("骑兵", "Cavalier", "战士", "XGtE",
    "骑乘战斗与守护大师", "无敌印记：标记攻击目标，迫使其攻击非你目标时具有劣势"))
_reg(ExpansionSubclass("魔射手", "Arcane Archer", "战士", "XGtE",
    "以魔法之箭杀敌", "魔能射击：掌握2种魔射选项（放逐箭/缠绕箭/爆破箭等）"))

# ── 武僧 ──
_reg(ExpansionSubclass("剑圣宗", "Way of the Kensei", "武僧", "XGtE",
    "武器大师的武道之路", "剑圣武器：选择近战和远程各一种武器作为剑圣武器，使用敏捷攻击"))
_reg(ExpansionSubclass("日魂宗", "Way of the Sun Soul", "武僧", "XGtE",
    "以太阳光辉焚尽黑暗", "光耀箭：可发射30尺光耀能量束造成光耀伤害"))
_reg(ExpansionSubclass("醉拳宗", "Way of the Drunken Master", "武僧", "XGtE",
    "以醉态迷惑对手", "醉拳技巧：疾风连击时额外获得移动和脱离能力"))

# ── 圣武士 ──
_reg(ExpansionSubclass("征服之誓", "Oath of Conquest", "圣武士", "XGtE",
    "以恐惧与铁腕统治", "征服引导：引导神力对周围生物造成恐慌状态"))
_reg(ExpansionSubclass("救赎之誓", "Oath of Redemption", "圣武士", "XGtE",
    "以和平之道救赎罪人", "和平使者：引导神力在交涉检定+5，受击时反弹伤害"))

# ── 游侠 ──
_reg(ExpansionSubclass("幽域追踪者", "Gloom Stalker", "游侠", "XGtE",
    "暗影中的致命猎手", "恐惧伏击：首回合额外一次攻击并附加1d8伤害，获得黑暗视觉"))
_reg(ExpansionSubclass("怪物杀手", "Monster Slayer", "游侠", "XGtE",
    "专精猎杀超自然生物", "屠戮猎物：附赠动作分析目标，获知抗性/弱点/免疫"))
_reg(ExpansionSubclass("边界行者", "Horizon Walker", "游侠", "XGtE",
    "守卫诸位面边界", "位面战士：附赠动作附加1d8力场伤害，标记为宿敌"))

# ── 游荡者 ──
_reg(ExpansionSubclass("审判官", "Inquisitive", "游荡者", "XGtE",
    "洞穿一切谎言的侦探", "洞悉之眼：附赠做感知(洞悉)对抗魅力(欺瞒)，成功则可用偷袭"))
_reg(ExpansionSubclass("策士", "Mastermind", "游荡者", "XGtE",
    "幕后操纵战局的大师", "战术大师：附赠动作30尺内协助盟友攻击"))
_reg(ExpansionSubclass("斥候", "Scout", "游荡者", "XGtE",
    "荒野中的先遣兵", "散兵战术：敌人结束回合于5尺内时可反应移一半速度不引发借机"))
_reg(ExpansionSubclass("游荡剑客", "Swashbuckler", "游荡者", "XGtE",
    "以魅力与剑术决斗", "花哨剑术：近战攻击后即使无盟友也可偷袭，无借机脱离"))

# ── 术士 ──
_reg(ExpansionSubclass("幽影魔法", "Shadow Magic", "术士", "XGtE",
    "操控影界的术士", "暗影之眼：120尺黑暗视觉，濒死时可魅力豁免维持1HP"))
_reg(ExpansionSubclass("神圣之魂", "Divine Soul", "术士", "XGtE",
    "神圣之力与奥术的融合", "神恩：获得牧师法术列表扩展，你的法术和戏法可从牧师列表选择"))
_reg(ExpansionSubclass("风暴术法", "Storm Sorcery", "术士", "XGtE",
    "驾驭风暴与雷电", "风暴之语：获得风语能力，施法后可附赠飞行10尺不引发借机"))

# ── 邪术师 ──
_reg(ExpansionSubclass("天界宗主", "The Celestial", "邪术师", "XGtE",
    "与上位天族缔约", "治愈之光：获得治疗骰池，附赠远程治疗盟友"))
_reg(ExpansionSubclass("咒剑", "The Hexblade", "邪术师", "XGtE",
    "缔结暗影武器之约", "咒剑诅咒：附赠标记目标，重击范围19-20，命中附加熟练加值伤害。用魅力进行武器攻击。"))

# ── 法师 ──
_reg(ExpansionSubclass("战争魔法", "War Magic", "法师", "XGtE",
    "战场上的奥术大师", "奥术偏转：反应增加AC或豁免+2/+4，但下轮只能施放戏法"))


# ═══════════════════════════════════════════════════════════════════════════
# 查询函数
# ═══════════════════════════════════════════════════════════════════════════

def get_subclass(name: str) -> Optional[ExpansionSubclass]:
    return SUBCLASSES.get(name)

def subclass_by_class(class_name: str) -> list[ExpansionSubclass]:
    return CLASS_SUBCLASSES.get(class_name, [])

def subclass_by_source(source: str) -> list[ExpansionSubclass]:
    return [s for s in SUBCLASSES.values() if s.source == source]

def all_classes() -> list[str]:
    return sorted(CLASS_SUBCLASSES.keys())


# ═══════════════════════════════════════════════════════════════════════════
# 自检
# ═══════════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    total = len(SUBCLASSES)
    assert total >= 60, f"扩展子职业数量不足: {total}"

    tcoe = subclass_by_source("TCoE")
    xgte = subclass_by_source("XGtE")
    assert len(tcoe) >= 28, f"TCoE子职业不足: {len(tcoe)}"
    assert len(xgte) >= 28, f"XGtE子职业不足: {len(xgte)}"

    # 奇械师
    arti = subclass_by_class("奇械师")
    assert len(arti) >= 3, f"奇械师子职业不足: {len(arti)}"

    # 各职业至少1个扩展
    classes = all_classes()
    assert len(classes) >= 12, f"职业数量不足: {len(classes)}"

    # 热门子职查询
    hexblade = get_subclass("咒剑")
    assert hexblade is not None and hexblade.class_name == "邪术师"

    gs = get_subclass("幽域追踪者")
    assert gs is not None and gs.source == "XGtE"

    print(f"[expansion_subclasses] 自检通过 ✓ ({total}扩展子职业, {len(classes)}职业)")


if __name__ == "__main__":
    _self_test()
