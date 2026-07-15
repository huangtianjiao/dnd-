# DECISIONS — 发现与决策记录

> **记录"有什么发现 / 为什么这么做 / 待办什么"**。ADR 式：背景 → 决策/现状 → 后果 → 关联。
> 配套 `CHANGELOG.md`（已发生的变动动作）。
> 维护时机：做完一次技术选型、跑完一轮验收、或核对出文档↔代码漂移时，追加一条。

## 结构约定

每条编号 `D-NNN`，含：

- **背景**：问题/触发点是什么。
- **现状/决策**：实际怎么做 / 选了什么（已落地的写「现状」，未拍板的写「决策建议」）。
- **后果**：带来的影响、限制、需注意的点。
- **待办**：尚需跟进的事项（若无则省）。
- **关联**：`文件:行` / `规则: R-XXX-NNN` / 相关文档章节。

状态图例：`✅ 已落地` · `🟡 进行中` · `🔵 待办` · `🔴 待确认`

---

## 2026-07-14 · 首批核对发现（文档↔代码漂移）

> 本批为建立记录体系时，对 `aidm/docs/` 与 `src/aidm/` 全量核对得出的发现。架构文档的订正（第 1 步外科式订正）尚未进行，订正完成后往 `CHANGELOG.md` 补条。

### D-001 · 向量库改用 Qdrant 本地文件模式（非 docker 服务） ✅

- **背景**：`ARCHITECTURE.md §7` 选型写"Qdrant（独立服务，docker）"，`BUILD.md §5 P2` 步骤写 `docker run -p 6333:6333 qdrant/qdrant`。
- **现状**：`indexer.py:21-26` 用 `QdrantClient(path="...rules.db")` 本地文件模式，不起服务、免 docker。`data/rules.db/meta.json` 确认三集合（`dnd_rules`/`dnd_rule_text`/`dnd_rule_spec`，512维 Cosine）已建库。
- **后果**：部署简化、存档即拷一个 `.db` 文件；但**单进程**、不支持并发服务访问。对当前单机跑团足够；将来多客户端并发需切回 server 模式。
- **关联**：`src/aidm/knowledge/indexer.py:17-26` · ARCHITECTURE §7 / §5.1 · BUILD §5 P2

### D-002 · 嵌入用本地 bge-small-zh-v1.5（512维），非 API / 非 bge-m3 ✅

- **背景**：`ARCHITECTURE §7/§5.1` 写"优先 API embedding；无则本地 bge-m3"，且 §5.1 提"sqlite-vec"。
- **现状**：`config.py:34-36` 默认 `embedding_model=BAAI/bge-small-zh-v1.5`、`embedding_dim=512`；`embedding.py:17` 走 HF 镜像 `hf-mirror.com` 下载，CPU 推理、归一化向量。`bge-m3` 留为可选（更强但 2.3GB/1024维，需重建集合）。
- **后果**：检索够用且轻（模型 ~95MB）；中文规则关键词仍偶有偏移（见 D-005 hybrid 弥补）。`sqlite-vec` 路线未采用——规则入 Qdrant。
- **关联**：`src/aidm/config.py:34-36` · `src/aidm/knowledge/embedding.py:17,32` · ARCHITECTURE §7/§5.1

### D-003 · LLM = deepseek-v4-flash @ senseaudio 网关（§10 待确认已落地） ✅

- **背景**：`ARCHITECTURE §10` 把 base_url / model / 是否有 embedding / key 全列 `[ ]` 待确认。
- **现状**：`config.py:27-29` 已定——`base_url=https://api.senseaudio.cn/v1`、`model=deepseek-v4-flash`、key 读 `.env` 的 `key=` 字段（`D:\game\dnd\.env`）。`brain/llm.py` 用 `langchain_openai.ChatOpenAI`（OpenAI 兼容协议）封装。
- **后果**：§10 的 4 个待确认项实质已解决；文档可标"已确认"。embedding 仍走本地（不占该网关）。
- **关联**：`src/aidm/config.py:27-29` · `src/aidm/brain/llm.py` · ARCHITECTURE §10

### D-004 · 三套检索语料 + 三 Qdrant 集合（非单一 data.js） ✅

