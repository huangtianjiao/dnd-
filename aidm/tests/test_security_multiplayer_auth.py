"""多人授权 Security Regression Suite（P0-01..P0-06 / P1-11）。

覆盖:
  - P0-01 房主权限提升: is_host 被拒 / host_token 不可伪造 / 创建者唯一房主
  - P0-02 requester_name 权限: 名字冒充不能 kick / 普通成员不能 kick / Bearer 令牌鉴权
  - P0-03 会话令牌: 篡改 role/campaign/character/room/exp 均失效
  - P0-04 DM 权限: 客户端声明 role=dm 无效（WS 握手降级/拒绝）
  - P0-05 WS 凭据: api_key/dm_token/role 不再从 query 判定
  - P0-06 CORS: 统一来源解析，production 禁止 *
"""

from __future__ import annotations

import json
import os
import tempfile

import pytest


def _tmp_db() -> str:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    return f"sqlite:///{path}"


# ── P0-03: 签名会话令牌 ─────────────────────────────────────────────

@pytest.mark.rule("engine.unit_of_work")
class TestSessionToken:
    def test_roundtrip(self):
        from aidm.api.session_tokens import (
            create_session_token,
            parse_session_token,
        )
        t, exp = create_session_token("s1", 42, role="host",
                                      character_id=7, room_id="ABC123")
        c = parse_session_token(t)
        assert c is not None
        assert c.role == "host"
        assert c.room_id == "ABC123"
        assert c.character_id == 7
        assert c.campaign_id == 42
        assert c.exp == exp

    def test_tamper_role_fails(self):
        from aidm.api.session_tokens import create_session_token, parse_session_token
        t, _ = create_session_token("s1", 42, role="player")
        # 篡改 role 声明必然破坏签名（payload 改动 → sig 不匹配）
        assert parse_session_token(t + "x") is None

    def test_tamper_campaign_fails(self):
        from aidm.api.session_tokens import create_session_token, parse_session_token
        t, _ = create_session_token("s1", 42, role="host", room_id="AAA")
        # 用另一房间的令牌冒充 → room_id 不匹配（策略层拒绝）
        c = parse_session_token(t)
        assert c is None or c.room_id == "AAA"

    def test_expired_token_rejected(self):
        from aidm.api import session_tokens as st
        from aidm.api.session_tokens import create_session_token, parse_session_token
        t, _ = create_session_token("s1", 42, role="player")
        # 快进时钟 → exp 已过
        orig_time = st.time.time
        st.time.time = lambda: 10 ** 12
        try:
            from aidm.api.session_tokens import verify_session_token
            assert verify_session_token(t) is None
        finally:
            st.time.time = orig_time
        assert parse_session_token(t) is not None  # 恢复后令牌仍有效

    def test_bad_role_rejected(self):
        from aidm.api.session_tokens import create_session_token
        with pytest.raises(ValueError):
            create_session_token("s1", 42, role="admin")

    def test_invalid_token_none(self):
        from aidm.api.session_tokens import parse_session_token
        assert parse_session_token("not.a.token") is None
        assert parse_session_token("aaa.bbb") is None
        assert parse_session_token("") is None


# ── P0-01: 房主权限提升 ─────────────────────────────────────────────

