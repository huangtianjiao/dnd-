"""借机攻击 — 当敌人离开你的触及范围时，用反应对其发动一次近战攻击。

规则出处:
  - topics/玩家手册2024/进行游戏/近战攻击.htm
  - topics/玩家手册2024/进行游戏/动作.htm（撤离避免借机攻击）

关键规则:
  - R-CMB-024 近战触及范围：生物通常具有5尺触及。
  - R-CMB-025 借机攻击触发：当一个你可见的生物离开你的触及范围时，
    你可以消耗一个反应对其发动一次近战攻击（徒手打击或武器）。
    该攻击发生于对方离开你触及范围前的那一刻。
  - R-CMB-026 避免借机攻击：撤离动作、传送、或不消耗移动力/动作/
    附赠动作/反应的移动不引发借机攻击。
"""

from __future__ import annotations

from . import check, damage
from .actions import ActionResult, WeaponProfile
from .combat import Combatant, use_reaction

# ──────────────────────────────────────────────────────────────────────────
# 触发条件判定
# ──────────────────────────────────────────────────────────────────────────

def can_make_opportunity_attack(attacker: Combatant,
                                target: Combatant,
                                target_leaving_reach: bool = True,
                                target_visible: bool = True,
                                movement_type: str = "normal") -> bool:
    """是否满足借机攻击的所有触发条件。

    规则: R-CMB-025 借机攻击触发 + R-CMB-026 避免借机攻击
          trigger = visible_creature_exits_reach
          cost = 1 reaction
          attack_type = melee weapon OR unarmed strike
          不引发借机攻击的移动: 撤离/传送/不消耗移动力·动作·附赠·反应的移动
    出处: topics/玩家手册2024/进行游戏/近战攻击.htm

    条件:
      1. attacker 还有反应可用（R-CMB-013）
      2. target 正在离开 attacker 的触及范围（target_leaving_reach）
      3. target 对 attacker 可见（target_visible）
      4. target 的移动方式会引发借机攻击
         movement_type: "normal"=普通移动(引发) / "teleport"=传送(不引发) /
                         "free"=免费移动(不引发) / "disengage"=撤离(不引发)
    """
    # R-CMB-013: 反应经济
    if attacker.reaction_used:
        return False
    # R-CMB-025: 目标必须正在离开触及范围
    if not target_leaving_reach:
        return False
    # R-CMB-025: 目标必须可见
    if not target_visible:
        return False
    # R-CMB-026: 撤离/传送/免费移动不引发借机攻击
    if movement_type in ("teleport", "free"):
        return False
    return not getattr(target, "disengage_active", False)


