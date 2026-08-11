"""resolvers.actions — 其余 resolve 函数 + 遭遇系统 + 时间推进。

从 brain/graph.py 提取。包含:
  - 属性检定/技能检定（ability_check, hide, search, grapple, shove, study）
  - 休息/社交/升级/探索/旅行
  - 战斗开始 + 突袭判定
  - 遭遇前置判定（场景过滤/时钟/类型）
  - 目标确定性包装
  - 游戏内时间推进
"""

from __future__ import annotations

import dataclasses
import logging

from ...brain import exploration as exploration_mod
from ...brain import levelup as levelup_mod
from ...brain import rest as rest_mod
from ...brain import social as social_mod
from ...engine import check, conditions
from ...engine import combat as cmb
from ...engine import dice as engine_dice
from ...engine.visibility import VisibilityService
from ...rules.grant import GrantManager
from ...rules.choice import ChoiceManager
from ...rules.resource import ResourceManager
from ...build.level_up_service import LevelUpService
from ...stats import models, store
from ..utils import CLASS_CAST_ABILITY

_log = logging.getLogger(__name__)

# ★ CHR-007: 实例化规则管理器与升级服务，接入生产升级路径
_grant_mgr = GrantManager()
_choice_mgr = ChoiceManager()
_resource_mgr = ResourceManager()
_level_up_service = LevelUpService(
    grant_manager=_grant_mgr,
    choice_manager=_choice_mgr,
    resource_manager=_resource_mgr,
)


# ──────────────────────────────────────────────────────────────────────────
# CR → XP 映射表（D&D 5E 标准）
# ──────────────────────────────────────────────────────────────────────────

CR_XP_TABLE: dict[float, int] = {
    0: 10, 0.125: 25, 0.25: 50, 0.5: 100,
    1: 200, 2: 450, 3: 700, 4: 1100, 5: 1800,
    6: 2300, 7: 2900, 8: 3900, 9: 5000, 10: 5900,
    11: 7200, 12: 8400, 13: 10000, 14: 11500, 15: 13000,
    16: 15000, 17: 18000, 18: 20000, 19: 22000, 20: 25000,
    21: 33000, 22: 41000, 23: 50000, 24: 62000, 25: 75000,
    26: 90000, 27: 105000, 28: 120000, 29: 135000, 30: 155000,
}


def cr_to_xp(cr: float) -> int:
    """根据 CR 查表返回 XP。未找到时按最近 CR 向下取档。"""
    if cr in CR_XP_TABLE:
        return CR_XP_TABLE[cr]
    # 向下取最近的已知 CR
    known = sorted(CR_XP_TABLE.keys())
    for k in reversed(known):
        if k <= cr:
            return CR_XP_TABLE[k]
    return 10  # CR<0 兆底


def award_combat_xp(campaign_id: int, character_id: int,
                    defeated_enemies: list[dict]) -> dict:
    """战斗结束后根据击败敌人的 CR 计算 XP 并持久化。

    defeated_enemies: [{"name": str, "cr": float}, ...]
    返回: {"total_xp": int, "new_xp": int}
    """
    total_xp = 0
    for e in defeated_enemies:
        cr = float(e.get("cr", 0))
        total_xp += cr_to_xp(cr)
    if total_xp > 0 and character_id:
        new_xp = store.add_character_xp(character_id, total_xp)
        _log.info("XP奖励 campaign=%s char=%d xp=+%d total=%d",
                  campaign_id, character_id, total_xp, new_xp)
        return {"total_xp": total_xp, "new_xp": new_xp}
    return {"total_xp": total_xp, "new_xp": 0}


# ──────────────────────────────────────────────────────────────────────────
# 属性/技能检定
# ──────────────────────────────────────────────────────────────────────────

# CHK-001: 熟练查询只能从角色数据派生

def _build_check_service(ch):
    """CHK-001: 构建 CheckService，从 ProficiencyGrant 集合派生熟练。"""
    from ...engine.proficiency_service import (
        build_registry_from_character, CheckService,
    )
    registry = build_registry_from_character(ch)
    return CheckService(registry=registry, proficiency_bonus=ch.prof())


def _check_skill_proficient(ch, skill_name: str) -> bool:
    """CHK-001: 从 Character 的 skill_proficiencies 查询技能熟练状态。

    熟练只能从角色数据获取，不能从 LLM 输出或硬编码中获取。
    未熟练不加 PB；专精（Expertise）恰好加两次 PB。

    优先使用 ProficiencyRegistry + CheckService（统一熟练度来源），
    回退到旧版 skill_proficiencies 列表查询。
    """
    if not skill_name or not ch:
        return False
    # CHK-001: 使用 CheckService 从 ProficiencyGrant 集合派生熟练
    try:
        from ...engine.proficiency_service import (
            build_registry_from_character, CheckService,
        )
        registry = build_registry_from_character(ch)
        service = CheckService(registry=registry, proficiency_bonus=ch.prof())
        if service.is_skill_proficient(skill_name):
            return True
    except Exception:
        pass
    # 回退：Character.skill_proficiencies 从 skill_prof_json 加载
    profs = getattr(ch, "skill_proficiencies", []) or []
    # 支持精确匹配和子串匹配（如 "感知(察觉)" 匹配 "察觉"）
    for p in profs:
        if p == skill_name or skill_name in p or p in skill_name:
            return True
    return False


# CHK-002: DC 来源分类

# 规则书标准 DC 锚点（PHB 2024）——权威查表见 engine.core_loop.dc_by_difficulty


def _resolve_ability_check_dc(it: dict) -> int:
    """CHK-002: 属性检定 DC 解析，不允许 LLM 直接提供 DC 值。

    DC 来源优先级:
      1. 规则书标准难度等级标签（如"中等"→ 15）——权威实现 engine.core_loop
      2. 场景/旅行模块预设的 DC
      3. 默认 10（无明确规则场景）
    """
    # 1) 难度等级标签 → 查表（★ 权威实现: engine.core_loop.dc_by_difficulty）
    difficulty = (it.get("difficulty") or "").strip()
    if difficulty:
        try:
            from ...engine.core_loop import dc_by_difficulty
            _alias = {"很容易": "非常容易"}  # 词汇别名→引擎标准键
            return dc_by_difficulty(_alias.get(difficulty, difficulty))
        except ValueError:
            pass
    # 2) 旅行/探索模块预设 DC
    nav_dc = it.get("nav_dc")
    if nav_dc is not None:
        return int(nav_dc)
    # 3) 默认 DC 10（PHB 标准）
    return 10


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


