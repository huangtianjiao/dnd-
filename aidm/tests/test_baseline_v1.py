"""第一轮 P0/P1 基础锁定测试（改造方案 v1.0 第21节任务 2-7）。

覆盖:
  - 任务2 (R-DRV-001): 服务器权威 derived stats — 客户端提交值被忽略，
    save→reload 派生值一致，三处创建入口共用唯一 derive 入口
  - 任务3 (R-RSM-001): RulesetManifest v2 字段（mechanics_baseline/
    house_rule_pack/schema_revision）+ Campaign 规则模式 + migration 002
  - 任务4 (R-CON-001): RuleConformanceMatrix 注册/序列化/CI 输出
  - 任务6 (R-GRC-001): CharacterGrant/CharacterChoice 持久化与幂等
  - 任务7 (R-FGT-001): Fighter golden snapshots 结构与基线对照

运行:
  cd aidm && python -m pytest tests/test_baseline_v1.py -v
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

import golden_fighter_2024 as golden


def _tmp_db() -> str:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    Path(path).unlink()
    return f"sqlite:///{path}"


def _cleanup(db: str) -> None:
    """释放 SQLite 引擎句柄后删除临时库（Windows 文件锁）。"""
    from contextlib import suppress

    from aidm.stats import store
    eng = store._engines.pop(db, None)
    if eng is not None:
        eng.dispose()
    with suppress(PermissionError, FileNotFoundError):
        Path(db.replace("sqlite:///", "")).unlink()


# ──────────────────────────────────────────────────────────────────────────
# 任务2 — 服务器权威机械属性（R-DRV-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-DRV-001")
class TestDeriveStatsAuthority:
    def test_client_submitted_mechanical_stats_ignored(self):
        """客户端提交 hp_max/ac/speed 被服务器值覆盖（P1-01 语义）。"""
        from aidm.build.derive_stats import apply_server_stats
        from aidm.stats.models import Character

        ch = Character(name="测试", race="人类", char_class="战士", level=5)
        ch.set_abilities({"str": 16, "dex": 10, "con": 15, "int": 10, "wis": 12, "cha": 10})
        ch.hp_max = 999          # 客户端伪造值
        ch.hp_current = 999
        ch.ac = 42
        ch.speed = 999
        apply_server_stats(ch, "战士", "人类", 5,
                           {"str": 16, "dex": 10, "con": 15, "int": 10, "wis": 12, "cha": 10})
        assert ch.hp_max == 44     # 满骰10+2 → 之后每级(6+2)
        assert ch.hp_current == ch.hp_max
        assert ch.ac == 10         # 无甲 10（战士无无甲防御）
        assert ch.speed == 30

    def test_save_reload_derived_stats_consistent(self):
        """save → reload 后派生值（HP/AC/速度/PB）与创建时完全一致。"""
        from aidm.build.derive_stats import apply_server_stats
        from aidm.stats import store
        from aidm.stats.models import Character

        db = _tmp_db()
        camp = store.create_campaign("战役", db)
        ch = Character(name="阿拉贡", race="人类", char_class="战士", level=5,
                       campaign_id=camp.id)
        ch.set_abilities({"str": 16, "dex": 12, "con": 15, "int": 10, "wis": 12, "cha": 10})
        apply_server_stats(ch, "战士", "人类", 5,
                           {"str": 16, "dex": 12, "con": 15, "int": 10, "wis": 12, "cha": 10})
        ch = store.save_character(ch, db)
        snapshot = (ch.hp_max, ch.hp_current, ch.ac, ch.speed)

        loaded = store.get_character(ch.id, db)
        assert (loaded.hp_max, loaded.hp_current, loaded.ac, loaded.speed) == snapshot
        assert loaded.prof() == 3  # 5 级熟练 +3
        _cleanup(db)

    def test_all_creation_entrypoints_share_derive(self):
        """/character、/join、/room/join 三个创建入口均引用 apply_server_stats。"""
        from pathlib import Path
        src = Path(__file__).resolve().parents[1] / "src"
        for rel in ("api/routes/character.py", "api/routes/room.py"):
            code = (src / "aidm" / rel).read_text(encoding="utf-8")
            assert "apply_server_stats" in code, f"{rel} 未使用服务器权威推导"


# ──────────────────────────────────────────────────────────────────────────
# 任务3 — RulesetManifest v2（R-RSM-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-RSM-001")
class TestRulesetManifestV2:
    def test_default_manifest_v2_fields(self):
        """默认 manifest 具备 mechanics_baseline / content_packs / house_rule_pack / schema_revision。"""
        from aidm.engine.ruleset_manifest import load_default_manifest
        m = load_default_manifest()
        assert m.mechanics_baseline == "srd_5.2.1"
        assert m.content_packs == ["srd_5.2.1_core"]
        assert m.house_rule_pack is None
        assert m.schema_revision == 3

    def test_round_trip_preserves_v2_fields(self):
        from aidm.engine.ruleset_manifest import RulesetManifest
        m = RulesetManifest(
            ruleset_id="dnd5e_2024_core", revision="2024.1",
            content_packs=["srd_5.2.1_core"],
            mechanics_baseline="srd_5.2.1",
            house_rule_pack=None, schema_revision=3)
        d = m.to_dict()
        assert d["mechanics_baseline"] == "srd_5.2.1"
        assert d["schema_revision"] == 3
        assert "house_rule_pack" in d
        loaded = RulesetManifest.from_dict(d)
        assert loaded.mechanics_baseline == m.mechanics_baseline
        assert loaded.house_rule_pack == m.house_rule_pack
        assert loaded.schema_revision == 3

    def test_old_manifest_missing_v2_fields_backward_compatible(self):
        """旧 manifest（无新字段）加载时不报错并回退默认值。"""
        from aidm.engine.ruleset_manifest import RulesetManifest
        old = {"ruleset_id": "dnd5e_2024_core", "revision": "2024.1",
               "source_books": [], "content_packs": [], "policies": {}}
        m = RulesetManifest.from_dict(old)
        assert m.mechanics_baseline == "srd_5.2.1"
        assert m.house_rule_pack is None
        assert m.schema_revision == 3

    def test_rules_mode_enum(self):
        from aidm.engine.ruleset_manifest import RulesMode
        assert RulesMode.RAW_2024.value == "raw_2024"
        assert RulesMode.RAW_2024_OPTIONAL.value == "raw_2024_optional"
        assert RulesMode.HOUSE_RULE.value == "house_rule"
        assert RulesMode.FREEFORM.value == "freeform"


@pytest.mark.rule("R-RSM-001")
class TestCampaignRulesMode:
    def test_campaign_default_mode_and_baseline(self):
        """Campaign 默认 raw_2024 + mechanics_baseline 固化自 manifest。"""
        from aidm.stats import store
        db = _tmp_db()
        camp = store.create_campaign("默认战役", db)
        assert camp.rules_mode == "raw_2024"
        assert camp.mechanics_baseline == "srd_5.2.1"
        assert camp.ruleset_id == "dnd5e_2024_core"
        _cleanup(db)

    def test_campaign_custom_mode(self):
        from aidm.stats import store
        db = _tmp_db()
        camp = store.create_campaign("房规战役", db, rules_mode="house_rule")
        assert camp.rules_mode == "house_rule"
        reloaded = store.get_campaign(camp.id, db)
        assert reloaded.rules_mode == "house_rule"  # save→reload 不丢
        _cleanup(db)

    def test_campaign_invalid_mode_rejected(self):
        """未知规则模式 fail closed——不允许伪装成 RAW。"""
        from aidm.stats import store
        db = _tmp_db()
        with pytest.raises(ValueError):
            store.create_campaign("坏战役", db, rules_mode="evil_mode")
        _cleanup(db)

    def test_migration_002_backfills_legacy_campaign(self):
        """旧库（无 rules_mode/mechanics_baseline 列）打开时自动迁移补列。"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        con = sqlite3.connect(path)
        con.executescript("""
            CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT (datetime('now')));
            INSERT INTO schema_migrations VALUES (1, datetime('now'));
            CREATE TABLE campaign (
              id INTEGER NOT NULL PRIMARY KEY,
              name VARCHAR NOT NULL,
              setting VARCHAR DEFAULT '' NOT NULL,
              tone VARCHAR DEFAULT '' NOT NULL,
              world_background VARCHAR DEFAULT '' NOT NULL,
              rolling_summary VARCHAR DEFAULT '' NOT NULL,
              world_flags_json VARCHAR DEFAULT '{}' NOT NULL,
              ruleset_id VARCHAR DEFAULT 'dnd5e_2024_core' NOT NULL,
              ruleset_revision VARCHAR DEFAULT '2024.1' NOT NULL,
              content_pack_versions_json VARCHAR DEFAULT '{}' NOT NULL,
              version INTEGER DEFAULT 0 NOT NULL
            );
            INSERT INTO campaign (name, version) VALUES ('旧战役', 0);
        """)
        con.commit()
        con.close()
        from aidm.stats import store
        db = f"sqlite:///{path}"
        store.get_engine(db)
        camp = store.get_campaign(1, db)
        assert camp.rules_mode == "raw_2024"
        assert camp.mechanics_baseline == "srd_5.2.1"
        _cleanup(db)


