# 需求分析：基于前端原型、规则书与调研文档

> 注：本文档部分"待实现"项已随后落地，状态已就近标注（详见 §1.3 与 §5 各节）。

> 本文档综合 `DND5e_UI_交互原型.html`（前端原型）、`AI跑团规则书使用指南.html`（规则书使用指南）、以及五份调研报告（AI_DM模型技术能力与架构总报告、DND5e完整游玩流程指南、DND5e完整游玩流程深度调研报告、多人同玩架构设计调研报告、跑团流程深度调研报告），提取系统需求并制定实施路线图。
>
> 生成时间：2026-07-15。配套 `PRD.md` / `ARCHITECTURE.md` / `REFACTOR_PLAN.md`。

---

## 一、现状基线

### 1.1 已完成阶段（P0–P5）

| Phase | 状态 | 核心模块 |
|-------|------|----------|
| P0 引擎核心 | ✅ | `engine/{dice,check,damage,conditions,combat,equipment}` — 8 模块自检通过 |
| P1 状态层 | ✅ | `stats/{models,store}` — SQLModel 角色卡/战役/场景/战斗/日志 + SQLite 持久化 + rolling summary |
| P2 知识层 | ✅ | `knowledge/*` — 三语料 hybrid RAG（data.js 6238 + rules_text 141 + RULE_SPEC 400 → Qdrant 本地文件三集合） |
| P3 编排层 | ✅ | `brain/graph.py` — LangGraph StateGraph 判定链（classify→retrieve→verify→resolve→narrate→apply），含 HITL |
| P4 API 层 | ✅ | `api/main.py` FastAPI（/health /campaign /character /chat /chat/resume /summary /open /scene）+ `api/ws.py` WebSocket + `cli.py` |
| P5 前端 | ✅ | `ui/static/index.html` Web 聊天页+场景面板 + `ui/app/page.tsx` Next.js scaffold |

### 1.2 技术栈

| 模块 | 选型 |
|------|------|
| 语言 | Python 3.12.11 |
| LLM 编排 | LangGraph 1.2.9 |
| LLM 接入 | langchain-openai 1.3.5 + openai 1.107.2 |
| 实际 LLM | deepseek-v4-flash @ senseaudio 网关 |
| Embedding | 本地 bge-small-zh-v1.5（512 维，sentence-transformers，走 HF 镜像） |
| 向量库 | Qdrant 本地文件模式（path=rules.db，免 docker） |
| ORM | SQLModel 0.0.39（Pydantic + SQLAlchemy） |
| 状态库 | SQLite（SQLModel 驱动，存档即拷文件） |
| API | FastAPI 0.118.3（异步、自动文档、Pydantic 原生） |
| 前端 | Next.js 14 + React 18 + Tailwind CSS 3.4 + @3d-dice/dice-box + socket.io-client（双前端：`ui/static/` 原生 HTML + `ui/app/` Next.js；无 shadcn/ui，组件自研） |

### 1.3 当前能力边界

**已具备**：
- 完整的 D&D 5E 规则引擎（骰子/检定/伤害/状态/战斗/装备）
- SQLite 持久化状态层（角色卡/战役/场景/战斗/日志 + rolling summary）
- 三语料 hybrid RAG 知识层（BM25 中文字符级 + 向量 RRF 融合 + 别名富化）
- LangGraph 编排层（硬性判定链端到端跑通，含 HITL interrupt + resume）
- FastAPI API 层 + WebSocket 多人连接管理 + CLI 交互层
- Next.js 前端 scaffold（对话区+骰子动画/日志+角色卡+战斗追踪器+场景面板）

**尚未具备**：
- 工具层完善（6 大模块 40+ 工具）— 让 AI 有"手"可用 ✅ 已实现（`brain/` 19 业务模块已覆盖检定/战斗/角色/空间/规则/记忆工具域，部分工具待补全）
- 多智能体架构改造（5-Agent 协作）— 从单 graph 升级为 Director + Narrator + Combat + World Manager + Rule Judge ✅ 已实现（`agents/` 6 Agent 已建：Director/Narrator/Combat/WorldManager/RuleJudge/EnemyAI，与单 graph 渐进迁移中）
- 记忆系统升级（三层记忆架构）— 解决 Session 3 崩塌问题 ✅ 已实现（`brain/memory.py` 三层记忆：工作/中期 rolling summary/长期 Qdrant 向量，跨 Session 持久化）
- 多人同玩架构升级（python-socketio → Room 生命周期 → 权限分层 → 地图/Token）
- 体验优化 & 模型调优（中文叙事 prompt 优化、RAG 规则索引优化、反刍/幻觉监控）
- 交互式产物生成（场景插图、战术地图、角色卡/怪物卡渲染、战报自动生成）✅ 已实现（`brain/image_gen.py` 场景插图生成已落地；战术地图/角色卡渲染部分待补）

---

## 二、前端原型需求提取

> 来源：`D:/game/dnd/DND5e_UI_交互原型.html`（单体 HTML + 内联 CSS/JS，约 84KB，2436 行）
>
> **关键判断**：该原型是高保真交互规格说明，不是最终实现。数据全部硬编码在 JS 中，AI 响应是关键词匹配伪模拟，战斗回合推进是链式 setTimeout 脚本化演示。迁移到真实应用时需改为 API/WebSocket 调用 + 后端权威状态机。

### 2.1 整体布局

**三栏式布局**（全屏 `height: 100vh; overflow: hidden`，内部区域各自滚动）：

| 区域 | 宽度 | 内容 |
|------|------|------|
| 左栏 — 角色卡 | 220px | 队伍头像列表、HP 条、AC/速度/先攻三宫格、六维属性网格、技能熟练列表、死亡豁免追踪器、状态条件标签、专注追踪条、法术位格子、特性 & 动作、背包 & 装备 |
| 中央 — 主舞台 | flex:1 | 顶部模式切换器（探索/战斗/社交）、叙事消息流（6 种类型化消息）、战斗时叠加先攻条 + 战术网格 + 战斗者 HP 迷你卡 + 动作面板 |
| 右栏 — 骰子与日志 | 240px | 8 个骰子按钮、优势/劣势切换、修饰值输入、投掷结果显示、行动日志、短休/长休按钮 |

**顶部栏**（48px）：左侧战役信息（"Lost Mine of Phandelver · 第3次会话·探索阶段"）、中间模式切换器、右侧规则参考/设置图标按钮。

### 2.2 三种游戏模式

| 模式 | data-mode | 核心差异 |
|------|-----------|----------|
| **探索模式**（默认） | `exploration` | 显示快捷检定按钮（调查/感知/潜行/运动/洞悉/生存），隐藏先攻条/战术网格/战斗者HP/动作面板；加载探索叙事 |
| **战斗模式** | `combat` | 显示先攻条、战术网格（10列×6行，每格24px）、战斗者HP迷你卡、动作面板；加载战斗叙事并重置动作 |
| **社交模式** | `social` | 与探索类似布局，但加载 NPC 对话叙事，包含 NPC 态度系统（中立→友好）和任务触发 |

### 2.3 六种类型化叙事消息

叙事区采用类聊天界面，消息按类型差异化渲染：

| 类型 | CSS 类 | 视觉 | 说明 |
|------|--------|------|------|
| DM 叙事 | `msg-dm` | 蓝色左边框，衬线字体 | AI DM 的场景描述、结果叙述 |
| 玩家发言 | `msg-player` | 紫色气泡，右对齐 | 玩家的行动描述、对话 |
| NPC 对话 | `msg-npc` | 琥珀色左边框 | NPC 的台词、反应 |
| 骰子结果 | `msg-roll` | 绿色卡片 | 骰子图标/明细/结果/标签 |
| 伤害/治疗 | `msg-damage` | 红色居中卡片 | HP 变更提示 |
| 系统消息 | `msg-system` | 居中灰色 | 会话开始/结束、模式切换等 |

**设计意图**：这种类型化渲染天然适合后端返回结构化消息体 `{type, speaker, content}` 由前端统一渲染。

### 2.4 前端需要与后端进行的数据交互（11 类）

#### 2.4.1 会话与战役管理
- 获取战役信息：战役名称、会话编号、当前阶段
- 加载/保存会话状态：叙事历史、当前模式、回合数、先攻顺序

#### 2.4.2 角色数据（完整角色卡 JSON）
- 基本信息：姓名、种族、职业、等级
- 属性：六维数值及调整值（STR/DEX/CON/INT/WIS/CHA）
- 战斗数据：HP（当前/最大）、AC、速度、先攻加值
- 技能：技能列表、熟练项标记、修正值
- 特性：职业特性、种族特性
- 法术：已知法术列表、准备法术列表、戏法列表、法术位状态
- 背包：物品清单、负重、装备状态
- Hit Dice：骰子类型、已用/可用状态
- 状态条件：当前激活的状态条件列表
- 专注：当前专注的法术

#### 2.4.3 AI DM 叙事交互（核心）
- 玩家文本提交 → 后端调 LLM → 返回结构化消息体
- 原型中 `generateDMResponse(text)` 是本地关键词匹配模拟，真实实现需：
  - 发送玩家行动文本到后端
  - 后端结合当前游戏状态（角色 HP、位置、剧情进度）调用 AI 生成响应
  - 返回结构化数据：叙事文本、要求的检定类型、DC 值、NPC 对话、状态变化等

