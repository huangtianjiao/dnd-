"""状态层数据模型 — 角色卡 / 战役 / 场景 / 战斗 / 日志（SQLModel）。

单文件 SQLite 持久化，存档即拷文件。变长字段（属性/状态/法术位/物品/参战者）
以 JSON 字符串存储，读写经 helper 方法。提供到 engine 层类型的桥接
（to_condition_state / to_death_tracker / ability_mod / prof）。

规则依据见 RULE_SPEC.md 数据模型（§6）与对应规则点。
"""

from __future__ import annotations

import json
from typing import ClassVar

from sqlmodel import Field, SQLModel, create_engine

from ..engine import conditions, damage, dice

# ──────────────────────────────────────────────────────────────────────────
# 建表
# ──────────────────────────────────────────────────────────────────────────

def get_engine(db_path: str = "sqlite:///aidm/data/saves/save.db"):
    """创建/获取 SQLite 引擎。db_path 形如 'sqlite:///path.db' 或 'sqlite://'（内存）。"""
    return create_engine(db_path, echo=False)


def init_db(db_path: str = "sqlite:///aidm/data/saves/save.db"):
    """建表（幂等）。"""
    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)
    return engine


# ──────────────────────────────────────────────────────────────────────────
# 角色卡
# ──────────────────────────────────────────────────────────────────────────

