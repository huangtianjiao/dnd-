"use client";

import { useState, useCallback } from "react";
import { apiGet, errMsg } from "../lib/api";

interface MonsterInfoModalProps {
  monsterName: string;
  onClose: () => void;
}

export function MonsterInfoModal({ monsterName, onClose }: MonsterInfoModalProps) {
  const [data, setData] = useState<{ name: string; body: string; tag: string; path: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await apiGet(`/monster/${encodeURIComponent(monsterName)}`);
      setData(r);
    } catch (e) {
      setError(errMsg(e));
    } finally {
      setLoading(false);
    }
  }, [monsterName]);

  if (loading && data === null && error === null) {
    load();
  }

  return (
    <div className="modal-overlay visible" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="mh-title">👾 {monsterName}</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {loading ? (
            <div className="text-muted">检索怪物数据中...</div>
          ) : error ? (
            <div className="text-red">{error}</div>
          ) : data ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {data.tag && (
                <div className="text-xs text-muted">类型: {data.tag}</div>
              )}
              <div style={{
                whiteSpace: "pre-wrap",
                fontSize: 12,
                lineHeight: 1.6,
                color: "var(--text-secondary)",
                maxHeight: "50vh",
                overflowY: "auto",
              }}>
                {data.body}
              </div>
            </div>
          ) : (
            <div className="text-muted">未找到怪物数据</div>
          )}
        </div>
      </div>
    </div>
  );
}
