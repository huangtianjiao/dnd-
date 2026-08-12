"""状态层存储 — SQLite 持久化 / CRUD / rolling summary / 战斗状态序列化。

存档即拷一个 SQLite 文件。提供 Character/Campaign/Scene/CombatState/Log 的增删查，
以及战役 rolling summary 追加（防上下文失忆）与 engine.Combat 的存/取往返。

规则依据见 RULE_SPEC.md §6 数据模型。
"""

from __future__ import annotations

import dataclasses
import json
import os
from contextlib import contextmanager, suppress

from sqlmodel import Session, select

from ..engine import combat as cmb
from ..errors import InvariantViolation  # P2-05: 错误分类
from ..engine import conditions as cond
from . import models as M

# ──────────────────────────────────────────────────────────────────────────
# 引擎与会话
# ──────────────────────────────────────────────────────────────────────────

# RAG-003/可移植性: 存档路径由项目根目录/数据目录派生，不硬编码 Windows 盘符。
# 可用环境变量 AIDM_SAVE_DB 覆盖；P0-09: AIDM_DATA_DIR 统一数据根目录。
def _default_db_path() -> str:
    from ..config import DATA_DIR, get_settings
    default = str(DATA_DIR / "saves" / "save.db")
    return get_settings().aidm_save_db or default


DEFAULT_DB = "sqlite:///" + _default_db_path()


# ──────────────────────────────────────────────────────────────────────────
# P1-07: 版本化数据库迁移（替代 best-effort ALTER）
# ──────────────────────────────────────────────────────────────────────────
# - schema_migrations 表记录已应用版本
# - 迁移按序执行，失败 → 抛错拒绝启动（不再 suppress 吞异常）
# - 老库（无 schema_migrations）→ 基线迁移 001 补齐缺失列后标记

SCHEMA_VERSION = 1  # 当前 schema 版本（新增迁移时 +1）


def _migrate(engine) -> None:
    """版本化迁移入口：按 SCHEMA_VERSION 依次应用未执行的迁移。

    规则: P1-07 — 迁移失败必须抛错（应用拒绝启动），
    不再 best-effort 吞异常继续跑。
    """
    from sqlalchemy import inspect, text
    insp = inspect(engine)
    # 建版本表（幂等）
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            " version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT "
            "(datetime('now')) )"))

    # 读取已应用版本
    applied = set()
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT version FROM schema_migrations"))
        applied = {r[0] for r in rows}

    # 按序执行未应用的迁移
    for version, fn in sorted(_MIGRATIONS.items()):
        if version in applied:
            continue
        fn(engine, insp)          # 失败 → 抛错（拒绝启动）
        with engine.begin() as conn:
            conn.execute(text(
                "INSERT INTO schema_migrations (version) VALUES (:v)"),
                {"v": version})


def _migration_001_add_missing_columns(engine, insp) -> None:
    """基线迁移 001：给已存在表补缺失列（历史行为，纳入版本管理）。"""
    from sqlalchemy import text
    for model in (M.Campaign, M.Scene, M.Character, M.CombatState, M.Log):
        tbl = model.__tablename__
        if not insp.has_table(tbl):
            continue
        existing = {c["name"] for c in insp.get_columns(tbl)}
        with engine.begin() as conn:
            for col in model.__table__.columns:
                if col.name in existing:
                    continue
                coltype = col.type.compile(engine.dialect)
                dv = ""
                if col.default is not None and hasattr(col.default, "arg"):
                    a = col.default.arg
                    dv = f" DEFAULT {'NULL' if a is None else repr(a)}"
                else:
                    tn = str(col.type).upper()
                    dv = " DEFAULT 0" if "INT" in tn or "BOOL" in tn else " DEFAULT ''"
                conn.execute(text(
                    f'ALTER TABLE "{tbl}" ADD COLUMN "{col.name}" {coltype}{dv}'))


# 迁移注册表: {version: 迁移函数}（有序）
_MIGRATIONS: dict[int, object] = {
    1: _migration_001_add_missing_columns,
}


_engines: dict[str, object] = {}


