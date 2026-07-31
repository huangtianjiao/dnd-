# AIDM — DND 5e AI 跑团系统 · 游戏流程总文档

---

## 一、系统概述

### 1.1 项目定位

AIDM 是一个 D&D 5E 电子跑团系统，核心理念为 **"叙事交给 LLM，规则判定交给代码"**。

LLM 只在"理解玩家意图"和"叙事生成"两端活动，中间所有掷骰、数值计算、状态变更均由确定性代码执行，确保规则判定的公平性与一致性。

### 1.2 技术架构

系统采用六层架构设计：

```
前端交互层 (Next.js 14 + React 18 + Tailwind CSS + Zustand)
    ↓ HTTP REST (39个端点) / WebSocket (Socket.IO)
API 接口层 (FastAPI, 端口 8080)
    ↓
AI DM 大脑 (LangGraph StateGraph 8节点编排)  ←→  规则知识库 (RAG, Qdrant三集合, BM25+向量混合检索)
    ↓
引擎层 (确定性代码, 21个模块)
    ↓
状态层 (SQLite 持久化, SQLModel ORM)
```

**技术栈选型：**

| 组件 | 技术选型 |
|------|----------|
| LLM | deepseek-v4-flash (via senseaudio 网关, OpenAI 兼容协议) |
| LLM 编排 | LangGraph (StateGraph + SqliteSaver checkpointer) |
| Embedding | 本地 bge-small-zh-v1.5 (512维) |
| 向量库 | Qdrant 本地文件模式 (免 Docker) |
| API | FastAPI + python-socketio |
| ORM | SQLModel (Pydantic + SQLAlchemy) |
| 状态库 | SQLite 单文件 |
| 前端 | Next.js 14 + React 18 + Tailwind CSS + Zustand |
| 3D骰子 | @3d-dice/dice-box |

### 1.3 源码结构

```
src/aidm/
├── engine/       # 引擎层 (21个核心模块, 8085行)
├── brain/        # LangGraph 编排层 (21个业务模块, 12159行)
├── agents/       # 多智能体 (Director/RuleJudge/Narrator/EnemyAI等, 7个模块)
├── data/         # 游戏数据表 (12个模块, 7532行)
├── knowledge/    # RAG 知识检索 (10个模块)
├── stats/        # 状态持久化 (models/store/npc/checkpoint, 4个模块)
├── api/          # FastAPI 接口 + WebSocket (routes/ + ws.py + main.py)
├── config.py     # pydantic-settings 配置
└── cli.py        # CLI 交互入口
```

---

## 二、完整游戏流程总览

### 2.1 从打开游戏到完整冒险的链路

```
玩家打开游戏
    ↓
主菜单 (6个入口)
    ├── 开始新游戏 → 角色创建(五步车卡法) → AI生成世界设定 → DM开场叙事 → 游戏主界面
    ├── 继续游戏 → 选择战役 → 恢复状态 → 游戏主界面
    ├── 加入游戏 → 输入战役编号 → 游戏主界面
    ├── 创建房间 → 多人房间
    ├── 房间列表 → 多人房间
    └── 以DM身份加入
```

### 2.2 核心游戏循环（对照 DND 5e 规则书）

**标准 DND 5e 循环：** DM描述 → 玩家行动 → DM裁定 → 掷骰(如需) → DM描述结果 → 循环

**AIDM 实现对照：**

| 标准 DND 5e 流程 | AIDM 实现 | 对齐度 |
|----------|-----------|--------|
| DM 描绘场景 | `world.open_campaign()` + `narrate` 注入场景上下文 | ✅ 已对齐 |
| 玩家声明行动 | `/chat` REST 或 WebSocket `action` 事件 | ✅ 已对齐 |
| DM 裁定判定方式 | `classify`(LLM意图分类) → `retrieve`(规则检索) → `verify`(校验) | ✅ 已对齐 |
| 掷骰 | `resolve`(纯代码硬性骰子，LLM不可绕过) | ✅ 已对齐 |
| DM 描述结果 | `narrate`(LLM叙事 + 三层记忆注入) | ✅ 已对齐 |
| 仅不确定时才掷骰 | `core_loop.py` 实现确定性分类（确定成功/不确定/不可能） | ✅ 已对齐 |

---

## 三、角色创建流程

### 3.1 五步车卡法（对照 PHB 2024）

| 步骤 | 内容 | 实现位置 |
|------|------|----------|
| Step 1: 选择职业 | 12核心职业 → 生命骰/主属性/豁免熟练/护甲武器熟练/施法属性 | `brain/char_create.py: step1_choose_class()` |
| Step 2: 选择起源 | 10种种族 + 16种背景 → 速度/体型/黑暗视觉/特质/起源专长/语言 | `brain/char_create.py: step2_choose_origin()` |
| Step 3: 分配属性 | 三种方式：标准阵列[15,14,13,12,10,8] / 购点法(27点) / 4d6弃最低 | `brain/char_create.py: step3_assign_ability_scores()` |
| Step 4: 选择阵营 | 九宫格阵营 | `brain/char_create.py: step4_choose_alignment()` |
| Step 5: 丰富细节 | 名字/外貌/性格 + 衍生数值自动计算 | `brain/char_create.py: step5_enrich_details()` |

### 3.2 衍生数值自动计算

- **1级HP** = 生命骰面值 + 体质调整值 (+矮人刚毅+1)
- **无甲AC** = 10 + 敏捷调整值 (野蛮人: 10 + 敏捷 + 体质)
- **先攻加值** = 敏捷调整值
- **熟练加值** = 2 + (等级-1) // 4
- **被动察觉** = 10 + 感知调整值 (+熟练加值 if 察觉熟练)
- **法术豁免DC** = 8 + 施法属性调整值 + 熟练加值

