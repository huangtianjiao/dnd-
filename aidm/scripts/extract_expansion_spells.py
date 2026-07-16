"""
Extract expansion spells from XGtE and TCoE and merge with existing PHB 2024 spells.
Reuses parsing logic from extract_spells.py.
"""

import re
import os
import sys
import json
import html as html_mod
from typing import Optional
from pathlib import Path

# Add parent for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from extract_spells import (
    clean_html, strip_uu,
    parse_spell_level_and_school, parse_components,
    detect_casting_time_type, parse_duration,
    detect_effect_type, extract_upcast,
    LEVEL_FILES, LEVEL_NAMES
)

BASE = Path("E:/Project/dnd--master/5echm_web/topics")
OUTPUT = Path("E:/Project/dnd--master/aidm/src/aidm/data/_expansion_spells_data.py")

SOURCES = [
    ("珊娜萨的万事指南/法术/法术详述", "XGtE"),
    ("塔莎的万事坩埚/法术/法术详述", "TCoE"),
    # Additional expansion spell sources
    ("施法者速查/扩展内容", "EXP"),
]


def parse_spells_from_html_xgte(html_text: str, level: int, source: str) -> list[dict]:
    """Parse spells from XGtE/TCoE format HTML (H4 tags)."""
    spells = []

    html_text = re.sub(r'<script[^>]*>.*?</script>', '', html_text, flags=re.DOTALL)
    html_text = re.sub(r'<style[^>]*>.*?</style>', '', html_text, flags=re.DOTALL)

    # Match H4 blocks with id
    h4_pattern = re.compile(
        r'<H4\s+id="([^"]+)">\s*(.+?)\s*</H4>\s*'
        r'(.*?)(?=<H4\s+id="|$)',
        re.DOTALL
    )

    for m in h4_pattern.finditer(html_text):
        spell_id = m.group(1)
        h4_text = m.group(2)
        body = m.group(3)

        # Parse name: "中文名｜English Name"
        name_parts = h4_text.split('｜')
        if len(name_parts) == 2:
            cn_name = name_parts[0].strip()
            en_name = name_parts[1].strip()
        else:
            cn_name = h4_text.strip()
            en_name = spell_id.replace('_', ' ')

        # Parse EM (school/level/classes)
        em_m = re.search(r'<EM>(.+?)</EM>', body)
        if not em_m:
            continue
        em_text = em_m.group(1).strip()

        # Get content after EM
        content_start = em_m.end()
        content = body[content_start:]

        # Parse standard spell fields from content
        ct_match = re.search(r'<b>施法时间[：:].*?</b>\s*(.+?)(?:<BR|</)', content, re.DOTALL | re.IGNORECASE)
        range_match = re.search(r'<b>施法距离[：:].*?</b>\s*(.+?)(?:<BR|</)', content, re.DOTALL | re.IGNORECASE)
        comp_match = re.search(r'<b>法术成分[：:].*?</b>\s*(.+?)(?:<BR|</)', content, re.DOTALL | re.IGNORECASE)
        dur_match = re.search(r'<b>持续时间[：:].*?</b>\s*(.+?)(?:<BR|</)', content, re.DOTALL | re.IGNORECASE)

        casting_time = clean_html(ct_match.group(1)) if ct_match else "1动作"
        spell_range = clean_html(range_match.group(1)) if range_match else "触及"
        components_raw = clean_html(comp_match.group(1)) if comp_match else "V、S"
        duration_raw = clean_html(dur_match.group(1)) if dur_match else "立即"

        # Get description (after duration or EM)
        if dur_match:
            desc_start = dur_match.end()
        else:
            desc_start = content_start
        desc = content[desc_start:]
        # Remove extra BR tags before description
        desc = re.sub(r'^[\s<BR>]*', '', desc, flags=re.IGNORECASE)
        description = clean_html(strip_uu(desc))

        # Parse structured fields
        try:
            spell_level, school, classes_str = parse_spell_level_and_school(em_text)
        except ValueError:
            spell_level = level
            school = "变化"
            classes_str = ""

        class_list = [c.strip() for c in classes_str.replace("、", ",").split(",") if c.strip()]

        components_set, material_desc, material_cost, material_consumed = parse_components(components_raw)
        casting_time_type = detect_casting_time_type(casting_time)
        duration, concentration, ritual = parse_duration(duration_raw)
        effect_type, save_ability, damage_dice, damage_type, heal_dice, heal_type, ac_bonus, add_casting_mod = \
            detect_effect_type(description, cn_name)
        upcast = extract_upcast(description, spell_level)

        spells.append({
            "name": cn_name,
            "name_en": en_name,
            "level": spell_level,
            "school": school,
            "casting_time": casting_time,
            "casting_time_type": casting_time_type,
            "spell_range": spell_range,
            "components": sorted(list(components_set)),
            "material_desc": material_desc,
            "material_cost": material_cost,
            "material_consumed": material_consumed,
            "duration": duration,
            "concentration": concentration,
            "ritual": ritual,
            "class_list": class_list,
            "effect_type": effect_type,
            "save_ability": save_ability,
            "damage_dice": damage_dice,
            "damage_type": damage_type,
            "heal_dice": heal_dice,
            "heal_type": heal_type,
            "ac_bonus": ac_bonus,
            "add_casting_mod_to_heal": add_casting_mod,
            "upcast": upcast,
            "description": description,
            "source": source,
        })

    return spells


def main():
    all_spells = {}
    total = 0

    for rel_path, source_name in SOURCES:
        src_dir = BASE / rel_path
        if not src_dir.exists():
            print(f"  SKIP: {src_dir} not found")
            continue

        source_count = 0
        for level, filename in LEVEL_FILES.items():
            filepath = src_dir / filename
            if not filepath.exists():
                # Try .html extension
                filepath = src_dir / filename.replace('.htm', '.html')
                if not filepath.exists():
                    continue

            with open(filepath, 'r', encoding='utf-8') as f:
                html_text = f.read()

            try:
                spells = parse_spells_from_html_xgte(html_text, level, source_name)
                for s in spells:
                    key = s["name"]
                    if key not in all_spells:
                        all_spells[key] = s
                        source_count += 1
            except Exception as e:
                print(f"  ERROR parsing {filepath}: {e}")

        print(f"  {source_name}: {source_count} new spells")
        total += source_count

    print(f"\n  Total new spells: {len(all_spells)}")

    # Show by level
    by_level = {}
    for s in all_spells.values():
        lv = s["level"]
        by_level[lv] = by_level.get(lv, 0) + 1
    for lv in sorted(by_level.keys()):
        print(f"    {lv}环: {by_level[lv]}")

    # Write output
    lines = [
        '# Auto-generated. Expansion spells from XGtE + TCoE.',
        f'# Total: {len(all_spells)} spells',
        '',
        '_EXPANSION_SPELLS_LIST = [',
    ]
    for s in sorted(all_spells.values(), key=lambda x: (x["level"], x["name"])):
        json_str = json.dumps(s, ensure_ascii=False)
        # Fix JSON booleans to Python booleans
        json_str = json_str.replace(': true,', ': True,').replace(': false,', ': False,')
        json_str = json_str.replace(': true}', ': True}').replace(': false}', ': False}')
        json_str = json_str.replace(': null,', ': None,').replace(': null}', ': None}')
        lines.append(f'    {json_str},')
    lines.append(']')
    lines.append('')

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f"\n  Written to {OUTPUT}")


if __name__ == "__main__":
    main()