#### 2.4.4 骰子投掷与检定
- 投骰请求：骰子类型（d20/d4/d6...）、数量、优势/劣势模式、修饰值
- 检定结果：原始骰值、修饰值、最终结果、成功/失败判定
- **安全性要求**：骰子结果必须由服务端决定（防作弊）；检定结果的业务逻辑判定（DC 比较、自然 1/20 特殊处理）应在后端完成

#### 2.4.5 战斗系统数据
- 先攻列表：各战斗者的先攻值、名称、类型（玩家/敌方）、当前回合指针
- 战斗者状态：每个战斗者的 HP、AC、位置（战术网格坐标）、状态条件
- 回合管理：当前轮次（roundCount）、当前行动者索引（currentInitIndex）、已用动作（usedActions）
- 战术网格状态：10×6 网格中每个单元格的类型（空/墙/困难地形）和占据单位

#### 2.4.6 法术系统数据
- 法术书数据：角色可用法术列表，每个法术包含名称、环阶、学派、施法时间、射程、持续时间、成分、描述
- 法术位管理：各环阶法术位的总数、已用数、恢复事件
- 专注管理：当前专注的法术、专注持续时间、专注打断事件

#### 2.4.7 状态条件系统
- 条件定义：14 种标准状态及其描述
- 角色当前状态：每个角色身上激活的状态条件列表，需持久化到后端
- 状态效果计算：某些状态影响检定（如中毒→劣势、祝福→+1d4），后端需维护这些修正

#### 2.4.8 休息与资源恢复
- 短休请求：触发后端计算可恢复的 HP（基于 Hit Dice 投掷）、恢复的职业特性
- 长休请求：触发后端执行 HP 回满、Hit Dice 恢复一半、法术位全恢复、口粮消耗检查
- Hit Dice 投掷：d8 + CON 修正的回血计算

#### 2.4.9 死亡豁免系统
- 死亡状态触发：HP 归零时后端标记角色进入濒死状态
- 死亡豁免检定：每轮一次 d20 投掷，后端记录成功/失败计数
- 稳定/死亡判定：3 次成功→稳定；3 次失败→死亡；天然 20→恢复 1HP；天然 1→2 次失败
- 需后端权威判定

#### 2.4.10 日志与历史记录
- 行动日志：时间戳 + 文本，需同步到后端作为会话记录
- 叙事历史：整个叙事区的消息流需持久化，支持会话恢复和历史回看

#### 2.4.11 多人协作数据
- 各玩家角色的实时状态同步
- 当前操作权传递（谁的回合）
- DM 权限管理（AI DM vs 人类 DM）
- 玩家加入/离开通知

### 2.5 关键 UI 组件清单

| # | 组件 | 功能 | 数据来源 |
|---|------|------|----------|
| 1 | 队伍栏 (party-bar) | 显示队伍成员头像和 HP 状态点 | GET /character（多角色） |
| 2 | 属性网格 (ability-grid) | 六维属性数值和调整值 | 角色卡 JSON |
| 3 | 技能列表 (skill-list) | 18 项技能，熟练项绿色圆点 | 角色卡 JSON |
| 4 | HP 条 (hp-bar-fill) | 红色进度条，带 transition 动画 | 战斗状态 |
| 5 | 法术位格子 (spell-slots) | available 蓝/used 灰，点击消耗/恢复 | 角色卡 JSON |
| 6 | 状态标签 (cond-chip) | 每种状态独立配色，点击移除 | 战斗状态 |
| 7 | 专注追踪条 (concentration-track) | 蓝色条，显示专注法术，"打断专注"按钮 | 战斗状态 |
| 8 | 死亡豁免追踪器 (death-save-box) | 3 成功/3 失败圆点 + "掷死亡豁免 d20"按钮 | 战斗状态 |
| 9 | 先攻条 (initiative-bar) | 横向排列先攻卡，当前回合高亮琥珀色边框 | 战斗状态 |
| 10 | 战术网格 (tac-grid) | 10×6 CSS Grid，区分玩家/敌人/墙壁/困难地形 | 战斗状态 |
| 11 | 战斗者 HP 迷你卡 (combatant-hp) | 横向滚动卡片，显示每个战斗者的名字/HP 条/HP 数值 | 战斗状态 |
| 12 | 动作面板 (action-panel) | 分组按钮：移动组/动作组/附赠动作&反应组，已用动作变灰+删除线 | 战斗状态 |
| 13 | 快捷检定 (quick-actions) | 6 个圆形按钮：调查/感知/潜行/运动/洞悉/生存 | 前端发起 → 后端检定 |
| 14 | 骰子投掷器 (dice-section) | 8 个骰子按钮 + 优势/劣势切换 + 修饰值输入 + 结果显示区 | 后端骰子引擎 |
| 15 | 行动日志 (log-section) | 时间戳 + 文本，高亮项绿色，伤害项红色 | 后端日志 |
| 16 | 法术书模态框 (spellbookModal) | 法术卡片列表，点击展开详情，"施放"按钮 | 角色卡 JSON |
| 17 | 玩家输入区 (player-input-area) | 文本输入框 + 发送按钮，Enter 键提交 | 前端 → POST /chat |
| 18 | 休息按钮 (rest-section) | 短休 1h / 长休 8h 按钮 | 前端 → POST /rest |

### 2.6 配色语义系统

原型使用 CSS 变量系统，配色语义清晰：

| 颜色 | 语义 | 用途 |
|------|------|------|
| 紫 | 法术/玩家 | 玩家消息气泡、法术相关元素 |
| 蓝 | DM/专注 | DM 叙事左边框、专注追踪条 |
| 绿 | 成功/骰子 | 骰子结果卡片、行动日志高亮项 |
| 红 | HP/伤害/敌方 | HP 进度条、伤害提示、敌方名字 |
| 琥珀 | NPC/警告/当前回合 | NPC 对话左边框、先攻条当前回合高亮 |

### 2.7 交互流程详解

#### 探索模式流程
1. DM(AI) 以衬线字体描述场景（古老废墟、断裂柱子、金属碰撞声）
2. 玩家通过底部输入框描述行动（"我靠近入口，仔细观察"）
3. DM 要求进行**感知(察觉)检定**
4. 系统自动投骰 d20(14)+4=18，结果以绿色卡片形式插入叙事流
5. DM 根据检定结果描述发现（压力触发装置、弩箭发射口）
6. DM 给出选择分支（绕过/解除/冒险通过）

#### 战斗模式流程
1. 切换到战斗模式 → 先攻条出现，战术网格生成，战斗者 HP 卡显示，动作面板激活
2. DM 叙述遭遇（哥布林突袭）并给出先攻顺序：格罗姆(18) > 哥布林A(14) > 哥布林B(12) > 埃尔达(10)
3. 玩家通过动作面板选择行动：
   - **攻击**：点击"攻击"按钮 → 自动插入玩家叙事 → 500ms 后 DM 提示投攻击检定 → 再 500ms 后调用 `rollDice(20)` 并自动设置修正值为+5 → 动作按钮标记为已使用
   - **施法**：点击"施法" → 打开法术书模态框 → 选择法术施放
4. 点击"结束回合" → 触发 `endTurn()` 的链式 setTimeout 动画序列：
   - DM 叙述哥布林A攻击埃尔达（800ms）
   - 投攻击检定 d20(8)+4=12，未命中 AC 14（500ms）
   - 哥布林B选择脱离后退，埃尔达施放魔法飞弹（600ms）
   - 投伤害 3d4(2+3+1)=6，哥布林B剩余HP 1/7（500ms）
   - 第N轮结束，第N+1轮开始，重置动作（600ms）

#### 社交模式流程
1. DM 描述遇到老学者萨多，NPC 态度标注为"中立"
2. NPC 以琥珀色气泡发言（"你们是谁？为什么来这里？"）
3. 玩家选择说服方式
4. DM 要求**魅力(说服)检定**，DC 15（中立态度）
5. 检定结果刚好达到 DC → NPC 态度变化：中立→友好
6. NPC 提出交易（帮找回古书）→ **任务触发**

#### 法术施放流程
1. 点击"法术列表"或战斗中"施法" → 打开法术书模态框
2. 法术以卡片形式列出，点击展开详情（施法时间/射程/成分/持续时间/描述）
3. 点击"施放"按钮 → 关闭模态框 → 叙事区插入施法叙述 → 消耗对应法术位 → 如需专注则添加 concentrating 条件并显示专注追踪条

#### 死亡豁免流程
1. HP 归零时显示死亡豁免追踪器（3 成功圆点 + 3 失败圆点）
2. 点击"掷死亡豁免 d20" → `rollDeathSave()` 处理：
   - 天然 20：恢复 1HP，苏醒
   - 天然 1：记 2 次失败
   - 10+：记 1 次成功
   - 9-：记 1 次失败
3. 累计 3 次成功 → 稳定（不再掷骰但仍昏迷）
4. 累计 3 次失败 → 死亡

#### 休息流程
1. 点击"短休"按钮 → 叙事提示可消耗 Hit Dice 回 HP，恢复部分职业特性
2. 点击"长休"按钮 → HP 回满（45/45）、恢复一半 Hit Dice、法术位全恢复、力竭等级-1
3. 注意需消耗 1 份口粮

### 2.8 原型的局限性（开发参考需注意）