### 3.3 前端角色创建界面

- **数据预加载**：并行拉取 `/races`, `/classes`, `/backgrounds`, `/spells`
- **9个字段**：角色名/种族/职业/等级/子职/背景/阵营/六维属性/世界设定
- **4种属性分配方式**：标准阵列 / 购点法 / 掷骰(后端4d6去最低) / 自由输入
- **HP/AC 实时预览**
- **提交流程**：校验 → `POST /campaign` → `POST /character` → `POST /open` → 开场预览 → 进入游戏

---

## 四、LangGraph 编排管线（核心判定链）

### 4.1 八节点线性管线

LangGraph StateGraph 定义了 8 个节点的判定管线，实现在 `brain/graph.py` (585行)：

```
classify (LLM: Director Agent 意图分类 → 结构化 intent JSON)
    ↓ 条件路由
retrieve (Rule Judge: hybrid BM25+向量 RRF 检索规则)
    ↓
verify (Rule Judge: 关键词预检判定参数合规性)
    ├─ 校验驳回 → retrieve_retry (补关键词重检索) → resolve
    ├─ HITL 启用 → confirm (interrupt 让 DM 确认 y/n) → resolve
    └─ 通过 → resolve
resolve (纯代码骰子! 按 action_type 分派到 23 种动作处理器)
    ↓
narrate (LLM: 叙事 + 结构化 state_changes JSON + 3个行动选项)
    ↓
apply (持久化 HP/法术位/日志/summary + 战斗轮次推进 + 记忆处理)
    ↓ END
```

### 4.2 LLM 活动范围

LLM **只在三个节点**活动：

| 节点 | LLM 职责 | 不可绕过性 |
|------|----------|-----------|
| **classify** | 意图理解 — 将自然语言分类为23种结构化动作类型 | 输出结构化 JSON，下游代码校验 |
| **narrate** | 叙事生成 — 依据掷骰结果生成2-4句第二人称叙事 + 3个行动选项 | 掷骰结果已锁定，LLM 不可修改 |
| **confirm** | HITL 确认 — 让 DM 确认判定参数 (y/n) | 可选路径，DM 审批 |

**`resolve` 完全由确定性代码执行，LLM 不可绕过。**

### 4.3 23种动作类型分派

`resolve` 节点按 `action_type` 分派到不同的处理器（实现在 `brain/resolvers/` 子模块）：

| 类别 | 动作类型 | 处理方式 |
|------|----------|----------|
| 攻击类 | `attack`, `opportunity_attack` | `check.attack_roll` → `damage.roll_damage` (重击骰翻倍) |
| 施法类 | `cast` | 法术位检查 → 成分校验 → 效应结算(攻击/豁免/自动/治疗) |
| 技能类 | `ability_check`, `explore`, `hide`, `search`, `study` | `check.ability_check` vs DC |
| 战斗类 | `start_combat`, `end_combat` | `roll_initiative` + 持久化 |
| 战术动作 | `dash`, `dodge`, `disengage`, `help`, `ready` | 状态标记 (不掷骰) |
| 社交类 | `social` | NPC态度DC修正 + 技能检定 |
| 休整类 | `rest` | 短休: 生命骰恢复HP; 长休: 全恢复 |
| 成长类 | `levelup` | XP表 + 升级五步骤 |
| 旅行类 | `travel` | 旅行步调 + 导航检定 + 随机遭遇 |
| 物品类 | `use_item` | 治疗药水等物品效果 |
| 其他 | `grapple`, `shove` | 竞技检定 |
| 纯叙事 | `other` | 不掷骰，直接叙事 |

### 4.4 免检定机制

对 `ability_check` / `explore` / `search` / `study`，当 `needs_check=false` 时自动成功。这遵循 DMG 规则：**仅当结果不确定且失败有实质后果时才掷骰**。实现在 `engine/core_loop.py` (679行)。

---

## 五、战斗系统流程

### 5.1 战斗流程总览（对照 DND 5e 规则书）

| 标准 DND 5e 战斗流程 | AIDM 实现 | 对齐度 |
|----------|-----------|--------|
| 确定位置 | `Combatant.position` + `scene_context` | ✅ 已对齐 |
| 突袭判定 | `_determine_surprise()`（2024版：被突袭者先攻劣势） | ✅ 已对齐 |
| 掷先攻 | `roll_initiative()`（d20+敏捷，降序，同组怪物共用） | ✅ 已对齐 |
| 每回合：移动+动作+附赠+反应 | 完整动作经济追踪 | ✅ 已对齐 |
| 回合推进 | `advance_turn()`（跳过死亡/逃跑者，重置经济） | ✅ 已对齐 |
| 战斗结束 | `check_combat_end()`（区分玩家0HP与dead） | ✅ 已对齐 |

### 5.2 战斗状态机详解

`engine/combat.py` (1124行) 是战斗系统的核心，提供以下功能：

- **先攻**：d20 + 敏捷调整值，降序排列；同组怪物共用先攻；突袭者先攻劣势
- **回合推进**：每生物每轮一动作+附赠动作+反应+移动；`advance_turn()` 自动推进
- **动作经济**：`action_used` / `bonus_action_used` / `reaction_used` 精确追踪
- **移动系统**：速度(尺) → 格数转换，困难地形每尺2尺，穿过生物空间
- **专注维持**：受伤时 DC = max(10, 伤害/2) 的体质豁免
- **掩护**：半身 +2 / 四分之三 +5 / 全身不可选
- **擒抱/推撞(2024)**：目标豁免机制（非对抗检定）
- **传奇动作/抗性/充能**：完整实现

