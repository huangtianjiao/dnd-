"""据点管理系统 — DMG 第八章 据点。

规则依据: 城主指南2024/8.据点/
  - 据点.htm                    据点总论
  - 1.建立一个据点.htm          建立流程（5级获得据点）
  - 2.据点回合.htm              据点回合机制（每7天一次）
  - 3.据点地图/基础设施.htm     基础设施
  - 3.据点地图/据点地图.htm     据点地图总论（防御墙/合并据点/设施空间）
  - 3.据点地图/特色设施/        25种特色设施
  - 4.据点事件.htm              据点随机事件表
  - 5.失去据点.htm              失去据点条件

本模块提供:
  - Stronghold dataclass:       据点状态
  - create_stronghold():        建立据点
  - build_facility():           建设设施（扣金币+建造时间）
  - run_stronghold_turn():      执行据点回合（收入/支出/事件触发）
  - trigger_event():            触发据点事件
  - lose_stronghold():          失去据点
"""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from typing import Any

from ..data.strongholds import (
    ADD_BASIC_FACILITY_COST,
    BASIC_FACILITIES,
    ENLARGE_FACILITY_COST_GP,
    FacilitySpace,
    OrderType,
    StrongholdEvent,
    StrongholdType,
    get_event_by_roll,
    get_facility,
    get_facility_count_for_level,
    list_facilities_by_level,
)

# ──────────────────────────────────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class FacilityInstance:
    """据点内一个特色设施的实例。

    Attributes:
        facility_name: 设施中文名(对应FACILITIES的key)
        space: 当前空间大小
        hirelings_current: 当前雇员数量
        closed: 是否因事件关闭(下个据点回合修复)
        enlarged: 是否已扩大为庞大设施
    """
    facility_name: str
    space: FacilitySpace = FacilitySpace.SPACIOUS
    hirelings_current: int = 1
    closed: bool = False
    enlarged: bool = False


@dataclass
class BasicFacilityInstance:
    """据点内一个基础设施的实例。

    Attributes:
        name: 基础设施名称(卧室/餐厅/客厅/庭院/厨房/储藏室)
        space: 空间大小(狭窄或宽敞)
    """
    name: str
    space: FacilitySpace = FacilitySpace.CRAMPED


@dataclass
class Defender:
    """据点卫兵。

    规则: DMG第八章 §4 据点事件 — 攻击
    每个据点可以拥有多个据点卫兵(Bastion Defender)，
    他们的任务是在据点遭受攻击时保护据点。
    """
    defender_id: str
    name: str = "据点卫兵"
    source: str = "兵营"   # 来源设施


@dataclass
class Stronghold:
    """据点状态 — 规则: DMG第八章 据点

    Attributes:
        stronghold_id: 据点唯一ID
        campaign_id: 所属战役ID
        owner_character_id: 拥有者角色ID
        owner_name: 拥有者名称
        owner_level: 拥有者等级
        name: 据点名称
        stronghold_type: 据点类型(塔楼/城堡/神殿/公会会所/要塞)
        treasury_gp: 金库中的金币
        facilities: 已拥有的特色设施实例列表
        basic_facilities: 已拥有的基础设施实例列表
        defenders: 据点卫兵列表
        turn_count: 已执行的据点回合数
        neglect_count: 连续未下达指令的据点回合数
        active: 据点是否仍然活跃(未被放弃/毁灭)
        log: 据点事件日志(最近的事件描述列表)
    """
    stronghold_id: str
    campaign_id: int
    owner_character_id: int
    owner_name: str
    owner_level: int
    name: str
    stronghold_type: StrongholdType
    treasury_gp: float = 0.0
    facilities: list[FacilityInstance] = field(default_factory=list)
    basic_facilities: list[BasicFacilityInstance] = field(default_factory=list)
    defenders: list[Defender] = field(default_factory=list)
    turn_count: int = 0
    neglect_count: int = 0
    active: bool = True
    log: list[str] = field(default_factory=list)

    def add_log(self, message: str) -> None:
        """添加一条日志，保留最近50条。"""
        self.log.append(message)
        if len(self.log) > 50:
            self.log = self.log[-50:]


