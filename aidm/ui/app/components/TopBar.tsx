"use client";

import type { SceneData } from "../lib/types";

interface TopBarProps {
  campaignName: string;
  campId: number | null;
  mode: "exploration" | "combat";
  round?: number;
  scene?: SceneData | null;
  onOpenRules: () => void;
  onOpenSettings?: () => void;
}

export function TopBar({ campaignName, campId, mode, round, scene, onOpenRules, onOpenSettings }: TopBarProps) {
  const modeLabel = mode === "combat" ? `战斗 · 第 ${round ?? 1} 轮` : "探索阶段";
  const location = scene?.location || scene?.situation;

  return (
    <div className="top-bar">
      <div className="campaign-info">
        <span className="title">{campaignName}</span>
        <span className="session">
          {campId ? `#${campId} · ` : ""}{modeLabel}
          {location ? ` · ${location}` : ""}
        </span>
      </div>
      <div className="top-right">
        <button className="icon-btn" title="规则参考" onClick={onOpenRules}>i</button>
        {onOpenSettings && (
          <button className="icon-btn" title="设置" onClick={onOpenSettings}>⚙</button>
        )}
      </div>
    </div>
  );
}