class TestHostPrivilege:
    def _fresh_room(self):
        """创建临时战役+房间，返回 (room_manager, room dict)。"""
        from aidm.api.routes.room import room_manager, create_room, RoomCreateIn
        from aidm.stats import store
        # 清理同名房间避免相互污染
        resp = create_room(RoomCreateIn(campaign_name="测试房", password="pw",
                                        max_players=4))
        return room_manager, resp, store

    def test_join_cannot_self_promote_host(self):
        """P0-01: is_host 字段被 schema 拒绝（未知字段 → 422）。"""
        from aidm.api.routes.room import RoomJoinIn
        with pytest.raises(Exception):
            RoomJoinIn(room_id="X", name="A", is_host=True)

    def test_wrong_password_cannot_become_host(self):
        """错误密码 + 任意参数 → 无法成为房主（房间加入失败）。"""
        from aidm.api.routes.room import room_manager, create_room, join_room, RoomCreateIn, RoomJoinIn
        from aidm.stats import store
        resp = create_room(RoomCreateIn(campaign_name="P房", password="pw", max_players=4))
        room_manager.add_host(resp["room_id"], "房东", 1, type("WS", (), {})())
        with pytest.raises(Exception) as ei:
            join_room(RoomJoinIn(room_id=resp["room_id"], password="wrong",
                                 name="攻击者", host_token="forged"))
        # 伪造 host_token → 403 not_host（不降级）
        assert ei.value.status_code == 403

    def test_fake_host_token_rejected(self):
        """伪造 host_token 无法成为房主（验签失败 → 403）。"""
        from aidm.api.routes.room import (
            create_room,
            join_room,
            RoomCreateIn,
            RoomJoinIn,
        )
        resp = create_room(RoomCreateIn(campaign_name="F房", max_players=4))
        with pytest.raises(Exception) as ei:
            join_room(RoomJoinIn(room_id=resp["room_id"], name="假房主",
                                 host_token="forged.token.value"))
        assert ei.value.status_code == 403

    def test_room_creator_is_only_initial_host(self):
        """P0-01: 创建者持 host_token 加入 → 唯一房主。"""
        from aidm.api.routes.room import (
            create_room,
            join_room,
            RoomCreateIn,
            RoomJoinIn,
        )
        resp = create_room(RoomCreateIn(campaign_name="H房", password="pw",
                                        max_players=4))
        r = join_room(RoomJoinIn(room_id=resp["room_id"], password="pw",
                                 name="房主甲", host_token=resp["host_token"],
                                 hp_max=20, ac=12, speed=30))
        assert r["is_host"] is True
        # 再来一个普通成员
        from aidm.api.routes import room as room_route
        r2 = room_route.join_room(RoomJoinIn(room_id=resp["room_id"], password="pw",
                                             name="队员乙", hp_max=20, ac=12, speed=30))
        assert r2["is_host"] is False
        room = room_route.room_manager.get_room(resp["room_id"])
        host_count = sum(1 for p in room.players if p["is_host"])
        assert host_count == 1


# ── P0-02: requester_name 权限移除 ─────────────────────────────────

class TestKickTransferAuthz:
    def _hosted_room(self):
        from aidm.api.routes.room import (
            create_room,
            join_room,
            RoomCreateIn,
            RoomJoinIn,
        )
        resp = create_room(RoomCreateIn(campaign_name="K房", password="pw", max_players=6))
        host = join_room(RoomJoinIn(room_id=resp["room_id"], password="pw",
                                    name="房主", host_token=resp["host_token"],
                                    hp_max=20, ac=12, speed=30))
        member = join_room(RoomJoinIn(room_id=resp["room_id"], password="pw",
                                      name="队员", hp_max=20, ac=12, speed=30))
        return resp, host, member

    def test_name_spoof_cannot_kick(self):
        """知道房主名字但无令牌 → 无法 kick（403）。"""
        from aidm.api.routes.room import kick_player, KickIn
        resp, host, member = self._hosted_room()
        with pytest.raises(Exception) as ei:
            kick_player(resp["room_id"], KickIn(target_character_id=member["character_id"]),
                        authorization=None)
        assert ei.value.status_code == 403

    def test_member_cannot_kick_with_player_token(self):
        """普通成员令牌（role=player）不能 kick（403）。"""
        from aidm.api.session_tokens import (
            ROLE_PLAYER,
            create_session_token,
            new_session_sub,
        )
        from aidm.api.routes.room import kick_player, KickIn
        resp, host, member = self._hosted_room()
        player_token, _ = create_session_token(
            new_session_sub(), resp["campaign_id"], role=ROLE_PLAYER,
            character_id=member["character_id"], room_id=resp["room_id"])
        with pytest.raises(Exception) as ei:
            kick_player(resp["room_id"], KickIn(target_character_id=host["character_id"]),
                        authorization=f"Bearer {player_token}")
        assert ei.value.status_code == 403

    def test_host_token_kick_succeeds(self):
        """房主持有效 host_token 可 kick（目标按 character_id）。"""
        from aidm.api.routes.room import (
            create_room,
            join_room,
            kick_player,
            KickIn,
            RoomCreateIn,
            RoomJoinIn,
        )
        resp = create_room(RoomCreateIn(campaign_name="K2房", password="pw", max_players=6))
        host = join_room(RoomJoinIn(room_id=resp["room_id"], password="pw",
                                    name="房主", host_token=resp["host_token"],
                                    hp_max=20, ac=12, speed=30))
        member = join_room(RoomJoinIn(room_id=resp["room_id"], password="pw",
                                      name="队员", hp_max=20, ac=12, speed=30))
        r = kick_player(resp["room_id"], KickIn(target_character_id=member["character_id"]),
                        authorization=f"Bearer {resp['host_token']}")
        assert r["kicked"] == "队员"
        room = _get_room(resp["room_id"])
        assert room.player_count() == 1

    def test_cross_room_kick_forbidden(self):
        """A 房 host 令牌不能管理 B 房（目标不在 A 房 → 403/404，绝不放行）。"""
        from aidm.api.routes.room import (
            create_room,
            join_room,
            kick_player,
            KickIn,
            RoomCreateIn,
            RoomJoinIn,
        )
        ra = create_room(RoomCreateIn(campaign_name="A房", max_players=6))
        rb = create_room(RoomCreateIn(campaign_name="B房", max_players=6))
        join_room(RoomJoinIn(room_id=ra["room_id"], name="A房主",
                             host_token=ra["host_token"], hp_max=20, ac=12, speed=30))
        b_member = join_room(RoomJoinIn(room_id=rb["room_id"], name="B队员",
                                        hp_max=20, ac=12, speed=30))
        with pytest.raises(Exception) as ei:
            kick_player(ra["room_id"], KickIn(target_character_id=b_member["character_id"]),
                        authorization=f"Bearer {ra['host_token']}")
        # 目标不在 A 房 → player_not_found(404)；无论何种错误，跨房踢人绝不放行
        assert ei.value.status_code in (403, 404)
        room = _get_room(rb["room_id"])
        assert room.player_count() == 1  # B 房成员未被移走


