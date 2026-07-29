# 流程对照矩阵：规则书基准 vs aidm 实际流程

> 目的：逐环节对照 D&D 5E 2024 规则书标准流程与 aidm 实际实现，标注差异与严重度，作为阶段 B 修复依据。
> 基准来源：`data/rules_text/玩家手册2024/进行游戏/` + `data/rules_text/城主指南2024/2.运作游戏/`，参照根目录《DND5e完整游玩流程指南.html》。
> aidm 来源：`src/aidm/brain/graph.py` 管线、`src/aidm/api/main.py` + `api/ws.py`、各 brain 模块。

## 一、规则书基准流程骨架

### 1. 核心游戏循环（三支柱统一）
1. **DM 描绘场景**（环境/氛围/可感知选项）
2. **玩家声明行动**（想做什么、怎么做）
3. **DM 判定**（判定四问：D20 检定合理吗？→ 类型（属性检定/豁免/攻击）→ 用哪个属性 → DC 多少（10 易 / 15 中 / 20 难））——**仅当结果不确定且有后果时才掷骰**，否则直接叙述结果
4. **DM 叙述结果**（后果 → 新场景 → 回到 1）

### 2. 战斗时序
1. **确定位置**（DM 描述参战者位置、环境）
2. **突袭判定**（2024 版：察觉方对隐匿方，被突袭者先攻检定劣势，不再跳回合）
3. **掷先攻**（所有参战者 d20+Dex，排序）
4. **回合循环**（每回合：移动+动作+附赠动作；DM 叙述伤势——浴血=半血以下、强项弱点显露）
5. **战斗结束**（一方倒下/逃跑/投降）

### 3. 探索流程
- **时间尺度**：轮（战斗）/ 分钟（地城房间级）/ 小时（野外旅行）/ 日（长途）
- **旅行步调**：快速/中速/慢速，影响每日里程与感知/隐匿优劣势
- **随机遭遇**：通常**每日 2 次**检定；遭遇**不一定是战斗**——可能是环境事件、文明痕迹、生物足迹、追逐
- **导航**：感知(生存) 对抗地形 DC，失败迷路

### 4. 社交流程（态度四步）
1. DM 设定 NPC 起始态度（友好/中立/敌对）
2. 玩家陈述方式与内容
3. DM 判定是否需检定（魅力系，DC 随态度）
4. 叙述结果，态度随成功/失败累积移动

### 5. 休整与奖励
- 短休 1 小时（生命骰回血）、长休 8 小时（全恢复，每 24 小时一次）
- **英雄激励**：DM 对出色扮演/契合性格特点的行动奖励激励（2024 版可重掷一次 d20）

## 二、aidm 实际流程

每轮一次 `/chat`（或 WS `action`）走 LangGraph 线性管线：

```
classify(Director 意图分类) → retrieve(RAG 规则检索) → verify(规则校验)
  → {confirm(HITL) | retrieve_retry | resolve} → resolve(确定性掷骰)
  → narrate(LLM 叙事+三层记忆) → apply(状态应用+持久化+遇敌)
```

- 探索/旅行：`resolve` 内导航检定+步调+被动察觉；`apply` step5.5 随机遇敌
- 社交：`brain/social.py` 模块存在（NPC 态度/DC/累积），**未接入 graph 管线**（graph.py 全文无 social_interaction 引用）
- 战斗：玩家 start_combat 或 apply 遇敌触发；怪物回合在 apply 内自动执行
- 休整/升级/战利品/据点：各自独立模块，经 intent 分类进入对应 resolve 分支

## 三、逐环节对照矩阵

严重度：P0=破坏叙事正确性/规则正确性；P1=明显偏离桌面体验；P2=优化项。

