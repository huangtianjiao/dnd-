# AI DM 架构设计文档

> 基于 D&D 5E 不全书规则数据，搭建以 AI 为 DM 的跑团系统。
> 本文档为后续开发的实施依据。

## 0. 文档索引与当前进展（v4）

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
- ✅ 全栈联调跑通（建角色→算AC→攻击命中→伤害→存档→重载）
- ✅ **P2 知识层完成**（三语料 RAG：data.js 6238 + rules_text 141 + RULE_SPEC 400 → Qdrant 本地文件三集合；hybrid BM25+向量 RRF + 别名富化；15 条评测集；本地 bge-small-zh 嵌入）
- ✅ **P3 编排层完成**（`brain/graph.py` LangGraph 硬性判定链：classify→retrieve→verify→[retrieve_retry/confirm HITL]→resolve(纯代码骰子)→narrate→apply，覆盖 attack/cast/ability_check/start_combat/rest/social/levelup/travel，MemorySaver checkpointer，端到端跑通含天然20重击）
- ✅ **P4 API 层完成**（`api/main.py` FastAPI：39 个路由端点，覆盖战役/角色/聊天/HITL/专长/魔法物品/据点/房间等；`cli.py` CLI 跑团）
- ✅ **叙事/世界层完成**（brain/world.py: DM 依据世界设定生成完整背景+当前场景(地点/时间/多感官氛围/在场NPC/可感知选项)，依据 DMG 叙事技巧；Campaign.setting + Scene.situation/atmosphere/exits 持久化；graph narrate 在场景中叙事+场景推进；API /open + /scene；前端场景面板（非单纯输入框）；e2e 实测 open→scene→chat→场景推进 全通）
- ✅ **P5 前端完成**（双前端架构：`ui/static/` 原生 HTML 单页应用 + `ui/app/` Next.js 14 + Tailwind + @3d-dice/dice-box 3D 骰子动画；Socket.IO 实时多人通信；三栏 VTT 布局）
- ✅ **WebSocket 实时同桌层完成**（`api/ws.py` python-socketio AsyncServer，Colyseus 风格 Room 生命周期管理，多人在线跑团，一人掷骰全员看到）
- ✅ **测试体系建立**（`tests/` 下 7 个测试文件，138 个测试全通过，覆盖骰子引擎/检定系统/伤害结算/状态条件/战斗流程/API端点/端到端集成）
- 全阶段 P0–P5 + 叙事/世界层 + WebSocket 实时同桌 + 测试体系 完成。技术栈：deepseek-v4-flash（.env）+ 本地 bge-small（hf-mirror，recall@3=100%）+ Qdrant 本地文件（免docker）+ LangGraph + FastAPI + SQLModel + Socket.IO + Next.js。运行：`uvicorn aidm.api.main:app` 后浏览器开 `http://localhost:8080/`；CLI：`python -m aidm.cli`。

> 订正依据与发现的文档↔代码漂移见 `DECISIONS.md` D-001~D-026。
> **v4 变动标注**（2026-07-15 架构梳理）：§0 补全模块清单（brain 19 子模块/data 9 子模块/engine 新增 4 模块）、API 端点数（6→39）、WebSocket 同桌层、测试体系（138 测试）、前端双架构（静态 HTML + Next.js 14）。§3 架构图加入 WebSocket 层和前端双架构。§5 模块设计补全 brain/data/engine 子模块清单和完整 API 端点列表。§8 目录结构反映实际代码组织。

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

> **v4 变动标注**：原架构图为"交互层→AI DM 大脑→引擎层→状态层"四层。实际代码已演化为六层架构：
> ①前端交互层（双前端：静态 HTML + Next.js 14）、②API 接口层（FastAPI REST + Socket.IO WebSocket 实时同桌）、
> ③AI DM 大脑（LangGraph 图编排）、④规则知识库（RAG hybrid 检索）、⑤引擎层（确定性代码）、⑥状态层（SQLite）。

