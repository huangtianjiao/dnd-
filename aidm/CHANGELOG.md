# Changelog

本文件面向用户/发版的精简变更记录。开发级详细变更（含文件:行引用、规则点 ID）见 [docs/CHANGELOG.md](docs/CHANGELOG.md)。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/)，版本号遵循语义化版本。

## [Unreleased]

## [0.3.0] - 2026-07-15

D&D 5E 电子跑团系统首个完整版本：确定性规则引擎 + LLM 叙事 + RAG 检索 + 三层记忆 + 多人同桌。

### 新增 — 规则引擎（P0 ✅）
- 骰子引擎：`secrets` 密码学随机，骰子表达式解析，优劣势，重击骰翻倍
- 检定系统：属性检定/豁免/攻击命中，范例 DC 表，天然 20/1
- 伤害系统：免疫→修正→抗性→易伤管线，临时 HP，死亡豁免完整周期
- 战斗状态机：先政/回合/动作经济/移动/体型空间/专注维持
- 施法引擎：法术位/成分校验/升环/效应结算
- 15 种状态条件 + 力竭累加 + 专注打断
- 机会攻击与 11 种战斗动作分派

### 新增 — 状态持久化（P1 ✅）
- SQLModel + SQLite：Character/Campaign/Scene/CombatState/Log 五表
- NPC 持久化：NPCProfile + NPCMemory + 关系演化（stats/npc.py）
- Checkpoint/Rewind：JSON 快照存档/读档/回退（stats/checkpoint.py）

### 新增 — RAG 知识层（P2 ✅）
- Qdrant 三集合：data.js 6238 条 + rules_text 141 页 + RULE_SPEC 400 条结构化规则点
- 混合检索：BM25（字符级）+ 向量，RRF 倒数排名融合
- 中文别名富化，保证"玩家词↔规则原词"稳定命中
- 评测 recall@3 = 100%

### 新增 — LangGraph 编排（P3 ✅）
- 8 节点判定链：classify→retrieve→verify→[retrieve_retry/confirm]→resolve→narrate→apply
- HITL interrupt/resume（DM 关键判定暂停）+ MemorySaver checkpointer
- 8 种 action_type 硬性骰子分派（attack/cast/ability_check/start_combat/end_combat/rest/social/levelup/travel）
- 三层记忆系统：工作记忆（近 6 回合）+ 中期 rolling_summary + 长期 Qdrant 语义记忆（Generative Agents 三分量评分）
- 19 个业务模块：探索/升级/战利品/据点/位面旅行/社交/Session0/房间/角色创建…

### 新增 — 多智能体（agents/）
- Director / RuleJudge / Narrator / CombatEngine / WorldManager / EnemyAI（渐进迁移中）

### 新增 — API 层（P4 ✅）
- FastAPI 43 个 REST 端点（战役/角色/对话/HITL/专长/魔法物品/据点/房间…）
- python-socketio WebSocket 同桌：Colyseus 风格 Room 生命周期，一人掷骰全员可见

### 新增 — 前端（P5 ✅）
- Next.js 14 + Tailwind + @3d-dice/dice-box 3D 骰子
- 静态 HTML 备用前端（XSS 安全重构版）

### 规则数据
12 职业 / 10 种族 / 16 背景 / 74 专长 / 30 魔法物品 / 29 据点设施 / 58 位面 / 12 法术

### 测试
8 个测试文件 ~138+ 用例全通过，覆盖引擎规则正确性 + API 端点 + 端到端流程

### 安全修复
- 修复静态前端 innerHTML XSS（引入 esc() 转义 + textContent）
- 修复前端 API 端口配置与后端不一致
- 修复 `/loot/distribute` 路由重复定义冲突

## [0.2.0] - 2026-07-14
- 集成休息/社交/升级/探索动作到 LangGraph 编排链
- 新增怪物图片资源与前端交互原型
- 骰子动画库调研与集成

## [0.1.0] - 2026-07-13
- 项目初始化：D&D 桌面角色扮演项目骨架
