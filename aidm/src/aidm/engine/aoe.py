"""效应区域（Area of Effect）判定引擎 — 6 种形状覆盖计算。

提供 6 种 AoE 形状的"哪些位置在效应区域内"判定：
球形(Sphere) / 锥形(Cone) / 立方(Cube) / 柱形(Cylinder) / 光环(Emanation) / 线形(Line)。
以及全身掩护阻挡效应线的遮挡检查。

基于方格地图（5尺/格），使用欧氏距离判定。

规则依据:
  - R-AOE-001~006 效应区域六种形状
    出处: topics/玩家手册2024/术语汇编/效应区域.htm
  - R-AOE-007 效应线与全身掩护阻挡
    出处: topics/玩家手册2024/术语汇编/效应区域.htm（"无法画出未被阻挡的直线"条款）

坐标约定: 位置用 (x, y) 元组表示（单位: 尺）；3D 判定用 (x, y, z)。
"""

from __future__ import annotations

import math


# ──────────────────────────────────────────────────────────────────────────
# 距离计算
# ──────────────────────────────────────────────────────────────────────────

def _distance_2d(a: tuple[float, float], b: tuple[float, float]) -> float:
    """2D 欧氏距离（尺）。"""
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _distance_3d(a: tuple, b: tuple) -> float:
    """3D 欧氏距离（尺）。z 缺失视为 0。"""
    ax, ay, az = (a[0], a[1], a[2] if len(a) > 2 else 0)
    bx, by, bz = (b[0], b[1], b[2] if len(b) > 2 else 0)
    return math.sqrt((bx - ax) ** 2 + (by - ay) ** 2 + (bz - az) ** 2)


# ──────────────────────────────────────────────────────────────────────────
# 全身掩护阻挡（效应线检查）
# ──────────────────────────────────────────────────────────────────────────

def is_blocked_by_total_cover(
    origin: tuple[float, float],
    target: tuple[float, float],
    obstacles: list[tuple[float, float]],
    obstacle_radius: float = 2.5,
) -> bool:
    """判断从源点到目标的效应线是否被全身掩护障碍物阻挡。

    规则: R-AOE-007 效应线与全身掩护阻挡
          「如果从源点到效应区域内的某处位置之间，无法画出任何一条未被
          障碍物阻挡的直线，那么该处位置就不被视为效应区域的一部分。
          只有提供全身掩护的障碍物能够阻挡这些直线。」
    出处: topics/玩家手册2024/术语汇编/效应区域.htm

    简化模型: 障碍物视为圆形（半径 obstacle_radius，默认 2.5 尺=半格），
    判断线段 origin→target 是否穿过任何障碍物圆。
    """
    ox, oy = origin
    tx, ty = target
    dx, dy = tx - ox, ty - oy
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq < 0.01:
        return False  # 源点与目标重合

    for obs in obstacles:
        # 点到线段的最近点参数 t ∈ [0,1]
        cx, cy = obs
        t = max(0, min(1, ((cx - ox) * dx + (cy - oy) * dy) / seg_len_sq))
        closest_x = ox + t * dx
        closest_y = oy + t * dy
        dist_sq = (cx - closest_x) ** 2 + (cy - closest_y) ** 2
        if dist_sq <= obstacle_radius ** 2:
            return True  # 被阻挡
    return False


# ──────────────────────────────────────────────────────────────────────────
# 球形 Sphere
# ──────────────────────────────────────────────────────────────────────────

def targets_in_sphere(
    origin: tuple[float, float],
    radius_ft: float,
    all_positions: dict[str, tuple[float, float]],
    obstacles: list[tuple[float, float]] | None = None,
) -> list[str]:
    """球形效应区域：返回半径内且未被全身掩护阻挡的目标 ID 列表。

    规则: R-AOE-006 球形（Sphere）
          以源点向所有方向沿直线扩散形成的球体区域。源点包含在区域内。
    出处: topics/玩家手册2024/术语汇编/效应区域.htm
    说明: 使用 2D 距离（忽略高度）。如需 3D 判定传 3-元组坐标。
    """
    obstacles = obstacles or []
    result = []
    for cid, pos in all_positions.items():
        dist = _distance_2d(origin, pos)
        if dist <= radius_ft:
            if not is_blocked_by_total_cover(origin, pos, obstacles):
                result.append(cid)
    return result


# ──────────────────────────────────────────────────────────────────────────
# 锥形 Cone
# ──────────────────────────────────────────────────────────────────────────

