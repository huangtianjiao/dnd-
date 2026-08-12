"""规则库索引器 — data.js 6238 条 → 本地 Qdrant（文件模式，免 docker）。

用 qdrant-client 的本地模式（path=...db），无需起 Qdrant 服务，存档即一个文件。
向量化用本地 bge 嵌入（knowledge.embedding）。
集成 LlamaIndex QdrantVectorStore 用于结构化索引构建。
"""

from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass, field

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from ..config import get_settings
from . import embedding, parse_datajs

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────
# RAG-002: 规则溯源链
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class SourceSpan:
    """规则溯源信息。

    规则: RAG-002 规则溯源链
    出处: 为每条索引规则添加来源文档/书名/页码/锚点/内容hash/权威级别。

    属性:
        source_id: 来源文档 ID（路径 hash）
        book: 书名
        page: 页码/章节
        anchor: 锚点
        content_hash: 内容 hash（用于检测变更）
        authority_level: core / supplement
    """
    source_id: str = ""
    book: str = ""
    page: str = ""
    anchor: str = ""
    content_hash: str = ""
    authority_level: str = "core"

    def to_payload(self) -> dict:
        """转换为索引 payload 字典。"""
        return {
            "source_id": self.source_id,
            "book": self.book,
            "page": self.page,
            "anchor": self.anchor,
            "content_hash": self.content_hash,
            "authority_level": self.authority_level,
        }

    @classmethod
    def from_entry(cls, body: str, source: str) -> "SourceSpan":
        """从条目内容和来源路径构建 SourceSpan。"""
        book = derive_book(source)
        edition = derive_edition(source)
        authority = derive_authority_level(book)
        # 生成内容 hash（前 16 位）
        content_hash = hashlib.sha256(body.encode("utf-8", errors="replace")).hexdigest()[:16]
        # source_id = 路径 hash
        source_id = hashlib.md5(source.encode("utf-8", errors="replace")).hexdigest()[:12]
        return cls(
            source_id=source_id,
            book=book,
            page="",
            anchor="",
            content_hash=content_hash,
            authority_level=authority,
        )

# ── 版本推断辅助 ────────────────────────────────────────────────────────
# 2024 版核心规则书目录名（路径中包含这些子串即判定为 2024 edition）
_EDITION_2024_MARKERS = ("2024", "2025")


def derive_edition(path: str) -> str:
    """从来源路径推断 edition（'2024' 或 '2014'）。"""
    norm = path.replace("\\", "/")
    for marker in _EDITION_2024_MARKERS:
        if marker in norm:
            return "2024"
    return "2014"


def derive_book(path: str) -> str:
    """从来源路径提取书名（topics/<book>/... → book）。"""
    norm = path.replace("\\", "/")
    parts = norm.split("/")
    # 期望格式: topics/<book>/...
    if len(parts) >= 2 and parts[0].lower() == "topics":
        return parts[1]
    return parts[0] if parts else ""


def derive_authority_level(book: str) -> str:
    """根据书名判断权威级别: core / supplement。"""
    core_books = {
        "玩家手册", "城主指南", "怪物图鉴",
        "玩家手册2024", "城主指南2024", "怪物图鉴2025",
        "玩家手册2024（试读版）",
    }
    return "core" if book in core_books else "supplement"


def derive_source_class(edition: str) -> str:
    """根据版本推断来源分类。"""
    return f"rule_{edition}"

# RAG-003/P0-09: 路径由配置与数据目录派生，不硬编码到 Windows 盘符
# Qdrant 落盘目录统一走 AIDM_DATA_DIR（Docker 挂载 /data/qdrant）
def _qdrant_db_path() -> str:
    from ..config import DATA_DIR
    return str(DATA_DIR / "qdrant")


_client: QdrantClient | None = None


def get_qdrant() -> QdrantClient:
    """本地 Qdrant 客户端（文件存储，单进程）。"""
    global _client
    if _client is None:
        _client = QdrantClient(path=_qdrant_db_path())
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
                payload={
                    "body": e.body, "tag": e.tag, "path": e.source, "title": e.title,
                    "edition": derive_edition(e.source),
                    "book": derive_book(e.source),
                    "authority_level": derive_authority_level(derive_book(e.source)),
                    "source_class": derive_source_class(derive_edition(e.source)),
                    **SourceSpan.from_entry(e.body, e.source).to_payload(),
                },
            )
            for j, e in enumerate(batch)
        ]
        q.upsert(s.qdrant_collection, points=points)
        total += len(points)
        if (i // batch_size) % 5 == 0:
            print(f"  已索引 {total}/{len(entries)} 条")
    print(f"[indexer] 索引完成 {total} 条 → {_qdrant_db_path()}")
    return total


def search(query: str, limit: int = 5,
           tag_filter: str | None = None,
           edition_filter: str | None = None) -> list[dict]:
    """语义检索规则：查询文本 → top-k 相关条目（数据语料 data.js 集合）。

    规则: RAG 检索（top-k + 可选标签过滤）
    edition_filter: 版本硬过滤（'2024'/'2014'/None）。指定时仅返回对应版本结果。
    """
    s = get_settings()
    q = get_qdrant()
    vec = embedding.embed_query(query)
    flt = _build_filter(tag_filter=tag_filter, edition_filter=edition_filter)
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


def _build_filter(*, tag_filter: str | None = None,
                  edition_filter: str | None = None):
    """构建 Qdrant 复合过滤器（所有条件取交集）。"""
    from qdrant_client.models import FieldCondition, MatchValue, Filter
    conditions = []
    if tag_filter:
        conditions.append(FieldCondition(key="tag", match=MatchValue(value=tag_filter)))
    if edition_filter:
        conditions.append(FieldCondition(key="edition", match=MatchValue(value=edition_filter)))
    if not conditions:
        return None
    return Filter(must=conditions)


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
            book = derive_book(rel)
            edition = derive_edition(rel)
            metas.append({
                "body": body, "tag": rel, "path": rel,
                "title": os.path.splitext(os.path.basename(fp))[0],
                "edition": edition,
                "book": book,
                "authority_level": derive_authority_level(book),
                "source_class": derive_source_class(edition),
            })
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
                "edition": item.get("edition", derive_edition(item.get("path", ""))),
                "book": item.get("book", derive_book(item.get("path", ""))),
                "authority_level": item.get("authority_level", "supplement"),
                "source_class": item.get("source_class", derive_source_class(
                    derive_edition(item.get("path", "")))),
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


def search_spec(query: str, limit: int = 5,
                edition_filter: str | None = None) -> list[dict]:
    """语义检索 RULE_SPEC 结构化规则点（校验判定参数用，最高信号）。

    RAG-001: edition_filter 硬过滤——指定 '2024' 时仅返回 2024 版规则。
    """
    s = get_settings()
    q = get_qdrant()
    vec = embedding.embed_query(query)
    col = getattr(s, "qdrant_spec_collection", "dnd_rule_spec")
    flt = _build_filter(edition_filter=edition_filter)
    res = q.query_points(col, query=vec, limit=limit, query_filter=flt)
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
    if os.path.exists(_qdrant_db_path()):
        os.remove(_qdrant_db_path())
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
