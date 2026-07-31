"""骰子引擎 — D&D 5E 纯骰子与基础数值机制。

设计原则（ARCHITECTURE.md §2）：
  - 叙事交给 LLM，规则判定交给代码。本模块的所有掷骰/数值计算为确定性实现，
    LLM 不得绕过。
  - 随机源用 secrets（密码学随机，非伪随机）。
  - 每次掷骰返回详细结果（各骰、加值、总计），供上层记日志/审计。

标注约定：每条规则实现处标注 RULE_SPEC.md 的规则点 ID + 原文出处路径
（topics/.../xxx.htm），形成"代码↔规则"双向索引。代码写完后在
RULE_SPEC.md 末尾"实现回填区"补一行实际函数位置，闭合索引。

注：ability_modifier / proficiency_bonus 为基础数值查表，暂置于此模块，
    后续可拆到 engine/stats.py。
"""

from __future__ import annotations

import math
import re
import secrets
from dataclasses import dataclass, field

# ──────────────────────────────────────────────────────────────────────────
# 基础数值
# ──────────────────────────────────────────────────────────────────────────

def _randbelow(exclusive_upper: int) -> int:
    """密码学随机数，返回 [0, exclusive_upper)。"""
    return secrets.randbelow(exclusive_upper)


def roll_die(sides: int) -> int:
    """掷一颗 sides 面骰，返回 [1, sides]。

    规则: R-CHK-025 骰子标识 NdM，M∈{4,6,8,10,12,20}（d100/d3 为派生见下）
    出处: topics/玩家手册2024/进行游戏/骰子.htm
    """
    if sides < 1:
        raise ValueError(f"骰面数必须≥1，得到 {sides}")
    return 1 + _randbelow(sides)


def round_down(value: float) -> int:
    """向下取整：游戏中除法/乘法结果有小数则向下取整，即使小数>0.5。

    规则: R-GLS-005 向下取整
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    """
    return math.floor(value)


def ability_modifier(score: int) -> int:
    """属性调整值 = floor((score - 10) / 2)。

    对照表: 1→-5, 2-3→-4, ..., 10-11→0, ..., 20-21→+5, ..., 30→+10
    规则: R-CHK-024 属性调整值表与公式
    出处: topics/玩家手册2024/进行游戏/六项属性.htm
    """
    # R-CHK-023 属性值范围：玩家1-20，怪物最高30；此处不钳制，由调用方保证
    return round_down((score - 10) / 2)


# 熟练加值表（R-CHK-015），保留显式表便于核对，公式版见 proficiency_bonus
# 规则: R-CHK-015 熟练加值表  出处: topics/玩家手册2024/进行游戏/熟练.htm
_PROF_BONUS_TABLE = {
    range(1, 5): 2,    # 1-4 级/CR
    range(5, 9): 3,   # 5-8
    range(9, 13): 4,  # 9-12
    range(13, 17): 5, # 13-16
    range(17, 21): 6, # 17-20
    range(21, 25): 7, # 21-24
    range(25, 29): 8, # 25-28
    range(29, 31): 9, # 29-30
}


def proficiency_bonus(level_or_cr: float) -> int:
    """熟练加值随等级/CR 提升，从 +2 到 +9。

    规则: R-CHK-015 熟练加值表 / R-CHK-016 熟练加值不叠加（叠加由调用方保证只加一次）
    出处: topics/玩家手册2024/进行游戏/熟练.htm
    说明: CR 可为小数（0, 1/8, 1/4, 1/2），向下取整后归入对应档；≤4 一律 +2。
          等价公式: 2 + (max(1, floor(level_or_cr)) - 1) // 4。
    """
    lvl = max(1, math.floor(level_or_cr))
    for band, bonus in _PROF_BONUS_TABLE.items():
        if lvl in band:
            return bonus
    # >30 外推（类神）；按每4级+1继续
    if lvl >= 31:
        return 9 + (lvl - 29) // 4
    return 2  # 兜底（不应到达）


# ──────────────────────────────────────────────────────────────────────────
# 骰子表达式解析与掷骰
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class RollResult:
    """一次掷骰的完整结果。"""
    total: int                          # 最终总计
    rolls: list[int] = field(default_factory=list)  # 各骰明细（已含符号方向）
    expression: str = ""                # 原始表达式
    dice_rolls: list[int] = field(default_factory=list)  # 原始骰点（不含符号，便于重击回看）
    modifier: int = 0                   # 常数加/减值合计
    crit: bool = False                  # 是否重击加倍
    notes: str = ""                     # 附加说明（如 "advantage"）


# 解析词法：一个"项"= 可选符号 + (骰子 NdM | 整数)
# 规则: R-CHK-025 骰子标识与表达式（NdM+K，例 3d8+5）
# 出处: topics/玩家手册2024/进行游戏/骰子.htm
_TOKEN_RE = re.compile(r"([+-]?)(\d*[dD]\d+|\d+)")


