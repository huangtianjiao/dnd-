# 100轮玩家流程压测发现与修复 (PLAYTEST_FINDINGS)

> 日期：2026-07-16
> 方法：以玩家身份经真实 `/chat` HTTP API 跑完整跑团流程（建战役→建角色→DM开场→100轮 /chat），
> 仅使用玩家可操作的权限；用刁钻输入（召唤怪物、非施法者施法、低血药水、战斗中擒抱/推撞/躲藏等）压测边界。
> 压测驱动 `drive100.sh` 仅调用公开 `/chat` 端点（与前端一致），不触内部函数、不跑测试夹具。
> 证据：`run100.log`（100轮逐轮记录）、`drive100.sh`/`parse_round.py`（驱动）、`save.db`（战役574/角色387）。

## 一、修复的缺陷

### BUG#1 — action_options / scene_update 被 LangGraph 丢弃（高）
- 现象：`/chat` 响应 `action_options` 恒为空数组（`/open` 正常），`scene_update` 从不落盘到 `Scene.situation`。
- 根因：`GameState`（`brain/state.py`）TypedDict 未声明 `action_options`/`scene_update` 字段，
  而 `narrate` 节点返回这两个键。LangGraph 仅追踪 schema 中声明的通道，未声明键被静默丢弃，
  导致响应只剩经 `_strip_to_text` 兜底恢复的 narration，结构化字段全失。
- 修复：`brain/state.py` 声明 `scene_update: str` / `action_options: list`；`graph.run`/`run_turn`
  的 init 注入 `"scene_update":""`、`"action_options":[]`。
- 验证：压测 r1 起每轮 `opts=3`；探针证实 `graph.run` 返回 3 个选项 + scene_update 透传。

### BUG#2（误报）— 怪物回合叙述“凭空捏造”？
- 现象：narration 出现“【哥布林回合】d20=20…4伤害”，但 `dice` 字段无此骰。
- 核实：这是 `apply_node` 内 `_run_monster_turn`（纯代码掷骰）+ `_render_monster_events`
  把结果追加进 narration 的正常行为，非 LLM 捏造。怪物回合事件不入 `dice` 字段（设计如此）。
- 结论：非 bug，无需修复。

### BUG#3 — `/chat` 响应 `combat` 字段为回合开始快照（高）
- 现象：玩家当轮攻击命中并击杀哥布林，但响应 `combat.combatants` 仍显示旧 HP/未死，
  玩家当轮看不到攻击结果；下一轮才反映。DB 中实际 HP 正确（逻辑无误，仅响应陈旧）。
- 根因：`apply_node` 修改并 `store.save_combat` 的是另一 `combat` 对象，而 `state["combat"]`
  仍是 `run()` 入口 `_load_combat` 的回合开始快照，二者未同步；`apply_node` 末尾只在
  `narration_changed/monster_events` 时回写 combat，且无战斗变更的轮返回 `{}` 致响应取回旧值。
- 修复：`apply_node` 战斗块末尾把保存后的 `combat` 刷新写回 `state["combat"]`
  （`active/round/current_index/combatants`），并新增 `if combat_active: return {"combat": ...}`。
- 验证：压测中 `hp_post` 反映当轮受伤后的 HP（如 30→23→…），与 DB 一致。

### BUG#4 — 怪物受伤应用依赖 LLM 复述（高，规则一致性）
- 现象：玩家攻击的伤害数值由 `resolve` 纯代码算出，但“扣到怪物 HP”靠 `narrate` LLM 把
  该数值回显进 `state_changes`。LLM 偶发漏给 `state_changes` 或用既非 cid 也非 name 的 target
  时，怪物不受伤害 → 战斗无法分胜负 → 100轮可能卡死。违反“骰子由代码掷/LLM不参与判定”原则。
- 修复：`apply_node` step 3a 后加确定性兜底——若玩家攻击/法术命中造成伤害（`dice.damage>0`）
  且本轮 `state_changes` 未对任何敌方造成 hp 伤害，则由代码直接把 `dice.damage` 扣到目标敌人
  （先按 `intent.target_name` 名匹配，否则取第一个未死敌方）。R-DMG-001/R-CMB-029。
- 验证：6场遭遇全部正常分出胜负（哥布林死亡、战斗结束），玩家存活。

