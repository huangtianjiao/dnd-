"""resolvers.attack — 攻击检定 + 伤害计算 + 多次攻击 + 借机攻击。

从 brain/graph.py 提取。包含:
  - resolve_attack: 单次近战/远程武器攻击（含武器回退/拥有性门控/熟练度/条件优劣势/力竭惩罚）
  - resolve_multi_attack: 攻击动作内多次攻击分配（额外攻击 Extra Attack）
  - resolve_opportunity_attack: 借机攻击（复用 attack 逻辑）
"""

from __future__ import annotations

import logging

from ...data import equipment
from ...data.classes import get_extra_attacks
from ...engine import check, conditions, damage
from ...engine.weapon_rules import WeaponRuleContext, WeaponRuleHandler
from ..utils import target_condition_state

_log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────
# COM-001: AC 权威来源解析
# ──────────────────────────────────────────────────────────────────────

def _lookup_target_ac(ch, it, state) -> int:
    """COM-001: 从 EntityState 读取目标 AC，不可被 LLM 覆盖。

    查找顺序:
      1. 战斗中的目标 Character 卡 (target_cid → Character.ac)
      2. 怪物数据表 (target_name → Monster.ac)
      3. 兆底 10 (PHB 无甲 AC)
    """
    # 1) 从战斗状态查目标角色卡
    target_cid = it.get("target_cid") or ""
    camp = (state or {}).get("campaign_id")
    if target_cid and camp:
        try:
            from ...stats import store as _store
            # 尝试作为角色卡 ID
            try:
                target_ch = _store.get_character(int(target_cid))
                if target_ch:
                    return target_ch.ac
            except (ValueError, TypeError):
                pass
            # 尝试从战斗参战者关联的怪物查 AC
            combat = _store.load_combat(camp)
            if combat and combat.active:
                for c in list(combat.participants) + list(combat.initiative_order):
                    if c.cid == target_cid and not c.is_player:
                        # 从怪物数据表查 AC
                        try:
                            from ...data import monsters as _mon
                            m = _mon.get_monster(c.name)
                            if m:
                                return m.ac
                        except Exception:
                            pass
        except Exception as e:
            _log.debug("COM-001 AC 查找失败 cid=%s: %s", target_cid, e)
    # 2) 按目标名称查怪物数据表
    tname = it.get("target_name") or ""
    if tname:
        try:
            from ...data import monsters as _mon
            m = _mon.get_monster(tname)
            if m:
                return m.ac
        except Exception:
            pass
    # 3) 兆底: 无甲 AC=10
    return 10


# ──────────────────────────────────────────────────────────────────────
# COM-002: 武器属性 → 允许属性集合
# ──────────────────────────────────────────────────────────────────────

def _resolve_attack_ability(wname: str, it: dict) -> str:
    """COM-002: 根据武器类型确定允许使用的属性。

    规则:
      - 近战武器默认用力量(STR)
      - 有灵巧(Finesse)属性的武器可以用力量或敏捷（攻击者选择，但攻击和伤害必须用同一属性）
      - 远程武器默认用敏捷(DEX)
      - 有投掷(Thrown)属性的近战武器投掷时用力量
    如果 intent 指定了不允许的属性，返回错误信息。
    """
    intent_ability = (it.get("ability") or "").strip().lower()
    weapon_entry = equipment.WEAPONS.get(wname)
    if weapon_entry is None:
        # 徒手或未知武器 → 力量
        return "str"
    props = weapon_entry.get("props", [])
    cat = weapon_entry.get("cat", "")
    is_ranged = "远程" in cat
    has_finesse = "灵巧" in props
    has_thrown = "投掷" in props

    if is_ranged:
        # 远程武器默认敏捷
        allowed = {"dex"}
        # 远程武器带灵巧（如飞镖）可以用力量或敏捷
        if has_finesse:
            allowed = {"str", "dex"}
        default = "dex"
    elif has_thrown and not has_finesse:
        # 投掷近战武器（无灵巧）→ 力量
        allowed = {"str"}
        default = "str"
    elif has_finesse:
        # 灵巧近战武器 → 力量或敏捷
        allowed = {"str", "dex"}
        default = "str"
    else:
        # 普通近战武器 → 力量
        allowed = {"str"}
        default = "str"

    if intent_ability and intent_ability not in allowed:
        _log.warning("COM-002: 武器 %r 不允许属性 %r，回退为 %r", wname, intent_ability, default)
        return default
    return intent_ability or default