- **背景**：`ARCHITECTURE §5.1` 描述为单一 data.js 语料；`PRD §4 P2` 也按单语料框架。
- **现状**：实际三套语料各建一集合：
  | 集合 | 语料 | 规模 | 角色 |
  |---|---|---|---|
  | `dnd_rules` | data.js | 6238 条 | 数据语料（怪物/物品/法术正文） |
  | `dnd_rule_text` | rules_text | 141 页 .txt | 判定规则文本 |
  | `dnd_rule_spec` | RULE_SPEC | 400 条结构化 | **最高信号**校验语料（含精确公式/审计） |
- **后果**：检索精度与校验能力远超单一语料；但语料维护面变宽（三套各自建/重建）。`indexer.py` 提供 `build_index`/`index_text_files`/`index_chunks` 三入口分别建。
- **关联**：`src/aidm/knowledge/indexer.py:42-195` · `data/rules.db/meta.json` · ARCHITECTURE §5.1

### D-005 · Hybrid 检索：BM25(字符级) + 向量 RRF 融合 ✅

- **背景**：`ARCHITECTURE §5.1` 只写"语义检索 top-k + 标签过滤"。纯向量在中文规则关键词（"摔绊""豁免DC""+2"）上易偏移。
- **现状**：`hybrid.py` 实现字符级+ASCII词级分词的 BM25，与向量 top-N 做 RRF（Reciprocal Rank Fusion, k=60）融合，输出 top-k。目前作用于 `dnd_rule_spec`（`search_spec_hybrid`）。
- **后果**：关键词精确命中补回，规则检索更稳。BM25 语料懒加载（`parse_rulespec` 解析 400 条）。
- **关联**：`src/aidm/knowledge/hybrid.py` · `verifier.py:25`（`gather_evidence` 默认走 hybrid）

### D-006 · 别名富化（aliases.py）桥接"玩家词↔规则原词" ✅

- **背景**：玩家说"摔绊"，规则原文用"徒手打击/推撞"——向量+BM25 都未必映射，导致校验 airtight 不住。
- **现状**：`aliases.py` 给机制类规则（R-GLS-034 等）配玩家同义词串，`parse_rulespec.py:29-30` 在建库时把 `【别名】...` 注入 chunk body 前部，让"摔绊"稳定命中 R-GLS-034。
- **后果**：检索召回显著提升（见 D-007 量化）。别名表需随新机制规则手工扩充。
- **关联**：`src/aidm/knowledge/aliases.py` · `parse_rulespec.py:29-30`

### D-007 · 检索评测集：15 条查询 recall@3/5 🔵

- **现状**：`eval_retrieval.py` 内置 15 条 `(查询, 期望命中规则ID集合)`，量化纯向量 vs hybrid 的 recall。`verifier.py:46` 默认 `limit=8`——因 top-3 常被"结果类"规则占据，机制类规则多在 top5-8，LLM 通读 8 条即可引用正确机制。
- **后果**：检索质量可量化、可回归。评测集偏小（15 条），后续随真实用例扩充。
- **关联**：`src/aidm/knowledge/eval_retrieval.py` · `verifier.py:44-55`

### D-008 · P3 编排层已落地（brain/graph.py） ✅ 已落地

- **背景**：本条原记"P3 脚手架就位、graph.py 未落地 🟡"（2026-07-14 早期快照）。核对期间项目被推进，graph.py 已落地（见 D-013）。
- **现状**：`brain/graph.py`（474 行）LangGraph StateGraph 硬性判定链已端到端跑通：classify→retrieve→verify→[retrieve_retry/confirm HITL]→resolve(纯代码骰子)→narrate→apply。覆盖 attack/cast/ability_check/start_combat；`MemorySaver` checkpointer + interrupt(HITL)；prompt 内嵌于 classify/narrate 节点（无独立 prompts.py）。`brain/llm.py`(deepseek 客户端) + `brain/state.py`(GameState 含 hitl/confirmed/combat) 配套。
- **后果**：P3 已完成，ARCHITECTURE §0 / BUILD §5 P3 均标 ✅。HITL 经 `/chat/resume` 恢复。
- **关联**：`src/aidm/brain/graph.py` · ARCHITECTURE §5.4 · BUILD §5 P3

### D-009 · Character 表缺口：skill_prof / save_prof 未持久化 🔴

