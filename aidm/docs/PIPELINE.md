# PIPELINE — 判定链流程与记忆数据流

> 本文描述 AIDM 核心编排：LangGraph StateGraph 判定链的节点、边、条件路由，以及三层记忆如何注入叙事节点。
> 对应源码：`src/aidm/brain/graph.py`、`brain/memory.py`、`brain/state.py`、`agents/director.py`、`agents/rule_judge.py`。

## 概览

一次玩家行动（`/chat` 或 WebSocket `action`）的完整流转：

```
玩家输入 → classify(意图) → retrieve(检索规则) → verify(校验)
  → [retrieve_retry / confirm(HITL) / resolve]
  → resolve(硬性骰子) → narrate(LLM叙事+记忆注入) → apply(持久化+记忆处理) → END
```

**架构原则**（`brain/state.py` 开篇定义）：LLM 只在 classify（意图理解）与 narrate（叙事）两端活动，中间 retrieve→verify→resolve（骰子）全代码硬性判定，LLM 不可绕过。这保证规则一致性与可审计性。

## 1. 状态对象 GameState

`GameState(TypedDict)`（`brain/state.py`）贯穿所有节点：

| 字段 | 类型 | 产生节点 | 含义 |
|---|---|---|---|
| `player_input` | str | 输入 | 玩家原始输入 |
| `campaign_id` / `character_id` | int | 输入 | 战役/角色 ID |
| `hitl` | bool | 输入 | 是否启用 human-in-the-loop |
| `intent` | dict | classify | 结构化意图（action_type 等） |
| `evidence` | list | retrieve/retrieve_retry | 检索到的规则点 |
| `verification` | dict | verify | `{ok, issues}` |
| `confirmed` | bool | confirm | DM 确认结果 |
| `dice` | dict | resolve | 硬性骰子结果 |
| `narration` | str | narrate | DM 叙事 |
| `state_changes` | list | narrate | 结构化状态变更 |
| `combat` | dict | resolve/_load_combat | 战斗状态 |
| `error` / `summary` | str | — | 错误/rolling summary |

## 2. 节点清单与注册映射

`build_graph()`（`graph.py`）注册 8 个节点。**注意：前 4 个节点的实现不在 `graph.py` 本地，而在 `agents/` 包**（`graph.py` 里的 classify/retrieve/verify/retrieve_retry 是遗留参考实现，未被注册）：

| 图节点 | 实现来源 | 入口函数 | 职责 |
|---|---|---|---|
| `classify` | `agents/director.py` | `classify_intent` | LLM 意图分类 → 结构化 intent |
| `retrieve` | `agents/rule_judge.py` | `retrieve` | hybrid 检索规则点 |
| `verify` | `agents/rule_judge.py` | `verify` | 关键词预检参数合规性 |
| `retrieve_retry` | `agents/rule_judge.py` | `retrieve_retry` | 校验驳回后重检索 |
| `confirm` | `graph.py` 本地 | `confirm` | HITL 关键判定暂停 |
| `resolve` | `graph.py` 本地 | `resolve` | 纯代码硬性骰子分派 |
| `narrate` | `graph.py` 本地 | `narrate` | LLM 叙事 + 三层记忆注入 |
| `apply` | `graph.py` 本地 | `apply_node` | 持久化 + 战斗推进 + 记忆处理 |

## 3. 边与条件路由（完整拓扑）

```
ENTRY → classify ──→ retrieve ──→ verify ──┐
                                             │ _after_verify
              ┌──────────────────────────────┴──┐
              ▼              ▼                    ▼
       retrieve_retry    confirm             resolve
              │              │  _after_confirm
              │  (驳回→retry) │
              └──────────────┘
              (retry→resolve 终态，无循环)
                                    narrate ◄── resolve
                                       │
                                       ▼
                                     apply
                                       │
                                       ▼
                                      END
```

边定义（`graph.py:591-601`）：

