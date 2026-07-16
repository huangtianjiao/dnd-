# API_REFERENCE — REST 端点与 WebSocket 事件参考

> 对应源码：`src/aidm/api/main.py`（FastAPI，`app = FastAPI(title="AI DM", version="0.3.0")`）、`src/aidm/api/ws.py`（python-socketio AsyncServer）。
> 后端默认端口 8080。Socket.IO 与 FastAPI 组合：`combined_app = socketio.ASGIApp(sio, app)`，`/ws/*` 由 Socket.IO 处理。

## 1. 基础与前端

| 方法 | 路径 | 函数 | 功能 |
|---|---|---|---|
| GET | `/` | `index` | Web 跑团前端 HTML 聊天页 |
| GET | `/health` | `health` | 健康检查 |
| GET | `/static/*` | (StaticFiles) | 静态资源托管 |

## 2. 战役/角色核心

| 方法 | 路径 | 函数 | 功能 |
|---|---|---|---|
| POST | `/campaign` | `create_campaign` | 建战役 |
| POST | `/character` | `create_character` | 建角色卡 |
| GET | `/character/{cid}` | `get_character` | 角色卡全数据（前端面板） |
| GET | `/character/{cid}/inventory` | `get_inventory` | 物品栏 + 同调 + 魔法物品详情 + gold |
| GET | `/campaigns` | `list_campaigns` | 列出所有战役（继续游戏） |
| GET | `/campaign/{campaign_id}/state` | `get_campaign_state` | 加载战役完整状态（战役+场景+角色+摘要+战斗） |
| POST | `/generate_setting` | `generate_setting` | AI 生成世界设定（150-250字） |
| POST | `/open` | `open_campaign` | DM 开场：生成完整背景 + 当前场景 + 3 行动选项 |
| GET | `/scene/{campaign_id}` | `get_scene` | 取当前场景 |
| GET | `/summary/{campaign_id}` | `summary` | 取 rolling summary |
| POST | `/session/end` | `session_end` | Session 结束生成前情提要 |

## 3. 对话/判定链（核心）

| 方法 | 路径 | 函数 | 功能 |
|---|---|---|---|
| POST | `/chat` | `chat` | 跑一轮判定链；HITL interrupt 时返回 `interrupted=True` |
| POST | `/chat/resume` | `chat_resume` | HITL 恢复：DM 给 y/n 后继续（`Command(resume=...)`） |

## 4. 魔法物品与战利品（brain/loot.py）

| 方法 | 路径 | 函数 | 功能 |
|---|---|---|---|
| GET | `/magic-items` | `list_magic_items` | 魔法物品库（rarity/item_type/cursed_only 筛选） |
| GET | `/magic-items/{name}` | `get_magic_item` | 查特定魔法物品 |
| POST | `/character/{cid}/attune` | `attune_item` | 同调魔法物品（≤3 件） |
| POST | `/character/{cid}/break-attunement` | `break_attunement` | 解除同调 |
| POST | `/loot/generate` | `generate_loot` | 生成随机战利品池（按 CR） |
| POST | `/loot/distribute` | `distribute_loot`（L285，第一版） | 分配战利品 + 金币（method=need_priority/round_robin/point_bid/dm_assign） |

## 5. 战斗/怪物

| 方法 | 路径 | 函数 | 功能 |
|---|---|---|---|
| GET | `/combat/{campaign_id}` | `get_combat` | 战斗状态（追踪器） |
| GET | `/monster/{name}` | `get_monster` | 怪物数值检索（data.js RAG） |

## 6. 多人/加入

| 方法 | 路径 | 函数 | 功能 |
|---|---|---|---|
| POST | `/join` | `join_campaign` | 加入已有战役，返回 character_id + ws_url |
| GET | `/players/{campaign_id}` | `get_players` | 列出在线玩家 + 当前回合 |

## 7. 房间管理（brain/room.py RoomManager）

| 方法 | 路径 | 函数 | 功能 |
|---|---|---|---|
| POST | `/room/create` | `create_room` | 房主建战役 + 房间（密码/人数上限） |
| POST | `/room/join` | `join_room` | 玩家加入房间（错误码：room_not_found/wrong_password/room_full/name_taken） |
| GET | `/room/{room_id}` | `get_room_status` | 房间状态 |
| GET | `/rooms` | `list_rooms` | 列出所有活跃房间 |
| POST | `/room/{room_id}/kick` | `kick_player` | 房主踢人（不能踢房主） |
| POST | `/room/{room_id}/transfer` | `transfer_host` | 房主转让权限 |

## 8. 战利品分配（brain/loot_distribution.py）

| 方法 | 路径 | 函数 | 功能 |
|---|---|---|---|
| POST | `/loot/pool` | `generate_loot`（L844） | 按 CR 列表生成战利品池 |
| POST | `/loot/distribute/v2` | `distribute_loot`（L883，第二版） | 完整分配流程（mode=NEED_FIRST/ROUND_ROBIN/ROLL_OFF/DM_ASSIGN） |
| GET | `/loot/history/{campaign_id}` | `get_loot_history` | 分配历史 |

## 9. 专长系统（PHB 第五章）

