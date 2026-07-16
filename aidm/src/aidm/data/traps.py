"""陷阱与危害数据 — DMG 2024 第三章。

来源: 城主指南2024/3.地下城主工具箱/陷阱.htm
提供: 范例陷阱(11种) + 危害(5种) + 诅咒与魔法疫病
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Trap:
    """陷阱数据模型。"""
    name: str
    name_en: str
    severity: str            # "致命" or "妨碍"
    level_range: str         # "1-4", "5-10", etc.
    trigger: str
    duration: str
    effect: str              # 效应描述
    save_dc: Optional[int] = None
    save_ability: str = ""   # DEX/CON/WIS/etc
    damage: str = ""         # e.g. "2d10钝击"
    damage_on_save: str = "half"
    detect_dc: Optional[int] = None
    detect_skill: str = "察觉"
    disarm_dc: Optional[int] = None
    disarm_skill: str = ""
    description: str = ""


@dataclass
class Hazard:
    """危害数据模型（环境危害）。"""
    name: str
    name_en: str
    description: str
    severity: str = "可变"


# ──────────────────────────────────────────────────────────────────────────
# DMG 2024 范例陷阱 (11种)
# ──────────────────────────────────────────────────────────────────────────

TRAPS: dict[str, Trap] = {}

def _register_trap(t: Trap):
    TRAPS[t.name] = t

_register_trap(Trap(
    name="塌方", name_en="Collapsing Roof",
    severity="致命", level_range="1-4",
    trigger="生物穿过绊线时",
    duration="立即",
    effect="绊线触发天花板塌陷。区域内所有生物通过DC13敏捷豁免，失败受11(2d10)钝击伤害，成功减半。塌陷区域变为困难地形。",
    save_dc=13, save_ability="DEX",
    damage="2d10钝击",
    detect_dc=11, detect_skill="察觉",
    disarm_skill="绊线可被轻易剪断或避开（无需属性检定）。",
    description="该陷阱以绊线触发天花板的不稳定区域。绊线离地3英寸，架在两个脆弱的支撑柱之间。",
))

_register_trap(Trap(
    name="落网", name_en="Falling Net",
    severity="妨碍", level_range="1-4",
    trigger="生物穿过绊线时",
    duration="立即",
    effect="触发后10尺见方捕网落下。目标须通过DC10敏捷豁免，否则陷入束缚直至挣脱。巨型或更大目标自动通过。挣脱需DC10力量(运动)检定。",
    save_dc=10, save_ability="DEX",
    detect_dc=11, detect_skill="察觉",
    disarm_skill="绊线可被轻易剪断或避开（无需属性检定）。",
    description="陷阱使用绊线释放悬挂在天花板上的捕网。",
))

_register_trap(Trap(
    name="喷火雕像", name_en="Fire-casting Statue",
    severity="致命", level_range="1-4",
    trigger="生物移至压力板上或在其上开始回合",
    duration="立即，下一回合开始时重置",
    effect="雕像喷吐15尺锥状魔法烈焰。区域内每个生物须通过DC15敏捷豁免，失败受11(2d10)火焰伤害，成功减半。",
    save_dc=15, save_ability="DEX",
    damage="2d10火焰",
    detect_dc=15, detect_skill="察觉",
    disarm_dc=15, disarm_skill="巧手",
    description="压力板连接着隐藏的魔法雕像，可重复触发。",
))

_register_trap(Trap(
    name="陷坑", name_en="Hidden Pit",
    severity="妨碍", level_range="1-4",
    trigger="生物走入其上时",
    duration="立即",
    effect="生物落入10尺深的陷坑，受3(1d6)钝击伤害并陷入倒地。陷坑底部可能有尖刺，增加7(2d6)穿刺伤害。",
    save_dc=10, save_ability="DEX",
    damage="1d6钝击",
    detect_dc=15, detect_skill="察觉",
    description="陷坑的盖板隐藏得如同普通地面。生物可用搜索动作进行感知(察觉)检定以侦测。",
))

_register_trap(Trap(
    name="毒镖陷阱", name_en="Poisoned Dart Trap",
    severity="致命", level_range="1-4",
    trigger="生物打开被设下陷阱的宝箱或门时",
    duration="立即",
    effect="一根或多根毒镖从隐藏的位置射出。目标须通过DC15敏捷豁免，否则受5(1d10)穿刺伤害和11(2d10)毒素伤害，豁免成功则伤害减半。陷入中毒状态1小时。",
    save_dc=15, save_ability="DEX",
    damage="1d10穿刺+2d10毒素",
    detect_dc=15, detect_skill="察觉",
    disarm_dc=15, disarm_skill="巧手",
    description="毒镖隐藏在钥匙孔或其他触发机制附近。",
))

_register_trap(Trap(
    name="滚石", name_en="Rolling Stone",
    severity="致命", level_range="1-4",
    trigger="生物穿过绊线或踏入触发区域时",
    duration="立即",
    effect="巨大的石球滚过20尺宽10尺高的走廊。区域内所有生物须通过DC15敏捷豁免，失败受22(4d10)钝击伤害，成功减半。豁免失败的生物被推至区域边缘并倒地。",
    save_dc=15, save_ability="DEX",
    damage="4d10钝击",
    detect_dc=10, detect_skill="察觉",
    disarm_skill="可用楔子或支柱阻止滚石（DC15力量检定）。",
    description="隐藏在天花板或通道上方的巨石被触发后滚落。",
))

_register_trap(Trap(
    name="睡眠毒气", name_en="Sleep Gas Trap",
    severity="妨碍", level_range="5-10",
    trigger="生物打开宝箱、门或进入房间时",
    duration="1分钟",
    effect="10尺半径区域内充满魔法毒气。区域内每个生物须通过DC13体质豁免，否则陷入昏迷1分钟，或直至受到伤害或有人用动作将其唤醒。毒气在1分钟后消散。",
    save_dc=13, save_ability="CON",
    detect_dc=15, detect_skill="察觉",
    disarm_dc=15, disarm_skill="巧手",
    description="密闭容器或房间在打开时释放睡眠气体。",
))

_register_trap(Trap(
    name="闪电线圈", name_en="Lightning Coil Trap",
    severity="致命", level_range="5-10",
    trigger="生物进入线圈10尺范围内时",
    duration="立即，每轮重置",
    effect="魔法线圈对触发区域内的所有生物造成22(4d10)闪电伤害和22(4d10)雷鸣伤害。区域内生物须通过DC15敏捷豁免，失败受全额伤害，成功减半。",
    save_dc=15, save_ability="DEX",
    damage="4d10闪电+4d10雷鸣",
    detect_dc=15, detect_skill="察觉",
    disarm_dc=15, disarm_skill="奥秘",
    description="一组充能的魔法线圈不断释放电能。",
))

_register_trap(Trap(
    name="湮灭之球", name_en="Sphere of Annihilation Trap",
    severity="致命", level_range="11-16",
    trigger="生物进入球的10尺范围内或在其范围内开始回合",
    duration="持续（球存在直至移动出区域）",
    effect="一个2尺直径的黑色球体悬浮在空中。球体10尺内生物回合开始时受22(4d10)力场伤害。任何接触球的生物须通过DC17敏捷豁免，失败受44(8d10)力场伤害，成功减半。被球触碰的生物若生命值降至0则被湮灭。",
    save_dc=17, save_ability="DEX",
    damage="4d10力场(范围)/8d10力场(接触)",
    detect_dc=20, detect_skill="奥秘",
    disarm_dc=20, disarm_skill="奥秘",
    description="一个微小的湮灭之球被魔法固定在特定位置。球体消灭任何接触它的物质。",
))

_register_trap(Trap(
    name="流星风暴符文", name_en="Meteor Swarm Rune Trap",
    severity="致命", level_range="17-20",
    trigger="生物触碰雕有符文的物件或进入触发区域时",
    duration="立即",
    effect="符文释放出类似9环法术流星爆的效应。选择四个40尺半径球状区域，区域内每个生物须通过DC19敏捷豁免，失败受20d6火焰+20d6钝击伤害，成功减半。",
    save_dc=19, save_ability="DEX",
    damage="20d6火焰+20d6钝击",
    detect_dc=20, detect_skill="奥秘",
    disarm_dc=20, disarm_skill="奥秘",
    description="最强大的魔法陷阱之一，雕有星辰符文的远古遗物。",
))

_register_trap(Trap(
    name="即死符文", name_en="Symbol of Death Trap",
    severity="致命", level_range="17-20",
    trigger="生物看到或触碰符文时",
    duration="立即",
    effect="符文化为60尺半径的死亡能量爆发。区域内每个生物须通过DC20体质豁免，失败受55(10d10)暗蚀伤害并HP上限减少等量数值，成功受半伤且无减上限效果。",
    save_dc=20, save_ability="CON",
    damage="10d10暗蚀",
    detect_dc=20, detect_skill="奥秘",
    disarm_dc=20, disarm_skill="奥秘",
    description="雕有死亡符文的魔法陷阱，凡人靠近即触发。",
))


# ──────────────────────────────────────────────────────────────────────────
# DMG 2024 危害 (5种)
# ──────────────────────────────────────────────────────────────────────────

HAZARDS: dict[str, Hazard] = {}

_register_hazard = lambda h: HAZARDS.update({h.name: h})

_register_hazard(Hazard(
    name="塌方区", name_en="Cave-in Zone",
    description="不稳定的天花板或墙壁随时可能坍塌。踏入区域的生物引发塌方：15尺半径内所有生物须通过DC15敏捷豁免，失败受10(3d6)钝击伤害并被掩埋（束缚+窒息），成功减半且不被掩埋。",
))

_register_hazard(Hazard(
    name="激流", name_en="Strong Current",
    description="汹涌的水流将生物向下游推动。进入或开始于激流中的生物须通过DC15力量(运动)检定，失败被推动60尺并受7(2d6)钝击伤害。水流速度为60尺/轮。",
))

_register_hazard(Hazard(
    name="岩浆", name_en="Lava",
    description="接触岩浆的生物每轮受55(10d10)火焰伤害。浸入岩浆受99(18d10)火焰伤害。岩浆散发出的热量对10尺内生物每轮造成2d10火焰伤害。",
))

_register_hazard(Hazard(
    name="酸池", name_en="Acid Pool",
    description="绿色发泡的腐蚀性液体。接触酸池的生物受22(4d10)强酸伤害。浸入酸池的生物受44(8d10)强酸伤害。强酸会持续腐蚀金属和非魔法物品。",
))

_register_hazard(Hazard(
    name="极寒", name_en="Extreme Cold",
    description="每小时的极寒暴露中，生物须通过DC10体质豁免，失败获得一级力竭。穿着抗寒服装或具有寒冷抗性的生物自动通过。当温度低于-20华氏度时，豁免DC每降低10度+1。",
))


# ──────────────────────────────────────────────────────────────────────────
# 查询函数
# ──────────────────────────────────────────────────────────────────────────

def get_trap(name: str) -> Optional[Trap]:
    return TRAPS.get(name)

def get_hazard(name: str) -> Optional[Hazard]:
    return HAZARDS.get(name)

def traps_by_severity(severity: str) -> list[Trap]:
    return [t for t in TRAPS.values() if t.severity == severity]

def traps_by_level_range(level: int) -> list[Trap]:
    """返回对该等级角色有效的陷阱。"""
    result = []
    for t in TRAPS.values():
        parts = t.level_range.split('-')
        if len(parts) == 2:
            lo, hi = int(parts[0]), int(parts[1])
            if lo <= level <= hi:
                result.append(t)
    return result

def hazards_by_name(query: str) -> list[Hazard]:
    q = query.lower()
    return [h for h in HAZARDS.values() if q in h.name or q in h.name_en.lower()]


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    assert len(TRAPS) >= 10, f"陷阱不足: {len(TRAPS)}"
    assert len(HAZARDS) >= 4, f"危害不足: {len(HAZARDS)}"

    # 致命陷阱存在
    deadly = traps_by_severity("致命")
    assert len(deadly) >= 6, f"致命陷阱不足: {len(deadly)}"

    # 1-4级陷阱
    low_traps = traps_by_level_range(3)
    assert len(low_traps) >= 5, f"1-4级陷阱不足: {len(low_traps)}"

    # 塌方查询
    t = get_trap("塌方")
    assert t is not None and t.save_dc == 13

    print(f"[traps] 自检通过 ✓ ({len(TRAPS)}陷阱 + {len(HAZARDS)}危害)")


if __name__ == "__main__":
    _self_test()
