# 多人战斗流程重构设计（服务端回合状态机）

> 状态：设计稿（待实施）
> 关联文档：docs/ISSUES.md、docs/FLOW_ALIGNMENT.md、docs/FRONTEND_BACKEND_AUDIT.md
> 规则版本：D&D 5E 2024（PHB/DMG，中文规则库 `5echm_web/topics/`）

## 1. 背景与问题

多人战斗模块 review（2026-07）发现当前实现存在结构性缺陷，根因是
**单人流程的"一条输入 = 一个完整回合"假设泄漏到了多人场景**，
并叠加了两套互相冲突的回合推进机制：

| # | 问题 | 位置 | 后果 |
|---|------|------|------|
| A | 玩家每次行动后 `apply_node` 自动 `advance_turn` 并内联跑完怪物回合 | `brain/resolvers/apply.py` 3e 段 | 回合粒度错误；与手动 `end_turn` 叠加会双重推进跳过队友 |
| B | `on_end_turn` 只推进 1 格；轮到活怪物/死者时无人能行动、无事件能推进 | `api/ws.py on_end_turn` | **战斗死锁** |
| C | `monster_turn`/`monster_action` 是纯广播，不改战斗状态 | `api/ws.py` | DM 事件无法解开死锁 |
| D | 怪物永远只攻击"最后行动的玩家"（`run_monster_turn(cur, ch, ...)` 的 `ch` 是当前行动者） | `apply.py run_monster_turn` | 多人下其他队友永不被攻击 |
| E | `_combatant_to_dict` 不序列化 conditions/speed_remaining/group_id 等字段 | `stats/store.py` | 状态条件跨行动全部丢失 |
| F | 死亡豁免在受伤当下（攻击者流程内）掷 | `apply.py` 3d 段 | 违反 PHB「以 0 HP 开始回合时掷」 |
| G | 回合检查在 campaign 锁外（TOCTOU）；`end_turn` 不加锁 | `api/ws.py` | 并发丢失更新 |
| H | 非当前回合玩家的一切输入被拒绝 | `api/ws.py on_action` | 违反「交流不需要动作」「反应发生在别人回合」 |
| I | 怪物精确 HP 广播给所有玩家 | `api/ws.py _combatant_payload` | 违反 DMG「DM 秘密跟进怪物 HP」惯例 |

## 2. 规则依据（原文出处）

所有设计决策均以仓库内规则库原文为准：

### 2.1 战斗结构（PHB 战斗流程）
> 出处：`topics/玩家手册2024/进行游戏/战斗流程.htm`

- 战斗步骤：确定位置 → 投掷先攻 → **每位参与者按先攻序列执行其战斗回合**，
  所有参与者完成回合后该轮结束，循环直至战斗结束。（R-CMB-001~004）
- 先攻序列每轮保持一致；同组相同怪物只掷一次先攻共用。
- 突袭者先攻掷骰具有劣势。（R-GLS-009）
- 结束战斗：一方全部被击杀/击晕/投降/逃跑，或双方认可结束。

### 2.2 回合内容（PHB 你的回合 / 动作）
> 出处：`topics/玩家手册2024/进行游戏/战斗流程.htm`、`动作.htm`

- 你的回合 = 移动（至多速度值）+ 一个动作，顺序自定；可能还有 1 个附赠动作、
  1 次免费物件交互 —— **一个回合由多个步骤组成**。
- 交流不需要动作或移动力，可随时进行。
- 「一次一件事」：一次只能执行一个动作。（R-CMB-011）
- **「在你的回合里什么也不干」是合法的**；规则书建议不知道做什么时执行
  回避（Dodge）或预备（Ready）→ 这是掉线/超时玩家兜底的官方答案。

### 2.3 反应（PHB 反应）
> 出处：`topics/玩家手册2024/进行游戏/反应.htm`

- 反应可以发生在**别人的回合**（最常见：借机攻击）。
- 用掉后直至自己下个回合开始不能再用。（R-CMB-013）

### 2.4 死亡豁免（PHB 生命值降至0点）
> 出处：`topics/玩家手册2024/进行游戏/生命值降至0点.htm`

