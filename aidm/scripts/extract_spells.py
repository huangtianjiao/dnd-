#!/usr/bin/env python
"""解析 玩家手册2024/法术详述/{0..9}环.htm 为结构化法术数据。

输出: src/aidm/data/spells_full.py — SPELLS_FULL dict（中文名 -> 法术条目）

页面结构（每个法术块）:
    中文名｜English Name
    学派 环阶或"戏法"（职业1、职业2） [、仪式]
    施法时间： / 施法距离： / 法术成分： / 持续时间：
    描述正文（多行，至下一个法术标题或文件尾）

推断字段（基于描述文本规则匹配，精度以人工精校表 SPELLS 为准）:
    effect_type / save_ability / damage_dice / damage_type / heal / concentration / ritual / upcast

用法: python scripts/extract_spells.py [源目录] [输出文件]
"""
from __future__ import annotations

import os
import re
import sys

SCHOOLS = ("防护", "咒法", "预言", "惑控", "塑能", "幻术", "死灵", "变化")

# 与引擎 engine/damage.py 的 DAMAGE_TYPES 保持一致（“寒冷”非“冷冻”）
DAMAGE_TYPES = ("强酸", "钝击", "寒冷", "火焰", "力场", "闪电", "暗蚀",
                "穿刺", "毒素", "心灵", "光耀", "挥砍", "雷鸣")

SAVE_ABILITIES = {"力量": "STR", "敏捷": "DEX", "体质": "CON",
                  "智力": "INT", "感知": "WIS", "魅力": "CHA"}

# 法术标题行：中文名｜English Name（全角竖线）
RE_TITLE = re.compile(r"^([^｜\n]{1,30})｜([A-Za-z][A-Za-z0-9 '\-\(\)/]+)$")
# 环阶行两种格式：0环页为「塑能 戏法（术士、法师）」（学派在前）；
# 1-9环页为「一环 防护（游侠、法师）」（环阶在前）
CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
          "六": 6, "七": 7, "八": 8, "九": 9}
RE_LEVEL = re.compile(
    r"^(?:(" + "|".join(SCHOOLS) + r")\s+)?"
    r"(戏法|[一二三四五六七八九]环)"
    r"(?:\s+(" + "|".join(SCHOOLS) + r"))?（([^）]+)）$")
RE_DMG = re.compile(r"(\d+d\d+(?:\s*[+＋]\s*\d+)?)点?(?:的)?(" + "|".join(DAMAGE_TYPES) + r")伤害")
RE_HEAL = re.compile(
    r"恢复[^。]{0,30}?(\d+d\d+(?:[+＋]\d+)?)[^。]{0,20}?点生命值"
    r"|(\d+d\d+)点生命值"
    r"|恢复量?(?:等同于|等于)(\d+d\d+)")
RE_UPCAST = re.compile(r"升环施法|使用更高环|更高一?环|戏法强化")
RE_UPCAST_DICE = re.compile(r"(?:伤害|治疗量)[^。]{0,10}?增加(\d+d\d+)")
RE_CANTRIP_SCALING = re.compile(r"5级（(\d+d\d+)）、11级（(\d+d\d+)）(?:以及|与|、)?17级（(\d+d\d+)）")
# 魔能爆型：5级两条射线、11级三条、17级四条
RE_BEAM_SCALING = re.compile(r"5级后[^。]{0,12}?两[条道](?:射线|束)[^。]{0,12}?11级后三[条道][^。]{0,12}?17级后四[条道]")
RE_HEAL_ADD_MOD = re.compile(r"\+你的?施法属性调整值")
RE_SAVE = re.compile(r"(力量|敏捷|体质|智力|感知|魅力)豁免")
RE_ATTACK = re.compile(r"(近战|远程)?法术攻击")
RE_GP = re.compile(r"价值(\d+(?:,\d{3})*)\s*(?:GP|gp|金币)")


def decode(path: str) -> str:
    raw = open(path, "rb").read()
    for enc in ("utf-8", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"无法解码 {path}")


def parse_page(path: str) -> list[dict]:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(decode(path), "lxml")
    for s in soup(["script", "style", "meta", "link", "noscript"]):
        s.decompose()
    text = (soup.body or soup).get_text("\n", strip=True)
    lines = [l for l in text.split("\n") if l.strip()]

    blocks: list[list[str]] = []
    cur: list[str] | None = None
    for l in lines:
        if RE_TITLE.match(l):
            if cur:
                blocks.append(cur)
            cur = [l]
        elif cur is not None:
            cur.append(l)
    if cur:
        blocks.append(cur)
    return [b for b in blocks if len(b) >= 8]


