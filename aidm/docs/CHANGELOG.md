# CHANGELOG — 变动日志

> **记录"做了什么变动"**。倒序（最新在上）。每条尽量带 `文件:位置` 引用，便于回溯。
> 维护时机：每次改代码 / 改文档 / 建库 / 跑通验收后追加一条。
> 配套 `DECISIONS.md`（发现与决策）、`docs/README.md`（索引）。

## 变动分类图例

- `Added` 新增文件/功能/语料
- `Changed` 修改既有行为
- `Fixed` 修复
- `Docs` 文档变动
- `Build` 建库/依赖/部署
- `Verified` 验收/自检通过

---

## [Unreleased] · 进行中

### 2026-07-15 · 全模块完整性审查 + 规则书对照验证

- `Added` 新建 `scripts/test_all_modules.py`（全模块功能验证脚本，63项测试）。
- `Verified` **全模块功能验证通过（63/63）**。编写 `scripts/test_all_modules.py` 系统性测试脚本，覆盖 8 个引擎模块、10 个数据模块、15 个大脑模块、2 个 API 模块、2 个统计模块、7 个知识库模块。所有模块导入成功、核心功能验证通过。
- `Verified` **规则书对照验证通过（14项核心规则点）**。逐条对照 D&D 5E 规则书验证代码实现正确性：
  - R-CHK-025: d20骰子范围[1,20] ✓
  - R-CHK-024: 属性调整值 floor((score-10)/2) ✓
  - R-CHK-004/005: 优势取高/劣势取低/同时存在抵消 ✓
  - R-CMB-029: 重击伤害骰翻倍(常数不加倍) ✓
  - R-CMB-022/023: 天然20必命中+重击/天然1必失手 ✓
  - R-CMB-004: 回合动作经济(1动作/回合) ✓
  - R-CMB-001: 一轮=6秒 ✓
  - R-SPL-020: 专注豁免DC=max(10,floor(dmg/2))至高30 ✓
  - R-SPL-002/003: 法术位消耗与恢复(5级=4/3/2) ✓
  - PHB第五章专长分类(起源10/通用43/战斗风格9/传奇恩惠12=74个) ✓
  - DMG第七章魔法物品稀有度(普通16/非普通11/珍稀3=30个) ✓
  - DMG第八章据点系统(特色设施29/基础设施6/事件11) ✓
  - DMG第六章宇宙学(29个位面) ✓
  - PHB基础数据(种族10/职业12/背景16) ✓
- `Docs` 本次审查确认：**所有模块均为完整实现，无空文件或存根**。之前子智能体已完成全部工作，包括专长系统(74个)、魔法物品系统(30个+同调/鉴定)、冒险创建工具(adventure_builder.py+campaign_manager.py)、据点系统(29种设施+11种事件)、宇宙学(58个位面+位面旅行)。多人同玩架构(python-socketio)也已落地。
- `Docs` DECISIONS 新增 D-020（全模块完整性审查 + 规则书对照验证），记录审查方法、结论和验证结果。

### 2026-07-14

- `Docs` 订正 ARCHITECTURE.md → v3：§0 文档索引补 4 新档+进展校准；§5.1 RAG 改三语料/Qdrant本地/bge-small/hybrid/别名/评测；§5.4 编排补 brain/graph 节点流+MemorySaver；§5.5 交互层补 cli.py+api/main；§6 数据模型对齐 models.py（rule_chunk→Qdrant、Character 字段、current_index/active/exhaustion/死亡计数）；§7 选型订正（Qdrant本地/bge-small/deepseek）；§8 目录补 knowledge9模块/brain graph/api/cli/config.py/docs新档；§9 阶段表统一 P0-P5 划分+状态列；§10 待确认标已落地。依据 D-001~D-012。 `aidm/docs/ARCHITECTURE.md`
- `Docs` 订正 BUILD.md：§1 环境去 docker；§3 结构补实际模块；§4 自检补 P0-P4 入口；§5 P2 路径订正(scripts→knowledge)+部署去 docker；§5 P3 prompts.py→内嵌+MemorySaver；§5 P4 端点订正；§6 config.yaml→config.py/.env。 `aidm/docs/BUILD.md`
- `Changed` DECISIONS D-008 状态 🟡→✅（brain/graph.py 已落地，P3 完成；核对期间项目被推进，见 D-013）。
- `Added` DECISIONS D-013（核对期间项目被推进：graph.py/api/main/cli.py 落地、§0 自更新，订正基线变化）。
- `Docs` DECISIONS D-009 补充：经 graph.py 验证，ability_check 的 proficient 由 LLM classify 给出（设计取舍），非纯遗漏。
- `Docs` 新建本档（CHANGELOG）、`DECISIONS.md`、`docs/README.md`，建立"变动 + 发现"双轨记录体系。
  背景：核对发现现有架构文档多处落后于代码（详见 `DECISIONS.md` 2026-07-14 各条），需一个常更载体把变动与发现持续落进去。
  `aidm/docs/CHANGELOG.md` · `aidm/docs/DECISIONS.md` · `aidm/docs/README.md`

---

## 维护约定

1. **日期分组**：同一天的多条变动并列，不重复写日期头。
2. **倒序**：新条目加在 `## [Unreleased]` 下、日期小节顶部。
3. **带引用**：能定位到 `文件:行` 或 `规则: R-XXX-NNN` 就带上，方便回溯。
4. **不发版也记**：项目未正式发版，用日期即可；将来若发版可加 `## [vx.y.z] - 日期` 锚点。
5. **与 DECISIONS 的边界**：CHANGELOG 记"做了什么"（动作）；DECISIONS 记"为什么这么做 / 发现了什么 / 待办"。一次改动可能两边都留痕：改动落 CHANGELOG，背后的判断/发现落 DECISIONS。
