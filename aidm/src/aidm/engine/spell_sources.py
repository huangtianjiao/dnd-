"""法术来源体系 — 区分已知、已准备、法术书条目和职业授予。

SPL-003: 建立 SpellGrant / PreparedSpell / SpellbookEntry / KnownSpell 来源。
规则依据:
  - 法师只能施展法术书中且已准备的非仪式法术
  - 牧师/德鲁伊准备 WIS mod + 等级 数量的法术
  - 圣武士准备 CHA mod + 等级/2（最少1）数量的法术
  - 魔契师是"已知"列表，不准备
  - 戏法始终已知且不消耗法术位

出处: topics/玩家手册2024/法术/法术准备.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Set


class SpellSource(Enum):
    """法术来源类型。"""

    KNOWN = "known"              # 已知法术（术士/魔契师/吟游诗人）
    PREPARED = "prepared"        # 已准备法术（法师/牧师/德鲁伊/圣武士/游侠）
    SPELLBOOK = "spellbook"      # 法术书条目（法师抄录的法术）
    CLASS_GRANT = "class_grant"  # 职业特性直接授予（如领域法术）
    RACIAL = "racial"            # 物种特质授予
    ITEM = "item"                # 魔法物品授予（如法杖中的法术）
    FEAT = "feat"                # 专长授予


@dataclass
class SpellAcquisition:
    """单个法术的获取记录。

    追踪法术来源、获取等级、是否可准备等元数据，
    用于运行时验证施法资格。
    """

    spell_name: str
    source_type: SpellSource
    acquired_level: int = 1
    source_detail: str = ""       # 具体来源描述（如"3级法师选择"）
    always_prepared: bool = False  # 是否始终视为已准备（领域法术等）
    can_prepare: bool = True       # 是否可被准备（某些来源不可准备）

    def is_available(self, prepared_set: Optional[Set[str]] = None) -> bool:
        """判断该法术在当前状态下是否可施展。

        Args:
            prepared_set: 当前已准备的法术名集合；None 表示不检查准备状态

        Returns:
            该法术是否可施展
        """
        if self.source_type in (SpellSource.KNOWN, SpellSource.RACIAL,
                                SpellSource.CLASS_GRANT, SpellSource.ITEM,
                                SpellSource.FEAT):
            return True
        if self.source_type == SpellSource.SPELLBOOK:
            # 法术书法术需要被准备才能施展
            if prepared_set is None:
                return False
            return self.spell_name in prepared_set
        if self.source_type == SpellSource.PREPARED:
            if prepared_set is None:
                return False
            return self.spell_name in prepared_set
        return False


@dataclass
class SpellSourceRegistry:
    """法术来源注册表 — 管理角色所有法术获取记录。

    设计原则:
      - 每个法术可有多个来源记录（如同时来自法术书和魔法物品）
      - 准备法术列表独立维护，每日长休后可重新选择
      - 施法资格验证统一通过此注册表进行
    """

    acquisitions: List[SpellAcquisition] = field(default_factory=list)
    prepared_spells: Set[str] = field(default_factory=set)

    def add(self, acquisition: SpellAcquisition) -> None:
        """添加一条法术获取记录。"""
        self.acquisitions.append(acquisition)

    def remove_by_source(self, source_type: SpellSource,
                         spell_name: Optional[str] = None) -> None:
        """按来源类型移除获取记录。"""
        self.acquisitions = [
            a for a in self.acquisitions
            if not (a.source_type == source_type
                    and (spell_name is None or a.spell_name == spell_name))
        ]

    def get_all_spell_names(self) -> Set[str]:
        """获取所有已获取的法术名（不区分准备状态）。"""
        return {a.spell_name for a in self.acquisitions}

    def get_castable_spells(self) -> Set[str]:
        """获取当前可施展的法术名集合。

        包含:
          - 已知法术（始终可施展）
          - 始终准备的法术
          - 当前已准备的法术
        """
        castable: Set[str] = set()
        for acq in self.acquisitions:
            if acq.always_prepared:
                castable.add(acq.spell_name)
            elif acq.source_type in (SpellSource.KNOWN, SpellSource.RACIAL,
                                     SpellSource.CLASS_GRANT, SpellSource.ITEM,
                                     SpellSource.FEAT):
                castable.add(acq.spell_name)
            elif acq.source_type in (SpellSource.PREPARED,
                                     SpellSource.SPELLBOOK):
                if acq.spell_name in self.prepared_spells:
                    castable.add(acq.spell_name)
        return castable

    def can_cast(self, spell_name: str) -> bool:
        """判断角色是否可以施展指定法术。"""
        return spell_name in self.get_castable_spells()

    def prepare_spell(self, spell_name: str) -> bool:
        """准备一个法术。

        Returns:
            是否成功准备（法术必须在获取列表中且可准备）
        """
        for acq in self.acquisitions:
            if acq.spell_name == spell_name and acq.can_prepare:
                self.prepared_spells.add(spell_name)
                return True
        return False

    def unprepare_spell(self, spell_name: str) -> None:
        """取消准备一个法术。"""
        self.prepared_spells.discard(spell_name)

    def clear_prepared(self) -> None:
        """清空已准备法术列表（每日重新准备前调用）。"""
        self.prepared_spells.clear()


# ── 职业准备法术数量上限 ──────────────────────────────────────────────

def max_prepared_spells(class_name: str, level: int,
                        casting_ability_mod: int) -> int:
    """计算职业在该等级可准备的法术数量上限。

    规则依据:
      - 法师: 可准备 = 施法属性调整值 + 等级（最低1）
      - 牧师/德鲁伊: 可准备 = 施法属性调整值 + 等级（最低1）
      - 圣武士: 可准备 = 施法属性调整值 + floor(等级/2)（最低1）
      - 游侠: 可准备 = 施法属性调整值 + floor(等级/2)（最低1）
      - 术士/魔契师/吟游诗人: 不使用准备机制（已知法术列表）

    出处: topics/玩家手册2024/法术/法术准备.htm
    """
    if class_name in ("法师", "牧师", "德鲁伊"):
        return max(1, casting_ability_mod + level)
    if class_name in ("圣武士", "游侠"):
        return max(1, casting_ability_mod + level // 2)
    # 不使用准备机制的职业返回0
    return 0


# ── 从 Character 模型构建来源注册表 ──────────────────────────────────

def build_registry_from_character(ch) -> SpellSourceRegistry:
    """从 Character 模型构建法术来源注册表。

    处理逻辑:
      1. known_spells 列表中的法术 → 根据职业标记为 KNOWN 或 PREPARED
      2. 戏法（level=0）→ 标记为 KNOWN 且 always_prepared
      3. 如果 known_spells 为空 → 角色不会任何法术（不回退）

    Args:
        ch: Character SQLModel 实例

    Returns:
        填充好的 SpellSourceRegistry
    """
    from ..data import spells as spell_db

    registry = SpellSourceRegistry()
    char_class = ch.char_class or ""
    level = ch.level or 1

    # 判断该职业是否使用"准备"机制
    uses_preparation = char_class in ("法师", "牧师", "德鲁伊",
                                      "圣武士", "游侠")

    # 获取已知法术列表
    known = ch.known_spells or []

    # SPL-003: known_spells 为空时不回退——空意味着角色不会任何法术

    # ★ SPL-003: 准备数量上限 = 施法属性调整值 + 等级（圣武士/游侠为一半）
    prepared_limit = None
    if uses_preparation:
        from ..data.spells import get_casting_ability
        try:
            casting_ability = get_casting_ability(char_class)
        except ValueError:
            casting_ability = "int"
        casting_mod = (getattr(ch, "ability_mod", None)
                       or (lambda ab: ((ch.abilities or {}).get(ab, 10) - 10) // 2))
        if callable(casting_mod):
            mod_val = casting_mod(casting_ability.lower())
        else:
            mod_val = 0
        prepared_limit = max_prepared_spells(char_class, level, mod_val)

    for spell_name in known:
        # 查询法术数据以确定环阶
        spell_data = spell_db.get_spell(spell_name)
        is_cantrip = spell_data is not None and spell_data.level == 0

        if is_cantrip:
            # 戏法始终已知且可施展
            registry.add(SpellAcquisition(
                spell_name=spell_name,
                source_type=SpellSource.KNOWN,
                acquired_level=1,
                source_detail="戏法",
                always_prepared=True,
                can_prepare=False,
            ))
        elif uses_preparation:
            # 使用准备机制的职业：法术进入"可准备"列表
            registry.add(SpellAcquisition(
                spell_name=spell_name,
                source_type=SpellSource.PREPARED,
                acquired_level=level,
                source_detail=f"{char_class}职业法术",
                can_prepare=True,
            ))
            # ★ SPL-003: 只准备前 N 个（N=施法属性调整值+等级/半），
            #   而非"默认全部准备"的简化处理
            if prepared_limit is not None and len(registry.prepared_spells) < prepared_limit:
                registry.prepared_spells.add(spell_name)
        else:
            # 不使用准备机制的职业（术士/魔契师/吟游诗人）：已知即可施展
            registry.add(SpellAcquisition(
                spell_name=spell_name,
                source_type=SpellSource.KNOWN,
                acquired_level=level,
                source_detail=f"{char_class}已知法术",
                can_prepare=False,
            ))

    return registry