def resolve_ability_check(ch, it) -> dict:
    ability = it.get("ability") or _infer_ability(it.get("skill"),
                                                  it.get("action_type", "ability_check"))
    # CHK-001: 熟练只能从 Character 的 skill_proficiencies 查询，不能从 LLM 获取
    skill_name = it.get("skill", "")
    proficient = _check_skill_proficient(ch, skill_name)
    # CHK-002: DC 来源分类——属性检定 DC 从规则书标准或场景数据获取
    dc = _resolve_ability_check_dc(it)
    # R-GLS-047 力竭 d20 惩罚（等级×2）
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())
    r = check.ability_check(mod=ch.ability_mod(ability), prof=ch.prof(),
                            proficient=proficient, dc=dc, circ=exh_penalty)    # R-CHK-010
    out = {"kind": "ability_check", "check_total": r.total, "d20": r.d20,
           "success": r.success, "dc": dc, "margin": r.margin, "ability": ability,
           "proficient": proficient, "dc_source": "ability_check"}
    # ★ OBS-001: 透传修正来源解释（engine.resolution_trace 权威结构）
    if getattr(r, "modifier_breakdown", None):
        out["resolution_trace"] = _build_resolution_trace(
            "ability_check", ability, r.d20, r.modifier_breakdown, r.total, dc)
    return out


def _build_resolution_trace(action: str, ability: str, d20: int,
                            breakdown: list, total: int, target: int) -> dict:
    """OBS-001: 用 engine.resolution_trace / resolution_trace_ext 构建完整轨迹。

    返回可直接 JSON 化的 dict（含 UI 可展开的公式树）。
    """
    try:
        from ...engine.resolution_trace import (
            ModifierSource,
            ResolutionTrace,
            RollTrace,
        )
        from ...engine.resolution_trace_ext import FormulaNode
        trace = ResolutionTrace(
            trace_id=f"{action}_{ability}_{d20}",
            action_type=action,
            actor_id=ability,
            final_result={"total": total, "target": target,
                          "success": total >= target},
        )
        roll = RollTrace(
            dice_expr=f"d20+{sum(m.get('value', 0) for m in breakdown)}",
            dice_rolls=[d20],
            modifiers=[
                ModifierSource(
                    source_type="circumstance",
                    source_name=m.get("source", ""),
                    value=m.get("value", 0),
                ) for m in breakdown
            ],
            total=total,
        )
        trace.add_roll(roll)
        root = FormulaNode(node_type="result", label=action, value=total)
        root.children.append(FormulaNode(node_type="roll", label="d20", value=d20))
        for m in breakdown:
            root.children.append(FormulaNode(
                node_type="modifier", label=m.get("source", ""),
                value=m.get("value", 0)))
        root.children.append(FormulaNode(
            node_type="total", label="vs target", value=target))
        return {
            "action": action,
            "d20": d20,
            "modifiers": [m for m in breakdown],
            "total": total,
            "target": target,
            "display": trace.to_display_string(),
            "formula_tree": _formula_node_to_dict(root),
        }
    except Exception:
        # 引擎不可用时回退为扁平 dict（保持输出兼容）
        return {
            "action": action,
            "d20": d20,
            "modifiers": [{"source": m.get("source", ""), "value": m.get("value", 0)}
                          for m in breakdown],
            "total": total,
            "target": target,
        }


def _formula_node_to_dict(node) -> dict:
    """递归序列化 FormulaNode（供 UI 渲染）。"""
    return {
        "node_type": getattr(node, "node_type", ""),
        "label": getattr(node, "label", ""),
        "value": getattr(node, "value", 0),
        "children": [_formula_node_to_dict(c) for c in getattr(node, "children", [])],
    }


def resolve_hide(ch, it) -> dict:
    """躲藏：敏捷(隐匿)检定 vs 固定 DC15（2024 规则）。

    规则: 术语汇编/动作.htm「躲藏」— 2024 版为固定 DC15（非旧的被动
          察觉 DC）；成功后检定总值成为他人察觉该生物的 DC。

    ★ COM-015/ENV-001: 躲藏前置条件由 VisibilityService 验证。
      无遮挡且被可见敌人观察时返回 ILLEGAL_HIDE 且不消耗动作。
    """
    # COM-015: 检查躲藏前置条件——需要遮蔽/掩护
    has_cover = bool(it.get("has_cover", False))
    is_heavily_obscured = bool(it.get("is_heavily_obscured", False))
    is_visible_to_enemy = bool(it.get("is_visible_to_enemy", False))

    # 如果没有遮蔽且没有掩护，且被敌人可见，则不能躲藏
    if not has_cover and not is_heavily_obscured and is_visible_to_enemy:
        return {"kind": "hide", "error": "ILLEGAL_HIDE",
                "reason": "无遮挡且被敌人观察，无法躲藏"}

    stealth_mod = ch.ability_mod("dex")
    prof = ch.prof()
    dc = int(it.get("dc") or 15)
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())  # R-GLS-047
    # CHK-001: 熟练从角色数据派生（隐匿技能），不再硬编码 True
    proficient = _check_skill_proficient(ch, "潜行") or _check_skill_proficient(ch, "隐匿")
    r = check.ability_check(mod=stealth_mod, prof=prof,
                            proficient=proficient, dc=dc, circ=exh_penalty)
    return {"kind": "hide", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "proficient": proficient,
            "effect": "隐蔽成功" if r.success else "被发现"}


def resolve_search(ch, it) -> dict:
    """搜索：感知(察觉)或智力(调查)检定 vs DC。R-CHK-010"""
    ability = it.get("ability") or "wis"
    mod = ch.ability_mod(ability)
    prof = ch.prof()
    dc = int(it.get("dc") or 15)
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())  # R-GLS-047
    # CHK-001: 熟练从角色数据派生（察觉/调查技能），不再硬编码 True
    skill_name = it.get("skill", "察觉" if ability == "wis" else "调查")
    proficient = _check_skill_proficient(ch, skill_name)
    r = check.ability_check(mod=mod, prof=prof, proficient=proficient, dc=dc, circ=exh_penalty)
    return {"kind": "search", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "ability": ability,
            "proficient": proficient}


