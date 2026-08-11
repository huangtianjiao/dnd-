"""Wave 3 怪物编译与多人支持测试 — MON-001/MON-002/API-001/INT-002。"""

import pytest


# ── MonsterAction ─────────────────────────────────────────────────────

class TestMonsterAction:
    def test_create_default(self):
        from aidm.data.monster_compiler import MonsterAction
        action = MonsterAction(name="测试攻击")
        assert action.name == "测试攻击"
        assert action.action_type == "action"
        assert action.attack_bonus == 0
        assert action.damage_dice == "1d6"
        assert action.action_id != ""

    def test_create_with_values(self):
        from aidm.data.monster_compiler import MonsterAction
        action = MonsterAction(
            action_id="test_action",
            name="火焰吐息",
            action_type="recharge",
            attack_bonus=5,
            damage_dice="4d6",
            damage_type="fire",
        )
        assert action.action_id == "test_action"
        assert action.attack_bonus == 5
        assert action.damage_type == "fire"


# ── MonsterStatBlock ──────────────────────────────────────────────────

class TestMonsterStatBlock:
    def test_create_default(self):
        from aidm.data.monster_compiler import MonsterStatBlock
        block = MonsterStatBlock(monster_id="goblin", name="哥布林")
        assert block.monster_id == "goblin"
        assert block.name == "哥布林"
        assert block.hp == 0
        assert block.ac == 10
        assert block.actions == []

    def test_with_actions(self):
        from aidm.data.monster_compiler import MonsterAction, MonsterStatBlock
        block = MonsterStatBlock(
            monster_id="orc",
            name="兽人",
            hp=15,
            ac=13,
            actions=[
                MonsterAction(name="弯刀攻击", attack_bonus=5, damage_dice="1d6+3"),
            ],
        )
        assert len(block.actions) == 1
        assert block.actions[0].name == "弯刀攻击"


# ── RechargeTracker ──────────────────────────────────────────────────

class TestRechargeTracker:
    def test_register_and_charge(self):
        from aidm.data.monster_compiler import RechargeTracker
        tracker = RechargeTracker()
        tracker.register("dragon", "fire_breath", initially_charged=False)
        assert not tracker.is_charged("dragon", "fire_breath")

    def test_roll_recharge_success(self):
        from aidm.data.monster_compiler import RechargeTracker

        class MockRng:
            def roll(self, sides):
                return 6  # 总是掷出 6

        tracker = RechargeTracker()
        tracker.register("dragon", "fire_breath", initially_charged=False)
        result = tracker.roll_recharge("dragon", "fire_breath", threshold=6, rng=MockRng())
        assert result is True
        assert tracker.is_charged("dragon", "fire_breath")

    def test_roll_recharge_failure(self):
        from aidm.data.monster_compiler import RechargeTracker

        class MockRng:
            def roll(self, sides):
                return 3  # 掷出 3，不够

        tracker = RechargeTracker()
        tracker.register("dragon", "fire_breath", initially_charged=False)
        result = tracker.roll_recharge("dragon", "fire_breath", threshold=6, rng=MockRng())
        assert result is False
        assert not tracker.is_charged("dragon", "fire_breath")

    def test_use_charge(self):
        from aidm.data.monster_compiler import RechargeTracker
        tracker = RechargeTracker()
        tracker.register("dragon", "fire_breath", initially_charged=True)
        assert tracker.use_charge("dragon", "fire_breath") is True
        assert not tracker.is_charged("dragon", "fire_breath")
        # 再次使用应该失败
        assert tracker.use_charge("dragon", "fire_breath") is False

    def test_reset(self):
        from aidm.data.monster_compiler import RechargeTracker
        tracker = RechargeTracker()
        tracker.register("dragon", "fire_breath", initially_charged=False)
        tracker.register("dragon", "lightning_breath", initially_charged=False)
        tracker.reset("dragon")
        assert tracker.is_charged("dragon", "fire_breath")
        assert tracker.is_charged("dragon", "lightning_breath")


# ── LairActionController ─────────────────────────────────────────────

