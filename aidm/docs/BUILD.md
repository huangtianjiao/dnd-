# BUILD — 搭建指南与分阶段路线图

> 从零搭建 AI DM 系统的操作手册。配套 `PRD.md`（做什么）/ `ARCHITECTURE.md`（怎么设计）/ `RULE_SPEC.md`（规则依据）。

## 1. 环境要求

| 组件 | 版本 | 用途 |
|------|------|------|
| Python | 3.12.11 | 后端/引擎/编排（`langchain_312` conda env 已配齐） |
| Node.js | ≥20 | 前端（P5，可选） |
| Docker | — | 不需要（Qdrant 本地文件模式，免 docker） |

> P0/P1 完全离线；P2 用本地 bge 嵌入（免 docker，首次需从 HF 镜像下载模型）；P3 起需 LLM API（deepseek-v4-flash @ senseaudio）。

## 2. 依赖清单（`langchain_312` env 已装）

| 包 | 版本 | 用途 |
|----|------|------|
| langchain | 1.3.13 | LLM 应用 |
| langgraph | 1.2.9 | 编排状态机 |
| langchain-openai | 1.3.5 | OpenAI 兼容 API |
| openai | 1.107.2 | LLM SDK |
| qdrant-client | 1.18.0 | 向量库客户端（P2） |
| sqlmodel | 0.0.39 | ORM（P1 状态层） |
| pydantic | 2.11.8 | 数据模型/校验 |
| fastapi | 0.118.3 | API（P4） |
| sentence-transformers | 5.1.0 | 本地 embedding（P2 默认 bge-small-zh） |
| beautifulsoup4 + lxml | — | HTML 解析（提取脚本用） |

> 前端依赖（P5，`ui/package.json`）：next 14.2.5 / react 18.3.1 / tailwindcss 3.4.7 / @3d-dice/dice-box ^1.1.4 / socket.io-client ^4.8.3（无 shadcn/ui，自研组件）。

## 3. 项目结构

```
D:\game\dnd\
├── 5echm_web/              # 规则书数据源（只读）
├── .env                   # 密钥（key=/doc1/doc2），config.py 读
├── aidm/
│   ├── docs/              # README/PRD/ARCHITECTURE/BUILD/RULE_SPEC/IMAGE_ASSETS/CHANGELOG/DECISIONS
│   ├── scripts/          # extract_rules.py / generate_images.py / generate_images_batch2.py
│   ├── data/
│   │   ├── rules_text/    # 141页纯文本（判定规则语料）
│   │   ├── rules.db/      # Qdrant 本地文件（三集合，P2 产物）
│   │   ├── images/        # 112张配图 + manifest
│   │   └── saves/         # 跑团存档
│   └── src/aidm/
│       ├── config.py      # pydantic-settings 读 .env
│       ├── cli.py         # P4 CLI 入口（python -m aidm.cli）
│       ├── engine/        # P0 ✅ dice/check/damage/conditions/combat
│       ├── stats/         # P1 ✅ models(SQLModel) + store(CRUD)
│       ├── knowledge/     # P2 ✅ parse_datajs/parse_rulespec/embedding/indexer/retriever/verifier/hybrid/aliases/eval_retrieval
│       ├── brain/         # P3 ✅ graph(LangGraph编排)/llm/state + 16 业务模块（含 memory/world/image_gen/rest/social/loot/…，共 19 子模块）
│       ├── agents/       # 多智能体层（6 Agent：Director/Narrator/Combat/WorldManager/RuleJudge/EnemyAI，渐进迁移中）
│       └── api/           # P4 ✅ main(FastAPI 43 端点) + ws(Socket.IO 同桌)
```

## 4. 快速开始（自检）

```bash
cd D:/game/dnd/aidm
PY=/d/software/Anaconda3/envs/langchain_312/python.exe

# P0 引擎各模块自检（离线）
PYTHONPATH=src $PY -m aidm.engine.dice
PYTHONPATH=src $PY -m aidm.engine.check
PYTHONPATH=src $PY -m aidm.engine.damage
PYTHONPATH=src $PY -m aidm.engine.conditions
PYTHONPATH=src $PY -m aidm.engine.combat
# P1 状态层自检（离线）
PYTHONPATH=src $PY -m aidm.stats.store
# P2 知识层（首次下载 bge 模型，离线）
PYTHONPATH=src $PY -m aidm.knowledge.indexer        # 建 80 条子集索引 + 检索
PYTHONPATH=src $PY -m aidm.knowledge.eval_retrieval  # 纯向量 vs hybrid recall
# P3 编排端到端（需 LLM API）
PYTHONPATH=src $PY -m aidm.brain.graph
# P4 CLI 跑团 / API 服务（需 LLM API）
PYTHONPATH=src $PY -m aidm.cli
PYTHONPATH=src $PY -m uvicorn aidm.api.main:combined_app --host 0.0.0.0 --port 8080
```

## 5. 分阶段搭建路线图（P0→P5）

每阶段独立可验收。**P0/P1 完全离线；P2 用本地 embedding（免 docker）；P3 起需 LLM API。** 已全部完成至 P5（含 WebSocket 同桌 + 多智能体 agents/ + 三层记忆，组件重构进行中）。