def resolve_grapple(ch, it) -> dict:
    """擒抱（2024）：目标投力量/敏捷豁免 vs DC=8+力调+熟练；失败则受擒。

    规则: 术语汇编/武器与徒手打击.htm「擒抱」— 目标必须通过一次力量或
          敏捷豁免检定（由目标选择），否则陷入受擒；豁免/逃脱 DC =
          8 + 攻击者力量调整值 + 熟练加值。
    说明: 2014 版对抗检定已废弃；攻击者不掷骰，改由目标豁免。
    """
    from ...engine import combat as _combat
    save_choice = it.get("target_save_choice") or "strength"
    r = _combat.attempt_grapple(
        ch.ability_mod("str"), ch.prof(),
        save_choice=save_choice,
        target_save_mod=int(it.get("target_save_bonus") or 0),
        target_save_prof=bool(it.get("target_save_prof")),
        target_prof=int(it.get("target_prof") or 0),
        attacker_size=it.get("attacker_size") or "medium",
        target_size=it.get("target_size") or "medium",
        has_free_hand=bool(it.get("has_free_hand", True)),
    )
    return {"kind": "grapple", "check_total": r["save_total"], "d20": r["save_d20"],
            "success": r["grappled"], "dc": r["dc"], "escape_dc": r["escape_dc"],
            "ability": save_choice, "reason": r["reason"],
            "effect": "擒抱成功，目标陷入受擒" if r["grappled"] else "擒抱失败"}


def resolve_shove(ch, it) -> dict:
    """推撞（2024）：目标投力量/敏捷豁免 vs DC=8+力调+熟练；失败则倒地或被推离5尺。

    规则: 术语汇编/武器与徒手打击.htm「推撞」— 目标必须通过一次力量或
          敏捷豁免检定（由目标选择），否则被推开5尺或陷入倒地（由你选择）。
    说明: 2014 版对抗检定已废弃；攻击者不掷骰，改由目标豁免。
    """
    from ...engine import combat as _combat
    save_choice = it.get("target_save_choice") or "strength"
    shove_type = it.get("shove_type", "prone")
    r = _combat.attempt_shove(
        ch.ability_mod("str"), ch.prof(),
        save_choice=save_choice,
        target_save_mod=int(it.get("target_save_bonus") or 0),
        target_save_prof=bool(it.get("target_save_prof")),
        target_prof=int(it.get("target_prof") or 0),
        attacker_size=it.get("attacker_size") or "medium",
        target_size=it.get("target_size") or "medium",
        shove_type=shove_type,
    )
    return {"kind": "shove", "check_total": r["save_total"], "d20": r["save_d20"],
            "success": r["shoved"], "dc": r["dc"], "ability": save_choice,
            "shove_type": shove_type, "reason": r["reason"],
            "effect": f"推撞成功({shove_type})" if r["shoved"] else "推撞失败"}


def resolve_study(ch, it) -> dict:
    """研究：智力(奥秘/历史/调查/自然/宗教) 检定 vs DC。R-CHK-010"""
    ability = it.get("ability") or "int"
    mod = ch.ability_mod(ability)
    prof = ch.prof()
    dc = int(it.get("dc") or 15)
    exh_penalty = -conditions.d20_penalty(ch.to_condition_state())  # R-GLS-047
    # CHK-001: 熟练从角色数据派生（研究技能），不再硬编码 True
    skill_name = it.get("skill", "调查")
    proficient = _check_skill_proficient(ch, skill_name)
    r = check.ability_check(mod=mod, prof=prof, proficient=proficient, dc=dc, circ=exh_penalty)
    return {"kind": "study", "check_total": r.total, "d20": r.d20,
            "success": r.success, "dc": dc, "ability": ability,
            "proficient": proficient}


# ──────────────────────────────────────────────────────────────────────────
# 休息
# ──────────────────────────────────────────────────────────────────────────

def resolve_rest(state, ch, it) -> dict:
    """休息机制：短休消耗生命骰恢复HP+恢复职业特性；长休恢复全部HP+所有法术位+力竭-1。
    R-GLS-014/R-GLS-015
    ★ REST-002: 通过 engine.rest_state.RestStateRegistry 追踪持久状态机
      （StartRest → RestInterrupted/RestCompleted 事件语义）。
    """
    pi = state.get("player_input", "") or ""
    rest_type = it.get("rest_type") or (
        "long" if ("长休" in pi or "long rest" in pi.lower() or "long" in pi.lower() and "休" in pi) else "short")

    # ★ REST-002: 开始休息会话（StartRest）
    session = None
    try:
        from ...engine.rest_state import RestStateRegistry
        _rest_registry = RestStateRegistry()
        game_minutes = int(state.get("game_minutes", 0) or 0)
        session = _rest_registry.start_rest(
            str(getattr(ch, "id", "unknown")), rest_type, game_minutes)
    except Exception as e:
        _log.debug("休息会话创建失败（跳过）: %s", e)

    if rest_type == "short":
        hit_dice_to_spend = int(it.get("hit_dice_to_spend", 0))
        result = rest_mod.short_rest(ch, hit_dice_to_spend=hit_dice_to_spend)
    else:  # long
        camp_id = state.get("campaign_id")
        if camp_id:
            try:
                c = store.get_campaign(camp_id)
                flags = c.world_flags if c else {}
                last = flags.get(f"last_long_rest_min_{ch.id}")
                now_min = int(flags.get("game_minutes", 8 * 60))
                cd_min = rest_mod.LONG_REST_COOLDOWN_HOURS * 60
                if last is not None and now_min - int(last) < cd_min:
                    remain = cd_min - (now_min - int(last))
                    return {"kind": "rest",
                            "error": f"距上次长休不足{rest_mod.LONG_REST_COOLDOWN_HOURS}小时，"
                                     f"还需等待约{max(1, remain // 60)}小时才能再次长休（可先短休）"}
            except Exception as e:
                _log.debug("长休冷却检查失败 camp=%s: %s", camp_id, e)
        result = rest_mod.long_rest(ch)
    result["kind"] = "rest"

    # ★ REST-002: 推进会话并标记完成/打断（RestCompleted / RestInterrupted）
    if session is not None:
        try:
            if result.get("success"):
                session.advance(session.target_duration)  # 完成
                result["rest_session_id"] = session.character_id
                result["rest_phase"] = session.phase.value
            elif result.get("interrupted"):
                session.interrupt(result.get("cause", "未知"))
                result["rest_session_id"] = session.character_id
                result["rest_phase"] = session.phase.value
        except Exception as e:
            _log.debug("休息会话状态更新失败（跳过）: %s", e)

    return result


