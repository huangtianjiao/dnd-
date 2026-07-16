# REPO_CLEANUP — 仓库瘦身与历史清理方案

> 生成时间: 2026-07-16
> 背景: gitee 仓库已达 1796 MB，超过 1024 MB 配额，仅剩 3 次 push 机会；GitHub origin 无硬性配额。
> 目标: 把 .git 从 1.76 GB 降到几百 MB，消除历史大文件，恢复可用。

## 1. 现状

| 指标 | 数值 | 说明 |
|---|---|---|
| .git 总大小 | 1.76 GB | pack 1.40 GiB + loose 358 MiB |
| gitee 仓库 | 1796 MB | 超 1024 MB 配额，剩 3 次 push |
| GitHub origin | 同步 | 无硬性配额（建议 <5GB） |
| 提交数 | 4 | 历史短，清理代价低 |

## 2. 大文件分析（当前工作树）

| 目录 | 大小 | 文件数 | 说明 |
|---|---|---|---|
| `aidm/data/images/` | **1.8 GB** | 682 | 游戏配图 PNG（AI 生成，`scripts/generate_images*.py` 产物） |
| `5echm_web/` | **226 MB** | 8692 | 规则书数据源克隆（只读，WinCHM 导出） |

### images 子目录分布

| 子目录 | 大小 |
|---|---|
| magic-items/ | 878 MB |
| monsters/ | 541 MB |
| weapons/ | 80 MB |
| stronghold/ | 76 MB |
| conditions/ | 40 MB |
| classes/ | 31 MB |
| armor/ | 30 MB |
| spell-schools/ | 26 MB |
| scenes/ | 22 MB |
| races/ | 21 MB |
| 其余（dice/coins 等） | ~95 MB |

### 历史最大单体文件

| 文件 | 大小 |
|---|---|
| `5echm_web/data.js` | 25.6 MB |
| `aidm/data/images/coins/coins_pile.png` | 3.8 MB |
| `5echm_web/webhelpcontents.htm` | 3.5 MB |
| `aidm/data/images/magic-items/Adamantine_精金护甲.png` | 3.5 MB |
| 其余 3.1–3.3 MB 的 PNG × 20+ | — |

### 根因

根 `.gitignore` 历史上**未忽略 `5echm_web/` 和 `aidm/data/images/`**，导致规则书 HTML 与所有配图被提交入库。4 次提交中图片以二进制 diff 累积，历史 pack 膨胀到 1.40 GiB。`5echm_web/` 是只读外部克隆，`images/` 是可由脚本重新生成的产物——两者都不应进入代码仓库。

## 3. 清理方案

### 方案 A：移除 5echm_web + images 转 Git LFS（保留资产）

- `5echm_web/`：移除历史，加 `.gitignore`，文档说明从哪获取。
- `aidm/data/images/`：保留，但用 **Git LFS** 管理大文件。需先 filter-repo 清历史，再 LFS track 新提交。
- 优点：配图保留，前端可正常展示。
- 缺点：LFS 只管未来提交，历史仍需 filter-repo 清理；GitHub LFS 免费配额 1GB 存储/1GB 月流量。

### 方案 B：移除两者，images 按需重新生成（最瘦，推荐）

- `5echm_web/`：移除历史，加 `.gitignore`。
- `aidm/data/images/`：移除历史，加 `.gitignore`。需要时用 `scripts/generate_images*.py` 重新生成。
- 优点：仓库降到几百 KB（仅代码+文档）；历史彻底干净。
- 缺点：重新生成图片需 LLM/图像 API（`scripts/generate_images*.py`）；首次恢复需跑脚本。

> **推荐方案 B**：历史仅 4 个提交、图片可重生、gitee 配额告急——清理代价最低、收益最高。

## 4. 操作步骤（方案 B，git filter-repo）

### 4.1 安装 git-filter-repo

```bash
pip install git-filter-repo
# 或 conda: conda install -c conda-forge git-filter-repo
```

> `git filter-branch`（git 内置）也可用但慢且不推荐；filter-repo 是官方推荐工具。

