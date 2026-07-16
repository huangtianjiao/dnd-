# ENGINE_REFERENCE — 规则引擎函数签名表

> 对应源码：`src/aidm/engine/`（10 模块）。
> 设计原则：所有掷骰用 `secrets`（密码学随机），每次返回详细结果供审计；LLM 不得绕过代码判定。每函数标注 `RULE_SPEC.md` 规则点 ID + topics 原文路径，形成"代码↔规则"双向索引。每个模块末尾自带 `_self_test()` 自检。

## 模块依赖链

```
dice ──┬── check ──┬── combat ──┬── actions ──┐
       │           │            │             ├── opportunity_attack
       ├── damage  ├── conditions│             │
       │           │            ├── concentration
       │           │            │
       └── (基础)  └── core_loop (独立依赖 check/dice)
                                    │
                       spellcasting ── 依赖 data.spells
```

---

## 1. dice.py — 骰子引擎（纯骰子与基础数值）

| 函数名 | 签名 | 返回 | 功能 | 规则点 |
|---|---|---|---|---|
| `roll_die` | `(sides: int) -> int` | `[1, sides]` | 掷一颗 M 面骰 | R-CHK-025 |
| `round_down` | `(value: float) -> int` | 整数 | 向下取整（游戏除法/乘法结果） | R-GLS-005 |
| `ability_modifier` | `(score: int) -> int` | 调整值 | 属性调整值 = floor((score-10)/2) | R-CHK-024 |
| `proficiency_bonus` | `(level_or_cr: float) -> int` | +2..+9 | 熟练加值（按等级/CR 查表） | R-CHK-015/016 |
| `parse_dice_expression` | `(expression: str) -> tuple[list, int]` | (骰子项, 常数) | 解析 "3d8+5" 等表达式 | R-CHK-025 |
| `roll_dice` | `(expression: str, *, crit: bool = False) -> RollResult` | RollResult | 掷骰表达式；crit=True 骰数翻倍（常数不加倍） | R-CHK-025, R-CMB-029 |
| `roll_d20` | `(advantage=False, disadvantage=False) -> D20Roll` | D20Roll | 掷 d20 处理优/劣势；同时存在则抵消 | R-CHK-004/005 |
| `roll_d100` | `() -> int` | 1..100 | 百分骰 d100 | R-CHK-026 |
| `roll_d3` | `() -> int` | 1..3 | d3 = ceil(d6/2) | R-CHK-027 |
| `roll_percent_chance` | `(percent: int) -> tuple[bool, int]` | (是否发生, 骰值) | 百分比概率判定（≤percent 则发生） | R-CHK-029 |
| `roll_random_table` | `(table: dict, die_notation="1d100") -> tuple` | (结果, 骰值) | 随机表掷骰查表 | R-CHK-030 |

数据类：`RollResult`(total, rolls, expression, dice_rolls, modifier, crit, notes)、`D20Roll`(used, rolls, mode)。

---

## 2. check.py — D20 检定引擎

天然 20/1 仅对攻击生效（R-DM-010）。

| 函数名 | 签名 | 返回 | 功能 | 规则点 |
|---|---|---|---|---|
| `dc_by_label` | `(label: str) -> int` | DC | 按难度返回范例 DC（非常容易5/容易10/中等15/困难20/非常困难25/近乎不可能30） | R-CHK-009 |
| `calc_save_dc` | `(ability_mod: int, prof: int) -> int` | DC | 施法豁免 DC = 8 + 属性调整值 + 熟练加值 | R-DM-002 |
| `resolve_advantage` | `(adv_count: int, dis_count: int) -> tuple[bool, bool]` | (优势, 劣势) | 统计优劣势来源数解析为布尔（同时存在则抵消） | R-CHK-005, R-DM-006 |
| `passive_check` | `(modifiers: Iterable[int]) -> int` | 整数 | 被动检定值 = 10 + sum(调整值) | R-DM-012 |
| `ability_check` | `(mod, prof, proficient, dc, advantage=False, disadvantage=False, circ=0) -> CheckResult` | CheckResult | 属性检定：d20+调整值+(熟练加值 if 熟练)+临时加值 ≥ DC 则成功 | R-CHK-010 |
| `saving_throw` | `(mod, prof, proficient, dc, advantage=False, disadvantage=False, waive=False, circ=0) -> CheckResult` | CheckResult | 豁免检定；waive=True 主动放弃判失败 | R-CHK-011 |
| `attack_roll` | `(bonus, ac, advantage=False, disadvantage=False, circ=0) -> AttackResult` | AttackResult | 攻击检定：d20+命中加值 vs AC；天然20必出+重击，天然1必失手 | R-CMB-017/022/023, R-DM-010 |
| `is_natural_20` | `(d20: int) -> bool` | bool | 是否天然 20 | R-CMB-022 |
| `is_natural_1` | `(d20: int) -> bool` | bool | 是否天然 1 | R-CMB-023 |

