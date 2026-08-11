"""武器精通效应引擎 — 8 种精通词条的触发与效果判定。

规则依据:
  - R-ITM-015 武器精通词条（削弱/缓速/横扫/擦掠/迅击/推离/失衡/侵扰）
    出处: topics/玩家手册2024/装备/精通词条.htm

设计原则: 本模块为纯判定层，返回结构化效果（状态变更/额外伤害/位移），
由调用方（brain 层）应用到角色/参战者状态。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from . import check, dice


# ──────────────────────────────────────────────────────────────────────────
# COM-004: MasteryGrant — 角色精通授权追踪
# ──────────────────────────────────────────────────────────────────────────

# 精通名称（中文）→ 英文名映射
MASTERY_NAME_MAP = {
    "削弱": "sap",
    "缓速": "slow",
    "横扫": "cleave",
    "擦掠": "graze",
    "迅击": "nick",
    "推离": "push",
    "失衡": "topple",
    "侵扰": "vex",
}

# 每回合使用次数限制
MASTERY_PER_TURN_LIMITS: Dict[str, int] = {
    "削弱": 99,   # 无显式限制，每命中都可触发
    "缓速": 99,
    "横扫": 1,    # 每回合 1 次
    "擦掠": 99,
    "迅击": 1,    # 每回合 1 次
    "推离": 99,
    "失衡": 99,
    "侵扰": 99,
}


@dataclass
class MasteryGrant:
    """追踪角色是否获得特定武器精通及其每回合使用状态。

    规则: COM-004 武器精通完整接线
    """

    entity_id: str
    granted_masteries: List[str] = field(default_factory=list)  # 中文精通名列表
    per_turn_usage: Dict[str, int] = field(default_factory=dict)

    def has_mastery(self, mastery_name: str) -> bool:
        """是否拥有指定精通。"""
        return mastery_name in self.granted_masteries

    def grant(self, mastery_name: str) -> None:
        """授予精通。"""
        if mastery_name not in self.granted_masteries:
            self.granted_masteries.append(mastery_name)

    def revoke(self, mastery_name: str) -> None:
        """撤销精通。"""
        if mastery_name in self.granted_masteries:
            self.granted_masteries.remove(mastery_name)

    def can_use(self, mastery_name: str) -> bool:
        """本回合是否还能使用该精通。"""
        if not self.has_mastery(mastery_name):
            return False
        limit = MASTERY_PER_TURN_LIMITS.get(mastery_name, 99)
        current = self.per_turn_usage.get(mastery_name, 0)
        return current < limit

    def record_use(self, mastery_name: str) -> bool:
        """记录一次使用，返回是否成功（未超限）。"""
        if not self.can_use(mastery_name):
            return False
        current = self.per_turn_usage.get(mastery_name, 0)
        self.per_turn_usage[mastery_name] = current + 1
        return True

    def reset_turn(self) -> None:
        """回合开始重置使用计数。"""
        self.per_turn_usage.clear()


# ──────────────────────────────────────────────────────────────────────────
# COM-004: 精通效应与 AttackSequence 集成
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class MasteryEffect:
    """精通效应结果，用于与 AttackSequence 联动。"""

    mastery_name: str
    applied: bool
    effect_type: str = ""           # 效应类型标识
    extra_attack_available: bool = False   # Cleave: 额外攻击可用
    graze_damage: int = 0                  # Graze: 失手伤害
    push_distance_ft: int = 0              # Push: 推离距离
    target_prone: bool = False             # Topple: 倒地
    speed_reduction_ft: int = 0            # Slow: 速度减少
    attacker_advantage: bool = False       # Vex: 攻击者优势
    target_disadvantage: bool = False      # Sap: 目标劣势
    nick_active: bool = False              # Nick: 迅击激活
    dc: int = 0                            # 豁免 DC
    save_result: Optional[dict] = None     # 豁免掷骰结果
    events: List[dict] = field(default_factory=list)


def resolve_mastery_with_grant(
    mastery_name: str,
    grant: MasteryGrant,
    *,
    hit: bool,
    attacker_ability_mod: int = 0,
    attacker_prof: int = 0,
    target_size: str = "medium",
    target_con_mod: int = 0,
    target_con_prof: bool = False,
    target_prof: int = 0,
) -> MasteryEffect:
    """带 MasteryGrant 追踪的精通效应解析。

    与 resolve_mastery 互补：本函数额外检查每回合使用限制并记录使用。
    """
    if not grant.can_use(mastery_name):
        return MasteryEffect(
            mastery_name=mastery_name,
            applied=False,
            effect_type="not_available",
        )

    # 调用原始 resolve_mastery
    raw = resolve_mastery(
        mastery_name,
        hit=hit,
        attacker_ability_mod=attacker_ability_mod,
        attacker_prof=attacker_prof,
        target_size=target_size,
        target_con_mod=target_con_mod,
        target_con_prof=target_con_prof,
        target_prof=target_prof,
    )

    effect = MasteryEffect(
        mastery_name=mastery_name,
        applied=raw.get("applied", False),
        effect_type=raw.get("target_effect", ""),
    )

    if raw.get("applied"):
        grant.record_use(mastery_name)

        # 填充具体效应字段
        if mastery_name == "横扫":
            effect.extra_attack_available = True
        elif mastery_name == "擦掠":
            effect.graze_damage = raw.get("damage", 0)
        elif mastery_name == "推离":
            effect.push_distance_ft = raw.get("push_distance_ft", 0)
        elif mastery_name == "失衡":
            effect.dc = raw.get("dc", 0)
            effect.target_prone = raw.get("target_prone", False)
            effect.save_result = {"total": raw.get("save_total", 0), "d20": raw.get("save_d20", 0)}
        elif mastery_name == "缓速":
            effect.speed_reduction_ft = raw.get("speed_reduction_ft", 0)
        elif mastery_name == "侵扰":
            effect.attacker_advantage = True
        elif mastery_name == "削弱":
            effect.target_disadvantage = True
        elif mastery_name == "迅击":
            effect.nick_active = True

    return effect


# ──────────────────────────────────────────────────────────────────────────
# 精通效应分派
# ──────────────────────────────────────────────────────────────────────────

def resolve_mastery(
    mastery_name: str,
    *,
    hit: bool,
    attacker_ability_mod: int = 0,
    attacker_prof: int = 0,
    target_size: str = "medium",
    target_con_mod: int = 0,
    target_con_prof: bool = False,
    target_prof: int = 0,
) -> dict:
    """攻击后应用武器精通效应。

    规则: R-ITM-015 武器精通词条
    出处: topics/玩家手册2024/装备/精通词条.htm

    参数:
      mastery_name: 精通名称（"削弱"/"缓速"/"横扫"/"擦掠"/"迅击"/"推离"/"失衡"/"侵扰"）
      hit: 本次攻击是否命中
      attacker_ability_mod: 攻击者使用的属性调整值（擦掠用）
      attacker_prof: 攻击者熟练加值（失衡 DC 计算用）
      target_size: 目标体型（推离的体型限制用）
      target_con_mod: 目标体质调整值（失衡豁免用）
      target_con_prof: 目标是否熟练体质豁免（失衡用）
      target_prof: 目标熟练加值（失衡用）

    返回 dict:
      {"effect": str, "applied": bool, ...效果详情}
      applied=False 表示不满足触发条件（如擦掠需失手、推离目标过大）。
    """
    m = mastery_name
    if m == "削弱":
        return _mastery_sap(hit)
    if m == "缓速":
        return _mastery_slow(hit)
    if m == "横扫":
        return _mastery_cleave(hit)
    if m == "擦掠":
        return _mastery_graze(hit, attacker_ability_mod)
    if m == "迅击":
        return _mastery_nick(hit)
    if m == "推离":
        return _mastery_push(hit, target_size)
    if m == "失衡":
        return _mastery_topple(hit, attacker_ability_mod, attacker_prof,
                               target_con_mod, target_con_prof, target_prof)
    if m == "侵扰":
        return _mastery_vex(hit)
    return {"effect": "unknown", "applied": False, "reason": f"未知精通 {m!r}"}


# ──────────────────────────────────────────────────────────────────────────
# 各精通效应实现
# ──────────────────────────────────────────────────────────────────────────

def _mastery_sap(hit: bool) -> dict:
    """削弱(Sap): 命中 → 目标下次攻击检定劣势（至下回合开始）。

    规则: 精通词条.htm「削弱」— 命中后至下回合开始前，目标下一次攻击检定劣势。
    """
    if not hit:
        return {"effect": "削弱", "applied": False, "reason": "未命中"}
    return {"effect": "削弱", "applied": True,
            "target_effect": "next_attack_disadvantage",
            "duration": "until_next_turn_start"}


def _mastery_slow(hit: bool) -> dict:
    """缓速(Slow): 命中 → 目标速度 −10 尺（至下回合开始，不叠加）。

    规则: 精通词条.htm「缓速」— 命中造成伤害可令目标速度-10尺至下回合开始；多次命中不叠加。
    """
    if not hit:
        return {"effect": "缓速", "applied": False, "reason": "未命中"}
    return {"effect": "缓速", "applied": True,
            "target_effect": "speed_reduction",
            "speed_reduction_ft": 10,
            "duration": "until_next_turn_start",
            "stacks": False}


def _mastery_cleave(hit: bool) -> dict:
    """横扫(Cleave): 命中 → 可对 5 尺内另一生物再攻击一次（不加属性调整值伤害）。

    规则: 精通词条.htm「横扫」— 命中后可对5尺内另一生物再攻击一次，
          造成武器伤害（不加属性调整值，负数除外）；每回合1次。
    说明: 本函数仅标记"可发动横扫"；实际的额外攻击掷骰由调用方执行。
    """
    if not hit:
        return {"effect": "横扫", "applied": False, "reason": "未命中"}
    return {"effect": "横扫", "applied": True,
            "target_effect": "cleave_available",
            "add_ability_mod": False,
            "note": "对5尺内另一生物再攻击一次（不加属性调整值）；每回合1次"}


def _mastery_graze(hit: bool, ability_mod: int) -> dict:
    """擦掠(Graze): 失手 → 仍造成 = 属性调整值的伤害（同武器伤害类型）。

    规则: 精通词条.htm「擦掠」— 失手仍造成等于所用属性调整值的伤害（同武器伤害类型）。
    """
    if hit:
        return {"effect": "擦掠", "applied": False, "reason": "已命中（仅失手时生效）"}
    graze_damage = max(0, ability_mod)  # 属性调整值为负时不造成伤害
    return {"effect": "擦掠", "applied": True,
            "target_effect": "graze_damage",
            "damage": graze_damage,
            "note": "失手仍造成属性调整值的伤害"}


def _mastery_nick(hit: bool) -> dict:
    """迅击(Nick): 轻型武器的额外攻击改用攻击动作而非附赠动作（每回合1次）。

    规则: 精通词条.htm「迅击」— 轻型词条的额外攻击改用攻击动作而非附赠动作（每回合仍1次）。
    说明: 不依赖 hit——只要使用具有迅击精通的轻型武器发动攻击动作，即可改为不消耗附赠动作。
          本函数标记"迅击生效"，由调用方在双武器战斗中据此跳过附赠动作消耗。
    """
    return {"effect": "迅击", "applied": True,
            "target_effect": "nick_active",
            "note": "轻型词条额外攻击改用攻击动作（不消耗附赠动作）；每回合1次"}


def _mastery_push(hit: bool, target_size: str) -> dict:
    """推离(Push): 命中体型≤大型 → 直线推离至多 10 尺。

    规则: 精通词条.htm「推离」— 命中体型至多大型的生物可将其直线推离至多10尺。
    """
    if not hit:
        return {"effect": "推离", "applied": False, "reason": "未命中"}
    _SIZE_ORDER = ["tiny", "small", "medium", "large", "huge", "gargantuan"]
    try:
        idx = _SIZE_ORDER.index(target_size.lower())
    except ValueError:
        idx = 3  # 未知体型默认按大型处理
    if idx > 3:  # 超过大型
        return {"effect": "推离", "applied": False, "reason": "目标体型超过大型"}
    return {"effect": "推离", "applied": True,
            "target_effect": "push",
            "push_distance_ft": 10,
            "note": "直线推离至多10尺"}


def _mastery_vex(hit: bool) -> dict:
    """侵扰(Vex): 命中造成伤害 → 至下回合结束前，对该生物的下一次攻击检定优势。

    规则: 精通词条.htm「侵扰」— 命中并造成伤害后至下回合结束前，
          对该生物的下一次攻击检定将具有优势。
    """
    if not hit:
        return {"effect": "侵扰", "applied": False, "reason": "未命中"}
    return {"effect": "侵扰", "applied": True,
            "target_effect": "next_attack_against_target_advantage",
            "duration": "until_next_turn_end",
            "note": "至下回合结束前，对该生物的下一次攻击检定优势"}


def _mastery_topple(hit: bool, atk_ability_mod: int, atk_prof: int,
                    target_con_mod: int, target_con_prof: bool,
                    target_prof: int) -> dict:
    """失衡(Topple): 命中 → 目标体质豁免(DC=8+攻击调整值+PB)，失败倒地。

    规则: 精通词条.htm「失衡」— 命中可迫使目标体质豁免(DC=8+本次攻击调整值+PB)，失败倒地。
    """
    if not hit:
        return {"effect": "失衡", "applied": False, "reason": "未命中"}
    dc = 8 + atk_ability_mod + atk_prof
    sv = check.saving_throw(mod=target_con_mod, prof=target_prof,
                            proficient=target_con_prof, dc=dc)
    return {"effect": "失衡", "applied": True,
            "dc": dc, "save_total": sv.total, "save_d20": sv.d20,
            "target_prone": not sv.success,
            "note": "体质豁免失败则倒地" if not sv.success else "体质豁免成功，未倒地"}


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 削弱：命中生效，未命中不生效
    assert resolve_mastery("削弱", hit=True)["applied"] is True
    assert resolve_mastery("削弱", hit=False)["applied"] is False

    # 缓速：命中生效
    r = resolve_mastery("缓速", hit=True)
    assert r["applied"] and r["speed_reduction_ft"] == 10

    # 横扫：命中生效
    assert resolve_mastery("横扫", hit=True)["applied"] is True
    assert resolve_mastery("横扫", hit=False)["applied"] is False

    # 擦掠：失手生效，命中不生效
    r = resolve_mastery("擦掠", hit=False, attacker_ability_mod=4)
    assert r["applied"] and r["damage"] == 4
    assert resolve_mastery("擦掠", hit=True)["applied"] is False
    # 负属性调整值→伤害0
    r = resolve_mastery("擦掠", hit=False, attacker_ability_mod=-1)
    assert r["damage"] == 0

    # 迅击：始终生效
    assert resolve_mastery("迅击", hit=True)["applied"] is True
    assert resolve_mastery("迅击", hit=False)["applied"] is True

    # 推离：命中+体型≤大型生效
    assert resolve_mastery("推离", hit=True, target_size="medium")["applied"] is True
    assert resolve_mastery("推离", hit=True, target_size="huge")["applied"] is False
    assert resolve_mastery("推离", hit=False)["applied"] is False

    # 失衡：命中→体质豁免（monkeypatch）
    from . import dice as _dice
    orig = _dice.roll_d20
    class _R:
        def __init__(s, u): s.used, s.rolls, s.mode = u, [u], "normal"
    _dice.roll_d20 = lambda advantage=False, disadvantage=False: _R(5)
    r = resolve_mastery("失衡", hit=True, attacker_ability_mod=3, attacker_prof=2,
                        target_con_mod=1, target_con_prof=False, target_prof=2)
    assert r["applied"] and r["dc"] == 13  # 8+3+2
    assert r["target_prone"] is True       # 5+1 < 13 → 倒地
    _dice.roll_d20 = lambda advantage=False, disadvantage=False: _R(15)
    r = resolve_mastery("失衡", hit=True, attacker_ability_mod=3, attacker_prof=2,
                        target_con_mod=1, target_con_prof=False, target_prof=2)
    assert r["target_prone"] is False      # 15+1 ≥ 13 → 未倒地
    _dice.roll_d20 = orig

    # 侵扰：命中生效，未命中不生效
    r = resolve_mastery("侵扰", hit=True)
    assert r["applied"] and r["target_effect"] == "next_attack_against_target_advantage"
    assert resolve_mastery("侵扰", hit=False)["applied"] is False

    # 未知精通
    assert resolve_mastery("无名", hit=True)["applied"] is False

    print("[mastery] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
