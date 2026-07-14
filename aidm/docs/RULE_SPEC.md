# D&D 5E 规则规格书（RULE_SPEC）

> 骰子引擎与判定模板的实现依据 + 规则↔函数反查索引。
> 数据源：`5echm_web` 规则书（data.js 6238 条 + topics 8644 页），已提取 141 页纯文本通读提炼。

## 文档说明

- **来源**：玩家手册2024 / 城主指南2024 / DM速查 / 术语汇编 的核心判定规则页，经 9 组并行提炼。
- **条目数**：364 条规则点，分 9 板块。
- **schema**：每条含 `摘要 / 数值·公式 / 状态读取 / 状态变更 / 出处 / 待实现函数 / 优先级`。
- **优先级**：`P0` 骰子引擎必需 ｜ `P1` 判定模板 ｜ `P2` 扩展规则。
- **用法**：①查规则→按"待实现函数"列定位代码；②写代码→按规则点原文实现，数值以"数值·公式"列为准；③写完在此回填实际函数签名与文件位置，形成双向索引。
- **硬性原则**：所有数值/骰子由代码执行，LLM 不得臆测；规则以本规格书原文为准，冲突时以出处页回溯。

## 目录

| 板块 | 前缀 | 条数 | 主题 |
|------|------|------|------|
| 1 检定机制 | R-CHK | 30 | d20检定/优劣势/属性检定/豁免/熟练/属性调整值/骰子 |
| 2 战斗与动作 | R-CMB | 46 | 战斗流程/动作经济/攻击命中/重击/移动/掩护/体型 |
| 3 伤害生命治疗 | R-DMG | 24 | 伤害骰/抗性易伤免疫/HP/临时HP/死亡豁免/治疗 |
| 4 状态与探索 | R-CON | 24 | 状态(索引)/躲藏/视野/旅行/交涉/案例 |
| 5 DM判定 | R-DM | 47 | DC设定/即兴伤害/先攻/怪物HP/旅行地形/天气/XP |
| 6 施法 | R-SPL | 36 | 法术环阶/法术位/成分/距离/持续时间/专注/法术DC |
| 7 装备护甲 | R-ITM | 42 | 护甲表/武器表/词条/精通/钱币/消耗品/制作 |
| 8 速查数值表 | R-QCK | 28 | 状态速查/力竭/掩护/坠落/陷阱/毒药/单位换算 |
| 9 术语汇编 | R-GLS | 87 | 状态详细效应/危害/感官/物件破坏/效应区域/移动 |
| 10 审计补遗 | R-ADD | 36 | 7组并行审计复核源文后补充的遗漏规则(+待补清单) |

---

## 1. 检定机制（R-CHK，30 条）

### R-CHK-001 D20检定三步流程
- 摘要: 行动结果不确定时掷d20决定成败，三步：掷d20→加调整值→比较目标数值
- 数值/公式: `total=d20+ability_mod+(prof_bonus if proficient else 0)+circ_mod; 成功 if total>=target_num`
- 状态读取: ability_mod, prof_bonus, proficient, target_num, advantage, circ_mod
- 状态变更: outcome=success/failure, total
- 出处: topics/玩家手册2024/进行游戏/D20检定.htm
- 待实现函数: d20_check(mod, prof, proficient, target, advantage, circ=0)->(success,total,rolls)
- 优先级: P0

### R-CHK-002 D20检定三种类型与目标值
- 摘要: D20检定分属性检定、豁免检定、攻击检定；属性/豁免的目标为DC，攻击的目标为AC
- 数值/公式: `check_type∈{ability,save,attack}; target = DC(ability/save) | AC(attack)`
- 状态读取: check_type, DC, AC
- 状态变更: target_num
- 出处: topics/玩家手册2024/进行游戏/D20检定.htm
- 待实现函数: resolve_target(check_type, dc, ac)->target_num
- 优先级: P1

### R-CHK-003 攻击检定命中判定
- 摘要: 攻击检定的目标数值为护甲等级(AC)，总掷>=AC则命中
- 数值/公式: `hit = (attack_total >= AC)`
- 状态读取: attack_total, AC
- 状态变更: outcome=hit/miss
- 出处: topics/玩家手册2024/进行游戏/D20检定.htm
- 待实现函数: attack_check(mod, prof, proficient, ac, advantage)->(hit,total)
- 优先级: P1

### R-CHK-004 优势与劣势掷骰
- 摘要: 优势掷两d20取高，劣势掷两d20取低
- 数值/公式: `rolls=[d20_1,d20_2]; d20_used = max(rolls) if advantage else (min(rolls) if disadvantage else rolls[0]); 普通时roll_count=1`
- 状态读取: advantage, disadvantage
- 状态变更: rolls, d20_used
- 出处: topics/玩家手册2024/进行游戏/优势_劣势.htm
- 待实现函数: roll_d20(advantage, disadvantage)->(used, rolls)
- 优先级: P0

### R-CHK-005 优势劣势不叠加与抵消
- 摘要: 多个优势或多个劣势仍只掷两d20；同时存在优势与劣势则两者抵消，只掷一d20
- 数值/公式: `has_adv=(adv_count>0); has_dis=(dis_count>0); if has_adv and has_dis: roll_count=1,adv=dis=False; elif has_adv or has_dis: roll_count=2; else: roll_count=1`
- 状态读取: adv_source_count, dis_source_count
- 状态变更: effective_advantage, effective_disadvantage, roll_count
- 出处: topics/玩家手册2024/进行游戏/优势_劣势.htm
- 待实现函数: resolve_advantage(adv_count, dis_count)->(roll_count, advantage, disadvantage)
- 优先级: P0

### R-CHK-006 优势劣势下重骰仅替换一骰
- 摘要: 具有优势/劣势时可重骰或替换的骰子只限一个，由玩家选择哪一个
- 数值/公式: `rerolled_dice_count = 1; 选择 rolls[index] 重骰/替换，其余保持`
- 状态读取: rolls, advantage/disadvantage, reroll_source
- 状态变更: rolls[index]
- 出处: topics/玩家手册2024/进行游戏/优势_劣势.htm
- 待实现函数: reroll_one_die(rolls, index)->rolls
- 优先级: P1

### R-CHK-007 英雄激励重骰
- 摘要: 拥有英雄激励可在任意骰子掷出后立即消耗它重骰，必须采用新结果；同时最多持有一个
- 数值/公式: `max_heroic_inspiration=1; if has_heroic_inspiration: has_heroic_inspiration-=1, reroll, must_use_new=True`
- 状态读取: has_heroic_inspiration, old_roll
- 状态变更: has_heroic_inspiration, roll_result(新)
- 出处: topics/玩家手册2024/进行游戏/优势_劣势.htm
- 待实现函数: heroic_inspiration_reroll(has_inspiration, old_roll)->(new_roll, has_inspiration)
- 优先级: P1

### R-CHK-008 人类每日英雄激励
- 摘要: 人类角色每天可获得一个英雄激励（受上限1约束）
- 数值/公式: `if race==human: has_heroic_inspiration = min(has_heroic_inspiration+1, 1) per day`
- 状态读取: race
- 状态变更: has_heroic_inspiration
- 出处: topics/玩家手册2024/进行游戏/优势_劣势.htm
- 待实现函数: grant_human_daily_inspiration(char)->has_heroic_inspiration
- 优先级: P2

### R-CHK-009 范例难度等级DC表
- 摘要: 属性检定常用DC参考表
- 数值/公式: `DC_map={非常容易:5, 容易:10, 中等:15, 困难:20, 非常困难:25, 近乎不可能:30}`
- 状态读取: task_difficulty_label
- 状态变更: DC
- 出处: topics/玩家手册2024/进行游戏/属性检定.htm
- 待实现函数: dc_by_label(label)->int
- 优先级: P1

### R-CHK-010 属性检定
- 摘要: 非攻击的克服挑战行为，失败会产生有意义结果时进行属性检定
- 数值/公式: `total=d20+ability_mod+(prof_bonus if proficient else 0); 成功 if total>=DC`
- 状态读取: ability_mod, prof_bonus, proficient(skill/tool), DC, advantage
- 状态变更: outcome=success/failure, total
- 出处: topics/玩家手册2024/进行游戏/属性检定.htm
- 待实现函数: ability_check(mod, prof, proficient, dc, advantage)->(success,total)
- 优先级: P1

### R-CHK-011 豁免检定
- 摘要: 抵抗危险时进行豁免检定；可主动放弃掷骰直接判失败
- 数值/公式: `if waive: outcome=failure; else: total=d20+ability_mod+(prof_bonus if proficient else 0); 成功 if total>=DC`
- 状态读取: ability_mod, prof_bonus, proficient(save), save_DC, advantage, waive
- 状态变更: outcome=success/failure, total
- 出处: topics/玩家手册2024/进行游戏/豁免检定.htm
- 待实现函数: saving_throw(mod, prof, proficient, dc, advantage, waive=False)->(success,total)
- 优先级: P1

### R-CHK-012 法术豁免DC构成
- 摘要: 法术迫使豁免时，其DC由施法者的施法属性调整值与熟练加值决定；基准8（见R-DM-002/R-SPL-021）
- 数值/公式: `save_DC = 8 + caster_casting_ability_mod + caster_prof_bonus`
- 状态读取: caster_casting_ability_mod, caster_prof_bonus
- 状态变更: save_DC
- 出处: topics/玩家手册2024/进行游戏/豁免检定.htm
- 待实现函数: compute_spell_save_dc(prof, casting_mod)->int
- 优先级: P1

### R-CHK-013 豁免多目标伤害一次掷骰
- 摘要: 一个伤害效应迫使两个或以上目标同时豁免时，只掷一次伤害决定所有目标所受伤害
- 数值/公式: `if target_count>=2: damage_per_target = roll(dice_expr) once`
- 状态读取: target_count, dice_expr
- 状态变更: damage_per_target
- 出处: topics/玩家手册2024/进行游戏/豁免检定与伤害.htm
- 待实现函数: roll_area_damage(dice_expr, targets)->damage_per_target
- 优先级: P1

### R-CHK-014 豁免成功半伤
- 摘要: 豁免效应在目标豁免成功时只造成半伤，向下取整
- 数值/公式: `if save_success: damage = floor(full_damage / 2); else: damage = full_damage`
- 状态读取: full_damage, save_outcome
- 状态变更: damage
- 出处: topics/玩家手册2024/进行游戏/豁免检定与伤害.htm
- 待实现函数: apply_save_half_damage(full_damage, save_success)->damage
- 优先级: P1

### R-CHK-015 熟练加值表
- 摘要: 熟练加值随等级/CR提升，从+2到+9
- 数值/公式: `prof_bonus_map = {1-4:+2, 5-8:+3, 9-12:+4, 13-16:+5, 17-20:+6, 21-24:+7, 25-28:+8, 29-30:+9}`
- 状态读取: level_or_CR
- 状态变更: prof_bonus
- 出处: topics/玩家手册2024/进行游戏/熟练.htm
- 待实现函数: proficiency_bonus(level_or_cr)->int
- 优先级: P0

### R-CHK-016 熟练加值不叠加
- 摘要: 熟练加值不能多次添加到同一掷骰或结果中
- 数值/公式: `prof_bonus_applied_count = 1 (max); 多项熟练仅取一次`
- 状态读取: applicable_proficiencies[]
- 状态变更: prof_bonus_applied
- 出处: topics/玩家手册2024/进行游戏/熟练.htm
- 待实现函数: apply_prof_once(prof_bonus, applicable_list)->int
- 优先级: P1

### R-CHK-017 专精熟练加值翻倍
- 摘要: 专精特性令特定属性检定的熟练加值翻倍；乘算与除算各只执行一次
- 数值/公式: `if expertise: effective_prof_bonus = prof_bonus * 2`
- 状态读取: expertise_flag, prof_bonus
- 状态变更: effective_prof_bonus
- 出处: topics/玩家手册2024/进行游戏/熟练.htm
- 待实现函数: apply_expertise(prof_bonus, expertise)->int
- 优先级: P2

### R-CHK-018 技能熟练应用
- 摘要: 熟练某技能时涉及该技能的属性检定加熟练加值；不熟练仍可检定但不加
- 数值/公式: `prof_bonus_added = prof_bonus if proficient(skill) else 0`
- 状态读取: skill_proficiencies[], skill
- 状态变更: proficient
- 出处: topics/玩家手册2024/进行游戏/熟练.htm
- 待实现函数: resolve_skill_proficiency(skill, proficiencies)->bool
- 优先级: P1

### R-CHK-019 豁免熟练应用
- 摘要: 拥有某豁免熟练则该类豁免加熟练加值；每个职业至少给予两个豁免熟练
- 数值/公式: `prof_bonus_added = prof_bonus if proficient(save) else 0; min_saves_per_class = 2`
- 状态读取: save_proficiencies[], save
- 状态变更: proficient
- 出处: topics/玩家手册2024/进行游戏/熟练.htm
- 待实现函数: resolve_save_proficiency(save, proficiencies)->bool
- 优先级: P1

### R-CHK-020 武器与工具熟练应用
- 摘要: 武器熟练则该武器攻击检定加熟练加值；工具熟练则该工具属性检定加熟练加值
- 数值/公式: `attack_prof_bonus += prof_bonus if weapon_proficient; ability_prof_bonus += prof_bonus if tool_proficient`
- 状态读取: weapon_proficiencies[], tool_proficiencies[], item
- 状态变更: proficient
- 出处: topics/玩家手册2024/进行游戏/熟练.htm
- 待实现函数: resolve_equipment_proficiency(item, weapon_profs, tool_profs)->bool
- 优先级: P1

### R-CHK-021 工具与技能双熟练得优势
- 摘要: 进行属性检定时若同时熟练该检定使用的技能和工具，则该检定具有优势
- 数值/公式: `if proficient(skill) and proficient(tool): advantage = True`
- 状态读取: skill_proficient, tool_proficient
- 状态变更: advantage
- 出处: topics/玩家手册2024/进行游戏/熟练.htm
- 待实现函数: check_dual_proficiency_advantage(skill_prof, tool_prof)->advantage
- 优先级: P2

### R-CHK-022 技能默认属性对应表
- 摘要: 各技能最常联用的属性映射
- 数值/公式: `skill_ability={特技:敏捷, 驯兽:感知, 奥秘:智力, 运动:力量, 欺瞒:魅力, 历史:智力, 洞悉:感知, 威吓:魅力, 调查:智力, 医药:感知, 自然:智力, 察觉:感知, 表演:魅力, 游说:魅力, 宗教:智力, 巧手:敏捷, 隐匿:敏捷, 求生:感知}`
- 状态读取: skill_name
- 状态变更: ability_used
- 出处: topics/玩家手册2024/进行游戏/熟练.htm
- 待实现函数: skill_ability_map(skill)->ability
- 优先级: P1

### R-CHK-023 属性值范围与上限
- 摘要: 属性值1-20，怪物最高30；20为冒险者上限
- 数值/公式: `min_score=1; max_player=20; max_monster=30`
- 状态读取: is_monster, score
- 状态变更: score(clamped)
- 出处: topics/玩家手册2024/进行游戏/六项属性.htm
- 待实现函数: clamp_ability_score(score, is_monster)->int
- 优先级: P2

### R-CHK-024 属性调整值表与公式
- 摘要: 属性调整值公式 floor((score-10)/2)
- 数值/公式: `mod = floor((score - 10) / 2); 表: 1→-5, 2-3→-4, 4-5→-3, 6-7→-2, 8-9→-1, 10-11→0, 12-13→+1, 14-15→+2, 16-17→+3, 18-19→+4, 20-21→+5, 22-23→+6, 24-25→+7, 26-27→+8, 28-29→+9, 30→+10`
- 状态读取: ability_score
- 状态变更: ability_mod
- 出处: topics/玩家手册2024/进行游戏/六项属性.htm
- 待实现函数: ability_modifier(score)->int
- 优先级: P0

### R-CHK-025 骰子标识与表达式
- 摘要: 骰标识NdM，掷N颗M面骰相加再加常数；M∈{4,6,8,10,12,20}
- 数值/公式: `expr = NdM + K; result = sum(roll(M) for _ in range(N)) + K; 例 3d8+5`
- 状态读取: dice_expr
- 状态变更: roll_result
- 出处: topics/玩家手册2024/进行游戏/骰子.htm
- 待实现函数: parse_and_roll_dice(expr)->int
- 优先级: P0

### R-CHK-026 百分骰d100
- 摘要: d100由两颗十面骰(十位+个位)组成，两骰皆0则结果为100
- 数值/公式: `d100 = tens*10 + ones; if tens==0 and ones==0: result=100`
- 状态读取: tens_die, ones_die
- 状态变更: d100_result
- 出处: topics/玩家手册2024/进行游戏/骰子.htm
- 待实现函数: roll_d100()->int
- 优先级: P1

### R-CHK-027 D3骰换算
- 摘要: 1d3由掷1d6除以2向上取整得到
- 数值/公式: `d3 = ceil(d6 / 2)`
- 状态读取: d6_roll
- 状态变更: d3_result
- 出处: topics/玩家手册2024/进行游戏/骰子.htm
- 待实现函数: roll_d3()->int
- 优先级: P2

### R-CHK-028 武器与法术伤害骰示例
- 摘要: 武器/法术伤害骰表达式示例
- 数值/公式: `匕首=1d4; 巨斧=1d12; 火球术=8d6`
- 状态读取: weapon_or_spell_name
- 状态变更: damage_dice
- 出处: topics/玩家手册2024/进行游戏/骰子.htm
- 待实现函数: get_damage_dice(item_name)->expr
- 优先级: P2

### R-CHK-029 百分比概率判定
- 摘要: 规则给出百分比概率时掷d100，结果<=概率百分比则事件发生
- 数值/公式: `event_occurs = (roll_d100() <= percent_chance); 例 5% → 01-05发生`
- 状态读取: percent_chance
- 状态变更: event_occurred
- 出处: topics/玩家手册2024/进行游戏/骰子.htm
- 待实现函数: roll_percent_chance(percent)->bool
- 优先级: P1

### R-CHK-030 随机表掷骰查表
- 摘要: 随机表最左列标骰标识，掷该骰后按结果数值或范围匹配行读取结果
- 数值/公式: `result = table.lookup(roll(die_notation))`
- 状态读取: table, die_notation
- 状态变更: table_result
- 出处: topics/玩家手册2024/进行游戏/骰子.htm
- 待实现函数: roll_random_table(table, die_notation)->entry
- 优先级: P2

---

## 2. 战斗与动作（R-CMB，46 条）

### R-CMB-001 战斗轮时长
- 摘要: 一轮战斗在游戏世界代表约6秒，每轮每个参战者执行一个回合
- 数值/公式: `round_seconds = 6; turns_per_round = 1 per combatant`
- 状态读取: combatant_count
- 状态变更: round_counter += 1 (所有回合完成时)
- 出处: topics/玩家手册2024/进行游戏/战斗流程.htm
- 待实现函数: advance_round()->(new_round, initiative_unchanged)
- 优先级: P1

### R-CMB-002 先攻检定
- 摘要: 战斗开始时每名参战者进行敏捷检定决定回合顺序；突袭者先攻检定具有劣势
- 数值/公式: `initiative = d20 + DEX_mod; if surprised: roll with disadvantage; 排序降序; 相同怪物组可只掷一次全组共用`
- 状态读取: actor.dex_mod, actor.is_surprised, actor.is_identical_group
- 状态变更: actor.initiative, combat.initiative_order = sorted(desc)
- 出处: topics/玩家手册2024/进行游戏/战斗流程.htm
- 待实现函数: roll_initiative(actors, surprise_flags)->initiative_order
- 优先级: P0

### R-CMB-003 先攻平局处理
- 摘要: 先攻数值相同时，怪物间由DM决定，玩家间自行决定，玩家与怪物相同由DM裁定
- 数值/公式: `tie: monster_vs_monster=DM_choice; player_vs_player=player_choice; player_vs_monster=DM_choice`
- 状态读取: actor.type, tied_initiative_values
- 状态变更: combat.initiative_order
- 出处: topics/玩家手册2024/进行游戏/战斗流程.htm
- 待实现函数: resolve_initiative_ties(tied_actors)->ordered
- 优先级: P2

### R-CMB-004 回合动作经济
- 摘要: 你的回合中可移动距离至多等于速度，并执行一个动作；先移动还是先动作由你决定
- 数值/公式: `move_allowed <= speed; actions_allowed = 1; order = free_choice`
- 状态读取: actor.speed, actor.action_available
- 状态变更: actor.remaining_move = speed, actor.action_used = false
- 出处: topics/玩家手册2024/进行游戏/战斗流程.htm
- 待实现函数: start_turn(actor)->(remaining_move, action_available)
- 优先级: P0

### R-CMB-005 免费物件交互
- 摘要: 移动或动作期间可免费与一个物件交互；第二个物件需执行操作动作
- 数值/公式: `free_interactions_per_turn = 1; 2nd_object = requires Utilize action`
- 状态读取: actor.free_interaction_used
- 状态变更: actor.free_interaction_used = true
- 出处: topics/玩家手册2024/进行游戏/战斗流程.htm
- 待实现函数: interact_object(actor, object, is_first)->requires_action
- 优先级: P2

### R-CMB-006 动作:疾走
- 摘要: 疾走动作给予自己等同于自身速度的额外移动力，持续至回合结束
- 数值/公式: `bonus_movement = speed; move_total_this_turn = speed + bonus_movement`
- 状态读取: actor.speed
- 状态变更: actor.remaining_move += speed, actor.action_used = true
- 出处: topics/玩家手册2024/进行游戏/动作.htm
- 待实现函数: action_dash(actor)->remaining_move
- 优先级: P1

### R-CMB-007 动作:撤离
- 摘要: 撤离动作使本回合余下时间的移动不引发借机攻击
- 数值/公式: `provokes_opportunity_attack = false (for this turn's movement)`
- 状态读取: actor.action_used
- 状态变更: actor.disengage_active = true (until turn end), actor.action_used = true
- 出处: topics/玩家手册2024/进行游戏/动作.htm
- 待实现函数: action_disengage(actor)->disengage_active
- 优先级: P1

### R-CMB-008 动作:回避
- 摘要: 直至下个回合开始，对你进行的攻击检定具有劣势，你进行的敏捷豁免检定具有优势；失能或速度0时失去增益
- 数值/公式: `attacks_against_self = disadvantage; own_DEX_saves = advantage; duration = until start of next turn; lose_if incapacitated OR speed==0`
- 状态读取: actor.is_incapacitated, actor.speed
- 状态变更: actor.dodge_active = true, actor.action_used = true
- 出处: topics/玩家手册2024/进行游戏/动作.htm
- 待实现函数: action_dodge(actor)->dodge_active
- 优先级: P1

### R-CMB-009 动作:躲藏
- 摘要: 躲藏动作进行一次敏捷（隐匿）检定
- 数值/公式: `check = d20 + DEX_mod + stealth_proficiency(if proficient)`
- 状态读取: actor.dex_mod, actor.stealth_bonus
- 状态变更: actor.hidden = (check vs passive_perception，DC机制见R-GLS-018)
- 出处: topics/玩家手册2024/进行游戏/动作.htm
- 待实现函数: action_hide(actor)->stealth_check_result
- 优先级: P1

### R-CMB-010 动作:技能检定属性映射
- 摘要: 影响=魅力(欺瞒/威吓/表演/游说)或感知(驯兽)；搜索=感知(洞悉/医药/察觉/求生)；研究=智力(奥秘/历史/调查/自然/宗教)
- 数值/公式: `Influence=CHA(欺瞒/威吓/表演/游说) OR WIS(驯兽); Search=WIS(洞悉/医药/察觉/求生); Study=INT(奥秘/历史/调查/自然/宗教)`
- 状态读取: actor.ability_mod[CHA/WIS/INT], actor.skill_bonus[skill]
- 状态变更: check_result = d20 + ability_mod + skill_bonus
- 出处: topics/玩家手册2024/进行游戏/动作.htm
- 待实现函数: action_skill_check(actor, action_type, skill)->check_result
- 优先级: P2

### R-CMB-011 一次一个动作限制
- 摘要: 你一次只能执行一个动作（含非战斗场景）
- 数值/公式: `max_concurrent_actions = 1`
- 状态读取: actor.action_used
- 状态变更: actor.action_used = true
- 出处: topics/玩家手册2024/进行游戏/动作.htm
- 待实现函数: can_take_action(actor)->bool
- 优先级: P1

### R-CMB-012 附赠动作经济
- 摘要: 特殊能力/法术允许时可执行一个附赠动作；每回合仅一个；无法执行动作时同样无法执行附赠动作
- 数值/公式: `bonus_actions_per_turn = 1; must_have_enabling_feature = true; blocked_if action_blocked`
- 状态读取: actor.has_enabling_feature, actor.action_blocked
- 状态变更: actor.bonus_action_used = true
- 出处: topics/玩家手册2024/进行游戏/附赠动作.htm
- 待实现函数: can_take_bonus_action(actor)->bool
- 优先级: P1

### R-CMB-013 反应经济
- 摘要: 执行反应后直至下个回合开始不能再次执行反应；反应在触发条件满足后立刻发生
- 数值/公式: `reactions_per_round = 1; refresh_at = start of next own turn`
- 状态读取: actor.reaction_used
- 状态变更: actor.reaction_used = true (reset at next turn start)
- 出处: topics/玩家手册2024/进行游戏/反应.htm
- 待实现函数: can_take_reaction(actor)->bool, use_reaction(actor)
- 优先级: P1

### R-CMB-014 攻击流程
- 摘要: 发动攻击三步：选择目标、确定调整（掩护/优劣势/加值减值）、结算攻击（检定命中后掷伤害）
- 数值/公式: `step1=choose_target; step2=determine_modifiers(cover,advantage,bonuses); step3=resolve(attack_roll -> if hit then damage_roll)`
- 状态读取: target.ac, target.cover, attacker.advantage, attacker.bonuses
- 状态变更: target.hp (if hit), hit/crit flags
- 出处: topics/玩家手册2024/进行游戏/发动攻击.htm
- 待实现函数: make_attack(attacker, target, weapon, modifiers)->(hit, crit, damage)
- 优先级: P0

### R-CMB-015 掩护加值
- 摘要: 掩护分三档：半身+2、四分之三+5、全身不可被直接选作目标；多重掩护只取最高且不累加
- 数值/公式: `half_cover: AC+2 AND DEX_save+2; three_quarters_cover: AC+5 AND DEX_save+5; full_cover: cannot_be_targeted; multi_cover = max(cover_values)`
- 状态读取: target.cover_degree, attacker.position_relative_to_cover
- 状态变更: target.effective_ac += cover_bonus, target.dex_save_bonus += cover_bonus
- 出处: topics/玩家手册2024/进行游戏/发动攻击.htm
- 待实现函数: apply_cover(target, attacker, covers)->(ac_bonus, dex_save_bonus, targetable)
- 优先级: P0

### R-CMB-016 不可见攻击者与目标
- 摘要: 攻击不可见目标具有劣势；对看不见你的生物进行的攻击具有优势；攻击检定时处于躲藏中无论命中与否位置暴露
- 数值/公式: `if target_invisible: attack_roll disadvantage; if target_not_at_designated_square: auto_miss; if attacker_unseen_by_target: attack_roll advantage; if attacker_hidden: hidden=false after roll`
- 状态读取: target.is_invisible, target.position, attacker.is_hidden, attacker.unseen_by_target
- 状态变更: attacker.is_hidden = false (after attack roll)
- 出处: topics/玩家手册2024/进行游戏/发动攻击.htm
- 待实现函数: resolve_visibility_modifiers(attacker, target)->(advantage, auto_miss)
- 优先级: P0

### R-CMB-017 攻击检定命中判定
- 摘要: 攻击检定高于等于目标护甲等级则命中
- 数值/公式: `attack_total = d20 + ability_mod + proficiency_bonus(if proficient) + magic_bonus; hit = (attack_total >= target_ac)`
- 状态读取: attacker.ability_mod, attacker.proficiency_bonus, attacker.magic_bonus, target.ac
- 状态变更: hit = bool
- 出处: topics/玩家手册2024/进行游戏/攻击检定.htm
- 待实现函数: attack_roll(bonus, advantage, ac)->(hit, total, rolls)
- 优先级: P0

### R-CMB-018 攻击检定属性映射
- 摘要: 力量用于近战/徒手打击，敏捷用于远程攻击，法术攻击属性由施法者施法特性决定
- 数值/公式: `melee/unarmed: STR_mod; ranged: DEX_mod; spell: casting_ability_mod`
- 状态读取: attack_type, weapon.finesse_flag, caster.spellcasting_ability
- 状态变更: ability_mod = resolved per type
- 出处: topics/玩家手册2024/进行游戏/攻击检定.htm
- 待实现函数: get_attack_ability(attacker, attack_type, weapon)->ability_mod
- 优先级: P0

### R-CMB-019 灵巧武器属性选择
- 摘要: 具有灵巧词条的武器可使用力量或敏捷调整值（攻击者选择）
- 数值/公式: `finesse_mod = max(STR_mod, DEX_mod) OR chosen_by_attacker`
- 状态读取: weapon.finesse, attacker.str_mod, attacker.dex_mod
- 状态变更: attack_ability_mod = chosen
- 出处: topics/玩家手册2024/进行游戏/攻击检定.htm
- 待实现函数: resolve_finesse_mod(attacker, weapon)->ability_mod
- 优先级: P0

### R-CMB-020 熟练加值应用
- 摘要: 使用熟练的武器或法术进行攻击时，将熟练加值添加到攻击检定
- 数值/公式: `attack_total += proficiency_bonus (if weapon/spell proficient)`
- 状态读取: attacker.proficiency_bonus, attacker.is_proficient
- 状态变更: attack_total += proficiency_bonus
- 出处: topics/玩家手册2024/进行游戏/攻击检定.htm
- 待实现函数: apply_proficiency(attacker, weapon)->bonus
- 优先级: P0

### R-CMB-021 基础护甲等级计算
- 摘要: 所有生物基础AC = 10 + 敏捷调整值；护甲/魔法物品/法术可改变；多个AC计算方式只能选一种生效
- 数值/公式: `base_AC = 10 + DEX_mod; effective_AC = base_AC + armor_bonus + magic_bonus + spell_bonus; if multiple_AC_formulas: pick_one_only`
- 状态读取: actor.dex_mod, actor.armor, actor.magic_items, actor.active_spells
- 状态变更: actor.ac = computed_value
- 出处: topics/玩家手册2024/进行游戏/攻击检定.htm
- 待实现函数: compute_ac(actor)->ac_value
- 优先级: P0

### R-CMB-022 天然20必命中与重击
- 摘要: 攻击检定d20掷出20无论调整值与目标AC如何必命中，且为重击
- 数值/公式: `if d20==20: hit=true (ignore mods/AC); crit=true`
- 状态读取: d20_roll
- 状态变更: hit=true, crit=true
- 出处: topics/玩家手册2024/进行游戏/攻击检定.htm
- 待实现函数: check_natural_20(d20_roll)->(auto_hit, crit)
- 优先级: P0

### R-CMB-023 天然1必失手
- 摘要: 攻击检定d20掷出1无论调整值与目标AC如何必失手
- 数值/公式: `if d20==1: hit=false (ignore mods/AC)`
- 状态读取: d20_roll
- 状态变更: hit=false
- 出处: topics/玩家手册2024/进行游戏/攻击检定.htm
- 待实现函数: check_natural_1(d20_roll)->auto_miss
- 优先级: P0

### R-CMB-024 近战触及范围
- 摘要: 生物通常具有5尺触及；特定生物可达超过5尺（见其描述）
- 数值/公式: `default_reach = 5 ft; special_reach = per creature description`
- 状态读取: attacker.reach
- 状态变更: in_range = distance <= reach
- 出处: topics/玩家手册2024/进行游戏/近战攻击.htm
- 待实现函数: is_within_reach(attacker, target)->bool
- 优先级: P0

