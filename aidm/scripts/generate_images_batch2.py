"""batch2 — 从 5echm_web 抽取魔法物品/据点地点/核心怪物，复用 batch1 异步管线生成图片。

复用 generate_images.py 的：Job / load_api_key / main_async / slugify / STYLE / 尺寸常量。
输出：aidm/data/images/{magic-items,stronghold,monsters}/*.png + images_manifest_batch2.json

用法：
  cd D:/game/dnd/aidm
  PYTHONPATH=src python scripts/generate_images_batch2.py --concurrency 10
  PYTHONPATH=src python scripts/generate_images_batch2.py --dry-run
  PYTHONPATH=src python scripts/generate_images_batch2.py --categories monsters --limit 5
"""

from __future__ import annotations

import argparse
import json
import os
import re
import html
import sys
import time
from collections import defaultdict
from pathlib import Path

# 复用 batch1 管线
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import generate_images as g  # noqa: E402

from generate_images import (Job, load_api_key, main_async, slugify,  # noqa: E402
                             STYLE, SIZE_ICON, OUT_ROOT, PROJECT_ROOT, MODEL)

TOPICS = PROJECT_ROOT.parent / "5echm_web" / "topics"   # D:/game/dnd/5echm_web/topics
MANIFEST2 = OUT_ROOT / "images_manifest_batch2.json"

# ──────────────────────────────────────────────────────────────────────────
# 通用读取/清洗
# ──────────────────────────────────────────────────────────────────────────
def readtext(p: Path) -> str:
    raw = p.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except Exception:
            pass
    return raw.decode("utf-8", errors="replace")

def clean(t: str) -> str:
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()

# 中英名对：中文 + 空格 + 首字母大写英文
PAIR_RE = re.compile(r"([\u4e00-\u9fff·]{2,12})\s+([A-Z][A-Za-z’'\- ]{3,40})")

AGE_PREFIX = ("幼年", "少年", "青年", "成年", "老年", "远古", "古龙")


# ──────────────────────────────────────────────────────────────────────────
# 1. 魔法物品（DMG2024 魔法物品详述，按稀有度分文件，每文件多条）
# ──────────────────────────────────────────────────────────────────────────
MI_CAT = {"武器": "weapon", "护甲": "armor", "戒指": "ring", "权杖": "rod",
          "法杖": "staff", "药水": "potion", "魔杖": "wand", "卷轴": "scroll",
          "奇物": "wondrous"}
MI_ITEMWORD = {"weapon": "weapon", "armor": "suit of armor", "ring": "ring",
               "rod": "rod", "staff": "staff", "potion": "potion bottle",
               "wand": "wand", "scroll": "spell scroll",
               "wondrous": "magical artifact", "misc": "magical item"}
# 排除小节标题/稀有度名等非物品词
MI_NOISE = {"魔法物品", "多种稀有度", "普通", "非普通", "珍稀", "极珍稀", "传说",
            "神器", "物品", "稀有度", "属性", "同调", "诅咒"}


def extract_magic_items() -> list[Job]:
    base = TOPICS / "城主指南2024" / "7.宝藏" / "魔法物品详述"
    items: dict[str, tuple[str, str]] = {}   # cn -> (en, cat)
    h6_re = re.compile(r"<H6[^>]*>(.*?)</H6>", re.S | re.I)
    for r, ds, fs in os.walk(base):
        rel = os.path.relpath(r, base)
        top = rel.split(os.sep)[0] if rel != "." else "."
        cat = MI_CAT.get(top, "misc")
        for f in fs:
            if not f.lower().endswith((".htm", ".html")):
                continue
            raw = readtext(Path(r) / f)
            for m in h6_re.finditer(raw):
                h = clean(m.group(1))                  # "营养珠 Bead of Nourishment"
                pm = re.match(r"([\u4e00-\u9fff·]{2,12})\s+([A-Z][A-Za-z’'\- ]{3,40})", h)
                if not pm:
                    continue
                cn, en = pm.group(1), pm.group(2).strip()
                if cn in MI_NOISE or cn in items:
                    continue
                items[cn] = (en, cat)
    jobs: list[Job] = []
    for cn, (en, cat) in items.items():
        word = MI_ITEMWORD.get(cat, "magical item")
        prompt = (f"a {en}, a magical {word}, glowing enchantment aura, "
                  f"intricate arcane runes, fantasy magic item icon, "
                  f"centered on dark gradient background, soft rim lighting, {STYLE}")
        out = OUT_ROOT / "magic-items" / f"{slugify(en.split()[0])}_{slugify(cn)}.png"
        jobs.append(Job("magic-items", en, cn, prompt, SIZE_ICON, out))
    return jobs


