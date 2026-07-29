"""检索质量评测 — 量化 LlamaIndex hybrid(BM25+向量) 的 recall。

评测集：55 条查询 + 期望命中的规则ID集合（每条查询可能有多个等价正确答案）。
指标：recall@k = 期望ID是否出现在 top-k 内。
"""

from __future__ import annotations

import sys

# (查询, 期望命中的规则ID集合)
EVAL: list[tuple[str, set[str]]] = [
    # ── 徒手/擒抱/推撞 ──
    ("摔绊 推撞 让目标倒地", {"R-GLS-034", "R-ADD-011"}),
    ("擒抱 怎么逃脱", {"R-GLS-036", "R-GLS-049"}),
    ("推撞 shove 力量运动", {"R-GLS-034", "R-ADD-011"}),
    ("擒抱 grapple 速度变为0", {"R-GLS-049", "R-ADD-010"}),
    ("徒手打击 unarmed 力量调整值", {"R-GLS-034"}),
    # ── 状态 ──
    ("倒地 prone 起立 5尺", {"R-GLS-055"}),
    ("中毒 poisoned 攻击劣势", {"R-GLS-054"}),
    ("力竭 exhaustion 6级死亡", {"R-GLS-047"}),
    ("失能 incapacitated 无法动作", {"R-GLS-050"}),
    ("麻痹 paralyzed 5尺重击", {"R-GLS-052"}),
    ("昏迷 unconscious 倒地", {"R-GLS-058"}),
    ("隐形 invisible 攻击优势", {"R-GLS-051"}),
    ("石化 petrified 状态", {"R-GLS-053"}),
    ("恐慌 frightened 劣势", {"R-GLS-056"}),
    ("魅惑 charmed 不能攻击", {"R-GLS-057"}),
    ("束缚 restrained 速度0", {"R-GLS-056"}),
    # ── 攻击/战斗 ──
    ("攻击检定 d20 命中 AC", {"R-CMB-017", "R-CHK-001"}),
    ("天然20 必出 重击 暴击", {"R-CMB-022", "R-CMB-029"}),
    ("天然1 必失 失手", {"R-CMB-023"}),
    ("重击 伤害骰翻倍", {"R-CMB-029", "R-GLS-002"}),
    ("先攻 initiative 突袭 敏捷", {"R-CMB-002", "R-GLS-009"}),
    ("借机攻击 opportunity 反应", {"R-CMB-025"}),
    ("掩护 cover +2 +5", {"R-CMB-015", "R-QCK-005", "R-GLS-007"}),
    ("近战5尺远程攻击劣势", {"R-CMB-028"}),
    ("回合 移动 动作 附赠动作", {"R-CMB-001", "R-GLS-001"}),
    ("多重攻击 extra attack", {"R-CMB-011"}),
    ("远程攻击 射程 正常 远距离劣势", {"R-CMB-014"}),
    ("双手武器 精通 伤害骰", {"R-CMB-030"}),
    # ── 检定/DC ──
    ("d20检定 三步 掷骰 调整值", {"R-CHK-001"}),
    ("属性检定 ability check DC", {"R-CHK-010"}),
    ("豁免检定 saving throw", {"R-CHK-011"}),
    ("熟练加值 等级 +2 +3", {"R-CHK-015"}),
    ("属性调整值 公式 floor (score-10)/2", {"R-CHK-024"}),
    ("计算DC公式 8+属性+熟练", {"R-DM-002", "R-SPL-021"}),
    ("被动检定 被动察觉 10+调整值", {"R-DM-012"}),
    ("难度等级 DC 10 15 20", {"R-CHK-009"}),
    ("优势 劣势 d20 额外骰子", {"R-CHK-005"}),
    ("百分骰 d100 百分比", {"R-CHK-026"}),
    # ── 伤害/HP/死亡 ──
    ("伤害掷骰 武器 属性调整值", {"R-DMG-001"}),
    ("抗性 减半 易伤 翻倍", {"R-DMG-003"}),
    ("抗性 易伤 免疫 结算顺序", {"R-DMG-005", "R-QCK-002", "R-DMG-003"}),
    ("生命值 HP 扣除", {"R-DMG-007"}),
    ("临时生命值 先扣除", {"R-DMG-009"}),
    ("死亡豁免 1d20 3次 天然1双败", {"R-DMG-017", "R-GLS-020"}),
    ("治疗 恢复 上限", {"R-DMG-020"}),
    ("伤害类型 钝击 穿刺 挥砍", {"R-DMG-002"}),
    ("暴击 额外伤害骰 叠加", {"R-CMB-029"}),
    # ── 施法 ──
    ("专注 concentration 受伤 DC", {"R-GLS-013", "R-SPL-020"}),
    ("法术豁免DC 8 施法属性", {"R-SPL-021", "R-DM-002"}),
    ("法术位 消耗 环阶", {"R-SPL-002"}),
    ("仪式施法 ritual 10分钟", {"R-GLS-040"}),
    ("法术攻击 命中 法术豁免", {"R-SPL-021"}),
    ("反制法术 counterspell 反应", {"R-SPL-005"}),
    # ── 休息/恢复 ──
    ("短休 1小时 生命骰", {"R-GLS-014"}),
    ("长休 8小时 恢复 法术位", {"R-GLS-015", "R-SPL-003", "R-ADD-016"}),
    # ── 装备/AC ──
    ("AC计算 护甲 敏捷 盾牌", {"R-ITM-004", "R-GLS-006"}),
    ("护甲表 轻甲 中甲 重甲", {"R-ITM-003"}),
    ("盾牌 AC+2", {"R-ITM-004"}),
    # ── 移动/探索 ──
    ("速度 行走 攀爬 游泳", {"R-GLS-031"}),
    ("困难地形 额外移动消耗", {"R-GLS-032"}),
    ("跳跃 立定跳远 助跑跳远", {"R-GLS-079"}),
    # ── 环境危险 ──
    ("坠落伤害 高度 钝击", {"R-GLS-059"}),
    ("溺水 窒息 耗尽空气", {"R-GLS-060"}),
    ("极端温度 力竭 豁免", {"R-GLS-061"}),
    # ── 综合/玩家用语 ──
    ("怎么计算我的攻击能不能打中", {"R-CMB-017", "R-CHK-001"}),
    ("被摔绊了会怎样", {"R-GLS-055", "R-GLS-034"}),
    ("豁免DC怎么算", {"R-DM-002", "R-CHK-012"}),
    ("被打到0血会死吗", {"R-DMG-017", "R-DMG-007"}),
]


