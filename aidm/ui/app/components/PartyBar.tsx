"use client";

import type { PartyMember } from "../lib/types";

interface PartyBarProps {
  members: PartyMember[];
  activeName?: string;
  onSelect?: (name: string) => void;
}

const AVATAR_COLORS: string[] = [
  "var(--bg-purple)|var(--text-purple)",
  "var(--bg-blue)|var(--text-blue)",
  "var(--bg-green)|var(--text-green)",
  "var(--bg-amber)|var(--text-amber)",
  "var(--bg-red)|var(--text-red)",
];

export function PartyBar({ members, activeName, onSelect }: PartyBarProps) {
  if (members.length === 0) return null;

  const hpState = (hp?: number, hpMax?: number) => {
    if (!hp || !hpMax || hpMax === 0) return null;
    const pct = (hp / hpMax) * 100;
    if (hp <= 0) return "down";
    if (pct > 50) return "full";
    if (pct > 25) return "hurt";
    return "critical";
  };

  return (
    <div className="party-bar">
      {members.map((m, i) => {
        const [bg, color] = (AVATAR_COLORS[i % AVATAR_COLORS.length] || AVATAR_COLORS[0]).split("|");
        const hpDot = hpState(m.hp, m.hpMax);
        return (
          <div
            key={i}
            className={`party-member ${m.name === activeName ? "active" : ""}`}
            onClick={() => onSelect?.(m.name)}
          >
            <div className="pm-avatar" style={{ background: bg, color }}>{m.name.charAt(0)}</div>
            <div className="pm-name">{m.name}</div>
            {hpDot && <div className={`pm-hp-dot ${hpDot}`} title={`${m.hp}/${m.hpMax}`} />}
          </div>
        );
      })}
    </div>
  );
}
