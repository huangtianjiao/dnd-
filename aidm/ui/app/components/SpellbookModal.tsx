"use client";

import { useState } from "react";

interface Spell {
  name: string;
  level: number;
  school: string;
  time: string;
  range: string;
  duration: string;
  components: string;
  desc: string;
}

interface SpellbookModalProps {
  spells: Spell[];
  spellSlots: Record<string, number>;
  onCast: (spellName: string) => void;
}

export function SpellbookModal({ spells, spellSlots, onCast }: SpellbookModalProps) {
  const [open, setOpen] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="w-full px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400"
      >
        📖 法术书 ({spells.length})
      </button>

      {open && (
        <div
          className="fixed inset-0 bg-black/60 flex items-center justify-center z-50"
          onClick={() => setOpen(false)}
        >
          <div
            className="bg-neutral-900 border border-neutral-700 rounded-lg p-4 max-w-md max-h-[70vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-3">
              <div className="text-sm font-bold text-amber-400">法术书</div>
              <button onClick={() => setOpen(false)} className="text-neutral-500 hover:text-neutral-300">
                ✕
              </button>
            </div>

            {/* 法术位显示 */}
            <div className="mb-3 space-y-1">
              {Object.entries(spellSlots).map(([level, remaining]) => (
                <div key={level} className="flex items-center gap-1">
                  <span className="text-[10px] text-neutral-500 w-8">{level}环</span>
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded border ${
                      remaining > 0
                        ? "bg-purple-950 border-purple-700 text-purple-300"
                        : "bg-neutral-800 border-neutral-700 text-neutral-600"
                    }`}
                  >
                    剩余{remaining}
                  </span>
                </div>
              ))}
            </div>

            {/* 法术列表 */}
            <div className="space-y-2">
              {spells.map((s) => (
                <div key={s.name} className="border border-neutral-700 rounded p-2">
                  <div
                    className="flex justify-between items-center cursor-pointer"
                    onClick={() => setExpanded(expanded === s.name ? null : s.name)}
                  >
                    <div>
                      <span className="text-sm font-bold text-blue-300">{s.name}</span>
                      <span className="text-[10px] text-neutral-500 ml-2">
                        {s.level === 0 ? "戏法" : `${s.level}环`} · {s.school}
                      </span>
                    </div>
                    <span className="text-neutral-500 text-xs">{expanded === s.name ? "▼" : "▶"}</span>
                  </div>

                  {expanded === s.name && (
                    <div className="mt-2 text-xs text-neutral-400 space-y-1">
                      <div>时间: {s.time} | 射程: {s.range} | 持续: {s.duration}</div>
                      <div>成分: {s.components}</div>
                      <div className="text-neutral-300">{s.desc}</div>
                    </div>
                  )}

                  {s.level > 0 && (
                    <button
                      onClick={() => {
                        onCast(s.name);
                        setOpen(false);
                      }}
                      className="mt-2 w-full px-2 py-1 bg-blue-700 border border-blue-500 rounded text-xs hover:bg-blue-600"
                    >
                      施放 {s.name}
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
