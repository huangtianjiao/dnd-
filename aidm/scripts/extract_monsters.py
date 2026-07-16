#!/usr/bin/env python3
"""从 5echm_web 怪物图鉴2025 提取怪物数据。

解析 2025 版 stat-block 格式的 HTML，生成 _monsters_data.py。
"""

import re
import json
import html as html_mod
from pathlib import Path
from typing import Optional

# ── 项目路径 ──
WEB_DIR = Path(r"E:\Project\dnd--master\5echm_web\topics\怪物图鉴2025")
OUTPUT = Path(r"E:\Project\dnd--master\aidm\src\aidm\data\_monsters_data.py")
SKIP_DIRS = {"附录A", "附录B", "前言", "引言"}


def extract_div_content(html: str, class_name: str) -> Optional[str]:
    """提取指定 class 的 div 内容，正确处理嵌套 div。"""
    # 找到 class="class_name" 的 div 起始
    pattern = re.compile(rf'<div\s+class=["\'\s]*{class_name}["\'\s]', re.I)
    m = pattern.search(html)
    if not m:
        return None

    div_start = html.rfind('<div', 0, m.start())
    content_start = html.find('>', m.start()) + 1

    # 跟踪嵌套深度
    depth = 1
    pos = content_start
    while depth > 0 and pos < len(html):
        next_open = html.find('<div', pos)
        next_close = html.find('</div>', pos)

        if next_open >= 0 and (next_open < next_close or next_close < 0):
            depth += 1
            pos = next_open + 4
        elif next_close >= 0:
            depth -= 1
            if depth == 0:
                return html[content_start:next_close]
            pos = next_close + 6
        else:
            break
    return None


