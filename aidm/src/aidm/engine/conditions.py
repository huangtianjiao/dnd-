"""状态条件引擎 — 14 种状态效应 + 力竭累加。

提供状态集合/增删（不叠加规则）、战斗相关修饰符（攻防优劣势/速度/d20惩罚/
失能/专注打断）。标注规则ID+出处。规则依据 R-GLS-044~058、R-QCK-003/004、
R-GLS-043（不叠加）、R-GLS-047（力竭累加）。
"""

from __future__ import annotations

from dataclasses import dataclass, field

# R-QCK-003（审计修正后）状态条件全集 15 项（含力竭）
# 出处: topics/玩家手册2024/术语汇编/状态.htm
CONDITIONS = frozenset({
    "目盲", "魅惑", "耳聋", "恐慌", "受擒", "失能", "隐形",
    "麻痹", "石化", "力竭", "中毒", "倒地", "束缚", "震慑", "昏迷",
})

# 失能性状态：含"失能"本身及隐含失能的状态
# R-GLS-050 失能 / R-GLS-052 麻痹 / R-GLS-057 震慑 / R-GLS-058 昏迷 / R-GLS-053 石化
INCAPACITATING = frozenset({"失能", "麻痹", "震慑", "昏迷", "石化"})

# 速度归0的状态（除倒地外）
# R-GLS-049 受擒 / R-GLS-052 麻痹 / R-GLS-053 石化 / R-GLS-056 束缚 / R-GLS-058 昏迷
SPEED_ZERO_STATES = frozenset({"受擒", "麻痹", "石化", "束缚", "昏迷"})


@dataclass
class ConditionState:
    """生物的状态集合（持久化于角色卡）。力竭单独记等级。"""
    conditions: set[str] = field(default_factory=set)
    exhaustion: int = 0                # R-GLS-047 力竭等级 0..6

    # —— 序列化（供 stats.store 持久化参战者状态，DMG「使用并跟进状态」）——
    def to_dict(self) -> dict:
        return {"conditions": sorted(self.conditions), "exhaustion": self.exhaustion}

    @classmethod
    def from_dict(cls, d: dict | None) -> "ConditionState":
        d = d or {}
        return cls(conditions=set(d.get("conditions", [])),
                   exhaustion=int(d.get("exhaustion", 0)))

    def add(self, cond: str) -> bool:
        """施加状态。非力竭不叠加（仅有/无）；力竭等级+1。

        规则: R-GLS-043 状态不叠加原则（力竭例外）
        出处: topics/玩家手册2024/术语汇编/状态与其他游戏状况.htm
        返回: 是否为新施加（力竭总返回True）。
        """
        if cond == "力竭":              # R-GLS-047 力竭可叠加
            self.exhaustion = min(6, self.exhaustion + 1)
            return True
        if cond not in CONDITIONS:
            raise ValueError(f"未知状态 {cond!r}，可选: {sorted(CONDITIONS)}")
        if cond in self.conditions:
            return False                # 已有，不叠加
        self.conditions.add(cond)
        # 昏迷自动施加倒地（规则: 状态.txt「昏迷」→ 失能+倒地+掉落物品）
        if cond == "昏迷" and "倒地" not in self.conditions:
            self.conditions.add("倒地")
        return True

    def remove(self, cond: str) -> bool:
        if cond == "力竭":
            if self.exhaustion > 0:
                self.exhaustion -= 1
                return True
            return False
        if cond in self.conditions:
            self.conditions.discard(cond)
            return True
        return False

    def has(self, cond: str) -> bool:
        return (cond == "力竭" and self.exhaustion > 0) or cond in self.conditions

    def is_incapacitated(self) -> bool:
        """是否失能（无法动作/附赠/反应，打断专注）。

        规则: R-GLS-050 失能（含隐含失能的麻痹/震慑/昏迷/石化）
        """
        return any(c in self.conditions for c in INCAPACITATING)

    def is_dead_from_exhaustion(self) -> bool:
        """力竭6级即死。规则: R-GLS-047 / R-QCK-004"""
        return self.exhaustion >= 6


# ──────────────────────────────────────────────────────────────────────────
# 战斗修饰符
# ──────────────────────────────────────────────────────────────────────────

def d20_penalty(state: ConditionState) -> int:
    """D20 检定的减值：力竭等级×2。

    规则: R-GLS-047 力竭（每级 D20 检定 −2）
    出处: topics/玩家手册2024/术语汇编/状态.htm
    """
    return state.exhaustion * 2


