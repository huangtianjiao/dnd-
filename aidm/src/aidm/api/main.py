"""P4 API 层 — FastAPI 端点，包裹 P3 编排与 P1 状态层。

端点:
  POST /campaign          建战役
  POST /character         建角色卡
  GET  /character/{id}    取角色卡
  POST /chat              跑一轮硬性判定链（玩家输入→AI DM 叙事+骰子+状态）
  GET  /summary/{camp}    取 rolling summary
"""

from __future__ import annotations

import asyncio
import os
import socketio
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from ..stats import store, models
from ..brain import graph
from ..data import magic_items as mi_db
from .memory_bg import _async_memory_process

app = FastAPI(title="AI DM", version="0.3.0")

# CORS — 允许的源从环境变量 ALLOWED_ORIGINS 读取（逗号分隔），默认 Next.js dev server (:3000)
# 生产模式同源不需要 CORS，但保留以防反向代理场景
_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO 实时同桌（升级版，基于 python-socketio）
from .ws import sio, manager, CampaignRoom, _graph_lock

# 静态前端（P5 交互层：Web 聊天界面）
_UI_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "ui", "static")
)

# 挂载静态文件目录（CSS/JS）
app.mount("/static", StaticFiles(directory=_UI_DIR), name="static")


@app.get("/")
def index():
    """Web 跑团前端（HTML 聊天页，调 /chat）。"""
    p = os.path.join(_UI_DIR, "index.html")
    if os.path.exists(p):
        return FileResponse(p)
    return {"status": "frontend not found", "path": p}


class CampaignIn(BaseModel):
    name: str


class CharIn(BaseModel):
    name: str
    race: str = "人类"
    char_class: str = "战士"
    subclass: str = ""            # 子职（PHB 第一章），subclass_level <= level 时可选
    background: str = ""          # 背景（PHB 第一章），影响属性加成/起源专长/技能熟练
    alignment: str = "绝对中立"   # 阵营九宫格（PHB 第一章）
    level: int = 1
    abilities: dict = {"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10}
    hp_max: int = 10
    ac: int = 10
    speed: int = 30
    equipped_weapon: str = ""   # 可选：指定起始武器，留空则按职业默认
    campaign_id: int | None = None
    # 属性生成方式：standard_array(标准阵列)/point_buy(购点法)/roll(掷骰)/free(不校验)
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


class OpenIn(BaseModel):
    setting: str
    tone: str = ""
    campaign_id: int
    character_id: int


def _validate_abilities(abilities: dict, method: str) -> None:
    """按 D&D 5e 属性生成方式校验，非法抛 422。

    复用 brain/char_create 的规则（标准阵列/购点法/掷骰），
    这些原本未接入 HTTP，POST /character 之前对属性完全不校验。
    """
    if not method or method == "free":
        return
    from ..brain.char_create import validate_point_buy, STANDARD_ARRAY
    vals = list(abilities.values())
    if method == "standard_array":
        if sorted(vals) != sorted(STANDARD_ARRAY):
            raise HTTPException(422, detail={"error": "invalid_abilities",
                "message": "标准阵列须为 [15,14,13,12,10,8] 的排列"})
    elif method == "point_buy":
        if not validate_point_buy(vals):
            raise HTTPException(422, detail={"error": "invalid_abilities",
                "message": "购点法：6项各8-15，总花费≤27"})
    elif method == "roll":
        if len(vals) != 6 or any(not (3 <= int(v) <= 18) for v in vals):
            raise HTTPException(422, detail={"error": "invalid_abilities",
                "message": "掷骰属性：6项各3-18"})


@app.get("/health")
def health():
    return {"status": "ok"}


def _init_loadout(ch, equipped_weapon: str = "") -> None:
    """角色创建时统一初始化拥有物：法术位/已学法术/起始武器入包。

    拥有性门控（R-SPL-036 职业法术列表 / R-ITM-012 武器表）：
      - 施法职业按等级初始化法术位（R-SPL-002）与 known_spells；
      - 起始武器写入 equipped_weapon 并加入 inventory（后续
        /equip-weapon 与攻击结算只认 inventory 内的武器）。
    三处创建入口（/character、/join、/room/join）共用，避免漏初始化。
    """
    from ..data import classes as _cls, spells as _sp
    from ..data.equipment import default_weapon_for_class
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


@app.post("/campaign")
def create_campaign(c: CampaignIn):
    camp = store.create_campaign(c.name)
    return {"id": camp.id, "name": camp.name}


@app.post("/character")
def create_character(c: CharIn):
    ch = models.Character(name=c.name, race=c.race, char_class=c.char_class,
                          subclass=c.subclass, background=c.background,
                          alignment=c.alignment, level=c.level,
                          campaign_id=c.campaign_id)
    _validate_abilities(c.abilities, c.ability_method)
    ch.set_abilities(c.abilities)
    ch.hp_max = c.hp_max; ch.hp_current = c.hp_max; ch.ac = c.ac; ch.speed = c.speed
    # 统一初始化拥有物：法术位 + 已学法术 + 起始武器入包（拥有性门控）
    _init_loadout(ch, c.equipped_weapon)
    ch = store.save_character(ch)
    return {"id": ch.id, "name": ch.name, "hp": ch.hp_current, "ac": ch.ac}


@app.get("/character/{cid}")
def get_character(cid: int):
    """角色卡全数据（前端角色面板用）。"""
    from ..engine import dice
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    ab = ch.abilities
    # 历史施法角色 known_spells 为空 → 动态回退职业默认表（不落盘，
    # 与 graph._resolve_cast 校验口径一致，否则前端法术书空显）
    _known = ch.known_spells
    if not _known:
        from ..data import spells as _sp
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


@app.get("/character/{cid}/inventory")
def get_inventory(cid: int):
    """获取角色完整物品栏。

    返回:
      - inventory: 物品栏中的魔法物品名称列表
      - attuned_items: 已同调的魔法物品名称列表（最多3个）
      - magic_items: 物品栏中每件魔法物品的详细数据
      - gold: 角色持有金币（暂未持久化，返回0）

    规则依据: 城主指南2024/7.宝藏/ — 战利品分配后写入角色物品栏
    """
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})

    inv_names = ch.inventory
    attuned = ch.attuned_items

    # 拆分物品栏：魔法物品附详情；武器附伤害/属性（拥有性门控后前端只列拥有武器）
    from ..data import equipment as equip_db
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
        "gold": 0,
    }


