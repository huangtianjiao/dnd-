# -*- coding: utf-8 -*-
"""后端冒烟：health → campaign → character → state → chat → combat。临时脚本，跑完即删。"""
import json
import sys
import time
import urllib.request

BASE = "http://localhost:8080"


def req(method: str, path: str, body: dict | None = None, timeout: int = 120):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def check(name: str, ok: bool, detail: str = ""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        sys.exit(1)


# 1. health
st, out = req("GET", "/health")
check("health", st == 200 and out.get("status") == "ok", str(out))

# 2. create campaign
st, out = req("POST", "/campaign", {"name": "冒烟测试战役"})
camp_id = out.get("id") or out.get("campaign_id")
check("create campaign", st == 200 and camp_id, f"id={camp_id}")

# 3. create character
st, out = req("POST", "/character", {
    "name": "冒烟骑士", "race": "人类", "char_class": "战士",
    "campaign_id": camp_id,
})
char_id = out.get("id") or out.get("character_id")
check("create character", st == 200 and char_id, f"id={char_id}")

# 4. get character（角色卡契约字段）
st, out = req("GET", f"/character/{char_id}")
need = [k for k in ("name", "hp", "hp_max", "ac", "abilities") if k not in out]
check("get character", st == 200 and not need, f"missing={need}" if need else f"hp={out.get('hp')}/{out.get('hp_max')} ac={out.get('ac')}")

# 5. campaign state（继续游戏载入契约）
st, out = req("GET", f"/campaign/{camp_id}/state")
check("campaign state", st == 200 and out.get("campaign", {}).get("id") == camp_id,
      f"chars={len(out.get('characters', []))} scene={'yes' if out.get('scene') else 'no'}")

# 6. chat 一轮硬判定链（走 LLM，耐心等）
t0 = time.time()
st, out = req("POST", "/chat", {
    "player_input": "我环顾四周，观察周围环境",
    "campaign_id": camp_id, "character_id": char_id,
    "thread_id": f"smoke-{camp_id}", "hitl": False,
}, timeout=180)
dt = time.time() - t0
narr = out.get("narration", "")
check("chat round", st == 200 and len(narr) > 10 and not out.get("error"),
      f"{dt:.1f}s narration={len(narr)}字 dice_keys={list(out.get('dice', {}).keys())} options={len(out.get('action_options', []))}")

# 7. combat 状态端点（无战斗时应返回合法结构）
st, out = req("GET", f"/combat/{camp_id}")
check("combat endpoint", st == 200, f"active={out.get('active')}")

print("\nSMOKE BACKEND: ALL PASS")
print(f"camp_id={camp_id} char_id={char_id}")