### R-CMB-025 借机攻击触发
- 摘要: 当一个你可见的生物离开你的触及范围时，你可以用反应对其发动一次近战攻击/徒手打击
- 数值/公式: `trigger = visible_creature_exits_reach; cost = 1 reaction; attack_type = melee weapon OR unarmed strike`
- 状态读取: attacker.reaction_used, attacker.reach, target.is_visible, target.leaving_reach
- 状态变更: attacker.reaction_used = true, target.hp (if hit)
- 出处: topics/玩家手册2024/进行游戏/近战攻击.htm
- 待实现函数: opportunity_attack(attacker, target)->(triggered, attack_result)
- 优先级: P0

### R-CMB-026 避免借机攻击
- 摘要: 撤离动作、传送、或不消耗移动力/动作/附赠动作/反应的移动不引发借机攻击
- 数值/公式: `no_opportunity_attack_if: disengage_active OR teleporting OR movement_cost_free`
- 状态读取: actor.disengage_active, movement.is_teleport, movement.cost_type
- 状态变更: provokes_opportunity = false
- 出处: topics/玩家手册2024/进行游戏/近战攻击.htm
- 待实现函数: check_opportunity_trigger(actor, movement)->provokes
- 优先级: P1

### R-CMB-027 远程攻击射程
- 摘要: 单一射程武器不能攻击超出射程目标；双射程武器常规射程外攻击检定劣势，最大射程外不能攻击
- 数值/公式: `single_range: distance>range → cannot_attack; dual_range: distance>normal AND <=max → disadvantage; distance>max → cannot_attack`
- 状态读取: weapon.range(normal/max), target.distance
- 状态变更: attack_advantage = disadvantage(if beyond normal within max)
- 出处: topics/玩家手册2024/进行游戏/远程攻击.htm
- 待实现函数: check_ranged_range(weapon, distance)->(can_attack, advantage)
- 优先级: P0

### R-CMB-028 近战接战时远程攻击劣势
- 摘要: 远程攻击检定时，若5尺内有**能看到你**且未失能的敌人，则该检定具有劣势（审计修正:原"可见的敌人"方向写反，应为"敌人能看到你"——隐匿/目盲场景关键）
- 数值/公式: `if any_enemy within 5ft AND enemy.can_see(attacker) AND not enemy.is_incapacitated: ranged_attack_roll = disadvantage`
- 状态读取: enemies_within_5ft, enemy.can_see_attacker, enemy.is_incapacitated
- 状态变更: attack_advantage = disadvantage
- 出处: topics/玩家手册2024/进行游戏/远程攻击.htm
- 待实现函数: check_close_combat_ranged_disadvantage(attacker, enemies)->advantage
- 优先级: P0

### R-CMB-029 重击伤害骰翻倍
- 摘要: 重击时投掷两次该攻击的伤害骰并累加，再如常加上调整值；附加伤害骰（如偷袭）也掷两次
- 数值/公式: `crit_damage = (2 * weapon_damage_dice) + ability_mod + flat_bonuses; bonus_dice_features also rolled twice; 例: 匕首 crit = 2d4 + STR/DEX_mod`
- 状态读取: weapon.damage_dice, attack.ability_mod, attack.flat_bonuses, attack.bonus_dice_sources
- 状态变更: damage_total = crit_formula
- 出处: topics/玩家手册2024/进行游戏/重击.htm
- 待实现函数: crit_damage_roll(weapon, ability_mod, bonus_dice_sources)->damage_total
- 优先级: P0

### R-CMB-030 回合移动上限
- 摘要: 你的回合内可移动至多等于你速度的距离，可将移动拆分到动作前后
- 数值/公式: `max_move = speed; remaining_move decreases as moves; can_interleave with actions`
- 状态读取: actor.speed
- 状态变更: actor.remaining_move = speed (turn start), decremented per move
- 出处: topics/玩家手册2024/进行游戏/移动和位置.htm
- 待实现函数: move(actor, distance)->remaining_move
- 优先级: P0

### R-CMB-031 困难地形移动力消耗
- 摘要: 困难地形上每移动1尺需额外消耗1尺移动力，多因素叠加仍如此
- 数值/公式: `cost_per_ft_difficult = 2 ft (1 normal + 1 extra); multi_factor = still 2`
- 状态读取: terrain.is_difficult
- 状态变更: remaining_move -= 2 per ft
- 出处: topics/玩家手册2024/进行游戏/移动和位置.htm
- 待实现函数: move_cost(distance, terrain)->cost_ft
- 优先级: P0

### R-CMB-032 方格地图尺度与速度转格
- 摘要: 每格代表5尺；速度除以5转为格数
- 数值/公式: `ft_per_square = 5; squares = speed_ft / 5; 例: 30ft = 6 squares`
- 状态读取: actor.speed (ft)
- 状态变更: actor.speed_squares = speed_ft/5
- 出处: topics/玩家手册2024/进行游戏/移动和位置.htm
- 待实现函数: speed_to_squares(speed_ft)->squares
- 优先级: P0

### R-CMB-033 方格进入移动力
- 摘要: 进入未占据邻接格需1格移动力；困难地形格子需2格
- 数值/公式: `enter_normal_square = 1 square; enter_difficult_square = 2 squares`
- 状态读取: target_square.is_difficult, target_square.is_occupied
- 状态变更: remaining_move_squares -= cost
- 出处: topics/玩家手册2024/进行游戏/移动和位置.htm
- 待实现函数: enter_square(actor, square)->cost_squares
- 优先级: P0

### R-CMB-034 方格斜线移动与转角限制
- 摘要: 斜线移动不能穿过墙角、大型树木或其他填满整格空间的格子
- 数值/公式: `diagonal_blocked_if target_square_fully_filled`
- 状态读取: square.is_filled
- 状态变更: movement_blocked = bool
- 出处: topics/玩家手册2024/进行游戏/移动和位置.htm
- 待实现函数: can_move_diagonal(from_sq, to_sq)->bool
- 优先级: P1

### R-CMB-035 方格距离计算
- 摘要: 方格地图上两物距离从一方邻接格数到另一方，取最短距离
- 数值/公式: `grid_distance = min_adjacent_square_count`
- 状态读取: positions
- 状态变更: distance_value
- 出处: topics/玩家手册2024/进行游戏/移动和位置.htm
- 待实现函数: grid_distance(pos_a, pos_b)->squares
- 优先级: P1

### R-CMB-036 俯卧倒地
- 摘要: 回合内可令自身进入倒地状态，无需动作或速度，但速度为0时不能
- 数值/公式: `cost = 0; precondition: speed > 0`
- 状态读取: actor.speed
- 状态变更: actor.prone = true
- 出处: topics/玩家手册2024/进行游戏/移动和位置.htm
- 待实现函数: drop_prone(actor)->success
- 优先级: P1

### R-CMB-037 生物体型与占据空间
- 摘要: 体型决定占据格数：微型2.5尺/1/4格，小型与中型5尺/1格，大型10尺/4格，巨型15尺/9格，超巨型20尺/16格
- 数值/公式: `Tiny:2.5x2.5ft,1/4sq; Small:5x5ft,1sq; Medium:5x5ft,1sq; Large:10x10ft,4sq(2x2); Huge:15x15ft,9sq(3x3); Gargantuan:20x20ft,16sq(4x4)`
- 状态读取: creature.size
- 状态变更: creature.footprint = mapped_value
- 出处: topics/玩家手册2024/进行游戏/移动和位置.htm
- 待实现函数: get_size_footprint(size)->(ft, squares, grid_dims)
- 优先级: P1

### R-CMB-038 穿过其他生物空间
- 摘要: 可穿过盟友、失能生物、微型生物、或体型相差两级以上的生物空间；除微型和盟友外其他生物空间对你为困难地形
- 数值/公式: `can_pass_if: ally OR incapacitated OR tiny OR size_diff>=2; other_creature_space = difficult_terrain (unless tiny/ally)`
- 状态读取: creature.relation, creature.is_incapacitated, creature.size, size_diff
- 状态变更: movement_cost_multiplier
- 出处: topics/玩家手册2024/进行游戏/移动和位置.htm
- 待实现函数: can_pass_through(mover, creature)->bool, pass_cost(mover, creature)->multiplier
- 优先级: P1

### R-CMB-039 生物空间结束移动
- 摘要: 不能在其他生物占据空间结束移动；若因故在其空间结束回合则陷入倒地（除非微型或比对方体型更大）
- 数值/公式: `end_move_in_other_space = forbidden; if forced: actor.prone=true; exempt_if: size==Tiny OR size > creature.size`
- 状态读取: mover.size, occupant.size
- 状态变更: actor.prone = true (if not exempt)
- 出处: topics/玩家手册2024/进行游戏/移动和位置.htm
- 待实现函数: check_end_in_creature_space(mover, occupant)->prone
- 优先级: P1

### R-CMB-040 水下近战攻击劣势
- 摘要: 水下用武器近战攻击检定，除非造成穿刺伤害，否则无游泳速度的生物具有劣势
- 数值/公式: `if underwater AND weapon_damage != piercing AND attacker.swim_speed == 0: melee_attack_roll = disadvantage`
- 状态读取: environment=underwater, weapon.damage_type, attacker.swim_speed
- 状态变更: attack_advantage = disadvantage
- 出处: topics/玩家手册2024/进行游戏/水下战斗.htm
- 待实现函数: underwater_melee_disadvantage(attacker, weapon)->advantage
- 优先级: P1

### R-CMB-041 水下远程攻击
- 摘要: 水下远程攻击超过常规射程自动失手；常规射程内攻击检定具有劣势
- 数值/公式: `if underwater ranged: distance>normal_range → auto_miss; distance<=normal_range → disadvantage`
- 状态读取: environment=underwater, weapon.range, target.distance
- 状态变更: attack_roll disadvantage OR auto_miss
- 出处: topics/玩家手册2024/进行游戏/水下战斗.htm
- 待实现函数: underwater_ranged(weapon, distance)->(can_hit, advantage)
- 优先级: P1

### R-CMB-042 水下火焰抗性
- 摘要: 水下所有存在均对火焰伤害具有抗性（伤害减半）
- 数值/公式: `if underwater AND damage_type == fire: damage = floor(damage / 2)`
- 状态读取: environment=underwater, damage.type
- 状态变更: damage_total = floor(original/2)
- 出处: topics/玩家手册2024/进行游戏/水下战斗.htm
- 待实现函数: apply_underwater_fire_resistance(damage)->adjusted
- 优先级: P1

### R-CMB-043 坐骑条件
- 摘要: 体型比骑手至少大一级、具有适合被骑的生理结构且自愿的生物可作坐骑
- 数值/公式: `mount_valid_if: mount.size >= rider.size + 1 AND suitable_anatomy AND willing`
- 状态读取: mount.size, rider.size, mount.anatomy, mount.willing
- 状态变更: mount.is_mountable = bool
- 出处: topics/玩家手册2024/进行游戏/骑乘战斗.htm
- 待实现函数: can_mount(rider, mount)->bool
- 优先级: P2

### R-CMB-044 上下坐骑移动力消耗
- 摘要: 移动期间可骑乘5尺内生物或下坐骑，消耗等于速度一半的移动力（向下取整）
- 数值/公式: `cost = floor(speed / 2); 例: speed=30 -> cost=15ft`
- 状态读取: actor.speed, mount.distance
- 状态变更: actor.remaining_move -= floor(speed/2), actor.mounted = true/false
- 出处: topics/玩家手册2024/进行游戏/骑乘战斗.htm
- 待实现函数: mount_dismount(actor, mount)->cost_ft
- 优先级: P1

### R-CMB-045 受控坐骑先攻与动作
- 摘要: 受控坐骑先攻与骑手相同，在骑手回合行动，仅可执行疾走/撤离/回避三个动作
- 数值/公式: `controlled_mount.initiative = rider.initiative; action_options = [Dash, Disengage, Dodge] only`
- 状态读取: rider.initiative, mount.is_controlled
- 状态变更: mount.initiative = rider.initiative, mount.allowed_actions = subset
- 出处: topics/玩家手册2024/进行游戏/骑乘战斗.htm
- 待实现函数: init_controlled_mount(rider, mount)
- 优先级: P1

### R-CMB-046 跌落坐骑豁免
- 摘要: 骑乘期间若效应违背坐骑意愿使其移动，或骑手/坐骑被击至倒地，骑手须DC10敏捷豁免，失败则跌落于坐骑5尺内未占据空间并倒地
- 数值/公式: `trigger = mount_moved_unwillingly OR rider_prone OR mount_prone; save = d20 + DEX_mod vs DC10; fail: dismount, land within 5ft, rider.prone=true`
- 状态读取: rider.dex_mod, mount.moved_unwillingly, rider.prone, mount.prone
- 状态变更: rider.mounted = false, rider.prone = true (on fail), rider.position
- 出处: topics/玩家手册2024/进行游戏/骑乘战斗.htm
- 待实现函数: falling_off_mount_save(rider, mount, trigger)->(save_result, prone, position)
- 优先级: P1

## 3. 伤害生命治疗（R-DMG，24 条）

### R-DMG-001 伤害掷骰构成
- 摘要: 武器攻击伤害骰加上攻击检定所用同一属性的调整值；法术伤害按法术说明掷骰；定值伤害默认不加属性调整值
- 数值/公式: 武器`damage=sum(weapon_damage_dice)+ability_mod`; 法术`damage=roll(spell_dice)+(spell_mod if spell_says_so else 0)`; 定值`damage=fixed_value`
- 状态读取: weapon_damage_dice, attack_ability, ability_mod, spell_damage_dice, spell_adds_mod, is_fixed_damage
- 状态变更: pending_damage
- 出处: topics/玩家手册2024/进行游戏/伤害掷骰.htm
- 待实现函数: compute_damage_roll(dice_expr, ability_mod=None, add_mod=False)->int
- 优先级: P0

### R-DMG-002 伤害下限为0
- 摘要: 伤害若因减值而可为负，则记为0
- 数值/公式: `final_damage = max(0, computed_damage)`
- 状态读取: computed_damage
- 状态变更: final_damage
- 出处: topics/玩家手册2024/进行游戏/伤害掷骰.htm
- 待实现函数: apply_damage_floor(damage)->int
- 优先级: P0

### R-DMG-003 抗性与易伤倍数
- 摘要: 抗性则该类型伤害减半（向下取整）；易伤则翻倍
- 数值/公式: 抗性`damage=floor(damage/2)`; 易伤`damage=damage*2`
- 状态读取: target.resistances, target.vulnerabilities, damage_type
- 状态变更: damage
- 出处: topics/玩家手册2024/进行游戏/抗性和易伤.htm
- 待实现函数: apply_resistance_vulnerability(damage, damage_type, resistances, vulnerabilities)->int
- 优先级: P0

### R-DMG-004 抗性易伤不叠加
- 摘要: 同伤害类型的多个抗性只计算一次（易伤同理）
- 数值/公式: `multiplier_resist=0.5(取一次); multiplier_vuln=2(取一次)`
- 状态读取: target.resistances, target.vulnerabilities, damage_type
- 状态变更: 无（判定逻辑）
- 出处: topics/玩家手册2024/进行游戏/抗性和易伤.htm
- 待实现函数: has_resistance(damage_type, resistances)->bool
- 优先级: P0

### R-DMG-005 伤害调整生效顺序
- 摘要: 伤害结算顺序：先数值修正（加值/减值/乘数）→ 再抗性 → 再易伤
- 数值/公式: `step1=apply_numerical_modifiers(damage); step2=floor(step1/2) if resist; final=step2*2 if vuln`; 官方算例: 28火焰,-5灵光,全抗,火易伤→(28-5)=23→floor(23/2)=11→11×2=22
- 状态读取: numerical_modifiers, resistances, vulnerabilities, damage_type
- 状态变更: final_damage
- 出处: topics/玩家手册2024/进行游戏/抗性和易伤.htm
- 待实现函数: resolve_damage_pipeline(damage, damage_type, mods, resistances, vulnerabilities)->int
- 优先级: P0

### R-DMG-006 免疫
- 摘要: 免疫特定伤害类型则不受该类型伤害（伤害为0）；免疫某状态则不受该状态
- 数值/公式: `if damage_type in immunities: damage=0`; 状态免疫则不施加
- 状态读取: target.damage_immunities, target.condition_immunities, damage_type/condition
- 状态变更: damage=0 或 condition 不施加
- 出处: topics/玩家手册2024/进行游戏/免疫.htm
- 待实现函数: apply_immunity(damage, damage_type, immunities)->int; is_condition_immune(condition, immunities)->bool
- 优先级: P0

### R-DMG-007 生命值范围与伤害扣除
- 摘要: 当前HP在0到上限之间；受伤害时扣除；未降至0则不影响行动能力
- 数值/公式: `0<=current_hp<=hp_max; current_hp=current_hp-damage（不低于0，过量伤害判定先保留余量）`
- 状态读取: current_hp, hp_max, incoming_damage
- 状态变更: current_hp
- 出处: topics/玩家手册2024/进行游戏/生命值.htm
- 待实现函数: subtract_hp(current_hp, damage)->int
- 优先级: P0

### R-DMG-008 浴血状态
- 摘要: 当前HP≤上限一半时处于浴血状态；本身无游戏效果但可触发其他效应
- 数值/公式: `is_bloodied = current_hp <= floor(hp_max / 2)`
- 状态读取: current_hp, hp_max
- 状态变更: status.bloodied
- 出处: topics/玩家手册2024/进行游戏/生命值.htm
- 待实现函数: check_bloodied(current_hp, hp_max)->bool
- 优先级: P1

### R-DMG-009 临时生命值优先扣除
- 摘要: 有临时HP时受伤害，先扣临时HP，余下才扣真正HP
- 数值/公式: `if temp_hp>0: absorbed=min(temp_hp,damage); temp_hp-=absorbed; damage-=absorbed; current_hp-=damage`; 算例: 5临时HP受7→失5临时再失2HP
- 状态读取: temp_hp, current_hp, incoming_damage
- 状态变更: temp_hp, current_hp
- 出处: topics/玩家手册2024/进行游戏/临时生命值.htm
- 待实现函数: apply_damage_with_temp_hp(temp_hp, current_hp, damage)->(temp_hp, current_hp)
- 优先级: P0

### R-DMG-010 临时生命值不叠加
- 摘要: 临时HP无法叠加；获得新的时取较大者
- 数值/公式: `temp_hp = max(old_temp_hp, new_temp_hp)`
- 状态读取: temp_hp(旧), new_temp_hp
- 状态变更: temp_hp
- 出处: topics/玩家手册2024/进行游戏/临时生命值.htm
- 待实现函数: grant_temp_hp(current_temp, new_temp)->int
- 优先级: P1

### R-DMG-011 临时生命值持续与限制
- 摘要: 临时HP持续至被消耗或长休完成；不能被治疗恢复；满HP仍可获；HP0时获临时HP不能恢复意识
- 数值/公式: `on_consumed 或 on_long_rest → temp_hp=0; 治疗不影响temp_hp; hp==0时获temp不恢复意识`
- 状态读取: temp_hp, current_hp, hp_max, rest_state
- 状态变更: temp_hp(长休后清0)
- 出处: topics/玩家手册2024/进行游戏/临时生命值.htm
- 待实现函数: clear_temp_hp_on_long_rest(temp_hp)->0
- 优先级: P2

### R-DMG-012 即刻毙命-怪物0血死亡
- 摘要: 怪物HP降至0时可立即死亡；DM可无视此规则
- 数值/公式: `if is_monster and current_hp<=0 and dm_use_monster_rule: die()`
- 状态读取: is_monster, current_hp, dm_use_monster_instant_death
- 状态变更: is_dead
- 出处: topics/玩家手册2024/进行游戏/生命值降至0点.htm
- 待实现函数: monster_death_check(creature)->bool
- 优先级: P1

### R-DMG-013 即刻毙命-生命值上限归0
- 摘要: 若生物HP上限降至0，则该生物死亡
- 数值/公式: `if hp_max <= 0: die()`
- 状态读取: hp_max
- 状态变更: is_dead
- 出处: topics/玩家手册2024/进行游戏/生命值降至0点.htm
- 待实现函数: check_hp_max_zero_death(hp_max)->bool
- 优先级: P1

### R-DMG-014 即刻毙命-过量伤害
- 摘要: 一次伤害将HP降至0且仍有剩余，若余量≥HP上限则立即死亡
- 数值/公式: `if damage>=current_hp: overflow=damage-current_hp; if overflow>=hp_max: die()`; 算例: max12,cur6,dmg18→余12≥12死亡
- 状态读取: current_hp, hp_max, damage
- 状态变更: is_dead
- 出处: topics/玩家手册2024/进行游戏/生命值降至0点.htm
- 待实现函数: check_massive_damage(current_hp, hp_max, damage)->bool
- 优先级: P1

### R-DMG-015 生命值0陷入昏迷
- 摘要: HP变为0且未立即死亡，则陷入昏迷，直至恢复任意HP
- 数值/公式: `if current_hp==0 and not instant_death: add_condition('unconscious')`
- 状态读取: current_hp, is_dead
- 状态变更: conditions.unconscious=True
- 出处: topics/玩家手册2024/进行游戏/生命值降至0点.htm
- 待实现函数: apply_unconscious_on_zero_hp(creature)
- 优先级: P1

### R-DMG-016 击晕生物
- 摘要: 用近战攻击将生物HP降至0时可改为降至1并昏迷；该生物立即短休，结束脱离昏迷；DC10感知(医药)检定可提前结束
- 数值/公式: `if is_melee and lethal_reduces_to_0: current_hp=1, add(unconscious), start_short_rest; 提前解除: on_regen_hp 或 dc10 wisdom(medicine) success`
- 状态读取: is_melee, current_hp, damage
- 状态变更: current_hp=1, conditions.unconscious, short_rest_active
- 出处: topics/玩家手册2024/进行游戏/生命值降至0点.htm
- 待实现函数: knock_out_creature(creature, attack_type)->bool
- 优先级: P1

### R-DMG-017 死亡豁免检定
- 摘要: 以0HP开始回合时进行死亡豁免（1d20，与属性无关）；≥10记一次成功，否则失败；3次成功则稳定，3次失败则死亡；自然1记两次失败，自然20恢复1点HP
- 数值/公式: `roll=d20(); if roll==1: failures+=2; elif roll==20: hp+=1,reset; elif roll>=10: successes+=1; else: failures+=1; if successes>=3: stabilize,reset; if failures>=3: die,reset`
- 状态读取: current_hp(==0且回合开始), death_successes, death_failures
- 状态变更: death_successes, death_failures, current_hp(自然20+1), is_stable, is_dead
- 出处: topics/玩家手册2024/进行游戏/生命值降至0点.htm
- 待实现函数: death_save_throw(creature)->dict
- 优先级: P0

### R-DMG-018 生命值0时受伤害
- 摘要: HP为0期间受任何伤害记一次死亡豁免失败；重击记两次失败；伤害≥HP上限则死亡
- 数值/公式: `if current_hp==0: if damage>=hp_max: die(); else: if is_crit: failures+=2; else: failures+=1`
- 状态读取: current_hp(==0), damage, hp_max, is_critical_hit
- 状态变更: death_failures, is_dead
- 出处: topics/玩家手册2024/进行游戏/生命值降至0点.htm
- 待实现函数: damage_at_zero_hp(creature, damage, is_crit)->None
- 优先级: P1

### R-DMG-019 稳定角色伤势
- 摘要: 以协助动作进行DC10感知(医药)检定可稳定0血生物；稳定者不再死亡豁免但仍昏迷；受伤害失去稳定；1d4小时后恢复1HP
- 数值/公式: `dc=10; check=d20+wis_mod+medicine_prof; success=is_stable=True,reset counts; 受害:is_stable=False; 1d4小时后:hp=1`
- 状态读取: current_hp(==0), wisdom_mod, medicine_proficiency
- 状态变更: is_stable, death_successes, death_failures, current_hp(1d4h后+1)
- 出处: topics/玩家手册2024/进行游戏/生命值降至0点.htm
- 待实现函数: stabilize_check(creature, helper)->bool; stable_natural_regen(creature)->None
- 优先级: P1

### R-DMG-020 治疗与生命值上限
- 摘要: 治疗将恢复值加到当前HP；不能超过上限，溢出消失
- 数值/公式: `current_hp = min(hp_max, current_hp + heal_amount)`; 算例: cur14,heal8,max20→20实际恢复6
- 状态读取: current_hp, hp_max, heal_amount
- 状态变更: current_hp
- 出处: topics/玩家手册2024/进行游戏/治疗.htm
- 待实现函数: apply_healing(current_hp, hp_max, heal)->int
- 优先级: P0

### R-DMG-021 危害类型
- 摘要: 危害含燃烧/坠落/窒息/脱水/饥饿；具体公式见 R-GLS-059~063（术语汇编危害）
- 数值/公式: 危害集合={燃烧,坠落,窒息,脱水,饥饿}；公式见 R-GLS-059~063
- 状态读取: hazard_type
- 状态变更: 视类型（见R-GLS）
- 出处: topics/玩家手册2024/进行游戏/危害.htm
- 待实现函数: apply_hazard(creature, hazard_type)->None（委托R-GLS板块）
- 优先级: P2

### R-DMG-022 短时物件交互
- 摘要: 战斗时每回合可免费与物件交互一次，须在移动或动作途中；额外交互需操作动作
- 数值/公式: `free_interactions_per_turn=1; 超出需 action(Use)`
- 状态读取: in_combat, turn.free_interactions_used
- 状态变更: turn.free_interactions_used+=1 或消耗动作
- 出处: topics/玩家手册2024/进行游戏/与物件交互.htm
- 待实现函数: try_object_interaction(creature, turn)->bool
- 优先级: P2

### R-DMG-023 寻找隐藏物件
- 摘要: 角色在隐藏物件周边搜索时，DM要求感知(察觉)检定；不在周边搜索则无法发现
- 数值/公式: `check=d20+wis_mod+perception_prof; dc=dm_set; 前置:is_searching_near_object; 成功 check>=dc`
- 状态读取: wisdom_mod, perception_proficiency, search_location
- 状态变更: discovered_objects
- 出处: topics/玩家手册2024/进行游戏/与物件交互.htm
- 待实现函数: find_hidden_object(creature, dc, is_nearby)->bool
- 优先级: P2

### R-DMG-024 破坏物件
- 摘要: 以一个动作可摧毁脆弱非魔法物件；坚韧物件用破坏物件规则（见 R-GLS-022~024）
- 数值/公式: `脆弱非魔法: cost=1 action,自动摧毁; 坚韧:见R-GLS物件AC/HP表`
- 状态读取: object.is_fragile, object.is_magical, object.toughness
- 状态变更: object.destroyed=True
- 出处: topics/玩家手册2024/进行游戏/与物件交互.htm
- 待实现函数: break_object(actor, target_object)->bool（委托R-GLS）
- 优先级: P2

---

## 4. 状态与探索（R-CON，24 条）

> 注：状态条件的具体数值效应见 R-GLS-043~058（术语汇编补全），本板块为状态机制与探索规则。

### R-CON-001 状态不叠加
- 摘要: 同一状态被多个效应施加时效果不增强（仅有/无）；力竭例外可累加等级
- 数值/公式: `has_condition∈{true,false}; 力竭: exhaustion_level+=1`
- 状态读取: target.conditions[cond].sources[]
- 状态变更: 新增来源条目; 力竭则 level+=1
- 出处: topics/玩家手册2024/进行游戏/状态.htm
- 待实现函数: add_condition(target, cond, duration, source); is_stacking_exception(cond)->bool
- 优先级: P1

### R-CON-002 状态持续时间与解除
- 摘要: 状态持续到效应时长结束或被解除（如倒地站起解除）
- 数值/公式: `effect.remaining_duration==0 或触发解除 → 移除; 倒地解除:站起(消耗移动力)`
- 状态读取: target.conditions[cond], effect.remaining_duration
- 状态变更: target.conditions.remove(cond)
- 出处: topics/玩家手册2024/进行游戏/状态.htm
- 待实现函数: expire_conditions(target); remove_condition(target, cond, trigger)
- 优先级: P1

### R-CON-003 状态数值效应（已由 R-GLS-043~058 补全）
- 摘要: 各状态数值效应详见 R-GLS-043~058（倒地/擒抱/束缚/中毒/麻痹/震慑/昏迷/目盲/耳聋/隐形/魅惑/恐慌/石化/失能）
- 数值/公式: 见 R-GLS-043~058
- 状态读取: condition
- 状态变更: 见 R-GLS
- 出处: topics/玩家手册2024/进行游戏/状态.htm（定义见术语汇编）
- 待实现函数: get_condition_effects(cond)->EffectSpec（实现见 R-GLS）
- 优先级: P0

### R-CON-004 遮蔽区域效应
- 摘要: 轻度遮蔽令基于视觉的察觉检定劣势；重度遮蔽令尝试视物者目盲
- 数值/公式: `轻度→perception(视觉)disadvantage; 重度→add_condition(observer,BLINDED)`
- 状态读取: area.obscured_level, check.basis
- 状态变更: 检定加disadvantage; 重度对观察者加BLINDED
- 出处: topics/玩家手册2024/进行游戏/视野与光照.htm
- 待实现函数: apply_obscured_penalty(check, area); is_visually_blinded(observer, area)->bool
- 优先级: P0

### R-CON-005 光照等级映射遮蔽
- 摘要: 明亮正常视物；微光→轻度遮蔽；黑暗→重度遮蔽
- 数值/公式: `bright→none; dim→light; dark→heavy`
- 状态读取: area.light_level
- 状态变更: area.obscured_level=map(light_level)
- 出处: topics/玩家手册2024/进行游戏/视野与光照.htm
- 待实现函数: light_to_obscured(light_level)->obscured_level
- 优先级: P1

### R-CON-006 特殊感官（已由 R-GLS-064~067 补全）
- 摘要: 盲视/黑暗视觉/震颤感知/真实视觉，半径由数据卡给定，详见 R-GLS-064~067
- 数值/公式: 见 R-GLS-064~067
- 状态读取: creature.senses[]
- 状态变更: 可能抵消遮蔽/目盲（见R-GLS）
- 出处: topics/玩家手册2024/进行游戏/视野与光照.htm
- 待实现函数: has_special_sense(creature, sense)->bool（实现见R-GLS）
- 优先级: P2

### R-CON-007 躲藏动作
- 摘要: 尝试躲藏即执行躲藏动作；环境是否适合由DM裁定；检定 DC15 敏捷(隐匿)（DC来源为术语汇编/动作.htm，审计修正:原出处标躲藏.htm但该页源文不含DC15数值）
- 数值/公式: `stealth=d20+DEX_mod+stealth_prof vs DC15; search_dc=hide_check_total`
- 状态读取: creature.dexterity, creature.stealth_prof, 环境遮蔽/光照
- 状态变更: 成功→add_condition(HIDDEN) 或设 hidden_from[]
- 出处: topics/玩家手册2024/进行游戏/躲藏.htm
- 待实现函数: hide_action(actor, environment)->CheckResult
- 优先级: P1

### R-CON-008 旅行步调距离表
- 摘要: 战斗外旅行按快速/中速/慢速，对应每分钟/小时/天的距离
- 数值/公式: `快速=400尺/分,4里/时,30里/天; 中速=300尺/分,3里/时,24里/天; 慢速=200尺/分,2里/时,18里/天`
- 状态读取: party.pace
- 状态变更: distance=pace_table[pace][unit]
- 出处: topics/玩家手册2024/进行游戏/旅行.htm
- 待实现函数: travel_distance(pace, unit)->int
- 优先级: P1

### R-CON-009 旅行步调检定修正
- 摘要: 不同步调对察觉/生存与隐匿检定施加优劣势
- 数值/公式: `快速→察觉/生存disadv + 隐匿disadv; 中速→隐匿disadv; 慢速→察觉/生存adv`
- 状态读取: party.pace, check.skill
- 状态变更: 检定加advantage/disadvantage
- 出处: topics/玩家手册2024/进行游戏/旅行.htm
- 待实现函数: apply_pace_modifier(check, pace)
- 优先级: P1

