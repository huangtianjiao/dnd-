# 改造计划 v2：按完整游玩流程重构 AI DM

> 基于 `DND5e完整游玩流程深度调研报告.html`（11阶段交互级解析）+ `DND5e完整游玩流程指南.html`（12章含全部核心公式与数值表）综合编写。
> 两份文档互补：调研报告定义了"为什么这么做"和DM/玩家交互细节；指南提供了"具体怎么做"的公式表、职业数据、骰子标识等可直接代码化的内容。

## 一、两份文档的合并映射

| 指南章节 | 调研报告章节 | 合并后的系统模块 |
|----------|-------------|-----------------|
| Ch1 游戏概览与基本循环 | §1 三大支柱 | `brain/graph.py` 核心循环 |
| Ch2 Session Zero | §2 Session 0 | `brain/session0.py` |
| Ch3 角色创建：五步车卡法 | §3 角色创建流程 | `brain/char_create.py` + `data/classes.py` + `data/races.py` + `data/backgrounds.py` |
| Ch4 核心机制：D20检定系统 | §4 核心游戏循环 | `engine/check.py` + `engine/dice.py` |
| Ch5 探索：旅行、视野与光照 | §6 探索流程 | `brain/exploration.py` |
| Ch6 交涉：社交互动 | §7 社交互动流程 | `brain/social.py` |
| Ch7 战斗系统全流程 | §5 战斗流程 | `engine/combat.py` 扩展 |
| Ch8 伤害、治疗与死亡 | §10 濒死与死亡 | `engine/damage.py` 扩展 |
| Ch9 施法系统详解 | §8 施法流程 | `engine/spells.py` 新建 |
| Ch10 休息与恢复 | §9 休息机制 | `brain/rest.py` 新建 |
| Ch11 升级与成长 | — | `brain/levelup.py` 新建 |
| Ch12 速查表 | — | `RULE_SPEC.md` 已覆盖 |

## 二、现状 vs 目标

| 阶段 | 报告/指南定义 | 当前实现 | 差距 |
|------|-------------|---------|------|
| Session 0 | 基调校准/内容边界/规则后勤 | 无 | 全缺 |
| 角色创建 | 五步车卡法(职业→种族→属性→背景→阵营) | 硬编码战士Lv5 | 全缺 |
| 核心循环 | DM描述→玩家行动→DM判断掷骰→叙述→循环 | 有但粗糙 | 需细化 |
| D20检定 | 三步流程(掷d20→加调整值→比较DC/AC) | check.py有 | 基本够 |
| 探索 | 旅行步调/视野光照/躲藏机制 | 无 | 全缺 |
| 社交 | NPC态度(友好/冷漠/敌对)/两条途径(RP/检定) | 无 | 全缺 |
| 战斗 | 三步(确定位置→投掷先攻→执行回合)+15种状态 | 先政+回合推进 | 缺移动/动作经济/状态详情 |
| 伤害死亡 | 伤害计算/抗性易伤/死亡豁免/稳定伤势/击晕 | damage.py有 | 基本够，缺击晕 |
| 施法 | 法术环阶/法术位/成分/施法时间/距离/持续时间/专注 | cast有save_dc | 缺法术位消耗/成分检查/专注维持 |
| 休息 | 短休(1h)/长休(8h)→恢复HP/法术位/特性 | 无 | 全缺 |
| 升级 | XP表/升级五步骤/游戏四阶段(T1-T4) | 无 | 全缺 |

## 三、分阶段改造方案

### Phase A：Session 0（游戏前准备）

**新增文件**：`brain/session0.py`

**功能**（指南Ch2 + 报告§2）：
1. 基调选择：黑暗写实 / 高魔奇幻 / 政治阴谋 / 恐怖风格
2. 严肃度滑块：1-10（严肃剧情 ↔ 随性搞笑）
3. 内容边界：线（禁止话题）/ 纱（可存在但不详细描写）
4. 规则版本：2014 PHB / 2024 修订版
5. 升级方式：经验值（XP）/ 里程碑（Milestone）
6. 角色死亡处理：复活魔法是否容易获取
7. 安全词/禁忌话题

**数据模型扩展**（`stats/models.py` Campaign）：
```python
class Campaign(SQLModel, table=True):
    # ... 现有字段 ...
    tone: str = ""                    # 基调（黑暗/英雄/恐怖...）
    seriousness: int = 5              # 1-10 严肃度
    lines_json: str = "[]"            # 禁止话题列表
    veils_json: str = "[]"            # 模糊处理话题列表
    rule_version: str = "2024"        # 规则版本
    advancement: str = "milestone"    # 升级方式：xp/milestone
    death_policy: str = "standard"    # 死亡处理方式
```

**API**：
- `POST /campaign` 增加 Session 0 字段
- `GET /campaign/{id}/session0` 返回 Session 0 配置

**前端**：
- 主菜单"开始新游戏"后增加 Session 0 配置页
- 基调卡片选择 + 严肃度滑块 + 内容边界输入

---

### Phase B：角色创建流程（五步车卡法）

**新增文件**：`brain/char_create.py`, `data/classes.py`, `data/races.py`, `data/backgrounds.py`

**功能**（指南Ch3 + 报告§3）：按五步顺序实现完整角色创建

**第一步：选择职业（Class）**

12个核心职业，每个决定生命骰、主属性、复杂度：

| 职业 | 生命骰 | 主属性 | 复杂度 |
|------|--------|--------|--------|
| 🪓 野蛮人 | d12 | 力量 | 中 |
| 🎵 吟游诗人 | d8 | 魅力 | 高 |
| ✝️ 牧师 | d8 | 感知 | 中 |
| 🌿 德鲁伊 | d8 | 感知 | 高 |
| ⚔️ 战士 | d10 | 力量/敏捷 | 低 |
| 👊 武僧 | d8 | 敏捷+感知 | 高 |
| 🛡️ 圣武士 | d10 | 力量+魅力 | 中 |
| 🏹 游侠 | d10 | 敏捷+感知 | 中 |
| 🗡️ 游荡者 | d8 | 敏捷 | 低 |
| ✨ 术士 | d6 | 魅力 | 高 |
| 📕 魔契师 | d8 | 魅力 | 高 |
| 📖 法师 | d6 | 智力 | 中 |

**第二步：确定起源（Origin）**

起源 = 背景 + 种族 + 语言

10种种族：
- 🧝 精灵（黑暗视觉，擅长魔法）
- 🪨 矮人（毒素抗性，黑暗视觉）
- 🐉 龙裔（龙息武器）
- 🧌 侏儒（小体型，魔法抗性）
- 👤 人类（万金油，每天英雄激励）
- 😈 提夫林（地狱血统，火焰抗性）
- 😇 阿斯莫（天界血统）
- 🦶 半身人（小体型，幸运天赋）
- 🐗 兽人（力量天赋，凶猛冲锋）
- ⛰️ 歌利亚（大型体格，高海拔适应）

16种背景（每种给一个专长 + 两项技能熟练 + 一项工具熟练 + 起始装备）：
侍僧 · 农民 · 向导 · 商人 · 士兵 · 工匠 · 抄写员 · 智者 · 水手 · 流浪者 · 罪犯 · 艺人 · 警卫 · 贵族 · 隐士 · 骗子

**第三步：确定属性值（Ability Scores）**

三种生成方式：
1. **标准数列**：固定数值 15, 14, 13, 12, 10, 8，自由分配到六项属性。最快速、最平衡。
2. **随机生成**：投 4d6 弃最低，取三个骰子总和，重复六次。随机性高，可能很强或很弱。
3. **购点法**：27点自由分配。8花费0点，15花费9点。上限15。最公平的竞技开卡方式。

购点法花费表：

| 属性值 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|--------|---|---|----|----|----|----|----|----|
| 花费   | 0 | 1 | 2  | 3  | 4  | 5  | 7  | 9  |

背景属性加成：每个背景列出三项属性——将其中一项 +2、另一项 +1，或三项各 +1。无法将属性提升到 20 以上。

属性调整值 = (属性值 - 10) ÷ 2，向下取整

| 属性值 | 1 | 2-3 | 4-5 | 6-7 | 8-9 | 10-11 | 12-13 | 14-15 | 16-17 | 18-19 | 20 |
|--------|---|-----|-----|-----|-----|-------|-------|-------|-------|-------|----|
| 调整值 | -5 | -4 | -3 | -2 | -1 | 0 | +1 | +2 | +3 | +4 | +5 |

**第四步：选择阵营（Alignment）**

阵营由道德倾向（善良/中立/邪恶）和秩序态度（守序/中立/混乱）两轴交叉构成 3×3=9 种。

预设规则：玩家角色不属于邪恶阵营。

**第五步：丰富细节（Fill in Details）**

关键公式（指南Ch3 Step 5）：

| 项目 | 公式 |
|------|------|
| 1级HP | 职业生命骰面值 + 体质调整值 |
| 无甲AC | 10 + 敏捷调整值 |
| 先攻 | d20 + 敏捷调整值 |
| 熟练加值 | 1级时 +2，每4级提升 |
| 被动察觉 | 10 + 感知(察觉)检定调整值 |
| 近战攻击加值 | 力量调整值 + 熟练加值 |
| 远程攻击加值 | 敏捷调整值 + 熟练加值 |
| 灵巧武器攻击 | max(力量, 敏捷)调整值 + 熟练加值 |
| 法术豁免DC | 8 + 施法属性调整值 + 熟练加值 |
| 法术攻击加值 | 施法属性调整值 + 熟练加值 |

18项技能及对应属性：

| 力量 | 敏捷 | 体质 | 智力 | 感知 | 魅力 |
|------|------|------|------|------|------|
| 运动 | 特技 | — | 奥秘 | 驯兽 | 欺瞒 |
| — | 隐匿 | — | 历史 | 洞悉 | 威吓 |
| — | 巧手 | — | 调查 | 医药 | 表演 |
| — | — | — | 自然 | 察觉 | 游说 |
| — | — | — | 宗教 | 求生 | — |

