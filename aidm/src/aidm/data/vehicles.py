"""坐骑、载具与船只数据 — PHB 2024 第六章。

来源: 玩家手册2024/装备/坐骑与载具.htm
提供: 8种坐骑 + 7种陆运载具/鞍具 + 7种大型载具(含飞艇和船只)
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Mount:
    """坐骑数据模型。"""
    name: str
    name_en: str
    price_gp: float
    capacity_lb: int      # 载重（磅）
    speed: str = ""        # 速度描述


@dataclass
class TackVehicle:
    """鞍具与陆运载具。"""
    name: str
    name_en: str
    price_gp: float
    weight_lb: float
    category: str = ""     # "鞍座", "载具", "其他"


@dataclass
class LargeVehicle:
    """大型空中与水上载具。"""
    name: str
    name_en: str
    price_gp: float
    speed: str             # e.g. "8 mph"
    crew: int
    passengers: int
    cargo_tons: float      # 货物吨数
    ac: int
    hp: int
    damage_threshold: int  # 0 = 无门槛
    category: str = ""     # "空中", "水上"


# ═══════════════════════════════════════════════════════════════════════════
# 坐骑
# ═══════════════════════════════════════════════════════════════════════════

MOUNTS: dict[str, Mount] = {}

def _reg_m(m: Mount):
    MOUNTS[m.name] = m

_reg_m(Mount("大象", "Elephant", 200, 1320, speed="40尺"))
_reg_m(Mount("战马", "Warhorse", 400, 540, speed="60尺"))
_reg_m(Mount("驮用马", "Draft Horse", 50, 540, speed="40尺"))
_reg_m(Mount("乘用马", "Riding Horse", 75, 480, speed="60尺"))
_reg_m(Mount("骆驼", "Camel", 50, 450, speed="50尺"))
_reg_m(Mount("骡子", "Mule", 8, 420, speed="40尺"))
_reg_m(Mount("矮种马", "Pony", 30, 225, speed="40尺"))
_reg_m(Mount("獒犬", "Mastiff", 25, 195, speed="40尺"))


# ═══════════════════════════════════════════════════════════════════════════
# 鞍具与陆运载具
# ═══════════════════════════════════════════════════════════════════════════

TACK_VEHICLES: dict[str, TackVehicle] = {}

def _reg_t(tv: TackVehicle):
    TACK_VEHICLES[tv.name] = tv

_reg_t(TackVehicle("客车(四轮)", "Carriage", 100, 600, "载具"))
_reg_t(TackVehicle("货车(四轮)", "Wagon", 35, 400, "载具"))
_reg_t(TackVehicle("雪橇", "Sled", 20, 300, "载具"))
_reg_t(TackVehicle("货车(二轮)", "Cart", 15, 200, "载具"))
_reg_t(TackVehicle("战车(二轮)", "Chariot", 250, 100, "载具"))
_reg_t(TackVehicle("特种鞍座", "Exotic Saddle", 60, 40, "鞍座"))
_reg_t(TackVehicle("军用鞍座", "Military Saddle", 20, 30, "鞍座"))
_reg_t(TackVehicle("乘用鞍座", "Riding Saddle", 10, 25, "鞍座"))
_reg_t(TackVehicle("饲料(每日)", "Feed (per day)", 0.05, 10, "其他"))
_reg_t(TackVehicle("马厩(每日)", "Stabling (per day)", 0.5, 0, "其他"))
_reg_t(TackVehicle("具装(护甲×4价格, ×2重量)", "Barding", 0, 0, "其他"))


# ═══════════════════════════════════════════════════════════════════════════
# 大型空中与水上载具
# ═══════════════════════════════════════════════════════════════════════════

LARGE_VEHICLES: dict[str, LargeVehicle] = {}

def _reg_l(lv: LargeVehicle):
    LARGE_VEHICLES[lv.name] = lv

_reg_l(LargeVehicle("飞艇", "Airship", 40000, "8 mph", 10, 20, 1, 13, 300, 0, "空中"))
_reg_l(LargeVehicle("桨帆船", "Galley", 30000, "4 mph", 80, 0, 150, 15, 500, 20, "水上"))
_reg_l(LargeVehicle("单帆长船", "Longship", 10000, "3 mph", 40, 150, 10, 15, 300, 15, "水上"))
_reg_l(LargeVehicle("战舰", "Warship", 25000, "2.5 mph", 60, 60, 200, 15, 500, 20, "水上"))
_reg_l(LargeVehicle("帆船", "Sailing Ship", 10000, "2 mph", 20, 20, 100, 15, 300, 15, "水上"))
_reg_l(LargeVehicle("划艇", "Rowboat", 50, "1.5 mph", 1, 3, 0, 11, 50, 0, "水上"))
_reg_l(LargeVehicle("龙骨船", "Keelboat", 3000, "1 mph", 1, 6, 0.5, 15, 100, 10, "水上"))


# ═══════════════════════════════════════════════════════════════════════════
# 坐骑载重规则
# ═══════════════════════════════════════════════════════════════════════════

def mount_pull_capacity(mount: Mount, count: int = 1) -> int:
    """计算拉车载具时的总载重（载重 × 5 × 数量）。"""
    return mount.capacity_lb * 5 * count

def mount_carry_capacity(mount: Mount) -> int:
    """计算骑乘载重（坐骑自身体型限制）。"""
    return mount.capacity_lb


# ═══════════════════════════════════════════════════════════════════════════
# 查询函数
# ═══════════════════════════════════════════════════════════════════════════

def get_mount(name: str) -> Optional[Mount]:
    return MOUNTS.get(name)

def get_large_vehicle(name: str) -> Optional[LargeVehicle]:
    return LARGE_VEHICLES.get(name)

def mounts_by_price(max_gp: float) -> list[Mount]:
    return [m for m in MOUNTS.values() if m.price_gp <= max_gp]

def vehicles_by_category(category: str) -> list[LargeVehicle]:
    return [v for v in LARGE_VEHICLES.values() if v.category == category]

def vehicles_by_min_crew(max_crew: int) -> list[LargeVehicle]:
    """只返回玩家团队能操作的船只（船员需求≤max_crew）。"""
    return [v for v in LARGE_VEHICLES.values() if v.crew <= max_crew]


# ═══════════════════════════════════════════════════════════════════════════
# 自检
# ═══════════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    assert len(MOUNTS) == 8, f"坐骑应为8, 实有{len(MOUNTS)}"
    assert len(LARGE_VEHICLES) == 7, f"大型载具应为7, 实有{len(LARGE_VEHICLES)}"
    assert len(TACK_VEHICLES) >= 8, f"鞍具/陆运载具不足: {len(TACK_VEHICLES)}"

    elephant = get_mount("大象")
    assert elephant is not None and elephant.price_gp == 200
    assert mount_pull_capacity(elephant) == 6600, f"大象拉车应为6600磅"

    airship = get_large_vehicle("飞艇")
    assert airship is not None and airship.price_gp == 40000
    assert airship.speed == "8 mph"

    # 少于5人的船只（小型团队可操作）
    small = vehicles_by_min_crew(5)
    assert all(v.crew <= 5 for v in small)
    assert len(small) >= 2, f"5人以下可操作船只太少: {len(small)}"

    print(f"[vehicles] 自检通过 ✓ ({len(MOUNTS)}坐骑 + {len(LARGE_VEHICLES)}大型载具 + {len(TACK_VEHICLES)}鞍具/陆运)")


if __name__ == "__main__":
    _self_test()
