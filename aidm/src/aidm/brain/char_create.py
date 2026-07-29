"""角色创建逻辑 — 五步车卡法。

五步流程（出处: topics/玩家手册2024/创建角色/）：
  Step 1 选择职业     创建角色/第一步：选择职业.htm
  Step 2 确定起源     创建角色/第二步：确定起源.htm
  Step 3 确定属性值   创建角色/第三步：确定属性值.htm
  Step 4 选择阵营     创建角色/第四步：选择阵营.htm
  Step 5 丰富细节     创建角色/第五步：丰富细节.htm

衍生数值公式（出处: RULE_SPEC.md R-CHK-024 等）：
  属性调整值      = floor((score - 10) / 2)
  1级HP           = 职业生命骰面值 + 体质调整值
  无甲AC          = 10 + 敏捷调整值
  先攻            = d20 + 敏捷调整值
  熟练加值(PB)    = 1级+2，每4级提升（5级+3,9级+4,13级+5,17级+6）
  被动察觉        = 10 + 感知(察觉)检定加值
  法术豁免DC      = 8 + 施法属性调整值 + 熟练加值
  法术攻击加值    = 施法属性调整值 + 熟练加值
"""

from __future__ import annotations

import random
from typing import Any

from aidm.data.backgrounds import get_background
from aidm.data.classes import get_class
from aidm.data.races import dwarven_toughness, get_race

# ──────────────────────────────────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────────────────────────────────

ABILITY_ORDER = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
ABILITY_CN = {
    "STR": "力量", "DEX": "敏捷", "CON": "体质",
    "INT": "智力", "WIS": "感知", "CHA": "魅力",
}

# 标准数列  出处: 第三步：确定属性值.htm
STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]

# 购点法总点数  出处: 第三步：确定属性值.htm ("你有27点")
POINT_BUY_BUDGET = 27

# 购点法花费表  出处: 第三步：确定属性值.htm 属性值点数花费表
POINT_BUY_COST = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}

# 阵营九宫格  出处: 第四步：选择阵营.htm
ALIGNMENTS = [
    "守序善良", "中立善良", "混乱善良",
    "守序中立", "绝对中立", "混乱中立",
    "守序邪恶", "中立邪恶", "混乱邪恶",
]

# 标准语言  出处: 第二步：确定起源.htm / 进行游戏/六项属性.htm（语言与文字）
# 角色至少懂通用语 + 2 门自选标准语言。
STANDARD_LANGUAGES = [
    "通用语", "矮人语", "精灵语", "巨人语", "侏儒语",
    "哥布林语", "半身人语", "兽人语",
]


# ──────────────────────────────────────────────────────────────────────────
# 衍生数值计算
# ──────────────────────────────────────────────────────────────────────────

def ability_modifier(score: int) -> int:
    """属性调整值 = floor((score - 10) / 2)。

    规则: R-CHK-024  出处: 进行游戏/六项属性.htm
    """
    return (score - 10) // 2


def proficiency_bonus(level: int) -> int:
    """熟练加值(PB)：1级+2，每4级提升。

    规则: R-CHK-015  出处: 进行游戏/熟练加值.htm
    1-4:+2  5-8:+3  9-12:+4  13-16:+5  17-20:+6
    """
    if level < 1:
        raise ValueError(f"等级必须>=1，得到{level}")
    if level > 20:
        raise ValueError(f"等级必须<=20，得到{level}")
    return 2 + (level - 1) // 4


def hit_points_level1(hit_die: int, con_mod: int, race: str | None = None) -> int:
    """1级HP = 生命骰最大值 + 体质调整值 + 种族刚毅加成（矮人+1）。

    规则: R-DMG-007  出处: 进行游戏/生命值.htm
          矮人刚毅 Dwarven Toughness：生命值上限+1，此后每次升级时再加1。
          出处: 角色起源/种族/矮人.htm
    """
    hp = hit_die + con_mod
    if race is not None and dwarven_toughness(race):
        hp += 1  # 矮人刚毅：1级时生命值上限+1
    return hp


def unarmored_ac(
    dex_mod: int, con_mod: int = 0, class_name: str | None = None
) -> int:
    """无甲AC = 10 + 敏捷调整值；野蛮人无甲防御 = 10 + 敏捷 + 体质。

    规则: R-CMB-021  出处: 进行游戏/护甲等级.htm
          野蛮人无甲防御 Unarmored Defense：AC = 10 + 敏捷调整值 + 体质调整值。
          出处: 角色职业/野蛮人/野蛮人.htm
    """
    if class_name == "野蛮人":
        return 10 + dex_mod + con_mod
    return 10 + dex_mod


