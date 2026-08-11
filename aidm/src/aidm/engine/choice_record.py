"""角色创建选择来源与验证轨迹 — ChoiceRecord / Grant。

CHAR-008: 角色创建缺少选择来源和验证轨迹。
保存Grant记录与ChoiceRecord；派生字段从grant重建。

规则依据: topics/玩家手册2024/角色创建/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class GrantType(str, Enum):
    """授予类型。"""

    SPECIES = "species"
    BACKGROUND = "background"
    CLASS = "class"
    SUBCLASS = "subclass"
    FEAT = "feat"
    ITEM = "item"
    SKILL = "skill"
    TOOL = "tool"
    LANGUAGE = "language"
    SPELL = "spell"


@dataclass
class Grant:
    """单条授予记录。

    CHAR-008: 追踪每个能力/资源的来源。
    """

    grant_type: GrantType
    source_id: str = ""           # 来源 ID（物种 ID、职业 ID 等）
    source_name: str = ""         # 来源名称
    granted_item: str = ""        # 授予的项目名
    level: int = 1                # 获取等级
    metadata: dict = field(default_factory=dict)


@dataclass
class ChoiceRecord:
    """选择记录 — 记录角色在创建过程中做出的每一项选择。

    CHAR-008: 保存完整来源清单，重新构建后数值一致。
    """

    choice_id: str = ""
    choice_type: str = ""         # species/background/class/subclass/feat/skill/tool/language
    selected_value: str = ""      # 选中的值
    available_options: List[str] = field(default_factory=list)
    level_at_choice: int = 1
    validated: bool = False       # 是否通过约束验证

    def to_dict(self) -> dict:
        """序列化为字典。"""
        return {
            "id": self.choice_id,
            "type": self.choice_type,
            "value": self.selected_value,
            "options": list(self.available_options),
            "level": self.level_at_choice,
            "validated": self.validated,
        }


@dataclass
class CharacterBuildLog:
    """角色构建日志 — 完整记录创建过程中的所有授予和选择。

    CHAR-008: 角色可输出完整来源清单，重新构建后数值一致。
    """

    character_id: str = ""
    grants: List[Grant] = field(default_factory=list)
    choices: List[ChoiceRecord] = field(default_factory=list)

    def add_grant(self, grant: Grant) -> None:
        """添加一条授予记录。"""
        self.grants.append(grant)

    def add_choice(self, choice: ChoiceRecord) -> None:
        """添加一条选择记录。"""
        self.choices.append(choice)

    def get_grants_by_type(self, grant_type: GrantType) -> List[Grant]:
        """按类型获取所有授予记录。"""
        return [g for g in self.grants if g.grant_type == grant_type]

    def get_all_sources(self) -> List[str]:
        """获取所有来源 ID（去重）。"""
        return list({g.source_id for g in self.grants if g.source_id})

    def to_dict(self) -> dict:
        """序列化为字典。"""
        return {
            "character_id": self.character_id,
            "grants": [
                {
                    "type": g.grant_type.value,
                    "source_id": g.source_id,
                    "source_name": g.source_name,
                    "item": g.granted_item,
                    "level": g.level,
                }
                for g in self.grants
            ],
            "choices": [
                {
                    "id": c.choice_id,
                    "type": c.choice_type,
                    "value": c.selected_value,
                    "options": c.available_options,
                    "level": c.level_at_choice,
                    "validated": c.validated,
                }
                for c in self.choices
            ],
        }
