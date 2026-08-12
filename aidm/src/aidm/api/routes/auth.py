"""认证路由 — 会话令牌签发（P0-03 / P0-04）。

提供一个统一入口换取签名会话令牌，替代客户端自声明身份：
  - POST /auth/session
      {campaign_id, character_id?, room_id?, dm_token?}
    → 持正确 AIDM_DM_TOKEN 时返回 role=dm 令牌；否则 role=player 令牌。
      校验 campaign/character 存在性（与 WS 握手同口径）。
  - GET  /auth/session/{token}（自检用，返回 claims 摘要）

令牌本身不包含服务器密钥；篡改任何字段都会验签失败。
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from ...config import get_settings
from ...stats import store
from ..session_tokens import (
    ROLE_DM,
    ROLE_PLAYER,
    create_session_token,
    new_session_sub,
    parse_session_token,
)

router = APIRouter(tags=["auth"])


class SessionRequest(BaseModel):
    """换取会话令牌的请求。"""

    campaign_id: int
    character_id: int = 0
    room_id: str = ""
    dm_token: str = ""

    @field_validator("campaign_id")
    @classmethod
    def _validate_campaign(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("campaign_id 必须为正整数")
        return v


@router.post("/auth/session")
def create_session(req: SessionRequest):
    """签发会话令牌。

    - 战役必须存在；character_id>0 时角色必须存在且属于该战役。
    - dm_token 与 AIDM_DM_TOKEN 匹配（且已配置）→ role=dm；否则 role=player。
      客户端无法通过任何请求参数自封 DM 或 host。
    """
    if store.get_campaign(req.campaign_id) is None:
        raise HTTPException(status_code=404, detail={"error": "campaign_not_found",
                                                     "message": "战役不存在"})
    if req.character_id:
        ch = store.get_character(req.character_id)
        if ch is None or ch.campaign_id != req.campaign_id:
            raise HTTPException(status_code=404, detail={"error": "character_not_found",
                                                         "message": "角色不存在或不属于该战役"})

    settings = get_settings()
    expected_dm = settings.aidm_dm_token.strip()
    is_dm = bool(expected_dm) and req.dm_token == expected_dm

    token, exp = create_session_token(
        sub=new_session_sub(),
        campaign_id=req.campaign_id,
        role=ROLE_DM if is_dm else ROLE_PLAYER,
        character_id=req.character_id,
        room_id=req.room_id,
    )
    return {
        "token": token,
        "expires_at": exp,
        "role": ROLE_DM if is_dm else ROLE_PLAYER,
        "campaign_id": req.campaign_id,
        "character_id": req.character_id,
    }


@router.get("/auth/session/inspect/{token}")
def inspect_session(token: str):
    """（诊断）解析令牌声明，不泄露签名。"""
    claims = parse_session_token(token)
    if claims is None:
        raise HTTPException(status_code=401, detail={"error": "invalid_token",
                                                     "message": "令牌无效或已过期"})
    return {
        "sub": claims.sub,
        "campaign_id": claims.campaign_id,
        "character_id": claims.character_id,
        "room_id": claims.room_id,
        "role": claims.role,
        "exp": claims.exp,
    }