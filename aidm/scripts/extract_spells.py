"""从 5echm_web HTML 提取全部法术数据并生成 spells.py 数据块。

用法：从项目根目录运行
    cd E:/Project/dnd--master
    python aidm/scripts/extract_spells.py

输出：aidm/src/aidm/data/_spells_data.py（自动生成的法术数据）
"""
from __future__ import annotations

import html as html_mod
import os
import re
import sys
from dataclasses import asdict
from typing import Optional

# ---- 配置 ----
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WEB_SPELLS_DIR = os.path.join(BASE_DIR, "5echm_web", "topics", "玩家手册2024", "法术详述")
OUTPUT_FILE = os.path.join(BASE_DIR, "aidm", "src", "aidm", "data", "_spells_data.py")

LEVEL_NAMES = {0: "戏法", 1: "一环", 2: "二环", 3: "三环", 4: "四环",
               5: "五环", 6: "六环", 7: "七环", 8: "八环", 9: "九环"}

# 环阶文件名映射
LEVEL_FILES = {
    0: "0环.htm", 1: "1环.htm", 2: "2环.htm", 3: "3环.htm", 4: "4环.htm",
    5: "5环.htm", 6: "6环.htm", 7: "7环.htm", 8: "8环.htm", 9: "9环.htm",
}


# ---- HTML 解析 ----

def clean_html(text: str) -> str:
    """去掉 HTML 标签，合并空白。"""
    # 移除 <script> 块
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # 移除 style 块
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # 解码 HTML 实体
    text = html_mod.unescape(text)
    # 移除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    # 规范化空白
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'\n+', ' ', text)
    return text.strip()


def strip_uu(text: str) -> str:
    """移除描述中的 <U> 标签（游戏术语标记），保留文本。"""
    return re.sub(r'<U[^>]*>', '', re.sub(r'</U>', '', text))


def parse_spell_level_and_school(em_text: str) -> tuple[int, str, str]:
    """解析 EM 标签内容，返回 (环阶, 学派, 职业列表字符串)。

    戏法格式: "塑能 戏法（术士、法师）"
    有环阶格式: "一环 防护（游侠、法师）"
    """
    # 戏法: "{学派} 戏法（{职业}）"
    m = re.match(r'(.+?)\s+戏法（(.+?)）', em_text)
    if m:
        school = m.group(1).strip()
        classes_str = m.group(2).strip()
        return 0, school, classes_str

    # 有环阶: "{X}环 {学派}（{职业}）"
    m = re.match(r'(\S+)环\s+(.+?)（(.+?)）', em_text)
    if m:
        level_str = m.group(1).strip()
        school = m.group(2).strip()
        classes_str = m.group(3).strip()
        # 汉字数字 → 阿拉伯数字
        level_map = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
                     "六": 6, "七": 7, "八": 8, "九": 9}
        level = level_map.get(level_str, 1)
        return level, school, classes_str

    raise ValueError(f"无法解析 EM 标签: {em_text!r}")


def parse_components(comp_str: str) -> tuple[set, str, float, bool]:
    """解析法术成分字符串，返回 (成分集合, 材料描述, 价格, 是否消耗)。

    例: "V、S、M（一颗蝙蝠粪和硫磺搓成的小球）" → ({"V","S","M"}, "一颗蝙蝠粪...", 0.0, False)
    例: "V、S、M（价值100gp的珍珠，被法术消耗）" → ({"V","S","M"}, "价值100gp的珍珠", 100.0, True)
    """
    components = set()
    material_desc = ""
    material_cost = 0.0
    material_consumed = False

    # 检测 M 材料成分
    m_match = re.search(r'M[（(](.+?)[）)]$', comp_str)
    if m_match:
        components.add("M")
        material_desc = m_match.group(1).strip()
        # 检测价格
        cost_m = re.search(r'价值\s*(\d+)\s*gp', material_desc)
        if cost_m:
            material_cost = float(cost_m.group(1))
        # 检测是否消耗
        if re.search(r'被法术消耗|会被消耗|消耗', material_desc):
            material_consumed = True

    # 检测 V/S
    for ch in ["V", "S"]:
        if ch in comp_str:
            components.add(ch)

    return components, material_desc, material_cost, material_consumed


