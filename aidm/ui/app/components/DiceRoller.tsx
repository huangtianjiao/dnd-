"use client";

import { useState, useCallback } from "react";
import type { DiceRollResult, AdvantageMode } from "../lib/types";

interface DiceRollerProps {
  onRoll: (result: DiceRollResult) => void;
}

const DICE_OPTIONS: { label: string; sides: number; count: number }[] = [
  { label: "d20", sides: 20, count: 1 },
  { label: "d4", sides: 4, count: 1 },
  { label: "d6", sides: 6, count: 1 },
  { label: "d8", sides: 8, count: 1 },
  { label: "d10", sides: 10, count: 1 },
  { label: "d12", sides: 12, count: 1 },
  { label: "d100", sides: 100, count: 1 },
  { label: "2d6", sides: 6, count: 2 },
];

export function DiceRoller({ onRoll }: DiceRollerProps) {
  const [advMode, setAdvMode] = useState<AdvantageMode>("normal");
  const [modInput, setModInput] = useState(0);
  const [display, setDisplay] = useState<{ total: number; breakdown: string } | null>(null);

  const rollDice = useCallback((sides: number, count: number) => {
    const rolls: number[] = [];
    let total = 0;
    const isD20 = sides === 20;

    if (isD20 && advMode !== "normal") {
      const r1 = Math.floor(Math.random() * sides) + 1;
      const r2 = Math.floor(Math.random() * sides) + 1;
      rolls.push(r1, r2);
      total = advMode === "adv" ? Math.max(r1, r2) : Math.min(r1, r2);
    } else {
      for (let i = 0; i < count; i++) {
        const r = Math.floor(Math.random() * sides) + 1;
        rolls.push(r);
        total += r;
      }
    }

    const modifier = modInput || 0;
    const finalTotal = total + modifier;

    // 更新展示区
    let breakdown = "";
    if (isD20 && advMode !== "normal") {
      const tag = advMode === "adv" ? "优势" : "劣势";
      breakdown = `[${rolls.join(", ")}] → ${total}${modifier !== 0 ? ` ${modifier > 0 ? "+" : ""}${modifier}` : ""} (${tag})`;
    } else if (count > 1) {
      breakdown = `[${rolls.join("+")}] = ${total}${modifier !== 0 ? ` ${modifier > 0 ? "+" : ""}${modifier}` : ""}`;
    } else {
      breakdown = `d${sides}(${total})${modifier !== 0 ? ` ${modifier > 0 ? "+" : ""}${modifier}` : ""}`;
    }
    setDisplay({ total: finalTotal, breakdown });

    // 回调
    onRoll({
      sides, count, rolls, total, modifier, finalTotal, advantage: advMode,
    });
  }, [advMode, modInput, onRoll]);

  const setAdv = (mode: AdvantageMode) => setAdvMode(mode);

  return (
    <div className="dice-section">
      <div className="section-title">骰子</div>
      <div className="dice-grid">
        {DICE_OPTIONS.map((d) => (
          <button key={d.label} className="die-btn" onClick={() => rollDice(d.sides, d.count)}>
            {d.label}
          </button>
        ))}
      </div>
      <div className="adv-toggle">
        <button
          className={`adv-btn ${advMode === "normal" ? "active normal" : ""}`}
          onClick={() => setAdv("normal")}
        >正常</button>
        <button
          className={`adv-btn ${advMode === "adv" ? "active adv" : ""}`}
          onClick={() => setAdv("adv")}
        >优势</button>
        <button
          className={`adv-btn ${advMode === "dis" ? "active dis" : ""}`}
          onClick={() => setAdv("dis")}
        >劣势</button>
      </div>
      <div className="mod-input-row">
        <label>修饰值:</label>
        <input
          type="number"
          className="mod-input"
          value={modInput}
          onChange={(e) => setModInput(parseInt(e.target.value) || 0)}
        />
      </div>
      <div className={`roll-display ${display ? "" : "empty"}`}>
        {display ? (
          <>
            <div className="roll-num">{display.total}</div>
            <div className="roll-breakdown">{display.breakdown}</div>
          </>
        ) : (
          "点击骰子进行投掷"
        )}
      </div>
    </div>
  );
}
