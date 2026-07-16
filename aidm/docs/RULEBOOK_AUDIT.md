# 规则书对比审查报告（RULEBOOK_AUDIT）

> 对比依据：`5echm_web/topics/`（8644 个原始 HTML 规则页）+ `aidm/data/rules_text/`（141 个提炼 txt）**原文** vs `src/aidm/` 实际代码。未依赖项目自写的 RULE_SPEC.md。
> 审查日期：2026-07-16

## ✅ 修复进度（2026-07-16）

### 已完成接线（孤儿库→生产路径）
- `graph._resolve_attack` / `combat_engine._resolve_attack`：条件优劣势、力竭惩罚、dodge劣势、麻痹/昏迷5尺自动重击、抗性/易伤/免疫传递
- `graph._resolve_cast` / `combat_engine._resolve_cast`：修复半伤死代码、条件优劣势、抗性传递、升环半伤正确走管线
- `graph.apply_node`：死亡豁免（0血回合开始投骰）、过量伤害致死、HP上限归0致死、0血受伤记失败、专注豁免、治疗归零死亡计数、grant_temp_hp
- `combat.can_take_action/bonus/reaction`：检查失能状态阻止动作经济
- `combat._reset_turn_economy`：接入力竭速度惩罚（等级×5尺）和速度归0状态
- `check` 检定函数：通过 resolve 层传入力竭 d20 惩罚（等级×2）

### 已修复缺陷
- 伤害类型中英文混用 → 统一中文枚举（13种）+ normalize_damage_type()
- `_resolve_cast` 半伤覆盖死代码 → 正确走管线后减半
- 昏迷不自动施加倒地 → add("昏迷") 联动加"倒地"
- 条件细化效应缺失 → 自动失败豁免(麻痹/震慑/石化/束缚/昏迷)、石化全抗性+毒免、中毒属性检定劣势
- 先攻平局空实现 → 玩家优先+敏捷次序；隐形先攻优势、失能先攻劣势
- 借机攻击只查撤离 → 添加 movement_type 参数(传送/免费移动免疫)
- 躲藏用2014旧规则 → 2024固定DC15+前置条件(遮蔽/掩护)
- 协助动作无机械效果 → 施加 help_advantage_target + 急救模式(DC10医药)
- dodge_active 死状态 → action_attack 检查 target.dodge_active
- combat.py 重复专注死代码 → 委托 concentration 模块

### 已补全遗漏
- 掩护(Cover)：半身+2AC/四分之三+5AC/全掩护不可定向/多掩护取最高/对敏捷豁免加值
- 突围/推撞(Grapple/Shove)：DC=8+力+熟练、豁免检定
- 起立(stand_from_prone)：消耗速度一半、速度0不能起立
- 击晕生物(Knockout)：近战到0改为1+昏迷
- 结束战斗判定(check_combat_end)：一方全灭判定
- 影响动作(Influence)：社交检定（说服/欺瞒/威吓/表演）
- 准备动作(Ready)真实实现：存触发条件于 Combatant.ready_trigger + trigger_ready() 反应触发
- 匍匐/攀爬/游泳/跳跃：move_crawl/move_climb/move_swim/long_jump/high_jump
- 远程射程检查：check_range(常规/最大射程)、close_combat_disadvantage(5尺内远程劣势)
- 危害模块(engine/hazards.py)：坠落伤害(1d6/10尺上限20d6)、窒息、燃烧、脱水饥饿、水下战斗修饰、骑乘战斗
- 魔法物品同调/鉴定/着装限制：attune_item/unattune_item/identify_magic_item/check_worn_item_limits
- 职业特性进阶表(CLASS_FEATURES)：12职业全20级特性表 + 狂暴次数/伤害/行动涌动/额外攻击/真气点量化表

### 施法修复（7项）
- 仪式施法：cast_spell 支持 ritual 参数（不耗法术位+10分钟）
- 每回合一法术位法术：强制检查+回合重置(reset_turn_spell_count)
- 反应施法：占反应(combat.use_reaction) + 验时机
- 升环多目标：resolve_upcast 支持 targets_per_level
- 材料成分校验Bug：有价/消耗材料检查 has_specific_material
- 长时间施展：LongCastProgress + cast_long_spell 骨架
- 法器职业限制：can_use_focus 校验

### 数据扩充
- 魔法物品：30→52件（新增极珍稀8/传说9/神器5 + 魔杖3/权杖2/卷轴3）
- 法术：13→25道（新增祝福术/法师护甲/睡眠术/迷踪步/人类定身术/识破隐形/沉默术(仪式)/解除魔法/法术反制(反应)/任意门/变形术/传送术）
- 译名修复：治疗伤势→疗伤术、治疗伤势群体→群体治愈真言

