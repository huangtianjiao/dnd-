# Graph 动态化改造方案（消灭"描述固定死"）

> 目标：消除 `brain/graph.py` 编排链中大量硬编码的"描述固定死"问题，让判定参数来自数据源与上下文，
> 而非写死常量。同时为 LLM 意图分类补上"信息注入 + 解析失败重试"两道防线。
>
> 状态：实施完成（阶段 A–D 全部落地并验证）
> 关联文件：`brain/graph.py`、`agents/director.py`、`agents/combat_engine.py`、`agents/rule_judge.py`、
> `brain/memory.py`、`brain/exploration.py`、`brain/llm.py`、`stats/models.py`、`stats/store.py`、
> `api/main.py`、`data/spells.py`、`data/equipment.py`、`data/monsters.py`(新建)

---

## 1. 问题诊断

### 1.1 现象

graph 里塞了大量"写死"的描述/数值，导致游戏感失真：

| 位置 | 写死内容 | 后果 |
|---|---|---|
| `graph.py:268` 等攻击 | `weapon = it.get("weapon") or "长剑"`，`"1d8"/"挥砍"` 兜底 | 玩家没明说武器→永远长剑 |
| `graph.py:316-317` 施法 | `spell_dice or "1d8"`、`damage_type or "力场"` | 法术名提取失败→1d8 力场 |
| `graph.py:629-660` 旅行 | `terrain="森林"`、`nav_dc=15`、被动察觉 DC=15 | 不管在哪都按森林/DC15 |
| `graph.py:858-866` 开战 | 敌人 `hp=7/atk+4/1d6+2/挥砍` | 兽人/巨魔也退化成哥布林数值 |
| `graph.py:1371-1374` 自动遇遇 | 永远 1-2 只哥布林 | 无论场景/等级都是哥布林 |

### 1.2 根因（两层）

**根因 A：让 LLM 去填它不该填的字段。**
施法的 `spell_dice/damage_type/effect_type/save_ability`，`data/spells.py` 的 `Spell` 本就有权威值，
代码却让 LLM 猜 + 兜底"1d8力场"。正确做法是 **LLM 只提取 key（spell_name/weapon 名），复杂属性走数据表查**。

**根因 B：classify 节点是个"失忆"入口。**
`director.py:95` `llm.chat(_DIRECTOR_PROMPT, state["player_input"])` 只喂玩家一句话——
角色卡武器、场景地形、已知法术这些**结构化当前态**完全没注入；连现成的四层记忆（工作/中期/长期/前情）也只喂给了 narrate，classify 一行没有。
LLM 看不到信息，自然只能瞎猜/留空 → 走兜底 → 写死常量。

### 1.3 "出错"分两类（决定重试是否有效）

- **解析出错**：LLM 知道答案但输出格式炸（JSON 拼错、字段名错）。重试能救。
- **信息源缺失**：LLM 拿不到该填的信息（武器在角色卡、地形在 Scene）。重试 100 次也白搭——靠信息注入解决。

---

## 2. 改造总览（四阶段）

```
阶段 A 数据层奠基（无 LLM 改动，低风险）
  └ 阶段 B 兜底走数据表（核心对症"描述固定死"）
      └ 阶段 C 信息注入 Director（复用现成记忆）
          └ 阶段 D 解析失败重试
```

执行顺序 A→B→C→D：A/B 风险最低、收益最直接，先做；C 复用现成轮子；D 取决于网关能力验证。

---

## 3. 阶段 A：数据层奠基

### A1. Character 加 `equipped_weapon` 字段
- 文件：`stats/models.py:43` Character 类，加 `equipped_weapon: str = ""`。
- 迁移：`store._migrate`（`store.py:29-61`）自动 `ALTER TABLE ... ADD COLUMN equipped_weapon VARCHAR DEFAULT ''`，无需删库、无需手写迁移。老角色行为空。
- 验证：启动后查 `character` 表有该列。