```
┌──────────────────────────────────────────────────────────────────────┐
│                     前端交互层（双前端架构）                             │
│  ┌─────────────────────┐  ┌──────────────────────────────────────┐  │
│  │ ui/static/ (HTML)   │  │ ui/app/ (Next.js 14 + Tailwind)      │  │
│  │ 原生 JS 单页应用    │  │ React 18 + @3d-dice/dice-box 3D骰子  │  │
│  │ Socket.IO 客户端    │  │ Socket.IO 客户端                     │  │
│  │ 三栏 VTT 布局       │  │ 主菜单/三栏布局/Toast通知            │  │
│  └──────────┬──────────┘  └──────────────────┬───────────────────┘  │
│             │  HTTP REST (fetch)              │  WebSocket (Socket.IO) │
└─────────────┼─────────────────────────────────┼──────────────────────┘
              │                                 │
┌─────────────▼─────────────────────────────────▼──────────────────────┐
│                        API 接口层 (FastAPI)                            │
│  • REST 端点: /campaign /character /chat /open /scene /feats ...      │
│  • WebSocket 端点: /ws/{campaign_id} (python-socketio AsyncServer)    │
│  • Socket.IO 事件: join/leave/result/processing/scene_update/...      │
│  • Colyseus 风格 Room 生命周期管理（空房 30 秒后自动销毁）              │
└─────────────┬─────────────────────────────────┬──────────────────────┘
              │                                 │
    ┌─────────▼──────────┐   ┌──────────────────▼──────────────────────┐
    │  AI DM 大脑 (LLM)  │   │        规则知识库 (RAG)                   │
    │  • LangGraph 图编排 │   │  • data.js 6238条纯文本                  │
    │  • 意图分类(LLM)    │   │  • 语义检索 top-k                       │
    │  • 叙事生成(LLM)    │◄──►  • hybrid BM25+向量 RRF 融合            │
    │  • 结构化状态指令   │   │  • 返回正文+标签+出处路径                │
    │    (JSON)           │   │  • 校验判定参数合规性                    │
    └─────────┬──────────┘   └──────────────────────────────────────────┘
              │
    ┌─────────▼──────────────────────────────────────────────────────────┐
    │                    引擎层 (确定性代码)                               │
    │  • 骰子 RNG (secrets)   • 检定计算 (attack_roll/saving_throw)     │
    │  • 命中vsAC/豁免DC     • 伤害结算 (roll_damage/apply_damage)     │
    │  • 战斗回合/先攻状态机  • 状态效应计时 (conditions/concentration)  │
    │  • 动作经济 (actions)   • 施法机制 (spellcasting)                 │
    │  • 借机攻击 (opportunity_attack)                                    │
    └─────────┬──────────────────────────────────────────────────────────┘
              │
    ┌─────────▼──────────────────────────────────────────────────────────┐
    │                    状态层 (SQLite 持久化)                           │
    │  • 角色卡 • 战役状态 • 当前场景                                     │
    │  • 战斗状态 • 剧情 rolling summary • 日志                          │
    └────────────────────────────────────────────────────────────────────┘
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
  → resolve(纯代码骰子, 按 action_type 分派: attack/cast/ability_check/start_combat/rest/social/levelup/travel)
  → narrate(LLM 叙事 + 结构化 state_changes JSON, 掷骰结果固定不可改)
  → apply(持久化 HP/法术位/日志/summary + 战斗轮次推进) → END
```

LLM 只在 classify/narrate/confirm 活动，resolve 全代码（硬性判定）。覆盖：attack（命中+重击骰翻倍 R-CMB-017/022/023/CMB-029）、cast（法术 DC=8+施法属性+熟练 / 法术攻击 / 豁免半伤 / 法术位消耗 R-DMG-002/SPL-021/022/CHK-011/014）、ability_check（R-CHK-010）、start_combat（roll_initiative 持久化 R-CMB-002）、rest（短休消耗生命骰/长休恢复全部 R-GLS-014/015）、social（NPC态度系统/四步社交互动 R-CON-012/R-DM-047）、levelup（XP表/升级五步骤/游戏四阶段 R-DM-041~045）、travel（旅行步调/导航检定/被动察觉/随机遭遇 R-DM-026~040）。

System prompt 要点（内嵌于 classify/narrate 节点，无独立 prompts.py）：DM 身份定位、只引用检索到的规则不准凭记忆编规则、骰子结果以引擎输出为准、状态变更必须用指定 JSON schema。