def get_engine(db_path: str | None = None):
    db_path = db_path or DEFAULT_DB
    if db_path not in _engines:
        # 自动建父目录（绝对路径）
        if db_path.startswith("sqlite:///") and ":memory:" not in db_path:
            p = db_path.replace("sqlite:///", "", 1)
            d = os.path.dirname(p)
            if d:
                os.makedirs(d, exist_ok=True)
        _engines[db_path] = M.get_engine(db_path)
        M.SQLModel.metadata.create_all(_engines[db_path])
        _migrate(_engines[db_path])   # P1-07: 版本化迁移（失败即抛错）
    return _engines[db_path]


@contextmanager
def session(db_path: str | None = None):
    db_path = db_path or DEFAULT_DB
    """事务会话上下文。"""
    eng = get_engine(db_path)
    s = Session(eng, expire_on_commit=False)   # 提交后对象仍可用（非 detached）
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


# ──────────────────────────────────────────────────────────────────────────
# 角色卡
# ──────────────────────────────────────────────────────────────────────────

def save_character(ch: M.Character, db_path: str | None = None) -> M.Character:
    db_path = db_path or DEFAULT_DB
    # ★ P1-10: 保存前收敛 inventory 双权威（inventory 权威，items_structured 派生）
    try:
        ch.sync_inventory_views()
    except Exception:  # noqa: BLE001  结构性视图同步失败不阻断主保存
        pass
    with session(db_path) as s:
        s.add(ch)
        s.commit()
        s.refresh(ch)
        return ch


def get_character(cid: int, db_path: str | None = None) -> M.Character | None:
    db_path = db_path or DEFAULT_DB
    with session(db_path) as s:
        return s.get(M.Character, cid)


# ──────────────────────────────────────────────────────────────────────────
# 存档迁移（engine.migration 权威实现）
# ──────────────────────────────────────────────────────────────────────────

def migrate_character_data(data: dict) -> dict:
    """对角色存档数据执行内容定义迁移（engine.migration.MigrationRegistry）。

    规则: ARC-001 规则集版本固定 — 数据字段增删改通过 MigrationPlan 声明，
          不硬编码。当前注册的默认计划用于角色结构字段的向后兼容。

    ★ review#12: fail-closed——迁移失败必须抛错（SaveMigrationError），
      绝不静默继续使用旧数据（对游戏存档静默回退比报错更危险）。
    """
    from ..engine.migration import (
        MigrationPlan,
        MigrationRegistry,
        MigrationStep,
    )
    registry = MigrationRegistry()
    registry.register_plan(MigrationPlan(
        from_revision="2024.1",
        to_revision="2024.2",
        content_id="character.save",
        steps=[
            MigrationStep(
                description="旧角色无 class_levels_json → 从 char_class 派生",
                field_path="class_levels",
                operation="set_default",
                new_value=None,
            ),
        ],
    ))
    save_rev = data.get("revision", "2024.1")
    if registry.needs_migration("character.save", save_rev, "2024.2"):
        # ★ review#12: 未知 revision（不在任何计划的 from_revision 中）
        #   → 显式报错，绝不静默按旧数据继续
        if registry.get_plan("character.save", save_rev) is None:
            from ..errors import SaveMigrationError
            raise SaveMigrationError(
                f"未知存档 revision={save_rev!r}，无法迁移（需人工处理）",
                operation="migrate_character_data")
        try:
            return registry.migrate("character.save", save_rev, data)
        except Exception as e:  # noqa: BLE001
            from ..errors import SaveMigrationError
            raise SaveMigrationError(
                f"角色存档迁移失败（revision={save_rev}）: {e}",
                operation="migrate_character_data") from e
    return data


def list_characters(campaign_id: int | None = None,
                    db_path: str | None = None) -> list[M.Character]:
    with session(db_path) as s:
        stmt = select(M.Character)
        if campaign_id is not None:
            stmt = stmt.where(M.Character.campaign_id == campaign_id)
        return list(s.exec(stmt))


def get_character_by_name(name: str, campaign_id: int | None = None,
                          db_path: str | None = None) -> M.Character | None:
    """按名字查找角色（用于战利品分配等按名字操作的场景）。

    campaign_id 为 None 时全局搜索（返回第一个匹配）。
    """
    with session(db_path) as s:
        stmt = select(M.Character).where(M.Character.name == name)
        if campaign_id is not None:
            stmt = stmt.where(M.Character.campaign_id == campaign_id)
        return s.exec(stmt).first()