- **背景**：`ARCHITECTURE §6.2` 表结构含 `skill_prof_json`、`save_prof_json`、`proficiency_bonus`、`alignment`、`background`、`hit_dice_json`、`features_json`、`initiative_mod` 等列。
- **现状**：`stats/models.py:43-72` 的 `Character` 表：
  - ❌ 缺 `skill_prof_json` / `save_prof_json`（**技能/豁免熟练无法持久化**——做属性检定时无法知道角色擅长哪些技能、是否该加熟练加值）
  - ❌ 缺 `alignment`/`background`/`hit_dice_json`/`features_json`/`initiative_mod`；`proficiency_bonus` 改为 `prof()` 按等级算（无列）
  - ➕ 多 `exhaustion`/`death_successes`/`death_failures`/`stable`/`dead`/`campaign_id`；`spellcasting_json` 拆成 `spell_slots_json`+`known_spells_json`；`hp_temp`→`temp_hp`、`class`→`char_class`
- **后果**：文档与 schema 实质偏离。经 `brain/graph.py` 验证（`_resolve_ability_check` 用 `proficient=bool(it.get("proficient"))`）：熟练与否由 LLM classify 给出、不从角色卡读——属**设计取舍**，非纯遗漏。但持久化缺失仍是潜在缺口（重载/多角色/历史回放场景下熟练无法回溯）。
- **待办**：仍需用户拍板——维持"LLM 每轮判 proficient"现状，还是补 `skill_prof_json`/`save_prof_json` 列持久化（若补需迁移）。
- **关联**：`src/aidm/stats/models.py:43-72` · ARCHITECTURE §6.2

### D-010 · 配置走 .env + config.py（非 config.yaml） ✅

- **背景**：`BUILD §6` 写"aidm/config.yaml（待建）"并给 yaml 片段。
- **现状**：`config.py` 用 `pydantic-settings` 的 `BaseSettings`，读 `D:\game\dnd\.env`（`key=`/`doc1`/`doc2`），`@lru_cache` 单例。无 config.yaml。
- **后果**：密钥不入仓更安全；但配置项分散在代码默认值 + .env 两处，BUILD 的 yaml 片段过时。
- **关联**：`src/aidm/config.py:14-46` · BUILD §6 · `.env`

### D-011 · topics 页数自相矛盾：8644 vs 7523 🔴

- **背景**：ARCHITECTURE §0/§1.2/§8、PRD §1/§7、BUILD 均写 **8644 页**；IMAGE_ASSETS §2 实测写 **46 本 / 7523 个 HTML 页面**。
- **现状**：两套数字未统一。推测 8644 = `webhelpcontents.htm` 目录项数，7523 = 实际 `.htm` 文件数（含万象无常书 pic 等）。
- **待办**：跑一次 `find topics -name '*.htm' | wc -l` 实测，统一全文档口径。
- **关联**：ARCHITECTURE §1.2 · IMAGE_ASSETS §2 · PRD §7

### D-012 · 图片 batch2 刚起步（3/500） 🟡

- **现状**：`images_manifest_batch2.json` 显示 `count=3`、`summary{ok:3}`、`generated_at=2026-07-14 13:56`，仅 3 张 magic-items。IMAGE_ASSETS §5 标"~500 进行中"方向正确，但实际进度为初期。
- **关联**：`aidm/data/images/images_manifest_batch2.json` · IMAGE_ASSETS §5

### D-013 · 核对期间项目被推进：订正基线变化 🟡

- **背景**：建立记录体系时（2026-07-14）做的"文档↔代码漂移"清单（D-001~D-012）基于某时间点快照。核对期间（同日稍后）项目代码与 ARCHITECTURE §0 被大幅推进。
- **现状**：新增 `brain/graph.py`(474行 LangGraph 编排)、`api/main.py`(FastAPI)、`cli.py`(CLI 交互)；ARCHITECTURE §0 自更新到 P2/P3/P4 完成。原 D-008（graph.py 未落地）据此自愈、状态改 ✅。
- **后果**：漂移清单部分条目（D-008）已过时，需就地订正状态。本次订正 ARCHITECTURE/BUILD 以"当前代码 + §0"为基线，而非旧快照。教训：长任务核对期间代码会变，记录体系应允许就地更新状态（本档维护约定第2条已据此运作）。
- **关联**：影响 D-008/D-009 · ARCHITECTURE §0 v3 · BUILD §5

---

## D-013 骰子动画库调研 + 集成 ✅已落地

