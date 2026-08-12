"""API-001 真实乐观锁 E2E 测试。

验证:
  1. _check_version() 从 stub 改为真实校验 expected_combat_version
  2. 并发提交时仅一个成功，另一个收到 STALE_VERSION
  3. actor_id/turn_owner 校验（非当前回合参与者被拒）
  4. 数据库最终状态断言（版本号已持久化递增）
  5. end_turn 推进也递增版本号

运行:
  PYTHONPATH=src python -m pytest tests/test_api001_optimistic_lock.py -v
"""

from __future__ import annotations

import os
import sys
import tempfile

import pytest

from aidm.engine import combat as cmb
from aidm.stats import store
from aidm.api.routes.combat import (
    _check_action_permission,
    _check_version,
    submit_action,
)

CAMP = 9902


@pytest.fixture()
def combat_db(monkeypatch):
    """将 store 的 load/save 重定向到临时库，真实走路由全链路。"""
    db = _tmp_db()
    _orig_load = store.load_combat
    _orig_save = store.save_combat

    def _load(campaign_id, db_path=None):
        return _orig_load(campaign_id, db)

    def _save(campaign_id, combat, db_path=None):
        return _orig_save(campaign_id, combat, db)

    monkeypatch.setattr(store, "load_combat", _load)
    monkeypatch.setattr(store, "save_combat", _save)
    return db


def _tmp_db() -> str:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    return f"sqlite:///{path}"


def _mk_combat(db, player_name="勇者A", enemy_name="哥布林") -> cmb.Combat:
    """构建 A(先攻20) vs 哥布林(10) 的战斗并持久化。"""
    pa = cmb.Combatant(cid="pa1", name=player_name, initiative=20,
                       side="player", is_player=True, hp=30, hp_max=30)
    gob = cmb.Combatant(cid="gob1", name=enemy_name, initiative=10,
                        side="enemy", is_player=False, hp=7, hp_max=7)
    c = cmb.Combat(participants=[pa, gob], initiative_order=[pa, gob],
                   round=1, current_index=0, active=True)
    store.save_combat(CAMP, c, db)
    return c


# ── _check_version 单元级 ──────────────────────────────────────

class TestCheckVersion:
    def test_matching_version_passes(self):
        combat = cmb.Combat(version=5)
        _check_version(combat, expected_version=5)  # 不应抛异常

    def test_none_version_passes(self):
        combat = cmb.Combat(version=5)
        _check_version(combat, expected_version=None)  # 宽松放行

    def test_stale_version_raises(self):
        from fastapi import HTTPException
        combat = cmb.Combat(version=6)
        with pytest.raises(HTTPException) as exc:
            _check_version(combat, expected_version=5)
        assert exc.value.status_code == 409
        detail = exc.value.detail
        assert detail["error"] == "STALE_VERSION"
        assert detail["expected_version"] == 5
        assert detail["current_version"] == 6


# ── 并发场景全链路 ─────────────────────────────────────────────

class TestOptimisticLockE2E:
    def test_concurrent_submissions(self, combat_db):
        """两个并发提交携带同一版本 → 仅一个成功，另一个 STALE_VERSION。"""
        from fastapi import HTTPException
        db = combat_db
        combat = _mk_combat(db)

        # 读取当前版本
        loaded = store.load_combat(CAMP, db)
        v0 = loaded.version

        # 两个客户端同时基于 v0 提交
        from aidm.api.routes.combat import ActionRequest

        # 第一次提交（带 v0）→ 成功
        r1 = submit_action(CAMP, ActionRequest(
            player_id="勇者A", actor_id="pa1", command_type="MakeWeaponAttack",
            payload={"action_type": "attack", "target_name": "哥布林"},
            expected_version=v0,
        ))
        assert r1["status"] == "accepted"
        assert r1["combat_version"] == v0 + 1

        # 第二次提交（仍带 v0）→ STALE_VERSION
        with pytest.raises(HTTPException) as exc:
            submit_action(CAMP, ActionRequest(
                player_id="勇者A", actor_id="pa1", command_type="MakeWeaponAttack",
                payload={"action_type": "attack", "target_name": "哥布林"},
                expected_version=v0,
            ))
        assert exc.value.status_code == 409
        assert exc.value.detail["error"] == "STALE_VERSION"

        # 数据库最终状态断言：版本号已递增持久化
        final = store.load_combat(CAMP, db)
        assert final.version == v0 + 1

    def test_version_persists_after_roundtrip(self, combat_db):
        """版本号在 save→load 往返后保持不变（数据库最终状态）。"""
        db = combat_db
        combat = _mk_combat(db)
        loaded1 = store.load_combat(CAMP, db)
        v1 = loaded1.version

        # 再保存一次（不 bump）→ 版本不变
        store.save_combat(CAMP, loaded1, db)
        loaded2 = store.load_combat(CAMP, db)
        assert loaded2.version == v1

    def test_actor_turn_owner_validation(self, combat_db):
        """非当前回合参与者的 actor_id 被拒（NOT_YOUR_TURN）。"""
        from fastapi import HTTPException
        db = combat_db
        combat = _mk_combat(db)

        # 当前回合是 pa1（勇者A），用 gob1 的 actor_id → 拒绝
        with pytest.raises(HTTPException) as exc:
            _check_action_permission(CAMP, "勇者A", "gob1", combat)
        assert exc.value.status_code == 409
        assert exc.value.detail["error"] == "NOT_YOUR_TURN"

    def test_wrong_player_rejected(self, combat_db):
        """非当前回合的玩家被拒。"""
        from fastapi import HTTPException
        db = combat_db
        combat = _mk_combat(db)

        with pytest.raises(HTTPException) as exc:
            _check_action_permission(CAMP, "另一个玩家", "pa1", combat)
        assert exc.value.status_code == 409

    def test_end_turn_bumps_version(self, combat_db):
        """end_turn 推进回合也递增版本号。"""
        db = combat_db
        combat = _mk_combat(db)
        v0 = combat.version

        from aidm.api.routes.combat import end_turn
        r = end_turn(CAMP, "勇者A")
        assert r["status"] == "turn_ended"
        assert r["combat_version"] == v0 + 1

        # 数据库最终状态
        final = store.load_combat(CAMP, db)
        assert final.version == v0 + 1
