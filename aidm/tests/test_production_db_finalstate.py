"""生产链路数据库最终状态 E2E 断言测试。

验证新建 engine 模块已真实接入生产链路，且对数据库最终状态断言：
  - rest_state → brain/resolvers.actions.resolve_rest（休息会话状态）
  - recharge_spec → brain.rest._recharge_resource_pools（资源池恢复数值）
  - choice_record → build.character_builder.build_character（构建轨迹）
  - resolution_trace/OBS-001 → attack/ability_check 结算输出
  - downtime/EXP-003 → graph resolve 分派
  - RAG-003 → 存档/RULE_SPEC 路径由配置派生
"""

from __future__ import annotations

import json

import pytest


# ── REST-002: rest_state 接入 resolve_rest ──────────────────────

class TestRestStateProduction:
    def test_rest_session_tracked(self):
        """短休完成后返回 rest_session_id 与 phase=completed。"""
        from aidm.brain.resolvers.actions import resolve_rest
        import aidm.brain.rest as rest_mod
        orig_short = rest_mod.short_rest
        rest_mod.short_rest = lambda ch, hit_dice_to_spend=0: {
            "success": True, "type": "short", "hp_restored": 5,
            "hit_dice_spent": 0, "hit_dice_remaining": 1,
            "features_recharged": [], "errors": [],
        }
        try:
            state = {"campaign_id": 1, "player_input": "短休", "game_minutes": 100}
            ch = _MockChar(id=7)
            r = resolve_rest(state, ch, {"rest_type": "short"})
            assert r.get("rest_session_id"), "应返回休息会话ID"
            assert r.get("rest_phase") == "completed"
        finally:
            rest_mod.short_rest = orig_short


# ── REST-003: recharge_spec 接入资源池恢复 ──────────────────────

class TestRechargeSpecProduction:
    def test_resource_pool_recharged_to_full(self):
        """短休后资源池恢复为满（经 engine.recharge_spec）。"""
        from aidm.rules.resource import ResourceManager, ResourcePool
        from aidm.brain.rest import _recharge_resource_pools

        mgr = ResourceManager()
        mgr.create_pool("c1", ResourcePool(
            name="rage", max_value=2, current_value=0, recharge_on="short_rest"))

        class _Ch:
            entity_id = "c1"
            resource_manager = mgr

        recharged = _recharge_resource_pools(_Ch(), "short_rest")
        assert "rage" in recharged
        # 数据库最终状态：池满
        assert mgr.get_pool("c1", "rage").current_value == 2


# ── CHAR-008: choice_record 接入角色构建 ────────────────────────

class TestChoiceRecordProduction:
    def test_character_builder_records_log(self):
        """角色创建产出 build_log（含来源 Grant 与 ChoiceRecord）。"""
        from aidm.build.character_builder import CharacterBuilder, CharacterBuildPlan
        from aidm.rules.grant import GrantManager
        from aidm.rules.choice import ChoiceManager
        from aidm.rules.resource import ResourceManager

        builder = CharacterBuilder(
            grant_mgr=GrantManager(),
            choice_mgr=ChoiceManager(),
            resource_mgr=ResourceManager(),
        )
        plan = CharacterBuildPlan(
            entity_id="c1",
            species_choice="human",
            background_choice="acolyte",
            class_choice="fighter",
            ability_scores={"str": 15, "dex": 14, "con": 13,
                            "int": 10, "wis": 10, "cha": 10},
            skill_choices=["insight", "religion"],
        )
        result = builder.build_character(plan)
        assert "build_log" in result, "应产出构建轨迹 build_log"
        build_log = result["build_log"]
        assert len(build_log["grants"]) >= 3  # species + background + class
        assert len(build_log["choices"]) >= 4


# ── OBS-001: resolution_trace 接入结算输出 ──────────────────────

class TestResolutionTraceProduction:
    def _char(self):
        class _Ch:
            id = 1
            name = "勇者"
            char_class = "战士"
            level = 1
            abilities = {"str": 16, "dex": 14, "con": 14,
                         "int": 10, "wis": 12, "cha": 10}
            inventory = ["长剑"]
            equipped_weapon = "长剑"

            def ability_score(self, ab):
                return self.abilities[ab]

            def ability_mod(self, ab):
                return (self.abilities[ab] - 10) // 2

            def prof(self):
                return 2

            def to_condition_state(self):
                from aidm.engine.conditions import ConditionState
                return ConditionState(conditions=[], exhaustion=0)
        return _Ch()

    def test_attack_trace(self):
        from aidm.brain.resolvers.attack import resolve_attack
        r = resolve_attack(self._char(), {"weapon": "长剑"}, None)
        assert "resolution_trace" in r
        assert r["resolution_trace"]["modifiers"], "应有修正来源"
        assert r["resolution_trace"]["total"] == r.get("attack_total")

    def test_ability_check_trace(self):
        from aidm.brain.resolvers.actions import resolve_ability_check
        ch = self._char()
        ch.skill_proficiencies = ["洞察"]
        r = resolve_ability_check(ch, {"skill": "洞察", "action_type": "ability_check"})
        assert "resolution_trace" in r
        assert r["resolution_trace"]["action"] == "ability_check"


# ── EXP-003: downtime 接入生产分派 ──────────────────────────────

class TestDowntimeProduction:
    def test_resolve_downtime(self):
        from aidm.brain.resolvers.actions import resolve_downtime
        class _Ch:
            id = 5
        r = resolve_downtime(_Ch(), {"downtime_action": "start",
                                     "activity": "crafting",
                                     "item_value_gp": 100})
        assert r["kind"] == "downtime"
        assert r["days_required"] > 0
        assert r["cost_gp"] > 0


# ── RAG-003: 路径配置派生 ───────────────────────────────────────

