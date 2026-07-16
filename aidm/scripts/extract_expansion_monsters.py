"""
Extract monsters from expansion books (MPMM, VGtM, etc.) that use
the older stat block format (not the MM 2025 stat-block div).

Format: <P><STRONG><FONT size=5>Name EN</FONT></STRONG></P>
        <P><STRONG>Name EN</STRONG><BR><EM>type</EM><BR>AC/HP/Speed/Abilities<BR>...</P>
"""

import re
import json
import os
from pathlib import Path
from collections import defaultdict

BASE = Path("E:/Project/dnd--master/5echm_web/topics")
OUTPUT = Path("E:/Project/dnd--master/aidm/src/aidm/data/_expansion_monsters_data.py")

SOURCES = [
    ("多元宇宙的怪物/图鉴", "MPMM"),
]


def clean_html(text):
    """Strip HTML tags and normalize whitespace."""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_monster(html_content, filepath):
    """Extract a single MPMM-style monster from HTML."""
    # Remove script/style blocks
    html = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)

    # Find stat block: starts with name in STRONG+FONT size=5 (case-insensitive, handle nesting)
    # Patterns:
    #   A: <P><STRONG><FONT size=5>Name EN</FONT></STRONG></P>
    #   B: <p><font size=5><font><strong>Name EN</strong></font></font></p>
    #   C: <p><font size=5><font color=#800000><strong>Name</strong></font></font></p>
    name_match = re.search(
        r'<(?:P|p)>\s*<(?:STRONG|strong)>\s*<(?:FONT|font)[^>]*size\s*=\s*5[^>]*>\s*(.+?)\s*</(?:FONT|font)>\s*</(?:STRONG|strong)>\s*</(?:P|p)>',
        html, re.DOTALL
    )
    if not name_match:
        # Try with nested font tags
        name_match = re.search(
            r'<(?:P|p)>\s*<(?:FONT|font)[^>]*size\s*=\s*5[^>]*>\s*<(?:FONT|font)[^>]*>\s*<(?:STRONG|strong)>\s*(.+?)\s*</(?:STRONG|strong)>\s*</(?:FONT|font)>\s*</(?:FONT|font)>\s*</(?:P|p)>',
            html, re.DOTALL
        )
    if not name_match:
        # Try without size=5
        name_match = re.search(
            r'<(?:P|p)>\s*<(?:STRONG|strong)>\s*<(?:FONT|font)[^>]*>\s*(.+?)\s*</(?:FONT|font)>\s*</(?:STRONG|strong)>\s*</(?:P|p)>',
            html, re.DOTALL
        )
    if not name_match:
        return None

    name_raw = name_match.group(1)
    name_text = clean_html(name_raw)

    # Split Chinese/English name
    # Pattern: "中文名English Name" or "中文名 English Name"
    name_parts = re.split(r'\s(?=[A-Z])', name_text, maxsplit=1)
    if len(name_parts) == 2:
        cn_name = name_parts[0].strip()
        en_name = name_parts[1].strip()
    else:
        # Try camelCase split
        cn_name = name_text
        en_name = ''

    # Find stat block: second instance of name in STRONG+FONT
    # Pattern: <P><STRONG><FONT>Name EN</FONT></STRONG><BR><EM>...</EM><BR>AC/HP/...
    body_start = name_match.end()

    # Find the stat line paragraph
    stat_match = re.search(
        r'<(?:P|p)>\s*<(?:STRONG|strong)>\s*<(?:FONT|font)[^>]*>\s*'
        + re.escape(name_text) +
        r'\s*</(?:FONT|font)>\s*</(?:STRONG|strong)>\s*<BR\s*/?>\s*<(?:EM|em)>\s*(.+?)\s*</(?:EM|em)>\s*<BR\s*/?>\s*(.+?)\s*</(?:P|p)>',
        html[body_start:],
        re.DOTALL
    )
    if not stat_match:
        # Try nested font pattern
        stat_match = re.search(
            r'<(?:P|p)>\s*<(?:FONT|font)[^>]*>\s*<(?:FONT|font)[^>]*>\s*<(?:STRONG|strong)>\s*'
            + re.escape(name_text) +
            r'\s*</(?:STRONG|strong)>\s*</(?:FONT|font)>\s*</(?:FONT|font)>\s*<BR\s*/?>\s*<(?:EM|em)>\s*(.+?)\s*</(?:EM|em)>\s*<BR\s*/?>\s*(.+?)\s*</(?:P|p)>',
            html[body_start:],
            re.DOTALL
        )
    if not stat_match:
        # Try generic: any STRONG+FONT followed by EM and stats
        stat_match = re.search(
            r'<(?:P|p)>\s*<(?:STRONG|strong)>\s*<(?:FONT|font)[^>]*>\s*(.+?)\s*</(?:FONT|font)>\s*</(?:STRONG|strong)>\s*<BR\s*/?>\s*<(?:EM|em)>\s*(.+?)\s*</(?:EM|em)>\s*<BR\s*/?>\s*(.+?)\s*</(?:P|p)>',
            html[body_start:],
            re.DOTALL
        )

    if not stat_match:
        return None

    em_text = stat_match.group(2) if len(stat_match.groups()) >= 2 else stat_match.group(1)
    stats_text = stat_match.group(3) if len(stat_match.groups()) >= 3 else stat_match.group(2)

    # Parse type/size/alignment from EM
    # "中型龙类，无阵营"
    em_clean = clean_html(em_text)
    type_parts = em_clean.split('，')
    size_type = type_parts[0] if type_parts else ''
    alignment = type_parts[1] if len(type_parts) > 1 else ''

    # Parse size and creature type
    size = ''
    creature_type = ''
    size_keywords = ['微型', '小型', '中型', '大型', '巨型', '超巨型']
    for sk in size_keywords:
        if sk in size_type:
            size = sk
            creature_type = size_type.replace(sk, '').strip()
            break
    if not size:
        creature_type = size_type
        size = '中型'

    # Parse stat line
    stats_clean = clean_html(stats_text)

    result = {
        "name": cn_name,
        "en_name": en_name,
        "size": size,
        "creature_type": creature_type,
        "alignment": alignment,
        "ac": 0,
        "hp": 0,
        "hp_formula": "",
        "speed": {},
        "abilities": {},
        "skills": {},
        "senses": {},
        "languages": "",
        "cr": "0",
        "xp": 0,
        "pb": 2,
        "traits": [],
        "actions": [],
        "bonus_actions": [],
        "reactions": [],
        "legendary_actions": [],
        "description": "",
        "source": "MPMM",
    }

    # Parse AC
    ac_match = re.search(r'护甲等级[：:]\s*(\d+)', stats_clean)
    if ac_match:
        result["ac"] = int(ac_match.group(1))

    # Parse HP
    hp_match = re.search(r'生命值[：:]\s*(\d+)[（(](\d+d\d+\s*[+\-]?\s*\d*)[）)]', stats_clean)
    if hp_match:
        result["hp"] = int(hp_match.group(1))
        result["hp_formula"] = hp_match.group(2).replace(" ", "")

    # Parse speed
    speed_match = re.search(r'速度[：:]\s*([\d，,、；;\s尺攀爬游泳飞行掘穴]+)', stats_clean)
    if speed_match:
        speed_text = speed_match.group(1)
        speeds = {}
        # "30尺" or "30尺，飞行60尺，游泳30尺"
        for seg in re.split(r'[，,、]', speed_text):
            seg = seg.strip()
            if not seg:
                continue
            m = re.match(r'(\d+)\s*尺\s*(.*)', seg)
            if m:
                dist = int(m.group(1))
                move_type = m.group(2).strip() or '步行'
                speeds[move_type] = dist
        result["speed"] = speeds

    # Parse abilities: "力量16（+3） 敏捷11（+0） 体质16（+3） 智力4（-3） 感知10（+0） 魅力7（-2）"
    ability_map = {
        '力量': 'str', '敏捷': 'dex', '体质': 'con',
        '智力': 'int', '感知': 'wis', '魅力': 'cha'
    }
    for cn, en in ability_map.items():
        m = re.search(rf'{cn}\s*(\d+)[（(]\s*([+\-]?\d+)\s*[）)]', stats_clean)
        if m:
            score = int(m.group(1))
            mod = int(m.group(2))
            result["abilities"][en] = {"score": score, "mod": mod, "save": mod}

    # Parse skills
    skill_match = re.search(r'技能[：:]\s*(.+?)(?:感官|$)', stats_clean)
    if skill_match:
        skill_text = skill_match.group(1)
        # "察觉+2，隐匿+5"
        for pair in re.finditer(r'(\S+)\s*([+\-]\d+)', skill_text):
            result["skills"][pair.group(1)] = int(pair.group(2))

    # Parse senses
    senses_match = re.search(r'感官[：:]\s*(.+?)(?:语言|$)', stats_clean)
    if senses_match:
        senses_text = senses_match.group(1)
        # "黑暗视觉60尺，被动察觉12"
        dv_match = re.search(r'黑暗视觉\s*(\d+)\s*尺', senses_text)
        if dv_match:
            result["senses"]["黑暗视觉"] = int(dv_match.group(1))
        pp_match = re.search(r'被动察觉\s*(\d+)', senses_text)
        if pp_match:
            result["senses"]["被动察觉"] = int(pp_match.group(1))

    # Parse languages
    lang_match = re.search(r'语言[：:]\s*(.+?)(?:挑战等级|$)', stats_clean)
    if lang_match:
        result["languages"] = lang_match.group(1).strip()

    # Parse CR
    cr_match = re.search(r'挑战等级[：:]\s*(\d+)(?:/\d+)?[（(]?(\d+)\s*XP[）)]?', stats_clean)
    if cr_match:
        result["cr"] = cr_match.group(1)
        result["xp"] = int(cr_match.group(2))

    # Parse PB
    pb_match = re.search(r'熟练加值[：:]\s*[+\-]?(\d+)', stats_clean)
    if pb_match:
        result["pb"] = int(pb_match.group(1))
    else:
        # Calculate from CR
        cr_val = float(result["cr"]) if result["cr"] != "?" else 0
        result["pb"] = max(2, 2 + int((cr_val - 1) / 4) if cr_val >= 5 else 2)

    # Parse actions
    action_match = re.search(
        r'<(?:P|p)>\s*<(?:STRONG|strong)>\s*<(?:FONT|font)[^>]*>\s*(?:动作|Actions?)\s*</(?:FONT|font)>\s*</(?:STRONG|strong)>\s*(.+?)\s*</(?:P|p)>',
        html[body_start:], re.DOTALL | re.IGNORECASE
    )
    if action_match:
        actions_text = action_match.group(1)
        # Split by <BR> then parse <STRONG>name</STRONG>description
        parts = re.split(r'<BR\s*/?>', actions_text)
        for part in parts:
            strong_match = re.search(r'<STRONG>\s*(.+?)\s*</STRONG>\s*(.*)', part, re.DOTALL | re.IGNORECASE)
            if strong_match:
                act_name = clean_html(strong_match.group(1))
                act_desc = clean_html(strong_match.group(2))
                # Split Chinese/English name
                act_parts = act_name.split()
                act_en = act_parts[-1] if act_parts and act_parts[-1][0].isascii() else ''
                act_cn = ' '.join(act_parts[:-1]) if act_en else act_name
                if act_desc:
                    result["actions"].append({
                        "name": act_cn,
                        "en_name": act_en,
                        "description": act_desc,
                    })

    # Parse traits  
    trait_match = re.search(
        r'<(?:P|p)>\s*<(?:STRONG|strong)>\s*<(?:FONT|font)[^>]*>\s*(?:特性|特质|Traits?)\s*</(?:FONT|font)>\s*</(?:STRONG|strong)>\s*(.+?)\s*</(?:P|p)>',
        html[body_start:], re.DOTALL | re.IGNORECASE
    )
    if trait_match:
        traits_text = trait_match.group(1)
        parts = re.split(r'<BR\s*/?>', traits_text)
        for part in parts:
            strong_match = re.search(r'<STRONG>\s*(.+?)\s*</STRONG>\s*(.*)', part, re.DOTALL | re.IGNORECASE)
            if strong_match:
                t_name = clean_html(strong_match.group(1))
                t_desc = clean_html(strong_match.group(2))
                act_parts = t_name.split()
                act_en = act_parts[-1] if act_parts and act_parts[-1][0].isascii() else ''
                act_cn = ' '.join(act_parts[:-1]) if act_en else t_name
                if t_desc:
                    result["traits"].append({
                        "name": act_cn,
                        "en_name": act_en,
                        "description": t_desc,
                    })

    return result