> **v4 变动标注**：§5.4 节点流中 resolve 的 action_type 分派已从"attack/cast/ability_check/start_combat"扩展到 8 种（新增 rest/social/levelup/travel）。对应 brain/ 下新增的业务模块见 §5.6。

### 5.5 交互层 ✅ CLI+API+前端 已就绪

- **CLI**：`cli.py`（`python -m aidm.cli`），交互式跑团，调 `graph.run_turn`，HITL responder，骰子/HP 侧栏显示
- **API**：`api/main.py`（FastAPI），前后端分离，HITL 经 `/chat/resume` 恢复
- **WebSocket**：`api/ws.py`（python-socketio AsyncServer），多人在线跑团实时通信
- **前端**：双前端架构——`ui/static/`（原生 HTML 单页应用）+ `ui/app/`（Next.js 14 + Tailwind + @3d-dice/dice-box 3D 骰子动画）

> **v4 变动标注**：§5.5 从"CLI+API 已就绪，Next.js 待 P5"更新为"CLI+API+前端 已就绪"。新增 WebSocket 实时同桌层和前端双架构描述。详见 §5.7 和 §5.8。

### 5.6 brain/ 业务模块清单

> **v4 新增**：brain/ 包含 19 个子模块，远超原文档描述的"graph/llm/state 三件套"。

| 文件 | 说明 |
|------|------|
| `brain/graph.py` | **LangGraph 编排核心**（607 行）。`build_graph()` 构建 StateGraph(GameState)，定义 8 个节点（classify/retrieve/verify/retrieve_retry/confirm/resolve/narrate/apply）和条件边。`MemorySaver` checkpointer 保留每轮状态。提供 `run()` 和 `run_turn()` 接口 |
| `brain/state.py` | **GameState（TypedDict）**。贯穿 LangGraph 图节点的状态对象，定义所有流转字段 |
| `brain/llm.py` | LLM 客户端。`get_llm()` 返回 ChatOpenAI 实例，`chat()` 便捷问答。被 graph.py 的 classify/narrate 节点调用 |
| `brain/world.py` | 叙事/世界层。DM 依据世界设定生成完整背景+当前场景(地点/时间/多感官氛围/在场NPC/可感知选项)，依据 DMG 叙事技巧。Campaign.setting + Scene.situation/atmosphere/exits 持久化 |
| `brain/adventure_builder.py` | 冒险构建器。DM 依据世界设定生成完整背景+当前场景 |
| `brain/campaign_manager.py` | 战役管理器。创建/加载/列出战役 |
| `brain/char_create.py` | 角色创建逻辑。五步车卡流程 + 衍生数值计算（标准阵列/购点法27点/4d6弃最低） |
| `brain/exploration.py` | 探索流程。旅行步调(快速30里/中速24里/慢速18里)/导航检定/被动察觉/随机遭遇/资源追踪 (R-DM-026~040) |
| `brain/levelup.py` | 升级与成长。XP表(20级)/升级五步骤/游戏四阶段(T1-T4)/专长选择 (R-DM-041~045) |
| `brain/loot.py` | 战利品生成与分配。`generate_loot`(cr,count,include_magic_items,seed)、`distribute_loot`(pool,players,method,needs,dm_assignments,seed)、`attune_magic_item`/`break_attunement` |
| `brain/loot_distribution.py` | 战利品分配策略。NEED_FIRST/ROUND_ROBIN/ROLL_OFF/DM_ASSIGN 四种模式，金币平均分配 |
| `brain/plane_travel.py` | 位面旅行机制。58个位面数据 + 位面旅行规则 |
| `brain/rest.py` | 休息机制。短休消耗生命骰恢复HP+恢复职业特性；长休恢复全部HP+所有法术位+力竭-1 (R-GLS-014/R-GLS-015) |
| `brain/room.py` | 多人房间管理。`RoomManager` 类，Colyseus 风格 Room 生命周期管理，房主权限转让/踢人 |
| `brain/session0.py` | Session 0（跑团前准备）逻辑。确定桌规/角色创建/战役设定 |
| `brain/social.py` | 社交流程。NPC态度系统(友好/冷漠/敌对)/四步社交互动/态度转换阈值 (R-CON-012/R-DM-047) |
| `brain/stronghold.py` | 据点系统。DMG 第八章据点建立/设施建设/据点回合指令 |
| `brain/memory.py` | **三层记忆系统**。工作记忆（最近 N 轮对话原文）+ 中期记忆（rolling summary 压缩）+ 长期记忆（关键事实入 Qdrant 向量库按语义检索注入）。解决跨 Session 崩塌，跨 Session 持久化 |
| `brain/image_gen.py` | 交互式产物生成。依据场景描述生成配图（场景插图/NPC 肖像/关键场景配图），落地"交互式产物生成"需求 |

