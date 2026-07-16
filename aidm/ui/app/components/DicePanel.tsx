"use client";

import { useState } from "react";

interface DicePanelProps {
  onRoll: (sides: number, count: number, modifier: number, advantage: "normal" | "adv" | "dis") => void;
}

const DICE = [
  { label: "d4", sides: 4 },
  { label: "d6", sides: 6 },
  { label: "d8", sides: 8 },
  { label: "d10", sides: 10 },
  { label: "d12", sides: 12 },
  { label: "d20", sides: 20 },
  { label: "d100", sides: 100 },
];

export function DicePanel({ onRoll }: DicePanelProps) {
  const [advMode, setAdvMode] = useState<"normal" | "adv" | "dis">("normal");
  const [mod, setMod] = useState(0);
  const [count, setCount] = useState(1);
  const [result, setResult] = useState<string>("");

  const handleRoll = (sides: number) => {
    onRoll(sides, count, mod, advMode);
    setResult(`🎲 ${count}d${sides}${mod >= 0 ? `+${mod}` : mod} (${advMode})`);
  };

  return (
    <div className="space-y-2">
      {/* 骰子按钮 */}
      <div className="grid grid-cols-4 gap-1">
        {DICE.map((d) => (
          <button
            key={d.label}
            onClick={() => handleRoll(d.sides)}
            className="px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400 hover:bg-neutral-700"
          >
            {d.label}
          </button>
        ))}
      </div>

      {/* 数量 + 修饰值 */}
      <div className="flex gap-2 items-center">
        <label className="text-[10px] text-neutral-500">数量</label>
        <input
          type="number"
          min={1}
          max={20}
          value={count}
          onChange={(e) => setCount(Math.max(1, parseInt(e.target.value) || 1))}
          className="w-12 px-1 py-0.5 bg-neutral-800 border border-neutral-700 rounded text-xs text-center"
        />
        <label className="text-[10px] text-neutral-500 ml-1">修正</label>
        <input
          type="number"
          value={mod}
          onChange={(e) => setMod(parseInt(e.target.value) || 0)}
          className="w-12 px-1 py-0.5 bg-neutral-800 border border-neutral-700 rounded text-xs text-center"
        />
      </div>

      {/* 优势/劣势切换（仅 d20 有效） */}
      <div className="flex gap-1">
        {(["normal", "adv", "dis"] as const).map((m) => (
          <button
            key={m}
            onClick={() => setAdvMode(m)}
            className={`flex-1 px-2 py-1 rounded text-[10px] ${
              advMode === m
                ? m === "adv" ? "bg-blue-700 text-white" : m === "dis" ? "bg-red-700 text-white" : "bg-amber-400 text-neutral-900"
                : "bg-neutral-800 border border-neutral-700 text-neutral-400"
            }`}
          >
            {m === "normal" ? "正常" : m === "adv" ? "优势" : "劣势"}
          </button>
        ))}
      </div>

      {/* 结果显示 */}
      {result && <div className="text-xs text-green-400 font-mono">{result}</div>}
    </div>
  );
}
