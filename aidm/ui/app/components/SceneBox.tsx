"use client";

import type { SceneData } from "../lib/types";

export function SceneBox({ scene }: { scene: SceneData | null }) {
  if (!scene || !scene.location) return null;

  return (
    <div className="border-b border-neutral-800 px-4 py-2 bg-neutral-850">
      <div className="text-sm font-bold text-amber-400">📍 {scene.location}</div>
      {scene.atmosphere && (
        <div className="text-xs text-neutral-500">{scene.atmosphere}</div>
      )}
      {scene.npcs && scene.npcs.length > 0 && (
        <div className="text-xs text-neutral-400 mt-1">
          在场NPC: {scene.npcs.map((n) => n.name).join(", ")}
        </div>
      )}
      {scene.exits && scene.exits.length > 0 && (
        <div className="text-xs text-neutral-400 mt-1">
          出口: {scene.exits.join(" / ")}
        </div>
      )}
    </div>
  );
}
