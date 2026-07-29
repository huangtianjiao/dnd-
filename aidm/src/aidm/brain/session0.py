"""Session 0 配置逻辑 — 游戏前准备（基调/严肃度/边界/规则版本/升级方式/死亡处理）。

Session 0 是 DM 与玩家在正式开跑前的对齐会议，用于设定战役基调、
明确内容边界（Lines & Veils）、选择规则版本与升级方式等。
本模块提供配置数据结构、默认值与校验逻辑。

规则出处:
  - R-DM-041 奖励XP分配          topics/城主指南2024/2.运作游戏/角色升级.htm
  - R-DM-042 里程碑XP等级         topics/城主指南2024/2.运作游戏/角色升级.htm
  - R-DM-043 长休外升级HP         topics/城主指南2024/2.运作游戏/角色升级.htm
  - R-DM-044 通过训练获得等级(变体) topics/城主指南2024/2.运作游戏/角色升级.htm
  - R-DM-045 基于游戏回的升级速率  topics/城主指南2024/2.运作游戏/角色升级.htm
  - R-DM-046 团队规模预设          topics/城主指南2024/2.运作游戏/团队规模.htm

字段与 Campaign 模型(stats/models.py)的对应关系:
  config.tone        -> Campaign.tone
  config.seriousness -> Campaign.seriousness (需模型扩展)
  config.lines       -> Campaign.lines_json  (需模型扩展)
  config.veils       -> Campaign.veils_json  (需模型扩展)

注: 当前 Campaign 模型仅有 tone 字段；seriousness/lines_json/veils_json
    为 Session 0 所需的扩展字段，由调用方按需迁移模型。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


# ──────────────────────────────────────────────────────────────────────────
# 枚举常量
# ──────────────────────────────────────────────────────────────────────────

# 战役基调选项
TONES = [
    "黑暗写实",   # Dark/Gritty realism
    "高魔奇幻",   # High fantasy
    "政治阴谋",   # Political intrigue
    "恐怖风格",   # Horror
]

# 规则版本（仅列已实装版本：数据/引擎全部为 2024 修订版）
RULE_VERSIONS = [
    "2024 修订版",  # 2024 Revised edition
]

# 已知但未实装的版本：选择时给出明确“未实装”错误，而不是静默用 2024 数据冒充。
# 说明: 全部数据表（法术/怪物/职业/装备）均出自 topics/玩家手册2024 与
#       怪物图鉴2025；2014 PHB 数据未建库，选它会得到假 2024 结果，故禁用。
UNSUPPORTED_RULE_VERSIONS = [
    "2014 PHB",     # 原 Player's Handbook — 未实装
]

# 升级方式
ADVANCEMENT_MODES = [
    "经验值",       # XP-based advancement (R-DM-041)
    "里程碑",       # Milestone-based advancement (R-DM-042)
]

# 角色死亡处理：复活魔法获取难度
RESURRECTION_ACCESS = [
    "容易获取",   # 复活卷轴/牧师常见，死亡代价低
    "困难获取",   # 高环法术稀有，需任务获取
    "不可获取",   # 无复活魔法，死亡永久
]


# ──────────────────────────────────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class Session0Config:
    """Session 0 配置 — 游戏前对齐的所有可调参数。

    属性说明:
      tone: 战役基调，取值见 TONES
      seriousness: 严肃度滑块 1-10（1=纯搞笑随性, 10=严肃硬核剧情）
      lines: 禁止话题列表（Lines — 完全不出现的内容）
      veils: 纱幕话题列表（Veils — 可存在但不详细描写的内容）
      rule_version: 规则版本，取值见 RULE_VERSIONS
      advancement_mode: 升级方式，取值见 ADVANCEMENT_MODES
      resurrection_access: 复活魔法获取难度，取值见 RESURRECTION_ACCESS
      safewords: 安全词/暂停信号列表（如 "暂停"/"X卡"）
      party_size_min: 团队最小人数（R-DM-046 默认4）
      party_size_max: 团队最大人数（R-DM-046 默认6）
    """
    tone: str = "高魔奇幻"
    seriousness: int = 5
    lines: List[str] = field(default_factory=list)
    veils: List[str] = field(default_factory=list)
    rule_version: str = "2024 修订版"
    advancement_mode: str = "经验值"
    resurrection_access: str = "困难获取"
    safewords: List[str] = field(default_factory=lambda: ["暂停"])
    party_size_min: int = 4
    party_size_max: int = 6


# ──────────────────────────────────────────────────────────────────────────
# 默认配置
# ──────────────────────────────────────────────────────────────────────────

def default_session0() -> Session0Config:
    """返回 Session 0 默认配置。

    默认值依据:
      - 基调: 高魔奇幻（最通用入门基调）
      - 严肃度: 5（中性平衡）
      - Lines/Veils: 空（由 DM/玩家自行填写）
      - 规则版本: 2024 修订版（最新官方版本）
      - 升级方式: 经验值（R-DM-041 标准方式）
      - 复活魔法: 困难获取（平衡死亡代价与故事张力）
      - 安全词: ["暂停"]
      - 团队规模: 4-6 人（R-DM-046 团队规模预设）

    规则: R-DM-046  出处: topics/城主指南2024/2.运作游戏/团队规模.htm
    """
    return Session0Config()


# ──────────────────────────────────────────────────────────────────────────
# 校验逻辑
# ──────────────────────────────────────────────────────────────────────────

def validate_session0(config: Session0Config) -> List[str]:
    """校验 Session 0 配置合法性，返回错误信息列表（空列表表示通过）。

    校验项:
      1. tone 必须在 TONES 中
      2. seriousness 必须为 1-10 的整数
      3. rule_version 必须在 RULE_VERSIONS 中
      4. advancement_mode 必须在 ADVANCEMENT_MODES 中
      5. resurrection_access 必须在 RESURRECTION_ACCESS 中
      6. party_size_min/max 必须 >=1 且 min <= max
      7. lines/veils/safewords 必须为列表且元素为字符串

    规则: R-DM-046 (团队规模范围)  出处: topics/城主指南2024/2.运作游戏/团队规模.htm
    """
    errors: List[str] = []

    # 1. 基调
    if config.tone not in TONES:
        errors.append(f"tone '{config.tone}' 不合法，必须为 {TONES} 之一")

    # 2. 严肃度
    if not isinstance(config.seriousness, int):
        errors.append(f"seriousness 必须为整数，得到 {type(config.seriousness).__name__}")
    elif config.seriousness < 1 or config.seriousness > 10:
        errors.append(f"seriousness 必须为 1-10，得到 {config.seriousness}")

    # 3. 规则版本（2014 PHB 未实装 → 明确报错而非静默冒充）
    if config.rule_version in UNSUPPORTED_RULE_VERSIONS:
        errors.append(
            f"rule_version '{config.rule_version}' 未实装：当前规则数据全部为 2024 修订版"
            "（topics/玩家手册2024 + 怪物图鉴2025），2014 PHB 数据未建库。"
        )
    elif config.rule_version not in RULE_VERSIONS:
        errors.append(
            f"rule_version '{config.rule_version}' 不合法，必须为 {RULE_VERSIONS} 之一"
        )

    # 4. 升级方式
    if config.advancement_mode not in ADVANCEMENT_MODES:
        errors.append(
            f"advancement_mode '{config.advancement_mode}' 不合法，"
            f"必须为 {ADVANCEMENT_MODES} 之一"
        )

    # 5. 复活魔法获取难度
    if config.resurrection_access not in RESURRECTION_ACCESS:
        errors.append(
            f"resurrection_access '{config.resurrection_access}' 不合法，"
            f"必须为 {RESURRECTION_ACCESS} 之一"
        )

    # 6. 团队规模 (R-DM-046)
    if not isinstance(config.party_size_min, int) or config.party_size_min < 1:
        errors.append(
            f"party_size_min 必须 >=1 的整数，得到 {config.party_size_min}"
        )
    if not isinstance(config.party_size_max, int) or config.party_size_max < 1:
        errors.append(
            f"party_size_max 必须 >=1 的整数，得到 {config.party_size_max}"
        )
    if (
        isinstance(config.party_size_min, int)
        and isinstance(config.party_size_max, int)
        and config.party_size_min > config.party_size_max
    ):
        errors.append(
            f"party_size_min({config.party_size_min}) 不能大于 "
            f"party_size_max({config.party_size_max})"
        )

    # 7. 列表类型校验
    for name in ("lines", "veils", "safewords"):
        val = getattr(config, name)
        if not isinstance(val, list):
            errors.append(f"{name} 必须为列表，得到 {type(val).__name__}")
        else:
            for i, item in enumerate(val):
                if not isinstance(item, str):
                    errors.append(
                        f"{name}[{i}] 必须为字符串，得到 {type(item).__name__}"
                    )

    return errors


# ──────────────────────────────────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────────────────────────────────

def is_valid_config(config: Session0Config) -> bool:
    """快速判断配置是否合法（不返回具体错误）。"""
    return len(validate_session0(config)) == 0
