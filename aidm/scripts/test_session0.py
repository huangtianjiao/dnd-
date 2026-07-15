"""Phase A 自检测试 — 验证 Session 0 配置逻辑。

运行: PYTHONPATH=src python scripts/test_session0.py
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aidm.brain.session0 import (
    Session0Config,
    default_session0,
    validate_session0,
    is_valid_config,
    TONES,
    RULE_VERSIONS,
    ADVANCEMENT_MODES,
    RESURRECTION_ACCESS,
)


def test_default_config():
    """默认配置合法且字段正确。"""
    cfg = default_session0()
    assert cfg.tone == "高魔奇幻"
    assert cfg.seriousness == 5
    assert cfg.rule_version == "2024 修订版"
    assert cfg.advancement_mode == "经验值"
    assert cfg.resurrection_access == "困难获取"
    assert cfg.party_size_min == 4   # R-DM-046
    assert cfg.party_size_max == 6   # R-DM-046
    assert cfg.lines == []
    assert cfg.veils == []
    assert cfg.safewords == ["暂停"]
    assert is_valid_config(cfg), "默认配置应通过校验"
    print("[PASS] test_default_config")


def test_all_tones_valid():
    """所有预设基调均合法。"""
    for tone in TONES:
        cfg = Session0Config(tone=tone)
        errs = validate_session0(cfg)
        assert not errs, f"基调 {tone} 应合法，得到错误: {errs}"
    print("[PASS] test_all_tones_valid")


def test_invalid_tone():
    """非法基调被拒绝。"""
    cfg = Session0Config(tone="不存在基调")
    errs = validate_session0(cfg)
    assert any("tone" in e for e in errs), f"应报告 tone 错误，得到: {errs}"
    assert not is_valid_config(cfg)
    print("[PASS] test_invalid_tone")


def test_seriousness_bounds():
    """严肃度边界 1 和 10 合法，0 和 11 非法。"""
    for s in (1, 10):
        cfg = Session0Config(seriousness=s)
        assert is_valid_config(cfg), f"seriousness={s} 应合法"
    for s in (0, 11):
        cfg = Session0Config(seriousness=s)
        assert not is_valid_config(cfg), f"seriousness={s} 应非法"
    print("[PASS] test_seriousness_bounds")


def test_seriousness_type():
    """非整数严肃度被拒绝。"""
    cfg = Session0Config(seriousness=5.5)  # type: ignore[arg-type]
    errs = validate_session0(cfg)
    # 5.5 不在 1-10 整数范围 -> 报错
    assert errs, "非整数 seriousness 应报错"
    print("[PASS] test_seriousness_type")


def test_rule_versions():
    """规则版本枚举校验。"""
    for rv in RULE_VERSIONS:
        cfg = Session0Config(rule_version=rv)
        assert is_valid_config(cfg), f"rule_version={rv} 应合法"
    cfg = Session0Config(rule_version="3.5版")
    assert not is_valid_config(cfg)
    print("[PASS] test_rule_versions")


def test_advancement_modes():
    """升级方式枚举校验。"""
    for am in ADVANCEMENT_MODES:
        cfg = Session0Config(advancement_mode=am)
        assert is_valid_config(cfg), f"advancement_mode={am} 应合法"
    cfg = Session0Config(advancement_mode="随机升级")
    assert not is_valid_config(cfg)
    print("[PASS] test_advancement_modes")


def test_resurrection_access():
    """复活魔法获取难度枚举校验。"""
    for ra in RESURRECTION_ACCESS:
        cfg = Session0Config(resurrection_access=ra)
        assert is_valid_config(cfg), f"resurrection_access={ra} 应合法"
    cfg = Session0Config(resurrection_access="随便复活")
    assert not is_valid_config(cfg)
    print("[PASS] test_resurrection_access")


def test_party_size():
    """团队规模范围校验 (R-DM-046)。"""
    # 合法范围
    cfg = Session0Config(party_size_min=2, party_size_max=8)
    assert is_valid_config(cfg)
    # min > max 非法
    cfg = Session0Config(party_size_min=6, party_size_max=4)
    errs = validate_session0(cfg)
    assert any("party_size_min" in e for e in errs), f"应报告 min>max，得到: {errs}"
    # min < 1 非法
    cfg = Session0Config(party_size_min=0, party_size_max=6)
    assert not is_valid_config(cfg)
    print("[PASS] test_party_size")


def test_lines_veils_safewords():
    """Lines / Veils / Safewords 列表校验。"""
    # 正常列表
    cfg = Session0Config(
        lines=["自残", "酷刑描写"],
        veils=["宗教隐喻"],
        safewords=["暂停", "X卡"],
    )
    assert is_valid_config(cfg)

    # 非字符串元素
    cfg = Session0Config(lines=["ok", 123])  # type: ignore[list-item]
    errs = validate_session0(cfg)
    assert any("lines[1]" in e for e in errs), f"应报告 lines 类型错误，得到: {errs}"

    # 非列表类型
    cfg = Session0Config(veils="不是列表")  # type: ignore[arg-type]
    errs = validate_session0(cfg)
    assert any("veils" in e for e in errs), f"应报告 veils 类型错误，得到: {errs}"
    print("[PASS] test_lines_veils_safewords")


def test_full_session0_scenario():
    """完整 Session 0 场景：黑暗写实 + 里程碑 + 困难复活。"""
    cfg = Session0Config(
        tone="黑暗写实",
        seriousness=9,
        lines=["儿童受害详细描写", "性侵内容"],
        veils=["药物成瘾", "精神崩溃"],
        rule_version="2024 修订版",
        advancement_mode="里程碑",
        resurrection_access="困难获取",
        safewords=["暂停", "安全"],
        party_size_min=4,
        party_size_max=5,
    )
    errs = validate_session0(cfg)
    assert not errs, f"完整场景配置应合法，得到错误: {errs}"
    print("[PASS] test_full_session0_scenario")


def test_multiple_errors():
    """多个错误同时存在时全部报告。"""
    cfg = Session0Config(
        tone="错误基调",
        seriousness=0,
        rule_version="错误版本",
        advancement_mode="错误方式",
        resurrection_access="错误难度",
        party_size_min=5,
        party_size_max=4,
    )
    errs = validate_session0(cfg)
    # tone / seriousness / rule_version / advancement_mode /
    # resurrection_access / party_size min>max => 6 errors
    assert len(errs) >= 6, f"应报告至少6个错误，得到 {len(errs)}: {errs}"
    print(f"[PASS] test_multiple_errors ({len(errs)} errors reported)")


if __name__ == "__main__":
    test_default_config()
    test_all_tones_valid()
    test_invalid_tone()
    test_seriousness_bounds()
    test_seriousness_type()
    test_rule_versions()
    test_advancement_modes()
    test_resurrection_access()
    test_party_size()
    test_lines_veils_safewords()
    test_full_session0_scenario()
    test_multiple_errors()
    print("\n=== All Session 0 tests passed ===")