def speed_after_conditions(base_speed: int, state: ConditionState) -> int:
    """受状态影响后的速度。

    规则: R-GLS-049/052/053/056/058 速度归0；R-GLS-047 力竭 −等级×5 尺
    出处: 术语汇编/状态.htm
    说明: 倒地不直接归0（可匍匐/起立），倒地起立消耗由 combat 处理。
    """
    if any(state.has(c) for c in SPEED_ZERO_STATES):
        return 0
    speed = base_speed - state.exhaustion * 5     # R-GLS-047
    return max(0, speed)


@dataclass
class AttackModifiers:
    """一次攻击检定的优劣势/自动重击标记（由调用方传入 attack_roll）。"""
    attacker_advantage: bool = False
    attacker_disadvantage: bool = False
    target_auto_crit_if_hit: bool = False   # 目标麻痹/昏迷且近战5尺内 → 命中即重击


def attack_modifiers(attacker: ConditionState, target: ConditionState,
                     distance_ft: int = 5, *,
                     target_is_grappler: bool = False,
                     fear_source_visible: bool = True,
                     attacker_visible_to_target: bool = False,
                     target_visible_to_attacker: bool = False) -> AttackModifiers:
    """根据攻守双方状态计算攻击检定的优劣势与自动重击。

    规则: R-GLS-044目盲 / R-GLS-054中毒 / R-GLS-055倒地 / R-GLS-052麻痹 /
          R-GLS-058昏迷（5尺内命中即重击）/ R-GLS-056束缚 / R-GLS-051隐形
    出处: topics/玩家手册2024/术语汇编/状态.htm
    参数:
      target_is_grappler: 目标是否为攻击者的擒抱者。受擒状态原文：
          「除擒抱者外，你对其他任何目标进行的攻击检定都具有劣势」。
      fear_source_visible: 恐慌源是否在攻击者视线内。恐慌状态原文：
          「只要恐惧源在你的视线范围内，你进行的属性检定与攻击检定就具有劣势」。
      attacker_visible_to_target: 目标能否看见隐形的攻击者。隐形状态原文：
          「如果一个生物能以某种方式看见你，那么你在面对该生物时不会获得这一增益」，
          为 True 时隐形攻击者不获得攻击优势。
      target_visible_to_attacker: 攻击者能否看见隐形的目标（如真实视觉/盲视），
          为 True 时对隐形目标的攻击不受劣势。
    """
    adv = False
    dis = False

    # —— 攻击者侧 ——
    if attacker.has("目盲"):            # R-GLS-044 自己攻击劣势
        dis = True
    if attacker.has("中毒"):            # R-GLS-054 攻击检定劣势
        dis = True
    if attacker.has("束缚"):            # R-GLS-056 自己攻击劣势
        dis = True
    # R-GLS-049 受擒：仅对擒抱者以外的目标攻击劣势（2024）
    if attacker.has("受擒") and not target_is_grappler:
        dis = True
    # R-GLS-048 恐慌：仅恐惧源在视线内时攻击劣势
    if attacker.has("恐慌") and fear_source_visible:
        dis = True
    if attacker.has("倒地"):            # R-GLS-055 倒地自己攻击劣势
        dis = True
    # R-GLS-051 隐形：自己攻击优势；若目标能看见隐形者则无此增益（2024）
    if attacker.has("隐形") and not attacker_visible_to_target:
        adv = True

    # —— 目标侧（对目标的攻击） ——
    if target.has("目盲"):              # R-GLS-044 目标目盲 → 攻击其有优势
        adv = True
    # R-GLS-051 目标隐形 → 攻击其劣势；若攻击者能看见隐形目标则无劣势（2024）
    if target.has("隐形") and not target_visible_to_attacker:
        dis = True
    if target.has("束缚") or target.has("麻痹") or target.has("震慑") or target.has("昏迷") or target.has("石化"):
        adv = True                       # R-GLS-052/053/056/057/058 攻击这些目标优势
    if target.has("倒地"):              # R-GLS-055 倒地：5尺内优势，5尺外劣势
        if distance_ft <= 5:
            adv = True
        else:
            dis = True

    # R-GLS-052 麻痹 / R-GLS-058 昏迷：5尺内近战命中即重击
    auto_crit = (target.has("麻痹") or target.has("昏迷")) and distance_ft <= 5

    return AttackModifiers(adv, dis, auto_crit)


