"""生命值状态机 — 0HP / 非致命 / 死亡豁免完整状态管理。

设计原则：
  - HealthStateMachine 封装实体从满血到死亡的全部状态转换。
  - 与 engine.damage 的底层函数互补：本模块管理"状态"，damage 模块提供"计算"。
  - 所有状态转换产生事件列表，供调用方记日志 / 推送 UI。

规则依据: DMG-002 生命值状态机
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from . import dice
from .damage import (
    apply_damage_to_hp,
    apply_healing,
    check_massive_damage,
    damage_at_zero_hp as _damage_at_zero,
    DeathTracker,
    grant_temp_hp,
    reset_death_counts_on_recovery,
)


# ──────────────────────────────────────────────────────────────────────────
# 枚举与子状态
# ──────────────────────────────────────────────────────────────────────────

class KnockoutState(str, Enum):
    """击倒/意识状态。"""

    CONSCIOUS = "conscious"           # 有意识
    UNCONSCIOUS = "unconscious"       # 昏迷（0HP，未稳定）
    STABILIZED = "stabilized"         # 已稳定（0HP，死亡豁免 3 成功）
    DEAD = "dead"                     # 死亡


@dataclass
class DeathSaveState:
    """死亡豁免进度。"""

    successes: int = 0
    failures: int = 0

    def is_stable(self) -> bool:
        """是否已稳定（3 次成功）。"""
        return self.successes >= 3

    def is_dead(self) -> bool:
        """是否已死亡（3 次失败）。"""
        return self.failures >= 3

    def reset(self) -> None:
        """重置计数。"""
        self.successes = 0
        self.failures = 0


# ──────────────────────────────────────────────────────────────────────────
# 状态机主体
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class HealthStateMachine:
    """0HP / 非致命 / 死亡完整状态机。

    规则:
      - R-DMG-007 HP 扣除
      - R-DMG-009 临时 HP 优先扣除
      - R-DMG-013 HP 上限归 0 则死
      - R-DMG-014 巨量伤害即刻毙命
      - R-DMG-017 死亡豁免检定
      - R-DMG-018 0HP 时受伤害
      - R-DMG-020 治疗重置死亡豁免
      - 2024 PHB knockout 规则（可选 1HP 规则）
    """

    entity_id: str
    hp_current: int = 0
    hp_max: int = 0
    temp_hp: int = 0
    knockout_state: KnockoutState = KnockoutState.CONSCIOUS
    death_saves: DeathSaveState = field(default_factory=DeathSaveState)
    is_nonlethal: bool = False
    events: List[dict] = field(default_factory=list)

    # ── 伤害应用 ──────────────────────────────────────────────────────

    def on_damage_applied(self, damage: int, is_crit: bool = False) -> List[dict]:
        """伤害应用后的状态检查。

        流程:
          1. 检查巨量伤害 (massive damage) → 即刻死亡
          2. 扣 HP（先扣临时 HP）
          3. 若到 0HP：knockout 或 unconscious + death tracking
          4. 重击 = 2 failures（若已在 0HP）

        Returns:
            事件列表
        """
        events: List[dict] = []

        if self.knockout_state == KnockoutState.DEAD:
            events.append({"type": "already_dead", "entity": self.entity_id})
            return events

        # Step 1: 巨量伤害检查（R-DMG-014）
        if check_massive_damage(self.hp_current, self.hp_max, damage):
            self.knockout_state = KnockoutState.DEAD
            self.hp_current = 0
            events.append({
                "type": "massive_damage_death",
                "entity": self.entity_id,
                "damage": damage,
                "hp_max": self.hp_max,
            })
            return events

        # Step 2: 扣 HP
        old_hp = self.hp_current
        self.hp_current, self.temp_hp = apply_damage_to_hp(
            self.hp_current, self.temp_hp, self.hp_max, damage
        )
        actual_damage = old_hp - self.hp_current + (damage - (old_hp - self.hp_current + self.temp_hp))
        events.append({
            "type": "hp_changed",
            "entity": self.entity_id,
            "old_hp": old_hp,
            "new_hp": self.hp_current,
            "temp_hp": self.temp_hp,
            "damage_taken": damage,
        })

        # Step 3: 到 0HP？
        if self.hp_current <= 0:
            # 非致命伤害模式
            if self.is_nonlethal:
                self.knockout_state = KnockoutState.UNCONSCIOUS
                events.append({
                    "type": "nonlethal_knockout",
                    "entity": self.entity_id,
                })
                return events

            # 已在 0HP 时再受伤害
            if old_hp <= 0:
                zero_events = self.on_damage_at_zero(damage, is_crit)
                events.extend(zero_events)
            else:
                # 刚降到 0HP：进入 unconscious + 开始死亡豁免
                self.knockout_state = KnockoutState.UNCONSCIOUS
                events.append({
                    "type": "dropped_to_zero",
                    "entity": self.entity_id,
                    "is_crit": is_crit,
                })
                # 重击命中 = 2 failures（R-DMG-017）
                if is_crit:
                    self.death_saves.failures += 2
                    events.append({
                        "type": "crit_death_save_failure",
                        "entity": self.entity_id,
                        "failures_added": 2,
                        "failures": self.death_saves.failures,
                    })
                    if self.death_saves.failures >= 3:
                        self.knockout_state = KnockoutState.DEAD
                        events.append({
                            "type": "death_by_crit_failures",
                            "entity": self.entity_id,
                        })

        return events

    # ── 治疗 ──────────────────────────────────────────────────────────

    def on_healing(self, amount: int) -> List[dict]:
        """治疗：重置死亡豁免、结束 unconscious。

        Returns:
            事件列表
        """
        events: List[dict] = []

        if self.knockout_state == KnockoutState.DEAD:
            events.append({"type": "cannot_heal_dead", "entity": self.entity_id})
            return events

        old_hp = self.hp_current
        self.hp_current = apply_healing(self.hp_current, self.hp_max, amount)
        healed = self.hp_current - old_hp

        events.append({
            "type": "healed",
            "entity": self.entity_id,
            "old_hp": old_hp,
            "new_hp": self.hp_current,
            "healed_amount": healed,
        })

        # 恢复到 >0HP：重置死亡豁免、结束昏迷（R-DMG-020）
        if self.hp_current > 0 and self.knockout_state in (
            KnockoutState.UNCONSCIOUS,
            KnockoutState.STABILIZED,
        ):
            reset_death_counts_on_recovery(DeathTracker())  # 仅做规则参考
            self.death_saves.reset()
            self.knockout_state = KnockoutState.CONSCIOUS
            events.append({
                "type": "regained_consciousness",
                "entity": self.entity_id,
                "death_saves_reset": True,
            })

        return events

    # ── 回合开始：死亡豁免 ────────────────────────────────────────────

    def at_turn_start(self, rng: Any = None) -> List[dict]:
        """回合开始：死亡豁免检定。

        仅当 knockout_state == UNCONSCIOUS 时触发。

        Returns:
            事件列表
        """
        events: List[dict] = []

        if self.knockout_state != KnockoutState.UNCONSCIOUS:
            return events

        # 掷死亡豁免（R-DMG-017）
        roll = dice.roll_die(20)
        events.append({
            "type": "death_save_roll",
            "entity": self.entity_id,
            "roll": roll,
        })

        if roll == 1:
            # 天然 1 = 两次失败
            self.death_saves.failures += 2
            events.append({
                "type": "death_save_natural_1",
                "entity": self.entity_id,
                "failures_added": 2,
                "failures": self.death_saves.failures,
            })
        elif roll == 20:
            # 天然 20 = 恢复 1HP，计数归零
            self.hp_current = 1
            self.death_saves.reset()
            self.knockout_state = KnockoutState.CONSCIOUS
            events.append({
                "type": "death_save_natural_20",
                "entity": self.entity_id,
                "hp_restored": 1,
            })
            return events
        elif roll + 0 >= 10:  # 无 modifier 简化
            self.death_saves.successes += 1
            events.append({
                "type": "death_save_success",
                "entity": self.entity_id,
                "successes": self.death_saves.successes,
            })
        else:
            self.death_saves.failures += 1
            events.append({
                "type": "death_save_failure",
                "entity": self.entity_id,
                "failures": self.death_saves.failures,
            })

        # 检查终止条件
        if self.death_saves.successes >= 3:
            self.knockout_state = KnockoutState.STABILIZED
            self.death_saves.reset()
            events.append({
                "type": "stabilized",
                "entity": self.entity_id,
            })
        elif self.death_saves.failures >= 3:
            self.knockout_state = KnockoutState.DEAD
            events.append({
                "type": "dead_by_failures",
                "entity": self.entity_id,
            })

        return events

    # ── 0HP 时受伤害 ──────────────────────────────────────────────────

    def on_damage_at_zero(self, damage: int, is_crit: bool = False) -> List[dict]:
        """0HP 时受伤害：增加死亡豁免失败次数。

        规则: R-DMG-018 生命值 0 时受伤害
        Returns:
            事件列表
        """
        events: List[dict] = []

        if self.knockout_state == KnockoutState.DEAD:
            return events

        # 伤害 ≥ HP 上限 → 即刻死亡（R-DMG-018）
        if damage >= self.hp_max:
            self.knockout_state = KnockoutState.DEAD
            events.append({
                "type": "death_by_damage_at_zero",
                "entity": self.entity_id,
                "damage": damage,
                "hp_max": self.hp_max,
            })
            return events

        # 重击 = 2 failures，普通 = 1 failure（R-DMG-018）
        added = 2 if is_crit else 1
        self.death_saves.failures += added

        events.append({
            "type": "damage_at_zero_hp",
            "entity": self.entity_id,
            "damage": damage,
            "is_crit": is_crit,
            "failures_added": added,
            "failures": self.death_saves.failures,
        })

        if self.death_saves.failures >= 3:
            self.knockout_state = KnockoutState.DEAD
            events.append({
                "type": "dead_by_accumulated_failures",
                "entity": self.entity_id,
            })

        return events

    # ── 稳定 ──────────────────────────────────────────────────────────

    def stabilize(self) -> List[dict]:
        """稳定：结束死亡豁免，进入 STABILIZED 状态。

        Returns:
            事件列表
        """
        events: List[dict] = []

        if self.knockout_state != KnockoutState.UNCONSCIOUS:
            events.append({
                "type": "cannot_stabilize",
                "entity": self.entity_id,
                "reason": "not_unconscious",
            })
            return events

        self.knockout_state = KnockoutState.STABILIZED
        self.death_saves.reset()
        events.append({
            "type": "stabilized",
            "entity": self.entity_id,
        })
        return events

    # ── 2024 Knockout 选择 ────────────────────────────────────────────

    def choose_knockout(self, use_1hp_rule: bool = True) -> dict:
        """2024 knockout 规则选择。

        当角色降至 0HP 时，玩家可选择：
          - 使用 "1HP 规则"（若可用）：保留 1HP，但倒地
          - 进入 unconscious + prone + 开始死亡豁免

        Args:
            use_1hp_rule: 是否选择 1HP 规则（仅当 hp_current 刚降至 0 时可用）

        Returns:
            选择结果 dict
        """
        if self.hp_current > 0:
            return {"choice": "none", "reason": "hp_above_zero"}

        if use_1hp_rule and self.hp_max > 0:
            # 1HP 规则：保留 1HP，倒地
            self.hp_current = 1
            self.knockout_state = KnockoutState.CONSCIOUS
            return {
                "choice": "one_hp_rule",
                "hp_current": 1,
                "condition": "prone",
            }

        # 进入 unconscious
        self.knockout_state = KnockoutState.UNCONSCIOUS
        return {
            "choice": "unconscious",
            "condition": "unconscious_prone",
            "death_saves_active": True,
        }

    # ── 临时 HP ───────────────────────────────────────────────────────

    def grant_temp_hp(self, amount: int) -> List[dict]:
        """获得临时 HP（不叠加，取较大者）。

        Returns:
            事件列表
        """
        events: List[dict] = []
        old_temp = self.temp_hp
        self.temp_hp = grant_temp_hp(self.temp_hp, amount)

        events.append({
            "type": "temp_hp_granted",
            "entity": self.entity_id,
            "old_temp": old_temp,
            "new_temp": self.temp_hp,
            "amount": amount,
        })
        return events
