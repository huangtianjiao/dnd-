"""Wave 3C 测试 — 移动/反应/状态系统 (COM-009~015)。

覆盖:
  COM-013: TimingPoint / TimingHandler / TimingQueue / TimingController
  COM-009: ReactionWindow / ReactionController
  COM-010: ReadyEffect 准备动作
  COM-011: CONDITION_DEFINITIONS / get_condition_effects / get_exhaustion_effects
  COM-012: MovementSegment / MovementPlan
  COM-014/015: 回避/协助/躲藏 EffectInstance 化增强
"""

from __future__ import annotations

import pytest

from aidm.engine.timing import (
    TimingController,
    TimingHandler,
    TimingPoint,
    TimingQueue,
)
from aidm.engine.reaction_window import (
    ReactionController,
    ReactionOption,
    ReactionType,
    ReactionWindow,
    ReadyEffect,
)
from aidm.engine.conditions import (
    CONDITION_DEFINITIONS,
    ConditionState,
    get_condition_effects,
    get_exhaustion_effects,
)
from aidm.engine.combat import (
    Combatant,
    MovementPlan,
    MovementSegment,
    FT_PER_SQUARE,
)
from aidm.engine.battle_map import BattleMap, GridCell
from aidm.engine.effects import (
    DurationSpec,
    DurationType,
    EffectInstance,
    EffectManager,
    SourceRef,
    StackPolicyType,
)


# ──────────────────────────────────────────────────────────────────────────
# COM-013: TimingPoint 同时效应排序
# ──────────────────────────────────────────────────────────────────────────

class TestTimingPoint:
    """TimingPoint 枚举测试。"""

    def test_ordering(self):
        """数值越小越先执行。"""
        assert TimingPoint.COMBAT_START < TimingPoint.INITIATIVE_BEFORE_ROLL
        assert TimingPoint.TURN_START < TimingPoint.BEFORE_ACTION
        assert TimingPoint.BEFORE_ATTACK_ROLL < TimingPoint.AFTER_ATTACK_ROLL
        assert TimingPoint.TURN_END < TimingPoint.ROUND_END
        assert TimingPoint.ROUND_END < TimingPoint.COMBAT_END

    def test_all_values_unique(self):
        """所有时序点值唯一。"""
        values = [tp.value for tp in TimingPoint]
        assert len(values) == len(set(values))

    def test_rest_timing_points(self):
        """休息相关时序点。"""
        assert TimingPoint.REST_STARTED < TimingPoint.REST_COMPLETED
        assert TimingPoint.REST_STARTED < TimingPoint.REST_INTERRUPTED


class TestTimingHandler:
    """TimingHandler 测试。"""

    def test_priority_sorting(self):
        """高优先级排在前面。"""
        h1 = TimingHandler(TimingPoint.TURN_START, "h1", priority=0)
        h2 = TimingHandler(TimingPoint.TURN_START, "h2", priority=10)
        h3 = TimingHandler(TimingPoint.TURN_START, "h3", priority=5)
        handlers = sorted([h1, h2, h3])
        assert handlers[0].handler_id == "h2"
        assert handlers[1].handler_id == "h3"
        assert handlers[2].handler_id == "h1"


class TestTimingQueue:
    """TimingQueue 测试。"""

    def test_add_and_execute(self):
        """添加 handler 并按优先级执行。"""
        results = []

        def cb1(ctx):
            results.append("cb1")
            return {"action": "cb1"}

        def cb2(ctx):
            results.append("cb2")
            return {"action": "cb2"}

        q = TimingQueue(timing=TimingPoint.TURN_START)
        q.add(TimingHandler(TimingPoint.TURN_START, "h1", callback=cb1, priority=0))
        q.add(TimingHandler(TimingPoint.TURN_START, "h2", callback=cb2, priority=10))

        events = q.execute_all({})
        # h2 优先级高，先执行
        assert results == ["cb2", "cb1"]
        assert len(events) == 2
        assert events[0]["handler_id"] == "h2"

    def test_remove(self):
        """移除 handler。"""
        q = TimingQueue(timing=TimingPoint.TURN_START)
        q.add(TimingHandler(TimingPoint.TURN_START, "h1"))
        q.add(TimingHandler(TimingPoint.TURN_START, "h2"))
        assert q.remove("h1") is True
        assert len(q.handlers) == 1
        assert q.handlers[0].handler_id == "h2"
        assert q.remove("nonexistent") is False

    def test_execute_no_callback(self):
        """没有 callback 的 handler 不产生事件。"""
        q = TimingQueue(timing=TimingPoint.TURN_START)
        q.add(TimingHandler(TimingPoint.TURN_START, "h1", callback=None))
        events = q.execute_all({})
        assert events == []