- **背景**：玩家需要"自己点击掷骰"的参与感，要有视觉动画。硬性判定要求骰子值由后端(secrets RNG)算出，前端只做动画展示——不能前端自己随机。
- **调研**（基于训练知识，WebSearch 不可用）：
  | 库 | 类型 | 依赖 | 能掷到指定值 | 推荐度 |
  |---|---|---|---|---|
  | @3d-dice/dice-box | CSS3D+BabylonJS 物理 | npm | 自带随机，后端值覆盖 | ⭐⭐⭐⭐⭐ 已集成到 Next.js |
  | Dice3D (Three.js) | 3D物理 | Three.js+cannon.js | 可设最终面 | ⭐⭐⭐ 重 |
  | CSS-only 骰子 | CSS transform | 无 | 天然可控 | ⭐⭐⭐⭐ HTML版用 |
  | dice-roller-parser | 纯数学无动画 | npm | N/A | 配合视觉库 |
- **实际集成与后续调整**：
  - **Next.js 版**（`ui/app/page.tsx`）：`npm install @3d-dice/dice-box@1.1.4`（BabylonJS 物理引擎+Web Worker+OffscreenCanvas）；assets 拷到 `public/assets/dice-box/`；page.tsx 用 `useEffect` 动态 `import('@3d-dice/dice-box')`（SSR 安全）；`diceBox.roll('1d20')` 3D 物理动画 + `fetch('/chat')` 后端值**并行**→后端 d20 值大字覆盖（权威）→叙事。`dice-box.d.ts` 类型声明解决 TS 编译。`npm run build` 绿（Route / 3.29kB）。
  - **HTML 版**最初实现了 CSS-only 3D 翻转 + d20 值揭示（命中绿/未中红/重击金），后根据用户反馈"掷筛动画太久/删掉掷筛"，**已删除 HTML 前端骰子动画 overlay**，改回直接显示后端骰子文本结果；按钮文案由"🎲掷骰"改回"行动"。多人实时版以行动广播为主。
  - **硬性判定不破**：不论是否展示动画，骰子值始终来自后端 secrets RNG（前端不随机）。
- **后果**：保留 Next.js 3D 骰子库调研与构建能力，当前 HTML/多人实时版界面不再显示前端骰子动画，只展示后端权威骰子值与结果。
- **关联**：`ui/app/page.tsx` · `ui/static/index.html` · `ui/dice-box.d.ts` · `ui/public/assets/dice-box/` · ARCHITECTURE §0 · PRD §4 P5

---

## D-014 叙事/世界层（brain/world.py）✅已落地

- **背景**：之前系统是"一个输入框对着虚空打字"，缺跑团该有的完整背景（DM 设定世界/开场场景/氛围/在场 NPC/可做之事）。用户指出不完整。
- **调研**：读城主指南 2024「运作游戏」章（叙事/运作探索/决定掷骰结果/冒险速查），把 DM 叙事技巧（简洁/多感官氛围/区分选项/不臆测角色行动/秘密与发现）和四问检定法写进 `world.py` 的 system prompt。
- **现状/决策**：
  - `brain/world.py`：`open_campaign(setting,tone)` → LLM 生成完整背景+当前场景(地点/时间/多感官氛围/在场NPC/可感知选项/可做之事)，持久化 Campaign.setting + Scene。
  - `graph.py narrate`：在 `scene_context` 中叙事（非虚空）+ 输出 `scene_update`（行动后场景推进）+ `action_options`（3 个可点击选项，DMG 区分选项）。
  - `models.py`：Campaign 加 setting/tone；Scene 加 situation/atmosphere/exits_json。
  - `store.py`：save_scene/get_scene/set_campaign_setting + `_migrate`（老库自动 ALTER TABLE 补列）。
  - API：`POST /open` + `GET /scene`。
  - 前端：场景面板（地点/时间/氛围/在场/可做之事/场景叙事）。
- **后果**：跑团循环完整：DM 框定场景+3选项 → 玩家选/输入 → 硬性骰子 → DM 叙事+场景推进+新选项。不再是"虚空打字"。
- **关联**：`brain/world.py` · `brain/graph.py:260` narrate · `stats/models.py:132` Campaign · `stats/store.py:_migrate` · `api/main.py:/open` · DMG 叙事 R-DM · ARCHITECTURE §0

---