class TestPathConfig:
    def test_default_db_from_config(self):
        from aidm.stats import store
        from aidm.config import PROJECT_ROOT
        assert str(PROJECT_ROOT) in store.DEFAULT_DB

    def test_spec_path_from_config(self):
        from aidm.knowledge.parse_rulespec import SPEC_PATH
        from aidm.config import PROJECT_ROOT
        assert str(PROJECT_ROOT) in SPEC_PATH


# ── 辅助 ────────────────────────────────────────────────────────

class _MockChar:
    def __init__(self, id):
        self.id = id


# ── CHR-004/005/002: 注册表接入 CharacterBuilder ───────────────

class TestRegistryInBuilder:
    def _builder(self):
        from aidm.build.character_builder import CharacterBuilder
        from aidm.rules.choice import ChoiceManager
        from aidm.rules.grant import GrantManager
        from aidm.rules.resource import ResourceManager
        return CharacterBuilder(
            grant_mgr=GrantManager(),
            choice_mgr=ChoiceManager(),
            resource_mgr=ResourceManager(),
        )

    def _plan(self, subclass="champion"):
        from aidm.build.character_builder import CharacterBuildPlan
        return CharacterBuildPlan(
            entity_id="c1", species_choice="human", background_choice="acolyte",
            class_choice="fighter", subclass_choice=subclass,
            ability_scores={"str": 15, "dex": 14, "con": 13,
                            "int": 10, "wis": 10, "cha": 10},
            skill_choices=["insight", "religion"],
        )

    def test_valid_build_uses_registries(self):
        """合法角色通过注册表校验（物种/背景/子职均存在）。"""
        builder = self._builder()
        errors = builder.validate_build(self._plan())
        assert errors == [], f"合法构建不应有错误: {errors}"

    def test_invalid_subclass_rejected(self):
        """非法子职被 subclass_registry_data 拒绝。"""
        builder = self._builder()
        errors = builder.validate_build(self._plan(subclass="not_real"))
        assert any("子职" in e for e in errors), f"应拒绝非法子职: {errors}"

    def test_build_enriched_from_registries(self):
        """角色构建从注册表补充物种特性/背景起源专长。"""
        builder = self._builder()
        result = builder.build_character(self._plan())
        assert "species_features" in result  # CHR-004 注册表特性
        assert result.get("origin_feat_cn"), "CHR-005 背景起源专长（中文）"


# ── DATA-002: canonical_id 接入角色创建 ────────────────────────

class TestCanonicalIdProduction:
    def test_character_creation_registers_canonical(self, monkeypatch):
        """角色创建时写入 class_canonical_id 并持久化到 DB。"""
        import tempfile
        from aidm.api.routes import character as char_route
        from aidm.api.routes.character import create_character
        from aidm.stats import store
        from aidm.api.routes.dependencies import CharIn

        tmp = tempfile.mktemp(suffix=".db")
        db = f"sqlite:///{tmp}"
        # 路由内部调用 store.save_character(ch)（无 db_path → DEFAULT_DB）
        # 通过 monkeypatch 使 DEFAULT_DB 指向临时库
        import aidm.stats.store as _store
        orig_db = _store.DEFAULT_DB
        _store.DEFAULT_DB = db
        try:
            store.create_campaign(1, db_path=db)
            # 先创建角色（调用路由全链路）
            req = CharIn(
                name="法师甲", race="人类", char_class="法师", subclass="塑能师",
                background="智者", alignment="守序善良", level=1, campaign_id=1,
                abilities={"str": 10, "dex": 10, "con": 10, "int": 16,
                           "wis": 10, "cha": 10},
                ability_method="free",
                hp_max=8, ac=10, speed=30,
            )
            # 模拟路由 save 到临时库（patch store.save_character 的默认 db）
            _orig_save = _store.save_character
            _orig_get = _store.get_character
            monkeypatch.setattr(
                _store, "save_character",
                lambda ch, db_path=None: _orig_save(ch, db))
            monkeypatch.setattr(
                _store, "get_character",
                lambda cid, db_path=None: _orig_get(cid, db))
            r = create_character(req)
            assert r["id"] is not None
            # DB 最终状态: class_canonical_id 已持久化
            loaded = _store.get_character(r["id"], db)
            assert loaded.class_canonical_id == "class.wizard", \
                f"应写入 class.wizard，实际 {loaded.class_canonical_id!r}"
        finally:
            _store.DEFAULT_DB = orig_db


# ── ENV-002: ObjectEntity/TerrainFeature 接入 Scene ─────────────

class TestEnv002Production:
    def test_scene_persists_objects_terrain(self):
        """物件/地形实体持久化到 Scene 并可从 DB 读回（ENV-002）。"""
        import tempfile
        from aidm.stats import store
        from aidm.stats.models import Scene
        from aidm.engine.objects import ObjectEntity, TerrainFeature

        tmp = tempfile.mktemp(suffix=".db")
        db = f"sqlite:///{tmp}"
        store.create_campaign(99, db_path=db)

        sc = Scene(campaign_id=99, location="地牢")
        obj = ObjectEntity.from_material(object_id="o1", name="木门", material="wood")
        terr = TerrainFeature(terrain_id="t1", terrain_type="difficult",
                              cost_multiplier=2.0)
        sc.add_object(obj.__dict__)
        sc.add_terrain(terr.__dict__)
        store.save_scene(sc, db)

        # DB 最终状态断言
        loaded = store.get_scene(99, db)
        assert len(loaded.objects) == 1
        assert loaded.objects[0]["material"] == "wood"
        assert loaded.objects[0]["ac"] >= 5  # 木材质自动计算 AC
        assert len(loaded.terrain) == 1
        assert loaded.terrain[0]["cost_multiplier"] == 2.0