| 方法 | 路径 | 函数 | 功能 |
|---|---|---|---|
| GET | `/feats` | `list_feats_api` | 可选专长列表（category 筛选） |
| POST | `/character/{cid}/feat` | `add_feat` | 为角色选专长（非复选不可重复） |
| GET | `/character/{cid}/available-feats` | `available_feats_api` | 当前等级可选专长（4/8/12/16 通用，19 传奇恩惠） |
| POST | `/character/{cid}/select-feat` | `select_feat_api` | 选专长并持久化（校验起源/传奇恩惠等级） |

## 10. 据点系统（DMG 第八章）

| 方法 | 路径 | 函数 | 功能 |
|---|---|---|---|
| POST | `/stronghold/create` | `create_stronghold_api` | 建据点（要求等级 ≥5） |
| GET | `/stronghold/{campaign_id}` | `get_stronghold_api` | 查据点状态 |
| POST | `/stronghold/build` | `build_facility_api` | 建设施（狭窄 500GP / 宽敞 1000GP / 庞大 3000GP） |
| POST | `/stronghold/turn` | `run_stronghold_turn_api` | 据点回合（每 7 天：维护/制造/增强/收获/招募/调查/贸易） |
| GET | `/strongholds/facilities` | `list_facilities_api` | 特色设施列表（按 level 筛选） |

---

## ⚠️ 已知问题：/loot/distribute 路由冲突

`main.py` 中 `/loot/distribute` 路径被定义两次：
- **第一版**（L285）：用 `brain/loot.py` 的 `LootPool` + `distribute_loot`，`method=need_priority/round_robin/point_bid/dm_assign`，输入 `{gold, magic_item_names, players, method, ...}`
- **第二版**（L883，原 `/loot/distribute`）：用 `brain/loot_distribution.py`，`mode=NEED_FIRST/ROUND_ROBIN/ROLL_OFF/DM_ASSIGN`，输入 `{campaign_id, gold, items, player_names, mode, ...}`

FastAPI 同 path+method 注册两次，第一个匹配优先 → 第二版被遮蔽成死代码。**已修复**：第二版重命名为 `/loot/distribute/v2`（保留功能，避免遮蔽）。根因是模块级 `from ..brain import loot_distribution as loot`（L833）重绑定了 `loot` 名字，与函数体内 `from ..brain import loot`（L291）冲突。

---

## WebSocket 事件（api/ws.py）

基于 `python-socketio` 的 `AsyncServer`（async_mode="asgi"，cors="*"，ping_interval=25，ping_timeout=20）。房间命名 `campaign_{id}`。`CampaignRoom`（Colyseus 风格）管理生命周期：空房 30 秒后自动销毁（`DISPOSE_DELAY=30.0`）。`_graph_lock` 序列化 `graph.run`（线程池执行，避免 Qdrant 并发问题）。

### 客户端 → 服务端事件

| 事件 | 处理函数 | 权限 | 职责 |
|---|---|---|---|
| `connect`（内置） | `connect` | — | query string 传 campaign_id/character_id/name/role，`enter_room` + `save_session`（断线重连）+ 注册 CampaignRoom + 推场景/战斗初始状态 |
| `disconnect`（内置） | `disconnect` | — | 从房间移除，广播 leave |
| `action` | `on_action` | 玩家 | 回合检查 → 通知 `player_acting` → 序列化 `graph.run` → 广播 `result` + `_broadcast_state` + 给行动者 `character_update` |
| `end_turn` | `on_end_turn` | 玩家 | 推进先政序列，跨回合时发 `round_end`，发 `turn_advanced` |
| `ready` | `on_ready` | 玩家 | 标记准备，广播 `player_ready` |
| `monster_turn` | `on_monster_turn` | 仅 DM | 怪物回合开始广播 |
| `monster_action` | `on_monster_action` | 仅 DM | 怪物行动结果广播 |
| `combat_end` | `on_combat_end` | 仅 DM | 战斗结束广播（outcome） |

### 服务端 → 客户端 emit 事件

| 事件 | 触发场景 |
|---|---|
| `join` | 玩家加入房间 |
| `leave` | 玩家离开/断线 |
| `scene_update` | 场景变更（`_broadcast_state` 增量同步） |
| `combat_update` | 战斗状态变更（只发 active/round/current_turn/initiative_order） |
| `player_acting` | 某玩家开始行动 |
| `processing` | 行动判定进行中 |
| `result` | 行动判定结果（narration + dice + action_options） |
| `character_update` | 角色状态更新（给行动者） |
| `error` | 错误通知 |
| `round_end` | 战斗一轮结束 |
| `turn_advanced` | 回合推进 |
| `player_ready` | 玩家标记准备 |
| `monster_turn` | 怪物回合开始 |
| `monster_action` | 怪物行动结果 |
| `combat_end` | 战斗结束 |

### 兼容层

`ConnectionManager`（`manager` 单例）为旧代码提供 `get_players` / `current_turn_name` / `is_player_turn` 静态方法，转发到 `CampaignRoom`。

> 注意：`brain/room.py` 自身也定义了 `PlayerSession`/`CampaignRoom`，与 `api/ws.py` 中的同名类是**两套实现**（main.py 房间端点用 `room.RoomManager`，ws.py 用自己的 `CampaignRoom`）。