def concentration_broken_on_state_change(new_state: ConditionState) -> bool:
    """陷入失能/昏迷/石化等是否打断专注。

    规则: R-GLS-050 失能打断专注（施展另一专注法术/失能/死亡均失去专注，见 R-SPL-019）
    出处: topics/玩家手册2024/术语汇编/状态.htm
    """
    return new_state.is_incapacitated()


def long_rest_reduce_exhaustion(state: ConditionState) -> None:
    """长休力竭−1级（降至0结束）。规则: R-GLS-047/R-QCK-004  出处: 状态.htm"""
    state.exhaustion = max(0, state.exhaustion - 1)


# ──────────────────────────────────────────────────────────────────────────
# 状态衍生的规则效果（豁免自动失败 / 抗性 / 检定劣势）
# ──────────────────────────────────────────────────────────────────────────

# 力/敏豁免自动失败的状态
# 规则: 术语汇编/状态.htm — 麻痹/震慑/石化/昏迷 → 自动失败力量和敏捷豁免
# 注意: 束缚（Restrained）不自动失败，原文仅为「敏捷豁免检定具有劣势」，
#       见 save_disadvantage()。
_AUTO_FAIL_SAVE_STATES = frozenset({"麻痹", "震慑", "石化", "昏迷"})


def auto_fail_save_abilities(state: ConditionState) -> frozenset[str]:
    """返回该状态下自动失败的豁免属性集合。

    规则: 术语汇编/状态.htm（麻痹/震慑/石化/昏迷 自动失败力/敏豁免）
    出处: topics/玩家手册2024/术语汇编/状态.htm
    """
    if any(state.has(c) for c in _AUTO_FAIL_SAVE_STATES):
        return frozenset({"str", "dex"})
    return frozenset()


def save_disadvantage(state: ConditionState, save_ability: str) -> bool:
    """该豁免是否因状态具有劣势。

    规则: 术语汇编/状态.htm「束缚」— 你进行的敏捷豁免检定具有劣势。
    出处: topics/玩家手册2024/术语汇编/状态.htm
    用法: check.saving_throw(..., disadvantage=conditions.save_disadvantage(state, ability))
    """
    return save_ability.lower() == "dex" and state.has("束缚")


def should_waive_save(state: ConditionState, save_ability: str) -> bool:
    """该豁免是否应自动判失败（因状态导致）。

    规则: 术语汇编/状态.txt
    用法: check.saving_throw(..., waive=conditions.should_waive_save(state, ability))
    """
    return save_ability.lower() in auto_fail_save_abilities(state)


def condition_resistances(state: ConditionState) -> set[str]:
    """状态衍生的伤害抗性集合。

    规则: 术语汇编/状态.txt「石化」→ 对所有伤害具有抗性
    出处: topics/玩家手册2024/术语汇编/状态.htm
    """
    resists: set[str] = set()
    if state.has("石化"):
        resists.add("*")    # 石化：对所有伤害抗性
    return resists


def condition_immunities(state: ConditionState) -> set[str]:
    """状态衍生的伤害免疫集合。

    规则: 术语汇编/状态.htm「石化」
    出处: topics/玩家手册2024/术语汇编/状态.htm
    说明: 2024 版石化的「中毒免疫」是对「中毒状态」的免疫而非毒素
          伤害免疫（见 status_immunities），故此处不再返回伤害免疫。
    """
    return set()


def status_immunities(state: ConditionState) -> set[str]:
    """状态衍生的「状态免疫」集合（非伤害免疫）。

    规则: 术语汇编/状态.htm「石化」— 中毒免疫Poison Immunity：
          你具有中毒状态的免疫。
    出处: topics/玩家手册2024/术语汇编/状态.htm
    用法: 施加状态前检查 cond in status_immunities(state) 则跳过。
    """
    immuns: set[str] = set()
    if state.has("石化"):
        immuns.add("中毒")  # 石化：免疫中毒状态
    return immuns


def ability_check_disadvantage(state: ConditionState) -> bool:
    """该状态下属性检定是否具有劣势。

    规则: 术语汇编/状态.txt
          - 中毒：攻击检定+属性检定均劣势
          - 力竭：不直接给检定劣势（而是 d20 减值，见 d20_penalty）
    出处: topics/玩家手册2024/术语汇编/状态.htm
    """
    return state.has("中毒")