## D-015 全套 VTT 界面（3 栏布局）✅已落地

- **背景**：用户要求"完整界面"——角色数值 + 场景 + 怪物数值 + 3 可选项 + 骰子，不是单纯输入框。
- **调研**：参考 Roll20（地图+角色卡+战斗追踪+聊天）/ Foundry VTT（Actor Sheet+Item+Combat Tracker+Chat Cards）/ D&D Beyond（角色卡：6属性+调整值/HP/AC/技能/状态/法术位/装备）。
- **现状/决策**：3 栏 CSS grid 布局单页 HTML：
  - 左栏：角色卡面板（HP 血条渐变色 + 6 属性值+调整值 + AC/速度/熟练 + 状态标签 + 法术位）
  - 中栏：场景面板（地点/时间/氛围/在场/可做之事/场景叙事）+ 叙事日志 + 3 可选按钮 + 自由输入
  - 右栏：战斗追踪器（先政顺序/回合/HP 条）+ 怪物数值（AC/HP/攻击/CR 从 data.js RAG 检索）
- **API 扩展**：`GET /character/{id}` 返回全数据(属性+mod+HP/AC/熟练/状态/法术位)；`GET /combat/{id}` 战斗状态；`GET /monster/{name}` 怪物检索；`POST /open`+`POST /chat` 返回 action_options。
- **后果**：玩家看到完整桌面信息，3 个可点击选项（DMG 区分选项），不再是"虚空输入框"。
- **关联**：`ui/static/index.html` · `api/main.py` · ARCHITECTURE §0 · PRD §4

---

## D-016 端口 8080 + dnd_rules 重建 ✅已落地

- **背景**：用户要求换端口（之前 8000 测试）；dnd_rules 集合（6238 怪物/物品数据语料）被清库后需重建以支持 `/monster` 端点。
- **现状/决策**：`api/main.py __main__` 端口改为 8080；`dnd_rules` 集合重建完成（6238 条全量索引），`/monster/{name}` 可检索怪物属性块。
- **后果**：服务运行在 `http://127.0.0.1:8080`；怪物数值面板可用。
- **关联**：`api/main.py:__main__` · `knowledge/indexer.py:build_index` · ARCHITECTURE §0

---

## D-017 WebSocket 实时同桌（多人在线跑团）✅已落地

- **背景**：用户要求 B 方案——真正的"同时在线"多人跑团。一人行动，其他玩家实时看到 DM 叙事+骰子+场景更新。
- **现状/决策**：
  - `api/ws.py`：`ConnectionManager`（campaign_id → WebSocket 连接列表）+ `websocket_endpoint`。
    - `connect/disconnect`：管理连接，通知全员 join/leave。
    - `broadcast(campaign_id, message, exclude?)`：广播给同战役所有连接。
    - `is_player_turn`：战斗中按先政检查是否轮到你；非战斗时自由行动。
    - `broadcast_state`：广播场景更新 + 战斗/回合信息。
  - `asyncio.Lock` 序列化 `graph.run`（Qdrant 本地模式非线程安全 + D&D 本来就是回合制 → 天然序列化不违和）。
  - `run_in_executor`：在线程池跑同步的 graph.run（LLM 阻塞调用不阻塞事件循环）。
  - API：`POST /join`（加入已有战役，创建角色，返回 WS URL）+ `GET /players/{id}`（在线玩家+当前回合）+ `WS /ws/{campaign_id}?character_id=X&name=Y`。
  - 前端：WebSocket 客户端（connectWS + ws.onmessage 广播处理 + ws.send 发行动）+ 加入表单（Campaign ID → /join → 连接 WS）+ 玩家列表 + 回合提示。
  - 消息类型：join/leave/result/processing/player_acting/scene_update/combat_update/character_update/turn/error。
- **e2e 验证**：双连接（阿拉贡+梅莉）→ 玩家1行动"检查地窖" → processing → RESULT(d20=14,后端secrets,叙事"蹲下身...铁锈味...抓痕...") → 玩家2收到 player_acting 广播。
- **后果**：真正的"同桌多人在线跑团"——一人掷骰全员看到，战斗按先政回合协调，场景实时同步。非战斗时自由行动（先到先得）。
- **关联**：`api/ws.py` · `api/main.py:/join+/players+/ws` · `ui/static/index.html` WebSocket 客户端 · ARCHITECTURE §0 · PRD §4

