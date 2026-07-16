"use client";

export type GameMode = "exploration" | "combat" | "social";

interface ModeSwitcherProps {
  mode: GameMode;
  onChange: (mode: GameMode) => void;
}

const MODES: { id: GameMode; label: string }[] = [
  { id: "exploration", label: "🗺️ 探索" },
  { id: "combat", label: "⚔️ 战斗" },
  { id: "social", label: "💬 社交" },
];

export function ModeSwitcher({ mode, onChange }: ModeSwitcherProps) {
  return (
    <div className="flex gap-1">
      {MODES.map((m) => (
        <button
          key={m.id}
          onClick={() => onChange(m.id)}
          className={`px-2 py-0.5 rounded text-[10px] ${
            mode === m.id
              ? "bg-amber-400 text-neutral-900"
              : "bg-neutral-800 border border-neutral-700 text-neutral-400"
          }`}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}
