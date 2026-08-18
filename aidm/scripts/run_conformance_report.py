"""规则一致性矩阵 CI 输出（改造方案 §13.1/§13.2）。

输出 JSON 报告到 stdout（--check 模式用于 CI：任何规则未达到
min-status 时退出码非 0）。

用法:
  python scripts/run_conformance_report.py                # 打印 JSON 报告
  python scripts/run_conformance_report.py --check        # CI 门禁（默认 DECLARED）
  python scripts/run_conformance_report.py --check --min-status E2E_VERIFIED
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

AIDM = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AIDM / "src"))

from aidm.rules.conformance import RawStatus, load_default_matrix  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="规则一致性矩阵 CI 输出")
    parser.add_argument("--check", action="store_true",
                        help="CI 门禁模式：低于 min-status 的规则导致非零退出")
    parser.add_argument("--min-status", default="DECLARED",
                        choices=[s.value for s in RawStatus])
    parser.add_argument("--out", default="", help="额外写入的 JSON 文件路径")
    args = parser.parse_args(argv)

    matrix = load_default_matrix()
    text = matrix.json_report()
    print(text)

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")

    if args.check:
        level = {s.value: i for i, s in enumerate(RawStatus)}
        min_level = level[args.min_status]
        failed = [
            r.rule_id for r in matrix
            if level[r.raw_status] < min_level
        ]
        if failed:
            print(f"[conformance] FAIL: {len(failed)} 条规则低于 {args.min_status}: "
                  f"{', '.join(failed)}", file=sys.stderr)
            return 1
        print(f"[conformance] OK: {len(matrix)} 条规则全部 ≥ {args.min_status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
