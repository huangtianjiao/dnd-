"""CoverageManifest 生成器 — 内容覆盖度追踪。

扫描 engine/data/tests 模块，自动生成内容覆盖度清单。
用于度量规则内容的实现完整度。

规则依据: TEST-002 CoverageManifest 生成器
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class CoverageStatus(str, Enum):
    """内容覆盖度状态。"""

    MISSING = "MISSING"          # 完全缺失
    DATA_ONLY = "DATA_ONLY"      # 仅有数据，无处理逻辑
    PARTIAL = "PARTIAL"          # 部分实现
    WIRED = "WIRED"              # 已接入引擎
    FULL = "FULL"                # 完整实现
    VERIFIED = "VERIFIED"        # 已验证（有测试覆盖）


def _find_engine_imports(source: str) -> list[str]:
    """从源码文本中提取引用的 engine 子模块名。

    支持:
      - `from ..engine import combat as cmb` / `from .engine import X`
      - `from aidm.engine import X`
      - `from ...engine.spell_sources import Y` / `from aidm.engine.spellcasting import Z`
    """
    import re
    modules: list[str] = []

    # 形式: from <...engine> import a, b
    for m in re.finditer(r"from\s+([\w.]+\.engine)\s+import\s+([^\n]+)", source):
        # 提取具体的引擎子模块（a.engine.x 形式）
        path = m.group(1)
        tail = path.split(".")[-1] if path.endswith("engine") else ""
        names = [n.strip().split(" ")[0] for n in m.group(2).split(",") if n.strip()]
        # 若 import 的是具体子模块对象（如 cast_spell），尝试匹配引擎模块名
        if tail and tail != "engine":
            modules.append(tail)
        for name in names:
            if name in _ENGINE_SUBMODULES:
                modules.append(name)

    # 形式: from <...engine.>module import ...
    for m in re.finditer(r"from\s+[\w.]+\.engine\.([a-z_]+)\s+import", source):
        if m.group(1) in _ENGINE_SUBMODULES:
            modules.append(m.group(1))

    # 形式: import aidm.engine.X 或 import ...engine.X
    for m in re.finditer(r"import\s+[\w.]+\.engine\.([a-z_]+)\b", source):
        if m.group(1) in _ENGINE_SUBMODULES:
            modules.append(m.group(1))

    # 去重
    return list(dict.fromkeys(modules))


# 已知引擎子模块名（用于 import 解析）— 动态扫描 engine/ 目录获得
def _load_engine_submodules() -> frozenset[str]:
    """扫描 engine/ 目录得到全部子模块名。"""
    engine_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "engine")
    mods = set()
    if os.path.isdir(engine_dir):
        for f in os.listdir(engine_dir):
            if f.endswith(".py") and not f.startswith("_"):
                mods.add(f[:-3])
    return frozenset(mods)


_ENGINE_SUBMODULES = _load_engine_submodules()
_ENGINE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "engine")


def _parse_parenthesized_names(text: str) -> list[str]:
    """解析 `import (a, b, c)` 形式的名字列表（支持跨行）。"""
    import re
    flat = re.sub(r"[\n()]", " ", text)
    return [n.strip().split(" ")[0].rstrip(",") for n in flat.split(",") if n.strip()]


def _engine_internal_imports(source: str) -> set[str]:
    """提取 engine 模块内部对同级子模块的相对引用（`.foo` / `from . import foo`）。"""
    import re
    deps: set[str] = set()
    for m in re.finditer(r"from\s+\.([a-z_][a-z0-9_]*)\s+import", source):
        if m.group(1) in _ENGINE_SUBMODULES:
            deps.add(m.group(1))
    for m in re.finditer(r"from\s+\.\s+import\s+\(?\s*([^\n]+?)\)?\s*\n", source, re.S):
        for n in _parse_parenthesized_names(m.group(1)):
            if n in _ENGINE_SUBMODULES:
                deps.add(n)
    for m in re.finditer(r"(?:import|from)\s+\.([a-z_][a-z0-9_]*)\b", source):
        if m.group(1) in _ENGINE_SUBMODULES:
            deps.add(m.group(1))
    return deps


def _reexport_symbol_map() -> dict[str, str]:
    """解析 engine/__init__.py 的 `from .X import Y` 重导出 → {symbol: module}。"""
    import re
    init_path = os.path.join(_ENGINE_DIR, "__init__.py")
    if not os.path.isfile(init_path):
        return {}
    src = open(init_path, encoding="utf-8", errors="replace").read()
    mapping: dict[str, str] = {}
    for m in re.finditer(r"from\s+\.([a-z_][a-z0-9_]*)\s+import\s+\(?\s*([^\n]+?)\)?\s*\n",
                         src, re.S):
        mod = m.group(1)
        if mod not in _ENGINE_SUBMODULES:
            continue
        for n in _parse_parenthesized_names(m.group(2)):
            mapping[n] = mod
    return mapping


def _prod_engine_seeds(source: str) -> set[str]:
    """提取生产源码中直接引用的 engine 子模块名（含通过 __init__ 重导出的符号）。"""
    import re
    direct: set[str] = set(_find_engine_imports(source))
    # `from ...engine import <symbol>` 中经 __init__.py 重导出的符号 → 溯源到源模块
    for m in re.finditer(r"from\s+[\w.]+\.engine\s+import\s+\(?\s*([^\n]+?)\)?\s*\n",
                         source, re.S):
        for n in _parse_parenthesized_names(m.group(1)):
            if n in _REEXPORT_SYMBOL_MAP:
                direct.add(_REEXPORT_SYMBOL_MAP[n])
    return direct


_REEXPORT_SYMBOL_MAP = _reexport_symbol_map()


@dataclass
class CoverageEntry:
    """单条内容的覆盖度记录。"""

    content_id: str                    # e.g. "spell.fireball"
    ruleset_revision: str = ""
    status: CoverageStatus = CoverageStatus.MISSING
    source_spans: List[str] = field(default_factory=list)
    handlers: List[str] = field(default_factory=list)
    unit_tests: List[str] = field(default_factory=list)
    scenario_tests: List[str] = field(default_factory=list)
    # P1-08: CI 已确认该模块的显式 rule 测试通过（load_ci_results 写入）
    ci_passed: bool = False


@dataclass
class CoverageManifest:
    """内容覆盖度清单。"""

    entries: Dict[str, CoverageEntry] = field(default_factory=dict)
    ruleset_revision: str = "2024.1"

    # ── 注册与查询 ──────────────────────────────────────────────────

    def register(
        self,
        content_id: str,
        status: CoverageStatus,
        handlers: list = None,
        unit_tests: list = None,
        scenario_tests: list = None,
        source_spans: list = None,
    ) -> None:
        """注册或更新一条内容的覆盖度。"""
        entry = self.entries.get(content_id)
        if entry is None:
            entry = CoverageEntry(
                content_id=content_id,
                ruleset_revision=self.ruleset_revision,
            )
            self.entries[content_id] = entry
        entry.status = status
        if handlers:
            entry.handlers = handlers
        if unit_tests:
            entry.unit_tests = unit_tests
        if scenario_tests:
            entry.scenario_tests = scenario_tests
        if source_spans:
            entry.source_spans = source_spans

    def get_status(self, content_id: str) -> CoverageStatus:
        """获取指定内容的覆盖度状态。"""
        entry = self.entries.get(content_id)
        return entry.status if entry else CoverageStatus.MISSING

    def is_complete(self) -> bool:
        """所有内容均已验证。"""
        return all(
            e.status == CoverageStatus.VERIFIED for e in self.entries.values()
        )

    def summary(self) -> dict:
        """按状态统计数量。"""
        counts: Dict[str, int] = {}
        for entry in self.entries.values():
            key = entry.status.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    # ── 扫描 ────────────────────────────────────────────────────────

    def scan_modules(self) -> "CoverageManifest":
        """扫描 engine/data/tests 模块，自动检测覆盖度。

        扫描逻辑:
        1. engine/ 下模块 → 检测 handler 实现
        2. data/ 下数据文件 → 检测结构化数据
        3. tests/ 下测试文件 → 关联到对应 content_id
        """
        base_dir = os.path.dirname(os.path.dirname(__file__))
        engine_dir = os.path.join(base_dir, "engine")
        data_dir = os.path.join(base_dir, "data")
        tests_dir = os.path.normpath(os.path.join(base_dir, "..", "..", "tests"))

        # 1. 扫描 engine 模块
        engine_modules = self._scan_engine_modules(engine_dir)
        for content_id, handlers in engine_modules.items():
            entry = self.entries.get(content_id)
            if entry is None:
                entry = CoverageEntry(
                    content_id=content_id,
                    ruleset_revision=self.ruleset_revision,
                )
                self.entries[content_id] = entry
            entry.handlers = handlers
            if entry.status == CoverageStatus.MISSING:
                entry.status = CoverageStatus.WIRED

        # 2. 扫描 data 文件
        data_files = self._scan_data_files(data_dir)
        for content_id, data_file in data_files.items():
            entry = self.entries.get(content_id)
            if entry is None:
                entry = CoverageEntry(
                    content_id=content_id,
                    ruleset_revision=self.ruleset_revision,
                )
                self.entries[content_id] = entry
            entry.source_spans.append(data_file)
            if entry.status == CoverageStatus.MISSING:
                entry.status = CoverageStatus.DATA_ONLY

        # 3. 扫描测试文件 → 关联到真实存在的引擎模块
        #    仅关联已注册的引擎模块，不创建假的 engine.<test_name> 条目
        test_files = self._scan_test_files(tests_dir)
        for content_id, tests in test_files.items():
            entry = self.entries.get(content_id)
            if entry is None:
                continue  # 该 content_id 不是真实引擎模块，跳过
            entry.unit_tests = tests
            if entry.status in (CoverageStatus.DATA_ONLY, CoverageStatus.WIRED):
                entry.status = CoverageStatus.VERIFIED

        return self

    def _scan_engine_modules(self, engine_dir: str) -> Dict[str, List[str]]:
        """扫描 engine/ 目录，提取模块名作为 content_id。"""
        result: Dict[str, List[str]] = {}
        if not os.path.isdir(engine_dir):
            return result
        for fname in os.listdir(engine_dir):
            if fname.endswith(".py") and not fname.startswith("_"):
                module_name = fname[:-3]
                content_id = f"engine.{module_name}"
                result[content_id] = [module_name]
        return result

    def _scan_data_files(self, data_dir: str) -> Dict[str, str]:
        """扫描 data/ 目录，提取数据文件名作为 content_id。"""
        result: Dict[str, str] = {}
        if not os.path.isdir(data_dir):
            return result
        for fname in os.listdir(data_dir):
            if fname.endswith(".py") and not fname.startswith("_"):
                module_name = fname[:-3]
                content_id = f"data.{module_name}"
                result[content_id] = fname
        return result

    def _scan_test_files(self, tests_dir: str) -> Dict[str, List[str]]:
        """扫描 tests/ 目录，按模块名关联测试文件。"""
        result: Dict[str, List[str]] = {}
        if not os.path.isdir(tests_dir):
            return result
        for fname in os.listdir(tests_dir):
            if fname.startswith("test_") and fname.endswith(".py"):
                # test_combat_flow.py → engine.combat
                test_module = fname[5:-3]  # 去掉 test_ 前缀和 .py 后缀
                content_id = f"engine.{test_module}"
                result.setdefault(content_id, []).append(fname)
        return result

    # ── 持久化 ──────────────────────────────────────────────────────

    def save(self, path: str) -> None:
        """保存为 JSON 文件。"""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        data = {
            "ruleset_revision": self.ruleset_revision,
            "entries": {
                cid: {
                    "content_id": e.content_id,
                    "ruleset_revision": e.ruleset_revision,
                    "status": e.status.value,
                    "source_spans": e.source_spans,
                    "handlers": e.handlers,
                    "unit_tests": e.unit_tests,
                    "scenario_tests": e.scenario_tests,
                }
                for cid, e in self.entries.items()
            },
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str) -> "CoverageManifest":
        """从 JSON 文件加载。"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        manifest = cls(ruleset_revision=data.get("ruleset_revision", "2024.1"))
        for cid, edata in data.get("entries", {}).items():
            manifest.entries[cid] = CoverageEntry(
                content_id=edata["content_id"],
                ruleset_revision=edata.get("ruleset_revision", ""),
                status=CoverageStatus(edata.get("status", "MISSING")),
                source_spans=edata.get("source_spans", []),
                handlers=edata.get("handlers", []),
                unit_tests=edata.get("unit_tests", []),
                scenario_tests=edata.get("scenario_tests", []),
            )
        return manifest

    # ── 发布门禁 (TEST-002) ─────────────────────────────────────────

    def apply_wired_status(self) -> "CoverageManifest":
        """由生产链路自动推导覆盖度（TEST-002/DOC-001）。

        规则: 不允许手工宣称未验证的 FULL——状态从实际代码自动派生：
          1. 扫描生产链路目录（brain/agents/api/stats/build/data/knowledge/rules）
             对 `engine.X` 的 import（含经 engine/__init__.py 重导出的符号溯源）
             → 标记 WIRED（已接入生产入口）
          2. 沿 engine 模块内部相对引用做传递闭包（引擎内调用链同样视为已接入）
          3. 扫描 tests/ 目录对 `engine.X` 或模块名 `X` 的引用
             → 标记 VERIFIED（有 E2E/单测覆盖）
          4. 无引用 → 保持 MISSING/DATA_ONLY（门禁将失败）
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prod_dirs = ["brain", "agents", "api", "stats", "build",
                     "data", "knowledge", "rules"]
        tests_dir = os.path.normpath(os.path.join(base_dir, "..", "..", "tests"))

        # 收集生产链路直接引用的 engine 模块（种子）
        seeds: set[str] = set()
        for d in prod_dirs:
            dpath = os.path.join(base_dir, d)
            if not os.path.isdir(dpath):
                continue
            for dp, _dirs, fs in os.walk(dpath):
                for f in fs:
                    if not f.endswith(".py") or f.startswith("__"):
                        continue
                    try:
                        with open(os.path.join(dp, f), encoding="utf-8",
                                  errors="replace") as fh:
                            src = fh.read()
                    except Exception:
                        continue
                    seeds |= _prod_engine_seeds(src)

        # 引擎内部调用链：相对引用闭包（被生产种子引用的模块，其引擎内部依赖也算接入）
        internal: dict[str, set[str]] = {}
        for mod in _ENGINE_SUBMODULES:
            path = os.path.join(_ENGINE_DIR, f"{mod}.py")
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    internal[mod] = _engine_internal_imports(fh.read())
            except Exception:
                internal[mod] = set()

        wired = set(seeds)
        stack = list(seeds)
        while stack:
            m = stack.pop()
            for dep in internal.get(m, ()):
                if dep not in wired:
                    wired.add(dep)
                    stack.append(dep)
        wired = {f"engine.{m}" for m in wired}

        # 收集测试引用的 engine 模块
        verified: set[str] = set()
        # ★ P1-08: 测试显式声明其验证的规则/模块（@pytest.mark.rule("engine.X")）
        #   VERIFIED 必须具备显式 rule 映射 + 生产引用 + CI 确认通过。
        rule_mapped: set[str] = set()
        if os.path.isdir(tests_dir):
            for f in sorted(os.listdir(tests_dir)):
                if not f.startswith("test_") or not f.endswith(".py"):
                    continue
                try:
                    with open(os.path.join(tests_dir, f), encoding="utf-8",
                              errors="replace") as fh:
                        src = fh.read()
                except Exception:
                    continue
                verified |= {f"engine.{m}" for m in _find_engine_imports(src)}
                verified |= {f"engine.{m}" for m in _engine_internal_imports(src)}
                # P1-08: 解析 @pytest.mark.rule("engine.X") / rule('R-CMB-017')
                for m in re.finditer(
                        r'@pytest\.mark\.rule\(\s*["\']((?:engine\.)?[a-z_0-9.]+)["\']\s*\)',
                        src):
                    _rid = m.group(1)
                    if _rid.startswith("engine."):
                        rule_mapped.add(_rid)
                    elif _rid in _ENGINE_SUBMODULES:
                        rule_mapped.add(f"engine.{_rid}")

        # 登记状态（TEST-002/DOC-001 + P1-08）：
        #   - 仅生产引用（无测试）→ WIRED（已接入生产，缺验收测试）
        #   - 仅测试引用（无生产调用）→ FULL（测试通过但未接入生产链路）
        #   - 生产引用 + 测试引用（无显式 rule 映射）→ FULL（已实现且有测试，
        #     但未显式声明验证的规则/模块——不再单凭 import 即 VERIFIED）
        #   - 生产引用 + 测试引用 + 显式 rule 映射 → VERIFIED（生产入口真实调用，
        #     且测试显式声明验证该模块；CI 确认见 load_ci_results）
        wired_only = wired - verified
        for cid in wired_only:
            self.register(content_id=cid, status=CoverageStatus.WIRED)
        for cid in verified:
            if cid in wired:
                if cid in rule_mapped:
                    self.register(content_id=cid, status=CoverageStatus.VERIFIED)
                else:
                    self.register(content_id=cid, status=CoverageStatus.FULL)
            else:
                self.register(content_id=cid, status=CoverageStatus.FULL)

        # 先扫描存在的 engine 模块（handler 存在性）
        self.scan_modules()
        return self

    def load_ci_results(self, ci_json: dict) -> "CoverageManifest":
        """P1-08: 加载 CI 测试结果，仅对「CI 确认规则测试通过」的模块授予 VERIFIED。

        ci_json 形态（由 scripts/run_cov_gate.py 生成）:
          {"R-CMB-017": {"passed": true, "tests": ["tests/test_x.py::test_y"]},
           "engine.combat": {"passed": true, "tests": [...]}}
        规则: VERIFIED 的最终条件是「显式 rule 映射 + CI 确认通过」——
        仅出现在源码 import 中不再是充分条件。
        """
        passed_modules: set[str] = set()
        for rid, info in (ci_json or {}).items():
            if not isinstance(info, dict) or not info.get("passed"):
                continue
            if rid.startswith("engine."):
                passed_modules.add(rid)
            elif rid in _ENGINE_SUBMODULES:
                passed_modules.add(f"engine.{rid}")
        for cid in passed_modules:
            entry = self.entries.get(cid)
            if entry is not None and entry.status == CoverageStatus.VERIFIED:
                entry.ci_passed = True
        return self

    # 覆盖度等级排序（用于门禁比较）— 普通类属性
    _STATUS_RANK = {
        "MISSING": 0, "DATA_ONLY": 1, "PARTIAL": 2,
        "WIRED": 3, "FULL": 4, "VERIFIED": 5,
    }

    def assert_release_gate(self, required: CoverageStatus = CoverageStatus.FULL) -> None:
        """发布门禁：要求全部公开内容达到指定状态。

        规则: TEST-002 — 任何公开内容缺 handler 或验收测试即失败。
        complete 模式只发布 FULL。

        门禁范围限定为可执行模块（engine.*）——纯数据文件（data.*）
        不要求 handler（其执行逻辑在 engine 层），故不计入门禁。
        """
        self.apply_wired_status()
        below = [
            cid for cid, e in self.entries.items()
            if cid.startswith("engine.")
            and self._STATUS_RANK.get(e.status.value, 0) < self._STATUS_RANK[required.value]
        ]
        if below:
            raise AssertionError(
                f"CoverageManifest 发布门禁失败：{len(below)} 项未达 {required.value}\n"
                f"  未达标: {below[:20]}"
            )

    # ── 报告 ────────────────────────────────────────────────────────

    def generate_report(self) -> str:
        """生成可读的覆盖度报告。"""
        lines = [
            f"# CoverageManifest Report (revision {self.ruleset_revision})",
            "",
            f"Total entries: {len(self.entries)}",
            "",
            "## Summary",
        ]
        for status, count in sorted(self.summary().items()):
            lines.append(f"  {status}: {count}")
        lines.append("")
        lines.append("## Details")
        lines.append("")
        for cid, entry in sorted(self.entries.items()):
            lines.append(f"### {cid}")
            lines.append(f"  Status: {entry.status.value}")
            if entry.handlers:
                lines.append(f"  Handlers: {', '.join(entry.handlers)}")
            if entry.unit_tests:
                lines.append(f"  Tests: {', '.join(entry.unit_tests)}")
            lines.append("")
        return "\n".join(lines)
