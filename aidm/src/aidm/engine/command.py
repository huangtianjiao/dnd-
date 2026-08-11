"""原子命令与幂等键 — Command 数据结构。

所有对游戏状态的变更必须通过 Command 对象提交，携带幂等键防止重复执行，
携带 expected_versions 实现乐观并发控制。

规则依据: STATE-003 原子事务与幂等键
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Command:
    """原子游戏命令。

    每个命令携带唯一 idempotency_key（格式 "session:client_seq"），
    以及 expected_versions 用于乐观锁检测并发冲突。
    """

    command_id: str                          # UUID
    idempotency_key: str                     # "session:client_seq"
    campaign_id: int
    actor_id: str                            # UUID of acting entity
    expected_versions: Dict[str, int] = field(default_factory=dict)  # {"character": 12, "combat": 44}
    command_type: str = ""                   # e.g. "MakeWeaponAttack", "CastSpell"
    payload: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        campaign_id: int,
        actor_id: str,
        command_type: str,
        payload: dict,
        idempotency_key: str = "",
        expected_versions: dict = None,
    ) -> "Command":
        """便捷工厂：自动生成 command_id，缺省时自动生成 idempotency_key。"""
        if not idempotency_key:
            idempotency_key = f"{campaign_id}:{uuid.uuid4()}"
        return cls(
            command_id=str(uuid.uuid4()),
            idempotency_key=idempotency_key,
            campaign_id=campaign_id,
            actor_id=actor_id,
            expected_versions=expected_versions or {},
            command_type=command_type,
            payload=payload,
        )