### R-CON-010 骑乘坐具加速与休整
- 摘要: 骑乘坐骑时一小时内可移动既定距离两倍；此后坐骑需短休或长休才能再次加速
- 数值/公式: `hourly_distance*=2(单次); mount.needs_rest=true; 经rest重置`
- 状态读取: party.mounted, mount.needs_rest
- 状态变更: mount.needs_rest=true/false
- 出处: topics/玩家手册2024/进行游戏/旅行.htm
- 待实现函数: apply_mounted_pace(party)->distance; reset_mount_after_rest(mount)
- 优先级: P2

### R-CON-011 水上载具航行限制
- 摘要: 水上船只受限于船只速度，不能选旅行步调，每天至多航行24小时
- 数值/公式: `pace=locked; daily_sail_hours<=24; 速度=vessel.speed`
- 状态读取: vehicle.type, vessel.speed, crew_size
- 状态变更: 跳过步调选择; sail_hours=min(24,...)
- 出处: topics/玩家手册2024/进行游戏/旅行.htm
- 待实现函数: water_vehicle_daily_distance(vessel, hours<=24)->int
- 优先级: P2

### R-CON-012 NPC态度层级
- 摘要: NPC态度分友好/冷漠/敌对；影响检定（见R-GLS-017态度优劣势）
- 数值/公式: `attitude∈{friendly,indifferent,hostile}`
- 状态读取: npc.attitude
- 状态变更: 检定优劣势依态度（见R-GLS-017）
- 出处: topics/玩家手册2024/进行游戏/交涉.htm
- 待实现函数: attitude_difficulty(attitude)->DC（见R-GLS-017）
- 优先级: P1

### R-CON-013 友好态度影响检定优势
- 摘要: 对友好态度NPC执行影响动作时，相关属性检定具优势
- 数值/公式: `if npc.attitude==friendly: influence_check.advantage=true`
- 状态读取: npc.attitude, check.skill
- 状态变更: 检定加advantage
- 出处: topics/玩家手册2024/进行游戏/交涉案例.htm
- 待实现函数: influence_npc(actor, npc, skill)->CheckResult
- 优先级: P1

### R-CON-014 洞悉检定DC（示例）
- 摘要: 感知(洞悉)检定判定NPC内心，DC由DM设
- 数值/公式: `insight=d20+WIS_mod+insight_prof vs DC=15(示例); 成功 total>=DC`
- 状态读取: check.ability=WIS, check.skill=insight
- 状态变更: 揭示NPC隐藏情绪/信息
- 出处: topics/玩家手册2024/进行游戏/交涉案例.htm
- 待实现函数: insight_check(actor, dc=15)->CheckResult
- 优先级: P2

### R-CON-015 先攻检定（案例）
- 摘要: 战斗开始各方掷d20为先攻，高者先动
- 数值/公式: `initiative=d20+DEX_mod; 排序降序`
- 状态读取: combatants[].initiative
- 状态变更: turn_order=sort_desc(initiative)
- 出处: topics/玩家手册2024/进行游戏/战斗与伤害案例.htm
- 待实现函数: roll_initiative(combatants)->turn_order
- 优先级: P0

### R-CON-016 攻击检定对护甲等级（案例）
- 摘要: 攻击掷d20+加值与目标AC比较定命中
- 数值/公式: `attack=d20+attack_bonus vs target.AC; 命中 attack>=AC`
- 状态读取: target.AC, attacker.attack_bonus
- 状态变更: 命中→触发伤害结算
- 出处: topics/玩家手册2024/进行游戏/战斗与伤害案例.htm
- 待实现函数: resolve_attack(attacker, target)->{hit, roll, total}
- 优先级: P0

### R-CON-017 伤害类型与应用（案例）
- 摘要: 命中后按伤害类型结算扣HP；类型含穿刺/钝击/雷鸣/光耀等
- 数值/公式: `hp-=damage（抗性/免疫/易伤见R-DMG）`
- 状态读取: target.hp, target.resistances, damage.type/amount
- 状态变更: target.hp-=adjusted_damage
- 出处: topics/玩家手册2024/进行游戏/战斗与伤害案例.htm
- 待实现函数: apply_damage(target, damage)->int
- 优先级: P1

### R-CON-018 偷袭触发
- 摘要: 游荡者偷袭需满足条件（目标旁有盟友等），命中时额外伤害
- 数值/公式: `触发: ally_adjacent_to_target; sneak_damage依等级骰`
- 状态读取: target.allies_nearby, rogue.level, attack.hit
- 状态变更: 伤害+=sneak_attack_dice
- 出处: topics/玩家手册2024/进行游戏/战斗与伤害案例.htm
- 待实现函数: can_sneak_attack(attacker, target)->bool; sneak_attack_damage(rogue_level)->dice
- 优先级: P1

### R-CON-019 灵巧动作-撤离
- 摘要: 游荡者可用附赠动作执行撤离，随后移动
- 数值/公式: `action_economy=bonus_action; move=依速度`
- 状态读取: actor.class==rogue, actor.bonus_action_available, actor.speed
- 状态变更: 消耗附赠动作; 移动扣减
- 出处: topics/玩家手册2024/进行游戏/战斗与伤害案例.htm
- 待实现函数: cunning_action_disengage(actor)
- 优先级: P2

### R-CON-020 反应法术-护盾术
- 摘要: 被命中时可用反应施展护盾术抵消命中
- 数值/公式: `action_economy=reaction; 本次攻击 hit=false（+5 AC来自护盾术法术条目；审计修正:+5数值不在战斗与伤害案例源文中，出处应指法术详述）`
- 状态读取: actor.reaction_available, attack.hit
- 状态变更: 消耗反应; 本次命中置否
- 出处: topics/玩家手册2024/进行游戏/战斗与伤害案例.htm
- 待实现函数: cast_shield_reaction(actor, incoming_attack)
- 优先级: P2

### R-CON-021 豁免法术判定流程
- 摘要: 部分法术/能力要求目标做属性豁免，过DC则减半/免伤，失败则全额伤害+附加效应
- 数值/公式: `save=d20+ability_mod+save_prof vs spell_DC; 失败→全额+附加; 成功→减半/免伤`
- 状态读取: target.save_bonus(ability), spell.save_dc/damage/save_ability
- 状态变更: target.hp-=damage; 位置移动/附加
- 出处: topics/玩家手册2024/进行游戏/战斗与伤害案例.htm
- 待实现函数: resolve_saving_throw(target, spell)->{success, damage, effects}
- 优先级: P1

### R-CON-022 造水/枯水术（实用法术数据）
- 摘要: 造水术在30尺立方区域落10加仑水，熄灭区域内所有火焰
- 数值/公式: `area=30尺立方; water=10加仑; 效果:熄灭区域火焰`
- 状态读取: spell.area, spell.water
- 状态变更: area.flames=extinguished
- 出处: topics/玩家手册2024/进行游戏/探索案例.htm
- 待实现函数: cast_create_water(caster, area)
- 优先级: P2

### R-CON-023 毒气陷阱致麻痹
- 摘要: 开启毒气宝箱触发体质豁免，失败则陷入麻痹
- 数值/公式: `save=d20+CON_mod+save_prof vs DC; 失败→add_condition(PARALYZED)`
- 状态读取: target.con_save_bonus, trap.save_dc
- 状态变更: 失败→add_condition(PARALYZED)
- 出处: topics/玩家手册2024/进行游戏/探索案例.htm
- 待实现函数: trigger_poison_trap(targets)->SaveResult
- 优先级: P2

### R-CON-024 无熟练亦可检定
- 摘要: 无熟练的角色掷属性检定，掷出20仍可成功；不熟练仅无熟练加值
- 数值/公式: `check=d20+ability_mod(不熟练则熟练加值+0); 成功 total>=DC`
- 状态读取: actor.proficiency[skill]
- 状态变更: 无
- 出处: topics/玩家手册2024/进行游戏/探索案例.htm
- 待实现函数: ability_check(actor, ability, skill)->total
- 优先级: P1

## 5. DM判定（R-DM，47 条）

### R-DM-001 难度等级DC（范例DC表）
- 摘要: DM为属性检定设定DC，掷骰总结果≥DC则成功；快速档以简单10/适中15/困难20设定
- 数值/公式: `范例DC={非常简单:5,简单:10,中等:15,困难:20,非常困难:25,几乎不可能:30}; success=(check_total>=dc)`
- 状态读取: check_total, dc
- 状态变更: outcome=success/failure
- 出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/难度等级.htm
- 待实现函数: ability_check(mod, prof, dc, advantage)->(success, total)
- 优先级: P0

### R-DM-002 计算DC公式
- 摘要: 生物施法或特殊能力的豁免DC标准公式
- 数值/公式: `dc = 8 + ability_mod + proficiency_bonus`
- 状态读取: ability_mod, proficiency_bonus
- 状态变更: save_dc
- 出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/难度等级.htm
- 待实现函数: calc_save_dc(ability_mod, prof)->dc
- 优先级: P0

### R-DM-003 豁免DC取值范围（仅DM即兴DC）
- 摘要: DM**即兴**设立豁免检定DC时不应低于10或高于20；计算DC（R-DM-002公式8+属性+熟练）不受此clamp约束（审计修正:限定适用域，避免误压高等级施法者算出的DC）
- 数值/公式: `if dc_source==DM_IMPROVISED: save_dc=clamp(save_dc,10,20); elif dc_source==FORMULA: save_dc=8+ability_mod+prof_bonus(不clamp)`
- 状态读取: save_dc
- 状态变更: save_dc
- 出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/难度等级.htm
- 待实现函数: clamp_save_dc(dc)->dc
- 优先级: P1

### R-DM-004 即兴伤害表
- 摘要: 临时伤害的方针表，按严重程度给出伤害骰
- 数值/公式: `severity_dice={1d10:烫伤/书柜/毒针, 2d10:闪电/火坑, 4d10:隧道碎石/强酸, 10d10:碾压/利刃/淌熔岩, 18d10:淹没熔岩/飞行堡垒, 24d10:火元素涡流/类神}`
- 状态读取: damage_event
- 状态变更: hp-=roll(count,d10)
- 出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/即兴伤害.htm
- 待实现函数: improvising_damage(severity_level)->damage_dice
- 优先级: P1

### R-DM-005 伤害危害度与等级
- 摘要: 按角色等级衡量即兴伤害的危害度（妨害/致命）
- 数值/公式: `severity_by_level={1-4: hindering=5(1d10),lethal=11(2d10); 5-10: 11,22; 11-16: 22,55; 17-20: 55,99}`
- 状态读取: char_level, damage
- 状态变更: severity=hindering/lethal
- 出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/即兴伤害.htm
- 待实现函数: damage_severity(char_level, damage)->("hindering"|"lethal")
- 优先级: P1

### R-DM-006 优势与劣势抵消
- 摘要: 同时存在优势和劣势时互相抵消，无论数量多寡
- 数值/公式: `if has_adv and has_dis: effective="none"; elif has_adv: "advantage"; elif has_dis: "disadvantage"; else "none"`
- 状态读取: has_advantage, has_disadvantage
- 状态变更: effective_advantage_status
- 出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/优势与劣势.htm
- 待实现函数: resolve_advantage(adv_sources, dis_sources)->status
- 优先级: P0

### R-DM-007 有代价的成功
- 摘要: 失败仅差1或2时，可允许以复杂情况为代价通过
- 数值/公式: `near_miss=(dc-check_total) in {1,2}; if near_miss: outcome=success_at_cost`
- 状态读取: check_total, dc
- 状态变更: outcome=success_at_cost
- 出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/后果.htm
- 待实现函数: success_at_cost(check_total, dc)->bool
- 优先级: P2

### R-DM-008 失败程度
- 摘要: 失败差值≥5可触发更严重后果
- 数值/公式: `margin=dc-check_total; if margin>=5: degree="severe"; elif margin>0: "mild"`
- 状态读取: check_total, dc
- 状态变更: failure_degree
- 出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/后果.htm
- 待实现函数: degree_of_failure(check_total, dc)->("mild"|"severe")
- 优先级: P2

### R-DM-009 成功程度（分级）
- 摘要: 成功检定可按超出DC的程度分级
- 数值/公式: `margin=check_total-dc; 分环示例(数值为示例)`
- 状态读取: check_total, dc
- 状态变更: success_degree
- 出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/后果.htm
- 待实现函数: degree_of_success(check_total, dc, tiers)->degree
- 优先级: P2

### R-DM-010 攻击天然20与天然1
- 摘要: 攻击检定天然20为重击命中，天然1永远失手（属性/豁免检定天然20/1默认无特殊效果）
- 数值/公式: `if d20==20: hit=true,critical=true; elif d20==1: hit=false`
- 状态读取: d20_roll, test_type
- 状态变更: hit, critical
- 出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/后果.htm
- 待实现函数: attack_nat_die(d20_roll)->(hit, critical)
- 优先级: P0

### R-DM-011 团队检定
- 摘要: 团队检定中若一半以上成员成功则全队通过
- 数值/公式: `group_success=(success_count > total_count/2)`
- 状态读取: success_count, total_count
- 状态变更: group_outcome
- 出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/属性检定.htm
- 待实现函数: group_check(individual_results)->success
- 优先级: P1

### R-DM-012 被动检定
- 摘要: 被动检定值=10+所有适用调整值（如被动察觉、被动洞悉）
- 数值/公式: `passive_score = 10 + sum(modifiers)`
- 状态读取: modifiers
- 状态变更: passive_score
- 出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/属性检定.htm
- 待实现函数: passive_check(modifiers)->score
- 优先级: P0

### R-DM-013 先攻定值（角色）
- 摘要: 角色先攻定值=10+所有先攻调整值（含敏捷调整值及特殊加值）
- 数值/公式: `initiative_score = 10 + sum(initiative_modifiers)`
- 状态读取: initiative_modifiers
- 状态变更: initiative_score
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/投掷先攻.htm
- 待实现函数: initiative_score(modifiers)->score
- 优先级: P0

### R-DM-014 先攻定值优劣势调整
- 摘要: 先攻掷骰具优势则定值+5，具劣势则-5
- 数值/公式: `if advantage: score+=5; elif disadvantage: score-=5`
- 状态读取: initiative_score, advantage_status
- 状态变更: initiative_score
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/投掷先攻.htm
- 待实现函数: initiative_score_adj(score, adv_status)->score
- 优先级: P1

### R-DM-015 战斗或逃跑意愿检定
- 摘要: 不确定生物是否参战时（在掷先攻前）进行DC10感知豁免，失败逃跑/谈和，通过则参战；DC可上下调整；群体由领袖代掷（审计修正:补"先攻前"时机+DC可调+群体代掷）
- 数值/公式: `dc=10; if wis_save_total>=10: fight; else: flee_or_parley`
- 状态读取: wis_save_total
- 状态变更: willingness_to_fight
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/战斗或者逃跑.htm
- 待实现函数: fight_or_flight(wis_save_total, dc=10)->("fight"|"flee"|"parley")
- 优先级: P1

### R-DM-016 怪物逃跑触发条件
- 摘要: 怪物浴血且过半盟友死亡/失能（敌方无失能），或浴血且恐慌时倾向逃跑
- 数值/公式: `flee_tendency=(bloodied and allies_down>total/2 and no_enemy_down) or (bloodied and frightened); bloodied=hp<=max_hp/2`
- 状态读取: bloodied, allies_status, frightened
- 状态变更: flee_tendency
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/战斗或者逃跑.htm
- 待实现函数: monster_flee_tendency(monster, allies)->bool
- 优先级: P2

### R-DM-017 怪物逃跑豁免
- 摘要: 怪物倾向逃跑时可进行DC10感知豁免，失败则逃跑或谈和
- 数值/公式: `dc=10; if wis_save_total<10: action in {flee,parley}`
- 状态读取: wis_save_total
- 状态变更: action
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/战斗或者逃跑.htm
- 待实现函数: monster_flee_save(wis_save_total, dc=10)->("flee"|"parley"|"stay")
- 优先级: P2

### R-DM-018 战术地图方格尺度
- 摘要: 战术地图常用单位为5尺见方
- 数值/公式: `grid_unit = 5 ft`
- 状态读取: none
- 状态变更: grid_scale
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/微缩模型.htm
- 待实现函数: tactical_grid_scale()->5
- 优先级: P2

### R-DM-019 生物体型与占据空间
- 摘要: 生物体型决定其在方格/六边格占据空间
- 数值/公式: `方格:{Tiny:1/4,Small:1,Medium:1,Large:4,Huge:9,Gargantuan:16+}; 六边格:{Tiny:1/4,Small:1,Medium:1,Large:3,Huge:7,Gargantuan:12+}`
- 状态读取: creature_size, grid_type
- 状态变更: space_occupied
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/微缩模型.htm
- 待实现函数: creature_space(size, grid_type)->squares
- 优先级: P1

### R-DM-020 效应区域方格覆盖
- 摘要: 效应区域至少覆盖半个方格/六边格则整格受影响
- 数值/公式: `affected=(covered_fraction>=0.5)`
- 状态读取: covered_fraction
- 状态变更: cell_affected
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/微缩模型.htm
- 待实现函数: aoe_cell_affected(covered_fraction)->bool
- 优先级: P1

### R-DM-021 掩护判定（方格/六边格）
- 摘要: 从攻击方角落/源点到目标四角画线，按阻挡线数确定掩护等级
- 数值/公式: `blocked=count_blocked_lines; 方格:1-2→half,3-4→three_quarters; 六边格:1-3→half,4+→three_quarters`
- 状态读取: blocked_lines, grid_type
- 状态变更: cover_level
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/微缩模型.htm
- 待实现函数: cover_level(blocked_lines, grid_type)->("none"|"half"|"three_quarters")
- 优先级: P1

### R-DM-022 视觉线判定
- 摘要: 从空间一角到另一空间任何部分的假想线无阻挡则存在视觉线
- 数值/公式: `line_of_sight = not any_blocker_intersects(corner_line)`
- 状态读取: blockers, origin_space, target_space
- 状态变更: line_of_sight
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/微缩模型.htm
- 待实现函数: has_line_of_sight(origin_space, target_space, blockers)->bool
- 优先级: P2

### R-DM-023 对角线移动（精确变体）
- 摘要: 对角线方格5尺与10尺交替计算
- 数值/公式: `第n个对角线格 cost=5 if n奇数 else 10; cost_diagonal(n)=(n//2)*15+(5 if n%2==1 else 0)`
- 状态读取: diagonal_steps
- 状态变更: movement_cost
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/微缩模型.htm
- 待实现函数: diagonal_move_cost(diagonal_steps)->feet
- 优先级: P1

### R-DM-024 远距离战斗网格比例
- 摘要: 跟进远距离战斗时可调整网格比例为每格30尺
- 数值/公式: `grid_unit = 30 ft (long_range)`
- 状态读取: combat_range
- 状态变更: grid_scale
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/跟进远距离的位置.htm
- 待实现函数: long_range_grid_scale()->30
- 优先级: P2

### R-DM-025 怪物生命值跟踪
- 摘要: 跟进怪物受伤，从HP减去伤害，归零则死亡
- 数值/公式: `hp_current-=damage; dead=(hp_current<=0)`（替代: damage_accumulated+=damage; dead=(damage_accumulated>=hp_max)）
- 状态读取: monster_hp_max, hp_current, damage
- 状态变更: monster_hp_current, monster_dead
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/跟进怪物生命值.htm
- 待实现函数: track_monster_hp(hp_current, damage)->(hp_current, dead)
- 优先级: P1

### R-DM-026 声音传播距离
- 摘要: 不同噪音等级的听力范围
- 数值/公式: `audible_distance={quiet:2d6×5ft, normal:2d6×10ft, very_loud:2d6×50ft}`
- 状态读取: noise_level
- 状态变更: audible_distance
- 出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm
- 待实现函数: audible_distance(noise_level)->ft
- 优先级: P1

### R-DM-027 户外能见度
- 摘要: 户外旅行能见度规则
- 数值/公式: `clear_day=2miles; high_vantage=40miles; rain=1mile; fog=100-300ft`
- 状态读取: weather, vantage
- 状态变更: visibility
- 出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm
- 待实现函数: outdoor_visibility(weather, vantage)->dist
- 优先级: P2

### R-DM-028 海上能见度
- 摘要: 晴朗平静海面瞭望台能见10英里，阴沉减半
- 数值/公式: `clear=10miles; overcast=5miles`
- 状态读取: sky_condition
- 状态变更: visibility
- 出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm
- 待实现函数: sea_visibility(sky)->miles
- 优先级: P2

### R-DM-029 水下遭遇距离
- 摘要: 水下能见度决定的遭遇距离
- 数值/公式: `encounter_distance={clear_bright:60ft, clear_dim:30ft, murky_or_dark:10ft}`
- 状态读取: water_clarity, lighting
- 状态变更: encounter_distance
- 出处: topics/城主指南2024/2.运作游戏/运作探索/察觉.htm
- 待实现函数: underwater_encounter_distance(clarity, lighting)->ft
- 优先级: P2

### R-DM-030 天气表
- 摘要: 投掷1d20分别确定温度、风力、降雨量
- 数值/公式: `温度:1-14正常,15-17冷1d4×10°F,18-20热1d4×10°F; 风:1-12无,13-17轻,18-20强; 雨:1-12无,13-17轻,18-20重`
- 状态读取: d20_roll×3
- 状态变更: weather
- 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
- 待实现函数: weather_roll()->(temperature, wind, rain)
- 优先级: P1

### R-DM-031 延长旅行力竭
- 摘要: 超8小时旅行每额外1小时体质豁免，DC=10+额外小时数，失败+1级力竭
- 数值/公式: `dc=10+extra_hours; if con_save_total<dc: exhaustion_level+=1 (每额外1小时)`
- 状态读取: travel_hours, con_save_total
- 状态变更: exhaustion_level
- 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
- 待实现函数: extended_travel_exhaustion(extra_hours, con_save_total)->exhaustion_added
- 优先级: P1

### R-DM-032 特殊移动旅行速率
- 摘要: 高速移动方式将速度换算为旅行速率
- 数值/公式: `mph=speed/10; miles_per_day(中速)=mph×travel_hours; fast=floor(×4/3); slow=floor(×2/3)`
- 状态读取: speed, pace, travel_hours
- 状态变更: miles_per_day
- 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
- 待实现函数: special_travel_rate(speed, pace, hours)->miles_per_day
- 优先级: P1

### R-DM-033 旅行地形表
- 摘要: 各地形的旅行参数（最快步调/遭遇距离/觅食DC/导航DC/搜索DC）
- 数值/公式: `terrain={寒带:fast/6d6×10ft/forage20/nav10/search10, 海岸:medium/2d10×10ft/10/5/15, 荒漠:medium/6d6×10ft/20/10/10, 森林:medium/2d8×10ft/10/15/15, 草原:fast/6d6×10ft/15/5/15, 丘陵:medium/2d10×10ft/15/10/15, 山地:slow/4d10×10ft/20/15/20, 沼泽:slow/2d8×10ft/10/15/20, 幽暗地域:medium/2d6×10ft/20/10/20, 城市:medium/2d6×10ft/20/15/15, 水路:special/6d6×10ft/15/10/15}`
- 状态读取: terrain
- 状态变更: max_pace, encounter_distance, forage_dc, nav_dc, search_dc
- 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
- 待实现函数: terrain_params(terrain)->{max_pace, encounter_distance, forage_dc, nav_dc, search_dc}
- 优先级: P0

### R-DM-034 路况良好提速
- 摘要: 良好道路使团队最快步调提高一节
- 数值/公式: `if good_road: max_pace=upgrade_one_step(max_pace)  # slow->medium->fast`
- 状态读取: road_quality, max_pace
- 状态变更: max_pace
- 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
- 待实现函数: apply_good_road(max_pace, good_road)->max_pace
- 优先级: P2

### R-DM-035 慢速成员拖累团队
- 摘要: 任一成员速度低于正常速度一半以下则全队必须慢速
- 数值/公式: `if any(member.speed<normal_speed/2): party_pace="slow"`
- 状态读取: member_speeds
- 状态变更: party_pace
- 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
- 待实现函数: party_pace_slow_check(member_speeds)->bool
- 优先级: P2

### R-DM-036 觅食检定
- 摘要: 觅食角色进行感知(求生)检定对抗觅食DC，成功掷1d6+感知调整值得食物磅数与水加仑
- 数值/公式: `if survival_total>=forage_dc: food_lb=1d6+wis_mod; water_gal=1d6+wis_mod; else: 0`
- 状态读取: survival_total, forage_dc, wis_mod
- 状态变更: food_lb, water_gal
- 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
- 待实现函数: forage(survival_total, forage_dc, wis_mod)->(food_lb, water_gal)
- 优先级: P1

### R-DM-037 导航检定与迷路延误
- 摘要: 迷路风险时感知(求生)检定对抗导航DC，失败偏离并延长旅程1d6×10%
- 数值/公式: `if survival_total<nav_dc: lost=true; stage_length_multiplier=1+(1d6×0.1)`
- 状态读取: survival_total, nav_dc
- 状态变更: lost, stage_length
- 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
- 待实现函数: navigation(survival_total, nav_dc)->(lost, length_multiplier)
- 优先级: P1

### R-DM-038 阻碍力竭
- 摘要: 阻碍（如暴风雪）可对角色造成1d4级力竭
- 数值/公式: `exhaustion_levels = 1d4 (示例: 暴风雪)`
- 状态读取: obstacle_type
- 状态变更: exhaustion_level
- 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
- 待实现函数: obstacle_exhaustion(obstacle_type)->levels
- 优先级: P2

### R-DM-039 追踪检定与重新搜索时间
- 摘要: 追踪失败后可在区域重新搜索，窄区10分钟/户外1小时
- 数值/公式: `if not track_success: research_time=10min(窄区) or 60min(户外)`
- 状态读取: track_success, area_type
- 状态变更: search_time
- 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
- 待实现函数: track_research_time(track_success, area_type)->minutes
- 优先级: P2

### R-DM-040 战斗回合时长
- 摘要: 一轮为6秒；战斗遭遇通常<1分钟(10回合)，四舍五入为1分钟
- 数值/公式: `round_seconds=6; typical_battle_rounds<=10; battle_seconds=rounds×6`
- 状态读取: rounds
- 状态变更: elapsed_time
- 出处: topics/城主指南2024/2.运作游戏/运作探索/跟进时间.htm
- 待实现函数: battle_duration(rounds)->seconds
- 优先级: P2

### R-DM-041 奖励XP分配
- 摘要: 战胜怪物后均分总XP；NPC提供大量帮助时计入分配
- 数值/公式: `xp_per_member = total_monster_xp / party_size`
- 状态读取: total_monster_xp, party_size
- 状态变更: character_xp
- 出处: topics/城主指南2024/2.运作游戏/角色升级.htm
- 待实现函数: award_xp(total_xp, party_size)->xp_per_member
- 优先级: P1

### R-DM-042 里程碑XP等级
- 摘要: 主要里程碑视为高难度遭遇XP，次要里程碑视为低难度遭遇XP
- 数值/公式: `milestone_xp = high_difficulty_xp if major else low_difficulty_xp`
- 状态读取: milestone_type
- 状态变更: character_xp
- 出处: topics/城主指南2024/2.运作游戏/角色升级.htm
- 待实现函数: milestone_xp(milestone_type)->xp
- 优先级: P2

### R-DM-043 长休外升级HP
- 摘要: 长休外升级时当前HP与HP上限适量增加，但不恢复已消耗资源
- 数值/公式: `hp_max+=level_up_hp_gain; hp_current+=level_up_hp_gain`
- 状态读取: level_up_hp_gain
- 状态变更: hp_max, hp_current
- 出处: topics/城主指南2024/2.运作游戏/角色升级.htm
- 待实现函数: level_up_outside_rest(character, hp_gain)->character
- 优先级: P2

### R-DM-044 通过训练获得等级（变体）
- 摘要: 变体规则，升级需训练，时长与花费依达到的等级
- 数值/公式: `training={2-4级:10天/20GP, 5-10级:20天/40GP, 11-16级:30天/60GP, 17-20级:40天/80GP}`
- 状态读取: target_level
- 状态变更: training_days, training_cost
- 出处: topics/城主指南2024/2.运作游戏/角色升级.htm
- 待实现函数: training_cost(target_level)->(days, gp)
- 优先级: P2

### R-DM-045 基于游戏回的升级速率
- 摘要: 无XP时按游戏回数升级的推荐速率（前提约4小时/回）
- 数值/公式: `sessions_to_level: 第1回→2级,第2回→3级,第3回→4级;之后每级2-3回;10级以上每级1-2回`
- 状态读取: current_level, sessions_played
- 状态变更: character_level
- 出处: topics/城主指南2024/2.运作游戏/角色升级.htm
- 待实现函数: session_based_level(current_level, sessions)->new_level
- 优先级: P2

### R-DM-046 团队规模预设
- 摘要: 规则与冒险预设4到6名玩家加DM
- 数值/公式: `default_party_size = range(4, 6)`
- 状态读取: none
- 状态变更: party_size_assumption
- 出处: topics/城主指南2024/2.运作游戏/团队规模.htm
- 待实现函数: default_party_size()->(4, 6)
- 优先级: P2

### R-DM-047 NPC态度分类
- 摘要: DM控制生物对冒险者有三种态度：友好/冷漠/敌对，可由言行改变
- 数值/公式: `attitude ∈ {"friendly", "indifferent", "hostile"}`
- 状态读取: npc, initial_attitude, interactions
- 状态变更: attitude
- 出处: topics/城主指南2024/2.运作游戏/运作交涉/态度.htm
- 待实现函数: npc_attitude(npc, initial_attitude, interactions)->attitude
- 优先级: P2

---

## 6. 施法（R-SPL，36 条）

### R-SPL-001 法术环阶范围
- 摘要: 法术环阶为0至9环，0环即戏法
- 数值/公式: `spellLevel∈{0..9}; cantrip=(level==0)`
- 状态读取: spell.level
- 状态变更: spellInstance.effectiveLevel
- 出处: topics/玩家手册2024/法术/法术环阶.htm
- 待实现函数: isValidSpellLevel(level)->bool
- 优先级: P0

### R-SPL-002 法术位消耗规则
- 摘要: 施展1环及以上法术须消耗与环阶相同或更高的法术位；戏法不消耗
- 数值/公式: `if spell.level>=1: consume slot where chosenSlotLevel>=spell.level; cantrip: cost=0`
- 状态读取: spell.level, caster.spellSlots[chosenSlotLevel]
- 状态变更: caster.spellSlots[chosenSlotLevel]-=1
- 出处: topics/玩家手册2024/法术/法术环阶.htm
- 待实现函数: consumeSpellSlot(caster, spellLevel, chosenSlotLevel)->bool
- 优先级: P0

### R-SPL-003 法术位长休恢复
- 摘要: 完成一次长休恢复所有已消耗的法术位
- 数值/公式: `onLongRest: spellSlots[l]=maxSpellSlots[l] for l in 1..9`
- 状态读取: caster.spellSlots, classTable.maxSlots
- 状态变更: caster.spellSlots[*]=max
- 出处: topics/玩家手册2024/法术/法术环阶.htm
- 待实现函数: restoreSlotsOnLongRest(caster)->void
- 优先级: P1

### R-SPL-004 升环施法
- 摘要: 用高于法术环阶的法术位施放，法术视为更高环阶；部分法术升环效应更强
- 数值/公式: `effectiveLevel=chosenSlotLevel(>=spell.level); spell.applyUpcast(effectiveLevel)`
- 状态读取: spell.level, chosenSlotLevel, spell.upcastEffect
- 状态变更: spellInstance.effectiveLevel=chosenSlotLevel
- 出处: topics/玩家手册2024/法术/法术环阶.htm
- 待实现函数: upcastSpell(spell, chosenSlotLevel)->SpellInstance
- 优先级: P0

