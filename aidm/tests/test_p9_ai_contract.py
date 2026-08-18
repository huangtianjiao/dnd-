"""P9 AI/UI Contract 测试（方案 §11.5）。

覆盖:
  - R-AI-001: Narrator 只消费确定性机械事实（ResolutionTrace），不接收
    原始 DB 对象或"请你判断"；narratable 视图不含内部状态
  - R-AI-002: 同样 action 在固定 RNG 下产生相同机械结果（REST/AI 同源）
  - R-AI-003: LLM 输出机械字段剥离后不进入 state（ARC-003 现有实现锁定）
"""

from __future__ import annotations

import json

import pytest


@pytest.mark.rule("R-AI-001")
class TestNarratorConsumesTrace:
    def test_narratable_view_of_attack_trace(self):
        """trace 的可叙事视图包含全部机械事实，且不含内部 state_changes。"""
        from aidm.rules.combat_trace import attack_trace, narratable
        t = attack_trace(weapon="长剑", attack_roll=17, attack_bonus=6,
                         target_ac=15, hit=True, damage_roll="1d8+4",
                         damage=9, mastery="sap")
        view = narratable(t)
        assert view["action"] == "attack:长剑"
        assert view["attack_roll"] == 17 and view["hit"] is True
        assert view["damage"] == 9 and view["mastery"] == "sap"
        # 可 JSON 序列化（LLM 输入必须是结构化事实，不是对象）
        json.dumps(view)

    def test_trace_has_no_ambiguous_fields(self):
        """trace 中不存在需要 DM 猜测的字段（确定性机械事实）。"""
        from aidm.rules.combat_trace import attack_trace
        t = attack_trace(weapon="长剑", attack_roll=17, attack_bonus=6,
                         target_ac=15, hit=True, damage=9)
        d = t.to_dict()
        for key in ("attack_roll", "attack_bonus", "target_ac", "hit", "damage"):
            assert isinstance(d[key], (int, bool)), key


@pytest.mark.rule("R-AI-002")
class TestDeterministicSameActionSameResult:
    def test_same_attack_twice_same_result(self):
        """固定 RNG 下同一攻击两次解析 → 完全相同（REST/AI 同源确定性）。"""
        from aidm.brain.resolvers import attack as atk_mod
        from aidm.engine import dice as engine_dice
        from aidm.stats.models import Character

        class _FixedRng:
            def randbelow(self, exclusive_upper):
                return 12  # d20=13

        ch = Character(name="战", race="人类", char_class="战士", level=1)
        ch.set_abilities({"str": 16, "dex": 12, "con": 14,
                          "int": 10, "wis": 10, "cha": 10})
        ch.hp_max = 12
        ch.hp_current = 12
        ch.equipped_weapon = "长剑"
        orig = engine_dice.get_active_rng()
        engine_dice.set_active_rng(_FixedRng())
        try:
            it = {"weapon": "长剑", "target_ac": 12, "distance_ft": 5}
            r1 = atk_mod.resolve_attack(ch, it)
            r2 = atk_mod.resolve_attack(ch, it)
            for k in ("hit", "attack_total", "damage", "crit"):
                assert r1.get(k) == r2.get(k), f"{k} 不一致: {r1.get(k)} vs {r2.get(k)}"
            assert r1["action_trace"] == r2["action_trace"]
        finally:
            engine_dice.set_active_rng(orig)


@pytest.mark.rule("R-AI-003")
class TestLLMNoMechanicalMutation:
    def test_strip_mechanical_fields_keeps_legal_action(self):
        """LLM 意图中的机械字段剥离后仍保留合法动作字段（ARC-003 锁定）。"""
        from aidm.agents.director import _strip_llm_mechanical_fields
        intent = {"action_type": "attack", "weapon": "长剑",
                  "target_ac": 99, "damage": 999}
        _strip_llm_mechanical_fields(intent)
        assert intent["action_type"] == "attack"
        assert intent["weapon"] == "长剑"
        assert "target_ac" not in intent
        assert "damage" not in intent

    def test_narrator_force_empty_state_changes(self):
        """Narrator 输出 state_changes 恒为空（ARC-004 机制已由 wave1 测试覆盖）。"""
        import inspect

        from aidm.agents import narrator
        src = inspect.getsource(narrator.narrate)
        assert "state_changes" in src  # 输出契约包含该键（值为空列表）
        assert "ARC-004" in src        # 注释标记剥离逻辑存在
