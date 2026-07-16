# AI DM 架构设计文档

> 基于 D&D 5E 不全书规则数据，搭建以 AI 为 DM 的跑团系统。
> 本文档为后续开发的实施依据。

## 0. 文档索引与当前进展（v3）

| 文档 | 内容 | 位置 |
|------|------|------|
| README.md | 文档索引+维护约定 | `aidm/docs/README.md` |
| PRD.md | 产品需求（做什么/功能/范围/验收） | `aidm/docs/PRD.md` |
| ARCHITECTURE.md | 架构（本档：怎么设计/硬性判定链/技术选型/目录） | `aidm/docs/ARCHITECTURE.md` |
| BUILD.md | 搭建指南+P0→P5 路线图 | `aidm/docs/BUILD.md` |
| RULE_SPEC.md | 规则规格书（400 条规则点+函数索引，经审计复核） | `aidm/docs/RULE_SPEC.md` |
| IMAGE_ASSETS.md | 图片资产盘点+生成方案 | `aidm/docs/IMAGE_ASSETS.md` |
| CHANGELOG.md | 变动日志（做了什么，倒序） | `aidm/docs/CHANGELOG.md` |
| DECISIONS.md | 发现与决策记录（ADR 式，D-NNN） | `aidm/docs/DECISIONS.md` |

**当前进展**：
- ✅ 规则书数据克隆（`5echm_web`，8644页+data.js 6238条）
- ✅ 规则规格书 `RULE_SPEC.md` v1.1（400 条，7 组并行审计复核，修正 11 处不准确+补遗 36 条）
- ✅ **P0 引擎核心全部完成**（dice/check/damage/conditions/combat/data.equipment，8 模块自检通过）
- ✅ **P1 状态层完成**（stats/models SQLModel 角色卡/战役/场景/战斗/日志 + stats/store SQLite 持久化+rolling summary+Combat往返）
- ✅ 全栈联调跑通（建角色→算AC→攻击命中→伤害→状态优劣势→存档→重载）
- ✅ **P2 知识层完成**（三语料 RAG：data.js 6238 + rules_text 141 + RULE_SPEC 400 → Qdrant 本地文件三集合；hybrid BM25+向量 RRF + 别名富化；15 条评测集；本地 bge-small-zh 嵌入）
- ✅ **P3 编排层完成**（`brain/graph.py` LangGraph 硬性判定链：classify→retrieve→verify→[retrieve_retry/confirm HITL]→resolve(纯代码骰子)→narrate→apply，覆盖 attack/cast/ability_check/start_combat，MemorySaver checkpointer，端到端跑通含天然20重击）
- ✅ **P4 API 层完成**（`api/main.py` FastAPI：/health /campaign /character /chat /chat/resume /summary；`cli.py` CLI 跑团）
- ✅ **叙事/世界层完成**（brain/world.py: DM 依据世界设定生成完整背景+当前场景(地点/时间/多感官氛围/在场NPC/可感知选项)，依据 DMG 叙事技巧；Campaign.setting + Scene.situation/atmosphere/exits 持久化；graph narrate 在场景中叙事+场景推进；API /open + /scene；前端场景面板（非单纯输入框）；e2e 实测 open→scene→chat→场景推进 全通）
- ✅ **P5 前端完成**（`ui/static/index.html` Web 聊天页+场景面板由 API `GET /` 托管 + `ui/app/page.tsx` Next.js+Tailwind scaffold；实测 GET / + /open + /scene + /chat 全通）
- 全阶段 P0–P5 + 叙事/世界层 完成。技术栈：deepseek-v4-flash（.env）+ 本地 bge-small（hf-mirror，recall@3=100%）+ Qdrant 本地文件（免docker）+ LangGraph + FastAPI + SQLModel。运行：`uvicorn aidm.api.main:app` 后浏览器开 `http://localhost:8000/`；CLI：`python -m aidm.cli`。

> 订正依据与发现的文档↔代码漂移见 `DECISIONS.md` D-001~D-012。

---

## 1. 项目概述

