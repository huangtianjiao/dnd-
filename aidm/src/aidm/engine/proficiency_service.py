"""熟练度服务 — ProficiencyGrant 集合与 CheckService。

CHK-001: 技能熟练由 LLM 或硬编码决定。
本模块建立统一的熟练度派生体系：

  1. ProficiencyGrant — 单条熟练授予记录（来源+类型+技能/武器/护甲）
  2. ProficiencyRegistry — 管理角色所有熟练授予记录
  3. CheckService — 从 ProficiencyRegistry 派生熟练/专精/半熟练

规则依据:
  - 技能熟练来自职业、背景、物种、专长
  - 专精(expertise)加两次熟练加值
  - 半熟练(jack of all trades)加一半熟练加值
  - 未熟练角色的 Search 不加 PB

出处: topics/玩家手册2024/进行游戏/属性检定.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class ProficiencyType(Enum):
    """熟练度类型。"""

    SKILL = "skill"            # 技能熟练
    WEAPON = "weapon"          # 武器熟练
    ARMOR = "armor"            # 护甲熟练
    TOOL = "tool"              # 工具熟练
    SAVING_THROW = "save"      # 豁免熟练
    LANGUAGE = "language"      # 语言


class ProficiencyLevel(Enum):
    """熟练等级。"""

    NONE = 0           # 不熟练
    HALF = 1           # 半熟练（吟游诗人万金油）
    PROFICIENT = 2     # 熟练
    EXPERT = 3         # 专精（加两次 PB）


@dataclass
class ProficiencyGrant:
    """单条熟练授予记录。

    追踪熟练来源、类型、具体项目、等级，
    用于运行时派生熟练状态。

    属性:
        grant_type: 熟练类型
        item: 具体项目名（如"察觉"、"长剑"、"轻甲"）
        level: 熟练等级
        source: 来源描述（如"职业:战士"、"背景:罪犯"）
        source_type: 来源类型（class/background/species/feat/item）
    """

    grant_type: ProficiencyType
    item: str
    level: ProficiencyLevel = ProficiencyLevel.PROFICIENT
    source: str = ""
    source_type: str = ""


@dataclass
class ProficiencyRegistry:
    """熟练度注册表 — 管理角色所有熟练授予记录。

    设计原则:
      - 每条熟练可有多条来源记录（如同时来自职业和背景）
      - 取最高等级（expert > proficient > half > none）
      - 统一通过此注册表查询熟练状态
    """

    grants: List[ProficiencyGrant] = field(default_factory=list)

    def add(self, grant: ProficiencyGrant) -> None:
        """添加一条熟练授予记录。"""
        self.grants.append(grant)

    def add_skill(self, skill: str, level: ProficiencyLevel = ProficiencyLevel.PROFICIENT,
                  source: str = "", source_type: str = "") -> None:
        """便捷添加技能熟练。"""
        self.add(ProficiencyGrant(
            grant_type=ProficiencyType.SKILL,
            item=skill,
            level=level,
            source=source,
            source_type=source_type,
        ))

    def get_proficiency_level(self, grant_type: ProficiencyType,
                              item: str) -> ProficiencyLevel:
        """获取指定项目的熟练等级。

        取所有来源中的最高等级。
        """
        best = ProficiencyLevel.NONE
        for g in self.grants:
            if g.grant_type != grant_type:
                continue
            # 精确匹配或类别匹配
            if g.item == item or g.item == "*":
                if g.level.value > best.value:
                    best = g.level
        return best

    def is_proficient(self, grant_type: ProficiencyType, item: str) -> bool:
        """判断是否熟练指定项目。"""
        level = self.get_proficiency_level(grant_type, item)
        return level != ProficiencyLevel.NONE

    def is_expert(self, grant_type: ProficiencyType, item: str) -> bool:
        """判断是否专精指定项目。"""
        return self.get_proficiency_level(grant_type, item) == ProficiencyLevel.EXPERT

    def get_all_skills(self) -> Set[str]:
        """获取所有已熟练的技能名。"""
        return {g.item for g in self.grants
                if g.grant_type == ProficiencyType.SKILL
                and g.level != ProficiencyLevel.NONE}

    def get_proficient_saves(self) -> Set[str]:
        """获取所有熟练的豁免属性。"""
        return {g.item for g in self.grants
                if g.grant_type == ProficiencyType.SAVING_THROW
                and g.level != ProficiencyLevel.NONE}


# ── CheckService — 从 ProficiencyRegistry 派生熟练加值 ──────────────

@dataclass
class CheckService:
    """检定服务 — 从 ProficiencyRegistry 派生熟练状态。

    CHK-001: 技能熟练由 LLM 或硬编码决定。
    本服务从角色 ProficiencyGrant 集合派生熟练/专精/半熟练，
    替代之前信任 intent.proficient 的做法。

    使用方式:
        service = CheckService(registry, proficiency_bonus=2)
        is_prof = service.is_skill_proficient("察觉")
        mod = service.get_skill_modifier("察觉", ability_mod=3)
    """

    registry: ProficiencyRegistry
    proficiency_bonus: int = 2

    def is_skill_proficient(self, skill: str) -> bool:
        """判断角色是否熟练指定技能。"""
        return self.registry.is_proficient(ProficiencyType.SKILL, skill)

    def is_skill_expert(self, skill: str) -> bool:
        """判断角色是否专精指定技能。"""
        return self.registry.is_expert(ProficiencyType.SKILL, skill)

    def get_skill_modifier(self, skill: str, ability_mod: int) -> int:
        """计算技能检定调整值。

        规则:
          - 熟练: ability_mod + proficiency_bonus
          - 专精: ability_mod + 2 * proficiency_bonus
          - 半熟练: ability_mod + proficiency_bonus // 2
          - 不熟练: ability_mod

        出处: topics/玩家手册2024/进行游戏/属性检定.htm
        """
        level = self.registry.get_proficiency_level(ProficiencyType.SKILL, skill)
        if level == ProficiencyLevel.EXPERT:
            return ability_mod + 2 * self.proficiency_bonus
        elif level == ProficiencyLevel.PROFICIENT:
            return ability_mod + self.proficiency_bonus
        elif level == ProficiencyLevel.HALF:
            return ability_mod + self.proficiency_bonus // 2
        else:
            return ability_mod

    def is_save_proficient(self, save_ability: str) -> bool:
        """判断角色是否熟练指定豁免属性。"""
        return self.registry.is_proficient(ProficiencyType.SAVING_THROW, save_ability)

    def get_save_modifier(self, save_ability: str, ability_mod: int) -> int:
        """计算豁免检定调整值。

        规则:
          - 熟练: ability_mod + proficiency_bonus
          - 不熟练: ability_mod

        出处: topics/玩家手册2024/进行游戏/豁免检定.htm
        """
        if self.is_save_proficient(save_ability):
            return ability_mod + self.proficiency_bonus
        return ability_mod

    def is_weapon_proficient(self, weapon: str) -> bool:
        """判断角色是否熟练指定武器。"""
        return self.registry.is_proficient(ProficiencyType.WEAPON, weapon)

    def is_armor_proficient(self, armor: str) -> bool:
        """判断角色是否熟练指定护甲。"""
        return self.registry.is_proficient(ProficiencyType.ARMOR, armor)


# ── 从 Character 模型构建熟练度注册表 ──────────────────────────────

def build_registry_from_character(ch) -> ProficiencyRegistry:
    """从 Character 模型构建熟练度注册表。

    处理逻辑:
      1. 从 skill_prof_json 读取技能熟练列表
      2. 从 char_class 添加职业豁免熟练
      3. 从 char_class 添加武器/护甲熟练
      4. 从 feats_json 检查专精专长

    Args:
        ch: Character SQLModel 实例

    Returns:
        填充好的 ProficiencyRegistry
    """
    from ..data.equipment import ARMOR_PROFICIENCY

    registry = ProficiencyRegistry()

    # 1. 技能熟练（从 skill_prof_json 读取）
    skill_profs = ch.skill_prof or []
    for skill in skill_profs:
        registry.add_skill(
            skill=skill,
            level=ProficiencyLevel.PROFICIENT,
            source=f"角色卡",
            source_type="character",
        )

    # 2. 职业豁免熟练
    class_name = ch.char_class or ""
    class_save_profs = _get_class_save_proficiencies(class_name)
    for save_ab in class_save_profs:
        registry.add(ProficiencyGrant(
            grant_type=ProficiencyType.SAVING_THROW,
            item=save_ab,
            level=ProficiencyLevel.PROFICIENT,
            source=f"职业:{class_name}",
            source_type="class",
        ))

    # 3. 职业→武器/护甲熟练
    # 从 ARMOR_PROFICIENCY 表读取护甲类别熟练
    armor_cats = ARMOR_PROFICIENCY.get(class_name, set())
    for cat in armor_cats:
        registry.add(ProficiencyGrant(
            grant_type=ProficiencyType.ARMOR,
            item=cat,
            level=ProficiencyLevel.PROFICIENT,
            source=f"职业:{class_name}",
            source_type="class",
        ))

    # 武器熟练通过 class_weapon_proficient() 查询，此处注册通配符
    from . import equipment as _eq
    if class_name in ("战士", "圣武士", "游侠", "野蛮人", "牧师", "德鲁伊"):
        registry.add(ProficiencyGrant(
            grant_type=ProficiencyType.WEAPON,
            item="*",
            level=ProficiencyLevel.PROFICIENT,
            source=f"职业:{class_name}",
            source_type="class",
        ))

    # 4. 专精专长检查
    feat_names = ch.feats or []
    expertise_skills = _get_expertise_from_feats(feat_names)
    for skill in expertise_skills:
        registry.add_skill(
            skill=skill,
            level=ProficiencyLevel.EXPERT,
            source=f"专精专长",
            source_type="feat",
        )

    return registry


# ── 职业豁免熟练表 ──────────────────────────────────────────────────

# PHB2024 职业豁免熟练表
_CLASS_SAVE_PROFICIENCIES: Dict[str, List[str]] = {
    "野蛮人": ["str", "con"],
    "吟游诗人": ["dex", "cha"],
    "牧师": ["wis", "cha"],
    "德鲁伊": ["wis", "int"],
    "战士": ["str", "con"],
    "武僧": ["str", "dex"],
    "圣武士": ["wis", "cha"],
    "游侠": ["str", "dex"],
    "盗贼": ["dex", "int"],
    "术士": ["con", "cha"],
    "魔契师": ["wis", "cha"],
    "法师": ["wis", "int"],
}


def _get_class_save_proficiencies(class_name: str) -> List[str]:
    """获取职业的豁免熟练属性列表。"""
    return _CLASS_SAVE_PROFICIENCIES.get(class_name, [])


# ── 专精专长→技能映射 ────────────────────────────────────────────────

# 提供专精(expertise)的专长→技能列表
_EXPERTISE_FEATS: Dict[str, List[str]] = {
    "技艺精湛": [],  # 选择两项技能获得专精
    "盗贼专精": [],  # 盗贼子职特性
    # 可扩展更多
}


def _get_expertise_from_feats(feat_names: List[str]) -> List[str]:
    """从专长列表中提取专精技能。

    简化处理：技艺精湛等专长提供专精，
    但具体技能选择存储在角色卡的选择记录中。
    此处返回空列表，实际专精应由角色卡显式标记。
    """
    return []
