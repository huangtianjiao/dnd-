"""P0-07..P0-10 Docker 生产配置回归测试。

验证:
  - P0-07: Dockerfile CMD 指向 combined_app（Socket.IO 入口）
  - P0-08: next.config.js 配置 output=export（静态产物 out/ 可被 COPY）
  - P0-09: AIDM_DATA_DIR 统一数据目录（DB/checkpoint/qdrant 路径派生）
  - P0-10: compose 传递 AIDM_LLM_* / AIDM_REDIS_URL，不再依赖 OPENAI_* 死变量
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

_AIDM = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (_AIDM / rel).read_text(encoding="utf-8", errors="replace")


# ── P0-07: combined_app 入口 ────────────────────────────────────────

class TestDockerEntrypoint:
    def test_cmd_uses_combined_app(self):
        dockerfile = _read("Dockerfile")
        assert "combined_app" in dockerfile
        assert "uvicorn" in dockerfile
        # 不得再指向 app（缺 Socket.IO）
        m = re.search(r'CMD\s+\[[^\]]*uvicorn[^\]]*\]', dockerfile)
        assert m and "combined_app" in m.group(0)

    def test_healthcheck_present(self):
        dockerfile = _read("Dockerfile")
        assert "HEALTHCHECK" in dockerfile
        assert "/health" in dockerfile


# ── P0-08: Next.js 静态导出 ─────────────────────────────────────────

class TestNextExport:
    def test_output_export_configured(self):
        cfg = _read("ui/next.config.js")
        assert "output" in cfg and "export" in cfg

    def test_out_dir_produced(self):
        """干净构建产出 out/（Docker 阶段2 COPY 依赖它）。"""
        out = _AIDM / "ui" / "out"
        assert out.is_dir(), "ui/out 不存在——请先执行 npm run build"
        assert (out / "index.html").exists()


# ── P0-09: AIDM_DATA_DIR 统一数据目录 ──────────────────────────────

@pytest.mark.rule("engine.ruleset_manifest")
class TestDataDir:
    def test_db_under_data_dir(self, monkeypatch):
        from pathlib import Path
        import aidm.config as config
        from aidm.stats import store
        monkeypatch.setattr(config, "DATA_DIR", Path("C:/tmp/aidm-data"))
        assert str(Path("C:/tmp/aidm-data")) in str(Path(store._default_db_path()))

    def test_checkpoint_under_data_dir(self, monkeypatch):
        from pathlib import Path
        import aidm.config as config
        from aidm.brain import graph
        monkeypatch.setattr(config, "DATA_DIR", Path("C:/tmp/aidm-data"))
        assert str(Path("C:/tmp/aidm-data")) in str(Path(graph._checkpoint_db_path()))

    def test_qdrant_under_data_dir(self, monkeypatch):
        from pathlib import Path
        import aidm.config as config
        from aidm.knowledge import indexer
        monkeypatch.setattr(config, "DATA_DIR", Path("C:/tmp/aidm-data"))
        assert str(Path("C:/tmp/aidm-data")) in str(Path(indexer._qdrant_db_path()))

    def test_compose_mounts_data_dir(self):
        compose = _read("docker-compose.yml")
        assert "AIDM_DATA_DIR=/data" in compose
        assert "aidm-data:/data" in compose


# ── P0-10: compose 环境变量统一 ─────────────────────────────────────

class TestComposeEnv:
    def test_unified_llm_env(self):
        compose = _read("docker-compose.yml")
        assert "AIDM_LLM_API_KEY" in compose
        assert "AIDM_LLM_BASE_URL" in compose
        assert "AIDM_LLM_MODEL" in compose
        # 不再传 OPENAI_* 死变量
        assert "OPENAI_API_KEY" not in compose
        assert "OPENAI_BASE_URL" not in compose

    def test_redis_url_passed(self):
        compose = _read("docker-compose.yml")
        assert "AIDM_REDIS_URL=redis://redis:6379/0" in compose

    def test_session_secret_and_dm_token_passed(self):
        compose = _read("docker-compose.yml")
        assert "AIDM_SESSION_SECRET" in compose
        assert "AIDM_DM_TOKEN" in compose

    def test_settings_alias_llm_names(self):
        """config 支持 AIDM_LLM_*（新名）与旧别名。"""
        from aidm.config import Settings
        s = Settings(_env_file=None)
        assert hasattr(s, "llm_api_key")
        assert hasattr(s, "llm_base_url")
        assert hasattr(s, "llm_model")


# ── P1-12: Docker 冒烟 E2E 脚本 ──────────────────────────────────

class TestDockerSmokeScript:
    def test_script_exists_and_executable(self):
        script = _AIDM / "scripts" / "docker_smoke.sh"
        assert script.exists(), "scripts/docker_smoke.sh 缺失"
        src = script.read_text(encoding="utf-8")
        assert src.startswith("#!/usr/bin/env bash")

    def test_script_covers_full_chain(self):
        """冒烟必须覆盖: 构建→health→campaign→character→WS connect→action→重启持久化。"""
        src = _read("scripts/docker_smoke.sh")
        for required in (
            "docker compose build",
            "docker compose up -d",
            "/health",
            "create campaign",
            "create character",
            "auth/session",
            "socketio.Client",
            "sio.connect",
            'emit("action"',
            "docker compose restart",
            "重启后战役丢失",
        ):
            assert required in src, f"冒烟脚本缺少关键步骤: {required}"

    def test_ci_gate_script_exists(self):
        scripts = _AIDM / "scripts"
        assert (scripts / "run_cov_gate.py").exists()
        assert (scripts / "run_mutation.py").exists()