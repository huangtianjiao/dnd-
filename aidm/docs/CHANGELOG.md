# CHANGELOG — 变动日志

> **记录"做了什么变动"**。倒序（最新在上）。每条尽量带 `文件:位置` 引用，便于回溯。
> 维护时机：每次改代码 / 改文档 / 建库 / 跑通验收后追加一条。
> 配套 `DECISIONS.md`（发现与决策）、`docs/README.md`（索引）。

## 变动分类图例

- `Added` 新增文件/功能/语料
- `Changed` 修改既有行为
- `Fixed` 修复
- `Docs` 文档变动
- `Build` 建库/依赖/部署
- `Verified` 验收/自检通过

---

## [Unreleased] · 进行中

### 2026-07-15 · 多智能体架构 + NPC持久化 + Checkpoint + 动态图片 + Enemy AI

- `Added` **新建 `src/aidm/agents/` 包** — 5-Agent 协作架构。
  - `director.py` — Director Agent：LLM 意图分类 → 条件路由。入口节点，决定走向 Narrator/Combat/World/Rule Judge。
  - `narrator.py` — Narrator Agent：基于骰子结果生成叙事，注入四层记忆（工作/中期/长期/前情提要）到 prompt。
  - `combat_engine.py` — Combat Engine Agent：确定性骰子检定（attack/cast/ability_check），纯代码 LLM 不参与。
  - `world_manager.py` — World Manager Agent：应用状态变更（HP/法术位/物品）、持久化角色卡和场景、推进战斗回合、触发记忆处理。
  - `rule_judge.py` — Rule Judge Agent：hybrid 检索相关规则 + 关键词预检判定参数合规性。拥有否决权。
  - `enemy_ai.py` — Enemy AI Agent：LLM 决策怪物本回合行动。HP<25%且无狂暴→强制逃跑；HP<50%考虑撤退。temperature 0.4。
  - 全部模块语法检查通过 ✓；全部模块导入验证通过 ✓。
- `Added` **新建 `src/aidm/stats/npc.py`** — NPC 人格持久化模块。
  - `NPCProfile` 表：每个 NPC 有独立的人格档案（背景/性格/知识范围/目标/秘密/信任等级/关系状态）。
  - `NPCMemory` 表：NPC 记忆流，每条记忆含 importance(1-10)/turn/timestamp/memory_type。
  - CRUD 操作：`create_npc()` / `get_npc()` / `find_npc_by_name()` / `list_npcs()` / `update_npc()` / `delete_npc()`。
  - 记忆流操作：`add_memory()` / `get_memories()` / `retrieve_npc_memories()`（按重要性+关键词匹配排序）。
  - 关系演化追踪：`update_trust()` 自动更新 relationship_status（hostile/neutral/friendly）；`record_interaction()` 记录互动并更新信任。
  - 信任阈值：TRUST_HOSTILE=-30, TRUST_NEUTRAL=0, TRUST_FRIENDLY=30。信任变化：成功+5, 失败-3, 背叛-50。
  - 含完整自检（9个测试），全部通过 ✓。
- `Added` **新建 `src/aidm/stats/checkpoint.py`** — Checkpoint/Rewind 模块。
  - `create_checkpoint(campaign_id, label)` — 创建战役状态快照（Campaign信息 + 所有角色卡 + 当前场景 + 战斗状态 + 最近10条日志），存储为 JSON 文件。
  - `list_checkpoints(campaign_id)` — 列出战役的所有检查点（按时间戳倒序）。
  - `restore_checkpoint(checkpoint_id)` — 从检查点恢复游戏状态（Campaign信息 + 角色卡 + 场景 + 战斗状态）。
  - `delete_checkpoint(checkpoint_id)` — 删除指定检查点。
  - 快照存储目录：`data/checkpoints/`，文件名格式 `cp_{campaign_id}_{timestamp}.json`。
  - 含完整自检（4个测试），全部通过 ✓。
