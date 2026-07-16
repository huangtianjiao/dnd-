"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { io, Socket } from "socket.io-client";

const API = process.env.NEXT_PUBLIC_API || "";

// ──────────────────────────────────────────────────────────────────────────
// 类型定义
// ──────────────────────────────────────────────────────────────────────────

interface AbilityScore {
  score: number;
  mod: number;
}

interface CharacterSheet {
  id: number;
  name: string;
  race: string;
  char_class: string;
  subclass?: string;
  level: number;
  proficiency: number;
  abilities: Record<string, AbilityScore>;
  hp: number;
  hp_max: number;
  temp_hp?: number;
  ac: number;
  speed: number;
  conditions: string[];
  exhaustion: number;
  spell_slots?: Record<string, number>;
  attuned_items?: string[];
  dead?: boolean;
  stable?: boolean;
}

interface SceneData {
  location?: string;
  time?: string;
  atmosphere?: string;
  environment?: string;
  npcs?: { name: string; attitude: string; role: string }[];
  exits?: string[];
  situation?: string;
  story_log?: string;
  world_background?: string;
  campaign_name?: string;
}

interface CombatData {
  active: boolean;
  round: number;
  current_turn?: string;
  initiative_order?: { name: string; initiative: number; side: string }[];
}

interface LogEntry {
  c: string; // dm | you | dice | meta | npc | damage | system | other
  t: string;
  roll?: { d20: number; hit: boolean; crit: boolean; damage?: number };
}

// ──────────────────────────────────────────────────────────────────────────
// 主页面
// ──────────────────────────────────────────────────────────────────────────

