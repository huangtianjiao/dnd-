"""状态层数据模型 — 角色卡 / 战役 / 场景 / 战斗 / 日志（SQLModel）。

单文件 SQLite 持久化，存档即拷文件。变长字段（属性/状态/法术位/物品/参战者）
以 JSON 字符串存储，读写经 helper 方法。提供到 engine 层类型的桥接
（to_condition_state / to_death_tracker / ability_mod / prof）。

规则依据见 RULE_SPEC.md 数据模型（§6）与对应规则点。
"""

from __future__ import annotations

import json
from enum import Enum
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


class EquipmentSlots(str, Enum):
    """装备槽位名。"""
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    BODY = "body"


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
    # DATA-002: 稳定 canonical_id（职业/武器/法术等引用用，显示名作为 locale 资源）
    class_canonical_id: str = Field(default="")
    # CHR-006: 多职业等级持久化 — {class_name: level_in_that_class}
    class_levels_json: str = Field(default="{}")
    # 变长字段（JSON）
    abilities_json: str = Field(default=json.dumps(DEFAULT_ABILITIES))
    spell_slots_json: str = Field(default="{}")     # {环阶:剩余}
    known_spells_json: str = Field(default="[]")
    # P7（方案 §10.3）: Known/Prepared/Spellbook/Always-Prepared 分离
    prepared_spells_json: str = Field(default="[]")     # 当前准备列表（准备制）
    spellbook_spells_json: str = Field(default="[]")    # 法术书（法师）
    always_prepared_spells_json: str = Field(default="[]")  # 来源永久准备
    inventory_json: str = Field(default="[]")
    conditions_json: str = Field(default="[]")     # 状态集合
    attuned_items_json: str = Field(default="[]")  # 已同调魔法物品名称列表（最多3个）
    feats_json: str = Field(default="[]")          # 已选专长名列表（PHB 第五章）
    skill_prof_json: str = Field(default="[]")      # 技能熟练列表（如 ["察觉","潜行"]）
    # 装备槽位 JSON: {"off_hand": "盾牌", ...} — 记录各槽位装备的物品名
    # ITEM-002: 盾牌必须装备在 off_hand 槽位才加 AC，背包中的不加。
    equipment_slots_json: str = Field(default=json.dumps({}))
    # ITEM-001: 结构化物品栏 — 存储 ItemInstance 序列化列表
    items_structured_json: str = Field(default="[]")
    # 专注跨回合持久化
    concentration_spell: str = ""                    # 当前专注的法术名
    concentration_dc: int = 0                        # 维持专注需检定的 DC
    # 经验值
    xp: int = 0                                     # 当前经验值
    # 当前手持武器（武器中文名）；攻击时优先于"徒手"兆底，由 /equip-weapon 或创建时按职业设默认。
    # 详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段A。
    equipped_weapon: str = ""
    # P8（方案 §11.2）: 持久化武器精通授权 — [{source_id, mastery_name,
    #   weapon_type, acquired_level, replace_policy}]；战斗解析只认此列表。
    mastery_grants_json: str = Field(default="[]")
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
    # P6（方案 §9.1/§5.4）: 资源池持久化权威
    # {"second_wind": {"current": 2, "max": 2, "recharge": "short_rest",
    #                  "source_feature_id": "...", "resource_type": "..."}}
    resource_pools_json: str = Field(default="{}")
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

    # —— 法术准备/法术书桥接（P7，方案 §10.3）——
    @property
    def prepared_spells(self) -> list:
        return json.loads(self.prepared_spells_json)

    def set_prepared_spells(self, spells: list) -> None:
        self.prepared_spells_json = json.dumps(spells)

    @property
    def spellbook_spells(self) -> list:
        return json.loads(self.spellbook_spells_json)

    def set_spellbook_spells(self, spells: list) -> None:
        self.spellbook_spells_json = json.dumps(spells)

    @property
    def always_prepared_spells(self) -> list:
        return json.loads(self.always_prepared_spells_json)

    def set_always_prepared_spells(self, spells: list) -> None:
        self.always_prepared_spells_json = json.dumps(spells)

    @property
    def equipment_slots(self) -> dict:
        """各装备槽位的物品名映射，如 {"off_hand": "盾牌"}。"""
        return json.loads(self.equipment_slots_json)

    def set_equipment_slots(self, slots: dict) -> None:
        """设置装备槽位。"""
        self.equipment_slots_json = json.dumps(slots)

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

    # —— 结构化物品栏桥接 (ITEM-001) ——
    @property
    def items_structured(self) -> list[dict]:
        """结构化物品栏 — ItemInstance 序列化列表。

        每个物品包含: item_id, name, quantity, charges, attuned, properties 等。
        """
        return json.loads(self.items_structured_json)

    def set_items_structured(self, items: list[dict]) -> None:
        """设置结构化物品栏。"""
        self.items_structured_json = json.dumps(items)

    def add_structured_item(self, item: dict) -> None:
        """向结构化物品栏添加一件物品。"""
        items = self.items_structured
        items.append(item)
        self.items_structured_json = json.dumps(items)

    def remove_structured_item(self, item_id: str) -> bool:
        """从结构化物品栏移除指定 item_id 的物品。"""
        items = self.items_structured
        original_len = len(items)
        items = [i for i in items if i.get("item_id") != item_id]
        self.items_structured_json = json.dumps(items)
        return len(items) < original_len

    def migrate_inventory_to_structured(self) -> int:
        """从字符串列表迁移到结构化物品。

        返回迁移的物品数量。
        """
        inv = self.inventory
        migrated = 0
        for name in inv:
            # 简单迁移：将字符串转为基本结构化格式
            item = {
                "item_id": f"item.{name.lower().replace(' ', '_')}",
                "name": name,
                "quantity": 1,
                "charges": -1,
                "attuned": False,
                "properties": {},
            }
            self.add_structured_item(item)
            migrated += 1
        return migrated

    def sync_inventory_views(self) -> None:
        """★ P1-10（review#11）: 收敛双权威——以 inventory（字符串列表）
        为唯一权威，items_structured 作为派生视图。

        每次保存前调用：删除 inventory 中已不存在的结构化条目，
        补上 inventory 中有而结构化缺失的条目，杜绝状态漂移。
        """
        inv = set(self.inventory)
        structured = self.items_structured
        kept = [
            i for i in structured
            if i.get("name") in inv or i.get("item_id") in inv
        ]
        names = {i.get("name") for i in kept}
        for name in self.inventory:
            if name in names:
                continue
            kept.append({
                "item_id": f"item.{name.lower().replace(' ', '_')}",
                "name": name,
                "quantity": 1,
                "charges": -1,
                "attuned": False,
                "properties": {},
            })
            names.add(name)
        self.items_structured_json = json.dumps(kept)

    # —— ITEM-001: InventoryManager 桥接 ——
    # 使用 engine.item_instance.InventoryManager 统一操作结构化物品栏
    def get_inventory_manager(self):
        """获取 InventoryManager 实例，将结构化物品加载其中。

        ITEM-001: ItemInstance/ItemStack 分离定义与实例，
        支持 quantity、charges、attunement、container、equipped。
        """
        from ..engine.item_instance import InventoryManager, ItemInstance
        mgr = InventoryManager()
        for data in self.items_structured:
            inst = ItemInstance(**{
                k: v for k, v in data.items()
                if k in ("instance_id", "item_id", "name", "quantity", "charges",
                         "max_charges", "equipped", "slot", "attuned",
                         "container_id", "value_gp", "weight_lb")
            })
            if not inst.instance_id:
                import uuid
                inst.instance_id = str(uuid.uuid4())
            mgr.add_item(inst)
        return mgr

    def sync_inventory_from_manager(self, mgr) -> None:
        """将 InventoryManager 中的物品写回 items_structured_json。"""
        self.items_structured_json = json.dumps([
            {
                "instance_id": i.instance_id,
                "item_id": i.item_id,
                "name": i.name,
                "quantity": i.quantity,
                "charges": i.charges,
                "max_charges": i.max_charges,
                "equipped": i.equipped,
                "slot": i.slot,
                "attuned": i.attuned,
                "container_id": i.container_id,
                "value_gp": i.value_gp,
                "weight_lb": i.weight_lb,
            }
            for i in mgr.list_all()
        ])

    # —— 专长桥接 ——
    # 规则: PHB 第五章「专长」— 起源/通用/战斗风格/传奇恩惠
    @property
    def feats(self) -> list[str]:
        """已选专长名列表。"""
        return json.loads(self.feats_json)

    def set_feats(self, names: list[str]) -> None:
        """设置已选专长名列表。"""
        self.feats_json = json.dumps(names)

    # —— 多职业等级桥接 (CHR-006) ——
    @property
    def class_levels(self) -> dict[str, int]:
        """多职业等级映射 {class_name: level}。

        如果未迁移（空字典），返回 {char_class: level} 作为默认。
        """
        cl = json.loads(self.class_levels_json)
        if not cl and self.char_class:
            return {self.char_class: self.level}
        return cl

    def set_class_levels(self, levels: dict[str, int]) -> None:
        """设置多职业等级映射。"""
        self.class_levels_json = json.dumps(levels)

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

    # —— 武器精通授权桥接（P8，方案 §11.2）——
    @property
    def mastery_grants(self) -> list:
        """持久化精通授权列表 [{source_id, mastery_name, acquired_level, ...}]。"""
        return json.loads(self.mastery_grants_json)

    def set_mastery_grants(self, grants: list) -> None:
        self.mastery_grants_json = json.dumps(grants)

    def add_mastery_grant(self, mastery_name: str, *, source_id: str = "",
                          acquired_level: int = 1,
                          weapon_type: str = "", replace_policy: str = "") -> None:
        grants = self.mastery_grants
        if any(g.get("mastery_name") == mastery_name for g in grants):
            return  # 幂等
        grants.append({
            "source_id": source_id,
            "mastery_name": mastery_name,
            "weapon_type": weapon_type,
            "acquired_level": acquired_level,
            "replace_policy": replace_policy,
        })
        self.set_mastery_grants(grants)

    def has_mastery(self, mastery_name: str) -> bool:
        """角色是否拥有该精通授权（战斗解析唯一查询入口）。"""
        return any(g.get("mastery_name") == mastery_name
                   for g in self.mastery_grants)

    # —— 资源池持久化桥接（P6，方案 §9.1/§5.4）——
    @property
    def resource_pools(self) -> dict:
        """持久化资源池：{池名: {current, max, recharge, source_feature_id, ...}}。"""
        return json.loads(self.resource_pools_json)

    def set_resource_pools(self, pools: dict) -> None:
        self.resource_pools_json = json.dumps(pools)

    def pool_current(self, name: str) -> int:
        return int(self.resource_pools.get(name, {}).get("current", 0))

    def pool_max(self, name: str) -> int:
        return int(self.resource_pools.get(name, {}).get("max", 0))

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
              ★ 方案 §5.1: Derived State 唯一入口 —— 复用 build.derive_stats
              （服务器权威推导，禁止在模型内出现第二套 AC 公式）。
        """
        from ..build.derive_stats import derive_ac
        # ITEM-002: 盾牌必须装备在 off_hand 槽位才加 AC，背包中的盾牌不计入
        off_hand_item = self.equipment_slots.get(EquipmentSlots.OFF_HAND.value, "") or ""
        has_shield = "盾牌" in off_hand_item
        self.ac = derive_ac(self.char_class, self.abilities,
                            self.equipped_armor or "", has_shield)


# ──────────────────────────────────────────────────────────────────────────
# 战役 / 场景 / 战斗 / 日志
# ──────────────────────────────────────────────────────────────────────────

class Campaign(SQLModel, table=True):
    """战役：世界设定输入 + AI 生成的完整背景故事 + rolling summary + 世界标记。

    规则依据: ARC-001 不可变规则集标识 — 战役创建时固化 ruleset_id 和 revision。
    """
    id: int | None = Field(default=None, primary_key=True)
    name: str
    setting: str = Field(default="")                  # 玩家输入/编辑的世界设定提示词
    tone: str = Field(default="")                    # 基调（黑暗/英雄/恐怖...）
    world_background: str = Field(default="")        # AI 生成的完整背景故事（长文，持续显示）
    rolling_summary: str = Field(default="")         # 剧情压缩摘要（防上下文失忆）
    world_flags_json: str = Field(default="{}")      # 世界状态标记（NPC关系/阵营/任务）
    # ARC-001: 不可变规则集标识 — 创建战役时固化，运行中只允许显式迁移
    ruleset_id: str = Field(default="dnd5e_2024_core")
    ruleset_revision: str = Field(default="2024.1")
    mechanics_baseline: str = Field(default="srd_5.2.1")  # 机械基线（方案 §2.2）
    # 规则模式（方案 §2.1）: raw_2024 / raw_2024_optional / house_rule / freeform
    rules_mode: str = Field(default="raw_2024")
    content_pack_versions_json: str = Field(default="{}")  # {pack_name: version}
    # P1-05: 乐观锁版本（与 CombatState.version 同构）— 防并发丢失更新
    version: int = Field(default=0)

    @property
    def world_flags(self) -> dict:
        return json.loads(self.world_flags_json)

    def set_world_flags(self, flags: dict) -> None:
        self.world_flags_json = json.dumps(flags)

    @property
    def content_pack_versions(self) -> dict:
        return json.loads(self.content_pack_versions_json)

    def set_content_pack_versions(self, versions: dict) -> None:
        self.content_pack_versions_json = json.dumps(versions)


class Scene(SQLModel, table=True):
    """当前场景：地点/在场NPC/氛围/时间/场景叙事/可做之事/叙事日志。

    ★ ENV-002: objects_json/terrain_json 存储结构化物件与地形实体
      （ObjectEntity/TerrainFeature），取代纯文本 environment。
    """
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
    # ★ ENV-002: 结构化物件与地形
    objects_json: str = Field(default="[]")   # ObjectEntity 序列化列表
    terrain_json: str = Field(default="[]")   # TerrainFeature 序列化列表

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

    # ★ ENV-002: 物件/地形桥接
    @property
    def objects(self) -> list:
        return json.loads(self.objects_json)

    def set_objects(self, objects: list) -> None:
        self.objects_json = json.dumps(objects)

    @property
    def terrain(self) -> list:
        return json.loads(self.terrain_json)

    def set_terrain(self, terrain: list) -> None:
        self.terrain_json = json.dumps(terrain)

    def add_object(self, obj: dict) -> None:
        """添加一个结构化物件。"""
        objs = self.objects
        objs.append(obj)
        self.objects_json = json.dumps(objs)

    def add_terrain(self, terr: dict) -> None:
        """添加一个结构化地形。"""
        terrains = self.terrain
        terrains.append(terr)
        self.terrain_json = json.dumps(terrains)


class CombatState(SQLModel, table=True):
    """战斗状态（持久化）：先攻顺序/轮次/参战者快照/是否激活。

    规则: R-CMB-001/002  出处: 进行游戏/战斗流程.htm
    ★ API-001: version 字段实现乐观锁——每次保存递增，
      客户端提交动作时携带 expected_version 检测并发冲突。
    """
    id: int | None = Field(default=None, primary_key=True)
    campaign_id: int | None = Field(default=None, foreign_key="campaign.id")
    initiative_order_json: str = Field(default="[]")   # [{cid,name,initiative,side}]
    participants_json: str = Field(default="[]")        # 参战者快照
    round: int = 0
    current_index: int = 0
    active: bool = False
    version: int = 0

    @property
    def initiative_order(self) -> list:
        return json.loads(self.initiative_order_json)

    def set_initiative_order(self, order: list) -> None:
        self.initiative_order_json = json.dumps(order)


# ──────────────────────────────────────────────────────────────────────────
# CharacterAggregate provenance（改造方案 §5.3）
# ──────────────────────────────────────────────────────────────────────────
# Grant / ChoiceRecord 从「角色构建日志工具」升级为角色领域的 provenance
# 核心：可回答「某能力从何而来、何时获得、依据哪个 ruleset revision」。

class CharacterGrant(SQLModel, table=True):
    """角色授予记录（持久化）— 追踪每个能力/资源的来源。

    grant_type: species/background/class/subclass/feat/item/skill/tool/
                language/spell/mastery/resource
    """
    id: int | None = Field(default=None, primary_key=True)
    character_id: int = Field(default=0, foreign_key="character.id")
    grant_id: str = Field(default="")         # 唯一授予 ID（生成或外部传入）
    grant_type: str = Field(default="")
    source_id: str = Field(default="")        # 来源 ID（物种/职业/背景 ID 等）
    source_name: str = Field(default="")
    source_revision: str = Field(default="")  # 来源定义版本（方案 §5.3）
    granted_item_id: str = Field(default="")
    level_acquired: int = Field(default=1)
    ruleset_revision: str = Field(default="2024.1")
    metadata_json: str = Field(default="{}")

    @property
    def meta(self) -> dict:
        """授予附加元数据（属性名避开 SQLModel 保留的 metadata）。"""
        return json.loads(self.metadata_json)

    def set_meta(self, data: dict) -> None:
        self.metadata_json = json.dumps(data)

    def to_dict(self) -> dict:
        return {
            "grant_id": self.grant_id,
            "grant_type": self.grant_type,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_revision": self.source_revision,
            "granted_item_id": self.granted_item_id,
            "level_acquired": self.level_acquired,
            "ruleset_revision": self.ruleset_revision,
            "metadata": self.meta,
        }


class CharacterChoice(SQLModel, table=True):
    """角色选择记录（持久化）— 选择来源与合法选项快照。

    choice_type: species/background/class/subclass/feat/asi/skill/tool/
                 language/mastery/spell/metamagic/invocation/expertise
    """
    id: int | None = Field(default=None, primary_key=True)
    character_id: int = Field(default=0, foreign_key="character.id")
    choice_id: str = Field(default="")
    choice_type: str = Field(default="")
    source_id: str = Field(default="")           # 触发该选择的来源
    selected_values_json: str = Field(default="[]")
    legal_options_json: str = Field(default="[]")  # 选择时的合法选项快照
    level_at_choice: int = Field(default=1)
    ruleset_revision: str = Field(default="2024.1")
    validated: bool = Field(default=False)

    @property
    def selected_values(self) -> list:
        return json.loads(self.selected_values_json)

    def set_selected_values(self, values: list) -> None:
        self.selected_values_json = json.dumps(values)

    @property
    def legal_options(self) -> list:
        return json.loads(self.legal_options_json)

    def set_legal_options(self, options: list) -> None:
        self.legal_options_json = json.dumps(options)

    def to_dict(self) -> dict:
        return {
            "choice_id": self.choice_id,
            "choice_type": self.choice_type,
            "source_id": self.source_id,
            "selected_values": self.selected_values,
            "legal_options_snapshot": self.legal_options,
            "level_at_choice": self.level_at_choice,
            "ruleset_revision": self.ruleset_revision,
            "validated": self.validated,
        }


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
