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
  common: "text-muted",
  uncommon: "text-green",
  rare: "text-blue",
  very_rare: "text-purple",
  legendary: "text-amber",
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
        className="btn btn-secondary w-full"
      >
        💰 战利品
      </button>

      {open && (
        <div className="modal-overlay visible" onClick={() => setOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="mh-title">💰 战利品分配</div>
              <button onClick={() => setOpen(false)} className="modal-close">✕</button>
            </div>

            <div className="modal-body">
              <div className="flex-col">
                {/* 生成战利品池 */}
                <div className="flex-col" style={{ gap: 4 }}>
                  <div className="form-label">怪物 CR（逗号分隔，如 1, 0.5, 3）</div>
                  <div className="flex-row">
                    <input
                      value={crInput}
                      onChange={(e) => setCrInput(e.target.value)}
                      placeholder="1, 0.5, 3"
                      className="form-input"
                      style={{ flex: 1 }}
                    />
                    <button onClick={generatePool} disabled={busy} className="btn btn-primary">
                      {busy && !pool ? "生成中..." : "生成"}
                    </button>
                  </div>
                </div>

                {/* 战利品池展示 */}
                {pool && (
                  <div style={{ border: "0.5px solid var(--border)", borderRadius: "var(--radius-md)", padding: 8, display: "flex", flexDirection: "column", gap: 2 }}>
                    <div className="text-sm text-amber text-bold">🪙 金币: {pool.gold} gp</div>
                    {pool.items.length === 0 ? (
                      <div className="text-xs text-muted">无物品掉落</div>
                    ) : (
                      pool.items.map((it) => (
                        <div key={it.item_id} className="text-xs flex-between">
                          <div>
                            <span className={RARITY_COLOR[it.rarity] || "text-muted"}>{it.name}</span>
                            <span className="text-muted" style={{ marginLeft: 4 }}>×{it.quantity} · {it.type} · {it.value_gp}gp</span>
                          </div>
                          {mode === "DM_ASSIGN" && (
                            <select
                              value={assignments[it.item_id] || ""}
                              onChange={(e) => setAssignments({ ...assignments, [it.item_id]: e.target.value })}
                              className="form-input"
                              style={{ width: "auto", fontSize: 10, padding: "2px 6px" }}
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
                  <div className="flex-col" style={{ gap: 6 }}>
                    <label>
                      <span className="form-label">分配模式</span>
                      <select value={mode} onChange={(e) => setMode(e.target.value as LootMode)} className="form-input">
                        {MODES.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
                      </select>
                    </label>
                    <label>
                      <span className="form-label">参与玩家（逗号分隔）</span>
                      <input value={playersInput} onChange={(e) => setPlayersInput(e.target.value)} className="form-input" />
                    </label>
                    <button onClick={distribute} disabled={busy} className="btn btn-primary w-full">
                      {busy ? "分配中..." : "⚖️ 执行分配"}
                    </button>
                  </div>
                )}

                {/* 分配结果 */}
                {result && (
                  <div style={{ border: "0.5px solid var(--border)", borderRadius: "var(--radius-md)", padding: 8, display: "flex", flexDirection: "column", gap: 2 }}>
                    <div className="text-sm text-green text-bold">✅ 分配结果（{result.mode}）</div>
                    {result.gold_distribution && Object.entries(result.gold_distribution).map(([p, g]) => (
                      <div key={p} className="text-xs">🪙 {p}: {g} gp</div>
                    ))}
                    {result.item_distribution && Object.entries(result.item_distribution).map(([p, items]) => (
                      <div key={p} className="text-xs">
                        🎁 {p}: {Array.isArray(items)
                          ? items.map((it: any) => (typeof it === "string" ? it : it.name)).join(", ") || "(无)"
                          : String(items)}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
