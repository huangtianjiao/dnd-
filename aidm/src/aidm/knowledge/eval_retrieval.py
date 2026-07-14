"""检索质量评测 — 量化 bge-small 纯向量 vs hybrid(BM25+向量) 的 recall。

评测集：15 条查询 + 期望命中的规则ID集合（每条查询可能有多个等价正确答案）。
指标：recall@k = 期望ID是否出现在 top-k 内。
"""

from __future__ import annotations

import sys

# (查询, 期望命中的规则ID集合)
EVAL: list[tuple[str, set[str]]] = [
    ("摔绊 推撞 让目标倒地", {"R-GLS-034", "R-ADD-011"}),
    ("擒抱 怎么逃脱", {"R-GLS-036", "R-GLS-049"}),
    ("死亡豁免检定 1d20", {"R-DMG-017", "R-GLS-020"}),
    ("专注 受伤 维持 豁免DC", {"R-GLS-013", "R-SPL-020"}),
    ("法术豁免DC 8+属性+熟练", {"R-SPL-021", "R-DM-002", "R-CHK-012"}),
    ("重击 天然20 伤害骰翻倍", {"R-CMB-029", "R-GLS-002"}),
    ("抗性 易伤 伤害结算顺序", {"R-DMG-005", "R-QCK-002", "R-DMG-003"}),
    ("先攻 突袭 劣势", {"R-CMB-002", "R-GLS-009"}),
    ("掩护 半身+2 四分之三+5", {"R-CMB-015", "R-QCK-005", "R-GLS-007"}),
    ("倒地 5尺内攻击优势", {"R-GLS-055"}),
    ("临时生命值 先扣除", {"R-DMG-009"}),
    ("长休 恢复生命值 法术位", {"R-GLS-015", "R-SPL-003", "R-ADD-016"}),
    ("熟练加值 等级 +2", {"R-CHK-015"}),
    ("属性调整值 公式 floor", {"R-CHK-024"}),
    ("中毒 攻击检定劣势", {"R-GLS-054"}),
]


def _ids(results: list[dict]) -> list[str]:
    return [r.get("tag", "") for r in results]


def run_eval(search_fn, k_list=(3, 5), label="") -> dict:
    """search_fn(query, limit) -> list[payload]. 返回各 k 的 recall + 逐条命中。"""
    hits = {k: 0 for k in k_list}
    details = []
    for query, expected in EVAL:
        res = search_fn(query, limit=max(k_list))
        ids = _ids(res)
        row = {"query": query, "expected": expected}
        for k in k_list:
            topk = set(ids[:k])
            ok = bool(topk & expected)
            row[f"hit@{k}"] = ok
            if ok:
                hits[k] += 1
        row["retrieved_top3"] = ids[:3]
        details.append(row)
    n = len(EVAL)
    print(f"\n=== {label} ===")
    for k in k_list:
        print(f"recall@{k}: {hits[k]}/{n} = {hits[k]/n:.0%}")
    print("逐条:")
    for d in details:
        flag = "✓" if d["hit@3"] else "✗"
        print(f"  {flag} {d['query'][:24]:24} 期望={sorted(d['expected'])} 命中@3={d['retrieved_top3']}")
    return {"label": label, "n": n, "recall": {k: hits[k] / n for k in k_list}, "details": details}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    from . import indexer, hybrid  # hybrid 稍后实现

    # 确保 RULE_SPEC 语料已索引
    try:
        indexer.search_spec("测试", limit=1)
    except Exception:
        from . import parse_rulespec
        indexer.index_chunks(parse_rulespec.parse_rulespec(), "dnd_rule_spec")

    print("评测 bge-small 纯向量 vs hybrid(BM25+向量 RRF)")
    run_eval(indexer.search_spec, label="纯向量(bge-small)")
    run_eval(hybrid.search_spec_hybrid, label="hybrid(BM25+向量RRF)")