内部：`_d20_check_core(mod, prof, proficient, target, advantage, disadvantage, circ=0) -> CheckResult`（R-CHK-001 三步流程核心）。
数据类：`CheckResult`(success, total, d20, rolls, mode, target, margin, modifier)；`AttackResult(CheckResult)` 增加 hit, crit。

---

## 3. damage.py — 伤害系统

| 函数名 | 签名 | 返回 | 功能 | 规则点 |
|---|---|---|---|---|
| `apply_damage_pipeline` | `(raw, damage_type, flat_modifiers=(), resistances=(), vulnerabilities=(), immunities=()) -> DamageResult` | DamageResult | 结算顺序：免疫→数值修正→一项抗性(减半)→一项易伤(翻倍)→下限0。"*" 代表全伤害通配 | R-QCK-002, R-DMG-006/003/004/002 |
| `roll_damage` | `(req: DamageRequest, *, resistances=(), vulnerabilities=(), immunities=()) -> DamageResult` | DamageResult | 掷伤害骰并跑管线；重击骰数翻倍 | R-DMG-001, R-CMB-029 |
| `resolve_stat_block` | `(notation: str, mode="roll") -> int` | 整数 | 数据卡记法 "4(1d4+2)"：fixed 取固定值 / roll 掷表达式 | R-GLS-086 |
| `apply_damage_to_hp` | `(hp, temp_hp, max_hp, dmg) -> tuple[int, int]` | (new_hp, new_temp_hp) | 受伤害：先扣临时HP，余下扣真正HP（不低于0） | R-DMG-009/007, R-GLS-085 |
| `grant_temp_hp` | `(current_temp: int, new_temp: int) -> int` | 整数 | 临时HP 不叠加，取较大者 | R-DMG-010 |
| `apply_healing` | `(hp, max_hp, heal) -> int` | 整数 | 治疗：加到当前HP，不超过上限 | R-DMG-020 |
| `check_massive_damage` | `(current_hp, max_hp, dmg) -> bool` | bool | 过量伤害致死：HP降至0且余量≥HP上限则立即死亡 | R-DMG-014 |
| `check_hp_max_zero_death` | `(max_hp: int) -> bool` | bool | HP上限归0则死亡 | R-DMG-013 |
| `death_save` | `(tracker: DeathTracker) -> dict` | dict | 死亡豁免：1d20≥10成功；3成功稳定/3失败死亡；天然1记两次失败，天然20恢复1HP | R-DMG-017 |
| `damage_at_zero_hp` | `(tracker: DeathTracker, dmg: int, is_crit: bool, max_hp: int) -> dict` | dict | HP为0时受伤害：记死亡豁免失败（重击记两次）；伤害≥上限则死亡 | R-DMG-018 |
| `reset_death_counts_on_recovery` | `(tracker: DeathTracker) -> None` | None | 恢复任意HP时死亡豁免计数归零并解除昏迷 | R-ADD-008 |

数据类：`DamageRequest`(dice_expr, damage_type, ability_mod, add_mod, crit, flat_modifiers)、`DamageResult`(raw, final, damage_type, immune, resisted, vulnerable, dice_rolls, modifier, crit)、`DeathTracker`(successes, failures, stable, dead; 有 reset())。

---

## 4. combat.py — 战斗状态机

