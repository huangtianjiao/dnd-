"use client";

interface QuickActionsProps {
  onAction: (action: string) => void;
}

const SKILLS = [
  { id: "investigate", label: "调查" },
  { id: "perception", label: "感知" },
  { id: "stealth", label: "潜行" },
  { id: "athletics", label: "运动" },
  { id: "insight", label: "洞悉" },
  { id: "survival", label: "求生" },
];

export function QuickActions({ onAction }: QuickActionsProps) {
  return (
    <div className="space-y-1">
      <div className="text-[10px] text-neutral-500 uppercase">快捷检定</div>
      <div className="grid grid-cols-3 gap-1">
        {SKILLS.map((s) => (
          <button
            key={s.id}
            onClick={() => onAction(s.label)}
            className="px-1 py-1 bg-neutral-800 border border-neutral-700 rounded text-[10px] hover:border-amber-400"
          >
            {s.label}
          </button>
        ))}
      </div>
    </div>
  );
}