1. **数据全部硬编码**：角色数据、法术列表、叙事内容都写死在 JS 中，无任何后端 API 调用
2. **AI 响应是伪模拟**：`generateDMResponse()` 仅做关键词匹配返回预设文案，非真实 AI 调用
3. **战斗回合推进是脚本化的**：`endTurn()` 用链式 setTimeout 演示了一轮战斗的完整流程，但不是真实的回合制状态机
4. **单人视角**：虽然 party-bar 支持切换查看角色，但 `switchCharacter()` 只记录日志，未实际切换角色卡数据
5. **部分功能未接线**：`takeRest('short')` 的短休只显示叙事提示，未实际消耗 Hit Dice 或恢复资源；战术网格的移动逻辑存在但未与战斗回合系统联动

### 2.9 关键技术决策暗示

- 选择单体 HTML 文件而非框架项目，说明这是**快速原型验证阶段**，重点在于交互流程的可视化而非工程实现
- CSS 变量系统完善（--bg-*、--text-*、--border 等），配色语义清晰，便于后续迁移到 React/Vue 组件库
- 叙事消息采用类型化渲染（msg-dm/msg-player/msg-npc/msg-roll/msg-damage/msg-system），这种设计天然适合后端返回结构化消息体 `{type, speaker, content}` 由前端统一渲染

---

## 三、规则书使用指南要点

> 来源：`D:/game/dnd/AI跑团规则书使用指南.html`
>
> 该指南基于 5echm 规则书库（D&D 5e 中文完整版）生成，采用 T1-T4 四级优先级体系组织规则内容。

### 3.1 规则书在 AI 跑团中扮演的角色

规则书是 AI DM 的**事实依据和操作手册**，主要解决三大问题：

1. **防止规则幻觉**：AI 容易编造不存在的法术效果或给职业不存在的特性。规则书提供了权威的规则原文，让 AI 在不确定时查询而非编造。建议"在 AI DM 的系统提示中写明：如果不确定某个法术的具体效果，先查询规则书文件再回答"，并"让 AI 在做出关键规则判定时引用规则书原文"。

2. **提供查表入口**：AI 不需要把所有数据记在上下文里，但需要知道**去哪查**。规则书库中的"速查"目录就是为快速查阅设计的——法术速查、战斗速查、冒险速查等。

3. **统一游戏循环与判定标准**：规则书定义了 AI 每个回合都要执行的核心循环和判定机制，确保跑团体验的一致性。

### 3.2 T1 必须掌握：核心机制循环（最高优先级）

这是 AI 每一个回合都要执行的内容，搞错了跑团体验直接崩。

#### 游戏循环（Play Loop）
- 核心三步循环：DM 描述环境 → 玩家描述行动 → DM 叙述结果（可能掷骰），然后回到第 1 步
- AI 特别注意：不要跳步。常见错误是 AI 在玩家还没行动时就替玩家做了决定，或在玩家行动后不回到"描述环境"。每次玩家行动后都应重新描述当前环境状态

#### 战斗流程（Combat Order）
- 五步走：判定突袭（隐匿检定 vs 被动感知）→ 决定位置 → 掷先攻（敏捷检定，高到低排序）→ 执行回合 → 新一轮
- 每回合可做的事：移动（等于速度）+ 一个动作 + 一个附赠动作（如有特权）+ 与物件交互（免费）+ 沟通（免费）
- 相关文件：`战斗流程.htm`、`战斗动作.htm`、`移动与位置.htm`、`发起攻击.htm`、`伤害与治疗.htm`、`掩护.htm`

#### d20 检定系统
- 三种用途：属性检定（d20 + 属性调整值 + 熟练加值 vs DC）、攻击检定（d20 + 属性调整值 + 熟练加值 vs 目标 AC）、豁免检定（d20 + 属性调整值 + 豁免熟练加值 vs DC）
- 优势/劣势：掷两个 d20 取高（优势）或取低（劣势），不叠加
- DC 参考：非常简单 5 / 简单 10 / 中等 15 / 困难 20 / 非常困难 25 / 几乎不可能 30
- AI 特别注意：不要什么检定都设 DC 15。城主指南明确说了三种风格——"以掷骰为本"、"掷骰不如思考"、"掷骰与思考结合"。推荐用"结合"风格：玩家描述合理时可直接判定成功，只有不确定时才掷骰

#### 状态系统（Conditions）
- D&D 5e 有 14 种标准状态：目盲、魅惑、耳聋、恐慌、擒抱、失能、隐形、中毒、倒地、压制、震慑、昏迷、麻痹、力竭
- 最大风险：AI 经常忘记追踪状态持续时间。建议 AI 在每回合结束时输出一个状态追踪表

### 3.3 T2 关键数据：角色与世界

AI 需要查表才能正确执行的数据，不一定要全部记在上下文里，但要知道去哪查。

#### 职业特性（Class Features）
12 个核心职业，每个有子职业分支。关键资源、恢复方式和核心机制：

| 职业 | 关键资源 | 恢复方式 | 核心机制 |
|------|---------|---------|---------|
| 野蛮人 | 狂暴次数 | 长休 | 狂暴（物理伤害优势、抗性） |
| 吟游诗人 | 法术位 | 长休 | 灵感骰、万能魔法 |
| 牧师 | 法术位 | 长休 | 引导神力、领域特性 |
| 德鲁伊 | 法术位 | 长休 | 荒野形态 |
| 战士 | 动作汹涌 | 短休 | 动作汹涌（一回合多打） |
| 武僧 | 气点 | 短休 | 疾风连击、散打 |
| 圣武士 | 法术位 | 长休 | 神圣攻击、誓约 |
| 游侠 | 法术位 | 长休 | 宿敌、自然探索者 |
| 游荡者 | 无资源系统 | — | 偷袭（每回合一次）、灵巧动作 |
| 术士 | 法术位 + 术法点 | 长休 | 超魔、术法点转换 |
| 邪术师 | 法术位 | **短休** | 魔契恩赐、邪术祈唤 |
| 法师 | 法术位 | 长休 | 奥术恢复、法术书 |

AI 特别注意：邪术师的法术位在短休恢复，这和其他施法者不同；游荡者没有资源系统但偷袭骰每回合只能用一次。这些细节 AI 容易搞混。

#### 法术系统（Spell System）
法术是 D&D 中最容易让 AI 产生"规则幻觉"的部分。AI 必须搞清的法术规则：
- **法术位**：施法消耗对应等级的法术位，高阶法术位可以施放低阶法术（升阶施法）
- **戏法**：0 级法术，不需要法术位，可随意施放
- **准备法术 vs 已知法术**：牧师/德鲁伊/圣武士/法师是"准备"制（每天选），术士/吟游诗人/游侠/邪术师是"已知"制（升级时学）
- **专注**：同一时间只能专注一个法术，受伤害要过体质豁免（DC = 10 或伤害的一半取高），失败则法术中断
- **施法时间**：1 动作（最常见）、1 附赠动作、1 分钟、10 分钟、1 小时等
- **效应范围**：参考 `玩家手册/魔法/效应范围示意图.png`

#### 怪物数据（Monster Stats）
AI 在设计遭遇时必须参考真实怪物数据，不能"编"一个怪物出来。怪物数据卡的关键字段：
- CR（挑战等级）、AC（护甲等级）、HP（生命值，通常是骰子表达式如 `3d8 + 6`）
- 速度、属性、技能/豁免熟练
- 伤害免疫/抗性/易伤、感官、语言
- 动作/传奇动作/反应

#### 休息与资源管理
- **短休**：1 小时以上，消耗生命骰恢复 HP，仅邪术师恢复法术位，部分能力（如战士动作汹涌）恢复
- **长休**：8 小时以上（可含 2 小时值守），HP 回满 + 恢复一半生命骰，所有法术位和资源恢复
- **生命骰**：等于角色等级数，类型由职业决定（d6/d8/d10/d12）。短休时消耗，掷骰 + 体质调整值恢复对应血量

### 3.4 T3 DM 工具箱：判断与临场

帮助 AI 做更好的"DM 判断"——什么时候该骰、怎么平衡遭遇、怎么设计冒险。

#### 遭遇平衡（Encounter Building）
这是 AI DM 最容易翻车的地方之一。核心是用 CR（挑战等级）和 XP 预算来构建遭遇。

遭遇难度阈值表（单人 XP 阈值）：

| 难度 | 1 级 | 3 级 | 5 级 | 10 级 | 15 级 |
|------|------|------|------|-------|-------|
| 简单 | 25 | 75 | 250 | 600 | 1100 |
| 中等 | 50 | 150 | 500 | 1200 | 2200 |
| 困难 | 75 | 225 | 750 | 1900 | 3400 |
| 致命 | 100 | 400 | 1100 | 2800 | 4900 |

多人遭遇时累加后乘以遭遇乘数（2 只 ×1.5，3-6 只 ×2，7-10 只 ×2.5，11-14 只 ×3）。

AI 建议：不要只算 CR。一个 CR 3 的怪物打 4 个 3 级角色算"中等"，但如果怪物有范围攻击而队伍挤在一起，实际可能致命。AI 设计时多准备一个"逃跑路线"或"增援延迟"机制。

#### 掷骰哲学（Dice Philosophy）
三种风格：
1. **以掷骰为本**：所有行动都骰，让运气决定一切。优点公平，缺点降低角色扮演兴致
2. **掷骰不如思考**：只在战斗时骰，其他靠 DM 判断。优点鼓励创新，缺点 DM 可能不中立
3. **掷骰与思考结合（推荐）**：玩家描述合理时直接成功，不确定时才骰

