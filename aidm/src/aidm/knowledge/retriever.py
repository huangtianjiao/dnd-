"""规则检索器 — 封装 indexer.search，输出供 LLM/校验使用的格式化规则。

集成 LlamaIndex VectorStoreIndex 作为可选增强检索路径（data.js 语料）。
默认仍使用 indexer.search（直接 Qdrant 向量检索），保持接口兼容。

规则: RAG 检索 top-k + 标签过滤（PRD §4 P2 / ARCHITECTURE §5.1）
"""

from __future__ import annotations

import logging

from . import indexer

logger = logging.getLogger(__name__)

# 模组内容 tag 前缀：命中时对 LLM 标注防剧透（DM 可参考，勿直接向玩家泄露谜底）
SPOILER_TAG_PREFIX = "模组/"
SPOILER_NOTICE = (
    "⚠ 模组内容（仅供 DM 参考：仅供幕后使用，"
    "向玩家叙述时不得泄露模组谜底、陷阱位置、Boss 弱点等未揭露信息）"
)

# LlamaIndex VectorStoreIndex 缓存（懒加载）
_li_index = None


def _get_li_index():
    """懒加载 LlamaIndex VectorStoreIndex（data.js 语料集合）。"""
    global _li_index
    if _li_index is None:
        try:
            _li_index = indexer.get_llamaindex_vector_index(
                collection=None,  # 使用默认集合（dnd_rules）
            )
            logger.info("[retriever] LlamaIndex VectorStoreIndex 加载成功")
        except Exception as e:
            logger.warning(f"[retriever] LlamaIndex 加载失败，使用直接 Qdrant 检索: {e}")
            _li_index = False  # 标记为不可用，避免重复尝试
    return _li_index if _li_index is not False else None


def query_rules(query: str, limit: int = 5, tag_filter: str | None = None) -> list[dict]:
    """语义检索规则条目（top-k，可选标签过滤）。

    优先使用直接 Qdrant 检索（稳定可靠）；
    如需 LlamaIndex 增强检索（如节点后处理），可调用 query_rules_llamaindex()。
    """
    return indexer.search(query, limit=limit, tag_filter=tag_filter)


def query_rules_llamaindex(query: str, limit: int = 5,
                           tag_filter: str | None = None) -> list[dict]:
    """使用 LlamaIndex VectorStoreIndex 检索规则条目（增强路径）。

    支持 LlamaIndex 的节点后处理（如关键词过滤、相似度阈值）。
    如果 LlamaIndex 不可用，自动回退到 query_rules()。
    """
    idx = _get_li_index()
    if idx is None:
        return query_rules(query, limit=limit, tag_filter=tag_filter)

    try:
        retriever = idx.as_retriever(similarity_top_k=limit)
        nodes = retriever.retrieve(query)
        results = []
        for nws in nodes:
            meta = nws.node.metadata or {}
            tag = meta.get("tag", "")
            # 标签过滤
            if tag_filter and tag != tag_filter:
                continue
            results.append({
                "score": nws.score or 0.0,
                "body": nws.node.get_content(),
                "tag": tag,
                "path": meta.get("path", ""),
                "title": meta.get("title", ""),
            })
        return results[:limit]
    except Exception as e:
        logger.warning(f"[retriever] LlamaIndex 检索失败，回退直接检索: {e}")
        return query_rules(query, limit=limit, tag_filter=tag_filter)


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
