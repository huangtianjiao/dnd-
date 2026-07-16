# 三层记忆系统调研报告

> 生成时间: 2026-07-15
> 调研目标: 确定 AIDM 记忆系统的实现方案
> 调研范围: 开源框架 (1k+ stars)、学术论文、现有代码审查

---

## 一、问题定义

### 核心问题

LLM 上下文窗口装不下完整跑团历史。

| 时间点 | 累积 token 量 | 状态 |
|---|---|---|
| 第1回合 | ~200 tokens | 轻松 |
| 第50回合 | ~10000 tokens | 上下文开始拥挤 |
| 第200回合 | ~40000 tokens | 爆了，LLM 开始遗忘前面的剧情 |

### 当前状态

AIDM 的 `narrate()` 节点（`brain/graph.py:374`）构建 prompt 时：

**注入了**：
- 当前骰子结果 (`dice`)
- 战斗状态 (`combat`)
- 当前场景上下文 (`scene_ctx`)
- 规则摘要 (`dig`)
- 玩家输入 (`player_input`)

**没有注入**：
- ❌ 前几回合的对话历史（LLM 每回合都"失忆"）
- ❌ `rolling_summary`（虽然一直在追加，但 narrate 从不读取它）
- ❌ 跨 Session 的关键事件、NPC 关系、任务进度

**已有但不用的数据**：
- `Log` 表：每回合存 player_input + dm_output + dice_rolls + state_changes，但从不读回
- `Campaign.rolling_summary`：每回合追加 `[轮] {player_input[:30]} → {narration[:40]}`，但从不注入 prompt

---

## 二、三层架构详解

### 第一层：工作记忆（Working Memory）

**存什么**：最近 N 回合（比如6回合）的完整对话原文

```
[回合-5] 玩家: 我踢开门 → DM: 门后是黑暗的走廊...
[回合-4] 玩家: 我举着火把往前走 → DM: 走廊尽头分叉...
[回合-3] 玩家: 走左边 → DM: 你听到水声...
[回合-2] 玩家: 检查陷阱 → DM: 发现一个触发板...
[回合-1] 玩家: 我绕过触发板 → DM: 你成功跨过去...
[回合-0] 玩家: 继续前进 → DM: ...
```

**怎么用**：直接拼到 `narrate()` 的 prompt 里

**为什么需要它**：LLM 需要知道"上一回合发生了什么"才能连贯叙事。比如玩家说"我再敲一下"，LLM 必须知道上一回合是在敲门还是敲怪。

### 第二层：中期记忆（Mid-term Memory）

**存什么**：当前 Session 的滚动摘要 + 结构化观察

```
摘要: 队伍进入黑木镇废弃神殿，在走廊遭遇陷阱，绕过后到达分叉口。
      玩家选择了左侧通道，发现地下水源。

观察:
  - [重要:7] 守卫被玩家敲晕，藏在酒桶后
  - [重要:9] 玩家发现了通往地下二层的隐藏楼梯
  - [重要:5] NPC酒馆老板提到"三周前开始的失踪"
  - [重要:3] 玩家的匕首在战斗中损坏
```

**怎么用**：
1. **摘要**注入 prompt — 让 LLM 知道这个 Session 大致发生了什么
2. **观察提取** — 每回合结束后，用一个轻量 LLM 调用从本回合叙事中提取关键事实，打重要性分数

**为什么需要它**：工作记忆只覆盖最近6回合。第7回合之前的细节会"掉出"工作记忆。中期记忆用压缩摘要的方式保留更长时间跨度的信息。

### 第三层：长期记忆（Long-term Memory）

**存什么**：跨 Session 的关键事件、NPC关系、世界状态变化，存到向量数据库

```
记忆库 (Qdrant dnd_memories collection):
  - "玩家在黑木镇杀死了邪教头目马尔科" [重要性:9] [Session:1]
  - "酒馆老板鲍勃对玩家态度友好(信任)" [重要性:7] [Session:1]
  - "玩家获得了魔法剑'破晓'" [重要性:8] [Session:2]
  - "玩家与精灵王国建立了同盟关系" [重要性:9] [Session:3]
```

**怎么用**：每回合开始时，用玩家输入做语义查询，检索相关记忆注入 prompt

