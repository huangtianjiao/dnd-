"""装备数据表 — 护甲 / 武器 / 词条 / 精通 / 钱币。

纯数据 + 少量计算（AC）。标注规则ID+出处。规则依据 R-ITM-001~015。
"""

from __future__ import annotations


# ──────────────────────────────────────────────────────────────────────────
# 钱币换算（以 GP 为基准）
# 规则: R-ITM-001 钱币换算  出处: topics/玩家手册2024/装备/钱币.htm
# ──────────────────────────────────────────────────────────────────────────
COIN_TO_GP = {"CP": 0.01, "SP": 0.10, "EP": 0.50, "GP": 1.0, "PP": 10.0}


def convert_coins(amount: float, frm: str, to: str = "GP") -> float:
    """钱币换算。1GP=100CP=10SP=2EP=0.1PP。"""
    gp = amount * COIN_TO_GP[frm]
    return gp / COIN_TO_GP[to]


# ──────────────────────────────────────────────────────────────────────────
# 护甲表（2024版，13 套护甲 + 盾牌）
# 规则: R-ITM-003 护甲表  出处: topics/玩家手册2024/装备/护甲.htm
# dex_mode: full=+全部敏捷调整值; cap2=+敏捷调整值(最大+2); none=不加; bonus=盾牌AC加值(+2)
# ──────────────────────────────────────────────────────────────────────────
ARMOR = {
    # 轻甲（穿1分钟/脱1分钟）
    "布甲":     {"cat": "轻", "base_ac": 11, "dex_mode": "full", "str_req": None, "stealth_disadv": True,  "weight": 8,  "price_gp": 5,    "don_time": 1,  "doff_time": 1},
    "皮甲":     {"cat": "轻", "base_ac": 11, "dex_mode": "full", "str_req": None, "stealth_disadv": False, "weight": 10, "price_gp": 10,   "don_time": 1,  "doff_time": 1},
    "镶钉皮甲": {"cat": "轻", "base_ac": 12, "dex_mode": "full", "str_req": None, "stealth_disadv": False, "weight": 13, "price_gp": 45,   "don_time": 1,  "doff_time": 1},
    # 中甲（穿5分钟/脱1分钟）
    "兽皮甲":   {"cat": "中", "base_ac": 12, "dex_mode": "cap2", "str_req": None, "stealth_disadv": False, "weight": 12, "price_gp": 10,   "don_time": 5,  "doff_time": 1},
    "链甲衫":   {"cat": "中", "base_ac": 13, "dex_mode": "cap2", "str_req": None, "stealth_disadv": False, "weight": 20, "price_gp": 50,   "don_time": 5,  "doff_time": 1},
    "鳞甲":     {"cat": "中", "base_ac": 14, "dex_mode": "cap2", "str_req": None, "stealth_disadv": True,  "weight": 45, "price_gp": 50,   "don_time": 5,  "doff_time": 1},
    "胸甲":     {"cat": "中", "base_ac": 14, "dex_mode": "cap2", "str_req": None, "stealth_disadv": False, "weight": 20, "price_gp": 400,  "don_time": 5,  "doff_time": 1},
    "半身板甲": {"cat": "中", "base_ac": 15, "dex_mode": "cap2", "str_req": None, "stealth_disadv": True,  "weight": 40, "price_gp": 750,  "don_time": 5,  "doff_time": 1},
    # 重甲（穿10分钟/脱5分钟）
    "环甲":     {"cat": "重", "base_ac": 14, "dex_mode": "none", "str_req": None, "stealth_disadv": True,  "weight": 40, "price_gp": 30,   "don_time": 10, "doff_time": 5},
    "链甲":     {"cat": "重", "base_ac": 16, "dex_mode": "none", "str_req": 13,  "stealth_disadv": True,  "weight": 55, "price_gp": 75,   "don_time": 10, "doff_time": 5},
    "板条甲":   {"cat": "重", "base_ac": 17, "dex_mode": "none", "str_req": 15,  "stealth_disadv": True,  "weight": 60, "price_gp": 200,  "don_time": 10, "doff_time": 5},
    "板甲":     {"cat": "重", "base_ac": 18, "dex_mode": "none", "str_req": 15,  "stealth_disadv": True,  "weight": 65, "price_gp": 1500, "don_time": 10, "doff_time": 5},
    # 盾牌（穿/脱各1操作动作；以 0.1 分钟表示）
    "盾牌":     {"cat": "盾", "base_ac": 2,  "dex_mode": "bonus", "str_req": None, "stealth_disadv": False, "weight": 6,  "price_gp": 10,   "don_time": 0.1, "doff_time": 0.1},
}


