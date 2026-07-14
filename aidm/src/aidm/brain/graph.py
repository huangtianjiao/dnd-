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
import re

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from . import llm
from . import world
from .state import GameState
from ..knowledge import hybrid, verifier
from ..engine import check, damage, combat as cmb
from ..data import equipment
from ..stats import store, models


# ──────────────────────────────────────────────────────────────────────────
# 工具
# ──────────────────────────────────────────────────────────────────────────

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


def _digest(evidence: list[dict], n: int = 4, body: int = 320) -> str:
    return "\n---\n".join(f"[{e.get('tag')}] {e.get('body','')[:body]}" for e in evidence[:n])


def _load_combat(campaign_id: int) -> dict:
    """若战役有进行中战斗，载入 GameState.combat。"""
    try:
        c = store.load_combat(campaign_id)
        return {"active": c.active, "combat_id": None, "round": c.round,
                "current_index": c.current_index,
                "combatants": [_c.dict() if hasattr(_c, "dict") else _c
                               for _c in c.initiative_order]}
    except Exception:
        return {"active": False, "combat_id": None, "round": 0,
                "current_index": 0, "combatants": []}


# ──────────────────────────────────────────────────────────────────────────
# 节点：classify / retrieve / verify / confirm
# ──────────────────────────────────────────────────────────────────────────