| # | 环节 | 规则书流程 | aidm 流程 | 差异 | 严重度 |
|---|------|-----------|-----------|------|--------|
| 1 | 遇敌时机 | DM 先知晓遭遇再描述场景，叙事一致 | 遇敌在 `apply` step5.5（narrate 之后）判定，narration 已写完再硬拼"【遭遇】…向你扑来" | 叙述自相矛盾：前文还在说"街道安宁"，后文突然遇敌（PLAYTEST_FINDINGS BUG#6） | **P0** |
| 2 | 遇敌场景适配 | DM 按当前场景选遭遇（镇内不会刷野外哥布林） | `apply` step5.5 直接 `pick_encounter_pool(ch.level)`，不读 Scene.location/environment | 镇内刷野外怪，场景违和（BUG#6 伴随问题）；Scene 模型无场景类型字段 | **P0** |
| 3 | 攻击目标确定 | DM 明确玩家攻击哪个目标，伤害确定性地落到该目标 | classify 只输出 `target_name`（自由文本）；扣血依赖 narrate LLM 输出 `state_changes` 复述选择目标 | LLM 选错/编造目标 → narration 谎报击杀、血扣错人（PLAYTEST_FINDINGS BUG#5） | **P0** |
| 4 | 遭遇频率 | 通常每日 2 次随机遭遇检定 | `random_encounter_check` 在**每个探索类动作后**掷 d20≥18（15%） | 频率失控：100 轮约 6-7 场遭遇，探索变战斗串烧；`exploration.py` docstring 自述"每日 2 次"但实现是每动作 | **P1** |
| 5 | 遭遇类型 | 遭遇不一定是战斗：环境事件/痕迹/追逐/NPC | 触发即选怪开战（`_resolve_start_combat`） | 所有遭遇强制战斗化，丢失非战斗遭遇的叙事空间 | **P1** |
| 6 | 遭遇检定一致性 | 一次判定一个结果 | `resolve` travel 分支掷一次 `random_encounter_check`（仅作 narrate 参考），`apply` step5.5 再掷一次（实际生效） | 双重检定结果可矛盾：resolve 说"有动静"，apply 未触发（或反之） | **P1** |
| 7 | 战斗开场叙述 | 确定位置 → 突袭判定 → 先攻，三段分明 | `start_combat` 直接掷先攻开战；突袭劣势已在 `roll_initiative` 实现但**无叙述环节**，位置描述缺失 | 玩家看不到"谁先察觉谁"，先攻序列凭空出现 | **P1** |
| 8 | 探索时间推进 | 轮/分钟/小时/日尺度消费；长休按 24h | graph 无 game_time 概念；Scene.time 只是自由文本（"白天/夜晚"），无推进逻辑 | 旅行不耗时、长休无 24h 约束依据、法术持续时间无锚点 | **P1** |
| 9 | 社交流程 | 态度四步，魅力检定随态度定 DC | `_resolve_social` 已接入管线（social_mod.NPC/check_social_dc/update_attitude + apply 2.7 持久化跨回合累积） | **已对齐**（A2 初判误报：graph 未直接调 `social_interaction` 函数，但态度状态机经 `_resolve_social` 完整生效） | — |
| 10 | 判定时机 | 仅结果不确定且有后果才掷骰 | 每个非 other 动作都走 retrieve→verify→resolve 全管线 | 纯对话/自由扮演也被全量规则校验+可能强行掷骰，节奏拖沓 | **P2** |
| 11 | 英雄激励 | DM 对出色扮演奖励激励（2024：重掷一次 d20） | 无激励字段/机制 | 缺失奖励循环 | **P2** |
| 12 | 伤势叙述 | DM 描述浴血（半血）、强项弱点显露 | narration 有 HP 数值但无浴血/弱点叙述规范注入 | DM 叙事缺战斗反馈层次 | **P2** |

## 四、修复计划映射（阶段 B）

| 矩阵 # | 修复项 | 计划任务 |
|--------|--------|----------|
| 1, 2, 6 | 遇敌判定前移到 narrate 之前 + 场景过滤 + 消除双重检定 | B1 |
| 3 | classify 输出 target_cid，apply 确定性扣血 | B2 |
| 7 | 战斗开场输出突袭判定+先攻序列事件，narrate 按序叙述 | B3 |
| 4, 5, 8, 9, 10, 11, 12 | 遭遇时钟/非战斗遭遇/时间推进/社交接入/轻管线/激励/伤势叙述 | B4（按 P1→P2 增量） |

## 五、修复记录（阶段 B 回填）

- **B1（矩阵#1/#2/#6，BUG#6）已修复**：遇敌判定从 `apply_node` step5.5 前移到 `resolve` 的 `_with_encounter`（narrate 之前），触发即 `_resolve_start_combat` 并把 combat 快照 merge 进 state，narrate 按「遭遇出现→先攻→对峙」叙述；`_scene_blocks_encounter` 场景过滤（镇内/室内关键词抑制野外遭遇，野外词优先）；travel 分支删除自带 `random_encounter_check`（消除双重检定）；开战回合 apply 不 advance_turn（先攻首位不被跳过，先攻高于玩家的怪物立即行动）。探针 `scripts/probe_encounter_flow.py` 6/6 通过；pytest 143 全绿。
- **B2（矩阵#3，BUG#5）已修复**：`director._resolve_target_cid` 在 classify 后把 target_name 确定性匹配到参战者 cid（cid精确→name精确→互含→唯一存活敌人）；`graph._with_target_outcome` 在 resolve 预判击杀写入 dice（target_cid/target_hp_before/target_killed），narrate 注入【击杀确认】/【伤害确认】指令；apply 新增 3a-target 按 target_cid 确定性扣血（attack 类跳过 LLM 所有敌方复述，cast 仅跳同目标保留 AoE 分支）；顺带修复治疗法术被兑底误扣敌方血（_HEAL_TYPES 排除）。探针 `scripts/probe_target_cid.py` 5/5 通过；pytest 143 全绿。
- **B4（矩阵#4/#5/#8/#10/#12）已修复**：
  - #8 时间推进：`_advance_game_time`（存 Campaign.world_flags.game_minutes，默认第1日08:00起），travel 1h/explore 30min/search·study·ability_check 10min/rest 短休1h·长休8h，dice.time 输出 day/clock，narrate 注入【时间推进】提示；
  - #4 遭遇时钟：`_encounter_clock_allows` 每 4 游戏小时最多 1 次检定（对齐“每日 2 次”，world_flags.encounter_last_check_min），杜绝每动作 15% 的频率失控；
  - #5 非战斗遭遇：`_encounter_type`（d20：combat 50%/environment 25%/omen 20%/npc 5%），非战斗遭遇不开战、写 prompt_hint，narrate【非战斗遭遇】指令织入叙述；
  - #10 轻管线：build_graph classify 改条件边（route_action：other/end_combat 直接 resolve，跳过 retrieve/verify 重管线）；
  - #12 伤势叙述：narrate 检测敌方半血以下注入【伤势叙述】浴血提示（不透露具体 HP）；
  - #9 经核实为**已对齐**（社交态度状态机经 `_resolve_social` 完整接入，A2 误报已修正）；
  - #11 英雄激励**暂缓**：需 Character 表结构迁移（加 inspiration 列），列入后续迭代；
  - 探针 `scripts/probe_exploration_clock.py` 6/6 通过。
