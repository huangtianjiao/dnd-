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
    <div className="player-input-area">
      <input
        className="player-input"
        value={inp}
        onChange={(e) => setInp(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") handleSend();
        }}
        placeholder="描述你的行动...（如：我要用长剑攻击哥布林A）"
      />
      <button className="send-btn" onClick={handleSend} disabled={disabled}>
        {disabled ? "处理中..." : "发送"}
      </button>
    </div>
  );
}