### 5.3 11种战斗动作

`engine/actions.py` (955行) 定义了 11 种战斗动作：

`attack` / `dash` / `disengage` / `dodge` / `help` / `hide` / `magic` / `ready` / `search` / `study` / `utilize`

### 5.4 多人战斗回合

`brain/combat_flow.py` (421行) 管理多人战斗回合：

- 服务端统一驱动回合推进，回合归属权为唯一真相
- 玩家行动只消耗动作经济，不隐式推进回合
- 怪物回合由 `run_monster_turn()` 自动结算
- 多人局需显式 `end_turn`；单人局自动推进

### 5.5 前端战斗界面

- **CombatBar**：先攻条(水平chip, 当前回合金色高亮) + 参战者HP卡(玩家蓝/敌方红) + 结束回合按钮
- **QuickChips**：攻击/施法/闪避/撤离/疾走/治疗药水快捷按钮
- **模式自动派生**：`combat.active` → combat模式; `scene.npcs` → social模式; 默认 → explore模式

---

## 六、规则判定系统

### 6.1 骰子引擎 (`engine/dice.py`, 342行)

- **RNG**：使用 `secrets` (密码学随机，非伪随机)，防止骰子可预测
- **优劣势**：掷2个d20取高/低；同时存在则抵消
- **重击**：天然20必命中 + 重击(骰数翻倍，常数不加倍)
- **天然1**：必失手
- 每次掷骰返回完整明细 (各骻值/加值/总计/模式) 供审计

### 6.2 检定系统 (`engine/check.py`, 269行)

- **属性检定**：d20 + 属性调整值 + (熟练加值 if 熟练) + 临时加值 ≥ DC
- **豁免检定**：同上，可主动放弃 (`waive` → 直接失败)
- **攻击检定**：d20 + 命中加值 vs AC；天然20必出+重击，天然1必失
- **DC公式**：施法豁免DC = 8 + 属性调整值 + 熟练加值
- **被动检定**：10 + 调整值合计；优势 +5 / 劣势 -5
- **范例DC表**：5(很容易) / 10(简单) / 15(中等) / 20(困难) / 25(很困难) / 30(几乎不可能)

### 6.3 伤害系统 (`engine/damage.py`, 368行)

- **结算管线**：免疫 → 数值修正 → 抗性(减半) → 易伤(翻倍) → 下限0
- **临时HP**：不叠加取较大者；受伤先扣临时HP
- **过量伤害致死**：HP降至0且余量 ≥ HP上限则立即死亡
- **13种伤害类型**完整覆盖：酸/冷/火/力场/光/闪电/暗蚀/毒素/ psychic/ 辐射/ 雷鸣/ 穿刺/ 钝击/ 挥砍

### 6.4 死亡豁免

- d20 ≥ 10 记成功
- 天然1 = 两次失败
- 天然20 = 恢复1HP + 计数归零
- 3次成功 = 稳定
- 3次失败 = 死亡
- HP0时受伤害追加失败（重击两次）
- 伤害 ≥ max_hp = 即死

### 6.5 状态条件 (`engine/conditions.py`, 358行)

覆盖 **15种状态 + 力竭**：

目盲 / 魅惑 / 耳聋 / 恐慌 / 受擒 / 失能 / 隐形 / 麻痹 / 石化 / 力竭 / 中毒 / 倒地 / 束缚 / 震慑 / 昏迷

**关键规则：**
- 状态不叠加（力竭例外，可累加至6级）
- 力竭累加：d20减值 = 等级×2，速度减 = 等级×5，6级即死
- 失能性状态：麻痹/震慑/昏迷/石化隐含失能
- 5尺内自动重击：麻痹/昏迷目标

### 6.6 法术系统 (`engine/spellcasting.py`, 1274行)

- 法术位消耗与升环
- V/S/M 成分校验
- 法术豁免DC = 8 + 施法属性调整值 + 熟练加值
- 法术攻击加值 = 施法属性调整值 + 熟练加值
- 长休恢复全部法术位
- 专注设置
- 效应类型：攻击 / 豁免 / 自动 / 治疗 四种分支
- 戏法不耗位
- 数据：12个硬编码法术 + 完整法术位进度表(1-20级)

---

## 七、探索与社交系统

### 7.1 探索系统 (`brain/exploration.py`, 1267行)

- 旅行步调：快速 / 正常 / 慢速
- 导航检定
- 被动察觉（自动触发）
- 随机遭遇

### 7.2 社交流程 (`brain/social.py`, 608行)

**四步社交互动循环：**

1. DM 扮演 NPC（口吻/表情/姿态，NPC 有自己的目标和态度）
2. 玩家角色扮演回应（描述意图和方法）
3. DM 判断是否需要掷骰（好的角色扮演可能自动成功）
4. 掷骰解决（说服/欺瞒/威吓/表演/洞悉检定）

**NPC 态度系统**：友好(-5 DC) / 冷漠(0) / 敌对(+5 DC)

### 7.3 旅行系统 (`engine/travel.py`, 122行)

- 旅行步调 + 导航检定 + 随机遭遇

### 7.4 休整期 (`engine/downtime.py`, 128行)

- 休整期活动处理

### 7.5 升级系统 (`brain/levelup.py`, 1156行)

- XP表 + 升级五步骤
- 等级段：1-4低 / 5-10中 / 11-16高 / 17-20史诗

### 7.6 休息机制 (`brain/rest.py`, 1071行)