### 5.7 data/ 游戏数据模块清单

> **v4 新增**：data/ 包含 9 个数据表模块，提供 D&D 5E 核心规则数据（feats/planes/strongholds/magic_items/spells/equipment/classes/races/backgrounds）。

| 文件 | 说明 |
|------|------|
| `data/backgrounds.py` | 背景数据表（PHB 第四章背景，16 种） |
| `data/classes.py` | 职业数据表（PHB 第三章职业，12 个核心职业：生命骰/主属性/豁免熟练/技能选择/护甲武器熟练/子职） |
| `data/equipment.py` | 装备数据表。`weapon_damage_dice(weapon_name)` 返回武器伤害骰表达式，`weapon_damage_type(weapon_name)` 返回伤害类型。KeyError 时默认 "1d8"/"挥砍" |
| `data/feats.py` | 专长数据表（PHB 2024 第五章专长）。`list_feats(category)`、`get_feat(feat_name)`、`feat_categories()`。支持起源/通用/战斗风格/传奇恩惠分类，非复选专长不可重复选择 |
| `data/magic_items.py` | 魔法物品数据库。`list_magic_items(rarity, item_type, cursed_only)`、`get_magic_item(name)`。支持稀有度(COMMON/UNCOMMON/RARE/VERY_RARE/LEGENDARY/ARTIFACT)和类别(WEAPON/ARMOR/WONDROUS_ITEM/RING/SCROLL/POTION/STAFF/ROD/WAND)筛选 |
| `data/planes.py` | 位面数据表。58 个位面数据（DMG 第六章宇宙学） |
| `data/races.py` | 种族数据表（PHB 第二章种族，10 种：属性加成/速度/黑暗视觉/特质/子族） |
| `data/spells.py` | 法术数据表。12 个法术数据表（火焰箭/魔法飞弹/火球术/闪电束/治愈真言/护盾术等）+ 法术位进度表(1-20级) + 施法属性映射 |
| `data/strongholds.py` | 据点设施数据表（DMG 第八章）。`StrongholdType`/`OrderType` 枚举，`FACILITIES` 字典，`FacilitySpace` 枚举 |

### 5.8 engine/ 引擎模块清单

> **v4 新增**：engine/ 包含 11 个模块，覆盖 D&D 5E 核心机制。

| 文件 | 说明 |
|------|------|
| `engine/dice.py` | 骰子引擎核心。`roll_die`/`roll_d20`/`attack_roll`/`save_dc`/`damage`，优劣势掷 2 取高/低，大失败(1)/必出(20)标注，RNG 用 `secrets`（密码学随机） |
| `engine/check.py` | 检定计算。`attack_roll`/`saving_throw`/`ability_check`/`calc_save_dc`(8+属性+熟练) |
| `engine/damage.py` | 伤害结算。`roll_damage`/`apply_damage_to_hp`/`apply_healing`，重击骰翻倍(R-CMB-029)，抗性/易伤减免 |
| `engine/conditions.py` | 状态效应（prone/restrained/poisoned 等 14 种），每轮衰减计时，专注(Concentration)维持检定触发 |
| `engine/combat.py` | 战斗状态机。`Combatant`/`Combat` 类，`roll_initiative`/`current_combatant`/`advance_turn`，先攻排序，回合推进 |
| `engine/actions.py` | 动作系统（动作/附赠动作/反应/移动），动作经济，11种战斗动作分派器（attack/dash/disengage/dodge/help/hide/magic/ready/search/study/utilize） |
| `engine/concentration.py` | 专注检定。受伤害时按 `max(10, 伤害/2)` DC 的专注检定（代码触发），同时只能集中维持一个法术 |
| `engine/core_loop.py` | 核心循环逻辑 |
| `engine/opportunity_attack.py` | 借机攻击机制。触发条件判定 + 近战攻击检定 |
| `engine/spellcasting.py` | 施法机制。`cast_spell` 完整施法流程（检查法术位→检查成分V/S/M→解决效果attack_roll/saving_throw/automatic/heal/shield→消耗法术位→设置集中） |
| `engine/__init__.py` | 包初始化 |

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