def initiative(dex_mod: int) -> int:
    """先攻 = d20 + 敏捷调整值。

    规则: R-CMB-002  出处: 进行游戏/先攻.htm
    """
    return dex_mod   # 加值部分；d20由掷骰提供


def passive_perception(wis_mod: int, proficient: bool, pb: int) -> int:
    """被动察觉 = 10 + 感知(察觉)检定加值。

    规则: R-CHK-019  出处: 进行游戏/被动察觉.htm
    检定加值 = 感知调整值 + (熟练加值 if 察觉熟练)
    """
    bonus = wis_mod + (pb if proficient else 0)
    return 10 + bonus


def spell_save_dc(casting_mod: int, pb: int) -> int:
    """法术豁免DC = 8 + 施法属性调整值 + 熟练加值。

    规则: R-CHK-012  出处: 进行游戏/法术豁免DC.htm
    """
    return 8 + casting_mod + pb


def spell_attack_bonus(casting_mod: int, pb: int) -> int:
    """法术攻击加值 = 施法属性调整值 + 熟练加值。

    规则: R-SPL-021  出处: 第七章：法术.htm
    """
    return casting_mod + pb


# ──────────────────────────────────────────────────────────────────────────
# 属性生成方法
# ──────────────────────────────────────────────────────────────────────────

def roll_4d6_drop_lowest() -> int:
    """掷4d6弃最低，返回总和。

    规则: 第三步：确定属性值.htm 随机生成
    """
    rolls = sorted(random.randint(1, 6) for _ in range(4))
    return sum(rolls[1:])   # 弃最低


def roll_ability_scores() -> list[int]:
    """随机生成六项属性值（4d6弃最低 × 6）。"""
    return [roll_4d6_drop_lowest() for _ in range(6)]


def validate_point_buy(scores: list[int]) -> bool:
    """校验购点法属性值是否合法。

    合法条件：6项，每项在8-15之间，总花费<=27。
    """
    if len(scores) != 6:
        return False
    total = 0
    for s in scores:
        if s not in POINT_BUY_COST:
            return False
        total += POINT_BUY_COST[s]
    return total <= POINT_BUY_BUDGET


def point_buy_cost(scores: list[int]) -> int:
    """计算购点法总花费。"""
    return sum(POINT_BUY_COST.get(s, 0) for s in scores)


# ──────────────────────────────────────────────────────────────────────────
# 五步车卡流程
# ──────────────────────────────────────────────────────────────────────────

class CharacterSheet:
    """角色卡：保存五步流程产生的全部数据。"""

    def __init__(self) -> None:
        self.name: str = ""
        # Step 1 职业
        self.class_name: str = ""
        self.level: int = 1
        self.hit_die: int = 0
        self.primary_abilities: list[str] = []
        self.save_prof: list[str] = []
        self.armor_training: str = ""
        self.weapon_prof: str = ""
        self.spellcasting: str | None = None
        # Step 2 起源
        self.race: str = ""
        self.background: str = ""
        self.speed: int = 30
        self.size: str = ""
        self.feats: list[str] = []          # 起源专长（背景给予）→ 对应 Character.feats_json
        self.languages: list[str] = ["通用语"]  # 至少通用语+2门标准语言
        # Step 3 属性
        self.scores: dict[str, int] = {}      # STR..CHA -> 分数
        # Step 4 阵营
        self.alignment: str = ""
        # Step 5 细节
        self.appearance: str = ""
        self.personality: str = ""

    # ── 衍生数值 ──────────────────────────────────────
    def mods(self) -> dict[str, int]:
        """六项属性的调整值。"""
        return {a: ability_modifier(self.scores[a]) for a in ABILITY_ORDER}

    def prof_bonus(self) -> int:
        """当前等级的熟练加值。"""
        return proficiency_bonus(self.level)

    def max_hp(self) -> int:
        """1级最大HP = 生命骰面值 + 体质调整值（矮人另+1刚毅）。"""
        return hit_points_level1(self.hit_die, self.mods()["CON"], self.race)

    def ac_unarmored(self) -> int:
        """无甲AC（野蛮人无甲防御 = 10 + 敏捷 + 体质）。"""
        return unarmored_ac(
            self.mods()["DEX"], self.mods()["CON"], self.class_name
        )

    def init_bonus(self) -> int:
        """先攻加值。"""
        return initiative(self.mods()["DEX"])

    def passive_perc(self, perception_proficient: bool = False) -> int:
        """被动察觉。"""
        return passive_perception(
            self.mods()["WIS"], perception_proficient, self.prof_bonus()
        )

    def spell_save_dc_value(self) -> int | None:
        """法术豁免DC（非施法者返回None）。"""
        if not self.spellcasting:
            return None
        casting_mod = self.mods()[self.spellcasting]
        return spell_save_dc(casting_mod, self.prof_bonus())

    def spell_atk_bonus(self) -> int | None:
        """法术攻击加值（非施法者返回None）。"""
        if not self.spellcasting:
            return None
        casting_mod = self.mods()[self.spellcasting]
        return spell_attack_bonus(casting_mod, self.prof_bonus())

    def to_dict(self) -> dict[str, Any]:
        """导出为字典（便于序列化/展示）。"""
        return {
            "name": self.name,
            "class": self.class_name,
            "level": self.level,
            "race": self.race,
            "background": self.background,
            "alignment": self.alignment,
            "hit_die": self.hit_die,
            "primary_abilities": self.primary_abilities,
            "save_prof": self.save_prof,
            "armor_training": self.armor_training,
            "weapon_prof": self.weapon_prof,
            "spellcasting": self.spellcasting,
            "speed": self.speed,
            "size": self.size,
            "feats": list(self.feats),
            "languages": list(self.languages),
            "scores": dict(self.scores),
            "mods": self.mods(),
            "prof_bonus": self.prof_bonus(),
            "max_hp": self.max_hp(),
            "ac_unarmored": self.ac_unarmored(),
            "initiative_bonus": self.init_bonus(),
            "passive_perception": self.passive_perc(),
            "spell_save_dc": self.spell_save_dc_value(),
            "spell_attack_bonus": self.spell_atk_bonus(),
        }