class TestTimingController:
    """TimingController 测试。"""

    def test_register_and_trigger(self):
        """注册并触发。"""
        ctrl = TimingController()
        triggered = []

        def on_turn_start(ctx):
            triggered.append(ctx.get("entity"))
            return {"type": "turn_start"}

        ctrl.register(TimingHandler(
            TimingPoint.TURN_START, "ts1",
            callback=on_turn_start, priority=0,
        ))
        events = ctrl.trigger(TimingPoint.TURN_START, {"entity": "warrior"})
        assert triggered == ["warrior"]
        assert len(events) == 1
        assert events[0]["timing"] == "TURN_START"

    def test_unregister(self):
        """注销 handler。"""
        ctrl = TimingController()
        ctrl.register(TimingHandler(TimingPoint.TURN_END, "te1"))
        assert ctrl.unregister("te1") is True
        assert ctrl.unregister("te1") is False
        assert ctrl.trigger(TimingPoint.TURN_END, {}) == []

    def test_clear(self):
        """清除所有。"""
        ctrl = TimingController()
        ctrl.register(TimingHandler(TimingPoint.TURN_START, "a"))
        ctrl.register(TimingHandler(TimingPoint.TURN_END, "b"))
        ctrl.clear()
        assert ctrl.trigger(TimingPoint.TURN_START, {}) == []
        assert ctrl.trigger(TimingPoint.TURN_END, {}) == []

    def test_get_handlers(self):
        """查询 handler 列表。"""
        ctrl = TimingController()
        ctrl.register(TimingHandler(TimingPoint.TURN_START, "a", priority=5))
        ctrl.register(TimingHandler(TimingPoint.TURN_START, "b", priority=10))
        handlers = ctrl.get_handlers(TimingPoint.TURN_START)
        assert len(handlers) == 2
        assert handlers[0].handler_id == "b"  # 高优先级在前

    def test_trigger_empty_timing(self):
        """触发未注册时点的返回空。"""
        ctrl = TimingController()
        assert ctrl.trigger(TimingPoint.COMBAT_START, {}) == []


# ──────────────────────────────────────────────────────────────────────────
# COM-009: ReactionWindow 统一反应系统
# ──────────────────────────────────────────────────────────────────────────

class TestReactionWindow:
    """ReactionWindow 测试。"""

    def test_open_and_select(self):
        """打开窗口并选择反应。"""
        window = ReactionWindow()
        cb_called = []

        def on_opp_attack(ctx):
            cb_called.append(True)
            return {"type": "opportunity_attack", "damage": 5}

        opt = ReactionOption(
            reaction_type=ReactionType.OPPORTUNITY_ATTACK,
            entity_id="fighter",
            ability_name="借机攻击",
            callback=on_opp_attack,
        )
        window.open_window(
            trigger_event="leave_reach",
            context={"mover": "rogue"},
            eligible=["fighter"],
            reactions=[opt],
        )
        assert window.is_open

        selected = window.select_reaction("fighter", ReactionType.OPPORTUNITY_ATTACK)
        assert selected is opt

        events = window.close_window()
        assert not window.is_open
        assert any(e.get("type") == "opportunity_attack" for e in events)
        assert cb_called

    def test_select_invalid_entity(self):
        """非法实体选择返回 None。"""
        window = ReactionWindow()
        window.open_window("test", {}, ["a"], [])
        assert window.select_reaction("b", ReactionType.CUSTOM) is None

    def test_select_invalid_type(self):
        """非法反应类型选择返回 None。"""
        window = ReactionWindow()
        opt = ReactionOption(ReactionType.SHIELD_SPELL, "a")
        window.open_window("test", {}, ["a"], [opt])
        assert window.select_reaction("a", ReactionType.COUNTERSPELL) is None

    def test_close_without_selection(self):
        """无人反应关闭窗口。"""
        window = ReactionWindow()
        window.open_window("test", {}, ["a"], [])
        events = window.close_window()
        assert any(e.get("type") == "reaction_window_closed" for e in events)
        assert not window.is_open

    def test_add_available_reaction(self):
        """动态添加反应选项。"""
        window = ReactionWindow()
        window.open_window("test", {}, ["a"], [])
        opt = ReactionOption(ReactionType.CUSTOM, "a", ability_name="Custom")
        window.add_available_reaction(opt)
        assert len(window.available_reactions) == 1