# ──────────────────────────────────────────────────────────────────────────
# 15种状态完整数值效果定义（COM-011）
# ──────────────────────────────────────────────────────────────────────────

CONDITION_DEFINITIONS: dict[str, dict] = {
    "目盲": {
        "action_constraints": [],
        "roll_modifiers": {
            "attack_roll": "auto_miss",
            "ability_check_see": "auto_fail",
        },
        "movement_constraints": {},
        "on_apply": [],
        "on_remove": [],
    },
    "魅惑": {
        "action_constraints": {"cannot_attack_source": True},
        "roll_modifiers": {},
        "movement_constraints": {},
        "source_id_required": True,
        "on_apply": [],
        "on_remove": [],
    },
    "耳聋": {
        "action_constraints": {},
        "roll_modifiers": {"ability_check_hear": "auto_fail"},
        "movement_constraints": {},
    },
    "恐慌": {
        "action_constraints": {},
        "roll_modifiers": {
            "attack_roll": "disadvantage_if_source_visible",
            "ability_check": "disadvantage_if_source_visible",
        },
        "movement_constraints": {"cannot_move_closer_to_source": True},
        "source_id_required": True,
    },
    "受擒": {
        "action_constraints": {},
        "roll_modifiers": {},
        "movement_constraints": {"speed": 0},
    },
    "失能": {
        "action_constraints": {
            "no_actions": True,
            "no_bonus_actions": True,
            "no_reactions": True,
        },
        "roll_modifiers": {},
        "movement_constraints": {},
    },
    "隐形": {
        "action_constraints": {},
        "roll_modifiers": {"attack_roll_again": "advantage"},
        "movement_constraints": {},
    },
    "麻痹": {
        "action_constraints": {
            "no_actions": True,
            "no_bonus_actions": True,
            "no_reactions": True,
        },
        "roll_modifiers": {
            "dex_save": "auto_fail",
            "attack_roll_again": "advantage_and_crit",
        },
        "movement_constraints": {"speed": 0},
    },
    "石化": {
        "action_constraints": {"no_actions": True},
        "roll_modifiers": {"dex_save": "auto_fail"},
        "movement_constraints": {"speed": 0},
        "special": {"weight_changes": True, "stops_aging": True},
    },
    "力竭": {
        "levels": {
            1: {"disadvantage_ability_checks": True},
            2: {"speed_halved": True},
            3: {"disadvantage_attack_and_save": True},
            4: {"hp_max_halved": True},
            5: {"speed_zero": True},
            6: {"dead": True},
        }
    },
    "中毒": {
        "action_constraints": {},
        "roll_modifiers": {
            "attack_roll": "disadvantage",
            "ability_check": "disadvantage",
        },
        "movement_constraints": {},
    },
    "倒地": {
        "action_constraints": {},
        "roll_modifiers": {"attack_roll_self": "disadvantage"},
        "movement_constraints": {"crawl_cost": "extra_half_speed"},
        "attack_again_modifiers": {
            "melee_within_5ft": "advantage",
            "ranged_or_far": "disadvantage",
        },
    },
    "束缚": {
        "action_constraints": {},
        "roll_modifiers": {
            "attack_roll": "disadvantage",
            "dex_save": "disadvantage",
        },
        "movement_constraints": {"speed": 0},
        "attack_again_modifiers": {"advantage": True},
    },
    "震慑": {
        "action_constraints": {
            "no_actions": True,
            "no_bonus_actions": True,
            "no_reactions": True,
        },
        "roll_modifiers": {
            "attack_roll": "disadvantage",
            "dex_save": "auto_fail",
        },
        "movement_constraints": {},
    },
    "昏迷": {
        "action_constraints": {
            "no_actions": True,
            "no_bonus_actions": True,
            "no_reactions": True,
        },
        "roll_modifiers": {
            "dex_save": "auto_fail",
            "attack_roll_again": "advantage_and_crit",
        },
        "movement_constraints": {"speed": 0},
        "special": {"drops_items": True, "unaware": True},
    },
}


def get_condition_effects(condition_name: str) -> dict:
    """返回指定状态的完整效果定义。

    规则: R-GLS-044~058 各状态效果
    出处: topics/玩家手册2024/术语汇编/状态.htm
    参数:
      condition_name: 中文名（如 "目盲"、"魅惑"、"力竭"）
    返回:
      该状态的完整效果规格字典；未知状态返回空字典。
    """
    return CONDITION_DEFINITIONS.get(condition_name, {})