### Phase 0 — 引擎核心（硬性判定地基）✅ 已完成
**目标**：骰子/检定/伤害/状态/装备数据全部代码化，离线可跑。8 模块自检通过 + 全栈联调跑通。
**已交付**：
1. `engine/dice.py` ✅ 完成（R-CHK-004/015/024/025~030, R-CMB-029, R-GLS-005）
2. `engine/check.py` — D20检定三步(R-CHK-001)、属性检定(R-CHK-010)、豁免(R-CHK-011)、攻击命中(R-CMB-017)、天然20/1(R-CMB-022/023)、被动检定(R-DM-012)
3. `engine/damage.py` — 伤害掷骰(R-DMG-001)、抗性易伤免疫顺序(R-DMG-003~006/ R-QCK-002)、HP扣减(R-DMG-007)、临时HP(R-DMG-009)、死亡豁免(R-DMG-017)、治疗(R-DMG-020)、伤害下限0(R-DMG-002)
4. `engine/conditions.py` — 14状态效应(R-GLS-044~058)+力竭(R-GLS-047/R-QCK-004)、不叠加(R-GLS-043)
5. `engine/combat.py` — 先攻(R-CMB-002)、回合/动作经济(R-CMB-004/012/013)、专注维持(R-GLS-013)
6. `data/equipment.py` — 护甲表/武器表/词条/精通/钱币(R-ITM-003/012/014/015/001)
**验收**：`python -m aidm.engine.*` 各模块自检通过；一次完整攻击命中→伤害→HP扣减流程跑通（纯代码）。

### Phase 1 — 状态层（持久化）✅ 已完成
**目标**：角色卡/场景/战斗状态 SQLite 持久化，存档即拷文件。已交付 `stats/models.py`+`stats/store.py`，自检通过。
**步骤**：`stats/models.py`(SQLModel: character/campaign/scene/combat/log) → `stats/store.py`(CRUD) → rolling summary。
**验收**：建角色卡→打3回合战斗→存档→重载状态不丢。

### Phase 2 — 知识层（RAG）✅ 已完成
**目标**：规则可检索+可校验。三语料 + hybrid + 别名富化，15 条评测集 recall@3 量化。
**步骤**：`knowledge/parse_datajs.py`(data.js→6238条) + `parse_rulespec.py`(RULE_SPEC→400条) → `knowledge/embedding.py`(本地 bge-small-zh) → `knowledge/indexer.py`(三集合→Qdrant 本地文件) → `hybrid.py`(BM25+向量 RRF) + `aliases.py`(玩家同义词富化) → `knowledge/verifier.py`(校验判定参数)。
**部署**：无需 docker。Qdrant 本地文件模式 `QdrantClient(path=data/rules.db)`；首次 `python -m aidm.knowledge.indexer` 建库（首次下载 bge 模型，走 HF 镜像）。
**验收**：问"擒抱怎么判"→返回规则原文+出处；`eval_retrieval.py` recall@3 达标；校验器对错误判定参数能驳回。

### Phase 3 — 编排层（LangGraph）✅ 已完成
**目标**：AI DM 对话循环，硬性判定链落地。`brain/graph` 端到端跑通（attack/cast/ability_check/start_combat，含天然20重击）。
**步骤**：`brain/graph.py`(StateGraph: classify→retrieve→verify→[retrieve_retry/confirm HITL]→resolve(纯代码骰子)→narrate→apply) → `brain/state.py`(GameState) → `brain/llm.py`(deepseek-v4-flash 客户端)。prompt 内嵌于 classify/narrate 节点（无独立 prompts.py）。`MemorySaver` checkpointer + interrupt(HITL)。
**验收**：玩家输入→走完判定链→AI叙事+状态更新；HITL 可 interrupt 经 `/chat/resume` 恢复。

### Phase 4 — API 层 + 交互层 ✅ 已完成
**目标**：前后端分离 + CLI 跑团。
**步骤**：`api/main.py`(FastAPI，43 个端点，含 REST + WebSocket) + `api/ws.py`(python-socketio AsyncServer，多人同桌 Room 生命周期) + `cli.py`(交互式 CLI，HITL responder)。HITL 经 `/chat/resume` 恢复。
**验收**：HTTP 客户端能跑一轮对话+查状态；CLI 能开跑。

### Phase 5 — 前端 ✅ 已完成
**目标**：可视跑团界面。
**步骤**：`ui/static/`(原生 HTML 单页应用，零构建快速迭代) + `ui/app/`(Next.js 14 App Router + Tailwind CSS + @3d-dice/dice-box 3D 骰子 + socket.io-client 实时同步) → 三栏 VTT 布局：对话区 + 骰子动画/日志 + 角色卡 + 战斗追踪器 + 场景面板。无 shadcn/ui，组件自研。
**状态**：✅ 已完成（Next.js 14 + Tailwind + 3D 骰子，组件重构进行中）。
**验收**：浏览器开跑，骰子/状态实时显示。

## 6. 配置（`config.py` 读 `.env`）

配置由 `src/aidm/config.py`（pydantic-settings BaseSettings）管理，读 `D:\game\dnd\.env`。非 config.yaml。

| 项 | 默认值 | 说明 |
|----|--------|------|
| `key` | （填入 .env） | senseaudio API key，映射为 `llm_api_key` |
| `llm_base_url` | `https://api.senseaudio.cn/v1` | OpenAI 兼容端点 |
| `llm_model` | `deepseek-v4-flash` | LLM 模型 |
| `embedding_provider` | `local` | local=本地 bge（不走 API） |
| `embedding_model` | `BAAI/bge-small-zh-v1.5` | 512维；可改 `bge-m3`（需重建集合） |
| `qdrant_url` | `http://localhost:6333` | 本地文件模式时不使用 |

> 切换 embedding 模型（如 bge-small→bge-m3）需重建 Qdrant 集合（`indexer.reset_collection`）。详见 DECISIONS D-002/D-010。

## 7. 标注与索引约定

- 代码每条规则实现处标注 `规则: R-XXX-NNN` + `出处: topics/.../xxx.htm`
- 模块完成后在 `RULE_SPEC.md` 末尾"实现回填区"补一行 `路径::函数(签名)#规则ID`，闭合代码↔规则双向索引