## 7. 技术选型（v4 订正）

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
| WebSocket | **python-socketio**（AsyncServer，ASGI 模式） | 14k | 多人在线跑团实时通信；Colyseus 风格 Room 生命周期 |
| 前端（静态） | 原生 HTML + JS + CSS（FastAPI `/static` 托管） | — | 零构建、快速迭代；Socket.IO CDN 客户端 |
| 前端（Next.js） | **Next.js 14** + React 18 + Tailwind CSS 3.4 | 141k/119k/96k | 跑团定制面板（P5）；@3d-dice/dice-box 3D 物理骰子动画 |
| 测试 | pytest + httpx（AsyncClient） | — | 7 个测试文件，138 个测试覆盖引擎/API/端到端 |

> **v4 变动标注**：技术选型表新增 WebSocket（python-socketio）、前端双架构（静态 HTML + Next.js 14）、测试体系（pytest 138 测试）。原 v3 表中"前端: Next.js + shadcn/ui + Tailwind (P5 可选)"已更新为实际落地的双前端架构。

---

## 8. 项目目录结构

> **v4 变动标注**：原目录结构仅列 5 大包概要。实际代码中 brain/ 有 19 个子模块、data/ 有 9 个数据表模块、engine/ 有 11 个模块、api/ 新增 ws.py WebSocket 层、tests/ 下有 7 个测试文件。以下为完整目录结构。

```
D:\game\dnd\
├── 5echm_web/              # 规则书数据源（只读，已克隆）
│   ├── data.js            # RAG 语料主源（6238条三元组）
│   ├── topics/            # 8644个HTML原文（兜底引用）
│   └── ...
├── .env                   # 密钥（key=/doc1/doc2），config.py 读取
├── aidm/                   # AI DM 项目主体
│   ├── docs/              # 文档目录（10 个文档）
│   ├── scripts/           # 工具脚本（extract_rules/generate_images*/test_*）
│   ├── tests/             # 测试套件（7 个文件，138 个测试）
│   │   ├── test_dice_engine.py      # 骰子引擎测试（23 通过）
│   │   ├── test_check_system.py     # 检定系统测试（20 通过）
│   │   ├── test_damage_system.py    # 伤害结算测试（29 通过）
│   │   ├── test_conditions.py       # 状态条件测试（27 通过）
│   │   ├── test_combat_flow.py      # 战斗流程测试（24 通过）
│   │   ├── test_api_endpoints.py    # API端点测试（8 通过）
│   │   └── test_e2e_flow.py         # 端到端集成测试（7 通过）
│   ├── data/
│   │   ├── rules_text/    # 141页纯文本（判定规则语料）
│   │   ├── rules.db/      # Qdrant 本地文件（三集合，建库产物）
│   │   ├── images/        # ~680张 D&D 配图 + manifest
│   │   └── saves/         # 跑团存档（save.db SQLite）
│   ├── ui/                # 前端目录（双前端架构）
│   │   ├── static/        # 静态 HTML 单页应用（index.html/app.js/style.css）
│   │   ├── app/           # Next.js 14 前端（page.tsx/layout.tsx/globals.css）
│   │   ├── package.json   # 前端依赖配置
│   │   └── ...            # next.config.js/tailwind.config.ts/tsconfig.json
│   └── src/aidm/          # Python 后端源码
│       ├── config.py      # pydantic-settings 读 .env（非 config.yaml）
│       ├── cli.py         # CLI 交互层入口（python -m aidm.cli）
│       ├── engine/        # 引擎层（11 模块：dice/check/damage/conditions/combat/actions/concentration/core_loop/opportunity_attack/spellcasting）
│       ├── stats/         # 状态持久化层（models: SQLModel 表定义 + store: SQLite CRUD）
│       ├── knowledge/     # RAG 知识检索层（9 模块：parse_datajs/parse_rulespec/embedding/indexer/retriever/verifier/hybrid/aliases/eval_retrieval）
│       ├── brain/         # LangGraph 编排层（19 模块：graph/state/llm/memory/world/image_gen/adventure_builder/campaign_manager/char_create/exploration/levelup/loot/loot_distribution/plane_travel/rest/room/session0/social/stronghold）
│       ├── data/          # 游戏数据模块（9 模块：backgrounds/classes/equipment/feats/magic_items/planes/races/spells/strongholds）
│       └── api/           # FastAPI 接口层（main: 39 REST 端点 + ws: Socket.IO WebSocket 实时同桌）
```

