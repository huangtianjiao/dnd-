"""P3 LangGraph 编排 v2 — 硬性判定链，覆盖 attack/cast/ability_check/explore + 战斗状态机 + HITL。

节点流：classify(意图,LLM) → retrieve(规则,hybrid) → verify(校验) →
[校验失败→retrieve重检索] / [ok+HITL→confirm(暂停让DM确认)] →
resolve(骰子,纯代码!) → narrate(叙事,LLM) → apply(持久化+战斗轮次推进)。
LLM 只在 classify/narrate/confirm 活动，resolve 全代码（硬性判定）。

硬性骰子覆盖：
- attack: check.attack_roll + damage.roll_damage（重击骰翻倍）R-CMB-017/022/023, R-DMG-001/CMB-029
- cast:   check.calc_save_dc(8+属性+熟练) + 法术攻击(check.attack_roll) / 目标豁免(check.saving_throw)
          + 豁免成功半伤(R-CHK-014) + 法术位消耗(R-SPL-002)   R-DM-002/SPL-021/022/CHK-011
- ability_check/explore: check.ability_check vs DC   R-CHK-010
- start_combat: combat.roll_initiative + store.save_combat   R-CMB-002
"""

from __future__ import annotations

import dataclasses
import json
import logging
import re

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from . import llm
from . import world
from .state import GameState
from ..knowledge import hybrid, verifier
from ..engine import check, damage, combat as cmb, conditions, concentration, dice as engine_dice
from ..data import equipment
from ..brain import rest as rest_mod
from ..brain import social as social_mod
from ..brain import levelup as levelup_mod
from ..brain import exploration as exploration_mod
from ..stats import store, models

# 多智能体架构接入：Director + Rule Judge 从 agents 包导入
from ..agents.director import classify_intent as _director_classify
from ..agents.rule_judge import (
    retrieve as _judge_retrieve,
    retrieve_retry as _judge_retrieve_retry,
    verify as _judge_verify,
)


_log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────
# 工具
# ──────────────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict:
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


def _strip_to_text(raw: str) -> str:
    """JSON 解析彻底失败时的兜底：剥离 markdown/JSON 大括号结构，给玩家纯叙事文本。"""
    s = re.sub(r"```(?:json)?|```", "", raw, flags=re.I).strip()
    s = re.sub(r'^\s*\{', "", s).strip()
    s = re.sub(r'\}\s*$', "", s).strip()
    # 去掉行首 "narration": 这类键名残留
    s = re.sub(r'^"?(narration|scene_update)"?\s*:\s*', "", s, flags=re.I)
    return s[:600]


def _digest(evidence: list[dict], n: int = 4, body: int = 320) -> str:
    return "\n---\n".join(f"[{e.get('tag')}] {e.get('body','')[:body]}" for e in evidence[:n])


def _combatant_view(_c) -> dict:
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


def _load_combat(campaign_id: int) -> dict:
    """若战役有进行中战斗，载入 GameState.combat。

    无战斗记录是常态（多数回合不在战斗中），故异常降级为空战斗并记 debug，
    便于排查真实 DB 故障而不污染正常流程。
    combatants 必须是 JSON 安全的纯 dict（narrate 会 json.dumps），
    Combatant 对象无 .dict()，故经 _combatant_view 转换。
    """
    try:
        c = store.load_combat(campaign_id)
        return {"active": c.active, "combat_id": None, "round": c.round,
                "current_index": c.current_index,
                "combatants": [_combatant_view(_c) for _c in c.initiative_order]}
    except Exception as e:
        _log.debug("载入战斗状态失败（通常表示无进行中战斗）campaign=%s: %s",
                   campaign_id, e)
        return {"active": False, "combat_id": None, "round": 0,
                "current_index": 0, "combatants": []}


# ──────────────────────────────────────────────────────────────────────────
# 节点：classify / retrieve / verify / confirm
# ──────────────────────────────────────────────────────────────────────────

def classify(state: GameState) -> dict:
    """LLM 意图分类 → 结构化 intent。

    ⚠ 本节点目前未被 build_graph() 使用——图的实际入口节点是
    agents.director.classify_intent（其 _DIRECTOR_PROMPT 已枚举全部动作类型）。
    本函数保留为离线/回退用途，prompt 与 Director 对齐到同一完整动作集，
    避免出现「本地枚举残缺 → 误以为战术动作不可达」的误导。
    """
    prompt = (
        "你是D&D 5E意图分类器。把玩家输入分类为动作意图,只输出JSON(不要markdown)。\n"
        "action_type ∈ attack|cast|ability_check|explore|start_combat|end_combat|rest|"
        "social|levelup|travel|hide|search|grapple|shove|dash|dodge|disengage|help|"
        "ready|use_item|study|opportunity_attack|other\n"
        "通用字段: target_name, target_ac(整数,未知0), ability(str/dex/con/int/wis/cha), "
        "retrieval_query(用规则原词构造的检索串:动作规范名+检定类型+DC关键词,如'徒手打击 推撞 豁免DC 8 力量 熟练')\n"
        "attack/opportunity_attack专有: weapon(武器中文名)\n"
        "cast专有: spell_name, spell_level(整数), spell_dice(如8d6), damage_type(火焰/力场/...), "
        "spell_attack(true=攻击检定型/false=豁免型), save_ability(con/dex/...目标豁免属性), "
        "target_save_bonus(目标该豁免加值,未知0), casting_ability(int/wis/cha 施法属性)\n"
        "ability_check/explore/hide/search/study专有: skill(技能名), dc(整数,未知给10), proficient(true/false)\n"
        "grapple/shove专有: ability(str/dex), dc, shove_type(prone/push,仅shove)\n"
        "help专有: target_name(协助对象); ready专有: trigger_condition, readied_action\n"
        "use_item专有: item_name, item_effect; start_combat专有: enemies(数组[{name,dex_mod,side='enemy',hp_max(整数,怪物HP上限,如哥布林7,未知给7)}])\n"
        "只输出JSON。"
    )
    raw = llm.chat(prompt, state["player_input"], temperature=0.1)
    intent = _extract_json(raw)
    intent.setdefault("action_type", "other")
    return {"intent": intent, "error": "" if intent else "意图解析失败"}


def retrieve(state: GameState) -> dict:
    """hybrid 检索相关规则（校验与叙事用）。"""
    q = state["intent"].get("retrieval_query") or state["player_input"]
    return {"evidence": hybrid.search_spec_hybrid(q, limit=6)}


def retrieve_retry(state: GameState) -> dict:
    """校验驳回后重检索：用 issues/正确方法 补关键词。"""
    issues = state.get("verification", {}).get("issues", [])
    base = state["intent"].get("retrieval_query") or state["player_input"]
    q = base + " " + " ".join(issues) + " 检定方式 DC来源 豁免"
    return {"evidence": hybrid.search_spec_hybrid(q[:80], limit=6)}


def verify(state: GameState) -> dict:
    """关键词预检判定参数合规性（语义校验留 confirm/LLM）。"""
    it = state["intent"]
    if it.get("action_type") in ("other", "start_combat", "end_combat"):
        return {"verification": {"ok": True, "issues": []}}
    v = verifier.verify(it.get("retrieval_query", state["player_input"]),
                        proposed_check_type=it.get("ability"),
                        proposed_dc=it.get("target_ac") or it.get("dc"),
                        limit=6)
    return {"verification": {"ok": v.ok, "issues": v.issues}}


def confirm(state: GameState) -> dict:
    """HITL：关键判定暂停让 DM 确认（interrupt）。不启用 hitl 则直通。"""
    if not state.get("hitl"):
        return {"confirmed": True}
    answer = interrupt({  # 暂停；恢复时 answer = DM 输入
        "question": "DM 确认此判定？（y=通过 / n=驳回重做）",
        "intent": state["intent"],
        "verification": state["verification"],
        "evidence": [e.get("tag") for e in state.get("evidence", [])],
    })
    ok = str(answer).lower() in ("y", "yes", "true", "1", "通过")
    return {"confirmed": ok}


# ──────────────────────────────────────────────────────────────────────────
# 节点：resolve（硬性骰子，按 action_type 分派，纯代码）
# ──────────────────────────────────────────────────────────────────────────

def _target_condition_state(it: dict) -> conditions.ConditionState:
    """从 intent 构建目标条件状态（由上层/LLM 提供 target_conditions 列表）。"""
    ts = conditions.ConditionState()
    for c in it.get("target_conditions", []):
        try:
            ts.add(c)
        except ValueError:
            pass
    return ts


def _resolve_attack(ch, it) -> dict:
    ability = it.get("ability") or "str"
    bonus = ch.ability_mod(ability) + ch.prof()
    ac = int(it.get("target_ac") or 10)

    # R-GLS-044~058 条件优劣势：从角色卡读攻击者状态 + 从 intent 读目标状态
    atk_state = ch.to_condition_state()
    tgt_state = _target_condition_state(it)
    distance = int(it.get("distance_ft") or 5)
    mods = conditions.attack_modifiers(atk_state, tgt_state, distance)
    adv = bool(it.get("advantage")) or mods.attacker_advantage
    dis = bool(it.get("disadvantage")) or mods.attacker_disadvantage
    # R-CMB-008 目标回避 → 攻击劣势
    if it.get("target_dodging"):
        dis = True

    # R-GLS-047 力竭 d20 惩罚（等级×2，作为负的临时加值传入）
    exh_penalty = -conditions.d20_penalty(atk_state)

    atk = check.attack_roll(bonus=bonus, ac=ac, advantage=adv, disadvantage=dis,
                            circ=exh_penalty)             # R-CMB-017/022/023
    out = {"kind": "attack", "attack_total": atk.total, "d20": atk.d20,
           "hit": atk.hit, "crit": atk.crit, "rolls": atk.rolls, "target_ac": ac, "bonus": bonus}
    if atk.hit:
        # 武器三级回退：玩家明说 → 角色卡 equipped_weapon → 徒手(1+力量)
        # 详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段A4/B1
        wname = it.get("weapon") or getattr(ch, "equipped_weapon", "") or "徒手"
        dice_expr, dmg_type = equipment.resolve_weapon_damage(wname)
        # R-GLS-052/058 麻痹/昏迷5尺内近战命中即重击
        crit = atk.crit or mods.target_auto_crit_if_hit
        dr = damage.roll_damage(damage.DamageRequest(  # R-DMG-001 + R-CMB-029
            dice_expr=dice_expr, damage_type=dmg_type,
            ability_mod=ch.ability_mod(ability), add_mod=True, crit=crit),
            resistances=it.get("resistances", []),
            vulnerabilities=it.get("vulnerabilities", []),
            immunities=it.get("immunities", []))
        out.update({"damage": dr.final, "damage_type": dmg_type,
                    "damage_rolls": dr.dice_rolls, "weapon": wname,
                    "resisted": dr.resisted, "vulnerable": dr.vulnerable, "immune": dr.immune})
    return out


