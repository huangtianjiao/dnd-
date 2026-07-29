"""World Manager Agent — 地点/时间/天气/NPC状态/任务进度/物品栏管理。

职责:
  - 应用状态变更（HP/法术位/物品）
  - 持久化角色卡和场景
  - 推进战斗回合
  - 触发记忆处理

设计参考: ITMO AI-DM 的 World Engine 角色，
管理环境与游戏状态的持久化。
"""

from __future__ import annotations

import contextlib

from ..brain.state import GameState
from ..engine import combat as cmb
from ..engine import damage
from ..stats import store


def apply(state: GameState) -> dict:
    """World Manager Agent: 应用状态变更 + 持久化。

    流程:
      1. 结构化状态变更 → 玩家角色 HP
      2. 施法消耗法术位 R-SPL-002
      3. 战斗轮次推进 R-CMB-001/004
      4. 持久化日志
      5. 场景推进：更新 Scene.situation
      6. 记忆处理：观察提取 → 长期记忆存储 → 摘要压缩
    """
    cid = state.get("character_id")
    camp = state.get("campaign_id")
    ch = store.get_character(cid) if cid else None

    # 1) 结构化状态变更：玩家角色 HP
    for chg in state.get("state_changes", []):
        if str(chg.get("target")) == str(cid) and chg.get("field") == "hp" and ch:
            delta = int(chg.get("delta", 0))
            if delta < 0:
                nhp, _ = damage.apply_damage_to_hp(ch.hp_current, ch.temp_hp, ch.hp_max, -delta)
                ch.hp_current = nhp
            else:
                ch.hp_current = damage.apply_healing(ch.hp_current, ch.hp_max, delta)

    # 2) 施法消耗法术位 R-SPL-002
    if ch and state.get("dice", {}).get("kind") == "cast":
        lvl = state["dice"].get("spell_level", 1)
        import json as _j
        try:
            sd = _j.loads(ch.spell_slots_json)
        except Exception:
            sd = {}
        if sd.get(str(lvl), 0) > 0:
            sd[str(lvl)] -= 1
        ch.spell_slots_json = _j.dumps(sd)

    if ch:
        store.save_character(ch)

    # 3) 战斗轮次推进 R-CMB-001/004
    if state.get("combat", {}).get("active") and camp:
        try:
            combat = store.load_combat(camp)
            cmb.advance_turn(combat)
            store.save_combat(camp, combat)
        except Exception:
            pass

    # 4) 持久化日志（rolling_summary 不再逐回合追加，由步骤6每10回合压缩）
    if camp:
        store.append_log(camp, player_input=state.get("player_input", ""),
                         dm_output=state.get("narration", ""),
                         dice_rolls=[state.get("dice", {})])

    # 5) 场景推进：更新 Scene.situation（行动后场景叙事）
    scene_update = state.get("scene_update", "")
    if scene_update and camp:
        sc = store.get_scene(camp)
        if sc:
            sc.situation = scene_update
            store.save_scene(sc)

    # 6) 记忆处理：观察提取 → 长期记忆存储 → 摘要压缩
    if camp:
        from ..brain.memory import process_turn_memories
        try:
            turn = store.get_recent_logs(camp, n=1)[0].id if camp else 0
        except Exception:
            turn = 0
        with contextlib.suppress(Exception):
            process_turn_memories(
                campaign_id=camp,
                player_input=state.get("player_input", ""),
                narration=state.get("narration", ""),
                intent=state.get("intent", {}),
                turn=turn,
            )

    return {}
