# 三层记忆系统 — 完成状态与缺失清单

> 生成时间: 2026-07-15
> 文档目的: 记录记忆系统"做了什么 / 缺什么"，供后续迭代参考

---

## 一、已完成 ✅

### 1. 工作记忆（Working Memory）

**功能**: 每回合 narrate() 注入最近6回合对话原文，解决"LLM每回合失忆"问题。

| 组件 | 文件位置 | 状态 |
|---|---|---|
| `get_recent_logs()` | `stats/store.py` | ✅ 已实现 |
| narrate() 注入工作记忆 | `brain/graph.py:narrate()` | ✅ 已注入 |

**数据流**: `Log` 表 → `get_recent_logs(camp_id, n=6)` → 格式化为 `[回合] 玩家: ... → DM: ...` → 注入 narrate prompt

---

### 2. 中期记忆（Mid-term Memory）

**功能**: rolling_summary 每10回合用 LLM 压缩成3-5句摘要，narrate() 注入前500字。

| 组件 | 文件位置 | 状态 |
|---|---|---|
| `compress_rolling_summary()` | `brain/memory.py` | ✅ 已实现 |
| 每10回合自动压缩 | `brain/memory.py:process_turn_memories()` | ✅ 已接入 |
| narrate() 注入 rolling_summary | `brain/graph.py:narrate()` | ✅ 已注入 |
| 旧的逐回合 append_summary | `brain/graph.py:apply_node()` | ✅ 已删除（消除冗余） |

**数据流**: 每10回合 → `get_recent_logs(n=10)` → LLM 压缩成摘要 → 追加到 `Campaign.rolling_summary`

---

### 3. 长期记忆（Long-term Memory）

**功能**: 每回合结束后 LLM 提取1-3条关键观察（含重要性1-10评分），嵌入存入 Qdrant `dnd_memories` collection。narrate() 时语义检索 top-20 → 三分量评分 rerank → top-5 注入。

| 组件 | 文件位置 | 状态 |
|---|---|---|
| `extract_observations()` | `brain/memory.py` | ✅ 已实现 |
| `store_memory()` | `brain/memory.py` | ✅ 已实现 |
| `retrieve_memories()` | `brain/memory.py` | ✅ 已实现 |
| Qdrant `dnd_memories` collection | `brain/memory.py:_ensure_collection()` | ✅ 自动创建 |
| narrate() 注入长期记忆 | `brain/graph.py:narrate()` | ✅ 已注入 |

**评分公式** (参考 Generative Agents, Stanford):
```
final_score = 0.5 * recency + 3.0 * relevance + 2.0 * importance

recency    = 0.99 ^ hours_since_creation     (每小时衰减1%)
relevance  = Qdrant cosine similarity        (语义相关性)
importance = stored_score(1-10) / 10         (重要性归一化)
```

**数据流**:
- 写入: `apply_node()` → `process_turn_memories()` → `extract_observations()` → `store_memory()` (嵌入+存Qdrant)
- 读取: `narrate()` → `retrieve_memories(query, top_k=20)` → 三分量评分 → rerank → top-5 注入 prompt

---

### 4. Session 间前情提要

**功能**: Session结束时生成浓缩摘要（500-1000字），新Session开始时注入 narrate prompt。

| 组件 | 文件位置 | 状态 |
|---|---|---|
| `generate_recap()` | `brain/memory.py` | ✅ 已实现 |
| `get_recap()` | `brain/memory.py` | ✅ 已实现 |
| narrate() 注入前情提要 | `brain/graph.py:narrate()` | ✅ 已注入 |

**数据流**:
- 生成: `generate_recap(camp_id)` → 汇总 rolling_summary + 高重要性记忆(importance>=7) → LLM 生成前情提要 → 存入 `Campaign.rolling_summary` 的 `[前情提要]...[/前情提要]` 块
- 注入: `narrate()` → `get_recap(camp_id)` → 提取 `[前情提要]` 块 → 注入 prompt 开头

---

### 5. Qdrant 记忆清理上限

**功能**: 单战役长期记忆超过500条时，按重要性升序删除最低分记忆。

| 组件 | 文件位置 | 状态 |
|---|---|---|
| `cleanup_memories()` | `brain/memory.py` | ✅ 已实现 |
| `MAX_MEMORIES = 500` | `brain/memory.py` | ✅ 已配置 |

**注意**: `cleanup_memories()` 目前未自动调用。可在 `process_turn_memories()` 结尾加上 `cleanup_memories(campaign_id)` 实现自动清理，但当前记忆量远未达到500条上限，暂不启用。

---

### 6. 自检覆盖

| 测试 | 覆盖内容 | 状态 |
|---|---|---|
| test1 | `extract_observations()` 返回类型 | ✅ |
| test2 | `store_memory()` 存储 | ✅ |
| test3 | `retrieve_memories()` 检索 | ✅ |
| test4 | `compress_rolling_summary()` 压缩 | ✅ |
| test5 | `process_turn_memories()` 完整管线 | ✅ |
| test6 | `generate_recap()` / `get_recap()` 前情提要 | ✅ |
| test7 | `cleanup_memories()` 清理 | ✅ |