- **「每当你以 0 生命值开始回合时，你必须进行死亡豁免检定」**——
  时点是濒死者自己回合的开始，不是受伤当下。
- 0 HP 期间受到伤害 = 记 1 次豁免失败；重击 = 2 次；伤害 ≥ HP 上限 = 直接死亡。
- d20=1 记 2 次失败；d20=20 恢复 1 HP 苏醒。
- 昏迷（0 HP 未死）= 失能，不能执行动作/附赠/反应。

### 2.5 DM 主持惯例（DMG 运作战斗）
> 出处：`topics/城主指南2024/2.运作游戏/运作战斗/*.htm`

- 跟进先攻：叫出当前者时**顺口提及下一位**，让玩家提前准备。
- 跟进怪物生命值：**大多数 DM 秘密跟进，玩家不知道怪物剩余 HP**。
- 使用并跟进状态：状态必须持续跟进（要求持久化完整）。
- 让战斗持续推进：僵局时可加速怪物死亡、停止敌对等（授权超时兜底机制）。
- 战斗或者逃跑（士气）：怪物**浴血（≤半血）且过半盟友倒下**时，
  WIS DC10 豁免，失败则逃跑或谈和。

### 2.6 怪物目标选择（DMG 怪物行为）
> 出处：`topics/城主指南2024/4.创建冒险/规划遭遇/怪物行为.htm`、
> `2.运作游戏/运作战斗/让战斗持续推进.htm`

- 怪物有性格/战术/关系，会对局势做出反应；
  「不要重复游戏状态」——不应固定纠缠单一目标。
- 最低要求：目标从**全体存活玩家**中选择，而非最后行动者。

## 3. 目标架构：服务端回合状态机

核心原则：**回合归属权是唯一真相（single source of truth），
由服务端驱动推进；玩家行动只消耗动作经济，不隐式推进回合。**

```
                    ┌──────────────────────────────────────────┐
                    │  advance_to_next_actor(combat) 服务端循环  │
                    └──────────────────────────────────────────┘
 start_combat ──▶ 回合开始钩子 begin_turn(cur):
                    ├─ 跳过 dead / 已逃跑者（引擎层保证）
                    ├─ _reset_turn_economy(cur)（已有）
                    ├─ 0HP 玩家 → 掷死亡豁免 → 广播 → 昏迷失能 → 自动结束回合
                    └─ 广播 turn_started {current, next}
                          │
        ┌─────────────────┴──────────────────┐
        ▼ 当前者是怪物                        ▼ 当前者是玩家
  resolve_monster_turn():              等待玩家输入（可多次）:
    ├─ 士气豁免（浴血+半数盟友倒下       ├─ action 事件 → graph.run
    │   → WIS DC10，败则逃跑/谈和）     │   只结算+消耗动作经济，不推进回合
    ├─ 选目标：全体存活玩家中选          ├─ 结束条件（三选一）:
    │   （最低 HP 比例 / 随机加权）      │   a. 玩家显式 end_turn
    ├─ 攻击结算（确定性，不调 LLM）      │   b. 动作+移动耗尽 → 前端提示确认
    ├─ 广播 monster_action              │   c. 回合计时器超时
    └─ 自动 advance ──────┐             │      → 自动【回避】+ end_turn
                          │             └──────────┐
                          ▼                        ▼
                 每次伤害后 check_combat_end；结束→广播 combat_end
                          │
                          └─▶ advance_to_next_actor（回到顶部）
```

### 3.1 与现状的关键差异

| 维度 | 现状 | 目标 |
|------|------|------|
| 回合推进者 | 玩家行动隐式推进（apply.py）+ 手动 end_turn 双轨 | 仅服务端状态机推进 |
| 怪物回合 | 内联在玩家行动的结算尾部 | 独立结算函数，推进到怪物时自动触发 |
| 怪物目标 | 最后行动的玩家 | 全队选择（策略可配） |
| 死亡豁免 | 受伤当下掷 | 濒死者回合开始时掷 |
| 回合粒度 | 1 输入 = 1 回合 | 1 回合 = N 次输入 + 显式/超时结束 |
| 死者回合 | 会轮到死人 → 死锁 | 引擎层跳过 |
| 掉线玩家 | 卡死全桌 | 超时自动回避（PHB 背书） |

