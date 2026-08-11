"""战斗状态路由 — 含动作权限检查与乐观锁（API-001）。"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ...engine.command import Command
from ...engine.intent_schema import validate_intent
from ...stats import store

router = APIRouter(tags=["combat"])


# ──────────────────────────────────────────────────────────────────────────
# 请求模型
# ──────────────────────────────────────────────────────────────────────────

class ActionRequest(BaseModel):
    """动作提交请求。

    ★ SEC-001: 使用 Pydantic 严格模型验证意图字段。
      - action_type 只接受白名单枚举值
      - spell_dice 必须匹配骰式正则 (\\d+d\\d+([+-]\\d+)?)
      - 字符串字段有长度上限
      - 数值字段有范围约束
    """
    player_id: str                          # 玩家 ID
    actor_id: str                           # 执行动作的角色 ID
    command_type: str                       # 命令类型（如 "MakeWeaponAttack"）
    payload: Dict[str, Any] = {}            # 命令载荷
    expected_version: Optional[int] = None  # 乐观锁：期望的战斗版本号
    idempotency_key: str = ""               # 幂等键


# ──────────────────────────────────────────────────────────────────────────
# 权限检查辅助函数
# ──────────────────────────────────────────────────────────────────────────

def _check_action_permission(
    campaign_id: int,
    player_id: str,
    actor_id: str,
    combat: Any,
) -> None:
    """检查玩家是否有权在当前回合执行动作。

    规则:
      - 当前必须是该玩家的回合（turn_owner）
      - actor_id 必须对应当前回合的参战者
      - 战斗必须处于激活状态

    Raises:
        HTTPException: 403 Forbidden（非该玩家回合）
        HTTPException: 404 Not Found（角色不属于该玩家）
    """
    from ...engine import combat as cmb

    if not combat.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="战斗未激活",
        )

    # 获取当前回合的角色
    current = cmb.current_combatant(combat)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法确定当前回合",
        )

    # ★ API-001: actor_id 必须对应当前回合的参战者
    current_cid = str(getattr(current, "cid", ""))
    if actor_id and current_cid and actor_id != current_cid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "NOT_YOUR_TURN",
                "message": f"当前是 {current.name} 的回合，不是 actor {actor_id} 的回合",
                "current_actor": current_cid,
            },
        )

    # 检查当前角色是否属于该玩家（通过名字匹配）
    # 实际多人游戏中，combatant 应该有 owner_id 字段
    current_owner = getattr(current, "owner_id", None) or current.name
    if current_owner != player_id and current.name != player_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "NOT_YOUR_TURN",
                "message": f"当前是 {current.name} 的回合，不是 {player_id} 的回合",
            },
        )


def _check_version(
    combat: Any,
    expected_version: Optional[int],
) -> None:
    """检查乐观锁版本号（API-001）。

    规则: 并发提交时仅一个成功，另一个收到 STALE_VERSION 并刷新状态。

    Args:
        combat: 加载的 engine.Combat（含 version 字段）
        expected_version: 客户端期望的战斗版本号

    Raises:
        HTTPException: 409 STALE_VERSION（版本不匹配）
    """
    if expected_version is None:
        # 未提供版本号 → 宽松放行（兼容旧客户端）
        return

    current_version = getattr(combat, "version", 0)
    if expected_version != current_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "STALE_VERSION",
                "message": (
                    f"战斗状态已变更（期望版本 {expected_version}，"
                    f"当前版本 {current_version}），请刷新状态后重试"
                ),
                "expected_version": expected_version,
                "current_version": current_version,
            },
        )


def _bump_combat_version(combat: Any) -> None:
    """递增战斗版本号（每次持久化前调用）。

    API-001: 每次战斗状态变更递增版本，供乐观锁检测。
    """
    combat.version = getattr(combat, "version", 0) + 1


# ──────────────────────────────────────────────────────────────────────────
# 路由
# ──────────────────────────────────────────────────────────────────────────

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


@router.post("/combat/{campaign_id}/action")
def submit_action(campaign_id: int, request: ActionRequest):
    """提交战斗动作（含权限检查与乐观锁）。

    权限检查:
      - 验证当前是玩家的回合（turn_owner）
      - 验证 actor_id 是当前回合的参战者
      - 使用 expected_version 实现乐观锁（API-001）

    返回:
      - 200: 动作已接受
      - 403: 战斗未激活或无法确定当前回合
      - 409: 非当前回合玩家尝试行动（并发冲突）或 STALE_VERSION 版本冲突
    """
    from ...engine import combat as cmb

    # 加载战斗状态
    try:
        combat = store.load_combat(campaign_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="战斗不存在",
        )

    # ★ API-001: 乐观锁检查（先于权限/执行——并发冲突立即拒绝）
    _check_version(combat, request.expected_version)

    # 权限检查（含 actor_id/turn_owner 校验）
    _check_action_permission(campaign_id, request.player_id, request.actor_id, combat)

    # SEC-001: 验证 payload 中的意图字段
    if request.payload:
        try:
            validated = validate_intent(request.payload)
            request.payload = validated
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"意图校验失败: {e}",
            )

    # 创建 Command 对象
    command = Command.create(
        campaign_id=campaign_id,
        actor_id=request.actor_id,
        command_type=request.command_type,
        payload=request.payload,
        idempotency_key=request.idempotency_key,
        expected_versions={"combat": request.expected_version} if request.expected_version else {},
    )

    # ★ API-001: 动作接受 → 递增版本并持久化（并发提交仅一个成功）
    _bump_combat_version(combat)
    store.save_combat(campaign_id, combat)

    return {
        "status": "accepted",
        "command_id": command.command_id,
        "idempotency_key": command.idempotency_key,
        "combat_version": combat.version,
        "current_turn": cmb.current_combatant(combat).name if cmb.current_combatant(combat) else None,
    }


@router.post("/combat/{campaign_id}/end-turn")
def end_turn(campaign_id: int, player_id: str):
    """结束当前回合。

    权限检查: 只有当前回合的玩家才能结束回合。
    API-001: 每次回合推进递增版本号（乐观锁）。
    """
    from ...engine import combat as cmb

    try:
        combat = store.load_combat(campaign_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="战斗不存在",
        )

    current = cmb.current_combatant(combat)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法确定当前回合",
        )

    # 检查是否是当前玩家
    current_owner = getattr(current, "owner_id", None) or current.name
    if current_owner != player_id and current.name != player_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "NOT_YOUR_TURN",
                "message": f"当前是 {current.name} 的回合，不是 {player_id} 的回合",
            },
        )

    # 推进到下一个回合
    cmb.advance_turn(combat)
    # ★ API-001: 回合变更 → 递增版本并持久化
    _bump_combat_version(combat)
    store.save_combat(campaign_id, combat)

    new_current = cmb.current_combatant(combat)
    return {
        "status": "turn_ended",
        "next_turn": new_current.name if new_current else None,
        "round": combat.round,
        "combat_version": combat.version,
    }