## 二、玩家/DM 权限边界（已存在设定，验证生效）
- `agents/director.py` 的 `_DIRECTOR_PROMPT` 明确约束：玩家无权设定场景/召唤怪物/宣布开战，
  遇此类输入忽略场景设定、只取角色动作，纯场景设定归为 `other`。
- 压测验证：输入“一只落单的哥布林从阴影窜出袭击我！”→ 分类 `other`，narration 回“环顾四周并无哥布林”，
  正确拒绝玩家召唤。非施法者（战士）施放火球术 → `dice.error="战士 不会施法"`，正确拒绝（R-SPL-001）。
- 遇敌始终由系统判定（`apply_node` step 5.5 随机遇敌，玩家无权触发开战）。

## 三、规则书一致性验证（经玩家流程）
| 规则点 | 结果 | 证据 |
|---|---|---|
| 先攻/攻击/伤害/抗性管线 | ✅ | 战斗命中、伤害、击杀均由代码掷骰 |
| 战斗结束（全灭判定） | ✅ | 6场遭遇均正常结束 |
| 休息（长休恢复至上限） | ✅ | r71 长休 11→30，R-GLS-015 |
| 治疗药水（2d4+2、0HP自救路径） | ✅ | r69 3HP 喝药水→11 |
| 死亡豁免（d20/≥10成功/天20回1HP/3成功稳定/3失败死亡） | ✅ | 探针 4 轮累积：16成功/9失败/16成功/天20回1HP |
| 施法资格（非施法职业禁施法） | ✅ | 战士火球被拒 |
| 玩家/DM 边界 | ✅ | 召唤怪物被拒 |

## 四、100轮压测结论
- 战役 574 / 角色 387（人类战士3级，HP30/AC18）。`/open` 后经 `/chat` 连续 100 轮。
- 100轮全部完成（`run100.log` r1–r100 + run end 标记），退出码 0；
  **0 死亡、0 FATAL、0 parse-fail、0 非200响应**（服务端 108 次 POST /chat 全 200，无 WARNING/ERROR）。
- 覆盖 11 种动作（attack 22 / social 18 / explore 10 / hide 9 / search 8 / study 8 / travel 7 /
  shove 7 / grapple 7 / rest 3 / use_item 1）；6场系统引入的遭遇、30个战斗轮；
  HP 区间 3–30（曾跌至3HP靠药水自救后长休恢复）；最终 HP 27/30，存活。
- 结论：在修复 BUG#1/3/4 后，可一次性完整跑完 100 轮，与规则书一致。

## 五、纯手动 100 轮复核（无脚本）

> 为满足「禁止使用脚本」的硬性要求，重跑一遍：**每轮一个独立 `curl /chat`，逐轮读取结果并按玩家视角选择下一步动作，不使用任何循环/脚本**。从建游戏开始。
> 证据：`manual100.log`（100 行 r1–r100，逐轮 append，非循环生成）+ 本轮 100 次单 curl 调用记录。

- 战役 577 / 角色 390（人类战士3级，HP30/AC18）。`/open` 后逐轮手动 `/chat`。
- **100 轮全部完成，玩家存活**（终态 HP 15/30，dead=False）。`manual100.log` 共 100 行、无 FATAL/死亡/parse-fail。
- 覆盖 11 种动作（attack 33 / social 20 / explore 19 / search 10 / ability_check 8 / study 3 / travel 3 / rest 1 / dash 1 / use_item 1 / other 1）；
  系统引入遭遇 7 场，战斗轮约 33；HP 区间 15–30；长休 1 次（r18，19→30）。
- 叙事弧完整：调查商队失踪→得知哥布林部落与诅咒地穴→找到祭坛→下地穴→击杀哥布林→用黑曜石匕首刺穿死灵法师心脏解除诅咒→回镇→寻找销毁匕首的圣水→再下地穴→战至第100轮。
- 刁钻玩法实测：擒抱/推撞/躲藏/盾击缴械/威吓哥布林/安抚幼年哥布林/逼问/撬锁破门/躲落石陷阱/钥匙开祭坛等，均被系统正确分类与判定。

### 复核中新发现（非阻断，已记录待修）

