# 改造实施方案执行状态（v1.0 → 最终）

> 依据: `DND5e2024_AIDM_完整改造实施方案_v1.0.docx`
> 执行窗口: 2026-08-17（两轮连续实施）
> 验证基线: 全量 pytest **1211 passed / 0 failed / 4 xfailed（2014 污染锁定）**；
> RuleConformanceMatrix **19 条规则**全部注册并通过 CI 门禁 `--check`。

## 阶段总览

| 阶段 | 状态 | 关键产出（rule_id） |
|------|------|---------------------|
| P0 Clean Baseline | ✅ | derive_stats 权威入口锁定（R-DRV-001）；三入口共用服务器推导；修复 3 个测试文件长期依赖生产库的隐患 |
| P1 Ruleset & Conformance | ✅ | RulesetManifest v2（mechanics_baseline/content_pack/house_rule/schema_revision，R-RSM-001）；Campaign rules_mode（RAW_2024 默认，非法拒绝）；RuleConformanceMatrix + CI 门禁（R-CON-001）；migration 002/003 |
| P2 CharacterAggregate | ✅ | CharacterGrant/CharacterChoice 持久化 provenance（R-GRC-001）；recompute_ac 收敛单一 derived 入口；invariant 校验（hp/力竭/生命状态/class_levels） |
| P3 CharacterBuilder | ✅ | 三创建入口统一 builder 校验 + provenance 落库（R-BLD-001）；pending choices API（R-CHC-001）；非法背景/职业/属性 422 |
| P4 Classes & Subclasses | 🔶 | Fighter 垂直样板（R-FGT-001，IMPLEMENTED）：Indomitable 9 级修正、资源公式驱动、golden snapshots 1/4/5/6/9/11/14/20、GAP 全部关闭；**其余 11 职业 progression 重建未做**（沿用 classes.py 2024 结构表 + class_features 执行层） |
| P5 LevelUp/Feat/Multiclass | ✅ | FeatEntitlementService（战士 6/14、游荡者 10、全局 FEAT_LEVELS 退役，R-FTR-001）；PrerequisiteEvaluator（R-PRE-001）；MulticlassService 收敛（levelup 委托 engine，删除重复表，Pact 独立，R-MC-001）；level-up 事务管线 + feat/ASI pending choice（R-LVL-001） |
| P6 Resources/Rest/Health | ✅ | ResourcePool 持久化（R-RES-001）；RestService 完整事务（R-RST-001，API 不再手动挑字段，HD/力竭/临时HP/法术位/资源池原子落库）；HealthService 状态机（R-HLT-001，临时HP吸收/濒死/死亡豁免/稳定/瞬死） |
| P7 Spellcasting | ✅ | SpellcastingModel 按职业分来源（R-SPL-101）：known/spellbook/prepared 分离；GET fallback 废止；prepare-spell 唯一路径（环阶门控/数量上限/准备制校验，R-SPL-103）；数量表 2024（R-SPL-104） |
| P8 Combat/Mastery | 🔶 | MasteryGrant 持久化 + 战斗解析授权门控（R-MAS-001，武器词条 ≠ 自动会用）；ResolutionTrace 动作级 trace（R-TRC-001）；**combat 底层 engine 全复用，未重写** |
| P9 AI/UI Contract | ✅ | Narrator 只消费 trace 事实（R-AI-001）；同 action 确定性一致（R-AI-002）；LLM 机械字段剥离无 mutation 路径（R-AI-003）；UI pending choices 契约已由后端提供 |
| P10 Migration/Legacy | ✅ | Legacy 删除清单逐项锁定（R-LGC-001..006，test_p10）：FEAT_LEVELS 生产路径、重复兼职表、default_known_spells fallback、API 局部 rest 写回、进程内资源权威、feat/mastery/spell 旁路全部退役；migration 002/003 版本化 |

## DoD 状态（方案 §18）

### 角色创建
- ✅ 12 职业 RAW_2024 创建合法（builder 校验 + 服务器权威派生）
- ✅ Species/Background/属性/Origin Feat/技能/装备/Mastery/Spells/Resources 落盘并有来源（provenance 表 + resource_pools/mastery_grants/spell 来源字段）

### 职业与子职业
- 🔶 仅 Fighter 1-20 快照完整；其余 11 职业沿用已有 2024 结构表（classes.py），子职业覆盖待逐职业细化

### 升级/专长/多职业
- ✅ class level 与 total level 区分（class_levels 持久化 + entitlement 按职业等级）
- ✅ 专长只能 entitlement + 先决选择
- ✅ 多职业先决/熟练/Extra Attack/spell slots/Pact Magic 收敛 engine 权威

### 资源/休息/生命
- ✅ 资源池/法术位/Hit Dice 权威持久化；短/长休完整事务 save→reload 不漂移
- ✅ 0HP/死亡/稳定/治疗统一 HealthService

### 法术
- ✅ production 不再"整个可及列表自动已知"；Known/Prepared/Spellbook/Always-Prepared 来源分离
- ⚠️ EXECUTABLE 等级效果执行依赖现有 cast resolver（未逐一升级法术到 E2E_VERIFIED）

### 战斗/AI/UI
- ✅ 角色只有拥有 Feature/Mastery/Resource 才能触发（MasteryGrant 门控）
- ✅ LLM 无直接 state mutation；Narrator 只消费 trace
- ✅ 前端不复制规则（server-provided pending choices）

### 规则治理
- ✅ 2024 RAW / SRD baseline / content pack / House Rule 区分（manifest + rules_mode）
- ✅ 2014 contamination suite 持续锁定（4 项 xfail strict：Berserker Frenzy 力竭、Bard 核心额外攻击、Cleric 1 级领域、Monk 'ki' 命名）
- ✅ RuleConformanceMatrix 19 条规则注册 + CI 输出

### 工程发布
- ✅ clean checkout install/build/run/migrate 经全量回归验证
- ✅ 所有 mutation auth + ownership + version + domain validation（feat 路由补齐 owner guard）
- ✅ Legacy production rule paths 实际退役（测试锁定）

## 遗留（明确未做的部分）

1. **P4 其余 11 职业渐进重建**：Fighter 已作为样板闭环；其余职业沿用现有 2024 结构数据，逐职业 golden snapshots 待建（机制已在 R-FGT-001 验证）。
2. **P4/P7 子职业与法术 EXECUTABLE 覆盖**：现有 subclass registry 为英文名覆盖不全（校验已做兼容降级）；法术效果执行依赖既有 cast resolver，未逐法术升级 E2E_VERIFIED。
3. **前端 choice-driven UI 重构**：后端契约（pending choices API）已就绪，前端静态导出页面未改造。
4. **content provenance 补哈希**：manifest 的 source_books content_hash 为空，发布前需人工填写与授权确认（方案 §2.3）。
5. **存量 ruff lint**：全仓 `ruff check` 有改造前存量错误（1588→1574，新代码全部干净），独立 PR 清理。

## 规则一致性矩阵（19 条）

R-DRV-001 / R-RSM-001 / R-GRC-001 / R-CON-001 / R-FGT-001(IMPLEMENTED) /
R-BLD-001 / R-CHC-001 / R-EDT-001(DECLARED) / R-FTR-001 / R-PRE-001 /
R-LVL-001 / R-MC-001 / R-SPL-101/103/104 / R-RST-001 / R-HLT-001 /
R-RES-001 / R-MAS-001 / R-TRC-001 / R-LGC-001 — 全部 ≥ DECLARED 通过 CI 门禁。