### 1.1 目标
让 AI 担任 DM（地下城主），玩家扮演角色进行 D&D 5E 跑团。AI 负责描述场景、演绎 NPC、裁决规则、推进战斗；玩家通过自然语言行动参与冒险。

### 1.2 数据基础
已克隆官方开源仓库 `DND5eChm/5echm_web` 至 `D:\game\dnd\5echm_web`：

| 数据 | 规模 | 用途 |
|------|------|------|
| `data.js` | 6238 条三元组（正文+标签+路径），26MB | **RAG 语料主源**，已纯文本化 |
| `topics/` | 8644 个 HTML 页面 | 原文兜底、可视化引用 |
| `webhelpcontents.htm` | 3.6MB 目录树 | 分类参考 |
| `icons/` `images/` | 资源 | 展示 |

`data.js` 三元组结构：`(正文纯文本, 标签[稀有度/类型/等级段], 来源路径)`。标签可用于检索时的粗过滤（如"只查法术""只查怪物"）。

### 1.3 核心理念
**叙事交给 LLM，规则判定交给代码。** LLM 只在"理解意图"和"讲故事"两头活动，中间的查规则→定检定→掷骰→算结果全走确定性代码。

---

## 2. 设计原则

1. **硬性判定**：所有掷骰、数值计算、状态变更由代码执行，LLM 不得"脑补"骰子结果或自创 DC。这是系统可信度的根基。
2. **LLM 边界明确**：LLM 只做①理解玩家自然语言意图②受规则约束地决定"是否检定/用哪个"③把判定结果叙事。不碰计算。
3. **RAG 校验而非参考**：检索到的规则原文用于**校验** LLM 提出的判定方案，而非仅"给 LLM 参考"。规则原文说了算，冲突时驳回重填。
4. **状态外部化**：角色卡、剧情、战斗状态存 SQLite，不依赖 LLM 上下文记忆。老剧情压缩成 rolling summary，防上下文爆炸。
5. **可存档可回溯**：每轮（玩家输入+AI回复+骰子+状态变更）全记日志，跑团存档即拷一个 SQLite 文件。

---

## 3. 总体架构

```
┌──────────────────────────────────────────────────────────────┐
│                    交互层 (CLI / Web)                          │
│        玩家输入 → AI DM 叙事回复 + 状态变更展示                  │
└────────────────┬──────────────────────────────┬───────────────┘
                 │                              │
    ┌────────────▼─────────────┐   ┌────────────▼──────────────┐
    │    AI DM 大脑 (LLM)      │   │   规则知识库 (RAG)         │
    │  • system prompt         │◄──►  • data.js 6238条纯文本   │
    │  • 意图分类/决策编排      │   │  • 语义检索 top-k          │
    │  • 叙事生成              │   │  • 返回正文+标签+出处路径   │
    │  • 结构化状态指令(JSON)   │   │  • 校验判定参数合规性      │
    └────────────┬─────────────┘   └───────────────────────────┘
                 │
    ┌────────────▼─────────────────────────────────┐
    │            引擎层 (确定性代码)                │
    │  • 骰子 RNG (secrets)   • 检定计算          │
    │  • 命中vsAC/豁免DC     • 伤害结算           │
    │  • 战斗回合/先攻状态机  • 状态效应计时       │
    │  • 法术位消耗恢复       • 判定模板执行        │
    └────────────┬─────────────────────────────────┘
                 │
    ┌────────────▼─────────────────────────────────┐
    │            状态层 (SQLite 持久化)             │
    │  • 角色卡 • 战役状态 • 当前场景               │
    │  • 战斗状态 • 剧情rolling summary • 日志     │
    └─────────────────────────────────────────────┘
```

---

## 4. 核心：硬性判定链

每条需要判定的玩家行动，走这条流水线。LLM 活动范围被夹在两端。

### 4.1 判定流水线

