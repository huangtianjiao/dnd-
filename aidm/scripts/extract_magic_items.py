"""
Extract magic items from DMG 2024 and DMG 2014 HTML files.
Generates _magic_items_data.py with complete item data.
"""

import re
import os
import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("E:/Project/dnd--master/5echm_web/topics")
OUTPUT = Path("E:/Project/dnd--master/aidm/src/aidm/data/_magic_items_data.py")

# Rarity mapping from filename
RARITY_MAP = {
    "普通": "COMMON",
    "非普通": "UNCOMMON",
    "珍稀": "RARE",
    "极珍稀": "VERY_RARE",
    "传说": "LEGENDARY",
    "神器": "ARTIFACT",
    "多种稀有度": "VARIABLE",
}

# Item type mapping from directory name
TYPE_MAP = {
    "武器": "WEAPON",
    "护甲": "ARMOR",
    "药水": "POTION",
    "戒指": "RING",
    "权杖": "ROD",
    "法杖": "STAFF",
    "魔杖": "WAND",
    "卷轴": "SCROLL",
    "奇物": "WONDROUS",
}

# Sub-type mapping for wondrous items
WONDROUS_SUB_MAP = {
    "其他物品": "WONDROUS",
    "着装品": "WONDROUS_WORN",
    "装饰品": "WONDROUS_ORNAMENT",
}

# Chinese to English rarity for data storage
CN_RARITY_MAP = {
    "普通": "Common",
    "非普通": "Uncommon",
    "珍稀": "Rare",
    "极珍稀": "Very Rare",
    "传说": "Legendary",
    "神器": "Artifact",
}