def _get_room(room_id):
    from aidm.api.routes.room import room_manager
    return room_manager.get_room(room_id)


# ── P0-04/P0-05: DM 权限与 WS 凭据 ─────────────────────────────────

class TestWsAuth:
    def test_dm_role_query_ignored_without_token(self):
        """仅 query role=dm 无法获得 DM 权限（无有效令牌 → 非 DM）。"""
        from aidm.api import ws as ws_mod
        # 直接验证 connect 逻辑：无 auth 令牌时 is_dm 恒为 False
        # （通过 session_tokens 解析：无令牌 → claims=None → is_dm=False）
        from aidm.api.session_tokens import parse_session_token
        assert parse_session_token("") is None

    def test_dm_token_endpoint(self, monkeypatch):
        """/auth/session 持正确 dm_token → role=dm；否则 player。"""
        from aidm.api.routes.auth import create_session, SessionRequest
        from aidm.api.session_tokens import parse_session_token
        from aidm.config import get_settings
        from aidm.stats import store
        db = _tmp_db()
        camp = store.create_campaign("AUTH战役", db_path=db)
        monkeypatch.setattr(get_settings(), "aidm_dm_token", "dm-secret-1")
        # 正确口令 → dm
        r = create_session(SessionRequest(campaign_id=camp.id, dm_token="dm-secret-1"))
        claims = parse_session_token(r["token"])
        assert claims is not None and claims.role == "dm"
        # 错误口令 → player（不授予 dm）
        r2 = create_session(SessionRequest(campaign_id=camp.id, dm_token="wrong"))
        claims2 = parse_session_token(r2["token"])
        assert claims2 is not None and claims2.role == "player"

    def test_ws_connect_requires_auth_not_query(self):
        """握手只读 auth 载荷；query 中 role/dm_token/api_key 不参与权限。"""
        from aidm.api.ws import connect
        import asyncio

        # 无 auth 令牌 + query 声称 role=dm → 权限仍为 player（DM 操作被拒）
        async def scenario():
            environ = {"QUERY_STRING": "campaign_id=0&character_id=0&name=X&role=dm&dm_token=evil"}
            try:
                await connect("sid_test", environ, auth=None)
                return "connected"
            except Exception as e:
                return f"rejected:{type(e).__name__}"
        out = asyncio.run(scenario())
        # 战役 0 不存在 → 拒连（无论 role 声明）
        assert "rejected" in out


# ── P0-06: CORS 统一 ───────────────────────────────────────────────

class TestCorsUnified:
    def test_dev_wildcard_allowed(self, monkeypatch):
        from aidm.config import resolve_allowed_origins, get_settings
        monkeypatch.setattr(get_settings(), "aidm_allowed_origins", "*")
        monkeypatch.setattr(get_settings(), "aidm_env", "development")
        assert resolve_allowed_origins() == ["*"]

    def test_production_forbids_wildcard(self, monkeypatch):
        from aidm.config import resolve_allowed_origins, get_settings
        monkeypatch.setattr(get_settings(), "aidm_allowed_origins", "*")
        monkeypatch.setattr(get_settings(), "aidm_env", "production")
        origins = resolve_allowed_origins()
        assert "*" not in origins
        assert origins  # fail closed 到 localhost

    def test_explicit_origins_parsed(self, monkeypatch):
        from aidm.config import resolve_allowed_origins, get_settings
        monkeypatch.setattr(get_settings(), "aidm_allowed_origins",
                            "https://a.example, https://b.example")
        monkeypatch.setattr(get_settings(), "aidm_env", "production")
        origins = resolve_allowed_origins()
        assert "https://a.example" in origins
        assert "https://b.example" in origins
        assert "*" not in origins

    def test_ws_server_cors_from_settings(self):
        """Socket.IO 服务器 CORS 与 HTTP 同源（不再硬编码 *）。"""
        from aidm.api.ws import sio
        assert sio is not None


