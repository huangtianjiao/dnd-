"""2024 版本污染回归套件（改造方案 §13.4《2014 污染回归套件》+ 第21节任务8）。

两类测试:
  1) 当前仍存在的 2014 污染 — 以 @pytest.mark.xfail(strict=True) 锁定：
     污染在 → XFAIL（机器持续发现）；污染修复 → XPASS 失败，提醒把断言转正。
     这保证「修复 = 测试变绿的唯一途径」，而不是被静默忽略。
  2) 已正确的 2024 语义 — 直接断言（负向回归，防旧版结构回流）。

规则依据:
  改造方案 §13.4：
    - Berserker Frenzy 不使用旧版「额外攻击 + 力竭」机制
    - Bard 不出现旧 Song of Rest / 核心级 5 额外攻击
    - Cleric/… 子职业 entry level 与 2024 ruleset 一致
    - Fighter Indomitable progression 与 2024 ruleset 一致
    - Fighter/Rogue 额外 ASI 节点不被全局 FEAT_LEVELS 吞掉
"""

from __future__ import annotations

import pytest

# ──────────────────────────────────────────────────────────────────────────
# Berserker Frenzy — 2014: 狂乱=额外攻击+1级力竭；2024: 狂暴中额外伤害骰
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("edition.regression.barbarian")
class TestBerserkerFrenzyNoExhaustion:
    @pytest.mark.xfail(
        strict=True,
        reason="已知污染: class_features.berserker_frenzy 仍为 2014「额外攻击+力竭」（P4 修复）")
    def test_frenzy_no_fighter_style_extra_attack_exhaustion(self):
        """狂乱不应携带旧版力竭机制（2024 Berserker Frenzy 是伤害骰而非力竭）。"""
        from aidm.data import class_features as cf
        frenzy = next(
            f for levels in cf.CLASS_FEATURES["barbarian"].values()
            for f in levels if f.feature_id == "berserker_frenzy")
        assert "力竭" not in frenzy.description
        assert frenzy.source_level == 3    # 2024 子职在 3 级

    def test_barbarian_rage_no_exhaustion(self):
        """基础狂暴（Rage）本身不含力竭副作用。"""
        from aidm.data import class_features as cf
        rage = next(
            f for levels in cf.CLASS_FEATURES["barbarian"].values()
            for f in levels if f.feature_id == "barbarian_rage")
        assert "力竭" not in rage.description


# ──────────────────────────────────────────────────────────────────────────
# Bard — 2014: Song of Rest + 核心 5 级额外攻击；2024: 均不成立
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("edition.regression.bard")
class TestBardNo2014Structures:
    @pytest.mark.xfail(
        strict=True,
        reason="已知污染: bard_extra_attack 5 级仍在 class_features 主表（P4 移除）")
    def test_bard_no_core_extra_attack(self):
        """2024 吟游诗人核心职业无 5 级额外攻击（仅勇气/刀锋学院 6 级子职特性）。"""
        from aidm.data import class_features as cf
        entry = cf.CLASS_FEATURES["bard"]
        for level, feats in entry.items():
            for f in feats:
                assert f.feature_id != "bard_extra_attack", \
                    f"2014 污染: bard_extra_attack 不应存在于 {level} 级"

    def test_bard_college_entry_level_3(self):
        """吟游学院子职 3 级进入（2024 一致，锁定已正确项）。"""
        from aidm.data import class_features as cf
        college = next(f for f in cf.CLASS_FEATURES["bard"][3]
                       if f.feature_id == "bard_college")
        assert college.source_level == 3

    def test_get_extra_attacks_excludes_bard(self):
        """classes.get_extra_attacks 不授予吟游诗人额外攻击（已正确，防回流）。"""
        from aidm.data.classes import get_extra_attacks
        assert get_extra_attacks("吟游诗人", 5) == 0


# ──────────────────────────────────────────────────────────────────────────
# Cleric / 施法者子职 entry — 2024: 子职 3 级进入；1 级为 Divine Order
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("edition.regression.cleric")
class TestClericSubclassEntry2024:
    @pytest.mark.xfail(
        strict=True,
        reason="已知污染: cleric_divine_domain source_level=1（2014 结构；2024 子职 3 级、1 级为 Divine Order）")
    def test_cleric_domain_entry_is_level_3(self):
        """2024 牧师神圣领域在 3 级进入（1 级是 Divine Order 选择）。"""
        from aidm.data import class_features as cf
        domain = next(f for f in cf.CLASS_FEATURES["cleric"][1]
                      if f.feature_id == "cleric_divine_domain")
        assert domain.source_level == 3, "2014 污染: 领域 1 级进入"

    def test_cleric_spellcasting_prepared_at_1(self):
        """牧师 1 级为准备制施法者（2024 一致，锁定已正确项）。"""
        from aidm.data import class_features as cf
        sc = next(f for f in cf.CLASS_FEATURES["cleric"][1]
                  if f.feature_id == "cleric_spellcasting")
        assert sc.source_level == 1


