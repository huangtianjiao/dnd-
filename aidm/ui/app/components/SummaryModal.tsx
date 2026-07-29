"use client";

import { useState, useCallback } from "react";
import { apiGet, errMsg } from "../lib/api";

interface SummaryModalProps {
  campaignId: number;
  onClose: () => void;
}

export function SummaryModal({ campaignId, onClose }: SummaryModalProps) {
  const [summary, setSummary] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await apiGet<{ summary: string }>(`/summary/${campaignId}`);
      setSummary(r.summary || "(无摘要)");
    } catch (e) {
      setSummary("加载失败: " + errMsg(e));
    } finally {
      setLoading(false);
    }
  }, [campaignId]);

  // 首次打开时加载
  if (loading && summary === null) {
    load();
  }

  return (
    <div className="modal-overlay visible" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="mh-title">📖 剧情回顾</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {loading ? (
            <div className="text-muted">加载中...</div>
          ) : (
            <div style={{
              whiteSpace: "pre-wrap",
              fontSize: 13,
              lineHeight: 1.7,
              color: "var(--text-primary)",
              fontFamily: "var(--font-serif)",
              maxHeight: "60vh",
              overflowY: "auto",
            }}>
              {summary}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
