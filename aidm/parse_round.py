# -*- coding: utf-8 -*-
"""Per-round log formatter for the 100-round driver. Reads the /chat JSON
response from a file and prints one compact line. Pure display; does not
touch game state."""
import sys, json

i, hppre, dead, cpre, rf = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
try:
    d = json.load(open(rf, encoding="utf-8"))
except Exception:
    print(f"round {i} | FATAL: bad JSON response (respfile={rf})")
    sys.exit(0)
dk = d.get("dice", {}) or {}
cb = d.get("combat", {}) or {}
ph = [c.get("hp") for c in cb.get("combatants", []) if c.get("is_player")]
ph = ph[0] if ph else "?"
intent = (d.get("intent") or {}).get("action_type", "?")
print(f"r{i} hp_pre={hppre} dead={dead} c_pre={cpre} | intent={intent} | "
      f"dice={dk.get('kind','?')} hit={dk.get('hit','-')} dmg={dk.get('damage','-')} "
      f"diceerr={str(dk.get('error','') or '-')[:30]} | c_post={cb.get('active','?')} "
      f"c_round={cb.get('round','-')} | hp_post={ph} | opts={len(d.get('action_options',[]))} "
      f"| apierr={str(d.get('error','') or '-')[:30]}")
