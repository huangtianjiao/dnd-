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
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from ..stats import store, models
from ..brain import graph

app = FastAPI(title="AI DM", version="0.2.0")

# WebSocket 实时同桌
from .ws import manager, websocket_endpoint

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
            "spell_slots": ch.spell_slots, "dead": ch.dead, "stable": ch.stable}


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


@app.websocket("/ws/{campaign_id}")
async def ws_endpoint(ws: WebSocket, campaign_id: int,
                     character_id: int = 0, name: str = "玩家"):
    """WebSocket 实时同桌端点。"""
    await websocket_endpoint(ws, campaign_id, character_id, name)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
