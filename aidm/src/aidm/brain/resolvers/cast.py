"""resolvers.cast — 施法检定 + 伤害/效果计算。

★ SPL-001 委托关系说明:
  本 resolver 为薄包装层——构建 CasterState 和目标列表，
  然后委托 engine.spellcasting.cast_spell() 进行权威施法结算。
  cast_spell() 实现 Plan/Commit 两阶段施法 (SPL-013)：
    - 法术存在性校验 (SPL-002)
    - 成分校验 (R-SPL-010~013)
    - 反应可用性校验 (R-SPL-006)
    - 法术位可用性校验 (R-SPL-002)
    - 每回合一法术位法术校验 (R-SPL-007)
    - 原子消耗资源 (SPL-014: 戏法/仪式/失败不消耗法术位)
  本 resolver 负责:
    - 从 Character 构建 CasterState
    - 从 intent 和战斗状态构建目标列表
    - 将 cast_spell() 的返回格式适配为 apply_node 期望的 dice 结构
  禁止: 在本 resolver 中直接做施法计算或法术位消耗。
"""

from __future__ import annotations

import json

from ...engine import check, conditions, damage
from ...engine import dice as engine_dice
from ...engine.spellcasting import (
    CasterState,
    cast_spell,
    check_casting_components,
)
from ..utils import CLASS_CAST_ABILITY, target_condition_state