def apply_rest_to_character(ch, result: dict) -> None:
    """将休息收益落盘到 Character（在 apply_node 中调用）。R-GLS-014 短休 / R-GLS-015 长休"""
    if not result.get("success"):
        return
    rtype = result.get("type", "short")
    hp_restored = int(result.get("hp_restored", 0))
    if hp_restored:
        ch.hp_current = min(ch.hp_max, ch.hp_current + hp_restored)
    if rtype == "short":
        spent = int(result.get("hit_dice_spent", 0))
        remaining = int(result.get("hit_dice_remaining", 0))
        if hasattr(ch, "hit_dice_current"):
            ch.hit_dice_current = max(0, remaining)
    if rtype == "long":
        exh = int(result.get("exhaustion_reduced", 0))
        if exh:
            ch.exhaustion = max(0, ch.exhaustion - exh)
        if result.get("temp_hp_cleared"):
            ch.temp_hp = 0
        if result.get("spell_slots_restored") and ch.char_class in CLASS_CAST_ABILITY:
            try:
                from ...data import spells as _sp
                ch.set_spell_slots(_sp.max_spell_slots(ch.level))
            except Exception as e:
                _log.debug("长休恢复法术位失败 cid=%s: %s", getattr(ch, "id", "?"), e)
        if hasattr(ch, "hit_dice_current"):
            ch.hit_dice_current = ch.level


# ──────────────────────────────────────────────────────────────────────────
# 社交
# ──────────────────────────────────────────────────────────────────────────

# NPC 态度同义词归一化表（LLM 可能返回中文/非标准串）
_ATTITUDE_ALIASES = {
    "friendly": "friendly", "friend": "friendly", "友善": "friendly", "友好": "friendly",
    "indifferent": "indifferent", "neutral": "indifferent", "normal": "indifferent",
    "中立": "indifferent", "冷漠": "indifferent", "一般": "indifferent", "普通": "indifferent",
    "hostile": "hostile", "enemy": "hostile", "angry": "hostile",
    "敌对": "hostile", "敌意": "hostile", "愤怒": "hostile", "仇视": "hostile",
}


def _normalize_attitude(raw) -> str:
    """把 LLM 返回的态度串归一化为 {friendly, indifferent, hostile}。"""
    if not isinstance(raw, str):
        return "indifferent"
    return _ATTITUDE_ALIASES.get(raw.strip().lower(), "indifferent")


def resolve_social(state, ch, it) -> dict:
    """社交流程：NPC态度系统/四步社交互动/态度转换阈值。R-CON-012/R-DM-047"""
    npc_name = it.get("npc_name", "NPC")
    llm_attitude = _normalize_attitude(it.get("npc_attitude", "indifferent"))
    skill = it.get("skill", "persuasion")
    dc = int(it.get("dc", 15))

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

    # 免检定（DMG「运作交涉」：友好/冷漠 NPC 面对合理、不损其利益的请求
    # 无需魅力检定）。needs_check 由 Director 判断请求合理性；存盘态度为敌对时
    # 不信任该判断，仍走掷骰（LLM 误判防护）。
    if it.get("needs_check") is False and stored_attitude != social_mod.ATTITUDE_HOSTILE:
        return {"kind": "social", "skill": skill, "auto_success": True, "success": True,
                "npc_name": npc_name, "npc_attitude": stored_attitude,
                "new_attitude": stored_attitude,
                "note": "NPC态度非敌对且请求合理，无需检定（DMG：仅在结果不确定时掷骰）"}

    npc = social_mod.NPC(name=npc_name, attitude=stored_attitude)
    dc_modifier = social_mod.check_social_dc(npc.attitude)
    final_dc = max(1, dc + dc_modifier)

    ability = "cha" if skill in ("persuasion", "deception", "intimidation", "performance") else "wis"
    # CHK-001: 社交技能熟练从角色数据派生，不再硬编码 True
    skill_name = it.get("skill", "说服")
    _skill_map = {"persuasion": "说服", "deception": "欺瞒",
                  "intimidation": "威吓", "performance": "表演", "insight": "洞悉"}
    proficient = _check_skill_proficient(ch, _skill_map.get(str(skill_name), str(skill_name)))
    r = check.ability_check(mod=ch.ability_mod(ability), prof=ch.prof(),
                            proficient=proficient, dc=final_dc)

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


# ──────────────────────────────────────────────────────────────────────────
# 升级
# ──────────────────────────────────────────────────────────────────────────

def _character_to_levelup_dict(ch) -> dict:
    """把 Character 桥接为 level_up() 期望的角色字典。"""
    next_level = min(ch.level + 1, levelup_mod.MAX_LEVEL)
    return {
        "level": ch.level,
        "xp": levelup_mod.XP_TABLE.get(next_level, 0),
        "class_name": ch.char_class,
        "scores": {k.upper(): v for k, v in ch.abilities.items()},
        "hp_max": ch.hp_max,
        "hp_current": ch.hp_current,
        "features": list(ch.feats),
        "asi_taken": False,
    }


def resolve_levelup(ch, it) -> dict:
    """升级与成长。R-DM-041~045

    ★ CHR-007: 升级流程不依赖调用方传入新特性。
      使用 LevelUpService 自动计算授予/选择。
    """
    current_level = ch.level
    new_level = current_level + 1
    if new_level > levelup_mod.MAX_LEVEL:
        return {"kind": "levelup", "error": "已达最高等级20"}

    # ★ CHR-007: 使用 LevelUpService 规划升级
    try:
        plan = _level_up_service.plan_level_up(
            entity_id=str(ch.id),
            class_name=ch.char_class,
            new_level=new_level,
            character_data={
                "level": ch.level,
                "class_name": ch.char_class,
                "subclass": ch.subclass,
                "scores": {k.upper(): v for k, v in ch.abilities.items()},
            },
        )
    except Exception as e:
        _log.warning("LevelUpService.plan_level_up 失败: %s", e)
        plan = None

    char_dict = _character_to_levelup_dict(ch)
    try:
        result = levelup_mod.level_up(
            char_dict, new_class=None, new_features=None,
            ability_improvements=None, hit_die_roll=None,
        )
    except ValueError as e:
        return {"kind": "levelup", "error": str(e)}

    out = {"kind": "levelup", "old_level": current_level,
           "new_level": result.get("new_level", new_level),
           "hp_gained": result.get("hp_gained", 0),
           "pb_changed": result.get("pb_changed", False),
           "new_pb": result.get("new_proficiency_bonus", 0),
           "tier": result.get("tier", levelup_mod.get_tier(new_level))}

    # ★ CHR-007: 附加 LevelUpService 计算的特性和选择
    if plan:
        out["new_features"] = [f.name for f in plan.new_features]
        out["choice_requests"] = [cr.to_dict() for cr in plan.choice_requests]
        out["resource_updates"] = plan.resource_updates

    return out


