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

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# ── 项目根路径（去硬编码） ──────────────────────────────────────────────
# ★ review#10: 默认从代码位置推导（不再绑定某台 Windows 机器），
#   环境变量 AIDM_PROJECT_ROOT 可覆盖。
_PACKAGE_ROOT = Path(__file__).resolve().parent          # .../aidm/src/aidm
PROJECT_ROOT = Path(os.getenv(
    "AIDM_PROJECT_ROOT", str(_PACKAGE_ROOT.parents[2])))  # 仓库根

# ── 运行时数据目录（P0-09）──────────────────────────────────────────────
# 统一 SQLite/checkpoint/Qdrant/缓存/日志 的落盘根目录。
# Docker Compose 挂载 aidm-data:/data 并设置 AIDM_DATA_DIR=/data。
# 未设置时回退到 {PROJECT_ROOT}/aidm/data。
DATA_DIR = Path(os.getenv("AIDM_DATA_DIR", str(PROJECT_ROOT / "aidm" / "data")))

# .env 位置（项目上级目录）。可被环境变量 AIDM_ENV_FILE 覆盖。
DEFAULT_ENV = str(PROJECT_ROOT / ".env")


class Settings(BaseSettings):
    """全局配置。"""

    model_config = SettingsConfigDict(
        env_file=DEFAULT_ENV, env_file_encoding="utf-8",
        extra="ignore", case_sensitive=False,
    )

    # —— LLM ——
    # P0-10: 统一命名 AIDM_LLM_API_KEY / AIDM_LLM_BASE_URL / AIDM_LLM_MODEL；
    # 兼容旧名 key / fallback_key（不再鼓励 OPENAI_API_KEY 等多套名字）
    llm_api_key: str = Field("", validation_alias=AliasChoices(
        "AIDM_LLM_API_KEY", "key"))
    llm_fallback_key: str = Field("", validation_alias=AliasChoices(
        "AIDM_LLM_FALLBACK_KEY", "fallback_key"))
    llm_base_url: str = Field("https://api.senseaudio.cn/v1",
                              validation_alias=AliasChoices(
                                  "AIDM_LLM_BASE_URL", "LLM_BASE_URL"))
    llm_model: str = Field("deepseek-v4-flash", validation_alias=AliasChoices(
        "AIDM_LLM_MODEL", "LLM_MODEL"))

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
    # 运行环境: development | production（production 下未配置安全项时 fail closed）
    aidm_env: str = "development"
    # 会话令牌签名密钥（P0-03）。未配置时：development 用进程内随机密钥，
    # production 拒绝启动（fail closed）。
    aidm_session_secret: str = ""
    # 会话令牌有效期（秒），默认 8 小时
    aidm_session_ttl: int = 28800
    # DM 口令（P0-04）：设置后 /auth/session 需持正确口令才能换取 dm 角色令牌
    aidm_dm_token: str = ""
    # Redis 地址（P0-10）：统一 AIDM_REDIS_URL，用于离线消息队列/缓存
    aidm_redis_url: str = ""
    # 运行时路径/开关（P2-01: 全部经 Settings 读取，禁止散落 os.getenv）
    aidm_save_db: str = ""                  # 存档库覆盖路径（AIDM_SAVE_DB）
    aidm_rule_spec: str = ""                # RULE_SPEC 文档路径（AIDM_RULE_SPEC）
    aidm_morale: bool = False               # 士气系统开关（AIDM_MORALE）
    aidm_llm_cache: bool = True             # LLM 缓存开关（AIDM_LLM_CACHE）
    room_dispose_delay: float = 120.0       # 空房销毁延迟（ROOM_DISPOSE_DELAY）


@lru_cache
def get_settings() -> Settings:
    return Settings()


def is_production() -> bool:
    """是否生产模式（AIDM_ENV=production）。"""
    return get_settings().aidm_env.strip().lower() == "production"


def resolve_allowed_origins() -> list[str]:
    """统一解析 CORS 允许来源（HTTP 与 Socket.IO 共用，P0-06）。

    - AIDM_ALLOWED_ORIGINS 逗号分隔；默认 "*"
    - production 模式禁止 "*"（fail closed → 仅同源 localhost 默认）
    """
    raw = get_settings().aidm_allowed_origins.strip()
    if raw == "*":
        if is_production():
            # 生产模式未显式配置来源 → 仅允许本机同源，禁止通配
            return ["http://localhost:8080", "http://127.0.0.1:8080"]
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]


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
    log_dir = DATA_DIR / "logs"   # ★ review#10: 日志统一落 DATA_DIR（Docker /data 可写卷）
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        str(log_dir / "aidm_{time:YYYY-MM-DD}.log"),
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
    )
    return logger


# ── LLM 缓存 & 嵌入加速（★ review#10: 统一经 Settings，禁止散落 os.getenv）──
@lru_cache
def _llm_cache_enabled() -> bool:
    return get_settings().aidm_llm_cache


@lru_cache
def _embedding_device() -> str:
    s = get_settings()
    return "cpu"  # 默认 cpu；GPU 由部署环境配置（当前无独立 env 字段）


# 兼容旧引用（全部经 Settings 读取）
llm_cache_enabled = _llm_cache_enabled()
embedding_device = _embedding_device()
