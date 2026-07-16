"""P3 编排状态 — GameState（贯穿 LangGraph 图节点的状态对象）。

设计原则（ARCHITECTURE §4）：LLM 只在 classify(意图) 与 narrate(叙事) 两端活动，
中间 retrieve→verify→resolve(骰子) 全代码。GameState 承载每轮流转的数据。
v2: 扩展 cast/ability_check/explore/start_combat 意图 + combat 跟踪 + hitl。
"""

from __future__ import annotations

from typing import TypedDict


class GameState(TypedDict):
    """一轮玩家输入经判定链流转的状态。"""
    # 输入
    player_input: str
    campaign_id: int
    character_id: int
    hitl: bool                 # 是否启用 HITL（关键判定暂停让 DM 确认）
    # 各节点产物
    intent: dict               # classify 产物: {action_type, weapon, target_name, target_ac, ability, retrieval_query, ...}
    evidence: list             # retrieve 产物: 检索到的规则点
    verification: dict         # verify 产物: {ok, issues}
    confirmed: bool            # HITL confirm 产物: DM 确认结果
    dice: dict                 # resolve 产物(硬性): {hit, crit, attack_total, damage, ...} 或 {save_dc, save_success, damage} 或 {check_total, success}
    narration: str             # narrate 产物: DM 叙事
    state_changes: list        # narrate 产物: 结构化状态变更
    scene_update: str          # narrate 产物: 行动后场景新状态叙事（apply_node 据此更新 Scene.situation）
    action_options: list       # narrate 产物: 玩家下一步可做的3个行动选项（透传给前端）
    combat: dict               # 战斗状态: {active, combat_id, round, current_index, combatants}
    # 元
    error: str
    summary: str               # rolling summary（防上下文失忆）
