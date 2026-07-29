"""本地嵌入服务 — bge 系列（sentence-transformers）。

提供 embed_texts()/embed_query() 用于规则库向量化与检索。模型懒加载（首次下载）。
归一化向量，便于 Qdrant 余弦相似度。模型可在 config.embedding_model 切换
（bge-small-zh-v1.5 默认；BAAI/bge-m3 更强但更大）。
"""

from __future__ import annotations

import os
from collections.abc import Iterable

import numpy as np

# 国内默认走 HuggingFace 镜像（直连 huggingface.co 不通）
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from ..config import get_settings

_embedder = None

# 单条查询嵌入结果缓存（避免重复推理）
_query_cache: dict[str, list[float]] = {}
_QUERY_CACHE_MAX = 1024


def get_embedder():
    """懒加载 sentence-transformers 模型（首次会从 HuggingFace 下载）。"""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        s = get_settings()
        device = os.getenv("AIDM_EMBEDDING_DEVICE", "cpu")
        _embedder = SentenceTransformer(s.embedding_model, device=device)
    return _embedder


def embed_texts(texts: Iterable[str], batch_size: int = 64,
                show_progress: bool = True) -> list[list[float]]:
    """批量嵌入文本 → 归一化向量列表。

    规则: 知识库 RAG 语料向量化（data.js 6238 条）
    """
    texts = list(texts)
    emb = get_embedder()
    vecs = emb.encode(
        texts, batch_size=batch_size, show_progress_bar=show_progress,
        convert_to_numpy=True, normalize_embeddings=True,  # 余弦相似度
    )
    return vecs.tolist()


def embed_query(text: str) -> list[float]:
    """单条查询嵌入（带结果缓存）。"""
    if text in _query_cache:
        return _query_cache[text]
    result = embed_texts([text], show_progress=False)[0]
    if len(_query_cache) >= _QUERY_CACHE_MAX:
        # 简单淘汰：清空前半部分
        keys = list(_query_cache.keys())
        for k in keys[:len(keys) // 2]:
            del _query_cache[k]
    _query_cache[text] = result
    return result


def dim() -> int:
    """向量维度（= config.embedding_dim）。"""
    return get_settings().embedding_dim


# ──────────────────────────────────────────────────────────────────────────
# 可选：起独立 HTTP 嵌入服务（OpenAI 兼容 /v1/embeddings）
# 用法: python -m aidm.knowledge.embedding serve --port 8787
# ──────────────────────────────────────────────────────────────────────────

def _serve(port: int = 8787) -> None:
    import uvicorn
    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI(title="aidm-local-embedding")

    class EmbReq(BaseModel):
        input: list[str]
        model: str = ""

    @app.post("/v1/embeddings")
    def embeddings(req: EmbReq):
        vecs = embed_texts(req.input, show_progress=False)
        return {"object": "list", "data": [{"object": "embedding", "index": i, "embedding": v}
                                            for i, v in enumerate(vecs)]}

    print(f"[embedding] 本地嵌入服务启动 http://localhost:{port} (模型={get_settings().embedding_model})")
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == "serve":
        _serve(int(sys.argv[2]) if len(sys.argv) > 2 else 8787)
    else:
        # 自检：加载模型 + 嵌入两条样本，打印维度与相似度
        a = embed_query("攻击检定 d20 命中护甲等级 AC")
        b = embed_query("摔绊擒抱推撞近战攻击")
        c = embed_query("治疗法术恢复生命值")
        a, b, c = np.array(a), np.array(b), np.array(c)
        cos = lambda x, y: float(x @ y)
        print(f"[embedding] 自检通过 ✓ 维度={len(a.tolist())}")
        print(f"  sim(攻击,摔绊)={cos(a,b):.3f}  sim(攻击,治疗)={cos(a,c):.3f}  (前者应更高)")