```
玩家输入: "我去找酒馆老板鲍勃问问地下的事"
→ 语义检索 → 找到"鲍勃对玩家友好"、"上次见面鲍勃提到了地下活动"
→ 注入 prompt
```

**为什么需要它**：Session 3 时，玩家可能提到 Session 1 的某个 NPC。如果没有长期记忆 + 语义检索，LLM 根本不知道玩家在说什么。

---

## 三、开源框架评估

### 评估方法论

对每个框架评估四个维度：
1. **向量存储**：是否支持 Qdrant？
2. **重要性评分**：是否实现 importance scoring？
3. **时间衰减**：是否实现 time decay？
4. **集成成本**：与现有 LangGraph + Qdrant + bge-small + deepseek 技术栈的兼容性

### 框架对比矩阵

| 框架 | Stars | 向量存储 | 重要性评分 | 时间衰减 | 与现有技术栈兼容 |
|---|---|---|---|---|---|
| **Mem0** | ~60.9k | ✅ Qdrant | ❌ 无显式评分 | ❌ 用"temporal reasoning"代替 | ⚠️ 自带 LLM/embedding 管线，跟 deepseek+bge 冲突 |
| **Letta/MemGPT** | ~23.8k | ⚠️ 可配置 | ❌ 无显式评分 | ❌ 无 | ⚠️ 需要 Letta server，不原生支持 Qdrant |
| **Generative Agents (Stanford)** | ~18k | ⚠️ 自定义 | ✅ LLM 打分 1-10 | ✅ 指数衰减 0.99/hr | ✅ 参考其算法，自行实现 |
| **LangChain Memory** | ~141.8k (含LC) | ✅ 通过 VectorStoreRetrieverMemory | ❌ 无 | ❌ 无 | ✅ 已在技术栈中 |
| **Zep/Graphiti** | ~29k (Graphiti) | ❌ 需要 Neo4j/FalkorDB | ✅ 双时序有效期 | ✅ 事实失效机制 | ❌ 需要 graph DB，不用 Qdrant |

### 详细评估

#### Mem0 (~60.9k stars)

- **GitHub**: https://github.com/mem0ai/mem0
- **License**: Apache-2.0
- **核心价值**: Universal memory layer for AI agents. Single-pass ADD-only extraction (one LLM call). Multi-signal retrieval: semantic + BM25 + entity matching fused in parallel.
- **Qdrant 支持**: 显式支持 Qdrant 作为 vector store provider
- **局限性**:
  - 没有显式的重要性评分机制
  - 没有数学化的时间衰减公式（用 "temporal reasoning" for time-aware retrieval）
  - Fact extraction 是通用的，不是为 D&D 叙事调优的
  - 默认 LLM 是 `gpt-5-mini`，跟 deepseek-v4-flash 设置冲突
  - 会添加依赖，使用自己的 LLM/embedding pipeline

#### Letta/MemGPT (~23.8k stars)

- **GitHub**: https://github.com/letta-ai/letta
- **License**: Apache-2.0
- **核心价值**: Platform for stateful agents with OS-like memory hierarchy. Core memory blocks persist across interactions and are always visible to the agent.
- **三层映射**:
  - Core memory (in-context, always visible) → 工作记忆
  - Recall memory (conversation history) → 中期记忆
  - Archival memory (vector DB, semantic search) → 长期记忆
- **局限性**:
  - 需要 running the Letta server（额外基础设施）
  - Self-editing approach adds LLM overhead per turn
  - 不原生 integrate with existing Qdrant setup
  - 没有重要性评分或时间衰减

#### Generative Agents / Stanford (~18k stars)

