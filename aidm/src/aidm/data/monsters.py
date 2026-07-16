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
# 怪物表（5E SRD，常见低-中 CR 怪物铺底）
# ──────────────────────────────────────────────────────────────────────────

_MONSTERS_LIST: list[Monster] = [
    Monster("狗头人", cr=0.125, hp=5, ac=12, dex_mod=2, attack_bonus=4,
            damage_dice="1d4+2", damage_type="穿刺", speed=30,
            abilities=["黑暗视觉60尺", "群体战术", "阳光敏感"],
            senses="黑暗视觉60尺, 被动察觉12", creature_type="类人", size="小型"),
    Monster("哥布林", cr=0.25, hp=7, ac=15, dex_mod=2, attack_bonus=4,
            damage_dice="1d6+2", damage_type="挥砍", speed=30,
            abilities=["黑暗视觉60尺", "撤离(附赠动作)"],
            senses="黑暗视觉60尺, 被动察觉9", creature_type="类人", size="小型"),
    Monster("狼", cr=0.25, hp=11, ac=12, dex_mod=2, attack_bonus=4,
            damage_dice="1d6+2", damage_type="穿刺", speed=40,
            abilities=["群体战术", "咬击击倒(力量豁免DC11)"],
            senses="被动察觉13, 嗅觉敏锐", creature_type="野兽", size="中型"),
    Monster("骷髅", cr=0.25, hp=13, ac=13, dex_mod=2, attack_bonus=4,
            damage_dice="1d6+2", damage_type="穿刺", speed=30,
            abilities=["伤害抗性(穿刺)", "免疫毒素"],
            senses="黑暗视觉60尺, 被动察觉9", creature_type="不死", size="中型"),
    Monster("僵尸", cr=0.25, hp=22, ac=8, dex_mod=-2, attack_bonus=3,
            damage_dice="1d6+1", damage_type="钝击", speed=20,
            abilities=["不朽之力(体质豁免DC5免死, 非光耀暴击直接死)"],
            senses="被动察觉9", creature_type="不死", size="中型"),
    Monster("兽人", cr=0.5, hp=15, ac=13, dex_mod=1, attack_bonus=5,
            damage_dice="1d12+3", damage_type="挥砍", speed=30,
            abilities=["恒怒(生命值低于一半时攻击优势)"],
            senses="被动察觉10, 黑暗视觉60尺", creature_type="类人", size="中型"),
    Monster("霍布哥布林", cr=0.5, hp=11, ac=18, dex_mod=1, attack_bonus=5,
            damage_dice="1d8+3", damage_type="挥砍", speed=30,
            abilities=["军事战术(触及内盟友攻击检定优势)"],
            senses="黑暗视觉60尺, 被动察觉12", creature_type="类人", size="中型"),
    Monster("黑熊", cr=0.5, hp=19, ac=11, dex_mod=2, attack_bonus=3,
            damage_dice="1d6+2", damage_type="穿刺", speed=40,
            abilities=["多重攻击(咬+爪)", "攀爬"],
            senses="被动察觉13, 嗅觉敏锐", creature_type="野兽", size="中型"),
    Monster("灰色软泥", cr=0.5, hp=22, ac=8, dex_mod=-5, attack_bonus=2,
            damage_dice="1d6", damage_type="酸", speed=10,
            abilities=["伪足", "腐蚀金属(非魔法金属护甲降AC)", "黏附"],
            senses="盲视60尺(无视觉)", creature_type="泥形", size="中型"),
    Monster("巨型蜘蛛", cr=1, hp=26, ac=14, dex_mod=4, attack_bonus=5,
            damage_dice="1d8+3", damage_type="穿刺", speed=30,
            abilities=["喷网(射程30尺, 力量豁免DC12)", "攀爬", "蛛网感知"],
            senses="盲视60尺, 被动察觉10", creature_type="野兽", size="大型"),
    Monster("龙裔战士", cr=1, hp=33, ac=16, dex_mod=1, attack_bonus=5,
            damage_dice="1d8+3", damage_type="挥砍", speed=30,
            abilities=["喷吐武器(锥形8d6能量, 敏捷豁免DC13)"],
            senses="被动察觉11", creature_type="龙", size="中型"),
    Monster("食人魔", cr=2, hp=52, ac=11, dex_mod=-1, attack_bonus=6,
            damage_dice="2d8+4", damage_type="钝击", speed=40,
            abilities=["巨棒(触及10尺)"],
            senses="被动察觉9", creature_type="巨人", size="大型"),
    Monster("巨魔", cr=5, hp=84, ac=14, dex_mod=1, attack_bonus=7,
            damage_dice="1d6+4", damage_type="挥砍", speed=30,
            abilities=["再生(每回合恢复10HP, 非强酸/火焰伤害致死则不再生)",
                      "多重攻击(爪×2+咬)"],
            senses="黑暗视觉60尺, 被动察觉9", creature_type="巨人", size="大型"),
]


MONSTERS: dict[str, Monster] = {m.name: m for m in _MONSTERS_LIST}


def get_monster(name: str) -> Optional[Monster]:
    """按中文名查怪物。未收录返回 None（调用方走 LLM 填值/保守默认/RAG 兜底）。"""
    return MONSTERS.get(name)


def list_monsters() -> list[str]:
    """所有收录怪物名（调试/前端展示）。"""
    return list(MONSTERS)


def monsters_by_cr(max_cr: float) -> list[Monster]:
    """返回 cr <= max_cr 的怪物（用于按等级/难度选遭遇怪）。

    例：1级角色用 monsters_by_cr(1.0) → 低 CR 怪池；5级用 monsters_by_cr(5.0)。
    """
    return [m for m in _MONSTERS_LIST if m.cr <= max_cr]


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
    print("[monsters] 自检通过 ✓")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    _self_test()