关键原则："游戏的主宰不是骰子，而是你。"——城主指南原文。AI 作为 DM 应该灵活运用，不要变成规则计算器。

#### 冒险结构设计
城主指南提供了完整的冒险设计框架：
- 冒险故事结构.htm — 起承转合
- 冒险环境.html — 地城/荒野/城镇的不同处理
- 创建冒险.html — 从零开始设计
- 随机地下城.html — 随机生成地城
- 创建非玩家角色.html — 快速 NPC 生成表

### 3.5 T4 扩展内容：锦上添花

起步阶段可以全部跳过，等 T1-T3 跑顺了再加载。

- **扩展职业与种族**：塔莎的万事坩埚、珊娜萨的万事指南、剑湾冒险者指南、费资本的巨龙宝库、万象无常书
- **变体规则**：英雄点数、情节点数、扫荡怪群、先攻变体
- **世界观设定集**：艾伯伦、塔尔多雷、鸦阁魔域、荒洲、印记城

### 3.6 AI 跑团五大瓶颈与对策

| 瓶颈 | 类型 | 问题 | 对策 |
|------|------|------|------|
| **状态遗忘** | 即时性 | AI 忘记之前施加的状态或角色 HP 变化 | 每回合结束时输出状态快照表（角色名/HP/条件/法术位） |
| **规则幻觉** | 即时性 | AI 编造不存在的法术效果或职业特性 | 核心法术和职业特性提前喂入上下文；不确定时查询规则书；让 AI 引用规则书原文 |
| **空间感缺失** | 即时性 | AI 无法"看到"地图，距离/掩护/范围出错 | 用文字坐标网格替代视觉地图（每格=5 尺） |
| **难度失控** | 即时性 | 遭遇太强导致团灭或太弱毫无挑战 | 每次设计遭遇走 CR 计算；准备 3 档方案；给怪物设计逃跑条件；给玩家留撤退路线 |
| **叙事断裂** | 跨 session | 新 session 时 AI 忘记上次发生的事 | 每 session 结束时生成剧情摘要 JSON（party/key_events/active_quests/npcs/next_hooks） |

### 3.7 AI DM 五条铁律（不可违反）

1. **绝不替玩家行动** — AI 不能描述玩家角色的行动、说话、思考或感受
2. **绝不透露未发现的信息** — 场景不预宣布伏击，NPC 不透露未发现的秘密
3. **绝不假设行动成功** — 简单任务自动成功、不可能任务自动失败，其余必须掷骰
4. **绝不强行推进预设剧情** — 优先响应玩家选择，DM 的"计划"只是备选
5. **绝不跳过时间** — 除非玩家明确要求

---

## 四、调研报告核心结论

> 来源：五份 HTML 调研文档（AI_DM模型技术能力与架构总报告、DND5e完整游玩流程指南、DND5e完整游玩流程深度调研报告、多人同玩架构设计调研报告、跑团流程深度调研报告）

### 4.1 AI DM 系统整体架构

#### 核心公式
**AI DM = LLM(叙事大脑) + 确定性引擎(规则手脚) + 持久记忆(跨会话存在) + 多智能体协作(职责分离)**

#### 架构演进三范式
1. **范式 A：单模型+Prompt**（已淘汰）— Session 3 后必然崩塌（上下文溢出、规则遗忘、叙事断裂）
2. **范式 B：单 Agent + Tool Calling** — 性价比最高，代表 FRPG Creator、dnd-llm-game
3. **范式 C：多智能体协作**（共识方向）— 能力最强，代表 ITMO AI-DM(8-Agent)、Critical Miss、ChatRPG 论文

#### 推荐的 5-Agent 精简架构（基于 AIDM 现状）

| Agent | 职责 | 何时激活 | AIDM 对应 |
|-------|------|----------|-----------|
| **Director** | 接收玩家输入→分类意图→路由到专业 Agent→组装最终叙事输出 | 每个回合 | 新增（替代原有单一 graph 入口） |
| **Narrator** | 场景描述、NPC 对话、剧情推进、氛围渲染 | 非战斗场景 | `brain/graph.py` 重构 |
| **Combat Engine** | 先攻管理、逐回合推进、攻击判定、伤害计算、条件追踪 | 战斗场景 | `engine/combat/*` 扩展为 Agent |
| **World Manager** | 地点/时间/天气/NPC 状态/任务进度/物品栏 | 每次状态变更 | `stats/store.py` 扩展 |
| **Rule Judge** | 验证行动合法性+规则书 RAG 查询+法术/怪物数据检索 | 每次行动前 | `knowledge/*` (Qdrant) 扩展 |

### 4.2 D&D 5e 完整游玩流程

#### 流程层次全景（从宏观到微观）
```
战役层(Campaign): Session 0 → Session 1 → Session 2 → ... → 大结局
    ↓ 每次会话包含多个
会话层(Session): 开场回顾 → 探索 → 社交 → 战斗 → 休息 → ... → 悬念结尾
    ↓ 每个阶段使用
核心循环(Core Loop): DM描述环境 → 玩家声明行动 → DM判断/要求掷骰 → 玩家掷骰 → DM叙述结果 → 循环
    ↓ 战斗中细化为
战斗轮次(Combat Round): 掷先攻 → 按序列执行回合 → 每回合：移动+动作+附赠动作+反应 → 新一轮
    ↓ 每个动作触发
掷骰解决(Dice Resolution): d20 + 修正值 ≥ DC/AC → 成功/失败 → 叙述结果
```

#### 核心机制：D20 检定系统
- **核心公式**：d20 + 属性调整值 + 熟练加值（如适用）≥ DC/AC = 成功
- **三种检定类型**：能力检定（玩家主动做有失败风险的事）、攻击检定（d20+攻击加值≥目标 AC）、豁免检定（被动反应危险）
- **优势与劣势三大规则**：不叠加（多个优势仍只投两颗 d20）、互相抵消（同时有优势和劣势只投一颗 d20）、重骰规则
- **难度等级参考(DC)**：非常容易 5、容易 10、中等 15、困难 20、非常困难 25、近乎不可能 30
- **熟练加值表**：1-4 级 +2、5-8 级 +3、9-12 级 +4、13-16 级 +5、17-20 级 +6
- **关键规则**：只有 DM 能要求掷骰；自然 1 = 自动未命中，自然 20 = 自动命中且暴击（伤害骰翻倍）

#### 战斗系统全流程
1. **判定突袭(Surprise)** — 基于隐匿检定 vs 被动感知判定；被突袭者在第一轮无法行动
2. **确定位置(Establish Positions)** — DM 确定所有角色和怪物的起始位置；网格地图每格=5 尺
3. **掷先攻(Roll Initiative)** — 先攻=d20+敏捷调整值；由高到低排序形成先攻序列，整个战斗保持不变
4. **执行回合(Take Turns)** — 按先攻顺序每人执行一个回合；一轮(Round)=游戏世界 6 秒，所有参战者各行动一次
5. **开始新一轮(Begin Next Round)** — 所有人完成回合后回到先攻序列顶端

**单个回合结构**：
- 移动(Movement)：至多等于速度距离，可拆分到动作前后
- 动作(Action)：每回合一个，主要行动（攻击/施法/冲刺/脱离/闪避/协助/躲藏/预备/搜索/使用物品）
- 附赠动作(Bonus Action)：0-1 次，仅当特殊能力/法术允许时
- 反应(Reaction)：0-1 次，触发式行动（借机攻击/特定法术如护盾术）
- 免费物品互动：每回合一次免费与一个物品互动
- 对话：6 秒内能说的量，不需要消耗动作

#### 施法系统详解
- **法术环阶与法术位**：法术分为 0-9 环；零环法术即戏法(Cantrips)可无限次施展；施展一环或更高法术需消耗相应或更高环阶的法术位；长休恢复所有法术位
- **法术成分**：言语(V)、姿势(S)、材料(M)
- **施法核心公式**：法术豁免 DC=8+熟练加值+施法属性调整值；法术攻击加值=熟练加值+施法属性调整值
- **集中维持**：标注"集中"的法术需施法者保持集中；受到伤害时体质豁免 DC=max(10, 伤害/2)，失败则法术中断；同时只能集中维持一个法术
- **升环施法**：用更高环阶法术位施展低环法术时该法术被视为更高环阶，部分法术升环后效果更强

#### 休息机制：短休与长休
- **短休(Short Rest)**：至少 1 小时，进行轻度活动；花费生命骰恢复 HP（每枚生命骰掷骰+CON 修正值=恢复量）；邪术师恢复所有法术位；战士恢复行动涌动和风之息；武僧恢复所有真气点；吟游诗人(5 级+)恢复吟游灵感；德鲁伊恢复野性变身
- **长休(Long Rest)**：至少 8 小时其中至少 6 小时睡眠最多 2 小时轻度活动；恢复所有 HP；恢复已花费生命骰的一半（向下取整）；恢复所有法术位（除邪术师外）；恢复几乎所有职业特性；力竭等级减少 1 层；限制：每 24 小时最多获益一次；开始长休时至少有 1HP；被战斗打断需重新开始 8 小时

