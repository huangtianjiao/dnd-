"""位面旅行系统 — DMG 第六章 宇宙学。

规则依据: 城主指南2024/6.宇宙学/
  - 位面旅行.htm         传送门开启条件 / 法术旅行 / 跨位面通道
  - 位面冒险.htm         血战与位面冒险情景
  - 诸位面.htm           位面分类（物质界域/中转/内层/外层/正负）
  - 多元宇宙之旅/*.htm   各位面的危害与传送门详述

本模块提供:
  - TRAVEL_METHODS 枚举: PORTAL / SPELL / GATE / VORTEX / COLOR_POOL
  - TravelResult 数据类: 旅行结果（成功/失败/耗时/遭遇）
  - HazardResult 数据类: 危害检定结果
  - travel_to_plane(): 执行位面旅行
  - apply_plane_hazards(): 应用位面危害
  - check_portal_accessibility(): 检查传送门可达性
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from ..data.planes import Plane, PlaneType, get_plane, list_planes


# ──────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────

class TRAVEL_METHODS(Enum):
    """位面旅行方式。

    出处: 城主指南2024/6.宇宙学/位面旅行.htm
      - 传送门 Planar Portals: 静态的位面间通路，需满足开启条件
      - 法术 Spells: 异界之门 Gate / 位面转移 Plane Shift / 以太化 Etherealness / 星光投影 Astral Projection
      - 位面之门 Gate: 特指异界之门法术创造的通道
      - 漩涡 Vortex: 通往元素位面的涡流，如火山中心的岩浆漩涡
      - 彩池 Color Pool: 星界通往其他位面的门户
    """
    PORTAL = "传送门"
    SPELL = "法术"
    GATE = "位面之门"
    VORTEX = "漩涡"
    COLOR_POOL = "彩池"


# ──────────────────────────────────────────────────────────────────────────
# 结果数据类
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class TravelResult:
    """位面旅行结果。

    字段说明:
      success:          旅行是否成功
      origin_plane:     出发位面名称
      destination_plane: 目的位面名称
      method:           旅行方式（TRAVEL_METHODS 的 value）
      travel_time_hours: 预计旅行耗时（小时），0 表示瞬时
      message:          旅行结果描述
      hazards:          途中遭遇的危害列表
      encounters:       途中可能遭遇的事件/生物列表
      arrival_layer:    抵达的位层名称（多位层位面用）
    """
    success: bool = False
    origin_plane: str = ""
    destination_plane: str = ""
    method: str = ""
    travel_time_hours: float = 0.0
    message: str = ""
    hazards: list[str] = field(default_factory=list)
    encounters: list[str] = field(default_factory=list)
    arrival_layer: str = ""


@dataclass
class HazardResult:
    """位面危害检定结果。

    字段说明:
      plane_name:    位面名称
      hazard_type:   危害类型描述
      dc:            豁免 DC（0 表示无需豁免）
      save_attribute: 豁免属性（感知/体质/智力/魅力等）
      passed:        豁免是否通过（None 表示未进行豁免）
      damage:        受到的伤害（如有）
      effect:        产生的状态效应描述
      description:   危害的详细描述
    """
    plane_name: str = ""
    hazard_type: str = ""
    dc: int = 0
    save_attribute: str = ""
    passed: Optional[bool] = None
    damage: int = 0
    effect: str = ""
    description: str = ""


# ──────────────────────────────────────────────────────────────────────────
# 位面旅行核心函数
# ──────────────────────────────────────────────────────────────────────────

def travel_to_plane(
    origin_plane: str,
    destination_plane: str,
    method: TRAVEL_METHODS = TRAVEL_METHODS.SPELL,
    *,
    seed: Optional[int] = None,
) -> TravelResult:
    """执行位面旅行。

    规则依据: 城主指南2024/6.宇宙学/位面旅行.htm
      - 传送门旅行：需找到传送门、满足开启条件、可能遭遇守卫
      - 法术旅行：位面转移 Plane Shift 需要正确的音叉；异界之门 Gate 更为可靠
      - 彩池旅行：从星光位面定位通向目标位面的彩池

    Args:
        origin_plane:      出发位面名称（中文或英文）
        destination_plane: 目的位面名称（中文或英文）
        method:            旅行方式，默认 SPELL
        seed:              随机种子（用于可复现的旅行耗时计算）

    Returns:
        TravelResult 对象，包含旅行是否成功、耗时、途中遭遇等信息

    出处: 城主指南2024/6.宇宙学/位面旅行.htm 及各位面 HTML 文件
    """
    rng = random.Random(seed)

    # 解析出发和目的位面
    origin = get_plane(origin_plane)
    dest = get_plane(destination_plane)

    result = TravelResult(
        origin_plane=origin_plane,
        destination_plane=destination_plane,
        method=method.value,
    )

    # 校验位面是否存在
    if origin is None:
        result.message = f"出发位面 {origin_plane!r} 不存在于已知多元宇宙中"
        return result
    if dest is None:
        result.message = f"目的位面 {destination_plane!r} 不存在于已知多元宇宙中"
        return result

    # 同一位面无需旅行
    if origin.name == dest.name:
        result.success = True
        result.travel_time_hours = 0.0
        result.message = f"已在 {origin.name}，无需位面旅行"
        return result

    # 根据旅行方式计算结果
    if method == TRAVEL_METHODS.PORTAL:
        _apply_portal_travel(origin, dest, result, rng)
    elif method == TRAVEL_METHODS.SPELL:
        _apply_spell_travel(origin, dest, result, rng)
    elif method == TRAVEL_METHODS.GATE:
        _apply_gate_travel(origin, dest, result, rng)
    elif method == TRAVEL_METHODS.VORTEX:
        _apply_vortex_travel(origin, dest, result, rng)
    elif method == TRAVEL_METHODS.COLOR_POOL:
        _apply_color_pool_travel(origin, dest, result, rng)

    # 确定抵达位层（多位层位面取第一层作为前厅）
    if dest.layers:
        result.arrival_layer = dest.layers[0].get("name", "")
    elif result.success:
        result.arrival_layer = dest.name

    # 收集目的位面的潜在危害提示
    if result.success and dest.hazards:
        result.hazards = list(dest.hazards)

    return result


def _apply_portal_travel(
    origin: Plane, dest: Plane, result: TravelResult, rng: random.Random
) -> None:
    """传送门旅行逻辑。

    规则: 位面旅行.htm - 传送门开启条件
      - 命令 Command: 给出特定命令才会开启
      - 钥匙物品 Key Item: 携带特定物件才会开启
      - 随机 Random: 随机开启一段时间，允许1d6+6名旅行者通过
      - 情境 Situation: 特定条件下开启（满月/下雨/施法等）
      - 时间 Time: 物质位面上的特定时间开启
    """
    # 检查目的位面是否有已知传送门
    if not dest.portals:
        result.message = (
            f"{dest.name} 没有已知的传送门，无法通过传送门方式抵达。"
            f"建议使用法术（位面转移/异界之门）或其他旅行方式。"
        )
        return

    # 传送门守卫检查
    guardian_encounters = [
        "气巨灵守卫", "斯芬克斯守卫", "泰坦守卫",
        "位面居民守卫", "魔法生物守卫",
    ]
    encounter = rng.choice(guardian_encounters)
    result.encounters.append(encounter)

    # 传送门开启条件（随机模拟一种）
    conditions = ["命令语", "钥匙物品", "随机开启", "情境触发", "特定时间"]
    condition = rng.choice(conditions)

    # 传送门旅行通常较快
    result.travel_time_hours = rng.uniform(0.5, 4.0)
    result.success = True
    result.message = (
        f"通过传送门从 {origin.name} 前往 {dest.name}。"
        f"传送门以「{condition}」方式开启，途中遭遇 {encounter}。"
        f"预计旅行耗时约 {result.travel_time_hours:.1f} 小时。"
    )


def _apply_spell_travel(
    origin: Plane, dest: Plane, result: TravelResult, rng: random.Random
) -> None:
    """法术旅行逻辑。

    规则: 位面旅行.htm - 法术 Spells
      - 位面转移 Plane Shift: 需要正确的音叉（调谐 fork）
      - 以太化 Etherealness: 进入以太位面边界
      - 星光投影 Astral Projection: 将自身投影进星光位面
      - 异界之门 Gate: 创造通往目标位面的通道（更可靠）
    """
    # 位面转移需要正确的音叉
    # 不同位面类型的旅行难度不同
    if dest.plane_type == PlaneType.DEMIPLANE:
        # 半位面：所需频率的音叉往往极其难以获取
        result.travel_time_hours = rng.uniform(1.0, 6.0)
        result.success = True
        result.message = (
            f"通过位面转移法术从 {origin.name} 前往半位面 {dest.name}。"
            f"注意：进入半位面所需频率的音叉往往极其难以获取。"
            f"若施法者知道该半位面的存在，异界之门 Gate 更为可靠。"
        )
        return

    # 正常法术旅行
    result.travel_time_hours = rng.uniform(1.0, 8.0)
    result.success = True
    result.message = (
        f"通过位面转移法术从 {origin.name} 前往 {dest.name}。"
        f"需要与目标位面共振的正确音叉。预计旅行耗时约 "
        f"{result.travel_time_hours:.1f} 小时。"
    )


def _apply_gate_travel(
    origin: Plane, dest: Plane, result: TravelResult, rng: random.Random
) -> None:
    """位面之门（异界之门 Gate 法术）旅行逻辑。

    规则: 位面旅行.htm - 法术 Spells
      异界之门 Gate 法术创造通往目标位面的通道，更为可靠。
      若施法者知道目标位面的存在，此法比位面转移更可靠。
    """
    result.travel_time_hours = 0.0  # 异界之门近乎瞬时
    result.success = True
    result.message = (
        f"通过异界之门 Gate 法术从 {origin.name} 前往 {dest.name}。"
        f"此法最为可靠，旅行近乎瞬时完成。"
    )


def _apply_vortex_travel(
    origin: Plane, dest: Plane, result: TravelResult, rng: random.Random
) -> None:
    """漩涡旅行逻辑。

    规则: 位面旅行.htm - 传送门 Planar Portals
      漩涡是通往元素位面的涡流，一般位于物质位面上与之十分类似的地点。
      例如：火山中心岩浆池的漩涡（通往火元素位面），
      大洋深处的巨大漩涡（通往水元素位面）。
    """
    # 漩涡主要适用于元素位面
    if dest.plane_type != PlaneType.INNER:
        result.message = (
            f"漩涡旅行方式主要适用于元素位面，"
            f"而 {dest.name} 是 {dest.plane_type.value}，不适合此方式。"
            f"建议使用传送门、法术或其他旅行方式。"
        )
        return

    result.travel_time_hours = rng.uniform(0.1, 2.0)
    result.success = True
    result.encounters.append("元素涡流中的原初力量")
    result.message = (
        f"通过元素漩涡从 {origin.name} 前往 {dest.name}。"
        f"漩涡一般位于物质位面上与之十分类似的地点。"
        f"预计旅行耗时约 {result.travel_time_hours:.1f} 小时。"
    )


def _apply_color_pool_travel(
    origin: Plane, dest: Plane, result: TravelResult, rng: random.Random
) -> None:
    """彩池旅行逻辑。

    规则: 多元宇宙之旅/星光位面.htm - 彩池 Color Pools
      星界通往其他位面的门户显现为涟漪的二维彩池，其直径为1d6×10尺。
      前往其他位面需要定位一个通向那一位面的彩池。
      这些门户通向的位面可以通过其颜色加以鉴别。
      寻找通向某特定位面的彩池，旅途可能耗时1d4×10小时。
    """
    # 彩池旅行要求从星光位面出发，或经由星光位面中转
    if origin.plane_type != PlaneType.ASTRAL:
        result.message = (
            f"彩池旅行方式要求从星光位面出发，"
            f"而当前出发位面 {origin.name} 是 {origin.plane_type.value}。"
            f"建议先通过星光投影 Astral Projection 进入星光位面，"
            f"再通过彩池前往目标位面。"
        )
        return

    # 寻找彩池耗时 1d4×10 小时
    d4_roll = rng.randint(1, 4)
    result.travel_time_hours = d4_roll * 10.0
    result.success = True
    result.message = (
        f"通过星界彩池从 {origin.name} 前往 {dest.name}。"
        f"寻找通向 {dest.name} 的彩池耗时约 {result.travel_time_hours:.0f} 小时"
        f"（1d4={d4_roll}）。彩池直径为1d6×10尺，颜色鉴别目的地。"
    )


# ──────────────────────────────────────────────────────────────────────────
# 位面危害函数
# ──────────────────────────────────────────────────────────────────────────

def apply_plane_hazards(
    plane_name: str,
    characters: list[dict],
    *,
    seed: Optional[int] = None,
) -> list[HazardResult]:
    """应用位面危害到角色列表。

    规则依据: 城主指南2024/6.宇宙学/多元宇宙之旅/*.htm
      各位面的危害效应，例如：
      - 妖精荒野：记忆丧失（DC10 感知豁免）/ 时间扭曲
      - 堕影冥界：堕影绝望（DC10 感知豁免，d6 效应表）
      - 哈迪斯：幽郁位面效应（每次长休后 DC10 感知豁免，失败获1级力竭）
      - 正位面：过载生命能量（唯有免疫光耀伤害的生物才能存活）
      - 负位面：生命吸取（唯有对暗蚀伤害免疫的存在才能长时间存活）

    Args:
        plane_name:  位面名称（中文或英文）
        characters:  角色列表，每个角色为字典，至少包含 name 和 abilities
                     abilities 应包含 str/dex/con/int/wis/cha 的分数
        seed:        随机种子

    Returns:
        HazardResult 列表，每个角色对应一个或多个危害结果

    出处: 城主指南2024/6.宇宙学/多元宇宙之旅/妖精荒野.htm 等
    """
    rng = random.Random(seed)
    plane = get_plane(plane_name)

    if plane is None:
        return [HazardResult(
            plane_name=plane_name,
            description=f"位面 {plane_name!r} 不存在，无法应用危害",
        )]

    results: list[HazardResult] = []

    for char in characters:
        char_name = char.get("name", "未知角色")
        abilities = char.get("abilities", {})
        wis_score = abilities.get("wis", 10)
        con_score = abilities.get("con", 10)
        int_score = abilities.get("int", 10)
        cha_score = abilities.get("cha", 10)

        # 根据位面类型应用不同的危害
        hazard = _resolve_hazard_for_plane(
            plane, char_name, wis_score, con_score, int_score, cha_score, rng
        )
        if hazard is not None:
            results.append(hazard)

    return results


def _ability_mod(score: int) -> int:
    """将属性分数转换为调整值。"""
    return (score - 10) // 2


def _make_save(
    mod: int, dc: int, rng: random.Random
) -> tuple[bool, int]:
    """进行一次豁免检定。

    Returns:
        (是否通过, 骰点)
    """
    roll = rng.randint(1, 20)
    total = roll + mod
    return total >= dc, roll


def _resolve_hazard_for_plane(
    plane: Plane,
    char_name: str,
    wis: int,
    con: int,
    intel: int,
    cha: int,
    rng: random.Random,
) -> Optional[HazardResult]:
    """根据位面解析具体的危害效应。"""

    # ── 妖精荒野：记忆丧失 ──
    if plane.name == "妖精荒野":
        wis_mod = _ability_mod(wis)
        passed, roll = _make_save(wis_mod, 10, rng)
        # 妖精及拥有妖精血统特质的种族自动通过
        is_fey = cha >= 14  # 简化判定：高魅力者视为有妖精血统
        if is_fey:
            passed = True
        return HazardResult(
            plane_name=plane.name,
            hazard_type="记忆丧失 Memory Loss",
            dc=10,
            save_attribute="感知",
            passed=passed,
            effect=("自动通过（妖精血统）" if is_fey else
                    ("记忆保存完整但模糊" if passed else "完全遗忘在妖精荒野中的经历")),
            description=(
                f"角色 {char_name} 离开妖精荒野时需进行 DC10 感知豁免。"
                f"掷骰 {roll} + 调整值 {wis_mod} = {roll + wis_mod}。"
                f"{'通过' if passed else '失败'}。"
            ),
        )

    # ── 堕影冥界：堕影绝望 ──
    if plane.name == "堕影冥界":
        wis_mod = _ability_mod(wis)
        passed, roll = _make_save(wis_mod, 10, rng)
        # d6 绝望效应表
        despair_roll = rng.randint(1, 6)
        if despair_roll <= 3:
            effect = "冷漠：角色在死亡豁免和先攻检定上具有劣势"
        elif despair_roll <= 5:
            effect = "恐惧：角色在所有豁免上具有劣势"
        else:
            effect = "幻觉：角色在所有基于智力、感知和魅力的属性检定和豁免上具有劣势"
        return HazardResult(
            plane_name=plane.name,
            hazard_type="堕影绝望 Shadowfell Despair",
            dc=10,
            save_attribute="感知",
            passed=passed,
            effect=effect,
            description=(
                f"角色 {char_name} 在堕影冥界长时间停留需进行 DC10 感知豁免。"
                f"掷骰 {roll} + 调整值 {wis_mod} = {roll + wis_mod}。"
                f"绝望效应掷骰 d6={despair_roll}。"
            ),
        )

    # ── 哈迪斯：幽郁位面效应 ──
    if plane.name == "哈迪斯":
        wis_mod = _ability_mod(wis)
        passed, roll = _make_save(wis_mod, 10, rng)
        exhaustion_level = 0 if passed else 1
        larva_warning = ""
        if exhaustion_level >= 6:
            larva_warning = " 力竭达到6级，角色永久化为幼虫魔 Larva！"
        return HazardResult(
            plane_name=plane.name,
            hazard_type="幽郁位面效应 Plane of Gloom",
            dc=10,
            save_attribute="感知",
            passed=passed,
            effect=f"获得 {exhaustion_level} 级无法在哈迪斯消除的力竭。{larva_warning}",
            description=(
                f"角色 {char_name} 在哈迪斯每次长休后需进行 DC10 感知豁免。"
                f"掷骰 {roll} + 调整值 {wis_mod} = {roll + wis_mod}。"
                f"{'通过，无效果' if passed else '失败，获得1级力竭'}。"
                f"当力竭等级达到6时，生物不会死亡，而是永久化为一只幼虫魔。"
            ),
        )

    # ── 正位面：过载生命能量 ──
    if plane.name == "正位面":
        con_mod = _ability_mod(con)
        # 简化判定：体质低于14的角色承受过载伤害
        overload_damage = rng.randint(1, 10) if con < 14 else 0
        return HazardResult(
            plane_name=plane.name,
            hazard_type="过载生命能量 Positive Energy Overload",
            dc=0,
            save_attribute="体质",
            passed=(overload_damage == 0),
            damage=overload_damage,
            effect=(
                "充沛的生命力使角色难以平静、难以抑制涌动的思想，甚至难以安然入眠"
                if overload_damage == 0 else
                f"凡人无法长时间承受这股力量，受到 {overload_damage} 点光耀伤害"
            ),
            description=(
                f"角色 {char_name} 踏足正位面。"
                f"唯有那些免疫光耀伤害的生物才能在此存活。"
                f"体质 {con}（调整值 {con_mod}）。"
            ),
        )

    # ── 负位面：生命吸取 ──
    if plane.name == "负位面":
        con_mod = _ability_mod(con)
        # 简化判定：体质低于14的角色承受生命吸取
        drain_damage = rng.randint(1, 10) if con < 14 else 0
        return HazardResult(
            plane_name=plane.name,
            hazard_type="生命吸取 Life Drain",
            dc=0,
            save_attribute="体质",
            passed=(drain_damage == 0),
            damage=drain_damage,
            effect=(
                "负位面的本质会逐步抽离角色的活力、能量与喜悦"
                if drain_damage == 0 else
                f"仅仅踏入这片位面就如遭遇邪灵的生命吸取，受到 {drain_damage} 点暗蚀伤害"
            ),
            description=(
                f"角色 {char_name} 踏足负位面。"
                f"唯有对暗蚀伤害免疫的存在才能在此长时间存活。"
                f"体质 {con}（调整值 {con_mod}）。"
            ),
        )

    # ── 通用：外层位面的阵营失谐 ──
    if plane.plane_type == PlaneType.OUTER:
        con_mod = _ability_mod(con)
        # 位面失谐：天族到访下层位面、邪魔到访上层位面，长休后需 DC10 体质豁免
        # 简化判定：这里只返回危害提示，不强制执行
        return HazardResult(
            plane_name=plane.name,
            hazard_type="位面失谐风险 Planar Dissonance Risk",
            dc=10,
            save_attribute="体质",
            passed=None,  # 未进行豁免，仅提示
            effect=(
                "到访与其本质相异的外层位面的天族或邪魔，"
                "若在那些位面待上超过数小时便会感觉极其不适。"
                "长休后需进行 DC10 体质豁免，失败则 D20 检定减去 1d4。"
            ),
            description=(
                f"角色 {char_name} 位于外层位面 {plane.name}。"
                f"外层位面更像是思想与道德的界域，会对访问者的身心产生影响。"
                f"阵营 {plane.alignment}。"
            ),
        )

    # 其他位面暂无特殊危害机制
    return None


# ──────────────────────────────────────────────────────────────────────────
# 传送门可达性检查
# ──────────────────────────────────────────────────────────────────────────

def check_portal_accessibility(portal: dict) -> bool:
    """检查传送门是否可达/可开启。

    规则依据: 城主指南2024/6.宇宙学/位面旅行.htm - 传送门开启条件
      传送门开启条件可以随意设定，但最常见的是以下几种：
        - 命令 Command: 给出特定的命令才会开启
        - 钥匙物品 Key Item: 携带一件特定物件才会开启
        - 随机 Random: 随机开启一段时间，允许1d6+6名旅行者通过
        - 情境 Situation: 特定条件下开启（满月/下雨/施法等）
        - 时间 Time: 物质位面上的特定时间开启

    Args:
        portal: 传送门描述字典，应包含以下字段：
            - name: 传送门名称
            - open_condition: 开启条件类型
              （command/key_item/random/situation/time）
            - has_key: 是否持有钥匙物品（布尔值，可选）
            - knows_command: 是否知道命令语（布尔值，可选）
            - current_time_match: 当前时间是否匹配（布尔值，可选）
            - situation_met: 情境条件是否满足（布尔值，可选）

    Returns:
        True 如果传送门可达且可开启，False 否则

    出处: 城主指南2024/6.宇宙学/位面旅行.htm
    """
    if not isinstance(portal, dict):
        return False

    condition = portal.get("open_condition", "").lower()

    # 无条件限制的传送门总是可达
    if not condition or condition == "none":
        return True

    if condition == "command":
        # 命令型：需要知道命令语
        return bool(portal.get("knows_command", False))

    if condition == "key_item":
        # 钥匙物品型：需要持有钥匙
        return bool(portal.get("has_key", False))

    if condition == "random":
        # 随机型：传送门随机开启一段时间
        # 此处简化为总是可达（实际应由 DM 判定或掷骰决定）
        return True

    if condition == "situation":
        # 情境型：特定条件下开启
        return bool(portal.get("situation_met", False))

    if condition == "time":
        # 时间型：物质位面上的特定时间开启
        return bool(portal.get("current_time_match", False))

    # 未知条件类型，保守起见返回 False
    return False


# ──────────────────────────────────────────────────────────────────────────
# 辅助查询函数
# ──────────────────────────────────────────────────────────────────────────

def get_travel_methods() -> list[dict]:
    """返回所有可用的位面旅行方式。

    Returns:
        旅行方式列表，每项 {"value": ..., "label": ...}

    出处: 城主指南2024/6.宇宙学/位面旅行.htm
    """
    return [
        {"value": m.name, "label": m.value}
        for m in TRAVEL_METHODS
    ]


def list_available_destinations(origin_plane: str) -> list[Plane]:
    """列出从指定出发位面可到达的目的位面。

    规则依据: 城主指南2024/6.宇宙学/位面旅行.htm
      - 从物质位面可通过传送门/法术前往大多数位面
      - 从星光位面可通过彩池前往其他位面
      - 从以太位面可通往边界以太重叠的位面
      - 外域的门镇连接各外层位面

    Args:
        origin_plane: 出发位面名称

    Returns:
        可到达的目的位面列表（不含出发位面本身）

    出处: 城主指南2024/6.宇宙学/位面旅行.htm
    """
    origin = get_plane(origin_plane)
    if origin is None:
        return []

    all_planes = list_planes()
    # 排除出发位面本身
    destinations = [p for p in all_planes if p.name != origin.name]

    # 根据出发位面类型筛选可达目的地
    if origin.plane_type == PlaneType.ASTRAL:
        # 从星光位面可通过彩池前往大多数位面
        return destinations
    elif origin.plane_type == PlaneType.ETHEREAL:
        # 从以太位面可通往边界以太重叠的位面
        return destinations
    elif origin.plane_type == PlaneType.MATERIAL:
        # 从物质位面可通过传送门/法术前往大多数位面
        return destinations
    elif origin.plane_type == PlaneType.OUTER:
        # 从外层位面可通过门镇/传送门前往其他外层位面
        return destinations
    else:
        # 其他情况默认所有位面可达
        return destinations


# ──────────────────────────────────────────────────────────────────────────
# 模块自检
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("位面旅行系统自检")
    print("规则依据: 城主指南2024/6.宇宙学/")
    print("=" * 70)
    print()

    # 测试 1: 旅行方式枚举
    print("=== 测试 1: 旅行方式枚举 ===")
    methods = get_travel_methods()
    for m in methods:
        print(f"  {m['value']}: {m['label']}")
    assert len(methods) == 5, f"应有 5 种旅行方式，实际 {len(methods)}"
    print()

    # 测试 2: 位面旅行 - 法术方式
    print("=== 测试 2: 位面旅行（法术方式）===")
    result = travel_to_plane("物质位面", "九层地狱", TRAVEL_METHODS.SPELL, seed=42)
    print(f"  成功: {result.success}")
    print(f"  方式: {result.method}")
    print(f"  耗时: {result.travel_time_hours:.1f} 小时")
    print(f"  消息: {result.message}")
    print(f"  抵达位层: {result.arrival_layer}")
    print(f"  危害数: {len(result.hazards)}")
    assert result.success, "法术旅行应该成功"
    print()

    # 测试 3: 位面旅行 - 传送门方式
    print("=== 测试 3: 位面旅行（传送门方式）===")
    result = travel_to_plane("外域", "九层地狱", TRAVEL_METHODS.PORTAL, seed=42)
    print(f"  成功: {result.success}")
    print(f"  消息: {result.message}")
    assert result.success, "传送门旅行应该成功"
    print()

    # 测试 4: 位面旅行 - 彩池方式（从非星光位面出发应失败）
    print("=== 测试 4: 位面旅行（彩池方式，错误出发点）===")
    result = travel_to_plane("物质位面", "九层地狱", TRAVEL_METHODS.COLOR_POOL, seed=42)
    print(f"  成功: {result.success}")
    print(f"  消息: {result.message}")
    assert not result.success, "从物质位面出发的彩池旅行应该失败"
    print()

    # 测试 5: 位面旅行 - 彩池方式（从星光位面出发应成功）
    print("=== 测试 5: 位面旅行（彩池方式，正确出发点）===")
    result = travel_to_plane("星光位面", "九层地狱", TRAVEL_METHODS.COLOR_POOL, seed=42)
    print(f"  成功: {result.success}")
    print(f"  消息: {result.message}")
    assert result.success, "从星光位面出发的彩池旅行应该成功"
    print()

    # 测试 6: 位面旅行 - 不存在的位面
    print("=== 测试 6: 位面旅行（不存在的位面）===")
    result = travel_to_plane("不存在的位面", "九层地狱", TRAVEL_METHODS.SPELL, seed=42)
    print(f"  成功: {result.success}")
    print(f"  消息: {result.message}")
    assert not result.success, "不存在的位面旅行应该失败"
    print()

    # 测试 7: 位面危害 - 妖精荒野记忆丧失
    print("=== 测试 7: 位面危害（妖精荒野记忆丧失）===")
    chars = [
        {"name": "战士A", "abilities": {"wis": 8, "con": 14, "int": 10, "cha": 10}},
        {"name": "法师B", "abilities": {"wis": 16, "con": 10, "int": 18, "cha": 10}},
    ]
    hazards = apply_plane_hazards("妖精荒野", chars, seed=42)
    for h in hazards:
        print(f"  角色: {h.plane_name}")
        print(f"  危害: {h.hazard_type}")
        print(f"  DC: {h.dc}, 属性: {h.save_attribute}")
        print(f"  通过: {h.passed}")
        print(f"  效应: {h.effect}")
        print(f"  描述: {h.description}")
        print()
    assert len(hazards) == 2, "应为 2 个角色各生成 1 个危害结果"
    print()

    # 测试 8: 位面危害 - 堕影冥界绝望
    print("=== 测试 8: 位面危害（堕影冥界绝望）===")
    chars = [
        {"name": "游侠C", "abilities": {"wis": 12, "con": 14, "int": 10, "cha": 10}},
    ]
    hazards = apply_plane_hazards("堕影冥界", chars, seed=100)
    for h in hazards:
        print(f"  危害: {h.hazard_type}")
        print(f"  效应: {h.effect}")
        print(f"  描述: {h.description}")
    assert len(hazards) == 1
    print()

    # 测试 9: 传送门可达性检查
    print("=== 测试 9: 传送门可达性检查 ===")
    portals = [
        {"name": "无条件传送门", "open_condition": "none"},
        {"name": "命令传送门-知道命令", "open_condition": "command", "knows_command": True},
        {"name": "命令传送门-不知道命令", "open_condition": "command", "knows_command": False},
        {"name": "钥匙传送门-有钥匙", "open_condition": "key_item", "has_key": True},
        {"name": "钥匙传送门-无钥匙", "open_condition": "key_item", "has_key": False},
        {"name": "随机传送门", "open_condition": "random"},
        {"name": "情境传送门-满足", "open_condition": "situation", "situation_met": True},
        {"name": "情境传送门-不满足", "open_condition": "situation", "situation_met": False},
        {"name": "时间传送门-匹配", "open_condition": "time", "current_time_match": True},
        {"name": "时间传送门-不匹配", "open_condition": "time", "current_time_match": False},
    ]
    for p in portals:
        accessible = check_portal_accessibility(p)
        print(f"  {p['name']}: {'可达' if accessible else '不可达'}")
    print()

    # 测试 10: 可达目的地列表
    print("=== 测试 10: 可达目的地列表 ===")
    dests = list_available_destinations("物质位面")
    print(f"  从物质位面可到达 {len(dests)} 个位面")
    assert len(dests) > 0, "应至少有 1 个可达目的地"
    print()

    print("=" * 70)
    print("自检完成，所有测试通过。")
    print("=" * 70)
