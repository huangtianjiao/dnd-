"""战斗状态路由。"""

from __future__ import annotations

from fastapi import APIRouter

from ...stats import store

router = APIRouter(tags=["combat"])


@router.get("/combat/{campaign_id}")
def get_combat(campaign_id: int):
    """战斗状态（前端战斗追踪器用）。"""
    from ...engine import combat as cmb
    try:
        c = store.load_combat(campaign_id)
    except Exception:
        return {"active": False}
    cur = cmb.current_combatant(c)
    return {"active": c.active, "round": c.round,
            "current_index": c.current_index,
            "current_turn": cur.name if cur else None,
            "initiative_order": [{"name": x.name, "initiative": x.initiative,
                                  "side": x.side, "hp": x.hp, "hp_max": x.hp_max,
                                  "dead": x.dead, "surprised": getattr(x, "surprised", False)}
                                 for x in c.initiative_order]}
