"""房间管理系统 — 多人同桌的房间生命周期。

房主创建战役+设置密码 → 玩家输入房间号+密码+角色信息加入 →
房间状态机 waiting/playing/paused → 房主可踢人/转让/观战。

规则出处:
  - D&D 5E 本身无"房间"概念；本模块为多人在线跑团的协调层。
  - 房间内战斗回合协调见 api/ws.py（基于 engine.combat）。
  - 战利品分配见 brain/loot_distribution.py。

设计:
  - Room 是纯内存 dataclass（进程重启即丢失）；持久化由 stats.store 负责。
  - room_id 全局唯一（短码），映射到 campaign_id。
  - players 列表每项: {ws, character_id, name, is_host, ready}
  - spectators 列表每项: {ws, name}
"""

from __future__ import annotations

import secrets
import string
from dataclasses import dataclass, field
from typing import Optional

from fastapi import WebSocket


# ──────────────────────────────────────────────────────────────────────────
# 房间数据结构
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class Room:
    """一个多人同桌房间。

    属性:
      room_id: 6位短码，全局唯一
      campaign_id: 关联的战役ID
      password: 加入密码（空串=无密码）
      status: waiting(等待玩家) / playing(游戏进行中) / paused(暂停)
      max_players: 最大玩家数（不含观战）
      players: [{ws, character_id, name, is_host, ready}]
      spectators: [{ws, name}]
    """
    room_id: str
    campaign_id: int
    password: str = ""
    status: str = "waiting"          # waiting / playing / paused
    max_players: int = 6
    players: list = field(default_factory=list)
    spectators: list = field(default_factory=list)

    # —— 查询 ——
    def player_count(self) -> int:
        return len(self.players)

    def is_full(self) -> bool:
        return self.player_count() >= self.max_players

    def find_player_by_ws(self, ws: WebSocket) -> Optional[dict]:
        for p in self.players:
            if p["ws"] is ws:
                return p
        return None

    def find_player_by_name(self, name: str) -> Optional[dict]:
        for p in self.players:
            if p["name"] == name:
                return p
        return None

    def find_spectator_by_ws(self, ws: WebSocket) -> Optional[dict]:
        for s in self.spectators:
            if s["ws"] is ws:
                return s
        return None

    def get_host(self) -> Optional[dict]:
        for p in self.players:
            if p["is_host"]:
                return p
        return None

    def all_ready(self) -> bool:
        """所有玩家都已准备就绪（房主默认ready）。"""
        if not self.players:
            return False
        return all(p.get("ready", False) for p in self.players)

    def to_dict(self) -> dict:
        """房间公开状态（不含ws对象、不含密码）。"""
        return {
            "room_id": self.room_id,
            "campaign_id": self.campaign_id,
            "status": self.status,
            "max_players": self.max_players,
            "player_count": self.player_count(),
            "has_password": bool(self.password),
            "players": [{"character_id": p["character_id"], "name": p["name"],
                         "is_host": p["is_host"], "ready": p.get("ready", False)}
                        for p in self.players],
            "spectator_count": len(self.spectators),
        }


# ──────────────────────────────────────────────────────────────────────────
# 房间管理器
# ──────────────────────────────────────────────────────────────────────────

def _gen_room_id(existing: set[str]) -> str:
    """生成6位大写字母数字短码，避免碰撞。"""
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(100):
        code = "".join(secrets.choice(alphabet) for _ in range(6))
        if code not in existing:
            return code
    # 极端情况：加时间戳后缀
    return _gen_room_id(existing) + "X"