export default function Page() {
  const [screen, setScreen] = useState<"menu" | "newGame" | "continue" | "join" | "game">("menu");
  const [log, setLog] = useState<LogEntry[]>([]);
  const [campId, setCampId] = useState<number | null>(null);
  const [charId, setCharId] = useState<number | null>(null);
  const [character, setCharacter] = useState<CharacterSheet | null>(null);
  const [scene, setScene] = useState<SceneData | null>(null);
  const [combat, setCombat] = useState<CombatData | null>(null);
  const [choices, setChoices] = useState<string[]>([]);
  const [inp, setInp] = useState("");
  const [rolling, setRolling] = useState(false);
  const [diceResult, setDiceResult] = useState<{ d20?: number; hit?: boolean; crit?: boolean; dmg?: number } | null>(null);
  const [campaigns, setCampaigns] = useState<{ id: number; name: string; setting?: string }[]>([]);
  const [myName, setMyName] = useState("");
  const [toastMsg, setToastMsg] = useState<{ msg: string; type: string } | null>(null);

  const socketRef = useRef<Socket | null>(null);
  const logEndRef = useRef<HTMLDivElement | null>(null);
  const diceBoxRef = useRef<any>(null);

  // ── Toast ──
  const toast = useCallback((msg: string, type = "info") => {
    setToastMsg({ msg, type });
    setTimeout(() => setToastMsg(null), 3000);
  }, []);

  // ── 滚动日志到底部 ──
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [log]);

  // ── 动态加载 3D 骰子 ──
  useEffect(() => {
    import("@3d-dice/dice-box")
      .then(({ default: DiceBox }) => {
        const db = new DiceBox("#dice-box", { assetPath: "/assets/dice-box" });
        db.init();
        diceBoxRef.current = db;
      })
      .catch(() => console.log("DiceBox 未加载（降级）"));
  }, []);

  // ── API 封装 ──
  const apiPost = useCallback(async (path: string, body: any) => {
    const res = await fetch(`${API}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }, []);

  const apiGet = useCallback(async (path: string) => {
    const res = await fetch(`${API}${path}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }, []);

  // ── 刷新角色卡 ──
  const refreshChar = useCallback(async () => {
    if (!charId) return;
    try {
      const c = await apiGet(`/character/${charId}`);
      setCharacter(c);
    } catch (e) {
      /* 忽略 */
    }
  }, [charId, apiGet]);

  // ── Socket.IO 连接 ──
  const connectWS = useCallback(
    (cid: number, chId: number, name: string) => {
      if (socketRef.current) socketRef.current.disconnect();

      const socket = io(API || window.location.origin, {
        transports: ["websocket"],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: Infinity,
        query: { campaign_id: cid, character_id: chId, name },
      });

      socket.on("connect", () => {
        setLog((l) => [...l, { c: "meta", t: "(已连接)" }]);
      });
      socket.on("disconnect", () => {
        setLog((l) => [...l, { c: "meta", t: "(连接断开，尝试重连...)" }]);
      });
      socket.on("connect_error", (err: Error) => {
        toast(`连接错误: ${err.message}`, "error");
      });

      socket.on("join", (d: any) => {
        setLog((l) => [...l, { c: "meta", t: `${d.name} 加入了` }]);
      });
      socket.on("leave", (d: any) => {
        setLog((l) => [...l, { c: "meta", t: `${d.name} 离开了` }]);
      });
      socket.on("result", (d: any) => {
        const isMe = d.player === name;
        setLog((l) => [
          ...l,
          { c: isMe ? "dm" : "other", t: isMe ? d.narration : `【${d.player}】 ${d.narration}` },
        ]);
        if (d.dice) {
          const dd = d.dice;
          setLog((l) => [
            ...l,
            {
              c: "dice",
              t: `[${d.player}] d20=${dd.d20} ${dd.hit ? "命中" : "未中"}${dd.crit ? " 重击" : ""}${dd.damage ? ` 伤${dd.damage}` : ""}`,
            },
          ]);
        }
        if (d.action_options) setChoices(d.action_options);
        refreshChar();
      });
      socket.on("processing", (d: any) => {
        setLog((l) => [...l, { c: "meta", t: `⏳ ${d.player} 正在判定...` }]);
      });
      socket.on("player_acting", (d: any) => {
        if (d.player !== name)
          setLog((l) => [...l, { c: "meta", t: `⟳ ${d.player} 正在行动` }]);
      });
      socket.on("scene_update", (d: any) => setScene(d.scene || d));
      socket.on("combat_update", (d: any) => setCombat(d));
      socket.on("turn_advanced", (d: any) => {
        setLog((l) => [...l, { c: "meta", t: `轮到 ${d.next || "?"}` }]);
      });
      socket.on("round_end", (d: any) => {
        setLog((l) => [...l, { c: "meta", t: `第 ${d.round} 轮结束` }]);
      });
      socket.on("monster_turn", (d: any) => {
        setLog((l) => [...l, { c: "meta", t: `👾 ${d.monster} 的回合` }]);
      });
      socket.on("combat_end", (d: any) => {
        setLog((l) => [...l, { c: "system", t: `⚔️ 战斗结束: ${d.outcome || ""}` }]);
        setCombat(null);
      });
      socket.on("character_update", (d: any) => {
        refreshChar();
      });
      socket.on("error", (d: any) => {
        toast(d.message || "未知错误", "error");
      });

      socketRef.current = socket;
    },
    [refreshChar, toast]
  );

  // ── 开始新游戏 ──
  const startNewGame = useCallback(async () => {
    const name = myName.trim() || "冒险者";
    const setting = inp.trim();
    if (!setting) {
      toast("请输入世界设定", "warn");
      return;
    }

    try {
      toast("创建角色中...", "info");
      const c = await apiPost("/campaign", { name: `${name}的冒险` });
      const camp = c;

      const ch = await apiPost("/character", {
        name,
        race: "人类",
        char_class: "战士",
        level: 5,
        abilities: { str: 16, dex: 10, con: 15, int: 10, wis: 12, cha: 10 },
        hp_max: 38,
        ac: 18,
        campaign_id: camp.id,
      });

      setCampId(camp.id);
      setCharId(ch.id);

      toast("DM 生成开场中...(约10秒)", "info");
      const r = await apiPost("/open", {
        setting,
        tone: "",
        campaign_id: camp.id,
        character_id: ch.id,
      });

      setLog([]);
      if (r.narration) setLog((l) => [...l, { c: "dm", t: r.narration }]);
      if (r.action_options) setChoices(r.action_options);

      setScreen("game");
      connectWS(camp.id, ch.id, name);
      setInp("");

      // 加载场景和角色
      setTimeout(() => {
        refreshChar();
        apiGet(`/scene/${camp.id}`).then(setScene).catch(() => {});
        apiGet(`/combat/${camp.id}`).then(setCombat).catch(() => {});
      }, 100);
    } catch (e: any) {
      toast("创建游戏失败: " + e.message, "error");
    }
  }, [myName, inp, apiPost, apiGet, connectWS, refreshChar, toast]);

  // ── 继续游戏 ──
  const showContinue = useCallback(async () => {
    setScreen("continue");
    try {
      const data = await apiGet("/campaigns");
      setCampaigns(data.campaigns || []);
    } catch (e) {
      toast("加载战役失败", "error");
    }
  }, [apiGet, toast]);

  const resumeCampaign = useCallback(
    async (cid: number) => {
      try {
        const st = await apiGet(`/campaign/${cid}/state`);
        if (st.characters && st.characters.length > 0) {
          const ch = st.characters[0];
          setCharId(ch.id);
          setMyName(ch.name);
          setCampId(cid);
          setScreen("game");
          connectWS(cid, ch.id, ch.name);
          setLog([]);
          if (st.summary) setLog((l) => [...l, { c: "meta", t: `📖 剧情回顾: ${st.summary.slice(0, 200)}...` }]);
          setTimeout(() => {
            refreshChar();
            apiGet(`/scene/${cid}`).then(setScene).catch(() => {});
            apiGet(`/combat/${cid}`).then(setCombat).catch(() => {});
          }, 100);
        } else {
          toast("该战役没有角色", "warn");
        }
      } catch (e: any) {
        toast("继续游戏失败: " + e.message, "error");
      }
    },
    [apiGet, apiPost, connectWS, refreshChar, toast]
  );

  // ── 加入房间 ──
  const joinGame = useCallback(async () => {
    const cid = parseInt(inp);
    if (!cid) {
      toast("请填写房间号", "warn");
      return;
    }
    const name = myName.trim() || "冒险者";
    try {
      const ch = await apiPost("/join", { name, campaign_id: cid });
      if (ch.error) {
        toast(ch.error, "error");
        return;
      }
      setCharId(ch.character_id || ch.id);
      setCampId(cid);
      setMyName(name);
      setScreen("game");
      connectWS(cid, ch.character_id || ch.id, name);
      setLog([]);
      setLog((l) => [...l, { c: "meta", t: `加入房间 #${cid}` }]);
      setInp("");
    } catch (e: any) {
      toast("加入房间失败: " + e.message, "error");
    }
  }, [inp, myName, apiPost, connectWS, toast]);

  // ── 发送行动 ──
  const send = useCallback(() => {
    const t = inp.trim();
    if (!t || !socketRef.current) return;
    setLog((l) => [...l, { c: "you", t: `> ${t}` }]);
    socketRef.current.emit("action", { player_input: t });
    setInp("");
  }, [inp]);

  // ── AI 生成世界设定 ──
  const generateWorld = useCallback(async () => {
    try {
      const r = await apiPost("/generate_setting", {});
      if (r.setting) {
        setInp(r.setting);
        toast("世界设定生成成功", "success");
      }
    } catch (e: any) {
      toast("生成失败: " + e.message, "error");
    }
  }, [apiPost, toast]);

  // ── HP 颜色 ──
  const hpColor = (pct: number) => (pct > 50 ? "#22aa22" : pct > 25 ? "#aaaa22" : "#aa2222");

  // ── 渲染 ──
  if (screen === "menu") {
    return (
      <main className="min-h-screen flex items-center justify-center bg-neutral-900 text-neutral-100">
        <div className="text-center space-y-6">
          <h1 className="text-4xl font-bold text-amber-400">🐉 AI DM</h1>
          <p className="text-neutral-500">D&D 5E 硬性判定链跑团系统</p>
          <div className="space-y-3">
            <button onClick={() => setScreen("newGame")} className="block w-64 px-6 py-3 bg-amber-400 text-neutral-900 font-bold rounded hover:bg-amber-300">
              🆕 开始新游戏
            </button>
            <button onClick={showContinue} className="block w-64 px-6 py-3 bg-neutral-800 border border-neutral-700 rounded hover:border-amber-400">
              📖 继续游戏
            </button>
            <button onClick={() => setScreen("join")} className="block w-64 px-6 py-3 bg-neutral-800 border border-neutral-700 rounded hover:border-amber-400">
              🚪 加入房间
            </button>
          </div>
        </div>
      </main>
    );
  }

  if (screen === "newGame") {
    return (
      <main className="min-h-screen flex items-center justify-center bg-neutral-900 text-neutral-100 p-4">
        <div className="w-full max-w-md space-y-4">
          <h2 className="text-2xl font-bold text-amber-400">开始新冒险</h2>
          <input value={myName} onChange={(e) => setMyName(e.target.value)} placeholder="角色名..." className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded" />
          <textarea value={inp} onChange={(e) => setInp(e.target.value)} placeholder="输入世界设定..." rows={4} className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded resize-none" />
          <div className="flex gap-2">
            <button onClick={generateWorld} className="px-4 py-2 bg-neutral-700 border border-neutral-600 rounded text-sm hover:bg-neutral-600">
              ✨ AI 生成世界设定
            </button>
            <button onClick={() => setScreen("menu")} className="px-4 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm">
              ← 返回
            </button>
          </div>
          <button onClick={startNewGame} className="w-full px-6 py-3 bg-amber-400 text-neutral-900 font-bold rounded hover:bg-amber-300">
            🗺️ 开始冒险
          </button>
        </div>
      </main>
    );
  }

  if (screen === "continue") {
    return (
      <main className="min-h-screen flex items-center justify-center bg-neutral-900 text-neutral-100 p-4">
        <div className="w-full max-w-md space-y-4">
          <h2 className="text-2xl font-bold text-amber-400">继续冒险</h2>
          {campaigns.length === 0 ? (
            <p className="text-neutral-500">暂无保存的战役</p>
          ) : (
            <ul className="space-y-2">
              {campaigns.map((c) => (
                <li key={c.id}>
                  <button onClick={() => resumeCampaign(c.id)} className="w-full text-left px-4 py-3 bg-neutral-800 border border-neutral-700 rounded hover:border-amber-400">
                    <div className="font-bold text-amber-400">#{c.id} {c.name}</div>
                    <div className="text-xs text-neutral-500">{c.setting || "(无摘要)"}</div>
                  </button>
                </li>
              ))}
            </ul>
          )}
          <button onClick={() => setScreen("menu")} className="px-4 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm">
            ← 返回
          </button>
        </div>
      </main>
    );
  }

  if (screen === "join") {
    return (
      <main className="min-h-screen flex items-center justify-center bg-neutral-900 text-neutral-100 p-4">
        <div className="w-full max-w-md space-y-4">
          <h2 className="text-2xl font-bold text-amber-400">加入房间</h2>
          <input value={myName} onChange={(e) => setMyName(e.target.value)} placeholder="角色名..." className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded" />
          <input value={inp} onChange={(e) => setInp(e.target.value)} placeholder="房间号..." className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded" />
          <div className="flex gap-2">
            <button onClick={joinGame} className="flex-1 px-6 py-3 bg-amber-400 text-neutral-900 font-bold rounded hover:bg-amber-300">
              🚪 加入
            </button>
            <button onClick={() => setScreen("menu")} className="px-4 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm">
              ← 返回
            </button>
          </div>
        </div>
      </main>
    );
  }

  // ── 游戏主界面 ──
  const hpPct = character ? Math.max(0, (character.hp / character.hp_max) * 100) : 0;
  const abbr: Record<string, string> = { str: "力", dex: "敏", con: "体", int: "智", wis: "感", cha: "魅" };

  return (
    <main className="min-h-screen bg-neutral-900 text-neutral-100">
      {/* 3D 骰子容器 */}
      <div id="dice-box" style={{ position: "fixed", top: 0, left: 0, width: "100%", height: "100%", pointerEvents: "none", zIndex: 50 }} />

      {/* 骰子结果覆盖层 */}
      {diceResult && (
        <div style={{ position: "fixed", top: "30%", left: 0, width: "100%", textAlign: "center", zIndex: 60 }}>
          <div style={{ fontSize: "3em", fontWeight: "bold", color: diceResult.crit ? "#d4af37" : diceResult.hit ? "#4a4" : "#a44", textShadow: "0 0 20px currentColor" }}>
            {diceResult.d20}
          </div>
          <div style={{ fontSize: "1.2em", color: diceResult.crit ? "#d4af37" : diceResult.hit ? "#4a4" : "#a44" }}>
            {diceResult.crit ? "⚡ 重击!" : diceResult.hit ? "✓ 命中" : "✗ 未中"}
            {diceResult.dmg != null ? ` 💥${diceResult.dmg}` : ""}
          </div>
        </div>
      )}

      {/* Toast */}
      {toastMsg && (
        <div style={{ position: "fixed", top: 12, right: 12, zIndex: 80 }}
          className={`px-4 py-2 rounded shadow-lg ${toastMsg.type === "error" ? "bg-red-800" : toastMsg.type === "warn" ? "bg-yellow-800" : toastMsg.type === "success" ? "bg-green-800" : "bg-blue-800"}`}>
          {toastMsg.msg}
        </div>
      )}

      {/* 三栏布局 */}
      <div className="flex h-screen overflow-hidden">
        {/* 左栏 — 角色卡 */}
        <aside className="w-56 shrink-0 border-r border-neutral-800 overflow-y-auto p-3 space-y-3">
          {character ? (
            <>
              <div className="text-center">
                <div className="text-lg font-bold text-amber-400">{character.name}</div>
                <div className="text-xs text-neutral-500">{character.race} {character.char_class} Lv{character.level}</div>
              </div>

              {/* HP 条 */}
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-neutral-400">HP</span>
                  <span className="text-neutral-300">{character.hp}/{character.hp_max}</span>
                </div>
                <div className="h-2 bg-neutral-800 rounded-full overflow-hidden">
                  <div className="h-full transition-all duration-400 rounded-full" style={{ width: `${hpPct}%`, background: hpColor(hpPct) }} />
                </div>
              </div>

              {/* AC / 速度 / 熟练 */}
              <div className="grid grid-cols-3 gap-1 text-center">
                <div className="bg-neutral-800 rounded p-1">
                  <div className="text-base font-bold text-amber-400">{character.ac}</div>
                  <div className="text-[10px] text-neutral-500">AC</div>
                </div>
                <div className="bg-neutral-800 rounded p-1">
                  <div className="text-base font-bold text-amber-400">{character.speed}</div>
                  <div className="text-[10px] text-neutral-500">速度</div>
                </div>
                <div className="bg-neutral-800 rounded p-1">
                  <div className="text-base font-bold text-amber-400">+{character.proficiency}</div>
                  <div className="text-[10px] text-neutral-500">熟练</div>
                </div>
              </div>

              {/* 六维属性 */}
              <div className="grid grid-cols-2 gap-1">
                {Object.entries(character.abilities).map(([k, v]) => (
                  <div key={k} className="bg-neutral-800 rounded p-1 text-center">
                    <div className="text-[10px] text-neutral-500">{abbr[k] || k}</div>
                    <div className="text-sm font-bold">{v.score}</div>
                    <div className="text-[10px] text-neutral-400">{v.mod >= 0 ? `+${v.mod}` : v.mod}</div>
                  </div>
                ))}
              </div>

              {/* 状态条件 */}
              {character.conditions && character.conditions.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {character.conditions.map((cond, i) => (
                    <span key={i} className="text-[10px] px-1.5 py-0.5 bg-neutral-800 rounded border border-neutral-700">{cond}</span>
                  ))}
                </div>
              )}

              {/* 死亡豁免追踪器 */}
              {character.hp <= 0 && !character.dead && (
                <div className="bg-red-950 border border-red-800 rounded p-2 text-center">
                  <div className="text-xs text-red-400 mb-1">⚠️ 濒死状态</div>
                  {character.stable ? (
                    <div className="text-xs text-green-400">已稳定</div>
                  ) : (
                    <div className="text-xs text-neutral-400">需要死亡豁免检定</div>
                  )}
                </div>
              )}

              {character.dead && (
                <div className="bg-red-950 border border-red-800 rounded p-2 text-center">
                  <div className="text-sm font-bold text-red-400">💀 角色已死亡</div>
                </div>
              )}
            </>
          ) : (
            <div className="text-xs text-neutral-600">加载角色卡...</div>
          )}
        </aside>

        {/* 中栏 — 主舞台 */}
        <section className="flex-1 flex flex-col overflow-hidden">
          {/* 场景盒 */}
          {scene && scene.location && (
            <div className="border-b border-neutral-800 px-4 py-2 bg-neutral-850">
              <div className="text-sm font-bold text-amber-400">📍 {scene.location}</div>
              {scene.atmosphere && <div className="text-xs text-neutral-500">{scene.atmosphere}</div>}
              {scene.npcs && scene.npcs.length > 0 && (
                <div className="text-xs text-neutral-400 mt-1">
                  在场NPC: {scene.npcs.map((n) => n.name).join(", ")}
                </div>
              )}
              {scene.exits && scene.exits.length > 0 && (
                <div className="text-xs text-neutral-400 mt-1">
                  出口: {scene.exits.join(" / ")}
                </div>
              )}
            </div>
          )}

          {/* 叙事区 */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2">
            {log.map((e, i) => (
              <div key={i} className={
                e.c === "you" ? "text-amber-400 text-right" :
                e.c === "dm" ? "text-blue-300" :
                e.c === "npc" ? "text-amber-300" :
                e.c === "dice" ? "text-green-400 text-xs font-mono" :
                e.c === "damage" ? "text-red-400 text-center" :
                e.c === "system" ? "text-neutral-500 text-center" :
                e.c === "meta" ? "text-neutral-600 text-xs" :
                "text-neutral-400"
              }>
                {e.t}
              </div>
            ))}
            <div ref={logEndRef} />
          </div>

          {/* 行动选项 */}
          {choices.length > 0 && (
            <div className="px-4 py-2 flex gap-2 flex-wrap border-t border-neutral-800">
              {choices.map((c, i) => (
                <button key={i} onClick={() => setInp(c)}
                  className="px-3 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400 hover:bg-neutral-700">
                  {i + 1}. {c}
                </button>
              ))}
            </div>
          )}

          {/* 输入框 */}
          <div className="px-4 py-3 flex gap-2 border-t border-neutral-800">
            <input
              value={inp}
              onChange={(e) => setInp(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") send(); }}
              placeholder="输入你的行动..."
              className="flex-1 px-3 py-2 bg-neutral-800 border border-neutral-700 rounded focus:border-amber-400 focus:outline-none"
            />
            <button
              onClick={send}
              disabled={rolling}
              className="px-5 py-2 bg-amber-400 text-neutral-900 font-bold rounded hover:bg-amber-300 disabled:opacity-40"
            >
              {rolling ? "🎲 掷骰中..." : "🎲 掷骰"}
            </button>
          </div>
        </section>

        {/* 右栏 — 战斗面板 */}
        <aside className="w-56 shrink-0 border-l border-neutral-800 overflow-y-auto p-3 space-y-3">
          {/* 战斗状态 */}
          {combat && combat.active ? (
            <>
              <div className="text-sm font-bold text-red-400">⚔️ 战斗中</div>
              <div className="text-xs text-neutral-500">第 {combat.round} 轮</div>
              {combat.initiative_order && (
                <div className="space-y-1">
                  {combat.initiative_order.map((p, i) => (
                    <div key={i} className={`text-xs px-2 py-1 rounded ${p.side === "enemy" ? "bg-red-950 text-red-300" : "bg-blue-950 text-blue-300"}`}>
                      {p.initiative} | {p.name} ({p.side})
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="text-xs text-neutral-600">非战斗状态</div>
          )}

          {/* 玩家信息 */}
          <div className="border-t border-neutral-800 pt-2">
            <div className="text-xs text-neutral-500">玩家: {myName}</div>
            {campId && <div className="text-xs text-neutral-500">战役 #{campId}</div>}
          </div>
        </aside>
      </div>
    </main>
  );
}
