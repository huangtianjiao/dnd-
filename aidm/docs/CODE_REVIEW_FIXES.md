# CODE REVIEW FIXES — 运行时审查与修复规格

> 日期: 2026-07-16
> 范围: 一次完整代码审查发现的运行时/规则/集成问题，及从 P0 到 P2 的逐项修复规格。
> 与 `ISSUES.md` 的关系: ISSUES.md 记录的是历史遗留问题；本文档记录本次审查**新发现**的
> 直接影响玩家游玩的崩溃与规则 bug。修复完成后归档入 ISSUES.md「已修复」表。

## 0. 流程通畅性结论

编排链 `classify → retrieve → verify → [confirm|retrieve_retry] → resolve → narrate → apply`
主体可跑通，但 classify 的 prompt（`brain/graph.py:88-98`）枚举的动作类型与 `resolve()`
的分派表（`brain/graph.py:437-487`）**严重脱节**：

- prompt 实际枚举: `attack|cast|ability_check|explore|start_combat|end_combat|rest|social|levelup|travel|other`
- resolve 还分派: `dash|dodge|disengage|help|ready|hide|search|grapple|shove|study|opportunity_attack|use_item`
  —— 后者**全部不在 prompt 里**，LLM 永远不会分类到它们，玩家说"我躲藏"会被归为
  `other`/`ability_check`，永远走不到确定性判定 `_resolve_hide`。大段战术动作分派是死代码。

可达动作类型状态:

| 动作 | 状态 | 问题编号 |
|---|---|---|
| attack / cast / ability_check / explore / start_combat / end_combat | ✅ 通 | — |
| rest | ✅ 通 | ⑩(契约不一致) |
| other | ✅ 通 | — |
| **levelup** | ❌ 崩 | ① |
| **travel** | ❌ 崩 | ② |
| social | ⚠️ 易崩 | ③ |
| dash/dodge/disengage/help/ready/hide/search/grapple/shove/use_item | ⚪ 不可达 | ⑫ |
| study / opportunity_attack | ⚪ 不可达 + 函数未定义 | ④ |

---

## P0 — 直接中断玩家流程（必须先修）

### ① 【P0】升级动作必崩：Character 传给期望 dict 的 `level_up()`
- **位置**: `brain/graph.py:354-372` → `brain/levelup.py:478`
- **现象**: `_resolve_levelup` 调 `levelup_mod.level_up(ch, ...)`，`ch` 是 `store.get_character()`
  返回的 SQLModel `Character` 对象；而 `level_up(character: dict, *, ...)` 第一步
  `character.get("level", 1)`（levelup.py:518）。SQLModel 对象没有 `.get()` 方法 →
  `AttributeError: 'Character' object has no attribute 'get'`。
- **次生问题**: 即便不崩，`level_up` 只原地改 dict，`_resolve_levelup` 未把结果映射回 `ch`，
  apply_node 末尾 `save_character(ch)` 存的是未改对象 → 升级对角色卡零效果。
- **对照**: `brain/rest.py` 有 `_derive_for_character` 适配层桥接 Character ↔ dict，levelup 没有。
- **修复**: 在 `_resolve_levelup` 内构建适配 dict（含 level/xp/class_name/scores/hp_max/feats 等），
  调 `level_up`，再把返回结果显式映射回 `ch`（level→ch.level, hp_gained→ch.hp_max+=, scores→ch.set_abilities,
  feats→ch.set_feats, new_proficiency_bonus 无独立字段则记录在结果里返回）。落盘由 apply_node 完成。

### ② 【P0】旅行动作必崩：dataclass 塞进 dice dict，narrate 的 `json.dumps` 崩
- **位置**: `brain/graph.py:412-425` → `brain/graph.py:629`(narrate) / `:779-781`(apply 日志)
- **现象**: `_resolve_travel` 返回的 dict 嵌了三个 dataclass 实例：`nav_result`(NavigationResult,
  exploration.py:466)、`encounter_result`(EncounterCheckResult, :582)、
  `perception_result`(PassivePerceptionResult, :536)。`narrate` 无条件
  `json.dumps(dice, ensure_ascii=False)` 无 `default=` 处理器 →
  `TypeError: Object of type NavigationResult is not JSON serializable`。
- **修复**: 用 `dataclasses.asdict(...)` 把三个 dataclass 转成纯 dict 再放进 dice。