#### 濒死与死亡流程
1. **判定是否瞬间死亡** — 如果受到的伤害将角色降至 0HP 且剩余伤害≥角色最大 HP → 瞬间死亡
2. **濒死状态(0 HP, Unconscious)** — 角色倒地昏迷无法移动或行动；每轮在你的回合开始时必须进行死亡豁免检定：掷 d20 不加任何修正值；10+记录 1 次成功；9 以下记录 1 次失败；天然 1=2 次失败；天然 20=恢复 1HP 苏醒；累计 3 次成功→稳定（不再掷骰但仍昏迷）；累计 3 次失败→死亡
3. **濒死状态下受到伤害** — 如果昏迷角色受到任何伤害→1 次死亡豁免失败；如果是近战暴击（5 尺内的攻击对昏迷目标自动暴击）→2 次失败；如果伤害≥最大 HP→瞬间死亡
4. **挽救濒死角色** — 治疗法术（任何治疗→恢复至少 1HP→立刻苏醒，死亡豁免计数归零）、医药检定（动作进行 DC10 感知医药检定→成功则稳定）、医疗包（消耗 1 次使用次数自动稳定）、濒死之触戏法（接触范围动作自动稳定）

### 4.3 多人同玩架构关键设计点

#### 当前项目已有的多人能力（基础版）
- WebSocket 连接管理 — 多玩家连同一战役
- 广播机制 — 一人行动全员收到结果
- 回合协调 — 战斗中检查 `is_player_turn()`
- 序列化执行 — `asyncio.Lock` 保证 `graph.run` 串行
- 玩家列表 — `get_players()` / `current_turn_name()`
- 状态广播 — `broadcast_state()` 同步场景+战斗+回合

#### 当前架构的瓶颈
1. **单进程内存态** — `ConnectionManager.campaigns` 是内存 dict，重启即丢失，无法水平扩展
2. **无重连恢复** — 玩家断线后无法恢复到之前的游戏状态（WebSocket 断 = 退出）
3. **无房间生命周期管理** — 房间不会自动创建/销毁，无匹配机制
4. **无权限分层** — DM 和普通玩家走同一 WebSocket，没有权限差异
5. **无地图/Token 系统** — 纯文本跑团，缺少 VTT 核心的地图可视化
6. **全量广播** — 每次广播整个状态，无增量同步，状态变大后带宽压力
7. **无离线消息队列** — 玩家离线期间的消息直接丢失

#### 权威服务器模式
- **推荐：权威服务器(Authoritative Server)** — 服务器持有唯一真实状态，客户端发操作请求，服务器验证+执行+广播结果
- 防作弊（骰子结果服务端决定）；状态一致（不会出现客户端状态分歧）；DND 天然适合（本来就是 DM 说了算）
- 项目已经是这个模式（`graph.run` 在服务端执行），方向正确

#### "一人行动，全员观看"模式
- 玩家 A 发送 action → 服务器
- 服务器验证：`isPlayerTurn(A)` → YES
- 服务器执行 `graph.run(input)` → narration+dice+state_changes
- 服务器广播 result → 所有客户端
- 服务器广播 state_update → 所有客户端（HP/战斗/回合）
- 其他玩家 UI 更新："轮到 B 了"

#### DM 权限模型

| 能力 | DM（主持人） | 玩家 |
|------|-------------|------|
| 查看隐藏信息（陷阱 DC/怪物 HP/隐藏笔记） | ✅ | ❌ |
| 修改任何状态（HP/物品/位置） | ✅ | ❌ 仅自己的角色 |
| 撤销/回溯操作 | ✅ | ❌ |
| 控制 NPC/怪物 | ✅ | ❌ |
| 控制地图 FOW（战争迷雾） | ✅ | ❌ |
| 强制结束/跳过回合 | ✅ | ❌ |
| 在自己的回合执行操作 | ✅ | ✅ |
| 查看公开骰子结果 | ✅ | ✅ |
| 发送聊天消息 | ✅ | ✅ |

#### 房间生命周期管理
```
创建 ──→ 等待玩家 ──→ 游戏中 ──→ 暂停 ──→ 销毁
 ↑          │           │         ↑         │
 │     可重连窗口    可断线重连    │    持久化到DB
 │     (30s)        (保持状态)    │
 └──────────────────────────────────────────┘
关键时间点:
  onCreate:  初始化战役状态、加载规则书 RAG
  onJoin:    加载角色卡、发送当前场景+战斗状态
  onAction:  序列化执行 graph.run、广播结果
  onLeave:   标记离线、30s 重连窗口
  onDispose: 持久化到 SQLite、清理内存
```

### 4.4 技术选型和实现方案建议

#### 分层模型架构
一个模型打不了全场。最佳实践是按任务分配不同能力的模型：

| Agent 角色 | 最需要的模型能力 | 推荐模型 | Temperature | 成本占比 |
|-----------|-----------------|---------|-------------|---------|
| Director(编排) | 意图分类/路由判断/Tool Calling | GPT-4o | 0.2-0.3 | ~15% |
| Narrator(叙事) | 创意写作/场景描述/情感渲染 | Claude Sonnet 4 / GPT-4o | 0.7-0.8 | ~50% |
| Combat Engine(战斗) | 结构化 Tool Call/数学准确 | GPT-4o-mini（或确定性引擎） | 0 | ~10% |
| World Manager(世界) | 结构化数据管理 | 确定性函数（非 LLM） | N/A | ~0% |
| Rule Judge(规则) | RAG 检索/精确匹配/严格约束 | GPT-4o-mini+Qdrant | 0-0.1 | ~10% |
| 摘要/观察提取 | 信息压缩/关键点提取 | GPT-4o-mini/Claude Haiku | 0.2 | ~15% |

#### 两种 Tool Calling 实现方案对比

| 特性 | OpenAI Function Calling(原生) | LangChain Tools |
|------|-------------------------------|-----------------|
| 集成难度 | 低—直接定义 JSON Schema | 中等—需 LangChain 框架 |
| 多模型支持 | 仅 OpenAI 模型 | 跨模型（通过 adapter） |
| 可靠性 | 最高—GPT-4o 原生优化 | 依赖底层模型能力 |
| 结构化输出 | 原生 JSON mode+strict mode | Pydantic+with_structured_output |
| 流式响应 | 原生支持 | 需 LangGraph streaming |
| 适用场景 | 主 DM 编排（GPT-4o 作为中枢） | 跨模型/多提供商场景 |

推荐方案：如果以 GPT-4o 为主模型，用原生 Function Calling（更可靠、更简单）。如果需要多模型支持，用 LangChain Tools。AIDM 场景推荐前者——先把一个模型做深做稳。

### 4.5 关键技术难点与对策

| 难点 | 根源 | 当前最佳对策 | 成熟度 |
|------|------|-------------|--------|
| Session 3 崩塌 | 上下文窗口无法承载完整对话历史 | 三层记忆架构+每回合观察提取+摘要压缩+语义检索注入。ChatRPG 论文方案（Archivist 外置状态）已验证可线性化 token 增长 | 中高 |
| 规则幻觉 | LLM 训练数据中 D&D 规则不完整/过时 | RAG 规则书检索—AI 必须"查规则"而非"背规则"。Divination 项目(USP)和 AIDM 的 Qdrant 方案都指向这个方向 | 高 |
| 空间感缺失 | LLM 无空间推理能力 | 确定性空间工具（距离/AoE/视线/掩护）—ChatRPG 的 5 个空间工具是最完整参考 | 高 |
| 叙事反刍 | LLM 倾向于重复已有信息 | 80 词约束+novelty filtering+Pacing Agent（Narra·Gym 反停滞控制） | 中 |
| 玩家代理权侵犯 | LLM 有"替人做决定"的倾向 | 铁律约束（见上文）+Rule Judge 验证+输出后置审核 | 中 |
| 多玩家并发 | 回合内多人同时行动 | asyncio.Lock 序列化（已实现）+Director 优先级排序+广播增量状态 | 中 |
| 遭遇平衡 | CR 系统本身不精确+LLM 不理解战术深度 | XP Budget 工具+CR 数据 RAG+"逃跑路线"硬编码+动态调整（增援延迟/怪物撤退） | 中 |
| 成本控制 | 多 Agent+长对话→token 爆炸 | 分层模型（大模型做叙事、小模型做琐事）、摘要压缩、工具返回结构化短数据而非长文本 | 高 |

### 4.6 全网参考资源索引

| 资源 | 类型 | 核心价值 |
|------|------|---------|
| Critical Miss | 技术博客 | 最详细的记忆系统设计（MongoDB+ChromaDB+观察提取流水线） |
| ITMO AI Dungeon Master | 开源项目 | 最完整的 8-Agent 多智能体架构+LangGraph 实现 |
| ChatRPG 论文 | 学术论文 | 多智能体 ReAct vs 纯 Prompt 的对照实验（统计显著） |
| tegridydev/dnd-llm-game | 开源项目 | "一个核心+两层管理+多方协作"设计理念 |
| Multi-agent D&D with LangChain | 技术教程 | 最详细的 LangGraph 编排实现教程（含完整代码示例） |
| FRPG Creator (GM-ENGINE) | 开源项目 | LangGraph+Tool Calling+RAG+动态摘要实战（Streamlit 前端） |
| llm-dungeon-master | 开源项目 | 多模型 agent 分拆（setting/rules/memory 三类 agent） |
| Narra·Gym | 评估框架 | LLM 交互叙事能力五维评估（含主流模型排行榜） |
| ChatRPG MCP Server | MCP 工具 | 最完整的 D&D 5e 工具集（30+工具，可参考实现） |
| DnD-MCP Server | MCP 工具 | 90+工具+checkpoint+rewind |
| nekro_trpg_dice_plugin | 开源项目 | Qdrant RAG+跨会话记忆+QQ Bot 集成（中文 CoC/D&D） |
| AI-DM (xxkiba) | 开源项目 | 多 Agent+RAG+GenAI 插图+战斗状态持久化 |
| ScriptoriumGM | 商业产品 | RAG 记忆力在 GM 场景的实际应用案例分析 |