- **短休**(1小时)：生命骰回血
- **长休**(8小时)：全恢复，24小时冷却
- **长休打断条件**：投先攻 / 施非戏法 / 受伤
- **力竭恢复**：长休 -1级

---

## 八、AI DM 系统

### 8.1 AI DM 在各阶段的角色

| 阶段 | AI DM 角色 | 实现位置 |
|------|-----------|----------|
| 开场 | 据世界设定生成完整背景+当前场景(地点/时间/多感官氛围/NPC/选项) | `brain/world.py: open_campaign()` |
| 意图理解 | 将玩家自然语言分类为23种结构化动作类型+参数 | `agents/director.py: classify_intent()` |
| 规则校验 | 检索规则原文校验LLM提出的判定参数，冲突驳回 | `agents/rule_judge.py: verify()` |
| 叙事生成 | 依据掷骰结果(不可改)生成2-4句第二人称叙事+3个行动选项 | `brain/graph.py: narrate()` |
| 场景推进 | 行动后更新场景状态，处理地点变更 | narrate 的 `scene_update` / `location_change` |
| 社交互动 | 扮演NPC(口吻/表情/姿态)，判断是否需要掷骰 | `brain/social.py` |
| 记忆管理 | 三层记忆注入叙事prompt | `brain/memory.py` + narrate |

### 8.2 四层记忆系统

| 层级 | 内容 | 来源 |
|------|------|------|
| 工作记忆 | 最近6回合对话原文 | `store.get_recent_logs(campaign_id, n=6)` |
| 中期记忆 | rolling_summary 压缩摘要 (截取前500字) | `store.get_summary(campaign_id)` |
| 长期记忆 | 跨Session语义检索 (Qdrant dnd_memories) | `brain/memory.py: retrieve_memories()` |
| 前情提要 | 跨Session浓缩摘要 | `brain/memory.py: get_recap()` |

### 8.3 多智能体架构

| 智能体 | 职责 | 实现文件 |
|--------|------|----------|
| Director Agent | 意图分类 + 路由决策，注入角色卡/场景/战斗/四层记忆上下文 | `agents/director.py` |
| Rule Judge Agent | 规则检索与校验 | `agents/rule_judge.py` |
| Narrator | 叙事生成 | `agents/narrator.py` |
| Enemy AI | 怪物 AI | `agents/enemy_ai.py` |
| Combat Engine | 战斗引擎协调 | `agents/combat_engine.py` |
| World Manager | 世界管理 | `agents/world_manager.py` |

---

## 九、前端交互界面

### 9.1 页面流转

8种页面状态：

`menu` → `newGame` → `continue` → `join` → `createRoom` → `roomList` → `openingReview` → `game`

### 9.2 游戏主界面布局

```
grid-template-rows: 52px 44px 1fr
grid-template-columns: 1fr 340px
```

| 区域 | 组件 | 功能 |
|------|------|------|
| 顶栏 (52px) | TopBar | 菜单/战役名/模式徽章/游戏内时钟/面板开关 |
| 队伍条 (44px) | PartyBar | 队友头像+HP微条+在线状态+回合高亮 |
| 主舞台 (flex:1) | CombatBar + NarrativeStream + QuickChips + ActionInput | 叙事流 + 战斗层 + 快捷行动 + 输入框 |
| 右侧面板 (340px) | SidePanel | 4标签页: 角色卡/法术书/物品栏/规则速查 |

### 9.3 叙事流消息类型

5种消息气泡：

| 类型 | 样式 | 触发来源 |
|------|------|----------|
| DM 叙述 | 左侧金色书脊引文式, 衬线字体 | `result.narration` |
| 玩家发言 | 右侧暗金气泡 | 本地输入即时上屏 |
| 骰子结果卡 | 居中横卡: 面 + 标题 + 算式 + 判定 | `result.dice` |
| 伤害/治疗浮卡 | 居中胶囊: 红=伤害/绿=治疗 | `dice.damage` / `target_killed` |
| 事件卡 | 居中虚线灰卡 | `monster_action` / 场景 / 时间推进 |

### 9.4 角色面板（右侧4标签页）

- **CharacterSheetTab**：头像/名称/种族/职业/等级/HP血条/AC/速度/六维属性/法术位/生命骰/死亡豁免/状态条件/专长
- **SpellbookTab**：按环阶分组法术列表，一键施展
- **InventoryTab**：装备中/背包/同调位，支持同调/解除同调/装备武器
- **RuleLookupTab**：静态规则卡（阶段2计划接RAG）

---

## 十、数据持久化与API

### 10.1 存储架构

| 存储 | 路径 | 用途 |
|------|------|------|
| SQLite 主库 | `data/saves/save.db` | 战役/角色/场景/战斗/日志 |
| SQLite 检查点 | `data/saves/checkpoints.db` | LangGraph 图执行快照 + HITL 中断恢复 |
| Qdrant 向量库 | `data/rules.db` | 长期记忆 + 规则检索 |
| 规则数据 | `src/aidm/data/` (12模块) | 法术/专长/位面/魔法物品/装备/职业/种族/背景/据点/怪物 |

### 10.2 数据库表结构

```
Campaign (1) ──┬── (N) Character    角色卡
               ├── (N) Scene        场景
               ├── (1) CombatState  战斗状态
               └── (N) Log          跑团日志
```

### 10.3 REST API 端点

共 39 个端点，按功能域分组：

**系统 (2个)**
| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/` | 根路径 |
| GET | `/health` | 健康检查 |

**战役 (3个)**
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/campaign` | 创建战役 |
| GET | `/campaigns` | 列出战役 |
| GET | `/campaign/{id}/state` | 获取战役完整状态 |

