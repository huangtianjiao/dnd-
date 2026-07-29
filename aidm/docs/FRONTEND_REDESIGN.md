# 前端重设计（FRONTEND_REDESIGN）

> 版本：v2 · 配套交互原型：`d:\game\dnd\DND5e_UI_交互原型_v2.html`（单文件、可点击、含模拟数据）
> 依据：阶段 A/B 流程对齐结果（见 `docs/FLOW_ALIGNMENT.md`）、`docs/FRONTEND_BACKEND_AUDIT.md` 前后端审计
> 原则：**不沿用旧组件样式**，仅保留其数据接口与 REST/WS 对接关系；布局以原型 v2 为唯一视觉基准。

---

## 0. 设计基线

| 项 | 结论 |
|---|---|
| 布局流派 | AI DM 产品（Friends & Fables / AI Dungeon / NovelAI）的「**聊天叙事中心 + 角色状态侧栏**」为骨架；战斗时叠加战术层（先攻条 + 参战者 HP 卡）。不采用 Foundry/Roll20 的地图画布中心（那是为真人 DM 操作地图设计的）。 |
| 主舞台 | 叙事流是唯一的"游戏画面"：DM 叙述、玩家发言、骰子结果、伤害提示、怪物回合全部按时间轴流入同一滚动列。 |
| 3D 骰子 | 保留 `@3d-dice/dice-box`，作为全屏动画层覆盖在主舞台之上，掷骰落定后结果落入叙事流成为骰子卡。 |
| 多人 | 队伍条常驻顶栏下方：在线玩家头像 + HP 微条 + 当前行动者高亮。 |
| 旧版关系 | 旧 32 组件 + 1079 行 `page.tsx` 全部退役；仅 FeatDialog / LootPanel / RoomPanel / RestDialog / OpeningConfirm / HITLDialog 等"流程弹窗"保留逻辑、重做样式。 |

阶段 B 后端新增数据 → UI 消费点（本次设计必须落地）：

| 后端新增（B 阶段） | 载体 | UI 消费 |
|---|---|---|
| 遇敌前移 + 突袭判定 | `result.dice.encounter`（`combat_started` / `surprise` / `initiative_order[].surprised`） | 战斗开场事件卡序列 + 先攻条"突袭"标记 |
| 攻击目标确定性 | `result.dice.target_cid` / `target_name` / `target_killed` | 伤害浮卡的击杀徽标、DM 叙述一致性 |
| 游戏内时间推进 | `result.dice.time`（`day` / `clock`） | 顶栏游戏内时钟 + 时间推进事件卡 |
| 遭遇时钟/非战斗遭遇 | `result.dice.encounter.suppressed` / `type` | 叙事事件卡（环境征兆/NPC 遭遇不开战） |
| 浴血叙述 | narration 内文（后端已注入提示） | 参战者卡"浴血"角标（hp×2≤hp_max 前端派生） |

---

## 1. 布局规格

### 1.1 栅格（桌面 ≥1100px）

```
grid-template-rows: 52px 44px 1fr
grid-template-columns: 1fr 340px        ← 右栏折叠时 1fr 0px
┌──────────────────────────────────────────────┐
│ TopBar                                   52px│
├──────────────────────────────────────────────┤
│ PartyBar                                 44px│
├───────────────────────────────────┬──────────┤
│ CombatBar（仅战斗模式，~110px）    │          │
├───────────────────────────────────┤ SidePanel│
│ NarrativeStream（滚动，max-w 760） │  340px   │
├───────────────────────────────────┤ 4 标签页 │
│ QuickChips（横向滚动，~36px）      │          │
├───────────────────────────────────┤          │
│ ActionInput（~64px）               │          │
└───────────────────────────────────┴──────────┘
```

- `<1100px`：SidePanel 变为右侧 drawer（`position:fixed`，box-shadow），默认折叠。
- `<720px`：隐藏时钟与演示开关文案，叙事列内边距收窄。

### 1.2 区域职责

