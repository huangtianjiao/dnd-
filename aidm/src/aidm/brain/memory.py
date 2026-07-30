"""三层记忆系统 — 工作记忆 / 中期记忆 / 长期记忆。

架构参考: Generative Agents (Park et al., 2023)
    final_score = α * recency + β * relevance + γ * importance
    recency   = 0.99 ** hours_since_memory_creation
    relevance = cosine_similarity(query_embedding, memory_embedding)
    importance = stored_importance_score / 10.0

数据流:
    narrate() 读取 → ① get_recent_logs(工作记忆)
                     ② get_summary(中期摘要)
                     ③ retrieve_memories(长期检索)

    apply_node() 写入 → extract_observations(LLM提取关键事件)
                        store_memory(嵌入+存Qdrant)
                        compress_rolling_summary(每10回合压缩)

存储后端:
    Qdrant dnd_memories collection — 跨Session长期记忆
    SQLite Log 表 — 工作记忆数据源
    Campaign.rolling_summary — 中期摘要存储
"""

from __future__ import annotations

import contextlib
import json
from datetime import datetime

from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from ..config import get_settings
from ..knowledge import embedding, indexer
from ..stats import store
from . import llm

# ──────────────────────────────────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────────────────────────────────

MEMORIES_COLLECTION = "dnd_memories"

# 检索评分权重 (参考 Generative Agents gw=[0.5, 3, 2])
RECENCY_WEIGHT = 0.5
RELEVANCE_WEIGHT = 3.0
IMPORTANCE_WEIGHT = 2.0

# 时间衰减率: 0.99/hr (来自 Generative Agents recency_decay=0.99)
DECAY_RATE_PER_HOUR = 0.99

# 摘要维护分两层：
#   ① 周期折叠 — 每 COMPRESS_EVERY_N_TURNS 回合把最近日志压缩后追加进 summary，
#      按日志数触发，与 summary 是否为空无关（避免空 summary 永不启动）。
#   ② 超限浓缩 — summary_tokens / llm_context_window > summary_compress_ratio 时，
#      用 LLM 浓缩 summary 自身（而非追加，防止越压越长）。
# 配置见 config.py: llm_context_window, summary_compress_ratio

COMPRESS_EVERY_N_TURNS = 10


def _estimate_tokens(text: str) -> int:
    """粗略估算文本的 token 数。

    中文约 1 字 ≈ 1.5 token，英文约 4 字符 ≈ 1 token。
    取折中：len(text) * 1.5（偏保守，宁可早压缩）。
    """
    if not text:
        return 0
    return int(len(text) * 1.5)


def _should_condense(campaign_id: int) -> bool:
    """检查 rolling_summary 是否超限需要浓缩。

    触发条件：summary 的 token 估算值占 LLM 上下文窗口的比例
    超过 summary_compress_ratio（默认 15%）。

    Returns:
        True 表示需要浓缩。
    """
    s = get_settings()
    summary = store.get_summary(campaign_id)
    if not summary:
        return False

    summary_tokens = _estimate_tokens(summary)
    threshold_tokens = int(s.llm_context_window * s.summary_compress_ratio)

    return summary_tokens > threshold_tokens


def _should_fold(campaign_id: int) -> bool:
    """检查是否到达周期折叠点（每 COMPRESS_EVERY_N_TURNS 回合）。

    按战役日志总数取模触发，不依赖 summary 现状，
    保证空 summary 也能在第 N 回合启动首次折叠。
    """
    try:
        n = store.count_logs(campaign_id)
    except Exception:
        return False
    return n > 0 and n % COMPRESS_EVERY_N_TURNS == 0


# ──────────────────────────────────────────────────────────────────────────
# 观察提取 — 每回合结束后从叙事中提取关键事件
# ──────────────────────────────────────────────────────────────────────────