**数据模型扩展**（`stats/models.py` Character）：
```python
class Character(SQLModel, table=True):
    # ... 现有字段 ...
    background: str = ""              # 背景
    alignment: str = ""               # 阵营
    ideal: str = ""                   # 理想
    bond: str = ""                    # 羁绊
    flaw: str = ""                    # 缺陷
    personality_traits: str = ""      # 性格特质
    skill_proficiencies_json: str = "[]"  # 技能熟练度列表
    tool_proficiencies_json: str = "[]"   # 工具熟练度列表
    languages_json: str = "[]"            # 语言列表
    cantrips_json: str = "[]"             # 戏法列表
    known_spells_json: str = "[]"         # 已知法术列表
    prepared_spells_json: str = "[]"      # 准备法术列表
    hit_dice_remaining: int = 0           # 剩余生命骰
    hit_dice_total: int = 0               # 总生命骰
    spellcasting_ability: str = ""        # 施法属性(INT/WIS/CHA)
    spell_save_dc: int = 0                # 法术豁免DC
    spell_attack_bonus: int = 0           # 法术攻击加值
    passive_perception: int = 10          # 被动感知
    inventory_json: str = "[]"            # 物品栏
    gold: int = 0                         # 金币
    xp: int = 0                           # 经验值
```

**职业数据表**（`data/classes.py`）：
```python
CLASSES = {
    "战士": {
        "hit_die": 10,
        "primary_ability": ["str", "dex"],
        "saving_throws": ["str", "con"],
        "skill_choices": ["运动", "历史", "威吓", "察觉", "生存"],  # 选3
        "armor_prof": ["轻甲", "中甲", "重甲", "盾牌"],
        "weapon_prof": ["简易武器", "军用武器"],
        "subclass_level": 3,
        "complexity": "low",
    },
    "法师": {
        "hit_die": 6,
        "primary_ability": ["int"],
        "saving_throws": ["int", "wis"],
        "skill_choices": ["奥秘", "历史", "洞悉", "医药", "宗教"],  # 选2
        "armor_prof": [],
        "weapon_prof": ["匕首", "飞镖", "投石索", "法杖", "轻弩"],
        "spellcasting": True,
        "spellcasting_ability": "int",
        "ritual_casting": True,
        "cantrips_known": 3,  # 1级
        "spells_known": 6,    # 1级（法师可准备 INT_mod + 等级 个）
        "spell_slots_1": 2,   # 1级时1环法术位
        "complexity": "medium",
    },
    # ... 其余10个职业 ...
}
```

**种族数据表**（`data/races.py`）：
```python
RACES = {
    "人类": {
        "ability_bonuses": {"str": 1, "dex": 1, "con": 1, "int": 1, "wis": 1, "cha": 1},
        "speed": 30,
        "languages": ["通用语"],
        "traits": ["英雄激励：每天获得一个英雄激励"],
        "size": "中型",
    },
    "精灵": {
        "ability_bonuses": {"dex": 2},
        "speed": 30,
        "languages": ["通用语", "精灵语"],
        "traits": ["黑暗视觉60尺", "敏锐感官", "出神4小时睡眠"],
        "subraces": ["高精灵", "木精灵", "卓尔精灵"],
        "size": "中型",
    },
    # ... 矮人/龙裔/侏儒/提夫林/阿斯莫/半身人/兽人/歌利亚 ...
}
```

**背景数据表**（`data/backgrounds.py`）：
```python
BACKGROUNDS = {
    "士兵": {
        "feat": "野蛮打击者",
        "skill_prof": ["运动", "威吓"],
        "tool_prof": ["骰子游戏", "陆上载具"],
        "equipment": ["徽章", "军衔", "骨骰", "背包", "绳索"],
        "feature": "军阶——军队中仍有认识你的人",
        "ability_options": ["str", "con", "cha"],  # +2/+1 或 各+1
    },
    "学者": {
        "feat": "学者",
        "skill_prof": ["奥秘", "历史"],
        "tool_prof": ["书法家工具"],
        "equipment": ["墨水瓶", "羊皮纸", "小刀", "书籍"],
        "feature": "学者——知道哪里能找到信息",
        "ability_options": ["int", "con", "cha"],
    },
    # ... 其余14个背景 ...
}
```

**API**：
- `GET /classes` — 返回可选职业列表（含生命骰/主属性/复杂度）
- `GET /races` — 返回可选种族列表（含属性加成/速度/特性/子族）
- `GET /backgrounds` — 返回可选背景列表（含专长/技能熟练/工具熟练/装备/特性）
- `POST /character/create` — 分步创建角色（step 1-5）
- `GET /character/{id}/sheet` — 返回完整角色卡

**前端**：
- 角色创建向导（多步骤表单）
- Step 1: 职业卡片网格（12个职业，显示生命骰/主属性/复杂度）
- Step 2: 种族卡片网格（10个种族，显示属性加成/速度/特性/子族）
- Step 3: 属性生成方式选择（标准阵列/点数购买/掷骰）+ 属性分配界面
- Step 4: 背景选择（16个背景，显示专长/技能熟练/工具熟练/装备/特性）
- Step 5: 阵营选择（3×3网格）+ 角色扮演细节（理想/羁绊/缺陷/性格特质）
- 最终预览：自动计算的衍生数值（HP/AC/先攻/熟练加值/被动察觉/攻击加值/施法数值）

---

### Phase C：核心循环细化

**修改文件**：`brain/graph.py`, `brain/world.py`

**功能**（指南Ch1 + Ch4 + 报告§4）：将核心循环从"单一聊天"细化为报告中的三步循环

**核心循环状态机**（指南Ch1）：
```
DM_DESCRIBE → PLAYER_ACT → DM_RESOLVE → DM_DESCRIBE → ...
```

**graph.py classify 节点改造**：
```python
def classify(state: GameState) -> dict:
    """LLM 意图分类 → 结构化 intent
    
    action_type（指南Ch7动作一览表 + Ch4三步流程）:
    - attack: 攻击检定（近战用力量/远程用敏捷/法术用施法属性）
    - ability_check: 能力检定（攀爬/潜行/说服等）
    - saving_throw: 豁免检定（被动反应危险）
    - cast: 施法
    - explore: 探索行动（搜索/检查/开门等）
    - social: 社交行动（对话/谈判/威胁等）
    - rest: 休息（短休/长休）
    - move: 移动（旅行/换区域）
    - other: 其他自由行动
    """
```

**resolve 节点改造**（指南Ch4三步流程 + Ch12速查表）：
```python
def resolve(state: GameState) -> dict:
    """根据 action_type 分派到对应的硬性骰子解决器
    
    核心公式（指南Ch12速查表）:
    - D20检定成功条件: d20 + 调整值 ≥ DC / AC
    - 熟练技能检定: d20 + 属性调整值 + 熟练加值
    - 非熟练技能检定: d20 + 属性调整值
    - 近战攻击加值: 力量调整值 + 熟练加值
    - 远程攻击加值: 敏捷调整值 + 熟练加值
    - 灵巧武器攻击: max(力量, 敏捷)调整值 + 熟练加值
    - 重击伤害: 所有伤害骰 × 2 + 属性调整值
    - 抗性: 伤害 ÷ 2（向下取整）
    - 易伤: 伤害 × 2
    - 伤害调整顺序: 数值修正 → 抗性 → 易伤
    - 死亡豁免: d20 ≥ 10 = 成功；3成功稳定，3失败死亡
    - 稳定伤势: DC 10 感知(医药)检定
    """
```

**narrate 节点改造**（指南Ch1基本游戏循环 + 报告§4核心循环三步）：
```python
def narrate(state: GameState) -> dict:
    """LLM 叙事 + 结构化状态变更 + 场景推进
    
    输出:
    - narration: DM 叙事（依据掷骰结果，不可改）
    - state_changes: 结构化状态变更 [{target, field, delta, reason}]
    - scene_update: 行动后场景叙事更新
    - action_options: 3个玩家下一步可做的行动选项（区分细节）
    - new_phase: 是否触发阶段切换（探索→战斗/社交→战斗等）
    """
```

---

### Phase D：战斗流程完善

**修改文件**：`engine/combat.py`, `brain/graph.py`

**功能**（指南Ch7 + 报告§5）：按报告实现完整战斗流程

**战斗三步**（指南Ch7）：
1. 确定位置（DM决定所有角色和怪物的位置，方格地图每格=5尺）
2. 投掷先攻（d20 + 敏捷调整值，由高到低排序，被突袭者在先攻检定上有劣势）
3. 执行回合（每回合约6秒游戏时间，可以：移动至多速度距离 + 一个动作）

**每回合可执行的内容**（指南Ch7表格）：

| 类型 | 每回合 | 说明 |
|------|--------|------|
| 动作（Action） | 1次 | 主要行动，从动作表中选择 |
| 附赠动作 | 0-1次 | 仅当特殊能力/法术明确允许时可用 |
| 反应（Reaction） | 0-1次 | 触发式行动，可在任何人的回合发生 |
| 移动（Movement） | 速度值 | 可拆分：走15尺→攻击→再走15尺 |
| 物件交互 | 1次 | 免费与一个物件交互（如开门、拔剑） |
| 交流 | 不限 | 简短说话/手势免费；长篇大论需要动作 |

**动作一览表**（指南Ch7）：

| 动作 | 说明 |
|------|------|
| ⚔️ 攻击 | 使用武器或徒手打击 |
| 🏃 疾走 | 获得等于速度的额外移动力 |
| 🚪 撤离 | 移动不引发借机攻击 |
| 🛡️ 回避 | 对你攻击有劣势，敏捷豁免有优势 |
| 🤝 协助 | 盟友的属性/攻击检定获得优势，或急救 |
| 🌿 躲藏 | 进行敏捷（隐匿）检定 |
| 💬 影响 | 魅力（欺瞒/威吓/表演/游说）或感知（驯兽）检定 |
| ✨ 魔法 | 施展法术、使用魔法物品或特性 |
| ⏳ 预备 | 设定触发条件，准备好后用反应执行 |
| 🔍 搜索 | 感知（察觉/求生）检定 |
| 📖 研究 | 智力（调查/奥秘/历史/自然/宗教）检定 |
| 🔧 操作 | 使用一个非魔法物件 |

**掩护（Cover）**（指南Ch7）：