---

## 五、待实现功能模块详解

### 5.1 工具层完善（6 大模块 40+ 工具）

> 优先级：**最高**。预估工作量：~2 周。
>
> **状态**：✅ 部分已实现 — `brain/` 19 业务模块已覆盖检定/战斗/角色/空间/规则/记忆工具域；下表"新建"项已落地者就近标 ✅ 已存在，未落地者仍标新建。
>
> 这是让 AI 有"手"可用的基础，也是多智能体架构的前提。模板已有 ChatRPG/DnD-MCP 可参考，每个工具返回结构化 JSON，严格错误处理，集成现有 `engine/*` 确定性引擎 + `knowledge/*` Qdrant RAG。

#### 5.1.1 骰子与检定工具（5 个）

| 工具名 | 功能 | 输入 | 输出 | 关联引擎 |
|--------|------|------|------|----------|
| `roll_dice` | 投掷任意面数的骰子 | `{sides, count, modifier, advantage, disadvantage}` | `{rolls, total, modifier, final_result}` | `engine/dice.py` |
| `roll_check` | 执行属性检定 | `{ability, skill, dc, advantage, disadvantage}` | `{roll, modifier, total, success, dc}` | `engine/check.py` |
| `roll_attack` | 执行攻击检定 | `{attacker, target, weapon, advantage, disadvantage}` | `{attack_roll, attack_total, hit, critical, target_ac}` | `engine/check.py` + `engine/combat.py` |
| `roll_saving_throw` | 执行豁免检定 | `{character, ability, dc, advantage, disadvantage}` | `{roll, modifier, total, success, dc}` | `engine/check.py` |
| `roll_initiative` | 投掷先攻 | `{combatants: [{cid, name, dex_mod}]}` | `{initiative_order: [{cid, name, initiative, side}]}` | `engine/combat.py` |

#### 5.1.2 战斗系统工具（8 个）

| 工具名 | 功能 | 输入 | 输出 | 关联引擎 |
|--------|------|------|------|----------|
| `create_encounter` | 创建遭遇（CR 计算+怪物选择） | `{party_level, party_size, difficulty, terrain}` | `{encounter_id, monsters, total_xp, difficulty_rating}` | 新建 `engine/encounter.py` |
| `initiate_combat` | 启动战斗（突袭判定+先攻投掷） | `{encounter_id, combatants}` | `{combat_id, initiative_order, surprised_combatants}` | `engine/combat.py` |
| `execute_action` | 执行战斗动作 | `{combat_id, actor_id, action_type, target_id, params}` | `{action_result, damage_dealt, conditions_applied, state_snapshot}` | `engine/combat.py` + `engine/actions.py` |
| `advance_turn` | 推进到下一回合 | `{combat_id}` | `{next_combatant, round_number, turn_effects_resolved}` | `engine/combat.py` |
| `manage_condition` | 施加/移除/查询状态条件 | `{target_id, condition, action, duration}` | `{success, current_conditions, expired_conditions}` | `engine/conditions.py` |
| `get_combat_state` | 获取当前战斗状态 | `{combat_id}` | `{active, round, initiative_order, combatants_state}` | `engine/combat.py` |
| `render_battlefield` | 渲染战场文字坐标网格 | `{combat_id}` | `{grid_text, combatant_positions, terrain_features}` | 新建 `engine/battlefield.py` |
| `resolve_death` | 处理死亡豁免/稳定/复活 | `{character_id, action, params}` | `{death_save_result, successes, failures, status}` | `engine/damage.py` |

#### 5.1.3 角色与资源管理工具（6 个）

| 工具名 | 功能 | 输入 | 输出 | 关联引擎 |
|--------|------|------|------|----------|
| `create_character` | 创建新角色 | `{name, race, class, level, abilities, background}` | `{character_id, character_sheet}` | `stats/models.py` + `data/classes.py` |
| `get_character_sheet` | 获取完整角色卡 | `{character_id}` | `{character_sheet_json}` | `stats/store.py` |
| `update_character` | 更新角色属性/HP/状态 | `{character_id, updates}` | `{success, updated_fields, new_state}` | `stats/store.py` |
| `manage_spell_slots` | 管理法术位消耗/恢复 | `{character_id, slot_level, action}` | `{success, remaining_slots, restored_slots}` | `engine/spellcasting.py` |
| `manage_inventory` | 管理物品栏（添加/移除/装备） | `{character_id, item, action, quantity}` | `{success, current_inventory, weight}` | `data/equipment.py` + `stats/store.py` |
| `take_rest` | 执行短休/长休 | `{character_id, rest_type, hit_dice_to_spend}` | `{hp_restored, hit_dice_spent, spell_slots_restored, features_restored, time_elapsed}` | `brain/rest.py` ✅ 已存在 |

#### 5.1.4 空间与世界工具（7 个）

| 工具名 | 功能 | 输入 | 输出 | 关联引擎 |
|--------|------|------|------|----------|
| `measure_distance` | 测量两点间距离（格子数×5尺） | `{from: {x,y}, to: {x,y}}` | `{distance_feet, distance_cells, path_cells}` | 新建 `engine/space.py` |
| `calculate_aoe` | 计算法术效应范围覆盖的格子 | `{center: {x,y}, shape, size}` | `{affected_cells, total_area}` | 新建 `engine/space.py` |
| `check_line_of_sight` | 检查视线是否被阻挡 | `{from: {x,y}, to: {x,y}, obstacles}` | `{has_los, blocked_by, cover_level}` | 新建 `engine/space.py` |
| `check_cover` | 检查目标掩护等级 | `{attacker_pos, target_pos, obstacles}` | `{cover_level: none/half/three_quarters/full, ac_bonus}` | 新建 `engine/space.py` |
| `calculate_movement` | 计算可移动距离（含困难地形） | `{combatant_id, destination, terrain_map}` | `{can_reach, path, movement_cost, remaining_speed}` | 新建 `engine/space.py` |
| `manage_location` | 管理队伍当前位置/区域切换 | `{campaign_id, action, location_data}` | `{success, current_location, available_exits}` | `brain/world.py` |
| `move_party` | 移动队伍到新位置 | `{campaign_id, destination, pace}` | `{time_elapsed, encounters_triggered, new_location}` | `brain/exploration.py` |

#### 5.1.5 规则查询(RAG)工具（3 个）

| 工具名 | 功能 | 输入 | 输出 | 关联模块 |
|--------|------|------|------|----------|
| `query_rules` | 查询规则书原文 | `{query, tag_filter, limit}` | `{results: [{body, tag, path, score}]}` | `knowledge/retriever.py` + `knowledge/hybrid.py` |
| `lookup_spell` | 查询法术详情 | `{spell_name}` | `{name, level, school, casting_time, range, components, duration, description, upcast}` | `data/spells.py` + `knowledge/retriever.py` |
| `lookup_monster` | 查询怪物数据卡 | `{monster_name}` | `{name, cr, ac, hp, speed, abilities, skills, saves, immunities, resistances, vulnerabilities, senses, languages, actions, legendary_actions, reactions}` | `data/monsters.py` + `knowledge/retriever.py` |

#### 5.1.6 记忆与会话工具（5 个）

| 工具名 | 功能 | 输入 | 输出 | 关联模块 |
|--------|------|------|------|----------|
| `create_observation` | 从回合交互中提取关键观察 | `{turn_log, campaign_id}` | `{observations: [{type, content, importance, timestamp}]}` | `brain/memory.py` ✅ 已存在 |
| `create_memory` | 创建长期记忆条目 | `{content, memory_type, tags, importance}` | `{memory_id, embedding_stored}` | `brain/memory.py` ✅ 已存在 + `knowledge/indexer.py` |
| `retrieve_memories` | 检索相关长期记忆 | `{query, limit, min_importance}` | `{memories: [{content, score, timestamp}]}` | `brain/memory.py` ✅ 已存在 + `knowledge/hybrid.py` |
| `get_session_context` | 获取当前会话上下文摘要 | `{campaign_id}` | `{summary, active_quests, key_npcs, party_status, recent_events}` | `stats/store.py` + `brain/memory.py` ✅ 已存在 |
| `save_checkpoint` | 保存完整状态快照 | `{campaign_id, checkpoint_type}` | `{checkpoint_id, state_snapshot, timestamp}` | `stats/store.py` + LangGraph checkpointer |

### 5.2 多智能体架构改造

> 优先级：**高**。预估工作量：~3 周。
>
> **状态**：✅ 已实现（渐进迁移中）— `agents/` 6 Agent 已建（Director/Narrator/Combat/WorldManager/RuleJudge/EnemyAI），与单 graph 并行迁移；下文"新建 `brain/director.py`"实际落位于 `agents/director.py`。
>
> 将现有单 graph 改造为 5-Agent 协作架构。Director Agent 作为新入口（替代现有 `graph.run` 直调），LangGraph StateGraph 条件路由。

