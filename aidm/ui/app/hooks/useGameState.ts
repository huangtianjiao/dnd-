"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { apiGet } from "../lib/api";
import type {
  CharacterSheet,
  CombatData,
  DiceCardData,
  GameClock,
  HarmCardData,
  LogEntry,
  PartyMember,
  SceneData,
  StreamMessage,
} from "../lib/types";

/* ================================================================
 * useCharacter —— 角色卡 server state + character_update 防抖重取
 * （见 docs/FRONTEND_REDESIGN.md §3）
 * ================================================================ */
export function useCharacter(charId: number | null) {
  const [character, setCharacter] = useState<CharacterSheet | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const refreshChar = useCallback(async () => {
    if (!charId) return;
    try {
      const c = await apiGet<CharacterSheet>(`/character/${charId}`);
      setCharacter(c);
    } catch {
      /* 忽略瞬时错误 */
    }
  }, [charId]);

  /** character_update 事件 → 300ms 防抖重取（一轮行动可能触发多次） */
  const refreshDebounced = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(refreshChar, 300);
  }, [refreshChar]);

  useEffect(() => {
    setCharacter(null);
    if (charId) refreshChar();
  }, [charId, refreshChar]);

  useEffect(
    () => () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    },
    []
  );

  return { character, setCharacter, refreshChar, refreshDebounced };
}

/* ================================================================
 * useCombat —— 战斗 server state（WS combat_update 覆盖 / combat_end 清空）
 * ================================================================ */
export function useCombat() {
  const [combat, setCombat] = useState<CombatData | null>(null);

  const handleCombatUpdate = useCallback((d: CombatData) => setCombat(d), []);
  const handleCombatEnd = useCallback(() => setCombat(null), []);
  const loadCombat = useCallback(async (campId: number) => {
    try {
      setCombat(await apiGet<CombatData>(`/combat/${campId}`));
    } catch {
      /* 无进行中的战斗 */
    }
  }, []);

  return { combat, setCombat, handleCombatUpdate, handleCombatEnd, loadCombat };
}

/* ================================================================
 * useGameState —— 叙事流消息 / choices / 场景 / 队伍 / 忙态 / 游戏内时钟
 *
 * result 事件的 dice 对象在这里完成结构化分派：
 *   dice.d20      → 骰子卡（diceCardOf）+ DiceLayer 动画
 *   dice.damage   → 伤害/治疗浮卡（harmCardOf，target_killed → 击杀徽标）
 *   dice.time     → TopBar 游戏时钟 + 时间推进事件卡
 *   dice.encounter→ 战斗开场卡序列（遭遇/突袭）或不开战的征兆卡
 * ================================================================ */

let msgSeq = 1;

function clockIcon(label: string) {
  return /夜|凌晨|黄昏/.test(label) ? "☾" : "☀";
}

type Vcls = DiceCardData["vcls"];
type Fcls = NonNullable<DiceCardData["fcls"]>;

const fclsOf = (d20: number | undefined): Fcls =>
  d20 === 20 ? "crit" : d20 === 1 ? "fail" : "";