def get_armor_entry(name: str) -> dict:
    """取护甲条目。规则: R-ITM-003"""
    if name not in ARMOR:
        raise KeyError(f"未知护甲 {name!r}，可选: {list(ARMOR)}")
    return ARMOR[name]


def compute_ac(armor_entry: dict, dex_mod: int, has_shield: bool = False) -> int:
    """根据护甲类别计算基础 AC（无甲=10+敏捷，见 R-CMB-021/R-GLS-006）。

    规则: R-ITM-004 AC计算公式  出处: topics/玩家手册2024/装备/护甲.htm
    """
    m = armor_entry["dex_mode"]
    if m == "full":
        ac = armor_entry["base_ac"] + dex_mod
    elif m == "cap2":
        ac = armor_entry["base_ac"] + min(dex_mod, 2)
    elif m == "none":
        ac = armor_entry["base_ac"]                  # 重甲忽略敏捷
    elif m == "bonus":
        ac = armor_entry["base_ac"]                  # 盾牌单独作加值
    else:
        ac = armor_entry["base_ac"]
    if has_shield:
        ac += 2                                       # 盾牌 +2
    return ac


def compute_unarmored_ac(dex_mod: int) -> int:
    """无甲基础 AC = 10 + 敏捷调整值。

    规则: R-CMB-021 / R-GLS-006  出处: 进行游戏/攻击检定.htm ; 术语汇编/常见规则词汇.htm
    """
    return 10 + dex_mod


def armor_str_penalty(armor_entry: dict, str_score: int, base_speed: int) -> int:
    """力量低于护甲要求时移速 -10 尺。

    规则: R-ITM-005 护甲力量要求与移速惩罚  出处: 装备/护甲.htm
    """
    req = armor_entry.get("str_req")
    if req is not None and str_score < req:
        return base_speed - 10
    return base_speed


def armor_stealth_disadv(armor_entry: dict) -> bool:
    """标注"劣势"的护甲使敏捷(隐匿)检定劣势。规则: R-ITM-006"""
    return armor_entry["stealth_disadv"]


# ──────────────────────────────────────────────────────────────────────────
# 穿脱护甲时间
# 规则: R-ITM-007 穿脱护甲时间  出处: 装备/护甲.txt
#   轻甲: 穿/脱各1分钟；中甲: 穿5分钟/脱1分钟；重甲: 穿10分钟/脱5分钟；
#   盾牌: 穿/脱各1个操作动作（此处以 0.1 分钟表示）。
# ──────────────────────────────────────────────────────────────────────────

def armor_don_time(armor_name: str) -> float:
    """穿戴护甲所需时间（分钟）。

    规则: R-ITM-007 穿脱护甲时间  出处: 装备/护甲.txt
    """
    return get_armor_entry(armor_name)["don_time"]


def armor_doff_time(armor_name: str) -> float:
    """卸除护甲所需时间（分钟）。

    规则: R-ITM-007 穿脱护甲时间  出处: 装备/护甲.txt
    """
    return get_armor_entry(armor_name)["doff_time"]


# ──────────────────────────────────────────────────────────────────────────
# 护甲受训
# 规则: R-ITM-008 护甲受训  出处: 装备/护甲.txt
#   未受训穿戴轻/中/重护甲 → 力量与敏捷的 D20 检定劣势 + 无法施法。
#   盾牌未受训 → 不获得其 AC 加值（由调用方在 AC 计算时处理）。
# ──────────────────────────────────────────────────────────────────────────

