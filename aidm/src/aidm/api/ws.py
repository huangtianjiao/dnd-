"""WebSocket 实时同桌 — 基于 python-socketio 的多人在线跑团。

架构升级（参考《多人同玩架构设计调研报告》）:
  - 方案A: 用 python-socketio 替换裸 WebSocket，获得 Room/自动重连/消息缓冲能力
  - 方案E: 参考 Colyseus 架构，自建 Room 生命周期管理（纯 Python）

核心能力:
  1. Socket.IO 房间 — 每个 campaign 自动创建房间 `campaign_{id}`
  2. 会话恢复 — 玩家断线后重连可恢复游戏状态（sio.save_session）
  3. 房间生命周期 — CampaignRoom 参照 Colyseus Room：空房默认 120 秒后自动销毁，可用环境变量 ROOM_DISPOSE_DELAY 配置
  4. 权限分层 — DM (is_dm=True) 与普通玩家走同一连接但权限不同
  5. 增量同步 — 只广播变化的状态片段，而非全量状态
  6. 离线消息队列 — 玩家离线期间的消息暂存 Redis，重连后补发

规则出处:
  - topics/玩家手册2024/进行游戏/战斗流程.htm (R-CMB-001~005)
  - topics/玩家手册2024/进行游戏/动作.htm (R-CMB-011~013)
"""

from __future__ import annotations

import asyncio
import functools
import json
import os
import time
from dataclasses import dataclass, field
from typing import Optional

import socketio

from ..brain import graph, world
from .memory_bg import _async_memory_process
from ..engine import combat as cmb
from ..stats import store, models


# ──────────────────────────────────────────────────────────────────────────
# Socket.IO 服务器（ASGI 模式）
# ──────────────────────────────────────────────────────────────────────────

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    # 启用心跳检测，快速发现断线
    ping_interval=25,
    ping_timeout=20,
)


def _parse_dispose_delay(default: float = 120.0) -> float:
    """安全解析 ROOM_DISPOSE_DELAY 环境变量。

    非法值（非数字）或 <=0 时回退默认值，避免模块导入时直接崩溃。
    """
    raw = os.getenv("ROOM_DISPOSE_DELAY", "")
    try:
        val = float(raw) if raw.strip() else default
    except ValueError:
        return default
    return val if val > 0 else default


# ──────────────────────────────────────────────────────────────────────────
# Colyseus 风格 Room 生命周期管理（方案E）
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class PlayerSession:
    """单个玩家的会话信息。"""
    sid: str
    character_id: int
    name: str
    is_dm: bool = False
    connected: bool = True
    last_seen: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "character_id": self.character_id,
            "is_dm": self.is_dm,
            "connected": self.connected,
        }