def resolve_attack(ch, it, state=None) -> dict:
    """攻击检定 + 伤害掷骰。R-CMB-017/022/023, R-DMG-001/CMB-029, R-GLS-044~058

    ★ COM-003: 武器属性 handler 在 BuildAttackPlan 阶段统一校验并产生修正/资源事件。
    """
    # —— 武器确定（掷骰前，熟练度影响命中加值）——
    wname = it.get("weapon") or getattr(ch, "equipped_weapon", "") or "徒手"
    weapon_substituted = None
    _owned = set(getattr(ch, "inventory", []) or []) | {getattr(ch, "equipped_weapon", ""), "徒手"}
    if wname not in _owned:
        weapon_substituted = wname
        wname = getattr(ch, "equipped_weapon", "") or "徒手"

    # COM-002: 根据武器属性确定允许使用的属性
    ability = _resolve_attack_ability(wname, it)

    # 武器熟练门控（R-ITM-013）：不熟练武器攻击检定不加熟练加值
    proficient = equipment.class_weapon_proficient(ch.char_class, wname)
    bonus = ch.ability_mod(ability) + (ch.prof() if proficient else 0)
    # COM-001: AC 只能从 EntityState 读取，忽略 intent 中的 target_ac
    ac = _lookup_target_ac(ch, it, state)

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

    # ★ COM-003: 武器属性 handler 统一校验
    weapon_entry = equipment.WEAPONS.get(wname)
    if weapon_entry:
        props = weapon_entry.get("props", [])
        ctx = WeaponRuleContext(
            attacker_str=ch.ability_score("str"),
            attacker_dex=ch.ability_score("dex"),
            target_distance_ft=float(distance),
            attacker_size="Medium",
        )
        rule_result = WeaponRuleHandler().validate_attack(props, ctx)
        if not rule_result.allowed:
            return {"kind": "attack", "error": "; ".join(rule_result.errors),
                    "weapon": wname}
        if rule_result.has_disadvantage:
            dis = True

    atk = check.attack_roll(bonus=bonus, ac=ac, advantage=adv, disadvantage=dis,
                            circ=exh_penalty)             # R-CMB-017/022/023
    out = {"kind": "attack", "attack_total": atk.total, "d20": atk.d20,
           "hit": atk.hit, "crit": atk.crit, "rolls": atk.rolls, "target_ac": ac,
           "bonus": bonus, "weapon": wname}
    # ★ OBS-001: 透传修正来源解释（d20 + 属性 + 熟练 - 力竭 + 掩护 完整轨迹）
    if getattr(atk, "modifier_breakdown", None):
        out["resolution_trace"] = _build_resolution_trace(
            "attack", wname, atk.d20, atk.modifier_breakdown, atk.total, ac)
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
        # ★ COM-004: 武器精通真实结算（engine.mastery 权威实现）
        mastery_effect = _resolve_weapon_mastery(wname, ch, it, atk)
        if mastery_effect:
            out["mastery"] = mastery_effect
    return out


def _build_resolution_trace(action: str, label: str, d20: int,
                            breakdown: list, total: int, target: int) -> dict:
    """OBS-001: 用 engine.resolution_trace / resolution_trace_ext 构建完整轨迹。"""
    try:
        from ...engine.resolution_trace import (
            ModifierSource,
            ResolutionTrace,
            RollTrace,
        )
        from ...engine.resolution_trace_ext import FormulaNode
        trace = ResolutionTrace(
            trace_id=f"{action}_{label}_{d20}",
            action_type=action,
            actor_id=label,
            final_result={"total": total, "target": target,
                          "success": total >= target},
        )
        roll = RollTrace(
            dice_expr=f"d20+{sum(m.get('value', 0) for m in breakdown)}",
            dice_rolls=[d20],
            modifiers=[
                ModifierSource(
                    source_type="circumstance",
                    source_name=m.get("source", ""),
                    value=m.get("value", 0),
                ) for m in breakdown
            ],
            total=total,
        )
        trace.add_roll(roll)
        root = FormulaNode(node_type="result", label=action, value=total)
        root.children.append(FormulaNode(node_type="roll", label="d20", value=d20))
        for m in breakdown:
            root.children.append(FormulaNode(
                node_type="modifier", label=m.get("source", ""),
                value=m.get("value", 0)))
        root.children.append(FormulaNode(
            node_type="total", label="vs target", value=target))
        return {
            "action": action,
            "d20": d20,
            "modifiers": list(breakdown),
            "total": total,
            "target": target,
            "display": trace.to_display_string(),
            "formula_tree": _formula_node_to_dict(root),
        }
    except Exception:
        return {
            "action": action,
            "d20": d20,
            "modifiers": [{"source": m.get("source", ""), "value": m.get("value", 0)}
                          for m in breakdown],
            "total": total,
            "target": target,
        }