CLASS_CAST_ABILITY = {  # 职业→施法属性（确定性，优先于 LLM 猜测）
    "法师": "int", "术士": "cha", "吟游诗人": "cha", "魔契师": "cha",
    "牧师": "wis", "德鲁伊": "wis", "圣武士": "wis", "游侠": "wis",
}

# 体质豁免熟练的职业（出处: PHB 职业表 Saving Throws）。
# 专注维持是体质豁免（R-SPL-020）：只有熟练体质豁免的职业才加熟练加值。
# 5E 默认仅野蛮人/战士/术士熟练体质豁免，其余施法职业需 War Caster / Resilient 专长。
CLASS_CON_PROFICIENCY = {"野蛮人", "战士", "术士"}


def _resolve_cast(ch, it) -> dict:
    # 施法资格校验：非施法职业不能施法（R-SPL-001 施法者前提）
    if ch.char_class not in CLASS_CAST_ABILITY:
        return {"kind": "cast", "error": f"{ch.char_class} 不会施法，无法施展法术"}
    # 法术位校验（戏法 level<=0 不耗位）R-SPL-002
    level = int(it.get("spell_level") or 1)
    if level >= 1:
        try:
            _sd = json.loads(ch.spell_slots_json) if ch.spell_slots_json else {}
        except Exception:
            _sd = {}
        if _sd.get(str(level), 0) <= 0:
            return {"kind": "cast", "error": f"无 {level} 环法术位"}
    cast_ability = CLASS_CAST_ABILITY.get(ch.char_class) or it.get("casting_ability") or "int"
    cast_mod = ch.ability_mod(cast_ability)
    prof = ch.prof()
    save_dc = check.calc_save_dc(cast_mod, prof)            # R-DMG-002/R-SPL-021
    atk_bonus = cast_mod + prof                              # R-SPL-022
    # 目标抗性/易伤/免疫
    resists = it.get("resistances", [])
    vulns = it.get("vulnerabilities", [])
    immuns = it.get("immunities", [])
    out = {"kind": "cast", "spell_save_dc": save_dc, "spell_attack_bonus": atk_bonus,
           "spell_level": level}

    # 查 spells 数据表取权威值（优先于 LLM 猜测）：damage_dice/damage_type/effect_type/
    # save_ability/concentration。表未收录（get_spell 抛 KeyError）则回退 LLM 猜测，
    # 再保守默认；不硬性报错——因 spells 表仅 25 条，报错会阻断多数施法。
    # 详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段B2
    spell_name = it.get("spell_name", "")
    _spell = None
    if spell_name:
        try:
            from ..data import spells as _sp
            _spell = _sp.get_spell(spell_name)
        except Exception:
            _spell = None
    if _spell:
        if _spell.concentration:
            out["concentrating_on"] = _spell.name
        spell_dice = _spell.damage_dice or it.get("spell_dice") or ""
        dmg_type = damage.normalize_damage_type(_spell.damage_type or it.get("damage_type") or "力场")
        _etype = _spell.effect_type
        if _spell.save_ability:
            out["save_ability"] = _spell.save_ability.lower()
    else:
        spell_dice = it.get("spell_dice") or ""
        dmg_type = damage.normalize_damage_type(it.get("damage_type") or "力场")
        _etype = None
    out["spell_name"] = spell_name
    out["spell_dice"] = spell_dice or "1d8"   # 输出展示用（无伤害骰时保守占位）
    has_damage = bool(spell_dice)             # 无伤害骰 → buff/utility/护盾，不走伤害结算

    if _etype == "automatic" or it.get("auto_hit"):
        # 自动命中型（魔法飞弹）：不掷攻击/豁免，直接伤害（抗性/易伤/免疫仍走管线）
        if has_damage:
            dr = damage.roll_damage(damage.DamageRequest(dice_expr=spell_dice, damage_type=dmg_type, add_mod=False),
                                    resistances=resists, vulnerabilities=vulns, immunities=immuns)
            out.update({"hit": True, "auto_hit": True, "damage": dr.final, "damage_type": dmg_type,
                        "damage_rolls": dr.dice_rolls, "resisted": dr.resisted,
                        "vulnerable": dr.vulnerable, "immune": dr.immune})
        else:
            out.update({"hit": True, "auto_hit": True, "damage": 0})
    elif it.get("spell_attack") or _etype == "attack_roll":  # 法术攻击检定型
        ac = int(it.get("target_ac") or 10)
        # 条件优劣势
        atk_state = ch.to_condition_state()
        mods = conditions.attack_modifiers(atk_state, _target_condition_state(it),
                                           int(it.get("distance_ft") or 5))
        adv = bool(it.get("advantage")) or mods.attacker_advantage
        dis = bool(it.get("disadvantage")) or mods.attacker_disadvantage or bool(it.get("target_dodging"))
        atk = check.attack_roll(bonus=atk_bonus, ac=ac, advantage=adv, disadvantage=dis,
                                 circ=-conditions.d20_penalty(atk_state))  # R-SPL-022 + R-CMB-017
        out.update({"spell_attack_total": atk.total, "d20": atk.d20, "hit": atk.hit, "crit": atk.crit, "target_ac": ac})
        if atk.hit and has_damage:
            crit = atk.crit or mods.target_auto_crit_if_hit
            dr = damage.roll_damage(damage.DamageRequest(dice_expr=spell_dice, damage_type=dmg_type,
                                                          add_mod=False, crit=crit),
                                     resistances=resists, vulnerabilities=vulns, immunities=immuns)
            out.update({"damage": dr.final, "damage_type": dmg_type, "damage_rolls": dr.dice_rolls,
                        "resisted": dr.resisted, "vulnerable": dr.vulnerable, "immune": dr.immune})
    else:  # 豁免型法术 / 无伤害 buff·utility
        if has_damage:
            save_bonus = int(it.get("target_save_bonus") or 0)
            sv = check.saving_throw(mod=save_bonus, prof=0, proficient=False, dc=save_dc)  # R-CHK-011
            dr = damage.roll_damage(damage.DamageRequest(dice_expr=spell_dice, damage_type=dmg_type, add_mod=False),
                                    resistances=resists, vulnerabilities=vulns, immunities=immuns)
            piped = dr.final  # 经管线后的全额伤害（已处理抗性/易伤/免疫）
            # R-CHK-014 豁免成功半伤：管线后再减半（抗性+半伤可叠加=1/4）
            final = engine_dice.round_down(piped / 2) if sv.success else piped
            out.update({"save_success": sv.success, "save_total": sv.total, "raw_damage": piped,
                        "damage": final, "damage_type": dmg_type, "damage_rolls": dr.dice_rolls,
                        "resisted": dr.resisted, "vulnerable": dr.vulnerable, "immune": dr.immune})
        else:
            out.update({"hit": True, "damage": 0})  # 无伤害法术默认生效
    return out


# 技能名→属性映射（LLM 未给 ability 时按 skill 推断，避免察觉/调查误用力量的 +3）
_SKILL_ABILITY = {
    "察觉": "wis", "求生": "wis", "医药": "wis", "洞悉": "wis", "驯兽": "wis", "感知": "wis",
    "调查": "int", "奥秘": "int", "历史": "int", "自然": "int", "宗教": "int",
    "运动": "str", "特技": "dex", "潜行": "dex", "手上功夫": "dex",
    "表演": "cha", "威吓": "cha", "欺瞒": "cha", "说服": "cha",
}


def _infer_ability(skill, action_type: str) -> str:
    """从 skill 名推断属性；explore→wis, study→int，其余兜底 str。"""
    if skill:
        s = str(skill)
        for k, ab in _SKILL_ABILITY.items():
            if k in s:
                return ab
    if action_type == "explore":
        return "wis"
    if action_type == "study":
        return "int"
    return "str"


def _resolve_ability_check(ch, it) -> dict:
    ability = it.get("ability") or _infer_ability(it.get("skill"),
                                                  it.get("action_type", "ability_check"))
    dc = int(it.get("dc") or 10)
    proficient = bool(it.get("proficient"))
    # R-GLS-047 力竭 d20 惩罚（等级×2）
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())
    r = check.ability_check(mod=ch.ability_mod(ability), prof=ch.prof(),
                            proficient=proficient, dc=dc, circ=exh_penalty)    # R-CHK-010
    return {"kind": "ability_check", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "margin": r.margin, "ability": ability}