def strip_html(text: str) -> str:
    """移除 HTML 标签，保留纯文本。"""
    # 先处理 <br> / <BR>
    text = re.sub(r'<br\s*/?\s*>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    # 解码 HTML 实体
    text = html_mod.unescape(text)
    # 清理多余空白
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text


def extract_stat_block(html_content: str) -> Optional[dict]:
    """从 HTML 内容中提取 stat-block 数据。"""
    # 找到 stat-block div（正确处理嵌套 div）
    sb = extract_div_content(html_content, "stat-block")
    if not sb:
        return None

    monster = {}

    # ── 名称 ──
    h5_m = re.search(r'<h5>(.*?)</h5>', sb, re.S | re.I)
    if not h5_m:
        return None
    name_text = strip_html(h5_m.group(1)).strip()
    # 中文名 和 英文名分离（英文名可能在中文名后面紧跟着）
    # 例如 "巫妖Lich" 或 "幽影 Shadow"
    name_parts = re.match(r'(.+?)\s*([A-Z][a-zA-Z\s\-\']+)$', name_text)
    if name_parts:
        monster["name"] = name_parts.group(1).strip()
        monster["en_name"] = name_parts.group(2).strip()
    else:
        monster["name"] = name_text
        monster["en_name"] = ""

    # ── 体型/类型/阵营 ──
    sub_m = re.search(r'<div class="sub-line">(.*?)</div>', sb, re.S | re.I)
    if sub_m:
        type_line = strip_html(sub_m.group(1)).strip()
        monster["type_line"] = type_line
        # 解析: "中型亡灵（法师），中立邪恶"
        # 或: "大型龙类，混乱邪恶"
        size_types = {
            "微型": "Tiny", "小型": "Small", "中型": "Medium",
            "大型": "Large", "巨型": "Huge", "超巨型": "Gargantuan",
            "任意": "Any",
        }
        monster["size"] = "中型"
        for cn, en in size_types.items():
            if cn in type_line:
                monster["size"] = en
                break

        # 类型和阵营
        rest = type_line[len(monster.get("size_cn", "中型")):].strip()
        # 中文 size 可能不在 size_types 中，直接取匹配
        size_cn = ""
        for cn in size_types:
            if type_line.startswith(cn):
                size_cn = cn
                break
        if not size_cn and type_line:
            # 取"任意"开头的特殊情况
            for cn in ["任意"]:
                if type_line.startswith(cn):
                    size_cn = cn
                    break

        monster["size"] = size_types.get(size_cn, "Medium")
        rest = type_line[len(size_cn):].strip()

        # 分离类型和阵营
        # 类型可能有括号子类型: "亡灵（法师）"
        ali_parts = rest.split("，")
        type_part = ali_parts[0] if ali_parts else rest
        monster["creature_type"] = type_part.strip()
        if len(ali_parts) > 1:
            monster["alignment"] = ali_parts[-1].strip()
        else:
            monster["alignment"] = ""

    # ── 表格数据 ──
    # 解析所有 <table>（包含属性和内容）
    tables = re.findall(r'(<table[^>]*>.*?</table>)', sb, re.S | re.I)

    for table_full in tables:
        # 提取 table 属性和内容
        tag_match = re.match(r'<table([^>]*)>(.*)</table>', table_full, re.S | re.I)
        if not tag_match:
            continue
        table_attrs = tag_match.group(1)
        table_html = tag_match.group(2)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.S | re.I)

        # 检查是否为 stat-abilities 表
        if 'stat-abilities' in table_attrs:
                # 属性表 - 两行: 力量/敏捷/体质, 智力/感知/魅力
                # 每组5个单元格: [属性名, 值, 调整, 豁免, 分隔空td]
                abilities = {}
                for row_html in rows:
                    cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row_html, re.S | re.I)
                    cell_texts = [strip_html(c) for c in cells]

                    # 跳过标题行
                    if any(t in ('调整', '豁免') for t in cell_texts):
                        continue

                    # 每组5个：属性名, 值, 调整, 豁免, 分隔td
                    i = 0
                    while i + 3 < len(cell_texts):
                        ability_name = cell_texts[i]
                        if ability_name in ("力量", "敏捷", "体质", "智力", "感知", "魅力"):
                            ability_val = cell_texts[i + 1]
                            ability_mod = cell_texts[i + 2]
                            ability_save = cell_texts[i + 3] if i + 3 < len(cell_texts) and cell_texts[i + 3] else ""

                            try:
                                score = int(ability_val)
                            except ValueError:
                                score = 10
                            mod_val = ability_mod.replace("+", "").strip()
                            try:
                                mod_val = int(mod_val)
                            except ValueError:
                                mod_val = (score - 10) // 2
                            save_val = ability_save.replace("+", "").strip()
                            try:
                                save_val = int(save_val)
                            except ValueError:
                                save_val = mod_val

                            abilities[ability_name] = {
                                "score": score,
                                "mod": mod_val,
                                "save": save_val,
                            }
                        i += 5  # 每组5个单元格（含分隔td）
                monster["abilities"] = abilities
                continue

        # 普通属性表
        for row_html in rows:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row_html, re.S | re.I)
            if not cells:
                continue
            cell_text = strip_html(' '.join(cells)).strip()

            # ── AC / 先攻 ──
            # 格式: "AC 20" "先攻 +17（27）"
            for cell_html in cells:
                ct = strip_html(cell_html)
                if ct.startswith("AC "):
                    # AC 20（天生护甲）
                    ac_match = re.match(r'AC\s+(\d+)(?:（(.+?)）)?', ct)
                    if ac_match:
                        monster["ac"] = int(ac_match.group(1))
                        if ac_match.group(2):
                            monster["ac_desc"] = ac_match.group(2).strip()
                elif ct.startswith("先攻 "):
                    init_match = re.match(r'先攻\s*\+?([\d\-]+)(?:（(\d+)）)?', ct)
                    if init_match:
                        monster["initiative_bonus"] = int(init_match.group(1))
                        if init_match.group(2):
                            monster["initiative_total"] = int(init_match.group(2))

            # ── HP ──
            if cell_text.startswith("HP "):
                hp_text = cell_text[3:].strip()
                hp_match = re.match(r'(\d+)(?:（(.+?)）)?', hp_text)
                if hp_match:
                    monster["hp"] = int(hp_match.group(1))
                    if hp_match.group(2):
                        monster["hp_formula"] = hp_match.group(2).strip()

            # ── 速度 ──
            elif cell_text.startswith("速度 "):
                speed_text = cell_text[3:].strip()
                monster["speed"] = {"walk": speed_text}

            # ── 技能 ──
            elif cell_text.startswith("技能 "):
                skills_text = cell_text[3:].strip()
                monster["skills"] = parse_proficiency_list(skills_text)

            # ── 易伤 ──
            elif cell_text.startswith("易伤 "):
                vuln_text = cell_text[3:].strip()
                monster["damage_vulnerabilities"] = [v.strip() for v in vuln_text.split("，") if v.strip()]

            # ── 抗性 ──
            elif cell_text.startswith("抗性 "):
                resist_text = cell_text[3:].strip()
                monster["damage_resistances"] = [r.strip() for r in resist_text.split("，") if r.strip()]

            # ── 免疫 ──
            elif cell_text.startswith("免疫 "):
                immune_text = cell_text[3:].strip()
                # 分号分隔伤害免疫和状态免疫
                parts = immune_text.split("；")
                if parts:
                    monster["damage_immunities"] = [i.strip() for i in parts[0].split("，") if i.strip()]
                if len(parts) > 1:
                    monster["condition_immunities"] = [i.strip() for i in parts[1].split("，") if i.strip()]

            # ── 装备 ──
            elif cell_text.startswith("装备 "):
                gear_text = cell_text[3:].strip()
                if gear_text:
                    monster["equipment"] = gear_text

            # ── 感官 ──
            elif cell_text.startswith("感官 "):
                senses_text = cell_text[3:].strip()
                monster["senses"] = parse_senses(senses_text)

            # ── 语言 ──
            elif cell_text.startswith("语言 "):
                lang_text = cell_text[3:].strip()
                monster["languages"] = lang_text

            # ── CR ──
            elif cell_text.startswith("CR "):
                cr_text = cell_text[3:].strip()
                # 格式: "21（XP33,000，或巢穴内41,000；PB+7）"
                cr_match = re.match(r'(\d+(?:/\d+)?)', cr_text)
                if cr_match:
                    cr_str = cr_match.group(1)
                    monster["cr"] = cr_str if '/' in cr_str else int(cr_str)

                xp_match = re.search(r'XP\s*([\d,]+)', cr_text)
                if xp_match:
                    monster["xp"] = int(xp_match.group(1).replace(",", ""))

                pb_match = re.search(r'PB\s*\+\s*(\d+)', cr_text)
                if pb_match:
                    monster["pb"] = int(pb_match.group(1))

    # ── 特质/动作/传奇动作等 ──
    # 解析 h6 标题和后面的 <p> 内容
    sections = {}
    current_section = None

    # 使用更精确的解析: 依次找 h6 和后续的 p
    h6_pattern = re.compile(
        r'<h6>(.*?)</h6>\s*(<p[^>]*>(.*?)</p>)',
        re.S | re.I
    )

    pos = 0
    for match in h6_pattern.finditer(sb):
        if match.start() < pos:
            continue
        pos = match.end()

        section_title = strip_html(match.group(1)).strip()
        section_content_html = match.group(2)

        if "特质" in section_title:
            sections["traits"] = parse_traits_actions(section_content_html)
        elif "动作" in section_title and "传奇" not in section_title and "附赠" not in section_title:
            sections["actions"] = parse_traits_actions(section_content_html)
        elif "附赠" in section_title:
            sections["bonus_actions"] = parse_traits_actions(section_content_html)
        elif "反应" in section_title:
            sections["reactions"] = parse_traits_actions(section_content_html)
        elif "传奇动作" in section_title:
            sections["legendary_actions"] = parse_legendary_actions(section_content_html)

    monster.update(sections)

    # ── 巢穴动作（在 stat-block 外但紧接其后） ──
    # 在 body 中找巢穴动作
    lair_pattern = re.search(
        r'(?:巢穴动作|Lair\s*Actions)[^<]*?</(?:h\d|H\d)>\s*<[pP][^>]*>(.*?)(?:</[pP]>|$)',
        html_content, re.S | re.I
    )
    if lair_pattern:
        lair_text = strip_html(lair_pattern.group(1))
        monster["lair_actions"] = lair_text[:500]

    return monster


