"""聊天跑团路由。"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException
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
    """跑一轮硬性判定链。HITL 启用时若 interrupt，返回 interrupted=True 供 /chat/resume 恢复。

    ★ P1-02: thread_id 由服务器生成（campaign:{cid}:character:{charid}:session:{uuid}），
      客户端传入的任意/默认 thread_id 被忽略，防止跨战役/跨角色状态串扰。
    ★ P1-04: 客户端可提交 command_id 作为幂等键（重复提交不重复执行）。
    ★ P1-05: 客户端可提交 expected_version（战役乐观锁），不匹配返回 409。
    """
    # P1-02: 服务器权威线程 ID
    thread_id = graph.make_thread_id(req.campaign_id, req.character_id)

    # P1-05: 战役乐观锁检查（可选）
    if req.expected_version is not None:
        camp = store.get_campaign(req.campaign_id)
        current = getattr(camp, "version", 0) if camp else 0
        if camp is None or current != int(req.expected_version):
            raise HTTPException(status_code=409, detail={
                "error": "STALE_VERSION",
                "message": "战役状态已变更，请刷新后重试",
                "expected_version": req.expected_version,
                "current_version": current})

    # P1-04: 幂等键（可选；apply_node 幂等检查 + 重复提交返回缓存结果）
    command_id = (getattr(req, "command_id", "") or "").strip()
    state_extra = {"idempotency_key": command_id} if command_id else {}

    loop = asyncio.get_event_loop()
    async with get_campaign_lock(req.campaign_id):
        out = await loop.run_in_executor(
            None,
            lambda: graph.run(req.player_input, req.campaign_id, req.character_id,
                              thread_id, hitl=req.hitl, **state_extra))
        # P1-05: 行动成功后推进战役版本（乐观锁）
        if req.expected_version is not None:
            try:
                camp = store.get_campaign(req.campaign_id)
                if camp is not None:
                    store.save_campaign(camp, expected_version=int(req.expected_version))
            except store.StaleVersionError:
                raise HTTPException(status_code=409, detail={
                    "error": "STALE_VERSION",
                    "message": "战役状态已变更，请刷新后重试"}) from None
    if out.get("__interrupt__"):
        v = out["__interrupt__"][0]
        q = v.value if hasattr(v, "value") else v
        return {"interrupted": True, "thread_id": thread_id, "question": q}

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
        "thread_id": thread_id,
    }


@router.post("/chat/resume")
async def chat_resume(req: ResumeIn):
    """HITL 恢复：DM 给出 y/n 后继续判定链。

    ★ P1-03: 越权与并发防护——
      1. thread_id 必须为服务器标准格式（campaign:{cid}:character:{charid}:session:{uuid}）
      2. 解析出的 campaign/character 必须与请求方一致（ownership）
      3. 角色必须属于该战役
      4. 全程持 campaign 锁（与 /chat 的 graph.run 互斥，防重复应用）
    """
    from langgraph.types import Command

    parsed = graph.parse_thread_id(req.thread_id)
    if parsed is None:
        raise HTTPException(status_code=400, detail={
            "error": "INVALID_THREAD_ID",
            "message": "线程 ID 非法——只能恢复由服务器签发的会话线程"})
    campaign_id = parsed["campaign_id"]
    thread_character_id = parsed["character_id"]

    # P1-03: 请求方身份必须与线程绑定角色一致
    if req.character_id != thread_character_id:
        raise HTTPException(status_code=403, detail={
            "error": "FORBIDDEN",
            "message": "不能恢复其他角色的 HITL 线程"})
    # 角色必须属于线程对应的战役（防跨战役恢复）
    ch = store.get_character(req.character_id)
    if ch is None or ch.campaign_id != campaign_id:
        raise HTTPException(status_code=403, detail={
            "error": "FORBIDDEN",
            "message": "角色不属于该战役"})

    cfg = {"configurable": {"thread_id": req.thread_id}}
    async with get_campaign_lock(campaign_id):
        loop = asyncio.get_event_loop()
        out = await loop.run_in_executor(
            None,
            lambda: graph.get_graph().invoke(Command(resume=req.answer), config=cfg))
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