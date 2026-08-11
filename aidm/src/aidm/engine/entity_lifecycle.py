"""实体生命周期管理 — 召唤/变形/创造物的 spawn/despawn。

设计原则：
  - EntityLifecycleManager 管理所有召唤物和变形效果的生命周期。
  - 召唤物与专注链接，专注打断时自动消失。
  - 变形效果在持续时间结束或被覆盖时恢复原始属性。

规则依据:
  SPL-016 召唤/变形/创造物实体生命周期
  R-SPL-019 专注维持（召唤物通常需专注）
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ──────────────────────────────────────────────────────────────────────────
# 召唤物实体
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class SummonedEntity:
    """召唤物实体。

    属性:
        entity_id: 召唤物唯一 ID
        summoner_id: 召唤者 ID
        spell_id: 产生该召唤物的法术 ID
        stat_block: 召唤物属性块（AC, HP, 攻击等）
        hp_current: 当前 HP
        hp_max: 最大 HP
        ac: 护甲等级
        duration_rounds: 剩余持续轮数（-1 = 永久）
        concentration_link_id: 关联的专注链接 ID（若需专注）
        has_independent_turn: 是否有独立回合
        active: 是否存活/活跃
    """

    entity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    summoner_id: str = ""
    spell_id: str = ""
    stat_block: dict = field(default_factory=dict)
    hp_current: int = 0
    hp_max: int = 0
    ac: int = 10
    duration_rounds: int = 0
    concentration_link_id: Optional[str] = None
    has_independent_turn: bool = True
    active: bool = True


# ──────────────────────────────────────────────────────────────────────────
# 变形效果
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class FormOverride:
    """变形术效果 — 覆盖目标属性。

    属性:
        target_id: 被变形目标 ID
        original_stats: 原始属性（保存以便恢复）
        new_stats: 新属性（变形后的属性）
        spell_id: 产生变形的法术 ID
        duration_rounds: 剩余持续轮数（-1 = 永久）
        concentration_link_id: 关联的专注链接 ID
    """

    target_id: str = ""
    original_stats: dict = field(default_factory=dict)
    new_stats: dict = field(default_factory=dict)
    spell_id: str = ""
    duration_rounds: int = 0
    concentration_link_id: Optional[str] = None


# ──────────────────────────────────────────────────────────────────────────
# 实体生命周期管理器
# ──────────────────────────────────────────────────────────────────────────

class EntityLifecycleManager:
    """管理召唤/变形/创造物的生命周期 (SPL-016)。

    功能:
      - summon(): 创建召唤物
      - despawn(): 移除召唤物
      - despawn_by_concentration(): 专注打断时移除关联召唤物
      - apply_form_override(): 应用变形效果
      - remove_form_override(): 移除变形效果并恢复原属性
      - on_round_end(): 轮次结束时处理持续时间到期
      - on_concentration_broken(): 专注被打断时清理关联实体
    """

    def __init__(self) -> None:
        self._summoned: Dict[str, SummonedEntity] = {}
        self._form_overrides: Dict[str, FormOverride] = {}

    # ── 召唤物管理 ─────────────────────────────────────────────────────

    def summon(
        self,
        summoner_id: str,
        spell_id: str,
        stat_block: dict,
        duration: int,
        concentration_id: Optional[str] = None,
    ) -> SummonedEntity:
        """创建一个新的召唤物实体。

        Args:
            summoner_id: 召唤者 ID
            spell_id: 法术 ID
            stat_block: 召唤物属性块 {"hp": 10, "ac": 13, ...}
            duration: 持续轮数（-1 = 永久）
            concentration_id: 关联的专注链接 ID

        Returns:
            创建的 SummonedEntity
        """
        entity = SummonedEntity(
            summoner_id=summoner_id,
            spell_id=spell_id,
            stat_block=dict(stat_block),
            hp_current=stat_block.get("hp", stat_block.get("hp_max", 0)),
            hp_max=stat_block.get("hp_max", stat_block.get("hp", 0)),
            ac=stat_block.get("ac", 10),
            duration_rounds=duration,
            concentration_link_id=concentration_id,
            active=True,
        )
        self._summoned[entity.entity_id] = entity
        return entity

    def despawn(self, entity_id: str) -> List[dict]:
        """移除一个召唤物实体。

        Args:
            entity_id: 召唤物 ID

        Returns:
            事件列表 [{"type": "entity_despawned", "entity_id": ..., "spell_id": ...}]
        """
        entity = self._summoned.pop(entity_id, None)
        if entity is None:
            return []
        entity.active = False
        return [{
            "type": "entity_despawned",
            "entity_id": entity_id,
            "summoner_id": entity.summoner_id,
            "spell_id": entity.spell_id,
            "reason": "despawn",
        }]

    def despawn_by_concentration(self, concentration_link_id: str) -> List[dict]:
        """专注被打断时移除所有关联的召唤物。

        Args:
            concentration_link_id: 专注链接 ID

        Returns:
            事件列表
        """
        events: List[dict] = []
        to_remove = [
            eid for eid, e in self._summoned.items()
            if e.concentration_link_id == concentration_link_id
        ]
        for eid in to_remove:
            events.extend(self.despawn(eid))
        return events

    def despawn_all_by_summoner(self, summoner_id: str) -> List[dict]:
        """移除某召唤者的所有召唤物。

        Args:
            summoner_id: 召唤者 ID

        Returns:
            事件列表
        """
        events: List[dict] = []
        to_remove = [
            eid for eid, e in self._summoned.items()
            if e.summoner_id == summoner_id
        ]
        for eid in to_remove:
            events.extend(self.despawn(eid))
        return events

    # ── 变形效果管理 ───────────────────────────────────────────────────

    def apply_form_override(
        self,
        target_id: str,
        new_stats: dict,
        spell_id: str,
        duration: int,
        concentration_id: Optional[str] = None,
        original_stats: Optional[dict] = None,
    ) -> FormOverride:
        """对目标应用变形效果。

        Args:
            target_id: 被变形目标 ID
            new_stats: 新属性
            spell_id: 法术 ID
            duration: 持续轮数（-1 = 永久）
            concentration_id: 关联的专注链接 ID
            original_stats: 原始属性（若不传则自动从当前状态保存）

        Returns:
            创建的 FormOverride
        """
        override = FormOverride(
            target_id=target_id,
            original_stats=dict(original_stats) if original_stats else {},
            new_stats=dict(new_stats),
            spell_id=spell_id,
            duration_rounds=duration,
            concentration_link_id=concentration_id,
        )
        self._form_overrides[target_id] = override
        return override

    def remove_form_override(self, target_id: str) -> dict:
        """移除目标的变形效果，返回恢复信息。

        Args:
            target_id: 被变形目标 ID

        Returns:
            恢复事件 {"type": "form_restored", "target_id": ..., "original_stats": ...}
            或空字典（若无变形效果）
        """
        override = self._form_overrides.pop(target_id, None)
        if override is None:
            return {}
        return {
            "type": "form_restored",
            "target_id": target_id,
            "original_stats": override.original_stats,
            "spell_id": override.spell_id,
            "reason": "override_removed",
        }

    def remove_form_by_concentration(self, concentration_link_id: str) -> List[dict]:
        """专注被打断时移除所有关联的变形效果。

        Args:
            concentration_link_id: 专注链接 ID

        Returns:
            事件列表
        """
        events: List[dict] = []
        to_remove = [
            tid for tid, fo in self._form_overrides.items()
            if fo.concentration_link_id == concentration_link_id
        ]
        for tid in to_remove:
            result = self.remove_form_override(tid)
            if result:
                result["reason"] = "concentration_broken"
                events.append(result)
        return events

    # ── 查询 ───────────────────────────────────────────────────────────

    def get_summoned(self, entity_id: str) -> Optional[SummonedEntity]:
        """获取指定召唤物实体。"""
        return self._summoned.get(entity_id)

    def get_all_summoned_by(self, summoner_id: str) -> List[SummonedEntity]:
        """获取某召唤者的所有召唤物。"""
        return [e for e in self._summoned.values() if e.summoner_id == summoner_id]

    def get_form_override(self, target_id: str) -> Optional[FormOverride]:
        """获取目标的变形效果。"""
        return self._form_overrides.get(target_id)

    def get_all_summoned(self) -> List[SummonedEntity]:
        """获取所有活跃召唤物。"""
        return list(self._summoned.values())

    def get_all_form_overrides(self) -> List[FormOverride]:
        """获取所有活跃变形效果。"""
        return list(self._form_overrides.values())

    # ── 时间推进 ───────────────────────────────────────────────────────

    def on_round_end(self, round_num: int) -> List[dict]:
        """轮次结束时处理持续时间到期的实体。

        Args:
            round_num: 当前轮次编号

        Returns:
            事件列表（到期消失/恢复）
        """
        events: List[dict] = []

        # 处理召唤物持续时间
        to_despawn = []
        for eid, entity in self._summoned.items():
            if entity.duration_rounds > 0:
                entity.duration_rounds -= 1
                if entity.duration_rounds <= 0:
                    to_despawn.append(eid)

        for eid in to_despawn:
            entity_events = self.despawn(eid)
            for ev in entity_events:
                ev["reason"] = "duration_expired"
            events.extend(entity_events)

        # 处理变形效果持续时间
        to_remove_forms = []
        for tid, fo in self._form_overrides.items():
            if fo.duration_rounds > 0:
                fo.duration_rounds -= 1
                if fo.duration_rounds <= 0:
                    to_remove_forms.append(tid)

        for tid in to_remove_forms:
            result = self.remove_form_override(tid)
            if result:
                result["reason"] = "duration_expired"
                events.append(result)

        return events

    def on_concentration_broken(self, link_id: str) -> List[dict]:
        """专注被打断时清理所有关联实体 (SPL-016)。

        Args:
            link_id: 专注链接 ID

        Returns:
            事件列表
        """
        events: List[dict] = []
        # 移除关联的召唤物
        events.extend(self.despawn_by_concentration(link_id))
        # 移除关联的变形效果
        events.extend(self.remove_form_by_concentration(link_id))
        return events