# ── 魔法物品 API ────────────────────────────────────────────────────────────
# 规则依据: 城主指南2024/7.宝藏/
# magic_items 已在文件顶部 import 为 mi_db。

@app.get("/magic-items")
def list_magic_items(rarity: str | None = None,
                     item_type: str | None = None,
                     cursed_only: bool = False):
    """返回魔法物品数据库。

    Query params:
        rarity:     稀有度筛选 (COMMON/UNCOMMON/RARE/VERY_RARE/LEGENDARY/ARTIFACT)
        item_type:  类别筛选 (WEAPON/ARMOR/WONDROUS_ITEM/RING/SCROLL/POTION/STAFF/ROD/WAND)
        cursed_only: 仅返回诅咒物品

    Returns:
        {"items": [...], "count": N}
    """
    rar = None
    if rarity is not None:
        try:
            rar = mi_db.Rarity[rarity.upper()]
        except KeyError:
            return {"error": f"未知稀有度: {rarity}"}

    itype = None
    if item_type is not None:
        try:
            itype = mi_db.ItemType[item_type.upper().replace("-", "_")]
        except KeyError:
            return {"error": f"未知类别: {item_type}"}

    items = mi_db.list_magic_items(rarity=rar, item_type=itype, cursed_only=cursed_only)
    return {"items": [item.to_dict() for item in items], "count": len(items)}


@app.get("/magic-items/{name}")
def get_magic_item(name: str):
    """查询特定魔法物品。"""
    item = mi_db.get_magic_item(name)
    if item is None:
        return {"error": f"未找到魔法物品: {name}"}
    return item.to_dict()


class AttuneIn(BaseModel):
    item_name: str


@app.post("/character/{cid}/attune")
def attune_item(cid: int, req: AttuneIn):
    """同调魔法物品。

    规则: 玩家手册 同调Attunement
      - 物品必须需要同调
      - 一个生物最多同时与3件魔法物品同调
      - 同调需要一个短休
    """
    from ..brain import loot
    result = loot.attune_magic_item(cid, req.item_name)
    return result


class BreakAttuneIn(BaseModel):
    item_name: str


@app.post("/character/{cid}/break-attunement")
def break_attunement(cid: int, req: BreakAttuneIn):
    """解除魔法物品同调。"""
    from ..brain import loot
    result = loot.break_attunement(cid, req.item_name)
    return result


class EquipWeaponIn(BaseModel):
    weapon_name: str


@app.post("/character/{cid}/equip-weapon")
def equip_weapon(cid: int, req: EquipWeaponIn):
    """装备/更换当前手持武器（攻击结算优先读 equipped_weapon）。

    拥有性门控：只能装备 inventory 内（或当前已装备）的武器；
    旧角色 inventory 可能未含起始武器 → 懒回填 equipped_weapon 入包。
    详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段A2。weapon_name 应为 equipment.WEAPONS 中的武器名。
    """
    from ..data import equipment as equip_db
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


@app.get("/weapons")
def list_weapons():
    """返回所有可用武器列表。

    规则依据: R-ITM-012 武器表  出处: topics/玩家手册2024/装备/武器.htm
    """
    from ..data import equipment as equip_db
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


class LootGenerateIn(BaseModel):
    cr: float
    count_enemies: int = 1
    include_magic_items: bool = True
    seed: int | None = None


@app.post("/loot/generate")
def generate_loot(req: LootGenerateIn):
    """生成随机战利品池。

    规则: 城主指南2024/7.宝藏/宝藏.htm
      - CR越高，金币越多、魔法物品越多越珍稀
    """
    from ..brain import loot
    pool = loot.generate_loot(
        cr=req.cr,
        count_enemies=req.count_enemies,
        include_magic_items=req.include_magic_items,
        seed=req.seed,
    )
    return pool.to_dict()


class LootDistributeInV1(BaseModel):
    """loot.py 体系（method=need_priority/...）的战利品分配请求。

    与下方 loot_distribution.py 体系的 LootDistributeIn（mode=NEED_FIRST/...）同名遮蔽，
    故本类重命名为 V1 以消除歧义；/loot/distribute 使用本类。
    """
    gold: int = 0
    magic_item_names: list[str] = []
    players: list[str]
    method: str = "need_priority"   # need_priority/round_robin/point_bid/dm_assign
    needs: dict[str, list[str]] | None = None
    dm_assignments: dict[str, list[str]] | None = None
    gold_method: str = "equal"       # equal/contribution
    contributions: dict[str, float] | None = None
    seed: int | None = None


@app.post("/loot/distribute")
def distribute_loot_v1(req: LootDistributeInV1):
    """分配战利品（魔法物品 + 金币）。

    规则: 城主指南2024/7.宝藏/宝藏主题.htm
    """
    from ..brain import loot
    from ..data.magic_items import get_magic_item

    # 构建LootPool
    magic_items = []
    unassigned_names = []
    for name in req.magic_item_names:
        item = get_magic_item(name)
        if item is not None:
            magic_items.append(item)
        else:
            unassigned_names.append(name)

    pool = loot.LootPool(gold=req.gold, magic_items=magic_items)

    # 分配魔法物品
    dist = loot.distribute_loot(
        pool=pool,
        players=req.players,
        method=req.method,
        needs=req.needs,
        dm_assignments=req.dm_assignments,
        seed=req.seed,
    )

    # 分配金币
    gold_dist = loot.distribute_gold(
        total_gold=req.gold,
        players=req.players,
        method=req.gold_method,
        contributions=req.contributions,
    )

    return {
        "item_distribution": dist.to_dict(),
        "gold_distribution": gold_dist,
        "unrecognized_items": unassigned_names,
        "total_gold": req.gold,
        "total_items": len(magic_items),
    }