**角色 (15个)**
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/character` | 创建角色 |
| GET | `/character/{cid}` | 获取角色详情 |
| GET | `/character/{cid}/inventory` | 获取背包 |
| POST | `/character/{cid}/attune` | 同调物品 |
| POST | `/character/{cid}/break-attunement` | 解除同调 |
| POST | `/character/{cid}/equip-weapon` | 装备武器 |
| POST | `/character/{cid}/rest` | 休息 |
| POST | `/character/{cid}/feat` | 获得专长 |
| GET | `/character/{cid}/available-feats` | 可选专长 |
| POST | `/character/{cid}/select-feat` | 选择专长 |
| GET | `/races` | 种族列表 |
| GET | `/classes` | 职业列表 |
| GET | `/roll-abilities` | 掷属性值 |
| GET | `/backgrounds` | 背景列表 |
| GET | `/spells` | 法术列表 |

**场景/战斗 (6个)**
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/open` | 开场 |
| GET | `/scene/{campaign_id}` | 获取场景 |
| POST | `/generate_setting` | AI生成世界设定 |
| GET | `/monster/{name}` | 查询怪物 |
| GET | `/players/{campaign_id}` | 获取玩家列表 |
| GET | `/combat/{campaign_id}` | 获取战斗状态 |

**对话 (2个)**
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/chat` | 发送消息 |
| POST | `/session/end` | 结束会话 |

**加入 (1个)**
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/join` | 加入战役 |

**房间 (7个)**
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/room/create` | 创建房间 |
| POST | `/room/join` | 加入房间 |
| GET | `/room/by-campaign/{campaign_id}` | 按战役查房间 |
| GET | `/room/{room_id}` | 房间详情 |
| GET | `/rooms` | 房间列表 |
| POST | `/room/{room_id}/kick` | 踢出玩家 |
| POST | `/room/{room_id}/transfer` | 转移房主 |

**战利品 (5个)**
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/loot/generate` | 生成战利品 |
| POST | `/loot/distribute` | 分配战利品 |
| POST | `/loot/pool` | 战利品池 |
| POST | `/loot/distribute/v2` | V2分配 |
| GET | `/loot/history/{campaign_id}` | 战利品历史 |

**据点 (5个)**
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/stronghold/create` | 创建据点 |
| GET | `/stronghold/{campaign_id}` | 据点详情 |
| POST | `/stronghold/build` | 建造设施 |
| POST | `/stronghold/turn` | 据点回合 |
| GET | `/strongholds/facilities` | 设施列表 |

**数据查询 (4个)**
| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/weapons` | 武器列表 |
| GET | `/feats` | 专长列表 |
| GET | `/magic-items` | 魔法物品列表 |
| GET | `/magic-items/{name}` | 魔法物品详情 |

### 10.4 WebSocket 事件

**客户端 → 服务端 (6种事件)：**

| 事件 | 功能 |
|------|------|
| `connect` | 建立连接，加入战役房间 |
| `join` | 以玩家身份加入 |
| `action` | 发送行动指令 |
| `end_turn` | 结束回合 |
| `ready` | 准备就绪 |
| `monster_turn` / `monster_action` / `combat_end` | 怪物回合/行动/战斗结束 |

**服务端 → 客户端 (15种事件)：**

| 事件 | 功能 |
|------|------|
| `join` | 新玩家加入通知 |
| `leave` | 玩家离开通知 |
| `scene_update` | 场景更新 |
| `combat_update` | 战斗状态更新 |
| `player_acting` | 玩家行动中 |
| `processing` | 处理中 |
| `result` | 判定结果 |
| `combat_end` | 战斗结束 |
| `character_update` | 角色数据更新 |
| `monster_turn` | 怪物回合 |
| `monster_action` | 怪物行动 |
| `death_save` | 死亡豁免 |
| `error` | 错误信息 |

### 10.5 存档与恢复

- **保存**：`POST /session/end` → 生成 rolling summary
- **继续**：`GET /campaigns` → `GET /campaign/{id}/state` → 恢复完整状态
- **检查点**：JSON 快照存档，支持 create / list / restore / delete

---

## 十一、规则知识库

### 11.1 规则数据来源

| 数据源 | 规模 | 用途 |
|--------|------|------|
| `data/rules_text/` | 44个顶级子目录, 5190个文本文件 | 判定规则文本语料 (RAG) |
| `5echm_web/data.js` | 6238条三元组 | RAG 数据语料 (怪物/物品/法术) |
| `RULE_SPEC.md` | ~400条结构化规则点 | 最高信号校验语料 |
| `src/aidm/data/` | 12模块, 7532行代码 | 硬编码游戏数据表 |

### 11.2 三集合向量库

| 集合名 | 语料来源 | 用途 |
|--------|----------|------|
| `dnd_rules` | data.js 正文 | 数据检索（怪物查询等） |
| `dnd_rule_text` | rules_text 文本文件 | 规则文本检索 |
| `dnd_rule_spec` | RULE_SPEC 结构化规则点 | 最高信号校验 |

### 11.3 检索方式

**BM25 + 向量 RRF 融合检索**，嵌入模型 bge-small-zh-v1.5 (512维)。

实现在 `knowledge/hybrid.py` (混合检索) 和 `knowledge/retriever.py` (检索器)。

### 11.4 硬编码游戏数据