def parse_dice_expression(expression: str) -> tuple[list[tuple[int, int, int]], int]:
    """解析骰子表达式 → (骰子项列表, 常数合计)。

    骰子项: (count, sides, sign)，sign∈{+1,-1}。
    支持: "3d8+5" "2d6" "1d20" "8d6" "d6"(隐式1) "1d4-1" "1d8+1d6+3" "1"(定值)。
    规则: R-CHK-025  出处: topics/玩家手册2024/进行游戏/骰子.htm
    """
    expr = expression.replace(" ", "").lower()
    terms: list[tuple[int, int, int]] = []
    constant = 0
    pos = 0
    for m in _TOKEN_RE.finditer(expr):
        if m.start() != pos:
            raise ValueError(f"无法解析表达式 {expression!r} 于位置 {pos}（{expr[pos:m.start()]!r}）")
        sign_str, tok = m.group(1), m.group(2)
        sign = -1 if sign_str == "-" else 1
        if "d" in tok:
            cnt_str, sides_str = tok.split("d")
            cnt = int(cnt_str) if cnt_str else 1  # R-CHK-025: NdM，N省略为1
            if cnt <= 0:
                # 0 颗骰的表达式（如 "0d6"）无意义，几乎总是上游 bug，显式拒绝
                raise ValueError(f"骰子数量必须 ≥1，得到 {expression!r}（{tok!r}）")
            sides = int(sides_str)
            if sides <= 0:
                raise ValueError(f"骰子面数必须 ≥1，得到 {expression!r}（{tok!r}）")
            terms.append((cnt, sides, sign))
        else:
            constant += sign * int(tok)
        pos = m.end()
    if pos != len(expr):
        raise ValueError(f"表达式 {expression!r} 末尾有未解析字符: {expr[pos:]!r}")
    return terms, constant


def roll_dice(expression: str, *, crit: bool = False) -> RollResult:
    """掷一个骰子表达式，返回 RollResult。

    规则: R-CHK-025 骰子标识与表达式（NdM+K，掷N颗M面骰相加再加常数）
    出处: topics/玩家手册2024/进行游戏/骰子.htm
    重击: crit=True 时伤害骰数量翻倍（常数不加倍）——
          规则: R-CMB-029 重击伤害骰翻倍
          出处: topics/玩家手册2024/进行游戏/重击.htm
    """
    terms, constant = parse_dice_expression(expression)
    all_rolls: list[int] = []   # 带符号方向的各骰贡献
    raw_rolls: list[int] = []  # 原始骰点
    subtotal = 0
    for count, sides, sign in terms:
        n = count * (2 if crit else 1)  # R-CMB-029 重击骰数翻倍
        for _ in range(n):
            r = roll_die(sides)
            raw_rolls.append(r)
            all_rolls.append(sign * r)
            subtotal += sign * r
    total = subtotal + constant
    return RollResult(
        total=total,
        rolls=all_rolls,
        expression=expression,
        dice_rolls=raw_rolls,
        modifier=constant,
        crit=crit,
    )


# ──────────────────────────────────────────────────────────────────────────
# d20 与优劣势
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class D20Roll:
    """一次 d20 掷骰结果（含优劣势信息）。"""
    used: int               # 实际采用的骰值
    rolls: list[int]        # 所有掷出的 d20
    mode: str               # "normal" | "advantage" | "disadvantage" | "cancelled"


def roll_d20(advantage: bool = False, disadvantage: bool = False) -> D20Roll:
    """掷 d20，处理优势/劣势。

    规则:
      - R-CHK-004 优势与劣势掷骰（优势掷两d20取高，劣势取低）
      - R-CHK-005 优势劣势不叠加与抵消（同时存在则抵消，只掷一d20）
    出处: topics/玩家手册2024/进行游戏/优势_劣势.htm
    """
    # R-CHK-005: 优劣势同时存在 → 抵消，按普通掷一骰
    if advantage and disadvantage:
        r = roll_die(20)
        return D20Roll(used=r, rolls=[r], mode="cancelled")
    if advantage:  # R-CHK-004: 优势取高
        a, b = roll_die(20), roll_die(20)
        return D20Roll(used=max(a, b), rolls=[a, b], mode="advantage")
    if disadvantage:  # R-CHK-004: 劣势取低
        a, b = roll_die(20), roll_die(20)
        return D20Roll(used=min(a, b), rolls=[a, b], mode="disadvantage")
    r = roll_die(20)
    return D20Roll(used=r, rolls=[r], mode="normal")


# ──────────────────────────────────────────────────────────────────────────
# 英雄气概（Heroic Inspiration）重掷
# ──────────────────────────────────────────────────────────────────────────

def reroll_d20(advantage: bool = False, disadvantage: bool = False) -> D20Roll:
    """英雄气概重掷：消耗英雄气概重新掷 d20（与原始掷骰相同的优劣势模式）。

    规则: 术语汇编/常见规则词汇.htm「英雄气概 Heroic Inspiration」
          「你可以消耗你的英雄气概来重掷你刚刚投掷的任何一颗 D20。
          你必须使用新的掷骰结果。」
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    说明: 调用方消耗灵感后调用本函数获取新骰值，必须使用新结果（不可选择保留旧值）。
    """
    return roll_d20(advantage=advantage, disadvantage=disadvantage)


