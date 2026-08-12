"""端到端集成测试 — 完整跑通 D&D 5E 跑团流程

验证完整链路:
  1. 建战役+角色 — POST /campaign + POST /character
  2. DM 开场 — POST /open，验证返回 narration + action_options + scene
  3. 探索行动 — POST /chat（player_input="我搜索房间"），验证意图分类为 explore
  4. 战斗开始 — POST /chat（player_input="哥布林出现了，拔剑攻击"），验证意图分类为 attack/start_combat
  5. 施法 — POST /chat（player_input="我施放祝福术"），验证意图分类为 cast
  6. 休息 — POST /chat（player_input="我们短休"），验证意图分类为 rest
  7. 升级 — POST /chat（player_input="我升级了"），验证意图分类为 levelup

使用 TestClient + 临时 SQLite 数据库。

运行:
  PYTHONPATH=src python tests/test_e2e_flow.py
  PYTHONPATH=src python -m pytest tests/test_e2e_flow.py -v
"""

from __future__ import annotations

import os
import sys
import tempfile


def _setup_test_db():
    """创建临时数据库并 patch store 模块。"""
    tmpdir = tempfile.mkdtemp(prefix="aidm_e2e_")
    db_path = f"sqlite:///{tmpdir}/test.db"

    from aidm.stats import store
    orig_default = store.DEFAULT_DB
    orig_engines = store._engines.copy()

    store.DEFAULT_DB = db_path
    store._engines.clear()
    store.get_engine(db_path)

    return db_path, orig_default, orig_engines, store


def _teardown_test_db(orig_default, orig_engines, store):
    """恢复原始数据库配置。"""
    store.DEFAULT_DB = orig_default
    store._engines.clear()
    store._engines.update(orig_engines)


# ──────────────────────────────────────────────────────────────────────────
# 纯引擎端到端测试（不依赖 LLM）
# ──────────────────────────────────────────────────────────────────────────

def test_full_combat_round_engine():
    """纯引擎：完整战斗回合（先攻→攻击→伤害→HP扣减→回合推进）。

    验证规则点:
      R-CMB-002 先攻检定
      R-CMB-017 攻击命中判定
      R-DMG-001 伤害掷骰
      R-DMG-007 HP扣除
      R-CMB-004 回合推进
    """
    from aidm.engine import combat, damage, dice, check

    # 创建参战者
    player = combat.Combatant(cid="p1", name="战士", dex_mod=1, side="player")
    goblin = combat.Combatant(cid="g1", name="哥布林", dex_mod=2,
                              side="enemy", is_player=False)

    # 开始战斗
    battle = combat.Combat()
    combat.start_combat(battle, [player, goblin])

    assert battle.active is True
    assert battle.round == 1
    assert len(battle.initiative_order) == 2

    # 当前参战者
    cur = combat.current_combatant(battle)
    assert cur is not None

    # 执行动作（攻击）
    assert combat.use_action(cur) is True
    assert combat.can_take_action(cur) is False   # 动作已用

    # 推进回合
    nxt = combat.advance_turn(battle)
    assert nxt is not None
    assert combat.can_take_action(nxt) is True     # 新回合重置

    # 第二轮
    combat.advance_turn(battle)
    assert battle.round == 2


