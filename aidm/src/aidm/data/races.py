"""种族数据表 — 10 个可扮演种族。

纯数据 + 少量计算。每条记录标注出处。
数据来源: topics/玩家手册2024/角色起源/种族/<种族>.htm
"""

from __future__ import annotations


# creature_type 生物类型 / size 体型选项 / speed 基础速度(尺) /
# darkvision 黑暗视觉(尺,0表示无) / traits 特殊特质列表 /
# subraces 子族/血系(可空)
RACES = {
    # ── 人类 ──────────────────────────────────────────────
    "人类": {
        "creature_type": "类人",
        "size": ["中型", "小型"],   # 选择此种族时决定
        "speed": 30,
        "darkvision": 0,
        "traits": [
            "适应力Resourceful：每当你完成长休时，你都会获得英雄激励。",
            "技能Skillful：你获得一项自选的技能的熟练。",
            "多才多艺Versatile：你获得一项自选的起源专长。",
        ],
        "subraces": None,
    },
    # ── 矮人 ──────────────────────────────────────────────
    "矮人": {
        "creature_type": "类人",
        "size": ["中型"],
        "speed": 30,
        "darkvision": 120,
        "traits": [
            "黑暗视觉Darkvision：120尺。",
            "矮人体魄Dwarven Resilience：毒素伤害抗性；为避免/结束中毒状态所做的豁免检定具有优势。",
            "矮人刚毅Dwarven Toughness：生命值上限+1，此后每次升级时再加1。",
            "石中精妙Stonecunning：附赠动作获得60尺震颤感知，持续10分钟；次数=熟练加值，长休后重获。",
        ],
        "subraces": None,
    },
    # ── 精灵 ──────────────────────────────────────────────
    "精灵": {
        "creature_type": "类人",
        "size": ["中型"],
        "speed": 30,
        "darkvision": 60,
        "traits": [
            "黑暗视觉Darkvision：60尺。",
            "精灵血系Elven Lineage：从血系表格中选择其一（卓尔/高等/木精灵），获得1级好处，3级与5级习得更高级法术。选择智力、感知或魅力作为施法属性。",
        ],
        "subraces": ["卓尔", "高等精灵", "木精灵"],
    },
    # ── 半身人 ────────────────────────────────────────────
    "半身人": {
        "creature_type": "类人",
        "size": ["小型"],
        "speed": 30,
        "darkvision": 0,
        "traits": [
            "勇气Brave：在避免或结束恐慌状态进行的豁免时具有优势。",
            "半身人灵巧Halfling Nimbleness：可穿越比你大1级的生物所在空间，但不能在其内停下。",
            "幸运Lucky：当你在D20检定中的d20掷出1时，你可以重新掷骰，但必须使用重骰的结果。",
            "天生善匿Naturally Stealthy：在有比你体型至少大1级的生物遮蔽你的情况下，你也可以执行躲藏动作。",
        ],
        "subraces": None,
    },
    # ── 侏儒 ──────────────────────────────────────────────
    "侏儒": {
        "creature_type": "类人",
        "size": ["小型"],
        "speed": 30,
        "darkvision": 60,
        "traits": [
            "黑暗视觉Darkvision：60尺。",
            "侏儒狡黠Gnome Cunning：你进行的智力、感知、魅力豁免检定均具有优势。",
            "侏儒血系Gnome Lineage：从森林侏儒或岩石侏儒中选择其一。选择智力、感知或魅力作为施法属性。",
        ],
        "subraces": ["森林侏儒", "岩石侏儒"],
    },
    # ── 歌利亚 ────────────────────────────────────────────
    "歌利亚": {
        "creature_type": "类人",
        "size": ["中型"],
        "speed": 35,
        "darkvision": 0,
        "traits": [
            "巨人先祖Giant Ancestry：你是巨人的后裔。选择以下好处之一——云之远迹、火之燃烧、霜之刺骨、山之翻撞、石之坚韧、岚之暴鸣。使用次数=熟练加值，长休后重获。",
            "大型形态Large Form：从第5级开始，可用附赠动作将体型变为大型，持续10分钟；力量检定具有优势，速度+10尺。使用后直至长休才能再次使用。",
            "身强力壮Powerful Build：为让自己结束受擒状态所进行的属性检定具有优势；计算载重时视为大一级的体型。",
        ],
        "subraces": None,
    },
    # ── 兽人 ──────────────────────────────────────────────
    "兽人": {
        "creature_type": "类人",
        "size": ["中型"],
        "speed": 30,
        "darkvision": 120,
        "traits": [
            "激昂冲锋Adrenaline Rush：你能用附赠动作执行疾走动作，并获得等同于熟练加值的临时生命值。次数=熟练加值，短休或长休后重获。",
            "黑暗视觉Darkvision：120尺。",
            "坚韧不屈Relentless Endurance：当你生命值降至0而没有立即死亡时，可以改为使生命值降至1。此特质一经使用，直至完成长休你都无法再次使用。",
        ],
        "subraces": None,
    },
    # ── 提夫林 ────────────────────────────────────────────
    "提夫林": {
        "creature_type": "类人",
        "size": ["中型", "小型"],   # 选择此种族时决定
        "speed": 30,
        "darkvision": 60,
        "traits": [
            "黑暗视觉Darkvision：60尺。",
            "邪魔遗赠Fiendish Legacy：从深渊/幽冥/炼狱遗赠表格中选择其一，获得1级好处，3级与5级习得更高级法术。选择智力、感知或魅力作为施法属性。",
        ],
        "subraces": ["深渊遗赠", "幽冥遗赠", "炼狱遗赠"],
    },
    # ── 龙裔 ──────────────────────────────────────────────
    "龙裔": {
        "creature_type": "类人",
        "size": ["中型"],
        "speed": 30,
        "darkvision": 60,
        "traits": [
            "龙族血统Draconic Ancestry：从龙族血统表格中选择一种龙（白/黑/绿/蓝/红/黄铜/赤铜/青铜/银/金），决定吐息武器和伤害抗性的伤害类型。",
            "吐息武器Breath Weapon：每当你在自己回合内进行攻击动作时，可将其中一次攻击替换为释放魔法性能量，覆盖15尺锥状区域或30尺长5尺宽线状区域。区域内生物须进行敏捷豁免检定（DC=8+体质调整值+熟练加值）。豁免失败受到1d10伤害（5级2d10，11级3d10，17级4d10），成功则受到一半伤害。使用次数=熟练加值，长休后重获全部。",
            "伤害抗性Damage Resistance：根据你龙族血统所选龙种，获得对应伤害类型的伤害抗性。",
            "黑暗视觉Darkvision：60尺。",
        ],
        "subraces": None,
    },
    # ── 阿斯莫 ────────────────────────────────────────────
    "阿斯莫": {
        "creature_type": "类人",
        "size": ["中型", "小型"],   # 选择此种族时决定
        "speed": 30,
        "darkvision": 60,
        "traits": [
            "天界抗性Celestial Resistance：光耀伤害与暗蚀伤害的抗性。",
            "黑暗视觉Darkvision：60尺。",
            "治愈之手Healing Hands：以一个魔法动作触碰一个生物，掷数量等于熟练加值枚d4，该生物恢复等于掷骰结果之和的生命值。使用后直到完成长休为止都不能再次使用。",
            "光辉掌者Light Bearer：习得光亮术Light戏法。其施法属性为魅力。",
            "天启Celestial Revelation：到达3级时获得用附赠动作变身的能力。每次使用选择天堂飞翼/内耀辉光/死灵环绕之一。使用后直到完成长休为止都不能再次使用。",
        ],
        "subraces": None,
    },
}


