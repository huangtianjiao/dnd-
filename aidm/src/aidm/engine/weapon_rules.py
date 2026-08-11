"""武器属性规则 — 10 种武器属性的判定 Handler。

设计原则：
  - 每种武器属性（ammunition, finesse, heavy, light, loading, range,
    reach, thrown, two_handed, versatile）各有一个 handler。
  - validate_attack 综合验证所有属性。

规则依据: COM-003 武器属性 Handler
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class WeaponRuleContext:
    """武器规则判定的上下文。"""

    attacker_str: int = 10
    attacker_dex: int = 10
    target_distance_ft: float = 0.0
    is_bonus_action: bool = False
    attacker_size: str = "Medium"
    weapon_str_required: int = 0       # Heavy 武器的力量门槛


@dataclass
class WeaponRuleResult:
    """武器规则判定结果。"""

    allowed: bool = True
    ability_used: str = ""             # "str" / "dex"
    attack_modifier: int = 0
    damage_modifier: int = 0
    has_disadvantage: bool = False
    has_advantage: bool = False
    ammo_consumed: bool = False
    errors: List[str] = None

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


def _str_mod(ctx: WeaponRuleContext) -> int:
    return (ctx.attacker_str - 10) // 2


def _dex_mod(ctx: WeaponRuleContext) -> int:
    return (ctx.attacker_dex - 10) // 2


class WeaponRuleHandler:
    """10 种武器属性 handler。"""

    # ── 1. 弹药 ───────────────────────────────────────────────────────

    def ammunition(self, ctx: WeaponRuleContext, ammo_count: int) -> WeaponRuleResult:
        """弹药：验证弹药存在、每次攻击消耗、战后回收。"""
        result = WeaponRuleResult()
        if ammo_count <= 0:
            result.allowed = False
            result.errors.append("无可用弹药")
        else:
            result.ammo_consumed = True
        return result

    # ── 2. 灵巧 ───────────────────────────────────────────────────────

    def finesse(
        self, ctx: WeaponRuleContext, chosen_ability: str = ""
    ) -> WeaponRuleResult:
        """灵巧：允许 STR 或 DEX，攻击和伤害必须使用同一属性。"""
        result = WeaponRuleResult()
        if chosen_ability not in ("str", "dex", ""):
            result.allowed = False
            result.errors.append(f"灵巧武器只能选择 str 或 dex，收到: {chosen_ability!r}")
            return result

        ability = chosen_ability or "dex"
        result.ability_used = ability
        mod = _str_mod(ctx) if ability == "str" else _dex_mod(ctx)
        result.attack_modifier = mod
        result.damage_modifier = mod
        return result

    # ── 3. 重型 ───────────────────────────────────────────────────────

    def heavy(self, ctx: WeaponRuleContext) -> WeaponRuleResult:
        """重型：按 2024 属性门槛给攻击劣势。

        若攻击者的力量低于武器门槛，攻击具有劣势。
        小型生物自动获得劣势。
        """
        result = WeaponRuleResult()
        if ctx.attacker_size == "Small":
            result.has_disadvantage = True
            result.errors.append("小型生物使用重型武器具有劣势")
        elif ctx.weapon_str_required > 0 and ctx.attacker_str < ctx.weapon_str_required:
            result.has_disadvantage = True
            result.errors.append(
                f"力量 {ctx.attacker_str} 低于门槛 {ctx.weapon_str_required}"
            )
        return result

    # ── 4. 轻型 ───────────────────────────────────────────────────────

    def light(self, ctx: WeaponRuleContext) -> WeaponRuleResult:
        """轻型：开放另一轻型武器额外攻击（双武器战斗）。

        轻型武器本身不限制攻击，但允许副手攻击。
        """
        result = WeaponRuleResult()
        # 轻型武器本身不添加限制，仅标记可用
        return result

    # ── 5. 装填 ───────────────────────────────────────────────────────

    def loading(
        self, ctx: WeaponRuleContext, used_this_action: bool = False
    ) -> WeaponRuleResult:
        """装填：该武器至多一发/动作。

        若本动作已使用过该武器，则不允许再次使用。
        """
        result = WeaponRuleResult()
        if used_this_action:
            result.allowed = False
            result.errors.append("装填武器每动作只能发射一发")
        return result

    # ── 6. 射程 ───────────────────────────────────────────────────────

    def range(
        self, ctx: WeaponRuleContext, normal_range: int, long_range: int
    ) -> WeaponRuleResult:
        """射程：常规正常、长程劣势、最大外非法。"""
        result = WeaponRuleResult()
        dist = ctx.target_distance_ft
        if dist > long_range:
            result.allowed = False
            result.errors.append(
                f"目标距离 {dist} 尺超出最大射程 {long_range} 尺"
            )
        elif dist > normal_range:
            result.has_disadvantage = True
            result.errors.append(
                f"目标距离 {dist} 尺超出常规射程 {normal_range} 尺，攻击劣势"
            )
        return result

    # ── 7. 触及 ───────────────────────────────────────────────────────

    def reach(self, ctx: WeaponRuleContext, base_reach: int = 5) -> WeaponRuleResult:
        """触及：武器提供 +5 触及距离。

        默认基础触及 5 尺，reach 属性武器增加 5 尺。
        """
        result = WeaponRuleResult()
        effective_reach = base_reach + 5
        if ctx.target_distance_ft > effective_reach:
            result.allowed = False
            result.errors.append(
                f"目标距离 {ctx.target_distance_ft} 尺超出触及范围 {effective_reach} 尺"
            )
        return result

    # ── 8. 投掷 ───────────────────────────────────────────────────────

    def thrown(self, ctx: WeaponRuleContext, is_melee: bool = True) -> WeaponRuleResult:
        """投掷：远程攻击但使用近战属性（STR）。

        若武器同时具有 finesse 属性，可选择 DEX。
        此处默认使用 STR。
        """
        result = WeaponRuleResult()
        result.ability_used = "str"
        mod = _str_mod(ctx)
        result.attack_modifier = mod
        result.damage_modifier = mod
        return result

    # ── 9. 双手 ───────────────────────────────────────────────────────

    def two_handed(self, ctx: WeaponRuleContext, hands_available: int = 2) -> WeaponRuleResult:
        """双手：攻击时必须两手。"""
        result = WeaponRuleResult()
        if hands_available < 2:
            result.allowed = False
            result.errors.append("双手武器需要两只手")
        return result

    # ── 10. 多用 ──────────────────────────────────────────────────────

    def versatile(self, ctx: WeaponRuleContext, mode: str = "one_handed") -> WeaponRuleResult:
        """多用：单手/双手选择影响伤害骰。

        one_handed: 单手使用，伤害骰较小
        two_handed: 双手使用，伤害骰较大
        """
        result = WeaponRuleResult()
        if mode not in ("one_handed", "two_handed"):
            result.allowed = False
            result.errors.append(f"多用武器模式必须为 one_handed 或 two_handed，收到: {mode!r}")
        return result

    # ── 综合验证 ──────────────────────────────────────────────────────

    # COM-003: 中文属性名→英文 key 映射
    _CN_TO_EN = {
        "弹药": "ammunition", "灵巧": "finesse", "重型": "heavy",
        "轻型": "light", "装填": "loading", "射程": "range",
        "触及": "reach", "投掷": "thrown", "双手": "two_handed",
        "多用": "versatile",
    }

    def validate_attack(
        self,
        weapon_properties: List[str],
        ctx: WeaponRuleContext,
        **kwargs: Any,
    ) -> WeaponRuleResult:
        """综合验证所有武器属性。

        COM-003: 支持中文和英文属性名。
        Args:
            weapon_properties: 武器属性列表，如 ["灵巧", "轻型"] 或 ["finesse", "light"]
            ctx: 判定上下文
            **kwargs: 传递给各 handler 的额外参数

        Returns:
            合并所有属性判定的 WeaponRuleResult
        """
        combined = WeaponRuleResult()

        for prop in weapon_properties:
            prop_lower = prop.lower().strip()
            # COM-003: 中文属性名翻译为英文 key
            en_key = self._CN_TO_EN.get(prop.strip(), prop_lower)
            if en_key == "ammunition":
                r = self.ammunition(ctx, kwargs.get("ammo_count", 1))
            elif en_key == "finesse":
                r = self.finesse(ctx, kwargs.get("chosen_ability", ""))
            elif en_key == "heavy":
                r = self.heavy(ctx)
            elif en_key == "light":
                r = self.light(ctx)
            elif en_key == "loading":
                r = self.loading(ctx, kwargs.get("used_this_action", False))
            elif en_key == "range":
                r = self.range(ctx, kwargs.get("normal_range", 80), kwargs.get("long_range", 320))
            elif en_key == "reach":
                r = self.reach(ctx, kwargs.get("base_reach", 5))
            elif en_key == "thrown":
                r = self.thrown(ctx, kwargs.get("is_melee", True))
            elif en_key == "two_handed":
                r = self.two_handed(ctx, kwargs.get("hands_available", 2))
            elif en_key == "versatile":
                r = self.versatile(ctx, kwargs.get("mode", "one_handed"))
            else:
                continue

            # 合并结果
            if not r.allowed:
                combined.allowed = False
            combined.has_disadvantage = combined.has_disadvantage or r.has_disadvantage
            combined.has_advantage = combined.has_advantage or r.has_advantage
            combined.ammo_consumed = combined.ammo_consumed or r.ammo_consumed
            combined.errors.extend(r.errors)
            if r.ability_used:
                combined.ability_used = r.ability_used
            combined.attack_modifier += r.attack_modifier
            combined.damage_modifier += r.damage_modifier

        # 若无属性设定 ability_used，默认使用 STR
        if not combined.ability_used:
            combined.ability_used = "str"
            combined.attack_modifier = _str_mod(ctx)
            combined.damage_modifier = _str_mod(ctx)

        return combined


# ── 武器属性数据映射 ──────────────────────────────────────────────────

WEAPON_PROPERTIES = {
    "ammunition": "弹药",
    "finesse": "灵巧",
    "heavy": "重型",
    "light": "轻型",
    "loading": "装填",
    "range": "射程",
    "reach": "触及",
    "thrown": "投掷",
    "two_handed": "双手",
    "versatile": "多用",
}
