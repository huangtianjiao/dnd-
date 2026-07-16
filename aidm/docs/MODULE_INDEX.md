# MODULE_INDEX — brain / agents / knowledge 模块索引

> 对应源码：`src/aidm/brain/`（19 模块）、`src/aidm/agents/`（6 Agent）、`src/aidm/knowledge/`（RAG 知识层）。
> 每个模块列出主要类与入口函数签名 + 一句话功能。仅列顶层 `class` 与 `def`（`_self_test` 省略）。

## 1. brain/ — 编排与业务模块（19 个）

### state.py
`GameState(TypedDict)` — 贯穿图节点的状态对象（字段详见 docs/PIPELINE.md §1）。

### llm.py
LLM 客户端。
- `get_llm(temperature=0.3, streaming=False, **kwargs)` — langchain_openai ChatOpenAI，model/api_key/base_url 来自 config
- `chat(system, user, temperature=0.3) -> str` — 便捷一次性问答

### graph.py
LangGraph 编排（详见 docs/PIPELINE.md）。本地节点：`confirm`、`resolve`、`narrate`、`apply_node`；`build_graph()`、`run()`、`run_turn()`。

### memory.py
三层记忆系统（详见 docs/PIPELINE.md §11）。`extract_observations` / `store_memory` / `retrieve_memories` / `compress_rolling_summary` / `process_turn_memories` / `generate_recap` / `get_recap` / `cleanup_memories`。

### world.py
叙事/世界层。
- `open_campaign(setting, tone, campaign_id, character_id) -> dict` — DM 框定场景，跑团开场
- `scene_context(campaign_id) -> str` — 场景上下文（地点/时间/氛围/环境/在场NPC/可做之事）
- `get_scene(campaign_id) -> dict` — 取场景

### exploration.py
Phase E 探索流程 — 旅行步调/地形/觅食/导航/追踪/躲藏/遭遇（DMG「运作探索」）。
- `TravelPace.get_travel_pace(pace_name)` / `TerrainParams.terrain_params(terrain)`
- `light_obscurement(light_level)` / `effective_obscurement(obscurement, senses)` / `audible_distance(noise_level)` / `outdoor_visibility(weather, vantage)` / `sea_visibility(sky_condition)` / `underwater_encounter_distance(clarity, lighting)`
- `Weather.weather_roll()` / `extended_travel_exhaustion(extra_hours, con_save_total)` / `special_travel_rate(speed, pace, travel_hours=8)` / `apply_good_road(max_pace, good_road)` / `party_pace_slow_check(member_speeds, normal_speed=30)`
- `ForageResult.forage(survival_total, forage_dc, wis_mod)` / `NavigationResult.navigation(survival_total, nav_dc)` / `track_research_time(track_success, area_type)` / `battle_duration(rounds)`
- `PassivePerceptionResult.check_passive_perception(party_members, dc, ...)` / `EncounterCheckResult.random_encounter_check(threshold=18)` / `HideResult.hide_check(...)`
- `Resources` / `ExplorationState` / `TravelDayResult.travel_day(...)` / `DungeonTurnResult.dungeon_turn(...)`

### adventure_builder.py
冒险创建工具 — DMG 第四章「创建冒险」+ 第五章「创作战役」。
- 类：`Hook` / `Background` / `NPC` / `Encounter` / `Ending` / `Adventure`
- `_level_to_tier(level)` / `_roll_table(table, rng)`
- `create_adventure(name, ...)` / `import_players(method="sponsor", ...)` / `set_background(adventure, ...)` / `add_encounter(adventure, ...)` / `add_npc(adventure, ...)` / `end_adventure(adventure, ...)` / `generate_rewards(cr_list, ...)` / `get_xp_budget(party_level, ...)` / `roll_adventure_connection(seed=None)`

### levelup.py
角色升级与成长（Phase I）— 升级五步骤 + DMG 变体。
- `proficiency_bonus(level)` / `get_tier(level)` / `xp_for_level(level)` / `level_from_xp(xp)` / `check_level_up(character)` / `award_xp(party, total_xp)` / `milestone_xp(milestone_type, level=1)` / `training_cost(target_level)` / `session_based_level(sessions_played)`
- `_roll_hit_die(hit_die)` / `_hp_gain_for_level(...)`
- `available_feats(character)` / `select_feat(character, feat_name)` / `level_up(...)` / `level_up_outside_rest(character, hp_gain)`

### rest.py
休息机制 — 短休/长休/打断休息。
- 类：`RestState` / `MockCharacter`(测试用)
- `_get(character, attr, default=0)` / `short_rest(character, hit_dice_to_spend=0, ...)` / `_fail_short(errors)` / `long_rest(character)` / `_fail_long(errors)` / `interrupt_rest(rest_state, cause)` / `recharge_features_on_short_rest(character)` / `recharge_features_on_long_rest(character)`

