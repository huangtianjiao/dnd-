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
    <main className="min-h-screen flex items-center justify-center bg-neutral-900 text-neutral-100 p-4">
      <div className="w-full max-w-2xl space-y-4">
        <h2 className="text-2xl font-bold text-amber-400">📜 开场预览</h2>

        {loading ? (
          <div className="bg-neutral-800 border border-neutral-700 rounded p-4 text-neutral-500 text-sm">
            ⏳ DM 正在重新生成开场...(约10秒)
          </div>
        ) : (
          <>
            <div className="bg-neutral-800 border border-neutral-700 rounded p-4 max-h-[50vh] overflow-y-auto whitespace-pre-wrap text-blue-300 text-sm leading-relaxed">
              {narration || "(无开场叙述)"}
            </div>

            {actionOptions.length > 0 && (
              <div className="space-y-1">
                <div className="text-xs text-neutral-500">可选行动</div>
                <div className="flex gap-2 flex-wrap">
                  {actionOptions.map((c, i) => (
                    <span key={i} className="px-3 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs text-neutral-300">
                      {i + 1}. {c}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        <div className="flex gap-2">
          <button
            onClick={onConfirm}
            disabled={loading}
            className="flex-1 px-6 py-3 bg-amber-400 text-neutral-900 font-bold rounded hover:bg-amber-300 disabled:opacity-40"
          >
            🗺️ 开始冒险
          </button>
          <button
            onClick={onRegenerate}
            disabled={loading}
            className="px-4 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm hover:border-amber-400 disabled:opacity-40"
          >
            {loading ? "⏳ 生成中..." : "🔄 重新生成"}
          </button>
          <button onClick={onBack} disabled={loading} className="px-4 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm disabled:opacity-40">
            ← 返回
          </button>
        </div>
      </div>
    </main>
  );
}
