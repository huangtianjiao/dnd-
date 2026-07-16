"""异步记忆处理 — 后台执行，不阻塞 API/WebSocket 响应。

将 process_turn_memories() 从 graph.py 的 apply_node 中剥离，
改为在 narrate 输出后由 API 层异步触发。
"""

from __future__ import annotations

import asyncio
import functools

from ..stats import store


def _run_memory_process(campaign_id: int, player_input: str,
                        narration: str, intent: dict) -> None:
    """后台同步执行记忆处理（在线程池中调用）。"""
    try:
        from ..brain.memory import process_turn_memories
        turn = 0
        try:
            logs = store.get_recent_logs(campaign_id, n=1)
            turn = logs[0].id if logs else 0
        except Exception:
            pass
        process_turn_memories(
            campaign_id=campaign_id,
            player_input=player_input,
            narration=narration,
            intent=intent,
            turn=turn,
        )
    except Exception:
        pass


async def _async_memory_process(campaign_id: int, player_input: str,
                                narration: str, intent: dict) -> None:
    """异步后台执行记忆处理，不阻塞响应。"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        functools.partial(_run_memory_process,
                          campaign_id, player_input, narration, intent),
    )
