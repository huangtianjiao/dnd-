"""法术数据表 — Phase G 施法流程完善。

每个法术条目含：name, level(0-9), school, casting_time, range,
components(V/S/M), duration, concentration(bool), ritual(bool),
effect_type(attack_roll/saving_throw/automatic/heal/shield),
save_ability, damage(dice_expr+type 或 None), upcast(升环说明或None),
description, material_cost_gp, material_consumed.

标注约定：每条规则实现处标注 RULE_SPEC.md 的规则点 ID + 原文出处路径
（topics/玩家手册2024/...）。

规则依据 R-SPL-001~036；
数据来源 topics/玩家手册2024/法术详述/{0..9}环.htm（391个法术，自动生成）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────
# 法术数据结构
# ──────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Spell:
    """单个法术的完整数据。

    规则: R-SPL-001 法术环阶0-9 / R-SPL-010 成分V,S,M / R-SPL-014 距离 /
          R-SPL-017 持续时间 / R-SPL-035 学派
    出处: topics/玩家手册2024/法术详述/{0..3}环.htm
    """
    name: str                               # 中文名
    en_name: str                            # 英文名
    level: int                              # 环阶 0-9 (R-SPL-001)
    school: str                             # 魔法学派 (R-SPL-035)
    casting_time: str                       # 施法时间描述 (R-SPL-006)
    casting_time_type: str                  # ACTION/BONUS_ACTION/REACTION/TIME
    range: str                              # 施法距离描述 (R-SPL-014)
    components: frozenset[str]              # 成分子集 {"V","S","M"} (R-SPL-010)
    material_desc: str = ""                 # 材料成分描述
    material_cost_gp: float = 0.0           # 材料指定价格 (>0 则须实备)
    material_consumed: bool = False         # 材料是否被消耗
    duration: str = "立即"                  # 持续时间描述 (R-SPL-017)
    concentration: bool = False             # 是否需要专注 (R-SPL-019)
    ritual: bool = False                    # 是否可仪式施法 (R-SPL-005)
    effect_type: str = "automatic"          # attack_roll/saving_throw/automatic/heal/shield
    save_ability: Optional[str] = None      # 豁免属性 DEX/CON/WIS/CHA/INT/STR
    damage_dice: Optional[str] = None       # 伤害骰表达式 如 "1d10"
    damage_type: Optional[str] = None       # 伤害类型 如 "fire"
    heal_dice: Optional[str] = None         # 治疗骰表达式 如 "2d8"
    add_casting_mod_to_heal: bool = False   # 治疗是否加施法属性调整值
    ac_bonus: int = 0                       # 护甲加值 (护盾术 +5)
    upcast: Optional[dict] = None           # 升环效应 {per_level: dice_expr 或 count}
    description: str = ""
    class_list: tuple[str, ...] = ()        # 可施展职业列表 (R-SPL-036)


# ──────────────────────────────────────────────────────────────────────────
# 法术位进度表（每职业每等级各环阶法术位数量）
# 规则: R-SPL-002 法术位消耗 / R-SPL-003 长休恢复
# 出处: topics/玩家手册2024/法术/法术环阶.htm
# ──────────────────────────────────────────────────────────────────────────

# 标准施法者法术位表 [level_index] -> {slot_level: count}
# level_index 0 = 1级, ..., 19 = 20级
SPELL_SLOTS_BY_LEVEL: list[dict[int, int]] = [
    {1: 2},                                    # 1级
    {1: 3},                                    # 2级
    {1: 4, 2: 2},                              # 3级
    {1: 4, 2: 3},                              # 4级
    {1: 4, 2: 3, 3: 2},                        # 5级
    {1: 4, 2: 3, 3: 3},                        # 6级
    {1: 4, 2: 3, 3: 3, 4: 1},                  # 7级
    {1: 4, 2: 3, 3: 3, 4: 2},                  # 8级
    {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},            # 9级
    {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},            # 10级
    {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},      # 11级
    {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},      # 12级
    {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},# 13级
    {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},# 14级
    {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1}, # 15级
    {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1}, # 16级
    {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1}, # 17级
    {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1}, # 18级
    {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1}, # 19级
    {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1}, # 20级
]


def max_spell_slots(caster_level: int) -> dict[int, int]:
    """返回该等级施法者的最大法术位表。

    规则: R-SPL-002 法术位消耗 / R-SPL-003 长休恢复
    出处: topics/玩家手册2024/法术/法术环阶.htm
    """
    if caster_level < 1:
        return {}
    idx = min(caster_level - 1, len(SPELL_SLOTS_BY_LEVEL) - 1)
    return dict(SPELL_SLOTS_BY_LEVEL[idx])


# ──────────────────────────────────────────────────────────────────────────
# 施法属性映射
# 规则: R-SPL-021 法术豁免DC = 8 + 施法属性调整值 + 熟练加值
#       R-SPL-022 法术攻击加值 = 施法属性调整值 + 熟练加值
# 出处: topics/玩家手册2024/法术/法术效应.htm
# ──────────────────────────────────────────────────────────────────────────

CASTING_ABILITY_BY_CLASS: dict[str, str] = {
    "法师": "INT",
    "术士": "CHA",
    "魔契师": "CHA",
    "吟游诗人": "CHA",
    "圣武士": "CHA",
    "牧师": "WIS",
    "德鲁伊": "WIS",
    "游侠": "WIS",
}


def get_casting_ability(class_name: str) -> str:
    """取职业对应的施法属性缩写。

    规则: R-SPL-021/R-SPL-022 施法属性
    出处: topics/玩家手册2024/法术/法术效应.htm
    说明: 法师=智力(INT)，牧师/德鲁伊/游侠=感知(WIS)，
          吟游诗人/术士/魔契师/圣武士=魅力(CHA)。
    """
    if class_name not in CASTING_ABILITY_BY_CLASS:
        raise ValueError(f"未知施法职业 {class_name!r}，可选: {list(CASTING_ABILITY_BY_CLASS)}")
    return CASTING_ABILITY_BY_CLASS[class_name]


# ──────────────────────────────────────────────────────────────────────────
# 法术数据表 — 从自动生成文件导入
# 数据来源: topics/玩家手册2024/法术详述/{0..9}环.htm
# 生成脚本: aidm/scripts/extract_spells.py
# ──────────────────────────────────────────────────────────────────────────

from aidm.data._spells_data import _SPELLS_LIST, SPELLS  # noqa: E402, F401

# ── 扩展法术（XGtE + TCoE，自动生成）─────────────────────────────────────
# 若数据文件存在则导入并合并到 SPELLS
try:
    from aidm.data._expansion_spells_data import _EXPANSION_SPELLS_LIST  # noqa: E402
    _expansion_count = 0
    for _raw in _EXPANSION_SPELLS_LIST:
        _spell = Spell(
            name=_raw["name"],
            en_name=_raw.get("name_en", ""),
            level=_raw["level"],
            school=_raw["school"],
            casting_time=_raw["casting_time"],
            casting_time_type=_raw.get("casting_time_type", "ACTION"),
            range=_raw["spell_range"],
            components=frozenset(_raw.get("components", [])),
            material_desc=_raw.get("material_desc", ""),
            material_cost_gp=_raw.get("material_cost", 0.0),
            material_consumed=_raw.get("material_consumed", False),
            duration=_raw["duration"],
            concentration=_raw.get("concentration", False),
            ritual=_raw.get("ritual", False),
            effect_type=_raw.get("effect_type", "automatic"),
            save_ability=_raw.get("save_ability"),
            damage_dice=_raw.get("damage_dice"),
            damage_type=_raw.get("damage_type"),
            heal_dice=_raw.get("heal_dice"),
            ac_bonus=_raw.get("ac_bonus", 0),
            add_casting_mod_to_heal=_raw.get("add_casting_mod_to_heal", False),
            upcast=_raw.get("upcast"),
            description=_raw["description"],
            class_list=tuple(_raw.get("class_list", [])),
        )
        if _spell.name not in SPELLS:
            SPELLS[_spell.name] = _spell
            _expansion_count += 1
    if _expansion_count:
        print(f"[spells] 已合并 {_expansion_count} 个扩展法术 (XGtE+TCoE)")
except ImportError:
    pass  # 扩展数据文件尚未生成


def get_spell(name: str) -> Spell:
    """按中文名取法术条目。

    规则: R-SPL-001 法术环阶范围
    出处: topics/玩家手册2024/法术详述/{0..9}环.htm
    """
    if name not in SPELLS:
        raise KeyError(f"未知法术 {name!r}，可选: {sorted(SPELLS)}")
    return SPELLS[name]


def is_cantrip(spell: Spell) -> bool:
    """是否为戏法（0环，不消耗法术位）。

    规则: R-SPL-001 cantrip=(level==0)
    出处: topics/玩家手册2024/法术/法术环阶.htm
    """
    return spell.level == 0


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 法术数量 ≥ 10
    assert len(SPELLS) >= 10, f"法术数量不足: {len(SPELLS)}"
    # 环阶范围合法 (R-SPL-001)
    for name, s in list(SPELLS.items())[:100]:  # 抽查前100个
        assert 0 <= s.level <= 9, f"{name}: 环阶越界 {s.level}"
        assert s.components <= {"V", "S", "M"}, f"{name}: 成分越界 {s.components}"
    # 关键法术存在
    for nm in ["火焰箭", "光亮术", "法师之手", "魔法飞弹", "治愈真言",
               "护盾术", "灼热射线", "隐形术", "火球术", "闪电束"]:
        assert nm in SPELLS, f"缺少法术 {nm}"
    # 火焰箭: 0环 塑能 1d10 fire (R-SPL-001)
    fb = get_spell("火焰箭")
    assert fb.level == 0 and fb.school == "塑能"
    assert fb.damage_dice == "1d10" and fb.damage_type == "fire"
    assert is_cantrip(fb)
    # 魔法飞弹: 1环 自动命中 1d4+1 force (R-SPL-024)
    mm = get_spell("魔法飞弹")
    assert mm.level == 1 and mm.effect_type in ("automatic", "attack_roll")
    assert mm.damage_dice and "d4" in mm.damage_dice
    assert mm.damage_type == "force"
    # 护盾术: 反应 +5 AC (R-SPL-006)
    sh = get_spell("护盾术")
    assert sh.casting_time_type == "REACTION" and sh.ac_bonus == 5
    # 火球术: 3环 DEX豁免 8d6 fire (R-SPL-021)
    fba = get_spell("火球术")
    assert fba.level == 3 and fba.save_ability == "DEX"
    assert fba.damage_dice == "8d6" and fba.damage_type == "fire"
    # 治愈真言: 附赠动作 治疗 2d4+施法属性 (R-SPL-006)
    hw = get_spell("治愈真言")
    assert hw.casting_time_type == "BONUS_ACTION" and hw.heal_dice == "2d4"
    assert hw.add_casting_mod_to_heal is True
    # 隐形术: 专注 (R-SPL-019)
    inv = get_spell("隐形术")
    assert inv.concentration is True
    # 施法属性映射 (R-SPL-021)
    assert get_casting_ability("法师") == "INT"
    assert get_casting_ability("牧师") == "WIS"
    assert get_casting_ability("圣武士") == "CHA"
    # 法术位表 (R-SPL-002)
    slots3 = max_spell_slots(3)
    assert slots3 == {1: 4, 2: 2}, slots3
    slots9 = max_spell_slots(9)
    assert slots9[1] == 4 and slots9[5] == 1, slots9
    print(f"[spells] 自检通过 ✓ ({len(SPELLS)} 个法术)")


if __name__ == "__main__":
    _self_test()
