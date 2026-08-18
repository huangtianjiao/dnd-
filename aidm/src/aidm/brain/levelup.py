"""角色升级与成长 — Phase I。

实现 D&D 5E 升级五步骤（指南 Ch11）以及 DMG 变体规则。
所有规则点标注 `# 规则: R-DM-XXX + 出处: topics/.../xxx.htm`。

数据来源:
  - topics/玩家手册2024/创建角色/等级提升.htm  (XP表、固定HP、五步骤、游戏阶段)
  - topics/城主指南2024/2.运作游戏/角色升级.htm (奖励XP、里程碑、训练变体、基于游戏回)

规则映射 (RULE_SPEC.md):
  R-DM-041 奖励XP分配   → award_xp()
  R-DM-042 里程碑XP等级  → milestone_xp()
  R-DM-043 长休外升级HP  → level_up_outside_rest() / level_up()
  R-DM-044 通过训练获得等级(变体) → training_cost()
  R-DM-045 基于游戏回的升级速率   → session_based_level()
"""

from __future__ import annotations

import random

from aidm.data import feats as feat_db
from aidm.data.classes import CLASSES, get_class, get_extra_attacks

# ──────────────────────────────────────────────────────────────────────────
# 经验值与等级表
# 出处: topics/玩家手册2024/创建角色/等级提升.htm "角色升级表"
# 规则: R-DM-041 (XP分配) ; R-DM-045 (基于游戏回升级速率)
# ──────────────────────────────────────────────────────────────────────────

# 等级 -> 达到该等级所需的总XP
XP_TABLE: dict[int, int] = {
    1: 0,
    2: 300,
    3: 900,
    4: 2700,
    5: 6500,
    6: 14000,
    7: 23000,
    8: 34000,
    9: 48000,
    10: 64000,
    11: 85000,
    12: 100000,
    13: 120000,
    14: 140000,
    15: 165000,
    16: 195000,
    17: 225000,
    18: 265000,
    19: 305000,
    20: 355000,
}

MAX_LEVEL = 20


# ──────────────────────────────────────────────────────────────────────────
# 固定HP增长表（指南Ch11 Step 2 "职业固定生命值表"）
# 出处: topics/玩家手册2024/创建角色/等级提升.htm
# ──────────────────────────────────────────────────────────────────────────

# 职业名 -> 每级固定HP增长（不含体质调整值）
FIXED_HP_GAIN: dict[str, int] = {
    "野蛮人": 7,
    "战士": 6,
    "圣武士": 6,
    "游侠": 6,
    "吟游诗人": 5,
    "牧师": 5,
    "德鲁伊": 5,
    "武僧": 5,
    "游荡者": 5,
    "魔契师": 5,
    "术士": 4,
    "法师": 4,
}


# ──────────────────────────────────────────────────────────────────────────
# 熟练加值
# 出处: topics/玩家手册2024/创建角色/等级提升.htm "角色升级表"
# 规则: R-CHK-015 (熟练加值)
# ──────────────────────────────────────────────────────────────────────────

def proficiency_bonus(level: int) -> int:
    """熟练加值(PB)：1-4级+2，5-8级+3，9-12级+4，13-16级+5，17-20级+6。

    规则: R-CHK-015
    出处: topics/玩家手册2024/创建角色/等级提升.htm
    """
    if level < 1 or level > MAX_LEVEL:
        raise ValueError(f"等级必须在1-{MAX_LEVEL}之间，得到{level}")
    return 2 + (level - 1) // 4


# ──────────────────────────────────────────────────────────────────────────
# 游戏四阶段 Tiers of Play
# 出处: topics/玩家手册2024/创建角色/等级提升.htm "游戏阶段"
# ──────────────────────────────────────────────────────────────────────────

def get_tier(level: int) -> str:
    """返回角色所处的游戏阶段。

    T1(1-4)新手冒险者 / T2(5-10)成熟冒险者 /
    T3(11-16)力量超凡 / T4(17-20)英雄典范

    出处: topics/玩家手册2024/创建角色/等级提升.htm "游戏阶段"
    """
    if level < 1 or level > MAX_LEVEL:
        raise ValueError(f"等级必须在1-{MAX_LEVEL}之间，得到{level}")
    if level <= 4:
        return "T1"
    if level <= 10:
        return "T2"
    if level <= 16:
        return "T3"
    return "T4"


# ──────────────────────────────────────────────────────────────────────────
# XP 相关
# ──────────────────────────────────────────────────────────────────────────

def xp_for_level(level: int) -> int:
    """达到指定等级所需的总XP。

    出处: topics/玩家手册2024/创建角色/等级提升.htm "角色升级表"
    """
    if level < 1 or level > MAX_LEVEL:
        raise ValueError(f"等级必须在1-{MAX_LEVEL}之间，得到{level}")
    return XP_TABLE[level]


def level_from_xp(xp: int) -> int:
    """根据当前总XP返回对应等级。

    当总XP >= 某等级所需XP时即达到该等级。
    超过20级上限XP仍返回20。

    出处: topics/玩家手册2024/创建角色/等级提升.htm "角色升级表"
    """
    if xp < 0:
        raise ValueError(f"XP不能为负，得到{xp}")
    for level in range(MAX_LEVEL, 0, -1):
        if xp >= XP_TABLE[level]:
            return level
    return 1


def check_level_up(character: dict) -> bool:
    """检查角色XP是否达到下一级所需。

    规则: R-DM-041 (XP达到阈值即可升级)
    出处: topics/玩家手册2024/创建角色/等级提升.htm

    character 需包含: level, xp
    返回 True 表示可以升级（已达到下一级XP阈值或已达满级后继续获得XP）。
    """
    level = character.get("level", 1)
    xp = character.get("xp", 0)
    if level >= MAX_LEVEL:
        return False
    next_level = level + 1
    return xp >= XP_TABLE[next_level]


