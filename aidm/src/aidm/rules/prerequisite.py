"""PrerequisiteEvaluator — 先决条件统一求值（方案 §4.4）。

专长、多职业、装备、法术、Subclass、可选特性共用同一套先决条件求值器，
避免每个子系统各写一份。支持原子条件与 ANY/ALL/NOT 嵌套。

原子条件:
  - level >= N              角色总等级
  - class_level(c) >= N     某职业的职业等级
  - ability(ab) >= N        属性值（str/dex/con/int/wis/cha）
  - has_feature(id)         拥有特性（feature_id 或中文名）
  - has_proficiency(id)     拥有熟练（技能/武器/护甲/工具名）

逻辑组合:
  ALL(...)、ANY(...)、NOT(...) 可嵌套。

求值返回 (ok, failures)：failures 为未满足谓词的可读描述列表，
供 422 RuleViolation/PrerequisiteNotMet 错误输出。
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PrereqType(StrEnum):
    LEVEL = "level"
    CLASS_LEVEL = "class_level"
    ABILITY = "ability"
    HAS_FEATURE = "has_feature"
    HAS_PROFICIENCY = "has_proficiency"
    ANY = "any"
    ALL = "all"
    NOT = "not"


@dataclass(frozen=True)
class Prerequisite:
    """一条先决条件（原子或组合）。"""

    type: PrereqType
    args: Any = None            # 原子: [名称, 数值]；组合: [子条件...]
    children: tuple[Prerequisite, ...] = field(default_factory=tuple)


def level(min_level: int) -> Prerequisite:
    return Prerequisite(PrereqType.LEVEL, min_level)


def class_level(class_name: str, min_level: int) -> Prerequisite:
    return Prerequisite(PrereqType.CLASS_LEVEL, [class_name, min_level])


def ability(ab: str, min_score: int) -> Prerequisite:
    return Prerequisite(PrereqType.ABILITY, [ab, min_score])


def has_feature(feature_id: str) -> Prerequisite:
    return Prerequisite(PrereqType.HAS_FEATURE, feature_id)


def has_proficiency(prof_id: str) -> Prerequisite:
    return Prerequisite(PrereqType.HAS_PROFICIENCY, prof_id)


def all_of(*items: Prerequisite) -> Prerequisite:
    return Prerequisite(PrereqType.ALL, children=items)


def any_of(*items: Prerequisite) -> Prerequisite:
    return Prerequisite(PrereqType.ANY, children=items)


def not_of(item: Prerequisite) -> Prerequisite:
    return Prerequisite(PrereqType.NOT, children=(item,))


class PrerequisiteContext:
    """求值上下文（角色状态快照 + 职业名映射）。"""

    def __init__(self, *, level: int = 1,
                 class_levels: dict[str, int] | None = None,
                 abilities: dict[str, int] | None = None,
                 features: Sequence[str] = (),
                 proficiencies: Sequence[str] = ()) -> None:
        self.level = int(level)
        # 职业等级：键同时接受英文 key 与中文名（如 "fighter"/"战士"）
        self.class_levels = {k: int(v) for k, v in (class_levels or {}).items()}
        self.abilities = dict(abilities or {})
        self.features = set(features)
        self.proficiencies = set(proficiencies)

    def _class_level_of(self, name: str) -> int:
        zh = {"野蛮人": "barbarian", "吟游诗人": "bard", "牧师": "cleric",
              "德鲁伊": "druid", "战士": "fighter", "武僧": "monk",
              "圣武士": "paladin", "游侠": "ranger", "游荡者": "rogue",
              "术士": "sorcerer", "魔契师": "warlock", "法师": "wizard"}
        key = zh.get(name, name)
        if key in self.class_levels:
            return self.class_levels[key]
        if name in self.class_levels:
            return self.class_levels[name]
        return 0

    def evaluate(self, pre: Prerequisite) -> tuple[bool, list[str]]:
        """递归求值。返回 (是否满足, 未满足谓词描述列表)。"""
        t = pre.type
        if t == PrereqType.LEVEL:
            ok = self.level >= int(pre.args)
            fail = [] if ok else [f"总等级 {self.level} < {pre.args}"]
            return ok, fail
        if t == PrereqType.CLASS_LEVEL:
            name, need = pre.args
            got = self._class_level_of(name)
            ok = got >= int(need)
            fail = [] if ok else [f"{name} 职业等级 {got} < {need}"]
            return ok, fail
        if t == PrereqType.ABILITY:
            ab, need = pre.args
            score = int(self.abilities.get(ab, 0))
            ok = score >= int(need)
            fail = [] if ok else [f"{ab} 属性 {score} < {need}"]
            return ok, fail
        if t == PrereqType.HAS_FEATURE:
            ok = pre.args in self.features
            fail = [] if ok else [f"缺少特性 {pre.args!r}"]
            return ok, fail
        if t == PrereqType.HAS_PROFICIENCY:
            ok = pre.args in self.proficiencies
            fail = [] if ok else [f"缺少熟练 {pre.args!r}"]
            return ok, fail
        if t == PrereqType.ALL:
            failures: list[str] = []
            for ch in pre.children:
                ok, fl = self.evaluate(ch)
                if not ok:
                    failures.extend(fl)
            return not failures, failures
        if t == PrereqType.ANY:
            for ch in pre.children:
                ok, _ = self.evaluate(ch)
                if ok:
                    return True, []
            return False, ["任一条件均未满足"]
        if t == PrereqType.NOT:
            ok, _ = self.evaluate(pre.children[0])
            return (not ok), [] if not ok else ["排除条件被满足"]
        raise ValueError(f"未知先决条件类型: {t}")


def evaluate(pre: Prerequisite, **ctx_kwargs: Any) -> tuple[bool, list[str]]:
    """便捷入口：构造上下文并求值。"""
    return PrerequisiteContext(**ctx_kwargs).evaluate(pre)
