"use client";

import { useState } from "react";

interface PlayerInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function PlayerInput({ onSend, disabled }: PlayerInputProps) {
  const [inp, setInp] = useState("");

  const handleSend = () => {
    if (!inp.trim() || disabled) return;
    onSend(inp.trim());
    setInp("");
  };

  return (
    <div className="px-4 py-3 flex gap-2 border-t border-neutral-800">
      <input
        value={inp}
        onChange={(e) => setInp(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") handleSend();
        }}
        placeholder="输入你的行动..."
        className="flex-1 px-3 py-2 bg-neutral-800 border border-neutral-700 rounded focus:border-amber-400 focus:outline-none"
      />
      <button
        onClick={handleSend}
        disabled={disabled}
        className="px-5 py-2 bg-amber-400 text-neutral-900 font-bold rounded hover:bg-amber-300 disabled:opacity-40"
      >
        🎲 行动
      </button>
    </div>
  );
}
