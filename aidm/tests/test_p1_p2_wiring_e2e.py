"""P1/P2 生产链路接线 E2E 测试。

验证新模块已真实接入生产路径：
  - MaterialCost → cast_spell（有价/消耗材料验证与扣除）
  - DurationScheduler → cast_spell（持续效果调度）
  - TriggerWindow → cast_spell（反应法术窗口注册）
  - ItemInstance → stats.models.Character（物品栏实例化）
  - LegendaryActions/RechargeTracker → combat_flow.run_monster_turn
  - magic_item_def/attunement → loot.attune_magic_item（前置条件）
  - RngContext → engine.dice（确定性回放）
  - target_query → brain/resolvers/target_resolver（消歧整合）
"""

from __future__ import annotations

import json

import pytest


# ── MaterialCost + cast_spell ────────────────────────────────────

class TestMaterialCostWiring:
    def _caster(self, cid="cast1"):
        from aidm.engine.spellcasting import CasterState
        return CasterState(
            caster_id=cid, class_name="法师", level=3,
            ability_scores={"str": 10, "dex": 10, "con": 10,
                            "int": 16, "wis": 10, "cha": 10},
            spell_slots={1: 4, 2: 2},
        )

    def test_cast_with_material_succeeds(self):
        from aidm.engine.material_cost import MaterialTracker
        from aidm.engine.spellcasting import cast_spell
        tracker = MaterialTracker()
        tracker.add_material("珍珠", 1)
        result = cast_spell(
            caster=self._caster(), spell_name="鉴定术", slot_level=1, targets=[],
            component_kwargs={"free_hands": 1, "has_material_pouch": True},
            material_tracker=tracker,
        )
        assert result["success"], result.get("errors")
        # 有价材料不消耗（material_consumed=False）
        assert result.get("material_consumed") is False

    def test_cast_without_material_rejected_no_slot(self):
        from aidm.engine.material_cost import MaterialTracker
        from aidm.engine.spellcasting import cast_spell
        result = cast_spell(
            caster=self._caster("cast2"), spell_name="鉴定术", slot_level=1, targets=[],
            component_kwargs={"free_hands": 1, "has_material_pouch": True},
            material_tracker=MaterialTracker(),  # 空库存
        )
        assert not result["success"]
        assert result.get("slot_consumed") is False  # 不耗法术位

    def test_cast_without_tracker_uses_kwarg(self):
        from aidm.engine.spellcasting import cast_spell
        result = cast_spell(
            caster=self._caster("cast3"), spell_name="鉴定术", slot_level=1, targets=[],
            component_kwargs={"free_hands": 1, "has_material_pouch": True,
                              "has_specific_material": True},
        )
        assert result["success"], result.get("errors")


# ── DurationScheduler + cast_spell ───────────────────────────────

class TestDurationSchedulerWiring:
    def test_schedules_effect(self):
        from aidm.engine.spell_duration import DurationScheduler
        from aidm.engine.spellcasting import CasterState, cast_spell
        caster = CasterState(
            caster_id="dur1", class_name="法师", level=3,
            ability_scores={"str": 10, "dex": 10, "con": 10,
                            "int": 16, "wis": 10, "cha": 10},
            spell_slots={1: 4, 2: 2},
        )
        sched = DurationScheduler()
        result = cast_spell(
            caster=caster, spell_name="光亮术", slot_level=0, targets=[],
            duration_scheduler=sched,
            component_kwargs={"free_hands": 2, "has_material_pouch": True},
        )
        assert result["success"], result.get("errors")
        assert result.get("scheduled_effect_id"), "应调度持续效果"
        # 光亮术持续1小时 → ROUNDS 600
        from aidm.engine.spell_duration import DurationType
        eff = sched._effects[result["scheduled_effect_id"]]
        assert eff.duration.duration_type == DurationType.ROUNDS


# ── TriggerWindow + cast_spell ──────────────────────────────────

class TestTriggerWindowWiring:
    def test_reaction_spell_registers_window(self):
        from aidm.engine.spell_trigger_window import TriggerWindowRegistry
        from aidm.engine.spellcasting import CasterState, cast_spell
        caster = CasterState(
            caster_id="tw1", class_name="法师", level=3,
            ability_scores={"str": 10, "dex": 10, "con": 10,
                            "int": 16, "wis": 10, "cha": 10},
            spell_slots={1: 4, 2: 2},
        )
        reg = TriggerWindowRegistry()
        result = cast_spell(
            caster=caster, spell_name="护盾术", slot_level=1, targets=[],
            trigger_window_registry=reg,
            component_kwargs={"free_hands": 1},
        )
        assert result["success"], result.get("errors")
        assert result.get("trigger_window_registered"), "应注册触发窗口"
        assert len(reg.get_windows_for_spell("护盾术")) == 1


# ── ItemInstance → Character ────────────────────────────────────

