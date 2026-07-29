"use client";

// 生命骰只读展示（无独立掷骰 API，消耗通过短休）

interface HitDiceTrackerProps {
  total: number;
  remaining: number;
  faces: number;
}

export function HitDiceTracker({ total, remaining, faces }: HitDiceTrackerProps) {
  return (
    <div className="hit-dice-row">
      {Array.from({ length: total }).map((_, i) => (
        <div
          key={i}
          className={`hd-die ${i < remaining ? "" : "used"}`}
          title={i < remaining ? `可用 d${faces}` : "已消耗"}
        >
          d{faces}
        </div>
      ))}
    </div>
  );
}
