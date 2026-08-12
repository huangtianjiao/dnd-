"""错误分类（P2-05）— 替换裸异常吞噬的三类错误。

- DomainError: 规则/业务域错误（如非法动作、权限不足）→ 可映射为 4xx
- InfrastructureError: 基础设施错误（DB/LLM/网络/缓存）→ 5xx，需日志含
  campaign_id/character_id/operation/exception type/trace id
- InvariantViolation: 状态不变量被破坏（如乐观锁冲突、重复命令）→ 4xx/5xx

规范:
  1. 禁止 `except Exception: pass` 静默吞错——至少记日志并归类
  2. 生产日志必须包含: campaign_id, character_id, operation, exception type
  3. 未分类异常按 InfrastructureError 兜底
"""

from __future__ import annotations

import traceback
from typing import Any, Optional


class DomainError(Exception):
    """业务域错误（可预期，映射 4xx）。"""

    code: str = "domain_error"
    status_code: int = 400

    def __init__(self, message: str, *, code: str | None = None,
                 status_code: int | None = None,
                 campaign_id: int | None = None,
                 character_id: int | None = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        self.campaign_id = campaign_id
        self.character_id = character_id


class InfrastructureError(Exception):
    """基础设施错误（DB/LLM/网络/缓存，映射 5xx）。"""

    code: str = "infrastructure_error"
    status_code: int = 500

    def __init__(self, message: str, *, operation: str = "",
                 campaign_id: int | None = None,
                 character_id: int | None = None,
                 cause: BaseException | None = None):
        super().__init__(message)
        self.message = message
        self.operation = operation
        self.campaign_id = campaign_id
        self.character_id = character_id
        self.cause = cause


class InvariantViolation(Exception):
    """状态不变量被破坏（乐观锁冲突/重复命令等，映射 409）。"""

    code: str = "invariant_violation"
    status_code: int = 409

    def __init__(self, message: str, *, campaign_id: int | None = None,
                 character_id: int | None = None):
        super().__init__(message)
        self.message = message
        self.campaign_id = campaign_id
        self.character_id = character_id


def log_error(logger, exc: BaseException, *, operation: str = "",
              campaign_id: int | None = None,
              character_id: int | None = None) -> None:
    """统一错误日志（P2-05: 至少含 campaign/character/operation/类型/trace）。"""
    logger.error(
        "operation=%s campaign_id=%s character_id=%s type=%s message=%s\n%s",
        operation, campaign_id, character_id, type(exc).__name__,
        str(exc)[:300], traceback.format_exc(),
    )


def contextualize(exc: BaseException, *, operation: str = "",
                  campaign_id: int | None = None,
                  character_id: int | None = None) -> BaseException:
    """把上下文附着到异常（供日志/响应使用）。"""
    for attr, val in (("operation", operation),
                      ("campaign_id", campaign_id),
                      ("character_id", character_id)):
        if val is not None and not hasattr(exc, attr):
            try:
                setattr(exc, attr, val)
            except Exception:  # noqa: BLE001
                pass
    return exc


def http_error_payload(exc: BaseException) -> dict:
    """把分类异常转为统一响应结构。"""
    if isinstance(exc, DomainError):
        return {"error": exc.code, "message": exc.message}
    if isinstance(exc, InvariantViolation):
        return {"error": exc.code, "message": exc.message}
    if isinstance(exc, InfrastructureError):
        return {"error": exc.code, "message": exc.message}
    return {"error": "internal_error", "message": str(exc) or "内部错误"}


__all__ = [
    "DomainError",
    "InfrastructureError",
    "InvariantViolation",
    "log_error",
    "contextualize",
    "http_error_payload",
]