def parse_block(lines: list[str]) -> dict | None:
    m = RE_TITLE.match(lines[0])
    if not m:
        return None
    name_zh, name_en = m.group(1).strip(), m.group(2).strip()

    # 第二行应为 学派 环阶（职业）
    if len(lines) < 2:
        return None
    lm = RE_LEVEL.match(lines[1])
    if not lm:
        return None
    school_a, lv_txt, school_b, classes_txt = lm.groups()
    school = school_a or school_b or ""
    level = 0 if lv_txt == "戏法" else CN_NUM[lv_txt[0]]
    class_list = [c.strip() for c in re.split(r"[、，,]", classes_txt) if c.strip()]
    ritual = False

    # 固定字段（标签:值 相邻两行）
    fields: dict[str, str] = {}
    i = 2
    LABELS = ("施法时间：", "施法距离：", "法术成分：", "持续时间：")
    while i < len(lines):
        if lines[i] in LABELS and i + 1 < len(lines):
            fields[lines[i]] = lines[i + 1]
            i += 2
        else:
            break
    desc = "\n".join(lines[i:])
    # 压缩空白文本（供规则匹配，避免 HTML 断行切断词组）
    flat = re.sub(r"\s+", "", desc)

    casting_time = fields.get("施法时间：", "")
    # 仪式标记在施法时间字段（如「1 分钟或仪式」）
    ritual = ritual or "仪式" in casting_time
    if "附赠动作" in casting_time:
        ct_type = "BONUS_ACTION"
    elif "反应" in casting_time:
        ct_type = "REACTION"
    elif "动作" in casting_time:
        ct_type = "ACTION"
    else:
        ct_type = "TIME"

    comp_raw = fields.get("法术成分：", "")
    components = frozenset(c for c in "VSM" if re.search(rf"\b{c}\b", comp_raw))
    mat_desc = ""
    mm = re.search(r"M（([^）]+)）", comp_raw)
    if mm:
        mat_desc = mm.group(1)
    gp = RE_GP.search(comp_raw) or RE_GP.search(flat)
    mat_cost = float(gp.group(1).replace(",", "")) if gp else 0.0
    mat_consumed = bool(re.search(r"消耗|耗尽|化为灰烬", comp_raw)) and "M" in components

    duration = fields.get("持续时间：", "")
    concentration = "专注" in duration

    # 描述推断
    dmg = RE_DMG.search(flat)
    save = RE_SAVE.search(flat)
    atk = RE_ATTACK.search(flat)
    heal = RE_HEAL.search(flat)
    if atk:
        effect_type = "attack_roll"
    elif save:
        effect_type = "saving_throw"
    elif heal:
        effect_type = "heal"
    else:
        effect_type = "automatic"
    heal_dice = None
    if heal:
        heal_dice = (heal.group(1) or heal.group(2) or heal.group(3) or "").replace(" ", "") or None
    half = bool(re.search(r"豁免成功.{0,12}(?:一半|减半)", flat))

    # 升环结构推断：戏法随角色等级加骰 / 伤害与治疗升环加骰
    upcast = None
    cm = RE_CANTRIP_SCALING.search(flat)
    if cm:
        upcast = {"cantrip_scaling": [(5, cm.group(1)), (11, cm.group(2)), (17, cm.group(3))]}
    elif level == 0 and RE_BEAM_SCALING.search(flat):
        upcast = {"beam_scaling": [(5, 2), (11, 3), (17, 4)]}
    else:
        um = RE_UPCAST_DICE.search(flat)
        if um:
            upcast = {"per_level_above_base": "+" + um.group(1)}
    add_mod_heal = bool(heal_dice and RE_HEAL_ADD_MOD.search(flat))

    return {
        "name": name_zh,
        "en_name": name_en,
        "level": level,
        "school": school,
        "casting_time": casting_time,
        "casting_time_type": ct_type,
        "range": fields.get("施法距离：", ""),
        "components": sorted(components),
        "material_desc": mat_desc,
        "material_cost_gp": mat_cost,
        "material_consumed": mat_consumed,
        "duration": duration,
        "concentration": concentration,
        "ritual": ritual,
        "effect_type": effect_type,
        "save_ability": SAVE_ABILITIES.get(save.group(1)) if save else None,
        "damage_dice": dmg.group(1).replace(" ", "") if dmg else None,
        "damage_type": dmg.group(2) if dmg else None,
        "half_on_save": half,
        "heal_dice": heal_dice,
        "add_mod_heal": add_mod_heal,
        "upcast": upcast,
        "upcast_note": bool(RE_UPCAST.search(flat)),
        "description": desc,
        "class_list": class_list,
    }


def py_repr(value) -> str:
    return repr(value)


def main() -> None:
    src = sys.argv[1] if len(sys.argv) > 1 else r"d:\game\dnd\5echm_web\topics\玩家手册2024\法术详述"
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(__file__), "..", "src", "aidm", "data", "spells_full.py")
    dst = os.path.abspath(dst)

    spells: dict[str, dict] = {}
    dup: list[str] = []
    for n in range(10):
        path = os.path.join(src, f"{n}环.htm")
        if not os.path.exists(path):
            print(f"!! 缺页 {path}")
            continue
        for block in parse_page(path):
            sp = parse_block(block)
            if sp is None:
                continue
            if sp["name"] in spells:
                dup.append(sp["name"])
            spells[sp["name"]] = sp

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write('"""法术全量数据表 — 由 scripts/extract_spells.py 自动解析生成，请勿手改。\n\n')
        f.write("数据来源: topics/玩家手册2024/法术详述/{0..9}环.htm（逐页解析）\n")
        f.write("字段推断说明: effect_type/save_ability/damage 由描述文本规则匹配，\n")
        f.write("精度以 spells.py 中人工精校的 SPELLS 表为准；本表提供全量覆盖兜底。\n")
        f.write('"""\n\n')
        f.write("SPELLS_FULL: dict[str, dict] = {\n")
        for name in sorted(spells, key=lambda k: (spells[k]["level"], k)):
            f.write(f"    {name!r}: {py_repr(spells[name])},\n")
        f.write("}\n")
    lv_count: dict[int, int] = {}
    for sp in spells.values():
        lv_count[sp["level"]] = lv_count.get(sp["level"], 0) + 1
    print(f"解析 {len(spells)} 个法术 -> {dst}")
    print("环阶分布:", {k: lv_count[k] for k in sorted(lv_count)})
    if dup:
        print("重名（已覆盖）:", dup)


if __name__ == "__main__":
    main()