# ──────────────────────────────────────────────────────────────────────────
# R-DM-041 奖励XP分配
# ──────────────────────────────────────────────────────────────────────────

def award_xp(party: list[dict], total_xp: int) -> dict:
    """将总XP均分给队伍成员，原地更新每个成员的xp字段。

    规则: R-DM-041 奖励XP分配
    出处: topics/城主指南2024/2.运作游戏/角色升级.htm

    party: 角色字典列表，每个需有 'xp' 字段（int）。
    total_xp: 本次遭遇/里程碑的总XP。
    返回: {"per_member": int, "members": [...]} 其中 members 为更新后的副本。
    若 party 为空，per_member=0。
    余数向下取整（R-GLS-005 向下取整）。
    """
    if not party:
        return {"per_member": 0, "members": []}
    if total_xp < 0:
        raise ValueError(f"total_xp 不能为负，得到{total_xp}")
    per_member = total_xp // len(party)  # 向下取整
    updated = []
    for member in party:
        new_member = dict(member)
        new_member["xp"] = member.get("xp", 0) + per_member
        updated.append(new_member)
    return {"per_member": per_member, "members": updated}


# ──────────────────────────────────────────────────────────────────────────
# R-DM-042 里程碑XP等级
# ──────────────────────────────────────────────────────────────────────────

# 里程碑难度对应的XP量级（出处: 城主指南 角色升级.htm "将主要里程碑视为高难度遭遇，
# 次要里程碑视为低难度遭遇"）。这里提供按角色等级查XP的简化接口。
# 高难度遭遇XP参考表（按角色等级），出处: 城主指南 遭遇难度表
_HIGH_DIFFICULTY_XP: dict[int, int] = {
    1: 200, 2: 400, 3: 600, 4: 800, 5: 1100,
    6: 1400, 7: 1800, 8: 2300, 9: 2900, 10: 3700,
    11: 4700, 12: 6100, 13: 7800, 14: 10000, 15: 12700,
    16: 16300, 17: 21000, 18: 27000, 19: 35000, 20: 45000,
}
_LOW_DIFFICULTY_XP: dict[int, int] = {
    1: 50, 2: 100, 3: 150, 4: 250, 5: 500,
    6: 600, 7: 750, 8: 1000, 9: 1300, 10: 1600,
    11: 1900, 12: 2200, 13: 2600, 14: 3150, 15: 3800,
    16: 4700, 17: 6200, 18: 7800, 19: 9800, 20: 12700,
}


def milestone_xp(milestone_type: str, level: int = 1) -> int:
    """根据里程碑类型返回奖励XP。

    规则: R-DM-042 里程碑XP等级
    出处: topics/城主指南2024/2.运作游戏/角色升级.htm

    milestone_type: "major"(主要里程碑→高难度遭遇XP) 或 "minor"(次要里程碑→低难度遭遇XP)
    level: 角色等级，用于查对应难度的XP表。
    """
    if level < 1 or level > MAX_LEVEL:
        raise ValueError(f"等级必须在1-{MAX_LEVEL}之间，得到{level}")
    if milestone_type == "major":
        return _HIGH_DIFFICULTY_XP[level]
    if milestone_type == "minor":
        return _LOW_DIFFICULTY_XP[level]
    raise ValueError(f"未知里程碑类型 {milestone_type!r}，可选: 'major', 'minor'")


# ──────────────────────────────────────────────────────────────────────────
# R-DM-044 通过训练获得等级（变体）
# ──────────────────────────────────────────────────────────────────────────

# 训练时间/花费表（出处: 城主指南 角色升级.htm "通过训练获得等级表"）
_TRAINING_TABLE: dict[tuple[int, int], tuple[int, int]] = {
    (2, 4): (10, 20),
    (5, 10): (20, 40),
    (11, 16): (30, 60),
    (17, 20): (40, 80),
}


def training_cost(target_level: int) -> tuple[int, int]:
    """返回达到目标等级所需的训练天数和花费(GP)。

    规则: R-DM-044 通过训练获得等级（变体）
    出处: topics/城主指南2024/2.运作游戏/角色升级.htm "通过训练获得等级表"

    target_level: 要达到的等级（2-20）。
    返回: (days, gp)
    """
    if target_level < 2 or target_level > MAX_LEVEL:
        raise ValueError(f"目标等级必须在2-{MAX_LEVEL}之间，得到{target_level}")
    for (lo, hi), (days, gp) in _TRAINING_TABLE.items():
        if lo <= target_level <= hi:
            return (days, gp)
    raise ValueError(f"无法找到目标等级 {target_level} 的训练表条目")


# ──────────────────────────────────────────────────────────────────────────
# R-DM-045 基于游戏回的升级速率
# ──────────────────────────────────────────────────────────────────────────

# 基于游戏回的升级速率（出处: 城主指南 角色升级.htm "基于游戏回的升级"）
# 第1回→2级, 第2回→3级, 第3回→4级; 之后每级2-3回; 10级以上每级1-2回。
# 这里用累计游戏回数 -> 目标等级 的映射。
_SESSION_TO_LEVEL: list[int] = [
    # sessions_played(0-indexed) -> level after that many sessions
    1,   # 0 回 → 1级
    2,   # 1 回 → 2级
    3,   # 2 回 → 3级
    4,   # 3 回 → 4级
    5,   # ~5 回 → 5级 (4级后每级2-3回，取中值~2.5)
    6,   # ~7-8 回 → 6级
    7,   # ~10 回 → 7级
    8,   # ~12-13 回 → 8级
    9,   # ~15 回 → 9级
    10,  # ~17-18 回 → 10级
    11,  # 10级以上每级1-2回
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
]


