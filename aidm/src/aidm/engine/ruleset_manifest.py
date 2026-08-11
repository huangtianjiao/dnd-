"""不可变规则集标识 — RulesetManifest 数据类。

定义当前战役所使用的规则集版本、源书清单、内容包及策略约束。
用于确保 AI 与引擎在相同规则版本下运行，防止规则混用。

规则依据: ARC-001 不可变规则集标识
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List


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

    标识当前战役使用的规则集版本、包含的源书、内容包与策略。
    """

    ruleset_id: str                    # e.g. "dnd5e_2024_core"
    revision: str                      # e.g. "2024.1"
    source_books: List[SourceBook] = field(default_factory=list)
    content_packs: List[str] = field(default_factory=list)
    policies: dict = field(default_factory=dict)

    # ── 序列化 ──────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """序列化为字典。"""
        return {
            "ruleset_id": self.ruleset_id,
            "revision": self.revision,
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
            "content_packs": list(self.content_packs),
            "policies": dict(self.policies),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RulesetManifest":
        """从字典反序列化。"""
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
        )

    # ── 持久化 ──────────────────────────────────────────────────────

    def save(self, path: str) -> None:
        """保存为 JSON 文件。"""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str) -> "RulesetManifest":
        """从 JSON 文件加载。"""
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


# ── 默认 manifest 路径 ────────────────────────────────────────────────

_DEFAULT_MANIFEST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "ruleset_manifest.json"
)


def load_default_manifest() -> RulesetManifest:
    """加载项目内置的默认规则集清单。"""
    return RulesetManifest.load(_DEFAULT_MANIFEST_PATH)
