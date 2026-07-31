"""反应时点触发系统 — 反应法术/特性的触发条件注册与匹配。

规则依据:
  - R-CMB-013 反应经济（每回合1反应）
  - R-SPL-006 反应施法时点
  - 各反应法术/特性的触发条件描述
出处: topics/玩家手册2024/进行游戏/反应.htm ; 法术详述/1环.htm
"""

from __future__ import annotations

from dataclasses import dataclass


# ──────────────────────────────────────────────────────────────────────────
# 触发器定义
# ──────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ReactionTrigger:
    """一个反应触发器的定义。

    trigger_type: 触发事件类型标识
    condition: 额外条件描述（如"60尺内可见"）
    reaction_name: 反应名称（法术/特性名）
    """
    trigger_type: str
    condition: str
    reaction_name: str


# 已知反应触发器表（可扩展）
KNOWN_REACTION_TRIGGERS: dict[str, ReactionTrigger] = {
    "护盾术": ReactionTrigger(
        trigger_type="hit_by_attack",
        condition="被攻击命中时（包括触发的攻击）",
        reaction_name="护盾术",
    ),
    "法术反制": ReactionTrigger(
        trigger_type="creature_cast_spell",
        condition="60尺内可见生物施展法术时",
        reaction_name="法术反制",
    ),
    "借机攻击": ReactionTrigger(
        trigger_type="creature_leaves_reach",
        condition="可见生物离开你的触及范围时",
        reaction_name="借机攻击",
    ),
    "吸收元素": ReactionTrigger(
        trigger_type="take_elemental_damage",
        condition="受到强酸/寒冷/火焰/闪电/雷鸣伤害时",
        reaction_name="吸收元素",
    ),
    "羽落术": ReactionTrigger(
        trigger_type="falling",
        condition="自己或60尺内可见生物坠落时",
        reaction_name="羽落术",
    ),
}


# ──────────────────────────────────────────────────────────────────────────
# 触发匹配
# ──────────────────────────────────────────────────────────────────────────

def check_trigger(trigger: ReactionTrigger, event: dict) -> bool:
    """判断事件是否满足触发条件。

    规则: R-SPL-006 反应施法时点 + 各法术触发条件
    出处: topics/玩家手册2024/进行游戏/反应.htm

    参数:
      trigger: 已注册的反应触发器
      event: 发生的事件 {"type": str, "target": str, "source": str, "distance_ft": float, ...}

    返回: 是否匹配触发条件
    """
    if event.get("type") != trigger.trigger_type:
        return False

    # 距离条件（如法术反制需60尺内）
    if "60尺" in trigger.condition:
        if event.get("distance_ft", 0) > 60:
            return False

    # 可见条件
    if "可见" in trigger.condition:
        if not event.get("visible", True):
            return False

    return True


def available_reactions(
    known_reactions: list[str],
    event: dict,
) -> list[str]:
    """从已知反应列表中筛选出当前事件可触发的反应名称。

    参数:
      known_reactions: 角色已知/已准备的反应列表（法术名/特性名）
      event: 发生的事件

    返回: 可触发的反应名称列表
    """
    result = []
    for name in known_reactions:
        trigger = KNOWN_REACTION_TRIGGERS.get(name)
        if trigger and check_trigger(trigger, event):
            result.append(name)
    return result


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 护盾术：被攻击命中时触发
    t = KNOWN_REACTION_TRIGGERS["护盾术"]
    assert check_trigger(t, {"type": "hit_by_attack"}) is True
    assert check_trigger(t, {"type": "creature_cast_spell"}) is False

    # 法术反制：60尺内可见施法
    t = KNOWN_REACTION_TRIGGERS["法术反制"]
    assert check_trigger(t, {"type": "creature_cast_spell", "distance_ft": 30, "visible": True}) is True
    assert check_trigger(t, {"type": "creature_cast_spell", "distance_ft": 80}) is False
    assert check_trigger(t, {"type": "creature_cast_spell", "distance_ft": 30, "visible": False}) is False

    # 借机攻击
    t = KNOWN_REACTION_TRIGGERS["借机攻击"]
    assert check_trigger(t, {"type": "creature_leaves_reach", "visible": True}) is True

    # available_reactions
    reactions = available_reactions(
        ["护盾术", "法术反制", "借机攻击"],
        {"type": "hit_by_attack"},
    )
    assert reactions == ["护盾术"]

    reactions = available_reactions(
        ["护盾术", "法术反制"],
        {"type": "creature_cast_spell", "distance_ft": 50, "visible": True},
    )
    assert reactions == ["法术反制"]

    print("[triggers] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
