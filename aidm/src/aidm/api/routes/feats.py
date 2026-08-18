"""专长系统路由（PHB 第五章 / 方案 §8.2 FeatEntitlementService）。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...stats import store
from .dependencies import require_character_owner, require_session

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
def add_feat(cid: int, req: FeatIn, claims: dict = Depends(require_session)):
    """为角色选择一个专长（★ P5: 与 character 路由同等 owner guard + entitlement 校验）。

    规则: 方案 §8.2 —— 专长只能通过 entitlement + 先决条件选择，
    API 不再是无条件向 feats_json 追加字符串的旁路。
    """
    require_character_owner(cid, claims)
    from ...data import feats as F
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    feat = F.get_feat(req.feat_name)
    if feat is None:
        raise HTTPException(status_code=400, detail={"error": "invalid_request", "message": f"未知专长 {req.feat_name!r}"})
    if feat["category"] == "起源":
        raise HTTPException(status_code=422, detail={"error": "invalid_request",
            "message": "起源专长仅在 1 级创建时由背景给予，升级流程不可选择"})
    current = ch.feats
    if req.feat_name in current and not feat["repeatable"]:
        raise HTTPException(status_code=400, detail={"error": "invalid_request", "message": f"专长 {req.feat_name!r} 不可重复选择"})
    if req.feat_name not in current:
        current.append(req.feat_name)
    ch.set_feats(current)
    ch = store.save_character(ch)
    return {"id": ch.id, "name": ch.name, "feats": ch.feats}


@router.get("/character/{cid}/available-feats")
def available_feats_api(cid: int, claims: dict = Depends(require_session)):
    """返回角色当前可选的专长列表（★ P5: entitlement 驱动，不再依赖全局 FEAT_LEVELS）。"""
    require_character_owner(cid, claims)
    from ...brain import levelup as lu
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})
    char_dict = {
        "level": ch.level,
        "feats": ch.feats,
        "class_levels": ch.class_levels,
    }
    avail = lu.available_feats(char_dict)
    from ...rules.feat_entitlement import is_entitled_at
    feat_available = is_entitled_at(ch.level, ch.class_levels)
    return {
        "level": ch.level,
        "feat_available": feat_available,
        "available_feats": avail,
        "count": len(avail),
    }


@router.post("/character/{cid}/select-feat")
def select_feat_api(cid: int, req: SelectFeatIn, claims: dict = Depends(require_session)):
    """为角色选择一个专长并持久化（★ P5: owner guard + entitlement 驱动）。"""
    require_character_owner(cid, claims)
    from ...brain import levelup as lu
    from ...rules.feat_entitlement import is_entitled_at
    ch = store.get_character(cid)
    if ch is None:
        raise HTTPException(status_code=404, detail={"error": "not found", "message": f"角色 {cid} 不存在"})

    # ★ P5: entitlement 校验——非节点等级不可选择通用/战斗风格专长
    from ...data import feats as F
    feat = F.get_feat(req.feat_name)
    if (feat is not None and feat["category"] in ("通用", "战斗风格")
            and not is_entitled_at(ch.level, ch.class_levels)):
        raise HTTPException(status_code=422, detail={"error": "invalid_request",
            "message": f"等级 {ch.level} 不是 ASI/专长 entitlement 节点，无法选择专长"})

    char_dict = {
        "level": ch.level,
        "feats": list(ch.feats),
        "class_levels": ch.class_levels,
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
