"""Hybrid 检索 — LlamaIndex BM25Retriever + 向量(bge-small) QueryFusionRetriever RRF 融合。

纯向量在中文规则关键词（"摔绊""豁免DC""+2"）上易偏移；BM25 精确命中关键词。
LlamaIndex QueryFusionRetriever 以 RECIPROCAL_RANK 模式融合两者排名，补足精度。
"""

from __future__ import annotations

import logging
from typing import List

from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.retrievers.fusion_retriever import FUSION_MODES
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.retrievers.bm25 import BM25Retriever

from . import indexer, parse_rulespec

logger = logging.getLogger(__name__)

# 中文 token_pattern：每个汉字为独立 token，ASCII 字母数字串为词 token
_ZH_TOKEN_PATTERN = r"[\u4e00-\u9fff]|[a-zA-Z0-9]+"

_corpus: list[dict] | None = None
_bm25_retriever: BM25Retriever | None = None
_fusion_retriever: QueryFusionRetriever | None = None


# ──────────────────────────────────────────────────────────────────────────
# 向量检索适配器 — 包装 indexer.search_spec 为 LlamaIndex BaseRetriever
# ──────────────────────────────────────────────────────────────────────────

class _DenseVectorRetriever:
    """将现有 Qdrant 向量检索（indexer.search_spec）适配为 LlamaIndex 检索器接口。

    复用已有的 bge-small 嵌入 + Qdrant 本地文件存储，不重复建索引。
    """

    def __init__(self, search_fn, top_k: int = 20):
        self._search = search_fn
        self._top_k = top_k

    def retrieve(self, query: str) -> list[NodeWithScore]:
        results = self._search(query, limit=self._top_k)
        nodes: list[NodeWithScore] = []
        for r in results:
            node = TextNode(
                text=r.get("body", ""),
                metadata={
                    "tag": r.get("tag", ""),
                    "path": r.get("path", ""),
                    "title": r.get("title", ""),
                },
            )
            nodes.append(NodeWithScore(node=node, score=r.get("score", 0.0)))
        return nodes

    # QueryFusionRetriever 内部调用 get_retrieved_nodes → 最终调到 retrieve
    def get_retrieved_nodes(self, query: str) -> list[NodeWithScore]:
        return self.retrieve(query)


# ──────────────────────────────────────────────────────────────────────────
# 懒加载初始化
# ──────────────────────────────────────────────────────────────────────────

def _ensure() -> None:
    """懒加载：解析 RULE_SPEC 语料 → 构建 BM25 + 向量检索器 → QueryFusionRetriever。"""
    global _corpus, _bm25_retriever, _fusion_retriever
    if _fusion_retriever is not None:
        return

    _corpus = parse_rulespec.parse_rulespec()

    # 构建 LlamaIndex TextNode 列表（BM25 语料）
    nodes: list[TextNode] = []
    for item in _corpus:
        node = TextNode(
            text=item["body"],
            metadata={"tag": item["tag"], "path": item["path"], "title": item["title"]},
        )
        nodes.append(node)

    # LlamaIndex BM25Retriever（中文 token_pattern 字符级分词）
    _bm25_retriever = BM25Retriever.from_defaults(
        nodes=nodes,
        token_pattern=_ZH_TOKEN_PATTERN,
        similarity_top_k=20,
        skip_stemming=True,  # 中文无需词干提取
    )

    # 向量检索器（复用 indexer.search_spec + Qdrant）
    dense_retriever = _DenseVectorRetriever(
        search_fn=indexer.search_spec, top_k=20,
    )

    # LlamaIndex QueryFusionRetriever — RECIPROCAL_RANK 模式（RRF 融合）
    # num_queries=1 禁用 LLM 查询扩展（避免额外 LLM 调用，中文场景下扩展效果不稳定）
    try:
        _fusion_retriever = QueryFusionRetriever(
            retrievers=[dense_retriever, _bm25_retriever],
            mode=FUSION_MODES.RECIPROCAL_RANK,
            similarity_top_k=20,  # 融合后取 top-20，最终由 search_spec_hybrid 截取
            num_queries=1,
            use_async=False,
            verbose=False,
        )
        logger.info("[hybrid] QueryFusionRetriever 初始化成功 (BM25 + Dense, RRF)")
    except Exception as e:
        logger.warning(f"[hybrid] QueryFusionRetriever 初始化失败，回退手动 RRF: {e}")
        _fusion_retriever = None  # 标记回退