## 4. 详细设计

### 4.1 引擎层 `engine/combat.py`

#### 4.1.1 `advance_turn` 跳过丧失行动能力者

```python
def _cannot_act(c: Combatant) -> bool:
    """死亡或已逃离战场者没有回合。0HP 昏迷玩家仍保留回合（要掷死亡豁免）。"""
    return c.dead or getattr(c, "fled", False)

def advance_turn(combat: Combat) -> Combatant | None:
    if not combat.active:
        return None
    n = len(combat.initiative_order)
    for _ in range(n + 1):                    # guard：最多绕一圈
        combat.current_index += 1
        if combat.current_index >= n:
            combat.current_index = 0
            combat.round += 1
            combat.seconds_elapsed += 6       # R-CMB-001
        cur = current_combatant(combat)
        if cur is not None and not _cannot_act(cur):
            _reset_turn_economy(cur)
            return cur
    combat.active = False                     # 全员丧失行动能力
    return None
```

注意：**0 HP 未死玩家不跳过**——他的回合开始要掷死亡豁免（见 4.1.2），
这正是 PHB 规定的时点。掷完后因昏迷=失能自然无法行动，由状态机自动结束其回合。

#### 4.1.2 回合开始钩子 `begin_turn`

新增纯函数（引擎层只产出事件，不做 IO/广播）：

```python
def begin_turn(combat: Combat, cur: Combatant) -> dict:
    """回合开始处理，返回事件供上层广播。
    规则: R-CMB-004 回合开始 / 生命值降至0点（死亡豁免时点）
    """
    events = {"combatant": cur.name, "auto_end": False}
    # 濒死玩家：掷死亡豁免（由上层拿 Character 数据掷，这里只标记）
    if cur.is_player and cur.hp <= 0 and not cur.dead:
        events["needs_death_save"] = True
        events["auto_end"] = True            # 昏迷=失能，掷完即结束回合
    if cur.conditions.is_incapacitated():
        events["auto_end"] = True            # 失能者无事可做
    return events
```

死亡豁免的实际掷骰复用 `apply.py` 已有的 `damage.death_save + to_death_tracker`
链路，从 3d 段整体搬到回合开始处理中（见 4.3）。

#### 4.1.3 turn/round 事件语义不变

`round`、`current_index`、`seconds_elapsed` 语义保持，前端 `combat_update` 不受影响。

### 4.2 新模块 `brain/combat_flow.py`（服务端回合驱动）

把散落在 `apply.py` 3e 段和 `ws.py on_end_turn` 的推进逻辑收拢为一个模块，
REST 与 WS 共用：

```python
# brain/combat_flow.py（新建）

def advance_and_resolve(campaign_id: int, party: list[Character]) -> FlowResult:
    """推进回合并自动结算非玩家回合，直到轮到某个玩家或战斗结束。

    返回 FlowResult:
      events:   [dict]  # 依序发生的事件（怪物行动/死亡豁免/士气/轮次结束）
      combat:   Combat  # 推进后的战斗状态（已持久化）
      current:  Combatant | None  # 停在谁的回合（玩家）；None=战斗结束
    """
```

内部循环（伪代码）：

```
combat = store.load_combat(campaign_id)
loop:
    cur = cmb.advance_turn(combat)
    if cur is None: break                        # 战斗结束/全灭
    ev = cmb.begin_turn(combat, cur)
    if ev.needs_death_save:
        events += 掷死亡豁免(cur 对应的 Character)  # 复用 apply.py 3d 逻辑
    if ev.auto_end: continue                     # 昏迷/失能者回合直接结束
    if cur.is_player: break                      # 停：等这个玩家输入
    # —— 怪物回合 ——
    if 士气检查失败(cur, combat):                 # DMG 战斗或者逃跑
        cur.fled = True; events += 逃跑事件; continue
    target = select_target(cur, party, combat)   # 见 4.2.1
    events += run_monster_turn(cur, target, ...)  # 复用现有确定性结算
    cmb.check_combat_end(combat)
    if not combat.active: break
store.save_combat(campaign_id, combat)
```

#### 4.2.1 怪物目标选择 `select_target`