def targets_in_cone(
    origin: tuple[float, float],
    direction: tuple[float, float],
    length_ft: float,
    all_positions: dict[str, tuple[float, float]],
    obstacles: list[tuple[float, float]] | None = None,
) -> list[str]:
    """锥形效应区域：从源点沿指定方向扩散的圆锥体。

    规则: R-AOE-001 锥形（Cone）
          锥形从源点出发，沿指定方向射线为轴，其高上任意一点的截面直径
          与该点到源点的距离相同。源点不含在区域内（除非创造者选择包含）。
    出处: topics/玩家手册2024/术语汇编/效应区域.htm

    参数:
      direction: 方向向量 (dx, dy)，不必归一化。
      length_ft: 锥形最大高度（尺）。

    判定: 目标到源点距离 ≤ length_ft，且目标相对于方向轴的偏角 ≤ arctan(0.5)
          （锥形截面直径=距离 → 半角 ≈ 26.57°）。
    """
    obstacles = obstacles or []
    # 归一化方向
    mag = math.hypot(direction[0], direction[1])
    if mag < 0.001:
        return []
    dx, dy = direction[0] / mag, direction[1] / mag
    half_angle = math.atan(0.5)  # ~26.57°

    result = []
    for cid, pos in all_positions.items():
        rx, ry = pos[0] - origin[0], pos[1] - origin[1]
        dist = math.hypot(rx, ry)
        if dist < 0.01 or dist > length_ft:
            continue
        # 计算与方向轴的夹角
        cos_angle = (rx * dx + ry * dy) / dist
        if cos_angle < math.cos(half_angle):
            continue
        if not is_blocked_by_total_cover(origin, pos, obstacles):
            result.append(cid)
    return result


# ──────────────────────────────────────────────────────────────────────────
# 线形 Line
# ──────────────────────────────────────────────────────────────────────────

def targets_in_line(
    origin: tuple[float, float],
    direction: tuple[float, float],
    length_ft: float,
    width_ft: float,
    all_positions: dict[str, tuple[float, float]],
    obstacles: list[tuple[float, float]] | None = None,
) -> list[str]:
    """线形效应区域：从源点沿直线路径传播并覆盖一定宽度的"粗线"。

    规则: R-AOE-005 线形（Line）
          从源点出发，沿一条直线路径传播，覆盖一定区域（取决于宽度）。
          源点不含在区域内（除非创造者选择包含）。
    出处: topics/玩家手册2024/术语汇编/效应区域.htm

    判定: 目标到线段的垂直距离 ≤ width_ft/2，且沿方向的投影 ∈ (0, length_ft]。
    """
    obstacles = obstacles or []
    mag = math.hypot(direction[0], direction[1])
    if mag < 0.001:
        return []
    dx, dy = direction[0] / mag, direction[1] / mag
    half_width = width_ft / 2

    result = []
    for cid, pos in all_positions.items():
        rx, ry = pos[0] - origin[0], pos[1] - origin[1]
        # 沿方向的投影
        proj = rx * dx + ry * dy
        if proj <= 0 or proj > length_ft:
            continue
        # 垂直距离
        perp = abs(rx * (-dy) + ry * dx)
        if perp > half_width:
            continue
        if not is_blocked_by_total_cover(origin, pos, obstacles):
            result.append(cid)
    return result


# ──────────────────────────────────────────────────────────────────────────
# 立方 Cube
# ──────────────────────────────────────────────────────────────────────────

def targets_in_cube(
    origin: tuple[float, float],
    size_ft: float,
    all_positions: dict[str, tuple[float, float]],
    obstacles: list[tuple[float, float]] | None = None,
) -> list[str]:
    """立方效应区域：源点在立方任意一面上。

    规则: R-AOE-002 立方（Cube）
          以源点向外扩散构成的立方体，源点在其任意一面上。
          源点不含在区域内（除非创造者选择包含）。
    出处: topics/玩家手册2024/术语汇编/效应区域.htm

    简化: 以源点为一面中心，向+x方向延伸 size_ft 的立方体。
    调用方可通过旋转坐标系适配不同方向。
    """
    obstacles = obstacles or []
    half = size_ft / 2
    result = []
    for cid, pos in all_positions.items():
        rx, ry = pos[0] - origin[0], pos[1] - origin[1]
        # x 方向 [0, size_ft]，y 方向 [-half, half]
        if 0 < rx <= size_ft and abs(ry) <= half:
            if not is_blocked_by_total_cover(origin, pos, obstacles):
                result.append(cid)
    return result


# ──────────────────────────────────────────────────────────────────────────
# 柱形 Cylinder
# ──────────────────────────────────────────────────────────────────────────

def targets_in_cylinder(
    origin: tuple[float, float],
    radius_ft: float,
    height_ft: float,
    all_positions: dict[str, tuple[float, float]],
    obstacles: list[tuple[float, float]] | None = None,
) -> list[str]:
    """柱形效应区域：源点在圆柱顶面或底面中心。

    规则: R-AOE-003 柱形（Cylinder）
          以源点向外扩散构成的圆柱体，源点在顶面或底面中心。源点含在区域内。
    出处: topics/玩家手册2024/术语汇编/效应区域.htm

    简化: 2D 判定等同于圆形（半径），高度由调用方据目标 z 坐标判断（此处忽略）。
    """
    obstacles = obstacles or []
    result = []
    for cid, pos in all_positions.items():
        dist = _distance_2d(origin, pos)
        if dist <= radius_ft:
            if not is_blocked_by_total_cover(origin, pos, obstacles):
                result.append(cid)
    return result


# ──────────────────────────────────────────────────────────────────────────
# 光环 Emanation
# ──────────────────────────────────────────────────────────────────────────