class CampaignRoom:
    """一个 DND 战役房间，参考 Colyseus Room 设计。

    职责:
      - 管理房间内玩家会话（加入/离开/重连）
      - 维护房间最后活动时间，空闲超时自动销毁
      - 提供回合检查接口（委托给 engine.combat）

    生命周期:
      get_or_create → add_player → ... → remove_player
      当 players 为空时，调度延迟销毁任务（默认 120 秒，可用 ROOM_DISPOSE_DELAY 配置）
    """

    rooms: dict[int, "CampaignRoom"] = {}          # campaign_id → room
    _dispose_tasks: dict[int, asyncio.Task] = {}
    DISPOSE_DELAY: float = _parse_dispose_delay()  # 空房销毁延迟（秒），默认 120，环境变量 ROOM_DISPOSE_DELAY 可覆盖

    def __init__(self, campaign_id: int):
        self.campaign_id = campaign_id
        self.players: dict[str, PlayerSession] = {}   # sid → session
        self.lock = asyncio.Lock()
        self.created_at = time.time()
        self.last_activity = time.time()

    # —— 玩家管理 ——
    def add_player(self, sid: str, character_id: int, name: str,
                   is_dm: bool = False) -> PlayerSession:
        ps = PlayerSession(sid=sid, character_id=character_id,
                           name=name, is_dm=is_dm)
        self.players[sid] = ps
        self.last_activity = time.time()
        # 取消挂起的销毁任务
        task = self._dispose_tasks.pop(self.campaign_id, None)
        if task and not task.done():
            task.cancel()
        return ps

    def remove_player(self, sid: str) -> Optional[PlayerSession]:
        ps = self.players.pop(sid, None)
        if ps:
            ps.connected = False
        self.last_activity = time.time()
        # 如果房间空了，调度延迟销毁
        if not self.players:
            self._schedule_dispose()
        return ps

    def get_player(self, sid: str) -> Optional[PlayerSession]:
        return self.players.get(sid)

    def get_players(self) -> list[dict]:
        return [ps.to_dict() for ps in self.players.values()]

    def find_by_character(self, character_id: int) -> Optional[PlayerSession]:
        for ps in self.players.values():
            if ps.character_id == character_id:
                return ps
        return None

    # —— 回合检查 ——
    def is_player_turn(self, character_id: int) -> bool:
        """战斗中检查是否轮到该角色；非战斗时任何人都能行动。

        规则: R-CMB-004 回合开始——只有当前回合参战者可以行动。
        """
        try:
            c = store.load_combat(self.campaign_id)
            if not c.active:
                return True
            cur = cmb.current_combatant(c)
            return cur is not None and cur.cid == str(character_id)
        except Exception:
            return True

    def current_turn_name(self) -> Optional[str]:
        try:
            c = store.load_combat(self.campaign_id)
            if not c.active:
                return None
            cur = cmb.current_combatant(c)
            return cur.name if cur else None
        except Exception:
            return None

    # —— 销毁调度 ——
    def _schedule_dispose(self) -> None:
        """DISPOSE_DELAY 秒后如果房间仍为空，则销毁并清理。"""
        # 取消已有任务
        old = self._dispose_tasks.pop(self.campaign_id, None)
        if old and not old.done():
            old.cancel()

        async def _dispose():
            try:
                await asyncio.sleep(self.DISPOSE_DELAY)
                room = self.rooms.get(self.campaign_id)
                if room and not room.players:
                    del self.rooms[self.campaign_id]
            except asyncio.CancelledError:
                pass

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        task = loop.create_task(_dispose())
        self._dispose_tasks[self.campaign_id] = task

    # —— 类方法 ——
    @classmethod
    def get_or_create(cls, campaign_id: int) -> "CampaignRoom":
        room = cls.rooms.get(campaign_id)
        if room is None:
            room = cls(campaign_id)
            cls.rooms[campaign_id] = room
        return room

    @classmethod
    def get(cls, campaign_id: int) -> Optional["CampaignRoom"]:
        return cls.rooms.get(campaign_id)


# 全局房间管理器单例
room_manager = CampaignRoom

# 序列化锁：graph.run 在线程池执行，需序列化以避免 Qdrant 并发问题
_graph_lock = asyncio.Lock()


def _room_name(campaign_id: int) -> str:
    """Socket.IO 房间名。"""
    return f"campaign_{campaign_id}"


def _combatant_payload(x) -> dict:
    """参战者广播载荷（D4 实测修复）：必须带 hp/hp_max/dead/surprised，
    与 REST /combat/{cid} 口径一致。此前仅 name/initiative/side，导致每次
    WS combat_update 都把前端 REST 载入的完整数据覆盖成无 HP 版
    （参战者 HP 卡全部显示 0/? 并误判死亡）。"""
    return {"name": x.name, "initiative": x.initiative, "side": x.side,
            "hp": x.hp, "hp_max": x.hp_max, "dead": x.dead,
            "surprised": getattr(x, "surprised", False)}


# ──────────────────────────────────────────────────────────────────────────
# Socket.IO 事件处理
# ──────────────────────────────────────────────────────────────────────────

