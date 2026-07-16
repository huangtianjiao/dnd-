"""LLM 客户端 — langchain_openai.ChatOpenAI（兼容 senseaudio 网关 deepseek-v4-flash）。

P3 LangGraph 编排将基于此客户端。base_url/key/model 来自 config（读 .env）。
"""

from __future__ import annotations

from ..config import get_settings


def get_llm(temperature: float = 0.3, streaming: bool = False, **kwargs):
    """获取 LLM 实例（deepseek-v4-flash，OpenAI 兼容协议）。"""
    from langchain_openai import ChatOpenAI
    s = get_settings()
    return ChatOpenAI(
        model=s.llm_model,
        api_key=s.llm_api_key,
        base_url=s.llm_base_url,
        temperature=temperature,
        streaming=streaming,
        **kwargs,
    )


def chat(system: str, user: str, temperature: float = 0.3) -> str:
    """便捷：一次性问答，返回文本。"""
    llm = get_llm(temperature=temperature)
    from langchain_core.messages import SystemMessage, HumanMessage
    resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return resp.content


if __name__ == "__main__":
    # 联调：用检索到的规则作上下文，让 LLM 仅据规则回答
    import sys
    from ..knowledge import retriever
    q = "D&D 5E 中摔绊（Shove）动作如何判定？"
    rules = retriever.query_formatted(q, limit=3, body_limit=400)
    system = "你是D&D 5E规则助手。只能依据提供的规则原文回答，规则未覆盖时明说'规则未提供'，不要凭记忆编造。"
    user = f"问题：{q}\n\n规则原文（检索结果）：\n{rules}"
    print("=== RAG 检索到的规则 ===")
    print(rules[:200], "...\n")
    print("=== LLM 据规则回答 ===")
    print(chat(system, user))
