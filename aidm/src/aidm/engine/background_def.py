"""背景定义 — BackgroundDefinition。

CHR-005: 背景选择与起源专长没有完整约束。
BackgroundDefinition包含属性选项、技能、工具、装备包、起源专长；CharacterBuilder执行约束求解。

规则依据: topics/玩家手册2024/角色创建/背景.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EquipmentPack:
    """起始装备包。"""

    items: List[str] = field(default_factory=list)
    gold: int = 0


@dataclass
class BackgroundDefinition:
    """背景完整定义。

    CHR-005: 统一可执行的背景定义。
    """

    background_id: str                    # canonical ID
    name: str                              # 中文名
    skill_choices: List[str] = field(default_factory=list)   # 可选技能列表
    skill_count: int = 2                   # 选择数量
    tool_choices: List[str] = field(default_factory=list)
    tool_count: int = 1
    languages_count: int = 0               # 额外语言数量
    origin_feat: str = ""                  # 起源专长 ID
    equipment: EquipmentPack = field(default_factory=EquipmentPack)
    feature_name: str = ""                 # 背景特性名
    feature_description: str = ""

    def validate_skill_selection(self, selected: List[str]) -> bool:
        """验证技能选择是否合法。"""
        if len(selected) != self.skill_count:
            return False
        for s in selected:
            if s not in self.skill_choices:
                return False
        return True

    def validate_tool_selection(self, selected: List[str]) -> bool:
        """验证工具选择是否合法。"""
        if len(selected) != self.tool_count:
            return False
        for t in selected:
            if t not in self.tool_choices:
                return False
        return True


# ── 背景注册表 ──────────────────────────────────────────────────

@dataclass
class BackgroundRegistry:
    """背景注册表 — 管理所有已定义背景。"""

    _backgrounds: Dict[str, BackgroundDefinition] = field(default_factory=dict)

    def register(self, bg: BackgroundDefinition) -> None:
        """注册一个背景定义。"""
        self._backgrounds[bg.background_id] = bg

    def get(self, bg_id: str) -> BackgroundDefinition | None:
        """获取指定背景的定义。"""
        return self._backgrounds.get(bg_id)

    def list_all(self) -> List[str]:
        """列出所有已注册背景 ID。"""
        return list(self._backgrounds.keys())
