# ISSUES — 已知问题清单

> 项目 review 发现的遗留问题与状态。供后续迭代排期。

## 已修复 ✅

| # | 问题 | 修复 |
|---|------|------|
| 1 | 前端 API 端口配置与后端不一致 | `ui/.env.local` `NEXT_PUBLIC_API` `http://localhost:9000` → `http://localhost:8080` |
| 2 | config.py docstring 嵌入模型描述漂移 | docstring "嵌入本地 bge-m3" → "bge-small-zh-v1.5（512维）"（与默认值一致） |
| 3 | `/loot/distribute` 路由重复定义 | `main.py` L285 与 L883 同路径，FastAPI 第一匹配优先致 L883 被遮蔽。L883 版重命名为 `/loot/distribute/v2` |
| 4 | 静态前端 innerHTML XSS | `ui/static/app.js` 已是安全重构版（`esc()` 转义 + `createEl()` 用 textContent + `setHtmlWithBr()` 先转义再替换）。`security_report.md` 针对旧版本 |
| 5 | 无 Python 依赖锁定文件 | 新增 `requirements.txt`（锁定版本，可 `pip install -r` 复现） |

## 待办 — 安全 🔴

| 优先级 | 问题 | 说明 |
|---|------|------|
| 🔴 高 | CORS 未限制来源 | 当前 `allow_origins` 含 `localhost:3000/127.0.0.1:3000`，生产环境需收敛为实际域名 |
| 🔴 高 | 缺安全头 | `X-Frame-Options` / `X-Content-Type-Options` / `Content-Security-Policy` / `HSTS` / `Referrer-Policy` 全缺失（CSP 缺失为高风险） |
| 🔴 高 | 无鉴权/Session 校验 | 所有端点无 Authorization/Session，任何人都可操作任意战役/角色 |
| 🟡 中 | 无 CSRF Token | POST 端点无 CSRF 防护 |
| 🟡 中 | HEAD 请求返回 405 | 应支持 HEAD 方法 |

## 待办 — 功能/一致性 🟡

| 优先级 | 问题 | 说明 |
|---|------|------|
| 🟡 中 | Character 表缺 `skill_prof_json`/`save_prof_json` 持久化 | DECISIONS D-009 仍开放：熟练与否由 LLM classify 每轮判，重载/多角色场景无法回溯 |
| 🟡 中 | `brain/room.py` 与 `api/ws.py` 的 `CampaignRoom`/`PlayerSession` 是两套实现 | 需统一为单一来源 |
| 🟢 低 | MemorySaver 是内存级 checkpointer | 进程重启丢失图执行状态；持久化需换 SQLite/Postgres checkpointer |
| 🟢 低 | 无 lock 文件 | 已补 `requirements.txt`，但无 `poetry.lock`/`uv.lock` 等锁定哈希 |

## 已知架构缺口（非 bug，待实现）

| 缺口 | 状态 | 说明 |
|------|------|------|
| 空间推理工具 0/7 | ⚪ 暂缓 | 无网格寻路/视线/掩护/AoE 计算（GAP_ANALYSIS §3.3，仍准确） |
| agents/ 6 个 Agent 未完全接入 graph.py | 🟡 渐进迁移中 | Director/RuleJudge 已接入，Narrator/CombatEngine/WorldManager/EnemyAI 待替换 graph.py 本地节点 |
| GameState 仍是 TypedDict | 🟡 待升级 | 未升级为 Pydantic v2 |
| 多人架构 Phase 2-4 | ⚪ 未做 | 缺 Redis 扩展/断线重连恢复/DM-Player 权限分层 + Secret State 过滤 |
| 动态场景插图 API 未接 | 🟡 部分 | `image_gen.generate_scene_image` 待接真实图像服务；`render_battlefield_ascii` 已实现 |
| Enemy AI 待接入战斗循环 | 🟡 部分 | `agents/enemy_ai.py` 已建，但怪物行动现仍由 DM 手动操作（`ws.py:on_monster_action`） |

## 规则门控审计（2026-07-29 全量审计，已修复项见 tests/test_ownership_gate.py + test_rule_gates.py）

### 本轮已修复（硬性门控已接入判定链）

| 规则 | 修复内容 |
|---|---|
| R-SPL-036 法术须学会 | `_resolve_cast` 校验 known_spells（职业法术表+环阶可及）；创建时初始化；历史角色动态回退 |
| R-ITM-012 武器须拥有 | `_resolve_attack` 降级未拥有武器；`/equip-weapon` 拒绝 not_owned；起始武器入包 |
| R-ITM-013 武器熟练 | `class_weapon_proficient` 解析职业熟练串（含武僧/游荡者词条变体）；不熟练不加熟练加值 |
| R-GLS-015 长休冷却 | 16h 冷却存 world_flags[last_long_rest_min_{cid}]，_resolve_rest 拒绝、apply 落盘 |
| DMG 药水消耗品 | 治疗药水/高级治疗药水入魔法物品库；喝药须拥有，用后从 inventory 移除 |
| 同调拥有性 | `attune_magic_item` 校验物品在 inventory |
| R-GLS-047 力竭 6 级即死 | apply_node 强制 dead=True |
| state_changes 注入防护 | 玩家 hp delta 钳制 ±2×hp_max；temp_hp 钳制 ≤hp_max |

### 已审计确认为非问题（现有架构隐式覆盖）

| 审计项 | 结论 |
|---|---|
| 动作经济/每回合一法术位 | 每次 graph.run = 一个玩家回合（行动后 apply 3e 自动 advance_turn），单回合多动作无法通过聊天流触发 |
| 战斗中长休 | resolve 已拒绝 combat.active 时 rest/travel/explore/levelup |

### 遗留缺口（需 DB 迁移/大特性，按优先级排期）

| 优先级 | 缺口 | 阻塞原因 |
|---|---|---|
| 🔴 高 | 金币系统（Character 无 gold 字段，loot 金币不落盘，交易不可用） | 需 DB 字段 + 交易流程设计 |
| 🔴 高 | 技能熟练未持久化（skill_prof_json 缺失，现由 LLM 每轮猜 proficient） | 需 DB 字段 + 创角流程选技能 |
| 🟡 中 | 专注跨回合不持久（同一轮内受伤会触发豁免，下一轮丢失状态；新专注不终止旧专注） | 需持久化字段（可用 world_flags 过渡） |
| 🟡 中 | 稳定后 1d4 小时自动苏醒未实现（现需治疗才能起身） | 需游戏时间调度钩子 |
| 🟡 中 | XP 自动获取未接入（现仅里程碑升级） | 需遭遇结算钩子 + Character.xp 字段 |
| 🟡 中 | 施法成分 V/S/M 未在 graph 路径强制（engine.cast_spell 已有，但 LLM 无法可靠提供空手/法器状态） | 需装备槽位系统 |
| ⚪ 低 | 弹药消耗/双持/距离射程检查/负重/状态自动解除/种族特性/多人物品转移 | 位置/时间系统不完善，LLM 叙事层现阶段代管 |

## 问题处理流程模板

```
问题标题：
问题描述：
出现环境：本地 / 测试 / 生产
相关分支：
报错截图：
复现步骤：
期望结果：
实际结果：
已尝试方式：
优先级：高 / 中 / 低
```