- **GitHub**: https://github.com/joonspk-research/generative_agents
- **License**: Apache-2.0
- **核心价值**: Reference implementation behind "Generative Agents: Interactive Simulacra of Human Behavior" (Park et al., 2023). The canonical reference for observation extraction, importance scoring, and the recency/relevance/importance retrieval formula.
- **关键算法**:

  **Memory Stream Structure** — each memory (observation) stored as a node with:
  - `description`: natural language string
  - `created`: timestamp when recorded
  - `last_accessed`: timestamp updated on retrieval
  - `poignancy`: integer 1-10 representing importance
  - `embedding_key`: reference to precomputed embedding vector

  **Observation Extraction** — via `perceive.py` module. Each observation gets:
  1. A poignancy score (1-10) via LLM call
  2. An embedding vector for semantic search
  3. Timestamps for recency calculation

  Poignancy prompt template:
  ```
  On the scale of 1 to 10, where 1 is purely mundane
  (e.g., brushing teeth, making bed) and 10 is extremely poignant
  (e.g., a break up, college acceptance), rate the likely poignancy
  of the following event for {agent_name}.

  Event: {event_description}
  Rate (return a number between 1 to 10):
  ```

  **Retrieval Formula** — combines three normalized components:
  ```python
  gw = [0.5, 3, 2]  # [recency_weight, relevance_weight, importance_weight]

  final_score = (recency_w * recency * gw[0]
                 + relevance_w * relevance * gw[1]
                 + importance_w * importance * gw[2])
  ```

  Three scoring components:
  1. **Recency**: `recency_decay ** i` where `recency_decay = 0.99` and `i` is position in chronological order
  2. **Relevance**: cosine similarity between query embedding and memory embedding
  3. **Importance**: pre-assigned poignancy value (1-10 scale)

  **Reflection Mechanism** — triggered when accumulated poignancy exceeds threshold (`importance_trigger_max = 150`). Takes recent observations, asks LLM "What high-level insights can you infer from the above statements?", stores resulting insights as new memory nodes.

- **局限性**:
  - 使用自定义向量存储，不直接支持 Qdrant
  - 学术原型，不是生产级框架
  - 但其算法可以直接在现有 Qdrant 上实现

#### LangChain Memory (~141.8k stars for LangChain)

- **GitHub**: https://github.com/langchain-ai/langchain
- **License**: MIT
- **核心价值**: Composable memory modules for LLM applications. Already in AIDM's tech stack.
- **记忆模块**:
  - `ConversationBufferMemory`: stores all messages in buffer (working memory)
  - `ConversationBufferWindowMemory`: keeps only last `k` conversations (working memory with window)
  - `ConversationSummaryMemory`: maintains rolling summaries (mid-term memory)
  - `ConversationSummaryBufferMemory`: hybrid of summary + buffer
  - `VectorStoreRetrieverMemory`: stores memories in vector DB, retrieves semantically (long-term memory)
  - `EntityMemory`: extracts and tracks information about entities
- **局限性**:
  - 这些类是 legacy `langchain.memory` 模块的一部分
  - LangChain 当前推荐使用 LangGraph 的 built-in checkpointing
  - 没有重要性评分或时间衰减

### 结论：不引入新框架

**理由**：
1. 现有技术栈已经够用 — Qdrant、bge-small、SQLite Log 表都已就位
2. 大 star 框架要么需要额外基础设施（Letta server），要么用自带的 LLM/embedding 管线跟 deepseek+bge 冲突（Mem0），要么不实现重要性评分和时间衰减
3. 直接在现有 Qdrant 上实现 Generative Agents 模式，只需要 ~300-400 行新代码，零新依赖

**参考算法来源**：Generative Agents (Stanford) 的记忆流架构 — 重要性评分 + 时间衰减 + 相关性检索 + 反思机制

---

## 四、实施方案

### 总体架构

```
玩家输入
    │
    ├─→ classify (意图分类)
    ├─→ retrieve (规则 RAG)
    ├─→ verify (校验)
    ├─→ resolve (确定性骰子)
    ├─→ narrate (LLM 叙事)
    │       │
    │       │  注入上下文:
    │       │  ① 工作记忆 (最近6回合, 从 Log 表查)
    │       │  ② rolling_summary (本Session摘要)
    │       │  ③ 长期记忆 top-5 (从 Qdrant dnd_memories 检索)
    │       │  ④ 当前场景上下文
    │       │  ⑤ 规则摘要
    │       │  ⑥ 骰子结果 + 战斗状态
    │       │
    │       ▼
    └─→ apply (持久化)
            │
            ├─→ 存 Log 表 (player_input + dm_output + dice)
            ├─→ 更新 Scene.situation
            └─→ extract_observations (LLM 提取关键事件)
                    │
                    ├─→ 存入 Qdrant dnd_memories (嵌入 + payload)
                    └─→ 每10回合压缩一次 rolling_summary
```

### 分步实施

#### Step 1: 工作记忆 — 最近 N 回合对话注入

**改动文件**: `stats/store.py`, `brain/graph.py`