def resolve_cast(ch, it) -> dict:
    """施法检定 + 伤害/效果掷骰。R-DMG-002/R-SPL-021/022/CHK-011/014

    ★ SPL-001: 本函数为施法结算的【唯一权威入口】的薄包装。
      所有施法逻辑由 engine.spellcasting.cast_spell() 处理。
    """
    # 施法资格校验：非施法职业不能施法（R-SPL-001 施法者前提）
    if ch.char_class not in CLASS_CAST_ABILITY:
        return {"kind": "cast", "error": f"{ch.char_class} 不会施法，无法施展法术"}

    spell_name = it.get("spell_name", "")

    # SPL-003: 拥有性门控——通过 SpellSourceRegistry 验证施法资格
    if spell_name:
        from ...engine.spell_sources import build_registry_from_character
        registry = build_registry_from_character(ch)
        if not registry.can_cast(spell_name):
            return {"kind": "cast",
                    "error": f"尚未学会或准备法术「{spell_name}」，无法施展"}

    # —— 构建 CasterState ——
    # ★ engine.spell_slots / engine.multiclass: 法术位上权威计算（含多职业法术位合并）
    _max_slots = {}
    try:
        from ...engine.spell_slots import SpellSlotCalculator
        from ...engine.multiclass import multiclass_caster_level, multiclass_spell_slots
        _cl = getattr(ch, "class_levels", None) or {}
        if _cl:
            _max_slots = SpellSlotCalculator.calculate_slots(_cl) or {}
            # ★ CHR-006: 多职业合并法术位（engine.multiclass 权威合并）
            _merged = multiclass_spell_slots(_cl)
            if _merged:
                _max_slots = _merged
        else:
            _max_slots = SpellSlotCalculator.slots_for_class_level(
                ch.char_class, ch.level) or {}
    except Exception:
        _max_slots = {}
    caster = CasterState(
        caster_id=str(getattr(ch, "id", "unknown")),
        class_name=ch.char_class,
        level=ch.level,
        ability_scores=ch.abilities,
        spell_slots=ch.spell_slots,
        max_spell_slots=_max_slots,  # ★ SPL-003: 权威法术位上限
        spells_cast_with_slot_this_turn=int(it.get("_spells_cast_this_turn", 0)),
        current_turn_key=it.get("_turn_key"),
        concentrating_on=getattr(ch, "concentration_spell", None) or None,
    )

    # —— 构建目标列表 ——
    targets = _build_targets(ch, it)

    # ★ engine.spell_targeting / spell_targeting_ext / aoe: 目标范围与 AoE 校验
    targets = _validate_spell_targets(ch, it, targets)

    # —— 确定法术位环阶 ——
    slot_level = it.get("spell_level")
    if slot_level is not None:
        slot_level = int(slot_level)
    # 戏法传 None 或 0
    if slot_level == 0:
        slot_level = None

    # —— 仪式施法标志 ——
    ritual = bool(it.get("ritual", False))

    # ★ SPL-011: 从角色装备推导成分参数（空手/材料包/法器）——
    # engine.component_check 权威校验（与旧估算互为校验）
    _inv = getattr(ch, "inventory", None) or []
    component_kwargs = {
        "muted": bool(it.get("muted", False)),
        "silenced": bool(it.get("silenced", False)),
        "free_hands": _estimate_free_hands(ch),
        "has_material_pouch": _has_component_pouch(_inv),
        "has_focus": _has_spell_focus(_inv, ch.char_class),
        "has_specific_material": bool(it.get("has_specific_material", False)),
    }
    try:
        from ...engine.component_check import (
            ComponentType,
            EquipmentSlotState,
            check_casting_components as engine_check_components,
        )
        _slots = getattr(ch, "equipment_slots", None) or {}
        _cc = engine_check_components(
            components={ComponentType.SOMATIC, ComponentType.MATERIAL},
            equipment=EquipmentSlotState(
                main_hand=_slots.get("main_hand", "") or "",
                off_hand=_slots.get("off_hand", "") or "",
                armor=_slots.get("armor", "") or "",
                focus=_slots.get("focus", "") or "",
            ),
            inventory=list(_inv),
        )
        # 权威结果回填（引擎判定优先）
        if _cc.free_hands is not None:
            component_kwargs["free_hands"] = _cc.free_hands
        component_kwargs["has_focus"] = component_kwargs["has_focus"] or _cc.has_focus
        component_kwargs["has_material_pouch"] = (
            component_kwargs["has_material_pouch"] or _cc.has_material_pouch)
    except Exception:
        pass

    # ★ SPL-012: 从角色物品栏构建 MaterialTracker（有价/消耗材料真实扣除）
    material_tracker = None
    try:
        from ...engine.material_cost import MaterialTracker
        _tracker = MaterialTracker()
        for item_name in _inv:
            _tracker.add_material(str(item_name), 1)
        # 结构化物品也加入（item_id 作为材料 tag）
        for item in (getattr(ch, "items_structured", None) or []):
            _iid = item.get("item_id") or item.get("name") or ""
            if _iid:
                _tracker.add_material(_iid, int(item.get("quantity", 1)))
        material_tracker = _tracker
    except Exception:
        material_tracker = None

    # ★ SPL-009/SPL-015: 持续效果调度器与触发窗口注册表（模块级单例）
    duration_scheduler = None
    trigger_window_registry = None
    try:
        from ...engine.spell_duration import DurationScheduler
        from ...engine.spell_trigger_window import TriggerWindowRegistry
        duration_scheduler = DurationScheduler()
        trigger_window_registry = TriggerWindowRegistry()
    except Exception:
        pass

    # —— 委托 cast_spell 进行权威施法结算 ——
    result = cast_spell(
        caster=caster,
        spell_name=spell_name,
        slot_level=slot_level,
        targets=targets,
        ritual=ritual,
        component_kwargs=component_kwargs,
        material_tracker=material_tracker,
        duration_scheduler=duration_scheduler,
        trigger_window_registry=trigger_window_registry,
    )

    # —— 将 cast_spell 返回格式适配为 apply_node 期望的 dice 结构 ——
    return _adapt_cast_result(result, ch, it)


# ──────────────────────────────────────────────────────────────────────────
# 目标构建
# ──────────────────────────────────────────────────────────────────────────

def _build_targets(ch, it) -> list[dict]:
    """从 intent 和战斗状态构建 cast_spell 期望的目标列表。

    每个目标 dict 包含:
        ac: 护甲等级
        save_bonus: 豁免加值
        save_prof: 是否熟练该豁免
        resistances: 抗性列表
        vulnerabilities: 易伤列表
        immunities: 免疫列表
        prof_bonus: 熟练加值
    """
    targets = []

    # 单目标法术
    target_ac = int(it.get("target_ac") or 10)
    resists = it.get("resistances", [])
    vulns = it.get("vulnerabilities", [])
    immuns = it.get("immunities", [])

    tgt = {
        "ac": target_ac,
        "save_bonus": int(it.get("target_save_bonus") or 0),
        "save_prof": bool(it.get("target_save_prof", False)),
        "resistances": resists,
        "vulnerabilities": vulns,
        "immunities": immuns,
        "prof_bonus": ch.prof(),
    }
    targets.append(tgt)

    return targets