---

## D-018 游戏主菜单 + 继续游戏 ✅已落地

- **背景**：用户指出应像正规游戏一样有主菜单（开始新游戏/继续游戏/加入房间），不是一上来就是世界设定输入框。
- **现状/决策**：
  - 前端 3 个主菜单卡片：**🎲开始新游戏**（设定世界→DM开场→WS连接）/ **📖继续游戏**（GET /campaigns 列出已保存战役→选一个→GET /campaign/{id}/state 加载场景+角色+战斗+摘要→WS连接继续）/ **🚪加入房间**（输入房间号→POST /join→WS连接）。
  - API 新增：`GET /campaigns`（列出所有战役）+ `GET /campaign/{id}/state`（加载战役完整状态：战役信息+场景+角色列表+剧情摘要+战斗）。
  - store 新增：`list_campaigns()`。
  - 继续游戏流程：列出战役 → 点选 → 加载状态(场景/角色/战斗/摘要) → WS 连接 → 继续。
- **后果**：像正规游戏主菜单——3个明确选项，每种游戏方式都有独立流程。
- **关联**：`ui/static/index.html` 主菜单 · `api/main.py:/campaigns+/campaign/{id}/state` · `stats/store.py:list_campaigns` · ARCHITECTURE §0

---

## D-019 Phase B/D/G 并行实现（6子智能体）✅已落地

- **背景**：改造计划 v2 定义了 9 个 Phase，其中 B（角色创建）、D（战斗流程）、G（施法流程）是 P0/P1 优先级。用户授权开 6 个子智能体并行工作。
- **执行方式**：3 个子智能体分别负责 Phase B/D/G，每个先读 `5echm_web/topics/` 规则书原文，再编码，最后自检。
- **Phase B 交付**（209项自检通过）：
  - `data/classes.py`：12个核心职业数据表（生命骰/主属性/豁免熟练/技能选择/护甲武器熟练/子职）
  - `data/races.py`：10种种族数据表（属性加成/速度/黑暗视觉/特质/子族）
  - `data/backgrounds.py`：16种背景数据表（起源专长/技能熟练/工具熟练/装备）
  - `brain/char_create.py`：五步车卡流程 + 衍生数值计算（标准阵列/购点法27点/4d6弃最低）
- **Phase D 交付**（6模块自检通过）：
  - `engine/combat.py` 扩展：Combatant 数据结构扩展（position/speed_remaining/reach/group_id）、动作经济管理、移动与位置辅助
  - `engine/actions.py` 新建：11种战斗动作分派器（attack/dash/disengage/dodge/help/hide/magic/ready/search/study/utilize）
  - `engine/opportunity_attack.py` 新建：借机攻击触发条件判定 + 近战攻击检定
- **Phase G 交付**（3文件自检通过）：
  - `data/spells.py` 新建：12个法术数据表（火焰箭/魔法飞弹/火球术/闪电束/治愈真言/护盾术等）+ 法术位进度表(1-20级) + 施法属性映射
  - `engine/concentration.py` 新建：ConcentrationManager 集中维持引擎（同时只能集中维持一个法术；受伤体质豁免DC=max(10,floor(dmg/2))至高30）
  - `engine/spellcasting.py` 新建：cast_spell 完整施法流程（检查法术位→检查成分V/S/M→解决效果attack_roll/saving_throw/automatic/heal/shield→消耗法术位→设置集中）
- **回归验证**：15个模块全回归自检通过，无冲突。现有 engine/dice.py、engine/check.py、engine/damage.py 未被修改。
- **关联**：REFACTOR_PLAN.md §三 Phase B/D/G · RULE_SPEC.md "实现回填区" 已更新 · ARCHITECTURE.md §0

---

## 维护约定

1. **编号连续**：新条用下一个 `D-NNN`，不复用旧号。
2. **状态标注**：条目标题尾标 `✅已落地` / `🟡进行中` / `🔵待办` / `🔴待确认`；状态变化时就地改标注（不新增条），并在 `CHANGELOG` 记一笔"状态变更"。
3. **不删条**：决策被推翻时标 `⛔ 已废弃` 并写替代条编号，保留历史。
4. **与 CHANGELOG 边界**：DECISIONS 记"为什么/发现什么/待办"；CHANGELOG 记"实际改了什么"。一次改动可两边留痕。