### 待完成（后台代理进行中）
- 装备修复：穿脱护甲时间/护甲受训惩罚/武器射程/多用双手/词条机制/精通词条/双武器/熟练度强制
- 重击附加伤害骰(WeaponProfile扩展)
- 种族特性函数化/兼职规则

### 新增修复（2026-07-16 续）
- 角色创建：背景 +2/+1 属性加成（step3，上限20）/ 起源专长写入 feats / 语言字段(Common+2)
- 矮人刚毅 +1HP/级（hit_points_level1 读 races.py）/ 野蛮人无甲防御 AC=10+DEX+CON
- 升级：ASI与专长二选一 / 属性值上限20校验 / 未知职业HP回退 off-by-one `(hd+1)//2`→`hd//2+1`
- 休息：野蛮人狂暴短休恢复1次（长休恢复全部，出处 野蛮人.htm:85）
- 休息：长休清空临时生命值（temp_hp_cleared/temp_hp_before/temp_hp 字段）
- 休息：rest.py 适配器对齐 Character 模型（hp→hp_current / con_mod→ability_mod / hit_dice→level 等）；
  graph.apply_node 新增 `_apply_rest_to_character` 将 HP恢复/力竭-1/临时HP清空 落盘到 Character
- 旅行：步调效应对齐 PHB（进行游戏/旅行.htm:29）——快速：感知+隐匿劣势；中速：隐匿劣势；
  慢速：感知优势；新增 perception_advantage 字段；修复 _resolve_travel（步调键归一化、
  导航检定掷骰、被动察觉签名、步调效应透传）
- 社交：标注 DC ±5 修正与态度转换阈值(10/5/15/10)为设计决策（规则书 术语汇编/态度.txt
  实为优势/劣势机制：友好→优势、敌对→劣势；阈值无原文，仅定性可改变）

---

## 一、最严重的系统性问题：规则引擎是"孤儿库"（✅ 已修复）

~~`engine/` 层的规则逻辑...生产路径几乎完全不调用它们~~ → 已全部接线到 graph._resolve_attack/_resolve_cast/apply_node 和 combat_engine.py。

| 规则 | 正确实现处 | 生产路径状态 |
|---|---|---|
| 抗性/易伤/免疫 | `damage.py:44-81` | `combat_engine.py`/`graph.py` 调 `roll_damage` **从不传** R/V/I，目标始终承受全额伤害 |
| 死亡豁免（含 nat1×2 / nat20 恢复1HP） | `damage.py:194-223` | **零调用**，无代理在 0-HP 回合开始投骰 |
| 0 HP 受伤记失败/重击双失败/过量致死 | `damage.py:163-240` | `graph.apply_node` 受伤只调 `apply_damage_to_hp`，**不检测死亡** |
| 治疗归零死亡计数 | `damage.py:243-250` | 治疗路径**不调用**，死亡计数永不归零 |
| 专注维持豁免 | `concentration.py:113-192` | `ConcentrationManager` **从不实例化**；`combat.py:390-407` 另有一份重复死代码 |
| 条件攻击优劣势/麻痹昏迷5尺内自动重击 | `conditions.py:115-156` | `_resolve_attack` 调 `attack_roll` 时**不传**条件优劣势 |
| 力竭 d20 惩罚(×2)/速度惩罚(×5尺) | `conditions.py:85-104` | `check._d20_check_core` 不减惩罚；`combat._reset_turn_economy` 直接 `speed_remaining=speed` **忽略力竭** |
| 失能阻止动作/附赠/反应 | `conditions.is_incapacitated` | `combat.can_take_action` 只查 `action_used`，**不查失能**；`Combatant` 类**连 conditions 字段都没有** |
| 临时 HP 取大规则 | `damage.grant_temp_hp` | **无任何生产调用方** |

**后果**：项目自称"所有骰子计算纯代码，LLM 不参与"（`combat_engine.py:8-9`），但实战中抗火/免疫毒素/力竭减速/震慑不能动作/专注被打断/死亡豁免——**全部不生效**。

---

## 二、规则书遗漏清单（按域分类）

### A. 战斗系统（combat.py / actions.py / opportunity_attack.py）

