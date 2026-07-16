"use client";

const RULES = [
  {
    title: "d20 检定",
    content: "d20 + 属性调整值 + 熟练加值（如适用）≥ DC = 成功\nDC 参考: 非常容易5 / 容易10 / 中等15 / 困难20 / 非常困难25 / 近乎不可能30",
  },
  {
    title: "优势与劣势",
    content: "优势: 掷两个 d20 取高\n劣势: 掷两个 d20 取低\n不叠加: 多个优势仍只掷两骰\n抵消: 同时有优势和劣势只掷一骰",
  },
  {
    title: "攻击检定",
    content: "d20 + 攻击加值 ≥ 目标 AC = 命中\n天然 20: 必命中且暴击（伤害骰翻倍）\n天然 1: 必失手\n重击: 所有伤害骰 × 2（常数不加倍）",
  },
  {
    title: "死亡豁免",
    content: "HP 归零时进入濒死状态\n每轮掷 d20（无修正）:\n  ≥ 10: 记一次成功\n  < 10: 记一次失败\n  天然 20: 恢复 1 HP\n  天然 1: 记两次失败\n3 次成功 → 稳定\n3 次失败 → 死亡",
  },
  {
    title: "休息机制",
    content: "短休（1小时）: 消耗生命骰恢复 HP，恢复部分职业特性\n长休（8小时）: HP 回满，恢复一半生命骰，法术位全恢复，力竭 -1\n限制: 每 24 小时最多获益一次长休",
  },
];

export function RulesReference() {
  return (
    <div className="space-y-2 text-[10px]">
      {RULES.map((r) => (
        <details key={r.title} className="border border-neutral-800 rounded">
          <summary className="px-2 py-1 cursor-pointer text-amber-400 hover:bg-neutral-800/50">
            {r.title}
          </summary>
          <pre className="px-2 py-1 whitespace-pre-wrap text-neutral-400 font-sans">
            {r.content}
          </pre>
        </details>
      ))}
    </div>
  );
}