def _resolve_rest(state, ch, it) -> dict:
    """休息机制：短休消耗生命骰恢复HP+恢复职业特性；长休恢复全部HP+所有法术位+力竭-1。
    R-GLS-014/R-GLS-015

    直接透传 rest_mod 的完整结果字典（含 hp_restored / exhaustion_reduced /
    temp_hp_cleared / features_recharged / feature_recharge_amounts 等），
    供 apply_node 落盘。注意 rest_mod 不修改角色卡，落盘由 _apply_rest_to_character 完成。
    """
    # rest_type 从 intent 读，否则从玩家输入推断（LLM 常不给 rest_type，"长休"→long）
    pi = state.get("player_input", "") or ""
    rest_type = it.get("rest_type") or (
        "long" if ("长休" in pi or "long rest" in pi.lower() or "long" in pi.lower() and "休" in pi) else "short")
    if rest_type == "short":
        hit_dice_to_spend = int(it.get("hit_dice_to_spend", 0))
        result = rest_mod.short_rest(ch, hit_dice_to_spend=hit_dice_to_spend)
    else:  # long
        result = rest_mod.long_rest(ch)
    result["kind"] = "rest"
    return result


def _apply_rest_to_character(ch, result: dict) -> None:
    """将休息收益落盘到 Character（在 apply_node 中调用）。

    R-GLS-014 短休 / R-GLS-015 长休

    可落盘字段：
        - HP 恢复（短休/长休）→ ch.hp_current（上限 ch.hp_max）
        - 力竭 -1（长休）→ ch.exhaustion
        - 临时生命值清空（长休）→ ch.temp_hp = 0
        - 法术位恢复至上限（长休，施法职业，R-SPL-003）→ ch.set_spell_slots(max)

    暂不可落盘（Character 模型无对应字段，需后续扩展）：
        - 生命骰消耗/恢复（无 hit_dice 字段）
        - 职业特性使用次数恢复（无特性用量追踪）
    """
    if not result.get("success"):
        return
    rtype = result.get("type", "short")
    # HP 恢复（短休与长休）
    hp_restored = int(result.get("hp_restored", 0))
    if hp_restored:
        ch.hp_current = min(ch.hp_max, ch.hp_current + hp_restored)
    if rtype == "long":
        # 力竭 -1（至少 0）
        exh = int(result.get("exhaustion_reduced", 0))
        if exh:
            ch.exhaustion = max(0, ch.exhaustion - exh)
        # 临时生命值清空
        if result.get("temp_hp_cleared"):
            ch.temp_hp = 0
        # 法术位恢复至上限（施法职业，R-SPL-003）。Character 无 max_spell_slots 持久化，
        # 故按等级重算 max（与 create_character 初始化一致）。
        if result.get("spell_slots_restored") and ch.char_class in CLASS_CAST_ABILITY:
            try:
                from ..data import spells as _sp
                ch.set_spell_slots(_sp.max_spell_slots(ch.level))
            except Exception as e:
                _log.debug("长休恢复法术位失败 cid=%s: %s", getattr(ch, "id", "?"), e)


# NPC 态度同义词归一化表（LLM 可能返回中文/非标准串）
_ATTITUDE_ALIASES = {
    "friendly": "friendly", "friend": "friendly", "友善": "friendly", "友好": "friendly",
    "indifferent": "indifferent", "neutral": "indifferent", "normal": "indifferent",
    "中立": "indifferent", "冷漠": "indifferent", "一般": "indifferent", "普通": "indifferent",
    "hostile": "hostile", "enemy": "hostile", "angry": "hostile",
    "敌对": "hostile", "敌意": "hostile", "愤怒": "hostile", "仇视": "hostile",
}


def _normalize_attitude(raw) -> str:
    """把 LLM 返回的态度串归一化为 {friendly, indifferent, hostile}，非法回退 indifferent。

    NPC.__post_init__ 校验态度必须为三选一，否则 ValueError。LLM 可能返回
    "neutral"/"友好"/"wary" 等非标准串，这里做容错归一化，避免社交动作崩溃。
    """
    if not isinstance(raw, str):
        return "indifferent"
    return _ATTITUDE_ALIASES.get(raw.strip().lower(), "indifferent")


def _resolve_social(state: GameState, ch, it) -> dict:
    """社交流程：NPC态度系统(友好/冷漠/敌对)/四步社交互动/态度转换阈值。
    R-CON-012/R-DM-047

    态度持久化：从 Scene.npcs 读取该 NPC 已记录的态度与连续成功/失败计数，
    累加本轮结果后用 update_attitude 判定是否转换，结果交 apply_node 写回 Scene。
    这样态度转换阈值（10/5/15/10）能跨回合累积，社交态度系统真正生效，
    而非每轮单次检定因达不到阈值而恒不变。
    """
    npc_name = it.get("npc_name", "NPC")
    llm_attitude = _normalize_attitude(it.get("npc_attitude", "indifferent"))
    skill = it.get("skill", "persuasion")
    dc = int(it.get("dc", 15))

    # 从场景读取该 NPC 的已记录态度与连续计数（跨回合累积）
    camp_id = state.get("campaign_id")
    stored_attitude = llm_attitude
    consec_success = 0
    consec_failure = 0
    sc = None
    if camp_id:
        try:
            sc = store.get_scene(camp_id)
        except Exception as e:
            _log.debug("社交读取场景失败 campaign=%s: %s", camp_id, e)
    if sc:
        for n in sc.npcs:
            if n.get("name") == npc_name:
                stored_attitude = _normalize_attitude(n.get("attitude", llm_attitude))
                consec_success = int(n.get("success_count", 0))
                consec_failure = int(n.get("failure_count", 0))
                break

    # 创建NPC对象（用场景记录的态度优先于 LLM 猜测）
    npc = social_mod.NPC(name=npc_name, attitude=stored_attitude)

    # 计算社交DC修正（友好-5/冷漠0/敌对+5）
    dc_modifier = social_mod.check_social_dc(npc.attitude)
    final_dc = max(1, dc + dc_modifier)

    # 执行社交检定
    ability = "cha" if skill in ("persuasion", "deception", "intimidation", "performance") else "wis"
    r = check.ability_check(mod=ch.ability_mod(ability), prof=ch.prof(),
                            proficient=True, dc=final_dc)

    # 累加连续计数：成功则连续成功+1、连续失败清0；失败则反之
    if r.success:
        consec_success += 1
        consec_failure = 0
    else:
        consec_failure += 1
        consec_success = 0
    new_attitude = social_mod.update_attitude(npc, consec_success, consec_failure)

    return {"kind": "social", "skill": skill, "dc": final_dc,
            "check_total": r.total, "d20": r.d20,
            "success": r.success, "margin": r.margin,
            "npc_name": npc_name, "npc_attitude": stored_attitude,
            "new_attitude": new_attitude if new_attitude else stored_attitude,
            "consec_success": consec_success, "consec_failure": consec_failure,
            "dc_modifier": dc_modifier}


def _character_to_levelup_dict(ch) -> dict:
    """把 Character 桥接为 level_up() 期望的角色字典。

    level_up() 期望：大写属性键（scores["CON"]）、xp 字段、class_name 键；
    而 Character 用小写属性键、无 xp 字段、职业字段名为 char_class。
    DM 主导的升级视为里程碑升级：注入「达到下一级所需 XP」以通过 XP 门槛
    （R-DM-042 里程碑），不强制玩家先刷 XP。
    """
    next_level = min(ch.level + 1, levelup_mod.MAX_LEVEL)
    return {
        "level": ch.level,
        "xp": levelup_mod.XP_TABLE.get(next_level, 0),   # 里程碑：满足门槛
        "class_name": ch.char_class,
        "scores": {k.upper(): v for k, v in ch.abilities.items()},
        "hp_max": ch.hp_max,
        "hp_current": ch.hp_current,
        "features": list(ch.feats),
        "asi_taken": False,
    }


def _apply_levelup_to_character(ch, dice: dict) -> None:
    """把升级结果落盘到 Character（在 apply_node 中调用，仿 rest 模式）。

    level_up() 已在 _resolve_levelup 中对纯字典计算完毕；此处仅写回等级与 HP 增量。
    熟练加值由 ch.prof() 按等级实时计算，无需独立字段。属性提升(ASI)与专长选择
    走 /character/{cid}/select-feat 等专用 API，本次升级调用 ability_improvements=None，
    故不在此落盘属性/专长。
    """
    new_level = dice.get("new_level")
    if new_level:
        ch.level = new_level
    gained = int(dice.get("hp_gained", 0))
    if gained:
        ch.hp_max += gained
        ch.hp_current += gained


def _resolve_levelup(ch, it) -> dict:
    """升级与成长：XP表(20级)/升级五步骤/游戏四阶段(T1-T4)。
    R-DM-041/R-DM-042/R-DM-043/R-DM-044/R-DM-045

    注意：level_up(character: dict, ...) 期望 dict 角色，直接传 Character 对象会
    因无 .get() 方法而 AttributeError。这里先桥接为 dict 再调用，结果落盘由
    apply_node 的 levelup 分支完成（resolve 不持久化，保持与 rest 一致）。
    """
    current_level = ch.level
    new_level = current_level + 1

    if new_level > levelup_mod.MAX_LEVEL:
        return {"kind": "levelup", "error": "已达最高等级20"}

    char_dict = _character_to_levelup_dict(ch)
    try:
        result = levelup_mod.level_up(
            char_dict, new_class=None, new_features=None,
            ability_improvements=None, hit_die_roll=None,
        )
    except ValueError as e:
        return {"kind": "levelup", "error": str(e)}

    return {"kind": "levelup", "old_level": current_level,
            "new_level": result.get("new_level", new_level),
            "hp_gained": result.get("hp_gained", 0),
            "pb_changed": result.get("pb_changed", False),
            "new_pb": result.get("new_proficiency_bonus", 0),
            "tier": result.get("tier", levelup_mod.get_tier(new_level))}


def _resolve_terrain(state, it) -> str:
    """地形解析：intent.terrain 优先（须在 TERRAIN_TABLE 内），
    否则从 Scene.environment 子串匹配 TERRAIN_TABLE，再回退 intent 原值或"森林"。

    详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段B3。返回值未必在 TERRAIN_TABLE 内。
    """
    terrain = it.get("terrain")
    if terrain and terrain in exploration_mod.TERRAIN_TABLE:
        return terrain
    camp_id = state.get("campaign_id")
    if camp_id:
        try:
            sc = store.get_scene(camp_id)
            if sc and sc.environment:
                for t in exploration_mod.TERRAIN_TABLE:
                    if t in sc.environment:
                        return t
        except Exception:
            pass
    return terrain or "森林"