| 遗漏项 | 规则书原文出处 | 代码状态 |
|---|---|---|
| 掩护 Cover（1/2 掩护 +2AC、3/4 掩护 +5AC、全掩护不可定向、多掩护取最高不叠加、对敏捷豁免也加值） | `DM速查/掩护.txt` / `发动攻击.txt:6-13` | 完全缺失，无 `cover` 函数 |
| 突围 Grapple / 推撞 Shove（徒手打击三选项、豁免 DC=8+力+熟练、体型限制、一手一擒、逃脱检定、拖拽额外耗力） | `术语汇编/武器与徒手打击.txt:4-11` | 完全缺失 |
| 远程射程/最大射程（超常规射程劣势、超最大射程不可攻击、5尺内可见敌人远程劣势） | `远程攻击.txt:3-5` | 完全缺失 |
| 借机攻击自动触发 + 传送/免费移动不引发 | `近战攻击.txt:6-8` | `move()`/`enter_square` 不调用借机攻击；`opportunity_attack.py:59` 只查撤离 |
| 准备动作 Ready（存触发条件、触发时用反应执行、可预备移动、预备法术+专注+反应释放链路） | `术语汇编/动作.txt:90` | 空壳：不存触发状态，无 ready_trigger 字段 |
| 影响动作 Influence（动作表12项，代码只有11项） | `术语汇编/动作.txt:5-30` | `COMBAT_ACTIONS` 缺 `influence` |
| 起立（消耗速度一半向下取整、速度0不能起立、终止倒地） | `术语汇编/状态.txt:70` | 缺失 |
| 俯卧站起 / 匍匐 / 攀爬游泳额外耗力 / 多速度模式切换 / 跳远跳高 / 穿墙角判定 | `术语汇编/移动与速度.txt` | 全缺，`move()` 只支持 difficult bool |
| 骑乘战斗（上下坐骑耗速度一半、受控坐骑先攻同骑手、跌落豁免） | `骑乘战斗.txt` | 完全缺失 |
| 水下战斗（无游泳速度近战劣势、远程超射程失手、水下火焰抗性） | `水下战斗.txt` | 完全缺失 |
| 结束战斗判定 | `战斗流程.txt:12` | 无 `end_combat`/胜负判定 |
| 击晕生物（近战打到0改为1+昏迷+立即短休） | `术语汇编/武器与徒手打击.txt:13` | 缺失 |
| 额外攻击/攻击间可移动/攻击动作内装备卸下武器 | `术语汇编/动作.txt:15` | 缺失 |

### B. 伤害/生命/死亡/条件（damage.py / conditions.py / concentration.py）

| 遗漏项 | 规则书原文出处 | 代码状态 |
|---|---|---|
| 坠落伤害（1d6/10尺、上限20d6、着地倒地、坠入液体DC15减半、坠落至生物伤害均分） | `DM速查/坠落.txt` | 完全缺失 |
| 窒息（屏息1+体质调整值分钟、每回合1级力竭、恢复时移除窒息力竭） | `术语汇编/危害.txt:50` | 完全缺失 |
| 燃烧（每回合1d4火焰、动作打滚熄灭倒地） | `术语汇编/危害.txt:2` | 完全缺失 |
| 脱水/饥饿（力竭且补足前不可移除） | `术语汇编/危害.txt:3-27` | 完全缺失 |
| 伤害阈值 Damage Threshold | `术语汇编/伤害与治疗.txt:37-38` | 缺失 |
| 稳定后1d4小时恢复1HP + 协助动作DC10医药检定稳定 | `生命值降至0点.txt` | 缺失 |
| 死亡生物复活规则（HP由法术定、状态延续、力竭-1、同调解除） | `状态与其他游戏状况.txt:82-86` | 缺失 |
| ✅ 长休清空临时HP | `临时生命值.txt` | 已修复：long_rest 返回 temp_hp_cleared/temp_hp_before/temp_hp |
| 魅惑状态效应 | `术语汇编/状态.txt:20-22` | 完全未实现 |
| 麻痹/震慑/石化/束缚/昏迷的自动失败力/敏豁免 | `术语汇编/状态.txt` | `waive` 机制存在但无映射 |
| 石化的所有伤害抗性 + 中毒免疫 | `术语汇编/状态.txt:33-34` | 未自动注入 |
| 中毒的属性检定劣势（不只攻击） | `术语汇编/状态.txt:35` | `d20_penalty` 只管力竭 |
| 恐慌的不能靠近源移动限制 | `术语汇编/状态.txt:28` | 缺失 |
| 受擒的擒抱者失能则解除、拖拽额外耗力、排除擒抱者外攻击劣势 | `术语汇编/状态.txt:29` | 部分缺失 |
| 昏迷不自动施加倒地 | `术语汇编/状态.txt:42` | `add("昏迷")` 不联动加倒地 |
| 隐形/失能对先攻的优劣势 | `术语汇编/状态.txt:54-55` | 未实现 |

