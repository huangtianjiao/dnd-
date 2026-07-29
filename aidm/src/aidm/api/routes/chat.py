"""聊天跑团路由。"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter
from pydantic import BaseModel

from ...brain import graph
from ...stats import store
from ..memory_bg import _async_memory_process
from ..ws import get_campaign_lock
from .dependencies import ChatIn, ResumeIn

router = APIRouter(tags=["chat"])


class SessionEndIn(BaseModel):
    campaign_id: int


@router.post("/chat")
async def chat(req: ChatIn):
    """跑一轮硬性判定链。HITL 启用时若 interrupt，返回 interrupted=True 供 /chat/resume 恢复。"""
    loop = asyncio.get_event_loop()
    async with get_campaign_lock(req.campaign_id):
        out = await loop.run_in_executor(
            None,
            lambda: graph.run(req.player_input, req.campaign_id, req.character_id,
                              req.thread_id, hitl=req.hitl))
    if out.get("__interrupt__"):
        v = out["__interrupt__"][0]
        q = v.value if hasattr(v, "value") else v
        return {"interrupted": True, "thread_id": req.thread_id, "question": q}

    # 异步后台执行记忆处理，不阻塞响应
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


@router.post("/chat/resume")
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


@router.get("/summary/{campaign_id}")
def summary(campaign_id: int):
    return {"summary": store.get_summary(campaign_id)}


@router.post("/session/end")
def session_end(req: SessionEndIn):
    """Session 结束时生成前情提要（浓缩摘要）。"""
    from ...brain.memory import generate_recap
    recap = generate_recap(req.campaign_id)
    return {"recap": recap}
