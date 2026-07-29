"""NPC 人格持久化 — 独立记忆流 + 关系演化追踪。

职责:
  - 每个 NPC 维护独立的人格档案（背景/性格/知识范围/目标/秘密）
  - NPC 记忆流：存储与玩家的交互历史
  - PC-NPC 关系追踪：信任等级随时间推移变化
  - 语义检索 NPC 记忆（"上次见面鲍勃提到了什么？"）

设计参考: Generative Agents (Stanford) 的记忆流架构 +
调研报告 §1.3 角色模拟要求。
"""

from __future__ import annotations

import json
from datetime import datetime

from sqlmodel import Field, SQLModel, select

from . import store

# ──────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────

class NPCProfile(SQLModel, table=True):
    """NPC 人格档案 — 持久化的角色身份。

    每个 NPC 有独立的人格、知识范围和秘密。
    与 NPCMemory 表配合实现记忆流。
    """
    id: int | None = Field(default=None, primary_key=True)
    campaign_id: int | None = Field(default=None, foreign_key="campaign.id")
    name: str                                    # NPC 名称
    role: str = ""                               # 职业身份
    description: str = ""                        # 外貌描述
    personality: str = ""                        # 性格特征
    background: str = ""                         # 背景故事
    goals_json: str = Field(default="[]")        # NPC 自身目标
    knowledge_json: str = Field(default="[]")    # NPC 所知信息
    secrets_json: str = Field(default="[]")      # NPC 隐藏秘密
    # 关系状态
    trust_level: int = 0                         # 信任等级 (-100 到 100)
    relationship_status: str = "neutral"         # neutral/friendly/hostile
    # 元数据
    first_met_turn: int = 0                      # 首次相遇回合
    interaction_count: int = 0                   # 互动次数
    last_interaction_turn: int = 0               # 最后互动回合

    @property
    def goals(self) -> list[str]:
        return json.loads(self.goals_json)

    def set_goals(self, goals: list[str]) -> None:
        self.goals_json = json.dumps(goals)

    @property
    def knowledge(self) -> list[str]:
        return json.loads(self.knowledge_json)

    def set_knowledge(self, knowledge: list[str]) -> None:
        self.knowledge_json = json.dumps(knowledge)

    @property
    def secrets(self) -> list[str]:
        return json.loads(self.secrets_json)

    def set_secrets(self, secrets: list[str]) -> None:
        self.secrets_json = json.dumps(secrets)


class NPCMemory(SQLModel, table=True):
    """NPC 记忆流 — 单条交互记忆。

    参考 Generative Agents 的 memory stream：
    每条记忆有 importance(1-10)、timestamp、embedding。
    """
    id: int | None = Field(default=None, primary_key=True)
    npc_profile_id: int | None = Field(default=None, foreign_key="npcprofile.id")
    event: str                                   # 记忆内容描述
    importance: int = 5                          # 重要性 (1-10)
    turn: int = 0                                # 发生回合
    timestamp: str = ""                          # 创建时间
    # 记忆类型
    memory_type: str = "interaction"             # interaction/secret_revealed/attitude_change


# ──────────────────────────────────────────────────────────────────────────
# CRUD 操作
# ──────────────────────────────────────────────────────────────────────────

def create_npc(campaign_id: int, name: str, role: str = "",
               personality: str = "", background: str = "",
               goals: list[str] = None, knowledge: list[str] = None,
               secrets: list[str] = None) -> NPCProfile:
    """创建新的 NPC 人格档案。"""
    npc = NPCProfile(
        campaign_id=campaign_id, name=name, role=role,
        personality=personality, background=background,
    )
    if goals:
        npc.set_goals(goals)
    if knowledge:
        npc.set_knowledge(knowledge)
    if secrets:
        npc.set_secrets(secrets)

    with store.session() as s:
        s.add(npc)
        s.commit()
        s.refresh(npc)
        return npc


def get_npc(npc_id: int) -> NPCProfile | None:
    """获取 NPC 档案。"""
    with store.session() as s:
        return s.get(NPCProfile, npc_id)


def find_npc_by_name(campaign_id: int, name: str) -> NPCProfile | None:
    """按名称查找 NPC。"""
    with store.session() as s:
        stmt = (select(NPCProfile)
                .where(NPCProfile.campaign_id == campaign_id)
                .where(NPCProfile.name == name))
        return s.exec(stmt).first()


