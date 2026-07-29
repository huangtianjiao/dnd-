"""战利品路由。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["loot"])


class LootGenerateIn(BaseModel):
    cr: float
    count_enemies: int = 1
    include_magic_items: bool = True
    seed: int | None = None


class LootDistributeInV1(BaseModel):
    """loot.py 体系（method=need_priority/...）的战利品分配请求。"""
    gold: int = 0
    magic_item_names: list[str] = []
    players: list[str]
    method: str = "need_priority"
    needs: dict[str, list[str]] | None = None
    dm_assignments: dict[str, list[str]] | None = None
    gold_method: str = "equal"
    contributions: dict[str, float] | None = None
    seed: int | None = None


class LootPoolIn(BaseModel):
    """生成战利品池。"""
    campaign_id: int
    monster_crs: list[float]
    combat_round: int = 0


class LootDistributeIn(BaseModel):
    """分配战利品。"""
    campaign_id: int
    gold: int = 0
    items: list[dict] = []
    player_names: list[str]
    mode: str = "ROUND_ROBIN"
    initiative_order: list[str] | None = None
    needs: dict[str, list[str]] | None = None
    dm_assignments: dict[str, str] | None = None


@router.post("/loot/generate")
def generate_loot(req: LootGenerateIn):
    """生成随机战利品池。"""
    from ...brain import loot
    pool = loot.generate_loot(
        cr=req.cr,
        count_enemies=req.count_enemies,
        include_magic_items=req.include_magic_items,
        seed=req.seed,
    )
    return pool.to_dict()


@router.post("/loot/distribute")
def distribute_loot_v1(req: LootDistributeInV1):
    """分配战利品（魔法物品 + 金币）。"""
    from ...brain import loot
    from ...data.magic_items import get_magic_item
    from ...stats import store

    magic_items = []
    unassigned_names = []
    for name in req.magic_item_names:
        item = get_magic_item(name)
        if item is not None:
            magic_items.append(item)
        else:
            unassigned_names.append(name)

    pool = loot.LootPool(gold=req.gold, magic_items=magic_items)

    dist = loot.distribute_loot(
        pool=pool,
        players=req.players,
        method=req.method,
        needs=req.needs,
        dm_assignments=req.dm_assignments,
        seed=req.seed,
    )

    gold_dist = loot.distribute_gold(
        total_gold=req.gold,
        players=req.players,
        method=req.gold_method,
        contributions=req.contributions,
    )

    # 持久化金币到角色卡
    for player_name, gold_amount in gold_dist.items():
        if gold_amount > 0:
            ch = store.get_character_by_name(player_name)
            if ch:
                store.add_character_gold(ch.id, gold_amount)

    return {
        "item_distribution": dist.to_dict(),
        "gold_distribution": gold_dist,
        "unrecognized_items": unassigned_names,
        "total_gold": req.gold,
        "total_items": len(magic_items),
    }


@router.post("/loot/pool")
def generate_loot_pool(req: LootPoolIn):
    """根据击败怪物的CR列表生成战利品池。"""
    from ...brain import loot_distribution as loot
    pool = loot.generate_loot_pool(
        campaign_id=req.campaign_id,
        monster_crs=req.monster_crs,
        combat_round=req.combat_round,
    )
    return {
        "pool_id": pool.pool_id,
        "gold": pool.gold,
        "items": [
            {"item_id": it.item_id, "name": it.name,
             "type": it.item_type, "rarity": it.rarity,
             "value_gp": it.value_gp, "quantity": it.quantity,
             "description": it.description}
            for it in pool.items
        ],
    }


@router.post("/loot/distribute/v2")
def distribute_loot(req: LootDistributeIn):
    """执行完整的战利品分配流程（v2）。"""
    from ...brain import loot_distribution as loot
    from ...stats import store
    # 重建 LootPool
    pool = loot.LootPool(
        pool_id=f"distribute_{req.campaign_id}",
        campaign_id=req.campaign_id,
        gold=req.gold,
    )
    for item_data in req.items:
        pool.items.append(loot.LootItem(
            item_id=item_data.get("item_id", ""),
            name=item_data.get("name", ""),
            item_type=item_data.get("type", "misc"),
            rarity=item_data.get("rarity", "普通"),
            value_gp=item_data.get("value_gp", 0),
            quantity=item_data.get("quantity", 1),
            description=item_data.get("description", ""),
        ))

    try:
        mode = loot.DistributionMode(req.mode)
    except ValueError:
        raise HTTPException(status_code=400, detail={"error": "invalid_request", "message": f"未知分配模式 {req.mode!r}"})

    record = loot.distribute_loot(
        pool=pool,
        player_names=req.player_names,
        mode=mode,
        initiative_order=req.initiative_order,
        needs=req.needs,
        dm_assignments=req.dm_assignments,
    )

    # 持久化金币到角色卡
    for player_name, gold_amount in record.gold_distribution.items():
        if gold_amount > 0:
            ch = store.get_character_by_name(player_name, campaign_id=req.campaign_id)
            if ch:
                store.add_character_gold(ch.id, gold_amount)

    return {
        "record_id": record.record_id,
        "mode": record.mode,
        "gold_distribution": record.gold_distribution,
        "item_distribution": record.item_distribution,
        "timestamp": record.timestamp,
    }


@router.get("/loot/history/{campaign_id}")
def get_loot_history(campaign_id: int):
    """获取指定战役的战利品分配历史。"""
    return {"campaign_id": campaign_id, "history": []}