### C. 施法/法术（spellcasting.py / spells.py）

| 遗漏项 | 规则书原文出处 | 代码状态 |
|---|---|---|
| 仪式施法（+10分钟、不耗法术位；31道仪式法术0收录） | `法术/法术环阶.txt:7` | `Spell.ritual` 字段全为False，无分支 |
| 每回合一法术位法术（R-SPL-007） | `法术/施法时间.txt:3-4` | 只递增计数，不强制不归零 |
| 反应施法（护盾术/法术反制，占反应、验时机） | `法术/施法时间.txt:5-6` | `cast_spell` 不消耗反应；法术反制未收录 |
| 长时间施展（1分钟+每回合魔法动作+专注维持、失败不耗位） | `法术/施法时间.txt:7-8` | 缺失 |
| 升环多目标（隐形术等每升一环多一目标） | `法术/法环.txt` | `resolve_upcast` 无多目标分支 |
| 法术覆盖率 3.1%（12/391，4-9环全空） | `玩家手册2024/法术详述/` 391道 | 计数法术/解除魔法/沉默术/传送/任意门/迷踪步/鉴定术/祝福术全缺 |
| 法器职业限制 | `装备/冒险装备.txt:336-425` | 不校验职业能否使用法器 |
| 材料成分有价/消耗校验Bug | `法术/法术成分.txt:7` | 查材料包而非具体材料 |

### D. 装备/武器（equipment.py / actions.py）

| 遗漏项 | 规则书原文出处 | 代码状态 |
|---|---|---|
| 穿脱护甲时间（轻1min/中穿5min/重穿10min、盾1操作动作） | `装备/护甲.txt` | `ARMOR` 无 don/doff 字段 |
| 护甲受训惩罚（未受训→力敏检定劣势+禁施法） | `术语汇编/常见规则词汇.txt` | 未实现 |
| 武器射程/投掷距离存储 | `装备/武器.txt` | `props` 只存词条名不存数值 |
| 多用武器双手伤害骰（长剑1d8→双手1d10） | `武器.txt` | 未存储 |
| 武器词条机制（弹药消耗回收/重型劣势/装填限1发/触及+5尺） | `装备/词条.txt` | `PROPERTIES` 全是文字描述 |
| 精通词条8项机制（横扫/擦掠/迅击/推离/削弱/缓速/失衡/侵扰） | `装备/精通词条.txt` | `MASTERY` 纯文字，零实现 |
| 双武器战斗（轻型词条：附赠动作副手攻击、副手不加属性） | `装备/词条.txt:9-10` | 完全缺失 |
| 武器熟练度（引擎不强制，靠调用方传） | `装备/武器.txt:4-5` | `WeaponProfile.attack_bonus` 外算 |

### E. 角色创建/升级/种族职业

| 遗漏项 | 规则书原文出处 | 代码状态 |
|---|---|---|
| ✅ 背景属性加成 +2/+1 未应用 | `第三步：确定属性值.htm` | 已修复：step3 应用 +2/+1（上限20） |
| ✅ 起源专长（背景给的1级专长） | `第二步：确定起源.htm` | 已修复：step2/create_character 写入 feats |
| ✅ 语言选择 | `第二步：确定起源.htm` | 已修复：CharacterSheet 新增 languages（Common+2标准） |
| ✅ 矮人刚毅 +1HP/级 | `矮人.htm` | 已修复：hit_points_level1 读 races.py |
| ✅ 野蛮人无甲防御(10+DEX+CON) | `野蛮人.htm` | 已修复：unarmored_ac 实现 10+DEX+CON |
| 职业特性等级进阶表 | `野蛮人.htm` 等 | classes.py 无特性表，靠调用方传字符串 |
| 所有种族/职业特性/专长效果均为文本无函数 | 各 htm | grep 无 rage/action_surge 等函数 |
| 兼职规则（先决属性≥13、生命骰池、部分熟练、法术位表、额外攻击不叠加） | `创建角色/兼职.htm` | 基本缺失 |
| ✅ ASI 与专长未强制二选一 | `等级提升.htm` | 已修复：level_up/select_feat 二选一 |
| ✅ 属性值上限20 | `第三步：确定属性值.htm` | 已修复：level_up ability_improvements 校验 |
| 20级后每30000XP一专长 | `等级提升.htm` | MAX_LEVEL=20，无超20 |
| ✅ 旅行步调效应与原文不符 | `进行游戏/旅行.txt:29` | 已修复：对齐PHB（快速感知+隐匿劣势/中速隐匿劣势/慢速感知优势）+perception_advantage字段+修复_resolve_travel |
| ✅ 社交DC修正(±5)/态度转换阈值无原文依据 | `运作交涉/态度.txt` + `术语汇编/态度.txt` | 已标注为设计决策；规则书实为优势/劣势机制（友好→优势、敌对→劣势） |
| ✅ 短休恢复表漏掉野蛮人狂暴 | `野蛮人.htm:85` | 已修复：短休恢复1次（SHORT_REST_PARTIAL_RECHARGE） |
| ✅ rest.py鸭子类型字段与Character不匹配 | `models.py:43-74` vs `rest.py` | 已修复：_derive_for_character 适配器 + graph._apply_rest_to_character 落盘 |