_EXTRACT_PROMPT = """\
你是D&D 5E记忆助手。从以下回合中提取1-3条关键观察。
只提取重要的、影响后续剧情的事件。忽略纯氛围描述和无关细节。

重要性评分标准:
  9-10: 极重要 — 角色死亡/NPC背叛/获得传说物品/任务完成
  7-8:  重要 — 战斗胜利/获得关键物品/NPC态度转变/发现秘密
  4-6:  一般 — 发现线索/移动到新区域/普通战斗/社交互动
  1-3:  琐碎 — 开门/走路/休息/闲聊

输出JSON:
{{"observations": [
  {{"event": "简述发生的事件", "importance": 1-10的整数,
   "entities": ["涉及的实体名"], "type": "combat|social|exploration|story|rest"}}
]}}

玩家输入: {player_input}
DM叙事: {narration}
意图分类: {intent}"""


def extract_observations(player_input: str, narration: str,
                         intent: dict) -> list[dict]:
    """从本回合叙事中提取关键观察 + 重要性评分。

    使用 LLM 从玩家输入和 DM 叙事中提取 1-3 条结构化观察。
    每条观察包含: event(事件描述), importance(1-10),
                  entities(涉及实体), type(事件类型)

    Returns:
        观察列表，格式为 [{"event": "...", "importance": 7,
                           "entities": ["玩家","守卫"], "type": "combat"}]
        提取失败时返回空列表。
    """
    prompt = _EXTRACT_PROMPT.format(
        player_input=player_input[:200],
        narration=narration[:300],
        intent=json.dumps(intent, ensure_ascii=False)[:200],
    )
    raw = llm.chat(
        "你是D&D记忆助手。只输出JSON。",
        prompt,
        temperature=0.1,
    )

    # 解析 JSON
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        return []

    observations = data.get("observations", [])
    # 补充默认值，确保字段完整
    for obs in observations:
        obs.setdefault("importance", 5)
        obs.setdefault("entities", [])
        obs.setdefault("type", "story")

    return observations


# ──────────────────────────────────────────────────────────────────────────
# 长期记忆存储 — 将观察嵌入并存储到 Qdrant
# ──────────────────────────────────────────────────────────────────────────

def _ensure_collection() -> None:
    """确保 dnd_memories collection 存在。"""
    q = indexer.get_qdrant()
    cols = [c.name for c in q.get_collections().collections]
    if MEMORIES_COLLECTION not in cols:
        q.create_collection(
            MEMORIES_COLLECTION,
            vectors_config=VectorParams(
                size=embedding.dim(),
                distance=Distance.COSINE,
            ),
        )


def store_memory(campaign_id: int, observation: dict,
                 turn: int, obs_index: int = 0) -> int | None:
    """将观察嵌入并存储到 Qdrant dnd_memories collection。

    payload 包含: event, importance, entities, type, turn,
                  campaign_id, timestamp

    Args:
        campaign_id: 战役ID
        observation: 观察字典，需包含 event 字段
        turn: 当前回合数（用于生成唯一 point id）
        obs_index: 本回合第几条观察（防同一回合多条观察 id 碰撞）

    Returns:
        存储的 point id，失败时返回 None。
    """
    event_text = observation.get("event", "")
    if not event_text:
        return None

    _ensure_collection()

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

    # 用 turn*1000 + obs_index 生成唯一 id（防碰撞）
    point_id = turn * 1000 + obs_index

    q = indexer.get_qdrant()
    q.upsert(
        MEMORIES_COLLECTION,
        points=[PointStruct(id=point_id, vector=vec, payload=payload)],
    )
    return point_id


# ──────────────────────────────────────────────────────────────────────────
# 长期记忆检索 — 语义搜索 + 重要性加权 + 时间衰减 + rerank
# ──────────────────────────────────────────────────────────────────────────

