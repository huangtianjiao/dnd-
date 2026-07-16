# DATA_MODELS — 数据表结构与规则数据统计

> 对应源码：`src/aidm/stats/models.py`（SQLModel 表定义）、`stats/store.py`（CRUD）、`stats/npc.py`（NPC 持久化）、`stats/checkpoint.py`（存档检查点）、`src/aidm/data/`（规则数据）。
> 存储后端：SQLite（`aidm/data/saves/save.db`）+ Qdrant 本地文件（`aidm/data/rules.db/`，记忆集合 `dnd_memories`）。

## 1. 表关系总览

所有表通过 `campaign_id` 外键关联到 `Campaign.id`。

```
Campaign (1) ──┬── (N) Character
               ├── (N) Scene
               ├── (1) CombatState
               └── (N) Log

+ stats/npc.py:    NPCProfile / NPCMemory (按 campaign_id)
+ stats/checkpoint.py: Checkpoint (JSON 快照，按 campaign_id)
+ brain/memory.py: Qdrant dnd_memories (按 campaign_id payload 过滤)
```

## 2. Character — 角色卡

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Optional[int] (PK) | 主键 |
| campaign_id | Optional[int] (FK→campaign.id) | 所属战役 |
| name | str | 姓名 |
| race / char_class / subclass / level | str/str/str/int | 种族/职业/子职/等级 |
| abilities_json | str (JSON) | 六项属性 {str,dex,con,int,wis,cha} |
| spell_slots_json | str (JSON) | 法术位 {环阶:剩余} |
| known_spells_json | str (JSON) | 已知法术列表 |
| inventory_json | str (JSON) | 物品栏魔法物品名列表 |
| conditions_json | str (JSON) | 状态集合 |
| attuned_items_json | str (JSON) | 已同调物品(最多3) |
| feats_json | str (JSON) | 已选专长列表 |
| hp_current / hp_max / temp_hp | int | 当前/最大/临时 HP |
| ac / speed / exhaustion | int | AC/速度/力竭等级 |
| death_successes / death_failures | int | 死亡豁免成功/失败计数 |
| stable / dead | bool | 稳定/死亡 |

桥接方法：`abilities`/`set_abilities`、`conditions_list`/`set_conditions`、`spell_slots`/`set_spell_slots`、`attuned_items`/`set_attuned_items`(强制上限3)、`inventory`/`set_inventory`/`add_to_inventory`、`feats`/`set_feats`、`ability_score(ab)`、`ability_mod(ab)`、`prof()`、`to_condition_state()`/`apply_condition_state()`、`to_death_tracker()`/`apply_death_tracker()`。常量 `MAX_ATTUNED_ITEMS=3`。

> **遗留**：Character 表缺 `skill_prof_json`/`save_prof_json` 持久化（熟练与否现由 LLM classify 每轮判，重载/多角色场景无法回溯）。见 docs/ISSUES.md。

## 3. Campaign — 战役

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Optional[int] (PK) | 主键 |
| name | str | 战役名 |
| setting | str | 玩家输入的世界设定提示词 |
| tone | str | 基调(黑暗/英雄/恐怖...) |
| world_background | str | AI 生成的完整背景故事(长文) |
| rolling_summary | str | 剧情压缩摘要(防上下文失忆)，含 `[前情提要]...[/前情提要]` 块 |
| world_flags_json | str (JSON) | 世界状态标记(NPC关系/阵营/任务) |

桥接：`world_flags`/`set_world_flags`。

## 4. Scene — 当前场景

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Optional[int] (PK) | 主键 |
| campaign_id | Optional[int] (FK) | 所属战役 |
| location | str | 地点 |
| npcs_json | str (JSON) | 在场NPC [{name,attitude,role}] |
| environment / time / atmosphere | str | 环境/时间/氛围(多感官) |
| situation | str | 当前场景摘要(短) |
| story_log | str | 场景内叙事日志(长) |
| exits_json | str (JSON) | 可感知选项/出路 |
| notes | str | DM 私密备注(秘密/发现) |

桥接：`npcs`/`set_npcs`、`exits`/`set_exits`。

## 5. CombatState — 战斗状态(持久化)

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Optional[int] (PK) | 主键 |
| campaign_id | Optional[int] (FK) | 所属战役 |
| initiative_order_json | str (JSON) | 先政顺序 [{cid,name,initiative,side}] |
| participants_json | str (JSON) | 参战者快照 |
| round / current_index | int | 轮次/当前索引 |
| active | bool | 是否激活 |

桥接：`initiative_order`/`set_initiative_order`。

## 6. Log — 跑团日志

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Optional[int] (PK) | 主键 |
| campaign_id | Optional[int] (FK) | 所属战役 |
| ts | str | 时间戳 |
| player_input / dm_output | str | 玩家输入/AI 回复 |
| dice_rolls_json | str (JSON) | 骰子记录 |
| state_changes_json | str (JSON) | 状态变更 |
| rag_refs_json | str (JSON) | RAG 引用 |

## 7. NPC 持久化（stats/npc.py）

- `NPCProfile` — NPC 人格档案：性格/态度/关系/信任度等
- `NPCMemory` — NPC 记忆流：对玩家的交互记录与关系演化
- CRUD + 记忆流查询 + 关系演化追踪（按 campaign_id）

## 8. Checkpoint（stats/checkpoint.py）

- 存档检查点：`create` / `list` / `restore` / `delete`
- JSON 快照格式（游戏状态序列化）
- 按 campaign_id 组织，支持回退到任意检查点

## 9. store.py — 持久化存储 CRUD