def clean_html(text):
    """Strip HTML tags and normalize whitespace."""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_dmg2024_file(filepath, item_type, rarity_cn, rarity_en, sub_type=None):
    """Parse DMG 2024 format: <H6>Name EN</H6><P><EM>type, rarity</EM>..."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    items = []

    # Find all H6 + P pairs
    # Pattern: <H6>name</H6><P>content</P>
    pattern = re.compile(
        r'<H6>\s*(.+?)\s*</H6>\s*<P>\s*(.+?)\s*</P>',
        re.DOTALL | re.IGNORECASE
    )

    for match in pattern.finditer(html):
        name_raw = match.group(1)
        p_content = match.group(2)

        # Split name: "中文名 English Name"
        name_text = clean_html(name_raw)
        name_parts = name_text.split()
        if len(name_parts) >= 2:
            # Last word(s) might be English
            en_name = name_parts[-1] if name_parts[-1][0].isascii() else ''
            if en_name:
                cn_name = ' '.join(name_parts[:-1])
            else:
                cn_name = name_text
                en_name = ''
        else:
            cn_name = name_text
            en_name = ''

        # Parse <EM> for type/rarity/attunement
        em_match = re.search(r'<EM>\s*(.+?)\s*</EM>', p_content, re.DOTALL | re.IGNORECASE)
        item_subtype = ''
        attunement = False
        attunement_class = ''

        if em_match:
            em_text = clean_html(em_match.group(1))
            # Format: "武器（标枪），非普通（需同调）"
            # Or: "药水，非普通"
            # First part before comma may contain subtypes
            parts = em_text.split('，')
            if len(parts) >= 1:
                first_part = parts[0]
                # Extract subtype from parentheses
                sub_match = re.search(r'[（(](.+?)[）)]', first_part)
                if sub_match:
                    item_subtype = sub_match.group(1).strip()

            if len(parts) >= 2:
                # Check for attunement requirement
                if '需同调' in em_text:
                    attunement = True
                    # Check for class restriction
                    class_match = re.search(r'需(.+?)同调', em_text)
                    if class_match:
                        restriction = class_match.group(1).strip()
                        if restriction and restriction != '需':
                            attunement_class = restriction

        # Get description (everything after EM or the whole P content)
        desc_start = em_match.end() if em_match else 0
        desc_raw = p_content[desc_start:]
        description = clean_html(desc_raw)
        # Remove leading BR tags content
        description = re.sub(r'^[，,\s]*', '', description)

        # Remove trailing BR-like content
        description = description.strip()

        # Skip if description is just a table or empty
        if not description or len(description) < 5:
            continue

        items.append({
            "name": cn_name,
            "en_name": en_name,
            "type": item_type,
            "sub_type": item_subtype,
            "rarity_cn": rarity_cn,
            "rarity": rarity_en,
            "attunement": attunement,
            "attunement_class": attunement_class,
            "description": description,
            "source": "DMG 2024",
        })

    return items


def parse_dmg2014_file(filepath, item_type, rarity_cn, rarity_en, sub_type=None):
    """Parse DMG 2014 format: <P><STRONG><FONT>Name EN</FONT></STRONG><BR><EM>type</EM>..."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    items = []

    # Each item is in its own <P> block
    # Find all P blocks
    p_pattern = re.compile(r'<P>\s*(.+?)\s*</P>', re.DOTALL | re.IGNORECASE)

    for match in p_pattern.finditer(html):
        p_content = match.group(1)

        # Check for name: <STRONG><FONT>Name EN</FONT></STRONG>
        name_match = re.search(
            r'<STRONG>\s*<FONT[^>]*>\s*(.+?)\s*</FONT>\s*</STRONG>',
            p_content, re.DOTALL | re.IGNORECASE
        )
        if not name_match:
            # Try alternative: just STRONG without FONT
            name_match = re.search(
                r'<STRONG>\s*(.+?)\s*</STRONG>',
                p_content, re.DOTALL | re.IGNORECASE
            )
        if not name_match:
            continue

        name_raw = name_match.group(1)
        name_text = clean_html(name_raw)

        # Split name
        name_parts = name_text.split()
        if len(name_parts) >= 2:
            en_name = name_parts[-1] if name_parts[-1][0].isascii() else ''
            if en_name:
                cn_name = ' '.join(name_parts[:-1])
            else:
                cn_name = name_text
                en_name = ''
        else:
            cn_name = name_text
            en_name = ''

        # Parse <EM> for type/rarity
        em_match = re.search(r'<EM>\s*(.+?)\s*</EM>', p_content, re.DOTALL | re.IGNORECASE)
        item_subtype = ''
        attunement = False
        attunement_class = ''

        if em_match:
            em_text = clean_html(em_match.group(1))
            parts = em_text.split('，')
            if len(parts) >= 1:
                sub_match = re.search(r'[（(](.+?)[）)]', parts[0])
                if sub_match:
                    item_subtype = sub_match.group(1).strip()
            if '需同调' in em_text:
                attunement = True
                class_match = re.search(r'需(.+?)同调', em_text)
                if class_match:
                    restriction = class_match.group(1).strip()
                    if restriction and restriction != '需':
                        attunement_class = restriction

        # Get description
        desc_start = em_match.end() if em_match else name_match.end()
        desc_raw = p_content[desc_start:]
        description = clean_html(desc_raw)

        if not description or len(description) < 5:
            continue

        items.append({
            "name": cn_name,
            "en_name": en_name,
            "type": item_type,
            "sub_type": item_subtype,
            "rarity_cn": rarity_cn,
            "rarity": rarity_en,
            "attunement": attunement,
            "attunement_class": attunement_class,
            "description": description,
            "source": "DMG 2014",
        })

    return items