| 函数名 | 签名 | 返回 | 功能 | 规则点 |
|---|---|---|---|---|
| `roll_initiative` | `(combatants: list[Combatant]) -> list[Combatant]` | 排序后列表 | d20+敏捷调整值，突袭者劣势，降序排列；同组怪物共用先政 | R-CMB-002, R-GLS-009 |
| `resolve_initiative_ties` | `(tied_combatants) -> list` | 列表 | 先政平局处理 | R-CMB-003 |
| `start_combat` | `(combat: Combat, combatants) -> None` | None | 掷先政、排序、进入第1轮 | R-CMB-001/002/004 |
| `current_combatant` | `(combat: Combat) -> Optional[Combatant]` | Combatant? | 当前回合的参战者 | R-CMB-004 |
| `advance_turn` | `(combat: Combat) -> Optional[Combatant]` | Combatant? | 推进到下一参战者；轮次结束进入下一轮(+6秒) | R-CMB-001/004 |
| `can_take_action` / `can_take_bonus_action` / `can_take_reaction` | `(c: Combatant) -> bool` | bool | 查询是否还能执行动作/附赠动作/反应 | R-CMB-011/012/013 |
| `use_action` / `use_bonus_action` / `use_reaction` | `(c: Combatant) -> bool` | bool | 消耗一个动作/附赠动作/反应 | R-CMB-004/011/012/013 |
| `use_free_interaction` | `(c: Combatant) -> bool` | bool | 消耗本回合免费物件交互（每回合1次） | R-CMB-005 |
| `speed_to_squares` | `(speed_ft: int) -> int` | 格数 | 速度(尺)转格数 = speed/5 | R-CMB-032 |
| `move_cost` | `(distance_ft: int, difficult: bool = False) -> int` | 尺 | 计算移动消耗移动力（困难地形每尺2尺） | R-CMB-031 |
| `move` | `(c: Combatant, distance_ft: int, difficult: bool = False) -> int` | 实际移动尺数 | 消耗移动力移动；不足按可承受最大距离移动 | R-CMB-030/031 |
| `enter_square` | `(c: Combatant, difficult: bool = False) -> int` | 消耗格数 | 进入邻接格消耗移动力；困难地形2格 | R-CMB-033 |
| `get_size_footprint` | `(size: str) -> tuple[float, float]` | (空间尺, 占据格数) | 生物体型占据空间 | R-CMB-037 |
| `can_pass_through` | `(mover_size, creature_size, is_ally=False, is_incapacitated=False) -> bool` | bool | 是否能穿过某生物空间 | R-CMB-038 |
| `pass_cost_multiplier` | `(mover_size, creature_size, is_ally=False, is_incapacitated=False) -> int` | 1 或 2 | 穿过生物空间移动力倍率 | R-CMB-038 |
| `drop_prone` | `(c: Combatant) -> bool` | bool | 俯卧倒地；速度0时不能 | R-CMB-036 |
| `concentration_save_dc` | `(damage_taken: int) -> int` | DC | 专注伤害豁免 DC = max(10, floor(dmg/2))，至高30 | R-GLS-013 |
| `concentration_save` | `(con_mod, con_prof, prof, damage_taken) -> bool` | bool | 专注者受伤体质豁免维持专注 | R-GLS-013 |

常量 `FT_PER_SQUARE = 5`。内部 `_reset_turn_economy(c)`。
数据类：`Combatant`(cid, name, dex_mod, initiative, side, is_player, surprised, group_id + 动作经济字段 + 移动字段 + concentrating_on + disengage_active/dodge_active/hidden)、`Combat`(participants, initiative_order, round, current_index, active, seconds_elapsed)。

---

## 5. actions.py — 动作经济分派器（11 种战斗动作）

