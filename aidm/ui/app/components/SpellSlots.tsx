"use client";

interface SpellSlotsProps {
  slots: Record<string, { total: number; remaining: number }>;
  onUse?: (level: string) => void;
}

export function SpellSlots({ slots, onUse }: SpellSlotsProps) {
  const entries = Object.entries(slots).sort(([a], [b]) =>
    parseInt(a) < parseInt(b) ? -1 : 1
  );

  if (entries.length === 0) return null;

  return (
    <div className="space-y-1">
      <div className="text-[10px] text-neutral-500 uppercase">法术位</div>
      <div className="space-y-0.5">
        {entries.map(([level, { total, remaining }]) => (
          <button
            key={level}
            onClick={() => onUse?.(level)}
            disabled={remaining === 0}
            className="w-full flex items-center gap-1 text-[10px] px-1 py-0.5 rounded hover:bg-neutral-800 disabled:opacity-40"
          >
            <span className="text-neutral-500 w-8">{level}环</span>
            <div className="flex gap-0.5">
              {Array.from({ length: total }).map((_, i) => (
                <div
                  key={i}
                  className={`w-2.5 h-2.5 rounded-sm ${
                    i < remaining ? "bg-blue-500" : "bg-neutral-700"
                  }`}
                />
              ))}
            </div>
            <span className="text-neutral-400 ml-auto">
              {remaining}/{total}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