def parse_proficiency_list(text: str) -> dict:
    """解析技能熟练列表: "奥秘+19，历史+12" -> {"奥秘": 19, "历史": 12}"""
    result = {}
    for item in re.split(r'[，,]', text):
        item = item.strip()
        match = re.match(r'(.+?)\s*([+\-]\d+)', item)
        if match:
            result[match.group(1).strip()] = int(match.group(2))
    return result


def parse_senses(text: str) -> dict:
    """解析感官: "真实视觉120尺；被动察觉19" -> {"真实视觉": "120尺", "被动察觉": 19}"""
    result = {}
    for part in text.split("；"):
        part = part.strip()
        # 尝试 "名称 距离" 格式
        match = re.match(r'(.+?)\s*(\d+)\s*尺?', part)
        if match:
            name = match.group(1).strip()
            val = match.group(2)
            try:
                result[name] = int(val)
            except ValueError:
                result[name] = val
        else:
            # 被动察觉特殊处理
            pp_match = re.match(r'被动察觉\s*(\d+)', part)
            if pp_match:
                result["被动察觉"] = int(pp_match.group(1))
    return result


def parse_traits_actions(html_content: str) -> list:
    """解析特质/动作列表。

    格式: <strong>名称English Name（参数）。</strong>描述...<br>
    """
    result = []
    # 按 <br> 分割
    items = re.split(r'<\s*br\s*/?\s*>', html_content, flags=re.I)

    for item in items:
        item = item.strip()
        if not item:
            continue

        # 提取 strong 标签中的名称
        strong_match = re.search(r'<\s*strong[^>]*>(.*?)</\s*strong\s*>', item, re.S | re.I)
        if not strong_match:
            # 可能是纯文本或法术列表，跳过
            continue

        name_block = strong_match.group(1)
        rest = item[strong_match.end():]

        # 清理名称中的 HTML
        name_clean = strip_html(name_block).strip()
        # 移除末尾的句号
        name_clean = re.sub(r'[。.]$', '', name_clean)

        # 分离中英文名称
        # 格式: "多重攻击Multiattack" 或 "魔能迸裂Eldritch Burst"
        # 或 "传奇抗性Legendary Resistance（4/日）"
        name_match = re.match(r'(.+?)([A-Z][a-zA-Z\s\-/()]*)(?:[（(](.+?)[）)])?', name_clean)
        if name_match:
            cn_name = name_match.group(1).strip()
            en_name = name_match.group(2).strip()
            params = name_match.group(3)
        else:
            cn_name = name_clean
            en_name = ""
            params = None

        # 清理描述
        desc = strip_html(rest).strip()
        if desc.startswith("。"):
            desc = desc[1:].strip()

        entry = {
            "name": cn_name,
            "en_name": en_name,
            "description": desc[:800],  # 限制长度
        }
        if params:
            entry["params"] = params
        result.append(entry)

    return result