| 区域 | 内容 | 数据源 |
|---|---|---|
| **TopBar** | 菜单☰ · 战役名 · 模式徽章（探索/社交/战斗）· 游戏内时钟 · 面板开关 | scene / combat / dice.time |
| **PartyBar** | 队友头像+名+在线点+HP 微条；战斗中当前行动者金框+「行动中」角标；右侧"轮到 X"提示 | WS join/leave/players + character_update |
| **CombatBar** | 先攻条（init 降序 chips：当前金框高亮、已行动半透明、突袭标记）+ 参战者 HP 卡横排（浴血角标/死亡灰化）+ 轮次 | WS combat_update |
| **NarrativeStream** | 5 类消息气泡（见 1.3），底部锚定自动滚动 | WS result / monster_action / 本地输入 |
| **QuickChips** | 按模式与情境出现：探索（搜索/潜行/聆听/地图/短休/长休）、社交（说服/欺瞒/威吓/洞悉/打探）、战斗（攻击/施法/闪避/撤离/药水） | 本地配置 + known_spells/药水存量 |
| **ActionInput** | 自由文本行动声明（Enter 发送）+ 自由掷骰按钮 | WS action emit |
| **SidePanel** | 标签页：角色卡 / 法术书 / 物品栏 / 规则速查 | REST character、inventory、spells |

### 1.3 叙事流消息类型（5 种气泡）

| 类型 | 样式 | 触发 |
|---|---|---|
| DM 叙述 | 左侧金色书脊引文式，衬线 15.5px/1.85 | `result.narration` |
| 玩家发言 | 右侧暗金气泡（≤78% 宽） | 本地发送即时上屏；他人经 `result` 前缀【玩家名】 |
| 骰子结果卡 | 居中横卡：六边形面 + 标题 + 算式 + 判定徽标（命中/未中/重击） | `result.dice`（按 `kind` 分派文案） |
| 伤害/治疗浮卡 | 居中胶囊：红=伤害 / 绿=治疗，`+/-数值`，可带「击杀」徽标 | `dice.damage` / `target_killed` / 治疗类 |
| 事件卡 | 居中虚线灰卡；战斗事件红虚线（怪物回合）；时间事件居中衬线 | `monster_action`、场景/时间推进、`combat_end` |

### 1.4 模式指示

模式为**前端派生态**（无后端字段）：`combat.active` → 战斗；否则默认探索；社交仅作为叙事语境徽章（scene.npcs 存在且最近 3 条消息无骰子时显示，可后续迭代）。模式决定：徽章颜色、CombatBar 显隐、QuickChips 集合。

---

## 2. 组件树（新建，样式全部重写）

```
app/page.tsx                      仅布局组合 + 阶段路由（onboarding → game）
app/components/
  layout/
    TopBar.tsx                    战役名/模式徽章/游戏时钟/菜单/面板开关
    PartyBar.tsx                  队伍条（HP 微条/回合高亮/在线点）
    SidePanel.tsx                 右栏容器：标签页切换 + 折叠
  stage/
    CombatBar.tsx                 战斗层容器（先攻条 + 参战者卡 + 轮次）
    InitiativeChip.tsx            先攻 chip（当前/已行动/突袭标记）
    CombatantCard.tsx             参战者 HP 卡（浴血/死亡）
    NarrativeStream.tsx           叙事流容器（消息数组渲染、自动滚底）
    messages/
      DmMessage.tsx               DM 书脊引文气泡
      PlayerMessage.tsx           玩家气泡
      DiceCard.tsx                骰子卡（移植 useSocket.formatDice 分派逻辑）
      HarmCard.tsx                伤害/治疗浮卡（击杀徽标）
      EventCard.tsx               系统/怪物回合/时间事件卡
    QuickChips.tsx                情境快捷行动（模式→chips 映射）
    ActionInput.tsx               输入框/掷骰钮/发送钮
  panel/
    CharacterSheetTab.tsx         HP/AC/六属性/技能/法术位/生命骰/死亡豁免/状态/同调/专长
    SpellbookTab.tsx              按 known_spells 过滤 + 环阶分组 + 展开描述 + 一键声明施展
    InventoryTab.tsx              装备中/背包/同调位（attune/break/equip-weapon）
    RuleLookupTab.tsx             规则速查（阶段1 静态卡；阶段2 接 RAG 查询）
  dice/
    DiceLayer.tsx                 @3d-dice/dice-box 挂载层（全屏 fixed）
  overlays/（流程弹窗：逻辑保留，样式重做）
    OpeningConfirm.tsx  FeatDialog.tsx  RestDialog.tsx  HITLDialog.tsx
    LootPanel.tsx       RoomPanel.tsx   RoomInfoModal.tsx
app/hooks/
  useSocket.ts                    保留（事件分发已对齐，见 §4）
  useGameState.ts                 新增：会话/战役/场景/消息流/模式/choices
  useCombat.ts                    新增：combat 状态/先攻/当前回合/怪物回合事件
  useCharacter.ts                 新增：角色卡 + character_update 防抖重取
```