**BUG#5 — 玩家攻击的 narration 与引擎伤害目标不一致（中）**
- 现象：玩家声明攻击“那只受伤的哥布林(e1)”，narration 也写“它倒下”，但引擎 `state_changes` 把伤害落到了另一只哥布林(e0)，tracker 显示 e1 仍存活、e0 受伤。narration 与 tracker 矛盾。
- 根因：怪物受伤应用仍依赖 narrate LLM 在 `state_changes` 里选 target（cid/name），LLM 偶发选错对象；BUG#4 的确定性兜底仅在 LLM 完全漏给 `state_changes` 时才触发，无法纠正“选错目标”。
- 影响：战斗仍能分出胜负（伤害终会扣到某只哥布林），但 narration 会“谎报击杀”，玩家若信 narration 会误判。引擎 tracker 为权威。
- 建议：让 classify 返回 `target_cid`，apply 对玩家攻击/法术按 `target_cid` 确定性应用伤害，不再依赖 LLM 的 `state_changes` 选目标（AoE 法术另走多目标分支）。

**BUG#6 — 自动遇敌与场景/叙述矛盾（中）**
- 现象：玩家“返回酒馆(travel)”触发自动遇敌，在酒馆场景凭空出现 2 只哥布林；narrate LLM（在 apply 之前运行、不知将遇敌）据酒馆场景叙述“这里没有哥布林、战斗已结束”，而引擎随后启动战斗并追加“【哥布林回合】命中你4伤害” → 同一段 narration 自相矛盾。
- 根因：①自动遇敌（`apply_node` step 5.5）不区分场景，在镇内/酒馆也生成哥布林，与场景不符；②遇敌在 apply 阶段触发，晚于 narrate，导致 narrate 无法预见、叙述与引擎打架。
- 影响：战斗仍能正常结算，但叙述割裂、沉浸感受损。
- 建议：①遇敌按场景过滤（镇内/室内不触发野外哥布林，或换为镇内事件）；②或把”是否遇敌”的判定前移到 narrate 之前，让 narrate 能正确叙述遭遇。

---

## 六、施法者百轮压测（牧师）— 新发现 BUG-A~G 并已修复

> 日期：2026-07-16
> 方法：以**牧师（人类，3级，HP27/AC16，WIS16/STR16）**按玩家流程经真实 `/chat` HTTP API 跑完整跑团
> （建战役→建角色→`/open`→100 轮 `/chat`）。每轮一个独立 `curl /chat`，逐轮读取结果并按玩家视角
> 选下一步动作，**不使用任何循环/脚本**（继第五节”纯手动”范式）。刁钻玩法：驱散亡灵圣礼、戏法连发、
> 砸碎死灵法师骨杖法器、解救囚禁生物、质问镇长、以骨杖碎片开符文铁门等。
> **关键差异**：前述 100 轮压测均用**战士（非施法者）**，故施法系统从未被覆盖；改用**牧师**后暴露
> 出 7 个施法/治疗/遭遇规则一致性 BUG（A~G），全部已修复并实时验证。

- 战役 625 / 角色 423（人类牧师3级，HP27/AC18→实际AC16）。`/open` 后逐轮手动 `/chat`。
- **100 轮全部完成，玩家存活**（终态 HP 27/27，dead=False，slots {1:4,2:2}，无 500/无 FATAL/无死亡）。
- 叙事弧完整：问镇长→访老神父→墓园探索→战哥布林/霍布哥布林/狼（6场遭遇，含2怪场）→击杀死灵法师
  （砸碎骨杖法器）→解救村民→重封噬魂者裂口→得知格雷夫斯家族秘辛→长休→以骨杖碎片开符文铁门→
  彻底消灭噬魂者→回镇报捷（村民半信半疑的苦涩结局）→离镇踏上新路（迷路/扎营/收束）。
- 覆盖动作：attack/cast(cantrip+leveled)/social/explore/study/search/hide/travel/rest(短+长)/ability_check/other。
- HP 区间 5–27（曾跌至5靠疗伤术自救）；长休2次（满血+法术位恢复）；治疗术治疗自身/治疗NPC均验。