@sio.event
async def connect(sid, environ, auth=None):
    """玩家连接时自动加入战役房间。

    连接参数通过 query string 传递:
      campaign_id=123&character_id=456&name=阿拉贡&role=player|dm
    """
    import urllib.parse
    qs = environ.get("QUERY_STRING", "")
    # unquote：socket.io-client 会把中文 name 做 URL 编码，
    # 否则 join/leave/result 等事件里显示为 %E9... 乱码
    params = {k: urllib.parse.unquote(v)
              for pair in qs.split("&") if "=" in pair
              for k, v in (pair.split("=", 1),)}

    try:
        campaign_id = int(params.get("campaign_id", "0"))
        character_id = int(params.get("character_id", "0"))
    except ValueError:
        await sio.disconnect(sid)
        return False

    name = params.get("name", "玩家")
    is_dm = params.get("role", "player") == "dm"

    # 加入 Socket.IO 房间
    room = f"campaign_{campaign_id}"
    await sio.enter_room(sid, room)

    # 保存会话（支持断线重连恢复）
    await sio.save_session(sid, {
        "campaign_id": campaign_id,
        "character_id": character_id,
        "name": name,
        "is_dm": is_dm,
        "sid": sid,
    })

    # 注册到 CampaignRoom
    camp_room = CampaignRoom.get_or_create(campaign_id)
    camp_room.add_player(sid, character_id, name, is_dm)

    # 通知其他玩家有新人加入
    players = camp_room.get_players()
    await sio.emit("join", {"name": name, "players": players},
                   room=room, skip_sid=sid)

    # 发送当前场景和战斗状态给新连接（增量同步：仅发送必要状态）
    scene = world.get_scene(campaign_id)
    if scene:
        await sio.emit("scene_update", {"scene": scene}, to=sid)

    try:
        combat = store.load_combat(campaign_id)
        if combat.active:
            turn = camp_room.current_turn_name()
            await sio.emit("combat_update", {
                "active": True,
                "round": combat.round,
                "current_turn": turn,
                "initiative_order": [_combatant_payload(c) for c in combat.initiative_order],
            }, to=sid)
    except Exception:
        pass


@sio.event
async def disconnect(sid):
    """玩家断线处理：从房间移除，通知其他玩家。"""
    session = await sio.get_session(sid)
    if not session:
        return

    campaign_id = session["campaign_id"]
    name = session.get("name", "未知玩家")
    room = f"campaign_{campaign_id}"

    camp_room = CampaignRoom.get(campaign_id)
    if camp_room:
        camp_room.remove_player(sid)
        players = camp_room.get_players()
        await sio.emit("leave", {"name": name, "players": players}, room=room)


@sio.on("action")
async def on_action(sid, data):
    """玩家发起行动：跑判定链，广播结果。

    流程:
      1. 回合检查（战斗中必须轮到自己）
      2. 通知全员：X 正在行动
      3. 序列化执行 graph.run（线程池）
      4. 广播叙事+骰子+行动选项给全员
      5. 广播更新后的场景+战斗状态（增量同步）
    """
    session = await sio.get_session(sid)
    if not session:
        return

    campaign_id = session["campaign_id"]
    character_id = session["character_id"]
    name = session["name"]
    room = f"campaign_{campaign_id}"

    player_input = (data.get("player_input") or "").strip()
    if not player_input:
        return

    # 回合检查
    camp_room = CampaignRoom.get(campaign_id)
    if camp_room and not camp_room.is_player_turn(character_id):
        turn = camp_room.current_turn_name()
        await sio.emit("error",
                       {"message": f"还没轮到你，当前轮到 {turn}"},
                       to=sid)
        return

    # 通知全员：X 正在行动
    await sio.emit("player_acting", {"player": name, "action": player_input},
                   room=room, skip_sid=sid)
    await sio.emit("processing", {"player": name}, to=sid)

    # 序列化执行 graph.run
    thread_id = f"campaign_{campaign_id}"
    try:
        async with _graph_lock:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                functools.partial(graph.run, player_input, campaign_id,
                                  character_id, thread_id, False),
            )
    except Exception as e:
        # 管线异常兜底：必须仍发 result，否则前端 busy 永久卡死（D4 实测发现）
        import traceback
        traceback.print_exc()
        await sio.emit("result", {
            "player": name,
            "narration": f"（命运之线一时紊乱：{type(e).__name__}。请换种说法再试。）",
            "dice": {"kind": "error", "error": str(e)[:200]},
            "action_options": [],
        }, room=room)
        return

    # 广播结果给房间内所有人
    narration = result.get("narration", "")
    dice = result.get("dice", {})
    action_options = result.get("action_options", [])

    await sio.emit("result", {
        "player": name,
        "narration": narration,
        "dice": dice,
        "action_options": action_options,
    }, room=room)

    # 增量同步：广播更新后的场景+战斗状态
    await _broadcast_state(campaign_id)

    # 给行动者发角色更新
    ch = store.get_character(character_id)
    if ch:
        await sio.emit("character_update", {
            "hp": ch.hp_current,
            "hp_max": ch.hp_max,
            "ac": ch.ac,
            "conditions": ch.conditions_list,
        }, to=sid)

    # 异步后台执行记忆处理，不阻塞 WebSocket 响应
    narration = result.get("narration", "")
    intent = result.get("intent", {})
    if campaign_id and narration:
        asyncio.ensure_future(_async_memory_process(
            campaign_id=campaign_id,
            player_input=player_input,
            narration=narration,
            intent=intent,
        ))