### R-SPL-005 仪式施法
- 摘要: 带仪式标签的法术可作为仪式施展，施法时间+10分钟，不消耗法术位，不可升环
- 数值/公式: `ritualCastingTime=base+10min; slotCost=0; upcastAllowed=false`
- 状态读取: spell.ritual, spell.castingTime, caster.hasRitualCasting, caster.preparedOrKnown(spell)
- 状态变更: castMode=RITUAL
- 出处: topics/玩家手册2024/法术/法术环阶.htm
- 待实现函数: castAsRitual(caster, spell)->SpellInstance
- 优先级: P1

### R-SPL-006 施法时间类型
- 摘要: 法术施法时间为魔法动作/附赠动作/反应/1分钟或更久之一
- 数值/公式: `castingTimeType∈{MAGIC_ACTION, BONUS_ACTION, REACTION, TIME_1MIN_PLUS}`
- 状态读取: spell.castingTime
- 状态变更: 消耗对应动作槽
- 出处: topics/玩家手册2024/法术/施法时间.htm
- 待实现函数: getCastingAction(spell)->ActionType
- 优先级: P0

### R-SPL-007 每回合一法术位法术（2024）
- 摘要: 每个回合中通过施法最多消耗一个法术位（含附赠动作施法）
- 数值/公式: `spellsCastWithSlotThisTurn<=1（戏法不计）`
- 状态读取: turn.spellsCastWithSlotCount
- 状态变更: turn.spellsCastWithSlotCount+=1（消耗法术位时）
- 出处: topics/玩家手册2024/法术/施法时间.htm
- 待实现函数: canCastWithSlotThisTurn(turn)->bool
- 优先级: P0

### R-SPL-008 附赠动作施法限制（2014版，疑被R-SPL-007取代）
- 摘要: 附赠动作施法的同回合只能再施展施法时间为1动作的戏法
- 数值/公式: `if bonusActionSpellCast: otherSpellsThisTurn must be cantrips(castingTime==1action)`
- 状态读取: turn.bonusActionSpellCast, spell.castingTime, spell.level
- 状态变更: turn.bonusActionSpellCast=true
- 出处: topics/玩家手册2024/第七章/施法.htm
- 待实现函数: enforceBonusActionCantripRestriction(turn, spell)->bool
- 优先级: P2

### R-SPL-009 长时间施法专注要求
- 摘要: 施法时间1分钟或更久的法术，施法期间每回合须执行魔法动作并保持专注；失去专注则法术失败但不消耗法术位
- 数值/公式: `if castingTime>=1min: require concentration && magicActionEachTurn; onConcentrationLoss: {spellFails=true, slotConsumed=false}`
- 状态读取: spell.castingTime, caster.concentration
- 状态变更: caster.concentration=spellInstance; 失败→cancelled=true,法术位保留
- 出处: topics/玩家手册2024/法术/施法时间.htm
- 待实现函数: handleLongCastConcentrationLoss(spellInstance)->{failed, slotConsumed:false}
- 优先级: P1

### R-SPL-010 法术成分类型
- 摘要: 法术成分含言语V、姿势S、材料M；须满足全部成分需求方可施法
- 数值/公式: `components⊆{V,S,M}; castable=all(canV,canS,canM)`
- 状态读取: spell.components
- 状态变更: （仅校验）
- 出处: topics/玩家手册2024/法术/法术成分.htm
- 待实现函数: canCastByComponents(spell, caster, area)->bool
- 优先级: P0

### R-SPL-011 言语成分限制
- 摘要: 需言语成分的法术，施法者被堵嘴或身处沉默区域时无法施展
- 数值/公式: `if V in components: requires(!caster.muted && !area.silenced)`
- 状态读取: spell.components, caster.muted, area.silenced
- 状态变更: （仅校验）
- 出处: topics/玩家手册2024/法术/法术成分.htm
- 待实现函数: canCastVerbal(spell, caster, area)->bool
- 优先级: P0

### R-SPL-012 姿势成分限制
- 摘要: 需姿势成分的法术，施法者须至少空出一只手
- 数值/公式: `if S in components: caster.freeHandCount>=1`
- 状态读取: spell.components, caster.freeHandCount
- 状态变更: （仅校验）
- 出处: topics/玩家手册2024/法术/法术成分.htm
- 待实现函数: canCastSomatic(spell, caster)->bool
- 优先级: P0

### R-SPL-013 材料成分限制与替代
- 摘要: 材料成分可用材料包或法器替代，但有指定价格或被消耗的材料须实备；须一只空手
- 数值/公式: `if M in components: if spell.materialCost!=null||spell.materialConsumed: mustHoldSpecificMaterial; else: materialPouch||(focus && hasFocusFeature) suffices; freeHandCount>=1`
- 状态读取: spell.materialCost, spell.materialConsumed, caster.pouch, caster.focus, caster.hasFocusFeature, caster.freeHandCount
- 状态变更: if materialConsumed: caster.materials[item]-=1
- 出处: topics/玩家手册2024/法术/法术成分.htm
- 待实现函数: canCastMaterial(spell, caster)->bool; consumeMaterial(spell, caster)->void
- 优先级: P0

### R-SPL-014 施法距离类型
- 摘要: 施法距离为尺数/触碰/自身之一
- 数值/公式: `rangeType∈{DISTANCE(feet), TOUCH, SELF}`
- 状态读取: spell.range
- 状态变更: （仅校验）
- 出处: topics/玩家手册2024/法术/施法距离.htm
- 待实现函数: getRangeType(spell)->RangeType
- 优先级: P0

### R-SPL-015 施法距离生效后限制
- 摘要: 法术施展后其效应作用范围不再受施法距离限制，除非法术另有说明
- 数值/公式: `postCastRangeConstrained=spell.rangeConstrainedAfterCast (default false)`
- 状态读取: spell.rangeConstrainedAfterCast
- 状态变更: （仅校验）
- 出处: topics/玩家手册2024/法术/施法距离.htm
- 待实现函数: isEffectRangeConstrainedAfterCast(spell)->bool
- 优先级: P2

### R-SPL-016 自身距离与锥/线效应源
- 摘要: 以施法者为源点创造锥状或线状效应的法术，施法距离视为自身
- 数值/公式: `if spell.aoeShape in {CONE,LINE} && origin==caster: range=SELF`
- 状态读取: spell.aoeShape, spell.origin
- 状态变更: （解析距离时）
- 出处: topics/玩家手册2024/第七章/施法.htm
- 待实现函数: resolveRangeForConeLine(spell)->Range
- 优先级: P1

### R-SPL-017 持续时间类型
- 摘要: 持续时间为专注/立即/时间段之一
- 数值/公式: `durationType∈{CONCENTRATION, INSTANTANEOUS, TIME_SPAN}`
- 状态读取: spell.duration
- 状态变更: if TIME_SPAN: spellInstance.endTime=now+duration
- 出处: topics/玩家手册2024/法术/持续时间.htm
- 待实现函数: getDurationType(spell)->DurationType
- 优先级: P0

### R-SPL-018 主动结束持续法术
- 摘要: 未失能的施法者可随时结束自己施展的持续法术，无需动作
- 数值/公式: `if !caster.incapacitated: endOwnOngoingSpell(actionCost=0)`
- 状态读取: caster.incapacitated, spellInstance.caster
- 状态变更: spellInstance.ended=true
- 出处: topics/玩家手册2024/法术/持续时间.htm
- 待实现函数: endOngoingSpell(caster, spellInstance)->bool
- 优先级: P1

### R-SPL-019 专注维持与打断
- 摘要: 专注法术须维持专注；施展另一专注法术、失能或死亡会失去专注；可随时主动终止
- 数值/公式: `castConcentrationSpell→lose previous(max 1 concurrent); if incapacitated||dead: lost; voluntaryEnd: actionCost=0`
- 状态读取: caster.concentration, caster.conditions
- 状态变更: caster.concentration=newSpellInstance（旧结束）
- 出处: topics/玩家手册2024/第七章/施法.htm
- 待实现函数: setConcentration(caster, spellInstance)->void
- 优先级: P0

### R-SPL-020 专注伤害豁免
- 摘要: 专注期间受伤须过体质豁免维持；DC为10或所受伤害一半中较高者，至高30；多来源分别投
- 数值/公式: `conSaveDC=max(10, floor(damageTaken/2)); dc=min(dc,30); saveType=CON; per source: separate save; fail→lose concentration`
- 状态读取: caster.concentration, damageSource, damageAmount, caster.conSaveBonus
- 状态变更: onFail: caster.concentration=null
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm（审计修正:"至高30"上限来自术语汇编非施法.htm；DC=max(10,dmg/2)主体见R-GLS-013）
- 待实现函数: concentrationSaveOnDamage(caster, damageSources)->list<{source,dc,success}>
- 优先级: P0

### R-SPL-021 法术豁免DC
- 摘要: 法术豁免DC = 8 + 施法属性调整值 + 熟练加值
- 数值/公式: `spellSaveDC = 8 + castingAbilityMod + proficiencyBonus`
- 状态读取: caster.castingAbilityMod, caster.proficiencyBonus
- 状态变更: （只读）
- 出处: topics/玩家手册2024/法术/法术效应.htm
- 待实现函数: computeSpellSaveDC(caster)->int
- 优先级: P0

### R-SPL-022 法术攻击调整值
- 摘要: 法术攻击加值 = 施法属性调整值 + 熟练加值
- 数值/公式: `spellAttackBonus = castingAbilityMod + proficiencyBonus`
- 状态读取: caster.castingAbilityMod, caster.proficiencyBonus
- 状态变更: （只读）
- 出处: topics/玩家手册2024/法术/法术效应.htm
- 待实现函数: computeSpellAttackBonus(caster)->int
- 优先级: P0

### R-SPL-023 远程法术攻击近战劣势
- 摘要: 在敌对生物5尺范围内进行远程法术攻击具劣势（须该生物能看见你且其未失能）
- 数值/公式: `if spell.attackType==RANGED && hostile enemy within 5ft where canSeeCaster && !incapacitated: disadvantage`
- 状态读取: spell.attackType, enemies within 5ft, enemy.canSeeCaster, enemy.incapacitated
- 状态变更: attackRoll.disadvantage=true
- 出处: topics/玩家手册2024/第七章/施法.htm
- 待实现函数: applyRangedSpellAttackDisadvantage(attack, nearbyEnemies)->bool
- 优先级: P1

### R-SPL-024 无效目标法术位消耗
- 摘要: 对无效目标施展需法术位的法术，目标不受影响但法术位仍消耗
- 数值/公式: `if target.invalidForSpell && spell.needsSlot: {slotConsumed=true, effectApplied=false}`
- 状态读取: target.validForSpell, spell.needsSlot
- 状态变更: caster.spellSlots[level]-=1; spellInstance.noEffect=true
- 出处: topics/玩家手册2024/法术/法术效应.htm
- 待实现函数: handleInvalidTarget(caster, spell, target)->{slotConsumed, effectApplied}
- 优先级: P1

### R-SPL-025 无效目标豁免表现
- 摘要: 若法术在豁免成功时对目标无影响，无效目标表现为成功通过豁免（不暴露其无效）
- 数值/公式: `if spell.noEffectOnSaveSuccess && target.invalid: treatAsSaveSuccess(revealed=false); else: caster.knowsInvalid=true`
- 状态读取: spell.noEffectOnSaveSuccess, target.validForSpell
- 状态变更: target.saveResult=SUCCESS（仅表现层）
- 出处: topics/玩家手册2024/法术/法术效应.htm
- 待实现函数: maskInvalidTarget(spell, target)->bool
- 优先级: P2

### R-SPL-026 目标畅通无阻
- 摘要: 指定目标须与施法者畅通无阻，不可处于全身掩护后；路径有障碍则源点移至障碍靠近施法者一侧
- 数值/公式: `if target.fullCover: invalid; if pathBlocked: origin=obstacleSideNearCaster`
- 状态读取: target.cover, pathObstacles
- 状态变更: spellInstance.origin=adjustedPoint
- 出处: topics/玩家手册2024/法术/法术效应.htm
- 待实现函数: validateTargetPath(caster, target)->{valid, adjustedOrigin}
- 优先级: P1

### R-SPL-027 以自身为目标
- 摘要: 法术目标为生物时可选自身，除非法术须为敌对或不可为自身
- 数值/公式: `canTargetSelf=(spell.targetType==CREATURE && !requiresHostile && !excludesSelf)`
- 状态读取: spell.targetType, spell.requiresHostileTarget, spell.excludesSelf
- 状态变更: （仅校验）
- 出处: topics/玩家手册2024/法术/法术效应.htm
- 待实现函数: canTargetSelf(spell)->bool
- 优先级: P1

### R-SPL-028 法术效应混合
- 摘要: 不同法术效应叠加；同名法术多次施展不累加，取最强者，等效取最新施展
- 数值/公式: `distinct: stack; same spell: only strongest active; ties: most recent cast wins`
- 状态读取: activeEffects, spell.id, spell.bonus
- 状态变更: 抑制被覆盖的同名较弱效应
- 出处: topics/玩家手册2024/法术/法术效应.htm
- 待实现函数: combineMagicalEffects(activeEffects, newSpellInstance)->list<Effect>
- 优先级: P1

### R-SPL-029 效应区域形状
- 摘要: 效应区域形状含锥状、立方、柱状、光环、线状、球状
- 数值/公式: `aoeShape∈{CONE, CUBE, CYLINDER, AURA, LINE, SPHERE}`
- 状态读取: spell.aoe.shape
- 状态变更: （仅解析）
- 出处: topics/玩家手册2024/法术/法术效应.htm
- 待实现函数: getAoEShape(spell)->AoEShape
- 优先级: P1

### R-SPL-030 效应源点遮挡
- 摘要: 效应从源点以直线扩散；源点到某点直线被全身掩护阻挡则该点排除
- 数值/公式: `for point p in aoe: if LOS(origin,p) blockedBy totalCover: p excluded`
- 状态读取: aoe.origin, map.cover
- 状态变更: aoe.affectedPoints=filtered
- 出处: topics/玩家手册2024/第七章/施法.htm
- 待实现函数: computeAoEBlockedPoints(origin, shape, map)->set<Point>
- 优先级: P1

### R-SPL-031 各形状源点默认包含与参数
- 摘要: 线/锥/立方源点默认不含；球/柱源点含。各形状读取对应几何参数
- 数值/公式: `LINE:originIncluded=false,params={length,width}; CONE:originIncluded=false,params={maxLength}; CUBE:originIncluded=false,originOnFace,params={side}; SPHERE:originIncluded=true,params={radius_ft}; CYLINDER:originIncluded=true,params={radius_ft,height_ft}`
- 状态读取: spell.aoeShape, spell.aoe.{length,width,maxLength,side,radius,height}
- 状态变更: aoe.originIncluded
- 出处: topics/玩家手册2024/第七章/施法.htm
- 待实现函数: isOriginIncludedByDefault(shape)->bool; buildAoE(spell, origin)->AoE
- 优先级: P1

### R-SPL-032 着甲施法熟练项
- 摘要: 着甲施法须具有所着护甲的熟练项，否则施法受碍
- 数值/公式: `if caster.wearingArmor && !hasProficiency(armor): castingImpeded=true`
- 状态读取: caster.armor, caster.proficiencies
- 状态变更: （仅校验）
- 出处: topics/玩家手册2024/第七章/施法.htm
- 待实现函数: canCastInArmor(caster)->bool
- 优先级: P1

### R-SPL-033 准备法术更换表
- 摘要: 各职业准备法术列表的更换时机与单次更换数量
- 数值/公式: `吟游诗人:LEVEL_UP,1; 牧师:LONG_REST,ANY; 德鲁伊:LONG_REST,ANY; 圣武士:LONG_REST,1; 游侠:LONG_REST,1; 术士:LEVEL_UP,1; 魔契师:LEVEL_UP,1; 法师:LONG_REST,ANY`
- 状态读取: caster.class, triggerEvent
- 状态变更: caster.preparedSpells（按配额更换）
- 出处: topics/玩家手册2024/法术/获得法术.htm
- 待实现函数: canSwapPreparedSpells(class, trigger)->{allowed, count}
- 优先级: P1

### R-SPL-034 始终准备法术不计入上限
- 摘要: 始终准备的法术不计入可更改的准备法术列表数目上限
- 数值/公式: `if spell.alwaysPrepared: excludedFromPreparedLimit`
- 状态读取: spell.alwaysPrepared, caster.preparedCount, caster.maxPrepared
- 状态变更: （仅校验）
- 出处: topics/玩家手册2024/法术/获得法术.htm
- 待实现函数: isExemptFromPreparedLimit(spell)->bool
- 优先级: P2

### R-SPL-035 魔法学派分类
- 摘要: 八个魔法学派（防护/咒法/预言/惑控/塑能/幻术/死灵/变化），学派本身不带规则效应
- 数值/公式: `school∈{ABJURATION,CONJURATION,DIVINATION,ENCHANTMENT,EVOCATION,ILLUSION,NECROMANCY,TRANSMUTATION}; schoolHasInherentEffect=false`
- 状态读取: spell.school
- 状态变更: （仅标签）
- 出处: topics/玩家手册2024/法术/魔法学派.htm
- 待实现函数: getSchool(spell)->School
- 优先级: P2

### R-SPL-036 职业法术列表归属
- 摘要: 法术属于某职业法术列表则在学派后括号标职业名；特性可将法术加入非本职列表
- 数值/公式: `spell.classList=[className...]; feature.mayAddToNonNativeList(spell, class)`
- 状态读取: spell.classList, feature.addsToClassList
- 状态变更: character.classSpellList+=spell
- 出处: topics/玩家手册2024/法术/职业法术列表.htm
- 待实现函数: isOnClassSpellList(spell, className)->bool
- 优先级: P1

## 7. 装备护甲（R-ITM，42 条）

### R-ITM-001 钱币换算
- 摘要: 各钱币相对金币(GP)的价值换算
- 数值/公式: `COIN_TO_GP={"CP":0.01,"SP":0.10,"EP":0.50,"GP":1.0,"PP":10.0}; 1GP=100CP=10SP=2EP=0.1PP`
- 状态读取: character.coins{CP,SP,EP,GP,PP}
- 状态变更: character.coins[*] 增减
- 出处: topics/玩家手册2024/装备/钱币.htm
- 待实现函数: convert_coins(amount, frm, to)->float
- 优先级: P0

### R-ITM-002 钱币重量
- 摘要: 50枚钱币约重1磅
- 数值/公式: `coin_weight_lb = coin_count / 50`
- 状态读取: 各钱币数量
- 状态变更: 载重计算
- 出处: topics/玩家手册2024/装备/钱币.htm
- 待实现函数: coins_weight_lb(coins)->float
- 优先级: P1

### R-ITM-003 护甲表
- 摘要: 全部护甲的AC/力量要求/隐匿劣势/重量/价格数据
- 数值/公式:
```python
ARMOR = {
  "布甲":{"cat":"轻","base_ac":11,"dex_mode":"full","str_req":None,"stealth_disadv":True,"weight":8,"price_gp":5},
  "皮甲":{"cat":"轻","base_ac":11,"dex_mode":"full","str_req":None,"stealth_disadv":False,"weight":10,"price_gp":10},
  "镶钉皮甲":{"cat":"轻","base_ac":12,"dex_mode":"full","str_req":None,"stealth_disadv":False,"weight":13,"price_gp":45},
  "兽皮甲":{"cat":"中","base_ac":12,"dex_mode":"cap2","str_req":None,"stealth_disadv":False,"weight":12,"price_gp":10},
  "链甲衫":{"cat":"中","base_ac":13,"dex_mode":"cap2","str_req":None,"stealth_disadv":False,"weight":20,"price_gp":50},
  "鳞甲":{"cat":"中","base_ac":14,"dex_mode":"cap2","str_req":None,"stealth_disadv":True,"weight":45,"price_gp":50},
  "胸甲":{"cat":"中","base_ac":14,"dex_mode":"cap2","str_req":None,"stealth_disadv":False,"weight":20,"price_gp":400},
  "半身板甲":{"cat":"中","base_ac":15,"dex_mode":"cap2","str_req":None,"stealth_disadv":True,"weight":40,"price_gp":750},
  "环甲":{"cat":"重","base_ac":14,"dex_mode":"none","str_req":None,"stealth_disadv":True,"weight":40,"price_gp":30},
  "链甲":{"cat":"重","base_ac":16,"dex_mode":"none","str_req":13,"stealth_disadv":True,"weight":55,"price_gp":75},
  "板条甲":{"cat":"重","base_ac":17,"dex_mode":"none","str_req":15,"stealth_disadv":True,"weight":60,"price_gp":200},
  "板甲":{"cat":"重","base_ac":18,"dex_mode":"none","str_req":15,"stealth_disadv":True,"weight":65,"price_gp":1500},
  "盾牌":{"cat":"盾","base_ac":2,"dex_mode":"bonus","str_req":None,"stealth_disadv":False,"weight":6,"price_gp":10},
}
# dex_mode: full=+全部敏捷调整值; cap2=+敏捷调整值(最大+2); none=不加; bonus=盾牌AC加值(+2)
```
- 状态读取: armor_id, character.dex_mod, character.str_score
- 状态变更: character.ac
- 出处: topics/玩家手册2024/装备/护甲.htm ; topics/速查/DM速查/护甲表.htm
- 待实现函数: get_armor_entry(armor_name)->dict
- 优先级: P0

### R-ITM-004 AC计算公式
- 摘要: 根据护甲类别计算基础AC，盾牌额外+2
- 数值/公式:
```python
def compute_ac(armor_entry, dex_mod, has_shield):
    m = armor_entry["dex_mode"]
    if m=="full": ac=armor_entry["base_ac"]+dex_mod
    elif m=="cap2": ac=armor_entry["base_ac"]+min(dex_mod,2)
    elif m=="none": ac=armor_entry["base_ac"]
    elif m=="bonus": ac=armor_entry["base_ac"]
    if has_shield: ac+=2
    return ac
# 无甲基础AC=10+敏捷调整值（见R-CMB-021/R-GLS-006）
```
- 状态读取: armor.dex_mode, dex_mod, has_shield
- 状态变更: character.ac
- 出处: topics/玩家手册2024/装备/护甲.htm
- 待实现函数: compute_ac(armor_entry, dex_mod, has_shield)->int
- 优先级: P0

### R-ITM-005 护甲力量要求与移速惩罚
- 摘要: 力量低于护甲要求时移速-10尺
- 数值/公式: `if str_score < armor.str_req: speed -= 10`
- 状态读取: character.str_score, armor.str_req, character.speed
- 状态变更: character.speed（临时减10）
- 出处: topics/玩家手册2024/装备/护甲.htm
- 待实现函数: armor_str_penalty(armor_entry, str_score, base_speed)->int
- 优先级: P0

### R-ITM-006 护甲隐匿劣势
- 摘要: 标注"劣势"的护甲使穿戴者敏捷(隐匿)检定劣势
- 数值/公式: `stealth_disadv = armor_entry["stealth_disadv"]`
- 状态读取: armor_entry["stealth_disadv"]
- 状态变更: character.stealth_disadvantage
- 出处: topics/玩家手册2024/装备/护甲.htm
- 待实现函数: armor_stealth_disadv(armor_entry)->bool
- 优先级: P1

### R-ITM-007 护甲穿脱时长
- 摘要: 按护甲类别决定穿/脱时间；有人协助脱甲时间减半
- 数值/公式:
```python
ARMOR_DON_DOFF={"轻":{"don":"1分钟","doff":"1分钟"},"中":{"don":"5分钟","doff":"1分钟"},"重":{"don":"10分钟","doff":"5分钟"},"盾":{"don":"1动作","doff":"1动作"}}
# doff_with_help=doff/2; 仅完整穿甲才获AC收益
```
- 状态读取: armor.cat
- 状态变更: 动作/时间消耗
- 出处: topics/玩家手册2024/装备/护甲.htm ; topics/速查/DM速查/护甲表.htm
- 待实现函数: don_doff_time(category, action, assisted=False)->str
- 优先级: P1

### R-ITM-008 护甲受训惩罚
- 摘要: 未受训穿轻/中/重甲：所有力量或敏捷d20检定劣势且不能施法；未受训持盾无AC增益
- 数值/公式: `无护甲受训: STR/DEX d20检定→劣势; 施法→禁止; 无盾牌受训: shield_ac_bonus=0`
- 状态读取: character.armor_training{轻,中,重,盾}
- 状态变更: 检定劣势标志、施法禁用、盾牌AC置0
- 出处: topics/玩家手册2024/装备/护甲.htm
- 待实现函数: armor_training_penalty(armor_cat, training)->dict
- 优先级: P0

### R-ITM-009 一次一件
- 摘要: 一个生物同时只能着装一套护甲并持用一面盾牌
- 数值/公式: `len(equipped_armor)==1 and len(equipped_shields)<=1`
- 状态读取: character.equipped.armor, character.equipped.shield
- 状态变更: 装备槽校验
- 出处: topics/玩家手册2024/装备/护甲.htm
- 待实现函数: can_equip_armor(character)->bool
- 优先级: P1

### R-ITM-010 具装 Barding
- 摘要: 为坐骑设计的护甲，价格4倍、重量2倍
- 数值/公式: `barding_price=base*4; barding_weight=base*2`
- 状态读取: 基础护甲条目
- 状态变更: 坐骑护甲价格/重量
- 出处: topics/玩家手册2024/装备/坐骑与载具.htm
- 待实现函数: barding_stats(armor_entry)->dict
- 优先级: P2

### R-ITM-011 装备尺寸变体
- 摘要: 变体规则：不合身装备需改造，费用为市场价的1d4×10%
- 数值/公式: `alter_cost=floor(market_price * (roll_1d4*10/100))`
- 状态读取: 物品市场价
- 状态变更: 金钱消耗
- 出处: topics/玩家手册2024/装备/护甲.htm
- 待实现函数: resizing_cost(market_price_gp)->float
- 优先级: P2

### R-ITM-012 武器表(2024版)
- 摘要: 全部武器的伤害/词条/精通/重量/价格数据
- 数值/公式:
```python
WEAPONS = {
  # 简易近战
  "短棒":{"cat":"简易近战","dmg":"1d4钝击","props":["轻型"],"mastery":"缓速","wt":2,"price":"1SP"},
  "匕首":{"cat":"简易近战","dmg":"1d4穿刺","props":["灵巧","轻型","投掷20/60"],"mastery":"迅击","wt":1,"price":"2GP"},
  "巨棒":{"cat":"简易近战","dmg":"1d8钝击","props":["双手"],"mastery":"推离","wt":10,"price":"2SP"},
  "手斧":{"cat":"简易近战","dmg":"1d6挥砍","props":["轻型","投掷20/60"],"mastery":"侵扰","wt":2,"price":"5GP"},
  "标枪":{"cat":"简易近战","dmg":"1d6穿刺","props":["投掷30/120"],"mastery":"缓速","wt":2,"price":"5SP"},
  "轻锤":{"cat":"简易近战","dmg":"1d4钝击","props":["轻型","投掷20/60"],"mastery":"迅击","wt":2,"price":"2GP"},
  "硬头锤":{"cat":"简易近战","dmg":"1d6钝击","props":[],"mastery":"削弱","wt":4,"price":"5GP"},
  "长棍":{"cat":"简易近战","dmg":"1d6钝击","props":["多用1d8"],"mastery":"失衡","wt":4,"price":"2SP"},
  "镰刀":{"cat":"简易近战","dmg":"1d4挥砍","props":["轻型"],"mastery":"迅击","wt":2,"price":"1GP"},
  "矛":{"cat":"简易近战","dmg":"1d6穿刺","props":["投掷20/60","多用1d8"],"mastery":"削弱","wt":3,"price":"1GP"},
  # 简易远程
  "飞镖":{"cat":"简易远程","dmg":"1d4穿刺","props":["灵巧","投掷20/60"],"mastery":"侵扰","wt":0.25,"price":"5CP"},
  "轻弩":{"cat":"简易远程","dmg":"1d8穿刺","props":["弹药80/320","装填","双手"],"mastery":"缓速","wt":5,"price":"25GP"},
  "短弓":{"cat":"简易远程","dmg":"1d6穿刺","props":["弹药80/320","双手"],"mastery":"侵扰","wt":2,"price":"25GP"},
  "投石索":{"cat":"简易远程","dmg":"1d4钝击","props":["弹药30/120"],"mastery":"缓速","wt":None,"price":"1SP"},
  # 军用近战
  "战斧":{"cat":"军用近战","dmg":"1d8挥砍","props":["多用1d10"],"mastery":"失衡","wt":4,"price":"10GP"},
  "链枷":{"cat":"军用近战","dmg":"1d8钝击","props":[],"mastery":"削弱","wt":2,"price":"10GP"},
  "长柄刀":{"cat":"军用近战","dmg":"1d10挥砍","props":["重型","触及","双手"],"mastery":"擦掠","wt":6,"price":"20GP"},
  "巨斧":{"cat":"军用近战","dmg":"1d12挥砍","props":["重型","双手"],"mastery":"横扫","wt":7,"price":"30GP"},
  "巨剑":{"cat":"军用近战","dmg":"2d6挥砍","props":["重型","双手"],"mastery":"擦掠","wt":6,"price":"50GP"},
  "戟":{"cat":"军用近战","dmg":"1d10挥砍","props":["重型","触及","双手"],"mastery":"横扫","wt":6,"price":"20GP"},
  "骑枪":{"cat":"军用近战","dmg":"1d10穿刺","props":["重型","触及","双手(骑乘除外)"],"mastery":"失衡","wt":6,"price":"10GP"},
  "长剑":{"cat":"军用近战","dmg":"1d8挥砍","props":["多用1d10"],"mastery":"削弱","wt":3,"price":"15GP"},
  "巨锤":{"cat":"军用近战","dmg":"2d6钝击","props":["重型","双手"],"mastery":"失衡","wt":10,"price":"10GP"},
  "钉头锤":{"cat":"军用近战","dmg":"1d8穿刺","props":[],"mastery":"削弱","wt":4,"price":"15GP"},
  "长矛":{"cat":"军用近战","dmg":"1d10穿刺","props":["重型","触及","双手"],"mastery":"推离","wt":18,"price":"5GP"},
  "刺剑":{"cat":"军用近战","dmg":"1d8穿刺","props":["灵巧"],"mastery":"侵扰","wt":2,"price":"25GP"},
  "弯刀":{"cat":"军用近战","dmg":"1d6挥砍","props":["灵巧","轻型"],"mastery":"迅击","wt":3,"price":"25GP"},
  "短剑":{"cat":"军用近战","dmg":"1d6穿刺","props":["灵巧","轻型"],"mastery":"侵扰","wt":2,"price":"10GP"},
  "三叉戟":{"cat":"军用近战","dmg":"1d8穿刺","props":["投掷20/60","多用1d10"],"mastery":"失衡","wt":4,"price":"5GP"},
  "战镐":{"cat":"军用近战","dmg":"1d8穿刺","props":["多用1d10"],"mastery":"削弱","wt":2,"price":"5GP"},
  "战锤":{"cat":"军用近战","dmg":"1d8钝击","props":["多用1d10"],"mastery":"推离","wt":2,"price":"15GP"},
  "鞭":{"cat":"军用近战","dmg":"1d4挥砍","props":["灵巧","触及"],"mastery":"缓速","wt":3,"price":"2GP"},
  # 军用远程
  "吹箭筒":{"cat":"军用远程","dmg":"1穿刺","props":["弹药25/100","装填"],"mastery":"侵扰","wt":1,"price":"10GP"},
  "手弩":{"cat":"军用远程","dmg":"1d6穿刺","props":["弹药30/120","轻型","装填"],"mastery":"侵扰","wt":3,"price":"75GP"},
  "重弩":{"cat":"军用远程","dmg":"1d10穿刺","props":["弹药100/400","重型","装填","双手"],"mastery":"推离","wt":18,"price":"50GP"},
  "长弓":{"cat":"军用远程","dmg":"1d8穿刺","props":["弹药150/600","重型","双手"],"mastery":"缓速","wt":2,"price":"50GP"},
  "火铳":{"cat":"军用远程","dmg":"1d12穿刺","props":["弹药40/120","装填","双手"],"mastery":"缓速","wt":10,"price":"500GP"},
  "手铳":{"cat":"军用远程","dmg":"1d10穿刺","props":["弹药30/90","装填"],"mastery":"侵扰","wt":3,"price":"250GP"},
}
```
- 状态读取: weapon_id
- 状态变更: 攻击/伤害掷骰参数
- 出处: topics/玩家手册2024/装备/武器.htm
- 待实现函数: get_weapon_entry(name)->dict
- 优先级: P0

