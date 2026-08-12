"""RULE_SPEC.md 解析器 — 400 条结构化规则点 → 校验语料。

按 `### R-XXX-NNN` 标题切分，每条规则点作为一个 chunk（含摘要/数值公式/出处/函数）。
这是最高信号的校验语料（已审计、含精确公式）。
"""

from __future__ import annotations

import os
import re

# RAG-003/可移植性: 路径由项目根目录派生，不硬编码 Windows 盘符。
# 可用环境变量 AIDM_RULE_SPEC 覆盖。
def _default_spec_path() -> str:
    from ..config import PROJECT_ROOT
    from ..config import get_settings
    return get_settings().aidm_rule_spec or str(PROJECT_ROOT / "aidm" / "docs" / "RULE_SPEC.md")


SPEC_PATH = _default_spec_path()


def parse_rulespec(path: str = SPEC_PATH) -> list[dict]:
    """解析 RULE_SPEC.md → 规则点 payload 列表（注入玩家别名以桥接检索）。"""
    from .aliases import ALIASES
    with open(path, encoding="utf-8") as f:
        text = f.read()
    # 按 "### R-XXX-NNN" 切分（每条规则点一个块）
    parts = re.split(r"\n(?=### R-[A-Z]+-\d+)", text)
    items: list[dict] = []
    for p in parts:
        p = p.strip()
        m = re.match(r"### (R-[A-Z]+-\d+)\s+(.*)", p)
        if not m:
            continue
        rid, title = m.group(1), m.group(2).strip()
        body = p
        # P2.5 别名富化：给机制规则注入玩家同义词，桥接"玩家词↔规则原词"
        if rid in ALIASES:
            body = f"【别名】{ALIASES[rid]}\n" + body
        items.append({
            "body": body,
            "tag": rid,
            "path": "RULE_SPEC.md#" + rid,
            "title": f"{rid} {title}",
        })
    return items


if __name__ == "__main__":
    from . import indexer
    items = parse_rulespec()
    print(f"[parse_rulespec] 解析 {len(items)} 条规则点")
    assert len(items) > 350
    # 建索引 + 校验 demo
    indexer.index_chunks(items, "dnd_rule_spec")
    print()
    q = "摔绊 推撞 力量豁免 倒地"
    print(f"检索 RULE_SPEC: {q}")
    for r in indexer.search_spec(q, limit=3):
        print(f"  [{r['score']:.3f}] {r['title']} | {r['body'][:80]}")
    print("[parse_rulespec] 自检通过 ✓")
