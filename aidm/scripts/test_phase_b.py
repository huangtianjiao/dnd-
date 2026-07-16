"""Phase B 自检测试 — 验证角色创建流程的数值正确性。

运行: PYTHONPATH=src python scripts/test_phase_b.py
"""

from __future__ import annotations

import sys
import os

# 确保 src 在路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aidm.data.classes import CLASSES, get_class, class_names
from aidm.data.races import RACES, get_race, race_names
from aidm.data.backgrounds import BACKGROUNDS, get_background, background_names
from aidm.brain.char_create import (
    CharacterSheet,
    ability_modifier,
    proficiency_bonus,
    hit_points_level1,
    unarmored_ac,
    initiative,
    passive_perception,
    spell_save_dc,
    spell_attack_bonus,
    STANDARD_ARRAY,
    POINT_BUY_COST,
    POINT_BUY_BUDGET,
    ALIGNMENTS,
    step1_choose_class,
    step2_choose_origin,
    step3_assign_ability_scores,
    step4_choose_alignment,
    step5_enrich_details,
    create_character,
    validate_point_buy,
    point_buy_cost,
)

PASS = 0
FAIL = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")


# ──────────────────────────────────────────────────────────────────────────
# 1. 属性调整值公式 (R-CHK-024)
# ──────────────────────────────────────────────────────────────────────────
print("=== 1. 属性调整值公式 ===")
check("mod(3)=-4", ability_modifier(3) == -4)
check("mod(8)=-1", ability_modifier(8) == -1)
check("mod(10)=0", ability_modifier(10) == 0)
check("mod(11)=0", ability_modifier(11) == 0)
check("mod(12)=+1", ability_modifier(12) == 1)
check("mod(14)=+2", ability_modifier(14) == 2)
check("mod(20)=+5", ability_modifier(20) == 5)

# ──────────────────────────────────────────────────────────────────────────
# 2. 熟练加值表 (R-CHK-015)
# ──────────────────────────────────────────────────────────────────────────
print("=== 2. 熟练加值表 ===")
pb_table = {1: 2, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3, 8: 3,
            9: 4, 10: 4, 11: 4, 12: 4, 13: 5, 17: 6, 20: 6}
for lvl, expected in pb_table.items():
    check(f"PB({lvl})={expected}", proficiency_bonus(lvl) == expected)

# ──────────────────────────────────────────────────────────────────────────
# 3. 衍生数值公式
# ──────────────────────────────────────────────────────────────────────────
print("=== 3. 衍生数值公式 ===")
# HP = HD + CON mod
check("HP(D10,CON+2)=12", hit_points_level1(10, 2) == 12)
check("HP(D6,CON-1)=5", hit_points_level1(6, -1) == 5)
check("HP(D12,CON+3)=15", hit_points_level1(12, 3) == 15)
# 无甲AC = 10 + DEX mod
check("AC(DEX+3)=13", unarmored_ac(3) == 13)
check("AC(DEX-1)=9", unarmored_ac(-1) == 9)
# 先攻 = DEX mod
check("init(+2)=2", initiative(2) == 2)
# 被动察觉 = 10 + WIS mod (+ PB if proficient)
check("passive(WIS+3,prof,PB2)=15", passive_perception(3, True, 2) == 15)
check("passive(WIS+0,noprof,PB2)=10", passive_perception(0, False, 2) == 10)
check("passive(WIS+4,prof,PB3)=17", passive_perception(4, True, 3) == 17)
# 法术豁免DC = 8 + casting mod + PB
check("save_dc(+3,PB2)=13", spell_save_dc(3, 2) == 13)
check("save_dc(+5,PB3)=16", spell_save_dc(5, 3) == 16)
# 法术攻击加值 = casting mod + PB
check("spell_atk(+3,PB2)=5", spell_attack_bonus(3, 2) == 5)
check("spell_atk(+4,PB3)=7", spell_attack_bonus(4, 3) == 7)

# ──────────────────────────────────────────────────────────────────────────
# 4. 标准数列与购点法
# ──────────────────────────────────────────────────────────────────────────
print("=== 4. 标准数列与购点法 ===")
check("标准数列=[15,14,13,12,10,8]", STANDARD_ARRAY == [15, 14, 13, 12, 10, 8])
# 购点法花费表 (出处: 第三步：确定属性值.htm)
expected_cost = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
check("购点花费表一致", POINT_BUY_COST == expected_cost,
      f"got {POINT_BUY_COST}")