---

## 9. 分阶段实施

| 阶段 | 产出 | 验收 | 依赖API | 状态 |
|------|------|------|---------|------|
| **P0 引擎** | 骰子/检定/伤害/状态/战斗状态机/装备数据 | 各模块自检通过；攻击命中→伤害→HP 流程跑通 | 否 | ✅ |
| **P1 状态层** | SQLModel 角色卡/战役/场景/战斗/日志 + store CRUD + rolling summary | 建角色→打3回合→存档→重载不丢 | 否 | ✅ |
| **P2 知识层** | 三语料→Qdrant 三集合 + hybrid 检索 + 别名富化 + 校验器 | 问"擒抱怎么判"查得准；校验器能驳回 | 本地(embedding) | ✅ |
| **P3 编排层** | LangGraph StateGraph 判定链 + HITL + MemorySaver | 玩家输入→判定链→叙事+状态更新端到端 | 是(LLM) | ✅ |
| **P4 API层** | FastAPI 端点(39个) + CLI 交互层 | HTTP 客户端能跑一轮对话+查状态 | 是 | ✅ |
| **P5 前端** | 双前端：静态 HTML 单页 + Next.js 14 + Tailwind + 3D 骰子动画 | 浏览器开跑，骰子/状态实时显示 | 是 | ✅ |
| **WebSocket 同桌** | python-socketio AsyncServer + Colyseus 风格 Room 管理 | 多人在线跑团，一人掷骰全员看到 | 是 | ✅ |
| **测试体系** | pytest 7 文件 138 测试（引擎/检定/伤害/状态/战斗/API/e2e） | 全部通过 | 否 | ✅ |

> **v4 变动标注**：分阶段实施表从"P0-P5 六阶段"扩展为"P0-P5 + WebSocket 同桌 + 测试体系 八项"。P5 前端状态从"⏳ 可选"更新为"✅ 完成"。新增 WebSocket 同桌层和测试体系两行。

---

## 10. API 接入（已落地 `config.py` + `.env`）

LLM 接入选 OpenAI 兼容格式，经 senseaudio 网关接 deepseek-v4-flash。配置读 `D:\game\dnd\.env` 的 `key=` 字段。

- [x] **API base_url**：`https://api.senseaudio.cn/v1`
- [x] **模型名**：`deepseek-v4-flash`
- [x] **embedding**：本地 `bge-small-zh-v1.5`（不走 API，免积分）
- [x] **API key**：填入 `D:\game\dnd\.env`（`key=...`），不入仓

> 全部已确认（原 §10"待确认事项"已解决，依据见 DECISIONS D-003）。P0/P1 完全离线先行；P2 用本地 embedding；P3 起用 LLM API。

### 10.1 REST API 端点清单（39 个）

> **v4 新增**：原文档仅列 6 个核心端点。实际 `api/main.py` 已实现 39 个路由端点，覆盖战役管理、角色创建、聊天跑团、HITL 恢复、专长系统、魔法物品、据点系统、房间管理等全部功能域。