### R-ITM-013 武器熟练
- 摘要: 仅拥有熟练者可在武器攻击检定加入熟练加值
- 数值/公式: `attack_bonus = ability_mod + (PB if proficient else 0)`
- 状态读取: character.weapon_proficiencies, character.pb
- 状态变更: 攻击检定加值
- 出处: topics/玩家手册2024/装备/武器.htm
- 待实现函数: weapon_attack_bonus(character, weapon_cat)->int
- 优先级: P0

### R-ITM-014 武器词条(Properties)
- 摘要: 各词条判定流程与数值
- 数值/公式:
```python
PROPERTIES = {
  "弹药":"需对应弹药;每次攻击耗1枚;战后1分钟回收一半(向下取整);近战使用视为临时武器",
  "灵巧":"攻击检定与伤害可用力量或敏捷调整值(须同一值)",
  "重型":"力量<13用重型近战攻击检定劣势;敏捷<13用重型远程攻击检定劣势",
  "轻型":"攻击动作用轻型武器攻击后,可用附赠动作用另一轻型武器再攻击一次,第二次伤害不加属性调整值(负数除外)",
  "装填":"用动作/附赠/反应射击时只能射出一发,无视额外攻击次数",
  "射程":"(常规/最大);超常规射程攻击检定劣势;不能攻击最大射程外目标",
  "触及":"触及范围+5尺(含借机攻击)",
  "投掷":"可投掷发动远程攻击;近战武器投掷用近战相同属性调整值",
  "双手":"需双手并用",
  "多用":"可单手或双手;括号内为双手近战伤害",
}
```
- 状态读取: weapon.props, str_mod, dex_mod
- 状态变更: 攻击检定/伤害/射程/触及
- 出处: topics/玩家手册2024/装备/词条.htm
- 待实现函数: resolve_property(prop, context)->dict
- 优先级: P0

### R-ITM-015 精通词条(Mastery)
- 摘要: 需武器精通特性解锁的命中后效果
- 数值/公式:
```python
MASTERY = {
  "横扫":"命中后可对5尺内另一生物再攻击一次,造成武器伤害(不加属性调整值,负数除外);每回合1次",
  "擦掠":"失手仍造成=所用属性调整值的伤害(同武器伤害类型)",
  "迅击":"轻型词条的额外攻击改用攻击动作而非附赠动作(每回合仍1次)",
  "推离":"命中体型≤大型生物可直线推离至多10尺",
  "削弱":"命中后至下回合开始前,目标下一次攻击检定劣势",
  "缓速":"命中造成伤害可令目标速度-10尺至下回合开始;多次命中不叠加",
  "失衡":"命中可迫使目标体质豁免(DC=8+本次攻击调整值+PB),失败倒地",
  "侵扰":"命中造成伤害后至下回合结束前,对该生物下一次攻击检定优势",
}
```
- 状态读取: weapon.mastery, character.has_weapon_mastery_feature
- 状态变更: 目标状态(倒地/束缚/速度/优劣势标志)
- 出处: topics/玩家手册2024/装备/精通词条.htm
- 待实现函数: apply_mastery(mastery, hit, target, attacker)->list
- 优先级: P1

### R-ITM-016 弹药表与回收
- 摘要: 各类弹药的份量/容器/重量/价格及战后回收规则
- 数值/公式:
```python
AMMO={"箭矢":{"qty":20,"container":"箭袋","weight":1,"price":"1GP"},"弩矢":{"qty":20,"container":"弩矢匣","weight":1.5,"price":"1GP"},"枪械子弹":{"qty":10,"container":"小包","weight":2,"price":"3GP"},"投石索子弹":{"qty":20,"container":"小包","weight":1.5,"price":"4CP"},"吹矢":{"qty":50,"container":"小包","weight":1,"price":"1GP"}}
# 回收: 战后花1分钟搜索, 回收=floor(消耗数/2)
```
- 状态读取: ammo.type, ammo.consumed
- 状态变更: ammo.qty
- 出处: topics/玩家手册2024/装备/冒险装备.htm
- 待实现函数: recover_ammo(consumed)->int
- 优先级: P1

### R-ITM-017 2014版武器差异(遗留规则)
- 摘要: DM速查(2014版)武器表与2024版的差异点
- 数值/公式: `骑枪:2014=1d12穿刺触及特殊,2024=1d10重型触及双手(骑乘除外); 捕网2014在武器表,2024移入冒险装备; 2014重型=小型生物用重型武器劣势,2024=STR/DEX<13劣势; 2014有"特殊"词条,2024移除; 译名2014"两用"=2024"多用"`
- 状态读取: edition
- 状态变更: 武器词条/伤害
- 出处: topics/速查/DM速查/护甲，武器与物品.htm
- 待实现函数: weapon_entry_by_edition(name, edition)->dict
- 优先级: P1

### R-ITM-018 银质武器
- 摘要: 武器镀银费用，用于克制对非魔法武器免疫/抗性的怪物
- 数值/公式: `silver_cost_gp = 100 (1件武器 或 10发弹药)`
- 状态读取: 物品类型
- 状态变更: 物品.silvered=True, 金钱-100
- 出处: topics/速查/DM速查/护甲，武器与物品.htm
- 待实现函数: silver_weapon(item)->float
- 优先级: P2

### R-ITM-019 临时武器
- 摘要: 无相似武器物件造成的伤害与射程
- 数值/公式: `damage="1d4"(DM定类型); 临时投掷射程=20/60; 远程武器近战攻击或无投掷属性近战武器投掷=1d4`
- 状态读取: 物件相似度判定
- 状态变更: 伤害掷骰
- 出处: topics/速查/DM速查/护甲，武器与物品.htm
- 待实现函数: improvised_weapon_damage()->str
- 优先级: P2

### R-ITM-020 治疗药水
- 摘要: 恢复生命值的药水
- 数值/公式: `POTION_OF_HEALING={"price":"50GP","weight":0.5,"heal":"2d4+2","action":"附赠动作(2024)/动作(2014)"}; 2024可自饮或喂5尺内生物`
- 状态读取: potion.uses
- 状态变更: target.hp+=roll("2d4+2")
- 出处: topics/玩家手册2024/装备/冒险装备.htm ; topics/速查/DM速查/物品表.htm
- 待实现函数: use_potion_of_healing(target)->int
- 优先级: P1

### R-ITM-021 投掷类消耗品与DC公式
- 摘要: 强酸/炽火胶/圣水/燃油/捕网等的攻击替换与豁免DC
- 数值/公式:
```python
SPLASH_ITEMS={
  "强酸":{"price":"25GP","range":20,"save":"DEX","dc":"8+DEX_mod+PB","effect":"2d6强酸"},
  "炽火胶":{"price":"50GP","range":20,"save":"DEX","dc":"8+DEX_mod+PB","effect":"1d4火焰+燃烧"},
  "圣水":{"price":"25GP","range":20,"save":"DEX","dc":"8+DEX_mod+PB","effect":"对邪魔/亡灵失败2d8光耀"},
  "燃油(泼生物)":{"price":"1SP","range":20,"save":"DEX","dc":"8+DEX_mod+PB","effect":"覆盖;1分钟内受火焰伤害则+5火焰"},
  "燃油(泼空间)":{"price":"1SP","area":"5尺方","burn_rounds":2,"effect":"进入/结束回合者受5火焰(每回合1次)"},
  "捕网":{"price":"1GP","range":15,"save":"DEX","dc":"8+DEX_mod+PB","effect":"束缚;逃脱DC10力量(动作);摧毁AC10/5HP(免疫钝击/毒素/心灵)"},
}
```
- 状态读取: attacker.dex_mod, attacker.pb
- 状态变更: 目标HP/状态(燃烧/束缚/覆盖)
- 出处: topics/玩家手册2024/装备/冒险装备.htm ; topics/速查/DM速查/物品表.htm
- 待实现函数: use_splash_item(item_id, attacker, target)->dict
- 优先级: P1

### R-ITM-022 滚珠与铁蒺藜
- 摘要: 地面陷阱区域的豁免DC与效果
- 数值/公式: `BALL_BEARINGS={"area":"10尺方","save":"DEX","dc":10,"effect":"倒地","recover_min":10}; CALTROPS={"area":"5尺方","save":"DEX","dc":15,"effect":"1穿刺+速度0至下回合开始(2024)","recover_min":10}`
- 状态读取: 区域/生物位置
- 状态变更: 目标倒地/速度/HP
- 出处: topics/玩家手册2024/装备/冒险装备.htm ; topics/速查/DM速查/物品表.htm
- 待实现函数: apply_ground_hazard(item_id, area, targets)->list
- 优先级: P2

### R-ITM-023 基础毒药
- 摘要: 涂毒武器/弹药的额外毒素伤害
- 数值/公式: `BASIC_POISON={"price":"100GP","action":"附赠动作(2024)/动作(2014)","coat":"1把武器或3发弹药","extra_dmg":"1d4毒素","duration":"1分钟或直至造成额外伤害","trigger":"造成穿刺或挥砍伤害时","save_2014":"DC10体质,失败1d4毒素"}`
- 状态读取: weapon.poisoned, duration
- 状态变更: 目标HP(额外1d4毒素)
- 出处: topics/玩家手册2024/装备/冒险装备.htm ; topics/速查/DM速查/物品表.htm
- 待实现函数: apply_basic_poison(weapon)->dict
- 优先级: P2

### R-ITM-024 制造非魔法物品
- 摘要: 工具+原料+时间规则
- 数值/公式: `原料=floor(购买价/2); 时间(天)=ceil(购买价GP/10),每天8h; 多人:time_days/crafter_count(通常最多+1协助者); 须用指定工具且熟练`
- 状态读取: item.price_gp, tool.proficient, crafter_count
- 状态变更: 原料/金钱消耗, 制作进度
- 出处: topics/玩家手册2024/装备/制作装备.htm
- 待实现函数: craft_nonmagical(item, crafters)->dict
- 优先级: P1

### R-ITM-025 酿造治疗药水
- 摘要: 草药工具制造治疗药水的成本与时间
- 数值/公式: `tool="草药工具"; materials=25GP; time=1天(8小时)`
- 状态读取: character.tool_prof["草药工具"]
- 状态变更: 金钱-25, 获得1治疗药水
- 出处: topics/玩家手册2024/装备/制作装备.htm
- 待实现函数: brew_potion_of_healing(character)->bool
- 优先级: P2

### R-ITM-026 抄录法术卷轴
- 摘要: 按环阶的卷轴抄录时间与价格
- 数值/公式:
```python
SCROLL_COST={"戏法":(1,15),"一环":(1,25),"二环":(3,100),"三环":(5,150),"四环":(10,1000),"五环":(25,1500),"六环":(40,10000),"七环":(50,12500),"八环":(60,15000),"九环":(120,50000)}  # (天数, GP)
# 先决: 奥术技能或书法工具熟练; 每日须准备该法术; 需材料成分(消耗成分在完成时)
```
- 状态读取: spell.level, character.arcana_or_calligraphy_prof
- 状态变更: 金钱消耗, 获得卷轴
- 出处: topics/玩家手册2024/装备/制作装备.htm
- 待实现函数: scribe_scroll(spell_level, character)->dict
- 优先级: P1

### R-ITM-027 工具熟练规则
- 摘要: 工具熟练加PB；同时熟练相关技能则该检定优势
- 数值/公式: `check_bonus=ability_mod+(PB if tool_prof else 0); advantage=tool_prof and skill_prof`
- 状态读取: character.tool_prof, character.skill_prof, character.pb
- 状态变更: 检定加值/优劣势
- 出处: topics/玩家手册2024/装备/工具.htm
- 待实现函数: tool_check_bonus(character, tool_id, skill_id)->dict
- 优先级: P1

### R-ITM-028 工匠工具表
- 摘要: 各工匠工具的属性/重量/价格/操作DC/可造物品（数据见原 R-ITM-028，含炼金/酿酒/书法/木匠/制图/鞋匠/厨师/玻璃匠/珠宝匠/皮匠/石匠/画家/陶匠/铁匠/修补/织布/木雕工具）
- 数值/公式: `ARTISAN_TOOLS={各工具: {ability, weight, price_gp, utilize{操作:DC}, craft[可造物品]}}; 详见原文`
- 状态读取: tool_id
- 状态变更: 检定DC/可造列表
- 出处: topics/玩家手册2024/装备/工匠工具.htm
- 待实现函数: get_artisan_tool(tool_id)->dict
- 优先级: P2

### R-ITM-029 其他工具表
- 摘要: 易容/伪造/赌具/草药/乐器/领航/毒药/盗贼工具数据
- 数值/公式: `OTHER_TOOLS={易容工具,文书伪造工具,赌具,草药工具,乐器,领航工具,毒药工具,盗贼工具}: {ability,weight,price,utilize{DC}}; 详见原文`
- 状态读取: tool_id
- 状态变更: 检定DC
- 出处: topics/玩家手册2024/装备/其他工具.htm
- 待实现函数: get_other_tool(tool_id)->dict
- 优先级: P2

### R-ITM-030 坐骑表
- 摘要: 各动物的载重与价格
- 数值/公式: `MOUNTS={大象:(1320磅,200GP),战马:(540磅,400GP),驮用马:(540磅,50GP),乘用马:(480磅,75GP),骆驼:(450磅,50GP),骡子:(420磅,8GP),矮种马:(225磅,30GP),獒犬:(195磅,25GP)}`
- 状态读取: mount_id
- 状态变更: 载重上限/价格
- 出处: topics/玩家手册2024/装备/坐骑与载具.htm
- 待实现函数: get_mount(mount_id)->dict
- 优先级: P2

### R-ITM-031 鞍具与陆运载具
- 摘要: 鞍座类型与陆运载具数据；拖拽载重=动物基础载重×5，多动物叠加
- 数值/公式: `draw_capacity=base_carry*5*num_animals; 军用鞍座提供维持骑乘检定优势`
- 状态读取: 载具类型/动物数
- 状态变更: 载重/价格
- 出处: topics/玩家手册2024/装备/坐骑与载具.htm
- 待实现函数: drawn_vehicle_capacity(animal_carry, n_animals)->int
- 优先级: P2

### R-ITM-032 大型载具表
- 摘要: 空中与水上载具的速度/船员/乘客/货物/AC/HP/伤害阈值/价格
- 数值/公式: `LARGE_VEHICLES={飞艇,桨帆船,单帆长船,战舰,帆船,划艇,龙骨船}: {speed,crew,passengers,cargo_tons,ac,hp,dt,price}; 逆风半速; 无风仅靠桨`
- 状态读取: vehicle_id
- 状态变更: 载具AC/HP/DT
- 出处: topics/玩家手册2024/装备/坐骑与载具.htm
- 待实现函数: get_large_vehicle(vehicle_id)->dict
- 优先级: P2

### R-ITM-033 修复船只
- 摘要: 修复1点HP的耗时与费用；城市船坞减半
- 数值/公式: `repair_1hp={"time":"1天","cost":"20GP"}; 城市船坞: time/2, cost/2`
- 状态读取: 修复地点
- 状态变更: 载具HP, 金钱/时间
- 出处: topics/玩家手册2024/装备/坐骑与载具.htm
- 待实现函数: repair_ship(hp_to_repair, at_dockyard)->dict
- 优先级: P2

### R-ITM-034 生活开支
- 摘要: 每周/每月支付的生活方式日费用
- 数值/公式: `LIFESTYLE_DAILY_GP={乞食:0.0,流浪:0.1,穷困:0.2,俭朴:1.0,舒适:2.0,富裕:4.0,奢华:10.0}`
- 状态读取: character.lifestyle
- 状态变更: 金钱消耗
- 出处: topics/玩家手册2024/装备/服务.htm
- 待实现函数: lifestyle_cost(lifestyle, days)->float
- 优先级: P2

### R-ITM-035 饮食与住宿
- 摘要: 单项饮食与按生活方式的旅馆/食膳价格
- 数值/公式: `FOOD_LODGING={各项饮食价格; 旅馆住宿(每日)按生活方式; 食膳(每日)按生活方式}`
- 状态读取: lifestyle
- 状态变更: 金钱消耗
- 出处: topics/玩家手册2024/装备/服务.htm
- 待实现函数: food_lodging_cost(item, lifestyle=None)->float
- 优先级: P2

### R-ITM-036 旅行费用
- 摘要: 车夫/船运/过路费价格
- 数值/公式: `TRAVEL={城际旅程:"每里3CP",城内旅程:"每里1CP",道路/关卡费:"1CP",船运费:"每里1SP"}`
- 状态读取: 距离(里)
- 状态变更: 金钱消耗
- 出处: topics/玩家手册2024/装备/服务.htm
- 待实现函数: travel_cost(service, miles)->float
- 优先级: P2

### R-ITM-037 雇工
- 摘要: 雇佣费用标准
- 数值/公式: `HIRELINGS={熟练雇工:"每日2GP",新手雇工:"每日2SP",信使:"每里2CP"}`
- 状态读取: 雇工类型/天数/距离
- 状态变更: 金钱消耗
- 出处: topics/玩家手册2024/装备/服务.htm
- 待实现函数: hireling_cost(service, units)->float
- 优先级: P2

### R-ITM-038 施法服务
- 摘要: 按环阶购买施法的价格与可购地点(另加材料费)
- 数值/公式: `SPELLCASTING_SERVICES={戏法:村庄/城镇/城市,30GP; 一环:50GP; 二环:200GP; 三环:仅城镇/城市,300GP; 四到五环:2000GP; 六到八环:仅城市,20000GP; 九环:仅城市,100000GP}`
- 状态读取: 法术环阶/聚落类型
- 状态变更: 金钱消耗(+材料费)
- 出处: topics/玩家手册2024/装备/服务.htm
- 待实现函数: spellcasting_cost(spell_tier, material_cost=0)->float
- 优先级: P2

### R-ITM-039 魔法物品鉴定
- 摘要: 鉴定术或短休集中接触物品可获知词条(不含诅咒)
- 数值/公式: `identify_method in ["鉴定术","短休(集中接触)"]; 短休鉴定不揭示诅咒`
- 状态读取: item.identified
- 状态变更: item.identified=True
- 出处: topics/玩家手册2024/装备/魔法物品.htm
- 待实现函数: identify_magic_item(item, method)->bool
- 优先级: P1

### R-ITM-040 同调规则
- 摘要: 需同调物品须短休建立同调；同时最多3件；不可同调多个同一物品
- 数值/公式: `max_simultaneous=3; same_item_unique=True; 终止:不满足条件/距物品100尺外≥24h/死亡/他生物同调/自愿短休解除(除非诅咒)`
- 状态读取: character.attuned_items, item.requires_attunement
- 状态变更: character.attuned_items 增删
- 出处: topics/玩家手册2024/装备/魔法物品.htm
- 待实现函数: attune(character, item)->bool
- 优先级: P1

### R-ITM-041 着装同类限制
- 摘要: 不能着装多个同类魔法物品；成对物品须成对着装才生效
- 数值/公式: `EQUIP_SLOTS={足具:1,手套/护手:1,护腕:1,护甲:1,头饰:1,披风:1}; paired_items须成对`
- 状态读取: character.equipped_by_slot
- 状态变更: 装备槽校验
- 出处: topics/玩家手册2024/装备/魔法物品.htm
- 待实现函数: can_equip_magic_item(character, item)->bool
- 优先级: P1

### R-ITM-042 冒险装备价格表(关键条目)
- 摘要: 冒险装备与套组的价格/重量(合并2024与2014两表)
- 数值/公式: `GEAR={name:(price,weight_lb)}; 含强酸/炽火胶/抗毒剂/圣水/基础毒药/治疗药水/燃油/火把/蜡烛/火绒盒/滚珠/铁蒺藜/捕网/捕猎陷阱/锁/镣铐/链条/绳索/撬棍/铲子/爪钩/长杆/便携式攻城锤/医疗包/攀爬工具/放大镜/望远镜/背包/小包/麻袋/木桶/篮子/箱子/吊桶/玻璃瓶/扁瓶/铁壶/壶罐/水袋/梯子/油灯/牛眼提灯/附盖提灯/铺盖/毯子/帐篷/口粮/书籍/纸张/羊皮纸/墨水/墨水笔/地图/镜子/铃铛/信号笛/小瓶/弩矢匣/卷轴匣/箭袋/材料包/滑轮组/铁钉/套组(窃贼/外交/地城/艺人/探索/祭司/学者)/奥术法器/德鲁伊法器/圣徽; 容器容量: 背包30磅/1立方尺, 木桶40加仑/4立方尺 等`
- 状态读取: gear_id
- 状态变更: 金钱/载重
- 出处: topics/玩家手册2024/装备/冒险装备.htm ; topics/速查/DM速查/物品表.htm
- 待实现函数: get_gear_entry(name)->dict
- 优先级: P2

---

## 8. 速查数值表（R-QCK，28 条）

### R-QCK-001 伤害类型分类表
- 摘要: 13种伤害类型分类与范例
- 数值/公式: `DAMAGE_TYPES={钝击,穿刺,挥砍,强酸,寒冷,火焰,力场,闪电,暗蚀,毒素,心灵,光耀,雷鸣}; 物理三系:钝击/穿刺/挥砍`
- 状态读取: damage_type, source_effect
- 状态变更: -
- 出处: topics/速查/DM速查/伤害类型.htm
- 待实现函数: get_damage_type_label(damage_type)->str
- 优先级: P0

### R-QCK-002 抗性与易伤及伤害修改顺序
- 摘要: 易伤翻倍，抗性减半；伤害修改按固定顺序依次应用
- 数值/公式: `顺序: 1.免疫(→0) 2.加值/减值 3.一项抗性(×0.5) 4.一项易伤(×2)`
- 状态读取: immunities[], damage_modifiers[], resistances[], vulnerabilities[]
- 状态变更: final_damage
- 出处: topics/速查/DM速查/抗性与易伤.htm
- 待实现函数: apply_resistance_vulnerability(base_damage, mods)->float
- 优先级: P0

### R-QCK-003 状态条件速查表
- 摘要: 15种状态条件对攻击检定/豁免/移动的影响速查（审计修正:原14项漏列力竭；"擒抱"应为"受擒"）
- 数值/公式: `CONDITIONS={目盲,魅惑,耳聋,恐慌,受擒,失能,隐形,麻痹,石化,力竭,中毒,倒地,束缚,震慑,昏迷}; 各状态攻击/豁免/移动影响见R-GLS-043~058（力竭细节见R-GLS-047/R-QCK-004）`
- 状态读取: condition, attacker_distance, source_in_sight
- 状态变更: condition_flags, attack_roll_modifiers
- 出处: topics/速查/DM速查/状态.htm
- 待实现函数: get_condition_effect(condition, context)->dict（实现见R-GLS-043~058）
- 优先级: P0

### R-QCK-004 力竭等级递增表（2024可标度模型）
- 摘要: 力竭为可叠加状态，每获1次+1级；D20检定−(等级×2)；速度−(等级×5)尺；累计6级死亡；长休−1级（审计修正:原用2014离散分级表与R-GLS-047矛盾，改用2024累加模型）
- 数值/公式: `exhaustion_level累加; d20_penalty=level*2; speed_penalty=level*5(ft); death_at=6; long_rest→level-=1; 复活→level-=1(见R-GLS-042); 降至0结束`
- 状态读取: exhaustion_level
- 状态变更: exhaustion_level, speed, d20_modifier, dead
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: apply_exhaustion(current_level, added_level)->dict（与R-GLS-047一致）
- 优先级: P0

### R-QCK-005 掩护加值表
- 摘要: 掩护分三级，给予AC和敏捷豁免加值；全身掩护无法被直接选为目标
- 数值/公式: `COVER_BONUS={half:{ac_dex_save_bonus:+2}, three_quarters:{+5}, total:{cannot_be_targeted}}; 加值同时作用于AC和敏捷豁免`
- 状态读取: cover_level
- 状态变更: ac_bonus, dex_save_bonus, targetable
- 出处: topics/速查/DM速查/掩护.htm
- 待实现函数: get_cover_bonus(cover_level)->dict
- 优先级: P0

### R-QCK-006 坠落伤害基准规则
- 摘要: 坠落结束时每10尺受1d6钝击，最大20d6，以倒地着陆
- 数值/公式: `dice=min(fall_distance_ft//10, 20); damage=roll(d6,dice); land_prone=True`
- 状态读取: fall_distance_ft
- 状态变更: hp, condition=prone
- 出处: topics/速查/DM速查/坠落.htm
- 待实现函数: calc_falling_damage(fall_distance_ft)->tuple
- 优先级: P0

### R-QCK-007 坠落速度可选规则
- 摘要: 高空坠落分回合下降，首回合立即降500尺，其后每回合结束再降500尺
- 数值/公式: `FALL_RATE_PER_TURN_FT=500; round0立即-500; round1+回合结束-500`
- 状态读取: fall_distance_ft, round_num
- 状态变更: remaining_distance_ft
- 出处: topics/速查/DM速查/坠落.htm
- 待实现函数: fall_rate_per_round(round_num, remaining_ft)->int
- 优先级: P1

### R-QCK-008 飞行生物坠落可选规则
- 摘要: 计算坠落伤害前从坠落距离中减去当前飞行速度(适用于倒地但清醒且飞行速度>0的飞行者)
- 数值/公式: `effective=max(0, fall_distance_ft - current_fly_speed_ft); 仅适用:prone && conscious && fly_speed>0`
- 状态读取: fall_distance_ft, fly_speed_ft, is_prone, is_conscious
- 状态变更: effective_fall_distance, condition
- 出处: topics/速查/DM速查/坠落.htm
- 待实现函数: calc_flyer_fall_distance(fall_ft, fly_speed, prone, conscious)->int
- 优先级: P1

### R-QCK-009 坠落至生物上可选规则
- 摘要: 生物坠落到另一生物空间，后者DC15敏捷豁免**失败**则被撞击，坠落伤害两者均分（审计修正:原摘要"豁免成功则被撞击"方向写反）
- 数值/公式: `save_dc=15; 双方均非微型; 失败:被撞击,坠落伤害平均分配; 被撞击生物倒地除非其体型比坠落生物大≥2级; split_damage=fall_damage//2`
- 状态读取: fall_damage, target_size, faller_size
- 状态变更: target_hp, target_condition=prone, faller_hp
- 出处: topics/速查/DM速查/坠落.htm
- 待实现函数: resolve_falling_onto_creature(fall_dmg, sizes)->dict
- 优先级: P1

### R-QCK-010 陷阱豁免DC与攻击加值表
- 摘要: 陷阱按危害度三档决定豁免DC范围与攻击加值范围
- 数值/公式: `TRAP_SEVERITY={setback:{save_dc:(10,11),attack_bonus:(+3,+5)}, dangerous:{(12,15),(+6,+8)}, deadly:{(16,20),(+9,+12)}}`
- 状态读取: trap_severity
- 状态变更: trap_save_dc, trap_attack_bonus
- 出处: topics/速查/DM速查/陷阱与毒药.htm
- 待实现函数: get_trap_severity_stats(severity)->dict
- 优先级: P1

### R-QCK-011 各等级下危害度对应伤害表
- 摘要: 陷阱伤害按角色等级分四档×危害度三档，均用d10
- 数值/公式: `TRAP_DAMAGE_BY_LEVEL={(1,4):{setback:1d10,dangerous:2d10,deadly:4d10}, (5,10):{2d10,4d10,10d10}, (11,16):{4d10,10d10,18d10}, (17,20):{10d10,18d10,24d10}}`
- 状态读取: char_level_range, trap_severity
- 状态变更: trap_damage_dice
- 出处: topics/速查/DM速查/陷阱与毒药.htm
- 待实现函数: get_trap_damage_dice(char_level, severity)->str
- 优先级: P1

### R-QCK-012 复合陷阱运作规则
- 摘要: 复合陷阱每轮执行动作，激活后骰先攻(含先攻加值)，每回合开始自行激活
- 数值/公式: `激活后:1.骰先攻+描述先攻加值 2.每自己回合开始时激活并执行特定动作`
- 状态读取: trap_initiative_bonus, round_num
- 状态变更: initiative, room_state
- 出处: topics/速查/DM速查/陷阱与毒药.htm
- 待实现函数: init_complex_trap(init_bonus)->int
- 优先级: P2

### R-QCK-013 陷阱范例速查表
- 摘要: 各类陷阱范例的侦测DC/解除DC/豁免DC/伤害速查
- 数值/公式: `SAMPLE_TRAPS={塌方,落网,喷火雕像,普通陷坑,隐蔽陷坑,锁困陷坑,尖刺陷坑,毒镖,毒针,滚石,湮灭法球}: {type,trigger,spot_dc,disarm_dc,save_dc,save_attr,damage,save_success,aftermath}`
- 状态读取: trap_id, char_action
- 状态变更: detected, disarmed, hp, condition
- 出处: topics/速查/DM速查/陷阱与毒药.htm
- 待实现函数: get_sample_trap(trap_id)->dict
- 优先级: P1

### R-QCK-014 水下战斗规则
- 摘要: 无游泳速度者近战攻击劣势(特定武器除外)；远程超出常规射程直接未命中；完全没入水者火焰抗性
- 数值/公式: `MELEE_DISADV_WEAPONS_EXEMPT={匕首,标枪,短剑,矛,三叉戟}; 无游泳速度且非豁免武器→近战劣势; 远程超常规射程→auto_miss; 完全没入→火焰抗性`
- 状态读取: attacker_swim_speed, weapon, range, target_submerged
- 状态变更: attack_roll_mod, damage_resistance
- 出处: topics/速查/DM速查/水下战斗.htm
- 待实现函数: resolve_underwater_attack(context)->dict
- 优先级: P1

### R-QCK-015 骑乘上马下马与失能豁免
- 摘要: 上马下马花费一半速度移动力；坐骑被强行移动或骑手倒地须DC10敏捷豁免否则倒地
- 数值/公式: `MOUNT_DISMOUNT_COST=half_speed(坐骑5尺内); 速度不足一半或0不能上马; MOUNT_SAVE_DC=10(敏捷); 触发:坐骑被强移OR骑手倒地; 失败:坐骑5尺内倒地`
- 状态读取: speed, mount_within_5ft, mount_moved_against_will, rider_prone, mount_prone
- 状态变更: remaining_speed, condition=prone, mounted
- 出处: topics/速查/DM速查/骑乘战斗.htm
- 待实现函数: resolve_mount_dismount(context)->dict
- 优先级: P1

### R-QCK-016 控制坐骑与自主坐骑
- 摘要: 受控坐骑(须受训)用骑手先攻且仅可选疾走/撤离/回避；自主坐骑保留自身先攻且动作不受限
- 数值/公式: `CONTROLLED_MOUNT={initiative:equals_rider, allowed_actions:[Dash,Disengage,Dodge]}; INDEPENDENT_MOUNT={initiative:own, allowed_actions:unrestricted}`
- 状态读取: mount_type, mount_trained, mount_intelligence
- 状态变更: mount_initiative, mount_available_actions
- 出处: topics/速查/DM速查/骑乘战斗.htm
- 待实现函数: get_mount_mode(mount)->dict
- 优先级: P1

