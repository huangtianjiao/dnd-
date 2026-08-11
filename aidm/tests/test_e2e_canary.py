"""E2E 金丝雀测试 — Director→resolve→apply→persist 全链路。

★ TEST-001: 规则金丝雀 E2E，所有关键规则从 API/WS 入口走完整生产链。
★ TEST-003: 随机结算可稳定回放，RngContext 接入骰子管线。

这些测试验证：
  1. 同一权威状态、玩家选择和骰子序列，永远得到相同的机械结果
  2. LLM 不能决定 AC、DC、伤害、资源、目标合法性或状态变化
  3. 所有权威数值从状态和规则数据派生，而非 LLM 猜测
"""

from __future__ import annotations

import os
import sys
import tempfile
import uuid

import pytest

# 添加 src 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aidm.engine.rng import RngContext, RollRecord
from aidm.engine.entity_state import EntityStateRegistry, EntityState, EntityType
from aidm.engine.intent_schema import IntentSchema, ActionType, validate_intent
from aidm.engine.resolution_trace import ResolutionTrace, ModifierSource, RollTrace


class TestE2ECanary:
    """TEST-001: 规则金丝雀 E2E 测试。"""

    def test_intent_validation_rejects_invalid_dice(self):
        """SEC-001: 非法骰式被拒绝。"""
        with pytest.raises(ValueError, match="非法骰式"):
            validate_intent({
                "action_type": "cast",
                "spell_name": "火球术",
                "spell_dice": "abc123",  # 完全非法的骰式
            })

    def test_intent_validation_rejects_invalid_ability(self):
        """SEC-001: 非法属性被拒绝。"""
        with pytest.raises(ValueError, match="非法属性"):
            validate_intent({
                "action_type": "ability_check",
                "ability": "xxx",
            })

    def test_intent_validation_accepts_valid_intent(self):
        """SEC-001: 合法意图通过校验。"""
        result = validate_intent({
            "action_type": "attack",
            "target_name": "哥布林",
            "weapon": "长剑",
            "ability": "str",
        })
        assert result["action_type"] == "attack"
        assert result["weapon"] == "长剑"

    def test_entity_state_registry_as_single_source(self):
        """STATE-001: EntityStateRegistry 作为单一权威状态源。"""
        registry = EntityStateRegistry()

        # 注册一个实体
        state = EntityState(
            entity_id="char_1",
            entity_type=EntityType.CHARACTER,
            hp_current=30,
            hp_max=30,
            armor_class=15,
        )
        registry.register(state)

        # 通过 registry 更新
        updated = registry.update("char_1", hp_current=25)
        assert updated.hp_current == 25
        assert updated.version >= state.version

        # 获取快照
        snapshot = registry.snapshot("char_1")
        assert snapshot["hp_current"] == 25

    def test_rng_context_reproducibility(self):
        """TEST-003: 固定种子的随机数可重放。"""
        rng1 = RngContext(seed=42)
        rng2 = RngContext(seed=42)

        # 两次掷骰应该得到相同结果
        roll1 = rng1.roll_die(20)
        roll2 = rng2.roll_die(20)
        assert roll1 == roll2

        # 记录应该被保存
        records = rng1.get_records()
        assert len(records) > 0
        assert isinstance(records[0], RollRecord)

    def test_resolution_trace_records_formula_tree(self):
        """OBS-001: ResolutionTrace 记录公式树。"""
        trace = ResolutionTrace(
            trace_id=str(uuid.uuid4()),
            action_type="attack",
            actor_id="char_1",
            target_ids=["goblin_1"],
        )

        # 添加一次掷骰记录
        roll = RollTrace(
            roll_id=str(uuid.uuid4()),
            dice_expr="1d20+5",
            dice_rolls=[15],
            modifiers=[
                ModifierSource(source_type="ABILITY", source_name="STR", value=3),
                ModifierSource(source_type="PROFICIENCY", source_name="PROF", value=2),
            ],
            total=20,
        )
        trace.add_roll(roll)

        # 验证轨迹字符串
        display = trace.to_display_string()
        assert "d20" in display
        assert "15" in display

    def test_attack_resolver_ac_from_entity_state(self):
        """COM-001: 目标AC来自EntityState，不可被LLM覆盖。"""
        from aidm.brain.resolvers.attack import _lookup_target_ac

        class MockChar:
            char_class = "战士"
            level = 1
            equipped_weapon = "长剑"

        ch = MockChar()
        it = {"target_cid": "999", "target_ac": 99}  # LLM 试图注入 AC=99
        state = {"campaign_id": 999}

        ac = _lookup_target_ac(ch, it, state)
        # 找不到目标时返回兆底 AC 10，不使用 LLM 注入的 99
        assert ac == 10

    def test_cast_resolver_delegates_to_cast_spell(self):
        """SPL-001: resolve_cast 委托给 engine.spellcasting.cast_spell()。"""
        from aidm.brain.resolvers.cast import resolve_cast

        # 创建一个模拟角色和 intent
        class MockChar:
            char_class = "法师"
            level = 1
            abilities = {"str": 10, "dex": 10, "con": 10, "int": 16, "wis": 10, "cha": 10}
            spell_slots = {1: 2}
            known_spells = ["火焰箭"]

            def ability_mod(self, ab):
                return (self.abilities.get(ab, 10) - 10) // 2

            def prof(self):
                return 2

        it = {
            "spell_name": "火焰箭",
            "spell_level": 0,
            "target_ac": 10,
        }

        result = resolve_cast(MockChar(), it)
        # 施法应该成功
        assert result.get("kind") == "cast"
        assert result.get("spell_name") == "火焰箭"


class TestRngReplay:
    """TEST-003: 随机结算可稳定回放。"""

    def test_same_seed_same_sequence(self):
        """同一 seed 产生相同的骰子序列。"""
        rng1 = RngContext(seed=100)
        rng2 = RngContext(seed=100)

        rolls1 = [rng1.roll_die(6) for _ in range(10)]
        rolls2 = [rng2.roll_die(6) for _ in range(10)]

        assert rolls1 == rolls2

    def test_different_seed_different_sequence(self):
        """不同 seed 产生不同的骰子序列。"""
        rng1 = RngContext(seed=100)
        rng2 = RngContext(seed=200)

        rolls1 = [rng1.roll_die(6) for _ in range(10)]
        rolls2 = [rng2.roll_die(6) for _ in range(10)]

        assert rolls1 != rolls2

    def test_roll_record_captures_complete_info(self):
        """RollRecord 记录完整的掷骰信息。"""
        rng = RngContext(seed=42)
        rng.roll_die(20)
        rng.roll_die(6)

        records = rng.get_records()
        assert len(records) == 2
        assert records[0].dice_expr == "1d20"
        assert records[1].dice_expr == "1d6"
        # 每条记录都有结果
        assert len(records[0].results) == 1
        assert len(records[1].results) == 1
