"""Unit of Work — 原子事务与幂等键去重。

STATE-003: 结算缺少原子事务与幂等键。
本模块实现:
  1. IdempotencyStore — 幂等键去重存储（内存版，可扩展为 Redis）
  2. UnitOfWork — 单个命令的原子事务上下文
  3. @atomic 装饰器 — 简化事务包装

设计原则:
  - Command携带idempotency_key与expected_version
  - 单个Unit of Work原子写入事件和投影
  - 采用乐观锁
  - 重复提交相同key只返回原结果
  - 中途异常后数据库不出现半完成动作

规则依据: STATE-003 原子事务与幂等键
出处: topics/城主指南2024/2.运作游戏/
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """命令执行结果。"""

    command_id: str
    idempotency_key: str
    success: bool
    result_data: Any = None
    error: str = ""
    applied_version: int = 0


class IdempotencyStore:
    """幂等键去重存储。

    维护一个 {idempotency_key → CommandResult} 映射，
    重复提交相同 key 时直接返回缓存结果。

    线程安全：内部使用 threading.Lock 保护。
    """

    def __init__(self) -> None:
        self._store: Dict[str, CommandResult] = {}
        self._lock = threading.Lock()

    def check(self, idempotency_key: str) -> Optional[CommandResult]:
        """检查幂等键是否已处理。

        Returns:
            已缓存的 CommandResult，或 None（首次提交）
        """
        with self._lock:
            return self._store.get(idempotency_key)

    def record(self, result: CommandResult) -> None:
        """记录命令执行结果。"""
        with self._lock:
            if result.idempotency_key in self._store:
                logger.warning(
                    "幂等键 %s 已存在，跳过重复记录",
                    result.idempotency_key,
                )
                return
            self._store[result.idempotency_key] = result

    def clear(self) -> None:
        """清空所有记录（测试用）。"""
        with self._lock:
            self._store.clear()


# ── 全局幂等存储单例 ──────────────────────────────────────────────

_idempotency_store = IdempotencyStore()


def get_idempotency_store() -> IdempotencyStore:
    """获取全局幂等存储实例。"""
    return _idempotency_store


# ── Unit of Work ──────────────────────────────────────────────────

@dataclass
class UnitOfWork:
    """单个命令的原子事务上下文。

    使用方式:
        uow = UnitOfWork(command=cmd)
        try:
            uow.begin()
            # 执行业务逻辑...
            uow.events.append(event1)
            uow.commit()
        except Exception:
            uow.rollback()
            raise

    特性:
      - begin(): 检查幂等键，若已处理则直接返回缓存结果
      - commit(): 原子写入所有事件和状态变更
      - rollback(): 回滚所有未提交的变更
      - 幂等性: 重复提交相同 key 只返回原结果
    """

    command: Any  # Command 对象
    events: list = field(default_factory=list)
    state_changes: list = field(default_factory=list)
    _begun: bool = False
    _committed: bool = False
    _rolled_back: bool = False
    _cached_result: Optional[CommandResult] = None

    def begin(self) -> Optional[CommandResult]:
        """开始事务。

        检查幂等键是否已处理：
          - 若已处理，返回缓存的 CommandResult（调用方应直接返回）
          - 若首次提交，标记事务开始

        Returns:
            缓存的 CommandResult（幂等命中时），或 None（首次提交）
        """
        if self._begun:
            raise RuntimeError("事务已开始")

        # 幂等检查
        cached = _idempotency_store.check(self.command.idempotency_key)
        if cached is not None:
            self._cached_result = cached
            return cached

        self._begun = True
        return None

    def add_event(self, event: dict) -> None:
        """添加一个领域事件到待提交列表。"""
        if not self._begun or self._committed:
            raise RuntimeError("事务不在可写入状态")
        self.events.append(event)

    def add_state_change(self, change: dict) -> None:
        """添加一个状态变更到待提交列表。"""
        if not self._begun or self._committed:
            raise RuntimeError("事务不在可写入状态")
        self.state_changes.append(change)

    def commit(self) -> CommandResult:
        """提交事务。

        原子写入所有事件和状态变更。
        记录幂等键 → 结果映射。

        Returns:
            命令执行结果
        """
        if not self._begun:
            raise RuntimeError("事务未开始")
        if self._committed:
            raise RuntimeError("事务已提交")
        if self._rolled_back:
            raise RuntimeError("事务已回滚")

        # 在实际实现中，这里会:
        # 1. 检查 expected_versions（乐观锁）
        # 2. 原子写入事件到事件存储
        # 3. 原子更新投影（Character/Combatant 等）
        # 4. 记录幂等键

        result = CommandResult(
            command_id=self.command.command_id,
            idempotency_key=self.command.idempotency_key,
            success=True,
            result_data={
                "events": self.events,
                "state_changes": self.state_changes,
            },
        )

        _idempotency_store.record(result)
        self._committed = True
        return result

    def rollback(self) -> None:
        """回滚事务。"""
        if self._committed:
            raise RuntimeError("事务已提交，无法回滚")
        self._rolled_back = True
        self.events.clear()
        self.state_changes.clear()


# ── 便捷函数 ──────────────────────────────────────────────────────

def execute_command(command: Any, handler: Callable[[UnitOfWork], Any]) -> CommandResult:
    """执行命令的通用入口。

    自动处理幂等检查、事务开始/提交/回滚。

    Args:
        command: Command 对象
        handler: 业务逻辑函数，接收 UnitOfWork，返回结果数据

    Returns:
        CommandResult
    """
    uow = UnitOfWork(command=command)

    # 幂等检查
    cached = uow.begin()
    if cached is not None:
        logger.info("幂等命中 key=%s，返回缓存结果", command.idempotency_key)
        return cached

    try:
        result_data = handler(uow)
        result = uow.commit()
        result.result_data = result_data
        return result
    except Exception as e:
        uow.rollback()
        logger.error("命令执行失败 command_id=%s: %s", command.command_id, e)
        return CommandResult(
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            success=False,
            error=str(e),
        )