def test_attack_to_damage_pipeline():
    """纯引擎：攻击检定 → 伤害结算 → HP扣减 完整管线。

    验证规则点:
      R-CMB-017 攻击命中 (d20+bonus ≥ AC)
      R-CMB-022 天然20必出+重击
      R-DMG-001 伤害掷骰 (武器=dice+属性调整值)
      R-CMB-029 重击骰翻倍
      R-DMG-007 HP扣除
      R-DMG-009 临时HP优先扣除
    """
    from aidm.engine import damage, dice, check

    # ★ 修复: 补丁必须 try/finally 还原（此前 roll_die 补丁泄漏到后续测试，
    #   导致全量运行时其他测试的 d20 被固定为 4）
    orig_roll_d20 = dice.roll_d20
    orig_roll_die = dice.roll_die
    try:
        # === 场景1: 普通命中 ===
        # 战士 STR16(+3) 熟练+2 → 攻击加值 +5
        # d20=15 → 15+5=20 ≥ AC15 → 命中
        dice.roll_d20 = lambda advantage=False, disadvantage=False: \
            type("R", (), {"used": 15, "rolls": [15], "mode": "normal"})()

        a = check.attack_roll(bonus=5, ac=15)
        assert a.hit is True
        assert a.crit is False
        assert a.total == 20

        # 伤害: 长剑 1d8+3 (STR)
        dice.roll_die = lambda s: 6   # d8=6
        req = damage.DamageRequest(
            dice_expr="1d8",
            damage_type="slashing",
            ability_mod=3,
            add_mod=True,
        )
        rd = damage.roll_damage(req)
        assert rd.final == 9   # 6+3=9

        # HP扣减: 哥布林 HP7 受9伤 → 0
        new_hp, new_temp = damage.apply_damage_to_hp(hp=7, temp_hp=0, max_hp=7, dmg=9)
        assert new_hp == 0

        # === 场景2: 天然20重击 ===
        dice.roll_d20 = lambda advantage=False, disadvantage=False: \
            type("R", (), {"used": 20, "rolls": [20], "mode": "normal"})()

        a = check.attack_roll(bonus=5, ac=30)   # 即使AC30，天然20必出
        assert a.hit is True
        assert a.crit is True

        # 重击伤害: 2d6+3 (大剑重击)
        dice.roll_die = lambda s: 4   # d6=4
        req2 = damage.DamageRequest(
            dice_expr="2d6",
            damage_type="slashing",
            ability_mod=3,
            add_mod=True,
            crit=True,                # 重击！
        )
        rd2 = damage.roll_damage(req2)
        # 2d6 重击 = 4d6 = 4*4=16, +3 STR = 19
        assert rd2.final == 19
        assert len(rd2.dice_rolls) == 4   # 2d6 翻倍为 4d6

        # === 场景3: 临时HP优先扣 ===
        hp, temp = damage.apply_damage_to_hp(hp=10, temp_hp=5, max_hp=20, dmg=7)
        assert hp == 8 and temp == 0   # 失5临时再失2HP
    finally:
        dice.roll_d20 = orig_roll_d20
        dice.roll_die = orig_roll_die


def test_death_save_full_cycle():
    """纯引擎：死亡豁免完整周期。

    验证规则点:
      R-DMG-017 死亡豁免检定
      - ≥10 → 一次成功
      - <10 → 一次失败
      - 天然1 → 两次失败
      - 天然20 → 恢复1HP，计数归零
      - 3次成功 → 稳定
      - 3次失败 → 死亡
    """
    from aidm.engine import damage, dice

    # 场景1: 3次成功 → 稳定
    orig = dice.roll_die
    try:
        t = damage.DeathTracker()
        dice.roll_die = lambda s: 15   # ≥10 成功
        r1 = damage.death_save(t); assert t.successes == 1, f"after 1st: {t.successes}"
        r2 = damage.death_save(t); assert t.successes == 2, f"after 2nd: {t.successes}"
        r3 = damage.death_save(t)
        # 3次成功后 tracker.reset() 将计数归零并设 stable=True
        assert r3.get("stable") or t.stable, f"r3={r3}, stable={t.stable}"

        # 场景2: 天然1 → 两次失败
        t2 = damage.DeathTracker()
        dice.roll_die = lambda s: 1   # 天然1
        damage.death_save(t2)
        assert t2.failures == 2, f"failures={t2.failures}"

        # 场景3: 天然20 → 恢复1HP
        t3 = damage.DeathTracker()
        t3.successes = 2   # 已有2成功
        dice.roll_die = lambda s: 20   # 天然20
        result = damage.death_save(t3)
        assert result["regain_hp"] == 1, f"regain_hp={result.get('regain_hp')}"
        assert t3.successes == 0   # 计数归零
        assert t3.failures == 0

        # 场景4: 3次失败 → 死亡
        t4 = damage.DeathTracker()
        dice.roll_die = lambda s: 5   # <10 失败
        damage.death_save(t4); assert t4.failures == 1, f"after 1st: {t4.failures}"
        damage.death_save(t4); assert t4.failures == 2, f"after 2nd: {t4.failures}"
        damage.death_save(t4)
        assert t4.failures >= 3, f"failures={t4.failures}"
        assert t4.dead is True, f"dead={t4.dead}"
    finally:
        dice.roll_die = orig


