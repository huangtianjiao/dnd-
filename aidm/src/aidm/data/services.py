"""服务与开销数据 — PHB 2024 第六章。

来源: 玩家手册2024/装备/服务.htm
提供: 生活方式、饮食住宿、旅行、雇工、施法服务价格
"""

from dataclasses import dataclass
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════
# 生活方式 (Lifestyle)
# ═══════════════════════════════════════════════════════════════════════════

LIFESTYLES = {
    "乞食":     {"name_en": "Wretched",      "cost_day": 0,      "cost_month": 0,       "desc": "仅依靠运气和施舍生存，露宿街头。"},
    "流浪":     {"name_en": "Squalid",       "cost_day": 0.1,    "cost_month": 3,       "desc": "最低限度购置必需品，健康堪忧。"},
    "穷困":     {"name_en": "Poor",          "cost_day": 0.2,    "cost_month": 6,       "desc": "节约地为自己购置必需品。"},
    "俭朴":     {"name_en": "Modest",        "cost_day": 1,      "cost_month": 30,      "desc": "为自己提供平均水平的生活。"},
    "舒适":     {"name_en": "Comfortable",   "cost_day": 2,      "cost_month": 60,      "desc": "较为宽松地购置必需品，偶尔享乐。"},
    "富裕":     {"name_en": "Wealthy",       "cost_day": 4,      "cost_month": 120,     "desc": "习惯了优越的生活，或许还有仆人。"},
    "奢华":     {"name_en": "Aristocratic",  "cost_day": 10,     "cost_month": 300,     "desc": "生活各方面都追求最好，可能雇佣了一队人。"},
}


# ═══════════════════════════════════════════════════════════════════════════
# 饮食与住宿 (Food, Drink, and Lodging)
# ═══════════════════════════════════════════════════════════════════════════

FOOD_DRINK = {
    "麦酒(马克杯)":     {"name_en": "Ale (mug)",        "price_gp": 0.04},
    "面包(一块)":       {"name_en": "Bread (loaf)",     "price_gp": 0.02},
    "奶酪(一角)":       {"name_en": "Cheese (hunk)",    "price_gp": 0.10},
    "普通红酒(瓶装)":   {"name_en": "Wine, Common",     "price_gp": 0.20},
    "优质红酒(瓶装)":   {"name_en": "Wine, Fine",       "price_gp": 10},
}

LODGING = {
    "流浪旅馆": {"name_en": "Inn Stay (Squalid)",     "price_gp": 0.07},
    "穷困旅馆": {"name_en": "Inn Stay (Poor)",        "price_gp": 0.10},
    "俭朴旅馆": {"name_en": "Inn Stay (Modest)",      "price_gp": 0.50},
    "舒适旅馆": {"name_en": "Inn Stay (Comfortable)", "price_gp": 0.80},
    "富裕旅馆": {"name_en": "Inn Stay (Wealthy)",     "price_gp": 2},
    "奢华旅馆": {"name_en": "Inn Stay (Aristocratic)","price_gp": 4},
}

MEALS = {
    "流浪餐": {"name_en": "Meal (Squalid)",      "price_gp": 0.01},
    "穷困餐": {"name_en": "Meal (Poor)",         "price_gp": 0.02},
    "俭朴餐": {"name_en": "Meal (Modest)",       "price_gp": 0.10},
    "舒适餐": {"name_en": "Meal (Comfortable)",  "price_gp": 0.20},
    "富裕餐": {"name_en": "Meal (Wealthy)",      "price_gp": 0.30},
    "奢华餐": {"name_en": "Meal (Aristocratic)", "price_gp": 0.60},
}

STABLING = {"name_en": "Stabling (per day)", "price_gp": 0.50}
FEED = {"name_en": "Feed (per day)", "price_gp": 0.05}


# ═══════════════════════════════════════════════════════════════════════════
# 旅行 (Travel)
# ═══════════════════════════════════════════════════════════════════════════