---

## 3. 状态分层

| 层 | 内容 | 权威来源 | 更新方式 |
|---|---|---|---|
| **Server state** | 角色卡（HP/法术位/物品/同调/生命骰/死亡豁免） | REST `GET /character/{cid}` | `result` / `character_update` → 防抖重取 |
| | 场景（location/time/npcs/exits…） | REST `GET /scene/{cid}` 初始化 | WS `scene_update` 覆盖 |
| | 战斗（round/initiative_order/current_turn） | REST `GET /combat/{cid}` 初始化 | WS `combat_update` 覆盖；`combat_end` 清空 |
| | 队伍成员 | WS `join`/`leave` 携带 players | 直接覆盖 |
| **本地 UI state** | 消息流（含本地即时上屏的玩家气泡） | 无（由 WS 事件+本地输入累积） | append-only |
| | 面板折叠/激活标签/输入草稿/菜单开合 | 无 | React state |
| | 骰子动画层显隐、typing 指示 | 无 | 时序控制 |
| | QuickChips 集合（由模式派生） | 派生 | 模式变化重算 |

原则：**数值一律以 server state 为准**；消息流是本地投影，刷新页面后经 `GET /campaign/{cid}/state` 的历史摘要重建。

---

## 4. WS 事件 → UI 更新映射表

### 4.1 后端 → 前端（15 事件，全部保留并落地到具体组件）

| 事件 | payload 关键字段 | 消费组件 | UI 变化 |
|---|---|---|---|
| `result` | `narration` / `dice` / `action_options` / `player` | NarrativeStream / QuickChips / DiceLayer | DM 气泡+骰子卡+伤害浮卡上屏；dice.d20→DiceLayer 动画；choices→chips；dice.time→TopBar 时钟+时间事件卡；dice.encounter→战斗开场卡序列；dice.target_killed→击杀徽标 |
| `scene_update` | `scene{location,time,environment,npcs,exits}` | TopBar / NarrativeStream | 战役名/场景徽章更新；场景变更事件卡 |
| `combat_update` | `active,round,current_turn,initiative_order[{name,init,side,hp,hp_max,surprised,dead}]` | CombatBar / PartyBar / 模式徽章 | 先攻条+参战者卡重渲；当前回合高亮；模式切战斗 |
| `character_update` | —（触发重取） | useCharacter → 右栏 4 标签页 + PartyBar HP | 防抖 300ms 重取 `GET /character/{cid}` |
| `monster_action` | `monster, action_result` | NarrativeStream（EventCard 红虚线） | 怪物回合事件内嵌叙事区 |
| `monster_turn` | `monster` | CombatBar | 先攻条对应 chip 高亮过渡 |
| `turn_advanced` | `next` | CombatBar / PartyBar | 当前行动者高亮 + "轮到 X" |
| `round_end` | `round` | CombatBar | 轮次徽标 +1 |
| `player_ready` | `player` | PartyBar / DM 控制提示 | 就绪勾选 |
| `combat_end` | `outcome` | CombatBar / NarrativeStream | 战斗层收起、模式回探索、结算事件卡 |
| `processing` | `player` | NarrativeStream | typing 指示（DM 正在判定） |
| `player_acting` | `player` | PartyBar | 他人行动中高亮 |
| `join` | `name, players[]` | PartyBar / NarrativeStream | 成员条刷新 + 加入事件卡 |
| `leave` | `name, players[]` | PartyBar / NarrativeStream | 成员条刷新 + 离开事件卡 |
| `error` | `message` | Toast（TopBar 下方浮层） | 错误提示 |

### 4.2 前端 → 后端（6 emit，全部保留）

| emit | 触发 UI | 说明 |
|---|---|---|
| `action` | ActionInput 发送 / QuickChips 点击 / 法术"一键声明" | 唯一行动入口 |
| `end_turn` | CombatBar「结束回合」按钮（轮到己方时显示） | 推进先攻 |
| `ready` | DM 控制（战斗开场集合阶段） | 广播 player_ready |
| `monster_turn` | DM 控制 | 单人 AI DM 模式下由后端自动驱动，前端仅显示 |
| `monster_action` | DM 控制 | 同上 |
| `combat_end` | DM 控制 | 强制收尾 |

