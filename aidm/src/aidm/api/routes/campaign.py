"""战役管理路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ...stats import store
from .dependencies import CampaignIn, require_campaign_owner, require_session

router = APIRouter(tags=["campaign"])


@router.post("/campaign")
def create_campaign(c: CampaignIn):
    camp = store.create_campaign(c.name)
    return {"id": camp.id, "name": camp.name}


@router.get("/campaigns")
def list_campaigns():
    """列出所有已保存战役（继续游戏用）。"""
    camps = store.list_campaigns()
    return {"campaigns": [
        {"id": c.id, "name": c.name,
         "setting": (c.setting or "")[:80],
         "summary": (c.rolling_summary or "")[:100]}
        for c in camps
    ]}


@router.get("/campaign/{campaign_id}/state")
def get_campaign_state(campaign_id: int,
                       claims: dict = Depends(require_session)):
    """加载战役完整状态（继续游戏用）：战役信息+场景+角色列表+摘要+战斗。

    ★ P0-4: 会话归属校验——只能访问令牌绑定的战役（或 DM/房主）。
    """
    require_campaign_owner(campaign_id, claims)
    from ...brain import world
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
    # 最近对话历史（Log 表逐回合落盘）：继续游戏时恢复叙事流
    history = [{"player_input": lg.player_input, "dm_output": lg.dm_output}
               for lg in store.get_recent_logs(campaign_id, n=20)]
    return {
        "campaign": {"id": camp.id, "name": camp.name, "setting": camp.setting, "tone": camp.tone},
        "scene": scene,
        "characters": [{"id": ch.id, "name": ch.name, "level": ch.level,
                        "hp": ch.hp_current, "hp_max": ch.hp_max, "ac": ch.ac,
                        "char_class": ch.char_class} for ch in chars],
        "summary": (camp.rolling_summary or "")[:300],
        "combat": combat,
        "history": history,
    }