def get_exhaustion_effects(level: int) -> dict:
    """返回指定力竭等级的效果定义。

    规则: R-GLS-047 力竭累加效果
    出处: topics/玩家手册2024/术语汇编/状态.htm
    """
    levels = CONDITION_DEFINITIONS.get("力竭", {}).get("levels", {})
    return levels.get(level, {})


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    s = ConditionState()
    assert s.add("中毒") is True and s.has("中毒")
    assert s.add("中毒") is False              # 不叠加（R-GLS-043）
    assert s.add("力竭") and s.add("力竭")     # 力竭可叠加
    assert s.exhaustion == 2
    assert s.add("力竭") and s.exhaustion == 3
    # 失能判定
    assert not ConditionState({"中毒"}).is_incapacitated()
    assert ConditionState({"麻痹"}).is_incapacitated()
    assert ConditionState({"昏迷"}).is_incapacitated()
    # 力竭 d20惩罚/速度
    s2 = ConditionState(); s2.add("力竭"); s2.add("力竭")
    assert d20_penalty(s2) == 4                # 2级→-4
    assert speed_after_conditions(30, s2) == 20  # 30-10
    assert speed_after_conditions(30, ConditionState({"束缚"})) == 0  # 束缚→0
    # 攻击修饰符
    m = attack_modifiers(ConditionState({"中毒"}), ConditionState())  # 攻击者中毒→劣势
    assert m.attacker_disadvantage and not m.attacker_advantage
    m = attack_modifiers(ConditionState(), ConditionState({"目盲"}))   # 目标目盲→优势
    assert m.attacker_advantage
    m = attack_modifiers(ConditionState(), ConditionState({"倒地"}), distance_ft=5)  # 倒地5尺内优势
    assert m.attacker_advantage
    m = attack_modifiers(ConditionState(), ConditionState({"倒地"}), distance_ft=15)  # 倒地5尺外劣势
    assert m.attacker_disadvantage
    m = attack_modifiers(ConditionState(), ConditionState({"麻痹"}), 5)  # 麻痹5尺内自动重击
    assert m.target_auto_crit_if_hit and m.attacker_advantage
    # 受擒：对擒抱者攻击无劣势，对其他目标劣势（R-GLS-049 2024）
    m = attack_modifiers(ConditionState({"受擒"}), ConditionState(), target_is_grappler=True)
    assert not m.attacker_disadvantage
    m = attack_modifiers(ConditionState({"受擒"}), ConditionState(), target_is_grappler=False)
    assert m.attacker_disadvantage
    # 恐慌：恐惧源不在视线内则无劣势（R-GLS-048）
    m = attack_modifiers(ConditionState({"恐慌"}), ConditionState(), fear_source_visible=False)
    assert not m.attacker_disadvantage
    m = attack_modifiers(ConditionState({"恐慌"}), ConditionState(), fear_source_visible=True)
    assert m.attacker_disadvantage
    # 豁免：束缚不自动失败，仅敏捷豁免劣势；麻痹自动失败力/敏
    assert auto_fail_save_abilities(ConditionState({"束缚"})) == frozenset()
    assert save_disadvantage(ConditionState({"束缚"}), "dex") is True
    assert save_disadvantage(ConditionState({"束缚"}), "str") is False
    assert auto_fail_save_abilities(ConditionState({"麻痹"})) == frozenset({"str", "dex"})
    assert should_waive_save(ConditionState({"麻痹"}), "dex") is True
    assert should_waive_save(ConditionState({"束缚"}), "dex") is False
    # 石化：全伤害抗性 + 中毒状态免疫（非毒素伤害免疫）
    assert condition_resistances(ConditionState({"石化"})) == {"*"}
    assert condition_immunities(ConditionState({"石化"})) == set()
    assert status_immunities(ConditionState({"石化"})) == {"中毒"}
    # 力竭6级死
    s3 = ConditionState()
    for _ in range(6):
        s3.add("力竭")
    assert s3.is_dead_from_exhaustion()
    # 长休-1
    s4 = ConditionState(); s4.add("力竭"); s4.add("力竭")
    long_rest_reduce_exhaustion(s4); assert s4.exhaustion == 1
    # 专注打断
    assert concentration_broken_on_state_change(ConditionState({"昏迷"}))
    assert not concentration_broken_on_state_change(ConditionState({"中毒"}))
    print("[conditions] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