def session_based_level(sessions_played: int) -> int:
    """根据已进行的游戏回数返回推荐等级。

    规则: R-DM-045 基于游戏回的升级速率
    出处: topics/城主指南2024/2.运作游戏/角色升级.htm "基于游戏回的升级"

    速率: 第1回→2级, 第2回→3级, 第3回→4级;
          之后每升一级需2-3回; 10级以上每级1-2回。
    前提: 每回约4小时，含不同难度遭遇并以达成重要里程碑结尾。
    """
    if sessions_played < 0:
        raise ValueError(f"游戏回数不能为负，得到{sessions_played}")
    if sessions_played >= len(_SESSION_TO_LEVEL):
        return MAX_LEVEL
    return _SESSION_TO_LEVEL[sessions_played]


# ──────────────────────────────────────────────────────────────────────────
# 升级五步骤核心
# ──────────────────────────────────────────────────────────────────────────

def _roll_hit_die(hit_die: int) -> int:
    """掷一颗生命骰，返回 [1, hit_die]。"""
    return random.randint(1, hit_die)


def _hp_gain_for_level(
    class_name: str,
    level: int,
    con_mod: int,
    use_fixed: bool = True,
    roll: int | None = None,
) -> int:
    """计算升到 level 级时获得的HP增量。

    出处: topics/玩家手册2024/创建角色/等级提升.htm Step 2 "职业固定生命值表"

    use_fixed=True 时使用固定HP增长表（FIXED_HP_GAIN）；
    use_fixed=False 时掷生命骰（或使用传入的 roll 值）。
    最终 HP增量 = (固定值 或 掷骰结果) + 体质调整值，至少为1。
    """
    fixed = FIXED_HP_GAIN.get(class_name)
    if fixed is None:
        # 未知职业，回退到生命骰面值的一半向上取整作为固定值
        cls = get_class(class_name)
        hd = cls["hit_die"]
        fixed = hd // 2 + 1  # e.g. d12→7, d10→6, d8→5, d6→4（与 FIXED_HP_GAIN 一致）

    if use_fixed:
        base = fixed
    else:
        cls = get_class(class_name)
        hd = cls["hit_die"]
        base = roll if roll is not None else _roll_hit_die(hd)

    gain = base + con_mod
    return max(gain, 1)  # 至少为1


# ──────────────────────────────────────────────────────────────────────────
# 专长选择 Feat Selection — PHB 2024 第五章「专长」
# ──────────────────────────────────────────────────────────────────────────

# ★ P5（方案 §8.2）: 生产路径不再以全局 FEAT_LEVELS 作为唯一 feat 机会判断；
#   ASI/专长 entitlement 由 rules.feat_entitlement（标准节点 + 职业额外节点
#   Fighter 6/14、Rogue 10）计算。此常量仅保留供旧测试/兼容展示引用。
FEAT_LEVELS: frozenset[int] = frozenset({4, 8, 12, 16, 19})


def _entitlement_for(character: dict) -> set[int]:
    """按角色 class_levels 计算已获得的 ASI/专长 entitlement 节点。

    方案 §8.2: 标准节点按总等级、职业额外节点（战士 6/14 等）按职业等级。
    class_levels 缺失时回退总等级标准节点（与旧 FEAT_LEVELS 行为一致）。
    """
    from ..rules.feat_entitlement import entitled_asi_levels
    class_levels = character.get("class_levels") or {}
    return entitled_asi_levels(class_levels, character.get("level", 1))


def available_feats(character: dict) -> list[dict]:
    """返回角色当前可选的专长列表。

    规则出处:
      - PHB 2024 第五章「专长」: 专长分为起源/通用/战斗风格/传奇恩惠四类。
      - 起源专长仅在 1 级创建角色时选取（背景给予），升级时不可选。
      - 通用/战斗风格专长: 仅在 ASI/专长 entitlement 节点开放
        （标准 4/8/12/16 + 战士 6/14、游荡者 10 等职业额外节点——方案 §8.2）。
      - 传奇恩惠专长: 达到 19 级时可选（先决「等级19+」）。
      - 非复选专长（repeatable=False）不可重复选择。
      - 复选专长（repeatable=True，名字带 *）可多次选取。

    Args:
        character: 角色字典，需含 level、feats、可选 class_levels。

    Returns:
        可选专长字典列表（浅拷贝），按数据表原顺序排列。
        每个字典额外附带 ``already_taken`` 布尔字段，
        标识该专长是否已被角色选取（仅对复选专长有意义）。
    """
    level = character.get("level", 1)
    taken: set[str] = set(character.get("feats", []))
    entitled = _entitlement_for(character)

    result: list[dict] = []
    for feat in feat_db.FEATS:
        cat = feat["category"]
        # 起源专长仅在角色创建时由背景给予，升级流程不提供
        if cat == "起源":
            continue
        # 传奇恩惠专长先决条件为「等级19+」
        if cat == "传奇恩惠" and level < 19:
            continue
        # 通用与战斗风格专长：仅在 entitlement 节点等级开放
        if cat in ("通用", "战斗风格") and level not in entitled:
            # 若当前等级不是专长节点，仍允许查询（返回空由调用方处理）
            continue

        entry = dict(feat)
        entry["already_taken"] = feat["name_zh"] in taken
        # 非复选且已选 → 不可再选，跳过
        if not feat["repeatable"] and entry["already_taken"]:
            continue
        result.append(entry)

    return result


