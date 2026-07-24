"use client";

import { useCallback, useState } from "react";
import { apiGet, apiPost, errMsg } from "../lib/api";
import type { AvailableFeats, FeatInfo } from "../lib/types";

interface FeatDialogProps {
  charId: number;
  /** 选择专长成功后回调（刷新角色卡） */
  onSelected: () => void;
  toast: (msg: string, type?: string) => void;
}

/** 专长选择对话框 — 打开时拉取可选专长，可选时列表选择 */
export function FeatDialog({ charId, onSelected, toast }: FeatDialogProps) {
  const [open, setOpen] = useState(false);
  const [data, setData] = useState<AvailableFeats | null>(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  const openDialog = useCallback(async () => {
    setOpen(true);
    setLoading(true);
    setData(null);
    try {
      const d: AvailableFeats = await apiGet(`/character/${charId}/available-feats`);
      setData(d);
    } catch (e) {
      toast("加载可选专长失败: " + errMsg(e), "error");
      setOpen(false);
    } finally {
      setLoading(false);
    }
  }, [charId, toast]);

  const selectFeat = useCallback(
    async (featName: string) => {
      setBusy(true);
      try {
        await apiPost(`/character/${charId}/select-feat`, { feat_name: featName });
        toast(`已习得专长「${featName}」`, "success");
        setOpen(false);
        onSelected();
      } catch (e) {
        toast("选择专长失败: " + errMsg(e), "error");
      } finally {
        setBusy(false);
      }
    },
    [charId, onSelected, toast]
  );

  const featName = (f: FeatInfo | string) => (typeof f === "string" ? f : f.name);
  const featDesc = (f: FeatInfo | string) => (typeof f === "string" ? "" : f.description || "");

  return (
    <>
      <button
        onClick={openDialog}
        className="w-full px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400"
      >
        ⭐ 专长
      </button>

      {open && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setOpen(false)}>
          <div
            className="bg-neutral-900 border border-neutral-700 rounded-lg p-4 w-full max-w-md max-h-[70vh] overflow-y-auto space-y-3"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center">
              <div className="text-sm font-bold text-amber-400">⭐ 专长选择</div>
              <button onClick={() => setOpen(false)} className="text-neutral-500 hover:text-neutral-300">✕</button>
            </div>

            {loading ? (
              <div className="text-xs text-neutral-500">加载中...</div>
            ) : !data ? null : !data.feat_available ? (
              <div className="text-xs text-neutral-400">
                当前等级 {data.level} 暂无可用的专长选择。
                <div className="text-neutral-500 mt-1">达到属性值提升等级（如 4/8/12/16/19 级）后可以选择专长。</div>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="text-xs text-neutral-500">等级 {data.level} · 可选专长 {data.count} 个</div>
                {data.available_feats.map((f, i) => {
                  const name = featName(f);
                  const desc = featDesc(f);
                  return (
                    <div key={`${name}-${i}`} className="border border-neutral-700 rounded p-2">
                      <div
                        className="flex justify-between items-center cursor-pointer"
                        onClick={() => setExpanded(expanded === name ? null : name)}
                      >
                        <span className="text-sm font-bold text-blue-300">{name}</span>
                        <span className="text-neutral-500 text-xs">{expanded === name ? "▼" : "▶"}</span>
                      </div>
                      {expanded === name && desc && (
                        <div className="mt-1 text-xs text-neutral-400">{desc}</div>
                      )}
                      <button
                        onClick={() => selectFeat(name)}
                        disabled={busy}
                        className="mt-2 w-full px-2 py-1 bg-amber-400 text-neutral-900 font-bold rounded text-xs hover:bg-amber-300 disabled:opacity-40"
                      >
                        选择 {name}
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
