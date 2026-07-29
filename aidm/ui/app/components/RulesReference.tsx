"use client";

const RULES = [
  {
    title: "d20 检定公式",
    html: <>d20 + 修正值 vs DC<br/><b>修正值</b> = 属性调整值 + 熟练加值(如熟练)<br/><b>自然1</b> = 总是失败 · <b>自然20</b> = 总是成功</>,
  },
  {
    title: "DC 难度表",
    html: <><b>5</b> 非常简单 · <b>10</b> 简单<br/><b>15</b> 中等 · <b>20</b> 困难<br/><b>25</b> 非常困难 · <b>30</b> 几乎不可能</>,
  },
  {
    title: "优势 / 劣势",
    html: <><b>优势</b>: 掷两个d20取高<br/><b>劣势</b>: 掷两个d20取低<br/>多个优势/劣势不叠加——只要有任一来源的优势和劣势就互相抵消</>,
  },
  {
    title: "回合结构",
    html: <>每回合可执行：<br/>· <b>移动</b> (速度尺数，可拆分)<br/>· <b>动作</b> (攻击/施法/闪避/协助/疾步/脱离/躲藏/使用物品)<br/>· <b>附赠动作</b> (仅当特性/法术允许)<br/>· <b>反应</b> (每轮1次，在他人回合触发)<br/>· <b>免费互动</b> (拔武器/开门等)</>,
  },
  {
    title: "攻击流程",
    html: <>1. 声明攻击目标<br/>2. 投 d20 + 攻击修正值<br/>3. 与目标 AC 比较 → 命中/未命中<br/>4. 命中则投伤害骰<br/>5. 暴击(自然20): 伤害骰翻倍</>,
  },
  {
    title: "施法检查清单",
    html: <>1. <b>施法时间</b>: 动作/附赠/反应/分钟<br/>2. <b>法术位</b>: 消耗对应环阶<br/>3. <b>成分</b>: V(言语) S(姿态) M(材料)<br/>4. <b>效果解决</b>: 攻击检定 or 豁免检定<br/>5. <b>专注</b>: 部分法术需专注维持<br/><span style={{ color: "var(--text-red)" }}>受伤害时专注DC = 10 或 伤害值/2(取高)</span></>,
  },
  {
    title: "休息机制",
    html: <><b>短休</b> (1小时): 消耗Hit Dice回HP, 恢复部分职业特性<br/><b>长休</b> (8小时): HP回满, 恢复一半Hit Dice, 法术位全恢复<br/><span style={{ color: "var(--text-tertiary)" }}>长休后需消耗1份口粮</span></>,
  },
  {
    title: "死亡豁免",
    html: <>HP = 0 时开始:<br/>· 每回合掷 d20 (无修饰)<br/>· <b>10+</b>: 1次成功<br/>· <b>9-</b>: 1次失败<br/>· <b>自然20</b>: 恢复1HP<br/>· <b>自然1</b>: 2次失败<br/>· 3次成功 → 稳定<br/>· 3次失败 → 死亡</>,
  },
];

export function RulesReference() {
  return (
    <div className="rules-ref">
      {RULES.map((r) => (
        <div key={r.title} className="rules-section">
          <div className="rs-title">{r.title}</div>
          <div className="rs-content">{r.html}</div>
        </div>
      ))}
    </div>
  );
}
