"""状态层存储 — SQLite 持久化 / CRUD / rolling summary / 战斗状态序列化。

存档即拷一个 SQLite 文件。提供 Character/Campaign/Scene/CombatState/Log 的增删查，
以及战役 rolling summary 追加（防上下文失忆）与 engine.Combat 的存/取往返。

规则依据见 RULE_SPEC.md §6 数据模型。
"""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from typing import Optional

from sqlmodel import Session, select

from . import models as M
from ..engine import combat as cmb


# ──────────────────────────────────────────────────────────────────────────
# 引擎与会话
# ──────────────────────────────────────────────────────────────────────────

DEFAULT_DB = "sqlite:///D:/game/dnd/aidm/data/saves/save.db"


def _migrate(engine) -> None:
    """自动迁移：给已存在表补缺失列（SQLite ALTER TABLE ADD COLUMN）。

    解决旧库缺 setting/atmosphere/situation/exits 等新列的问题。
    """
    from sqlalchemy import inspect, text
    insp = inspect(engine)
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
                    if "INT" in tn:
                        dv = " DEFAULT 0"
                    elif "BOOL" in tn:
                        dv = " DEFAULT 0"
                    else:  # TEXT/VARCHAR/JSON
                        dv = " DEFAULT ''"
                try:
                    conn.execute(text(f'ALTER TABLE "{tbl}" ADD COLUMN "{col.name}" {coltype}{dv}'))
                except Exception:
                    pass


_engines: dict[str, object] = {}


def get_engine(db_path: str = DEFAULT_DB):
    if db_path not in _engines:
        # 自动建父目录（绝对路径）
        if db_path.startswith("sqlite:///") and ":memory:" not in db_path:
            p = db_path.replace("sqlite:///", "", 1)
            d = os.path.dirname(p)
            if d:
                os.makedirs(d, exist_ok=True)
        _engines[db_path] = M.get_engine(db_path)
        M.SQLModel.metadata.create_all(_engines[db_path])
        _migrate(_engines[db_path])   # 老库补列
    return _engines[db_path]


@contextmanager
def session(db_path: str = DEFAULT_DB):
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

def save_character(ch: M.Character, db_path: str = DEFAULT_DB) -> M.Character:
    with session(db_path) as s:
        s.add(ch)
        s.commit()
        s.refresh(ch)
        return ch


def get_character(cid: int, db_path: str = DEFAULT_DB) -> Optional[M.Character]:
    with session(db_path) as s:
        return s.get(M.Character, cid)


def list_characters(campaign_id: Optional[int] = None,
                    db_path: str = DEFAULT_DB) -> list[M.Character]:
    with session(db_path) as s:
        stmt = select(M.Character)
        if campaign_id is not None:
            stmt = stmt.where(M.Character.campaign_id == campaign_id)
        return list(s.exec(stmt))


# ──────────────────────────────────────────────────────────────────────────
# 战役 / rolling summary
# ──────────────────────────────────────────────────────────────────────────

def create_campaign(name: str, db_path: str = DEFAULT_DB) -> M.Campaign:
    c = M.Campaign(name=name)
    with session(db_path) as s:
        s.add(c); s.commit(); s.refresh(c)
        return c


def save_campaign(c: M.Campaign, db_path: str = DEFAULT_DB) -> M.Campaign:
    with session(db_path) as s:
        s.add(c); s.commit(); s.refresh(c)
        return c


def get_campaign(campaign_id: int, db_path: str = DEFAULT_DB) -> Optional[M.Campaign]:
    with session(db_path) as s:
        return s.get(M.Campaign, campaign_id)


def list_campaigns(db_path: str = DEFAULT_DB) -> list[M.Campaign]:
    """列出所有已保存战役（继续游戏用）。"""
    with session(db_path) as s:
        return list(s.exec(select(M.Campaign)))


def append_summary(campaign_id: int, text: str, db_path: str = DEFAULT_DB) -> str:
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


def get_summary(campaign_id: int, db_path: str = DEFAULT_DB) -> str:
    c = get_campaign(campaign_id, db_path)
    return c.rolling_summary if c else ""