@app.get("/combat/{campaign_id}")
def get_combat(campaign_id: int):
    """战斗状态（前端战斗追踪器用）。

    current_turn 与 socket combat_update（ws._broadcast_state）口径一致，
    前端 CombatData 统一读 current_turn；current_index 保留供调试。
    """
    from ..engine import combat as cmb
    try:
        c = store.load_combat(campaign_id)
    except Exception:
        return {"active": False}
    cur = cmb.current_combatant(c)
    # D4 实测修复：initiative_order 必须带 hp/hp_max/dead，否则刷新/重进后
    # 前端参战者 HP 卡全部显示 0/? 并误判死亡（此前仅 name/initiative/side）。
    return {"active": c.active, "round": c.round,
            "current_index": c.current_index,
            "current_turn": cur.name if cur else None,  # D4 fix below
            "initiative_order": [{"name": x.name, "initiative": x.initiative,
                                  "side": x.side, "hp": x.hp, "hp_max": x.hp_max,
                                  "dead": x.dead, "surprised": getattr(x, "surprised", False)}
                                 for x in c.initiative_order]}


@app.get("/races")
def list_races():
    """可扮演种族列表（前端角色创建下拉用，避免前端硬编码漂移）。"""
    from ..data.races import RACES
    return {"races": [
        {"name": n, "speed": r["speed"], "darkvision": r["darkvision"],
         "subraces": r["subraces"], "size": r["size"]}
        for n, r in RACES.items()
    ]}


@app.get("/classes")
def list_classes():
    """可选职业列表（前端角色创建下拉用）。

    返回生命骰/护甲受训/施法属性/子职业，供前端 suggestHP/suggestAC 与
    施法标记派生；字段名与 data/classes.py 对齐。
    """
    from ..data.classes import CLASSES
    return {"classes": [
        {"name": n, "hit_die": c["hit_die"],
         "armor_training": c["armor_training"],
         "spellcasting": c["spellcasting"],
         "subclasses": c["subclasses"],
         "subclass_level": c["subclass_level"]}
        for n, c in CLASSES.items()
    ]}


@app.get("/roll-abilities")
def roll_abilities():
    """掷骰生成六项属性（4d6弃最低×6），供前端掷骰模式。

    规则: 第三步：确定属性值.htm 随机生成
    """
    from ..brain.char_create import roll_ability_scores
    return {"values": roll_ability_scores()}


@app.get("/backgrounds")
def list_backgrounds():
    """可选背景列表（前端角色创建下拉用）。

    返回属性加成/起源专长/技能熟练/工具熟练/起始装备，
    字段名与 data/backgrounds.py 对齐。
    """
    from ..data.backgrounds import BACKGROUNDS
    return {"backgrounds": [
        {"name": n, "ability_scores": b["ability_scores"],
         "feat": b["feat"], "skill_prof": b["skill_prof"],
         "tool_prof": b["tool_prof"], "equipment": b["equipment"]}
        for n, b in BACKGROUNDS.items()
    ]}


@app.get("/spells")
def list_spells(level: int | None = None):
    """法术列表（前端法术书用）。

    精校表 SPELLS 优先，其余用全量表 SPELLS_FULL 补齐（与 get_spell/
    default_known_spells 口径一致，否则已学法术在法术书中漏显）。

    Query params:
        level: 按环阶过滤

    Returns:
        {"spells": [{name, level, school, casting_time, range,
                     duration, components, description}], "count": N}
    """
    from ..data.spells import SPELLS
    from ..data.spells_full import SPELLS_FULL
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


class RestIn(BaseModel):
    type: str = "short"   # short | long


@app.post("/character/{cid}/rest")
def rest_character(cid: int, req: RestIn):
    """执行短休/长休，应用结果到角色卡。

    规则: R-GLS-014 短休 / R-GLS-015 长休
    说明:
      - 短休：消耗生命骰恢复HP，恢复职业特性使用次数
      - 长休：恢复全部HP、生命骰、法术位，力竭-1，清空临时HP
    """
    from ..brain import rest as rest_mod
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
        from ..data import spells as _sp
        ch.set_spell_slots(_sp.max_spell_slots(ch.level))
    ch = store.save_character(ch)
    return {"success": result.get("success", True), "type": req.type,
            "hp_restored": result.get("hp_restored", 0),
            "exhaustion_reduced": result.get("exhaustion_reduced", 0),
            "spell_slots_restored": result.get("spell_slots_restored", False)}


@app.get("/monster/{name}")
def get_monster(name: str):
    """怪物数值检索（从 data.js RAG 查怪物属性块）。"""
    from ..knowledge import indexer
    try:
        res = indexer.search(name, limit=1)
    except Exception:
        raise HTTPException(status_code=503, detail={"error": "collection not available", "message": "规则库索引不可用"})
    if res:
        return {"name": res[0].get("title", ""), "body": res[0].get("body", "")[:800],
                "tag": res[0].get("tag", ""), "path": res[0].get("path", "")}
    raise HTTPException(status_code=404, detail={"error": "not found", "message": f"未找到怪物: {name}"})


# ── WebSocket 实时同桌 ──────────────────────────────────────────────────────

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


