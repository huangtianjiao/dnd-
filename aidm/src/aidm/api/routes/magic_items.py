"""魔法物品路由。"""

from __future__ import annotations

from fastapi import APIRouter

from ...data import magic_items as mi_db

router = APIRouter(tags=["magic_items"])


@router.get("/magic-items")
def list_magic_items(rarity: str | None = None,
                     item_type: str | None = None,
                     cursed_only: bool = False):
    """返回魔法物品数据库。"""
    rar = None
    if rarity is not None:
        try:
            rar = mi_db.Rarity[rarity.upper()]
        except KeyError:
            return {"error": f"未知稀有度: {rarity}"}

    itype = None
    if item_type is not None:
        try:
            itype = mi_db.ItemType[item_type.upper().replace("-", "_")]
        except KeyError:
            return {"error": f"未知类别: {item_type}"}

    items = mi_db.list_magic_items(rarity=rar, item_type=itype, cursed_only=cursed_only)
    return {"items": [item.to_dict() for item in items], "count": len(items)}


@router.get("/magic-items/{name}")
def get_magic_item(name: str):
    """查询特定魔法物品。"""
    item = mi_db.get_magic_item(name)
    if item is None:
        return {"error": f"未找到魔法物品: {name}"}
    return item.to_dict()