- `Added` **新建 `src/aidm/brain/image_gen.py`** — 动态图片生成模块。
  - `generate_scene_description(narration)` — 从 DM 叙事中提取视觉描述（英文，适合 Stable Diffusion / DALL-E 风格）。包含场景类型/光照/氛围/关键元素。
  - `generate_scene_image(narration, output_path)` — 生成场景插图。流程：从叙事提取视觉描述 (LLM) → 调用图片生成 API (待接入)。当前返回描述供前端自行渲染。
  - `render_battlefield_ascii(width, height, combatants, obstacles)` — 渲染 ASCII 战术地图。符号：P=玩家 E=敌方 #=障碍 .=空地。
  - 含完整自检（3个测试），全部通过 ✓。
- `Changed` **`src/aidm/brain/graph.py` apply_node()** — 在末尾（步骤6）调用 `process_turn_memories()`。记忆处理失败时静默跳过（`except: pass`），不阻断主流程。用 Log 表行数近似回合序号。
- `Changed` **`src/aidm/api/main.py`** — 新增 `/session/end` 端点。Session 结束时调用 `generate_recap()` 生成浓缩摘要（500-1000字），存入 `Campaign.rolling_summary` 的 `[前情提要]...[/前情提要]` 块。下次 narrate() 时自动注入。
- `Verified` 全部新模块语法检查通过 ✓；全部模块导入验证通过 ✓；npc 自检全部9项通过 ✓；checkpoint 自检全部4项通过 ✓；image_gen 自检全部3项通过 ✓。

### 2026-07-15 · 三层记忆系统实现（工作记忆 / 中期记忆 / 长期记忆）

- `Added` **新建 `src/aidm/brain/memory.py`（~320行）** — 三层记忆系统核心模块。
  - `extract_observations()` — 每回合结束后 LLM 从叙事中提取 1-3 条关键观察，每条含 importance(1-10) + entities + type。参考 Generative Agents 的 poignancy prompt。
  - `store_memory()` — 观察文本经 bge-small 嵌入后存入 Qdrant `dnd_memories` collection（与规则 RAG 的 `dnd_rules` 分离）。payload 含 importance/entities/type/turn/campaign_id/timestamp。point_id = turn*1000 + obs_index 防碰撞。
  - `retrieve_memories()` — 语义检索管线：Qdrant cosine top-20 → 三分量评分（recency=0.99^hours, relevance=cosine, importance=score/10）→ 加权求和(0.5/3.0/2.0) → rerank → top-5。参考 Generative Agents `gw=[0.5, 3, 2]`。
  - `compress_rolling_summary()` — 每10回合用 LLM 将最近10回合压缩成3-5句摘要，追加到 `Campaign.rolling_summary`。
  - `process_turn_memories()` — 完整管线入口：提取观察 → 存储长期记忆 → 压缩摘要。在 `apply_node` 末尾调用。
  - 含完整自检（5个测试），全部通过 ✓。
- `Changed` **`src/aidm/brain/graph.py` narrate() 节点** — 注入三层记忆到 LLM prompt。
  - ① 工作记忆：`store.get_recent_logs(camp_id, n=6)` 获取最近6回合对话原文注入 prompt（此前 narrate 完全看不到历史）。
  - ② 中期记忆：`store.get_summary(camp_id)` 读取 `Campaign.rolling_summary` 截取前500字注入 prompt（此前 rolling_summary 只写不读）。
  - ③ 长期记忆：`retrieve_memories(camp_id, query)` 语义检索 top-5 记忆注入 prompt（try/except 保护，检索失败不阻断叙事）。
  - docstring 更新：标注三层记忆注入点 ①②③。
- `Changed` **`src/aidm/brain/graph.py` apply_node() 节点** — 在末尾（步骤6）调用 `process_turn_memories()`。记忆处理失败时静默跳过（`except: pass`），不阻断主流程。用 Log 表行数近似回合序号。
- `Added` **`src/aidm/stats/store.py` 新增 `get_recent_logs()`** — 查 Log 表获取最近 N 条记录（时间正序），工作记忆数据源。
- `Verified` 语法检查通过（memory.py / graph.py / store.py）；store 自检通过 ✓；memory 自检全部5项通过 ✓；graph.py 导入成功。

