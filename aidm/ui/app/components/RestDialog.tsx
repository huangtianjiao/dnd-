"use client";

import { useState } from "react";

interface RestDialogProps {
  onRest: (type: "short" | "long") => void;
}

export function RestDialog({ onRest }: RestDialogProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="w-full px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400"
      >
        💤 休息
      </button>

      {open && (
        <div
          className="fixed inset-0 bg-black/60 flex items-center justify-center z-50"
          onClick={() => setOpen(false)}
        >
          <div
            className="bg-neutral-900 border border-neutral-700 rounded-lg p-4 space-y-3 max-w-xs"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="text-sm font-bold text-amber-400">选择休息方式</div>
            <button
              onClick={() => {
                onRest("short");
                setOpen(false);
              }}
              className="w-full px-3 py-2 bg-blue-800 border border-blue-600 rounded text-sm hover:bg-blue-700"
            >
              ☕ 短休（1小时）
              <div className="text-[10px] text-blue-300 mt-0.5">消耗生命骰恢复HP，恢复部分职业特性</div>
            </button>
            <button
              onClick={() => {
                onRest("long");
                setOpen(false);
              }}
              className="w-full px-3 py-2 bg-purple-800 border border-purple-600 rounded text-sm hover:bg-purple-700"
            >
              🛏️ 长休（8小时）
              <div className="text-[10px] text-purple-300 mt-0.5">HP回满，恢复一半生命骰，法术位全恢复，力竭-1</div>
            </button>
            <button
              onClick={() => setOpen(false)}
              className="w-full px-3 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs"
            >
              取消
            </button>
          </div>
        </div>
      )}
    </>
  );
}