```python
def select_target(monster, party_combatants, combat) -> Combatant:
    """DMG 怪物行为：从全体存活玩家中选目标。
    默认策略 weighted_random：存活玩家等权随机，已倒地(0HP)者不选
    （避免鞭尸刷死亡豁免失败——除非只剩倒地者）。
    预留 strategy 参数：nearest / lowest_hp / random。
    """
```

选择"随机"为默认而非"最低 HP"：DMG 无集火规则，随机最接近
「不要重复游戏状态」的精神，也避免算法性针对同一玩家。

#### 4.2.2 `run_monster_turn` 签名调整

从 `apply.py` 移入 `combat_flow.py`（`apply.py` 保留 re-export 兼容）：

```python
def run_monster_turn(monster: Combatant, target_ch: Character, state) -> dict
```

与现在唯一区别：`target_ch` 由 `select_target` 决定，不再固定为行动者。
事件 dict 增加 `"target": target_ch.name` 字段供叙事与前端渲染。

#### 4.2.3 士气检查（P2，可先留桩）

```python
def morale_check(monster, combat) -> bool:
    """DMG 战斗或者逃跑：浴血 + 过半盟友倒下 → WIS DC10 豁免，失败则逃跑。
    出处: topics/城主指南2024/2.运作游戏/运作战斗/战斗或者逃跑.htm
    """
    bloodied = monster.hp <= monster.hp_max // 2
    allies = [c for c in combat.participants if c.side == monster.side]
    downed = sum(1 for c in allies if c.dead or c.hp <= 0)
    if not (bloodied and downed * 2 > len(allies)):
        return True                                  # 无需检查
    return check.saving_throw(mod=0, prof=0, proficient=False, dc=10).success
```

`Combatant` 增加字段 `fled: bool = False`；`check_combat_end` 的
`_down` 判定补充 `or c.fled`（逃跑者视为退出战斗，符合 PHB「逃跑则战斗结束」）。

### 4.3 结算层 `brain/resolvers/apply.py`

**删除**（迁移）以下内容：

1. **3d 段（死亡豁免）**：整体迁移到 `combat_flow` 的回合开始处理。
   受伤当下只保留 PHB 规定的即时效果（已在 `apply_damage_to_character` 中：
   0HP 受伤记失败/重击双失败/过量伤害即死——保留不动）。
2. **3e 段（`advance_turn` + 怪物回合内联循环）**：整体删除。
   `apply_node` 在战斗中只做：伤害/治疗结算 → 双列表 HP 同步 →
   `check_combat_end` → `save_combat`。
3. `run_monster_turn` / `render_monster_events` 移至 `combat_flow.py`，
   原位置保留 `from ..combat_flow import run_monster_turn  # 兼容` 。

**新增**：结算后标记动作经济。`apply_node` 根据 `dice.kind` 消耗当前
Combatant 的动作资源：

| dice.kind | 消耗 |
|-----------|------|
| attack / cast / dash / dodge / disengage / help / hide / search / study / use_item / grapple / shove | `use_action(cur)` |
| bonus 类（后续细分） | `use_bonus_action(cur)` |
| opportunity_attack | `use_reaction(cur)` |
| 移动类 | 扣 `speed_remaining` |

行动被引擎拒绝（`use_action` 返回 False = 本回合动作已用完）时，
在 narration 附加提示「本回合动作已用完，可结束回合」。
> 说明：P0 阶段允许宽松处理——只标记不硬拒绝，避免 LLM 意图分类误伤；
> P1 收紧为硬约束。

### 4.4 WS 层 `api/ws.py`

#### 4.4.1 事件协议（对照前端 `ui/app/hooks/useSocket.ts`）

