"""data.js 解析器 — 提取 6238 条规则三元组（正文/标签/来源路径）。

data.js 是 WinCHM 导出的搜索索引：`var contents = new Array("正文","标签","路径",...)`。
本解析器用 JS 字符串分词器处理转义（\\" \\\\ \\n \\uXXXX 等），比正则稳健。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuleEntry:
    body: str          # 纯文本正文
    tag: str           # 标签（稀有度/类型/等级段，可空）
    path: str          # 来源路径 topics/.../xxx.htm

    @property
    def title(self) -> str:
        """正文首行/首段作为标题。"""
        first = self.body.strip().split("\n", 1)[0]
        return first[:60]

    @property
    def source(self) -> str:
        """规范化来源路径（统一正斜杠）。"""
        return self.path.replace("\\", "/").strip()


# JS 转义映射
_JS_ESCAPES = {
    "n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f",
    "\\": "\\", '"': '"', "'": "'", "/": "/", "0": "\0",
}


def _tokenize_strings(body: str) -> list[str]:
    """从 data.js 的数组体里分词出所有双引号字符串（处理转义）。"""
    strings: list[str] = []
    i, n = 0, len(body)
    while i < n:
        # 跳过空白与逗号
        while i < n and body[i] in " \n\r\t,":
            i += 1
        if i >= n:
            break
        if body[i] != '"':               # 非字符串字符，跳过
            i += 1
            continue
        i += 1                            # 跳过开引号
        buf: list[str] = []
        while i < n:
            c = body[i]
            if c == "\\" and i + 1 < n:   # 转义序列
                nxt = body[i + 1]
                if nxt in _JS_ESCAPES:
                    buf.append(_JS_ESCAPES[nxt]); i += 2; continue
                if nxt == "u" and i + 5 < n:   # \uXXXX
                    try:
                        buf.append(chr(int(body[i + 2:i + 6], 16))); i += 6; continue
                    except ValueError:
                        pass
                buf.append(nxt); i += 2; continue
            if c == '"':                  # 闭引号
                i += 1
                break
            buf.append(c); i += 1
        strings.append("".join(buf))
    return strings


def parse_datajs(path: str) -> list[RuleEntry]:
    """解析 data.js → RuleEntry 列表（约 6238 条）。

    规则: 知识库 RAG 语料源（data.js 6238 条纯文本索引）
    """
    raw = open(path, "rb").read().decode("utf-8", errors="replace")
    start = raw.find("new Array(")
    if start < 0:
        raise ValueError("data.js 中未找到 'new Array(' —— 格式不符")
    start += len("new Array(")
    end = raw.rfind(")")
    body = raw[start:end]
    strings = _tokenize_strings(body)
    entries: list[RuleEntry] = []
    # 三元一组：(正文, 标签, 路径)
    for j in range(0, len(strings) - 2, 3):
        ebody, etag, epath = strings[j], strings[j + 1], strings[j + 2]
        entries.append(RuleEntry(body=ebody, tag=etag, path=epath))
    return entries


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    from ..config import get_settings
    p = get_settings().rules_datajs_path
    entries = parse_datajs(p)
    print(f"[parse_datajs] 解析 {len(entries)} 条规则条目")
    assert len(entries) > 6000, f"条目数异常: {len(entries)}"
    # 抽查前几条 + 标签分布
    for e in entries[:3]:
        print(f"  - tag={e.tag!r:12} title={e.title!r}")
    tags = {}
    for e in entries:
        tags[e.tag] = tags.get(e.tag, 0) + 1
    top = sorted(tags.items(), key=lambda x: -x[1])[:8]
    print("  标签分布 top8:", {k: v for k, v in top})
    print("[parse_datajs] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