DEFAULT_ABILITIES = {"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10}


class Character(SQLModel, table=True):
    """角色卡：属性/HP/AC/速度/状态/法术位/物品/死亡豁免计数。

    规则: R-DMG-007/009 HP与临时HP + R-DMG-017 死亡豁免计数 + R-GLS-043 状态集合
    """
    id: int | None = Field(default=None, primary_key=True)
    campaign_id: int | None = Field(default=None, foreign_key="campaign.id")
    name: str
    race: str = ""
    char_class: str = ""
    subclass: str = ""
    background: str = ""          # 背景（PHB 第一章），影响属性加成/起源专长/技能熟练
    alignment: str = "绝对中立"   # 阵营九宫格（PHB 第一章）
    level: int = 1
    # 变长字段（JSON）
    abilities_json: str = Field(default=json.dumps(DEFAULT_ABILITIES))
    spell_slots_json: str = Field(default="{}")     # {环阶:剩余}
    known_spells_json: str = Field(default="[]")
    inventory_json: str = Field(default="[]")
    conditions_json: str = Field(default="[]")     # 状态集合
    attuned_items_json: str = Field(default="[]")  # 已同调魔法物品名称列表（最多3个）
    feats_json: str = Field(default="[]")          # 已选专长名列表（PHB 第五章）
    skill_prof_json: str = Field(default="[]")      # 技能熟练列表（如 ["察觉","潜行"]）
    # 专注跨回合持久化
    concentration_spell: str = ""                    # 当前专注的法术名
    concentration_dc: int = 0                        # 维持专注需检定的 DC
    # 经验值
    xp: int = 0                                     # 当前经验值
    # 当前手持武器（武器中文名）；攻击时优先于"徒手"兆底，由 /equip-weapon 或创建时按职业设默认。
    # 详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段A。
    equipped_weapon: str = ""
    # 当前穿戴的护甲（护甲中文名）；"" = 无甲。穿卸护甲时更新此字段并调用 recompute_ac()。
    equipped_armor: str = ""
    # 数值
    hp_current: int = 0
    hp_max: int = 0
    temp_hp: int = 0
    ac: int = 10
    speed: int = 30
    exhaustion: int = 0
    gold: int = 0                       # 金币(GP)， loot 分配落盘
    # 生命骰追踪（R-GLS-014 短休消耗 / R-GLS-015 长休恢复）
    hit_dice_current: int = 0   # 可用生命骰数量
    hit_dice_max: int = 0       # 生命骰上限（=等级）
    # 死亡豁免计数（R-DMG-017）
    death_successes: int = 0
    death_failures: int = 0
    stable: bool = False
    dead: bool = False
    # 英雄气概（Heroic Inspiration） R-GLS-070
    has_inspiration: bool = False

    # —— JSON 桥接 ——
    @property
    def abilities(self) -> dict:
        return json.loads(self.abilities_json)

    def set_abilities(self, scores: dict) -> None:
        self.abilities_json = json.dumps(scores)

    @property
    def conditions_list(self) -> list:
        return json.loads(self.conditions_json)

    def set_conditions(self, conds: list) -> None:
        self.conditions_json = json.dumps(conds)

    @property
    def spell_slots(self) -> dict:
        return json.loads(self.spell_slots_json)

    def set_spell_slots(self, slots: dict) -> None:
        self.spell_slots_json = json.dumps(slots)

    @property
    def known_spells(self) -> list:
        return json.loads(self.known_spells_json)

    def set_known_spells(self, spells: list) -> None:
        self.known_spells_json = json.dumps(spells)

    # —— 同调物品桥接 ——
    # 规则: 玩家手册 同调Attunement — 一个生物最多同时与3件魔法物品同调
    MAX_ATTUNED_ITEMS: ClassVar[int] = 3

    @property
    def attuned_items(self) -> list[str]:
        """已同调的魔法物品名称列表（最多3个）。

        规则: 同调 — 一个生物最多同时与三件魔法物品同调。
        """
        return json.loads(self.attuned_items_json)

    def set_attuned_items(self, names: list[str]) -> None:
        """设置已同调物品列表（强制上限3）。"""
        if len(names) > self.MAX_ATTUNED_ITEMS:
            raise ValueError(
                f"同调物品上限为{self.MAX_ATTUNED_ITEMS}件，"
                f"试图设置{len(names)}件"
            )
        self.attuned_items_json = json.dumps(names)

    # —— 物品栏桥接 ——
    # 规则: 城主指南2024/7.宝藏/ — 角色持有的魔法物品名称列表
    @property
    def inventory(self) -> list[str]:
        """角色物品栏中的魔法物品名称列表。

        规则: 城主指南2024/7.宝藏/ — 战利品分配后写入角色物品栏。
        """
        return json.loads(self.inventory_json)

    def set_inventory(self, items: list[str]) -> None:
        """设置角色物品栏。"""
        self.inventory_json = json.dumps(items)

    def add_to_inventory(self, item_name: str) -> None:
        """向物品栏添加一件物品（不重复添加）。"""
        inv = self.inventory
        if item_name not in inv:
            inv.append(item_name)
            self.inventory_json = json.dumps(inv)

    # —— 专长桥接 ——
    # 规则: PHB 第五章「专长」— 起源/通用/战斗风格/传奇恩惠
    @property
    def feats(self) -> list[str]:
        """已选专长名列表。"""
        return json.loads(self.feats_json)

    def set_feats(self, names: list[str]) -> None:
        """设置已选专长名列表。"""
        self.feats_json = json.dumps(names)

    # —— 技能熟练桥接 ——
    @property
    def skill_proficiencies(self) -> list[str]:
        """技能熟练列表。"""
        return json.loads(self.skill_prof_json)

    def set_skill_proficiencies(self, skills: list[str]) -> None:
        """设置技能熟练列表。"""
        self.skill_prof_json = json.dumps(skills)

    def is_proficient(self, skill_name: str) -> bool:
        """判断角色是否熟练某技能。"""
        return skill_name in self.skill_proficiencies

    # —— 专注状态桥接 ——
    def start_concentration(self, spell_name: str, dc: int = 10) -> None:
        """开始专注一个法术。规则: R-GLS-036 专注"""
        self.concentration_spell = spell_name
        self.concentration_dc = dc

    def end_concentration(self) -> None:
        """结束专注。"""
        self.concentration_spell = ""
        self.concentration_dc = 0

    @property
    def is_concentrating(self) -> bool:
        """是否正在专注。"""
        return bool(self.concentration_spell)

    # —— engine 桥接 ——
    def ability_score(self, ab: str) -> int:
        return self.abilities.get(ab, 10)

    def ability_mod(self, ab: str) -> int:
        """属性调整值 floor((score-10)/2)。规则: R-CHK-024"""
        return dice.ability_modifier(self.ability_score(ab))

    def prof(self) -> int:
        """熟练加值（按等级）。规则: R-CHK-015"""
        return dice.proficiency_bonus(self.level)

    def to_condition_state(self) -> conditions.ConditionState:
        """转状态集合（含力竭）。规则: R-GLS-043"""
        s = conditions.ConditionState(exhaustion=self.exhaustion)
        for c in self.conditions_list:
            if c != "力竭":
                s.conditions.add(c)
        return s

    def apply_condition_state(self, state: conditions.ConditionState) -> None:
        """从 ConditionState 回写。"""
        self.conditions_json = json.dumps(sorted(state.conditions))
        self.exhaustion = state.exhaustion

    def to_death_tracker(self) -> damage.DeathTracker:
        """转死亡豁免计数器。规则: R-DMG-017"""
        return damage.DeathTracker(
            successes=self.death_successes, failures=self.death_failures,
            stable=self.stable, dead=self.dead,
        )

    def apply_death_tracker(self, t: damage.DeathTracker) -> None:
        self.death_successes = t.successes
        self.death_failures = t.failures
        self.stable = t.stable
        self.dead = t.dead

    def recompute_ac(self) -> None:
        """根据当前装备、属性、职业重新计算 AC。

        规则: R-ITM-004 AC计算公式 + 野蛮人/武僧无甲防御
        出处: topics/玩家手册2024/装备/护甲.htm
        说明: 穿卸护甲、升级、属性变化等场景后调用，自动写入 self.ac。
              盾牌判定通过物品栏检查。
        """
        from ..data.equipment import compute_character_ac
        dex = self.ability_mod("dex")
        con = self.ability_mod("con")
        wis = self.ability_mod("wis")
        has_shield = "盾牌" in (self.inventory or [])
        unarmored = self.char_class if self.char_class in ("野蛮人", "武僧") else None
        self.ac = compute_character_ac(
            self.equipped_armor or None, dex, has_shield,
            unarmored_class=unarmored, con_mod=con, wis_mod=wis,
        )


# ──────────────────────────────────────────────────────────────────────────
# 战役 / 场景 / 战斗 / 日志
# ──────────────────────────────────────────────────────────────────────────

class Campaign(SQLModel, table=True):
    """战役：世界设定输入 + AI 生成的完整背景故事 + rolling summary + 世界标记。"""
    id: int | None = Field(default=None, primary_key=True)
    name: str
    setting: str = Field(default="")                  # 玩家输入/编辑的世界设定提示词
    tone: str = Field(default="")                    # 基调（黑暗/英雄/恐怖...）
    world_background: str = Field(default="")        # AI 生成的完整背景故事（长文，持续显示）
    rolling_summary: str = Field(default="")         # 剧情压缩摘要（防上下文失忆）
    world_flags_json: str = Field(default="{}")      # 世界状态标记（NPC关系/阵营/任务）

    @property
    def world_flags(self) -> dict:
        return json.loads(self.world_flags_json)

    def set_world_flags(self, flags: dict) -> None:
        self.world_flags_json = json.dumps(flags)


class Scene(SQLModel, table=True):
    """当前场景：地点/在场NPC/氛围/时间/场景叙事/可做之事/叙事日志。"""
    id: int | None = Field(default=None, primary_key=True)
    campaign_id: int | None = Field(default=None, foreign_key="campaign.id")
    location: str = ""                    # 地点
    npcs_json: str = Field(default="[]")  # 在场 NPC [{name, attitude, role}]
    environment: str = ""                 # 环境（光照/遮蔽/地形）
    time: str = ""                        # 时间（白天/夜晚/第N日）
    atmosphere: str = ""                  # 氛围（多感官：视觉/听觉/嗅觉/触觉）
    situation: str = ""                   # 当前场景摘要（短）
    story_log: str = ""                   # 场景内叙事日志（长，持续显示）
    exits_json: str = Field(default="[]") # 可感知的选项/出路
    notes: str = ""                       # DM 私密备注（秘密/发现）

    @property
    def npcs(self) -> list:
        return json.loads(self.npcs_json)

    def set_npcs(self, npcs: list) -> None:
        self.npcs_json = json.dumps(npcs)

    @property
    def exits(self) -> list:
        return json.loads(self.exits_json)

    def set_exits(self, exits: list) -> None:
        self.exits_json = json.dumps(exits)


class CombatState(SQLModel, table=True):
    """战斗状态（持久化）：先攻顺序/轮次/参战者快照/是否激活。

    规则: R-CMB-001/002  出处: 进行游戏/战斗流程.htm
    """
    id: int | None = Field(default=None, primary_key=True)
    campaign_id: int | None = Field(default=None, foreign_key="campaign.id")
    initiative_order_json: str = Field(default="[]")   # [{cid,name,initiative,side}]
    participants_json: str = Field(default="[]")        # 参战者快照
    round: int = 0
    current_index: int = 0
    active: bool = False

    @property
    def initiative_order(self) -> list:
        return json.loads(self.initiative_order_json)

    def set_initiative_order(self, order: list) -> None:
        self.initiative_order_json = json.dumps(order)


class Log(SQLModel, table=True):
    """完整跑团日志（可审计回溯）：玩家输入/AI回复/骰子/状态变更/RAG引用。"""
    id: int | None = Field(default=None, primary_key=True)
    campaign_id: int | None = Field(default=None, foreign_key="campaign.id")
    ts: str = ""
    player_input: str = ""
    dm_output: str = ""
    dice_rolls_json: str = Field(default="[]")
    state_changes_json: str = Field(default="[]")
    rag_refs_json: str = Field(default="[]")