def untrained_armor_penalty(has_training: bool) -> dict:
    """未受训穿戴护甲的惩罚。

    规则: R-ITM-008 护甲受训  出处: 装备/护甲.txt
    返回: {"disadvantage_str": bool, "disadvantage_dex": bool, "cannot_cast": bool}
          未受训时三项均为 True（力量/敏捷 D20 检定劣势且无法施法）；
          受训时三项均为 False。
    """
    if has_training:
        return {"disadvantage_str": False, "disadvantage_dex": False, "cannot_cast": False}
    return {"disadvantage_str": True, "disadvantage_dex": True, "cannot_cast": True}


# ──────────────────────────────────────────────────────────────────────────
# 武器表（2024版，38 件）
# 规则: R-ITM-012 武器表  出处: topics/玩家手册2024/装备/武器.htm
# dmg 形如 "1d8穿刺"；props 为词条列表；mastery 为精通词条
# ──────────────────────────────────────────────────────────────────────────
WEAPONS = {
    # 简易近战
    "短棒":   {"cat": "简易近战", "dmg": "1d4钝击",  "props": ["轻型"],                    "mastery": "缓速", "wt": 2,    "price": "1SP"},
    "匕首":   {"cat": "简易近战", "dmg": "1d4穿刺",  "props": ["灵巧", "轻型", "投掷"],     "range": (20, 60),    "mastery": "迅击", "wt": 1,    "price": "2GP"},
    "巨棒":   {"cat": "简易近战", "dmg": "1d8钝击",  "props": ["双手"],                    "mastery": "推离", "wt": 10,   "price": "2SP"},
    "手斧":   {"cat": "简易近战", "dmg": "1d6挥砍",  "props": ["轻型", "投掷"],             "range": (20, 60),    "mastery": "侵扰", "wt": 2,    "price": "5GP"},
    "标枪":   {"cat": "简易近战", "dmg": "1d6穿刺",  "props": ["投掷"],                    "range": (30, 120),   "mastery": "缓速", "wt": 2,    "price": "5SP"},
    "轻锤":   {"cat": "简易近战", "dmg": "1d4钝击",  "props": ["轻型", "投掷"],             "range": (20, 60),    "mastery": "迅击", "wt": 2,    "price": "2GP"},
    "硬头锤": {"cat": "简易近战", "dmg": "1d6钝击",  "props": [],                          "mastery": "削弱", "wt": 4,    "price": "5GP"},
    "长棍":   {"cat": "简易近战", "dmg": "1d6钝击",  "props": ["多用"],                    "versatile_damage": "1d8",  "mastery": "失衡", "wt": 4,    "price": "2SP"},
    "镰刀":   {"cat": "简易近战", "dmg": "1d4挥砍",  "props": ["轻型"],                    "mastery": "迅击", "wt": 2,    "price": "1GP"},
    "矛":     {"cat": "简易近战", "dmg": "1d6穿刺",  "props": ["投掷", "多用"],             "range": (20, 60), "versatile_damage": "1d8",  "mastery": "削弱", "wt": 3,    "price": "1GP"},
    # 简易远程
    "飞镖":   {"cat": "简易远程", "dmg": "1d4穿刺",  "props": ["灵巧", "投掷"],             "range": (20, 60),    "mastery": "侵扰", "wt": 0.25, "price": "5CP"},
    "轻弩":   {"cat": "简易远程", "dmg": "1d8穿刺",  "props": ["弹药", "装填", "双手"],     "range": (80, 320),   "mastery": "缓速", "wt": 5,    "price": "25GP"},
    "短弓":   {"cat": "简易远程", "dmg": "1d6穿刺",  "props": ["弹药", "双手"],             "range": (80, 320),   "mastery": "侵扰", "wt": 2,    "price": "25GP"},
    "投石索": {"cat": "简易远程", "dmg": "1d4钝击",  "props": ["弹药"],                    "range": (30, 120),   "mastery": "缓速", "wt": None, "price": "1SP"},
    # 军用近战
    "战斧":   {"cat": "军用近战", "dmg": "1d8挥砍",  "props": ["多用"],                    "versatile_damage": "1d10", "mastery": "失衡", "wt": 4,    "price": "10GP"},
    "链枷":   {"cat": "军用近战", "dmg": "1d8钝击",  "props": [],                          "mastery": "削弱", "wt": 2,    "price": "10GP"},
    "长柄刀": {"cat": "军用近战", "dmg": "1d10挥砍", "props": ["重型", "触及", "双手"],     "mastery": "擦掠", "wt": 6,    "price": "20GP"},
    "巨斧":   {"cat": "军用近战", "dmg": "1d12挥砍", "props": ["重型", "双手"],             "mastery": "横扫", "wt": 7,    "price": "30GP"},
    "巨剑":   {"cat": "军用近战", "dmg": "2d6挥砍",  "props": ["重型", "双手"],             "mastery": "擦掠", "wt": 6,    "price": "50GP"},
    "戟":     {"cat": "军用近战", "dmg": "1d10挥砍", "props": ["重型", "触及", "双手"],     "mastery": "横扫", "wt": 6,    "price": "20GP"},
    "骑枪":   {"cat": "军用近战", "dmg": "1d10穿刺", "props": ["重型", "触及", "双手"],     "mastery": "失衡", "wt": 6,    "price": "10GP"},
    "长剑":   {"cat": "军用近战", "dmg": "1d8挥砍",  "props": ["多用"],                    "versatile_damage": "1d10", "mastery": "削弱", "wt": 3,    "price": "15GP"},
    "巨锤":   {"cat": "军用近战", "dmg": "2d6钝击",  "props": ["重型", "双手"],             "mastery": "失衡", "wt": 10,   "price": "10GP"},
    "钉头锤": {"cat": "军用近战", "dmg": "1d8穿刺",  "props": [],                          "mastery": "削弱", "wt": 4,    "price": "15GP"},
    "长矛":   {"cat": "军用近战", "dmg": "1d10穿刺", "props": ["重型", "触及", "双手"],     "mastery": "推离", "wt": 18,   "price": "5GP"},
    "刺剑":   {"cat": "军用近战", "dmg": "1d8穿刺",  "props": ["灵巧"],                    "mastery": "侵扰", "wt": 2,    "price": "25GP"},
    "弯刀":   {"cat": "军用近战", "dmg": "1d6挥砍",  "props": ["灵巧", "轻型"],             "mastery": "迅击", "wt": 3,    "price": "25GP"},
    "短剑":   {"cat": "军用近战", "dmg": "1d6穿刺",  "props": ["灵巧", "轻型"],             "mastery": "侵扰", "wt": 2,    "price": "10GP"},
    "三叉戟": {"cat": "军用近战", "dmg": "1d8穿刺",  "props": ["投掷", "多用"],             "range": (20, 60), "versatile_damage": "1d10", "mastery": "失衡", "wt": 4,    "price": "5GP"},
    "战镐":   {"cat": "军用近战", "dmg": "1d8穿刺",  "props": ["多用"],                    "versatile_damage": "1d10", "mastery": "削弱", "wt": 2,    "price": "5GP"},
    "战锤":   {"cat": "军用近战", "dmg": "1d8钝击",  "props": ["多用"],                    "versatile_damage": "1d10", "mastery": "推离", "wt": 2,    "price": "15GP"},
    "鞭":     {"cat": "军用近战", "dmg": "1d4挥砍",  "props": ["灵巧", "触及"],             "mastery": "缓速", "wt": 3,    "price": "2GP"},
    # 军用远程
    "吹箭筒": {"cat": "军用远程", "dmg": "1穿刺",    "props": ["弹药", "装填"],             "range": (25, 100),   "mastery": "侵扰", "wt": 1,    "price": "10GP"},
    "手弩":   {"cat": "军用远程", "dmg": "1d6穿刺",  "props": ["弹药", "轻型", "装填"],     "range": (30, 120),   "mastery": "侵扰", "wt": 3,    "price": "75GP"},
    "重弩":   {"cat": "军用远程", "dmg": "1d10穿刺", "props": ["弹药", "重型", "装填", "双手"], "range": (100, 400), "mastery": "推离", "wt": 18, "price": "50GP"},
    "长弓":   {"cat": "军用远程", "dmg": "1d8穿刺",  "props": ["弹药", "重型", "双手"],     "range": (150, 600),  "mastery": "缓速", "wt": 2,    "price": "50GP"},
    "火铳":   {"cat": "军用远程", "dmg": "1d12穿刺", "props": ["弹药", "装填", "双手"],     "range": (40, 120),   "mastery": "缓速", "wt": 10,   "price": "500GP"},
    "手铳":   {"cat": "军用远程", "dmg": "1d10穿刺", "props": ["弹药", "装填"],             "range": (30, 90),    "mastery": "侵扰", "wt": 3,    "price": "250GP"},
}