def _resolve_travel(state, ch, it) -> dict:
    """探索流程：旅行步调/导航检定/被动察觉/随机遭遇/资源追踪。
    R-DM-026~R-DM-040 / R-GLS-048 旅行步调效应

    地形与 nav_dc 从场景/地形表取（B3），不再写死"森林"/15。
    """
    # 归一化步调名（兼容英文/中文输入），默认中速
    pace_raw = str(it.get("pace", "中速")).strip().lower()
    _PACE_ALIASES = {
        "fast": "快速", "快速": "快速",
        "normal": "中速", "中速": "中速", "medium": "中速",
        "slow": "慢速", "慢速": "慢速",
    }
    pace = _PACE_ALIASES.get(pace_raw, "中速")
    terrain = _resolve_terrain(state, it)
    # nav_dc / 被动察觉 DC：地形表命中则用权威值，否则回退 intent/默认
    try:
        _tp = exploration_mod.terrain_params(terrain)
        nav_dc = _tp.nav_dc
        perception_dc = _tp.search_dc
    except ValueError:
        nav_dc = int(it.get("nav_dc", 15))
        perception_dc = 15

    # 获取旅行步调信息（含步调效应：感知/隐匿优劣势）
    # 规则: R-GLS-048  出处: 玩家手册2024/进行游戏/旅行.htm
    pace_info = exploration_mod.get_travel_pace(pace)

    # 导航检定：感知(生存) d20 检定对抗 nav_dc
    # 规则: R-DM-037  出处: 城主指南2024/2.运作游戏/运作探索/旅行.htm
    nav_check = check.ability_check(mod=ch.ability_mod("wis"), prof=ch.prof(),
                                    proficient=True, dc=nav_dc)
    nav_result = exploration_mod.navigation(
        survival_total=nav_check.total, nav_dc=nav_dc,
    )

    # 随机遭遇检定
    encounter_result = exploration_mod.random_encounter_check()

    # 被动察觉检测（队伍最高被动察觉，此处以角色单人代表）
    # 规则: R-DM-012  出处: 察觉.htm
    passive_perception = 10 + ch.ability_mod("wis")
    perception_result = exploration_mod.check_passive_perception(
        party_passive_scores=[(ch.name, passive_perception)],
        dc=perception_dc,
    )

    return {"kind": "travel", "pace": pace,
            "per_minute_ft": pace_info.per_minute_ft,
            "per_hour_miles": pace_info.per_hour_miles,
            "per_day_miles": pace_info.per_day_miles,
            # 步调效应（供 narrate 层叙述优劣势）
            "stealth_disadvantage": pace_info.stealth_disadvantage,
            "perception_disadvantage": pace_info.perception_disadvantage,
            "perception_advantage": pace_info.perception_advantage,
            # dataclass → 纯 dict，避免 narrate/apply 的 json.dumps 序列化崩溃
            "nav_result": dataclasses.asdict(nav_result),
            "nav_check_total": nav_check.total,
            "nav_check_success": nav_check.success,
            "encounter_result": dataclasses.asdict(encounter_result),
            "perception_result": dataclasses.asdict(perception_result),
            "nav_dc": nav_dc,
            "perception_dc": perception_dc,
            "terrain": terrain}


def resolve(state: GameState) -> dict:
    """硬性骰子分派（纯代码，LLM 不参与）。"""
    it = state["intent"]
    at = it.get("action_type")
    cid = state.get("character_id")
    ch = store.get_character(cid) if cid else None
    if ch is None and at not in ("start_combat", "end_combat"):
        return {"dice": {}, "error": "角色卡不存在"}
    # 死亡/倒下行动限制（R-DMG-017）：
    #   dead=True 完全死亡 → 拒绝所有动作（需复活，药水不能复活死者）
    #   0HP 倒下(未死) → 拒绝战斗动作(攻击/施法/擒抱等)，但允许 use_item(治疗自救)/rest/other；
    #   死亡豁免由 apply_node 自动投，无需玩家行动。
    if ch and ch.dead:
        return {"dice": {"kind": at, "error": "你已死亡，无法行动（需复活法术）"}}
    if (ch and ch.hp_current <= 0 and not ch.dead
            and at not in ("use_item", "other")):
        return {"dice": {"kind": at, "error": "你已倒下(0HP)无法行动，只能使用治疗药水自救或等待死亡豁免"}}
    # 战斗中动作限制：战斗中只能做战斗动作，travel/explore/rest/levelup 是战斗外活动
    # （逃跑用 dash/disengage，搜索/研究战斗中可作动作）。R-CMB-004 回合动作经济
    if state.get("combat", {}).get("active") and at in ("travel", "explore", "rest", "levelup"):
        return {"dice": {"kind": at, "error": "战斗中不能旅行/探索/休息/升级；逃跑用 dash/disengage，战斗用 attack/cast"}}

    if at == "attack":
        return {"dice": _resolve_attack(ch, it)}
    if at == "cast":
        return {"dice": _resolve_cast(ch, it)}
    if at in ("ability_check", "explore"):
        return {"dice": _resolve_ability_check(ch, it)}
    if at == "start_combat":
        return _resolve_start_combat(state, ch, it)
    if at == "end_combat":
        return {"dice": {"kind": "end_combat"}, "combat": {"active": False}}
    if at == "rest":
        return {"dice": _resolve_rest(state, ch, it)}
    if at == "social":
        return {"dice": _resolve_social(state, ch, it)}
    if at == "levelup":
        return {"dice": _resolve_levelup(ch, it)}
    if at == "travel":
        return {"dice": _resolve_travel(state, ch, it)}
    # —— 战术动作（不掷骰，仅标记状态）——
    if at == "dash":
        return {"dice": {"kind": "dash", "extra_movement_ft": ch.speed}}
    if at == "dodge":
        return {"dice": {"kind": "dodge", "effect": "对本角色的攻击具有劣势"}}
    if at == "disengage":
        return {"dice": {"kind": "disengage", "effect": "本回合移动不引发借机攻击"}}
    if at == "help":
        return {"dice": {"kind": "help",
                         "target": it.get("target_name", ""),
                         "effect": f"使{it.get('target_name', '盟友')}的下次检定具有优势"}}
    if at == "ready":
        return {"dice": {"kind": "ready",
                         "trigger": it.get("trigger_condition", ""),
                         "action": it.get("readied_action", "")}}
    # —— 技能动作（需要检定）——
    if at == "hide":
        return {"dice": _resolve_hide(ch, it)}
    if at == "search":
        return {"dice": _resolve_search(ch, it)}
    if at == "use_item":
        item = it.get("item_name", "") or ""
        effect = it.get("item_effect", "") or ""
        pi = state.get("player_input", "") or ""
        # 治疗药水等恢复物品：LLM 常不提取 item_name，故从 player_input+item+effect 综合检测
        # 关键词 → 掷标准治疗药水(2d4+2)生成 heal，由 apply_node 应用（含死亡计数归零
        # R-ADD-008），打通 0HP倒下→喝药水→恢复HP。
        if any(k in (item + effect + pi) for k in ("治疗", "药水", "治愈", "回血", "生命药剂")):
            rolls = engine_dice.roll_dice("2d4+2")
            return {"dice": {"kind": "use_item", "item": item or "治疗药水", "effect": effect,
                             "heal": rolls.total, "heal_rolls": rolls.dice_rolls,
                             "heal_type": "治疗药水"}}
        return {"dice": {"kind": "use_item", "item": item, "effect": effect}}
    if at == "grapple":
        return {"dice": _resolve_grapple(ch, it)}
    if at == "shove":
        return {"dice": _resolve_shove(ch, it)}
    if at == "study":
        return {"dice": _resolve_study(ch, it)}
    if at == "opportunity_attack":
        return {"dice": _resolve_opportunity_attack(ch, it)}
    return {"dice": {}}  # other → 仅叙事


# —— 新增技能动作的确定性检定 ——


def _resolve_hide(ch, it) -> dict:
    """躲藏：敏捷(潜行)检定 vs 对手被动察觉。R-GLS-009"""
    stealth_mod = ch.ability_mod("dex")
    prof = ch.prof()
    dc = int(it.get("dc") or 15)
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())  # R-GLS-047
    r = check.ability_check(mod=stealth_mod, prof=prof,
                            proficient=True, dc=dc, circ=exh_penalty)
    return {"kind": "hide", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc,
            "effect": "隐蔽成功" if r.success else "被发现"}


def _resolve_search(ch, it) -> dict:
    """搜索：感知(察觉)或智力(调查)检定 vs DC。R-CHK-010"""
    ability = it.get("ability") or "wis"
    mod = ch.ability_mod(ability)
    prof = ch.prof()
    dc = int(it.get("dc") or 15)
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())  # R-GLS-047
    r = check.ability_check(mod=mod, prof=prof, proficient=True, dc=dc, circ=exh_penalty)
    return {"kind": "search", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "ability": ability}


def _resolve_grapple(ch, it) -> dict:
    """擒抱：力量或敏捷竞技检定 vs 目标力量/敏捷竞技。R-CMB-017"""
    ability = it.get("ability") or "str"
    mod = ch.ability_mod(ability)
    prof = ch.prof()
    dc = int(it.get("dc") or 10)
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())  # R-GLS-047
    r = check.ability_check(mod=mod, prof=prof, proficient=True, dc=dc, circ=exh_penalty)
    return {"kind": "grapple", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "ability": ability,
            "effect": "擒抱成功" if r.success else "擒抱失败"}


