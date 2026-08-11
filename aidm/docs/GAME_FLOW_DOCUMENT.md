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

# 三、角色创建流程

角色创建实现在 `brain/char_create.py`（635行），严格对照 PHB 2024 第一章五步车卡法。
核心数据结构 `CharacterSheet` 保存五步全部中间数据，最终写入 `stats/models.py` 的 `Character` SQLModel。

### 3.1 五步车卡法（对照 PHB 2024）

| 步骤 | 函数签名 | 说明 | 实现位置 |
|------|----------|------|----------|
| Step 1 | `step1_choose_class(class_name, sheet)` | 12核心职业 → 生命骰/主属性/豁免熟练/护甲武器熟练/施法属性 | `char_create.py` |
| Step 2 | `step2_choose_origin(race, background, sheet)` | 10种种族 + 16种背景 → 速度/体型/黑暗视觉/特质/起源专长/语言 | `char_create.py` |
| Step 3 | `step3_assign_ability_scores(method, scores, sheet)` | 三种方式：标准阵列 / 购点法 / 4d6弃最低 | `char_create.py` |
| Step 4 | `step4_choose_alignment(alignment, sheet)` | 九宫格阵营 | `char_create.py` |
| Step 5 | `step5_enrich_details(name, appearance, sheet)` | 名字/外貌/性格 + 衍生数值自动计算 | `char_create.py` |

#### Step 1：选择职业 — 12职业完整数据

每个职业在 `data/classes.py` 中定义完整属性：

| 职业 | 生命骰 | 主属性 | 豁免熟练 | 1级HP(含+3CON) | 固定HP增长 |
|------|--------|--------|----------|----------------|------------|
| 野蛮人 | d12 | 力量 | 力量/体质 | 15 | 7 |
| 战士 | d10 | 力量/敏捷 | 力量/体质 | 13 | 6 |
| 圣武士 | d10 | 力量/魅力 | 体质/魅力 | 13 | 6 |
| 游侠 | d10 | 敏捷/感知 | 力量/敏捷 | 13 | 6 |
| 吟游诗人 | d8 | 魅力 | 敏捷/魅力 | 11 | 5 |
| 牧师 | d8 | 感知 | 体质/感知 | 11 | 5 |
| 德鲁伊 | d8 | 感知 | 智力/感知 | 11 | 5 |
| 武僧 | d8 | 敏捷/感知 | 力量/敏捷 | 11 | 5 |
| 游荡者 | d8 | 敏捷 | 敏捷/智力 | 11 | 5 |
| 魔契师 | d8 | 魅力 | 感知/魅力 | 11 | 5 |
| 术士 | d6 | 魅力 | 体质/魅力 | 9 | 4 |
| 法师 | d6 | 智力 | 智力/感知 | 9 | 4 |

#### Step 2：选择起源 — 种族与背景

**10种种族核心特性**（`data/races.py`, 321行）：

| 种族 | 速度 | 体型 | 特殊感官 | 核心特性 |
|------|------|------|----------|----------|
| 人类 | 30尺 | 中型 | — | 全能+1 |
| 矮人 | 25尺 | 中型 | 黑暗视觉60尺 | 矮人刚毅(+1 HP/级)、毒素抗性 |
| 精灵 | 30尺 | 中型 | 黑暗视觉60尺 | 精类血统(魅惑免疫)、长休变体(冥想4h) |
| 半身人 | 25尺 | 小型 | — | 幸运(重掷1)、勇敢(恐慌优势)、半身人敏捷 |
| 龙裔 | 30尺 | 中型 | — | 龙息武器、伤害抗性 |
| 侏儒 | 25尺 | 小型 | 黑暗视觉60尺 | 侏儒狡黠 |
| 半精灵 | 30尺 | 中型 | 黑暗视觉60尺 | 暗裔血统(魅惑免疫)、2项+1属性 |
| 半兽人 | 30尺 | 中型 | 黑暗视觉60尺 | 不屈(0HP→1HP)、凶猛重击 |
| 提夫林 | 30尺 | 中型 | 黑暗视觉60尺 | 地狱抗性(火焰抗性)、炼狱遗产 |
| 神裔 | 30尺 | 中型 | 黑暗视觉60尺 | 光辉遗产 |

**16种背景**（`data/backgrounds.py`, 182行）：每种背景提供 2项技能熟练 + 1项起源专长 + 属性加成（2/1分配，每项不超过20）。

#### Step 3：属性分配 — 三种方式

```python
# 标准阵列
STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]

# 购点法（27点预算）
POINT_BUY_BUDGET = 27
POINT_BUY_COST = {8:0, 9:1, 10:2, 11:3, 12:4, 13:5, 14:7, 15:9}  # 8→15

# 掷骰法：4d6弃最低
roll_4d6_drop_lowest() → sorted([d6,d6,d6,d6])[1:] 求和
```

**12职业默认属性分配表** `_DEFAULT_ARRAY_BY_CLASS`：为每个职业预设最优属性分配，玩家可在此基础上调整。

#### Step 5：衍生数值自动计算

```python
def ability_modifier(score: int) -> int:
    """属性调整值 = floor((score - 10) / 2)"""
    return (score - 10) // 2

def proficiency_bonus(level: int) -> int:
    """熟练加值 = 2 + (level - 1) // 4"""
    return 2 + (level - 1) // 4  # 1-4级+2, 5-8级+3, ..., 17-20级+6

def hit_points_level1(hit_die: int, con_mod: int, race: str) -> int:
    """1级HP = 生命骰面值 + 体质调整值 (+矮人刚毅+1)"""
    hp = hit_die + con_mod
    if race == "矮人":
        hp += 1  # 矮人刚毅
    return max(1, hp)  # 下限1

def unarmored_ac(dex_mod: int, con_mod: int, wis_mod: int, char_class: str) -> int:
    """无甲AC计算"""
    if char_class == "野蛮人":
        return 10 + dex_mod + con_mod  # 野蛮人无甲防御
    if char_class == "武僧":
        return 10 + dex_mod + wis_mod  # 武僧无甲防御
    return 10 + dex_mod                 # 标准无甲

def passive_perception(wis_mod: int, proficient: bool, prof_bonus: int) -> int:
    """被动察觉 = 10 + 感知调整值 (+熟练加值 if 察觉熟练)"""
    return 10 + wis_mod + (prof_bonus if proficient else 0)

def spell_save_dc(casting_mod: int, prof_bonus: int) -> int:
    """法术豁免DC = 8 + 施法属性调整值 + 熟练加值"""
    return 8 + casting_mod + prof_bonus

def spell_attack_bonus(casting_mod: int, prof_bonus: int) -> int:
    """法术攻击加值 = 施法属性调整值 + 熟练加值"""
    return casting_mod + prof_bonus
```

### 3.2 前端角色创建界面

- **数据预加载**：并行拉取 `/races`, `/classes`, `/backgrounds`, `/spells`
- **9个字段**：角色名/种族/职业/等级/子职/背景/阵营/六维属性/世界设定
- **4种属性分配方式**：标准阵列 / 购点法 / 掷骰(后端4d6去最低) / 自由输入
- **HP/AC 实时预览**：前端根据选中职业+属性实时计算
- **提交流程**：校验 → `POST /campaign` → `POST /character` → `POST /open` → 开场预览 → 进入游戏

---

## 四、LangGraph 编排管线（核心判定链）

实现在 `brain/graph.py`（586行），是整个系统的核心。采用 LangGraph `StateGraph` 构建 8 节点有向图，通过 `SqliteSaver` checkpointer 支持断点恢复和 HITL。

### 4.1 八节点管线总览