```
玩家: "我用力攻击摔绊那个哥布林"
   │
[LLM] 意图映射 ──────────────────────────────────────────┐
   │  → 动作模板「摔绊」+ 参数{目标=哥布林, 用力攻击=True, ……}   │
   │                                                         │ LLM 负责
[RAG] 查"摔绊"规则原文 ────────────────────────────────────┤
   │  → 校验: 摔绊=近战武器攻击 vs 目标力量(竞技)豁免          │
   │  → DC = 8 + 玩家熟练加值 + 玩家力量调整值                 │
   │  ← 若 LLM 填的参数与规则冲突, 驳回重填                    │
   │                                                         │ 代码负责
[代码] 掷骰 ───────────────────────────────────────────────┤
   │  攻击: d20 + 玩家命中加值(熟练+力量), 含优劣势             │ (硬性)
   │  哥布林豁免: d20 + 哥布林力量豁免加值                      │
   │  比较: 命中 ≥ 豁免 → 摔倒; 否则未中   (记日志)            │
   │                                                         │
[LLM] 叙事 ────────────────────────────────────────────────┤
   │  "你猛力一扫, 哥布林躲闪不及踉跄倒地……"                    │ LLM 负责
   │  + 结构化指令(JSON): {哥布林→加 prone 效应, 用力攻击→-2命中已计}
   │                                                         │
[代码] 执行指令 ───────────────────────────────────────────┘
   │  状态库更新: 哥布林加 prone, 战斗状态推进
```

### 4.2 LLM / 代码边界

| 步骤 | 负责 | 不可交给 LLM 的理由 |
|------|------|---------------------|
| 掷骰 d20 | 🔒 代码 | LLM 倾向"给好结果"或算错 |
| 优劣势、大失败/必出 | 🔒 代码 | 临界判定必须严格 |
| 命中 vs AC 比较 | 🔒 代码 | 比较运算无歧义 |
| 伤害骰+加值、扣 HP/临时HP | 🔒 代码 | 数值累加不能有偏差 |
| 豁免 DC 计算（8+熟练+属性） | 🔒 代码 | 公式固定 |
| 状态效应计时/每轮衰减 | 🔒 代码 | 状态机，LLM 记不住 |
| 专注(Concentration)维持检定 | 🔒 代码 | 触发条件复杂 |
| 法术位消耗与恢复 | 🔒 代码 | 计数器 |
| 熟练加值随等级查表 | 🔒 代码 | 固定映射 |
| 理解玩家自然语言 | ✅ LLM | 语义理解 |
| 决定"要不要检定/用哪个动作" | ✅ LLM（受规则约束） | 创造性裁决 |
| 把结果讲成故事 | ✅ LLM | 叙事 |

---

## 5. 模块设计

### 5.1 规则知识库（RAG）

**数据源：直接用 `data.js`，不解析 HTML 正文。**（data.js 已纯文本化、带标签和路径，省去剔除 8644 个 WinCHM 页面 `syn()` 脚本的脏活）

**三套语料，各建一 Qdrant 集合**（`knowledge/indexer.py`，本地文件模式 `QdrantClient(path=rules.db)`，免 docker）：

| 集合 | 语料 | 规模 | 角色 |
|------|------|------|------|
| `dnd_rules` | data.js | 6238 条 `{正文, 标签, 路径}` | 数据语料（怪物/物品/法术正文） |
| `dnd_rule_text` | `data/rules_text/` | 141 页 .txt | 判定规则文本 |
| `dnd_rule_spec` | `RULE_SPEC.md` | 400 条结构化 | **最高信号**校验语料（含精确公式/审计/函数索引） |

| 环节 | 方案 |
|------|------|
| 解析 | `parse_datajs.py`（JS 字符串分词器处理转义，比正则稳健）解析 data.js；`parse_rulespec.py` 按 `### R-XXX-NNN` 切分 RULE_SPEC |
| 切分 | 大条目整条一个 chunk；RULE_SPEC 每条规则点一个 chunk |
| 元数据 | payload `{body, tag, path, title}`；data.js 标签可过滤"只查法术/只查怪物" |
| 向量化 | 本地 `bge-small-zh-v1.5`（512维，`embedding.py`，走 HF 镜像，CPU 归一化）；可切 `bge-m3`（更强，需重建集合） |
| 存储 | **Qdrant 本地文件模式**（`data/rules.db`，零部署、存档即拷文件；非 sqlite-vec、非 docker 服务） |
| 检索 | **hybrid**：BM25(中文字符级) + 向量 RRF 融合（`hybrid.py`），补纯向量在中文关键词（"摔绊""豁免DC"）的偏移；+ 标签过滤 |
| 别名 | `aliases.py` 给机制类规则注入玩家同义词（"摔绊"→R-GLS-034），桥接"玩家词↔规则原词" |
| 评测 | `eval_retrieval.py` 15 条查询 recall@3/5，量化纯向量 vs hybrid |
| 兜底 | 检索结果可疑时，按路径回读 `topics/` 原 HTML 片段核对 |
| 角色 | **校验器**（`verifier.py`）：`gather_evidence`(hybrid) + `keyword_preflight`(粗筛) + `verify`；语义级校验留 P3 LLM 比对 |