def step1_choose_class(sheet: CharacterSheet, class_name: str) -> CharacterSheet:
    """Step 1：选择职业。

    返回职业的核心特质：生命骰、主属性、豁免熟练、护甲受训、武器熟练、施法属性。
    出处: 创建角色/第一步：选择职业.htm ; 角色职业/<职业>.htm
    """
    data = get_class(class_name)
    sheet.class_name = class_name
    sheet.hit_die = data["hit_die"]
    sheet.primary_abilities = list(data["primary"])
    sheet.save_prof = list(data["save_prof"])
    sheet.armor_training = data["armor_training"]
    sheet.weapon_prof = data["weapon_prof"]
    sheet.spellcasting = data["spellcasting"]
    return sheet


def step2_choose_origin(
    sheet: CharacterSheet,
    race: str,
    background: str,
    size: str | None = None,
) -> CharacterSheet:
    """Step 2：确定起源（种族 + 背景）。

    种族决定速度、体型、黑暗视觉、特殊特质。
    背景决定三项属性、起源专长、技能熟练、工具熟练、装备。
    出处: 创建角色/第二步：确定起源.htm ; 角色起源/种族|背景/*.htm
    """
    rdata = get_race(race)
    bdata = get_background(background)
    sheet.race = race
    sheet.background = background
    sheet.speed = rdata["speed"]
    # 体型：若种族有多种体型，调用方需指定；否则取唯一项
    sizes = rdata["size"]
    if size is not None:
        sheet.size = size
    else:
        sheet.size = sizes[0]
    # 记录背景提供的属性（供Step3分配参考）
    sheet._bg_abilities = bdata["ability_scores"]  # type: ignore[attr-defined]
    sheet._bg_feat = bdata["feat"]                 # type: ignore[attr-defined]
    # 起源专长：背景给予的专长直接写入角色卡（对应 Character.feats_json）
    # 出处: 创建角色/第二步：确定起源.htm
    sheet.feats = [sheet._bg_feat] if sheet._bg_feat else []
    return sheet


