"""Director Agent — 意图分类 + 路由决策中枢。

职责:
  - 接收玩家输入，用 LLM 分类意图
  - 决定路由到哪个专项 Agent（Narrator / Combat / World / Rule Judge）
  - 组装最终叙事输出

设计参考: ITMO AI-DM 8-Agent 架构的 Director 角色，
AIDM 精简为单节点 LLM 分类 → 条件路由。
"""

from __future__ import annotations

import contextlib
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


# ARC-003: LLM 不应输出的机械数值字段——即使输出也静默丢弃
_LLM_FORBIDDEN_FIELDS = frozenset({
    "target_ac", "dc", "damage", "attack_bonus",
    "saving_throw_result", "proficient", "resistance", "immunity",
})


def _strip_llm_mechanical_fields(intent: dict) -> dict:
    """移除 LLM 可能输出的机械数值字段（ARC-003）。

    所有机械数值（AC/DC/伤害/熟练等）只能由代码从状态数据计算，
    LLM 无权提供或覆盖这些值。
    """
    for key in _LLM_FORBIDDEN_FIELDS:
        intent.pop(key, None)
    return intent


# Director 的 system prompt — 意图分类器
_DIRECTOR_PROMPT = """\
你是D&D 5E意图分类器。把玩家输入分类为动作意图,只输出JSON(不要markdown)。

action_type 取值:
  attack        近战/远程攻击
  cast          施放法术
  ability_check 属性检定(力量/敏捷等)
  explore       探索/旅行
  start_combat  开始战斗(掷先攻)【仅系统(DM)触发:玩家无权召唤怪物/宣布开战】
  end_combat    结束战斗【仅系统触发:玩家逃跑用dash/disengage,战斗结束由系统判定全灭/逃跑】
  rest          短休/长休
  social        社交互动(说服/欺瞒/威吓)
  levelup       升级
  travel        旅行移动
  downtime      停工期活动(制作/研究/训练; 字段: downtime_action=start/advance/interrupt/resume, activity, days, item_value_gp)
  dash          加速(本回合额外移动)
  dodge         回避(对本角色的攻击具有劣势)
  disengage     撤离(本回合移动不引发借机攻击)
  help          协助(使盟友的下次检定具有优势)
  ready         准备动作(设定触发条件,条件满足时执行)
  hide          躲藏(固定DC15敏捷(隐匿)检定,2024版非被动察觉)
  search        搜索(感知(察觉)或智力(调查)检定)
  study         研究(智力检定:奥秘/历史/调查/自然/宗教)
  use_item      使用物品(药水/卷轴/工具)
  grapple       擒抱(目标力量或敏捷豁免vs DC=8+力调+熟练)
  shove         推撞(目标力量或敏捷豁免vs DC=8+力调+熟练,让目标倒地或移开)
  opportunity_attack 借机攻击(反应:目标离开触及范围时发动近战攻击)
  other         其他(纯叙事,不掷骰)

玩家权限约束(重要):
  玩家只能描述自己角色的动作(攻击/施法/检定/移动/休息/社交/使用物品等)。
  玩家无权设定场景、召唤怪物/NPC、宣布战斗开始或结束(这些是DM权限,由系统判断)。
  若玩家输入含场景设定或召唤怪物(如"一只哥布林窜出袭击我""NPC出现"等),
  忽略该场景设定,只提取玩家角色动作;若整句都是设定场景无角色动作,分类为 other。

通用字段:
  target_name   目标名称(自由文本,系统自动匹配到战斗参战者)
  ability       str/dex/con/int/wis/cha
  needs_check   本次行动是否需要掷骰检定(true/false),判定标准见【检定门槛】
  retrieval_query 用规则原词构造的检索串(动作规范名+检定类型+DC关键词)

检定门槛(DMG「骰子的角色」:只有结果不确定且失败有实质后果时才掷骰):
  needs_check=false(自动成功,不掷骰)的情形:
    - 任务对角色轻而易举(踹开朽烂的门/回忆常识/无压力下爬结实的梯子)
    - 失败无实质后果且可反复尝试(无时间压力、无风险的搜索/研究)
    - 社交对象态度友好(friendly)且请求合理、不损其利益(问路/闲聊/正常买卖)
    - 沿已知道路或有向导旅行(无迷路风险,免导航检定)
  attack/cast/start_combat/hide/grapple/shove/opportunity_attack 总是掷骰,不受此字段影响。

attack专有: weapon(武器中文名)
cast专有: spell_name, spell_level(整数), spell_dice(如8d6), damage_type(火焰/力场/...), \
spell_attack(true=攻击检定型/false=豁免型), save_ability(con/dex/...目标豁免属性), \
target_save_bonus(目标该豁免加值,未知0), casting_ability(int/wis/cha 施法属性)
ability_check/explore/search/study/social专有: skill(技能名)
start_combat专有: enemies(数组[{name,dex_mod,side='enemy',hp_max(整数,该怪物HP上限,如哥布林7,兽人15,未知给7)}])

注意: 不要输出 target_ac/dc/damage/proficient 等机械数值,这些由系统自动计算。
只输出JSON。"""


