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

import json
import logging
import os
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from langgraph.types import interrupt

# 多智能体架构接入：Director + Rule Judge 从 agents 包导入
from ..agents.director import classify_intent as _director_classify
from ..agents.director import route_action as _director_route
from ..agents.rule_judge import (
    retrieve as _judge_retrieve,
)
from ..agents.rule_judge import (
    retrieve_retry as _judge_retrieve_retry,
)
from ..agents.rule_judge import (
    verify as _judge_verify,
)
from ..data import equipment
from ..engine import check, conditions, damage
from ..engine import combat as cmb
from ..engine import dice as engine_dice
from ..knowledge import hybrid, verifier
from ..stats import store
from . import llm, world
from .state import GameState

# ── 拆分后的子模块导入 ──────────────────────────────────────────────────
from .utils import (
    extract_json as _extract_json,
    strip_to_text as _strip_to_text,
    digest as _digest,
    combatant_view as _combatant_view,
    load_combat as _load_combat,
)
from .resolvers import (
    resolve_attack as _resolve_attack,
    resolve_multi_attack as _resolve_multi_attack,
    resolve_opportunity_attack as _resolve_opportunity_attack,
    resolve_cast as _resolve_cast,
    resolve_ability_check as _resolve_ability_check,
    resolve_hide as _resolve_hide,
    resolve_search as _resolve_search,
    resolve_grapple as _resolve_grapple,
    resolve_shove as _resolve_shove,
    resolve_study as _resolve_study,
    resolve_rest as _resolve_rest,
    resolve_social as _resolve_social,
    resolve_levelup as _resolve_levelup,
    resolve_travel as _resolve_travel,
    resolve_start_combat as _resolve_start_combat,
    with_target_outcome as _with_target_outcome,
    with_encounter as _with_encounter,
    advance_game_time as _advance_game_time,
    apply_node as _apply_node_impl,
    run_monster_turn as _run_monster_turn,
    render_monster_events as _render_monster_events,
)

_log = logging.getLogger(__name__)

# ── SQLite Checkpointer（持久化，替代 MemorySaver）──────────────────────
_CHECKPOINT_DB = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "saves", "checkpoints.db")


