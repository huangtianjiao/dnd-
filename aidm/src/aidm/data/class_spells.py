"""职业法术列表 — 每个职业的可施法池。

基于 spells.py 中每个法术的 class_list 字段自动汇总。
提供按职业/环阶查询法术的能力，是 spellcasting engine 的前置数据层。

规则依据 R-SPL-036 职业法术列表；
数据来源 aidm/data/_spells_data.py（391个法术）。
"""

from __future__ import annotations

from collections import defaultdict
from typing import Optional

from aidm.data.spells import Spell, SPELLS

# ──────────────────────────────────────────────────────────────────────────
# 核心数据结构：CLASS_SPELLS[class_name][level] → list[Spell]
# ──────────────────────────────────────────────────────────────────────────

CLASS_SPELLS: dict[str, dict[int, list[Spell]]] = {}

# Build from SPELLS data, normalizing class names
_raw: dict[str, dict[int, list[Spell]]] = defaultdict(lambda: defaultdict(list))
for spell in SPELLS.values():
    for raw_cls in spell.class_list:
        # Normalize class names: "仪式；牧师" → "牧师", "仪式；吟游诗人" → "吟游诗人"
        # Also handle "仪式；法师" etc.
        cls_name = raw_cls.strip()
        if "；" in cls_name:
            # Split and take the actual class name (second part)
            cls_name = cls_name.split("；")[-1].strip()
        if ";" in cls_name:
            cls_name = cls_name.split(";")[-1].strip()
        if not cls_name:
            continue
        _raw[cls_name][spell.level].append(spell)

# Sort each level's spells by name for determinism
for cls_name in _raw:
    CLASS_SPELLS[cls_name] = {}
    for level in sorted(_raw[cls_name]):
        CLASS_SPELLS[cls_name][level] = sorted(_raw[cls_name][level], key=lambda s: s.name)


# ──────────────────────────────────────────────────────────────────────────
# 职业施法起始等级
#
# 规则: R-CLS-010 施法特性起始等级
# 出处: topics/玩家手册2024/角色职业/<职业>/<职业>.htm
#
# 半施法者（圣武士/游侠）在职业等级2才获得施法能力；
# 1/3施法者（奥法骑士/诡术师）在职业等级3才获得施法能力。
# ──────────────────────────────────────────────────────────────────────────

CASTER_START_LEVEL: dict[str, int] = {
    "法师": 1,
    "术士": 1,
    "牧师": 1,
    "吟游诗人": 1,
    "德鲁伊": 1,
    "魔契师": 1,
    "圣武士": 2,      # 半施法者
    "游侠": 2,        # 半施法者
}


# ──────────────────────────────────────────────────────────────────────────
# 最大已知法术数 / 准备法术数（简化规则）
#
# 规则: R-CLS-011 已知法术表 / R-CLS-012 准备法术
# 出处: topics/玩家手册2024/角色职业/<职业>/法术表.htm
#
# 说明:
#   - 已知施法者（术士/吟游诗人/魔契师/游侠）：固定数量的已知法术
#   - 准备施法者（法师/牧师/德鲁伊/圣武士）：每次长休从职业法术列表中准备
#        准备数量 = 施法属性调整值 + 职业等级
#        法师另有法术书机制（每升一级可抄写2个法术）
# ──────────────────────────────────────────────────────────────────────────

# 已知施法者：每级最大已知法术数
# [class_level_index] -> max_known
KNOWN_SPELLS_MAX: dict[str, list[int]] = {
    # 术士：1级2个，每级+1，上限15
    "术士": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 15, 15, 15, 15, 15, 15],
    # 吟游诗人：1级4个，之后每级+1，上限22
    "吟游诗人": [4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 15, 16, 18, 19, 19, 20, 22, 22, 22],
    # 魔契师：1级2个，之后每级+1，上限15（另有魔能祈唤扩展）
    "魔契师": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 15, 15, 15, 15, 15, 15],
    # 游侠：2级2个，之后每级+1（spells_known表，2级=level_index 1）
    "游侠": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15],
}