| 掩护程度 | AC / 敏捷豁免加值 | 条件 |
|----------|-------------------|------|
| 半身掩护 | +2 | 另一个生物或遮挡约一半的物件 |
| 四分之三掩护 | +5 | 遮挡约四分之三的物件 |
| 全身掩护 | 无法被攻击 | 完全遮挡，不能被选作目标 |

多重掩护取最高值，不叠加。

**借机攻击（Opportunity Attack）**（指南Ch7）：
- 最常见的反应
- 当敌人离开你的触及范围（通常5尺）时，你可以消耗反应进行一次近战攻击
- 使用撤离动作可以避免引发借机攻击

**移动规则**（指南Ch7）：
- 📐 拆分移动：可将移动拆分到动作前后
- ⛰️ 困难地形：每尺移动需额外消耗1尺移动力。多个因素不叠加
- 🧎 俯卧倒地：爬起消耗一半速度
- 🚶 穿过生物：可穿过盟友/失能/微型生物。其他生物的空间视为困难地形

**15种状态（Conditions）**（指南Ch7）：

| 状态 | 效果 |
|------|------|
| 👁️ 目盲 | 攻击检定劣势，基于视觉的检定劣势。对目盲者的攻击有优势 |
| 💕 魅惑 | 不能攻击魅惑者。魅惑者对你进行社交检定有优势 |
| 👂 耳聋 | 失聪，基于听觉的检定劣势 |
| 😴 力竭 | 分6级，每级速度-5尺、属性检定/攻击/豁免-1。6级=死亡 |
| 😱 恐慌 | 不能自愿移向恐惧源。恐慌源在视线内时属性检定劣势 |
| 🤝 受擒 | 速度为0。攻击对受擒者有优势（非擒拿者攻击时） |
| 😵 失能 | 不能行动或反应。攻击对失能者有优势。豁免检定和敏捷检定失败 |
| 👻 隐形 | 攻击有优势，被攻击有劣势。察觉检定劣势对试图发现你者 |
| ⚡ 麻痹 | 失能+无法移动/说话。近战攻击对麻痹者有优势且为重击 |
| 🤢 中毒 | 攻击检定和属性检定劣势 |
| 🧎 倒地 | 唯一动作是爬起（消耗一半速度）。近战攻击对你优势，远程劣势 |
| 📜 石化 | 开始石化过程，完成后变为石头物件 |
| 🪢 束缚 | 速度为0。攻击检定劣势，敏捷检定劣势。对你攻击有优势 |
| 💫 震慑 | 失能+无法移动/说话。对你攻击有优势 |
| 💀 昏迷 | 失能+无法移动/说话/感知。丢下手中物品。倒地。攻击有优势。5尺内攻击为重击 |

**combat.py 改造**：
```python
@dataclass
class Combatant:
    cid: str
    name: str
    dex_mod: int = 0
    initiative: int = 0
    side: str = "player"
    is_player: bool = True
    surprised: bool = False
    # 回合经济
    action_used: bool = False
    bonus_action_used: bool = False
    reaction_used: bool = False
    free_interaction_used: int = 0
    concentrating_on: Optional[str] = None
    # 位置
    position: tuple[int, int] = (0, 0)  # 网格坐标
    speed: int = 30
    speed_remaining: int = 30
    # 状态
    hp_current: int = 0
    hp_max: int = 0
    ac: int = 10
    conditions: set = field(default_factory=set)
    exhaustion: int = 0
```

**战斗动作分派**（指南Ch7动作一览表 + Ch12常用动作速查）：
```python
COMBAT_ACTIONS = {
    "attack": "使用武器或徒手打击",
    "cast": "施展法术",
    "dash": "获得等于速度的额外移动力",
    "disengage": "移动不引发借机攻击",
    "dodge": "对你攻击有劣势，敏捷豁免有优势",
    "help": "盟友的属性/攻击检定获得优势",
    "hide": "进行敏捷（隐匿）检定",
    "influence": "魅力（欺瞒/威吓/表演/游说）或感知（驯兽）检定",
    "magic": "施展法术、使用魔法物品或特性",
    "ready": "设定触发条件，用反应执行",
    "search": "感知（察觉/求生）检定",
    "study": "智力（调查/奥秘/历史/自然/宗教）检定",
    "utilize": "使用一个非魔法物件",
}
```

**API**：
- `POST /combat/start` — 启动战斗（参战者列表 + 突袭判定）
- `POST /combat/action` — 执行战斗动作
- `GET /combat/{campaign_id}` — 获取战斗状态
- `POST /combat/end` — 结束战斗

**前端**：
- 战斗追踪器面板（先攻序列/当前回合/HP条/AC/状态标签）
- 战斗动作按钮组（攻击/施法/冲刺/脱离/闪避/协助/躲藏/预备/搜索/使用物品）
- 移动控制（网格地图点击移动 / 方向键移动）
- 借机攻击提示弹窗

---

### Phase E：探索流程

**新增文件**：`brain/exploration.py`

**功能**（指南Ch5 + 报告§6）：按报告实现完整探索流程

**旅行步调**（指南Ch5）：

| 步调 | 每分钟 | 每小时 | 每天 | 游戏效果 |
|------|--------|--------|------|----------|
| 快速 | 400尺 | 4里 | 30里 | 察觉/生存 + 隐匿检定均劣势 |
| 中速 | 300尺 | 3里 | 24里 | 隐匿检定劣势 |
| 慢速 | 200尺 | 2里 | 18里 | 察觉/生存检定优势 |

**视野与光照**（指南Ch5）：

| 光照等级 | 来源 | 效果 |
|----------|------|------|
| 明亮光照 | 白昼、火把、提灯 | 正常视物 |
| 微光光照 | 黎明/黄昏、满月月光 | 形成轻度遮蔽：基于视觉的察觉检定劣势 |
| 黑暗 | 夜晚户外、无灯地城 | 形成重度遮蔽：尝试看穿时陷入目盲状态 |

**特殊感官**（指南Ch5）：
- 👁️ 黑暗视觉：在微光/黑暗中可看到如同微光的景象，范围通常60尺
- 🌊 震颤感知：可感知震动，无视视觉遮蔽
- 🔮 真实视觉：可看穿一切幻象和遮蔽
- 🦇 盲视：无需视觉即可感知周围环境

**躲藏机制**（指南Ch5）：
- 执行躲藏动作，进行一次敏捷（隐匿）检定
- 结果对抗敌人的被动察觉
- 是否适合躲藏由DM决定（需要遮蔽物）
- 攻击后位置暴露（无论命中与否）

**exploration.py**：
```python
@dataclass
class ExplorationState:
    pace: str = "normal"           # fast/normal/slow
    roles: dict = {}               # {navigator: char_id, scout: char_id, ...}
    nav_dc: int = 15               # 导航DC（基于地形）
    current_location: str = ""     # 当前位置描述
    time_elapsed: int = 0          # 已用时间（分钟）
    resources: dict = {}           # {rations: N, water: N, torches: N, ...}
    encounter_table: list = []     # 随机遭遇表
    last_encounter_roll: int = 0   # 上次遭遇检定结果


PACE_TABLE = {
    "fast": {"per_min": 400, "per_hour": 4, "per_day": 30, "effect": "察觉/生存+隐匿均劣势"},
    "normal": {"per_min": 300, "per_hour": 3, "per_day": 24, "effect": "隐匿劣势"},
    "slow": {"per_min": 200, "per_hour": 2, "per_day": 18, "effect": "察觉/生存优势"},
}

LIGHTING_TABLE = {
    "bright": {"effect": "正常视物"},
    "dim": {"effect": "轻度遮蔽：基于视觉的察觉检定劣势"},
    "dark": {"effect": "重度遮蔽：尝试看穿时陷入目盲状态"},
}
```

**API**：
- `POST /explore/travel` — 旅行一天
- `POST /explore/dungeon-turn` — 地城探索回合
- `GET /explore/state/{campaign_id}` — 获取探索状态

**前端**：
- 探索面板（旅行步调选择/队伍职责分配/当前位置/已用时间/资源追踪）
- 地城探索面板（当前房间描述/可见出口/搜索按钮/检查按钮/使用物品按钮）
- 遭遇提示弹窗

---

### Phase F：社交互动流程

**新增文件**：`brain/social.py`

**功能**（指南Ch6 + 报告§7）：按报告实现完整社交互动流程

**NPC态度**（指南Ch6）：
- 😊 友好：乐于提供帮助，可能主动提供信息或资源
- 😐 冷漠：中立态度，需要说服才会配合
- 😠 敌对：会试图妨碍、攻击或拒绝合作

**两条途径**（指南Ch6）：
1. 🎭 角色扮演（RP）：由玩家决定角色如何思考、行动、发言。可用演出式（直接说台词）或描述式（描述角色行为）。DM根据NPC性格和角色行为决定反应。为NPC提供它想要的事物或利用其同情心、恐惧、目的，可能收获友谊或关键信息。
2. 🎲 属性检定：DM想让骰子发挥作用时，要求执行一次影响动作。考虑自己和队友的技能熟练——如欺骗卫兵用欺瞒，说服贵族用游说，恐吓犯人用威吓。

**social.py**：
```python
@dataclass
class NPC:
    name: str
    role: str                    # 身份/职业
    attitude: str = "neutral"    # friendly/indifferent/hostile
    knowledge: dict = {}         # {topic: info}
    goals: list = []             # NPC想要什么
    secrets: list = []           # NPC隐藏的信息
    cr: str = ""                 # 挑战等级（如果可战斗）


@dataclass
class SocialState:
    current_npc: Optional[NPC] = None
    conversation_history: list = []  # [{speaker, text, timestamp}]
    attitude_changes: dict = {}      # {npc_name: new_attitude}
    revealed_secrets: list = []      # 已揭示的秘密
    persuasion_dc: int = 15          # 当前说服DC（受态度影响）


SOCIAL_DC_MODIFIERS = {
    "friendly": -5,       # 友善态度降低DC
    "indifferent": 0,     # 冷漠态度无修正
    "hostile": +5,        # 敌对态度提高DC
}

ATTITUDE_THRESHOLDS = {
    "friendly_to_indifferent": 10,  # 连续失败次数
    "indifferent_to_hostile": 5,
    "hostile_to_indifferent": 15,   # 连续成功次数
    "indifferent_to_friendly": 10,
}
```