class RoomManager:
    """全局房间注册表 + 房间操作。"""

    def __init__(self):
        self.rooms: dict[str, Room] = {}       # room_id -> Room

    # —— 创建 ——
    def create_room(self, campaign_id: int, password: str = "",
                    max_players: int = 6) -> Room:
        """房主创建房间。返回新 Room。

        说明: 调用方应先把房主作为第一个 player 加入。
        """
        room_id = _gen_room_id(set(self.rooms.keys()))
        room = Room(room_id=room_id, campaign_id=campaign_id,
                    password=password, max_players=max_players)
        self.rooms[room_id] = room
        return room

    # —— 加入 ——
    def join_room(self, room_id: str, password: str, name: str,
                  character_id: int, ws: WebSocket) -> dict:
        """玩家加入房间。

        返回: {"ok": True, "room": Room} 或 {"ok": False, "error": str}
        错误: room_not_found / wrong_password / room_full / name_taken
        """
        room = self.rooms.get(room_id)
        if room is None:
            return {"ok": False, "error": "room_not_found"}
        if room.password and room.password != password:
            return {"ok": False, "error": "wrong_password"}
        if room.is_full():
            return {"ok": False, "error": "room_full"}
        if room.find_player_by_name(name):
            return {"ok": False, "error": "name_taken"}
        room.players.append({
            "ws": ws, "character_id": character_id, "name": name,
            "is_host": False, "ready": False,
        })
        return {"ok": True, "room": room}

    def add_host(self, room_id: str, name: str, character_id: int,
                 ws: WebSocket) -> Optional[Room]:
        """把房主作为第一个玩家加入房间。"""
        room = self.rooms.get(room_id)
        if room is None:
            return None
        room.players.append({
            "ws": ws, "character_id": character_id, "name": name,
            "is_host": True, "ready": True,
        })
        return room

    # —— 观战 ——
    def join_as_spectator(self, room_id: str, password: str, name: str,
                          ws: WebSocket) -> dict:
        """以观战者身份加入房间。"""
        room = self.rooms.get(room_id)
        if room is None:
            return {"ok": False, "error": "room_not_found"}
        if room.password and room.password != password:
            return {"ok": False, "error": "wrong_password"}
        room.spectators.append({"ws": ws, "name": name})
        return {"ok": True, "room": room}

    # —— 踢出 ——
    def kick_player(self, room_id: str, target_name: str,
                    requester_ws: WebSocket) -> dict:
        """房主踢出指定玩家。

        返回: {"ok": True, "kicked": name} 或 {"ok": False, "error": str}
        错误: room_not_found / not_host / player_not_found / cannot_kick_host
        """
        room = self.rooms.get(room_id)
        if room is None:
            return {"ok": False, "error": "room_not_found"}
        requester = room.find_player_by_ws(requester_ws)
        if requester is None or not requester["is_host"]:
            return {"ok": False, "error": "not_host"}
        target = room.find_player_by_name(target_name)
        if target is None:
            return {"ok": False, "error": "player_not_found"}
        if target["is_host"]:
            return {"ok": False, "error": "cannot_kick_host"}
        room.players = [p for p in room.players if p["name"] != target_name]
        return {"ok": True, "kicked": target_name, "ws": target["ws"]}

    # —— 转让房主 ——
    def transfer_host(self, room_id: str, target_name: str,
                      requester_ws: WebSocket) -> dict:
        """房主将房主权限转让给另一玩家。"""
        room = self.rooms.get(room_id)
        if room is None:
            return {"ok": False, "error": "room_not_found"}
        requester = room.find_player_by_ws(requester_ws)
        if requester is None or not requester["is_host"]:
            return {"ok": False, "error": "not_host"}
        target = room.find_player_by_name(target_name)
        if target is None:
            return {"ok": False, "error": "player_not_found"}
        requester["is_host"] = False
        target["is_host"] = True
        return {"ok": True, "new_host": target_name}

    # —— 准备状态 ——
    def set_ready(self, room_id: str, ready: bool,
                  requester_ws: WebSocket) -> dict:
        """玩家标记自己准备就绪。"""
        room = self.rooms.get(room_id)
        if room is None:
            return {"ok": False, "error": "room_not_found"}
        p = room.find_player_by_ws(requester_ws)
        if p is None:
            return {"ok": False, "error": "not_in_room"}
        p["ready"] = ready
        return {"ok": True, "all_ready": room.all_ready(),
                "room": room.to_dict()}

    # —— 状态变更 ——
    def set_status(self, room_id: str, status: str,
                   requester_ws: WebSocket) -> dict:
        """房主切换房间状态。"""
        room = self.rooms.get(room_id)
        if room is None:
            return {"ok": False, "error": "room_not_found"}
        requester = room.find_player_by_ws(requester_ws)
        if requester is None or not requester["is_host"]:
            return {"ok": False, "error": "not_host"}
        if status not in ("waiting", "playing", "paused"):
            return {"ok": False, "error": "invalid_status"}
        room.status = status
        return {"ok": True, "status": status}

    # —— 断线处理 ——
    def disconnect(self, room_id: str, ws: WebSocket) -> Optional[dict]:
        """玩家/观战者断线时移除。若房主离开，自动转让给最早加入的玩家。

        返回: {"room": Room, "left": name, "new_host": name|None} 或 None
        """
        room = self.rooms.get(room_id)
        if room is None:
            return None
        left_name = None
        # 移除玩家
        for i, p in enumerate(room.players):
            if p["ws"] is ws:
                left_name = p["name"]
                was_host = p["is_host"]
                room.players.pop(i)
                if was_host and room.players:
                    # 转让给列表中第一个玩家
                    room.players[0]["is_host"] = True
                    return {"room": room, "left": left_name,
                            "new_host": room.players[0]["name"]}
                break
        # 移除观战者
        if left_name is None:
            for i, s in enumerate(room.spectators):
                if s["ws"] is ws:
                    left_name = s["name"]
                    room.spectators.pop(i)
                    break
        # 房间空了 → 清理
        if not room.players and not room.spectators:
            self.rooms.pop(room_id, None)
        return {"room": room, "left": left_name, "new_host": None} if left_name else None

    # —— 查询 ——
    def get_room(self, room_id: str) -> Optional[Room]:
        return self.rooms.get(room_id)

    def list_rooms(self) -> list[dict]:
        return [r.to_dict() for r in self.rooms.values()]

    def broadcast_room(self, room: Room, message: dict,
                       exclude: Optional[WebSocket] = None) -> None:
        """广播给房间内所有玩家+观战者（同步发送，ws.send_text 是 async，
        故本方法应在 async 上下文中 await，或由调用方自行遍历）。

        说明: 实际异步广播在 api/ws.py 中实现；此处保留同步语义占位。
        """
        import json
        text = json.dumps(message, ensure_ascii=False)
        targets = [p["ws"] for p in room.players] + \
                  [s["ws"] for s in room.spectators]
        for ws in targets:
            if ws is exclude:
                continue
            try:
                # ws.send_text 是协程；这里不 await，仅作占位
                pass
            except Exception:
                pass


