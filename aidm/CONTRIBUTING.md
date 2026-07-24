# 贡献指南 — AIDM 协作规范

> 本文档定义 AIDM 项目的分支管理、提交规范、代码合并规则与问题处理流程。所有贡献者请遵守。
> 项目入门与启动方式见 [README.md](README.md)。

## 一、分支管理

### 分支说明

| 分支 | 用途 | 权限 |
|------|------|------|
| `main` | 生产环境，只放稳定代码 | 只能通过 Pull Request 合并，**禁止直接推送** |
| `dev` | 日常开发集成分支 | 尽量通过 Pull Request 合并 |
| `feature/*` | 功能开发分支 | 开发者自由提交 |
| `fix/*` | Bug 修复分支 | 开发者自由提交 |
| `release/*` | 发版分支 | 由负责人从 dev 切出 |

### 分支流程图

```
        main          生产环境，只放稳定代码
          ↑
         dev          日常开发集成分支
          ↑
   ┌──────┴──────┬──────────┐
feature/login  feature/order  fix/payment-bug
```

### 开发流程

```bash
# 1. 从 dev 拉分支
git checkout dev
git pull
git checkout -b feature/user-login

# 2. 开发完成后
git add .
git commit -m "feat: add user login"
git push origin feature/user-login

# 3. 发起 Merge Request / Pull Request，合并到 dev
# 4. 测试没问题后，再从 dev 合并到 main，触发上线
```

## 二、提交规范

### 提交信息前缀

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 新增怪物图片资源` |
| `fix` | 修复问题 | `fix: 修复前端端口配置` |
| `docs` | 文档修改 | `docs: 补全 API 参考文档` |
| `style` | 格式修改（不影响代码逻辑） | `style: 统一缩进` |
| `refactor` | 代码重构 | `refactor: 抽取骰子工具函数` |
| `test` | 测试相关 | `test: 补充伤害管线测试` |
| `chore` | 构建、依赖、配置修改 | `chore: 升级 langgraph 版本` |
| `deploy` | 部署相关 | `deploy: 新增启动脚本` |

格式：`<前缀>: <简要描述>`

## 三、代码合并规则

1. **禁止直接推送到 `main`**
2. **禁止直接在服务器上改代码**
3. 所有功能从 `feature/*` 合并到 `dev`
4. 上线前由负责人从 `dev` 合并到 `main`
5. 合并前至少自己跑通本地项目
6. 重要功能需要另一个人 Review

### 分支合并权限

| 分支 | 合并方式 |
|------|---------|
| `main` | 只能通过 Pull Request 合并 |
| `dev` | 尽量通过 Pull Request 合并 |
| `feature/*` | 开发者自由提交 |

## 四、问题处理流程

处理问题时按以下模板记录（可后期使用多维表格 / Issue 系统创建）：

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

## 五、本地开发入门

详见 [README.md](README.md) 第 3 节「本地启动方式」与 [deploy/](deploy/)。要点：

| 项目 | 命令 | 端口 |
|------|------|------|
| 后端 | `PYTHONPATH=src python -m aidm.api.main` | 8080 |
| 前端 | `cd ui && npm run dev` | 3000 |
| 测试 | `PYTHONPATH=src python tests/test_*.py`（逐个） | — |
| 规则库索引（首次） | `PYTHONPATH=src python -m aidm.knowledge.indexer` | — |

## 六、文档维护约定

详见 [docs/README.md](docs/README.md)。文档按维护频率分三档：

- 🟢 **稳定参考档**：描述"应当是什么"，很少改（PRD / RULE_SPEC）
- 🟡 **中频档**：随进度订正，但不每天动（ARCHITECTURE / BUILD）
- 🔴 **常更档**：持续追加，是日常开发的活页（CHANGELOG / DECISIONS / ISSUES）

已知问题与遗留技术债见 [docs/ISSUES.md](docs/ISSUES.md)。
