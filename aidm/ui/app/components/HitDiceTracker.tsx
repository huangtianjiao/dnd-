"use client";

interface HitDiceTrackerProps {
  total: number;
  remaining: number;
  faces: number;
  onRoll: () => void;
}

export function HitDiceTracker({
  total,
  remaining,
  faces,
  onRoll,
}: HitDiceTrackerProps) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center">
        <span className="text-[10px] text-neutral-500 uppercase">生命骰</span>
        <span className="text-[10px] text-neutral-400">
          {remaining}/{total} d{faces}
        </span>
      </div>
      <div className="flex gap-0.5 flex-wrap">
        {Array.from({ length: total }).map((_, i) => (
          <div
            key={i}
            className={`w-4 h-4 rounded border text-[8px] flex items-center justify-center ${
              i < remaining
                ? "bg-red-800 border-red-600 text-red-200"
                : "bg-neutral-800 border-neutral-700 text-neutral-600"
            }`}
          >
            {faces}
          </div>
        ))}
      </div>
      {remaining > 0 && (
        <button
          onClick={onRoll}
          className="w-full px-2 py-1 bg-red-900 border border-red-700 rounded text-[10px] hover:bg-red-800"
        >
          掷生命骰恢复HP
        </button>
      )}
    </div>
  );
}
