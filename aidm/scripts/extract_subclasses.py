"""从 5echm_web 子职业 HTML 提取结构化数据。

来源: topics/玩家手册2024/角色职业/<职业>/<子职业>.htm
输出: aidm/data/_subclasses_data.py
"""

import json
import os
import re
import sys
from pathlib import Path

HTML_DIR = Path("E:/Project/dnd--master/5echm_web/topics/玩家手册2024/角色职业")
OUTPUT = Path("E:/Project/dnd--master/aidm/src/aidm/data/_subclasses_data.py")


def extract_features(html: str) -> list[dict]:
    """从 HTML 中提取子职业特性列表。

    每个特性格式:
      <p><STRONG><FONT color=#800000>X级：特性名 EnglishName</FONT></STRONG><BR>描述</p>
    """
    features = []

    # Find all feature paragraphs: level: name pattern inside STRONG tag
    # Pattern: X级：name EnglishName
    # Three closing patterns observed in wild:
    #   A: </FONT></STRONG><BR>desc</p>  (most common)
    #   B: </FONT><BR></STRONG>desc</p>  (魅心学院, 世界树道途 etc.)
    #   C: </STRONG></FONT><BR>desc</p>  (FONT outside STRONG)
    # Also handle: <BR> inside FONT before level number (盗贼)
    feature_pattern = re.compile(
        r'<p>\s*'
        r'(?:<STRONG>\s*<FONT[^>]*>|<FONT[^>]*>\s*<STRONG>)\s*'
        r'(?:<BR[^>]*>\s*)?'  # optional BR before level (盗贼格式)
        r'(\d+)级[：:]\s*(.+?)'
        r'\s*</FONT>\s*'
        r'(?:</STRONG>\s*(?:<BR[^>]*>)?|(?:<BR[^>]*>)?\s*</STRONG>)\s*'
        r'(?:\s*<BR[^>]*>\s*)?'
        r'(.*?)'
        r'</p>',
        re.DOTALL | re.IGNORECASE
    )

    for match in feature_pattern.finditer(html):
        level = int(match.group(1))
        raw_name_line = match.group(2).strip()
        desc_raw = match.group(3).strip()

        # Split name into Chinese and English parts
        # Format: "特性名 EnglishName" with possible newlines
        # Strategy: find where Chinese characters end and English starts
        cleaned = raw_name_line.replace('\n', ' ').strip()
        # Match: Chinese chars and spaces, then English words
        m = re.match(r'^([\u4e00-\u9fff\s]+)\s+([A-Za-z].*)$', cleaned)
        if m:
            cn_name = m.group(1).strip()
            en_name = m.group(2).strip()
        else:
            # Fallback: last word is English
            name_parts = cleaned.split()
            if len(name_parts) >= 2 and re.match(r'[A-Za-z]', name_parts[-1]):
                en_name = name_parts[-1]
                cn_name = ' '.join(name_parts[:-1])
            else:
                cn_name = cleaned
                en_name = ''

        # Clean description: strip HTML tags for summary
        desc_clean = re.sub(r'<[^>]+>', ' ', desc_raw)
        desc_clean = re.sub(r'\s+', ' ', desc_clean).strip()

        # Trim to reasonable length for description
        if len(desc_clean) > 200:
            desc_short = desc_clean[:197] + '...'
        else:
            desc_short = desc_clean

        features.append({
            "level": level,
            "name": cn_name,
            "en_name": en_name,
            "description": desc_short,
        })

    return features