# ──────────────────────────────────────────────────────────────────────────
# Fighter Indomitable — 2014: 5 级；2024: 9 级（13 级两次、17 级三次）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("edition.regression.fighter")
class TestFighterIndomitableProgression:
    def test_indomitable_entry_is_level_9(self):
        """2024 战士不屈在 9 级获得（P4 已修复；5 级不得再出现旧结构）。"""
        from aidm.data import class_features as cf
        indom_at_9 = [f for f in cf.CLASS_FEATURES["fighter"].get(9, [])
                      if f.feature_id == "fighter_indomitable"]
        assert indom_at_9, "不屈必须登记在 9 级"
        assert indom_at_9[0].source_level == 9
        id_at_5 = [f for f in cf.CLASS_FEATURES["fighter"].get(5, [])
                   if f.feature_id == "fighter_indomitable"]
        assert not id_at_5, "2014 污染回流: 不屈不应在 5 级"

    def test_indomitable_uses_driven_by_formula_table(self):
        """不屈次数由 classes.FIGHTER_INDOMITABLE_BY_LEVEL 驱动（9/13/17 级 1/2/3 次）。"""
        from aidm.data.classes import FIGHTER_INDOMITABLE_BY_LEVEL
        assert FIGHTER_INDOMITABLE_BY_LEVEL[9] == 1
        assert FIGHTER_INDOMITABLE_BY_LEVEL[13] == 2
        assert FIGHTER_INDOMITABLE_BY_LEVEL[17] == 3
        assert FIGHTER_INDOMITABLE_BY_LEVEL[8] == 0

    def test_fighter_level5_has_tactical_shift(self):
        """5 级战士特性为「额外攻击 + 战术转进」（2024 锁定已正确项）。"""
        from aidm.data.classes import get_features_for_level
        feats = get_features_for_level("战士", 5)
        assert "额外攻击" in feats
        assert "战术转进" in feats

    def test_fighter_level9_has_indomitable_tactical_master(self):
        """9 级 = 不屈（一次）+ 战术主宰（2024 锁定已正确项）。"""
        from aidm.data.classes import get_features_for_level
        feats = get_features_for_level("战士", 9)
        assert "不屈（一次）" in feats
        assert "战术主宰" in feats


# ──────────────────────────────────────────────────────────────────────────
# Feat/ASI — 2014: 全局 FEAT_LEVELS={4,8,12,16,19}；2024: 职业 prog 驱动的 entitlement
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("edition.regression.feat")
class TestFeatASIDrivenByClassProgression:
    def test_fighter_extra_asi_nodes_via_entitlement(self):
        """战士 6/14 额外 ASI 节点由 entitlement 服务按职业等级生成（P5 已拆除全局旁路）。"""
        from aidm.rules.feat_entitlement import entitled_asi_levels
        nodes6 = entitled_asi_levels({"fighter": 6}, 6)
        assert 4 in nodes6 and 6 in nodes6
        nodes14 = entitled_asi_levels({"fighter": 14}, 14)
        assert 14 in nodes14
        # 泛型职业（法师）6 级无额外节点（只有标准 4）
        wizard6 = entitled_asi_levels({"wizard": 6}, 6)
        assert 6 not in wizard6 and 4 in wizard6

    def test_rogue_extra_asi_level_10(self):
        """游荡者 10 级额外 ASI（2024），按职业等级判定。"""
        from aidm.rules.feat_entitlement import entitled_asi_levels
        assert 10 in entitled_asi_levels({"rogue": 10}, 10)
        assert 10 not in entitled_asi_levels({"fighter": 10}, 10)

    def test_levelup_entitlement_drives_feat_available(self):
        """level_up 返回的 feat_available 由 entitlement 计算（战士 6 级 = True）。"""
        from aidm.brain.levelup import level_up
        character = {
            "level": 5, "xp": 14000, "class_name": "战士",
            "class_levels": {"fighter": 5},
            "scores": {"CON": 15, "STR": 16}, "hp_max": 44,
        }
        result = level_up(character, use_fixed_hp=True)
        assert result["new_level"] == 6
        assert result["feat_available"] is True  # 战士 6 级额外 ASI 节点

    def test_levelup_non_fighter_level6_no_feat(self):
        """非战士职业 6 级无 feat 节点（entitlement 与全局 FEAT_LEVELS 的差异）。"""
        from aidm.brain.levelup import level_up
        character = {
            "level": 5, "xp": 14000, "class_name": "法师",
            "class_levels": {"wizard": 5},
            "scores": {"CON": 14, "INT": 18}, "hp_max": 32,
        }
        result = level_up(character, use_fixed_hp=True)
        assert result["new_level"] == 6
        assert result["feat_available"] is False

    def test_global_feat_levels_covers_standard(self):
        """标准节点 4/8/12/16/19 常量仍在（兼容引用），但生产判断走 entitlement。"""
        from aidm.brain.levelup import FEAT_LEVELS
        assert {4, 8, 12, 16, 19} <= set(FEAT_LEVELS)


# ──────────────────────────────────────────────────────────────────────────
# 2024 关键新语义锁定（§13.4 最后一条：Grapple/Shove/Exhaustion/Rest 等）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("edition.regression.semantics")
class Test2024KeySemantics:
    def test_fighter_level1_has_weapon_mastery(self):
        """战士 1 级获得武器精通（2024 特性表）。"""
        from aidm.data.classes import get_features_for_level
        assert "武器精通" in get_features_for_level("战士", 1)

    @pytest.mark.xfail(
        strict=True,
        reason="已知污染: monk 资源池登记名仍为 'ki'（2024 应 'focus'/Focus Points，P4 迁移）")
    def test_monk_uses_focus_points_registry_name(self):
        """武僧资源登记名为 focus（2024 变更，防旧 Ki 命名回流）。"""
        from aidm.data import class_features as cf
        ki_entries = [f for levels in cf.CLASS_FEATURES["monk"].values()
                      for f in levels
                      if getattr(f, "resource_pool", None)]
        assert ki_entries, "monk 应有资源型特性"
        for f in ki_entries:
            pool = f.resource_pool or {}
            assert pool.get("name") == "focus", \
                f"2014 污染: 武僧资源名 {pool.get('name')!r}（应 focus）"
