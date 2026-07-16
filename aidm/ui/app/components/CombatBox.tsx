"use client";

import type { CombatData } from "../lib/types";

export function CombatBox({ combat }: { combat: CombatData | null }) {
  if (!combat || !combat.active) {
    return <div className="text-xs text-neutral-600">非战斗状态</div>;
  }

  return (
    <>
      <div className="text-sm font-bold text-red-400">⚔️ 战斗中</div>
      <div className="text-xs text-neutral-500">第 {combat.round} 轮</div>

      {combat.initiative_order && (
        <div className="space-y-1 mt-2">
          {combat.initiative_order.map((p, i) => (
            <div
              key={i}
              className={`text-xs px-2 py-1 rounded ${
                p.side === "enemy"
                  ? "bg-red-950 text-red-300"
                  : "bg-blue-950 text-blue-300"
              } ${p.name === combat.current_turn ? "ring-1 ring-amber-400" : ""}`}
            >
              {p.initiative} | {p.name} ({p.side})
            </div>
          ))}
        </div>
      )}
    </>
  );
}
