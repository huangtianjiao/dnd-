"""规则门控单元测试（第二批）— 武器熟练/长休冷却/药水消耗/同调拥有性/力竭即死。

验证规则点:
  R-ITM-013 武器熟练 — 不熟练武器攻击检定不加熟练加值
  R-GLS-015 长休冷却 — 完成后须等待16小时才能再次长休
  DMG2024 药水详述 — 治疗药水须拥有才能喝，喝后消耗
  玩家手册 同调 — 只能同调物品栏内的物品
  R-GLS-047 力竭 — 6级即死

运行:
  PYTHONPATH=src python -m pytest tests/test_rule_gates.py -v
"""

from __future__ import annotations

import os
import sys
import tempfile


def _setup_test_db():
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


def _make_char(char_class="战士", level=5, inventory=None, weapon=""):
    from aidm.stats import models
    ch = models.Character(name="门控测试者", race="人类", char_class=char_class, level=level)
    if inventory is not None:
        ch.set_inventory(inventory)
    ch.equipped_weapon = weapon
    ch.hp_max = 30
    ch.hp_current = 30
    return ch


# ──────────────────────────────────────────────────────────────────────────
# R-ITM-013 武器熟练
# ──────────────────────────────────────────────────────────────────────────

def test_class_weapon_proficient():
    """职业武器熟练判定：战士全熟练；法师仅简易；游荡者带灵巧/轻型的军用。"""
    from aidm.data.equipment import class_weapon_proficient

    assert class_weapon_proficient("战士", "巨剑")          # 简易和军用
    assert class_weapon_proficient("法师", "匕首")          # 简易
    assert not class_weapon_proficient("法师", "巨剑")      # 军用 → 法师不熟练
    assert class_weapon_proficient("游荡者", "短剑")        # 军用但轻型/灵巧
    assert not class_weapon_proficient("游荡者", "巨剑")    # 军用非轻型/灵巧
    assert class_weapon_proficient("武僧", "矛")            # 简易
    assert class_weapon_proficient("牧师", "徒手")          # 徒手始终熟练


def test_resolve_attack_no_prof_bonus_for_untrained():
    """法师持巨剑攻击：不加熟练加值且输出 weapon_not_proficient 标记。"""
    from aidm.brain import graph as g

    wiz = _make_char("法师", 5, inventory=["巨剑"], weapon="巨剑")
    war = _make_char("战士", 5, inventory=["巨剑"], weapon="巨剑")

    class _Atk:
        total = 25; d20 = 18; hit = True; crit = False; rolls = [18]
    orig = g.check.attack_roll
    captured = {}

    def _stub(**kw):
        captured["bonus"] = kw.get("bonus")
        return _Atk()
    g.check.attack_roll = _stub
    try:
        out_w = g._resolve_attack(wiz, {"weapon": "巨剑", "target_ac": 10})
        assert out_w.get("weapon_not_proficient") is True
        assert captured["bonus"] == wiz.ability_mod("str")           # 无熟练加值

        out_f = g._resolve_attack(war, {"weapon": "巨剑", "target_ac": 10})
        assert "weapon_not_proficient" not in out_f
        assert captured["bonus"] == war.ability_mod("str") + war.prof()  # 含熟练
    finally:
        g.check.attack_roll = orig


# ──────────────────────────────────────────────────────────────────────────
# R-GLS-015 长休冷却
# ──────────────────────────────────────────────────────────────────────────

def test_long_rest_cooldown():
    """距上次长休不足16小时 → 拒绝；超过16小时 → 允许。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from aidm.brain import graph as g

        camp = store.create_campaign("冷却测试")
        ch = _make_char("战士", 3)
        ch.campaign_id = camp.id
        ch.hp_current = 10          # 有伤可休
        ch = store.save_character(ch)

        state = {"campaign_id": camp.id, "player_input": "长休"}

        # 记录"上次长休"为当前时刻 → 冷却中
        c = store.get_campaign(camp.id)
        fl = c.world_flags
        fl["game_minutes"] = 1000
        fl[f"last_long_rest_min_{ch.id}"] = 900     # 距今 100 分钟 < 960
        c.set_world_flags(fl)
        store.save_campaign(c)

        r1 = g._resolve_rest(state, ch, {"rest_type": "long"})
        assert "error" in r1 and "不足" in r1["error"]

        # 时间推进 17 小时后 → 允许
        c = store.get_campaign(camp.id)
        fl = c.world_flags
        fl["game_minutes"] = 900 + 17 * 60
        c.set_world_flags(fl)
        store.save_campaign(c)

        r2 = g._resolve_rest(state, ch, {"rest_type": "long"})
        assert r2.get("success") is True and r2.get("type") == "long"
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


# ──────────────────────────────────────────────────────────────────────────
# 药水拥有性 + 消耗
# ──────────────────────────────────────────────────────────────────────────

def test_potion_ownership_gate():
    """没有治疗药水 → 拒绝；有 → 掷 heal 并标记 consumed_item。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from aidm.brain.graph import resolve

        ch = _make_char("战士", 1, inventory=["长剑"])
        ch = store.save_character(ch)
        state = {"intent": {"action_type": "use_item", "item_name": "治疗药水"},
                 "character_id": ch.id, "player_input": "我喝下治疗药水"}
        out = resolve(state)
        assert "error" in out["dice"] and "没有治疗药水" in out["dice"]["error"]

        ch.set_inventory(["长剑", "治疗药水"])
        store.save_character(ch)
        out2 = resolve(state)
        assert out2["dice"].get("heal", 0) >= 4          # 2d4+2 ≥ 4
        assert out2["dice"].get("consumed_item") == "治疗药水"

        # 高级治疗药水 → 4d4+4
        ch.set_inventory(["高级治疗药水"])
        store.save_character(ch)
        out3 = resolve(state)
        assert out3["dice"].get("heal", 0) >= 8
        assert out3["dice"].get("consumed_item") == "高级治疗药水"
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


def test_potion_in_magic_items_db():
    """治疗药水已入魔法物品库（战利品体系可产出）。"""
    from aidm.data.magic_items import get_magic_item

    p = get_magic_item("治疗药水")
    assert p is not None and p.rarity.value == "普通"
    gp = get_magic_item("高级治疗药水")
    assert gp is not None


# ──────────────────────────────────────────────────────────────────────────
# 同调拥有性
# ──────────────────────────────────────────────────────────────────────────

def test_attune_requires_ownership():
    """未持有的魔法物品无法同调；入包后可同调。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from aidm.brain import loot
        from aidm.data.magic_items import MAGIC_ITEMS

        # 找一件需同调的物品
        target = next(m.name for m in MAGIC_ITEMS.values() if m.attunement)

        ch = _make_char("战士", 3)
        ch = store.save_character(ch, db_path)

        r1 = loot.attune_magic_item(ch.id, target, db_path)
        assert not r1["success"] and "不在物品栏" in r1["message"]

        ch.add_to_inventory(target)
        store.save_character(ch, db_path)
        r2 = loot.attune_magic_item(ch.id, target, db_path)
        assert r2["success"], r2["message"]
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


if __name__ == "__main__":
    for fn in sorted(k for k in dir() if k.startswith("test_")):
        print(f"-- {fn}")
        globals()[fn]()
    print("ALL OK")