def step3_assign_ability_scores(
    sheet: CharacterSheet,
    method: str = "standard_array",
    scores: list[int] | None = None,
    assignment: dict[str, int] | None = None,
    bg_bonus: dict[str, int] | None = None,
) -> CharacterSheet:
    """Step 3：确定属性值。

    method:
      - "standard_array": 使用标准数列 [15,14,13,12,10,8]
      - "point_buy":      购点法（27点），需提供 scores
      - "roll":           随机生成（4d6弃最低 × 6）
    scores: 仅 point_buy 时使用，6项属性值（8-15）。
    assignment: 可选，将6个数值显式分配到 STR/DEX/CON/INT/WIS/CHA。
                若不提供，则按标准数列建议表分配。
    bg_bonus: 可选，背景属性加成显式分配，如 {"STR": 2, "DEX": 1}。
              默认 None → 取背景三项属性的第一项+2、第二项+1（即 2/1 分配）；
              若需三项各+1，传入 {"A":1,"B":1,"C":1}。每项加成后不超过20。

    出处: 创建角色/第三步：确定属性值.htm（背景属性加成：+2/+1 或 +1/+1/+1）
    """
    if method == "standard_array":
        values = list(STANDARD_ARRAY)
    elif method == "point_buy":
        if scores is None:
            raise ValueError("购点法需要提供 scores")
        if not validate_point_buy(scores):
            raise ValueError(
                f"购点法属性非法或超预算(27点): {scores}, "
                f"花费={point_buy_cost(scores)}"
            )
        values = list(scores)
    elif method == "roll":
        values = roll_ability_scores()
    else:
        raise ValueError(f"未知属性生成方法: {method}")

    if assignment is not None:
        # 校验：分配的数值集合应等于生成的数值集合
        if sorted(assignment.values()) != sorted(values):
            raise ValueError(
                f"分配与生成不匹配: 分配={sorted(assignment.values())}, "
                f"生成={sorted(values)}"
            )
        sheet.scores = dict(assignment)
    else:
        # 默认按标准数列建议表分配（按职业）
        sheet.scores = _default_assignment(sheet.class_name, values)

    # 应用背景属性加成（背景给予三项属性，一项+2另一项+1，或三项各+1；不超过20）
    # 出处: 创建角色/第三步：确定属性值.htm
    _apply_background_ability_bonus(sheet, bg_bonus)

    return sheet


def _apply_background_ability_bonus(
    sheet: CharacterSheet, bg_bonus: dict[str, int] | None
) -> None:
    """将背景的属性加成叠加到已分配的属性值上，每项不超过20。

    出处: 创建角色/第三步：确定属性值.htm（背景属性加成）
          sheet._bg_abilities 由 step2 记录（背景给予的三项属性）。
    """
    bg_abilities: list[str] = getattr(sheet, "_bg_abilities", None) or []
    if not bg_abilities:
        return

    if bg_bonus is None:
        # 默认 2/1 分配：第一项+2，第二项+1
        bg_bonus = {bg_abilities[0]: 2, bg_abilities[1]: 1}

    for ability, delta in bg_bonus.items():
        if ability not in sheet.scores or delta == 0:
            continue
        sheet.scores[ability] = min(sheet.scores[ability] + delta, 20)


# 按职业给出的标准数列建议（出处: 第三步：确定属性值.htm 按职业给出的标准数列表）
# 键=职业名，值=[STR, DEX, CON, INT, WIS, CHA] 的推荐数值排序
# 实际上该表给出的是把标准数列分配给各属性的建议。这里我们提供一个简单的
# 默认分配：把最大的数值给主属性，其余按顺序填入。
_DEFAULT_ARRAY_BY_CLASS: dict[str, dict[str, int]] = {
    # 数值来自规则书"按职业给出的标准数列"表
    "野蛮人":   {"STR": 15, "DEX": 13, "CON": 14, "INT": 10, "WIS": 12, "CHA": 8},
    "吟游诗人": {"STR": 8,  "DEX": 14, "CON": 12, "INT": 13, "WIS": 10, "CHA": 15},
    "牧师":     {"STR": 14, "DEX": 8,  "CON": 13, "INT": 10, "WIS": 15, "CHA": 12},
    "德鲁伊":   {"STR": 8,  "DEX": 12, "CON": 14, "INT": 13, "WIS": 15, "CHA": 10},
    "战士":     {"STR": 15, "DEX": 14, "CON": 13, "INT": 8,  "WIS": 10, "CHA": 12},
    "武僧":     {"STR": 12, "DEX": 15, "CON": 13, "INT": 8,  "WIS": 14, "CHA": 10},
    "圣武士":   {"STR": 15, "DEX": 10, "CON": 13, "INT": 8,  "WIS": 12, "CHA": 14},
    "游侠":     {"STR": 12, "DEX": 15, "CON": 13, "INT": 8,  "WIS": 14, "CHA": 10},
    "游荡者":   {"STR": 12, "DEX": 15, "CON": 13, "INT": 14, "WIS": 10, "CHA": 8},
    "术士":     {"STR": 10, "DEX": 13, "CON": 14, "INT": 8,  "WIS": 12, "CHA": 15},
    "魔契师":   {"STR": 8,  "DEX": 14, "CON": 13, "INT": 12, "WIS": 10, "CHA": 15},
    "法师":     {"STR": 8,  "DEX": 12, "CON": 13, "INT": 15, "WIS": 14, "CHA": 10},
}


