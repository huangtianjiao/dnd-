"""Narrator Agent — 场景描述、NPC对话、剧情推进、氛围渲染。

职责:
  - 基于骰子结果（固定不可改）生成叙事
  - 输出结构化状态变更 + 场景更新
  - 给出3个玩家下一步行动选项

设计参考: ITMO AI-DM 的 Dungeon Master 角色，
负责将确定性引擎的结构化结果"翻译"成叙事。
"""

from __future__ import annotations

import contextlib
import json
import re

import logging

from ..brain import llm, world
from ..brain.state import GameState
from ..stats import store

_log = logging.getLogger(__name__)


def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?|```", "", text, flags=re.I)
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        try:
            return json.loads(m.group(0) + "}")
        except Exception:
            return {}


def _digest(evidence: list[dict], n: int = 4, body: int = 320) -> str:
    return "\n---\n".join(f"[{e.get('tag')}] {e.get('body','')[:body]}" for e in evidence[:n])


_NARRATOR_SYSTEM = "你是D&D DM,严格依据掷骰结果叙述,不改动数值。只输出JSON。"

_NARRATOR_PROMPT = """\
你是D&D 5E DM。依据【掷骰结果(硬性,已由代码算出,不可更改)】与规则,在当前场景中以第二人称简洁叙述(2-4句)。
遵循叙事技巧:简洁、多感官氛围、区分选项、不臆测角色行动。

重要: 你只负责叙事描述,不能修改任何游戏状态(HP/AC/条件等)。所有数值已由代码计算完毕。

前情提要:
{recap_text}

本局摘要:
{summary_text}

近期对话(工作记忆):
{history}

{long_term_ctx}

掷骰结果: {dice}
战斗: {combat}
{scene_ctx}
规则摘要:
{dig}
玩家输入: {player_input}
然后输出场景叙事。只输出JSON:
{{"narration":"叙事","scene_update":"","action_options":["选项1","选项2","选项3"]}}
"""


def narrate(state: GameState) -> dict:
    """Narrator Agent: LLM 叙事 + 结构化状态变更。

    注入四层记忆到 prompt:
      ① 工作记忆 — 最近6回合对话原文 (store.get_recent_logs)
      ② 中期记忆 — Campaign.rolling_summary 摘要 (store.get_summary)
      ③ 长期记忆 — 跨Session语义检索 (brain.memory.retrieve_memories)
      ④ 前情提要 — Session间浓缩摘要 (brain.memory.get_recap)
    """
    dice = state.get("dice", {})
    dig = _digest(state.get("evidence", []))
    combat_ctx = state.get("combat", {})
    camp_id = state.get("campaign_id", 0)
    scene_ctx = world.scene_context(camp_id)

    # ① 工作记忆：最近6回合对话（时间正序）
    recent_logs = store.get_recent_logs(camp_id, n=6) if camp_id else []
    history = "\n".join(
        f"[回合] 玩家: {log.player_input[:80]} → DM: {log.dm_output[:80]}"
        for log in recent_logs
    ) if recent_logs else "(无历史对话)"

    # ② 中期记忆：rolling_summary（截取前500字防止prompt过长）
    rolling_summary = store.get_summary(camp_id) if camp_id else ""
    summary_text = rolling_summary[:500] if rolling_summary else "(无摘要)"

    # ③ 长期记忆：跨Session语义检索（top-5，重要性加权+时间衰减）
    long_term_ctx = ""
    if camp_id:
        from ..brain.memory import retrieve_memories
        try:
            query = state.get("player_input", "")[:100]
            memories = retrieve_memories(camp_id, query, top_k=20)
            if memories:
                long_term_ctx = "相关记忆(长期):\n" + "\n".join(
                    f"- {m['event']} [重要:{m['importance']}]"
                    for m in memories
                )
        except Exception:
            pass

    # ④ 前情提要：跨Session浓缩摘要
    recap_text = ""
    if camp_id:
        from ..brain.memory import get_recap
        with contextlib.suppress(Exception):
            recap_text = get_recap(camp_id)

    prompt = _NARRATOR_PROMPT.format(
        recap_text=recap_text or "(无前情提要)",
        summary_text=summary_text,
        history=history,
        long_term_ctx=long_term_ctx or "",
        dice=json.dumps(dice, ensure_ascii=False),
        combat=json.dumps(combat_ctx, ensure_ascii=False),
        scene_ctx=scene_ctx,
        dig=dig,
        player_input=state["player_input"],
    )

    raw = llm.chat(_NARRATOR_SYSTEM, prompt, temperature=0.4)
    obj = _extract_json(raw)
    # ARC-004: Narrator 只读——剥离 state_changes，LLM 不应修改游戏状态
    if obj.get("state_changes"):
        _log.warning("ARC-004: Narrator 返回 state_changes 已被丢弃 (len=%d)",
                     len(obj["state_changes"]))
    return {
        "narration": obj.get("narration", raw[:200]),
        "state_changes": [],  # ARC-004: 始终返回空列表，Narrator 不能修改状态
        "scene_update": obj.get("scene_update", ""),
        "action_options": obj.get("action_options", []),
    }
