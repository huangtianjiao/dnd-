"""Phase E 探索流程 — 旅行步调 / 地形 / 觅食 / 导航 / 追踪 / 躲藏 / 遭遇。

依据《城主指南2024》「2.运作游戏/运作探索」与报告§6，实现完整探索流程。
所有数值/骰子由代码执行（ARCHITECTURE §2），LLM 不得臆测。

标注约定：每条规则实现处标注 RULE_SPEC.md 规则点 ID + 原文出处路径
（topics/.../xxx.htm），形成"代码↔规则"双向索引。

主要数据来源：
- 旅行.htm        → 旅行步调表、旅行地形表、觅食/导航/追踪规则
- 使用地图.htm     → 地图类型与地城探索
- 察觉.htm        → 声音传播距离表、户外/海上/水下能见度表
- 探索中的动作.htm  → 搜索/研究/操作动作、轮流行动
- 跟进时间.htm     → 时间尺度（轮/分钟/小时/日）、战斗回合时长
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from ..engine import dice

# ══════════════════════════════════════════════════════════════════════════
# 一、旅行步调表（指南Ch5 / 报告§6）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
# 规则: R-DM-032 特殊移动旅行速率（中速基准，快速×4/3，慢速×2/3）
# ══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TravelPace:
    """旅行步调：每分钟/每小时/每天行进距离 + 游戏效果。

    出处: topics/玩家手册2024/进行游戏/旅行.htm（旅行步调表 + 游戏效果）
    """
    name: str               # 快速/中速/慢速
    per_minute_ft: int      # 每分钟尺数
    per_hour_miles: int     # 每小时英里
    per_day_miles: int      # 每天英里（8小时旅行）
    stealth_disadvantage: bool = False   # 该步调下隐匿（敏捷）检定劣势
    perception_disadvantage: bool = False  # 察觉/生存（感知）检定劣势
    perception_advantage: bool = False    # 察觉/生存（感知）检定优势


# 旅行步调表 + 游戏效果  出处: 玩家手册2024/进行游戏/旅行.htm（旅行步调）
# 规则: R-DM-032 / R-GLS-048 旅行步调效应
#   快速 Fast：感知（察觉或生存）与 敏捷（隐匿）检定均劣势
#   中速 Normal：敏捷（隐匿）检定劣势
#   慢速 Slow：感知（察觉或生存）检定优势
# 距离：快速 400尺/分 4里/时 30里/天；中速 300尺/分 3里/时 24里/天；慢速 200尺/分 2里/时 18里/天
TRAVEL_PACES: dict[str, TravelPace] = {
    "快速": TravelPace(
        name="快速", per_minute_ft=400, per_hour_miles=4, per_day_miles=30,
        stealth_disadvantage=True, perception_disadvantage=True,
        perception_advantage=False,
    ),
    "中速": TravelPace(
        name="中速", per_minute_ft=300, per_hour_miles=3, per_day_miles=24,
        stealth_disadvantage=True, perception_disadvantage=False,
        perception_advantage=False,
    ),
    "慢速": TravelPace(
        name="慢速", per_minute_ft=200, per_hour_miles=2, per_day_miles=18,
        stealth_disadvantage=False, perception_disadvantage=False,
        perception_advantage=True,
    ),
}

# 注：坐骑可在1小时内以双倍步调移动，之后需短休或长休才能再次加速。
# 出处: 玩家手册2024/进行游戏/旅行.htm（旅行步调）


def get_travel_pace(pace_name: str) -> TravelPace:
    """按名称获取旅行步调。

    规则: R-DM-032  出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
    """
    if pace_name not in TRAVEL_PACES:
        raise ValueError(f"未知旅行步调 {pace_name!r}，可选: {list(TRAVEL_PACES)}")
    return TRAVEL_PACES[pace_name]


# ══════════════════════════════════════════════════════════════════════════
# 二、旅行地形表（R-DM-033）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
# 字段: max_pace(最快步调), encounter_distance(遭遇距离表达式),
#       forage_dc(觅食DC), nav_dc(导航DC), search_dc(搜索DC)
# ══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TerrainParams:
    """旅行地形参数。

    规则: R-DM-033 旅行地形表
    出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
    """
    terrain: str                # 地形名
    max_pace: str               # 最快步调: 快速/中速/慢速/特殊
    encounter_distance: str     # 遭遇距离骰表达式，如 "2d8x10"
    forage_dc: int              # 觅食DC
    nav_dc: int                 # 导航DC
    search_dc: int              # 搜索DC


# 旅行地形表  出处: 旅行.htm  规则: R-DM-033
TERRAIN_TABLE: dict[str, TerrainParams] = {
    "寒带": TerrainParams("寒带", "快速", "6d6x10", 20, 10, 10),
    "海岸": TerrainParams("海岸", "中速", "2d10x10", 10, 5, 15),
    "荒漠": TerrainParams("荒漠", "中速", "6d6x10", 20, 10, 10),
    "森林": TerrainParams("森林", "中速", "2d8x10", 10, 15, 15),
    "草原": TerrainParams("草原", "快速", "6d6x10", 15, 5, 15),
    "丘陵": TerrainParams("丘陵", "中速", "2d10x10", 15, 10, 15),
    "山地": TerrainParams("山地", "慢速", "4d10x10", 20, 15, 20),
    "沼泽": TerrainParams("沼泽", "慢速", "2d8x10", 10, 15, 20),
    "幽暗地域": TerrainParams("幽暗地域", "中速", "2d6x10", 20, 10, 20),
    "城市": TerrainParams("城市", "中速", "2d6x10", 20, 15, 15),
    "水路": TerrainParams("水路", "特殊", "6d6x10", 15, 10, 15),
}


def terrain_params(terrain: str) -> TerrainParams:
    """查询旅行地形参数。

    规则: R-DM-033 旅行地形表
    出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
    """
    if terrain not in TERRAIN_TABLE:
        raise ValueError(f"未知地形 {terrain!r}，可选: {list(TERRAIN_TABLE)}")
    return TERRAIN_TABLE[terrain]


# ══════════════════════════════════════════════════════════════════════════
# 三、光照与遮蔽（指南Ch5）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm
# ══════════════════════════════════════════════════════════════════════════

# 光照等级  出处: 察觉.htm
LIGHT_BRIGHT = "明亮光照"      # 白昼、火把、提灯 → 正常视物
LIGHT_DIM = "微光光照"         # 黎明/黄昏、满月月光 → 轻度遮蔽
LIGHT_DARK = "黑暗"            # 夜晚户外、无灯地城 → 重度遮蔽

# 遮蔽等级 → 对基于视觉的察觉检定的影响
# 出处: 察觉.htm
OBSCUREMENT_EFFECTS: dict[str, str] = {
    "无遮蔽": "正常视物",
    "轻度遮蔽": "基于视觉的察觉检定劣势",
    "重度遮蔽": "形成目盲状态（尝试看穿时）",
}


def light_obscurement(light_level: str) -> str:
    """根据光照等级返回遮蔽等级。

    规则: R-DM-027 户外能见度（轻度遮蔽降低能见度）
    出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm
    """
    mapping = {
        LIGHT_BRIGHT: "无遮蔽",
        LIGHT_DIM: "轻度遮蔽",
        LIGHT_DARK: "重度遮蔽",
    }
    if light_level not in mapping:
        raise ValueError(f"未知光照等级 {light_level!r}")
    return mapping[light_level]


# ══════════════════════════════════════════════════════════════════════════
# 四、特殊感官（指南Ch5）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm
# ══════════════════════════════════════════════════════════════════════════

# 特殊感官标识  出处: 察觉.htm
SENSE_DARKVISION = "黑暗视觉"      # 微光/黑暗中可看到如同微光的景象，范围通常60尺
SENSE_TREMORSENSE = "震颤感知"     # 可感知震动，无视视觉遮蔽
SENSE_TRUESIGHT = "真实视觉"       # 可看穿一切幻象和遮蔽
SENSE_BLINDSIGHT = "盲视"          # 无需视觉即可感知周围环境


def effective_obscurement(obscurement: str, senses: set[str]) -> str:
    """考虑特殊感官后，生物实际受到的遮蔽影响。

    规则: R-DM-026 声音传播距离 / R-DM-027 户外能见度（特殊感官绕过遮蔽）
    出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm

    - 真实视觉：看穿一切遮蔽 → 无遮蔽
    - 盲视：无需视觉 → 无遮蔽（不受光照影响）
    - 黑暗视觉：在黑暗中视为微光 → 重度遮蔽降为轻度遮蔽
    - 震颤感知：无视视觉遮蔽（仅对地面震动有效）
    """
    if SENSE_TRUESIGHT in senses or SENSE_BLINDSIGHT in senses:
        return "无遮蔽"
    if obscurement == "重度遮蔽" and SENSE_DARKVISION in senses:
        return "轻度遮蔽"
    return obscurement


# ══════════════════════════════════════════════════════════════════════════
# 五、声音传播距离表（R-DM-026）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm
# ══════════════════════════════════════════════════════════════════════════

# 噪音等级 → 听力范围（尺）
# 出处: 察觉.htm  规则: R-DM-026
NOISE_DISTANCE: dict[str, str] = {
    "尽量保持安静": "2d6x5",     # 2d6×5 尺
    "正常噪音等级": "2d6x10",    # 2d6×10 尺
    "非常响": "2d6x50",          # 2d6×50 尺
}


def audible_distance(noise_level: str) -> int:
    """根据噪音等级掷骰确定听力范围（尺）。

    规则: R-DM-026 声音传播距离
    出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm
    """
    if noise_level not in NOISE_DISTANCE:
        raise ValueError(f"未知噪音等级 {noise_level!r}，可选: {list(NOISE_DISTANCE)}")
    expr = NOISE_DISTANCE[noise_level]
    # 解析 "NdMxK" 格式
    parts = expr.split("x")
    roll_expr = parts[0]  # e.g. "2d6"
    multiplier = int(parts[1]) if len(parts) > 1 else 1
    r = dice.roll_dice(roll_expr)
    return r.total * multiplier


# ══════════════════════════════════════════════════════════════════════════
# 六、能见度表（R-DM-027 / R-DM-028 / R-DM-029）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm
# ══════════════════════════════════════════════════════════════════════════

def outdoor_visibility(weather: str = "晴朗", vantage: bool = False) -> int:
    """户外能见度（英里）。

    规则: R-DM-027 户外能见度
    出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm

    - 晴朗日约2英里；高处俯瞰40英里
    - 下雨时最大能见度降到1英里
    - 雾气使其降到100-300尺
    """
    if weather == "雾":
        return dice.roll_dice("1d3").total * 100 + 0  # 100-300尺，转成英尺整数
    if weather == "雨":
        return 1  # 1英里
    # 晴朗/正常
    return 40 if vantage else 2


def sea_visibility(sky_condition: str) -> int:
    """海上能见度（英里）。

    规则: R-DM-028 海上能见度
    出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm

    - 晴朗平静海面瞭望台能见10英里
    - 阴沉天空能见度减半（5英里）
    """
    if sky_condition == "晴朗":
        return 10
    if sky_condition == "阴沉":
        return 5
    raise ValueError(f"未知天空状况 {sky_condition!r}，可选: 晴朗/阴沉")


def underwater_encounter_distance(clarity: str, lighting: str) -> int:
    """水下遭遇距离（尺）。

    规则: R-DM-029 水下遭遇距离
    出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm

    | 能见度 | 遭遇距离 |
    | 清澈水体，明亮光照 | 60尺 |
    | 清澈水体，微光光照 | 30尺 |
    | 浑浊水体或黑暗 | 10尺 |
    """
    if clarity == "浑浊" or lighting == LIGHT_DARK:
        return 10
    if clarity == "清澈" and lighting == LIGHT_BRIGHT:
        return 60
    if clarity == "清澈" and lighting == LIGHT_DIM:
        return 30
    raise ValueError(f"未知水体清澈度/光照组合: clarity={clarity!r}, lighting={lighting!r}")


# ══════════════════════════════════════════════════════════════════════════
# 七、天气表（R-DM-030）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class Weather:
    """天气状态。"""
    temperature: str = "本季正常水准"   # 温度描述
    temp_delta_f: int = 0               # 温度变化（华氏度）
    wind: str = "无"                    # 风力
    rain: str = "无"                    # 降雨量


def weather_roll() -> Weather:
    """投掷三次1d20确定温度、风力、降雨量。

    规则: R-DM-030 天气表
    出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm

    温度: 1-14正常, 15-17冷1d4×10°F, 18-20热1d4×10°F
    风: 1-12无, 13-17轻, 18-20强
    雨: 1-12无, 13-17轻, 18-20重
    """
    temp_roll = dice.roll_die(20)
    wind_roll = dice.roll_die(20)
    rain_roll = dice.roll_die(20)

    w = Weather()

    # 温度
    if temp_roll <= 14:
        w.temperature = "本季正常水准"
        w.temp_delta_f = 0
    elif temp_roll <= 17:
        delta = dice.roll_dice("1d4").total * 10
        w.temperature = f"变冷 {delta}°F"
        w.temp_delta_f = -delta
    else:  # 18-20
        delta = dice.roll_dice("1d4").total * 10
        w.temperature = f"变热 {delta}°F"
        w.temp_delta_f = delta

    # 风力
    if wind_roll <= 12:
        w.wind = "无"
    elif wind_roll <= 17:
        w.wind = "轻风"
    else:
        w.wind = "强风"

    # 降雨量
    if rain_roll <= 12:
        w.rain = "无"
    elif rain_roll <= 17:
        w.rain = "轻度降雨或降雪"
    else:
        w.rain = "重度降雨或降雪"

    return w


# ══════════════════════════════════════════════════════════════════════════
# 八、延长旅行力竭（R-DM-031）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
# ══════════════════════════════════════════════════════════════════════════

def extended_travel_exhaustion(extra_hours: int, con_save_total: int) -> bool:
    """超8小时旅行每额外1小时体质豁免，DC=10+额外小时数，失败+1级力竭。

    规则: R-DM-031 延长旅行力竭
    出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm

    参数:
        extra_hours: 超出8小时的额外旅行小时数（本次判定的当前累计小时）
        con_save_total: 本次体质豁免的总计值
    返回:
        (gained_exhaustion: bool) 是否增加力竭等级
    """
    dc = 10 + extra_hours
    return con_save_total < dc


# ══════════════════════════════════════════════════════════════════════════
# 九、特殊移动旅行速率（R-DM-032）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
# ══════════════════════════════════════════════════════════════════════════

def special_travel_rate(speed: int, pace: str, travel_hours: int = 8) -> int:
    """将团队速度换算为旅行速率（英里/天）。

    规则: R-DM-032 特殊移动旅行速率
    出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm

    公式:
        英里/小时 = 速度 ÷ 10
        英里/天（中速）= 英里/小时 × 旅行小时数（通常8）
        快速步调 = 英里/天 × 4/3（向下取整）
        慢速步调 = 英里/天 × 2/3（向下取整）
    """
    mph = speed / 10
    miles_per_day = mph * travel_hours  # 中速基准
    if pace == "快速":
        return math.floor(miles_per_day * 4 / 3)
    if pace == "慢速":
        return math.floor(miles_per_day * 2 / 3)
    # 中速
    return math.floor(miles_per_day)


# ══════════════════════════════════════════════════════════════════════════
# 十、路况良好提速（R-DM-034）/ 慢速成员拖累（R-DM-035）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
# ══════════════════════════════════════════════════════════════════════════

# 步调升降阶序  出处: 旅行.htm
_PACE_ORDER = ["慢速", "中速", "快速"]


def apply_good_road(max_pace: str, good_road: bool) -> str:
    """良好道路使团队最快步调提高一节。

    规则: R-DM-034 路况良好提速
    出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
    """
    if not good_road:
        return max_pace
    idx = _PACE_ORDER.index(max_pace) if max_pace in _PACE_ORDER else 1
    return _PACE_ORDER[min(idx + 1, len(_PACE_ORDER) - 1)]


def party_pace_slow_check(member_speeds: list[int], normal_speed: int = 30) -> bool:
    """任一成员速度低于正常速度一半以下则全队必须慢速。

    规则: R-DM-035 慢速成员拖累团队
    出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
    """
    threshold = normal_speed / 2
    return any(s < threshold for s in member_speeds)


# ══════════════════════════════════════════════════════════════════════════
# 十一、觅食检定（R-DM-036）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class ForageResult:
    """觅食检定结果。"""
    success: bool
    food_lb: int = 0       # 找到的食物（磅）
    water_gal: int = 0     # 找到的水（加仑）


def forage(survival_total: int, forage_dc: int, wis_mod: int) -> ForageResult:
    """觅食检定：感知(求生)检定对抗觅食DC。

    规则: R-DM-036 觅食检定
    出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm

    成功时掷1d6+感知调整值得食物磅数，再重复掷骰得水加仑数。
    失败时什么也找不到。
    """
    if survival_total >= forage_dc:
        food_lb = dice.roll_dice("1d6").total + wis_mod
        water_gal = dice.roll_dice("1d6").total + wis_mod
        return ForageResult(success=True, food_lb=max(0, food_lb), water_gal=max(0, water_gal))
    return ForageResult(success=False, food_lb=0, water_gal=0)


# ══════════════════════════════════════════════════════════════════════════
# 十二、导航检定与迷路延误（R-DM-037）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class NavigationResult:
    """导航检定结果。"""
    success: bool
    lost: bool = False                 # 是否偏离路线
    length_multiplier: float = 1.0     # 旅程长度乘数（迷路时延长1d6×10%）


def navigation(survival_total: int, nav_dc: int) -> NavigationResult:
    """导航检定：感知(求生)检定对抗导航DC。

    规则: R-DM-037 导航检定与迷路延误
    出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm

    失败则队伍偏离路线，旅程阶段长度延长1d6×10%。
    """
    if survival_total >= nav_dc:
        return NavigationResult(success=True, lost=False, length_multiplier=1.0)
    # 迷路：延长1d6×10%
    d6 = dice.roll_die(6)
    multiplier = 1.0 + d6 * 0.1
    return NavigationResult(success=False, lost=True, length_multiplier=multiplier)


# ══════════════════════════════════════════════════════════════════════════
# 十三、追踪检定与重新搜索时间（R-DM-039）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
# ══════════════════════════════════════════════════════════════════════════

def track_research_time(track_success: bool, area_type: str) -> int:
    """追踪失败后重新搜索的时间（分钟）。

    规则: R-DM-039 追踪检定与重新搜索时间
    出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm

    - 窄区（如一连串洞穴）：10分钟
    - 户外：1小时（60分钟）
    """
    if track_success:
        return 0
    if area_type == "窄区":
        return 10
    if area_type == "户外":
        return 60
    raise ValueError(f"未知区域类型 {area_type!r}，可选: 窄区/户外")


# ══════════════════════════════════════════════════════════════════════════
# 十四、战斗回合时长（R-DM-040）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/跟进时间.htm
# ══════════════════════════════════════════════════════════════════════════

def battle_duration(rounds: int) -> int:
    """战斗回合时长：一轮6秒，总时长=rounds×6秒。

    规则: R-DM-040 战斗回合时长
    出处: topics/城主指南2024/2.运作游戏/运作探索/跟进时间.htm

    说明: 大多数战斗遭遇持续不到1分钟（10回合=60秒），
          考虑到角色们战斗后需要几秒钟振作，大多数情况下将战斗四舍五入到1分钟也很合理。
    """
    return rounds * 6


# ══════════════════════════════════════════════════════════════════════════
# 十五、被动察觉检测（check_passive_perception）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm
# 规则: R-DM-012 被动检定 / R-CHK-019 被动察觉
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class PassivePerceptionResult:
    """被动察觉检测结果。"""
    detected: bool              # 是否察觉（被动察觉 ≥ DC）
    passive_score: int          # 队伍最高被动察觉值
    dc: int                     # 目标DC（敌人隐匿检定值或隐藏物DC）
    detector_name: str = ""     # 察觉者名称


def check_passive_perception(
    party_passive_scores: list[tuple[str, int]],
    dc: int,
) -> PassivePerceptionResult:
    """检查队伍被动察觉是否达到DC。

    规则: R-DM-012 被动检定（=R-GLS-010 被动察觉=10+感知(察觉)加值,优+5/劣-5）
    出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm

    参数:
        party_passive_scores: [(角色名, 被动察觉值), ...]
        dc: 目标DC（通常是敌人的隐匿检定结果，或隐藏物的察觉DC）
    返回:
        PassivePerceptionResult: detected=任意队员被动察觉≥DC
    说明:
        - DM用被动察觉决定角色是否"自动"注意到某些东西——不需要玩家要求掷骰
        - 若敌人隐匿>队伍被动感知→队伍被伏击(突袭！)
        - 若敌人隐匿≤队伍被动感知→队伍提前发现敌人，可以准备
    """
    if not party_passive_scores:
        return PassivePerceptionResult(detected=False, passive_score=0, dc=dc)

    best_name, best_score = max(party_passive_scores, key=lambda x: x[1])
    detected = best_score >= dc
    return PassivePerceptionResult(
        detected=detected,
        passive_score=best_score,
        dc=dc,
        detector_name=best_name if detected else "",
    )


# ══════════════════════════════════════════════════════════════════════════
# 十六、随机遭遇检定（random_encounter_check）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm（旅程阶段挑战·遭遇其他生物）
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class EncounterCheckResult:
    """随机遭遇检定结果。"""
    triggered: bool             # 是否触发遭遇
    roll: int                   # d20掷骰结果
    threshold: int              # 触发阈值（默认18）


def random_encounter_check(threshold: int = 18) -> EncounterCheckResult:
    """随机遭遇检定：掷d20，结果≥阈值则触发遭遇。

    出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
          （旅程阶段挑战·遭遇其他生物；通常每日2次检定）

    参数:
        threshold: 触发阈值，默认18（即d20≥18触发，15%概率）
    返回:
        EncounterCheckResult: triggered=d20≥threshold
    说明:
        - 通常每日进行2次随机遭遇检定
        - 遭遇不一定是战斗——可能是环境事件、文明痕迹、生物足迹
        - 遭遇类型参考：埋伏、从天而降的攻击、远距离观测、偶然发现、追逐
    """
    roll = dice.roll_die(20)
    triggered = roll >= threshold
    return EncounterCheckResult(triggered=triggered, roll=roll, threshold=threshold)


# ══════════════════════════════════════════════════════════════════════════
# 十七、躲藏机制（指南Ch5）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class HideResult:
    """躲藏检定结果。"""
    success: bool               # 隐匿检定是否超过对手被动察觉
    stealth_total: int          # 隐匿检定总计
    opponent_passive: int       # 对手被动察觉
    position_revealed: bool = False  # 攻击后位置暴露


def hide_check(
    stealth_total: int,
    opponent_passive_perception: int,
) -> HideResult:
    """躲藏检定：敏捷(隐匿)检定对抗敌人的被动察觉。

    出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm
          （当其他生物正在采取躲藏动作时，就是一个要求进行感知（察觉）检定的重要时间点）

    参数:
        stealth_total: 隐匿检定总计值（d20+敏捷调整值+熟练加值if熟练）
        opponent_passive_perception: 对手的被动察觉值
    返回:
        HideResult: success=stealth_total > opponent_passive_perception
    说明:
        - 是否适合躲藏由DM决定（需要遮蔽物）
        - 攻击后位置暴露（无论命中与否）
        - 隐匿检定须严格大于被动察觉才算成功躲藏
    """
    success = stealth_total > opponent_passive_perception
    return HideResult(
        success=success,
        stealth_total=stealth_total,
        opponent_passive=opponent_passive_perception,
    )


# ══════════════════════════════════════════════════════════════════════════
# 十八、资源追踪（报告§6）
# 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm（跟进食物和水的消耗）
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class Resources:
    """旅行资源追踪。

    出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
          （团队中的每个成员在阶段内消耗相应数量的食物和水）
    """
    food_lb: int = 0            # 口粮库存（磅）
    water_gal: int = 0          # 水库存（加仑）
    torches: int = 0            # 火把数量
    torch_duration_hours: float = 1.0  # 每根火把持续时间（小时）

    def consume_daily(self, party_size: int) -> dict[str, int]:
        """每日消耗：每生物1磅食物 + 1加仑水。

        出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
              （如果团队补给不足，角色们可能会面临脱水Dehydration或饥饿Malnutrition的风险）
        """
        food_needed = party_size * 1
        water_needed = party_size * 1
        food_consumed = min(food_needed, self.food_lb)
        water_consumed = min(water_needed, self.water_gal)
        self.food_lb -= food_consumed
        self.water_gal -= water_consumed
        return {
            "food_consumed_lb": food_consumed,
            "water_consumed_gal": water_consumed,
            "food_shortage_lb": max(0, food_needed - food_consumed),
            "water_shortage_gal": max(0, water_needed - water_consumed),
        }


# ══════════════════════════════════════════════════════════════════════════
# 十九、ExplorationState 数据类
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class ExplorationState:
    """探索流程状态对象。

    承载旅行/地城探索过程中的全部状态：
    - pace: 当前旅行步调（快速/中速/慢速）
    - roles: 队伍职责分配 {navigator: cid, scout: cid, rear_guard: cid, quartermaster: cid}
    - nav_dc: 当前导航DC（由地形决定）
    - current_location: 当前地点描述
    - time_elapsed: 已流逝时间（分钟）
    - resources: 资源追踪对象
    - encounter_table: 遭遇表 [{trigger, type, description}]
    - terrain: 当前地形
    - light_level: 当前光照等级
    - lost: 是否迷路
    - exhaustion_levels: 力竭等级累积（6级制，1级劣势能力检定，6级死亡）
    """
    pace: str = "中速"
    roles: dict[str, Any] = field(default_factory=dict)
    nav_dc: int = 15
    current_location: str = ""
    time_elapsed: int = 0           # 分钟
    resources: Resources = field(default_factory=Resources)
    encounter_table: list[dict] = field(default_factory=list)
    terrain: str = "草原"
    light_level: str = LIGHT_BRIGHT
    lost: bool = False
    exhaustion_levels: int = 0      # 力竭等级（报告§6：6级制）

    def advance_time(self, minutes: int) -> None:
        """推进时间。"""
        self.time_elapsed += minutes

    def add_exhaustion(self, levels: int = 1) -> int:
        """增加力竭等级（6级死亡）。

        出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
              （阻碍会使角色筋疲力尽，从而导致获得力竭等级；
                不闪不避地在暴风雪中前进可能会导致每个角色获得1d4级力竭）
        """
        self.exhaustion_levels = min(6, self.exhaustion_levels + levels)
        return self.exhaustion_levels

    @property
    def is_dead_from_exhaustion(self) -> bool:
        """力竭6级即死。"""
        return self.exhaustion_levels >= 6


# ══════════════════════════════════════════════════════════════════════════
# 二十、travel_day — 一天旅行流程
# 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm（运行各个阶段）
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class TravelDayResult:
    """一天旅行流程的结果。"""
    pace: str                           # 实际采用的步调
    distance_miles: int                 # 当日行进距离（英里）
    weather: Weather                    # 天气
    navigation: NavigationResult        # 导航结果
    forage_results: list[ForageResult]  # 各觅食角色的结果
    encounter_checks: list[EncounterCheckResult]  # 随机遭遇检定（通常2次）
    resource_consumption: dict          # 资源消耗
    lost: bool                          # 是否迷路
    notes: list[str] = field(default_factory=list)  # 流程备注


def travel_day(
    state: ExplorationState,
    party_size: int,
    navigator_survival_total: int,
    foragers: list[tuple[str, int, int]] | None = None,
    good_road: bool = False,
    encounter_checks_per_day: int = 2,
) -> TravelDayResult:
    """执行一天旅行流程。

    出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm（运行各个阶段）

    流程（报告§6）：
    1. 设定旅行步调（快速/中速/慢速）
    2. 分配队伍职责（导航员/侦察兵/后卫/军需官）
    3. 导航检定（DM根据地形设定导航DC；导航员进行感知(生存)检定；
       失败则队伍偏离路线——可能多走一天，也可能闯入危险区域）
    4. 被动感知与遭遇检测（DM用敌人的隐匿检定对比队伍的被动感知；
       如果敌人隐匿>队伍被动感知→队伍被伏击(突袭！)；
       如果敌人隐匿≤队伍被动感知→队伍提前发现敌人，可以准备）
    5. 随机遭遇检定（DM定期掷随机遭遇骰(通常每日2次，d20≥18触发)；
       遭遇不一定是战斗——可能是环境事件、文明痕迹、生物足迹）
    6. 资源追踪（每日消耗口粮(每生物1磅)、追踪水源、火把持续时间(每根1小时)、
       黑暗视觉范围(60尺)；缺乏食物/水/睡眠→累力等级累积(6级制，1级劣势能力检定，6级死亡)）

    参数:
        state: ExplorationState 对象（会被原地修改）
        party_size: 队伍人数
        navigator_survival_total: 导航员的感知(生存)检定总计值
        foragers: 觅食角色列表 [(角色名, survival_total, wis_mod), ...]，None表示无人觅食
        good_road: 是否有良好道路（使最快步调提高一节）
        encounter_checks_per_day: 每日随机遭遇检定次数（默认2次）
    返回:
        TravelDayResult: 一天旅行的完整结果
    """
    notes: list[str] = []

    # ── 第一步：设定步调 ──
    # 根据地形确定最快步调，应用路况提速
    terrain = terrain_params(state.terrain)
    max_pace = apply_good_road(terrain.max_pace, good_road)
    # 实际步调不能超过地形最快步调
    pace_order_idx = {"慢速": 0, "中速": 1, "快速": 2}
    requested_idx = pace_order_idx.get(state.pace, 1)
    max_idx = pace_order_idx.get(max_pace, 1) if max_pace != "特殊" else 2
    actual_pace_idx = min(requested_idx, max_idx)
    actual_pace = ["慢速", "中速", "快速"][actual_pace_idx]
    state.pace = actual_pace
    pace = get_travel_pace(actual_pace)
    notes.append(f"步调: {actual_pace}（地形最快: {max_pace}）")

    # ── 第二步：职责分配（由调用方通过 state.roles 设置）──
    navigator_id = state.roles.get("navigator")
    notes.append(f"导航员: {navigator_id if navigator_id is not None else '未指定'}")

    # ── 第三步：导航检定 ──
    state.nav_dc = terrain.nav_dc
    nav_result = navigation(navigator_survival_total, state.nav_dc)
    state.lost = nav_result.lost
    if nav_result.lost:
        notes.append(f"导航失败！队伍偏离路线，旅程延长至 {nav_result.length_multiplier:.1f} 倍")
    else:
        notes.append("导航成功，队伍沿正确路线前进")

    # ── 计算当日行进距离 ──
    base_distance = pace.per_day_miles
    # 迷路延长旅程：实际有效距离 = 基础距离 / 乘数（因为多走了路）
    distance_miles = math.floor(base_distance / nav_result.length_multiplier) if nav_result.lost else base_distance

    # ── 第四步：天气 ──
    weather = weather_roll()
    notes.append(f"天气: 温度{weather.temperature}, 风{weather.wind}, 降雨{weather.rain}")

    # ── 第五步：觅食 ──
    forage_results: list[ForageResult] = []
    if foragers:
        forager_name, survival_total, wis_mod = foragers[0]  # 取第一个觅食者示例
        fr = forage(survival_total, terrain.forage_dc, wis_mod)
        forage_results.append(fr)
        if fr.success:
            notes.append(f"{forager_name} 觅食成功: 食物{fr.food_lb}磅, 水{fr.water_gal}加仑")
            state.resources.food_lb += fr.food_lb
            state.resources.water_gal += fr.water_gal
        else:
            notes.append(f"{forager_name} 觅食失败，什么也没找到")

    # ── 第六步：随机遭遇检定 ──
    encounter_checks: list[EncounterCheckResult] = []
    for _ in range(encounter_checks_per_day):
        ec = random_encounter_check()
        encounter_checks.append(ec)
        if ec.triggered:
            notes.append(f"随机遭遇触发！(d20={ec.roll}≥{ec.threshold})")

    # ── 第七步：资源追踪 ──
    consumption = state.resources.consume_daily(party_size)
    if consumption["food_shortage_lb"] > 0 or consumption["water_shortage_gal"] > 0:
        notes.append("补给不足！缺乏食物/水将导致力竭等级累积")
        state.add_exhaustion(1)  # 缺乏食物/水→力竭+1

    # ── 推进时间：8小时旅行 = 480分钟 ──
    state.advance_time(480)

    return TravelDayResult(
        pace=actual_pace,
        distance_miles=distance_miles,
        weather=weather,
        navigation=nav_result,
        forage_results=forage_results,
        encounter_checks=encounter_checks,
        resource_consumption=consumption,
        lost=nav_result.lost,
        notes=notes,
    )


# ══════════════════════════════════════════════════════════════════════════
# 二十一、dungeon_turn — 地城探索回合
# 出处: topics/城主指南2024/2.运作游戏/运作探索/跟进时间.htm
#       topics/城主指南2024/2.运作游戏/运作探索/探索中的动作.htm
# ══════════════════════════════════════════════════════════════════════════

# 地城探索时间单位：10分钟为一段（探索回合）
# 出处: 跟进时间.htm（分钟Minutes。地城或聚落中的移动将以分钟为单位）
DUNGEON_TURN_MINUTES = 10

# 探索动作类型  出处: 探索中的动作.htm
EXPLORATION_ACTIONS = frozenset({
    "搜索",     # Search — 寻找隐藏事物（密门、陷阱、宝藏）
    "调查",     # Investigate — 推理与演绎（如何开启机关门等）
    "操作",     # Interact — 操作物件/开门/开箱
    "协助",     # Help — 协助另一角色完成动作
    "移动",     # Move — 在地城中移动
    "聆听",     # Listen — 主动聆听声音
})


@dataclass
class DungeonTurnResult:
    """地城探索回合的结果。"""
    action: str                         # 执行的动作
    minutes_elapsed: int                # 本回合流逝时间（分钟）
    check_result: dict | None = None # 检定结果（若有）
    detected: bool = False              # 被动察觉是否检测到隐藏物
    passive_score: int = 0              # 队伍最高被动察觉值
    notes: list[str] = field(default_factory=list)


def dungeon_turn(
    state: ExplorationState,
    action: str,
    party_passive_scores: list[tuple[str, int]] | None = None,
    check_dc: int | None = None,
    check_total: int | None = None,
    ability: str = "",
) -> DungeonTurnResult:
    """执行一个地城探索回合（10分钟）。

    出处: topics/城主指南2024/2.运作游戏/运作探索/跟进时间.htm
          topics/城主指南2024/2.运作游戏/运作探索/探索中的动作.htm

    地城探索流程（报告§6）：
    - 地城探索使用更紧凑的时间单位——通常以10分钟为一段（探索回合）
    - 被动感知 vs 主动检定：DM用被动感知决定角色是否"自动"注意到某些东西
      ——不需要玩家要求掷骰

    参数:
        state: ExplorationState 对象（会被原地修改）
        action: 探索动作类型（见 EXPLORATION_ACTIONS）
        party_passive_scores: [(角色名, 被动察觉值), ...]，用于被动察觉检测
        check_dc: 主动检定的DC（如搜索DC、调查DC）
        check_total: 主动检定的总计值
        ability: 检定所用的属性（感知/智力等）
    返回:
        DungeonTurnResult: 回合结果
    """
    notes: list[str] = []
    if action not in EXPLORATION_ACTIONS:
        raise ValueError(f"未知探索动作 {action!r}，可选: {sorted(EXPLORATION_ACTIONS)}")

    # 推进时间：一个探索回合 = 10分钟
    # 出处: 跟进时间.htm
    state.advance_time(DUNGEON_TURN_MINUTES)
    notes.append(f"执行动作: {action}（耗时{DUNGEON_TURN_MINUTES}分钟）")

    check_result: dict | None = None
    detected = False
    passive_score = 0

    # 被动察觉检测：DM用被动感知决定角色是否"自动"注意到某些东西
    # 出处: 察觉.htm / 探索中的动作.htm
    if party_passive_scores and check_dc is not None:
        pp_result = check_passive_perception(party_passive_scores, check_dc)
        passive_score = pp_result.passive_score
        detected = pp_result.detected
        if detected:
            notes.append(f"被动察觉({passive_score})≥DC({check_dc})，{pp_result.detector_name}自动发现了隐藏事物")
        else:
            notes.append(f"被动察觉({passive_score})<DC({check_dc})，未自动发现")

    # 主动检定（搜索/调查等）
    # 出处: 探索中的动作.htm（属性检定与角色扮演之间的平衡）
    if check_total is not None and check_dc is not None:
        success = check_total >= check_dc
        check_result = {
            "ability": ability,
            "dc": check_dc,
            "total": check_total,
            "success": success,
        }
        notes.append(f"{ability}检定: {check_total} vs DC{check_dc} → {'成功' if success else '失败'}")

    return DungeonTurnResult(
        action=action,
        minutes_elapsed=DUNGEON_TURN_MINUTES,
        check_result=check_result,
        detected=detected,
        passive_score=passive_score,
        notes=notes,
    )


# ══════════════════════════════════════════════════════════════════════════
# 自检
# ══════════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    """基本正确性自检（非穷尽）。"""

    # ── 旅行步调表 ──
    # 规则: R-DM-032 / R-GLS-048  出处: 玩家手册2024/进行游戏/旅行.htm
    fast = get_travel_pace("快速")
    assert fast.per_minute_ft == 400 and fast.per_day_miles == 30
    med = get_travel_pace("中速")
    assert med.per_hour_miles == 3 and med.per_day_miles == 24
    slow = get_travel_pace("慢速")
    assert slow.per_minute_ft == 200 and slow.per_day_miles == 18
    # 快速：感知(察觉/生存)与敏捷(隐匿)检定均劣势
    assert fast.perception_disadvantage is True
    assert fast.stealth_disadvantage is True
    assert fast.perception_advantage is False
    # 中速：敏捷(隐匿)检定劣势，感知无优劣势
    assert med.stealth_disadvantage is True
    assert med.perception_disadvantage is False
    assert med.perception_advantage is False
    # 慢速：感知(察觉/生存)检定优势，隐匿无劣势
    assert slow.perception_advantage is True
    assert slow.perception_disadvantage is False
    assert slow.stealth_disadvantage is False

    # ── 旅行地形表 ──
    # 规则: R-DM-033  出处: 旅行.htm
    forest = terrain_params("森林")
    assert forest.max_pace == "中速" and forest.encounter_distance == "2d8x10"
    assert forest.forage_dc == 10 and forest.nav_dc == 15 and forest.search_dc == 15
    swamp = terrain_params("沼泽")
    assert swamp.max_pace == "慢速" and swamp.nav_dc == 15 and swamp.search_dc == 20
    mountain = terrain_params("山地")
    assert mountain.max_pace == "慢速" and mountain.encounter_distance == "4d10x10"

    # ── 光照与遮蔽 ──
    # 规则: R-DM-027  出处: 察觉.htm
    assert light_obscurement(LIGHT_BRIGHT) == "无遮蔽"
    assert light_obscurement(LIGHT_DIM) == "轻度遮蔽"
    assert light_obscurement(LIGHT_DARK) == "重度遮蔽"

    # ── 特殊感官 ──
    # 出处: 察觉.htm
    # 黑暗视觉：重度遮蔽 → 轻度遮蔽
    assert effective_obscurement("重度遮蔽", {SENSE_DARKVISION}) == "轻度遮蔽"
    # 真实视觉：看穿一切遮蔽
    assert effective_obscurement("重度遮蔽", {SENSE_TRUESIGHT}) == "无遮蔽"
    # 盲视：无需视觉
    assert effective_obscurement("重度遮蔽", {SENSE_BLINDSIGHT}) == "无遮蔽"
    # 无特殊感官：重度遮蔽不变
    assert effective_obscurement("重度遮蔽", set()) == "重度遮蔽"

    # ── 声音传播距离 ──
    # 规则: R-DM-026  出处: 察觉.htm
    dist = audible_distance("正常噪音等级")
    assert 20 <= dist <= 120  # 2d6×10 = 20-120
    dist_quiet = audible_distance("尽量保持安静")
    assert 10 <= dist_quiet <= 60  # 2d6×5 = 10-60

    # ── 户外能见度 ──
    # 规则: R-DM-027  出处: 察觉.htm
    assert outdoor_visibility("晴朗") == 2
    assert outdoor_visibility("晴朗", vantage=True) == 40
    assert outdoor_visibility("雨") == 1
    fog_vis = outdoor_visibility("雾")
    assert 100 <= fog_vis <= 300

    # ── 海上能见度 ──
    # 规则: R-DM-028  出处: 察觉.htm
    assert sea_visibility("晴朗") == 10
    assert sea_visibility("阴沉") == 5

    # ── 水下遭遇距离 ──
    # 规则: R-DM-029  出处: 察觉.htm
    assert underwater_encounter_distance("清澈", LIGHT_BRIGHT) == 60
    assert underwater_encounter_distance("清澈", LIGHT_DIM) == 30
    assert underwater_encounter_distance("浑浊", LIGHT_BRIGHT) == 10
    assert underwater_encounter_distance("清澈", LIGHT_DARK) == 10

    # ── 天气表 ──
    # 规则: R-DM-030  出处: 旅行.htm
    w = weather_roll()
    assert w.wind in ("无", "轻风", "强风")
    assert w.rain in ("无", "轻度降雨或降雪", "重度降雨或降雪")

    # ── 延长旅行力竭 ──
    # 规则: R-DM-031  出处: 旅行.htm
    # DC=10+extra_hours；第1个额外小时DC=11
    assert extended_travel_exhaustion(extra_hours=1, con_save_total=11) is False  # 11≥11 不力竭
    assert extended_travel_exhaustion(extra_hours=1, con_save_total=10) is True   # 10<11 力竭
    assert extended_travel_exhaustion(extra_hours=3, con_save_total=12) is True   # DC=13, 12<13

    # ── 特殊移动旅行速率 ──
    # 规则: R-DM-032  出处: 旅行.htm
    # 速度60 → mph=6 → 中速8小时=48英里
    assert special_travel_rate(speed=60, pace="中速", travel_hours=8) == 48
    # 快速 = 48 × 4/3 = 64
    assert special_travel_rate(speed=60, pace="快速", travel_hours=8) == 64
    # 慢速 = 48 × 2/3 = 32
    assert special_travel_rate(speed=60, pace="慢速", travel_hours=8) == 32

    # ── 路况良好提速 ──
    # 规则: R-DM-034  出处: 旅行.htm
    assert apply_good_road("慢速", good_road=True) == "中速"
    assert apply_good_road("中速", good_road=True) == "快速"
    assert apply_good_road("快速", good_road=True) == "快速"  # 已是最快
    assert apply_good_road("中速", good_road=False) == "中速"

    # ── 慢速成员拖累 ──
    # 规则: R-DM-035  出处: 旅行.htm
    # 任一成员速度<正常速度/2则全队慢速
    assert party_pace_slow_check([30, 30, 30], normal_speed=30) is False  # 都≥15
    assert party_pace_slow_check([30, 10, 30], normal_speed=30) is True   # 10<15
    assert party_pace_slow_check([25, 25], normal_speed=30) is False      # 25≥15

    # ── 觅食检定 ──
    # 规则: R-DM-036  出处: 旅行.htm
    # 成功时掷1d6+wis_mod得食物磅数，重复得水加仑
    fr = forage(survival_total=15, forage_dc=10, wis_mod=3)
    assert fr.success is True
    assert fr.food_lb >= 4  # 1d6(1-6)+3 = 4-9
    assert fr.water_gal >= 4
    fr_fail = forage(survival_total=5, forage_dc=10, wis_mod=3)
    assert fr_fail.success is False and fr_fail.food_lb == 0

    # ── 导航检定 ──
    # 规则: R-DM-037  出处: 旅行.htm
    # 成功：不迷路，乘数1.0
    nav_ok = navigation(survival_total=16, nav_dc=15)
    assert nav_ok.success is True and nav_ok.lost is False and nav_ok.length_multiplier == 1.0
    # 失败：迷路，乘数1.1-1.6（1d6×10%）
    nav_fail = navigation(survival_total=10, nav_dc=15)
    assert nav_fail.success is False and nav_fail.lost is True
    assert 1.1 <= nav_fail.length_multiplier <= 1.6

    # ── 追踪重新搜索时间 ──
    # 规则: R-DM-039  出处: 旅行.htm
    assert track_research_time(track_success=False, area_type="窄区") == 10
    assert track_research_time(track_success=False, area_type="户外") == 60
    assert track_research_time(track_success=True, area_type="窄区") == 0

    # ── 战斗回合时长 ──
    # 规则: R-DM-040  出处: 跟进时间.htm
    assert battle_duration(rounds=10) == 60  # 10回合=60秒=1分钟
    assert battle_duration(rounds=1) == 6
    assert battle_duration(rounds=5) == 30

    # ── 被动察觉检测 ──
    # 规则: R-DM-012  出处: 察觉.htm
    party_pp = [("阿拉贡", 12), ("莱戈拉斯", 16), ("金雳", 10)]
    # DC=15：莱戈拉斯(16)≥15 → 检测到
    r = check_passive_perception(party_pp, dc=15)
    assert r.detected is True and r.passive_score == 16 and r.detector_name == "莱戈拉斯"
    # DC=17：无人≥17 → 未检测到
    r2 = check_passive_perception(party_pp, dc=17)
    assert r2.detected is False and r2.passive_score == 16
    # 空队伍
    r3 = check_passive_perception([], dc=10)
    assert r3.detected is False

    # ── 随机遭遇检定 ──
    # 出处: 旅行.htm（通常每日2次，d20≥18触发）
    ec = random_encounter_check(threshold=18)
    assert 1 <= ec.roll <= 20
    assert ec.triggered == (ec.roll >= 18)
    # 阈值=1：必定触发
    ec2 = random_encounter_check(threshold=1)
    assert ec2.triggered is True

    # ── 躲藏检定 ──
    # 出处: 察觉.htm
    # stealth_total > opponent_passive → 成功
    hr = hide_check(stealth_total=18, opponent_passive_perception=15)
    assert hr.success is True and hr.position_revealed is False
    # 相等不算成功（须严格大于）
    hr2 = hide_check(stealth_total=15, opponent_passive_perception=15)
    assert hr2.success is False
    # 低于对方被动察觉 → 失败
    hr3 = hide_check(stealth_total=10, opponent_passive_perception=15)
    assert hr3.success is False

    # ── 资源追踪 ──
    # 出处: 旅行.htm（每生物1磅食物+1加仑水）
    res = Resources(food_lb=10, water_gal=10, torches=5)
    cons = res.consume_daily(party_size=4)
    assert cons["food_consumed_lb"] == 4 and cons["water_consumed_gal"] == 4
    assert res.food_lb == 6 and res.water_gal == 6
    assert cons["food_shortage_lb"] == 0
    # 补给不足
    res2 = Resources(food_lb=2, water_gal=10)
    cons2 = res2.consume_daily(party_size=4)
    assert cons2["food_consumed_lb"] == 2 and cons2["food_shortage_lb"] == 2
    assert res2.food_lb == 0

    # ── ExplorationState 基本功能 ──
    es = ExplorationState(terrain="森林", pace="中速")
    assert es.exhaustion_levels == 0
    es.add_exhaustion(2)
    assert es.exhaustion_levels == 2
    es.add_exhaustion(10)  # 上限6
    assert es.exhaustion_levels == 6 and es.is_dead_from_exhaustion
    es.advance_time(30)
    assert es.time_elapsed == 30

    # ── travel_day 集成测试 ──
    state = ExplorationState(
        terrain="草原",
        pace="中速",
        roles={"navigator": "阿拉贡"},
        resources=Resources(food_lb=20, water_gal=20, torches=3),
    )
    result = travel_day(
        state=state,
        party_size=4,
        navigator_survival_total=16,  # ≥草原nav_dc=5 → 导航成功
        foragers=[("莱戈拉斯", 16, 3)],  # survival=16 ≥ forage_dc=15 → 成功
    )
    # 步调应为中速（草原最快=快速，请求中速≤快速）
    assert result.pace == "中速"
    # 草原中速：per_day_miles=24
    assert result.distance_miles == 24
    # 导航成功
    assert result.navigation.success is True and result.navigation.lost is False
    # 觅食成功
    assert len(result.forage_results) == 1
    assert result.forage_results[0].success is True
    # 随机遭遇检定：默认2次
    assert len(result.encounter_checks) == 2
    # 资源消耗：4人 × 1磅 = 4磅食物，4加仑水
    assert result.resource_consumption["food_consumed_lb"] == 4
    assert result.resource_consumption["water_consumed_gal"] == 4
    # 时间推进480分钟
    assert state.time_elapsed == 480
    # 库存减少
    assert state.resources.food_lb == 20 - 4 + result.forage_results[0].food_lb

    # ── travel_day 迷路场景 ──
    state2 = ExplorationState(
        terrain="森林",
        pace="中速",
        roles={"navigator": "阿拉贡"},
        resources=Resources(food_lb=20, water_gal=20),
    )
    result2 = travel_day(
        state=state2,
        party_size=4,
        navigator_survival_total=5,  # < 森林nav_dc=15 → 迷路
    )
    assert result2.navigation.lost is True
    # 迷路时有效距离 = 24 / multiplier（< 24）
    assert result2.distance_miles < 24

    # ── dungeon_turn 集成测试 ──
    dstate = ExplorationState(terrain="幽暗地域", pace="中速", light_level=LIGHT_DARK)
    party_pp2 = [("阿拉贡", 12), ("莱戈拉斯", 16)]
    # 搜索动作：DC=15，莱戈拉斯被动察觉16≥15 → 自动发现
    dt = dungeon_turn(
        state=dstate,
        action="搜索",
        party_passive_scores=party_pp2,
        check_dc=15,
        check_total=18,
        ability="感知",
    )
    assert dt.action == "搜索"
    assert dt.minutes_elapsed == 10
    assert dt.detected is True  # 被动察觉16≥15
    assert dt.passive_score == 16
    assert dt.check_result is not None
    assert dt.check_result["success"] is True  # 18≥15
    assert dstate.time_elapsed == 10

    # ── dungeon_turn 未知动作报错 ──
    try:
        dungeon_turn(dstate, action="飞行")
        assert False, "应抛出ValueError"
    except ValueError:
        pass

    print("[exploration] 自检通过 ✓")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    _self_test()