/** 按 dice.kind 分派生成骰子卡数据（移植自旧 useSocket.formatDice，结构化输出） */
function diceCardOf(d: any): DiceCardData | null {
  if (!d || typeof d !== "object") return null;
  const kind: string = d.kind || "";
  const fcls = fclsOf(d.d20);
  const dmgTxt = d.damage
    ? ` · ${d.damage_type === "治疗" ? "治疗" : "伤害"} ${d.damage}${d.damage_type && d.damage_type !== "治疗" ? `（${d.damage_type}）` : ""}`
    : "";

  switch (kind) {
    case "attack":
    case "opportunity_attack": {
      const vcls: Vcls = d.crit ? "crit" : d.hit ? "hit" : "miss";
      return {
        title: `${d.weapon ? d.weapon + " " : ""}攻击${d.target_name ? ` → ${d.target_name}` : ""}`,
        formula: `d20 = ${d.d20}${dmgTxt}`,
        face: d.d20 ?? "—",
        verdict: d.crit ? "重击！" : d.hit ? "命中" : "未命中",
        vcls,
        fcls,
      };
    }
    case "cast": {
      const name = d.spell_name || "法术";
      const tgt = d.target_name ? ` → ${d.target_name}` : "";
      // 豁免类法术
      if (d.save_success !== undefined) {
        return {
          title: `${name}${tgt}`,
          formula: `目标豁免${dmgTxt}`,
          face: "✦",
          verdict: d.save_success ? "豁免成功" : "豁免失败",
          vcls: d.save_success ? "hit" : "miss",
        };
      }
      // 治疗类法术
      if (d.damage_type === "治疗" || d.heal != null) {
        return {
          title: `${name}${tgt}`,
          formula: `恢复 ${d.damage ?? d.heal ?? 0} 点生命`,
          face: "✚",
          verdict: "治疗",
          vcls: "hit",
        };
      }
      // 攻击检定型法术
      if (d.d20 !== undefined) {
        const vcls: Vcls = d.crit ? "crit" : d.hit ? "hit" : "miss";
        return {
          title: `${name}${tgt}`,
          formula: `d20 = ${d.d20}${dmgTxt}`,
          face: d.d20,
          verdict: d.crit ? "重击！" : d.hit ? "命中" : "未命中",
          vcls,
          fcls,
        };
      }
      // 自动命中（魔法飞弹等）
      return {
        title: `${name}${tgt}`,
        formula: `自动命中${dmgTxt}`,
        face: "✦",
        verdict: "必中",
        vcls: "hit",
      };
    }
    case "ability_check":
    case "explore":
    case "hide":
    case "search":
    case "grapple":
    case "shove":
    case "study":
    case "social": {
      const ok = !!d.success;
      return {
        title: `${d.ability || d.skill || kind}检定`,
        formula: `d20(${d.d20}) = ${d.check_total}${d.dc ? ` vs DC ${d.dc}` : ""}`,
        face: d.d20 ?? "—",
        verdict: ok ? "成功" : "失败",
        vcls: ok ? "hit" : "miss",
        fcls,
      };
    }
    case "rest":
      return {
        title: "休整",
        formula: d.hp_restored ? `恢复 ${d.hp_restored} HP` : "养精蓄锐",
        face: "☾",
        verdict: "休息",
        vcls: "hit",
      };
    case "levelup":
      return {
        title: "升级",
        formula: `→ ${d.new_level} 级${d.hp_gained ? ` · HP +${d.hp_gained}` : ""}`,
        face: "★",
        verdict: "提升",
        vcls: "crit",
        fcls: "crit",
      };
    case "travel":
      return {
        title: "旅行",
        formula:
          [d.nav_result, d.encounter_result ? `遭遇：${d.encounter_result}` : ""]
            .filter(Boolean)
            .join(" · ") || "行进中",
        face: "🗺",
        verdict: "旅行",
        vcls: "hit",
      };
    case "start_combat": {
      const seq = (d.initiative_order || [])
        .map((x: any) => `${x.name}${x.init ?? x.initiative ?? "?"}`)
        .join(" · ");
      return { title: "先攻", formula: seq, face: "⏱", verdict: "开战", vcls: "crit", fcls: "crit" };
    }
    case "end_combat":
      return { title: "战斗结束", formula: "", face: "⚑", verdict: "结束", vcls: "hit" };
    default:
      if (d.d20 !== undefined) {
        return {
          title: kind || "掷骰",
          formula: `d20 = ${d.d20}${dmgTxt}`,
          face: d.d20,
          verdict: d.hit === undefined ? "结果" : d.hit ? "命中" : "未中",
          vcls: d.hit ? "hit" : "miss",
          fcls,
        };
      }
      return null;
  }
}

/** 伤害/治疗浮卡（target_killed → 击杀徽标） */
function harmCardOf(d: any): HarmCardData | null {
  if (!d || typeof d !== "object") return null;
  const heal = d.damage_type === "治疗" || d.heal != null;
  const dmg = typeof d.damage === "number" ? d.damage : typeof d.heal === "number" ? d.heal : 0;
  if (dmg <= 0) return null;
  if (heal) {
    return { text: `${d.target_name || "你"} 恢复生命`, amount: dmg, kind: "heal" };
  }
  if (d.hit === false) return null; // 未命中不出伤害卡
  return {
    text: d.target_name ? `${d.target_name} 受到${d.damage_type || ""}伤害` : `造成${d.damage_type || ""}伤害`,
    amount: dmg,
    kind: "dmg",
    kill: !!d.target_killed,
  };
}

