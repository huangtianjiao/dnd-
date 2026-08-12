"""滚动摘要触发机制回归测试 — 三层记忆系统的中期摘要层。

验证:
  1. 空 summary 在第 N 回合能触发首次周期折叠（冷启动死锁修复）
  2. 未到折叠周期时不触发
  3. summary 超限时浓缩自身（替换而非追加）
  4. LLM 输出异常（未变短）时不覆盖原摘要
  5. store.count_logs 正确统计战役日志数

运行:
  pytest tests/test_memory_summary.py
"""

from __future__ import annotations

import os
import sys

# 确保 src 在路径中
from aidm.brain import memory
from aidm.stats import store


def _make_campaign_with_logs(n_logs: int) -> int:
    """创建测试战役并写入 n 条日志，返回 campaign_id。"""
    camp = store.create_campaign(f"摘要测试_{n_logs}回合")
    for i in range(n_logs):
        store.append_log(camp.id,
                         player_input=f"玩家第{i + 1}回合行动",
                         dm_output=f"DM第{i + 1}回合叙事")
    return camp.id


def test_count_logs():
    """count_logs 应正确统计战役日志数，且不串战役。"""
    print("\n[Test 1] count_logs 统计...")
    cid = _make_campaign_with_logs(7)
    other = _make_campaign_with_logs(3)

    assert store.count_logs(cid) == 7, "应统计到 7 条日志"
    assert store.count_logs(other) == 3, "不应串到其他战役"
    print("  ✓ count_logs 正确")


def test_fold_triggers_on_empty_summary(monkeypatch):
    """空 summary 在第 N 回合应触发首次折叠（冷启动死锁回归）。"""
    print("\n[Test 2] 空 summary 冷启动折叠...")
    cid = _make_campaign_with_logs(memory.COMPRESS_EVERY_N_TURNS)
    assert store.get_summary(cid) == "", "前提：summary 为空"
    assert memory._should_fold(cid), "第 N 回合应到达折叠点"

    # mock 掉所有 LLM/Qdrant 依赖
    monkeypatch.setattr(memory, "extract_observations",
                        lambda *a, **k: [])
    monkeypatch.setattr(memory, "compress_rolling_summary",
                        lambda *a, **k: "冒险者进入矿道，发现哥布林踪迹。")
    monkeypatch.setattr(memory, "cleanup_memories", lambda *a, **k: None)

    result = memory.process_turn_memories(
        campaign_id=cid, player_input="测试", narration="测试叙事",
        intent={}, turn=memory.COMPRESS_EVERY_N_TURNS)

    assert result["summary_compressed"], "应完成首次折叠"
    assert "哥布林" in store.get_summary(cid), "summary 应写入折叠内容"
    print("  ✓ 空 summary 第 N 回合成功启动折叠")


def test_fold_not_triggered_mid_cycle(monkeypatch):
    """未到折叠周期（N-1 条日志）时不应触发。"""
    print("\n[Test 3] 周期中途不折叠...")
    cid = _make_campaign_with_logs(memory.COMPRESS_EVERY_N_TURNS - 1)
    assert not memory._should_fold(cid), "N-1 回合不应触发折叠"

    monkeypatch.setattr(memory, "extract_observations",
                        lambda *a, **k: [])
    monkeypatch.setattr(memory, "cleanup_memories", lambda *a, **k: None)

    result = memory.process_turn_memories(
        campaign_id=cid, player_input="测试", narration="测试叙事",
        intent={}, turn=1)

    assert not result["summary_compressed"], "周期中途不应折叠"
    assert store.get_summary(cid) == "", "summary 应保持为空"
    print("  ✓ 周期中途不触发")


def test_condense_replaces_long_summary(monkeypatch):
    """summary 超限时应浓缩自身（替换），而非继续追加。"""
    print("\n[Test 4] 超限浓缩替换...")
    cid = _make_campaign_with_logs(1)
    # 构造超过阈值的长摘要（threshold = 128000*0.15 tokens ≈ 12800 字符）
    camp = store.get_campaign(cid)
    camp.rolling_summary = "冗长的战役记录。" * 2000  # 16000 字符
    store.save_campaign(camp)
    assert memory._should_condense(cid), "超长 summary 应触发浓缩"

    monkeypatch.setattr(memory.llm, "chat",
                        lambda *a, **k: "浓缩后的主线摘要。")
    ok = memory._condense_summary(cid)

    assert ok, "浓缩应成功"
    assert store.get_summary(cid) == "浓缩后的主线摘要。", "应替换而非追加"
    assert not memory._should_condense(cid), "浓缩后不应再触发"
    print("  ✓ 超限浓缩替换成功")


def test_condense_keeps_original_on_bad_llm_output(monkeypatch):
    """LLM 输出异常（未变短/为空）时不覆盖原摘要。"""
    print("\n[Test 5] 异常输出保护...")
    cid = _make_campaign_with_logs(1)
    original = "重要摘要内容。" * 10
    camp = store.get_campaign(cid)
    camp.rolling_summary = original
    store.save_campaign(camp)

    # LLM 返回比原文更长的输出 → 不应覆盖
    monkeypatch.setattr(memory.llm, "chat",
                        lambda *a, **k: "异常膨胀输出！" * 100)
    assert not memory._condense_summary(cid), "未变短应返回 False"
    assert store.get_summary(cid) == original, "原摘要应保留"

    # LLM 返回空 → 不应覆盖
    monkeypatch.setattr(memory.llm, "chat", lambda *a, **k: "")
    assert not memory._condense_summary(cid), "空输出应返回 False"
    assert store.get_summary(cid) == original, "原摘要应保留"
    print("  ✓ 异常输出不覆盖原摘要")
