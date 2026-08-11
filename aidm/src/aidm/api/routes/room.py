"""房间管理路由。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from ...brain import room as room_mod
from ...stats import models, store
from .dependencies import init_loadout, _NAME_INJECT_RE, _HP_MIN, _HP_MAX, _AC_MIN, _AC_MAX, _SPEED_MIN, _SPEED_MAX, _LEVEL_MIN, _LEVEL_MAX, _ABILITY_MIN, _ABILITY_MAX

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
    subclass: str = ""
    background: str = ""
    alignment: str = "绝对中立"
    level: int = 1
    abilities: dict = {"str": 10, "dex": 10, "con": 10,
                       "int": 10, "wis": 10, "cha": 10}
    ability_method: str = "free"
    hp_max: int = 10
    ac: int = 10
    speed: int = 30
    equipped_weapon: str = ""
    is_host: bool = False

    # SEC-001: 输入校验（与 CharIn 同口径）
    @field_validator("name")
    @classmethod
    def _validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("名称不能为空")
        if len(v) > 50:
            raise ValueError("名称不能超过50字符")
        if _NAME_INJECT_RE.search(v):
            raise ValueError("名称包含非法字符")
        return v.strip()

    @field_validator("hp_max")
    @classmethod
    def _validate_hp(cls, v: int) -> int:
        if not (_HP_MIN < v <= _HP_MAX):
            raise ValueError(f"HP上限须在 {_HP_MIN+1}-{_HP_MAX} 范围内")
        return v

    @field_validator("ac")
    @classmethod
    def _validate_ac(cls, v: int) -> int:
        if not (_AC_MIN <= v <= _AC_MAX):
            raise ValueError(f"AC须在 {_AC_MIN}-{_AC_MAX} 范围内")
        return v

    @field_validator("level")
    @classmethod
    def _validate_level(cls, v: int) -> int:
        if not (_LEVEL_MIN <= v <= _LEVEL_MAX):
            raise ValueError(f"等级须在 {_LEVEL_MIN}-{_LEVEL_MAX} 范围内")
        return v

    @field_validator("abilities")
    @classmethod
    def _validate_abilities(cls, v: dict) -> dict:
        for k, val in v.items():
            if k not in ("str", "dex", "con", "int", "wis", "cha"):
                raise ValueError(f"未知属性 {k}")
            if not (_ABILITY_MIN <= int(val) <= _ABILITY_MAX):
                raise ValueError(f"属性值须在 {_ABILITY_MIN}-{_ABILITY_MAX} 范围内")
        return v


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
        campaign_name=camp.name,
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

    # 先创建角色卡（关联到房间对应的战役；与 /character 同口径校验属性）
    from .dependencies import validate_abilities
    validate_abilities(req.abilities, req.ability_method)
    ch = models.Character(name=req.name, race=req.race,
                          char_class=req.char_class, level=req.level,
                          subclass=req.subclass, background=req.background,
                          alignment=req.alignment,
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


@router.get("/room/by-campaign/{campaign_id}")
def get_room_by_campaign(campaign_id: int):
    """按战役 ID 查房间（继续游戏时恢复房间上下文）。

    房间是纯内存对象，进程重启后不存在属正常情况 → 404。
    """
    room = room_manager.find_by_campaign(campaign_id)
    if room is None:
        raise _room_http_error("room_not_found")
    return room.to_dict()


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
