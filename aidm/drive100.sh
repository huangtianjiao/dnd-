#!/usr/bin/env bash
# 100-round player driver. ONLY calls the public /chat HTTP API (the player
# interface), exactly as the web frontend does (one fetch /chat per turn).
# No internal functions, no test harness. Actions are player-permitted only.
set -u
cd D:/game/dnd/aidm
CAMP=${CAMP:-574}; CHAR=${CHAR:-387}; THREAD="play100"
LOG=D:/game/dnd/aidm/run100.log
echo "=== 100-round run start camp=$CAMP char=$CHAR $(date '+%H:%M:%S') ===" > "$LOG"
for i in $(seq 1 100); do
  ST=$(curl -s -m 10 http://localhost:8080/character/$CHAR 2>/dev/null)
  HP=$(echo "$ST" | python -c "import sys,json;d=json.load(sys.stdin);print(d.get('hp',0))" 2>/dev/null)
  DEAD=$(echo "$ST" | python -c "import sys,json;d=json.load(sys.stdin);print(d.get('dead',False))" 2>/dev/null)
  CACT=$(curl -s -m 10 http://localhost:8080/combat/$CAMP 2>/dev/null | python -c "import sys,json;print(json.load(sys.stdin).get('active',False))" 2>/dev/null)
  [ -z "$HP" ] && HP=0
  if [ "$DEAD" = "True" ]; then echo "round $i | PLAYER DIED — run ended (hp_pre=$HP)" >> "$LOG"; break; fi
  if [ "$CACT" = "True" ]; then
    if [ "$((i % 5))" -eq 3 ]; then ACT="我试图擒抱最近的哥布林将它制服。"
    elif [ "$HP" -lt 8 ]; then ACT="我掏出治疗药水一饮而尽，恢复伤势。"
    else ACT="我用长剑全力劈砍最近的哥布林。"; fi
  else
    if [ "$HP" -lt 22 ]; then ACT="我退到安全处长休，恢复全部体力与精神。"
    else
      case $((i % 8)) in
        0) ACT="我俯身仔细搜索地面与灌木，寻找哥布林活动的踪迹。";;
        1) ACT="我向酒馆老板娘艾琳诚恳地打听近来镇上发生的怪事。";;
        2) ACT="我沿小径探索黑鸦森林边缘，保持高度警惕。";;
        3) ACT="我向镇长马库斯询问悬赏金额与商队失踪当晚的细节。";;
        4) ACT="我尝试躲入阴影隐蔽身形，观察酒馆内众人的反应。";;
        5) ACT="我研究墙上泛黄的悬赏令与老旧地图，理清线索。";;
        6) ACT="我向森林方向旅行推进，谨慎选择路线。";;
        7) ACT="我尝试推开挡路的酒醉农夫开路。";;
      esac
    fi
  fi
  python -c "import json,sys;print(json.dumps({'player_input':sys.argv[1],'campaign_id':$CAMP,'character_id':$CHAR,'thread_id':'$THREAD'},ensure_ascii=False))" "$ACT" > D:/game/dnd/aidm/round_body.json
  RESP=$(curl -s -m 150 -X POST http://localhost:8080/chat -H "Content-Type: application/json" -d @D:/game/dnd/aidm/round_body.json 2>/dev/null)
  if [ -z "$RESP" ]; then echo "round $i | FATAL: empty response — run aborted" >> "$LOG"; break; fi
  echo "$RESP" > D:/game/dnd/aidm/round_resp.json
  python D:/game/dnd/aidm/parse_round.py "$i" "$HP" "$DEAD" "$CACT" D:/game/dnd/aidm/round_resp.json >> "$LOG" 2>/dev/null
  if [ $? -ne 0 ]; then echo "round $i | parse-fail (resp len=$(printf '%s' "$RESP" | wc -c))" >> "$LOG"; fi
done
echo "=== run end $(date '+%H:%M:%S') ===" >> "$LOG"
echo "rounds logged:"; grep -c "^r" "$LOG" 2>/dev/null || true
