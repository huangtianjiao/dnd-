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
    "布甲":     {"cat": "轻", "base_ac": 11, "dex_mode": "full", "str_req": None, "stealth_disadv": True,  "weight": 8,  "price_gp": 5},
    "皮甲":     {"cat": "轻", "base_ac": 11, "dex_mode": "full", "str_req": None, "stealth_disadv": False, "weight": 10, "price_gp": 10},
    "镶钉皮甲": {"cat": "轻", "base_ac": 12, "dex_mode": "full", "str_req": None, "stealth_disadv": False, "weight": 13, "price_gp": 45},
    # 中甲（穿5分钟/脱1分钟）
    "兽皮甲":   {"cat": "中", "base_ac": 12, "dex_mode": "cap2", "str_req": None, "stealth_disadv": False, "weight": 12, "price_gp": 10},
    "链甲衫":   {"cat": "中", "base_ac": 13, "dex_mode": "cap2", "str_req": None, "stealth_disadv": False, "weight": 20, "price_gp": 50},
    "鳞甲":     {"cat": "中", "base_ac": 14, "dex_mode": "cap2", "str_req": None, "stealth_disadv": True,  "weight": 45, "price_gp": 50},
    "胸甲":     {"cat": "中", "base_ac": 14, "dex_mode": "cap2", "str_req": None, "stealth_disadv": False, "weight": 20, "price_gp": 400},
    "半身板甲": {"cat": "中", "base_ac": 15, "dex_mode": "cap2", "str_req": None, "stealth_disadv": True,  "weight": 40, "price_gp": 750},
    # 重甲（穿10分钟/脱5分钟）
    "环甲":     {"cat": "重", "base_ac": 14, "dex_mode": "none", "str_req": None, "stealth_disadv": True,  "weight": 40, "price_gp": 30},
    "链甲":     {"cat": "重", "base_ac": 16, "dex_mode": "none", "str_req": 13,  "stealth_disadv": True,  "weight": 55, "price_gp": 75},
    "板条甲":   {"cat": "重", "base_ac": 17, "dex_mode": "none", "str_req": 15,  "stealth_disadv": True,  "weight": 60, "price_gp": 200},
    "板甲":     {"cat": "重", "base_ac": 18, "dex_mode": "none", "str_req": 15,  "stealth_disadv": True,  "weight": 65, "price_gp": 1500},
    # 盾牌（1动作穿/脱）
    "盾牌":     {"cat": "盾", "base_ac": 2,  "dex_mode": "bonus", "str_req": None, "stealth_disadv": False, "weight": 6,  "price_gp": 10},
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
# 武器表（2024版，38 件）
# 规则: R-ITM-012 武器表  出处: topics/玩家手册2024/装备/武器.htm
# dmg 形如 "1d8穿刺"；props 为词条列表；mastery 为精通词条
# ──────────────────────────────────────────────────────────────────────────
WEAPONS = {
    # 简易近战
    "短棒":   {"cat": "简易近战", "dmg": "1d4钝击",  "props": ["轻型"],                    "mastery": "缓速", "wt": 2,    "price": "1SP"},
    "匕首":   {"cat": "简易近战", "dmg": "1d4穿刺",  "props": ["灵巧", "轻型", "投掷"],     "mastery": "迅击", "wt": 1,    "price": "2GP"},
    "巨棒":   {"cat": "简易近战", "dmg": "1d8钝击",  "props": ["双手"],                    "mastery": "推离", "wt": 10,   "price": "2SP"},
    "手斧":   {"cat": "简易近战", "dmg": "1d6挥砍",  "props": ["轻型", "投掷"],             "mastery": "侵扰", "wt": 2,    "price": "5GP"},
    "标枪":   {"cat": "简易近战", "dmg": "1d6穿刺",  "props": ["投掷"],                    "mastery": "缓速", "wt": 2,    "price": "5SP"},
    "轻锤":   {"cat": "简易近战", "dmg": "1d4钝击",  "props": ["轻型", "投掷"],             "mastery": "迅击", "wt": 2,    "price": "2GP"},
    "硬头锤": {"cat": "简易近战", "dmg": "1d6钝击",  "props": [],                          "mastery": "削弱", "wt": 4,    "price": "5GP"},
    "长棍":   {"cat": "简易近战", "dmg": "1d6钝击",  "props": ["多用"],                    "mastery": "失衡", "wt": 4,    "price": "2SP"},
    "镰刀":   {"cat": "简易近战", "dmg": "1d4挥砍",  "props": ["轻型"],                    "mastery": "迅击", "wt": 2,    "price": "1GP"},
    "矛":     {"cat": "简易近战", "dmg": "1d6穿刺",  "props": ["投掷", "多用"],             "mastery": "削弱", "wt": 3,    "price": "1GP"},
    # 简易远程
    "飞镖":   {"cat": "简易远程", "dmg": "1d4穿刺",  "props": ["灵巧", "投掷"],             "mastery": "侵扰", "wt": 0.25, "price": "5CP"},
    "轻弩":   {"cat": "简易远程", "dmg": "1d8穿刺",  "props": ["弹药", "装填", "双手"],     "mastery": "缓速", "wt": 5,    "price": "25GP"},
    "短弓":   {"cat": "简易远程", "dmg": "1d6穿刺",  "props": ["弹药", "双手"],             "mastery": "侵扰", "wt": 2,    "price": "25GP"},
    "投石索": {"cat": "简易远程", "dmg": "1d4钝击",  "props": ["弹药"],                    "mastery": "缓速", "wt": None, "price": "1SP"},
    # 军用近战
    "战斧":   {"cat": "军用近战", "dmg": "1d8挥砍",  "props": ["多用"],                    "mastery": "失衡", "wt": 4,    "price": "10GP"},
    "链枷":   {"cat": "军用近战", "dmg": "1d8钝击",  "props": [],                          "mastery": "削弱", "wt": 2,    "price": "10GP"},
    "长柄刀": {"cat": "军用近战", "dmg": "1d10挥砍", "props": ["重型", "触及", "双手"],     "mastery": "擦掠", "wt": 6,    "price": "20GP"},
    "巨斧":   {"cat": "军用近战", "dmg": "1d12挥砍", "props": ["重型", "双手"],             "mastery": "横扫", "wt": 7,    "price": "30GP"},
    "巨剑":   {"cat": "军用近战", "dmg": "2d6挥砍",  "props": ["重型", "双手"],             "mastery": "擦掠", "wt": 6,    "price": "50GP"},
    "戟":     {"cat": "军用近战", "dmg": "1d10挥砍", "props": ["重型", "触及", "双手"],     "mastery": "横扫", "wt": 6,    "price": "20GP"},
    "骑枪":   {"cat": "军用近战", "dmg": "1d10穿刺", "props": ["重型", "触及", "双手"],     "mastery": "失衡", "wt": 6,    "price": "10GP"},
    "长剑":   {"cat": "军用近战", "dmg": "1d8挥砍",  "props": ["多用"],                    "mastery": "削弱", "wt": 3,    "price": "15GP"},
    "巨锤":   {"cat": "军用近战", "dmg": "2d6钝击",  "props": ["重型", "双手"],             "mastery": "失衡", "wt": 10,   "price": "10GP"},
    "钉头锤": {"cat": "军用近战", "dmg": "1d8穿刺",  "props": [],                          "mastery": "削弱", "wt": 4,    "price": "15GP"},
    "长矛":   {"cat": "军用近战", "dmg": "1d10穿刺", "props": ["重型", "触及", "双手"],     "mastery": "推离", "wt": 18,   "price": "5GP"},
    "刺剑":   {"cat": "军用近战", "dmg": "1d8穿刺",  "props": ["灵巧"],                    "mastery": "侵扰", "wt": 2,    "price": "25GP"},
    "弯刀":   {"cat": "军用近战", "dmg": "1d6挥砍",  "props": ["灵巧", "轻型"],             "mastery": "迅击", "wt": 3,    "price": "25GP"},
    "短剑":   {"cat": "军用近战", "dmg": "1d6穿刺",  "props": ["灵巧", "轻型"],             "mastery": "侵扰", "wt": 2,    "price": "10GP"},
    "三叉戟": {"cat": "军用近战", "dmg": "1d8穿刺",  "props": ["投掷", "多用"],             "mastery": "失衡", "wt": 4,    "price": "5GP"},
    "战镐":   {"cat": "军用近战", "dmg": "1d8穿刺",  "props": ["多用"],                    "mastery": "削弱", "wt": 2,    "price": "5GP"},
    "战锤":   {"cat": "军用近战", "dmg": "1d8钝击",  "props": ["多用"],                    "mastery": "推离", "wt": 2,    "price": "15GP"},
    "鞭":     {"cat": "军用近战", "dmg": "1d4挥砍",  "props": ["灵巧", "触及"],             "mastery": "缓速", "wt": 3,    "price": "2GP"},
    # 军用远程
    "吹箭筒": {"cat": "军用远程", "dmg": "1穿刺",    "props": ["弹药", "装填"],             "mastery": "侵扰", "wt": 1,    "price": "10GP"},
    "手弩":   {"cat": "军用远程", "dmg": "1d6穿刺",  "props": ["弹药", "轻型", "装填"],     "mastery": "侵扰", "wt": 3,    "price": "75GP"},
    "重弩":   {"cat": "军用远程", "dmg": "1d10穿刺", "props": ["弹药", "重型", "装填", "双手"], "mastery": "推离", "wt": 18, "price": "50GP"},
    "长弓":   {"cat": "军用远程", "dmg": "1d8穿刺",  "props": ["弹药", "重型", "双手"],     "mastery": "缓速", "wt": 2,    "price": "50GP"},
    "火铳":   {"cat": "军用远程", "dmg": "1d12穿刺", "props": ["弹药", "装填", "双手"],     "mastery": "缓速", "wt": 10,   "price": "500GP"},
    "手铳":   {"cat": "军用远程", "dmg": "1d10穿刺", "props": ["弹药", "装填"],             "mastery": "侵扰", "wt": 3,    "price": "250GP"},
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
# 冒险物品效果规则集（R-ADD-033）
# 规则: R-ADD-033 冒险物品效果规则集（扩充 R-ITM-042）
# 出处: topics/玩家手册2024/装备/冒险装备.htm ; topics/速查/DM速查/物品表.htm
# ──────────────────────────────────────────────────────────────────────────
ITEM_EFFECTS = {
    "抗毒剂": {"price": "50GP", "action": "附赠动作", "effect": "中毒豁免优势1小时", "excludes": ["不死", "构装"]},
    "链条": {"bind": "DC13 STR(运动)", "escape": "DC18 DEX(特技)", "break": "DC20 STR(运动)", "action": "操作动作", "hp": 10},
    "医疗包": {"price": "5GP", "uses": 10, "action": "操作动作", "effect": "稳定0HP生物,跳过DC10医药检定"},
    "捕猎陷阱": {"save": "DEX DC13", "dmg": "1d4穿刺", "effect": "速度0至下回合", "escape": "DC13 STR(运动)", "fail_dmg": "1穿刺"},
    "锁": {"pick": "DC15 DEX(巧手,需盗贼工具)"},
    "镣铐": {"bind": "DC13 DEX(巧手)", "escape": "DC20 DEX(巧手)", "break": "DC25 STR(运动)", "pick": "DC15 DEX(巧手)", "effect": "被铐者攻击劣势"},
    "绳索": {"knot": "DC10 DEX(巧手)", "break": "DC20 STR(运动)", "bind_escape": "DC15 DEX(特技)", "hp": 2},
    "爪钩": {"range": 50, "check": "DC13 DEX(特技)"},
    "便携式攻城锤": {"str_bonus": "+4", "assist": "优势"},
    "法术卷轴": {"requires": "法术在职业列表", "material": "无需", "save_dc": 13, "attack_bonus": 5, "destroyed_on_cast": True},
    "圣水": {"create_ritual": {"caster": "牧师/圣武士", "time": "1小时", "cost": "25GP银粉", "slot": "1环法术位"}},
    "燃油": {"fuel_duration": "6小时(油灯/提灯)"},
    "书籍": {"skills": ["奥秘", "历史", "自然", "宗教"], "bonus": "+5", "cond": "参考准确非虚构书"},
    "地图": {"skill": "求生", "bonus": "+5", "cond": "参考准确地图"},
    "火把": {"bright": 20, "dim": 20, "duration": "1小时", "melee_dmg": "1火焰"},
    "蜡烛": {"bright": 5, "dim": 5, "duration": "1小时"},
    "油灯": {"bright": 15, "dim": 30, "fuel": "6小时/品脱"},
    "牛眼提灯": {"bright": 60, "dim": 60, "shape": "锥", "fuel": "6小时/品脱"},
    "附盖提灯": {"bright": 30, "dim": 30, "fuel": "6小时/品脱", "cover_action": "附赠动作→5尺微光"},
}


def get_item_effect(item_id: str) -> dict:
    """查询冒险物品的效果规则（精确匹配+模糊匹配）。

    规则: R-ADD-033 冒险物品效果规则集（扩充 R-ITM-042）
    """
    if item_id in ITEM_EFFECTS:
        return ITEM_EFFECTS[item_id]
    for key in ITEM_EFFECTS:
        if key in item_id or item_id in key:
            return ITEM_EFFECTS[key]
    return {}


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
    print("[equipment] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
