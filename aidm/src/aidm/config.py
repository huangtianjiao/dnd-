"""配置 — 从 .env 读取 LLM/向量库/嵌入设置。

.env 位于项目根目录上级（默认 D:\\game\\dnd\\.env）。
所有路径基于 PROJECT_ROOT（环境变量 AIDM_PROJECT_ROOT 可覆盖）。
LLM 用 senseaudio 网关的 deepseek-v4-flash；嵌入本地 bge-small-zh-v1.5（512维）。
"""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# ── 项目根路径（去硬编码） ──────────────────────────────────────────────
# 默认 D:/game/dnd，可通过环境变量 AIDM_PROJECT_ROOT 覆盖
PROJECT_ROOT = Path(os.getenv("AIDM_PROJECT_ROOT", "D:/game/dnd"))

# .env 位置（项目上级目录）。可被环境变量 AIDM_ENV_FILE 覆盖。
DEFAULT_ENV = str(PROJECT_ROOT / ".env")


class Settings(BaseSettings):
    """全局配置。"""

    model_config = SettingsConfigDict(
        env_file=DEFAULT_ENV, env_file_encoding="utf-8",
        extra="ignore", case_sensitive=False,
    )

    # —— LLM ——
    llm_api_key: str = Field("", validation_alias="key")     # .env 中字段名为 key
    llm_base_url: str = "https://api.senseaudio.cn/v1"
    llm_model: str = "deepseek-v4-flash"

    # —— 嵌入（本地 bge 系列）——
    # 默认 bge-small-zh-v1.5（~95MB/512维，中文检索够用，下载快）；
    # 想要更强可改 "BAAI/bge-m3"（~2.3GB/1024维），需重建 Qdrant 集合。
    embedding_provider: str = "local"        # local | api
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    embedding_dim: int = 512

    # —— 向量库 Qdrant ——
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "dnd_rules"            # 数据语料(data.js 怪物/物品/法术)
    qdrant_rule_collection: str = "dnd_rule_text"   # 规则文本语料(rules_text 判定规则)

    # —— LLM 上下文窗口（token 数）——
    # 用于动态决定何时压缩 rolling_summary。
    # deepseek-v4-flash 支持 128k；如换更大窗口模型可调高。
    llm_context_window: int = 128000

    # rolling_summary 占上下文窗口的比例阈值。
    # 超过此比例时触发 LLM 压缩。
    # 调研结论：Mem0 生产环境推荐每次检索 <7000 tokens；
    # RULER 基准显示只有一半模型在 32K 时维持满意性能。
    # 15% 在 128K 窗口下 ≈ 19K tokens（~12000字符）触发压缩，
    # 给 narrate prompt 其他部分（工作记忆/长期记忆/规则摘要/骰子）留足空间。
    summary_compress_ratio: float = 0.15

    # —— 规则数据（基于 PROJECT_ROOT）——
    rules_datajs_path: str = str(PROJECT_ROOT / "5echm_web" / "data.js")
    rules_topics_dir: str = str(PROJECT_ROOT / "5echm_web" / "topics")
    rules_text_dir: str = str(PROJECT_ROOT / "aidm" / "data" / "rules_text")

    # —— Langfuse LLM 可观测性（可选，无环境变量时零影响）——
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    # —— 安全（可选，无环境变量时零影响）——
    # API Key 认证密钥，设置后所有 API 端点需携带 X-API-Key 请求头
    aidm_api_key: str = ""
    # CORS 允许的来源，逗号分隔，默认 *（允许所有）
    aidm_allowed_origins: str = "*"


@lru_cache
def get_settings() -> Settings:
    return Settings()


# ── Loguru 结构化日志 ─────────────────────────────────────────────────

def setup_logging(level: str = "INFO"):
    """配置 Loguru 日志。

    - 移除默认 handler，添加 stderr 输出（带颜色/结构化格式）
    - 添加按日滚动的文件日志（10MB 旋转，保留 7 天）

    Args:
        level: 控制台日志级别，默认 INFO。文件日志始终 DEBUG。
    """
    from loguru import logger

    logger.remove()  # 移除默认 handler
    logger.add(
        sys.stderr,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} | {message}",
    )
    log_dir = PROJECT_ROOT / "aidm" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        str(log_dir / "aidm_{time:YYYY-MM-DD}.log"),
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
    )
    return logger


# ── LLM 缓存 & 嵌入加速 ────────────────────────────────────────────────
# LLM Cache
llm_cache_enabled = os.getenv("AIDM_LLM_CACHE", "true")

# Embedding device
embedding_device = os.getenv("AIDM_EMBEDDING_DEVICE", "cpu")
