"""集中维持引擎 — ConcentrationManager。

管理施法者的集中状态：同时只能集中维持一个法术；施展新专注法术自动结束旧的；
受伤时进行体质豁免维持（DC=max(10, dmg/2)，至高30）；失能/死亡中断集中；
可随时主动终止（无需动作）。

依赖 engine.dice（roll_die / round_down）、engine.check（saving_throw）。
标注规则ID+出处。规则依据 R-SPL-019/R-SPL-020、R-GLS-013。

注意: 不修改 engine/dice.py、engine/check.py、engine/damage.py。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from . import dice, check


# ──────────────────────────────────────────────────────────────────────────
# 集中状态
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class ConcentrationSlot:
    """单个施法者的集中槽。

    规则: R-SPL-019 专注维持与打断（max 1 concurrent）
    出处: topics/玩家手册2024/第七章/施法.htm
    """
    spell_id: Optional[str] = None     # 当前集中的法术标识（None=无集中）
    caster_id: str = ""                # 施法者标识（便于审计）

    @property
    def is_concentrating(self) -> bool:
        return self.spell_id is not None


# ──────────────────────────────────────────────────────────────────────────
# 集中维持 DC
# ──────────────────────────────────────────────────────────────────────────

def concentration_save_dc(damage_taken: int) -> int:
    """集中维持体质豁免 DC = max(10, floor(damage/2))，至高 30。

    规则: R-SPL-020 专注伤害豁免（=R-GLS-013）
          DC为10或所受伤害一半中较高者，至高30
    出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm
    说明: 多来源伤害分别投各自 DC（per source: separate save）。
    """
    dc_from_damage = dice.round_down(damage_taken / 2)
    return min(30, max(10, dc_from_damage))


# ──────────────────────────────────────────────────────────────────────────
# ConcentrationManager
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class ConcentrationManager:
    """全局集中状态管理器（每个施法者一个 ConcentrationSlot）。

    规则: R-SPL-019 专注维持与打断
          - 施展另一专注法术 → 旧专注结束（max 1 concurrent）
          - 失能或死亡 → 失去专注
          - 可随时主动终止（actionCost=0）
    出处: topics/玩家手册2024/第七章/施法.htm
    """
    slots: dict[str, ConcentrationSlot] = field(default_factory=dict)

    def _get_slot(self, caster_id: str) -> ConcentrationSlot:
        if caster_id not in self.slots:
            self.slots[caster_id] = ConcentrationSlot(caster_id=caster_id)
        return self.slots[caster_id]

    def set_concentration(self, caster_id: str, spell_id: str) -> bool:
        """设置集中：旧的自动结束，新的占据集中槽。

        规则: R-SPL-019 castConcentrationSpell→lose previous(max 1 concurrent)
        出处: topics/玩家手册2024/第七章/施法.htm
        返回: True（总是成功设置，旧专注被覆盖）
        """
        slot = self._get_slot(caster_id)
        # 旧专注自动结束（R-SPL-019）
        slot.spell_id = spell_id
        return True

    def break_concentration(self, caster_id: str) -> bool:
        """中断集中：失能/死亡/主动放弃时调用。

        规则: R-SPL-019 if incapacitated||dead: lost; voluntaryEnd: actionCost=0
        出处: topics/玩家手册2024/第七章/施法.htm
        返回: 是否确实中断了正在维持的集中
        """
        slot = self._get_slot(caster_id)
        if slot.spell_id is None:
            return False
        slot.spell_id = None
        return True

    def get_active_concentration(self, caster_id: str) -> Optional[str]:
        """获取当前集中的法术ID。

        规则: R-SPL-019 caster.concentration=newSpellInstance（旧结束）
        出处: topics/玩家手册2024/第七章/施法.htm
        返回: 法术ID 或 None
        """
        slot = self._get_slot(caster_id)
        return slot.spell_id

    def concentration_save_on_damage(
        self,
        caster_id: str,
        damage_taken: int,
        con_mod: int,
        con_proficient: bool,
        prof_bonus: int,
        advantage: bool = False,
        disadvantage: bool = False,
    ) -> dict:
        """集中者受伤时进行体质豁免维持集中。

        规则: R-SPL-020 专注伤害豁免
              - DC = max(10, floor(damage/2))，至高30
              - 豁免失败 → 失去集中
              - 多来源伤害分别投（此处处理单次伤害）
        出处: topics/玩家手册2024/术语汇编/常见规则词汇.htm

        参数:
            damage_taken: 本次受到的伤害值
            con_mod: 体质调整值
            con_proficient: 是否熟练体质豁免
            prof_bonus: 熟练加值
            advantage/disadvantage: 豁免优劣势

        返回 dict:
            success: bool — 是否维持集中
            dc: int — 豁免DC
            roll: int — d20结果
            total: int — d20+调整值
            broken: bool — 是否失去集中（=not success 且原本在集中）
            was_concentrating: bool — 受伤时是否在集中
        """
        slot = self._get_slot(caster_id)
        was_concentrating = slot.is_concentrating

        # 未在集中则无需检定
        if not was_concentrating:
            return {
                "success": True,
                "dc": 0,
                "roll": 0,
                "total": 0,
                "broken": False,
                "was_concentrating": False,
            }

        # 0 伤害不触发检定（但 DC 下限 10 已涵盖正常情况）
        if damage_taken <= 0:
            return {
                "success": True,
                "dc": 0,
                "roll": 0,
                "total": 0,
                "broken": False,
                "was_concentrating": True,
            }

        dc = concentration_save_dc(damage_taken)
        res = check.saving_throw(
            mod=con_mod,
            prof=prof_bonus,
            proficient=con_proficient,
            dc=dc,
            advantage=advantage,
            disadvantage=disadvantage,
        )

        if not res.success:
            # 失去集中（R-SPL-020）
            slot.spell_id = None

        return {
            "success": res.success,
            "dc": dc,
            "roll": res.d20,
            "total": res.total,
            "broken": not res.success,
            "was_concentrating": True,
        }


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    mgr = ConcentrationManager()

    # 初始无集中
    assert mgr.get_active_concentration("wiz1") is None

    # 设置集中 (R-SPL-019)
    assert mgr.set_concentration("wiz1", "invisible_wiz1")
    assert mgr.get_active_concentration("wiz1") == "invisible_wiz1"

    # 新专注覆盖旧专注 (R-SPL-019 max 1 concurrent)
    mgr.set_concentration("wiz1", "fly_wiz1")
    assert mgr.get_active_concentration("wiz1") == "fly_wiz1"

    # 主动中断 (R-SPL-019 voluntaryEnd)
    assert mgr.break_concentration("wiz1") is True
    assert mgr.get_active_concentration("wiz1") is None
    # 再次中断返回 False
    assert mgr.break_concentration("wiz1") is False

    # 多个施法者互不干扰
    mgr.set_concentration("wiz1", "a1")
    mgr.set_concentration("wiz2", "a2")
    assert mgr.get_active_concentration("wiz1") == "a1"
    assert mgr.get_active_concentration("wiz2") == "a2"
    mgr.break_concentration("wiz1")
    assert mgr.get_active_concentration("wiz1") is None
    assert mgr.get_active_concentration("wiz2") == "a2"

    # 集中维持 DC (R-SPL-020)
    assert concentration_save_dc(0) == 10       # 下限10
    assert concentration_save_dc(5) == 10       # floor(2.5)=2 → max(10,2)=10
    assert concentration_save_dc(20) == 10      # floor(10)=10 → max(10,10)=10
    assert concentration_save_dc(22) == 11      # floor(11)=11
    assert concentration_save_dc(25) == 12      # floor(12.5)=12
    assert concentration_save_dc(60) == 30      # 上限30
    assert concentration_save_dc(100) == 30     # 上限30

    # 受伤集中豁免 — 用 monkeypatch 固定 d20
    orig = check.saving_throw
    mgr2 = ConcentrationManager()
    mgr2.set_concentration("c1", "spell_x")

    # 成功维持：d20=15, con_mod=3, prof=2 → 15+3+2=20 ≥ DC10
    check.saving_throw = lambda **kw: type("R", (), {
        "success": True, "d20": 15, "total": 20
    })()
    r = mgr2.concentration_save_on_damage("c1", 10, con_mod=3,
                                          con_proficient=True, prof_bonus=2)
    assert r["success"] is True and r["dc"] == 10
    assert mgr2.get_active_concentration("c1") == "spell_x"  # 仍集中

    # 失败失去：d20=2, con_mod=0, prof=0 → 2 < DC10
    check.saving_throw = lambda **kw: type("R", (), {
        "success": False, "d20": 2, "total": 2
    })()
    r = mgr2.concentration_save_on_damage("c1", 10, con_mod=0,
                                          con_proficient=False, prof_bonus=0)
    assert r["success"] is False and r["broken"] is True
    assert mgr2.get_active_concentration("c1") is None  # 失去集中

    # 未在集中时受伤 — 不触发检定
    r = mgr2.concentration_save_on_damage("c1", 20, con_mod=0,
                                          con_proficient=False, prof_bonus=0)
    assert r["was_concentrating"] is False and r["success"] is True

    # 0 伤害不触发
    mgr2.set_concentration("c1", "y")
    r = mgr2.concentration_save_on_damage("c1", 0, con_mod=0,
                                          con_proficient=False, prof_bonus=0)
    assert r["success"] is True and r["dc"] == 0
    assert mgr2.get_active_concentration("c1") == "y"

    check.saving_throw = orig
    print("[concentration] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