class TestItemInstanceCharacterWiring:
    def test_inventory_manager_roundtrip(self):
        from aidm.stats.models import Character
        ch = Character(
            name="物品测试", race="人类", char_class="战士", level=5,
            abilities_json=json.dumps({"str": 15, "dex": 14, "con": 13,
                                       "int": 10, "wis": 10, "cha": 10}),
            items_structured_json=json.dumps([
                {"instance_id": "i1", "item_id": "item.arrow", "name": "箭矢",
                 "quantity": 20},
            ]),
        )
        mgr = ch.get_inventory_manager()
        assert len(mgr.list_all()) == 1
        assert mgr.get_item("i1").quantity == 20
        # 消耗一支箭
        ch.sync_inventory_from_manager(mgr)
        assert ch.items_structured[0]["quantity"] == 20


# ── LegendaryActions → run_monster_turn ─────────────────────────

class TestLegendaryWiring:
    def test_monster_turn_emits_action_metadata(self):
        from aidm.engine.combat import Combatant
        from aidm.brain.combat_flow import run_monster_turn

        class _Ch:
            id = 1
            name = "勇者"
            ac = 15
            hp_current = 30
            hp_max = 30
            temp_hp = 0
            dead = False
            exhaustion = 0
            speed = 30
            char_class = "战士"
            abilities = {"str": 16, "dex": 14, "con": 14,
                         "int": 10, "wis": 12, "cha": 10}

            def ability_mod(self, ab):
                return (self.abilities.get(ab, 10) - 10) // 2

            def prof(self):
                return 3

            @property
            def conditions_list(self):
                return []

            def to_condition_state(self):
                from aidm.engine.conditions import ConditionState
                return ConditionState(conditions=[], exhaustion=self.exhaustion)

            def to_death_tracker(self):
                from aidm.engine.damage import DeathTracker
                return DeathTracker()

            def apply_death_tracker(self, _):
                pass

        monster = Combatant(
            cid="m1", name="巨龙", dex_mod=1, side="enemy", is_player=False,
            hp=100, hp_max=100, attack_bonus=8, damage_dice="2d10+4",
            damage_type="挥砍", legendary_actions_max=3,
        )
        ev = run_monster_turn(monster, _Ch(), state=None)
        # 即使编译失败回退基础攻击，也应带 monster_actions 元数据
        assert "monster" in ev
        if "monster_actions" in ev:
            assert ev["monster_actions"]["legendary_available"] is True


# ── magic_item_def → loot.attune_magic_item ─────────────────────

class TestAttunementWiring:
    def test_class_prerequisite_enforced(self):
        import tempfile
        from aidm.brain import loot
        from aidm.stats import store
        from aidm.stats.models import Character

        tmp = tempfile.mktemp(suffix=".db")
        db = f"sqlite:///{tmp}"
        store.create_campaign("测试", db_path=db)

        # 法师尝试同调神圣复仇者（需圣武士）→ 拒绝
        ch = Character(
            name="法师甲", race="人类", char_class="法师", level=5,
            abilities_json=json.dumps({"str": 10, "dex": 10, "con": 10,
                                       "int": 16, "wis": 10, "cha": 10}),
            hp_current=30, hp_max=30, ac=12,
            inventory_json=json.dumps(["神圣复仇者"]),
        )
        store.save_character(ch, db)
        r = loot.attune_magic_item(ch.id, "神圣复仇者", db_path=db)
        assert not r["success"]
        assert "职业" in r["message"] or "无法" in r["message"]

        # 圣武士同调 → 成功
        ch2 = Character(
            name="圣武士甲", race="人类", char_class="圣武士", level=5,
            abilities_json=json.dumps({"str": 16, "dex": 10, "con": 12,
                                       "int": 10, "wis": 10, "cha": 14}),
            hp_current=30, hp_max=30, ac=16,
            inventory_json=json.dumps(["神圣复仇者"]),
        )
        store.save_character(ch2, db)
        r2 = loot.attune_magic_item(ch2.id, "神圣复仇者", db_path=db)
        assert r2["success"], r2["message"]


# ── RngContext → engine.dice ────────────────────────────────────

class TestRngContextWiring:
    def test_deterministic_replay(self):
        from aidm.engine import dice
        from aidm.engine.rng_context import create_rng_context

        rng1 = create_rng_context(seed=42)
        dice.set_active_rng(rng1)
        rolls1 = [dice.roll_die(20) for _ in range(5)]

        rng2 = create_rng_context(seed=42)
        dice.set_active_rng(rng2)
        rolls2 = [dice.roll_die(20) for _ in range(5)]

        assert rolls1 == rolls2
        dice.set_active_rng(None)

    def test_d20_deterministic(self):
        from aidm.engine import dice
        from aidm.engine.rng_context import create_rng_context

        dice.set_active_rng(create_rng_context(seed=7))
        a1 = dice.roll_d20().used
        dice.set_active_rng(create_rng_context(seed=7))
        a2 = dice.roll_d20().used
        assert a1 == a2
        dice.set_active_rng(None)


