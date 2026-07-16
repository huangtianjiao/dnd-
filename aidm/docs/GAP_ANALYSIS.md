# AIDM 实现差距分析与开源框架调研报告

> 生成时间: 2026-07-15
> 基于调研报告 `AI_DM模型技术能力与架构总报告.html` 与 AIDM 项目源码逐项对比
> 调研范围: GitHub 开源项目 (1k+ stars)、学术论文、技术博客

---

> ## ⚠️ 部分内容已过时（2026-07-15 更新）
> 本文档生成于功能实现之前/同期，以下章节描述的"未实现"项实际已落地，请以 `IMPLEMENTATION_VS_REPORT.md` 为准：
> - §3.1 三层记忆系统 — ✅ 已实现（`brain/memory.py` ~493 行）
> - §3.2 记忆与会话工具 0/5 — ✅ 已实现 5/5
> - §3.4 多智能体架构 — ✅ `agents/` 包已建（6 个 Agent，渐进迁移中）
> - §3.5 NPC 人格持久化 — ✅ `stats/npc.py` 已建
> - §3.6 Checkpoint/Rewind — ✅ `stats/checkpoint.py` 已建
> - §3.7 Session 存档/读档 — ✅ `/session/end` 端点 + `generate_recap` 已接
> - §3.8 动态图片/产物生成 — ✅ `brain/image_gen.py` 已建
> - §3.9 Enemy AI — ✅ `agents/enemy_ai.py` 已建
> - §3.10 战术地图渲染 — ✅ `image_gen.render_battlefield_ascii()` 已实现
> - §一 架构对比表相关行 — 见上
>
> 仍准确（确实未实现）：§3.3 空间推理工具 0/7

## 目录