check("购点预算=27", POINT_BUY_BUDGET == 27)
# 全8 = 0点 → 合法
check("全8合法", validate_point_buy([8, 8, 8, 8, 8, 8]) is True)
# [15,15,15,8,8,8] = 27点 → 合法
check("[15*3,8*3]=27合法", validate_point_buy([15, 15, 15, 8, 8, 8]) is True)
# [15,15,15,15,8,8] = 36点 → 超预算非法
check("[15*4,8*2]=36超预算", validate_point_buy([15, 15, 15, 15, 8, 8]) is False)
# 16非法（超出购点范围）
check("16非法", validate_point_buy([16, 8, 8, 8, 8, 8]) is False)
# 花费计算
check("cost([15,14,13,12,10,8])=27", point_buy_cost([15, 14, 13, 12, 10, 8]) == 27)

# ──────────────────────────────────────────────────────────────────────────
# 5. 阵营九宫格
# ──────────────────────────────────────────────────────────────────────────
print("=== 5. 阵营九宫格 ===")
check("阵营共9种", len(ALIGNMENTS) == 9)
check("守序善良存在", "守序善良" in ALIGNMENTS)
check("混乱邪恶存在", "混乱邪恶" in ALIGNMENTS)
check("绝对中立存在", "绝对中立" in ALIGNMENTS)

# ──────────────────────────────────────────────────────────────────────────
# 6. 职业数据完整性 (12个职业)
# ──────────────────────────────────────────────────────────────────────────
print("=== 6. 职业数据完整性 ===")
check("共12个职业", len(CLASSES) == 12)
# 生命骰抽查 (出处: 各职业 .htm 核心特质表)
hit_die_expected = {
    "野蛮人": 12, "吟游诗人": 8, "牧师": 8, "德鲁伊": 8,
    "战士": 10, "武僧": 8, "圣武士": 10, "游侠": 10,
    "游荡者": 8, "术士": 6, "魔契师": 8, "法师": 6,
}
for name, hd in hit_die_expected.items():
    check(f"{name} HD={hd}", CLASSES[name]["hit_die"] == hd,
          f"got {CLASSES[name]['hit_die']}")
# 施法属性抽查 (出处: 各职业 .htm 施法属性)
casting_expected = {
    "野蛮人": None, "吟游诗人": "CHA", "牧师": "WIS", "德鲁伊": "WIS",
    "战士": None, "武僧": None, "圣武士": "CHA", "游侠": "WIS",
    "游荡者": None, "术士": "CHA", "魔契师": "CHA", "法师": "INT",
}
for name, sc in casting_expected.items():
    check(f"{name} spellcasting={sc}", CLASSES[name]["spellcasting"] == sc,
          f"got {CLASSES[name]['spellcasting']}")
# 每个职业有4个子职
for name, data in CLASSES.items():
    check(f"{name} 有4子职", len(data["subclasses"]) == 4,
          f"got {len(data['subclasses'])}")

# ──────────────────────────────────────────────────────────────────────────
# 7. 种族数据完整性 (10个种族)
# ──────────────────────────────────────────────────────────────────────────
print("=== 7. 种族数据完整性 ===")
check("共10个种族", len(RACES) == 10)
# 速度抽查 (出处: 各种族 .htm)
speed_expected = {
    "人类": 30, "矮人": 30, "精灵": 30, "半身人": 30, "侏儒": 30,
    "歌利亚": 35, "兽人": 30, "提夫林": 30, "龙裔": 30, "阿斯莫": 30,
}
for name, sp in speed_expected.items():
    check(f"{name} speed={sp}", RACES[name]["speed"] == sp,
          f"got {RACES[name]['speed']}")
# 黑暗视觉抽查 (出处: 各种族 .htm)
darkvision_expected = {
    "人类": 0, "矮人": 120, "精灵": 60, "半身人": 0, "侏儒": 60,
    "歌利亚": 0, "兽人": 120, "提夫林": 60, "龙裔": 60, "阿斯莫": 60,
}
for name, dv in darkvision_expected.items():
    check(f"{name} darkvision={dv}", RACES[name]["darkvision"] == dv,
          f"got {RACES[name]['darkvision']}")

