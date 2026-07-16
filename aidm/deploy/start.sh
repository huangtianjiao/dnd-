#!/usr/bin/env bash
# AIDM 后端一键启动（Linux / macOS）
# 用法：./deploy/start.sh  或  bash deploy/start.sh
set -euo pipefail

# 切到项目根（deploy 的上一级）
cd "$(dirname "$0")/.."

export PYTHONPATH=src

# 可用环境变量 PY 指定解释器，默认 python
: "${PY:=python}"

echo "启动 AIDM 后端 http://0.0.0.0:8080 (reload 模式)..."
exec "$PY" -m uvicorn aidm.api.main:app --host 0.0.0.0 --port 8080 --reload