# ──────────────────────────────────────────────────────────────────────────
# 2. 据点地点（DMG2024 据点特色设施）
# ──────────────────────────────────────────────────────────────────────────
LOC_EN = {
    "仓库": "storeroom", "传送法阵": "teleportation circle", "公会大厅": "guildhall",
    "兵营": "barracks", "军械库": "armory", "冥想间": "meditation chamber",
    "剧院": "theater", "动物园": "menagerie", "半位面": "demiplane",
    "图书馆": "library", "圣器室": "reliquary", "圣坛": "altar", "圣所": "sanctuary",
    "圣物库": "reliquary vault", "天文台": "observatory",
    "奥术研究室": "arcane study", "实验室": "laboratory", "工坊": "workshop",
    "战事中心": "war room", "抄写室": "scribing chamber", "档案室": "archive",
    "温室": "greenhouse", "游戏厅": "gaming hall", "种植园": "plantation",
    "训练场": "training ground", "酒馆": "tavern", "铁匠铺": "blacksmith forge",
    "陈列室": "exhibition hall", "马厩": "stable",
}
LOC_SKIP = {"特色设施", "基础设施", "据点地图"}


def extract_stronghold() -> list[Job]:
    base = TOPICS / "城主指南2024" / "8.据点" / "3.据点地图" / "特色设施"
    jobs: list[Job] = []
    for f in sorted(os.listdir(base)):
        if not f.lower().endswith(".htm"):
            continue
        cn = os.path.splitext(f)[0]
        if cn in LOC_SKIP:
            continue
        en = LOC_EN.get(cn, cn)
        prompt = (f"the interior of a stronghold {en} ({cn}), fantasy architecture, "
                  f"atmospheric candlelight, rich detail, wide scene, {STYLE}")
        out = OUT_ROOT / "stronghold" / f"{slugify(cn)}.png"
        jobs.append(Job("stronghold", en, cn, prompt, "1536x864", out))
    return jobs


# ──────────────────────────────────────────────────────────────────────────
# 3. 核心怪物（2025 怪物图鉴，一文件一怪，折叠年龄变体，按类型均衡取 ~200）
# ──────────────────────────────────────────────────────────────────────────
MON_TYPE = {"亡灵": "undead", "元素": "elemental", "天族": "celestial",
            "妖精": "fey", "巨人": "giant", "异怪": "aberration",
            "怪兽": "monstrosity", "构装": "construct", "植物": "plant",
            "泥怪": "ooze", "类人": "humanoid", "邪魔": "fiend", "龙类": "dragon"}
MON_SKIP = {"目录", "索引", "前言", "序", "总览"}
PER_TYPE_CAP = 16


def _species(cn: str) -> str:
    for a in AGE_PREFIX:
        if cn.startswith(a):
            return cn[len(a):]
    return cn


def extract_monsters(limit_per_type: int = PER_TYPE_CAP) -> list[Job]:
    base = TOPICS / "怪物图鉴2025"
    by_type: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for r, ds, fs in os.walk(base):
        rel = os.path.relpath(r, base)
        top = rel.split(os.sep)[0] if rel != "." else "."
        if rel == "." or top in ("附录A", "附录B", "前言"):
            continue
        typ = MON_TYPE.get(top, "creature")
        for f in fs:
            if not f.lower().endswith((".htm", ".html")):
                continue
            cn0 = os.path.splitext(f)[0]
            if cn0 in MON_SKIP:
                continue
            t = clean(readtext(Path(r) / f))
            m = PAIR_RE.search(t)
            if not m:
                continue
            cn = m.group(1).strip()
            en = m.group(2).strip()
            if cn in MON_SKIP or en in ("Zombies",):
                continue
            sp = _species(cn)
            by_type[typ].append((sp, en, cn, cn0))
    # 去重 + 按类型均衡取
    jobs: list[Job] = []
    for typ, lst in by_type.items():
        seen = set()
        took = 0
        for sp, en, cn, cn0 in lst:
            if sp in seen:
                continue
            seen.add(sp)
            prompt = (f"a {en} ({cn}), a {typ} creature from a fantasy bestiary, "
                      f"full body monster concept art, dramatic, "
                      f"plain atmospheric background, {STYLE}")
            out = OUT_ROOT / "monsters" / f"{slugify(en.split()[0])}_{slugify(cn)}.png"
            jobs.append(Job("monsters", en, cn, prompt, SIZE_ICON, out))
            took += 1
            if took >= limit_per_type:
                break
    return jobs


