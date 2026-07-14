"""叙事/世界层 — DM 框定场景（完整背景 + 当前场景），跑团开场与场景推进。

依据 DMG「运作游戏/叙事」(R-DM 叙事/R-DM-027察觉/R-DM-029水下/R-DM-026声音等)：
  简洁、多感官氛围(视/听/嗅/触)、区分选项(左路腐臭/右路水声)、不臆测角色行动、
  秘密与发现(冒险所需信息可获得)。
把"输入框对着虚空"变成"DM 先呈现世界背景+当前场景，玩家据场景说意图"。
"""

from __future__ import annotations

import json
import re

from . import llm
from ..stats import store, models


def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?|```", "", text, flags=re.I)
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        try:
            return json.loads(m.group(0) + "}")
        except Exception:
            return {}


# R-DM 叙事 技巧锚定
SCENE_FRAMING_PROMPT = (
    "你是D&D 5E DM。依据世界设定与角色,生成跑团开场(完整背景)。遵循叙事技巧:\n"
    "- 简洁:短而回味,聚焦重要信息与线索\n"
    "- 氛围:多感官(视/听/嗅/触)让场景活灵活现\n"
    "- 区分选项:给可感知的不同选项(如左路腐臭/右路水声),但别限制\n"
    "- 不臆测角色行动(别说'你走进房间'除非玩家已做)\n"
    "- 秘密与发现:确保冒险所需信息可获得\n"
    "先回顾世界背景,再呈现当前场景(地点/时间/氛围/在场NPC/可感知细节/玩家可做之事)。\n"
    "只输出JSON: {\"narration\":\"开场叙事(背景回顾+当前场景,3-5段)\", "
    "\"action_options\":[\"选项1(含区分细节)\",\"选项2\",\"选项3\"], "
    "\"scene\":{\"location\":\"\",\"time\":\"\",\"atmosphere\":\"\",\"environment\":\"\","
    "\"npcs\":[{\"name\":\"\",\"role\":\"\",\"attitude\":\"\",\"ac\":0,\"hp\":0}],\"exits\":[\"可做之事1\"],\"situation\":\"\"}}"
)


def open_campaign(setting: str, tone: str, campaign_id: int, character_id: int) -> dict:
    """跑团开场：DM 据世界设定生成完整背景+当前场景，持久化 Campaign.setting + Scene。

    返回 {narration, scene}。narration 是 DM 呈现的开场（背景+场景）。
    """
    ch = store.get_character(character_id)
    ch_desc = f"{ch.name}({ch.race}{ch.char_class}Lv{ch.level})" if ch else "冒险者"
    raw = llm.chat(SCENE_FRAMING_PROMPT,
                   f"世界设定:\n{setting}\n基调:{tone or '未指定'}\n角色:{ch_desc}",
                   temperature=0.6)
    obj = _extract_json(raw)
    # 持久化设定 + 场景
    store.set_campaign_setting(campaign_id, setting, tone)
    sc = store.get_scene(campaign_id) or models.Scene(campaign_id=campaign_id)
    s = obj.get("scene", {})
    sc.location = s.get("location", "")
    sc.time = s.get("time", "")
    sc.atmosphere = s.get("atmosphere", "")
    sc.environment = s.get("environment", "")
    sc.situation = s.get("situation", obj.get("narration", "")[:300])
    sc.set_npcs(s.get("npcs", []))
    sc.set_exits(s.get("exits", []))
    store.save_scene(sc)
    return {"narration": obj.get("narration", raw[:300]),
            "action_options": obj.get("action_options", []),
            "scene": s}


def scene_context(campaign_id: int) -> str:
    """取当前场景格式化串（供 narrate prompt 用，让 DM 在场景中叙事而非虚空）。"""
    sc = store.get_scene(campaign_id)
    if not sc:
        return "(尚无场景，需先 /open 开场)"
    npc_names = [n.get("name", "") for n in sc.npcs] if sc.npcs else []
    return (f"当前场景——地点:{sc.location} 时间:{sc.time} 氛围:{sc.atmosphere} "
            f"环境:{sc.environment} 在场:{npc_names} 可做之事:{sc.exits} "
            f"场景叙事:{sc.situation[:200]}")


def get_scene(campaign_id: int) -> dict:
    """取当前场景（给前端场景面板）。"""
    sc = store.get_scene(campaign_id)
    if not sc:
        return {}
    return {"location": sc.location, "time": sc.time, "atmosphere": sc.atmosphere,
            "environment": sc.environment, "npcs": sc.npcs, "exits": sc.exits,
            "situation": sc.situation}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    import os
    os.makedirs("data/saves", exist_ok=True)
    # 老库由 store._migrate 自动补列（setting/atmosphere/situation/exits）
    camp = store.create_campaign("世界层测")
    ch = models.Character(name="阿拉贡", race="人类", char_class="战士", level=5, campaign_id=camp.id)
    ch.set_abilities({"str": 16, "dex": 10, "con": 15, "int": 10, "wis": 12, "cha": 10})
    ch.hp_max = 38; ch.hp_current = 38; ch.ac = 18
    ch = store.save_character(ch)
    setting = ("被诅咒的村庄黑木镇：三周前镇民开始失踪，夜里能听见地底传来的钟声。"
               "镇长悬赏冒险者查清真相。村庄北缘有一座废弃神殿，地窖入口半掩在藤蔓下。")
    r = open_campaign(setting, "黑暗调查", camp.id, ch.id)
    print("=== DM 开场（完整背景+场景）===")
    print(r["narration"])
    print("\n=== 场景结构 ===")
    print("地点:", r["scene"].get("location"), "| 时间:", r["scene"].get("time"))
    print("氛围:", r["scene"].get("atmosphere"))
    print("在场NPC:", r["scene"].get("npcs"))
    print("可做之事:", r["scene"].get("exits"))
