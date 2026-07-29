"""LLM 客户端 — langchain_openai.ChatOpenAI（兼容 senseaudio 网关 deepseek-v4-flash）。

P3 LangGraph 编排将基于此客户端。base_url/key/model 来自 config（读 .env）。
"""

from __future__ import annotations

import os

from ..config import get_settings

# ── LLM 调用缓存（模块级，只初始化一次）──────────────────────────────────
_llm_cache_initialized = False


def _init_llm_cache():
    global _llm_cache_initialized
    if _llm_cache_initialized:
        return
    _llm_cache_initialized = True
    if os.getenv("AIDM_LLM_CACHE", "true").lower() == "true":
        try:
            from langchain.cache import SQLiteCache
            from langchain.globals import set_llm_cache
            cache_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'saves')
            os.makedirs(cache_dir, exist_ok=True)
            set_llm_cache(SQLiteCache(database_path=os.path.join(cache_dir, 'llm_cache.db')))
        except Exception:
            pass


def get_llm(temperature: float = 0.3, streaming: bool = False, **kwargs):
    """获取 LLM 实例（deepseek-v4-flash，OpenAI 兼容协议）。"""
    _init_llm_cache()
    from langchain_openai import ChatOpenAI
    s = get_settings()
    llm = ChatOpenAI(
        model=s.llm_model,
        api_key=s.llm_api_key,
        base_url=s.llm_base_url,
        temperature=temperature,
        streaming=streaming,
        **kwargs,
    )

    # Langfuse integration (optional) — 无环境变量时零影响
    callbacks = []
    if s.langfuse_public_key:
        try:
            from langfuse.callback import CallbackHandler
            callbacks.append(CallbackHandler(
                public_key=s.langfuse_public_key,
                secret_key=s.langfuse_secret_key,
                host=s.langfuse_host,
            ))
        except ImportError:
            pass  # langfuse 未安装，静默跳过
    if callbacks:
        llm.callbacks = callbacks

    return llm


def chat(system: str, user: str, temperature: float = 0.3) -> str:
    """便捷：一次性问答，返回文本。"""
    llm = get_llm(temperature=temperature)
    from langchain_core.messages import HumanMessage, SystemMessage
    resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return resp.content


if __name__ == "__main__":
    # 联调：用检索到的规则作上下文，让 LLM 仅据规则回答
    from ..knowledge import retriever
    q = "D&D 5E 中摔绊（Shove）动作如何判定？"
    rules = retriever.query_formatted(q, limit=3, body_limit=400)
    system = "你是D&D 5E规则助手。只能依据提供的规则原文回答，规则未覆盖时明说'规则未提供'，不要凭记忆编造。"
    user = f"问题：{q}\n\n规则原文（检索结果）：\n{rules}"
    print("=== RAG 检索到的规则 ===")
    print(rules[:200], "...\n")
    print("=== LLM 据规则回答 ===")
    print(chat(system, user))