### ⑤ 【P0】`store.delete_character` 缺失但被调用
- **位置**: `api/main.py:770`(调用) / `stats/store.py`(无定义)
- **现象**: 房间加入失败清理路径 `store.delete_character(ch.id)` → `AttributeError`，二次故障
  掩盖原始错误。
- **修复**: 在 `stats/store.py` 补 `delete_character(cid, db_path=DEFAULT_DB) -> bool`。

### ⑥ 【P0】天然20死亡豁免的 1HP 恢复从未落盘（战斗每回合触发）
- **位置**: `brain/graph.py:766-771`
- **现象**: `ds = damage.death_save(tracker)` 的返回字典整个被丢弃。damage.py 在 nat20 产出
  `regain_hp=1`，graph 没写回 `ch.hp_current`。违反 R-DMG-017。且整块包在
  `except Exception: pass`，advance_turn/死亡豁免抛错时静默跳过、回合不推进且无日志。
- **修复**: 应用 `ds` 返回（nat20 → `ch.hp_current = max(ch.hp_current, 1)`；deathsaves 计数
  已通过 `apply_death_tracker(tracker)` 落盘）；把 `except Exception: pass` 改为捕获并记日志
  (import logging)，不再静默吞错。

---

## P1 — 规则正确性 / 高频问题

### ③ 【P1】社交动作易崩：NPC 态度来自 LLM 但未约束取值
- **位置**: `brain/graph.py:320-351` → `brain/social.py:129-133`
- **现象**: `npc_attitude = it.get("npc_attitude", "indifferent")` 来自 LLM，`NPC.__post_init__`
  校验必须 ∈ {friendly, indifferent, hostile} 否则 `ValueError`。prompt 未约束 → LLM 可能
  返回 "neutral"/"友好"/"wary"。
- **修复**: 在 `_resolve_social` 内做态度归一化（映射常见同义词到三选一，非法回退 indifferent）。

### ⑦ 【P1】专注豁免硬编码 `proficient=True`（graph.py:689）
- **位置**: `brain/graph.py:686-690`
- **现象**: 专注是体质豁免；法师/术士/吟游/魔契/德鲁伊/游侠/圣武士**默认不熟练体质豁免**，
  不应加 `ch.prof()`。当前一律 `proficient=True, prof=ch.prof()` 高估 +2~+6。
- **修复**: 新增 `CLASS_CON_PROFICIENCY` 集合（野蛮人/战士/圣武士/武僧/术士/游侠），按
  `ch.char_class` 判定 `proficient`。

### ⑨ 【P1】力竭 d20 惩罚漏加（actions.py 多处）
- **位置**: `engine/actions.py:436/456/479/351`（search/study/utilize/hide）
- **现象**: 这些 `ability_check` 调用未传 `circ=-conditions.d20_penalty(...)`，而
  `action_influence/action_attack` 正确传了。R-GLS-047 规定力竭对所有 d20 检定 −2/级。
- **修复**: 为这些检定补 `circ=-conditions.d20_penalty(ch.to_condition_state())`（需 actions.py
  内角色对象可取条件状态；若 actions 用 dict 角色则用 dict 路径）。

### ⑫ 【P1】classify prompt 与 resolve 分派表对齐
- **位置**: `brain/graph.py:88-98`(prompt) / `:437-487`(resolve)
- **现象**: 见 §0。战术动作分支不可达。
- **修复**: 把**已实现**的战术动作加进 classify prompt 枚举：`hide|search|grapple|shove|dash|
  dodge|disengage|help|ready|use_item`。并对每个新动作在 prompt 里给一句专有字段提示（如
  hide→隐匿 DC、grapple→擒抱能力）。`study|opportunity_attack` 见 ④。

### ④ 【P1】`_resolve_study` / `_resolve_opportunity_attack` 未定义
- **位置**: `brain/graph.py:484 / 486`（只有调用、无 `def`）
- **现象**: NameError（目前不可达，因 prompt 无此枚举；一旦 ⑫ 扩展即崩）。
- **修复**: 补 `def _resolve_study(ch, it)`（智力(调查)/感知(察觉) 检定，DC 由 LLM 给）；
  补 `def _resolve_opportunity_attack(ch, it)`（复用近战攻击逻辑，ability 默认 str/dex）。
  两者补完后方可把 study/opportunity_attack 加进 ⑫ 的 prompt 枚举。

