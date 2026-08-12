# P2-03 Repo 历史瘦身 — 执行方案（待人工确认后执行）

> ⚠ 历史重写会改变所有已发布 commit 的 hash，影响远端协作者。
> 本文件为可执行方案；**执行前需用户确认**（本会话不自动执行）。
>
> **当前决定（2026-08）：不重写 git 历史。** 用户明确：
> - 项目图片（`aidm/data/images/`，682 张 / 约 1.76GB）**必须保留**，后续会使用；
> - 历史瘦身不执行，仓库体积 1.8G 仅影响克隆速度，不影响功能/测试/部署。
> 下列方案仅存档备查，若将来需要执行，**严禁触碰图片目录**。

## 目标

```
fresh clone < 100 MB（理想 < 50 MB）—— 仅当用户将来决定执行历史瘦身时
```

## 大文件来源（已分析）

- `5echm_web/` — 外部规则数据源（非本项目产物）
- 历史中的 `ui/out/`、`htmlcov/`、`__pycache__` 等构建/缓存产物

## ⛔ 禁区（绝不可移除）

- **`aidm/data/images/`** — 项目正式图片资产（武器/护甲/法术/物品图标等 682 张），
  前端与后续功能会使用。**任何历史瘦身/清理操作都不得触碰此目录。**
- 若需压缩体积，替代方向：图片转 WebP/压缩后再入库（新 commit 起生效），
  而不是从历史中删除。

## 执行步骤（仅当用户明确要求时，在专用分支/本地副本上先行验证）

```bash
# 1. 安装 git-filter-repo（官方推荐，替代 filter-branch）
pip install git-filter-repo

# 2. 移除历史中的大目录（严格排除图片目录）
git filter-repo --path 5echm_web --invert-paths
git filter-repo --path-glob 'ui/out/*' --invert-paths
git filter-repo --path-glob 'htmlcov/*' --invert-paths

# 3. 压缩对象库
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. 验证体积 + 图片完整性
git count-objects -vH
git ls-tree -r --name-only HEAD -- aidm/data/images | wc -l   # 必须仍为 682

# 5. 强制推送（需团队就绪 + 备份原仓库）
git push --force origin master
```

## 前置保护（已在本仓库生效）

- `.gitignore` 已忽略 `ui/out/`、`htmlcov/`、`__pycache__/`、运行时 db/saves
- 新增 `aidm/requirements.lock`（可复现依赖），避免 lock 文件反复变更
- 图片目录始终被 git 追踪，无任何忽略规则

## 风险与回滚

- 远端协作者需 `git fetch --force` + `git rebase`
- 执行前必须 `git clone --mirror` 全量备份
- 若 GitHub 端有 PR/Issue 引用旧 commit，需一并处理

## 验收

```bash
git clone <remote> /tmp/fresh
du -sh /tmp/fresh                               # < 100 MB（不含图片则按实际）
git ls-tree -r --name-only HEAD -- aidm/data/images | wc -l   # = 682
```