def opportunity_attack(attacker: Combatant,
                       target: Combatant,
                       weapon: WeaponProfile | None = None,
                       target_ac: int = 10,
                       target_leaving_reach: bool = True,
                       target_visible: bool = True,
                       movement_type: str = "normal",
                       advantage: bool = False,
                       disadvantage: bool = False) -> ActionResult:
    """执行一次借机攻击。

    规则: R-CMB-025 借机攻击触发
          当一个你可见的生物离开你的触及范围时，你可以用反应对其发动
          一次近战攻击（徒手打击或武器）。该攻击发生于对方离开你触及
          范围前的那一刻。传送/免费移动/撤离不引发。
    出处: topics/玩家手册2024/进行游戏/近战攻击.htm

    参数:
      attacker: 发动借机攻击的参战者
      target: 离开触及范围的目标
      weapon: 使用的武器档案；None 表示徒手打击（1 + STR_mod）
      target_ac: 目标护甲等级（已含掩护加值等）
      target_leaving_reach: 目标是否正在离开触及范围
      target_visible: 目标对攻击者是否可见
      movement_type: "normal"/"teleport"/"free"/"disengage"
      advantage/disadvantage: 攻击检定的优劣势

    返回:
      ActionResult；success=False 表示未触发（无反应/不满足条件）。
    """
    # 检查触发条件
    if not can_make_opportunity_attack(
            attacker, target, target_leaving_reach, target_visible, movement_type):
        return ActionResult("opportunity_attack", success=False,
                            message="借机攻击条件不满足（无反应/不可见/"
                                    "目标撤离/传送/未离开触及范围）")

    # 消耗反应（R-CMB-013 / R-CMB-025）
    if not use_reaction(attacker):
        return ActionResult("opportunity_attack", success=False,
                            message="无可用反应")

    # 默认徒手打击：伤害 = 1 + STR_mod
    if weapon is None:
        weapon = WeaponProfile(
            name="徒手打击",
            attack_bonus=0,           # 调用方应填入实际加值
            damage_dice="1",
            damage_type="钝击",
            ability_mod=0,
            add_ability_mod_to_damage=True,
        )

    # R-CMB-017/R-CMB-022/R-CMB-023: 攻击检定
    atk = check.attack_roll(bonus=weapon.attack_bonus, ac=target_ac,
                            advantage=advantage, disadvantage=disadvantage)

    result = ActionResult(
        "opportunity_attack",
        success=True,
        message=f"{attacker.name} 对 {target.name} 发动借机攻击",
        attack_result=atk,
    )

    if not atk.hit:
        result.message += "：未命中"
        return result

    # R-CMB-029: 重击时伤害骰翻倍
    req = damage.DamageRequest(
        dice_expr=weapon.damage_dice,
        damage_type=weapon.damage_type,
        ability_mod=weapon.ability_mod,
        add_mod=weapon.add_ability_mod_to_damage,
        crit=atk.crit,
    )
    dmg = damage.roll_damage(req)
    result.damage_result = dmg
    result.message += (f"：命中{'（重击）' if atk.crit else ''}，"
                       f"造成 {dmg.final} 点{weapon.damage_type}伤害")
    return result


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    from . import dice as _dice

    attacker = Combatant(cid="g1", name="哥布林", side="enemy", reach=5)
    target = Combatant(cid="p1", name="战士", side="player", speed=30)

    # 固定 d20=15 → 命中 AC10
    orig = _dice.roll_d20
    orig_rd = _dice.roll_dice
    _dice.roll_d20 = lambda advantage=False, disadvantage=False: \
        type("R", (), {"used": 15, "rolls": [15], "mode": "normal"})()
    _dice.roll_dice = lambda expr, *, crit=False: \
        type("R", (), {"total": 6, "dice_rolls": [6],
                       "expression": expr, "modifier": 0,
                       "crit": crit, "notes": ""})()

    weapon = WeaponProfile(name="短剑", attack_bonus=4,
                           damage_dice="1d6", damage_type="piercing",
                           ability_mod=2, add_ability_mod_to_damage=True)

    r = opportunity_attack(attacker, target, weapon=weapon, target_ac=10)
    assert r.success, r.message
    assert r.attack_result.hit
    assert r.damage_result.final == 8   # 6 + 2
    assert attacker.reaction_used is True

    # 第二次借机攻击：反应已用，应失败
    r2 = opportunity_attack(attacker, target, weapon=weapon, target_ac=10)
    assert r2.success is False

    # 重置反应
    attacker.reaction_used = False

    # 目标撤离（disengage_active）：不应触发
    target.disengage_active = True
    r3 = opportunity_attack(attacker, target, weapon=weapon, target_ac=10)
    assert r3.success is False
    target.disengage_active = False

    # 目标不可见：不应触发
    r4 = opportunity_attack(attacker, target, weapon=weapon, target_ac=10,
                            target_visible=False)
    assert r4.success is False

    # 目标未离开触及范围：不应触发
    r5 = opportunity_attack(attacker, target, weapon=weapon, target_ac=10,
                            target_leaving_reach=False)
    assert r5.success is False

    # 传送不引发借机攻击
    attacker.reaction_used = False
    r5b = opportunity_attack(attacker, target, weapon=weapon, target_ac=10,
                             movement_type="teleport")
    assert r5b.success is False, "传送不应引发借机攻击"
    # 免费移动不引发
    r5c = opportunity_attack(attacker, target, weapon=weapon, target_ac=10,
                             movement_type="free")
    assert r5c.success is False, "免费移动不应引发借机攻击"

    # 天然20重击
    _dice.roll_d20 = lambda advantage=False, disadvantage=False: \
        type("R", (), {"used": 20, "rolls": [20], "mode": "normal"})()
    _dice.roll_dice = lambda expr, *, crit=False: \
        type("R", (), {"total": 12 if crit else 6,
                       "dice_rolls": [6, 6] if crit else [6],
                       "expression": expr, "modifier": 0,
                       "crit": crit, "notes": ""})()
    attacker.reaction_used = False
    r6 = opportunity_attack(attacker, target, weapon=weapon, target_ac=30)
    assert r6.attack_result.hit and r6.attack_result.crit
    assert r6.damage_result.final == 14   # 12 + 2

    # 徒手打击（weapon=None）
    _dice.roll_d20 = lambda advantage=False, disadvantage=False: \
        type("R", (), {"used": 15, "rolls": [15], "mode": "normal"})()
    _dice.roll_dice = lambda expr, *, crit=False: \
        type("R", (), {"total": 1, "dice_rolls": [1],
                       "expression": expr, "modifier": 0,
                       "crit": crit, "notes": ""})()
    attacker.reaction_used = False
    r7 = opportunity_attack(attacker, target, weapon=None, target_ac=10)
    assert r7.success and r7.damage_result.final == 1   # 1d1=1 + 0

    _dice.roll_d20 = orig
    _dice.roll_dice = orig_rd

    print("[opportunity_attack] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
