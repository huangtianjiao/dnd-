#!/usr/bin/env bash
# P1-12 Docker 生产冒烟 E2E — compose 构建/启动 + 全链路验证。
#
# 验证链:
#   docker compose build            干净构建（不依赖本地 out/）
#   docker compose up -d            启动 aidm-api + redis
#   GET /health → 200               REST 存活
#   create campaign → id            REST 写
#   create character → id           REST 写
#   Socket.IO connect → ok          WS 握手（combined_app 入口）
#   Socket.IO action → result       WS 判定链
#   save state → DB 落盘
#   restart API → campaign 仍在     P0-09 持久化卷
#
# 用法: bash scripts/docker_smoke.sh [--skip-build]
set -euo pipefail
cd "$(dirname "$0")/.."

API="${AIDM_SMOKE_API:-http://localhost:8000}"
SKIP_BUILD=0
[ "${1:-}" = "--skip-build" ] && SKIP_BUILD=1

log() { echo "[smoke] $*"; }
fail() { echo "[smoke] ✗ $*" >&2; exit 1; }

# ── 1. 构建 ─────────────────────────────────────────────────────────
if [ "$SKIP_BUILD" = "0" ]; then
  log "docker compose build ..."
  docker compose build || fail "docker compose build 失败（干净 checkout 必须可构建）"
fi

log "docker compose up -d ..."
docker compose up -d || fail "docker compose up 失败"

# 等待健康（最多 90s）
log "等待 /health 就绪 ..."
for i in $(seq 1 30); do
  if curl -sf "$API/health" > /dev/null 2>&1; then break; fi
  sleep 3
  [ "$i" = "30" ] && fail "/health 90 秒内未就绪"
done
log "✓ /health → $(curl -s "$API/health")"

# ── 2. REST: 建战役 + 角色 ────────────────────────────────────────
log "创建 campaign ..."
CAMP=$(curl -sf -X POST "$API/campaign" -H 'Content-Type: application/json' \
  -d '{"name":"smoke-'"$(date +%s)"'"}' | python -c "import sys,json;print(json.load(sys.stdin)['id'])") \
  || fail "创建 campaign 失败"
log "✓ campaign id=$CAMP"

log "创建 character ..."
CHAR=$(curl -sf -X POST "$API/character" -H 'Content-Type: application/json' \
  -d "{\"name\":\"冒烟勇士\",\"race\":\"人类\",\"char_class\":\"战士\",\"level\":1,\
       \"abilities\":{\"str\":16,\"dex\":14,\"con\":14,\"int\":10,\"wis\":10,\"cha\":10},\
       \"campaign_id\":$CAMP}" \
  | python -c "import sys,json;print(json.load(sys.stdin)['id'])") || fail "创建 character 失败"
log "✓ character id=$CHAR"

# ── 3. 会话令牌（WS 握手需要）──────────────────────────────────────
TOKEN=$(curl -sf -X POST "$API/auth/session" -H 'Content-Type: application/json' \
  -d "{\"campaign_id\":$CAMP,\"character_id\":$CHAR}" \
  | python -c "import sys,json;print(json.load(sys.stdin)['token'])") || fail "会话令牌失败"
log "✓ session token 签发"

# ── 4. Socket.IO 连接 + 行动 ───────────────────────────────────────
log "Socket.IO connect + action ..."
python - "$API" "$CAMP" "$CHAR" "$TOKEN" << 'PYEOF' || fail "Socket.IO 冒烟失败"
import sys, json, time
import socketio

api, camp, char, token = sys.argv[1:5]
sio = socketio.Client()
result = {"got": None, "connected": False}

@sio.event
def connect():
    result["connected"] = True
    sio.emit("action", {"player_input": "我观察周围环境", "command_id": "smoke-e2e-1"})

@sio.event
def result_event(d):
    result["got"] = d
    sio.disconnect()

@sio.on("error")
def err(d):
    result["error"] = d

sio.connect(api, auth={"token": token},
            query={"campaign_id": camp, "character_id": char, "name": "冒烟勇士"})
deadline = time.time() + 60
while result["got"] is None and time.time() < deadline:
    time.sleep(0.5)
sio.disconnect()
assert result["connected"], "WS 未连接"
assert result["got"] is not None, f"未收到 result: {result}"
print("✓ WS connected + action result received")
PYEOF

# ── 5. 持久化: 重启后战役仍在（P0-09 卷）──────────────────────────
log "restart aidm-api（验证持久化卷）..."
docker compose restart aidm-api > /dev/null
for i in $(seq 1 20); do
  if curl -sf "$API/health" > /dev/null 2>&1; then break; fi
  sleep 3
  [ "$i" = "20" ] && fail "重启后 /health 未就绪"
done
CAMP2=$(curl -sf "$API/campaigns" | python -c "
import sys, json
data = json.load(sys.stdin)
camps = data.get('campaigns', data if isinstance(data, list) else [])
ids = [str(c.get('id')) for c in camps]
print($CAMP if str($CAMP) in ids else 'MISSING')
") || fail "重启后列表拉取失败（AIDM_DATA_DIR 卷未生效）"
[ "$CAMP2" = "$CAMP" ] || fail "重启后战役丢失（AIDM_DATA_DIR 卷未生效）"
log "✓ 重启后 campaign 仍在（持久化卷生效）"

log "全部冒烟通过 ✓"