```
classify → [条件路由] → retrieve → verify → [条件路由] → resolve → narrate → apply → END
                                │              │
                                │              ├─ HITL → confirm → resolve
                                │              └─ 驳回 → retrieve_retry → resolve
                                │
                                └─ other/end_combat → 跳过 retrieve 直接 resolve
```

**条件路由规则**（`build_graph()` 中定义）：

| 路由函数 | 源节点 | 条件 | 目标 |
|----------|--------|------|------|
| `_director_route` | classify | action_type ∈ {other, end_combat} | resolve |
| `_director_route` | classify | 其余 | retrieve |
| `_after_verify` | verify | 校验失败 | retrieve (retry) |
| `_after_verify` | verify | HITL 启用 | confirm (interrupt) |
| `_after_verify` | verify | 通过 | resolve |
| `_after_confirm` | confirm | 确认通过 | resolve |
| `_after_confirm` | confirm | 驳回 | retrieve |

### 4.2 GameState 数据结构

管线中每个节点读写 `GameState`（`brain/state.py`, 95行），核心字段：

```python
GameState = {
    "player_input": str,        # 玩家原始输入
    "campaign_id": int,         # 战役 ID
    "character_id": int,        # 角色 ID
    "intent": dict,             # classify 输出的结构化意图
    "rules_context": str,       # retrieve 检索到的规则原文
    "verified": bool,           # verify 校验结果
    "resolve_result": dict,     # resolve 确定性计算结果
    "narration": str,           # narrate 生成的叙事文本
    "state_changes": dict,      # 持久化变更指令
    "combat": dict,             # 战斗状态快照
    "action_options": list,     # narrate 生成的 3 个行动选项
    "error": str,               # 错误信息
}
```

### 4.3 节点详解

#### 4.3.1 classify 节点 — Director Agent 意图分类

**函数**：`agents/director.py: classify_intent(state: GameState) -> dict`

**输入**：玩家原始输入 + 游戏上下文（角色卡/场景/战斗/四层记忆）
**输出**：`{"intent": {...}, "error": ""}`

**Director Prompt 模板**（`_DIRECTOR_PROMPT`，约 60行）：

```
你是D&D 5E意图分类器。把玩家输入分类为动作意图,只输出JSON。

action_type 取值 (23种):
  attack / cast / ability_check / explore / start_combat / end_combat
  rest / social / levelup / travel / dash / dodge / disengage / help
  ready / hide / search / study / use_item / grapple / shove
  opportunity_attack / other

玩家权限约束：
  玩家只能描述自己角色的动作，无权设定场景/召唤怪物/宣布战斗开始结束。

检定门槛(DMG「骰子的角色」):
  needs_check=false: 任务轻而易举 / 失败无后果 / 社交友好 / 已知路线
  needs_check=true: 按DC锚点 5/10/15/20/25/30
  attack/cast/start_combat/hide/grapple/shove/opportunity_attack 总是掷骰
```

**上下文注入**（`_build_classify_context()`）：

| 上下文片段 | 内容 | 用途 |
|----------|------|------|
| 角色卡 | 名称/种族/职业/等级/HP/AC/速度/属性/当前武器/法术位 | 让 LLM 填 weapon/spell_level |
| 场景 | 地点/环境地形/时间/NPC/情境 | 让 LLM 填 terrain/npc_name |
| 战斗状态 | 第N轮/参战者数 | 判断是否在战斗中 |
| 近期对话 | 最近4条对话摘要(截300字) | 上下文连贯性 |
| 前情提要 | 跨Session浓缩摘要(截300字) | 长期连贯性 |
| 相关记忆 | 语义检索 top-3 记忆 | 补充背景 |

**JSON 解析失败重试**（D2 机制）：解析失败时重试 ≤3 次，把"只输出纯JSON"反馈进 prompt。

**确定性目标匹配**（`_resolve_target_cid()`）：
```
匹配优先级: cid精确 → name精确 → name互含 → 唯一存活敌人
命中写入 intent["target_cid"]，供 resolve/apply 确定性定位目标
```

#### 4.3.2 retrieve 节点 — RAG 规则检索

**函数**：`brain/graph.py: retrieve(state) -> state`

**输入**：`intent.retrieval_query`（由 classify 生成的规则检索串）
**输出**：`rules_context`（检索到的规则原文）

**检索流程**：
1. 从 intent 提取 `retrieval_query`（如"攻击检定 敏捷 武器 命中 AC"）
2. 调用 `knowledge/hybrid.py` 的混合检索：BM25 + 向量 RRF 融合
3. 三集合并行检索：`dnd_rules`（数据）/ `dnd_rule_text`（规则文本）/ `dnd_rule_spec`（结构化规则点）
4. RRF（Reciprocal Rank Fusion）融合排序
5. 截取 top-K 结果拼接为 `rules_context`

#### 4.3.3 verify 节点 — 规则校验

**函数**：`agents/rule_judge.py: verify(state) -> state`

**校验规则**：
- 关键词预检：判定参数与规则原文是否一致
- 冲突驳回：LLM 提出的 DC/属性/技能与规则原文冲突时驳回，重检索
- HITL 审批：启用时通过 LangGraph `interrupt()` 让 DM 确认 y/n

#### 4.3.4 resolve 节点 — 23种动作分派（纯代码，LLM不可绕过）

**函数**：`brain/graph.py: resolve(state) -> state`

这是整个系统的核心安全边界。resolve 完全由确定性代码执行，LLM 不可绕过。

**分派逻辑**：

| action_type | 分派目标 | 处理逻辑 |
|-------------|----------|----------|
| `attack` | `_resolve_multi_attack()` | 多次攻击检定→命中→伤害（含重击骰翻倍） |
| `cast` | `_resolve_cast()` | 法术位检查→成分校验→效应结算(攻击/豁免/自动/治疗) |
| `ability_check` / `explore` | `_resolve_ability_check()` | `check.ability_check()` vs DC |
| `dash` | 状态标记 | `combat.use_action("dash")`，本回合额外移动=速度 |
| `dodge` | 状态标记 | `combat.use_action("dodge")`，对本角色攻击劣势 |
| `disengage` | 状态标记 | `combat.use_action("disengage")`，本回合移动不引发借机攻击 |
| `help` | 状态标记 | `combat.use_action("help")`，盟友下次检定优势 |
| `ready` | 状态标记 | `combat.use_action("ready")`，设定触发条件 |
| `hide` | 检定 | `check.ability_check(dex_stealth)` vs DC 15 (2024 PHB硬编码) |
| `search` | 检定 | `check.ability_check(wis_perception 或 int_investigation)` vs DC |
| `study` | 检定 | `check.ability_check(int_study)` vs DC |
| `use_item` | 物品检查 | 检查治疗药水→`damage.roll_heal()` |
| `grapple` | 竞技检定 | `check.ability_check(str)` vs 目标豁免 |
| `shove` | 竞技检定 | `check.ability_check(str)` vs 目标豁免→倒地或推开 |
| `social` | 社交检定 | NPC态度DC修正 + 技能检定 |
| `rest` | 休息结算 | `rest.short_rest()` / `rest.long_rest()` |
| `levelup` | 升级结算 | `levelup.level_up()` 五步骤 |
| `travel` | 旅行结算 | 旅行步调 + 导航检定 + 随机遭遇 |
| `start_combat` | 开始战斗 | `combat.roll_initiative()` + 持久化 |
| `end_combat` | 结束战斗 | 清理战斗状态 |
| `opportunity_attack` | 借机攻击 | 反应检定 |
| `other` | 纯叙事 | 不掷骰，直接传递到 narrate |

#### 4.3.5 narrate 节点 — LLM 叙事生成