| 事件 | 方向 | 现状 | 变更 |
|------|------|------|------|
| `action` | C→S | 回合检查在锁外 | 检查移入锁内；非战斗性输入放行（见 4.4.3） |
| `end_turn` | C→S | 裸 advance 1 格 | 改调 `combat_flow.advance_and_resolve`，全程持 campaign 锁 |
| `turn_advanced` | S→C | `{next, is_player}` | 增加 `{next_next}`（DMG「顺口提及下一位」）；前端已有监听，字段向后兼容 |
| `monster_action` | S→C | 仅 DM 手动触发 | 由 `advance_and_resolve` 的怪物事件自动逐条发出，载荷含 `target`；DM 手动路径保留 |
| `monster_turn` | C→S (DM) | 纯广播 | 降级为可选叙事覆盖；不再是推进战斗的必要路径 |
| `combat_end` | S→C | 仅 DM 手动 | `check_combat_end` 判定结束时服务端自动广播 `{outcome}` |
| `combat_update` | S→C | 含怪物精确 HP | 载荷分流（见 4.4.4） |
| `death_save` | S→C | 无 | **新增**：`{player, roll, successes, failures, stable, dead, regain}` |
| `turn_timeout_warning` | S→C | 无 | **新增**：超时前 15s 提醒当前玩家 |

前端未监听的新事件不影响现有 UI（socket.io 未知事件被忽略），可渐进接入。

#### 4.4.2 `on_end_turn` 重写（核心）

```python
@sio.on("end_turn")
async def on_end_turn(sid, data):
    session = await sio.get_session(sid)
    if not session: return
    campaign_id, character_id = session["campaign_id"], session["character_id"]
    room = _room_name(campaign_id)

    async with get_campaign_lock(campaign_id):          # G: 并发修正
        camp_room = CampaignRoom.get(campaign_id)
        if camp_room and not camp_room.is_player_turn(character_id):
            await sio.emit("error", {"message": "不是你的回合"}, to=sid); return
        party = _load_party_characters(campaign_id)     # 房间内全部角色卡
        loop = asyncio.get_event_loop()
        flow = await loop.run_in_executor(
            None, combat_flow.advance_and_resolve, campaign_id, party)

    for ev in flow.events:                              # 锁外逐条广播
        await _emit_flow_event(room, ev)                # monster_action / death_save / round_end...
    await _broadcast_state(campaign_id)
    if flow.current:
        await sio.emit("turn_advanced", {
            "next": flow.current.name, "is_player": True,
            "next_next": _peek_next_name(flow.combat)}, room=room)
        _restart_turn_timer(campaign_id, flow.current)  # 见 4.4.5
    elif not flow.combat.active:
        await sio.emit("combat_end", {"outcome": _outcome(flow.combat)}, room=room)
```

`on_action` 尾部（graph.run 返回后）追加一步：若结算后战斗仍激活且
**当前玩家动作已耗尽**，`result` 载荷带 `"turn_hint": "action_exhausted"`，
前端据此高亮"结束回合"按钮。**不自动推进**。

#### 4.4.3 非当前回合输入策略（问题 H）

`on_action` 的回合拦截改为三分类：

```
战斗未激活          → 放行（现状）
轮到自己            → 放行
没轮到自己:
  ├─ intent 为纯对话/扮演（graph 意图分类已有 talk/social 类别）→ 放行，
  │   但强制走"不消耗动作经济、不推进状态"的窄路径
  └─ 其他 → 拒绝，提示"当前轮到 {turn}"
```

P0 简化版：没轮到自己时，凡 `player_input` 不以战斗动词开头即视为交流，
只广播不进结算链。P1 接入意图分类做精确判定。
反应（借机攻击确认窗口）列为 P2，当前由引擎在结算内自动处理，不阻塞本重构。

#### 4.4.4 怪物 HP 保密（问题 I / DMG 惯例）

`_combatant_payload` 拆两档：

```python
def _combatant_payload(x, for_dm: bool) -> dict:
    base = {"name": x.name, "initiative": x.initiative, "side": x.side,
            "dead": x.dead, "surprised": x.surprised}
    if x.side == "player" or for_dm:
        base |= {"hp": x.hp, "hp_max": x.hp_max}
    else:
        base |= {"hp_state": "dead" if x.dead
                 else "bloodied" if x.hp <= x.hp_max // 2   # 5e 术语「浴血」
                 else "healthy"}
    return base
```

`_broadcast_state` 对 DM 的 sid 单发全量版，房间广播发脱敏版。
前端 `PartyBar`/战斗追踪器需适配 `hp_state`（无 `hp` 字段时显示状态词）。
> 兼容开关：`MONSTER_HP_VISIBLE=1` 环境变量可回退旧行为，供既有单人局使用。