def _resolve_shove(ch, it) -> dict:
    """推撞：力量或敏捷竞技检定,让目标倒地或移开。R-CMB-017"""
    ability = it.get("ability") or "str"
    mod = ch.ability_mod(ability)
    prof = ch.prof()
    dc = int(it.get("dc") or 10)
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())  # R-GLS-047
    r = check.ability_check(mod=mod, prof=prof, proficient=True, dc=dc, circ=exh_penalty)
    shove_type = it.get("shove_type", "prone")
    return {"kind": "shove", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "ability": ability,
            "shove_type": shove_type,
            "effect": f"推撞成功({shove_type})" if r.success else "推撞失败"}


def _resolve_study(ch, it) -> dict:
    """研究：智力(奥秘/历史/调查/自然/宗教) 检定 vs DC。R-CHK-010

    Director 分类器会发出 study 动作，resolve 必须有对应分派，否则 NameError。
    """
    ability = it.get("ability") or "int"
    mod = ch.ability_mod(ability)
    prof = ch.prof()
    dc = int(it.get("dc") or 15)
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())  # R-GLS-047
    r = check.ability_check(mod=mod, prof=prof, proficient=True, dc=dc, circ=exh_penalty)
    return {"kind": "study", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "ability": ability}


def _resolve_opportunity_attack(ch, it) -> dict:
    """借机攻击：目标离开触及范围时触发的反应近战攻击。R-CMB-024

    本质是一次近战武器攻击，复用 _resolve_attack 逻辑（已含力竭惩罚/条件优劣势），
    仅改 kind 以便 narrate/apply 区分。
    Director 分类器会发出 opportunity_attack 动作，resolve 必须有对应分派，否则 NameError。
    """
    out = _resolve_attack(ch, it)
    out["kind"] = "opportunity_attack"
    return out


def _resolve_start_combat(state: GameState, ch, it) -> dict:
    """开始战斗：roll_initiative + persist。R-CMB-002

    敌人 HP 从 intent.enemies[].hp_max 读取（由 classify 从怪物数据/LLM 填入），
    未给则用保守默认 7（约一只低 CR 小怪），使战斗可分出胜负。
    玩家参战者 hp 从 Character 同步到 Combatant（角色卡仍为权威来源）。
    """
    enemies = it.get("enemies") or [{"name": "敌人", "dex_mod": 1, "side": "enemy"}]
    combatants = [cmb.Combatant(cid=str(state["character_id"]), name=ch.name,
                                dex_mod=ch.ability_mod("dex"), side="player",
                                is_player=True, hp=ch.hp_current, hp_max=ch.hp_max)]
    for i, e in enumerate(enemies):
        _ename = e.get("name", f"敌人{i}")
        # B4: 怪物属性优先从 data.monsters 表查（按 name）；intent 显式值可覆盖表值。
        # 表未收录则 base 为空，落到保守默认（7/4/1d6+2/挥砍，与原行为一致）。
        # 详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段B4
        base: dict = {}
        try:
            from ..data import monsters as _mon
            _m = _mon.get_monster(_ename)
            if _m:
                base = _m.to_combatant_dict()
        except Exception:
            pass
        base.update({k: e[k] for k in ("hp_max", "hp", "attack_bonus", "damage_dice",
                     "damage_type", "dex_mod", "speed") if k in e})
        ehp = int(base.get("hp_max", base.get("hp", 7)) or 7)
        eab = int(base.get("attack_bonus", 4) or 4)
        edd = base.get("damage_dice") or "1d6+2"
        edt = base.get("damage_type") or "挥砍"
        edex = int(base.get("dex_mod", 0))
        espd = int(base.get("speed", 30))
        combatants.append(cmb.Combatant(cid=f"e{i}", name=_ename, dex_mod=edex,
                                        side="enemy", is_player=False,
                                        hp=ehp, hp_max=ehp,
                                        attack_bonus=eab, damage_dice=edd, damage_type=edt,
                                        speed=espd))
    combat = cmb.Combat()
    order = cmb.roll_initiative(combatants)                  # R-CMB-002
    combat.participants = combatants
    combat.initiative_order = order
    combat.round = 1; combat.current_index = 0; combat.active = True
    cs = store.save_combat(state["campaign_id"], combat)     # persist
    return {"dice": {"kind": "start_combat",
                     "initiative_order": [{"name": c.name, "init": c.initiative,
                                           "side": c.side} for c in order]},
            "combat": {"active": True, "combat_id": cs.id, "round": 1,
                       "current_index": 0,
                       "combatants": [{"name": c.name, "init": c.initiative, "side": c.side,
                                       "cid": c.cid, "hp": c.hp, "hp_max": c.hp_max} for c in order]}}


# ──────────────────────────────────────────────────────────────────────────
# 节点：narrate / apply
# ──────────────────────────────────────────────────────────────────────────

def narrate(state: GameState) -> dict:
    """LLM 叙事 + 结构化状态变更（掷骰结果固定，不可改；在当前场景中叙事）。

    注入三层记忆到 prompt:
      ① 工作记忆 — 最近6回合对话原文 (store.get_recent_logs)
      ② 中期记忆 — Campaign.rolling_summary 摘要 (store.get_summary)
      ③ 长期记忆 — 跨Session语义检索 (brain.memory.retrieve_memories)
    """
    dice = state.get("dice", {})
    dig = _digest(state.get("evidence", []))
    combat_ctx = state.get("combat", {})
    camp_id = state.get("campaign_id", 0)
    scene_ctx = world.scene_context(camp_id)  # 在场景中叙事而非虚空

    # ① 工作记忆：最近6回合对话（时间正序）
    recent_logs = store.get_recent_logs(camp_id, n=6) if camp_id else []
    history = "\n".join(
        f"[回合] 玩家: {log.player_input[:80]} → DM: {log.dm_output[:80]}"
        for log in recent_logs
    ) if recent_logs else "(无历史对话)"

    # ② 中期记忆：rolling_summary（截取前500字防止prompt过长）
    #    优先注入前情提要（跨Session），其次注入本Session摘要
    rolling_summary = store.get_summary(camp_id) if camp_id else ""
    summary_text = rolling_summary[:500] if rolling_summary else "(无摘要)"

    # ②b 前情提要：跨Session浓缩摘要（从rolling_summary中提取[前情提要]块）
    recap_text = ""
    if camp_id:
        from ..brain.memory import get_recap
        try:
            recap_text = get_recap(camp_id)
        except Exception as e:
            _log.debug("前情提要检索失败 campaign=%s: %s", camp_id, e)

    # ③ 长期记忆：跨Session语义检索（top-5，重要性加权+时间衰减）
    long_term_ctx = ""
    if camp_id:
        from ..brain.memory import retrieve_memories
        try:
            query = state.get("player_input", "")[:100]
            memories = retrieve_memories(camp_id, query, top_k=20)
            if memories:
                long_term_ctx = "相关记忆(长期):\n" + "\n".join(
                    f"- {m['event']} [重要:{m['importance']}]"
                    for m in memories
                )
        except Exception as e:
            _log.debug("长期记忆检索失败 campaign=%s: %s", camp_id, e)  # 不阻断叙事

    prompt = (
        "你是D&D 5E DM。依据【掷骰结果(硬性,已由代码算出,不可更改)】与规则,在当前场景中以第二人称简洁叙述(2-4句)。\n"
        "遵循叙事技巧:简洁、多感官氛围、区分选项、不臆测角色行动。\n\n"
        f"前情提要:\n{recap_text}\n\n" if recap_text else
        "你是D&D 5E DM。依据【掷骰结果(硬性,已由代码算出,不可更改)】与规则,在当前场景中以第二人称简洁叙述(2-4句)。\n"
        "遵循叙事技巧:简洁、多感官氛围、区分选项、不臆测角色行动。\n\n"
    )
    prompt += (
        f"本局摘要:\n{summary_text}\n\n"
        f"近期对话(工作记忆):\n{history}\n\n"
        f"{long_term_ctx}\n\n"
        f"掷骰结果: {json.dumps(dice, ensure_ascii=False)}\n"
        f"战斗: {json.dumps(combat_ctx, ensure_ascii=False)}\n"
        f"{scene_ctx}\n"
        f"规则摘要:\n{dig}\n玩家输入: {state['player_input']}\n"
        "然后输出结构化状态变更 + 更新后的场景叙事。只输出JSON: "
        '{"narration":"...", "state_changes":[{"target":"怪物名或character_id","field":"hp","delta":-N,"reason":"..."}], '
        '"scene_update":"行动后场景的新状态叙事(1-2句,更新场景)"}\n'
        "然后给出3个玩家下一步可做的行动选项(区分细节,如DMG区分选项)。\n"
        "只输出JSON: {\"narration\":\"叙事\",\"state_changes\":[],\"scene_update\":\"\",\"action_options\":[\"选项1\",\"选项2\",\"选项3\"]}\n"
    )
    raw = llm.chat("你是D&D DM,严格依据掷骰结果叙述,不改动数值。只输出JSON。", prompt, temperature=0.4)
    obj = _extract_json(raw)
    narration = obj.get("narration") or _strip_to_text(raw)
    return {"narration": narration,
            "state_changes": obj.get("state_changes", []),
            "scene_update": obj.get("scene_update", ""),
            "action_options": obj.get("action_options", [])}


