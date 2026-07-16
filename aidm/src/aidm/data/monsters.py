"""怪物数据模型与查询接口。

数据来源: 5echm_web 怪物图鉴2025（402只怪物）
由 scripts/extract_monsters.py 自动提取。
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from aidm.data._monsters_data import _MONSTERS_LIST, MONSTERS, EN_MONSTERS, CR_MONSTERS

# ── 扩展怪物（MPMM等）───────────────────────────────────────────────────
try:
    from aidm.data._expansion_monsters_data import _EXPANSION_MONSTERS_LIST
    _exp_count = 0
    for _raw in _EXPANSION_MONSTERS_LIST:
        if _raw["name"] not in MONSTERS:
            # Convert to the Monster dict format expected by the module
            _monster_dict = {
                "name": _raw["name"],
                "en_name": _raw.get("en_name", ""),
                "size": _raw.get("size", "中型"),
                "type": _raw.get("creature_type", ""),
                "ac": _raw.get("ac", 10),
                "hp": _raw.get("hp", 0),
                "hp_formula": _raw.get("hp_formula", ""),
                "speed": _raw.get("speed", {}),
                "abilities": _raw.get("abilities", {}),
                "skills": _raw.get("skills", {}),
                "senses": _raw.get("senses", {}),
                "languages": _raw.get("languages", ""),
                "cr": _raw.get("cr", "0"),
                "xp": _raw.get("xp", 0),
                "pb": _raw.get("pb", 2),
                "traits": _raw.get("traits", []),
                "actions": _raw.get("actions", []),
                "bonus_actions": _raw.get("bonus_actions", []),
                "reactions": _raw.get("reactions", []),
                "legendary_actions": _raw.get("legendary_actions", []),
                "alignment": _raw.get("alignment", ""),
                "source": _raw.get("source", "MPMM"),
            }
            MONSTERS[_raw["name"]] = _monster_dict
            if _raw.get("en_name"):
                EN_MONSTERS[_raw["en_name"]] = _monster_dict
            cr_key = str(_raw.get("cr", "0"))
            if cr_key not in CR_MONSTERS:
                CR_MONSTERS[cr_key] = []
            CR_MONSTERS[cr_key].append(_monster_dict)
            _exp_count += 1
    if _exp_count:
        print(f"[monsters] 已合并 {_exp_count} 个扩展怪物 (MPMM)")
except ImportError:
    pass


@dataclass
class AbilityBlock:
    """六维属性块。"""
    score: int
    mod: int
    save: int


@dataclass
class Monster:
    """怪物数据模型。匹配 D&D 2024 怪物图鉴 stat block 格式。"""
    name: str
    en_name: str = ""
    size: str = "Medium"
    creature_type: str = ""
    alignment: str = ""
    ac: int = 10
    ac_desc: str = ""
    hp: int = 1
    hp_formula: str = ""
    speed: dict = field(default_factory=dict)
    abilities: dict[str, Any] = field(default_factory=dict)
    skills: dict[str, int] = field(default_factory=dict)
    damage_vulnerabilities: list[str] = field(default_factory=list)
    damage_resistances: list[str] = field(default_factory=list)
    damage_immunities: list[str] = field(default_factory=list)
    condition_immunities: list[str] = field(default_factory=list)
    senses: dict[str, Any] = field(default_factory=dict)
    languages: str = ""
    cr: Any = "?"
    xp: int = 0
    pb: int = 2
    traits: list[dict] = field(default_factory=list)
    actions: list[dict] = field(default_factory=list)
    bonus_actions: list[dict] = field(default_factory=list)
    reactions: list[dict] = field(default_factory=list)
    legendary_actions: list[dict] = field(default_factory=list)
    lair_actions: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Monster":
        return cls(
            name=d.get("name", ""),
            en_name=d.get("en_name", ""),
            size=d.get("size", "Medium"),
            creature_type=d.get("creature_type", ""),
            alignment=d.get("alignment", ""),
            ac=d.get("ac", 10),
            ac_desc=d.get("ac_desc", ""),
            hp=d.get("hp", 1),
            hp_formula=d.get("hp_formula", ""),
            speed=d.get("speed", {}),
            abilities=d.get("abilities", {}),
            skills=d.get("skills", {}),
            damage_vulnerabilities=d.get("damage_vulnerabilities", []),
            damage_resistances=d.get("damage_resistances", []),
            damage_immunities=d.get("damage_immunities", []),
            condition_immunities=d.get("condition_immunities", []),
            senses=d.get("senses", {}),
            languages=d.get("languages", ""),
            cr=d.get("cr", "?"),
            xp=d.get("xp", 0),
            pb=d.get("pb", 2),
            traits=d.get("traits", []),
            actions=d.get("actions", []),
            bonus_actions=d.get("bonus_actions", []),
            reactions=d.get("reactions", []),
            legendary_actions=d.get("legendary_actions", []),
            lair_actions=d.get("lair_actions", ""),
        )

    def cr_float(self) -> float:
        """将 CR 转为浮点数用于排序比较。"""
        cr = self.cr
        if cr == "?":
            return -1.0
        if isinstance(cr, int):
            return float(cr)
        if isinstance(cr, str) and "/" in cr:
            parts = cr.split("/")
            return float(parts[0]) / float(parts[1])
        return float(cr)

    def ability_mod(self, ab: str) -> int:
        """获取属性调整值。ab: 'str'/'dex'/'con'/'int'/'wis'/'cha'"""
        key_map = {"str": "力量", "dex": "敏捷", "con": "体质",
                    "int": "智力", "wis": "感知", "cha": "魅力"}
        key = key_map.get(ab.lower(), ab)
        ab_data = self.abilities.get(key, {})
        if isinstance(ab_data, dict):
            return ab_data.get("mod", 0)
        return 0

    def passive_perception(self) -> int:
        return self.senses.get("被动察觉", 10)


# ── 查询接口 ──

def get_monster(name: str) -> Optional[Monster]:
    """按中文名查怪物。"""
    d = MONSTERS.get(name)
    return Monster.from_dict(d) if d else None


def get_monster_by_en(en_name: str) -> Optional[Monster]:
    """按英文名查怪物。"""
    d = EN_MONSTERS.get(en_name)
    return Monster.from_dict(d) if d else None


def get_monsters_by_cr(cr: Any) -> list[Monster]:
    """按CR获取怪物列表。"""
    key = str(cr)
    return [Monster.from_dict(d) for d in CR_MONSTERS.get(key, [])]


def get_monsters_by_type(creature_type: str) -> list[Monster]:
    """按生物类型筛选（模糊匹配）。"""
    results = []
    for d in _MONSTERS_LIST:
        if creature_type in d.get("creature_type", ""):
            results.append(Monster.from_dict(d))
    return results


def get_monsters_by_cr_range(min_cr: float, max_cr: float) -> list[Monster]:
    """按CR范围筛选。"""
    results = []
    for d in _MONSTERS_LIST:
        m = Monster.from_dict(d)
        cr = m.cr_float()
        if min_cr <= cr <= max_cr:
            results.append(m)
    return results


def search_monsters(query: str) -> list[Monster]:
    """模糊搜索怪物（匹配中文名/英文名/类型）。"""
    results = []
    q = query.lower()
    for d in _MONSTERS_LIST:
        m = Monster.from_dict(d)
        if (q in m.name.lower() or q in m.en_name.lower()
                or q in m.creature_type.lower()):
            results.append(m)
    return results


def all_monsters() -> list[Monster]:
    """获取全部怪物。"""
    return [Monster.from_dict(d) for d in _MONSTERS_LIST]


def all_monster_names() -> list[str]:
    """获取全部怪物中文名列表。"""
    return [d["name"] for d in _MONSTERS_LIST]


# ── 自检 ──

def _self_test():
    print(f"[monsters] 载入 {len(_MONSTERS_LIST)} 只怪物")

    # 按名查询
    lich = get_monster("巫妖")
    assert lich is not None
    assert lich.cr == 21
    assert lich.ac == 20
    assert lich.hp == 315
    assert lich.ability_mod("int") == 5
    assert "传奇抗性" in [t["name"] for t in lich.traits]
    print(f"  ✓ 巫妖: CR{lich.cr}, AC{lich.ac}, HP{lich.hp}")

    # CR 范围
    low = get_monsters_by_cr_range(0, 1)
    assert len(low) > 10
    print(f"  ✓ CR 0-1 共 {len(low)} 只")

    # 搜索
    dragons = search_monsters("龙")
    assert len(dragons) > 3
    print(f"  ✓ 搜索'龙'找到 {len(dragons)} 只")

    # 类型筛选
    undead = get_monsters_by_type("亡灵")
    assert len(undead) > 10
    print(f"  ✓ 亡灵生物 {len(undead)} 只")

    print("[monsters] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