class TestReactionController:
    """ReactionController 测试。"""

    def test_open_and_resolve(self):
        """打开并结算。"""
        ctrl = ReactionController()
        called = []

        def cb(ctx):
            called.append(True)
            return {"type": "shield"}

        opt = ReactionOption(
            ReactionType.SHIELD_SPELL, "wizard",
            ability_name="Shield", callback=cb,
        )
        window = ctrl.open(
            trigger_event="before_damage",
            context={"target": "wizard"},
            eligible_reactors=["wizard"],
            reactions=[opt],
        )
        assert ctrl.current_window is window

        events = ctrl.resolve("wizard", ReactionType.SHIELD_SPELL)
        assert ctrl.current_window is None
        assert len(ctrl.history) == 1
        assert called

    def test_skip(self):
        """跳过反应窗口。"""
        ctrl = ReactionController()
        ctrl.open("test", {}, ["a"])
        events = ctrl.skip()
        assert ctrl.current_window is None
        assert any(e.get("type") == "reaction_window_closed" for e in events)

    def test_open_replaces_existing(self):
        """新窗口替换旧窗口。"""
        ctrl = ReactionController()
        w1 = ctrl.open("event1", {}, ["a"])
        w2 = ctrl.open("event2", {}, ["b"])
        assert ctrl.current_window is w2
        assert len(ctrl.history) == 1
        assert ctrl.history[0] is w1

    def test_resolve_no_window(self):
        """无窗口时 resolve 返回空。"""
        ctrl = ReactionController()
        assert ctrl.resolve("a", ReactionType.CUSTOM) == []

    def test_skip_no_window(self):
        """无窗口时 skip 返回空。"""
        ctrl = ReactionController()
        assert ctrl.skip() == []


# ──────────────────────────────────────────────────────────────────────────
# COM-010: ReadyEffect 准备动作
# ──────────────────────────────────────────────────────────────────────────

class TestReadyEffect:
    """ReadyEffect 准备动作测试。"""

    def test_activate_and_trigger(self):
        """激活并触发。"""
        ready = ReadyEffect(
            entity_id="fighter",
            prepared_action="attack",
            trigger_predicate="敌人靠近",
        )
        ready.activate(current_round=1)
        assert ready.is_active
        assert ready.expires_round == 2

        assert ready.matches_trigger("敌人靠近了", {})
        events = ready.execute({"target": "goblin"})
        assert len(events) == 1
        assert events[0]["type"] == "ready_triggered"
        assert not ready.is_active  # 一次性

    def test_matches_trigger_callback(self):
        """使用回调判定触发。"""
        def pred(event, ctx):
            return ctx.get("distance", 10) <= 5

        ready = ReadyEffect(
            entity_id="fighter",
            prepared_action="attack",
            trigger_callback=pred,
        )
        ready.activate(1)
        assert ready.matches_trigger("move", {"distance": 3})
        assert not ready.matches_trigger("move", {"distance": 10})

    def test_inactive_no_match(self):
        """未激活时不匹配。"""
        ready = ReadyEffect(entity_id="a", prepared_action="attack")
        assert not ready.matches_trigger("test", {})

    def test_expire(self):
        """过期处理。"""
        ready = ReadyEffect(entity_id="a", prepared_action="attack")
        ready.activate(1)
        ev = ready.expire()
        assert ev["type"] == "ready_expired"
        assert not ready.is_active

    def test_execute_inactive(self):
        """未激活执行返回空。"""
        ready = ReadyEffect(entity_id="a", prepared_action="attack")
        assert ready.execute({}) == []

    def test_concentration_flag(self):
        """准备法术需要专注。"""
        ready = ReadyEffect(
            entity_id="wizard",
            prepared_action="spell",
            prepared_payload={"spell": "fireball"},
            requires_concentration=True,
        )
        assert ready.requires_concentration is True


# ──────────────────────────────────────────────────────────────────────────
# COM-011: 15种状态完整数值效果
# ──────────────────────────────────────────────────────────────────────────

