"""升级流程自动派生 — LevelUpPlan。

CHR-007: 升级流程依赖调用方传入新特性。
LevelUpPlan根据class_levels和Definition自动计算授予/选择；客户端只能提交合法选择。

规则依据: topics/玩家手册2024/角色创建/升级.htm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LevelUpStep:
    """升级步骤中的单个授予项。"""

    feature_id: str = ""          # 特性 canonical ID
    feature_name: str = ""
    source: str = "class"         # class/subclass/feat
    requires_choice: bool = False  # 是否需要玩家选择
    choice_options: List[str] = field(default_factory=list)
    auto_granted: bool = True     # 是否自动授予（无需选择）


@dataclass
class LevelUpPlan:
    """完整升级计划。

    CHR-007: 自动派生，客户端只能提交合法选择。
    """

    character_id: str = ""
    from_level: int = 1
    to_level: int = 2
    class_name: str = ""
    subclass_name: str = ""

    # HP 变化
    hit_die: int = 8              # d6/d8/d10/d12
    hp_gain_roll: int = 0        # 掷骰结果（0=取平均）
    hp_gain_avg: int = 5         # 平均值
    con_modifier: int = 0
    hp_gain_total: int = 0       # 最终 HP 增量

    # 特性授予
    new_features: List[LevelUpStep] = field(default_factory=list)

    # 能力值提升
    asi_available: bool = False   # 是否有属性提升机会
    asi_points: int = 0           # 可分配点数

    # 专长选择
    feat_available: bool = False
    feat_choices: List[str] = field(default_factory=list)

    # 法术位变化
    spell_slots_before: Dict[int, int] = field(default_factory=dict)
    spell_slots_after: Dict[int, int] = field(default_factory=dict)

    # 新法术
    new_spells: List[str] = field(default_factory=list)

    def compute_hp_gain(self) -> int:
        """计算 HP 增量。"""
        roll = self.hp_gain_roll if self.hp_gain_roll > 0 else self.hp_gain_avg
        self.hp_gain_total = roll + self.con_modifier
        return max(1, self.hp_gain_total)

    def validate_feat_selection(self, selected_feat: str) -> bool:
        """验证专长选择是否合法。"""
        if not self.feat_available:
            return False
        return selected_feat in self.feat_choices

    def to_dict(self) -> dict:
        """序列化为字典。"""
        return {
            "character_id": self.character_id,
            "from_level": self.from_level,
            "to_level": self.to_level,
            "class_name": self.class_name,
            "subclass_name": self.subclass_name,
            "hp_gain": self.compute_hp_gain(),
            "new_features": [
                {
                    "id": f.feature_id,
                    "name": f.feature_name,
                    "source": f.source,
                    "requires_choice": f.requires_choice,
                    "auto_granted": f.auto_granted,
                }
                for f in self.new_features
            ],
            "asi_available": self.asi_available,
            "asi_points": self.asi_points,
            "feat_available": self.feat_available,
            "spell_slots_before": dict(self.spell_slots_before),
            "spell_slots_after": dict(self.spell_slots_after),
            "new_spells": list(self.new_spells),
        }
