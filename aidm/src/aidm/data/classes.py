"""职业数据表 — 12 个核心职业。

纯数据 + 少量计算。每条记录标注规则ID+出处。
数据来源: topics/玩家手册2024/角色职业/<职业>/<职业>.htm
"""

from __future__ import annotations


# ──────────────────────────────────────────────────────────────────────────
# 属性缩写
# STR 力量 / DEX 敏捷 / CON 体质 / INT 智力 / WIS 感知 / CHA 魅力
# ──────────────────────────────────────────────────────────────────────────

# 职业主属性、生命骰面值、豁免熟练、技能熟练选择池、技能选择数量、
# 武器熟练、护甲受训、起始装备、施法属性(可空)、子职列表、子职等级
CLASSES = {
    # ── 野蛮人 ──────────────────────────────────────────────
    "野蛮人": {
        "primary": ["STR"],
        "hit_die": 12,
        "save_prof": ["STR", "CON"],
        "skill_pool": ["驯兽", "运动", "威吓", "自然", "察觉", "求生"],
        "skill_pick": 2,
        "weapon_prof": "简易和军用武器",
        "armor_training": "轻甲、中甲和盾牌",
        "starting_equipment": "巨斧，4把手斧，探索套组以及15GP；或者75GP",
        "spellcasting": None,
        "subclasses": ["狂战士道途", "兽心道途", "世界树道途", "狂热者道途"],
        "subclass_level": 3,
    },
    # ── 吟游诗人 ────────────────────────────────────────────
    "吟游诗人": {
        "primary": ["CHA"],
        "hit_die": 8,
        "save_prof": ["DEX", "CHA"],
        "skill_pool": "任意",   # 任选3项（见第一章）
        "skill_pick": 3,
        "weapon_prof": "简易武器",
        "armor_training": "轻甲",
        "starting_equipment": "皮甲，2把匕首，你选择的乐器，艺人套组以及19GP；或者90GP",
        "spellcasting": "CHA",
        "subclasses": ["逸闻学院", "勇气学院", "舞蹈学院", "魅心学院"],
        "subclass_level": 3,
    },
    # ── 牧师 ────────────────────────────────────────────────
    "牧师": {
        "primary": ["WIS"],
        "hit_die": 8,
        "save_prof": ["WIS", "CHA"],
        "skill_pool": ["历史", "洞悉", "医药", "游说", "宗教"],
        "skill_pick": 2,
        "weapon_prof": "简易武器",
        "armor_training": "轻甲、中甲和盾牌",
        "starting_equipment": "链甲衫，盾牌，硬头锤，圣徽，祭司套组以及7GP；或110GP",
        "spellcasting": "WIS",
        "subclasses": ["生命领域", "光明领域", "诡术领域", "战争领域"],
        "subclass_level": 1,
    },
    # ── 德鲁伊 ──────────────────────────────────────────────
    "德鲁伊": {
        "primary": ["WIS"],
        "hit_die": 8,
        "save_prof": ["INT", "WIS"],
        "skill_pool": ["奥秘", "驯兽", "洞悉", "医疗", "自然", "察觉", "宗教", "求生"],
        "skill_pick": 2,
        "weapon_prof": "简易武器",
        "armor_training": "轻甲和盾牌",
        "starting_equipment": "皮甲，盾牌，镰刀，德鲁伊法器（长棍），探索套组，草药工具以及9GP；或者50GP",
        "spellcasting": "WIS",
        "subclasses": ["大地结社", "月亮结社", "星辰结社", "海洋结社"],
        "subclass_level": 2,
    },
    # ── 战士 ────────────────────────────────────────────────
    "战士": {
        "primary": ["STR", "DEX"],   # 力量或敏捷
        "hit_die": 10,
        "save_prof": ["STR", "CON"],
        "skill_pool": ["特技", "驯兽", "运动", "历史", "洞悉", "威吓", "游说", "察觉", "求生"],
        "skill_pick": 2,
        "weapon_prof": "简易和军用武器",
        "armor_training": "轻甲、中甲、重甲和盾牌",
        "starting_equipment": "(A)链甲，巨剑，链枷，8杆标枪，地城套组以及4GP；(B)镶钉皮甲，弯刀，短剑，长弓，20支箭矢，箭袋，地城套组以及11GP；(C)155GP",
        "spellcasting": None,
        "subclasses": ["勇士", "战斗大师", "奥法骑士", "灵能武士"],
        "subclass_level": 3,
    },
    # ── 武僧 ────────────────────────────────────────────────
    "武僧": {
        "primary": ["DEX", "WIS"],   # 敏捷与感知
        "hit_die": 8,
        "save_prof": ["STR", "DEX"],
        "skill_pool": ["特技", "运动", "历史", "洞悉", "宗教", "隐匿"],
        "skill_pick": 2,
        "weapon_prof": "简易与具有轻型词条的军用武器",
        "armor_training": "无",
        "starting_equipment": "矛，5把匕首，你在工具熟练中所选择的工匠工具或乐器，探索套组以及11GP；或者50GP",
        "spellcasting": None,
        "subclasses": ["散打武者", "命流武者", "四象武者", "暗影武者"],
        "subclass_level": 3,
    },
    # ── 圣武士 ──────────────────────────────────────────────
    "圣武士": {
        "primary": ["STR", "CHA"],   # 力量与魅力
        "hit_die": 10,
        "save_prof": ["WIS", "CHA"],
        "skill_pool": ["运动", "洞悉", "威吓", "医疗", "游说", "宗教"],
        "skill_pick": 2,
        "weapon_prof": "简易和军用武器",
        "armor_training": "轻甲、中甲、重甲和盾牌",
        "starting_equipment": "链甲，盾牌，长剑，6杆标枪，圣徽，祭司套组以及9GP；或者150GP",
        "spellcasting": "CHA",
        "subclasses": ["奉献之誓", "复仇之誓", "古贤之誓", "荣耀之誓"],
        "subclass_level": 3,
    },
    # ── 游侠 ────────────────────────────────────────────────
    "游侠": {
        "primary": ["DEX", "WIS"],   # 敏捷与感知
        "hit_die": 10,
        "save_prof": ["STR", "DEX"],
        "skill_pool": ["驯兽", "运动", "洞悉", "调查", "自然", "察觉", "隐匿", "求生"],
        "skill_pick": 3,
        "weapon_prof": "简易和军用武器",
        "armor_training": "轻甲、中甲和盾牌",
        "starting_equipment": "镶钉皮甲，弯刀，短剑，长弓，20支箭矢，箭袋，德鲁伊法器（槲寄生枝条），探索套组以及7GP；或者150GP",
        "spellcasting": "WIS",
        "subclasses": ["猎人", "驯兽师", "妖精漫游者", "幽域追猎者"],
        "subclass_level": 3,
    },
    # ── 游荡者 ──────────────────────────────────────────────
    "游荡者": {
        "primary": ["DEX"],
        "hit_die": 8,
        "save_prof": ["DEX", "INT"],
        "skill_pool": ["特技", "运动", "欺瞒", "洞悉", "威吓", "调查", "察觉", "巧手", "表演", "游说", "隐匿"],
        "skill_pick": 4,
        "weapon_prof": "简易武器和具有灵巧或轻型词条的军用武器",
        "armor_training": "轻甲",
        "starting_equipment": "皮甲，2把匕首，短剑，短弓，20支箭矢，箭袋，盗贼工具，窃贼套组以及8GP；或者100GP",
        "spellcasting": None,
        "subclasses": ["盗贼", "刺客", "诡术师", "魂刃"],
        "subclass_level": 3,
    },
    # ── 术士 ────────────────────────────────────────────────
    "术士": {
        "primary": ["CHA"],
        "hit_die": 6,
        "save_prof": ["CON", "CHA"],
        "skill_pool": ["奥秘", "欺瞒", "洞悉", "威吓", "游说", "宗教"],
        "skill_pick": 2,
        "weapon_prof": "简易武器",
        "armor_training": "无",
        "starting_equipment": "矛，2把匕首，奥术法器（水晶），地城套组以及28GP；或者50GP",
        "spellcasting": "CHA",
        "subclasses": ["龙族术法", "狂野术法", "畸变术法", "时械术法"],
        "subclass_level": 1,
    },
    # ── 魔契师 ──────────────────────────────────────────────
    "魔契师": {
        "primary": ["CHA"],
        "hit_die": 8,
        "save_prof": ["WIS", "CHA"],
        "skill_pool": ["奥秘", "欺瞒", "历史", "威吓", "调查", "自然", "宗教"],
        "skill_pick": 2,
        "weapon_prof": "简易武器",
        "armor_training": "轻甲",
        "starting_equipment": "皮甲，镰刀，2把匕首，奥术法器（法球），书（隐秘学识），学者套组以及15GP；或者100GP",
        "spellcasting": "CHA",
        "subclasses": ["至高妖精宗主", "邪魔宗主", "天界宗主", "旧日支配者宗主"],
        "subclass_level": 3,
    },
    # ── 法师 ────────────────────────────────────────────────
    "法师": {
        "primary": ["INT"],
        "hit_die": 6,
        "save_prof": ["INT", "WIS"],
        "skill_pool": ["奥秘", "历史", "洞悉", "调查", "医疗", "自然", "宗教"],
        "skill_pick": 2,
        "weapon_prof": "简易武器",
        "armor_training": "无",
        "starting_equipment": "2把匕首，奥术法器（长棍），长袍，法术书，学者套组以及5GP；或55GP",
        "spellcasting": "INT",
        "subclasses": ["防护师", "塑能师", "幻术师", "预言师"],
        "subclass_level": 2,
    },
}


