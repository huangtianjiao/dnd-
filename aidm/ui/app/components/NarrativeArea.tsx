"use client";

import { useEffect, useRef } from "react";
import type { LogEntry } from "../lib/types";

export function NarrativeArea({ log }: { log: LogEntry[] }) {
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [log]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2">
      {log.map((e, i) => (
        <div
          key={i}
          className={
            e.c === "you"
              ? "text-amber-400 text-right"
              : e.c === "dm"
              ? "text-blue-300"
              : e.c === "npc"
              ? "text-amber-300"
              : e.c === "dice"
              ? "text-green-400 text-xs font-mono"
              : e.c === "damage"
              ? "text-red-400 text-center"
              : e.c === "system"
              ? "text-neutral-500 text-center"
              : e.c === "meta"
              ? "text-neutral-600 text-xs"
              : "text-neutral-400"
          }
        >
          {e.t}
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