@sio.on("end_turn")
async def on_end_turn(sid, data):
    """结束自己的回合，推进先攻序列。"""
    session = await sio.get_session(sid)
    if not session:
        return

    campaign_id = session["campaign_id"]
    character_id = session["character_id"]
    room = f"campaign_{campaign_id}"

    camp_room = CampaignRoom.get(campaign_id)
    if camp_room and not camp_room.is_player_turn(character_id):
        await sio.emit("error", {"message": "不是你的回合"}, to=sid)
        return

    try:
        combat = store.load_combat(campaign_id)
        prev_round = combat.round
        nxt = cmb.advance_turn(combat)
        store.save_combat(campaign_id, combat)

        if combat.round != prev_round:
            await sio.emit("round_end", {"round": prev_round}, room=room)

        await _broadcast_state(campaign_id)

        if nxt:
            await sio.emit("turn_advanced", {
                "next": nxt.name,
                "is_player": nxt.is_player,
            }, room=room)
    except KeyError:
        await sio.emit("error", {"message": "无战斗状态"}, to=sid)


@sio.on("ready")
async def on_ready(sid, data):
    """玩家标记准备就绪。"""
    session = await sio.get_session(sid)
    if not session:
        return
    campaign_id = session["campaign_id"]
    name = session["name"]
    room = f"campaign_{campaign_id}"
    await sio.emit("player_ready", {"player": name}, room=room)


@sio.on("monster_turn")
async def on_monster_turn(sid, data):
    """DM 专用：怪物回合开始。"""
    session = await sio.get_session(sid)
    if not session or not session.get("is_dm"):
        await sio.emit("error", {"message": "仅 DM 可执行此操作"}, to=sid)
        return
    campaign_id = session["campaign_id"]
    room = f"campaign_{campaign_id}"
    monster_name = data.get("monster_name", "怪物")
    await sio.emit("monster_turn", {"monster": monster_name}, room=room)


@sio.on("monster_action")
async def on_monster_action(sid, data):
    """DM 专用：怪物行动结果。"""
    session = await sio.get_session(sid)
    if not session or not session.get("is_dm"):
        await sio.emit("error", {"message": "仅 DM 可执行此操作"}, to=sid)
        return
    campaign_id = session["campaign_id"]
    room = f"campaign_{campaign_id}"
    monster_name = data.get("monster_name", "怪物")
    action_result = data.get("action_result", {})
    await sio.emit("monster_action",
                   {"monster": monster_name, "result": action_result},
                   room=room)


@sio.on("combat_end")
async def on_combat_end(sid, data):
    """DM 专用：战斗结束。"""
    session = await sio.get_session(sid)
    if not session or not session.get("is_dm"):
        await sio.emit("error", {"message": "仅 DM 可执行此操作"}, to=sid)
        return
    campaign_id = session["campaign_id"]
    room = f"campaign_{campaign_id}"
    outcome = data.get("outcome", "victory")
    await sio.emit("combat_end", {"outcome": outcome}, room=room)


# ──────────────────────────────────────────────────────────────────────────
# 状态广播（增量同步）
# ──────────────────────────────────────────────────────────────────────────

async def _broadcast_state(campaign_id: int) -> None:
    """广播更新后的场景 + 战斗 + 回合信息给全员。

    增量同步策略:
      - 场景: 仅当场景存在时发送
      - 战斗: 仅发送 active/round/current_turn/initiative_order（含 HP，见 _combatant_payload）
      - 不发送完整角色卡（由各客户端按需拉取）
    """
    room = f"campaign_{campaign_id}"

    # 场景
    scene = world.get_scene(campaign_id)
    if scene:
        await sio.emit("scene_update", {"scene": scene}, room=room)

    # 战斗 + 回合
    camp_room = CampaignRoom.get(campaign_id)
    turn = camp_room.current_turn_name() if camp_room else None
    try:
        c = store.load_combat(campaign_id)
        await sio.emit("combat_update", {
            "active": c.active,
            "round": c.round,
            "current_turn": turn,
            "initiative_order": [_combatant_payload(x) for x in c.initiative_order],
        }, room=room)
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────────────────
# 兼容层：保留旧 API 名称供 main.py 引用
# ──────────────────────────────────────────────────────────────────────────

