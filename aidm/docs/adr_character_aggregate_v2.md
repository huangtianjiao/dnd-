# ADR — CharacterAggregate v2：角色状态单一权威（设计稿）

> 状态: **Accepted（改造方案 v1.0 §5 / 第21节任务5）**
> 日期: 2026-08-14
> 关联规则: R-DRV-001 / R-GRC-001 / R-RSM-001

## 背景

当前 `stats/models.Character` 单表保存角色全部状态，字段同时承担
canonical state、derived state 与 legacy 兼容三职责；`class_levels`/
`feats`/`skill_prof` 等以 JSON 字符串落盘，来源不可解释（无法回答
"该专长来自职业升级还是背景授予"）。改造方案 §5 要求：

- Canonical State 与 Derived State 分离；
- Grant/Choice/Resource/SpellSource/MasteryGrant 成为持久化 provenance；
- 单一 DerivedStats 服务，缓存允许但不成为第二权威。

## 决策

### 1. 字段三分类（Character 表演进，不改表名）

| 分类 | 字段示例 | 策略 |
| ---- | -------- | ---- |
| **Canonical State** | abilities、class_levels_json、resource_pools、equipment（items_structured）、conditions、hit_dice、death_saves、gold | 持久化，事务修改；保存后不可从其他字段可靠重建 |
| **Provenance** | CharacterGrant / CharacterChoice 表（§5.3）、feats/spells/masteries 的来源记录、ruleset_revision | 持久化，支持解释/迁移/重建（本轮已落表：`charactergrant`/`characterchoice`） |
| **Derived State** | hp_max、ac、speed、proficiency、spell save DC、资源上限 | 由 `build.derive_stats` 唯一推导；落库仅为便捷查询（派生缓存），客户端提交被忽略；recompute 入口必须收敛到该服务 |
| **Ephemeral State** | reaction window、单次 action resolution 中间值 | 战斗/事务上下文，必要时 checkpoint；不落库为权威 |

### 2. 当前字段迁移归类清单（对照 models.Character 现有字段）

| 现有字段 | 归类 | 本轮动作 |
| -------- | ---- | -------- |
| abilities_json / class_levels_json / level / xp | Canonical | 保留 |
| spell_slots_json / known_spells_json | Canonical（待 P7 拆 known/prepared/spellbook） | 保留，P7 拆分 |
| feats_json / skill_prof_json | Canonical + Provenance 缺口 | 本轮新增 `charactergrant`/`characterchoice` 表补齐来源（R-GRC-001） |
| hp_max / hp_current / ac / speed | Derived（hp_current 为 canonical current） | 已由 `apply_server_stats` 强制覆写（P1-01） |
| inventory / items_structured | Canonical（inventory 权威，structured 派生视图） | 已有 sync_inventory_views 收敛（P1-10） |
| conditions / concentration / exhaustion | Canonical（生命/状态机 P6 统一 HealthService） | 保留 |
| class_canonical_id | Canonical（稳定引用） | 保留 |

### 3. 规则模式与版本不可变（§2.1/§2.2）

- Campaign 固化 `ruleset_id / ruleset_revision / mechanics_baseline / rules_mode`
  （原始模式 RAW_2024 默认；未知模式拒绝创建——fail closed）；
- House Rule 只允许经 `house_rule_pack` 显式记录，不允许散落 if/else；
- 本轮完成：Campaign 列迁移 002 + RulesetManifest v2 字段 + store 层校验。

### 4. 事务边界（§3.4）

所有机械状态变更走 application-level transaction：
load aggregate → 校验 auth/expected_version → 规则验证 →
deterministic 解析 → state changes → invariant 校验 → 原子持久化 →
ResolutionTrace。本轮先落持久化基础设施（provenance 表 + 幂等写入），
服务层编排在 P3-P6 逐阶段接入。

## 后果

- 正向：状态可解释（provenance）、可重建（derived 重算）、可迁移（版本化）；
- 代价：创建/升级/休息路径需逐步迁移到新事务（P3-P6），期间
  旧路径与 provenance 并存，由 schema_revision 与 edition regression 门禁约束；
- 风险：双写期间 provenance 缺失——按 §14.2 分类标记
  NEEDS_PLAYER_CONFIRMATION，绝不静默伪造来源。

## 完成定义（本轮 P0/P1 部分）

- [x] CharacterGrant/CharacterChoice 持久化 schema 与幂等写入（R-GRC-001）
- [x] RulesetManifest v2 字段 + Campaign rules_mode/mechanics_baseline + 迁移 002（R-RSM-001）
- [x] derive_stats 唯一入口锁定测试（save→reload 一致、客户端值忽略，R-DRV-001）
- [ ] P3: CharacterBuilder 统一创建（所有入口共用 builder 与 provenance 写入）
- [ ] P4: 12 职业 canonical progression（Fighter 垂直样板）
- [ ] P5: FeatEntitlementService（删除全局 FEAT_LEVELS 生产路径）
- [ ] P6: 资源/休息/生命 HealthService 事务化