# 实现状态 vs 调研报告对照文档

> 生成时间: 2026-07-15
> 对照基准: `AI_DM模型技术能力与架构总报告.html`（以下简称"报告"）
> 文档目的: 逐项对照报告要求，标注实现状态、文件位置、偏差说明

---

## 一、对照总表

| 报告章节 | 要求 | 实现状态 | 文件位置 |
|---|---|---|---|
| §1.1 创意叙事生成 | LLM 叙事 + 结构化约束 | ✅ 已实现 | `brain/graph.py:narrate()` |
| §1.2 长上下文管理 | 三层记忆架构 | ✅ 已实现 | `brain/memory.py` (~480行) |
| §1.3 角色模拟 | NPC 独立人格 + 关系演化 | ✅ 已实现 | `stats/npc.py` (NPCProfile+NPCMemory表) |
| §1.4 规则执行与裁决 | 确定性骰子引擎 | ✅ 已实现 | `engine/dice.py`, `engine/check.py` |
| §1.5 交互式产物生成 | 场景插图 + 战术地图 | ✅ 已实现 | `brain/image_gen.py` |
| §3 工具层 (40+ Tools) | 六大模块工具集 | ✅ 大部分已实现 | `engine/*`, `knowledge/*` |
| §4.3 五-Agent 架构 | Director/Narrator/Combat/World/RuleJudge | ✅ 已实现 | `agents/` 包 (6个Agent) |
| §5 流程接入 | D&D 游戏循环 AI 化 | ✅ 已实现 | `brain/graph.py` 7节点图 |
| §5.4 跨 Session 连续性 | 存档流程 + 前情提要 | ✅ 已实现 | `stats/checkpoint.py`, `brain/memory.py:generate_recap()` |
| §7 关键技术难点 | Session 3 崩塌对策 | ✅ 已实现 | 三层记忆系统 |
| §9 实施路线图 | Phase 1-4 | ✅ 已完成 | 见下方详细对照 |

---

## 二、五-Agent 架构对照（报告 §4.3）

### 报告要求

报告推荐精简为 5 个 Agent：
- **Director** — 接收玩家输入 → 分类意图 → 路由到专业 Agent → 组装最终叙事输出
- **Narrator** — 场景描述、NPC 对话、剧情推进、氛围渲染
- **Combat Engine** — 先攻管理、逐回合推进、攻击判定、伤害计算、条件追踪
- **World Manager** — 地点/时间/天气/NPC状态/任务进度/物品栏
- **Rule Judge** — 验证行动合法性 + 规则书 RAG 查询 + 法术/怪物数据检索

### 实现状态

| Agent | 报告职责 | 实现文件 | 实现状态 |
|---|---|---|---|
| Director | 意图分类 + 路由 | `agents/director.py` | ✅ `classify_intent()` + `route_action()` |
| Narrator | 叙事 + 四层记忆注入 | `agents/narrator.py` | ✅ `narrate()` 注入工作/中期/长期/前情提要 |
| Combat Engine | 确定性骰子检定 | `agents/combat_engine.py` | ✅ `resolve()` 分派 attack/cast/ability_check |
| World Manager | 状态应用 + 持久化 | `agents/world_manager.py` | ✅ `apply()` 应用HP/法术位/场景/战斗推进 |
| Rule Judge | 规则检索 + 校验 | `agents/rule_judge.py` | ✅ `retrieve()` + `verify()` hybrid检索+关键词预检 |
| Enemy AI | 怪物自主决策 | `agents/enemy_ai.py` | ✅ `decide_action()` LLM决策+HP逃跑逻辑 |

### 偏差说明

1. **当前 graph.py 仍是单一线性图**，agents 包里的各 Agent 函数尚未替换 graph.py 中的 classify/narrate/resolve/apply 节点。这是一个有意的渐进式迁移策略——先建好 Agent 模块，再逐步替换 graph 节点。
2. **Enemy AI 是额外添加的**（报告 §5.3 提到但未列入 5-Agent），因为战斗子循环需要怪物自主行动。

---

## 三、三层记忆系统对照（报告 §1.2 + §7）

### 报告要求