def get_max_slot_level_for_class(class_name: str, char_level: int) -> int:
    """该职业在该等级能施展的最高法术环阶。

    规则: R-SPL-002 法术位表
    出处: topics/玩家手册2024/角色职业/<职业>/<职业>法术位表.htm

    注意: 圣武士/游侠是半施法者，施法者等级 = floor(char_level/2).
    """
    if class_name in ("圣武士", "游侠"):
        # 半施法者环阶解锁: 1级(1环), 5级(2环), 9级(3环), 13级(4环), 17级(5环)
        # 公式: max_slot = (level + 1) // 4 + 1, 上限5
        return min(5, (char_level + 1) // 4 + 1)
    else:
        effective_level = char_level

    # 标准施法者环阶解锁
    if effective_level >= 17:
        return 9
    elif effective_level >= 15:
        return 8
    elif effective_level >= 13:
        return 7
    elif effective_level >= 11:
        return 6
    elif effective_level >= 9:
        return 5
    elif effective_level >= 7:
        return 4
    elif effective_level >= 5:
        return 3
    elif effective_level >= 3:
        return 2
    elif effective_level >= 1:
        return 1
    return 0


def get_max_known_spells(class_name: str, char_level: int) -> int:
    """已知施法者在该等级的最大已知法术数。

    准备施法者返回 -1（通过准备机制，无固定上限）。
    """
    if class_name not in KNOWN_SPELLS_MAX:
        return -1  # 准备施法者
    idx = min(char_level - 1, len(KNOWN_SPELLS_MAX[class_name]) - 1)
    if idx < 0:
        return 0
    return KNOWN_SPELLS_MAX[class_name][idx]


# ──────────────────────────────────────────────────────────────────────────
# 查询接口
# ──────────────────────────────────────────────────────────────────────────

def get_class_spells(class_name: str, level: Optional[int] = None) -> list[Spell]:
    """获取某职业的全部法术，或指定环阶的法术。

    参数:
        class_name: 职业中文名
        level: 环阶 0-9，None 返回所有环阶

    返回: Spell 列表（按名称排序）
    """
    if class_name not in CLASS_SPELLS:
        raise KeyError(f"未知职业 {class_name!r}，可选: {list(CLASS_SPELLS)}")
    if level is not None:
        return list(CLASS_SPELLS[class_name].get(level, []))
    # 返回所有环阶法术，按环阶→名称排序
    result: list[Spell] = []
    for lv in sorted(CLASS_SPELLS[class_name]):
        result.extend(CLASS_SPELLS[class_name][lv])
    return result


def get_class_cantrips(class_name: str) -> list[Spell]:
    """获取某职业的戏法列表。

    规则: R-SPL-001 cantrip=(level==0)
    """
    return get_class_spells(class_name, level=0)


def get_spells_known_at_level(class_name: str, char_level: int) -> list[Spell]:
    """获取该职业在该角色等级下能够施展的所有法术。

    规则: R-SPL-036 职业法术列表 × R-SPL-002 法术位解锁

    返回: 所有环阶 ≤ 当前最高法术位的该职业法术。
    """
    max_slot = get_max_slot_level_for_class(class_name, char_level)
    spells: list[Spell] = []
    cls_data = CLASS_SPELLS.get(class_name, {})
    for lv in sorted(cls_data):
        if lv <= max_slot:
            spells.extend(cls_data[lv])
    return spells


def get_spells_available_at_level(class_name: str, char_level: int) -> dict[int, list[Spell]]:
    """获取该职业在该角色等级下按环阶分组的可施展法术。

    返回: {0: [戏法列表], 1: [1环], ..., N: [N环]}
    """
    max_slot = get_max_slot_level_for_class(class_name, char_level)
    result: dict[int, list[Spell]] = {}
    cls_data = CLASS_SPELLS.get(class_name, {})
    for lv in sorted(cls_data):
        if lv <= max_slot:
            result[lv] = list(cls_data[lv])
    return result


def is_class_spell(class_name: str, spell_name: str) -> bool:
    """判断某法术是否在某职业的法术列表中。"""
    if class_name not in CLASS_SPELLS:
        return False
    spell = SPELLS.get(spell_name)
    if spell is None:
        return False
    return class_name in spell.class_list


def search_class_spells(class_name: str, keyword: str,
                        level: Optional[int] = None) -> list[Spell]:
    """在某职业法术列表中模糊搜索。

    参数:
        class_name: 职业中文名
        keyword: 搜索关键词（匹配法术中文名/英文名/学派/描述）
        level: 限制环阶（可选）
    """
    results: list[Spell] = []
    spells = get_class_spells(class_name, level=level)
    kw_lower = keyword.lower()
    for s in spells:
        if (kw_lower in s.name or
                kw_lower in s.en_name.lower() or
                kw_lower in s.school or
                kw_lower in s.description):
            results.append(s)
    return results


def class_has_spell_level(class_name: str, spell_level: int) -> bool:
    """该职业的法术列表中是否有该环阶的法术。"""
    if class_name not in CLASS_SPELLS:
        return False
    return spell_level in CLASS_SPELLS[class_name]


def get_spell_count_by_class() -> dict[str, dict[int, int]]:
    """返回每个职业每环阶的法术数量统计。

    返回: {"法师": {0: 20, 1: 31, ...}, ...}
    """
    result: dict[str, dict[int, int]] = {}
    for cls_name in sorted(CLASS_SPELLS):
        result[cls_name] = {}
        for level in sorted(CLASS_SPELLS[cls_name]):
            result[cls_name][level] = len(CLASS_SPELLS[cls_name][level])
    return result


# ──────────────────────────────────────────────────────────────────────────
# 法术学校筛选
# ──────────────────────────────────────────────────────────────────────────

MAGIC_SCHOOLS = [
    "防护", "咒法", "预言", "附魔", "塑能",
    "幻术", "死灵", "变化",
]

SCHOOL_EN_MAP = {
    "防护": "Abjuration", "咒法": "Conjuration", "预言": "Divination",
    "附魔": "Enchantment", "塑能": "Evocation", "幻术": "Illusion",
    "死灵": "Necromancy", "变化": "Transmutation",
}


def get_class_spells_by_school(class_name: str, school: str) -> dict[int, list[Spell]]:
    """按学派获取某职业的法术（按环阶分组）。"""
    result: dict[int, list[Spell]] = defaultdict(list)
    for level_spells in CLASS_SPELLS.get(class_name, {}).values():
        for s in level_spells:
            if s.school == school:
                result[s.level].append(s)
    return dict(result)


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 8 个施法职业
    assert len(CLASS_SPELLS) >= 8, f"应有至少8个职业，实有{len(CLASS_SPELLS)}"
    assert "法师" in CLASS_SPELLS
    assert "牧师" in CLASS_SPELLS
    assert "圣武士" in CLASS_SPELLS
    assert "游侠" in CLASS_SPELLS

    # 法师法术数量 (R-SPL-036)
    wiz_all = get_class_spells("法师")
    assert len(wiz_all) >= 240, f"法师应有大量法术，实有{len(wiz_all)}"
    # 法师戏法
    wiz_0 = get_class_cantrips("法师")
    assert len(wiz_0) >= 20, f"法师应有大量戏法，实有{len(wiz_0)}"
    # 法师1环
    wiz_1 = get_class_spells("法师", level=1)
    assert len(wiz_1) >= 30, f"法师应有大量1环法术，实有{len(wiz_1)}"
    assert any(s.name == "魔法飞弹" for s in wiz_1)
    assert any(s.name == "护盾术" for s in wiz_1)

    # 牧师法术
    cle_all = get_class_spells("牧师")
    assert len(cle_all) >= 100
    assert any(s.name == "治愈真言" for s in cle_all)
    assert any(s.name == "灵体武器" for s in cle_all)

    # 圣武士（半施法者，无戏法，最高5环）
    pal_all = get_class_spells("圣武士")
    assert len(pal_all) >= 50
    assert len(get_class_cantrips("圣武士")) == 0  # 圣武士无戏法
    assert get_max_slot_level_for_class("圣武士", 5) == 2   # 半施法者5级→2环
    assert get_max_slot_level_for_class("圣武士", 9) == 3   # 半施法者9级→3环

    # 法术位解锁 (R-SPL-002)
    assert get_max_slot_level_for_class("法师", 1) == 1
    assert get_max_slot_level_for_class("法师", 5) == 3
    assert get_max_slot_level_for_class("法师", 9) == 5
    assert get_max_slot_level_for_class("游侠", 5) == 2

    # class spell check
    assert is_class_spell("法师", "火球术") is True
    assert is_class_spell("牧师", "火球术") is False
    assert is_class_spell("圣武士", "至圣斩") is True
    assert is_class_spell("战士", "魔法飞弹") is False

    # 已知法术数
    assert get_max_known_spells("术士", 1) == 2
    assert get_max_known_spells("术士", 10) == 11
    assert get_max_known_spells("法师", 5) == -1  # 准备施法者
    assert get_max_known_spells("牧师", 3) == -1  # 准备施法者

    # search
    fire_spells = search_class_spells("法师", "火")
    assert len(fire_spells) >= 5  # 火焰箭、火球术、火焰护盾等

    # spell count stats
    stats = get_spell_count_by_class()
    assert stats["法师"][0] >= 20
    assert stats["法师"][3] >= 30

    print(f"[class_spells] 自检通过 ✓ ({sum(len(v) for v in CLASS_SPELLS.values() for v2 in v.values() for _ in v2)} 法术-职业关联)")


if __name__ == "__main__":
    _self_test()