def get_weapon_entry(name: str) -> dict:
    """取武器条目。规则: R-ITM-012"""
    if name not in WEAPONS:
        raise KeyError(f"未知武器 {name!r}，可选: {list(WEAPONS)}")
    return WEAPONS[name]


def weapon_damage_dice(name: str) -> str:
    """取武器伤害骰表达式（如 '1d8'；吹箭筒 '1'）。规则: R-ITM-012"""
    dmg = get_weapon_entry(name)["dmg"]  # 形如 "1d8穿刺" / "1穿刺"
    for t in ("穿刺", "挥砍", "钝击"):
        if t in dmg:
            return dmg.split(t)[0]
    return dmg


def weapon_damage_type(name: str) -> str:
    """取武器伤害类型。规则: R-ITM-012"""
    dmg = get_weapon_entry(name)["dmg"]
    for t in ["穿刺", "挥砍", "钝击"]:
        if t in dmg:
            return t
    return "钝击"


def resolve_weapon_damage(name: str) -> tuple[str, str]:
    """取武器的 (伤害骰表达式, 伤害类型)，处理徒手与未知武器。

    - 徒手（name ∈ {"","徒手","徒手打击"}）→ ("1", "钝击")；
      命中后由 damage 管线加力量调整值（add_mod=True）得 1+力量调整值。
    - 已知武器 → (weapon_damage_dice, weapon_damage_type)。
    - 未知武器名（非徒手且不在 WEAPONS）→ 保守回退 ("1d8", "挥砍")（罕见）。

    详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段A4/B1。
    """
    if name in ("", "徒手", "徒手打击"):
        return "1", "钝击"
    try:
        return weapon_damage_dice(name), weapon_damage_type(name)
    except KeyError:
        return "1d8", "挥砍"