**主要调用：**
- `retriever.query_rules(意图, 标签过滤)` / `query_formatted(...)` → 返回格式化规则块，供 LLM 决策
- `hybrid.search_spec_hybrid(查询)` → RULE_SPEC hybrid 检索（校验/编排主用）
- `verifier.verify(动作描述, proposed_check_type, proposed_dc)` → `Verification{ok, issues, evidence, digest}`

### 5.2 状态层（SQLite）

单文件持久化，跑团存档 = 拷文件。表结构见第 6 节。

加载策略：每轮只把**当前场景 + 相关角色卡 + 最近 N 轮原文 + 旧剧情 rolling summary**塞进 LLM 上下文，超出窗口的旧对话压缩成摘要存库。

### 5.3 引擎层（确定性代码）

#### 5.3.1 骰子引擎
```python
class Dice:
    def roll_d20(mod, advantage=None) -> (total, rolls, crit_state)
    def roll_dice(expr: str) -> (total, detail)   # "3d8+7" 等表达式
    def attack_roll(bonus, advantage, target_ac) -> (hit, rolls, crit)
    def save_dc(save_bonus, dc) -> (success, roll)
    def damage(dice_expr, mod, crit_multiplier) -> (total, detail)
```
- RNG 用 `secrets`（密码学随机，非伪随机）
- 优劣势：掷 2 个取高/低
- 大失败(1)/必出(20)显式标注
- 每次掷骰记日志（表达式、各骰、加值、总计、判定结果）

#### 5.3.2 判定模板库
预置常见动作的判定流程，LLM 把玩家意图映射到模板+参数，代码执行。无模板时走 RAG 解读（见 4.1）。

| 模板 | 检定方式 | DC/对抗 | 命中/效果 |
|------|----------|---------|-----------|
| 近战/远程攻击 | d20+命中加值 vs AC | 目标 AC | 命中→伤害骰 |
| 摔绊 Shove | d20+体育(力量) vs 目标力量豁免 | 8+熟练+力量 | 倒地 prone |
| 擒抱 Grapple | d20+体育 vs 目标力量/敏捷豁免(取高) | 8+熟练+力量 | 擒抱状态 |
| 推撞 Push | 同摔绊 | 8+熟练+力量 | 推离5尺 |
| 施法 攻击型 | d20+施法命中 vs AC | 目标 AC | 伤害/效果 |
| 施法 豁免型 | 目标 d20+豁免 vs 法术DC | 8+熟练+施法属性 | 全程/半程伤害 |
| 陷阱/陷阱豁免 | d20+属性豁免 vs DC | 规则原文定 DC | 触发效果 |
| 属性检定 | d20+属性调整值(+熟练?) vs DC | DM(规则)定 DC | 成功/失败 |
| 死亡豁免 | d20(无加值) vs 10 | DC10 | 记成败数 |
| 用力攻击 GWM/精确 | 攻击-?命中换+伤害 | 同攻击 | 已含调整 |

模板参数结构：`{template, target, options{advantage, gwf, ...}, dc_override?, roll_reason}`，`dc_override` 留空时由规则/公式自动填。

#### 5.3.3 战斗状态机
- 先攻：掷 d20+敏捷调整值排序，平手按敏捷或设定规则
- 回合：每轮每生物一动作+附赠动作+移动；效应按"回合结束衰减1"计时
- 集中：受伤害时按 `max(10, 伤害/2)` DC 的专注检定（代码触发）
- 死亡：HP≤0 进入稳定/死亡豁免；0HP 巨伤规则

