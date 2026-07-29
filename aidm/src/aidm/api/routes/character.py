"""角色管理路由。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...data import magic_items as mi_db
from ...stats import models, store
from .dependencies import CharIn, JoinIn, validate_abilities, init_loadout

router = APIRouter(tags=["character"])


class RestIn(BaseModel):
    type: str = "short"   # short | long


class AttuneIn(BaseModel):
    item_name: str


class BreakAttuneIn(BaseModel):
    item_name: str


class EquipWeaponIn(BaseModel):
    weapon_name: str


@router.post("/character")
def create_character(c: CharIn):
    ch = models.Character(name=c.name, race=c.race, char_class=c.char_class,
                          subclass=c.subclass, background=c.background,
                          alignment=c.alignment, level=c.level,
                          campaign_id=c.campaign_id)
    validate_abilities(c.abilities, c.ability_method)
    ch.set_abilities(c.abilities)
    ch.hp_max = c.hp_max; ch.hp_current = c.hp_max; ch.ac = c.ac; ch.speed = c.speed
    # 统一初始化拥有物：法术位 + 已学法术 + 起始武器入包（拥有性门控）
    init_loadout(ch, c.equipped_weapon)
    ch = store.save_character(ch)
    return {"id": ch.id, "name": ch.name, "hp": ch.hp_current, "ac": ch.ac}


@router.get("/character/{cid}")
def get_character(cid: int):
    """角色卡全数据（前端角色面板用）。"""
    from ...engine import dice
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    ab = ch.abilities
    # 历史施法角色 known_spells 为空 → 动态回退职业默认表
    _known = ch.known_spells
    if not _known:
        from ...data import spells as _sp
        _known = _sp.default_known_spells(ch.char_class, ch.level)
    return {"id": ch.id, "name": ch.name, "race": ch.race, "char_class": ch.char_class,
            "subclass": ch.subclass, "background": ch.background,
            "alignment": ch.alignment, "level": ch.level, "proficiency": ch.prof(),
            "abilities": {k: {"score": v, "mod": dice.ability_modifier(v)} for k, v in ab.items()},
            "hp": ch.hp_current, "hp_max": ch.hp_max, "temp_hp": ch.temp_hp, "ac": ch.ac,
            "speed": ch.speed, "conditions": ch.conditions_list, "exhaustion": ch.exhaustion,
            "spell_slots": ch.spell_slots, "known_spells": _known,
            "hit_dice_current": getattr(ch, "hit_dice_current", ch.level),
            "hit_dice_max": ch.level,
            "death_successes": ch.death_successes, "death_failures": ch.death_failures,
            "dead": ch.dead, "stable": ch.stable,
            "attuned_items": ch.attuned_items, "equipped_weapon": ch.equipped_weapon}


@router.get("/character/{cid}/inventory")
def get_inventory(cid: int):
    """获取角色完整物品栏。"""
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
def attune_item(cid: int, req: AttuneIn):
    """同调魔法物品。"""
    from ...brain import loot
    return loot.attune_magic_item(cid, req.item_name)


@router.post("/character/{cid}/break-attunement")
def break_attunement(cid: int, req: BreakAttuneIn):
    """解除魔法物品同调。"""
    from ...brain import loot
    return loot.break_attunement(cid, req.item_name)


@router.post("/character/{cid}/equip-weapon")
def equip_weapon(cid: int, req: EquipWeaponIn):
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
def rest_character(cid: int, req: RestIn):
    """执行短休/长休，应用结果到角色卡。"""
    from ...brain import rest as rest_mod
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    if req.type == "short":
        result = rest_mod.short_rest(ch)
    elif req.type == "long":
        result = rest_mod.long_rest(ch)
    else:
        raise HTTPException(status_code=422, detail={"error": "invalid_type", "message": f"未知休息类型: {req.type}"})
    # 应用结果到角色卡
    if result.get("hp_restored"):
        ch.hp_current = min(ch.hp_max, ch.hp_current + result["hp_restored"])
    if result.get("exhaustion_reduced") is not None:
        ch.exhaustion = max(0, ch.exhaustion - result["exhaustion_reduced"])
    if result.get("temp_hp_cleared"):
        ch.temp_hp = 0
    if result.get("spell_slots_restored"):
        from ...data import spells as _sp
        ch.set_spell_slots(_sp.max_spell_slots(ch.level))
    ch = store.save_character(ch)
    return {"success": result.get("success", True), "type": req.type,
            "hp_restored": result.get("hp_restored", 0),
            "exhaustion_reduced": result.get("exhaustion_reduced", 0),
            "spell_slots_restored": result.get("spell_slots_restored", False)}


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
    """加入已有战役：创建角色卡，返回 character_id + WebSocket URL。"""
    ch = models.Character(name=req.name, race=req.race, char_class=req.char_class,
                          level=req.level, campaign_id=req.campaign_id)
    ch.set_abilities(req.abilities)
    ch.hp_max = req.hp_max; ch.hp_current = req.hp_max; ch.ac = req.ac
    # 统一初始化拥有物（与 /character 一致）：法术位 + 已学法术 + 起始武器入包
    init_loadout(ch, req.equipped_weapon)
    ch = store.save_character(ch)
    return {"character_id": ch.id, "campaign_id": req.campaign_id,
            "name": ch.name,
            "ws_url": f"ws://{req.campaign_id}?character_id={ch.id}&name={req.name}"}
