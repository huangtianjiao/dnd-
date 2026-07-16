"""危害引擎 — D&D 5E 环境危害规则（燃烧/脱水/坠落/饥饿/窒息 + 水下战斗/骑乘）。

提供危害的纯数值/判定实现：坠落伤害与液体减半、屏息与窒息力竭、燃烧、
脱水/饥饿力竭、水下战斗修饰、骑乘上下马/受控坐骑动作/跌落坐骑豁免。
叙事交给 LLM，危害的骰子与判定交给代码（不可绕过）。

依赖 engine.dice（round_down）、engine.check（saving_throw）。
标注约定：每条规则实现处标注 RULE_SPEC.md 规则点 ID + 原文出处路径
（topics/.../xxx.htm），形成"代码↔规则"双向索引。

规则依据:
  - R-GLS-059 燃烧 / R-GLS-060 脱水 / R-GLS-061 坠落 / R-GLS-062 饥饿 / R-GLS-063 窒息
    出处: topics/玩家手册2024/术语汇编/危害.htm
  - R-QCK-006 坠落伤害基准 / R-QCK-009 坠落至生物上（可选）
    出处: topics/速查/DM速查/坠落.htm
  - R-CMB-040 水下近战攻击劣势 / R-CMB-041 水下远程攻击 / R-CMB-042 水下火焰抗性
    R-CMB-044 上下坐骑移动力 / R-CMB-045 受控坐骑动作 / R-CMB-046 跌落坐骑豁免
    出处: topics/玩家手册2024/进行游戏/水下战斗.htm ; 骑乘战斗.htm
  - R-ADD-030 水下远程常规射程内劣势（豁免：弩/捕网/标枪类投掷）
    出处: topics/速查/DM速查/水下战斗.htm
"""

from __future__ import annotations

from . import dice, check


# ──────────────────────────────────────────────────────────────────────────
# 坠落危害
# ──────────────────────────────────────────────────────────────────────────