### ⑧ 【P1】spellcasting.py / actions.py 绕过伤害管线
- **位置**: `engine/spellcasting.py:413/437`、`engine/actions.py:117`
- **现象**: 用 `dice.roll_dice` 而非 `damage.DamageRequest + roll_damage`，不传抗性/易伤/免疫。
  `graph._resolve_attack`(`:193-198`) 是正确传的，二者不一致。
- **修复**: actions.py:117 `action_attack` 改用 `roll_damage(req, resistances=..., vulnerabilities=...,
  immunities=...)`；spellcasting.py 的目标抗性需从 targets 字典携带（当前架构缺失，本次先让函数
  接受可选 `resistances/vulnerabilities/immunities` 并透传给 roll_damage，目标层后续补）。
  注: spellcasting.py 目前无生产调用方，修复以"接入即正确"为目标。

### ⑩ 【P1】社交态度系统在 graph 集成下形同虚设
- **位置**: `brain/graph.py:344` + `brain/social.py:82-88`
- **现象**: `update_attitude` 阈值 friendly→indifferent 需连续失败 10 次等，单次检定永远达
  不到 → 态度恒不变；NPC 局部对象不存回 Scene。
- **修复**: 本轮先把 `new_attitude` 写回结果供 narrate 叙述；持久化（态度存 Scene/NPC 表）
  列为后续（记 ISSUES）。阈值设计本身符合 5E 社交"多次互动转变态度"，不改阈值。

---

## P2 — 一致性 / 低风险

### ⑪ 【P2】`main.py` `LootDistributeIn` 重复定义
- **位置**: `api/main.py:275` 与 `:885`
- **现象**: 第二个类定义覆盖第一个（靠模块执行顺序 + FastAPI 注册时机才"凑巧不撞"）。
- **修复**: 把第一个（loot.py 体系，`/loot/distribute`）的请求体重命名为 `LootDistributeInV1`，
  消除歧义。第二个（loot_distribution.py 体系，`/loot/distribute/v2`）保持 `LootDistributeIn`。

### ⑫b 【P2】`get_inventory` 用 `mi_db` 在其导入之前
- **位置**: `api/main.py:137-171`(函数) / `:177`(import)
- **现象**: 函数体引用 `mi_db`，但 `from ..data import magic_items as mi_db` 在函数定义之后。
  靠"模块级 import 在任何函数调用前执行"才不崩，但顺序混乱。
- **修复**: 把该 import 上移到文件顶部 import 区。

### ⑬ 【P2】`actions.py:312` 急救检定写死 +0
- **现象**: `check.ability_check(mod=0, prof=0, proficient=False, dc=10)`，忽略医疗者感知+医药熟练。
- **修复**: 用医疗者感知调整值 + 医药熟练加值（需角色对象；actions.py 内角色若为 dict 则取
  `character["scores"]["WIS"]` 等）。

### ⑭ 【P2】`combat.py:512` 起立用基础速度
- **现象**: `cost = round_down(c.speed / 2)` 用基础速度，未用力竭减速后速度。R-GLS-048。
- **修复**: 用 `speed_after_conditions(...)`（回合开始已算好的 `speed_remaining` 上限）。

### ⑮ 【P2】`dice.py:131-146` 骰子解析过宽
- **现象**: `"1d8++5"` 静默接受为 `1d8+5`；`"0d6"` 掷0骰不报警。
- **修复**: 拒绝连续符号；掷0骰抛 ValueError。

### ⑯ 【P2】其他异常吞噬点
- **位置**: `graph.py:70-78`(_load_combat)、`:600-601`(get_recap)、`:615-616`(retrieve_memories)
- **现象**: `except Exception: pass`。记忆检索失败不阻断叙事是**有意设计**，保留但加 `logging.debug`
  便于排查。`_load_combat` 同理保留但记日志。

---

## 验证计划

每完成一档运行测试:

```bash
cd /d/game/dnd/aidm
PYTHONPATH=src python -m pytest tests/ -v
PYTHONPATH=src python tests/test_e2e_flow.py
PYTHONPATH=src python tests/test_combat_flow.py
```

重点回归:
- `test_e2e_flow.py` 含 levelup 分类步骤（修复 ① 后应能跑通 resolve 而非崩）。
- `test_combat_flow.py` 覆盖战斗回合推进（修复 ⑥ 死亡豁免后应不破坏）。
- `test_dice_engine.py` 验证 ⑮ 解析严格化不误伤合法表达式。