def get_race(name: str) -> dict:
    """取种族条目。"""
    if name not in RACES:
        raise KeyError(f"未知种族 {name!r}，可选: {list(RACES)}")
    return RACES[name]


def has_trait(race_name: str, trait_en: str) -> bool:
    """检查种族是否拥有指定特性（按英文特性名做子串匹配）。

    数据来源中的特性字符串形如「矮人刚毅Dwarven Toughness：……」，
    含中文名+英文名，故以英文片段做子串（不区分大小写）匹配。

    出处: topics/玩家手册2024/角色起源/种族/<种族>.htm
    """
    if race_name not in RACES:
        return False
    needle = trait_en.lower()
    return any(needle in str(trait).lower() for trait in RACES[race_name]["traits"])


def dwarven_toughness(race_name: str) -> bool:
    """矮人刚毅 Dwarven Toughness：生命值上限+1，此后每次升级时再加1。

    规则: R-DMG-007（1级HP/升级HP）
    出处: topics/玩家手册2024/角色起源/种族/矮人.htm
    """
    return has_trait(race_name, "Dwarven Toughness")


def race_names() -> list[str]:
    """返回全部种族名（按定义顺序）。"""
    return list(RACES)


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    assert len(RACES) == 10, f"应有10个种族，实有{len(RACES)}"
    # 关键数值抽查（出处: 各种族 .htm）
    assert RACES["矮人"]["darkvision"] == 120
    assert RACES["精灵"]["darkvision"] == 60
    assert RACES["半身人"]["darkvision"] == 0
    assert RACES["歌利亚"]["speed"] == 35
    assert RACES["人类"]["speed"] == 30
    # 子族
    assert RACES["精灵"]["subraces"] == ["卓尔", "高等精灵", "木精灵"]
    assert RACES["人类"]["subraces"] is None
    # 所有种族速度合理
    for name, data in RACES.items():
        assert 25 <= data["speed"] <= 40, f"{name} 速度异常"
        assert data["creature_type"] == "类人"
    # 种族特性检测  出处: 矮人.htm(矮人刚毅)
    assert dwarven_toughness("矮人") is True
    assert has_trait("矮人", "Stonecunning") is True
    assert dwarven_toughness("人类") is False
    assert has_trait("人类", "Resourceful") is True
    assert has_trait("精灵", "Dwarven Resilience") is False
    assert dwarven_toughness("不存在的种族") is False
    print("[races] 自检通过 ✓")


if __name__ == "__main__":
    _self_test()