#### 4.4.5 回合计时器（掉线兜底，PHB「什么也不干→回避」）

```python
TURN_TIMEOUT = float(os.getenv("TURN_TIMEOUT", "90"))   # 0 = 关闭

async def _turn_timer(campaign_id: int, combatant_cid: str):
    await asyncio.sleep(TURN_TIMEOUT - 15)
    await sio.emit("turn_timeout_warning", {...}, room=...)
    await asyncio.sleep(15)
    async with get_campaign_lock(campaign_id):
        c = store.load_combat(campaign_id)
        cur = cmb.current_combatant(c)
        if cur and cur.cid == combatant_cid:            # 仍是该玩家 → 超时
            cur.dodge_active = True                      # 自动回避（R-CMB-008）
            store.save_combat(campaign_id, c)
            # 走与 on_end_turn 相同的 advance_and_resolve 流程
```

计时器任务存 `dict[campaign_id, asyncio.Task]`，玩家 `end_turn`/行动推进时取消重建。
单人局（房间内仅 1 名玩家）默认不启用计时器，保持现有单人体验。

### 4.5 持久化 `stats/store.py`（问题 E）

#### 4.5.1 全字段序列化

`ConditionState` 增加：

```python
def to_dict(self) -> dict:
    return {"conditions": sorted(self.conditions), "exhaustion": self.exhaustion}

@classmethod
def from_dict(cls, d: dict) -> "ConditionState":
    return cls(conditions=set(d.get("conditions", [])),
               exhaustion=int(d.get("exhaustion", 0)))
```

`_combatant_to_dict` 改为基于 `dataclasses.fields` 的全量导出
（`conditions` 走 `to_dict`，`position` tuple→list），
`_dict_to_combatant` 逆向恢复，**未知/缺失字段用 dataclass 默认值**
（保证旧存档可读，向前兼容）。

补齐字段清单：`group_id, speed, speed_remaining, position, reach,
conditions, disengage_active, dodge_active, hidden, ready_trigger,
ready_action_name, help_advantage_target, fled`。
`Combat.seconds_elapsed` 一并入 `CombatState`（新列或塞进 JSON，选 JSON 免迁移：
在 `participants_json` 外增 `meta_json`）。

#### 4.5.2 对象同一性

`load_combat` 后按 `cid` 合并：

```python
by_cid = {c.cid: c for c in combat.initiative_order}
combat.participants = [by_cid.get(c.cid, c) for c in combat.participants]
```

`initiative_order` 与 `participants` 共享同一对象，
`apply.py` 中所有 `for _lst in (combat.participants, combat.initiative_order)`
双列表写法可随后简化为单列表（P1 清理项，先保留不影响正确性）。

### 4.6 并发（问题 G）

- `on_action`：`is_player_turn` 检查**移入** `get_campaign_lock` 临界区，
  与 `graph.run` 同锁。
- `on_end_turn` / 回合计时器超时处理：同一把锁。
- REST `/chat`：进入前同样做回合检查（战斗激活时），复用
  `ConnectionManager.is_player_turn`；多人房间的战役 REST 战斗性输入直接 409。
- 锁清理：`CampaignRoom` 销毁（`_dispose`）时调用现有
  `_cleanup_campaign_lock(campaign_id)`（当前是死代码，接上即可）。

## 5. 实施计划

### 阶段 P0 —— 解死锁 + 状态机（一次合入，不可拆）

| 步骤 | 文件 | 内容 |
|------|------|------|
| 1 | `engine/combat.py` | `advance_turn` 跳过 dead/fled；新增 `begin_turn`；`Combatant.fled` |
| 2 | `stats/store.py` + `engine/conditions.py` | 全字段序列化 + `ConditionState.to_dict/from_dict` + cid 合并 |
| 3 | `brain/combat_flow.py`（新建） | `advance_and_resolve` / `select_target` / 迁移 `run_monster_turn`（改签名）/ 死亡豁免迁移 |
| 4 | `brain/resolvers/apply.py` | 删 3d/3e 段；结算后标记动作经济（宽松版） |
| 5 | `api/ws.py` | `on_end_turn` 重写；回合检查入锁；`turn_advanced` 加 `next_next`；战斗结束自动广播 `combat_end`；新增 `death_save` 事件 |
| 6 | `ui/app/hooks/useSocket.ts` + `combat-store.ts` | 监听 `death_save`；`turn_hint` 高亮结束回合按钮 |

