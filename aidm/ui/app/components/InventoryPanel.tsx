"use client";

interface InventoryItem {
  name: string;
  qty?: number;
  equipped?: boolean;
}

interface InventoryPanelProps {
  items: InventoryItem[];
  weight?: { current: number; max: number };
}

export function InventoryPanel({ items, weight }: InventoryPanelProps) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center">
        <span className="text-[10px] text-neutral-500 uppercase">背包</span>
        {weight && (
          <span className="text-[10px] text-neutral-400">
            {weight.current}/{weight.max} lb
          </span>
        )}
      </div>
      <div className="space-y-0.5 max-h-32 overflow-y-auto">
        {items.length === 0 ? (
          <div className="text-[10px] text-neutral-700">空</div>
        ) : (
          items.map((item, i) => (
            <div
              key={i}
              className="flex items-center gap-1 text-[10px] px-1 py-0.5 bg-neutral-800/50 rounded"
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  item.equipped ? "bg-green-500" : "bg-neutral-600"
                }`}
              />
              <span className="flex-1 truncate">{item.name}</span>
              {item.qty && item.qty > 1 && (
                <span className="text-neutral-500">×{item.qty}</span>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