interface EventCardInput {
  text: string;
  cls?: "" | "combat" | "time";
  head?: string;
}

/** dice.encounter / dice.time → 事件卡序列（B 阶段新增数据的 UI 消费点） */
function eventCardsOf(d: any): EventCardInput[] {
  const out: EventCardInput[] = [];
  if (!d || typeof d !== "object") return out;
  const enc = d.encounter;
  if (enc && typeof enc === "object") {
    if (enc.combat_started) {
      out.push({ head: "⚔ 遭遇", text: enc.description || "战斗打响！", cls: "combat" });
      if (enc.surprise) {
        out.push({
          head: "✦ 突袭",
          text:
            typeof enc.surprise === "string"
              ? enc.surprise
              : "部分参战者被突袭——其先攻检定具有劣势。",
          cls: "combat",
        });
      }
    } else if (!enc.suppressed && (enc.type || enc.description)) {
      // 非战斗遭遇 / 环境征兆：不开战，仅叙事提示
      out.push({
        head: "✦ 征兆",
        text: enc.description || `遭遇了${enc.type}，但并未发展为战斗。`,
        cls: "",
      });
    }
  }
  const t = d.time;
  if (t && typeof t === "object") {
    const label: string = t.clock || t.label || "";
    out.push({
      text: `${clockIcon(label)} 第 ${t.day ?? 1} 天 · ${label}${t.note ? ` —— ${t.note}` : ""}`,
      cls: "time",
    });
  }
  return out;
}

interface UseGameStateDeps {
  getMyName: () => string;
  /** result.dice 含 d20 时回调（驱动 DiceLayer 动画） */
  onDiceFace?: (d: any) => void;
}