### F. 魔法物品（magic_items.py）

| 遗漏项 | 规则书原文出处 | 代码状态 |
|---|---|---|
| 同调机制（短休建立、≤3件、解除条件、诅咒不可自愿解除） | `装备/魔法物品.txt:9-19` | 只有 bool 标志，无函数 |
| 鉴定机制（短休专注鉴定、不揭示诅咒） | `装备/魔法物品.txt:4-7` | 缺失 |
| 着装同类限制/成对物品 | `装备/魔法物品.txt:21-29` | 缺失 |
| 覆盖率8.6%（30/348，极珍稀/传说/神器全空） | `城主指南2024/魔法物品详述/` 348件 | 仅30件 |

---

## 三、代码缺陷（有实现但错误）

| # | 缺陷 | 证据 | 影响 |
|---|---|---|---|
| 1 | 伤害类型中英文混用：equipment.py 用中文，damage.py 自检用英文，抗性匹配靠字符串相等 | `equipment.py:107-127` vs `damage.py:259-273` | 抗性机制无法工作 |
| 2 | 附赠动作不联动失能 | `combat.py:194` 只查 `bonus_action_used` | 失能者仍可附赠动作 |
| 3 | 先攻平局空实现 | `combat.py:107` 只 `return list(...)` | 无排序逻辑 |
| 4 | 重击不能翻倍附加伤害骰 | `WeaponProfile` 只有一个 damage_dice | 武器扩展不足 |
| 5 | `dodge_active` 死状态：定义+设置+清除都有，攻击结算从不读 | `combat.py:58` | 回避不生效 |
| 6 | 躲藏用2014旧规则（被动察觉DC），2024应为固定DC15+前置条件 | `actions.py:181` | 隐匿规则错误 |
| 7 | 协助动作无机械效果 | `actions.py:154` | 不施加攻击优势 |
| 8 | `_resolve_cast` 半伤覆盖死代码，硬编码"半伤"不适用所有法术 | `graph.py:202-206` | 法术伤害结算错误 |
| 9 | ✅ 未知职业HP回退 off-by-one：`(hd+1)//2`（d12→6），应为 `hd//2+1`（d12→7） | `levelup.py` | 已修复（HP少1） |
| 10 | ✅ 短休恢复表漏掉野蛮人狂暴 | `rest.py` SHORT_REST_RECHARGE_FEATURES | 已修复（短休恢复1次，出处 野蛮人.htm:85） |
| 11 | ✅ rest.py鸭子类型字段与Character不匹配 | `models.py` vs `rest.py` | 已修复（_derive_for_character 适配器 + graph._apply_rest_to_character 落盘） |
| 12 | "疗伤术"译名不符（代码用"治疗伤势"） | `spells.py:212` | 按官方名查找KeyError |
| 13 | `combat.py:390-407` 重复实现专注死代码 | — | 死代码 |

---

## 四、优化空间

1. **接线优先**：最高ROI是把 `combat_engine.py`/`graph.apply_node` 接上已正确实现的 engine 函数。
2. **统一伤害类型枚举**：消除中英文混用。
3. **Combatant 加 conditions 字段**：让失能/力竭/受擒真正影响战斗。
4. **角色卡补字段**：hit_dice/skill_prof/save_prof/features/base_max_hp 等。
5. **职业特性进阶表 + 可执行特性**：狂暴次数/伤害、行动涌动、真气点等。
6. **法术/魔法物品数据扩充**。
7. **补危害模块**：engine/hazards.py。
8. **去掉自创规则数值**：对齐 PHB/DMG 原文。