def get_class(name: str) -> dict:
    """取职业条目。"""
    if name not in CLASSES:
        raise KeyError(f"未知职业 {name!r}，可选: {list(CLASSES)}")
    return CLASSES[name]


def class_names() -> list[str]:
    """返回全部职业名（按定义顺序）。"""
    return list(CLASSES)


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    assert len(CLASSES) == 12, f"应有12个职业，实有{len(CLASSES)}"
    # 关键数值抽查（出处: 各职业 .htm 核心特质表）
    assert CLASSES["野蛮人"]["hit_die"] == 12
    assert CLASSES["法师"]["hit_die"] == 6
    assert CLASSES["战士"]["hit_die"] == 10
    assert CLASSES["术士"]["hit_die"] == 6
    assert CLASSES["圣武士"]["hit_die"] == 10
    # 施法属性
    assert CLASSES["吟游诗人"]["spellcasting"] == "CHA"
    assert CLASSES["法师"]["spellcasting"] == "INT"
    assert CLASSES["德鲁伊"]["spellcasting"] == "WIS"
    assert CLASSES["魔契师"]["spellcasting"] == "CHA"
    assert CLASSES["战士"]["spellcasting"] is None
    # 豁免熟练
    assert set(CLASSES["野蛮人"]["save_prof"]) == {"STR", "CON"}
    assert set(CLASSES["游荡者"]["save_prof"]) == {"DEX", "INT"}
    # 子职数量
    for name, data in CLASSES.items():
        assert len(data["subclasses"]) == 4, f"{name} 应有4个子职"
    print("[classes] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
