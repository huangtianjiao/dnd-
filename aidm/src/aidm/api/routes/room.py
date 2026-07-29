"""房间管理路由。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...brain import room as room_mod
from ...stats import models, store
from .dependencies import init_loadout

router = APIRouter(tags=["room"])

# 房间管理器实例
room_manager = room_mod.RoomManager()


# 房间错误码 → HTTP 状态码/中文描述
_ROOM_ERR_STATUS = {
    "room_not_found": 404,
    "player_not_found": 404,
    "wrong_password": 400,
    "name_taken": 400,
    "room_full": 409,
    "cannot_kick_host": 400,
    "not_host": 403,
}
_ROOM_ERR_MSG = {
    "room_not_found": "房间号不存在",
    "player_not_found": "玩家不存在",
    "wrong_password": "密码错误",
    "name_taken": "名字已被占用",
    "room_full": "房间已满",
    "cannot_kick_host": "不能踢出房主",
    "not_host": "只有房主可以执行此操作",
}


def _room_http_error(code: str) -> HTTPException:
    """将房间错误码转为统一形态的 HTTPException。"""
    return HTTPException(
        status_code=_ROOM_ERR_STATUS.get(code, 400),
        detail={"error": code, "message": _ROOM_ERR_MSG.get(code, code)},
    )


class RoomCreateIn(BaseModel):
    """房主创建房间：先建战役，再设密码/人数上限。"""
    campaign_name: str = "新战役"
    password: str = ""
    max_players: int = 6


class RoomJoinIn(BaseModel):
    """玩家加入房间：输入房间号+密码+角色信息。"""
    room_id: str
    password: str = ""
    name: str
    race: str = "人类"
    char_class: str = "战士"
    level: int = 1
    abilities: dict = {"str": 10, "dex": 10, "con": 10,
                       "int": 10, "wis": 10, "cha": 10}
    hp_max: int = 10
    ac: int = 10
    speed: int = 30
    equipped_weapon: str = ""
    is_host: bool = False


class KickIn(BaseModel):
    """房主踢出玩家。"""
    target_name: str
    requester_name: str


class TransferIn(BaseModel):
    """房主转让权限。"""
    target_name: str
    requester_name: str


@router.post("/room/create")
def create_room(req: RoomCreateIn):
    """房主创建房间。"""
    camp = store.create_campaign(req.campaign_name)
    room = room_manager.create_room(
        campaign_id=camp.id,
        password=req.password,
        max_players=req.max_players,
    )
    return {
        "room_id": room.room_id,
        "campaign_id": camp.id,
        "campaign_name": camp.name,
        "has_password": bool(room.password),
        "max_players": room.max_players,
    }


@router.post("/room/join")
def join_room(req: RoomJoinIn):
    """玩家加入房间：创建角色卡并加入房间。"""
    room = room_manager.get_room(req.room_id)
    if room is None:
        raise _room_http_error("room_not_found")

    # 先创建角色卡（关联到房间对应的战役）
    ch = models.Character(name=req.name, race=req.race,
                          char_class=req.char_class, level=req.level,
                          campaign_id=room.campaign_id)
    ch.set_abilities(req.abilities)
    ch.hp_max = req.hp_max; ch.hp_current = req.hp_max
    ch.ac = req.ac; ch.speed = req.speed
    # 统一初始化拥有物（与 /character 一致）：法术位 + 已学法术 + 起始武器入包
    init_loadout(ch, req.equipped_weapon)
    ch = store.save_character(ch)

    # 加入房间（用假 ws 占位；真实连接由 WebSocket 端点建立）
    fake_ws = type("FakeWS", (), {})()

    if req.is_host:
        room_manager.add_host(req.room_id, req.name, ch.id, fake_ws)
    else:
        result = room_manager.join_room(
            req.room_id, req.password, req.name, ch.id, fake_ws)
        if not result["ok"]:
            # 加入失败，删除刚创建的角色卡
            store.delete_character(ch.id)
            raise _room_http_error(result["error"])

    return {
        "room_id": req.room_id,
        "campaign_id": room.campaign_id,
        "character_id": ch.id,
        "name": ch.name,
        "ws_url": f"ws://<host>/ws/{room.campaign_id}"
                  f"?character_id={ch.id}&name={req.name}",
    }


@router.get("/room/{room_id}")
def get_room_status(room_id: str):
    """获取房间状态（不含密码）。"""
    room = room_manager.get_room(room_id)
    if room is None:
        raise _room_http_error("room_not_found")
    return room.to_dict()


@router.get("/rooms")
def list_rooms():
    """列出所有活跃房间。"""
    return {"rooms": room_manager.list_rooms()}


@router.post("/room/{room_id}/kick")
def kick_player(room_id: str, req: KickIn):
    """房主踢出指定玩家。"""
    room = room_manager.get_room(room_id)
    if room is None:
        raise _room_http_error("room_not_found")
    host = room.get_host()
    if host is None or host["name"] != req.requester_name:
        raise _room_http_error("not_host")
    target = room.find_player_by_name(req.target_name)
    if target is None:
        raise _room_http_error("player_not_found")
    if target["is_host"]:
        raise _room_http_error("cannot_kick_host")
    room.players = [p for p in room.players
                    if p["name"] != req.target_name]
    return {"kicked": req.target_name, "room": room.to_dict()}


@router.post("/room/{room_id}/transfer")
def transfer_host(room_id: str, req: TransferIn):
    """房主将房主权限转让给另一玩家。"""
    room = room_manager.get_room(room_id)
    if room is None:
        raise _room_http_error("room_not_found")
    host = room.get_host()
    if host is None or host["name"] != req.requester_name:
        raise _room_http_error("not_host")
    target = room.find_player_by_name(req.target_name)
    if target is None:
        raise _room_http_error("player_not_found")
    for p in room.players:
        p["is_host"] = (p["name"] == req.target_name)
    return {"new_host": req.target_name, "room": room.to_dict()}
