"use client";

import { useEffect, useRef, useState } from "react";
import type { CombatData, GameMode, StreamMessage } from "../../lib/types";

/* ================================================================
 * 主舞台四件套：CombatBar / NarrativeStream / QuickChips / ActionInput
 * （docs/FRONTEND_REDESIGN.md §2 stage/*；InitiativeChip/CombatantCard
 *  与 5 种消息气泡作为内部组件合并实现，见 §8 偏差记录）
 * ================================================================ */

/* ---------------- CombatBar：先攻条 + 参战者 HP 卡 ---------------- */

interface CombatBarProps {
  combat: CombatData | null;
  myName: string;
  onEnemyClick?: (name: string) => void;
  onEndTurn?: () => void;
}

export function CombatBar({ combat, myName, onEnemyClick, onEndTurn }: CombatBarProps) {
  if (!combat?.active) return null;
  const order = combat.initiative_order || [];
  const curIdx = order.findIndex((c) => c.name === combat.current_turn);
  const myTurn = combat.current_turn === myName;

  return (
    <section className="v2-combatbar">
      <div className="v2-init-row">
        <span className="cap">先攻</span>
        <div className="v2-init-strip">
          {order.map((c, i) => {
            const dead = !!c.dead || (c.hp != null && c.hp <= 0);
            return (
              <div
                key={`${c.name}-${i}`}
                className={`v2-init-chip ${c.side === "enemy" ? "enemy" : "ally"} ${
                  i === curIdx ? "current" : ""
                } ${i < curIdx || dead ? "done" : ""}`}
              >
                <span className="iv">{c.initiative}</span>
                {c.name}
                {c.surprised && <span className="surprised">突袭</span>}
              </div>
            );
          })}
        </div>
        <span className="v2-round-info">第 {combat.round} 轮</span>
        {myTurn && onEndTurn && (
          <button className="v2-endturn-btn" onClick={onEndTurn}>
            结束回合 ⏭
          </button>
        )}
      </div>
      <div className="v2-combatant-cards">
        {order.map((c, i) => {
          const hp = c.hp ?? 0;
          const max = c.hp_max ?? 0;
          const pct = max > 0 ? Math.max(0, Math.round((hp / max) * 100)) : 0;
          const dead = !!c.dead || hp <= 0;
          const bloodied = !dead && max > 0 && hp * 2 <= max;
          const isEnemy = c.side === "enemy";
          return (
            <div
              key={`${c.name}-card-${i}`}
              className={`v2-ccard ${isEnemy ? "enemy" : "ally"} ${i === curIdx ? "current" : ""} ${
                dead ? "dead" : ""
              } ${bloodied ? "bloodied" : ""}`}
              onClick={isEnemy && onEnemyClick ? () => onEnemyClick(c.name) : undefined}
              style={isEnemy && onEnemyClick ? { cursor: "pointer" } : undefined}
              title={isEnemy && onEnemyClick ? "查看怪物资料" : undefined}
            >
              <div className="nm">
                <span>
                  {c.name}
                  {c.name === myName ? "（我）" : ""}
                </span>
                <span className="hp-t">
                  {Math.max(0, hp)}/{max || "?"}
                </span>
              </div>
              <div className="hpbar">
                <i style={{ width: `${pct}%` }} />
              </div>
              <div className="sub">
                <span>{isEnemy ? "敌方" : "队友"}</span>
                <span>先攻 {c.initiative}</span>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

/* ---------------- NarrativeStream：叙事流（5 种气泡 + typing） ---------------- */

interface NarrativeStreamProps {
  messages: StreamMessage[];
  busy: boolean;
}

export function NarrativeStream({ messages, busy }: NarrativeStreamProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, busy]);

  return (
    <section className="v2-stream" ref={scrollRef}>
      <div className="v2-stream-col">
        {messages.map((m) => {
          switch (m.type) {
            case "dm":
              return (
                <div key={m.id} className="v2-msg v2-msg-dm">
                  <div className="spine" />
                  <div className="body">
                    <div className="who">{m.speaker || "地下城主"}</div>
                    <div className="text">{m.text}</div>
                  </div>
                </div>
              );
            case "player":
              return (
                <div key={m.id} className="v2-msg v2-msg-player">
                  <div className="bubble">
                    <div className="who">{m.speaker || "你"}</div>
                    <div className="text">{m.text}</div>
                  </div>
                </div>
              );
            case "dice":
              return (
                <div key={m.id} className="v2-msg v2-msg-dice">
                  <div className="v2-dice-card">
                    <div className={`face ${m.dice?.fcls || ""}`}>{m.dice?.face}</div>
                    <div className="meta">
                      <div className="title">{m.dice?.title}</div>
                      <div className="formula">{m.dice?.formula}</div>
                    </div>
                    <span className={`verdict ${m.dice?.vcls || ""}`}>{m.dice?.verdict}</span>
                  </div>
                </div>
              );
            case "harm":
              return (
                <div key={m.id} className="v2-msg v2-msg-harm">
                  <div className={`v2-harm-card ${m.harm?.kind || "dmg"}`}>
                    <span>{m.harm?.text}</span>
                    <span className="num">
                      {m.harm?.kind === "heal" ? "+" : "-"}
                      {m.harm?.amount}
                    </span>
                    {m.harm?.kill && <span className="kill">击杀</span>}
                  </div>
                </div>
              );
            case "event":
            case "meta":
            default:
              return (
                <div key={m.id} className={`v2-msg v2-msg-event ${m.eventCls || ""}`}>
                  <div className="card">
                    {m.speaker && <div className="head">{m.speaker}</div>}
                    {m.text}
                  </div>
                </div>
              );
          }
        })}
        {busy && (
          <div className="v2-msg v2-msg-dm">
            <div className="spine" />
            <div className="body">
              <div className="who">地下城主</div>
              <span className="v2-typing">
                <i />
                <i />
                <i />
              </span>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

/* ---------------- QuickChips：情境快捷行动 ---------------- */

interface ChipDef {
  ico: string;
  label: string;
  say: string;
  cls?: string;
}

const CHIPS: Record<GameMode, ChipDef[]> = {
  explore: [
    { ico: "🔍", label: "搜索附近", say: "我仔细搜索这片区域" },
    { ico: "🤫", label: "潜行前进", say: "我放轻脚步潜行前进" },
    { ico: "👂", label: "仔细聆听", say: "我停下脚步仔细聆听四周的动静" },
    { ico: "🗺", label: "查看地图", say: "我摊开地图确认行进方向" },
    { ico: "🔥", label: "短休", say: "我们在此扎营短休一小时", cls: "rest" },
    { ico: "🛏", label: "长休", say: "我们寻找安全处进行长休", cls: "rest" },
  ],
  social: [
    { ico: "💬", label: "说服", say: "我试图说服对方" },
    { ico: "🎭", label: "欺瞒", say: "我编造一个说辞糊弄对方" },
    { ico: "😠", label: "威吓", say: "我沉下脸威吓对方" },
    { ico: "👁", label: "洞悉", say: "我仔细观察对方的神色，判断真实意图" },
    { ico: "🍺", label: "打探消息", say: "我请对方喝一杯，顺便打探些消息" },
  ],
  combat: [
    { ico: "⚔", label: "攻击", say: "我攻击最近的敌人", cls: "danger" },
    { ico: "✨", label: "施法", say: "我要施放法术", cls: "danger" },
    { ico: "🛡", label: "闪避", say: "我摆出防御姿态（闪避）" },
    { ico: "💨", label: "撤离", say: "我谨慎地撤离敌人的触及范围", cls: "danger" },
    { ico: "🏃", label: "疾走", say: "我全力冲刺（疾走）" },
    { ico: "🧪", label: "治疗药水", say: "我喝下一瓶治疗药水" },
  ],
};

interface QuickChipsProps {
  mode: GameMode;
  choices: string[];
  onAction: (text: string) => void;
  disabled?: boolean;
}

export function QuickChips({ mode, choices, onAction, disabled }: QuickChipsProps) {
  return (
    <div className="v2-quickbar">
      <span className="cap">行动</span>
      {choices.map((c, i) => (
        <button
          key={`${i}-${c}`}
          className="v2-chip choice"
          disabled={disabled}
          onClick={() => onAction(c)}
        >
          {i + 1}. {c}
        </button>
      ))}
      {CHIPS[mode].map((ch) => (
        <button
          key={ch.label}
          className={`v2-chip ${ch.cls || ""}`}
          disabled={disabled}
          onClick={() => onAction(ch.say)}
        >
          <span className="ico">{ch.ico}</span>
          {ch.label}
        </button>
      ))}
    </div>
  );
}

/* ---------------- ActionInput：自由文本行动声明 + 自由掷骰 ---------------- */

interface ActionInputProps {
  onSend: (text: string) => void;
  onFreeRoll: () => void;
  disabled?: boolean;
}

export function ActionInput({ onSend, onFreeRoll, disabled }: ActionInputProps) {
  const [text, setText] = useState("");
  const taRef = useRef<HTMLTextAreaElement>(null);

  const autosize = () => {
    const ta = taRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = Math.min(ta.scrollHeight, 120) + "px";
    }
  };

  const submit = () => {
    const v = text.trim();
    if (!v || disabled) return;
    setText("");
    requestAnimationFrame(() => {
      if (taRef.current) taRef.current.style.height = "auto";
    });
    onSend(v);
  };

  return (
    <footer className="v2-inputbar">
      <div className="v2-input-wrap">
        <button className="v2-dice-btn" title="掷 d20" onClick={onFreeRoll} disabled={disabled}>
          ⚄
        </button>
        <textarea
          ref={taRef}
          rows={1}
          value={text}
          disabled={disabled}
          placeholder="描述你的行动……（Enter 发送，Shift+Enter 换行）"
          onChange={(e) => {
            setText(e.target.value);
            autosize();
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
        />
        <button className="v2-send-btn" onClick={submit} disabled={disabled}>
          行动
        </button>
      </div>
    </footer>
  );
}