### loot.py
战利品系统 — DMG 第七章 宝藏。
- `cr_to_loot_tier(cr)`
- `LootPool.generate_loot(cr, count_enemies=1, include_magic_items=True, seed=None, ...)`
- `LootDistribution.distribute_loot(pool, players, method="needPriority", needs=None, dm_assignments=None, seed=None)` / `distribute_gold(total_gold, players, method="equal", contributions=None)`
- `attune_magic_item(character_id, item_name)` / `break_attunement(character_id, item_name)` / `identify_magic_item(character_id, item_name)`

### plane_travel.py
位面旅行系统 — DMG 第六章 宇宙学。
- 类：`TRAVEL_METHODS(Enum)` / `TravelResult` / `HazardResult`
- `travel_to_plane(...)` / `_apply_portal_travel/_apply_spell_travel/_apply_gate_travel/_apply_vortex_travel/_apply_color_pool_travel(...)` / `apply_plane_hazards(...)` / `check_portal_accessibility(portal)` / `get_travel_methods()` / `list_available_destinations(origin_plane)`

### campaign_manager.py
战役管理工具 — DMG 第五章「创作战役」。
- 类：`LogEntry` / `Session` / `Milestone` / `Campaign`
- `create_campaign(name, ...)` / `add_session(campaign, ...)` / `log_campaign_event(campaign, ...)` / `get_campaign_timeline(campaign)` / `end_campaign(campaign, ...)` / `get_fantasy_style(style_key)` / `list_fantasy_styles()` / `list_dnd_settings()`

### stronghold.py
据点管理系统 — DMG 第八章 据点。
- 类：`FacilityInstance` / `BasicFacilityInstance` / `Defender` / `Stronghold` / `Result` / `TurnResult` / `EventResult`
- `create_stronghold(...)` / `add_special_facility(...)` / `build_facility(...)` / `run_stronghold_turn(...)` / `trigger_event(...)` / `recruit_defenders(...)` / `lose_stronghold(...)` / `get_stronghold_status(stronghold)` / `list_available_facilities(stronghold)`

### social.py
社交流程 — DM 扮演 NPC / 态度转换。
- 类：`NPC` / `SocialState`
- `check_social_dc(npc_attitude)` — 友好-5/冷漠0/敌对+5（R-CON-012）
- `update_attitude(npc, success_count, failure_count)`
- `social_interaction(party, npc, player_input, ...)`

### char_create.py
角色创建逻辑 — 五步车卡法。
- `ability_modifier(score)` / `proficiency_bonus(level)` / `hit_points_level1(hit_die, con_mod)` / `unarmored_ac(dex_mod)` / `initiative(dex_mod)` / `passive_perception(wis_mod, proficient, pb)` / `spell_save_dc(casting_mod, pb)` / `spell_attack_bonus(casting_mod, pb)` / `roll_4d6_drop_lowest()` / `roll_ability_scores()` / `validate_point_buy(scores)` / `point_buy_cost(scores)`
- 类：`CharacterSheet`
- `step1_choose_class(sheet, class_name)` / `step2_choose_origin(...)` / `step3_assign_ability_scores(...)` / `step4_choose_alignment(sheet, alignment)` / `step5_enrich_details(...)` / `create_character(...)`

### room.py
房间管理系统 — 多人同桌房间生命周期。
- 类：`Room`(`_gen_room_id`) / `RoomManager` / `PlayerSession` / `CampaignRoom` / `_FakeWS`
> 注：`room.py` 的 `PlayerSession`/`CampaignRoom` 与 `api/ws.py` 中同名类是**两套实现**。

### session0.py
Session 0 配置逻辑 — 游戏前准备（基调/严肃度/边界/规则版本/升级方式/死亡处理）。
- 类：`Session0Config`
- `default_session0()` / `validate_session0(config)` / `is_valid_config(config)`

### loot_distribution.py
多人战利品分配系统 — 按 CR 生成池再按策略分发。
- 类：`Rarity(str, Enum)` / `DistributionMode(str, Enum)` / `LootItem` / `LootPool` / `DistributionRecord`
- `_cr_bucket(cr)` / `generate_loot_pool(campaign_id, monster_crs, ...)` / `distribute_gold(pool, player_names)` / `distribute_items_need_first(...)` / `distribute_items_round_robin(...)` / `distribute_items_roll_off(...)` / `distribute_items_dm_assign(...)` / `distribute_loot(...)`