**API**：
- `POST /social/interact` — 社交互动
- `GET /social/state/{campaign_id}` — 获取社交状态

**前端**：
- 社交面板（当前NPC信息/态度指示器/对话历史/可用社交技能按钮）
- NPC态度可视化（友善/冷漠/敌对的颜色编码）
- 对话气泡式UI

---

### Phase G：施法流程完善

**新增文件**：`engine/spells.py`, `data/spells.py`

**功能**（指南Ch9 + 报告§8）：按报告实现完整施法流程

**法术环阶与法术位**（指南Ch9）：
- 法术分为 0-9 环。零环法术即戏法（Cantrips），可无限次施展。
- 法术位：施展一环或更高法术需消耗一个相应或更高环阶的法术位。长休恢复所有法术位。
- 仪式施法：带有"仪式"标签的法术可多花10分钟施法时间，不消耗法术位。必须准备了该法术。
- 升环施法：用更高环阶法术位施展低环法术时，该法术被视为更高环阶。部分法术升环后效果更强。
- 戏法：零环法术，无需法术位，可随意施展。随等级提升威力增加。

**每回合限施一道消耗法术位的法术**（指南Ch9）：
- 每个回合中，至多只能消耗一个法术位
- 不能在同一回合用动作消耗法术位施法后，再用附赠动作消耗法术位施另一道法术
- 但可以用附赠动作施戏法 + 动作施法术等组合，只要不违反此规则

**法术成分（Components）**（指南Ch9）：

| 成分 | 缩写 | 要求 |
|------|------|------|
| 言语 | V | 以正常音量咏唱咒文。被堵嘴或身处魔法性沉默区域时不能施带有V的法术 |
| 姿势 | S | 至少一只手做出固定手印或精巧动作 |
| 材料 | M | 需要一只空闲的手拿取材料。可用材料包或法器取代（除非材料有指定价格或会被消耗） |

**施法时间**（指南Ch9）：

| 施法时间 | 说明 |
|----------|------|
| 1个动作 | 最常见的施法时间，通过魔法动作施展 |
| 1个附赠动作 | 快速法术，仅在特殊能力允许时 |
| 1个反应 | 对触发条件的响应（如护盾术） |
| 1分钟或更久 | 需每个回合执行魔法动作 + 保持专注。失去专注则法术失败（但不消耗法术位） |

**施法距离**（指南Ch9）：
- 📏 距离：以尺数列出，如"60尺"、"120尺"
- 🤚 触碰：效应以施法者接触的事物为源点
- 🧍 自身：法术在施法者自身施展或从自身弥散

**持续时间**（指南Ch9）：
- ⚡ 立即：魔法只存在一瞬间，随后消散
- ⏱️ 持续时间段：如"1分钟"=10轮。只要未失能，可随时结束（无需动作）
- 🧠 专注：需保持专注。受到伤害需进行体质豁免（DC=10或伤害值的一半，取高），失败则法术中断

**施法核心公式**（指南Ch9 + Ch12速查表）：
```
法术豁免DC = 8 + 施法属性调整值 + 熟练加值
法术攻击加值 = 施法属性调整值 + 熟练加值
```

**准备法术**（指南Ch9）：

| 职业 | 何时可更换 | 更换数量 |
|------|-----------|----------|
| 吟游诗人/术士/魔契师 | 升级时 | 一个 |
| 牧师/德鲁伊/法师 | 完成长休时 | 任意 |
| 圣武士/游侠 | 完成长休时 | 一个 |

始终准备的法术（来自特性）不计入准备法术列表的数目限制。

**spells.py 数据表**：
```python
SPELLS = {
    "火球术": {
        "level": 3,
        "school": "塑能",
        "casting_time": "1动作",
        "range": "150尺",
        "components": "V,S,M",
        "duration": "立即",
        "concentration": False,
        "effect_type": "saving_throw",
        "save_ability": "dex",
        "damage": "8d6火焰",
        "upcast": "+1d6 per level above 3",
        "description": "...",
    },
    "魔法飞弹": {
        "level": 1,
        "school": "塑能",
        "casting_time": "1动作",
        "range": "120尺",
        "components": "V,S",
        "duration": "立即",
        "concentration": False,
        "effect_type": "automatic",
        "damage": "3d4力场",
        "upcast": "+1飞弹 per level above 1",
        "description": "...",
    },
    # ... 更多法术 ...
}
```

**API**：
- `GET /spells` — 返回可选法术列表
- `POST /cast` — 施法流程
- `GET /character/{id}/spellbook` — 返回角色法术书

**前端**：
- 法术书面板（已知法术列表/准备法术列表/戏法列表/法术位网格）
- 施法界面（选择法术 → 选择法术位等级 → 选择目标 → 施放）
- 集中法术指示器

---

### Phase H：休息机制

**新增文件**：`brain/rest.py`

**功能**（指南Ch10 + 报告§9）：按报告实现完整休息机制

**短休（Short Rest）**（指南Ch10）：
- 时长：1小时
- 条件：必须至少 1 HP
- 活动限制：不能做比阅读、交谈、进食、站岗更费力的事
- 收益：
  - 消耗生命骰恢复HP：投掷任意枚生命骰 + 体质调整值 × 投掷次数。每次投掷后可决定是否继续消耗。
  - 特殊特性恢复：某些职业特性在短休时恢复使用次数。

**长休（Long Rest）**（指南Ch10）：
- 时长：至少 8 小时
- 要求：至少 6 小时睡眠 + 至多 2 小时轻度活动
- 冷却：完成后须等待 16 小时才能再次长休
- 收益：
  - 恢复全部HP和所有已消耗的生命骰
  - HP上限被减少的也恢复原状
  - 被减少的属性值恢复原状
  - 力竭等级减少 1 层
  - 恢复所有法术位
  - 特殊特性在长休时恢复

**打断休息**（指南Ch10）：

| 打断条件 | 短休 | 长休 |
|----------|------|------|
| 投掷先攻 | 打断 | 打断 |
| 施展非戏法法术 | 打断 | 打断 |
| 受到任何伤害 | 打断 | 打断 |
| 1小时行走或体力劳动 | — | 打断 |

长休被打断的处理：如果在长休被打断前已休息至少1小时，可获得一次短休的增益。可以在被打断后立刻继续长休，但每被打断一次需额外休息1小时才能完成。

短休被打断：一次被打断的短休不会提供任何增益。

**rest.py**：
```python
def short_rest(character: Character, hit_dice_to_spend: int = 0) -> dict:
    """短休流程
    
    1. 检查条件（至少1小时，必须至少1HP）
    2. 花费生命骰恢复HP（每枚生命骰掷骰 + CON调整值 = 恢复量）
    3. 恢复职业特性（邪术师法术位/战士行动涌动/武僧真气/吟游诗人灵感/德鲁伊野性变身）
    
    返回: {hp_restored, hit_dice_spent, features_restored, time_elapsed}
    """


def long_rest(character: Character) -> dict:
    """长休流程
    
    1. 检查条件（至少8小时，其中至少6小时睡眠，最多2小时轻度活动）
    2. 检查限制（每24小时最多获益一次；开始长休时至少有1HP）
    3. 恢复所有HP
    4. 恢复已花费生命骰的一半（向下取整，至少1枚）
    5. 恢复所有法术位（除邪务师外的施法者）
    6. 恢复几乎所有职业特性
    7. 力竭等级-1
    
    返回: {hp_restored, hit_dice_restored, spell_slots_restored, features_restored, exhaustion_reduced, time_elapsed}
    """
```

**API**：
- `POST /rest/short` — 短休
- `POST /rest/long` — 长休
- `GET /character/{id}/hit_dice` — 获取角色生命骰信息

**前端**：
- 休息面板（短休按钮/长休按钮/生命骰掷骰界面/恢复结果展示）
- 休息确认弹窗
- 休息被打断弹窗

---

### Phase I：升级与成长

**新增文件**：`brain/levelup.py`

**功能**（指南Ch11）：按报告实现完整升级流程

**经验值与等级表**（指南Ch11）：

| 等级 | 所需XP（总计） | 熟练加值 | 游戏阶段 |
|------|---------------|----------|----------|
| 1 | 0 | +2 | T1 新手冒险者 |
| 2 | 300 | +2 | |
| 3 | 900 | +2 | |
| 4 | 2,700 | +2 | |
| 5 | 6,500 | +3 | T2 成熟冒险者 |
| 6 | 14,000 | +3 | |
| 7 | 23,000 | +3 | |
| 8 | 34,000 | +3 | |
| 9 | 48,000 | +4 | T3 力量超凡 |
| 10 | 64,000 | +4 | |
| 11 | 85,000 | +4 | |
| 12 | 100,000 | +4 | |
| 13 | 120,000 | +5 | |
| 14 | 140,000 | +5 | |
| 15 | 165,000 | +5 | |
| 16 | 195,000 | +5 | |
| 17 | 225,000 | +6 | T4 英雄典范 |
| 18 | 265,000 | +6 | |
| 19 | 305,000 | +6 | |
| 20 | 355,000 | +6 | |

**升级五步骤**（指南Ch11）：
1. 选择职业（大多数在同一个职业升级，也可使用兼职规则）
2. 修改生命值和生命骰（获得一个额外生命骰。投掷后 + 体质调整值（至少1）加到HP上限。也可使用固定值：野蛮人+7，战士/圣武士/游侠+6，诗人/牧师/德鲁伊/武僧/游荡者/魔契师+5，术士/法师+4（均+体质调整））
3. 记录新职业特性（查看职业表格，记录该等级获得的新特性）
4. 修改熟练加值（提升时，角色卡上所有含熟练加值的数值都相应提升）
5. 修改属性调整值（体质调整值每提升1，生命值上限额外再提升等于当前等级的点数）

**游戏四阶段（Tiers of Play）**（指南Ch11）：
- T1（1-4级）新手冒险者：面对村庄级别威胁，3级选择子职
- T2（5-10级）成熟冒险者：获得标志性法术（如火球术、额外攻击），面对城市与王国级危机
- T3（11-16级）力量超凡：力量远超普通冒险者，面对威胁整个地区的事物
- T4（17-20级）英雄典范：影响世界命运乃至多元宇宙秩序，9环法术可以改变现实