def fall_damage(fall_distance_ft: int) -> dict:
    """坠落伤害：每10尺1d6钝击，上限20d6；着地陷倒地（除非全数避免伤害）。

    规则: R-GLS-061 坠落危害 / R-QCK-006 坠落伤害基准规则
    出处: topics/玩家手册2024/术语汇编/危害.htm ; topics/速查/DM速查/坠落.htm
    说明: N = min(fall_distance_ft // 10, 20)，至少0。
          着地倒地：未将坠落伤害全数避免则陷倒地（R-GLS-061）。本函数 dice_count>0
          即意味"会产生倒地"，prone=True；若调用方经抗性/减免把伤害降至0，
          应自行将 prone 置 False（"除非全数避免"）。不足10尺（N=0）无伤害亦不倒地。
    返回: {"damage_dice": "Nd6", "damage_type": "钝击", "prone": bool, "dice_count": N}
    """
    n = max(0, min(fall_distance_ft // 10, 20))      # R-GLS-061: 每10尺1d6，上限20
    return {
        "damage_dice": f"{n}d6",
        "damage_type": "钝击",
        "prone": n > 0,            # R-GLS-061: 未全数避免则倒地（N=0 无伤害不倒地）
        "dice_count": n,
    }


def fall_into_liquid_save(con_mod: int, con_prof: bool, prof: int) -> dict:
    """坠入液体减半：反应 DC15 检定，成功则坠落伤害减半。

    规则: R-GLS-061 坠落危害（坠入水/液体条款）
          DC15 力量(运动)或敏捷(特技)检定，成功→由此次坠落导致的伤害减半
    出处: topics/玩家手册2024/术语汇编/危害.htm
    说明: 简化实现——用体质(CON)豁免模拟该反应检定（接受 con_mod/con_prof/prof）。
          原规则为力(运动)或敏(特技)检定；此处统一走 check.saving_throw（DC15）。
    返回: {"dc": 15, "success": bool, "half_damage": bool}
    """
    res = check.saving_throw(
        mod=con_mod, prof=prof, proficient=con_prof, dc=15,
    )
    return {
        "dc": 15,
        "success": res.success,
        "half_damage": res.success,   # 成功→坠落伤害减半
    }


# ──────────────────────────────────────────────────────────────────────────
# 窒息危害
# ──────────────────────────────────────────────────────────────────────────

def suffocation_rounds(con_mod: int) -> int:
    """屏息时长（分钟）：1 + 体质调整值分钟，至少30秒(0.5分钟)，向下取整。

    规则: R-GLS-063 窒息危害
          生物可屏息至多 1+体质调整值 分钟（至少30秒），然后窒息开始
    出处: topics/玩家手册2024/术语汇编/危害.htm
    说明: 公式 breath = max(0.5, 1+con_mod) 分钟（0.5分钟=30秒为规则下限）；
          返回整数分钟（向下取整），且至少1分钟——30秒在整分钟表达下取1分钟。
          注: 函数名沿用"rounds"历史命名，但按规则返回的是"分钟数"。
    """
    minutes = dice.round_down(max(0.5, 1 + con_mod))   # R-GLS-063: 至少30秒
    return max(1, minutes)


def suffocation_exhaustion_per_round() -> int:
    """屏息殆尽后每回合结束获1级力竭。

    规则: R-GLS-063 窒息危害
          屏息时间殆尽或呼吸受阻 → 自己每个回合结束时获1级力竭；
          重新可呼吸时所有因窒息获得的力竭等级被移除
    出处: topics/玩家手册2024/术语汇编/危害.htm
    返回: 1
    """
    return 1


# ──────────────────────────────────────────────────────────────────────────
# 燃烧危害
# ──────────────────────────────────────────────────────────────────────────

def burning_damage() -> dict:
    """燃烧伤害：每回合开始受1d4火焰伤害。

    规则: R-GLS-059 燃烧危害
          燃烧中的生物/物件在其每个回合开始时受到1d4火焰伤害。
          - 以一个动作在地上打滚可熄灭身上的火焰，并因此陷入倒地状态。
          - 火焰同样会在被浇灭、淹灭、扑灭时消失。
    出处: topics/玩家手册2024/术语汇编/危害.htm
    返回: {"damage_dice": "1d4", "damage_type": "火焰"}
    附加效果（由调用方驱动，非本函数返回）:
          - 动作打滚熄火 → 移除燃烧 + 陷倒地
          - 被浇灭/淹灭/扑灭 → 移除燃烧
    """
    return {"damage_dice": "1d4", "damage_type": "火焰"}


# ──────────────────────────────────────────────────────────────────────────
# 脱水/饥饿危害
# ──────────────────────────────────────────────────────────────────────────

def dehydration_exhaustion() -> int:
    """脱水/饥饿导致的力竭等级：当日结束获1级。

    规则: R-GLS-060 脱水危害 / R-GLS-062 饥饿危害
          - 脱水: 每日饮水低于需求量一半 → 当日结束获1级力竭
          - 饥饿: 每日进食低于需求量一半 → DC10体质豁免，失败获1级力竭
            （连续5天不食第5天结束自动+1级，其后每日+1级）
    出处: topics/玩家手册2024/术语汇编/危害.htm
    说明: 本函数返回"每日不足半量所获的力竭等级"=1（饥饿的 DC10 体质豁免
          由调用方经 check.saving_throw(dc=10) 判定，失败时取本返回值）。
          因脱水/饥饿获得的力竭等级，在补足完整一日需求量（水/食）前不可移除。
    返回: 1
    """
    return 1


# ──────────────────────────────────────────────────────────────────────────
# 水下战斗修饰
# ──────────────────────────────────────────────────────────────────────────

def underwater_combat_modifiers(
    has_swim_speed: bool,
    weapon_type: str,
    beyond_normal_range: bool = False,
) -> dict:
    """水下战斗的攻击检定修饰与火焰抗性。

    规则: R-CMB-040 水下近战攻击劣势 / R-CMB-041 水下远程攻击 /
          R-CMB-042 水下火焰抗性 / R-ADD-030 水下远程常规射程内劣势（豁免）
    出处: topics/玩家手册2024/进行游戏/水下战斗.htm ; topics/速查/DM速查/水下战斗.htm

    参数:
        has_swim_speed: 攻击者是否具有游泳速度（仅影响近战，R-CMB-040）
        weapon_type: 武器类别
            "melee"    — 近战武器（按非穿刺处理；穿刺近战豁免见下）
            "ranged"   — 远程武器（弓等普通远程）
            "crossbow" — 弩（豁免常规射程内劣势，R-ADD-030）
            "thrown"   — 标枪类投掷/捕网（穿刺投掷，豁免常规射程内劣势，R-ADD-030）
        beyond_normal_range: 远程攻击是否超过武器常规射程（True→自动失手）

    返回: {"disadvantage": bool, "auto_miss": bool, "fire_resistance": True}

    说明:
      - 近战(R-CMB-040): 无游泳速度且非穿刺→劣势。穿刺近战武器
        （匕首/标枪/短剑/矛/三叉戟）豁免；本函数"melee"按非穿刺近战处理，
        穿刺近战由调用方判定豁免（或按"thrown"类投掷武器处理）。
      - 远程(R-CMB-041): 超常规射程→自动失手；常规射程内→劣势。
        弩/捕网/标枪类投掷豁免常规射程内劣势(R-ADD-030)。
        远程劣势不因游泳速度而豁免（仅近战规则提及游泳速度）。
      - 完全没入水→火焰抗性(R-CMB-042)，对火焰伤害减半（由调用方经 damage 管线结算）。
    """
    disadvantage = False
    auto_miss = False
    wt = weapon_type.lower()

    if wt == "melee":
        # R-CMB-040: 无游泳速度的非穿刺近战→劣势
        if not has_swim_speed:
            disadvantage = True
    elif wt in ("ranged", "crossbow", "thrown"):
        if beyond_normal_range:
            # R-CMB-041: 超常规射程→自动失手（所有远程，无豁免）
            auto_miss = True
        elif wt == "ranged":
            # R-CMB-041 + R-ADD-030: 常规射程内普通远程→劣势
            # （弩 crossbow / 标枪类投掷 thrown 豁免）
            disadvantage = True
    else:
        raise ValueError(
            f"未知 weapon_type {weapon_type!r}，可选: melee/ranged/crossbow/thrown"
        )

    return {
        "disadvantage": disadvantage,
        "auto_miss": auto_miss,
        "fire_resistance": True,           # R-CMB-042 完全没入水→火焰抗性
    }


# ──────────────────────────────────────────────────────────────────────────
# 骑乘战斗
# ──────────────────────────────────────────────────────────────────────────

def mount_dismount_cost(speed: int) -> int:
    """上下坐骑消耗的移动力：速度的一半（向下取整）。

    规则: R-CMB-044 上下坐骑移动力消耗
          移动期间可骑乘5尺内生物或下坐骑，消耗等于速度一半的移动力
    出处: topics/玩家手册2024/进行游戏/骑乘战斗.htm
    算例: speed=30 → 15尺；speed=25 → 12尺
    """
    return dice.round_down(speed / 2)            # R-GLS-005 向下取整


# 受控坐骑仅可执行的动作（R-CMB-045: 疾走/撤离/回避）
# 规则: R-CMB-045 受控坐骑先攻与动作  出处: topics/玩家手册2024/进行游戏/骑乘战斗.htm
CONTROLLED_MOUNT_ACTIONS = ("疾走", "撤离", "回避")


def controlled_mount_actions() -> list:
    """受控坐骑可执行的动作：仅疾走/撤离/回避。

    规则: R-CMB-045 受控坐骑先攻与动作
          受控坐骑先攻与骑手相同，在骑手回合行动，仅可执行疾走/撤离/回避三个动作
    出处: topics/玩家手册2024/进行游戏/骑乘战斗.htm
    返回: ["疾走", "撤离", "回避"]
    """
    return list(CONTROLLED_MOUNT_ACTIONS)


def fall_off_mount_save(con_mod: int, prof: int, proficient: bool) -> dict:
    """跌落坐骑豁免：DC10敏捷豁免，失败则跌落于坐骑5尺内并倒地。

    规则: R-CMB-046 跌落坐骑豁免
          骑乘期间若效应违背坐骑意愿使其移动，或骑手/坐骑被击至倒地，
          骑手须DC10敏捷豁免，失败则跌落于坐骑5尺内未占据空间并倒地
    出处: topics/玩家手册2024/进行游戏/骑乘战斗.htm
    说明: 规则为 DC10 敏捷(DEX)豁免；参数名 con_mod 沿用调用约定，实为
          敏捷调整值，请传入骑手的 DEX 调整值。prof/proficient 对应熟练加值/是否熟练。
    返回: {"dc": 10, "success": bool, "prone": bool}
          （prone = 豁免失败 → 跌落倒地）
    """
    res = check.saving_throw(
        mod=con_mod, prof=prof, proficient=proficient, dc=10,
    )
    return {
        "dc": 10,
        "success": res.success,
        "prone": not res.success,    # R-CMB-046: 失败→跌落倒地
    }


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    # —— 坠落伤害（R-GLS-061 / R-QCK-006）——
    r = fall_damage(0)
    assert r["dice_count"] == 0 and r["damage_dice"] == "0d6"
    assert r["prone"] is False and r["damage_type"] == "钝击"
    assert fall_damage(5)["dice_count"] == 0                # 不足10尺
    assert fall_damage(10)["dice_count"] == 1               # 10尺→1d6
    assert fall_damage(10)["prone"] is True                 # 有伤害→倒地
    assert fall_damage(99)["dice_count"] == 9
    assert fall_damage(200)["dice_count"] == 20             # 200尺→20d6
    assert fall_damage(200)["damage_dice"] == "20d6"
    assert fall_damage(250)["dice_count"] == 20            # 上限20d6（R-GLS-061）
    assert fall_damage(9999)["dice_count"] == 20           # 远超上限仍20

    # —— 坠入液体减半（R-GLS-061 液体条款，DC15）—— 固定 d20
    orig = dice.roll_d20
    class _Fake:
        def __init__(s, used, rolls, mode): s.used, s.rolls, s.mode = used, rolls, mode
    # 成功: d20=15, con_mod=0, prof=0 → 15≥15 → 减半
    dice.roll_d20 = lambda adv=False, dis=False: _Fake(15, [15], "normal")
    r = fall_into_liquid_save(con_mod=0, con_prof=False, prof=0)
    assert r["dc"] == 15 and r["success"] is True and r["half_damage"] is True
    # 失败: d20=14 → 14<15 → 不减半
    dice.roll_d20 = lambda adv=False, dis=False: _Fake(14, [14], "normal")
    r = fall_into_liquid_save(con_mod=0, con_prof=False, prof=0)
    assert r["success"] is False and r["half_damage"] is False
    # 熟练加成: d20=12, con_mod=1, prof=2, 熟练 → 12+1+2=15 ≥15 → 成功
    dice.roll_d20 = lambda adv=False, dis=False: _Fake(12, [12], "normal")
    r = fall_into_liquid_save(con_mod=1, con_prof=True, prof=2)
    assert r["success"] is True

    # —— 窒息屏息分钟数（R-GLS-063）——
    assert suffocation_rounds(3) == 4            # 1+3=4分钟
    assert suffocation_rounds(0) == 1           # 1分钟
    assert suffocation_rounds(-1) == 1          # 0→下限30秒→整分钟取1
    assert suffocation_rounds(-5) == 1          # 最低体质仍至少1分钟
    assert suffocation_rounds(5) == 6
    # 窒息每回合力竭
    assert suffocation_exhaustion_per_round() == 1

    # —— 燃烧（R-GLS-059）——
    b = burning_damage()
    assert b["damage_dice"] == "1d4" and b["damage_type"] == "火焰"

    # —— 脱水/饥饿力竭（R-GLS-060/062）——
    assert dehydration_exhaustion() == 1

    # —— 水下战斗修饰（R-CMB-040/041/042, R-ADD-030）——
    # 近战无游泳速度→劣势；有游泳速度→无劣势
    r = underwater_combat_modifiers(False, "melee")
    assert r["disadvantage"] is True and r["auto_miss"] is False and r["fire_resistance"] is True
    r = underwater_combat_modifiers(True, "melee")
    assert r["disadvantage"] is False
    # 远程常规射程内→劣势（不论游泳速度）
    r = underwater_combat_modifiers(False, "ranged")
    assert r["disadvantage"] is True and r["auto_miss"] is False
    r = underwater_combat_modifiers(True, "ranged")   # 游泳速度不免除远程劣势
    assert r["disadvantage"] is True
    # 远程超常规射程→自动失手
    r = underwater_combat_modifiers(False, "ranged", beyond_normal_range=True)
    assert r["auto_miss"] is True and r["disadvantage"] is False
    # 弩/标枪类投掷→常规射程内豁免劣势
    r = underwater_combat_modifiers(False, "crossbow")
    assert r["disadvantage"] is False and r["auto_miss"] is False
    r = underwater_combat_modifiers(False, "thrown")
    assert r["disadvantage"] is False
    # 弩超常规射程仍自动失手
    r = underwater_combat_modifiers(False, "crossbow", beyond_normal_range=True)
    assert r["auto_miss"] is True
    # 火焰抗性恒为真
    assert underwater_combat_modifiers(False, "melee")["fire_resistance"] is True
    # 非法 weapon_type
    try:
        underwater_combat_modifiers(False, "bazooka")
        raise AssertionError("应拒绝未知 weapon_type")
    except ValueError:
        pass

    # —— 骑乘战斗（R-CMB-044/045/046）——
    assert mount_dismount_cost(30) == 15          # 30→15
    assert mount_dismount_cost(25) == 12          # 25→12（向下取整）
    assert mount_dismount_cost(1) == 0            # 1→0
    assert mount_dismount_cost(0) == 0
    acts = controlled_mount_actions()
    assert acts == ["疾走", "撤离", "回避"]
    # 跌落坐骑豁免 DC10：成功不倒地，失败倒地
    dice.roll_d20 = lambda adv=False, dis=False: _Fake(10, [10], "normal")
    r = fall_off_mount_save(con_mod=0, prof=0, proficient=False)   # 10≥10 成功
    assert r["dc"] == 10 and r["success"] is True and r["prone"] is False
    dice.roll_d20 = lambda adv=False, dis=False: _Fake(9, [9], "normal")
    r = fall_off_mount_save(con_mod=0, prof=0, proficient=False)   # 9<10 失败
    assert r["success"] is False and r["prone"] is True
    # 熟练+调整值: d20=7, dex=1, prof=2, 熟练 → 7+1+2=10 ≥10 成功
    dice.roll_d20 = lambda adv=False, dis=False: _Fake(7, [7], "normal")
    r = fall_off_mount_save(con_mod=1, prof=2, proficient=True)
    assert r["success"] is True and r["prone"] is False

    dice.roll_d20 = orig
    print("[hazards] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
