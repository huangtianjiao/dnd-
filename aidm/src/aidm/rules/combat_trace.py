"""ResolutionTrace — 动作结算的可解释痕迹（方案 §11.4）。

Narrator 的输入是 ResolutionTrace，而不是原始数据库对象或
"请你判断发生了什么"。trace 覆盖关键 mechanical facts：
动作/攻击骰/加值/目标AC/命中/伤害骰/伤害/精通/消耗资源/状态变更。
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ResolutionTrace:
    """一次动作解析的确定性记录（供叙事/审计/回放）。"""

    action: str = ""
    attack_roll: int | None = None
    attack_bonus: int | None = None
    target_ac: int | None = None
    hit: bool | None = None
    damage_roll: str = ""
    damage: int = 0
    mastery: str = ""
    resources_spent: list[dict] = field(default_factory=list)
    state_changes: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


def attack_trace(*, weapon: str = "", attack_roll: int = 0,
                 attack_bonus: int = 0, target_ac: int = 0,
                 hit: bool = False, damage_roll: str = "",
                 damage: int = 0, mastery: str = "",
                 resources_spent: list[dict] | None = None,
                 notes: list[str] | None = None) -> ResolutionTrace:
    """从攻击结算结果构造 trace（唯一构造入口，方案 §11.4 示例字段）。"""
    return ResolutionTrace(
        action=f"attack:{weapon}" if weapon else "attack",
        attack_roll=int(attack_roll),
        attack_bonus=int(attack_bonus),
        target_ac=int(target_ac),
        hit=bool(hit),
        damage_roll=damage_roll,
        damage=int(damage),
        mastery=mastery,
        resources_spent=list(resources_spent or []),
        notes=list(notes or []),
    )


def narratable(trace: ResolutionTrace) -> dict:
    """供甲方叙事的最小视图（不含内部状态细节，符合 AI 契约 §11.5）。"""
    d = trace.to_dict()
    return {k: v for k, v in d.items()
            if k not in ("state_changes",) or not v}


# ──────────────────────────────────────────────────────────────────────────
# 便捷序列化（战斗/法术结算复用时）
# ──────────────────────────────────────────────────────────────────────────

def trace_from_dict(data: dict) -> ResolutionTrace:
    valid = set(ResolutionTrace.__dataclass_fields__)
    return ResolutionTrace(**{k: v for k, v in data.items() if k in valid})


def any_to_trace(action: str, **kwargs: Any) -> ResolutionTrace:
    """普通动作（治疗/移动等）的最小 trace。"""
    return ResolutionTrace(action=action, **{k: v for k, v in kwargs.items()
                                              if k in ResolutionTrace.__dataclass_fields__})