def delete_character(cid: int, db_path: str | None = None) -> bool:
    db_path = db_path or DEFAULT_DB
    """删除角色卡。返回是否实际删除了一行（cid 不存在则 False）。

    用于房间加入失败时回滚刚创建的临时角色卡，避免脏数据残留。
    """
    with session(db_path) as s:
        ch = s.get(M.Character, cid)
        if ch is None:
            return False
        s.delete(ch)
        return True


def add_character_gold(cid: int, amount: int, db_path: str | None = None) -> int:
    db_path = db_path or DEFAULT_DB
    """为角色增加/扣除金币，返回更新后的余额。

    amount 可为负数（购买/消费时扣除）。
    """
    with session(db_path) as s:
        ch = s.get(M.Character, cid)
        if ch is None:
            raise KeyError(f"角色 {cid} 不存在")
        ch.gold = max(0, ch.gold + amount)
        s.add(ch)
        return ch.gold


def set_character_gold(cid: int, amount: int, db_path: str | None = None) -> int:
    db_path = db_path or DEFAULT_DB
    """直接设置角色金币数量，返回更新后的余额。"""
    with session(db_path) as s:
        ch = s.get(M.Character, cid)
        if ch is None:
            raise KeyError(f"角色 {cid} 不存在")
        ch.gold = max(0, amount)
        s.add(ch)
        return ch.gold


# ──────────────────────────────────────────────────────────────────────────
# 技能熟练
# ──────────────────────────────────────────────────────────────────────────

def set_character_skills(character_id: int, skills: list[str],
                         db_path: str | None = None) -> list[str]:
    """保存角色技能熟练列表，返回更新后的列表。"""
    import json as _json
    with session(db_path) as s:
        ch = s.get(M.Character, character_id)
        if ch is None:
            raise KeyError(f"角色 {character_id} 不存在")
        ch.skill_prof_json = _json.dumps(skills)
        s.add(ch)
        return ch.skill_proficiencies


def get_character_skills(character_id: int,
                         db_path: str | None = None) -> list[str]:
    """读取角色技能熟练列表。"""
    with session(db_path) as s:
        ch = s.get(M.Character, character_id)
        if ch is None:
            return []
        return ch.skill_proficiencies


# ──────────────────────────────────────────────────────────────────────────
# 专注状态
# ──────────────────────────────────────────────────────────────────────────

def set_concentration(character_id: int, spell_name: str, dc: int = 10,
                      db_path: str | None = None) -> dict:
    """设置角色专注状态（开始/结束专注）。返回当前专注信息。"""
    with session(db_path) as s:
        ch = s.get(M.Character, character_id)
        if ch is None:
            raise KeyError(f"角色 {character_id} 不存在")
        if spell_name:
            ch.start_concentration(spell_name, dc)
        else:
            ch.end_concentration()
        s.add(ch)
        return {"spell": ch.concentration_spell, "dc": ch.concentration_dc}


def get_concentration(character_id: int,
                      db_path: str | None = None) -> dict:
    """读取角色专注状态。"""
    with session(db_path) as s:
        ch = s.get(M.Character, character_id)
        if ch is None:
            return {"spell": "", "dc": 0}
        return {"spell": ch.concentration_spell, "dc": ch.concentration_dc}


# ──────────────────────────────────────────────────────────────────────────
# XP
# ──────────────────────────────────────────────────────────────────────────

def add_character_xp(character_id: int, amount: int,
                     db_path: str | None = None) -> int:
    """为角色增加 XP，返回更新后的总 XP。"""
    with session(db_path) as s:
        ch = s.get(M.Character, character_id)
        if ch is None:
            raise KeyError(f"角色 {character_id} 不存在")
        ch.xp = max(0, ch.xp + amount)
        s.add(ch)
        return ch.xp


def get_character_xp(character_id: int,
                     db_path: str | None = None) -> int:
    """读取角色当前 XP。"""
    with session(db_path) as s:
        ch = s.get(M.Character, character_id)
        if ch is None:
            return 0
        return ch.xp


# ──────────────────────────────────────────────────────────────────────────
# 战役 / rolling summary
# ──────────────────────────────────────────────────────────────────────────

