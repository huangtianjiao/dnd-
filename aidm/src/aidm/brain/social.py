"""社交流程 — DM 扮演 NPC / 玩家角色扮演回应 / 判断掷骰 / 态度转换。

依据 DMG「运作游戏/运作交涉」(R-CON-012 NPC态度层级, R-DM-047 NPC态度分类)
与 PHB 术语汇编「态度」(R-GLS-017 态度对影响检定的优劣势——友好→优势/敌对→劣势，
出处: topics/玩家手册2024/术语汇编/态度.txt)，以及报告§7社交互动循环。

【规则书 vs 设计决策】（详见 _SOCIAL_DC_MODIFIER / ATTITUDE_THRESHOLDS 处注释）
  - 三种态度（友好/冷漠/敌对）：规则书原文（运作交涉/态度.txt + 术语汇编/态度.txt）
  - 态度对影响检定的优劣势（友好→优势、敌对→劣势）：规则书原文（术语汇编/态度.txt）
  - 态度 DC ±5 修正：⚠ 设计决策（项目报告§7，非规则书）；规则书用 adv/disadv 而非 ±5
  - 态度转换阈值 10/5/15/10：⚠ 设计决策（项目报告§7，非规则书）；规则书仅定性可改变

  1. DM 扮演 NPC（以 NPC 的口吻说话，描述表情/姿态/语气；NPC 有自己的目标、
     态度和知识——DM 扮演他们就像扮演另一个角色）
  2. 玩家角色扮演回应（玩家以自己角色的口吻回应，描述意图和方法，
     而不是说"我掷说服"。好的说法："我走近守卫，压低声音说：
     '如果你放我们进去，没人需要知道你见过我们。'"不好的说法："我掷说服。"）
  3. DM 判断是否需要掷骰（DM 评估：NPC 是否可能被说服/欺骗/恐吓？
     → 如果角色扮演足够好，可能自动成功；结果是否不确定？→ 需要掷骰；
     NPC 的态度（友善/中立/敌对）影响 DC）
  4. 掷骰与解决（玩家掷相应技能检定：说服(魅力)/欺瞒(魅力)/威吓(魅力)/
     表演(魅力)/洞悉(感知)。DM 秘密设定 DC，比较结果，叙述 NPC 反应）

关键规则（指南Ch6 callout）：
  - 说服不是精神控制：说服检定成功不会让 NPC 做完全不合理的事
  - 不能用说服让酒馆老板免费让你住3个月——这不叫说服，这叫妄想
  - DC 30 的任务几乎是"不可能"级别的
  - 如果 NPC 根本不可能同意，DM 应该直接说"不，这不可能"，不需要掷骰

标注约定：每条规则实现处标注 RULE_SPEC.md 规则点 ID + 原文出处路径
（topics/.../xxx.htm），形成"代码↔规则"双向索引。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..engine import check as check_engine
from . import llm

# ──────────────────────────────────────────────────────────────────────────
# 常量与枚举
# ──────────────────────────────────────────────────────────────────────────

# NPC 三种态度（R-CON-012 / R-DM-047）
# 出处: topics/城主指南2024/2.运作游戏/运作交涉/态度.htm
ATTITUDE_FRIENDLY = "friendly"        # 友好：乐于提供帮助
ATTITUDE_INDIFFERENT = "indifferent"  # 冷漠：中立态度，需要说服才会配合
ATTITUDE_HOSTILE = "hostile"          # 敌对：会试图妨碍、攻击或拒绝合作

ALL_ATTITUDES = (ATTITUDE_FRIENDLY, ATTITUDE_INDIFFERENT, ATTITUDE_HOSTILE)

# ──────────────────────────────────────────────────────────────────────────
# 社交系统 Policy 配置（EXP-001）
# ──────────────────────────────────────────────────────────────────────────

class SocialPolicy(str, Enum):
    """社交系统规则策略。

    规则: EXP-001 社交态度RAW Policy
    出处: topics/城主指南2024/2.运作游戏/运作交涉/态度.htm
    """
    CUSTOM = "custom"              # 自定义规则（项目报告§7，DC±5 + 阈值）
    RULE_2024_RAW = "2024_raw"     # 2024 RAW（优势/劣势机制）


# 全局默认 policy
SOCIAL_POLICY_CONFIG: dict[str, Any] = {"social_system": "custom"}


def set_social_policy(policy: str) -> None:
    """设置社交系统策略。"""
    if policy not in (SocialPolicy.CUSTOM, SocialPolicy.RULE_2024_RAW):
        raise ValueError(f"未知社交策略 {policy!r}，可选: {[p.value for p in SocialPolicy]}")
    SOCIAL_POLICY_CONFIG["social_system"] = policy


def get_social_policy() -> str:
    """获取当前社交系统策略。"""
    return SOCIAL_POLICY_CONFIG["social_system"]


# 2024 RAW 态度效果（优势/劣势而非 DC ±5）
# 规则出处: topics/玩家手册2024/术语汇编/态度.txt
_2024_RAW_ATTITUDE_EFFECTS: dict[str, str] = {
    ATTITUDE_FRIENDLY: "advantage",      # 友好 → 优势
    ATTITUDE_INDIFFERENT: "none",         # 冷漠 → 无
    ATTITUDE_HOSTILE: "disadvantage",     # 敌对 → 劣势
}

# 2024 RAW 态度转换阈值（基于成功/失败次数，与 custom 相同结构但数值可不同）
# 规则出处: topics/城主指南2024/2.运作游戏/运作交涉/态度.htm
# 2024 RAW 未给出具体数值阈值，此处采用与 custom 相同的默认值
_2024_RAW_ATTITUDE_THRESHOLDS: dict[tuple[str, str], int] = {
    ("friendly", "degrade"): 10,
    ("indifferent", "degrade"): 5,
    ("hostile", "improve"): 15,
    ("indifferent", "improve"): 10,
}

# 社交 DC 修正表 —— 【设计决策，非规则书原文】
# ⚠ 规则书原文（术语汇编/态度.txt）对态度的影响采用 *优势/劣势* 机制，而非 DC ±5：
#     友好 Friendly  → 影响该生物的属性检定具有 *优势*
#     敌对 Hostile   → 影响该生物的属性检定具有 *劣势*
#     冷漠 Indifferent → 无优劣势
#   即规则出处: topics/玩家手册2024/术语汇编/态度.txt（参见"友好""敌对""冷漠"词条）。
#
# 本模块采用 *DC ±5 修正* 作为该优势/劣势机制的数值近似（出处: 项目报告§7，
# 非规则书）。这与规则书的 adv/disadv 并不等价（±5 ≈ ±5 成功率，而 adv/disadv
# 的期望偏移随 DC 变化）。理想做法是在 check_engine.ability_check 中按态度传入
# advantage/disadvantage 而非调整 DC；当前实现保留 ±5 作为简化设计决策。
# 规则点引用 R-GLS-017 为项目自拟，规则书无对应编号。
_SOCIAL_DC_MODIFIER = {
    ATTITUDE_FRIENDLY: -5,
    ATTITUDE_INDIFFERENT: 0,
    ATTITUDE_HOSTILE: +5,
}

# 态度转换阈值 —— 【设计决策，非规则书原文】
# ⚠ 规则书原文（运作交涉/态度.txt）仅定性说明"角色可以通过言行改变生物的态度"
#   （例：为冷漠的矿工买饮料可能使其变为友好），并要求 DM 在态度变化时向玩家描述，
#   但 *未给出* 任何连续成功/失败次数阈值。下表的 10/5/15/10 阈值为项目自拟调参
#   （出处: 项目报告§7，非规则书），仅用于量化态度转换节奏。
# 规则: R-DM-047 NPC态度分类（态度可由言行改变——定性，无具体次数）
# 出处: topics/城主指南2024/2.运作游戏/运作交涉/态度.txt
ATTITUDE_THRESHOLDS = {
    # (当前态度, 方向) → 所需连续次数（设计决策，见上方说明）
    ("friendly", "degrade"): 10,      # 友好→冷漠
    ("indifferent", "degrade"): 5,    # 冷漠→敌对
    ("hostile", "improve"): 15,       # 敌对→冷漠
    ("indifferent", "improve"): 10,   # 冷漠→友好
}

# 社交技能映射（报告§7第4步）
# 技能名 → (属性, 中文说明)
SOCIAL_SKILLS = {
    "persuasion": ("cha", "说服(魅力)——真诚影响他人态度"),
    "deception": ("cha", "欺瞒(魅力)——说谎或误导"),
    "intimidation": ("cha", "威吓(魅力)——用威胁迫使合作"),
    "performance": ("cha", "表演(魅力)——娱乐或伪装"),
    "insight": ("wis", "洞悉(感知)——判断NPC是否说谎"),
}


# ──────────────────────────────────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class NPC:
    """NPC 数据结构 — DM 扮演的角色卡。

    规则: R-CON-012 NPC态度层级 / R-DM-047 NPC态度分类
    出处: topics/城主指南2024/2.运作游戏/运作交涉/态度.htm

    属性:
      name: NPC 名称
      role: NPC 职业身份（如"酒馆老板""守卫队长"）
      attitude: 当前态度 friendly|indifferent|hostile
      knowledge: NPC 所知信息列表（可被揭示的秘密/线索）
      goals: NPC 自身目标列表（DM 扮演依据）
      secrets: NPC 隐藏秘密列表（需高 DC 或特定触发才揭示）
      cr: 挑战等级（用于熟练加值计算，默认0=平民）
    """
    name: str
    role: str = ""
    attitude: str = ATTITUDE_INDIFFERENT
    knowledge: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)
    secrets: list[str] = field(default_factory=list)
    cr: float = 0

    def __post_init__(self) -> None:
        if self.attitude not in ALL_ATTITUDES:
            raise ValueError(
                f"attitude 必须为 {ALL_ATTITUDES} 之一，得到 {self.attitude!r}"
            )


@dataclass
class SocialState:
    """社交互动状态 — 贯穿一次完整对话的累积状态。

    规则: R-CON-012 / R-DM-047（态度跟踪与转换）
    出处: topics/城主指南2024/2.运作游戏/运作交涉/态度.htm

    属性:
      current_npc: 当前交互的 NPC
      conversation_history: 对话历史 [{speaker, text, round}]
      attitude_changes: 态度变更记录 [{from, to, round, reason}]
      revealed_secrets: 已揭示的秘密列表
      persuasion_dc: 当前说服 DC（由态度修正动态计算）
      consecutive_successes: 连续成功次数（用于态度提升）
      consecutive_failures: 连续失败次数（用于态度降级）
      round: 当前对话轮次
    """
    current_npc: NPC | None = None
    conversation_history: list[dict] = field(default_factory=list)
    attitude_changes: list[dict] = field(default_factory=list)
    revealed_secrets: list[str] = field(default_factory=list)
    persuasion_dc: int = 15
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    round: int = 0


# ──────────────────────────────────────────────────────────────────────────
# 核心函数
# ──────────────────────────────────────────────────────────────────────────

def check_social_dc(npc_attitude: str) -> int:
    """计算社交 DC 修正值（按 NPC 态度与当前策略）。

    规则: EXP-001 社交态度RAW Policy
    出处: topics/城主指南2024/2.运作游戏/运作交涉/态度.htm
          topics/玩家手册2024/术语汇编/态度.txt

    当 policy="custom" 时返回 DC ±5 修正（项目报告§7）。
    当 policy="2024_raw" 时返回 0（RAW 用优势/劣势而非 DC 修正）。

    Args:
        npc_attitude: NPC 当前态度 friendly|indifferent|hostile

    Returns:
        DC 修正值（整数，加到基础 DC 上）

    Raises:
        ValueError: 态度不在合法取值范围内
    """
    if npc_attitude not in _SOCIAL_DC_MODIFIER:
        raise ValueError(
            f"npc_attitude 必须为 {list(_SOCIAL_DC_MODIFIER)} 之一，"
            f"得到 {npc_attitude!r}"
        )
    # 2024 RAW 策略: 用优势/劣势而非 DC 修正，返回 0
    if get_social_policy() == SocialPolicy.RULE_2024_RAW:
        return 0
    return _SOCIAL_DC_MODIFIER[npc_attitude]


def get_attitude_effect(npc_attitude: str) -> str:
    """获取态度对检定的影响（按当前策略）。

    规则: EXP-001 社交态度RAW Policy
    出处: topics/玩家手册2024/术语汇编/态度.txt

    Returns:
        "advantage" / "disadvantage" / "none"
    """
    if get_social_policy() == SocialPolicy.RULE_2024_RAW:
        return _2024_RAW_ATTITUDE_EFFECTS.get(npc_attitude, "none")
    # custom 策略: 映射 DC 修正到 adv/disadv
    mod = _SOCIAL_DC_MODIFIER.get(npc_attitude, 0)
    if mod < 0:
        return "advantage"
    elif mod > 0:
        return "disadvantage"
    return "none"


def update_attitude(npc: NPC, success_count: int, failure_count: int) -> str | None:
    """根据连续成功/失败次数更新 NPC 态度。

    【设计决策，非规则书原文】
    规则书（运作交涉/态度.txt）仅定性说明态度可由言行改变（无具体次数阈值）。
    下述 10/5/15/10 阈值为项目自拟调参（报告§7，非规则书）：
      friendly → indifferent : 连续失败 10 次
      indifferent → hostile  : 连续失败  5 次
      hostile → indifferent  : 连续成功 15 次
      indifferent → friendly : 连续成功 10 次

    规则: R-DM-047 NPC态度分类（态度可由言行改变——定性，无具体次数）
    出处: topics/城主指南2024/2.运作游戏/运作交涉/态度.txt

    当态度发生转换时，直接修改 npc.attitude 并返回新态度字符串；
    若无转换发生，返回 None。

    Args:
        npc: 要更新的 NPC 对象
        success_count: 当前连续成功次数
        failure_count: 当前连续失败次数

    Returns:
        新态度字符串（若发生转换），否则 None
    """
    cur = npc.attitude

    # 检查降级路径（连续失败触发）
    degrade_threshold = ATTITUDE_THRESHOLDS.get((cur, "degrade"))
    if degrade_threshold is not None and failure_count >= degrade_threshold:
        if cur == ATTITUDE_FRIENDLY:
            npc.attitude = ATTITUDE_INDIFFERENT
        elif cur == ATTITUDE_INDIFFERENT:
            npc.attitude = ATTITUDE_HOSTILE
        return npc.attitude

    # 检查提升路径（连续成功触发）
    improve_threshold = ATTITUDE_THRESHOLDS.get((cur, "improve"))
    if improve_threshold is not None and success_count >= improve_threshold:
        if cur == ATTITUDE_HOSTILE:
            npc.attitude = ATTITUDE_INDIFFERENT
        elif cur == ATTITUDE_INDIFFERENT:
            npc.attitude = ATTITUDE_FRIENDLY
        return npc.attitude

    return None


def social_interaction(party: list, npc: NPC, player_input: str,
                       conversation_history: list[dict]) -> dict:
    """执行一次完整的社交互动循环。

    流程（报告§7）：
      1. DM 扮演 NPC（LLM 据 NPC 态度/目标/知识生成口吻化回应）
      2. 玩家角色扮演回应（player_input，应描述意图和方法而非"我掷说服"）
      3. DM 判断是否需要掷骰（角色扮演足够好→自动成功；不确定→掷骰；
         NPC 根本不可能同意→直接拒绝不掷骰）
      4. 掷骰与解决（说服/欺瞒/威吓/表演=魅力；洞悉=感知；
         DC = 基础DC + 态度修正，DM 秘密设定）

    规则: R-CON-012 NPC态度层级 / R-DM-047 NPC态度分类 /
          R-GLS-017 态度对影响检定的优劣势
    出处: topics/城主指南2024/2.运作游戏/运作交涉/态度.htm
          topics/城主指南2024/2.运作游戏/运作交涉/角色扮演.htm
          topics/城主指南2024/2.运作游戏/运作交涉/运作交涉.htm

    关键规则（指南Ch6 callout）：
      - 说服不是精神控制：说服检定成功不会让 NPC 做完全不合理的事
      - 不能用说服让酒馆老板免费让你住3个月——这不叫说服，这叫妄想
      - DC 30 的任务几乎是"不可能"级别的
      - 如果 NPC 根本不可能同意，DM 应该直接说"不，这不可能"，不需要掷骰

    Args:
        party: 冒险者角色列表（Character 对象）
        npc: 当前交互的 NPC 对象
        player_input: 玩家的角色扮演回应文本
        conversation_history: 此前的对话历史 [{speaker, text, round}]

    Returns:
        dict 包含:
          - npc_response: DM 扮演 NPC 的回应文本
          - dice_result: 掷骰结果（若进行了检定）
          - attitude_changed: 是否发生了态度转换
          - new_attitude: 转换后的新态度（若无转换则为原态度）
          - revealed_secret: 本次揭示的秘密（若有）
          - conversation_history: 更新后的对话历史
          - social_state: 更新后的 SocialState 快照
    """
    # 取主角（party 第一个角色）作为社交主体
    protagonist = party[0] if party else None

    # 构建 DM 扮演 NPC 的 LLM 提示
    # NPC 有自己的目标、态度和知识——DM 扮演他们就像扮演另一个角色
    system_prompt = (
        "你是D&D 5E的DM，正在扮演一个NPC进行社交互动。\n"
        "依据NPC的态度、目标和知识，以NPC的口吻回应玩家。\n"
        "NPC态度影响回应方式：\n"
        "- 友好(friendly)：乐于帮助，主动提供信息和资源\n"
        "- 冷漠(indifferent)：中立态度，需要说服才会配合\n"
        "- 敌对(hostile)：会试图妨碍、攻击或拒绝合作\n\n"
        "输出JSON格式：\n"
        '{"npc_response":"NPC的回应(含表情/姿态/语气描述)",'
        '"needs_roll":true/false,'  # DM判断是否需要掷骰
        '"skill":"persuasion|deception|intimidation|performance|insight",'
        '"base_dc":15,'  # DM秘密设定的基础DC
        '"auto_success":false,'  # 角色扮演足够好时自动成功
        '"impossible":false,'  # NPC根本不可能同意时直接拒绝
        '"reveal_secret":""}'  # 本次可揭示的秘密(空字符串表示无)
    )

    # 构建用户消息：NPC信息 + 玩家输入 + 对话历史
    npc_info = (
        f"NPC名称: {npc.name}\n"
        f"NPC身份: {npc.role}\n"
        f"NPC态度: {npc.attitude}\n"
        f"NPC目标: {', '.join(npc.goals) if npc.goals else '无明确目标'}\n"
        f"NPC所知: {', '.join(npc.knowledge) if npc.knowledge else '无特殊信息'}\n"
        f"NPC秘密: {', '.join(npc.secrets) if npc.secrets else '无'}\n"
    )

    history_text = "\n".join(
        f"[轮{h.get('round', 0)}] {h.get('speaker', '?')}: {h.get('text', '')}"
        for h in conversation_history[-5:]  # 最近5轮防止上下文过长
    ) or "(无历史对话)"

    user_message = (
        f"=== NPC信息 ===\n{npc_info}\n"
        f"=== 对话历史 ===\n{history_text}\n"
        f"=== 玩家本次回应 ===\n{player_input}\n\n"
        f"请以NPC口吻回应，并判断是否需要掷骰。"
    )

    # LLM 生成 NPC 回应与判定参数
    raw_response = llm.chat(system_prompt, user_message, temperature=0.5)
    import json
    response_data = {}
    # 尝试提取 JSON
    cleaned = raw_response.replace("```json", "").replace("```", "").strip()
    try:
        response_data = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        # JSON 解析失败，使用原始文本作为 NPC 回应
        response_data = {"npc_response": raw_response, "needs_roll": False}

    npc_response = response_data.get("npc_response", "")
    needs_roll = response_data.get("needs_roll", False)
    skill = response_data.get("skill", "persuasion")
    base_dc = int(response_data.get("base_dc", 15))
    auto_success = response_data.get("auto_success", False)
    impossible = response_data.get("impossible", False)
    reveal_secret = response_data.get("reveal_secret", "")

    # 初始化社交状态
    social_state = SocialState(current_npc=npc)
    social_state.persuasion_dc = base_dc + check_social_dc(npc.attitude)

    dice_result = None
    attitude_changed = False
    new_attitude = npc.attitude

    # 处理"不可能"情况：NPC 根本不可能同意，DM 直接拒绝，不掷骰
    # 关键规则（指南Ch6 callout）：如果NPC根本不可能同意，
    # DM应该直接说"不，这不可能"，不需要掷骰
    if impossible:
        # 不掷骰，直接拒绝；不计入连续失败（因为根本没尝试）
        pass
    # 处理自动成功：角色扮演足够好，可能自动成功
    elif auto_success:
        social_state.consecutive_successes += 1
        social_state.consecutive_failures = 0
        dice_result = {"auto_success": True, "skill": skill}
    # 需要掷骰的情况
    elif needs_roll and protagonist is not None:
        # 确定技能属性
        skill_info = SOCIAL_SKILLS.get(skill, ("cha", "说服(魅力)"))
        ability = skill_info[0]

        # 计算检定加值
        ability_mod = protagonist.ability_mod(ability)
        prof_bonus = protagonist.prof()

        # 判断是否熟练（简化：魅力技能默认熟练，感知技能看洞察）
        proficient = True  # 简化处理，实际应由角色卡决定

        # 执行属性检定
        # DC = 基础DC + 态度修正（已在 social_state.persuasion_dc 中计算）
        check_result = check_engine.ability_check(
            mod=ability_mod,
            prof=prof_bonus,
            proficient=proficient,
            dc=social_state.persuasion_dc,
        )

        dice_result = {
            "skill": skill,
            "ability": ability,
            "d20": check_result.d20,
            "total": check_result.total,
            "dc": social_state.persuasion_dc,
            "success": check_result.success,
            "margin": check_result.margin,
        }

        # 更新连续成功/失败计数
        if check_result.success:
            social_state.consecutive_successes += 1
            social_state.consecutive_failures = 0
        else:
            social_state.consecutive_failures += 1
            social_state.consecutive_successes = 0

        # 检查态度转换
        old_attitude = npc.attitude
        changed = update_attitude(
            npc,
            social_state.consecutive_successes,
            social_state.consecutive_failures,
        )
        if changed is not None:
            attitude_changed = True
            new_attitude = changed
            social_state.attitude_changes.append({
                "from": old_attitude,
                "to": new_attitude,
                "round": social_state.round,
                "reason": f"连续{'成功' if social_state.consecutive_successes > 0 else '失败'}"
                          f"达阈值",
            })

    # 处理秘密揭示
    if reveal_secret and reveal_secret not in social_state.revealed_secrets:
        social_state.revealed_secrets.append(reveal_secret)

    # 更新对话历史
    updated_history = list(conversation_history)
    updated_history.append({
        "speaker": "player",
        "text": player_input,
        "round": social_state.round,
    })
    updated_history.append({
        "speaker": f"npc:{npc.name}",
        "text": npc_response,
        "round": social_state.round,
    })
    social_state.conversation_history = updated_history
    social_state.round += 1

    return {
        "npc_response": npc_response,
        "dice_result": dice_result,
        "attitude_changed": attitude_changed,
        "new_attitude": new_attitude,
        "revealed_secret": reveal_secret if reveal_secret else None,
        "conversation_history": updated_history,
        "social_state": {
            "persuasion_dc": social_state.persuasion_dc,
            "consecutive_successes": social_state.consecutive_successes,
            "consecutive_failures": social_state.consecutive_failures,
            "round": social_state.round,
            "revealed_secrets": social_state.revealed_secrets,
            "attitude_changes": social_state.attitude_changes,
        },
    }


# ──────────────────────────────────────────────────────────────────────────
# 自检测试
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    """social.py 自检测试。"""

    # === 测试 1: NPC 数据结构 ===
    npc = NPC(name="酒馆老板鲍勃", role="酒馆老板",
              attitude=ATTITUDE_INDIFFERENT,
              knowledge=["镇上有奇怪的地下活动"],
              goals=["维持生意", "避免惹麻烦"])
    assert npc.name == "酒馆老板鲍勃"
    assert npc.attitude == ATTITUDE_INDIFFERENT
    assert len(npc.knowledge) == 1
    print("[test1] NPC数据结构 ✓")

    # === 测试 2: NPC 态度校验 ===
    try:
        NPC(name="测试", attitude="invalid_attitude")
        assert False, "应该抛出 ValueError"
    except ValueError:
        pass
    print("[test2] NPC态度校验 ✓")

    # === 测试 3: check_social_dc 态度修正 ===
    # 社交 DC 修正表（报告§7）：友好-5 / 冷漠0 / 敌对+5
    assert check_social_dc(ATTITUDE_FRIENDLY) == -5
    assert check_social_dc(ATTITUDE_INDIFFERENT) == 0
    assert check_social_dc(ATTITUDE_HOSTILE) == +5
    print("[test3] check_social_dc 态度修正 ✓")

    # === 测试 4: check_social_dc 非法态度 ===
    try:
        check_social_dc("invalid")
        assert False, "应该抛出 ValueError"
    except ValueError:
        pass
    print("[test4] check_social_dc 非法态度校验 ✓")

    # === 测试 5: update_attitude 友好→冷漠（连续失败10次）===
    npc_friendly = NPC(name="友好的商人", attitude=ATTITUDE_FRIENDLY)
    result = update_attitude(npc_friendly, success_count=0, failure_count=10)
    assert result == ATTITUDE_INDIFFERENT, f"期望 indifferent，得到 {result}"
    assert npc_friendly.attitude == ATTITUDE_INDIFFERENT
    print("[test5] update_attitude friendly→indifferent ✓")

    # === 测试 6: update_attitude 冷漠→敌对（连续失败5次）===
    npc_indifferent = NPC(name="冷漠的守卫", attitude=ATTITUDE_INDIFFERENT)
    result = update_attitude(npc_indifferent, success_count=0, failure_count=5)
    assert result == ATTITUDE_HOSTILE, f"期望 hostile，得到 {result}"
    assert npc_indifferent.attitude == ATTITUDE_HOSTILE
    print("[test6] update_attitude indifferent→hostile ✓")

    # === 测试 7: update_attitude 敌对→冷漠（连续成功15次）===
    npc_hostile = NPC(name="敌对的兽人", attitude=ATTITUDE_HOSTILE)
    result = update_attitude(npc_hostile, success_count=15, failure_count=0)
    assert result == ATTITUDE_INDIFFERENT, f"期望 indifferent，得到 {result}"
    assert npc_hostile.attitude == ATTITUDE_INDIFFERENT
    print("[test7] update_attitude hostile→indifferent ✓")

    # === 测试 8: update_attitude 冷漠→友好（连续成功10次）===
    npc_neutral = NPC(name="中立的镇长", attitude=ATTITUDE_INDIFFERENT)
    result = update_attitude(npc_neutral, success_count=10, failure_count=0)
    assert result == ATTITUDE_FRIENDLY, f"期望 friendly，得到 {result}"
    assert npc_neutral.attitude == ATTITUDE_FRIENDLY
    print("[test8] update_attitude indifferent→friendly ✓")

    # === 测试 9: update_attitude 未达阈值不转换 ===
    npc_test = NPC(name="测试NPC", attitude=ATTITUDE_INDIFFERENT)
    result = update_attitude(npc_test, success_count=5, failure_count=3)
    assert result is None, f"未达阈值应返回 None，得到 {result}"
    assert npc_test.attitude == ATTITUDE_INDIFFERENT
    print("[test9] update_attitude 未达阈值不转换 ✓")

    # === 测试 10: update_attitude 边界值（刚好达到阈值）===
    npc_edge = NPC(name="边界NPC", attitude=ATTITUDE_INDIFFERENT)
    # 连续失败4次（未达5）→ 不转换
    assert update_attitude(npc_edge, 0, 4) is None
    # 连续失败5次（刚好达到）→ 转换
    assert update_attitude(npc_edge, 0, 5) == ATTITUDE_HOSTILE
    print("[test10] update_attitude 边界值测试 ✓")

    # === 测试 11: SocialState 初始化 ===
    state = SocialState()
    assert state.current_npc is None
    assert state.conversation_history == []
    assert state.persuasion_dc == 15
    assert state.consecutive_successes == 0
    assert state.consecutive_failures == 0
    print("[test11] SocialState 初始化 ✓")

    # === 测试 12: 态度转换阈值常量完整性 ===
    # 所有四种转换路径都应有定义
    assert ("friendly", "degrade") in ATTITUDE_THRESHOLDS
    assert ("indifferent", "degrade") in ATTITUDE_THRESHOLDS
    assert ("hostile", "improve") in ATTITUDE_THRESHOLDS
    assert ("indifferent", "improve") in ATTITUDE_THRESHOLDS
    # 验证具体阈值
    assert ATTITUDE_THRESHOLDS[("friendly", "degrade")] == 10
    assert ATTITUDE_THRESHOLDS[("indifferent", "degrade")] == 5
    assert ATTITUDE_THRESHOLDS[("hostile", "improve")] == 15
    assert ATTITUDE_THRESHOLDS[("indifferent", "improve")] == 10
    print("[test12] 态度转换阈值常量完整性 ✓")

    # === 测试 13: 社交技能映射完整性 ===
    expected_skills = {"persuasion", "deception", "intimidation",
                       "performance", "insight"}
    assert set(SOCIAL_SKILLS.keys()) == expected_skills
    # 验证属性映射
    assert SOCIAL_SKILLS["persuasion"][0] == "cha"
    assert SOCIAL_SKILLS["insight"][0] == "wis"
    print("[test13] 社交技能映射完整性 ✓")

    # === 测试 14: 完整态度转换链路 ===
    # 冷漠 → (失败5次) → 敌对 → (成功15次) → 冷漠 → (成功10次) → 友好
    npc_chain = NPC(name="链路NPC", attitude=ATTITUDE_INDIFFERENT)
    # 冷漠→敌对
    assert update_attitude(npc_chain, 0, 5) == ATTITUDE_HOSTILE
    assert npc_chain.attitude == ATTITUDE_HOSTILE
    # 敌对→冷漠
    assert update_attitude(npc_chain, 15, 0) == ATTITUDE_INDIFFERENT
    assert npc_chain.attitude == ATTITUDE_INDIFFERENT
    # 冷漠→友好
    assert update_attitude(npc_chain, 10, 0) == ATTITUDE_FRIENDLY
    assert npc_chain.attitude == ATTITUDE_FRIENDLY
    print("[test14] 完整态度转换链路 ✓")

    # === 测试 15: 友好态度不因成功而进一步提升（已是最高）===
    npc_top = NPC(name="顶级友好NPC", attitude=ATTITUDE_FRIENDLY)
    # 友好态没有 improve 路径（已是最高级别）
    result = update_attitude(npc_top, success_count=100, failure_count=0)
    assert result is None, "友好态不应有提升路径"
    assert npc_top.attitude == ATTITUDE_FRIENDLY
    print("[test15] 友好态度不因成功而进一步提升 ✓")

    # === 测试 16: 敌对态度不因失败而进一步降级（已是最低）===
    npc_bottom = NPC(name="最低敌对NPC", attitude=ATTITUDE_HOSTILE)
    # 敌对态没有 degrade 路径（已是最低级别）
    result = update_attitude(npc_bottom, success_count=0, failure_count=100)
    assert result is None, "敌对态不应有降级路径"
    assert npc_bottom.attitude == ATTITUDE_HOSTILE
    print("[test16] 敌对态度不因失败而进一步降级 ✓")

    print("\n[social] 全部自检通过 ✓")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    _self_test()