**函数**：`brain/graph.py: narrate(state) -> state`

**输入**：resolve_result（已锁定的掷骰结果） + 四层记忆 + 场景上下文
**输出**：narration（2-4句第二人称叙事） + action_options（3个行动选项） + state_changes

**叙事 Prompt 注入内容**：

| 层级 | 来源 | 截取量 | 用途 |
|------|------|--------|------|
| ① 工作记忆 | `store.get_recent_logs(n=6)` | 最近6回合原文 | 短期连贯性 |
| ② 中期记忆 | `store.get_summary()` | rolling_summary 前500字 | 剧情压缩摘要 |
| ③ 长期记忆 | `memory.retrieve_memories(top_k=20)` | 语义检索 top-20 | 跨Session记忆 |
| ④ 前情提要 | `memory.get_recap()` | 浓缩摘要 | 跨Session连贯 |
| 场景上下文 | `world.scene_context()` | 当前场景格式化串 | 让DM在场景中叙事 |

**关键约束**：掷骰结果已锁定，LLM 不可修改数值。Prompt 明确要求"以下骰子结果不可更改，请据实叙事"。

#### 4.3.6 apply 节点 — 持久化与状态更新

**函数**：`brain/graph.py: apply_node(state) -> state`

**持久化操作**：
1. HP/法术位/状态条件 → 写入 `Character` SQLModel
2. 战斗状态 → 写入 `CombatState` SQLModel
3. 日志 → 写入 `Log` SQLModel（玩家输入/AI回复/骰子/状态变更/RAG引用）
4. 场景更新 → 写入 `Scene` SQLModel
5. 战斗轮次推进 → `combat.advance_turn()`
6. 异步记忆处理 → `asyncio.ensure_future(_async_memory_process())`

### 4.4 免检定机制

对 `ability_check` / `explore` / `search` / `study`，当 `needs_check=false` 时自动成功。

实现在 `engine/core_loop.py`（680行）：

```python
class ActionCertainty(Enum):
    CERTAIN = "certain"       # 自动成功（角色轻而易举）
    UNCERTAIN = "uncertain"   # 需要掷骰
    IMPOSSIBLE = "impossible" # 自动失败（不可能完成）

def should_roll_dice(action_desc: str) -> ActionCertainty:
    """关键词推断是否需要掷骰"""
    # 关键词："轻松"/"直接"/"简单" → CERTAIN
    # 关键词："尝试"/"试图"/"努力" → UNCERTAIN
    # 关键词："不可能"/"无法" → IMPOSSIBLE
```

**DMG DC 参考表**：

| 难度 | DC | 示例 |
|------|-----|------|
| 很容易 | 5 | 踹开朽烂的门 |
| 简单 | 10 | 回忆常识 |
| 中等 | 15 | 无压力下爬结实的梯子 |
| 困难 | 20 | 跟踪经验丰富的猎人 |
| 很困难 | 25 | 破解古老符文 |
| 几乎不可能 | 30 | 20尺跳跃 |

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

### 5.2 战斗数据模型

实现在 `engine/combat.py`（1125行）。

#### Combatant 数据类

```python
@dataclass
class Combatant:
    cid: str              # 唯一标识（角色ID或怪物名+序号）
    name: str             # 显示名称
    dex_mod: int          # 敏捷调整值
    initiative: int = 0   # 先攻值 (d20 + dex_mod)
    side: str = "player"  # "player" | "enemy"
    hp: int = 0           # 当前 HP
    hp_max: int = 0       # HP 上限
    ac: int = 10          # 护甲等级
    # 动作经济
    action_used: bool = False
    bonus_action_used: bool = False
    reaction_used: bool = False
    # 移动
    speed: int = 30       # 速度(尺)
    remaining_move: int = 0  # 本回合剩余移动
    # 状态
    dead: bool = False
    fled: bool = False
    surprised: bool = False  # 2024版突袭标记
    conditions: set = set()  # 状态条件集合
    # 专注
    concentration_spell: str = ""
    # 传奇动作
    legendary_actions_used: int = 0
    legendary_actions_max: int = 0
```

#### Combat 数据类

```python
@dataclass
class Combat:
    participants: dict[str, Combatant]   # cid → Combatant
    initiative_order: list[Combatant]    # 先攻降序列表
    round: int = 1                       # 当前轮次
    current_index: int = 0               # 当前先攻列表索引
    active: bool = False                 # 战斗是否激活
```

### 5.3 先攻掷骰完整逻辑

`roll_initiative(participants: list[dict]) -> Combat`

```python
def roll_initiative(participants):
    for p in participants:
        init_roll = dice.roll_die(20)  # d20
        # 突袭劣势：2024版被突袭者先攻掷骰劣势
        if p.get("surprised"):
            init_roll = min(dice.roll_die(20), dice.roll_die(20))
        # 隐形优势：隐形的角色先攻优势
        if "隐形" in p.get("conditions", []):
            init_roll = max(dice.roll_die(20), dice.roll_die(20))
        p["initiative"] = init_roll + p["dex_mod"]
    # 同组怪物共用先攻（规则书标准做法）
    # 按 initiative 降序排列，平局时 dex_mod 高的在前
    combat.initiative_order.sort(key=lambda c: (-c.initiative, -c.dex_mod))
```

### 5.4 回合推进完整逻辑

`advance_turn(combat: Combat) -> Combatant`

```python
def advance_turn(combat):
    while True:
        combat.current_index += 1
        if combat.current_index >= len(combat.initiative_order):
            combat.current_index = 0
            combat.round += 1          # 新一轮
        c = combat.initiative_order[combat.current_index]
        # 跳过条件：死亡 / 逃跑 / 失能自动结束回合
        if c.dead or c.fled:
            continue
        # 重置动作经济
        c.action_used = False
        c.bonus_action_used = False
        c.reaction_used = False
        c.remaining_move = c.speed
        c.legendary_actions_used = 0
        # 轮次 +6秒（DMG 时间推进）
        return c
```

`begin_turn()` 特殊处理：
- 0HP 玩家角色 → 自动掷死亡豁免
- 失能状态 → 自动结束回合（跳过行动）

### 5.5 动作经济完整追踪

```python
def can_take_action(c) -> bool:
    return not c.action_used and not _is_incapacitated(c)

def can_take_bonus_action(c) -> bool:
    return not c.bonus_action_used and not _is_incapacitated(c)

def can_take_reaction(c) -> bool:
    return not c.reaction_used

def use_action(c, action_type: str):
    c.action_used = True

def use_bonus_action(c, action_type: str):
    c.bonus_action_used = True

def use_reaction(c, action_type: str):
    c.reaction_used = True

def free_interaction(c):
    """每回合一次免费交互（开门/拔剑等）不耗动作"""
    pass
```

### 5.6 移动系统完整逻辑

```python
def move(combatant, distance_feet: int) -> int:
    """移动，返回实际移动距离。困难地形每尺消2尺。"""
    cost = distance_feet  # 正常地形 1:1
    # 困难地形：每尺消耗 2 尺移动
    if terrain == "difficult":
        cost = distance_feet * 2
    if cost > combatant.remaining_move:
        distance_feet = combatant.remaining_move // (2 if difficult else 1)
    combatant.remaining_move -= cost
    return distance_feet

def move_crawl(combatant, feet):      # 匍匐：速度减半
    return move(combatant, feet * 2)   # 每尺消耗2尺

def move_climb(combatant, feet):      # 攀爬：速度减半
    return move(combatant, feet * 2)

def move_swim(combatant, feet):       # 游泳：速度减半
    return move(combatant, feet * 2)

def long_jump(combatant, str_mod):    # 跳远 = 力量调整值尺数
    return str_mod  # 助跑至少10尺

def high_jump(combatant, str_mod):    # 跳高 = 3 + 力量调整值尺
    return 3 + str_mod

def move_squeeze(combatant):          # 挤过狭窄空间：速度减半
    pass
```