def _apply_damage_to_character(ch, dmg: int, state: GameState) -> dict:
    """对角色施加伤害，含死亡/过量致死/专注豁免判定。

    规则: R-DMG-007/009/014/017/018 + R-SPL-020 专注维持
    """
    result = {"dmg": dmg, "died": False, "death_failures_added": 0,
              "concentration_save": None}
    old_hp = ch.hp_current

    # 先扣临时HP再扣HP（R-DMG-009）
    nhp, ntemp = damage.apply_damage_to_hp(ch.hp_current, ch.temp_hp, ch.hp_max, dmg)
    ch.hp_current = nhp
    ch.temp_hp = ntemp

    # R-DMG-014 过量伤害致死（HP降到0且余量≥上限 → 即死）
    if ch.hp_current == 0 and damage.check_massive_damage(old_hp, ch.hp_max, dmg):
        ch.dead = True
        result["died"] = True
        result["death_reason"] = "过量伤害"
        return result
    # R-DMG-013 HP上限归0则死亡
    if ch.hp_current == 0 and damage.check_hp_max_zero_death(ch.hp_max):
        ch.dead = True
        result["died"] = True
        result["death_reason"] = "HP上限归零"
        return result

    # R-DMG-018 HP为0时受伤害 → 记死亡豁免失败（重击两次）
    if old_hp == 0 and ch.hp_current == 0 and not ch.dead:
        tracker = ch.to_death_tracker()
        is_crit = bool(state.get("dice", {}).get("crit"))
        ds = damage.damage_at_zero_hp(tracker, dmg, is_crit, ch.hp_max)
        ch.apply_death_tracker(tracker)
        result["death_failures_added"] = ds.get("failures_added", 0)
        if ds.get("dead"):
            ch.dead = True
            result["died"] = True

    # R-SPL-020 专注豁免：受伤时体质豁免维持专注
    # concentrating_on 由 _resolve_cast 写入 dice（专注法术）；亦兼容旧 intent 写法
    conc_on = state.get("dice", {}).get("concentrating_on") or state.get("intent", {}).get("concentrating_on")
    if conc_on and not ch.dead:
        conc_dc = cmb.concentration_save_dc(dmg)
        # 体质豁免熟练与否取决于职业（法师/牧师等默认不熟练，不应加 PB）
        con_proficient = ch.char_class in CLASS_CON_PROFICIENCY
        sv = check.saving_throw(mod=ch.ability_mod("con"), prof=ch.prof(),
                                proficient=con_proficient, dc=conc_dc)
        result["concentration_save"] = {
            "spell": conc_on, "dc": conc_dc, "success": sv.success, "d20": sv.d20}
        if not sv.success:
            # 失去专注：清 concentrating_on，后续受伤不再触发 con 豁免
            state.get("dice", {})["concentrating_on"] = None
            state.get("intent", {})["concentrating_on"] = None

    return result


def _apply_healing_to_character(ch, heal: int) -> dict:
    """对角色施加治疗，含死亡计数归零。

    规则: R-DMG-020 治疗不超上限 + R-ADD-008 恢复HP时死亡豁免计数归零
    """
    was_dying = ch.hp_current == 0 and not ch.dead
    ch.hp_current = damage.apply_healing(ch.hp_current, ch.hp_max, heal)
    result = {"heal": heal, "hp_after": ch.hp_current}
    if was_dying and ch.hp_current > 0:
        tracker = ch.to_death_tracker()
        damage.reset_death_counts_on_recovery(tracker)
        ch.apply_death_tracker(tracker)
        result["death_counts_reset"] = True
    return result


def _run_monster_turn(monster, ch, state) -> dict:
    """怪物回合自动攻击玩家（确定性，不调 LLM）。

    命中即伤害，经 _apply_damage_to_character 应用（含死亡豁免/专注打断/过量致死）。
    用于 REST 路径自动结算连续怪物回合，使玩家可被打到 0HP→触发死亡豁免链路。
    """
    atk = check.attack_roll(bonus=monster.attack_bonus, ac=ch.ac)
    ev = {"monster": monster.name, "hit": atk.hit, "damage": 0,
          "damage_type": monster.damage_type or "挥砍", "d20": atk.d20,
          "attack_total": atk.total, "player_hp_after": ch.hp_current}
    if atk.hit:
        dr = damage.roll_damage(damage.DamageRequest(
            dice_expr=monster.damage_dice or "1d6+2",
            damage_type=monster.damage_type or "挥砍",
            ability_mod=0, add_mod=False))
        ev["damage"] = dr.final
        res = _apply_damage_to_character(ch, dr.final, state)
        ev["player_hp_after"] = ch.hp_current
        ev["died"] = res.get("died", False)
        ev["concentration_save"] = res.get("concentration_save")
    return ev


def _render_monster_events(events: list) -> str:
    """把怪物回合事件渲染为追加到 narration 的文本。"""
    parts = []
    for ev in events:
        if ev.get("hit"):
            line = (f"【{ev['monster']}回合】攻击命中你（d20={ev['d20']}，攻击总值"
                    f"{ev['attack_total']}），造成{ev['damage']}点{ev['damage_type']}伤害，"
                    f"你当前HP {ev['player_hp_after']}。" +
                    ("你倒下了！" if ev.get("died") else ""))
        else:
            line = f"【{ev['monster']}回合】攻击未命中你（d20={ev['d20']}）。"
        cs = ev.get("concentration_save")
        if cs:
            line += f" 专注豁免DC{cs.get('dc')}（{cs.get('spell')}）d20={cs.get('d20')}→" + \
                    ("维持专注。" if cs.get("success") else "失去专注！")
        parts.append(line)
    return "\n" + "\n".join(parts)


