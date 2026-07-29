#!/usr/bin/env python
"""解析 怪物图鉴2025（新版块）+ 怪物图鉴2014（旧版块）为结构化怪物数据。

输出: src/aidm/data/monsters_full.py — MONSTERS_FULL dict（中文名 -> 怪物条目）

2025 版块格式（每怪一页）:
    巨魔Troll
    大型巨人，混乱邪恶
    AC 15 / 先攻 +1（11）/ HP 94（9d10+45）/ 速度 30尺
    六维表 / 技能 / 感官 / 语言 / CR 5（XP1,800；PB+3）
    特质Traits ... 动作Actions ... 近战攻击检定：+7，触及10尺。命中：11（2d6+4）挥砍伤害。

2014 版块格式（类人生物等旧页）:
    小型类人（类地精），中立邪恶
    护甲等级：15（皮甲，盾牌） 生命值：7（2d6） 速度：30尺
    挑战等级：1/4（50 XP）
    近战武器攻击：命中+4，触及5尺，单一目标。命中：5（1d6+2）点挥砍伤害。

用法: python scripts/extract_monsters.py [输出文件]
"""
from __future__ import annotations

import os
import re
import sys

MM2025 = r"d:\game\dnd\5echm_web\topics\怪物图鉴2025"
MM2014 = r"d:\game\dnd\5echm_web\topics\怪物图鉴"

# 2025 跳过的页面（总述/前言/附录）
SKIP_2025 = ("总.htm", "前言", "附录B")

# 2014 补充表：文件名 -> 标准中文名（2025 未收录的常用怪）
MM2014_EXTRA = {
    r"类人生物\地精.html": "哥布林",
    r"类人生物\兽人.html": "兽人",
    r"类人生物\大地精.html": "霍布哥布林",
}

# 2025 别名：常用名 -> 2025 实际版块名（2025 将基础怪改为“武者”版块）
ALIAS_2025 = {
    "熊地精": "熊地精武者",
    "狗头人": "狗头人武者",
}

DAMAGE_TYPES = ("强酸", "钝击", "寒冷", "火焰", "力场", "闪电", "暗蚀",
                "穿刺", "毒素", "心灵", "光耀", "挥砍", "雷鸣")
CREATURE_TYPES = ("亡灵", "元素", "天族", "妖精", "巨人", "异怪", "怪兽",
                  "构装", "植物", "泥怪", "类人", "邪魔", "龙类", "野兽",
                  "不死", "龙", "泥形", "天界", "精类")
SIZES = ("微型", "超小型", "小型", "中型", "大型", "巨型", "超巨型")

# ── 新版块（2025）正则，作用于压缩空白后的 flat 文本 ──
RE25_AC = re.compile(r"AC(\d+)")
RE25_HP = re.compile(r"HP(\d+)")
RE25_SPEED = re.compile(r"速度(\d+)尺")
RE25_CR = re.compile(r"CR(\d+(?:/\d+)?)（")
RE25_DEX = re.compile(r"敏捷\d+([+-]\d+)[+-]\d+")
RE25_ATK = re.compile(r"(?:近战|远程)攻击检定：\+(\d+)")
RE25_DMG = re.compile(r"命中：\d+（(\d+d\d+(?:[+-]\d+)?)）(" + "|".join(DAMAGE_TYPES) + r")伤害")

# ── 旧版块（2014）正则 ──
RE14_AC = re.compile(r"护甲等级：(\d+)")
RE14_HP = re.compile(r"生命值：(\d+)")
RE14_SPEED = re.compile(r"速度：(\d+)尺")
RE14_CR = re.compile(r"挑战等级：(\d+(?:/\d+)?)（")
RE14_DEX = re.compile(r"敏捷\d+（([+-]\d+)）")
RE14_ATK = re.compile(r"(?:近战|远程)武器攻击：命中\+(\d+)")
RE14_DMG = re.compile(r"命中：\d+（(\d+d\d+(?:[+-]\d+)?)）点?(" + "|".join(DAMAGE_TYPES) + r")伤害")

RE_NAME_2025 = re.compile(r"^([一-鿿（）·]{1,12}?)\s*[A-Z][A-Za-z '\-’]*$")
RE_HEAD = re.compile(
    r"^(" + "|".join(SIZES) + r")(?:或(?:" + "|".join(SIZES) + r"))?"
    r"(" + "|".join(CREATURE_TYPES) + r")")