class TestConditionDefinitions:
    """CONDITION_DEFINITIONS 完整性测试。"""

    def test_all_15_conditions_defined(self):
        """15种状态均有定义。"""
        expected = {
            "目盲", "魅惑", "耳聋", "恐慌", "受擒", "失能", "隐形",
            "麻痹", "石化", "力竭", "中毒", "倒地", "束缚", "震慑", "昏迷",
        }
        assert set(CONDITION_DEFINITIONS.keys()) == expected

    def test_blinded_effects(self):
        """目盲效果定义。"""
        eff = get_condition_effects("目盲")
        assert eff["roll_modifiers"]["attack_roll"] == "auto_miss"
        assert eff["roll_modifiers"]["ability_check_see"] == "auto_fail"

    def test_charmed_effects(self):
        """魅惑效果定义。"""
        eff = get_condition_effects("魅惑")
        assert eff["action_constraints"]["cannot_attack_source"] is True
        assert eff.get("source_id_required") is True

    def test_frightened_effects(self):
        """恐慌效果定义。"""
        eff = get_condition_effects("恐慌")
        assert eff["roll_modifiers"]["attack_roll"] == "disadvantage_if_source_visible"
        assert eff["movement_constraints"]["cannot_move_closer_to_source"] is True

    def test_grappled_effects(self):
        """受擒效果定义。"""
        eff = get_condition_effects("受擒")
        assert eff["movement_constraints"]["speed"] == 0

    def test_incapacitated_effects(self):
        """失能效果定义。"""
        eff = get_condition_effects("失能")
        assert eff["action_constraints"]["no_actions"] is True
        assert eff["action_constraints"]["no_reactions"] is True

    def test_paralyzed_effects(self):
        """麻痹效果定义。"""
        eff = get_condition_effects("麻痹")
        assert eff["roll_modifiers"]["dex_save"] == "auto_fail"
        assert eff["roll_modifiers"]["attack_roll_again"] == "advantage_and_crit"
        assert eff["movement_constraints"]["speed"] == 0

    def test_petrified_effects(self):
        """石化效果定义。"""
        eff = get_condition_effects("石化")
        assert eff["special"]["weight_changes"] is True
        assert eff["special"]["stops_aging"] is True

    def test_exhaustion_levels(self):
        """力竭各级效果。"""
        assert get_exhaustion_effects(1)["disadvantage_ability_checks"] is True
        assert get_exhaustion_effects(2)["speed_halved"] is True
        assert get_exhaustion_effects(3)["disadvantage_attack_and_save"] is True
        assert get_exhaustion_effects(4)["hp_max_halved"] is True
        assert get_exhaustion_effects(5)["speed_zero"] is True
        assert get_exhaustion_effects(6)["dead"] is True
        assert get_exhaustion_effects(7) == {}  # 超出范围

    def test_poisoned_effects(self):
        """中毒效果定义。"""
        eff = get_condition_effects("中毒")
        assert eff["roll_modifiers"]["attack_roll"] == "disadvantage"
        assert eff["roll_modifiers"]["ability_check"] == "disadvantage"

    def test_prone_effects(self):
        """倒地效果定义。"""
        eff = get_condition_effects("倒地")
        assert eff["attack_again_modifiers"]["melee_within_5ft"] == "advantage"
        assert eff["attack_again_modifiers"]["ranged_or_far"] == "disadvantage"

    def test_restrained_effects(self):
        """束缚效果定义。"""
        eff = get_condition_effects("束缚")
        assert eff["roll_modifiers"]["dex_save"] == "disadvantage"
        assert eff["attack_again_modifiers"]["advantage"] is True

    def test_stunned_effects(self):
        """震慑效果定义。"""
        eff = get_condition_effects("震慑")
        assert eff["action_constraints"]["no_actions"] is True
        assert eff["roll_modifiers"]["dex_save"] == "auto_fail"

    def test_unconscious_effects(self):
        """昏迷效果定义。"""
        eff = get_condition_effects("昏迷")
        assert eff["special"]["drops_items"] is True
        assert eff["special"]["unaware"] is True
        assert eff["roll_modifiers"]["attack_roll_again"] == "advantage_and_crit"

    def test_unknown_condition_returns_empty(self):
        """未知状态返回空字典。"""
        assert get_condition_effects("不存在的状态") == {}