SQLite 路径：`DEFAULT_DB = "sqlite:///D:/game/dnd/aidm/data/saves/save.db"`（绝对路径）。`get_engine` 自动建父目录与表、自动迁移（补缺失列 ALTER TABLE ADD COLUMN）。

| 函数名 | 签名 | 返回 | 功能 |
|---|---|---|---|
| `get_engine` | `(db_path: str = DEFAULT_DB)` | 引擎 | 创建/获取引擎(幂等建表+自动迁移) |
| `session` | `(db_path=DEFAULT_DB)` (contextmanager) | Session | 事务会话上下文(提交/回滚/关闭) |
| `save_character` | `(ch: Character, db_path=DEFAULT_DB) -> Character` | Character | 保存角色卡 |
| `get_character` | `(cid: int, db_path=DEFAULT_DB) -> Optional[Character]` | Character? | 取角色卡 |
| `list_characters` | `(campaign_id=None, db_path=DEFAULT_DB) -> list[Character]` | 列表 | 列出角色(可按战役过滤) |
| `create_campaign` | `(name: str, db_path=DEFAULT_DB) -> Campaign` | Campaign | 创建战役 |
| `save_campaign` | `(c: Campaign, db_path=DEFAULT_DB) -> Campaign` | Campaign | 保存战役 |
| `get_campaign` | `(campaign_id: int, db_path=DEFAULT_DB) -> Optional[Campaign]` | Campaign? | 取战役 |
| `list_campaigns` | `(db_path=DEFAULT_DB) -> list[Campaign]` | 列表 | 列出所有已保存战役 |
| `append_summary` | `(campaign_id, text, db_path=DEFAULT_DB) -> str` | str | 追加剧情摘要到 rolling summary |
| `get_summary` | `(campaign_id, db_path=DEFAULT_DB) -> str` | str | 取 rolling summary |
| `set_campaign_setting` | `(campaign_id, setting, tone="", db_path=DEFAULT_DB) -> Optional[Campaign]` | Campaign? | 设置战役世界背景/基调 |
| `save_scene` | `(scene: Scene, db_path=DEFAULT_DB) -> Scene` | Scene | 保存/更新当前场景 |
| `get_scene` | `(campaign_id, db_path=DEFAULT_DB) -> Optional[Scene]` | Scene? | 取战役当前场景(最新一条) |
| `save_combat` | `(campaign_id, combat: Combat, db_path=DEFAULT_DB) -> CombatState` | CombatState | 把 engine.Combat 序列化为 CombatState 行(覆盖) |
| `load_combat` | `(campaign_id, db_path=DEFAULT_DB) -> Combat` | Combat | 从 CombatState 行重建 engine.Combat |
| `append_log` | `(campaign_id, *, player_input="", dm_output="", dice_rolls=None, state_changes=None, rag_refs=None, db_path=DEFAULT_DB) -> Log` | Log | 追加跑团日志 |
| `get_recent_logs` | `(campaign_id, n=6, db_path=DEFAULT_DB) -> list[Log]` | 列表 | **特殊查询**：取最近 n 条日志(按id倒序后反转→时间正序)，工作记忆数据源 |

内部：`_migrate(engine)`、`_combatant_to_dict(c)`、`_dict_to_combatant(d)`（engine.Combatant ↔ dict 序列化往返）。

## 10. 规则数据统计（src/aidm/data/，9 模块，4838 行）

| 文件 | 数据结构 | 条目数 | public 查询函数 | 规则/出处 |
|---|---|---|---|---|
| `feats.py` (1330行) | `FEATS` dict | **74** | `get_feat`, `list_feats`, `feat_categories` | PHB2024 第五章专长(起源/通用/战斗风格/传奇恩惠) |
| `planes.py` (1055行) | `PLANES` dict | **58** | `get_plane`, `list_planes`, `get_portals`, `search_planes`, `get_plane_count` | DMG 第六章宇宙学 |
| `strongholds.py` (652行) | `FACILITIES`/`BASIC_FACILITIES`/`STRONGHOLD_EVENTS` | **29** 特色 / **6** 基础 / **11** 事件 | `get_facility`, `list_facilities_by_level`, `get_event_by_roll` | DMG 第八章据点 |
| `magic_items.py` (601行) | `MAGIC_ITEMS` dict | **30** | `get_magic_item`, `list_magic_items`, `items_by_rarity`, `items_by_type`, `random_magic_items` | DMG 第七章宝藏 |
| `spells.py` (367行) | `SPELLS` dict | **12** | `get_spell`, `is_cantrip`, `get_casting_ability`, `max_spell_slots` | 法术详述0-3环 |
| `equipment.py` (236行) | `ARMOR` dict / `WEAPONS` | **13** 护甲 / **38** 武器 | `convert_coins`, `get_armor_entry`, `get_weapon_entry`, `compute_ac`, `compute_unarmored_ac`, `armor_stealth_disadv`, `weapon_damage_dice`, `weapon_damage_type` | R-ITM-001~015 |
| `classes.py` (229行) | `CLASSES` dict | **12** | `class_names`, `get_class` | 12 核心职业 |
| `races.py` (185行) | `RACES` dict | **10** | `race_names`, `get_race` | 10 可扮演种族 |
| `backgrounds.py` (183行) | `BACKGROUNDS` dict | **16** | `background_names`, `get_background` | 16 背景 |

**汇总**：法术 12、专长 74、位面 58、魔法物品 30、护甲 13、武器 38、职业 12、种族 10、背景 16、据点特色设施 29 + 基础设施 6 + 随机事件 11。规则库 RAG 语料源 data.js 约 6238 条。