### A2. 创建端点设默认 + equip 端点 + GET 暴露
- 真实落库在 3 处 API：`POST /character`（`main.py:113`）、`POST /join`（`main.py:390`）、`POST /room/join`（`main.py:774`），都直接 `models.Character(...)`。`char_create.CharacterSheet` 不被 API 用，改它无效。
- 默认值策略：按 `char_class` 用小映射表设（战士→长剑、法师/术士/牧师→匕首、游侠→短弓、圣武士→长剑、游荡者→短剑 …），而非解析 `classes.starting_equipment`（自由文本，脆）。
- 新增端点：`POST /character/{cid}/equip-weapon`，body `{weapon_name}`，仿 `attune_item`（`main.py:232` 区块）。
- `GET /character/{cid}`（`main.py:137-143`）响应加 `"equipped_weapon": ch.equipped_weapon`。
- 前端：当前零影响（不读写武器）；可选改 `ui/app/lib/types.ts` 让 UI 支持。

### A3. 新建 `data/monsters.py`
- 镜照 `data/magic_items.py` 范式：`@dataclass class Monster` + `MONSTERS: dict[str, Monster]` + `get_monster(name) -> Optional[Monster]` + `to_dict()`/`to_combatant_dict()`。
- Monster 字段：`name, cr, hp, ac, dex_mod, attack_bonus, damage_dice, damage_type, speed, abilities, senses, type`。
- 先填约 12 个常见怪：哥布林、兽人、狼、骷髅、僵尸、巨魔、食人魔、地精、黑熊、巨型蜘蛛、灰色软泥、龙裔佣兵。
- 数值参照 5E SRD；`cr` 给 loot 用（不进 Combatant）。
- `to_combatant_dict()` 产出 `_resolve_start_combat` 期望的 `{name, dex_mod, hp_max, attack_bonus, damage_dice, damage_type, side}`。

### A4. 徒手打击特判
- 问题：`equipment.weapon_damage_dice("徒手打击")` 若未收录→KeyError→回退 `"1d8","挥砍"`，错误。
- 方案：`_resolve_attack` 检测 `wname == "徒手"`（或 weapon 为空且无 equipped_weapon）时走徒手规则：伤害 = 1 + 力量调整值，类型"钝击"。
- 确认 `data/equipment.py` 是否收录"徒手打击"（`engine/opportunity_attack.py:114` 有 `name="徒手打击"` 先例可参）。

---

## 4. 阶段 B：兜底走数据表（核心）

> ⚠ **graph.py 与 agents/combat_engine.py 的 `_resolve_attack` 是重复实现**，B1/B2 须双写，易漏 combat_engine.py。
> 三处武器取值：`graph.py:268`、`combat_engine.py:59`、`combat_engine.py:274`。

### B1. 攻击武器三级回退
- 三处 `wname = it.get("weapon") or "长剑"` → `wname = it.get("weapon") or getattr(ch, "equipped_weapon", "") or "徒手"`。
- 命中后取伤害骰：`wname=="徒手"` 走徒手特判（1+str，钝击）；否则 `equipment.weapon_damage_dice/type`，KeyError 兜底改为"报错或保守值"而非静默"1d8挥砍"。

### B2. 施法 get_spell 取权威值
- 现状 `graph.py:328-335` 已查 `get_spell` 取 `concentration/effect_type`，但 `spell_dice/damage_type/save_ability` 仍先读 LLM 猜的 intent 值（`graph.py:316-317`）。
- 改造：把 `get_spell` 查询上移到取值前；命中 `Spell` 时 `damage_dice/damage_type/save_ability/effect_type/concentration/level` 全用权威值，LLM 只需提 `spell_name`（+`spell_level` 用于升环）。
- 未知法术：返回 `{"kind":"cast","error":"未知法术 {name}"}` 而非静默用"1d8力场"。
- 同步改 `combat_engine.py` 对应 cast 分支（若有）。

