"use client";

import { useCallback, useState } from "react";
import { apiPost, errMsg } from "../lib/api";
import type { LootDistribution, LootMode, LootPool } from "../lib/types";

interface LootPanelProps {
  campaignId: number;
  /** 默认参与分配的玩家名（当前队伍） */
  partyNames: string[];
  toast: (msg: string, type?: string) => void;
}

const MODES: { value: LootMode; label: string }[] = [
  { value: "NEED_FIRST", label: "需求优先 (Need First)" },
  { value: "ROUND_ROBIN", label: "轮流拾取 (Round Robin)" },
  { value: "ROLL_OFF", label: "掷骰竞拍 (Roll Off)" },
  { value: "DM_ASSIGN", label: "DM 指定 (DM Assign)" },
];

const RARITY_COLOR: Record<string, string> = {
  common: "text-neutral-300",
  uncommon: "text-green-400",
  rare: "text-blue-400",
  very_rare: "text-purple-400",
  legendary: "text-amber-400",
};

/** 战利品面板 — 生成战利品池 + 分配 */
export function LootPanel({ campaignId, partyNames, toast }: LootPanelProps) {
  const [open, setOpen] = useState(false);
  const [crInput, setCrInput] = useState("");
  const [pool, setPool] = useState<LootPool | null>(null);
  const [mode, setMode] = useState<LootMode>("NEED_FIRST");
  const [playersInput, setPlayersInput] = useState(partyNames.join(", "));
  const [assignments, setAssignments] = useState<Record<string, string>>({});
  const [result, setResult] = useState<LootDistribution | null>(null);
  const [busy, setBusy] = useState(false);

  const openPanel = useCallback(() => {
    setOpen(true);
    if (!playersInput.trim() && partyNames.length > 0) setPlayersInput(partyNames.join(", "));
  }, [playersInput, partyNames]);

  // ── 生成战利品池 ──
  const generatePool = useCallback(async () => {
    // CR 解析健壮化（E2E B2）：全角数字/句号转半角，支持空格/中英文逗号/顿号分隔
    const normalized = crInput
      .replace(/[０-９]/g, (ch) => String.fromCharCode(ch.charCodeAt(0) - 0xfee0))
      .replace(/[．。]/g, ".");
    const tokens = normalized.split(/[\s,，、;；]+/).map((s) => s.trim()).filter(Boolean);
    const crs = tokens.map((s) => parseFloat(s)).filter((n) => !isNaN(n) && n >= 0);
    if (crs.length === 0) {
      toast("CR 解析失败，请输入数字（逗号/空格分隔，如 1, 0.5, 3）", "warn");
      return;
    }
    if (crs.length < tokens.length) {
      toast(`部分 CR 无法解析已忽略，实际使用: ${crs.join(", ")}`, "warn");
    }
    setBusy(true);
    setResult(null);
    try {
      const p: LootPool = await apiPost("/loot/pool", { campaign_id: campaignId, monster_crs: crs });
      setPool(p);
      setAssignments({});
      toast(`战利品已生成: ${p.gold} gp、${p.items.length} 件物品`, "success");
    } catch (e) {
      toast("生成战利品失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [crInput, campaignId, toast]);

  // ── 分配 ──
  const distribute = useCallback(async () => {
    if (!pool) return;
    const players = playersInput
      .split(/[,，]/)
      .map((s) => s.trim())
      .filter(Boolean);
    if (players.length === 0) {
      toast("请填写至少一名玩家", "warn");
      return;
    }
    setBusy(true);
    try {
      const body: Record<string, any> = {
        campaign_id: campaignId,
        gold: pool.gold,
        items: pool.items,
        player_names: players,
        mode,
      };
      if (mode === "DM_ASSIGN") body.dm_assignments = assignments;
      const r: LootDistribution = await apiPost("/loot/distribute/v2", body);
      setResult(r);
      toast("分配完成", "success");
    } catch (e) {
      toast("分配失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [pool, playersInput, mode, assignments, campaignId, toast]);

  const players = playersInput.split(/[,，]/).map((s) => s.trim()).filter(Boolean);

  return (
    <>
      <button
        onClick={openPanel}
        className="w-full px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400"
      >
        💰 战利品
      </button>

      {open && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setOpen(false)}>
          <div
            className="bg-neutral-900 border border-neutral-700 rounded-lg p-4 w-full max-w-lg max-h-[80vh] overflow-y-auto space-y-3"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center">
              <div className="text-sm font-bold text-amber-400">💰 战利品分配</div>
              <button onClick={() => setOpen(false)} className="text-neutral-500 hover:text-neutral-300">✕</button>
            </div>

            {/* 生成战利品池 */}
            <div className="space-y-2">
              <div className="text-xs text-neutral-500">怪物 CR（逗号分隔，如 1, 0.5, 3）</div>
              <div className="flex gap-2">
                <input
                  value={crInput}
                  onChange={(e) => setCrInput(e.target.value)}
                  placeholder="1, 0.5, 3"
                  className="flex-1 px-3 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm"
                />
                <button onClick={generatePool} disabled={busy} className="px-4 py-2 bg-amber-400 text-neutral-900 font-bold rounded text-sm hover:bg-amber-300 disabled:opacity-40">
                  {busy && !pool ? "生成中..." : "生成"}
                </button>
              </div>
            </div>

            {/* 战利品池展示 */}
            {pool && (
              <div className="border border-neutral-700 rounded p-2 space-y-1">
                <div className="text-xs text-amber-400 font-bold">🪙 金币: {pool.gold} gp</div>
                {pool.items.length === 0 ? (
                  <div className="text-xs text-neutral-500">无物品掉落</div>
                ) : (
                  pool.items.map((it) => (
                    <div key={it.item_id} className="text-xs flex items-center justify-between gap-2">
                      <div>
                        <span className={RARITY_COLOR[it.rarity] || "text-neutral-300"}>{it.name}</span>
                        <span className="text-neutral-500 ml-1">×{it.quantity} · {it.type} · {it.value_gp}gp</span>
                      </div>
                      {mode === "DM_ASSIGN" && (
                        <select
                          value={assignments[it.item_id] || ""}
                          onChange={(e) => setAssignments({ ...assignments, [it.item_id]: e.target.value })}
                          className="px-1 py-0.5 bg-neutral-800 border border-neutral-700 rounded text-[10px]"
                        >
                          <option value="">未指定</option>
                          {players.map((p) => <option key={p} value={p}>{p}</option>)}
                        </select>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {/* 分配设置 */}
            {pool && (
              <div className="space-y-2">
                <label className="block text-xs text-neutral-500 space-y-1">
                  <span>分配模式</span>
                  <select value={mode} onChange={(e) => setMode(e.target.value as LootMode)} className="w-full px-2 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm text-neutral-100">
                    {MODES.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
                  </select>
                </label>
                <label className="block text-xs text-neutral-500 space-y-1">
                  <span>参与玩家（逗号分隔）</span>
                  <input value={playersInput} onChange={(e) => setPlayersInput(e.target.value)} className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm text-neutral-100" />
                </label>
                <button onClick={distribute} disabled={busy} className="w-full px-4 py-2 bg-amber-400 text-neutral-900 font-bold rounded text-sm hover:bg-amber-300 disabled:opacity-40">
                  {busy ? "分配中..." : "⚖️ 执行分配"}
                </button>
              </div>
            )}

            {/* 分配结果 */}
            {result && (
              <div className="border border-neutral-700 rounded p-2 space-y-1">
                <div className="text-xs font-bold text-green-400">✅ 分配结果（{result.mode}）</div>
                {result.gold_distribution && Object.entries(result.gold_distribution).map(([p, g]) => (
                  <div key={p} className="text-xs text-neutral-300">🪙 {p}: {g} gp</div>
                ))}
                {result.item_distribution && Object.entries(result.item_distribution).map(([p, items]) => (
                  <div key={p} className="text-xs text-neutral-300">
                    🎁 {p}: {Array.isArray(items)
                      ? items.map((it: any) => (typeof it === "string" ? it : it.name)).join(", ") || "(无)"
                      : String(items)}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