def decode(path: str) -> str:
    raw = open(path, "rb").read()
    for enc in ("utf-8", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return ""


def cr_value(txt: str) -> float:
    if "/" in txt:
        a, b = txt.split("/", 1)
        try:
            return round(int(a) / int(b), 3)
        except (ValueError, ZeroDivisionError):
            return 0.0
    return float(txt)


def parse_2025(path: str) -> dict | None:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(decode(path), "lxml")
    for s in soup(["script", "style", "meta", "link", "noscript"]):
        s.decompose()
    text = (soup.body or soup).get_text("\n", strip=True)
    lines = [l for l in text.split("\n") if l.strip()]
    if len(lines) < 20:
        return None
    flat = re.sub(r"\s+", "", text)

    # 定位 stat block 头：「中文English」行 + 下一行「体型类型[（注释）]，阵营」
    # （lore 段落长短不一，巫妖等页版块头在行 50+，故全文扫描）
    name = None
    size, ctype = "中型", "类人"
    for i, l in enumerate(lines):
        nm = RE_NAME_2025.match(l.strip())
        if nm and i + 1 < len(lines):
            hm = RE_HEAD.match(lines[i + 1].strip())
            if hm:
                name = nm.group(1)
                size, ctype = hm.group(1), hm.group(2)
                break
    if name is None:
        return None

    ac = RE25_AC.search(flat)
    hp = RE25_HP.search(flat)
    cr = RE25_CR.search(flat)
    if not (ac and hp and cr):
        return None
    dex = RE25_DEX.search(flat)
    spd = RE25_SPEED.search(flat)
    atk = RE25_ATK.search(flat)
    dmg = RE25_DMG.search(flat)
    # 感官行
    senses = ""
    for i, l in enumerate(lines):
        if l == "感官" and i + 1 < len(lines):
            senses = lines[i + 1]
            break
    return {
        "name": name,
        "cr": cr_value(cr.group(1)),
        "hp": int(hp.group(1)),
        "ac": int(ac.group(1)),
        "dex_mod": int(dex.group(1)) if dex else 0,
        "attack_bonus": int(atk.group(1)) if atk else 0,
        "damage_dice": dmg.group(1).replace(" ", "") if dmg else "1d6",
        "damage_type": dmg.group(2) if dmg else "钝击",
        "speed": int(spd.group(1)) if spd else 30,
        "senses": senses,
        "creature_type": ctype,
        "size": size,
        "source": "怪物图鉴2025",
    }


def parse_2014(path: str, name: str) -> dict | None:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(decode(path), "lxml")
    for s in soup(["script", "style", "meta", "link", "noscript"]):
        s.decompose()
    text = (soup.body or soup).get_text("\n", strip=True)
    flat = re.sub(r"\s+", "", text)

    ac = RE14_AC.search(flat)
    hp = RE14_HP.search(flat)
    cr = RE14_CR.search(flat)
    if not (ac and hp and cr):
        return None
    dex = RE14_DEX.search(flat)
    spd = RE14_SPEED.search(flat)
    atk = RE14_ATK.search(flat)
    dmg = RE14_DMG.search(flat)
    # 体型+类型：找「小型类人（类地精），中立邪恶」式样行
    size, ctype = "中型", "类人"
    for l in [x for x in text.split("\n") if x.strip()]:
        hm = RE_HEAD.match(l.strip())
        if hm and "，" in l:
            size, ctype = hm.group(1), hm.group(2)
            break
    senses = ""
    sm = re.search(r"感官：([^语]{1,40})", flat)
    if sm:
        senses = sm.group(1).rstrip("，；")
    return {
        "name": name,
        "cr": cr_value(cr.group(1)),
        "hp": int(hp.group(1)),
        "ac": int(ac.group(1)),
        "dex_mod": int(dex.group(1)) if dex else 0,
        "attack_bonus": int(atk.group(1)) if atk else 0,
        "damage_dice": dmg.group(1).replace(" ", "") if dmg else "1d6",
        "damage_type": dmg.group(2) if dmg else "挥砍",
        "speed": int(spd.group(1)) if spd else 30,
        "senses": senses,
        "creature_type": ctype,
        "size": size,
        "source": "怪物图鉴2014",
    }


def main() -> None:
    dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), "..", "src", "aidm", "data", "monsters_full.py")
    dst = os.path.abspath(dst)

    monsters: dict[str, dict] = {}
    fail: list[str] = []

    # ── 2025 全量 ──
    for dirpath, _dirs, files in os.walk(MM2025):
        for fn in sorted(files):
            if not fn.endswith(".htm"):
                continue
            if any(k in fn for k in SKIP_2025):
                continue
            path = os.path.join(dirpath, fn)
            try:
                m = parse_2025(path)
            except Exception as e:  # noqa: BLE001
                print(f"!! 解析异常 {fn}: {e}")
                m = None
            if m is None:
                fail.append(fn)
                continue
            if m["name"] in monsters:
                continue  # 同名保留先见（类型目录序优先）
            monsters[m["name"]] = m

    # ── 2025 别名回填（熊地精→熊地精武者 等）──
    for alias, real in ALIAS_2025.items():
        if alias not in monsters and real in monsters:
            monsters[alias] = monsters[real]

    # ── 2014 补充（2025 未收录的常用怪）──
    for rel, std_name in MM2014_EXTRA.items():
        if std_name in monsters:
            continue
        path = os.path.join(MM2014, rel)
        if not os.path.exists(path):
            print(f"!! 2014 缺页 {rel}")
            continue
        m = parse_2014(path, std_name)
        if m:
            monsters[std_name] = m
        else:
            print(f"!! 2014 解析失败 {rel}")

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write('"""怪物全量数据表 — 由 scripts/extract_monsters.py 自动解析生成，请勿手改。\n\n')
        f.write("数据来源: topics/怪物图鉴2025/**.htm（新版块全量）\n")
        f.write("          topics/怪物图鉴/类人生物/{地精,兽人,大地精}.html（2014 补充）\n")
        f.write("说明: attack_bonus/damage_dice 取该怪第一个攻击动作；多动作怪以人工精校表为准。\n")
        f.write('"""\n\n')
        f.write("MONSTERS_FULL: dict[str, dict] = {\n")
        for name in sorted(monsters, key=lambda k: (monsters[k]["cr"], k)):
            f.write(f"    {name!r}: {monsters[name]!r},\n")
        f.write("}\n")

    print(f"解析 {len(monsters)} 个怪物 -> {dst}")
    cr_lo = sum(1 for m in monsters.values() if m["cr"] <= 1)
    print(f"CR<=1 低阶怪: {cr_lo}")
    if fail:
        print(f"未解析页面 {len(fail)} 个（多为总述/无版块页）:", fail[:8])


if __name__ == "__main__":
    main()