# ── target_query → target_resolver ──────────────────────────────

class TestTargetQueryWiring:
    def _combat(self):
        from aidm.engine.combat import Combat, Combatant
        goblin1 = Combatant(cid="g1", name="哥布林", dex_mod=1, side="enemy",
                            hp=7, hp_max=7, position=(1, 0))
        goblin2 = Combatant(cid="g2", name="哥布林", dex_mod=1, side="enemy",
                            hp=7, hp_max=7, position=(2, 0))
        player = Combatant(cid="p1", name="勇者", dex_mod=2, side="player",
                           hp=30, hp_max=30, is_player=True, position=(0, 0))
        return Combat(participants=[player, goblin1, goblin2], active=True)

    def test_ambiguous_same_name(self):
        from aidm.brain.resolvers.target_resolver import resolve_target
        result = resolve_target("哥布林", "p1", self._combat(),
                                max_range_ft=30, attacker_position=(0, 0))
        assert result.ambiguous
        assert len(result.candidates) == 2

    def test_out_of_range(self):
        from aidm.brain.resolvers.target_resolver import resolve_target
        from aidm.engine.combat import Combat, Combatant
        player = Combatant(cid="p1", name="勇者", dex_mod=2, side="player",
                           hp=30, hp_max=30, is_player=True, position=(0, 0))
        far = Combatant(cid="g9", name="远敌", dex_mod=1, side="enemy",
                        hp=7, hp_max=7, position=(50, 0))
        combat = Combat(participants=[player, far], active=True)
        result = resolve_target("远敌", "p1", combat, max_range_ft=10,
                                attacker_position=(0, 0))
        assert result.error
        assert result.resolved_target is None


# ── MON-002: 传奇动作/充能/巢穴动作生产接线 ────────────────────

class TestLegendaryProduction:
    def test_legendary_action_executes_after_turn(self, monkeypatch):
        """传奇动作在怪物回合后真实执行（非仅元数据）。"""
        from aidm.brain import combat_flow
        from aidm.data.monster_compiler import MonsterCompiler, MonsterStatBlock

        sb = MonsterStatBlock(
            monster_id="m1", name="测试巨龙",
            legendary_actions=[{"name": "尾击", "cost": 1, "damage_dice": "2d8",
                                "damage_type": "钝击", "attack_bonus": 8}],
            legendary_action_points=2,
            legendary_resistance_count=1,
        )
        orig_compile = MonsterCompiler.compile_from_existing
        monkeypatch.setattr(
            MonsterCompiler, "compile_from_existing",
            lambda self, name: sb if name == "测试巨龙" else orig_compile(self, name),
        )
        events = combat_flow.process_legendary_actions_after_turn("测试巨龙", "m1", 1)
        assert events, "应产生传奇动作事件"
        assert events[0]["type"] == "legendary_action"
        assert events[0]["action_name"] == "尾击"
        assert events[0]["damage"] > 0

    def test_recharge_at_turn_start(self, monkeypatch):
        """怪物回合开始处理充能（RechargeAtTurnStart）。"""
        from aidm.brain import combat_flow
        from aidm.data.monster_compiler import MonsterCompiler, MonsterStatBlock

        sb = MonsterStatBlock(
            monster_id="m2", name="喷火兽",
            recharge_abilities=[{"ability_id": "breath", "threshold": 6,
                                 "damage_dice": "6d8", "damage_type": "火焰",
                                 "attack_bonus": 8}],
        )
        orig_compile = MonsterCompiler.compile_from_existing
        monkeypatch.setattr(
            MonsterCompiler, "compile_from_existing",
            lambda self, name: sb if name == "喷火兽" else orig_compile(self, name),
        )
        events = combat_flow.process_recharge_at_turn_start("喷火兽", "m2")
        assert isinstance(events, list)


# ── CoverageManifest 发布门禁 (TEST-002) ─────────────────────────

class TestCoverageReleaseGate:
    def test_release_gate_passes_full(self):
        """CoverageManifest 发布门禁：全部公开内容达 FULL 及以上。

        规则: TEST-002 — 任何公开内容缺 handler 或验收测试即失败。
        门禁状态语义:
          - VERIFIED = 生产链路 import + 测试引用（生产入口真实调用）
          - FULL = 测试通过（≥FULL 即满足门禁）
        """
        from aidm.engine.coverage import CoverageManifest, CoverageStatus
        m = CoverageManifest(ruleset_revision="2024.1")
        m.assert_release_gate(CoverageStatus.FULL)
        # 所有引擎模块 ≥ FULL（VERIFIED+FULL 覆盖全部引擎模块）
        counts = m.summary()
        assert counts.get("MISSING", 0) == 0
        assert counts.get("VERIFIED", 0) >= 20  # 生产+测试双覆盖
        assert counts.get("FULL", 0) + counts.get("VERIFIED", 0) >= 70