# ──────────────────────────────────────────────────────────────────────────
# 结果数据结构
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class Result:
    """通用操作结果。"""
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class TurnResult:
    """据点回合执行结果。

    规则: DMG第八章 §2 据点回合
    每经过7天游戏时间进行一次据点回合。
    在据点回合中，角色可以向特色设施下达指令，
    或者对整个据点下达维护指令。
    """
    success: bool
    turn_number: int
    income_gp: float = 0.0
    expense_gp: float = 0.0
    events: list[StrongholdEvent] = field(default_factory=list)
    defenders_lost: int = 0
    facilities_closed: list[str] = field(default_factory=list)
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class EventResult:
    """据点事件触发结果。"""
    event: StrongholdEvent
    d100_roll: int
    effects: dict[str, Any] = field(default_factory=dict)
    message: str = ""


# ──────────────────────────────────────────────────────────────────────────
# 核心函数
# ──────────────────────────────────────────────────────────────────────────

def create_stronghold(
    campaign_id: int,
    owner_character_id: int,
    owner_name: str,
    owner_level: int,
    name: str,
    stronghold_type: StrongholdType,
    initial_gold: float = 0.0,
    rng: random.Random | None = None,
) -> Stronghold:
    """建立据点。

    规则: DMG第八章 §1 建立一个据点
      - 角色达到5级时获得据点
      - 每个据点最初拥有两个基础(免费)设施：
        一个狭窄设施、一个宽敞设施
      - 角色的据点最初拥有两个特色设施，
        由角色选择但必须满足获取其设施的先决条件

    Args:
        campaign_id: 战役ID
        owner_character_id: 拥有者角色ID
        owner_name: 拥有者名称
        owner_level: 拥有者等级(需>=5)
        name: 据点名称
        stronghold_type: 据点类型
        initial_gold: 初始金币
        rng: 随机数生成器(测试用)

    Returns:
        新建的Stronghold对象

    Raises:
        ValueError: 如果等级<5
    """
    if owner_level < 5:
        raise ValueError(
            f"据点要求角色等级>=5 (DMG §1)，得到: {owner_level}"
        )

    stronghold = Stronghold(
        stronghold_id=f"sh_{uuid.uuid4().hex[:12]}",
        campaign_id=campaign_id,
        owner_character_id=owner_character_id,
        owner_name=owner_name,
        owner_level=owner_level,
        name=name,
        stronghold_type=stronghold_type,
        treasury_gp=initial_gold,
    )

    # 赠送两个基础(免费)设施：一个狭窄、一个宽敞
    # 规则: DMG第八章 §3 基础设施
    stronghold.basic_facilities.append(
        BasicFacilityInstance(name="卧室", space=FacilitySpace.CRAMPED)
    )
    stronghold.basic_facilities.append(
        BasicFacilityInstance(name="厨房", space=FacilitySpace.SPACIOUS)
    )

    stronghold.add_log(
        f"据点 '{name}' 建立。类型: {stronghold_type.value}。"
        f"初始基础设施: 卧室(狭窄)、厨房(宽敞)。"
    )

    return stronghold


def add_special_facility(
    stronghold: Stronghold,
    facility_name: str,
) -> Result:
    """向据点添加一个特色设施。

    规则: DMG第八章 §3 特色设施详述
      - 每个特色设施都标有一个等级
      - 角色必须达到该等级或更高才能获取该设施
      - 每个特色设施只能被选择一次，除非其描述中另有说明
      - 角色的据点最初拥有两个特色设施

    Args:
        stronghold: 据点对象
        facility_name: 要添加的特色设施名称

    Returns:
        Result对象，包含成功/失败信息
    """
    try:
        facility = get_facility(facility_name)
    except KeyError as e:
        return Result(success=False, message=str(e))

    # 检查等级要求
    if stronghold.owner_level < facility.level:
        return Result(
            success=False,
            message=(
                f"角色等级{stronghold.owner_level}不足，"
                f"设施'{facility_name}'要求等级{facility.level}。"
                f"(DMG §3 特色设施)"
            ),
        )

    # 检查先决条件
    if facility.prerequisite and facility.prerequisite != "无":
        # 先决条件检查由调用方处理(需要角色特性信息)
        # 这里仅记录警告
        pass

    # 检查是否已拥有该设施(非多重允许)
    existing_count = sum(
        1 for f in stronghold.facilities
        if f.facility_name == facility_name
    )
    if existing_count > 0 and not facility.multiple_allowed:
        return Result(
            success=False,
            message=(
                f"据点已拥有设施'{facility_name}'，"
                f"且该设施不允许拥有多个。(DMG §3 特色设施)"
            ),
        )

    # 检查特色设施总数是否超过等级限制
    max_facilities = get_facility_count_for_level(stronghold.owner_level)
    if len(stronghold.facilities) >= max_facilities:
        return Result(
            success=False,
            message=(
                f"据点已拥有{len(stronghold.facilities)}个特色设施，"
                f"达到等级{stronghold.owner_level}的上限{max_facilities}。"
                f"(DMG §3 特色设施获取表)"
            ),
        )

    # 添加设施
    instance = FacilityInstance(
        facility_name=facility_name,
        space=facility.space,
        hirelings_current=facility.hirelings,
    )
    stronghold.facilities.append(instance)

    msg = (
        f"特色设施'{facility_name}'({facility.name_en})已加入据点。"
        f"空间: {facility.space.value}，雇员: {facility.hirelings}人。"
    )
    stronghold.add_log(msg)

    return Result(
        success=True,
        message=msg,
        data={
            "facility_name": facility_name,
            "space": facility.space.value,
            "hirelings": facility.hirelings,
            "order": facility.order.value,
        },
    )