# ──────────────────────────────────────────────────────────────────────────
# 任务4 — RuleConformanceMatrix（R-CON-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-CON-001")
class TestConformanceMatrix:
    def test_register_get_and_duplicate_rejected(self):
        from aidm.rules.conformance import RawStatus, RuleConformanceMatrix, RuleRecord
        m = RuleConformanceMatrix()
        m.register(RuleRecord(rule_id="R-X-001", domain="character",
                              raw_status=RawStatus.DECLARED.value))
        assert m.get("R-X-001") is not None
        assert len(m) == 1
        with pytest.raises(ValueError):
            m.register(RuleRecord(rule_id="R-X-001"))

    def test_status_progression(self):
        from aidm.rules.conformance import RawStatus, RuleRecord
        r = RuleRecord(rule_id="R-Y-001", wired=True, persisted=True)
        assert r.status() == RawStatus.PERSISTED
        r.e2e_verified = True
        assert r.status() == RawStatus.E2E_VERIFIED
        r2 = RuleRecord(rule_id="R-Y-002")
        assert r2.status() == RawStatus.DECLARED

    def test_default_matrix_report_structure(self):
        """默认矩阵可序列化，summary 含按等级统计（CI 最小输出）。"""
        from aidm.rules.conformance import load_default_matrix
        m = load_default_matrix()
        assert len(m) >= 6
        report = m.to_dict()
        assert report["count"] == len(m)
        assert set(report["summary"].keys()) == {"by_status", "total"}
        assert report["summary"]["total"] == len(m)
        # JSON 报告可解析
        parsed = json.loads(m.json_report())
        assert len(parsed["rules"]) == len(m)

    def test_ci_script_check_exit_zero(self):
        """CI 脚本 --check 退出 0（全部 ≥ 最小状态）。"""
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "run_conformance_report.py"
        r = subprocess.run([sys.executable, str(script), "--check"],
                           capture_output=True, text=True, cwd=root)
        assert r.returncode == 0, r.stderr


