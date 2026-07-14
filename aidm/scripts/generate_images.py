"""批量生成 D&D AI DM 项目图片 — SenseAudio 图片 API（异步 + 轮询，并发 10）。

数据来源：
  - 状态/护甲/武器/钱币：直接读 aidm 引擎数据（conditions.CONDITIONS / equipment.*）
  - 职业/种族/法术学派/骰子/场景/封面：内置主题清单
模型：senseaudio-image-2.0-260319（最佳画质）

用法：
  cd D:/game/dnd/aidm
  PYTHONPATH=src python scripts/generate_images.py
可选参数：
  --concurrency N   并发数（默认 10）
  --categories a,b 仅跑指定分类
  --dry-run        只打印任务清单不生成
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import io
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx

# ──────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]          # aidm/
DND_ROOT = PROJECT_ROOT.parent                              # D:/game/dnd
ENV_FILE = DND_ROOT / ".env"
SRC_ROOT = PROJECT_ROOT / "src"
OUT_ROOT = PROJECT_ROOT / "data" / "images"
MANIFEST_PATH = OUT_ROOT / "images_manifest.json"

API_BASE = "https://api.senseaudio.cn"
ASYNC_EP = "/v1/image/async"
PENDING_EP = "/v1/image/pending"
SYNC_EP = "/v1/image/sync"        # 同步直出，无队列，比异步快且稳

MODEL = "senseaudio-image-2.0-260319"
CONCURRENCY = 10
POLL_INTERVAL = 3.0          # 轮询间隔（秒）
POLL_TIMEOUT = 300.0         # 单任务最长等待（秒）
MAX_ATTEMPTS = 3             # 失败重试次数

# 配额/速率限制识别（命中即触发熔断，停止提交新任务，避免重试风暴）
LIMIT_RE = re.compile(r"已达到使用限制|余额不足|rate.?limit|quota|insufficient", re.IGNORECASE)

# 各分类尺寸（senseaudio-image-2.0-260319 支持值）
SIZE_ICON = "1024x1024"      # 状态/护甲/武器/钱币/法术学派/骰子
SIZE_PORTRAIT = "864x1536"   # 职业/种族
SIZE_SCENE = "2048x1024"     # 场景
SIZE_COVER = "2688x1152"     # 封面

# 统一风格后缀
STYLE = ("fantasy illustration, dungeons and dragons style, highly detailed, "
         "rich colors, dramatic lighting, digital painting, concept art")


# ──────────────────────────────────────────────────────────────────────────
# 中文名 → 英文名映射（图片模型英文 prompt 更稳）
# ──────────────────────────────────────────────────────────────────────────
COND_EN = {
    "目盲": "blinded", "魅惑": "charmed", "耳聋": "deafened", "恐慌": "frightened",
    "受擒": "grappled", "失能": "incapacitated", "隐形": "invisible", "麻痹": "paralyzed",
    "石化": "petrified", "力竭": "exhaustion", "中毒": "poisoned", "倒地": "prone",
    "束缚": "restrained", "震慑": "stunned", "昏迷": "unconscious",
}
# 状态效应的视觉描述（不只是画一个词，而是画出生动的状态意象）
COND_DESC = {
    "目盲": "a warrior clutching their eyes, a white cloth bandage over the eyes, stumbling, hazy grey fog obscuring vision",
    "魅惑": "an adventurer entranced by glowing magical heart-shaped runes swirling around their head, dreamy pink and gold magical charm aura",
    "耳聋": "a fighter pressing hands to their ears, ringing sound waves depicted as faded broken concentric arcs, muted grey sound",
    "恐慌": "a hero recoiling in terror, fleeing from a looming shadowy monster silhouette, cold blue fear aura, wide scared eyes",
    "受擒": "an adventurer seized firmly by a large clawed gauntlet around the torso, struggling, locked in a grapple",
    "失能": "a slumped dazed adventurer unable to act, swirling confusion stars above the head, limp and helpless",
    "隐形": "a faint shimmering translucent outline of a sneaking rogue, only ripples and footprints in dust visible, glinting invisible silhouette",
    "麻痹": "a fighter frozen rigid mid-stride, body turned to stiff golden stone-like sheen, unable to move, paralyzed",
    "石化": "an adventurer halfway turned to grey cracked stone from feet upward, statue-like, petrification spreading",
    "力竭": "a weary exhausted traveler hunched over, dark circles, sweat, dragging feet, three darkened exhaustion pips glowing",
    "中毒": "an adventurer clutching stomach, sickly green poison bubbles and dripping venom, green toxic mist around",
    "倒地": "a knight fallen flat on the ground face-up, prone and struggling to rise, dropped sword beside",
    "束缚": "an adventurer tangled in glowing magical bonds and chains, roots wrapping around limbs, restrained",
    "震慑": "a warrior dazed and stunned, spiral stars and lightning circling the head, frozen blank stare",
    "昏迷": "an unconscious adventurer lying collapsed on the ground, small floating Z's of sleep, knocked out cold",
}

ARMOR_EN = {
    "布甲": "padded armor", "皮甲": "leather armor", "镶钉皮甲": "studded leather armor",
    "兽皮甲": "hide armor", "链甲衫": "chain shirt", "鳞甲": "scale mail",
    "胸甲": "breastplate", "半身板甲": "half plate armor", "环甲": "ring mail",
    "链甲": "chain mail", "板条甲": "splint armor", "板甲": "full plate armor",
    "盾牌": "knight's shield",
}

WEAPON_EN = {
    "短棒": "wooden club", "匕首": "dagger", "巨棒": "greatclub", "手斧": "hand axe",
    "标枪": "javelin", "轻锤": "light hammer", "硬头锤": "mace", "长棍": "quarterstaff",
    "镰刀": "sickle", "矛": "spear", "飞镖": "throwing dart", "轻弩": "light crossbow",
    "短弓": "shortbow", "投石索": "sling", "战斧": "battleaxe", "链枷": "flail",
    "长柄刀": "glaive", "巨斧": "great axe", "巨剑": "greatsword", "戟": "halberd",
    "骑枪": "cavalry lance", "长剑": "longsword", "巨锤": "maul", "钉头锤": "morningstar",
    "长矛": "pike", "刺剑": "rapier", "弯刀": "scimitar", "短剑": "shortsword",
    "三叉戟": "trident", "战镐": "war pick", "战锤": "warhammer", "鞭": "whip",
    "吹箭筒": "blowgun", "手弩": "hand crossbow", "重弩": "heavy crossbow",
    "长弓": "longbow", "火铳": "musket", "手铳": "flintlock pistol",
}

# 职业（竖版概念图）
CLASSES = [
    ("barbarian", "野蛮人", "a towering barbarian warrior in furs, raging, gripping a massive greataxe, tribal tattoos, wild long hair, muscles tensed, battle cry"),
    ("bard", "吟游诗人", "a charismatic bard playing an ornate lute, flamboyant decorated outfit, magical music notes swirling in golden light, charming performer"),
    ("cleric", "牧师", "a devout cleric in shining holy vestments holding a glowing mace, holy symbol radiating golden light, divine aura, prayerful stance"),
    ("druid", "德鲁伊", "a druid robed in leaves and moss, wooden staff, glowing nature magic, leaves and vines swirling, antlered hood, forest guardian"),
    ("fighter", "战士", "a veteran fighter in scarred plate armor, sword and shield ready, battle-hardened, determined stance, experienced warrior"),
    ("monk", "武僧", "a martial monk in simple flowing robes, balanced combat stance, ki energy glowing around fists, shaved head, calm focused eyes"),
    ("paladin", "圣武士", "a noble paladin in gleaming plate armor, glowing holy sword raised, cape flowing, divine light from above, righteous champion"),
    ("ranger", "游侠", "a ranger in green leather with hood and bow, accompanied by a wolf companion, forest path, keen eyes tracking prey, wilderness scout"),
    ("rogue", "游荡者", "a hooded rogue in dark leather, twin daggers, crouched in shadow, stealthy, lockpicks and tools, cunning grin, alley skulker"),
    ("sorcerer", "术士", "a sorcerer with wild arcane energy crackling from hands, glowing eyes, flowing robes, raw innate magic spiraling, charismatic arcane power"),
    ("warlock", "邪术师", "a warlock in dark robes, eerie pact magic, eldritch green energy from an outstretched hand, otherworldly patron sigil, mysterious occultist"),
    ("wizard", "法师", "a wise wizard in starry robes and pointed hat, ancient tome open, arcane runes and spell circles, long white beard, tower study"),
]

# 种族（竖版概念图）
RACES = [
    ("human", "人类", "a versatile human adventurer in practical traveling gear, determined expression, neutral hero"),
    ("elf", "精灵", "a graceful tall elf with pointed ears, slender elegant features, fine flowing robes, long hair, ethereal fair beauty, forest elf"),
    ("dwarf", "矮人", "a stout bearded dwarf warrior in heavy armor, braided beard, battle-hardened, stocky and strong, mountain clan"),
    ("halfling", "半身人", "a cheerful barefoot halfling with curly hair, small and nimble, rustic vest, slingshot at hip"),
    ("dragonborn", "龙裔", "a proud dragonborn with draconic scales, snout and horns, breath weapon glowing in throat, tall scaly humanoid, dragon heritage"),
    ("gnome", "侏儒", "a small cheerful gnome with a big nose and tinkering goggles, inventive, oversized hat, curious bright eyes"),
    ("half-elf", "半精灵", "a half-elf combining human and elven features, slightly pointed ears, balanced and adaptable, attractive and capable"),
    ("half-orc", "半兽人", "a powerful half-orc with greenish skin and tusks, scarred, muscular, fierce determined glare, tribal warrior"),
    ("tiefling", "提夫林", "a tiefling with reddish skin, curved horns and a spaded tail, fiendish heritage, glowing golden eyes, exotic infernal beauty"),
]

# 法术学派（徽记）
SPELL_SCHOOLS = [
    ("abjuration", "防护", "abjuration school emblem, a glowing protective ward shield with runes, shimmering barrier of protective magic, blue-white barrier"),
    ("conjuration", "咒法", "conjuration school emblem, objects and creatures materializing from a swirling portal vortex, summoning gateway"),
    ("divination", "占卜", "divination school emblem, a glowing all-seeing eye in a triangle, visions and foresight, scrying crystal orb"),
    ("enchantment", "附魔", "enchantment school emblem, spiraling hypnotic charm runes, mind-affecting purple magic, entrancing spiral"),
    ("evocation", "塑能", "evocation school emblem, explosive elemental energy — fire, lightning and ice erupting outward, raw destructive power"),
    ("illusion", "幻术", "illusion school emblem, shimmering mirage and duplicate shapes, bending light, ethereal fake images"),
    ("necromancy", "死灵", "necromancy school emblem, a skull wreathed in sickly green spectral flames, bone and spirit magic, deathly green glow"),
    ("transmutation", "变化", "transmutation school emblem, matter transforming — stone to gold, shifting forms, alchemical change swirl"),
]

# 骰子
DICE = [
    ("d20_hero", "d20主图", "a single glowing red twenty-sided die (d20) resting on a dark oak table, dramatic spotlight, the number 20 facing up, fantasy tabletop rpg dice, sharp focus"),
    ("polyhedral_set", "全套骰子", "a complete set of seven polyhedral dice — d4 d6 d8 d10 d12 d20 and percentile — scattered on a weathered dungeon map, dice set, parchment and candle"),
    ("rolling_d20", "投掷d20", "a d20 die tumbling mid-roll across a wooden table, motion blur, scattered character sheets, tense moment of a roll"),
]

# 场景（宽屏）
SCENES = [
    ("tavern", "酒馆", "a cozy medieval fantasy tavern interior, roaring fireplace, wooden tables, adventurers drinking, warm candlelight, bard performing"),
    ("dungeon", "地牢", "a dark stone dungeon corridor, mossy bricks, dripping water, torchlit, bones and cobwebs, ominous shadows, ancient prison"),
    ("forest", "森林", "an ancient enchanted forest path, towering old trees, shafts of golden sunlight, fireflies, misty depth, mossy glade"),
    ("dungeon_gate", "地下城大门", "a massive ancient stone dungeon gate carved with runes, torches flanking, fog rolling out, forbidding entrance to a ruined stronghold"),
    ("dragon_lair", "龙穴", "a vast dragon's lair cavern filled with gold coin hoard, bones, a colossal red dragon sleeping on treasure, embers glowing"),
    ("mountain_ruin", "山顶遗迹", "crumbling ancient ruins atop a misty mountain peak, broken pillars and arches, sunrise breaking through clouds, isolated shrine"),
    ("village", "村庄", "a peaceful medieval fantasy village with thatched cottages, dirt paths, smoke from chimneys, green hills, sheep grazing"),
    ("port_town", "港口城镇", "a bustling fantasy harbor town, sailing ships at dock, seagulls, warehouses and taverns, morning sun, busy waterfront"),
]

# 封面（宽屏大图）
COVERS = [
    ("cover_banner", "项目主横幅",
     "an epic fantasy banner illustration, a party of diverse dnd heroes — warrior, wizard, rogue, cleric — silhouetted against a dramatic dragon-filled sky, grand adventure, sweeping vista, heroic composition, no text"),
    ("ai_dm_theme", "AI DM 主题图",
     "a mysterious hooded dungeon master figure behind a wooden table scattered with polyhedral dice and open rulebooks, glowing arcane runes and a faint holographic map of a fantasy world, candlelight, mystical AI storyteller, no text"),
]

# 钱币
COINS = [
    ("coins_pile", "钱币堆", "a scattered pile of fantasy coins — copper, silver, electrum, gold and platinum — of varying sizes and engravings, on a velvet cloth, treasure hoard coins, gleaming metallics"),
]


# ──────────────────────────────────────────────────────────────────────────
# 任务数据结构
# ──────────────────────────────────────────────────────────────────────────
@dataclass
class Job:
    category: str
    name: str            # 英文文件名 slug
    cn_name: str         # 中文名（展示用）
    prompt: str
    size: str
    out_path: Path
    status: str = "pending"   # pending / ok / failed / skipped
    url: str = ""
    attempts: int = 0
    error: str = ""
    elapsed: float = 0.0


def slugify(s: str) -> str:
    """中文名 → 安全文件名（保留中文，去掉路径非法字符）。"""
    return re.sub(r'[\\/:*?"<>|]+', "_", s).strip()


def build_catalog() -> list[Job]:
    """从 aidm 数据 + 主题清单构建全部任务。"""
    jobs: list[Job] = []

    def add(category: str, name: str, cn_name: str, prompt: str, size: str) -> None:
        out = OUT_ROOT / category / f"{slugify(name)}.png"
        jobs.append(Job(category, name, cn_name, prompt, size, out))

    # —— 数据驱动：状态/护甲/武器 ——
    # 直接 import（已通过 PYTHONPATH=src 可见 aidm 包）
    sys.path.insert(0, str(SRC_ROOT))
    from aidm.engine import conditions as cond_mod  # noqa: E402
    from aidm.data import equipment as equip_mod   # noqa: E402

    for cn in sorted(cond_mod.CONDITIONS):
        en = COND_EN.get(cn, cn)
        desc = COND_DESC.get(cn, f"the {en} condition depicted as a status effect")
        add("conditions", en, cn,
            f"an icon depicting the {en} condition: {desc}, single character centered, "
            f"status effect emblem, clean dark gradient background, glowing magical aura, "
            f"icon illustration, {STYLE}", SIZE_ICON)

    for cn in equip_mod.ARMOR:
        en = ARMOR_EN.get(cn, cn)
        add("armor", en, cn,
            f"a suit of {en} on an armored stand, detailed fantasy {en}, "
            f"centered item illustration, clean dark gradient background, soft rim lighting, "
            f"equipment icon, {STYLE}", SIZE_ICON)

    for cn in equip_mod.WEAPONS:
        en = WEAPON_EN.get(cn, cn)
        add("weapons", en, cn,
            f"a {en}, detailed fantasy {en} weapon, centered, diagonal angle, "
            f"clean dark gradient background, soft rim lighting, weapon icon illustration, "
            f"{STYLE}", SIZE_ICON)

    # —— 主题扩充 ——
    for en, cn, desc in CLASSES:
        add("classes", en, cn,
            f"full body character concept art of a {desc}, centered portrait composition, "
            f"plain atmospheric background, character design sheet, {STYLE}", SIZE_PORTRAIT)

    for en, cn, desc in RACES:
        add("races", en, cn,
            f"full body character concept art of a {desc}, centered portrait composition, "
            f"plain atmospheric background, character design sheet, {STYLE}", SIZE_PORTRAIT)

    for en, cn, desc in SPELL_SCHOOLS:
        add("spell-schools", en, cn,
            f"a magical emblem symbol representing the {en} school of magic: {desc}, "
            f"centered sigil on dark background, glowing arcane energy, emblem icon, "
            f"{STYLE}", SIZE_ICON)

    for en, cn, desc in DICE:
        add("dice", en, cn, f"{desc}, {STYLE}", SIZE_ICON)

    for en, cn, desc in SCENES:
        add("scenes", en, cn,
            f"{desc}, wide cinematic landscape, atmospheric depth, establishing shot, "
            f"{STYLE}", SIZE_SCENE)

    for en, cn, desc in COINS:
        add("coins", en, cn, f"{desc}, {STYLE}", SIZE_ICON)

    for en, cn, desc in COVERS:
        add("cover", en, cn,
            f"{desc}, wide cinematic banner composition, epic scale, {STYLE}", SIZE_COVER)

    return jobs


# ──────────────────────────────────────────────────────────────────────────
# 读取 API key
# ──────────────────────────────────────────────────────────────────────────
def load_api_key() -> str:
    # 环境变量优先（可临时换 key 而不改 .env，例如某 key 日额度耗尽时换一个）
    env = os.environ.get("SENSEAUDIO_KEY")
    if env:
        return env
    if not ENV_FILE.exists():
        raise SystemExit(f"未找到 .env：{ENV_FILE}")
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("key="):
            return line.split("=", 1)[1].strip()
    raise SystemExit(".env 中未找到 key= ...")


# ──────────────────────────────────────────────────────────────────────────
# 单任务：异步生成 + 轮询 + 下载
# ──────────────────────────────────────────────────────────────────────────
async def submit_task(client: httpx.AsyncClient, api_key: str, job: Job) -> str:
    """提交异步生成，返回 task_id。"""
    body = {"model": MODEL, "prompt": job.prompt, "size": job.size}
    r = await client.post(ASYNC_EP, headers=_auth(api_key), json=body)
    if r.status_code != 200:
        raise RuntimeError(f"submit HTTP {r.status_code}: {r.text[:300]}")
    data = r.json()
    tid = data.get("task_id")
    if not tid:
        raise RuntimeError(f"submit 无 task_id: {data}")
    return tid


async def generate_sync(client: httpx.AsyncClient, api_key: str, job: Job) -> str:
    """同步生成：POST /v1/image/sync，直接返回图片 URL。

    比异步+轮询快且稳——异步端点在并发提交时易排队挂起；同步是直接请求-响应，
    生成期间服务端保持连接，完成即返回 URL，无 task 队列。
    """
    body = {"model": MODEL, "prompt": job.prompt, "size": job.size}
    r = await client.post(SYNC_EP, headers=_auth(api_key), json=body)
    if r.status_code != 200:
        raise RuntimeError(f"sync HTTP {r.status_code}: {r.text[:300]}")
    data = r.json()
    url = data.get("url")
    if not url:
        raise RuntimeError(f"sync 无 url: {data}")
    return url


async def poll_task(client: httpx.AsyncClient, api_key: str, task_id: str,
                    label: str = "") -> str:
    """轮询直到 completed/failed，返回图片 URL 或抛错。

    慢生成时每 ~20s 打印心跳，保持 stdout 活跃，避免无输出看门狗杀进程
    （表现为 exit 1 无 traceback）。
    """
    deadline = time.time() + POLL_TIMEOUT
    t0 = time.time()
    last_beat = t0
    while time.time() < deadline:
        r = await client.get(PENDING_EP, headers=_auth(api_key),
                             params={"task_id": task_id})
        if r.status_code != 200:
            raise RuntimeError(f"poll HTTP {r.status_code}: {r.text[:300]}")
        data = r.json()
        status = data.get("status")
        if status == "completed":
            url = data.get("url")
            if not url:
                raise RuntimeError(f"completed 但无 url: {data}")
            return url
        if status == "failed":
            raise RuntimeError(f"生成失败: {data.get('error_message', data)}")
        if label and time.time() - last_beat >= 20:
            print(f"    ... {label} 生成中 ({int(time.time()-t0)}s)", flush=True)
            last_beat = time.time()
        await asyncio.sleep(POLL_INTERVAL)
    raise RuntimeError(f"轮询超时（{POLL_TIMEOUT:.0f}s）task_id={task_id}")


async def download_image(client: httpx.AsyncClient, url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = await client.get(url)
    if r.status_code != 200:
        raise RuntimeError(f"download HTTP {r.status_code}")
    dest.write_bytes(r.content)


def _auth(api_key: str) -> dict:
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


async def run_one(client: httpx.AsyncClient, api_key: str, sem: asyncio.Semaphore,
                  job: Job, stop_event: asyncio.Event | None = None) -> Job:
    # 可恢复：已存在则跳过
    if job.out_path.exists() and job.out_path.stat().st_size > 0:
        job.status = "skipped"
        return job

    # 配额/速率熔断已跳闸：不再提交新任务（已成功产物不受影响）
    if stop_event is not None and stop_event.is_set():
        job.status = "skipped"
        job.error = "skipped: quota breaker tripped"
        return job

    async with sem:
        # 取得信号后再确认一次（排队期间熔断器可能已跳闸）
        if stop_event is not None and stop_event.is_set():
            job.status = "skipped"
            job.error = "skipped: quota breaker tripped"
            return job
        t0 = time.time()
        last_err = ""
        for attempt in range(1, MAX_ATTEMPTS + 1):
            job.attempts = attempt
            try:
                print(f"    → {job.name} 生成中…", flush=True)
                url = await generate_sync(client, api_key, job)
                await download_image(client, url, job.out_path)
                job.url = url
                job.status = "ok"
                job.elapsed = time.time() - t0
                return job
            except Exception as e:  # noqa: BLE001
                msg = repr(e)
                # 触达使用限制/余额不足：跳闸，停止提交新任务（重试只会加重速率压力）
                if stop_event is not None and LIMIT_RE.search(msg):
                    stop_event.set()
                    job.status = "failed"
                    job.error = f"quota/limit breaker: {msg[:140]}"
                    job.elapsed = time.time() - t0
                    return job
                last_err = f"attempt{attempt}: {e!r}"
                await asyncio.sleep(1.5 * attempt)
        job.status = "failed"
        job.error = last_err
        job.elapsed = time.time() - t0
    return job


# ──────────────────────────────────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────────────────────────────────
async def main_async(jobs: list[Job], concurrency: int, api_key: str,
                     max_ok: int = 0) -> list[Job]:
    sem = asyncio.Semaphore(concurrency)
    stop_event = asyncio.Event()           # 配额/速率熔断器（也用于日额度护栏）
    total = len(jobs)
    done = 0
    ok_new = 0                             # 本次新生成成功数（不含已存在跳过）
    results: list[Job] = [None] * total  # type: ignore[list-item]

    async def _wrap(i: int, job: Job) -> None:
        nonlocal done, ok_new
        res = await run_one(client, api_key, sem, job, stop_event)
        done += 1
        if res.status == "ok":
            ok_new += 1
            # 日额度护栏：新生成达到上限即跳闸，其余跳过（留余量避免撞 300/天墙）
            if max_ok and ok_new >= max_ok:
                stop_event.set()
        results[i] = res
        mark = {"ok": "✓", "skipped": "↻", "failed": "✗"}[res.status]
        extra = f" ({res.attempts}次, {res.elapsed:.0f}s)" if res.status == "ok" else \
                (f" {res.error[:80]}" if res.status == "failed" else " 已存在/护栏跳过")
        print(f"[{done}/{total}] {res.category}/{res.name} {mark}{extra}", flush=True)

    # 同步生成期间服务端保持连接（实测 31–124s），read 需 ≥ 最大生成时间；
    # connect/write/pool 收紧。生成期间靠并发错峰输出，无长时间静默。
    timeout = httpx.Timeout(connect=15.0, read=240.0, write=60.0, pool=10.0)
    async with httpx.AsyncClient(base_url=API_BASE, timeout=timeout) as client:
        await asyncio.gather(*(_wrap(i, j) for i, j in enumerate(jobs)))
    return results


def write_manifest(jobs: list[Job]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "model": MODEL,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(jobs),
        "summary": {
            s: sum(1 for j in jobs if j.status == s)
            for s in ("ok", "skipped", "failed")
        },
        "items": [
            {
                "category": j.category, "name": j.name, "cn_name": j.cn_name,
                "file": j.out_path.relative_to(PROJECT_ROOT).as_posix()
                if j.out_path.exists() else None,
                "size": j.size, "status": j.status, "url": j.url,
                "attempts": j.attempts, "error": j.error, "prompt": j.prompt,
            }
            for j in jobs
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                             encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="批量生成 D&D 项目图片（SenseAudio）")
    ap.add_argument("--concurrency", type=int, default=CONCURRENCY)
    ap.add_argument("--categories", default="", help="仅跑指定分类，逗号分隔")
    ap.add_argument("--dry-run", action="store_true", help="只打印任务清单")
    ap.add_argument("--limit", type=int, default=0, help="限制任务数（测试用，0=全部）")
    args = ap.parse_args()

    api_key = load_api_key()
    jobs = build_catalog()

    if args.categories:
        want = {c.strip() for c in args.categories.split(",")}
        jobs = [j for j in jobs if j.category in want]
    if args.limit:
        jobs = jobs[:args.limit]

    print(f"模型: {MODEL}  并发: {args.concurrency}  任务数: {len(jobs)}")
    if args.dry_run:
        for j in jobs:
            print(f"  [{j.category}] {j.name} ({j.cn_name}) {j.size}")
        return

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    results = asyncio.run(main_async(jobs, args.concurrency, api_key))
    write_manifest(results)

    ok = sum(1 for j in results if j.status == "ok")
    sk = sum(1 for j in results if j.status == "skipped")
    fail = [j for j in results if j.status == "failed"]
    print("\n==== 统计 ====")
    print(f"成功 {ok}  跳过(已存在) {sk}  失败 {len(fail)}")
    if fail:
        print("失败列表：")
        for j in fail:
            print(f"  [{j.category}] {j.name} — {j.error[:120]}")
    print(f"清单: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