def create_campaign(name: str, db_path: str | None = None) -> M.Campaign:
    db_path = db_path or DEFAULT_DB
    """创建战役，固定规则集标识（ARC-001）。

    从默认 ruleset_manifest.json 加载 ruleset_id / revision / content_packs，
    写入 Campaign，运行中只允许显式迁移。
    """
    from ..engine.ruleset_manifest import load_default_manifest
    manifest = load_default_manifest()
    c = M.Campaign(
        name=name,
        ruleset_id=manifest.ruleset_id,
        ruleset_revision=manifest.revision,
    )
    # 固定内容包版本
    pack_versions = {}
    for cp in manifest.content_packs:
        if isinstance(cp, dict):
            pack_versions[cp.get("name", "")] = cp.get("version", "1.0")
        else:
            pack_versions[str(cp)] = "1.0"
    c.set_content_pack_versions(pack_versions)
    with session(db_path) as s:
        s.add(c); s.commit(); s.refresh(c)
        return c


def save_campaign(c: M.Campaign, db_path: str | None = None,
                  expected_version: int | None = None) -> M.Campaign:
    """保存战役（★ P1-05: 乐观锁）。

    expected_version 提供时执行条件更新：
      UPDATE ... SET version = version + 1
      WHERE id = ? AND version = expected_version
    0 rows → 抛 StaleVersionError（调用方转 409）。
    expected_version=None 时向后兼容直接保存（旧调用方）。
    """
    if expected_version is None:
        with session(db_path) as s:
            s.add(c); s.commit(); s.refresh(c)
            return c
    from sqlalchemy import text
    eng = get_engine(db_path)
    with eng.begin() as conn:
        result = conn.execute(
            text("UPDATE campaign SET version = version + 1 "
                 "WHERE id = :cid AND version = :expected"),
            {"cid": c.id, "expected": int(expected_version)},
        )
        if result.rowcount == 0:
            raise StaleVersionError(
                f"战役 {c.id} 版本冲突：期望 {expected_version}")
        conn.execute(
            text("UPDATE campaign SET rolling_summary = :s, "
                 "world_flags_json = :w, setting = :st, tone = :t, "
                 "world_background = :wb, content_pack_versions_json = :cp "
                 "WHERE id = :cid"),
            {"s": c.rolling_summary, "w": c.world_flags_json,
             "st": c.setting, "t": c.tone, "wb": c.world_background,
             "cp": c.content_pack_versions_json, "cid": c.id},
        )
    return get_campaign(c.id, db_path)


class StaleVersionError(InvariantViolation):
    """P1-05: 乐观锁版本冲突（P2-05: 归类为状态不变量破坏 → 409）。"""


def get_campaign(campaign_id: int, db_path: str | None = None) -> M.Campaign | None:
    db_path = db_path or DEFAULT_DB
    with session(db_path) as s:
        return s.get(M.Campaign, campaign_id)


def list_campaigns(db_path: str | None = None) -> list[M.Campaign]:
    db_path = db_path or DEFAULT_DB
    """列出所有已保存战役（继续游戏用）。"""
    with session(db_path) as s:
        return list(s.exec(select(M.Campaign)))


def append_summary(campaign_id: int, text: str, db_path: str | None = None) -> str:
    db_path = db_path or DEFAULT_DB
    """追加剧情摘要到 rolling summary（P3 由 LLM 压缩旧剧情；P1 提供存储钩子）。

    规则: 数据模型 rolling_summary（防上下文爆炸）
    """
    with session(db_path) as s:
        c = s.get(M.Campaign, campaign_id)
        if c is None:
            raise KeyError(f"战役 {campaign_id} 不存在")
        prefix = c.rolling_summary + "\n" if c.rolling_summary else ""
        c.rolling_summary = prefix + text
        s.add(c)
        return c.rolling_summary


def get_summary(campaign_id: int, db_path: str | None = None) -> str:
    db_path = db_path or DEFAULT_DB
    c = get_campaign(campaign_id, db_path)
    return c.rolling_summary if c else ""


def set_campaign_setting(campaign_id: int, setting: str, tone: str = "",
                         db_path: str | None = None) -> M.Campaign | None:
    """设置战役世界背景/基调。"""
    with session(db_path) as s:
        c = s.get(M.Campaign, campaign_id)
        if c is None:
            raise KeyError(f"战役 {campaign_id} 不存在")
        c.setting = setting; c.tone = tone
        s.add(c)
        return c


def save_scene(scene: M.Scene, db_path: str | None = None) -> M.Scene:
    db_path = db_path or DEFAULT_DB
    """保存/更新当前场景。"""
    with session(db_path) as s:
        s.add(scene); s.commit(); s.refresh(scene)
        return scene


