"""规则检索器 — 封装 indexer.search，输出供 LLM/校验使用的格式化规则。

规则: RAG 检索 top-k + 标签过滤（PRD §4 P2 / ARCHITECTURE §5.1）
"""

from __future__ import annotations

from . import indexer


def query_rules(query: str, limit: int = 5, tag_filter: str | None = None) -> list[dict]:
    """语义检索规则条目（top-k，可选标签过滤）。"""
    return indexer.search(query, limit=limit, tag_filter=tag_filter)


def format_for_llm(results: list[dict], body_limit: int = 600) -> str:
    """格式化为给 LLM 的上下文块（带相关度/标签/出处+正文）。"""
    lines: list[str] = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] 相关度 {r.get('score', 0):.2f} | 标签 {r.get('tag', '')!r} | 出处 {r.get('path', '')}")
        lines.append(r.get("body", "")[:body_limit])
        lines.append("")
    return "\n".join(lines)


def query_formatted(query: str, limit: int = 5, body_limit: int = 600) -> str:
    """一步：检索 + 格式化。"""
    return format_for_llm(query_rules(query, limit=limit), body_limit=body_limit)


if __name__ == "__main__":
    q = "擒抱怎么判定 逃脱DC"
    print(f"查询: {q}\n")
    print(query_formatted(q, limit=3))