def list_npcs(campaign_id: int) -> list[NPCProfile]:
    """列出战役中的所有 NPC。"""
    with store.session() as s:
        stmt = select(NPCProfile).where(NPCProfile.campaign_id == campaign_id)
        return list(s.exec(stmt))


def update_npc(npc: NPCProfile) -> NPCProfile:
    """更新 NPC 档案。"""
    with store.session() as s:
        s.add(npc)
        s.commit()
        s.refresh(npc)
        return npc


def delete_npc(npc_id: int) -> bool:
    """删除 NPC 及其所有记忆。"""
    with store.session() as s:
        # 先删除关联的记忆
        stmt = select(NPCMemory).where(NPCMemory.npc_profile_id == npc_id)
        memories = s.exec(stmt).all()
        for mem in memories:
            s.delete(mem)

        # 再删除 NPC 档案
        npc = s.get(NPCProfile, npc_id)
        if npc:
            s.delete(npc)
            s.commit()
            return True
        return False


# ──────────────────────────────────────────────────────────────────────────
# NPC 记忆流操作
# ──────────────────────────────────────────────────────────────────────────

def add_memory(npc_profile_id: int, event: str,
               importance: int = 5, turn: int = 0,
               memory_type: str = "interaction") -> NPCMemory:
    """向 NPC 记忆流添加一条记忆。"""
    memory = NPCMemory(
        npc_profile_id=npc_profile_id,
        event=event,
        importance=max(1, min(10, importance)),
        turn=turn,
        timestamp=datetime.now().isoformat(),
        memory_type=memory_type,
    )

    with store.session() as s:
        s.add(memory)
        s.commit()
        s.refresh(memory)
        return memory


def get_memories(npc_profile_id: int, limit: int = 20) -> list[NPCMemory]:
    """获取 NPC 的记忆流（按时间倒序）。"""
    with store.session() as s:
        stmt = (select(NPCMemory)
                .where(NPCMemory.npc_profile_id == npc_profile_id)
                .order_by(NPCMemory.turn.desc())
                .limit(limit))
        return list(s.exec(stmt))


def retrieve_npc_memories(npc_profile_id: int, query: str,
                          top_k: int = 5) -> list[NPCMemory]:
    """检索 NPC 相关记忆（简化版：按重要性排序）。

    完整版应使用向量嵌入进行语义检索，
    这里先用重要性+时间排序的简化方案。
    """
    with store.session() as s:
        stmt = (select(NPCMemory)
                .where(NPCMemory.npc_profile_id == npc_profile_id)
                .order_by(NPCMemory.importance.desc(),
                          NPCMemory.turn.desc())
                .limit(top_k * 2))  # 多取一些做筛选
        all_memories = list(s.exec(stmt))

        # 简单关键词匹配
        query_lower = query.lower()
        scored = []
        for mem in all_memories:
            score = mem.importance
            if query_lower in mem.event.lower():
                score += 5  # 关键词匹配加分
            scored.append((score, mem))

        # 按分数降序，取 top_k
        scored.sort(key=lambda x: x[0], reverse=True)
        return [mem for _, mem in scored[:top_k]]


# ──────────────────────────────────────────────────────────────────────────
# 关系演化追踪
# ──────────────────────────────────────────────────────────────────────────

# 信任等级阈值
TRUST_HOSTILE = -30       # < -30 → 敌对
TRUST_NEUTRAL = 0         # -30 ~ 30 → 中立
TRUST_FRIENDLY = 30       # > 30 → 友好
# 信任变化量
TRUST_GAIN_SUCCESS = 5    # 成功互动 +5
TRUST_LOSS_FAILURE = 3    # 失败互动 -3
TRUST_LOSS_BETRAYAL = 50  # 背叛 -50


def update_trust(npc: NPCProfile, delta: int) -> NPCProfile:
    """更新 NPC 对玩家的信任等级。

    自动更新 relationship_status:
      trust < -30 → hostile
      -30 <= trust < 30 → neutral
      trust >= 30 → friendly

    Args:
        npc: NPC 档案对象
        delta: 信任变化量（正数增加，负数减少）

    Returns:
        更新后的 NPC 档案
    """
    npc.trust_level = max(-100, min(100, npc.trust_level + delta))

    # 更新关系状态
    if npc.trust_level < TRUST_HOSTILE:
        npc.relationship_status = "hostile"
    elif npc.trust_level >= TRUST_FRIENDLY:
        npc.relationship_status = "friendly"
    else:
        npc.relationship_status = "neutral"

    return update_npc(npc)


