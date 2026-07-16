"""子职业数据表 — 48个子职业 (12职业×4)。

每个子职业含：name, en_name, class_name, flavor, features(list)。
features每项含：level, name, en_name, description。

规则依据 R-SBC-001~008；
数据来源 topics/玩家手册2024/角色职业/<职业>/<子职业>.htm。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from aidm.data._subclasses_data import _SUBCLASSES_LIST


# ──────────────────────────────────────────────────────────────────────────
# 子职业数据结构
# ──────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SubclassFeature:
    """子职业的单个特性。

    规则: R-SBC-005 子职业特性等级
    出处: topics/玩家手册2024/角色职业/<职业>/<子职业>.htm
    """
    level: int
    name: str
    en_name: str
    description: str


@dataclass(frozen=True)
class Subclass:
    """单个子职业的完整数据。

    规则: R-SBC-001 子职业定义
    出处: topics/玩家手册2024/角色职业/<职业>/<子职业>.htm
    """
    name: str
    en_name: str
    class_name: str           # 所属职业
    flavor: str               # 一句标语
    features: tuple[SubclassFeature, ...]

    @classmethod
    def from_dict(cls, d: dict) -> "Subclass":
        features = tuple(
            SubclassFeature(
                level=f["level"],
                name=f["name"],
                en_name=f["en_name"],
                description=f["description"],
            )
            for f in d["features"]
        )
        return cls(
            name=d["name"],
            en_name=d["en_name"],
            class_name=d["class_name"],
            flavor=d["flavor"],
            features=features,
        )

    def get_features_at_level(self, level: int) -> list[SubclassFeature]:
        """获取该子职业在指定等级获得的所有特性。"""
        return [f for f in self.features if f.level == level]

    def get_feature(self, name: str) -> Optional[SubclassFeature]:
        """按中文名查找特性。"""
        for f in self.features:
            if f.name == name:
                return f
        return None

    @property
    def max_level(self) -> int:
        """子职业最高特性等级。"""
        return max((f.level for f in self.features), default=0)

    @property
    def feature_levels(self) -> list[int]:
        """子职业特性出现的所有等级（去重排序）。"""
        return sorted(set(f.level for f in self.features))


# ──────────────────────────────────────────────────────────────────────────
# 加载全部子职业数据
# ──────────────────────────────────────────────────────────────────────────

_SUBCLASSES: dict[str, Subclass] = {}
_CLASS_SUBCLASSES: dict[str, list[Subclass]] = {}

for _d in _SUBCLASSES_LIST:
    sc = Subclass.from_dict(_d)
    _SUBCLASSES[sc.name] = sc
    _CLASS_SUBCLASSES.setdefault(sc.class_name, []).append(sc)


# ──────────────────────────────────────────────────────────────────────────
# 查询接口
# ──────────────────────────────────────────────────────────────────────────

def get_subclass(name: str) -> Subclass:
    """按子职业名查找。

    参数:
        name: 子职业中文名，如 "预言师"、"狂战士道途"

    返回: Subclass 对象

    抛出: KeyError 若未找到
    """
    if name not in _SUBCLASSES:
        raise KeyError(f"未知子职业 {name!r}，可选: {sorted(_SUBCLASSES)}")
    return _SUBCLASSES[name]


def get_subclasses_by_class(class_name: str) -> list[Subclass]:
    """获取某职业的所有子职业。

    参数:
        class_name: 职业中文名，如 "法师"、"战士"

    返回: Subclass 列表
    """
    if class_name not in _CLASS_SUBCLASSES:
        raise KeyError(f"未知职业 {class_name!r}，可选: {sorted(_CLASS_SUBCLASSES)}")
    return list(_CLASS_SUBCLASSES[class_name])


def search_subclasses(keyword: str) -> list[Subclass]:
    """模糊搜索子职业（匹配名称、英文名、职业、特性名）。

    参数:
        keyword: 搜索关键词
    """
    results: list[Subclass] = []
    kw_lower = keyword.lower()
    for sc in _SUBCLASSES.values():
        score = 0
        if kw_lower in sc.name:
            score += 10
        if kw_lower in sc.en_name.lower():
            score += 8
        if kw_lower in sc.class_name:
            score += 3
        for feat in sc.features:
            if kw_lower in feat.name or kw_lower in feat.en_name.lower():
                score += 5
                break
        if score > 0:
            results.append((score, sc))
    results.sort(key=lambda x: x[0], reverse=True)
    return [sc for _, sc in results]


def all_subclasses() -> list[Subclass]:
    """返回全部子职业（按职业-名称排序）。"""
    return sorted(_SUBCLASSES.values(), key=lambda sc: (sc.class_name, sc.name))


def subclass_count() -> int:
    """返回子职业总数。"""
    return len(_SUBCLASSES)


# ──────────────────────────────────────────────────────────────────────────
# 子职业特性等级模式
#
# 规则: R-SBC-005 子职业特性等级
# 出处: 各职业 HTML 主文件
#
# 不同职业的子职业特性等级不同：
#   法师/吟游诗人/战士/游荡者: 3, 6, 10, 14
#   牧师: 3, 6, 17（另有领域法术在3/5/7/9级）
#   德鲁伊: 3, 6, 10, 14
#   武僧: 3, 6, 11, 17
#   圣武士: 3, 7, 15, 20
#   游侠: 3, 7, 11, 15
#   野蛮人: 3, 6, 10, 14
#   术士: 3, 6, 14, 18
#   魔契师: 3, 6, 10, 14
# ──────────────────────────────────────────────────────────────────────────

SUBCLASS_FEATURE_LEVELS: dict[str, list[int]] = {
    "法师": [3, 6, 10, 14],
    "吟游诗人": [3, 6, 14],
    "牧师": [3, 6, 17],
    "德鲁伊": [3, 6, 10, 14],
    "战士": [3, 7, 10, 15, 18],
    "武僧": [3, 6, 11, 17],
    "圣武士": [3, 7, 15, 20],
    "游侠": [3, 7, 11, 15],
    "游荡者": [3, 9, 13, 17],
    "野蛮人": [3, 6, 10, 14],
    "术士": [3, 6, 14, 18],
    "魔契师": [3, 6, 10, 14],
}


def get_subclass_feature_levels(class_name: str) -> list[int]:
    """获取某职业的子职业特性获得等级。

    参数:
        class_name: 职业名

    返回: 等级列表，如 [3, 6, 10, 14]
    """
    if class_name not in SUBCLASS_FEATURE_LEVELS:
        raise KeyError(f"未知职业 {class_name!r}")
    return list(SUBCLASS_FEATURE_LEVELS[class_name])


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 48个子职业
    assert subclass_count() == 48, f"应有48个子职业，实有{subclass_count()}"

    # 每个职业4个子职业
    for cls_name in ["法师", "战士", "牧师", "野蛮人", "吟游诗人", "德鲁伊",
                     "武僧", "圣武士", "游侠", "游荡者", "术士", "魔契师"]:
        subs = get_subclasses_by_class(cls_name)
        assert len(subs) == 4, f"{cls_name}应有4个子职业，实有{len(subs)}"

    # 预言师 Diviner
    div = get_subclass("预言师")
    assert div.class_name == "法师"
    assert div.en_name == "Diviner"
    assert len(div.features) >= 4  # 预兆、专业预言、天眼通、高等预兆
    assert any(f.name == "预兆" for f in div.features)
    assert any(f.name == "天眼通" for f in div.features)

    # 勇士 Champion
    champ = get_subclass("勇士")
    assert champ.class_name == "战士"
    assert any(f.name == "精通重击" for f in champ.features)

    # 按等级查询
    div_l3 = div.get_features_at_level(3)
    assert len(div_l3) >= 1  # 预言学者+预兆

    # 搜索
    results = search_subclasses("治疗")
    assert len(results) >= 1  # 生命领域等

    results2 = search_subclasses("diviner")
    assert len(results2) >= 1
    assert results2[0].name == "预言师"

    # 特性等级模式
    assert get_subclass_feature_levels("法师") == [3, 6, 10, 14]
    assert get_subclass_feature_levels("圣武士") == [3, 7, 15, 20]
    assert get_subclass_feature_levels("战士") == [3, 7, 10, 15, 18]

    print(f"[subclasses] 自检通过 ✓ ({subclass_count()} 个子职业, "
          f"{sum(len(sc.features) for sc in all_subclasses())} 个特性)")


if __name__ == "__main__":
    _self_test()