## 修复顺序

P0(①②⑤⑥) → P1(③⑦⑨⑫④⑧⑩) → P2(⑪⑫b⑬⑭⑮⑯)，逐项改、逐项验。

---

## 修复结果与勘误（实施后记录）

> 全部 P0/P1/P2 项已修复。`python -m pytest tests/` 143 通过、0 失败；
> `scripts/verify_fixes.py` 针对性验证全部通过。实施过程中的勘误如下。

### 勘误 1：P1⑫「classify/resolve 对齐」实为非问题
审查时依据的是 `brain/graph.py` 内**本地 `classify` 函数**的 prompt（仅枚举 11 种动作），
但 `build_graph()` 实际入口节点是 `agents/director.py:classify_intent`，其
`_DIRECTOR_PROMPT` **早已枚举全部 23 种动作**（含 hide/search/grapple/shove/dash/
dodge/disengage/help/ready/use_item/study/opportunity_attack）。即真实流程的战术动作
**一直可达**，本地 `classify` 是被 agents 取代的死代码。本次仍把本地 `classify` 的
prompt 对齐到完整枚举并标注「已被 Director 取代」，消除误导。

### 勘误 2：P1④「study/opportunity_attack」是可达崩溃而非潜伏
正因为 Director prompt 发出 `study`/`opportunity_attack`，而 `resolve()` 调用了
**未定义**的 `_resolve_study`/`_resolve_opportunity_attack` → 一旦玩家动作被分类为这两者
即 `NameError` 崩溃。严重度应升为 **P0 级可达崩溃**。本次已补两个函数定义
（`_resolve_study` 走智力检定；`_resolve_opportunity_attack` 复用 `_resolve_attack`）。

### 实施扩展：P1⑨ 力竭惩罚也补到 graph resolvers
审查仅点名 `engine/actions.py`，但 graph 的 `_resolve_hide/_resolve_search/_resolve_grapple/
_resolve_shove` 同样漏了 `circ=-conditions.d20_penalty(...)`（仅 `_resolve_ability_check/
_resolve_attack` 有）。本次一并补齐，保持 R-GLS-047 一致。

### 各项落点
| 项 | 文件 | 状态 |
|---|---|---|
| ① levelup | `brain/graph.py`（`_character_to_levelup_dict`/`_apply_levelup_to_character`/`_resolve_levelup` + apply_node levelup 分支） | ✅ 验证升级 5→6、HP 24→29 落盘 |
| ② travel | `brain/graph.py`（`import dataclasses` + `asdict`） | ✅ dice 可 json.dumps |
| ⑤ delete_character | `stats/store.py` | ✅ |
| ⑥ 死亡豁免 nat20 | `brain/graph.py` apply_node | ✅ regain_hp 落盘 + 去静默吞错 |
| ③ 社交态度归一化 | `brain/graph.py` `_normalize_attitude` | ✅ "neutral"/"友好" 不崩 |
| ⑦ 专注 proficient | `brain/graph.py` `CLASS_CON_PROFICIENCY` | ✅ {战士,术士,野蛮人} |
| ⑨ 力竭惩罚 | `engine/actions.py` + `brain/graph.py` resolvers | ✅ |
| ⑫ prompt 对齐 | `brain/graph.py` 本地 classify（Director 已对齐） | ✅ |
| ④ study/opportunity_attack | `brain/graph.py` 新增两函数 | ✅ 可调可序列化 |
| ⑧ 伤害管线 | `engine/actions.py`(action_attack) + `engine/spellcasting.py`(共享掷骰+按目标抗性) | ✅ |
| ⑩ 社交态度持久化 | `brain/graph.py` `_resolve_social`(读Scene累积) + apply_node 写回 | ✅ 跨回合累积 |
| ⑪ LootDistributeIn 重名 | `api/main.py` → `LootDistributeInV1` | ✅ |
| ⑫b import 上移 | `api/main.py` | ✅ |
| ⑬ 急救医药 | `engine/actions.py` action_help 加 medicine 参数 | ✅ |
| ⑭ stand_from_prone | `engine/combat.py` 用 `speed_after_conditions` | ✅ |
| ⑮ 0d6 拒绝 | `engine/dice.py` | ✅（连续符号此前已正确报错） |
| ⑯ except 日志 | `brain/graph.py` | ✅ debug 级 |

### 验证脚本
`scripts/verify_fixes.py` —— 不依赖 LLM，直接调 resolver/apply 验证崩溃路径已修复。