| 函数名 | 签名 | 返回 | 功能 | 规则点 |
|---|---|---|---|---|
| `action_attack` | `(attacker, target, weapon, advantage=False, disadvantage=False, target_ac=10) -> ActionResult` | ActionResult | 攻击动作：攻击检定→命中掷伤害（重击骰翻倍） | R-CMB-014/017/022/023/029 |
| `action_dash` | `(attacker: Combatant) -> ActionResult` | ActionResult | 疾走：给予等同于速度的额外移动力 | R-CMB-006 |
| `action_disengage` | `(attacker: Combatant) -> ActionResult` | ActionResult | 撤离：本回合移动不引发借机攻击 | R-CMB-007 |
| `action_dodge` | `(attacker: Combatant) -> ActionResult` | ActionResult | 回避：对自身攻击劣势，自身敏捷豁免优势 | R-CMB-008 |
| `action_help` | `(attacker, ally, target=None) -> ActionResult` | ActionResult | 协助：盟友下次对该目标攻击检定优势 | R-CMB-014 |
| `action_hide` | `(attacker, stealth_mod, stealth_prof, proficient, dc, advantage=False, disadvantage=False) -> ActionResult` | ActionResult | 躲藏：敏捷(隐匿)检定，成功进入隐形 | R-CMB-009 |
| `action_magic` | `(attacker, spell_name="", spell_dc=0) -> ActionResult` | ActionResult | 魔法：施展法术（占位，真正结算由 spellcasting） | R-CMB-014 |
| `action_ready` | `(attacker, trigger_condition, ready_action="attack") -> ActionResult` | ActionResult | 预备：设定触发条件，用反应执行 | R-CMB-014 |
| `action_search` | `(attacker, perception_mod, perception_prof, proficient, dc, ...) -> ActionResult` | ActionResult | 搜索：感知(洞悉/医药/察觉/求生)检定 | R-CMB-010 |
| `action_study` | `(attacker, intelligence_mod, intelligence_prof, proficient, dc, ...) -> ActionResult` | ActionResult | 研究：智力(奥秘/历史/调查/自然/宗教)检定 | R-CMB-010 |
| `action_utilize` | `(attacker, object_name="", ability_mod=0, prof=0, proficient=False, dc=0, ...) -> ActionResult` | ActionResult | 操作：使用非魔法物件 | R-CMB-014/005 |
| `resolve_combat_action` | `(action_type, attacker, target=None, weapon=None, **kwargs) -> ActionResult` | ActionResult | 分派并结算一次战斗动作（按 COMBAT_ACTIONS 表） | R-CMB-011/014 |

数据类：`ActionResult`(action_type, success, message, attack_result, damage_result, extra)、`WeaponProfile`(name, attack_bonus, damage_dice, damage_type, ability_mod, add_ability_mod_to_damage, crit)。常量 `COMBAT_ACTIONS`（11 个动作名 → 处理函数映射）。

---

## 6. spellcasting.py — 施法引擎

| 函数名 | 签名 | 返回 | 功能 | 规则点 |
|---|---|---|---|---|
| `compute_spell_save_dc` | `(caster: CasterState) -> int` | DC | 法术豁免 DC = 8 + 施法属性调整值 + 熟练加值 | R-SPL-021 |
| `compute_spell_attack_bonus` | `(caster: CasterState) -> int` | 加值 | 法术攻击加值 = 施法属性调整值 + 熟练加值 | R-SPL-022 |
| `has_spell_slot` | `(caster, slot_level) -> bool` | bool | 是否有指定环阶可用法术位 | R-SPL-002 |
| `consume_spell_slot` | `(caster, slot_level) -> bool` | bool | 消耗一个指定环阶法术位 | R-SPL-002 |
| `restore_slots_on_long_rest` | `(caster: CasterState) -> None` | None | 长休恢复所有已消耗法术位 | R-SPL-003 |
| `can_cast_by_components` | `(spell, caster, *, muted=False, silenced=False, free_hands=2, has_material_pouch=False, has_focus=False) -> bool` | bool | 校验施法者满足全部成分需求（V言语/S姿势/M材料） | R-SPL-010~013 |
| `resolve_upcast` | `(spell, slot_level, caster_level) -> dict` | dict | 升环效应解析（effective_level/damage_dice/heal_dice/num_attacks/num_darts） | R-SPL-004 |
| `cast_spell` | `(caster, spell_name, slot_level=None, targets=None, *, concentration_mgr=None, component_kwargs=None) -> dict` | dict | 施展法术主函数：戏法判定→成分校验→法术位消耗→升环→效应结算（attack_roll/saving_throw/automatic/heal/shield）→集中设置 | R-SPL-001~036 |

数据类：`CasterState`(caster_id, class_name, level, ability_scores, spell_slots, max_spell_slots, spells_cast_with_slot_this_turn, concentrating_on；属性 casting_ability/casting_ability_mod/proficiency_bonus)。

---

## 7. core_loop.py — 核心循环状态机

实现 D&D 5E 基本游戏模式（DM描绘→玩家行动→DM解决）。

| 函数名 | 签名 | 返回 | 功能 | 规则点 |
|---|---|---|---|---|
| `dc_by_difficulty` | `(label: str) -> int` | DC | 按任务难度返回范例 DC | R-CHK-009 |
| `should_roll_dice` | `(action_desc: str, situation: Any = None) -> ActionCertainty` | ActionCertainty | 判断行动是否需掷骰（CERTAIN/UNCERTAIN/IMPOSSIBLE） | 核心循环步骤3 |
| `resolve_action` | `(d20_result, modifiers, dc, *, rolls=None, mode="normal") -> ActionResult` | ActionResult | 解决行动结果：d20+修正值 vs DC | R-CHK-001 |