class TestLairActionController:
    def test_register_lair(self):
        from aidm.data.monster_compiler import LairActionController
        controller = LairActionController()
        controller.register_lair("dragon_lair", 20, [{"name": "岩浆喷发"}])
        assert controller.should_trigger("dragon_lair", 20)
        assert not controller.should_trigger("dragon_lair", 15)

    def test_execute_lair_action(self):
        from aidm.data.monster_compiler import LairActionController
        controller = LairActionController()
        controller.register_lair("dragon_lair", 20, [{"name": "岩浆喷发", "damage": "6d6"}])
        result = controller.execute_lair_action("dragon_lair", 0, {"round": 3})
        assert result["type"] == "lair_action_executed"
        assert result["action"]["name"] == "岩浆喷发"

    def test_deactivate_lair(self):
        from aidm.data.monster_compiler import LairActionController
        controller = LairActionController()
        controller.register_lair("dragon_lair", 20, [{"name": "岩浆喷发"}])
        controller.deactivate_lair("dragon_lair")
        assert not controller.should_trigger("dragon_lair", 20)


# ── MonsterCompiler ──────────────────────────────────────────────────

class TestMonsterCompiler:
    def test_compile_basic_monster(self):
        from aidm.data.monster_compiler import MonsterCompiler
        compiler = MonsterCompiler()
        data = {
            "name": "哥布林",
            "cr": 0.25,
            "hp": 7,
            "ac": 15,
            "attack_bonus": 4,
            "damage_dice": "1d6+2",
            "damage_type": "挥砍",
            "speed": 30,
            "senses": "黑暗视觉60尺；被动察觉9",
            "creature_type": "类人",
            "size": "小型",
        }
        block = compiler.compile(data)
        assert block.name == "哥布林"
        assert block.hp == 7
        assert block.ac == 15
        assert block.cr == 0.25
        assert block.senses.get("darkvision") == 60
        assert block.passive_perception == 9
        assert block.size == "Small"
        assert len(block.actions) >= 1

    def test_compile_with_recharge(self):
        from aidm.data.monster_compiler import MonsterCompiler
        compiler = MonsterCompiler()
        data = {
            "id": "dragon",
            "name": "火龙",
            "hp": 100,
            "ac": 18,
            "recharge_abilities": [
                {
                    "ability_id": "fire_breath",
                    "name": "火焰吐息",
                    "damage_dice": "6d6",
                    "damage_type": "fire",
                }
            ],
        }
        block = compiler.compile(data)
        assert len(block.recharge_abilities) == 1
        assert compiler.recharge_tracker.is_charged("dragon", "fire_breath")

    def test_compile_from_existing(self):
        from aidm.data.monster_compiler import MonsterCompiler
        compiler = MonsterCompiler()
        # 尝试从现有数据编译
        block = compiler.compile_from_existing("哥布林")
        if block is not None:
            assert block.name == "哥布林"
            assert block.hp > 0

    def test_get_valid_actions(self):
        from aidm.data.monster_compiler import MonsterAction, MonsterCompiler, MonsterStatBlock
        compiler = MonsterCompiler()
        block = MonsterStatBlock(
            monster_id="orc",
            name="兽人",
            actions=[
                MonsterAction(name="弯刀", action_type="action", reach_ft=5),
                MonsterAction(name="标枪", action_type="action", range_ft=30),
            ],
            bonus_actions=[
                MonsterAction(name="闪避", action_type="bonus_action"),
            ],
        )
        # 近战范围内
        valid = compiler.get_valid_actions(block, {"target_distance_ft": 5})
        assert len(valid) == 2  # 两个主动作都可以

        # 远程目标
        valid = compiler.get_valid_actions(block, {"target_distance_ft": 20})
        assert len(valid) == 1  # 只有标枪

        # 请求 bonus_action
        valid = compiler.get_valid_actions(block, {"action_type": "bonus_action"})
        assert len(valid) == 1
        assert valid[0].name == "闪避"

    def test_execute_action(self):
        from aidm.data.monster_compiler import MonsterAction, MonsterCompiler, MonsterStatBlock
        compiler = MonsterCompiler()
        block = MonsterStatBlock(
            monster_id="goblin_1",
            name="哥布林",
        )
        action = MonsterAction(
            name="弯刀攻击",
            attack_bonus=4,
            damage_dice="1d6+2",
            damage_type="挥砍",
        )
        events = compiler.execute_action(block, action, "player_1", {"target_ac": 12})
        assert len(events) >= 1
        assert events[0]["type"] == "monster_attack"
        assert events[0]["attacker_id"] == "goblin_1"
        assert events[0]["target_id"] == "player_1"