def _make_checkpointer() -> SqliteSaver:
    """创建持久化 SQLite checkpointer。

    使用 data/saves/checkpoints.db 存储 HITL 中断状态与图执行快照，
    进程重启后可恢复中断会话。
    """
    os.makedirs(os.path.dirname(_CHECKPOINT_DB), exist_ok=True)
    conn = sqlite3.connect(_CHECKPOINT_DB, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    checkpointer.setup()
    _log.info("SQLite checkpointer 已初始化: %s", _CHECKPOINT_DB)
    return checkpointer


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
        "needs_check(true/false,DMG:仅结果不确定且失败有实质后果才掷骰;琐碎/无风险/友好NPC合理请求→false), "
        "retrieval_query(用规则原词构造的检索串:动作规范名+检定类型+DC关键词,如'徒手打击 推撞 豁免DC 8 力量 熟练')\n"
        "attack/opportunity_attack专有: weapon(武器中文名)\n"
        "cast专有: spell_name, spell_level(整数), spell_dice(如8d6), damage_type(火焰/力场/...), "
        "spell_attack(true=攻击检定型/false=豁免型), save_ability(con/dex/...目标豁免属性), "
        "target_save_bonus(目标该豁免加值,未知0), casting_ability(int/wis/cha 施法属性)\n"
        "ability_check/explore/hide/search/study专有: skill(技能名), "
        "dc(整数,DMG锚点:很容易5/容易10/中等15/困难20/极难25), proficient(true/false)\n"
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

def resolve(state: GameState) -> dict:
    """硬性骰子分派（纯代码，LLM 不参与）。"""
    it = state["intent"]
    at = it.get("action_type")
    cid = state.get("character_id")
    ch = store.get_character(cid) if cid else None
    if ch is None and at not in ("start_combat", "end_combat"):
        return {"dice": {}, "error": "角色卡不存在"}
    # 死亡/倒下行动限制（R-DMG-017）
    if ch and ch.dead:
        return {"dice": {"kind": at, "error": "你已死亡，无法行动（需复活法术）"}}
    if (ch and ch.hp_current <= 0 and not ch.dead
            and at not in ("use_item", "other")):
        return {"dice": {"kind": at, "error": "你已倒下(0HP)无法行动，只能使用治疗药水自救或等待死亡豁免"}}
    # 战斗中动作限制
    if state.get("combat", {}).get("active") and at in ("travel", "explore", "rest", "levelup"):
        return {"dice": {"kind": at, "error": "战斗中不能旅行/探索/休息/升级；逃跑用 dash/disengage，战斗用 attack/cast"}}

    # —— 免检定分支（DMG「骰子的角色」：结果确定或失败无实质后果→不掷骰自动成功）——
    # 仅限非对抗的技能类动作；攻击/施法/躲藏/擒抱等对抗动作不受影响。
    # social 的免检定在 resolve_social 内部处理（需校验存盘的 NPC 态度）。
    _AUTO_OK = ("ability_check", "explore", "search", "study")
    if at in _AUTO_OK and it.get("needs_check") is False:
        auto = {"kind": at, "auto_success": True, "success": True,
                "skill": it.get("skill", ""),
                "note": "结果确定或失败无实质后果，无需检定（DMG：仅在结果不确定时掷骰）"}
        # 探索类免检定仍可能触发遭遇（世界保持鲜活）
        return _with_encounter(state, ch, auto)

    if at == "attack":
        return _with_target_outcome(state, _resolve_multi_attack(ch, it))
    if at == "cast":
        return _with_target_outcome(state, _resolve_cast(ch, it))
    if at in ("ability_check", "explore"):
        return _with_encounter(state, ch, _resolve_ability_check(ch, it))
    if at == "start_combat":
        return _resolve_start_combat(state, ch, it)
    if at == "end_combat":
        return {"dice": {"kind": "end_combat"}, "combat": {"active": False}}
    if at == "rest":
        _r = _resolve_rest(state, ch, it)
        # 矩阵#8：休息时间推进
        _camp_r = state.get("campaign_id")
        if _camp_r and not _r.get("error"):
            _pi_r = state.get("player_input", "") or ""
            _rt = it.get("rest_type") or ("long" if ("长休" in _pi_r or "long" in _pi_r.lower()) else "short")
            _ti = _advance_game_time(_camp_r, 480 if _rt == "long" else 60)
            if _ti.get("day"):
                _r["time"] = _ti
        return {"dice": _r}
    if at == "social":
        return {"dice": _resolve_social(state, ch, it)}
    if at == "levelup":
        return {"dice": _resolve_levelup(ch, it)}
    if at == "travel":
        return _with_encounter(state, ch, _resolve_travel(state, ch, it))
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
        return _with_encounter(state, ch, _resolve_search(ch, it))
    if at == "use_item":
        item = it.get("item_name", "") or ""
        effect = it.get("item_effect", "") or ""
        pi = state.get("player_input", "") or ""
        if any(k in (item + effect + pi) for k in ("治疗", "药水", "治愈", "回血", "生命药剂")):
            _inv = getattr(ch, "inventory", []) or []
            _potion = next((n for n in _inv
                            if "药水" in n and ("治疗" in n or "治愈" in n or "疗伤" in n)), None)
            if _potion is None:
                return {"dice": {"kind": "use_item", "item": item or "治疗药水",
                                 "error": "你没有治疗药水（需先通过战利品/购买获得）"}}
            from ..engine import dice as engine_dice
            _expr = "4d4+4" if "高级" in _potion else "2d4+2"
            rolls = engine_dice.roll_dice(_expr)
            return {"dice": {"kind": "use_item", "item": _potion, "effect": effect,
                             "heal": rolls.total, "heal_rolls": rolls.dice_rolls,
                             "heal_type": "治疗药水", "consumed_item": _potion}}
        return {"dice": {"kind": "use_item", "item": item, "effect": effect}}
    if at == "grapple":
        return {"dice": _resolve_grapple(ch, it)}
    if at == "shove":
        return {"dice": _resolve_shove(ch, it)}
    if at == "study":
        return _with_encounter(state, ch, _resolve_study(ch, it))
    if at == "opportunity_attack":
        return _with_target_outcome(state, _resolve_opportunity_attack(ch, it))
    return {"dice": {}}  # other → 仅叙事


# ──────────────────────────────────────────────────────────────────────────
# 节点：narrate
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
    scene_ctx = world.scene_context(camp_id)

    # ① 工作记忆：最近6回合对话（时间正序）
    recent_logs = store.get_recent_logs(camp_id, n=6) if camp_id else []
    history = "\n".join(
        f"[回合] 玩家: {log.player_input[:80]} → DM: {log.dm_output[:80]}"
        for log in recent_logs
    ) if recent_logs else "(无历史对话)"

    # ② 中期记忆：rolling_summary（截取前500字防止prompt过长）
    rolling_summary = store.get_summary(camp_id) if camp_id else ""
    summary_text = rolling_summary[:500] if rolling_summary else "(无摘要)"

    # ②b 前情提要：跨Session浓缩摘要
    recap_text = ""
    if camp_id:
        from ..brain.memory import get_recap
        try:
            recap_text = get_recap(camp_id)
        except Exception as e:
            _log.debug("前情提要检索失败 campaign=%s: %s", camp_id, e)

    # ③ 长期记忆：跨Session语义检索
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
            _log.debug("长期记忆检索失败 campaign=%s: %s", camp_id, e)

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
        '"scene_update":"行动后场景的新状态叙事(1-2句,更新场景)", '
        '"location_change":"玩家实际移动到的新地点短名(仅当本次行动使地点发生改变,如从镇上进入矿坑/森林/洞穴;原地行动则为空串)"}\n'
        "然后给出3个玩家下一步可做的行动选项(区分细节,如DMG区分选项)。\n"
        "只输出JSON: {\"narration\":\"叙事\",\"state_changes\":[],\"scene_update\":\"\",\"location_change\":\"\",\"action_options\":[\"选项1\",\"选项2\",\"选项3\"]}\n"
    )
    # 遭遇前移 + 战斗开场叙述
    _enc = dice.get("encounter", {})
    if _enc.get("combat_started") or dice.get("kind") == "start_combat":
        _sp = dice.get("surprise") or _enc.get("surprise") or {}
        if _sp.get("surprised_side") == "player":
            _sp_text = f"②突袭判定：{_sp.get('note', '你被突袭')}（先攻劣势已体现）→"
        elif _sp.get("surprised_side") == "enemy":
            _sp_text = f"②突袭判定：{_sp.get('note', '敌人猝不及防')}（敌方先攻劣势）→"
        else:
            _sp_text = f"②突袭判定：{_sp.get('note', '双方互相察觉，无突袭')}→" if _sp else ""
        _intro = (f"探索中触发遭遇：{_enc.get('enemy_count')}只「{_enc.get('enemy_name')}」出现。"
                  if _enc.get("combat_started") else "战斗开始。")
        prompt += (
            f"\n【战斗开场】{_intro}\n"
            f"按此顺序叙述(2-4句)：①敌人如何出现/对峙如何形成(环境/声音/视觉冲击)→{_sp_text}"
            "③先攻序列(见战斗数据,逐一报出先后,序列靠前者抢占先机)→④开场对峙局势。\n"
            "玩家尚未行动，不要叙述玩家的攻击或伤害结果。\n"
        )
    # 击杀/伤害确认
    if dice.get("target_killed"):
        prompt += (f"\n【击杀确认】你的攻击/法术击杀了「{dice.get('target_name')}」"
                   f"（伤害{dice.get('damage')}≥其剩余HP{dice.get('target_hp_before')}），请叙述其倒地身亡。\n")
    elif dice.get("target_cid") and int(dice.get("damage") or 0) > 0:
        prompt += (f"\n【伤害确认】你的攻击/法术对「{dice.get('target_name')}」造成{dice.get('damage')}点伤害，"
                   "其尚未倒下——不要宣称击杀。\n")
    # 非战斗遭遇叙述
    if _enc.get("triggered") and not _enc.get("combat_started") and _enc.get("encounter_type"):
        prompt += (f"\n【非战斗遭遇】探索中触发遭遇：{_enc.get('prompt_hint', '')}\n"
                   "将其自然织入叙述(2-3句)，给出可互动的钩子，不要开战。\n")
    # 时间推进提示
    _time = dice.get("time") or {}
    if _time.get("clock"):
        prompt += (f"\n【时间推进】游戏内时间推进至第{_time.get('day')}日{_time.get('clock')}"
                   "（光影/作息变化可体现在叙述中）。\n")
    # 伤势叙述规范
    if combat_ctx.get("active"):
        _bloodied = [str(c.get("name", "")) for c in combat_ctx.get("combatants", [])
                     if c.get("side") == "enemy" and not c.get("dead")
                     and int(c.get("hp") or 0) > 0
                     and int(c.get("hp") or 0) * 2 <= int(c.get("hp_max") or 1)]
        if _bloodied:
            prompt += (f"\n【伤势叙述】以下敌人已浴血（HP过半以下）：{'、'.join(_bloodied)}"
                       "——叙述中体现其伤势外观（流血/踉跄/护住伤处），但不要透露具体HP数值。\n")
    raw = llm.chat("你是D&D DM,严格依据掷骰结果叙述,不改动数值。只输出JSON。", prompt, temperature=0.4)
    obj = _extract_json(raw)
    narration = obj.get("narration") or _strip_to_text(raw)
    return {"narration": narration,
            "state_changes": obj.get("state_changes", []),
            "scene_update": obj.get("scene_update", ""),
            "location_change": obj.get("location_change", ""),
            "action_options": obj.get("action_options", [])}