@app.post("/join")
def join_campaign(req: JoinIn):
    """加入已有战役：创建角色卡，返回 character_id + WebSocket URL。"""
    ch = models.Character(name=req.name, race=req.race, char_class=req.char_class,
                          level=req.level, campaign_id=req.campaign_id)
    ch.set_abilities(req.abilities)
    ch.hp_max = req.hp_max; ch.hp_current = req.hp_max; ch.ac = req.ac
    # 统一初始化拥有物（与 /character 一致）：法术位 + 已学法术 + 起始武器入包
    _init_loadout(ch, req.equipped_weapon)
    ch = store.save_character(ch)
    return {"character_id": ch.id, "campaign_id": req.campaign_id,
            "name": ch.name,
            "ws_url": f"ws://{req.campaign_id}?character_id={ch.id}&name={req.name}"}


@app.get("/players/{campaign_id}")
def get_players(campaign_id: int):
    """列出在线玩家。"""
    return {"players": manager.get_players(campaign_id),
            "current_turn": manager.current_turn_name(campaign_id)}


@app.get("/campaigns")
def list_campaigns():
    """列出所有已保存战役（继续游戏用）。"""
    camps = store.list_campaigns()
    return {"campaigns": [
        {"id": c.id, "name": c.name,
         "setting": (c.setting or "")[:80],
         "summary": (c.rolling_summary or "")[:100]}
        for c in camps
    ]}


class GenSettingIn(BaseModel):
    theme: str = ""


@app.post("/generate_setting")
def generate_setting(req: GenSettingIn):
    """AI 生成世界设定（给玩家灵感，可编辑后提交）。"""
    from ..brain import llm
    prompt = (
        "你是D&D 5E的世界构建师。生成一个引人入胜的冒险世界设定(150-250字)。\n"
        "包含: 世界背景/基调、当前危机或委托、1-2个关键地点、1个NPC线索。\n"
        "风格: 黑暗奇幻、有悬念、给玩家行动空间。\n"
    )
    if req.theme:
        prompt += f"主题倾向: {req.theme}\n"
    raw = llm.chat("你是D&D世界构建师", prompt, temperature=0.8)
    # 清理可能的 markdown 包裹
    setting = raw.strip()
    if setting.startswith("```"):
        setting = setting.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return {"setting": setting}


@app.get("/campaign/{campaign_id}/state")
def get_campaign_state(campaign_id: int):
    """加载战役完整状态（继续游戏用）：战役信息+场景+角色列表+摘要+战斗。"""
    from ..brain import world
    camp = store.get_campaign(campaign_id)
    if not camp:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": f"战役 {campaign_id} 不存在"})
    chars = store.list_characters(campaign_id)
    scene = world.get_scene(campaign_id)
    try:
        c = store.load_combat(campaign_id)
        combat = {"active": c.active, "round": c.round,
                  "initiative_order": [{"name": x.name, "initiative": x.initiative,
                                        "side": x.side, "hp": x.hp, "hp_max": x.hp_max,
                                        "dead": x.dead, "surprised": getattr(x, "surprised", False)}
                                       for x in c.initiative_order]}
    except Exception:
        combat = None
    return {
        "campaign": {"id": camp.id, "name": camp.name, "setting": camp.setting, "tone": camp.tone},
        "scene": scene,
        "characters": [{"id": ch.id, "name": ch.name, "level": ch.level,
                        "hp": ch.hp_current, "hp_max": ch.hp_max, "ac": ch.ac,
                        "char_class": ch.char_class} for ch in chars],
        "summary": (camp.rolling_summary or "")[:300],
        "combat": combat,
    }


# Socket.IO 端点由 sio (AsyncServer) 处理，无需 FastAPI WebSocket 路由。
# ASGI 应用在模块末尾挂载：combined_app = socketio.ASGIApp(sio, app)


@app.post("/chat")
async def chat(req: ChatIn):
    """跑一轮硬性判定链。HITL 启用时若 interrupt，返回 interrupted=True 供 /chat/resume 恢复。

    graph.run 是同步阻塞，放线程池跑（run_in_executor）避免卡事件循环；
    复用 ws._graph_lock 串行化以避免 Qdrant 并发问题（与 ws.on_action 一致）。
    之前是同步 def + asyncio.ensure_future：同步 endpoint 在 AnyIO worker thread
    执行，该线程无事件循环 → ensure_future 抛 RuntimeError 500。改为 async def 后
    在主事件循环运行，ensure_future 有 loop 可用。
    """
    loop = asyncio.get_event_loop()
    async with _graph_lock:
        out = await loop.run_in_executor(
            None,
            lambda: graph.run(req.player_input, req.campaign_id, req.character_id,
                              req.thread_id, hitl=req.hitl))
    if out.get("__interrupt__"):
        v = out["__interrupt__"][0]
        q = v.value if hasattr(v, "value") else v
        return {"interrupted": True, "thread_id": req.thread_id, "question": q}

    # 异步后台执行记忆处理，不阻塞响应（async endpoint 在主事件循环，ensure_future 有 loop）
    narration = out.get("narration", "")
    intent = out.get("intent", {})
    if req.campaign_id and narration:
        asyncio.ensure_future(_async_memory_process(
            campaign_id=req.campaign_id,
            player_input=req.player_input,
            narration=narration,
            intent=intent,
        ))

    return {
        "narration": narration,
        "intent": intent,
        "dice": out.get("dice", {}),
        "state_changes": out.get("state_changes", []),
        "action_options": out.get("action_options", []),
        "combat": out.get("combat", {}),
        "error": out.get("error", ""),
    }


@app.post("/chat/resume")
def chat_resume(req: ResumeIn):
    """HITL 恢复：DM 给出 y/n 后继续判定链。"""
    from langgraph.types import Command
    cfg = {"configurable": {"thread_id": req.thread_id}}
    out = graph.get_graph().invoke(Command(resume=req.answer), config=cfg)
    if out.get("__interrupt__"):
        return {"interrupted": True, "thread_id": req.thread_id}
    return {
        "narration": out.get("narration", ""),
        "dice": out.get("dice", {}),
        "state_changes": out.get("state_changes", []),
    }


