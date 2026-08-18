"""共享依赖与工具函数 — 多个路由模块共用的 Pydantic 模型、校验器、初始化器。"""

from __future__ import annotations

import re

from fastapi import Header, HTTPException
from pydantic import BaseModel, Field, field_validator

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
    # 规则模式（方案 §2.1）: 默认 raw_2024；house_rule 必须有显式 house_rule_pack
    rules_mode: str = "raw_2024"

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

    @field_validator("rules_mode")
    @classmethod
    def _validate_rules_mode(cls, v: str) -> str:
        from ...engine.ruleset_manifest import RulesMode
        try:
            return RulesMode(v).value
        except ValueError:
            raise ValueError(
                f"未知规则模式 {v!r}，可选: {[m.value for m in RulesMode]}"
            ) from None


class CharIn(BaseModel):
    name: str
    race: str = "人类"
    char_class: str = "战士"
    subclass: str = ""
    background: str = ""
    alignment: str = "绝对中立"
    level: int = 1
    abilities: dict = {"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10}
    # ★ P1-01/审查#13: 客户端提交值被服务器忽略（deprecated）
    hp_max: int = Field(10, deprecated=True)
    ac: int = Field(10, deprecated=True)
    speed: int = Field(30, deprecated=True)
    equipped_weapon: str = ""
    campaign_id: int | None = None
    ability_method: str = "free"
    # ★ P3（方案 §6.3）: 背景技能选择（英文 key；省略时跳过背景技能数量校验）
    skills: list[str] = []

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
    # ★ P1-01/审查#13: 客户端提交值被服务器忽略（deprecated）
    hp_max: int = Field(38, deprecated=True)
    ac: int = Field(18, deprecated=True)
    speed: int = Field(30, deprecated=True)
    equipped_weapon: str = ""
    campaign_id: int
    # ★ P3（方案 §6.3）: 背景技能选择（英文 key；省略时跳过背景技能数量校验）
    skills: list[str] = []

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


# ── P3（方案 §6.1）: 唯一构建服务接入点 ────────────────────────────────

def validate_build_plan(race: str, char_class: str, subclass: str,
                        background: str, abilities: dict,
                        skills: list[str] | None = None) -> None:
    """所有创建入口共用 CharacterBuilder 校验，非法选择 → 422（fail closed）。

    规则: 方案 §2.1 RAW_2024 — 非法创建拒绝，任何入口不得绕过。
    """
    from ...build.character_builder import CharacterBuilder, build_plan_from_request
    from ...rules.choice import ChoiceManager
    from ...rules.grant import GrantManager
    from ...rules.resource import ResourceManager

    plan = build_plan_from_request(
        name="", race=race, char_class=char_class, subclass=subclass,
        background=background, abilities=abilities, skills=skills)
    builder = CharacterBuilder(GrantManager(), ChoiceManager(), ResourceManager())
    errors = builder.validate_build(plan)
    if errors:
        raise HTTPException(status_code=422, detail={
            "error": "invalid_character_build",
            "message": "角色创建非法: " + "; ".join(errors[:5]),
            "reasons": errors[:10],
        })


def persist_build_provenance(ch, race: str, char_class: str, subclass: str,
                             background: str, abilities: dict,
                             skills: list[str] | None = None,
                             db_path: str | None = None) -> None:
    """创建落库后写入 Grant/Choice provenance（方案 §5.3，幂等）。"""
    from ...build.character_builder import build_plan_from_request
    from ...build.character_builder import persist_build_provenance as _persist
    plan = build_plan_from_request(
        name="", race=race, char_class=char_class, subclass=subclass,
        background=background, abilities=abilities, skills=skills)
    _persist(ch, plan, db_path)


def init_resource_pools(ch) -> None:
    """创建时初始化持久化资源池与生命骰（P6，方案 §9.1）。

    - 生命骰: 1 级 = 1 枚（hit_dice_max/current = 等级，R-GLS-014 语义）
    - 资源池: 上限来自 class level 公式表（目前覆盖战士回气、野蛮人狂暴）
    """
    # 生命骰初始化（短休消耗的基础；旧角色由 migration 兜底）
    if ch.hit_dice_max <= 0:
        ch.hit_dice_max = ch.level
        ch.hit_dice_current = ch.level
    pools: dict = {}
    if ch.char_class == "战士":
        from ...data.classes import FIGHTER_SECOND_WIND_BY_LEVEL
        pools["second_wind"] = {
            "current": FIGHTER_SECOND_WIND_BY_LEVEL.get(ch.level, 2),
            "max": FIGHTER_SECOND_WIND_BY_LEVEL.get(ch.level, 2),
            "recharge": "short_rest",
            "source_feature_id": "fighter_second_wind",
        }
    elif ch.char_class == "野蛮人":
        from ...data.classes import get_rage_uses
        pools["rage"] = {
            "current": get_rage_uses(ch.level),
            "max": get_rage_uses(ch.level),
            "recharge": "short_rest",
            "source_feature_id": "barbarian_rage",
        }
    if pools:
        ch.set_resource_pools(pools)


def _mastery_seed(count: int) -> list:
    """战士初始精通 seed（P8: 演示；具体选择待 choice API 重选）。"""
    from ...engine.mastery import MASTERY_NAME_MAP
    names = list(MASTERY_NAME_MAP.keys())
    return names[:max(0, int(count))]


def init_loadout(ch, equipped_weapon: str = "") -> None:
    """角色创建时统一初始化拥有物：法术位/法术来源/起始武器入包。

    拥有性门控（R-SPL-036 职业法术列表 / R-ITM-012 武器表）：
      - 施法职业按等级初始化法术位（R-SPL-002）；
      - 法术按 P7（方案 §10.2/§10.3）施法模型分来源初始化：
          * 已知制（吟游诗人/术士/魔契师）→ known_spells（demo seed 截断到数量表）
          * 法术书制（法师）→ spellbook_spells（seed 进法术书，不自动准备）
          * 准备制（牧师/德鲁伊/圣武士/游侠）→ prepared_spells（seed 前 N 个，
            N=prepared_spells_count）——N 由 cast 服务强制校验
        default_known_spells 保留为 demo/seed 工具（方案 §10.1 允许），
        不再作为 API 读取的生产 fallback。
      - 起始武器写入 equipped_weapon 并加入 inventory。
    三处创建入口（/character、/join、/room/join）共用，避免漏初始化。
    """
    from ...data import classes as _cls
    from ...data.equipment import default_weapon_for_class
    from ...rules.spellcasting import (
        known_spells_count, model_for, prepared_spells_count)
    try:
        _cdef = _cls.get_class(ch.char_class)
        if _cdef and _cdef.get("spellcasting"):
            from ...data import spells as _sp
            ch.set_spell_slots(_sp.max_spell_slots(ch.level))
            m = model_for(ch.char_class)
            if m is not None:
                # demo seed（方案 §10.1: 保留为创建演示工具）
                seed = _sp.default_known_spells(ch.char_class, ch.level)
                if m.preparation_model.value in ("known", "pact"):
                    limit = known_spells_count(ch.char_class, ch.level)
                    ch.set_known_spells(seed[:limit])
                elif m.preparation_model.value == "spellbook":
                    ch.set_spellbook_spells(seed)
                else:  # prepared
                    limit = prepared_spells_count(
                        ch.char_class, ch.level, ch.ability_mod(m.casting_ability))
                    ch.set_prepared_spells(seed[:limit])
    except Exception:
        pass  # spellcasting 初始化失败不阻断角色创建（后续可经 choice API 补齐）
    ch.equipped_weapon = equipped_weapon or default_weapon_for_class(ch.char_class)
    if ch.equipped_weapon:
        ch.add_to_inventory(ch.equipped_weapon)
    # P8（方案 §11.2）: MasteryGrant 持久化——战士 1 级武器精通授权
    # （数量按公式表；具体精通演示 seed，之后经 choice API 重选）
    if ch.char_class == "战士":
        from ...data.classes import FIGHTER_MASTERY_BY_LEVEL
        count = FIGHTER_MASTERY_BY_LEVEL.get(ch.level, 3)
        for mc in _mastery_seed(count):
            ch.add_mastery_grant(mc, source_id="class.fighter.level1",
                                 acquired_level=1)


# ── P0-4: Session Ownership 校验（IDOR 防护）────────────────────────

def require_session(authorization: str | None = Header(default=None)) -> dict:
    """FastAPI 依赖：解析 Bearer 会话令牌，返回 claims（无效 → 401）。

    规则: P0-4 — REST 角色/战役资源接口必须校验调用者归属，
    防止 IDOR（仅凭 ID 访问/修改他人资源）。
    """
    from ..session_tokens import parse_session_token
    claims = None
    if authorization and authorization.lower().startswith("bearer "):
        claims = parse_session_token(authorization[7:].strip())
    if claims is None:
        raise HTTPException(status_code=401, detail={
            "error": "UNAUTHORIZED",
            "message": "缺少或无效的会话令牌（请先连接游戏会话）"})
    return claims


def require_character_owner(cid: int, claims: dict) -> None:
    """校验调用者对该角色卡的归属（本人 或 DM/房主）。

    规则: P0-4 — character_id 与令牌绑定不一致 → 403（fail closed）。
    """
    from ..session_tokens import ROLE_DM, ROLE_HOST
    # claims 为 SessionClaims dataclass（属性访问）
    role = getattr(claims, "role", None)
    if role in (ROLE_DM, ROLE_HOST):
        return
    if int(getattr(claims, "character_id", 0) or 0) != int(cid):
        raise HTTPException(status_code=403, detail={
            "error": "FORBIDDEN",
            "message": "无权访问该角色（会话令牌与角色不匹配）"})


def require_campaign_owner(campaign_id: int, claims: dict) -> None:
    """校验调用者对该战役的归属（令牌 campaign 绑定一致 或 DM/房主）。

    规则: P0-4 — 跨战役访问 → 403。
    """
    from ..session_tokens import ROLE_DM, ROLE_HOST
    role = getattr(claims, "role", None)
    if role in (ROLE_DM, ROLE_HOST):
        return
    if int(getattr(claims, "campaign_id", 0) or 0) != int(campaign_id):
        raise HTTPException(status_code=403, detail={
            "error": "FORBIDDEN",
            "message": "无权访问该战役（会话令牌与战役不匹配）"})
