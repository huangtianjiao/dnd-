# 状态权威关系（P1-06）

> 约定：**每个规则状态字段有且只有一个权威持有者**。其余层只是快照/投影，
> 不得作为可独立修改规则状态的"第二数据库"。

## Aggregate 权威归属

| 状态载体 | 角色 | 权威字段 |
|---|---|---|
| `Character`（SQLite `stats.models.Character`） | **权威** | HP/AC/速度/属性/法术位/物品/熟练（P1-01 服务器计算） |
| `Campaign`（`stats.models.Campaign`） | **权威** | 世界标记/摘要/规则集标识；`version` 乐观锁（P1-05） |
| `Combat`（`engine.combat.Combat` + `CombatState`） | **权威** | 回合/先攻/参战者 HP/效果；`version` 乐观锁（API-001） |
| `GameState`（`brain.state.GameState`） | 命令执行快照 | 单轮判定链的输入/输出，不持久化为规则状态 |
| `CampaignRoom` / `CampaignRoom.players` | 连接在场投影 | 仅 sid/name/connected；**不得存储规则数值** |
| LangGraph checkpoint | 工作流延续 | 仅 HITL 中断恢复，**不得作为规则状态读取** |
| `RoomManager`（REST 房间） | 房间在场投影 | 玩家列表/密码/状态标识；HP 等规则数值一律读 Character |

## 强制规则

1. **写入唯一入口**：规则状态（HP/法术位/回合）只能经
   `stats.store`（SQLite）与 `engine.combat` 修改；`Room`/`GameState`/复数
   checkpoint 一律只读。
2. **Room 不是状态库**：`CampaignRoom.players` 只用于广播在场与回合提示；
   若需要玩家 HP，从 `store.load_combat` / `store.get_character` 读取。
3. **checkpoint 不是状态库**：`/chat/resume` 恢复工作流前必须重新加载
   权威状态（P1-03 已按 campaign 锁 + 权威校验）。
4. **客户端无状态写入**：`/character`、`/join`、`/room/join` 的
   HP/AC/速度由服务器计算（P1-01），客户端提交值被忽略。
5. **版本化并发**：`Campaign.version`（P1-05）与 `Combat.version`（API-001）
   构成乐观锁；`expected_version` 不匹配 → 409，防止丢失更新。

## 数据流示例（攻击行动）

```
ws.on_action / POST /chat
  → GameState（快照）
  → graph.resolve → check.attack_roll（只读 Character 数据）
  → apply_node → store.save_character / store.save_combat（写权威库）
  → _broadcast_state（广播投影，不写库）
```