# ──────────────────────────────────────────────────────────────────────────
# Colyseus 风格 Room 生命周期管理（方案E）
# ──────────────────────────────────────────────────────────────────────────

import asyncio
import time as _time


@dataclass
class PlayerSession:
    """单个玩家的会话信息。

    参考 Colyseus Room 的 client 管理设计：
      - sid: Socket.IO 会话ID
      - character_id: 关联的角色卡ID
      - is_dm: 是否为DM（权限分层）
      - connected: 当前是否在线（断线时设为False，重连恢复True）
      - last_seen: 最后活动时间戳
    """
    sid: str
    character_id: int
    name: str
    is_dm: bool = False
    connected: bool = True
    last_seen: float = field(default_factory=_time.time)

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
      当 players 为空时，调度 30 秒延迟销毁任务

    规则出处:
      - R-CMB-004 回合开始——只有当前回合参战者可以行动
      - D&D 5E 本身无"房间"概念；本模块为多人在线跑团的协调层
    """

    rooms: dict[int, "CampaignRoom"] = {}          # campaign_id → room
    _dispose_tasks: dict[int, asyncio.Task] = {}
    DISPOSE_DELAY: float = 30.0                     # 空房 30 秒后销毁

    def __init__(self, campaign_id: int):
        self.campaign_id = campaign_id
        self.players: dict[str, PlayerSession] = {}   # sid → session
        self.lock = asyncio.Lock()
        self.created_at = _time.time()
        self.last_activity = _time.time()

    # —— 玩家管理 ——
    def add_player(self, sid: str, character_id: int, name: str,
                   is_dm: bool = False) -> PlayerSession:
        """玩家加入房间。

        如果该 sid 已存在，则更新其会话信息（支持重连）。
        """
        ps = PlayerSession(sid=sid, character_id=character_id,
                           name=name, is_dm=is_dm)
        self.players[sid] = ps
        self.last_activity = _time.time()
        # 取消挂起的销毁任务（房间重新有人了）
        task = self._dispose_tasks.pop(self.campaign_id, None)
        if task and not task.done():
            task.cancel()
        return ps

    def remove_player(self, sid: str) -> Optional[PlayerSession]:
        """玩家离开房间。

        返回被移除的 PlayerSession，如果不存在返回 None。
        房间空了则调度延迟销毁。
        """
        ps = self.players.pop(sid, None)
        if ps:
            ps.connected = False
        self.last_activity = _time.time()
        # 如果房间空了，调度延迟销毁
        if not self.players:
            self._schedule_dispose()
        return ps

    def get_player(self, sid: str) -> Optional[PlayerSession]:
        return self.players.get(sid)

    def get_players(self) -> list[dict]:
        """返回房间内所有玩家的公开信息。"""
        return [ps.to_dict() for ps in self.players.values()]

    def find_by_character(self, character_id: int) -> Optional[PlayerSession]:
        """通过角色ID查找玩家会话。"""
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
            from ..stats import store
            from ..engine import combat as cmb
            c = store.load_combat(self.campaign_id)
            if not c.active:
                return True
            cur = cmb.current_combatant(c)
            return cur is not None and cur.cid == str(character_id)
        except Exception:
            return True

    def current_turn_name(self) -> Optional[str]:
        """当前回合是谁（给其他玩家提示'轮到 X'）。"""
        try:
            from ..stats import store
            from ..engine import combat as cmb
            c = store.load_combat(self.campaign_id)
            if not c.active:
                return None
            cur = cmb.current_combatant(c)
            return cur.name if cur else None
        except Exception:
            return None

    # —— 销毁调度 ——
    def _schedule_dispose(self) -> None:
        """30秒后如果房间仍为空，则销毁并清理。

        参考 Colyseus Room 的 autoDispose 机制：
        当最后一个客户端断开时，延迟一段时间后自动销毁房间，
        以便短暂断线的玩家能快速重连恢复。
        """
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
        """获取或创建战役房间。

        幂等操作：同一 campaign_id 多次调用返回同一实例。
        """
        room = cls.rooms.get(campaign_id)
        if room is None:
            room = cls(campaign_id)
            cls.rooms[campaign_id] = room
        return room

    @classmethod
    def get(cls, campaign_id: int) -> Optional["CampaignRoom"]:
        return cls.rooms.get(campaign_id)


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

class _FakeWS:
    """测试用 WebSocket 替身。"""
    _counter = 0
    def __init__(self):
        type(self)._counter += 1
        self.id = type(self)._counter
    def __eq__(self, other):
        return isinstance(other, _FakeWS) and self.id == other.id
    def __hash__(self):
        return hash(self.id)


def _self_test() -> None:
    rm = RoomManager()

    # 创建房间
    room = rm.create_room(campaign_id=1, password="secret", max_players=4)
    assert room.room_id and room.status == "waiting"
    assert room.password == "secret"

    # 房主加入
    host_ws = _FakeWS()
    rm.add_host(room.room_id, "DM", character_id=10, ws=host_ws)
    assert room.player_count() == 1
    assert room.get_host()["name"] == "DM"

    # 玩家加入
    p1_ws = _FakeWS()
    r = rm.join_room(room.room_id, "secret", "Alice", 11, p1_ws)
    assert r["ok"] and r["room"].player_count() == 2

    # 错误密码
    r = rm.join_room(room.room_id, "wrong", "Bob", 12, _FakeWS())
    assert not r["ok"] and r["error"] == "wrong_password"

    # 房间不存在
    r = rm.join_room("XXXXXX", "", "Bob", 12, _FakeWS())
    assert not r["ok"] and r["error"] == "room_not_found"

    # 名字重复
    r = rm.join_room(room.room_id, "secret", "Alice", 11, _FakeWS())
    assert not r["ok"] and r["error"] == "name_taken"

    # 填满房间
    p2_ws = _FakeWS()
    rm.join_room(room.room_id, "secret", "Bob", 12, p2_ws)
    p3_ws = _FakeWS()
    rm.join_room(room.room_id, "secret", "Carol", 13, p3_ws)
    assert room.is_full()
    r = rm.join_room(room.room_id, "secret", "Dave", 14, _FakeWS())
    assert not r["ok"] and r["error"] == "room_full"

    # 准备状态
    assert not room.all_ready()  # Alice/Bob/Carol 未ready
    rm.set_ready(room.room_id, True, p1_ws)
    rm.set_ready(room.room_id, True, p2_ws)
    rm.set_ready(room.room_id, True, p3_ws)
    assert room.all_ready()

    # 踢出玩家（房主操作）
    r = rm.kick_player(room.room_id, "Bob", host_ws)
    assert r["ok"] and r["kicked"] == "Bob"
    assert room.player_count() == 3

    # 非房主不能踢人
    r = rm.kick_player(room.room_id, "Carol", p1_ws)
    assert not r["ok"] and r["error"] == "not_host"

    # 不能踢房主
    r = rm.kick_player(room.room_id, "DM", host_ws)
    assert not r["ok"] and r["error"] == "cannot_kick_host"

    # 转让房主
    r = rm.transfer_host(room.room_id, "Alice", host_ws)
    assert r["ok"] and r["new_host"] == "Alice"
    assert room.get_host()["name"] == "Alice"

    # 状态变更
    r = rm.set_status(room.room_id, "playing", p1_ws)  # Alice现在是房主
    assert r["ok"] and r["status"] == "playing"
    r = rm.set_status(room.room_id, "invalid", p1_ws)
    assert not r["ok"]

    # 观战者加入
    spec_ws = _FakeWS()
    r = rm.join_as_spectator(room.room_id, "secret", "Watcher", spec_ws)
    assert r["ok"] and len(room.spectators) == 1

    # 断线：房主(Alice)离开 → 自动转让
    r = rm.disconnect(room.room_id, p1_ws)
    assert r is not None and r["left"] == "Alice"
    # 剩余玩家: DM, Carol (Bob被踢)
    host_after = room.get_host()
    assert host_after is not None  # 应自动转让

    # 观战者断线
    r = rm.disconnect(room.room_id, spec_ws)
    assert r is not None and r["left"] == "Watcher"
    assert len(room.spectators) == 0

    # to_dict 不含密码和ws
    d = room.to_dict()
    assert "password" not in d
    assert d["has_password"] is True
    assert d["player_count"] == room.player_count()

    # 清空房间后自动清理
    remaining = list(room.players)
    for p in remaining:
        rm.disconnect(room.room_id, p["ws"])
    assert room.room_id not in rm.rooms

    print("[room] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