### 5.4 AI DM 大脑（LLM 编排）✅ 已落地 `brain/graph.py`

每轮玩家输入后，LangGraph StateGraph 按 §4.1 流程编排。LLM 通过**结构化输出（JSON）**产出意图与状态变更指令，中间掷骰全代码。`MemorySaver` checkpointer 保留每轮状态（HITL 可中断恢复）。

节点流（`brain/graph.py`）：
```
classify(LLM 意图分类 → JSON intent: action_type/target/weapon/spell…)
  → retrieve(hybrid 检索规则)
  → verify(关键词预检)
     ├─ 校验驳回 → retrieve_retry(补关键词重检索) → resolve
     ├─ HITL 开 → confirm(interrupt 让 DM y/n) → resolve
     └─ 通过   → resolve
  → resolve(纯代码骰子, 按 action_type 分派: attack/cast/ability_check/start_combat)
  → narrate(LLM 叙事 + 结构化 state_changes JSON, 掷骰结果固定不可改)
  → apply(持久化 HP/法术位/日志/summary + 战斗轮次推进) → END
```

LLM 只在 classify/narrate/confirm 活动，resolve 全代码（硬性判定）。覆盖：attack（命中+重击骰翻倍 R-CMB-017/022/023/CMB-029）、cast（法术 DC=8+施法属性+熟练 / 法术攻击 / 豁免半伤 / 法术位消耗 R-DM-002/SPL-021/022/CHK-011/014）、ability_check（R-CHK-010）、start_combat（roll_initiative 持久化 R-CMB-002）。

System prompt 要点（内嵌于 classify/narrate 节点，无独立 prompts.py）：DM 身份定位、只引用检索到的规则不准凭记忆编规则、骰子结果以引擎输出为准、状态变更必须用指定 JSON schema。

### 5.5 交互层 ✅ CLI+API 已就绪
- **CLI**：`cli.py`（`python -m aidm.cli`），交互式跑团，调 `graph.run_turn`，HITL responder，骰子/HP 侧栏显示
- **API**：`api/main.py`（FastAPI：`/health /campaign /character /chat /chat/resume /summary`），前后端分离，HITL 经 `/chat/resume` 恢复
- **后续**：Next.js + shadcn/ui 前端（P5，可选增强；CLI+API 已构成完整可用系统）

---

## 6. 数据模型（SQLite 表，`stats/models.py` SQLModel 实现）

```sql
-- 6.1 规则语料：不入 SQL，入 Qdrant 三集合（见 §5.1）
--   dnd_rules(data.js 6238) / dnd_rule_text(141页) / dnd_rule_spec(RULE_SPEC 400)
--   payload: {body, tag, path, title}；向量 512维 Cosine
--   （原设计的 rule_chunk SQL 表 + sqlite-vec 未采用）

-- 6.2 角色卡（Character）
CREATE TABLE character (
  id INTEGER PRIMARY KEY,
  campaign_id INTEGER,        -- FK campaign.id
  name TEXT, race TEXT, char_class TEXT, subclass TEXT,   -- class→char_class 避 Python 关键字
  level INTEGER,
  abilities_json TEXT,        -- {str,dex,con,int,wis,cha: score}；mod/prof 按需算不存
  spell_slots_json TEXT,     -- {环阶: 剩余}
  known_spells_json TEXT,    -- 已知法术
  inventory_json TEXT,
  conditions_json TEXT,       -- 状态集合（R-GLS-043）
  hp_current, hp_max, temp_hp INTEGER,   -- hp_temp→temp_hp
  ac INTEGER, speed INTEGER, exhaustion INTEGER,   -- 力竭级（R-GLS-047）
  death_successes, death_failures INTEGER,  -- 死亡豁免计数（R-DMG-017）
  stable, dead BOOLEAN
  -- 注：skill_prof_json/save_prof_json/alignment/background/hit_dice_json/features_json 暂未持久化；
  --     熟练与否由 LLM classify 给出 proficient，不存角色卡（见 DECISIONS D-009）
  -- 注：proficiency_bonus 不存列，按 level 用 dice.proficiency_bonus() 算
);
-- JSON 桥接：abilities/conditions_list/spell_slots 属性 + to_condition_state/to_death_tracker

-- 6.3 战役与场景
CREATE TABLE campaign (
  id INTEGER PRIMARY KEY,
  name TEXT,
  rolling_summary TEXT,       -- 旧剧情压缩摘要
  world_flags_json TEXT
);
CREATE TABLE scene (
  id INTEGER PRIMARY KEY,
  campaign_id INTEGER,        -- FK
  location TEXT, npcs_json TEXT, environment TEXT,
  time TEXT, notes TEXT
);

-- 6.4 战斗状态（CombatState）
CREATE TABLE combat (
  id INTEGER PRIMARY KEY,
  campaign_id INTEGER,
  initiative_order_json TEXT,  -- [{cid, name, initiative, side}]
  participants_json TEXT,
  round INTEGER, current_index INTEGER,   -- current_turn→current_index
  active BOOLEAN
);

-- 6.5 日志（完整回溯）
CREATE TABLE log (
  id INTEGER PRIMARY KEY,
  campaign_id INTEGER,
  ts TEXT, player_input TEXT, dm_output TEXT,
  dice_rolls_json TEXT,          -- 所有掷骰明细
  state_changes_json TEXT,       -- 结构化状态变更指令
  rag_refs_json TEXT             -- 引用的规则条目id列表
);
```

