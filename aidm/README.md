# AIDM — AI 地下城主（D&D 5E 电子跑团系统）

> AI Dungeon Master：用确定性规则引擎执行 D&D 5E 判定，用 LLM 负责叙事与意图理解，规则与叙事分离——骰子由代码掷，故事由 AI 讲。

## 1. 项目介绍

AIDM 是一个 D&D 5E（龙与地下城第五版）电子跑团系统，让 AI 担任地下城主（DM）。核心理念是**"LLM 只在意图理解与叙事两端活动，中间判定全部由代码硬性执行"**，从而保证规则一致性、可审计性，同时保留 AI 叙事的灵活性。

### 核心能力

| 能力 | 说明 |
|------|------|
| **确定性规则引擎** | 骰子/检定/伤害/战斗/施法/专注/状态条件——全部用 `secrets` 密码学随机，LLM 不可绕过，每函数标注 400+ 规则点 ID |
| **RAG 规则检索** | Qdrant 三集合（规则书原文 + 判定规则文本 + 结构化规则点），BM25+向量 RRF 融合，中文别名富化 |
| **LangGraph 编排** | 8 节点判定链，HITL（human-in-the-loop）暂停/恢复，8 种动作类型硬性骰子分派 |
| **三层记忆系统** | 工作记忆（近 6 回合）+ 中期摘要 + 长期语义记忆，参考 Generative Agents 三分量评分 |
| **多人同桌** | WebSocket 实时同步，一人掷骰全员可见，Colyseus 风格房间生命周期 |
| **多智能体** | Director/RuleJudge/Narrator/CombatEngine/WorldManager/EnemyAI（渐进迁移中） |

### 规则数据覆盖

12 职业 · 10 种族 · 16 背景 · 74 专长 · 30 魔法物品 · 29 据点设施 · 58 位面 · 12 法术，全部对照规则书验证。

## 2. 技术栈

### 后端（Python 3.12）
| 组件 | 版本 | 用途 |
|------|------|------|
| LangGraph | 1.2.9 | 判定链状态机编排 |
| langchain-openai | 1.3.5 | LLM 客户端（接 senseaudio 网关 / DeepSeek） |
| sentence-transformers | 5.1.0 | 本地嵌入 bge-small-zh-v1.5（512 维） |
| qdrant-client | 1.18.0 | 向量库（本地文件模式，免 docker） |
| SQLModel + SQLite | 0.0.39 | 角色卡/战役/场景/战斗/日志持久化 |
| FastAPI | 0.118.3 | 43 个 REST 端点 |
| python-socketio | ≥5.11 | WebSocket 实时同桌 |

### 前端（Node.js ≥20）
| 组件 | 版本 | 用途 |
|------|------|------|
| Next.js | 14.2.5 | React 前端框架 |
| React | 18.3.1 | UI 库 |
| Tailwind CSS | 3.4.7 | 样式 |
| @3d-dice/dice-box | 1.1.4 | 3D 骰子动画 |
| socket.io-client | 4.8.3 | 实时通信 |

> 另有静态 HTML 备用前端（`ui/static/`），无需 Node 即可运行。

## 3. 本地启动方式

### 前置准备
1. Python 3.12（推荐 conda env `langchain_312`）
2. Node.js ≥20
3. 在 `D:\game\dnd\.env` 配置 API Key（见第 4 节）

### 后端启动（端口 8080）
```bash
cd D:/game/dnd/aidm
pip install -r requirements.txt          # 首次
./deploy/start.sh                         # Linux/macOS
# 或 Windows: deploy\start.bat
```
等价于 `PYTHONPATH=src python -m uvicorn aidm.api.main:app --port 8080 --reload`

### 前端启动（端口 4000）
```bash
cd D:/game/dnd/aidm/ui
npm install        # 首次
npm run dev        # → http://localhost:4000
```

### 规则库索引（首次必做）
规则 RAG 需先把规则书数据建入 Qdrant（首次会下载 bge 模型约 100MB）：
```bash
cd D:/game/dnd/aidm
PYTHONPATH=src python -m aidm.knowledge.indexer
```

### CLI 跑团（无前端，交互式）
```bash
cd D:/game/dnd/aidm
PYTHONPATH=src python -m aidm.cli
```

## 4. 环境变量说明

环境变量文件默认位于 `D:\game\dnd\.env`（项目根目录的上一级），可用环境变量 `AIDM_ENV_FILE` 覆盖路径。示例见 [`aidm/.env.example`](.env.example)。

| 变量 | 必填 | 默认值 | 说明 |
|------|:----:|--------|------|
| `key` | ✅ | — | senseaudio API Key（config.py 映射为 `llm_api_key`） |
| `LLM_BASE_URL` | | `https://api.senseaudio.cn/v1` | OpenAI 兼容端点 |
| `LLM_MODEL` | | `deepseek-v4-flash` | LLM 模型名 |
| `EMBEDDING_MODEL` | | `BAAI/bge-small-zh-v1.5` | 嵌入模型（改 bge-m3 需重建 Qdrant） |
| `EMBEDDING_DIM` | | `512` | 嵌入维度 |
| `QDRANT_COLLECTION` | | `dnd_rules` | data.js 语料集合 |
| `QDRANT_RULE_COLLECTION` | | `dnd_rule_text` | 规则文本集合 |

## 5. 分支规范

### 分支说明
| 分支 | 用途 | 权限 |
|------|------|------|
| `main` | 生产环境，只放稳定代码 | 只能通过 PR 合并，禁止直接推送 |
| `dev` | 日常开发集成分支 | 尽量通过 PR 合并 |
| `feature/*` | 功能开发分支 | 开发者自由提交 |
| `fix/*` | Bug 修复分支 | 开发者自由提交 |
| `release/*` | 发版分支 | 由负责人从 dev 切出 |