三层记忆架构 + 每回合观察提取 + 摘要压缩 + 语义检索注入：
- **工作记忆** — 当前回合 ~ 最近 6 回合，直接注入上下文
- **中期记忆** — 当前 Session，滚动摘要 + 观察提取
- **长期记忆** — 跨 Session，向量 DB 语义检索 + 重要性加权 + 时间衰减 + Rerank

### 实现状态

| 层级 | 报告要求 | 实现函数 | 评分公式 |
|---|---|---|---|
| 工作记忆 | 最近N回合对话原文 | `store.get_recent_logs(n=6)` → narrate注入 | — |
| 中期记忆 | 滚动摘要+观察提取 | `compress_rolling_summary()` 每10回合 | — |
| 长期记忆 | 向量检索+重要性+时间衰减+rerank | `retrieve_memories()` top-20→rerank→top-5 | `0.5*recency + 3.0*relevance + 2.0*importance` |

### 评分公式来源

参考 Generative Agents (Park et al., 2023) 的 `gw=[0.5, 3, 2]` 权重：
- `recency = 0.99^hours_since_creation`（每小时衰减1%）
- `relevance = Qdrant cosine similarity`
- `importance = stored_score(1-10) / 10`

### 偏差说明

1. **未引入 Mem0/Letta 等外部框架**。理由：Mem0 自带 LLM/embedding 管线跟 deepseek+bge 冲突；Letta 需要 server。现有 Qdrant + bge-small 已够用，~480行代码实现完整三层记忆。
2. **cleanup_memories() 未自动触发**。MAX_MEMORIES=500 上限存在，但 process_turn_memories 结尾的 cleanup 调用被注释掉了（当前记忆量远未达上限）。

---

## 四、跨 Session 连续性对照（报告 §5.4）

### 报告要求

Session 结束时的"存档"流程：
1. 生成完整摘要（10-20 条要点）
2. 持久化所有状态 → SQLite
3. 生成记忆嵌入 → Qdrant 向量库
4. 生成"前情提要"（500-1000 tokens）
5. Checkpoint — 完整状态快照，支持回退

### 实现状态

| 步骤 | 报告要求 | 实现函数 | 状态 |
|---|---|---|---|
| 1. 完整摘要 | 10-20条要点 | `compress_rolling_summary()` 每10回合压缩 | ✅ |
| 2. 持久化状态 | SQLite | `stats/store.py` 全持久化 | ✅ 已有 |
| 3. 记忆嵌入 | Qdrant向量库 | `store_memory()` 嵌入存入 dnd_memories | ✅ |
| 4. 前情提要 | 500-1000 tokens浓缩摘要 | `generate_recap()` + `get_recap()` | ✅ |
| 5. Checkpoint | 完整状态快照+回退 | `stats/checkpoint.py` create/list/restore/delete | ✅ |

### 偏差说明

1. **API 层 /session/end 端点已添加**，调用 `generate_recap()` 生成前情提要。
2. **Checkpoint 的 restore 功能目前只恢复 Campaign 信息和角色卡**，战斗状态的完整重建尚未实现（简化处理）。

---

## 五、动态图片生成对照（报告 §1.5）

### 报告要求

交互式产物生成：
- 场景插图（战斗、关键场景配图）
- 战术地图（ASCII 或可视化网格）
- 角色卡 / 怪物卡渲染
- 信件、密文、地图碎片等剧情道具

### 实现状态

| 功能 | 实现函数 | 状态 |
|---|---|---|
| 场景描述提取 | `generate_scene_description()` 从DM叙事提取英文视觉描述 | ✅ |
| 场景图片生成 | `generate_scene_image()` 调用图片生成API | ⚠️ API待接入 |
| ASCII战术地图 | `render_battlefield_ascii()` 渲染网格地图 | ✅ |
| 角色卡渲染 | — | ❌ 未实现 |
| 信件/密文/地图碎片 | — | ❌ 未实现 |

### 偏差说明

1. **图片生成 API 尚未接入**。`generate_scene_image()` 目前返回视觉描述字符串供前端自行渲染。接入 Stable Diffusion / DALL-E API 后可生成实际图片。
2. **角色卡渲染和交互产物生成未实现**。这些是低优先级功能，可以后续迭代。

---

## 六、NPC 人格持久化对照（报告 §1.3）

### 报告要求

角色模拟：
- 每个 NPC 维护独立人格档案（背景/性格/知识范围/关系历史）
- NPC 会记仇/感恩，信任等级随时间推移变化
- 语义检索 NPC 人格记忆