def extract_all():
    """Extract all magic items from both DMG versions."""
    all_items = []

    # === DMG 2024 ===
    dmg2024_base = BASE_DIR / "城主指南2024" / "7.宝藏" / "魔法物品详述"

    for type_dir_name, item_type in TYPE_MAP.items():
        type_path = dmg2024_base / type_dir_name
        if not type_path.exists():
            continue

        if type_dir_name == "奇物":
            # Has sub-sub-directories: 其他物品, 着装品, 装饰品
            for sub_dir in type_path.iterdir():
                if not sub_dir.is_dir():
                    continue
                sub_type = WONDROUS_SUB_MAP.get(sub_dir.name, "WONDROUS")
                for rarity_file in sub_dir.glob("*.htm"):
                    rarity_cn = rarity_file.stem
                    rarity_en = RARITY_MAP.get(rarity_cn, "COMMON")
                    items = parse_dmg2024_file(
                        rarity_file, item_type, rarity_cn, rarity_en, sub_type
                    )
                    all_items.extend(items)
        else:
            for rarity_file in type_path.glob("*.htm"):
                rarity_cn = rarity_file.stem
                rarity_en = RARITY_MAP.get(rarity_cn, "COMMON")
                items = parse_dmg2024_file(
                    rarity_file, item_type, rarity_cn, rarity_en
                )
                all_items.extend(items)

    # === DMG 2014 ===
    dmg2014_base = BASE_DIR / "城主指南" / "宝藏" / "魔法物品"

    for type_dir_name, item_type in TYPE_MAP.items():
        type_path = dmg2014_base / type_dir_name
        if not type_path.exists():
            continue

        if type_dir_name == "奇物":
            for rarity_file in type_path.glob("*.htm"):
                if rarity_file.stem in RARITY_MAP:
                    rarity_cn = rarity_file.stem
                    rarity_en = RARITY_MAP[rarity_cn]
                    items = parse_dmg2014_file(
                        rarity_file, item_type, rarity_cn, rarity_en
                    )
                    all_items.extend(items)
            for rarity_file in type_path.glob("*.html"):
                if rarity_file.stem in RARITY_MAP:
                    rarity_cn = rarity_file.stem
                    rarity_en = RARITY_MAP[rarity_cn]
                    items = parse_dmg2014_file(
                        rarity_file, item_type, rarity_cn, rarity_en
                    )
                    all_items.extend(items)
        else:
            for rarity_file in type_path.glob("*.htm"):
                if rarity_file.stem in RARITY_MAP:
                    rarity_cn = rarity_file.stem
                    rarity_en = RARITY_MAP[rarity_cn]
                    items = parse_dmg2014_file(
                        rarity_file, item_type, rarity_cn, rarity_en
                    )
                    all_items.extend(items)
            for rarity_file in type_path.glob("*.html"):
                if rarity_file.stem in RARITY_MAP:
                    rarity_cn = rarity_file.stem
                    rarity_en = RARITY_MAP[rarity_cn]
                    items = parse_dmg2014_file(
                        rarity_file, item_type, rarity_cn, rarity_en
                    )
                    all_items.extend(items)

    # Also check the "魔法物品详述" subdir in DMG 2014
    detail_path = dmg2014_base / "魔法物品详述"
    if detail_path.exists():
        for html_file in detail_path.glob("*.htm"):
            # These are all WONDROUS items
            items = parse_dmg2014_file(html_file, "WONDROUS", "多种稀有度", "VARIABLE")
            all_items.extend(items)

    return all_items


def deduplicate(items):
    """Remove duplicate items (same name from both DMG versions). Keep DMG 2024 version."""
    seen = {}
    for item in items:
        key = item["name"]
        if key in seen:
            # Keep DMG 2024 over DMG 2014
            if item["source"] == "DMG 2024":
                seen[key] = item
        else:
            seen[key] = item
    return list(seen.values())


def main():
    print("Extracting magic items...")
    all_items = extract_all()
    print(f"  Extracted {len(all_items)} items (before dedup)")

    items = deduplicate(all_items)
    print(f"  After dedup: {len(items)} items")

    # Stats
    by_type = defaultdict(int)
    by_rarity = defaultdict(int)
    by_source = defaultdict(int)
    for item in items:
        by_type[item["type"]] += 1
        by_rarity[item["rarity_cn"]] += 1
        by_source[item["source"]] += 1

    print("\n  By type:")
    for t, n in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"    {t}: {n}")
    print("\n  By rarity:")
    for r, n in sorted(by_rarity.items(), key=lambda x: -x[1]):
        print(f"    {r}: {n}")
    print("\n  By source:")
    for s, n in sorted(by_source.items()):
        print(f"    {s}: {n}")

    # Generate output
    output_lines = [
        '# Auto-generated by extract_magic_items.py. DO NOT EDIT.',
        f'# Source: 5echm_web DMG 2024 + DMG 2014',
        f'# Total items: {len(items)}',
        '',
        '_MAGIC_ITEMS_LIST = [',
    ]

    for item in sorted(items, key=lambda x: (x["type"], x["name"])):
        # json.dumps outputs "true"/"false", need to replace with Python's True/False
        json_str = json.dumps(item, ensure_ascii=False)
        json_str = json_str.replace(': true,', ': True,').replace(': false,', ': False,')
        json_str = json_str.replace(': true}', ': True}').replace(': false}', ': False}')
        output_lines.append(f'    {json_str},')

    output_lines.append(']')
    output_lines.append('')

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text('\n'.join(output_lines), encoding='utf-8')
    print(f"\n  Written to {OUTPUT}")
    print(f"  File size: {OUTPUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
