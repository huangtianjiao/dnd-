# IMAGE_ASSETS — 图片资产盘点与生成方案

> 配套 `PRD.md` / `BUILD.md`。记录 5echm_web 规则书库的**可配图内容盘点**与 aidm 项目**图片资产生成方案**（SenseAudio 图片 API）。

## 1. 背景

项目以 5echm_web（8644 页 CHM→静态网页 + data.js 6238 条索引）为规则数据源，aidm 为 AI DM 引擎。
跑团/前端需要大量 D&D 主题图片（角色概念图、怪物、装备、法术、场景…）。本文件固化：

1. **发现**：规则书库里到底有多少可配图内容、各自规模与抽取难度。
2. **做法**：用什么 API、什么脚本、什么并发策略把图生成出来并落盘。

## 2. 可配图内容盘点（5echm_web）

> 数据来自对 `5echm_web/topics/` 46 本书的文件系统遍历与内容扫描（见 §8 脚本）。
> 总计 **46 本电子书 / 7523 个 HTML 页面**。

| 类别 | 规模（估算） | 已有图 | 抽取难度 | 说明 |
|---|---|---|---|---|
| **怪物** | ~600–800 种（去重）；含变体 ~1500 stat block | 0 | 中 | 8 本怪物书共 1961 页。2014MM≈400 种（按 CR 分组在 CR0-4.html 等文件内，每文件多条）、2025MM≈400 种（一文件一怪，含年龄/亚种变体）、瓦罗≈120、魔邓肯≈120、费资本龙≈30、布布≈45、多元宇宙≈250（大量重印） |
| **法术** | ~400 首（5E 全量） | 0 | 高 | ⚠️ PHB2024 的「法术」目录实为施法机制页（施法时间/成分/环阶/学派），法术本体在 data.js 索引里、未拆成独立页，难以逐首枚举 |
| **魔法物品** | ~250 件 | 0 | 中 | DMG2024「7.宝藏/魔法物品详述」62 个分组文件（武器7/护甲6/戒指4/权杖5/法杖6/药水5/魔杖6/卷轴3/奇物19…），每文件多条 |
| **地图/地点** | ~32 据点设施 + 模组区域页 ~100+ | 0 | 低-中 | ⚠️ 原 CHM 的**地图位图未被提取**——现有 178 张图里没有地图；可改为给据点设施/区域画概念图 |
| **菜肴/饮食** | ~10 个离散项 | 0 | — | 768 页提到食物，但全是 incidental 文本（怪物食谱/口粮/英雄宴法术），**无结构化菜谱**，不值得单建索引，并入「物品」即可 |
| 职业概念图 | 12 | 0 | 低 | 野蛮人…法师（已生成） |
| 种族概念图 | 9 | 0 | 低 | 人类…提夫林（已生成） |
| 装备 | 护甲13+武器38+钱币 | 0 | 低 | aidm 引擎 `equipment.py` 直接可读（已生成） |
| 状态效应 | 15 | 0 | 低 | `conditions.CONDITIONS` 直接可读（已生成） |
| 万象无常书牌 | 22 | **22** | — | `万象无常书/pic/` 已有 jpg/png 插图 |

### 2.1 关键结论

- **「完整图片索引」全量约 1500–2000+ 张**，是当前已生成的 15–20 倍；纯生成约 2.5h（75s/张·并发10）+ 大量 API 积分。**不建议一次全做**。
- **菜肴不需要单独索引**：无结构化菜谱内容。
- **地图**：原图未提取，无法「给已有地图配图」；改为给 ~32 据点设施 + 模组关键区域画场景概念图。
- **法术**：不必每首一图，复用 8 张学派徽记即可；真要配图需先从 data.js 抽取法术名（高难度）。
- **性价比最高批**：魔法物品(~250) + 据点地点(~32) + 核心怪物(~200 iconic) ≈ 500 张以内。

## 3. 已有图片资产

| 位置 | 内容 | 数量 | 来源 |
|---|---|---|---|
| `5echm_web/topics/万象无常书/pic/` | 万象无常书 22 张牌插图 | 22 | 原 CHM |
| `aidm/data/images/**` | D&D 主题配图（10 分类） | 109 | 本方案 batch1 生成 |
| `5echm_web/images/`、`icons/` | CHM 导航 UI 图标 | ~30 | 原 CHM，非美术资产 |

### 3.1 batch1 生成明细（109 张）