# ──────────────────────────────────────────────────────────────────────────
# 8. 背景数据完整性 (16个背景)
# ──────────────────────────────────────────────────────────────────────────
print("=== 8. 背景数据完整性 ===")
check("共16个背景", len(BACKGROUNDS) == 16)
# 每个背景有3项属性、2项技能熟练、1个专长
for name, data in BACKGROUNDS.items():
    check(f"{name} 有3项属性", len(data["ability_scores"]) == 3)
    check(f"{name} 有2项技能熟练", len(data["skill_prof"]) == 2)
    check(f"{name} 有专长", bool(data["feat"]))
# 抽查关键背景 (出处: 各背景 .htm)
check("侍僧属性=[INT,WIS,CHA]",
      BACKGROUNDS["侍僧"]["ability_scores"] == ["INT", "WIS", "CHA"])
check("士兵技能=[运动,威吓]",
      BACKGROUNDS["士兵"]["skill_prof"] == ["运动", "威吓"])
check("农民专长=健壮", BACKGROUNDS["农民"]["feat"] == "健壮")
check("智者专长=魔法学徒（法师）",
      BACKGROUNDS["智者"]["feat"] == "魔法学徒（法师）")

# ──────────────────────────────────────────────────────────────────────────
# 9. 五步流程端到端测试
# ──────────────────────────────────────────────────────────────────────────
print("=== 9. 五步流程端到端测试 ===")

# 测试1: 1级战士 (人类/士兵)
sheet = create_character(
    class_name="战士", race="人类", background="士兵",
    scores_method="standard_array", alignment="守序善良", name="勇者",
)
d = sheet.to_dict()
check("战士: HD=10", d["hit_die"] == 10)
check("战士: STR=15", d["scores"]["STR"] == 15)
check("战士: DEX=14", d["scores"]["DEX"] == 14)
check("战士: CON=13", d["scores"]["CON"] == 13)
check("战士: CON mod=+1", d["mods"]["CON"] == 1)
check("战士: HP=11 (10+1)", d["max_hp"] == 11)
check("战士: DEX mod=+2", d["mods"]["DEX"] == 2)
check("战士: 无甲AC=12 (10+2)", d["ac_unarmored"] == 12)
check("战士: 先攻+2", d["initiative_bonus"] == 2)
check("战士: PB=+2", d["prof_bonus"] == 2)
check("战士: 无施法", d["spellcasting"] is None)
check("战士: spell_save_dc=None", d["spell_save_dc"] is None)

# 测试2: 1级法师 (精灵/智者) — 施法者
mage = create_character(
    class_name="法师", race="精灵", background="智者",
    scores_method="standard_array", alignment="绝对中立", name="大法师",
)
md = mage.to_dict()
check("法师: HD=6", md["hit_die"] == 6)
check("法师: INT=15", md["scores"]["INT"] == 15)
check("法师: INT mod=+2", md["mods"]["INT"] == 2)
check("法师: CON=13→+1", md["mods"]["CON"] == 1)
check("法师: HP=7 (6+1)", md["max_hp"] == 7)
check("法师: spellcasting=INT", md["spellcasting"] == "INT")
check("法师: 法术豁免DC=12 (8+2+2)", md["spell_save_dc"] == 12)
check("法师: 法术攻击加值=4 (2+2)", md["spell_attack_bonus"] == 4)

# 测试3: 1级野蛮人 (兽人/隐士) — 高HD
barb = create_character(
    class_name="野蛮人", race="兽人", background="隐士",
    scores_method="standard_array", alignment="混乱善良", name="狂战士",
)
bd = barb.to_dict()
check("野蛮人: HD=12", bd["hit_die"] == 12)
check("野蛮人: STR=15", bd["scores"]["STR"] == 15)
check("野蛮人: CON=14→+2", bd["mods"]["CON"] == 2)
check("野蛮人: HP=14 (12+2)", bd["max_hp"] == 14)
check("野蛮人: DEX=13→+1", bd["mods"]["DEX"] == 1)
check("野蛮人: 无甲AC=11 (10+1)", bd["ac_unarmored"] == 11)

