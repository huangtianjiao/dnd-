"use client";
import { useEffect, useRef, useState } from "react";

const API = process.env.NEXT_PUBLIC_API || "http://localhost:8080";

/** AI DM 跑团前端（Next.js + Tailwind + @3d-dice/dice-box 3D骰子）
 * 硬性判定链：玩家点击"掷骰"→ 3D物理骰子动画 → 后端secrets RNG算d20 → 揭示权威值 → LLM叙事
 * 3D动画是视觉参与感，骰子值来自后端（硬性判定不破）。 */
export default function Page() {
  const [inp, setInp] = useState("");
  const [log, setLog] = useState<{c: string; t: string}[]>([]);
  const [campId, setCampId] = useState<number | null>(null);
  const [charId, setCharId] = useState<number | null>(null);
  const [hp, setHp] = useState("38/38");
  const [choices, setChoices] = useState<string[]>([]);
  const [rolling, setRolling] = useState(false);
  const [diceResult, setDiceResult] = useState<{d20?: number; hit?: boolean; crit?: boolean; dmg?: number} | null>(null);
  const diceBoxRef = useRef<any>(null);

  useEffect(() => {
    // 客户端动态加载 DiceBox（BabylonJS 需要 window/WebGL）
    import("@3d-dice/dice-box").then(({ default: DiceBox }) => {
      const db = new DiceBox("#dice-box", { assetPath: "/assets/dice-box" });
      db.init();
      diceBoxRef.current = db;
    }).catch(() => console.log("DiceBox 未加载（降级CSS骰子）"));
  }, []);

  async function init() {
    if (campId) return;
    const c = await fetch(`${API}/campaign`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({name: "Next冒险"})}).then(r => r.json());
    setCampId(c.id);
    const ch = await fetch(`${API}/character`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({name: "阿拉贡", char_class: "战士", level: 5, abilities: {str: 16, dex: 10, con: 15, int: 10, wis: 12, cha: 10}, hp_max: 38, ac: 18, campaign_id: c.id})}).then(r => r.json());
    setCharId(ch.id);
    setLog([{c: "dm", t: "角色就绪：阿拉贡 Lv5 战士 HP38/38 AC18。输入世界设定开始。"}]);
  }

  async function open() {
    if (!campId) await init();
    const r = await fetch(`${API}/open`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({setting: inp, campaign_id: campId, character_id: charId})}).then(r => r.json());
    setLog([{c: "dm", t: r.narration}]);
    setChoices(r.action_options || []);
    setInp("");
    refreshScene();
  }

  async function roll() {
    if (!campId) await init();
    if (!inp.trim()) return;
    const action = inp; setInp("");
    setLog(l => [...l, {c: "you", t: "> " + action}]);
    setRolling(true); setDiceResult(null);
    // 3D 骰子动画（视觉）+ 后端判定（权威值）并行
    const [diceVisual, chatRes] = await Promise.all([
      diceBoxRef.current?.roll("1d20").catch(() => null),
      fetch(`${API}/chat`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({player_input: action, campaign_id: campId, character_id: charId, thread_id: "next"})}).then(r => r.json()),
    ]);
    const dd = chatRes.dice || {};
    // 后端 d20 值是权威值（覆盖 3D 动画的随机值）
    setDiceResult({d20: dd.d20, hit: dd.hit, crit: dd.crit, dmg: dd.damage});
    setRolling(false);
    setLog(l => [...l, {c: "dm", t: chatRes.narration || "(无叙事)"}]);
    if (dd.kind) {
      let s = `[骰子] d20=${dd.d20}`;
      if (dd.kind === "attack") s += ` 总${dd.attack_total} vs AC${dd.target_ac} → ${dd.hit ? "✓命中" : "✗未中"}${dd.crit ? " ⚡重击" : ""}${dd.damage != null ? ` 💥${dd.damage}` : ""}`;
      else if (dd.kind === "cast") s += ` 施法DC${dd.spell_save_dc}${dd.damage != null ? ` 💥${dd.damage}` : ""}`;
      else if (dd.kind === "ability_check") s += ` 总${dd.check_total} vs DC${dd.dc} → ${dd.success ? "✓成功" : "✗失败"}`;
      setLog(l => [...l, {c: "dice", t: s}]);
    }
    setChoices(chatRes.action_options || []);
    const c = await fetch(`${API}/character/${charId}`).then(r => r.json());
    setHp(`${c.hp}/${c.hp_max}`);
    refreshScene();
  }

  async function refreshScene() {
    if (!campId) return;
    const s = await fetch(`${API}/scene/${campId}`).then(r => r.json());
    if (s.location) setLog(l => [...l, {c: "meta", t: `📍 ${s.location} | ${s.atmosphere || ""}`}]);
  }

  const hasCamp = campId !== null;
  return (
    <main className="max-w-4xl mx-auto p-6 bg-neutral-900 text-neutral-100 min-h-screen">
      {/* 3D 骰子容器 */}
      <div id="dice-box" style={{position: "fixed", top: 0, left: 0, width: "100%", height: "100%", pointerEvents: "none", zIndex: 50}} />
      {/* 骰子结果覆盖 */}
      {diceResult && (
        <div style={{position: "fixed", top: "30%", left: 0, width: "100%", textAlign: "center", zIndex: 60}}>
          <div style={{fontSize: "3em", fontWeight: "bold",
            color: diceResult.crit ? "#d4af37" : diceResult.hit ? "#4a4" : "#a44",
            textShadow: "0 0 20px currentColor"}}>
            {diceResult.d20}
          </div>
          <div style={{fontSize: "1.2em", color: diceResult.crit ? "#d4af37" : diceResult.hit ? "#4a4" : "#a44"}}>
            {diceResult.crit ? "⚡ 重击!" : diceResult.hit ? "✓ 命中" : "✗ 未中"}
            {diceResult.dmg != null ? `  💥${diceResult.dmg}` : ""}
          </div>
        </div>
      )}
      <h1 className="text-2xl font-bold text-amber-400 border-b border-neutral-700 pb-2">🐉 AI DM — 3D 骰子跑团</h1>
      <p className="text-xs text-neutral-500 mt-2">点击"掷骰"→ 3D物理骰子动画 → 后端硬性d20值揭示 → LLM叙事</p>
      {/* 场景 + 叙事 */}
      <div className="mt-4 bg-neutral-950 border border-neutral-800 rounded-lg p-3 h-[400px] overflow-y-auto text-sm">
        {log.map((e, i) => <div key={i} className={e.c === "you" ? "text-amber-400" : e.c === "dice" ? "text-green-500 text-xs" : e.c === "meta" ? "text-neutral-500 text-xs" : "text-blue-300"}>{e.t}</div>)}
      </div>
      {/* 3 选项 */}
      {choices.length > 0 && (
        <div className="flex gap-2 mt-3 flex-wrap">
          {choices.map((c, i) => (
            <button key={i} className="flex-1 min-w-[120px] px-3 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm text-neutral-300 hover:border-amber-400 hover:bg-neutral-700"
              onClick={() => setInp(c)}>{i+1}. {c}</button>
          ))}
        </div>
      )}
      {/* 输入 + 掷骰按钮 */}
      <div className="flex gap-2 mt-3">
        {!hasCamp ? (
          <>
            <input className="flex-1 px-3 py-2 bg-neutral-800 border border-neutral-700 rounded" value={inp}
              placeholder="输入世界设定..." onChange={e => setInp(e.target.value)}
              onKeyDown={e => e.key === "Enter" && open()} />
            <button className="px-5 py-2 bg-amber-400 text-neutral-900 font-bold rounded hover:bg-amber-300" onClick={open}>开始冒险</button>
          </>
        ) : (
          <>
            <input className="flex-1 px-3 py-2 bg-neutral-800 border border-neutral-700 rounded" value={inp}
              placeholder="输入行动..." onChange={e => setInp(e.target.value)}
              onKeyDown={e => e.key === "Enter" && roll()} />
            <button className="px-5 py-2 bg-amber-400 text-neutral-900 font-bold rounded hover:bg-amber-300 disabled:opacity-40"
              onClick={roll} disabled={rolling}>{rolling ? "🎲 掷骰中..." : "🎲 掷骰"}</button>
          </>
        )}
      </div>
      <p className="text-xs text-neutral-500 mt-2">HP {hp} | 3D骰子=BabylonJS物理 | 值=后端secrets RNG</p>
    </main>
  );
}