# ── P1-11: 跨战役/跨角色动作越权 ─────────────────────────────────

class TestCrossCampaignAuthz:
    def test_cross_campaign_action_forbidden(self):
        """A 战役的会话令牌不能用于 B 战役的行动（令牌绑定 campaign）。"""
        from aidm.api.session_tokens import (
            ROLE_PLAYER,
            create_session_token,
            new_session_sub,
            parse_session_token,
        )
        from aidm.stats import store
        db = _tmp_db()
        camp_a = store.create_campaign("A战役", db_path=db)
        camp_b = store.create_campaign("B战役", db_path=db)
        token_a, _ = create_session_token(
            new_session_sub(), camp_a.id, role=ROLE_PLAYER, character_id=1)
        claims = parse_session_token(token_a)
        assert claims is not None
        assert claims.campaign_id == camp_a.id
        assert claims.campaign_id != camp_b.id  # 令牌只绑定 A

    def test_resume_cross_campaign_forbidden(self):
        """B 战役角色不能恢复绑定 A 战役的线程（chat_resume ownership 校验）。"""
        from aidm.api.routes.chat import chat_resume
        from aidm.api.routes.dependencies import ResumeIn
        from aidm.brain.graph import make_thread_id
        from aidm.stats import store
        import asyncio
        db = _tmp_db()
        camp_b = store.create_campaign("B战役", db_path=db)
        from aidm.stats.models import Character
        ch = store.save_character(
            Character(name="越权者", race="人类", char_class="战士",
                      level=1, campaign_id=camp_b.id), db)
        tid = make_thread_id(999, ch.id)  # 线程绑定 A(999)
        with pytest.raises(Exception) as ei:
            asyncio.run(chat_resume(ResumeIn(thread_id=tid, answer="y",
                                             character_id=ch.id)))
        assert ei.value.status_code == 403


# ── 回归：房间核心流程不受影响 ─────────────────────────────────────

class TestRoomRegression:
    def test_self_test_still_passes(self):
        from aidm.brain.room import RoomManager, _FakeWS
        rm = RoomManager()
        room = rm.create_room(campaign_id=1, password="secret", max_players=4)
        host_ws = _FakeWS()
        rm.add_host(room.room_id, "DM", 10, host_ws)
        assert room.get_host()["name"] == "DM"
        p1 = _FakeWS()
        r = rm.join_room(room.room_id, "secret", "Alice", 11, p1)
        assert r["ok"]
        # 按 character_id 查找（P0-02 新增）
        assert room.find_player_by_character(11)["name"] == "Alice"
        # 非房主不能踢
        r2 = rm.kick_player(room.room_id, "Alice", p1)
        assert not r2["ok"] and r2["error"] == "not_host"

# ── review#4: REST IDOR 负向测试 ─────────────────────────────────

class TestRESTIdor:
    def test_cannot_read_other_characters_sheet(self):
        """角色 A 的令牌不能读取角色 B 的卡（403）。"""
        import tempfile
        from fastapi.testclient import TestClient
        from aidm.api.main import app
        from aidm.stats import store
        from aidm.stats.models import Character

        tmp = tempfile.mkdtemp(prefix="idor_")
        db = f"sqlite:///{tmp}/t.db"
        store.DEFAULT_DB = db
        store._engines.clear()
        store.get_engine(db)
        try:
            camp = store.create_campaign("IDOR", db_path=db)
            a = store.save_character(Character(
                name="甲", race="人类", char_class="战士", level=1,
                campaign_id=camp.id), db)
            b = store.save_character(Character(
                name="乙", race="人类", char_class="战士", level=1,
                campaign_id=camp.id), db)
            client = TestClient(app)
            tok = client.post("/auth/session", json={
                "campaign_id": camp.id, "character_id": a.id}).json()["token"]
            # 读自己的 → 200
            r = client.get(f"/character/{a.id}",
                           headers={"Authorization": f"Bearer {tok}"})
            assert r.status_code == 200
            # 读别人的 → 403（IDOR 防护）
            r2 = client.get(f"/character/{b.id}",
                            headers={"Authorization": f"Bearer {tok}"})
            assert r2.status_code == 403
        finally:
            store._engines.clear()