def build_facility(
    stronghold: Stronghold,
    facility_name: str,
    is_basic: bool = False,
    target_space: FacilitySpace | None = None,
) -> Result:
    """建设设施（扣金币+建造时间）。

    规则: DMG第八章 §3 增添基础设施 / 特色设施详述
      - 基础设施增添价格表:
        狭窄500GP/20天，宽敞1000GP/45天，庞大3000GP/125天
      - 特色设施无法被直接购买；角色通过升级来获取
      - 但特色设施可以被扩大(花费2000GP扩大为庞大设施)

    本函数处理两种情况:
      1. is_basic=True: 增添一个基础设施(扣金币+建造时间)
      2. is_basic=False: 扩大一个已有的特色设施(扣2000GP)

    Args:
        stronghold: 据点对象
        facility_name: 设施名称
        is_basic: 是否为基础设施
        target_space: 目标空间大小(仅基础设施增添时使用)

    Returns:
        Result对象，包含花费和建造时间信息
    """
    if is_basic:
        # 增添基础设施
        if facility_name not in BASIC_FACILITIES:
            return Result(
                success=False,
                message=f"'{facility_name}'不是有效的基础设施名称。",
            )

        if target_space is None:
            target_space = FacilitySpace.CRAMPED

        cost_gp, build_days = ADD_BASIC_FACILITY_COST[target_space]

        if stronghold.treasury_gp < cost_gp:
            return Result(
                success=False,
                message=(
                    f"金库金币不足: 需要{cost_gp}GP，"
                    f"当前{stronghold.treasury_gp}GP。"
                ),
            )

        stronghold.treasury_gp -= cost_gp

        # 添加基础设施实例
        from ..data.strongholds import BasicFacilityInstance
        stronghold.basic_facilities.append(
            BasicFacilityInstance(
                name=facility_name,
                space=target_space,
            )
        )

        msg = (
            f"基础设施'{facility_name}'({target_space.value})建造开始。"
            f"花费: {cost_gp}GP，建造时间: {build_days}天。"
            f"剩余金币: {stronghold.treasury_gp}GP。"
        )
        stronghold.add_log(msg)

        return Result(
            success=True,
            message=msg,
            data={
                "cost_gp": cost_gp,
                "build_days": build_days,
                "remaining_gp": stronghold.treasury_gp,
            },
        )

    # 扩大特色设施
    facility_instance = None
    for f in stronghold.facilities:
        if f.facility_name == facility_name:
            facility_instance = f
            break

    if facility_instance is None:
        return Result(
            success=False,
            message=f"据点未拥有特色设施'{facility_name}'。",
        )

    if facility_instance.enlarged:
        return Result(
            success=False,
            message=f"特色设施'{facility_name}'已被扩大，无法再次扩大。",
        )

    # 检查该设施是否支持扩大
    facility_data = get_facility(facility_name)
    if not facility_data.can_enlarge:
        return Result(
            success=False,
            message=f"特色设施'{facility_name}'不支持扩大。",
        )

    cost_gp = ENLARGE_FACILITY_COST_GP  # 2000GP

    if stronghold.treasury_gp < cost_gp:
        return Result(
            success=False,
            message=(
                f"金库金币不足: 需要{cost_gp}GP，"
                f"当前{stronghold.treasury_gp}GP。"
            ),
        )

    stronghold.treasury_gp -= cost_gp
    facility_instance.enlarged = True
    facility_instance.space = FacilitySpace.VAST

    msg = (
        f"特色设施'{facility_name}'已扩大为庞大设施。"
        f"花费: {cost_gp}GP，剩余金币: {stronghold.treasury_gp}GP。"
    )
    stronghold.add_log(msg)

    return Result(
        success=True,
        message=msg,
        data={
            "cost_gp": cost_gp,
            "remaining_gp": stronghold.treasury_gp,
        },
    )