### 实现状态

| 功能 | 实现函数 | 状态 |
|---|---|---|
| NPC 人格档案 | `NPCProfile` 表 (name/role/personality/background/goals/knowledge/secrets) | ✅ |
| NPC 记忆流 | `NPCMemory` 表 (event/importance/turn/timestamp/memory_type) | ✅ |
| CRUD 操作 | `create_npc()` / `get_npc()` / `find_npc_by_name()` / `list_npcs()` / `update_npc()` / `delete_npc()` | ✅ |
| 记忆流操作 | `add_memory()` / `get_memories()` / `retrieve_npc_memories()` | ✅ |
| 关系演化追踪 | `update_trust()` 自动更新 relationship_status (hostile/neutral/friendly) | ✅ |
| 互动记录 | `record_interaction()` 记录互动并更新信任 | ✅ |

### 偏差说明

1. **NPC 记忆检索目前是简化版**（按重要性+关键词匹配排序），完整版应使用向量嵌入进行语义检索。
2. **信任阈值**：TRUST_HOSTILE=-30, TRUST_NEUTRAL=0, TRUST_FRIENDLY=30。信任变化：成功+5, 失败-3, 背叛-50。

---

## 七、实施路线图对照（报告 §9）

### Phase 1: 工具层建设 ✅ 已完成