def _formula_node_to_dict(node) -> dict:
    """递归序列化 FormulaNode。"""
    return {
        "node_type": getattr(node, "node_type", ""),
        "label": getattr(node, "label", ""),
        "value": getattr(node, "value", 0),
        "children": [_formula_node_to_dict(c) for c in getattr(node, "children", [])],
    }


def _resolve_weapon_mastery(wname: str, ch, it, atk) -> dict | None:
    """COM-004: 武器精通结算（engine.mastery）。

    从武器数据表读取精通词条（如"推离"/"失衡"），命中后调用
    engine.mastery.resolve_mastery_with_grant 权威结算特效。
    """
    try:
        from ...engine.mastery import (
            MASTERY_NAME_MAP,
            MasteryGrant,
            resolve_mastery_with_grant,
        )
        entry = equipment.WEAPONS.get(wname)
        if not entry:
            return None
        mastery_cn = entry.get("mastery")
        if not mastery_cn or mastery_cn not in MASTERY_NAME_MAP:
            return None
        grant = MasteryGrant(
            entity_id=str(getattr(ch, "id", "unknown")),
            granted_masteries=[mastery_cn],
        )
        if not grant.can_use(mastery_cn):
            return None
        effect = resolve_mastery_with_grant(
            mastery_cn,
            grant,
            hit=bool(atk.hit),
            attacker_ability_mod=ch.ability_mod(
                it.get("ability") or "str"),
            attacker_prof=ch.prof(),
            target_size=it.get("target_size", "medium"),
            target_con_mod=int(it.get("target_con_mod", 0)),
            target_con_prof=bool(it.get("target_con_prof", False)),
            target_prof=int(it.get("target_prof", 0)),
        )
        grant.record_use(mastery_cn)
        return {
            "mastery": mastery_cn,
            "applied": effect.applied,
            "effect_type": effect.effect_type,
            "push_distance_ft": effect.push_distance_ft,
            "target_prone": effect.target_prone,
            "speed_reduction_ft": effect.speed_reduction_ft,
            "graze_damage": effect.graze_damage,
            "extra_attack_available": effect.extra_attack_available,
            "nick_active": effect.nick_active,
        }
    except Exception as e:
        _log.debug("武器精通结算失败 %s: %s", wname, e)
        return None


def resolve_opportunity_attack(ch, it, state=None) -> dict:
    """借机攻击：目标离开触及范围时触发的反应近战攻击。R-CMB-024

    本质是一次近战武器攻击，复用 resolve_attack 逻辑（已含力竭惩罚/条件优劣势），
    仅改 kind 以便 narrate/apply 区分。

    ★ R-CMB-025: 触发条件由 engine.opportunity_attack 权威判定
      （反应可用/离开触及/可见/移动类型），engine.triggers 提供触发注册表。
    """
    # 触发条件预设（intent 侧标记；战斗内离开触及判定见 combat_flow）
    try:
        from ...engine.opportunity_attack import can_make_opportunity_attack
        from ...engine.triggers import KNOWN_REACTION_TRIGGERS
        _trigger = KNOWN_REACTION_TRIGGERS.get("借机攻击")
        _allowed = can_make_opportunity_attack(
            attacker=_combatant_from_character(ch),
            target=_combatant_from_intent(it),
            target_leaving_reach=bool(it.get("target_leaving_reach", True)),
            target_visible=not bool(it.get("target_hidden", False)),
            movement_type=it.get("movement_type", "normal"),
        )
        if not _allowed:
            return {"kind": "opportunity_attack",
                    "error": "借机攻击条件不满足（目标未离开触及/不可见/已撤离，或已无反应）"}
    except Exception:
        pass
    out = resolve_attack(ch, it, state=state)
    out["kind"] = "opportunity_attack"
    return out


def _combatant_from_character(ch) -> "object":
    """将 Character 转换为 combat.Combatant 形状（供 opportunity_attack 判定）。"""
    from ...engine import combat as _cmb
    return _cmb.Combatant(
        cid=str(getattr(ch, "id", "unknown")),
        name=getattr(ch, "name", ""),
        dex_mod=int(getattr(ch, "ability_mod", lambda a: 0)("dex") or 0),
        side="player",
        is_player=True,
        speed=int(getattr(ch, "speed", 30) or 30),
        reach=5,
    )