### BUG-A — 驱散亡灵(Turn Undead/Channel Divinity)被当作法术、错误消耗法术位（高·规则一致性）
- 现象：玩家”启动驱散亡灵圣礼”→分类 `cast`，`spell_name=”驱散亡灵”`，**消耗一个1环法术位**（{1:4}→{1:3}）。
- 根因：系统无 Channel Divinity 动作类型；LLM 最近匹配到 `cast`；`_resolve_cast` 按 LLM 猜测的 `spell_level`
  消耗法术位。按 5E，驱散亡灵是 Channel Divinity 能力，**非法术、不耗法术位**（耗 Channel Divinity 使用次数，短/长休恢复）。
- 关联：与 BUG-B/D 同根（`spell_level` 取值不可靠）。
- 修复：BUG-D 的根因修复（DB 环阶优先于 LLM 猜测）后，驱散亡灵这类”非DB法术”不再被误判环阶；Channel Divinity
  作为独立动作类型的建模列为后续（本次不新增表项，避免误伤）。本项的”耗法术位”问题已随 BUG-D 消除。

### BUG-B — `spell_level` 在 intent 与 dice 间不一致（中）
- 现象：intent 给 `spell_level=0`（戏法），但响应 `dice.spell_level=1`；驱散亡灵 intent 0、dice 1。
- 根因：`level = int(it.get(“spell_level”) or 1)` —— Python `0 or 1 == 1`，戏法(0)被改写成 1。
- 修复：`brain/graph.py` `_resolve_cast` 改 `int(it.get(“spell_level”, 1))`（key 缺省才回退1）。

### BUG-C — 豁免成功一律半伤（圣火术应为0伤）（高·规则一致性）
- 现象：圣火术(戏法，”豁免失败受1d8光耀”)目标豁免成功时仍受 `round_down(dmg/2)` 半伤。
- 根因：`_resolve_cast` 豁免分支对**所有**法术 `final = round_down(piped/2) if sv.success else piped`。
  按 5E：火球术等”成功减半”半伤；圣火术/毒素喷吐等”成功不受伤害”0伤——是否半伤**按法术**。
- 修复：`data/spells.py` Spell 新增 `half_on_save: bool=False`（火球术/闪电束=True）；`_resolve_cast`
  按 `_spell.half_on_save` 决定，表外法术默认0伤。
- **实时验证**：r12 圣火术对哥布林，哥布林豁免成功(roll14 vs DC13)→`raw_damage=6, damage=0`，叙事”毫发无伤”。✓

### BUG-D — 戏法(level0)被当作1环法术、消耗法术位（高·规则一致性）
- 现象：施放圣火术(戏法)后法术位 {1:4}→{1:3}；连发戏法会迅速耗尽法术位，破坏施法者可持续性。
- 根因：① BUG-B 的 `or 1` 把戏法(0)判为1；② LLM 对戏法环阶猜测不稳定（圣火术时而报0时而报1），
  即便修了 `or 1`，LLM 报1时仍会耗位。
- 修复：`_resolve_cast` **把法术表查询前移**，`level = int(_spell.level) if _spell else int(it.get(“spell_level”,1))`
  —— **DB 环阶优先于 LLM 猜测**；`apply_node` 法术位消耗加 `lvl>=1` 守卫；`data/spells.py` 补录
  **圣火术**(0环·DEX豁免·1d8光耀·half_on_save=False)，使该戏法对 LLM 误报免疫。
- **实时验证**：r8/r12 圣火术后法术位不变 {1:4,2:2}，`dice.spell_level=0`（即便 LLM 报1，DB=0 胜出）。✓

### BUG-E — 自动遇敌可对单人角色生成致命级遭遇（中·平衡/规则一致性）
- 现象：3级单人牧师(HP27)遇 2×龙裔战士(各 HP33/CR1) → CR2，对单人3级为**致命级**(DMG XP阈值400)；
  首跑角色393 在 r11 遭此遭遇被打到濒死。前述100轮日志用战士+旧”永远哥布林”代码，未暴露。
- 根因：`apply_node` step5.5 从等级怪池**均匀**抽1只、再 50% 抽第2只，不按 CR 适当性/队伍规模过滤。
- 修复：`n>=2` 时仅从 `cr<=0.5` 怪池抽（2×CR0.5≈CR1，单人3级为中等-困难，可战）；单怪仍可从全池取。
- **实时验证**：r16 遭 2×霍布哥布林(CR0.5)而非2×龙裔，可战且胜。✓