# ──────────────────────────────────────────────────────────────────────────
# 派生骰：d100 / d3 / 百分比 / 随机表
# ──────────────────────────────────────────────────────────────────────────

def roll_d100() -> int:
    """百分骰 d100：两颗十面骰（十位+个位），两骰皆0则为100。

    规则: R-CHK-026 百分骰d100
    出处: topics/玩家手册2024/进行游戏/骰子.htm
    """
    tens = _randbelow(10) * 10   # 0,10,...,90
    ones = _randbelow(10)        # 0..9
    if tens == 0 and ones == 0:  # 两骰皆0 → 100
        return 100
    return tens + ones           # 00+5=5, 10+5=15, ..., 90+9=99


def roll_d3() -> int:
    """d3 = ceil(d6 / 2)（掷1d6除以2向上取整）。

    规则: R-CHK-027 D3骰换算
    出处: topics/玩家手册2024/进行游戏/骰子.htm
    """
    d6 = roll_die(6)
    return math.ceil(d6 / 2)


def roll_percent_chance(percent: int) -> tuple[bool, int]:
    """百分比概率判定：掷d100，结果≤百分比则事件发生。

    规则: R-CHK-029 百分比概率判定（例 5% → 01-05发生）
    出处: topics/玩家手册2024/进行游戏/骰子.htm
    """
    r = roll_d100()
    return (r <= percent, r)


def roll_random_table(table: dict, die_notation: str = "1d100") -> tuple[object, int]:
    """随机表掷骰查表：掷指定骰后按结果匹配行读取。

    table: {键: 结果}，键可为 int（精确匹配）或 (lo, hi) 元组（范围匹配）。
    规则: R-CHK-030 随机表掷骰查表
    出处: topics/玩家手册2024/进行游戏/骰子.htm
    """
    r = roll_dice(die_notation).total
    for key, value in table.items():
        if isinstance(key, tuple) and len(key) == 2:
            if key[0] <= r <= key[1]:
                return value, r
        elif key == r:
            return value, r
    raise ValueError(f"掷骰结果 {r} 不在表 {list(table)} 任何区间内")


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    """基本正确性自检（非穷尽）。"""
    # R-CHK-024 属性调整值
    assert ability_modifier(1) == -5
    assert ability_modifier(10) == 0
    assert ability_modifier(11) == 0
    assert ability_modifier(12) == 1
    assert ability_modifier(20) == 5
    assert ability_modifier(30) == 10
    # R-CHK-015 熟练加值
    assert proficiency_bonus(1) == 2 and proficiency_bonus(4) == 2
    assert proficiency_bonus(5) == 3 and proficiency_bonus(8) == 3
    assert proficiency_bonus(9) == 4 and proficiency_bonus(17) == 6
    assert proficiency_bonus(20) == 6 and proficiency_bonus(29) == 9 and proficiency_bonus(30) == 9
    assert proficiency_bonus(0.5) == 2  # CR 小数
    # R-CHK-025 表达式解析
    assert parse_dice_expression("3d8+5") == ([(3, 8, 1)], 5)
    assert parse_dice_expression("2d6") == ([(2, 6, 1)], 0)
    assert parse_dice_expression("d6") == ([(1, 6, 1)], 0)
    assert parse_dice_expression("1d4-1") == ([(1, 4, 1)], -1)
    assert parse_dice_expression("1d8+1d6+3") == ([(1, 8, 1), (1, 6, 1)], 3)
    assert parse_dice_expression("1") == ([], 1)  # 定值伤害
    # roll_dice 范围
    r = roll_dice("3d8+5")
    assert 8 <= r.total <= 29, r
    assert len(r.dice_rolls) == 3
    assert r.modifier == 5
    # 重击骰数翻倍（R-CMB-029）
    rc = roll_dice("1d6+3", crit=True)
    assert len(rc.dice_rolls) == 2 and rc.modifier == 3
    # d20 优劣势
    assert 1 <= roll_d20().used <= 20
    adv = roll_d20(advantage=True)
    assert len(adv.rolls) == 2 and adv.used == max(adv.rolls)
    dis = roll_d20(disadvantage=True)
    assert len(dis.rolls) == 2 and dis.used == min(dis.rolls)
    can = roll_d20(advantage=True, disadvantage=True)  # R-CHK-005 抵消
    assert len(can.rolls) == 1 and can.mode == "cancelled"
    # d100 / d3 / 百分比
    assert 1 <= roll_d100() <= 100
    assert roll_d3() in (1, 2, 3)
    ok, _ = roll_percent_chance(100)
    assert ok is True
    # 随机表
    tbl = {(1, 50): "A", (51, 100): "B"}
    res, _ = roll_random_table(tbl, "1d100")
    assert res in ("A", "B")
    print("[dice] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
