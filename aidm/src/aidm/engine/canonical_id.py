"""稳定标识符系统 — canonical_id 替代中文显示名。

设计原则：
  - 所有内容项（武器、法术、状态、物品）使用稳定的 canonical_id。
  - 显示名作为 locale 资源，不作为主键。
  - 迁移旧字符串到 canonical_id。

规则依据: DATA-002 核心标识依赖中文显示名
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# canonical_id 格式：namespace.slug (如 weapon.long_sword, spell.fireball)
_ID_PATTERN = re.compile(r"^[a-z_]+\.[a-z_]+$")


@dataclass
class CanonicalEntry:
    """单个内容项的规范条目。

    属性:
        canonical_id: 稳定标识符 (如 "weapon.long_sword")
        display_names: 各语言的显示名 {"zh": "长剑", "en": "Long Sword"}
        category: 内容类别 (weapon/spell/condition/item/class/species/background/feat)
        revision: 内容版本号
        source_rule_id: 关联的规则ID
    """
    canonical_id: str = ""
    display_names: Dict[str, str] = field(default_factory=dict)
    category: str = ""
    revision: int = 1
    source_rule_id: str = ""

    def get_display_name(self, locale: str = "zh") -> str:
        """获取指定语言的显示名。"""
        return self.display_names.get(locale, self.display_names.get("zh", self.canonical_id))


class CanonicalRegistry:
    """内容项规范注册表。

    管理 canonical_id ↔ 显示名 的双向映射。
    """

    def __init__(self) -> None:
        self._by_id: Dict[str, CanonicalEntry] = {}
        self._by_display: Dict[str, str] = {}  # "zh:长剑" → canonical_id

    def register(self, entry: CanonicalEntry) -> None:
        """注册一个内容项。"""
        if not _ID_PATTERN.match(entry.canonical_id):
            raise ValueError(f"非法 canonical_id 格式: {entry.canonical_id!r}, 应为 namespace.slug")
        self._by_id[entry.canonical_id] = entry
        for locale, name in entry.display_names.items():
            self._by_display[f"{locale}:{name}"] = entry.canonical_id

    def get(self, canonical_id: str) -> Optional[CanonicalEntry]:
        """通过 canonical_id 查找。"""
        return self._by_id.get(canonical_id)

    def resolve_by_display_name(self, name: str, locale: str = "zh") -> Optional[str]:
        """通过显示名查找 canonical_id。"""
        return self._by_display.get(f"{locale}:{name}")

    def list_by_category(self, category: str) -> List[CanonicalEntry]:
        """列出指定类别的所有条目。"""
        return [e for e in self._by_id.values() if e.category == category]

    def migrate_legacy_string(self, legacy_name: str, category: str = "") -> Optional[str]:
        """迁移旧的中文字符串到 canonical_id。

        Args:
            legacy_name: 旧的中文显示名
            category: 可选的内容类别

        Returns:
            对应的 canonical_id，如果找不到则返回 None
        """
        # 先尝试精确匹配
        cid = self.resolve_by_display_name(legacy_name)
        if cid:
            return cid

        # 尝试模糊匹配（子串包含）
        for entry in self._by_id.values():
            if category and entry.category != category:
                continue
            for name in entry.display_names.values():
                if legacy_name in name or name in legacy_name:
                    return entry.canonical_id

        return None


# 全局注册表实例
_registry = CanonicalRegistry()


def get_registry() -> CanonicalRegistry:
    """获取全局 CanonicalRegistry 实例。"""
    return _registry


def register_canonical(
    canonical_id: str,
    display_names: Dict[str, str],
    category: str = "",
    revision: int = 1,
    source_rule_id: str = "",
) -> None:
    """注册一个内容项到全局注册表。"""
    _registry.register(CanonicalEntry(
        canonical_id=canonical_id,
        display_names=display_names,
        category=category,
        revision=revision,
        source_rule_id=source_rule_id,
    ))


def resolve_canonical_id(display_name: str, locale: str = "zh") -> Optional[str]:
    """通过显示名解析 canonical_id。"""
    return _registry.resolve_by_display_name(display_name, locale)