def set_campaign_setting(campaign_id: int, setting: str, tone: str = "",
                         db_path: str = DEFAULT_DB) -> Optional[M.Campaign]:
    """设置战役世界背景/基调。"""
    with session(db_path) as s:
        c = s.get(M.Campaign, campaign_id)
        if c is None:
            raise KeyError(f"战役 {campaign_id} 不存在")
        c.setting = setting; c.tone = tone
        s.add(c)
        return c


def save_scene(scene: M.Scene, db_path: str = DEFAULT_DB) -> M.Scene:
    """保存/更新当前场景。"""
    with session(db_path) as s:
        s.add(scene); s.commit(); s.refresh(scene)
        return scene


def get_scene(campaign_id: int, db_path: str = DEFAULT_DB) -> Optional[M.Scene]:
    """取战役当前场景（最新一条）。"""
    with session(db_path) as s:
        stmt = select(M.Scene).where(M.Scene.campaign_id == campaign_id)
        return s.exec(stmt).first()


# ──────────────────────────────────────────────────────────────────────────
# 战斗状态（engine.Combat ↔ CombatState 往返）
# ──────────────────────────────────────────────────────────────────────────

def _combatant_to_dict(c: cmb.Combatant) -> dict:
    return {
        "cid": c.cid, "name": c.name, "dex_mod": c.dex_mod,
        "initiative": c.initiative, "side": c.side, "is_player": c.is_player,
        "surprised": c.surprised, "action_used": c.action_used,
        "bonus_action_used": c.bonus_action_used, "reaction_used": c.reaction_used,
        "free_interaction_used": c.free_interaction_used,
        "concentrating_on": c.concentrating_on,
    }


def _dict_to_combatant(d: dict) -> cmb.Combatant:
    return cmb.Combatant(**d)


def save_combat(campaign_id: int, combat: cmb.Combat,
               db_path: str = DEFAULT_DB) -> M.CombatState:
    """把 engine.Combat 序列化为 CombatState 行（覆盖该战役的战斗行）。"""
    order = [_combatant_to_dict(c) for c in combat.initiative_order]
    parts = [_combatant_to_dict(c) for c in combat.participants]
    with session(db_path) as s:
        existing = s.exec(select(M.CombatState).where(M.CombatState.campaign_id == campaign_id)).first()
        cs = existing or M.CombatState(campaign_id=campaign_id)
        cs.set_initiative_order(order)
        cs.participants_json = json.dumps(parts)
        cs.round = combat.round
        cs.current_index = combat.current_index
        cs.active = combat.active
        s.add(cs); s.commit(); s.refresh(cs)
        return cs


def load_combat(campaign_id: int, db_path: str = DEFAULT_DB) -> cmb.Combat:
    """从 CombatState 行重建 engine.Combat。"""
    with session(db_path) as s:
        cs = s.exec(select(M.CombatState).where(M.CombatState.campaign_id == campaign_id)).first()
        if cs is None:
            raise KeyError(f"战役 {campaign_id} 无战斗状态")
        combat = cmb.Combat()
        combat.participants = [_dict_to_combatant(d) for d in json.loads(cs.participants_json)]
        combat.initiative_order = [_dict_to_combatant(d) for d in cs.initiative_order]
        combat.round = cs.round
        combat.current_index = cs.current_index
        combat.active = cs.active
        return combat


# ──────────────────────────────────────────────────────────────────────────
# 日志
# ──────────────────────────────────────────────────────────────────────────

def append_log(campaign_id: int, *, player_input: str = "", dm_output: str = "",
               dice_rolls: list = None, state_changes: list = None, rag_refs: list = None,
               db_path: str = DEFAULT_DB) -> M.Log:
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
                    db_path: str = DEFAULT_DB) -> list[M.Log]:
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


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    import tempfile
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = f"sqlite:///{tmp.name}"
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
        try:
            os.unlink(tmp.name)
        except PermissionError:
            pass


if __name__ == "__main__":
    _self_test()