### R-QCK-017 毒药分类表
- 摘要: 毒药分四类(接触/服用/吸入/损伤)，各有不同施加方式与生效条件
- 数值/公式: `POISON_TYPES={contact, ingested, inhaled, injury}: {apply, trigger, duration, area}`
- 状态读取: poison_type, application
- 状态变更: poison_active, target_condition
- 出处: topics/速查/DM速查/毒药单独分页.htm
- 待实现函数: get_poison_type_info(poison_type)->dict
- 优先级: P1

### R-QCK-018 毒药价格表
- 摘要: 14种毒药每剂参考价格(gp)，按种类分类
- 数值/公式: `POISON_PRICES_GP={刺客之血:ingested,150; 焦引熏烟:inhaled,500; 食腐虫粘液:contact,200; 卓尔毒药:injury,200; 乙太精:inhaled,300; 怨恨:inhaled,250; 午夜之泪:ingested,1500; 腐精之油:contact,400; 苍白酊剂:ingested,250; 紫虫毒液:injury,2000; 蛇毒:injury,200; 蒙汗药:ingested,600; 真理之血:ingested,150; 飞龙毒液:injury,1200}`
- 状态读取: poison_name
- 状态变更: gold_spent
- 出处: topics/速查/DM速查/毒药单独分页.htm
- 待实现函数: get_poison_price(poison_name)->tuple
- 优先级: P2

### R-QCK-019 毒药范例效应表
- 摘要: 14种毒药的豁免DC、伤害、附加状态与持续时间速查
- 数值/公式: `POISON_EFFECTS={各毒药: {type, save_dc, save_attr, fail(伤害+状态), success, ends_after, delay, repeat_save}}; 详见原文`
- 状态读取: poison_name, save_result, save_margin
- 状态变更: hp, condition, condition_duration
- 出处: topics/速查/DM速查/毒药单独分页.htm
- 待实现函数: apply_poison_effect(poison_name, save_result)->dict
- 优先级: P1

### R-QCK-020 毒药制作与提炼规则
- 摘要: 从有毒生物尸体提炼毒药需1d6分钟+DC20智力(自然)检定；失败差5+则自身中毒
- 数值/公式: `HARVEST_POISON={precondition:死亡或失能, time:1d6分钟, check_dc:20, check:int(nature), success:提取1剂, fail_by_5+:自身中毒}`
- 状态读取: creature_dead_or_incapacitated, nature_proficiency
- 状态变更: inventory(poison_dose), hp, condition
- 出处: topics/速查/DM速查/毒药单独分页.htm
- 待实现函数: harvest_poison(nature_check_total)->dict
- 优先级: P2

### R-QCK-021 休整期活动-制作
- 摘要: 每日休整(≥8h)可制作市价≤5gp物品并付一半原料费；超5gp按5gp/日进度
- 数值/公式: `daily_progress_gp=5; material_cost=half_market_value; min_daily_hours=8; tool_proficiency_required=True; multi_crafter每人每日5gp`
- 状态读取: item_market_value_gp, crafter_count, tool_proficiency
- 状态变更: days_spent, gold_spent, item_completed
- 出处: topics/速查/DM速查/休整期.htm
- 待实现函数: calc_crafting_days(market_value_gp, crafters)->dict
- 优先级: P1

### R-QCK-022 休整期活动-休养
- 摘要: 每完成3日休养可做一次DC15体质豁免，成功可选终止妨碍回血效应或24h抗毒抗病优势
- 数值/公式: `period_days=3; save_dc=15; save_attr=con; success_options=[终止妨碍回血效应, 24h抗毒抗病优势]`
- 状态读取: days_recuperating, con_save_result
- 状态变更: healing_hindrance_removed, save_advantage_24h
- 出处: topics/速查/DM速查/休整期.htm
- 待实现函数: resolve_recuperation(days, con_save_total)->dict
- 优先级: P1

### R-QCK-023 休整期活动-调查与训练
- 摘要: 调查每日1gp(不含生活开支)；训练新语言/工具须250日且每日1gp
- 数值/公式: `RESEARCHING={daily_cost_gp:1}; TRAINING={duration_days:250, daily_cost_gp:1, result:新语言或工具熟练}`
- 状态读取: days_spent, gold, has_instructor
- 状态变更: gold_spent, new_language, new_tool_proficiency
- 出处: topics/速查/DM速查/休整期.htm
- 待实现函数: calc_downtime_cost(activity, days)->dict
- 优先级: P1

### R-QCK-024 单位转换-长度
- 摘要: 英制长度单位换算
- 数值/公式: `LENGTH={1尺:12寸, 1里:5280尺, 1尺:0.3048米, 1寸:2.54厘米, 1里:1.6093公里}`
- 状态读取: value, unit
- 状态变更: converted_value
- 出处: topics/速查/DM速查/单位转换.htm
- 待实现函数: convert_length(value, from_unit, to_unit)->float
- 优先级: P2

### R-QCK-025 单位转换-重量
- 摘要: 英制重量单位换算
- 数值/公式: `WEIGHT={1磅:16盎司, 1磅:453.59克, 1盎司:28.35克}`
- 状态读取: value, unit
- 状态变更: converted_value
- 出处: topics/速查/DM速查/单位转换.htm
- 待实现函数: convert_weight(value, from_unit, to_unit)->float
- 优先级: P2

### R-QCK-026 单位转换-温度
- 摘要: 华氏度与摄氏度互转公式
- 数值/公式: `F = 32 + C*1.8; C = (F-32)/1.8`
- 状态读取: temp_value, scale
- 状态变更: converted_temp
- 出处: topics/速查/DM速查/单位转换.htm
- 待实现函数: convert_temp(value, from_scale, to_scale)->float
- 优先级: P2

### R-QCK-027 单位转换-体积
- 摘要: 体积单位换算(品脱均为美制非英制)
- 数值/公式: `VOLUME={1立方尺:0.02832立方米, 1加仑:3.79升, 1品脱(液):0.473升, 1品脱(干):0.550升}`
- 状态读取: value, unit
- 状态变更: converted_value
- 出处: topics/速查/DM速查/单位转换.htm
- 待实现函数: convert_volume(value, from_unit, to_unit)->float
- 优先级: P2

### R-QCK-028 货币换算表
- 摘要: D&D货币换算关系(金币为基准)
- 数值/公式: `CURRENCY={1GP:{SP:10,CP:100,EP:2}, 1PP:{GP:10}}; 1GP=10SP=100CP=2EP; 1PP=10GP; 推导:1EP=5SP=50CP;1SP=10CP`
- 状态读取: amount, coin_type
- 状态变更: converted_amount
- 出处: topics/速查/DM速查/单位转换.htm
- 待实现函数: convert_currency(amount, from_coin, to_coin)->float
- 优先级: P2

## 9. 术语汇编（R-GLS，87 条）

> 本板块补全前述板块标记"待核实"的 P0 缺口：状态条件数值效应、危害公式、特殊感官、物件破坏、效应区域、移动速度。

### R-GLS-001 优势/劣势
- 摘要: 优势投两枚d20取高，劣势取低；复数不叠加，优劣势互相抵消
- 数值/公式: `advantage: max(2d20); disadvantage: min(2d20); both present → cancel(1d20)`
- 状态读取: adv_count, dis_count
- 状态变更: d20_result
- 出处: topics/玩家手册2024/术语汇编/D20检定.htm
- 待实现函数: resolveAdvantage(roll1, roll2, hasAdv, hasDis)->int
- 优先级: P0

### R-GLS-002 重击
- 摘要: 攻击检定d20骰出20直接命中，所有伤害骰投两次相加再加调整值
- 数值/公式: `crit_threshold=20(natural); crit_damage=sum(dice)*2+modifiers; auto-hits regardless of AC`
- 状态读取: natural_d20, damage_dice, damage_mod
- 状态变更: is_hit=true, damage_dice_count*=2
- 出处: topics/玩家手册2024/术语汇编/D20检定.htm
- 待实现函数: isCriticalHit(naturalD20)->bool; rollCriticalDamage(diceExpr, mod)->int
- 优先级: P0

### R-GLS-003 抗性/易伤/免疫
- 摘要: 抗性减半(向下取整)，易伤加倍，免疫不受影响；每个伤害实例只生效一次
- 数值/公式: `resistant: floor(dmg/2); vulnerable: dmg*2; immune: 0; once per instance`
- 状态读取: target.resistances, target.vulnerabilities, target.immunities, damage_type
- 状态变更: final_damage
- 出处: topics/玩家手册2024/术语汇编/伤害与治疗.htm
- 待实现函数: applyDamageModifiers(damage, dtype, target)->int
- 优先级: P0

### R-GLS-004 伤害阈值
- 摘要: 单次伤害低于阈值免疫，等于或超出阈值承受全额
- 数值/公式: `if single_damage<threshold: damage=0; else: damage=full_damage`
- 状态读取: target.damage_threshold
- 状态变更: applied
- 出处: topics/玩家手册2024/术语汇编/伤害与治疗.htm
- 待实现函数: applyDamageThreshold(singleDamage, threshold)->int
- 优先级: P0

### R-GLS-005 向下取整
- 摘要: 游戏中除法或乘法结果有小数则向下取整，即使小数>0.5
- 数值/公式: `round_down(x) = floor(x)`
- 状态读取: N/A
- 状态变更: value=floor(value)
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: roundDown(value)->int
- 优先级: P0

### R-GLS-006 基础护甲等级(AC)
- 摘要: 基础AC = 10 + 敏捷调整值；其他AC算法择一使用不可叠加
- 数值/公式: `base_ac = 10 + dex_mod; alt_formulas optional, pick one`
- 状态读取: actor.dex_mod, actor.ac_formula
- 状态变更: actor.ac
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: computeBaseAC(dex_mod, formula)->int
- 优先级: P0

### R-GLS-007 掩护加值
- 摘要: 半身掩护AC与敏捷豁免+2，四分之三+5，全身无法被直接选为目标；多重取最高
- 数值/公式: `half: ac+2,dex_save+2; three_quarter: +5; full: untargetable; take max`
- 状态读取: target.cover_level
- 状态变更: ac+=bonus, dex_save+=bonus
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: applyCoverBonuses(target, cover)->{ac, dex_save}
- 优先级: P0

### R-GLS-008 先攻定值
- 摘要: 不掷先攻时采用定值=10+敏捷调整值；优势+5，劣势-5
- 数值/公式: `passive_initiative = 10 + dex_mod + (adv?5:0) + (dis?-5:0)`
- 状态读取: actor.dex_mod, actor.init_adv/dis
- 状态变更: initiative_score
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: passiveInitiative(dex_mod, adv, dis)->int
- 优先级: P1

### R-GLS-009 突袭
- 摘要: 战斗开始时未察觉危险的生物，其先攻检定具有劣势
- 数值/公式: `surprised → initiative_roll disadvantage`
- 状态读取: actor.is_surprised
- 状态变更: actor.initiative_disadvantage=true
- 出处: topics/玩家手册2024/术语汇编/常见其他名词.htm
- 待实现函数: applySurpriseToInitiative(actor, isSurprised)->void
- 优先级: P1

### R-GLS-010 被动察觉
- 摘要: 被动察觉=10+感知(察觉)检定加值；优势+5，劣势-5
- 数值/公式: `passive_perception = 10 + perception_bonus + (adv?5:0) + (dis?-5:0)`
- 状态读取: actor.perception_bonus, actor.perception_adv/dis
- 状态变更: passive_perception
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: passivePerception(perception_bonus, adv, dis)->int
- 优先级: P1

### R-GLS-011 专精
- 摘要: 具有专精的技能熟练，属性检定中熟练加值加倍；与其他加倍效果不叠加
- 数值/公式: `bonus = proficiency_bonus * 2 (if expertise; not stackable)`
- 状态读取: actor.expertise_skills, actor.proficiency_bonus
- 状态变更: skill_bonus
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: applyExpertise(pb, hasExpertise)->int
- 优先级: P2

### R-GLS-012 护甲受训惩罚
- 摘要: 着甲未受训则基于力量/敏捷的D20检定劣势且无法施法；盾牌未受训无AC加值
- 数值/公式: `untrained_armor → str/dex D20 tests disadvantage + cannot cast; untrained_shield → no shield AC`
- 状态读取: actor.armor_trained[type], actor.shield_equipped/trained
- 状态变更: str_dex_disadv=true, can_cast=false
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: applyArmorTrainingPenalty(actor, armorType)->void
- 优先级: P1

### R-GLS-013 专注维持检定
- 摘要: 受伤时需通过体质豁免维持专注；DC=10或所受伤害一半(向下取整)取高者，至高30
- 数值/公式: `dc = max(10, floor(damage_taken/2)); dc = min(dc, 30); save = con_save`
- 状态读取: caster.damage_taken, caster.con_save_bonus
- 状态变更: concentration_maintained = (con_save >= dc)
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: concentrationSaveDC(damage)->int; maintainConcentration(caster, damage)->bool
- 优先级: P0

### R-GLS-014 短休
- 摘要: 1小时休整；消耗生命骰恢复HP(掷骰+体质调整值×次数，至少1)；受伤/掷先攻/施非戏法法术即打断
- 数值/公式: `duration=1hr; hp_restored=sum(hd_rolls)+con_mod*dice_count; min 1 per roll; require hp>=1`
- 状态读取: actor.hp, actor.hit_dice, actor.con_mod
- 状态变更: actor.hp+=restored; actor.hit_dice-=spent
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: shortRestHeal(actor, diceSpent)->int
- 优先级: P1

### R-GLS-015 长休
- 摘要: 至少8小时(睡眠≥6h，轻度活动≤2h)；间隔≥16h；恢复全部HP与生命骰、减少的属性值、力竭-1级
- 数值/公式: `duration_min=8hr; sleep_min=6hr; light_max=2hr; cooldown=16hr; exhaustion-=1; hp=max_hp; hit_dice reset; require hp>=1`
- 状态读取: actor.hp, actor.max_hp, actor.exhaustion_level, actor.reduced_ability_scores
- 状态变更: actor.hp=max_hp; actor.exhaustion=max(0,exhaustion-1)
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: longRestRestore(actor)->void
- 优先级: P1

### R-GLS-016 影响检定DC
- 摘要: 影响犹豫不决的怪物需属性检定，DC=15或怪物智力属性值取高者；失败24h内不可再要求
- 数值/公式: `dc = max(15, creature.int_score); failure_cooldown = 24hr`
- 状态读取: creature.int_score, creature.attitude
- 状态变更: check_success → creature acts as requested
- 出处: topics/玩家手册2024/术语汇编/动作.htm
- 待实现函数: influenceCheckDC(int_score)->int
- 优先级: P2

### R-GLS-017 态度对影响检定的优劣势
- 摘要: 友好→影响检定优势；敌对→劣势；冷漠→无；默认冷漠
- 数值/公式: `friendly → advantage; hostile → disadvantage; indifferent → none`
- 状态读取: creature.attitude
- 状态变更: check_adv/dis
- 出处: topics/玩家手册2024/术语汇编/态度.htm
- 待实现函数: attitudeAdvantage(attitude)->{adv, dis}
- 优先级: P2

### R-GLS-018 躲藏检定
- 摘要: 执行躲藏需通过DC15敏捷(隐匿)检定，且身处重度遮蔽/四分之三掩护/全身掩护且不在敌人视野内；检定总值成为他人搜寻DC
- 数值/公式: `dc=15; skill=dex(stealth); search_dc=hide_check_total`
- 状态读取: actor.stealth_bonus, actor.cover_level, actor.visibility
- 状态变更: actor.hidden=true; actor.hide_dc=roll_total
- 出处: topics/玩家手册2024/术语汇编/动作.htm
- 待实现函数: hideCheck(actor)->{success, dc}
- 优先级: P1

### R-GLS-019 击晕生物
- 摘要: 近战攻击将HP降至0时可改为降至1并昏迷开始短休；救治需动作通过DC10感知(医药)检定
- 数值/公式: `hp_set=1; condition=unconscious; stabilise_dc=10; skill=wis(medicine)`
- 状态读取: target.hp, target.wis_medicine_bonus
- 状态变更: target.hp=1; target.add(unconscious); on_success: remove(unconscious)
- 出处: topics/玩家手册2024/术语汇编/武器与徒手打击.htm
- 待实现函数: knockOut(target)->void; stabilizeDC()->int
- 优先级: P1

### R-GLS-020 死亡豁免检定触发
- 摘要: 玩家角色回合开始时HP为0，必须进行死亡豁免检定（具体数值见R-DMG-017）
- 数值/公式: `trigger: turn_start AND hp==0 → death_save; DC10/3成功稳定/3失败死亡(见R-DMG-017)`
- 状态读取: actor.hp, actor.is_player
- 状态变更: queue death_save
- 出处: topics/玩家手册2024/术语汇编/D20检定.htm
- 待实现函数: triggerDeathSave(actor)->bool
- 优先级: P0

### R-GLS-021 浴血状态
- 摘要: 生物HP≤最大HP一半时处于浴血
- 数值/公式: `bloodied = (hp <= floor(max_hp / 2))`
- 状态读取: actor.hp, actor.max_hp
- 状态变更: actor.bloodied
- 出处: topics/玩家手册2024/术语汇编/状态与其他游戏状况.htm
- 待实现函数: isBloodied(hp, max_hp)->bool
- 优先级: P1

### R-GLS-022 物件护甲等级表
- 摘要: 物件AC由材质决定
- 数值/公式: `布料/纸/绳索=11; 水晶/玻璃/冰=13; 木头=15; 石头=17; 铁/钢铁=19; 秘银=21; 精金=23`
- 状态读取: object.material
- 状态变更: object.ac
- 出处: topics/玩家手册2024/术语汇编/其他术语.htm
- 待实现函数: objectAC(material)->int
- 优先级: P0

### R-GLS-023 物件生命值表
- 摘要: 物件HP降至0被摧毁；按体型×(脆弱/牢固)查表；巨型/超巨型拆分分别计HP
- 数值/公式: `微型:脆弱2(1d4)/牢固5(2d4); 小型:3(1d6)/10(3d6); 中型:4(1d8)/18(4d8); 大型:5(1d10)/27(5d10)`
- 状态读取: object.size, object.durability
- 状态变更: object.max_hp
- 出处: topics/玩家手册2024/术语汇编/其他术语.htm
- 待实现函数: objectHP(size, durability)->{hp, dice}
- 优先级: P0

### R-GLS-024 物件伤害类型互动
- 摘要: 物件具有毒素与心灵伤害免疫；纸/布质物件可能有火焰易伤
- 数值/公式: `object.immunities={poison, psychic}; optional: paper/cloth vulnerable to fire`
- 状态读取: object.material
- 状态变更: object.immunities += [poison, psychic]
- 出处: topics/玩家手册2024/术语汇编/其他术语.htm
- 待实现函数: defaultObjectImmunities()->set
- 优先级: P1

### R-GLS-025 载重表
- 摘要: 承载/拖拽/抬起/推动上限由体型与力量属性值决定；超出承载则速度限5尺
- 数值/公式: `微型:承载STR×7.5磅,拖=STR×15; 小/中:STR×15,STR×30; 大:STR×30,STR×60; 巨:STR×60,STR×120; 超巨:STR×120,STR×240; 超载→speed=5`
- 状态读取: actor.size, actor.str_score
- 状态变更: actor.carry_cap; if load>cap: speed=5
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: carryingCapacity(size, str_score)->{carry, drag}; overloadSpeed(load, cap)->int
- 优先级: P2

### R-GLS-026 困难地形
- 摘要: 困难地形每尺移动额外消耗1尺移动力(5尺需10尺移动力)；不叠加，二元
- 数值/公式: `cost_per_ft=2(1 base+1 extra); not stackable`
- 状态读取: tile.is_difficult
- 状态变更: move_cost += extra
- 出处: topics/玩家手册2024/术语汇编/移动与速度.htm
- 待实现函数: difficultTerrainCost(base_cost, is_difficult)->int
- 优先级: P0

### R-GLS-027 攀爬/游泳/匍匐移动力
- 摘要: 攀爬/游泳/匍匐每尺额外消耗1尺(困难地形下额外2尺)；具备对应特殊速度并使用则无视额外消耗
- 数值/公式: `cost_per_ft=2(or 3 if also difficult); if has matching special speed → 1(or 2 if difficult)`
- 状态读取: actor.climb_speed, actor.swim_speed, tile.is_difficult
- 状态变更: move_cost
- 出处: topics/玩家手册2024/术语汇编/移动与速度.htm
- 待实现函数: climbCost(has_special, is_difficult)->int; swimCost(...); crawlCost(...)
- 优先级: P1

### R-GLS-028 攀爬/游泳技能检定
- 摘要: 光滑/无抓握面攀爬或激流游泳需DM判断DC15的力量(运动)检定
- 数值/公式: `dc=15; climb: str(athletics); swim_rapids: str(athletics)`
- 状态读取: N/A (DM judgment trigger)
- 状态变更: require_check(dc=15, str_athletics)
- 出处: topics/玩家手册2024/术语汇编/移动与速度.htm
- 待实现函数: climbSwimCheckDC()->int
- 优先级: P2

### R-GLS-029 跳远
- 摘要: 助跑≥10尺可跳至多=力量属性值尺；立定跳远为一半；困难地形落地需DC10敏捷(特技)否则倒地
- 数值/公式: `dist=(runup>=10ft)?str_score:floor(str_score/2); landing_difficult_dc=10 dex(acrobatics); obstacle_max=dist/4; obstacle_dc=10 str(athletics)`
- 状态读取: actor.str_score, actor.runup_dist
- 状态变更: jump_dist; on_fail → prone
- 出处: topics/玩家手册2024/术语汇编/移动与速度.htm
- 待实现函数: longJumpDist(str_score, runup)->int; longJumpLandingDC()->int
- 优先级: P1

### R-GLS-030 跳高
- 摘要: 助跑≥10尺可跳至多3+力量调整值尺(最低0)；立定跳高为一半；可触及=跳跃高度+1.5×身高
- 数值/公式: `height=(runup>=10ft)?max(0,3+str_mod):max(0,floor((3+str_mod)/2)); reach=height+1.5*actor_height`（审计修正:立定跳高补max(0,...)下限钳制）
- 状态读取: actor.str_mod, actor.runup_dist, actor.height
- 状态变更: jump_height; reach
- 出处: topics/玩家手册2024/术语汇编/移动与速度.htm
- 待实现函数: highJumpHeight(str_mod, runup)->int; highJumpReach(height, actor_height)->float
- 优先级: P1

### R-GLS-031 多速度换算
- 摘要: 拥有多个速度时移动中可切换；切换后剩余=新速度−已移动距离，≤0则不可用
- 数值/公式: `remaining_new = new_speed - distance_already_moved; if <=0 → cannot use new speed`
- 状态读取: actor.speeds[], actor.distance_moved
- 状态变更: remaining
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: switchSpeedRemaining(new_speed, distance_moved)->int
- 优先级: P1

### R-GLS-032 速度变化的连锁影响
- 摘要: 速度被增减时所有特殊速度同向同幅变化；速度0则特殊速度归0；减半则特殊速度减半
- 数值/公式: `delta applied to all special speeds; if base==0 → all special=0; if halved → all special halved`
- 状态读取: actor.base_speed, actor.special_speeds[]
- 状态变更: special_speed
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: propagateSpeedChange(actor, delta)->void
- 优先级: P1

### R-GLS-033 飞行坠落触发
- 摘要: 飞行中陷入失能/倒地/飞行速度降至0则坠落；具备悬浮能力可保持悬停
- 数值/公式: `fall_trigger = incapacitated OR prone OR fly_speed==0; hover → no fall`
- 状态读取: actor.flying, actor.hover, actor.conditions, actor.fly_speed
- 状态变更: if !hover && fall_trigger → start_falling
- 出处: topics/玩家手册2024/术语汇编/移动与速度.htm
- 待实现函数: checkFlightFall(actor)->bool
- 优先级: P1

### R-GLS-034 徒手打击
- 摘要: 徒手打击攻击加值=力量调整值+熟练加值，命中造成1+力量调整值钝击伤害；或擒抱/推撞(豁免DC=8+力量调整值+熟练加值)
- 数值/公式: `attack_bonus=str_mod+pb; damage=1+str_mod(bludgeoning); grapple/shove_save_dc=8+str_mod+pb; target_size<=attacker_size+1`
- 状态读取: actor.str_mod, actor.pb, actor.size
- 状态变更: target.hp-=damage OR target.add(grappled/prone)
- 出处: topics/玩家手册2024/术语汇编/武器与徒手打击.htm
- 待实现函数: unarmedStrikeDamage(str_mod)->int; grappleShoveDC(str_mod, pb)->int
- 优先级: P0

### R-GLS-035 临时武器
- 摘要: 临时武器攻击不加熟练加值，命中造成1d4伤害(DM定类型)；投掷常规射程20尺最大60尺
- 数值/公式: `attack_bonus=0(no pb); damage=1d4; range_normal=20ft, range_max=60ft`
- 状态读取: N/A
- 状态变更: attack.bonus-=pb; damage_dice=1d4
- 出处: topics/玩家手册2024/术语汇编/武器与徒手打击.htm
- 待实现函数: improvisedWeaponStats()->{bonus_delta, damage, range}
- 优先级: P1

### R-GLS-036 擒抱逃脱
- 摘要: 受擒生物用动作进行力量(运动)或敏捷(特技)检定对抗逃脱DC则结束受擒；擒抱者失能或距离超出范围也结束
- 数值/公式: `escape_check=str(athletics) OR dex(acrobatics) vs escape_dc; end if success OR grappler incapacitated OR out of range`
- 状态读取: target.escape_dc, target.grappler, target.distance_to_grappler
- 状态变更: on success → remove(grappled)
- 出处: topics/玩家手册2024/术语汇编/武器与徒手打击.htm
- 待实现函数: escapeGrapple(target)->bool
- 优先级: P0

### R-GLS-037 借机攻击
- 摘要: 可见生物用动作/附赠/反应/速度离开你的触及范围时，可用反应以武器/徒手打击对其发动近战攻击
- 数值/公式: `trigger: visible creature uses action/bonus/reaction/speed to leave reach; cost: reaction; attack: melee weapon/unarmed`
- 状态读取: creature.visibility, creature.distance_to_actor, actor.reach
- 状态变更: actor.reaction_used=true; melee_attack(target)
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: canOpportunityAttack(actor, target, trigger)->bool
- 优先级: P1

### R-GLS-038 传送
- 摘要: 传送不消耗移动力且不引发借机攻击；穿着携带物品随传送；目标空间被占/被阻则传送至最近未占据空间
- 数值/公式: `move_cost=0; no_opportunity_attack=true; worn_carried_transported=true; occupied/blocked → nearest unoccupied`
- 状态读取: destination.is_occupied, destination.is_blocked
- 状态变更: actor.position=nearest_unoccupied(destination)
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: teleportResolve(actor, destination)->position
- 优先级: P1

### R-GLS-039 同调上限
- 摘要: 一个生物同一时间至多同调3个魔法物品
- 数值/公式: `max_attuned = 3`
- 状态读取: actor.attuned_items
- 状态变更: can_attune = len(attuned) < 3
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: canAttuneMore(actor)->bool
- 优先级: P2

### R-GLS-040 仪式施法
- 摘要: 具仪式标签的法术可仪式施放，施法时间+10分钟，不消耗法术位且无法升环
- 数值/公式: `cast_time += 10min; slot_cost=0; cannot upcast`
- 状态读取: spell.ritual_tag, spell.cast_time
- 状态变更: cast_time += 600 (seconds)
- 出处: topics/玩家手册2024/术语汇编/法术与魔法.htm
- 待实现函数: ritualCastTime(base_time)->int
- 优先级: P2

### R-GLS-041 英雄激励重骰
- 摘要: 拥有英雄激励可在投掷任意骰子后消耗激励重骰且必须用新结果；同时最多1个
- 数值/公式: `consume_inspiration → reroll any die, must keep new; cannot hold 2`
- 状态读取: actor.heroic_inspiration
- 状态变更: actor.heroic_inspiration=false; reroll(die)
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: useHeroicInspiration(actor, die)->int
- 优先级: P2

### R-GLS-042 死亡与复活
- 摘要: 死亡生物无HP无法恢复，需魔法复活；复活法术决定当前HP；持续时间未结束的状态/疫病/诅咒维持；复活后力竭-1级；死亡解除同调
- 数值/公式: `on_revive: current_hp=spell_defined; exhaustion=max(0,exhaustion-1); attunements cleared; conditions persist`
- 状态读取: target.is_dead, target.exhaustion, target.conditions, revive_spell
- 状态变更: target.hp=spell_hp; target.exhaustion-=1; target.attuned=[]
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: reviveCreature(target, spell)->void
- 优先级: P2

### R-GLS-043 状态不叠加原则
- 摘要: 状态不会与自己叠加(有/无二元)，力竭例外可累加
- 数值/公式: `condition_stackable[exhaustion]=true; all others=false`
- 状态读取: actor.conditions[]
- 状态变更: add condition if not present (except exhaustion)
- 出处: topics/玩家手册2024/术语汇编/状态与其他游戏状况.htm
- 待实现函数: addCondition(actor, condition)->void
- 优先级: P0

### R-GLS-044 目盲状态
- 摘要: 自动失败任何需视觉的属性检定；以你为目标的攻击检定优势，你进行的攻击检定劣势
- 数值/公式: `visual_checks → auto_fail; attacks_against_self → advantage; own_attacks → disadvantage`
- 状态读取: actor.conditions[blinded]
- 状态变更: apply attack adv/dis
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyBlinded(actor)->modifiers
- 优先级: P0

### R-GLS-045 魅惑状态
- 摘要: 无法攻击魅惑源或将其作为伤害性能力/魔法效应对象；魅惑源对你社交属性检定优势
- 数值/公式: `cannot_target_charmer; charmer_social_checks → advantage`
- 状态读取: actor.conditions[charmed], actor.charmer_id
- 状态变更: block targeting charmer; charmer.social_adv=true
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyCharmed(actor)->rules
- 优先级: P1

### R-GLS-046 耳聋状态
- 摘要: 自动失败任何依赖听觉的属性检定
- 数值/公式: `audio_checks → auto_fail`
- 状态读取: actor.conditions[deafened]
- 状态变更: mark audio auto-fail
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyDeafened(actor)->void
- 优先级: P1

### R-GLS-047 力竭状态
- 摘要: 可叠加；每获得1次等级+1；D20检定减去力竭等级×2；速度减少力竭等级×5尺；6级即死；长休-1级
- 数值/公式: `d20_penalty=exhaustion_level*2; speed_penalty=exhaustion_level*5(ft); death_at=6; long_rest→level-=1; end at 0`
- 状态读取: actor.exhaustion_level
- 状态变更: d20_modifier-=level*2; speed-=level*5; if level>=6 → dead
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyExhaustion(actor)->{d20_penalty, speed_penalty, is_dead}
- 优先级: P0

### R-GLS-048 恐慌状态
- 摘要: 恐惧源在视线内时，你的属性检定与攻击检定劣势；无法自愿向靠近恐惧源方向移动
- 数值/公式: `if source_visible → disadvantage on ability_checks & attack_rolls; cannot voluntarily move closer`
- 状态读取: actor.conditions[frightened], actor.can_see_source
- 状态变更: checks/attacks disadvantage; block approach moves
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyFrightened(actor)->void
- 优先级: P0

