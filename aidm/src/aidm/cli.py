"""P5 交互层（CLI）— 交互式跑团，调 P3 硬性判定链 + P1 持久化。

用法: PYTHONPATH=src python -m aidm.cli
（Next.js 前端为可选增强层；CLI 是 BUILD.md Phase 1 允许的交互方式）
"""

from __future__ import annotations

import sys

from .brain import graph
from .stats import models, store


def bootstrap_character(name: str = "勇者") -> tuple[models.Campaign, models.Character]:
    """建一个默认战役+5级战士角色（已存在则复用）。"""
    camp = store.create_campaign(name + "的冒险")
    ch = models.Character(name=name, race="人类", char_class="战士", level=5, campaign_id=camp.id)
    ch.set_abilities({"str": 16, "dex": 10, "con": 15, "int": 10, "wis": 12, "cha": 10})
    ch.hp_max = 38; ch.hp_current = 38; ch.ac = 18; ch.speed = 30
    ch = store.save_character(ch)
    return camp, ch


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 50)
    print(" AI DM — D&D 5E 跑团（硬性判定链 + HITL）")
    print("=" * 50)
    name = input("角色名（回车=勇者）: ").strip() or "勇者"
    hitl_input = input("启用 HITL 关键判定确认？(y/N): ").strip().lower()
    hitl = hitl_input in ("y", "yes")
    camp, ch = bootstrap_character(name)
    print(f"\n角色就绪: {ch.name} Lv{ch.level} {ch.char_class}  HP {ch.hp_current}/{ch.hp_max}  AC {ch.ac}"
          + ("  [HITL开]" if hitl else ""))
    print("输入行动（自然语言），如：我用长剑攻击那只AC15的哥布林 / 我对哥布林施展火球术。输入 '退出' 结束。\n")

    thread = "cli"

    def responder(q):
        print(f"\n  [HITL] {q.get('question','确认?')}  证据={q.get('evidence',[])}")
        return input("  DM> ").strip() or "y"

    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line in ("退出", "exit", "quit"):
            break
        if not line:
            continue
        try:
            out = graph.run_turn(line, camp.id, ch.id, thread_id=thread,
                                 hitl=hitl, responder=responder if hitl else None)
        except Exception as e:
            print(f"[错误] {e}")
            continue
        # 若被中断且无 responder（理论上不会，hitl 时已传 responder）
        if out.get("__interrupt__"):
            print("  [HITL] 判定暂停，需恢复（略）")
            continue
        if out.get("narration"):
            print(f"\n{out['narration']}")
        dice = out.get("dice", {})
        if dice:
            k = dice.get("kind")
            if k == "attack":
                hit = "命中" if dice.get("hit") else "未中"
                crit = " 重击!" if dice.get("crit") else ""
                print(f"  [骰子] 攻击 d20={dice.get('d20')} 总{dice.get('attack_total')} vs AC{dice.get('target_ac')} → {hit}{crit}", end="")
                if dice.get("damage") is not None:
                    print(f"  伤害 {dice['damage']}({dice.get('damage_type','')})")
                else:
                    print()
            elif k == "cast":
                print(f"  [骰子] 施法 DC{dice.get('spell_save_dc')} " +
                      (f"法术攻击总{dice.get('spell_attack_total')} 命中{dice.get('hit')}" if dice.get("spell_attack") is True
                       else f"豁免{'成功' if dice.get('save_success') else '失败'}(总{dice.get('save_total')})"),
                      end="")
                if dice.get("damage") is not None:
                    print(f"  伤害 {dice['damage']}({dice.get('damage_type','')}) [{dice.get('spell_dice')}]")
                else:
                    print()
            elif k == "ability_check":
                print(f"  [骰子] 属性检定 d20={dice.get('d20')} 总{dice.get('check_total')} vs DC{dice.get('dc')} → {'成功' if dice.get('success') else '失败'}")
            elif k == "start_combat":
                print(f"  [战斗] 先攻: {[(c['name'],c['init']) for c in dice.get('initiative_order',[])]}")
        ch = store.get_character(ch.id)
        print(f"  [HP {ch.hp_current}/{ch.hp_max}]  剧情已存档\n")


if __name__ == "__main__":
    main()
