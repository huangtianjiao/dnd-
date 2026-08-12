"""P1-08 信任验证门禁 — 运行规则标记测试并生成 CI 结果。

CoverageManifest 的 VERIFIED 不再由「源码 import 扫描」单独决定：
  1. 运行 `pytest tests/ -m "rule" --junitxml=...`（仅执行带 @pytest.mark.rule 的测试）
  2. 解析 junit 结果 → {rule_id: {passed, tests: [...]}}
  3. 生成 docs/coverage_ci.json
  4. CoverageManifest.load_ci_results(json) → 仅对 CI 确认通过的模块授 VERIFIED

用法:
  python scripts/run_cov_gate.py            # 全量运行 + 生成 + 校验
  python scripts/run_cov_gate.py --collect  # 只统计 rule 标记覆盖（不执行）
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

AIDM = Path(__file__).resolve().parents[1]
TESTS = AIDM / "tests"
OUT_JSON = AIDM / "docs" / "coverage_ci.json"

# 非 rule 标记测试（-m "rule" 时排除）
NOT_RULE = "-m", "rule"


def collect_rule_tests() -> dict[str, list[str]]:
    """收集带 @pytest.mark.rule 的测试节点（--co 只收集不执行）。"""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(TESTS), "--co", "-q", "-m", "rule",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=AIDM,
    )
    mapping: dict[str, list[str]] = {}
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or "::" not in line:
            continue
        node = line.split()[0] if line.split() else ""
        if not node.endswith(".py"):
            continue
        # 从测试文件源码解析该测试的 rule 标记
        _map_from_node(node, mapping)
    return mapping


def _map_from_node(node_id: str, mapping: dict[str, list[str]]) -> None:
    """node_id → 测试文件 → 解析文件内规则标记 → 填充映射。"""
    import re
    parts = node_id.split("::")
    fname = parts[0]
    path = TESTS / fname
    if not path.exists():
        return
    src = path.read_text(encoding="utf-8", errors="replace")
    rules = re.findall(r'@pytest\.mark\.rule\(\s*["\']((?:engine\.)?[a-z_0-9.]+)["\']\s*\)', src)
    for rid in rules:
        mapping.setdefault(rid, []).append(node_id)


def run_and_generate() -> dict[str, dict]:
    """运行 rule 标记测试，解析 junit 生成 CI 结果。"""
    fd, junit = tempfile.mkstemp(suffix=".xml")
    os.close(fd)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(TESTS), "-m", "rule", "-q",
             "--junitxml=" + junit, "-p", "no:cacheprovider"],
            capture_output=True, text=True, cwd=AIDM,
        )
    finally:
        pass
    passed_tests: set[str] = set()
    failed_tests: set[str] = set()
    tree = ET.parse(junit)
    for tc in tree.iter("testcase"):
        name = tc.get("name", "")
        classname = tc.get("classname", "")
        # classname 形如 tests.test_wiring_finalstate_wave2.TestTravelWiring
        parts = classname.split(".") if classname else []
        if len(parts) >= 2 and parts[0] == "tests":
            base = parts[1]
        elif parts:
            base = parts[0]
        else:
            base = ""
        node = f"{base}::{name}" if base else name
        if tc.find("failure") is not None or tc.find("error") is not None:
            failed_tests.add(node)
        else:
            passed_tests.add(node)

    # 收集 rule 映射（源码静态解析，与 CoverageManifest 同口径）
    import re
    mapping: dict[str, list[str]] = {}
    for f in sorted(os.listdir(TESTS)):
        if not f.startswith("test_") or not f.endswith(".py"):
            continue
        src = (TESTS / f).read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(
                r'@pytest\.mark\.rule\(\s*["\']((?:engine\.)?[a-z_0-9.]+)["\']\s*\)',
                src):
            mapping.setdefault(m.group(1), []).append(f)

    ci: dict[str, dict] = {}
    for rid, files in mapping.items():
        # 该规则对应的测试节点（按 classname 文件前缀匹配）
        nodes = [n for n in passed_tests | failed_tests
                 if any(n.split("::")[0] == f.replace(".py", "") or
                        n.startswith(f.replace(".py", "") + "::")
                        for f in files)]
        ok = bool(nodes) and all(n in passed_tests for n in nodes)
        ci[rid] = {"passed": ok, "tests": sorted(nodes)}

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(ci, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    return ci


def main() -> int:
    """入口：生成 CI 结果并断言门禁。"""
    if "--collect" in sys.argv:
        mapping = collect_rule_tests()
        print(f"rule 标记规则数: {len(mapping)}")
        for rid in sorted(mapping):
            print(f"  {rid}: {len(mapping[rid])} 测试")
        return 0

    ci = run_and_generate()
    passed = sum(1 for v in ci.values() if v["passed"])
    print(f"CI 结果: {passed}/{len(ci)} 规则通过 → {OUT_JSON}")
    engine_passed = sum(1 for k, v in ci.items()
                        if k.startswith("engine.") and v["passed"])
    print(f"engine 模块 CI 通过: {engine_passed}")

    # 门禁：至少 20 个 engine 模块有 CI 确认的显式测试
    if engine_passed < 20:
        print("✗ 门禁失败: engine 模块 CI 确认 < 20")
        return 1
    print("✓ P1-08 门禁通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())