"""召唤、变形和创造物实体生命周期 — EntityLifecycleExt。

SPL-016: 召唤、变形和创造物缺少实体生命周期。
实现EntitySpawned、FormOverride、ControlLink、DespawnAtEnd；绑定来源和持续时间。

规则依据: topics/玩家手册2024/法术详述/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SummonedEntity:
    """被召唤的临时实体。

    SPL-016: 绑定来源和持续时间。
    """

    entity_id: str = ""                    # 临时实体 ID
    summoner_id: str = ""                  # 召唤者 ID
    spell_id: str = ""                     # 来源法术 ID
    stat_block: dict = field(default_factory=dict)  # 属性块
    duration_rounds: int = -1              # 持续轮数（-1=永久）
    concentration_link_id: str = ""        # 专注链接 ID
    control_link: str = ""                 # 控制权链接
    current_hp: int = 0                    # 当前 HP
    max_hp: int = 0                        # 最大 HP
    initiative: int = 0                    # 先攻
    active: bool = True                    # 是否存活


@dataclass
class FormOverride:
    """变形覆盖 — 替换目标属性块。

    SPL-016: 变形法术替换属性块。
    """

    target_id: str = ""                    # 目标实体 ID
    spell_id: str = ""                     # 来源法术 ID
    new_stats: dict = field(default_factory=dict)  # 新属性块
    original_stats: dict = field(default_factory=dict)  # 原属性备份
    duration_rounds: int = -1              # 持续轮数
    concentration_link_id: str = ""        # 专注链接 ID
    active: bool = True


@dataclass
class EntityLifecycleManager:
    """实体生命周期管理器。

    SPL-016: 管理召唤、变形和创造物的完整生命周期。
    """

    _summons: Dict[str, SummonedEntity] = field(default_factory=dict)
    _overrides: Dict[str, FormOverride] = field(default_factory=dict)

    def summon(
        self,
        summoner_id: str,
        spell_id: str,
        stat_block: dict,
        duration: int = -1,
        concentration_id: str = "",
    ) -> SummonedEntity:
        """召唤一个临时实体。"""
        import uuid
        entity = SummonedEntity(
            entity_id=str(uuid.uuid4()),
            summoner_id=summoner_id,
            spell_id=spell_id,
            stat_block=stat_block,
            duration_rounds=duration,
            concentration_link_id=concentration_id,
            control_link=summoner_id,
            current_hp=stat_block.get("hp", 1),
            max_hp=stat_block.get("hp", 1),
            initiative=stat_block.get("initiative", 0),
        )
        self._summons[entity.entity_id] = entity
        return entity

    def despawn(self, entity_id: str) -> bool:
        """驱散一个召唤物。"""
        entity = self._summons.get(entity_id)
        if entity is None:
            return False
        entity.active = False
        del self._summons[entity_id]
        return True

    def despawn_by_concentration(self, concentration_link_id: str) -> List[str]:
        """按专注链接驱散所有关联召唤物。"""
        despawned: List[str] = []
        to_remove: List[str] = []

        for eid, entity in self._summons.items():
            if entity.concentration_link_id == concentration_link_id:
                entity.active = False
                to_remove.append(eid)
                despawned.append(eid)

        for eid in to_remove:
            del self._summons[eid]

        return despawned

    def apply_form_override(
        self,
        target_id: str,
        new_stats: dict,
        spell_id: str = "",
        duration: int = -1,
        concentration_id: str = "",
        original_stats: dict | None = None,
    ) -> FormOverride:
        """施加变形覆盖。"""
        override = FormOverride(
            target_id=target_id,
            spell_id=spell_id,
            new_stats=new_stats,
            original_stats=original_stats or {},
            duration_rounds=duration,
            concentration_link_id=concentration_id,
        )
        self._overrides[target_id] = override
        return override

    def remove_form_override(self, target_id: str) -> bool:
        """移除变形覆盖，恢复原属性。"""
        if target_id not in self._overrides:
            return False
        self._overrides[target_id].active = False
        del self._overrides[target_id]
        return True

    def get_active_summons(self, summoner_id: str = "") -> List[SummonedEntity]:
        """获取活跃的召唤物列表。"""
        result = [e for e in self._summons.values() if e.active]
        if summoner_id:
            result = [e for e in result if e.summoner_id == summoner_id]
        return result

    def tick_durations(self) -> List[str]:
        """推进所有临时实体的持续时间，返回过期的实体ID列表。"""
        expired: List[str] = []

        for eid, entity in list(self._summons.items()):
            if entity.duration_rounds > 0:
                entity.duration_rounds -= 1
                if entity.duration_rounds <= 0:
                    entity.active = False
                    expired.append(eid)
                    del self._summons[eid]

        for tid, override in list(self._overrides.items()):
            if override.duration_rounds > 0:
                override.duration_rounds -= 1
                if override.duration_rounds <= 0:
                    override.active = False
                    expired.append(tid)
                    del self._overrides[tid]

        return expired