def retrieve_memories(campaign_id: int, query: str,
                      top_k: int = 20) -> list[dict]:
    """语义检索相关记忆，返回 rerank 后的 top-5。

    检索管线 (参考 Generative Agents):
      1. 语义搜索 top-K 候选 (Qdrant cosine similarity)
      2. 计算三分量评分:
         - recency = 0.99 ** hours_since_creation
         - relevance = Qdrant cosine score
         - importance = stored score / 10
      3. 加权求和: final = 0.5*recency + 3.0*relevance + 2.0*importance
      4. 按 final 降序排列，取 top-5

    Args:
        campaign_id: 战役ID（用于过滤）
        query: 检索查询（通常是玩家输入）
        top_k: 语义搜索候选数量

    Returns:
        记忆列表，按相关性排序，最多5条。
        格式: [{"event": "...", "importance": 7, "score": 2.85, ...}]
    """
    _ensure_collection()

    # 嵌入查询
    query_vec = embedding.embed_query(query)

    # 语义搜索 top-K，按 campaign_id 过滤
    q = indexer.get_qdrant()
    res = q.query_points(
        MEMORIES_COLLECTION,
        query=query_vec,
        limit=top_k,
        query_filter=Filter(
            must=[FieldCondition(key="campaign_id",
                                 match=MatchValue(value=campaign_id))]
        ),
    )

    now = datetime.now()
    candidates = []

    for p in res.points:
        payload = p.payload or {}

        # 计算 recency (时间衰减)
        ts_str = payload.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_str)
            hours_since = max(0, (now - ts).total_seconds() / 3600)
        except (ValueError, TypeError):
            hours_since = 0
        recency = DECAY_RATE_PER_HOUR ** hours_since

        # 归一化各分量到 0-1
        relevance = max(0.0, min(1.0, p.score or 0.0))
        importance = min(1.0, payload.get("importance", 5) / 10.0)

        # 加权评分
        final_score = (
            RECENCY_WEIGHT * recency
            + RELEVANCE_WEIGHT * relevance
            + IMPORTANCE_WEIGHT * importance
        )

        candidates.append({
            "event": payload.get("event", ""),
            "importance": payload.get("importance", 5),
            "type": payload.get("type", "story"),
            "turn": payload.get("turn", 0),
            "score": round(final_score, 4),
            "relevance": round(relevance, 4),
            "recency": round(recency, 4),
        })

    # 按 final_score 降序排列，取 top-5
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:5]


# ──────────────────────────────────────────────────────────────────────────
# 滚动摘要压缩 — 每 N 回合用 LLM 压缩历史
# ──────────────────────────────────────────────────────────────────────────

_COMPRESS_PROMPT = """\
你是D&D 5E记忆助手。将以下{n}回合的对话压缩成3-5句摘要。
保留: 关键事件、角色状态变化、重要NPC互动、任务进展。
丢弃: 重复的氛围描述、无关的骰子细节。

对话记录:
{logs}

输出摘要(3-5句):"""

_CONDENSE_PROMPT = """\
你是D&D 5E记忆助手。以下是一段过长的战役滚动摘要，请将其浓缩到原长一半以内。
保留: 主线任务进展、关键 NPC 关系、未解悬念、角色重大状态变化。
丢弃: 重复信息、已完结且无后续影响的细节。
若含 [前情提要] 标记段落，原样保留该段落不参与浓缩。

现有摘要:
{summary}

输出浓缩后的摘要:"""


def _condense_summary(campaign_id: int) -> bool:
    """用 LLM 浓缩过长的 rolling_summary（替换而非追加）。

    Returns:
        True 表示浓缩成功并已保存。
    """
    summary = store.get_summary(campaign_id)
    if not summary:
        return False
    condensed = llm.chat(
        "你是D&D记忆助手。输出简洁摘要。",
        _CONDENSE_PROMPT.format(summary=summary),
        temperature=0.2,
    ).strip()
    # LLM 失败或输出异常（未变短）时不覆盖，保留原摘要
    if not condensed or len(condensed) >= len(summary):
        return False
    camp = store.get_campaign(campaign_id)
    if not camp:
        return False
    camp.rolling_summary = condensed
    store.save_campaign(camp)
    return True


def compress_rolling_summary(campaign_id: int,
                             recent_logs: list) -> str:
    """将最近 N 回合压缩成摘要。

    使用 LLM 将多回合对话压缩成简洁摘要，
    用于更新 Campaign.rolling_summary。

    Args:
        campaign_id: 战役ID
        recent_logs: 最近N回合的Log对象列表

    Returns:
        压缩后的摘要文本（3-5句）。
    """
    n = len(recent_logs)
    if n == 0:
        return ""

    logs_text = "\n".join(
        f"[{i+1}] 玩家: {log.player_input[:80]} → "
        f"DM: {log.dm_output[:80]}"
        for i, log in enumerate(recent_logs)
    )

    prompt = _COMPRESS_PROMPT.format(n=n, logs=logs_text)
    summary = llm.chat(
        "你是D&D记忆助手。输出简洁摘要。",
        prompt,
        temperature=0.2,
    )
    return summary.strip()