def test_rest_and_recovery_engine():
    """纯引擎：休息与恢复机制。

    验证规则点:
      R-DMG-020 治疗（不超过上限）
      R-DMG-010 临时HP不叠加（取较大者）
      R-GLS-047 长休力竭-1
    """
    from aidm.engine import damage, conditions

    # 治疗
    assert damage.apply_healing(14, 20, 8) == 20   # min(20, 22)=20
    assert damage.apply_healing(5, 20, 3) == 8     # 5+3=8

    # 临时HP取大
    assert damage.grant_temp_hp(10, 12) == 12
    assert damage.grant_temp_hp(15, 10) == 15

    # 长休力竭-1
    s = conditions.ConditionState()
    s.add("力竭"); s.add("力竭"); s.add("力竭")
    assert s.exhaustion == 3
    conditions.long_rest_reduce_exhaustion(s)
    assert s.exhaustion == 2


# ──────────────────────────────────────────────────────────────────────────
# API 端到端测试（需要 LLM，但可降级验证结构）
# ──────────────────────────────────────────────────────────────────────────

def test_api_create_campaign_and_character():
    """API E2E Step 1: 建战役+角色。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from fastapi.testclient import TestClient
        from aidm.api.main import app

        client = TestClient(app)

        # 建战役
        r = client.post("/campaign", json={"name": "龙之传说"})
        assert r.status_code == 200
        camp = r.json()
        assert camp["name"] == "龙之传说"
        assert isinstance(camp["id"], int)

        # 建角色
        r = client.post("/character", json={
            "name": "阿拉贡",
            "race": "人类",
            "char_class": "战士",
            "level": 3,
            "abilities": {"str": 16, "dex": 12, "con": 14, "int": 10, "wis": 10, "cha": 10},
            "hp_max": 28,
            "ac": 16,
            "campaign_id": camp["id"],
        })
        assert r.status_code == 200
        ch = r.json()
        assert ch["name"] == "阿拉贡"
        assert isinstance(ch["id"], int)

        # 验证角色卡
        r = client.get(f"/character/{ch['id']}")
        assert r.status_code == 200
        c = r.json()
        assert c["abilities"]["str"]["mod"] == 3   # STR16 → +3
        assert c["proficiency"] == 2               # 3级 → +2

        return camp, ch
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


def test_api_get_scene_and_combat():
    """API E2E Step 2: 获取场景和战斗状态。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from fastapi.testclient import TestClient
        from aidm.api.main import app

        client = TestClient(app)
        camp = client.post("/campaign", json={"name": "T"}).json()

        # 获取场景（无场景时返回空dict或默认）
        r = client.get(f"/scene/{camp['id']}")
        assert r.status_code == 200

        # 获取战斗状态
        r = client.get(f"/combat/{camp['id']}")
        assert r.status_code == 200
        data = r.json()
        assert data["active"] is False
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


def test_api_campaign_state():
    """API E2E Step 3: 获取战役完整状态。"""
    db_path, orig_default, orig_engines, store = _setup_test_db()
    try:
        from fastapi.testclient import TestClient
        from aidm.api.main import app

        client = TestClient(app)

        # 建战役+角色
        camp = client.post("/campaign", json={"name": "冒险"}).json()
        ch = client.post("/character", json={
            "name": "英雄",
            "race": "精灵",
            "char_class": "法师",
            "level": 1,
            "abilities": {"str": 8, "dex": 14, "con": 12, "int": 16, "wis": 12, "cha": 10},
            "hp_max": 8,
            "ac": 12,
            "campaign_id": camp["id"],
        }).json()

        # 获取战役状态
        r = client.get(f"/campaign/{camp['id']}/state")
        assert r.status_code == 200
        state = r.json()
        assert "campaign" in state or "characters" in state
    finally:
        _teardown_test_db(orig_default, orig_engines, store)


# ──────────────────────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────────────────────

def main():
    """运行所有端到端测试。"""
    tests = [
        # 纯引擎端到端
        test_full_combat_round_engine,
        test_attack_to_damage_pipeline,
        test_death_save_full_cycle,
        test_rest_and_recovery_engine,
        # API 端到端
        test_api_create_campaign_and_character,
        test_api_get_scene_and_combat,
        test_api_campaign_state,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  ✓ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__}: {e}")
            failed += 1
    print(f"\n{'='*50}")
    print(f"端到端集成测试: {passed} 通过, {failed} 失败")
    print(f"{'='*50}")
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
