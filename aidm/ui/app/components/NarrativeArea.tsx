"use client";

import { useEffect, useRef } from "react";
import type { LogEntry, DiceRollResult } from "../lib/types";

interface NarrativeAreaProps {
  log: LogEntry[];
}

/** 将结构化 DiceRollResult 渲染为 msg-roll 内部 HTML */
function renderRollMsg(r: DiceRollResult) {
  const isD20 = r.sides === 20;
  const diceLabel = r.count > 1 ? `${r.count}d${r.sides}` : `d${r.sides}`;
  const advLabel =
    isD20 && r.advantage !== "normal"
      ? r.advantage === "adv" ? "(优势)" : "(劣势)"
      : "";

  let detail = "";
  if (isD20 && r.advantage !== "normal") {
    detail = `[${r.rolls.join(", ")}] → ${r.total}`;
  } else if (r.count > 1) {
    detail = `${r.rolls.join("+")} = ${r.total}`;
  } else {
    detail = `d${r.sides}(${r.total})`;
  }
  if (r.modifier !== 0) {
    detail += ` ${r.modifier > 0 ? "+" : ""}${r.modifier}`;
  }

  const tag = isD20 ? "检定" : `d${r.sides}`;

  return (
    <>
      <span className="dice-icon">{diceLabel}</span>
      <span className="roll-detail">{detail}</span>
      <span className="roll-result">{r.finalTotal}</span>
      <span className="roll-tag">{tag}{advLabel}</span>
    </>
  );
}

export function NarrativeArea({ log }: NarrativeAreaProps) {
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [log]);

  return (
    <div className="narrative-area">
      {log.map((e, i) => {
        // 结构化掷骰消息（来自本地 DiceRoller）
        if (e.c === "dice" && e.roll) {
          return (
            <div key={i} className="msg-roll">
              {renderRollMsg(e.roll)}
            </div>
          );
        }

        // 文本骰子消息（来自后端 socket formatDice）
        if (e.c === "dice") {
          return (
            <div key={i} className="msg-roll">
              <span className="dice-icon">🎲</span>
              <span className="roll-detail">{e.t}</span>
            </div>
          );
        }

        switch (e.c) {
          case "dm":
            return (
              <div key={i} className="msg-dm">
                {e.speaker && <div className="speaker">{e.speaker}</div>}
                <div className="content">{e.t}</div>
              </div>
            );
          case "you":
            return (
              <div key={i} className="msg-player">
                {e.speaker && <div className="speaker">{e.speaker}</div>}
                <div className="content">{e.t}</div>
              </div>
            );
          case "npc":
            return (
              <div key={i} className="msg-npc">
                {e.speaker && <div className="speaker">{e.speaker}</div>}
                <div className="content">{e.t}</div>
              </div>
            );
          case "damage":
            return <div key={i} className="msg-damage">{e.t}</div>;
          case "system":
            return <div key={i} className="msg-system">{e.t}</div>;
          case "meta":
            return <div key={i} className="msg-system">{e.t}</div>;
          default:
            // "other" — 后端转发的其他玩家叙述
            return <div key={i} className="msg-dm"><div className="content">{e.t}</div></div>;
        }
      })}
      <div ref={endRef} />
    </div>
  );
}