def _build_classify_context(state: GameState) -> str:
    """组装注入 Director 的游戏上下文（角色卡 + 场景 + 战斗 + 四层记忆）。

    复用 narrate 的四层记忆检索（工作/中期/长期/前情），并补结构化当前态
    （角色卡 equipped_weapon、场景 environment 地形、在场 NPC），让 LLM 有依据
    填 weapon/terrain/npc_name 等 key，而非瞎猜/留空→走写死兜底。
    详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段C。任何子项失败均静默跳过（不阻断分类）。
    """
    import logging
    _log = logging.getLogger(__name__)
    camp_id = state.get("campaign_id")
    cid = state.get("character_id")
    parts: list[str] = []

    # 角色卡摘要（含 equipped_weapon，attack 兜底的关键依据）
    if cid:
        try:
            from ..stats import store as _store
            ch = _store.get_character(cid)
            if ch:
                mods = " ".join(f"{k}{ch.ability_mod(k):+d}"
                                for k in ("str", "dex", "con", "int", "wis", "cha"))
                parts.append(
                    f"【角色】{ch.name} {ch.race}{ch.char_class} Lv{ch.level} "
                    f"HP{ch.hp_current}/{ch.hp_max} AC{ch.ac} 速度{ch.speed} "
                    f"属性[{mods}] 当前武器:{ch.equipped_weapon or '无(徒手)'} "
                    f"法术位:{ch.spell_slots}"
                )
        except Exception as e:
            _log.debug("classify 角色卡注入失败 cid=%s: %s", cid, e)

    # 场景摘要（environment 含地形，travel/encounter 的依据）
    if camp_id:
        try:
            from ..stats import store as _store
            sc = _store.get_scene(camp_id)
            if sc:
                npc_names = ", ".join(
                    f"{n.get('name', '')}(态度:{n.get('attitude', 'indifferent')})"
                    for n in sc.npcs[:5]) if sc.npcs else "无"
                parts.append(
                    f"【场景】地点:{sc.location or '?'} 环境/地形:{sc.environment or '?'} "
                    f"时间:{sc.time or '?'} 在场NPC:{npc_names} 情境:{(sc.situation or '')[:120]}"
                )
        except Exception as e:
            _log.debug("classify 场景注入失败 camp=%s: %s", camp_id, e)

    # 战斗状态
    combat = state.get("combat") or {}
    if combat.get("active"):
        parts.append(
            f"【战斗中】第{combat.get('round', 1)}轮 "
            f"参战者{len(combat.get('combatants', []))}人"
        )

    # 四层记忆（复用 narrate 的检索，截断控 token）
    if camp_id:
        try:
            from ..stats import store as _store
            logs = _store.get_recent_logs(camp_id, n=4)
            if logs:
                hist = "; ".join(f"{l.player_input[:40]}→{l.dm_output[:40]}" for l in logs)
                parts.append(f"【近期对话】{hist[:300]}")
        except Exception as e:
            _log.debug("classify 工作记忆注入失败 camp=%s: %s", camp_id, e)
        try:
            from ..brain.memory import get_recap, retrieve_memories
            recap = get_recap(camp_id)
            if recap:
                parts.append(f"【前情提要】{recap[:300]}")
            mems = retrieve_memories(camp_id, state.get("player_input", "")[:100], top_k=10)
            if mems:
                parts.append("【相关记忆】" + "; ".join(m["event"][:40] for m in mems[:3]))
        except Exception as e:
            _log.debug("classify 长期记忆注入失败 camp=%s: %s", camp_id, e)

    return "\n".join(parts)


