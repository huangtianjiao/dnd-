"use client";

import { useCallback, useRef } from "react";
import { io, Socket } from "socket.io-client";
import { API, API_KEY, setSessionToken as _setApiSessionToken } from "../lib/api";
import type { LogEntry, SceneData, CombatData, PartyMember } from "../lib/types";

/**
 * 会话令牌（P0-03/P0-05）：由 /auth/session 或 /room/create 签发，
 * WS 连接经 Socket.IO auth 载荷传递，不进 query string。
 * 同时写入 lib/api.ts 供 REST 请求携带 Authorization: Bearer（P0-4 ownership）。
 */
let sessionToken = "";
export function setSessionToken(token: string) {
  sessionToken = token;
  _setApiSessionToken(token);
}
export function getSessionToken() {
  return sessionToken;
}

/** 房主令牌（P0-01）：/room/create 签发，供 HostControls 的 Bearer 管理操作使用。 */
let hostToken = "";
export function setHostToken(token: string) {
  hostToken = token;
}
export function getHostToken() {
  return hostToken;
}

/**
 * 按 dice.kind 分派格式化行动骰子日志。
 * 后端 graph.run 返回 20+ 种 kind（攻击/法术/检定/休息/升级/移动…），字段各异；
 * 统一在此分派，避免前端无脑按 d20/hit 渲染导致属性检定显示"未中"、
 * 治疗法术显示"d20=undefined"等问题。返回 null 表示不写 dice 日志行。
 */
function formatDice(player: string, d: any): string | null {
  if (!d || typeof d !== "object") return null;
  const pfx = `[${player}]`;
  const kind: string = d.kind || "";
  switch (kind) {
    case "attack":
    case "opportunity_attack": {
      let s = `${pfx} 攻击 d20=${d.d20} ${d.hit ? "命中" : "未中"}${d.crit ? " 重击" : ""}`;
      if (d.damage) s += ` 伤${d.damage}${d.damage_type ? `(${d.damage_type})` : ""}`;
      if (d.weapon) s += ` ${d.weapon}`;
      return s;
    }
    case "cast": {
      // 豁免类法术
      if (d.save_success !== undefined) {
        let s = `${pfx} ${d.spell_name || "法术"} 豁免${d.save_success ? "成功" : "失败"}`;
        if (d.damage) s += ` 伤${d.damage}${d.damage_type ? `(${d.damage_type})` : ""}`;
        return s;
      }
      // 治疗类法术
      if (d.damage_type === "治疗" || d.heal != null) {
        return `${pfx} ${d.spell_name || "治疗法术"} 治疗${d.damage ?? d.heal ?? 0}`;
      }
      // 攻击检定型法术（有 d20）
      if (d.d20 !== undefined) {
        let s = `${pfx} ${d.spell_name || "法术"} d20=${d.d20} ${d.hit ? "命中" : "未中"}${d.crit ? " 重击" : ""}`;
        if (d.damage) s += ` 伤${d.damage}${d.damage_type ? `(${d.damage_type})` : ""}`;
        return s;
      }
      // 自动命中无骰
      let s = `${pfx} ${d.spell_name || "法术"} 命中`;
      if (d.damage) s += ` 伤${d.damage}${d.damage_type ? `(${d.damage_type})` : ""}`;
      return s;
    }
    case "ability_check":
    case "explore":
    case "hide":
    case "search":
    case "grapple":
    case "shove":
    case "study":
    case "social": {
      const label = d.ability || d.skill || kind;
      let s = `${pfx} ${label} d20=${d.d20}=${d.check_total} ${d.success ? "成功" : "失败"}`;
      if (d.dc) s += `(DC${d.dc})`;
      return s;
    }
    case "rest":
      return d.hp_restored ? `${pfx} 休息 恢复${d.hp_restored}HP` : `${pfx} 休息`;
    case "levelup":
      return `${pfx} 升级→${d.new_level}级 +${d.hp_gained || 0}HP`;
    case "travel": {
      let s = `${pfx} 旅行 ${d.nav_result || ""}`;
      if (d.encounter_result) s += ` 遭遇:${d.encounter_result}`;
      return s.trim();
    }
    case "start_combat":
      return `${pfx} 先攻 ${(d.initiative_order || []).map((x: any) => `${x.name}=${x.init}`).join(", ")}`;
    case "end_combat":
      return `${pfx} 战斗结束`;
    case "dash":
    case "dodge":
    case "disengage":
    case "help":
    case "ready":
    case "use_item":
      return `${pfx} ${kind} ${d.effect || d.item || ""}`.trim();
    default:
      // 未知 kind 但含 d20：退化显示，避免信息丢失
      if (d.d20 !== undefined)
        return `${pfx} d20=${d.d20}${d.hit !== undefined ? (d.hit ? " 命中" : " 未中") : ""}${d.damage ? ` 伤${d.damage}` : ""}`;
      return null;
  }
}

