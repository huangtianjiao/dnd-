"use client";

interface ActionPanelProps {
  onAction: (action: string) => void;
}

const ACTIONS = [
  { id: "attack", label: "⚔️ 攻击" },
  { id: "cast", label: "✨ 施法" },
  { id: "dash", label: "🏃 疾走" },
  { id: "disengage", label: "🚪 撤离" },
  { id: "dodge", label: "🛡️ 闪避" },
  { id: "help", label: "🤝 协助" },
  { id: "hide", label: "🌿 躲藏" },
  { id: "ready", label: "⏳ 预备" },
  { id: "search", label: "🔍 搜索" },
  { id: "utilize", label: "🔧 使用物品" },
];

export function ActionPanel({ onAction }: ActionPanelProps) {
  return (
    <div className="space-y-1">
      <div className="text-[10px] text-neutral-500 uppercase">动作</div>
      <div className="grid grid-cols-2 gap-1">
        {ACTIONS.map((a) => (
          <button
            key={a.id}
            onClick={() => onAction(a.id)}
            className="px-2 py-1 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400 hover:bg-neutral-700"
          >
            {a.label}
          </button>
        ))}
      </div>
    </div>
  );
}
