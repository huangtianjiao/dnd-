"""动态图片生成 — 叙事过程中插图。

职责:
  - 根据叙事内容生成场景插图
  - 根据战斗状态生成战术地图（ASCII）
  - 角色卡可视化

设计参考: 调研报告 §1.5 交互式产物生成。
使用 LLM 从叙事中提取视觉描述，再调用图片生成API。
"""

from __future__ import annotations

from . import llm

# ──────────────────────────────────────────────────────────────────────────
# 场景插图生成
# ──────────────────────────────────────────────────────────────────────────

_SCENE_DESC_PROMPT = """\
你是D&D场景插画师。根据以下DM叙事，提取一个适合生成插画的视觉描述。
要求:
  - 用英文描述，适合 Stable Diffusion / DALL-E 风格
  - 包含: 场景类型(地牢/森林/酒馆)、光照、氛围、关键元素
  - 不包含人物（角色卡单独生成）
  - 50-80个词

DM叙事:
{narration}

输出英文视觉描述:"""


def generate_scene_description(narration: str) -> str:
    """从 DM 叙事中提取视觉描述。

    Args:
        narration: DM 叙事文本

    Returns:
        英文视觉描述字符串，失败时返回空字符串。
    """
    if not narration or len(narration) < 10:
        return ""

    raw = llm.chat(
        "你是D&D场景插画师。只输出英文视觉描述。",
        _SCENE_DESC_PROMPT.format(narration=narration[:500]),
        temperature=0.4,
    )

    # 清理输出
    desc = raw.strip()
    if desc.startswith("```"):
        desc = desc.split("\n", 1)[-1].rsplit("```", 1)[0]
    return desc.strip()


def generate_scene_image(narration: str,
                         output_path: str | None = None) -> dict:
    """生成场景插图。

    流程:
      1. 从叙事提取视觉描述 (LLM)
      2. 调用图片生成 API (待接入)

    Args:
        narration: DM 叙事文本
        output_path: 图片保存路径，None 则不保存

    Returns:
        {"description": "...", "image_url": "...", "path": "..."}
    """
    desc = generate_scene_description(narration)

    # TODO: 接入实际图片生成 API
    # 当前返回描述供前端自行渲染
    return {
        "description": desc,
        "image_url": "",  # 待接入
        "path": output_path or "",
    }


# ──────────────────────────────────────────────────────────────────────────
# 战术地图渲染（ASCII）
# ──────────────────────────────────────────────────────────────────────────

def render_battlefield_ascii(width: int = 20, height: int = 15,
                             combatants: list[dict] = None,
                             obstacles: list[dict] = None) -> str:
    """渲染 ASCII 战术地图。

    符号:
      .  空地
      #  墙壁/障碍
      P  玩家
      E  敌方
      N  NPC

    Args:
        width: 地图宽度（字符数）
        height: 地图高度（行数）
        combatants: 参战者列表 [{"name":"...", "side":"player|enemy",
                   "position":[x,y]}]
        obstacles: 障碍物列表 [{"position":[x,y], "type":"wall"}]

    Returns:
        ASCII 地图字符串
    """
    # 初始化空地图
    grid = [["." for _ in range(width)] for _ in range(height)]

    # 放置障碍物
    if obstacles:
        for obs in obstacles:
            pos = obs.get("position", [0, 0])
            x, y = pos[0], pos[1]
            if 0 <= x < width and 0 <= y < height:
                grid[y][x] = "#"

    # 放置参战者
    if combatants:
        for c in combatants:
            pos = c.get("position", [0, 0])
            x, y = pos[0], pos[1]
            if 0 <= x < width and 0 <= y < height:
                side = c.get("side", "player")
                if side == "player":
                    grid[y][x] = "P"
                elif side == "enemy":
                    grid[y][x] = "E"
                else:
                    grid[y][x] = "N"

    # 渲染为字符串
    lines = []
    # 上边框
    lines.append("+" + "-" * width + "+")
    for row in grid:
        lines.append("|" + "".join(row) + "|")
    # 下边框
    lines.append("+" + "-" * width + "+")

    # 添加图例
    lines.append("")
    lines.append("图例: P=玩家 E=敌方 #=障碍 .=空地")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    """image_gen.py 自检测试。"""
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    # 测试 1: generate_scene_description
    print("[test1] generate_scene_description...")
    try:
        desc = generate_scene_description(
            "你走进了一个阴暗的地牢，墙壁上爬满了藤蔓，"
            "远处传来水滴声。空气中弥漫着腐朽的气味。"
        )
        assert isinstance(desc, str), f"期望str, 得到{type(desc)}"
        print(f"  ✓ 描述生成: {desc[:60]}...")
    except Exception as e:
        print(f"  ⚠ 跳过 (需要LLM): {e}")

    # 测试 2: render_battlefield_ascii
    print("[test2] render_battlefield_ascii...")
    battlefield = render_battlefield_ascii(
        width=10, height=6,
        combatants=[
            {"name": "勇者", "side": "player", "position": [1, 1]},
            {"name": "哥布林", "side": "enemy", "position": [8, 4]},
        ],
        obstacles=[
            {"position": [5, 2], "type": "wall"},
            {"position": [5, 3], "type": "wall"},
        ],
    )
    assert isinstance(battlefield, str)
    assert "P" in battlefield  # 玩家标记
    assert "E" in battlefield  # 敌方标记
    assert "#" in battlefield  # 障碍标记
    print("  ✓ ASCII 地图渲染成功:")
    print(battlefield)

    # 测试 3: generate_scene_image
    print("[test3] generate_scene_image...")
    result = generate_scene_image("你看到了一座古老的祭坛。")
    assert isinstance(result, dict)
    assert "description" in result
    assert "image_url" in result
    print(f"  ✓ 返回结构: {list(result.keys())}")

    print("\n[image_gen] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
