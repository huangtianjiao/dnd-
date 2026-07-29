"use client";

import { useEffect, useRef } from "react";
import type { ActionLogEntry } from "../lib/types";

interface ActionLogProps {
  entries: ActionLogEntry[];
}

export function ActionLog({ entries }: ActionLogProps) {
  const listRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [entries]);

  return (
    <div className="log-section">
      <div className="section-title">行动日志</div>
      <div className="log-list" ref={listRef}>
        {entries.map((e, i) => (
          <div key={i} className="log-entry">
            <span className="log-time">{e.time}</span>{" "}
            <span className={e.cls || ""}>{e.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