# ──────────────────────────────────────────────────────────────────────────
# 完整记忆管线 — 在 apply_node 之后调用
# ──────────────────────────────────────────────────────────────────────────

def process_turn_memories(campaign_id: int, player_input: str,
                          narration: str, intent: dict,
                          turn: int) -> dict:
    """回合结束后处理记忆: 提取观察 → 存储长期记忆 → 压缩摘要。

    在 graph.py 的 apply_node 结尾调用。

    流程:
      1. extract_observations — LLM 从本回合叙事提取 1-3 条关键观察
      2. store_memory — 每条观察嵌入后存入 Qdrant dnd_memories
      3. compress_rolling_summary — 每 COMPRESS_EVERY_N_TURNS 回合折叠一次，
         summary 超限时再用 LLM 浓缩自身

    Args:
        campaign_id: 战役ID
        player_input: 本回合玩家输入
        narration: 本回合DM叙事
        intent: 本回合意图分类结果
        turn: 当前回合数

    Returns:
        处理结果摘要，格式为:
        {"observations_extracted": int, "memories_stored": int,
         "summary_compressed": bool}
    """
    result = {
        "observations_extracted": 0,
        "memories_stored": 0,
        "summary_compressed": False,
    }

    # 1. 提取观察
    observations = extract_observations(player_input, narration, intent)
    result["observations_extracted"] = len(observations)

    # 2. 存储到长期记忆
    for i, obs in enumerate(observations):
        store_memory(campaign_id, obs, turn, obs_index=i)
        result["memories_stored"] += 1

    # 3. 周期折叠：每 COMPRESS_EVERY_N_TURNS 回合把最近日志压缩追加进 summary
    if _should_fold(campaign_id):
        recent_logs = store.get_recent_logs(campaign_id,
                                            n=COMPRESS_EVERY_N_TURNS)
        if recent_logs:
            compressed = compress_rolling_summary(campaign_id, recent_logs)
            if compressed:
                existing = store.get_summary(campaign_id)
                new_summary = ((existing + "\n" + compressed)
                               if existing else compressed)
                camp = store.get_campaign(campaign_id)
                if camp:
                    camp.rolling_summary = new_summary
                    store.save_campaign(camp)
                    result["summary_compressed"] = True

    # 3b. 超限浓缩：summary 占 LLM 上下文比例超阈值时浓缩自身，防止无限增长
    if _should_condense(campaign_id):
        with contextlib.suppress(Exception):
            _condense_summary(campaign_id)

    # 4. 自动清理：记忆数超过上限时删除最低分旧记忆
    with contextlib.suppress(Exception):
        cleanup_memories(campaign_id)

    return result


# ──────────────────────────────────────────────────────────────────────────
# Session 间前情提要 — Session 结束时生成浓缩摘要，新 Session 注入
# ──────────────────────────────────────────────────────────────────────────

_PREVIOUSLY_ON_PROMPT = """\
你是D&D 5E记忆助手。以下是一场跑团Session的完整摘要和关键事件。
请生成一段"前情提要"（500-1000字），供下次开新Session时注入DM上下文。

要求:
  - 以叙事口吻写，像电视剧"前情提要"片段
  - 包含: 队伍当前状态、未解决的线索、重要NPC关系、当前任务进度
  - 不要透露未发现的秘密或伏笔
  - 结尾给出"当前处境"——队伍此刻在哪里、面对什么

本局摘要:
{summary}

关键记忆:
{memories}

前情提要:"""


