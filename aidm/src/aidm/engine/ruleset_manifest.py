"""不可变规则集标识 — RulesetManifest 数据类。

定义当前战役所使用的规则集版本、机械基线、源书清单、内容包、
House Rule 覆盖与策略约束。用于确保 AI 与引擎在相同规则版本下运行，
防止规则混用。

规则依据: ARC-001 不可变规则集标识 + 改造方案 §2.1/§2.2
（mechanics_baseline / house_rule_pack / schema_revision 与规则模式锁定）
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class RulesMode(StrEnum):
    """战役规则模式（改造方案 §2.1，默认 RAW_2024）。

    - RAW_2024: 严格执行 2024 规则；非法创建/升级/动作拒绝
    - RAW_2024_OPTIONAL: 显式开启官方可选规则
    - HOUSE_RULE: 战役自定义，覆盖项必须记录 rule_id/原值/新值/原因
    - FREEFORM: 沙盒/测试/特殊剧本，允许绕过部分规则，不得伪装成 RAW
    """

    RAW_2024 = "raw_2024"
    RAW_2024_OPTIONAL = "raw_2024_optional"
    HOUSE_RULE = "house_rule"
    FREEFORM = "freeform"


@dataclass
class SourceBook:
    """单本源规则书。"""

    book_id: str          # e.g. "PHB2024"
    edition: str          # "2024" or "2014"
    title: str
    content_hash: str     # SHA256 of source content
    authority_level: str  # "core" / "supplement" / "homebrew"


@dataclass
class RulesetManifest:
    """不可变规则集清单。

    标识当前战役使用的规则集版本、机械基线、源书、内容包与策略。
    """

    ruleset_id: str                    # e.g. "dnd5e_2024_core"
    revision: str                      # e.g. "2024.1"
    source_books: list[SourceBook] = field(default_factory=list)
    content_packs: list[str] = field(default_factory=list)
    policies: dict = field(default_factory=dict)
    # 改造方案 §2.2: 机械基线固定为 SRD v5.2.1 / 2024 core semantics
    mechanics_baseline: str = "srd_5.2.1"
    # 改造方案 §2.2: House Rule 必须是显式 override 包，不允许散落 if/else
    house_rule_pack: str | None = None
    schema_revision: int = 3           # 方案 JSON 示例中 schema_revision: 3

    # ── 序列化 ──────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """序列化为字典。"""
        return {
            "ruleset_id": self.ruleset_id,
            "revision": self.revision,
            "mechanics_baseline": self.mechanics_baseline,
            "content_packs": list(self.content_packs),
            "house_rule_pack": self.house_rule_pack,
            "schema_revision": self.schema_revision,
            "source_books": [
                {
                    "book_id": sb.book_id,
                    "edition": sb.edition,
                    "title": sb.title,
                    "content_hash": sb.content_hash,
                    "authority_level": sb.authority_level,
                }
                for sb in self.source_books
            ],
            "policies": dict(self.policies),
        }

    @classmethod
    def from_dict(cls, data: dict) -> RulesetManifest:
        """从字典反序列化（缺失新字段时回退默认，兼容旧 manifest 文件）。"""
        source_books = [
            SourceBook(
                book_id=sb["book_id"],
                edition=sb["edition"],
                title=sb["title"],
                content_hash=sb.get("content_hash", ""),
                authority_level=sb.get("authority_level", "core"),
            )
            for sb in data.get("source_books", [])
        ]
        return cls(
            ruleset_id=data["ruleset_id"],
            revision=data["revision"],
            source_books=source_books,
            content_packs=data.get("content_packs", []),
            policies=data.get("policies", {}),
            mechanics_baseline=data.get("mechanics_baseline", "srd_5.2.1"),
            house_rule_pack=data.get("house_rule_pack"),
            schema_revision=int(data.get("schema_revision", 3)),
        )

    # ── 持久化 ──────────────────────────────────────────────────────

    def save(self, path: str | Path) -> None:
        """保存为 JSON 文件。"""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
                     encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> RulesetManifest:
        """从 JSON 文件加载。"""
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


# ── 默认 manifest 路径 ────────────────────────────────────────────────

_DEFAULT_MANIFEST_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "ruleset_manifest.json"
)


def load_default_manifest() -> RulesetManifest:
    """加载项目内置的默认规则集清单。"""
    return RulesetManifest.load(_DEFAULT_MANIFEST_PATH)