- `set_entry_point("classify")`
- `classify → retrieve`（无条件直连）
- `retrieve → verify`（无条件直连）
- `verify → [retrieve_retry | confirm | resolve]`（条件路由 `_after_verify`）
- `retrieve_retry → resolve`（重检索后直通终态，**避免死循环**）
- `confirm → [resolve | retrieve_retry]`（条件路由 `_after_confirm`）
- `resolve → narrate`
- `narrate → apply`
- `apply → END`

> 注：`agents/director.py` 还导出了 `route_action` 条件路由，但 `build_graph()` **未挂载**——classify 后是无条件直连 retrieve。

## 4. 三个条件路由函数

**`_after_verify(state)`**（`graph.py:546`）：
- `action_type ∈ {other, end_combat}` → `"resolve"`（无判定，跳过 HITL）
- `state.hitl == True` → `"confirm"`（HITL 开则一律让 DM 确认，可靠触发 interrupt）
- `verification.ok == False` → `"retrieve_retry"`
- 否则 → `"resolve"`

**`_after_retry(state)`**（`graph.py:559`）：无条件返回 `"resolve"`（终态，避免死循环）。

**`_after_confirm(state)`**（`graph.py:564`）：`confirmed == True` → `"resolve"`；否则 → `"retrieve_retry"`（驳回重检索后必到 resolve，无循环）。

## 5. Checkpointer 与 HITL 机制

- **Checkpointer**：`g.compile(checkpointer=MemorySaver())`。`MemorySaver` 来自 `langgraph.checkpoint.memory`，**内存级**（进程重启丢失）。
- **HITL interrupt**：`confirm` 节点用 `from langgraph.types import interrupt`。`hitl=True` 时调 `interrupt({question, intent, verification, evidence})` 暂停图执行，等待 DM 恢复。恢复值 `answer` 解析为 y/n（`graph.py:142`：`str(answer).lower() in ("y","yes","true","1","通过")`）。`hitl=False` 时直接返回 `confirmed=True` 直通。
- **thread_id**：每轮调用用 `config={"configurable": {"thread_id": ...}}` 标识会话线程，HITL 中断后靠同 thread_id 恢复。

两个运行入口：
- `run(player_input, campaign_id, character_id, thread_id, hitl)` — 单次 `invoke`，interrupt 时返回带 `__interrupt__` 的状态（API 用）
- `run_turn(..., responder)` — HITL 感知循环版：`invoke` 后若 `r.get("__interrupt__")`，循环调 `responder(q)→ans`，再用 `Command(resume=ans)` 恢复，最多重试 5 次（`guard < 5`）

## 6. classify — 意图分类（Director Agent）

- **输入**：`player_input`
- **输出**：`{"intent": {...}, "error": ""}`
- **实现**：LLM 用 `_DIRECTOR_PROMPT`（`director.py:36`）把玩家输入分类为结构化 JSON。temperature=0.1。解析失败 fallback `action_type="other"`。

**action_type 枚举（11 种）**：`attack | cast | ability_check | explore | start_combat | end_combat | rest | social | levelup | travel | other`

| action_type | 专有字段 |
|---|---|
| attack | `weapon` |
| cast | `spell_name/spell_level/spell_dice/damage_type/spell_attack/save_ability/target_save_bonus/casting_ability` |
| ability_check / explore | `skill/dc/proficient` |
| start_combat | `enemies[{name,dex_mod,side}]` |

通用字段：`target_name, target_ac, ability, retrieval_query`（用规则原词构造的检索串）。

## 7. retrieve / verify / retrieve_retry — 规则检索（Rule Judge）

**retrieve**：输入 `intent.retrieval_query`（fallback `player_input`），调 `hybrid.search_spec_hybrid(q, limit=6)` 混合检索规则点，输出 `{"evidence": [...]}`。

**verify**：关键词预检判定参数合规性。`action_type ∈ {other, start_combat, end_combat}` 直接 `ok=True` 放行；其余调 `verifier.verify(query, proposed_check_type=intent.ability, proposed_dc=target_ac or dc, limit=6)`。输出 `{"verification": {"ok": bool, "issues": [...]}}`。语义级校验留给 confirm/LLM。

