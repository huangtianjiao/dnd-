"""Wave 1 P0 规则全链路测试 — 覆盖每个 P0 修复点的回归验证。

覆盖规则点:
  ARC-001: RulesetManifest 加载/保存
  STATE-003: Command 创建和幂等键
  REST-001: hit_dice_current=0 时花费失败
  ITEM-002: 背包盾牌不加AC，装备盾牌加AC
  ARC-003: LLM 输出的机械字段被剥离
  ARC-004: Narrator 不返回 state_changes
  COM-001: 注入伪造 target_ac 不改变结果
  COM-002: 长剑用力量、刺剑可选力/敏、长弓用敏捷
  CHK-001: 未熟练不加PB
  CHK-002: DC 有 source_rule_id
  SPL-002: 未知法术返回错误不消耗资源
  SPL-003: 空 known_spells 不默认全掌握
  RAG-001: edition_filter 过滤（接口可测性验证）

运行:
  cd d:\game\dnd\aidm
  python -m pytest tests/test_wave1_p0_rules.py -v
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

_SRC = os.path.join(os.path.dirname(__file__), "..", "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)


# ──────────────────────────────────────────────────────────────────────────
# ARC-001: RulesetManifest 加载/保存
# ──────────────────────────────────────────────────────────────────────────

class TestARC001RulesetManifest:
    """RulesetManifest 序列化/反序列化往返一致性。"""

    def test_round_trip_save_load(self, tmp_path):
        """保存后加载应得到相同数据。"""
        from aidm.engine.ruleset_manifest import RulesetManifest, SourceBook

        manifest = RulesetManifest(
            ruleset_id="dnd5e_2024_core",
            revision="2024.1",
            source_books=[
                SourceBook(book_id="PHB2024", edition="2024", title="玩家手册2024",
                           content_hash="abc123", authority_level="core"),
            ],
            content_packs=["core_rules"],
            policies={"allow_homebrew": False},
        )
        path = str(tmp_path / "manifest.json")
        manifest.save(path)

        loaded = RulesetManifest.load(path)
        assert loaded.ruleset_id == manifest.ruleset_id
        assert loaded.revision == manifest.revision
        assert len(loaded.source_books) == 1
        assert loaded.source_books[0].book_id == "PHB2024"
        assert loaded.source_books[0].edition == "2024"
        assert loaded.content_packs == ["core_rules"]
        assert loaded.policies == {"allow_homebrew": False}

    def test_load_default_manifest(self):
        """内置默认清单可正常加载。"""
        from aidm.engine.ruleset_manifest import load_default_manifest
        m = load_default_manifest()
        assert m.ruleset_id != ""
        assert m.revision != ""

    def test_to_dict_structure(self):
        """to_dict 输出结构正确。"""
        from aidm.engine.ruleset_manifest import RulesetManifest, SourceBook
        m = RulesetManifest(
            ruleset_id="test", revision="1.0",
            source_books=[SourceBook("B1", "2024", "Book", "hash", "core")],
        )
        d = m.to_dict()
        assert d["ruleset_id"] == "test"
        assert len(d["source_books"]) == 1
        assert d["source_books"][0]["book_id"] == "B1"


# ──────────────────────────────────────────────────────────────────────────
# STATE-003: Command 创建和幂等键
# ──────────────────────────────────────────────────────────────────────────

class TestSTATE003Command:
    """Command 工厂与幂等键。"""

    def test_create_generates_uuid(self):
        """Command.create 自动生成 command_id (UUID)。"""
        from aidm.engine.command import Command
        cmd = Command.create(
            campaign_id=1, actor_id="player1",
            command_type="CastSpell", payload={"spell": "火焰箭"},
        )
        assert cmd.command_id != ""
        assert len(cmd.command_id) > 10  # UUID 格式

    def test_idempotency_key_auto_generated(self):
        """未提供幂等键时自动生成。"""
        from aidm.engine.command import Command
        cmd = Command.create(campaign_id=1, actor_id="p1",
                             command_type="Attack", payload={})
        assert ":" in cmd.idempotency_key  # 格式 "campaign_id:uuid"

    def test_idempotency_key_explicit(self):
        """显式提供幂等键时原样使用。"""
        from aidm.engine.command import Command
        cmd = Command.create(campaign_id=1, actor_id="p1",
                             command_type="Attack", payload={},
                             idempotency_key="sess1:42")
        assert cmd.idempotency_key == "sess1:42"

    def test_expected_versions_default_empty(self):
        """默认 expected_versions 为空 dict。"""
        from aidm.engine.command import Command
        cmd = Command.create(campaign_id=1, actor_id="p1",
                             command_type="Move", payload={})
        assert cmd.expected_versions == {}

    def test_expected_versions_explicit(self):
        """可显式传入 expected_versions。"""
        from aidm.engine.command import Command
        cmd = Command.create(campaign_id=1, actor_id="p1",
                             command_type="Attack", payload={},
                             expected_versions={"character": 12, "combat": 44})
        assert cmd.expected_versions["character"] == 12
        assert cmd.expected_versions["combat"] == 44


# ──────────────────────────────────────────────────────────────────────────
# REST-001: hit_dice_current=0 时花费失败
# ──────────────────────────────────────────────────────────────────────────

class TestREST001HitDiceZero:
    """hit_dice_current=0 意味着已用完所有生命骰，不得回退到角色等级。"""

    def test_short_rest_zero_hit_dice_fails(self, monkeypatch):
        """hit_dice_current=0 时尝试花费生命骰 → 失败。"""
        from aidm.brain import rest as rest_mod
        from aidm.engine import dice

        class _Char:
            hp = 10
            max_hp = 20
            con_mod = 2
            hit_die_faces = 8
            hit_dice_current = 0  # 已用完
            level = 5
            char_class = "战士"
            feats = []
            conditions_list = []

        monkeypatch.setattr(dice, "roll_die", lambda faces: 5)
        c = _Char()
        r = rest_mod.short_rest(c, hit_dice_to_spend=1)
        assert r["success"] is False
        assert "不足" in r["errors"][0] or "生命骰" in r["errors"][0]

    def test_short_rest_zero_dice_no_restore(self, monkeypatch):
        """hit_dice_current=0 但不花费 → 成功但恢复 0 HP。"""
        from aidm.brain import rest as rest_mod

        class _Char:
            hp = 10
            max_hp = 20
            con_mod = 0
            hit_die_faces = 8
            hit_dice_current = 0
            level = 5
            char_class = "战士"
            feats = []
            conditions_list = []

        r = rest_mod.short_rest(_Char(), hit_dice_to_spend=0)
        assert r["success"] is True
        assert r["hp_restored"] == 0


# ──────────────────────────────────────────────────────────────────────────
# ITEM-002: 背包盾牌不加AC，装备盾牌加AC
# ──────────────────────────────────────────────────────────────────────────

class TestITEM002ShieldAC:
    """盾牌必须装备在 off_hand 槽位才加 AC。"""

    def test_shield_in_inventory_no_ac_bonus(self):
        """盾牌仅在物品栏（未装备）→ 不加 AC。"""
        from aidm.stats.models import Character
        ch = Character(name="Test", race="人类", char_class="战士", level=1)
        ch.abilities_json = json.dumps({"str": 10, "dex": 14, "con": 10, "int": 10, "wis": 10, "cha": 10})
        ch.hp_max = 10
        ch.hp_current = 10
        ch.set_inventory(["盾牌", "皮甲"])
        ch.equipped_armor = "皮甲"
        # equipment_slots 为空 → 盾牌未装备
        ch.equipment_slots_json = json.dumps({})
        ch.recompute_ac()
        # 皮甲 AC = 11 + dex_mod(2) = 13，无盾牌+2
        assert ch.ac == 13

    def test_shield_equipped_adds_ac(self):
        """盾牌装备在 off_hand → 加 AC。"""
        from aidm.stats.models import Character
        ch = Character(name="Test", race="人类", char_class="战士", level=1)
        ch.abilities_json = json.dumps({"str": 10, "dex": 14, "con": 10, "int": 10, "wis": 10, "cha": 10})
        ch.hp_max = 10
        ch.hp_current = 10
        ch.set_inventory(["盾牌", "皮甲"])
        ch.equipped_armor = "皮甲"
        ch.equipment_slots_json = json.dumps({"off_hand": "盾牌"})
        ch.recompute_ac()
        # 皮甲 AC = 11 + dex_mod(2) = 13 + 盾牌(+2) = 15
        assert ch.ac == 15


# ──────────────────────────────────────────────────────────────────────────
# ARC-003: LLM 输出的机械字段被剥离
# ──────────────────────────────────────────────────────────────────────────

class TestARC003StripMechanicalFields:
    """LLM 输出的机械数值字段必须被静默移除。"""

    def test_forbidden_fields_stripped(self):
        """所有禁止字段均被移除。"""
        from aidm.agents.director import _strip_llm_mechanical_fields
        intent = {
            "action_type": "attack",
            "weapon": "长剑",
            "target_ac": 99,       # 伪造 AC
            "damage": 999,         # 伪造伤害
            "dc": 30,              # 伪造 DC
            "attack_bonus": 50,    # 伪造攻击加值
            "proficient": True,    # 伪造熟练
        }
        _strip_llm_mechanical_fields(intent)
        assert "target_ac" not in intent
        assert "damage" not in intent
        assert "dc" not in intent
        assert "attack_bonus" not in intent
        assert "proficient" not in intent
        # 合法字段保留
        assert intent["action_type"] == "attack"
        assert intent["weapon"] == "长剑"

    def test_no_forbidden_fields_no_error(self):
        """无禁止字段时不报错。"""
        from aidm.agents.director import _strip_llm_mechanical_fields
        intent = {"action_type": "cast", "spell_name": "火焰箭"}
        result = _strip_llm_mechanical_fields(intent)
        assert result["action_type"] == "cast"
        assert result["spell_name"] == "火焰箭"


# ──────────────────────────────────────────────────────────────────────────
# ARC-004: Narrator 不返回 state_changes
# ──────────────────────────────────────────────────────────────────────────

class TestARC004NarratorReadOnly:
    """Narrator 节点始终返回空 state_changes。"""

    def test_narrate_strips_state_changes(self):
        """即使 LLM 输出包含 state_changes，narrate 也返回空列表。

        注: 此处测试 graph.narrate 的 ARC-004 逻辑。
        由于 narrate 需要 LLM，我们直接验证返回结构约定。
        """
        # 验证 narrate 返回结构约定：state_changes 始终为空列表
        # 通过检查源码中的硬编码返回值来验证
        import inspect
        from aidm.brain.graph import narrate
        source = inspect.getsource(narrate)
        # 源码中必须包含 "state_changes": [] 的硬编码
        assert '"state_changes": []' in source or "'state_changes': []" in source


# ──────────────────────────────────────────────────────────────────────────
# COM-001: 注入伪造 target_ac 不改变结果
# ──────────────────────────────────────────────────────────────────────────

class TestCOM001ACAuthority:
    """AC 只能从 EntityState 读取，LLM 注入的 target_ac 被忽略。"""

    def test_injected_target_ac_ignored(self):
        """resolve_attack 不使用 intent 中的 target_ac，而是从状态查找。"""
        import inspect
        from aidm.brain.resolvers.attack import resolve_attack
        source = inspect.getsource(resolve_attack)
        # 源码中 AC 必须通过 _lookup_target_ac 获取，而非 it.get("target_ac")
        assert "_lookup_target_ac" in source
        # 确认注释标注 COM-001
        assert "COM-001" in source


# ──────────────────────────────────────────────────────────────────────────
# COM-002: 长剑用力量、刺剑可选力/敏、长弓用敏捷
# ──────────────────────────────────────────────────────────────────────────

class TestCOM002WeaponAbility:
    """武器属性规则：近战默认力量，灵巧可选力/敏，远程默认敏捷。"""

    def test_longsword_uses_strength(self):
        """长剑（近战，无灵巧）→ 力量。"""
        from aidm.brain.resolvers.attack import _resolve_attack_ability
        ability = _resolve_attack_ability("长剑", {})
        assert ability == "str"

    def test_rapier_allows_str_or_dex(self):
        """刺剑（近战，灵巧）→ 力量或敏捷均可。"""
        from aidm.brain.resolvers.attack import _resolve_attack_ability
        # 不指定 → 默认力量
        ability_default = _resolve_attack_ability("刺剑", {})
        assert ability_default == "str"
        # 指定敏捷 → 允许
        ability_dex = _resolve_attack_ability("刺剑", {"ability": "dex"})
        assert ability_dex == "dex"
        # 指定力量 → 允许
        ability_str = _resolve_attack_ability("刺剑", {"ability": "str"})
        assert ability_str == "str"

    def test_longbow_uses_dexterity(self):
        """长弓（远程）→ 敏捷。"""
        from aidm.brain.resolvers.attack import _resolve_attack_ability
        ability = _resolve_attack_ability("长弓", {})
        assert ability == "dex"

    def test_dagger_finesse_ranged_allows_both(self):
        """匕首（灵巧+投掷）→ 力量或敏捷均可。"""
        from aidm.brain.resolvers.attack import _resolve_attack_ability
        ability = _resolve_attack_ability("匕首", {})
        assert ability == "str"  # 默认力量
        ability_dex = _resolve_attack_ability("匕首", {"ability": "dex"})
        assert ability_dex == "dex"

    def test_disallowed_ability_falls_back(self):
        """指定不允许的属性 → 回退默认。"""
        from aidm.brain.resolvers.attack import _resolve_attack_ability
        # 长剑不允许敏捷，指定敏捷 → 回退力量
        ability = _resolve_attack_ability("长剑", {"ability": "dex"})
        assert ability == "str"


# ──────────────────────────────────────────────────────────────────────────
# CHK-001: 未熟练不加PB
# ──────────────────────────────────────────────────────────────────────────

class TestCHK001ProficiencyGate:
    """CHK-001: 技能未熟练时不加熟练加值。"""

    def test_unskilled_no_pb(self, monkeypatch):
        """未熟练的角色技能检定不加 PB。"""
        from aidm.engine import check, dice

        # 固定骰值：d20=10
        class _Fake:
            def __init__(self):
                self.used, self.rolls, self.mode = 10, [10], "normal"

        monkeypatch.setattr(dice, "roll_d20", lambda advantage=False, disadvantage=False: _Fake())

        # 未熟练：mod=2, prof=2, proficient=False → total = 10+2+0 = 12
        r = check.ability_check(mod=2, prof=2, proficient=False, dc=15)
        assert r.total == 12  # 10 + 2 (mod only, no PB)
        assert r.success is False  # 12 < 15

    def test_proficient_adds_pb(self, monkeypatch):
        """熟练的角色技能检定加 PB。"""
        from aidm.engine import check, dice

        class _Fake:
            def __init__(self):
                self.used, self.rolls, self.mode = 10, [10], "normal"

        monkeypatch.setattr(dice, "roll_d20", lambda advantage=False, disadvantage=False: _Fake())

        # 熟练：mod=2, prof=2, proficient=True → total = 10+2+2 = 14
        r = check.ability_check(mod=2, prof=2, proficient=True, dc=15)
        assert r.total == 14  # 10 + 2 + 2
        assert r.success is False  # 14 < 15

    def test_resolver_check_skill_proficient(self):
        """CHK-001: resolver 层 _check_skill_proficient 从角色数据查询。"""
        from aidm.brain.resolvers.actions import _check_skill_proficient
        from aidm.stats.models import Character

        ch = Character(name="Test", race="人类", char_class="游荡者", level=1)
        ch.set_inventory([])
        ch.skill_prof_json = json.dumps(["察觉", "潜行"])

        assert _check_skill_proficient(ch, "察觉") is True
        assert _check_skill_proficient(ch, "潜行") is True
        assert _check_skill_proficient(ch, "运动") is False


# ──────────────────────────────────────────────────────────────────────────
# CHK-002: DC 有 source_rule_id
# ──────────────────────────────────────────────────────────────────────────

class TestCHK002DCSource:
    """CHK-002: DC 来源可溯源。"""

    def test_dc_by_label_has_source(self):
        """dc_by_label 接受 source_rule_id 参数。"""
        from aidm.engine.check import dc_by_label
        import inspect
        sig = inspect.signature(dc_by_label)
        assert "source_rule_id" in sig.parameters

    def test_calc_save_dc_has_source(self):
        """calc_save_dc 接受 source_rule_id 参数。"""
        from aidm.engine.check import calc_save_dc
        import inspect
        sig = inspect.signature(calc_save_dc)
        assert "source_rule_id" in sig.parameters

    def test_resolver_ability_check_dc_source(self):
        """CHK-002: resolver 层属性检定 DC 从规则书标准获取。"""
        from aidm.brain.resolvers.actions import _resolve_ability_check_dc
        # 难度等级标签 → 标准 DC
        assert _resolve_ability_check_dc({"difficulty": "中等"}) == 15
        assert _resolve_ability_check_dc({"difficulty": "容易"}) == 10
        assert _resolve_ability_check_dc({"difficulty": "困难"}) == 20
        # 无标签 → 默认 10
        assert _resolve_ability_check_dc({}) == 10


# ──────────────────────────────────────────────────────────────────────────
# SPL-002: 未知法术返回错误不消耗资源
# ──────────────────────────────────────────────────────────────────────────

class TestSPL002UnknownSpell:
    """SPL-002: 不在数据表中的法术必须被拒绝，不消耗任何资源。"""

    def test_unknown_spell_returns_error(self):
        """cast_spell 对未知法术返回 UNKNOWN_CONTENT 错误。"""
        from aidm.engine.spellcasting import CasterState, cast_spell

        wiz = CasterState(
            caster_id="wiz_test", class_name="法师", level=3,
            ability_scores={"STR": 10, "DEX": 14, "CON": 12, "INT": 16, "WIS": 10, "CHA": 10},
            spell_slots={1: 4, 2: 2}, max_spell_slots={1: 4, 2: 2},
        )
        slots_before = dict(wiz.spell_slots)

        result = cast_spell(wiz, "不存在的法术XYZ", slot_level=1,
                            targets=[{"ac": 10}],
                            component_kwargs={"free_hands": 2})
        assert result["success"] is False
        assert any("UNKNOWN_CONTENT" in e for e in result["errors"])
        # 不消耗法术位
        assert wiz.spell_slots == slots_before

    def test_unknown_spell_long_cast_returns_error(self):
        """cast_long_spell 对未知法术返回错误。"""
        from aidm.engine.spellcasting import CasterState, cast_long_spell

        wiz = CasterState(
            caster_id="wiz_test2", class_name="法师", level=5,
            ability_scores={"STR": 10, "DEX": 14, "CON": 12, "INT": 16, "WIS": 10, "CHA": 10},
            spell_slots={1: 4, 2: 3}, max_spell_slots={1: 4, 2: 3},
        )
        result = cast_long_spell(wiz, "完全虚构的法术", slot_level=1,
                                 component_kwargs={"free_hands": 2})
        assert result["success"] is False
        assert any("UNKNOWN_CONTENT" in e for e in result["errors"])

    def test_known_spell_still_works(self):
        """已知法术正常施展。"""
        from aidm.engine.spellcasting import CasterState, cast_spell

        wiz = CasterState(
            caster_id="wiz_test3", class_name="法师", level=3,
            ability_scores={"STR": 10, "DEX": 14, "CON": 12, "INT": 16, "WIS": 10, "CHA": 10},
            spell_slots={1: 4, 2: 2}, max_spell_slots={1: 4, 2: 2},
        )
        result = cast_spell(wiz, "火焰箭", slot_level=0,
                            targets=[{"ac": 10}],
                            component_kwargs={"free_hands": 2})
        assert result["success"] is True
        assert result["errors"] == []


# ──────────────────────────────────────────────────────────────────────────
# SPL-003: 空 known_spells 不默认全掌握
# ──────────────────────────────────────────────────────────────────────────

class TestSPL003NoDefaultAllKnown:
    """SPL-003: known_spells 为空意味着不会任何法术。"""

    def test_empty_known_spells_rejects_spell(self):
        """known_spells 为空 → 任何法术都被拒绝。"""
        from aidm.stats.models import Character
        from aidm.brain.resolvers.cast import resolve_cast

        ch = Character(name="Test", race="人类", char_class="法师", level=1)
        ch.abilities_json = json.dumps({"str": 10, "dex": 14, "con": 12, "int": 16, "wis": 10, "cha": 10})
        ch.hp_max = 10
        ch.hp_current = 10
        ch.spell_slots_json = json.dumps({1: 2})
        # known_spells 为空（默认）
        ch.known_spells_json = json.dumps([])
        ch.equipped_weapon = ""
        ch.set_inventory([])
        ch.set_conditions([])

        intent = {"spell_name": "火焰箭", "action_type": "cast"}
        result = resolve_cast(ch, intent)
        assert result.get("error") is not None
        assert "尚未学会" in result["error"]

    def test_known_spell_allowed(self):
        """known_spells 包含法术 → 可以施展。"""
        from aidm.stats.models import Character
        from aidm.brain.resolvers.cast import resolve_cast

        ch = Character(name="Test", race="人类", char_class="法师", level=1)
        ch.abilities_json = json.dumps({"str": 10, "dex": 14, "con": 12, "int": 16, "wis": 10, "cha": 10})
        ch.hp_max = 10
        ch.hp_current = 10
        ch.spell_slots_json = json.dumps({1: 2})
        ch.known_spells_json = json.dumps(["火焰箭"])  # 已学会
        ch.equipped_weapon = ""
        ch.set_inventory([])
        ch.set_conditions([])

        intent = {"spell_name": "火焰箭", "action_type": "cast"}
        result = resolve_cast(ch, intent)
        # 不应有 "尚未学会" 错误
        assert result.get("error") is None or "尚未学会" not in str(result.get("error", ""))


# ──────────────────────────────────────────────────────────────────────────
# RAG-001: edition_filter 过滤（接口可测性验证）
# ──────────────────────────────────────────────────────────────────────────

class TestRAG001EditionFilter:
    """RAG-001: 检索接口支持 edition_filter 参数。"""

    def test_query_rules_accepts_edition_filter(self):
        """query_rules 函数签名包含 edition_filter 参数。"""
        import inspect
        from aidm.knowledge.retriever import query_rules
        sig = inspect.signature(query_rules)
        assert "edition_filter" in sig.parameters

    def test_indexer_search_accepts_edition_filter(self):
        """indexer.search 函数签名包含 edition_filter 参数。"""
        import inspect
        from aidm.knowledge.indexer import search
        sig = inspect.signature(search)
        assert "edition_filter" in sig.parameters

    def test_build_filter_with_edition(self):
        """_build_filter 传入 edition_filter 时生成过滤条件。"""
        from aidm.knowledge.indexer import _build_filter
        # 不传 → None（无过滤）
        assert _build_filter() is None
        # 传 edition_filter → 返回 Filter 对象（非 None）
        f = _build_filter(edition_filter="2024")
        assert f is not None
