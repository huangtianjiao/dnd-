"""resolvers.attack — 攻击检定 + 伤害计算 + 借机攻击。

从 brain/graph.py 提取。包含:
  - resolve_attack: 近战/远程武器攻击（含武器回退/拥有性门控/熟练度/条件优劣势/力竭惩罚）
  - resolve_opportunity_attack: 借机攻击（复用 attack 逻辑）
"""

from __future__ import annotations

from ...data import equipment
from ...engine import check, conditions, damage
from ..utils import target_condition_state


def resolve_attack(ch, it) -> dict:
    """攻击检定 + 伤害掷骰。R-CMB-017/022/023, R-DMG-001/CMB-029, R-GLS-044~058"""
    ability = it.get("ability") or "str"
    # —— 武器确定（掷骰前，熟练度影响命中加值）——
    # 武器三级回退：玩家明说 → 角色卡 equipped_weapon → 徒手(1+力量)
    # 详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段A4/B1
    wname = it.get("weapon") or getattr(ch, "equipped_weapon", "") or "徒手"
    weapon_substituted = None
    # 拥有性门控：未拥有的武器不可用，降级为已装备武器/徒手（R-ITM-012）；
    # 拥有集 = inventory ∪ 当前装备（历史角色 inventory 可能未含起始武器）
    _owned = set(getattr(ch, "inventory", []) or []) | {getattr(ch, "equipped_weapon", ""), "徒手"}
    if wname not in _owned:
        weapon_substituted = wname   # 叙述层据此说明换成了实际武器
        wname = getattr(ch, "equipped_weapon", "") or "徒手"
    # 武器熟练门控（R-ITM-013）：不熟练武器攻击检定不加熟练加值
    proficient = equipment.class_weapon_proficient(ch.char_class, wname)
    bonus = ch.ability_mod(ability) + (ch.prof() if proficient else 0)
    ac = int(it.get("target_ac") or 10)

    # R-GLS-044~058 条件优劣势：从角色卡读攻击者状态 + 从 intent 读目标状态
    atk_state = ch.to_condition_state()
    tgt_state = target_condition_state(it)
    distance = int(it.get("distance_ft") or 5)
    mods = conditions.attack_modifiers(atk_state, tgt_state, distance)
    adv = bool(it.get("advantage")) or mods.attacker_advantage
    dis = bool(it.get("disadvantage")) or mods.attacker_disadvantage
    # R-CMB-008 目标回避 → 攻击劣势
    if it.get("target_dodging"):
        dis = True

    # R-GLS-047 力竭 d20 惩罚（等级×2，作为负的临时加值传入）
    exh_penalty = -conditions.d20_penalty(atk_state)

    atk = check.attack_roll(bonus=bonus, ac=ac, advantage=adv, disadvantage=dis,
                            circ=exh_penalty)             # R-CMB-017/022/023
    out = {"kind": "attack", "attack_total": atk.total, "d20": atk.d20,
           "hit": atk.hit, "crit": atk.crit, "rolls": atk.rolls, "target_ac": ac,
           "bonus": bonus, "weapon": wname}
    if weapon_substituted:
        out["weapon_substituted"] = weapon_substituted
    if not proficient:
        out["weapon_not_proficient"] = True   # 叙述层可提及持用生疏
    if atk.hit:
        dice_expr, dmg_type = equipment.resolve_weapon_damage(wname)
        # R-GLS-052/058 麻痹/昏迷5尺内近战命中即重击
        crit = atk.crit or mods.target_auto_crit_if_hit
        dr = damage.roll_damage(damage.DamageRequest(  # R-DMG-001 + R-CMB-029
            dice_expr=dice_expr, damage_type=dmg_type,
            ability_mod=ch.ability_mod(ability), add_mod=True, crit=crit),
            resistances=it.get("resistances", []),
            vulnerabilities=it.get("vulnerabilities", []),
            immunities=it.get("immunities", []))
        out.update({"damage": dr.final, "damage_type": dmg_type,
                    "damage_rolls": dr.dice_rolls,
                    "resisted": dr.resisted, "vulnerable": dr.vulnerable, "immune": dr.immune})
    return out


def resolve_opportunity_attack(ch, it) -> dict:
    """借机攻击：目标离开触及范围时触发的反应近战攻击。R-CMB-024

    本质是一次近战武器攻击，复用 resolve_attack 逻辑（已含力竭惩罚/条件优劣势），
    仅改 kind 以便 narrate/apply 区分。
    """
    out = resolve_attack(ch, it)
    out["kind"] = "opportunity_attack"
    return out