TRAVEL = {
    "城际旅程":     {"name_en": "Coach ride between towns", "price": "每里3CP"},
    "城内旅程":     {"name_en": "Coach ride within a city", "price": "每里1CP"},
    "道路或关卡费": {"name_en": "Road or gate toll",        "price": "1CP"},
    "船运费":       {"name_en": "Ship's passage",           "price": "每里1SP"},
}


# ═══════════════════════════════════════════════════════════════════════════
# 雇工 (Hirelings)
# ═══════════════════════════════════════════════════════════════════════════

HIRELINGS = {
    "熟练雇工": {"name_en": "Skilled hireling",    "price": "每日2GP"},
    "新手雇工": {"name_en": "Untrained hireling",  "price": "每日2SP"},
    "信使":     {"name_en": "Messenger",           "price": "每里2CP"},
}


# ═══════════════════════════════════════════════════════════════════════════
# 施法服务 (Spellcasting Services)
# ═══════════════════════════════════════════════════════════════════════════

SPELLCASTING_SERVICES = {
    0:  {"level_name": "戏法",     "price_gp": 30,      "available": "村庄、城镇或城市"},
    1:  {"level_name": "一环",     "price_gp": 50,      "available": "村庄、城镇或城市"},
    2:  {"level_name": "二环",     "price_gp": 200,     "available": "村庄、城镇或城市"},
    3:  {"level_name": "三环",     "price_gp": 300,     "available": "仅城镇或城市"},
    4:  {"level_name": "四到五环", "price_gp": 2000,    "available": "仅城镇或城市"},
    6:  {"level_name": "六到八环", "price_gp": 20000,   "available": "仅城市"},
    9:  {"level_name": "九环",     "price_gp": 100000,  "available": "仅城市"},
}


# ═══════════════════════════════════════════════════════════════════════════
# 查询函数
# ═══════════════════════════════════════════════════════════════════════════

def get_lifestyle(name: str) -> Optional[dict]:
    return LIFESTYLES.get(name)

def get_lifestyle_cost(name: str, period: str = "day") -> float:
    """获取某生活方式的开销。period: 'day' 或 'month'。"""
    ls = LIFESTYLES.get(name)
    if not ls:
        return 0
    return ls["cost_month"] if period == "month" else ls["cost_day"]

def get_spellcasting_price(level: int) -> dict:
    """获取施法服务价格。返回 {price_gp, available, level_name}。"""
    if level >= 9:
        return SPELLCASTING_SERVICES[9]
    if level >= 6:
        return SPELLCASTING_SERVICES[6]
    if level >= 4:
        return SPELLCASTING_SERVICES[4]
    return SPELLCASTING_SERVICES.get(level, SPELLCASTING_SERVICES[0])

def is_spellcasting_available(level: int, settlement: str) -> bool:
    """判断在给定聚落中是否可购买施法服务。settlement: 'village', 'town', 'city'."""
    info = get_spellcasting_price(level)
    required = info["available"]
    if settlement == "city" or settlement == "城市":
        return True
    if settlement == "town" or settlement == "城镇":
        return "城镇" in required or "村庄" in required
    if settlement == "village" or settlement == "村庄":
        return "村庄" in required
    return False


# ═══════════════════════════════════════════════════════════════════════════
# 自检
# ═══════════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    assert len(LIFESTYLES) == 7, f"生活方式应为7, 实有{len(LIFESTYLES)}"
    assert len(SPELLCASTING_SERVICES) == 7
    assert len(HIRELINGS) == 3

    # 俭朴生活 1GP/天
    assert get_lifestyle_cost("俭朴", "day") == 1
    assert get_lifestyle_cost("俭朴", "month") == 30

    # 3环法术300GP
    info3 = get_spellcasting_price(3)
    assert info3["price_gp"] == 300

    # 9环在城市可用
    assert is_spellcasting_available(9, "城市") is True
    assert is_spellcasting_available(9, "村庄") is False

    print(f"[services] 自检通过 ✓ ({len(LIFESTYLES)}生活方式 + {len(FOOD_DRINK)+len(LODGING)+len(MEALS)}饮食住宿 + {len(SPELLCASTING_SERVICES)}施法价位)")


if __name__ == "__main__":
    _self_test()
