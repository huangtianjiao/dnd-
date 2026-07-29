#!/usr/bin/env python
"""批量提取官方扩展书规则文本到 rules_text（F6 扩展书批次）。

范围决策（对照 5echm_web/topics 盘点）：
- 提取：官方扩展规则书 20 本 + 怪物扩展书 4 本 + 速查 2 本 + 怪物图鉴2025 全文
- 去重：巨人之荣耀==毕格比巨献（取后者）；魔邓肯出品:多元宇宙的怪物(32页)
  是 多元宇宙的怪物(320页) 的残版（取全版）
- 排除：2014 三宝书（F5 决定不建库）、玩家手册2024（试读版）、模组（剧透，
  单独批次）、第三方（非官方）、DNDBeyond/新人使用指南（网站说明）、模板
用法: python scripts/extract_expansions.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_rules import extract

ROOT = r"d:\game\dnd\5echm_web\topics"
DST = r"d:\game\dnd\aidm\data\rules_text"

BOOKS = [
    # 官方扩展规则书（20）
    "珊娜萨的万事指南", "塔莎的万事坩埚", "万象无常书",
    "费资本的巨龙宝库", "星界冒险者指南", "范·里希腾的鸦阁魔域指南",
    "龙枪：龙后之影", "艾伯伦寻路者指南", "艾伯伦：从终末战争中崛起",
    "荒洲探险家指南", "塞洛斯之神话奥德赛", "塔尔多雷战役设定集",
    "斯翠海文：混沌研习", "拉尼卡公会长指南", "莫提的位面游记",
    "印记城与外域", "异域风景：多元宇宙之冒险", "艾奎兹玄有限责任公司",
    "剑湾冒险者指南", "毕格比巨献：巨人之荣耀",
    # 怪物扩展书（4）
    "瓦罗怪物指南", "魔邓肯的众敌卷册", "布布的星界怪兽展",
    "多元宇宙的怪物",
    # 速查（2）
    "施法者速查", "速查",
    # 怪物图鉴2025 全文（lore/战术描述）
    "怪物图鉴2025",
]


# 第二批：模组整目录（tag 前缀「模组/」，供 retriever 防剧透标注识别）
MODULES_BOOK = "模组"
# 「其他」目录：排除 UA 测试材料（UA.htm / UA/ / 新UA/），保留正式内容
MISC_BOOK = "其他"
MISC_EXCLUDE_PREFIXES = ("UA.htm", "UA" + os.sep, "新UA" + os.sep)


def extract_book(src: str, dst_book: str, skip=None) -> int:
    """提取单个书目录 → rules_text/<dst_book>，返回页数。skip(rel) 返回 True 则跳过。"""
    n = 0
    for dp, _dirs, files in os.walk(src):
        for f in files:
            if not f.lower().endswith((".htm", ".html")):
                continue
            rel = os.path.relpath(os.path.join(dp, f), src)
            if skip and skip(rel):
                continue
            txt = extract(os.path.join(dp, f))
            if not txt:
                continue
            dstp = os.path.join(DST, dst_book, os.path.splitext(rel)[0] + ".txt")
            os.makedirs(os.path.dirname(dstp), exist_ok=True)
            open(dstp, "w", encoding="utf-8").write(txt)
            n += 1
    return n


def main():
    t0 = time.time()
    total = 0
    for book in BOOKS:
        src = os.path.join(ROOT, book)
        if not os.path.isdir(src):
            print(f"[SKIP] 目录不存在: {book}")
            continue
        n = extract_book(src, book)
        total += n
        print(f"[OK] {book}: {n} 页")

    # 第二批：模组 + 「其他」非 UA 部分
    n = extract_book(os.path.join(ROOT, MODULES_BOOK), MODULES_BOOK)
    total += n
    print(f"[OK] {MODULES_BOOK}: {n} 页")
    n = extract_book(os.path.join(ROOT, MISC_BOOK), MISC_BOOK,
                     skip=lambda rel: rel.startswith(MISC_EXCLUDE_PREFIXES))
    total += n
    print(f"[OK] {MISC_BOOK}(非UA): {n} 页")
    print(f"共提取 {total} 页, 耗时 {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