---

## 7. 技术选型（v3 订正）

| 模块 | 选型 | star | 理由 |
|------|------|------|------|
| 语言 | Python 3.12.11（`langchain_312` env） | — | 环境就绪，langchain 生态成熟 |
| LLM 编排 | **LangGraph** | 37.2k | 图式状态机，硬性判定链即状态机；MemorySaver checkpointer + interrupt(HITL) |
| LLM 接入 | langchain-openai + openai SDK（OpenAI 兼容协议） | 1.3.5 / 31.3k | 实接 **deepseek-v4-flash @ senseaudio 网关**（`config.py`） |
| Embedding | 本地 `bge-small-zh-v1.5`（512维，sentence-transformers） | — | 中文表现、轻量；可切 bge-m3 |
| 向量库 | **Qdrant 本地文件模式**（`path=rules.db`，免 docker） | 33.2k | 检索强、零部署、存档即拷文件 |
| ORM | SQLModel | 18.2k | Pydantic+SQLAlchemy，与 FastAPI 同生态 |
| 状态库 | SQLite（SQLModel 驱动） | — | 单文件、可移植、存档即拷文件 |
| data.js 解析 | Python 字符串分词器（`parse_datajs.py`） | — | 处理 JS 转义，比正则稳健（非 node） |
| API | FastAPI | 76k | 异步、自动文档、Pydantic 原生 |
| 前端 | Next.js + shadcn/ui + Tailwind | 141k/119k/96k | 跑团定制面板（P5，可选增强） |

> 订正：向量库由原"docker 服务"改本地文件模式；嵌入由"API/bge-m3"改本地 bge-small-zh；LLM 实接 deepseek-v4-flash @ senseaudio。依据见 `DECISIONS.md` D-001/D-002/D-003。

---

## 8. 项目目录结构

```
D:\game\dnd\
├── 5echm_web/              # 规则书数据源（只读，已克隆）
│   ├── data.js            # RAG 语料主源（6238条）
│   ├── topics/            # 8644个HTML原文（兜底）
│   └── ...
├── .env                   # 密钥（key=/doc1/doc2），config.py 读取
├── aidm/                   # AI DM 项目
│   ├── docs/              # README/PRD/ARCHITECTURE/BUILD/RULE_SPEC/IMAGE_ASSETS/CHANGELOG/DECISIONS
│   ├── scripts/          # extract_rules.py / generate_images*.py
│   ├── data/
│   │   ├── rules_text/    # 141页纯文本（判定规则语料）
│   │   ├── rules.db/      # Qdrant 本地文件（三集合，建库产物）
│   │   ├── images/        # 112张 D&D 配图 + manifest
│   │   └── saves/         # 跑团存档（每个跑团一个 SQLite）
│   └── src/aidm/
│       ├── config.py      # pydantic-settings 读 .env（非 config.yaml）
│       ├── cli.py         # CLI 交互层入口（python -m aidm.cli）
│       ├── engine/        # P0 骰子/检定/伤害/状态/战斗状态机
│       ├── stats/         # P1 SQLModel 模型(models) + store(CRUD)
│       ├── knowledge/     # P2 RAG: parse_datajs/parse_rulespec/embedding/indexer/retriever/verifier/hybrid/aliases/eval_retrieval
│       ├── brain/         # P3 LangGraph: graph(编排)/llm(客户端)/state(GameState)
│       └── api/           # P4 FastAPI: main（/chat /character /campaign /summary …）
```

