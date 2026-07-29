"use client";

interface ConditionTrackerProps {
  conditions: string[];
}

// 条件名 → CSS class 后缀（匹配 globals.css 中的 .cond-chip.cond-* 类）
const CONDITION_CLASS: Record<string, string> = {
  "中毒": "poisoned",
  "魅惑": "charmed",
  "耳聋": "deafened",
  "恐慌": "frightened",
  "受擒": "grappled",
  "失能": "incapacitated",
  "隐形": "invisible",
  "麻痹": "paralyzed",
  "石化": "petrified",
  "力竭": "exhaustion",
  "倒地": "prone",
  "束缚": "restrained",
  "震慑": "stunned",
  "昏迷": "unconscious",
  "目盲": "blinded",
  "祝福术": "blessed",
  "灵感": "inspired",
  "专注": "concentrating",
};

function condClass(name: string): string {
  // 先查精确匹配，再查包含关系
  if (CONDITION_CLASS[name]) return `cond-chip cond-${CONDITION_CLASS[name]}`;
  for (const [key, val] of Object.entries(CONDITION_CLASS)) {
    if (name.includes(key)) return `cond-chip cond-${val}`;
  }
  return "cond-chip";
}

export function ConditionTracker({ conditions }: ConditionTrackerProps) {
  return (
    <div className="condition-tracker">
      {conditions.length === 0 ? (
        <span style={{ fontSize: 10, color: "var(--text-tertiary)" }}>无状态</span>
      ) : (
        conditions.map((c, i) => (
          <span key={i} className={condClass(c)}>
            {c}
          </span>
        ))
      )}
    </div>
  );
}
