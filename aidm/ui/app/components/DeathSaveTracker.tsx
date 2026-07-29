"use client";

interface DeathSaveTrackerProps {
  successes: number;
  failures: number;
  onRoll: () => void;
}

export function DeathSaveTracker({ successes, failures, onRoll }: DeathSaveTrackerProps) {
  return (
    <div className="death-save-box">
      <div className="ds-title">死亡豁免检定</div>
      <div className="death-save-row">
        <span className="ds-label">成功</span>
        <div className="death-save-dots">
          {[0, 1, 2].map((i) => (
            <div key={i} className={`ds-dot ${i < successes ? "success" : ""}`}>
              {i < successes ? "✓" : ""}
            </div>
          ))}
        </div>
      </div>
      <div className="death-save-row">
        <span className="ds-label">失败</span>
        <div className="death-save-dots">
          {[0, 1, 2].map((i) => (
            <div key={i} className={`ds-dot ${i < failures ? "failure" : ""}`}>
              {i < failures ? "✕" : ""}
            </div>
          ))}
        </div>
      </div>
      <button className="ds-roll-btn" onClick={onRoll}>
        掷死亡豁免 d20
      </button>
    </div>
  );
}