def apply_levelup_to_character(ch, dice: dict) -> None:
    """把升级结果落盘到 Character。R-DM-043

    ★ CHR-007: 持久化等级、HP、新特性、资源池和 ASI 变更。
    """
    new_level = dice.get("new_level")
    if new_level:
        ch.level = new_level
    gained = int(dice.get("hp_gained", 0))
    if gained:
        ch.hp_max += gained
        ch.hp_current += gained

    # ★ CHR-007: 持久化新特性（如果有）
    new_features = dice.get("new_features")
    if new_features:
        existing_feats = list(ch.feats)
        for feat_name in new_features:
            if feat_name not in existing_feats:
                existing_feats.append(feat_name)
        ch.set_feats(existing_feats)

    # ★ CHR-007: 创建资源池（如果有）
    resource_updates = dice.get("resource_updates")
    if resource_updates:
        for ru in resource_updates:
            pool_name = ru.get("name", "")
            max_val = ru.get("max_value", 0)
            recharge_on = ru.get("recharge_on", "short_rest")
            source_feat = ru.get("source_feature_id", "")
            pool_type_str = ru.get("pool_type", "REGEN")
            res_type_str = ru.get("resource_type", "GENERAL")
            _resource_mgr.create_pool(
                entity_id=str(ch.id),
                name=pool_name,
                max_value=max_val,
                recharge_on=recharge_on,
                source_feature_id=source_feat,
                pool_type=pool_type_str,
                resource_type=res_type_str,
            )


# ──────────────────────────────────────────────────────────────────────────
# 探索/旅行
# ──────────────────────────────────────────────────────────────────────────

def _resolve_terrain(state, it) -> str:
    """地形解析。详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段B3。"""
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


def resolve_travel(state, ch, it) -> dict:
    """探索流程：旅行步调/导航检定/被动察觉/随机遭遇/资源追踪。
    R-DM-026~040 / R-GLS-048
    """
    pace_raw = str(it.get("pace", "中速")).strip().lower()
    _PACE_ALIASES = {
        "fast": "快速", "快速": "快速",
        "normal": "中速", "中速": "中速", "medium": "中速",
        "slow": "慢速", "慢速": "慢速",
    }
    pace = _PACE_ALIASES.get(pace_raw, "中速")
    terrain = _resolve_terrain(state, it)
    try:
        _tp = exploration_mod.terrain_params(terrain)
        nav_dc = _tp.nav_dc
        perception_dc = _tp.search_dc
    except ValueError:
        nav_dc = int(it.get("nav_dc", 15))
        perception_dc = 15

    pace_info = exploration_mod.get_travel_pace(pace)
    # 导航检定仅在有迷路风险时掷（R-DM-037；沿已知道路/有向导→免检定，
    # 由 Director 的 needs_check 判断）；被动察觉本就不掷骰，照常计算。
    if it.get("needs_check") is False:
        nav_check = None
        nav_result = exploration_mod.NavigationResult(success=True, lost=False,
                                                      length_multiplier=1.0)
    else:
        # CHK-001: 导航检定熟练从角色数据派生（求生技能），不再硬编码 True
        nav_proficient = _check_skill_proficient(ch, "求生")
        nav_check = check.ability_check(mod=ch.ability_mod("wis"), prof=ch.prof(),
                                        proficient=nav_proficient, dc=nav_dc)
        nav_result = exploration_mod.navigation(survival_total=nav_check.total, nav_dc=nav_dc)

    passive_perception = 10 + ch.ability_mod("wis")
    perception_result = exploration_mod.check_passive_perception(
        party_passive_scores=[(ch.name, passive_perception)],
        dc=perception_dc,
    )

    # ★ engine.travel: 权威每日/每小时行进距离（与 exploration_mod 互为校验）
    travel_info = {}
    try:
        from ...engine.travel import travel_daily_distance as _eng_daily
        from ...engine.travel import travel_distance as _eng_distance
        _pace_en = {"快速": "fast", "中速": "normal", "慢速": "slow"}[pace]
        travel_info = {
            "engine_miles_per_hour": _eng_distance(_pace_en, 1.0),
            "engine_miles_per_day": _eng_daily(_pace_en),
            "engine_pace": _pace_en,
        }
    except Exception as e:
        _log.debug("engine.travel 距离计算失败（跳过）: %s", e)

    # ★ engine.exploration_clock: 8小时旅行日时钟 + 地形速度系数
    clock_info = {}
    try:
        from ...engine.exploration_clock import ExplorationClock
        _clock = ExplorationClock()
        _day_dist = travel_info.get("engine_miles_per_day", pace_info.per_day_miles)
        clock_info = {"exploration_clock": _clock.travel_day(_day_dist, terrain=terrain)}
    except Exception as e:
        _log.debug("exploration_clock 旅行日计算失败（跳过）: %s", e)

    # ★ engine.encumbrance: 负重状态（STR 负重上限 vs 物品估算重量）
    enc_info = {}
    try:
        from ...engine.encumbrance import encumbrance_status
        _inv = getattr(ch, "inventory", []) or []
        _est_weight = min(300.0, len(_inv) * 2.0)  # 简化：每件物品估重 2 磅
        enc_info = {"encumbrance": encumbrance_status(
            _est_weight, int(ch.ability_score("str") or 10))}
    except Exception as e:
        _log.debug("encumbrance 负重计算失败（跳过）: %s", e)

    # ★ engine.hazards: 危险地形危害判定（悬崖坠落/荒漠灼烧等）
    hazard_info = {}
    try:
        from ...engine.hazards import burning_damage, fall_damage
        if terrain in ("峭壁", "悬崖", "山地"):
            hazard_info = {"hazard": "fall", "fall_damage": fall_damage(30)}
        elif terrain in ("荒漠", "沙漠", "火山"):
            hazard_info = {"hazard": "burn", "burning_damage": burning_damage()}
    except Exception as e:
        _log.debug("hazards 危害计算失败（跳过）: %s", e)

    return {"kind": "travel", "pace": pace,
            "per_minute_ft": pace_info.per_minute_ft,
            "per_hour_miles": pace_info.per_hour_miles,
            "per_day_miles": pace_info.per_day_miles,
            "stealth_disadvantage": pace_info.stealth_disadvantage,
            "perception_disadvantage": pace_info.perception_disadvantage,
            "perception_advantage": pace_info.perception_advantage,
            "nav_result": dataclasses.asdict(nav_result),
            "nav_check_total": nav_check.total if nav_check else None,
            "nav_check_success": nav_result.success,
            "nav_check_skipped": nav_check is None,
            "perception_result": dataclasses.asdict(perception_result),
            "nav_dc": nav_dc,
            "perception_dc": perception_dc,
            "terrain": terrain,
            **travel_info, **clock_info, **enc_info, **hazard_info}


