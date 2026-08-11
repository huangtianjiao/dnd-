"""多攻击序列管理 — AttackSequence / AttackPlan / AttackResult。

设计原则：
  - AttackPlan 封装单次攻击的完整上下文（9 步派生）。
  - AttackSequence 管理一回合内的多次子攻击（Extra Attack、Cleave、Nick 等）。
  - 与 engine/mastery.py 的精通效应联动。

规则依据: COM-007 多攻击序列
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from . import dice, check


# ──────────────────────────────────────────────────────────────────────────
# 数据类
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class AttackPlan:
    """单次攻击的完整计划。"""

    attacker_id: str
    target_id: str
    weapon_id: str = ""
    weapon_name: str = ""
    ability_used: str = "str"           # str / dex
    attack_modifier: int = 0            # 总命中修正
    proficiency_applied: bool = False
    has_advantage: bool = False
    has_disadvantage: bool = False
    target_ac: int = 10
    damage_dice: str = "1d6"
    damage_modifier: int = 0
    damage_type: str = "slashing"
    crit_dice: str = ""                 # 暴击额外骰
    is_ranged: bool = False
    range_ft: float = 0
    cover_level: str = "none"
    visibility: str = "visible"


@dataclass
class AttackResult:
    """单次攻击结果。"""

    attack_index: int
    attack_roll: int = 0
    total_attack: int = 0
    is_hit: bool = False
    is_crit: bool = False
    is_fumble: bool = False
    damage_total: int = 0
    damage_type: str = ""
    events: List[dict] = field(default_factory=list)


@dataclass
class AttackSequence:
    """多攻击序列管理。

    追踪一回合内的剩余攻击次数、装填状态、轻型额外攻击、
    Nick 转换、以及每回合特性使用次数。
    """

    sequence_id: str = ""
    attacker_id: str = ""
    remaining_attacks: int = 1
    loading_used: bool = False
    light_weapon_bonus_available: bool = False
    nick_conversion_used: bool = False
    per_turn_feature_usage: Dict[str, int] = field(default_factory=dict)
    results: List[AttackResult] = field(default_factory=list)

    # ── 构建攻击计划 ──────────────────────────────────────────────────

    def build_attack_plan(
        self,
        attacker: Dict[str, Any],
        target: Dict[str, Any],
        weapon: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AttackPlan:
        """构建单次攻击计划 — 9 步派生。

        9 步:
          1. 确定攻击者 / 目标 ID
          2. 确定武器信息
          3. 确定使用的属性（finesse 可选 str/dex，默认 str）
          4. 计算属性调整值
          5. 加上熟练加值（若熟练）
          6. 应用优劣势（可见性 / 武器属性 / 外部效应）
          7. 确定目标 AC
          8. 确定伤害骰与伤害类型
          9. 附加射程 / 掩护 / 可见性信息
        """
        ctx = context or {}

        # Step 1: ID
        attacker_id = attacker.get("id", "")
        target_id = target.get("id", "")

        # Step 2: 武器
        weapon_id = weapon.get("id", "")
        weapon_name = weapon.get("name", "")

        # Step 3: 属性
        ability_used = weapon.get("ability", "str")

        # Step 4: 属性调整值
        ability_score = attacker.get("abilities", {}).get(ability_used, 10)
        ability_mod = dice.ability_modifier(ability_score)

        # Step 5: 熟练加值
        proficiency_applied = weapon.get("proficient", False)
        prof_bonus = attacker.get("proficiency_bonus", 0)
        total_modifier = ability_mod
        if proficiency_applied:
            total_modifier += prof_bonus

        # Step 6: 优劣势
        has_advantage = ctx.get("advantage", False)
        has_disadvantage = ctx.get("disadvantage", False)

        # Step 7: 目标 AC
        target_ac = target.get("ac", 10)

        # Step 8: 伤害骰
        damage_dice = weapon.get("damage_dice", "1d6")
        damage_type = weapon.get("damage_type", "slashing")
        damage_modifier = ability_mod  # 武器伤害加属性调整值

        # Step 9: 射程 / 掩护 / 可见性
        is_ranged = weapon.get("is_ranged", False)
        range_ft = ctx.get("distance_ft", 0)
        cover_level = ctx.get("cover_level", "none")
        visibility = ctx.get("visibility", "visible")

        return AttackPlan(
            attacker_id=attacker_id,
            target_id=target_id,
            weapon_id=weapon_id,
            weapon_name=weapon_name,
            ability_used=ability_used,
            attack_modifier=total_modifier,
            proficiency_applied=proficiency_applied,
            has_advantage=has_advantage,
            has_disadvantage=has_disadvantage,
            target_ac=target_ac,
            damage_dice=damage_dice,
            damage_modifier=damage_modifier,
            damage_type=damage_type,
            is_ranged=is_ranged,
            range_ft=range_ft,
            cover_level=cover_level,
            visibility=visibility,
        )

    # ── 执行子攻击 ────────────────────────────────────────────────────

    def execute_sub_attack(self, plan: AttackPlan, rng: Any = None) -> AttackResult:
        """执行一次子攻击。

        掷 d20 → 判定命中/重击/失手 → 掷伤害骰。
        返回 AttackResult。
        """
        idx = len(self.results)
        result = AttackResult(attack_index=idx, damage_type=plan.damage_type)

        # 攻击检定
        atk = check.attack_roll(
            bonus=plan.attack_modifier,
            ac=plan.target_ac,
            advantage=plan.has_advantage,
            disadvantage=plan.has_disadvantage,
        )
        result.attack_roll = atk.d20
        result.total_attack = atk.total
        result.is_hit = atk.hit
        result.is_crit = atk.crit
        result.is_fumble = (atk.d20 == 1)

        result.events.append({
            "type": "attack_roll",
            "d20": atk.d20,
            "total": atk.total,
            "hit": atk.hit,
            "crit": atk.crit,
            "mode": atk.mode,
        })

        # 伤害掷骰（命中时）
        if atk.hit:
            dmg_roll = dice.roll_dice(plan.damage_dice, crit=atk.crit)
            raw_damage = dmg_roll.total + plan.damage_modifier
            raw_damage = max(0, raw_damage)
            result.damage_total = raw_damage

            result.events.append({
                "type": "damage_roll",
                "dice": plan.damage_dice,
                "rolls": dmg_roll.dice_rolls,
                "modifier": plan.damage_modifier,
                "total": raw_damage,
                "crit": atk.crit,
            })

        self.results.append(result)
        return result

    # ── 序列控制 ──────────────────────────────────────────────────────

    def can_continue(self) -> bool:
        """是否还有攻击机会。"""
        return self.remaining_attacks > 0

    def use_attack_opportunity(self) -> None:
        """消耗一次攻击机会。"""
        if self.remaining_attacks > 0:
            self.remaining_attacks -= 1

    def reset_turn(self, base_attacks: int = 1) -> None:
        """回合重置。"""
        self.remaining_attacks = base_attacks
        self.loading_used = False
        self.nick_conversion_used = False
        self.results.clear()

    def record_feature_usage(self, feature_name: str, max_per_turn: int = 1) -> bool:
        """记录特性使用，返回是否允许使用。

        若本回合已使用次数 ≥ max_per_turn 则拒绝。
        """
        current = self.per_turn_feature_usage.get(feature_name, 0)
        if current >= max_per_turn:
            return False
        self.per_turn_feature_usage[feature_name] = current + 1
        return True