# ──────────────────────────────────────────────────────────────────────────
# 清单
# ──────────────────────────────────────────────────────────────────────────
def build_catalog(categories: set[str] | None = None) -> list[Job]:
    jobs: list[Job] = []
    builders = {
        "magic-items": extract_magic_items,
        "stronghold": extract_stronghold,
        "monsters": extract_monsters,
    }
    for cat, fn in builders.items():
        if categories and cat not in categories:
            continue
        jobs.extend(fn())
    return jobs


def write_manifest(jobs: list[Job]) -> None:
    MANIFEST2.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "batch": "batch2 (from 5echm_web)",
        "model": MODEL,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(jobs),
        "summary": {s: sum(1 for j in jobs if j.status == s)
                    for s in ("ok", "skipped", "failed")},
        "items": [
            {
                "category": j.category, "name": j.name, "cn_name": j.cn_name,
                "file": j.out_path.relative_to(PROJECT_ROOT).as_posix()
                if j.out_path.exists() else None,
                "size": j.size, "status": j.status, "url": j.url,
                "attempts": j.attempts, "error": j.error, "prompt": j.prompt,
            } for j in jobs
        ],
    }
    MANIFEST2.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                         encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="batch2：从 5echm_web 抽取并生成图片")
    ap.add_argument("--concurrency", type=int, default=10)
    ap.add_argument("--categories", default="",
                    help="仅跑 magic-items/stronghold/monsters，逗号分隔")
    ap.add_argument("--limit", type=int, default=0, help="限制任务数（测试用）")
    ap.add_argument("--max", type=int, default=0,
                    help="本次最多新生成图片数（日额度护栏，如 285 留余量避免撞 300/天墙）")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cats = {c.strip() for c in args.categories.split(",") if c.strip()} or None
    jobs = build_catalog(cats)
    if args.limit:
        jobs = jobs[:args.limit]

    from collections import Counter
    by_cat = Counter(j.category for j in jobs)
    print(f"模型: {MODEL}  并发: {args.concurrency}  任务数: {len(jobs)}")
    print("  分类:", dict(by_cat))
    if args.dry_run:
        for j in jobs[:40]:
            print(f"  [{j.category}] {j.name} ({j.cn_name}) {j.size}")
        if len(jobs) > 40:
            print(f"  ... 共 {len(jobs)} 条")
        return

    # 实跑前剔除已存在的（不进 main_async），减少协程数与内存，避免跳过突发
    pending = [j for j in jobs
               if not (j.out_path.exists() and j.out_path.stat().st_size > 0)]
    skipped_exist = len(jobs) - len(pending)
    print(f"  已存在跳过: {skipped_exist}  待生成: {len(pending)}")
    if args.max:
        pending = pending[:args.max]
        print(f"  --max {args.max} -> 本次新生成上限 {len(pending)}")

    api_key = load_api_key()
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    results = asyncio_run_jobs(pending, args.concurrency, api_key, 0)
    write_manifest(results)
    ok = sum(1 for j in results if j.status == "ok")
    sk = sum(1 for j in results if j.status == "skipped")
    fail = [j for j in results if j.status == "failed"]
    print("\n==== batch2 统计 ====")
    print(f"成功 {ok}  跳过(已存在) {sk}  失败 {len(fail)}")
    if fail:
        for j in fail[:20]:
            print(f"  [{j.category}] {j.name} — {j.error[:120]}")
    print(f"清单: {MANIFEST2}")


def asyncio_run_jobs(jobs, concurrency, api_key, max_ok=0):
    import asyncio
    return asyncio.run(main_async(jobs, concurrency, api_key, max_ok=max_ok))


if __name__ == "__main__":
    main()