**levelup.py**：
```python
XP_TABLE = {
    1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500,
    6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000,
    11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000,
    16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000,
}

FIXED_HP_GAIN = {
    "野蛮人": 7, "战士": 6, "圣武士": 6, "游侠": 6,
    "吟游诗人": 5, "牧师": 5, "德鲁伊": 5, "武僧": 5, "游荡者": 5, "魔契师": 5,
    "术士": 4, "法师": 4,
}


def level_up(character: Character) -> dict:
    """升级流程
    
    1. 检查XP是否达到下一级
    2. 获得一个额外生命骰
    3. 增加HP上限（投掷生命骰 + CON调整值，或使用固定值）
    4. 记录新职业特性
    5. 修改熟练加值（如果跨过了+2/+3/+4/+5/+6的阈值）
    6. 修改属性调整值（如果适用）
    
    返回: {new_level, hp_gained, new_proficiency_bonus, new_features, ability_improvements}
    """
```

**API**：
- `POST /character/{id}/levelup` — 升级
- `GET /character/{id}/xp` — 获取经验值和等级信息

**前端**：
- 升级弹窗（显示新等级/新HP/新特性/新熟练加值）
- 升级动画（等级数字翻转/烟花效果）

---

## 四、实施优先级

| 优先级 | Phase | 说明 | 预估工作量 |
|--------|-------|------|-----------|
| P0 | Phase B | 角色创建流程（五步车卡法） | 大 |
| P0 | Phase C | 核心循环细化（最基础） | 中 |
| P0 | Phase D | 战斗流程完善（最常用） | 大 |
| P1 | Phase G | 施法流程完善（最复杂） | 大 |
| P1 | Phase H | 休息机制（最资源管理） | 小 |
| P1 | Phase I | 升级与成长（最成长感） | 中 |
| P2 | Phase E | 探索流程（最被忽视） | 中 |
| P2 | Phase F | 社交流程（最自由） | 中 |
| P3 | Phase A | Session 0（最前置） | 小 |

## 五、技术栈不变

- 后端：Python 3.12 + FastAPI + SQLModel + LangGraph
- LLM：deepseek-v4-flash（senseaudio 网关）
- 嵌入：本地 bge-small-zh（hf-mirror）
- 向量库：Qdrant 本地文件模式
- 前端：HTML 单页（FastAPI 托管）+ Next.js scaffold

## 六、数据流不变

```
玩家输入 → classify(LLM意图分类) → retrieve(hybrid检索规则) → verify(LLM校验) → 
[verify!ok→retrieve_retry] / [ok+HITL→confirm(暂停让DM确认)] → 
resolve(骰子,纯代码!) → narrate(LLM叙事) → apply(持久化+战斗轮次推进)
```

## 七、验收标准

每个 Phase 完成后需通过以下验收：

1. **功能完整性**：实现指南中定义的所有步骤
2. **硬性判定**：掷骰/数值/规则全走代码，LLM 不参与
3. **RAG 校验**：规则检索 + 参数校验，冲突驳回
4. **前端可用**：用户可通过界面完成完整流程
5. **API 文档**：所有新增 API 端点有文档说明
6. **单元测试**：核心逻辑有自检测试

## 八、风险与对策

| 风险 | 对策 |
|------|------|
| LLM 不稳定输出 | 强制 JSON schema + 重试 + 前端兜底 |
| Qdrant 本地模式并发限制 | asyncio.Lock 序列化（D&D 本来就是回合制） |
| 法术数据量大 | 分批导入 + 按需加载 |
| 角色创建步骤多 | 向导式 UI + 默认值 + 快速创建模式 |
| 战斗状态复杂 | 状态机管理 + 每步可审计回溯 |

## 九、时间线估算

| Phase | 预估时间 | 备注 |
|-------|---------|------|
| Phase A: Session 0 | 2-3h | 表单+配置存储 |
| Phase B: 角色创建 | 4-6h | 数据表+向导UI+衍生计算 |
| Phase C: 核心循环细化 | 3-4h | graph.py重构+action_type扩展 |
| Phase D: 战斗流程完善 | 4-6h | combat.py扩展+动作分派+借机攻击 |
| Phase E: 探索流程 | 3-4h | exploration.py新建+旅行/地城流程 |
| Phase F: 社交流程 | 3-4h | social.py新建+NPC交互+态度系统 |
| Phase G: 施法流程完善 | 4-6h | spells.py数据表+施法流程+法术位管理 |
| Phase H: 休息机制 | 2-3h | rest.py新建+短休/长休恢复 |
| Phase I: 升级与成长 | 3-4h | levelup.py新建+XP表+升级五步骤 |
| **总计** | **28-40h** | 约3-5个工作日 |

## 十、规则书回溯机制（编码必须参考规则书原文）

### 数据源层级

| 层级 | 来源 | 内容 | 用途 |
|------|------|------|------|
| L0 原始权威 | `5echm_web/topics/` 8644个HTML页 | 完整规则原文 | **编码时的最终参考** |
| L1 搜索索引 | `5echm_web/data.js` 6238条三元组 | 纯文本摘要(正文+标签+路径) | RAG检索语料 |
| L2 规则规格书 | `aidm/docs/RULE_SPEC.md` 400条结构化规则点 | 摘要+数值公式+出处+待实现函数 | 代码↔规则双向索引 |
| L3 提纯文本 | `aidm/data/rules_text/` 141页 | 从HTML提取的纯文本 | 审计/补充语料 |

### 编码流程（每个Phase都必须遵循）

```
1. 读 RULE_SPEC.md 找到对应规则点(R-XXX-NNN)和待实现函数签名
2. 按"出处"字段打开 5echm_web/topics/ 对应HTML原文
3. 对照原文实现代码（数值/公式/流程以原文为准）
4. 代码中标注 # 规则: R-XXX-NNN + 出处: topics/.../xxx.htm
5. 在 RULE_SPEC.md "实现回填区"记录实际函数位置
6. 写自检测试验证数值正确性
```

### 规则书目录结构（编码时按需查阅）

```
5echm_web/topics/
├── 玩家手册2024/          ← 核心规则（角色创建/战斗/施法/休息/升级）
│   ├── 创建角色/           ← Phase B 角色创建
│   ├── 进行游戏/           ← Phase C 核心循环
│   ├── 角色职业/           ← Phase B 职业数据
│   ├── 法术/              ← Phase G 施法
│   ├── 装备/              ← Phase B 装备
│   └── 专长/              ← Phase B 专长
├── 城主指南2024/          ← DM运作规则
│   ├── 2.运作游戏/         ← Phase C/D/E/F 运作规则
│   │   ├── 决定掷骰结果/   ← D20检定流程
│   │   ├── 运作战斗/       ← 战斗运作细节
│   │   ├── 运作探索/       ← 探索运作细节
│   │   └── 运作交涉/       ← 社交运作细节
│   └── ...
├── DM速查/                ← 速查表（DC表/状态表/掩护表/单位换算）
├── 术语汇编/              ← 术语定义（状态/效应区域/特殊感官等）
└── ...其他扩展书籍
```

### 关键规则书页面索引（编码时直接打开）

| Phase | 规则书页面路径 | 内容 |
|-------|---------------|------|
| B 角色创建 | `topics/玩家手册2024/创建角色/` | 五步车卡法每一步的详细规则 |
| B 职业数据 | `topics/玩家手册2024/角色职业/` | 12个职业的完整数据表(生命骰/熟练/特性/法术列表) |
| B 种族数据 | `topics/玩家手册2024/角色起源/` 或 `topics/玩家手册2024/多元宇宙/` | 10种种族的属性加成/速度/特性/子族 |
| B 背景数据 | `topics/玩家手册2024/角色起源/` | 16种背景的专长/技能熟练/工具熟练/装备/特性 |
| B 装备数据 | `topics/玩家手册2024/装备/` | 武器表/护甲表/冒险装备/工具/制作规则 |
| C 核心循环 | `topics/玩家手册2024/进行游戏/` | D20检定三步流程/优势劣势/三种检定类型 |
| D 战斗流程 | `topics/玩家手册2024/进行游戏/战斗.htm` + `战斗流程.htm` + `动作.htm` 等 | 战斗三步/回合经济/动作一览/掩护/借机攻击/移动规则 |
| D 15种状态 | `topics/术语汇编/状态.htm` + `状态与其他游戏状况.htm` | 每种状态的完整数值效应 |
| E 探索流程 | `topics/城主指南2024/2.运作游戏/运作探索/` | 旅行步调/导航检定/被动感知/随机遭遇/资源追踪 |
| F 社交流程 | `topics/城主指南2024/2.运作游戏/运作交涉/` | NPC态度/两条途径(RP/检定)/社交DC修正 |
| G 施法流程 | `topics/玩家手册2024/进行游戏/第七章：法术.htm` 或 `topics/玩家手册2024/法术/` | 法术环阶/法术位/成分/施法时间/距离/持续时间/专注/准备法术 |
| G 法术详述 | `topics/玩家手册2024/法术详述/` | 每个法术的完整描述(伤害/范围/豁免/升环) |
| H 休息机制 | `topics/玩家手册2024/进行游戏/休息.htm` 或 `topics/城主指南2024/` | 短休/长休的完整规则(时长/条件/收益/打断) |
| I 升级成长 | `topics/玩家手册2024/进行游戏/等级提升.htm` | XP表/升级五步骤/游戏四阶段 |

### 规则书回溯工具

已有工具可直接使用：

1. **HTML→纯文本提取器**（`scripts/extract_rules.py`）：
   ```bash
   # 提取某个规则页面的纯文本
   python scripts/extract_rules.py "topics/玩家手册2024/进行游戏/战斗.htm"
   ```

2. **RAG 检索**（`knowledge/indexer.py` + `hybrid.py`）：
   ```python
   # 语义检索规则书内容
   from aidm.knowledge import indexer, hybrid
   results = indexer.search("战斗回合动作经济", limit=5)
   # 或 hybrid 检索（BM25+向量RRF）
   results = hybrid.search_spec_hybrid("先攻投掷突袭", limit=5)
   ```

3. **RULE_SPEC.md 双向索引**：
   - 编码前：查 RULE_SPEC.md 找规则点 ID 和出处路径
   - 编码后：在"实现回填区"记录实际函数位置