def apply_node(state: GameState) -> dict:
    """应用状态变更 + 持久化（HP/法术位/日志/summary + 战斗轮次推进 + 死亡豁免/专注）。"""
    cid = state.get("character_id")
    camp = state.get("campaign_id")
    ch = store.get_character(cid) if cid else None
    combat_active = state.get("combat", {}).get("active")
    monster_events: list = []  # 怪物回合事件（apply 末尾回写 narration）
    narration_changed = False                # 死亡豁免/怪回合等是否追加了 narration
    # 玩家主动结束战斗 → 持久化 active=False（之前仅 state 标记未存盘，致后续轮 _load_combat
    # 仍 active=True，长休等动作会被怪回合干扰）
    if camp and state.get("dice", {}).get("kind") == "end_combat":
        try:
            _c = store.load_combat(camp)
            _c.active = False
            store.save_combat(camp, _c)
        except Exception as e:
            _log.warning("结束战斗持久化失败 campaign=%s: %s", camp, e)
    narration_changed = False                # 死亡豁免/怪回合等是否追加了 narration

    # 1) 结构化状态变更：玩家角色 HP / temp_hp / conditions
    for chg in state.get("state_changes", []):
        target = str(chg.get("target"))
        field = chg.get("field")
        try:                                   # LLM 偶发给非数字 delta（如 "unconscious"）
            delta = int(chg.get("delta", 0))
        except (ValueError, TypeError):
            continue
        if target != str(cid) or not ch:
            continue
        # use_item 轮的治疗由 step2.8 统一应用（避免与 narrate 的治疗 state_changes 叠加致恢复过多）
        if state.get("dice", {}).get("kind") == "use_item" and field == "hp" and delta > 0:
            continue
        if field == "hp":
            if delta < 0:
                _apply_damage_to_character(ch, -delta, state)
            elif delta > 0:
                _apply_healing_to_character(ch, delta)
        elif field == "temp_hp" and delta > 0:
            ch.temp_hp = damage.grant_temp_hp(ch.temp_hp, delta)

    # 2) 施法消耗法术位 R-SPL-002
    if ch and state.get("dice", {}).get("kind") == "cast":
        lvl = state["dice"].get("spell_level", 1)
        slots = ch.spell_slots if hasattr(ch, "spell_slots") else {}
        # 直接操作 spell_slots_json
        import json as _j
        try:
            sd = _j.loads(ch.spell_slots_json)
        except Exception as e:
            _log.debug("法术位 JSON 解析失败 cid=%s，回退为空: %s", cid, e)
            sd = {}
        if sd.get(str(lvl), 0) > 0:
            sd[str(lvl)] -= 1
        ch.spell_slots_json = _j.dumps(sd)

    # 2.5) 休息收益落盘 R-GLS-014 短休 / R-GLS-015 长休
    # rest_mod 只计算不修改角色卡；此处将 HP 恢复 / 力竭 -1 / 临时HP清空 写回 Character。
    if ch and state.get("dice", {}).get("kind") == "rest":
        _apply_rest_to_character(ch, state["dice"])

    # 2.6) 升级收益落盘 R-DM-043
    # _resolve_levelup 已对纯字典计算；此处把等级/HP 增量写回 Character。
    if ch and state.get("dice", {}).get("kind") == "levelup":
        _apply_levelup_to_character(ch, state["dice"])

    # 2.7) 社交态度持久化 R-DM-047
    # _resolve_social 已累加连续计数并判定态度转换；此处写回 Scene.npcs，
    # 使态度与连续成功/失败计数跨回合累积，态度转换阈值真正可触发。
    if camp and state.get("dice", {}).get("kind") == "social":
        ds_social = state["dice"]
        try:
            sc = store.get_scene(camp)
            if sc:
                npcs = sc.npcs
                name = ds_social.get("npc_name")
                new_att = ds_social.get("new_attitude") or ds_social.get("npc_attitude")
                cs = ds_social.get("consec_success", 0)
                cf = ds_social.get("consec_failure", 0)
                updated = False
                for n in npcs:
                    if n.get("name") == name:
                        n["attitude"] = new_att
                        n["success_count"] = cs
                        n["failure_count"] = cf
                        updated = True
                        break
                if not updated and name:
                    npcs.append({"name": name, "attitude": new_att, "role": "",
                                 "success_count": cs, "failure_count": cf})
                sc.set_npcs(npcs)
                store.save_scene(sc)
        except Exception as e:
            _log.warning("社交态度持久化失败 campaign=%s: %s", camp, e)

    # 2.8) use_item 治疗物品落盘（治疗药水等，打通 0HP倒下→喝药水→恢复HP+死亡计数归零）
    if ch and state.get("dice", {}).get("kind") == "use_item":
        heal = int(state["dice"].get("heal", 0) or 0)
        if heal > 0:
            _apply_healing_to_character(ch, heal)

    if ch:
        store.save_character(ch)

    # 3) 战斗轮次推进 R-CMB-001/004 + 死亡豁免 R-DMG-017 + 怪物 HP 应用/判结束
    if combat_active and camp:
        try:
            combat = store.load_combat(camp)
            # 3a) 应用 state_changes 到参战者 HP（怪物 target；玩家自身 HP 已在 step1
            #     落到 Character）。LLM 生成的 target 常用怪物名字而非 cid，故先按 cid
            #     精确匹配，否则按 name 匹配第一个未死敌方。participants 与 initiative_order
            #     反序列化后是独立副本，找到目标后需双写。
            _enemy_damaged = False  # 追踪 LLM state_changes 是否已对敌方造成 hp 伤害（兜底用）
            for chg in state.get("state_changes", []):
                tgt = str(chg.get("target")); field = chg.get("field")
                try:
                    delta = int(chg.get("delta", 0))
                except (ValueError, TypeError):
                    continue
                if field != "hp" or delta == 0 or tgt == str(cid):
                    continue
                target_cid = None
                for _lst in (combat.participants, combat.initiative_order):
                    for _c in _lst:
                        if _c.cid == tgt and not _c.is_player:
                            target_cid = _c.cid; break
                    if target_cid: break
                if target_cid is None:
                    for _lst in (combat.participants, combat.initiative_order):
                        for _c in _lst:
                            if not _c.is_player and _c.name == tgt and not _c.dead:
                                target_cid = _c.cid; break
                        if target_cid: break
                if target_cid:
                    for _lst in (combat.participants, combat.initiative_order):
                        for _c in _lst:
                            if _c.cid == target_cid:
                                _c.hp = max(0, _c.hp + delta)
                                if _c.hp <= 0:
                                    _c.dead = True
                    if delta < 0:
                        _enemy_damaged = True
            # 3a-deterministic) 伤害应用兜底：玩家攻击/法术命中造成伤害时，若 LLM 的
            # state_changes 未把该伤害落到任何敌方参战者（LLM 偶发漏给 state_changes、
            # 或 target 用了既非 cid 也非 name 的串），由代码直接把 dice.damage 扣到目标
            # 敌人，保证战斗可分出胜负——伤害数值本就由 resolve 纯代码掷出，不应依赖
            # LLM 复述（R-DMG-001 / R-CMB-029）。
            _dk = state.get("dice", {}).get("kind")
            _dr = state.get("dice", {})
            if (combat.active and not _enemy_damaged
                    and _dk in ("attack", "opportunity_attack", "cast")
                    and int(_dr.get("damage") or 0) > 0):
                _dmg_val = int(_dr["damage"])
                _tgt_name = state.get("intent", {}).get("target_name", "")
                _fallback = None
                for _lst in (combat.participants, combat.initiative_order):
                    for _c in _lst:
                        if (not _c.is_player and not _c.dead and _c.hp > 0
                                and _tgt_name and _c.name == _tgt_name):
                            _fallback = _c.cid; break
                    if _fallback: break
                if _fallback is None:
                    for _lst in (combat.participants, combat.initiative_order):
                        for _c in _lst:
                            if not _c.is_player and not _c.dead and _c.hp > 0:
                                _fallback = _c.cid; break
                        if _fallback: break
                if _fallback:
                    for _lst in (combat.participants, combat.initiative_order):
                        for _c in _lst:
                            if _c.cid == _fallback:
                                _c.hp = max(0, _c.hp - _dmg_val)
                                if _c.hp <= 0:
                                    _c.dead = True
            # 3b) 同步玩家参战者 HP（角色卡为权威）
            if ch:
                for _lst in (combat.participants, combat.initiative_order):
                    for _c in _lst:
                        if _c.is_player and _c.cid == str(cid):
                            _c.hp = ch.hp_current; _c.dead = ch.dead
            # 3c) 判战斗结束 R-CMB-001（全灭则 active=False）
            cmb.check_combat_end(combat)
            # 3d) 死亡豁免（玩家 0HP 倒下且战斗中，每轮投一次；非稳定/非死亡）
            # 不依赖 current==玩家：REST 自动结算怪回合后 current 可能停在怪，
            # 但玩家倒下后每轮仍应投死亡豁免（R-DMG-017）。
            if (combat.active and ch and ch.hp_current == 0
                    and not ch.dead and not ch.stable):
                tracker = ch.to_death_tracker()
                ds = damage.death_save(tracker)
                ch.apply_death_tracker(tracker)
                # R-DMG-017 天然20：恢复1HP并恢复意识（之前 ds 返回被丢弃致仍停0HP）
                regain = int(ds.get("regain_hp", 0))
                if regain:
                    ch.hp_current = max(ch.hp_current, regain)
                # 死亡豁免结果回写 narration（供玩家可见）
                roll = ds.get("roll", 0)
                if regain:
                    ds_text = f"【死亡豁免】d20={roll}，天然20！恢复1HP并苏醒。"
                elif ds.get("stable"):
                    ds_text = f"【死亡豁免】d20={roll}，累计3次成功，伤势稳定。"
                elif ds.get("dead"):
                    ds_text = f"【死亡豁免】d20={roll}，累计3次失败，你死了。"
                elif roll >= 10:
                    ds_text = f"【死亡豁免】d20={roll}≥10成功（成功{tracker.successes}/失败{tracker.failures}）。"
                else:
                    ds_text = f"【死亡豁免】d20={roll}<10失败（成功{tracker.successes}/失败{tracker.failures}）。"
                state["narration"] = (state.get("narration", "") or "") + "\n" + ds_text
                narration_changed = True
                store.save_character(ch)
                for _lst in (combat.participants, combat.initiative_order):
                    for _c in _lst:
                        if _c.is_player and _c.cid == str(cid):
                            _c.hp = ch.hp_current; _c.dead = ch.dead
            # 3e) 推进回合 + 自动结算连续怪物回合（REST 怪物 AI）
            # 玩家逃跑脱战检定：disengage/dash 后掷 d20+dex vs DC(10+敌方存活数*2)，
            # 成功则脱离战斗（避免被动挨打到死；5E逃跑由DM判定，此为确定性简化）
            _dk = state.get("dice", {}).get("kind")
            if combat.active and _dk in ("disengage", "dash") and ch and ch.hp_current > 0:
                _alive_e = sum(1 for c in combat.participants
                               if c.side == "enemy" and not c.dead and c.hp > 0)
                _flee_dc = 10 + _alive_e * 2
                _flee_roll = engine_dice.roll_die(20)
                if _flee_roll + ch.ability_mod("dex") >= _flee_dc:
                    combat.active = False
                    state["narration"] = (state.get("narration", "") or "") + \
                        f"\n【脱战】你成功摆脱追击逃离战斗（d20={_flee_roll}+dex vs DC{_flee_dc}）！"
                    narration_changed = True
                    store.save_combat(camp, combat)
            if combat.active:
                cmb.advance_turn(combat)               # 玩家行动后推进到下一参战者
            monster_events = []
            while combat.active and ch:
                cur = cmb.current_combatant(combat)
                if cur is None or cur.is_player or cur.dead or cur.hp <= 0:
                    break  # 轮到玩家或怪物已倒下 → 停止自动结算
                # 怪物回合：攻击玩家（玩家已倒下则跳过攻击）
                if ch.hp_current > 0 and not ch.dead:
                    ev = _run_monster_turn(cur, ch, state)
                    monster_events.append(ev)
                    for _lst in (combat.participants, combat.initiative_order):
                        for _c in _lst:
                            if _c.is_player and _c.cid == str(cid):
                                _c.hp = ch.hp_current; _c.dead = ch.dead
                if ch.hp_current <= 0 or ch.dead:
                    cmb.check_combat_end(combat)
                    break  # 玩家倒下，停止；下回合玩家开始时由 3d 投死亡豁免
                cmb.check_combat_end(combat)
                if not combat.active:
                    break
                cmb.advance_turn(combat)
            if ch:
                store.save_character(ch)
            store.save_combat(camp, combat)
            # 把怪物回合叙述追加到当轮 narration（apply 在 narrate 之后，可改 state）
            if monster_events:
                state["narration"] = (state.get("narration") or "") + _render_monster_events(monster_events)
            # 刷新响应战斗状态为「应用后」快照：state["combat"] 此前是 init 的回合开始
            # 快照（_load_combat 在 run() 入口读取），apply 内修改并保存的是另一个 combat
            # 对象，二者未同步 → /chat 响应与前端战斗追踪器一直显示旧 HP，玩家当轮攻击
            # 结果（命中/伤害/击杀/回合推进）不可见。这里把保存后的 combat 写回 state。
            state["combat"] = {
                "active": combat.active, "combat_id": None, "round": combat.round,
                "current_index": combat.current_index,
                "combatants": [_combatant_view(_c) for _c in combat.initiative_order]}
        except Exception as e:  # 不再静默吞错：记日志便于排查回合推进/死亡豁免故障
            _log.warning("战斗轮次推进/死亡豁免失败 campaign=%s cid=%s: %s", camp, cid, e)

    # 4) 持久化日志（rolling_summary 不再逐回合追加，由步骤6每10回合压缩）
    if camp:
        store.append_log(camp, player_input=state.get("player_input", ""),
                         dm_output=state.get("narration", ""),
                         dice_rolls=[state.get("dice", {})])

    # 5) 场景推进：更新 Scene.situation（行动后场景叙事）
    scene_update = state.get("scene_update", "")
    if scene_update and camp:
        sc = store.get_scene(camp)
        if sc:
            sc.situation = scene_update
            store.save_scene(sc)

    # 5.5) 系统自动遇敌（R-DM 随机遇遇）：玩家无权召唤怪物/开战，故遇敌由系统判定。
    #      玩家在探索/旅行/叙事推进类动作后，DM 可能引入遭遇（确定性掷骰，非玩家触发）。
    _explore_kinds = ("explore", "travel", "ability_check", "other", "search", "study")
    if (camp and ch and not combat_active and not ch.dead
            and state.get("dice", {}).get("kind") in _explore_kinds):
        try:
            enc = exploration_mod.random_encounter_check()
            if enc.triggered:
                # B5: 按角色等级(CR段)从 monsters.py 选遇遇怪池，取真实数值，不再永远哥布林。
                # 详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段B5
                try:
                    from ..data import monsters as _mon
                    _pool = _mon.pick_encounter_pool(ch.level)
                    _m = _pool[engine_dice.roll_die(len(_pool)) - 1] if _pool else None
                except Exception:
                    _m = None
                n = 1 if engine_dice.roll_die(2) == 1 else 2
                if _m:
                    _md = _m.to_combatant_dict()
                    enemies = [dict(_md) for _ in range(n)]
                    _enc_name = _m.name
                else:  # monsters 表不可用时的保守兜底
                    enemies = [{"name": "哥布林", "dex_mod": 2, "side": "enemy",
                                "hp_max": 7, "attack_bonus": 4,
                                "damage_dice": "1d6+2", "damage_type": "挥砍"}
                               for _ in range(n)]
                    _enc_name = "哥布林"
                enc_state = {"character_id": cid, "campaign_id": camp}
                enc_dice = _resolve_start_combat(enc_state, ch,
                                                 {"action_type": "start_combat", "enemies": enemies})
                state["combat"] = enc_dice.get("combat", {})
                state["narration"] = (state.get("narration", "") or "") + \
                    f"\n【遭遇】{n}只{_enc_name}从暗处窜出，向你扑来！战斗开始（先攻已掷）。"
                narration_changed = True
        except Exception as e:
            _log.warning("系统自动遇敌失败 campaign=%s: %s", camp, e)

    # 6) 记忆处理已移至 API 层异步执行，不阻塞图完成。
    #    见 api/main.py:chat() 和 api/ws.py:on_action() 中的 _async_memory_process()。
    # 怪物回合叙述已在 3e 追加到 state["narration"]；LangGraph 只 merge 节点返回值，
    # 故此处显式回写 narration（apply 内直接改 state 在 LangGraph 不一定生效）。
    if narration_changed or monster_events:
        return {"narration": state.get("narration", ""), "combat": state.get("combat", {})}
    # 战斗回合若被处理，state["combat"] 已在上文刷新为「应用后」快照，需回写以覆盖
    # init 的回合开始值，否则 /chat 响应仍返回旧 combat（玩家看不到当轮攻击结果）。
    if combat_active:
        return {"combat": state.get("combat", {})}
    return {}


