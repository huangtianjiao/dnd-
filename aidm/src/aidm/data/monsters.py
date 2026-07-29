"""怪物数据表 — 5E SRD 常见怪物属性。

本模块提供结构化怪物属性（hp/ac/attack_bonus/damage_dice/cr 等），用于：
  - 战斗开始时 `_resolve_start_combat` 按 name 回填真实数值，替代硬编码默认
    （hp=7/atk+4/1d6+2/挥砍），见 brain/graph.py 与 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段B4。
  - 自动遇遇按角色等级(CR段)+地形选怪，替代"永远哥布林"，见阶段B5。
  - 战利品生成按怪物 cr 取数（loot.cr_to_loot_tier），见阶段B4 注释。
  - API /monster/{name} 结构化快速回退（RAG 文本兜底），见阶段B4。

设计镜照 data/magic_items.py：@dataclass + 模块级 DICT 索引 + get_X(name)->Optional + to_dict。

⚠ 数值参照 5E SRD，部分为近似（hp/伤害骰取整便于结算）；落地前请按规则书逐条校对。
   cr 字段用于战利品/遇遇分档，不进 engine.combat.Combatant（战斗状态机不需 CR）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Monster:
    """单个怪物的属性条目。

    Attributes:
        name: 怪物中文名（检索/展示 key）
        cr: 挑战等级（float，如 0.25 / 1 / 5），用于战利品分档与遇遇难度
        hp: 生命值上限（取整，用于 Combatant.hp_max）
        ac: 护甲等级
        dex_mod: 敏捷调整值（先政用）
        attack_bonus: 攻击检定加值（怪物用）
        damage_dice: 伤害骰表达式如 "1d6+2"
        damage_type: 伤害类型（挥砍/穿刺/钝击/火焰/酸/毒素/...）
        speed: 速度（尺/回合）
        abilities: 能力名列表（供 enemy_ai.decide_action 等）
        senses: 感知描述（如 "黑暗视觉60尺, 被动察觉13"）
        creature_type: 生物类型（类人/野兽/不死/植物/泥形/龙/...）
        size: 体型（小型/中型/大型/巨型）
        source: 规则出处
    """
    name: str
    cr: float
    hp: int
    ac: int
    dex_mod: int
    attack_bonus: int
    damage_dice: str
    damage_type: str
    speed: int = 30
    abilities: list[str] = field(default_factory=list)
    senses: str = ""
    creature_type: str = "类人"
    size: str = "中型"
    source: str = "5E SRD（近似，需校对）"

    def to_combatant_dict(self) -> dict:
        """产出 _resolve_start_combat 期望的敌人 dict（覆盖硬编码默认值）。"""
        return {
            "name": self.name,
            "dex_mod": self.dex_mod,
            "side": "enemy",
            "hp_max": self.hp,
            "hp": self.hp,
            "ac": self.ac,
            "attack_bonus": self.attack_bonus,
            "damage_dice": self.damage_dice,
            "damage_type": self.damage_type,
            "speed": self.speed,
        }

    def to_dict(self) -> dict:
        """完整序列化（API /monster/{name} 等用）。"""
        return {
            "name": self.name, "cr": self.cr, "hp": self.hp, "ac": self.ac,
            "dex_mod": self.dex_mod, "attack_bonus": self.attack_bonus,
            "damage_dice": self.damage_dice, "damage_type": self.damage_type,
            "speed": self.speed, "abilities": list(self.abilities),
            "senses": self.senses, "creature_type": self.creature_type,
            "size": self.size, "source": self.source,
        }


# ──────────────────────────────────────────────────────────────────────────
# 怪物表（规则书权威值；数值出处见各条 source 字段）
# ──────────────────────────────────────────────────────────────────────────

_SRC_2025 = "topics/怪物图鉴2025"
_SRC_2014 = "topics/怪物图鉴2014"

_MONSTERS_LIST: list[Monster] = [
    Monster("狗头人", cr=0.125, hp=7, ac=14, dex_mod=2, attack_bonus=4,
            damage_dice="1d6", damage_type="钝击", speed=30,
            abilities=["黑暗视觉60尺", "群体战术", "阳光敏感"],
            senses="黑暗视觉60尺, 被动察觉12", creature_type="龙类", size="小型",
            source=_SRC_2025 + "/龙类/狗头人/狗头人武者.htm"),
    Monster("哥布林", cr=0.25, hp=7, ac=15, dex_mod=2, attack_bonus=4,
            damage_dice="1d6+2", damage_type="挥砍", speed=30,
            abilities=["黑暗视觉60尺", "迅捷逃逸(附赠动作撤离/躲藏)"],
            senses="黑暗视觉60尺, 被动察觉9", creature_type="类人", size="小型",
            source=_SRC_2014 + "/类人生物/地精.html"),
    Monster("狼", cr=0.25, hp=11, ac=12, dex_mod=2, attack_bonus=4,
            damage_dice="1d6+2", damage_type="穿刺", speed=40,
            abilities=["群体战术", "咬击击倒(力量豁免DC11)"],
            senses="被动察觉13, 嗅觉敏锐", creature_type="野兽", size="中型",
            source=_SRC_2025 + "/附录A/狼.htm"),
    Monster("骷髅", cr=0.25, hp=13, ac=14, dex_mod=3, attack_bonus=5,
            damage_dice="1d6+3", damage_type="穿刺", speed=30,
            abilities=["伤害易伤(钝击)", "免疫毒素", "免疫恐慌/麻痹"],
            senses="黑暗视觉60尺, 被动察觉9", creature_type="亡灵", size="中型",
            source=_SRC_2025 + "/亡灵/骷髅/骷髅.htm"),
    Monster("丧尸", cr=0.25, hp=15, ac=8, dex_mod=-2, attack_bonus=3,
            damage_dice="1d8+1", damage_type="钝击", speed=20,
            abilities=["不朽坚韧(生命值归0时体质豁免DC5+伤害值, 成功则保留1HP; 光耀/重击除外)"],
            senses="黑暗视觉60尺, 被动察觉9", creature_type="亡灵", size="中型",
            source=_SRC_2025 + "/亡灵/丧尸/丧尸.htm"),
    Monster("兽人", cr=0.5, hp=15, ac=13, dex_mod=1, attack_bonus=5,
            damage_dice="1d12+3", damage_type="挥砍", speed=30,
            abilities=["好斗(附赠动作向敌对生物移动至近身)", "黑暗视觉60尺"],
            senses="被动察觉10, 黑暗视觉60尺", creature_type="类人", size="中型",
            source=_SRC_2014 + "/类人生物/兽人.html"),
    Monster("霍布哥布林", cr=0.5, hp=11, ac=18, dex_mod=1, attack_bonus=3,
            damage_dice="1d8+1", damage_type="挥砍", speed=30,
            abilities=["军事优势(盟友在目标5尺内时伤害+2d6, 每回合一次)"],
            senses="黑暗视觉60尺, 被动察觉12", creature_type="类人", size="中型",
            source=_SRC_2014 + "/类人生物/大地精.html"),
    Monster("黑熊", cr=0.5, hp=19, ac=11, dex_mod=1, attack_bonus=4,
            damage_dice="1d6+2", damage_type="挥砍", speed=40,
            abilities=["多重攻击(咬+爪)", "攀爬30尺", "嗅觉敏锐"],
            senses="被动察觉13, 嗅觉敏锐", creature_type="野兽", size="中型",
            source=_SRC_2025 + "/附录A/黑熊.htm"),
    Monster("灰泥怪", cr=0.5, hp=22, ac=9, dex_mod=-2, attack_bonus=3,
            damage_dice="1d6", damage_type="钝击", speed=10,
            abilities=["伪足(命中附加2d6强酸)", "腐蚀金属(非魔法金属护甲降AC)", "黏附"],
            senses="盲视60尺(无视觉)", creature_type="泥怪", size="中型",
            source=_SRC_2025 + "/泥怪/灰泥怪.htm"),
    Monster("巨蜘蛛", cr=1, hp=26, ac=14, dex_mod=3, attack_bonus=5,
            damage_dice="1d8+3", damage_type="穿刺", speed=30,
            abilities=["喷网(射程30尺, 力量豁免DC12)", "攀爬", "蛛网感知"],
            senses="盲视60尺, 被动察觉10", creature_type="野兽", size="大型",
            source=_SRC_2025 + "/附录A/巨蜘蛛.htm"),
    Monster("龙裔战士", cr=1, hp=33, ac=16, dex_mod=1, attack_bonus=5,
            damage_dice="1d8+3", damage_type="挥砍", speed=30,
            abilities=["喷吐武器(锥形8d6能量, 敏捷豁免DC13)"],
            senses="被动察觉11", creature_type="龙", size="中型",
            source="无官方条目（SRD 近似值，待校对）"),
    Monster("食人魔", cr=2, hp=68, ac=11, dex_mod=-1, attack_bonus=6,
            damage_dice="2d8+4", damage_type="钝击", speed=40,
            abilities=["巨棒(触及10尺)"],
            senses="被动察觉9", creature_type="巨人", size="大型",
            source=_SRC_2025 + "/巨人/食人魔/食人魔.htm"),
    Monster("巨魔", cr=5, hp=94, ac=15, dex_mod=1, attack_bonus=7,
            damage_dice="2d6+4", damage_type="挥砍", speed=30,
            abilities=["再生(每回合恢复15HP, 受强酸/火焰伤害则下回合失效)",
                      "多重攻击(撕裂×3)", "扰人断肢(4/日)"],
            senses="黑暗视觉60尺, 被动察觉15", creature_type="巨人", size="大型",
            source=_SRC_2025 + "/巨人/巨魔/巨魔.htm"),
]


MONSTERS: dict[str, Monster] = {m.name: m for m in _MONSTERS_LIST}


# ──────────────────────────────────────────────────────────────────────────
# 全量表兜底：monsters_full.MONSTERS_FULL（505 个怪物，自动解析生成）
# 手工精校表 MONSTERS 未命中时按名转换；遭遇池合并两表（手工表同名优先）。
# ──────────────────────────────────────────────────────────────────────────

_FULL_CACHE: dict[str, Monster] = {}
_FULL_POOL: Optional[list[Monster]] = None


def _monster_from_full(raw: dict) -> Monster:
    """将 monsters_full 的 dict 条目转换为 Monster 对象（带缓存）。"""
    name = raw["name"]
    if name not in _FULL_CACHE:
        _FULL_CACHE[name] = Monster(
            name=name,
            cr=raw["cr"],
            hp=raw["hp"],
            ac=raw["ac"],
            dex_mod=raw["dex_mod"],
            attack_bonus=raw["attack_bonus"],
            damage_dice=raw["damage_dice"],
            damage_type=raw["damage_type"],
            speed=raw.get("speed", 30),
            abilities=[],
            senses=raw.get("senses", ""),
            creature_type=raw.get("creature_type", "类人"),
            size=raw.get("size", "中型"),
            source=raw.get("source", "怪物图鉴2025（自动解析）"),
        )
    return _FULL_CACHE[name]


def _full_pool() -> list[Monster]:
    """全量表所有怪物（转换并缓存）。延迟导入避免大数据表拖慢启动。"""
    global _FULL_POOL
    if _FULL_POOL is None:
        from .monsters_full import MONSTERS_FULL
        _FULL_POOL = [_monster_from_full(raw) for raw in MONSTERS_FULL.values()]
    return _FULL_POOL


def get_monster(name: str) -> Optional[Monster]:
    """按中文名查怪物。

    优先命中手工精校表 MONSTERS（13 个，含战斗 AI 能力描述）；未命中则兜底
    全量自动解析表 MONSTERS_FULL（505 个，2025/2014 图鉴权威值）。
    均未收录返回 None（调用方走 LLM 填值/保守默认/RAG 兜底）。
    """
    if name in MONSTERS:
        return MONSTERS[name]
    from .monsters_full import MONSTERS_FULL
    raw = MONSTERS_FULL.get(name)
    return _monster_from_full(raw) if raw else None


def list_monsters() -> list[str]:
    """所有收录怪物名（手工表 + 全量表，调试/前端展示）。"""
    names = set(MONSTERS)
    for m in _full_pool():
        names.add(m.name)
    return sorted(names)


def monsters_by_cr(max_cr: float) -> list[Monster]:
    """返回 cr <= max_cr 的怪物（用于按等级/难度选遭遇怪）。

    例：1级角色用 monsters_by_cr(1.0) → 低 CR 怪池；5级用 monsters_by_cr(5.0)。
    合并手工表与全量表，手工表同名优先（其 abilities 供战斗 AI 使用）。
    """
    merged: dict[str, Monster] = {m.name: m for m in _full_pool() if m.cr <= max_cr}
    for m in _MONSTERS_LIST:
        if m.cr <= max_cr:
            merged[m.name] = m
    return list(merged.values())


def pick_encounter_pool(level: int) -> list[Monster]:
    """按角色等级选遇遇怪池（CR 上限随等级放宽）。

    简化映射（可后续接 XP 预算/CR段）：
      level 1-2  → cr <= 0.5
      level 3-4  → cr <= 1
      level 5-9  → cr <= 2
      level 10+  → cr <= 5（含巨魔等）
    """
    if level <= 2:
        cap = 0.5
    elif level <= 4:
        cap = 1.0
    elif level <= 9:
        cap = 2.0
    else:
        cap = 5.0
    pool = monsters_by_cr(cap)
    return pool or [MONSTERS["哥布林"]]


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    assert get_monster("哥布林") is not None
    assert get_monster("不存在的怪") is None
    g = get_monster("哥布林")
    d = g.to_combatant_dict()
    assert d["hp_max"] == 7 and d["attack_bonus"] == 4
    assert d["side"] == "enemy" and d["damage_dice"] == "1d6+2"
    assert "哥布林" in list_monsters()
    low = monsters_by_cr(0.5)
    assert get_monster("巨魔") not in low
    assert get_monster("巨魔") in monsters_by_cr(5)
    assert len(pick_encounter_pool(1)) >= 1
    assert all(m.cr <= 1.0 for m in pick_encounter_pool(4))
    # 权威值：巨魔 2025 版块（HP94/AC15/+7/2d6+4）
    t = get_monster("巨魔")
    assert t.hp == 94 and t.ac == 15 and t.attack_bonus == 7
    assert t.damage_dice == "2d6+4" and "2025" in t.source
    # 权威值：霍布哥布林 2014 版块（+3/1d8+1，修正旧近似值 +5/1d8+3）
    h = get_monster("霍布哥布林")
    assert h.attack_bonus == 3 and h.damage_dice == "1d8+1"
    # 全量表兜底：手工表未收录的怪也能查到
    assert get_monster("巫妖") is not None and get_monster("巫妖").hp > 100
    assert get_monster("枭熊").cr == 3
    # 遭遇池合并后低 CR 池远大于原 13 个
    assert len(monsters_by_cr(1.0)) > 100
    print("[monsters] 自检通过 ✓")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    _self_test()
