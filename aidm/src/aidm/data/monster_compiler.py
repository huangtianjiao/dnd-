"""怪物编译器 — MonsterStatBlock / MonsterAction / MonsterCompiler / RechargeTracker。

将怪物原始数据编译为可执行动作列表，使用与玩家相同的引擎（AttackSequence、
TimingController、ReactionController）执行怪物动作。

规则依据:
  MON-001 MonsterStatBlock 编译器
  MON-002 充能/传奇/巢穴动作接线
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..engine.attack_sequence import AttackPlan, AttackSequence
from ..engine.reaction_window import ReactionController, ReactionOption, ReactionType
from ..engine.timing import TimingController, TimingHandler, TimingPoint


# ──────────────────────────────────────────────────────────────────────────
# 数据类
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class MonsterAction:
    """怪物可执行动作。"""

    action_id: str = ""
    name: str = ""
    action_type: str = "action"        # action/bonus_action/reaction/legendary
    attack_bonus: int = 0
    reach_ft: int = 5
    range_ft: int = 0
    damage_dice: str = "1d6"
    damage_type: str = "slashing"
    damage_modifier: int = 0
    special_effects: List[dict] = field(default_factory=list)
    uses_per_turn: int = -1            # -1 = unlimited
    description: str = ""

    def __post_init__(self) -> None:
        if not self.action_id:
            self.action_id = str(uuid.uuid4())


@dataclass
class MonsterStatBlock:
    """编译后的怪物数据块。"""

    monster_id: str = ""
    name: str = ""
    size: str = "Medium"
    creature_type: str = ""
    cr: float = 0

    # 基础属性
    abilities: Dict[str, int] = field(default_factory=dict)
    hp: int = 0
    hp_formula: str = ""
    ac: int = 10
    speed_ft: int = 30

    # 感官
    senses: Dict[str, int] = field(default_factory=dict)
    passive_perception: int = 10

    # 伤害亲和
    damage_immunities: List[str] = field(default_factory=list)
    damage_resistances: List[str] = field(default_factory=list)
    damage_vulnerabilities: List[str] = field(default_factory=list)
    condition_immunities: List[str] = field(default_factory=list)

    # 动作
    actions: List[MonsterAction] = field(default_factory=list)
    bonus_actions: List[MonsterAction] = field(default_factory=list)
    reactions: List[MonsterAction] = field(default_factory=list)
    legendary_actions: List[dict] = field(default_factory=list)
    legendary_resistance_count: int = 0
    legendary_action_points: int = 0

    # 特殊能力
    traits: List[dict] = field(default_factory=list)
    spellcasting: Optional[dict] = None

    # 充能
    recharge_abilities: List[dict] = field(default_factory=list)

    # 巢穴动作
    lair_actions: List[dict] = field(default_factory=list)
    lair_initiative_count: int = 0  # 巢穴动作的先攻计数（如 20）


# ──────────────────────────────────────────────────────────────────────────
# 充能追踪器
# ──────────────────────────────────────────────────────────────────────────

class RechargeTracker:
    """充能追踪器 — 管理怪物的充能动作。

    规则: 回合开始掷 d6，>= 阈值则充能成功，可使用一次。
    """

    def __init__(self) -> None:
        self._charges: Dict[str, Dict[str, bool]] = {}  # entity_id -> {ability_id: is_charged}

    def register(self, entity_id: str, ability_id: str, initially_charged: bool = True) -> None:
        """注册一个充能动作。"""
        if entity_id not in self._charges:
            self._charges[entity_id] = {}
        self._charges[entity_id][ability_id] = initially_charged

    def roll_recharge(self, entity_id: str, ability_id: str, threshold: int = 6, rng: Any = None) -> bool:
        """掷骰尝试充能。返回是否充能成功。

        Args:
            entity_id: 实体 ID
            ability_id: 充能动作 ID
            threshold: 充能阈值（默认 6，即掷 d6 >= 6 才充能）
            rng: 可选随机数生成器（需有 roll(sides) 方法）
        """
        if entity_id not in self._charges or ability_id not in self._charges[entity_id]:
            return False
        # 已经充能则无需再掷
        if self._charges[entity_id][ability_id]:
            return True
        # 掷骰
        if rng is not None:
            roll = rng.roll(6)
        else:
            import random
            roll = random.randint(1, 6)
        if roll >= threshold:
            self._charges[entity_id][ability_id] = True
            return True
        return False

    def use_charge(self, entity_id: str, ability_id: str) -> bool:
        """消耗一次充能。返回是否成功（有充能可用）。"""
        if entity_id not in self._charges or ability_id not in self._charges[entity_id]:
            return False
        if not self._charges[entity_id][ability_id]:
            return False
        self._charges[entity_id][ability_id] = False
        return True

    def is_charged(self, entity_id: str, ability_id: str) -> bool:
        """检查某充能动作是否可用。"""
        return self._charges.get(entity_id, {}).get(ability_id, False)

    def reset(self, entity_id: str) -> None:
        """重置实体的所有充能（如长休后）。"""
        if entity_id in self._charges:
            for ability_id in self._charges[entity_id]:
                self._charges[entity_id][ability_id] = True

    def get_status(self, entity_id: str) -> Dict[str, bool]:
        """获取实体所有充能状态。"""
        return dict(self._charges.get(entity_id, {}))


# ──────────────────────────────────────────────────────────────────────────
# 巢穴动作控制器
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class LairActionState:
    """巢穴动作状态。"""
    lair_id: str = ""
    initiative_count: int = 20  # 巢穴动作触发的先攻计数
    available_actions: List[dict] = field(default_factory=list)
    is_active: bool = True


class LairActionController:
    """巢穴动作控制器 — 绑定 Encounter/Lair，在指定先攻计数时运行。

    规则: 巢穴动作在先攻计数到指定值时触发（通常 20）。
    """

    def __init__(self) -> None:
        self._lair_states: Dict[str, LairActionState] = {}

    def register_lair(self, lair_id: str, initiative_count: int, actions: List[dict]) -> None:
        """注册一个巢穴。"""
        self._lair_states[lair_id] = LairActionState(
            lair_id=lair_id,
            initiative_count=initiative_count,
            available_actions=list(actions),
            is_active=True,
        )

    def should_trigger(self, lair_id: str, current_initiative: int) -> bool:
        """检查当前先攻计数是否应触发巢穴动作。"""
        state = self._lair_states.get(lair_id)
        if state is None or not state.is_active:
            return False
        return current_initiative == state.initiative_count

    def execute_lair_action(self, lair_id: str, action_index: int, context: dict) -> dict:
        """执行指定巢穴动作。"""
        state = self._lair_states.get(lair_id)
        if state is None or not state.is_active:
            return {"type": "lair_action_failed", "reason": "no_such_lair"}
        if action_index < 0 or action_index >= len(state.available_actions):
            return {"type": "lair_action_failed", "reason": "invalid_action_index"}
        action = state.available_actions[action_index]
        return {
            "type": "lair_action_executed",
            "lair_id": lair_id,
            "action": action,
            "context": context,
        }

    def deactivate_lair(self, lair_id: str) -> None:
        """停用巢穴（如 Boss 死亡后）。"""
        if lair_id in self._lair_states:
            self._lair_states[lair_id].is_active = False


# ──────────────────────────────────────────────────────────────────────────
# 怪物编译器
# ──────────────────────────────────────────────────────────────────────────

# 体型映射
_SIZE_MAP = {
    "微型": "Tiny", "小型": "Small", "中型": "Medium",
    "大型": "Large", "巨型": "Gargantuan",
    "Tiny": "Tiny", "Small": "Small", "Medium": "Medium",
    "Large": "Large", "Gargantuan": "Gargantuan",
}


def _parse_senses(senses_str: str) -> tuple:
    """解析感官字符串，返回 (senses_dict, passive_perception)。"""
    senses: Dict[str, int] = {}
    pp = 10
    if not senses_str:
        return senses, pp
    # 提取被动察觉
    pp_match = re.search(r'被动察觉\s*(\d+)', senses_str)
    if pp_match:
        pp = int(pp_match.group(1))
    # 提取各种感官
    dv_match = re.search(r'黑暗视觉\s*(\d+)', senses_str)
    if dv_match:
        senses["darkvision"] = int(dv_match.group(1))
    bs_match = re.search(r'盲视\s*(\d+)', senses_str)
    if bs_match:
        senses["blindsight"] = int(bs_match.group(1))
    tv_match = re.search(r'真实视觉\s*(\d+)', senses_str)
    if tv_match:
        senses["truesight"] = int(tv_match.group(1))
    return senses, pp


def _parse_damage_dice(dice_str: str) -> tuple:
    """解析伤害骰字符串，返回 (base_dice, modifier)。

    例: '1d6+2' -> ('1d6', 2), '2d4-1' -> ('2d4', -1), '1d8' -> ('1d8', 0)
    """
    if not dice_str:
        return "1d6", 0
    match = re.match(r'(\d+d\d+(?:[+-]\d+)?)([+-]\d+)?', dice_str)
    if match:
        base = match.group(1)
        mod_str = match.group(2)
        mod = int(mod_str) if mod_str else 0
        return base, mod
    return dice_str, 0


class MonsterCompiler:
    """怪物编译器 — 将数据转换为可执行 StatBlock。"""

    def __init__(self) -> None:
        self._recharge_tracker = RechargeTracker()
        self._lair_controller = LairActionController()
        self._timing_controller: Optional[TimingController] = None
        self._reaction_controller: Optional[ReactionController] = None

    @property
    def recharge_tracker(self) -> RechargeTracker:
        return self._recharge_tracker

    @property
    def lair_controller(self) -> LairActionController:
        return self._lair_controller

    def compile(self, monster_data: dict) -> MonsterStatBlock:
        """从原始怪物数据编译 StatBlock。

        支持的输入格式:
          - data/monsters.py 的 Monster.to_dict() 输出
          - data/monsters_full.py 的 MONSTERS_FULL[name] 字典
          - 自定义完整格式（含 actions 列表）
        """
        name = monster_data.get("name", "Unknown")
        monster_id = monster_data.get("id", str(uuid.uuid4()))

        # 解析感官
        senses_str = monster_data.get("senses", "")
        senses, passive_perception = _parse_senses(senses_str)

        # 解析伤害骰
        damage_dice_str = monster_data.get("damage_dice", "1d6")
        base_dice, modifier = _parse_damage_dice(damage_dice_str)

        # 体型映射
        size_raw = monster_data.get("size", "中型")
        size = _SIZE_MAP.get(size_raw, "Medium")

        # 构建主动作
        main_action = MonsterAction(
            action_id=f"{monster_id}_main_attack",
            name=f"{name}攻击",
            action_type="action",
            attack_bonus=monster_data.get("attack_bonus", 0),
            reach_ft=5,
            damage_dice=base_dice,
            damage_type=monster_data.get("damage_type", "slashing"),
            damage_modifier=modifier,
        )

        # 如果有额外动作定义
        extra_actions: List[MonsterAction] = [main_action]
        bonus_actions: List[MonsterAction] = []
        reactions: List[MonsterAction] = []
        legendary_actions: List[dict] = []
        recharge_abilities: List[dict] = []
        lair_actions: List[dict] = []

        # 解析自定义动作列表
        for act_data in monster_data.get("actions", []):
            act = self._compile_action(act_data, monster_id)
            if act.action_type == "bonus_action":
                bonus_actions.append(act)
            elif act.action_type == "reaction":
                reactions.append(act)
            else:
                extra_actions.append(act)

        # 解析充能动作
        for recharge_data in monster_data.get("recharge_abilities", []):
            recharge_abilities.append(recharge_data)
            act = self._compile_action(recharge_data, monster_id)
            extra_actions.append(act)

        # 解析传奇动作
        legendary_actions = list(monster_data.get("legendary_actions", []))
        lair_actions = list(monster_data.get("lair_actions", []))

        stat_block = MonsterStatBlock(
            monster_id=monster_id,
            name=name,
            size=size,
            creature_type=monster_data.get("creature_type", ""),
            cr=monster_data.get("cr", 0),
            abilities=monster_data.get("abilities", {}),
            hp=monster_data.get("hp", monster_data.get("hp_max", 0)),
            hp_formula=monster_data.get("hp_formula", ""),
            ac=monster_data.get("ac", 10),
            speed_ft=monster_data.get("speed", 30),
            senses=senses,
            passive_perception=passive_perception,
            damage_immunities=list(monster_data.get("damage_immunities", [])),
            damage_resistances=list(monster_data.get("damage_resistances", [])),
            damage_vulnerabilities=list(monster_data.get("damage_vulnerabilities", [])),
            condition_immunities=list(monster_data.get("condition_immunities", [])),
            actions=extra_actions,
            bonus_actions=bonus_actions,
            reactions=reactions,
            legendary_actions=legendary_actions,
            legendary_resistance_count=monster_data.get("legendary_resistance_count", 0),
            legendary_action_points=monster_data.get("legendary_action_points", 0),
            traits=list(monster_data.get("traits", [])),
            spellcasting=monster_data.get("spellcasting"),
            recharge_abilities=recharge_abilities,
            lair_actions=lair_actions,
            lair_initiative_count=monster_data.get("lair_initiative_count", 20),
        )

        # 注册充能动作
        for ra in recharge_abilities:
            ability_id = ra.get("ability_id", ra.get("action_id", ""))
            if ability_id:
                self._recharge_tracker.register(stat_block.monster_id, ability_id)

        # 注册巢穴
        if lair_actions and stat_block.monster_id:
            self._lair_controller.register_lair(
                lair_id=stat_block.monster_id,
                initiative_count=stat_block.lair_initiative_count,
                actions=lair_actions,
            )

        return stat_block

    def compile_from_existing(self, monster_name: str) -> Optional[MonsterStatBlock]:
        """从现有 data/monsters.py 或 data/monsters_full.py 编译。"""
        # 先查 monsters_full
        try:
            from .monsters_full import MONSTERS_FULL
            if monster_name in MONSTERS_FULL:
                return self.compile(MONSTERS_FULL[monster_name])
        except ImportError:
            pass

        # 再查 monsters
        try:
            from .monsters import MONSTERS
            if monster_name in MONSTERS:
                m = MONSTERS[monster_name]
                if hasattr(m, "to_dict"):
                    return self.compile(m.to_dict())
                return self.compile(m)
        except ImportError:
            pass

        return None

    def get_valid_actions(self, stat_block: MonsterStatBlock, context: dict) -> List[MonsterAction]:
        """获取当前上下文中怪物可执行的合法动作。

        context 可包含:
          - action_type: "action"/"bonus_action"/"reaction"
          - has_used_action: bool (本回合是否已使用动作)
          - target_in_reach: bool (目标是否在触及范围内)
          - is_ranged_possible: bool (是否可进行远程攻击)
        """
        action_type = context.get("action_type", "action")
        has_used_action = context.get("has_used_action", False)

        if action_type == "bonus_action":
            candidates = stat_block.bonus_actions
        elif action_type == "reaction":
            candidates = stat_block.reactions
        elif action_type == "legendary":
            # 传奇动作需要传奇点数
            if stat_block.legendary_action_points <= 0:
                return []
            return [MonsterAction(**la) if isinstance(la, dict) else la
                    for la in stat_block.legendary_actions]
        else:
            candidates = stat_block.actions

        valid: List[MonsterAction] = []
        for action in candidates:
            # 检查每回合使用次数
            if action.uses_per_turn == 0:
                continue
            # 如果已使用动作且该动作不是 bonus_action/reaction
            if has_used_action and action.action_type == "action":
                continue
            # 检查射程
            target_dist = context.get("target_distance_ft", 5)
            if action.range_ft > 0:
                # 远程攻击
                if target_dist > action.range_ft:
                    continue
            else:
                # 近战攻击
                if target_dist > action.reach_ft:
                    continue
            valid.append(action)

        return valid

    def execute_action(
        self,
        stat_block: MonsterStatBlock,
        action: MonsterAction,
        target_id: str,
        context: dict,
    ) -> List[dict]:
        """通过统一引擎执行怪物动作。

        使用 AttackSequence 系统执行攻击动作，返回事件列表。
        """
        events: List[dict] = []

        # 构建 AttackPlan
        plan = AttackPlan(
            attacker_id=stat_block.monster_id,
            target_id=target_id,
            weapon_name=action.name,
            attack_modifier=action.attack_bonus,
            damage_dice=action.damage_dice,
            damage_modifier=action.damage_modifier,
            damage_type=action.damage_type,
            is_ranged=action.range_ft > 0,
            range_ft=float(action.range_ft),
            target_ac=context.get("target_ac", 10),
        )

        # 使用 AttackSequence 执行
        seq = AttackSequence(attacker_id=stat_block.monster_id)
        result = seq.execute_sub_attack(plan)

        events.append({
            "type": "monster_attack",
            "attacker_id": stat_block.monster_id,
            "target_id": target_id,
            "action_name": action.name,
            "attack_roll": result.attack_roll,
            "total_attack": result.total_attack,
            "is_hit": result.is_hit,
            "is_crit": result.is_crit,
            "damage": result.damage_total,
            "damage_type": result.damage_type,
        })

        # 处理特殊效果
        for effect in action.special_effects:
            events.append({
                "type": "special_effect",
                "effect": effect,
                "target_id": target_id,
            })

        # 通过 TimingController 触发时序事件
        if self._timing_controller is not None:
            timing_events = self._timing_controller.trigger(
                TimingPoint.AFTER_DAMAGE,
                {"attacker_id": stat_block.monster_id, "target_id": target_id, "action": action},
            )
            events.extend(timing_events)

        return events

    def open_legendary_window(self, stat_block: MonsterStatBlock, trigger_context: dict) -> Optional[ReactionWindow]:
        """为传奇动作打开反应窗口。

        在其他生物回合结束后调用。
        """
        if stat_block.legendary_action_points <= 0 or not stat_block.legendary_actions:
            return None
        if self._reaction_controller is None:
            self._reaction_controller = ReactionController()

        options = []
        for la in stat_block.legendary_actions:
            cost = la.get("cost", 1) if isinstance(la, dict) else 1
            if cost <= stat_block.legendary_action_points:
                options.append(ReactionOption(
                    reaction_type=ReactionType.CUSTOM,
                    entity_id=stat_block.monster_id,
                    ability_name=la.get("name", "") if isinstance(la, dict) else "",
                    cost="legendary_action",
                    metadata={"cost": cost, "action_data": la},
                ))

        if not options:
            return None

        window = self._reaction_controller.open(
            trigger_event="legendary_action_window",
            context=trigger_context,
            eligible_reactors=[stat_block.monster_id],
            reactions=options,
            controller_id=stat_block.monster_id,
        )
        return window

    def use_legendary_resistance(self, stat_block: MonsterStatBlock) -> bool:
        """使用传奇抗性（豁免失败后替换为成功）。

        返回是否成功使用。
        """
        if stat_block.legendary_resistance_count <= 0:
            return False
        stat_block.legendary_resistance_count -= 1
        return True

    def _compile_action(self, act_data: dict, monster_id: str) -> MonsterAction:
        """从字典编译单个动作。"""
        dice_str = act_data.get("damage_dice", "1d6")
        base_dice, modifier = _parse_damage_dice(dice_str)
        return MonsterAction(
            action_id=act_data.get("action_id", str(uuid.uuid4())),
            name=act_data.get("name", ""),
            action_type=act_data.get("action_type", "action"),
            attack_bonus=act_data.get("attack_bonus", 0),
            reach_ft=act_data.get("reach_ft", 5),
            range_ft=act_data.get("range_ft", 0),
            damage_dice=base_dice,
            damage_type=act_data.get("damage_type", "slashing"),
            damage_modifier=act_data.get("damage_modifier", modifier),
            special_effects=act_data.get("special_effects", []),
            uses_per_turn=act_data.get("uses_per_turn", -1),
            description=act_data.get("description", ""),
        )
