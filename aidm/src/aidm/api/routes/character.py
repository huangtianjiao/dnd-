"""角色管理路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...data import magic_items as mi_db
from ...stats import models, store
from .dependencies import (
    CharIn,
    JoinIn,
    init_loadout,
    init_resource_pools,
    persist_build_provenance,
    require_character_owner,
    require_session,
    validate_abilities,
    validate_build_plan,
)

router = APIRouter(tags=["character"])


class RestIn(BaseModel):
    type: str = "short"   # short | long


class AttuneIn(BaseModel):
    item_name: str


class BreakAttuneIn(BaseModel):
    item_name: str


class EquipWeaponIn(BaseModel):
    weapon_name: str


class ChoiceSubmitIn(BaseModel):
    value: str = ""


class LevelUpIn(BaseModel):
    new_class: str = ""          # 兼职目标职业（中文名）；空 = 原职业升级
    use_fixed_hp: bool = True    # 固定 HP 增长（平均骰）


class PrepareSpellIn(BaseModel):
    spell_name: str


@router.post("/character")
def create_character(c: CharIn):
    # ★ P3: 所有创建入口共用 CharacterBuilder 校验（非法选择 → 422）
    validate_build_plan(c.race, c.char_class, c.subclass, c.background,
                        c.abilities, c.skills)
    ch = models.Character(name=c.name, race=c.race, char_class=c.char_class,
                          subclass=c.subclass, background=c.background,
                          alignment=c.alignment, level=c.level,
                          campaign_id=c.campaign_id)
    validate_abilities(c.abilities, c.ability_method)
    ch.set_abilities(c.abilities)
    # ★ P1-01: 机械属性由服务器权威计算（HP/AC/速度），客户端提交值被忽略
    from ...build.derive_stats import apply_server_stats
    apply_server_stats(ch, c.char_class, c.race, c.level, c.abilities)
    # ★ DATA-002: 注册职业 canonical_id（稳定标识，显示名作为 locale 资源）
    try:
        from ...engine.canonical_id import register_canonical
        # canonical_id 格式: namespace.slug（class.<英文slug>）
        _slug_map = {
            "野蛮人": "barbarian", "吟游诗人": "bard", "牧师": "cleric",
            "德鲁伊": "druid", "战士": "fighter", "武僧": "monk",
            "圣武士": "paladin", "游侠": "ranger", "盗贼": "rogue",
            "术士": "sorcerer", "魔契师": "warlock", "法师": "wizard",
        }
        _class_slug = _slug_map.get(c.char_class, c.char_class.lower())
        register_canonical(
            canonical_id=f"class.{_class_slug}",
            display_names={"zh": c.char_class},
            category="class",
        )
        ch.class_canonical_id = f"class.{_class_slug}"
    except Exception:
        pass  # canonical_id 为增强元数据，失败不阻断
    # 统一初始化拥有物：法术位 + 已学法术 + 起始武器入包（拥有性门控）
    init_loadout(ch, c.equipped_weapon)
    # P6: 持久化资源池初始化（上限来自公式表）
    init_resource_pools(ch)
    ch = store.save_character(ch)
    # ★ P3: Grant/Choice provenance 落库（幂等，方法 5.3）
    persist_build_provenance(ch, c.race, c.char_class, c.subclass,
                             c.background, c.abilities, c.skills)
    return {"id": ch.id, "name": ch.name, "hp": ch.hp_current, "ac": ch.ac}


@router.get("/character/{cid}")
def get_character(cid: int, claims: dict = Depends(require_session)):
    """角色卡全数据（前端角色面板用）。

    ★ P0-4: 会话归属校验——只能读自己的角色（或 DM/房主）。
    """
    require_character_owner(cid, claims)
    from ...engine import dice
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    ab = ch.abilities
    # P7（方案 §10.1）: 不再以职业列表自动回退 known_spells——
    # 空即空（来源只能由创建/选择写入），展示层按来源字段消费。
    _known = ch.known_spells
    return {"id": ch.id, "name": ch.name, "race": ch.race, "char_class": ch.char_class,
            "subclass": ch.subclass, "background": ch.background,
            "alignment": ch.alignment, "level": ch.level, "proficiency": ch.prof(),
            "abilities": {k: {"score": v, "mod": dice.ability_modifier(v)} for k, v in ab.items()},
            "hp": ch.hp_current, "hp_max": ch.hp_max, "temp_hp": ch.temp_hp, "ac": ch.ac,
            "speed": ch.speed, "conditions": ch.conditions_list, "exhaustion": ch.exhaustion,
            "spell_slots": ch.spell_slots, "known_spells": _known,
            "prepared_spells": ch.prepared_spells,
            "spellbook_spells": ch.spellbook_spells,
            "always_prepared_spells": ch.always_prepared_spells,
            "hit_dice_current": getattr(ch, "hit_dice_current", ch.level),
            "hit_dice_max": ch.level,
            "death_successes": ch.death_successes, "death_failures": ch.death_failures,
            "dead": ch.dead, "stable": ch.stable,
            "attuned_items": ch.attuned_items, "equipped_weapon": ch.equipped_weapon}


@router.get("/character/{cid}/inventory")
def get_inventory(cid: int, claims: dict = Depends(require_session)):
    """获取角色完整物品栏。

    ★ P0-4: 归属校验。
    """
    require_character_owner(cid, claims)
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})

    inv_names = ch.inventory
    attuned = ch.attuned_items

    from ...data import equipment as equip_db
    magic_items_detail = []
    weapons_detail = []
    for name in inv_names:
        item = mi_db.get_magic_item(name)
        if item is not None:
            d = item.to_dict()
            d["attuned"] = name in attuned
            magic_items_detail.append(d)
        elif name in equip_db.WEAPONS:
            entry = equip_db.WEAPONS[name]
            weapons_detail.append({
                "name": name, "category": entry["cat"], "damage": entry["dmg"],
                "properties": entry.get("props", []),
                "equipped": name == ch.equipped_weapon,
            })
    # 懒回填展示：历史角色起始武器未入包时，仍展示当前装备武器
    if ch.equipped_weapon and ch.equipped_weapon in equip_db.WEAPONS \
            and all(w["name"] != ch.equipped_weapon for w in weapons_detail):
        entry = equip_db.WEAPONS[ch.equipped_weapon]
        weapons_detail.append({
            "name": ch.equipped_weapon, "category": entry["cat"], "damage": entry["dmg"],
            "properties": entry.get("props", []), "equipped": True,
        })

    return {
        "character_id": cid,
        "inventory": inv_names,
        "attuned_items": attuned,
        "magic_items": magic_items_detail,
        "weapons": weapons_detail,
        "gold": ch.gold,
    }


@router.post("/character/{cid}/attune")
def attune_item(cid: int, req: AttuneIn,
                       claims: dict = Depends(require_session)):
    """★ P0-4: 归属校验。"""
    require_character_owner(cid, claims)
    """同调魔法物品。"""
    from ...brain import loot
    return loot.attune_magic_item(cid, req.item_name)


@router.post("/character/{cid}/break-attunement")
def break_attunement(cid: int, req: BreakAttuneIn,
                             claims: dict = Depends(require_session)):
    """★ P0-4: 归属校验。"""
    require_character_owner(cid, claims)
    """解除魔法物品同调。"""
    from ...brain import loot
    return loot.break_attunement(cid, req.item_name)


@router.post("/character/{cid}/equip-weapon")
def equip_weapon(cid: int, req: EquipWeaponIn,
                       claims: dict = Depends(require_session)):
    """★ P0-4: 归属校验。"""
    require_character_owner(cid, claims)
    """装备/更换当前手持武器。"""
    from ...data import equipment as equip_db
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    if req.weapon_name and req.weapon_name not in equip_db.WEAPONS:
        raise HTTPException(status_code=400, detail={"error": "invalid_request", "message": f"未知武器 {req.weapon_name!r}，可选示例: {list(equip_db.WEAPONS)[:10]}"})
    # 懒回填：历史角色创建时未把起始武器写入 inventory
    if ch.equipped_weapon and ch.equipped_weapon not in ch.inventory:
        ch.add_to_inventory(ch.equipped_weapon)
    if req.weapon_name and req.weapon_name not in ch.inventory:
        raise HTTPException(status_code=400, detail={
            "error": "not_owned",
            "message": f"未拥有武器 {req.weapon_name!r}，无法装备（需先通过战利品/购买获得）"})
    ch.equipped_weapon = req.weapon_name
    ch = store.save_character(ch)
    return {"character_id": ch.id, "equipped_weapon": ch.equipped_weapon}


@router.get("/character/{cid}/pending-choices")
def pending_choices(cid: int, claims: dict = Depends(require_session)):
    """返回角色所有未解决的选择（方案 §6.3/§8.3 Choice-driven UI）。

    升级/专长/子职等所有 entitlement 触发的选择统一沉淀为
    CharacterChoice(validated=False)；UI 只消费合法选项，不重复实现规则。
    """
    require_character_owner(cid, claims)
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    pending = [
        c.to_dict() for c in store.list_character_choices(cid)
        if not c.validated
    ]
    return {"character_id": cid, "pending_choices": pending, "count": len(pending)}


@router.post("/character/{cid}/choices/{choice_id}")
def submit_choice(cid: int, choice_id: str, req: ChoiceSubmitIn,
                  claims: dict = Depends(require_session)):
    """提交一个选择的解答案（方案 §8.3 统一 choice 系统）。

    校验: 选择必须存在且未解决；value 必须位于该选择的合法选项快照内
    （R-CHC 非法选择拒绝 → 422）。
    """
    require_character_owner(cid, claims)
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    candidates = [c for c in store.list_character_choices(cid)
                  if c.choice_id == choice_id]
    if not candidates:
        raise HTTPException(status_code=404, detail={
            "error": "choice_not_found", "message": f"选择 {choice_id!r} 不存在"})
    rec = candidates[0]
    if rec.validated:
        raise HTTPException(status_code=409, detail={
            "error": "choice_already_resolved",
            "message": f"选择 {choice_id!r} 已解决（幂等重放不改变状态）"})
    legal = rec.legal_options
    if legal and req.value and req.value not in legal:
        raise HTTPException(status_code=422, detail={
            "error": "invalid_choice",
            "message": f"值 {req.value!r} 不在合法选项内: {legal}",
        })
    resolved = store.resolve_character_choice(cid, choice_id, req.value)
    if resolved is None:
        raise HTTPException(status_code=404, detail={
            "error": "choice_not_found", "message": f"选择 {choice_id!r} 不存在"})
    return {"character_id": cid, "choice_id": choice_id,
            "resolved": True, "value": req.value}


@router.post("/character/{cid}/level-up")
def level_up_character(cid: int, req: LevelUpIn,
                       claims: dict = Depends(require_session)):
    """执行一次职业升级（方案 §8.1 LevelUpPlan 生产入口）。

    校验: owner guard + XP 足够 + 兼职先决（PrerequisiteEvaluator 由
    MulticlassService 承载）；结果原子落库，feat/ASI entitlement 落
    pending choices（§8.3 统一 choice 系统）。
    """
    require_character_owner(cid, claims)
    from ...build.level_up_service import apply_level_up
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    try:
        result = apply_level_up(ch, new_class=req.new_class,
                                use_fixed_hp=req.use_fixed_hp)
    except ValueError as e:
        raise HTTPException(status_code=422, detail={
            "error": "invalid_level_up", "message": str(e)}) from e
    return {k: v for k, v in result.items()
            if k in ("new_level", "hp_gained", "new_proficiency_bonus",
                     "pb_changed", "new_features", "asi_taken",
                     "feat_available", "available_feats", "character_id")}


@router.post("/character/{cid}/prepare-spell")
def prepare_spell_api(cid: int, req: PrepareSpellIn,
                      claims: dict = Depends(require_session)):
    """准备/更换一个法术（方案 §10.3 prepared_spells 唯一写入路径）。

    校验: owner guard + 准备制施法者 + 职业法术列表可及 + 数量上限
    （准备数 = 施法属性调整 + 施法者等级/半施法折半）。
    """
    require_character_owner(cid, claims)
    from ...rules.spellcasting import prepare_spell
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    try:
        result = prepare_spell(ch, req.spell_name)
    except ValueError as e:
        raise HTTPException(status_code=422, detail={
            "error": "invalid_prepare", "message": str(e)}) from e
    ch = store.save_character(ch)
    return {"character_id": cid, **result}


@router.delete("/character/{cid}/prepare-spell")
def unprepare_spell_api(cid: int, spell_name: str,
                        claims: dict = Depends(require_session)):
    """从 prepared_spells 移除一个法术（幂等）。"""
    require_character_owner(cid, claims)
    from ...rules.spellcasting import unprepared_spell
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    result = unprepared_spell(ch, spell_name)
    ch = store.save_character(ch)
    return {"character_id": cid, **result}


@router.get("/weapons")
def list_weapons():
    """返回所有可用武器列表。"""
    from ...data import equipment as equip_db
    weapons = []
    for name, entry in equip_db.WEAPONS.items():
        weapons.append({
            "name": name,
            "category": entry["cat"],
            "damage": entry["dmg"],
            "properties": entry.get("props", []),
            "weight": entry.get("wt"),
            "price": entry.get("price", ""),
        })
    return {"weapons": weapons, "count": len(weapons)}


@router.post("/character/{cid}/rest")
def rest_character(cid: int, req: RestIn,
                       claims: dict = Depends(require_session)):
    """★ P0-4: 归属校验 + P6（方案 §9.2）: 休息走 RestService 完整事务。

    API 不再自行挑选字段写回角色（HP/力竭/临时HP/法术位/生命骰/资源池
    全部由服务原子应用并落库）。
    """
    require_character_owner(cid, claims)
    from ...build.rest_service import apply_long_rest, apply_short_rest
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    if req.type == "short":
        result = apply_short_rest(ch, db_path=None)
    elif req.type == "long":
        result = apply_long_rest(ch)
    else:
        raise HTTPException(status_code=422, detail={"error": "invalid_type", "message": f"未知休息类型: {req.type}"})
    if not result.get("success"):
        raise HTTPException(status_code=422, detail={
            "error": "rest_failed",
            "message": "；".join(result.get("errors") or ["休息条件不满足"])})
    return {
        "success": True,
        "type": req.type,
        "applied": result.get("applied", True),
        "hp_restored": result.get("hp_restored", 0),
        "hp_current": result.get("hp_current"),
        "exhaustion_reduced": result.get("exhaustion_reduced", 0),
        "spell_slots_restored": result.get("spell_slots_restored", False),
        "hit_dice_spent": result.get("hit_dice_spent", 0),
        "hit_dice_remaining": result.get(
            "hit_dice_remaining",
            result.get("hit_dice_current", ch.hit_dice_current)),
        "exhaustion": result.get("exhaustion", ch.exhaustion),
        "pools_recharged": result.get("pools_recharged", []),
    }


@router.get("/races")
def list_races():
    """可扮演种族列表。"""
    from ...data.races import RACES
    return {"races": [
        {"name": n, "speed": r["speed"], "darkvision": r["darkvision"],
         "subraces": r["subraces"], "size": r["size"]}
        for n, r in RACES.items()
    ]}


@router.get("/classes")
def list_classes():
    """可选职业列表。"""
    from ...data.classes import CLASSES
    return {"classes": [
        {"name": n, "hit_die": c["hit_die"],
         "armor_training": c["armor_training"],
         "spellcasting": c["spellcasting"],
         "subclasses": c["subclasses"],
         "subclass_level": c["subclass_level"]}
        for n, c in CLASSES.items()
    ]}


@router.get("/roll-abilities")
def roll_abilities():
    """掷骰生成六项属性（4d6弃最低×6）。"""
    from ...brain.char_create import roll_ability_scores
    return {"values": roll_ability_scores()}


@router.get("/backgrounds")
def list_backgrounds():
    """可选背景列表。"""
    from ...data.backgrounds import BACKGROUNDS
    return {"backgrounds": [
        {"name": n, "ability_scores": b["ability_scores"],
         "feat": b["feat"], "skill_prof": b["skill_prof"],
         "tool_prof": b["tool_prof"], "equipment": b["equipment"]}
        for n, b in BACKGROUNDS.items()
    ]}


@router.get("/spells")
def list_spells(level: int | None = None):
    """法术列表（前端法术书用）。"""
    from ...data.spells import SPELLS
    from ...data.spells_full import SPELLS_FULL
    out = []
    for s in SPELLS.values():
        if level is not None and s.level != level:
            continue
        out.append({
            "name": s.name, "level": s.level, "school": s.school,
            "casting_time": s.casting_time, "range": s.range,
            "duration": s.duration,
            "components": sorted(s.components),
            "description": getattr(s, "description", ""),
        })
    for raw in SPELLS_FULL.values():
        if raw["name"] in SPELLS:
            continue
        if level is not None and raw["level"] != level:
            continue
        out.append({
            "name": raw["name"], "level": raw["level"], "school": raw.get("school", ""),
            "casting_time": raw.get("casting_time", ""), "range": raw.get("range", ""),
            "duration": raw.get("duration", ""),
            "components": sorted(raw.get("components", [])),
            "description": raw.get("description", ""),
        })
    return {"spells": out, "count": len(out)}


@router.post("/join")
def join_campaign(req: JoinIn):
    """加入已有战役：创建角色卡，返回 character_id。

    与 /character 同口径：校验战役存在性（避免输错房间号静默创建孤儿角色）、
    校验属性生成方式、完整写入子职/背景/阵营/速度。
    ★ P3: 通过 CharacterBuilder 校验（方案 §6.1 唯一构建服务）。
    """
    if store.get_campaign(req.campaign_id) is None:
        raise HTTPException(status_code=404, detail={
            "error": "campaign_not_found",
            "message": f"战役 {req.campaign_id} 不存在，请确认房间号"})
    validate_abilities(req.abilities, req.ability_method)
    validate_build_plan(req.race, req.char_class, req.subclass,
                        req.background, req.abilities, req.skills)
    ch = models.Character(name=req.name, race=req.race, char_class=req.char_class,
                          subclass=req.subclass, background=req.background,
                          alignment=req.alignment, level=req.level,
                          campaign_id=req.campaign_id)
    ch.set_abilities(req.abilities)
    # ★ P1-01: 机械属性由服务器权威计算，客户端提交值被忽略
    from ...build.derive_stats import apply_server_stats
    apply_server_stats(ch, req.char_class, req.race, req.level, req.abilities)
    # 统一初始化拥有物（与 /character 一致）：法术位 + 已学法术 + 起始武器入包
    init_loadout(ch, req.equipped_weapon)
    # P6: 持久化资源池初始化
    init_resource_pools(ch)
    ch = store.save_character(ch)
    persist_build_provenance(ch, req.race, req.char_class, req.subclass,
                             req.background, req.abilities, req.skills)
    return {"character_id": ch.id, "campaign_id": req.campaign_id,
            "name": ch.name}