**掩护规则**：

| 掩护类型 | AC 加值 | 敏捷豁免加值 |
|----------|---------|------------|
| 半身掩护 | +2 | +2 |
| 四分之三掩护 | +5 | +5 |
| 全身掩护 | — | 不可选为目标 |

**擒抱/推撞（2024版）**：

```python
def attempt_grapple(attacker, target):
    """擒抱：力量竞技检定 vs 目标豁免"""
    dc = 8 + attacker.str_mod + attacker.prof_bonus
    # 目标可用力量或敏捷豁免（取较高者）
    # 失败 → 受擒状态（速度=0）

def attempt_shove(attacker, target):
    """推撞：力量竞技检定 vs 目标豁免"""
    dc = 8 + attacker.str_mod + attacker.prof_bonus
    # 失败 → 倒地 或 推开20尺
```

### 5.7 战斗结束判定

`check_combat_end(combat: Combat) -> str | None`

- 所有敌人死亡/逃跑 → "victory"
- 所有玩家 dead=True（非0HP，0HP只是倒下） → "defeat"
- 否则 → None（战斗继续）

### 5.8 11种战斗动作

`engine/actions.py`（955行）定义了 11 种战斗动作：

| 动作 | 类型 | 效果 |
|------|------|------|
| `attack` | 动作 | 攻击检定→命中→伤害（含条件优劣势/回避/力竭惩罚/重击） |
| `dash` | 动作 | 本回合额外移动=速度 |
| `disengage` | 动作 | 本回合移动不引发借机攻击 |
| `dodge` | 动作 | 对本角色的攻击具有劣势，敏捷豁免优势 |
| `help` | 动作 | 盟友的下次检定具有优势 |
| `hide` | 动作 | 敏捷(潜行)检定 vs DC 15 (2024 PHB硬编码) |
| `magic` | 动作 | 施法（由 cast 分派处理） |
| `ready` | 动作 | 设定触发条件，条件满足时执行 |
| `search` | 动作 | 感知(察觉)或智力(调查)检定 |
| `study` | 动作 | 智力检定(奥秘/历史/调查/自然/宗教) |
| `utilize` | 动作 | 使用物品/工具 |

**武器攻击完整流程**（`action_attack()`）：

```
1. 构建 WeaponProfile（武器名/伤害骰/伤害类型/附加伤害骰/精通词条）
2. 条件优劣势计算（根据攻守双方状态条件）
3. check.attack_roll() → d20 + 命中加值 vs AC
4. 天然20 → 必中 + 重击（骰数翻倍，常数不加倍）
5. 天然1 → 必失手
6. 命中 → damage.roll_damage() → 伤害管线
7. 回避状态 → 攻击劣势
8. 力竭惩罚 → d20减值 = 等级×2
```

### 5.9 多人战斗回合

`brain/combat_flow.py`（422行）管理多人战斗回合：

**核心函数**：`advance_and_resolve(campaign_id) -> FlowResult`

```python
def advance_and_resolve(campaign_id):
    """推进回合并自动结算怪物/濒死者回合，直到轮到下一个可行动玩家。
    guard 8*n+16 封顶，防止无限循环。"""
    # 1. advance_turn() → 下一个参战者
    # 2. 如果是怪物 → run_monster_turn() 自动攻击随机玩家
    # 3. 如果是濒死玩家 → _roll_death_save() 自动掷死亡豁免
    # 4. 循环直到轮到玩家或战斗结束
    # 5. 单人局自动推进，多人局返回 [] 等待显式 end_turn
```

**怪物 AI**（`run_monster_turn()`）：
- 从站立玩家中随机选目标（`select_target()`）
- 自动执行攻击动作
- 浴血后触发士气检定（`morale_check()`：WIS DC10 豁免，失败则逃跑）

**服务端回合状态机**：
- 回合归属权为唯一真相（服务端权威）
- 玩家行动只消耗动作经济，不隐式推进回合
- 多人局需显式 `end_turn`；单人局自动推进

### 5.10 前端战斗界面

- **CombatBar**：先攻条(水平chip, 当前回合金色高亮) + 参战者HP卡(玩家蓝/敌方红) + 结束回合按钮
- **QuickChips**：攻击/施法/闪避/撤离/疾走/治疗药水快捷按钮
- **模式自动派生**：`combat.active` → combat模式; `scene.npcs` → social模式; 默认 → explore模式

---

## 六、规则判定系统

### 6.1 骰子引擎 (`engine/dice.py`, 343行)

**RNG**：使用 `secrets.randbelow()`（密码学随机，非伪随机），防止骰子可预测。

#### 数据模型

```python
@dataclass
class RollResult:
    dice: list[int]      # 每个骰子的面值
    modifier: int        # 加值
    total: int           # 总计
    expression: str      # 表达式如 "3d8+5"
    crit: bool = False   # 是否重击

@dataclass
class D20Roll:
    d20: int             # d20 面值
    modifier: int        # 加值
    total: int           # 总计
    mode: str            # "normal" | "advantage" | "disadvantage" | "cancelled"
    raw_rolls: list[int] # 原始骰子（优势/劣势时有2个）
```

#### 核心函数

```python
def roll_die(sides: int) -> int:
    """掷单个骰子，secrets.randbelow(sides) + 1"""

def roll_dice(expression: str, crit: bool = False) -> RollResult:
    """解析骰子表达式如 '3d8+5'，crit=True 时骰数翻倍（常数不加倍）"""
    # 解析 NdM+X 格式
    # crit: N → 2N（骰数翻倍）
    # 例: 3d8+5 crit → 6d8+5

def roll_d20(mod: int, advantage: bool, disadvantage: bool) -> D20Roll:
    """d20 掷骰，优劣势处理"""
    # 同时存在优势和劣势 → 抵消 → cancelled 模式（普通掷骰）
    # 优势 → 掷 2 个 d20 取高
    # 劣势 → 掷 2 个 d20 取低
    # 普通 → 掷 1 个 d20
```

#### 派生函数

```python
def ability_modifier(score: int) -> int:
    """属性调整值 = floor((score - 10) / 2)"""

def proficiency_bonus(level: int) -> int:
    """熟练加值 = 2 + (level-1)//4，支持 CR 小数"""

def roll_d100() -> int       # 百分比骰
def roll_d3() -> int         # d3（d6/2 向上取整）
def pick_random(items) -> Any  # 随机表选择
```

### 6.2 检定系统 (`engine/check.py`, 270行)

#### 数据模型

```python
@dataclass
class CheckResult:
    success: bool      # 是否成功
    d20: int           # d20 结果
    total: int         # d20 + 调整值
    dc: int            # 目标 DC
    modifier: int      # 总调整值

class AttackResult:
    hit: bool          # 是否命中
    d20: int           # d20 结果
    total: int         # d20 + 命中加值
    ac: int            # 目标 AC
    natural_20: bool   # 天然 20
    natural_1: bool    # 天然 1
    crit: bool         # 是否重击
```

#### 核心函数