# ──────────────────────────────────────────────────────────────────────────
# 任务6 — Grant/Choice 持久化（R-GRC-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-GRC-001")
class TestCharacterGrantsPersistent:
    def _make_character(self, db):
        from aidm.stats import store
        from aidm.stats.models import Character
        camp = store.create_campaign("战役", db)
        ch = Character(name="格兰特", race="人类", char_class="战士", campaign_id=camp.id)
        return store.save_character(ch, db)

    def test_grant_save_reload_with_provenance(self):
        """Grant 持久化：save → reload 后来源/修订/等级/metadata 完整。"""
        from aidm.stats import store
        from aidm.stats.models import CharacterGrant
        db = _tmp_db()
        ch = self._make_character(db)
        g = CharacterGrant(
            grant_id="grant.second_wind",
            grant_type="class",
            source_id="class.fighter",
            source_name="战士",
            source_revision="2024.1",
            granted_item_id="fighter_second_wind",
            level_acquired=1,
            ruleset_revision="2024.1")
        g.set_meta({"source_anchor": "PHB2024 战士 1级"})
        store.add_character_grant(ch, g, db)

        grants = store.list_character_grants(ch.id, db)
        assert len(grants) == 1
        got = grants[0]
        assert got.grant_id == "grant.second_wind"
        assert got.source_id == "class.fighter"
        assert got.source_revision == "2024.1"
        assert got.level_acquired == 1
        assert got.meta == {"source_anchor": "PHB2024 战士 1级"}
        _cleanup(db)

    def test_choice_save_reload_with_legal_options_snapshot(self):
        from aidm.stats import store
        from aidm.stats.models import CharacterChoice
        db = _tmp_db()
        ch = self._make_character(db)
        c = CharacterChoice(
            choice_id="choice.fighting_style",
            choice_type="fighting_style",
            source_id="class.fighter.level1",
            level_at_choice=1,
            ruleset_revision="2024.1",
            validated=False)
        c.set_selected_values(["箭术"])
        c.set_legal_options(["箭术", "防御", "决斗", "巨武器", "防护", "双武器"])
        store.add_character_choice(ch, c, db)

        choices = store.list_character_choices(ch.id, db)
        assert len(choices) == 1
        got = choices[0]
        assert got.selected_values == ["箭术"]
        assert len(got.legal_options) == 6
        assert got.ruleset_revision == "2024.1"
        assert got.validated is False
        _cleanup(db)

    def test_grant_choice_idempotent(self):
        """同 grant_id / choice_id 重复写入返回已有记录（不重复累积）。"""
        from aidm.stats import store
        from aidm.stats.models import CharacterChoice, CharacterGrant
        db = _tmp_db()
        ch = self._make_character(db)
        g1 = store.add_character_grant(
            ch, CharacterGrant(grant_id="g1", grant_type="class", source_id="x"), db)
        g2 = store.add_character_grant(ch, CharacterGrant(grant_id="g1"), db)
        assert g1.id == g2.id
        c1 = store.add_character_choice(
            ch, CharacterChoice(choice_id="c1", choice_type="skill"), db)
        c2 = store.add_character_choice(ch, CharacterChoice(choice_id="c1"), db)
        assert c1.id == c2.id
        assert len(store.list_character_grants(ch.id, db)) == 1
        assert len(store.list_character_choices(ch.id, db)) == 1
        _cleanup(db)


