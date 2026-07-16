"use client";

interface DeathSaveTrackerProps {
  successes: number;
  failures: number;
  onRoll: () => void;
}

export function DeathSaveTracker({ successes, failures, onRoll }: DeathSaveTrackerProps) {
  return (
    <div className="bg-red-950 border border-red-800 rounded p-2 space-y-2">
      <div className="text-xs font-bold text-red-400">💀 死亡豁免</div>

      {/* 成功 */}
      <div className="flex items-center gap-1">
        <span className="text-[10px] text-green-500 w-6">成功</span>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className={`w-3 h-3 rounded-full ${
              i < successes ? "bg-green-500" : "bg-neutral-700"
            }`}
          />
        ))}
      </div>

      {/* 失败 */}
      <div className="flex items-center gap-1">
        <span className="text-[10px] text-red-500 w-6">失败</span>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className={`w-3 h-3 rounded-full ${
              i < failures ? "bg-red-500" : "bg-neutral-700"
            }`}
          />
        ))}
      </div>

      <button
        onClick={onRoll}
        className="w-full px-2 py-1 bg-red-800 border border-red-600 rounded text-xs hover:bg-red-700"
      >
        掷死亡豁免 d20
      </button>
    </div>
  );
}
