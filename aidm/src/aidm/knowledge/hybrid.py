"""Hybrid 检索 — BM25(字符级) + 向量(bge-small) RRF 融合。

纯向量在中文规则关键词（"摔绊""豁免DC""+2"）上易偏移；BM25 精确命中关键词。
RRF(Reciprocal Rank Fusion) 融合两者排名，补足精度。
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Optional

from . import indexer, parse_rulespec

_corpus: Optional[list[dict]] = None
_bm25: Optional["BM25"] = None


def _tokenize(text: str) -> list[str]:
    """中文字符级 + ASCII 词级 分词（BM25 关键词匹配用）。"""
    toks: list[str] = []
    buf: list[str] = []
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff":
            if buf:
                toks.append("".join(buf).lower()); buf = []
            toks.append(ch)
        elif ch.isalnum():
            buf.append(ch)
        else:
            if buf:
                toks.append("".join(buf).lower()); buf = []
    if buf:
        toks.append("".join(buf).lower())
    return toks


class BM25:
    def __init__(self, tokenized_docs: list[list[str]]):
        self.N = len(tokenized_docs)
        self.docs = tokenized_docs
        self.dl = [len(d) for d in tokenized_docs]
        self.avgdl = (sum(self.dl) / self.N) if self.N else 1.0
        df: dict[str, int] = {}
        for d in tokenized_docs:
            for t in set(d):
                df[t] = df.get(t, 0) + 1
        self.idf = {t: math.log((self.N - n + 0.5) / (n + 0.5) + 1) for t, n in df.items()}
        self.tf = [Counter(d) for d in tokenized_docs]
        self.k1, self.b = 1.5, 0.75

    def search(self, query: str, top_n: int = 20) -> list[tuple[int, float]]:
        qt = _tokenize(query)
        scores = []
        for i in range(self.N):
            s = 0.0
            for t in qt:
                if t in self.idf:
                    f = self.tf[i].get(t, 0)
                    denom = f + self.k1 * (1 - self.b + self.b * self.dl[i] / self.avgdl)
                    s += self.idf[t] * (f * (self.k1 + 1)) / (denom + 1e-9)
            scores.append(s)
        ranked = sorted(range(self.N), key=lambda i: -scores[i])[:top_n]
        return [(i, scores[i]) for i in ranked]


def _ensure() -> None:
    global _corpus, _bm25
    if _corpus is None:
        _corpus = parse_rulespec.parse_rulespec()
        _bm25 = BM25([_tokenize(c["body"]) for c in _corpus])


def search_spec_hybrid(query: str, limit: int = 5, dense_n: int = 20,
                      bm25_n: int = 20, rrf_k: int = 60) -> list[dict]:
    """Hybrid 检索 RULE_SPEC 规则点：向量 top-N + BM25 top-N → RRF 融合 → top-k。"""
    _ensure()
    # 向量侧
    dense = indexer.search_spec(query, limit=dense_n)
    dense_tags = [r["tag"] for r in dense]
    # BM25 侧
    bm = _bm25.search(query, top_n=bm25_n)
    bm_tags = [_corpus[i]["tag"] for i, _ in bm]
    # RRF 融合
    score: dict[str, float] = {}
    for rank, rid in enumerate(dense_tags):
        score[rid] = score.get(rid, 0.0) + 1.0 / (rrf_k + rank + 1)
    for rank, rid in enumerate(bm_tags):
        score[rid] = score.get(rid, 0.0) + 1.0 / (rrf_k + rank + 1)
    # 组装 payload
    by_tag = {r["tag"]: r for r in dense}
    for idx, _ in bm:
        by_tag[_corpus[idx]["tag"]] = _corpus[idx]
    ranked = sorted(score, key=lambda t: -score[t])[:limit]
    return [{**by_tag[t], "score": score[t]} for t in ranked if t in by_tag]


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    for q in ["摔绊 推撞 让目标倒地", "法术豁免DC 8+属性+熟练", "倒地 5尺内攻击优势"]:
        print(f"hybrid 检索: {q}")
        for r in search_spec_hybrid(q, limit=3):
            print(f"  [{r['score']:.4f}] {r['tag']} {r.get('title','')}")
        print()
