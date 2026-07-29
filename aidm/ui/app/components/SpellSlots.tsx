"use client";

// 后端 spell_slots 是 Record<string, number>（level → remaining）
// 无 total/max 字段，因此仅展示剩余数对应的蓝色方块

interface SpellSlotsProps {
  slots: Record<string, number>;
}

export function SpellSlots({ slots }: SpellSlotsProps) {
  const entries = Object.entries(slots).sort(([a], [b]) =>
    parseInt(a) < parseInt(b) ? -1 : 1
  );

  if (entries.length === 0) return null;

  return (
    <div className="flex-col" style={{ gap: 4 }}>
      {entries.map(([level, remaining]) => (
        <div key={level} style={{ marginBottom: 4 }}>
          <span style={{ fontSize: 10, color: "var(--text-tertiary)" }}>
            {level}环 ({remaining})
          </span>
          <div className="spell-slots" style={{ marginTop: 2 }}>
            {remaining > 0 ? (
              Array.from({ length: remaining }).map((_, i) => (
                <div key={i} className="spell-slot available">{level}</div>
              ))
            ) : (
              <div className="spell-slot used">0</div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
