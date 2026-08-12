"""签名作用域会话令牌（P0-03）— 统一用户/房间身份模型。

替换弱身份模型（NEXT_PUBLIC_API_KEY + role=dm + requester_name + character_id 自声明）：
  - 服务器签名（HMAC-SHA256，密钥不进入令牌）
  - 短期有效（AIDM_SESSION_TTL，默认 8 小时）
  - 权限最小化（claims 绑定 campaign/room/character/role）
  - 篡改任意字段（character_id/campaign_id/role/room_id/exp）→ 验签失败

令牌格式: base64url(json_claims) . base64url(hmac_sha256(secret, canonical))

规则依据: P0-03 feint(auth): introduce signed scoped session tokens
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field
from typing import Any, Optional

# 合法角色（权限最小化）
ROLE_PLAYER = "player"
ROLE_HOST = "host"
ROLE_DM = "dm"
VALID_ROLES = {ROLE_PLAYER, ROLE_HOST, ROLE_DM}

# 进程内随机密钥缓存（development 未配置 AIDM_SESSION_SECRET 时使用）
_EPHEMERAL_SECRET: Optional[str] = None


def _derive_secret() -> str:
    """解析签名密钥。

    优先级: AIDM_SESSION_SECRET > AIDM_API_KEY > 进程内随机（仅 development）。
    production 模式未配置任何密钥 → 抛 RuntimeError（fail closed）。
    """
    from ..config import get_settings, is_production
    settings = get_settings()
    if settings.aidm_session_secret.strip():
        return settings.aidm_session_secret.strip()
    if settings.aidm_api_key.strip():
        return settings.aidm_api_key.strip()
    if is_production():
        # P2-05: 归类为基础设施错误（拒绝启动，fail closed）
        from ..errors import InfrastructureError
        raise InfrastructureError(
            "生产模式必须配置 AIDM_SESSION_SECRET（会话令牌签名密钥）",
            operation="session_tokens._derive_secret")
    global _EPHEMERAL_SECRET
    if _EPHEMERAL_SECRET is None:
        _EPHEMERAL_SECRET = secrets.token_hex(32)
    return _EPHEMERAL_SECRET


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def _sign(canonical: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), canonical.encode("utf-8"),
                    hashlib.sha256).hexdigest()


def create_session_token(
    sub: str,
    campaign_id: int,
    role: str = ROLE_PLAYER,
    character_id: int = 0,
    room_id: str = "",
    ttl: int | None = None,
) -> tuple[str, int]:
    """签发一个签名作用域会话令牌。

    Args:
        sub: 会话唯一 ID（如 room host 的 session-id）
        campaign_id: 绑定的战役 ID
        role: player / host / dm
        character_id: 绑定的角色卡 ID（0 = 未绑定，如 DM）
        room_id: 绑定的房间码（可选）
        ttl: 有效期秒数（None → 配置默认）

    Returns:
        (token, expires_at_unix)
    """
    from ..config import get_settings
    if role not in VALID_ROLES:
        raise ValueError(f"非法角色: {role}")
    settings = get_settings()
    ttl_s = ttl if ttl is not None else settings.aidm_session_ttl
    claims: dict[str, Any] = {
        "sub": sub,
        "campaign_id": int(campaign_id),
        "character_id": int(character_id),
        "room_id": room_id,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + max(1, int(ttl_s)),
    }
    payload = _b64encode(json.dumps(claims, ensure_ascii=False,
                                    separators=(",", ":")).encode("utf-8"))
    canonical = payload
    sig = _sign(canonical, _derive_secret())
    return f"{payload}.{sig}", claims["exp"]


def verify_session_token(token: str) -> Optional[dict]:
    """验证会话令牌。签名不符 / 过期 / 非法角色 → None。"""
    if not token or "." not in token:
        return None
    payload, sig = token.rsplit(".", 1)
    secret = _derive_secret()
    expected = _sign(payload, secret)
    if not hmac.compare_digest(sig, expected):
        return None
    try:
        claims = json.loads(_b64decode(payload).decode("utf-8"))
    except Exception:
        return None
    if not isinstance(claims, dict):
        return None
    exp = claims.get("exp")
    if not isinstance(exp, int) or exp < int(time.time()):
        return None
    if claims.get("role") not in VALID_ROLES:
        return None
    return claims


def new_session_sub() -> str:
    """生成会话唯一 ID。"""
    return secrets.token_hex(16)


@dataclass
class SessionClaims:
    """解析后的会话声明（供路由/WS 使用）。"""

    sub: str = ""
    campaign_id: int = 0
    character_id: int = 0
    room_id: str = ""
    role: str = ROLE_PLAYER
    exp: int = 0
    raw: dict = field(default_factory=dict)

    @property
    def is_dm(self) -> bool:
        """DM 能力（含房主）：可管理战斗/房间。"""
        return self.role in (ROLE_DM, ROLE_HOST)

    @property
    def is_host(self) -> bool:
        return self.role == ROLE_HOST


def parse_session_token(token: str) -> Optional[SessionClaims]:
    """验证并解析令牌为 SessionClaims（失败返回 None）。"""
    claims = verify_session_token(token)
    if claims is None:
        return None
    return SessionClaims(
        sub=claims.get("sub", ""),
        campaign_id=int(claims.get("campaign_id", 0) or 0),
        character_id=int(claims.get("character_id", 0) or 0),
        room_id=claims.get("room_id", ""),
        role=claims.get("role", ROLE_PLAYER),
        exp=int(claims.get("exp", 0) or 0),
        raw=claims,
    )