# ──────────────────────────────────────────────────────────────────────────
# COM-012: MovementPlan 移动路径结算
# ──────────────────────────────────────────────────────────────────────────

class TestMovementSegment:
    """MovementSegment 测试。"""

    def test_basic_segment(self):
        seg = MovementSegment(from_pos=(0, 0), to_pos=(1, 0), cost_ft=5.0)
        assert seg.cost_ft == 5.0
        assert seg.events == []


class TestMovementPlan:
    """MovementPlan 测试。"""

    def test_add_segment(self):
        """添加移动段。"""
        plan = MovementPlan(entity_id="hero", speed_ft=30)
        seg = plan.add_segment((0, 0), (1, 0))
        assert seg.cost_ft == 5.0  # 1格 × 5尺
        assert len(plan.segments) == 1

    def test_add_segment_difficult_terrain(self):
        """困难地形消耗加倍。"""
        plan = MovementPlan(entity_id="hero", speed_ft=30)
        seg = plan.add_segment((0, 0), (1, 0), terrain_cost=2.0)
        assert seg.cost_ft == 10.0  # 1格 × 5尺 × 2

    def test_validate_ok(self):
        """合法路径无错误。"""
        plan = MovementPlan(entity_id="hero", speed_ft=30)
        plan.add_segment((0, 0), (2, 0))  # 10尺
        plan.add_segment((2, 0), (4, 0))  # 10尺
        assert plan.validate() == []

    def test_validate_exceeds_speed(self):
        """超出速度的路径。"""
        plan = MovementPlan(entity_id="hero", speed_ft=10)
        plan.add_segment((0, 0), (3, 0))  # 15尺 > 10
        errors = plan.validate()
        assert len(errors) > 0
        assert "超过速度" in errors[0]

    def test_validate_out_of_bounds(self):
        """超出地图范围。"""
        bm = BattleMap(width=5, height=5)
        plan = MovementPlan(entity_id="hero", speed_ft=30)
        plan.add_segment((0, 0), (10, 10))  # 超出 5×5
        errors = plan.validate(battle_map=bm)
        assert any("超出地图范围" in e for e in errors)

    def test_execute_basic(self):
        """基础执行。"""
        plan = MovementPlan(entity_id="hero", speed_ft=30)
        plan.add_segment((0, 0), (1, 0))
        plan.add_segment((1, 0), (2, 0))
        events = plan.execute()
        # 2 segments + 1 complete
        seg_events = [e for e in events if e["type"] == "movement_segment"]
        assert len(seg_events) == 2
        complete = [e for e in events if e["type"] == "movement_complete"]
        assert len(complete) == 1
        assert complete[0]["total_cost_ft"] == 10.0
        assert complete[0]["remaining_speed_ft"] == 20.0

    def test_execute_insufficient_speed(self):
        """移动力不足时停止。"""
        plan = MovementPlan(entity_id="hero", speed_ft=10)
        plan.add_segment((0, 0), (1, 0))  # 5尺
        plan.add_segment((1, 0), (3, 0))  # 10尺 > 剩余5尺
        events = plan.execute()
        stopped = [e for e in events if e["type"] == "movement_stopped"]
        assert len(stopped) == 1

    def test_execute_with_battle_map(self):
        """配合 BattleMap 执行。"""
        bm = BattleMap(width=10, height=10)
        # 放置实体
        cell = bm.get_cell(0, 0)
        cell.occupant_id = "hero"
        cell.is_occupied = True

        plan = MovementPlan(entity_id="hero", speed_ft=30)
        plan.add_segment((0, 0), (1, 0))
        events = plan.execute(battle_map=bm)
        # 应成功移动
        seg_events = [e for e in events if e["type"] == "movement_segment"]
        assert len(seg_events) == 1
        # 地图位置更新
        assert bm.get_cell(1, 0).occupant_id == "hero"
        assert bm.get_cell(0, 0).occupant_id is None

    def test_diagonal_movement_cost(self):
        """对角线移动消耗（切比雪夫距离）。"""
        plan = MovementPlan(entity_id="hero", speed_ft=30)
        seg = plan.add_segment((0, 0), (1, 1))  # 对角1格 = 5尺
        assert seg.cost_ft == 5.0


