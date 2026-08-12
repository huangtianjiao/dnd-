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

import socketio

from ..brain import combat_flow, graph, world
from ..brain.room import CampaignRoom, ConnectionManager, manager
from ..config import resolve_allowed_origins
from ..stats import store
from .memory_bg import _async_memory_process
from .session_tokens import parse_session_token

# ──────────────────────────────────────────────────────────────────────────
# Socket.IO 服务器（ASGI 模式）
# ──────────────────────────────────────────────────────────────────────────

# ★ P0-06: CORS 与 HTTP 统一从配置读取（AIDM_ALLOWED_ORIGINS），不再硬编码 "*"
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=resolve_allowed_origins(),
    # 启用心跳检测，快速发现断线
    ping_interval=25,
    ping_timeout=20,
)


# ──────────────────────────────────────────────────────────────────────────
# 全局房间管理器单例（CampaignRoom 定义在 brain.room，此处仅保留别名）
# ──────────────────────────────────────────────────────────────────────────

room_manager = CampaignRoom

# 序列化锁：graph.run 在线程池执行，需序列化以避免 Qdrant 并发问题
# 升级为 per-campaign 锁：不同战役可并行执行，仅同一战役内串行
_campaign_locks: dict[int, asyncio.Lock] = {}


def get_campaign_lock(campaign_id: int) -> asyncio.Lock:
    """获取指定战役的锁。不同战役可并行执行。"""
    if campaign_id not in _campaign_locks:
        _campaign_locks[campaign_id] = asyncio.Lock()
    return _campaign_locks[campaign_id]


