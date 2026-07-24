# AGENTS.md — AIDM Agent 入口

> AI Dungeon Master：确定性规则引擎执行 D&D 5E 判定，LLM 负责叙事。规则与叙事分离——骰子由代码掷，故事由 AI 讲。

## 项目定位

AIDM 是 D&D 5E 电子跑团系统。核心架构六层：`engine`（规则引擎）→ `stats`（持久化）→ `knowledge`（RAG 检索）→ `brain`（LangGraph 编排）→ `agents`（多智能体）→ `api`（FastAPI + WebSocket）。前端为 Next.js 14。

## 目录与任务路由

| 改动区域 | 目录 | 验证命令 |
|----------|------|----------|
| 骰子/检定/伤害/战斗规则 | `src/aidm/engine/` | `pytest tests/test_dice_engine.py tests/test_check_system.py tests/test_damage_system.py tests/test_combat_flow.py` |
| 状态条件 | `src/aidm/engine/conditions.py` | `pytest tests/test_conditions.py` |
| 专长选择 | `src/aidm/stats/` | `pytest tests/test_feat_selection.py` |
| API 端点 / WebSocket | `src/aidm/api/` | `pytest tests/test_api_endpoints.py` |
| 端到端流程 | `src/aidm/brain/` 或 `agents/` | `pytest tests/test_e2e_flow.py` |
| 前端 UI | `ui/` | `cd ui && npm run typecheck && npm run lint` |
| 全量验证 | — | `pytest tests/` |

> `pyproject.toml` 已配置 `pythonpath = ["src"]`，无需手动设 `PYTHONPATH`。

## 常用命令

```bash
# 后端启动（端口 8080）
cd aidm && PYTHONPATH=src python -m uvicorn aidm.api.main:app --port 8080 --reload

# 前端启动（端口 3000）
cd aidm/ui && npm run dev

# 规则引擎自检（不依赖 LLM/API）
# Windows 若报 UnicodeEncodeError，先运行：chcp 65001
cd aidm && PYTHONPATH=src python -m aidm.engine.dice          # 骰子
cd aidm && PYTHONPATH=src python -m aidm.engine.check          # 检定
cd aidm && PYTHONPATH=src python -m aidm.engine.damage         # 伤害
cd aidm && PYTHONPATH=src python -m aidm.engine.conditions     # 状态条件
cd aidm && PYTHONPATH=src python -m aidm.engine.combat         # 战斗

# 规则库索引（首次必做，修改规则文本后需重建）
cd aidm && PYTHONPATH=src python -m aidm.knowledge.indexer

# Lint（ruff 配置在 pyproject.toml）
cd aidm && ruff check src/ tests/
cd aidm && ruff format --check src/ tests/

# CLI 跑团（无前端，交互式）
cd aidm && PYTHONPATH=src python -m aidm.cli
```

> **注意**：`pytest tests/` 无需手动设 `PYTHONPATH`（pyproject.toml 已配置 `pythonpath = ["src"]`），但直接运行 `python -m aidm.*` 模块仍需 `PYTHONPATH=src`。

## 高风险区域

| 区域 | 风险 | 保护措施 |
|------|------|----------|
| `aidm/data/saves/` | 用户存档（SQLite），删除即丢失游戏进度 | **禁止删除或覆盖**；备份时复制整个目录 |
| `.env` | 含 senseaudio API Key | **禁止提交**（.gitignore 已排除）；修改后不 echo 到日志 |
| `aidm/data/rules.db/` | Qdrant 本地索引，可重建但耗时（需下载嵌入模型 ~100MB） | 修改 `rules_text/` 后必须运行 `python -m aidm.knowledge.indexer` 重建 |
| `aidm/data/rules_text/` | 规则文本源数据，是索引的唯一来源 | 修改后必须重建 Qdrant 索引 |
| `main` 分支 | 生产环境 | **禁止直接推送**；只能通过 PR 从 `dev` 合并 |

## 分支与提交

- 分支：`main`（生产）← `dev`（集成）← `feature/*` / `fix/*`
- 提交前缀：`feat` / `fix` / `docs` / `style` / `refactor` / `test` / `chore` / `deploy`
- 合并前至少跑通 `pytest tests/`

## 已知重复任务模式

以下模式在开发中反复出现，按流程执行可避免遗漏：

### 模式 1：规则引擎自检

- **触发**：修改 `src/aidm/engine/` 下任意模块
- **步骤**：运行对应模块的 `_self_test()`（如 `python -m aidm.engine.dice`）→ 运行对应测试文件 → 运行 `ruff check`
- **验证**：自检输出无异常 + pytest 全绿

### 模式 2：规则库索引重建

- **触发**：修改 `aidm/data/rules_text/` 下的规则文本
- **步骤**：运行 `python -m aidm.knowledge.indexer` → 等待嵌入模型加载和索引完成 → 用 CLI 跑团验证检索结果
- **验证**：索引器无报错 + RAG 检索返回预期规则

## 文档导航

| 文档 | 用途 |
|------|------|
| [README.md](README.md) | 项目说明、启动方式、环境变量 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 六层架构总览 |
| [docs/PIPELINE.md](docs/PIPELINE.md) | 判定链流程图与记忆数据流 |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | REST 端点与 WebSocket 事件 |
| [docs/ENGINE_REFERENCE.md](docs/ENGINE_REFERENCE.md) | 规则引擎函数签名表 |
| [docs/RULE_SPEC.md](docs/RULE_SPEC.md) | 400+ 规则点规格书 |
| [docs/DECISIONS.md](docs/DECISIONS.md) | 架构决策记录（ADR） |