### B3. 旅行地形从场景读
- `_resolve_travel`（`graph.py:625-676`）：`terrain` 从 `Scene.environment` 读（经 `store.get_scene(camp_id)`）而非写死"森林"。
- `nav_dc` 调 `exploration.terrain_params(terrain).nav_dc`（已有按地形查表能力，`exploration.py:123`）。
- 被动察觉 DC（`graph.py:660` 写死 15）同源从 `terrain_params` 取，或保留 15 作 fallback。

### B4. 开战 get_monster 回填
- `_resolve_start_combat`（`graph.py:846-879`）：遍历 `intent.enemies[]` 时，对每个 enemy 调 `get_monster(name)`；
  命中则用 `to_combatant_dict()` 的真实数值覆盖硬编码默认（`hp=7/atk+4/1d6+2/挥砍`）。
- intent 里 LLM 只需填 `name`(+`count`)，Director prompt（`director.py:81`）相应简化：不再要求 LLM 填 `hp_max`。
- 未收录的怪物名：保留现有 LLM 填值 + 保守默认作最终兜底。

### B5. 自动遇遇动态化
- `graph.py:1371-1374` 硬编码哥布林 → 按**角色等级**（查 CR 段，参照 `loot.cr_to_loot_tier`）+ **地形**（`terrain_params`）从 `MONSTERS` 选合适怪物。
- 数量沿用 `engine_dice.roll_die(2)` 决定 1-2，或按 CR 调整。
- 叙事文本模板化（不写死"哥布林从暗处窜出"）。

---

## 5. 阶段 C：信息注入 Director（复用现成）

### C1. 记忆注入
- 复用 `narrate`（`graph.py:901-934`）的四层检索，搬到 `director.classify_intent`，拼进 user 消息开头：
  - 工作记忆：`store.get_recent_logs(camp_id, n=6)`
  - 中期记忆：`store.get_summary(camp_id)`
  - 长期记忆：`retrieve_memories(camp_id, query, top_k=20)`（`memory.py:231`）
  - 前情提要：`get_recap(camp_id)`（`memory.py:497`）
- 不改 `llm.chat(system, user, temperature)` 签名，context 拼进 user 段。
- 截断按 narrate 惯例（summary 500 字等），控制 token。

### C2. 结构化当前态注入
- 注入角色卡摘要：`name/race/char_class/level/属性 mod/equipped_weapon/spell_slots/known_spells`。
- 注入场景摘要：`location/environment(地形)/npcs(name+attitude)/situation`。
- 注入战斗状态：`combat.active/round/current_combatant`。
- 目的：让 LLM 有依据填 `weapon/terrain/npc_name` 等，而非瞎猜。

---

## 6. 阶段 D：解析失败重试

### D1. 验证网关 structured output（✓ 已验证：支持）
- 脚本：`aidm/scripts/verify_structured_output.py`（`python aidm/scripts/verify_structured_output.py`）。
- 实测（2026-07）：senseaudio 网关 + deepseek-v4-flash **支持** `with_structured_output`，
  返回了结构化 `Intent(action_type='attack', weapon=...)`。
- **决策：暂不切到 structured output 作主路径**。理由：function-calling 倾向给字段塞冗余
  描述（实测 weapon="长剑 (longsword, 1d8...)"），会破坏 B1/B2 的数据表查找
  （equipment.WEAPONS / spells / monsters 按精确名匹配）。当前 chat() 路径的调优 prompt
  产出干净字段名，且 B1/B2 已有数据表回退。待 B1/B2 查找层加"未命中→回退 equipped_weapon"
  兜底后再切（见第 10 节后续项）。

### D2. 解析失败重试（✓ 已实现：chat() + 重试）
- `director.classify_intent` 现在：`_extract_json(llm.chat(...))` 失败（返回空 dict）→ 重试 ≤3 次，
  每次把"只输出纯JSON，不要markdown/多余文字"反馈进 prompt。
- **只针对解析失败（JSON 格式炸），不针对信息缺失**（后者靠 C 的上下文注入解决）。
- `temperature=0.1` 下重试收益递减，主要救格式；正常路径仍 1 次调用。

---

## 7. 影响面清单（精确到文件:行）

