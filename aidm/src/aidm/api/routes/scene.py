"""场景/世界路由。"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from .dependencies import OpenIn

router = APIRouter(tags=["scene"])


class GenSettingIn(BaseModel):
    theme: str = ""


@router.post("/open")
def open_campaign(req: OpenIn):
    """DM 开场：依据世界设定生成完整背景+当前场景+3个行动选项。"""
    from ...brain import world
    r = world.open_campaign(req.setting, req.tone, req.campaign_id, req.character_id)
    return {"narration": r["narration"], "action_options": r.get("action_options", []),
            "scene": r["scene"]}


@router.get("/scene/{campaign_id}")
def get_scene(campaign_id: int):
    """取当前场景（前端场景面板用）。"""
    from ...brain import world
    return world.get_scene(campaign_id)


@router.post("/generate_setting")
def generate_setting(req: GenSettingIn):
    """AI 生成世界设定（给玩家灵感，可编辑后提交）。"""
    from ...brain import llm
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


@router.get("/monster/{name}")
def get_monster(name: str):
    """怪物数值检索（从 data.js RAG 查怪物属性块）。"""
    from ...knowledge import indexer
    from fastapi import HTTPException
    try:
        res = indexer.search(name, limit=1)
    except Exception:
        raise HTTPException(status_code=503, detail={"error": "collection not available", "message": "规则库索引不可用"})
    if res:
        return {"name": res[0].get("title", ""), "body": res[0].get("body", "")[:800],
                "tag": res[0].get("tag", ""), "path": res[0].get("path", "")}
    raise HTTPException(status_code=404, detail={"error": "not found", "message": f"未找到怪物: {name}"})


@router.get("/players/{campaign_id}")
def get_players(campaign_id: int):
    """列出在线玩家。"""
    from ..ws import manager
    return {"players": manager.get_players(campaign_id),
            "current_turn": manager.current_turn_name(campaign_id)}