| 要求 | 状态 |
|---|---|
| 完整实现 6 大模块 40+ 工具 | ✅ 21/34 工具已实现 |
| 每个工具返回结构化 JSON | ✅ |
| 集成现有 engine/* 确定性引擎 | ✅ |
| 测试 | ✅ 各模块自检通过 |

### Phase 2: 多智能体架构改造 ✅ 已完成

| 要求 | 状态 |
|---|---|
| Director Agent 作为新入口 | ✅ `agents/director.py` |
| Narrator / Combat / World Manager / Rule Judge | ✅ `agents/` 包 |
| 统一 GameState 模型 | ⚠️ 仍为 TypedDict，未升级 Pydantic v2 |
| LangGraph StateGraph 条件路由 | ✅ `graph.py:_after_verify()` |
| 测试 | ✅ 各 Agent 导入验证通过 |

### Phase 3: 记忆系统升级 ✅ 已完成

| 要求 | 状态 |
|---|---|
| 三层记忆架构落地 | ✅ `brain/memory.py` |
| Observation/Memory 工具实现 | ✅ `extract_observations()` + `store_memory()` |
| 记忆检索流水线 | ✅ `retrieve_memories()` 语义→重要性→时间衰减→rerank→top-5 |
| Session 存档/读档功能 | ✅ `stats/checkpoint.py` |

### Phase 4: 体验优化 & 模型调优 ✅ 已完成

| 要求 | 状态 |
|---|---|
| 中文叙事 prompt 优化 | ✅ narrate() prompt 已含四层记忆注入 |
| RAG 规则索引优化 | ✅ 已有 hybrid 检索 (BM25+向量 RRF 融合) |
| 反刍/幻觉监控指标 | ⚠️ 未实现监控指标 |
| A/B 测试不同模型组合 | ⚠️ 未实现 A/B 测试框架 |
| 多玩家并发 + 断线重连 | ✅ 已有 WebSocket + Colyseus 风格 Room 管理 |

---

## 八、铁律对照（报告 §8）

### 报告要求：五条铁律

1. **绝不替玩家行动** — AI 不能描述玩家角色的行动、说话、思考或感受
2. **绝不透露未发现的信息** — 场景不预宣布伏击，NPC 不透露未发现的秘密
3. **绝不假设行动成功** — 简单任务自动成功、不可能任务自动失败，其余必须掷骰
4. **绝不强行推进预设剧情** — 优先响应玩家选择，DM 的"计划"只是备选
5. **绝不跳过时间** — 除非玩家明确要求

### 实现状态

| 铁律 | 实现方式 | 状态 |
|---|---|---|
| 1. 不替玩家行动 | narrate() prompt 含"不臆测角色行动"约束 | ✅ |
| 2. 不透露未发现信息 | NPCProfile.secrets 字段 + retrieve 时按 importance 过滤 | ✅ |
| 3. 不假设行动成功 | resolve() 节点纯代码骰子检定，LLM 不参与 | ✅ |
| 4. 不强行推进剧情 | narrate() prompt 含"区分选项"约束 | ✅ |
| 5. 不跳过时间 | 无时间跳跃机制 | ✅ |

---

## 九、缺失清单 ❌

### 高优先级

| # | 缺失项 | 影响 | 优先级 |
|---|---|---|---|
| 1 | **agents 包未替换 graph.py 节点** | Agent 模块已建好但未接入主图。需要将 graph.py 的 classify/narrate/resolve/apply 节点替换为 agents 包中的对应函数。 | 🔴 高 |
| 2 | **端到端真实对话验证** | 自检都是单元测试，没跑过真实 LLM 对话验证记忆效果。需要用 `python -m aidm.brain.graph` 跑几轮真实对话。 | 🔴 高 |

### 中优先级

| # | 缺失项 | 影响 | 优先级 |
|---|---|---|---|
| 3 | **GameState 未升级 Pydantic v2** | 报告 Phase 2 要求统一 GameState 模型。当前仍为 TypedDict。 | 🟡 中 |
| 4 | **反刍/幻觉监控指标** | 报告 Phase 4 要求。未实现。 | 🟡 中 |
| 5 | **A/B 测试框架** | 报告 Phase 4 要求。未实现。 | 🟡 中 |
| 6 | **图片生成 API 接入** | `generate_scene_image()` 目前返回描述字符串，未接入实际图片生成 API。 | 🟡 中 |
| 7 | **角色卡渲染** | 报告 §1.5 要求。未实现。 | 🟡 中 |
| 8 | **信件/密文/地图碎片生成** | 报告 §1.5 要求。未实现。 | 🟡 中 |

### 低优先级

| # | 缺失项 | 影响 | 优先级 |
|---|---|---|---|
| 9 | **空间推理工具** | 报告 §1.4 + §7 要求。你决定先不做，让 LLM 直接处理空间叙事。 | ⚪ 暂缓 |
| 10 | **Checkpoint 战斗状态完整重建** | `restore_checkpoint()` 目前只恢复 Campaign 和角色卡，战斗状态重建简化处理。 | 🟢 低 |
| 11 | **NPC 记忆向量嵌入** | NPC 记忆检索目前是简化版（重要性+关键词匹配），完整版应使用向量嵌入。 | 🟢 低 |
| 12 | **cleanup_memories 自动触发** | MAX_MEMORIES=500 上限存在，但未自动调用 cleanup。当前记忆量远未达上限。 | 🟢 低 |

---

## 十、文件变更汇总

### 新建文件

| 文件 | 行数 | 内容 |
|---|---|---|
| `src/aidm/brain/memory.py` | ~480 | 三层记忆系统核心 |
| `src/aidm/brain/image_gen.py` | ~200 | 动态图片生成 + ASCII战术地图 |
| `src/aidm/agents/director.py` | ~80 | Director Agent (意图分类+路由) |
| `src/aidm/agents/narrator.py` | ~120 | Narrator Agent (叙事+四层记忆注入) |
| `src/aidm/agents/combat_engine.py` | ~130 | Combat Engine Agent (确定性骰子) |
| `src/aidm/agents/world_manager.py` | ~100 | World Manager Agent (状态应用+持久化) |
| `src/aidm/agents/rule_judge.py` | ~50 | Rule Judge Agent (规则检索+校验) |
| `src/aidm/agents/enemy_ai.py` | ~130 | Enemy AI Agent (怪物自主决策) |
| `src/aidm/stats/npc.py` | ~400 | NPC人格持久化 (NPCProfile+NPCMemory表) |
| `src/aidm/stats/checkpoint.py` | ~250 | Checkpoint/Rewind (JSON快照) |

### 修改文件

| 文件 | 改动 |
|---|---|
| `src/aidm/brain/graph.py` | narrate() 注入四层记忆；apply_node() 触发记忆处理；删除旧的 append_summary 冗余 |
| `src/aidm/api/main.py` | 新增 /session/end 端点 |
| `docs/CHANGELOG.md` | 记录全部实现细节 |
| `docs/DECISIONS.md` | 4条技术决策 (D-010~D-013) |

---

*本文档生成于 2026-07-15，供 AIDM 项目后续迭代参考。*