def get_scene(campaign_id: int, db_path: str | None = None) -> M.Scene | None:
    db_path = db_path or DEFAULT_DB
    """取战役当前场景（最新一条）。"""
    with session(db_path) as s:
        stmt = select(M.Scene).where(M.Scene.campaign_id == campaign_id)
        return s.exec(stmt).first()


# ──────────────────────────────────────────────────────────────────────────
# 战斗状态（engine.Combat ↔ CombatState 往返）
# ──────────────────────────────────────────────────────────────────────────

def _combatant_to_dict(c: cmb.Combatant) -> dict:
    """全字段导出 Combatant（D5 修复：之前手写字段清单丢 conditions/speed_remaining/
    group_id 等，导致状态条件跨行动全部丢失，违反 DMG「使用并跟进状态」）。"""
    d = {}
    for f in dataclasses.fields(cmb.Combatant):
        v = getattr(c, f.name)
        if f.name == "conditions":
            v = v.to_dict()
        elif f.name == "position":
            v = list(v)
        d[f.name] = v
    return d


def _dict_to_combatant(d: dict) -> cmb.Combatant:
    """从 dict 恢复 Combatant。未知字段忽略、缺失字段用 dataclass 默认值，
    保证旧存档（仅含旧字段清单）可加载。"""
    valid = {f.name for f in dataclasses.fields(cmb.Combatant)}
    kw = {k: v for k, v in d.items() if k in valid}
    if "conditions" in kw:
        kw["conditions"] = (cond.ConditionState.from_dict(kw["conditions"])
                            if isinstance(kw["conditions"], dict)
                            else cond.ConditionState())
    if "position" in kw and isinstance(kw["position"], list):
        kw["position"] = tuple(kw["position"])
    return cmb.Combatant(**kw)


def save_combat(campaign_id: int, combat: cmb.Combat,
               db_path: str | None = None) -> M.CombatState:
    """把 engine.Combat 序列化为 CombatState 行（覆盖该战役的战斗行）。

    participants_json 升级为包裹格式 {"combatants": [...], "seconds_elapsed": n}，
    免加列迁移即可持久化 seconds_elapsed；load 兼容旧 list 格式。
    """
    order = [_combatant_to_dict(c) for c in combat.initiative_order]
    parts = [_combatant_to_dict(c) for c in combat.participants]
    with session(db_path) as s:
        existing = s.exec(select(M.CombatState).where(M.CombatState.campaign_id == campaign_id)).first()
        cs = existing or M.CombatState(campaign_id=campaign_id)
        cs.set_initiative_order(order)
        cs.participants_json = json.dumps(
            {"combatants": parts, "seconds_elapsed": combat.seconds_elapsed})
        cs.round = combat.round
        cs.current_index = combat.current_index
        cs.active = combat.active
        # ★ API-001: 乐观锁版本号递增
        cs.version = combat.version
        s.add(cs); s.commit(); s.refresh(cs)
        return cs


def load_combat(campaign_id: int, db_path: str | None = None) -> cmb.Combat:
    db_path = db_path or DEFAULT_DB
    """从 CombatState 行重建 engine.Combat。

    participants 与 initiative_order 按 cid 共享同一批对象（D5 修复：
    之前反序列化为两组独立对象，上层被迫双列表同步，漏写即不一致）。
    """
    with session(db_path) as s:
        cs = s.exec(select(M.CombatState).where(M.CombatState.campaign_id == campaign_id)).first()
        if cs is None:
            raise KeyError(f"战役 {campaign_id} 无战斗状态")
        combat = cmb.Combat()
        raw = json.loads(cs.participants_json)
        if isinstance(raw, dict):                       # 新包裹格式
            parts_raw = raw.get("combatants", [])
            combat.seconds_elapsed = int(raw.get("seconds_elapsed", 0))
        else:                                            # 旧 list 格式
            parts_raw = raw
        combat.initiative_order = [_dict_to_combatant(d) for d in cs.initiative_order]
        by_cid = {c.cid: c for c in combat.initiative_order}
        combat.participants = [by_cid.get(d.get("cid"), None) or _dict_to_combatant(d)
                               for d in parts_raw]
        combat.round = cs.round
        combat.current_index = cs.current_index
        combat.active = cs.active
        combat.version = getattr(cs, "version", 0)  # ★ API-001: 乐观锁版本
        return combat