interface UseSocketOptions {
  onLog: (entry: LogEntry) => void;
  onScene: (scene: SceneData) => void;
  onCombat: (combat: CombatData) => void;
  onChoices: (choices: string[]) => void;
  onCharacterUpdate: () => void;
  onToast: (msg: string, type?: string) => void;
  /** 服务端主动断开（如房间关闭）时回调 */
  onServerDisconnect?: () => void;
  /** 战斗结束事件（combat_end）回调，用于清空本地战斗态 */
  onCombatEnd?: () => void;
  /** 派对成员变更（join/leave 事件）回调 */
  onPartyUpdate?: (members: PartyMember[]) => void;
  /** v2：结构化 result 分发（优先于 onLog 文本路径，见 docs/FRONTEND_REDESIGN.md §4） */
  onResult?: (d: any) => void;
  /** v2：结构化 monster_action 分发（优先于 onLog 文本路径） */
  onMonsterActionEvent?: (monster: string, result: any) => void;
}

export function useSocket(opts: UseSocketOptions) {
  const socketRef = useRef<Socket | null>(null);
  const optsRef = useRef(opts);
  optsRef.current = opts;

  const connectWS = useCallback(
    (cid: number, chId: number, name: string, role?: string, dmToken?: string) => {
      if (socketRef.current) socketRef.current.disconnect();

      const o = optsRef.current;
      // ★ P0-05: 凭据走 Socket.IO auth 载荷（不进 query string，避免泄露到
      //   代理日志/网络诊断/监控）。DM 权限由后端 /auth/session 签发的令牌决定。
      const socket = io(API || window.location.origin, {
        transports: ["websocket"],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 10000,
        reconnectionAttempts: 30,
        query: {
          campaign_id: cid,
          character_id: chId,
          name,
        },
        auth: {
          token: sessionToken,
        },
      });

      socket.on("connect", () => o.onLog({ c: "meta", t: "(已连接)" }));
      socket.on("disconnect", (reason: string) => {
        if (reason === "io server disconnect") {
          o.onToast("房间已关闭，请重新加入", "warn");
          o.onServerDisconnect?.();
        } else if (reason === "io client disconnect") {
          // 客户端主动断开（如切换房间/退出），不会自动重连
          o.onLog({ c: "meta", t: "(已断开连接)" });
        } else {
          o.onLog({ c: "meta", t: "(连接断开，重连中...)" });
        }
      });
      socket.on("connect_error", (err: Error) => o.onToast(`连接错误: ${err.message}`, "error"));

      socket.on("join", (d: any) => {
        o.onLog({ c: "meta", t: `${d.name} 加入了` });
        if (d.players && o.onPartyUpdate) {
          o.onPartyUpdate(
            (d.players as any[]).map((p) => ({
              name: p.name,
              characterId: p.character_id,
              isDm: p.is_dm,
              connected: p.connected,
            }))
          );
        }
      });
      socket.on("leave", (d: any) => {
        o.onLog({ c: "meta", t: `${d.name} 离开了` });
        if (d.players && o.onPartyUpdate) {
          o.onPartyUpdate(
            (d.players as any[]).map((p) => ({
              name: p.name,
              characterId: p.character_id,
              isDm: p.is_dm,
              connected: p.connected,
            }))
          );
        }
      });

      socket.on("result", (d: any) => {
        if (o.onResult) {
          // v2 结构化路径：narration/dice/choices/time/encounter 全部由 onResult 消费
          o.onResult(d);
        } else {
          const isMe = d.player === name;
          o.onLog({
            c: "dm",
            speaker: "DM (AI)",
            t: isMe ? d.narration : `【${d.player}】 ${d.narration}`,
          });
          if (d.dice) {
            const t = formatDice(d.player, d.dice);
            if (t) o.onLog({ c: "dice", t });
          }
          if (d.action_options) o.onChoices(d.action_options);
        }
        // 多人回合制：动作耗尽提示（后端 apply_node turn_hint）
        if (d.turn_hint === "action_exhausted" && d.player === name) {
          o.onLog({ c: "meta", t: "（本回合动作已用完，可点击“结束回合”）" });
        }
        o.onCharacterUpdate();
      });

      socket.on("processing", (d: any) => o.onLog({ c: "meta", t: `⏳ ${d.player} 正在判定...` }));
      socket.on("player_acting", (d: any) => {
        if (d.player !== name) o.onLog({ c: "meta", t: `⟳ ${d.player} 正在行动` });
      });
      socket.on("scene_update", (d: any) => o.onScene(d.scene || d));
      socket.on("combat_update", (d: any) => o.onCombat(d));
      socket.on("turn_advanced", (d: any) =>
        o.onLog({
          c: "meta",
          t: `轮到 ${d.next || "?"}${d.next_next ? `（下一位：${d.next_next}）` : ""}`,
        })
      );
      socket.on("round_end", (d: any) => o.onLog({ c: "meta", t: `第 ${d.round} 轮结束` }));
      // 死亡豁免（后端 combat_flow 回合开始时掷，R-DMG-017）
      socket.on("death_save", (d: any) => {
        o.onLog({ c: "system", t: d.text || `💀 ${d.player} 死亡豁免 d20=${d.roll}` });
        o.onCharacterUpdate();
      });
      socket.on("monster_turn", (d: any) => o.onLog({ c: "meta", t: `👾 ${d.monster} 的回合` }));
      socket.on("player_ready", (d: any) => o.onLog({ c: "meta", t: `✓ ${d.player} 已准备` }));
      socket.on("monster_action", (d: any) => {
        if (o.onMonsterActionEvent) o.onMonsterActionEvent(d.monster, d.result);
        else o.onLog({ c: "npc", t: `👾 ${d.monster}: ${JSON.stringify(d.result || {})}` });
      });
      socket.on("combat_end", (d: any) => {
        o.onLog({ c: "system", t: `⚔️ 战斗结束: ${d.outcome || ""}` });
        o.onCombatEnd?.();
      });
      socket.on("character_update", () => o.onCharacterUpdate());
      socket.on("error", (d: any) => o.onToast(d.message || "未知错误", "error"));

      socketRef.current = socket;
    },
    []
  );

  const send = useCallback((text: string) => {
    if (!text || !socketRef.current) return false;
    socketRef.current.emit("action", { player_input: text });
    return true;
  }, []);

  /** 结束自己的回合，推进先攻序列（后端 ws.on_end_turn）。 */
  const endTurn = useCallback(() => {
    socketRef.current?.emit("end_turn", {});
  }, []);

  /** 标记自己准备就绪（后端 ws.on_ready → player_ready 广播）。 */
  const ready = useCallback(() => {
    socketRef.current?.emit("ready", {});
  }, []);

  /** DM: 通知怪物回合开始（后端 ws.on_monster_turn）。 */
  const dmMonsterTurn = useCallback((monsterName: string) => {
    socketRef.current?.emit("monster_turn", { monster_name: monsterName });
  }, []);

  /** DM: 推送怪物行动结果（后端 ws.on_monster_action）。 */
  const dmMonsterAction = useCallback((monsterName: string, actionResult: any) => {
    socketRef.current?.emit("monster_action", { monster_name: monsterName, action_result: actionResult });
  }, []);

  /** DM: 结束战斗（后端 ws.on_combat_end）。 */
  const dmCombatEnd = useCallback((outcome: string = "victory") => {
    socketRef.current?.emit("combat_end", { outcome });
  }, []);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }
  }, []);

  return { connectWS, send, endTurn, ready, dmMonsterTurn, dmMonsterAction, dmCombatEnd, disconnect, socketRef };
}
