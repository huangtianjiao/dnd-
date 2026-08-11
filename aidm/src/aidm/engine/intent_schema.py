"""意图层严格校验 — Pydantic IntentSchema 白名单与边界校验。

设计原则：
  - 所有意图字段使用 Pydantic 严格模型验证。
  - action_type 只接受白名单枚举值。
  - 骰式必须匹配正则，不接受任意表达式。
  - 字符串字段有长度上限，数值字段有范围约束。

规则依据: SEC-001 自由文本规则字段缺少白名单与边界校验
"""

from __future__ import annotations

import re
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ActionType(str, Enum):
    """合法动作类型白名单。"""
    ATTACK = "attack"
    CAST = "cast"
    ABILITY_CHECK = "ability_check"
    EXPLORE = "explore"
    START_COMBAT = "start_combat"
    END_COMBAT = "end_combat"
    REST = "rest"
    SOCIAL = "social"
    LEVELUP = "levelup"
    TRAVEL = "travel"
    DASH = "dash"
    DODGE = "dodge"
    DISENGAGE = "disengage"
    HELP = "help"
    HIDE = "hide"
    SEARCH = "search"
    STUDY = "study"
    USE_ITEM = "use_item"
    GRAPPLE = "grapple"
    SHOVE = "shove"
    READY = "ready"
    OPPORTUNITY_ATTACK = "opportunity_attack"
    OTHER = "other"


# 骰式正则：只允许 NdM[+/-K] 格式
_DICE_PATTERN = re.compile(r"^\d+d\d+(?:[+-]\d+)?$")


class IntentSchema(BaseModel):
    """★ SEC-001: 意图层严格校验模型。

    所有字段都有白名单或边界约束：
      - action_type: 枚举白名单
      - ability: str/dex/con/int/wis/cha
      - spell_level: 0-9
      - spell_dice: 必须匹配骰式正则
      - damage_type: 白名单枚举
      - target_name: 最大长度100
      - weapon: 最大长度50
    """

    action_type: ActionType = ActionType.OTHER
    target_name: str = Field(default="", max_length=100)
    target_cid: str = Field(default="", max_length=50)
    weapon: str = Field(default="", max_length=50)
    spell_name: str = Field(default="", max_length=100)
    spell_level: int = Field(default=0, ge=0, le=9)
    spell_dice: str = Field(default="", max_length=30)
    damage_type: str = Field(default="", max_length=30)
    ability: str = Field(default="str", max_length=3)
    skill: str = Field(default="", max_length=50)
    dc: int = Field(default=10, ge=1, le=40)
    needs_check: bool = True
    retrieval_query: str = Field(default="", max_length=200)

    @field_validator("spell_dice")
    @classmethod
    def validate_spell_dice(cls, v: str) -> str:
        """骰式必须匹配 NdM[+/-K] 格式。"""
        if v and not _DICE_PATTERN.match(v):
            raise ValueError(f"非法骰式: {v!r}, 只允许 NdM[+/-K] 格式")
        return v

    @field_validator("ability")
    @classmethod
    def validate_ability(cls, v: str) -> str:
        """属性缩写必须在白名单内。"""
        allowed = {"str", "dex", "con", "int", "wis", "cha"}
        if v.lower() not in allowed:
            raise ValueError(f"非法属性: {v!r}, 允许: {allowed}")
        return v.lower()

    @field_validator("damage_type")
    @classmethod
    def validate_damage_type(cls, v: str) -> str:
        """伤害类型在白名单内。"""
        if not v:
            return v
        allowed = {
            "slashing", "piercing", "bludgeoning",
            "fire", "cold", "lightning", "thunder", "acid", "poison",
            "psychic", "radiant", "necrotic", "force",
            "挥砍", "穿刺", "钝击",
            "火焰", "寒冷", "闪电", "雷鸣", "酸蚀", "毒素",
            "心灵", "光耀", "死灵", "力场",
            "heal", "治疗",
        }
        if v.lower() not in allowed:
            raise ValueError(f"非法伤害类型: {v!r}")
        return v


def validate_intent(intent: dict) -> dict:
    """验证并清洗意图字典。

    ★ SEC-001: 使用 IntentSchema 严格验证。
      - 非法字段被拒绝（抛出 ValueError）
      - 多余字段被忽略
      - 缺失字段使用默认值

    Returns:
        清洗后的意图字典
    """
    try:
        schema = IntentSchema(**intent)
        return schema.model_dump()
    except Exception as e:
        raise ValueError(f"意图校验失败: {e}") from e
