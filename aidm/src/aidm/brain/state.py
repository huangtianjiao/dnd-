"""P3 编排状态 — GameState（贯穿 LangGraph 图节点的状态对象）。

设计原则（ARCHITECTURE §4）：LLM 只在 classify(意图) 与 narrate(叙事) 两端活动，
中间 retrieve→verify→resolve(骰子) 全代码。GameState 承载每轮流转的数据。
v2: 扩展 cast/ability_check/explore/start_combat 意图 + combat 跟踪 + hitl。
v3: 从 TypedDict 升级为 Pydantic v2 BaseModel，获得类型安全、默认值与字段验证，
    防止字段遗漏被 LangGraph 静默丢弃（BUG#1: action_options 丢失）。
    保留 dict-like 访问接口（__getitem__ / get / __setitem__）以兼容现有节点代码。
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ── 合法 action_type 枚举（与 classify prompt 保持一致）──────────────────
_VALID_ACTION_TYPES: frozenset[str] = frozenset({
    "attack", "cast", "ability_check", "explore", "start_combat", "end_combat",
    "rest", "social", "levelup", "travel", "hide", "search", "grapple", "shove",
    "dash", "dodge", "disengage", "help", "ready", "use_item", "study",
    "opportunity_attack", "other",
})


class GameState(BaseModel):
    """一轮玩家输入经判定链流转的状态。

    LangGraph StateGraph(GameState) 原生支持 Pydantic BaseModel：
    - invoke() 传入的 init dict 会经 Pydantic 校验，缺失字段自动填充默认值。
    - 节点收到的是 Pydantic 实例，但本类提供了 dict-like 访问接口
      （__getitem__ / __setitem__ / get / __contains__），因此现有
      state["field"] / state.get("field", default) 代码无需修改。
    """

    model_config = {"extra": "allow"}          # 允许 LangGraph 注入 __interrupt__ 等内部字段

    # ── 输入 ──────────────────────────────────────────────────────────
    player_input: str = ""
    campaign_id: int = 0
    character_id: int = 0
    hitl: bool = False                         # 是否启用 HITL（关键判定暂停让 DM 确认）

    # ── 各节点产物 ────────────────────────────────────────────────────
    intent: dict[str, Any] = Field(default_factory=dict)
    evidence: list[Any] = Field(default_factory=list)
    verification: dict[str, Any] = Field(default_factory=dict)
    confirmed: bool = False                    # HITL confirm 产物: DM 确认结果
    dice: dict[str, Any] = Field(default_factory=dict)
    narration: str = ""
    state_changes: list[Any] = Field(default_factory=list)
    scene_update: str = ""                     # 行动后场景新状态叙事（apply_node 据此更新 Scene.situation）
    location_change: str = ""                  # 玩家实际移动到的新地点短名（原地行动为空串）
    action_options: list[Any] = Field(default_factory=list)   # 玩家下一步可做的3个行动选项
    combat: dict[str, Any] = Field(default_factory=dict)      # 战斗状态: {active, combat_id, round, current_index, combatants}

    # ── 元 ────────────────────────────────────────────────────────────
    error: str = ""
    summary: str = ""                          # rolling summary（防上下文失忆）

    # ── dict-like 向后兼容接口 ────────────────────────────────────────
    # LangGraph 1.2.x 将 Pydantic BaseModel 作为 state 时，节点收到的是
    # 模型实例而非 dict。以下方法让 state["field"] / state.get(...) 继续可用。

    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            # extra 字段（如 __interrupt__）存储在 __pydantic_extra__
            extra = self.__pydantic_extra__ or {}
            if key in extra:
                return extra[key]
            raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self.model_fields:
            object.__setattr__(self, key, value)
        else:
            # 写入 extra 字段
            if self.__pydantic_extra__ is None:
                object.__setattr__(self, "__pydantic_extra__", {})
            self.__pydantic_extra__[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key: str) -> bool:
        if key in self.model_fields:
            return True
        extra = self.__pydantic_extra__ or {}
        return key in extra