### R-GLS-049 受擒状态
- 摘要: 速度变为0且无法增加；对除擒抱者外目标的攻击检定劣势；擒抱者移动可拖拽承载，每尺额外耗1尺(受擒者微型或体型小于擒抱者2级以上则无额外消耗)
- 数值/公式: `speed=0(non-incrementable); attacks vs non-grappler → disadvantage; drag_cost=1ft/ft unless (size==tiny OR size<=grappler_size-2)`
- 状态读取: actor.conditions[grappled], actor.grappler_id, actor.size, grappler.size
- 状态变更: speed=0; attack_disadvantage=true; grappler.move_cost_modifier
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyGrappled(actor)->void; grappleDragCost(grappled_size, grappler_size)->int
- 优先级: P0

### R-GLS-050 失能状态
- 摘要: 无法执行任何动作/附赠动作/反应；专注被打断；无法说话；失能期间掷先攻劣势
- 数值/公式: `actions=0; bonus=0; reactions=0; concentration_broken=true; speechless=true; initiative_disadvantage=true`
- 状态读取: actor.conditions[incapacitated]
- 状态变更: disable all action economy; break concentration
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyIncapacitated(actor)->void
- 优先级: P0

### R-GLS-051 隐形状态
- 摘要: 掷先攻优势；任何需看见目标的效应不影响你(除非源头能看见你)；以你为目标的攻击检定劣势，你进行的攻击检定优势；被看见则不获增益
- 数值/公式: `initiative_adv=true; untargetable by sight-dependent effects unless seen; attacks_against_self → disadvantage; own_attacks → advantage`
- 状态读取: actor.conditions[invisible], observer.can_see(actor)
- 状态变更: apply adv/dis; conceal equipment
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyInvisible(actor, observer)->modifiers
- 优先级: P0

### R-GLS-052 麻痹状态
- 摘要: 失能；速度0且无法增加；自动失败力量与敏捷豁免；以你为目标的攻击检定优势；5尺内的攻击者命中即重击
- 数值/公式: `incapacitated=true; speed=0; auto_fail(str,dex save); attacks_against → advantage; melee within 5ft → critical on hit`
- 状态读取: actor.conditions[paralyzed], attacker.distance
- 状态变更: apply modifiers; crit on hit if within 5ft
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyParalyzed(actor)->void; isAutoCrit(target, attacker_dist)->bool
- 优先级: P0

### R-GLS-053 石化状态
- 摘要: 化为坚固非活动材质；重量变10倍；停止老化；失能；速度0；以你为目标攻击优势；自动失败力量/敏捷豁免；具所有伤害抗性；具中毒免疫
- 数值/公式: `weight*=10; aging_stopped=true; incapacitated=true; speed=0; auto_fail(str,dex); attacks_against→advantage; all_damage_resistant=true; immune(poisoned)`
- 状态读取: actor.conditions[petrified]
- 状态变更: apply all; damage*=0.5
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyPetrified(actor)->void
- 优先级: P0

### R-GLS-054 中毒状态
- 摘要: 你进行的攻击检定与属性检定具有劣势
- 数值/公式: `attack_rolls → disadvantage; ability_checks → disadvantage`
- 状态读取: actor.conditions[poisoned]
- 状态变更: add disadvantage to own attack/ability
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyPoisoned(actor)->void
- 优先级: P0

### R-GLS-055 倒地状态
- 摘要: 唯二移动选项为匍匐或耗速度一半(向下取整)起立终止(速度0无法起立)；你的攻击检定劣势；5尺内攻击者对你优势，5尺外对你劣势
- 数值/公式: `stand_cost=floor(speed/2); if speed==0 cannot stand; own_attacks → disadvantage; attacks_vs_self: within5ft→advantage, beyond5ft→disadvantage`
- 状态读取: actor.conditions[prone], attacker.distance
- 状态变更: apply modifiers; stand option
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyProne(actor)->void; proneAttackMod(attacker_dist)->{adv, dis}
- 优先级: P0

### R-GLS-056 束缚状态
- 摘要: 速度0且无法增加；以你为目标的攻击检定优势，你进行的攻击检定劣势；你的敏捷豁免劣势
- 数值/公式: `speed=0; attacks_against_self → advantage; own_attacks → disadvantage; dex_save → disadvantage`
- 状态读取: actor.conditions[restrained]
- 状态变更: apply modifiers
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyRestrained(actor)->void
- 优先级: P0

### R-GLS-057 震慑状态
- 摘要: 失能；自动失败力量与敏捷豁免；以你为目标的攻击检定优势
- 数值/公式: `incapacitated=true; auto_fail(str,dex save); attacks_against_self → advantage`
- 状态读取: actor.conditions[stunned]
- 状态变更: apply modifiers
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyStunned(actor)->void
- 优先级: P0

### R-GLS-058 昏迷状态
- 摘要: 失能+倒地，手持物全掉落(状态结束倒地不结束)；速度0；以你为目标攻击优势；自动失败力量/敏捷豁免；5尺内攻击者命中即重击；无法感知周遭
- 数值/公式: `incapacitated=true; prone=true(persists); drop items; speed=0; auto_fail(str,dex); attacks_against→advantage; melee within5ft→crit on hit; unaware`
- 状态读取: actor.conditions[unconscious], attacker.distance
- 状态变更: apply all; crit within 5ft
- 出处: topics/玩家手册2024/术语汇编/状态.htm
- 待实现函数: applyUnconscious(actor)->void
- 优先级: P0

### R-GLS-059 燃烧危害
- 摘要: 燃烧中的生物/物件每回合开始受1d4火焰伤害；可用动作打滚熄火并陷入倒地；浇灭/淹灭/扑灭亦熄
- 数值/公式: `damage_per_turn_start = 1d4 fire; extinguish: action + prone; OR doused/submerged`
- 状态读取: target.conditions[burning]
- 状态变更: target.hp-=roll(1d4); on action → remove(burning), add(prone)
- 出处: topics/玩家手册2024/术语汇编/危害.htm
- 待实现函数: burningDamage()->int; extinguishFire(target)->void
- 优先级: P0

### R-GLS-060 脱水危害
- 摘要: 每日饮水低于需求量一半则当日结束获得1级力竭；饮足完整一日需求量前无法移除
- 数值/公式: `daily_water_need: tiny=1/4gal, small=1gal, medium=1gal, large=4gal, huge=16gal, gargantuan=64gal; if intake<half → exhaustion+=1; removable only after full day intake`
- 状态读取: actor.size, actor.daily_water_intake, actor.exhaustion
- 状态变更: if intake<need/2: exhaustion+=1
- 出处: topics/玩家手册2024/术语汇编/危害.htm
- 待实现函数: dailyWaterNeed(size)->float; applyDehydration(actor, intake)->void
- 优先级: P0

### R-GLS-061 坠落危害
- 摘要: 坠落结束时每10尺受1d6钝击(至多20d6)；未全数避免则着地陷倒地；坠入液体可反应DC15力量(运动)或敏捷(特技)，成功则伤害减半
- 数值/公式: `damage=min(20, floor(fall_dist/10)) d6 bludgeoning; if not fully avoided → prone; water: dc=15 str(athletics) or dex(acrobatics), success → damage/2`
- 状态读取: fall_distance, into_liquid
- 状态变更: target.hp-=damage; add(prone) if not avoided
- 出处: topics/玩家手册2024/术语汇编/危害.htm
- 待实现函数: fallDamage(fall_dist)->int; waterLandingDC()->int
- 优先级: P0

### R-GLS-062 饥饿危害
- 摘要: 每日进食低于需求量一半则当日结束DC10体质豁免，失败获1级力竭；连续5天不食第5天结束自动获1级，其后每日+1级；吃足完整一日需求量前无法移除
- 数值/公式: `daily_food_need: tiny=1/4lb, small=1lb, medium=1lb, large=4lb, huge=16lb, gargantuan=64lb; if intake<half → dc=10 con_save, fail→exhaustion+=1; 5 days no food → auto +1, then +1/day; removable only after full day intake`
- 状态读取: actor.size, actor.daily_food_intake, actor.days_starved, actor.con_save
- 状态变更: apply exhaustion
- 出处: topics/玩家手册2024/术语汇编/危害.htm
- 待实现函数: dailyFoodNeed(size)->float; applyStarvation(actor, intake)->void
- 优先级: P0

### R-GLS-063 窒息危害
- 摘要: 可屏息至多1+体质调整值分钟(至少30秒)后开始窒息；屏息殆尽或呼吸受阻则每回合结束获1级力竭；可呼吸时所有窒息力竭移除
- 数值/公式: `breath_hold=max(30sec, (1+con_mod)*60sec); after: exhaustion+=1 per turn end; on breathe: remove all suffocation exhaustion`
- 状态读取: actor.con_mod, actor.breath_hold_remaining
- 状态变更: if suffocating: exhaustion+=1/turn; if breathing: clear suffocation exhaustion
- 出处: topics/玩家手册2024/术语汇编/危害.htm
- 待实现函数: breathHoldDuration(con_mod)->int(seconds); applySuffocation(actor)->void
- 优先级: P0

### R-GLS-064 盲视感官
- 摘要: 不依赖物理视觉看见特定范围内事物；范围内可见任何事物(除全身掩护)，含目盲/黑暗/隐形中的事物
- 数值/公式: `radius=creature_defined(从数据卡senses字段读); can_see: ignores blinded/darkness/invisibility; blocked by total cover`
- 状态读取: actor.senses[blindsight].radius, target.cover_level, target.conditions
- 状态变更: target.visible_to_actor=true if within radius and not total_cover
- 出处: topics/玩家手册2024/术语汇编/光照与视觉.htm
- 待实现函数: blindsightCanSee(actor, target)->bool
- 优先级: P0

### R-GLS-065 黑暗视觉感官
- 摘要: 特定范围内微光光照视为明亮光照，黑暗视为微光光照(灰度，无颜色)
- 数值/公式: `radius=creature_defined(从senses读); dim→bright; darkness→dim; no color in darkness`
- 状态读取: actor.senses[darkvision].radius, tile.light_level
- 状态变更: effective_light=upgrade one tier within radius
- 出处: topics/玩家手册2024/术语汇编/光照与视觉.htm
- 待实现函数: darkvisionLightLevel(base_level, in_radius)->level
- 优先级: P0

### R-GLS-066 真实视觉感官
- 摘要: 特定范围内可看破黑暗(含魔法)、隐形、视觉幻象(自动通过豁免)、魔法变化形态、以太位面事物
- 数值/公式: `radius=creature_defined(从senses读); see_through: darkness(magical+mundane), invisibility, visual illusions(auto-pass), transformations(true form), ethereal plane`
- 状态读取: actor.senses[truesight].radius
- 状态变更: apply true sight flags
- 出处: topics/玩家手册2024/术语汇编/光照与视觉.htm
- 待实现函数: truesightCapabilities(actor)->flags
- 优先级: P0

### R-GLS-067 震颤感知感官
- 摘要: 精确定位特定范围内与同表面/液体接触的生物与移动物件；无法侦测空中目标；不算视觉能力
- 数值/公式: `radius=creature_defined(从senses读); requires shared surface/liquid contact; cannot detect airborne; not visual`
- 状态读取: actor.senses[tremorsense].radius, target.on_same_surface, target.is_airborne
- 状态变更: can_pinpoint if within radius and shared surface
- 出处: topics/玩家手册2024/术语汇编/特殊能力词汇.htm
- 待实现函数: tremorsenseCanDetect(actor, target)->bool
- 优先级: P0

### R-GLS-068 光照遮蔽层级
- 摘要: 明亮正常可见；微光为轻度遮蔽(察觉检定劣势)；黑暗为重度遮蔽(尝试看则目盲)
- 数值/公式: `bright→normal; dim→lightly_obscured(perception disadvantage); darkness→heavily_obscured(blinded when viewing)`
- 状态读取: tile.light_level
- 状态变更: apply obscurement penalty
- 出处: topics/玩家手册2024/术语汇编/光照与视觉.htm
- 待实现函数: lightObscurement(light_level)->{level, perception_disadvantage}
- 优先级: P1

### R-GLS-069 心灵感应
- 摘要: 特定范围内可精神联结其他生物；不需共通语言但对象须懂一门语言或亦有心灵感应；不需可见；任一方失能则终止
- 数值/公式: `radius=creature_defined(从senses读); requires: target understands a language OR has telepathy; ends on: incapacity either side, out of range`
- 状态读取: actor.senses[telepathy].radius, target.knows_language, target.has_telepathy
- 状态变更: link established/broken
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: canEstablishTelepathy(actor, target)->bool
- 优先级: P2

### R-GLS-070 效应区域总则
- 摘要: 效应区域有源点，能量从源点扩散；源点到区域内某点画不出未被全身掩护阻挡的直线则不属于区域；看不见的源点移到中间障碍物更近创造者一侧
- 数值/公式: `blocked_by=total_cover_only; line_of_effect required; blind source → relocate to near side of obstacle`
- 状态读取: aoe.source, obstacles, creator.can_see(source)
- 状态变更: aoe.cells=computeLineOfSight(source)
- 出处: topics/玩家手册2024/术语汇编/效应区域.htm
- 待实现函数: aoeAffectedCells(source, obstacles)->set
- 优先级: P1

### R-GLS-071 锥状效应区域
- 摘要: 创造者选方向；从源点沿轴向扩散，任意点截面直径=该点到源点距离；源点默认不含
- 数值/公式: `diameter_at_dist_d=d; source_excluded by default`
- 状态读取: aoe.size, aoe.direction
- 状态变更: cells=cone(source, direction, size)
- 出处: topics/玩家手册2024/术语汇编/效应区域.htm
- 待实现函数: coneCells(source, direction, size)->set
- 优先级: P1

### R-GLS-072 立方效应区域
- 摘要: 源点在立方任意一面上；参数为每边长度；源点默认不含
- 数值/公式: `side=specified; source_on_face; source_excluded by default`
- 状态读取: aoe.size
- 状态变更: cells=cube(source, size)
- 出处: topics/玩家手册2024/术语汇编/效应区域.htm
- 待实现函数: cubeCells(source, size)->set
- 优先级: P1

### R-GLS-073 柱状效应区域
- 摘要: 源点在顶/底面中心；参数为底面半径与高；源点含于区域
- 数值/公式: `radius=specified; height=specified; source_included=true`
- 状态读取: aoe.radius, aoe.height
- 状态变更: cells=cylinder(source, radius, height)
- 出处: topics/玩家手册2024/术语汇编/效应区域.htm
- 待实现函数: cylinderCells(source, radius, height)->set
- 优先级: P1

### R-GLS-074 光环效应区域
- 摘要: 源自生物/物件向全方向扩散；参数为最大扩散距离；非立即/非固定则跟随源头移动；源头默认不含
- 数值/公式: `radius=specified; follows_source unless instantaneous or fixed; source_excluded by default`
- 状态读取: aoe.radius, aoe.duration_type
- 状态变更: cells=emanation(source.position, radius)
- 出处: topics/玩家手册2024/术语汇编/效应区域.htm
- 待实现函数: emanationCells(source, radius)->set
- 优先级: P1

### R-GLS-075 线状效应区域
- 摘要: 从源点沿直线路径传播覆盖一定宽度；参数为长度与宽度；源点默认不含
- 数值/公式: `length=specified; width=specified; source_excluded by default`
- 状态读取: aoe.length, aoe.width
- 状态变更: cells=line(source, direction, length, width)
- 出处: topics/玩家手册2024/术语汇编/效应区域.htm
- 待实现函数: lineCells(source, direction, length, width)->set
- 优先级: P1

### R-GLS-076 球状效应区域
- 摘要: 从源点向所有方向直线扩散形成球体；参数为半径；源点含于区域
- 数值/公式: `radius=specified; source_included=true`
- 状态读取: aoe.radius
- 状态变更: cells=sphere(source, radius)
- 出处: topics/玩家手册2024/术语汇编/效应区域.htm
- 待实现函数: sphereCells(source, radius)->set
- 优先级: P1

### R-GLS-077 攻击动作
- 摘要: 执行攻击动作可用武器/徒手打击进行攻击检定；每次攻击可装备/卸下武器；具备额外攻击特性可在攻击间移动
- 数值/公式: `action_cost=1 action; attacks=features-based; free equip/unequip per attack; move between attacks if Extra Attack`
- 状态读取: actor.features[extra_attack], actor.movement_remaining
- 状态变更: consume action; allow inter-attack movement
- 出处: topics/玩家手册2024/术语汇编/动作.htm
- 待实现函数: attackAction(actor)->void
- 优先级: P1

### R-GLS-078 疾走动作
- 摘要: 获得等于当前速度(调整后)的额外移动力；可用特殊速度替代
- 数值/公式: `bonus_movement=current_speed; usable with special speed chosen`
- 状态读取: actor.speed, actor.special_speeds
- 状态变更: actor.movement_remaining+=speed
- 出处: topics/玩家手册2024/术语汇编/动作.htm
- 待实现函数: dashBonus(actor, chosen_speed)->int
- 优先级: P1

### R-GLS-079 撤离动作
- 摘要: 当前回合剩余时间内移动不引发借机攻击
- 数值/公式: `action_cost=1; no_opportunity_attack=true(rest of turn)`
- 状态读取: actor.actions_used
- 状态变更: actor.disengaged=true
- 出处: topics/玩家手册2024/术语汇编/动作.htm
- 待实现函数: disengageAction(actor)->void
- 优先级: P1

### R-GLS-080 回避动作
- 摘要: 至下回合开始前以你为目标的攻击检定劣势(除非看不见攻击者)，你的敏捷豁免优势；失能或速度0则失去增益
- 数值/公式: `attacks_against_self→disadvantage(unless attacker unseen); dex_save→advantage; lost if incapacitated or speed==0`
- 状态读取: actor.conditions[incapacitated], actor.speed
- 状态变更: apply dodge modifiers
- 出处: topics/玩家手册2024/术语汇编/动作.htm
- 待实现函数: dodgeAction(actor)->void
- 优先级: P1

### R-GLS-081 协助动作
- 摘要: 辅助属性检定→盟友下次使用所选技能/工具的属性检定优势；辅助攻击检定→5尺内敌人，盟友下次对该敌人攻击检定优势
- 数值/公式: `assist_check→ally next check advantage; assist_attack→ally next attack vs enemy within 5ft advantage; until ally next turn start`
- 状态读取: ally.distance, enemy.distance
- 状态变更: ally.give_advantage(next check/attack)
- 出处: topics/玩家手册2024/术语汇编/动作.htm
- 待实现函数: helpAction(actor, target, type)->void
- 优先级: P2

### R-GLS-082 预备动作
- 摘要: 设定可感知触发事件，触发时用反应执行设定动作或移动=速度距离；预备法术需施法时间为动作且维持专注(至多到下回合开始)
- 数值/公式: `action_cost=1 action; reaction on trigger; ready_spell cast_time must be action; concentration until next turn start`
- 状态读取: actor.features, spell.cast_time
- 状态变更: queue reaction; set concentration
- 出处: topics/玩家手册2024/术语汇编/动作.htm
- 待实现函数: readyAction(actor, trigger, response)->void
- 优先级: P2

### R-GLS-083 附赠动作与反应上限
- 摘要: 每回合至多1个附赠动作(需规则提及)；反应每回合1次，用后至下回合开始不可再用；可在自己回合执行反应
- 数值/公式: `bonus_action_max=1/turn; reaction_max=1/round; reaction_refresh=own_turn_start`
- 状态读取: actor.bonus_action_used, actor.reaction_used
- 状态变更: consume resource
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: canTakeBonusAction(actor)->bool; canTakeReaction(actor)->bool
- 优先级: P1

### R-GLS-084 临时生命值
- 摘要: 由特定效应提供，作为抵御实际生命值损失的缓冲层
- 数值/公式: `temp_hp absorbed first; cannot exceed effect-defined max; not stackable(take higher)`
- 状态读取: actor.temp_hp, effect.temp_hp_granted
- 状态变更: actor.temp_hp=max(existing, new)
- 出处: topics/玩家手册2024/术语汇编/特殊能力词汇.htm
- 待实现函数: applyTempHP(actor, amount)->void
- 优先级: P1

### R-GLS-085 生命值边界
- 摘要: HP无法超出上限且无法低于0
- 数值/公式: `hp = clamp(hp, 0, max_hp)`
- 状态读取: actor.hp, actor.max_hp
- 状态变更: actor.hp=clamp(value, 0, max_hp)
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: clampHP(hp, max_hp)->int
- 优先级: P0

### R-GLS-086 数据卡固定值/掷骰表达式
- 摘要: 数据卡伤害同时给固定值与掷骰表达式(如4(1d4+2))，DM择一使用不可并用
- 数值/公式: `damage=fixed OR roll(expr); not both`
- 状态读取: stat_block.damage_notation
- 状态变更: choose mode
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: resolveStatBlockDamage(notation, mode)->int
- 优先级: P2

### R-GLS-087 每日次数恢复
- 摘要: "每日N次"用完后需完成长休才能再用
- 数值/公式: `uses_refresh=long_rest`
- 状态读取: feature.uses_remaining
- 状态变更: on long_rest: uses=max
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: refreshDailyUses(actor)->void
- 优先级: P2

---

## 待核实项汇总

前述板块标记"待核实"的项，经 R-GLS 板块补全后状态如下：

| 原标记项 | 状态 | 补全位置 |
|----------|------|----------|
| R-CON-003 状态条件数值效应 | ✅ 已补全 | R-GLS-044~058（14种状态完整效应） |
| R-DMG-021 危害公式 | ✅ 已补全 | R-GLS-059~063（燃烧/脱水/坠落/饥饿/窒息） |
| R-CON-006 特殊感官 | ✅ 已补全 | R-GLS-064~067（盲视/黑暗视觉/真实视觉/震颤感知） |
| R-DMG-024 物件破坏 | ✅ 已补全 | R-GLS-022~024（物件AC表/HP表/伤害免疫） |
| R-ITM-004 无甲基础AC | ✅ 已补全 | R-CMB-021 / R-GLS-006（10+敏捷调整值） |
| R-SPL-008 附赠动作施法限制 | ✅ 已由2024版规则覆盖 | R-SPL-007（每回合一法术位法术） |
| R-DM-016 浴血阈值 | ✅ 已补全 | hp≤max_hp/2（R-DMG-008 / R-GLS-021） |

**唯一保留的"设计性待定"**：感官作用半径（R-GLS-064~067/069）——原文称"特定范围"，**半径由各生物数据卡/法术单独给定，无通用固定数值**。实现时从生物 `senses` 字段读取具体半径，缺省视为无该感官。此为规则本身设计，非数据缺口。

## 优先级分布

| 优先级 | 含义 | 数量(约) | 说明 |
|--------|------|----------|------|
| P0 | 骰子引擎必需 | ~130 | d20/骰子/优劣势/熟练/属性调整/攻击命中/重击/伤害/抗性易伤免疫/HP/临时HP/死亡豁免/状态效应/掩护/AC计算/DC公式/专注/法术DC/物件AC/危害 |
| P1 | 判定模板 | ~140 | 各动作/战斗流程/先攻/移动/视野/施法各环节/旅行/装备 |
| P2 | 扩展规则 | ~94 | 骑乘细节/制作/生活开支/单位换算/随机表/升级变体等 |

> 精确数量可在代码实现阶段按 `grep -c "优先级: P0"` 等统计。P0 优先实现，构成骰子引擎核心；P1 构成判定模板；P2 按需补充。

## 函数索引（按功能分组）

> 写代码时按功能定位函数；写完在此回填实际模块路径，形成规则↔代码双向索引。

| 功能组 | 关键函数 | 对应规则ID |
|--------|----------|-----------|
| **骰子核心** | parse_and_roll_dice, roll_d20, roll_d100, roll_d3, roll_percent_chance, roll_random_table | R-CHK-025~030 |
| **D20检定** | d20_check, resolve_advantage, roll_d20(优劣势), reroll_one_die, heroic_inspiration_reroll | R-CHK-001~008, R-GLS-001 |
| **属性/熟练** | ability_modifier, proficiency_bonus, clamp_ability_score, apply_expertise, skill_ability_map, resolve_*_proficiency | R-CHK-015~024 |
| **检定类型** | ability_check, saving_throw, attack_check, passive_check, group_check | R-CHK-010~014, R-DM-011~012 |
| **DC设定** | dc_by_label, calc_save_dc, clamp_save_dc, compute_spell_save_dc, compute_spell_attack_bonus | R-CHK-009/012, R-DM-001~003, R-SPL-021~022 |
| **攻击命中** | attack_roll, check_natural_20/1, get_attack_ability, resolve_finesse_mod, apply_proficiency, compute_ac, apply_cover, resolve_visibility_modifiers | R-CMB-014~023, R-GLS-006/007 |
| **重击** | isCriticalHit, crit_damage_roll, rollCriticalDamage, isAutoCrit | R-CMB-029, R-GLS-002 |
| **伤害** | compute_damage_roll, apply_damage_floor, resolve_damage_pipeline, apply_resistance_vulnerability, apply_immunity, applyDamageThreshold | R-DMG-001~006, R-GLS-003/004 |
| **HP/治疗** | subtract_hp, apply_damage_with_temp_hp, grant_temp_hp, apply_healing, check_bloodied, clampHP, check_massive_damage, death_save_throw, damage_at_zero_hp, stabilize_check | R-DMG-007~020, R-GLS-085 |
| **状态条件** | addCondition, applyBlinded/Charmed/Deafened/Exhaustion/Frightened/Grappled/Incapacitated/Invisible/Paralyzed/Petrified/Poisoned/Prone/Restrained/Stunned/Unconscious, escapeGrapple | R-GLS-043~058 |
| **战斗流程** | roll_initiative, start_turn, advance_round, action_dash/disengage/dodge/hide | R-CMB-001~013, R-GLS-077~080 |
| **移动** | move, move_cost, speed_to_squares, enter_square, drop_prone, difficultTerrainCost, climbCost, longJumpDist, highJumpHeight, switchSpeedRemaining | R-CMB-030~039, R-GLS-026~033 |
| **借机/掩护/视野** | opportunity_attack, canOpportunityAttack, apply_cover, cover_level, has_line_of_sight, lightObscurement | R-CMB-015/025/026, R-DM-021/022, R-GLS-068 |
| **感官** | blindsightCanSee, darkvisionLightLevel, truesightCapabilities, tremorsenseCanDetect, canEstablishTelepathy | R-GLS-064~069 |
| **施法** | consumeSpellSlot, upcastSpell, castAsRitual, canCastByComponents, setConcentration, concentrationSaveOnDamage, computeSpellSaveDC, buildAoE, computeAoEBlockedPoints | R-SPL-001~036, R-GLS-013/040 |
| **效应区域** | coneCells, cubeCells, cylinderCells, emanationCells, lineCells, sphereCells, aoeAffectedCells | R-GLS-070~076 |
| **装备数据** | get_armor_entry, compute_ac, get_weapon_entry, resolve_property, apply_mastery, convert_coins, get_gear_entry | R-ITM-001~042 |
| **危害** | burningDamage, fallDamage, dailyWaterNeed, dailyFoodNeed, breathHoldDuration, applyDehydration/Starvation/Suffocation | R-GLS-059~063 |
| **物件** | objectAC, objectHP, defaultObjectImmunities, break_object | R-GLS-022~024, R-DMG-024 |
| **旅行/DM** | travel_distance, terrain_params, forage, navigation, weather_roll, award_xp | R-DM-030~045, R-CON-008~011 |

---

## 10. 审计补遗（R-ADD，经7组并行审计复核源文后补充）

> 以下为通读全部源文逐条比对后发现的遗漏规则，已确认存在于源文但原9板块未覆盖或仅部分覆盖。编号 R-ADD-001 起，按优先级与板块归属排列。

### R-ADD-001 交流免费（R-CMB补遗）
- 摘要: 回合内可免费交流（简短说话/手势），不耗动作/移动力；说更多话或影响动作需动作
- 数值/公式: `free_communication=true（不耗action/move）; long_speech_or_influence → requires action`
- 出处: topics/玩家手册2024/进行游戏/战斗流程.htm
- 待实现函数: communicate(actor, content)->requires_action
- 优先级: P1

### R-ADD-002 动作:魔法（R-CMB补遗）
- 摘要: 魔法动作用于施展法术/使用魔法物品/使用魔法特性
- 数值/公式: `action_cost=1 action; 施法时间须为1动作（详见R-SPL-006）`
- 出处: topics/玩家手册2024/进行游戏/动作.htm
- 待实现函数: action_magic(actor)->void
- 优先级: P1

### R-ADD-003 动作:操作（R-CMB补遗）
- 摘要: 操作动作用于使用一个非魔法物件
- 数值/公式: `action_cost=1 action; 作用于一个非魔法物件；魔法/特殊物品见其描述`
- 出处: topics/玩家手册2024/进行游戏/动作.htm
- 待实现函数: action_utilize(actor, object)->void
- 优先级: P1

### R-ADD-004 掩护来源侧前置（R-CMB补遗）
- 摘要: 只有攻击/效应来源位于掩护另一侧时，目标才获掩护增益
- 数值/公式: `cover_active_only_if: source_on_opposite_side_of_cover_from_target; 否则 cover_bonus=0`
- 出处: topics/玩家手册2024/进行游戏/发动攻击.htm
- 待实现函数: cover_active(source, target, cover)->bool（补充R-CMB-015）
- 优先级: P0

### R-ADD-005 反应后回合继续（R-CMB补遗）
- 摘要: 反应发生在他人回合中，被中断者在该反应结束后立刻继续自己的回合
- 数值/公式: `on_reaction_in_other_turn: interrupted_creature_resumes_turn_immediately_after_reaction_resolves`
- 出处: topics/玩家手册2024/进行游戏/反应.htm
- 待实现函数: resume_after_reaction(interrupted_creature)（补充R-CMB-013）
- 优先级: P1

### R-ADD-006 拆分移动跨附赠动作/反应（R-CMB补遗）
- 摘要: 移动可拆分到动作、附赠动作、反应的前后
- 数值/公式: `can_interleave_with=[action, bonus_action, reaction]`（补充R-CMB-030，原仅含动作）
- 出处: topics/玩家手册2024/进行游戏/移动和位置.htm
- 待实现函数: move_split(actor, segments)（补充R-CMB-030）
- 优先级: P0

### R-ADD-007 借机攻击时机（R-CMB补遗）
- 摘要: 借机攻击发生于目标离开触及范围**前**的那一刻
- 数值/公式: `timing=resolves_at_moment_before_target_exits_reach`（补充R-CMB-025）
- 出处: topics/玩家手册2024/进行游戏/近战攻击.htm
- 待实现函数: opportunity_attack_timing()（补充R-CMB-025）
- 优先级: P0

### R-ADD-008 死亡豁免计数受治疗归零（R-DMG补遗）
- 摘要: 伤势稳定**或恢复任意生命值（含他人治疗）**时，死亡豁免成功/失败计数都归零
- 数值/公式: `on_any_hp_recovery(包括他人治疗): death_successes=0, death_failures=0, remove unconscious`（补充R-DMG-017）
- 出处: topics/玩家手册2024/进行游戏/生命值降至0点.htm
- 待实现函数: reset_death_counts_on_hp_recovery(creature)（补充R-DMG-017）
- 优先级: P0

### R-ADD-009 受控坐骑受训前置（R-CMB补遗）
- 摘要: 只能控制受训且接纳骑手的坐骑（驯养马/骡等）
- 数值/公式: `controlled_mount_requires: mount.is_trained AND mount.accepts_rider; 否则只能自主坐骑`（补充R-CMB-045）
- 出处: topics/玩家手册2024/进行游戏/骑乘战斗.htm
- 待实现函数: can_control_mount(rider, mount)->bool（补充R-CMB-045）
- 优先级: P1

### R-ADD-010 擒抱部位限制（R-GLS补遗）
- 摘要: 擒抱需一只空手；每只手/部位同时只能擒抱一个生物；擒抱者可随时免费释放
- 数值/公式: `grapple_requires_free_hand=true; one_grapple_per_hand_or_limbslot=true; grappler可no-action释放`
- 出处: topics/玩家手册2024/术语汇编/武器与徒手打击.htm + 常见规则词汇.htm
- 待实现函数: grapple_capacity(grappler)->max_count; release_grapple(grappler, target)->void
- 优先级: P0