def _validate_spell_targets(ch, it, targets: list[dict]) -> list[dict]:
    """SPL-006/SPL-015: 施法目标范围校验 + AoE 区域判定 + 多射线拆分。

    接线:
      - engine.spell_targeting.SpellTargetingService: 目标合法性（距离/视线/数量）
      - engine.spell_targeting_ext.validate_spell_targets: 纯几何范围校验
      - engine.aoe.resolve_aoe: 区域法术命中哪些位置
      - engine.multiray_spell.resolve_multi_ray_spell: 多射线法术拆分（灼热射线）
    失败不阻断施法（返回原文 targets），仅附加校验信息。
    """
    spell_name = it.get("spell_name", "")
    if not spell_name:
        return targets
    try:
        # 1) 目标合法性（engine.spell_targeting）
        from ...engine.spell_targeting import SpellTargetingService
        svc = SpellTargetingService()
        _caster = {"entity_id": str(getattr(ch, "id", "unknown")),
                   "position": (0, 0)}
        _v = svc.validate_target(spell_name, _caster,
                                 {"entity_id": it.get("target_cid", "target"),
                                  "position": tuple(it.get("target_pos", (1, 0)))})
        if _v.get("reasons"):
            for t in targets:
                t["targeting_notes"] = _v["reasons"]

        # 2) 纯几何范围校验（engine.spell_targeting_ext）
        from ...engine.spell_targeting_ext import (
            RangeSpec,
            TargetSpec,
            validate_spell_targets,
        )
        _res = validate_spell_targets(
            range_spec=RangeSpec(range_ft=int(it.get("range_ft", 60) or 60)),
            target_spec=TargetSpec(target_count=1, target_type="creature"),
            area_spec=None,
            caster_pos=(0, 0),
            candidate_positions={it.get("target_cid", "target"): tuple(
                it.get("target_pos", (1, 0)))},
        )
        if _res.out_of_range:
            for t in targets:
                t["targeting_notes"] = list(t.get("targeting_notes", [])) + \
                    ["目标超出射程"]

        # 3) AoE 法术：区域命中目标（engine.aoe）
        area_shape = it.get("area_shape", "")
        if area_shape:
            from ...engine.aoe import resolve_aoe
            _in_area = resolve_aoe(
                shape=area_shape,
                origin=tuple(it.get("origin_pos", (0, 0))),
                size_ft=float(it.get("area_size_ft", 20) or 20),
                all_positions={it.get("target_cid", "target"): tuple(
                    it.get("target_pos", (1, 0)))},
            )
            if _in_area:
                for t in targets:
                    t["in_area"] = True

        # 4) 多射线法术：拆分射线数（engine.multiray_spell）
        if it.get("num_rays"):
            from ...engine.multiray_spell import resolve_multi_ray_spell
            _mr = resolve_multi_ray_spell(
                spell_name=spell_name,
                num_rays=int(it["num_rays"]),
                target_assignments=[it.get("target_cid", "target")],
                target_acs={it.get("target_cid", "target"): int(
                    it.get("target_ac", 10) or 10)},
                damage_per_ray=int(it.get("damage_per_ray", 6) or 6),
            )
            for t in targets:
                t["num_rays"] = _mr.total_rays
    except Exception:
        pass
    return targets


# ──────────────────────────────────────────────────────────────────────────
# 结果适配
# ──────────────────────────────────────────────────────────────────────────