### 2026-07-15 · 架构文档全面梳理（ARCHITECTURE.md v3→v4）

- `Docs` **ARCHITECTURE.md 从 v3 升级到 v4**。本次梳理对照实际代码（brain 13 子模块、data 8 子模块、engine 11 模块、api 39 端点 + ws.py WebSocket 同桌层、tests/ 7 文件 138 测试、ui/ 双前端架构），全面订正架构文档：
  - §0 文档索引与当前进展：补全模块清单（brain 13/data 8/engine 新增 4）、API 端点数（6→39）、WebSocket 同桌层、测试体系（138 测试）、前端双架构（静态 HTML + Next.js 14）。变动标注：v4。
  - §3 总体架构图：从"交互层→AI DM 大脑→引擎层→状态层"四层更新为六层架构（前端交互层/API 接口层/AI DM 大脑/规则知识库/引擎层/状态层），加入 WebSocket 实时同桌层和前端双架构。变动标注：v4。
  - §5.4 AI DM 大脑：resolve 节点的 action_type 分派从"attack/cast/ability_check/start_combat"扩展到 8 种（新增 rest/social/levelup/travel）。变动标注：v4。
  - §5.5 交互层：从"CLI+API 已就绪，Next.js 待 P5"更新为"CLI+API+前端 已就绪"。新增 WebSocket 实时同桌层和前端双架构描述。变动标注：v4。
  - §5.6 brain/ 业务模块清单（新增）：13 个子模块（graph/state/llm/world/adventure_builder/campaign_manager/char_create/exploration/levelup/loot/loot_distribution/plane_travel/rest/room/session0/social/stronghold）。
  - §5.7 data/ 游戏数据模块清单（新增）：8 个数据表模块（backgrounds/classes/equipment/feats/magic_items/planes/races/spells/strongholds）。
  - §5.8 engine/ 引擎模块清单（新增）：11 个模块（dice/check/damage/conditions/combat/actions/concentration/core_loop/opportunity_attack/spellcasting）。
  - §7 技术选型表：新增 WebSocket（python-socketio）、前端双架构（静态 HTML + Next.js 14）、测试体系（pytest 138 测试）。原 v3 表中"前端: Next.js + shadcn/ui + Tailwind (P5 可选)"已更新为实际落地的双前端架构。变动标注：v4。
  - §8 项目目录结构：从概要列表更新为完整目录树，反映 brain 13 子模块、data 8 子模块、engine 11 模块、tests/ 7 文件、ui/ 双前端架构。变动标注：v4。
  - §9 分阶段实施表：从"P0-P5 六阶段"扩展为"P0-P5 + WebSocket 同桌 + 测试体系 八项"。P5 前端状态从"⏳ 可选"更新为"✅ 完成"。变动标注：v4。
  - §10.1 REST API 端点清单（新增）：39 个路由端点，按功能域分组（健康检查/战役管理/角色管理/聊天跑团/场景管理/世界设定/战斗状态/怪物检索/魔法物品/加入战役/在线玩家/专长系统/同调系统/战利品/房间管理/据点系统）。
  - §10.2 WebSocket 事件清单（新增）：16 个 Socket.IO 事件（connect/disconnect/action/join/leave/result/processing/player_acting/scene_update/combat_update/turn_advanced/round_end/monster_turn/monster_action/combat_end/player_ready/character_update/error）。
  - 文档末尾：版本标记从 v3.0 更新为 v4.0，添加变动标注约定说明。
- `Docs` DECISIONS 新增 D-022（架构文档全面梳理 ARCHITECTURE.md v3→v4），记录梳理方法、发现的差异点和订正内容。

### 2026-07-15 · 前端 bug 修复 + 后端单元测试 + Next.js 融合

