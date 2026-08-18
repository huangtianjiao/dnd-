"""HealthService — 生命状态机统一入口（方案 §9.4）。

状态流:
  ALIVE →(hp≤0)→ UNCONSCIOUS_DYING ↕(death saves / damage / healing)
  UNCONSCIOUS_DYING →(稳定成功)→ STABLE ↕(damage / healing)
  STABLE / UNCONSCIOUS_DYING →(伤害)→ DEAD
  ALIVE：临时HP优先吸收伤害；治疗只作用于 hp_current。

规则依据:
  PHB2024 第九章 死亡与倒下（0 HP / 死亡豁免 / 稳定 / 瞬死 / HP上限减少）
  改造方案 §9.4 HealthService —— damage、temporary HP、0 HP、death saves、
  stabilization、healing、instant death、max HP reduction 统一进入本服务；
  调用方不得直接 hp -= damage 绕过状态机。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol


class HealthState(StrEnum):
    ALIVE = "ALIVE"
    UNCONSCIOUS_DYING = "UNCONSCIOUS_DYING"
    STABLE = "STABLE"
    DEAD = "DEAD"


@dataclass
class HealthEvent:
    """一次生命状态变更的完整记录（供 ResolutionTrace/叙事复用）。"""

    state: HealthState
    hp_delta: int = 0
    temp_hp_delta: int = 0
    death_successes: int = 0
    death_failures: int = 0
    notes: list[str] = field(default_factory=list)


class HealthTarget(Protocol):
    """HealthService 操作的最小协议（Character ORM 天然满足）。"""

    hp_current: int
    hp_max: int
    temp_hp: int
    death_successes: int
    death_failures: int
    stable: bool
    dead: bool


class HealthService:
    """生命状态机 — 所有伤害/治疗/生命状态变更的唯一入口。"""

    def __init__(self) -> None:
        pass

    def state_of(self, t: HealthTarget) -> HealthState:
        if t.dead:
            return HealthState.DEAD
        if t.hp_current <= 0 and not t.stable:
            return HealthState.UNCONSCIOUS_DYING
        if t.hp_current <= 0 and t.stable:
            return HealthState.STABLE
        return HealthState.ALIVE

    def apply_damage(self, t: HealthTarget, amount: int) -> HealthEvent:
        """应用伤害（临时HP优先吸收；0 HP 进入濒死状态机）。

        规则: 瞬死——单次伤害 ≥ 最大HP 时直接死亡。
        """
        if t.dead:
            raise ValueError("已死亡目标不能再次受到伤害")
        amount = max(0, int(amount))
        event = HealthEvent(state=self.state_of(t))
        rest = amount
        # 临时HP吸收
        if t.temp_hp > 0:
            absorbed = min(t.temp_hp, rest)
            t.temp_hp -= absorbed
            rest -= absorbed
            event.temp_hp_delta = -absorbed
            if rest == 0:
                return event
        # 瞬死：伤害使 HP 降至 0 后，剩余伤害 ≥ 最大 HP
        # （PHB2024: 剩余伤害 ≥ 生命值上限 → 立即死亡）
        if rest > t.hp_current and (rest - t.hp_current) >= t.hp_max:
            t.hp_current = 0
            t.dead = True
            t.stable = False
            event.state = HealthState.DEAD
            event.hp_delta = -min(t.hp_max, rest)
            event.notes.append("instant_death")
            return event
        t.hp_current = max(0, t.hp_current - rest)
        event.hp_delta = -rest
        if t.hp_current <= 0:
            # 进入 dying：死亡豁免失败 +1（倒下瞬间自动失败1次，2024）
            t.death_failures += 1
            event.death_failures = t.death_failures
            event.state = HealthState.UNCONSCIOUS_DYING
        return event

    def apply_healing(self, t: HealthTarget, amount: int) -> HealthEvent:
        """治疗：恢复 hp_current（不超过 max）；从昏迷恢复为 1 HP 时醒来。"""
        if t.dead:
            raise ValueError("已死亡目标不能被治疗")
        amount = max(0, int(amount))
        before = t.hp_current
        t.hp_current = min(t.hp_max, t.hp_current + amount)
        event = HealthEvent(state=self.state_of(t), hp_delta=t.hp_current - before)
        if t.hp_current > 0:
            # 醒来：清空死亡豁免计数与稳定标记
            t.death_successes = 0
            t.death_failures = 0
            t.stable = False
            event.death_successes = 0
            event.death_failures = 0
        return event

    def apply_temp_hp(self, t: HealthTarget, amount: int) -> HealthEvent:
        """临时HP：覆盖式（新临时HP不低于旧值时替换）。"""
        amount = max(0, int(amount))
        event = HealthEvent(state=self.state_of(t))
        if amount >= t.temp_hp:
            event.temp_hp_delta = amount - t.temp_hp
            t.temp_hp = amount
        return event

    def add_death_save(self, t: HealthTarget, success: bool) -> HealthEvent:
        """死亡豁免计数：3 成功 → 稳定；3 失败 → 死亡。"""
        if t.hp_current > 0 or t.dead:
            raise ValueError("死亡豁免只在濒死/0HP 状态可计")
        if success:
            t.death_successes += 1
            if t.death_successes >= 3:
                t.stable = True
        else:
            t.death_failures += 1
            if t.death_failures >= 3:
                t.dead = True
        return HealthEvent(
            state=self.state_of(t),
            death_successes=t.death_successes,
            death_failures=t.death_failures,
        )

    def stabilize(self, t: HealthTarget) -> HealthEvent:
        """稳定（他人救助或 20 面成功）：HP 0、稳定标记、豁免计数保留。"""
        t.stable = True
        return HealthEvent(state=HealthState.STABLE,
                           death_successes=t.death_successes,
                           death_failures=t.death_failures)


def apply_character_damage(ch, amount: int) -> HealthEvent:
    """便捷入口：直接对 Character ORM 应用伤害（combat/法术调用的唯一路径）。"""
    return HealthService().apply_damage(ch, amount)


def apply_character_healing(ch, amount: int) -> HealthEvent:
    return HealthService().apply_healing(ch, amount)
