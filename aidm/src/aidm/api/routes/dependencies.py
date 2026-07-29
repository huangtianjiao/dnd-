"""共享依赖与工具函数 — 多个路由模块共用的 Pydantic 模型、校验器、初始化器。"""

from __future__ import annotations

from fastapi import HTTPException
from pydantic import BaseModel


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


class ChatIn(BaseModel):
    player_input: str
    campaign_id: int
    character_id: int
    thread_id: str = "default"
    hitl: bool = False


class ResumeIn(BaseModel):
    thread_id: str
    answer: str = "y"


class JoinIn(BaseModel):
    name: str
    race: str = "人类"
    char_class: str = "战士"
    level: int = 5
    abilities: dict = {"str": 16, "dex": 10, "con": 15, "int": 10, "wis": 12, "cha": 10}
    hp_max: int = 38
    ac: int = 18
    equipped_weapon: str = ""
    campaign_id: int


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