| 数据 | 条目 | 实现文件 |
|------|------|----------|
| 职业 | 12个核心职业 | `data/classes.py` (712行) |
| 种族 | 10种种族 | `data/races.py` (321行) |
| 背景 | 16种背景 | `data/backgrounds.py` (182行) |
| 专长 | 74个专长 | `data/feats.py` (1330行) |
| 法术 | 12个法术 (戏法-3环) | `data/spells.py` (618行) |
| 魔法物品 | 30个 | `data/magic_items.py` (911行) |
| 怪物 | 完整怪物数据 | `data/monsters.py` + `data/monsters_full.py` |
| 位面 | 58个 | `data/planes.py` (1053行) |
| 据点设施 | 29特色+6基础+11事件 | `data/strongholds.py` (650行) |
| 装备 | 护甲13套+武器38件 | `data/equipment.py` (546行) |

---

## 十二、与 DND 5e 规则书的对比评估

### 12.1 规则实现完整度总表

| 规则领域 | 实现完整度 | 测试覆盖 | 规则准确性 |
|----------|-----------|----------|-----------|
| 骰子引擎 | ★★★★★ 完整 | 高（23用例） | 正确 |
| 属性检定 | ★★★★★ 完整 | 高（20用例） | 正确 |
| 豁免检定 | ★★★★★ 完整 | 高 | 正确 |
| 攻击检定 | ★★★★★ 完整 | 高 | 正确 |
| 伤害计算 | ★★★★★ 完整 | 高（29用例） | 正确 |
| 技能 | ★★★☆☆ 部分 | 中（间接） | 正确但持久化缺失 |
| 法术系统 | ★★★★★ 完整 | 低（仅e2e间接） | 正确（经BUG修复后） |
| 状态效果 | ★★★★★ 完整 | 高（27用例） | 正确 |
| 休息机制 | ★★★★★ 完整 | 低（仅e2e间接） | 正确 |
| 升级系统 | ★★★★★ 完整 | 低（仅e2e间接） | 正确 |
| 死亡豁免 | ★★★★★ 完整 | 高 | 正确 |
| 战斗流程 | ★★★★★ 非常完整 | 高（24用例） | 正确 |
| 核心循环 | ★★★★★ 完整 | 低 | 正确 |

### 12.2 已实现的 DND 5e 核心规则

**引擎层 (21个模块)：**

| 模块 | 行数 | 职责 |
|------|------|------|
| `engine/combat.py` | 1124 | 战斗状态机、先攻、回合推进、动作经济 |
| `engine/actions.py` | 955 | 11种战斗动作定义 |
| `engine/core_loop.py` | 679 | 核心循环、确定性分类 |
| `engine/spellcasting.py` | 1274 | 法术位、成分校验、效应结算 |
| `engine/damage.py` | 368 | 伤害管线、免疫/抗性/易伤 |
| `engine/conditions.py` | 358 | 15种状态 + 力竭 |
| `engine/dice.py` | 342 | 骰子引擎、优劣势、重击 |
| `engine/check.py` | 269 | 属性/豁免/攻击检定 |
| `engine/opportunity_attack.py` | 240 | 借机攻击 |
| `engine/mastery.py` | 256 | 武器精通 |
| `engine/concentration.py` | 278 | 专注维持 |
| `engine/aoe.py` | 381 | 区域效果 |
| `engine/hazards.py` | 430 | 环境危害 |
| `engine/travel.py` | 122 | 旅行系统 |
| `engine/downtime.py` | 128 | 休整期 |
| `engine/encumbrance.py` | 126 | 负重 |
| `engine/attunement.py` | 144 | 同调 |
| `engine/multiclass.py` | 142 | 多职业 |
| `engine/objects.py` | 134 | 物件 |
| `engine/triggers.py` | 151 | 触发器 |
| `engine/vision.py` | 184 | 视觉规则 |

**编排层 (21个模块)：**

| 模块 | 行数 | 职责 |
|------|------|------|
| `brain/exploration.py` | 1267 | 探索系统 |
| `brain/adventure_builder.py` | 1076 | 冒险构建 |
| `brain/rest.py` | 1071 | 休息机制 |
| `brain/levelup.py` | 1156 | 升级系统 |
| `brain/stronghold.py` | 996 | 据点系统 |
| `brain/plane_travel.py` | 818 | 位面旅行 |
| `brain/loot.py` | 851 | 战利品生成 |
| `brain/memory.py` | 768 | 记忆管理 |
| `brain/campaign_manager.py` | 735 | 战役管理 |
| `brain/room.py` | 677 | 房间管理 |
| `brain/char_create.py` | 634 | 角色创建 |
| `brain/social.py` | 608 | 社交系统 |
| `brain/graph.py` | 585 | LangGraph 编排 |
| `brain/loot_distribution.py` | 476 | 战利品分配 |
| `brain/combat_flow.py` | 421 | 多人战斗回合 |
| `brain/session0.py` | 216 | Session 0 |
| `brain/image_gen.py` | 205 | 图像生成 |
| `brain/utils.py` | 159 | 工具函数 |
| `brain/llm.py` | 163 | LLM 调用封装 |
| `brain/world.py` | 126 | 世界管理 |
| `brain/state.py` | 95 | 状态定义 |

**数据层 (12个模块)：**

| 模块 | 行数 | 职责 |
|------|------|------|
| `data/feats.py` | 1330 | 74个专长数据 |
| `data/planes.py` | 1053 | 58个位面数据 |
| `data/magic_items.py` | 911 | 30个魔法物品 |
| `data/classes.py` | 712 | 12个核心职业 |
| `data/strongholds.py` | 650 | 据点设施 |
| `data/spells.py` | 618 | 12个法术 |
| `data/equipment.py` | 546 | 护甲+武器+装备 |
| `data/monsters_full.py` | 514 | 完整怪物数据 |
| `data/races.py` | 321 | 10种种族 |
| `data/monsters.py` | 295 | 怪物索引 |
| `data/backgrounds.py` | 182 | 16种背景 |
| `data/spells_full.py` | 400 | 扩展法术数据 |