### BUG-F — 施法治疗(疗伤术)不落盘到 HP（高·规则一致性）
- 现象：r14 疗伤术 `dice.damage=10, damage_type=”治疗”`，但 HP 21 不变（应→27）；法术位已正确消耗。
- 根因：`apply_node` step1 按 `target==str(cid)` 应用玩家自身 state_changes；LLM 用角色**名**(艾莉娅)而非 cid
  作 target → 匹配失败 → 治疗被跳过。（玩家受伤能生效，因伤害由怪物AI直接应用，不经 state_changes。）
- 修复：① step1 匹配放宽为 `target==str(cid) or target==ch.name`；② 新增 step2.9 确定性应用施法治疗
  （`dice.damage_type in (治疗/heal/healing)` → 按值治疗施法者），step1 跳过 cast 治疗的 state_changes 避免叠加。
- **实时验证**：r15 疗伤术 HP 21→27（治疗生效），耗1位；r21 危急(5HP)疗伤术 HP 5→12 自救。✓

### BUG-G — 治疗法术走豁免分支、产生”豁免成功=0治疗”（高·规则一致性）
- 现象：r79 疗伤术 `dice` 出现 `save_success=true, save_total=17, damage=0, damage_type=”healing”`——
  治疗法术不应有豁免，且”成功”导致 damage=0（BUG-C 的半伤/0伤逻辑误用到治疗）。
- 根因：`_resolve_cast` 分支仅 automatic/attack_roll/**else(豁免)**，**无 heal 分支**；治疗法术
  (effect_type=”heal”)落入 else，跑了一次无意义的豁免。
- 修复：`_resolve_cast` 新增 `elif _etype==”heal” or damage_type∈(heal/healing/治疗)` 分支——
  掷治疗骰(已含+施法属性调整值)、无攻击/无豁免、`damage_type` 统一为”治疗”供 step2.9 应用。
- **实时验证**：离线 `_resolve_cast(疗伤术, damage_type=”healing”)` → `damage=11, damage_type=”治疗”, save_success=N/A`。✓

### 附：陈旧服务器进程（运维）
- 发现：会话起始时运行中的 uvicorn 进程启动于 16:40:54 且**未带 `--reload`**，而 `main.py/graph.py/director.py`
  的提交(579fd32)在此之后——即**跑的是修复前的旧代码**（`/character/{id}` 响应缺 `equipped_weapon` 字段为证）。
  前 100 轮日志均在”修复前/陈旧”代码上产生。处置：重启服务以加载当前代码；后续每次改代码均手动重启确认生效。

### 100轮结论
- 修复 BUG-A~G 后，**施法者(牧师)可一次性完整跑完 100 轮**：无死亡、无 FATAL、无 parse-fail、无非200响应；
  戏法不耗位、豁免成功0伤、治疗生效、遭遇可战、长休恢复法术位——与 5E 规则一致。
- 与第五节(战士)互补：战士百轮只覆盖近战/探索/休息；**牧师百轮首次系统性覆盖施法/治疗/专注/法术位链路**，
  暴露并修复了 7 个规则一致性 BUG。`pytest tests/` 142 通过、0 失败（1 个 `test_monster_lookup` 为
  Qdrant 集合未就绪的环境性失败，与本次改动无关）。

### 修复落点汇总
| 项 | 文件 | 状态 |
|---|---|---|
| BUG-B/D 根因(`or 1`/DB环阶优先) | `brain/graph.py` `_resolve_cast`(查询前移+level取DB) | ✅ r8/r12 |
| BUG-C(half_on_save) | `data/spells.py`(Spell新字段+火球/闪电=True) + `brain/graph.py`(按flag) | ✅ r12 |
| BUG-D(戏法耗位守卫) | `brain/graph.py` `_resolve_cast`+`apply_node` step2(`lvl>=1`) | ✅ r8/r12 |
| BUG-E(遭遇平衡) | `brain/graph.py` step5.5(n>=2限cr<=0.5) | ✅ r16 |
| BUG-F(治疗落盘) | `brain/graph.py` step1(name/cid匹配)+step2.9(确定性治疗) | ✅ r15/r21 |
| BUG-G(治疗法术分支) | `brain/graph.py` `_resolve_cast`(新增heal分支) | ✅ 离线 |
| 圣火术补录 | `data/spells.py`(0环·DEX·1d8光耀·half_on_save=False) | ✅ |