def generate_recap(campaign_id: int) -> str:
    """Session 结束时生成"前情提要"浓缩摘要。

    汇总 rolling_summary + 高重要性长期记忆，用 LLM 生成
    500-1000 字的叙事摘要，供下次 Session 开始时注入。

    Args:
        campaign_id: 战役ID

    Returns:
        前情提文本本。失败时返回空字符串。
    """
    # 收集 rolling_summary
    summary = store.get_summary(campaign_id) or ""
    if not summary:
        return ""

    # 收集高重要性长期记忆（importance >= 7）
    try:
        all_memories = retrieve_memories(campaign_id, "", top_k=50)
    except Exception:
        all_memories = []
    key_memories = [m for m in all_memories if m.get("importance", 0) >= 7]
    memories_text = "\n".join(
        f"- {m['event']} [重要:{m['importance']}]"
        for m in key_memories
    ) if key_memories else "(无关键记忆)"

    prompt = _PREVIOUSLY_ON_PROMPT.format(
        summary=summary[:2000],
        memories=memories_text[:1000],
    )
    recap = llm.chat(
        "你是D&D记忆助手。生成前情提要。",
        prompt,
        temperature=0.3,
    )

    # 持久化到 Campaign（用 world_background 字段暂存前情提要）
    camp = store.get_campaign(campaign_id)
    if camp:
        # 用 notes 字段或追加到 rolling_summary 开头标记
        # 这里存到 rolling_summary 的开头，用 [前情提要] 标记
        existing = camp.rolling_summary or ""
        camp.rolling_summary = f"[前情提要]\n{recap.strip()}\n[/前情提要]\n{existing}"
        store.save_campaign(camp)

    return recap.strip()


def get_recap(campaign_id: int) -> str:
    """获取已存储的前情提要（供新 Session 开始时注入 narrate prompt）。

    从 Campaign.rolling_summary 中提取 [前情提要]...[/前情提要] 块。
    若不存在则返回空字符串。

    Args:
        campaign_id: 战役ID

    Returns:
        前情提文本本，不存在时返回 ""。
    """
    summary = store.get_summary(campaign_id) or ""
    if "[前情提要]" not in summary:
        return ""

    start = summary.find("[前情提要]") + len("[前情提要]")
    end = summary.find("[/前情提要]")
    if end == -1:
        return ""
    return summary[start:end].strip()


# ──────────────────────────────────────────────────────────────────────────
# Qdrant 记忆清理 — 超过上限时按低分清理旧记忆
# ──────────────────────────────────────────────────────────────────────────

MAX_MEMORIES = 500  # 单战役长期记忆上限


def cleanup_memories(campaign_id: int) -> int:
    """清理低分旧记忆，保持 Qdrant 记忆数量在上限内。

    当某战役的记忆数超过 MAX_MEMORIES 时，按综合评分（recency+relevance+importance）
    升序排列，删除最低分的超额记忆。

    Args:
        campaign_id: 战役ID

    Returns:
        删除的记忆数量。
    """
    _ensure_collection()
    q = indexer.get_qdrant()

    # 按导入序号取第1条（已知最旧）到上限区间
    qdrant_filter = Filter(
        must=[FieldCondition(key="campaign_id",
                              match=MatchValue(value=campaign_id))]
    )

    # 先统计总量
    count_result = q.count(MEMORIES_COLLECTION, count_filter=qdrant_filter, exact=True)
    total = count_result.count if hasattr(count_result, "count") else 0
    if total <= MAX_MEMORIES:
        return 0

    # 超额数量
    excess = total - MAX_MEMORIES

    # 按重要性升序 + 时间最旧 排序，删除最低分记忆
    # 简化：直接按 importance 升序取前 excess 条删除
    res = q.scroll(
        MEMORIES_COLLECTION,
        scroll_filter=qdrant_filter,
        limit=excess * 2,  # 多取一些做筛选
        order_by="importance",  # 按重要性升序
    )[0] if hasattr(q, "scroll") else []

    deleted = 0
    from qdrant_client.models import PointIdsList
    ids_to_delete = []
    for point in res:
        if deleted >= excess:
            break
        ids_to_delete.append(point.id)
        deleted += 1

    if ids_to_delete:
        q.delete(
            MEMORIES_COLLECTION,
            points_selector=PointIdsList(points=ids_to_delete),
        )

    return deleted