def classify(state: GameState) -> dict:
    """LLM 意图分类 → 结构化 intent（覆盖 attack/cast/ability_check/explore/start_combat/end_combat）。"""
    prompt = (
        "你是D&D 5E意图分类器。把玩家输入分类为动作意图,只输出JSON(不要markdown)。\n"
        "action_type ∈ attack|cast|ability_check|explore|start_combat|end_combat|other\n"
        "通用字段: target_name, target_ac(整数,未知0), ability(str/dex/con/int/wis/cha), "
        "retrieval_query(用规则原词构造的检索串:动作规范名+检定类型+DC关键词,如'徒手打击 推撞 豁免DC 8 力量 熟练')\n"
        "attack专有: weapon(武器中文名)\n"
        "cast专有: spell_name, spell_level(整数), spell_dice(如8d6), damage_type(火焰/力场/...), "
        "spell_attack(true=攻击检定型/false=豁免型), save_ability(con/dex/...目标豁免属性), "
        "target_save_bonus(目标该豁免加值,未知0), casting_ability(int/wis/cha 施法属性)\n"
        "ability_check/explore专有: skill(技能名), dc(整数,未知给10), proficient(true/false)\n"
        "start_combat专有: enemies(数组[{name,dex_mod,side='enemy'}])\n"
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

def _resolve_attack(ch, it) -> dict:
    ability = it.get("ability") or "str"
    bonus = ch.ability_mod(ability) + ch.prof()
    ac = int(it.get("target_ac") or 10)
    atk = check.attack_roll(bonus=bonus, ac=ac)             # R-CMB-017/022/023
    out = {"kind": "attack", "attack_total": atk.total, "d20": atk.d20,
           "hit": atk.hit, "crit": atk.crit, "rolls": atk.rolls, "target_ac": ac, "bonus": bonus}
    if atk.hit:
        wname = it.get("weapon") or "长剑"
        try:
            dice_expr = equipment.weapon_damage_dice(wname)
            dmg_type = equipment.weapon_damage_type(wname)
        except KeyError:
            dice_expr, dmg_type = "1d8", "挥砍"
        dr = damage.roll_damage(damage.DamageRequest(  # R-DMG-001 + R-CMB-029
            dice_expr=dice_expr, damage_type=dmg_type,
            ability_mod=ch.ability_mod(ability), add_mod=True, crit=atk.crit))
        out.update({"damage": dr.final, "damage_type": dmg_type,
                    "damage_rolls": dr.dice_rolls, "weapon": wname})
    return out


CLASS_CAST_ABILITY = {  # 职业→施法属性（确定性，优先于 LLM 猜测）
    "法师": "int", "术士": "cha", "吟游诗人": "cha", "魔契师": "cha",
    "牧师": "wis", "德鲁伊": "wis", "圣武士": "wis", "游侠": "wis",
}


def _resolve_cast(ch, it) -> dict:
    cast_ability = CLASS_CAST_ABILITY.get(ch.char_class) or it.get("casting_ability") or "int"
    cast_mod = ch.ability_mod(cast_ability)
    prof = ch.prof()
    save_dc = check.calc_save_dc(cast_mod, prof)            # R-DM-002/R-SPL-021
    atk_bonus = cast_mod + prof                              # R-SPL-022
    spell_dice = it.get("spell_dice") or "1d8"
    dmg_type = it.get("damage_type") or "力场"
    level = int(it.get("spell_level") or 1)
    out = {"kind": "cast", "spell_save_dc": save_dc, "spell_attack_bonus": atk_bonus,
           "spell_level": level, "spell_dice": spell_dice}
    if it.get("spell_attack"):  # 法术攻击检定型
        ac = int(it.get("target_ac") or 10)
        atk = check.attack_roll(bonus=atk_bonus, ac=ac)     # R-SPL-022 + R-CMB-017
        out.update({"spell_attack_total": atk.total, "d20": atk.d20, "hit": atk.hit, "crit": atk.crit, "target_ac": ac})
        if atk.hit:
            dr = damage.roll_damage(damage.DamageRequest(dice_expr=spell_dice, damage_type=dmg_type,
                                                          add_mod=False, crit=atk.crit))
            out.update({"damage": dr.final, "damage_type": dmg_type, "damage_rolls": dr.dice_rolls})
    else:  # 豁免型法术
        save_bonus = int(it.get("target_save_bonus") or 0)
        sv = check.saving_throw(mod=save_bonus, prof=0, proficient=False, dc=save_dc)  # R-CHK-011
        dr = damage.roll_damage(damage.DamageRequest(dice_expr=spell_dice, damage_type=dmg_type, add_mod=False))
        full = dr.final
        final = full if not sv.success else damage.apply_damage_pipeline(  # R-CHK-014 半伤
                    full, dmg_type)  # 简化：成功半伤（向下取整在管线内）
        # 用 R-CHK-014 的半伤逻辑
        from ..engine import dice as _d
        final = full if not sv.success else _d.round_down(full / 2)
        out.update({"save_success": sv.success, "save_total": sv.total, "raw_damage": full,
                    "damage": final, "damage_type": dmg_type, "damage_rolls": dr.dice_rolls})
    return out


def _resolve_ability_check(ch, it) -> dict:
    ability = it.get("ability") or "str"
    dc = int(it.get("dc") or 10)
    proficient = bool(it.get("proficient"))
    r = check.ability_check(mod=ch.ability_mod(ability), prof=ch.prof(),
                            proficient=proficient, dc=dc)    # R-CHK-010
    return {"kind": "ability_check", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "margin": r.margin}


def resolve(state: GameState) -> dict:
    """硬性骰子分派（纯代码，LLM 不参与）。"""
    it = state["intent"]
    at = it.get("action_type")
    cid = state.get("character_id")
    ch = store.get_character(cid) if cid else None
    if ch is None and at not in ("start_combat", "end_combat"):
        return {"dice": {}, "error": "角色卡不存在"}

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
    return {"dice": {}}  # other → 仅叙事


def _resolve_start_combat(state: GameState, ch, it) -> dict:
    """开始战斗：roll_initiative + persist。R-CMB-002"""
    enemies = it.get("enemies") or [{"name": "敌人", "dex_mod": 1, "side": "enemy"}]
    combatants = [cmb.Combatant(cid=str(state["character_id"]), name=ch.name,
                                dex_mod=ch.ability_mod("dex"), side="player", is_player=True)]
    for i, e in enumerate(enemies):
        combatants.append(cmb.Combatant(cid=f"e{i}", name=e.get("name", f"敌人{i}"),
                                        dex_mod=int(e.get("dex_mod", 0)),
                                        side="enemy", is_player=False))
    combat = cmb.Combat()
    order = cmb.roll_initiative(combatants)                  # R-CMB-002
    combat.participants = combatants
    combat.initiative_order = order
    combat.round = 1; combat.current_index = 0; combat.active = True
    cs = store.save_combat(state["campaign_id"], combat)     # persist
    return {"dice": {"kind": "start_combat",
                     "initiative_order": [{"name": c.name, "init": c.initiative, "side": c.side} for c in order]},
            "combat": {"active": True, "combat_id": cs.id, "round": 1,
                       "current_index": 0,
                       "combatants": [{"name": c.name, "init": c.initiative, "side": c.side} for c in order]}}


# ──────────────────────────────────────────────────────────────────────────
# 节点：narrate / apply
# ──────────────────────────────────────────────────────────────────────────

def narrate(state: GameState) -> dict:
    """LLM 叙事 + 结构化状态变更（掷骰结果固定，不可改；在当前场景中叙事）。"""
    dice = state.get("dice", {})
    dig = _digest(state.get("evidence", []))
    combat_ctx = state.get("combat", {})
    scene_ctx = world.scene_context(state.get("campaign_id", 0))  # 在场景中叙事而非虚空
    prompt = (
        "你是D&D 5E DM。依据【掷骰结果(硬性,已由代码算出,不可更改)】与规则,在当前场景中以第二人称简洁叙述(2-4句)。\n"
        "遵循叙事技巧:简洁、多感官氛围、区分选项、不臆测角色行动。\n"
        "然后输出结构化状态变更 + 更新后的场景叙事。只输出JSON: "
        '{"narration":"...", "state_changes":[{"target":"怪物名或character_id","field":"hp","delta":-N,"reason":"..."}], '
        '"scene_update":"行动后场景的新状态叙事(1-2句,更新场景)"}\n'
        f"掷骰结果: {json.dumps(dice, ensure_ascii=False)}\n"
        f"战斗: {json.dumps(combat_ctx, ensure_ascii=False)}\n"
        f"{scene_ctx}\n"
        f"规则摘要:\n{dig}\n玩家输入: {state['player_input']}\n"
        "然后给出3个玩家下一步可做的行动选项(区分细节,如DMG区分选项)。\n"
        "只输出JSON: {\"narration\":\"叙事\",\"state_changes\":[],\"scene_update\":\"\",\"action_options\":[\"选项1\",\"选项2\",\"选项3\"]}\n"
    )
    raw = llm.chat("你是D&D DM,严格依据掷骰结果叙述,不改动数值。只输出JSON。", prompt, temperature=0.4)
    obj = _extract_json(raw)
    return {"narration": obj.get("narration", raw[:200]),
            "state_changes": obj.get("state_changes", []),
            "scene_update": obj.get("scene_update", ""),
            "action_options": obj.get("action_options", [])}


def apply_node(state: GameState) -> dict:
    """应用状态变更 + 持久化（HP/法术位/日志/summary + 战斗轮次推进）。"""
    cid = state.get("character_id")
    camp = state.get("campaign_id")
    ch = store.get_character(cid) if cid else None

    # 1) 结构化状态变更：玩家角色 HP
    for chg in state.get("state_changes", []):
        if str(chg.get("target")) == str(cid) and chg.get("field") == "hp" and ch:
            delta = int(chg.get("delta", 0))
            if delta < 0:
                nhp, _ = damage.apply_damage_to_hp(ch.hp_current, ch.temp_hp, ch.hp_max, -delta)
                ch.hp_current = nhp
            else:
                ch.hp_current = damage.apply_healing(ch.hp_current, ch.hp_max, delta)

    # 2) 施法消耗法术位 R-SPL-002
    if ch and state.get("dice", {}).get("kind") == "cast":
        lvl = state["dice"].get("spell_level", 1)
        slots = ch.spell_slots if hasattr(ch, "spell_slots") else {}
        # 直接操作 spell_slots_json
        import json as _j
        try:
            sd = _j.loads(ch.spell_slots_json)
        except Exception:
            sd = {}
        if sd.get(str(lvl), 0) > 0:
            sd[str(lvl)] -= 1
        ch.spell_slots_json = _j.dumps(sd)

    if ch:
        store.save_character(ch)

    # 3) 战斗轮次推进 R-CMB-001/004
    if state.get("combat", {}).get("active") and camp:
        try:
            combat = store.load_combat(camp)
            cur = cmb.current_combatant(combat)
            nxt = cmb.advance_turn(combat)        # 推进到下一参战者
            store.save_combat(camp, combat)
        except Exception:
            pass

    # 4) 持久化日志 + rolling summary
    if camp:
        store.append_log(camp, player_input=state.get("player_input", ""),
                         dm_output=state.get("narration", ""),
                         dice_rolls=[state.get("dice", {})])
        store.append_summary(camp, f"[轮] {state.get('player_input','')[:30]} → {state.get('narration','')[:40]}")
    # 5) 场景推进：更新 Scene.situation（行动后场景叙事）
    scene_update = state.get("scene_update", "")
    if scene_update and camp:
        sc = store.get_scene(camp)
        if sc:
            sc.situation = scene_update
            store.save_scene(sc)
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
    g = StateGraph(GameState)
    g.add_node("classify", classify)
    g.add_node("retrieve", retrieve)
    g.add_node("verify", verify)
    g.add_node("retrieve_retry", retrieve_retry)
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
