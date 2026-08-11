"""P4 API 层 — FastAPI 端点，包裹 P3 编排与 P1 状态层。

路由已按功能域拆分至 aidm.api.routes 包：
  - campaign    战役管理
  - character   角色管理
  - chat        聊天跑团
  - combat      战斗状态
  - feats       专长系统
  - magic_items 魔法物品
  - loot        战利品
  - room        房间管理
  - stronghold  据点系统
  - scene       场景/世界
"""

from __future__ import annotations

import os

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .auth import SecurityHeadersMiddleware
from .cache import init_cache

# ── 路由模块 ──────────────────────────────────────────────────────────────────
from .routes import campaign, character, chat, combat, feats, loot, magic_items, room, scene, stronghold

app = FastAPI(title="AI DM", version="0.3.0")

# ── 安全头中间件 ──────────────────────────────────────────────────────────────
app.add_middleware(SecurityHeadersMiddleware)

# CORS — 允许的源从环境变量 AIDM_ALLOWED_ORIGINS 读取（逗号分隔）
# 未设置时默认 * （向后兼容），生产环境请设置具体域名
_allowed_origins_raw = os.getenv("AIDM_ALLOWED_ORIGINS", "*")
if _allowed_origins_raw.strip() == "*":
    _origins = ["*"]
else:
    _origins = [o.strip() for o in _allowed_origins_raw.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 全局 API Key 认证（可选，仅当 AIDM_API_KEY 环境变量存在时启用）────────────
if os.getenv("AIDM_API_KEY"):
    @app.middleware("http")
    async def _enforce_api_key(request, call_next):  # noqa: ANN001
        """Lightweight global gate — checks X-API-Key header."""
        from .auth import API_KEY_NAME, EXPECTED_API_KEY

        # Skip auth for health check, index, and static assets
        if request.url.path in ("/health", "/") or request.url.path.startswith("/static"):
            return await call_next(request)

        provided = request.headers.get(API_KEY_NAME, "")
        if provided != EXPECTED_API_KEY:
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid or missing API key"},
            )
        return await call_next(request)

# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    init_cache()


# ── 注册路由 ──────────────────────────────────────────────────────────────────
app.include_router(campaign.router)
app.include_router(character.router)
app.include_router(chat.router)
app.include_router(combat.router)
app.include_router(feats.router)
app.include_router(magic_items.router)
app.include_router(loot.router)
app.include_router(room.router)
app.include_router(stronghold.router)
app.include_router(scene.router)

# ── Socket.IO 实时同桌（升级版，基于 python-socketio）──────────────────────────
from .ws import manager, sio  # noqa: E402

# 静态前端（P5 交互层：Web 聊天界面）
_UI_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "ui", "static")
)

# 挂载静态文件目录（CSS/JS）
app.mount("/static", StaticFiles(directory=_UI_DIR), name="static")


@app.get("/")
def index():
    """Web 跑团前端（HTML 聊天页，调 /chat）。"""
    p = os.path.join(_UI_DIR, "index.html")
    if os.path.exists(p):
        return FileResponse(p)
    return {"status": "frontend not found", "path": p}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/coverage")
def coverage_manifest():
    """TEST-002: 实时生成 CoverageManifest 覆盖度报告（engine.coverage 权威实现）。

    返回 engine 模块的覆盖度状态汇总与明细，供 CI/门禁消费。
    同时注入 engine.performance_cache 的规则定义缓存统计（PERF-001）。
    """
    try:
        from ..engine.coverage import CoverageManifest
        m = CoverageManifest(ruleset_revision="2024.1").apply_wired_status()
        summary = m.summary()
        entries = {
            cid: {
                "status": e.status.value,
                "handlers": e.handlers,
                "unit_tests": e.unit_tests,
            }
            for cid, e in sorted(m.entries.items())
            if cid.startswith("engine.")
        }
        cache_stats = {}
        try:
            from ..engine.performance_cache import get_rule_cache
            cache_stats = get_rule_cache().stats() if hasattr(
                get_rule_cache(), "stats") else {"size": len(str(get_rule_cache()))}
        except Exception:
            cache_stats = {}
        return {
            "ruleset_revision": "2024.1",
            "summary": summary,
            "engine_entries": entries,
            "rule_cache": cache_stats,
        }
    except Exception as e:
        return {"error": f"CoverageManifest 生成失败: {e}"}


# ── Socket.IO ASGI 挂载 ────────────────────────────────────────────────────────
# 将 python-socketio 的 AsyncServer 包裹为 ASGI 应用，
# 与 FastAPI 应用组合，使 /ws/* 由 Socket.IO 处理，其余路由由 FastAPI 处理。
combined_app = socketio.ASGIApp(sio, app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(combined_app, host="0.0.0.0", port=8080)