# 测试4: 1级牧师 (矮人/侍僧) — WIS施法
cleric = create_character(
    class_name="牧师", race="矮人", background="侍僧",
    scores_method="standard_array", alignment="守序中立", name="祭司",
)
cd = cleric.to_dict()
check("牧师: HD=8", cd["hit_die"] == 8)
check("牧师: WIS=15→+2", cd["mods"]["WIS"] == 2)
check("牧师: CON=13→+1", cd["mods"]["CON"] == 1)
check("牧师: HP=9 (8+1)", cd["max_hp"] == 9)
check("牧师: spellcasting=WIS", cd["spellcasting"] == "WIS")
check("牧师: 法术豁免DC=12 (8+2+2)", cd["spell_save_dc"] == 12)

# 测试5: 被动察觉计算
# 牧师 WIS+2, 察觉熟练? 牧师技能池无察觉 → 不熟练 → 10+2=12
check("牧师被动察觉(不熟练)=12",
      cleric.passive_perc(perception_proficient=False) == 12)
# 若熟练 → 10+2+2=14
check("牧师被动察觉(熟练,PB2)=14",
      cleric.passive_perc(perception_proficient=True) == 14)

# 测试6: 购点法创建
# 用购点法分配: STR15 CON15 DEX8 INT8 WIS8 CHA8 → 花费 9+9=18 ≤27
buy_sheet = CharacterSheet()
step1_choose_class(buy_sheet, "战士")
step2_choose_origin(buy_sheet, "人类", "士兵")
step3_assign_ability_scores(
    buy_sheet, method="point_buy",
    scores=[15, 8, 15, 8, 8, 8],
    assignment={"STR": 15, "DEX": 8, "CON": 15, "INT": 8, "WIS": 8, "CHA": 8},
)
step4_choose_alignment(buy_sheet, "中立邪恶")
step5_enrich_details(buy_sheet, name="购点战士")
bd2 = buy_sheet.to_dict()
check("购点: STR=15", bd2["scores"]["STR"] == 15)
check("购点: CON=15→+2", bd2["mods"]["CON"] == 2)
check("购点: HP=12 (10+2)", bd2["max_hp"] == 12)

# 测试7: 分步流程 (逐步调用)
s = CharacterSheet()
step1_choose_class(s, "游荡者")
check("分步: 游荡者HD=8", s.hit_die == 8)
check("分步: 游荡者主属性=[DEX]", s.primary_abilities == ["DEX"])
step2_choose_origin(s, "半身人", "流浪者")
check("分步: 半身人速度=30", s.speed == 30)
check("分步: 半身人体型=小型", s.size == "小型")
step3_assign_ability_scores(s, method="standard_array")
check("分步: 游荡者DEX=15", s.scores["DEX"] == 15)
step4_choose_alignment(s, "混乱中立")
check("分步: 阵营=混乱中立", s.alignment == "混乱中立")
step5_enrich_details(s, name="潜行者")
check("分步: 名字=潜行者", s.name == "潜行者")

# ──────────────────────────────────────────────────────────────────────────
# 10. 边界与异常测试
# ──────────────────────────────────────────────────────────────────────────
print("=== 10. 边界与异常测试 ===")

# 未知职业
try:
    get_class("不存在")
    check("未知职业应抛错", False)
except KeyError:
    check("未知职业抛KeyError", True)

# 非法阵营
try:
    step4_choose_alignment(CharacterSheet(), "邪恶")
    check("非法阵营应抛错", False)
except ValueError:
    check("非法阵营抛ValueError", True)

# 购点法超预算
try:
    s2 = CharacterSheet()
    step1_choose_class(s2, "法师")
    step2_choose_origin(s2, "精灵", "智者")
    step3_assign_ability_scores(
        s2, method="point_buy",
        assignment={"STR": 15, "DEX": 15, "CON": 15, "INT": 8, "WIS": 8, "CHA": 8},
    )
    check("超预算购点应抛错", False)
except ValueError:
    check("超预算购点抛ValueError", True)

# 等级边界
check("PB(1)=2 (1级起始)", proficiency_bonus(1) == 2)
check("PB(20)=6 (满级)", proficiency_bonus(20) == 6)

# 属性边界
check("mod(1)=-5 (最低)", ability_modifier(1) == -5)
check("mod(20)=+5 (冒险者上限)", ability_modifier(20) == 5)

# ──────────────────────────────────────────────────────────────────────────
# 总结
# ──────────────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"Phase B 自检结果: {PASS} 通过, {FAIL} 失败")
print(f"{'='*50}")
sys.exit(0 if FAIL == 0 else 1)
