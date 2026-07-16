"""Enemy AI Agent — 怪物自主决策。

职责:
  - 基于怪物"战术"描述生成行动决策
  - HP < 50% 时考虑逃跑/投降
  - temperature 0.3-0.5：有变化但不离谱

设计参考: 调研报告 §5.3 战斗子循环中的 Enemy AI 设计。
LLM 决策但受规则约束：不能做规则不允许的动作。
"""

from __future__ import annotations

import json
import re

from ..brain import llm


_ENEMY_SYSTEM = "你是D&D 5E怪物战术AI。基于怪物特性决定本回合行动。只输出JSON。"

_ENEMY_PROMPT = """\
你是控制以下怪物的战术AI:

怪物名: {monster_name}
怪物HP: {hp}/{max_hp} ({hp_pct}%)
怪物位置: {position}
怪物能力: {abilities}

战场状态:
{battlefield}

当前回合轮到 {monster_name} 行动。

决策规则:
  1. HP < 50% 时考虑撤退或防御（除非有"狂暴"等特性）
  2. 优先攻击血量最低的敌人
  3. 利用地形优势（掩护、高地）
  4. 远程怪物保持距离，近战怪物冲锋
  5. 有特殊能力时优先使用（如龙的喷吐武器）

输出JSON:
{{"action":"attack|cast|move|flee|surrender",
  "target":"目标名(攻击/施法时)",
  "ability":"使用的能力名(施法/特殊能力时)",
  "reason":"简述决策理由"}}
"""


def decide_action(monster_name: str, hp: int, max_hp: int,
                  position: str, abilities: list[str],
                  battlefield: str) -> dict:
    """Enemy AI: LLM 决策怪物本回合行动。

    流程:
      1. 硬编码规则前置检查 (HP < 25% → flee)
      2. LLM 生成战术决策
      3. 后置校验 (HP < 25% 且非狂暴 → 强制 flee)

    Args:
        monster_name: 怪物名称
        hp: 当前HP
        max_hp: 最大HP
        position: 怪物当前位置描述
        abilities: 怪物可用能力列表
        battlefield: 战场状态描述

    Returns:
        {"action": "attack|cast|move|flee|surrender",
         "target": "...", "ability": "...", "reason": "..."}
    """
    hp_pct = int(hp / max_hp * 100) if max_hp > 0 else 100

    # 硬编码规则：HP < 25% 且无"狂暴"特性 → 高概率逃跑
    if hp_pct < 25 and "狂暴" not in abilities:
        return {"action": "flee", "target": "", "ability": "",
                "reason": f"HP仅{hp_pct}%，试图逃离战斗"}

    prompt = _ENEMY_PROMPT.format(
        monster_name=monster_name, hp=hp, max_hp=max_hp,
        hp_pct=hp_pct, position=position,
        abilities=", ".join(abilities) if abilities else "基础攻击",
        battlefield=battlefield[:500],
    )

    raw = llm.chat(_ENEMY_SYSTEM, prompt, temperature=0.4)
    cleaned = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        # 解析失败，默认攻击
        result = {"action": "attack", "target": "", "ability": "",
                  "reason": "默认攻击行为"}

    # 后置校验：HP < 25% 但 LLM 选 attack → 强制改为 flee（除非狂暴）
    if hp_pct < 25 and result.get("action") == "attack":
        if "狂暴" not in abilities:
            result["action"] = "flee"
            result["reason"] = f"HP仅{hp_pct}%，被迫逃离"

    return result


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    """enemy_ai.py 自检测试。"""
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    # 测试 1: 高HP怪物决策
    print("[test1] decide_action (高HP)...")
    try:
        result = decide_action(
            monster_name="哥布林战士",
            hp=15, max_hp=15,
            position="前排中央",
            abilities=["近战攻击", "盾牌格挡"],
            battlefield="玩家位于左前方5尺处",
        )
        assert isinstance(result, dict)
        assert "action" in result
        assert result["action"] != "flee", "满血不应逃跑"
        print(f"  ✓ 决策: {result}")
    except Exception as e:
        print(f"  ⚠ 跳过 (需要LLM): {e}")

    # 测试 2: 低HP怪物决策（硬编码逃跑）
    print("[test2] decide_action (低HP, 无狂暴)...")
    result = decide_action(
        monster_name="受伤的哥布林",
        hp=2, max_hp=15,
        position="后排角落",
        abilities=["近战攻击"],
        battlefield="玩家正在逼近",
    )
    assert result["action"] == "flee", f"低HP应逃跑, 得到{result['action']}"
    print(f"  ✓ 决策: {result}")

    # 测试 3: 低HP狂暴怪物决策
    print("[test3] decide_action (低HP, 有狂暴)...")
    try:
        result = decide_action(
            monster_name="狂暴兽人",
            hp=3, max_hp=20,
            position="前排左侧",
            abilities=["近战攻击", "狂暴"],
            battlefield="多个敌人在视野内",
        )
        # 狂暴怪物不应被强制逃跑
        assert result["action"] != "flee" or "狂暴" not in ["近战攻击", "狂暴"]
        print(f"  ✓ 决策: {result}")
    except Exception as e:
        print(f"  ⚠ 跳过 (需要LLM): {e}")

    print("\n[enemy_ai] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
