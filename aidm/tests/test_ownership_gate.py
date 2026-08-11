"""拥有性门控单元测试 — 武器须拥有、法术须学会才可使用。

验证规则点:
  R-SPL-036 职业法术列表 — 只能施展本职业法术列表内且环阶可及的法术
  R-SPL-001 法术环阶 — 环阶不超过当前等级可用最高法术位环
  R-ITM-012 武器表 — 攻击/装备只认角色拥有的武器

覆盖:
  - data.spells.default_known_spells 职业/环阶过滤
  - 角色创建三入口初始化 known_spells + 起始武器入包
  - graph._resolve_cast 拒绝未学会法术（含历史角色动态回退）
  - graph._resolve_attack 未拥有武器降级为已装备武器
  - POST /equip-weapon 拒绝未拥有武器 + 懒回填
  - GET /character/{cid}/inventory 返回拥有武器列表

运行:
  PYTHONPATH=src python -m pytest tests/test_ownership_gate.py -v
"""

from __future__ import annotations

import os
import sys
import tempfile

_SRC = os.path.join(os.path.dirname(__file__), "..", "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)


def _setup_test_db():
    """创建临时数据库并 patch store 模块（与 test_api_endpoints.py 一致）。"""
    tmpdir = tempfile.mkdtemp(prefix="aidm_test_")
    db_path = f"sqlite:///{tmpdir}/test.db"

    from aidm.stats import store
    orig_default = store.DEFAULT_DB
    orig_engines = store._engines.copy()

    store.DEFAULT_DB = db_path
    store._engines.clear()
    store.get_engine(db_path)

    return db_path, orig_default, orig_engines, store


def _teardown_test_db(orig_default, orig_engines, store):
    store.DEFAULT_DB = orig_default
    store._engines.clear()
    store._engines.update(orig_engines)


# ──────────────────────────────────────────────────────────────────────────
# default_known_spells 数据函数
# ──────────────────────────────────────────────────────────────────────────

def test_default_known_spells_wizard_l1():
    """1级法师：含法师戏法与1环法术，不含高环/他职业专属法术。"""
    from aidm.data.spells import default_known_spells

    known = default_known_spells("法师", 1)
    assert "火焰箭" in known or "冷冻射线" in known   # 法师戏法/1环
    assert "火球术" not in known                       # 3环，1级不可及
    assert all(isinstance(n, str) for n in known)
    assert len(known) > 0


def test_default_known_spells_ring_gate():
    """5级法师可及3环 → 火球术进入已学表。"""
    from aidm.data.spells import default_known_spells

    known5 = default_known_spells("法师", 5)
    assert "火球术" in known5


def test_default_known_spells_class_gate():
    """牧师表不含法师专属法术（魔法飞弹）；非施法职业返回空。"""
    from aidm.data.spells import default_known_spells

    cleric = default_known_spells("牧师", 5)
    assert "魔法飞弹" not in cleric      # class_list=("术士","法师")
    assert "治疗真言" in cleric or "疗伤术" in cleric
    assert default_known_spells("战士", 5) == []
    assert default_known_spells("野蛮人", 20) == []


# ──────────────────────────────────────────────────────────────────────────
# 角色创建初始化
# ──────────────────────────────────────────────────────────────────────────

def test_character_creation_initializes_loadout():
    """POST /character：施法者获得 known_spells；起始武器写入 inventory。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from fastapi.testclient import TestClient
        from aidm.api.main import app

        client = TestClient(app)
        r = client.post("/character", json={
            "name": "门控法师", "race": "人类", "char_class": "法师", "level": 1})
        assert r.status_code == 200
        cid = r.json()["id"]

        ch = store.get_character(cid)
        assert len(ch.known_spells) > 0                     # 已学法术已初始化
        assert ch.equipped_weapon                           # 有起始武器
        assert ch.equipped_weapon in ch.inventory           # 起始武器已入包

        # 非施法职业不给法术
        r2 = client.post("/character", json={
            "name": "门控战士", "race": "人类", "char_class": "战士", "level": 1})
        ch2 = store.get_character(r2.json()["id"])
        assert ch2.known_spells == []
        assert ch2.equipped_weapon in ch2.inventory
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


# ──────────────────────────────────────────────────────────────────────────
# graph 判定链门控
# ──────────────────────────────────────────────────────────────────────────

def _make_char(char_class="法师", level=5, known=None, inventory=None, weapon=""):
    from aidm.stats import models
    from aidm.data import spells as sp

    ch = models.Character(name="测试者", race="人类", char_class=char_class, level=level)
    if char_class in ("法师", "牧师", "术士", "吟游诗人", "德鲁伊", "圣武士", "游侠", "魔契师"):
        ch.set_spell_slots({str(k): v for k, v in sp.max_spell_slots(level).items()})
    if known is not None:
        ch.set_known_spells(known)
    if inventory is not None:
        ch.set_inventory(inventory)
    ch.equipped_weapon = weapon
    return ch


def test_resolve_cast_rejects_unlearned_spell():
    """已显式设置 known_spells 的角色：表外法术被拒。"""
    from aidm.brain.graph import _resolve_cast

    ch = _make_char("法师", 5, known=["火焰箭"])
    out = _resolve_cast(ch, {"spell_name": "火球术", "spell_level": 3})
    assert "error" in out
    assert "尚未学会" in out["error"]

    ok = _resolve_cast(ch, {"spell_name": "火焰箭"})
    assert "error" not in ok


def test_resolve_cast_legacy_fallback():
    """SPL-003: 历史角色 known_spells 为空 → 不再回退职业默认表，
    空 known_spells 意味着角色不会任何法术（如非施法职业或未初始化）。
    所有法术均被拒绝。"""
    from aidm.brain.graph import _resolve_cast

    ch = _make_char("法师", 5, known=[])
    # SPL-003: 空 known_spells → 任何法术都被拒绝
    bad = _resolve_cast(ch, {"spell_name": "火球术", "spell_level": 3})
    assert "error" in bad
    assert "尚未学会" in bad["error"]

    bad2 = _resolve_cast(ch, {"spell_name": "治疗真言", "spell_level": 1})
    assert "error" in bad2
    assert "尚未学会" in bad2["error"]


def test_resolve_attack_substitutes_unowned_weapon():
    """攻击指定未拥有武器 → 降级为已装备武器并标记 weapon_substituted。"""
    from aidm.brain import graph as g

    ch = _make_char("战士", 5, inventory=["长剑"], weapon="长剑")

    # 强制命中：attack_roll 打桩
    class _Atk:
        total = 25; d20 = 18; hit = True; crit = False; rolls = [18]
    orig = g.check.attack_roll
    g.check.attack_roll = lambda **kw: _Atk()
    try:
        out = g._resolve_attack(ch, {"weapon": "巨斧", "target_ac": 10})
        assert out["weapon"] == "长剑"                  # 降级为实际拥有武器
        assert out["weapon_substituted"] == "巨斧"

        out2 = g._resolve_attack(ch, {"weapon": "长剑", "target_ac": 10})
        assert out2["weapon"] == "长剑"
        assert "weapon_substituted" not in out2         # 拥有 → 不降级
    finally:
        g.check.attack_roll = orig


# ──────────────────────────────────────────────────────────────────────────
# API 端点门控
# ──────────────────────────────────────────────────────────────────────────

def test_equip_weapon_ownership_gate():
    """POST /equip-weapon：未拥有武器 400 not_owned；拥有武器可装备。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from fastapi.testclient import TestClient
        from aidm.api.main import app

        client = TestClient(app)
        r = client.post("/character", json={
            "name": "门控骑士", "race": "人类", "char_class": "战士", "level": 1})
        cid = r.json()["id"]

        # 未拥有 → 400 not_owned
        r2 = client.post(f"/character/{cid}/equip-weapon", json={"weapon_name": "巨剑"})
        assert r2.status_code == 400
        assert r2.json()["detail"]["error"] == "not_owned"

        # 拾取入包后 → 可装备
        ch = store.get_character(cid)
        ch.add_to_inventory("巨剑")
        store.save_character(ch)
        r3 = client.post(f"/character/{cid}/equip-weapon", json={"weapon_name": "巨剑"})
        assert r3.status_code == 200
        assert r3.json()["equipped_weapon"] == "巨剑"

        # inventory 端点返回拥有武器（含 equipped 标记）
        r4 = client.get(f"/character/{cid}/inventory")
        weapons = {w["name"]: w for w in r4.json()["weapons"]}
        assert "巨剑" in weapons and weapons["巨剑"]["equipped"]
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


def test_equip_weapon_legacy_backfill():
    """历史角色 inventory 未含起始武器 → 懒回填后仍可重新装备它。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from fastapi.testclient import TestClient
        from aidm.api.main import app
        from aidm.stats import models

        # 直接落库模拟历史角色（绕过 /character 的 _init_loadout）
        ch = models.Character(name="老角色", race="人类", char_class="战士", level=3)
        ch.equipped_weapon = "长剑"
        ch = store.save_character(ch)
        assert ch.inventory == []

        client = TestClient(app)
        r = client.post(f"/character/{ch.id}/equip-weapon", json={"weapon_name": "长剑"})
        assert r.status_code == 200
        ch2 = store.get_character(ch.id)
        assert "长剑" in ch2.inventory           # 懒回填生效
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


if __name__ == "__main__":
    for fn in sorted(k for k in dir() if k.startswith("test_")):
        print(f"-- {fn}")
        globals()[fn]()
    print("ALL OK")
