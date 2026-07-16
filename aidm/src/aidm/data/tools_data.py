"""工具数据 — PHB 2024 第六章。

来源: 玩家手册2024/装备/工匠工具.htm + 其他工具.htm
提供: 15种工匠工具 + 6种其他工具（属性、操作、制造）
"""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Tool:
    """工具数据模型。"""
    name: str
    name_en: str
    category: str           # "工匠工具", "其他工具"
    ability: str            # 主要属性: STR/DEX/CON/INT/WIS/CHA
    price_gp: float
    weight_lb: float
    operations: str         # 操作动作描述
    crafts: str = ""        # 可制造的物品列表
    variants: str = ""      # 变体（多类工具）


TOOLS: dict[str, Tool] = {}
TOOLS_EN: dict[str, Tool] = {}

def _reg(t: Tool):
    TOOLS[t.name] = t
    TOOLS_EN[t.name_en.lower()] = t


# ═══════════════════════════════════════════════════════════════════════════
# 工匠工具 (PHB 2024)
# ═══════════════════════════════════════════════════════════════════════════

_reg(Tool("炼金工具", "Alchemist's Supplies", "工匠工具", "INT", 50, 8,
    operations="辨析一种物质(DC15)，生起一场火(DC15)",
    crafts="强酸、炽火胶、材料包、燃油、纸张、香水"))

_reg(Tool("酿酒工具", "Brewer's Supplies", "工匠工具", "INT", 20, 9,
    operations="检测饮品是否下毒(DC15)，辨识酒精(DC10)",
    crafts="抗毒剂"))

_reg(Tool("书法工具", "Calligrapher's Supplies", "工匠工具", "DEX", 10, 5,
    operations="以华丽字迹撰写文字防止造假(DC15)",
    crafts="墨水、法术卷轴"))

_reg(Tool("木匠工具", "Carpenter's Tools", "工匠工具", "STR", 8, 6,
    operations="封死或撬开门/容器(DC20)",
    crafts="短棒、巨棒、长棍、木桶、箱子、梯子、长杆、便携式攻城锤、火把"))

_reg(Tool("制图工具", "Cartographer's Tools", "工匠工具", "WIS", 15, 6,
    operations="为一小片区域绘制地图(DC15)",
    crafts="地图"))

_reg(Tool("鞋匠工具", "Cobbler's Tools", "工匠工具", "DEX", 5, 5,
    operations="改造足具来为下一次敏捷(特技)检定提供优势(DC10)",
    crafts="攀爬工具"))

_reg(Tool("厨师工具", "Cook's Utensils", "工匠工具", "WIS", 1, 8,
    operations="改善食物风味(DC10)，检查食物是否腐坏或有毒(DC15)",
    crafts="口粮"))

_reg(Tool("玻璃匠工具", "Glassblower's Tools", "工匠工具", "INT", 30, 5,
    operations="判断玻璃物件在过去24小时内盛过什么内容物(DC15)",
    crafts="玻璃瓶、放大镜、望远镜、小瓶"))

_reg(Tool("珠宝匠工具", "Jeweler's Tools", "工匠工具", "INT", 25, 2,
    operations="判断珠宝价值(DC15)",
    crafts="奥术法器、圣徽"))

_reg(Tool("皮匠工具", "Leatherworker's Tools", "工匠工具", "DEX", 5, 5,
    operations="对皮制品进行图案设计(DC10)",
    crafts="投石索、鞭子、兽皮甲、皮甲、镶钉皮甲、背包、弩矢匣、地图/卷轴匣、羊皮纸、小包、箭袋、水袋"))

_reg(Tool("石匠工具", "Mason's Tools", "工匠工具", "STR", 10, 8,
    operations="在石头上凿出符号标志或洞(DC10)",
    crafts="滑轮组"))

_reg(Tool("画家工具", "Painter's Supplies", "工匠工具", "WIS", 10, 5,
    operations="画出你见过的某个事物的可辨图像(DC10)",
    crafts="德鲁伊法器、圣徽"))

_reg(Tool("陶匠工具", "Potter's Tools", "工匠工具", "INT", 10, 3,
    operations="判断陶瓷物件在过去24小时内盛过什么内容物(DC15)",
    crafts="壶、灯"))

_reg(Tool("铁匠工具", "Smith's Tools", "工匠工具", "STR", 20, 8,
    operations="撬开门或容器(DC20)",
    crafts="任意近战武器(除短棒/巨棒/长棍/鞭子)、中甲(除兽皮甲)、重甲、滚珠、吊桶、铁蒺藜、链条、撬棍、枪械子弹、爪钩、铁壶、铁钉、投石索子弹"))