### 12.3 与标准流程的差异

| 差异项 | 严重度 | 状态 | 说明 |
|--------|--------|------|------|
| 英雄激励（Heroic Inspiration） | P2 | 暂缓 | 需 Character 表迁移加 inspiration 列 |
| 技能/豁免熟练持久化 | P1 | 待决策 | Character 表缺 skill_prof_json/save_prof_json，当前由 LLM 每轮判定 |
| 法术数据库有限 | P2 | 已知 | 仅12个法术，完整DND 5E有300+法术，大部分依赖RAG检索 |
| 社交DC修正 | P3 | 设计决策 | ±5 DC修正为项目自拟，非规则书原文(规则书用adv/disadv) |
| 态度转换阈值 | P3 | 设计决策 | 10/5/15/10阈值为项目自拟，规则书仅定性可改变 |
| 子职实现 | P2 | 部分 | 数据层有子职字段，但子职特性未完整实现 |

### 12.4 规则准确性保障机制

1. **硬性判定链**：所有掷骰/数值计算由代码执行，LLM 不可绕过
2. **RAG 校验**：检索到的规则原文用于校验 LLM 提出的判定参数，冲突时驳回重填
3. **规则ID标注**：每个函数标注 RULE_SPEC.md 规则点 ID + topics 原文出处路径
4. **自检机制**：每个引擎模块末尾自带 `_self_test()` 自检函数
5. **测试覆盖**：15个测试文件，206个测试用例
6. **密码学随机**：使用 `secrets` 而非 `random`，防止骰子可预测
7. **100轮压测**：三轮完整100轮压测（战士×2 + 牧师×1），验证规则一致性

---

## 十三、测试覆盖

### 13.1 测试总览

15个测试文件，206个测试用例：

| 测试文件 | 行数 | 覆盖模块 |
|----------|------|----------|
| `test_dice_engine.py` | 304 | 骰子引擎 |
| `test_check_system.py` | 337 | 检定系统 |
| `test_damage_system.py` | 374 | 伤害系统 |
| `test_conditions.py` | 326 | 状态条件 |
| `test_combat_flow.py` | 362 | 战斗流程 |
| `test_multiplayer_combat.py` | 441 | 多人战斗 |
| `test_e2e_flow.py` | 385 | 全链路 |
| `test_api_endpoints.py` | 257 | API端点 |
| `test_ownership_gate.py` | 251 | 权限门控 |
| `test_feat_selection.py` | 261 | 专长选择 |
| `test_rule_fixes.py` | 195 | 规则修复 |
| `test_rule_gates.py` | 216 | 规则门控 |
| `test_no_check_gate.py` | 188 | 免检定门控 |
| `test_engine_properties.py` | 142 | 引擎属性 |
| `test_memory_summary.py` | 130 | 记忆摘要 |

### 13.2 高覆盖区域

- 骰子引擎、检定系统、伤害系统、状态条件、战斗流程、多人战斗

### 13.3 低覆盖区域

- 法术系统、休息机制、核心循环、升级系统、探索/旅行、社交系统、借机攻击、AoE、武器精通、环境危害

---

## 十四、评估与建议

### 14.1 整体评估

AIDM 系统已实现了一个相当完整的 D&D 5E 电子跑团系统。核心创新在于"硬性判定链"架构，将 LLM 的活动范围严格限制在意图理解和叙事生成两端，中间所有规则判定由 21 个引擎模块的确定性代码执行。

### 14.2 优势

1. **规则判定100%由确定性代码执行**，保证公平性和一致性
2. **21个引擎模块**覆盖了DND 5E绝大部分核心规则（8085行引擎代码）
3. **206个测试用例** + 三轮100轮压测验证
4. **四层记忆系统**让AI DM具有跨Session记忆能力
5. **WebSocket多人同桌**支持，基于 Socket.IO 的房间管理
6. **完整的角色创建五步车卡法**，对照 PHB 2024
7. **RAG 知识库**：44个规则子目录 + 6238条三元组 + 400条结构化规则点

### 14.3 建议改进项

| 优先级 | 改进项 | 说明 |
|--------|--------|------|
| P1 | 技能/豁免熟练持久化 | Character表需增加 skill_prof_json/save_prof_json |
| P2 | 法术系统测试 | spellcasting.py 有1274行但无专门测试文件 |
| P2 | 英雄激励 | 2024 PHB核心机制之一，尚未实现 |
| P2 | 法术数据扩充 | 当前仅12个法术，需扩充 |
| P3 | 社交/探索/升级测试 | 缺乏针对性单元测试 |
| P3 | 社交DC修正 | 当前±5 DC为项目自拟，可考虑改为规则书的adv/disadv |

---

## 附录A：关键文件索引