def _adapt_cast_result(result: dict, ch, it) -> dict:
    """将 cast_spell() 的返回格式适配为 apply_node 期望的 dice 结构。

    cast_spell 返回:
        success, spell, slot_level, slot_consumed, ritual, ritual_time_extra,
        effect_type, save_dc, attack_bonus, effective_level, results, errors

    apply_node 期望 (dice 字段):
        kind="cast", spell_name, spell_level, spell_save_dc, spell_attack_bonus,
        hit, damage, damage_type, save_success, auto_hit, concentrating_on,
        spell_dice, d20, save_total, raw_damage, resisted, vulnerable, immune
    """
    # 失败情况
    if not result.get("success"):
        errors = result.get("errors", [])
        error_msg = errors[0] if errors else "施法失败"
        return {"kind": "cast", "error": error_msg, "errors": errors}

    spell_name = result.get("spell", "")
    effect_type = result.get("effect_type", "")
    save_dc = result.get("save_dc", 0)
    attack_bonus = result.get("attack_bonus", 0)
    slot_level = result.get("slot_level", 0)
    slot_consumed = result.get("slot_consumed", False)
    ritual = result.get("ritual", False)
    ritual_time_extra = result.get("ritual_time_extra", 0)
    effective_level = result.get("effective_level", 0)
    concentration_set = result.get("concentration_set", False)
    results_list = result.get("results", [])

    # 从第一个结果中提取主要数据
    first_result = results_list[0] if results_list else {}

    out = {
        "kind": "cast",
        "spell_name": spell_name,
        "spell_level": slot_level,
        "spell_save_dc": save_dc,
        "spell_attack_bonus": attack_bonus,
        "effect_type": effect_type,
        "ritual": ritual,
        "ritual_time_extra": ritual_time_extra,
        "effective_level": effective_level,
        "slot_consumed": slot_consumed,
        "concentration_set": concentration_set,
    }

    # ★ SPL-008: 透传 Effect DSL 事件列表（供 apply/UI 消费）
    effect_events = result.get("effect_events") or []
    if effect_events:
        out["effect_events"] = effect_events

    # ★ SPL-009/012/015: 透传持续时间调度、材料消耗与触发窗口状态
    if result.get("scheduled_effect_id"):
        out["scheduled_effect_id"] = result["scheduled_effect_id"]
    if result.get("trigger_window_registered"):
        out["trigger_window_registered"] = True
    if result.get("material_consumed"):
        out["material_consumed"] = True

    # 根据效果类型适配结果
    if effect_type == "attack_roll":
        # 法术攻击检定型
        atk_roll = first_result.get("attack_roll", 0)
        atk_total = first_result.get("attack_total", 0)
        hit = first_result.get("hit", False)
        crit = first_result.get("crit", False)
        dmg_data = first_result.get("damage")

        out.update({
            "d20": atk_roll,
            "spell_attack_total": atk_total,
            "hit": hit,
            "crit": crit,
            "auto_hit": False,
        })

        if dmg_data:
            out.update({
                "damage": dmg_data.get("total", 0),
                "damage_type": dmg_data.get("type", ""),
                "damage_rolls": dmg_data.get("rolls", []),
                "resisted": dmg_data.get("resisted", False),
                "vulnerable": dmg_data.get("vulnerable", False),
                "immune": dmg_data.get("immune", False),
            })

    elif effect_type == "saving_throw":
        # 豁免型法术
        save_roll = first_result.get("save_roll", 0)
        save_total_val = first_result.get("save_total", 0)
        save_success = first_result.get("save_success", False)
        dc_val = first_result.get("dc", save_dc)
        dmg_data = first_result.get("damage")

        out.update({
            "d20": save_roll,
            "save_total": save_total_val,
            "save_success": save_success,
            "hit": True,  # 豁免型法术默认生效
            "auto_hit": True,
        })

        if dmg_data:
            out.update({
                "damage": dmg_data.get("total", 0),
                "damage_type": dmg_data.get("type", ""),
                "damage_rolls": dmg_data.get("rolls", []),
                "raw_damage": dmg_data.get("raw", 0),
                "resisted": dmg_data.get("resisted", False),
                "vulnerable": dmg_data.get("vulnerable", False),
                "immune": dmg_data.get("immune", False),
            })

    elif effect_type == "automatic":
        # 自动命中型法术（魔法飞弹）
        out.update({
            "hit": True,
            "auto_hit": True,
        })

        dmg_data = first_result.get("damage")
        if dmg_data:
            out.update({
                "damage": dmg_data.get("total", 0),
                "damage_type": dmg_data.get("type", ""),
                "damage_rolls": dmg_data.get("rolls", []),
                "resisted": dmg_data.get("resisted", False),
                "vulnerable": dmg_data.get("vulnerable", False),
                "immune": dmg_data.get("immune", False),
            })

    elif effect_type == "heal":
        # 治疗型法术
        heal_data = first_result.get("heal")
        out.update({
            "hit": True,
            "auto_hit": True,
            "damage_type": "治疗",
        })

        if heal_data:
            out.update({
                "damage": heal_data.get("total", 0),
                "damage_rolls": heal_data.get("rolls", []),
                "raw_damage": heal_data.get("total", 0),
            })

    elif effect_type == "shield":
        # 护盾术：反应 +5 AC
        out.update({
            "hit": True,
            "auto_hit": True,
            "damage_type": "",
            "ac_bonus": first_result.get("ac_bonus", 5),
        })

    # 专注信息
    if concentration_set:
        out["concentrating_on"] = spell_name

    # 输出展示用的法术骰表达式
    spell_dice = ""
    if effect_type in ("attack_roll", "saving_throw", "automatic"):
        # 从 damage_rolls 推断
        rolls = out.get("damage_rolls", [])
        if rolls:
            spell_dice = f"{len(rolls)}d{rolls[0] if isinstance(rolls[0], int) else 1}"
    out["spell_dice"] = spell_dice or "1d8"

    return out