```python
def calc_save_dc(ability_mod: int, prof_bonus: int) -> int:
    """施法豁免DC = 8 + 属性调整值 + 熟练加值"""

def ability_check(mod: int, dc: int, prof: int = 0,
                  proficient: bool = False,
                  advantage: bool = False,
                  disadvantage: bool = False,
                  circ: int = 0) -> CheckResult:
    """属性检定: d20 + 属性调整值 + (熟练加值 if 熟练) + 临时加值 ≥ DC"""
    # circ: 临时 d20 修正（如力竭每级 −2）

def saving_throw(mod: int, dc: int, prof: int = 0,
                 proficient: bool = False,
                 advantage: bool = False,
                 disadvantage: bool = False,
                 waive: bool = False,
                 circ: int = 0) -> CheckResult:
    """豁免检定: 同属性检定，可主动放弃 (waive=True → 直接失败)"""

def attack_roll(mod: int, ac: int,
                advantage: bool = False,
                disadvantage: bool = False,
                circ: int = 0) -> AttackResult:
    """攻击检定: d20 + 命中加值 vs AC
    天然20 → 必中 + 重击
    天然1 → 必失手"""

def passive_check(mod: int, prof: int = 0,
                  proficient: bool = False,
                  advantage: bool = False,
                  disadvantage: bool = False) -> int:
    """被动检定 = 10 + 调整值
    优势 +5 / 劣势 −5"""
```

### 6.3 伤害系统 (`engine/damage.py`, 369行)

#### 数据模型

```python
@dataclass
class DamageRequest:
    expression: str          # 如 "2d6+3"
    damage_type: str         # 伤害类型
    target_immunities: list  # 免疫列表
    target_resistances: list # 抗性列表
    target_vulnerabilities: list  # 易伤列表

@dataclass
class DamageResult:
    rolls: list[int]         # 每个骰子面值
    raw_total: int           # 原始总计
    final_total: int         # 管线后最终总计
    damage_type: str
    immune: bool             # 是否免疫
    resisted: bool           # 是否抗性减半
    vulnerable: bool         # 是否易伤翻倍

@dataclass
class DeathTracker:
    successes: int = 0       # 成功次数 (0-3)
    failures: int = 0        # 失败次数 (0-3)
    stable: bool = False     # 是否稳定
    dead: bool = False       # 是否死亡
```

#### 13种伤害类型

| 中文 | 英文 | 中文 | 英文 |
|------|------|------|------|
| 酸蚀 | acid | 火焰 | fire |
| 寒冷 | cold | 力场 | force |
| 光耀 | radiant | 闪电 | lightning |
| 暗蚀 | necrotic | 毒素 | poison |
| 心灵 | psychic | 辐射 | thunder |
| 穿刺 | piercing | 钝击 | bludgeoning |
| 挥砍 | slashing | | |

#### 伤害管线

```python
def apply_damage_pipeline(raw_damage: int, damage_type: str,
                          immunities: list, resistances: list,
                          vulnerabilities: list) -> int:
    """伤害管线: 免疫 → 数值修正 → 抗性(减半) → 易伤(翻倍) → 下限0"""
    # Step 1: 免疫检查
    if damage_type in immunities:
        return 0
    # Step 2: 数值修正（无当前实现，预留接口）
    # Step 3: 抗性减半
    if damage_type in resistances:
        raw_damage = raw_damage // 2
    # Step 4: 易伤翻倍
    if damage_type in vulnerabilities:
        raw_damage = raw_damage * 2
    # Step 5: 下限 0
    return max(0, raw_damage)

def roll_damage(expression: str, damage_type: str,
                crit: bool = False, **targets) -> DamageResult:
    """掷伤害骰 + 管线处理"""

def apply_damage_to_hp(hp_current: int, damage: int,
                       temp_hp: int = 0) -> tuple[int, int]:
    """先扣临时 HP，再扣正常 HP。临时 HP 不叠加取较大者。"""
```

#### 死亡豁免完整状态机

```python
def death_save(con_mod: int = 0, **kw) -> tuple[DeathTracker, dict]:
    """d20 ≥ 10 记成功，< 10 记失败
    天然1 = 两次失败
    天然20 = 恢复 1HP + 计数归零
    3次成功 = 稳定
    3次失败 = 死亡"""

def damage_at_zero_hp(tracker: DeathTracker, damage: int,
                      hp_max: int) -> tuple[DeathTracker, bool]:
    """0HP时受伤害追加失败（重击两次）
    伤害 ≥ max_hp 即死"""

def check_massive_damage(damage: int, hp_max: int) -> bool:
    """过量伤害致死：伤害 ≥ HP上限即死"""
```

### 6.4 状态条件 (`engine/conditions.py`, 359行)

#### 15种状态完整效果对照表

| 状态 | 速度 | 攻击(攻方) | 攻击(守方) | 豁免 | 检定 | 特殊效果 |
|------|------|-----------|-----------|------|------|----------|
| 目盲 | — | 劣势 | — | — | 自动失败(视觉) | 自动失败(视觉相关) |
| 魅惑 | 正常 | — | 不可攻击魅惑源 | — | — | 不可攻击来源 |
| 耳聋 | 正常 | — | — | 劣势(听觉) | 自动失败(听觉) | — |
| 恐慌 | 正常 | 劣势 | 劣势 | — | — | 不可靠近来源 |
| 受擒 | 速度=0 | — | — | — | — | 可被拖拽 |
| 失能 | 速度正常 | — | — | — | — | 不可动作/反应 |
| 隐形 | 正常 | — | 极难被看到 | — | — | 重度遮蔽 |
| 麻痹 | 速度=0 | — | 5尺内自动重击 | 失败(敏捷) | 失败(力量/敏捷) | 隐含失能 |
| 石化 | 速度=0 | — | 5尺内自动重击 | 失败 | 失败 | 全伤害抗性+隐含失能 |
| 力竭 | 见等级 | d20减值=等级×2 | — | — | — | 6级即死 |
| 中毒 | 正常 | 劣势 | 劣势 | — | — | — |
| 倒地 | 速度=0(只能爬) | 劣势 | 5尺内自动重击 | — | — | — |
| 束缚 | 速度=0 | — | 劣势 | 失败(敏捷) | — | — |
| 震慑 | 速度=0 | — | 劣势 | 失败 | 失败 | 隐含失能 |
| 昏迷 | 速度=0 | — | 5尺内自动重击 | 失败(敏捷/力量) | 失败 | 隐含失能+倒地 |

#### 力竭累加规则

```python
def d20_penalty(exhaustion_level: int) -> int:
    """d20减值 = 等级 × 2（适用于所有d20检定）"""
    return exhaustion_level * 2  # R-GLS-047

def speed_reduction(exhaustion_level: int) -> int:
    """速度减少 = 等级 × 5 尺"""
    return exhaustion_level * 5

# 力竭等级效果表:
# 1级: 速度-5, d20-2
# 2级: 速度-10, d20-4
# 3级: 速度-15, d20-6
# 4级: 速度-20, d20-8
# 5级: 速度-25, d20-10
# 6级: 即死
```

#### 攻击状态修正函数

```python
def attack_modifiers(attacker_state: ConditionState,
                     defender_state: ConditionState,
                     distance: int = 5) -> dict:
    """根据攻守双方状态计算优劣势 + 自动重击"""
    # 返回: {advantage: bool, disadvantage: bool, auto_crit: bool}
    # 5尺内自动重击: 麻痹/昏迷目标
    # 石化目标: 全伤害抗性 + 隐含失能
```

### 6.5 法术系统 (`engine/spellcasting.py`, 1274行)

#### 数据模型

```python
@dataclass
class CasterState:
    spell_slots: dict[int, int]    # {环阶: 剩余}
    max_spell_slots: dict[int, int] # {环阶: 上限}
    casting_ability: str           # 施法属性 (int/wis/cha)
    concentration_spell: str = ""  # 当前专注法术
```

#### 核心函数