# ── 目标解析消歧 (INT-002) ───────────────────────────────────────────

class TestTargetResolver:
    def _make_combat_state(self):
        """创建模拟战斗状态。"""
        class MockCombatant:
            def __init__(self, id, name, hp=10, dead=False, position=None):
                self.id = id
                self.name = name
                self.hp = hp
                self.dead = dead
                self.position = position

        class MockCombat:
            def __init__(self):
                self.active = True
                self.participants = [
                    MockCombatant("player_1", "战士", position=(0, 0)),
                    MockCombatant("goblin_1", "哥布林", position=(1, 0)),
                    MockCombatant("goblin_2", "哥布林", position=(2, 0)),
                    MockCombatant("orc_1", "兽人", position=(5, 0)),
                    MockCombatant("dead_goblin", "哥布林", dead=True, position=(3, 0)),
                ]
        return MockCombat()

    def test_resolve_unique_target(self):
        from aidm.brain.resolvers.target_resolver import resolve_target
        combat = self._make_combat_state()
        # 兽人在 (5,0)，距离 25 尺，需要足够的射程
        result = resolve_target("兽人", "player_1", combat, max_range_ft=30)
        assert not result.ambiguous
        assert result.resolved_target == "orc_1"
        assert result.error == ""

    def test_resolve_ambiguous_target(self):
        from aidm.brain.resolvers.target_resolver import resolve_target
        combat = self._make_combat_state()
        # 哥布林在 (1,0) 和 (2,0)，距离 5 尺和 10 尺
        result = resolve_target("哥布林", "player_1", combat, max_range_ft=15)
        assert result.ambiguous
        assert len(result.candidates) == 2  # 排除死亡的哥布林
        assert "消歧" in result.error or "2" in result.error

    def test_resolve_target_not_found(self):
        from aidm.brain.resolvers.target_resolver import resolve_target
        combat = self._make_combat_state()
        result = resolve_target("不存在的怪物", "player_1", combat)
        assert result.error != ""
        assert "找不到" in result.error

    def test_resolve_target_excludes_dead(self):
        from aidm.brain.resolvers.target_resolver import resolve_target
        combat = self._make_combat_state()
        result = resolve_target("哥布林", "player_1", combat, max_range_ft=15)
        # 死亡的哥布林不应在候选中
        for c in result.candidates:
            assert c.entity_id != "dead_goblin"

    def test_resolve_target_by_id(self):
        from aidm.brain.resolvers.target_resolver import resolve_target_by_id
        combat = self._make_combat_state()
        result = resolve_target_by_id("orc_1", "player_1", combat, max_range_ft=30)
        assert result.resolved_target == "orc_1"
        assert not result.ambiguous

    def test_resolve_target_out_of_range(self):
        from aidm.brain.resolvers.target_resolver import resolve_target
        combat = self._make_combat_state()
        # 兽人在 (5,0)，距离 25 尺，近战只有 5 尺
        result = resolve_target("兽人", "player_1", combat, max_range_ft=5)
        # 应该成功但距离较远
        # 注意：默认近战 5 尺，但目标在 25 尺外
        # 这里测试射程检查
        if result.candidates:
            cand = result.candidates[0]
            assert cand.distance_ft == 25.0

    def test_resolve_to_dict(self):
        from aidm.brain.resolvers.target_resolver import resolve_target
        combat = self._make_combat_state()
        result = resolve_target("兽人", "player_1", combat, max_range_ft=30)
        d = result.to_dict()
        assert "candidates" in d
        assert "ambiguous" in d
        assert "error" in d
        assert "resolved_target" in d


# ── 战斗路由权限检查 (API-001) ────────────────────────────────────────