枚举：`CoreLoopState`(DM_DESCRIBE/PLAYER_ACT/DM_RESOLVE)、`ActionCertainty`(CERTAIN/UNCERTAIN/IMPOSSIBLE)。
数据类：`ActionResult`(action_type, success, certainty, message, check_result, extra)、`HeroicInspiration`(has_inspiration; grant()/consume()/reroll_with_inspiration()；上限1个，R-CHK-007)、`CoreLoopMachine`(state, iteration; advance()/reset()/run_full_cycle())。

---

## 8. conditions.py — 状态条件引擎（15 种状态 + 力竭）

`CONDITIONS` frozenset 含 15 项：目盲/魅惑/耳聋/恐慌/受擒/失能/隐形/麻痹/石化/力竭/中毒/倒地/束缚/震慑/昏迷。`INCAPACITATING` = {失能, 麻痹, 震慑, 昏迷, 石化}。`SPEED_ZERO_STATES` = {受擒, 麻痹, 石化, 束缚, 昏迷}。

| 函数名 | 签名 | 返回 | 功能 | 规则点 |
|---|---|---|---|---|
| `d20_penalty` | `(state: ConditionState) -> int` | 减值 | D20检定减值 = 力竭等级×2 | R-GLS-047 |
| `speed_after_conditions` | `(base_speed: int, state: ConditionState) -> int` | 速度 | 受状态影响后速度（速度归0状态→0；力竭-等级×5尺） | R-GLS-049/052/053/056/058/047 |
| `attack_modifiers` | `(attacker: ConditionState, target: ConditionState, distance_ft: int = 5) -> AttackModifiers` | AttackModifiers | 计算攻击优劣势与自动重击（麻痹/昏迷5尺内命中即重击） | R-GLS-044~058 |
| `concentration_broken_on_state_change` | `(new_state: ConditionState) -> bool` | bool | 陷入失能/昏迷/石化等是否打断专注 | R-GLS-050, R-SPL-019 |
| `long_rest_reduce_exhaustion` | `(state: ConditionState) -> None` | None | 长休力竭-1级（降至0结束） | R-GLS-047, R-QCK-004 |

数据类：`ConditionState`(conditions:set, exhaustion:int; add(cond)/remove(cond)/has(cond)/is_incapacitated()/is_dead_from_exhaustion() 力竭6级即死)、`AttackModifiers`(attacker_advantage, attacker_disadvantage, target_auto_crit_if_hit)。

---

## 9. concentration.py — 专注维持引擎

| 函数名 | 签名 | 返回 | 功能 | 规则点 |
|---|---|---|---|---|
| `concentration_save_dc` | `(damage_taken: int) -> int` | DC | 集中维持体质豁免 DC = max(10, floor(dmg/2))，至高30 | R-SPL-020, R-GLS-013 |

数据类：
- `ConcentrationSlot`(spell_id, caster_id; property is_concentrating)
- `ConcentrationManager`(slots:dict; set_concentration(caster_id, spell_id) 设置集中(旧自动结束,max1), break_concentration(caster_id), get_active_concentration(caster_id), concentration_save_on_damage(caster_id, damage_taken, con_mod, con_proficient, prof_bonus, advantage, disadvantage) → {success, dc, roll, total, broken, was_concentrating})

> 注：`concentration_save_dc` 与 `combat.concentration_save_dc` 是两个独立实现，逻辑一致。

---

## 10. opportunity_attack.py — 借机攻击

| 函数名 | 签名 | 返回 | 功能 | 规则点 |
|---|---|---|---|---|
| `can_make_opportunity_attack` | `(attacker, target, target_leaving_reach=True, target_visible=True) -> bool` | bool | 是否满足借机攻击触发条件（有反应+目标离开触及+可见+未撤离） | R-CMB-025/013/026 |
| `opportunity_attack` | `(attacker, target, weapon=None, target_ac=10, target_leaving_reach=True, target_visible=True, advantage=False, disadvantage=False) -> ActionResult` | ActionResult | 执行借机攻击：触发检查→消耗反应→攻击检定→命中掷伤害（重击骰翻倍）；weapon=None 为徒手打击 | R-CMB-025/017/022/023/029 |
