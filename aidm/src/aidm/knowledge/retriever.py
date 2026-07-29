"""规则检索器 — 封装 indexer.search，输出供 LLM/校验使用的格式化规则。

规则: RAG 检索 top-k + 标签过滤（PRD §4 P2 / ARCHITECTURE §5.1）
"""

from __future__ import annotations

from . import indexer

# 模组内容 tag 前缀：命中时对 LLM 标注防剧透（DM 可参考，勿直接向玩家泄露谜底）
SPOILER_TAG_PREFIX = "模组/"
SPOILER_NOTICE = (
    "⚠ 模组内容（仅供 DM 参考：仅供幕后使用，"
    "向玩家叙述时不得泄露模组谜底、陷阱位置、Boss 弱点等未揭露信息）"
)


def query_rules(query: str, limit: int = 5, tag_filter: str | None = None) -> list[dict]:
    """语义检索规则条目（top-k，可选标签过滤）。"""
    return indexer.search(query, limit=limit, tag_filter=tag_filter)


def format_for_llm(results: list[dict], body_limit: int = 600) -> str:
    """格式化为给 LLM 的上下文块（带相关度/标签/出处+正文）。"""
    lines: list[str] = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] 相关度 {r.get('score', 0):.2f} | 标签 {r.get('tag', '')!r} | 出处 {r.get('path', '')}")
        tag = str(r.get("tag", "")).replace("\\", "/")
        if tag.startswith(SPOILER_TAG_PREFIX):
            lines.append(SPOILER_NOTICE)
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
