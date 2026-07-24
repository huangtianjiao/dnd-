# AIDM 部署指南

> 本项目**免 Docker**：Qdrant 本地文件模式，嵌入模型本地运行，LLM 走外部 API。

## 一、依赖安装

### 后端（Python 3.12）
```bash
cd D:/game/dnd/aidm
pip install -r requirements.txt
```
> 开发环境使用 conda env `langchain_312`。

### 前端（Node.js ≥20）
```bash
cd D:/game/dnd/aidm/ui
npm install
```

## 二、规则库索引（首次必做）

规则 RAG 需先把规则书数据建入 Qdrant 本地文件库：

```bash
cd D:/game/dnd/aidm
PYTHONPATH=src python -m aidm.knowledge.indexer
```

产物：`aidm/data/rules.db/`（三个集合：`dnd_rules` / `dnd_rule_text` / `dnd_rule_spec`）。
首次运行会从 HF 镜像下载 bge-small-zh-v1.5 嵌入模型（约 100MB）。

## 三、启动

### 后端（FastAPI + WebSocket，端口 8080）

- **Windows**：双击 `deploy\start.bat`，或命令行执行
  ```bat
  deploy\start.bat
  ```
- **Linux/macOS**：
  ```bash
  ./deploy/start.sh
  ```
  > 若提示权限不足，先 `chmod +x deploy/start.sh`，或用 `bash deploy/start.sh`。

### 前端（Next.js dev，端口 3000）
```bash
cd D:/game/dnd/aidm/ui
npm run dev
```
浏览器访问 http://localhost:3000 （`ui/package.json` 为 `next dev -p 3000`）。
前端通过 `NEXT_PUBLIC_API`（见 `ui/.env.local`，默认 `http://localhost:8080`）关联后端：后端 8080、前端 3000。

### 静态 HTML 前端（无需 Node）
由后端 `/static` 自动托管，直接访问 http://localhost:8080

### CLI 跑团（无前端，交互式）
```bash
cd D:/game/dnd/aidm
PYTHONPATH=src python -m aidm.cli
```

## 四、生产部署

前端构建（静态产物）：
```bash
cd D:/game/dnd/aidm/ui
npm run build
```

后端生产模式（去掉 `--reload`）：
```bash
PYTHONPATH=src python -m uvicorn aidm.api.main:combined_app --host 0.0.0.0 --port 8080
```
> 注意入口必须是 `combined_app`（Socket.IO ASGI 包装），用 `app` 启动会导致 WebSocket 同桌不可用。

存档即文件：`aidm/data/saves/save.db`（SQLite），备份直接拷贝该文件即可。

## 五、环境变量

见根目录 `.env.example`。`.env` 默认位于 `D:\game\dnd\.env`，可用环境变量 `AIDM_ENV_FILE` 覆盖路径。必填项仅为 `key`（LLM API Key）。
