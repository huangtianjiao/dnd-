"""扩展专长数据 — TCoE(塔莎) + XGtE(珊娜萨)。

来源:
- 塔莎的万事坩埚\玩家选项\专长.html (15个通用专长)
- 珊娜萨的万事指南\角色选项\种族专长.html (15个种族专长)
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExpansionFeat:
    name: str
    en_name: str
    source: str             # "TCoE", "XGtE"
    category: str           # "通用", "种族"
    prerequisite: str = ""  # 先决条件
    effect: str = ""        # 核心效果


FEATS: dict[str, ExpansionFeat] = {}
FEATS_EN: dict[str, ExpansionFeat] = {}

def _reg(f: ExpansionFeat):
    FEATS[f.name] = f
    FEATS_EN[f.en_name.lower()] = f


# ═══════════════════════════════════════════════════════════════════════════
# TCoE 专长 (15个通用专长)
# ═══════════════════════════════════════════════════════════════════════════

_reg(ExpansionFeat("奇械学徒", "Artificer Initiate", "TCoE", "通用",
    prerequisite="智力13+",
    effect="习得一项奇械师戏法和一个1环奇械师法术（长休后恢复），可用工匠工具作为施法法器。"))

_reg(ExpansionFeat("大厨", "Chef", "TCoE", "通用",
    effect="+1体质或感知。短休时烹饪给盟友额外HP恢复，可用烹饪工具制作临时HP点心。"))

_reg(ExpansionFeat("粉碎者", "Crusher", "TCoE", "通用",
    prerequisite="",
    effect="+1力量或敏捷。钝击伤害命中可移动目标5尺；重击时此后对该目标的攻击有优势。"))

_reg(ExpansionFeat("魔能导师", "Eldritch Adept", "TCoE", "通用",
    prerequisite="施法能力或契约魔法",
    effect="习得一项魔能祈唤，若有前置条件则需满足邪术师等级替换条件。"))

_reg(ExpansionFeat("妖精触碰", "Fey Touched", "TCoE", "通用",
    effect="+1智力/感知/魅力。习得迷踪步和1个1环预言/附魔系法术，每长休各免费施放一次。"))

_reg(ExpansionFeat("战斗学徒", "Fighting Initiate", "TCoE", "通用",
    prerequisite="军用武器熟练",
    effect="习得战士的一种战斗风格。每次获得属性值提升时可更换。"))

_reg(ExpansionFeat("枪手", "Gunner", "TCoE", "通用",
    effect="+1敏捷。获得枪械熟练，忽略装填属性。5尺内远程攻击不具劣势。"))

_reg(ExpansionFeat("超魔法导师", "Metamagic Adept", "TCoE", "通用",
    prerequisite="施法能力或契约魔法",
    effect="习得两项超魔法选项，获得2点术法点（用于超魔法）。长休后恢复。"))

_reg(ExpansionFeat("穿刺者", "Piercer", "TCoE", "通用",
    effect="+1力量或敏捷。穿刺伤害每回合可重掷一次伤害骰。重击时额外+1骰穿刺伤害。"))

_reg(ExpansionFeat("毒师", "Poisoner", "TCoE", "通用",
    effect="忽略毒素抗性。附赠动作给武器涂毒（DC14，1d8毒素伤害，持续1分钟）。"))

_reg(ExpansionFeat("影界触碰", "Shadow Touched", "TCoE", "通用",
    effect="+1智力/感知/魅力。习得隐形术和1个1环死灵/幻术系法术，每长休各免费施放一次。"))

_reg(ExpansionFeat("技艺专家", "Skill Expert", "TCoE", "通用",
    effect="+1任一属性。获得一项技能熟练和一项技能专精。"))

_reg(ExpansionFeat("劈砍者", "Slasher", "TCoE", "通用",
    effect="+1力量或敏捷。挥砍伤害命中敌人降速10尺；重击时目标攻击劣势。"))

_reg(ExpansionFeat("念动力", "Telekinetic", "TCoE", "通用",
    effect="+1智力/感知/魅力。习得无形法师之手（60尺，隐形）。附赠推/拉30尺内豁免失败的生物5尺。"))

_reg(ExpansionFeat("心电感应", "Telepathic", "TCoE", "通用",
    effect="+1智力/感知/魅力。可与60尺内生物心灵交流（需要共同语言）。附赠侦测思想一次，长休恢复。"))


# ═══════════════════════════════════════════════════════════════════════════
# XGtE 种族专长 (15个)
# ═══════════════════════════════════════════════════════════════════════════

_reg(ExpansionFeat("龙之威怖", "Dragon Fear", "XGtE", "种族",
    prerequisite="龙裔",
    effect="+1力量/体质/魅力。替代龙息：30尺内生物感知豁免否则陷入恐慌1分钟。"))

_reg(ExpansionFeat("龙之鳞爪", "Dragon Hide", "XGtE", "种族",
    prerequisite="龙裔",
    effect="+1力量/体质/魅力。无甲AC=13+敏捷。获得1d4挥砍的爪击天生武器。"))

_reg(ExpansionFeat("矮人坚毅", "Dwarven Fortitude", "XGtE", "种族",
    prerequisite="矮人",
    effect="+1体质。战斗中闪避时可消耗一个生命骰恢复HP。"))

_reg(ExpansionFeat("低身机敏", "Squat Nimbleness", "XGtE", "种族",
    prerequisite="矮人或半身人",
    effect="+1力量或敏捷。速度+5尺。获得运动或特技熟练。逃脱擒抱时敏捷(特技)优势。"))

_reg(ExpansionFeat("精灵之准", "Elven Accuracy", "XGtE", "种族",
    prerequisite="精灵或半精灵",
    effect="+1敏捷/智力/感知/魅力。敏捷/智力/感知/魅力攻击优势时重掷一次d20。"))

_reg(ExpansionFeat("高等卓尔魔法", "Drow High Magic", "XGtE", "种族",
    prerequisite="卓尔精灵",
    effect="任意施展侦测魔法。每长休一次：浮空术、解除魔法。"))

_reg(ExpansionFeat("妖精传送", "Fey Teleportation", "XGtE", "种族",
    prerequisite="高等精灵",
    effect="+1智力或魅力。习得精灵语。每短休一次免费施放迷踪步。"))

_reg(ExpansionFeat("木精灵魔法", "Wood Elf Magic", "XGtE", "种族",
    prerequisite="木精灵",
    effect="习得一个德鲁伊戏法。每长休一次：大步奔行、行动无踪。"))

_reg(ExpansionFeat("匿影无踪", "Fade Away", "XGtE", "种族",
    prerequisite="侏儒",
    effect="+1敏捷或智力。受到伤害后以反应隐形至下回合开始。短休后恢复。"))

_reg(ExpansionFeat("天赋异禀", "Prodigy", "XGtE", "种族",
    prerequisite="半精灵/半兽人/人类",
    effect="获得一项技能熟练、一项工具熟练和一门语言的熟练。选择一个已有熟练的技能获得专精。"))

_reg(ExpansionFeat("兽人狂怒", "Orcish Fury", "XGtE", "种族",
    prerequisite="半兽人",
    effect="+1力量或体质。命中后可加一个额外武器伤害骰（短休恢复）。使用坚韧不屈后可以反应攻击。"))

_reg(ExpansionFeat("慷慨吉运", "Bountiful Luck", "XGtE", "种族",
    prerequisite="半身人",
    effect="30尺内盟友d20掷出1时，可反应让其重掷。需半身人的幸运特性。"))

_reg(ExpansionFeat("花开二度", "Second Chance", "XGtE", "种族",
    prerequisite="半身人",
    effect="+1敏捷/体质/魅力。被命中时反应强迫攻击者重掷攻击。短休后恢复。"))

_reg(ExpansionFeat("弗莱格索斯之焰", "Flames of Phlegethos", "XGtE", "种族",
    prerequisite="提夫林",
    effect="+1智力或魅力。火焰法术重掷伤害骰中的1。施展火焰法术后直到下回合结束被火焰环绕，近战攻击者受1d4火焰伤害。"))


# ═══════════════════════════════════════════════════════════════════════════
# 查询函数
# ═══════════════════════════════════════════════════════════════════════════

def get_feat(name: str) -> Optional[ExpansionFeat]:
    return FEATS.get(name) or FEATS_EN.get(name.lower())

def feats_by_source(source: str) -> list[ExpansionFeat]:
    return [f for f in FEATS.values() if f.source == source]

def feats_by_category(category: str) -> list[ExpansionFeat]:
    return [f for f in FEATS.values() if f.category == category]

def feats_for_race(race: str) -> list[ExpansionFeat]:
    """获取某种族可选的种族专长。"""
    matching = []
    race_lower = race.lower()
    race_map = {
        "龙裔": "龙裔", "dragonborn": "龙裔",
        "矮人": "矮人", "dwarf": "矮人",
        "精灵": "精灵", "elf": "精灵",
        "卓尔": "精灵", "drow": "精灵",
        "半精灵": "半精灵", "half-elf": "半精灵",
        "侏儒": "侏儒", "gnome": "侏儒",
        "半身人": "半身人", "halfling": "半身人",
        "人类": "人类", "human": "人类",
        "半兽人": "半兽人", "half-orc": "半兽人",
        "提夫林": "提夫林", "tiefling": "提夫林",
    }
    normalized = race_map.get(race_lower, race)
    for f in FEATS.values():
        if f.category == "种族" and normalized in f.prerequisite:
            matching.append(f)
    return matching


# ═══════════════════════════════════════════════════════════════════════════
# 自检
# ═══════════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    tcoe_feats = feats_by_source("TCoE")
    xgte_feats = feats_by_source("XGtE")
    assert len(tcoe_feats) == 15, f"TCoE专长应为15, 实有{len(tcoe_feats)}"
    assert len(xgte_feats) >= 14, f"XGtE种族专长不足: {len(xgte_feats)}"

    # 半身人专长
    halfling_feats = feats_for_race("半身人")
    assert len(halfling_feats) >= 2, f"半身人专长不足: {len(halfling_feats)}"

    # 精灵之准
    ea = get_feat("精灵之准")
    assert ea is not None and "精灵" in ea.prerequisite

    # 英文查询
    assert get_feat("elven accuracy") is not None

    print(f"[expansion_feats] 自检通过 ✓ ({len(FEATS)}专长, {len(tcoe_feats)}TCoE + {len(xgte_feats)}XGtE)")


if __name__ == "__main__":
    _self_test()