| 分类 | 张数 | 尺寸 | 来源 |
|---|---|---|---|
| conditions 状态 | 15 | 1024² | `conditions.CONDITIONS` |
| armor 护甲 | 13 | 1024² | `equipment.ARMOR` |
| weapons 武器 | 38 | 1024² | `equipment.WEAPONS` |
| classes 职业 | 12 | 864×1536 | 主题 |
| races 种族 | 9 | 864×1536 | 主题 |
| spell-schools 法术学派 | 8 | 1024² | 主题 |
| dice 骰子 | 3 | 1024² | 主题 |
| scenes 场景 | 8 | 2048×1024 | 主题 |
| coins 钱币 | 1 | 1024² | 主题 |
| cover 封面 | 2 | 2688×1152 | 主题 |

### 3.2 batch2 生成明细（435 / 571；暂停于新 key 日额度 300/天）

> 从 5echm_web 抽取条目名（魔法物品 `<H6>` 头、怪物一文件一怪折叠年龄变体、据点特色设施文件名）。
> 旧 key（key1）跑到 ~187 项触达日额度；换 key3 续跑，又触其 **300/天** 上限（ref_code 400001, common），熔断器自动停。**magic-items + stronghold 已全部完成**，剩 136 怪物待明日重置后续跑。

| 分类 | 计划 | 已成 | 尺寸 | 来源 |
|---|---|---|---|---|
| magic-items 魔法物品 | 339 | **339** ✅ | 1024² | DMG2024 魔法物品详述（按稀有度分文件，`<H6>` 头抽中英名） |
| stronghold 据点地点 | 29 | **29** ✅ | 1536×864 | DMG2024 据点特色设施（文件名即地点名） |
| monsters 核心怪物 | 203 | 67 | 1024² | 2025 怪物图鉴（折叠年龄变体，按 13 类型均衡各取 ≤16） |

清单：`aidm/data/images/images_manifest_batch2.json`（ok=435, pending=136）。

### 3.3 过程踩坑与管线加固（batch2 调试记录）

- **日额度**：图像侧独立于文本，每 key **300 张/天**（ref_code 400001, ref_scope common）；文本/LLM 不受影响。
- **后台任务被杀（exit 1 无 traceback）**：根因是**无输出看门狗**——新 key 生成慢（100–260s/张，旧 key 60–90s），慢轮询期 stdout 长时间静默被判定卡死。加固：轮询每 20s 打心跳 `… XXX 生成中 (Ns)`。
- **异步端点排队**：`/v1/image/async` 并发提交易服务端排队挂起（一批任务卡 pending）。**改用同步端点 `/v1/image/sync`**（直请求-响应，无队列，实测 31–124s/张，怪物低至 41s）。
- **管线加固**：配额熔断器（命中 400001 即停提交，不重试风暴）；`SENSEAUDIO_KEY` 环境变量覆盖（换 key 不动 .env）；`--max` 日额度护栏；紧凑 httpx 超时；实跑前剔除已存在项（减少协程数）。
- **执行方式**：本环境后台长任务不可靠，改用**前台分块**（每块 `--max ~30`、10 分钟内可控，文件实时落盘、断点可续）。

## 4. 图片生成方案（做法）

### 4.1 API

- **平台**：SenseAudio 开放平台（商汤，Token Plan 订阅，跨模态共享积分池）。
- **鉴权**：`Authorization: Bearer <API_KEY>`，key 存于 `D:/game/dnd/.env`（`key=...`）。
- **文档**：`doc1`=接口总览 `https://docs.senseaudio.cn/api-reference/introduction`；`doc2`=Token Plan `…/guides/token-plan/overview`。
- **端点**（图片）：
  - 异步生成 `POST https://api.senseaudio.cn/v1/image/async` → `{task_id}`
  - 轮询结果 `GET https://api.senseaudio.cn/v1/image/pending?task_id=` → `{status: completed|failed|pending, url, error_message}`
  - （同步 `POST /v1/image/sync` 直接返回 url，但占连接、易超时，批量不用）
- **选异步+轮询**：官方推荐用于后台批量，对长生成更稳。
- **模型**：`senseaudio-image-2.0-260319`（自研最新，支持多宽高比与高分辨率，prompt 上限 6000 码位）。
  - 备选：`senseaudio-image-1.0-260319`（常规/省）、`doubao-seedream-5-0-260128`（大尺寸）、`sensenova-u1-fast`（信息图）。
- **尺寸**（2.0 支持子集）：图标 `1024x1024`、肖像 `864x1536`、场景 `2048x1024`、封面 `2688x1152`。

