"""背景数据表 — 16 种背景。

纯数据 + 少量计算。每条记录标注出处。
数据来源: topics/玩家手册2024/角色起源/背景/<背景>.htm

背景结构（见 起源的构成部分.htm）：
- ability_scores：背景列出的三项属性值
- feat：背景提供的起源专长
- skill_prof：背景赋予的两种特定技能熟练
- tool_prof：工具熟练（可是一种特定工具，也可以是从工匠工具类别中选择的一种）
- equipment：装备（一套行装或50GP）
"""

from __future__ import annotations

# 属性缩写: STR 力量 / DEX 敏捷 / CON 体质 / INT 智力 / WIS 感知 / CHA 魅力
BACKGROUNDS = {
    # ── 侍僧 Acolyte ─────────────────────────────────────
    "侍僧": {
        "ability_scores": ["INT", "WIS", "CHA"],
        "feat": "魔法学徒（牧师）",
        "skill_prof": ["洞悉", "宗教"],
        "tool_prof": "书法工具",
        "equipment": "(A)书法工具、书籍（祈祷文）、圣徽、羊皮纸（10张）、长袍、8GP；或(B)50GP",
    },
    # ── 警卫 Guard ───────────────────────────────────────
    "警卫": {
        "ability_scores": ["STR", "INT", "WIS"],
        "feat": "警戒",
        "skill_prof": ["运动", "察觉"],
        "tool_prof": "选择一种赌具",
        "equipment": "(A)矛、轻弩、20弩矢、赌具（同上所选）、附盖提灯、镣铐、箭袋、旅行者服装、12GP；或(B)50GP",
    },
    # ── 水手 Sailor ──────────────────────────────────────
    "水手": {
        "ability_scores": ["STR", "DEX", "WIS"],
        "feat": "酒馆斗殴者",
        "skill_prof": ["特技", "察觉"],
        "tool_prof": "领航工具",
        "equipment": "(A)匕首、领航工具、绳索、旅行者服装、20GP；或(B)50GP",
    },
    # ── 工匠 Artisan ─────────────────────────────────────
    "工匠": {
        "ability_scores": ["STR", "DEX", "INT"],
        "feat": "巧匠",
        "skill_prof": ["调查", "游说"],
        "tool_prof": "选择一种工匠工具",
        "equipment": "(A)工匠工具（同上所选）、2小包、旅行者服装、32GP；或(B)50GP",
    },
    # ── 向导 Guide ───────────────────────────────────────
    "向导": {
        "ability_scores": ["DEX", "CON", "WIS"],
        "feat": "魔法学徒（德鲁伊）",
        "skill_prof": ["隐匿", "求生"],
        "tool_prof": "制图工具",
        "equipment": "(A)短弓、20支箭、制图工具、铺盖、箭袋、帐篷、旅行者服装、3GP；或(B)50GP",
    },
    # ── 抄写员 Scribe ────────────────────────────────────
    "抄写员": {
        "ability_scores": ["DEX", "INT", "WIS"],
        "feat": "熟习",
        "skill_prof": ["调查", "察觉"],
        "tool_prof": "书法工具",
        "equipment": "(A)书法工具、高档服装、油灯、灯油（3瓶）、羊皮纸（12张）、23GP；或(B)50GP",
    },
    # ── 骗子 Charlatan ───────────────────────────────────
    "骗子": {
        "ability_scores": ["DEX", "CON", "CHA"],
        "feat": "熟习",
        "skill_prof": ["欺瞒", "巧手"],
        "tool_prof": "文书伪造工具",
        "equipment": "(A)文书伪造工具、表演服装、高档服装、15GP；或(B)50GP",
    },
    # ── 隐士 Hermit ──────────────────────────────────────
    "隐士": {
        "ability_scores": ["CON", "WIS", "CHA"],
        "feat": "医疗师",
        "skill_prof": ["医药", "宗教"],
        "tool_prof": "草药工具",
        "equipment": "(A)长棍、草药工具、铺盖、书籍（哲学）、油灯、灯油（3扁瓶）、旅行者服装、16GP；或(B)50GP",
    },
    # ── 士兵 Soldier ─────────────────────────────────────
    "士兵": {
        "ability_scores": ["STR", "DEX", "CON"],
        "feat": "凶蛮打手",
        "skill_prof": ["运动", "威吓"],
        "tool_prof": "选择一种赌具",
        "equipment": "(A)矛、短弓、20支箭、赌具（同上所选）、医疗包、箭袋、旅行者服装、14GP；或(B)50GP",
    },
    # ── 罪犯 Criminal ────────────────────────────────────
    "罪犯": {
        "ability_scores": ["DEX", "CON", "INT"],
        "feat": "警戒",
        "skill_prof": ["巧手", "隐匿"],
        "tool_prof": "盗贼工具",
        "equipment": "(A)2匕首、盗贼工具、撬棍、2小包、旅行者服装、16GP；或(B)50GP",
    },
    # ── 商人 Merchant ────────────────────────────────────
    "商人": {
        "ability_scores": ["CON", "INT", "CHA"],
        "feat": "幸运",
        "skill_prof": ["驯兽", "游说"],
        "tool_prof": "领航工具",
        "equipment": "(A)领航工具、2个小包、旅行者服装、22GP；或(B)50GP",
    },
    # ── 流浪者 Wayfarer ──────────────────────────────────
    "流浪者": {
        "ability_scores": ["DEX", "WIS", "CHA"],
        "feat": "幸运",
        "skill_prof": ["洞悉", "隐匿"],
        "tool_prof": "盗贼工具",
        "equipment": "(A)2匕首、盗贼工具、赌具（任意）、铺盖、2小包、旅行者服装、16GP；或(B)50GP",
    },
    # ── 艺人 Entertainer ─────────────────────────────────
    "艺人": {
        "ability_scores": ["STR", "DEX", "CHA"],
        "feat": "音乐家",
        "skill_prof": ["特技", "表演"],
        "tool_prof": "选择一种乐器",
        "equipment": "(A)乐器（同上所选）、2件表演服装、镜子、香水、旅行者服装、11GP；或(B)50GP",
    },
    # ── 贵族 Noble ───────────────────────────────────────
    "贵族": {
        "ability_scores": ["STR", "INT", "CHA"],
        "feat": "熟习",
        "skill_prof": ["历史", "游说"],
        "tool_prof": "选择一种赌具",
        "equipment": "(A)赌具（同上所选）、高档服装、香水、29GP；或(B)50GP",
    },
    # ── 农民 Farmer ──────────────────────────────────────
    "农民": {
        "ability_scores": ["STR", "CON", "WIS"],
        "feat": "健壮",
        "skill_prof": ["驯兽", "自然"],
        "tool_prof": "木匠工具",
        "equipment": "(A)镰刀、木匠工具、医疗包、铁壶、铲子、旅行者的衣服、30GP；或(B)50GP",
    },
    # ── 智者 Sage ────────────────────────────────────────
    "智者": {
        "ability_scores": ["CON", "INT", "WIS"],
        "feat": "魔法学徒（法师）",
        "skill_prof": ["奥秘", "历史"],
        "tool_prof": "书法工具",
        "equipment": "(A)长棍、书法工具、书籍（历史）、羊皮纸（8张）、长袍、8GP；或(B)50GP",
    },
}