```python
def compute_spell_save_dc(casting_mod: int, prof_bonus: int) -> int:
    """法术豁免DC = 8 + 施法属性调整值 + 熟练加值"""

def consume_spell_slot(caster: CasterState, spell_level: int) -> bool:
    """消耗法术位，戏法(0环)不耗位"""

def check_casting_components(caster, spell) -> tuple[bool, str]:
    """V/S/M 成分校验
    阻止状态列表: 失能/束缚/受擒(无法S)/沉默(无法V)"""

def resolve_upcast(spell: dict, slot_level: int) -> dict:
    """升环施法效应解析"""

def restore_slots_on_long_rest(caster: CasterState):
    """长休恢复全部法术位"""
```

**效应类型四种分支**：

| 类型 | 结算方式 | 示例 |
|------|----------|------|
| 攻击型 | `attack_roll()` vs AC → 命中→伤害 | 火焰箭 |
| 豁免型 | 目标 `saving_throw()` vs DC → 失败→伤害 | 火球术 |
| 自动型 | 直接生效，无需检定 | 法师护甲 |
| 治疗型 | `roll_heal()` 恢复 HP | 治疗创伤 |

### 6.6 专注维持 (`engine/concentration.py`, 279行)

```python
@dataclass
class ConcentrationSlot:
    spell_id: str | None = None  # 当前集中的法术
    caster_id: str = ""

def concentration_save_dc(damage_taken: int) -> int:
    """专注维持DC = max(10, floor(damage/2))，至高30"""
    return min(30, max(10, damage_taken // 2))

class ConcentrationManager:
    def set_concentration(self, caster_id, spell_id) -> bool:
        """设置专注：旧的自动结束（max 1 concurrent）"""
    def break_concentration(self, caster_id) -> bool:
        """中断专注：失能/死亡/主动放弃"""
    def concentration_save_on_damage(self, caster_id, damage, con_mod, ...) -> dict:
        """受伤时体质豁免维持专注，失败失去专注"""
```

**专注中断条件**：
- 施展另一个专注法术 → 旧专注自动结束
- 失能或死亡 → 失去专注
- 受伤 → DC = max(10, 伤害/2) 的体质豁免，失败失去专注
- 可随时主动终止（无需动作）

---

## 七、探索与社交系统

### 7.1 探索系统 (`brain/exploration.py`, 1268行)

#### 旅行步调表

| 步调 | 速度 | 隐匿 | 察觉 | 导航检定 |
|------|------|------|------|----------|
| 快速 | 400尺/分 | 劣势 | 劣势 | 无 |
| 中速 | 300尺/分 | 劣势 | 正常 | 正常 |
| 慢速 | 200尺/分 | 正常 | 优势 | 正常 |

#### 11种地形参数表

| 地形 | 快速速度 | 中速速度 | 慢速速度 | 导航DC | 遭遇DC |
|------|---------|---------|---------|--------|--------|
| 寒带 | 400 | 300 | 200 | 15 | 15 |
| 海岸 | 400 | 300 | 200 | 10 | 12 |
| 荒漠 | 300 | 200 | 150 | 20 | 15 |
| 森林 | 300 | 200 | 150 | 10 | 10 |
| 草原 | 400 | 300 | 200 | 5 | 12 |
| 丘陵 | 300 | 200 | 150 | 10 | 12 |
| 山地 | 200 | 150 | 100 | 20 | 15 |
| 沼泽 | 200 | 150 | 100 | 15 | 10 |
| 幽暗地域 | 200 | 150 | 100 | 20 | 10 |
| 城市 | 400 | 300 | 200 | 5 | 15 |
| 水路 | 400 | 300 | 200 | 10 | 12 |

#### 光照与遮蔽

| 光照 | 遮蔽 | 影响 |
|------|------|------|
| 明亮 | 无遮蔽 | 正常视觉 |
| 微光 | 轻度遮蔽 | 黑暗视觉正常，否则攻击劣势 |
| 黑暗 | 重度遮蔽 | 失明状态，除非有黑暗视觉 |

#### 特殊感官

| 感官 | 范围 | 效果 |
|------|------|------|
| 黑暗视觉 | 60尺 | 微光→明亮，黑暗→微光 |
| 震颤感知 | 可变 | 无需视觉探测振动 |
| 真实视觉 | 可变 | 看穿变形/隐形/幻象 |
| 盲视 | 可变 | 无需视觉感知环境 |

### 7.2 社交流程 (`brain/social.py`, 609行)

#### 社交四步循环

```
1. DM 扮演 NPC（口吻/表情/姿态，NPC 有自己的目标和态度）
    ↓
2. 玩家角色扮演回应（描述意图和方法）
    ↓
3. DM 判断是否需要掷骰（好的角色扮演可能自动成功）
    ↓
4. 掷骰解决（说服/欺瞒/威吓/表演/洞悉检定）
    ↓
  循环
```

#### NPC 态度系统

```python
@dataclass
class NPC:
    name: str
    role: str              # 角色描述
    attitude: str          # "friendly" | "indifferent" | "hostile"
    knowledge: list        # NPC 知道的信息
    goals: list            # NPC 的目标
    secrets: list          # NPC 的秘密
    cr: int = 0            # 挑战等级

@dataclass
class SocialState:
    conversation_history: list   # 对话历史
    attitude_changes: list       # 态度变更记录
    revealed_secrets: list       # 已揭示的秘密
    consecutive_successes: int   # 连续成功计数
    consecutive_failures: int    # 连续失败计数
```

**态度与 DC 修正**（设计决策，非规则书原文）：

| 态度 | DC 修正 | 说明 |
|------|---------|------|
| 友好 | -5 | 乐于助人，愿意配合 |
| 冷漠 | 0 | 中立，需要说服 |
| 敌对 | +5 | 不合作，难以说服 |

**态度转换阈值**（项目自拟）：

| 转换方向 | 触发条件 |
|----------|----------|
| 友好 → 冷漠 | 10次检定失败 |
| 冷漠 → 敌对 | 5次检定失败 |
| 敌对 → 冷漠 | 15次检定成功 |
| 冷漠 → 友好 | 10次检定成功 |

**社交技能**：

| 技能 | 属性 | 用途 |
|------|------|------|
| persuasion | CHA | 说服、请求帮助 |
| deception | CHA | 欺瞒、伪装 |
| intimidation | CHA | 威吓、威胁 |
| performance | CHA | 表演、娱乐 |
| insight | WIS | 洞悉、看穿谎言 |

### 7.3 休息机制 (`brain/rest.py`, 1072行)

#### 短休（1小时）

```python
def short_rest(character, hit_dice_to_spend: int = 0) -> dict:
    """短休收益:
    - 消耗生命骰恢复HP：掷骰 + 体质调整值，至少1
    - 特殊特性恢复（野蛮人狂暴等）"""
    # 条件: 必须至少1 HP
    # 每枚生命骰: roll(hit_die_faces) + con_mod
    # 总恢复量至少 1（即使 con_mod 为负）
```

#### 长休（8小时）

```
长休收益:
  - 恢复全部 HP
  - 恢复全部法术位
  - 力竭等级 -1
  - 恢复全部生命骰（上限=等级/2，至少1枚）

条件:
  - 至少 6 小时睡眠
  - 至多 2 小时轻度活动
  - 完成后须等待 16 小时才能再次长休
```

#### 打断条件

| 打断原因 | 短休 | 长休 |
|----------|------|------|
| 投掷先攻 | ✅ | ✅ |
| 施放非戏法法术 | ✅ | ✅ |
| 受到伤害 | ✅ | ✅ |
| 1小时行走/体力劳动 | — | ✅ |

长休每被打断一次需额外休息1小时。

#### 休息状态数据