> 序列化（步骤 2）必须与状态机同批：新流程依赖 conditions/fled 跨请求存活。

### 阶段 P1 —— 规则收紧

- 动作经济硬约束（动作用尽拒绝再攻击）。
- REST `/chat` 回合检查。
- 非回合输入的意图分类放行（交流窄路径）。
- apply.py 双列表写法清理（依赖 4.5.2 完成）。

### 阶段 P2 —— 多人体验

- 回合计时器 + 超时自动回避（4.4.5）。
- 怪物 HP 保密分流（4.4.4，带回退开关）。
- 士气系统（4.2.3）。
- 借机攻击的玩家确认窗口。

### 不在本次范围（另立议题）

- 鉴权体系（DM 身份服务端认定、房间密码在 WS 握手校验、character 归属校验）
  —— 见 review 问题 3，独立安全议题。
- `RoomManager` 与 `CampaignRoom` 双房间系统合并。

## 6. 测试计划

单测（`tests/test_combat_flow.py` 新建）：

1. **死锁回归**：先攻序列 [玩家A, 哥布林, 玩家B]，A `end_turn` →
   `advance_and_resolve` 自动结算哥布林回合并停在 B；B 可行动。
2. **跳过死者**：哥布林 dead 后 A `end_turn` 直达 B；全怪物死 → `combat_end`。
3. **死亡豁免时点**：B 被打到 0HP 时**不掷**豁免；轮到 B 回合开始才掷，
   掷完自动跳过到下一位；3 次失败 → dead → 之后被跳过。
4. **目标选择**：3 玩家在场，怪物 100 次攻击的目标覆盖全部存活玩家；
   0HP 倒地者不被选中（除非全员倒地）。
5. **序列化往返**：Combatant 加 3 种状态 + 半移动力 + group_id →
   save/load → 全字段相等；旧格式 JSON（缺新字段）可加载。
6. **并发**：两个并发 `end_turn` 只推进一次（锁内二次校验）。
7. **动作经济**：同回合两次 attack，第二次带"动作已用完"提示（P0 宽松）/
   拒绝（P1）。

集成冒烟：`scripts/` 下增加双客户端 socket.io 脚本，模拟 2 玩家 + 2 怪物
完整打满 3 轮（含一人掉线超时，P2 后）。

## 7. 风险与兼容性

| 风险 | 缓解 |
|------|------|
| 旧存档 CombatState 缺新字段 | `_dict_to_combatant` 缺省值兜底；不做 DB 迁移 |
| 前端依赖"行动后自动到下一回合"的现有体感 | 单人局（房间 1 人）保留自动 end_turn：`advance_and_resolve` 由 `on_action` 尾部在"仅一名玩家"时自动调用，行为与现状等价 |
| LLM 意图分类误判导致动作经济误消耗 | P0 只标记不拒绝；P1 结合实测再收紧 |
| 怪物 HP 隐藏影响现有单人 UI | `MONSTER_HP_VISIBLE` 开关回退 |
| `monster_turn`/`monster_action` DM 事件语义变化 | 保留事件与权限检查，仅从"必要路径"降级为"叙事覆盖" |

## 8. 决策记录

1. **超时兜底 = 自动回避**而非跳过回合：PHB 原文建议
  （「不妨执行戒备的回避动作」），且对掉线玩家更友好（AC 受劣势保护）。
2. **怪物默认随机选目标**而非集火最低 HP：DMG 无集火规则，
   「不要重复游戏状态」+ 避免体验性针对。
3. **0HP 玩家不跳过回合**：死亡豁免时点必须在其回合开始（PHB 原文），
   跳过会导致濒死状态永不推进。
4. **单人局保留自动推进**：多人语义（显式 end_turn）只在房间玩家 >1 时启用，
   避免破坏现有单人体验与既有测试。
5. **鉴权不混入本次重构**：回合状态机与安全边界正交，分开合入降低风险。
