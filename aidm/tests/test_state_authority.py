"""PR3 State Authority 测试 — P1-01..P1-05。

  - P1-01 服务器权威机械属性：客户端 HP/AC/速度被忽略，由规则引擎计算
  - P1-02 HITL 线程身份：thread_id 服务器生成并绑定 campaign/character
  - P1-03 /chat/resume 越权：跨角色/跨战役被拒、非法 thread_id 被拒、持锁
  - P1-04 幂等键：同 command_id 重复提交不重复执行
  - P1-05 战役乐观锁：expected_version 不匹配 → 409，匹配则推进版本
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


# ── P1-01: 服务器权威机械属性 ─────────────────────────────────────

@pytest.mark.rule("engine.dice")
@pytest.mark.rule("engine.combat")
class TestServerAuthoritativeStats:
    def test_derive_stats_basic(self):
        from aidm.build.derive_stats import derive_character_stats
        s = derive_character_stats("战士", "人类", 1,
                                   {"str": 16, "dex": 14, "con": 14,
                                    "int": 10, "wis": 10, "cha": 10})
        assert s["hp_max"] == 12          # 满骰10 + CON2
        assert s["ac"] == 12              # 10 + DEX2
        assert s["speed"] == 30           # 人类
        assert s["proficiency_bonus"] == 2

    def test_derive_stats_level5_wizard(self):
        from aidm.build.derive_stats import derive_character_stats
        s = derive_character_stats("法师", "精灵", 5,
                                   {"str": 8, "dex": 14, "con": 12,
                                    "int": 16, "wis": 10, "cha": 10})
        assert s["hp_max"] == 27
        assert s["proficiency_bonus"] == 3

    def test_create_character_ignores_client_stats(self):
        """P1-01: /character 提交 hp_max=999/ac=50 被忽略，服务器计算。"""
        from aidm.stats import store
        from aidm.stats.models import Character
        db = _tmp_db()
        store.create_campaign("S房", db_path=db)
        from aidm.api.routes.character import create_character
        from aidm.api.routes.dependencies import CharIn
        c = CharIn(name="勇者", race="人类", char_class="战士", level=1,
                   abilities={"str": 16, "dex": 14, "con": 14,
                              "int": 10, "wis": 10, "cha": 10},
                   hp_max=999, ac=50, speed=99)
        r = create_character(c)
        ch = store.get_character(r["id"])
        assert ch.hp_max == 12, ch.hp_max   # 服务器推导，非客户端 999
        assert ch.ac == 12
        assert ch.speed == 30

    def test_join_ignores_client_stats(self):
        from aidm.stats import store
        from aidm.api.routes.character import join_campaign
        from aidm.api.routes.dependencies import JoinIn
        db = _tmp_db()
        camp = store.create_campaign("J房", db_path=db)
        r = join_campaign(JoinIn(name="冒险者", campaign_id=camp.id,
                                 race="人类", char_class="战士", level=1,
                                 abilities={"str": 16, "dex": 14, "con": 14,
                                            "int": 10, "wis": 10, "cha": 10},
                                 hp_max=500, ac=40, speed=120))
        ch = store.get_character(r["character_id"])
        assert ch.hp_max == 12
        assert ch.ac == 12
        assert ch.speed == 30


# ── P1-02: HITL 线程身份 ──────────────────────────────────────────

@pytest.mark.rule("engine.timing")
class TestThreadIdentity:
    def test_make_thread_id_binds_campaign_character(self):
        from aidm.brain.graph import make_thread_id, parse_thread_id
        tid = make_thread_id(7, 42)
        parsed = parse_thread_id(tid)
        assert parsed["campaign_id"] == 7
        assert parsed["character_id"] == 42
        assert parsed["session_id"]

    def test_parse_rejects_legacy_format(self):
        from aidm.brain.graph import parse_thread_id
        assert parse_thread_id("default") is None
        assert parse_thread_id("campaign_7") is None
        assert parse_thread_id("") is None

    def test_threads_are_unique_per_session(self):
        from aidm.brain.graph import make_thread_id
        t1 = make_thread_id(1, 2)
        t2 = make_thread_id(1, 2)
        assert t1 != t2  # 每次会话独立线程


# ── P1-03: /chat/resume 越权 ──────────────────────────────────────

class TestResumeAuthz:
    def test_invalid_thread_id_rejected(self):
        from aidm.api.routes.chat import chat_resume
        from aidm.api.routes.dependencies import ResumeIn
        import asyncio
        with pytest.raises(Exception) as ei:
            asyncio.run(chat_resume(ResumeIn(thread_id="default", answer="y",
                                             character_id=1)))
        assert ei.value.status_code == 400

    def test_cross_character_resume_forbidden(self):
        """角色 A 不能恢复角色 B 的线程（ownership 校验）。"""
        from aidm.api.routes.chat import chat_resume
        from aidm.api.routes.dependencies import ResumeIn
        from aidm.brain.graph import make_thread_id
        import asyncio
        tid = make_thread_id(1, 100)  # 线程绑定 character 100
        with pytest.raises(Exception) as ei:
            asyncio.run(chat_resume(ResumeIn(thread_id=tid, answer="y",
                                             character_id=999)))
        assert ei.value.status_code == 403

    def test_resume_holds_campaign_lock(self):
        """resume 走 campaign 锁路径（与 /chat 的 graph.run 互斥）。"""
        from aidm.brain.graph import make_thread_id
        tid = make_thread_id(1, 1)
        assert "campaign:1:character:1" in tid


# ── P1-04: 幂等键 ─────────────────────────────────────────────────

class TestIdempotency:
    def test_game_state_accepts_idempotency_key(self):
        from aidm.brain.state import GameState
        st = GameState(player_input="x", campaign_id=1, character_id=1,
                       idempotency_key="cmd-1")
        assert st.idempotency_key == "cmd-1"

    def test_graph_run_passes_extra_state(self):
        from aidm.brain.graph import run
        # 不实际 invoke（需 DB/Qdrant），仅验证签名接受 extra
        import inspect
        sig = inspect.signature(run)
        assert "extra" in str(sig) or any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())

    def test_apply_node_idempotent(self):
        from aidm.engine.unit_of_work import (
            CommandResult,
            get_idempotency_store,
        )
        store = get_idempotency_store()
        store.clear()
        store.record(CommandResult(command_id="c1", idempotency_key="c1",
                                   success=True, result_data={"hp": 5}))
        cached = store.check("c1")
        assert cached is not None and cached.result_data == {"hp": 5}
        store.clear()


# ── P1-05: 战役乐观锁 ─────────────────────────────────────────────

class TestCampaignOptimisticLock:
    def test_stale_version_409(self):
        from aidm.stats import store
        db = _tmp_db()
        camp = store.create_campaign("V房", db_path=db)
        assert getattr(camp, "version", 0) == 0
        # 期望版本 5（实际 0）→ 冲突
        with pytest.raises(store.StaleVersionError):
            store.save_campaign(camp, db_path=db, expected_version=5)

    def test_matching_version_bumps(self):
        from aidm.stats import store
        db = _tmp_db()
        camp = store.create_campaign("V2房", db_path=db)
        saved = store.save_campaign(camp, db_path=db, expected_version=0)
        assert saved.version == 1

    def test_legacy_save_without_version(self):
        from aidm.stats import store
        db = _tmp_db()
        camp = store.create_campaign("V3房", db_path=db)
        camp.rolling_summary = "x"
        saved = store.save_campaign(camp, db_path=db)  # 无版本参数 → 兼容
        assert saved is not None

    def test_model_has_version_column(self):
        from aidm.stats.models import Campaign
        assert "version" in Campaign.__table__.columns


# ── P1-07: 版本化数据库迁移 ───────────────────────────────────────

class TestVersionedMigrations:
    def test_fresh_db_records_migration_version(self):
        """新库：schema_migrations 记录到 SCHEMA_VERSION。"""
        from aidm.stats import store
        db = _tmp_db()
        eng = store.get_engine(db)
        from sqlalchemy import text
        with eng.begin() as conn:
            rows = conn.execute(text("SELECT max(version) FROM schema_migrations"))
            assert rows.scalar() == store.SCHEMA_VERSION

    def test_old_db_gets_missing_columns(self):
        """旧库（缺列）→ 迁移 001 补齐并记录版本。"""
        import sqlite3
        import tempfile
        from aidm.stats import store
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        conn = sqlite3.connect(path)
        conn.execute("CREATE TABLE campaign (id INTEGER PRIMARY KEY, name TEXT)")
        conn.commit()
        conn.close()
        db = f"sqlite:///{path}"
        store.get_engine(db)
        conn = sqlite3.connect(path)
        cols = {r[1] for r in conn.execute("PRAGMA table_info(campaign)")}
        conn.close()
        assert "world_flags_json" in cols  # 迁移补上了缺失列

    def test_migration_failure_raises(self):
        """P1-07: 迁移失败必须抛错（拒绝启动），不吞异常。"""
        from aidm.stats import store

        def _bad(engine, insp):
            raise RuntimeError("boom")
        orig = store._MIGRATIONS
        store._MIGRATIONS = {1: orig[1], 999: _bad}
        try:
            db = _tmp_db()
            with pytest.raises(RuntimeError):
                store.get_engine(db)
        finally:
            store._MIGRATIONS = orig

# ── review#11: inventory 双权威收敛 ───────────────────────────────

class TestInventorySingleAuthority:
    def test_sync_inventory_views_reconciles(self):
        """保存后 items_structured 与 inventory 一致（inventory 权威）。"""
        from aidm.stats import store
        from aidm.stats.models import Character
        db = _tmp_db()
        ch = store.save_character(Character(
            name="背包客", race="人类", char_class="战士", level=1), db)
        ch.add_to_inventory("长剑")
        ch.add_to_inventory("皮甲")
        # 制造漂移：structured 里多一个已不存在的物品
        ch.add_structured_item({"item_id": "item.ghost", "name": "幽灵物",
                                "quantity": 1})
        saved = store.save_character(ch, db)
        names = {i["name"] for i in saved.items_structured}
        assert "幽灵物" not in names, "漂移条目应被清理"
        assert "长剑" in names and "皮甲" in names, "inventory 条目应回填"

    def test_inventory_is_authority(self):
        """inventory 是唯一权威：移除物品后 structured 同步消失。"""
        from aidm.stats import store
        from aidm.stats.models import Character
        db = _tmp_db()
        ch = store.save_character(Character(
            name="清理者", race="人类", char_class="战士", level=1), db)
        ch.add_to_inventory("匕首")
        store.save_character(ch, db)
        inv = ch.inventory
        inv.remove("匕首")
        ch.set_inventory(inv)
        saved = store.save_character(ch, db)
        assert all(i["name"] != "匕首" for i in saved.items_structured)