def main():
    all_monsters = []
    errors = []

    for rel_path, source_name in SOURCES:
        src_dir = BASE / rel_path
        count = 0

        for root, dirs, files in os.walk(src_dir):
            for fname in files:
                if not fname.endswith('.htm'):
                    continue
                filepath = Path(root) / fname
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        html = f.read()
                    monster = extract_monster(html, filepath)
                    if monster:
                        all_monsters.append(monster)
                        count += 1
                except Exception as e:
                    errors.append(f"{fname}: {e}")

        print(f"  {source_name}: {count} monsters")

    print(f"\n  Total: {len(all_monsters)} expansion monsters")
    if errors:
        print(f"  Errors: {len(errors)}")
        for e in errors[:5]:
            print(f"    {e}")

    # Stats
    by_type = defaultdict(int)
    for m in all_monsters:
        by_type[m["creature_type"]] += 1
    print("\n  By type:")
    for t, n in sorted(by_type.items(), key=lambda x: -x[1])[:10]:
        print(f"    {t}: {n}")

    # Deduplicate by name
    seen = {}
    for m in all_monsters:
        key = m["name"]
        if key not in seen:
            seen[key] = m
    print(f"  After dedup: {len(seen)} monsters")

    # Write output
    output_monsters = list(seen.values())
    lines = [
        '# Auto-generated by extract_expansion_monsters.py.',
        f'# Sources: MPMM, VGtM, etc.',
        f'# Total: {len(output_monsters)} monsters',
        '',
        '_EXPANSION_MONSTERS_LIST = [',
    ]
    for m in sorted(output_monsters, key=lambda x: x["name"]):
        json_str = json.dumps(m, ensure_ascii=False)
        json_str = json_str.replace(': true,', ': True,').replace(': false,', ': False,')
        json_str = json_str.replace(': true}', ': True}').replace(': false}', ': False}')
        lines.append(f'    {json_str},')
    lines.append(']')
    lines.append('')

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f"\n  Written to {OUTPUT}")


if __name__ == "__main__":
    main()