### 编码时的注意事项

1. **data.js 摘要可能不完整**：data.js 是搜索索引的纯文本摘要，可能遗漏细节。编码时必须打开 `topics/` 下的 HTML 原文确认。
2. **规则书有版本差异**：`DM速查/` 目录的源文整体为 2014 版（含 EP、离散力竭表、武器表无精通、状态用"擒抱"等）。`玩家手册2024/` 目录的源文为 2024 修订版。编码时以 2024 版为准。
3. **规则书页面有 WinCHM 框架脚本**：`topics/` 下的 HTML 页面包含 `syn()` 等 WinCHM 框架脚本，提取纯文本时需要剔除。使用已有的 `extract_rules.py` 脚本即可。
4. **规则书页面之间有交叉引用**：例如战斗页面引用了状态页面，施法页面引用了法术详述页面。编码时需要跟踪这些交叉引用，确保实现的完整性。

---

## 十一、文档更新计划

每个 Phase 完成后更新以下文档：

1. **ARCHITECTURE.md**：新增模块的架构说明
2. **DECISIONS.md**：记录技术决策和设计选择
3. **RULE_SPEC.md**：回填实现函数签名和文件位置
4. **PRD.md**：更新功能需求和验收标准
5. **BUILD.md**：更新构建指南和依赖说明

---

## 十二、遗漏项补充（基于规则书原文审计）

### 12.1 专长系统（P0 — PHB 第五章 专长）

**规则书出处**：`topics/玩家手册2024/专长/` 下5个页面

**数据模型扩展**（`stats/models.py` Character）：
```python
feats_json: str = "[]"  # 已选专长列表
```

**新增文件**：`src/aidm/data/feats.py`

**功能**：
- 专长概述：专长是角色的特殊能力，在特定等级（4/8/12/16/19）获得
- 起源专长：来自背景的专长
- 战斗风格专长：战士/游侠/圣武士的战斗风格
- 通用专长：所有角色可选的专长
- 传奇恩惠专长：高等级传奇专长

**API**：
- `GET /feats` — 返回可选专长列表
- `POST /character/{id}/feat` — 选择专长

**前端**：
- 角色卡增加"专长"区域
- 升级时弹出专长选择对话框

---

### 12.2 魔法物品系统（P0 — DMG 第七章 宝藏）

**规则书出处**：`topics/城主指南2024/7.宝藏/` 下84个文件

**数据模型扩展**（`stats/models.py` 新增 MagicItem）：
```python
class MagicItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    rarity: str          # 普通/非普通/珍稀/极珍稀/传说/神器
    type: str            # 武器/护甲/奇物/戒指/卷轴/药水/法杖/权杖/魔杖
    attunement: bool     # 是否需要同调
    cursed: bool         # 是否诅咒
    description: str
    properties_json: str # "{}" 魔法属性
```

**Character 扩展**：
```python
attuned_items_json: str = "[]"  # 已同调物品（最多3个）
```

**新增文件**：`src/aidm/data/magic_items.py`, `src/aidm/brain/loot.py`

**功能**：
- 魔法物品稀有度系统：普通/非普通/珍稀/极珍稀/传说/神器
- 同调机制：最多同调3件，短休建立同调
- 鉴定机制：鉴定术或短休集中接触
- 诅咒物品：鉴定时不揭示诅咒
- 随机魔法物品生成表：器具表/圣物表/奥秘表/武备表
- 战利品分配：击败怪物后按CR分配战利品

**API**：
- `GET /magic-items` — 返回魔法物品数据库
- `GET /magic-items/{name}` — 查询特定魔法物品
- `POST /character/{id}/attune` — 同调魔法物品
- `POST /loot/generate` — 生成随机战利品

**前端**：
- 物品栏增加魔法物品标识（稀有度颜色边框）
- 同调管理面板（已同调3/3，可解除同调）
- 鉴定弹窗（未鉴定物品显示为"未知物品"）
- 战利品分配弹窗（击败怪物后自动弹出）

---

### 12.3 冒险创建工具（P1 — DMG 第四章 创建冒险）

**规则书出处**：`topics/城主指南2024/4.创建冒险/` 下31个文件

**新增文件**：`src/aidm/brain/adventure_builder.py`

**功能**：
- 冒险设计步骤：钩子→地点→遭遇→NPC→奖励→结局
- 导入玩家：冒险赞助者/巧合引子/超自然引子
- 布置背景：不同等级的冒险情景/冒险冲突/冒险设定
- 规划遭遇：交涉遭遇/战斗遭遇/探索遭遇/遭遇节奏和紧张感
- 冒险奖励：XP/金币/魔法物品/信息
- 结束冒险：收尾/悬念

**API**：
- `POST /adventure/create` — 创建自定义冒险
- `GET /adventure/{id}` — 获取冒险详情
- `POST /adventure/{id}/encounter` — 添加遭遇

**前端**：
- DM工具箱面板（冒险设计向导）
- 遭遇规划器（拖拽式遭遇编辑）
- 冒险地图编辑器（简化版）

---

### 12.4 据点系统（P1 — DMG 第八章 据点）

**规则书出处**：`topics/城主指南2024/8.据点/` 下35个文件

**数据模型扩展**（`stats/models.py` 新增 Stronghold）：
```python
class Stronghold(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int
    name: str
    map_json: str        # "{}" 据点地图
    facilities_json: str # "[]" 已建设施
    events_json: str     # "[]" 据点事件
    treasury: int        # 金库
```

**新增文件**：`src/aidm/brain/stronghold.py`

**功能**：
- 建立据点：选择地点/类型
- 据点回合：管理据点的周期性活动
- 据点地图：基础设施+25种特色设施
  - 仓库/传送法阵/公会大厅/兵营/军械库
  - 冥想间/剧院/动物园/半位面
  - 图书馆/圣器室/圣坛/圣所/圣物库
  - 天文台/奥术研究室/实验室/工坊
  - 抄写室/档案室/温室/游戏厅
  - 种植园/训练场/酒馆/铁匠铺/陈列室/马厩
- 据点事件：随机事件/入侵/访客
- 失去据点：被攻占/被摧毁

**API**：
- `POST /stronghold/create` — 建立据点
- `GET /stronghold/{campaign_id}` — 获取据点状态
- `POST /stronghold/build` — 建设设施
- `POST /stronghold/event` — 触发据点事件

**前端**：
- 据点管理面板（地图视图+设施列表）
- 建设菜单（可选择要建设的设施）
- 据点事件弹窗

---

### 12.5 多人游戏系统（P0 — WebSocket 实时同桌）

**规则书出处**：DMG 2.运作游戏/团队规模.htm + 运作交拟/态度.htm

**需求**：真正的多人在线跑团——一人行动全员实时收到 DM 叙事+骰子+场景更新

**已有基础**：`api/ws.py` ConnectionManager + WS端点 + 回合协调 + 广播

**需要补充的功能**：

#### 12.5.1 房间管理系统
**新增文件**：`src/aidm/brain/room.py`

**功能**：
- 创建房间：房主创建战役+设置密码
- 加入房间：输入房间号+密码+角色信息
- 房间状态：等待中/进行中/暂停中
- 玩家管理：踢出玩家/转让房主/查看在线玩家
- 观战模式：非玩家可以观战

**数据模型**（`stats/models.py` 新增 Room）：
```python
class Room(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int
    password: str = ""
    status: str = "waiting"   # waiting/playing/paused
    max_players: int = 6
    spectators_json: str = "[]"  # 观战者列表
```

**API**：
- `POST /room/create` — 创建房间
- `POST /room/join` — 加入房间
- `GET /room/{id}` — 获取房间状态
- `POST /room/{id}/kick` — 踢出玩家
- `POST /room/{id}/transfer` — 转让房主
- `WebSocket /ws/{campaign_id}` — 实时通信（已有）

#### 12.5.2 多人战斗协调
**修改文件**：`engine/combat.py`, `api/ws.py`

**功能**：
- 先攻序列共享：所有玩家看到同一个先攻序列
- 回合锁定：只有当前回合的玩家可以行动
- 行动广播：玩家A攻击→所有人看到攻击结果
- 怪物AI回合：DM控制怪物行动，所有玩家看到结果
- 反应协调：玩家B在玩家A的回合使用反应（如借机攻击）

**WebSocket消息类型扩展**：
```python
# 已有
join/leave/result/processing/player_acting/scene_update/combat_update/character_update/turn/error

# 新增
initiative_roll      # 玩家掷先政，全员可见
action_start         # 玩家开始行动
action_complete      # 玩家完成行动
monster_turn         # 怪物回合开始
monster_action       # 怪物行动结果
reaction_available   # 可以使用反应
reaction_used        # 反应已使用
round_end            # 一轮结束
combat_end           # 战斗结束
player_ready         # 玩家准备就绪
all_ready            # 所有玩家准备就绪
```

#### 12.5.3 多人探索协调
**修改文件**：`brain/exploration.py`, `api/ws.py`

**功能**：
- 队伍行进：所有玩家同步移动
- 队形管理：先锋/殿后/侧翼
- 被动察觉：每个玩家有自己的被动察觉值
- 发现共享：玩家A发现陷阱→所有人看到提示
- 分头行动：玩家可以暂时离开队伍单独探索

#### 12.5.4 多人社交协调
**修改文件**：`brain/social.py`, `api/ws.py`

**功能**：
- 对话顺序：DM控制谁先说话
- 态度共享：所有玩家看到NPC对队伍的态度
- 协助检定：玩家A说服时，玩家B可以协助（给予优势）
- 信息共享：玩家A从NPC获取的信息→所有人可见

#### 12.5.5 多人休息协调
**修改文件**：`brain/rest.py`, `api/ws.py`

**功能**：
- 同步休息：所有玩家同时进入短休/长休
- 生命骰独立：每个玩家独立决定消耗多少生命骰
- 法术位恢复：长休后所有玩家的法术位恢复
- 打断通知：如果有敌人打断休息，所有玩家收到警报

#### 12.5.6 多人战利品分配
**新增文件**：`src/aidm/brain/loot_distribution.py`