---

## 二、缺失清单 ❌

> 注：以下清单生成较早，部分项已随后实现，状态已就近标注（2026-07-15 更新）。

### 记忆系统内部

| # | 缺失项 | 影响 | 优先级 |
|---|---|---|---|
| 1 | **端到端真实对话验证** | 自检都是单元测试，没跑过真实 LLM 对话验证记忆效果。需要用 `python -m aidm.brain.graph` 跑几轮真实对话。 | 🔴 高 |
| 2 | **cleanup_memories 未自动触发** | 长跑战役可能积累大量记忆。需在 `process_turn_memories` 结尾加 `cleanup_memories(campaign_id)`。当前记忆量远未达500条上限，暂不紧急。 | 🟡 中 |
| 3 | ~~Session 结束钩子未接入 API~~ ✅ 已实现 | `generate_recap()` + `/session/end` 端点已接入（见 `api/main.py`）。 | ✅ 已完成 |
| 4 | **记忆检索无 campaign_id 过滤** | `retrieve_memories()` 当前用 Qdrant filter 按 campaign_id 过滤，但 `_ensure_collection()` 创建的 collection 没有预设 filter。多战役场景下可能串味。实际影响小，因为 retrieve 时带了 filter。 | 🟢 低 |

### 记忆系统之外（AIDM 整体缺口）

| # | 缺失项 | 影响 | 优先级 |
|---|---|---|---|
| 5 | ~~多智能体架构升级~~ ✅ 已建 | `agents/` 包已建（6 个 Agent：Director/RuleJudge/Narrator/CombatEngine/WorldManager/EnemyAI），渐进迁移中。 | ✅ 已落地 |
| 6 | ~~NPC 人格持久化~~ ✅ 已实现 | `stats/npc.py` 已建（NPCProfile + NPCMemory + 关系演化追踪）。 | ✅ 已落地 |
| 7 | ~~Checkpoint/Rewind~~ ✅ 已实现 | `stats/checkpoint.py` 已建（JSON 快照存档/读档/回退）。 | ✅ 已落地 |
| 8 | ~~动态图片生成~~ ✅ 部分实现 | `brain/image_gen.py` 已建（场景描述 + `render_battlefield_ascii` 战术地图）；动态插图 API 待接。 | 🟡 部分 |
| 9 | ~~Enemy AI~~ ✅ 已建 | `agents/enemy_ai.py` 已建（`decide_action`，HP<25% 逃跑，temperature 0.4）；待接入战斗循环。 | 🟡 部分 |
| 10 | **空间推理工具** | 无网格/距离/视线/掩护/AoE计算。你决定先不做，让 LLM 直接处理空间叙事。 | ⚪ 暂缓 |

---

## 三、文件变更汇总

### 新建文件

| 文件 | 行数 | 内容 |
|---|---|---|
| `src/aidm/brain/memory.py` | ~480行 | 三层记忆系统核心模块（观察提取/存储/检索/压缩/前情提要/清理） |
| `docs/MEMORY_SYSTEM_RESEARCH.md` | — | 三层记忆系统调研报告 |
| `docs/MEMORY_SYSTEM_STATUS.md` | — | 本文档（完成/缺失清单） |

### 修改文件

| 文件 | 改动 | 行数 |
|---|---|---|
| `src/aidm/stats/store.py` | 新增 `get_recent_logs()` | ~12行 |
| `src/aidm/brain/graph.py` | narrate() 注入四层记忆（工作/中期/长期/前情提要）；apply_node() 触发记忆处理；删除旧的 append_summary 冗余 | ~60行 |
| `docs/CHANGELOG.md` | 记录三层记忆系统完整实现 | — |
| `docs/DECISIONS.md` | 4条技术决策（D-023~D-026） | — |

---

## 四、技术决策记录

| 决策ID | 内容 | 理由 |
|---|---|---|
| D-023 | 不引入外部记忆框架，直接在现有 Qdrant 上实现 | Mem0/Letta 自带 LLM/embedding 管线跟 deepseek+bge 冲突；无重要性评分和时间衰减；现有技术栈已就位 |
| D-024 | 长期记忆检索评分公式：`0.5*recency + 3.0*relevance + 2.0*importance` | 参考 Generative Agents (Park et al., 2023) 的 `gw=[0.5, 3, 2]` 权重 |
| D-025 | 滚动摘要压缩频率：每10回合一次 | 每回合压缩成本太高；每10回合一次平衡了成本和新鲜度 |
| D-026 | 工作记忆直接查 Log 表，不用 LangGraph messages 状态 | Log 表已经在写；不需要改 GameState schema；历史存 SQLite 进程重启不丢 |

---

*本文档生成于 2026-07-15，供 AIDM 记忆系统后续迭代参考。*