**retrieve_retry**：校验驳回后重检索，用 issues 补关键词：`base + " " + " ".join(issues) + " 检定方式 DC来源 豁免"`，截断到 80 字符，limit=6。

## 8. resolve — 8 分支硬性骰子分派

resolve 节点（纯代码）按 `action_type` 分派到子解析器（LLM 不参与，全部用 `engine.check/damage/combat`）。`character_id` 不存在且非 start/end_combat → 返回 `error="角色卡不存在"`。

| action_type | 子函数 | 引擎调用 | 规则点 |
|---|---|---|---|
| attack | `_resolve_attack` | `check.attack_roll` + `damage.roll_damage`（重击骰翻倍） | R-CMB-017/022/023, R-DMG-001/CMB-029 |
| cast | `_resolve_cast` | `check.calc_save_dc` + `attack_roll`/`saving_throw` + `damage.roll_damage` + 半伤管线 | R-DM-002, R-SPL-021/022, R-CHK-011/014 |
| ability_check / explore | `_resolve_ability_check` | `check.ability_check` vs DC | R-CHK-010 |
| start_combat | `_resolve_start_combat` | `combat.roll_initiative` + `store.save_combat` | R-CMB-002 |
| end_combat | （内联） | `combat.active=False` | — |
| rest | `_resolve_rest` | `rest.short_rest` / `long_rest` | R-GLS-014/015 |
| social | `_resolve_social` | `social.NPC` + `check_social_dc` + `ability_check` + `update_attitude` | R-CON-012, R-DM-047 |
| levelup | `_resolve_levelup` | `levelup.level_up` + `get_tier` | R-DM-041~045 |
| travel | `_resolve_travel` | `exploration.TRAVEL_PACES` + `navigation` + `random_encounter_check` + `check_passive_perception` | R-DM-026~040 |
| other | （内联） | `dice={}` 仅叙事 | — |

**cast 关键逻辑**：施法属性优先用 `CLASS_CAST_ABILITY` 字典（法师=int/术士=cha/...）确定性查表，优先于 LLM 猜测（`graph.py:172`）。豁免成功走 `dice.round_down(full/2)` 半伤（R-CHK-014）。

## 9. narrate — LLM 叙事 + 三层记忆注入

narrate 节点据硬性掷骰结果（已代码算出，不可改）+ 规则 + 当前场景，第二人称简洁叙述（2-4 句），并产出 `state_changes` + `scene_update` + 3 个 `action_options`。temperature=0.4。

注入内容：

| 层 | 来源 | 注入方式 | 代码位置 |
|---|---|---|---|
| ① 工作记忆 | `store.get_recent_logs(camp_id, n=6)` | 最近 6 回合对话原文（时间正序） | `graph.py:397` |
| ② 中期记忆 | `store.get_summary(camp_id)` | `Campaign.rolling_summary`，截取前 500 字 | `graph.py:405` |
| ②b 前情提要 | `memory.get_recap(camp_id)` | 跨 Session 浓缩摘要，注入 prompt 开头 | `graph.py:411` |
| ③ 长期记忆 | `memory.retrieve_memories(camp_id, query, top_k=20)` | 跨 Session 语义检索 top-5（重要性加权+时间衰减），失败不阻断叙事 | `graph.py:419` |
| 场景 | `world.scene_context(camp_id)` | 地点/时间/氛围/环境/在场NPC/可做之事/场景叙事 | `graph.py` narrate 内 |

输出字段：
- `narration` — DM 叙事文本
- `state_changes` — 结构化状态变更（HP/法术位/条件等）
- `scene_update` — 场景推进（situation 更新）
- `action_options` — 3 个可选行动

## 10. apply — 持久化 + 战斗推进 + 记忆处理

`apply_node`（副作用节点，返回空 dict）6 步（`graph.py:504-537`）：