# ──────────────────────────────────────────────────────────────────────────
# COM-014/015: 回避/协助/躲藏 EffectInstance 化增强
# ──────────────────────────────────────────────────────────────────────────

class TestDisengageEffect:
    """撤离动作 EffectInstance 化验证。"""

    def test_disengage_produces_effect(self):
        """撤离动作应产生不触发 OA 的效果标记。"""
        from aidm.engine.actions import action_disengage

        c = Combatant(cid="d1", name="游侠", speed=30)
        c.speed_remaining = 30
        result = action_disengage(c)
        assert result.success
        assert c.disengage_active is True

    def test_disengage_cleared_on_turn_reset(self):
        """撤离效果在下回合开始清除。"""
        from aidm.engine.combat import _reset_turn_economy

        c = Combatant(cid="d2", name="游侠", speed=30)
        c.disengage_active = True
        _reset_turn_economy(c)
        assert c.disengage_active is False


class TestDodgeEffect:
    """回避动作 EffectInstance 化验证。"""

    def test_dodge_produces_effect(self):
        """回避动作应产生攻击劣势+DEX豁免优势效果。"""
        from aidm.engine.actions import action_dodge

        c = Combatant(cid="dg1", name="牧师", speed=30)
        c.speed_remaining = 30
        result = action_dodge(c)
        assert result.success
        assert c.dodge_active is True
        assert result.extra["benefits_active"] is True

    def test_dodge_ineffective_when_incapacitated(self):
        """失能时回避动作无法执行。"""
        from aidm.engine.actions import action_dodge

        c = Combatant(cid="dg2", name="牧师", speed=30)
        c.speed_remaining = 30
        c.conditions.add("震慑")  # 震慑 → 失能
        result = action_dodge(c)
        assert not result.success  # 失能不能动作
        assert c.dodge_active is False

    def test_dodge_cleared_on_turn_reset(self):
        """回避效果在下回合开始清除。"""
        from aidm.engine.combat import _reset_turn_economy

        c = Combatant(cid="dg3", name="牧师", speed=30)
        c.dodge_active = True
        _reset_turn_economy(c)
        assert c.dodge_active is False


class TestHelpEffect:
    """协助动作增强验证。"""

    def test_help_marks_advantage_target(self):
        """协助标记盟友对目标攻击优势。"""
        from aidm.engine.actions import action_help

        attacker = Combatant(cid="h1", name="战士")
        ally = Combatant(cid="h2", name="法师")
        target = Combatant(cid="h3", name="哥布林")
        result = action_help(attacker, ally, target=target, mode="attack")
        assert result.success
        assert ally.help_advantage_target == "h3"

    def test_help_first_aid_mode(self):
        """急救模式。"""
        from aidm.engine.actions import action_help
        from aidm.engine import check

        # Mock ability_check
        orig = check.ability_check
        check.ability_check = lambda **kw: type("R", (), {
            "success": True, "total": 12, "d20": 10, "rolls": [10],
            "mode": "normal", "target": kw.get("dc", 0),
            "margin": 2, "modifier": 2,
        })()
        attacker = Combatant(cid="h4", name="牧师")
        ally = Combatant(cid="h5", name="伤员")
        result = action_help(attacker, ally, mode="first_aid",
                             medicine_mod=2, medicine_prof=0,
                             medicine_proficient=False)
        assert result.success
        assert result.extra["stabilized"] is True
        check.ability_check = orig


class TestHideEffect:
    """躲藏动作增强验证。"""

    def test_hide_requires_heavy_obscurement_or_cover(self):
        """躲藏前置条件：重度遮蔽或3/4以上掩护。"""
        from aidm.engine.actions import action_hide
        from aidm.engine.combat import COVER_HALF, COVER_THREE_QUARTERS

        c = Combatant(cid="hd1", name="游荡者", speed=30)
        # 无遮蔽 → 失败
        result = action_hide(c, stealth_mod=5, stealth_prof=3,
                             proficient=True)
        assert not result.success
        assert result.extra["reason"] == "no_obscurement"

    def test_hide_success_with_heavy_obscurement(self):
        """重度遮蔽下躲藏成功。"""
        from aidm.engine.actions import action_hide
        from aidm.engine import check

        orig = check.ability_check
        check.ability_check = lambda **kw: type("R", (), {
            "success": True, "total": 16, "d20": 11, "rolls": [11],
            "mode": "normal", "target": kw.get("dc", 0),
            "margin": 1, "modifier": 5,
        })()
        c = Combatant(cid="hd2", name="游荡者", speed=30)
        result = action_hide(c, stealth_mod=5, stealth_prof=3,
                             proficient=True, heavily_obscured=True)
        assert result.success
        assert c.hidden is True
        assert result.extra["dc"] == 15
        check.ability_check = orig

    def test_hide_dc_is_15(self):
        """躲藏 DC 固定为 15。"""
        from aidm.engine.actions import HIDE_DC
        assert HIDE_DC == 15