---

## 5. REST 对接清单

> 审计基线 29 条调用（FRONTEND_BACKEND_AUDIT §2.1）；现行代码 37 个调用点 / 30 个唯一端点。下表按功能域归并，标注新组件归属。

| 功能域 | 端点（方法） | 新组件/Hook | 备注 |
|---|---|---|---|
| 车卡资料 | GET `/races` `/classes` `/backgrounds` `/spells` | onboarding（page 阶段） | 开局一次性拉取 |
| 战役 | POST `/campaign` · GET `/campaigns` · GET `/campaign/{cid}/state` | onboarding / useGameState | state 用于刷新重建 |
| 角色 | POST `/character` · GET `/character/{cid}` | useCharacter | 重取唯一入口 |
| 加入 | POST `/join` | onboarding（继续游戏/加入房间） | |
| 开场 | POST `/open`（预览+确认 2 调用点） | OpeningConfirm | |
| 场景/战斗初始化 | GET `/scene/{cid}` · GET `/combat/{cid}` | useGameState / useCombat | |
| 休息 | POST `/character/{cid}/rest` | RestDialog → QuickChips 唤起 | 短休/长休 |
| 会话 | POST `/session/end` | TopBar 菜单「保存进度」 | |
| 世界设定 | POST `/generate_setting` | onboarding | |
| 专长 | GET `/character/{cid}/available-feats` · POST `/character/{cid}/select-feat` | FeatDialog | 保留逻辑 |
| 物品/同调/装备 | GET `/character/{cid}/inventory` · POST `/character/{cid}/attune` · POST `/character/{cid}/break-attunement` · GET `/weapons` · POST `/character/{cid}/equip-weapon` | InventoryTab | 审计 P0 已修，迁入新标签页 |
| 房间 | GET `/rooms` · POST `/room/create` · POST `/room/join` · GET `/room/{id}` · POST `/room/{id}/kick` · POST `/room/{id}/transfer` | RoomPanel/RoomInfoModal | 入口移至 TopBar 菜单 |
| 据点 | GET `/strongholds/facilities` · POST `/stronghold/create` | StrongholdPanel → SidePanel 第5标签或菜单弹窗 | 样式重做 |
| 战利品 | POST `/loot/pool` · POST `/loot/distribute/v2` | LootPanel（战斗结算后弹出） | 保留逻辑 |
| 怪物查询 | GET `/monster/{name}` | MonsterInfoModal → CombatantCard 点击弹出 | 现成模态迁入 |
| 待接入增强（端点已存在，本次顺手接入） | GET `/players/{cid}`（队伍条 HP 补全）· GET `/summary/{cid}`（菜单-会话摘要，现 SummaryModal）· GET `/loot/history/{cid}`（LootPanel 历史页签）· GET `/magic-items`（InventoryTab 图鉴）· GET `/feats`（FeatsBrowser） | 见对应组件 | 审计 §2.2 孤立端点 |
| **待后端新增** | GET `/rules/query?q=`（包装 `knowledge/hybrid.retrieve`，返回带出处段落的 top-k） | RuleLookupTab | 阶段2；阶段1 用静态规则卡兜底 |

---

## 6. dice-box 接入规格

- `DiceLayer`：`position:fixed inset-0 z-100`，挂载点 `#dice-box`；初始化逻辑从旧 `page.tsx` 平移（`@3d-dice/dice-box`，`assetPath` 不变）。
- 触发：`result.dice` 含 `d20` 时 `box.roll(`${d20}d20`)`；动画期间叙事流暂缓落骰子卡，落定回调后再 append。
- 自由掷骰：ActionInput 左侧骰子按钮 → 本地 `box.roll("1d20")` → 仅本地骰子卡，不发后端。
- 战斗连掷（先攻序列/魔法飞弹多骰）：按 `dice.kind` 批量构造 roll 表达式。

---

## 7. 旧组件处置清单（32 个）