def _default_assignment(class_name: str, values: list[int]) -> dict[str, int]:
    """默认分配：优先用规则书建议表；若数值集合不匹配则按降序填入。"""
    if class_name in _DEFAULT_ARRAY_BY_CLASS:
        suggested = _DEFAULT_ARRAY_BY_CLASS[class_name]
        if sorted(suggested.values()) == sorted(values):
            return dict(suggested)
    # 回退：按数值降序分配到 STR,DEX,CON,INT,WIS,CHA
    ordered = sorted(values, reverse=True)
    return dict(zip(ABILITY_ORDER, ordered))


def step4_choose_alignment(sheet: CharacterSheet, alignment: str) -> CharacterSheet:
    """Step 4：选择阵营。

    九宫格阵营。出处: 创建角色/第四步：选择阵营.htm
    """
    if alignment not in ALIGNMENTS:
        raise ValueError(f"未知阵营 {alignment!r}，可选: {ALIGNMENTS}")
    sheet.alignment = alignment
    return sheet


def step5_enrich_details(
    sheet: CharacterSheet,
    name: str = "",
    appearance: str = "",
    personality: str = "",
) -> CharacterSheet:
    """Step 5：丰富细节 + 计算衍生数值。

    衍生数值：HP、AC、先攻、熟练加值、被动察觉、法术豁免DC、法术攻击加值。
    出处: 创建角色/第五步：丰富细节.htm
    """
    sheet.name = name
    sheet.appearance = appearance
    sheet.personality = personality
    return sheet


