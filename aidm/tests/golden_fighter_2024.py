"""Fighter 2024 golden snapshots（改造方案 §7.1 / §13.5 / 第21节任务7）。

用途:
  以 data/classes.py「战士」1-20 progression 为当前事实基线，定义关键等级
  1/4/5/6/9/11/14/20 的结构快照（features/HP/PB/资源/ASI 节点/精通/施法）。
  本轮是「设计契约」——先固定结构供 P4 canonical progression 重建时对齐；
  重建后测试升级为逐字段断言（见 test_baseline_v1.py::TestFighterGoldenSnapshots）。

  快照来源:
    - data/classes.CLASS_FEATURES["战士"] — 2024 结构 progression
    - build.derive_stats — HP/PB 服务器权威推导
    - PHB2024 战士: 生命骰 d10；1级满骰+体质；升级平均6+体质
    - 武器精通 1 级（职业特性表）
    - 战斗风格/回气 1 级；动作如潮 2 级（17 级两次）；战术思维 2 级
    - 额外攻击 5/11/20 级；战术转进 5 级；战术主宰 9 级
    - 不屈 9 级起（13 级两次、17 级三次）— 2024 RAW
    - ASI/专长节点: 全局 4/8/12/16/19 + 战士额外 6/14（方案 §8.2）

  规则依据: 改造方案 §7.2 Fighter 垂直样板 + §8.2 FeatEntitlementService
"""

from __future__ import annotations

# 快照采样的关键等级（方案第21节任务7）
FIGHTER_KEY_LEVELS: tuple[int, ...] = (1, 4, 5, 6, 9, 11, 14, 20)

# 与 data/classes.CLASS_FEATURES["战士"] 一致的 1-20 progression（事实基线）
FIGHTER_PROGRESSION: dict[int, list[str]] = {
    1: ["战斗风格", "回气", "武器精通"],
    2: ["动作如潮（一次）", "战术思维"],
    3: ["战士子职"],
    4: ["属性值提升"],
    5: ["额外攻击", "战术转进"],
    6: ["属性值提升"],
    7: ["子职特性"],
    8: ["属性值提升"],
    9: ["不屈（一次）", "战术主宰"],
    10: ["子职特性"],
    11: ["额外攻击（二）"],
    12: ["属性值提升"],
    13: ["不屈（两次）", "究明攻击"],
    14: ["属性值提升"],
    15: ["子职特性"],
    16: ["属性值提升"],
    17: ["动作如潮（两次）", "不屈（三次）"],
    18: ["子职特性"],
    19: ["传奇恩惠"],
    20: ["额外攻击（三）"],
}

# 2024 RAW 期望值（设计基线；当前实现对齐情况见 KNOWN_GAPS）
FIGHTER_GOLDEN: dict[int, dict] = {
    1: {
        "features": ["战斗风格", "回气", "武器精通"],
        "hp_first_level": "10 + CON_MOD",      # 满骰 d10
        "hit_die": 10,
        "proficiency_bonus": 2,
        "extra_attacks": 1,                    # 攻击动作次数
        "action_surge_uses": 1,                # 2 级起，每短休一次
        "indomitable_uses": 0,                 # 2024: 9 级才获得
        "feat_asi_nodes": [],                  # 1 级无 ASI（起源专长由背景给）
        "weapon_mastery": True,
        "subclass_entry_level": 3,
        "spellcasting": None,
        "resources": ["second_wind", "action_surge"],
    },
    4: {
        "features": ["属性值提升"],
        "proficiency_bonus": 2,
        "extra_attacks": 1,
        "action_surge_uses": 1,
        "indomitable_uses": 0,
        "feat_asi_nodes": ["ASI_OR_FEAT_4"],
        "weapon_mastery": True,
        "spellcasting": None,
        "resources": ["second_wind", "action_surge"],
    },
    5: {
        "features": ["额外攻击", "战术转进"],
        "proficiency_bonus": 3,
        "extra_attacks": 2,
        "action_surge_uses": 1,
        "indomitable_uses": 0,
        "feat_asi_nodes": [],
        "weapon_mastery": True,
        "spellcasting": None,
        "resources": ["second_wind", "action_surge"],
    },
    6: {
        "features": ["属性值提升"],
        "proficiency_bonus": 3,
        "extra_attacks": 2,
        "action_surge_uses": 1,
        "indomitable_uses": 0,
        "feat_asi_nodes": ["ASI_OR_FEAT_6"],   # 战士额外节点（方案 §8.2）
        "weapon_mastery": True,
        "spellcasting": None,
    },
    9: {
        "features": ["不屈（一次）", "战术主宰"],
        "proficiency_bonus": 4,
        "extra_attacks": 2,
        "action_surge_uses": 1,
        "indomitable_uses": 1,                 # 2024: 9 级获得
        "feat_asi_nodes": [],
        "weapon_mastery": True,
        "spellcasting": None,
        "resources": ["second_wind", "action_surge", "indomitable"],
    },
    11: {
        "features": ["额外攻击（二）"],
        "proficiency_bonus": 4,
        "extra_attacks": 3,
        "action_surge_uses": 1,
        "indomitable_uses": 1,
        "feat_asi_nodes": [],
        "weapon_mastery": True,
        "spellcasting": None,
    },
    14: {
        "features": ["属性值提升"],
        "proficiency_bonus": 5,
        "extra_attacks": 3,
        "action_surge_uses": 1,
        "indomitable_uses": 2,                 # 13 级起两次
        "feat_asi_nodes": ["ASI_OR_FEAT_14"],  # 战士额外节点（方案 §8.2）
        "weapon_mastery": True,
        "spellcasting": None,
    },
    20: {
        "features": ["额外攻击（三）"],
        "proficiency_bonus": 6,
        "extra_attacks": 4,
        "action_surge_uses": 2,                # 17 级起两次
        "indomitable_uses": 3,                 # 17 级起三次
        "feat_asi_nodes": ["EPIC_BOON_19"],
        "weapon_mastery": True,
        "spellcasting": None,
        "resources": ["second_wind", "action_surge", "indomitable"],
    },
}

# Fighter ASI/专长 entitlement 节点（全局 4/8/12/16/19 + 战士额外 6/14）
FIGHTER_FEAT_ASI_LEVELS: tuple[int, ...] = (4, 6, 8, 12, 14, 16, 19)

# 当前实现与 2024 设计基线的已知差距。
# GAP-FGT-001（不屈 5 级）于 P4 关闭、GAP-FGT-002（全局 FEAT_LEVELS
# 缺战士 6/14 节点）于 P5 关闭——关闭后必须从清单移除。
KNOWN_GAPS: tuple[dict, ...] = ()
