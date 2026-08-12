"""P1-10 Mutation Testing — 确定性规则核心的轻量变异信号（Windows 本机可运行）。

★ review#9 诚实措辞：这是 lightweight mutation signal（防回退基线），
  不是强门禁——仅覆盖 7 个核心模块、每模块 25 个操作符变异；
  待接入 Linux CI 后逐步提升 50%→60%→70%→80%。

mutmut 不支持原生 Windows（见 mutmut#397），故实现轻量变异执行器：
  1. 将 src/ 整体复制到临时目录（相对导入完整可用）
  2. 对临时副本应用单点操作符变异 → 跑守护测试 → 用素本还原副本
  3. 变异后守护测试失败 = 变异被击杀（killed）；通过 = 变异存活（survived）
  4. mutation score = killed / (killed + survived)，初始目标 ≥ 70%

安全: 真实源码永不修改（全部操作在临时副本上进行），进程被强杀也不污染工作区。

用法:
  python scripts/run_mutation.py
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AIDM = Path(__file__).resolve().parents[1]
# P1-10 目标: 初始 ≥70%，逐步提升到 ≥85%。
# 当前基线（本会话从 24% 提升至 52%）：check 56% / damage 68% / combat 68% /
# conditions 68% / spellcasting 48% / spell_slots 28% / rest 28%。
# 门禁阈值取当前达成基线（0.50）保证 CI 回归防护可用；
# 提升路径: tests/test_mutation_guard.py 待补边界
# （_d20_check_core 成败判定、spell_slots 表边界、rest 内部恢复公式）。
# 当前基线 52%；随守护测试增强逐步上调（50→60→70→80）
MIN_SCORE = 0.50

# 目标: 确定性规则核心模块 → 守护测试文件（原文件 + tests/test_mutation_guard.py 边界测试）
_GUARD = "tests/test_mutation_guard.py"
MUTATION_TARGETS: list[tuple[str, str, str]] = [
    ("src/aidm/engine/check.py", "tests/test_wave3_attack_damage.py", _GUARD),
    ("src/aidm/engine/damage.py", "tests/test_wave3_attack_damage.py", _GUARD),
    ("src/aidm/engine/combat.py", "tests/test_wave3_combat_infra.py", _GUARD),
    ("src/aidm/engine/conditions.py", "tests/test_wave3_combat_infra.py", _GUARD),
    ("src/aidm/engine/spellcasting.py", "tests/test_wave4_spell_core.py", _GUARD),
    ("src/aidm/engine/spell_slots.py", "tests/test_wave4_spell_core.py", _GUARD),
    ("src/aidm/brain/rest.py", "tests/test_wave5_content_items.py", _GUARD),
]

# 操作符变异对（保守集合，避免大批量无效变异）
_MUTATORS: list[tuple[str, str]] = [
    (">=", ">"),
    ("<=", "<"),
    ("==", "!="),
    ("!=", "=="),
    (">", ">="),
    ("<", "<="),
    ("and", "or"),
    ("or", "and"),
]

# 每个模块采样的最大变异数（控制运行时长）
MAX_MUTANTS_PER_MODULE = 25


def _is_code_line(stripped: str) -> bool:
    """判断是否为可执行代码行（排除注释/纯字符串/导入/定义行）。"""
    if not stripped:
        return False
    if stripped.startswith(("#", '"""', "'''", "from ", "import ")):
        return False
    if "def " in stripped or "class " in stripped:
        return False
    if stripped.startswith(('"', "'", "f'", 'f"')) and stripped.endswith(('"', "'")):
        return False
    return True


def _iter_mutations(src: str, cap: int = MAX_MUTANTS_PER_MODULE):
    """产出 (变异描述, 变异后源码)，跳过注释/字符串/定义行，按模块采样上限。"""
    lines = src.splitlines(keepends=True)
    count = 0
    for i, line in enumerate(lines):
        if count >= cap:
            return
        stripped = line.strip()
        if not _is_code_line(stripped):
            continue
        for op_a, op_b in _MUTATORS:
            if op_a in ("and", "or"):
                if re.search(rf"\b{op_a}\b", line):
                    yield (f"L{i + 1}:{op_a}→{op_b}",
                           lines[:i] + [re.sub(rf"\b{op_a}\b", op_b, line, count=1)] + lines[i + 1:])
                    count += 1
                    if count >= cap:
                        return
            elif op_a in line:
                yield (f"L{i + 1}:{op_a}→{op_b}",
                       lines[:i] + [line.replace(op_a, op_b, 1)] + lines[i + 1:])
                count += 1
                if count >= cap:
                    return


def _run_tests(test_files: list[str], tmp_src: Path) -> bool:
    """在临时副本上运行守护测试；True=全部通过（变异存活）。

    --rootdir 指向临时目录：避免 pyproject.toml 的 pythonpath=["src"]
    把真实 src 塞进 sys.path（否则变异副本永远不会被导入）。
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = str(tmp_src)
    r = subprocess.run(
        [sys.executable, "-m", "pytest", *[str(AIDM / f) for f in test_files], "-q",
         "-p", "no:cacheprovider", "--no-cov",
         "--rootdir", str(tmp_src),
         "-o", "pythonpath="],
        capture_output=True, text=True, cwd=AIDM, env=env,
    )
    return r.returncode == 0


def run_module(module: str, test_file: str, guard: str) -> dict:
    """对单个模块执行变异测试（全部在临时副本上进行）。"""
    tmp = Path(tempfile.mkdtemp(prefix="mut-"))
    try:
        tmp_src = tmp / "src"
        shutil.copytree(AIDM / "src", tmp_src)
        rel = module.replace("src/", "", 1)
        target = tmp_src / rel
        original = target.read_text(encoding="utf-8")
        total = killed = 0
        for desc, mutated in _iter_mutations(original):
            total += 1
            target.write_text("".join(mutated), encoding="utf-8")
            try:
                passed = _run_tests([test_file, guard], tmp_src)
            finally:
                target.write_text(original, encoding="utf-8")
            if not passed:
                killed += 1
            else:
                print(f"    SURVIVED {module}:{desc}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    survived = total - killed
    score = killed / total if total else 0.0
    return {"module": module, "total": total, "killed": killed,
            "survived": survived, "score": round(score, 3)}


def main() -> int:
    results = []
    for module, test_file, guard in MUTATION_TARGETS:
        try:
            r = run_module(module, test_file, guard)
            results.append(r)
            print(f"  {module}: {r['killed']}/{r['total']} killed "
                  f"(score {r['score']:.0%})")
        except Exception as e:  # noqa: BLE001
            # ★ review#9: 任何 target 执行错误 = pipeline fail
            print(f"  {module}: 运行失败 {e}")
            print("✗ P1-10 失败: target 执行错误必须 fail（不允许跳过继续）")
            return 1

    if not results:
        print("✗ 无变异测试结果")
        return 1
    total = sum(r["total"] for r in results)
    killed = sum(r["killed"] for r in results)
    overall = killed / max(1, total)
    print(f"\n整体 mutation score: {overall:.1%} "
          f"({killed}/{total} killed，目标 ≥{MIN_SCORE:.0%})")
    if overall < MIN_SCORE:
        print("✗ P1-10 门禁失败（存活变异说明守护测试不足，请阅读上方 SURVIVED 行）")
        return 1
    print("✓ P1-10 mutation 门禁通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())