def detect_casting_time_type(ct: str) -> str:
    """将施法时间字符串映射为类型常量。"""
    ct_lower = ct.strip()
    if ct_lower.startswith("反应"):
        return "REACTION"
    if ct_lower.startswith("附赠"):
        return "BONUS_ACTION"
    if ct_lower in ("动作",):
        return "ACTION"
    return "TIME"


def parse_duration(dur_str: str) -> tuple[str, bool, bool]:
    """解析持续时间，返回 (duration, concentration, ritual)。

    例: "专注，至多1分钟" → ("专注，至多1分钟", True, False)
    例: "1小时或仪式" → ("1小时或仪式", False, True)
    """
    concentration = "专注" in dur_str
    ritual = "仪式" in dur_str
    return dur_str.strip(), concentration, ritual


def detect_effect_type(desc: str, spell_name: str) -> tuple[str, Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], int, bool]:
    """根据描述推测法术效果类型，返回 (effect_type, save_ability, damage_dice, damage_type, heal_dice, heal_type, ac_bonus, add_casting_mod_to_heal)。"""
    effect_type = "automatic"
    save_ability = None
    damage_dice = None
    damage_type = None
    heal_dice = None
    heal_type = None
    ac_bonus = 0
    add_casting_mod_to_heal = False

    # 护盾
    if spell_name in ("护盾术", "Shield") or re.search(r'AC\s*[具获]有\s*[+\-]?\d+\s*加值', desc):
        effect_type = "shield"
        m = re.search(r'AC.*?[+\-]?\s*(\d+)\s*加值', desc)
        if m:
            ac_bonus = int(m.group(1))
        return effect_type, save_ability, damage_dice, damage_type, heal_dice, heal_type, ac_bonus, add_casting_mod_to_heal

    # 治疗
    if any(kw in desc for kw in ["恢复", "回复", "治疗", "生命值"]):
        # 找最后一个"恢复/回复/治疗"之后的内容（最可能含治疗骰）
        heal_ctx = desc
        for kw in ["恢复", "回复", "治疗"]:
            if kw in desc:
                parts = desc.rsplit(kw, 1)
                heal_ctx = parts[-1] if len(parts) > 1 else desc
                break
        heal_m = re.search(r'(\d+d\d+(?:\s*[+\-]\s*\d+)?)', heal_ctx)
        if heal_m:
            effect_type = "heal"
            heal_dice = heal_m.group(1).replace(" ", "")
            # 检测是否加施法属性调整值
            add_casting_mod_to_heal = bool(re.search(r'施法属性调整值|施法关键属性调整值', desc))
            return effect_type, save_ability, damage_dice, damage_type, heal_dice, heal_type, ac_bonus, add_casting_mod_to_heal

    # 伤害检测
    if not heal_dice:
        # 远程法术攻击 / 近战法术攻击
        if re.search(r'远程法术攻击|近战法术攻击|进行一次.*攻击', desc):
            effect_type = "attack_roll"
        # 豁免
        elif re.search(r'成功[于]?一次.*豁免|必须.*豁免', desc):
            effect_type = "saving_throw"
            # 提取豁免属性
            save_map = {
                "敏捷": "DEX", "体质": "CON", "感知": "WIS",
                "智力": "INT", "魅力": "CHA", "力量": "STR",
            }
            for cn, ab in save_map.items():
                if cn in desc:
                    save_ability = ab
                    break

    # 伤害骰
    dmg_m = re.search(r'(?:受[到]?|造成|产生)\s*(\d+d\d+[\s+]*\d*)\s*点\s*(火焰|寒冷|闪电|强酸|毒素|暗蚀|光耀|力场|雷鸣|心灵|穿刺|挥砍|钝击|黯蚀)?\s*伤害', desc)
    if dmg_m:
        damage_dice = dmg_m.group(1).strip().replace(" ", "")
        if dmg_m.group(2):
            dt = dmg_m.group(2).strip()
            type_map = {"火焰": "fire", "寒冷": "cold", "闪电": "lightning", "强酸": "acid",
                       "毒素": "poison", "暗蚀": "necrotic", "黯蚀": "necrotic", "光耀": "radiant",
                       "力场": "force", "雷鸣": "thunder", "心灵": "psychic",
                       "穿刺": "piercing", "挥砍": "slashing", "钝击": "bludgeoning"}
            damage_type = type_map.get(dt, dt.lower())

    return effect_type, save_ability, damage_dice, damage_type, heal_dice, heal_type, ac_bonus, add_casting_mod_to_heal


