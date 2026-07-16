"""子职业数据表（自动生成）。

来源: topics/玩家手册2024/角色职业/<职业>/<子职业>.htm
子职业总数: 48
生成脚本: aidm/scripts/extract_subclasses.py
"""

# flake8: noqa: E501

_SUBCLASSES_LIST: list[dict] = [
    # ── 吟游诗人: 勇气学院 ──
    {
        'name': "勇气学院",
        'en_name': "College of Valor",
        'class_name': "吟游诗人",
        'flavor': "颂歌赞唱旧英杰",
        'features': [
            {'level': 3, 'name': "战斗激励Combat", 'en_name': "Inspiration", 'description': "你可以运用你的巧言来改变战斗的走向。一名拥有你的诗人激励骰的生物可以从下列选项中选择一种效应来使用诗人骰。 防御Defense。 当这名生物被一次攻击检定命中时，该生物能够以反应掷诗人激励骰并将骰值加到对抗这次攻击检定的AC中，这可能使这次攻击变为失手。 进攻Offense。 这名生物以一次攻击检定命中一名目标后，它可以立即投掷诗人激励骰，并将骰值加到这次攻击对这名目标造成的伤害中。"},
            {'level': 3, 'name': "战争训练", 'en_name': "Martial Training", 'description': "你获得军用武器熟练以及中甲和盾牌 的护甲受训。 此外，你施展吟游诗人法术列表中的法术时，可以使用简易或军用武器作为法器。"},
            {'level': 6, 'name': "额外攻击", 'en_name': "Extra Attack", 'description': "当你在自己的回合执行 攻击 动作时，你可以发动两次攻击而非一次。此外，你可以将额外攻击中的一次，替换为施展一道施法时间为一动作的戏法。"},
            {'level': 14, 'name': "战斗魔法", 'en_name': "Battle Magic", 'description': "在你施展一道施法时间为一动作的法术后，你能够以一个附赠动作，使用一把武器发动一次攻击。"},
        ],
    },
    # ── 吟游诗人: 舞蹈学院 ──
    {
        'name': "舞蹈学院",
        'en_name': "College of Dance",
        'class_name': "吟游诗人",
        'flavor': "舞步节律谐宇宙",
        'features': [
            {'level': 3, 'name': "炫目舞步", 'en_name': "Dazzling Footwork", 'description': "未着装护甲且未持用盾牌期间，你获得以下增益： 大舞蹈家Dance Virtuoso。 你进行的任何有关舞蹈的魅力（ 表演 ）检定均具有 优势 。 无甲防御Unarmored Defense。 你的基础护甲等级等于10＋你的敏捷调整值＋你的魅力调整值。 灵巧打击Agile Strikes。 当你在一次动作、附赠动作或反应中消耗了诗人激励使用次数时，作为该动作、附赠动作或反应的一部分，你可以发动..."},
            {'level': 6, 'name': "鼓舞之移", 'en_name': "Inspring Movement", 'description': "当一名你可见的敌人位于你5尺内结束它的回合时，你能够以反应消耗一次诗人激励使用次数，移动至多等于你速度一半的距离。此时，位于你30尺内的一名盟友（由你选择）也可以使用他的反应来移动至多等于他速度一半的距离。 此特性进行的移动不会引发 借机攻击 。"},
            {'level': 6, 'name': "协同舞步", 'en_name': "Tandem Footwork", 'description': "当你投掷 先攻 时，若你未陷入 失能 状态，你可以消耗一次诗人激励使用次数，投掷诗人激励骰，令你与位于你30尺内的每个能听见或看见你的盟友进行的先攻检定获得等于该骰值的加值。"},
            {'level': 14, 'name': "引导闪避", 'en_name': "Leading Evasion", 'description': "当你受到一个允许你进行敏捷豁免来只承受一半伤害的效应影响时，你在豁免成功时不受伤害，豁免失败时只承受一半伤害。若位于你5尺内的其他生物同样需要进行这次敏捷豁免，你可以令他们也享受到此特性的增益。 若你陷入失能状态，你无法使用此特性。"},
        ],
    },
    # ── 吟游诗人: 逸闻学院 ──
    {
        'name': "逸闻学院",
        'en_name': "College of Lore",
        'class_name': "吟游诗人",
        'flavor': "博观觅识深钻法",
        'features': [
            {'level': 3, 'name': "附赠熟练", 'en_name': "Bonus Proficiencies</STRONG></FONT> <BR>你获得三项由你选择的技能的熟练。</p>   <p><STRONG><FONT color=#800000>3级：语出惊人 Cutting Words", 'description': "你学会了如何运用你的妙语连珠来超自然地打断敌人、分散注意亦或是削弱他人的自信心和行动力。当一名你可见的位于你60尺内的生物进行伤害掷骰、成功于一次属性检定或攻击检定时，你能够以反应消耗一次诗人激励使用次数，并掷诗人激励骰，然后从该生物的掷骰结果中减去诗人骰的骰值，这将降低其造成的伤害或可能使这次检定的成功变为失败。"},
            {'level': 6, 'name': "魔法探秘", 'en_name': "Magical Discoveries", 'description': "你习得两道自选法术。这些法术可以从牧师、德鲁伊或法师的法术列表中单独或组合选择（这些职业的法术列表见其职业章节）。你选择的法术必须是戏法或是你拥有对应环阶法术位的法术，你拥有的法术位如吟游诗人特性表中所示。 你始终准备着你选择的这些法术。每当你获得一个吟游诗人等级时，你可以将其中一个法术替换为另一个满足上述要求的法术。"},
            {'level': 14, 'name': "超凡技艺", 'en_name': "Peerless Skill", 'description': "当你进行一次属性检定或攻击检定并在检定中失败时，你可以消耗一次诗人激励使用次数，投掷诗人激励骰，并将掷骰结果加到d20中，这可能使这次检定的失败变为成功。若检定仍然失败，将不会被消耗诗人激励次数。"},
        ],
    },
    # ── 吟游诗人: 魅心学院 ──
    {
        'name': "魅心学院",
        'en_name': "College of Glamour",
        'class_name': "吟游诗人",
        'flavor': "织魔作惑妖精术",
        'features': [
            {'level': 3, 'name': "惑心魔法", 'en_name': "Beguiling Magic", 'description': "你始终准备着法术 魅惑类人Charm Person 和 镜影术Mirror Image 。 此外，在你使用法术位施展一道惑控或幻术学派的法术后，你可以立即使一名位于你60尺内的你可见的生物进行一次感知豁免检定，对抗你的施法DC。豁免失败则目标陷入 魅惑 或 恐慌 状态（由你选择），持续1分钟。目标在其每个回合结束时，可以重新进行该豁免，成功则其身上的效应提前结束。 此增益一经使用，直至完成 ..."},
            {'level': 3, 'name': "灵感织衣", 'en_name': "Mantle of Insipration", 'description': "你可以将妖精魔法织入歌曲亦或是舞蹈，为他人献上满满的活力。以一个附赠动作，你可以消耗一次诗人激励使用次数，并掷诗人激励骰，从位于你60尺内的其他生物中选择任意生物，数量至多等于你魅力调整值（至少选择一名），每个被选中的生物获得等于两倍该诗人骰骰值的 临时生命值 ，然后每名生物均可以使用自己的反应立即移动至多等于自己速度的距离，这次移动不会引发 借机攻击 。"},
            {'level': 6, 'name': "威仪作锦", 'en_name': "Mantle of Majesty", 'description': "你始终准备着法术 命令术Command 。 以一个附赠动作，你无需法术位地施展命令术，然后你将获得超凡脱俗的容貌，持续1分钟或在你 专注 终止时提前结束。在此期间，你能够以一个附赠动作，无需法术位地施展法术命令术。 任何因你而陷入 魅惑 状态的生物在进行对抗你以此特性施展的命令术时，其豁免检定自动失败。 此特性一经使用，直至完成 长休 你都无法再次使用。你也可以消耗一个三环及以上的法术位（无..."},
            {'level': 14, 'name': "不破威仪", 'en_name': "Unbreakable Majesty", 'description': "以一个附赠动作，你可以魔法性地呈现出庄严的姿态，持续1分钟或在你陷入失能状态时结束。在此期间，任何生物在一个回合中的攻击检定首次命中你时，攻击者必须通过一次对抗你施法DC的魅力豁免检定，否则这次攻击将因畏惧你的威仪而变得畏缩并失手。 一旦你呈现出这庄严的姿态，直至完成 短休 或 长休 你都无法再如此做。"},
        ],
    },
    # ── 圣武士: 古贤之誓 ──
    {
        'name': "古贤之誓",
        'en_name': "Oath of the Ancients",
        'class_name': "圣武士",
        'flavor': "护生驱暗济世界",
        'features': [
            {'level': 3, 'name': "自然之怒", 'en_name': "Nature's  Wrath<BR></STRONG></FONT>以一个<FONT color=#008000><STRONG>魔法</STRONG></FONT>动作，你可以消耗一次引导神力次数，唤出灵体藤蔓缠绕周围的生物。你选择你能看到的位于你15尺内的任意数量生物，令其必须通过一次<STRONG>力量</STRONG>豁免，失败陷入<FONT color=#008000><STRONG>束缚</STRONG></FONT>状态1分钟。被束缚的生物可以在其回合结束时重复豁免，成功则不再受到此效应影响。</p>      <p><STRONG><FONT color=#800000>3级：古贤之誓法术 Oath of the  Ancients  Spells<BR>", 'description': "你誓言具有的魔法使你始终准备着特定的法术。当你到达古贤之誓法术表中特定的圣武士等级时，你就始终准备着表中对应的法术。"},
            {'level': 7, 'name': "守御灵光", 'en_name': "Aura of  Warding", 'description': "强大的远古魔法眷顾着你，以至于在你身边形成了一道神秘的结界，阻挡着来自物质位面外的能量；你和位于你守护灵光内的盟友获得对暗蚀，心灵以及光耀伤害的抗性。"},
            {'level': 15, 'name': "不灭哨卫", 'en_name': "Undying  Sentinel", 'description': "当你生命值降至0，但尚未被直接杀死时，可以选择让你的生命值降到1而不是0，然后你再恢复相当于你圣武士等级三倍的生命值。该能力一经使用，直至完成长休你都无法再次使用。 此外，你不会因为魔法效应而衰老，你的外表也会停止老去。"},
            {'level': 20, 'name': "上古斗士", 'en_name': "Elder  Champion", 'description': "以一个附赠动作，你可以用原力盈满你的守护灵光，灵光获得下列的增益。持续1分钟或直到你将之提前结束（无需动作）。此特性一经使用，直至完成长休你都无法再次使用。你也可以消耗一个五环法术位（无需动作）重置此特性的使用权。"},
        ],
    },
    # ── 圣武士: 复仇之誓 ──
    {
        'name': "复仇之誓",
        'en_name': "Oath of Vengeance",
        'class_name': "圣武士",
        'flavor': "铁面无情伏妖魔",
        'features': [
            {'level': 3, 'name': "复仇之誓法术", 'en_name': "Oath of Vengeance Spells", 'description': "你誓言具有的魔法使你始终准备着特定的法术。当你到达复仇之誓法术表中特定的圣武士等级时，你就始终准备着表中对应的法术。"},
            {'level': 3, 'name': "仇敌誓言", 'en_name': "Vow of  Enmity", 'description': "当你执行 攻击 动作时，你可以消耗一次你的引导神力次数，对一个你能看见的位于你30尺内的生物立下仇敌誓言。你在接下来1分钟内，对该生物的攻击检定具有 优势 。 如果在誓言结束前，该生物的生命值就降至0，你可以将誓言的目标换为另一个你可见的位于你30尺的生物（无需动作）。"},
            {'level': 7, 'name': "坚韧复仇", 'en_name': "Relentless  Avenger", 'description': "你超自然的专注力使你可以拦截敌人撤退。你以借机攻击中命中一个生物时，可以将其速度降为0，直到当前回合结束为止。且你在该攻击后立刻移动至多相当于你速度一半的距离，本次移动是原反应的一部分，且不引发借机攻击。"},
            {'level': 15, 'name': "复仇之魂", 'en_name': "Soul of  Vengeance", 'description': "受你仇敌誓言影响的生物在发动一次攻击以后，无论是否命中，只要其位于你的触及内，你就能够立即以反应对其进行一次近战攻击。"},
            {'level': 20, 'name': "复仇天使", 'en_name': "Avenging  Angel", 'description': "以一个附赠动作，你可获得下列的增益。持续10分钟或直到你将之提前结束（无需动作）。此特性一经使用，直至完成长休你都无法再次使用。你也可以消耗一个五环法术位（无需动作）重置此特性的使用权。"},
        ],
    },
    # ── 圣武士: 奉献之誓 ──
    {
        'name': "奉献之誓",
        'en_name': "Oath of Devotion",
        'class_name': "圣武士",
        'flavor': "当仁不让知行正",
        'features': [
            {'level': 3, 'name': "奉献之誓法术", 'en_name': "Oath of Devotion Spells", 'description': "你誓言具有的魔法使你始终准备着特定的法术。当你到达奉献之誓法术表中特定的圣武士等级时，你就始终准备着表中对应的法术。"},
            {'level': 3, 'name': "圣洁武器", 'en_name': "Sacred Weapon", 'description': "当你执行攻击动作时，你可以消耗一次你的引导神力次数，为你持握的一把近战武器注入正能量。随后10分钟或你再次使用此特性为止，你使用该武器进行的攻击检定可以加上你的魅力调整值（至少为 +1），且每次命中时可以选择是造成正常伤害或者是光耀伤害。 该武器同时提供半径20尺的 明亮光照 以及额外20尺 微光光照 。 你可以提前终止此效应（无需动作）。当你不再携带这把武器，此效应同样终止。"},
            {'level': 7, 'name': "奉献灵光", 'en_name': "Aura of  Devotion", 'description': "你与位于你守护灵光内的盟友具有魅惑免疫。陷入魅惑的盟友进入灵光时，该状态在灵光内会暂时无效。"},
            {'level': 15, 'name': "卫护斩", 'en_name': "Smite of  Protection", 'description': "你现在能让魔法斩击散发出保护性的能量。每当你施展至圣斩时，直到你的下个回合开始为止，你的灵光获得以下增益：身处你的守护灵光期间，你和你的盟友具有半身掩护。"},
            {'level': 20, 'name': "至圣光轮", 'en_name': "Holy  Nimbus", 'description': "以一个附赠动作，你可以用圣力盈满你的守护灵光，灵光获得下列的增益，持续10分钟或直到你将之提前结束（无需动作）。此特性一经使用，直至完成长休你都无法再次使用。你也可以消耗一个五环法术位（无需动作）重置此特性的使用权。"},
        ],
    },
    # ── 圣武士: 荣耀之誓 ──
    {
        'name': "荣耀之誓",
        'en_name': "Oath of Glory",
        'class_name': "圣武士",
        'flavor': "砥身励行蜚声英",
        'features': [
            {'level': 3, 'name': "鼓舞斩", 'en_name': "Inspiring  Smite", 'description': "当你施展至圣斩后，你可以立即消耗一次你的引导神力次数，使30尺内由你选择的生物或你自身获得临时生命值。这些生物共获得的临时生命值等同于2d8+你的圣武士等级，你可以为其随意分配这些临时生命值。"},
            {'level': 3, 'name': "荣耀之誓法术", 'en_name': "Oath of Glory  Spells", 'description': "你誓言具有的魔法使你始终准备着特定的法术。当你到达荣耀之誓法术表中特定的圣武士等级时，你就始终准备着表中对应的法术。"},
            {'level': 3, 'name': "绝伦健将", 'en_name': "Peerless  Athlete<BR>", 'description': "以一个附赠动作，你可以消耗一次引导神力次数以增强运动能力。1小时内，你在力量（ 运动 ）检定和敏捷（ 特技 ）检定上获得优势，且你跳远和跳高的距离增加10尺（你依然为此正常消耗移动力）。"},
            {'level': 7, 'name': "迅捷灵光", 'en_name': "Aura of  Alacrity<BR>", 'description': "你的速度提升10尺。 此外，每个在自己回合第一次进入你守护灵光内的盟友，或在其内开始回合的盟友，速度提升10尺，直到其下个回合结束为止。"},
            {'level': 15, 'name': "辉煌防御", 'en_name': "Glorious  Defense", 'description': "你能在防御中转守为攻，对敌人发起突然袭击。当你或位于你10尺内一个你可见的生物成为一次攻击的目标并被击中时，你可以用反应使其获得一定的AC加值，此举可能使该次攻击改为失手。此加值等同于你的魅力调整值（至少为+1）。若该次攻击失手，且攻击者在你的武器触及范围内，你可以用武器对其进行一次攻击，这次攻击视为反应的一部分。 你能使用此特性的次数为你的魅力调整值（最少一次）。你在完成一次长休后重获所有..."},
            {'level': 20, 'name': "现世传说", 'en_name': "Living  Legend", 'description': "你能够使自己有能力实现传奇的壮举——无论是确有此事，抑或夸大其词。以一个附赠动作，你获得下列的增益。持续10分钟或直到你将之提前结束（无需动作）。此特性一经使用，直至完成长休你都无法再次使用。你也可以消耗一个五环法术位（无需动作）重置此特性的使用权。"},
        ],
    },
    # ── 德鲁伊: 大地结社 ──
    {
        'name': "大地结社",
        'en_name': "Circle of the Land",
        'class_name': "德鲁伊",
        'flavor': "自然世界，颂之以系",
        'features': [
            {'level': 3, 'name': "大地结社法术Circle of the Land", 'en_name': "Spells", 'description': "当你完成一次长休时，选择一种地形：荒漠、极地，温带或热带。当你到达下列表中特定的德鲁伊等级时，你就始终准备着表中对应的法术。"},
            {'level': 3, 'name': "大地之援Land's", 'en_name': "Aid", 'description': "以一个魔法动作，你可以消耗一次荒野变形使用次数并且选择距你60尺内的一点。给予活力的繁花和吸取生命的荆刺在以那一点为源点的10尺半径球状区域同时生出。在该区域内每个你所选择的生物必须进行一次对抗你法术豁免DC的体质豁免，豁免失败时生物受到2d6暗蚀伤害，豁免成功时受到半数伤害。此外，区域内你所选择的一名生物恢复2d6生命值。 当你到达特定的德鲁伊等级时，伤害和治疗量会提升1d6：10级（3d..."},
            {'level': 6, 'name': "自然恢复Natural", 'en_name': "Recovery", 'description': "你可以施展一个你以结社法术特性准备的一环及以上法术，而无须消耗法术位，并且你必须在完成一次长休后才能再次这么做。 此外，当你结束一次短休时，你可以选择恢复消耗的法术位。法术环阶的总和等于你德鲁伊职业等级的一半（向上取整），且不能是六环或更高环阶的法术位。比如说，作为一位6级德鲁伊，你可以恢复环阶总和最多为3的法术位。你可以恢复一个三环法术位，或者一个二环和一个一环法术位，或者三个一环法术位。..."},
            {'level': 10, 'name': "自然守御Nature's", 'en_name': "Ward", 'description': "你免疫中毒状态，并且你具有和你目前在结社法术特性中选择的土地相关的伤害类型的抗性，如自然守御表格所示。"},
            {'level': 14, 'name': "自然庇护Nature's", 'en_name': "Sanctuary<BR>", 'description': "以一个魔法动作，你可以消耗一次荒野变形次数在距你120尺内的地面上制造出15尺立方区域的灵体丛林和藤蔓。它们持续存在1分钟或直到你陷入失能状态或死去。在该区域内，你和你的盟友获得 半身掩护 ，你的盟友还会获得你 自然守御 特性提供的伤害抗性。 以一个附赠动作，你可以将立方区域在你的120尺内移动最多60尺距离。"},
        ],
    },
    # ── 德鲁伊: 星辰结社 ──
    {
        'name': "星辰结社",
        'en_name': "Circle of the Stars",
        'class_name': "德鲁伊",
        'flavor': "群星隐秘，求索驭力",
        'features': [
            {'level': 3, 'name': "星图", 'en_name': "Star  Map", 'description': "作为你天文学研究的一部分，你创造了一张星图。它是一个微型物体，可以用作你施展德鲁伊法术时的法器。你通过在星图列表上掷骰或选择一个来确定它的形态。 当你持握这件星图时，你视作总是准备着 神导术Guidance 和 光导箭Guiding bolt 这两个法术，并且你可以施展 光导箭 而无需消耗法术位。其次数等同于你的感知调整值（最小为1），当你完成一次长休时，你重获全部已消耗的使用次数。 如果你..."},
            {'level': 3, 'name': "星耀形态", 'en_name': "Starry  Form", 'description': "以一个附赠动作，你可以消耗一次荒野变形特性使用次数以呈现一个星耀形态，而非变化为野兽形态。 处于星耀形态期间，你保留你的游戏数据，但你的身体变得明亮；你的关节星光熠熠并有如星图一般由亮线连接。这一形态散发出10尺半径的明亮光照以及其外10尺的微光光照。这一形态持续10分钟。如果你解除它（无需动作）、失能、死亡、或再次使用此特性，它就会提前结束。 每当你化身星耀形态时，你选择以下在星座之一在你..."},
            {'level': 6, 'name': "宇宙预兆", 'en_name': "Cosmic  Omen", 'description': "每当你完成一次长休时，你可以参照你的星图来寻找预兆。此时，掷一枚骰子。直到你完成下一次长休为止，你获得一个基于此掷骰结果奇偶性的特殊反应能力。 吉兆Weal（偶数）。 当你周围30尺内的一个可见生物将要进行一次d20检定时，你可以使用你的反应来投一个d6，并将结果加入到检定结果中。 凶兆Woe（奇数）。 当你周围30尺内的一个可见生物将要进行一次d20检定时，你可以使用你的反应来投一个d6，..."},
            {'level': 10, 'name': "闪烁星座", 'en_name': "Twinkling  Constellations", 'description': "你的星耀形态星座增强了。射手座和圣杯座中的1d8都变成了2d8，而在巨龙座激活期间，你将获得20尺的飞行速度，并且可以悬浮。 此外，每个你的回合开始时，若此时你处于在星耀形态下，你可以更改当前身上闪耀的星座。"},
            {'level': 14, 'name': "灿若繁星", 'en_name': "Full of  Stars", 'description': "处于星耀形态期间，你的身体部分无实质化，使你获得钝击、穿刺与挥砍伤害的抗性。"},
        ],
    },
    # ── 德鲁伊: 月亮结社 ──
    {
        'name': "月亮结社",
        'en_name': "Circle of the Moon",
        'class_name': "德鲁伊",
        'flavor': "荒野卫士，身化兽躯",
        'features': [
            {'level': 3, 'name': "结社形态Circle", 'en_name': "Forms", 'description': "你学会了如何在使用荒野变形的同时引导月之魔力，增益自身的力量，你获得以下增益： 挑战等级Challenge Rating。 你的荒野变形形态的最大挑战等级现在等于你德鲁伊等级的三分之一（向下取整）。 护甲等级Armor Class。 只要你仍处于荒野变形形态，如果13+你的感知调整值加起来高于野兽的护甲等级，你的护甲等级等于你13+你的感知调整值。 临时生命值Temporary Hit Po..."},
            {'level': 3, 'name': "月亮结社法术Circle of the Moon", 'en_name': "Spells", 'description': "当你到达月亮结社法术表中特定的德鲁伊等级时，你就始终准备着表中对应的法术。 此外，你可以在荒野变形下施展这些法术。"},
            {'level': 6, 'name': "进阶结社形态Improved Circle", 'en_name': "Forms<BR>", 'description': "荒野变形期间，你获得以下增益。 月耀辉光Lunar Radiance。 你在荒野变形形态下的每次攻击可以造成普通的伤害或光耀伤害。由你在每次攻击命中时选择。 强化韧性Increased Toughness。 你将你的感知调整值加到你的体质豁免结果当中。"},
            {'level': 10, 'name': "月光飞步Moonlight", 'en_name': "Step<BR>", 'description': "你能以魔法传送自身，在一道月光中重新出现。以一个附赠动作，你传送最多30尺到一处你能看见的未被占据的空间，并且你在这个回合结束前进行的下一次攻击具有优势。 你可以使用该特性的次数等于你的感知调整值（至少1次），并且你在结束一次长休后重获全部已消耗的使用次数。你也能消耗一个二环或更高的法术位来恢复一次使用次数（无需任何动作）。"},
            {'level': 14, 'name': "月辉形态Lunar", 'en_name': "Form<BR>", 'description': "月之力量充盈着你的身体，让你获得以下增益： 月耀炽光Improved Lunar Radiance。 一回合一次，你可以对一次荒野变形下的攻击命中的一名目标额外造成2d10光耀伤害。 月辉同行Shared Moonlight。 当你使用月光飞步时，你还能传送另一个自愿的生物。该生物必须在你的10尺内，并且你将它传送到你出现点的10尺内的一个你能看见的未被占据空间中。"},
        ],
    },
    # ── 德鲁伊: 海洋结社 ──
    {
        'name': "海洋结社",
        'en_name': "Circle of the Sea",
        'class_name': "德鲁伊",
        'flavor': "海潮风暴，一体同心",
        'features': [
            {'level': 3, 'name': "海洋结社法术Circle of the Sea", 'en_name': "Spells", 'description': "当你到达海洋结社法术表中特定的德鲁伊等级时，你就始终准备着表中对应的法术。"},
            {'level': 3, 'name': "瀚海之怒Wrath of the", 'en_name': "Sea", 'description': "以一个附赠动作，你可以消耗一次你的荒野变形次数来在自己周围显现出海浪形态的5尺光环。光环会持续存在10分钟。当你解除它（无需任何动作）、再度显现光环或陷入失能时，它会提前结束。 当你显现出光环时，以及在之后的回合中以一个附赠动作，你可以选择另一个在你光环范围内你可见的生物。该生物必须成功通过一次对抗你的法术豁免DC的体质豁免，否则受到寒冷伤害，如果该生物是大型或更小体型，它会被从你身边推离至..."},
            {'level': 6, 'name': "水生亲和Aquatic", 'en_name': "Affinity<BR>", 'description': "你的瀚海之怒创造的光环范围提升至10尺。 此外，你获得等于你速度的游泳速度。"},
            {'level': 10, 'name': "风暴降生Stormborn", 'en_name': "", 'description': "你的瀚海之怒特性在激活时获得两项额外增益： 飞行Flight。 你获得等于你的速度的飞行速度。 抗性Resistance。 你获得对寒冷、闪电和雷鸣伤害的抗性。"},
        ],
    },
    # ── 战士: 勇士 ──
    {
        'name': "勇士",
        'en_name': "Champion",
        'class_name': "战士",
        'flavor': "勇冠三军彰英豪",
        'features': [
            {'level': 3, 'name': "精通重击", 'en_name': "Improved  Critical<BR>", 'description': "你使用武器或 徒手打击 进行的攻击检定在d20中掷出19或20时即可造成重击。"},
            {'level': 3, 'name': "运动健将", 'en_name': "Remarkable  Athlete</STRONG></FONT><BR>得益于你平日的体育锻炼，你在先攻检定和力量（运动）检定中具有优势。<BR>此外，当你造成一次重击时，你可立即移动至多等于你速度一半的距离，这次移动不会引发借机攻击。</p>    <p><STRONG><FONT color=#800000>7级：额外战斗风格 Additional Fighting  Style<BR>", 'description': "你获得另一个自选的战斗风格专长。"},
            {'level': 10, 'name': "勇战英豪", 'en_name': "Heroic  Warrior", 'description': "战斗的艰难只会使你朝胜利更进一步。在战斗中，若你回合开始时没有英雄激励，你可以获得之。"},
            {'level': 15, 'name': "高效重击", 'en_name': "Superior  Critical", 'description': "你使用武器或徒手打击进行的攻击检定在d20中掷出18-20时即可造成重击。"},
            {'level': 18, 'name': "百折不挠", 'en_name': "Survivor", 'description': "你持续战斗的能力达到巅峰，赋予了你以下好处： 蔑视死亡Defy Death。 你进行死亡豁免时具有优势。此外，若你在死亡豁免上投出了18~20时，都会获得相当于投出20的好处。 英气风发Heroic Rally。 你的回合开始时，若你已浴血且拥有至少1生命值，你恢复5＋你的体质调整值的生命值。"},
        ],
    },
    # ── 战士: 奥法骑士 ──
    {
        'name': "奥法骑士",
        'en_name': "Eldritch Knight",
        'class_name': "战士",
        'flavor': "奥法遍身附剑戟",
        'features': [
            {'level': 3, 'name': "施法", 'en_name': "Spellcasting", 'description': "你学会了如何施展法术。施法规则见第七章。下文将详述如何将这些规则应用于奥法骑士。 戏法Cantrips。 你知晓两道你选择的法师戏法。推荐选择 冷冻射线Ray of Frost 和 电爪Shocking Grasp 。 每当你获得一个战士等级时，你都能从此特性的戏法中选择其一替换为另一道你所选择的法师戏法。 当你的战士等级到达10级时，你能另选一道法师戏法并习得。 法术位Spell Slot..."},
            {'level': 3, 'name': "战争联结", 'en_name': "War  Bond", 'description': "你习得一种让你和你的武器建立魔法联结的仪式。你执行持续一小时的仪式，且可在短休时进行。整个仪式过程中武器必须在你的触及范围内，直至仪式结束前，该武器必须一直在你触手可及的范围内，以完成联结。若该武器已与另一名战士建立联结，或是一把已被他人同调的魔法物品，仪式则会失败。 联结建立后，只要你不处于失能状态，使用联结武器时就不会被缴械。如果联结武器与你处于同一位面，则你可以用一个附赠动作使其立即传..."},
            {'level': 7, 'name': "战争魔法", 'en_name': "War  Magic<BR>", 'description': "当你在自己回合执行攻击动作时，你可以将该动作攻击中的一次攻击替换为施展一道施法时间为动作的你的法师戏法。"},
            {'level': 10, 'name': "奥法打击", 'en_name': "Eldritch  Strike<BR>", 'description': "你习得用武器攻击削弱敌人对你法术抵抗能力的方法。当你使用一把武器命中一个生物后，直到你的下个回合结束为止，该生物在对抗你法术所进行的下一次豁免检定中具有劣势。"},
            {'level': 15, 'name': "奥能冲锋", 'en_name': "Arcane  Charge<BR>", 'description': "你可以在使用动作如潮时传送至多30尺至一个你能看到的未被占据的空间。你可以在使用动作如潮提供的额外动作之前或之后进行传送。"},
            {'level': 18, 'name': "精通战争魔法", 'en_name': "Improved War  Magic<BR>", 'description': "当你在自己回合执行攻击动作时，你可以该动作攻击中的两次攻击替换为施展一道施法时间为动作，环阶为一环或二环的你的法师法术。"},
        ],
    },
    # ── 战士: 战斗大师 ──
    {
        'name': "战斗大师",
        'en_name': "Battle Master",
        'class_name': "战士",
        'flavor': "战技百般昭武艺",
        'features': [
            {'level': 3, 'name': "卓越战技", 'en_name': "Combat  Superiority<BR>", 'description': "你的战斗技巧在战场上接受了磨砺，你习得战技并获得一种名为卓越骰的特殊骰。 战技Maneuvers。 你从“战技项”中习得三种自选战技（详见后文）。许多战技能够以某种方式增幅你的攻击，而你在每次攻击时只能应用一次战技。 你在第7、第10和第15级时均习得两种自选的新战技。习得新战技时，你还可以额外替换一个已经习得的战技。 卓越骰Superiority Dice。 你拥有四个d8卓越骰。卓越骰一..."},
            {'level': 3, 'name': "战争学者", 'en_name': "Student of  War", 'description': "你选择一种工匠工具并获得其熟练。此外，你选择一项战士1级可用的技能，并获得该技能的熟练。"},
            {'level': 7, 'name': "料敌机先", 'en_name': "Know Your  Enemy", 'description': "以一个附赠动作，你可以获知一名位于你30尺内你可见的生物的长处和短处。你知晓该生物是否具有抗性、免疫或易伤，若有，则你知晓其具体内容是什么。 此特性一经使用，直至完成长休你都无法再次使用。你也可以消耗1粒卓越骰（无需动作）重置此特性的使用权。"},
            {'level': 10, 'name': "精通战技", 'en_name': "Improved Combat  Superiority", 'description': "你的卓越骰变为d10。"},
            {'level': 15, 'name': "坚韧", 'en_name': "Relentless", 'description': "每回合一次，当你使用一项战技时，你可以不消耗卓越骰，而是掷d8并使用结果作为代替。"},
            {'level': 18, 'name': "究极战技", 'en_name': "Ultimate Combat  Superiority", 'description': "你的卓越骰变为d12。"},
        ],
    },
    # ── 战士: 灵能武士 ──
    {
        'name': "灵能武士",
        'en_name': "Psi Warrior",
        'class_name': "战士",
        'flavor': "灵能庇体显神威",
        'features': [
            {'level': 3, 'name': "灵能力量", 'en_name': "Psionic  Power</STRONG></FONT><BR>你内心拥有一个灵能力量的源泉。这股能量表现为灵能骰，它是你从此子职中获得的可消耗能力。灵能武士灵能骰表展示了你在达到特定战士等级后的灵能骰大小与数量。</p>    <p><STRONG>灵能武士灵能骰Psi Warrior Energy Dice</STRONG>  </p> <TABLE style=\"BORDER-COLLAPSE: collapse; TEXT-ALIGN: center\" cellSpacing=0 cellPadding=2 border=0> <TR><TD width=100><STRONG>战士等级</STRONG></TD><TD width=60><STRONG>骰面</STRONG></TD><TD width=60><P align=center><STRONG>数量</STRONG></P></TD> <TR bgColor=#eeeeee><TD>3</TD><TD>D6</TD><TD><P align=center>4</P></TD> <TR><TD>5</TD><TD>D8</TD><TD><P align=center>6</P></TD></TR> <TR bgColor=#eeeeee><TD>9</TD><TD>D8</TD><TD><P align=center>8</P></TD> <TR><TD>11</TD><TD>D10</TD><TD><P align=center>8</P></TD></TR> <TR bgColor=#eeeeee><TD>13</TD><TD>D10</TD><TD><P align=center>10</P></TD> <TR><TD>17</TD><TD>D12</TD><TD><P align=center>12</P></TD></TR> </TABLE>    <p>此子职中所有需要使用灵能骰的特性只能使用你从该子职获得的灵能骰。你在使用某些能力时需要消耗灵能骰，如异能描述中所述，如果某个异能在你的灵能骰全部消耗完后还需要你使用一个灵能骰，你就不能使用该异能。<BR>你可以在完成短休时重获一枚已消耗的灵能骰，完成长休时重获所有已消耗的灵能骰。<BR><b>庇护力场Protective Field。</b>当你或者另一个位于你30尺内的你可见的生物受到伤害时，你可以执行一个反应来消耗一枚灵能骰，对其降低等同于灵能骰骰出的数值加你的智力调整值的伤害（最少1点），如同你创造了一面瞬间的念力盾牌。<BR><b>灵能打击Psionic Strike。</b>你可以用灵能驱动你的武器。每个你的回合一次，当你用武器命中并对位于你30尺范围内的目标造成伤害时，你可以立即消耗一枚灵能骰，对目标造成等同于灵能骰骰出的数值加你的智力调整值的力场伤害。<BR><b>念力控物Telekinetic Movement。</b>你可以用意念移动一个物体或生物。以一个魔法动作，你选中一个除你以外的自愿生物或一个至多大型的未固定物件。如果你可以看见目标且目标在你30尺范围内，你就可以将其移动至多30尺至另一个对你可见的未占据空间内。另外，如果目标是一个微型物件，你可以自由给出或收回手中。<BR>此异能一经使用，直至完成短休或长休你都无法再次使用。你也可以消耗一枚灵能骰（无需动作）重置此异能的使用权。</p>    <p><STRONG><FONT color=#800000>7级：念力精通 Telekinetic  Adept", 'description': "你已经掌握了使用念力异能的新方式，如下所示。 灵力跃动Psi-Powered Leap。 以一个附赠动作，你获得等同于两倍速度的飞行速度，直到本回合结束为止。一旦你执行了此附赠动作，直到你完成一次短休或长休为止你都不能再次使用它。你也可以消耗一枚灵能骰（无需动作）来再次使用该异能。 念力突刺Telekinetic Thrust。 当你使用灵能打击对一个目标造成伤害时，你可以迫使目标进行一次力..."},
            {'level': 10, 'name': "意念守护", 'en_name': "Guarded  Mind", 'description': "你获得心灵伤害的抗性。此外，如果你在你的回合开始时处于魅惑或者恐慌状态，你可以消耗一个灵能骰（无需动作）并结束自己身上全部造成这些状态的效应。"},
            {'level': 15, 'name': "力场壁垒", 'en_name': "Bulwark of  Force", 'description': "你可以使用念力庇护你自己和其他人。以一个附赠动作，包括你在内，你可以选择数个位于你30尺范围内的生物，其数量等同于你的智力调整值（最少1个）。每个被选中的生物将在1分钟内视为处于半身掩护中，该保护将会在你陷入失能状态时提前结束。 此特性一经使用，直至完成长休你都无法再次使用。你也可以消耗一枚灵能骰（无需动作）重置此特性的使用权。"},
        ],
    },
    # ── 术士: 时械术法 ──
    {
        'name': "时械术法",
        'en_name': "",
        'class_name': "术士",
        'flavor': "引导寰宇的秩序之力",
        'features': [
            {'level': 3, 'name': "时械法术Clockwork", 'en_name': "Spells", 'description': "当你到达时械法术表中特定的术士等级时，你就始终准备着表中对应的法术。"},
            {'level': 3, 'name': "归复平衡", 'en_name': "Restore  Balance<BR>", 'description': "你与绝对秩序之位面的联系使你能重整混沌的时刻。当你60尺内一个你可见的生物即将带着优势或是劣势进行一次检定时，你可以用反应使这次检定免受优势或劣势的影响。 你可以使用此能力的次数等同于你的魅力调整值（至少1次）。当你完成一次长休时，你重获全部已消耗的使用次数。"},
            {'level': 6, 'name': "律令之壁", 'en_name': "Bastion of  Law<BR>", 'description': "你可以利用世界的均衡之力为一个生物激发闪烁的秩序之盾。以一个魔法动作，你可以消耗1~5点术法点来创造出一个环绕你或30尺内的一个可见生物的魔法屏障。屏障具有等同于你所消耗术法点数量的d8骰。当被守护的生物受到伤害时，其可以消耗任意数量的这些d8骰，投掷它们，并使该伤害减少掷出结果合计的数值。 此屏障将一直保持存在，直到你完成一次长休或直至你再次使用该特性。"},
            {'level': 14, 'name': "序列意识", 'en_name': "Trance of  Order", 'description': "你获得了将你的意识和机械境无尽的计算达成同步的能力。以一个附赠动作，你可以在1分钟内进入此种状态。在此期间，对你进行的攻击免受优势的影响，且每当你进行一次d20检定时，你可以将d20掷出的9或以下的骰值视为10。 此特性一经使用，直至完成长休你都无法再次使用。你也可以消耗5点术法点（无需动作）重置此特性的使用权。"},
            {'level': 18, 'name': "时械矩阵", 'en_name': "Clockwork  Cavalcade", 'description': "你召唤出秩序的精魂以抹除周遭的混乱。以一个魔法动作，你在以你为源点的30尺立方空间范围内召唤出一些精魂。这些精魂看起来像是魔冢或你选择的其他构装，其没有实体也无法被摧毁，并在消失前使立方范围内产生以下效应。此特性一经使用，直到完成一次长休前都不能再次使用。你也可以消耗7点术法点（无需动作）以恢复此特性的使用次数。 治愈Heal。 精魂合计提供至多恢复100生命值，由你随意分配给范围内任意数量..."},
        ],
    },
    # ── 术士: 狂野术法 ──
    {
        'name': "狂野术法",
        'en_name': "Wild Magic Sorcery",
        'class_name': "术士",
        'flavor': "释放混沌魔力",
        'features': [
            {'level': 3, 'name': "狂野魔法浪涌", 'en_name': "Wild Magic  Surge", 'description': "你施法时会释放出未经塑造的魔法浪涌。一回合一次，你每次消耗法术位施展一道术士法术后，可以立刻骰一次d20。如果你骰出20，则在狂野魔法浪涌表上掷骰以确定随机魔法效应。 若掷出的魔法效应是一道法术，该法术因其过于狂野而无法受你的超魔法影响。"},
            {'level': 3, 'name': "混乱之潮", 'en_name': "Tide of  Chaos", 'description': "你可以驾驭机运的力量，以使一次自身的D20检定具有优势。你必须在掷出d20之前决定是否使用此特性。此特性一经使用，在你完成长休后才能再次被使用。 此特性在你使用法术位施展术士法术时也会恢复可用，但此时你会自动于狂野魔法浪涌表上掷骰。"},
            {'level': 6, 'name': "扭曲幸运", 'en_name': "Bend  Luck<BR>", 'description': "你获得用你的狂野魔法扭曲命运的能力。当一个你能看见的生物投掷d20进行D20检定时，你可以在掷骰完成之后立即用一个反应并消耗1术法点来骰一次1d4，并将结果用作加值或减值（由你决定）加到该d20的骰值结果中。"},
            {'level': 14, 'name': "受控混沌", 'en_name': "Controlled  Chaos", 'description': "你获得了对狂野魔法涌动的些微掌控。你每次骰狂野魔法浪涌表时，可以骰两次再自选其一生效。"},
            {'level': 18, 'name': "驯服浪涌", 'en_name': "Tamed  Surge", 'description': "你使用法术位施展一道术士法术之后，可以立即创造一种从狂野魔法浪涌表中选择的效应而非在其上掷骰。你可以选择表中任何除了最后一行的效应，且如果你选择的效应包含掷骰，则你必须掷骰。 此特性一经使用，直至完成长休你都无法再次使用。"},
        ],
    },
    # ── 术士: 畸变术法 ──
    {
        'name': "畸变术法",
        'en_name': "",
        'class_name': "术士",
        'flavor': "操弄非自然的灵能力量",
        'features': [
            {'level': 3, 'name': "灵能法术Psionic", 'en_name': "Spells", 'description': "当你到达灵能法术表中特定的术士等级时，你就始终准备着表中对应的法术。"},
            {'level': 3, 'name': "传心谈话Telepathic", 'en_name': "Speech<BR>", 'description': "你能够在自己与他人的意识中构建一道心灵感应的链接。以一个附赠动作，你可以选择30尺内一个你可见的生物创造这一链接。链接能使你与其能够通过心灵感应方式进行交流，但交流时，你们之间距离的里数不超过你的魅力调整值里（至少1里）。你们必须使用互相知晓的语言进行心灵交流，才能使其理解你通过心灵感应传达的话语。 心灵感应的链接持续等同于你术士等级的分钟数。这一链接在你与另一生物构建链接时提前结束。"},
            {'level': 6, 'name': "灵能术法Psionic", 'en_name': "Sorcery<BR>", 'description': "当你施展一道 灵能法术 特性中的一环或更高环阶的法术时，你可以改为使用等同于该法术环数数量的术法点而非消耗法术位施展该法术。你消耗术法点施放法术时，你无视该法术施法需要的言语成分或姿势成分。你同时无视该法术需要的不会消耗且未给出具体价值的材料成分。"},
            {'level': 6, 'name': "心灵防御", 'en_name': "Psychic  Defenses", 'description': "你获得心灵伤害的抗性。此外，你在避免和结束魅惑状态与恐慌状态的豁免检定上具有优势。"},
            {'level': 14, 'name': "血肉启示Revelation in", 'en_name': "Flesh", 'description': "你能够释放出潜藏在你内部扭曲的真实形态。以一个附赠动作，你使用1点或更多的术法点以魔法性地转变形态，持续10分钟。你每消耗1术法点，你便可以从下述内容中选择一项，在转变形态期间你同时获得你选择的每项效应的增益： 水生适应Aquatic Adaptation。 你获得等同于你两倍行走速度的游泳速度，且你能在水下呼吸。不止如此，你的脖子两侧会长出鳃、或鳃在耳后呈扇状翻出、或你的手指变成蹼趾、或是..."},
            {'level': 18, 'name': "扭曲内爆Warping", 'en_name': "Implosion", 'description': "你能够释放出扭曲空间的异常现象。以一个魔法动作，你传送到120尺内你可见的一个未被占据的位置，然后你消失位置30尺内的每个生物必须进行一次对抗你施法DC的力量豁免，豁免失败将受3d10力场伤害并被立即拉向你原本的位置，并停在最靠近的一处未被占据的空间内，豁免成功只受半伤。 此特性一经使用，直至完成长休你都无法再次使用。你也可以消耗5点术法点（无需动作）重置此特性的使用权。"},
        ],
    },
    # ── 术士: 龙族术法Draconic ──
    {
        'name': "龙族术法Draconic",
        'en_name': "Sorcery",
        'class_name': "术士",
        'flavor': "吐纳巨龙魔法",
        'features': [
            {'level': 3, 'name': "龙族体魄Draconic", 'en_name': "Resilience<BR>", 'description': "魔法在你的体内流动，外化为龙族赠礼体现出的生理特质。你的生命值上限提升3，此后每提升一个术士等级，都将再次提升1。 你部分皮肤覆盖着龙鳞样式的柔鳞。未着装护甲时，你的基础AC等于10+你的敏捷调整值＋你的魅力调整值。"},
            {'level': 3, 'name': "龙族法术Draconic", 'en_name': "Spells", 'description': "当你到达龙族法术表中特定的术士等级时，你就始终准备着表中对应的法术。"},
            {'level': 6, 'name': "元素亲和Elemental Affinity</STRONG></FONT><BR>你的龙族魔法与龙族相关的伤害类型有较强的亲和力。选择以下伤害类型之一：强酸、寒冷、火焰、闪电或毒素。<BR>你获得对所选伤害类型的抗性，且当你施展造成那种伤害的法术时，你可以将你的<STRONG>魅力</STRONG>调整值加到那个法术的其中一次伤害掷骰中。</p> <p><STRONG><FONT color=#800000>14级：龙翼Dragon", 'en_name': "Wings", 'description': "以一个附赠动作，你可以在背后张开一对龙翼。龙翼持续1小时，若你选择将其解散（无需动作）则会提前终止，在龙翼持续期间你获得60尺飞行速度。 此特性一经使用，直至完成 长休 你都无法再次使用。你也可以消耗3点术法点（无需动作）重置此特性的使用权。"},
            {'level': 18, 'name': "龙族伙伴Dragon", 'en_name': "Companion", 'description': "你可以无需材料成分施展 龙类召唤术Summon Dragon 。你可以无需法术位施展它一次，随后你在完成一次 长休 后重获以此法施展它的能力。 每当你开始施展此法术时，都可以修改此法术使其无需 专注 。以此法施展时，此法术的持续时间将变为1分钟。"},
        ],
    },
    # ── 武僧: 命流武者 ──
    {
        'name': "命流武者",
        'en_name': "Warrior of Mercy",
        'class_name': "武僧",
        'flavor': "掌执命流",
        'features': [
            {'level': 3, 'name': "夺命之手", 'en_name': "Hand of  Harm", 'description': "每回合一次，当你用徒手打击命中一名生物并造成伤害时，你可以消耗1点功力额外造成等于一枚你的武艺骰+你的感知调整值的暗蚀伤害。"},
            {'level': 3, 'name': "予命之手", 'en_name': "Hand of  Healing", 'description': "以一个 魔法 动作，你可以消耗1点功力并接触一名生物，为目标恢复等于一枚你的武艺骰+你的感知调整值的生命值。当你使用疾风连击时，你可以将其中一次徒手打击替换为使用此特性，且无需为予命之手消耗功力。"},
            {'level': 3, 'name': "操命本事", 'en_name': "Implements of  Mercy", 'description': "你获得洞悉和医药的熟练，并且获得草药工具的熟练。"},
            {'level': 6, 'name': "生死之触", 'en_name': "Physician's  Touch<BR>", 'description': "你的夺命之手和予命之手获得强化，具体内容见下。 夺命之手Hand of Harm。 当你对一名生物使用夺命之手时，你还可以使该生物陷入 中毒 状态，直至你的下个回合结束。 予命之手Hand of Healing。 当你使用予命之手时，你还可以结束你治疗的生物身上的以下状态之一： 目盲 、 耳聋 、 麻痹 、 中毒 或 震慑 。"},
            {'level': 11, 'name': "生杀予夺", 'en_name': "Flurry of Healing  and  Harm<BR>", 'description': "当你使用疾风连击时，你可以将每一次徒手打击都替换为使用予命之手，且均无需为予命之手消耗功力。 此外，当你以疾风连击发动徒手打击并造成伤害时，你可以为那次打击使用夺命之手且无需为夺命之手消耗功力。但你每回合仍然只能使用一次夺命之手。 你能使用这些增益的总次数等于你的感知调整值（至少一次）。在你完成长休时重获所有已消耗的次数。"},
            {'level': 17, 'name': "命极之手", 'en_name': "Hand of Ultimate  Mercy<BR>", 'description': "你对生命能量的掌握打开了通往命流奥义的大门。以一个魔法动作，你可以消耗5点功力并触碰一名死亡不超过24小时的生物的尸体。该生物会起死回生，以等于4d10+你的感知调整值的生命值复活。如果该生物死前具有任意以下状态，该生物复活时这些状态被移除：目盲、耳聋、麻痹、中毒和震慑。 此特性一经使用，直至完成长休你都无法再次使用。"},
        ],
    },
    # ── 武僧: 四</FONT><FONT color=#00ffff>象</FONT><FONT color=#008000>武</FONT><FONT color=#ffc000>者</FONT> <FONT color=#ff0000>Warrior</FONT> <FONT color=#00ffff>of</FONT> <FONT color=#008000>the</FONT> <FONT ──
    {
        'name': "四</FONT><FONT color=#00ffff>象</FONT><FONT color=#008000>武</FONT><FONT color=#ffc000>者</FONT> <FONT color=#ff0000>Warrior</FONT> <FONT color=#00ffff>of</FONT> <FONT color=#008000>the</FONT> <FONT",
        'en_name': "color=#ffc000>Elements",
        'class_name': "武僧",
        'flavor': "身起四象",
        'features': [
            {'level': 3, 'name': "元素同调", 'en_name': "Elemental  Attunement", 'description': "在你回合开始时，你可以消耗1点功力让元素能量浸润己身。这股能量将会持续存在10分钟，或直至你陷入失能状态。持续时间内，你获得以下好处："},
            {'level': 3, 'name': "掌控元素", 'en_name': "Manipulate  Elements<BR>", 'description': "你习得戏法 四象法门Elementalism ，其施法属性为感知。"},
            {'level': 6, 'name': "元素爆破拳", 'en_name': "Elemental  Burst", 'description': "以一个 魔法 动作，你可以消耗2点功力，凝聚元素能量，在你周围120尺内的一点产生一场半径20尺球状区域的能量爆发。你选择一种伤害类型：强酸、寒冷、火焰、闪电或雷鸣。 球状区域内的每个生物必须成功通过进行一次敏捷豁免。若失败，该生物受到相当于你3个武艺骰的伤害，其伤害类型为你之前所选择的类型。若成功，则受到一半伤害。"},
            {'level': 11, 'name': "四象遁术", 'en_name': "Stride of the  Elements", 'description': "当你处于元素同调特性激活期间，你获得相当于你速度的飞行速度与游泳速度。"},
            {'level': 17, 'name': "四象神通", 'en_name': "Elemental  Epitome", 'description': "当你处于元素同调特性激活期间，你在持续时间内获得以下增益： 伤害抗性Damage Resistance。 你选择一种伤害类型：强酸、寒冷、火焰、闪电或雷鸣，你获得该伤害类型的抗性。你在每个你的回合开始时可以改变所选择的伤害类型。 破灭奔行Destructive Stride。 当你使用疾步如风时，你的速度提升20尺，直至这个回合结束。在持续时间内，当你进入到某个生物5尺范围内的时候，你可以对..."},
        ],
    },
    # ── 武僧: 散打武者 ──
    {
        'name': "散打武者",
        'en_name': "Warrior of the Open Hand",
        'class_name': "武僧",
        'flavor': "散打随心",
        'features': [
            {'level': 3, 'name': "散打技巧", 'en_name': "Open Hand  Technique", 'description': "每当你疾风连击中的一次攻击命中一个生物时，你可以迫使其承受下列效应之一： 慌神Addle。 目标直至他的下个回合开始不能使用借机攻击。 推离Push。 目标必须成功通过一次力量豁免，否则被你推离15尺。 失衡Topple。 目标必须成功通过一次敏捷豁免，否则陷入倒地状态。"},
            {'level': 6, 'name': "混元体", 'en_name': "Wholeness of  Body", 'description': "你获得治愈己身的能力。你能够以一个附赠动作掷你的武艺骰。你恢复相当于掷骰结果+你的感知调整值数量的生命值（至少恢复1点生命值）。 你可以使用这个特性的次数相当于你的感知调整值（至少一次），在你完成一次长休时，你重获全部已消耗使用次数。"},
            {'level': 11, 'name': "流星步", 'en_name': "Fleet  Step", 'description': "当你执行疾步如风以外的附赠动作时，你还可以在该附赠动作完成后立即使用疾步如风。"},
            {'level': 17, 'name': "渗透劲", 'en_name': "Quivering  Palm", 'description': "你获得了将内劲击入他人体内的能力。当你以徒手打击命中一个生物时，可以消耗4点功力打入暗劲，其持续相当于你武僧等级的天数。在你使用你的动作将之结束前，暗劲是无害的。此外，当你在自己的回合执行攻击动作时，你可以将其中一次攻击替换为这个动作使暗劲结束。若你如此做，你和目标必须处于同一个存在位面。 当你结束暗劲时，目标必须进行一次体质豁免，失败则受到10d12力场伤害，成功则只受到一半伤害。 在同一..."},
        ],
    },
    # ── 武僧: 暗影武者 ──
    {
        'name': "暗影武者",
        'en_name': "Warrior of Shadow",
        'class_name': "武僧",
        'flavor': "暗影藏形",
        'features': [
            {'level': 3, 'name': "暗影技艺", 'en_name': "Shadow  Arts", 'description': "你掌握了如何唤出堕影冥界的力量，获得以下增益： 黑暗术Darkness。 你可以消耗1点功力以施展黑暗术Darkness法术且无需任何法术成分。你可以看穿以这个特性施展的黑暗区域。法术持续期间，你可以在你的每个回合开始时将此法术区域移动到你60尺范围内的任意一处空间。 黑暗视觉Darkvision。 你获得60尺黑暗视觉。如果你已经有黑暗视觉，则其范围提升60尺。 幻影术Shadowy Fi..."},
            {'level': 6, 'name': "暗影步", 'en_name': "Shadow  Step", 'description': "当你完全身处 微光光照 或 黑暗 下时，你能以一个附赠动作传送到60尺内另一处你可见的未占据的空间，目标地点需要同样位于微光光照或黑暗下。接下来，你在当前回合结束前所做的下一次近战攻击具有优势。"},
            {'level': 11, 'name': "无影步", 'en_name': "Improved Shadow  Step", 'description': "你可以利用与堕影冥界的连结来增强自己的传送能力。当你使用暗影步特性时，你可以消耗1点功力，移除开始和结束时对微光光照或黑暗环境的要求。此外，作为这个附赠动作的一部分，你可以立即在传送之后进行一次徒手打击。"},
        ],
    },
    # ── 法师: 塑能师 ──
    {
        'name': "塑能师",
        'en_name': "Evoker",
        'class_name': "法师",
        'flavor': "创造炸裂的元素特效",
        'features': [
            {'level': 3, 'name': "塑能学者", 'en_name': "Evocation Savant", 'description': "从法师法术列表中选择两道不高于二环的塑能学派法术，并将其免费加入你的法术书中。 此外，每当你在本职业中获得一个新环阶的法术位时，你都能免费将一道法师法术列表中的塑能学派法术加入你的法术书中。你所选的法术都必须是你当前拥有法术位的环阶。"},
            {'level': 3, 'name': "强力戏法", 'en_name': "Potent Cantrip", 'description': "你造成伤害的戏法甚至能影响到本可免受戏法效应影响的生物。当你施展一道戏法，其攻击检定失手，或目标对抗你戏法的豁免成功时，它仍会受到一半伤害（若有），但不会受到该戏法的其他效应影响。"},
            {'level': 6, 'name': "法术塑形", 'en_name': "Sculpt Spells", 'description': "你的塑能学派法术作用范围里可以保留一小部分相对安全的区域。当你施展一个会影响你可见的其他生物的塑能学派法术时，你能从中指定数量等同于1+该法术环阶的生物。被指定的生物进行对抗该法术的豁免时将直接成功，且如果法术在豁免成功后仍然造成一半的伤害，这些生物不会承受任何伤害。"},
            {'level': 10, 'name': "强效塑能", 'en_name': "Empowered Evocation", 'description': "当你施展一道法师法术列表里的塑能学派法术时，你能将你的 智力 调整值加入该法术的其中一次伤害掷骰中。"},
            {'level': 14, 'name': "超限导能", 'en_name': "Overchannel", 'description': "你能增强你法术的力量。当你用一个一至五环的法术位施展一个会造成伤害的法师法术时，你能在施展它的回合中令其造成的伤害取最大值。 你首次这么做时不会承受任何负面效应。但如果你在完成一次长休前再次使用该特性，则你会在施展法术后立即受到每环阶2d12暗蚀伤害。该伤害无视任何抗性或免疫。 你在完成一次长休前每多使用此特性一次，每环阶造成的伤害就提升1d12。"},
        ],
    },
    # ── 法师: 幻术师 ──
    {
        'name': "幻术师",
        'en_name': "Illusionist",
        'class_name': "法师",
        'flavor': "编织精妙的欺瞒法术",
        'features': [
            {'level': 3, 'name': "幻术学者", 'en_name': "Illusion Savant", 'description': "从法师法术列表中选择两道不高于二环的幻术学派法术，并将其免费加入你的法术书中。 此外，每当你在本职业中获得一个新环阶的法术位时，你都能免费将一道法师法术列表中的幻术学派法术加入你的法术书中。你所选的法术都必须是你当前拥有法术位的环阶。"},
            {'level': 3, 'name': "强化幻术", 'en_name': "Improved Illusions", 'description': "你施展幻术学派法术时无需言语成分，且若你施展的幻术学派法术的施法距离不小于10尺，则其施法距离增加60尺。 你同时知晓 次级幻象Minor Illusion 戏法。如果你已经知晓了此戏法，则你习得另一道你选择的法师戏法。此戏法不计入你的已知戏法数。当你施展次级幻象时，可以在一次施法中同时创造出声音和影像，并且你能以一个附赠动作施展它。"},
            {'level': 6, 'name': "魅影生灵", 'en_name': "Phantasmal Creatures", 'description': "你总是准备了 野兽召唤术Summon Beast 和 妖精召唤术Summon Fey 。你施展其中任意一道法术时，可以选择将其学派变为幻术学派，这会使召唤出的生物变得虚幻。你可以不消耗法术位地施展这两道法术的幻术版本各一次，但无需法术位地施展这两道法术会使其召唤出的生物只有一半生命值。一旦你无需法术位地施展了其中任意一道法术，直至完成长休你都无法再以此法施展那道法术。"},
            {'level': 10, 'name': "幻影化形", 'en_name': "Illusory Self", 'description': "当一名生物对你进行的一次攻击检定命中时，你可以使用你的反应在攻击者与你之间插入幻象分身。这次攻击对你自动失手，随后幻象分身消失。 此特性一经使用，直至完成长休你都无法再次使用。你也可以消耗一个二环或更高环阶的法术位（无需动作）重置此特性的使用权。"},
            {'level': 14, 'name': "亦真亦幻", 'en_name': "Illusory Reality", 'description': "你习得借由将暗影魔法编入你的幻术，从而使其获得半真实效果的秘密。当你用法术位施展一道幻术学派法术时，你能选择一个属于幻象一部分的非活化非魔法物件，并让该物件化作真实。你可以在法术持续过程中在自己的回合以一个附赠动作这样做。该物件将在接下来1分钟内保持真实，它在此期间无法造成伤害或赋予任何状态。例如，你可以创造一座横跨峡谷的桥梁幻象，而后将之化作真实，使你的队友能从桥上跨越峡谷。"},
        ],
    },
    # ── 法师: 防护师 ──
    {
        'name': "防护师",
        'en_name': "Abjurer",
        'class_name': "法师",
        'flavor': "保卫同伴，放逐仇敌",
        'features': [
            {'level': 3, 'name': "防护学者", 'en_name': "Abjuration Savant", 'description': "从法师法术列表中选择两道不高于二环的防护学派法术，并将其免费加入你的法术书中。 此外，每当你在本职业中获得一个新环阶的法术位时，你都能免费将一道法师法术列表中的防护学派法术加入你的法术书中。你所选的法术都必须是你当前拥有法术位的环阶。"},
            {'level': 3, 'name': "奥术守御", 'en_name': "Arcane Ward", 'description': "你可以在自己周围编织魔法来保护自己。当你消耗法术位施展一道防护学派法术时，你能同时使用该法术的一缕魔力为自己创建一个魔法结界，该结界会持续至你完成一次长休。该结界的生命值上限等同于你法师等级的两倍加上你的智力调整值。每当你受到伤害时，结界会代替你受到此伤害，如果你具有任何抗性或易伤，则先为伤害应用抗性和易伤后再计算结界生命值减损。如果该伤害会使结界的生命值降至0，你将会受到溢出部分的伤害。当..."},
            {'level': 6, 'name': "投射守御", 'en_name': "Projected Ward", 'description': "当30尺内一个你可见的生物受到伤害时，你可以用你的反应让你的奥术守御吸收此次伤害。如果该伤害使结界的生命值降为0，则被保护的生物将承受所有剩余伤害。如果被保护的生物有任何抗性或易伤，则应在计算结界承伤之前先结算抗性和易伤。"},
            {'level': 10, 'name': "破法者", 'en_name': "Spell Breaker", 'description': "你始终准备着法术 法术反制Counterspell 和 解除魔法Dispel Magic 。此外，你能够以一个附赠动作施展 解除魔法Dispel Magic ，且你能在其属性检定中加入你的熟练加值。你消耗法术位施展其中任意一道法术时，若该法术未能成功阻止法术施展或未能成功解除法术效应，则你用于施展法术反制或解除魔法的法术位不会被消耗。"},
            {'level': 14, 'name': "法术抗性", 'en_name': "Spell Resistance", 'description': "你抵抗法术时进行的豁免检定具有 优势 ，且你对法术造成的伤害具有抗性。"},
        ],
    },
    # ── 法师: 预言师 ──
    {
        'name': "预言师",
        'en_name': "Diviner",
        'class_name': "法师",
        'flavor': "探究多元宇宙之秘",
        'features': [
            {'level': 3, 'name': "预言学者", 'en_name': "Divination Savant", 'description': "从法师法术列表中选择两道不高于二环的预言学派法术，并将其免费加入你的法术书中。 此外，每当你在本职业中获得一个新环阶的法术位时，你都能免费将一道法师法术列表中的预言学派法术加入你的法术书中。你所选的法术都必须是你当前拥有法术位的环阶。"},
            {'level': 3, 'name': "预兆", 'en_name': "Portent", 'description': "预知未来的片段开始在你意识中闪过。每当你完成一次长休时，掷2次D20并记录其结果。你能用其中一个预言骰替换任何你或一个你能看见的生物进行的D20检定。你必须在检定进行前选择这样做，且你每回合只能以这种方式替换一次检定。 每个预言骰只能被使用一次。当你完成一次长休时，你失去所有未消耗的预言骰。"},
            {'level': 6, 'name': "专业预言", 'en_name': "Expert Divination", 'description': "施展预言学派法术对你来说是如此容易，以至于其只会占用你施法努力中的一小部分。你消耗法术位施展一个环阶为二环或更高的预言学派法术时，可以恢复一个已消耗的法术位。所恢复的法术位环阶必须低于你正施展的预言学派法术，且不高于五环。"},
            {'level': 10, 'name': "天眼通", 'en_name': "The Third Eye", 'description': "你可以增强你的察觉能力。以一个附赠动作，从以下增益中选择其一，其会持续至你开始一次短休或长休。此特性一经使用，直至完成短休或长休你都无法再次使用。"},
        ],
    },
    # ── 游侠: 妖精漫游者 ──
    {
        'name': "妖精漫游者",
        'en_name': "Fey Wanderer",
        'class_name': "游侠",
        'flavor': "驾驭妖精的哀与乐",
        'features': [
            {'level': 3, 'name': "哀惧灵袭", 'en_name': "Dreadful  Strikes", 'description': "你能够使用来自妖精荒野中黑暗空洞的摄心魔法以强化你的武器攻击。当你用一把武器击中一个生物时，你可以对目标造成额外的1d4点心灵伤害。每个生物在每个回合只能够受到这一额外伤害一次。你的游侠等级达到11级时，这一额外伤害变为1d6。"},
            {'level': 3, 'name': "妖精漫游者魔法", 'en_name': "Fey Wanderer  Magic<BR></STRONG></FONT>当你到达妖精漫游者法术表中特定的游侠等级时，你就始终准备着表中对应的法术。</p>    <p><STRONG>妖精漫游者法术Fey Wanderer Spells</STRONG>  </p>  <table class=\"MsoTable15Plain4\" border=\"0\" cellspacing=\"0\" cellpadding=\"0\" style=\"BORDER-COLLAPSE: collapse\">  <tr>   <td valign=\"top\" style=\"PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p align=center><b>游侠等级</b></p>   </td>   <td valign=\"top\" style=\"PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p><b>法术</b></p>   </td>  </tr>  <tr>   <td valign=\"top\" style=\"BACKGROUND: #f2f2f2; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p align=center><span lang=\"EN-US\" style=\"COLOR: black\"       >3</span></p>   </td>   <td valign=\"top\" style=\"BACKGROUND: #f2f2f2; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p><U><EM>魅惑类人Charm Person</EM></U> </p>   </td>  </tr>  <tr>   <td valign=\"top\" style=\"PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p align=center>5</p>   </td>   <td valign=\"top\" style=\"PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p><U><EM>迷踪步Misty Step</EM></U> </p>   </td>  </tr>  <tr>   <td valign=\"top\" style=\"BACKGROUND: #f2f2f2; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p align=center><span lang=\"EN-US\" style=\"COLOR: black\"       >9</span></p>   </td>   <td valign=\"top\" style=\"BACKGROUND: #f2f2f2; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p><U><EM>妖精召唤术Summon Fey</EM></U> </p>   </td>  </tr>  <tr>   <td valign=\"top\" style=\"PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p align=center>13</p>   </td>   <td valign=\"top\" style=\"PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p><U><EM>任意门Dimension Door</EM></U> </p>   </td>  </tr>  <tr>   <td valign=\"top\" style=\"BACKGROUND: #f2f2f2; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p align=center><span lang=\"EN-US\" style=\"COLOR: black\"       >17</span></p>   </td>   <td valign=\"top\" style=\"BACKGROUND: #f2f2f2; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p><U><EM>误导术Mislead</EM></U></p>   </td>  </tr> </table>    <p>你还获得了一种妖精祝福。你可以在下方精野之赐表中选择你的祝福或者随机决定它。</p>    <p><STRONG>精野之赐Feywild Gifts</STRONG>  </p>  <table class=\"MsoTable15Plain4\" border=\"0\" cellspacing=\"0\" cellpadding=\"0\" style=\"BORDER-COLLAPSE: collapse\">  <tr>   <td width=\"85\" valign=\"top\" style=\"WIDTH: 63.55pt; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p><b>1d6</b></p>   </td>   <td width=\"322\" valign=\"top\" style=\"WIDTH: 241.25pt; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p><b>祝福</b></p>   </td>  </tr>  <tr>   <td valign=\"top\" style=\"WIDTH: 0cm; BACKGROUND: #f2f2f2; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p><span lang=\"EN-US\" style=\"COLOR: black\"       >1</span></p>   </td>   <td width=\"322\" valign=\"top\" style=\"WIDTH:  241.25pt; BACKGROUND: #f2f2f2; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p><span style=\"COLOR: black\"       >在你进行长休或短休时，缥缈的蝴蝶在你周身振翅。</span></p>   </td>  </tr>  <tr>   <td width=\"85\" valign=\"top\" style=\"WIDTH: 63.55pt; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p>2</p>   </td>   <td width=\"322\" valign=\"top\" style=\"WIDTH: 241.25pt; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p>每天黎明，花朵将在你的头发中生长。</p>   </td>  </tr>  <tr>   <td valign=\"top\" style=\"WIDTH: 0cm; BACKGROUND: #f2f2f2; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p><span lang=\"EN-US\" style=\"COLOR: black\"       >3</span></p>   </td>   <td width=\"322\" valign=\"top\" style=\"WIDTH:  241.25pt; BACKGROUND: #f2f2f2; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p><span style=\"COLOR: black\"       >你身上有淡淡的肉桂、薰衣草或肉豆蔻，或另一种令人舒适的药草或香料的香味。</span></p>   </td>  </tr>  <tr>   <td width=\"85\" valign=\"top\" style=\"WIDTH: 63.55pt; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p>4</p>   </td>   <td width=\"322\" valign=\"top\" style=\"WIDTH: 241.25pt; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p>你的影子会在没人直视它时起舞。</p>   </td>  </tr>  <tr>   <td valign=\"top\" style=\"WIDTH: 0cm; BACKGROUND: #f2f2f2; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p><span lang=\"EN-US\" style=\"COLOR: black\"       >5</span></p>   </td>   <td width=\"322\" valign=\"top\" style=\"WIDTH:  241.25pt; BACKGROUND: #f2f2f2; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p><span style=\"COLOR: black\"       >你的头发中长出纤细的触角或鹿角。</span></p>   </td>  </tr>  <tr>   <td valign=\"top\" style=\"WIDTH: 0cm; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p>6</p>   </td>   <td width=\"322\" valign=\"top\" style=\"WIDTH: 241.25pt; PADDING-BOTTOM: 0cm; PADDING-TOP: 0cm; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt\"    >   <p>你的肤色和发色会在每个黎明时改变。</p>   </td>  </tr> </table>      <p><STRONG><FONT color=#800000>3级：妖冶娴都 Otherworldly  Glamour", 'description': "每当你进行一次魅力检定时，你都可以在那次检定中获得等于你的感知调整值的加值（至少+1）。 另外，你选择获得下列技能之一的熟练： 欺瞒 、 表演 或 游说 。"},
            {'level': 7, 'name': "妖思魅缕", 'en_name': "Beguiling  Twist", 'description': "妖精荒原的魔法护卫着你的心灵。你在对抗或终止魅惑或恐慌状态的豁免检定上具有优势。 此外，当你或位于你120尺内的一个你可见的生物，通过了一次对抗或终止魅惑或恐慌状态的豁免检定时，你可以用你的反应迫使位于你120尺内的另一个你可见的不同生物，进行一次对抗你法术豁免DC的感知豁免。豁免失败，目标则陷入魅惑或恐慌状态（由你选择）1分钟。目标在其每回合结束时重复此豁免，豁免成功则结束此效应。"},
            {'level': 11, 'name': "精宸所与", 'en_name': "Fey  Reinforcements", 'description': "你可以无需材料成分地施展 妖精召唤术Summon Fey 。同时，你可以免费施展这个法术一次而不需要消耗法术位，在你完成一次长休后，你重获免费施展该法术的能力。 每当你施展此法术时，你都可以微调这一法术使其无需专注。以无需专注的方式施法时，该法术的持续时间将变为一分钟。"},
            {'level': 15, 'name': "雾行漫游", 'en_name': "Misty  Wanderer", 'description': "你可以免费施展 迷踪步Misty Step 而不需要消耗法术位，次数等同于你的感知调整值次（至少一次），在完成一次长休后，你重获所有的已消耗的次数。 另外，每当你施展 迷踪步Misty Step 时，你可以携带一个位于你5尺内你可见的自愿生物与你一同传送。那个生物会被传送到由你选择的，位于你的目标位置5尺内的一处未占据空间内。"},
        ],
    },
    # ── 游侠: 幽域追猎者 ──
    {
        'name': "幽域追猎者",
        'en_name': "Gloom Stalker",
        'class_name': "游侠",
        'flavor': "利用阴影魔法制敌",
        'features': [
            {'level': 3, 'name': "阴影视野", 'en_name': "Umbral  Sight", 'description': "你获得60尺黑暗视觉。如果你获得本特性时已拥有了黑暗视觉，那个黑暗视觉的范围增加60尺。 你还擅长避开依赖黑暗视觉的角色。完全身处黑暗期间，对于任何依靠黑暗视觉观察黑暗中的你的生物而言，你具有隐形状态。"},
            {'level': 7, 'name': "钢铁意志", 'en_name': "Iron  Mind</STRONG></FONT><BR>你已经磨炼出了抵御精神影响的能力。你获得感知豁免熟练。如果你已经有这项熟练，你可以获得智力或者魅力豁免熟练（由你选择）来代替。</p>    <p><STRONG><FONT color=#800000>11级：追猎如风 Stalker's  Flurry", 'description': "你的恐惧打击造成的心灵伤害变为2d8。另外，当你使用恐惧伏击的恐惧打击特性时，你可以创造出以下的额外效应之一。 瞬杀Sudden Strike。 你可以用同一把武器，对位于原目标5尺范围内的另一生物再发动一次攻击，新目标必须处于你武器的触及或射程内。 群慌Mass Fear。 目标与位于目标10尺范围内的每个生物都必须通过一次对抗你法术豁免DC的感知豁免。若豁免失败，生物将会陷入恐慌状态，持..."},
            {'level': 15, 'name': "如影随行", 'en_name': "Shadowy  Dodge<BR>", 'description': "当一个生物对你发动了一次攻击检定时，你能用反应对这次检定施加劣势。不管那次攻击命中或失手，你都能在那之后传送至你30尺范围内的一处未被占据的、你可见的空间。"},
        ],
    },
    # ── 游侠: 猎人 ──
    {
        'name': "猎人",
        'en_name': "Hunter",
        'class_name': "游侠",
        'flavor': "保护自然与人民免于毁灭",
        'features': [
            {'level': 3, 'name': "猎人学识", 'en_name': "Hunter's  Lore<BR>", 'description': "你可以呼唤自然的力量以揭晓猎物的强弱。在一个生物被你的猎人印记标记的期间，你知道那个生物是否拥有任何免疫、抗性或易伤，并且能够得知其具体的项目是什么。"},
            {'level': 3, 'name': "猎杀技艺", 'en_name': "Hunter's  Prey<BR>", 'description': "你选择并获得以下特性选项之一。当你完成一次短休或长休时，你可以将所选的选项替换为另一个。 巨像屠夫Colossus Slayer。 你强而有力的攻击可以击倒最强壮的对手。当你用武器命中生物时，如果该敌人生命值不满，则该武器额外对目标造成1d8点伤害。你每回合只能造成一次这种额外伤害。 灭族者Horde Breaker。 每个你的回合一次，当你用武器进行攻击时，你可以用该武器对位于目标5尺内的..."},
            {'level': 7, 'name': "防守战术", 'en_name': "Defensive  Tactics<BR>", 'description': "你选择并获得以下特性选项之一。当你完成一次短休或长休时，你可以将所选的选项替换为另一个。 冲出重围Escape the Horde。 对你发动的借机攻击具有劣势。 多重防御Multiattack Defense。 当一个生物的攻击检定命中你时，该生物在本回合内对你进行的其他攻击检定具有劣势。"},
            {'level': 11, 'name': "高阶猎杀技艺", 'en_name': "Superior Hunter's  Prey<BR>", 'description': "每回合一次，当你对被你的猎人印记所标记的生物造成伤害时，你可以对位于这个生物30尺范围内的一个你能看见的另一名生物，同样施加由猎人印记造成的额外伤害。"},
            {'level': 15, 'name': "高阶防守战术", 'en_name': "Superior Hunter's  Defense", 'description': "当你受到伤害时，你可以用你的反应使你获得对该伤害以及相同伤害类型的抗性, 直至当前回合结束。"},
        ],
    },
    # ── 游侠: 驯兽师 ──
    {
        'name': "驯兽师",
        'en_name': "Beast Master",
        'class_name': "游侠",
        'flavor': "与原始野兽结缘",
        'features': [
            {'level': 3, 'name': "原初行侣", 'en_name': "Primal  Companion", 'description': "你魔法性的召唤出一只原初野兽，其力量来自于与你与自然的联系。你从 大地野兽Beast of the Land 、 海洋野兽Beast of the Sea 和 天空野兽Beast of the Sky 中选择其一项作为它的数据卡。你决定原初野兽是何种动物，选择适合其数据卡的外形。无论你选择什么样的动物，这只野兽都带有原初之力的印痕，暗示着其超凡起源。 这只野兽对你和你的伙伴态度友善，并会听从..."},
            {'level': 7, 'name': "特效训练", 'en_name': "Exceptional  Training", 'description': "当你以附赠动作命令你的原初行侣野兽执行动作时，你还可以令它以它自己的附赠动作执行 疾走 、 撤离 、 回避 或 协助 动作。 此外，每当你的野兽的攻击检定命中并造成伤害时，其伤害类型可以是力场伤害或其原本的伤害类型（由你选择）"},
            {'level': 11, 'name': "兽性狂怒", 'en_name': "Bestial  Fury", 'description': "当你命令原初行侣执行野兽打击动作时，它能使用该动作两次。 此外，每个回合中，当它首次击中一个受到你的法术 猎人印记Hunter's Mark 影响的生物时，它可以额外造成一定的力场伤害，其数值等同于那个法术的额外伤害。"},
            {'level': 15, 'name': "法术共享", 'en_name': "Share  Spells", 'description': "当你施展的法术指定了你自己作为目标，并且你的原初行侣正位于你30尺范围内时，你可以让该法术效应同时作用于你的原初行侣。"},
        ],
    },
    # ── 游荡者: 刺客 ──
    {
        'name': "刺客",
        'en_name': "Assassin",
        'class_name': "游荡者",
        'flavor': "践行死亡的不法技艺",
        'features': [
            {'level': 3, 'name': "暗杀", 'en_name': "Assassinate<BR>", 'description': "你精通于对目标发起奇袭，你获得以下增益："},
            {'level': 3, 'name': "刺客工具", 'en_name': "Assassin's  Tools", 'description': "你获得一套易容工具和一套毒药工具，并获得这些工具的熟练。"},
            {'level': 9, 'name': "专业渗透", 'en_name': "Infiltration  Expertise", 'description': "你是潜入渗透的专家，你熟练掌握了以下技巧来帮助自己的潜入："},
            {'level': 13, 'name': "淬毒武器", 'en_name': "Envenom  Weapons", 'description': "当你使用 诡诈打击 时，每当目标在对抗你的 淬毒 选项时豁免检定失败，它会受到额外2D6的毒素伤害。该伤害无视毒素抗性。"},
            {'level': 17, 'name': "致命袭杀", 'en_name': "Death  Strike", 'description': "当你在战斗的第一轮命中并偷袭了某一目标时，该目标必须成功通过一次体质豁免（DC8+你的熟练加值+你的敏捷调整值），否则本次攻击将对该目标造成双倍的伤害。"},
        ],
    },
    # ── 游荡者: 盗贼 ──
    {
        'name': "盗贼",
        'en_name': "Thief",
        'class_name': "游荡者",
        'flavor': "追秘猎宝的经典冒险家",
        'features': [
            {'level': 3, 'name': "快手", 'en_name': "Fast  Hands", 'description': "你可以通过附赠动作来进行下列行为中的一个："},
            {'level': 3, 'name': "梁上君子", 'en_name': "Second-Story  Work", 'description': "你的训练使你擅长抵达那些难以到达的地方。你获得以下增益："},
            {'level': 9, 'name': "极效潜行", 'en_name': "Supreme  Sneak", 'description': "你获得以下诡诈打击选项。"},
            {'level': 13, 'name': "使用魔法装置", 'en_name': "Use Magic  Device", 'description': "在你的寻宝历险生涯中，你学会了如何最大化利用魔法装置。你获得以下增益："},
        ],
    },
    # ── 游荡者: 诡术师 ──
    {
        'name': "诡术师",
        'en_name': "Arcane Trickster",
        'class_name': "游荡者",
        'flavor': "利用奥术魔法强化潜行",
        'features': [
            {'level': 3, 'name': "施法", 'en_name': "Spellcasting", 'description': "你学会了如何施展法术。施法规则见第七章。下文将详述如何将这些规则应用于诡术师。 戏法Cantrips。 你习得三道法师戏法。 法师之手Mage Hand 以及法师法术列表中你选择的两道戏法（法师法术列表见法师职业部分）。推荐选择 心灵之楔Mind Sliver 和 次级幻象Minor Illusion 。 每当你获得一个游荡者等级时，你都能从你的非 法师之手Mage Hand 的戏法中选择其..."},
            {'level': 3, 'name': "法师之手诈术", 'en_name': "Mage Hand  Legerdemain<BR>", 'description': "当你施展 法师之手Mage Hand 时，你可以通过附赠动作施展，并且你能够使幽灵手变得 隐形 。你可以通过附赠动作控制幽灵手，并且你可以通过它进行敏捷（ 巧手 ）检定。"},
            {'level': 9, 'name': "诡术伏击", 'en_name': "Magical  Ambush<BR>", 'description': "处于 隐形 状态期间，若你对一名生物施展法术，它在那个回合中为对抗该法术而进行的任何豁免检定都具有 劣势 。"},
            {'level': 13, 'name': "万能诡术", 'en_name': "Versatile  Trickster<BR>", 'description': "你获得了使用 法师之手Mage Hand 干扰敌人的能力。当你对一个生物使用诡诈打击中的摔绊选项时，你还可以对法师之手五尺内的另一个生物施加这个效果。"},
            {'level': 17, 'name': "法术窃贼", 'en_name': "Spell  Thief<BR>", 'description': "你获得了如何以魔法从其他施法者那里偷取有关如何施展某一法术的知识的能力。 当一个生物施展了一个目标是你或是其效应范围会影响你的法术后，你可以立刻使用你的反应来迫使该生物进行一次智力豁免。其豁免DC等同于你的施法DC。若豁免失败，你消除这个法术对你的影响，并且你将偷走使用这个法术的知识，但这个法术最低必须是一环并且你可以施展的更高等级的法术（不需要是法师法术）。接下来的八小时内，你准备了这个法..."},
        ],
    },
    # ── 游荡者: 魂刃 ──
    {
        'name': "魂刃",
        'en_name': "Soulknife",
        'class_name': "游荡者",
        'flavor': "以念为刃屠戮敌手",
        'features': [
            {'level': 3, 'name': "灵能力量", 'en_name': "Psionic  Power", 'description': "你内心蕴含着一股灵能力量，这股能量表现为你拥有数枚灵能骰。你可以使用这些灵能骰来驱动你从这个子职中获得的特定心灵异能。下方的魂刃灵能骰列表展示了你在达到特定游荡者等级时会拥有多少颗灵能骰，该列表同样列出了骰子大小。"},
            {'level': 3, 'name': "念刃", 'en_name': "Psychic  Blades", 'description': "你能将自己的心灵异能塑造为由灵能构成的闪亮刀刃。当你执行攻击动作或者进行一次借机攻击时，你能在空闲的手中塑造出心灵之刃，并使用它来进行攻击。这种魔法刀刃具有以下特性："},
            {'level': 9, 'name': "灵魂之刃", 'en_name': "Soul  Blades<BR>", 'description': "你现在能能够通过念刃使用以下能力："},
        ],
    },
    # ── 牧师: 光明领域 ──
    {
        'name': "光明领域",
        'en_name': "Light Domain",
        'class_name': "牧师",
        'flavor': "携光而来，逐尽黑暗",
        'features': [
            {'level': 3, 'name': "光明领域法术Light Domain", 'en_name': "Spells<BR>", 'description': "你与此神圣领域的链接使你始终准备着特定的法术。当你到达光明领域法术表中特定的牧师等级时，你就始终准备着表中对应的法术。"},
            {'level': 3, 'name': "黎明曙光Radiance of the", 'en_name': "Dawn", 'description': "以一个魔法动作，你展现圣徽，消耗一次引导神力次数来释放出一阵闪光，覆盖一处以你为源点的30尺光环区域。该区域内的任何魔法黑暗——例如法术 黑暗术Darkness 制造的黑暗——都将被解除。此外，区域内你选择的所有生物都必须进行一次体质豁免。豁免失败者将受2d10＋你牧师等级的光耀伤害，豁免成功则伤害减半。"},
            {'level': 3, 'name': "守御之光Warding", 'en_name': "Flare", 'description': "当位于你30尺内一名你可见的生物进行攻击检定时，你能够以反应在该次攻击命中或失手前在该生物面前发出闪耀之光，迫使其该次攻击检定具有 劣势 。 你可以使用该特性的次数等于你的感知调整值（最少1次）。你在完成一次长休时重获所有已消耗的使用次数。"},
            {'level': 6, 'name': "精通守御之光Improved Warding", 'en_name': "Flare<BR>", 'description': "你在完成一次短休或长休后重新获得所有守御之光的使用次数。 此外，每当你使用守御之光时，你可以给予触发此反应的该次攻击所指定那个目标2d6+你感知调整值点临时生命值。"},
            {'level': 17, 'name': "光冕Corona of", 'en_name': "Light<BR>", 'description': "以一个魔法动作，你可以让你自己散发出日光组成的灵光，持续一分钟或直至你将其解除（无需动作）。你散发出半径60尺的明亮光照以及额外30尺的微光光照。身处该明亮光照范围中的敌人，在抵抗你的黎明曙光特性以及任何造成火焰或光耀伤害的法术而进行豁免检定时具有劣势。 你可以使用该特性的次数等同于你的感知调整值（最低为1）。你在完成一次长休时重获所有已消耗的使用次数。"},
        ],
    },
    # ── 牧师: 战争领域 ──
    {
        'name': "战争领域",
        'en_name': "War Domain",
        'class_name': "牧师",
        'flavor': "激昂气概，击溃仇敌",
        'features': [
            {'level': 3, 'name': "导引打击", 'en_name': "Guided  Strike", 'description': "当你或者距离你30尺内的一个生物在一次攻击检定中失手时，你可以消耗一次引导神力次数来让这次攻击检定获得+10加值，这可能导致该次攻击命中。当你使用此特性让另一个生物的攻击检定获得此增益时，你必须使用你的反应。"},
            {'level': 3, 'name': "战争领域法术", 'en_name': "War Domain Spells", 'description': "你与此神圣领域的链接使你始终准备着特定的法术。当你到达战争领域法术表中特定的牧师等级时，你就始终准备着表中对应的法术。"},
            {'level': 3, 'name': "战争祭司", 'en_name': "War Priest", 'description': "作为一个附赠动作，你可以发动一次武器攻击或者徒手打击。你可以使用该附赠动作的次数等于你的感知调整值（最低为1），你在完成一次长休或短休后重新获得所有的使用次数。"},
            {'level': 6, 'name': "战神祝福", 'en_name': "War God's  Blessing", 'description': "你可以使用你的引导神力来施展虔诚护盾Shield of Faith或者灵体武器Spiritual Weapon而无需消耗法术位。当你以这种方式施展其中任何一道法术时，该法术都不需要专注，且其持续时间变为1分钟，但会在你再次施展该法术、陷入失能状态或是死亡时提前结束。"},
            {'level': 17, 'name': "战争化身", 'en_name': "Avatar of  Battle", 'description': "你获得对钝击、穿刺、挥砍伤害的抗性。"},
        ],
    },
    # ── 牧师: 生命领域 ──
    {
        'name': "生命领域",
        'en_name': "Life Domain",
        'class_name': "牧师",
        'flavor': "抚慰世界，疗愈伤痛",
        'features': [
            {'level': 3, 'name': "生命门徒", 'en_name': "Disciple of  Life</STRONG></FONT>   <BR>你消耗法术位施展法术的回合中，当该法术恢复生物的生命值时，额外恢复2+消耗法术位环阶生命值。</p>    <p><FONT color=#800000><STRONG>3级：生命领域法术 Life Domain  Spells</STRONG></FONT>   <BR>你与此神圣领域的链接使你始终准备着特定的法术。当你到达生命领域法术表中特定的牧师等级时，你就始终准备着表中对应的法术。</p>    <p><STRONG>生命领域法术Life Domain Spells</STRONG>   <TABLE class=\"basic\"> <TR> <TD>       <P align=center><STRONG>牧师等级</STRONG></P></TD><TD><STRONG>准备法术</STRONG></TD></TR> <TR bgColor=#eeeeee> <TD rowspan=2>       <P align=center>3</P></TD><TD><U><EM>援助术Aid</EM></U>，<U><EM>祝福术Bless</EM></U></TD></TR> <TR  bgColor=#eeeeee><TD><U><EM>疗伤术Cure wounds</EM></U>，<U><EM>次等复原术Lesser        Restoration</EM></U>  </TD></TR> <TR> <TD>       <P align=center>5</P></TD><TD><U><EM>群体治愈真言Mass Healing        Word</EM></U>，<U><EM>回生术Revivify</EM></U>  </TD></TR> <TR  bgColor=#eeeeee> <TD>       <P align=center>7</P></TD><TD><U><EM>生命灵光Aura of Life</EM></U>，<U><EM>防死结界Death        Ward</EM></U>   </TD></TR> <TR> <TD>       <P align=center>9</P></TD><TD><U><EM>高等复原术Greater        Restoration</EM></U>，<U><EM>群体疗伤术Mass Cure  Wounds</EM></U>   </TD></TR> </TABLE></p>    <p><STRONG><FONT color=#800000>3级：维持生命 Preserve  Life", 'description': "以一个魔法动作，你展示圣徽并消耗一次引导神力来引导治疗能量恢复等于你牧师等级五倍的生命值。你选择身边30尺内处于浴血状态的生物作为此特性的目标（可以包括你），再为其分配从中获得的治疗能量。该特性至多将目标的生命值恢复至其上限的一半。"},
            {'level': 6, 'name': "神祝医者", 'en_name': "Blessed  Healer", 'description': "你为其他人施展的治疗性法术也能治疗你自己。如果你用法术位施展的一道法术为除了你自己以外的一名或更多生物恢复了生命值，此次施法后你也将立刻恢复2+该法术位环阶的生命值。"},
            {'level': 17, 'name': "极效治疗", 'en_name': "Supreme  Healing", 'description': "当你需要用一道法术或引导神力掷一枚或多枚骰子，以决定为一个生物恢复的生命数值时，你无需掷骰，直接为每个骰子取最高值。例如，一道法术为某一生物恢复2d6生命值，则其结果直接取12。"},
        ],
    },
    # ── 牧师: 诡术领域 ──
    {
        'name': "诡术领域",
        'en_name': "Trickery Domain",
        'class_name': "牧师",
        'flavor': "挑起闹剧，直面权威",
        'features': [
            {'level': 3, 'name': "诡术祝福Blessing of the", 'en_name': "Trickster", 'description': "以一个魔法动作，你可以选择自己或30尺内一个自愿生物，所选生物在进行敏捷（隐匿）检定时具有优势。此祝福持续至你完成一次长休或直至你再次使用此特性。"},
            {'level': 3, 'name': "召现分身Invoke", 'en_name': "Duplicity<BR>", 'description': "以一个附赠动作，你可以消耗一次引导神力次数来创造一个自己的完美视觉幻象并出现在你身边30尺内一个你能看见且未占据空间。该幻象是无实体的且不占据它所在的空间。幻象持续1分钟，或直至你将其解除（无需动作）或陷入失能状态。这个幻象栩栩如生，能模仿你的表情和姿势。当幻象存在时，你将获得以下好处： 施法Cast Spells。 你可以如同你在幻象所在位置施展法术，但必须使用你自己的感官。 干扰Dist..."},
            {'level': 3, 'name': "诡术领域法术Trickery Domain", 'en_name': "Spells<BR>", 'description': "你与此神圣领域的链接使你始终准备着特定的法术。当你到达诡术领域法术表中特定的牧师等级时，你就始终准备着表中对应的法术。"},
            {'level': 6, 'name': "诡诈换位Trickster's", 'en_name': "Transposition", 'description': "每当你使用附赠动作创造或移动你来自 召现分身 特性的幻象时，你都可以通过传送与幻象交换位置。"},
            {'level': 17, 'name': "精通分身Improved", 'en_name': "Duplicity", 'description': "你召现分身特性所创造的幻象在以下方面变得更加强力。 共享干扰Shared Distraction。 当你和你的盟友对位于幻象5尺内的生物进行攻击检定时具有优势。 治愈幻象Healing Illusion。 当幻象消失时，你或你选择的5尺内的一名生物恢复等同于你牧师等级的生命值。"},
        ],
    },
    # ── 野蛮人: 世界树道途 ──
    {
        'name': "世界树道途",
        'en_name': "Path of the World Tree",
        'class_name': "野蛮人",
        'flavor': "追寻多元宇宙的根系和枝杈",
        'features': [
            {'level': 3, 'name': "圣树活力", 'en_name': "Vitality of theTree", 'description': "你的狂暴浸润着世界树的生命力。你获得以下增益： 活力之涌Vitality Surge 。 当你激活狂暴时，你获得等于你野蛮人等级的 临时生命值 。 赐命之源Life-Giving Force 。 你的狂暴激活期间，在你的每个回合开始时，你可以赋予位于你10尺内的另一名生物 临时生命值 。投掷等于你狂暴伤害加值数量的d6，将它们相加，即是该生物获得的临时生命值。当你的狂暴结束时，剩余的临时生命..."},
            {'level': 6, 'name': "灵树枝杈", 'en_name': "Branches of the Tree", 'description': "你的狂暴激活期间，每当你可见的位于你30尺内的生物的回合开始时，你能够以反应在其周围召唤世界树的灵体枝条。目标必须成功通过一次力量豁免（DC等于8+你的力量调整值+你的熟练加值），否则将被传送到位于你5尺内的你可见的未占据空间内或距离你最近的你可见的未占据空间内。目标被你传送后，你可以令其速度降为0，持续至当前回合结束。"},
            {'level': 10, 'name': "根击千钧", 'en_name': "Battering Roots<BR>", 'description': "世界树的卷须将你的武器延长。你的回合内，你持用的任何具有 重型 或 多用 词条的近战武器的触及增加10尺。当你在你的回合内以该武器命中时，除了激活这把武器本身具有的其他精通词条外，你还可以激活 推离 或 失衡 精通词条。"},
            {'level': 14, 'name': "世界树之奇旅", 'en_name': "Travel along the Tree", 'description': "当你激活狂暴时，你可以传送至多60尺的距离，到一处你可见的未占据空间中。在你的狂暴激活期间，你也能够以一个附赠动作来进行传送。 此外，每次狂暴期间仅一次，你可以使传送的距离提升至150尺，并可以选择带上至多6个位于你10尺内的自愿生物同你一起传送。每个其他生物都将被传送至位于你目的地10尺内的你选择的未占据空间中。"},
        ],
    },
    # ── 野蛮人: 兽心道途 ──
    {
        'name': "兽心道途",
        'en_name': "Path of Wild Heart",
        'class_name': "野蛮人",
        'flavor': "与动物世界一同漫步",
        'features': [
            {'level': 3, 'name': "动物语者", 'en_name': "Animal Speaker", 'description': "你可以施展法术 野兽知觉Beast Sense 与 动物交谈Speak With Animals ，仅限仪式施展。感知是你这些法术的施法属性。"},
            {'level': 3, 'name': "兽性狂暴", 'en_name': "Rage of the Wilds", 'description': "你的狂暴解放来自动物的原初之力。每当你激活狂暴时，你从下列选项中选择一项。 熊Bear。 狂暴激活期间，你具有除力场、心灵、暗蚀、光耀外所有伤害类型的抗性。 鹰Eagle。 当你激活狂暴时，作为你进入狂暴的附赠动作的一部分，你可以同时执行 撤离 与 疾走 动作。狂暴激活期间，你也能够以一个附赠动作同时执行这两个动作。 狼Wolf。 狂暴激活期间，你的盟友对位于你5尺内的敌人进行的攻击检定具有..."},
            {'level': 6, 'name': "兽之形貌", 'en_name': "Aspect of the Wilds", 'description': "你从下列选项中自选一项能力获得。当你完成一次 长休 时，你可以改变你的选择。 枭Owl。 你具有60尺 黑暗视觉 。如果你已经具有黑暗视觉，你的黑暗视觉范围增加60尺。 豹Panther。 你具有等于你速度的攀爬速度。 鲑Salmon。 你具有等于你速度的游泳速度。"},
            {'level': 10, 'name': "自然语者", 'en_name': "Nature Speaker", 'description': "你可以施展法术 问道自然Commune With Nature ，仅限仪式施展。感知是你该法术的施法属性。"},
            {'level': 14, 'name': "兽力威能", 'en_name': "Power of the Wilds", 'description': "每当你激活狂暴时，你从下列选项中选择一项。 猎鹰Falcon。 狂暴激活期间，只要你没有着装任何护甲*，你就具有等于你速度的飞行速度。 雄狮Lion。 狂暴激活期间，任何位于你5尺内的敌人不以你（或另一个选择该项能力的野蛮人）为目标的攻击检定具有 劣势 。 角羊Ram。 狂暴激活期间，当你的近战攻击命中一名体型不超过大型的生物时，你可以令其陷入 倒地 状态。 译注：武僧的无甲防御中特别强调了..."},
        ],
    },
    # ── 野蛮人: 狂战士道途 ──
    {
        'name': "狂战士道途",
        'en_name': "Path of the Berserker",
        'class_name': "野蛮人",
        'flavor': "以心头强烈的愤怒进入狂暴",
        'features': [
            {'level': 3, 'name': "狂怒", 'en_name': "Frenzy <BR>", 'description': "狂暴激活期间，在你使用鲁莽攻击的回合中，你基于力量的攻击首次命中时，对目标造成额外伤害。投掷等于你狂暴伤害加值数量的d6，将它们相加，即是你造成的额外伤害。额外伤害类型与此次攻击所使用的武器或 徒手打击 造成的伤害类型相同。"},
            {'level': 6, 'name': "无我狂暴", 'en_name': "Mindless Rage", 'description': "狂暴激活期间，你具有 魅惑 与 恐慌 状态的免疫。当你进入狂暴时，若你已陷入魅惑或恐慌，你陷入的这些状态立即结束。"},
            {'level': 10, 'name': "报偿", 'en_name': "Retaliation", 'description': "当一名位于你5尺内的生物对你造成伤害时，你能够以反应使用武器或 徒手打击 对其发动一次近战攻击。"},
            {'level': 14, 'name': "威慑之姿", 'en_name': "Intimidating Presence <BR>", 'description': "以一个附赠动作，你可以用你那令人魂消胆丧的面相，在原初之力的辅助下将恐惧打入他者内心。当你如此做时，每个位于以你为源点的30尺 光环 区域内你所选择的生物必须进行一次感知豁免检定（DC等于8＋你的力量调整值＋你的熟练加值）。豁免失败则陷入 恐慌 状态，持续1分钟。陷入恐慌的生物在其每个回合结束时重复豁免，成功则终止其身上的该效应。 此特性一经使用，直至完成 长休 你都无法再次使用。你也可以消..."},
        ],
    },
    # ── 野蛮人: 狂热者道途 ──
    {
        'name': "狂热者道途",
        'en_name': "Path of the Zealot",
        'class_name': "野蛮人",
        'flavor': "与神结合的至高愉悦狂暴体验",
        'features': [
            {'level': 3, 'name': "神性之怒", 'en_name': "Divine Fury", 'description': "你可以引导神性的怒火，将其注入打击之中。你的狂暴激活期间，你的每个回合中你首次以武器或 徒手打击 命中的生物将受到等于1d6+你野蛮人等级的一半（向下取整）的额外伤害。额外伤害的伤害类型为光耀或暗蚀，在每次造成伤害时由你选择伤害类型。"},
            {'level': 3, 'name': "神之勇者", 'en_name': "Warrior of the Gods", 'description': "某个神圣实体对你施以援手以确保你总能继续战斗。你获得一个有着4枚d12的治疗池，你可以用其中的骰子治愈自身。以一个附赠动作，你可以消耗治疗池中任意枚骰子来恢复你的生命值。投掷所有你消耗的骰子，将它们相加，即是你以此恢复的生命值。 当你完成一次 长休 时，你的治疗池重获所有已消耗的骰子。 治疗池中骰子的最大数量将会在你到达特定野蛮人等级时增加，分别为6级时增加至5枚，12级时增加至6枚，17级..."},
            {'level': 6, 'name': "专心炽志", 'en_name': "Fanatical Focus", 'description': "每次狂暴期间仅一次，若你失败于某次豁免检定，你可以重骰这次检定并在检定中获得等于你的狂暴伤害加值的加值，你必须使用重骰后的结果。"},
            {'level': 10, 'name': "狂热威仪", 'en_name': "Zealous Presence", 'description': "以一个附赠动作，你以满腔神圣能量发出战吼。选择至多十名位于你60尺内的生物，直至你的下个回合开始，他们的攻击检定和豁免检定具有 优势 。 此特性一经使用，直至完成 长休 你都无法再次使用。你也可以消耗一次狂暴使用次数（无需动作）来重置此特性的使用权。"},
            {'level': 14, 'name': "神之狂暴", 'en_name': "Rage of the  Gods<BR>", 'description': "当你激活狂暴时，你可以呈现出圣斗士姿态。圣斗士姿态持续1分钟，且在你生命值降至0时提前结束。此特性一经使用，直至完成 长休 你都无法再次使用。 处于圣斗士姿态期间，你获得以下增益。"},
        ],
    },
    # ── 魔契师: 天界宗主 ──
    {
        'name': "天界宗主",
        'en_name': "Celestial Patron",
        'class_name': "魔契师",
        'flavor': "呼唤天堂诸界之伟力",
        'features': [
            {'level': 3, 'name': "天界法术", 'en_name': "Celestial  Spells<BR>", 'description': "宗主赐予的魔法使你始终准备着特定的法术。当你到达 天界法术 表中特定的魔契师等级时，你就始终准备着表中对应的法术。"},
            {'level': 3, 'name': "治愈之光", 'en_name': "Healing  Light", 'description': "你获得了引导天界能量以治愈伤口的能力。它是一个有着1+你的魔契师等级枚d6骰的骰池，用以施展你的治愈能力。 以一个附赠动作，你可以消耗骰池中的任意数量的骰子，来治疗你自己或一个你可见的位于你60尺内的生物。每次你能消耗的最大骰子数量等于你的魅力调整值（至少一枚）。投掷全部被消耗骰子，这些骰值相加的总值即为所能恢复的生命值。 当你完成一次 长休 时，你的骰池将重获所有已消耗的骰子。"},
            {'level': 6, 'name': "光耀之魂", 'en_name': "Radiant  Soul<BR></STRONG></FONT>你与你天界宗主的链接允许你成为光耀能量的渠道。你获得对光耀伤害的抗性。每回合一次，当一个你施展的法术造成光耀伤害或火焰伤害时，你可以将你的魅力调整值加到该法术对其中一个目标所造成的伤害上。</p>  <p><STRONG><FONT color=#800000>10级：天界韧性 Celestial  Resilience", 'description': "每当你使用 秘法回流 ，或是完成一次 短休 或 长休 后，你都会获得一定的 临时生命值 。其数值等于你的魔契师等级+你的魅力调整值。此外，在你获得该临时生命值时，你还可以选择至多五个你可见的生物。这些生物也会获得等同于你魔契师等级的一半+你的魅力调整值的临时生命值。"},
            {'level': 14, 'name': "灼光复仇", 'en_name': "Searing  Vengeance", 'description': "当你或位于你60尺内的一名盟友将要进行一次 死亡豁免 时，你可以释放出一道光能来拯救那名生物。那名生物恢复等于其生命值上限一半的生命值，且可以选择结束自身的 倒地 状态。之后，每个由你选择的位于那名生物30尺内的生物都将受到2d8+你的魅力调整值的 光耀 伤害，并陷入 目盲 状态直至当前回合结束。 此特性一经使用，直至完成 长休 你都无法再次使用。"},
        ],
    },
    # ── 魔契师: 旧日支配者宗主 ──
    {
        'name': "旧日支配者宗主",
        'en_name': "Great Old One Patron",
        'class_name': "魔契师",
        'flavor': "洞见不可名状的存在与知识",
        'features': [
            {'level': 3, 'name': "旧日支配者法术", 'en_name': "Great Old One  Spells", 'description': "宗主赐予的魔法使你始终准备着特定的法术。当你到达 旧日支配者法术 表中特定的魔契师等级时，你就始终准备着表中对应的法术。"},
            {'level': 3, 'name': "唤醒心灵", 'en_name': "Awakened  Mind", 'description': "你的心灵可以与其他心灵建立感应联系。以一个附赠动作，你指定一个位于你30尺内的可见生物并创造一道心灵连结。当你与目标相距不超过等于你魅力调整值（至少1英里）的英里数时，你们便可以互相用心灵感应交谈。为了理解彼此，你们都必须在心灵交流中使用一种对方具有的语言。 这道心灵连结持续等于你魔契师等级的分钟。它也会在你使用此特性形成另一道心灵连结时提前结束。"},
            {'level': 3, 'name': "心灵法术", 'en_name': "Psychic Spells", 'description': "当你施展一道造成伤害的魔契师法术时，你可以将其伤害类型改为心灵伤害。此外，当你施展一道惑控/幻术学派的魔契师法术时，你可以令该法术不再具有言语与姿势成分。"},
            {'level': 6, 'name': "锐眼斗士", 'en_name': "Clairvoyant  Combatant", 'description': "当你用 唤醒心灵 与一个生物形成心灵连结时，你可以迫使对方进行一次对抗你法术豁免DC的感知豁免。若豁免失败，则该生物在连结期间对你进行的攻击检定具有 劣势 ，而你对它进行的攻击检定具有 优势 。 此特性一经使用，直至完成 短休 或 长休 你都无法再次使用。你也可以消耗一个 契约魔法 法术位（无需动作）来重置此特性的使用权。"},
            {'level': 10, 'name': "骇异恶咒", 'en_name': "Eldritch Hex", 'description': "你的异界宗主给予你强大的诅咒之力。你始终准备着 脆弱诅咒Hex 法术。当你施展脆弱诅咒并选择了一项属性时，目标在法术持续时间内还会在以这项属性进行的豁免上具有 劣势 。"},
            {'level': 10, 'name': "思维之盾", 'en_name': "Thought  Shield", 'description': "除非获得你的允许，否则你的思维无法被心灵感应或者其他手段阅读。此外你还具有对心灵伤害的抗性，且每当一个生物对你造成心灵伤害时，该生物将受到与你承受的同等的伤害。"},
            {'level': 14, 'name': "创造奴仆", 'en_name': "Create  Thrall", 'description': "当你施展 异怪召唤术Summon Aberration 时，你可以修改此法术使其无需 专注 。以此法施展时，此法术的持续时间将变为1分钟，且召唤来的异怪拥有等于你魔契师等级+你的魅力调整值的 临时生命值 。 此外，该异怪在每个回合中第一次命中一个被你的 脆弱诅咒Hex 影响的生物时，该异怪会对目标额外造成等于此法术附加伤害的心灵伤害。"},
        ],
    },
    # ── 魔契师: 至高妖精宗主 ──
    {
        'name': "至高妖精宗主",
        'en_name': "Archfey Patron",
        'class_name': "魔契师",
        'flavor': "与喜怒无常的妖精交易",
        'features': [
            {'level': 3, 'name': "至高妖精法术", 'en_name': "Archfey  Spells<BR>", 'description': "宗主赐予的魔法使你始终准备着特定的法术。当你到达 至高妖精法术 表中特定的魔契师等级时，你就始终准备着表中对应的法术。"},
            {'level': 3, 'name': "妖精步伐", 'en_name': "Steps of the  Fey<BR>", 'description': "你的宗主授予你在位面的边界之间穿行的能力。你可以无需消耗法术位地施展 迷踪步Misty Step ，次数等于你的魅力调整值（至少1次），并在完成一次 长休 时重获所有已消耗的次数。 此外，每当你施展该法术时，你都可以选择造成下列额外效应之一： 复苏步伐Refreshing Step。 在你传送之后，你或一个你可见的位于你10尺内的生物立刻获得1d10 临时生命值 。 嘲弄步伐Taunting..."},
            {'level': 6, 'name': "雾遁", 'en_name': "Misty  Escape<BR>", 'description': "当你受到伤害时，你可以用反应施展 迷踪步Misty Step 。 此外，你的 妖精步伐 获得以下选项。 无踪步伐Disappearing Step。 你获得 隐形 状态，持续到你的下一回合开始或你进行攻击检定、造成伤害、或是施展一道法术之后。 惊惧步伐Dreadful Step。 位于你传送前或传送后的空间（由你选择）5尺内的生物必须进行一次对抗你法术豁免DC的感知豁免，豁免失败则受到2d1..."},
            {'level': 10, 'name': "斗转星移", 'en_name': "Beguiling  Defenses<BR>", 'description': "你的宗主教会了你如何保护自己的心和身。你获得对 魅惑 状态的免疫。 此外，当一个你能看见的敌人的攻击检定命中你后，你可以立刻使用反应令该次攻击的伤害减半（向下取整），且你可以迫使攻击者进行一次对抗你法术豁免DC的感知豁免，豁免失败则会受到一定的心灵伤害，具体数值等同于你本次承受的实际伤害。此反应一经使用，直至完成 长休 你都无法再次使用。你也可以消耗一个 契约魔法 法术位（无需动作）来重置此..."},
            {'level': 14, 'name': "醉心魔法", 'en_name': "Bewitching  Magic<BR>", 'description': "你的宗主赋予你将魔法与传送之力编织在一起的能力。当你以一个动作消耗法术位施展一道 幻术 或 惑控 法术时，你可以无需法术位地立刻施展 迷踪步Misty Step 作为该动作的一部分。"},
        ],
    },
    # ── 魔契师: 邪魔宗主 ──
    {
        'name': "邪魔宗主",
        'en_name': "Fiend Patron",
        'class_name': "魔契师",
        'flavor': "与下层位面之物签订契约",
        'features': [
            {'level': 3, 'name': "邪魔法术", 'en_name': "Fiend  Spells<BR>", 'description': "宗主赐予的魔法使你始终准备着特定的法术。当你到达 邪魔法术 表中特定的魔契师等级时，你就始终准备着表中对应的法术。"},
            {'level': 3, 'name': "黑暗赐福", 'en_name': "Dark One's  Blessing", 'description': "当你将一个敌人的生命值降至0时，你获得等于你的魅力调整值＋你的魔契师等级的 临时生命值 （最低为1）。而若其他人将一个位于你10尺内的你的敌人的生命值降至0时，你也会获得此增益。"},
            {'level': 6, 'name': "黑暗强运", 'en_name': "Dark One's Own  Luck", 'description': "你可以呼唤你的宗主将命运改写为对你有利的方向。当你进行属性检定或豁免检定时，你可以使用该特性为此次掷骰增添一个d10骰。你可在看到掷骰结果后，其结果生效前使用该特性。 你可以使用此特性的次数等于你的魅力调整值（至少一次），但你在一次检定中只能使用此特性一次。你在完成一次 长休 后恢复所有已消耗的次数。"},
            {'level': 10, 'name': "邪魔体魄", 'en_name': "Fiendish  Resilience", 'description': "每当你完成一次 短休 或 长休 时，选择一种除 力场 之外的伤害类型。直到你以此特性选择另外一种伤害类型前，你都具有对所选伤害类型的抗性。"},
            {'level': 14, 'name': "直坠噩梦", 'en_name': "Hurl Through  Hell", 'description': "每回合一次，当你以攻击检定命中一个生物时，你可以将目标瞬间传送并拉入下层位面。目标必须进行一次对抗你法术豁免DC的魅力豁免，豁免失败则该生物立刻消失并坠入如同噩梦一般的景色中。若目标并非邪魔，则它会受到8d10点心灵伤害。目标还会陷入失能状态直至你的下一回合结束，此时目标返回先前所占据的空间、或是最近的未被占据空间。 此特性一经使用，直至完成 长休 你都无法再次使用。你也可以消耗一个 契约魔..."},
        ],
    },
]