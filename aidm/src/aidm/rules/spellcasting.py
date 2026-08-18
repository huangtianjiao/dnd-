"""Spellcasting 规则模块（方案 §10.2-§10.4）。

- SpellcastingModel: 职业施法模型（施法属性/准备制或已知制/数量表/契约魔法）
- 数量函数: known_spells_count / prepared_spells_count（2024 PHB 表）
- prepare_spell: 准备法术的唯一服务（越权选择拒绝、数量超限拒绝）

规则依据:
  PHB2024 各职业施法（准备制: 牧师/德鲁伊/圣武士/游侠/法师；
  已知制: 吟游诗人/术士/魔契师；契约魔法独立）
  改造方案 §10.4 SpellcastingModel
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PreparationModel(StrEnum):
    PREPARED = "prepared"        # 准备制（施法者从已知列表准备每天法术）
    KNOWN = "known"              # 已知制（learned spells 直接可用）
    SPELLBOOK = "spellbook"      # 法术书制（法师：书内已知 + 每日准备）
    PACT = "pact"                # 契约魔法（魔契师独立 slots）


@dataclass(frozen=True)
class SpellcastingModel:
    class_name: str                # 中文职业名
    casting_ability: str           # str/dex/con/int/wis/cha
    preparation_model: PreparationModel
    ritual_policy: str = "class_rituals"   # 仪式施法政策
    spellbook_policy: str = ""     # spellbook 制职业说明

    def is_prepared_caster(self) -> bool:
        return self.preparation_model in (
            PreparationModel.PREPARED, PreparationModel.SPELLBOOK)


#  职业 → 施法模型（2024 PHB）
SPELLCASTING_MODELS: dict[str, SpellcastingModel] = {
    "吟游诗人": SpellcastingModel("吟游诗人", "cha", PreparationModel.KNOWN),
    "牧师":     SpellcastingModel("牧师", "wis", PreparationModel.PREPARED),
    "德鲁伊":   SpellcastingModel("德鲁伊", "wis", PreparationModel.PREPARED),
    "圣武士":   SpellcastingModel("圣武士", "cha", PreparationModel.PREPARED,
                                   ritual_policy="none"),
    "游侠":     SpellcastingModel("游侠", "wis", PreparationModel.PREPARED,
                                   ritual_policy="none"),
    "术士":     SpellcastingModel("术士", "cha", PreparationModel.KNOWN),
    "魔契师":   SpellcastingModel("魔契师", "cha", PreparationModel.PACT),
    "法师":     SpellcastingModel("法师", "int", PreparationModel.SPELLBOOK),
}


def model_for(class_name: str) -> SpellcastingModel | None:
    return SPELLCASTING_MODELS.get(class_name)


def is_caster(class_name: str) -> bool:
    return class_name in SPELLCASTING_MODELS


# ──────────────────────────────────────────────────────────────────────────
# 数量表（PHB2024）
# ──────────────────────────────────────────────────────────────────────────

# 已知制职业（吟游诗人/术士）已知法术数量表
KNOWN_SPELLS_BY_LEVEL: dict[int, int] = {
    1: 4, 2: 5, 3: 6, 4: 7, 5: 9, 6: 10, 7: 11, 8: 12, 9: 14, 10: 15,
    11: 16, 12: 16, 13: 18, 14: 19, 15: 20, 16: 20, 17: 22, 18: 22,
    19: 22, 20: 22,
}

# 已知制职业已知数量（魔契师列；与 Bard/sorcerer 同表，SRD 差异以源锚点为准）
WARLOCK_KNOWN_BY_LEVEL: dict[int, int] = KNOWN_SPELLS_BY_LEVEL

# 准备制职业: 准备数 = 施法属性调整 + 表值（半施法者用职业等级折半）
# 全施法者（牧师/德鲁伊/法师）: level
# 半施法者（圣武士/游侠）: max(1, floor(类等级/2))
PREPARED_BASE_BY_LEVEL: dict[str, int] = {
    "full": 1,      # 1 级准备 = 修正 + 1（全施法者按等级）
    "half": 1,      # 半施法者按向上取整(等级/2) 的最小值
}


def known_spells_count(class_name: str, level: int) -> int:
    """已知制职业在某等级可拥有的已知法术数量。"""
    if class_name in ("吟游诗人", "术士"):
        return KNOWN_SPELLS_BY_LEVEL.get(int(level), 0)
    if class_name == "魔契师":
        return WARLOCK_KNOWN_BY_LEVEL.get(int(level), 0)
    raise ValueError(f"{class_name} 不是已知制职业")


def prepared_spells_count(class_name: str, level: int,
                          casting_mod: int) -> int:
    """准备制职业在某等级可准备的法术数量。

    2024 PHB:
      - 全施法者（牧师/德鲁伊/法师）: 施法属性调整 + 施法者等级
      - 半施法者（圣武士/游侠）: 施法属性调整 + max(1, 该类等级/2 向下取整)
    """
    if not is_caster(class_name):
        return 0
    base = max(1, int(level) // 2) if class_name in ("圣武士", "游侠") else int(level)
    return max(1, int(casting_mod) + base)


# ──────────────────────────────────────────────────────────────────────────
# 准备法术服务（方案 §10.3 prepared_spells 唯一写入路径）
# ──────────────────────────────────────────────────────────────────────────

def prepare_spell(ch, spell_name: str, *, legal_source: set | None = None,
                  db_path: str | None = None) -> dict:
    """把法术加入角色的 prepared_spells。

    校验（越权选择拒绝，方案 §6.4）:
      1. 职业必须为准备制/法术书制施法者
      2. 法术必须可及（legal_source 未提供时用职业法术列表）
      3. 数量不得超过 prepared_spells_count（花名册限制）
      4. 已在准备中 → 幂等返回

    Returns:
        {"prepared": [...], "count": n, "limit": N}
    Raises:
        ValueError: 非准备制 / 越权法术 / 数量超限
    """
    from ..data.spells import get_spell
    from ..stats import store

    m = model_for(ch.char_class)
    if m is None or not m.is_prepared_caster():
        raise ValueError(f"{ch.char_class} 不是准备制施法者，无法准备法术")
    spell = get_spell(spell_name)
    if spell is None:
        raise ValueError(f"未知法术 {spell_name!r}")
    if legal_source is not None and spell_name not in legal_source:
        raise ValueError(f"法术 {spell_name!r} 不在该施法者可及来源内")
    # 环阶门控（方案 §10.3）: 法术环阶不得超过职业当前可用最高环
    from ..data.spells import max_spell_slots
    class_level = int(ch.class_levels.get(ch.char_class, ch.level))
    if m.preparation_model == PreparationModel.PACT:
        from ..engine.multiclass import MulticlassService
        slots = MulticlassService().get_pact_slots(class_level)
    else:
        slots = max_spell_slots(class_level)
    max_ring = max(slots.keys(), default=0) if slots else 0
    if int(getattr(spell, "level", 0)) > max_ring:
        raise ValueError(
            f"法术 {spell_name!r} 为 {spell.level} 环，超过当前最高可用环 {max_ring}")

    prepared = list(ch.prepared_spells)
    if spell_name in prepared:
        return {"prepared": prepared, "count": len(prepared),
                "limit": _limit(ch, m)}

    limit = _limit(ch, m)
    if len(prepared) >= limit:
        raise ValueError(
            f"准备法术数量达到上限 {limit}（需要先更换已准备法术）")
    prepared.append(spell_name)
    ch.set_prepared_spells(prepared)
    if db_path is not None:
        store.save_character(ch, db_path)
    return {"prepared": prepared, "count": len(prepared), "limit": limit}


def _limit(ch, m: SpellcastingModel) -> int:
    mod = ch.ability_mod(m.casting_ability)
    # 该类职业等级（多职业时 half-caster 用职业等级折半）
    class_level = int(ch.class_levels.get(ch.char_class, ch.level))
    return prepared_spells_count(ch.char_class, class_level, mod)


def unprepared_spell(ch, spell_name: str, *, db_path: str | None = None) -> dict:
    """从 prepared_spells 移除一个法术（幂等）。"""
    from ..stats import store
    prepared = list(ch.prepared_spells)
    if spell_name in prepared:
        prepared.remove(spell_name)
        ch.set_prepared_spells(prepared)
        if db_path is not None:
            store.save_character(ch, db_path)
    return {"prepared": prepared, "count": len(prepared)}