def extract_upcast(desc: str, spell_level: int) -> Optional[dict]:
    """提取升环施法/戏法强化信息。"""
    # 升环施法
    upcast_m = re.search(r'升环施法[。，.]?\s*(.+?)(?:$|(?=<))', desc)
    if upcast_m:
        text = clean_html(upcast_m.group(1))[:200]
        # 常见模式: "每比X环高出一环，伤害+1d6"
        extra_dice = re.search(r'[+\-]?\s*(\d+d\d+)', text)
        if extra_dice:
            return {"per_level_above_base": extra_dice.group(1).replace(" ", ""),
                    "desc": text}
        # 额外目标模式
        if "目标" in text or "生物" in text:
            extra_target = re.search(r'额外.*?(\d+)\s*个', text)
            if extra_target:
                return {"per_level_above_base": "extra_target",
                        "targets_per_level": int(extra_target.group(1)),
                        "desc": text}
        return {"desc": text}

    # 戏法强化
    if spell_level == 0:
        cantrip_m = re.search(r'戏法强化[。，.]?\s*(.+?)(?:$|(?=<))', desc)
        if cantrip_m:
            text = clean_html(cantrip_m.group(1))[:200]
            # 提取各等级伤害提升
            scaling = {}
            for m in re.finditer(r'(\d+)\s*级[（(]\s*(\d+d\d+)', text):
                scaling[int(m.group(1))] = m.group(2).replace(" ", "")
            if scaling:
                return {"cantrip_scaling": sorted(scaling.items())}
            return {"cantrip_scaling": text}

    return None


