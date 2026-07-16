"""Director Agent — 意图分类 + 路由决策中枢。

职责:
  - 接收玩家输入，用 LLM 分类意图
  - 决定路由到哪个专项 Agent（Narrator / Combat / World / Rule Judge）
  - 组装最终叙事输出

设计参考: ITMO AI-DM 8-Agent 架构的 Director 角色，
AIDM 精简为单节点 LLM 分类 → 条件路由。
"""

from __future__ import annotations

import json
import re

from ..brain import llm
from ..brain.state import GameState


def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?|```", "", text, flags=re.I)
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        try:
            return json.loads(m.group(0) + "}")
        except Exception:
            return {}


# Director 的 system prompt — 意图分类器
_DIRECTOR_PROMPT = """\
你是D&D 5E意图分类器。把玩家输入分类为动作意图,只输出JSON(不要markdown)。
action_type ∈ attack|cast|ability_check|explore|start_combat|end_combat|rest|social|levelup|travel|other
通用字段: target_name, target_ac(整数,未知0), ability(str/dex/con/int/wis/cha), \
retrieval_query(用规则原词构造的检索串:动作规范名+检定类型+DC关键词,如'徒手打击 推撞 豁免DC 8 力量 熟练')
attack专有: weapon(武器中文名)
cast专有: spell_name, spell_level(整数), spell_dice(如8d6), damage_type(火焰/力场/...), \
spell_attack(true=攻击检定型/false=豁免型), save_ability(con/dex/...目标豁免属性), \
target_save_bonus(目标该豁免加值,未知0), casting_ability(int/wis/cha 施法属性)
ability_check/explore专有: skill(技能名), dc(整数,未知给10), proficient(true/false)
start_combat专有: enemies(数组[{name,dex_mod,side='enemy'}])
只输出JSON。"""


def classify_intent(state: GameState) -> dict:
    """Director Agent: LLM 意图分类 → 结构化 intent。

    这是多智能体架构的入口节点。Director 接收玩家输入，
    用 LLM 分类意图，返回结构化的 intent 字典。

    Returns:
        {"intent": {...}, "error": ""}
    """
    raw = llm.chat(_DIRECTOR_PROMPT, state["player_input"], temperature=0.1)
    intent = _extract_json(raw)
    intent.setdefault("action_type", "other")
    return {"intent": intent, "error": "" if intent else "意图解析失败"}


def route_action(state: GameState) -> str:
    """Director 的条件路由函数。

    根据 intent.action_type 决定下一步走向：
      - other/end_combat → 直接 resolve（无判定）
      - 其余 → 先 retrieve 规则

    这个函数被 LangGraph 的 add_conditional_edges 调用。
    """
    at = state.get("intent", {}).get("action_type")
    if at in ("other", "end_combat"):
        return "resolve"
    return "retrieve"