1. 应用 `state_changes` 中玩家 HP 变更（`damage.apply_damage_to_hp` / `apply_healing`）
2. 施法消耗法术位（`dice.kind=="cast"` 时 `spell_slots_json` 对应环位 -1）R-SPL-002
3. `store.save_character(ch)` 持久化角色
4. 战斗轮次推进（`combat.active` 时 `combat.advance_turn` + `store.save_combat`）R-CMB-001/004
5. `store.append_log` 持久化日志（rolling_summary 不再逐回合追加）
6. 场景推进：`store.get_scene` → `sc.situation = scene_update` → `store.save_scene`
7. **记忆处理**：调 `process_turn_memories(campaign_id, player_input, narration, intent, turn)`（用最新 Log.id 近似回合序号），包在 try/except 中——**记忆处理失败不阻断主流程**

## 11. 三层记忆系统（brain/memory.py）

参考 Generative Agents（Park et al., 2023）。三分量评分：

```
final_score = α·recency + β·relevance + γ·importance
  recency    = 0.99 ** hours_since_creation
  relevance  = cosine_similarity(query, memory)   [Qdrant score 归一化 0-1]
  importance = stored_importance / 10.0
```

权重（`memory.py:52-56`）：`RECENCY_WEIGHT=0.5`，`RELEVANCE_WEIGHT=3.0`，`IMPORTANCE_WEIGHT=2.0`，`DECAY_RATE_PER_HOUR=0.99`，`COMPRESS_EVERY_N_TURNS=10`，`MAX_MEMORIES=500`。

存储后端：Qdrant `dnd_memories`（长期）+ SQLite Log 表（工作记忆数据源）+ `Campaign.rolling_summary`（中期摘要）。

| 函数 | 签名 | 职责 |
|---|---|---|
| `extract_observations` | `(player_input, narration, intent) -> list[dict]` | LLM 提取 1-3 条观察，每条含 event/importance(1-10)/entities/type。temperature=0.1 |
| `store_memory` | `(campaign_id, observation, turn, obs_index=0) -> Optional[int]` | bge 嵌入后存入 Qdrant `dnd_memories`，point_id=`turn*1000+obs_index` 防碰撞 |
| `retrieve_memories` | `(campaign_id, query, top_k=20) -> list[dict]` | 语义检索 top-K → 三分量评分 → 加权求和 → 取 top-5 |
| `compress_rolling_summary` | `(campaign_id, recent_logs) -> str` | LLM 把 N 回合对话压缩成 3-5 句摘要。temperature=0.2 |
| `process_turn_memories` | `(campaign_id, player_input, narration, intent, turn) -> dict` | **完整管线**（apply_node 结尾调用）：extract→store→每10回合 compress→cleanup |
| `generate_recap` | `(campaign_id) -> str` | Session 结束生成 500-1000 字"前情提要"，存入 rolling_summary 的 `[前情提要]...[/前情提要]` 块 |
| `get_recap` | `(campaign_id) -> str` | 从 rolling_summary 提取前情提要块，供新 Session narrate 注入 |
| `cleanup_memories` | `(campaign_id) -> int` | 超 MAX_MEMORIES 时按 importance 升序删除超额记忆 |

## 12. 端到端 /chat 一次调用（9 步）

1. **入口**：`graph.run(player_input, campaign_id, character_id, thread_id, hitl)` 构造初始 GameState（含 `_load_combat` 载入战斗），`get_graph().invoke(init, config=cfg)`
2. **classify**（Director LLM）→ intent 含 action_type
3. **retrieve**（Rule Judge hybrid）→ evidence 规则点
4. **verify**（Rule Judge 关键词预检）→ verification{ok, issues}
5. **条件路由 `_after_verify`**：other/end_combat→resolve；hitl→confirm（interrupt 暂停）；verify 失败→retrieve_retry→resolve
6. **resolve**（纯代码 8 分支硬性骰子）→ dice + combat
7. **narrate**（LLM）→ 注入三层记忆(工作6回合/rolling_summary前500字/长期top-5 + 前情提要) + `world.scene_context`，产出 narration + state_changes + scene_update + action_options
8. **apply_node**（持久化）→ HP/法术位/角色存档 + 战斗轮次推进 + append_log + 场景 situation 更新 + `process_turn_memories`
9. **END**。API 返回 narration/intent/dice/state_changes/action_options/combat；HITL 中断则返回 `interrupted=True` 供 `/chat/resume` 恢复
