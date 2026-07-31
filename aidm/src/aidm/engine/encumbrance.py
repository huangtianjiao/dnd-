"""载重与负重引擎 — 携带能力 / 推拖举 / 负重状态。

规则依据:
  - R-ENC-001 携带能力（力量值 x 15 磅）
  - R-ENC-002 推/拖/举（携带能力 x 2）
  - R-ENC-003 负重状态（超载→速度归0）
  - R-ENC-004 体型修正（微型x0.5, 小型x1, 中型x1, 大型x2, 巨型x4, 超巨x8）
出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────
# 体型倍率
# ──────────────────────────────────────────────────────────────────────────

_SIZE_MULTIPLIER = {
    "tiny": 0.5,
    "small": 1.0,
    "medium": 1.0,
    "large": 2.0,
    "huge": 4.0,
    "gargantuan": 8.0,
}


# ──────────────────────────────────────────────────────────────────────────
# 核心函数
# ──────────────────────────────────────────────────────────────────────────

def carrying_capacity(strength_score: int, size: str = "medium") -> float:
    """携带能力 = 力量值 x 15 磅 x 体型倍率。

    规则: R-ENC-001 携带能力
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    """
    mult = _SIZE_MULTIPLIER.get(size.lower(), 1.0)
    return strength_score * 15 * mult


def push_drag_lift(strength_score: int, size: str = "medium") -> float:
    """推/拖/举上限 = 携带能力 x 2。

    规则: R-ENC-002 推/拖/举
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    """
    return carrying_capacity(strength_score, size) * 2


def encumbrance_status(total_weight: float, strength_score: int,
                       size: str = "medium") -> dict:
    """根据当前负载返回负重状态与速度惩罚。

    规则: R-ENC-003 负重状态
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm

    说明:
      - 负载 ≤ 携带能力: 正常（无惩罚）
      - 负载 > 携带能力: 超载（速度归0，不能移动）
      可选变体规则（2024 简化版无中间档；保留接口供 DM 可选变体启用）:
      - 负载 > 5×力量: 轻度负重（速度-10尺）
      - 负载 > 10×力量: 重度负重（速度-20尺，攻击/属性/豁免劣势）

    返回:
      {"encumbered": bool,           # 轻度负重（变体规则）
       "heavily_encumbered": bool,   # 重度负重（变体规则）
       "overloaded": bool,           # 超载（核心规则）
       "speed_penalty": int}         # 速度减少值（尺），超载时为 -999 表示速度归0
    """
    cap = carrying_capacity(strength_score, size)
    mult = _SIZE_MULTIPLIER.get(size.lower(), 1.0)

    # 变体负重阈值（5×力量, 10×力量, 按体型修正）
    threshold_light = 5 * strength_score * mult
    threshold_heavy = 10 * strength_score * mult

    if total_weight > cap:
        return {"encumbered": True, "heavily_encumbered": True,
                "overloaded": True, "speed_penalty": -999}
    if total_weight > threshold_heavy:
        return {"encumbered": True, "heavily_encumbered": True,
                "overloaded": False, "speed_penalty": -20}
    if total_weight > threshold_light:
        return {"encumbered": True, "heavily_encumbered": False,
                "overloaded": False, "speed_penalty": -10}
    return {"encumbered": False, "heavily_encumbered": False,
            "overloaded": False, "speed_penalty": 0}


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 携带能力
    assert carrying_capacity(10) == 150.0         # 10x15=150
    assert carrying_capacity(20) == 300.0
    assert carrying_capacity(10, "tiny") == 75.0  # x0.5
    assert carrying_capacity(10, "large") == 300.0  # x2

    # 推拖举
    assert push_drag_lift(10) == 300.0            # 150x2
    assert push_drag_lift(10, "large") == 600.0

    # 负重状态：正常
    r = encumbrance_status(40, 10)
    assert not r["encumbered"] and r["speed_penalty"] == 0

    # 负重状态：超载
    r = encumbrance_status(200, 10)  # 200 > 150(cap)
    assert r["overloaded"] and r["speed_penalty"] == -999

    # 负重状态：轻度（变体）
    r = encumbrance_status(60, 10)   # 60 > 50(5x10) 且 ≤100(10x10)
    assert r["encumbered"] and not r["heavily_encumbered"]
    assert r["speed_penalty"] == -10

    # 负重状态：重度（变体）
    r = encumbrance_status(120, 10)  # 120 > 100(10x10) 且 ≤150(cap)
    assert r["heavily_encumbered"] and r["speed_penalty"] == -20

    print("[encumbrance] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
