"""规则库索引器 — data.js 6238 条 → 本地 Qdrant（文件模式，免 docker）。

用 qdrant-client 的本地模式（path=...db），无需起 Qdrant 服务，存档即一个文件。
向量化用本地 bge 嵌入（knowledge.embedding）。
集成 LlamaIndex QdrantVectorStore 用于结构化索引构建。
"""

from __future__ import annotations

import logging

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from ..config import get_settings
from . import embedding, parse_datajs

logger = logging.getLogger(__name__)

_DB_PATH = r"D:\game\dnd\aidm\data\rules.db"
_client: QdrantClient | None = None


def get_qdrant() -> QdrantClient:
    """本地 Qdrant 客户端（文件存储，单进程）。"""
    global _client
    if _client is None:
        _client = QdrantClient(path=_DB_PATH)
    return _client


def reset_collection() -> None:
    """删除并重建集合（按当前 embedding_dim）。"""
    s = get_settings()
    q = get_qdrant()
    cols = [c.name for c in q.get_collections().collections]
    if s.qdrant_collection in cols:
        q.delete_collection(s.qdrant_collection)
    q.create_collection(
        s.qdrant_collection,
        vectors_config=VectorParams(size=s.embedding_dim, distance=Distance.COSINE),
    )


def build_index(batch_size: int = 64, limit: int | None = None,
                rebuild: bool = True) -> int:
    """解析 data.js → 嵌入 → 写入 Qdrant。

    规则: 知识库 RAG 向量化（data.js 6238 条；body 为正文，payload 含 tag/path/title）
    limit: 仅索引前 N 条（用于快速验证）；None=全量。
    """
    s = get_settings()
    entries = parse_datajs.parse_datajs(s.rules_datajs_path)
    if limit:
        entries = entries[:limit]
    if rebuild:
        reset_collection()
    q = get_qdrant()
    total = 0
    for i in range(0, len(entries), batch_size):
        batch = entries[i:i + batch_size]
        texts = [e.body for e in batch]
        vecs = embedding.embed_texts(texts, batch_size=batch_size, show_progress=False)
        points = [
            PointStruct(
                id=i + j, vector=vecs[j],
                payload={"body": e.body, "tag": e.tag, "path": e.source, "title": e.title},
            )
            for j, e in enumerate(batch)
        ]
        q.upsert(s.qdrant_collection, points=points)
        total += len(points)
        if (i // batch_size) % 5 == 0:
            print(f"  已索引 {total}/{len(entries)} 条")
    print(f"[indexer] 索引完成 {total} 条 → {_DB_PATH}")
    return total


def search(query: str, limit: int = 5,
           tag_filter: str | None = None) -> list[dict]:
    """语义检索规则：查询文本 → top-k 相关条目（数据语料 data.js 集合）。

    规则: RAG 检索（top-k + 可选标签过滤）
    """
    s = get_settings()
    q = get_qdrant()
    vec = embedding.embed_query(query)
    flt = None
    if tag_filter:
        from qdrant_client.models import FieldCondition, MatchValue
        flt = FieldCondition(key="tag", match=MatchValue(value=tag_filter))
    res = q.query_points(
        s.qdrant_collection, query=vec, limit=limit,
        query_filter=flt,
    )
    out = []
    for p in res.points:
        out.append({
            "score": p.score, **p.payload,
        })
    return out


# ──────────────────────────────────────────────────────────────────────────
# 规则文本语料（rules_text 141页 → 校验判定参数用）
# ──────────────────────────────────────────────────────────────────────────

def index_text_files(directory: str, collection: str, batch_size: int = 32,
                     limit: int | None = None, rebuild: bool = True) -> int:
    """扫描目录下所有 .txt → 嵌入 → 写入指定 Qdrant 集合。

    用于 rules_text/（判定规则文本，校验判定参数）。
    payload: {body, tag=相对路径, path, title=文件名}
    """
    import os
    files = []
    for dp, _dirs, fs in os.walk(directory):
        for f in sorted(fs):
            if f.lower().endswith(".txt"):
                files.append(os.path.join(dp, f))
    if limit:
        files = files[:limit]
    if rebuild:
        cols = [c.name for c in get_qdrant().get_collections().collections]
        if collection in cols:
            get_qdrant().delete_collection(collection)
    get_qdrant().create_collection(
        collection, vectors_config=VectorParams(size=get_settings().embedding_dim,
                                                distance=Distance.COSINE),
    )
    total = 0
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        texts, metas = [], []
        for fp in batch:
            try:
                with open(fp, encoding="utf-8", errors="replace") as f:
                    body = f.read()
            except Exception:
                continue
            texts.append(body)
            rel = os.path.relpath(fp, directory).replace("\\", "/")
            metas.append({"body": body, "tag": rel, "path": rel,
                          "title": os.path.splitext(os.path.basename(fp))[0]})
        if not texts:
            continue
        vecs = embedding.embed_texts(texts, batch_size=batch_size, show_progress=False)
        points = [PointStruct(id=i + j, vector=vecs[j], payload=metas[j])
                  for j in range(len(texts))]
        get_qdrant().upsert(collection, points=points)
        total += len(points)
    print(f"[indexer] 文本语料索引完成 {total} 条 → 集合 {collection}")
    return total


def search_rules(query: str, limit: int = 5) -> list[dict]:
    """语义检索规则文本（rules_text 集合，校验判定参数用）。"""
    s = get_settings()
    q = get_qdrant()
    vec = embedding.embed_query(query)
    res = q.query_points(s.qdrant_rule_collection, query=vec, limit=limit)
    return [{"score": p.score, **p.payload} for p in res.points]


def index_chunks(items: list[dict], collection: str, batch_size: int = 32,
                 rebuild: bool = True) -> int:
    """通用：把 payload 列表({body,tag,path,title}) 嵌入并写入指定集合。

    用于 RULE_SPEC 400 条结构化规则点（校验语料，最高信号）。
    支持 LlamaIndex QdrantVectorStore 路径（优先）和直接 Qdrant 路径（回退）。
    """
    try:
        return _index_chunks_llamaindex(items, collection, batch_size, rebuild)
    except Exception as e:
        logger.warning(f"[indexer] LlamaIndex 索引失败，回退直接 Qdrant: {e}")
        return _index_chunks_direct(items, collection, batch_size, rebuild)


def _index_chunks_llamaindex(items: list[dict], collection: str,
                             batch_size: int = 32, rebuild: bool = True) -> int:
    """使用 LlamaIndex QdrantVectorStore 索引 chunks。"""
    from llama_index.core import StorageContext, VectorStoreIndex
    from llama_index.core.schema import Document
    from llama_index.vector_stores.qdrant import QdrantVectorStore

    s = get_settings()
    q = get_qdrant()

    # 确保集合存在
    if rebuild:
        cols = [c.name for c in q.get_collections().collections]
        if collection in cols:
            q.delete_collection(collection)
    q.create_collection(
        collection,
        vectors_config=VectorParams(size=s.embedding_dim, distance=Distance.COSINE),
    )

    # 构建 LlamaIndex QdrantVectorStore（复用已有 Qdrant 客户端）
    vector_store = QdrantVectorStore(
        client=q,
        collection_name=collection,
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 将 items 转换为 LlamaIndex Document 列表
    documents = []
    for i, item in enumerate(items):
        doc = Document(
            text=item.get("body", ""),
            metadata={
                "tag": item.get("tag", ""),
                "path": item.get("path", ""),
                "title": item.get("title", ""),
            },
            doc_id=f"{collection}_{i}",
        )
        documents.append(doc)

    # 使用自定义嵌入函数
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    embed_model = HuggingFaceEmbedding(model_name=s.embedding_model)

    # 批量索引
    total = 0
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i + batch_size]
        VectorStoreIndex(
            documents=batch_docs,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=False,
        )
        total += len(batch_docs)

    print(f"[indexer] LlamaIndex chunks 索引完成 {total} 条 → 集合 {collection}")
    return total


def _index_chunks_direct(items: list[dict], collection: str,
                         batch_size: int = 32, rebuild: bool = True) -> int:
    """直接 Qdrant 索引 chunks（回退路径）。"""
    if rebuild:
        cols = [c.name for c in get_qdrant().get_collections().collections]
        if collection in cols:
            get_qdrant().delete_collection(collection)
    get_qdrant().create_collection(
        collection, vectors_config=VectorParams(size=get_settings().embedding_dim,
                                                 distance=Distance.COSINE),
    )
    total = 0
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        texts = [b["body"] for b in batch]
        vecs = embedding.embed_texts(texts, batch_size=batch_size, show_progress=False)
        points = [PointStruct(id=i + j, vector=vecs[j], payload=batch[j])
                  for j in range(len(batch))]
        get_qdrant().upsert(collection, points=points)
        total += len(points)
    print(f"[indexer] chunks 索引完成 {total} 条 → 集合 {collection}")
    return total


def search_spec(query: str, limit: int = 5) -> list[dict]:
    """语义检索 RULE_SPEC 结构化规则点（校验判定参数用，最高信号）。"""
    s = get_settings()
    q = get_qdrant()
    vec = embedding.embed_query(query)
    col = getattr(s, "qdrant_spec_collection", "dnd_rule_spec")
    res = q.query_points(col, query=vec, limit=limit)
    return [{"score": p.score, **p.payload} for p in res.points]


# ──────────────────────────────────────────────────────────────────────────
# LlamaIndex 集成：便捷函数
# ──────────────────────────────────────────────────────────────────────────

def get_llamaindex_vector_index(collection: str | None = None):
    """获取 LlamaIndex VectorStoreIndex（从已有 Qdrant 集合加载）。

    用于需要 LlamaIndex 高级功能（如异步检索、节点后处理）的场景。
    """
    from llama_index.core import VectorStoreIndex
    from llama_index.vector_stores.qdrant import QdrantVectorStore

    s = get_settings()
    col = collection or getattr(s, "qdrant_spec_collection", "dnd_rule_spec")
    q = get_qdrant()

    vector_store = QdrantVectorStore(client=q, collection_name=col)
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    embed_model = HuggingFaceEmbedding(model_name=s.embedding_model)

    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )


# ──────────────────────────────────────────────────────────────────────────
# 自检（索引 80 条子集 → 检索）
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    import os
    # 干净起见先删旧 db
    if os.path.exists(_DB_PATH):
        os.remove(_DB_PATH)
    global _client
    _client = None
    n = build_index(limit=80, rebuild=True)
    assert n == 80
    # 检索：问"火球术"应命中火焰相关条目（在 80 条里取决于命中）
    res = search("火球术 火焰伤害 法术", limit=3)
    print("  检索 '火球术 火焰伤害 法术' →")
    for r in res:
        print(f"    [{r['score']:.3f}] tag={r['tag']!r} {r['title']}")
    assert len(res) == 3
    res2 = search("攻击检定 命中 AC", limit=3)
    print("  检索 '攻击检定 命中 AC' →")
    for r in res2:
        print(f"    [{r['score']:.3f}] tag={r['tag']!r} {r['title']}")
    print("[indexer] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