_reg(Tool("修补工具", "Tinker's Tools", "工匠工具", "DEX", 50, 10,
    operations="用废料组装微型物品(1分钟后散架)(DC20)",
    crafts="火铳、手铳、铃铛、牛眼提灯、扁瓶、附盖提灯、捕猎陷阱、锁、镣铐、镜子、铲子、信号笛、火绒盒"))

_reg(Tool("织布工具", "Weaver's Tools", "工匠工具", "DEX", 1, 5,
    operations="修补衣服破口(DC10)，缝制微型图案(DC10)",
    crafts="布甲、篮子、铺盖、毯子、高档服装、捕网、长袍、绳索、麻袋、细绳、帐篷、旅行服装"))

_reg(Tool("木雕工具", "Woodcarver's Tools", "工匠工具", "DEX", 1, 5,
    operations="在木头上雕刻图案(DC10)",
    crafts="短棒、巨棒、长棍、远程武器(除手铳/火铳/投石索)、奥术法器、箭矢、弩矢、德鲁伊法器、墨水笔、吹矢"))


# ═══════════════════════════════════════════════════════════════════════════
# 其他工具 (PHB 2024)
# ═══════════════════════════════════════════════════════════════════════════

_reg(Tool("易容工具", "Disguise Kit", "其他工具", "CHA", 25, 3,
    operations="化妆(DC10)",
    crafts="戏服"))

_reg(Tool("文书伪造工具", "Forgery Kit", "其他工具", "DEX", 15, 5,
    operations="模仿他人笔迹至多10词(DC15)，伪造火漆(DC20)"))

_reg(Tool("赌具", "Gaming Set", "其他工具", "WIS", 0, 0,
    operations="判断作弊(DC10)，赢取游戏(DC20)",
    variants="骰子(1SP)、龙棋(1GP)、纸牌(5SP)、三龙牌(1GP)"))

_reg(Tool("草药工具", "Herbalism Kit", "其他工具", "INT", 5, 3,
    operations="辨认植物(DC10)",
    crafts="抗毒剂、蜡烛、医疗包、治疗药水"))

_reg(Tool("乐器", "Musical Instrument", "其他工具", "CHA", 0, 0,
    operations="演奏熟知曲调(DC10)，即兴乐曲(DC15)",
    variants="风笛(30GP,6磅)、鼓(6GP,3磅)、扬琴(25GP,10磅)、长笛(2GP,1磅)、号角(3GP,2磅)、鲁特琴(35GP,2磅)、里拉琴(30GP,2磅)、排箫(12GP,2磅)、芦笛(2GP,1磅)、提琴(30GP,1磅)"))

_reg(Tool("领航工具", "Navigator's Tools", "其他工具", "WIS", 25, 2,
    operations="计划路线(DC10)，观星判断位置(DC15)"))

_reg(Tool("毒药工具", "Poisoner's Kit", "其他工具", "INT", 50, 2,
    operations="侦测有毒物件(DC10)",
    crafts="基础毒药"))

_reg(Tool("盗贼工具", "Thieves' Tools", "其他工具", "DEX", 25, 1,
    operations="撬锁(DC15)，解除陷阱(DC15)"))


# ═══════════════════════════════════════════════════════════════════════════
# 查询函数
# ═══════════════════════════════════════════════════════════════════════════

def get_tool(name: str) -> Optional[Tool]:
    return TOOLS.get(name) or TOOLS_EN.get(name.lower())

def tools_by_category(category: str) -> list[Tool]:
    return [t for t in TOOLS.values() if t.category == category]

def tools_by_ability(ability: str) -> list[Tool]:
    return [t for t in TOOLS.values() if t.ability.upper() == ability.upper()]

def craftable_items(tool_name: str) -> list[str]:
    """获取某工具可制造的物品列表。"""
    t = get_tool(tool_name)
    if t and t.crafts:
        return [x.strip() for x in t.crafts.replace("、", ",").split(",")]
    return []


# ═══════════════════════════════════════════════════════════════════════════
# 自检
# ═══════════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    artisans = tools_by_category("工匠工具")
    assert len(artisans) == 17, f"工匠工具应为17, 实有{len(artisans)}"

    others = tools_by_category("其他工具")
    assert len(others) >= 6, f"其他工具不足: {len(others)}"

    # 盗贼工具
    tt = get_tool("盗贼工具")
    assert tt is not None and tt.ability == "DEX"

    # 炼金工具可制造
    alch = get_tool("炼金工具")
    assert "强酸" in alch.crafts

    # 英文查询
    assert get_tool("thieves' tools") is not None

    print(f"[tools_data] 自检通过 ✓ ({len(artisans)}工匠工具 + {len(others)}其他工具)")


if __name__ == "__main__":
    _self_test()