export function useGameState(deps: UseGameStateDeps) {
  const [messages, setMessages] = useState<StreamMessage[]>([]);
  const [choices, setChoices] = useState<string[]>([]);
  const [scene, setScene] = useState<SceneData | null>(null);
  const [party, setParty] = useState<PartyMember[]>([]);
  const [busy, setBusy] = useState(false);
  const [gameClock, setGameClock] = useState<GameClock | null>(null);
  const lastLocRef = useRef<string | undefined>(undefined);
  const depsRef = useRef(deps);
  depsRef.current = deps;

  const push = useCallback((m: Omit<StreamMessage, "id">) => {
    setMessages((ms) => [...ms, { ...m, id: msgSeq++ }]);
  }, []);

  const pushEvent = useCallback(
    (text: string, eventCls: StreamMessage["eventCls"] = "", head?: string) => {
      push({ type: "event", text, eventCls, speaker: head });
    },
    [push]
  );

  const pushPlayer = useCallback(
    (text: string, name?: string) => {
      push({ type: "player", text, speaker: name || depsRef.current.getMyName() || "你" });
    },
    [push]
  );

  const pushDiceCard = useCallback(
    (dice: DiceCardData) => push({ type: "dice", dice }),
    [push]
  );

  /** WS scene_update → 场景覆盖；地点变化时插入场景事件卡 */
  const handleScene = useCallback(
    (s: SceneData) => {
      setScene(s);
      const loc = s?.location;
      if (loc && loc !== lastLocRef.current) {
        lastLocRef.current = loc;
        pushEvent(`—— ${loc}${s.time ? ` · ${s.time}` : ""} ——`, "");
      }
    },
    [pushEvent]
  );

  /** WS result / REST /chat（HITL）结构化结果 → 叙事流 */
  const onResult = useCallback(
    (d: any) => {
      setBusy(false);
      const isMe = d.player === depsRef.current.getMyName();
      if (d.narration) {
        push({
          type: "dm",
          speaker: "地下城主",
          text: isMe ? d.narration : `【${d.player}】${d.narration}`,
        });
      }
      const dz = d.dice;
      if (dz && typeof dz === "object") {
        if (dz.d20 !== undefined) depsRef.current.onDiceFace?.(dz);
        const t = dz.time;
        if (t && typeof t === "object") {
          setGameClock({ day: t.day ?? 1, label: t.clock || t.label || "" });
        }
        for (const ev of eventCardsOf(dz)) pushEvent(ev.text, ev.cls || "", ev.head);
        const dc = diceCardOf(dz);
        if (dc) push({ type: "dice", dice: dc });
        const hc = harmCardOf(dz);
        if (hc) push({ type: "harm", harm: hc });
      }
      if (d.action_options) setChoices(d.action_options);
      if (d.scene) handleScene(d.scene);
    },
    [push, pushEvent, handleScene]
  );

  /** useSocket 旧文本日志路径 → v2 事件卡/气泡转译 */
  const onLog = useCallback(
    (entry: LogEntry) => {
      if (entry.c === "meta" && entry.t.includes("正在判定")) {
        setBusy(true);
        return;
      }
      if (entry.c === "meta") pushEvent(entry.t, "");
      else if (entry.c === "system" || entry.c === "npc") pushEvent(entry.t, "combat");
      else if (entry.c === "dm")
        push({ type: "dm", speaker: entry.speaker || "地下城主", text: entry.t });
      else if (entry.c === "you") push({ type: "player", speaker: entry.speaker, text: entry.t });
      // dice/damage 文本行已被结构化卡片取代，忽略
    },
    [push, pushEvent]
  );

  /** WS monster_action → 怪物回合事件卡（红虚线，内嵌叙事区） */
  const onMonsterAction = useCallback(
    (monster: string, result: any) => {
      let summary = "";
      if (result && typeof result === "object") {
        if (result.narration) summary = result.narration;
        else if (result.d20 !== undefined)
          summary = `d20=${result.d20} ${result.hit ? "命中" : "未中"}${result.damage ? `，造成 ${result.damage} 点伤害` : ""}`;
        else if (result.damage) summary = `造成 ${result.damage} 点伤害`;
      }
      if (!summary)
        summary = typeof result === "string" ? result : JSON.stringify(result || {}).slice(0, 140);
      pushEvent(summary, "combat", `⚔ ${monster} 的回合`);
    },
    [pushEvent]
  );

  /** WS join/leave → 队伍条覆盖（保留已知的 HP 数据） */
  const onPartyUpdate = useCallback((members: PartyMember[]) => {
    setParty((prev) =>
      members.map((m) => {
        const ex = prev.find((p) => p.characterId === m.characterId);
        return ex ? { ...m, hp: ex.hp, hpMax: ex.hpMax } : m;
      })
    );
  }, []);

  /** 自己角色卡刷新后 → 同步 HP 到队伍条（无变化时返回原引用，
   *  避免 page 层 effect 依赖 gs 对象时陷入 setState → 重渲染循环） */
  const syncOwnHp = useCallback((charId: number, hp: number, hpMax: number) => {
    setParty((prev) => {
      const idx = prev.findIndex((m) => m.characterId === charId);
      if (idx < 0) return prev;
      const m = prev[idx];
      if (m.hp === hp && m.hpMax === hpMax) return prev;
      const next = [...prev];
      next[idx] = { ...m, hp, hpMax };
      return next;
    });
  }, []);

  /** 进入新会话/战役时重置本地流 */
  const reset = useCallback((initial?: Omit<StreamMessage, "id">[]) => {
    msgSeq = 1;
    setMessages((initial || []).map((m) => ({ ...m, id: msgSeq++ })));
    setChoices([]);
    setBusy(false);
    setGameClock(null);
    lastLocRef.current = undefined;
  }, []);

  return {
    messages,
    choices,
    setChoices,
    scene,
    setScene,
    party,
    setParty,
    busy,
    setBusy,
    gameClock,
    setGameClock,
    onResult,
    onLog,
    onMonsterAction,
    onPartyUpdate,
    handleScene,
    pushPlayer,
    pushEvent,
    pushDiceCard,
    syncOwnHp,
    reset,
  };
}
