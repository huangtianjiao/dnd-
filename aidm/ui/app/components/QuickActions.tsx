"use client";

interface QuickActionsProps {
  onQuickCheck: (skill: string) => void;
}

const SKILLS = [
  "调查",
  "感知",
  "潜行",
  "运动",
  "洞悉",
  "生存",
];

export function QuickActions({ onQuickCheck }: QuickActionsProps) {
  return (
    <div className="quick-actions">
      <span className="qa-label">快捷检定:</span>
      {SKILLS.map((s) => (
        <button key={s} className="qa-btn" onClick={() => onQuickCheck(s)}>
          {s}
        </button>
      ))}
    </div>
  );
}
