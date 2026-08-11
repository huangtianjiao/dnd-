"""多射线与多目标分配 — MultiRaySpellResolver。

SPL-006: 多射线与多目标分配未实现。
每枚射线/飞弹独立target_id、攻击/伤害事件；玩家可把三道射线分给三个目标。

规则依据: topics/玩家手册2024/法术详述/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RayResult:
    """单枚射线的结算结果。"""

    ray_index: int = 0               # 射线序号（从0开始）
    target_id: str = ""              # 目标实体 ID
    attack_roll: int = 0             # 攻击检定 d20
    attack_total: int = 0            # 攻击总计
    hit: bool = False                # 是否命中
    crit: bool = False               # 是否重击
    damage: int = 0                  # 伤害值
    damage_type: str = ""            # 伤害类型
    resisted: bool = False           # 是否抗性减伤
    vulnerable: bool = False         # 是否易伤增伤
    immune: bool = False             # 是否免疫


@dataclass
class MultiRaySpellResult:
    """多射线法术的完整结算结果。

    SPL-006: 每枚射线独立 target_id、攻击/伤害事件。
    """

    spell_name: str = ""
    total_rays: int = 0              # 总射线数
    rays: List[RayResult] = field(default_factory=list)

    def add_ray(self, ray: RayResult) -> None:
        """添加一枚射线的结算结果。"""
        self.rays.append(ray)

    def get_rays_for_target(self, target_id: str) -> List[RayResult]:
        """获取指定目标承受的所有射线。"""
        return [r for r in self.rays if r.target_id == target_id]

    def get_total_damage_for_target(self, target_id: str) -> int:
        """获取指定目标承受的总伤害。"""
        return sum(r.damage for r in self.get_rays_for_target(target_id))

    def to_dict(self) -> dict:
        """序列化为字典。"""
        return {
            "spell_name": self.spell_name,
            "total_rays": self.total_rays,
            "rays": [
                {
                    "index": r.ray_index,
                    "target_id": r.target_id,
                    "attack_roll": r.attack_roll,
                    "attack_total": r.attack_total,
                    "hit": r.hit,
                    "crit": r.crit,
                    "damage": r.damage,
                    "damage_type": r.damage_type,
                    "resisted": r.resisted,
                    "vulnerable": r.vulnerable,
                    "immune": r.immune,
                }
                for r in self.rays
            ],
        }


def resolve_multi_ray_spell(
    spell_name: str,
    num_rays: int,
    target_assignments: List[str],
    target_acs: Dict[str, int],
    damage_per_ray: int,
    damage_type: str = "force",
) -> MultiRaySpellResult:
    """结算多射线法术。

    SPL-006: 玩家可把三道射线分给三个目标。

    Args:
        spell_name: 法术名称
        num_rays: 射线数量
        target_assignments: 每枚射线分配的目标ID列表
        target_acs: 目标ID → AC 的映射
        damage_per_ray: 每枚射线的伤害值
        damage_type: 伤害类型
    """
    result = MultiRaySpellResult(
        spell_name=spell_name,
        total_rays=num_rays,
    )

    for i in range(num_rays):
        target_id = target_assignments[i] if i < len(target_assignments) else (
            target_assignments[-1] if target_assignments else "unknown"
        )
        ac = target_acs.get(target_id, 10)

        from ..engine.dice import roll_d20
        atk = roll_d20()
        total = atk.used
        hit = atk.used >= ac
        crit = atk.used == 20

        dmg = damage_per_ray if (hit or crit) else 0
        if crit:
            dmg *= 2  # 暴击翻倍

        result.add_ray(RayResult(
            ray_index=i,
            target_id=target_id,
            attack_roll=atk.used,
            attack_total=total,
            hit=hit,
            crit=crit,
            damage=dmg,
            damage_type=damage_type,
        ))

    return result