def parse_spells_from_html(html_text: str, level: int) -> list[dict]:
    """从一个环阶文件的 HTML 中提取所有法术，返回 raw dict 列表。"""
    spells = []

    # 移除 script 和 style
    html_text = re.sub(r'<script[^>]*>.*?</script>', '', html_text, flags=re.DOTALL)
    html_text = re.sub(r'<style[^>]*>.*?</style>', '', html_text, flags=re.DOTALL)

    # 匹配所有法术 H4 块
    # 每个法术从 <H4 id="...">...</H4> 开始
    h4_pattern = re.compile(
        r'<H4\s+id="([^"]+)">\s*(.+?)\s*</H4>\s*'
        r'(.*?)(?=<H4\s+id="|$)',
        re.DOTALL
    )

    for m in h4_pattern.finditer(html_text):
        spell_id = m.group(1)  # Acid_Splash
        h4_text = m.group(2)   # 酸液飞溅｜Acid Splash
        body = m.group(3)      # P tag content + blockquotes

        # 解析名称
        name_parts = h4_text.split('｜')
        if len(name_parts) == 2:
            cn_name = name_parts[0].strip()
            en_name = name_parts[1].strip()
        else:
            cn_name = h4_text.strip()
            en_name = spell_id.replace('_', ' ')

        # 解析 EM（学派/环阶/职业）
        em_m = re.search(r'<EM>(.+?)</EM>', body)
        if not em_m:
            continue
        em_text = em_m.group(1).strip()

        try:
            _, school, classes_str = parse_spell_level_and_school(em_text)
        except ValueError:
            print(f"  [WARN] 无法解析学派: {cn_name} | EM={em_text!r}")
            continue

        class_list = [c.strip() for c in classes_str.replace('、', ',').replace('，', ',').split(',') if c.strip()]

        # 解析四个属性字段
        # 施法时间
        ct_m = re.search(r'<(?:STRONG|b|B)>\s*施法时间：\s*</(?:STRONG|b|B)>\s*(.+?)(?:\s*<BR>|<br>|<)', body)
        casting_time = ct_m.group(1).strip() if ct_m else "动作"

        # 施法距离
        rng_m = re.search(r'<(?:STRONG|b|B)>\s*施法距离：\s*</(?:STRONG|b|B)>\s*(.+?)(?:\s*<BR>|<br>|<)', body)
        spell_range = rng_m.group(1).strip() if rng_m else "自身"

        # 法术成分
        comp_m = re.search(r'<(?:STRONG|b|B)>\s*法术成分：\s*</(?:STRONG|b|B)>\s*(.+?)(?:\s*<BR>|<br>|<)', body)
        comp_str = comp_m.group(1).strip() if comp_m else "V、S"
        # Normalize comma/dunhao
        comp_str = comp_str.replace('，', ',').replace('、', ',')

        components, material_desc, material_cost, material_consumed = parse_components(comp_str)

        # 持续时间
        dur_m = re.search(r'<(?:STRONG|b|B)>\s*持续时间：\s*</(?:STRONG|b|B)>\s*(.+?)(?:\s*<BR>|<br>|<)', body)
        dur_str = dur_m.group(1).strip() if dur_m else "立即"
        duration, concentration, ritual = parse_duration(dur_str)

        # 提取描述文本
        # 去除 BLOCKQUOTE 标签但保留内容
        desc_body = body
        desc_body = re.sub(r'</?BLOCKQUOTE[^>]*>', '', desc_body)
        desc_body = re.sub(r'</?P[^>]*>', '', desc_body)

        # 提取纯文本描述
        desc_text = clean_html(desc_body)

        # 去掉属性字段前缀（施法时间/距离/成分/持续时间行）
        desc_lines = desc_text.split('。')
        # 找到描述开始的位置（在四个属性字段之后）
        # 简单做法：找到"持续时间"之后的内容开始
        dur_start = desc_text.find(dur_str)
        if dur_start >= 0:
            desc_text = desc_text[dur_start + len(dur_str):].strip(' 。')
            if desc_text.startswith('。'):
                desc_text = desc_text[1:].strip()

        # 提取升环/戏法强化（从原始HTML中提取，然后从描述文本中移除）
        upcast = extract_upcast(body, level)

        # 从描述中移除升环施法/戏法强化段（从关键词到文本末尾）
        if upcast is not None:
            desc_text = re.sub(r'升环施法[。，.]?\s*.*$', '', desc_text)
            desc_text = re.sub(r'戏法强化[。，.]?\s*.*$', '', desc_text)
            desc_text = desc_text.strip().rstrip('。，').strip()

        # 推测效果类型
        effect_type, save_ability, damage_dice, damage_type, heal_dice, heal_type, ac_bonus, add_casting_mod = \
            detect_effect_type(desc_text, cn_name)

        # 构建 raw dict
        raw = {
            "name": cn_name,
            "en_name": en_name,
            "level": level,
            "school": school,
            "casting_time": casting_time,
            "casting_time_type": detect_casting_time_type(casting_time),
            "range": spell_range,
            "components": components,
            "material_desc": material_desc,
            "material_cost_gp": material_cost,
            "material_consumed": material_consumed,
            "duration": duration,
            "concentration": concentration,
            "ritual": ritual,
            "effect_type": effect_type,
            "save_ability": save_ability,
            "damage_dice": damage_dice,
            "damage_type": damage_type,
            "heal_dice": heal_dice,
            "add_casting_mod_to_heal": add_casting_mod,
            "ac_bonus": ac_bonus,
            "upcast": upcast,
            "description": desc_text,
            "class_list": class_list,
        }
        spells.append(raw)

    return spells


# ---- Python 代码生成 ----

def _format_spell_class_list(class_list):
    """格式化职业元组。"""
    return f'({", ".join(f"{c!r}" for c in class_list)},)'

def _format_components(comp_set):
    """格式化 frozenset。"""
    items = sorted(comp_set)
    return f'frozenset({{{", ".join(f"{c!r}" for c in items)}}})'

def _escape_str(s):
    """转义字符串用于Python字面量。"""
    if s is None:
        return "None"
    return repr(s)

def _format_upcast(upcast):
    """格式化升环施法字典。"""
    if upcast is None:
        return "None"
    if "cantrip_scaling" in upcast:
        cs = upcast["cantrip_scaling"]
        if isinstance(cs, list):
            items = ", ".join(f"({lvl}, {dice!r})" for lvl, dice in cs)
            return f'{{"cantrip_scaling": [{items}]}}'
        return f'{{"cantrip_scaling": {cs!r}}}'
    parts = []
    for k, v in upcast.items():
        if k == "desc":
            continue
        if isinstance(v, int):
            parts.append(f'{k!r}: {v}')
        else:
            parts.append(f'{k!r}: {v!r}')
    return "{" + ", ".join(parts) + "}"