**功能**：
- 战利品池：击败怪物后生成战利品池
- 分配方式：
  - 需求优先：需要该物品的玩家优先
  - 轮流拾取：按先政顺序轮流选择
  - 点数分配：掷骰决定优先权
  - DM指定：DM直接指定归属
- 金币分配：平均分配或按贡献分配
- 分配记录：记录每次分配的结果

**API**：
- `POST /loot/pool` — 生成战利品池
- `POST /loot/distribute` — 分配战利品
- `GET /loot/history/{campaign_id}` — 获取分配历史

**前端**：
- 战利品分配弹窗（物品列表+分配按钮）
- 分配方式选择器
- 分配结果展示

---

### 12.6 宇宙学/位面旅行（P2 — DMG 第六章 宇宙学）

**规则书出处**：`topics/城主指南2024/6.宇宙学/` 下37个文件

**新增文件**：`src/aidm/data/planes.py`, `src/aidm/brain/plane_travel.py`

**功能**：
- 30个位面描述：物质位面/以太位面/星光位面/四大元素位面/外域/九层地狱/无底深渊等
- 位面旅行机制：位面传送门/法术传送/物理穿越
- 位面效应：不同位面的物理法则差异
- 位面居民：各位面的原住民和生物

**API**：
- `GET /planes` — 返回位面数据库
- `GET /planes/{name}` — 查询特定位面
- `POST /plane/travel` — 位面旅行

**前端**：
- 位面地图导航器
- 位面信息卡片

---

### 12.7 创作工具（P2 — DMG 第三章 地下城主工具箱）

**规则书出处**：`topics/城主指南2024/3.地下城主工具箱/` 下24个文件

**新增文件**：`src/aidm/brain/dm_toolbox.py`

**功能**：
- 创作法术：DM自定义法术
- 创作生物：DM自定义怪物
- 创作魔法物品：DM自定义魔法物品
- 危害系统：环境危害/陷阱
- 名望/声望系统
- 怪群设计
- 恐惧与精神压力
- 攻城装备
- 枪械与爆炸物
- 诅咒与魔法疫病
- 超自然赠礼
- 追逐规则
- 门机制
- 阵营系统
- NPC设计工具

**API**：
- `POST /dm/create-spell` — 创建自定义法术
- `POST /dm/create-monster` — 创建自定义怪物
- `POST /dm/create-item` — 创建自定义物品
- `GET /dm/toolbox` — 获取DM工具箱

**前端**：
- DM工具箱面板
- 自定义内容编辑器

---

## 十三、多人同玩架构升级方案

> 基于《多人同玩架构设计调研报告》制定。

### 13.1 推荐路线

| Phase | 目标 | 改动量 | 时间 |
|-------|------|--------|------|
| **Phase 1** | 用 `python-socketio` 替换裸 WebSocket，获得 Room/自动重连/消息缓冲 | 小（改 ws.py） | 1-2天 |
| **Phase 2** | 参考 Colyseus 实现 Room 生命周期 + Redis 扩展 + 30s 重连窗口 | 中 | 3-5天 |
| **Phase 3** | DM/Player 权限分层 + Secret State 过滤 | 中 | 2-3天 |
| **Phase 4** | 地图/Token 系统（可选，参考 PlanarAlly） | 大 | 5-7天 |

### 13.2 关键决策

1. **不需要引入 Node.js** — `python-socketio` 提供全部 Socket.IO 能力，保持纯 Python 技术栈
2. **不需要 CRDT** — DND 是回合制，权威服务器 + 事件驱动就够。Yjs 只在需要"离线编辑角色卡"时才值得引入
3. **不需要 UDP/WebRTC** — DND 不是 FPS，不需要毫秒级延迟。WebSocket 的可靠性更重要
4. **参考 Colyseus 架构但不直接使用** — Colyseus 的 Room/Schema/生命周期设计是教科书级别的。在 Python 中照着实现一套，比直接引入 Node.js 更好
5. **PlanarAlly 是最佳参考项目** — 同为 Python 后端 + WebSocket 多人 + VTT 功能，直接阅读其源码

### 13.3 当前架构瓶颈（报告指出）

| 瓶颈 | 说明 | 解决方案 |
|------|------|----------|
| ❌ 单进程内存态 | `ConnectionManager.campaigns` 是内存 dict，重启即丢失 | Redis 持久化 + SQLite 备份 |
| ❌ 无重连恢复 | 玩家断线后无法恢复游戏状态 | Socket.IO 自动重连 + 30s 窗口 |
| ❌ 无房间生命周期管理 | 房间不会自动创建/销毁 | CampaignRoom 类 + onDispose 钩子 |
| ❌ 无权限分层 | DM 和普通玩家走同一 WebSocket | 连接时区分角色 + emit 时按权限过滤 |
| ❌ 全量广播 | 每次广播整个状态，无增量同步 | 事件驱动 + 差异对比（长期） |
| ❌ 无离线消息队列 | 玩家离线期间的消息直接丢失 | Socket.IO 消息缓冲 + Redis 队列 |

### 13.4 Phase 1 实施方案：python-socketio 升级

#### 安装依赖
```bash
pip install python-socketio redis aiofiles
```

#### 核心改动：`src/aidm/api/ws.py` 重写

```python
import socketio
import asyncio
from ..brain import graph, world
from ..engine import combat as cmb
from ..stats import store, models
from ..brain.room import RoomManager

# 创建 Socket.IO 服务器
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# 房间管理器
room_manager = RoomManager()

# 序列化锁（Qdrant 本地模式非线程安全 + D&D 本来就是回合制）
lock = asyncio.Lock()


@sio.event
async def connect(sid, environ):
    """玩家连接时自动加入战役房间"""
    qs = dict(pair.split('=') for pair in environ.get('QUERY_STRING', '').split('&') if '=' in pair)
    campaign_id = int(qs.get('campaign_id', 0))
    character_id = int(qs.get('character_id', 0))
    name = qs.get('name', '玩家')
    is_dm = qs.get('role', 'player') == 'dm'

    # 加入 Socket.IO 房间
    await sio.enter_room(sid, f'campaign_{campaign_id}')

    # 保存会话
    await sio.save_session(sid, {
        'campaign_id': campaign_id,
        'character_id': character_id,
        'name': name,
        'is_dm': is_dm,
        'sid': sid,
    })

    # 注册到房间管理器
    room_manager.add_player(campaign_id, sid, character_id, name, is_dm)

    # 通知其他玩家
    players = room_manager.get_players(campaign_id)
    await sio.emit('join', {'name': name, 'players': players},
                   room=f'campaign_{campaign_id}', skip_sid=sid)

    # 发送当前场景和战斗状态
    scene = world.get_scene(campaign_id)
    if scene:
        await sio.emit('scene_update', scene, to=sid)

    try:
        combat = store.load_combat(campaign_id)
        if combat.active:
            await sio.emit('combat_update', {
                'active': True, 'round': combat.round,
                'initiative_order': [{'name': c.name, 'init': c.initiative, 'side': c.side}
                                     for c in combat.initiative_order],
            }, to=sid)
    except Exception:
        pass


@sio.on('action')
async def on_action(sid, data):
    """玩家发起行动"""
    session = await sio.get_session(sid)
    campaign_id = session['campaign_id']
    character_id = session['character_id']
    name = session['name']

    # 回合检查
    if not room_manager.is_player_turn(campaign_id, character_id):
        await sio.emit('error', {'message': '还没轮到你'}, to=sid)
        return

    # 通知全员：X 正在行动
    await sio.emit('player_acting', {'player': name},
                   room=f'campaign_{campaign_id}', skip_sid=sid)

    # 序列化执行
    async with lock:
        result = await asyncio.get_event_loop().run_in_executor(
            None, graph.run, data['player_input'], campaign_id, character_id
        )

    # 广播结果给房间内所有人
    await sio.emit('result', {
        'player': name,
        'narration': result.get('narration', ''),
        'dice': result.get('dice', {}),
        'action_options': result.get('action_options', []),
    }, room=f'campaign_{campaign_id}')


@sio.event
async def disconnect(sid):
    """玩家断线处理"""
    session = await sio.get_session(sid)
    if not session:
        return
    campaign_id = session['campaign_id']
    name = session.get('name', '未知玩家')

    room_manager.remove_player(campaign_id, sid)
    players = room_manager.get_players(campaign_id)
    await sio.emit('leave', {'name': name, 'players': players},
                   room=f'campaign_{campaign_id}')
```

#### 前端更新：`ui/static/index.html`

将 `new WebSocket(...)` 替换为 `io(...)` (socket.io-client)：

```javascript
// 旧代码
ws = new WebSocket(`${API.replace('http', 'ws')}/ws/${campId}?character_id=${charId}&name=${encodeURIComponent(myName)}`);

// 新代码
ws = io(API, {
    query: {
        campaign_id: campId,
        character_id: charId,
        name: myName,
        role: 'player'
    }
});

// 消息处理逻辑保持不变
ws.on('join', (data) => { ... });
ws.on('result', (data) => { ... });
ws.on('disconnect', () => { ... });

// 发送行动
ws.emit('action', { player_input: text });
```

#### API 层集成：`src/aidm/api/main.py`

```python
from ..api.ws import sio

# 将 Socket.IO ASGI 应用与 FastAPI 合并
combined_app = socketio.ASGIApp(sio, app)
```

### 13.5 Phase 2 实施方案：Room 生命周期 + Redis 扩展

#### `src/aidm/brain/room.py` — 升级，参考 Colyseus Room 设计

