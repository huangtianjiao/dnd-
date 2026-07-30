"""LLM 客户端 — langchain_openai.ChatOpenAI（兼容 senseaudio 网关 deepseek-v4-flash）。

P3 LangGraph 编排将基于此客户端。base_url/key/model 来自 config（读 .env）。
支持主/备双 key：每次会话开始或继续时测试当前 key，失败自动切换到备用 key。
"""

from __future__ import annotations

import os
import time
from loguru import logger

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


# ── 主/备 key 管理 ──────────────────────────────────────────────────────
_active_key: str | None = None       # 当前使用的 key（None 表示尚未初始化）
_last_check_time: float = 0.0        # 上次测试时间戳
_KEY_CHECK_INTERVAL: float = 60.0    # key 测试缓存间隔（秒）


def test_llm_key(api_key: str, timeout: float = 10.0) -> bool:
    """测试 API key 是否可用（最小化调用，max_tokens=1）。"""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        s = get_settings()
        test_llm = ChatOpenAI(
            model=s.llm_model,
            api_key=api_key,
            base_url=s.llm_base_url,
            max_tokens=1,
            timeout=timeout,
            cache=False,
        )
        test_llm.invoke([HumanMessage(content="hi")])
        return True
    except Exception as e:
        logger.warning(f"API key 测试失败 (key={api_key[:8]}...{api_key[-4:]}): {e}")
        return False


def ensure_active_key() -> str:
    """确保当前使用的是可用的 API key，返回可用的 key。

    策略：
    1. 首次调用时测试主 key，成功则设为活跃 key
    2. 后续调用若距上次测试不足 60s，直接返回缓存结果
    3. 若当前 key 测试失败，尝试切换到另一个 key
    4. 两个 key 都不可用则抛出异常
    """
    global _active_key, _last_check_time
    s = get_settings()
    primary_key = s.llm_api_key
    fallback_key = s.llm_fallback_key

    now = time.time()
    # 缓存未过期，直接返回当前 key
    if _active_key and (now - _last_check_time < _KEY_CHECK_INTERVAL):
        return _active_key

    # 测试当前活跃 key（或首次使用主 key）
    test_key = _active_key or primary_key
    if test_key and test_llm_key(test_key):
        _active_key = test_key
        _last_check_time = now
        return _active_key

    # 当前 key 不可用，尝试切换到另一个 key
    switched = False
    if test_key != primary_key and primary_key:
        if test_llm_key(primary_key):
            _active_key = primary_key
            _last_check_time = now
            logger.info("API key 切换到主 key")
            switched = True
    if not switched and fallback_key and test_key != fallback_key:
        if test_llm_key(fallback_key):
            _active_key = fallback_key
            _last_check_time = now
            logger.info("API key 切换到备用 key")
            switched = True

    if not switched:
        raise RuntimeError("所有 API key 均不可用，请检查 .env 配置")

    return _active_key


def get_llm(temperature: float = 0.3, streaming: bool = False, **kwargs):
    """获取 LLM 实例（deepseek-v4-flash，OpenAI 兼容协议）。

    自动通过 ensure_active_key() 选择可用的 API key。
    """
    _init_llm_cache()
    from langchain_openai import ChatOpenAI
    s = get_settings()
    active_key = ensure_active_key()
    llm = ChatOpenAI(
        model=s.llm_model,
        api_key=active_key,
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
