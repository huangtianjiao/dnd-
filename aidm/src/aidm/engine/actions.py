"""战斗动作分派器 — 攻击 / 疾走 / 撤离 / 回避 / 协助 / 躲藏 /
影响 / 魔法 / 预备 / 搜索 / 研究 / 操作。

依赖 engine.check（attack_roll, ability_check）、engine.damage（roll_damage）、
engine.combat（Combatant, use_action, conditions）。标注规则ID+出处。

规则出处:
  - topics/玩家手册2024/进行游戏/动作.htm
  - topics/玩家手册2024/进行游戏/攻击检定.htm
  - topics/玩家手册2024/进行游戏/重击.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from . import check, damage, conditions
from .combat import Combatant, use_action, use_bonus_action, use_reaction


# ──────────────────────────────────────────────────────────────────────────
# 动作结果
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class ActionResult:
    """一次战斗动作的结算结果。"""
    action_type: str                       # attack/dash/disengage/...
    success: bool = True                   # 动作是否成功执行
    message: str = ""                      # 叙事摘要
    attack_result: Optional[check.AttackResult] = None   # 攻击检定结果
    damage_result: Optional[damage.DamageResult] = None  # 伤害结算结果
    extra: dict[str, Any] = field(default_factory=dict)  # 动作特定附加数据


# ──────────────────────────────────────────────────────────────────────────
# 武器/攻击描述（轻量结构，供 actions 使用）
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class WeaponProfile:
    """武器攻击档案（简化版，完整武器数据见 data/equipment.py）。

    规则: R-CMB-018 攻击检定属性映射 / R-CMB-019 灵巧武器
          R-CMB-029 重击伤害骰翻倍（含附加伤害骰如偷袭/圣斩）
    """
    name: str                              # 武器名称
    attack_bonus: int = 0                  # 命中加值（含属性调整值+熟练加值）
    damage_dice: str = "1d6"               # 伤害骰表达式，如 "1d8"
    damage_type: str = "挥砍"              # 伤害类型（中文）
    ability_mod: int = 0                   # 伤害加的属性调整值
    add_ability_mod_to_damage: bool = True # 是否将属性调整值加到伤害
    crit: bool = False                     # 本次攻击是否为重击（由 attack 设置）
    extra_damage_dice: str = ""            # 附加伤害骰（如偷袭"1d6"/圣斩"2d8"），重击时也翻倍
    extra_damage_type: str = ""            # 附加伤害类型（如"暗蚀"/"光耀"）


# ──────────────────────────────────────────────────────────────────────────
# 各动作实现
# ──────────────────────────────────────────────────────────────────────────

def action_attack(attacker: Combatant, target: Combatant,
                  weapon: WeaponProfile,
                  advantage: bool = False, disadvantage: bool = False,
                  target_ac: int = 10, distance_ft: int = 5,
                  resistances: list[str] | None = None,
                  vulnerabilities: list[str] | None = None,
                  immunities: list[str] | None = None) -> ActionResult:
    """攻击动作：选择目标 → 攻击检定 → （命中则）掷伤害。

    规则: R-CMB-014 攻击流程 / R-CMB-017 命中判定 / R-CMB-022 天然20必出重击
          R-CMB-023 天然1必失手 / R-CMB-029 重击伤害骰翻倍
          R-GLS-044~058 条件优劣势 / R-CMB-008 回避 → 攻击劣势
    出处: topics/玩家手册2024/进行游戏/攻击检定.htm ; 重击.htm
    说明:
      - target_ac 由调用方提供（已计入掩护加值等，见 R-CMB-015）。
      - 重击时伤害骰数量翻倍（damage.roll_damage 的 crit 参数处理）。
      - 条件优劣势从攻守双方 ConditionState 计算（R-GLS-044~058）。
      - 目标回避(dodge_active)→攻击劣势；目标麻痹/昏迷5尺内命中即重击。
    """
    if not use_action(attacker):
        return ActionResult("attack", success=False,
                            message="无可用动作")

    # R-GLS-044~058: 条件优劣势
    mods = conditions.attack_modifiers(attacker.conditions, target.conditions, distance_ft)
    adv = advantage or mods.attacker_advantage
    dis = disadvantage or mods.attacker_disadvantage
    # R-CMB-008 目标回避 → 攻击劣势
    if target.dodge_active:
        dis = True
    # 力竭 d20 惩罚
    exh_penalty = -conditions.d20_penalty(attacker.conditions)

    # R-CMB-017/R-CMB-022/R-CMB-023: 攻击检定
    atk = check.attack_roll(bonus=weapon.attack_bonus, ac=target_ac,
                            advantage=adv, disadvantage=dis, circ=exh_penalty)

    result = ActionResult(
        "attack",
        success=True,
        message=f"{attacker.name} 攻击 {target.name}",
        attack_result=atk,
    )

    if not atk.hit:
        result.message += "：未命中"
        return result

    # R-CMB-029 + R-GLS-052/058: 重击（含麻痹/昏迷5尺内自动重击）
    crit = atk.crit or mods.target_auto_crit_if_hit
    req = damage.DamageRequest(
        dice_expr=weapon.damage_dice,
        damage_type=weapon.damage_type,
        ability_mod=weapon.ability_mod,
        add_mod=weapon.add_ability_mod_to_damage,
        crit=crit,
    )
    # 经伤害管线：抗性→数值修正→易伤→免疫（R-DMG-004~009）
    dmg = damage.roll_damage(req, resistances=resistances or [],
                             vulnerabilities=vulnerabilities or [],
                             immunities=immunities or [])

    # R-CMB-029: 附加伤害骰（偷袭/圣斩等）重击时也翻倍
    extra_total = 0
    if weapon.extra_damage_dice:
        extra_req = damage.DamageRequest(
            dice_expr=weapon.extra_damage_dice,
            damage_type=weapon.extra_damage_type or weapon.damage_type,
            ability_mod=0,
            add_mod=False,
            crit=crit,  # 重击翻倍附加骰
        )
        extra_dmg = damage.roll_damage(extra_req, resistances=resistances or [],
                                        vulnerabilities=vulnerabilities or [],
                                        immunities=immunities or [])
        extra_total = extra_dmg.final

    total_damage = dmg.final + extra_total
    result.damage_result = dmg
    if extra_total:
        result.extra["extra_damage"] = extra_total
        result.extra["extra_damage_type"] = weapon.extra_damage_type or weapon.damage_type
    result.message += (f"：命中{'（重击）' if crit else ''}，"
                       f"造成 {total_damage} 点伤害"
                       + (f"（含{extra_total}点{weapon.extra_damage_type or weapon.damage_type}）" if extra_total else ""))
    return result


def _is_light_weapon(weapon: WeaponProfile) -> bool:
    """判断武器是否具有"轻型"词条（按名称查 data.equipment 武器表）。

    规则: R-ITM-014 武器词条「轻型」  出处: 装备/词条.txt
    说明: 未知武器（不在武器表中）默认视为非轻型——规则要求副手须为轻型；
          调用方可用 off_hand_is_light 参数显式覆写以支持自定义轻型武器。
    """
    try:
        from ..data import equipment
        return "轻型" in equipment.get_weapon_entry(weapon.name)["props"]
    except KeyError:
        return False


def action_two_weapon_attack(attacker: Combatant, target: Combatant,
                             main_weapon: WeaponProfile, off_hand_weapon: WeaponProfile,
                             advantage: bool = False, disadvantage: bool = False,
                             target_ac: int = 10, distance_ft: int = 5,
                             off_advantage: bool = False, off_disadvantage: bool = False,
                             off_hand_is_light: Optional[bool] = None) -> ActionResult:
    """双武器战斗：用攻击动作以主手武器攻击，再以附赠动作用另一把轻型武器攻击。

    规则: R-ITM-014 武器词条「轻型」  出处: 装备/词条.txt
          当你在自己回合中执行攻击动作、并用一把轻型武器发动一次攻击后，
          可用附赠动作用另一把轻型武器再攻击一次；该次额外攻击的伤害
          不加入属性调整值（除非该调整值为负数）。
    说明:
      - 主手攻击消耗动作（复用 action_attack 的命中/重击/条件优劣势逻辑）。
      - 副手攻击消耗附赠动作；副手须为轻型武器（默认按名称查 data.equipment
        武器表，off_hand_is_light 可显式覆写以支持自定义武器）。
      - 副手伤害不加属性调整值（ability_mod < 0 时仍施加负值）。
      - 返回的 ActionResult.attack_result/damage_result 为主手结果；副手结果存于
        extra["off_hand"]，extra["bonus_action_used"] 标示是否消耗了附赠动作。
    """
    # 主手攻击：消耗动作（若无可用动作则整体失败）
    main_result = action_attack(attacker, target, main_weapon,
                                advantage=advantage, disadvantage=disadvantage,
                                target_ac=target_ac, distance_ft=distance_ft)
    if not main_result.success:
        return ActionResult("two_weapon_attack", success=False,
                            message=main_result.message or "无可用动作")

    # 副手须为轻型武器
    off_light = (off_hand_is_light if off_hand_is_light is not None
                 else _is_light_weapon(off_hand_weapon))
    if not off_light:
        return ActionResult("two_weapon_attack", success=True,
                            message=(main_result.message
                                     + f"；副手 {off_hand_weapon.name} 非轻型武器，未发动额外攻击"),
                            attack_result=main_result.attack_result,
                            damage_result=main_result.damage_result,
                            extra={"main": {"attack_result": main_result.attack_result,
                                            "damage_result": main_result.damage_result},
                                   "off_hand": {"attempted": False, "reason": "not_light"},
                                   "bonus_action_used": False})

    # 消耗附赠动作
    if not use_bonus_action(attacker):
        return ActionResult("two_weapon_attack", success=True,
                            message=(main_result.message + "；无可用附赠动作，未发动副手攻击"),
                            attack_result=main_result.attack_result,
                            damage_result=main_result.damage_result,
                            extra={"main": {"attack_result": main_result.attack_result,
                                            "damage_result": main_result.damage_result},
                                   "off_hand": {"attempted": False, "reason": "no_bonus_action"},
                                   "bonus_action_used": False})

    # 副手攻击检定（条件优劣势与主手一致：同攻击者/目标/距离）
    mods = conditions.attack_modifiers(attacker.conditions, target.conditions, distance_ft)
    off_adv = off_advantage or mods.attacker_advantage
    off_dis = off_disadvantage or mods.attacker_disadvantage
    if target.dodge_active:                          # R-CMB-008 目标回避 → 攻击劣势
        off_dis = True
    exh = -conditions.d20_penalty(attacker.conditions)   # 力竭 d20 惩罚
    off_atk = check.attack_roll(bonus=off_hand_weapon.attack_bonus, ac=target_ac,
                                advantage=off_adv, disadvantage=off_dis, circ=exh)

    off_hand: dict[str, Any] = {"attempted": True, "attack_result": off_atk,
                                "damage_result": None}
    message = main_result.message + f"；{attacker.name} 用 {off_hand_weapon.name} 发动副手攻击"

    if not off_atk.hit:
        message += "：未命中"
    else:
        # 副手伤害不加属性调整值（负数除外）— R-ITM-014「轻型」
        off_add_mod = off_hand_weapon.ability_mod < 0
        off_crit = off_atk.crit or mods.target_auto_crit_if_hit
        req = damage.DamageRequest(
            dice_expr=off_hand_weapon.damage_dice,
            damage_type=off_hand_weapon.damage_type,
            ability_mod=off_hand_weapon.ability_mod,
            add_mod=off_add_mod,
            crit=off_crit,
        )
        off_dmg = damage.roll_damage(req)
        off_hand["damage_result"] = off_dmg
        message += (f"：命中{'（重击）' if off_crit else ''}，"
                    f"造成 {off_dmg.final} 点{off_hand_weapon.damage_type}伤害")

    return ActionResult("two_weapon_attack", success=True, message=message,
                        attack_result=main_result.attack_result,
                        damage_result=main_result.damage_result,
                        extra={"main": {"attack_result": main_result.attack_result,
                                        "damage_result": main_result.damage_result},
                               "off_hand": off_hand,
                               "bonus_action_used": True})


def action_dash(attacker: Combatant) -> ActionResult:
    """疾走动作：给予自己等同于速度的额外移动力，持续至回合结束。

    规则: R-CMB-006 动作:疾走
          bonus_movement = speed; move_total_this_turn = speed + bonus_movement
    出处: topics/玩家手册2024/进行游戏/动作.htm
    """
    if not use_action(attacker):
        return ActionResult("dash", success=False, message="无可用动作")
    # 疾走给予额外等于速度的移动力
    attacker.speed_remaining += attacker.speed           # R-CMB-006
    return ActionResult("dash", success=True,
                        message=f"{attacker.name} 疾走，本回合移动力增至 {attacker.speed_remaining} 尺",
                        extra={"new_speed_remaining": attacker.speed_remaining})


def action_disengage(attacker: Combatant) -> ActionResult:
    """撤离动作：本回合余下时间的移动不引发借机攻击。

    规则: R-CMB-007 动作:撤离
          provokes_opportunity_attack = false (for this turn's movement)
    出处: topics/玩家手册2024/进行游戏/动作.htm
    """
    if not use_action(attacker):
        return ActionResult("disengage", success=False, message="无可用动作")
    attacker.disengage_active = True                     # R-CMB-007
    return ActionResult("disengage", success=True,
                        message=f"{attacker.name} 撤离，本回合移动不引发借机攻击")


def action_dodge(attacker: Combatant) -> ActionResult:
    """回避动作：直至下个回合开始，对你进行的攻击检定具有劣势，
    你进行的敏捷豁免检定具有优势；失能或速度0时失去增益。

    规则: R-CMB-008 动作:回避
          attacks_against_self = disadvantage; own_DEX_saves = advantage;
          duration = until start of next turn;
          lose_if incapacitated OR speed==0
    出处: topics/玩家手册2024/进行游戏/动作.htm
    """
    if not use_action(attacker):
        return ActionResult("dodge", success=False, message="无可用动作")
    attacker.dodge_active = True                         # R-CMB-008
    return ActionResult("dodge", success=True,
                        message=f"{attacker.name} 回避，对自身的攻击具有劣势")


def action_help(attacker: Combatant, ally: Combatant,
                target: Optional[Combatant] = None,
                mode: str = "attack",
                medicine_mod: int = 0, medicine_prof: int = 0,
                medicine_proficient: bool = False) -> ActionResult:
    """协助动作：盟友下次对该目标的攻击检定具有优势；或进行急救（医药检定DC10稳定伤势）。

    规则: 术语汇编/动作.txt「协助」— 两种模式：属性检定协助/攻击协助
    出处: topics/玩家手册2024/术语汇编/动作.htm
    说明: 攻击协助模式：在 ally 上标记 help_advantage_target，供攻击检定查询，
          下回合开始时清除。急救模式：进行 DC10 感知(医药)检定稳定伤势。
    """
    if not use_action(attacker):
        return ActionResult("help", success=False, message="无可用动作")
    if mode == "first_aid":
        # 急救：DC10 感知(医药)检定稳定伤势。
        # 用医疗者感知调整值 + 医药熟练加值（R-CHK-010），由调用方传入。
        exh = -conditions.d20_penalty(attacker.conditions)  # R-GLS-047 力竭惩罚
        r = check.ability_check(mod=medicine_mod, prof=medicine_prof,
                                proficient=medicine_proficient, dc=10, circ=exh)
        return ActionResult("help", success=r.success,
                            message=f"{attacker.name} 急救检定 {r.total} vs DC10："
                                    + ("成功，伤势稳定" if r.success else "失败"),
                            extra={"mode": "first_aid", "check_total": r.total,
                                   "dc": 10, "stabilized": r.success})
    # 攻击协助：标记 ally 下次对该 target 攻击有优势
    if target:
        ally.help_advantage_target = target.cid
    return ActionResult("help", success=True,
                        message=f"{attacker.name} 协助 {ally.name}"
                                + (f" 对抗 {target.name}" if target else ""),
                        extra={"ally": ally.cid,
                               "target": target.cid if target else None,
                               "mode": "attack"})


def action_hide(attacker: Combatant, stealth_mod: int, stealth_prof: int,
                proficient: bool, dc: int = 15,
                advantage: bool = False, disadvantage: bool = False,
                has_cover: bool = False, heavily_obscured: bool = False,
                not_in_enemy_sight: bool = True) -> ActionResult:
    """躲藏动作：进行一次敏捷（隐匿）检定（2024规则：固定DC15）。

    规则: 术语汇编/动作.txt「躲藏」(2024) — DC15 隐匿检定；
          需满足前置条件：重度遮蔽/3/4掩护/全身掩护/不在敌视野内。
          成功后检定总值成为他人察觉该生物的 DC。
    出处: topics/玩家手册2024/术语汇编/动作.htm
    说明: 2024 规则改为固定 DC15（非旧的被动察觉 DC）。
          成功则进入隐形状态（hidden=True），失败则未躲藏。
    """
    if not use_action(attacker):
        return ActionResult("hide", success=False, message="无可用动作")
    # 前置条件检查：需有遮蔽/掩护或不在敌视野内
    can_hide = has_cover or heavily_obscured or not_in_enemy_sight
    if not can_hide:
        return ActionResult("hide", success=False,
                            message=f"{attacker.name} 无法躲藏：需遮蔽或掩护",
                            extra={"hidden": False, "reason": "no_obscurement"})
    r = check.ability_check(mod=stealth_mod, prof=stealth_prof,
                            proficient=proficient, dc=dc,
                            advantage=advantage, disadvantage=disadvantage,
                            circ=-conditions.d20_penalty(attacker.conditions))  # R-GLS-047
    if r.success:
        attacker.hidden = True                           # 躲藏成功 → 隐形
    return ActionResult("hide", success=r.success,
                        message=f"{attacker.name} 躲藏检定 {r.total} vs DC{dc}："
                                + ("成功" if r.success else "失败"),
                        extra={"check_total": r.total, "dc": dc,
                               "hidden": attacker.hidden,
                               "detection_dc": r.total if r.success else None})


def action_magic(attacker: Combatant, spell_name: str = "",
                 spell_dc: int = 0) -> ActionResult:
    """魔法动作：施展一道法术、使用一个魔法物品或是使用一个魔法特性。

    规则: R-CMB-014 魔法 施展法术/使用魔法物品/魔法特性
    出处: topics/玩家手册2024/进行游戏/动作.htm
    说明: 法术的具体效果（伤害/豁免/状态）由施法模块（spell.py）结算；
          此函数仅消耗动作并返回占位结果，供上层调用真正的施法逻辑。
    """
    if not use_action(attacker):
        return ActionResult("magic", success=False, message="无可用动作")
    return ActionResult("magic", success=True,
                        message=f"{attacker.name} 施展法术" +
                                (f"：{spell_name}" if spell_name else ""),
                        extra={"spell": spell_name, "spell_dc": spell_dc})


def action_ready(attacker: Combatant, trigger_condition: str,
                 ready_action: str = "attack") -> ActionResult:
    """预备动作：设定触发条件，用反应在条件满足时执行该动作。

    规则: 术语汇编/动作.txt「预备」— 消耗动作设定触发条件，
          触发时用反应执行一个动作或移动等于速度的距离。
          预备法术：施法时间须为动作，预备时施展（耗资源）并维持专注，
          触发时用反应释放。
    出处: topics/玩家手册2024/术语汇编/动作.htm
    说明: 预备本身消耗动作；在 Combatant.ready_trigger 上记录触发条件，
          ready_action_name 上记录预备的动作/法术名。触发时消耗反应执行
          （由上层在反应阶段查询 ready_trigger 并调用 trigger_ready）。
    """
    if not use_action(attacker):
        return ActionResult("ready", success=False, message="无可用动作")
    attacker.ready_trigger = trigger_condition
    attacker.ready_action_name = ready_action
    return ActionResult("ready", success=True,
                        message=f"{attacker.name} 预备{ready_action}，"
                                f"触发条件：{trigger_condition}",
                        extra={"trigger": trigger_condition,
                               "ready_action": ready_action})


def trigger_ready(attacker: Combatant) -> Optional[ActionResult]:
    """触发预备动作：消耗反应执行预备的动作/移动。返回 None 表示无预备。

    规则: 术语汇编/动作.txt — 触发时用反应执行。
    说明: 清除 ready_trigger 和 ready_action_name，消耗反应。
    """
    if not attacker.ready_trigger:
        return None
    if not use_reaction(attacker):
        return ActionResult("ready_trigger", success=False,
                           message="无可用反应")
    action_name = attacker.ready_action_name or "attack"
    trigger = attacker.ready_trigger
    attacker.ready_trigger = None
    attacker.ready_action_name = None
    return ActionResult("ready_trigger", success=True,
                        message=f"{attacker.name} 触发预备：{action_name}（{trigger}）",
                        extra={"action": action_name, "trigger": trigger})


def action_search(attacker: Combatant, perception_mod: int,
                  perception_prof: int, proficient: bool, dc: int,
                  advantage: bool = False, disadvantage: bool = False) -> ActionResult:
    """搜索动作：进行一次感知（洞悉/医药/察觉/求生）检定。

    规则: R-CMB-010 动作:技能检定属性映射
          Search = WIS(洞悉/医药/察觉/求生)
    出处: topics/玩家手册2024/进行游戏/动作.htm
    """
    if not use_action(attacker):
        return ActionResult("search", success=False, message="无可用动作")
    r = check.ability_check(mod=perception_mod, prof=perception_prof,
                            proficient=proficient, dc=dc,
                            advantage=advantage, disadvantage=disadvantage,
                            circ=-conditions.d20_penalty(attacker.conditions))  # R-GLS-047
    return ActionResult("search", success=r.success,
                        message=f"{attacker.name} 搜索检定 {r.total} vs DC{dc}："
                                + ("成功" if r.success else "失败"),
                        extra={"check_total": r.total, "dc": dc})


def action_study(attacker: Combatant, intelligence_mod: int,
                 intelligence_prof: int, proficient: bool, dc: int,
                 advantage: bool = False, disadvantage: bool = False) -> ActionResult:
    """研究动作：进行一次智力（奥秘/历史/调查/自然/宗教）检定。

    规则: R-CMB-010 动作:技能检定属性映射
          Study = INT(奥秘/历史/调查/自然/宗教)
    出处: topics/玩家手册2024/进行游戏/动作.htm
    """
    if not use_action(attacker):
        return ActionResult("study", success=False, message="无可用动作")
    r = check.ability_check(mod=intelligence_mod, prof=intelligence_prof,
                            proficient=proficient, dc=dc,
                            advantage=advantage, disadvantage=disadvantage,
                            circ=-conditions.d20_penalty(attacker.conditions))  # R-GLS-047
    return ActionResult("study", success=r.success,
                        message=f"{attacker.name} 研究检定 {r.total} vs DC{dc}："
                                + ("成功" if r.success else "失败"),
                        extra={"check_total": r.total, "dc": dc})


def action_utilize(attacker: Combatant, object_name: str = "",
                   ability_mod: int = 0, prof: int = 0, proficient: bool = False,
                   dc: int = 0, advantage: bool = False,
                   disadvantage: bool = False) -> ActionResult:
    """操作动作：使用一个非魔法物件。

    规则: R-CMB-014 操作 使用一个非魔法物件
          R-CMB-005 第二个物件需执行操作动作
    出处: topics/玩家手册2024/进行游戏/动作.htm
    说明: 若需要检定（如撬锁），进行属性检定；否则仅消耗动作。
    """
    if not use_action(attacker):
        return ActionResult("utilize", success=False, message="无可用动作")
    if dc > 0:
        r = check.ability_check(mod=ability_mod, prof=prof,
                                proficient=proficient, dc=dc,
                                advantage=advantage, disadvantage=disadvantage,
                                circ=-conditions.d20_penalty(attacker.conditions))  # R-GLS-047
        return ActionResult("utilize", success=r.success,
                            message=f"{attacker.name} 操作{object_name}："
                                    + ("成功" if r.success else "失败"),
                            extra={"check_total": r.total, "dc": dc})
    return ActionResult("utilize", success=True,
                        message=f"{attacker.name} 操作{object_name}")


def action_influence(attacker: Combatant, ability_mod: int, prof: int,
                     proficient: bool, dc: int = 15,
                     skill: str = "persuasion",
                     advantage: bool = False, disadvantage: bool = False) -> ActionResult:
    """影响动作：进行社交检定（说服/欺瞒/威吓/表演）以改变 NPC 态度。

    规则: 术语汇编/动作.txt「影响」— 用魅力属性技能影响 NPC 态度。
          友好 DC-5 / 冷漠 DC+0 / 敌对 DC+5（态度修正由上层计算后传入 dc）。
    出处: topics/玩家手册2024/术语汇编/动作.htm
    """
    if not use_action(attacker):
        return ActionResult("influence", success=False, message="无可用动作")
    r = check.ability_check(mod=ability_mod, prof=prof,
                            proficient=proficient, dc=dc,
                            advantage=advantage, disadvantage=disadvantage,
                            circ=-conditions.d20_penalty(attacker.conditions))
    return ActionResult("influence", success=r.success,
                        message=f"{attacker.name} {skill}检定 {r.total} vs DC{dc}："
                                + ("成功" if r.success else "失败"),
                        extra={"check_total": r.total, "dc": dc, "skill": skill})


# ──────────────────────────────────────────────────────────────────────────
# 动作分派表
# ──────────────────────────────────────────────────────────────────────────

# 规则: R-CMB-014 动作表（攻击/疾走/撤离/回避/协助/躲藏/影响/魔法/预备/搜索/研究/操作）
# 出处: topics/玩家手册2024/进行游戏/动作.htm
COMBAT_ACTIONS: dict[str, Callable[..., ActionResult]] = {
    "attack":     action_attack,
    "dash":       action_dash,
    "disengage":  action_disengage,
    "dodge":      action_dodge,
    "help":       action_help,
    "hide":       action_hide,
    "influence":  action_influence,
    "magic":      action_magic,
    "ready":      action_ready,
    "search":     action_search,
    "study":      action_study,
    "two_weapon_attack": action_two_weapon_attack,
    "utilize":    action_utilize,
}


def resolve_combat_action(action_type: str, attacker: Combatant,
                          target: Optional[Combatant] = None,
                          weapon: Optional[WeaponProfile] = None,
                          **kwargs) -> ActionResult:
    """分派并结算一次战斗动作。

    规则: R-CMB-011 一次一个动作限制（use_action 内部检查）
          R-CMB-014 攻击流程 / 动作表
    出处: topics/玩家手册2024/进行游戏/动作.htm

    参数:
      action_type: COMBAT_ACTIONS 的键之一
      attacker: 执行动作的参战者
      target: 攻击/协助的目标（可选）
      weapon: 攻击用的武器档案（attack 必填）
      **kwargs: 动作特定参数（如 advantage, dc, stealth_mod 等）

    返回:
      ActionResult，包含命中/伤害/叙事摘要。
    """
    handler = COMBAT_ACTIONS.get(action_type)
    if handler is None:
        return ActionResult(action_type, success=False,
                            message=f"未知动作类型: {action_type}")

    # 根据动作类型组装参数
    if action_type == "attack":
        if weapon is None:
            return ActionResult("attack", success=False,
                                message="攻击动作需要 weapon 参数")
        if target is None:
            return ActionResult("attack", success=False,
                                message="攻击动作需要 target 参数")
        return action_attack(attacker=attacker, target=target, weapon=weapon,
                             **kwargs)
    elif action_type == "two_weapon_attack":
        if target is None:
            return ActionResult("two_weapon_attack", success=False,
                                message="双武器攻击需要 target 参数")
        main_weapon = kwargs.pop("main_weapon", weapon)
        off_hand_weapon = kwargs.pop("off_hand_weapon", None)
        if off_hand_weapon is None:
            return ActionResult("two_weapon_attack", success=False,
                                message="双武器攻击需要 off_hand_weapon 参数")
        return action_two_weapon_attack(attacker=attacker, target=target,
                                        main_weapon=main_weapon,
                                        off_hand_weapon=off_hand_weapon, **kwargs)
    elif action_type in ("dash", "disengage", "dodge"):
        return handler(attacker=attacker)
    elif action_type == "help":
        ally = kwargs.pop("ally", None)
        if ally is None:
            return ActionResult("help", success=False,
                                message="协助动作需要 ally 参数")
        return action_help(attacker=attacker, ally=ally, target=target, **kwargs)
    elif action_type == "hide":
        return action_hide(attacker=attacker, **kwargs)
    elif action_type == "magic":
        return action_magic(attacker=attacker, **kwargs)
    elif action_type == "ready":
        return action_ready(attacker=attacker, **kwargs)
    elif action_type == "search":
        return action_search(attacker=attacker, **kwargs)
    elif action_type == "study":
        return action_study(attacker=attacker, **kwargs)
    elif action_type == "utilize":
        return action_utilize(attacker=attacker, **kwargs)
    elif action_type == "influence":
        return action_influence(attacker=attacker, **kwargs)
    else:
        return handler(attacker=attacker, target=target, weapon=weapon, **kwargs)


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    from . import dice as _dice

    attacker = Combatant(cid="a1", name="战士", side="player")
    target = Combatant(cid="t1", name="哥布林", side="enemy")
    weapon = WeaponProfile(name="长剑", attack_bonus=5,
                           damage_dice="1d8", damage_type="slashing",
                           ability_mod=3, add_ability_mod_to_damage=True)

    # 攻击命中（固定 d20=15 → 15+5=20 ≥ AC10）
    orig = _dice.roll_d20
    orig_rd = _dice.roll_dice
    _dice.roll_d20 = lambda advantage=False, disadvantage=False: \
        type("R", (), {"used": 15, "rolls": [15], "mode": "normal"})()
    _dice.roll_dice = lambda expr, *, crit=False: \
        type("R", (), {"total": 6, "dice_rolls": [6], "expression": expr,
                       "modifier": 0, "crit": crit, "notes": ""})()

    r = resolve_combat_action("attack", attacker, target=target,
                              weapon=weapon, target_ac=10)
    assert r.success and r.attack_result.hit
    assert r.damage_result is not None
    # 伤害 = 骰子6 + 属性调整值3 = 9
    assert r.damage_result.final == 9, r.damage_result
    assert attacker.action_used is True

    # 无可用动作时再次攻击应失败
    r2 = resolve_combat_action("attack", attacker, target=target,
                               weapon=weapon, target_ac=10)
    assert r2.success is False

    # 重置动作
    attacker.action_used = False

    # 天然20重击（d20=20）
    _dice.roll_d20 = lambda advantage=False, disadvantage=False: \
        type("R", (), {"used": 20, "rolls": [20], "mode": "normal"})()
    _dice.roll_dice = lambda expr, *, crit=False: \
        type("R", (), {"total": 16 if crit else 8,
                       "dice_rolls": [8, 8] if crit else [8],
                       "expression": expr, "modifier": 0,
                       "crit": crit, "notes": ""})()
    r3 = resolve_combat_action("attack", attacker, target=target,
                               weapon=weapon, target_ac=30)
    assert r3.attack_result.hit and r3.attack_result.crit
    # 重击伤害 = 骰子16 + 属性3 = 19
    assert r3.damage_result.final == 19, r3.damage_result

    # 重置动作以测试天然1失手
    attacker.action_used = False
    # 天然1失手（d20=1）
    _dice.roll_d20 = lambda advantage=False, disadvantage=False: \
        type("R", (), {"used": 1, "rolls": [1], "mode": "normal"})()
    r4 = resolve_combat_action("attack", attacker, target=target,
                               weapon=weapon, target_ac=5)
    assert r4.attack_result.hit is False

    _dice.roll_d20 = orig
    _dice.roll_dice = orig_rd

    # 疾走（R-CMB-006）
    attacker2 = Combatant(cid="a2", name="盗贼", speed=30)
    attacker2.speed_remaining = 30
    rd = resolve_combat_action("dash", attacker2)
    assert rd.success
    assert attacker2.speed_remaining == 60   # 30 + 30
    assert attacker2.action_used is True

    # 撤离（R-CMB-007）
    attacker3 = Combatant(cid="a3", name="游侠", speed=30)
    rdis = resolve_combat_action("disengage", attacker3)
    assert rdis.success and attacker3.disengage_active is True

    # 回避（R-CMB-008）
    attacker4 = Combatant(cid="a4", name="牧师", speed=30)
    rdod = resolve_combat_action("dodge", attacker4)
    assert rdod.success and attacker4.dodge_active is True

    # 躲藏（R-CMB-009）— 固定 d20 让检定成功
    orig_chk = check.ability_check
    check.ability_check = lambda **kw: type("R", (), {
        "success": True, "total": 15, "d20": 10, "rolls": [10],
        "mode": "normal", "target": kw.get("dc", 0),
        "margin": 5, "modifier": 5})()
    attacker5 = Combatant(cid="a5", name="游荡者", speed=30)
    rh = resolve_combat_action("hide", attacker5, stealth_mod=5,
                               stealth_prof=3, proficient=True, dc=12)
    assert rh.success and attacker5.hidden is True
    check.ability_check = orig_chk

    # 搜索（R-CMB-010 Search=WIS）
    attacker6 = Combatant(cid="a6", name="游侠2", speed=30)
    check.ability_check = lambda **kw: type("R", (), {
        "success": True, "total": 18, "d20": 10, "rolls": [10],
        "mode": "normal", "target": kw.get("dc", 0),
        "margin": 3, "modifier": 8})()
    rs = resolve_combat_action("search", attacker6, perception_mod=8,
                               perception_prof=3, proficient=True, dc=15)
    assert rs.success
    check.ability_check = orig_chk

    # 研究（R-CMB-010 Study=INT）
    attacker7 = Combatant(cid="a7", name="法师2", speed=30)
    check.ability_check = lambda **kw: type("R", (), {
        "success": False, "total": 8, "d20": 5, "rolls": [5],
        "mode": "normal", "target": kw.get("dc", 0),
        "margin": -7, "modifier": 3})()
    rst = resolve_combat_action("study", attacker7, intelligence_mod=3,
                                intelligence_prof=3, proficient=True, dc=15)
    assert rst.success is False
    check.ability_check = orig_chk

    # 协助（R-CMB-014 help）
    attacker8 = Combatant(cid="a8", name="战士3", speed=30)
    ally = Combatant(cid="al", name="法师", speed=30)
    rhp = resolve_combat_action("help", attacker8, ally=ally, target=target)
    assert rhp.success

    # 魔法（R-CMB-014 magic）
    attacker9 = Combatant(cid="a9", name="法师3", speed=30)
    rm = resolve_combat_action("magic", attacker9, spell_name="火球术",
                               spell_dc=15)
    assert rm.success

    # 预备（R-CMB-014 ready）
    attacker10 = Combatant(cid="a10", name="战士4", speed=30)
    rr = resolve_combat_action("ready", attacker10,
                               trigger_condition="敌人靠近",
                               ready_action="attack")
    assert rr.success

    # 操作（R-CMB-014 utilize）
    attacker11 = Combatant(cid="a11", name="游荡者2", speed=30)
    ru = resolve_combat_action("utilize", attacker11, object_name="门把手")
    assert ru.success

    # 未知动作
    rbad = resolve_combat_action("fly", attacker5)
    assert rbad.success is False

    # ── 双武器战斗（R-ITM-014「轻型」）──
    main_w = WeaponProfile(name="短剑", attack_bonus=5, damage_dice="1d6",
                           damage_type="piercing", ability_mod=3,
                           add_ability_mod_to_damage=True)
    off_w = WeaponProfile(name="匕首", attack_bonus=5, damage_dice="1d4",
                          damage_type="piercing", ability_mod=3,
                          add_ability_mod_to_damage=True)
    # 1) 主+副均轻型、正属性调整值：主手6+3=9；副手6+0=6（不加属性）
    _dice.roll_d20 = lambda advantage=False, disadvantage=False: \
        type("R", (), {"used": 15, "rolls": [15], "mode": "normal"})()
    _dice.roll_dice = lambda expr, *, crit=False: \
        type("R", (), {"total": 6, "dice_rolls": [6], "expression": expr,
                       "modifier": 0, "crit": crit, "notes": ""})()
    a = Combatant(cid="tw", name="游荡者", side="player")
    t = Combatant(cid="twT", name="兽人", side="enemy")
    r = action_two_weapon_attack(a, t, main_w, off_w, target_ac=10)
    assert r.success and r.attack_result.hit, r.message
    assert r.damage_result.final == 9                          # 主手 6+3
    assert a.action_used and a.bonus_action_used
    off = r.extra["off_hand"]
    assert off["attempted"] and off["attack_result"].hit
    assert off["damage_result"].final == 6, off["damage_result"]   # 副手不加属性(3≥0)
    assert r.extra["bonus_action_used"] is True

    # 2) 副手非轻型 → 不发动额外攻击，附赠不消耗
    a2 = Combatant(cid="tw2", name="战士", side="player")
    t2 = Combatant(cid="tw2T", name="兽人2", side="enemy")
    off_heavy = WeaponProfile(name="长剑", attack_bonus=5, damage_dice="1d8",
                              damage_type="slashing", ability_mod=3,
                              add_ability_mod_to_damage=True)
    r2 = action_two_weapon_attack(a2, t2, main_w, off_heavy, target_ac=10)
    assert r2.success and r2.attack_result.hit
    assert r2.extra["off_hand"]["attempted"] is False
    assert r2.extra["off_hand"]["reason"] == "not_light"
    assert a2.action_used and not a2.bonus_action_used

    # 3) 无可用附赠动作 → 仅主手
    a3 = Combatant(cid="tw3", name="战士2", side="player")
    a3.bonus_action_used = True
    t3 = Combatant(cid="tw3T", name="兽人3", side="enemy")
    r3 = action_two_weapon_attack(a3, t3, main_w, off_w, target_ac=10)
    assert r3.success and r3.attack_result.hit
    assert r3.extra["off_hand"]["attempted"] is False
    assert r3.extra["off_hand"]["reason"] == "no_bonus_action"
    assert r3.extra["bonus_action_used"] is False

    # 4) 通过分派器调用
    a4 = Combatant(cid="tw4", name="战士3", side="player")
    t4 = Combatant(cid="tw4T", name="兽人4", side="enemy")
    r4 = resolve_combat_action("two_weapon_attack", a4, target=t4,
                               main_weapon=main_w, off_hand_weapon=off_w,
                               target_ac=10)
    assert r4.success and r4.extra["off_hand"]["attempted"]
    assert a4.action_used and a4.bonus_action_used

    _dice.roll_d20 = orig
    _dice.roll_dice = orig_rd

    # 5) 副手负属性调整值仍施加（"负数除外"）
    _dice.roll_d20 = lambda advantage=False, disadvantage=False: \
        type("R", (), {"used": 15, "rolls": [15], "mode": "normal"})()
    _dice.roll_dice = lambda expr, *, crit=False: \
        type("R", (), {"total": 4, "dice_rolls": [4], "expression": expr,
                       "modifier": 0, "crit": crit, "notes": ""})()
    a5 = Combatant(cid="tw5", name="虚弱盗贼", side="player")
    t5 = Combatant(cid="tw5T", name="兽人5", side="enemy")
    mw = WeaponProfile(name="短剑", attack_bonus=0, damage_dice="1d6",
                       damage_type="piercing", ability_mod=-1,
                       add_ability_mod_to_damage=True)
    ow = WeaponProfile(name="匕首", attack_bonus=0, damage_dice="1d4",
                       damage_type="piercing", ability_mod=-1,
                       add_ability_mod_to_damage=True)
    r5 = action_two_weapon_attack(a5, t5, mw, ow, target_ac=10)
    assert r5.success and r5.attack_result.hit
    assert r5.damage_result.final == 3                          # 主手 4+(-1)
    assert r5.extra["off_hand"]["damage_result"].final == 3      # 副手施加负值 4+(-1)
    _dice.roll_d20 = orig
    _dice.roll_dice = orig_rd

    print("[actions] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