def get_background(name: str) -> dict:
    """取背景条目。"""
    if name not in BACKGROUNDS:
        raise KeyError(f"未知背景 {name!r}，可选: {list(BACKGROUNDS)}")
    return BACKGROUNDS[name]


def background_names() -> list[str]:
    """返回全部背景名（按定义顺序）。"""
    return list(BACKGROUNDS)


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    assert len(BACKGROUNDS) == 16, f"应有16个背景，实有{len(BACKGROUNDS)}"
    # 关键数值抽查（出处: 各背景 .htm）
    assert BACKGROUNDS["侍僧"]["ability_scores"] == ["INT", "WIS", "CHA"]
    assert BACKGROUNDS["侍僧"]["skill_prof"] == ["洞悉", "宗教"]
    assert BACKGROUNDS["士兵"]["skill_prof"] == ["运动", "威吓"]
    assert BACKGROUNDS["农民"]["feat"] == "健壮"
    assert BACKGROUNDS["智者"]["feat"] == "魔法学徒（法师）"
    # 所有背景都有完整字段
    for name, data in BACKGROUNDS.items():
        assert len(data["ability_scores"]) == 3, f"{name} 应有3项属性"
        assert len(data["skill_prof"]) == 2, f"{name} 应有2项技能熟练"
        assert data["feat"], f"{name} 缺少专长"
    print("[backgrounds] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