> 注：原 `state/` 实为 `stats/`；`ui/` 占位未建，交互层由 `cli.py` + `api/main.py` 承担；Next.js 前端待 P5。

---

## 9. 分阶段实施

| 阶段 | 产出 | 验收 | 依赖API | 状态 |
|------|------|------|---------|------|
| **P0 引擎** | 骰子/检定/伤害/状态/战斗状态机/装备数据 | 各模块自检通过；攻击命中→伤害→HP 流程跑通 | 否 | ✅ |
| **P1 状态层** | SQLModel 角色卡/战役/场景/战斗/日志 + store CRUD + rolling summary | 建角色→打3回合→存档→重载不丢 | 否 | ✅ |
| **P2 知识层** | 三语料→Qdrant 三集合 + hybrid 检索 + 别名富化 + 校验器 | 问"擒抱怎么判"查得准；校验器能驳回 | 本地(embedding) | ✅ |
| **P3 编排层** | LangGraph StateGraph 判定链 + HITL + MemorySaver | 玩家输入→判定链→叙事+状态更新端到端 | 是(LLM) | ✅ |
| **P4 API层** | FastAPI 端点 + CLI 交互层 | HTTP 客户端能跑一轮对话+查状态 | 是 | ✅ |
| **P5 前端** | Next.js + shadcn/ui 面板 | 浏览器开跑，骰子/状态实时显示 | 是 | ⏳ 可选 |

> 进度与 BUILD §5 一致。P0/P1 不需外部服务；P2 用本地 embedding（免 docker）；P3 起需 LLM API。详细步骤见 `BUILD.md`。

---

## 10. API 接入（已落地 `config.py` + `.env`）

LLM 接入选 OpenAI 兼容格式，经 senseaudio 网关接 deepseek-v4-flash。配置读 `D:\game\dnd\.env` 的 `key=` 字段。

- [x] **API base_url**：`https://api.senseaudio.cn/v1`
- [x] **模型名**：`deepseek-v4-flash`
- [x] **embedding**：本地 `bge-small-zh-v1.5`（不走 API，免积分）
- [x] **API key**：填入 `D:\game\dnd\.env`（`key=...`），不入仓

> 全部已确认（原 §10"待确认事项"已解决，依据见 DECISIONS D-003）。P0/P1 完全离线先行；P2 用本地 embedding；P3 起用 LLM API。

---

## 11. 风险与对策

| 风险 | 对策 |
|------|------|
| LLM 凭记忆编规则 | RAG 校验驳回 + system prompt 严禁凭记忆 |
| 边缘规则无模板 | 走 RAG 查原文，LLM 解读规则但数值仍代码执行 |
| data.js 条目正文有缺失 | 按路径回读 `topics/` 原 HTML 兜底 |
| 上下文窗口溢出 | rolling summary + 只加载当前场景/相关角色 |
| LLM 不按 schema 输出状态指令 | 结构化输出+重试+JSON schema 校验 |
| 战斗状态复杂易错 | 状态机用代码管，LLM 只发指令不记账 |
| 标签字段语义杂(稀有度/类型混) | 检索时按需归一化过滤，不强求统一分类 |

---

*文档版本：v3.0 · 订正于 2026-07-14（对齐 P0-P4 已落地代码，依据见 DECISIONS D-001~D-012）· 基于规则书数据 `5echm_web`（data.js 6238条 / topics 8644页）*