#### 5.2.1 架构图

```
玩家输入
    │
    ▼
┌─────────────┐
│  Director    │ ← 意图分类、路由、最终叙事组装
│  Agent       │
└──────┬──────┘
       │ 条件路由
       ├──────────────────┬──────────────────┐
       ▼                  ▼                  ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Narrator    │  │  Combat      │  │  World       │
│  Agent       │  │  Engine      │  │  Manager     │
│  (非战斗)    │  │  (战斗)      │  │  (状态变更)  │
└─────────────┘  └─────────────┘  └─────────────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          ▼
                   ┌─────────────┐
                   │  Rule Judge  │ ← 行动合法性验证、RAG 查询
                   │  Agent       │
                   └─────────────┘
```

#### 5.2.2 各 Agent 职责与实现要点

**Director Agent（编排中枢）**
- 接收玩家自然语言输入
- 分类意图（attack/cast/ability_check/social/explore/rest/other）
- 路由到对应专业 Agent
- 收集各 Agent 输出，组装最终叙事返回给玩家
- 实现：新建 `brain/director.py`，基于 LangGraph StateGraph

**Narrator Agent（叙事生成）**
- 场景描述（多感官：视觉/听觉/嗅觉/触觉）
- NPC 对话生成（保持人格一致性）
- 剧情推进与氛围渲染
- 反停滞控制（novelty filtering，避免重复已有信息）
- 实现：重构 `brain/graph.py` 的 narrate 节点

**Combat Engine Agent（战斗执行）**
- 先攻管理（投掷、排序、持久化）
- 逐回合推进（动作经济、反应协调）
- 攻击判定与伤害计算（调用确定性引擎）
- 条件追踪（施加、持续时间衰减、解除）
- 实现：扩展 `engine/combat/*` 为 Agent 接口

**World Manager Agent（世界状态管理）**
- 地点/时间/天气/NPC 状态管理
- 任务进度追踪（active_quests 更新）
- 物品栏与战利品管理
- 跨 Session 状态持久化
- 实现：扩展 `stats/store.py`

**Rule Judge Agent（规则裁决）**
- 验证行动合法性（是否有武器、是否在射程内等）
- RAG 查询规则书原文（不确定时查询而非编造）
- 法术/怪物数据检索与校验
- 冲突驳回（LLM 填的参数与规则冲突时驳回重填）
- 实现：扩展 `knowledge/*` (Qdrant)

### 5.3 记忆系统升级

> 优先级：**高**。预估工作量：~2 周。
>
> **状态**：✅ 已实现 — `brain/memory.py` 三层记忆架构（工作记忆/中期 rolling summary/长期 Qdrant 向量）已落地，跨 Session 持久化。详见 `MEMORY_SYSTEM_STATUS.md`。
>
> 解决 Session 3 崩塌问题，实现跨 Session 可玩性。

#### 5.3.1 三层记忆架构

```
┌─────────────────────────────────────────────────────────┐
│  工作记忆 (Working Memory)                                │
│  最近 N 轮对话原文 (N=10~20)                              │
│  → 直接注入 LLM 上下文                                    │
├─────────────────────────────────────────────────────────┤
│  中期记忆 (Medium-term Memory)                            │
│  每 K 轮压缩成摘要替换原文 (K=5~10)                       │
│  → rolling summary，控制 token 线性增长                   │
├─────────────────────────────────────────────────────────┤
│  长期记忆 (Long-term Memory)                              │
│  关键事实嵌入向量库 (Qdrant)，按语义相关性检索注入        │
│  → 跨 Session 记忆持久化                                  │
└─────────────────────────────────────────────────────────┘
```

#### 5.3.2 配套实现

- **Observation/Memory 工具**（回合后自动提取关键信息）：每回合结束后，用小模型从交互日志中提取关键观察（NPC 名字、地点变化、HP 变化、任务进展等），存入长期记忆
- **记忆检索流水线**：语义搜索 → 重要性加权 → 时间衰减 → Rerank → Top-K 注入
- **Session 存档/读档功能**：
  1. 生成完整摘要：Narrator + World Manager 联合生成"本次 Session 关键事件"摘要（10-20 条要点）
  2. 持久化所有状态：角色卡、NPC 关系、物品栏、任务进度 → SQLite
  3. 生成记忆嵌入：关键事实 → Qdrant 向量库（语义可检索）
  4. 生成"前情提要"：下次 Session 开始时注入的浓缩摘要（500-1000 tokens）
  5. Checkpoint：完整状态快照，支持回退

### 5.4 多人同玩架构升级

> 优先级：**中**。预估工作量：分 4 个 Phase，共 ~2 周。
>
> 基于《多人同玩架构设计调研报告》制定。

#### 5.4.1 推荐路线

| Phase | 目标 | 改动量 | 时间 |
|-------|------|--------|------|
| **Phase 1** | 用 `python-socketio` 替换裸 WebSocket，获得 Room/自动重连/消息缓冲 | 小（改 ws.py） | 1-2 天 |
| **Phase 2** | 参考 Colyseus 实现 Room 生命周期 + Redis 扩展 + 30s 重连窗口 | 中 | 3-5 天 |
| **Phase 3** | DM/Player 权限分层 + Secret State 过滤 | 中 | 2-3 天 |
| **Phase 4** | 地图/Token 系统（可选，参考 PlanarAlly） | 大 | 5-7 天 |

#### 5.4.2 关键决策

1. **不需要引入 Node.js** — `python-socketio` 提供全部 Socket.IO 能力，保持纯 Python 技术栈
2. **不需要 CRDT** — DND 是回合制，权威服务器 + 事件驱动就够。Yjs 只在需要"离线编辑角色卡"时才值得引入
3. **不需要 UDP/WebRTC** — DND 不是 FPS，不需要毫秒级延迟。WebSocket 的可靠性更重要
4. **参考 Colyseus 架构但不直接使用** — Colyseus 的 Room/Schema/生命周期设计是教科书级别的。在 Python 中照着实现一套，比直接引入 Node.js 更好
5. **PlanarAlly 是最佳参考项目** — 同为 Python 后端 + WebSocket 多人 + VTT 功能，直接阅读其源码

### 5.5 体验优化 & 模型调优

> 优先级：**中**。预估工作量：~2 周。

#### 5.5.1 中文叙事 prompt 优化
- 融合 Oracle-RPG + Bilibili RPG-Bot + 机核语法
- 80 词约束（避免叙事反刍）
- novelty filtering（Pacing Agent 反停滞控制）

#### 5.5.2 RAG 规则索引优化
- 5echm 核心文件精选索引
- 别名富化扩展（玩家同义词→规则原词）
- 检索结果 rerank

#### 5.5.3 反刍/幻觉监控指标
- 叙事重复率监控
- 规则幻觉率监控（LLM 编造不存在的法术效果或职业特性的频率）
- 上下文利用率监控

#### 5.5.4 A/B 测试不同模型组合
- GPT-4o vs Claude Sonnet 4 叙事质量对比
- 分层模型架构成本优化
- 多玩家并发 + 断线重连

### 5.6 交互式产物生成

> 优先级：**低**。预估工作量：待定。
>
> **状态**：✅ 部分已实现 — `brain/image_gen.py` 场景插图生成已落地；战术地图/角色卡渲染部分待补。

#### 5.6.1 场景插图
- 战斗场景配图（怪物图鉴已有 112 张图片资产）
- 关键场景配图（城镇、地城、荒野）
- NPC 肖像生成

#### 5.6.2 战术地图
- ASCII 网格地图（文字坐标网格，每格=5 尺）
- 可视化网格地图（Canvas/PixiJS 渲染）
- Token 拖拽与位置同步

#### 5.6.3 角色卡/怪物卡渲染
- 角色卡 PDF 导出
- 怪物卡标准化展示
- 战报自动生成

#### 5.6.4 剧情道具
- 信件、密文、地图碎片等剧情道具
- 道具图标与描述

---

## 六、优先级排序与实施路线图

### 6.1 总体优先级矩阵

| 优先级 | 模块 | 预估工作量 | 依赖关系 | 价值 |
|--------|------|-----------|----------|------|
| **P0 最高** | 工具层完善（6 大模块 40+ 工具） | ~2 周 | 无 | 让 AI 有"手"可用，多智能体架构前提 |
| **P1 高** | 多智能体架构改造（5-Agent） | ~3 周 | P0 工具层 | 从单 graph 升级为协作架构 |
| **P1 高** | 记忆系统升级（三层记忆） | ~2 周 | 无 | 解决 Session 3 崩塌，跨 Session 可玩 |
| **P2 中** | 多人同玩架构升级（4 Phase） | ~2 周 | 无 | python-socketio → Room → 权限 → 地图 |
| **P2 中** | 体验优化 & 模型调优 | ~2 周 | P1 多智能体 | 中文叙事优化、RAG 优化、监控 |
| **P3 低** | 交互式产物生成 | 待定 | P1 多智能体 | 场景插图、战术地图、战报 |

### 6.2 实施路线图