def parse_subclass(filepath: Path, class_name: str) -> dict | None:
    """解析单个子职业 HTML 文件。"""
    if not filepath.exists():
        print(f"  [SKIP] 文件不存在: {filepath}")
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Extract title
    title_match = re.search(r'<title>(.+?)</title>', html)
    if not title_match:
        print(f"  [SKIP] 无标题: {filepath}")
        return None
    title = title_match.group(1).strip()

    # Extract h2: name + en_name
    h2_match = re.search(r'<h2>\s*<FONT[^>]*>\s*(.+?)\s*</FONT>\s*</h2>', html, re.DOTALL | re.IGNORECASE)
    if h2_match:
        h2_text = h2_match.group(1).strip()
        h2_text = re.sub(r'\s+', ' ', h2_text)
        # Split at Chinese/English boundary
        m = re.match(r'^([\u4e00-\u9fff\s]+)\s+([A-Za-z].*)$', h2_text)
        if m:
            cn_name = m.group(1).strip()
            en_name = m.group(2).strip()
        else:
            parts = h2_text.split()
            if len(parts) >= 2 and re.match(r'[A-Za-z]', parts[-1]):
                en_name = parts[-1]
                cn_name = ' '.join(parts[:-1])
            else:
                cn_name = h2_text
                en_name = ''
    else:
        cn_name = title
        en_name = ''

    # Flavor text
    flavor_match = re.search(r'<p class=sum>(.+?)</p>', html)
    flavor = flavor_match.group(1).strip() if flavor_match else ''

    # Features
    features = extract_features(html)

    if not features:
        print(f"  [WARN] 无特性: {filepath}")

    return {
        "name": cn_name,
        "en_name": en_name,
        "class_name": class_name,
        "flavor": flavor,
        "features": features,
    }


def main():
    results = {}
    total = 0
    failed = 0

    for class_dir in sorted(HTML_DIR.iterdir()):
        if not class_dir.is_dir():
            continue

        class_name = class_dir.name
        subclass_files = sorted(class_dir.glob("*.htm"))

        # Filter: only subclass files (not main class file, not spell lists)
        # Main class files are named exactly like the class (e.g., 法师.htm)
        main_files = {f"{class_name}.htm"}
        skip_patterns = ["法术列表", "战技项", "魔能祈唤", "超魔法", "战斗风格"]

        for sf in subclass_files:
            if sf.name in main_files:
                continue
            if any(p in sf.name for p in skip_patterns):
                continue

            print(f"Parsing: {class_name}/{sf.stem}...", end=" ")
            data = parse_subclass(sf, class_name)
            if data:
                key = f"{class_name}/{data['name']}"
                results[key] = data
                total += 1
                print(f"OK ({len(data['features'])} features)")
            else:
                failed += 1
                print("FAILED")

    print(f"\n=== 解析完成: {total} 个子职业, {failed} 失败 ===")

    # Generate Python data file
    lines = [
        '"""子职业数据表（自动生成）。',
        '',
        f'来源: topics/玩家手册2024/角色职业/<职业>/<子职业>.htm',
        f'子职业总数: {total}',
        f'生成脚本: aidm/scripts/extract_subclasses.py',
        '"""',
        '',
        '# flake8: noqa: E501',
        '',
        '_SUBCLASSES_LIST: list[dict] = [',
    ]

    for key, data in sorted(results.items()):
        lines.append(f"    # ── {data['class_name']}: {data['name']} ──")
        lines.append(f"    {{")
        lines.append(f"        'name': {json.dumps(data['name'], ensure_ascii=False)},")
        lines.append(f"        'en_name': {json.dumps(data['en_name'], ensure_ascii=False)},")
        lines.append(f"        'class_name': {json.dumps(data['class_name'], ensure_ascii=False)},")
        lines.append(f"        'flavor': {json.dumps(data['flavor'], ensure_ascii=False)},")
        lines.append(f"        'features': [")
        for feat in data['features']:
            lines.append(f"            {{'level': {feat['level']}, "
                         f"'name': {json.dumps(feat['name'], ensure_ascii=False)}, "
                         f"'en_name': {json.dumps(feat['en_name'], ensure_ascii=False)}, "
                         f"'description': {json.dumps(feat['description'], ensure_ascii=False)}}},")
        lines.append(f"        ],")
        lines.append(f"    }},")

    lines.append("]")

    os.makedirs(OUTPUT.parent, exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"\n输出: {OUTPUT}")


if __name__ == "__main__":
    main()