| 文件 | 路径 | 用途 |
|------|------|------|
| LangGraph 编排 | `src/aidm/brain/graph.py` | 8节点判定管线 |
| 骰子引擎 | `src/aidm/engine/dice.py` | 密码学随机骰子 |
| 检定系统 | `src/aidm/engine/check.py` | 属性/豁免/攻击检定 |
| 伤害系统 | `src/aidm/engine/damage.py` | 伤害管线 |
| 战斗引擎 | `src/aidm/engine/combat.py` | 战斗状态机 |
| 动作定义 | `src/aidm/engine/actions.py` | 11种战斗动作 |
| 核心循环 | `src/aidm/engine/core_loop.py` | 确定性分类 |
| 法术系统 | `src/aidm/engine/spellcasting.py` | 法术结算 |
| 状态条件 | `src/aidm/engine/conditions.py` | 15种状态+力竭 |
| Director Agent | `src/aidm/agents/director.py` | 意图分类 |
| Rule Judge | `src/aidm/agents/rule_judge.py` | 规则校验 |
| 角色创建 | `src/aidm/brain/char_create.py` | 五步车卡法 |
| 社交系统 | `src/aidm/brain/social.py` | 四步社交循环 |
| 记忆管理 | `src/aidm/brain/memory.py` | 四层记忆 |
| 战斗回合 | `src/aidm/brain/combat_flow.py` | 多人回合管理 |
| WebSocket | `src/aidm/api/ws.py` | Socket.IO 实时同桌 |
| API 主入口 | `src/aidm/api/main.py` | FastAPI 应用 |
| 状态持久化 | `src/aidm/stats/store.py` | SQLite 存储 |
| 数据模型 | `src/aidm/stats/models.py` | SQLModel ORM |
| 混合检索 | `src/aidm/knowledge/hybrid.py` | BM25+向量 RRF |
| 配置 | `src/aidm/config.py` | pydantic-settings |

## 附录B：引擎模块清单

| 模块 | 行数 | 职责 |
|------|------|------|
| `engine/combat.py` | 1124 | 战斗状态机、先攻、回合推进、动作经济、移动、掩护 |
| `engine/actions.py` | 955 | 11种战斗动作（attack/dash/disengage/dodge/help/hide/magic/ready/search/study/utilize） |
| `engine/core_loop.py` | 679 | 核心循环、确定性分类、免检定门控 |
| `engine/spellcasting.py` | 1274 | 法术位消耗、成分校验、效应结算、升环施法 |
| `engine/damage.py` | 368 | 伤害管线：免疫→修正→抗性→易伤→下限0 |
| `engine/conditions.py` | 358 | 15种状态条件 + 力竭累加 |
| `engine/dice.py` | 342 | 密码学随机骰子、优劣势、重击、天然1/20 |
| `engine/check.py` | 269 | 属性/豁免/攻击检定、DC计算、被动检定 |
| `engine/aoe.py` | 381 | 区域效果（锥/线/球/立方/圆柱） |
| `engine/hazards.py` | 430 | 环境危害（陷阱/极端天气/坠落/窒息） |
| `engine/opportunity_attack.py` | 240 | 借机攻击触发与结算 |
| `engine/mastery.py` | 256 | 武器精通特性 |
| `engine/concentration.py` | 278 | 专注维持豁免 |
| `engine/travel.py` | 122 | 旅行步调、导航、随机遭遇 |
| `engine/downtime.py` | 128 | 休整期活动 |
| `engine/encumbrance.py` | 126 | 负重与速度 |
| `engine/attunement.py` | 144 | 魔法物品同调 |
| `engine/multiclass.py` | 142 | 多职业规则 |
| `engine/objects.py` | 134 | 物件交互 |
| `engine/triggers.py` | 151 | 触发器与事件 |
| `engine/vision.py` | 184 | 视觉规则（黑暗视觉等） |

## 附录C：编排层模块清单

| 模块 | 行数 | 职责 |
|------|------|------|
| `brain/exploration.py` | 1267 | 探索系统（导航/被动察觉/随机遭遇） |
| `brain/levelup.py` | 1156 | 升级系统（XP表/五步升级） |
| `brain/adventure_builder.py` | 1076 | 冒险构建器 |
| `brain/rest.py` | 1071 | 休息机制（短休/长休/力竭恢复） |
| `brain/stronghold.py` | 996 | 据点系统（建造/升级/事件） |
| `brain/plane_travel.py` | 818 | 位面旅行 |
| `brain/loot.py` | 851 | 战利品生成 |
| `brain/memory.py` | 768 | 四层记忆管理 |
| `brain/campaign_manager.py` | 735 | 战役管理 |
| `brain/room.py` | 677 | 多人房间生命周期管理 |
| `brain/char_create.py` | 634 | 五步车卡法 |
| `brain/social.py` | 608 | 四步社交循环 + NPC态度系统 |
| `brain/graph.py` | 585 | LangGraph 8节点编排管线 |
| `brain/loot_distribution.py` | 476 | 战利品分配 |
| `brain/combat_flow.py` | 421 | 多人战斗回合管理 |
| `brain/session0.py` | 216 | Session 0 设置 |
| `brain/image_gen.py` | 205 | 图像生成 |
| `brain/utils.py` | 159 | 工具函数 |
| `brain/llm.py` | 163 | LLM 调用封装 |
| `brain/world.py` | 126 | 世界管理 + 开场叙事 |
| `brain/state.py` | 95 | GameState 状态定义 |

## 附录D：数据层模块清单

| 模块 | 行数 | 职责 |
|------|------|------|
| `data/feats.py` | 1330 | 74个专长数据 |
| `data/planes.py` | 1053 | 58个位面数据 |
| `data/magic_items.py` | 911 | 30个魔法物品 |
| `data/classes.py` | 712 | 12个核心职业 |
| `data/strongholds.py` | 650 | 据点设施（29特色+6基础+11事件） |
| `data/spells.py` | 618 | 12个法术（戏法-3环） |
| `data/equipment.py` | 546 | 护甲13套+武器38件+装备 |
| `data/monsters_full.py` | 514 | 完整怪物数据 |
| `data/races.py` | 321 | 10种种族 |
| `data/monsters.py` | 295 | 怪物索引 |
| `data/backgrounds.py` | 182 | 16种背景 |
| `data/spells_full.py` | 400 | 扩展法术数据 |