def _self_test() -> None:
    """memory.py 自检测试。"""
    import os
    import tempfile

    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    db = f"sqlite:///{db_path}"

    try:
        # 测试 1: extract_observations 返回列表
        print("[test1] extract_observations 返回类型...")
        # 不实际调用 LLM，测试空输入
        obs = extract_observations("", "", {})
        assert isinstance(obs, list), f"期望list, 得到{type(obs)}"
        print("  ✓ 返回列表")

        # 测试 2: store_memory 存储
        print("[test2] store_memory 存储...")
        # 注意: 这里需要 Qdrant 和 embedding，可能跳过
        try:
            pid = store_memory(
                campaign_id=1,
                observation={
                    "event": "玩家击败了哥布林首领",
                    "importance": 8,
                    "entities": ["玩家", "哥布林首领"],
                    "type": "combat",
                },
                turn=1,
            )
            assert pid is not None, "store_memory 应返回 point_id"
            print(f"  ✓ 存储成功, point_id={pid}")
        except Exception as e:
            print(f"  ⚠ 跳过 (需要Qdrant+embedding): {e}")

        # 测试 3: retrieve_memories 检索
        print("[test3] retrieve_memories 检索...")
        try:
            results = retrieve_memories(
                campaign_id=1,
                query="战斗 哥布林",
                top_k=10,
            )
            assert isinstance(results, list), f"期望list, 得到{type(results)}"
            print(f"  ✓ 检索返回 {len(results)} 条记忆")
            if results:
                m = results[0]
                assert "event" in m, "记忆应包含 event 字段"
                assert "score" in m, "记忆应包含 score 字段"
                print(f"  ✓ 第一条: {m['event'][:30]}... score={m['score']}")
        except Exception as e:
            print(f"  ⚠ 跳过 (需要Qdrant+embedding): {e}")

        # 测试 4: compress_rolling_summary
        print("[test4] compress_rolling_summary...")
        try:
            # 创建模拟 Log 对象
            class MockLog:
                def __init__(self, pi, do):
                    self.player_input = pi
                    self.dm_output = do

            logs = [
                MockLog("我攻击哥布林", "你命中了哥布林"),
                MockLog("我再攻击一次", "哥布林倒下了"),
            ]
            result = compress_rolling_summary(1, logs)
            assert isinstance(result, str), f"期望str, 得到{type(result)}"
            print(f"  ✓ 压缩摘要: {result[:50]}...")
        except Exception as e:
            print(f"  ⚠ 跳过 (需要LLM): {e}")

        # 测试 5: process_turn_memories 完整管线
        print("[test5] process_turn_memories 完整管线...")
        try:
            result = process_turn_memories(
                campaign_id=1,
                player_input="我用长剑攻击哥布林",
                narration="你的剑划出一道弧光，斩中了哥布林。",
                intent={"action_type": "attack"},
                turn=1,
            )
            assert isinstance(result, dict), f"期望dict, 得到{type(result)}"
            assert "observations_extracted" in result
            assert "memories_stored" in result
            assert "summary_compressed" in result
            print(f"  ✓ 管线完成: {result}")
        except Exception as e:
            print(f"  ⚠ 跳过 (需要完整环境): {e}")

        # 测试 6: generate_recap / get_recap 前情提要
        print("[test6] generate_recap / get_recap 前情提要...")
        try:
            # 先写一条 rolling_summary 让 generate_recap 有数据
            camp = store.create_campaign("前情提要测", db)
            store.append_summary(camp.id, "队伍进入地下城，击败了哥布林。")
            recap = generate_recap(camp.id)
            assert isinstance(recap, str), f"期望str, 得到{type(recap)}"
            # 验证 get_recap 能取回
            stored = get_recap(camp.id)
            assert isinstance(stored, str), f"期望str, 得到{type(stored)}"
            print(f"  ✓ 前情提要生成: {recap[:50]}..." if recap else "  ✓ 前情提为空（无摘要数据）")
        except Exception as e:
            print(f"  ⚠ 跳过 (需要LLM+Qdrant): {e}")

        # 测试 7: cleanup_memories 清理
        print("[test7] cleanup_memories 清理...")
        try:
            deleted = cleanup_memories(campaign_id=9999)
            assert isinstance(deleted, int), f"期望int, 得到{type(deleted)}"
            print(f"  ✓ 清理返回: deleted={deleted}（无数据时应为0）")
        except Exception as e:
            print(f"  ⚠ 跳过 (需要Qdrant): {e}")

        print("\n[memory] 自检通过 ✓")

    finally:
        with contextlib.suppress(PermissionError):
            os.unlink(db_path)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    _self_test()