1. [项目实现总览](#一项目实现总览)
2. [已实现能力清单](#二已实现能力清单)
3. [未实现能力与差距分析](#三未实现能力与差距分析)
4. [开源框架调研结果](#四开源框架调研结果)
5. [实施优先级建议](#五实施优先级建议)
6. [附录: 全部调研项目索引](#六附录全部调研项目索引)

---

## 一、项目实现总览

### 工具覆盖率

| 能力域 | 推荐工具数 | 已实现 | 缺失 | 覆盖率 |
|---|---|---|---|---|
| 骰子与检定 | 5 | 5 | 0 | 100% ✅ |
| 战斗系统 | 8 | 7 | 1 | 87% ✅ |
| 角色与资源 | 6 | 6 | 0 | 100% ✅ |
| 空间与世界 | 7 | 0 | 7 | 0% ❌ |
| 规则查询 RAG | 3 | 3 | 0 | 100% ✅ |
| 记忆与会话 | 5 | 0 | 5 | 0% ❌ |
| **总计** | **34** | **21** | **13** | **62%** |

### 架构对比

| 维度 | 调研报告推荐 | AIDM 实际实现 | 差距 |
|---|---|---|---|
| 编排方式 | 5 个独立 Agent 通过共享 GameState 协作 | 单一 LangGraph StateGraph，7 个线性节点 | 无自主 Agent 间通信 |
| 状态模型 | 统一 Pydantic v2 GameState | TypedDict (brain/state.py) | 类型安全但非 Pydantic |
| 记忆架构 | 三层记忆 (工作/中期/长期) + 观察提取 + 检索管线 | 仅 rolling_summary 文本追加 | **完全缺失** |
| NPC 持久化 | 每个 NPC 维护独立记忆文档集合 + 关系演化 | 临时内存对象，无持久化 | **完全缺失** |
| 空间推理 | 网格/距离/视线/掩护/AoE/寻路/渲染 7 个工具 | 战斗有基础移动，无网格/空间推理 | **完全缺失** |
| Checkpoint/Rewind | 游戏状态快照，支持回退 | 仅 LangGraph MemorySaver (HITL 用) | **游戏状态快照缺失** |
| 动态图片生成 | 叙事过程中动态插图 + 战术地图 + 交互产物 | 仅静态游戏资产图片生成 | **动态叙事插图缺失** |

---

## 二、已实现能力清单

### 2.1 骰子与检定工具 (5/5)

| 工具 | 实现位置 | 说明 |
|---|---|---|
| `roll_dice` | `engine/dice.py:roll_dice()` | 支持 d20/d6 等多种骰子表达式 |
| `roll_check` (ability_check) | `engine/check.py:ability_check()` | 属性检定 vs DC |
| `roll_attack` (attack_roll) | `engine/check.py:attack_roll()` | 攻击检定 vs AC，支持重击 |
| `roll_saving_throw` | `engine/check.py:saving_throw()` | 豁免检定 |
| `roll_initiative` | `engine/combat.py:roll_initiative()` | 先攻排序，同组怪物共用先攻 |

### 2.2 战斗系统工具 (7/8)

| 工具 | 实现位置 | 说明 |
|---|---|---|
| `create_encounter` | `engine/combat.py:start_combat()` | 创建遭遇 |
| `initiate_combat` | 同上 | 开始战斗：掷先攻、排序、进入第1轮 |
| `execute_action` | `engine/actions.py:resolve_combat_action()` | 执行战斗行动 |
| `advance_turn` | `engine/combat.py:advance_turn()` | 推进到下一参战者回合 |
| `manage_condition` | `engine/conditions.py` | 14种5e标准状态 + 持续时间追踪 |
| `get_combat_state` | `stats/store.py:load_combat()` | 查询当前战斗全貌 |
| `resolve_death` | `engine/damage.py` + DeathTracker | 死亡豁免处理 |
| ~~`render_battlefield`~~ | **未实现** | 无战场渲染功能 |

### 2.3 角色与资源工具 (6/6)

| 工具 | 实现位置 | 说明 |
|---|---|---|
| `create_character` | `api/main.py:create_character()` + `brain/char_create.py` | 角色创建 |
| `get_character_sheet` | `api/main.py:get_character()` | 查看完整角色卡 |
| `update_character` | `stats/store.py:save_character()` | 修改属性/HP/资源 |
| `manage_spell_slots` | `engine/spellcasting.py` | 法术位消耗/恢复/查询 |
| `manage_inventory` | `stats/models.py:Character.add_to_inventory()` | 物品增/删/装备/转移 |
| `take_rest` | `brain/rest.py:short_rest()/long_rest()` | 短休/长休恢复计算 |

### 2.4 规则查询 RAG (3/3)

| 工具 | 实现位置 | 说明 |
|---|---|---|
| `query_rules` | `knowledge/hybrid.py:search_spec_hybrid()` | Hybrid 检索: BM25(字符级) + 向量(bge-small) RRF 融合 |
| `lookup_spell` | `data/spells.py` | 静态法术数据库查询 |
| `lookup_monster` | `knowledge/indexer.py:search()` | 从 data.js RAG 查怪物属性 |

### 2.5 其他已实现能力

| 能力 | 实现位置 | 说明 |
|---|---|---|
| LangGraph 编排 | `brain/graph.py` | 单一 StateGraph，7 节点线性流转 |
| SQLite 持久化 | `stats/store.py`, `stats/models.py` | 角色/战役/场景/战斗/日志全持久化 |
| WebSocket 多人同桌 | `api/ws.py` | Socket.IO + Colyseus 风格 Room 生命周期管理 |
| HITL 人机协作 | `brain/graph.py:124-135` | interrupt/resume 机制，DM 可确认关键判定 |
| 社交流程 | `brain/social.py` | NPC 态度系统 (友好/冷漠/敌对)、态度转换阈值、四步社交互动 |
| 探索流程 | `brain/exploration.py` | 旅行步调、导航检定、被动察觉、随机遭遇 |
| 静态图片生成 | `scripts/generate_images.py` | 预定义游戏资产图片生成 (护甲/职业/硬币/怪物等) |
| 据点系统 | `brain/stronghold.py` | DMG 第八章据点建设与管理 |
| 战利品系统 | `brain/loot.py`, `brain/loot_distribution.py` | 战利品生成与分配 |
| 升级系统 | `brain/levelup.py` | XP 表 (20级)、升级五步骤、专长选择 |

---

## 三、未实现能力与差距分析

### 3.1 三层记忆系统 🔴 最高优先级

**调研报告推荐**: 三层记忆架构 — 工作记忆 (近 6 回合直接注入) + 中期记忆 (滚动摘要 + 观察提取) + 长期记忆 (Qdrant 向量检索 + 重要性加权 + 时间衰减 + Rerank)

**AIDM 实际实现**: **完全未实现**

当前仅有:
- `rolling_summary`: Campaign 表中的文本字段，每回合追加 `[轮] {player_input[:30]} → {narration[:40]}`
- `Log` 表: 审计日志，非可检索的记忆存储

**缺失组件**:
- ❌ 工作记忆层 (最近几回合注入上下文)
- ❌ 中期记忆层 (观察提取、滚动摘要压缩)
- ❌ 长期记忆层 (向量 DB 语义检索)
- ❌ 观察提取管线 (从 DM 叙事中自动提取关键信息)
- ❌ 重要性加权 (LLM 对每条观察打分 1-10)
- ❌ 时间衰减评分 (指数衰减 based on last access time)
- ❌ Rerank 步骤 (对检索结果重新排序)
- ❌ "前情提要"浓缩摘要生成 (500-1000 tokens，下次 Session 注入)
- ❌ 记忆嵌入 Qdrant (Qdrant 当前仅用于规则 RAG)

**影响**: 无法防止 "Session 3 崩塌" — 上下文窗口无法承载完整对话历史，导致规则遗忘、叙事断裂。

---

### 3.2 记忆与会话工具 (0/5) 🔴 最高优先级

**调研报告推荐 5 个工具**:

| 工具 | 功能 | AIDM 实现 |
|---|---|---|
| `create_observation` | 回合结束后生成观察 (重要事件/关系变化/线索揭示) | **未实现** |
| `create_memory` | 创建持久化记忆 (内容 + 关键词 + 重要性权重) | **未实现** |
| `retrieve_memories` | 检索相关记忆 (语义 + 关键词 + 时间衰减) | **未实现** |
| `get_session_context` | 获取当前会话全局快照 | **未实现** (仅 rolling_summary 文本) |
| `save_checkpoint` | 存档 (可回退) | **未实现** (仅 LangGraph MemorySaver 用于图执行状态) |

---

### 3.3 空间推理工具 (0/7) 🔴 高优先级

**调研报告推荐 7 个工具**:

| 工具 | 功能 | AIDM 实现 |
|---|---|---|
| `measure_distance` | 计算两点间距离 (含海拔差) | **未实现** |
| `calculate_aoe` | 计算范围效应覆盖的目标 (球/锥/线/方/柱) | **未实现** |
| `check_line_of_sight` | 判定视线是否通畅 | **未实现** |
| `check_cover` | 判定掩护等级 (半/四分之三/全掩蔽) | **未实现** |
| `calculate_movement` | 寻路计算 (含地形难度) | **部分实现** — `engine/combat.py:move()` 有基础移动，但无网格/寻路 |
| `manage_location` | 更新/查询地点描述和连接关系 | **部分实现** — `stats/models.py:Scene` 有文本地点描述 |
| `move_party` | 队伍移动到新地点 + 触发遭遇判定 | **部分实现** — `brain/exploration.py` 有旅行步调/里程 |

**影响**: 战术战斗无法正确运作 — LLM 无空间推理能力，需要确定性空间工具提供网格/视线/掩护/AoE 计算。

---

### 3.4 多智能体架构 🟡 中优先级

**调研报告推荐**: 5 个独立 Agent (Director / Narrator / Combat Engine / World Manager / Rule Judge) 通过共享 GameState 协作

**AIDM 实际实现**: 单一 LangGraph StateGraph，7 个线性节点

```
classify → retrieve → verify → confirm → resolve → narrate → apply
```

**差距分析**:
- `classify()` 节点充当 "Director"，通过 LLM 意图分类路由
- 但没有自主 Agent 间通信，没有独立的 Agent 人格
- 所有逻辑在一个图中线性流转，而非多个 Agent 协作

**升级路径**: 当前单一线性图可通过添加子图 (subgraph) 和条件边升级为多 Agent 协作架构。LangGraph 原生支持这一模式。

---

### 3.5 NPC 人格持久化 🟡 中优先级

**调研报告推荐**: 每个 NPC 维护独立记忆文档集合 (向量存储)，包含背景/性格/知识范围/关系历史；NPC 会记仇/感恩，信任等级随时间推移变化

**AIDM 实际实现**: **完全未实现**

当前 NPC 处理是极简且临时的:
- `brain/social.py:NPC` dataclass: 有 `name`, `attitude`, `role`, `knowledge`, `goals`, `secrets`, `cr`
- 在 `_resolve_social()` 中创建，**不持久化到数据库**
- `stats/models.py` 中**无 NPC 表** — NPC 仅作为字符串引用在 `Scene.npcs_json` 中
- **无关系演化追踪** — 没有 PC 与 NPC 之间的持久关系跟踪器
- **无人格记忆检索** — 因为 NPC 不持久化且无记忆系统

---

### 3.6 Checkpoint/Rewind 🟡 中优先级

**调研报告推荐**: 完整状态快照，支持回退

**AIDM 实际实现**: **未实现**

- 仅 LangGraph 的 `MemorySaver` checkpointer 存在 (`graph.py:508`)
- 这仅用于图执行状态检查点 (HITL interrupt/resume)
- **无游戏状态检查点/回退功能** — 无快照系统，无回滚能力

---

### 3.7 Session 存档/读档 🟡 中优先级

**调研报告推荐**: Session 结束时生成完整摘要 (10-20 条要点) + 持久化所有状态到 SQLite + 生成记忆嵌入到 Qdrant + 生成"前情提要"浓缩摘要 (500-1000 tokens) + Checkpoint

**AIDM 实际实现**: **部分实现**

| 功能 | 状态 | 详情 |
|---|---|---|
| 持久化状态到 SQLite | ✅ 已实现 | `stats/store.py` 保存角色、战役、场景、战斗状态、日志 |
| Session 列表/加载 | ✅ 已实现 | `list_campaigns()`, `get_campaign_state()` |
| Session 结束摘要生成 | ❌ 未实现 | 无显式 "session end" 摘要生成 |
| 记忆嵌入 Qdrant | ❌ 未实现 | Qdrant 仅用于规则 RAG |
| "前情提要"浓缩摘要 | ❌ 未实现 | 无 500-1000 token 浓缩摘要生成 |
| Checkpoint with rewind | ❌ 未实现 | 无游戏状态快照/回退 |

---

### 3.8 动态图片/产物生成 🟢 低优先级

**调研报告推荐**: 场景插图 (战斗/关键场景配图)、战术地图 (ASCII 或可视化网格)、角色卡渲染、信件/密文/地图碎片等剧情道具

**AIDM 实际实现**: **部分实现** — 仅静态游戏资产图片生成

已有:
- `scripts/generate_images.py` (29KB): 为护甲、职业、硬币、条件、掩护、骰子、魔法物品、怪物、种族、场景、法术学派、据点、武器等类别生成预定义静态图片
- `scripts/generate_images_batch2.py` (14KB): 第二批图片生成
- `data/images/` 目录: 已生成的静态图片资产

缺失:
- ❌ 叙事过程中的动态场景插图 (无与 narrate 节点集成的图片生成)
- ❌ 战术地图/战场渲染 (无空间网格可视化)
- ❌ 动态角色卡生成 (仅有静态职业/种族图片)
- ❌ 交互产物生成 (信件、密文、地图碎片等可玩道具)

---

### 3.9 Enemy AI 🟢 低优先级

**调研报告推荐**: LLM 决策但受规则约束，基于怪物"战术"描述 (兽人好斗冲锋、地精狡猾逃跑、龙优先用喷吐武器)，temperature 0.3-0.5，HP < 50% 触发逃跑/投降逻辑

**AIDM 实际实现**: **未实现**

- 怪物行动由 DM 手动操作 (`ws.py:on_monster_action`)
- 无自主 Enemy AI，无基于怪物战术描述的 LLM 决策

---

### 3.10 战术地图渲染 🟡 中优先级

**调研报告推荐**: `render_battlefield` — ASCII 网格或可视化战场地图

**AIDM 实际实现**: **未实现**

- 无战场渲染功能
- 战斗状态通过 JSON 返回 (`get_combat_state`)，前端自行展示

---

## 四、开源框架调研结果

### 4.1 三层记忆系统 — 框架推荐

#### Tier 1: 直接可用的记忆框架

##### 1. Mem0 — 通用 AI 记忆层
- **GitHub**: https://github.com/mem0ai/mem0
- **Stars**: ~60,900
- **语言**: TypeScript (48.7%) / Python (48.1%)
- **License**: Apache-2.0
- **核心价值**: 通用记忆层，支持向量存储 (Qdrant) + 时序推理 + 观察提取。`ADD` API 自动从 DM 叙事中提取观察。
- **三层映射**:
  - Session-scoped memories → 中期记忆
  - Cross-session user/campaign memories → 长期记忆
- **集成方式**: AIDM 使用 Mem0 作为中期和长期记忆骨干。Session 级记忆映射到中期；跨 session 用户/战役记忆映射到长期。

##### 2. Letta / MemGPT — OS 式三层记忆
- **GitHub**: https://github.com/letta-ai/letta
- **Stars**: ~23,800
- **语言**: Python (99.5%)
- **License**: Apache-2.0
- **核心价值**: Platform for stateful agents with advanced memory that can learn and self-improve over time. Originally MemGPT, implements an OS-like memory hierarchy inspired by virtual memory management.
- **三层映射**:
  - Core memory (in-context, always visible) → 工作记忆
  - Recall memory (conversation history) → 中期记忆
  - Archival memory (vector DB, semantic search) → 长期记忆
- **集成方式**: AIDM 可几乎直接采用 Letta 的三层架构。Core memory 持有当前场景/PC 状态；recall memory 保持 session 记录；archival memory 存储跨 session 传说、NPC 关系和历史事件。

##### 3. Generative Agents (Stanford Research) — 记忆流参考实现
- **GitHub**: https://github.com/joonspk-research/generative_agents
- **Stars**: ~21,800
- **语言**: Python
- **License**: Apache-2.0
- **核心价值**: Reference implementation for the Stanford paper "Generative Agents: Interactive Simulacra of Human Behavior." Introduces the memory stream architecture with importance scoring, recency weighting, and relevance-based retrieval.
- **关键算法**:
  - Memory stream: complete record of agent experiences
  - Importance scoring: LLM rates each observation's importance (1-10 scale)
  - Recency weighting: exponential decay based on time since last access
  - Relevance scoring: semantic similarity between query and memory
  - Retrieval function: combines recency + relevance + importance scores
  - Reflection mechanism: synthesizes higher-level conclusions from memories
- **集成方式**: 这是长期记忆层的基础架构。AIDM 应实现相同的评分公式: `score = α * recency + β * importance + γ * relevance`。反思机制可为中期层生成 session 摘要并提取反复出现的叙事主题。

##### 4. Honcho — 会话级记忆基础设施
- **GitHub**: https://github.com/plastic-labs/honcho
- **Stars**: ~6,000
- **语言**: Python (FastAPI server)
- **License**: AGPL-3.0
- **核心价值**: Memory infrastructure for building stateful agents that understand changing people, agents, groups, projects, and ideas over time.
- **集成方式**: AIDM 可使用 Honcho 的 session 抽象作为中期记忆 (每次游玩 session = 一个 Honcho session)。peer representation 功能对建模个体 PC 人格和 NPC 关系很有价值。

#### Tier 2: 通用 Agent 框架的记忆模块

##### 5. LangChain Memory — 可组合记忆模块
- **GitHub**: https://github.com/langchain-ai/langchain
- **Stars**: ~141,800
- **语言**: Python/TypeScript
- **License**: MIT
- **记忆模块**:
  - `ConversationBufferMemory`: stores conversation in buffer (working memory)
  - `ConversationSummaryMemory`: maintains rolling summaries of conversations (mid-term memory)
  - `ConversationSummaryBufferMemory`: hybrid of summary + buffer
  - `VectorStoreRetrieverMemory`: stores memories in vector DB, retrieves semantically (long-term memory)
  - `ConversationTokenBufferMemory`: token-based buffer management
  - `EntityMemory`: extracts and tracks information about entities
- **集成方式**: AIDM 可直接组合 LangChain 的记忆模块: `ConversationBufferMemory` 用于最近回合，`ConversationSummaryMemory` 用于 session 摘要，`VectorStoreRetrieverMemory` 用于跨 session 语义检索。`EntityMemory` 模块特别适合追踪 NPC 属性、PC 物品栏和任务状态。

##### 6. MemOS / MemTensor — 自演化记忆 OS
- **GitHub**: https://github.com/MemTensor/MemOS
- **Stars**: ~10,200
- **语言**: TypeScript
- **License**: Apache-2.0
- **核心价值**: Self-evolving memory OS for LLM & AI Agents with ultra-persistent memory, hybrid-retrieval, and cross-task skill reuse. Claims 35.24% token savings.
- **集成方式**: AIDM 可使用 MemOS 的 "memory cubes" 将战役传说、NPC 知识、PC 背景和世界状态分离到独立但可组合的知识库中。图结构支持实体间关系查询。

#### 记忆框架与三层架构的映射关系

| 记忆层级 | 最佳框架选择 | 关键能力 |
|---|---|---|
| **工作记忆** (近 6 回合，直接注入) | LangChain `ConversationBufferMemory`, Letta core memory, CrewAI short-term memory | 简单环形缓冲区 + 直接上下文注入 |
| **中期记忆** (当前 session，滚动摘要 + 观察提取) | Mem0 (session-level), LangChain `ConversationSummaryMemory` + `EntityMemory`, Honcho sessions, Letta recall memory | 滚动摘要、实体追踪、从叙事中提取观察 |
| **长期记忆** (跨 session，向量 DB + 重要性加权 + 时间衰减 + rerank) | Generative Agents 架构 (importance + recency + relevance), Mem0 (archival), Letta (archival), MemOS (graph memory), MemoryOS (hierarchical) | 向量 DB 语义检索 + 重要性评分 + 指数时间衰减 + 重排序 |

---

### 4.2 空间推理工具 — 框架推荐

#### 核心发现

**没有任何单一框架覆盖全部 7 项空间需求。** 空间推理生态是碎片化的: roguelike 工具包提供 FOV + 寻路但不提供 D&D 特定的 AoE/掩护; VTT 项目有网格 + LoS 但是完整应用而非库; 寻路库是单一用途的。

#### Tier 1: 综合性空间库

##### 1. rot.js — Roguelike Toolkit (JavaScript)
- **GitHub**: https://github.com/ondras/rot.js
- **Stars**: ~2,700
- **语言**: JavaScript
- **License**: BSD-3-Clause
- **覆盖能力**: 网格管理 ✅ | FOV/视线 ✅ | A* 寻路 ✅ | AoE 形状 (部分) ✅ | ASCII 渲染 ✅
- **核心价值**: 最完整的 JS 单库方案。提供地牢生成、视野计算、寻路、噪声生成、调度和显示渲染。
- **适用场景**: 前端战术地图渲染 + 后端调用 rot.js 算法

##### 2. RogueSharp — .NET Roguelike Library
- **GitHub**: https://github.com/FaronBracy/RogueSharp
- **Stars**: ~631
- **语言**: C# (.NET Standard)
- **License**: MIT
- **覆盖能力**: 网格管理 ✅ | FOV/视线 ✅ | A* 寻路 ✅ | AoE 形状 (圆/方/菱形) ✅ | ASCII 渲染 (部分) ✅
- **核心价值**: .NET 最完整方案。Map = 矩形 Cell 网格 (IsTransparent, IsWalkable, IsExplored, IsInFov)。PathFinder 类支持最短路径。Cell 选择支持圆形、方形、菱形 (Bresenham 中点圆算法)。
- **适用场景**: 算法参考设计 (C# → Python 移植)

##### 3. PathFinding.js — 纯寻路库
- **GitHub**: https://github.com/qiao/PathFinding.js
- **Stars**: ~8,700
- **语言**: JavaScript
- **License**: MIT
- **覆盖能力**: 网格管理 ✅ | A* 寻路 ✅ (11 种算法)
- **核心价值**: 最佳纯寻路 JS 库。包括 AStarFinder, BestFirstFinder, BreadthFirstFinder, DijkstraFinder, IDAStarFinder, JumpPointFinder 及双向变体。
- **适用场景**: 如仅需寻路功能

#### Tier 2: D&D 特定空间系统

##### 4. foundryvtt/dnd5e — D&D 5e 空间系统
- **GitHub**: https://github.com/foundryvtt/dnd5e
- **Stars**: ~566
- **语言**: JavaScript
- **License**: 专有 (Terms-limited)
- **覆盖能力**: 网格管理 ✅ | 视线/视野 ✅ | AoE 模板 (锥/球/方/线) ✅ | 掩护 (部分) ✅ | 地图渲染 ✅
- **核心价值**: D&D 5e 最完整空间系统。AoE 模板 (cone/sphere/cube/line)、网格测量、掩护计算。
- **适用场景**: 研究 AoE 模板和掩护计算的算法逻辑

##### 5. RPTools/maptool — 成熟 VTT 应用
- **GitHub**: https://github.com/RPTools/maptool
- **Stars**: ~917
- **语言**: Java
- **License**: AGPL-3.0
- **覆盖能力**: 网格管理 ✅ | 视线/视野阻挡 ✅ | AoE 模板 ✅ | 地图渲染 ✅
- **核心价值**: 成熟的虚拟桌面应用。展示了生产级的网格管理、LoS/视野阻挡和拓扑实现。
- **适用场景**: 参考 VTT 级别的空间推理实现

#### 空间框架能力矩阵

| 框架 | Stars | 语言 | 网格管理 | LoS/FOV | 寻路 | AoE 模板 | 掩护检测 | 渲染 |
|---|---|---|---|---|---|---|---|---|
| **PathFinding.js** | 8.7k | JS | ✅ | ❌ | ✅ (A*) | ❌ | ❌ | ❌ |
| **rot.js** | 2.7k | JS | ✅ | ✅ | ✅ (A*) | 部分 | ❌ | ✅ (ASCII) |
| **RogueSharp** | 631 | C# | ✅ | ✅ | ✅ (A*) | ✅ | ❌ | 部分 (ASCII) |
| **foundryvtt/dnd5e** | 566 | JS | ✅ | ✅ | 部分 | ✅ | 部分 | ✅ |
| **RPTools/maptool** | 917 | Java | ✅ | ✅ | 部分 | ✅ | 部分 | ✅ |

#### 掩护检测 — 最大缺口

**无开源库提供 D&D 5e 式的半掩护/四分之三掩护/全掩护计算。** 需要自定义实现，可能使用光线投射 (raycasting) 对障碍物网格进行计算。

参考 foundryvtt/dnd5e 的掩护计算逻辑:
- 半掩护: 目标被一个遮挡物挡住至少一半身体
- 四分之三掩护: 目标被遮挡至少 75%
- 全掩护: 目标完全被遮挡

---

### 4.3 多智能体架构 — 框架推荐

#### 核心发现

**LangGraph 是最佳选择** — AIDM 已在使用它。其 typed StateGraph 直接映射"单一事实来源 GameState"，`add_conditional_edges()` 实现 Director 的条件路由，`interrupt()` API 支持 HITL。

#### Tier 1: 主要框架候选

##### 1. LangGraph — 低级编排框架
- **GitHub**: https://github.com/langchain-ai/langgraph
- **Stars**: ~37,300
- **语言**: Python
- **License**: MIT
- **最后更新**: 2026-07-15 (每日提交)
- **核心价值**: Low-level orchestration framework for building long-running, stateful, multi-agent workflows. Core primitive is the `StateGraph`, where each node is an agent/function and edges define control flow.
- **适配架构**:
  - **Shared state**: Yes — the `StateGraph` passes a typed state object (Pydantic/TypedDict) through every node. This maps directly to your "single source of truth GameState."
  - **Conditional routing**: Yes — `add_conditional_edges()` lets the Director Agent route to Narrator / Combat / World / Rule agents based on classified intent. This is a headline feature.
  - **HITL interrupt/resume**: Yes — first-class `interrupt()` API. You can pause before a rule ruling or combat resolution, surface state to the DM/player, edit state, and resume. Durable execution persists across failures/restarts.
  - **Multi-agent orchestration**: Yes — supports supervisor/hierarchical patterns, subgraphs (each specialist agent = a subgraph), and handoffs.
- **注意事项**: Lower-level than CrewAI; you write more wiring code, but gain precise control over state transitions — exactly what a rules-heavy D&D engine needs.

##### 2. CrewAI — 角色扮演自主 Agent 框架
- **GitHub**: https://github.com/crewAIInc/crewAI
- **Stars**: ~55,500
- **语言**: Python
- **License**: MIT
- **最后更新**: 2026-07-14 (非常活跃)
- **核心价值**: Framework for orchestrating role-playing, autonomous AI agents. Two main primitives: **Crews** (autonomous agent collaboration with dynamic task delegation) and **Flows** (event-driven, structured-state workflows with conditional branching).
- **适配架构**:
  - **Shared state**: Partial — Flows support structured state (Pydantic BaseModel) for precise control; Crews share context via task outputs rather than a persistent shared object.
  - **Conditional routing**: Yes — Flows support `@router` decorators and `or_`/`and_` logical operators for branching.
  - **HITL**: Yes — supported within Flows/Crews for human-agent collaboration.
  - **Multi-agent orchestration**: Yes — this is CrewAI's core strength. The "role-playing autonomous agents" model maps naturally onto Narrator/Combat/World/Rule personas.
- **注意事项**: The shared-state model is less explicit than LangGraph's StateGraph. If you need strict single-source-of-truth state mutation across agents, LangGraph gives you tighter guarantees.

##### 3. AG2 (formerly AutoGen) — 开源 AgentOS
- **GitHub**: https://github.com/ag2ai/ag2
- **Stars**: ~4,800
- **语言**: Python
- **License**: Apache-2.0
- **最后更新**: 2026-07-14 (active; this is the post-Microsoft continuation of AutoGen)
- **核心价值**: Open-source "AgentOS." Agents interact via conversation patterns: swarms, group chats, nested chats, sequential chats. Supports tool use, RAG, code execution, structured outputs.
- **适配架构**:
  - **Shared state**: Not a first-class concept — state lives in the conversation history between agents rather than a shared GameState object. You'd implement GameState as a tool/service agents query.
  - **Conditional routing**: Indirect — routing emerges from conversation patterns and custom reply methods rather than an explicit graph.
  - **HITL**: Yes — `UserProxyAgent` provides seamless human feedback integration.
  - **Multi-agent orchestration**: Yes — strong here. Group chat patterns let a "manager agent" (your Director) route messages to specialized agents.

#### 框架能力矩阵

| 框架 | Stars | License | 多 Agent 编排 | 共享状态 | 条件路由 | HITL 中断/恢复 |
|---|---|---|---|---|---|---|
| **LangGraph** | ~37.3k | MIT | ✅ (supervisor, subgraphs, handoffs) | **✅** (typed StateGraph state passed node-to-node) | **✅** (`add_conditional_edges`) | **✅** (`interrupt()`, durable) |
| **CrewAI** | ~55.5k | MIT | ✅ (Crews, role-based agents) | 部分 (Flows structured state) | ✅ (Flows `@router`, `or_`/`and_`) | ✅ |
| **AG2 (AutoGen)** | ~4.8k | Apache-2.0 | ✅ (group chat, swarms, nested chats) | 弱 (conversation-history-based) | 间接 (emergent from patterns) | ✅ (`UserProxyAgent`) |

#### 最终推荐

**使用 LangGraph 作为核心编排层。** 原因:

1. **Shared GameState = StateGraph state.** LangGraph 的 typed state object 通过每个节点传递，就是你的"单一事实来源 GameState"。每个专项 Agent (Narrator, Combat, World, Rule) 成为读取和写入该状态类型字段的节点/子图。

2. **Conditional routing = Director Agent 的工作。** `add_conditional_edges()` 让 Director 分类玩家输入 ("我攻击哥布林" → 战斗意图) 并路由到适当的专项 Agent。这是 LangGraph 的看家本领。

3. **HITL = interrupt/resume.** LangGraph 的 `interrupt()` API 在关键决策前暂停执行 (规则裁决、战斗结果)，让人类检查/编辑 GameState，然后恢复。持久化执行意味着长战役能在崩溃中存活。

4. **已在技术栈中。** AIDM 已使用 LangGraph，升级路径清晰: 当前单一线性图 → 添加子图 (subgraph) 和条件边 → 多 Agent 协作架构。

---

### 4.4 NPC 人格持久化 — 框架推荐

#### Tier 1: 直接可用的 NPC 持久化框架

##### 1. Letta / MemGPT — 最直接的 NPC 持久化框架
- **GitHub**: https://github.com/letta-ai/letta
- **Stars**: ~23,800
- **语言**: Python (99.5%)
- **License**: Apache-2.0
- **核心价值**: Platform for stateful agents: AI with advanced memory that can learn and self-improve over time. Originally MemGPT, implements an OS-like memory hierarchy inspired by virtual memory management.
- **NPC 持久化映射**: Each NPC becomes a stateful agent with its own memory context window. The core MemGPT architecture implements an OS-like memory hierarchy (core memory, archival memory, recall memory) that maps perfectly to NPC persona memory needs.
- **集成方式**: AIDM 可几乎直接采用 Letta 的三层架构。Core memory 持有当前场景/PC 状态；recall memory 保持 session 记录；archival memory 存储跨 session 传说、NPC 关系和历史事件。

##### 2. Generative Agents (Stanford Research) — NPC 关系演化的黄金标准
- **GitHub**: https://github.com/joonspk-research/generative_agents
- **Stars**: ~21,800
- **语言**: Python
- **License**: Apache-2.0
- **核心价值**: Reference implementation behind "Generative Agents: Interactive Simulacra of Human Behavior" (Park et al., 2023). Directly implements NPC personality persistence through a memory stream architecture where agents store observations, retrieve them via recency/importance/relevance scoring, reflect on memories to form higher-level conclusions, and make plans.
- **NPC 持久化映射**: The Smallville simulation demonstrates 25 agents with distinct personalities who remember interactions, form relationships, and evolve socially. This is the gold-standard reference architecture for NPC relationship evolution and semantic retrieval of persona memory.
- **集成方式**: 以 Generative Agents 的记忆流架构为参考模型 — 每个 NPC 维护一个记忆流，存储观察 (observations)，通过 recency+importance+relevance 评分检索相关记忆。这与三层记忆系统的长期记忆层天然契合。

##### 3. SillyTavern — AI 角色扮演社区的主导前端
- **GitHub**: https://github.com/SillyTavern/SillyTavern
- **Stars**: ~30,700
- **语言**: JavaScript (86.2%)
- **License**: AGPL-3.0
- **核心价值**: LLM Frontend for Power Users. The dominant open-source frontend for character-based AI roleplay. Implements persistent character cards (persona, description, scenario, first message), world info/lorebooks for knowledge scoping, and supports long-term memory extensions.
- **NPC 持久化映射**: Its character card format has become a de facto standard in the AI roleplay community. For an AI DM application, SillyTavern's architecture for managing multiple persistent characters with distinct personalities, each maintaining their own context and memory, is highly relevant. The ecosystem includes memory plugins (e.g., Smart-Memory) that handle semantic retrieval of character memories.
- **集成方式**: 参考 SillyTavern 的角色卡格式 (persona/description/scenario) 和 lorebook 知识范围管理，为 AIDM 的 NPC 设计持久化人格档案。

##### 4. mem0 — NPC 记忆后端
- **GitHub**: https://github.com/mem0ai/mem0
- **Stars**: ~60,900
- **语言**: TypeScript (48.7%) / Python (48.1%)
- **License**: Apache-2.0
- **核心价值**: Universal memory layer for AI Agents. mem0 provides a universal, model-agnostic memory layer that can be integrated into any AI agent system.
- **NPC 持久化映射**: For NPC personality persistence, mem0 can serve as the backend memory infrastructure that stores and retrieves NPC interaction histories, relationship states, and persona details. It supports semantic search over stored memories, enabling NPCs to "remember" relevant past interactions contextually. Its API allows storing facts, preferences, and contextual information per-NPC, making it suitable for maintaining individual NPC memory stores.
- **集成方式**: 使用 mem0 的 per-user/per-agent 记忆隔离特性，为每个 NPC 创建独立的记忆存储。

---

### 4.5 动态图片/产物生成 — 框架推荐

#### Tier 1: 图像生成框架

##### 1. Hugging Face Diffusers — 基础库
- **GitHub**: https://github.com/huggingface/diffusers
- **Stars**: ~34,100
- **语言**: Python (100%)
- **License**: Apache-2.0
- **核心价值**: Diffusers: State-of-the-art diffusion models for image, video, and audio generation in PyTorch. The foundational Python package for running diffusion models programmatically.
- **集成方式**: 这是最底层的集成点: import pipeline, pass prompt derived from narrative context, receive generated image. Apache-2.0 许可证和丰富文档使其成为构建 AI DM 后端自定义图像生成管线的推荐选择。

##### 2. ComfyUI — 最强大的节点式工作流
- **GitHub**: https://github.com/comfyanonymous/ComfyUI
- **Stars**: ~121,000
- **语言**: Python (99.6%)
- **License**: GPL-3.0
- **核心价值**: The most powerful and modular diffusion model GUI, api and backend with a graph/nodes interface.
- **集成方式**: 对于 D&D 游戏过程中的动态场景插图，ComfyUI 提供了可视化工作流编辑器和 REST API。工作流可设计为: 从叙事文本提示生成场景插图、使用 ControlNet/IP-Adapter 创建角色一致性肖像、制作战术/战斗地图影像。

##### 3. AUTOMATIC1111 Stable Diffusion WebUI
- **GitHub**: https://github.com/AUTOMATIC1111/stable-diffusion-webui
- **Stars**: ~164,000
- **语言**: Python (87.5%)
- **License**: AGPL-3.0
- **核心价值**: The most widely-used Stable Diffusion interface. Features a built-in API (`--api` flag) that enables programmatic image generation from external applications.
- **集成方式**: 对于 AI DM，这允许: 通过 txt2img 将叙事描述转换为场景插图、使用 img2img 和 textual inversion/embeddings 生成角色卡视觉、制作产物视觉 (地图、信件、密文)。Dynamic Prompts 扩展对模板化奇幻场景提示特别有用。

##### 4. FLUX.1 — SOTA 开源文生图模型
- **GitHub**: https://github.com/black-forest-labs/flux
- **Stars**: ~25,700
- **语言**: Python (100%)
- **License**: Apache-2.0 (代码); 模型权重有不同许可
- **核心价值**: Official inference repo for FLUX.1 models. FLUX.1 represents the current state-of-the-art in open-weight text-to-image generation, surpassing earlier Stable Diffusion models in prompt adherence and image quality.
- **集成方式**: 对于需要高质量动态场景插图、角色肖像和产物视觉的 AI DM，FLUX 模型提供卓越结果。注意: FLUX.1 [schnell] 是 Apache-2.0，适合商业应用。

#### Tier 2: 地图生成工具

##### 5. Azgaar's Fantasy Map Generator
- **GitHub**: https://github.com/Azgaar/Fantasy-Map-Generator
- **Stars**: ~5,800
- **语言**: HTML (57.1%) / TypeScript (34.3%)
- **License**: NOASSERTION
- **核心价值**: Web application generating interactive and highly customizable maps. The premier open-source fantasy world map generator.
- **集成方式**: 对于 AI DM 应用，此工具可程序化生成整体战役世界地图。输出为 SVG 格式，完全可编辑。

##### 6. mewo2/terrain (Fantasy Map Generator)
- **GitHub**: https://github.com/mewo2/terrain
- **Stars**: ~3,000
- **语言**: JavaScript
- **License**: NOASSERTION
- **核心价值**: A lightweight JavaScript fantasy map generator based on Martin O'Leary's map generation algorithm. Generates hand-drawn-style fantasy maps with coastlines, rivers, settlements, and labels.
- **集成方式**: 为 AI DM 应用提供一个更简单的、可嵌入的 Azgaar 替代方案，用于生成区域或局部地图。JavaScript 实现意味着它可在浏览器端 DM 界面中运行。

#### 许可证考量

| 许可证类型 | 框架 |
|---|---|
| **最宽松 (MIT/Apache-2.0)** | Letta, Generative Agents, mem0, Diffusers, InvokeAI, FLUX 代码, LangChain, LangGraph |
| **Copyleft (GPL/AGPL)** | SillyTavern (AGPL-3.0), RisuAI (GPL-3.0), ComfyUI (GPL-3.0), AUTOMATIC1111 (AGPL-3.0), Fooocus (GPL-3.0) |

> **注意**: AGPL-3.0 特别要求如果软件作为网络服务提供，必须披露源代码。如果构建商业 SaaS AI DM，优先选择 Apache-2.0 许可的组件，或将 AGPL 工具作为通过 API 访问的独立服务。

---

## 五、实施优先级建议

### 优先级矩阵

| 优先级 | 缺失能力 | 影响程度 | 推荐框架/方案 | 预估工作量 |
|---|---|---|---|---|
| 🔴 P0 | 三层记忆系统 | 防止 Session 3 崩塌的核心机制 | LangChain Memory 模块 + Generative Agents 评分公式 | 2-3 周 |
| 🔴 P0 | 记忆与会话工具 (5个) | 跨 Session 可玩性的基础 | mem0 作为记忆服务后端 | 1-2 周 |
| 🔴 P1 | 空间推理工具 (7个) | 战术战斗必需 | rot.js 算法参考 + Python 自行实现 | 2-3 周 |
| 🟡 P2 | 多智能体架构升级 | 从单 Graph 到多 Agent 协作 | LangGraph 子图 + 条件边 (已有基础) | 1-2 周 |
| 🟡 P2 | NPC 人格持久化 | 长期战役沉浸感 | Generative Agents 记忆流架构 | 1-2 周 |
| 🟡 P3 | Checkpoint/Rewind | 存档回退能力 | LangGraph checkpointer + SQLite 快照 | 1 周 |
| 🟡 P3 | 战术地图渲染 | 战斗可视化 | ASCII 网格自实现 (参考 rot.js Display 类) | 3-5 天 |
| 🟢 P4 | 动态图片生成 | 叙事沉浸感增强 | Hugging Face Diffusers API 集成 | 1-2 周 |
| 🟢 P4 | Enemy AI | 怪物自主行动 | LLM 决策 + 规则约束 (temperature 0.3-0.5) | 1 周 |

### 分阶段实施路线图

#### Phase 1: 记忆系统建设 (2-3 周) 🔴

**目标**: 实现三层记忆架构，防止 Session 3 崩塌

**任务清单**:
1. 工作记忆层: 基于 `ConversationBufferMemory` 实现最近 6 回合对话缓冲
2. 中期记忆层: 基于 `ConversationSummaryMemory` 实现滚动摘要压缩
3. 长期记忆层: 基于 `VectorStoreRetrieverMemory` 实现跨 Session 向量检索
4. 观察提取管线: 每回合结束后 LLM 自动提取关键信息 (重要事件/关系变化/线索揭示)
5. 重要性加权: LLM 对每条观察打分 (1-10 scale，参考 Generative Agents)
6. 时间衰减评分: 指数衰减 based on last access time
7. Rerank 步骤: 对检索结果重新排序
8. 记忆嵌入 Qdrant: 将游戏记忆嵌入 Qdrant (新建 collection，与规则 RAG 分离)
9. "前情提要"浓缩摘要: Session 结束时生成 500-1000 tokens 浓缩摘要

**关键文件变更**:
- 新建 `src/aidm/memory/` 包
  - `working_memory.py` — 工作记忆 (对话缓冲)
  - `mid_term_memory.py` — 中期记忆 (滚动摘要 + 观察提取)
  - `long_term_memory.py` — 长期记忆 (向量检索 + 重要性 + 时间衰减)
  - `retrieval_pipeline.py` — 检索管线 (语义 → 重要性加权 → 时间衰减 → Rerank → Top-K)
- 修改 `src/aidm/brain/graph.py` — 在 narrate 节点后添加观察提取步骤
- 修改 `src/aidm/knowledge/indexer.py` — 新增 game_memory collection

#### Phase 2: 空间推理工具建设 (2-3 周) 🔴

**目标**: 实现网格/距离/视线/掩护/AoE/寻路/渲染 7 个空间工具

**任务清单**:
1. `measure_distance`: 计算两点间距离 (含海拔差) — 欧几里得距离 + 海拔差
2. `calculate_aoe`: 计算范围效应覆盖的目标 (球/锥/线/方/柱) — 参考 foundryvtt/dnd5e 的 AoE 模板
3. `check_line_of_sight`: 判定视线是否通畅 — 光线投射 (raycasting) 对障碍物网格
4. `check_cover`: 判定掩护等级 (半/四分之三/全) — 参考 foundryvtt/dnd5e 的掩护计算
5. `calculate_movement`: 寻路计算 (含地形难度) — A* 算法 + 地形难度消耗
6. `manage_location`: 更新/查询地点描述和连接关系 — 扩展 Scene 模型
7. `move_party`: 队伍移动到新地点 + 触发遭遇判定 — 整合 exploration 模块
8. `render_battlefield`: 生成战术地图 (ASCII 网格) — 参考 rot.js Display 类

**关键文件变更**:
- 新建 `src/aidm/engine/spatial.py` — 空间推理工具集
- 新建 `src/aidm/engine/battlefield.py` — 战场渲染 (ASCII 网格)
- 修改 `src/aidm/engine/combat.py` — 集成网格坐标和空间工具

#### Phase 3: 多智能体架构改造 (1-2 周) 🟡

**目标**: 将现有单 graph 改造为 5-Agent 协作架构

**任务清单**:
1. Director Agent 作为新入口 (替代现有 classify 节点) — 意图分类 + 路由决策
2. Narrator Agent 子图 — 场景描述、NPC 对话、剧情推进、氛围渲染
3. Combat Engine Agent 子图 — 先攻管理、逐回合推进、攻击判定、伤害计算、条件追踪
4. World Manager Agent 子图 — 地点/时间/天气/NPC 状态/任务进度/物品栏
5. Rule Judge Agent 子图 — 验证行动合法性 + 规则书 RAG 查询 + 法术/怪物数据检索
6. 统一 GameState 模型 (Pydantic v2) — 替代 TypedDict
7. LangGraph StateGraph 条件路由 — `add_conditional_edges()` 实现 Director 路由

**关键文件变更**:
- 重构 `src/aidm/brain/graph.py` — 从单一线性图改为多 Agent 子图架构
- 新建 `src/aidm/agents/` 包
  - `director.py` — Director Agent
  - `narrator.py` — Narrator Agent
  - `combat_engine.py` — Combat Engine Agent
  - `world_manager.py` — World Manager Agent
  - `rule_judge.py` — Rule Judge Agent
- 新建 `src/aidm/state/game_state.py` — Pydantic v2 GameState 模型

#### Phase 4: NPC 人格持久化 (1-2 周) 🟡

**目标**: 每个 NPC 维护独立记忆文档集合 + 关系演化

**任务清单**:
1. NPC 数据库表 — 新增 NPC 表到 stats/models.py
2. NPC 人格档案 — 每个 NPC 维护独立的记忆文档集合 (向量存储)
3. NPC 记忆流 — 参考 Generative Agents，每个 NPC 存储观察 (observations)
4. NPC 记忆检索 — 通过 recency+importance+relevance 评分检索相关记忆
5. 关系演化追踪 — PC 与 NPC 之间的持久关系跟踪器
6. NPC 反思机制 — 从记忆中综合出更高层次的结论

**关键文件变更**:
- 修改 `src/aidm/stats/models.py` — 新增 NPC 表
- 新建 `src/aidm/npc/` 包
  - `npc_profile.py` — NPC 人格档案
  - `npc_memory.py` — NPC 记忆流 (参考 Generative Agents)
  - `relationship_tracker.py` — 关系演化追踪

#### Phase 5: 体验优化 & 模型调优 (2 周) 🟢

**目标**: 打磨叙事质量 + 减少幻觉 + 动态图片生成

**任务清单**:
1. 中文叙事 prompt 优化 (融合 Oracle-RPG + Bilibili RPG-Bot + 机核语法)
2. RAG 规则索引优化 (5echm 核心文件精选索引)
3. 反刍/幻觉监控指标
4. A/B 测试不同模型组合 (GPT-4o vs Claude 叙事质量对比)
5. 动态图片生成 — Hugging Face Diffusers API 集成
6. Enemy AI — LLM 决策 + 规则约束 (temperature 0.3-0.5)
7. Checkpoint/Rewind — LangGraph checkpointer + SQLite 快照
8. 战术地图渲染 — ASCII 网格自实现

---

## 六、附录: 全部调研项目索引

### 记忆系统框架

| # | 项目 | Stars | 语言 | License | 核心价值 |
|---|---|---|---|---|---|
| 1 | [mem0](https://github.com/mem0ai/mem0) | ~60.9k | TS/Python | Apache-2.0 | 通用 AI 记忆层，向量存储+时序推理+观察提取 |
| 2 | [Letta/MemGPT](https://github.com/letta-ai/letta) | ~23.8k | Python | Apache-2.0 | OS 式三层记忆：core+recall+archival |
| 3 | [Generative Agents (Stanford)](https://github.com/joonspk-research/generative_agents) | ~21.8k | Python | Apache-2.0 | 记忆流参考实现：重要性+时间衰减+相关性 |
| 4 | [Honcho](https://github.com/plastic-labs/honcho) | ~6.0k | Python | AGPL-3.0 | 会话级记忆基础设施 |
| 5 | [MemOS/MemTensor](https://github.com/MemTensor/MemOS) | ~10.2k | TypeScript | Apache-2.0 | 自演化记忆 OS，hybrid-retrieval |
| 6 | [LangChain Memory](https://github.com/langchain-ai/langchain) | ~141.8k | Python | MIT | 可组合记忆模块：Buffer+Summary+Vector+Entity |
| 7 | [MemoryOS (BAI-LAB)](https://github.com/BAI-LAB/MemoryOS) | ~1.5k | Python | Apache-2.0 | 学术项目 (EMNLP 2025 Oral)，分层存储架构 |

### 空间推理框架

| # | 项目 | Stars | 语言 | License | 覆盖能力 |
|---|---|---|---|---|---|
| 8 | [PathFinding.js](https://github.com/qiao/PathFinding.js) | ~8.7k | JS | MIT | 纯寻路库，11 种算法 |
| 9 | [rot.js](https://github.com/ondras/rot.js) | ~2.7k | JS | BSD-3-Clause | 网格+FOV+A*+ASCII 渲染 |
| 10 | [RogueSharp](https://github.com/FaronBracy/RogueSharp) | ~631 | C# | MIT | .NET 最完整方案 |
| 11 | [libtcod](https://github.com/libtcod/libtcod) | ~1.2k | C/C++ | BSD-3-Clause | C/C++ roguelike 工具包 |
| 12 | [easystarjs](https://github.com/prettymuchbryce/easystarjs) | ~1.9k | JS | MIT | 异步 A* 寻路 API |
| 13 | [foundryvtt/dnd5e](https://github.com/foundryvtt/dnd5e) | ~566 | JS | 专有 | D&D 5e 最完整空间系统 |
| 14 | [RPTools/maptool](https://github.com/RPTools/maptool) | ~917 | Java | AGPL-3.0 | 成熟 VTT 应用 |
| 15 | [kelindar/tile](https://github.com/kelindar/tile) | ~225 | Go | MIT | 2D 网格引擎+观察者 |
| 16 | [pyastar2d](https://github.com/hjweide/pyastar2d) | ~161 | Python | MIT | C++ 优化 A* for Python |

### 多智能体架构框架

| # | 项目 | Stars | 语言 | License | 核心价值 |
|---|---|---|---|---|---|
| 17 | [LangGraph](https://github.com/langchain-ai/langgraph) | ~37.3k | Python | MIT | 低级编排框架，StateGraph+条件路由+HITL |
| 18 | [CrewAI](https://github.com/crewAIInc/crewAI) | ~55.5k | Python | MIT | 角色扮演自主 Agent 框架，Crews+Flows |
| 19 | [AG2/AutoGen](https://github.com/ag2ai/ag2) | ~4.8k | Python | Apache-2.0 | 开源 AgentOS，swarms+group chats |
| 20 | [OpenAI Swarm](https://github.com/openai/swarm) | ~21.8k | Python | MIT | 轻量级多 Agent 编排 (教育/实验性) |
| 21 | [MS Agent Framework](https://github.com/microsoft/agent-framework) | ~12.1k | Python/.NET | MIT | 微软统一 Agent 框架 |

### NPC 持久化与角色模拟框架

| # | 项目 | Stars | 语言 | License | 核心价值 |
|---|---|---|---|---|---|
| 22 | [SillyTavern](https://github.com/SillyTavern/SillyTavern) | ~30.7k | JS | AGPL-3.0 | AI 角色扮演社区主导前端 |
| 23 | [RisuAI](https://github.com/kwaroran/RisuAI) | ~1.5k | TS | GPL-3.0 | 跨平台 LLM roleplay |
| 24 | [NarrativeEngine-P](https://github.com/Sagesheep/NarrativeEngine-P) | ~68 | TS | MIT | 自托管 AI DM，持久记忆+活 NPC |

### 动态图片/产物生成框架

| # | 项目 | Stars | 语言 | License | 核心价值 |
|---|---|---|---|---|---|
| 25 | [AUTOMATIC1111 SD WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) | ~164k | Python | AGPL-3.0 | 最流行 SD 界面，`--api` 启用程序化生成 |
| 26 | [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | ~121k | Python | GPL-3.0 | 最强大节点式工作流+REST API |
| 27 | [Fooocus](https://github.com/lllyasviel/Fooocus) | ~51.1k | Python | GPL-3.0 | 简化图像生成，聚焦提示和生成 |
| 28 | [Hugging Face Diffusers](https://github.com/huggingface/diffusers) | ~34.1k | Python | Apache-2.0 | 基础库：`pipeline(prompt) → image` |
| 29 | [FLUX.1](https://github.com/black-forest-labs/flux) | ~25.7k | Python | Apache-2.0 (代码) | SOTA 开源文生图模型 |
| 30 | [InvokeAI](https://github.com/invoke-ai/InvokeAI) | ~27.6k | Python | Apache-2.0 | 专业级 SD 工具包 |
| 31 | [Azgaar's Fantasy Map Generator](https://github.com/Azgaar/Fantasy-Map-Generator) | ~5.8k | HTML/TS | — | 首屈一指的开源奇幻世界地图生成器 |
| 32 | [mewo2/terrain](https://github.com/mewo2/terrain) | ~3.0k | JS | — | 轻量级奇幻地图生成器 |

### D&D/TRPG 特定参考项目

| # | 项目 | Stars | 语言 | License | 核心价值 |
|---|---|---|---|---|---|
| 33 | [jeannineshiu/multi-agents-dnd-game](https://github.com/jeannineshiu/multi-agents-dnd-game) | ~2 | Python | MIT-0 | **最接近的架构参考**: Gamemaster Orchestrator + Rules Agent (RAG) + Character Agent + Dice MCP Server |
| 34 | [MoonlightByte/NeverEndingQuest](https://github.com/MoonlightByte/NeverEndingQuest) | ~72 | Python | NOASSERTION | 基于 WOTC CC SRD 的 AI DM |
| 35 | [nickwalton/AI-DungeonMaster](https://github.com/nickwalton/AI-DungeonMaster) | ~79 | Python | — | 早期 AI DM 实现 (Nick Walton, AI Dungeon 创作者) |

---

## 数据来源

- GitHub 开源项目 (1k+ stars 优先)
- 学术论文: Generative Agents (Park et al., 2023), ChatRPG (arXiv 2502.19519)
- 技术博客: Critical Miss (convnet.ai), emasterlabs LangChain 教程
- Narra·Gym v0.1 排行榜 (2026-05)
- ITMO AI Dungeon Master GitHub
- 本项目源码逐文件审查

---

*本报告生成于 2026-07-15，供 AIDM 项目技术决策参考。*
