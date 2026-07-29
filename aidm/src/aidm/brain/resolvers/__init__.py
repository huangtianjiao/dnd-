"""brain.resolvers — 从 graph.py 提取的确定性骰子分派与状态应用逻辑。

子模块:
  - attack: 攻击检定 + 借机攻击
  - cast: 施法检定
  - actions: 其余 resolve 函数 + 遭遇系统 + 时间推进
  - apply: apply_node + 伤害/治疗/怪物回合
"""

from .attack import resolve_attack, resolve_opportunity_attack
from .cast import resolve_cast
from .actions import (
    resolve_ability_check,
    resolve_hide,
    resolve_search,
    resolve_grapple,
    resolve_shove,
    resolve_study,
    resolve_rest,
    resolve_social,
    resolve_levelup,
    resolve_travel,
    resolve_start_combat,
    with_target_outcome,
    with_encounter,
    advance_game_time,
    apply_rest_to_character,
    apply_levelup_to_character,
)
from .apply import (
    apply_node,
    apply_damage_to_character,
    apply_healing_to_character,
    run_monster_turn,
    render_monster_events,
)

__all__ = [
    "resolve_attack", "resolve_opportunity_attack",
    "resolve_cast",
    "resolve_ability_check", "resolve_hide", "resolve_search",
    "resolve_grapple", "resolve_shove", "resolve_study",
    "resolve_rest", "resolve_social", "resolve_levelup", "resolve_travel",
    "resolve_start_combat",
    "with_target_outcome", "with_encounter", "advance_game_time",
    "apply_rest_to_character", "apply_levelup_to_character",
    "apply_node", "apply_damage_to_character", "apply_healing_to_character",
    "run_monster_turn", "render_monster_events",
]
