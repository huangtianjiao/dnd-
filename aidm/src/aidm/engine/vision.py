"""视野与光照引擎 — 光照等级 / 遮蔽 / 特殊感官判定。

规则依据:
  - R-VIS-001 光照三级（明亮/微光/黑暗）
  - R-VIS-002 遮蔽区域（轻度→察觉劣势，重度→目盲）
  - R-VIS-003 黑暗视觉（范围内黑暗视为微光，微光视为明亮）
  - R-VIS-004 盲视 / R-VIS-005 真实视觉 / R-VIS-006 颤动感知
出处: topics/玩家手册2024/进行游戏/视野与光照.htm ; 术语汇编/光照与视觉.htm
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────
# 光照等级
# ──────────────────────────────────────────────────────────────────────────

LIGHT_BRIGHT = "bright"
LIGHT_DIM = "dim"
LIGHT_DARK = "darkness"

# ──────────────────────────────────────────────────────────────────────────
# 遮蔽
# ──────────────────────────────────────────────────────────────────────────

OBSCURE_NONE = "none"
OBSCURE_LIGHT = "lightly_obscured"
OBSCURE_HEAVY = "heavily_obscured"


def obscurement_from_light(light_level: str) -> str:
    """光照等级 → 遮蔽等级。

    规则: R-VIS-002 遮蔽区域
          明亮=无遮蔽；微光=轻度遮蔽；黑暗=重度遮蔽。
    出处: topics/玩家手册2024/进行游戏/视野与光照.htm
    """
    if light_level == LIGHT_BRIGHT:
        return OBSCURE_NONE
    if light_level == LIGHT_DIM:
        return OBSCURE_LIGHT
    return OBSCURE_HEAVY


# ──────────────────────────────────────────────────────────────────────────
# 黑暗视觉
# ──────────────────────────────────────────────────────────────────────────

def darkvision_effective_light(base_light: str, darkvision_range_ft: float,
                               distance_ft: float) -> str:
    """黑暗视觉下的有效光照等级。

    规则: R-VIS-003 黑暗视觉
          在黑暗视觉范围内：黑暗视为微光，微光视为明亮。
          超出范围：按正常光照。
    出处: topics/玩家手册2024/术语汇编/光照与视觉.htm
    """
    if distance_ft > darkvision_range_ft:
        return base_light
    if base_light == LIGHT_DARK:
        return LIGHT_DIM
    if base_light == LIGHT_DIM:
        return LIGHT_BRIGHT
    return LIGHT_BRIGHT


# ──────────────────────────────────────────────────────────────────────────
# 综合视觉判定
# ──────────────────────────────────────────────────────────────────────────

def can_see(
    observer_senses: dict,
    target_light: str,
    distance_ft: float,
) -> dict:
    """判断观察者能否看见目标（含黑暗视觉/盲视/真实视觉/颤动感知）。

    规则: R-VIS-001~006
    出处: topics/玩家手册2024/进行游戏/视野与光照.htm ; 术语汇编/光照与视觉.htm

    参数:
      observer_senses: {
          "darkvision_ft": float,   # 黑暗视觉范围（0=无）
          "blindsight_ft": float,   # 盲视范围（0=无）
          "truesight_ft": float,    # 真实视觉范围（0=无）
          "tremorsense_ft": float,  # 颤动感知范围（0=无）
          "on_ground": bool,        # 观察者是否接触地面（颤动感知需要）
      }
      target_light: 目标所在位置的基础光照等级
      distance_ft: 观察者与目标之间的距离（尺）

    返回:
      {"can_see": bool,                   # 能否视觉感知目标
       "disadvantage_perception": bool,   # 感知（察觉）检定是否劣势
       "effectively_blinded": bool,       # 是否等效目盲
       "sense_used": str}                 # 使用的感官类型
    """
    dv = observer_senses.get("darkvision_ft", 0)
    bs = observer_senses.get("blindsight_ft", 0)
    ts = observer_senses.get("truesight_ft", 0)
    trem = observer_senses.get("tremorsense_ft", 0)
    on_ground = observer_senses.get("on_ground", True)

    # 真实视觉：范围内无视黑暗/隐形/幻术
    if ts > 0 and distance_ft <= ts:
        return {"can_see": True, "disadvantage_perception": False,
                "effectively_blinded": False, "sense_used": "truesight"}

    # 盲视：范围内无需视觉
    if bs > 0 and distance_ft <= bs:
        return {"can_see": True, "disadvantage_perception": False,
                "effectively_blinded": False, "sense_used": "blindsight"}

    # 颤动感知：范围内+接触地面可感知（非视觉，但可定位）
    if trem > 0 and distance_ft <= trem and on_ground:
        return {"can_see": True, "disadvantage_perception": False,
                "effectively_blinded": False, "sense_used": "tremorsense"}

    # 普通视觉 + 黑暗视觉
    effective_light = target_light
    if dv > 0:
        effective_light = darkvision_effective_light(target_light, dv, distance_ft)

    obscure = obscurement_from_light(effective_light)

    if obscure == OBSCURE_HEAVY:
        return {"can_see": False, "disadvantage_perception": True,
                "effectively_blinded": True, "sense_used": "normal_vision"}
    if obscure == OBSCURE_LIGHT:
        return {"can_see": True, "disadvantage_perception": True,
                "effectively_blinded": False, "sense_used": "normal_vision"}
    return {"can_see": True, "disadvantage_perception": False,
            "effectively_blinded": False, "sense_used": "normal_vision"}


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 遮蔽映射
    assert obscurement_from_light(LIGHT_BRIGHT) == OBSCURE_NONE
    assert obscurement_from_light(LIGHT_DIM) == OBSCURE_LIGHT
    assert obscurement_from_light(LIGHT_DARK) == OBSCURE_HEAVY

    # 黑暗视觉有效光照
    assert darkvision_effective_light(LIGHT_DARK, 60, 30) == LIGHT_DIM
    assert darkvision_effective_light(LIGHT_DIM, 60, 30) == LIGHT_BRIGHT
    assert darkvision_effective_light(LIGHT_DARK, 60, 80) == LIGHT_DARK  # 超范围

    # can_see：明亮
    r = can_see({"darkvision_ft": 0}, LIGHT_BRIGHT, 30)
    assert r["can_see"] and not r["disadvantage_perception"]

    # can_see：微光→察觉劣势
    r = can_see({"darkvision_ft": 0}, LIGHT_DIM, 30)
    assert r["can_see"] and r["disadvantage_perception"]

    # can_see：黑暗无黑暗视觉→目盲
    r = can_see({"darkvision_ft": 0}, LIGHT_DARK, 30)
    assert not r["can_see"] and r["effectively_blinded"]

    # can_see：黑暗+黑暗视觉60尺→微光（轻度遮蔽，察觉劣势）
    r = can_see({"darkvision_ft": 60}, LIGHT_DARK, 30)
    assert r["can_see"] and r["disadvantage_perception"]

    # can_see：盲视范围内黑暗→可视
    r = can_see({"blindsight_ft": 30}, LIGHT_DARK, 20)
    assert r["can_see"] and r["sense_used"] == "blindsight"

    # can_see：颤动感知
    r = can_see({"tremorsense_ft": 60, "on_ground": True}, LIGHT_DARK, 30)
    assert r["can_see"] and r["sense_used"] == "tremorsense"
    r = can_see({"tremorsense_ft": 60, "on_ground": False}, LIGHT_DARK, 30)
    assert not r["can_see"]  # 未接触地面

    # can_see：真实视觉
    r = can_see({"truesight_ft": 120}, LIGHT_DARK, 60)
    assert r["can_see"] and r["sense_used"] == "truesight"

    print("[vision] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