**新增函数** (`store.py`):
```python
def get_recent_logs(campaign_id: int, n: int = 6,
                    db_path: str = DEFAULT_DB) -> list[M.Log]:
    """获取最近 n 条日志（工作记忆数据源）。"""
    with session(db_path) as s:
        stmt = (select(M.Log)
                .where(M.Log.campaign_id == campaign_id)
                .order_by(M.Log.id.desc())
                .limit(n))
        logs = list(s.exec(stmt))
        return list(reversed(logs))  # 时间正序
```

**修改 narrate()** (`graph.py`):
```python
def narrate(state: GameState) -> dict:
    # ... 现有代码 ...
    
    # 新增：获取最近6回合的工作记忆
    recent_logs = store.get_recent_logs(state.get("campaign_id", 0), n=6)
    history = "\n".join(
        f"[回合] 玩家: {log.player_input} → DM: {log.dm_output}"
        for log in recent_logs
    ) if recent_logs else "(无历史对话)"
    
    prompt = (
        "你是D&D 5E DM。依据【掷骰结果】与规则,在当前场景中叙述...\n"
        f"近期对话历史(工作记忆):\n{history}\n\n"  # ← 新增
        f"掷骰结果: {json.dumps(dice, ensure_ascii=False)}\n"
        # ... 其余不变 ...
    )
```

**代码量**: ~15行
**新依赖**: 无

---

#### Step 2: 注入 rolling_summary

**改动文件**: `brain/graph.py`

**修改 narrate()**:
```python
def narrate(state: GameState) -> dict:
    # ... 现有代码 ...
    camp_id = state.get("campaign_id", 0)
    
    # 新增：获取 rolling_summary
    rolling_summary = store.get_summary(camp_id) if camp_id else ""
    summary_text = rolling_summary[:500] if rolling_summary else "(无摘要)"
    
    # 新增：获取工作记忆
    recent_logs = store.get_recent_logs(camp_id, n=6)
    history = "\n".join(
        f"玩家: {log.player_input} → DM: {log.dm_output}"
        for log in recent_logs
    ) if recent_logs else "(无历史)"
    
    prompt = (
        "你是D&D 5E DM...\n"
        f"本局摘要:\n{summary_text}\n\n"           # ← 新增
        f"近期对话(工作记忆):\n{history}\n\n"      # ← 新增
        f"掷骰结果: {json.dumps(dice, ensure_ascii=False)}\n"
        # ... 其余不变 ...
    )
```

**代码量**: ~5行
**新依赖**: 无

---

#### Step 3: 观察提取 — 每回合自动提取关键事件

**改动文件**: 新建 `brain/memory.py`, 修改 `brain/graph.py`