# ──────────────────────────────────────────────────────────────────────────
# 武器射程 / 多用伤害 / 熟练度
# 规则: R-ITM-014 武器词条(射程/投掷/多用) / R-ITM-013 武器熟练
# 出处: 装备/武器.txt ; 装备/词条.txt
# ──────────────────────────────────────────────────────────────────────────

def weapon_range(weapon_name: str) -> tuple[int, int] | None:
    """取武器射程 (常规射程, 最大射程)，单位：尺。

    规则: R-ITM-014 武器词条「射程」「投掷」  出处: 装备/武器.txt ; 装备/词条.txt
    返回: 远程/投掷武器返回 (常规, 最大) 元组；纯近战武器返回 None。
    说明: 超常规射程攻击检定劣势；不能攻击最大射程外目标
          （由 engine.combat.check_range 处理优劣势/不可达）。
    """
    return get_weapon_entry(weapon_name).get("range")


def weapon_versatile_damage(weapon_name: str) -> str | None:
    """取多用(versatile)武器双手持用时的近战伤害骰表达式。

    规则: R-ITM-014 武器词条「多用」  出处: 装备/武器.txt ; 装备/词条.txt
    返回: 多用武器返回双手伤害骰（如长剑 "1d10"）；非多用武器返回 None。
    """
    return get_weapon_entry(weapon_name).get("versatile_damage")


