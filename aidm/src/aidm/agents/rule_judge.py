"""Rule Judge Agent — 行动合法性验证 + 规则书 RAG 查询。

职责:
  - 验证玩家行动是否合法（关键词预检）
  - 从规则书检索相关规则
  - 校验判定参数合规性

设计参考: ITMO AI-DM 的 Rule Judge 角色，
拥有否决权：任何行动必须先通过规则校验。
"""

from __future__ import annotations

from ..brain.state import GameState
from ..knowledge import hybrid, verifier


def retrieve(state: GameState) -> dict:
    """Rule Judge: hybrid 检索相关规则（校验与叙事用）。"""
    q = state["intent"].get("retrieval_query") or state["player_input"]
    return {"evidence": hybrid.search_spec_hybrid(q, limit=6)}


def retrieve_retry(state: GameState) -> dict:
    """校验驳回后重检索：用 issues/正确方法 补关键词。"""
    issues = state.get("verification", {}).get("issues", [])
    base = state["intent"].get("retrieval_query") or state["player_input"]
    q = base + " " + " ".join(issues) + " 检定方式 DC来源 豁免"
    return {"evidence": hybrid.search_spec_hybrid(q[:80], limit=6)}


def verify(state: GameState) -> dict:
    """Rule Judge: 关键词预检判定参数合规性（语义校验留 confirm/LLM）。"""
    it = state["intent"]
    if it.get("action_type") in ("other", "start_combat", "end_combat"):
        return {"verification": {"ok": True, "issues": []}}
    v = verifier.verify(it.get("retrieval_query", state["player_input"]),
                        proposed_check_type=it.get("ability"),
                        proposed_dc=it.get("target_ac") or it.get("dc"),
                        limit=6)
    return {"verification": {"ok": v.ok, "issues": v.issues}}
