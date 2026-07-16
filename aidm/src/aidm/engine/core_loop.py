"""核心循环状态机 — DM 描绘场景 → 玩家描述行动 → DM 解决结果。

实现 D&D 5E 的基本游戏模式（玩家手册2024「游戏规律」）：
  1. DM 描绘场景（DM_DESCRIBE）
  2. 玩家描述角色行动（PLAYER_ACT）
  3. DM 解决结果并叙述（DM_RESOLVE）
     - 确定无疑（走穿过房间）→ 直接叙述结果，不掷骰
     - 结果不确定（撬锁、攀爬悬崖）→ DM 要求掷骰
     - 不可能（凡人跳过峡谷）→ 直接叙述失败，不掷骰
     - 若需掷骰：DM 设 DC → 玩家掷 d20+修正值 → 总数≥DC 则成功
     - 循环回到步骤 1

规则出处:
  - topics/玩家手册2024/进行游戏/游戏规律.htm （核心循环三步）
  - topics/玩家手册2024/进行游戏/D20检定.htm （D20 检定三步流程）
  - topics/玩家手册2024/进行游戏/优势_劣势.htm （优劣势三大规则 + 英雄激励）
  - topics/玩家手册2024/进行游戏/属性检定.htm （难度等级 DC 表）
  - topics/玩家手册2024/进行游戏/豁免检定.htm （豁免检定）

依赖 engine.dice（roll_d20）、engine.check（CheckResult, ability_check）。
不修改 engine/dice.py、engine/check.py。
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Optional

from . import check, dice


# ──────────────────────────────────────────────────────────────────────────
# 核心循环状态枚举
# ──────────────────────────────────────────────────────────────────────────

class CoreLoopState(enum.Enum):
    """核心循环的三步状态。

    规则: 核心循环三步（DM 描绘 / 玩家行动 / DM 解决）
    出处: topics/玩家手册2024/进行游戏/游戏规律.htm
    """
    DM_DESCRIBE = "dm_describe"   # 步骤1: DM 描述场景
    PLAYER_ACT = "player_act"      # 步骤2: 玩家描述行动
    DM_RESOLVE = "dm_resolve"      # 步骤3: DM 解决结果并叙述


# ──────────────────────────────────────────────────────────────────────────
# 行动确定性分类
# ──────────────────────────────────────────────────────────────────────────

class ActionCertainty(enum.Enum):
    """DM 解决阶段对行动结果的确定性分类。

    规则: 核心循环步骤3 的三种情况
          - 确定无疑 → 直接叙述结果，不掷骰
          - 结果不确定 → DM 要求掷骰
          - 不可能 → 直接叙述失败，不掷骰
    出处: topics/玩家手册2024/进行游戏/游戏规律.htm
    """
    CERTAIN = "certain"            # 确定无疑：直接叙述结果，不掷骰
    UNCERTAIN = "uncertain"        # 结果不确定：要求掷骰
    IMPOSSIBLE = "impossible"      # 不可能：直接叙述失败，不掷骰


# ──────────────────────────────────────────────────────────────────────────
# 难度等级 DC 参考表
# ──────────────────────────────────────────────────────────────────────────

# R-CHK-009 范例难度等级 DC 表
# 规则: R-CHK-009 范例难度等级DC表
# 出处: topics/玩家手册2024/进行游戏/属性检定.htm
_DC_BY_DIFFICULTY: dict[str, int] = {
    "非常容易": 5,
    "容易": 10,
    "中等": 15,
    "困难": 20,
    "非常困难": 25,
    "近乎不可能": 30,
}


def dc_by_difficulty(label: str) -> int:
    """按任务难度描述返回范例 DC。

    规则: R-CHK-009 范例难度等级DC表
    出处: topics/玩家手册2024/进行游戏/属性检定.htm
    说明: 任务越困难，其 DC 越高。
    """
    if label not in _DC_BY_DIFFICULTY:
        raise ValueError(f"未知难度描述 {label!r}，可选: {list(_DC_BY_DIFFICULTY)}")
    return _DC_BY_DIFFICULTY[label]


# ──────────────────────────────────────────────────────────────────────────
# 是否需要掷骰判定
# ──────────────────────────────────────────────────────────────────────────

def should_roll_dice(action_desc: str, situation: Any = None) -> ActionCertainty:
    """判断玩家行动是否需要掷骰。

    规则: 核心循环步骤3 的三种情况
          - 确定无疑（走穿过房间）→ 直接叙述结果，不掷骰
          - 结果不确定（撬锁、攀爬悬崖）→ DM 要求掷骰
          - 不可能（凡人跳过峡谷）→ 直接叙述失败，不掷骰
    出处: topics/玩家手册2024/进行游戏/游戏规律.htm

    参数:
      action_desc: 玩家用自然语言描述的行动
      situation: 可选的情境标记，支持以下值：
        - "impossible" 或 ActionCertainty.IMPOSSIBLE → 强制判为不可能
        - "certain" 或 ActionCertainty.CERTAIN → 强制判为确定无疑
        - "uncertain" 或 ActionCertainty.UNCERTAIN → 强制判为不确定
        - None → 由 action_desc 关键词推断

    返回:
      ActionCertainty 枚举值

    推断逻辑（当 situation 为 None 时）:
      - 含「不可能」「无法」「凡人跳过峡谷」等关键词 → IMPOSSIBLE
      - 含「撬锁」「攀爬」「说服」「欺骗」「察觉」「隐匿」「调查」
        「运动」「特技」「医药」「宗教」「自然」「奥秘」「历史」
        「威吓」「表演」「游说」「驯兽」「求生」「洞悉」等
        需要技能检定的动作 → UNCERTAIN
      - 其余默认 → CERTAIN
    """
    # 显式情境标记优先
    if isinstance(situation, ActionCertainty):
        return situation
    if isinstance(situation, str):
        key = situation.lower()
        if key in ("impossible", "不可能"):
            return ActionCertainty.IMPOSSIBLE
        if key in ("certain", "确定", "确定无疑"):
            return ActionCertainty.CERTAIN
        if key in ("uncertain", "不确定"):
            return ActionCertainty.UNCERTAIN

    desc = action_desc or ""

    # 不可能：含明确的不可能关键词
    impossible_keywords = [
        "不可能", "无法做到", "凡人跳过", "跳过峡谷",
        "徒手劈开", "肉身挡", "凡人",
    ]
    for kw in impossible_keywords:
        if kw in desc:
            return ActionCertainty.IMPOSSIBLE

    # 不确定：含需要技能检定的动作关键词
    uncertain_keywords = [
        # 技能名
        "特技", "运动", "驯兽", "奥秘", "欺瞒", "威吓",
        "表演", "游说", "历史", "调查", "医药", "自然",
        "察觉", "洞悉", "隐匿", "求生", "宗教",
        # 常见检定动作
        "撬锁", "撬开", "开锁", "攀爬", "攀登", "跳跃", "跨越",
        "说服", "交涉", "哄骗", "恐吓", "劝诱",
        "搜索", "搜查", "研究", "调查", "察觉", "聆听",
        "躲藏", "潜行", "隐匿",
        "推", "拉", "举", "破坏", "踹开", "撞开",
        "平衡", "翻滚", "杂技",
        "知识", "回忆", "辨认", "识别", "解读", "破译",
        "追踪", "觅食", "导航",
        "治疗", "急救", "诊断", "稳定伤势",
        "解除陷阱", "解除装置", "修理", "制作", "伪造",
    ]
    for kw in uncertain_keywords:
        if kw in desc:
            return ActionCertainty.UNCERTAIN

    # 默认：确定无疑（如走穿过房间开门）
    return ActionCertainty.CERTAIN


# ──────────────────────────────────────────────────────────────────────────
# 行动结果解决
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class ActionResult:
    """一次行动解决的完整结果。"""
    action_type: str                              # 行动类型标识
    success: bool = True                          # 行动是否成功执行
    certainty: ActionCertainty = ActionCertainty.CERTAIN  # 确定性分类
    message: str = ""                             # 叙事摘要
    check_result: Optional[check.CheckResult] = None     # D20 检定结果（若掷骰）
    extra: dict[str, Any] = field(default_factory=dict)  # 附加数据


def resolve_action(d20_result: int,
                   modifiers: int,
                   dc: int,
                   *,
                   rolls: Optional[list[int]] = None,
                   mode: str = "normal") -> ActionResult:
    """解决行动结果：d20 + 修正值 vs DC。

    规则: R-CHK-001 D20 检定三步流程
          step1: 掷 1d20（越高越好）
          step2: 添加调整值（相关属性调整值 + 熟练加值(如熟练) + 临时加值/减值）
          step3: 比较目标数值（总数 ≥ DC 则成功！否则失败）
    出处: topics/玩家手册2024/进行游戏/D20检定.htm

    参数:
      d20_result: 实际采用的 d20 骰值
      modifiers: 调整值合计（属性调整值 + 熟练加值 + 临时加值/减值）
      dc: 难度等级（DM 设定）
      rolls: 所有掷出的 d20（优劣势为 2 个）；默认 [d20_result]
      mode: 掷骰模式 "normal" | "advantage" | "disadvantage" | "cancelled"

    返回:
      ActionResult，包含检定结果与叙事摘要。

    说明:
      - 此函数处理通用的 D20 检定（属性检定/豁免检定）。
      - 攻击检定有天然 20/1 的特殊效果，由 check.attack_roll 处理，
        不应通过此函数解决。
      - 成功条件：total = d20_result + modifiers ≥ dc。
    """
    total = d20_result + modifiers
    success = total >= dc
    margin = total - dc

    check_res = check.CheckResult(
        success=success,
        total=total,
        d20=d20_result,
        rolls=list(rolls) if rolls is not None else [d20_result],
        mode=mode,
        target=dc,
        margin=margin,
        modifier=modifiers,
    )

    outcome = "成功" if success else "失败"
    message = (f"D20 检定：d20({d20_result}) + 修正值({modifiers}) "
               f"= {total} vs DC{dc} → {outcome}")

    return ActionResult(
        action_type="resolve_action",
        success=success,
        certainty=ActionCertainty.UNCERTAIN,
        message=message,
        check_result=check_res,
        extra={"total": total, "dc": dc, "margin": margin},
    )


# ──────────────────────────────────────────────────────────────────────────
# 英雄激励管理
# ──────────────────────────────────────────────────────────────────────────

# 英雄激励上限：一次只能拥有一个
# 规则: R-CHK-007 英雄激励重骰（has_heroic_inspiration, max=1）
# 出处: topics/玩家手册2024/进行游戏/优势_劣势.htm
_HEROIC_INSPIRATION_MAX = 1


@dataclass
class HeroicInspiration:
    """英雄激励管理类。

    规则: R-CHK-007 英雄激励重骰
          - 拥有英雄激励时，可在投任何骰子后立即消耗来重骰
          - 必须采用新结果
          - 一次只能拥有一个（max_heroic_inspiration=1）
          - 已有时获得新的可转交队友
    出处: topics/玩家手册2024/进行游戏/优势_劣势.htm

    说明:
      - has_inspiration: 当前是否拥有英雄激励
      - grant(): 给予英雄激励（受上限约束，已有时返回 False）
      - consume(): 消耗英雄激励用于重骰（无则返回 False）
      - reroll_with_inspiration(): 消耗英雄激励并重骰，返回新结果
    """
    has_inspiration: bool = False

    def grant(self) -> bool:
        """给予英雄激励。

        规则: R-CHK-007 英雄激励（一次只能拥有一个）
        出处: topics/玩家手册2024/进行游戏/优势_劣势.htm

        返回:
          True = 成功获得英雄激励
          False = 已拥有英雄激励（受上限约束，此时可转交队友）
        """
        if self.has_inspiration:
            # 已拥有时获得新的 → 可转交队友（此处返回 False 表示未新增）
            return False
        self.has_inspiration = True
        return True

    def consume(self) -> bool:
        """消耗英雄激励（用于重骰）。

        规则: R-CHK-007 英雄激励重骰（消耗后重骰，必须采用新结果）
        出处: topics/玩家手册2024/进行游戏/优势_劣势.htm

        返回:
          True = 成功消耗英雄激励
          False = 未拥有英雄激励，无法消耗
        """
        if not self.has_inspiration:
            return False
        self.has_inspiration = False
        return True

    def reroll_with_inspiration(self, roll_func) -> tuple[bool, Any]:
        """消耗英雄激励并重骰。

        规则: R-CHK-007 英雄激励重骰
              - 拥有英雄激励时，可在投任何骰子后立即消耗来重骰
              - 必须采用新结果（must_use_new=True）
        出处: topics/玩家手册2024/进行游戏/优势_劣势.htm

        参数:
          roll_func: 无参可调用对象，执行重骰并返回新结果

        返回:
          (consumed, new_result)
          - consumed=True: 成功消耗英雄激励并重骰
          - consumed=False: 未拥有英雄激励，new_result=None
        """
        if not self.consume():
            return (False, None)
        new_result = roll_func()
        return (True, new_result)


# ──────────────────────────────────────────────────────────────────────────
# 核心循环状态机
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class CoreLoopMachine:
    """核心循环状态机：管理 DM→玩家→DM 的三步循环转换。

    规则: 核心循环三步（DM 描绘场景 / 玩家描述行动 / DM 解决结果并叙述）
    出处: topics/玩家手册2024/进行游戏/游戏规律.htm

    状态转换图:
        DM_DESCRIBE → PLAYER_ACT → DM_RESOLVE → DM_DESCRIBE → ...

    说明:
      - 初始状态为 DM_DESCRIBE（DM 先描绘场景）
      - 每完成一步，advance() 推进到下一步
      - DM_RESOLVE 完成后自动回到 DM_DESCRIBE（循环回到步骤1）
      - iteration 记录当前是第几轮循环
    """
    state: CoreLoopState = CoreLoopState.DM_DESCRIBE
    iteration: int = 1

    def advance(self) -> CoreLoopState:
        """推进到下一个循环状态。

        规则: 核心循环三步的状态转换
        出处: topics/玩家手册2024/进行游戏/游戏规律.htm

        转换:
          DM_DESCRIBE → PLAYER_ACT
          PLAYER_ACT → DM_RESOLVE
          DM_RESOLVE → DM_DESCRIBE（循环回到步骤1，iteration+1）
        """
        if self.state == CoreLoopState.DM_DESCRIBE:
            self.state = CoreLoopState.PLAYER_ACT
        elif self.state == CoreLoopState.PLAYER_ACT:
            self.state = CoreLoopState.DM_RESOLVE
        elif self.state == CoreLoopState.DM_RESOLVE:
            # 循环回到步骤1
            self.state = CoreLoopState.DM_DESCRIBE
            self.iteration += 1
        return self.state

    def reset(self) -> None:
        """重置状态机到初始状态。"""
        self.state = CoreLoopState.DM_DESCRIBE
        self.iteration = 1

    def run_full_cycle(self,
                       dm_describe_fn: Optional[callable] = None,
                       player_act_fn: Optional[callable] = None,
                       dm_resolve_fn: Optional[callable] = None) -> CoreLoopState:
        """运行一个完整的循环周期（三步）。

        规则: 核心循环三步的完整执行
        出处: topics/玩家手册2024/进行游戏/游戏规律.htm

        参数:
          dm_describe_fn: 步骤1回调（DM 描绘场景）
          player_act_fn: 步骤2回调（玩家描述行动）
          dm_resolve_fn: 步骤3回调（DM 解决结果并叙述）

        返回:
          最终状态（DM_DESCRIBE，因为循环回到了步骤1）
        """
        # 步骤1: DM 描绘场景
        assert self.state == CoreLoopState.DM_DESCRIBE
        if dm_describe_fn:
            dm_describe_fn()
        self.advance()

        # 步骤2: 玩家描述行动
        assert self.state == CoreLoopState.PLAYER_ACT
        if player_act_fn:
            player_act_fn()
        self.advance()

        # 步骤3: DM 解决结果并叙述
        assert self.state == CoreLoopState.DM_RESOLVE
        if dm_resolve_fn:
            dm_resolve_fn()
        self.advance()  # 回到 DM_DESCRIBE

        return self.state


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    """核心循环模块自检。"""
    from . import dice as _dice

    # ── 1. CoreLoopState 枚举 ──
    assert CoreLoopState.DM_DESCRIBE.value == "dm_describe"
    assert CoreLoopState.PLAYER_ACT.value == "player_act"
    assert CoreLoopState.DM_RESOLVE.value == "dm_resolve"
    assert len(CoreLoopState) == 3

    # ── 2. CoreLoopMachine 状态转换 ──
    m = CoreLoopMachine()
    assert m.state == CoreLoopState.DM_DESCRIBE
    assert m.iteration == 1

    # DM_DESCRIBE → PLAYER_ACT
    s = m.advance()
    assert s == CoreLoopState.PLAYER_ACT
    assert m.state == CoreLoopState.PLAYER_ACT

    # PLAYER_ACT → DM_RESOLVE
    s = m.advance()
    assert s == CoreLoopState.DM_RESOLVE
    assert m.state == CoreLoopState.DM_RESOLVE

    # DM_RESOLVE → DM_DESCRIBE（循环回到步骤1）
    s = m.advance()
    assert s == CoreLoopState.DM_DESCRIBE
    assert m.iteration == 2

    # 第二轮循环
    m.advance()  # → PLAYER_ACT
    m.advance()  # → DM_RESOLVE
    m.advance()  # → DM_DESCRIBE, iteration=3
    assert m.iteration == 3

    # reset
    m.reset()
    assert m.state == CoreLoopState.DM_DESCRIBE
    assert m.iteration == 1

    # ── 3. run_full_cycle 完整循环 ──
    calls = []
    m2 = CoreLoopMachine()
    final = m2.run_full_cycle(
        dm_describe_fn=lambda: calls.append("describe"),
        player_act_fn=lambda: calls.append("act"),
        dm_resolve_fn=lambda: calls.append("resolve"),
    )
    assert final == CoreLoopState.DM_DESCRIBE
    assert calls == ["describe", "act", "resolve"]
    assert m2.iteration == 2

    # ── 4. should_roll_dice 判定 ──
    # 确定无疑：走穿过房间
    c = should_roll_dice("我走穿过房间去开门")
    assert c == ActionCertainty.CERTAIN, f"got {c}"

    # 不确定：撬锁
    c = should_roll_dice("我尝试撬开这把锁")
    assert c == ActionCertainty.UNCERTAIN, f"got {c}"

    # 不确定：攀爬悬崖
    c = should_roll_dice("我攀爬这座悬崖")
    assert c == ActionCertainty.UNCERTAIN, f"got {c}"

    # 不可能：凡人跳过峡谷
    c = should_roll_dice("我作为凡人试图跳过峡谷")
    assert c == ActionCertainty.IMPOSSIBLE, f"got {c}"

    # 不可能：肉身挡龙息
    c = should_roll_dice("我用肉身挡住龙息")
    assert c == ActionCertainty.IMPOSSIBLE, f"got {c}"

    # 不确定：说服
    c = should_roll_dice("我说服守卫放我过去")
    assert c == ActionCertainty.UNCERTAIN, f"got {c}"

    # 不确定：隐匿
    c = should_roll_dice("我隐匿在阴影中")
    assert c == ActionCertainty.UNCERTAIN, f"got {c}"

    # 确定无疑：拿取桌上的苹果
    c = should_roll_dice("我拿取桌上的苹果")
    assert c == ActionCertainty.CERTAIN, f"got {c}"

    # 显式情境标记
    assert should_roll_dice("任意", situation="impossible") == ActionCertainty.IMPOSSIBLE
    assert should_roll_dice("任意", situation="certain") == ActionCertainty.CERTAIN
    assert should_roll_dice("任意", situation="uncertain") == ActionCertainty.UNCERTAIN
    assert should_roll_dice("任意", situation=ActionCertainty.IMPOSSIBLE) == ActionCertainty.IMPOSSIBLE

    # 空描述默认 CERTAIN
    assert should_roll_dice("") == ActionCertainty.CERTAIN

    # ── 5. dc_by_difficulty DC 参考表 ──
    assert dc_by_difficulty("非常容易") == 5
    assert dc_by_difficulty("容易") == 10
    assert dc_by_difficulty("中等") == 15
    assert dc_by_difficulty("困难") == 20
    assert dc_by_difficulty("非常困难") == 25
    assert dc_by_difficulty("近乎不可能") == 30
    try:
        dc_by_difficulty("不存在的难度")
        assert False, "应抛 ValueError"
    except ValueError:
        pass

    # ── 6. resolve_action 行动结果解决 ──
    # 成功：d20=15, mod=5, total=20 ≥ DC15
    r = resolve_action(d20_result=15, modifiers=5, dc=15)
    assert r.success is True
    assert r.certainty == ActionCertainty.UNCERTAIN
    assert r.check_result is not None
    assert r.check_result.total == 20
    assert r.check_result.margin == 5
    assert r.check_result.d20 == 15
    assert r.check_result.target == 15

    # 失败：d20=5, mod=5, total=10 < DC15
    r = resolve_action(d20_result=5, modifiers=5, dc=15)
    assert r.success is False
    assert r.check_result.total == 10
    assert r.check_result.margin == -5

    # 刚好成功：total == DC
    r = resolve_action(d20_result=10, modifiers=5, dc=15)
    assert r.success is True
    assert r.check_result.margin == 0

    # 带 rolls 和 mode（优劣势场景）
    r = resolve_action(d20_result=18, modifiers=3, dc=15,
                       rolls=[3, 18], mode="advantage")
    assert r.success is True
    assert r.check_result.rolls == [3, 18]
    assert r.check_result.mode == "advantage"

    # ── 7. HeroicInspiration 英雄激励管理 ──
    hi = HeroicInspiration()
    assert hi.has_inspiration is False

    # grant: 成功获得
    assert hi.grant() is True
    assert hi.has_inspiration is True

    # grant: 已拥有时返回 False（可转交队友）
    assert hi.grant() is False
    assert hi.has_inspiration is True

    # consume: 成功消耗
    assert hi.consume() is True
    assert hi.has_inspiration is False

    # consume: 未拥有时返回 False
    assert hi.consume() is False
    assert hi.has_inspiration is False

    # ── 8. HeroicInspiration.reroll_with_inspiration 重骰 ──
    hi2 = HeroicInspiration(has_inspiration=True)
    roll_count = [0]

    def fake_reroll():
        roll_count[0] += 1
        return 42  # 新结果

    consumed, new_result = hi2.reroll_with_inspiration(fake_reroll)
    assert consumed is True
    assert new_result == 42
    assert hi2.has_inspiration is False
    assert roll_count[0] == 1  # 重骰了一次

    # 未拥有英雄激励时无法重骰
    hi3 = HeroicInspiration(has_inspiration=False)
    consumed, new_result = hi3.reroll_with_inspiration(fake_reroll)
    assert consumed is False
    assert new_result is None
    assert roll_count[0] == 1  # 没有再次重骰

    # ── 9. 端到端：核心循环 + 掷骰判定 ──
    m3 = CoreLoopMachine()

    # 步骤1: DM 描绘场景
    assert m3.state == CoreLoopState.DM_DESCRIBE
    m3.advance()

    # 步骤2: 玩家描述行动（撬锁）
    assert m3.state == CoreLoopState.PLAYER_ACT
    player_action = "我尝试用盗贼工具撬开宝箱上的锁"
    certainty = should_roll_dice(player_action)
    assert certainty == ActionCertainty.UNCERTAIN
    m3.advance()

    # 步骤3: DM 解决结果（设 DC15 中等，掷骰）
    assert m3.state == CoreLoopState.DM_RESOLVE
    dc = dc_by_difficulty("中等")  # DC=15
    assert dc == 15
    # 固定 d20=14, mod=5(DEX+3, 熟练+2), total=19 ≥ DC15 → 成功
    orig_roll_d20 = _dice.roll_d20
    _dice.roll_d20 = lambda advantage=False, disadvantage=False: \
        type("R", (), {"used": 14, "rolls": [14], "mode": "normal"})()
    d20_roll = _dice.roll_d20()
    result = resolve_action(
        d20_result=d20_roll.used,
        modifiers=5,  # DEX mod +3, 熟练加值 +2
        dc=dc,
        rolls=list(d20_roll.rolls),
        mode=d20_roll.mode,
    )
    _dice.roll_d20 = orig_roll_d20
    assert result.success is True
    assert result.check_result.total == 19
    m3.advance()  # 回到 DM_DESCRIBE
    assert m3.state == CoreLoopState.DM_DESCRIBE
    assert m3.iteration == 2

    # ── 10. 端到端：不可能行动直接失败 ──
    m4 = CoreLoopMachine()
    m4.advance()  # → PLAYER_ACT
    impossible_action = "我作为凡人试图跳过50尺宽的峡谷"
    certainty = should_roll_dice(impossible_action)
    assert certainty == ActionCertainty.IMPOSSIBLE
    m4.advance()  # → DM_RESOLVE
    # 不可能行动不掷骰，直接叙述失败
    impossible_result = ActionResult(
        action_type="impossible_action",
        success=False,
        certainty=ActionCertainty.IMPOSSIBLE,
        message="凡人无法跳过峡谷——行动失败",
    )
    assert impossible_result.success is False
    assert impossible_result.certainty == ActionCertainty.IMPOSSIBLE
    m4.advance()  # → DM_DESCRIBE
    assert m4.iteration == 2

    # ── 11. 端到端：确定无疑行动直接成功 ──
    m5 = CoreLoopMachine()
    m5.advance()  # → PLAYER_ACT
    certain_action = "我走穿过房间去开门"
    certainty = should_roll_dice(certain_action)
    assert certainty == ActionCertainty.CERTAIN
    m5.advance()  # → DM_RESOLVE
    # 确定无疑行动不掷骰，直接叙述结果
    certain_result = ActionResult(
        action_type="certain_action",
        success=True,
        certainty=ActionCertainty.CERTAIN,
        message="你走过房间，打开了门",
    )
    assert certain_result.success is True
    assert certain_result.certainty == ActionCertainty.CERTAIN
    m5.advance()  # → DM_DESCRIBE
    assert m5.iteration == 2

    print("[core_loop] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