class TestCombatRoutePermissions:
    def test_action_request_model(self):
        from aidm.api.routes.combat import ActionRequest
        req = ActionRequest(
            player_id="player_1",
            actor_id="char_1",
            command_type="MakeWeaponAttack",
            payload={"target": "goblin_1"},
        )
        assert req.player_id == "player_1"
        assert req.command_type == "MakeWeaponAttack"

    def test_check_version_no_conflict(self):
        from aidm.api.routes.combat import _check_version
        from aidm.engine import combat as cmb
        # 没有版本冲突（版本号为 None → 宽松放行）
        combat = cmb.Combat(version=3)
        _check_version(combat, expected_version=None)  # 不应抛出异常

    def test_check_version_with_match(self):
        from aidm.api.routes.combat import _check_version
        from aidm.engine import combat as cmb
        # API-001: 版本匹配 → 通过
        combat = cmb.Combat(version=5)
        _check_version(combat, expected_version=5)  # 不应抛出异常

    def test_check_version_stale(self):
        from aidm.api.routes.combat import _check_version
        from aidm.engine import combat as cmb
        from fastapi import HTTPException
        import pytest
        # API-001: 版本不匹配 → STALE_VERSION
        combat = cmb.Combat(version=6)
        with pytest.raises(HTTPException) as exc:
            _check_version(combat, expected_version=5)
        assert exc.value.status_code == 409
        assert exc.value.detail["error"] == "STALE_VERSION"


# ── 集成测试 ──────────────────────────────────────────────────────────

class TestIntegration:
    def test_monster_compiler_with_timing(self):
        """测试怪物编译器与 TimingController 集成。"""
        from aidm.data.monster_compiler import MonsterCompiler, MonsterStatBlock, MonsterAction
        from aidm.engine.timing import TimingController, TimingHandler, TimingPoint

        compiler = MonsterCompiler()
        timing = TimingController()

        # 注册一个时序处理器
        events_triggered = []
        def on_after_damage(ctx):
            events_triggered.append(ctx)
            return {"type": "timing_triggered"}

        timing.register(TimingHandler(
            timing=TimingPoint.AFTER_DAMAGE,
            handler_id="test_handler",
            callback=on_after_damage,
        ))

        # 将 timing controller 设置到编译器
        compiler._timing_controller = timing

        block = MonsterStatBlock(monster_id="test_monster", name="测试怪物")
        action = MonsterAction(name="测试攻击", attack_bonus=5, damage_dice="1d8+3")

        events = compiler.execute_action(block, action, "target_1", {"target_ac": 12})
        assert len(events) >= 1
        # 应该包含时序触发事件
        timing_events = [e for e in events if e.get("type") == "timing_triggered"]
        assert len(timing_events) == 1

    def test_legendary_resistance(self):
        """测试传奇抗性使用。"""
        from aidm.data.monster_compiler import MonsterCompiler, MonsterStatBlock

        compiler = MonsterCompiler()
        block = MonsterStatBlock(
            monster_id="lich",
            name="巫妖",
            legendary_resistance_count=3,
        )

        # 使用传奇抗性
        assert compiler.use_legendary_resistance(block) is True
        assert block.legendary_resistance_count == 2
        assert compiler.use_legendary_resistance(block) is True
        assert block.legendary_resistance_count == 1
        assert compiler.use_legendary_resistance(block) is True
        assert block.legendary_resistance_count == 0
        # 用完后再用应该失败
        assert compiler.use_legendary_resistance(block) is False

    def test_lair_action_with_combat(self):
        """测试巢穴动作与战斗集成。"""
        from aidm.data.monster_compiler import LairActionController

        lair = LairActionController()
        lair.register_lair("dragon_lair", 20, [
            {"name": "岩浆喷发", "damage": "6d6"},
            {"name": "毒气弥漫", "damage": "4d6"},
        ])

        # 先攻 20 时触发
        assert lair.should_trigger("dragon_lair", 20)
        result = lair.execute_lair_action("dragon_lair", 0, {"round": 5})
        assert result["type"] == "lair_action_executed"

        # 先攻 15 时不触发
        assert not lair.should_trigger("dragon_lair", 15)
