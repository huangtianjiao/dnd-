"""背景注册表 PHB2024 数据 — CHR-005。

从 data.backgrounds.BACKGROUNDS 数据表构建 BackgroundDefinition 并注册到全局 BackgroundRegistry。
包含属性选项、技能、工具、装备包、起源专长。

规则依据: CHR-005 背景选择与起源专长完整约束
出处: topics/玩家手册2024/角色创建/背景.htm
"""

from __future__ import annotations

from .background_def import BackgroundDefinition, BackgroundRegistry, EquipmentPack

# 全局背景注册表单例
_registry: BackgroundRegistry | None = None


def _build_background(bg_id: str, name: str, raw: dict) -> BackgroundDefinition:
    """从 BACKGROUNDS 原始数据构建 BackgroundDefinition。"""
    skill_profs = raw.get("skill_prof", [])
    return BackgroundDefinition(
        background_id=bg_id,
        name=name,
        skill_choices=skill_profs,
        skill_count=len(skill_profs),
        tool_choices=[raw.get("tool_prof", "")],
        tool_count=1 if raw.get("tool_prof") else 0,
        languages_count=0,
        origin_feat=raw.get("feat", ""),
        equipment=EquipmentPack(
            items=[],
            gold=0,
        ),
        feature_name="",
        feature_description=raw.get("equipment", ""),
    )


def load_background_registry() -> BackgroundRegistry:
    """加载全局背景注册表（幂等）。

    返回: 填充了 PHB2024 全部背景的 BackgroundRegistry。
    """
    global _registry
    if _registry is not None:
        return _registry

    from ..data.backgrounds import BACKGROUNDS

    registry = BackgroundRegistry()
    for zh_name, raw in BACKGROUNDS.items():
        bg_id = f"background.{zh_name}"
        registry.register(_build_background(bg_id, zh_name, raw))

    _registry = registry
    return _registry


def get_background_registry() -> BackgroundRegistry:
    """获取全局背景注册表。"""
    return load_background_registry()