# ──────────────────────────────────────────────────────────────────────────
# 日志
# ──────────────────────────────────────────────────────────────────────────

def append_log(campaign_id: int, *, player_input: str = "", dm_output: str = "",
               dice_rolls: list = None, state_changes: list = None, rag_refs: list = None,
               db_path: str | None = None) -> M.Log:
    log = M.Log(
        campaign_id=campaign_id, player_input=player_input, dm_output=dm_output,
        dice_rolls_json=json.dumps(dice_rolls or []),
        state_changes_json=json.dumps(state_changes or []),
        rag_refs_json=json.dumps(rag_refs or []),
    )
    with session(db_path) as s:
        s.add(log); s.commit(); s.refresh(log)
        return log


def get_recent_logs(campaign_id: int, n: int = 6,
                    db_path: str | None = None) -> list[M.Log]:
    """获取最近 n 条跑团日志（工作记忆数据源）。

    按时间正序返回（最旧的在前），用于注入 narrate prompt。
    规则: 三层记忆系统 — 工作记忆层（最近 N 回合对话原文）
    """
    with session(db_path) as s:
        stmt = (select(M.Log)
                .where(M.Log.campaign_id == campaign_id)
                .order_by(M.Log.id.desc())
                .limit(n))
        logs = list(s.exec(stmt))
        return list(reversed(logs))  # 时间正序


def count_logs(campaign_id: int, db_path: str | None = None) -> int:
    db_path = db_path or DEFAULT_DB
    """统计战役的日志总数（回合数，摘要折叠周期触发用）。"""
    from sqlalchemy import func
    with session(db_path) as s:
        stmt = (select(func.count())
                .select_from(M.Log)
                .where(M.Log.campaign_id == campaign_id))
        return int(s.exec(stmt).one())


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    db = f"sqlite:///{db_path}"
    try:
        # 战役
        camp = create_campaign("测试战役", db)
        assert camp.id is not None
        # 角色卡（5级战士，板甲，力16→调整+3，熟练+3）
        ch = M.Character(name="阿拉贡", race="人类", char_class="战士", level=5,
                         campaign_id=camp.id)
        ch.set_abilities({"str": 16, "dex": 10, "con": 15, "int": 10, "wis": 12, "cha": 10})
        ch.hp_max = 38; ch.hp_current = 38; ch.ac = 18; ch.speed = 30
        ch = save_character(ch, db)
        cid = ch.id
        # 重载验证
        loaded = get_character(cid, db)
        assert loaded.name == "阿拉贡" and loaded.ability_mod("str") == 3   # R-CHK-024
        assert loaded.prof() == 3                                          # R-CHK-015 5级
        assert loaded.ac == 18
        # rolling summary
        append_summary(camp.id, "队伍进入了幽暗地域", db)
        append_summary(camp.id, "击败了第一批哥布林", db)
        s = get_summary(camp.id, db)
        assert "幽暗地域" in s and "哥布林" in s
        # 战斗状态往返
        from ..engine import combat as C
        cs = [C.Combatant(cid="a", name="阿拉贡", dex_mod=3, side="player"),
              C.Combatant(cid="g1", name="哥布林", dex_mod=2, side="enemy", is_player=False)]
        combat = C.Combat()
        # 用固定先攻避免随机
        for c in cs:
            c.initiative = 15 + c.dex_mod
        combat.participants = cs
        combat.initiative_order = sorted(cs, key=lambda c: c.initiative, reverse=True)
        combat.round = 2; combat.current_index = 1; combat.active = True
        save_combat(camp.id, combat, db)
        re = load_combat(camp.id, db)
        assert re.round == 2 and re.current_index == 1 and re.active
        assert re.initiative_order[0].initiative >= re.initiative_order[1].initiative
        assert re.initiative_order[0].name == "阿拉贡"  # 18 > 17
        # 日志
        lg = append_log(camp.id, player_input="我攻击哥布林", dm_output="命中",
                        dice_rolls=[{"d20": 15}], db_path=db)
        assert lg.id is not None
        print("[store] 自检通过 ✓")
    finally:
        eng = _engines.pop(db, None)
        if eng is not None:
            eng.dispose()
        with suppress(PermissionError):
            os.unlink(db_path)


if __name__ == "__main__":
    _self_test()