# ──────────────────────────────────────────────────────────────────────────
# 停工期 (EXP-003)
# ──────────────────────────────────────────────────────────────────────────

def resolve_downtime(ch, it) -> dict:
    """停工期活动：开始/推进停工期项目（制作/研究/训练等）。

    规则: EXP-003 制作和停工期完整规则
    出处: topics/城主指南2024/2.运作游戏/运作交涉/停工期活动.htm

    intent 字段:
        downtime_action: "start"|"advance"|"interrupt"|"resume"
        activity: 活动类型（如 "crafting"）
        days: 推进天数
        item_value_gp: 制作物品价值（GP）

    ★ engine.downtime_craft: DowntimeManager 权威执行项目状态机
      （start_project/advance_project → ProgressEvent）。
    """
    from ...engine.downtime import (
        DOWNTIME_ACTIVITIES, DowntimeProject,
        crafting_cost, crafting_time_days,
    )

    action = it.get("downtime_action", "start")
    activity = it.get("activity", "crafting")
    days = int(it.get("days", 1) or 1)
    item_value_gp = float(it.get("item_value_gp", 0) or 0)

    if activity not in DOWNTIME_ACTIVITIES and activity != "crafting":
        return {"kind": "downtime", "error": f"未知停工期活动: {activity}",
                "available": list(DOWNTIME_ACTIVITIES.keys())}

    # ★ engine.downtime_craft: 权威项目状态机（含进度/事件）
    try:
        from ...engine.downtime_craft import (
            CraftingRequirement,
            DowntimeManager,
            ProjectDefinition,
        )
        _mgr = _downtime_manager()
        project_id = f"downtime_{ch.id}_{activity}"
        if action == "start":
            if activity == "crafting":
                total_days = crafting_time_days(item_value_gp)
                total_cost = crafting_cost(item_value_gp)
            else:
                entry = DOWNTIME_ACTIVITIES.get(activity, {})
                total_days = int(entry.get("time_days", 7))
                total_cost = float(entry.get("cost_gp", 0))
            project = ProjectDefinition(
                project_id=project_id,
                name=activity,
                project_type=activity,
                total_work_days=max(1.0, float(total_days)),
                cost_gp=float(total_cost),
                requirements=[CraftingRequirement(item_tag=activity, quantity=1)],
                check_ability="int",
                check_dc=max(5, int(it.get("check_dc", 15) or 15)),
            )
            _mgr.start_project(project)
            return {"kind": "downtime", "action": "started",
                    "project": project.snapshot() if hasattr(project, "snapshot")
                    else {"project_id": project_id, "name": activity,
                          "total_work_days": total_days, "cost_gp": total_cost,
                          "progress": project.progress_percent()},
                    "activity": activity, "days_required": total_days,
                    "cost_gp": total_cost,
                    "engine_downtime": "downtime_craft"}
        # advance/interrupt/resume → 推进项目
        ev = _mgr.advance_project(project_id, float(days))
        existing = _mgr.get_project(project_id)
        return {"kind": "downtime", "action": action,
                "activity": activity, "days": days,
                "progress_percent": existing.progress_percent() if existing else 0.0,
                "project_complete": existing.is_complete() if existing else False,
                "event": getattr(ev, "event_type", "") if ev else "",
                "note": f"停工期项目推进/中断规则已计算（EXP-003）",
                "crafting_time_days": crafting_time_days(item_value_gp) if activity == "crafting" else None,
                "crafting_cost_gp": crafting_cost(item_value_gp) if activity == "crafting" else None}
    except Exception as e:
        _log.debug("downtime_craft 状态机失败（回退公式）: %s", e)

    # 回退：旧公式路径
    project_id = f"downtime_{ch.id}_{activity}"

    if action == "start":
        if activity == "crafting":
            total_days = crafting_time_days(item_value_gp)
            total_cost = crafting_cost(item_value_gp)
        else:
            entry = DOWNTIME_ACTIVITIES.get(activity, {})
            total_days = int(entry.get("time_days", 7))
            total_cost = float(entry.get("cost_gp", 0))
        project = DowntimeProject(
            project_id=project_id, activity=activity,
            total_days=max(1, total_days), total_cost_gp=total_cost,
        )
        return {"kind": "downtime", "action": "started",
                "project": project.snapshot(),
                "activity": activity, "days_required": total_days,
                "cost_gp": total_cost}

    # advance/interrupt/resume 需先有项目（此处简化：返回公式说明）
    return {"kind": "downtime", "action": action,
            "activity": activity, "days": days,
            "note": f"停工期项目推进/中断规则已计算（EXP-003）",
            "crafting_time_days": crafting_time_days(item_value_gp) if activity == "crafting" else None,
            "crafting_cost_gp": crafting_cost(item_value_gp) if activity == "crafting" else None}


# ★ EXP-003: 停工期项目内存注册表（engine.downtime_craft.DowntimeManager）
_DOWNTIME_MANAGER = None


