# P2-03 Repo 历史瘦身 — 执行方案（待人工确认后执行）

> ⚠ 历史重写会改变所有已发布 commit 的 hash，影响远端协作者。
> 本文件为可执行方案；**执行前需用户确认**（本会话不自动执行）。

## 目标

```
fresh clone < 100 MB（理想 < 50 MB）
```

## 大文件来源（已分析）

- `5echm_web/` — 外部规则数据源（非本项目产物）
- `generated images/` — 生成图片产物
- 历史中的 `ui/out/`、`htmlcov/`、`__pycache__` 等构建/缓存产物

## 执行步骤（在专用分支/本地副本上先行验证）

```bash
# 1. 安装 git-filter-repo（官方推荐，替代 filter-branch）
pip install git-filter-repo

# 2. 移除历史中的大目录（保留最新版本仍需要的文件）
git filter-repo --path 5echm_web --invert-paths
git filter-repo --path-glob 'generated images/*' --invert-paths
git filter-repo --path-glob 'ui/out/*' --invert-paths
git filter-repo --path-glob 'htmlcov/*' --invert-paths

# 3. 压缩对象库
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. 验证体积
git count-objects -vH

# 5. 强制推送（需团队就绪 + 备份原仓库）
git push --force origin master
```

## 前置保护（已在本仓库生效）

- `.gitignore` 已忽略 `ui/out/`、`htmlcov/`、`__pycache__/`、运行时 db/saves
- 新增 `aidm/requirements.lock`（可复现依赖），避免 lock 文件反复变更

## 风险与回滚

- 远端协作者需 `git fetch --force` + `git rebase`
- 执行前必须 `git clone --mirror` 全量备份
- 若 GitHub 端有 PR/Issue 引用旧 commit，需一并处理

## 验收

```bash
git clone <remote> /tmp/fresh
du -sh /tmp/fresh   # < 100 MB
```