def check_weapon_proficiency(character_weapon_prof: list[str], weapon_name: str) -> bool:
    """检查角色是否熟练该武器。

    规则: R-ITM-013 武器熟练  出处: 装备/武器.txt
    说明: 武器熟练通常依照分类获取（简易武器/军用武器）。支持三类匹配：
          ① 直接武器名（如 "长剑"）；
          ② 宽分类（"简易武器" / "军用武器"）；
          ③ 细分类（"简易近战" / "简易远程" / "军用近战" / "军用远程"）。
          不熟练时熟练加值不加到攻击检定（由调用方据本返回值处理）。
    """
    if weapon_name in character_weapon_prof:
        return True
    entry = get_weapon_entry(weapon_name)
    cat = entry["cat"]                       # 简易近战/简易远程/军用近战/军用远程
    broad = "简易武器" if cat.startswith("简易") else ("军用武器" if cat.startswith("军用") else None)
    if broad and broad in character_weapon_prof:
        return True
    if cat in character_weapon_prof:          # 细分类
        return True
    return False


# ──────────────────────────────────────────────────────────────────────────
# 职业→起始默认武器
# 角色创建时填入 equipped_weapon 的兜底（不解析 classes.starting_equipment 自由文本）。
# 详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段A2。
# ──────────────────────────────────────────────────────────────────────────
DEFAULT_WEAPON_BY_CLASS = {
    "战士": "长剑", "圣武士": "长剑", "野蛮人": "巨斧",
    "游荡者": "短剑", "武僧": "短剑",
    "游侠": "短弓", "吟游诗人": "刺剑",
    "法师": "匕首", "术士": "匕首", "魔契师": "匕首",
    "牧师": "硬头锤", "德鲁伊": "弯刀",
}


def default_weapon_for_class(char_class: str) -> str:
    """职业起始默认武器名（攻击兜底用）。

    未知职业回退"匕首"（最轻量简易武器）。返回的武器名均在 WEAPONS 表内。
    """
    return DEFAULT_WEAPON_BY_CLASS.get(char_class, "匕首")


# ──────────────────────────────────────────────────────────────────────────
# 武器词条（10 项）与精通词条（8 项）
# 规则: R-ITM-014 武器词条 / R-ITM-015 精通词条
# 出处: topics/玩家手册2024/装备/词条.htm ; 精通词条.htm
# ──────────────────────────────────────────────────────────────────────────
PROPERTIES = {
    "弹药": "需对应弹药;每次攻击耗1枚;战后1分钟回收一半(向下取整);近战使用视为临时武器",
    "灵巧": "攻击检定与伤害可用力量或敏捷调整值(须同一值)",
    "重型": "力量<13用重型近战攻击检定劣势;敏捷<13用重型远程攻击检定劣势",
    "轻型": "攻击动作用轻型武器攻击后,可用附赠动作用另一轻型武器再攻击一次,第二次伤害不加属性调整值(负数除外)",
    "装填": "用动作/附赠/反应射击时只能射出一发,无视额外攻击次数",
    "射程": "(常规/最大);超常规射程攻击检定劣势;不能攻击最大射程外目标",
    "触及": "触及范围+5尺(含借机攻击)",
    "投掷": "可投掷发动远程攻击;近战武器投掷用近战相同属性调整值",
    "双手": "需双手并用",
    "多用": "可单手或双手;括号内为双手近战伤害",
}