def run_stronghold_turn(
    stronghold: Stronghold,
    order_type: OrderType = OrderType.MAINTAIN,
    facility_name: str | None = None,
    rng: random.Random | None = None,
) -> TurnResult:
    """执行据点回合。

    规则: DMG第八章 §2 据点回合
      - 默认情况下，游戏内每经过7天时间，就会进行一次据点回合
      - 在据点回合中，位于自己的据点内的角色可以向一个或更多
        特色设施下达特殊的指令——这被称为据点指令
      - 维护指令是特殊的，该指令下达给整个据点而非特定设施
      - 每当维护指令被下达时，DM都将在据点事件表格上掷骰一次

    Args:
        stronghold: 据点对象
        order_type: 指令类型(默认为维护)
        facility_name: 目标特色设施名称(非维护指令时需要)
        rng: 随机数生成器(测试用)

    Returns:
        TurnResult对象，包含回合执行结果
    """
    if not stronghold.active:
        return TurnResult(
            success=False,
            turn_number=stronghold.turn_count,
            message="据点已不活跃(被放弃/毁灭)，无法执行回合。",
        )

    if rng is None:
        rng = random.Random()

    result = TurnResult(
        success=True,
        turn_number=stronghold.turn_count + 1,
    )

    # 处理指令
    if order_type == OrderType.MAINTAIN:
        # 维护指令：掷d100决定据点事件
        # 规则: DMG第八章 §4 据点事件
        event_result = trigger_event(stronghold, rng=rng)
        result.events.append(event_result.event)
        result.details["event"] = {
            "name": event_result.event.name,
            "d100_roll": event_result.d100_roll,
            "effects": event_result.effects,
        }

        # 处理事件效果
        _apply_event_effects(stronghold, event_result, result, rng=rng)

        # 维护指令会增加疏于照顾计数器? 不，维护指令本身就是一种指令
        # 疏于照顾是指连续不下达指令
        stronghold.neglect_count = 0

    elif facility_name is not None:
        # 向特定设施下达指令
        facility_instance = None
        for f in stronghold.facilities:
            if f.facility_name == facility_name:
                facility_instance = f
                break

        if facility_instance is None:
            return TurnResult(
                success=False,
                turn_number=stronghold.turn_count,
                message=f"据点未拥有特色设施'{facility_name}'。",
            )

        if facility_instance.closed:
            return TurnResult(
                success=False,
                turn_number=stronghold.turn_count,
                message=f"特色设施'{facility_name}'已关闭，无法使用。",
            )

        # 执行指令(简化处理：记录指令并产生一些效果)
        facility_data = get_facility(facility_name)
        if facility_data.order != order_type:
            return TurnResult(
                success=False,
                turn_number=stronghold.turn_count,
                message=(
                    f"设施'{facility_name}'不支持'{order_type.value}'指令。"
                    f"支持的指令: {facility_data.order.value}"
                ),
            )

        result.details["order_executed"] = {
            "facility": facility_name,
            "order": order_type.value,
        }
        stronghold.neglect_count = 0

    else:
        # 非维护指令但未指定设施
        return TurnResult(
            success=False,
            turn_number=stronghold.turn_count,
            message="非维护指令需要指定目标特色设施。",
        )

    # 更新回合计数
    stronghold.turn_count += 1

    # 检查疏于照顾
    # 规则: DMG第八章 §5 失去据点 — 疏于照顾
    # 如果角色在连续的据点回合中一直不下达指令，
    # 持续了等同于角色等级的次数，那么据点的雇员会抛弃据点
    if stronghold.neglect_count >= stronghold.owner_level:
        stronghold.active = False
        result.message = (
            f"据点因疏于照顾而被废弃。"
            f"连续{stronghold.neglect_count}个回合未下达指令"
            f"(等于角色等级{stronghold.owner_level})。"
            f"(DMG §5 失去据点)"
        )
        stronghold.add_log(result.message)

    return result