# ──────────────────────────────────────────────────────────────────────────
# 手动 RRF 回退（当 QueryFusionRetriever 不可用时）
# ──────────────────────────────────────────────────────────────────────────

def _manual_rrf_search(query: str, limit: int = 5, dense_n: int = 20,
                       bm25_n: int = 20, rrf_k: int = 60) -> list[dict]:
    """手动 RRF 融合：向量 top-N + BM25 top-N → 倒数排名融合 → top-k。"""
    assert _corpus is not None and _bm25_retriever is not None

    # 向量侧
    dense = indexer.search_spec(query, limit=dense_n)
    dense_tags = [r["tag"] for r in dense]

    # BM25 侧（LlamaIndex BM25Retriever）
    bm25_nodes = _bm25_retriever.retrieve(query)
    bm25_tags = [n.metadata.get("tag", "") for n in bm25_nodes]

    # RRF 融合
    score: dict[str, float] = {}
    for rank, rid in enumerate(dense_tags):
        score[rid] = score.get(rid, 0.0) + 1.0 / (rrf_k + rank + 1)
    for rank, rid in enumerate(bm25_tags):
        score[rid] = score.get(rid, 0.0) + 1.0 / (rrf_k + rank + 1)

    # 组装 payload
    by_tag = {r["tag"]: r for r in dense}
    for n in bm25_nodes:
        tag = n.metadata.get("tag", "")
        if tag and tag not in by_tag:
            by_tag[tag] = {
                "body": n.text,
                "tag": tag,
                "path": n.metadata.get("path", ""),
                "title": n.metadata.get("title", ""),
            }

    ranked = sorted(score, key=lambda t: -score[t])[:limit]
    return [{**by_tag[t], "score": score[t]} for t in ranked if t in by_tag]


# ──────────────────────────────────────────────────────────────────────────
# 公开接口
# ──────────────────────────────────────────────────────────────────────────

def search_spec_hybrid(query: str, limit: int = 5, dense_n: int = 20,
                       bm25_n: int = 20, rrf_k: int = 60) -> list[dict]:
    """Hybrid 检索 RULE_SPEC 规则点：LlamaIndex QueryFusionRetriever (BM25 + 向量 RRF) → top-k。

    优先使用 LlamaIndex QueryFusionRetriever；若初始化失败则回退到手动 RRF。
    """
    _ensure()

    # 尝试 LlamaIndex QueryFusionRetriever
    if _fusion_retriever is not None:
        try:
            nodes_with_scores = _fusion_retriever.retrieve(query)
            results: list[dict] = []
            for nws in nodes_with_scores[:limit]:
                meta = nws.node.metadata or {}
                results.append({
                    "body": nws.node.get_content(),
                    "tag": meta.get("tag", ""),
                    "path": meta.get("path", ""),
                    "title": meta.get("title", ""),
                    "score": nws.score or 0.0,
                })
            return results
        except Exception as e:
            logger.warning(f"[hybrid] QueryFusionRetriever 检索失败，回退手动 RRF: {e}")

    # 回退：手动 RRF
    return _manual_rrf_search(query, limit=limit, dense_n=dense_n, bm25_n=bm25_n, rrf_k=rrf_k)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    for q in ["摔绊 推撞 让目标倒地", "法术豁免DC 8+属性+熟练", "倒地 5尺内攻击优势"]:
        print(f"hybrid 检索: {q}")
        for r in search_spec_hybrid(q, limit=3):
            print(f"  [{r['score']:.4f}] {r['tag']} {r.get('title', '')}")
        print()
