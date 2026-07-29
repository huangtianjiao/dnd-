"""brain.utils — graph.py 拆分出的工具函数与共享常量。

包含:
  - JSON 解析工具（_extract_json, _extract_fields_fallback, _strip_to_text）
  - 展示/序列化辅助（_digest, _combatant_view）
  - 战斗载入辅助（_load_combat）
  - 共享常量（CLASS_CAST_ABILITY, CLASS_CON_PROFICIENCY, _HEAL_TYPES 等）
"""

from __future__ import annotations

import contextlib
import json
import logging
import re

from ..engine import conditions
from ..stats import store

_log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────
# 共享常量
# ──────────────────────────────────────────────────────────────────────────

CLASS_CAST_ABILITY = {  # 职业→施法属性（确定性，优先于 LLM 猜测）
    "法师": "int", "术士": "cha", "吟游诗人": "cha", "魔契师": "cha",
    "牧师": "wis", "德鲁伊": "wis", "圣武士": "wis", "游侠": "wis",
}

# 体质豁免熟练的职业（出处: PHB 职业表 Saving Throws）。
# 专注维持是体质豁免（R-SPL-020）：只有熟练体质豁免的职业才加熟练加值。
# 5E 默认仅野蛮人/战士/术士熟练体质豁免，其余施法职业需 War Caster / Resilient 专长。
CLASS_CON_PROFICIENCY = {"野蛮人", "战士", "术士"}

_HEAL_TYPES = ("治疗", "heal", "healing")


# ──────────────────────────────────────────────────────────────────────────
# JSON 解析工具
# ──────────────────────────────────────────────────────────────────────────

def extract_json(text: str) -> dict:
    """从 LLM 输出中提取 JSON 对象（兼容 markdown 代码块）。"""
    text = re.sub(r"```(?:json)?|```", "", text, flags=re.I)
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return {}
    cand = m.group(0)
    # 渐进尝试：原样 → 去 trailing comma → 补 '}'，尽量直接解析
    for attempt in (cand,
                    re.sub(r",\s*([}\]])", r"\1", cand),
                    cand + "}"):
        try:
            return json.loads(attempt)
        except json.JSONDecodeError:
            continue
    # LLM 偶发输出非严格 JSON（字段值内未转义引号等）：字段级正则兜底，尽力救回
    return _extract_fields_fallback(cand)


def _unescape(s: str) -> str:
    return s.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")


def _extract_fields_fallback(s: str) -> dict:
    """整体 JSON 解析失败时，按字段正则提取，避免整包丢弃导致 narration 变 JSON 碎片。"""
    def get_str(key: str) -> str:
        mm = re.search(r'"%s"\s*:\s*"((?:[^"\\]|\\.)*)"' % key, s, re.DOTALL)
        return _unescape(mm.group(1)) if mm else ""

    def get_list(key: str) -> list:
        mm = re.search(r'"%s"\s*:\s*\[([\s\S]*?)\]' % key, s)
        if not mm:
            return []
        return [_unescape(x) for x in re.findall(r'"((?:[^"\\]|\\.)*)"', mm.group(1))]

    return {
        "narration": get_str("narration"),
        "state_changes": [],  # 结构复杂，整体失败时难以可靠提取，降级为空
        "scene_update": get_str("scene_update"),
        "action_options": get_list("action_options"),
    }


def strip_to_text(raw: str) -> str:
    """JSON 解析彻底失败时的兜底：剥离 markdown/JSON 大括号结构，给玩家纯叙事文本。"""
    s = re.sub(r"```(?:json)?|```", "", raw, flags=re.I).strip()
    s = re.sub(r'^\s*\{', "", s).strip()
    s = re.sub(r'\}\s*$', "", s).strip()
    # 去掉行首 "narration": 这类键名残留
    s = re.sub(r'^"?(narration|scene_update)"?\s*:\s*', "", s, flags=re.I)
    return s[:600]


def digest(evidence: list[dict], n: int = 4, body: int = 320) -> str:
    """把规则证据列表格式化为 prompt 可注入的文本块。"""
    return "\n---\n".join(f"[{e.get('tag')}] {e.get('body','')[:body]}" for e in evidence[:n])


# ──────────────────────────────────────────────────────────────────────────
# 战斗载入辅助
# ──────────────────────────────────────────────────────────────────────────

def combatant_view(_c) -> dict:
    """把参战者（Combatant 对象 或 序列化 dict）转成 JSON 安全的精简 dict。

    narrate 会 json.dumps(combat_ctx)，而 Combatant 是 dataclass 且无 .dict()，
    直接放入会致 TypeError。这里取展示所需的 name/init/side/cid/is_player/hp/dead。
    """
    if isinstance(_c, dict):
        return {"name": _c.get("name", ""),
                "init": _c.get("init", _c.get("initiative", 0)),
                "side": _c.get("side", ""),
                "cid": _c.get("cid", ""),
                "is_player": _c.get("is_player", False),
                "hp": _c.get("hp", 0), "hp_max": _c.get("hp_max", 0),
                "dead": _c.get("dead", False)}
    return {"name": getattr(_c, "name", ""),
            "init": getattr(_c, "initiative", 0),
            "side": getattr(_c, "side", ""),
            "cid": getattr(_c, "cid", ""),
            "is_player": getattr(_c, "is_player", False),
            "hp": getattr(_c, "hp", 0), "hp_max": getattr(_c, "hp_max", 0),
            "dead": getattr(_c, "dead", False)}


def load_combat(campaign_id: int) -> dict:
    """若战役有进行中战斗，载入 GameState.combat。

    无战斗记录是常态（多数回合不在战斗中），故异常降级为空战斗并记 debug，
    便于排查真实 DB 故障而不污染正常流程。
    combatants 必须是 JSON 安全的纯 dict（narrate 会 json.dumps），
    Combatant 对象无 .dict()，故经 combatant_view 转换。
    """
    try:
        c = store.load_combat(campaign_id)
        return {"active": c.active, "combat_id": None, "round": c.round,
                "current_index": c.current_index,
                "combatants": [combatant_view(_c) for _c in c.initiative_order]}
    except Exception as e:
        _log.debug("载入战斗状态失败（通常表示无进行中战斗）campaign=%s: %s",
                   campaign_id, e)
        return {"active": False, "combat_id": None, "round": 0,
                "current_index": 0, "combatants": []}


# ──────────────────────────────────────────────────────────────────────────
# 条件辅助
# ──────────────────────────────────────────────────────────────────────────

def target_condition_state(it: dict) -> conditions.ConditionState:
    """从 intent 构建目标条件状态（由上层/LLM 提供 target_conditions 列表）。"""
    ts = conditions.ConditionState()
    for c in it.get("target_conditions", []):
        with contextlib.suppress(ValueError):
            ts.add(c)
    return ts
