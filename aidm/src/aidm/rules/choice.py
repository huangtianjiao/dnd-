"""Choice 系统 — 管理角色创建/升级时的选择请求"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ChoiceRequest:
    """一个选择请求"""

    choice_id: str
    entity_id: str
    choice_type: str  # "skill" / "language" / "tool" / "feat" / "spell" / "ability_score"
    options: List[str] = field(default_factory=list)
    num_to_choose: int = 1
    source_feature_id: str = ""

    def to_dict(self) -> dict:
        return {
            "choice_id": self.choice_id,
            "entity_id": self.entity_id,
            "choice_type": self.choice_type,
            "options": self.options,
            "num_to_choose": self.num_to_choose,
            "source_feature_id": self.source_feature_id,
        }


@dataclass
class ChoiceRecord:
    """一条选择记录"""

    record_id: str
    choice_request_id: str
    entity_id: str
    chosen: List[str] = field(default_factory=list)
    validated: bool = False

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "choice_request_id": self.choice_request_id,
            "entity_id": self.entity_id,
            "chosen": self.chosen,
            "validated": self.validated,
        }


class ChoiceManager:
    """管理选择请求与记录"""

    def __init__(self) -> None:
        self._requests: Dict[str, ChoiceRequest] = {}  # choice_id -> request
        self._records: Dict[str, List[ChoiceRecord]] = {}  # entity_id -> records

    def create_request(
        self,
        entity_id: str,
        choice_type: str,
        options: List[str],
        num_to_choose: int = 1,
        source_feature_id: str = "",
    ) -> ChoiceRequest:
        """创建一个新的选择请求"""
        req = ChoiceRequest(
            choice_id=str(uuid.uuid4()),
            entity_id=entity_id,
            choice_type=choice_type,
            options=list(options),
            num_to_choose=num_to_choose,
            source_feature_id=source_feature_id,
        )
        self._requests[req.choice_id] = req
        return req

    def get_request(self, choice_id: str) -> Optional[ChoiceRequest]:
        """获取指定请求"""
        return self._requests.get(choice_id)

    def get_pending_requests(self, entity_id: str) -> List[ChoiceRequest]:
        """获取实体所有未完成的请求"""
        completed_ids = {
            r.choice_request_id for r in self._records.get(entity_id, []) if r.validated
        }
        return [
            req
            for req in self._requests.values()
            if req.entity_id == entity_id and req.choice_id not in completed_ids
        ]

    def validate_choice(self, request: ChoiceRequest, chosen: List[str]) -> bool:
        """校验选择是否合法"""
        if len(chosen) != request.num_to_choose:
            return False
        # 检查所有选项都在候选中
        for c in chosen:
            if c not in request.options:
                return False
        # 检查不能重复选择
        if len(set(chosen)) != len(chosen):
            return False
        return True

    def record_choice(self, request: ChoiceRequest, chosen: List[str]) -> Optional[ChoiceRecord]:
        """记录一个选择，如果校验失败返回 None"""
        if not self.validate_choice(request, chosen):
            return None
        record = ChoiceRecord(
            record_id=str(uuid.uuid4()),
            choice_request_id=request.choice_id,
            entity_id=request.entity_id,
            chosen=list(chosen),
            validated=True,
        )
        self._records.setdefault(request.entity_id, [])
        self._records[request.entity_id].append(record)
        return record

    def get_records(self, entity_id: str) -> List[ChoiceRecord]:
        """获取实体的所有选择记录"""
        return list(self._records.get(entity_id, []))

    def get_chosen(self, entity_id: str, choice_type: str = "") -> List[str]:
        """获取实体已选择的所有项，可按类型过滤"""
        results: List[str] = []
        for rec in self._records.get(entity_id, []):
            if not rec.validated:
                continue
            req = self._requests.get(rec.choice_request_id)
            if req and (not choice_type or req.choice_type == choice_type):
                results.extend(rec.chosen)
        return results
