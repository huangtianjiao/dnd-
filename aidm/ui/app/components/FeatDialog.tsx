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
      <button onClick={openDialog} className="btn btn-secondary w-full">
        ⭐ 专长
      </button>

      {open && (
        <div className="modal-overlay visible" onClick={() => setOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="mh-title">⭐ 专长选择</div>
              <button onClick={() => setOpen(false)} className="modal-close">
                ✕
              </button>
            </div>

            <div className="modal-body">
              {loading ? (
                <div className="text-sm text-muted">加载中...</div>
              ) : !data ? null : !data.feat_available ? (
                <div className="text-sm text-muted">
                  当前等级 {data.level} 暂无可用的专长选择。
                  <div className="text-sm text-muted mt-2">
                    达到属性值提升等级（如 4/8/12/16/19 级）后可以选择专长。
                  </div>
                </div>
              ) : (
                <div className="flex-col">
                  <div className="text-sm text-muted">
                    等级 {data.level} · 可选专长 {data.count} 个
                  </div>
                  {data.available_feats.map((f, i) => {
                    const name = featName(f);
                    const desc = featDesc(f);
                    return (
                      <div
                        key={`${name}-${i}`}
                        className="flex-col"
                        style={{
                          border: "0.5px solid var(--border)",
                          borderRadius: "var(--radius-md)",
                          background: "var(--bg-secondary)",
                          padding: "10px 12px",
                        }}
                      >
                        <div
                          className="flex-between"
                          style={{ cursor: "pointer" }}
                          onClick={() => setExpanded(expanded === name ? null : name)}
                        >
                          <span className="text-bold text-blue">{name}</span>
                          <span className="text-xs text-muted">
                            {expanded === name ? "▼" : "▶"}
                          </span>
                        </div>
                        {expanded === name && desc && (
                          <div className="text-xs text-muted">{desc}</div>
                        )}
                        <button
                          onClick={() => selectFeat(name)}
                          disabled={busy}
                          className="btn btn-amber w-full mt-2"
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
        </div>
      )}
    </>
  );
}