```python
@dataclass
class RestState:
    type: str = "short"           # "short" | "long"
    duration: float = 0.0         # 已休息时长(小时)
    start_time: float | None = None
    interrupted: bool = False
    completed: bool = False
    interrupt_count: int = 0      # 长休打断计数
    elapsed_at_interrupt: float = 0.0

    def required_duration(self) -> float:
        """长休每被打断一次需额外休息1小时"""
        base = 8 if self.type == "long" else 1
        extra = self.interrupt_count if self.type == "long" else 0
        return base + extra
```

### 7.4 升级系统 (`brain/levelup.py`, 1157行)

#### XP 表（1-20级）

| 等级 | XP | 等级 | XP | 等级 | XP |
|------|-----|------|-----|------|------|
| 1 | 0 | 8 | 34,000 | 15 | 165,000 |
| 2 | 300 | 9 | 48,000 | 16 | 195,000 |
| 3 | 900 | 10 | 64,000 | 17 | 225,000 |
| 4 | 2,700 | 11 | 85,000 | 18 | 265,000 |
| 5 | 6,500 | 12 | 100,000 | 19 | 305,000 |
| 6 | 14,000 | 13 | 120,000 | 20 | 355,000 |
| 7 | 23,000 | 14 | 140,000 | | |

#### 游戏四阶段

| 阶段 | 等级范围 | 描述 |
|------|---------|------|
| T1 | 1-4 | 新手冒险者 |
| T2 | 5-10 | 成熟冒险者 |
| T3 | 11-16 | 力量超凡 |
| T4 | 17-20 | 英雄典范 |

#### XP 分配规则

```python
def award_xp(party: list[dict], total_xp: int) -> dict:
    """将总XP均分给队伍成员，余数向下取整"""
    per_member = total_xp // len(party)
    # 每个成员 xp += per_member

def milestone_xp(milestone_type: str, level: int) -> int:
    """里程碑XP: major→高难度遭遇XP, minor→低难度遭遇XP"""
```

#### 训练变体（DNG变体规则）

| 等级范围 | 训练天数 | 花费(GP) |
|---------|---------|--------|
| 2-4 | 10天 | 20 GP |
| 5-10 | 20天 | 40 GP |
| 11-16 | 30天 | 60 GP |
| 17-20 | 40天 | 80 GP |

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
| 记忆管理 | 四层记忆注入叙事prompt | `brain/memory.py` + narrate |

### 8.2 Director Agent 意图分类完整流程

实现在 `agents/director.py`（267行）。

**完整流程**：

```
玩家输入 + 游戏上下文
    ↓
_build_classify_context() → 组装上下文
    ├─ 角色卡摘要 (名称/种族/职业/HP/AC/武器/法术位)
    ├─ 场景摘要 (地点/地形/时间/NPC/情境)
    ├─ 战斗状态 (第N轮/参战者数)
    ├─ 近期对话 (最近4条摘要)
    ├─ 前情提要 (浓缩摘要截300字)
    └─ 相关记忆 (语义检索top-3)
    ↓
llm.chat(_DIRECTOR_PROMPT, context + player_input, temperature=0.1)
    ↓
_extract_json() → 解析结构化 intent
    ├─ 解析失败 → 重试 ≤3 次（D2机制）
    └─ 成功 → intent dict
    ↓
_resolve_target_cid() → 确定性目标匹配
    ├─ cid精确 → name精确 → name互含 → 唯一存活敌人
    └─ 命中写入 intent["target_cid"]
    ↓
返回 {"intent": {...}, "error": ""}
```

**Director 路由决策**（`route_action()`）：

```python
def route_action(state: GameState) -> str:
    """根据 action_type 决定下一步走向"""
    at = state.get("intent", {}).get("action_type")
    if at in ("other", "end_combat"):
        return "resolve"     # 无判定，直接 resolve
    return "retrieve"        # 先检索规则
```

### 8.3 四层记忆注入完整逻辑

实现在 `brain/memory.py`（769行），参考 Generative Agents 论文。

#### 记忆架构

| 层级 | 来源 | 截取量 | 注入位置 |
|------|------|--------|----------|
| ① 工作记忆 | `store.get_recent_logs(n=6)` | 最近6回合原文 | narrate prompt |
| ② 中期记忆 | `store.get_summary()` | rolling_summary 前500字 | narrate prompt |
| ③ 长期记忆 | `retrieve_memories(top_k=20)` | 语义检索 top-20 | narrate prompt |
| ④ 前情提要 | `get_recap()` | 浓缩摘要 | narrate prompt |

#### 长期记忆检索算法

```python
def retrieve_memories(campaign_id: int, query: str, top_k: int = 5) -> list:
    """语义搜索 + 三分量评分"""
    # 1. 嵌入查询 → Qdrant 语义搜索 top-K
    # 2. 三分量评分:
    #    - recency: 0.99^hours (时间衰减, 权重0.5)
    #    - relevance: 语义相似度 (权重3.0)
    #    - importance: LLM评分1-10 (权重2.0)
    # 3. 加权总分 → top-5

def extract_observations(text: str) -> list:
    """LLM提取 1-3 条关键观察 + 重要性评分(1-10)"""

def store_memory(campaign_id: int, event: str, observation: str,
                 importance: int):
    """嵌入 + 存 Qdrant dnd_memories 集合"""
```

#### 记忆压缩机制

- 每 10 回合折叠：将近期记忆压缩为摘要
- 超限浓缩：超过上下文窗口时，浓缩为前情提要

### 8.4 世界开场 (`brain/world.py`, 127行)

```python
SCENE_FRAMING_PROMPT = (
    "你是D&D 5E DM。依据世界设定与角色,生成跑团开场。遵循叙事技巧:\n"
    "- 简洁:短而回味,聚焦重要信息与线索\n"
    "- 氛围:多感官(视/听/嗅/触)让场景活灵活现\n"
    "- 区分选项:给可感知的不同选项(如左路腐臭/右路水声)\n"
    "- 不臆测角色行动\n"
    "- 秘密与发现:确保冒险所需信息可获得\n"
)

def open_campaign(setting, tone, campaign_id, character_id) -> dict:
    """DM 据世界设定生成完整背景+当前场景"""
    # 返回: {narration, scene, action_options}
    # 持久化: Campaign.setting + Scene

def scene_context(campaign_id) -> str:
    """取当前场景格式化串（供 narrate prompt 用）"""
    # 返回: "当前场景——地点:X 时间:X 氛围:X 环境:X 在场:X 可做之事:X"
```

### 8.5 多智能体协作完整流程

| 智能体 | 职责 | 实现文件 |
|--------|------|----------|
| Director Agent | 意图分类 + 路由决策，注入角色卡/场景/战斗/四层记忆上下文 | `agents/director.py` |
| Rule Judge Agent | 规则检索与校验，冲突时驳回LLM参数 | `agents/rule_judge.py` |
| Narrator | 叙事生成，四层记忆注入 | `agents/narrator.py` |
| Enemy AI | 怪物AI（目标选择/士气检定） | `agents/enemy_ai.py` |
| Combat Engine | 战斗引擎协调 | `agents/combat_engine.py` |
| World Manager | 世界管理/场景更新 | `agents/world_manager.py` |

**协作流程**：

```
Director (意图分类)
    ↓ 路由
Rule Judge (规则校验) ←→ RAG知识库
    ↓
Resolve (纯代码执行)
    ↓
Narrator (叙事生成) ←→ 四层记忆
    ↓
Apply (持久化) → 状态更新广播
```

---

## 九、前端交互界面

### 9.1 页面流转状态机

8种页面状态及其转换：

