# aidm 文档索引

> AI DM（D&D 5E 跑团系统）文档导航。所有文档集中在 `aidm/docs/`。

## 文档清单

| 文档 | 内容 | 维护频率 | 说明 |
|------|------|----------|------|
| **README.md**（本档） | 索引 + 维护约定 | 偶尔 | 加新文档时更新此表 |
| **PRD.md** | 产品需求（做什么/功能/范围/验收） | 🟢 稳定 | 需求层，少改 |
| **ARCHITECTURE.md** | 架构（怎么设计/硬性判定链/选型/目录） | 🟡 中频 | 架构原则稳定，选型/目录随进度订正 |
| **BUILD.md** | 搭建指南 + P0→P5 路线图 | 🟡 中频 | 随各 Phase 进度更新状态 |
| **RULE_SPEC.md** | 规则规格书（400 条规则点 + 函数索引） | 🟢 稳定 | 规则参考档，改规则时才动 |
| **IMAGE_ASSETS.md** | 图片资产盘点 + 生成方案 | 🟡 中频 | 随 batch 进度更新 |
| **CHANGELOG.md** | 变动日志（做了什么） | 🔴 常更 | 每次改动后追加，倒序 |
| **DECISIONS.md** | 发现与决策记录（ADR 式） | 🔴 常更 | 选型/验收/漂移核对后追加 |

### 维护频率图例

- 🟢 **稳定参考档**：描述"应当是什么"，很少改（PRD / RULE_SPEC）。
- 🟡 **中频档**：随进度订正，但不每天动（ARCHITECTURE / BUILD / IMAGE_ASSETS）。
- 🔴 **常更档**：持续追加，是日常开发的活页（CHANGELOG / DECISIONS）。

---

## 常更档怎么用

### CHANGELOG.md — 记"做了什么"

- 每次改代码 / 改文档 / 建库 / 跑通验收后，在 `## [Unreleased]` 顶部加一条。
- 格式：`- 分类 一句话描述` + `文件:位置` 引用。分类用 `Added/Changed/Fixed/Docs/Build/Verified`。
- 倒序，最新在上。

### DECISIONS.md — 记"为什么 / 发现什么 / 待办什么"

- 做完一次选型、跑完一轮验收、或核对出文档↔代码漂移时，加一条 `D-NNN`。
- ADR 式：背景 → 现状/决策 → 后果 → 待办 → 关联。
- 标题尾标状态 `✅已落地 / 🟡进行中 / 🔵待办 / 🔴待确认`；状态变化就地改标注，不新增条，并在 CHANGELOG 记一笔。

### 两者的边界

| | CHANGELOG | DECISIONS |
|---|---|---|
| 记什么 | 实际改了什么（动作） | 为什么这么做 / 发现了什么 / 待办 |
| 粒度 | 一条改动一条记录 | 一个决策/发现一条记录 |
| 时机 | 改完即记 | 选定/发现即记 |
| 关系 | 可引用 `D-NNN` 说明动机 | 可引用 `CHANGELOG` 日期说明已落地 |

一次改动常常两边都留痕：动机与发现落 DECISIONS，动作落 CHANGELOG。

---

## 当前进度速览（2026-07-14）

> 详见 `ARCHITECTURE.md §0` 与 `BUILD.md §5`。此处仅导航。

| Phase | 状态 | 模块 |
|-------|------|------|
| P0 引擎核心 | ✅ | `engine/{dice,check,damage,conditions,combat}` + `data/equipment` |
| P1 状态层 | ✅ | `stats/{models,store}` |
| P2 知识层 RAG | ✅ | `knowledge/` 9 模块 + 三 Qdrant 集合已建库 |
| P3 编排层 | ✅ | `brain/{graph,llm,state}`（LangGraph 判定链端到端+HITL） |
| P4 API+交互 | ✅ | `api/main.py`(FastAPI) + `cli.py` |
| P5 前端 | 🔵 可选 | — |

> 上表为代码实测进度。`ARCHITECTURE.md §0`(v3) 与 `BUILD.md §5` 已订正同步，依据见 `DECISIONS.md` D-001~D-013。

---

## 外部资产与入口

| 项 | 位置 |
|----|------|
| 规则书源（只读） | `D:\game\dnd\5echm_web\`（data.js 6238 条 / topics HTML） |
| 项目代码 | `D:\game\dnd\aidm\src\aidm\` |
| 配置/密钥 | `D:\game\dnd\.env`（`key=`/`doc1`/`doc2`）→ `src/aidm/config.py` |
| 规则库 + 向量库 | `D:\game\dnd\aidm\data\rules.db`（Qdrant 本地文件，三集合） |
| 规则文本语料 | `D:\game\dnd\aidm\data\rules_text\`（141 页 .txt） |
| 图片资产 | `D:\game\dnd\aidm\data\images\`（112 张 + manifest） |
| 跑团存档 | `D:\game\dnd\aidm\data\saves\`（每个跑团一个 SQLite） |
| 自检入口 | `PYTHONPATH=src python -m aidm.<模块>` 各模块 `__main__` |