def record_interaction(npc: NPCProfile, event: str,
                       success: bool, turn: int,
                       importance: int = 5) -> NPCProfile:
    """记录一次 NPC 互动并更新关系。

    Args:
        npc: NPC 档案对象
        event: 互动事件描述
        success: 互动是否成功
        turn: 当前回合
        importance: 事件重要性 (1-10)

    Returns:
        更新后的 NPC 档案
    """
    # 添加记忆
    add_memory(npc.id, event, importance=importance,
               turn=turn, memory_type="interaction")

    # 更新信任
    npc = update_trust(npc, TRUST_GAIN_SUCCESS) if success else update_trust(npc, -TRUST_LOSS_FAILURE)

    # 更新互动计数
    npc.interaction_count += 1
    npc.last_interaction_turn = turn

    return update_npc(npc)


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    """npc.py 自检测试。使用 DEFAULT_DB。"""
    # 创建临时战役
    camp = store.create_campaign("NPC测试")

    # 测试 1: 创建 NPC
    print("[test1] create_npc...")
    npc = create_npc(
        campaign_id=camp.id,
        name="酒馆老板鲍勃",
        role="酒馆老板",
        personality="热情健谈，喜欢八卦",
        background="退伍军人，经营酒馆已有二十年",
        goals=["维持生意", "打听消息"],
        knowledge=["镇上有奇怪的地下活动", "镇长最近很焦虑"],
        secrets=["曾是盗贼公会的成员"],
    )
    assert npc.id is not None
    assert npc.name == "酒馆老板鲍勃"
    assert len(npc.goals) == 2
    assert len(npc.secrets) == 1
    print(f"  ✓ 创建成功: {npc.name} (id={npc.id})")

    # 测试 2: 查找 NPC
    print("[test2] find_npc_by_name...")
    found = find_npc_by_name(camp.id, "酒馆老板鲍勃")
    assert found is not None
    assert found.id == npc.id
    print(f"  ✓ 查找成功: {found.name}")

    # 测试 3: 添加记忆
    print("[test3] add_memory...")
    mem1 = add_memory(npc.id, "玩家第一次进入酒馆", importance=4, turn=1)
    mem2 = add_memory(npc.id, "玩家询问了地下活动", importance=7, turn=2)
    mem3 = add_memory(npc.id, "玩家威胁鲍勃交出信息", importance=8, turn=3)
    assert mem1.id is not None
    assert mem2.importance == 7
    print("  ✓ 添加3条记忆成功")

    # 测试 4: 获取记忆流
    print("[test4] get_memories...")
    memories = get_memories(npc.id, limit=10)
    assert len(memories) == 3
    print(f"  ✓ 获取 {len(memories)} 条记忆")

    # 测试 5: 检索相关记忆
    print("[test5] retrieve_npc_memories...")
    results = retrieve_npc_memories(npc.id, "地下活动", top_k=3)
    assert len(results) > 0
    print(f"  ✓ 检索到 {len(results)} 条相关记忆")

    # 测试 6: 更新信任等级
    print("[test6] update_trust...")
    original_trust = npc.trust_level  # 初始为 0
    npc = update_trust(npc, 15)       # 0 + 15 = 15
    assert npc.trust_level == 15, f"期望15, 得到{npc.trust_level}"
    # 15 < 30 (TRUST_FRIENDLY)，所以是 neutral
    assert npc.relationship_status == "neutral", \
        f"期望neutral, 得到{npc.relationship_status}"
    print(f"  ✓ 信任更新: {npc.trust_level}, 关系: {npc.relationship_status}")

    # 测试 7: 记录互动
    print("[test7] record_interaction...")
    npc = record_interaction(npc, "玩家成功说服鲍勃提供线索",
                             success=True, turn=4, importance=7)
    assert npc.interaction_count == 1
    assert npc.last_interaction_turn == 4
    print(f"  ✓ 互动记录: interactions={npc.interaction_count}, "
          f"trust={npc.trust_level}")

    # 测试 8: 列出 NPC
    print("[test8] list_npcs...")
    npc_list = list_npcs(camp.id)
    assert len(npc_list) == 1
    print(f"  ✓ 列出 {len(npc_list)} 个 NPC")

    # 测试 9: 删除 NPC
    print("[test9] delete_npc...")
    deleted = delete_npc(npc.id)
    assert deleted is True
    npc_list = list_npcs(camp.id)
    assert len(npc_list) == 0
    print("  ✓ 删除成功")

    print("\n[npc] 自检通过 ✓")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    _self_test()