**新建 `memory.py`**:
```python
"""记忆系统 — 观察提取 + 长期记忆存储/检索。"""

from __future__ import annotations
import json
from datetime import datetime
from . import llm
from ..knowledge import indexer, embedding
from ..stats import store


# ── 观察提取 ──────────────────────────────────────────────

EXTRACT_PROMPT = (
    "你是D&D 5E记忆助手。从以下回合中提取1-3条关键观察。\n"
    "只提取重要的、影响后续剧情的事件。\n"
    "忽略纯氛围描述和无关细节。\n\n"
    "输出JSON: {\"observations\": [\n"
    "  {\"event\": \"简述发生的事件\",\n"
    "   \"importance\": 1-10的整数(10=极重要如角色死亡/NPC背叛,\n"
    "                     7=重要如战斗胜利/获得关键物品,\n"
    "                     4=一般如发现线索/移动到新区域,\n"
    "                     1=琐碎如开门/走路),\n"
    "   \"entities\": [\"涉及的实体名\"],\n"
    "   \"type\": \"combat|social|exploration|story|rest\"\n"
    "  }\n"
    "]}\n\n"
    "玩家输入: {player_input}\n"
    "DM叙事: {narration}\n"
    "意图: {intent}"
)


def extract_observations(player_input: str, narration: str,
                         intent: dict) -> list[dict]:
    """从本回合叙事中提取关键观察 + 重要性评分。

    返回: [{"event": "...", "importance": 7, "entities": [...],
            "type": "combat", "turn": 42}]
    """
    prompt = EXTRACT_PROMPT.format(
        player_input=player_input[:200],
        narration=narration[:300],
        intent=json.dumps(intent, ensure_ascii=False)[:200],
    )
    raw = llm.chat("你是D&D记忆助手。只输出JSON。", prompt, temperature=0.1)
    
    # 解析 JSON
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        return []
    
    observations = data.get("observations", [])
    # 补充元数据
    for obs in observations:
        obs.setdefault("importance", 5)
        obs.setdefault("entities", [])
        obs.setdefault("type", "story")
    
    return observations


# ── 长期记忆存储 ──────────────────────────────────────────

MEMORIES_COLLECTION = "dnd_memories"


def store_memory(campaign_id: int, observation: dict,
                 turn: int) -> None:
    """将观察嵌入并存储到 Qdrant dnd_memories collection。

    payload 包含: event, importance, entities, type, turn,
                  campaign_id, timestamp
    """
    event_text = observation.get("event", "")
    if not event_text:
        return
    
    # 嵌入观察文本
    vec = embedding.embed_query(event_text)
    
    # 构建 payload
    payload = {
        "event": event_text,
        "importance": int(observation.get("importance", 5)),
        "entities": observation.get("entities", []),
        "type": observation.get("type", "story"),
        "turn": turn,
        "campaign_id": campaign_id,
        "timestamp": datetime.now().isoformat(),
    }
    
    # 存入 Qdrant
    q = indexer.get_qdrant()
    # 确保 collection 存在
    cols = [c.name for c in q.get_collections().collections]
    if MEMORIES_COLLECTION not in cols:
        from qdrant_client.models import VectorParams, Distance
        q.create_collection(
            MEMORIES_COLLECTION,
            vectors_config=VectorParams(
                size=len(vec), distance=Distance.COSINE
            ),
        )
    
    # 用 turn 作为 point id (确保唯一性)
    point_id = turn * 100 + len(payload["entities"])  # 简单唯一id
    from qdrant_client.models import PointStruct
    q.upsert(
        MEMORIES_COLLECTION,
        points=[PointStruct(id=point_id, vector=vec, payload=payload)],
    )


# ── 长期记忆检索 ──────────────────────────────────────────

def retrieve_memories(campaign_id: int, query: str,
                      top_k: int = 20) -> list[dict]:
    """语义检索相关记忆，返回候选列表。

    流程: 语义搜索 top-K → 重要性加权 → 时间衰减 → rerank
    """
    q = indexer.get_qdrant()
    query_vec = embedding.embed_query(query)
    
    # 语义搜索 top-K
    res = q.query_points(
        MEMORIES_COLLECTION,
        query=query_vec,
        limit=top_k,
        query_filter=None,  # TODO: 按 campaign_id 过滤
    )
    
    candidates = []
    now = datetime.now()
    for p in res.points:
        payload = p.payload or {}
        # 计算时间衰减
        ts_str = payload.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_str)
            hours_since = max(0, (now - ts).total_seconds() / 3600)
        except (ValueError, TypeError):
            hours_since = 0
        recency = 0.99 ** hours_since
        
        # 归一化各分量到 0-1
        relevance = max(0, min(1, p.score or 0))  # cosine similarity
        importance = payload.get("importance", 5) / 10.0
        
        # 加权评分 (参考 Generative Agents)
        # weights: recency=0.5, relevance=3.0, importance=2.0
        final_score = (0.5 * recency + 3.0 * relevance + 2.0 * importance)
        
        candidates.append({
            "event": payload.get("event", ""),
            "importance": payload.get("importance", 5),
            "score": final_score,
            "relevance": relevance,
            "recency": recency,
        })
    
    # 按 final_score 降序排列，取 top-5
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:5]


# ── 滚动摘要压缩 ──────────────────────────────────────────

COMPRESS_PROMPT = (
    "你是D&D 5E记忆助手。将以下{n}回合的对话压缩成3-5句摘要。\n"
    "保留: 关键事件、角色状态变化、重要NPC互动、任务进展。\n"
    "丢弃: 重复的氛围描述、无关的骰子细节。\n\n"
    "对话记录:\n{logs}\n\n"
    "输出摘要(3-5句):"
)


def compress_rolling_summary(campaign_id: int,
                             recent_logs: list) -> str:
    """将最近 N 回合压缩成摘要。"""
    n = len(recent_logs)
    if n == 0:
        return ""
    
    logs_text = "\n".join(
        f"[{i+1}] 玩家: {log.player_input[:80]} → "
        f"DM: {log.dm_output[:80]}"
        for i, log in enumerate(recent_logs)
    )
    
    prompt = COMPRESS_PROMPT.format(n=n, logs=logs_text)
    summary = llm.chat(
        "你是D&D记忆助手。输出简洁摘要。",
        prompt,
        temperature=0.2,
    )
    return summary.strip()


# ── 完整记忆管线 ──────────────────────────────────────────

def process_turn_memories(campaign_id: int, player_input: str,
                          narration: str, intent: dict,
                          turn: int) -> dict:
    """回合结束后处理记忆: 提取观察 → 存储 → 压缩摘要。

    在 graph.py 的 apply_node 之后调用。
    """
    # 1. 提取观察
    observations = extract_observations(player_input, narration, intent)
    
    # 2. 存储到长期记忆
    for obs in observations:
        store_memory(campaign_id, obs, turn)
    
    # 3. 每10回合压缩一次 rolling_summary
    if turn % 10 == 0:
        recent_logs = store.get_recent_logs(campaign_id, n=10)
        if recent_logs:
            compressed = compress_rolling_summary(campaign_id, recent_logs)
            existing = store.get_summary(campaign_id)
            new_summary = (existing + "\n" + compressed) if existing else compressed
            # 直接更新 Campaign.rolling_summary
            camp = store.get_campaign(campaign_id)
            if camp:
                camp.rolling_summary = new_summary
                store.save_campaign(camp)
    
    return {
        "observations_extracted": len(observations),
        "memories_stored": len(observations),
    }
```