def targets_in_emanation(
    source_pos: tuple[float, float],
    radius_ft: float,
    all_positions: dict[str, tuple[float, float]],
    obstacles: list[tuple[float, float]] | None = None,
) -> list[str]:
    """光环效应区域：源自生物或物件，向外全方向扩散。

    规则: R-AOE-004 光环（Emanation）
          源自一名生物或一个物件，向外全部方向扩散。源头不含在区域内
          （除非创造者选择包含）。光环跟随源头移动。
    出处: topics/玩家手册2024/术语汇编/效应区域.htm

    说明: 几何等同于球形（以源头为中心），源头本身不在区域内。
    """
    obstacles = obstacles or []
    result = []
    for cid, pos in all_positions.items():
        dist = _distance_2d(source_pos, pos)
        if 0 < dist <= radius_ft:  # 源头不含
            if not is_blocked_by_total_cover(source_pos, pos, obstacles):
                result.append(cid)
    return result


# ──────────────────────────────────────────────────────────────────────────
# 通用分派
# ──────────────────────────────────────────────────────────────────────────

def resolve_aoe(
    shape: str,
    origin: tuple[float, float],
    size_ft: float,
    all_positions: dict[str, tuple[float, float]],
    *,
    direction: tuple[float, float] = (1.0, 0.0),
    width_ft: float = 5.0,
    height_ft: float = 0.0,
    obstacles: list[tuple[float, float]] | None = None,
) -> list[str]:
    """通用效应区域分派：根据形状名返回覆盖的目标 ID 列表。

    参数:
      shape: "sphere"/"cone"/"line"/"cube"/"cylinder"/"emanation"
      origin: 源点坐标 (x, y)（尺）
      size_ft: 主尺寸（球形=半径、锥形=高度、立方=边长、柱形=半径、光环=半径、线形=长度）
      direction: 方向向量（锥形/线形/立方用）
      width_ft: 线形宽度（尺）
      height_ft: 柱形高度（尺）
      obstacles: 全身掩护障碍物坐标列表
    """
    shape = shape.lower()
    if shape == "sphere":
        return targets_in_sphere(origin, size_ft, all_positions, obstacles)
    if shape == "cone":
        return targets_in_cone(origin, direction, size_ft, all_positions, obstacles)
    if shape == "line":
        return targets_in_line(origin, direction, size_ft, width_ft, all_positions, obstacles)
    if shape == "cube":
        return targets_in_cube(origin, size_ft, all_positions, obstacles)
    if shape == "cylinder":
        return targets_in_cylinder(origin, size_ft, height_ft, all_positions, obstacles)
    if shape == "emanation":
        return targets_in_emanation(origin, size_ft, all_positions, obstacles)
    raise ValueError(f"未知 AoE 形状 {shape!r}，可选: sphere/cone/line/cube/cylinder/emanation")


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # 球形：半径20尺
    positions = {"a": (10, 0), "b": (20, 0), "c": (25, 0), "d": (0, 0)}
    r = targets_in_sphere((0, 0), 20, positions)
    assert "a" in r and "b" in r and "d" in r and "c" not in r

    # 球形+障碍物阻挡
    r = targets_in_sphere((0, 0), 20, positions, obstacles=[(5, 0)])
    assert "a" not in r and "d" in r  # a 被(5,0)阻挡

    # 锥形：方向(1,0)，长15尺
    positions2 = {"a": (10, 0), "b": (10, 8), "c": (10, 3)}
    r = targets_in_cone((0, 0), (1, 0), 15, positions2)
    assert "a" in r       # 正前方
    assert "b" not in r   # 偏角过大（8/10 > tan(26.57°)=0.5）
    assert "c" in r       # 3/10=0.3 < 0.5

    # 线形：方向(1,0)，长100尺，宽5尺
    positions3 = {"a": (50, 0), "b": (50, 3), "c": (50, 10)}
    r = targets_in_line((0, 0), (1, 0), 100, 5, positions3)
    assert "a" in r and "b" not in r and "c" not in r  # 宽5→半宽2.5，b距3>2.5

    # 立方：边长10尺
    positions4 = {"a": (5, 3), "b": (5, 6), "c": (11, 0)}
    r = targets_in_cube((0, 0), 10, positions4)
    assert "a" in r and "b" not in r and "c" not in r  # b.y=6>5, c.x=11>10

    # 柱形（2D等同圆形）
    r = targets_in_cylinder((0, 0), 15, 20, {"a": (10, 0), "b": (16, 0)})
    assert "a" in r and "b" not in r

    # 光环（源头不含）
    r = targets_in_emanation((0, 0), 10, {"self": (0, 0), "a": (5, 0)})
    assert "self" not in r and "a" in r

    # 通用分派
    assert resolve_aoe("sphere", (0, 0), 20, {"a": (10, 0)}) == ["a"]
    assert resolve_aoe("emanation", (0, 0), 10, {"a": (5, 0)}) == ["a"]

    # 阻挡检查
    assert is_blocked_by_total_cover((0, 0), (10, 0), [(5, 0)]) is True
    assert is_blocked_by_total_cover((0, 0), (10, 0), [(5, 5)]) is False

    print("[aoe] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