def trigger_event(
    stronghold: Stronghold,
    rng: random.Random | None = None,
) -> EventResult:
    """触发据点事件。

    规则: DMG第八章 §4 据点事件
      - 在一个角色向自己的据点下达维护指令后，
        DM立刻在据点事件表格中掷骰
      - 掷d100，根据结果决定发生什么事件

    Args:
        stronghold: 据点对象
        rng: 随机数生成器(测试用)

    Returns:
        EventResult对象，包含事件信息和效果
    """
    if rng is None:
        rng = random.Random()

    d100_roll = rng.randint(1, 100)
    event = get_event_by_roll(d100_roll)

    effects: dict[str, Any] = {}

    # 根据事件类型计算具体效果
    if event.name == "一切顺利":
        detail_roll = rng.randint(1, 8)
        details_map = {
            1: "事故报告正在减少",
            2: "天花板上的漏水处被修复了",
            3: "没有发现鼠患的痕迹",
            4: "'那家伙'又把眼镜弄丢了",
            5: "你的一位雇员收养了一只流浪狗",
            6: "你收到了朋友写来的一封令人欣喜的信件",
            7: "某些爱开玩笑的人一直在往人们的鞋子里放臭鸡蛋",
            8: "有人声称自己看见了鬼魂",
        }
        effects["detail"] = details_map.get(detail_roll, "")
        effects["detail_roll"] = detail_roll

    elif event.name == "攻击":
        # 投掷6d6; 每有一个骰子丢出1，便有一位据点卫兵死亡
        dice = [rng.randint(1, 6) for _ in range(6)]
        deaths = sum(1 for d in dice if d == 1)
        effects["dice"] = dice
        effects["defender_deaths"] = deaths
        effects["has_defenders"] = len(stronghold.defenders) > 0

    elif event.name == "罪犯雇员":
        bribe = rng.randint(1, 6) * 100
        effects["bribe_amount_gp"] = bribe

    elif event.name == "机不可失":
        effects["cost_gp"] = 500

    elif event.name == "友好的来访者":
        payment = rng.randint(1, 6) * 100
        effects["payment_gp"] = payment

    elif event.name == "客人":
        guest_roll = rng.randint(1, 4)
        guests_map = {
            1: "非常有名的人，暂住7天后给予你一封推荐信",
            2: "寻求庇护的客人，7天后离开前赠予你1d6*100GP作为礼物",
            3: "雇佣兵客人，给予你一位额外的据点卫兵",
            4: "友善的怪物客人(如黄铜龙或树人)，若据点遭受攻击怪物会保护你的据点",
        }
        effects["guest_type"] = guests_map.get(guest_roll, "")
        effects["guest_roll"] = guest_roll

    elif event.name == "失去雇员":
        # 随机选择一个特色设施失去所有雇员
        if stronghold.facilities:
            target_idx = rng.randint(0, len(stronghold.facilities) - 1)
            target_facility = stronghold.facilities[target_idx]
            effects["affected_facility"] = target_facility.facility_name
            effects["lost_all_hirelings"] = True
        else:
            effects["affected_facility"] = None

    elif event.name == "魔法发现":
        effects["item_rarity"] = "非普通(Uncommon)"
        effects["item_type_restriction"] = "药剂(Potion)或卷轴(Scroll)"

    elif event.name == "难民":
        refugee_count = sum(rng.randint(1, 4) for _ in range(2))
        payment = rng.randint(1, 6) * 100
        effects["refugee_count"] = refugee_count
        effects["payment_gp"] = payment

    elif event.name == "援助请求":
        effects["requires_defenders"] = True
        effects["reward_on_success_gp"] = "1d6*100"
        effects["death_threshold"] = 10

    elif event.name == "宝藏":
        treasure_roll = rng.randint(1, 100)
        treasures_map = {
            (1, 40): "投掷25GP艺术品表格",
            (41, 63): "投掷250GP艺术品表格",
            (64, 73): "投掷750GP艺术品表格",
            (74, 75): "投掷2500GP艺术品表格",
            (76, 90): "选择一张普通魔法物品表格(奥秘/武具/器具/圣物)并投掷",
            (91, 98): "选择一张非普通魔法物品表格并投掷",
            (99, 100): "选择一张珍稀魔法物品表格并投掷",
        }
        treasure_desc = ""
        for (lo, hi), desc in treasures_map.items():
            if lo <= treasure_roll <= hi:
                treasure_desc = desc
                break
        effects["treasure_roll"] = treasure_roll
        effects["treasure_description"] = treasure_desc

    msg = f"据点事件: {event.name}({event.name_en}) [d100={d100_roll}]"
    stronghold.add_log(msg)

    return EventResult(
        event=event,
        d100_roll=d100_roll,
        effects=effects,
        message=msg,
    )


