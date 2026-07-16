"use client";

import { useCallback, useRef } from "react";
import { io, Socket } from "socket.io-client";
import type { LogEntry, SceneData, CombatData, CharacterSheet } from "../lib/types";

const API = process.env.NEXT_PUBLIC_API || "";

interface UseSocketOptions {
  onLog: (entry: LogEntry) => void;
  onScene: (scene: SceneData) => void;
  onCombat: (combat: CombatData) => void;
  onChoices: (choices: string[]) => void;
  onCharacterUpdate: () => void;
  onToast: (msg: string, type?: string) => void;
}

export function useSocket(opts: UseSocketOptions) {
  const socketRef = useRef<Socket | null>(null);
  const optsRef = useRef(opts);
  optsRef.current = opts;

  const connectWS = useCallback(
    (cid: number, chId: number, name: string) => {
      if (socketRef.current) socketRef.current.disconnect();

      const o = optsRef.current;
      const socket = io(API || window.location.origin, {
        transports: ["websocket"],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: Infinity,
        query: { campaign_id: cid, character_id: chId, name },
      });

      socket.on("connect", () => o.onLog({ c: "meta", t: "(已连接)" }));
      socket.on("disconnect", () => o.onLog({ c: "meta", t: "(连接断开，尝试重连...)" }));
      socket.on("connect_error", (err: Error) => o.onToast(`连接错误: ${err.message}`, "error"));

      socket.on("join", (d: any) => o.onLog({ c: "meta", t: `${d.name} 加入了` }));
      socket.on("leave", (d: any) => o.onLog({ c: "meta", t: `${d.name} 离开了` }));

      socket.on("result", (d: any) => {
        const isMe = d.player === name;
        o.onLog({
          c: isMe ? "dm" : "other",
          t: isMe ? d.narration : `【${d.player}】 ${d.narration}`,
        });
        if (d.dice) {
          const dd = d.dice;
          o.onLog({
            c: "dice",
            t: `[${d.player}] d20=${dd.d20} ${dd.hit ? "命中" : "未中"}${dd.crit ? " 重击" : ""}${dd.damage ? ` 伤${dd.damage}` : ""}`,
          });
        }
        if (d.action_options) o.onChoices(d.action_options);
        o.onCharacterUpdate();
      });

      socket.on("processing", (d: any) => o.onLog({ c: "meta", t: `⏳ ${d.player} 正在判定...` }));
      socket.on("player_acting", (d: any) => {
        if (d.player !== name) o.onLog({ c: "meta", t: `⟳ ${d.player} 正在行动` });
      });
      socket.on("scene_update", (d: any) => o.onScene(d.scene || d));
      socket.on("combat_update", (d: any) => o.onCombat(d));
      socket.on("turn_advanced", (d: any) => o.onLog({ c: "meta", t: `轮到 ${d.next || "?"}` }));
      socket.on("round_end", (d: any) => o.onLog({ c: "meta", t: `第 ${d.round} 轮结束` }));
      socket.on("monster_turn", (d: any) => o.onLog({ c: "meta", t: `👾 ${d.monster} 的回合` }));
      socket.on("combat_end", (d: any) => {
        o.onLog({ c: "system", t: `⚔️ 战斗结束: ${d.outcome || ""}` });
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

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }
  }, []);

  return { connectWS, send, disconnect, socketRef };
}