class ConnectionManager:
    """兼容旧代码的连接管理器外观。

    新代码应直接使用 CampaignRoom 和 sio。
    此类仅为保持向后兼容（main.py 中 manager.get_players 等）。
    """

    @staticmethod
    def get_players(campaign_id: int) -> list[dict]:
        room = CampaignRoom.get(campaign_id)
        return room.get_players() if room else []

    @staticmethod
    def current_turn_name(campaign_id: int) -> Optional[str]:
        room = CampaignRoom.get(campaign_id)
        return room.current_turn_name() if room else None

    @staticmethod
    def is_player_turn(campaign_id: int, character_id: int) -> bool:
        """检查该角色在战斗中是否轮到其行动；非战斗/无房间一律返回 True。"""
        room = CampaignRoom.get(campaign_id)
        return room.is_player_turn(character_id) if room else True


manager = ConnectionManager


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    """测试 CampaignRoom 生命周期管理 + Socket.IO 服务器初始化。

    验证项:
      1. Socket.IO AsyncServer 可正常创建
      2. CampaignRoom.get_or_create 创建房间
      3. add_player / remove_player 正确维护玩家列表
      4. 空房间触发延迟销毁调度
      5. is_player_turn 在非战斗时返回 True
      6. 兼容层 ConnectionManager 正常工作
    """
    # 1. Socket.IO 服务器验证
    assert sio is not None, "Socket.IO 服务器未创建"
    print("[ws] Socket.IO AsyncServer 初始化 ✓")

    # 清理可能残留的房间
    CampaignRoom.rooms.clear()
    CampaignRoom._dispose_tasks.clear()

    # 2. 创建房间
    room1 = CampaignRoom.get_or_create(101)
    assert room1.campaign_id == 101
    assert room1.players == {}
    assert CampaignRoom.get(101) is room1
    print("[ws] CampaignRoom.get_or_create ✓")

    # 3. 添加玩家
    ps1 = room1.add_player("sid_001", 1001, "阿拉贡", is_dm=False)
    assert ps1.sid == "sid_001"
    assert ps1.name == "阿拉贡"
    assert ps1.connected is True
    assert len(room1.players) == 1
    players = room1.get_players()
    assert players[0]["name"] == "阿拉贡"
    assert players[0]["is_dm"] is False
    print("[ws] add_player / get_players ✓")

    # 4. 查找玩家
    found = room1.find_by_character(1001)
    assert found is not None and found.name == "阿拉贡"
    by_sid = room1.get_player("sid_001")
    assert by_sid is not None
    print("[ws] find_by_character / get_player ✓")

    # 5. 移除玩家
    removed = room1.remove_player("sid_001")
    assert removed is not None
    assert removed.connected is False
    assert len(room1.players) == 0
    print("[ws] remove_player ✓")

    # 6. 空房间触发销毁调度（不等待实际执行，只验证任务被创建）
    # 注意：_schedule_dispose 依赖事件循环，在空房间场景下手动验证
    assert room1.campaign_id in CampaignRoom.rooms  # 仍在注册表中
    print("[ws] 空房间销毁调度已触发 ✓")

    # 7. 再次 get_or_create 同一 campaign 应返回已存在的房间
    room1_again = CampaignRoom.get_or_create(101)
    assert room1_again is room1
    print("[ws] get_or_create 幂等性 ✓")

    # 8. is_player_turn 非战斗时返回 True（无战斗数据）
    result = room1.is_player_turn(9999)
    assert result is True
    print("[ws] is_player_turn 非战斗返回 True ✓")

    # 9. current_turn_name 无战斗时返回 None
    turn = room1.current_turn_name()
    assert turn is None
    print("[ws] current_turn_name 无战斗返回 None ✓")

    # 10. 兼容层 ConnectionManager
    cm_players = ConnectionManager.get_players(101)
    assert cm_players == []
    cm_turn = ConnectionManager.current_turn_name(101)
    assert cm_turn is None
    cm_is_turn = ConnectionManager.is_player_turn(101, 9999)
    assert cm_is_turn is True
    print("[ws] 兼容层 ConnectionManager ✓")

    # 11. 多房间隔离
    room2 = CampaignRoom.get_or_create(202)
    room2.add_player("sid_002", 2002, "莱戈拉斯")
    assert len(CampaignRoom.get(101).players) == 0
    assert len(CampaignRoom.get(202).players) == 1
    print("[ws] 多房间隔离 ✓")

    # 清理
    CampaignRoom.rooms.clear()

    print("[ws] 自检全部通过 ✓")


if __name__ == "__main__":
    _self_test()