# 需要明确单体目标的动作类型（匹配 target_cid 用）
_TARGETED_ACTIONS = ("attack", "opportunity_attack", "cast", "grapple", "shove", "help")


def _resolve_target_cid(intent: dict, state: GameState) -> None:
    """BUG#5/B2：从战斗状态把 target_name 确定性匹配到参战者 cid。

    LLM 的 target_name 是自由文本，战斗中按
    cid精确 → name精确 → name互含 → 唯一存活敌人 的顺序匹配，
    命中写入 intent["target_cid"]，供 resolve 预判结果、apply 确定性扣血，
    不再依赖 narrate LLM 复述 state_changes 选目标。
    匹配失败（多敌人且 name 不含）时留空，走 apply 原有兑底。
    """
    combat = state.get("combat") or {}
    if not combat.get("active"):
        return
    if (intent.get("action_type") or "") not in _TARGETED_ACTIONS:
        return
    tname = (intent.get("target_name") or "").strip()
    enemies = [c for c in combat.get("combatants", [])
               if c.get("side") != "player" and not c.get("dead")
               and int(c.get("hp") or 0) > 0]
    if not enemies:
        return
    hit = None
    if tname:
        for c in enemies:
            if c.get("cid") == tname:
                hit = c
                break
        if hit is None:
            for c in enemies:
                if c.get("name") == tname:
                    hit = c
                    break
        if hit is None:
            for c in enemies:
                cname = c.get("name") or ""
                if cname and (tname in cname or cname in tname):
                    hit = c
                    break
    if hit is None and len(enemies) == 1:
        hit = enemies[0]  # 唯一存活敌人：无需 LLM 猜
    if hit:
        intent["target_cid"] = hit.get("cid")
        if not tname:
            intent["target_name"] = hit.get("name", "")


def classify_intent(state: GameState) -> dict:
    """Director Agent: LLM 意图分类 → 结构化 intent。

    这是多智能体架构的入口节点。Director 接收玩家输入 + 游戏上下文（角色卡/场景/
    战斗/记忆），用 LLM 分类意图，返回结构化的 intent 字典。

    D2: JSON 解析失败时重试 ≤3 次，把"只输出纯JSON"反馈进 prompt（只救格式炸，
    不救信息缺失——后者靠 C 的上下文注入）。详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段D。

    Returns:
        {"intent": {...}, "error": ""}
    """
    # C1+C2: 注入上下文（记忆+当前态），让 LLM 有依据填 weapon/terrain 等 key
    ctx = _build_classify_context(state)
    user = (ctx + "\n\n玩家本轮输入: " + state["player_input"]) if ctx else state["player_input"]
    intent = _extract_json(llm.chat(_DIRECTOR_PROMPT, user, temperature=0.1))
    attempts = 0
    while not intent and attempts < 3:  # D2: 解析失败重试（只救格式炸）
        attempts += 1
        feedback = user + ("\n\n【重试%d】上次输出无法解析为JSON。"
                           "请只输出一个JSON对象，不要markdown代码块或多余文字。" % attempts)
        intent = _extract_json(llm.chat(_DIRECTOR_PROMPT, feedback, temperature=0.1))
    intent.setdefault("action_type", "other")
    # ARC-003: 剥离 LLM 可能输出的机械数值字段（AC/DC/伤害/熟练等）
    _strip_llm_mechanical_fields(intent)
    with contextlib.suppress(Exception):
        _resolve_target_cid(intent, state)   # BUG#5/B2：确定性目标匹配
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