---

## 实时冒烟测试发现与修复（真实 LLM 端到端）

> 用真实 senseaudio(deepseek-v4-flash) 起后端、逐轮 `/chat` 实时人肉跑团（非脚本批量），
> 覆盖 创建→探索→战斗(单怪/多怪)→攻击(命中/未中/击杀)→战斗结束→升级→社交→施法拒绝→
> 搜索→旅行→短休→擒抱→矛盾输入。这些 bug **静态审查未发现，只有真实跑才暴露**。

### 已修复

| # | bug | 现象 | 修复 |
|---|---|---|---|
| S1 | `/chat` 同步 endpoint + `asyncio.ensure_future` | 第 1 轮即 500：AnyIO worker thread 无事件循环 | `api/main.py` 改 `async def` + `run_in_executor` + 复用 `ws._graph_lock` |
| S2 | `_load_combat` 放原始 `Combatant` 进 combatants | start_combat 后下一轮 500：narrate 的 `json.dumps(combat)` 崩 | `graph._combatant_view` 转 JSON 安全 dict |
| S3 | `_extract_json` 解析 deepseek 近似 JSON 失败 | 每轮 narration 是 JSON 碎片、`action_options` 恒空 | trailing comma 修复 + 字段级正则兜底 `_extract_fields_fallback` + `_strip_to_text` 兜底 |
| S4 | 怪物 HP 不扣（apply_node 跳过非玩家 target + Combatant 无 hp） | 命中哥布林 8 伤但 HP 永不变、打不死、narration 说击毙但怪还在 | Combatant 加 `hp/hp_max/dead`；store 序列化加字段；`_resolve_start_combat` 用 `intent.enemies[].hp_max` 初始化（Director prompt 加 hp_max）；`apply_node` 按 cid 优先、name 兜底匹配怪物扣 hp（双写 participants+initiative_order）；`check_combat_end` 按 hp 判全灭。**实测：哥布林 7→2→0 dead→combat.active=False；多怪 e0 死、e1/e2 不受影响** |
| S5 | `ability_check/explore` 无 ability 时默认 str | "感知察觉""调查"用力量 +3（应为 wis/int） | `_infer_ability` 按 skill 名推断属性，explore→wis/study→int 兜底 |
| S6 | 施法无资格/法术位校验 | 战士(空法术位)照施 3 环火球、无法术位消耗 | `_resolve_cast` 开头校验：非施法职业→`error`；该环无法术位→`error`。**实测战士施火球→`dice.error:战士不会施法`** |

### 验证结果（真实 LLM）
- 升级 5→6 级、HP 45→53 落盘 ✓
- 旅行 `nav_result` 纯 dict 可序列化、不崩、迷路叙事 ✓
- 社交态度归一化+跨回合累积 ✓
- 战斗：start→命中扣 hp→击杀→全灭 `active=False`→多怪独立 HP ✓
- 施法拒绝、搜索 wis、擒抱可达 ✓
- 矛盾输入(全动作枚举)→other 纯叙事不崩 ✓
- `pytest tests/` 143 passed、0 failed

### 剩余（未做，需后续决策）
- 无阻塞级剩余问题。所有实时跑中暴露的刁钻问题（S1-S15）均已修复验证。

---

## 第五轮冒烟：魔法飞弹 automatic 分支（真实 LLM）

> 修复最后一项剩余：魔法飞弹等自动命中法术被 LLM 当豁免型处理。

### bug15
| # | bug | 现象 | 修复 |
|---|---|---|---|
| S15 | 魔法飞弹(automatic)被 LLM 当豁免型→走 saving_throw | `_resolve_cast` 用 `it.get("spell_attack")` 二分支，不查 spell.effect_type | `_resolve_cast` 查 `spells.get_spell().effect_type`：`automatic`→直接伤害(不掷攻击/豁免,抗性走管线)，`attack_roll`/`spell_attack`→攻击检定，否则豁免。**实测魔法飞弹 auto_hit=True 直接命中 dmg9(3d4+3)，无 save_success** |