### R-ADD-011 推撞结果（R-GLS补遗）
- 摘要: 徒手打击推撞成功时，攻击者选择推开5尺或使其倒地；体型至多比攻击者大一级
- 数值/公式: `shove_outcome∈{push_5ft, prone}（attacker选）; shove_size_limit=attacker_size+1`（补充R-GLS-034）
- 出处: topics/玩家手册2024/术语汇编/武器与徒手打击.htm
- 待实现函数: resolve_shove(attacker, target)->outcome（补充R-GLS-034）
- 优先级: P0

### R-ADD-012 躲藏结束触发（R-GLS补遗）
- 摘要: 4种情况结束躲藏：发出高于低语的响声/被敌人找到/进行攻击检定/施展带言语成分法术
- 数值/公式: `hide_ends_if: noise>whisper OR found_by_enemy OR make_attack_roll OR cast_spell_with_verbal_component`
- 出处: topics/玩家手册2024/术语汇编/动作.htm
- 待实现函数: end_hide_triggers(actor)->void（补充R-GLS-018）
- 优先级: P0

### R-ADD-013 躲藏成功→隐形状态（R-GLS补遗）
- 摘要: 躲藏检定成功，躲藏期间处于隐形(invisible)状态
- 数值/公式: `hide_success → add_condition(invisible)`（修订R-GLS-018/R-CMB-009，原用HIDDEN非标准状态名）
- 出处: topics/玩家手册2024/术语汇编/动作.htm
- 待实现函数: on_hide_success(actor)（补充R-GLS-018）
- 优先级: P0

### R-ADD-014 影响动作三分支流程（R-GLS补遗）
- 摘要: 影响怪物按其意愿分三分支：愿意→不需检定直接执行；不愿意（有悖阵营）→不需检定直接拒绝；犹豫不决→属性检定
- 数值/公式: `willing→no_check,act; unwilling→no_check,refuse; hesitant→check vs dc=max(15,int_score)`（补充R-GLS-016）
- 出处: topics/玩家手册2024/术语汇编/动作.htm
- 待实现函数: influence_branch(creature, request)->("act"|"refuse"|"check")（补充R-GLS-016）
- 优先级: P1

### R-ADD-015 长休打断与部分休整（R-GLS补遗）
- 摘要: 长休打断原因4项（掷先攻/施非戏法法术/受伤害/1小时体力劳动）；打断前已休≥1h可获短休增益；每打断一次需+1h完成
- 数值/公式: `interrupts={roll_initiative, cast_non_cantrip_spell, take_damage, 1hr_travel_or_labor}; if rested>=1hr before_interrupt→grant_short_rest_benefit; completion_extra_hours+=1 per_interrupt`（补充R-GLS-015）
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: long_rest_interrupt(actor, cause)（补充R-GLS-015）
- 优先级: P1

### R-ADD-016 长休恢复HP上限（R-GLS补遗）
- 摘要: 长休恢复全部HP，若HP上限被减少则恢复原状
- 数值/公式: `if max_hp_reduced: max_hp=base_max_hp`（补充R-GLS-015）
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: restore_max_hp(actor)（补充R-GLS-015）
- 优先级: P1

### R-ADD-017 短休特性恢复钩子（R-GLS补遗）
- 摘要: 部分特性在短休完成时恢复使用次数（按各自描述）
- 数值/公式: `features_with_recharge_on_short_rest → uses=max（按各自描述）`
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: recharge_features_on_short_rest(actor)
- 优先级: P1

### R-ADD-018 击晕恢复HP脱昏迷（R-GLS补遗）
- 摘要: 被击晕生物恢复任意HP即脱离昏迷（除DC10医药检定外）
- 数值/公式: `unconscious_ends_if: regain_any_hp OR stabilize_check(wis_medicine, dc=10) success`（补充R-GLS-019）
- 出处: topics/玩家手册2024/术语汇编/武器与徒手打击.htm
- 待实现函数: end_knockout_unconscious(creature)（补充R-GLS-019）
- 优先级: P1

### R-ADD-019 困难地形触发清单（R-GLS补遗）
- 摘要: 困难地形判定清单：非微型非盟友生物/体型相仿或更大的家具/厚积雪冰面砂石茂密植被/及胫到及腰液体/窄路缝隙/坡度>20°陡坡
- 数值/公式: `is_difficult_triggers=[non-tiny_non-ally_creature, furniture>=self_size, deep_liquid_shin-to-waist, narrow_passage(<self_size-1), slope>20°, thick_snow_ice_sand_dense_veg]`（补充R-GLS-026）
- 出处: topics/玩家手册2024/术语汇编/移动与速度.htm
- 待实现函数: is_difficult_terrain(tile, mover)->bool（补充R-GLS-026）
- 优先级: P1

### R-ADD-020 同时效应排序（R-GLS补遗）
- 摘要: 同一回合中两起以上事件同时发生时，由轮到回合者（玩家或DM）决定顺序
- 数值/公式: `if multiple_effects simultaneous in a turn → controller_of_turn(actor/DM) chooses order`
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: resolve_simultaneous_effects(effects, turn_controller)->ordered
- 优先级: P1

### R-ADD-021 英雄激励转赠队友（R-GLS/R-CHK补遗）
- 摘要: 已有英雄激励时又获得一个，可转赠小队中无激励的玩家角色；否则浪费
- 数值/公式: `if has_heroic_inspiration==1 and gains: may_transfer to allied_pc where target.has==0 → target.has=1; 否则 wasted`（补充R-CHK-007/R-GLS-041）
- 出处: topics/玩家手册2024/术语汇编/特殊能力词汇.htm + 优势_劣势.htm
- 待实现函数: transfer_inspiration(actor, ally_pc)->bool
- 优先级: P2

### R-ADD-022 传送触碰生物不随行（R-GLS补遗）
- 摘要: 传送时触碰着的生物默认不随传送，除非法术声明例外
- 数值/公式: `touched_creature_not_transported unless effect_excepts`（补充R-GLS-038）
- 出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
- 待实现函数: teleport_carried_creatures(spell, actor)（补充R-GLS-038）
- 优先级: P1

### R-ADD-023 缺席玩家XP补偿（R-DM补遗）
- 摘要: 给予缺席玩家与其他玩家每回相等XP，保持同等级
- 数值/公式: `absent_player_xp = xp_per_member_awarded_this_session`
- 出处: topics/城主指南2024/2.运作游戏/团队规模.htm
- 待实现函数: award_absent_xp(absent_players, xp_per_member)
- 优先级: P2

### R-ADD-024 非战斗挑战XP（R-DM补遗）
- 摘要: 非战斗挑战按遭遇难度折算同难度战斗XP发放
- 数值/公式: `noncombat_xp = difficulty_equivalent_encounter_xp(difficulty)`
- 出处: topics/城主指南2024/2.运作游戏/角色升级.htm
- 待实现函数: award_noncombat_xp(party, difficulty)
- 优先级: P2

### R-ADD-025 引发战斗者先攻优势（R-DM补遗）
- 摘要: 因角色动作引发战斗时，给予该角色先攻检定优势
- 数值/公式: `if action_triggered_combat(actor): actor.initiative_advantage=True`
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/投掷先政.htm
- 待实现函数: grant_initiative_advantage_on_trigger(actor)（补充R-DM-013）
- 优先级: P1

### R-ADD-026 DM授予英雄激励（R-DM/R-CHK补遗）
- 摘要: 玩家行为有趣/刺激/难忘或良好角色扮演时，DM可授予英雄激励（受上限1约束）
- 数值/公式: `grant_heroic_inspiration(actor, reason) if has_heroic_inspiration<1`
- 出处: topics/城主指南2024/2.运作游戏/运作战斗/战斗中的叙述.htm
- 待实现函数: dm_grant_inspiration(actor, reason)
- 优先级: P2

### R-ADD-027 飞行/无视困难地形可快速步调（R-DM补遗）
- 摘要: 飞行或特殊移动无视困难地形者，无论地形如何都可用快速步调
- 数值/公式: `if can_fly_or_ignore_difficult_terrain(actor): party_max_pace="fast"`（补充R-DM-032/033）
- 出处: topics/城主指南2024/2.运作游戏/运作探索/旅行.htm
- 待实现函数: override_pace_for_flyer(actor, terrain)（补充R-DM-033）
- 优先级: P1

### R-ADD-028 再次尝试失败检定1分钟（R-DM补遗）
- 摘要: 失败可再尝试，每次约1分钟（如撬锁）；若失败无后果且可反复尝试可跳过检定直接报时间
- 数值/公式: `retry_time(task)=1 minute(示例:撬锁); if no_failure_consequence: skip_check_and_report_time`
- 出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/属性检定.htm
- 待实现函数: retry_check_time(task)->minutes
- 优先级: P2

### R-ADD-029 D20检定必要性判定框架（R-DM补遗）
- 摘要: 目标太琐碎或不可能则不必检定；D20检定仅当成功/失败可能并存且失败有有意义后果时进行；积极尝试→属性检定，被动抵抗→豁免检定
- 数值/公式: `should_call_d20_check(task)->bool; classify(task)->"ability"|"save"|"attack"`
- 出处: topics/城主指南2024/2.运作游戏/决定掷骰结果/决定掷骰结果.htm
- 待实现函数: should_check(task)->bool; classify_test(task)->str
- 优先级: P2

### R-ADD-030 水下远程常规射程内劣势（R-QCK补遗）
- 摘要: 水下远程攻击超常规射程自动失手；常规射程内仍劣势，除非武器为弩/捕网/标枪类投掷（矛/三叉戟/飞镖）
- 数值/公式: `RANGED_DISADV_WEAPONS_EXEMPT={弩,捕网,标枪类投掷(矛,三叉戟,飞镖)}; 常规射程内→劣势(除非豁免); 超常规→auto_miss`（补充R-QCK-014/R-CMB-041）
- 出处: topics/速查/DM速查/水下战斗.htm
- 待实现函数: underwater_ranged_full(weapon, distance)->(can_hit, advantage)（补充R-QCK-014）
- 优先级: P1

### R-ADD-031 坠落飞行者半速解除倒地（R-QCK补遗）
- 摘要: 使用坠落速度规则时，飞行生物后续回合仍坠落且倒地，可花一半飞行速度解除倒地并终止坠落
- 数值/公式: `when_using_fall_rate_rule AND prone AND still_falling AND subsequent_round: 花费 floor(fly_speed/2) → 解除倒地+终止坠落`（补充R-QCK-008）
- 出处: topics/速查/DM速查/坠落.htm
- 待实现函数: flyer_recover_from_fall(actor)（补充R-QCK-008）
- 优先级: P1

### R-ADD-032 骑乘坐骑倒地反应下马（R-QCK补遗，2014版）
- 摘要: 坐骑应击倒地时，骑手可用反应立刻下马并安全着地；否则骑乘结束并在坐骑5尺内倒地
- 数值/公式: `trigger: mount_prone; rider可 Reaction 下马 safe_landing(prone=false); 不反应→骑乘结束+5尺内倒地`（注:2024版见R-CMB-046用DC10豁免，此为2014版机制，待核实取版）
- 出处: topics/速查/DM速查/骑乘战斗.htm（2014源）
- 待实现函数: mount_prone_reaction(rider, mount)（补充R-QCK-015）
- 优先级: P2

### R-ADD-033 冒险物品效果规则集（R-ITM补遗）
- 摘要: 多件含判定DC/机制的冒险物品（原R-ITM-042仅列价格）
- 数值/公式:
```python
ITEM_EFFECTS={
  "抗毒剂":{"price":"50GP","action":"附赠动作","effect":"中毒豁免优势1小时","excludes":["不死","构装"]},
  "链条":{"bind":"DC13 STR(运动)","escape":"DC18 DEX(特技)","break":"DC20 STR(运动)","action":"操作动作","hp":10},
  "医疗包":{"price":"5GP","uses":10,"action":"操作动作","effect":"稳定0HP生物,跳过DC10医药检定"},
  "捕猎陷阱":{"save":"DEX DC13","dmg":"1d4穿刺","effect":"速度0至下回合","escape":"DC13 STR(运动)","fail_dmg":"1穿刺"},
  "锁":{"pick":"DC15 DEX(巧手,需盗贼工具)"},
  "镣铐":{"bind":"DC13 DEX(巧手)","escape":"DC20 DEX(巧手)","break":"DC25 STR(运动)","pick":"DC15 DEX(巧手)","effect":"被铐者攻击劣势"},
  "绳索":{"knot":"DC10 DEX(巧手)","break":"DC20 STR(运动)","bind_escape":"DC15 DEX(特技)","hp":2},
  "爪钩":{"range":50,"check":"DC13 DEX(特技)"},
  "便携式攻城锤":{"str_bonus":"+4","assist":"优势"},
  "法术卷轴使用":{"requires":"法术在职业列表","material":"无需","save_dc":13,"attack_bonus":5,"destroyed_on_cast":True},
  "圣水创造仪式":{"caster":"牧师/圣武士","time":"1小时","cost":"25GP银粉","slot":"1环法术位"},
  "燃油":{"fuel_duration":"6小时(油灯/提灯)"},
  "书籍":{"skills":["奥秘","历史","自然","宗教"],"bonus":"+5","cond":"参考准确非虚构书"},
  "地图":{"skill":"求生","bonus":"+5","cond":"参考准确地图"},
  "火把":{"bright":20,"dim":20,"duration":"1小时","melee_dmg":"1火焰"},
  "蜡烛":{"bright":5,"dim":5,"duration":"1小时"},
  "油灯":{"bright":15,"dim":30,"fuel":"6小时/品脱"},
  "牛眼提灯":{"bright":60,"dim":60,"shape":"锥","fuel":"6小时/品脱"},
  "附盖提灯":{"bright":30,"dim":30,"fuel":"6小时/品脱","cover_action":"附赠动作→5尺微光"},
}
```
- 出处: topics/玩家手册2024/装备/冒险装备.htm + topics/速查/DM速查/物品表.htm
- 待实现函数: get_item_effect(item_id)->dict（扩充R-ITM-042）
- 优先级: P1

### R-ADD-034 魔法物品施法（R-SPL补遗）
- 摘要: 法术卷轴等魔法物品可无需法术位施法，次数由物品描述给定
- 数值/公式: `castFromMagicItem(item, spell): casterSlotCost=0; item.spellUsesPerDay=specified; onCast: item.uses-=1`
- 出处: topics/玩家手册2024/法术/法术环阶.htm + 获得法术.htm
- 待实现函数: cast_from_magic_item(caster, item, spell)->bool
- 优先级: P1

### R-ADD-035 特殊能力施法（R-SPL补遗）
- 摘要: 角色/怪物特殊能力可无需法术位施法，通常每日有限次数
- 数值/公式: `castBySpecialAbility(feature, spell): casterSlotCost=0; feature.usesPerDay=specified; onCast: feature.uses-=1`
- 出处: topics/玩家手册2024/法术/法术环阶.htm
- 待实现函数: cast_by_special_ability(caster, feature, spell)->bool
- 优先级: P2

### R-ADD-036 DM裁定专注干扰（R-SPL补遗）
- 摘要: DM可对特定情况（如暴风/巨浪击退）要求体质豁免维持专注，示例DC10
- 数值/公式: `concentrationInterruptFactors += {DM_DISCRETIONARY: save=CON, dc=10(示例,DM定), trigger=DM指定}`（补充R-SPL-019）
- 出处: topics/速查/DM速查/施法.htm
- 待实现函数: concentration_dm_discretion(caster, situation, dc=10)（补充R-SPL-019）
- 优先级: P2

---

## 待补清单（P2/P3，后续按需回填为正式规则点）

> 以下为审计发现但优先级较低的遗漏/数据回填项，集中列出待后续补全。

- **枚举表**：伤害类型13种（强酸/钝击/寒冷/火焰/力场/闪电/暗蚀/穿刺/毒素/心灵/光耀/挥砍/雷鸣）；生物类型14种（异怪/野兽/天族/构装/龙类/元素/妖精/巨人/类人/怪兽/泥怪/植物/亡灵/邪魔）；阵营9种（道德{善良/邪恶/中立}×秩序{守序/混乱/中立}）
- **R-ITM存根数据回填**：R-ITM-028工匠工具17件（炼金/酿酒/书法/木匠/制图/鞋匠/厨师/玻璃匠/珠宝匠/皮匠/石匠/画家/陶匠/铁匠/修补/织布/木雕，各含属性/重量/价格/操作DC/可造物品）；R-ITM-029其他工具8件（含赌具4变体/乐器10变体）；R-ITM-031陆运载具10行表+鞍座3类；R-ITM-032大型载具7船完整数据（飞艇/桨帆船/单帆长船/战舰/帆船/划艇/龙骨船）+顺流加速/吊床5SP/船舱2GP等规则；R-ITM-035饮食价目表（麦酒4CP/面包2CP/奶酪1SP+旅馆/食膳按生活方式6档）；R-ITM-042容器容量表（篮子40磅/2立方尺/吊桶半立方尺/玻璃瓶1.5品脱/扁瓶1品脱/壶1加仑/箱子12立方尺等）+套组7套价格内容
- **R-QCK数据回填**：R-QCK-013陷阱11范例实际数值（塌方/落网/喷火雕像/普通陷坑/隐蔽陷坑/锁困陷坑/尖刺陷坑/毒镖/毒针/滚石/湮灭法球，各spot_dc/disarm_dc/save_dc/damage）；R-QCK-019毒药14范例效应（刺客之血/焦引熏烟/卓尔毒药/紫虫毒液/苍白酊剂等，各save_dc/伤害/状态/持续时间）；R-QCK-017吸入毒药5立方尺作用范围
- **版本差异（2014 vs 2024）**：R-ITM-021消耗品2014机制（强酸/炽火胶/圣水/燃油/捕网2014均为远程攻击检定非豁免；圣水2014=2d6光耀 vs 2024=2d8）；R-ITM-022滚珠/铁蒺藜2014半速穿过免豁免+铁蒺藜速度-10至恢复1HP；R-ITM-017武器2014差异（三叉戟1d6/两用1d8、战镐无多用、火器为2024新增、捕网特殊规则、骑枪5尺内劣势）；R-ITM-042 2014独有物品17项（算盘/岩钉/丝绳/法术书等）
- **R-SPL次要**：法术位进度表（每职业每等级各环阶法术位数量，如法师3级=4×1环+2×2环）；9环需≥17级；立即法术后事不可解除；效应混合被抑制者较强者结束后恢复；法器须施法全程握持；戏法无需预先准备；怪物不可改准备列表(DM可改)
- **R-DM次要**：里程碑资源奖励变体（短休效益/恢复1生命骰/恢复1环法术位/重充魔法物品次数）；属性/豁免天然20/1可选大成功/大失败变体；中间DC取值（17/18夹值）；远距离无网格范围计数骰子法（百分骰/d20×5或10尺）；成功程度箭术靶分环示例数值；追踪检定优劣势触发/重投触发；极地地形保持快速步调需装备
- **R-QCK次要**：休整期专业实践（维持俭朴免1gp/有组织→舒适/有表演熟练→富裕）；休整期制作生活费用减免（俭朴免费或舒适半价）；单位转换反向换算
- **R-GLS次要**：诅咒移除法术（移除诅咒/高等复原术）；变形效应携带/死亡还原真形；附身防范(防护善恶)/终止(反制善恶)；同时效应排序（见R-ADD-020，已升P1）



## 实现回填区（代码写完后在此记录实际模块/函数位置）

```
# === engine/dice.py（已完成，自检通过）===
aidm/engine/dice.py :: roll_die(sides) -> int                    # R-CHK-025 骰子基础(1dM)  topics/玩家手册2024/进行游戏/骰子.htm
aidm/engine/dice.py :: parse_dice_expression(expr) -> (terms, const)  # R-CHK-025 NdM+K表达式解析
aidm/engine/dice.py :: roll_dice(expr, *, crit=False) -> RollResult  # R-CHK-025 掷骰; crit→R-CMB-029重击骰翻倍  重击.htm
aidm/engine/dice.py :: roll_d20(advantage, disadvantage) -> D20Roll  # R-CHK-004优劣势掷骰 + R-CHK-005抵消  优势_劣势.htm
aidm/engine/dice.py :: roll_d100() -> int                       # R-CHK-026 百分骰(两骰皆0=100)  骰子.htm
aidm/engine/dice.py :: roll_d3() -> int                        # R-CHK-027 d3=ceil(d6/2)  骰子.htm
aidm/engine/dice.py :: roll_percent_chance(percent) -> (bool,int) # R-CHK-029 百分比概率  骰子.htm
aidm/engine/dice.py :: roll_random_table(table, die) -> (value,int) # R-CHK-030 随机表查表  骰子.htm
aidm/engine/dice.py :: ability_modifier(score) -> int           # R-CHK-024 属性调整值 floor((score-10)/2)  六项属性.htm
aidm/engine/dice.py :: proficiency_bonus(level_or_cr) -> int   # R-CHK-015 熟练加值表(1-4:+2…29-30:+9)  熟练.htm
aidm/engine/dice.py :: round_down(value) -> int                 # R-GLS-005 向下取整  术语汇编/常见规则词汇.htm

# === engine/check.py（已完成，自检通过）===
aidm/engine/check.py :: dc_by_label(label) -> int               # R-CHK-009 范例DC表  属性检定.htm
aidm/engine/check.py :: calc_save_dc(ability_mod, prof) -> int  # R-DM-002 计算DC公式(8+属性+熟练)  难度等级.htm
aidm/engine/check.py :: resolve_advantage(adv_count, dis_count) -> (bool,bool)  # R-CHK-005/R-DM-006 优劣势抵消  优势_劣势.htm
aidm/engine/check.py :: passive_check(modifiers) -> int          # R-DM-012 被动检定(10+调整值)  属性检定.htm
aidm/engine/check.py :: ability_check(mod,prof,proficient,dc,adv,dis) -> CheckResult  # R-CHK-010 属性检定  属性检定.htm
aidm/engine/check.py :: saving_throw(mod,prof,proficient,dc,adv,dis,waive) -> CheckResult  # R-CHK-011 豁免(可放弃)  豁免检定.htm
aidm/engine/check.py :: attack_roll(bonus,ac,adv,dis) -> AttackResult  # R-CMB-017命中 + R-CMB-022天然20重击 + R-CMB-023天然1失手  攻击检定.htm
aidm/engine/check.py :: is_natural_20/is_natural_1 -> bool      # R-CMB-022/023  攻击检定.htm

# === engine/damage.py（已完成，自检通过）===
aidm/engine/damage.py :: apply_damage_pipeline(raw,type,mods,resist,vuln,immune)->DamageResult  # R-QCK-002/R-DMG-003~006 顺序管线(免疫→mods→抗性→易伤)  抗性和易伤.htm
aidm/engine/damage.py :: roll_damage(req,resist,vuln,immune)->DamageResult  # R-DMG-001伤害掷骰 + R-CMB-029重击骰翻倍  伤害掷骰.htm
aidm/engine/damage.py :: resolve_stat_block(notation,mode)->int  # R-GLS-086 数据卡固定值/掷骰  常见规则词汇.htm
aidm/engine/damage.py :: apply_damage_to_hp(hp,temp,max,dmg)->(hp,temp)  # R-DMG-009临时HP优先 + R-DMG-007/R-GLS-085 HP扣除  临时生命值.htm
aidm/engine/damage.py :: grant_temp_hp(cur,new)->int  # R-DMG-010 临时HP不叠加(取大)  临时生命值.htm
aidm/engine/damage.py :: apply_healing(hp,max,heal)->int  # R-DMG-020 治疗(不超上限)  治疗.htm
aidm/engine/damage.py :: check_massive_damage(cur,max,dmg)->bool  # R-DMG-014 过量伤害致死  生命值降至0点.htm
aidm/engine/damage.py :: death_save(tracker)->dict  # R-DMG-017 死亡豁免(1d20≥10/3成功稳定/3失败死亡/天然1双败/天然20恢复1HP)  生命值降至0点.htm
aidm/engine/damage.py :: damage_at_zero_hp(tracker,dmg,crit,max)->dict  # R-DMG-018 0血受伤害(重击双败)  生命值降至0点.htm
aidm/engine/damage.py :: reset_death_counts_on_recovery(tracker)  # R-ADD-008 受治疗计数归零  生命值降至0点.htm

# === engine/conditions.py（已完成，自检通过）===
aidm/engine/conditions.py :: ConditionState.add/remove/has  # R-GLS-043 状态不叠加(力竭例外)  状态与其他游戏状况.htm
aidm/engine/conditions.py :: ConditionState.is_incapacitated  # R-GLS-050 失能(含麻痹/震慑/昏迷/石化)  状态.htm
aidm/engine/conditions.py :: d20_penalty(state)->int  # R-GLS-047 力竭 D20−(级×2)  状态.htm
aidm/engine/conditions.py :: speed_after_conditions(base,state)->int  # R-GLS-049/052/053/056/058 速度归0 + R-GLS-047 力竭−级×5  状态.htm
aidm/engine/conditions.py :: attack_modifiers(atk,tgt,dist)->AttackModifiers  # R-GLS-044~058 攻防优劣势/自动重击(麻痹昏迷5尺内)  状态.htm
aidm/engine/conditions.py :: concentration_broken_on_state_change  # R-GLS-050/R-SPL-019 失能打断专注  状态.htm

# === data/equipment.py（已完成，自检通过）===
aidm/data/equipment.py :: ARMOR(13套+盾)/WEAPONS(38件)/PROPERTIES(10)/MASTERY(8)  # R-ITM-003/012/014/015  护甲.htm/武器.htm/词条.htm/精通词条.htm
aidm/data/equipment.py :: compute_ac(armor,dex,shield)->int  # R-ITM-004 AC公式(full/cap2/none/bonus)  护甲.htm
aidm/data/equipment.py :: compute_unarmored_ac(dex)->int  # R-CMB-021/R-GLS-006 无甲=10+dex  攻击检定.htm
aidm/data/equipment.py :: armor_str_penalty/armor_stealth_disadv  # R-ITM-005/006 力量不足-10尺/隐匿劣势  护甲.htm
aidm/data/equipment.py :: convert_coins(amt,frm,to)->float  # R-ITM-001 钱币换算  钱币.htm

# === engine/combat.py（已完成，自检通过）===
aidm/engine/combat.py :: roll_initiative(combatants)->order  # R-CMB-002 先政(d20+dex,突袭劣势) + R-GLS-009  战斗流程.htm
aidm/engine/combat.py :: start_combat/advance_turn/current_combatant  # R-CMB-001一轮6秒 + R-CMB-004回合动作经济  战斗流程.htm
aidm/engine/combat.py :: can_take_action/bonus/reaction, use_*  # R-CMB-011/012/013 + R-GLS-083 动作经济  动作.htm/附赠动作.htm/反应.htm
aidm/engine/combat.py :: concentration_save_dc(dmg)->int  # R-GLS-013 专注DC=max(10,dmg/2)上限30  常见规则词汇.htm
aidm/engine/combat.py :: concentration_save(con_mod,con_prof,prof,dmg)->bool  # R-GLS-013/R-SPL-020 受伤体质豁免维持  常见规则词汇.htm

# === stats/models.py + stats/store.py（已完成，自检通过，P1状态层）===
aidm/stats/models.py :: Character(SQLModel)  # R-DMG-007/009/017 角色卡(HP/临时HP/死亡计数) + engine桥接(ability_mod/prof/to_condition_state/to_death_tracker)  数据模型§6
aidm/stats/models.py :: Campaign/Scene/CombatState/Log  # rolling_summary(防失忆)/场景/战斗状态/日志  数据模型§6
aidm/stats/store.py :: save_character/get_character/list_characters  # 角色卡CRUD
aidm/stats/store.py :: create_campaign/append_summary/get_summary  # 战役 + rolling summary(P3 LLM压缩钩子)
aidm/stats/store.py :: save_combat/load_combat  # engine.Combat↔CombatState 往返(先政/轮次/参战者)
aidm/stats/store.py :: append_log  # 完整跑团日志(玩家输入/AI回复/骰子/状态变更/RAG引用)

# === P0+P1 联调验证 ===
# 全栈: 建角色卡→equipment.compute_ac算AC→check.attack_roll命中→damage.roll_damage+apply_damage_to_hp伤害→conditions.attack_modifiers状态优劣势→stats存档→重载  全部跑通

# === P2 知识层（已完成，三语料RAG+LLM联调通过）===
aidm/config.py :: Settings(get_settings)  # .env读取(LLM key/base_url/model + embedding + qdrant)
aidm/knowledge/embedding.py :: embed_texts/embed_query/get_embedder  # 本地bge嵌入(默认bge-small-zh-v1.5,可切bge-m3) + HF镜像 + 可选HTTP服务
aidm/knowledge/parse_datajs.py :: parse_datajs(path)->[RuleEntry]  # data.js→6238条数据语料(怪物/物品/法术)
aidm/knowledge/parse_rulespec.py :: parse_rulespec()->[dict]  # RULE_SPEC.md→400条结构化规则点(校验语料,最高信号)
aidm/knowledge/indexer.py :: build_index/index_text_files/index_chunks/search/search_rules/search_spec  # 本地Qdrant(文件模式免docker) 三语料
aidm/knowledge/retriever.py :: query_rules/query_formatted  # 检索+格式化给LLM
aidm/knowledge/verifier.py :: verify(action,check_type,dc)->Verification  # 判定校验(检索证据+关键词预检,语义校验留P3)
aidm/brain/llm.py :: get_llm/chat  # langchain_openai接senseaudio网关deepseek-v4-flash(P3编排用)
# 三语料: dnd_rules(数据6238) + dnd_rule_text(规则文本141) + dnd_rule_spec(规则点400)
# 联调验证: 数据提取(獾AC11/HP5) + 判定校验(摔绊DC15力量检定→LLM判定不合规并引正确规则) 均通过

# === P3 编排层（已完成，硬性判定链端到端跑通）===
aidm/brain/state.py :: GameState(TypedDict)  # 贯穿图节点的状态对象(意图/证据/校验/骰子/叙事/状态变更/summary)
aidm/brain/graph.py :: classify(LLM意图分类) → retrieve(hybrid) → verify(LLM校验) → resolve(纯代码骰子!) → narrate(LLM叙事) → apply(持久化)
aidm/brain/graph.py :: build_graph()/get_graph()/run(player_input,campaign,character)  # LangGraph StateGraph + MemorySaver checkpointer
aidm/brain/graph.py :: resolve(attack)  # R-CMB-017攻击命中 + R-CMB-022天然20重击 + R-CMB-023天然1失手 + R-DMG-001/R-CMB-029伤害(重击骰翻倍) — 纯代码
aidm/brain/graph.py :: apply_node  # R-DMG-009/007 HP变更 + 日志 + rolling summary 持久化
# 端到端验证: 玩家"用长剑攻击AC15哥布林" → d20+6命中 → 伤害(重击骰翻倍) → LLM叙事 → 存档 全链路通

# === P4 API 层（已完成，TestClient 验证通过）===
aidm/api/main.py :: FastAPI  # /health /campaign /character(GET/POST) /chat /summary
aidm/api/main.py :: /chat  # POST {player_input,campaign_id,character_id} → 跑判定链 → {narration,dice,intent,state_changes}
aidm/cli.py :: main()  # P5交互层(CLI,BUILD允许) 交互跑团: 输入→判定链→AI叙事+骰子+HP

# === 待实现（可选增强）===
# ui/ :: Next.js + shadcn/ui 跑团Web界面(当前用CLI交互层,API已就绪可直接接前端) # P5可选
```

---

*文档版本：v1.1 · 400 条规则点(364原+36审计补遗) · 经7组并行审计复核全部源文 · 修正11处不准确+补遗36条遗漏(P2/P3入待补清单)*
*下一步：按 P0 规则点编写骰子引擎代码，写完回填"实现回填区"形成双向索引*