```
menu (主菜单)
  ├─→ newGame (角色创建) ─→ openingReview (开场预览) ─→ game (游戏主界面)
  ├─→ continue (继续游戏) ─→ game
  ├─→ join (加入游戏) ─→ game
  ├─→ createRoom (创建房间) ─→ game
  ├─→ roomList (房间列表) ─→ game
  └─→ dmJoin (DM身份加入) ─→ game
```

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

### 9.4 WebSocket 事件完整处理流程

**连接流程**：

```
客户端 connect(campaign_id, character_id, name, role)
    ↓
服务端校验:
  ├─ API Key 校验
  ├─ 战役/角色存在性
  ├─ 房间密码校验
  └─ DM 口令校验
    ↓
加入 Socket.IO 房间 campaign_{id}
    ↓
保存会话 (save_session)
    ↓
注册到 CampaignRoom
    ↓
广播 join 事件 (新人加入)
    ↓
发送初始状态:
  ├─ scene_update (当前场景)
  └─ combat_update (战斗状态，若激活)
```

**行动流程**（`on_action` 事件）：

```
客户端 action(player_input)
    ↓
广播 player_acting (通知全员: X正在行动)
    ↓
获取 per-campaign 锁
    ↓
回合检查 (战斗中必须轮到自己)
    ↓
线程池执行 graph.run()
    ↓
广播 result (叙事+骰子+行动选项)
    ↓
广播 scene_update + combat_update (增量同步)
    ↓
发送 character_update (角色数据更新)
    ↓
异步后台执行记忆处理
```

**结束回合流程**（`on_end_turn` 事件）：

```
客户端 end_turn()
    ↓
获取 per-campaign 锁
    ↓
combat_flow.advance_and_resolve()
    ├─ 自动结算怪物回合
    ├─ 自动结算濒死者回合
    └─ 循环直到轮到下一玩家
    ↓
广播 flow events (怪物行动/死亡豁免/轮次/战斗结束)
    ↓
广播 combat_update + turn_advanced
```

### 9.5 角色面板（右侧4标签页）

- **CharacterSheetTab**：头像/名称/种族/职业/等级/HP血条/AC/速度/六维属性/法术位/生命骰/死亡豁免/状态条件/专长
- **SpellbookTab**：按环阶分组法术列表，一键施展
- **InventoryTab**：装备中/背包/同调位，支持同调/解除同调/装备武器
- **RuleLookupTab**：静态规则卡（阶段2计划接RAG）

### 9.6 增量同步机制

服务端只广播变化的状态片段，而非全量状态：

| 事件 | 触发时机 | 广播内容 |
|------|---------|----------|
| `scene_update` | 场景变化 | 地点/时间/氛围/NPC/可做之事 |
| `combat_update` | 战斗状态变化 | 先攻条/当前回合/参战者HP |
| `character_update` | 角色数据变化 | HP/AC/状态条件 |
| `turn_advanced` | 回合推进 | 下一位角色名/是否玩家 |
| `monster_turn` | 怪物行动 | 怪物名称 |
| `monster_action` | 怪物行动结果 | 攻击/伤害/效果 |
| `death_save` | 死亡豁免 | 结果/成功数/失败数 |
| `combat_end` | 战斗结束 | 结果(victory/defeat) |

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

#### Character 表完整字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 主键 |
| `campaign_id` | int | 外键→Campaign |
| `name` | str | 角色名 |
| `race` | str | 种族 |
| `char_class` | str | 职业 |
| `subclass` | str | 子职 |
| `background` | str | 背景 |
| `alignment` | str | 阵营 |
| `level` | int | 等级(1-20) |
| `abilities_json` | JSON | 六维属性 {str/dex/con/int/wis/cha} |
| `spell_slots_json` | JSON | 法术位 {环阶:剩余} |
| `known_spells_json` | JSON | 已知法术列表 |
| `inventory_json` | JSON | 物品栏 |
| `conditions_json` | JSON | 状态条件集合 |
| `attuned_items_json` | JSON | 已同调物品(最多3) |
| `feats_json` | JSON | 已选专长列表 |
| `skill_prof_json` | JSON | 技能熟练列表 |
| `concentration_spell` | str | 当前专注法术 |
| `concentration_dc` | int | 专注DC |
| `xp` | int | 经验值 |
| `equipped_weapon` | str | 当前武器 |
| `equipped_armor` | str | 当前护甲 |
| `hp_current` | int | 当前HP |
| `hp_max` | int | HP上限 |
| `temp_hp` | int | 临时HP |
| `ac` | int | 护甲等级 |
| `speed` | int | 速度(尺) |
| `exhaustion` | int | 力竭等级(0-6) |
| `gold` | int | 金币(GP) |
| `hit_dice_current` | int | 可用生命骰 |
| `hit_dice_max` | int | 生命骰上限 |
| `death_successes` | int | 死亡豁免成功数 |
| `death_failures` | int | 死亡豁免失败数 |
| `stable` | bool | 是否稳定 |
| `dead` | bool | 是否死亡 |
| `has_inspiration` | bool | 英雄气概 |

#### Campaign 表完整字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 主键 |
| `name` | str | 战役名 |
| `setting` | str | 世界设定提示词 |
| `tone` | str | 基调(黑暗/英雄/恐怖) |
| `world_background` | str | AI生成的完整背景故事 |
| `rolling_summary` | str | 剧情压缩摘要 |
| `world_flags_json` | JSON | 世界状态标记 |

#### Scene 表完整字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 主键 |
| `campaign_id` | int | 外键→Campaign |
| `location` | str | 地点 |
| `npcs_json` | JSON | 在场NPC [{name, attitude, role}] |
| `environment` | str | 环境(光照/遮蔽/地形) |
| `time` | str | 时间 |
| `atmosphere` | str | 氛围(多感官) |
| `situation` | str | 场景摘要 |
| `story_log` | str | 叙事日志 |
| `exits_json` | JSON | 可感知选项/出路 |

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

| 事件 | 数据结构 | 功能 |
|------|----------|------|
| `connect` | query: campaign_id, character_id, name, role, api_key | 建立连接，加入战役房间 |
| `disconnect` | — | 断线处理 |
| `action` | `{player_input: str}` | 发送行动指令，跑判定链 |
| `end_turn` | — | 结束回合，服务端自动推进 |
| `ready` | — | 标记准备就绪 |
| `monster_turn` | — | 怪物回合事件 |

**服务端 → 客户端 (15种事件)：**

| 事件 | 数据结构 | 功能 |
|------|----------|------|
| `join` | `{name: str, players: list}` | 新玩家加入通知 |
| `leave` | `{name: str, players: list}` | 玩家离开通知 |
| `scene_update` | `{scene: {location, time, atmosphere, npcs, exits}}` | 场景更新 |
| `combat_update` | `{active, round, current_turn, initiative_order}` | 战斗状态更新 |
| `player_acting` | `{player: str, action: str}` | 玩家行动中提示 |
| `processing` | `{player: str}` | 处理中指示器 |
| `result` | `{player, narration, dice, action_options, turn_hint?}` | 判定结果 |
| `combat_end` | `{outcome: "victory"/"defeat"}` | 战斗结束 |
| `character_update` | `{hp, hp_max, ac, conditions}` | 角色数据更新 |
| `monster_turn` | `{monster: str}` | 怪物回合通知 |
| `monster_action` | `{monster, result}` | 怪物行动结果 |
| `death_save` | `{character, result, successes, failures}` | 死亡豁免结果 |
| `turn_advanced` | `{next, is_player, next_next}` | 回合推进提示 |
| `round_end` | `{round: int}` | 轮次结束 |
| `error` | `{message: str}` | 错误信息 |

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
