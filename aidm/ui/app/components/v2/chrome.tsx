"use client";

import type { ReactNode } from "react";
import type { CombatData, GameClock, GameMode, PartyMember } from "../../lib/types";

/* ================================================================
 * 布局三件套：TopBar / PartyBar / SidePanel
 * （docs/FRONTEND_REDESIGN.md §2 layout/*）
 * ================================================================ */

const MODE_LABEL: Record<GameMode, string> = { explore: "探索", social: "社交", combat: "战斗" };

/* ---------------- TopBar ---------------- */

interface TopBarProps {
  campaignName: string;
  mode: GameMode;
  clock: GameClock | null;
  onOpenMenu: () => void;
  onTogglePanel: () => void;
}

export function TopBar({ campaignName, mode, clock, onOpenMenu, onTogglePanel }: TopBarProps) {
  return (
    <header className="v2-topbar">
      <button className="v2-icon-btn" title="菜单" onClick={onOpenMenu}>
        ☰
      </button>
      <div className="v2-campaign">
        <span className="tag">战役</span>
        <h1>{campaignName}</h1>
      </div>
      <span className="v2-mode-badge" data-mode={mode}>
        {MODE_LABEL[mode]}
      </span>
      {clock && (
        <span className="v2-game-clock" title="游戏内时间">
          {/夜|凌晨|黄昏/.test(clock.label) ? "☾" : "☀"} 第{clock.day}天 · {clock.label}
        </span>
      )}
      <div className="v2-top-spacer" />
      <button className="v2-icon-btn" title="折叠/展开角色面板" onClick={onTogglePanel}>
        🜲
      </button>
    </header>
  );
}

/* ---------------- PartyBar ---------------- */

const AVATAR_BG = [
  "linear-gradient(135deg,#c9a45c,#8a6a34)",
  "linear-gradient(135deg,#9a8f7c,#6b6252)",
  "linear-gradient(135deg,#7fa3c9,#4a6a8a)",
  "linear-gradient(135deg,#8f6fb8,#5d4480)",
  "linear-gradient(135deg,#6fa878,#3f6b4c)",
  "linear-gradient(135deg,#c4705f,#8f352f)",
];

const avatarBg = (name: string) =>
  AVATAR_BG[[...name].reduce((s, c) => s + c.charCodeAt(0), 0) % AVATAR_BG.length];

interface PartyBarProps {
  members: PartyMember[];
  myName: string;
  combat: CombatData | null;
}

export function PartyBar({ members, myName, combat }: PartyBarProps) {
  const curTurn = combat?.active ? combat.current_turn : undefined;
  if (members.length === 0) {
    return (
      <div className="v2-partybar">
        <span className="v2-party-empty">单人冒险</span>
        {combat?.active && curTurn && (
          <span className="v2-party-hint">
            <i className="dot" />
            轮到 {curTurn}
          </span>
        )}
      </div>
    );
  }
  return (
    <div className="v2-partybar">
      {members.map((m) => {
        const isSelf = m.name === myName;
        const isTurn = !!curTurn && m.name === curTurn;
        const pct = m.hpMax ? Math.max(0, Math.min(100, ((m.hp ?? m.hpMax) / m.hpMax) * 100)) : null;
        const low = m.hp != null && m.hpMax != null && m.hp > 0 && m.hp * 2 <= m.hpMax;
        return (
          <div
            key={`${m.characterId}-${m.name}`}
            className={`v2-pm ${isSelf ? "self" : ""} ${isTurn ? "turn" : ""}`}
          >
            <div className="avatar" style={{ background: avatarBg(m.name) }}>
              {m.name.charAt(0)}
            </div>
            <div className="info">
              <span className="name" style={m.connected ? undefined : { color: "var(--v2-ink-faint)" }}>
                <i
                  className="online"
                  style={m.connected ? undefined : { background: "#555", boxShadow: "none" }}
                />
                {m.name}
                {m.isDm ? " · DM" : ""}
                {isSelf ? "（我）" : ""}
                {!m.connected ? "（离开）" : ""}
              </span>
              {pct != null && (
                <>
                  <span className={`hpmini ${low ? "low" : ""}`}>
                    <i style={{ width: `${pct}%` }} />
                  </span>
                  <span className="hpnum">
                    {m.hp}/{m.hpMax}
                  </span>
                </>
              )}
            </div>
          </div>
        );
      })}
      {combat?.active && curTurn && (
        <span className="v2-party-hint">
          <i className="dot" />
          轮到 {curTurn}
        </span>
      )}
    </div>
  );
}

/* ---------------- SidePanel ---------------- */

export type PanelTab = "char" | "spell" | "item" | "rule";

const TABS: { key: PanelTab; label: string }[] = [
  { key: "char", label: "角色卡" },
  { key: "spell", label: "法术书" },
  { key: "item", label: "物品栏" },
  { key: "rule", label: "规则速查" },
];

interface SidePanelProps {
  activeTab: PanelTab;
  onTabChange: (t: PanelTab) => void;
  charContent: ReactNode;
  spellContent: ReactNode;
  itemContent: ReactNode;
  ruleContent: ReactNode;
  footer?: ReactNode;
}

export function SidePanel({
  activeTab,
  onTabChange,
  charContent,
  spellContent,
  itemContent,
  ruleContent,
  footer,
}: SidePanelProps) {
  const pages: Record<PanelTab, ReactNode> = {
    char: charContent,
    spell: spellContent,
    item: itemContent,
    rule: ruleContent,
  };
  return (
    <aside className="v2-panel">
      <nav className="v2-panel-tabs">
        {TABS.map((t) => (
          <button
            key={t.key}
            className={activeTab === t.key ? "on" : ""}
            onClick={() => onTabChange(t.key)}
          >
            {t.label}
          </button>
        ))}
      </nav>
      <div className="v2-panel-pages">
        {TABS.map((t) => (
          <section key={t.key} className={`v2-ppage ${activeTab === t.key ? "on" : ""}`}>
            {pages[t.key]}
          </section>
        ))}
      </div>
      {footer && <div className="v2-panel-footer">{footer}</div>}
    </aside>
  );
}
