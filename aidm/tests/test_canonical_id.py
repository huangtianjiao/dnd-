"""canonical_id 系统测试。

★ DATA-002: 核心标识使用稳定 canonical_id，不依赖中文显示名。
"""

from __future__ import annotations

import pytest

from aidm.engine.canonical_id import (
    CanonicalEntry,
    CanonicalRegistry,
    get_registry,
    register_canonical,
    resolve_canonical_id,
)


class TestCanonicalId:
    """DATA-002: 稳定标识符系统。"""

    def test_register_and_lookup(self):
        """注册后可通过 canonical_id 查找。"""
        registry = CanonicalRegistry()
        entry = CanonicalEntry(
            canonical_id="weapon.long_sword",
            display_names={"zh": "长剑", "en": "Long Sword"},
            category="weapon",
        )
        registry.register(entry)

        found = registry.get("weapon.long_sword")
        assert found is not None
        assert found.get_display_name("zh") == "长剑"
        assert found.get_display_name("en") == "Long Sword"

    def test_resolve_by_display_name(self):
        """通过中文显示名查找 canonical_id。"""
        registry = CanonicalRegistry()
        registry.register(CanonicalEntry(
            canonical_id="spell.fireball",
            display_names={"zh": "火球术"},
            category="spell",
        ))

        cid = registry.resolve_by_display_name("火球术")
        assert cid == "spell.fireball"

    def test_migrate_legacy_string_exact(self):
        """旧中文字符串精确匹配迁移。"""
        registry = CanonicalRegistry()
        registry.register(CanonicalEntry(
            canonical_id="condition.poisoned",
            display_names={"zh": "中毒"},
            category="condition",
        ))

        cid = registry.migrate_legacy_string("中毒")
        assert cid == "condition.poisoned"

    def test_migrate_legacy_string_fuzzy(self):
        """旧中文字符串模糊匹配迁移。"""
        registry = CanonicalRegistry()
        registry.register(CanonicalEntry(
            canonical_id="item.healing_potion",
            display_names={"zh": "治疗药水"},
            category="item",
        ))

        # 子串匹配
        cid = registry.migrate_legacy_string("治疗药水（大）")
        assert cid == "item.healing_potion"

    def test_invalid_canonical_id_rejected(self):
        """非法 canonical_id 格式被拒绝。"""
        registry = CanonicalRegistry()
        with pytest.raises(ValueError, match="非法 canonical_id"):
            registry.register(CanonicalEntry(
                canonical_id="长剑",  # 缺少 namespace.slug 格式
                display_names={"zh": "长剑"},
            ))

    def test_global_registry(self):
        """全局注册表可用。"""
        register_canonical(
            "weapon.short_sword",
            {"zh": "短剑"},
            category="weapon",
        )

        cid = resolve_canonical_id("短剑")
        assert cid == "weapon.short_sword"
