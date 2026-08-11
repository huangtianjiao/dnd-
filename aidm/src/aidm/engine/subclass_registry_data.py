"""子职注册表 PHB2024 数据 — CHR-002。

从 data.class_features.SUBCLASS_FEATURES 构建 SubclassProgression 并注册到全局 SubclassRegistry。
每个子职按等级授予 FeatureDefinition。

规则依据: CHR-002 子职进度（3级起获得特性，按等级自动授予）
出处: topics/玩家手册2024/职业/子职.htm
"""

from __future__ import annotations

from .subclass_progression import SubclassFeature, SubclassProgression, SubclassRegistry

# 全局子职注册表单例
_registry: SubclassRegistry | None = None

# 职业英文 key → 中文名（与 classes.py 一致）
_CLASS_CN = {
    "barbarian": "野蛮人",
    "bard": "吟游诗人",
    "cleric": "牧师",
    "druid": "德鲁伊",
    "fighter": "战士",
    "monk": "武僧",
    "paladin": "圣武士",
    "ranger": "游侠",
    "rogue": "盗贼",
    "sorcerer": "术士",
    "warlock": "魔契师",
    "wizard": "法师",
}


def load_subclass_registry() -> SubclassRegistry:
    """加载全局子职注册表（幂等）。

    返回: 填充了 PHB2024 已实现子职的 SubclassRegistry。
    """
    global _registry
    if _registry is not None:
        return _registry

    from ..data.class_features import SUBCLASS_FEATURES

    registry = SubclassRegistry()
    for class_key, subclasses in SUBCLASS_FEATURES.items():
        base_class = _CLASS_CN.get(class_key, class_key)
        for sub_key, features_by_level in subclasses.items():
            prog = SubclassProgression(subclass_name=sub_key, base_class=base_class)
            for level, features in features_by_level.items():
                for feat in features:
                    prog.add_feature(SubclassFeature(
                        name=getattr(feat, "name", str(feat)),
                        level=level,
                        description=getattr(feat, "description", ""),
                        grants=[],
                    ))
            registry.register(prog)

    _registry = registry
    return _registry


def get_subclass_registry() -> SubclassRegistry:
    """获取全局子职注册表。"""
    return load_subclass_registry()