def generate_spells_py(all_spells: list[dict], output_path: str) -> None:
    """生成 _spells_data.py 文件。"""
    # 按环阶分组
    by_level = {i: [] for i in range(10)}
    for s in all_spells:
        by_level[s["level"]].append(s)

    lines = []
    lines.append('""""法术数据表（自动生成）。')
    lines.append('')
    lines.append('来源：topics/玩家手册2024/法术详述/{0..9}环.htm')
    lines.append(f'法术总数：{len(all_spells)}')
    lines.append('生成脚本：aidm/scripts/extract_spells.py')
    lines.append('"""')
    lines.append('')
    lines.append('# flake8: noqa: E501')
    lines.append('')
    lines.append('from aidm.data.spells import Spell')
    lines.append('')
    lines.append('_SPELLS_LIST: list[Spell] = [')

    for level in range(10):
        spells = by_level[level]
        if not spells:
            continue
        level_name = LEVEL_NAMES.get(level, f"{level}环")
        lines.append(f'    # ── {level_name} ──')

        for s in spells:
            lines.append(f'    Spell(')
            lines.append(f'        name={s["name"]!r}, en_name={s["en_name"]!r},')
            lines.append(f'        level={s["level"]}, school={s["school"]!r},')
            lines.append(f'        casting_time={s["casting_time"]!r}, casting_time_type={s["casting_time_type"]!r},')
            lines.append(f'        range={s["range"]!r},')
            lines.append(f'        components={_format_components(s["components"])},')
            lines.append(f'        material_desc={s["material_desc"]!r},')
            lines.append(f'        material_cost_gp={s["material_cost_gp"]},')
            lines.append(f'        material_consumed={s["material_consumed"]},')
            lines.append(f'        duration={s["duration"]!r},')
            lines.append(f'        concentration={s["concentration"]},')
            lines.append(f'        ritual={s["ritual"]},')
            lines.append(f'        effect_type={s["effect_type"]!r},')
            lines.append(f'        save_ability={_escape_str(s["save_ability"])},')
            lines.append(f'        damage_dice={_escape_str(s["damage_dice"])},')
            lines.append(f'        damage_type={_escape_str(s["damage_type"])},')
            lines.append(f'        heal_dice={_escape_str(s["heal_dice"])},')
            lines.append(f'        add_casting_mod_to_heal={s.get("add_casting_mod_to_heal", False)},')
            lines.append(f'        ac_bonus={s["ac_bonus"]},')
            lines.append(f'        upcast={_format_upcast(s["upcast"])},')
            # 截断过长的描述
            desc = s["description"]
            if len(desc) > 500:
                desc = desc[:497] + "..."
            lines.append(f'        description={desc!r},')
            lines.append(f'        class_list={_format_spell_class_list(s["class_list"])},')
            lines.append(f'    ),')

    lines.append(']')
    lines.append('')
    lines.append('')
    lines.append('# 字典索引便于按名查找')
    lines.append('SPELLS: dict[str, Spell] = {s.name: s for s in _SPELLS_LIST}')
    lines.append('')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"✓ 已生成 {output_path}")
    print(f"  法术总数: {len(all_spells)}")
    for lvl in range(10):
        if by_level[lvl]:
            print(f"  {LEVEL_NAMES[lvl]:4s}: {len(by_level[lvl])} 个")


# ---- 主函数 ----

def main():
    all_spells = []

    for level in range(10):
        filepath = os.path.join(WEB_SPELLS_DIR, LEVEL_FILES[level])
        if not os.path.exists(filepath):
            print(f"[SKIP] 文件不存在: {filepath}")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            html_text = f.read()

        spells = parse_spells_from_html(html_text, level)
        all_spells.extend(spells)
        print(f"[{LEVEL_NAMES[level]:4s}] {filepath} → {len(spells)} 个法术")

    print(f"\n总计: {len(all_spells)} 个法术")

    if all_spells:
        generate_spells_py(all_spells, OUTPUT_FILE)
    else:
        print("[ERROR] 未提取到任何法术！请检查路径和 HTML 格式。")
        sys.exit(1)


if __name__ == "__main__":
    main()