### 4.2 备份（必做）

```bash
# 在 D:\game\dnd 的上级目录做完整镜像备份
git clone --mirror D:/game/dnd dnd-backup-$(date +%Y%m%d).git
```

### 4.3 重写历史移除大目录

```bash
cd D:/game/dnd

# filter-repo 默认要求 fresh clone，已有仓库需 --force
git filter-repo --force --path 5echm_web/ --invert-paths
git filter-repo --force --path aidm/data/images/ --invert-paths

# 如有其他大文件，按 --path <path> --invert-paths 逐一移除
```

> filter-repo 会重写所有 commit，移除指定路径的历史对象。重写后 remote 会被移除，需重新添加。

### 4.4 更新 .gitignore（防止再次入库）

根 `.gitignore` 追加：

```
# === 规则书数据源（外部只读克隆，不入库）===
5echm_web/

# === 图片资产（由 scripts/generate_images*.py 生成，不入库）===
aidm/data/images/
```

### 4.5 重新聚合与垃圾回收

```bash
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git count-objects -vH   # 验证大小已下降
```

### 4.6 重新添加远程并强制推送

```bash
# filter-repo 移除了 remote，重新添加
git remote add origin https://github.com/huangtianjiao/dnd-.git
git remote add gitee git@gitee.com:george_huang00/dd-tabletop-roleplaying.git

# 强制推送（历史重写，必须 --force）
git push origin --force --all
git push origin --force --tags
# gitee 如需同步（清理后体积变小，可重置配额）：
# git push gitee --force --all
```

## 5. 注意事项

1. **历史重写改变所有 commit hash**：必须 `--force` 推送；任何已有 clone 的协作者需重新 clone（不能 pull）。
2. **config.py 路径依赖**：`config.py` 的 `rules_datajs_path` 默认指向 `5echm_web/data.js`。移除后需文档说明 `5echm_web/` 的获取方式（WinCHM 导出的规则书，属外部数据源，需另行获取或从备份恢复到工作树）。
3. **前端图片依赖**：移除 `images/` 后，前端引用的图片路径会 404。需在 `README.md` 或 `deploy/README.md` 说明：首次部署需跑 `scripts/generate_images*.py` 重新生成，或从 release 附件/外部存储下载图片包解压到 `aidm/data/images/`。
4. **gitee 配额**：清理后体积变小，force push 可重置 gitee 计数；也可在 gitee GC 入口压缩：https://gitee.com/george_huang00/dd-tabletop-roleplaying/settings#git-gc
5. **GitHub LFS（若选方案 A）**：`git lfs install` → `git lfs track "*.png"` → 提交 `.gitattributes`。注意 LFS 配额限制。

## 6. gitee 配额应对（短期）

在完成历史清理前：
- **只推 GitHub origin，暂停 gitee**（gitee 仅剩 3 次 push）
- gitee GC 入口压缩：https://gitee.com/george_huang00/dd-tabletop-roleplaying/settings#git-gc
- 清理历史后 force push 到 gitee，可重置配额计数

## 7. 预期效果

| 阶段 | .git 大小 |
|---|---|
| 清理前 | 1.76 GB |
| 移除 5echm_web（历史+当前） | ~1.53 GB |
| 移除 images（历史+当前） | <50 MB |
| gc --aggressive 后 | <20 MB |

> 因历史仅 4 个提交、且大文件集中在两类目录，方案 B 清理后仓库可降至 20 MB 以内（仅代码 + 文档 + 测试）。

## 8. 执行检查清单

- [ ] 已安装 git-filter-repo
- [ ] 已做镜像备份（`git clone --mirror`）
- [ ] 已移除 `5echm_web/` 历史
- [ ] 已移除 `aidm/data/images/` 历史
- [ ] 已更新 `.gitignore`（根目录）
- [ ] 已跑 `git gc --prune=now --aggressive`
- [ ] `git count-objects -vH` 确认体积下降
- [ ] 已 `--force` 推送 origin
- [ ] README/deploy 已补充 5echm_web 获取与 images 生成说明