MASTERY = {
    "横扫": "命中后可对5尺内另一生物再攻击一次,造成武器伤害(不加属性调整值,负数除外);每回合1次",
    "擦掠": "失手仍造成=所用属性调整值的伤害(同武器伤害类型)",
    "迅击": "轻型词条的额外攻击改用攻击动作而非附赠动作(每回合仍1次)",
    "推离": "命中体型≤大型生物可直线推离至多10尺",
    "削弱": "命中后至下回合开始前,目标下一次攻击检定劣势",
    "缓速": "命中造成伤害可令目标速度-10尺至下回合开始;多次命中不叠加",
    "失衡": "命中可迫使目标体质豁免(DC=8+本次攻击调整值+PB),失败倒地",
    "侵扰": "命中造成伤害后至下回合结束前,对该生物下一次攻击检定优势",
}


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 钱币（R-ITM-001）
    assert convert_coins(1, "GP") == 1.0
    assert convert_coins(100, "CP", "GP") == 1.0
    assert convert_coins(1, "PP", "GP") == 10.0
    # 护甲 AC（R-ITM-004）
    assert compute_ac(ARMOR["皮甲"], dex_mod=3) == 14        # 11+3
    assert compute_ac(ARMOR["半身板甲"], dex_mod=5) == 17     # 15+min(5,2)=17
    assert compute_ac(ARMOR["链甲"], dex_mod=5) == 16          # 重甲不加敏捷
    assert compute_ac(ARMOR["皮甲"], dex_mod=3, has_shield=True) == 16  # 11+3+2
    assert compute_unarmored_ac(3) == 13                       # 10+3
    # 力量不足惩罚（R-ITM-005）
    assert armor_str_penalty(ARMOR["板甲"], 14, 30) == 20      # 15需求，14不足→-10
    assert armor_str_penalty(ARMOR["板甲"], 15, 30) == 30
    # 隐匿劣势（R-ITM-006）
    assert armor_stealth_disadv(ARMOR["板甲"]) is True
    assert armor_stealth_disadv(ARMOR["皮甲"]) is False
    # 武器表（R-ITM-012）
    assert len(WEAPONS) == 38
    assert get_weapon_entry("巨剑")["dmg"] == "2d6挥砍"
    assert get_weapon_entry("匕首")["props"] == ["灵巧", "轻型", "投掷"]
    assert "灵巧" in PROPERTIES and "横扫" in MASTERY
    # 穿脱护甲时间（R-ITM-007）
    assert armor_don_time("皮甲") == 1 and armor_doff_time("皮甲") == 1            # 轻甲各1
    assert armor_don_time("链甲衫") == 5 and armor_doff_time("链甲衫") == 1       # 中甲穿5/脱1
    assert armor_don_time("板甲") == 10 and armor_doff_time("板甲") == 5          # 重甲穿10/脱5
    assert armor_don_time("盾牌") == 0.1 and armor_doff_time("盾牌") == 0.1       # 盾牌1操作动作
    # 护甲受训惩罚（R-ITM-008）
    assert untrained_armor_penalty(True) == {"disadvantage_str": False, "disadvantage_dex": False, "cannot_cast": False}
    assert untrained_armor_penalty(False) == {"disadvantage_str": True, "disadvantage_dex": True, "cannot_cast": True}
    # 武器射程（R-ITM-014 射程/投掷）
    assert weapon_range("轻弩") == (80, 320)
    assert weapon_range("长弓") == (150, 600)
    assert weapon_range("匕首") == (20, 60)
    assert weapon_range("标枪") == (30, 120)
    assert weapon_range("投石索") == (30, 120)
    assert weapon_range("重弩") == (100, 400)
    assert weapon_range("长剑") is None and weapon_range("巨剑") is None   # 纯近战无射程
    # 多用武器双手伤害（R-ITM-014 多用）
    assert weapon_versatile_damage("长剑") == "1d10"
    assert weapon_versatile_damage("战斧") == "1d10"
    assert weapon_versatile_damage("战镐") == "1d10" and weapon_versatile_damage("战锤") == "1d10"
    assert weapon_versatile_damage("长棍") == "1d8" and weapon_versatile_damage("矛") == "1d8"
    assert weapon_versatile_damage("三叉戟") == "1d10"
    assert weapon_versatile_damage("匕首") is None and weapon_versatile_damage("巨剑") is None
    # 武器熟练度（R-ITM-013）
    assert check_weapon_proficiency(["长剑"], "长剑") is True                   # 直接名
    assert check_weapon_proficiency(["简易武器"], "匕首") is True              # 宽分类(简易)
    assert check_weapon_proficiency(["简易武器"], "短棒") is True
    assert check_weapon_proficiency(["简易武器"], "长剑") is False             # 简易不含军用
    assert check_weapon_proficiency(["军用武器"], "长剑") is True              # 宽分类(军用)
    assert check_weapon_proficiency(["军用武器"], "巨剑") is True
    assert check_weapon_proficiency(["简易近战"], "短棒") is True              # 细分类
    assert check_weapon_proficiency(["简易近战"], "飞镖") is False             # 飞镖是简易远程
    assert check_weapon_proficiency(["军用远程"], "长弓") is True
    assert check_weapon_proficiency([], "长剑") is False
    print("[equipment] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