def _combatant_from_intent(it: dict) -> "object":
    """从 intent 构建目标 Combatant（供 opportunity_attack 判定）。"""
    from ...engine import combat as _cmb
    return _cmb.Combatant(
        cid=it.get("target_cid", "target"),
        name=it.get("target_name", "目标"),
        side="enemy",
        is_player=False,
        speed=int(it.get("target_speed", 30) or 30),
        reach=5,
    )


# ──────────────────────────────────────────────────────────────────────
# 多次攻击分配（Extra Attack）
# ──────────────────────────────────────────────────────────────────────

def resolve_multi_attack(ch, it, state=None) -> dict:
    """攻击动作内多次攻击分配（额外攻击 Extra Attack）。

    规则: 玩家手册2024/角色职业/各职业「额外攻击」特性（战士5/11/20级、2/3/4次；
          野蛮人/武僧/圣武士/游侠5级、2次）
    出处: topics/玩家手册2024/角色职业/战士.htm ; 野蛮人.htm ; 武僧.htm ; 圣武士.htm ; 游侠.htm
    说明:
      - 攻击动作内攻击次数 = 1 + 额外攻击次数。
      - 每次攻击可选不同目标（通过 it["targets"] 列表指定，否则全部攻击同一目标）。
      - 向后兼容：num_attacks=1 时输出结构与旧版一致（保留顶层 hit/damage/d20 等字段）。
      - 多次攻击时输出 attacks[] 数组 + total_damage 汇总，及顶层兼容字段。

    ★ COM-008: 多目标伤害独立事件
      每次命中产生独立的伤害事件，不汇总到单一目标。
      每次攻击独立掷骰、独立计算伤害、独立应用抗性/易伤/免疫。
      即使多个攻击命中同一目标，每次命中的伤害也是独立事件，
      上层应分别为每个命中产生独立的 DamageApplied 事件。
    """
    extra = get_extra_attacks(ch.char_class, ch.level)
    num_attacks = 1 + extra

    # 目标列表：支持指定每次攻击的不同目标（可选）
    targets = it.get("targets") or []  # [{"target_ac":X, ...}, ...]

    attacks: list[dict] = []
    for i in range(num_attacks):
        # ★ COM-008: 每次攻击独立处理，产生独立的伤害事件
        # 每次攻击独立掷骰（命中/伤害）、独立应用目标抗性/易伤/免疫
        # 即使多攻击命中同一目标，每次命中的伤害也是独立事件
        if targets and i < len(targets):
            attack_it = {**it, **targets[i]}
        else:
            attack_it = it
        single = resolve_attack(ch, attack_it, state=state)
        # 标记攻击序号，供上层为每次命中生成独立的 DamageApplied 事件
        single["attack_index"] = i
        attacks.append(single)

    total_damage = sum(a.get("damage", 0) for a in attacks)
    total_hits = sum(1 for a in attacks if a.get("hit"))

    # 向后兼容：单次攻击时保持旧输出格式（顶层有 hit/damage/d20 等）
    if num_attacks == 1:
        out = attacks[0]
        out["num_attacks"] = 1
        return out

    # 多次攻击：新格式
    first = attacks[0]  # 顶层兼容字段取第一次攻击的参数
    out = {
        "kind": "attack",
        "num_attacks": num_attacks,
        "attacks": attacks,
        "total_damage": total_damage,
        "total_hits": total_hits,
        # 顶层兼容字段（供旧版 narrate/apply 不报错）
        "hit": total_hits > 0,
        "damage": total_damage,
        "d20": first.get("d20"),
        "attack_total": first.get("attack_total"),
        "crit": any(a.get("crit") for a in attacks),
        "rolls": first.get("rolls"),
        "target_ac": first.get("target_ac"),
        "bonus": first.get("bonus"),
        "weapon": first.get("weapon"),
    }
    if first.get("weapon_substituted"):
        out["weapon_substituted"] = first["weapon_substituted"]
    if first.get("weapon_not_proficient"):
        out["weapon_not_proficient"] = True
    # 伤害类型取第一次命中的
    for a in attacks:
        if a.get("hit"):
            out["damage_type"] = a.get("damage_type")
            out["damage_rolls"] = a.get("damage_rolls")
            break
    return out
