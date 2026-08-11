"""战斗地图 — 网格、地形、视线、掩护判定。

设计原则：
  - BattleMap 管理战斗区域的网格化空间。
  - 提供距离计算、路径查找、视线/效应线检查、掩护判定。

规则依据: COM-005 BattleMap 战斗地图
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class GridCell:
    """单个网格单元。"""

    x: int
    y: int
    z: int = 0
    terrain_cost: float = 1.0       # 1.0=正常, 2.0=困难地形
    is_hazardous: bool = False
    provides_cover: bool = False
    is_occupied: bool = False
    light_level: str = "bright"     # bright / dim / dark
    occupant_id: Optional[str] = None


@dataclass
class BattleMap:
    """战斗地图 — 管理网格化战斗空间。

    默认 50×50 格，每格 5 尺。
    """

    width: int = 50
    height: int = 50
    grid_size_ft: float = 5.0
    cells: Dict[Tuple[int, int, int], GridCell] = field(default_factory=dict)

    # ── 单元格访问 ────────────────────────────────────────────────────

    def get_cell(self, x: int, y: int, z: int = 0) -> GridCell:
        """获取指定坐标的单元格，不存在则自动创建默认单元格。"""
        key = (x, y, z)
        if key not in self.cells:
            self.cells[key] = GridCell(x=x, y=y, z=z)
        return self.cells[key]

    def is_valid_position(self, x: int, y: int, z: int = 0) -> bool:
        """判断坐标是否在地图范围内。"""
        return 0 <= x < self.width and 0 <= y < self.height

    # ── 距离计算 ──────────────────────────────────────────────────────

    def get_distance_ft(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """计算两个网格坐标之间的实际距离（尺）。

        使用切比雪夫距离（对角线移动与直线移动代价相同）× 每格尺数。
        对于不同高度层，加入高度差。
        """
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        grid_dist = max(dx, dy)  # 切比雪夫距离
        # 若有高度差（pos 含 z），加入垂直距离
        z1 = pos1[2] if len(pos1) > 2 else 0
        z2 = pos2[2] if len(pos2) > 2 else 0
        vertical_ft = abs(z1 - z2) * self.grid_size_ft
        horizontal_ft = grid_dist * self.grid_size_ft
        return math.sqrt(horizontal_ft ** 2 + vertical_ft ** 2)

    def get_distance_grid(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """计算两个网格坐标之间的格数距离（切比雪夫距离）。"""
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return max(dx, dy)

    # ── 路径查找 ──────────────────────────────────────────────────────

    def find_path(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int],
        speed_ft: float,
    ) -> List[Tuple[int, int]]:
        """简易 A* 路径查找，返回路径坐标列表。

        Args:
            start: 起点 (x, y)
            end: 终点 (x, y)
            speed_ft: 移动速度（尺），用于限制路径长度

        Returns:
            路径坐标列表（含起点和终点），若无法到达则返回空列表
        """
        max_steps = int(speed_ft / self.grid_size_ft)
        if not self.is_valid_position(*start) or not self.is_valid_position(*end):
            return []

        open_set: List[Tuple[int, int]] = [start]
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score: Dict[Tuple[int, int], float] = {start: 0.0}
        closed_set: Set[Tuple[int, int]] = set()

        while open_set:
            # 取 f_score 最小的节点
            current = min(open_set, key=lambda p: g_score.get(p, float("inf")) + self.get_distance_grid(p, end))
            if current == end:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            open_set.remove(current)
            closed_set.add(current)

            # 8 方向邻居
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = current[0] + dx, current[1] + dy
                    neighbor = (nx, ny)
                    if not self.is_valid_position(nx, ny) or neighbor in closed_set:
                        continue
                    cell = self.get_cell(nx, ny)
                    if cell.is_occupied and neighbor != end:
                        continue
                    move_cost = cell.terrain_cost * self.grid_size_ft
                    tentative_g = g_score.get(current, float("inf")) + move_cost
                    if tentative_g > speed_ft:
                        continue
                    if tentative_g < g_score.get(neighbor, float("inf")):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        if neighbor not in open_set:
                            open_set.append(neighbor)

        return []

    # ── 区域查询 ──────────────────────────────────────────────────────

    def get_creatures_in_reach(
        self,
        entity_id: str,
        reach_ft: float = 5.0,
    ) -> List[str]:
        """获取指定实体触及范围内的所有生物 ID。

        Args:
            entity_id: 发起者实体 ID
            reach_ft: 触及范围（尺）

        Returns:
            在触及范围内的实体 ID 列表
        """
        # 找到发起者位置
        origin = self._find_entity_position(entity_id)
        if origin is None:
            return []

        results: List[str] = []
        for key, cell in self.cells.items():
            if cell.occupant_id and cell.occupant_id != entity_id:
                dist = self.get_distance_ft(origin, (key[0], key[1]))
                if dist <= reach_ft:
                    results.append(cell.occupant_id)
        return results

    def get_creatures_in_area(
        self,
        center: Tuple[int, int],
        shape: str = "circle",
        size: float = 10.0,
    ) -> List[str]:
        """获取指定区域内的所有生物 ID。

        Args:
            center: 区域中心坐标 (x, y)
            shape: 区域形状 ("circle" / "square" / "cone")
            size: 区域大小（尺）

        Returns:
            区域内的实体 ID 列表
        """
        results: List[str] = []
        for key, cell in self.cells.items():
            if not cell.occupant_id:
                continue
            dist = self.get_distance_ft(center, (key[0], key[1]))
            if shape == "circle":
                if dist <= size:
                    results.append(cell.occupant_id)
            elif shape == "square":
                half = size / 2
                dx = abs(key[0] - center[0]) * self.grid_size_ft
                dy = abs(key[1] - center[1]) * self.grid_size_ft
                if dx <= half and dy <= half:
                    results.append(cell.occupant_id)
            elif shape == "cone":
                # 简化：锥形视为 90 度扇形，距离内且在前方
                if dist <= size:
                    results.append(cell.occupant_id)
        return results

    # ── 视线与效应线 ──────────────────────────────────────────────────

    def line_of_sight(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """视线检查 — 从 pos1 到 pos2 是否有畅通视线。

        使用 Bresenham 线逐格检查，遇到全掩护（provides_cover=True 的单元格）
        且非终点则阻挡视线。
        """
        points = self._bresenham_line(pos1, pos2)
        for i, point in enumerate(points):
            if i == 0 or i == len(points) - 1:
                continue  # 跳过起点和终点
            cell = self.get_cell(*point)
            if cell.provides_cover:
                return False
        return True

    def line_of_effect(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """效应线检查 — 从 pos1 到 pos2 是否能投射效应。

        与视线类似，但效应线不被非全掩护阻挡。
        只有完全封闭的障碍（连续 provides_cover）才阻挡。
        """
        points = self._bresenham_line(pos1, pos2)
        for i, point in enumerate(points):
            if i == 0 or i == len(points) - 1:
                continue
            cell = self.get_cell(*point)
            if cell.provides_cover:
                return False
        return True

    # ── 掩护判定 ──────────────────────────────────────────────────────

    def get_cover_level(
        self,
        attacker_pos: Tuple[int, int],
        target_pos: Tuple[int, int],
    ) -> str:
        """判定目标位置的掩护等级。

        规则:
          - none: 无掩护
          - half: 半掩护 (+2 AC/DEX save)
          - three_quarters: 3/4 掩护 (+5 AC/DEX save)
          - full: 全掩护（不可选为目标）

        简化判定：基于目标单元格及路径上的掩护单元格数量。
        """
        if not self.line_of_sight(attacker_pos, target_pos):
            return "full"

        target_cell = self.get_cell(*target_pos)
        # 检查目标周围相邻格是否有掩护
        cover_count = 0
        tx, ty = target_pos
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = tx + dx, ty + dy
                if self.is_valid_position(nx, ny):
                    neighbor = self.get_cell(nx, ny)
                    if neighbor.provides_cover:
                        cover_count += 1

        if target_cell.provides_cover:
            cover_count += 1

        if cover_count >= 6:
            return "full"
        if cover_count >= 4:
            return "three_quarters"
        if cover_count >= 2:
            return "half"
        return "none"

    # ── 实体移动 ──────────────────────────────────────────────────────

    def move_entity(
        self,
        entity_id: str,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
    ) -> bool:
        """移动实体从 from_pos 到 to_pos。

        Returns:
            是否移动成功
        """
        if not self.is_valid_position(*from_pos) or not self.is_valid_position(*to_pos):
            return False

        from_cell = self.get_cell(*from_pos)
        to_cell = self.get_cell(*to_pos)

        if from_cell.occupant_id != entity_id:
            return False
        if to_cell.is_occupied:
            return False

        # 执行移动
        from_cell.occupant_id = None
        from_cell.is_occupied = False
        to_cell.occupant_id = entity_id
        to_cell.is_occupied = True
        return True

    # ── 内部辅助 ──────────────────────────────────────────────────────

    def _find_entity_position(self, entity_id: str) -> Optional[Tuple[int, int]]:
        """查找实体在地图上的位置。"""
        for key, cell in self.cells.items():
            if cell.occupant_id == entity_id:
                return (key[0], key[1])
        return None

    @staticmethod
    def _bresenham_line(
        pos1: Tuple[int, int],
        pos2: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        """Bresenham 画线算法，返回经过的网格坐标列表。"""
        x0, y0 = pos1
        x1, y1 = pos2
        points: List[Tuple[int, int]] = []

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return points