def select_feat(character: dict, feat_name: str) -> dict:
    """为角色选择一个专长，原地更新 character['feats']。

    规则校验（出处: PHB 2024 第五章「专长」）:
      - 专长必须存在于数据表。
      - 非复选专长（repeatable=False）不可重复选择。
      - 角色等级须满足专长的先决条件（简化：传奇恩惠需 19 级）。
      - ASI 与专长二选一：若本次升级已应用属性值提升(ASI)，则不可选择专长。
        出处: 创建角色/等级提升.htm Step 3（属性提升或专长，二选一）

    Args:
        character: 角色字典，需含 level 与 feats 列表。
        feat_name: 专长中文名。

    Returns:
        {"feat": name, "feats": [...], "already_taken": bool}

    Raises:
        ValueError: 专长不存在 / 不可重复选择 / 等级不满足先决条件 /
                    本次升级已选ASI（ASI与专长二选一）。
    """
    feat = feat_db.get_feat(feat_name)
    if feat is None:
        raise ValueError(f"未知专长 {feat_name!r}")

    level = character.get("level", 1)
    # 传奇恩惠专长先决: 等级19+
    if feat["category"] == "传奇恩惠" and level < 19:
        raise ValueError(
            f"专长 {feat_name!r} 需要等级19+，当前等级{level}"
        )
    # 起源专长不在升级流程中选取
    if feat["category"] == "起源":
        raise ValueError(
            f"起源专长 {feat_name!r} 仅在角色创建时由背景给予"
        )
    # ASI 与专长二选一：若本次升级已应用ASI，则禁止选择专长
    # 出处: 创建角色/等级提升.htm Step 3
    if character.get("asi_taken"):
        raise ValueError(
            f"本次升级已选择属性值提升(ASI)，不可同时选择专长 "
            f"{feat_name!r}（ASI与专长二选一）"
        )

    current: list[str] = list(character.get("feats", []))
    already_taken = feat_name in current

    if already_taken and not feat["repeatable"]:
        raise ValueError(
            f"专长 {feat_name!r} 不可重复选择（非复选专长）"
        )

    if not already_taken:
        current.append(feat_name)
    character["feats"] = current

    return {
        "feat": feat_name,
        "feats": current,
        "already_taken": already_taken,
    }


def level_up(
    character: dict,
    *,
    use_fixed_hp: bool = True,
    hit_die_roll: int | None = None,
    new_class: str | None = None,
    new_features: list[str] | None = None,
    ability_improvements: dict[str, int] | None = None,
) -> dict:
    """执行升级五步骤，返回升级结果摘要并原地更新角色字典。

    五步骤（出处: topics/玩家手册2024/创建角色/等级提升.htm "获得新的等级"）：
      1. 选择职业（默认同职业；可传 new_class 兼职）
      2. 修改生命值和生命骰（获得一个生命骰，HP上限增加）
      3. 记录新职业特性（调用方传入 new_features 列表）
      4. 修改熟练加值（PB 提升时角色卡上所有含PB的数值相应提升）
      5. 修改属性调整值（若体质调整值提升，HP上限额外提升等于当前等级的点数）

    参数:
      character: 角色字典，需含 level, xp, class_name, scores(含CON), hp_max 等。
      use_fixed_hp: True 使用固定HP增长表；False 掷生命骰。
      hit_die_roll: 若 use_fixed_hp=False，可传入固定的掷骰结果（测试用）。
      new_class: 若兼职，指定新职业名；None 表示在原职业升级。
      new_features: 升级后获得的新特性列表（由调用方根据职业表填入）。
      ability_improvements: 属性提升字典，如 {"CON": 1, "STR": 1}，
                            表示对应属性值增加多少。用于 Step 5。

    返回:
      {
        "new_level": int,
        "hp_gained": int,             # 本次升级HP上限增量
        "new_proficiency_bonus": int, # 新等级的PB
        "pb_changed": bool,           # PB是否较升级前提升
        "new_features": list[str],    # 新获得的特性
        "ability_improvements": dict, # 实际应用的属性提升
        "con_mod_change": int,        # 体质调整值的变化量
        "retroactive_hp": int,        # 因体质调整值提升而追溯增加的HP
        "tier": str,                  # 新等级的游戏阶段
      }
    """
    old_level = character.get("level", 1)
    xp = character.get("xp", 0)

    # 校验：是否达到下一级XP
    if old_level >= MAX_LEVEL:
        raise ValueError(f"角色已达最高等级{MAX_LEVEL}，无法升级")
    next_level = old_level + 1
    if xp < XP_TABLE[next_level]:
        raise ValueError(
            f"XP不足：当前{xp}，升至{next_level}级需{XP_TABLE[next_level]}"
        )

    # Step 1: 选择职业
    chosen_class = new_class if new_class is not None else character.get("class_name", "")
    if chosen_class not in CLASSES and chosen_class:
        # 允许未知职业但警告——实际应来自 classes.py
        pass

    # 当前体质调整值
    scores = character.get("scores", {})
    con_score = scores.get("CON", 10)
    con_mod = (con_score - 10) // 2

    # Step 2: 修改生命值和生命骰
    hp_gained = _hp_gain_for_level(
        chosen_class, next_level, con_mod,
        use_fixed=use_fixed_hp, roll=hit_die_roll,
    )

    # Step 5: 修改属性调整值（先处理属性提升，再算追溯HP）
    applied_improvements: dict[str, int] = {}
    con_mod_change = 0
    retroactive_hp = 0

    if ability_improvements:
        for ability, delta in ability_improvements.items():
            if delta == 0:
                continue
            old_score = scores.get(ability, 10)
            # 属性值上限20：任何属性提升后不得超过20
            # 出处: 创建角色/第三步：确定属性值.htm ; 通用专长「属性值提升」
            new_score = min(old_score + delta, 20)
            actual_delta = new_score - old_score  # 受上限裁剪后的实际增量
            old_mod = (old_score - 10) // 2
            new_mod = (new_score - 10) // 2
            mod_change = new_mod - old_mod
            scores[ability] = new_score
            applied_improvements[ability] = actual_delta
            if ability == "CON" and mod_change > 0:
                con_mod_change += mod_change
                # 体质调整值每提升1，HP上限额外提升等于当前等级（新等级）的点数
                retroactive_hp += mod_change * next_level

    # ASI 与专长二选一：若本次升级已应用属性提升(ASI)，则不可同时选择专长
    # 出处: 创建角色/等级提升.htm Step 3（属性提升或专长，二选一）
    asi_taken = bool(applied_improvements)

    # 合并 HP 增量：Step2 的增量 + Step5 的追溯增量
    total_hp_gained = hp_gained + retroactive_hp

    # Step 4: 修改熟练加值
    old_pb = proficiency_bonus(old_level)
    new_pb = proficiency_bonus(next_level)
    pb_changed = new_pb > old_pb

    # Step 3: 记录新职业特性
    features = new_features if new_features is not None else []

    # 更新角色字典
    character["level"] = next_level
    character["scores"] = scores
    character["hp_max"] = character.get("hp_max", 0) + total_hp_gained
    # 同时增加当前HP（长休外升级：当前HP也增加，但不恢复已消耗资源）
    # 规则: R-DM-043 长休外升级HP
    character["hp_current"] = character.get("hp_current", 0) + total_hp_gained
    if "features" not in character:
        character["features"] = []
    character["features"].extend(features)
    character["proficiency_bonus"] = new_pb
    # 记录本次升级是否已选择ASI（供 select_feat 校验二选一约束）
    character["asi_taken"] = asi_taken

    # 专长选择提示（方案 §8.2）: 达到 ASI/专长 entitlement 节点时，
    # 角色可选择一个专长；但若本次升级已应用ASI，则不可再选专长
    # （ASI与专长二选一）。节点由 entitlement 服务计算——标准 4/8/12/16/19
    # + 职业额外节点（战士 6/14、游荡者 10 等，按职业等级）。
    # 出处: PHB 2024 第五章「专长」; 等级提升.htm Step 3
    if not asi_taken:
        from ..rules.feat_entitlement import is_entitled_at
        # 升级后的 class_levels：兼职时新职业为 1 级，其余不变
        cls_levels = dict(character.get("class_levels") or {})
        if new_class:
            cls_levels[new_class] = max(int(cls_levels.get(new_class, 0)), 1)
        else:
            cls_levels[chosen_class or character.get("class_name", "")] = next_level
        feat_available = is_entitled_at(next_level, cls_levels)
    else:
        feat_available = False
    available_feat_list = available_feats(character) if feat_available else []

    return {
        "new_level": next_level,
        "hp_gained": total_hp_gained,
        "step2_hp": hp_gained,
        "new_proficiency_bonus": new_pb,
        "pb_changed": pb_changed,
        "new_features": features,
        "ability_improvements": applied_improvements,
        "asi_taken": asi_taken,
        "con_mod_change": con_mod_change,
        "retroactive_hp": retroactive_hp,
        "tier": get_tier(next_level),
        "feat_available": feat_available,
        "available_feats": available_feat_list,
    }


