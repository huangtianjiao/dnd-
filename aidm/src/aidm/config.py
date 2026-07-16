"""配置 — 从 .env 读取 LLM/向量库/嵌入设置。

.env 位于 D:\\game\\dnd\\.env（含 key/doc1/doc2）。LLM 用 senseaudio 网关的
deepseek-v4-flash；嵌入本地 bge-small-zh-v1.5（512维）。
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env 位置（项目上级目录）。可被环境变量 AIDM_ENV_FILE 覆盖。
DEFAULT_ENV = r"D:\game\dnd\.env"


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
    # 超过此比例时触发 LLM 压缩。0.25 = 占25%时压缩。
    summary_compress_ratio: float = 0.25

    # —— 规则数据 ——
    rules_datajs_path: str = r"D:\game\dnd\5echm_web\data.js"
    rules_topics_dir: str = r"D:\game\dnd\5echm_web\topics"
    rules_text_dir: str = r"D:\game\dnd\aidm\data\rules_text"


@lru_cache
def get_settings() -> Settings:
    return Settings()
