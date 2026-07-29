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
      <div
        className="panel-section"
        style={{ marginBottom: 8 }}
      >
        <div className="section-title">
          <span>法术列表</span>
          <span
            style={{ fontSize: 10, color: "var(--text-blue)", cursor: "pointer", textDecoration: "underline" }}
            onClick={() => setOpen(true)}
          >
            法术书 ({spells.length})
          </span>
        </div>
        {/* 法术位概览 */}
        {Object.keys(spellSlots).length > 0 && (
          <div className="spell-slots" style={{ flexWrap: "wrap" }}>
            {Object.entries(spellSlots).sort(([a], [b]) => parseInt(a) - parseInt(b)).map(([level, remaining]) => (
              <span
                key={level}
                style={{
                  fontSize: 10,
                  padding: "2px 6px",
                  borderRadius: 4,
                  background: remaining > 0 ? "var(--bg-blue)" : "var(--bg-tertiary)",
                  color: remaining > 0 ? "var(--text-blue)" : "var(--text-tertiary)",
                  border: `0.5px solid ${remaining > 0 ? "#85b7eb" : "var(--border)"}`,
                }}
              >
                {level}环:{remaining}
              </span>
            ))}
          </div>
        )}
      </div>

      {open && (
        <div className="modal-overlay visible" onClick={() => setOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <span className="mh-title">法术书</span>
              <button className="modal-close" onClick={() => setOpen(false)}>✕</button>
            </div>
            <div className="modal-body">
              {spells.map((s) => (
                <div
                  key={s.name}
                  className={`spell-card ${expanded === s.name ? "expanded" : ""}`}
                  onClick={() => setExpanded(expanded === s.name ? null : s.name)}
                >
                  <div className="sc-header">
                    <span className="sc-name">{s.name}</span>
                    <span className="sc-level">{s.level === 0 ? "戏法" : `${s.level}环`}</span>
                  </div>
                  <div className="sc-meta">
                    <span>{s.time}</span>
                    <span>{s.range}</span>
                    <span>{s.components}</span>
                    <span>{s.duration}</span>
                  </div>
                  <div className="sc-desc">{s.desc}</div>
                  {s.level > 0 && (
                    <button
                      className="sc-cast"
                      onClick={(e) => {
                        e.stopPropagation();
                        onCast(s.name);
                        setOpen(false);
                      }}
                    >
                      施放 {s.name}
                    </button>
                  )}
                </div>
              ))}
              {spells.length === 0 && (
                <div style={{ fontSize: 12, color: "var(--text-tertiary)", textAlign: "center", padding: 16 }}>
                  无可用法术
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