```python
@dataclass
class PlayerSession:
    sid: str
    character_id: int
    name: str
    is_dm: bool = False
    connected: bool = True
    last_seen: float = field(default_factory=time.time)


class CampaignRoom:
    """一个 DND 战役房间，参考 Colyseus Room 设计。"""
    rooms: dict[int, 'CampaignRoom'] = {}  # campaign_id → room
    _dispose_tasks: dict[int, asyncio.Task] = {}

    def __init__(self, campaign_id: int):
        self.campaign_id = campaign_id
        self.players: dict[str, PlayerSession] = {}  # sid → session
        self.lock = asyncio.Lock()
        self.created_at = time.time()
        self.last_activity = time.time()

    def add_player(self, sid, character_id, name, is_dm=False):
        self.players[sid] = PlayerSession(sid, character_id, name, is_dm)
        self.last_activity = time.time()

    def remove_player(self, sid):
        if sid in self.players:
            del self.players[sid]
        # 如果房间空了，30秒后销毁
        if not self.players:
            self._schedule_dispose()

    def get_players(self):
        return [{'name': p.name, 'character_id': p.character_id, 'is_dm': p.is_dm}
                for p in self.players.values()]

    def is_player_turn(self, character_id):
        """检查是否轮到该角色"""
        try:
            combat = store.load_combat(self.campaign_id)
            if not combat.active:
                return True  # 非战斗时自由行动
            cur = cmb.current_combatant(combat)
            return cur and cur.cid == str(character_id)
        except Exception:
            return True

    def _schedule_dispose(self):
        """30秒后如果房间仍为空，则销毁并持久化"""
        async def _dispose():
            await asyncio.sleep(30)
            if not self.players:
                # 持久化到 SQLite（store 已有此能力）
                del CampaignRoom.rooms[self.campaign_id]

        loop = asyncio.get_event_loop()
        task = loop.create_task(_dispose())
        self._dispose_tasks[self.campaign_id] = task

    @classmethod
    def get_or_create(cls, campaign_id: int) -> 'CampaignRoom':
        if campaign_id not in cls.rooms:
            cls.rooms[campaign_id] = cls(campaign_id)
        return cls.rooms[campaign_id]
```

#### Redis 扩展（可选，多进程时启用）

```python
# 多进程广播：用 Redis Pub/Sub 跨服务器
mgr = socketio.AsyncRedisManager('redis://localhost:6379/0')
sio = socketio.AsyncServer(client_manager=mgr, async_mode='asgi',
                           cors_allowed_origins='*')
```

### 13.6 Phase 3 实施方案：DM/Player 权限分层

#### 权限模型

| 能力 | DM（主持人） | 玩家 |
|------|-------------|------|
| 查看隐藏信息（陷阱 DC / 怪物 HP / 隐藏笔记） | ✅ | ❌ |
| 修改任何状态（HP / 物品 / 位置） | ✅ | ❌ 仅自己的角色 |
| 撤销/回溯操作 | ✅ | ❌ |
| 控制 NPC / 怪物 | ✅ | ❌ |
| 控制地图 FOW（战争迷雾） | ✅ | ❌ |
| 强制结束/跳过回合 | ✅ | ❌ |
| 在自己的回合执行操作 | ✅ | ✅ |
| 查看公开骰子结果 | ✅ | ✅ |
| 发送聊天消息 | ✅ | ✅ |

#### 实现：连接时区分角色 + emit 时按权限过滤

```python
async def broadcast_with_filter(room, event, data, dm_data=None):
    """广播时按权限过滤：DM 收完整数据，玩家收过滤后数据。"""
    for sid, session in room.players.items():
        if session.is_dm:
            await sio.emit(event, dm_data or data, to=sid)
        else:
            await sio.emit(event, data, to=sid)

# 战斗状态广播：DM 看怪物 HP，玩家不看
await broadcast_with_filter(
    room, 'combat_update',
    data={'active': True, 'round': 3, 'initiative_order': public_order},
    dm_data={'active': True, 'round': 3,
             'initiative_order': full_order_with_monster_hp}
)
```

### 13.7 技术选型汇总

| 需求 | 推荐方案 | 理由 |
|------|----------|------|
| WebSocket 通信 | **python-socketio** | FastAPI 原生集成 / Room 支持 / 自动重连 / Redis 扩展 |
| 房间管理 | **自建 Room 类**（参考 Colyseus） | 纯 Python / 无语言桥接 / 完全控制生命周期 |
| 状态同步 | **事件驱动 + 全量快照** | DND 回合制 / 状态量小 / 全量同步简单可靠 |
| 回合协调 | **已有 `is_player_turn()`** | 已实现 / 保持现状 |
| 权限控制 | **DM/Player 角色过滤** | 连接时区分角色 / emit 时按权限过滤 |
| 断线重连 | **Socket.IO 自动重连 + 30s 窗口** | 原生支持 / 零额外代码 |
| 水平扩展 | **Redis Pub/Sub** | python-socketio 内置 / `AsyncRedisManager` |
| 持久化 | **SQLite (已有)** | 当前够用 / 未来量大可迁 PostgreSQL |
| 地图/Token (未来) | **Canvas + 自建状态管理**（参考 PlanarAlly） | Python 后端参考 / MIT 许可 |
| 角色卡协作 (未来) | **Yjs + y-websocket**（可选） | CRDT 离线编辑 / 冲突解决 / 21K star 成熟 |

### 13.8 开源项目一览表

| 项目 | Stars | 语言 | 用途 | 是否采用 |
|------|-------|------|------|----------|
| Socket.io | 63K | Node.js/TS | 实时通信框架 | ✅ 采用 Python 版 (python-socketio) |
| RxDB | 23K | TypeScript | 响应式本地数据库 | ⚠️ 暂不需要 |
| Yjs | 21K | TypeScript | CRDT 协作 | ⚠️ Phase 4+ 可选 |
| Nakama | 12.4K | Go | 游戏后端 BaaS | ❌ 过重，不采用 |
| boardgame.io | 12.3K | TypeScript | 回合制游戏框架 | ❌ 参考其设计理念 |
| Colyseus | 6.8K | Node.js/TS | 权威服务器+Room | ❌ 参考其架构设计 |
| python-socketio | 3.7K | Python | Socket.IO Python 实现 | ✅ 核心依赖 |
| Automerge | 6.4K | Rust+WASM | CRDT 版本历史 | ⚠️ 有 Python 绑定，可选 |
| PlanarAlly | ~482 | Python (aiohttp) | VTT 虚拟桌面 | 📖 最佳参考项目 |

| 优先级 | Phase/模块 | 说明 | 预估工作量 |
|--------|-----------|------|-----------|
| P0 | Phase B 角色创建 | 五步车卡法 | 已完成 ✅ |
| P0 | Phase C 核心循环 | DM描述→玩家行动→DM解决 | 已完成 ✅ |
| P0 | Phase D 战斗流程 | 突袭→先攻→回合经济→借机攻击 | 已完成 ✅ |
| P0 | Phase G 施法流程 | 声明→成分→效果→法术位→专注 | 已完成 ✅ |
| P0 | Phase H 休息机制 | 短休(1h)/长休(8h)→恢复HP/法术位/特性 | 已完成 ✅ |
| P0 | Phase I 升级成长 | XP表/升级五步骤/游戏四阶段(T1-T4) | 已完成 ✅ |
| P0 | Phase E 探索流程 | 旅行步调→导航→被动察觉→随机遭遇→资源追踪 | 已完成 ✅ |
| P0 | Phase F 社交流程 | NPC态度系统(友好/冷漠/敌对)/四步社交互动/态度转换阈值 | 已完成 ✅ |
| P0 | Phase A Session 0 | 基调校准/内容边界/规则后勤 | 已完成 ✅ |
| **P0** | **12.2 魔法物品系统** | **战利品/稀有度/同调/鉴定/诅咒** | **大** |
| **P0** | **12.5 多人游戏系统** | **房间管理/多人战斗协调/多人探索协调/多人社交协调/多人休息协调/多人战利品分配** | **大** |
| **P0** | **12.1 专长系统** | **PHB第五章专长(起源/战斗风格/通用/传奇恩惠)** | **中** |
| P1 | 12.3 冒险创建工具 | DMG第四章创建冒险(设计步骤/导入玩家/布置背景/规划遭遇) | 大 |
| P1 | 12.4 据点系统 | DMG第八章据点(建立/回合/地图/25种特色设施/事件/失去) | 大 |
| P2 | 12.6 宇宙学/位面旅行 | DMG第六章宇宙学(30个位面/位面旅行/位面效应/位面居民) | 中 |
| P2 | 12.7 创作工具 | DMG第三章地下城主工具箱(创作法术/生物/物品/危害/名望/声望/怪群/恐惧/攻城/枪械/诅咒/赠礼/追逐/门/阵营/NPC) | 大 |

---

## 十四、总结

这份改造计划将当前"单一聊天框"系统升级为**分阶段、全流程覆盖的跑团引擎**，涵盖：

- **Session 0**：基调校准/内容边界/规则后勤
- **角色创建**：五步车卡法（职业→种族→属性→背景→阵营→细节）
- **核心循环**：DM描述环境→玩家声明行动→DM判断/要求掷骰→玩家掷骰→DM叙述结果→循环回到步骤A
- **D20检定**：三步流程（掷d20→加调整值→比较DC/AC）
- **战斗流程**：三步（确定位置→投掷先攻→执行回合）+ 15种状态 + 借机攻击 + 掩护
- **探索流程**：旅行步调（快速/中速/慢速）+ 视野光照 + 躲藏机制
- **社交流程**：NPC态度（友好/冷漠/敌对）+ 两条途径（RP/检定）
- **施法流程**：法术环阶/法术位/成分/施法时间/距离/持续时间/专注
- **休息机制**：短休（1h）/长休（8h）→恢复HP/法术位/特性
- **升级与成长**：XP表/升级五步骤/游戏四阶段（T1-T4）

### 新增遗漏项（基于规则书原文审计）

- **专长系统**（P0）：PHB第五章，角色成长核心
- **魔法物品系统**（P0）：DMG第七章，战利品/稀有度/同调/鉴定/诅咒
- **冒险创建工具**（P1）：DMG第四章，DM自定义冒险
- **据点系统**（P1）：DMG第八章，高等级基地管理
- **宇宙学/位面旅行**（P2）：DMG第六章，多元宇宙冒险
- **创作工具**（P2）：DMG第三章，DM自定义内容

### 新增多人游戏系统（P0）

- **房间管理系统**：创建/加入/密码/状态/玩家管理/观战
- **多人战斗协调**：先攻序列共享/回合锁定/行动广播/怪物AI回合/反应协调
- **多人探索协调**：队伍行进/队形管理/被动察觉/发现共享/分头行动
- **多人社交协调**：对话顺序/态度共享/协助检定/信息共享
- **多人休息协调**：同步休息/生命骰独立/法术位恢复/打断通知
- **多人战利品分配**：战利品池/分配方式(需求优先/轮流拾取/点数分配/DM指定)/金币分配/分配记录