### 最终状态
- 累计 **15 个实时 bug（S1-S15）** 全部修复并真实 LLM 验证通过。
- 所有核心链路打通：怪物AI自动反击 / 死亡豁免(0HP→累积→稳定/死亡) / 专注打断(施专注法术→受伤→con豁免) / 法术位(初始化→消耗→耗尽→长休恢复) / 治疗药水恢复(0HP→喝药水→站起,不叠加) / dead-0HP行动限制 / 魔法飞弹automatic。
- 100 轮实时跑团全 HTTP 200、分类正确、不崩。
- `pytest tests/` 143 passed、0 failed。
- 文档"剩余"无阻塞项。

---

## 第四轮冒烟：治疗恢复与死亡/倒下行动限制（真实 LLM）

> 修复验证器指出的 use_item 治疗不生效（0HP 卡死）与 0HP/dead 仍可行动两个阻塞。

### 已修复（S13-S14）

| # | bug | 现象 | 修复 |
|---|---|---|---|
| S13 | use_item 治疗不生效→0HP 喝药水仍 0HP 卡死 | _resolve_use_item 只叙事不生成 heal；LLM 也不提取 item_name | _resolve_use_item 从 `player_input+item+effect` 检测治疗关键词→掷 2d4+2 生成 `dice.heal`；apply_node step2.8 `_apply_healing_to_character`（含死亡计数归零 R-ADD-008）；step1 跳过 use_item 轮的治疗 state_changes 避免叠加。**实测法师 0HP 喝药水→hp 恢复站起；12HP 喝药水 heal4→16 不叠加** |
| S14 | dead/0HP 倒下者仍可施法/攻击/行动 | resolve 无 hp/dead 检查 | resolve 开头：`ch.dead`→拒所有动作"已死亡需复活"；`ch.hp_current<=0`(未死)→拒战斗动作(attack/cast/grapple...)但允许 use_item(治疗自救)/rest/other。**实测 dead 法师施法/攻击/喝药水/探索全拒"已死亡"；0HP 倒下喝药水可恢复** |

### 恢复链路打通（实测）
- 0HP 倒下 → 喝治疗药水 → `_apply_healing_to_character` 恢复 HP + 死亡豁免计数归零 → 站起继续行动 ✓
- dead（过量伤害致死）→ 所有动作被拒，需复活法术（药水无效）✓

### 验证结果
- `pytest tests/` 143 passed、0 failed
- 累计 14 个实时 bug（S1-S14）全部修复验证
- 所有核心链路打通：怪物AI/死亡豁免/专注打断/法术位/治疗药水恢复/dead-0HP行动限制
- 100 轮实时跑团全不崩分类正确

---

## 第三轮冒烟：专注打断接入（真实 LLM）

> 接入专注打断链路（验证器要求的最后一个链路），又发现并修复 bug12。

### 专注打断接入
- `_resolve_cast` 查 `spells.get_spell(spell_name).concentration`，专注法术在 dice 设 `concentrating_on`。
- `_apply_damage_to_character` 从 `state["dice"]["concentrating_on"]` 读（兼容旧 intent），受伤时触发 con 豁免（`con_proficient` 按职业），失去专注则清 concentrating_on。
- `_render_monster_events` 追加专注豁免结果到 narration。
- **实测**：法师施祝福术（专注）→ 怪反击 → `专注豁免DC10（祝福术）d20=10→维持专注` ✓

### bug12
| # | bug | 现象 | 修复 |
|---|---|---|---|
| S12 | `end_combat` 没把 `active=False` 存 DB | 后续轮 `_load_combat` 仍 active=True，长休/探索被怪回合干扰（法师长休后 hp=11 而非满血） | apply_node 对 `dice.kind=="end_combat"` 调 `load_combat`+`active=False`+`save_combat` |

### 验证结果（真实 LLM，累计约 100 轮）
- 专注打断：施专注法术→怪反击→con 豁免→维持/失去，narration 含【专注豁免】DC/d20 ✓
- bug12 修后长休恢复满血（hp=24/24, 1环=4）✓
- 战斗完整循环联动：法师施法→怪AI反击→法师0HP→死亡豁免累积（成功2/失败2）+ 专注豁免同时触发 ✓
- 全部动作分类正确不崩：cast/hide/study/shove/disengage/use_item/search/attack ✓
- `pytest tests/` 143 passed、0 failed

### 累计 12 个实时 bug（S1-S12）全部修复验证
S1 async / S2 Combatant序列化 / S3 _extract_json / S4 怪物HP / S5 属性推断 / S6 施法拒绝 /
S7 非数字delta / S8 0HP全灭 / S9 长休识别 / S10 法术位初始化 / S11 长休恢复法术位 / S12 end_combat存盘。
所有核心链路打通：怪物AI自动反击、死亡豁免（0HP→累积→稳定/死亡）、专注打断、法术位（初始化→消耗→耗尽→长休恢复）。