# ──────────────────────────────────────────────────────────────────────────
# 任务7 — Fighter golden snapshots（R-FGT-001）
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.rule("R-FGT-001")
class TestFighterGoldenSnapshots:
    def test_snapshot_structural_completeness(self):
        """8 个关键等级均有完整快照，必填键齐备（P4 逐字段断言契约）。"""
        assert tuple(golden.FIGHTER_GOLDEN.keys()) == tuple(golden.FIGHTER_KEY_LEVELS)
        required = {
            "features", "proficiency_bonus", "extra_attacks",
            "feat_asi_nodes", "weapon_mastery", "spellcasting",
        }
        for level, snap in golden.FIGHTER_GOLDEN.items():
            missing = required - set(snap.keys())
            assert not missing, f"L{level} 快照缺键: {missing}"
        assert len(golden.KNOWN_GAPS) == 0  # P4+P5 已关闭全部 Fighter 差距

    def test_progression_matches_classes_py_baseline(self):
        """快照 progression 与 data/classes 战士表一致（事实基线锁定）。"""
        from aidm.data.classes import CLASS_FEATURES
        assert CLASS_FEATURES["战士"] == golden.FIGHTER_PROGRESSION, \
            "classes.py 战士 progression 被改动，需同步快照"

    def test_known_gaps_reflect_current_implementation(self):
        """已知差距与当前实现一一对应：修复差一 = CI 变红或快照过期。"""
        assert golden.KNOWN_GAPS == ()

    def test_key_level_derived_values(self):
        """关键等级的 HP/PB 派生值与 derive_stats 一致（1/5/9 级抽样）。"""
        from aidm.build.derive_stats import derive_character_stats
        abilities = {"str": 16, "dex": 10, "con": 15, "int": 10, "wis": 12, "cha": 10}
        for level in (1, 5, 9):
            s = derive_character_stats("战士", "人类", level, abilities)
            assert s["proficiency_bonus"] == golden.FIGHTER_GOLDEN[level]["proficiency_bonus"]
            assert s["hp_max"] > 0

    def test_snapshot_levels_include_fighter_extra_asi(self):
        """快照明确 6/14 级为战士额外 ASI 节点（防全局 FEAT_LEVELS 吞掉）。"""
        assert "ASI_OR_FEAT_6" in golden.FIGHTER_GOLDEN[6]["feat_asi_nodes"]
        assert "ASI_OR_FEAT_14" in golden.FIGHTER_GOLDEN[14]["feat_asi_nodes"]