# ──────────────────────────────────────────────────────────────────────────
# 节点：apply（薄包装 → resolvers.apply）
# ──────────────────────────────────────────────────────────────────────────

def apply_node(state: GameState) -> dict:
    """应用状态变更 + 持久化。委托给 resolvers.apply.apply_node。"""
    return _apply_node_impl(state)


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
      apply        → 状态应用 + 持久化 + 记忆处理 (resolvers.apply)
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
    # 矩阵#10 轻管线：other/end_combat 无判定动作跳过 retrieve/verify 直接 resolve
    g.add_conditional_edges("classify", _director_route,
                            {"retrieve": "retrieve", "resolve": "resolve"})
    g.add_edge("retrieve", "verify")
    g.add_conditional_edges("verify", _after_verify,
                            {"retrieve_retry": "retrieve_retry", "confirm": "confirm", "resolve": "resolve"})
    g.add_edge("retrieve_retry", "resolve")           # 重检索→终态resolve
    g.add_conditional_edges("confirm", _after_confirm,
                            {"resolve": "resolve", "retrieve_retry": "retrieve_retry"})
    g.add_edge("resolve", "narrate")
    g.add_edge("narrate", "apply")
    g.add_edge("apply", END)
    return g.compile(checkpointer=_make_checkpointer())


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
    init = GameState(
        player_input=player_input, campaign_id=campaign_id,
        character_id=character_id, hitl=hitl,
        combat=_load_combat(campaign_id),
    ).model_dump()
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
    init = GameState(
        player_input=player_input, campaign_id=campaign_id,
        character_id=character_id, hitl=hitl,
        combat=_load_combat(campaign_id),
    ).model_dump()
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
    from ..stats import models
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