- `Fixed` **app.js 致命 bug 修复**。删除 `ui/static/app.js:336-387` 孤儿 `switch(d.type)` 死代码块。该代码在脚本顶层执行时求值 `d.type`，而 `d` 不存在，抛 `ReferenceError: d is not defined`，导致脚本在第 336 行加载期崩溃，后续的回车发送绑定（第 562-564 行）永远不执行。修复后 app.js 从 564 行缩减到 512 行，页面加载无 Console 错误，回车可发送消息。
- `Added` **后端单元测试套件（7 个文件，138 个测试全通过）**：
  - `tests/test_dice_engine.py`（23 通过）— R-CHK-024 属性调整值, R-CHK-015 熟练加值表, R-CHK-025 骰子表达式, R-CMB-029 重击翻倍, R-CHK-004/005 优劣势
  - `tests/test_check_system.py`（20 通过）— R-CHK-009 DC 表, R-DM-002 豁免 DC, R-CHK-010 属性检定, R-CHK-011 豁免(放弃), R-CMB-017/022/023 攻击命中/天然 20/天然 1
  - `tests/test_damage_system.py`（29 通过）— R-QCK-002 伤害管线顺序, R-DMG-006 免疫→0, R-DMG-003 抗性减半/易伤翻倍, R-DMG-009 临时 HP 优先扣, R-DMG-017 死亡豁免(≥10 成功/天然 1 两次失败/天然 20 恢复 1HP/3 稳定/3 死亡)
  - `tests/test_conditions.py`（27 通过）— R-GLS-043 状态不叠加, R-GLS-047 力竭累加(0..6), R-GLS-050 失能性状态, 攻防优劣势(R-GLS-044/051/052/055/058)
  - `tests/test_combat_flow.py`（24 通过）— R-CMB-002 先攻检定, R-GLS-009 突袭劣势, R-CMB-004 回合动作经济, R-CMB-005 免费物件交互, R-CMB-030/031 移动消耗, R-CMB-037 体型空间, R-GLS-013 专注维持 DC
  - `tests/test_api_endpoints.py`（8 通过）— GET /health, POST /campaign + POST /character, GET /character/{id} 完整角色卡(含属性调整值+熟练加值), GET /campaigns, GET /combat/{id}, GET /monster/{name}, GET /magic-items, GET /feats
  - `tests/test_e2e_flow.py`（7 通过）— 纯引擎端到端(完整战斗回合/攻击到伤害管线/死亡豁免完整周期/休息与恢复) + API 端到端(建战役+角色/获取场景和战斗/获取战役完整状态)
- `Added` **Next.js 前端融合**。将 `ui/static/app.js` 的 Socket.IO 多人逻辑、三栏布局、XSS 安全渲染迁入 `ui/app/page.tsx`（671 行），同时保留 `@3d-dice/dice-box` 3D 骰子动画。安装 `socket.io-client@4.8.3` 依赖。统一为单一 Next.js 前端，包含：主菜单（开始新游戏/继续游戏/加入房间）、三栏布局（左栏角色卡+右栏战斗面板+中栏主舞台）、Socket.IO 实时通信、3D 骰子动画、Toast 通知系统。`npx next build` 构建成功。
- `Docs` DECISIONS 新增 D-021（前端 bug 修复 + 后端单元测试 + Next.js 融合），记录本次改动的方法、结论和待办。

### 2026-07-15 · 全模块完整性审查 + 规则书对照验证

- `Added` 新建 `scripts/test_all_modules.py`（全模块功能验证脚本，63项测试）。
- `Verified` **全模块功能验证通过（63/63）**。编写 `scripts/test_all_modules.py` 系统性测试脚本，覆盖 8 个引擎模块、10 个数据模块、15 个大脑模块、2 个 API 模块、2 个统计模块、7 个知识库模块。所有模块导入成功、核心功能验证通过。
- `Verified` **规则书对照验证通过（14项核心规则点）**。逐条对照 D&D 5E 规则书验证代码实现正确性：
  - R-CHK-025: d20骰子范围[1,20] ✓
  - R-CHK-024: 属性调整值 floor((score-10)/2) ✓
  - R-CHK-004/005: 优势取高/劣势取低/同时存在抵消 ✓
  - R-CMB-029: 重击伤害骰翻倍(常数不加倍) ✓
  - R-CMB-022/023: 天然20必命中+重击/天然1必失手 ✓
  - R-CMB-004: 回合动作经济(1动作/回合) ✓
  - R-CMB-001: 一轮=6秒 ✓
  - R-SPL-020: 专注豁免DC=max(10,floor(dmg/2))至高30 ✓
  - R-SPL-002/003: 法术位消耗与恢复(5级=4/3/2) ✓
  - PHB第五章专长分类(起源10/通用43/战斗风格9/传奇恩惠12=74个) ✓
  - DMG第七章魔法物品稀有度(普通16/非普通11/珍稀3=30个) ✓
  - DMG第八章据点系统(特色设施29/基础设施6/事件11) ✓
  - DMG第六章宇宙学(29个位面) ✓
  - PHB基础数据(种族10/职业12/背景16) ✓
