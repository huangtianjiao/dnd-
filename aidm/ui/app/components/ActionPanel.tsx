"use client";

import { useState, useCallback, useEffect, useRef } from "react";

interface ActionPanelProps {
  onAction: (actionText: string) => void;
  onEndTurn: () => void;
  onOpenSpellbook: () => void;
  /** 回合/轮次变化时外部可调用来重置已用状态 */
  resetKey?: number;
}

type ActionKey = "move" | "dash" | "attack" | "cast" | "dodge" | "help" | "disengage" | "hide" | "bonus" | "reaction";

interface ActionDef {
  key: ActionKey;
  label: string;
  tag?: string;
  primary?: boolean;
}

const MOVE_ACTIONS: ActionDef[] = [
  { key: "move", label: "移动", tag: "30ft" },
  { key: "dash", label: "疾步", tag: "+30ft" },
];

const MAIN_ACTIONS: ActionDef[] = [
  { key: "attack", label: "攻击", tag: "1动作", primary: true },
  { key: "cast", label: "施法", tag: "1动作" },
  { key: "dodge", label: "闪避" },
  { key: "help", label: "协助" },
  { key: "disengage", label: "脱离" },
  { key: "hide", label: "躲藏" },
];

export function ActionPanel({ onAction, onEndTurn, onOpenSpellbook, resetKey }: ActionPanelProps) {
  const [used, setUsed] = useState<Set<ActionKey>>(new Set());
  const prevReset = useRef(resetKey ?? 0);

  // resetKey 变化时重置已用状态（新回合/新轮次）
  useEffect(() => {
    if ((resetKey ?? 0) !== prevReset.current) {
      setUsed(new Set());
      prevReset.current = resetKey ?? 0;
    }
  }, [resetKey]);

  const handleAction = useCallback((def: ActionDef) => {
    if (used.has(def.key)) return;
    if (def.key === "cast") {
      onOpenSpellbook();
    } else {
      onAction(def.label);
    }
    setUsed((s) => {
      const next = new Set(s);
      next.add(def.key);
      return next;
    });
  }, [used, onAction, onOpenSpellbook]);

  const renderBtn = (def: ActionDef) => (
    <button
      key={def.key}
      className={`action-btn ${def.primary ? "primary" : ""} ${used.has(def.key) ? "used" : ""}`}
      onClick={() => handleAction(def)}
      disabled={used.has(def.key)}
    >
      {def.label}
      {def.tag && <span className="ap-tag">{def.tag}</span>}
    </button>
  );

  return (
    <div className="action-panel visible">
      <div className="action-row">
        <div className="action-group-label">移动</div>
        {MOVE_ACTIONS.map(renderBtn)}
      </div>
      <div className="action-row">
        <div className="action-group-label">动作</div>
        {MAIN_ACTIONS.map(renderBtn)}
      </div>
      <div className="action-row">
        <div className="action-group-label">附赠动作</div>
        <button
          className={`action-btn ${used.has("bonus") ? "used" : ""}`}
          onClick={() => handleAction({ key: "bonus", label: "附赠动作" })}
          disabled={used.has("bonus")}
        >
          专用附赠 <span className="ap-tag">1附赠</span>
        </button>
        <div className="action-group-label" style={{ marginLeft: "12px" }}>反应</div>
        <button
          className={`action-btn ${used.has("reaction") ? "used" : ""}`}
          onClick={() => handleAction({ key: "reaction", label: "反应" })}
          disabled={used.has("reaction")}
        >
          反应 <span className="ap-tag">每轮1次</span>
        </button>
        <button
          className="action-btn"
          onClick={onEndTurn}
          style={{ marginLeft: "auto", background: "var(--bg-green)", color: "var(--text-green)", borderColor: "#5dcaa5", fontWeight: 500 }}
        >
          结束回合
        </button>
      </div>
    </div>
  );
}
