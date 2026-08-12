"""房间管理路由。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi import Header
from pydantic import BaseModel, ConfigDict, field_validator

from ...brain import room as room_mod
from ...stats import models, store
from .dependencies import init_loadout, _NAME_INJECT_RE, _HP_MIN, _HP_MAX, _AC_MIN, _AC_MAX, _SPEED_MIN, _SPEED_MAX, _LEVEL_MIN, _LEVEL_MAX, _ABILITY_MIN, _ABILITY_MAX
from ..session_tokens import (
    ROLE_HOST,
    create_session_token,
    new_session_sub,
    parse_session_token,
)

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
    """玩家加入房间：输入房间号+密码+角色信息。

    ★ P0-01: 不再接受 is_host —— 房主身份只能由 /room/create 返回的
      host_token 换取（服务器签名），客户端无法自封房主。
    """
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
    # 房主令牌：由 /room/create 签发（role=host、绑定 room_id），
    # 服务器验签通过才创建 host 成员身份
    host_token: str = ""

    # ★ P0-01: 拒绝未知字段（如旧版 is_host），客户端无法通过任何字段自封房主
    model_config = ConfigDict(extra="forbid")

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
    """房主踢出玩家（P0-02：身份来自 Authorization: Bearer 令牌，非名字）。"""
    target_character_id: int


class TransferIn(BaseModel):
    """房主转让权限（P0-02：身份来自 Authorization: Bearer 令牌，非名字）。"""
    target_character_id: int


def _require_host_token(room_id: str, authorization: str | None) -> dict:
    """从 Bearer 令牌解析房主身份（P0-02）。

    校验: 令牌有效、role=host、room_id 与目标房间一致。
    失败抛 403（fail closed）。
    """
    claims = None
    if authorization and authorization.lower().startswith("bearer "):
        claims = parse_session_token(authorization[7:].strip())
    if claims is None or not claims.is_host or claims.room_id != room_id:
        raise _room_http_error("not_host")
    return claims.raw


@router.post("/room/create")
def create_room(req: RoomCreateIn):
    """房主创建房间。

    ★ P0-01: 创建即由服务器签发 host 身份令牌（绑定 room_id/campaign_id），
      房主凭令牌加入；客户端不提交任何 is_host 声明。
    """
    camp = store.create_campaign(req.campaign_name)
    room = room_manager.create_room(
        campaign_id=camp.id,
        password=req.password,
        max_players=req.max_players,
        campaign_name=camp.name,
    )
    host_token, exp = create_session_token(
        sub=new_session_sub(),
        campaign_id=camp.id,
        role=ROLE_HOST,
        room_id=room.room_id,
    )
    return {
        "room_id": room.room_id,
        "campaign_id": camp.id,
        "campaign_name": camp.name,
        "has_password": bool(room.password),
        "max_players": room.max_players,
        "host_token": host_token,
        "host_token_expires_at": exp,
    }


@router.post("/room/join")
def join_room(req: RoomJoinIn):
    """玩家加入房间：创建角色卡并加入房间。

    ★ P0-01: 只有携带 /room/create 签发的有效 host_token 才会成为房主；
      否则一律创建普通成员（走密码/人数/重名校验）。
    """
    room = room_manager.get_room(req.room_id)
    if room is None:
        raise _room_http_error("room_not_found")

    # 解析 host 身份：令牌验签 + role=host + room_id 匹配
    is_host = False
    if req.host_token:
        claims = parse_session_token(req.host_token)
        is_host = bool(claims and claims.is_host
                       and claims.room_id == req.room_id)
        if not is_host:
            # 令牌无效/不匹配 → 拒绝加入（不降级为普通成员静默通过）
            raise _room_http_error("not_host")

    # 先创建角色卡（关联到房间对应的战役；与 /character 同口径校验属性）
    from .dependencies import validate_abilities
    validate_abilities(req.abilities, req.ability_method)
    ch = models.Character(name=req.name, race=req.race,
                          char_class=req.char_class, level=req.level,
                          subclass=req.subclass, background=req.background,
                          alignment=req.alignment,
                          campaign_id=room.campaign_id)
    ch.set_abilities(req.abilities)
    # ★ P1-01: 机械属性由服务器权威计算（HP/AC/速度），客户端提交值被忽略
    from ...build.derive_stats import apply_server_stats
    apply_server_stats(ch, req.char_class, req.race, req.level, req.abilities)
    # 统一初始化拥有物（与 /character 一致）：法术位 + 已学法术 + 起始武器入包
    init_loadout(ch, req.equipped_weapon)
    ch = store.save_character(ch)

    # 加入房间（用假 ws 占位；真实连接由 WebSocket 端点建立）
    fake_ws = type("FakeWS", (), {})()

    if is_host:
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
        "is_host": is_host,
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
def kick_player(room_id: str, req: KickIn,
                authorization: str | None = Header(default=None)):
    """房主踢出指定玩家（P0-02：Authorization Bearer 令牌鉴权，禁止名字冒充）。"""
    room = room_manager.get_room(room_id)
    if room is None:
        raise _room_http_error("room_not_found")
    _require_host_token(room_id, authorization)
    target = room.find_player_by_character(req.target_character_id)
    if target is None:
        raise _room_http_error("player_not_found")
    if target["is_host"]:
        raise _room_http_error("cannot_kick_host")
    room.players = [p for p in room.players
                    if p["character_id"] != req.target_character_id]
    return {"kicked": target["name"], "room": room.to_dict()}


@router.post("/room/{room_id}/transfer")
def transfer_host(room_id: str, req: TransferIn,
                  authorization: str | None = Header(default=None)):
    """房主将房主权限转让给另一玩家（P0-02：Bearer 令牌鉴权）。"""
    room = room_manager.get_room(room_id)
    if room is None:
        raise _room_http_error("room_not_found")
    _require_host_token(room_id, authorization)
    target = room.find_player_by_character(req.target_character_id)
    if target is None:
        raise _room_http_error("player_not_found")
    for p in room.players:
        p["is_host"] = (p["character_id"] == req.target_character_id)
    return {"new_host": target["name"], "room": room.to_dict()}