def parse_legendary_actions(html_content: str) -> list:
    """解析传奇动作。先提取次数说明，再解析各动作。"""
    result = []
    # 提取次数说明
    uses_match = re.search(r'传奇动作次数[：:]\s*(\d+)', html_content)
    max_uses = int(uses_match.group(1)) if uses_match else 3

    # 移除次数说明行，按 <br> 分割
    # 先提取 <font> 内的说明
    font_match = re.search(r'<font[^>]*>(.*?)</font>', html_content, re.S | re.I)
    remaining = html_content
    if font_match:
        remaining = html_content[font_match.end():]

    items = re.split(r'<\s*br\s*/?\s*>', remaining, flags=re.I)

    for item in items:
        item = item.strip()
        if not item:
            continue

        strong_match = re.search(r'<\s*strong[^>]*>(.*?)</\s*strong\s*>', item, re.S | re.I)
        if not strong_match:
            continue

        name_block = strong_match.group(1)
        rest = item[strong_match.end():]

        name_clean = strip_html(name_block).strip()
        name_clean = re.sub(r'[。.]$', '', name_clean)

        name_match = re.match(r'(.+?)([A-Z][a-zA-Z\s\-/()]*)(?:[（(](.+?)[）)])?', name_clean)
        if name_match:
            cn_name = name_match.group(1).strip()
            en_name = name_match.group(2).strip()
            params = name_match.group(3)
        else:
            cn_name = name_clean
            en_name = ""
            params = None

        desc = strip_html(rest).strip()
        if desc.startswith("。"):
            desc = desc[1:].strip()

        entry = {
            "name": cn_name,
            "en_name": en_name,
            "description": desc[:800],
            "max_uses": max_uses,
        }
        if params:
            entry["cost"] = int(params.split("/")[0]) if params and "/" in params else 1
        result.append(entry)

    return result