---

## 第二轮冒烟：怪物 AI 接入与死亡豁免打通（真实 LLM）

> 接入怪物 AI 到 REST 战斗循环，打通 REST 回合强制与死亡豁免/专注实地触发链路。
> 继续实时人肉跑团至约 55 轮，又发现并修复 5 个 bug（S7-S11）。

### 怪物 AI 接入
- `Combatant` 加 `attack_bonus/damage_dice/damage_type` 字段；`store._combatant_to_dict` 序列化；`_resolve_start_combat` 从 `intent.enemies[]` 初始化（默认 +4/1d6+2）。
- `_run_monster_turn(monster, ch, state)`：确定性怪物攻击（`check.attack_roll`+`damage.roll_damage`），经 `_apply_damage_to_character` 应用（含死亡豁免/专注/过量）。
- `apply_node` 3e：玩家行动后自动结算连续怪物回合（怪攻击玩家→推进→直到轮到玩家或玩家倒下），怪回合叙述追加到 narration（LangGraph 只 merge 返回值，故末尾显式 return narration）。
- **实测**：2 哥布林自动攻击玩家 12→9→4→0；玩家行动后怪反击；narration 含【怪物回合】。

### 已修复（S7-S11）

| # | bug | 现象 | 修复 |
|---|---|---|---|
| S7 | `state_changes` delta 非数字（如 "unconscious"）→ `int()` 崩 500 | LLM 用 delta 表达状态而非数值 | apply_node step1/3a `delta` 解析 try/except 跳过非数字 |
| S8 | `check_combat_end` 把 0HP 玩家当全灭 → 玩家一倒下战斗立即 `enemies_win`、`active=False` → 死亡豁免从不投 | 玩家 0HP 是「倒下」非死亡 | check_combat_end：玩家只有 `dead=True` 才算全灭；怪物 `hp<=0` 即死 |
| S9 | `_resolve_rest` 默认 short，玩家说"长休"被当短休（满血恢复0） | LLM 不给 rest_type | `_resolve_rest(state,ch,it)` 从 `player_input` 推断 long/short |
| S10 | `create_character` 不初始化法术位 → 法师 `spell_slots={}` → 施法总被拒 | 施法职业建角色时法术位空 | create_character 按职业 spellcasting + `max_spell_slots(level)` 初始化 |
| S11 | 长休 `spell_slots_restored:true` 但法术位没实际恢复 | `_apply_rest_to_character` 只恢复 HP/力竭/temp_hp | 长休时施法职业 `set_spell_slots(max_spell_slots(level))` |

### 死亡豁免链路打通（实测）
- 玩家被打到 0HP → 倒下但 `combat.active=True`（S8 修复）→ 每轮投死亡豁免（3d 条件去掉 current==玩家依赖）→ 累积成功/失败 → 3 成功 `stable=True` / 3 失败 `dead=True`。
- narration 追加【死亡豁免】d20=... 结果（权威，LLM 叙事偶与骰子矛盾但代码行准确）。
- **实测**：d20=14成功(1/0)→d20=2失败(1/1)→d20=19成功(2/1)→d20=13成功(3/3)→`伤势稳定 stable=True`。

### 验证结果（真实 LLM，约 55 轮）
- 怪物 AI 自动攻击玩家 + HP 下降 ✓
- 0HP 倒下 + 死亡豁免累积 + 稳定 ✓
- 法师法术位初始化{1:4,2:3,3:2} + 施法消耗(1环4→3) + 长休恢复(3→4) ✓
- 长休识别 long + success ✓
- 战士施法被拒 + 非数字 delta 不崩 ✓
- `pytest tests/` 143 passed、0 failed

### 关于"100 轮"
实时人肉跑满 100 轮每轮 LLM 20-40 秒、纯等待 50 分钟以上；已跑约 55 轮覆盖全部动作类型路径（创建/探索/战斗单多怪/攻击命中未中击杀/战斗结束/升级/社交/施法拒绝+消耗+恢复/搜索/旅行/短休/长休/擒抱/死亡豁免累积稳定/矛盾输入）。所有实时发现的 11 个 bug（S1-S11）均已修复并真实 LLM 验证通过，143 测试无回归。


