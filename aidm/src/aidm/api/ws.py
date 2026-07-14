"""WebSocket 实时同桌 — 多人同时在线跑团。

玩家通过 WebSocket 连接同一战役；一人行动，全员实时收到 DM 叙事+骰子+场景更新。
战斗中按先政回合协调（轮到你才能行动）；非战斗时任何人可行动（先到先得）。
graph.run 用 asyncio.Lock 序列化（Qdrant 本地模式非线程安全 + D&D 本来就是回合制）。
"""

from __future__ import annotations

import asyncio
import functools
import json
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect

from ..brain import graph, world
from ..engine import combat as cmb
from ..stats import store, models


class ConnectionManager:
    """管理每个战役的 WebSocket 连接 + 回合协调。"""

    def __init__(self):
        self.campaigns: dict[int, list[dict]] = {}   # campaign_id → [{ws, character_id, name}]
        self.lock = asyncio.Lock()                    # 序列化 graph.run

    async def connect(self, campaign_id: int, character_id: int, name: str,
                      ws: WebSocket) -> dict:
        await ws.accept()
        conn = {"ws": ws, "character_id": character_id, "name": name}
        self.campaigns.setdefault(campaign_id, []).append(conn)
        return conn

    def disconnect(self, campaign_id: int, ws: WebSocket) -> None:
        if campaign_id in self.campaigns:
            self.campaigns[campaign_id] = [
                c for c in self.campaigns[campaign_id] if c["ws"] != ws
            ]

    def get_players(self, campaign_id: int) -> list[dict]:
        return [{"name": c["name"], "character_id": c["character_id"]}
                for c in self.campaigns.get(campaign_id, [])]

    async def broadcast(self, campaign_id: int, message: dict,
                        exclude: Optional[WebSocket] = None) -> None:
        """广播给同战役所有连接（可排除发送者）。"""
        text = json.dumps(message, ensure_ascii=False)
        for conn in self.campaigns.get(campaign_id, []):
            if exclude and conn["ws"] == exclude:
                continue
            try:
                await conn["ws"].send_text(text)
            except Exception:
                pass

    def is_player_turn(self, campaign_id: int, character_id: int) -> bool:
        """战斗中检查是否轮到该角色；非战斗时任何人都能行动。"""
        try:
            c = store.load_combat(campaign_id)
            if not c.active:
                return True
            cur = cmb.current_combatant(c)
            if cur and cur.cid == str(character_id):
                return True
            return False
        except Exception:
            return True

    def current_turn_name(self, campaign_id: int) -> Optional[str]:
        """当前回合是谁（给其他玩家提示'轮到 X'）。"""
        try:
            c = store.load_combat(campaign_id)
            if not c.active:
                return None
            cur = cmb.current_combatant(c)
            return cur.name if cur else None
        except Exception:
            return None

    async def broadcast_state(self, campaign_id: int) -> None:
        """广播更新后的场景 + 战斗 + 回合信息给全员。"""
        # 场景
        scene = world.get_scene(campaign_id)
        if scene:
            await self.broadcast(campaign_id, {"type": "scene_update", "scene": scene})
        # 战斗 + 回合
        turn = self.current_turn_name(campaign_id)
        try:
            c = store.load_combat(campaign_id)
            await self.broadcast(campaign_id, {
                "type": "combat_update",
                "active": c.active, "round": c.round,
                "current_turn": turn,
                "initiative_order": [{"name": x.name, "initiative": x.initiative,
                                      "side": x.side} for x in c.initiative_order],
            })
        except Exception:
            pass


manager = ConnectionManager()


async def websocket_endpoint(ws: WebSocket, campaign_id: int,
                             character_id: int = 0, name: str = "玩家"):
    """WebSocket 端点：玩家连接 → 接收行动 → 跑判定链 → 广播给全员。"""
    conn = await manager.connect(campaign_id, character_id, name, ws)
    # 通知全员：新玩家加入
    players = manager.get_players(campaign_id)
    await manager.broadcast(campaign_id, {"type": "join", "name": name,
                                         "players": players})
    # 给新连接发当前场景
    scene = world.get_scene(campaign_id)
    if scene:
        await ws.send_text(json.dumps({"type": "scene_update", "scene": scene},
                                      ensure_ascii=False))
    # 给新连接发当前回合
    turn = manager.current_turn_name(campaign_id)
    if turn:
        await ws.send_text(json.dumps({"type": "turn", "current": turn},
                                      ensure_ascii=False))

    try:
        while True:
            data = await ws.receive_json()
            if data.get("type") == "action":
                player_input = data.get("player_input", "").strip()
                if not player_input:
                    continue
                # 回合检查
                if not manager.is_player_turn(campaign_id, character_id):
                    await ws.send_text(json.dumps({
                        "type": "error", "message": f"还没轮到你，当前轮到 {manager.current_turn_name(campaign_id)}"
                    }, ensure_ascii=False))
                    continue
                # 通知发送者：处理中
                await ws.send_text(json.dumps({"type": "processing",
                    "player": name}, ensure_ascii=False))
                # 通知其他人：X 正在行动
                await manager.broadcast(campaign_id, {
                    "type": "player_acting", "player": name,
                    "action": player_input,
                }, exclude=ws)
                # 序列化执行 graph.run（Qdrant 本地 + LLM 调用）
                thread_id = f"campaign_{campaign_id}"
                async with manager.lock:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, functools.partial(
                        graph.run, player_input, campaign_id, character_id,
                        thread_id, False))
                # 广播结果给全员
                await manager.broadcast(campaign_id, {
                    "type": "result",
                    "player": name,
                    "narration": result.get("narration", ""),
                    "dice": result.get("dice", {}),
                    "action_options": result.get("action_options", []),
                    "state_changes": result.get("state_changes", []),
                })
                # 广播更新后的场景 + 战斗 + 回合
                await manager.broadcast_state(campaign_id)
                # 给行动者发角色更新（HP 等）
                ch = store.get_character(character_id)
                if ch:
                    await ws.send_text(json.dumps({
                        "type": "character_update",
                        "hp": ch.hp_current, "hp_max": ch.hp_max,
                        "ac": ch.ac, "conditions": ch.conditions_list,
                    }, ensure_ascii=False))

    except WebSocketDisconnect:
        manager.disconnect(campaign_id, ws)
        players = manager.get_players(campaign_id)
        await manager.broadcast(campaign_id, {"type": "leave", "name": name,
                                              "players": players})