@app.get("/summary/{campaign_id}")
def summary(campaign_id: int):
    return {"summary": store.get_summary(campaign_id)}


class SessionEndIn(BaseModel):
    campaign_id: int


@app.post("/session/end")
def session_end(req: SessionEndIn):
    """Session 结束时生成前情提要（浓缩摘要）。

    流程:
      1. generate_recap — 汇总 rolling_summary + 高重要性记忆 → LLM 生成前情提要
      2. 前情提存储到 Campaign.rolling_summary 的 [前情提要]...[/前情提要] 块
      3. 下次 narrate() 时自动注入

    返回:
      {"recap": "前情提文本本"}
    """
    from ..brain.memory import generate_recap
    recap = generate_recap(req.campaign_id)
    return {"recap": recap}


# ── 专长系统（PHB 第五章）──────────────────────────────────────────────────

class FeatIn(BaseModel):
    feat_name: str


@app.get("/feats")
def list_feats_api(category: Optional[str] = None):
    """返回可选专长列表。

    Args:
        category: 可选分类过滤。
                  起源 / 通用 / 战斗风格 / 传奇恩惠。
                  不传则返回全部。

    出处: PHB 2024 第五章「专长」
    """
    from ..data import feats as F
    valid_cats = set(F.feat_categories())
    if category is not None and category not in valid_cats:
        raise HTTPException(status_code=400, detail={"error": "invalid_request", "message": f"未知分类 {category!r}，可选: {sorted(valid_cats)}"})
    return {"feats": F.list_feats(category), "count": len(F.list_feats(category))}


@app.post("/character/{cid}/feat")
def add_feat(cid: int, req: FeatIn):
    """为角色选择一个专长。

    规则校验:
      - 专长必须存在于数据表
      - 非复选专长不可重复选择（PHB「复选Repeatable」）

    出处: PHB 2024 第五章「专长」
    """
    from ..data import feats as F
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    feat = F.get_feat(req.feat_name)
    if feat is None:
        raise HTTPException(status_code=400, detail={"error": "invalid_request", "message": f"未知专长 {req.feat_name!r}"})
    current = ch.feats
    if req.feat_name in current and not feat["repeatable"]:
        raise HTTPException(status_code=400, detail={"error": "invalid_request", "message": f"专长 {req.feat_name!r} 不可重复选择"})
    if req.feat_name not in current:
        current.append(req.feat_name)
    ch.set_feats(current)
    ch = store.save_character(ch)
    return {"id": ch.id, "name": ch.name, "feats": ch.feats}


@app.get("/character/{cid}/available-feats")
def available_feats_api(cid: int):
    """返回角色当前等级可选的专长列表。

    规则出处: PHB 2024 第五章「专长」
      - 通用/战斗风格专长在等级 4/8/12/16 开放。
      - 传奇恩惠专长在等级 19 开放（先决「等级19+」）。
      - 非复选专长若已被选取则不再列出。
      - 复选专长可多次选取，仍列于结果中。

    Returns:
        {
          "level": int,
          "feat_available": bool,   # 当前等级是否为专长选择等级
          "available_feats": [...], # 可选专长列表
          "count": int,
        }
    """
    from ..brain import levelup as lu
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    char_dict = {
        "level": ch.level,
        "feats": ch.feats,
    }
    avail = lu.available_feats(char_dict)
    feat_available = ch.level in lu.FEAT_LEVELS
    return {
        "level": ch.level,
        "feat_available": feat_available,
        "available_feats": avail,
        "count": len(avail),
    }


class SelectFeatIn(BaseModel):
    feat_name: str


