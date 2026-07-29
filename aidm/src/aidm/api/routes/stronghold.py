"""据点系统路由（DMG 第八章）。"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from ...brain import stronghold as sh
from ...data.strongholds import OrderType, StrongholdType

router = APIRouter(tags=["stronghold"])


class StrongholdCreateIn(BaseModel):
    """建立据点。"""
    campaign_id: int
    owner_character_id: int
    owner_name: str
    owner_level: int = 5
    name: str
    stronghold_type: str = "塔楼"
    initial_gold: float = 0.0


class StrongholdBuildIn(BaseModel):
    """建设设施。"""
    stronghold_id: str
    facility_name: str
    is_basic: bool = False
    target_space: str | None = None


class StrongholdTurnIn(BaseModel):
    """执行据点回合。"""
    stronghold_id: str
    order_type: str = "维护"
    facility_name: str | None = None


@router.post("/stronghold/create")
def create_stronghold_api(req: StrongholdCreateIn):
    """建立据点 — DMG第八章 §1 建立一个据点。"""
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


@router.get("/stronghold/{campaign_id}")
def get_stronghold_api(campaign_id: int, character_id: int | None = None):
    """获取据点状态 — DMG第八章 据点系统。"""
    return {
        "success": False,
        "error": "据点状态查询需要持久化层支持。请使用 /stronghold/create 创建据点后保存对象。",
        "campaign_id": campaign_id,
        "character_id": character_id,
    }


@router.post("/stronghold/build")
def build_facility_api(req: StrongholdBuildIn):
    """建设设施 — DMG第八章 §3 增添基础设施 / 特色设施详述。"""
    return {
        "success": False,
        "error": "建设设施需要据点对象的持久化层支持。",
        "request": req.dict(),
    }


@router.post("/stronghold/turn")
def run_stronghold_turn_api(req: StrongholdTurnIn):
    """执行据点回合 — DMG第八章 §2 据点回合。"""
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

    return {
        "success": False,
        "error": "据点回合执行需要据点对象的持久化层支持。",
        "request": req.dict(),
    }


@router.get("/strongholds/facilities")
def list_facilities_api(level: int | None = None):
    """返回所有可用特色设施列表 — DMG第八章 §3 特色设施详述。"""
    from ...data.strongholds import FACILITIES

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

    facilities.sort(key=lambda x: (x["level"], x["name"]))

    return {
        "success": True,
        "count": len(facilities),
        "facilities": facilities,
    }
