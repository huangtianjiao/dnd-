"""判定校验器 — 用检索到的规则原文校验 LLM 提出的判定参数。

设计原则"RAG 校验而非参考"（ARCHITECTURE §2）：规则原文说了算，冲突时驳回。
本模块提供证据收集 + 关键词预检；真正的语义级校验在 P3 由 LLM 比对完成。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from . import retriever, hybrid


@dataclass
class Verification:
    ok: bool                              # 是否通过校验
    evidence: list[dict] = field(default_factory=list)   # 检索到的规则原文
    issues: list[str] = field(default_factory=list)      # 关键词预检发现的问题
    digest: str = ""                      # 供 LLM 比对的格式化规则块


def gather_evidence(action_desc: str, limit: int = 5) -> list[dict]:
    """为一次判定动作检索相关规则原文（RULE_SPEC 语料，hybrid 检索，recall@3=100%）。"""
    return hybrid.search_spec_hybrid(action_desc, limit=limit)


def keyword_preflight(proposed_check_type: Optional[str], proposed_dc: Optional[int],
                      results: list[dict]) -> list[str]:
    """简易关键词预检：若规则原文未提及 proposed 检定类型/DC，标记存疑。

    真正的语义校验在 P3 由 LLM 完成；此处只做粗筛。
    """
    issues: list[str] = []
    text = " ".join(r.get("body", "") for r in results)
    if proposed_check_type and proposed_check_type not in text:
        issues.append(f"检索规则未提及检定类型 {proposed_check_type!r}，建议 LLM/人工复核")
    if proposed_dc is not None and str(proposed_dc) not in text:
        # DC 数值未直接命中是常态（DC 多由公式算），仅提示
        issues.append(f"DC={proposed_dc} 未在规则原文直接出现（多由公式算，需 LLM 核公式）")
    return issues


def verify(action_desc: str, *, proposed_check_type: Optional[str] = None,
           proposed_dc: Optional[int] = None, limit: int = 8) -> Verification:
    """校验一次判定：检索证据(hybrid, limit=8 保证机制类规则进上下文) + 关键词预检。

    返回 Verification（ok=True=无关键词冲突；evidence/digest 供 P3 LLM 语义校验）。
    说明: limit=8 因 top-3 常被"结果类"规则占据，机制类规则(如 R-GLS-034)多在 top5-8，
          LLM 通读全部证据即可引用正确机制。
    """
    evidence = gather_evidence(action_desc, limit=limit)
    issues = keyword_preflight(proposed_check_type, proposed_dc, evidence)
    digest = retriever.format_for_llm(evidence)
    return Verification(ok=(len(issues) == 0), evidence=evidence, issues=issues, digest=digest)


if __name__ == "__main__":
    v = verify("摔绊 倒地 擒抱 力量豁免", proposed_check_type="力量", proposed_dc=15, limit=3)
    print(f"校验通过(关键词预检): {v.ok}")
    print(f"问题: {v.issues}")
    print(f"证据条数: {len(v.evidence)}")
    print("digest 预览:\n", v.digest[:300])
