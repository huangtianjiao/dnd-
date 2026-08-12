"""共享依赖与工具函数 — 多个路由模块共用的 Pydantic 模型、校验器、初始化器。"""

from __future__ import annotations

import re

from fastapi import HTTPException
from pydantic import BaseModel, field_validator


# ── SEC-001: 输入校验常量 ────────────────────────────────────────────────

# 骰式表达式白名单: NdM+K / NdM-K / NdM 格式
_DICE_EXPR_RE = re.compile(r'^\d+d\d+([+-]\d+)?$')

# 名称字段禁止的特殊字符（防注入）
_NAME_INJECT_RE = re.compile(r'[<>{}\[\]|\\;`$()\'"]')

# 数值合理范围
_HP_MIN, _HP_MAX = 0, 999
_AC_MIN, _AC_MAX = 1, 50
_SPEED_MIN, _SPEED_MAX = 5, 200
_LEVEL_MIN, _LEVEL_MAX = 1, 20
_ABILITY_MIN, _ABILITY_MAX = 1, 30


# ── Pydantic 请求体模型 ──────────────────────────────────────────────────────

class CampaignIn(BaseModel):
    name: str


class CharIn(BaseModel):
    name: str
    race: str = "人类"
    char_class: str = "战士"
    subclass: str = ""
    background: str = ""
    alignment: str = "绝对中立"
    level: int = 1
    abilities: dict = {"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10}
    hp_max: int = 10
    ac: int = 10
    speed: int = 30
    equipped_weapon: str = ""
    campaign_id: int | None = None
    ability_method: str = "free"

    # SEC-001: 输入校验
    @field_validator("name")
    @classmethod
    def _validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("名称不能为空")
        if len(v) > 50:
            raise ValueError("名称不能超过50字符")
        if _NAME_INJECT_RE.search(v):
            raise ValueError("名称包含非法字符")
        return v.strip()

    @field_validator("hp_max")
    @classmethod
    def _validate_hp(cls, v: int) -> int:
        if not (_HP_MIN < v <= _HP_MAX):
            raise ValueError(f"HP上限须在 {_HP_MIN+1}-{_HP_MAX} 范围内")
        return v

    @field_validator("ac")
    @classmethod
    def _validate_ac(cls, v: int) -> int:
        if not (_AC_MIN <= v <= _AC_MAX):
            raise ValueError(f"AC须在 {_AC_MIN}-{_AC_MAX} 范围内")
        return v

    @field_validator("speed")
    @classmethod
    def _validate_speed(cls, v: int) -> int:
        if not (_SPEED_MIN <= v <= _SPEED_MAX):
            raise ValueError(f"速度须在 {_SPEED_MIN}-{_SPEED_MAX} 范围内")
        return v

    @field_validator("level")
    @classmethod
    def _validate_level(cls, v: int) -> int:
        if not (_LEVEL_MIN <= v <= _LEVEL_MAX):
            raise ValueError(f"等级须在 {_LEVEL_MIN}-{_LEVEL_MAX} 范围内")
        return v

    @field_validator("abilities")
    @classmethod
    def _validate_abilities(cls, v: dict) -> dict:
        for k, val in v.items():
            if k not in ("str", "dex", "con", "int", "wis", "cha"):
                raise ValueError(f"未知属性 {k}")
            if not (_ABILITY_MIN <= int(val) <= _ABILITY_MAX):
                raise ValueError(f"属性值须在 {_ABILITY_MIN}-{_ABILITY_MAX} 范围内")
        return v

    @field_validator("race", "char_class", "subclass", "background", "alignment", "equipped_weapon")
    @classmethod
    def _validate_text_fields(cls, v: str) -> str:
        if len(v) > 100:
            raise ValueError("字段长度不能超过100字符")
        if _NAME_INJECT_RE.search(v):
            raise ValueError("字段包含非法字符")
        return v


class ChatIn(BaseModel):
    player_input: str
    campaign_id: int
    character_id: int
    thread_id: str = "default"   # P1-02: 服务器忽略客户端值，改用权威线程 ID
    hitl: bool = False
    # P1-04: 幂等键（可选；同 command_id 重复提交不重复执行）
    command_id: str = ""
    # P1-05: 战役乐观锁版本（可选；不匹配返回 409 STALE_VERSION）
    expected_version: int | None = None

    # SEC-001: 输入校验
    @field_validator("player_input")
    @classmethod
    def _validate_player_input(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("玩家输入不能为空")
        if len(v) > 2000:
            raise ValueError("玩家输入不能超过2000字符")
        return v.strip()

    @field_validator("thread_id")
    @classmethod
    def _validate_thread_id(cls, v: str) -> str:
        if len(v) > 200:
            raise ValueError("thread_id 过长")
        if _NAME_INJECT_RE.search(v):
            raise ValueError("thread_id 包含非法字符")
        return v

    @field_validator("command_id")
    @classmethod
    def _validate_command_id(cls, v: str) -> str:
        if len(v) > 100:
            raise ValueError("command_id 过长")
        return v


class ResumeIn(BaseModel):
    thread_id: str
    answer: str = "y"
    character_id: int = 0   # P1-03: 恢复者的角色身份（ownership 校验）


class JoinIn(BaseModel):
    name: str
    race: str = "人类"
    char_class: str = "战士"
    subclass: str = ""
    background: str = ""
    alignment: str = "绝对中立"
    level: int = 5
    abilities: dict = {"str": 16, "dex": 10, "con": 15, "int": 10, "wis": 12, "cha": 10}
    ability_method: str = "free"
    hp_max: int = 38
    ac: int = 18
    speed: int = 30
    equipped_weapon: str = ""
    campaign_id: int

    # SEC-001: 输入校验（与 CharIn 同口径）
    @field_validator("name")
    @classmethod
    def _validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("名称不能为空")
        if len(v) > 50:
            raise ValueError("名称不能超过50字符")
        if _NAME_INJECT_RE.search(v):
            raise ValueError("名称包含非法字符")
        return v.strip()

    @field_validator("hp_max")
    @classmethod
    def _validate_hp(cls, v: int) -> int:
        if not (_HP_MIN < v <= _HP_MAX):
            raise ValueError(f"HP上限须在 {_HP_MIN+1}-{_HP_MAX} 范围内")
        return v

    @field_validator("ac")
    @classmethod
    def _validate_ac(cls, v: int) -> int:
        if not (_AC_MIN <= v <= _AC_MAX):
            raise ValueError(f"AC须在 {_AC_MIN}-{_AC_MAX} 范围内")
        return v

    @field_validator("speed")
    @classmethod
    def _validate_speed(cls, v: int) -> int:
        if not (_SPEED_MIN <= v <= _SPEED_MAX):
            raise ValueError(f"速度须在 {_SPEED_MIN}-{_SPEED_MAX} 范围内")
        return v

    @field_validator("level")
    @classmethod
    def _validate_level(cls, v: int) -> int:
        if not (_LEVEL_MIN <= v <= _LEVEL_MAX):
            raise ValueError(f"等级须在 {_LEVEL_MIN}-{_LEVEL_MAX} 范围内")
        return v

    @field_validator("abilities")
    @classmethod
    def _validate_abilities(cls, v: dict) -> dict:
        for k, val in v.items():
            if k not in ("str", "dex", "con", "int", "wis", "cha"):
                raise ValueError(f"未知属性 {k}")
            if not (_ABILITY_MIN <= int(val) <= _ABILITY_MAX):
                raise ValueError(f"属性值须在 {_ABILITY_MIN}-{_ABILITY_MAX} 范围内")
        return v

    @field_validator("race", "char_class", "subclass", "background", "alignment", "equipped_weapon")
    @classmethod
    def _validate_text_fields(cls, v: str) -> str:
        if len(v) > 100:
            raise ValueError("字段长度不能超过100字符")
        if _NAME_INJECT_RE.search(v):
            raise ValueError("字段包含非法字符")
        return v


class OpenIn(BaseModel):
    setting: str
    tone: str = ""
    campaign_id: int
    character_id: int


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def validate_abilities(abilities: dict, method: str) -> None:
    """按 D&D 5e 属性生成方式校验，非法抛 422。

    复用 brain/char_create 的规则（标准阵列/购点法/掷骰），
    这些原本未接入 HTTP，POST /character 之前对属性完全不校验。
    """
    if not method or method == "free":
        return
    from ...brain.char_create import STANDARD_ARRAY, validate_point_buy
    vals = list(abilities.values())
    if method == "standard_array":
        if sorted(vals) != sorted(STANDARD_ARRAY):
            raise HTTPException(422, detail={"error": "invalid_abilities",
                "message": "标准阵列须为 [15,14,13,12,10,8] 的排列"})
    elif method == "point_buy":
        if not validate_point_buy(vals):
            raise HTTPException(422, detail={"error": "invalid_abilities",
                "message": "购点法：6项各8-15，总花费≤27"})
    elif method == "roll" and (len(vals) != 6 or any(not (3 <= int(v) <= 18) for v in vals)):
        raise HTTPException(422, detail={"error": "invalid_abilities",
            "message": "掷骰属性：6项各3-18"})


def init_loadout(ch, equipped_weapon: str = "") -> None:
    """角色创建时统一初始化拥有物：法术位/已学法术/起始武器入包。

    拥有性门控（R-SPL-036 职业法术列表 / R-ITM-012 武器表）：
      - 施法职业按等级初始化法术位（R-SPL-002）与 known_spells；
      - 起始武器写入 equipped_weapon 并加入 inventory（后续
        /equip-weapon 与攻击结算只认 inventory 内的武器）。
    三处创建入口（/character、/join、/room/join）共用，避免漏初始化。
    """
    from ...data import classes as _cls
    from ...data import spells as _sp
    from ...data.equipment import default_weapon_for_class
    try:
        _cdef = _cls.get_class(ch.char_class)
        if _cdef and _cdef.get("spellcasting"):
            ch.set_spell_slots(_sp.max_spell_slots(ch.level))
            ch.set_known_spells(_sp.default_known_spells(ch.char_class, ch.level))
    except Exception:
        pass
    ch.equipped_weapon = equipped_weapon or default_weapon_for_class(ch.char_class)
    if ch.equipped_weapon:
        ch.add_to_inventory(ch.equipped_weapon)