### equipped_weapon
| 文件:行 | 改动 |
|---|---|
| `stats/models.py:43` Character | 加 `equipped_weapon: str = ""` |
| `store.py:29-61` _migrate | 自动补列，无需改 |
| `api/main.py:113` POST /character | 设默认武器（按职业映射） |
| `api/main.py:390` POST /join | 同上 |
| `api/main.py:774` POST /room/join | 同上 |
| `api/main.py:137-143` GET /character | 响应加 equipped_weapon |
| `api/main.py:232` 区块 | 新增 POST /character/{cid}/equip-weapon |
| `brain/graph.py:268` | 武器三级回退 |
| `agents/combat_engine.py:59,274` | 武器三级回退（双写） |
| `engine/combat.py` Combatant | **不改**（ch 即 Character，直接读） |
| `ui/app/lib/types.ts` | 可选加字段（UI 支持） |

### monsters.py
| 文件:行 | 改动 |
|---|---|
| `data/monsters.py` | 新建（Monster+MONSTERS+get_monster+to_combatant_dict） |
| `brain/graph.py:846-879` _resolve_start_combat | 调 get_monster 回填 |
| `brain/graph.py:1371-1374` 自动遇遇 | 动态选怪 |
| `api/main.py:360-371` /monster/{name} | get_monster 结构化回退 + RAG 兜底 |
| `brain/adventure_builder.py:758-768` | cr_list 可改由 get_monster(name).cr 取 |
| `engine/combat.py` Combatant | **不改**（字段已够，cr 不进战斗状态机） |
| `agents/enemy_ai.py:50` | 后续接（当前未被 graph 自动战斗调用） |

---

## 8. 风险与对策

| 风险 | 对策 |
|---|---|
| graph.py / combat_engine.py `_resolve_attack` 重复实现，易漏改 | B1/B2 双写；或抽公共函数 `_pick_weapon(ch, it)` 复用 |
| D2 重试在低温下收益递减 | 只救解析失败，不救信息缺失；max 3 次 |
| C 注入增 prompt 长度 | 按 narrate 惯例截断；记忆 top-k 限制 |
| equipped_weapon 默认值按职业映射是简化 | 靠 equip-weapon 端点 + 工作记忆兜；高等级角色可手动装 |
| monsters.py 数值需对齐 5E SRD | 标注数据出处；先用低 CR 怪铺底 |
| 徒手打击 KeyError 兜底成 1d8挥砍 | A4 特判，不落错误兜底 |

---

## 9. 验证计划

- **A1**：建库后 `PRAGMA table_info(character)` 含 equipped_weapon；老角色行值为 ''。
- **A2**：`POST /character` 建战士→equipped_weapon="长剑"；`POST /equip-weapon` 能改；`GET /character/{cid}` 返回含字段。
- **A3**：`get_monster("哥布林")` 返回非 None，`to_combatant_dict()` 含全部期望键。
- **B1**：玩家输入"我攻击"（未提武器）+ 角色装备长剑→用长剑；无装备→徒手(1+str)。
- **B2**：施火球术但 LLM 不给 spell_dice→用 Spell.damage_dice="8d6"；未知法术名→返回 error。
- **B4**：开战 enemy name="兽人"→Combatant hp 来自 monsters.py 而非默认 7。
- **B5**：自动遇遇在等级1森林→出低 CR 怪；非永远哥布林。
- **C**：Director prompt 含记忆/角色卡/场景段落；classify 结果 weapon 与角色卡一致。
- **D**：故意构造坏 JSON→触发重试→恢复。

---

## 10. 不在本次范围

- 激活 `Character.known_spells_json` 死字段（加 property/setter + char_create 写入，让施法校验"角色是否真会这法术"）——可作后续。
- `agents/enemy_ai.decide_action` 接入 Monster.abilities（当前 graph 自动战斗走确定性 `_run_monster_turn`，未用 LLM 战术）——后续接。
- 前端 UI 装备武器面板——后端就绪后再做。