# ──────────────────────────────────────────────────────────────────────────
# 集成测试
# ──────────────────────────────────────────────────────────────────────────

class TestIntegration:
    """集成测试 — 多系统联动。"""

    def test_timing_with_reaction(self):
        """时序系统触发反应窗口。"""
        timing_ctrl = TimingController()
        reaction_ctrl = ReactionController()

        def on_leave_reach(ctx):
            window = reaction_ctrl.open(
                trigger_event="leave_reach",
                context=ctx,
                eligible_reactors=["guard"],
            )
            return {"window_id": window.window_id}

        timing_ctrl.register(TimingHandler(
            TimingPoint.LEAVE_REACH, "oa_trigger",
            callback=on_leave_reach, priority=0,
        ))
        events = timing_ctrl.trigger(
            TimingPoint.LEAVE_REACH,
            {"mover": "rogue", "from": (0, 0), "to": (2, 0)},
        )
        assert len(events) == 1
        assert reaction_ctrl.current_window is not None

    def test_ready_with_timing(self):
        """准备动作与时序系统联动。"""
        ready = ReadyEffect(
            entity_id="fighter",
            prepared_action="attack",
            trigger_predicate="敌人进入范围",
        )
        ready.activate(current_round=1)

        timing_ctrl = TimingController()

        def check_ready(ctx):
            if ready.matches_trigger(ctx.get("event", ""), ctx):
                return ready.execute(ctx)
            return []

        timing_ctrl.register(TimingHandler(
            TimingPoint.ENTER_AREA, "ready_check",
            callback=check_ready, priority=0,
        ))
        events = timing_ctrl.trigger(
            TimingPoint.ENTER_AREA,
            {"event": "敌人进入范围", "entity": "goblin"},
        )
        assert any(e.get("type") == "ready_triggered" for e in events)
        assert not ready.is_active

    def test_movement_with_timing(self):
        """移动路径与时序系统联动。"""
        timing_ctrl = TimingController()
        leave_events = []

        def on_leave(ctx):
            leave_events.append(ctx)
            return {"type": "leave_detected"}

        timing_ctrl.register(TimingHandler(
            TimingPoint.LEAVE_REACH, "leave_watch",
            callback=on_leave, priority=0,
        ))

        plan = MovementPlan(entity_id="hero", speed_ft=30)
        plan.add_segment((0, 0), (2, 0))
        # 手动触发时序
        timing_ctrl.trigger(TimingPoint.LEAVE_REACH, {"entity": "hero"})
        assert len(leave_events) == 1

    def test_condition_effects_consistency(self):
        """状态效果定义与 ConditionState 逻辑一致。"""
        # 麻痹: 速度归0 + 失能
        state = ConditionState()
        state.add("麻痹")
        eff = get_condition_effects("麻痹")
        assert eff["movement_constraints"]["speed"] == 0
        assert state.is_incapacitated()
        from aidm.engine.conditions import speed_after_conditions
        assert speed_after_conditions(30, state) == 0

    def test_effect_manager_with_dodge(self):
        """EffectManager 管理回避效果。"""
        mgr = EffectManager()
        dodge_effect = EffectInstance(
            source=SourceRef(entity_id="cleric"),
            target_id="cleric",
            name="dodge",
            duration=DurationSpec(
                duration_type=DurationType.ROUNDS,
                remaining=1,
            ),
            modifiers=[
                {"category": "attack_again", "value": "disadvantage"},
                {"category": "dex_save", "value": "advantage"},
            ],
        )
        eid = mgr.add(dodge_effect)
        active = mgr.get_active("cleric")
        assert len(active) == 1
        mods = mgr.get_modifiers("cleric", "attack_again")
        assert len(mods) == 1
        assert mods[0]["value"] == "disadvantage"