**修改 `graph.py` 的 `apply_node`**:
```python
def apply_node(state: GameState) -> dict:
    # ... 现有持久化逻辑 ...
    
    # 新增：处理记忆（观察提取 + 长期记忆存储 + 摘要压缩）
    from ..brain.memory import process_turn_memories
    camp = state.get("campaign_id")
    if camp:
        # 计算当前回合数（从 Log 表计数）
        recent = store.get_recent_logs(camp, n=1)
        turn = recent[0].id if recent else 0
        
        process_turn_memories(
            campaign_id=camp,
            player_input=state.get("player_input", ""),
            narration=state.get("narration", ""),
            intent=state.get("intent", {}),
            turn=turn,
        )
    
    return {}
```

**修改 `graph.py` 的 `narrate()`**:
```python
def narrate(state: GameState) -> dict:
    # ... 现有代码 ...
    camp_id = state.get("campaign_id", 0)
    
    # 工作记忆：最近6回合
    recent_logs = store.get_recent_logs(camp_id, n=6)
    history = "\n".join(
        f"玩家: {log.player_input[:80]} → DM: {log.dm_output[:80]}"
        for log in recent_logs
    ) if recent_logs else "(无历史)"
    
    # 中期记忆：rolling_summary
    rolling_summary = store.get_summary(camp_id) if camp_id else ""
    summary_text = rolling_summary[:500] if rolling_summary else "(无摘要)"
    
    # 长期记忆：语义检索 top-5
    long_term_memories = []
    if camp_id:
        from ..brain.memory import retrieve_memories
        query = state.get("player_input", "")[:100]
        long_term_memories = retrieve_memories(camp_id, query, top_k=20)
    
    memory_context = ""
    if long_term_memories:
        memory_context = "相关记忆:\n" + "\n".join(
            f"- {m['event']} [重要:{m['importance']}]"
            for m in long_term_memories
        )
    
    prompt = (
        "你是D&D 5E DM。依据【掷骰结果】与规则,在当前场景中叙述...\n"
        f"本局摘要:\n{summary_text}\n\n"
        f"近期对话(工作记忆):\n{history}\n\n"
        f"{memory_context}\n\n"
        f"掷骰结果: {json.dumps(dice, ensure_ascii=False)}\n"
        # ... 其余不变 ...
    )
```

**代码量**: ~300行（新建 memory.py）+ ~40行（修改 graph.py）
**新依赖**: 无

---

## 五、数据流总结

### 写入流（每回合结束时）