# ──────────────────────────────────────────────────────────────────────────
# R-DM-043 长休外升级HP（辅助函数）
# ──────────────────────────────────────────────────────────────────────────

def level_up_outside_rest(character: dict, hp_gain: int) -> dict:
    """长休外升级时，当前HP与HP上限适量增加，但不恢复已消耗资源。

    规则: R-DM-043 长休外升级HP
    出处: topics/城主指南2024/2.运作游戏/角色升级.htm

    参数:
      character: 角色字典，需含 hp_max, hp_current。
      hp_gain: 本次升级HP上限增量（来自 level_up 的 hp_gained）。

    返回: 更新后的角色字典（原地修改）。
    """
    character["hp_max"] = character.get("hp_max", 0) + hp_gain
    character["hp_current"] = character.get("hp_current", 0) + hp_gain
    return character


# ──────────────────────────────────────────────────────────────────────────
# 兼职规则（Multiclass）— P5 收敛（方案 §8.4）
# ──────────────────────────────────────────────────────────────────────────
# ★ P5: 兼职先决/熟练/法术位合并的规则权威收敛到 engine.multiclass
#   （brain 与 engine 不得再分别维护完整规则）。以下仅保留兼容委托壳，
#   已删除重复数据表 _MULTICLASS_PREREQ/_MULTICLASS_PROFICIENCIES/
#   _MULTICLASS_SPELL_SLOTS 等——历史版本曾把魔契师按 0.5 权重参与合并，
#   违反「Pact Magic 独立」（方案 §8.4），engine 实现不做该合并。

_ABILITIES_UPPER = {"STR", "DEX", "CON", "INT", "WIS", "CHA"}


def check_multiclass_prerequisite(character: dict, new_class: str) -> dict:
    """检查兼职先决条件（委托 engine.multiclass 权威实现）。

    规则: R-MC-001 兼职前置属性值（当前职业与新职业的主属性都需≥13）
    """
    from ..engine.multiclass import MulticlassService
    scores = character.get("scores", {})
    abilities = {ab.lower(): int(v) for ab, v in scores.items()
                 if ab in _ABILITIES_UPPER}
    res = MulticlassService().validate_multiclass(
        {}, new_class, abilities)
    failures = [] if res["valid"] else [f"先决条件未满足: {res['reason']}"]
    return {
        "eligible": res["valid"],
        "new_class": new_class,
        "prerequisites": [],
        "failures": failures,
    }


def multiclass_proficiencies(class_name: str) -> dict:
    """取兼职时该职业第 1 级获得的熟练（委托 engine.multiclass 权威实现）。

    规则: R-MC-003 兼职获得的熟练（不含豁免熟练）
    """
    from ..engine.multiclass import MulticlassService
    granted = MulticlassService().get_proficiencies_granted(class_name, set())
    return {
        "armor": "、".join(granted["armor"]) or "无",
        "weapons": "、".join(granted["weapons"]) or "无",
        "skills": 0,
        "skill_pool": [],
    }