def _apply_event_effects(
    stronghold: Stronghold,
    event_result: EventResult,
    turn_result: TurnResult,
    rng: random.Random | None = None,
) -> None:
    """将事件效果应用到据点状态。

    规则: DMG第八章 §4 据点事件 — 各事件结算
    """
    if rng is None:
        rng = random.Random()

    event = event_result.event
    effects = event_result.effects

    if event.name == "攻击":
        deaths = effects.get("defender_deaths", 0)
        has_defenders = effects.get("has_defenders", False)

        if has_defenders and deaths > 0:
            # 移除死亡的卫兵
            actual_deaths = min(deaths, len(stronghold.defenders))
            for _ in range(actual_deaths):
                stronghold.defenders.pop()
            turn_result.defenders_lost = actual_deaths
        elif not has_defenders:
            # 没有卫兵，随机关闭一个特色设施
            open_facilities = [
                f for f in stronghold.facilities if not f.closed
            ]
            if open_facilities:
                target = rng.choice(open_facilities)
                target.closed = True
                turn_result.facilities_closed.append(target.facility_name)

    elif event.name == "罪犯雇员":
        # 如果贿赂，扣金币
        bribe = effects.get("bribe_amount_gp", 0)
        if stronghold.treasury_gp >= bribe:
            stronghold.treasury_gp -= bribe
            turn_result.expense_gp += bribe
        # 否则失去一个雇员(简化处理)

    elif event.name == "机不可失":
        cost = effects.get("cost_gp", 500)
        if stronghold.treasury_gp >= cost:
            stronghold.treasury_gp -= cost
            turn_result.expense_gp += cost
            # 重新掷骰据点事件
            new_event = trigger_event(stronghold, rng=rng)
            turn_result.events.append(new_event.event)
            _apply_event_effects(stronghold, new_event, turn_result, rng=rng)

    elif event.name == "友好的来访者":
        payment = effects.get("payment_gp", 0)
        stronghold.treasury_gp += payment
        turn_result.income_gp += payment

    elif event.name == "失去雇员":
        affected = effects.get("affected_facility")
        if affected:
            for f in stronghold.facilities:
                if f.facility_name == affected:
                    f.closed = True
                    turn_result.facilities_closed.append(affected)
                    break

    elif event.name == "难民":
        payment = effects.get("payment_gp", 0)
        stronghold.treasury_gp += payment
        turn_result.income_gp += payment

    elif event.name == "宝藏":
        # 宝藏价值取决于掷骰结果(简化处理)
        treasure_roll = effects.get("treasure_roll", 0)
        if 1 <= treasure_roll <= 40:
            value = 25
        elif 41 <= treasure_roll <= 63:
            value = 250
        elif 64 <= treasure_roll <= 73:
            value = 750
        elif 74 <= treasure_roll <= 75:
            value = 2500
        else:
            value = 0  # 魔法物品，价值不定
        if value > 0:
            stronghold.treasury_gp += value
            turn_result.income_gp += value


