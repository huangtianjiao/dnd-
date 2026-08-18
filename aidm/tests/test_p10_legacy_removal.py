"""P10 Legacy Removal 验证（方案 §14.4 删除清单）。

每条断言锁定「旧重复权威已经退役/删除」：
  - 全局 FEAT_LEVELS 不再作为生产 feat 判断（entitlement 服务替代）
  - brain/levelup 不再含重复兼职数据表（委托 engine.multiclass）
  - API 不再以 default_known_spells 作 GET fallback（来源只能写入）
  - rest 路由不再手动挑选字段写回（RestService 事务）
"""

from __future__ import annotations

import inspect

import pytest


@pytest.mark.rule("R-LGC-001")
class TestFeatureLevelsRetired:
    def test_levelup_production_uses_entitlement(self):
        """level_up 的 feat 判断不再引用全局 FEAT_LEVELS。"""
        from aidm.brain import levelup
        src = inspect.getsource(levelup.level_up)
        assert "FEAT_LEVELS" not in src
        assert "is_entitled_at" in src

    def test_available_feats_no_global_gate(self):
        from aidm.brain import levelup
        src = inspect.getsource(levelup.available_feats)
        assert "FEAT_LEVELS" not in src
        assert "entitled" in src


@pytest.mark.rule("R-LGC-002")
class TestMulticlassTablesRemoved:
    def test_levelup_has_no_duplicate_tables(self):
        from aidm.brain import levelup
        src = inspect.getsource(levelup)
        for legacy in ("_MULTICLASS_PREREQ =", "_MULTICLASS_PROFICIENCIES =",
                       "_MULTICLASS_SPELL_SLOTS =", "_MULTICLASS_SPELL_WEIGHT ="):
            assert legacy not in src, f"旧重复数据表仍存在: {legacy}"

    def test_levelup_delegates_to_engine(self):
        from aidm.brain import levelup
        src = inspect.getsource(levelup.multiclass_spell_slots)
        assert "engine.multiclass" in src


@pytest.mark.rule("R-LGC-003")
class TestSpellProductionFallbackRemoved:
    def test_get_character_no_default_known_fallback(self):
        from aidm.api.routes import character
        src = inspect.getsource(character.get_character)
        assert "default_known_spells" not in src, "GET 仍回退职业法术表"

    def test_init_loadout_model_driven(self):
        from aidm.api.routes import dependencies
        src = inspect.getsource(dependencies.init_loadout)
        assert "spellbook" in src or "prepared" in src  # 按模型分发


@pytest.mark.rule("R-LGC-004")
class TestRestRouteNoManualWrites:
    def test_rest_route_uses_service(self):
        from aidm.api.routes import character
        src = inspect.getsource(character.rest_character)
        assert "apply_short_rest" in src or "apply_long_rest" in src
        # API 不再直接挑选字段写回
        assert "ch.hp_current = min" not in src
        assert "ch.set_spell_slots" not in src


@pytest.mark.rule("R-LGC-005")
class TestResourceAuthorityPersisted:
    def test_rest_service_recharges_persisted_pools(self):
        from aidm.build import rest_service
        src = inspect.getsource(rest_service._recharge_pools)
        assert "resource_pools" in src


@pytest.mark.rule("R-LGC-006")
class TestFeatMasterySpellNoBypass:
    def test_feat_route_has_owner_guard_and_entitlement(self):
        from aidm.api.routes import feats
        src = inspect.getsource(feats.select_feat_api)
        assert "require_character_owner" in src
        assert "is_entitled_at" in src

    def test_prepare_spell_single_writer(self):
        """prepared 数组唯一写入路径为 rules.spellcasting（API 只调服务）。"""
        from aidm.api.routes import character
        src = inspect.getsource(character.prepare_spell_api)
        assert "prepare_spell" in src
        assert "set_prepared_spells" not in src  # API 不直接改数组

    def test_mastery_gated_by_character_auth(self):
        from aidm.brain.resolvers import attack
        src = inspect.getsource(attack._resolve_weapon_mastery)
        assert "has_mastery" in src  # 战斗解析查询角色授权