def _downtime_manager():
    """惰性单例 DowntimeManager。"""
    global _DOWNTIME_MANAGER
    if _DOWNTIME_MANAGER is None:
        from ...engine.downtime_craft import DowntimeManager
        _DOWNTIME_MANAGER = DowntimeManager()
    return _DOWNTIME_MANAGER


# ──────────────────────────────────────────────────────────────────────────
# 战斗开始 + 突袭
# ──────────────────────────────────────────────────────────────────────────

def _determine_surprise(state, ch, it, combatants) -> dict:
    """B3 突袭判定。R-CMB-002 + R-GLS-009（2024 突袭=先攻劣势，不跳回合）"""
    explicit = str(it.get("surprise") or "").strip().lower()
    if explicit in ("player", "enemy", "none"):
        surprised_side = None if explicit == "none" else explicit
        note = "DM/系统指定"
    else:
        enemies = [c for c in combatants if not c.is_player]
        surprised_side = None
        note = "无敌方，无突袭"
        if enemies:
            stealth_best = max(int(getattr(c, "dex_mod", 0) or 0) for c in enemies)
            stealth_roll = engine_dice.roll_die(20) + stealth_best
            passive_perc = 10 + ch.ability_mod("wis")
            if stealth_roll >= passive_perc:
                surprised_side = "player"
                note = f"敌方隐匿{stealth_roll}≥你的被动察觉{passive_perc}，你被突袭"
            else:
                note = f"敌方隐匿{stealth_roll}<你的被动察觉{passive_perc}，双方互相察觉"
    if surprised_side:
        for c in combatants:
            if surprised_side == "player" and c.is_player or surprised_side == "enemy" and not c.is_player:
                c.surprised = True
    return {"surprised_side": surprised_side, "note": note}


def resolve_start_combat(state, ch, it) -> dict:
    """开始战斗：突袭判定 + roll_initiative + persist。R-CMB-002"""
    enemies = it.get("enemies") or [{"name": "敌人", "dex_mod": 1, "side": "enemy"}]
    combatants = [cmb.Combatant(cid=str(state["character_id"]), name=ch.name,
                                dex_mod=ch.ability_mod("dex"), side="player",
                                is_player=True, hp=ch.hp_current, hp_max=ch.hp_max)]
    for i, e in enumerate(enemies):
        _ename = e.get("name", f"敌人{i}")
        base: dict = {}
        try:
            from ...data import monsters as _mon
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
    surprise_info = _determine_surprise(state, ch, it, combatants)
    combat = cmb.Combat()
    order = cmb.roll_initiative(combatants)
    combat.participants = combatants
    combat.initiative_order = order
    combat.round = 1; combat.current_index = 0; combat.active = True
    cs = store.save_combat(state["campaign_id"], combat)
    return {"dice": {"kind": "start_combat",
                     "surprise": surprise_info,
                     "initiative_order": [{"name": c.name, "init": c.initiative,
                                           "side": c.side,
                                           "surprised": bool(getattr(c, "surprised", False))}
                                          for c in order]},
            "combat": {"active": True, "combat_id": cs.id, "round": 1,
                       "current_index": 0,
                       "combatants": [{"name": c.name, "init": c.initiative, "side": c.side,
                                       "cid": c.cid, "hp": c.hp, "hp_max": c.hp_max} for c in order]}}


# ──────────────────────────────────────────────────────────────────────────
# 目标确定性包装
# ──────────────────────────────────────────────────────────────────────────

def with_target_outcome(state, dice_out: dict) -> dict:
    """BUG#5/B2：攻击/单体法术造成伤害时，把目标与预计结果写入 dice。"""
    from ..utils import _HEAL_TYPES
    out: dict = {"dice": dice_out}
    if dice_out.get("error") or dice_out.get("damage_type") in _HEAL_TYPES:
        return out
    dmg = int(dice_out.get("damage") or 0)
    tcid = (state.get("intent", {}) or {}).get("target_cid")
    if not tcid or dmg <= 0:
        return out
    kind = dice_out.get("kind")
    if kind in ("attack", "opportunity_attack") and not dice_out.get("hit"):
        return out
    if kind == "cast":
        if not dice_out.get("hit", True) and not dice_out.get("auto_hit"):
            return out
        if dice_out.get("save_success") and dmg <= 0:
            return out
    for c in (state.get("combat", {}) or {}).get("combatants", []):
        if c.get("cid") == tcid:
            hp_before = int(c.get("hp") or 0)
            dice_out["target_cid"] = tcid
            dice_out["target_name"] = c.get("name", "")
            dice_out["target_hp_before"] = hp_before
            dice_out["target_killed"] = dmg >= hp_before > 0
            break
    return out


# ──────────────────────────────────────────────────────────────────────────
# 遭遇系统 + 时间推进
# ──────────────────────────────────────────────────────────────────────────

# 野外/危险场景关键词
_WILD_SCENE_KEYWORDS = (
    "野", "林", "山", "洞", "地城", "沼泽", "荒", "路", "径", "谷", "废墟",
    "forest", "dungeon", "cave", "wild", "road", "mountain", "swamp", "ruin",
)
# 镇内/室内等安全场景关键词
_SAFE_SCENE_KEYWORDS = (
    "镇", "村", "城", "市", "酒馆", "旅舍", "旅店", "客栈", "庙", "神殿", "教堂",
    "商店", "店铺", "家", "屋内", "室内", "书房", "大厅", "王宫", "城堡",
    "tavern", "inn", "town", "village", "city", "indoor", "shop", "temple",
)

# 动作→时间推进（分钟）
_ACTION_MINUTES = {"travel": 60, "explore": 30, "search": 10, "study": 10, "ability_check": 10}
# 遭遇时钟：每 4 游戏小时允许 1 次遭遇检定
_ENCOUNTER_CHECK_INTERVAL_MIN = 240
# 非战斗遭遇叙述提示
_ENCOUNTER_HINTS = {
    "environment": "环境事件：天气骤变/地形阻碍/自然奇观等，呈现为旅途插曲",
    "omen": "痕迹预兆：生物足迹/营地残骸/远处烟火等，暗示附近有威胁但未遭遇",
    "npc": "NPC相遇：旅人/商人/巡逻队等友善或中立角色，可互动",
}