def recruit_defenders(
    stronghold: Stronghold,
    count: int,
    source: str = "兵营",
) -> Result:
    """招募据点卫兵。

    规则: DMG第八章 §3 兵营 — 招募：据点卫兵
      - 每当你对此设施下达招募指令，
        至多四位据点卫兵会被招募到你的据点
      - 招募不会花费任何金钱

    Args:
        stronghold: 据点对象
        count: 要招募的卫兵数量(最多4)
        source: 来源设施名称

    Returns:
        Result对象
    """
    if count > 4:
        return Result(
            success=False,
            message=f"每次招募最多4名卫兵(DMG §3 兵营)，请求: {count}",
        )

    if count <= 0:
        return Result(
            success=False,
            message="招募数量必须大于0。",
        )

    for i in range(count):
        defender = Defender(
            defender_id=f"def_{uuid.uuid4().hex[:8]}",
            name=f"据点卫兵{len(stronghold.defenders) + i + 1}",
            source=source,
        )
        stronghold.defenders.append(defender)

    msg = f"招募了{count}名据点卫兵(来源: {source})。当前卫兵总数: {len(stronghold.defenders)}。"
    stronghold.add_log(msg)

    return Result(
        success=True,
        message=msg,
        data={
            "recruited_count": count,
            "total_defenders": len(stronghold.defenders),
        },
    )


def lose_stronghold(
    stronghold: Stronghold,
    reason: str = "放弃所有权",
) -> Result:
    """失去据点。

    规则: DMG第八章 §5 失去据点
      - 放弃所有权(Divestiture): 角色可以随时放弃自己的据点
      - 疏于照顾(Neglect): 连续不下达指令持续等同于角色等级的次数
      - 彻底毁灭(Ruination): 从万象无常牌抽出废墟卡等

    Args:
        stronghold: 据点对象
        reason: 失去据点的原因

    Returns:
        Result对象
    """
    valid_reasons = ["放弃所有权", "疏于照顾", "彻底毁灭"]
    if reason not in valid_reasons:
        return Result(
            success=False,
            message=f"无效的失去原因: {reason}。可选: {valid_reasons}",
        )

    stronghold.active = False

    msg = (
        f"据点 '{stronghold.name}' 已失去。"
        f"原因: {reason}。"
        f"(DMG §5 失去据点)"
    )
    stronghold.add_log(msg)

    return Result(
        success=True,
        message=msg,
        data={
            "stronghold_id": stronghold.stronghold_id,
            "reason": reason,
            "turns_survived": stronghold.turn_count,
        },
    )


def get_stronghold_status(stronghold: Stronghold) -> dict[str, Any]:
    """获取据点状态摘要。

    Args:
        stronghold: 据点对象

    Returns:
        包含据点状态信息的字典
    """
    return {
        "stronghold_id": stronghold.stronghold_id,
        "campaign_id": stronghold.campaign_id,
        "owner_character_id": stronghold.owner_character_id,
        "owner_name": stronghold.owner_name,
        "owner_level": stronghold.owner_level,
        "name": stronghold.name,
        "stronghold_type": stronghold.stronghold_type.value,
        "treasury_gp": stronghold.treasury_gp,
        "facilities": [
            {
                "name": f.facility_name,
                "space": f.space.value,
                "hirelings": f.hirelings_current,
                "closed": f.closed,
                "enlarged": f.enlarged,
            }
            for f in stronghold.facilities
        ],
        "basic_facilities": [
            {
                "name": bf.name,
                "space": bf.space.value,
            }
            for bf in stronghold.basic_facilities
        ],
        "defenders": len(stronghold.defenders),
        "turn_count": stronghold.turn_count,
        "neglect_count": stronghold.neglect_count,
        "active": stronghold.active,
        "recent_log": stronghold.log[-10:] if stronghold.log else [],
    }


def list_available_facilities(stronghold: Stronghold) -> list[dict[str, Any]]:
    """列出据点当前可添加的特色设施。

    规则: DMG第八章 §3 特色设施详述
      - 角色必须达到设施标注的等级
      - 每个特色设施只能被选择一次(除非描述另有说明)

    Args:
        stronghold: 据点对象

    Returns:
        可添加的特色设施列表(每个元素为包含设施信息的字典)
    """
    owned_names = {f.facility_name for f in stronghold.facilities}
    available = []

    for facility in list_facilities_by_level(stronghold.owner_level):
        already_owned = facility.name in owned_names
        can_add_multiple = facility.multiple_allowed

        if already_owned and not can_add_multiple:
            continue  # 已拥有且不支持多个

        available.append({
            "name": facility.name,
            "name_en": facility.name_en,
            "level": facility.level,
            "space": facility.space.value,
            "hirelings": facility.hirelings,
            "order": facility.order.value,
            "prerequisite": facility.prerequisite,
            "description": facility.description,
            "can_enlarge": facility.can_enlarge,
            "multiple_allowed": facility.multiple_allowed,
        })

    return available
