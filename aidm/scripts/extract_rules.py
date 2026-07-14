#!/usr/bin/env python
"""提取 WinCHM 导出的 HTML 规则页正文为纯文本，供后续规则提炼。

剔除 syn() 等 WinCHM 框架脚本，保留标题/段落/列表/表格结构。
用法: extract_rules.py <源目录> <目标目录>
"""
import os
import sys
from bs4 import BeautifulSoup


def extract(path):
    raw = open(path, "rb").read()
    html = None
    for enc in ("utf-8", "gbk"):
        try:
            html = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if html is None:
        return None

    soup = BeautifulSoup(html, "lxml")
    for s in soup(["script", "style", "meta", "link", "noscript"]):
        s.decompose()
    body = soup.body or soup

    out = []
    for el in body.descendants:
        if el.name in ("h1", "h2", "h3", "h4", "h5"):
            out.append("\n## " + el.get_text(strip=True))
        elif el.name == "li":
            out.append("  - " + el.get_text(" ", strip=True))
        elif el.name == "p":
            t = el.get_text(" ", strip=True)
            if t:
                out.append(t)
        elif el.name == "th":
            out.append(" | " + el.get_text(strip=True))
        elif el.name == "td":
            out.append(" | " + el.get_text(strip=True))
        elif el.name == "tr" and out and not out[-1].startswith(" |"):
            out.append("")
    return "\n".join(out).strip()


def main():
    if len(sys.argv) < 3:
        print("用法: extract_rules.py <源目录> <目标目录>")
        sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    n = 0
    for dp, _dirs, files in os.walk(src):
        for f in files:
            if not f.lower().endswith((".htm", ".html")):
                continue
            srcp = os.path.join(dp, f)
            txt = extract(srcp)
            if not txt:
                continue
            rel = os.path.relpath(srcp, src)
            dstp = os.path.join(dst, os.path.splitext(rel)[0] + ".txt")
            os.makedirs(os.path.dirname(dstp), exist_ok=True)
            open(dstp, "w", encoding="utf-8").write(txt)
            n += 1
    print(f"提取 {n} 页 -> {dst}")


if __name__ == "__main__":
    main()