| 功能域 | 端点 | 说明 |
|--------|------|------|
| 健康检查 | `GET /health` | 返回 `{"status":"ok"}` |
| 战役管理 | `POST /campaign` | 创建战役 |
| | `GET /campaigns` | 列出所有战役 |
| | `GET /campaign/{id}/state` | 加载战役完整状态 |
| 角色管理 | `POST /character` | 创建角色 |
| | `GET /character/{id}` | 获取完整角色卡 |
| | `GET /character/{id}/inventory` | 获取角色物品栏 |
| 聊天跑团 | `POST /chat` | 跑一轮硬性判定链 |
| | `POST /chat/resume` | HITL 中断恢复 |
| 场景管理 | `POST /open` | DM 生成开场 |
| | `GET /scene/{campaign_id}` | 获取当前场景 |
| 世界设定 | `POST /generate_setting` | AI 生成世界设定 |
| 战斗状态 | `GET /combat/{campaign_id}` | 获取战斗状态 |
| 怪物检索 | `GET /monster/{name}` | 检索怪物属性块 |
| 魔法物品 | `GET /magic-items` | 列出魔法物品 |
| 加入战役 | `POST /join` | 加入已有战役 |
| 在线玩家 | `GET /players/{campaign_id}` | 获取在线玩家列表 |
| 专长系统 | `GET /feats` | 列出所有专长 |
| | `GET /character/{cid}/available-feats` | 获取角色可选专长 |
| | `POST /character/{cid}/feat` | 为角色添加专长 |
| | `POST /character/{cid}/select-feat` | 角色选择专长 |
| 同调系统 | `POST /character/{cid}/attune` | 角色同调魔法物品 |
| | `POST /character/{cid}/break-attunement` | 角色解除同调 |
| 战利品 | `POST /loot/generate` | 生成战利品 |
| | `POST /loot/distribute` | 分配战利品 |
| 房间管理 | `POST /room/create` | 创建房间 |
| | `POST /room/join` | 加入房间 |
| | `GET /room/{room_id}` | 获取房间信息 |
| | `GET /rooms` | 列出所有房间 |
| | `POST /room/{room_id}/kick` | 踢出房间成员 |
| | `POST /room/{room_id}/transfer` | 转让房主权限 |
| 据点系统 | `POST /stronghold/create` | 创建据点 |
| | `GET /stronghold/{campaign_id}` | 获取据点信息 |
| | `POST /stronghold/build` | 建设据点设施 |
| | `POST /stronghold/turn` | 据点回合指令 |
| | `GET /strongholds/facilities` | 获取据点设施列表 |

### 10.2 WebSocket 事件清单

> **v4 新增**：`api/ws.py` 实现 python-socketio AsyncServer，ASGI 模式集成到 FastAPI。Colyseus 风格 Room 生命周期管理（空房 30 秒后自动销毁）。

| 事件方向 | 事件名 | 说明 |
|----------|--------|------|
| 客户端→服务端 | `connect` | 建立 WebSocket 连接 |
| | `disconnect` | 断开连接 |
| | `action` | 发送玩家行动 |
| 服务端→客户端 | `join` | 玩家加入通知 |
| | `leave` | 玩家离开通知 |
| | `result` | 行动结果广播 |
| | `processing` | 处理中状态广播 |
| | `player_acting` | 当前行动玩家广播 |
| | `scene_update` | 场景更新广播 |
| | `combat_update` | 战斗状态更新广播 |
| | `turn_advanced` | 回合推进广播 |
| | `round_end` | 回合结束广播 |
| | `monster_turn` | 怪物回合广播 |
| | `monster_action` | 怪物行动广播 |
| | `combat_end` | 战斗结束广播 |
| | `player_ready` | 玩家准备状态广播 |
| | `character_update` | 角色信息更新广播 |
| | `error` | 错误消息广播 |

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

*文档版本：v4.0 · 架构梳理于 2026-07-15（补全 brain 19 子模块/data 9 子模块/engine 11 模块/API 39 端点/WS 同桌层/测试体系/前端双架构，依据见 DECISIONS D-001~D-026）· 基于规则书数据 `5echm_web`（data.js 6238条 / topics 8644页）*

> **变动标注约定**：本文档采用 `> **vN 变动标注**` 引用块标注每个版本的变动点。当架构发生变动时，在对应章节添加变动标注，并更新文档版本号。详细的变动动作记录在 `CHANGELOG.md`，背后的决策与发现记录在 `DECISIONS.md`。