### 4.2 并发与容错

- **并发 10**：`asyncio` + `httpx.AsyncClient` + `asyncio.Semaphore(10)`；10 个 worker 协程从共享队列取任务，形成 10 路在途生成的滑动窗口。
- **单任务流程**：提交 async → 每 3s 轮询 pending → completed 下载 URL 存盘 / failed 重试。
- **重试**：单任务最多 3 次（指数退避 1.5×）。
- **可恢复**：目标文件已存在且非空则跳过，中断后重跑续传。
- **超时**：单任务轮询上限 300s；httpx read timeout = 轮询上限+60s。

### 4.3 目录与 Prompt 设计

- **输出根目录**：`aidm/data/images/<分类>/<名称>.png`
- **清单**：`aidm/data/images/images_manifest.json`，每项含 `name/cn_name/category/file/size/status/url/attempts/prompt`。
- **数据驱动**：状态/护甲/武器/钱币直接 `import` aidm 引擎模块读名称，保证与项目数据一致。
- **英文 prompt**：图片模型英文更稳；中文名→英文名映射内置脚本，配统一风格后缀（fantasy illustration, D&D style, highly detailed, dramatic lighting, digital painting）。
- **尺寸按用途**：图标/物品/徽记用方图、角色概念图用竖图、场景用宽屏、封面用超宽。

### 4.4 脚本

| 文件 | 作用 |
|---|---|
| `aidm/scripts/generate_images.py` | 主生成器：env 读取、**同步生成**管线、并发、配额熔断器、心跳、下载、manifest |
| `aidm/scripts/generate_images_batch2.py` | batch2：从 5echm_web 抽取魔法物品/据点/核心怪物，复用 batch1 管线 |

## 5. 分批策略

| 批次 | 内容 | 张数 | 状态 |
|---|---|---|---|
| batch1 | 状态/护甲/武器/职业/种族/学派/骰子/场景/钱币/封面 | 109 | ✅ 完成 |
| batch2 | 魔法物品 + 据点地点 + 核心怪物 | 435 / 571 | ⏸️ 暂停于新 key 日额度（剩 136 怪物，见 §3.2） |
| batch3（可选） | 全怪物库去重 / 法术图标 / 模组区域图 | ~800–1500 | 待评估 |

> 累计已生成 **544 张**（batch1 109 + batch2 435）。明日 key 重置后续跑 `--categories monsters` 即可补完（136 < 300/天）。

## 6. 运行方式

```bash
cd D:/game/dnd/aidm
PY=/d/software/Anaconda3/envs/langchain_312/python.exe

# 续跑 batch2 剩余怪物（明日 key 重置后；< 300/天，一次可跑完）
SENSEAUDIO_KEY=sk-... PYTHONPATH=src $PY scripts/generate_images_batch2.py \
    --categories monsters --concurrency 10 --max 30
# 注：本环境后台长任务会被无输出看门哥杀，用前台分块（--max ~30、10 分钟内）最稳；
#    文件实时落盘、断了重跑即续传（自动跳过已有）。

# batch1（全量，自动跳过已有）
PYTHONPATH=src $PY scripts/generate_images.py --concurrency 10

# 仅指定分类 / 只看清单 / 限量测试
PYTHONPATH=src $PY scripts/generate_images_batch2.py --categories monsters --dry-run
PYTHONPATH=src $PY scripts/generate_images_batch2.py --categories monsters --max 3 --concurrency 3
```

## 7. 注意事项

- **成本**：每张耗积分；批量前先 `--dry-run` 核对数量，`--limit` 试跑。
- **编码**：5echm_web 为 GBK/UTF-8 混杂，抽取脚本需按 utf-8-sig/utf-8/gb18030 顺序解码。
- **怪物去重**：8 本怪物书大量重印/变体（龙年龄段、元素亚种），需按「物种」折叠，否则 stat block ~1500 远大于实际物种数。
- **不改动**：5echm_web（只读规则源）、aidm 引擎/数据代码（只读名称）。

## 8. 盘点脚本（参考）

§2 的统计由一次性遍历得到，核心逻辑：
1. `os.walk(topics/)` 按「书」计 HTML 文件数。
2. 怪物：按 `挑战等级` 计数（2014MM 分组文件内多条）+ 2025MM 一文件一怪按文件计。
3. 关键词扫描：`地图` / `菜肴`/`食物`/`英雄宴` 等的出现页数与上下文。
4. 已有图：`topics/` 下 `.png/.jpg/.gif/.bmp` 文件清单。