- **B5 回归验证**：pytest 143 全绿；4 个探针全过（probe_encounter_flow 6/6、probe_target_cid 5/5、probe_combat_opening 4/4、probe_exploration_clock 6/6，B1/B3 探针已适配 B4 新增遭遇类型骰）。
- **B3（矩阵#7）已修复**：`_resolve_start_combat` 新增 `_determine_surprise` 突袭判定（intent.surprise 显式指定 > 自动判定：敌方隐匿 d20+最高 dex vs 玩家被动察觉 10+wis），被突袭方 `Combatant.surprised=True` 由 `roll_initiative` 施加先攻劣势（2024 规则）；dice 显式输出 surprise 判定结果与先攻序列（含 surprised 标记）；narrate 统一【战斗开场】指令按「遭遇→突袭→先攻→对峙」叙述（遇敌与主动开战两路径，encounter 内嵌 surprise）。探针 `scripts/probe_combat_opening.py` 4/4 通过；pytest 143 全绿。

## 六、D4 浏览器实测修复记录（阶段 D 回填）

全链路实测（战役 #913：建卡→开场→社交→施法→休息→探索→战斗闭环）中发现并修复：

1. **场景地点永不迁移（矩阵#13 补遗，P1）**：`Scene.location/npcs` 自开场后从不更新，导致玩家离开城镇后 `_scene_blocks_encounter` 仍按「镇内」永久抑制遭遇、且残留 NPC 使模式恒为 social。修复：`GameState` 增加 `location_change` 字段，narrate prompt 要求输出 `location_change`（仅地点实际改变时非空），`apply_node` 5b 迁移场景（`sc.location` 更新、`environment` 清空、`set_npcs([])`——注意 `Scene.npcs` 为只读 property 须用 `set_npcs`）。
2. **管线异常致前端永久 busy（P1）**：`ws.py on_action` 无异常兜底，LLM/管线抛错时不发 `result`，前端锁死。修复：try/except 兜底发送错误占位 result（`dice.kind="error"`）。
3. **参战者 HP 载荷缺失（P1）**：REST `/combat/{cid}`、`/campaign/{cid}/state` 与 WS `connect`/`combat_update` 的 `initiative_order` 均缺 `hp/hp_max/dead/surprised`，前端 HP 卡显示 0/? 并误判死亡。修复：`ws.py` 新增 `_combatant_payload` 统一三处载荷，`main.py` 两处端点同步补齐。
4. **战斗软锁：怪物回合停在尸体上（P0）**：`graph.py` 怪物回合循环遇 `dead/hp<=0` 的参战者直接 `break`，回合永远停在尸体、玩家再无回合。修复：改为 `advance_turn` 跳过尸体（带 skip guard 防死循环）。
5. **v2 布局栅格塌陷（P0 前端）**：原型 v2 的 `grid-template-areas` 中 `topbar` 为 L 形非矩形区域（`"topbar topbar"/"party topbar"/"stage panel"`），整条声明按 CSS 规范无效，所有 `grid-area` 引用失效导致布局塌陷；该 bug 随移植带入 `globals.css`。修复：改为矩形分解 `"topbar topbar"/"party panel"/"stage panel"`（视觉不变，panel 自顶栏下方纵跨两行）。

回归：pytest 143 全绿；截图证据 `docs/shots/d4_game_main.png`（探索态）、`docs/shots/d4_game_combat.png`（战斗态：先攻条/突袭标记/浴血 HP 卡/骰卡/击杀伤害卡）。