### 分支流程图
```
        main          生产环境，只放稳定代码
          ↑
         dev          日常开发集成分支
          ↑
   ┌──────┴──────┬──────────┐
feature/login  feature/order  fix/payment-bug
```

### 开发流程
```bash
# 1. 从 dev 拉分支
git checkout dev
git pull
git checkout -b feature/user-login

# 2. 开发完成后
git add .
git commit -m "feat: add user login"
git push origin feature/user-login

# 3. 发起 Pull Request 合并到 dev
# 4. 测试通过后，由负责人从 dev 合并到 main，触发上线
```

## 6. 提交规范

### 提交信息前缀
| 前缀 | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复问题 |
| `docs` | 文档修改 |
| `style` | 格式修改（不影响代码逻辑） |
| `refactor` | 代码重构 |
| `test` | 测试相关 |
| `chore` | 构建、依赖、配置修改 |
| `deploy` | 部署相关 |

示例：`git commit -m "feat: 新增怪物图片资源与前端交互原型"`

### 代码合并规则
1. 禁止直接推送到 `main`
2. 禁止直接在服务器上改代码
3. 所有功能从 `feature/*` 合并到 `dev`
4. 上线前由负责人从 `dev` 合并到 `main`
5. 合并前至少自己跑通本地项目
6. 重要功能需要另一个人 Review

### 问题处理流程
处理问题时按以下模板记录（可后期迁移到多维表格/Issue 系统）：

```
问题标题：
问题描述：
出现环境：本地 / 测试 / 生产
相关分支：
报错截图：
复现步骤：
期望结果：
实际结果：
已尝试方式：
优先级：高 / 中 / 低
```

## 7. 部署方式

详见 [`deploy/README.md`](deploy/README.md)。要点：

- **免 Docker**：Qdrant 本地文件模式，嵌入模型本地运行，LLM 走外部 API。
- 后端生产模式：`PYTHONPATH=src python -m uvicorn aidm.api.main:app --host 0.0.0.0 --port 8080`
- 前端构建：`cd ui && npm run build`
- 存档即文件：备份 `aidm/data/saves/save.db`（SQLite）即可。

## 8. 常见问题

**Q: 前端连不上后端？**
A: 检查 `ui/.env.local` 的 `NEXT_PUBLIC_API` 是否指向后端端口（默认 `http://localhost:8080`），后端是否已启动。

**Q: 首次启动很慢 / 报模型下载错误？**
A: 规则索引首次需下载 bge-small-zh-v1.5 嵌入模型（约 100MB，从 HF 镜像）。确保网络可达 huggingface.co 或 hf-mirror.com。

**Q: `.env` 放哪里？**
A: 默认 `D:\game\dnd\.env`（项目根目录上一级）。可设环境变量 `AIDM_ENV_FILE` 指向其他路径。

**Q: 端口被占用？**
A: 后端默认 8080，前端默认 4000。可改 `deploy/start.sh` 的 `--port`，及 `ui/package.json` 的 `next dev -p`。

**Q: 如何只跑规则引擎自检（不依赖 LLM/API）？**
A: `PYTHONPATH=src python -m aidm.engine.dice`（及 check/damage/conditions/combat 等各模块自带 `_self_test()`）。

**Q: 测试怎么跑？**
A: `cd D:/game/dnd/aidm && PYTHONPATH=src python -m pytest tests/`

## 项目结构

```
aidm/
├── README.md              # 项目说明、启动方式（本文件）
├── .gitignore             # 忽略文件
├── .env.example           # 环境变量示例
├── CHANGELOG.md           # 版本更新记录（精简发版版）
├── requirements.txt       # Python 依赖锁定
├── deploy/                # 部署脚本与说明
│   ├── README.md
│   ├── start.sh
│   └── start.bat
├── docs/                  # 文档目录（架构/流程/API/引擎/数据模型/模块索引…）
├── src/aidm/              # 后端源码
│   ├── config.py          # 配置（读 .env）
│   ├── cli.py             # CLI 入口
│   ├── engine/            # P0 规则引擎（骰子/检定/伤害/战斗/施法…）
│   ├── stats/             # P1 持久化（SQLModel + SQLite + NPC + Checkpoint）
│   ├── knowledge/         # P2 RAG 知识层（索引/检索/校验）
│   ├── brain/             # P3 编排（LangGraph 判定链 + 三层记忆 + 19 业务模块）
│   ├── agents/            # 多智能体（Director/RuleJudge/Narrator…）
│   ├── api/               # P4 API（FastAPI + WebSocket）
│   └── data/              # 规则数据（职业/种族/专长/魔法物品/位面…）
├── tests/                 # 测试套件（8 文件 ~138+ 用例）
├── scripts/               # 工具脚本（规则提取/图片生成）
└── ui/                    # 前端（Next.js 14 + 静态 HTML 备用）
```

## 文档导航

| 文档 | 说明 |
|------|------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 架构总览（六层架构） |
| [docs/PIPELINE.md](docs/PIPELINE.md) | 判定链流程图与三层记忆数据流 |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | REST 端点与 WebSocket 事件参考 |
| [docs/ENGINE_REFERENCE.md](docs/ENGINE_REFERENCE.md) | 规则引擎函数签名表 |
| [docs/DATA_MODELS.md](docs/DATA_MODELS.md) | 数据表结构与规则数据统计 |
| [docs/MODULE_INDEX.md](docs/MODULE_INDEX.md) | brain/agents 模块索引 |
| [docs/RULE_SPEC.md](docs/RULE_SPEC.md) | 400+ 规则点规格书 |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | 开发级详细变更记录 |
| [docs/DECISIONS.md](docs/DECISIONS.md) | 架构决策记录（ADR） |