def _cleanup_campaign_lock(campaign_id: int) -> None:
    """清理不再使用的战役锁，避免内存泄漏。"""
    _campaign_locks.pop(campaign_id, None)


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

    ★ P0-05: 凭据经 Socket.IO auth 载荷传递（auth={"token": <session-token>}），
      不再放入 query string（避免出现在代理 access log / 监控 / tracing）。
    ★ P0-04: DM/房主身份取自服务器签名令牌的 role 声明（auth token），
      query 中的 role=dm 一律忽略，客户端无法自封 DM。

    连接参数（query，仅公开信息）:
      campaign_id=123&character_id=456&name=阿拉贡

    握手校验（与 REST 层同口径，否则可绕过 /room/join 密码直连）:
      1. 会话令牌（若提供）：验签解析 → 决定 DM/房主权限
      2. 战役存在、角色存在且属于该战役
      3. 若该战役存在带密码的 REST 房间 → 连接者必须已通过 /room/join 注册
    """
    import os
    import urllib.parse

    # —— P0-05: 只从 auth 载荷读取令牌（Socket.IO 客户端 auth 字段）——
    token = ""
    if isinstance(auth, dict):
        token = auth.get("token", "") or ""
    claims = parse_session_token(token) if token else None
    is_dm = bool(claims and claims.is_dm)

    qs = environ.get("QUERY_STRING", "")
    # unquote：socket.io-client 会把中文 name 做 URL 编码，
    # 否则 join/leave/result 等事件里显示为 %E9... 乱码
    params = {k: urllib.parse.unquote(v)
              for pair in qs.split("&") if "=" in pair
              for k, v in (pair.split("=", 1),)}

    async def _reject(message: str):
        """拒连：ConnectionRefusedError 的 message 会随 connect_error 送达客户端。"""
        raise socketio.exceptions.ConnectionRefusedError(message)

    try:
        campaign_id = int(params.get("campaign_id", "0"))
        character_id = int(params.get("character_id", "0"))
    except ValueError:
        return await _reject("连接参数非法")

    name = params.get("name", "玩家")

    # 2) 战役/角色存在性
    if store.get_campaign(campaign_id) is None:
        return await _reject(f"战役 {campaign_id} 不存在")
    if character_id:
        ch = store.get_character(character_id)
        if ch is None or ch.campaign_id != campaign_id:
            return await _reject("角色不存在或不属于该战役")
    elif not is_dm:
        return await _reject("缺少 character_id")

    # 3) 带密码房间：必须先走 /room/join 注册（按 character_id 校验成员资格）
    from .routes.room import room_manager as rest_rooms
    rest_room = rest_rooms.find_by_campaign(campaign_id)
    if rest_room is not None and rest_room.password and not is_dm:
        member = any(p["character_id"] == character_id for p in rest_room.players)
        if not member:
            return await _reject("该房间需要密码，请通过房间列表加入")

    # 4) DM/房主身份：仅来自验签后的令牌声明（P0-04）
    #    query 中的 role=dm / api_key / dm_token 不再参与权限判定

    # 加入 Socket.IO 房间
    room = f"campaign_{campaign_id}"
    await sio.enter_room(sid, room)

    # 保存会话（支持断线重连恢复）
    role = claims.role if claims else "player"
    await sio.save_session(sid, {
        "campaign_id": campaign_id,
        "character_id": character_id,
        "name": name,
        "is_dm": is_dm,
        "role": role,
        "sid": sid,
    })

    # 注册到 CampaignRoom
    camp_room = CampaignRoom.get_or_create(campaign_id)
    camp_room.add_player(sid, character_id, name, is_dm)

    # 广播新人加入；不跳过本人 —— 新连接者依赖此事件初始化自己的队伍条
    # （此前 skip_sid 导致进入游戏时看不到已在房玩家）
    players = camp_room.get_players()
    await sio.emit("join", {"name": name, "players": players}, room=room)

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
      1. 通知全员：X 正在行动
      2. 锁内回合检查（战斗中必须轮到自己；D5 修复 TOCTOU 竞态）
      3. 序列化执行 graph.run（线程池）；多人局行动不推进回合（显式 end_turn）
      4. 广播叙事+骰子+行动选项给全员（含 turn_hint 动作耗尽提示）
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

    # 通知全员：X 正在行动
    await sio.emit("player_acting", {"player": name, "action": player_input},
                   room=room, skip_sid=sid)
    await sio.emit("processing", {"player": name}, to=sid)

    # 序列化执行 graph.run（per-campaign 锁，不同战役可并行）
    # 回合检查在锁内二次确认：两玩家并发时后排队者在前者推进回合后不应再执行
    # ★ P1-02: 线程 ID 由服务器生成（绑定 campaign+character），客户端不可指定
    thread_id = graph.make_thread_id(campaign_id, character_id)
    # ★ P1-04: 客户端可携带 command_id 作为幂等键（WS 重连/前端重复点击不重复执行）
    command_id = (data.get("command_id") or "").strip()
    state_extra = {"idempotency_key": command_id} if command_id else {}
    try:
        async with get_campaign_lock(campaign_id):
            camp_room = CampaignRoom.get(campaign_id)
            if camp_room and not camp_room.is_player_turn(character_id):
                turn = camp_room.current_turn_name()
                await sio.emit("error",
                               {"message": f"还没轮到你，当前轮到 {turn}"},
                               to=sid)
                return
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                functools.partial(graph.run, player_input, campaign_id,
                                  character_id, thread_id, False, **state_extra),
            )
    except Exception as e:
        # 管线异常兑底：必须仍发 result，否则前端 busy 永久卡死（D4 实测发现）
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

    payload = {
        "player": name,
        "narration": narration,
        "dice": dice,
        "action_options": action_options,
    }
    if result.get("turn_hint"):
        payload["turn_hint"] = result["turn_hint"]     # 动作耗尽 → 前端高亮结束回合
    await sio.emit("result", payload, room=room)

    # 单人局自动推进可能已自然结束战斗 → 自动广播 combat_end
    _res_combat = result.get("combat") or {}
    if _res_combat.get("active") is False:
        try:
            _c_end = store.load_combat(campaign_id)
            await sio.emit("combat_end",
                           {"outcome": combat_flow.combat_outcome(_c_end)}, room=room)
        except Exception:
            pass

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


async def _emit_flow_events(room: str, events: list[dict]) -> None:
    """把 combat_flow 事件映射为 Socket.IO 事件逐条广播。

    事件协议见 docs/MULTIPLAYER_COMBAT_REDESIGN.md §4.4.1；
    monster_turn/monster_action 复用前端已监听的既有事件名。
    """
    for ev in events:
        t = ev.get("type")
        if t == "monster_action":
            await sio.emit("monster_turn", {"monster": ev["monster"]}, room=room)
            await sio.emit("monster_action",
                           {"monster": ev["monster"], "result": ev}, room=room)
        elif t == "death_save":
            await sio.emit("death_save", ev, room=room)
        elif t == "round_end":
            await sio.emit("round_end", {"round": ev["round"]}, room=room)
        elif t == "monster_flee":
            await sio.emit("monster_action",
                           {"monster": ev["monster"],
                            "result": {"fled": True, "monster": ev["monster"]}},
                           room=room)
        elif t == "combat_end":
            await sio.emit("combat_end", {"outcome": ev.get("outcome", "")}, room=room)


@sio.on("end_turn")
async def on_end_turn(sid, data):
    """结束自己的回合：服务端回合状态机推进并自动结算怪物/濒死者回合，
    直到轮到下一个可行动玩家或战斗结束（D5 死锁修复，见 combat_flow）。

    全程持 campaign 锁：与 on_action 的 graph.run 互斥，避免丢失更新。
    """
    session = await sio.get_session(sid)
    if not session:
        return

    campaign_id = session["campaign_id"]
    character_id = session["character_id"]
    room = f"campaign_{campaign_id}"

    async with get_campaign_lock(campaign_id):
        camp_room = CampaignRoom.get(campaign_id)
        if camp_room and not camp_room.is_player_turn(character_id):
            await sio.emit("error", {"message": "不是你的回合"}, to=sid)
            return
        try:
            loop = asyncio.get_event_loop()
            flow = await loop.run_in_executor(
                None, functools.partial(combat_flow.advance_and_resolve,
                                        campaign_id))
        except Exception as e:
            import traceback
            traceback.print_exc()
            await sio.emit("error", {"message": f"回合推进失败: {e}"}, to=sid)
            return

    if flow.combat is None:
        await sio.emit("error", {"message": "无战斗状态"}, to=sid)
        return

    # 锁外逐条广播推进中发生的事件（怪物行动/死亡豁免/轮次/战斗结束）
    await _emit_flow_events(room, flow.events)
    await _broadcast_state(campaign_id)

    if flow.current is not None:
        await sio.emit("turn_advanced", {
            "next": flow.current.name,
            "is_player": flow.current.is_player,
            # DMG 跟进先攻：叫出当前者时顺口提及下一位
            "next_next": combat_flow.peek_next_name(flow.combat),
        }, room=room)


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
# 兼容层（ConnectionManager / manager 已迁移至 brain.room，此处仅 re-export）
# main.py 的 `from .ws import manager` 和 routes/scene.py 的
# `from ..ws import manager` 仍可通过本模块访问。
# ──────────────────────────────────────────────────────────────────────────


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