def create_character(
    class_name: str,
    race: str,
    background: str,
    scores_method: str = "standard_array",
    alignment: str = "绝对中立",
    name: str = "",
    size: str | None = None,
    assignment: dict[str, int] | None = None,
    bg_bonus: dict[str, int] | None = None,
    languages: list[str] | None = None,
) -> CharacterSheet:
    """便捷函数：一次性完成五步车卡。

    bg_bonus: 背景属性加成显式分配（如 {"STR":2,"DEX":1}）；None→默认2/1。
    languages: 角色已知语言列表；None→通用语+2门标准语言。
              出处: 创建角色/第二步：确定起源.htm（至少通用语+2门标准语言）
    """
    sheet = CharacterSheet()
    step1_choose_class(sheet, class_name)
    step2_choose_origin(sheet, race, background, size=size)
    step3_assign_ability_scores(
        sheet, method=scores_method, assignment=assignment, bg_bonus=bg_bonus
    )
    # 语言：至少通用语 + 2 门自选标准语言
    # 出处: 创建角色/第二步：确定起源.htm
    if languages:
        sheet.languages = list(languages)
    else:
        sheet.languages = ["通用语", "矮人语", "精灵语"]
    step4_choose_alignment(sheet, alignment)
    step5_enrich_details(sheet, name=name)
    return sheet


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 属性调整值  R-CHK-024
    assert ability_modifier(8) == -1
    assert ability_modifier(10) == 0
    assert ability_modifier(11) == 0
    assert ability_modifier(14) == 2
    assert ability_modifier(20) == 5
    # 熟练加值  R-CHK-015
    assert proficiency_bonus(1) == 2
    assert proficiency_bonus(4) == 2
    assert proficiency_bonus(5) == 3
    assert proficiency_bonus(9) == 4
    assert proficiency_bonus(13) == 5
    assert proficiency_bonus(17) == 6
    assert proficiency_bonus(20) == 6
    # HP / AC / 先攻
    assert hit_points_level1(10, 2) == 12       # 战士 D10 + CON+2
    assert hit_points_level1(12, 2, "矮人") == 15  # 矮人刚毅：12+2+1
    assert hit_points_level1(10, 2, "人类") == 12  # 人类无刚毅
    assert unarmored_ac(3) == 13                # 10 + DEX+3
    assert unarmored_ac(3, 2, "野蛮人") == 15   # 野蛮人无甲防御：10+DEX+CON
    assert unarmored_ac(3, 2, "战士") == 13     # 非野蛮人：10+DEX
    assert initiative(2) == 2
    # 被动察觉
    assert passive_perception(3, True, 2) == 15  # 10 + 3 + 2
    assert passive_perception(0, False, 2) == 10
    # 法术豁免DC / 法术攻击加值
    assert spell_save_dc(3, 2) == 13            # 8 + 3 + 2
    assert spell_attack_bonus(3, 2) == 5         # 3 + 2
    # 购点法校验 (花费表: 8→0 9→1 10→2 11→3 12→4 13→5 14→7 15→9)
    assert point_buy_cost([15, 15, 15, 8, 8, 8]) == 27          # 9*3=27 正好
    assert validate_point_buy([15, 15, 15, 8, 8, 8]) is True    # 27点正好
    assert validate_point_buy([8, 8, 8, 8, 8, 8]) is True       # 0点
    assert validate_point_buy([16, 8, 8, 8, 8, 8]) is False     # 16非法
    assert validate_point_buy([15, 15, 15, 15, 8, 8]) is False  # 36>27 超预算
    # 端到端：创建一个1级战士
    sheet = create_character(
        class_name="战士",
        race="人类",
        background="士兵",
        scores_method="standard_array",
        alignment="守序善良",
        name="测试勇者",
    )
    d = sheet.to_dict()
    assert d["class"] == "战士"
    assert d["hit_die"] == 10
    assert d["race"] == "人类"
    assert d["background"] == "士兵"
    assert d["alignment"] == "守序善良"
    assert d["prof_bonus"] == 2
    # 标准数列建议（战士）：STR15 DEX14 CON13 INT8 WIS10 CHA12
    # 士兵背景三项属性 [STR,DEX,CON]，默认 2/1：STR+2、DEX+1 → STR17 DEX15 CON13
    assert d["scores"]["STR"] == 17
    assert d["scores"]["DEX"] == 15
    assert d["scores"]["CON"] == 13
    # CON mod = +1 → HP = 10 + 1 = 11（人类无刚毅）
    assert d["mods"]["CON"] == 1
    assert d["max_hp"] == 11
    # DEX mod = +2（15→+2）→ 无甲AC = 12, 先攻+2
    assert d["mods"]["DEX"] == 2
    assert d["ac_unarmored"] == 12
    assert d["initiative_bonus"] == 2
    # 战士无施法属性
    assert d["spellcasting"] is None
    assert d["spell_save_dc"] is None
    # 起源专长（背景给予）+ 语言
    assert d["feats"] == ["凶蛮打手"]
    assert d["languages"] == ["通用语", "矮人语", "精灵语"]
    # 端到端：创建一个1级法师（施法者）
    mage = create_character(
        class_name="法师",
        race="精灵",
        background="智者",
        scores_method="standard_array",
        alignment="绝对中立",
        name="大法师",
    )
    md = mage.to_dict()
    assert md["class"] == "法师"
    assert md["hit_die"] == 6
    assert md["spellcasting"] == "INT"
    # 法师标准数列建议：INT15 WIS14 CON13 ...
    # 智者背景三项属性 [CON,INT,WIS]，默认 2/1：CON+2、INT+1 → CON15 INT16 WIS14
    assert md["scores"]["INT"] == 16
    assert md["mods"]["INT"] == 3   # 16→+3
    # 法术豁免DC = 8 + 3 + 2 = 13
    assert md["spell_save_dc"] == 13
    # 法术攻击加值 = 3 + 2 = 5
    assert md["spell_attack_bonus"] == 5
    # HP = 6 + CON mod; CON=15→+2 → HP=8
    assert md["max_hp"] == 8
    # 起源专长（背景给予）
    assert md["feats"] == ["魔法学徒（法师）"]
    # 端到端：矮人野蛮人（矮人刚毅 +1HP；野蛮人无甲防御）
    dwarf_barb = create_character(
        class_name="野蛮人", race="矮人", background="农民",
        scores_method="standard_array", name="矮蛮子",
    )
    db = dwarf_barb.to_dict()
    # 野蛮人标准数列建议：STR15 DEX13 CON14 INT10 WIS12 CHA8
    # 农民背景三项属性 [STR,CON,WIS]，默认 2/1：STR+2、CON+1 → STR17 CON15 WIS12
    assert db["scores"]["CON"] == 15
    # 矮人刚毅：1级HP = 12(生命骰) + CON(+2) + 1(刚毅) = 15
    assert db["max_hp"] == 15
    # 野蛮人无甲防御 = 10 + DEX(13→+1) + CON(15→+2) = 13
    assert db["ac_unarmored"] == 13
    assert db["feats"] == ["健壮"]
    print("[char_create] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