# ═══════════════════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════════════════

def main():
    all_monsters = []
    errors = []

    # 遍历所有 HTML 文件
    html_files = list(WEB_DIR.rglob("*.htm*"))

    # 过滤不需要的文件
    skip_patterns = [
        r'总\.htm',  # "丧尸总.htm" 等汇总页
        r'Credits\.htm',
        r'怪物清单\.htm',
    ]
    skip_dirs = {WEB_DIR / d for d in SKIP_DIRS}

    valid_files = []
    for f in html_files:
        # 跳过某些目录
        if any(sd in f.parents for sd in skip_dirs):
            continue
        # 跳过模式匹配
        if any(re.search(p, f.name) for p in skip_patterns):
            continue
        valid_files.append(f)

    print(f"发现 {len(valid_files)} 个怪物文件（已排除 {len(html_files) - len(valid_files)} 个汇总/索引文件）")

    for f in valid_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()

            monster = extract_stat_block(content)
            if monster and monster.get("name"):
                monster["source_file"] = str(f.relative_to(WEB_DIR))
                all_monsters.append(monster)
            else:
                # 检查是否有stat-block
                if 'stat-block' in content:
                    errors.append(f"解析失败(有stat-block但未提取): {f.relative_to(WEB_DIR)}")
        except Exception as e:
            errors.append(f"异常 {f.relative_to(WEB_DIR)}: {e}")

    print(f"\n成功提取: {len(all_monsters)} 只怪物")
    if errors:
        print(f"失败/警告: {len(errors)} 个")
        for e in errors[:10]:
            print(f"  - {e}")

    # ── 写入数据文件 ──
    with open(OUTPUT, 'w', encoding='utf-8') as fh:
        fh.write('"""从 5echm_web 怪物图鉴2025 自动提取的怪物数据。\n')
        fh.write(f'共 {len(all_monsters)} 只怪物。\n')
        fh.write(f'由 scripts/extract_monsters.py 自动生成，请勿手动编辑。\n')
        fh.write('"""\n\n')
        fh.write('from typing import Any\n\n')
        fh.write(f'_MONSTERS_LIST: list[dict[str, Any]] = ')
        fh.write(json.dumps(all_monsters, ensure_ascii=False, indent=2))
        fh.write('\n\n')
        fh.write(f'MONSTERS: dict[str, dict] = {{m["name"]: m for m in _MONSTERS_LIST}}\n')
        fh.write(f'EN_MONSTERS: dict[str, dict] = {{m["en_name"]: m for m in _MONSTERS_LIST if m.get("en_name")}}\n')
        fh.write(f'CR_MONSTERS: dict[str, list[dict]] = {{}}\n')
        fh.write('for m in _MONSTERS_LIST:\n')
        fh.write('    cr_key = str(m.get("cr", "?"))\n')
        fh.write('    CR_MONSTERS.setdefault(cr_key, []).append(m)\n')

    print(f"\n数据已写入: {OUTPUT}")
    print(f"文件大小: {OUTPUT.stat().st_size:,} bytes")

    # ── 统计 ──
    cr_dist = {}
    for m in all_monsters:
        cr = str(m.get("cr", "?"))
        cr_dist[cr] = cr_dist.get(cr, 0) + 1

    print(f"\nCR 分布:")
    for cr in sorted(cr_dist.keys(), key=lambda x: (int(x.split('/')[0]) if '/' not in x else float(x.split('/')[0])/float(x.split('/')[1]) if '/' in x else 999)):
        print(f"  CR {cr}: {cr_dist[cr]} 只")

    types = {}
    for m in all_monsters:
        t = m.get("creature_type", "未知")
        types[t] = types.get(t, 0) + 1
    print(f"\n类型分布 (top 15):")
    for t, c in sorted(types.items(), key=lambda x: -x[1])[:15]:
        print(f"  {t}: {c} 只")


if __name__ == "__main__":
    main()