# ──────────────────────────────────────────────────────────────────────────
# 施法成分辅助：从角色装备推导空闲手/材料包/法器
# ──────────────────────────────────────────────────────────────────────────

# 已知法器/圣徽关键词（用于从物品栏匹配）
_FOCUS_KEYWORDS = ("法器", "圣徽", "奥术法器", "德鲁伊法器")
_POUCH_KEYWORDS = ("材料包", "材料组件包", "施法材料包")


def _estimate_free_hands(ch) -> int:
    """从角色装备粗略估算空闲手数量。

    规则: R-SPL-012 姿势成分需空闲手
    简化模型：无武器=2空手；单手武器=1空手；双手武器=0空手。

    ★ engine.equipment_slots: 优先用 EquipmentSlotsManager 权威计算
      （装备槽位/双手武器/盾牌判定），失败回退关键词估算。
    """
    try:
        from ...engine.equipment_slots import (
            EquipmentSlotsManager,
            ItemInstance,
            SlotType,
        )
        _slots = getattr(ch, "equipment_slots", None) or {}
        mgr = EquipmentSlotsManager()
        for slot_name, item_id in _slots.items():
            if not item_id:
                continue
            try:
                _slot = SlotType(slot_name)
            except ValueError:
                continue
            mgr.equip(ItemInstance(item_id=item_id, name=item_id),
                      _slot)
        return mgr.get_free_hands()
    except Exception:
        pass
    weapon = getattr(ch, "equipped_weapon", "") or ""
    if not weapon:
        return 2
    # 常见双手武器关键词（简化判断）
    _two_handed = ("巨剑", "巨斧", "长矛", "长棍", "战棍", "弩", "大锤",
                   "长弓", "重弩", "戟", "砍刀", "大剑")
    for kw in _two_handed:
        if kw in weapon:
            return 0
    # ITEM-002: 盾牌必须装备在 off_hand 槽位才生效，背包中的盾牌不计入
    _slots = getattr(ch, "equipment_slots", {}) or {}
    _off_hand = _slots.get("off_hand", "") or ""
    has_shield = "盾牌" in _off_hand
    if has_shield:
        return 0
    # 默认单手武器 → 1空手
    return 1


def _has_component_pouch(inventory: list[str]) -> bool:
    """物品栏是否包含材料包。"""
    for item in inventory:
        for kw in _POUCH_KEYWORDS:
            if kw in item:
                return True
    return False


def _has_spell_focus(inventory: list[str], char_class: str) -> bool:
    """物品栏是否包含该职业可用的法器/圣徽。

    规则: R-SPL-013 法器职业限制
    """
    from ...engine.spellcasting import can_use_focus
    for item in inventory:
        # 直接匹配材料包关键词 → 不算法器
        if any(kw in item for kw in _POUCH_KEYWORDS):
            continue
        # 匹配法器类型
        for focus_type in ("奥术法器", "德鲁伊法器", "圣徽"):
            if focus_type in item and can_use_focus(char_class, focus_type):
                return True
        # 通用"法器"关键词
        if "法器" in item:
            for ft in ("奥术法器", "德鲁伊法器"):
                if can_use_focus(char_class, ft):
                    return True
    return False