# ──────────────────────────────────────────────────────────────────────────
# 条件边 + 构图
# ──────────────────────────────────────────────────────────────────────────

def _after_verify(state: GameState) -> str:
    """HITL 优先：consequential 动作 + hitl → confirm（让 DM 确认，无论 verify ok 否）。
    other 无判定直接 resolve；非 hitl 时 verify 失败→retrieve_retry。"""
    at = state.get("intent", {}).get("action_type")
    if at in ("other", "end_combat"):
        return "resolve"  # 无判定，跳过 HITL
    if state.get("hitl"):
        return "confirm"   # HITL 开 → 一律让 DM 确认（可靠触发 interrupt）
    if not state.get("verification", {}).get("ok", True):
        return "retrieve_retry"
    return "resolve"


def _after_retry(state: GameState) -> str:
    """重检索后→resolve（终态，避免死循环）。"""
    return "resolve"


def _after_confirm(state: GameState) -> str:
    """DM 确认→resolve；驳回→retrieve_retry（重检索后 resolve，无循环）。"""
    return "resolve" if state.get("confirmed") else "retrieve_retry"


def build_graph():
    """构建多智能体协作图。

    节点映射:
      classify     → Director Agent (agents.director.classify_intent)
      retrieve     → Rule Judge Agent (agents.rule_judge.retrieve)
      retrieve_retry → Rule Judge Agent (agents.rule_judge.retrieve_retry)
      verify       → Rule Judge Agent (agents.rule_judge.verify)
      confirm      → HITL interrupt (本文件)
      resolve      → 确定性骰子分派 (本文件)
      narrate      → LLM 叙事 + 四层记忆注入 (本文件)
      apply        → 状态应用 + 持久化 + 记忆处理 (本文件)
    """
    g = StateGraph(GameState)
    g.add_node("classify", _director_classify)       # Director Agent
    g.add_node("retrieve", _judge_retrieve)          # Rule Judge Agent
    g.add_node("verify", _judge_verify)              # Rule Judge Agent
    g.add_node("retrieve_retry", _judge_retrieve_retry)  # Rule Judge Agent
    g.add_node("confirm", confirm)
    g.add_node("resolve", resolve)
    g.add_node("narrate", narrate)
    g.add_node("apply", apply_node)
    g.set_entry_point("classify")
    g.add_edge("classify", "retrieve")
    g.add_edge("retrieve", "verify")
    g.add_conditional_edges("verify", _after_verify,
                            {"retrieve_retry": "retrieve_retry", "confirm": "confirm", "resolve": "resolve"})
    g.add_edge("retrieve_retry", "resolve")           # 重检索→终态resolve
    g.add_conditional_edges("confirm", _after_confirm,
                            {"resolve": "resolve", "retrieve_retry": "retrieve_retry"})
    g.add_edge("resolve", "narrate")
    g.add_edge("narrate", "apply")
    g.add_edge("apply", END)
    return g.compile(checkpointer=MemorySaver())


_GRAPH = None


def get_graph():
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = build_graph()
    return _GRAPH


def run(player_input: str, campaign_id: int, character_id: int,
        thread_id: str = "default", hitl: bool = False) -> GameState:
    """跑一轮硬性判定链。HITL 启用时可能 interrupt，调用方需用 Command(resume=) 恢复。"""
    import uuid
    cfg = {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}
    init = {"player_input": player_input, "campaign_id": campaign_id,
            "character_id": character_id, "hitl": hitl,
            "intent": {}, "evidence": [], "verification": {}, "confirmed": False,
            "dice": {}, "narration": "", "state_changes": [],
            "scene_update": "", "action_options": [],
            "combat": _load_combat(campaign_id), "error": "", "summary": ""}
    return get_graph().invoke(init, config=cfg)


def run_turn(player_input: str, campaign_id: int, character_id: int,
             thread_id: str = "default", hitl: bool = False,
             responder=None) -> GameState:
    """HITL 感知的一轮：invoke，若 interrupt 则调 responder(q)->ans 恢复，循环至完成。

    responder: 可调用对象，接收 interrupt 的 question dict，返回 'y'/'n'。
               为 None 时遇到 interrupt 直接返回中断态（由调用方处理，如 API）。
    """
    from langgraph.types import Command
    cfg = {"configurable": {"thread_id": thread_id or "default"}}
    init = {"player_input": player_input, "campaign_id": campaign_id,
            "character_id": character_id, "hitl": hitl,
            "intent": {}, "evidence": [], "verification": {}, "confirmed": False,
            "dice": {}, "narration": "", "state_changes": [],
            "scene_update": "", "action_options": [],
            "combat": _load_combat(campaign_id), "error": "", "summary": ""}
    r = get_graph().invoke(init, config=cfg)
    guard = 0
    while r.get("__interrupt__") and guard < 5:
        guard += 1
        if responder is None:
            return r  # 交调用方处理（API 场景）
        v = r["__interrupt__"][0]
        q = v.value if hasattr(v, "value") else v
        ans = responder(q)
        r = get_graph().invoke(Command(resume=ans), config=cfg)
    return r


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    import os
    os.makedirs("data/saves", exist_ok=True)
    DB = store.DEFAULT_DB
    camp = store.create_campaign("P3v2联调", DB)
    # 法师角色（有法术位）测 cast
    wiz = models.Character(name="梅莉", race="高等精灵", char_class="法师", level=5, campaign_id=camp.id)
    wiz.set_abilities({"str": 8, "dex": 14, "con": 12, "int": 16, "wis": 12, "cha": 10})
    wiz.hp_max = 24; wiz.hp_current = 24; wiz.ac = 11; wiz.speed = 30
    import json as _j
    wiz.spell_slots_json = _j.dumps({"1": 4, "2": 2})  # 5级法师法术位
    wiz = store.save_character(wiz, DB)
    # 战士测 attack
    war = models.Character(name="阿拉贡", race="人类", char_class="战士", level=5, campaign_id=camp.id)
    war.set_abilities({"str": 16, "dex": 10, "con": 15, "int": 10, "wis": 12, "cha": 10})
    war.hp_max = 38; war.hp_current = 38; war.ac = 18
    war = store.save_character(war, DB)

    print("=== 1. 战士攻击 ===")
    out = run("我用长剑攻击那只AC15的哥布林", camp.id, war.id)
    print("意图:", out["intent"].get("action_type"), out["intent"].get("weapon"))
    print("骰子:", out["dice"])
    print("叙事:", out["narration"][:80])

    print("\n=== 2. 法师施法(火球术,豁免型) ===")
    out = run("我对那群哥布林施展火球术(3环,8d6火焰,敏捷豁免)", camp.id, wiz.id)
    print("意图:", out["intent"].get("action_type"), "spell_dice:", out["intent"].get("spell_dice"))
    print("骰子:", out["dice"])
    print("叙事:", out["narration"][:80])
    # 验证法术位消耗
    wiz2 = store.get_character(wiz.id)
    print("法术位3环剩余:", _j.loads(wiz2.spell_slots_json).get("3"))

    print("\n=== 3. 属性检定 ===")
    out = run("我搜寻密门(感知察觉,DC15)", camp.id, war.id)
    print("意图:", out["intent"].get("action_type"), "dc:", out["intent"].get("dc"))
    print("骰子:", out["dice"])
    print("叙事:", out["narration"][:80])

    print("\n=== 4. 开始战斗(先政) ===")
    out = run("战斗开始! 哥布林(敏捷+2)和兽人(敏捷+0)冲过来", camp.id, war.id)
    print("意图:", out["intent"].get("action_type"))
    print("骰子:", out["dice"])
    print("战斗:", out.get("combat"))