@app.post("/character/{cid}/select-feat")
def select_feat_api(cid: int, req: SelectFeatIn):
    """为角色选择一个专长并持久化。

    规则校验（出处: PHB 2024 第五章「专长」）:
      - 专长必须存在于数据表。
      - 非复选专长（repeatable=False）不可重复选择。
      - 起源专长仅在角色创建时由背景给予，升级流程拒绝。
      - 传奇恩惠专长需等级 19+。

    Returns:
        {"id": int, "name": str, "feat": str, "feats": [...]}
        或 {"error": "..."}
    """
    from ..brain import levelup as lu
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})

    char_dict = {
        "level": ch.level,
        "feats": list(ch.feats),
        "asi_taken": getattr(ch, "asi_taken", False),
    }
    try:
        result = lu.select_feat(char_dict, req.feat_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": "invalid_request", "message": str(e)})

    # 同步回 Character 并持久化
    ch.set_feats(result["feats"])
    ch = store.save_character(ch)
    return {
        "id": ch.id,
        "name": ch.name,
        "feat": result["feat"],
        "feats": ch.feats,
    }


@app.post("/open")
def open_campaign(req: OpenIn):
    """DM 开场：依据世界设定生成完整背景+当前场景+3个行动选项。"""
    from ..brain import world
    r = world.open_campaign(req.setting, req.tone, req.campaign_id, req.character_id)
    return {"narration": r["narration"], "action_options": r.get("action_options", []),
            "scene": r["scene"]}


@app.get("/scene/{campaign_id}")
def get_scene(campaign_id: int):
    """取当前场景（前端场景面板用）。"""
    from ..brain import world
    return world.get_scene(campaign_id)


# ── 多人房间管理 ───────────────────────────────────────────────────────

from ..brain import room as room_mod

room_manager = room_mod.RoomManager()


class RoomCreateIn(BaseModel):
    """房主创建房间：先建战役，再设密码/人数上限。"""
    campaign_name: str = "新战役"
    password: str = ""
    max_players: int = 6


@app.post("/room/create")
def create_room(req: RoomCreateIn):
    """房主创建房间。

    流程:
      1. 创建战役 (store.create_campaign)
      2. 创建房间 (RoomManager.create_room)
      3. 返回 room_id + campaign_id

    说明: 房主随后通过 /room/join 以房主身份加入。
    """
    camp = store.create_campaign(req.campaign_name)
    room = room_manager.create_room(
        campaign_id=camp.id,
        password=req.password,
        max_players=req.max_players,
    )
    return {
        "room_id": room.room_id,
        "campaign_id": camp.id,
        "campaign_name": camp.name,
        "has_password": bool(room.password),
        "max_players": room.max_players,
    }


class RoomJoinIn(BaseModel):
    """玩家加入房间：输入房间号+密码+角色信息。"""
    room_id: str
    password: str = ""
    name: str
    race: str = "人类"
    char_class: str = "战士"
    level: int = 1
    abilities: dict = {"str": 10, "dex": 10, "con": 10,
                       "int": 10, "wis": 10, "cha": 10}
    hp_max: int = 10
    ac: int = 10
    speed: int = 30
    equipped_weapon: str = ""
    is_host: bool = False       # 房主首次加入时为 True


# 房间错误码 → HTTP 状态码/中文描述（前端按 detail={"error", "message"} 契约对接）
_ROOM_ERR_STATUS = {
    "room_not_found": 404,
    "player_not_found": 404,
    "wrong_password": 400,
    "name_taken": 400,
    "room_full": 409,
    "cannot_kick_host": 400,
    "not_host": 403,
}
_ROOM_ERR_MSG = {
    "room_not_found": "房间号不存在",
    "player_not_found": "玩家不存在",
    "wrong_password": "密码错误",
    "name_taken": "名字已被占用",
    "room_full": "房间已满",
    "cannot_kick_host": "不能踢出房主",
    "not_host": "只有房主可以执行此操作",
}


def _room_http_error(code: str) -> HTTPException:
    """将房间错误码转为统一形态的 HTTPException。"""
    return HTTPException(
        status_code=_ROOM_ERR_STATUS.get(code, 400),
        detail={"error": code, "message": _ROOM_ERR_MSG.get(code, code)},
    )


@app.post("/room/join")
def join_room(req: RoomJoinIn):
    """玩家加入房间：创建角色卡并加入房间。

    错误码:
      - room_not_found: 房间号不存在
      - wrong_password: 密码错误
      - room_full: 房间已满
      - name_taken: 名字已被占用
    """
    room = room_manager.get_room(req.room_id)
    if room is None:
        raise _room_http_error("room_not_found")

    # 先创建角色卡（关联到房间对应的战役）
    ch = models.Character(name=req.name, race=req.race,
                          char_class=req.char_class, level=req.level,
                          campaign_id=room.campaign_id)
    ch.set_abilities(req.abilities)
    ch.hp_max = req.hp_max; ch.hp_current = req.hp_max
    ch.ac = req.ac; ch.speed = req.speed
    # 统一初始化拥有物（与 /character 一致）：法术位 + 已学法术 + 起始武器入包
    _init_loadout(ch, req.equipped_weapon)
    ch = store.save_character(ch)

    # 加入房间（用假 ws 占位；真实连接由 WebSocket 端点建立）
    from fastapi import WebSocket
    fake_ws = type("FakeWS", (), {})()   # 仅作字典键占位

    if req.is_host:
        room_manager.add_host(req.room_id, req.name, ch.id, fake_ws)
    else:
        result = room_manager.join_room(
            req.room_id, req.password, req.name, ch.id, fake_ws)
        if not result["ok"]:
            # 加入失败，删除刚创建的角色卡
            store.delete_character(ch.id)
            raise _room_http_error(result["error"])

    return {
        "room_id": req.room_id,
        "campaign_id": room.campaign_id,
        "character_id": ch.id,
        "name": ch.name,
        "ws_url": f"ws://<host>/ws/{room.campaign_id}"
                  f"?character_id={ch.id}&name={req.name}",
    }


@app.get("/room/{room_id}")
def get_room_status(room_id: str):
    """获取房间状态（不含密码）。"""
    room = room_manager.get_room(room_id)
    if room is None:
        raise _room_http_error("room_not_found")
    return room.to_dict()


@app.get("/rooms")
def list_rooms():
    """列出所有活跃房间。"""
    return {"rooms": room_manager.list_rooms()}


class KickIn(BaseModel):
    """房主踢出玩家。"""
    target_name: str
    requester_name: str


@app.post("/room/{room_id}/kick")
def kick_player(room_id: str, req: KickIn):
    """房主踢出指定玩家。

    服务端校验: requester_name 必须是当前房主（前端 UI 隐藏可被绕过，见评审 A1）。
    """
    room = room_manager.get_room(room_id)
    if room is None:
        raise _room_http_error("room_not_found")
    # 房主校验
    host = room.get_host()
    if host is None or host["name"] != req.requester_name:
        raise _room_http_error("not_host")
    # 找到目标玩家
    target = room.find_player_by_name(req.target_name)
    if target is None:
        raise _room_http_error("player_not_found")
    if target["is_host"]:
        raise _room_http_error("cannot_kick_host")
    # 从房间移除
    room.players = [p for p in room.players
                    if p["name"] != req.target_name]
    return {"kicked": req.target_name, "room": room.to_dict()}


class TransferIn(BaseModel):
    """房主转让权限。"""
    target_name: str
    requester_name: str


@app.post("/room/{room_id}/transfer")
def transfer_host(room_id: str, req: TransferIn):
    """房主将房主权限转让给另一玩家。

    服务端校验: requester_name 必须是当前房主（前端 UI 隐藏可被绕过，见评审 A1）。
    """
    room = room_manager.get_room(room_id)
    if room is None:
        raise _room_http_error("room_not_found")
    # 房主校验
    host = room.get_host()
    if host is None or host["name"] != req.requester_name:
        raise _room_http_error("not_host")
    target = room.find_player_by_name(req.target_name)
    if target is None:
        raise _room_http_error("player_not_found")
    # 转让
    for p in room.players:
        p["is_host"] = (p["name"] == req.target_name)
    return {"new_host": req.target_name, "room": room.to_dict()}


# ── 战利品分配 ─────────────────────────────────────────────────────────

from ..brain import loot_distribution as loot


class LootPoolIn(BaseModel):
    """生成战利品池。"""
    campaign_id: int
    monster_crs: list[float]         # 击败怪物的CR列表（支持 0.5 等小数 CR）
    combat_round: int = 0


@app.post("/loot/pool")
def generate_loot(req: LootPoolIn):
    """根据击败怪物的CR列表生成战利品池。

    规则: 城主指南 §7 宝藏阈值（简化版）
    说明:
      - 金币按CR查表掷区间随机值
      - 物品按概率表掷是否掉落及掉什么
      - 高CR(>10)按CR 10处理
    """
    pool = loot.generate_loot_pool(
        campaign_id=req.campaign_id,
        monster_crs=req.monster_crs,
        combat_round=req.combat_round,
    )
    return {
        "pool_id": pool.pool_id,
        "gold": pool.gold,
        "items": [
            {"item_id": it.item_id, "name": it.name,
             "type": it.item_type, "rarity": it.rarity,
             "value_gp": it.value_gp, "quantity": it.quantity,
             "description": it.description}
            for it in pool.items
        ],
    }


class LootDistributeIn(BaseModel):
    """分配战利品。"""
    campaign_id: int
    gold: int = 0
    items: list[dict] = []            # [{item_id, name, ...}]
    player_names: list[str]
    mode: str = "ROUND_ROBIN"         # NEED_FIRST/ROUND_ROBIN/ROLL_OFF/DM_ASSIGN
    initiative_order: Optional[list[str]] = None
    needs: Optional[dict[str, list[str]]] = None    # {player: [item_id]}
    dm_assignments: Optional[dict[str, str]] = None # {item_id: player}


# 注: 此为 loot_distribution.py 体系(mode=NEED_FIRST/...)，与上方 L285 的 loot.py 体系(method=need_priority/...)不同。
# 原路径 /loot/distribute 与 L285 重复导致被遮蔽，改为 /v2 避免冲突(见 docs/ISSUES.md)。
@app.post("/loot/distribute/v2")
def distribute_loot(req: LootDistributeIn):
    """执行完整的战利品分配流程。

    分配策略:
      - NEED_FIRST: 需求优先——声明需要的玩家优先获得
      - ROUND_ROBIN: 轮流拾取——按先政顺序轮流选择物品
      - ROLL_OFF: 点数分配——掷骰决定优先权
      - DM_ASSIGN: DM指定——DM直接指定归属

    金币分配: 平均分配（向下取整，余数给第一人）
    """
    # 重建 LootPool
    pool = loot.LootPool(
        pool_id=f"distribute_{req.campaign_id}",
        campaign_id=req.campaign_id,
        gold=req.gold,
    )
    for item_data in req.items:
        pool.items.append(loot.LootItem(
            item_id=item_data.get("item_id", ""),
            name=item_data.get("name", ""),
            item_type=item_data.get("type", "misc"),
            rarity=item_data.get("rarity", "普通"),
            value_gp=item_data.get("value_gp", 0),
            quantity=item_data.get("quantity", 1),
            description=item_data.get("description", ""),
        ))

    # 解析分配模式
    try:
        mode = loot.DistributionMode(req.mode)
    except ValueError:
        raise HTTPException(status_code=400, detail={"error": "invalid_request", "message": f"未知分配模式 {req.mode!r}"})

    # 执行分配
    record = loot.distribute_loot(
        pool=pool,
        player_names=req.player_names,
        mode=mode,
        initiative_order=req.initiative_order,
        needs=req.needs,
        dm_assignments=req.dm_assignments,
    )

    return {
        "record_id": record.record_id,
        "mode": record.mode,
        "gold_distribution": record.gold_distribution,
        "item_distribution": record.item_distribution,
        "timestamp": record.timestamp,
    }


@app.get("/loot/history/{campaign_id}")
def get_loot_history(campaign_id: int):
    """获取指定战役的战利品分配历史。

    说明: 当前实现返回空列表（持久化层未存储分配记录）。
          完整实现需在 stats.store 中增加分配记录表。
    """
    return {"campaign_id": campaign_id, "history": []}


# ── 据点系统 (DMG 第八章) ───────────────────────────────────────────────
# 规则依据: 城主指南2024/8.据点/

from ..brain import stronghold as sh
from ..data.strongholds import StrongholdType, OrderType


class StrongholdCreateIn(BaseModel):
    """建立据点。"""
    campaign_id: int
    owner_character_id: int
    owner_name: str
    owner_level: int = 5            # DMG §1: 5级获得据点
    name: str
    stronghold_type: str = "塔楼"   # 塔楼/城堡/神殿/公会会所/要塞
    initial_gold: float = 0.0


@app.post("/stronghold/create")
def create_stronghold_api(req: StrongholdCreateIn):
    """建立据点 — DMG第八章 §1 建立一个据点。

    规则:
      - 角色达到5级时获得据点
      - 每个据点最初拥有两个基础(免费)设施：一个狭窄、一个宽敞
      - 角色的据点最初拥有两个特色设施，由角色选择

    Args:
        req: 包含战役ID、拥有者信息、据点名称和类型的请求体

    Returns:
        新建据点的状态信息
    """
    try:
        stype = StrongholdType(req.stronghold_type)
    except ValueError:
        return {
            "success": False,
            "error": (
                f"未知据点类型 {req.stronghold_type!r}，"
                f"可选: {[t.value for t in StrongholdType]}"
            ),
        }

    if req.owner_level < 5:
        return {
            "success": False,
            "error": (
                f"据点要求角色等级>=5 (DMG §1)，得到: {req.owner_level}"
            ),
        }

    stronghold = sh.create_stronghold(
        campaign_id=req.campaign_id,
        owner_character_id=req.owner_character_id,
        owner_name=req.owner_name,
        owner_level=req.owner_level,
        name=req.name,
        stronghold_type=stype,
        initial_gold=req.initial_gold,
    )

    return {
        "success": True,
        "stronghold_id": stronghold.stronghold_id,
        "status": sh.get_stronghold_status(stronghold),
    }


@app.get("/stronghold/{campaign_id}")
def get_stronghold_api(campaign_id: int, character_id: Optional[int] = None):
    """获取据点状态 — DMG第八章 据点系统。

    根据战役ID(和可选的角色ID)查找据点并返回其当前状态。

    Args:
        campaign_id: 战役ID
        character_id: 可选的角色ID，用于筛选特定角色的据点

    Returns:
        据点状态信息，如果找不到则返回404错误信息
    """
    # 在实际实现中，这里应从持久化层加载据点
    # 目前作为示例，返回提示信息
    return {
        "success": False,
        "error": "据点状态查询需要持久化层支持。请使用 /stronghold/create 创建据点后保存对象。",
        "campaign_id": campaign_id,
        "character_id": character_id,
    }


class StrongholdBuildIn(BaseModel):
    """建设设施。"""
    stronghold_id: str
    facility_name: str              # 设施名称
    is_basic: bool = False          # 是否为基础设施
    target_space: Optional[str] = None  # 目标空间大小(狭窄/宽敞/庞大)


@app.post("/stronghold/build")
def build_facility_api(req: StrongholdBuildIn):
    """建设设施 — DMG第八章 §3 增添基础设施 / 特色设施详述。

    规则:
      - 基础设施增添价格表:
        狭窄500GP/20天，宽敞1000GP/45天，庞大3000GP/125天
      - 特色设施无法被直接购买；角色通过升级来获取
      - 但特色设施可以被扩大(花费2000GP扩大为庞大设施)

    Args:
        req: 包含据点ID、设施名称和建设参数的请求体

    Returns:
        建设结果，包含花费和建造时间信息
    """
    # 在实际实现中，这里应从持久化层加载据点对象
    # 目前返回提示信息
    return {
        "success": False,
        "error": "建设设施需要据点对象的持久化层支持。",
        "request": req.dict(),
    }


class StrongholdTurnIn(BaseModel):
    """执行据点回合。"""
    stronghold_id: str
    order_type: str = "维护"        # 维护/制造/增强/收获/招募/调查/贸易
    facility_name: Optional[str] = None  # 目标特色设施名称(非维护指令时需要)


@app.post("/stronghold/turn")
def run_stronghold_turn_api(req: StrongholdTurnIn):
    """执行据点回合 — DMG第八章 §2 据点回合。

    规则:
      - 默认情况下，游戏内每经过7天时间，就会进行一次据点回合
      - 在据点回合中，位于自己的据点内的角色可以向一个或更多
        特色设施下达特殊的指令——这被称为据点指令
      - 维护指令是特殊的，该指令下达给整个据点而非特定设施
      - 每当维护指令被下达时，DM都将在据点事件表格上掷骰一次

    Args:
        req: 包含据点ID、指令类型和目标设施的请求体

    Returns:
        据点回合执行结果，包含收入/支出/事件触发等信息
    """
    try:
        otype = OrderType(req.order_type)
    except ValueError:
        return {
            "success": False,
            "error": (
                f"未知指令类型 {req.order_type!r}，"
                f"可选: {[o.value for o in OrderType]}"
            ),
        }

    # 在实际实现中，这里应从持久化层加载据点对象
    # 目前返回提示信息
    return {
        "success": False,
        "error": "据点回合执行需要据点对象的持久化层支持。",
        "request": req.dict(),
    }


@app.get("/strongholds/facilities")
def list_facilities_api(level: Optional[int] = None):
    """返回所有可用特色设施列表 — DMG第八章 §3 特色设施详述。

    规则:
      - 每个特色设施都标有一个等级
      - 角色必须达到该等级或更高才能获取该设施
      - 每个特色设施只能被选择一次，除非其描述中另有说明
      - 某些特色设施还会赋予额外的增益

    Args:
        level: 可选的角色等级，用于筛选可获取的设施

    Returns:
        特色设施列表，每个设施包含名称、等级、空间、雇员数、指令、先决条件、描述和效果
    """
    from ..data.strongholds import FACILITIES, FacilitySpace

    facilities = []
    for name, facility in FACILITIES.items():
        if level is not None and facility.level > level:
            continue
        facilities.append({
            "name": facility.name,
            "name_en": facility.name_en,
            "level": facility.level,
            "space": facility.space.value,
            "hirelings": facility.hirelings,
            "order": facility.order.value,
            "prerequisite": facility.prerequisite,
            "description": facility.description,
            "effects": facility.effects,
            "can_enlarge": facility.can_enlarge,
            "multiple_allowed": facility.multiple_allowed,
        })

    # 按等级排序，同等级按名称排序
    facilities.sort(key=lambda x: (x["level"], x["name"]))

    return {
        "success": True,
        "count": len(facilities),
        "facilities": facilities,
    }


# ── Socket.IO ASGI 挂载 ────────────────────────────────────────────────────
# 将 python-socketio 的 AsyncServer 包裹为 ASGI 应用，
# 与 FastAPI 应用组合，使 /ws/* 由 Socket.IO 处理，其余路由由 FastAPI 处理。
combined_app = socketio.ASGIApp(sio, app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(combined_app, host="0.0.0.0", port=8080)