```
Phase 1: 工具层完善（~2 周）
├── 5.1.1 骰子与检定工具（5 个）
├── 5.1.2 战斗系统工具（8 个）
├── 5.1.3 角色与资源管理工具（6 个）
├── 5.1.4 空间与世界工具（7 个）
├── 5.1.5 规则查询(RAG)工具（3 个）
└── 5.1.6 记忆与会话工具（5 个）
    ↓
Phase 2: 多智能体架构改造 + 记忆系统升级（并行，~3 周）
├── 5.2 多智能体架构改造（5-Agent）
│   ├── Director Agent（编排中枢）
│   ├── Narrator Agent（叙事生成）
│   ├── Combat Engine Agent（战斗执行）
│   ├── World Manager Agent（世界状态管理）
│   └── Rule Judge Agent（规则裁决）
└── 5.3 记忆系统升级（三层记忆架构）
    ├── 工作记忆（对话缓冲）
    ├── 中期记忆（滚动摘要）
    └── 长期记忆（Qdrant 向量检索）
    ↓
Phase 3: 多人同玩架构升级 + 体验优化（并行，~2 周）
├── 5.4 多人同玩架构升级（4 Phase）
│   ├── Phase 1: python-socketio 升级
│   ├── Phase 2: Room 生命周期 + Redis 扩展
│   ├── Phase 3: 权限分层 + Secret State
│   └── Phase 4: 地图/Token 系统（可选）
└── 5.5 体验优化 & 模型调优
    ├── 中文叙事 prompt 优化
    ├── RAG 规则索引优化
    ├── 反刍/幻觉监控指标
    └── A/B 测试不同模型组合
    ↓
Phase 4: 交互式产物生成（待定）
├── 5.6.1 场景插图
├── 5.6.2 战术地图
├── 5.6.3 角色卡/怪物卡渲染
└── 5.6.4 剧情道具
```

### 6.3 关键里程碑与验收标准

#### 里程碑 1：工具层完成（~2 周）
- **验收标准**：
  1. 6 大模块 40+ 工具全部实现，每个工具返回结构化 JSON
  2. 每个工具有独立单元测试
  3. 工具集成现有 `engine/*` 确定性引擎 + `knowledge/*` Qdrant RAG
  4. 严格错误处理（玩家没有剑就不能"用剑攻击"）
  5. 幂等性（同一个工具调用多次不应产生副作用叠加）

#### 里程碑 2：多智能体架构完成（~3 周）
- **验收标准**：
  1. Director Agent 作为新入口，替代原有 `graph.run` 直调
  2. 5 个 Agent 通过 LangGraph StateGraph 条件路由协作
  3. 每个 Agent 有明确的激活时机和职责边界
  4. 端到端跑通：玩家输入 → Director 分类 → 专业 Agent 执行 → 叙事返回
  5. HITL（Human-in-the-Loop）保留，关键判定可暂停确认

#### 里程碑 3：记忆系统升级完成（~2 周）
- **验收标准**：
  1. 三层记忆架构落地：工作记忆（对话缓冲）+ 中期记忆（滚动摘要）+ 长期记忆（Qdrant 向量检索）
  2. Observation/Memory 工具实现（回合后自动提取关键信息）
  3. 记忆检索流水线：语义搜索 → 重要性加权 → 时间衰减 → Rerank → Top-K 注入
  4. Session 存档/读档功能实现
  5. 跨 Session 连续性验证：Session 1 结束 → 生成摘要+持久化+记忆嵌入 → Session 2 开始 → 注入前情提要 → AI 记得上次发生的事

#### 里程碑 4：多人同玩架构升级完成（~2 周）
- **验收标准**：
  1. python-socketio 替换裸 WebSocket，获得 Room/自动重连/消息缓冲能力
  2. Room 生命周期管理实现（创建→等待→游戏中→暂停→销毁）
  3. DM/Player 权限分层实现（DM 看隐藏信息，玩家看过滤后数据）
  4. 断线重连验证：玩家断线 → 30s 内重连 → 恢复到之前的游戏状态
  5. 多人战斗协调验证：先攻序列共享、回合锁定、行动广播、反应协调

#### 里程碑 5：体验优化完成（~2 周）
- **验收标准**：
  1. 中文叙事 prompt 优化完成，叙事质量提升
  2. RAG 规则索引优化完成，检索准确率提升
  3. 反刍/幻觉监控指标实现，可量化监控
  4. A/B 测试不同模型组合完成，有数据支撑的模型选择建议

### 6.4 风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| LLM 不稳定输出 | 工具调用失败、JSON 解析错误 | 强制 JSON schema + 重试 + 前端兜底；structured output / function calling |
| Qdrant 本地模式并发限制 | 多人同时操作时崩溃 | asyncio.Lock 序列化（D&D 本来就是回合制） |
| 法术数据量大 | 加载慢、内存占用高 | 分批导入 + 按需加载；法术速查目录 |
| 角色创建步骤多 | 用户流失 | 向导式 UI + 默认值 + 快速创建模式 |
| 战斗状态复杂易错 | 状态不一致、回溯困难 | 状态机用代码管，LLM 只发指令不记账；每步可审计回溯 |
| 多 Agent 通信开销 | 延迟增加、token 消耗 | 合并同类 Agent；减少不必要的 Agent 间通信；缓存中间结果 |
| 跨 Session 记忆丢失 | 叙事断裂、NPC 忘记玩家 | 三层记忆架构 + Session 结束时生成摘要+持久化+记忆嵌入 |
| 多人并发冲突 | 状态不一致 | asyncio.Lock 序列化 + 权威服务器模式 |
| 成本失控 | token 爆炸、API 费用高 | 分层模型（大模型做叙事、小模型做琐事）、摘要压缩、工具返回结构化短数据而非长文本 |

---

## 七、总结

### 7.1 核心需求汇总

基于前端原型、规则书使用指南和五份调研报告的综合分析，系统的核心需求可以归纳为以下六个方面：

1. **工具层完善**（最高优先级）：实现 6 大模块 40+ 工具，让 AI 有"手"可用。这是多智能体架构的前提，也是让 AI 从"说"到"做"的关键一步。

2. **多智能体架构改造**（高优先级）：将现有单 graph 改造为 5-Agent 协作架构（Director + Narrator + Combat Engine + World Manager + Rule Judge）。这是从"单一聊天框"升级为"分阶段、全流程覆盖的跑团引擎"的核心改造。

3. **记忆系统升级**（高优先级）：实现三层记忆架构（工作记忆 + 中期记忆 + 长期记忆），解决 Session 3 崩塌问题，实现跨 Session 可玩性。这是让 AI 从"一次性对话"升级为"持久化跑团伙伴"的关键。

4. **多人同玩架构升级**（中优先级）：用 python-socketio 替换裸 WebSocket，实现 Room 生命周期管理、DM/Player 权限分层、断线重连。这是从"单人跑团"升级为"多人同桌"的关键。

5. **体验优化 & 模型调优**（中优先级）：中文叙事 prompt 优化、RAG 规则索引优化、反刍/幻觉监控指标、A/B 测试不同模型组合。这是从"能用"升级为"好用"的关键。

6. **交互式产物生成**（低优先级）：场景插图、战术地图、角色卡/怪物卡渲染、战报自动生成。这是从"纯文本跑团"升级为"沉浸式体验"的关键。

### 7.2 与现有文档的关系

本文档（`REQUIREMENTS_ANALYSIS.md`）是需求分析层文档，与现有文档的关系如下：

| 文档 | 层级 | 与本文档的关系 |
|------|------|---------------|
| `PRD.md` | 需求层 | 本文档是 PRD 的扩展和细化，补充了前端原型、规则书和调研报告的需求 |
| `ARCHITECTURE.md` | 架构层 | 本文档的"待实现功能模块详解"部分需要 ARCHITECTURE 的技术支撑 |
| `BUILD.md` | 搭建层 | 本文档的"实施路线图"部分需要 BUILD 的分阶段指导 |
| `RULE_SPEC.md` | 规则层 | 本文档的规则相关需求需要 RULE_SPEC 的规则点支撑 |
| `REFACTOR_PLAN.md` | 改造计划 | 本文档与 REFACTOR_PLAN 互补：REFACTOR_PLAN 关注"按游玩流程重构"，本文档关注"基于前端原型、规则书和调研报告的综合需求分析" |
| `FRONTEND_DESIGN.md` | 前端设计 | 本文档的前端原型需求提取部分与 FRONTEND_DESIGN 互补 |
| `CHANGELOG.md` | 变动日志 | 本文档的实现进度需要在 CHANGELOG 中记录 |
| `DECISIONS.md` | 决策记录 | 本文档的技术决策需要在 DECISIONS 中记录 |

### 7.3 下一步行动

1. **立即可做**：工具层完善（6 大模块 40+ 工具）— 这是让 AI 有"手"可用的基础，也是多智能体架构的前提
2. **短期目标**：多智能体架构改造 + 记忆系统升级（并行）— 从单 graph 升级为 5-Agent 协作架构，解决 Session 3 崩塌问题
3. **中期目标**：多人同玩架构升级 + 体验优化（并行）— python-socketio 升级 → Room 生命周期 → 权限分层 → 地图/Token 系统
4. **长期目标**：交互式产物生成 — 场景插图、战术地图、角色卡/怪物卡渲染、战报自动生成

---

> **文档维护说明**：本文档为需求分析层文档，属于 🟢 稳定参考档。当前端原型、规则书或调研报告有重大更新时，需同步更新本文档。实现进度请在 `CHANGELOG.md` 中记录，技术决策请在 `DECISIONS.md` 中记录。