def _ids(results: list[dict]) -> list[str]:
    return [r.get("tag", "") for r in results]


def run_eval(search_fn, k_list=(3, 5), label="") -> dict:
    """search_fn(query, limit) -> list[payload]. 返回各 k 的 recall + 逐条命中。"""
    hits = {k: 0 for k in k_list}
    details = []
    for query, expected in EVAL:
        res = search_fn(query, limit=max(k_list))
        ids = _ids(res)
        row = {"query": query, "expected": expected}
        for k in k_list:
            topk = set(ids[:k])
            ok = bool(topk & expected)
            row[f"hit@{k}"] = ok
            if ok:
                hits[k] += 1
        row["retrieved_top3"] = ids[:3]
        details.append(row)
    n = len(EVAL)
    print(f"\n=== {label} ===")
    for k in k_list:
        print(f"recall@{k}: {hits[k]}/{n} = {hits[k]/n:.0%}")
    print("逐条:")
    for d in details:
        flag = "✓" if d["hit@3"] else "✗"
        print(f"  {flag} {d['query'][:24]:24} 期望={sorted(d['expected'])} 命中@3={d['retrieved_top3']}")
    return {"label": label, "n": n, "recall": {k: hits[k] / n for k in k_list}, "details": details}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    from . import hybrid, indexer  # hybrid 稍后实现

    # 确保 RULE_SPEC 语料已索引
    try:
        indexer.search_spec("测试", limit=1)
    except Exception:
        from . import parse_rulespec
        indexer.index_chunks(parse_rulespec.parse_rulespec(), "dnd_rule_spec")

    print(f"评测集: {len(EVAL)} 条查询")
    print("评测 bge-small 纯向量 vs LlamaIndex hybrid(BM25+向量)")
    run_eval(indexer.search_spec, label="纯向量(bge-small)")
    run_eval(hybrid.search_spec_hybrid, label="LlamaIndex hybrid(BM25+向量RRF)")
