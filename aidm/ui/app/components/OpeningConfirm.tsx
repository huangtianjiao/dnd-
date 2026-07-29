"use client";

interface OpeningConfirmProps {
  narration: string;
  actionOptions: string[];
  loading: boolean;
  onConfirm: () => void;
  onRegenerate: () => void;
  onBack: () => void;
}

/** 开场确认页 — 展示 /open 返回的开场叙述与行动选项，确认后才正式进入游戏 */
export function OpeningConfirm({ narration, actionOptions, loading, onConfirm, onRegenerate, onBack }: OpeningConfirmProps) {
  return (
    <main className="screen">
      <div className="screen-card flex-col">
        <h2 className="title-lg">📜 开场预览</h2>

        {loading ? (
          <div className="text-sm text-muted" style={{ background: "var(--bg-secondary)", border: "0.5px solid var(--border)", borderRadius: "var(--radius-md)", padding: 16 }}>
            ⏳ DM 正在重新生成开场...(约10秒)
          </div>
        ) : (
          <>
            <div
              className="text-sm"
              style={{
                background: "var(--bg-secondary)",
                color: "var(--text-primary)",
                border: "0.5px solid var(--border)",
                borderRadius: "var(--radius-md)",
                padding: 16,
                maxHeight: "50vh",
                overflowY: "auto",
                whiteSpace: "pre-wrap",
                lineHeight: 1.7,
              }}
            >
              {narration || "(无开场叙述)"}
            </div>

            {actionOptions.length > 0 && (
              <div className="flex-col" style={{ gap: 4 }}>
                <div className="form-label">可选行动</div>
                <div className="flex-row" style={{ flexWrap: "wrap" }}>
                  {actionOptions.map((c, i) => (
                    <span
                      key={i}
                      className="text-xs"
                      style={{ padding: "6px 12px", background: "var(--bg-secondary)", border: "0.5px solid var(--border)", borderRadius: "var(--radius-md)", color: "var(--text-secondary)" }}
                    >
                      {i + 1}. {c}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        <div className="flex-row">
          <button
            onClick={onConfirm}
            disabled={loading}
            className="btn btn-primary"
            style={{ flex: 1 }}
          >
            🗺️ 开始冒险
          </button>
          <button
            onClick={onRegenerate}
            disabled={loading}
            className="btn btn-secondary"
          >
            {loading ? "⏳ 生成中..." : "🔄 重新生成"}
          </button>
          <button onClick={onBack} disabled={loading} className="btn btn-secondary">
            ← 返回
          </button>
        </div>
      </div>
    </main>
  );
}