### image_gen.py
动态图片生成 — 叙事过程中插图。
- `generate_scene_description(narration) -> str` — 从叙事生成场景描述
- `generate_scene_image(narration, ...)` — 生成场景图（API 待接）
- `render_battlefield_ascii(width=20, height=15, ...)` — ASCII 战场渲染

---

## 2. agents/ — 多智能体（6 个，渐进迁移中）

> 现状：`agents/` 包已建，但 `graph.py` 的 `build_graph()` 仅注册了 `director.classify_intent` 与 `rule_judge` 的 retrieve/verify/retrieve_retry。narrator/combat_engine/world_manager/enemy_ai 尚未替换 `graph.py` 本地节点（渐进迁移）。

| Agent | 文件 | 职责 | 状态 |
|---|---|---|---|
| Director | `agents/director.py` | LLM 意图分类 → 结构化 intent；导出 `classify_intent`、`route_action`(未挂载) | ✅ 已接入 graph |
| Rule Judge | `agents/rule_judge.py` | hybrid 检索 + 关键词预检；导出 `retrieve`/`verify`/`retrieve_retry` | ✅ 已接入 graph |
| Narrator | `agents/narrator.py` | LLM 叙事（拟替换 graph.narrate） | 🟡 待接入 |
| Combat Engine | `agents/combat_engine.py` | 战斗分派（拟替换 graph.resolve 战斗分支） | 🟡 待接入 |
| World Manager | `agents/world_manager.py` | 世界/场景管理（拟替换 world.py 部分） | 🟡 待接入 |
| Enemy AI | `agents/enemy_ai.py` | 怪物自主战术决策（`decide_action`，HP<25% 逃跑，temperature 0.4） | 🟡 待接入 |

---

## 3. knowledge/ — RAG 知识层

### 索引构建流程
1. **数据源解析**（`parse_datajs.py`）：解析 WinCHM 导出的 `data.js`（格式 `var contents = new Array(...)`），用 JS 字符串分词器（处理转义）提取约 **6238 条**规则三元组 → `RuleEntry`(body/tag/path)。`_tokenize_strings()` 比 regex 稳健。
2. **向量化**（`embedding.py`）：本地 `sentence-transformers`（默认 `bge-small-zh-v1.5`，512 维，懒加载，首次从 hf-mirror.com 下载）。`embed_texts(texts, batch_size=64)` / `embed_query(text)` / `dim()`。可选独立 HTTP 嵌入服务（OpenAI 兼容 `/v1/embeddings`）。
3. **写入 Qdrant**（`indexer.py`）：本地文件模式（`path=aidm/data/rules.db`，免 docker）。
   - `build_index(batch_size=64, limit=None, rebuild=True)` — data.js → dnd_rules 集合
   - `index_text_files(directory, collection, ...)` — rules_text 141 页 → dnd_rule_text 集合
   - `index_chunks(items, collection, ...)` — RULE_SPEC 400 条结构化规则点 → dnd_rule_spec 集合
   - `reset_collection()` — 按 embedding_dim 删建集合(COSINE)

### 检索流程（BM25 + 向量 + RRF 融合）
- **向量检索**（`indexer.py`）：`search(query, limit=5, tag_filter)` / `search_rules(query, limit=5)` / `search_spec(query, limit=5)`
- **BM25 检索**（`hybrid.py`）：中文字符级 + ASCII 词级分词（`_tokenize`）。`BM25` 类(k1=1.5, b=0.75) 在 RULE_SPEC 语料精确命中关键词。
- **RRF 融合**（`hybrid.py` `search_spec_hybrid(query, limit=5, dense_n=20, bm25_n=20, rrf_k=60)`）：向量 top-N + BM25 top-N → 倒数排名融合 `score += 1/(rrf_k+rank+1)` → top-k。
- **检索封装**（`retriever.py`）：`query_rules(query, limit=5, tag_filter)` / `format_for_llm(results, body_limit=600)` / `query_formatted(query, limit=5)`
- **判定校验**（`verifier.py`）："RAG 校验而非参考"原则。
  - `gather_evidence(action_desc, limit=5)` — hybrid 检索证据
  - `keyword_preflight(proposed_check_type, proposed_dc, results)` — 关键词粗筛
  - `verify(action_desc, *, proposed_check_type=None, proposed_dc=None, limit=8)` — 检索+预检 → `Verification`(ok/evidence/issues/digest)
- **别名富化**（`aliases.py`）：`ALIASES` dict (rule_id → 玩家常用同义词串)，注入 chunk body 前部让玩家词稳定命中规则。

### 评测
`eval_retrieval.py` — 15 条评测集，recall@3 = 100%。
