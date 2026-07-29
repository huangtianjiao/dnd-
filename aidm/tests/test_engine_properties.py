"""Hypothesis 属性测试 — engine/ 核心数值函数。

验证 engine 模块中基础数值函数的不变量（invariants），
覆盖属性调整值、伤害掷骰、HP 结算等关键路径。
"""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from aidm.engine.damage import (
    DAMAGE_TYPES,
    DamageRequest,
    apply_damage_pipeline,
    apply_damage_to_hp,
    roll_damage,
)
from aidm.engine.dice import ability_modifier

# ──────────────────────────────────────────────────────────────────────────
# a) 属性调整值边界
# ──────────────────────────────────────────────────────────────────────────

@given(score=st.integers(min_value=1, max_value=30))
def test_ability_modifier_bounds(score: int) -> None:
    """对任意 1-30 的 ability score，modifier 在 [-5, +10] 范围内。"""
    mod = ability_modifier(score)
    assert -5 <= mod <= 10, f"ability_modifier({score}) = {mod} 超出 [-5, +10]"


# ──────────────────────────────────────────────────────────────────────────
# b) 伤害掷骰非负
# ──────────────────────────────────────────────────────────────────────────

# 合法骰子表达式列表（覆盖常见骰型）
_DICE_EXPRS = [
    "1d4", "1d6", "1d8", "1d10", "1d12", "2d6", "3d8", "4d6", "8d6",
    "1d4+1", "1d6+3", "1d8+5", "2d6+2",
]
_DAMAGE_TYPE_LIST = sorted(DAMAGE_TYPES)


@given(
    dice_expr=st.sampled_from(_DICE_EXPRS),
    damage_type=st.sampled_from(_DAMAGE_TYPE_LIST),
    ability_mod=st.integers(min_value=-5, max_value=10),
    flat_mod=st.integers(min_value=-10, max_value=10),
)
def test_roll_damage_non_negative(
    dice_expr: str,
    damage_type: str,
    ability_mod: int,
    flat_mod: int,
) -> None:
    """对任意骰子组合，最终伤害 >= 0（免疫时恰好为 0）。"""
    req = DamageRequest(
        dice_expr=dice_expr,
        damage_type=damage_type,
        ability_mod=ability_mod,
        add_mod=True,
        flat_modifiers=[flat_mod],
    )
    # 无免疫场景
    result = roll_damage(req)
    assert result.final >= 0, f"roll_damage({dice_expr}) final={result.final} < 0"

    # 免疫场景：final 必须恰好为 0
    result_immune = roll_damage(req, immunities={damage_type})
    assert result_immune.final == 0, (
        f"免疫时 final 应为 0，得到 {result_immune.final}"
    )


# ──────────────────────────────────────────────────────────────────────────
# c) HP 不超过上限
# ──────────────────────────────────────────────────────────────────────────

@given(
    max_hp=st.integers(min_value=1, max_value=500),
    current_hp=st.integers(min_value=0, max_value=500),
    temp_hp=st.integers(min_value=0, max_value=200),
    dmg=st.integers(min_value=0, max_value=1000),
)
def test_hp_never_exceeds_max(
    max_hp: int,
    current_hp: int,
    temp_hp: int,
    dmg: int,
) -> None:
    """apply_damage_to_hp 后 HP 不超过 max_hp（伤害不会让 HP 增加）。"""
    # 先钳制输入到合法范围
    hp = min(current_hp, max_hp)
    new_hp, new_temp_hp = apply_damage_to_hp(hp, temp_hp, max_hp, dmg)
    assert new_hp <= max_hp, (
        f"HP {new_hp} 超过 max_hp {max_hp}"
    )
    # 伤害不会增加 HP（只可能减少或不变）
    assert new_hp <= hp, f"HP 从 {hp} 增加到 {new_hp}，伤害不应增加 HP"


# ──────────────────────────────────────────────────────────────────────────
# d) HP 不为负数
# ──────────────────────────────────────────────────────────────────────────

@given(
    max_hp=st.integers(min_value=1, max_value=500),
    current_hp=st.integers(min_value=0, max_value=500),
    temp_hp=st.integers(min_value=0, max_value=200),
    dmg=st.integers(min_value=0, max_value=1000),
)
def test_hp_never_negative(
    max_hp: int,
    current_hp: int,
    temp_hp: int,
    dmg: int,
) -> None:
    """apply_damage_to_hp 后 HP >= 0。"""
    hp = min(current_hp, max_hp)
    new_hp, _ = apply_damage_to_hp(hp, temp_hp, max_hp, dmg)
    assert new_hp >= 0, f"HP {new_hp} 为负数"


# ──────────────────────────────────────────────────────────────────────────
# 补充：apply_damage_pipeline 最终伤害非负
# ──────────────────────────────────────────────────────────────────────────

@given(
    raw=st.integers(min_value=0, max_value=200),
    damage_type=st.sampled_from(_DAMAGE_TYPE_LIST),
    flat_mod=st.lists(st.integers(min_value=-20, max_value=20), max_size=5),
)
def test_damage_pipeline_non_negative(
    raw: int,
    damage_type: str,
    flat_mod: list[int],
) -> None:
    """apply_damage_pipeline 最终伤害 >= 0（下限为 0）。"""
    result = apply_damage_pipeline(raw, damage_type, flat_mod)
    assert result.final >= 0, (
        f"pipeline final={result.final} < 0 (raw={raw}, flat={flat_mod})"
    )