- `Docs` 本次审查确认：**所有模块均为完整实现，无空文件或存根**。之前子智能体已完成全部工作，包括专长系统(74个)、魔法物品系统(30个+同调/鉴定)、冒险创建工具(adventure_builder.py+campaign_manager.py)、据点系统(29种设施+11种事件)、宇宙学(58个位面+位面旅行)。多人同玩架构(python-socketio)也已落地。
- `Docs` DECISIONS 新增 D-020（全模块完整性审查 + 规则书对照验证），记录审查方法、结论和验证结果。

### 2026-07-14

- `Docs` 订正 ARCHITECTURE.md → v3：§0 文档索引补 4 新档+进展校准；§5.1 RAG 改三语料/Qdrant本地/bge-small/hybrid/别名/评测；§5.4 编排补 brain/graph 节点流+MemorySaver；§5.5 交互层补 cli.py+api/main；§6 数据模型对齐 models.py（rule_chunk→Qdrant、Character 字段、current_index/active/exhaustion/死亡计数）；§7 选型订正（Qdrant本地/bge-small/deepseek）；§8 目录补 knowledge9模块/brain graph/api/cli/config.py/docs新档；§9 阶段表统一 P0-P5 划分+状态列；§10 待确认标已落地。依据 D-001~D-012。 `aidm/docs/ARCHITECTURE.md`
- `Docs` 订正 BUILD.md：§1 环境去 docker；§3 结构补实际模块；§4 自检补 P0-P4 入口；§5 P2 路径订正(scripts→knowledge)+部署去 docker；§5 P3 prompts.py→内嵌+MemorySaver；§5 P4 端点订正；§6 config.yaml→config.py/.env。 `aidm/docs/BUILD.md`
- `Changed` DECISIONS D-008 状态 🟡→✅（brain/graph.py 已落地，P3 完成；核对期间项目被推进，见 D-013）。
- `Added` DECISIONS D-013（核对期间项目被推进：graph.py/api/main/cli.py 落地、§0 自更新，订正基线变化）。
- `Docs` DECISIONS D-009 补充：经 graph.py 验证，ability_check 的 proficient 由 LLM classify 给出（设计取舍），非纯遗漏。
- `Docs` 新建本档（CHANGELOG）、`DECISIONS.md`、`docs/README.md`，建立"变动 + 发现"双轨记录体系。
  背景：核对发现现有架构文档多处落后于代码（详见 `DECISIONS.md` 2026-07-14 各条），需一个常更载体把变动与发现持续落进去。
  `aidm/docs/CHANGELOG.md` · `aidm/docs/DECISIONS.md` · `aidm/docs/README.md`

---

## 维护约定

1. **日期分组**：同一天的多条变动并列，不重复写日期头。
2. **倒序**：新条目加在 `## [Unreleased]` 下、日期小节顶部。
3. **带引用**：能定位到 `文件:行` 或 `规则: R-XXX-NNN` 就带上，方便回溯。
4. **不发版也记**：项目未正式发版，用日期即可；将来若发版可加 `## [vx.y.z] - 日期` 锚点。
5. **与 DECISIONS 的边界**：CHANGELOG 记"做了什么"（动作）；DECISIONS 记"为什么这么做 / 发现了什么 / 待办"。一次改动可能两边都留痕：改动落 CHANGELOG，背后的判断/发现落 DECISIONS。