def multiclass_spell_slots(class_levels: dict[str, int]) -> dict:
    """计算兼职施法者合并法术位（委托 engine.multiclass 权威实现）。

    规则: R-MC-002 兼职法术位合并（全/半施法者；魔契师 Pact 独立不合并）
    """
    from ..engine.multiclass import multiclass_spell_slots as _engine_slots
    return _engine_slots(class_levels)


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    """levelup 模块自检。"""

    # ── XP 表完整性 ──────────────────────────────────────
    assert len(XP_TABLE) == 20, f"XP表应有20个条目，实有{len(XP_TABLE)}"
    assert XP_TABLE[1] == 0
    assert XP_TABLE[2] == 300
    assert XP_TABLE[5] == 6500
    assert XP_TABLE[20] == 355000
    # XP 单调递增
    for i in range(1, 20):
        assert XP_TABLE[i] < XP_TABLE[i + 1], f"XP表在{i}级非递增"

    # ── 固定HP增长表 ─────────────────────────────────────
    assert FIXED_HP_GAIN["野蛮人"] == 7
    assert FIXED_HP_GAIN["战士"] == 6
    assert FIXED_HP_GAIN["圣武士"] == 6
    assert FIXED_HP_GAIN["游侠"] == 6
    assert FIXED_HP_GAIN["吟游诗人"] == 5
    assert FIXED_HP_GAIN["牧师"] == 5
    assert FIXED_HP_GAIN["德鲁伊"] == 5
    assert FIXED_HP_GAIN["武僧"] == 5
    assert FIXED_HP_GAIN["游荡者"] == 5
    assert FIXED_HP_GAIN["魔契师"] == 5
    assert FIXED_HP_GAIN["术士"] == 4
    assert FIXED_HP_GAIN["法师"] == 4
    # 全部12个职业都有条目
    assert len(FIXED_HP_GAIN) == 12, f"固定HP表应有12个职业，实有{len(FIXED_HP_GAIN)}"

    # ── 熟练加值 ─────────────────────────────────────────
    assert proficiency_bonus(1) == 2
    assert proficiency_bonus(4) == 2
    assert proficiency_bonus(5) == 3
    assert proficiency_bonus(8) == 3
    assert proficiency_bonus(9) == 4
    assert proficiency_bonus(12) == 4
    assert proficiency_bonus(13) == 5
    assert proficiency_bonus(16) == 5
    assert proficiency_bonus(17) == 6
    assert proficiency_bonus(20) == 6

    # ── 游戏阶段 ─────────────────────────────────────────
    assert get_tier(1) == "T1"
    assert get_tier(4) == "T1"
    assert get_tier(5) == "T2"
    assert get_tier(10) == "T2"
    assert get_tier(11) == "T3"
    assert get_tier(16) == "T3"
    assert get_tier(17) == "T4"
    assert get_tier(20) == "T4"

    # ── level_from_xp ────────────────────────────────────
    assert level_from_xp(0) == 1
    assert level_from_xp(299) == 1
    assert level_from_xp(300) == 2
    assert level_from_xp(899) == 2
    assert level_from_xp(900) == 3
    assert level_from_xp(355000) == 20
    assert level_from_xp(999999) == 20

    # ── check_level_up ───────────────────────────────────
    char_lv1_low = {"level": 1, "xp": 100}
    assert check_level_up(char_lv1_low) is False
    char_lv1_ok = {"level": 1, "xp": 300}
    assert check_level_up(char_lv1_ok) is True
    char_lv1_over = {"level": 1, "xp": 500}
    assert check_level_up(char_lv1_over) is True
    char_max = {"level": 20, "xp": 400000}
    assert check_level_up(char_max) is False

    # ── award_xp (R-DM-041) ──────────────────────────────
    party = [
        {"name": "A", "xp": 0},
        {"name": "B", "xp": 100},
        {"name": "C", "xp": 200},
    ]
    result = award_xp(party, 900)
    assert result["per_member"] == 300
    assert result["members"][0]["xp"] == 300
    assert result["members"][1]["xp"] == 400
    assert result["members"][2]["xp"] == 500
    # 余数向下取整
    result2 = award_xp([{"xp": 0}, {"xp": 0}], 301)
    assert result2["per_member"] == 150
    # 空队伍
    assert award_xp([], 100)["per_member"] == 0

    # ── milestone_xp (R-DM-042) ──────────────────────────
    major1 = milestone_xp("major", 1)
    minor1 = milestone_xp("minor", 1)
    assert major1 == 200
    assert minor1 == 50
    assert major1 > minor1
    # 高等级
    assert milestone_xp("major", 20) == 45000
    assert milestone_xp("minor", 20) == 12700

    # ── training_cost (R-DM-044) ─────────────────────────
    assert training_cost(2) == (10, 20)
    assert training_cost(4) == (10, 20)
    assert training_cost(5) == (20, 40)
    assert training_cost(10) == (20, 40)
    assert training_cost(11) == (30, 60)
    assert training_cost(16) == (30, 60)
    assert training_cost(17) == (40, 80)
    assert training_cost(20) == (40, 80)

    # ── session_based_level (R-DM-045) ───────────────────
    assert session_based_level(0) == 1
    assert session_based_level(1) == 2
    assert session_based_level(2) == 3
    assert session_based_level(3) == 4
    # 大量游戏回后封顶20
    assert session_based_level(100) == 20

    # ── level_up 端到端 ──────────────────────────────────
    # 场景1: 1级战士(CON=14→+2)，XP达到300，升到2级
    warrior = {
        "level": 1,
        "xp": 300,
        "class_name": "战士",
        "scores": {"STR": 16, "DEX": 12, "CON": 14, "INT": 10, "WIS": 10, "CHA": 10},
        "hp_max": 12,       # 1级: 10 + CON(+2) = 12
        "hp_current": 10,
        "features": [],
    }
    up = level_up(warrior, use_fixed_hp=True)
    assert up["new_level"] == 2
    # 战士固定HP=6, CON mod=+2 → 6+2=8
    assert up["step2_hp"] == 8
    assert up["hp_gained"] == 8
    assert up["new_proficiency_bonus"] == 2
    assert up["pb_changed"] is False
    assert up["tier"] == "T1"
    # 角色字典已更新
    assert warrior["level"] == 2
    assert warrior["hp_max"] == 20     # 12 + 8
    assert warrior["hp_current"] == 18  # 10 + 8

    # 场景2: 4级野蛮人(CON=16→+3)，升到5级，PB从+2→+3
    barb = {
        "level": 4,
        "xp": 6500,
        "class_name": "野蛮人",
        "scores": {"STR": 18, "DEX": 14, "CON": 16, "INT": 10, "WIS": 12, "CHA": 10},
        "hp_max": 47,   # 1级12 + 3级×(7+3=10)=30 → 42? 重算: 1级=12+3=15? 简化用任意合法值
        "hp_current": 40,
        "features": ["鲁莽攻击"],
    }
    up2 = level_up(barb, use_fixed_hp=True, new_features=["额外攻击", "本能直觉"])
    assert up2["new_level"] == 5
    # 野蛮人固定HP=7, CON mod=+3 → 7+3=10
    assert up2["step2_hp"] == 10
    assert up2["hp_gained"] == 10
    assert up2["new_proficiency_bonus"] == 3
    assert up2["pb_changed"] is True
    assert up2["tier"] == "T2"
    assert "额外攻击" in barb["features"]

    # 场景3: 升级时提升体质(CON 14→16, mod +2→+3)，追溯HP
    fighter2 = {
        "level": 3,
        "xp": 2700,
        "class_name": "战士",
        "scores": {"STR": 16, "DEX": 12, "CON": 14, "INT": 10, "WIS": 10, "CHA": 10},
        "hp_max": 30,
        "hp_current": 25,
        "features": [],
    }
    up3 = level_up(
        fighter2,
        use_fixed_hp=True,
        ability_improvements={"CON": 2},  # CON 14→16, mod +2→+3, change=+1
    )
    assert up3["new_level"] == 4
    # step2: 战士固定6 + CON旧mod+2 = 8
    assert up3["step2_hp"] == 8
    # 追溯: CON mod +1 × 新等级4 = 4
    assert up3["con_mod_change"] == 1
    assert up3["retroactive_hp"] == 4
    # 总HP增量 = 8 + 4 = 12
    assert up3["hp_gained"] == 12
    assert fighter2["hp_max"] == 42  # 30 + 12
    # CON 已更新
    assert fighter2["scores"]["CON"] == 16
    # B6: 本次升级已选ASI → asi_taken=True，4级本是专长等级但不可再选专长
    assert up3["asi_taken"] is True
    assert up3["feat_available"] is False
    assert up3["available_feats"] == []
    assert fighter2["asi_taken"] is True

    # 场景4: 掷骰模式（传入固定roll值便于断言）
    rogue = {
        "level": 2,
        "xp": 900,
        "class_name": "游荡者",
        "scores": {"STR": 10, "DEX": 16, "CON": 12, "INT": 14, "WIS": 10, "CHA": 10},
        "hp_max": 19,   # 1级: 8 + CON(+1) = 9; 2级: +8+1=9 → 18? 用任意合法值
        "hp_current": 15,
        "features": ["潜行攻击"],
    }
    up4 = level_up(rogue, use_fixed_hp=False, hit_die_roll=6)
    assert up4["new_level"] == 3
    # 游荡者 d8, roll=6, CON mod=+1 → 6+1=7
    assert up4["step2_hp"] == 7
    assert up4["hp_gained"] == 7

    # 场景5: XP不足时应报错
    try:
        low_char = {"level": 1, "xp": 100, "class_name": "战士",
                    "scores": {"CON": 10}, "hp_max": 10, "hp_current": 10, "features": []}
        level_up(low_char)
        assert False, "XP不足时应抛出ValueError"
    except ValueError:
        pass

    # 场景6: 兼职——战士升野蛮人
    multi = {
        "level": 1,
        "xp": 300,
        "class_name": "战士",
        "scores": {"STR": 16, "DEX": 12, "CON": 14, "INT": 10, "WIS": 10, "CHA": 10},
        "hp_max": 12,
        "hp_current": 12,
        "features": [],
    }
    up6 = level_up(multi, use_fixed_hp=True, new_class="野蛮人")
    # 野蛮人固定HP=7, CON mod=+2 → 7+2=9
    assert up6["step2_hp"] == 9
    assert up6["hp_gained"] == 9

    # ── available_feats / select_feat (PHB 第五章「专长」) ───
    # 等级4角色可选通用/战斗风格专长
    char_lv4 = {"level": 4, "feats": []}
    avail4 = available_feats(char_lv4)
    assert len(avail4) > 0, "等级4应有可选专长"
    # 不含起源专长
    assert all(f["category"] != "起源" for f in avail4)
    # 不含传奇恩惠（需19级）
    assert all(f["category"] != "传奇恩惠" for f in avail4)

    # 等级3角色不应有可选专长（非专长等级）
    char_lv3 = {"level": 3, "feats": []}
    assert available_feats(char_lv3) == []

    # 等级19角色可选传奇恩惠
    char_lv19 = {"level": 19, "feats": []}
    avail19 = available_feats(char_lv19)
    boon_names = [f["name_zh"] for f in avail19 if f["category"] == "传奇恩惠"]
    assert len(boon_names) == 12, f"应有12个传奇恩惠，实有{len(boon_names)}"

    # select_feat: 选择一个通用专长（演员，非复选）
    char_sel = {"level": 4, "feats": []}
    r = select_feat(char_sel, "演员")
    assert r["feat"] == "演员"
    assert "演员" in char_sel["feats"]

    # 非复选专长不可重复选择
    try:
        select_feat(char_sel, "演员")
        assert False, "非复选专长重复选择应报错"
    except ValueError:
        pass

    # 复选专长可重复选择（如「属性值提升」，repeatable=True）
    char_rep = {"level": 4, "feats": ["属性值提升"]}
    r2 = select_feat(char_rep, "属性值提升")
    assert r2["already_taken"] is True
    # 复选专长不追加重复条目
    assert char_rep["feats"].count("属性值提升") == 1

    # 起源专长不可在升级流程选取
    try:
        select_feat({"level": 4, "feats": []}, "警戒")
        assert False, "起源专长应在升级流程中被拒绝"
    except ValueError:
        pass

    # 未知专长报错
    try:
        select_feat({"level": 4, "feats": []}, "不存在的专长")
        assert False, "未知专长应报错"
    except ValueError:
        pass

    # level_up 到达专长等级时返回 feat_available=True
    char_to4 = {
        "level": 3,
        "xp": 2700,
        "class_name": "战士",
        "scores": {"STR": 16, "DEX": 12, "CON": 14, "INT": 10, "WIS": 10, "CHA": 10},
        "hp_max": 28,
        "hp_current": 20,
        "features": [],
    }
    up_feat = level_up(char_to4, use_fixed_hp=True)
    assert up_feat["new_level"] == 4
    assert up_feat["feat_available"] is True
    assert up_feat["asi_taken"] is False
    assert len(up_feat["available_feats"]) > 0

    # ── B6: ASI与专长二选一 ──────────────────────────────
    # 升级时选ASI → feat_available=False，且 select_feat 应拒绝
    asi_char = {
        "level": 3, "xp": 2700, "class_name": "战士",
        "scores": {"STR": 16, "DEX": 12, "CON": 14, "INT": 10, "WIS": 10, "CHA": 10},
        "hp_max": 28, "hp_current": 20, "features": [],
    }
    up_asi = level_up(asi_char, use_fixed_hp=True, ability_improvements={"STR": 2})
    assert up_asi["asi_taken"] is True
    assert up_asi["feat_available"] is False  # 4级本是专长等级，但已选ASI
    assert up_asi["available_feats"] == []
    assert asi_char["asi_taken"] is True
    try:
        select_feat(asi_char, "演员")
        assert False, "已选ASI时 select_feat 应抛出 ValueError"
    except ValueError as e:
        assert "ASI" in str(e) or "二选一" in str(e), f"错误信息应提及ASI二选一，实为: {e}"
    # 升级未选ASI → select_feat 正常可用
    no_asi_char = {
        "level": 3, "xp": 2700, "class_name": "战士",
        "scores": {"STR": 16, "DEX": 12, "CON": 14, "INT": 10, "WIS": 10, "CHA": 10},
        "hp_max": 28, "hp_current": 20, "features": [],
    }
    up_no_asi = level_up(no_asi_char, use_fixed_hp=True)
    assert up_no_asi["asi_taken"] is False
    assert up_no_asi["feat_available"] is True
    r_sel = select_feat(no_asi_char, "演员")
    assert r_sel["feat"] == "演员"

    # ── B7: 属性值上限20 ──────────────────────────────────
    # CON 19 +2 → 截断为20，实际增量1
    cap_char = {
        "level": 3, "xp": 2700, "class_name": "战士",
        "scores": {"STR": 16, "DEX": 12, "CON": 19, "INT": 10, "WIS": 10, "CHA": 10},
        "hp_max": 30, "hp_current": 25, "features": [],
    }
    up_cap = level_up(cap_char, use_fixed_hp=True, ability_improvements={"CON": 2})
    assert cap_char["scores"]["CON"] == 20  # 19+2=21→截断20
    assert up_cap["ability_improvements"]["CON"] == 1  # 实际增量
    # CON mod: 19→+4, 20→+5, change+1 → 追溯1×4=4
    assert up_cap["con_mod_change"] == 1
    assert up_cap["retroactive_hp"] == 4
    # 已满20再加 → 仍为20，实际增量0，无追溯
    cap_full = {
        "level": 3, "xp": 2700, "class_name": "战士",
        "scores": {"STR": 16, "DEX": 12, "CON": 20, "INT": 10, "WIS": 10, "CHA": 10},
        "hp_max": 34, "hp_current": 30, "features": [],
    }
    up_full = level_up(cap_full, use_fixed_hp=True, ability_improvements={"CON": 2})
    assert cap_full["scores"]["CON"] == 20  # 不超20
    assert up_full["ability_improvements"]["CON"] == 0
    assert up_full["con_mod_change"] == 0
    assert up_full["retroactive_hp"] == 0

    # ── B8: 未知职业HP回退公式 = hd//2+1（d12→7，修复前为6）──
    # 各职业生命骰的回退公式与固定表一致
    for cname, cdata in CLASSES.items():
        hd = cdata["hit_die"]
        assert hd // 2 + 1 == FIXED_HP_GAIN[cname], (
            f"{cname} 回退公式 {hd//2+1} 与固定表 {FIXED_HP_GAIN[cname]} 不符"
        )
    # 关键：d12→7（修复前 (12+1)//2=6 是错误的）
    assert 12 // 2 + 1 == 7
    assert 6 // 2 + 1 == 4

    print("[levelup] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