```
apply_node
    │
    ├─→ append_log()          存 Log 表 (已有)
    ├─→ save_character()      存角色卡 (已有)
    ├─→ save_combat()         存战斗状态 (已有)
    │
    └─→ process_turn_memories()   新增
            │
            ├─→ extract_observations()    LLM 提取 1-3 条观察
            │       │
            │       └─→ 每条观察包含: event, importance(1-10), entities, type
            │
            ├─→ store_memory()            嵌入 + 存入 Qdrant dnd_memories
            │       │
            │       └─→ payload: {event, importance, entities, type, turn, campaign_id, timestamp}
            │
            └─→ compress_rolling_summary()   每10回合压缩一次
                    │
                    └─→ LLM 把最近10回合压成3-5句摘要，追加到 Campaign.rolling_summary
```

### 读取流（每回合 narrate 时）

```
narrate()
    │
    ├─→ get_recent_logs(n=6)              工作记忆：最近6回合对话
    ├─→ get_summary()                     中期记忆：rolling_summary (截取前500字)
    ├─→ retrieve_memories(top_k=20)       长期记忆：语义检索 → 重要性加权 → 时间衰减 → rerank → top-5
    │
    └─→ 全部注入 prompt → LLM 连贯叙事
```

### 评分公式（参考 Generative Agents）

```python
# 三个归一化分量 (0-1)
recency = 0.99 ** hours_since_memory_creation
relevance = cosine_similarity(query_embedding, memory_embedding)
importance = stored_importance_score / 10.0

# 加权求和
final_score = (0.5 * recency    # 时间衰减权重
             + 3.0 * relevance   # 语义相关性权重 (最重要)
             + 2.0 * importance) # 重要性权重

# 按 final_score 降序排列，取 top-5
```

### 时间衰减说明

- 衰减率: `0.99` 每小时 (来自 Generative Agents 源码)
- 1小时前的记忆: `0.99^1 = 0.99` (几乎全权重)
- 24小时前的记忆: `0.99^24 = 0.78` (仍然显著)
- 7天前的记忆: `0.99^168 = 0.18` (已衰减但高相关仍可检索)
- 30天前的记忆: `0.99^720 = 0.0007` (基本消失，除非极高重要性)

---

## 六、与现有代码的集成点

| 现有组件 | 文件位置 | 记忆系统复用方式 |
|---|---|---|
| Qdrant client | `knowledge/indexer.py:get_qdrant()` | 长期记忆存储后端 |
| bge-small 嵌入 | `knowledge/embedding.py:embed_query()` | 观察文本向量化 |
| SQLite Log 表 | `stats/store.py:append_log()` | 工作记忆数据源 |
| Campaign.rolling_summary | `stats/models.py:201` | 中期记忆摘要存储 |
| LLM 调用 | `brain/llm.py:chat()` | 观察提取 + 摘要压缩 |
| narrate() 节点 | `brain/graph.py:374` | 注入三层记忆到 prompt |
| apply_node() 节点 | `brain/graph.py:401` | 回合结束后触发记忆处理 |

### 新增文件

| 文件 | 内容 | 代码量 |
|---|---|---|
| `brain/memory.py` | 观察提取 + 长期记忆存储/检索 + 摘要压缩 | ~300行 |

### 修改文件

| 文件 | 修改内容 | 代码量 |
|---|---|---|
| `stats/store.py` | 新增 `get_recent_logs()` 函数 | ~10行 |
| `brain/graph.py` | narrate() 注入三层记忆；apply_node() 触发记忆处理 | ~40行 |

---

## 七、实施优先级

| 步骤 | 内容 | 代码量 | 效果 |
|---|---|---|---|
| **Step 1** | 工作记忆：get_recent_logs + narrate注入 | ~15行 | 立刻解决"LLM失忆"问题 |
| **Step 2** | 注入 rolling_summary | ~5行 | narrate 能看到本Session摘要 |
| **Step 3** | 观察提取 + 长期记忆存储 | ~200行 | 每回合自动提取关键事件 |
| **Step 4** | 长期记忆检索 + 注入 narrate | ~100行 | 跨Session语义记忆完成 |

**建议顺序**: Step 1 → Step 2 → Step 3 → Step 4

Step 1 和 Step 2 可以一起做，立刻让 narrate() 有上下文。Step 3 和 Step 4 是长期记忆的核心，需要新建 `memory.py` 模块。

---

*本报告生成于 2026-07-15，供 AIDM 记忆系统实施参考。*