def _scene_blocks_encounter(camp) -> bool:
    """场景过滤（矩阵#2）：镇内/室内等安全场景不刷野外战斗遭遇。"""
    try:
        sc = store.get_scene(camp)
    except Exception:
        return False
    if not sc:
        return False
    text = f"{sc.location or ''} {sc.environment or ''}".lower()
    if not text.strip():
        return False
    if any(k in text for k in _WILD_SCENE_KEYWORDS):
        return False
    return any(k in text for k in _SAFE_SCENE_KEYWORDS)


def _pick_encounter_enemies(ch) -> tuple:
    """按角色等级(CR段)从 monsters 表选遭遇怪。"""
    n = 1 if engine_dice.roll_die(2) == 1 else 2
    try:
        from ...data import monsters as _mon
        _pool = _mon.pick_encounter_pool(ch.level)
        if n >= 2:
            _low = [m for m in _pool if getattr(m, "cr", 1) <= 0.5]
            _sel = _low if _low else _pool
        else:
            _sel = _pool
        _m = _sel[engine_dice.roll_die(len(_sel)) - 1] if _sel else None
    except Exception:
        _m = None
    if _m:
        _md = _m.to_combatant_dict()
        return [dict(_md) for _ in range(n)], _m.name
    return ([{"name": "哥布林", "dex_mod": 2, "side": "enemy", "hp_max": 7,
              "attack_bonus": 4, "damage_dice": "1d6+2", "damage_type": "挥砍"}
             for _ in range(n)], "哥布林")


def _encounter_type(roll: int) -> str:
    """遭遇类型分布（d20）。"""
    if roll <= 10:
        return "combat"
    if roll <= 15:
        return "environment"
    if roll <= 19:
        return "omen"
    return "npc"


def advance_game_time(camp: int, minutes: int) -> dict:
    """推进战役游戏内时间（矩阵#8）。

    ★ engine.exploration_clock: 用 ExplorationClock.advance_hours 权威计算
      日/时刻（含昼夜/时段时间），替代手写换算。
    """
    info: dict = {"advanced": minutes}
    try:
        c = store.get_campaign(camp)
        if not c:
            return info
        flags = c.world_flags
        before = int(flags.get("game_minutes", 8 * 60))
        after = before + max(0, int(minutes))
        flags["game_minutes"] = after
        c.set_world_flags(flags)
        store.save_campaign(c)
        # 权威时钟计算（engine.exploration_clock）
        try:
            from ...engine.exploration_clock import ExplorationClock
            _clock = ExplorationClock()
            _b = before
            _clock.current_time = f"{(_b % 1440) // 60:02d}:{(_b % 60):02d}"
            _clock.current_day = _b // 1440 + 1
            _adv = _clock.advance_hours(max(1, minutes // 60))
            day = _clock.current_day
            _h, _m = map(int, _clock.current_time.split(":"))
            hour = _h
            clock = ("凌晨" if hour < 6 else "早晨" if hour < 9 else
                     "上午" if hour < 12 else "午后" if hour < 14 else
                     "下午" if hour < 17 else "黄昏" if hour < 20 else "夜晚")
        except Exception:
            day = after // 1440 + 1
            hour = (after % 1440) // 60
            clock = ("凌晨" if hour < 6 else "早晨" if hour < 9 else
                     "上午" if hour < 12 else "午后" if hour < 14 else
                     "下午" if hour < 17 else "黄昏" if hour < 20 else "夜晚")
        info.update({"minutes_before": before, "minutes_after": after,
                     "day": day, "clock": clock})
    except Exception as e:
        _log.debug("游戏时间推进失败 campaign=%s: %s", camp, e)
    return info


def _encounter_clock_allows(camp: int, now_min: int) -> tuple:
    """遭遇时钟（矩阵#4）：每 4 游戏小时最多 1 次遭遇检定。"""
    try:
        c = store.get_campaign(camp)
        if not c:
            return True, 0
        flags = c.world_flags
        last = int(flags.get("encounter_last_check_min", -10 ** 9))
        wait = _ENCOUNTER_CHECK_INTERVAL_MIN - (now_min - last)
        if wait > 0:
            return False, wait
        flags["encounter_last_check_min"] = now_min
        c.set_world_flags(flags)
        store.save_campaign(c)
        return True, 0
    except Exception:
        return True, 0


def with_encounter(state, ch, dice_out: dict) -> dict:
    """探索类动作统一处理（矩阵#1/#2/#4/#5/#6/#8，BUG#6 修复）。"""
    out: dict = {"dice": dice_out}
    camp = state.get("campaign_id")
    if not camp or not ch or ch.dead or dice_out.get("error"):
        return out
    if state.get("combat", {}).get("active"):
        return out
    time_info = advance_game_time(camp, _ACTION_MINUTES.get(dice_out.get("kind"), 10))
    if time_info.get("day"):
        dice_out["time"] = time_info
    if _scene_blocks_encounter(camp):
        dice_out["encounter"] = {"triggered": False, "suppressed": "safe_scene"}
        return out
    allowed, wait = _encounter_clock_allows(camp, int(time_info.get("minutes_after", 0)))
    if not allowed:
        dice_out["encounter"] = {"triggered": False, "suppressed": "clock",
                                 "next_check_in_min": wait}
        return out
    enc = exploration_mod.random_encounter_check()
    enc_info = dataclasses.asdict(enc)
    if not enc.triggered:
        dice_out["encounter"] = enc_info
        return out
    enc_type = _encounter_type(engine_dice.roll_die(20))
    enc_info["encounter_type"] = enc_type
    if enc_type != "combat":
        enc_info.update({"combat_started": False,
                         "prompt_hint": _ENCOUNTER_HINTS.get(enc_type, "")})
        dice_out["encounter"] = enc_info
        return out
    enemies, enc_name = _pick_encounter_enemies(ch)
    enc_state = {"character_id": state.get("character_id"), "campaign_id": camp}
    enc_dice = resolve_start_combat(enc_state, ch,
                                    {"action_type": "start_combat", "enemies": enemies})
    enc_info.update({"combat_started": True, "enemy_name": enc_name,
                     "enemy_count": len(enemies),
                     "surprise": enc_dice.get("dice", {}).get("surprise", {}),
                     "initiative_order": enc_dice.get("dice", {}).get("initiative_order", [])})
    dice_out["encounter"] = enc_info
    out["combat"] = enc_dice.get("combat", {})
    return out
