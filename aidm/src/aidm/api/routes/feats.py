"""专长系统路由（PHB 第五章）。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...stats import store

router = APIRouter(tags=["feats"])


class FeatIn(BaseModel):
    feat_name: str


class SelectFeatIn(BaseModel):
    feat_name: str


@router.get("/feats")
def list_feats_api(category: str | None = None):
    """返回可选专长列表。"""
    from ...data import feats as F
    valid_cats = set(F.feat_categories())
    if category is not None and category not in valid_cats:
        raise HTTPException(status_code=400, detail={"error": "invalid_request", "message": f"未知分类 {category!r}，可选: {sorted(valid_cats)}"})
    return {"feats": F.list_feats(category), "count": len(F.list_feats(category))}


@router.post("/character/{cid}/feat")
def add_feat(cid: int, req: FeatIn):
    """为角色选择一个专长。"""
    from ...data import feats as F
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


@router.get("/character/{cid}/available-feats")
def available_feats_api(cid: int):
    """返回角色当前等级可选的专长列表。"""
    from ...brain import levelup as lu
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


@router.post("/character/{cid}/select-feat")
def select_feat_api(cid: int, req: SelectFeatIn):
    """为角色选择一个专长并持久化。"""
    from ...brain import levelup as lu
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