| 处置 | 组件 |
|---|---|
| **重构迁入新树**（逻辑参考、样式废弃） | CharacterPanel→CharacterSheetTab · SpellbookModal→SpellbookTab · InventoryPanel+WeaponEquip→InventoryTab · RulesReference→RuleLookupTab · NarrativeArea→NarrativeStream · CombatBox+InitiativeBar→CombatBar · PartyBar→layout/PartyBar · TopBar→layout/TopBar · PlayerInput→ActionInput · QuickActions→QuickChips · DiceRoller→DiceLayer · SceneBox→场景事件卡+TopBar · DeathSaveTracker+HitDiceTracker+ConditionTracker+SpellSlots→CharacterSheetTab 区块 · ActionLog→事件卡流 · ActionPanel→QuickChips 战斗集 |
| **保留逻辑、重做样式** | OpeningConfirm · FeatDialog · RestDialog · HITLDialog · LootPanel · RoomPanel · RoomInfoModal · MonsterInfoModal · StrongholdPanel · SummaryModal · FeatsBrowser · MagicItemsBrowser |
| **删除** | （无——全部有归属；TacticalGrid/DicePanel/ModeSwitcher 已在审计阶段删除） |

---

## 8. 实现偏差记录（D 阶段回填）

> 随 D1–D4 实施，逐条记录与本文档/原型的偏差及原因。

1. **文件粒度合并**：§2 组件树的 20+ 文件合并为 6 个——`hooks/useGameState.ts`（useCharacter/useCombat/useGameState 三 hook 同文件）、`components/v2/chrome.tsx`（TopBar/PartyBar/SidePanel）、`components/v2/stage.tsx`（CombatBar/NarrativeStream/QuickChips/ActionInput，InitiativeChip/CombatantCard/5 种气泡作内部组件）、`components/v2/tabs.tsx`（4 个标签页）、`components/v2/DiceLayer.tsx`、`page.tsx`。导出接口与 §2 一致，仅物理分文件不同。
2. **休息改走 WS action 管线**：QuickChips 的短休/长休直接发送自然语言行动（如「我们在此扎营短休一小时」），由后端管线产生时间推进卡+DM 叙述；REST `/character/{cid}/rest` 与 RestDialog 不再挂载（§5 表中「RestDialog → QuickChips 唤起」修正）。
3. **服务器结果骰用 CSS d20**：`result.dice.d20` 已由服务器确定，DiceLayer.play(face) 用 CSS 动画落定到该确切值，保证动画与裁决一致；dice-box 仅用于自由掷骰 rollFree（§6 的 `box.roll(`${d20}d20`)` 方案不适用——dice-box 无法指定落定值）。骰子卡不再等动画落定回调，与动画并行入流（busyRef 防连掷重入）。
4. **dice-box 挂载点改名**：`#dice-box` → `#v2-dice-box-host`（v2- 前缀统一），assetPath/scale 不变。
5. **模式派生规则落地**（§1.4）：`combat?.active → combat`；否则 `scene?.npcs?.length > 0 → social`；否则 `explore`。
6. **法术位渲染简化**：后端 `/character/{cid}` 仅返回各环剩余数（无 max），法术位按「N 环 剩余 X」文本行渲染，不用 pips（原型为 pips）。
7. **角色卡省略区块**：后端无技能列表/施法属性/施法 DC 数据，对应区块省略；被动察觉由前端派生 `10 + 感知调整值`。
8. **旧组件实物删除 2 个**：`InitiativeBar.tsx`、`CombatBox.tsx` 因 `Combatant.initiative_order` 类型变更（字段 `initiative`，旧码用 `init`）无法编译，实物删除；§7 表中其余「重构迁入」旧文件保留在 `components/` 但已无任何引用（不挂载即无样式冲突，后续清理）。
9. **战斗连掷简化**：先攻序列等多骰场景不批量构造 dice-box 表达式，逐张骰子卡+CSS 动画（busyRef 跳过重入动画直接落卡）。
10. **globals.css 全量重写**：旧游戏屏样式块（game-screen/top-bar/left-panel/narrative/init-card 等 30+ 类）经 grep 确认无保留组件引用后删除；保留浅色 `:root` 变量与工具类/Modal/SpellCard 供 onboarding 与 12 个 overlay 组件；新增 `--v2-*` 暗色变量与全套 `v2-` 前缀样式（滚动条样式限定 `.v2-app` 内，避免污染浅色屏）。
11. **修正原型栅格 bug（偏离原型，D4 实测发现）**：原型 v2 的 `grid-template-areas: "topbar topbar"/"party topbar"/"stage panel"` 中 `topbar` 为 L 形非矩形区域，整条声明按 CSS 规范无效→布局塌陷。实现改为矩形分解 `"topbar topbar"/"party panel"/"stage panel"`，视觉效果与原型意图一致（panel 自 52px 顶栏下方纵跨队伍条与舞台两行）。
