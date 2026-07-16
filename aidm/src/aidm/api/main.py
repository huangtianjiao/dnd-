"""P4 API 层 — FastAPI 端点，包裹 P3 编排与 P1 状态层。

端点:
  POST /campaign          建战役
  POST /character         建角色卡
  GET  /character/{id}    取角色卡
  POST /chat              跑一轮硬性判定链（玩家输入→AI DM 叙事+骰子+状态）
  GET  /summary/{camp}    取 rolling summary
"""

from __future__ import annotations

import os
import socketio
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from ..stats import store, models
from ..brain import graph

app = FastAPI(title="AI DM", version="0.3.0")

# Socket.IO 实时同桌（升级版，基于 python-socketio）
from .ws import sio, manager, CampaignRoom

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
    level: int = 1
    abilities: dict = {"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10}
    hp_max: int = 10
    ac: int = 10
    speed: int = 30
    campaign_id: int | None = None


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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/campaign")
def create_campaign(c: CampaignIn):
    camp = store.create_campaign(c.name)
    return {"id": camp.id, "name": camp.name}


@app.post("/character")
def create_character(c: CharIn):
    ch = models.Character(name=c.name, race=c.race, char_class=c.char_class,
                          level=c.level, campaign_id=c.campaign_id)
    ch.set_abilities(c.abilities)
    ch.hp_max = c.hp_max; ch.hp_current = c.hp_max; ch.ac = c.ac; ch.speed = c.speed
    ch = store.save_character(ch)
    return {"id": ch.id, "name": ch.name, "hp": ch.hp_current, "ac": ch.ac}


@app.get("/character/{cid}")
def get_character(cid: int):
    """角色卡全数据（前端角色面板用）。"""
    from ..engine import dice
    ch = store.get_character(cid)
    if ch is None:
        return {"error": "not found"}
    ab = ch.abilities
    return {"id": ch.id, "name": ch.name, "race": ch.race, "char_class": ch.char_class,
            "subclass": ch.subclass, "level": ch.level, "proficiency": ch.prof(),
            "abilities": {k: {"score": v, "mod": dice.ability_modifier(v)} for k, v in ab.items()},
            "hp": ch.hp_current, "hp_max": ch.hp_max, "temp_hp": ch.temp_hp, "ac": ch.ac,
            "speed": ch.speed, "conditions": ch.conditions_list, "exhaustion": ch.exhaustion,
            "spell_slots": ch.spell_slots, "dead": ch.dead, "stable": ch.stable,
            "attuned_items": ch.attuned_items}


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
        return {"error": f"角色 {cid} 不存在"}

    inv_names = ch.inventory
    attuned = ch.attuned_items

    # 为物品栏中每件物品附加详细数据
    magic_items_detail = []
    for name in inv_names:
        item = mi_db.get_magic_item(name)
        if item is not None:
            d = item.to_dict()
            d["attuned"] = name in attuned
            magic_items_detail.append(d)

    return {
        "character_id": cid,
        "inventory": inv_names,
        "attuned_items": attuned,
        "magic_items": magic_items_detail,
        "gold": 0,
    }


# ── 魔法物品 API ────────────────────────────────────────────────────────────
# 规则依据: 城主指南2024/7.宝藏/

from ..data import magic_items as mi_db


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


class LootDistributeIn(BaseModel):
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
def distribute_loot(req: LootDistributeIn):
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
    """战斗状态（前端战斗追踪器用）。"""
    from ..engine import combat as cmb
    try:
        c = store.load_combat(campaign_id)
    except Exception:
        return {"active": False}
    return {"active": c.active, "round": c.round, "current_index": c.current_index,
            "initiative_order": [{"name": c.name, "initiative": c.initiative, "side": c.side}
                                 for c in c.initiative_order]}


@app.get("/monster/{name}")
def get_monster(name: str):
    """怪物数值检索（从 data.js RAG 查怪物属性块）。"""
    from ..knowledge import indexer
    try:
        res = indexer.search(name, limit=1)
    except Exception:
        return {"error": "collection not available"}
    if res:
        return {"name": res[0].get("title", ""), "body": res[0].get("body", "")[:800],
                "tag": res[0].get("tag", ""), "path": res[0].get("path", "")}
    return {"error": "not found"}


# ── WebSocket 实时同桌 ──────────────────────────────────────────────────────

class JoinIn(BaseModel):
    name: str
    race: str = "人类"
    char_class: str = "战士"
    level: int = 5
    abilities: dict = {"str": 16, "dex": 10, "con": 15, "int": 10, "wis": 12, "cha": 10}
    hp_max: int = 38
    ac: int = 18
    campaign_id: int


@app.post("/join")
def join_campaign(req: JoinIn):
    """加入已有战役：创建角色卡，返回 character_id + WebSocket URL。"""
    ch = models.Character(name=req.name, race=req.race, char_class=req.char_class,
                          level=req.level, campaign_id=req.campaign_id)
    ch.set_abilities(req.abilities)
    ch.hp_max = req.hp_max; ch.hp_current = req.hp_max; ch.ac = req.ac
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
        return {"error": "not found"}
    chars = store.list_characters(campaign_id)
    scene = world.get_scene(campaign_id)
    try:
        c = store.load_combat(campaign_id)
        combat = {"active": c.active, "round": c.round,
                  "initiative_order": [{"name": x.name, "initiative": x.initiative,
                                        "side": x.side} for x in c.initiative_order]}
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
def chat(req: ChatIn):
    """跑一轮硬性判定链。HITL 启用时若 interrupt，返回 interrupted=True 供 /chat/resume 恢复。"""
    out = graph.run(req.player_input, req.campaign_id, req.character_id,
                    req.thread_id, hitl=req.hitl)
    if out.get("__interrupt__"):
        v = out["__interrupt__"][0]
        q = v.value if hasattr(v, "value") else v
        return {"interrupted": True, "thread_id": req.thread_id, "question": q}
    return {
        "narration": out.get("narration", ""),
        "intent": out.get("intent", {}),
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
        return {"error": f"未知分类 {category!r}，可选: {sorted(valid_cats)}"}
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
        return {"error": f"角色 {cid} 不存在"}
    feat = F.get_feat(req.feat_name)
    if feat is None:
        return {"error": f"未知专长 {req.feat_name!r}"}
    current = ch.feats
    if req.feat_name in current and not feat["repeatable"]:
        return {"error": f"专长 {req.feat_name!r} 不可重复选择"}
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
        return {"error": f"角色 {cid} 不存在"}
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
        return {"error": f"角色 {cid} 不存在"}

    char_dict = {
        "level": ch.level,
        "feats": list(ch.feats),
    }
    try:
        result = lu.select_feat(char_dict, req.feat_name)
    except ValueError as e:
        return {"error": str(e)}

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
    is_host: bool = False       # 房主首次加入时为 True


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
        return {"error": "room_not_found"}

    # 先创建角色卡（关联到房间对应的战役）
    ch = models.Character(name=req.name, race=req.race,
                          char_class=req.char_class, level=req.level,
                          campaign_id=room.campaign_id)
    ch.set_abilities(req.abilities)
    ch.hp_max = req.hp_max; ch.hp_current = req.hp_max
    ch.ac = req.ac; ch.speed = req.speed
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
            return {"error": result["error"]}

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
        return {"error": "room_not_found"}
    return room.to_dict()


@app.get("/rooms")
def list_rooms():
    """列出所有活跃房间。"""
    return {"rooms": room_manager.list_rooms()}


class KickIn(BaseModel):
    """房主踢出玩家。"""
    target_name: str


@app.post("/room/{room_id}/kick")
def kick_player(room_id: str, req: KickIn):
    """房主踢出指定玩家。

    说明: 此处用 requester_ws=None 表示非WebSocket上下文调用，
          实际踢人权限校验应在WebSocket消息处理中完成。
    """
    room = room_manager.get_room(room_id)
    if room is None:
        return {"error": "room_not_found"}
    # 找到目标玩家
    target = room.find_player_by_name(req.target_name)
    if target is None:
        return {"error": "player_not_found"}
    if target["is_host"]:
        return {"error": "cannot_kick_host"}
    # 从房间移除
    room.players = [p for p in room.players
                    if p["name"] != req.target_name]
    return {"kicked": req.target_name, "room": room.to_dict()}


class TransferIn(BaseModel):
    """房主转让权限。"""
    target_name: str


@app.post("/room/{room_id}/transfer")
def transfer_host(room_id: str, req: TransferIn):
    """房主将房主权限转让给另一玩家。"""
    room = room_manager.get_room(room_id)
    if room is None:
        return {"error": "room_not_found"}
    target = room.find_player_by_name(req.target_name)
    if target is None:
        return {"error": "player_not_found"}
    # 转让
    for p in room.players:
        p["is_host"] = (p["name"] == req.target_name)
    return {"new_host": req.target_name, "room": room.to_dict()}


# ── 战利品分配 ─────────────────────────────────────────────────────────

from ..brain import loot_distribution as loot


class LootPoolIn(BaseModel):
    """生成战利品池。"""
    campaign_id: int
    monster_crs: list[int]           # 击败怪物的CR列表
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


@app.post("/loot/distribute")
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
        return {"error": f"未知分配模式 {req.mode!r}"}

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
