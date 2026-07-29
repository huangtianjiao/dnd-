"use client";

import { useState, useCallback } from "react";
import { apiGet, errMsg } from "../lib/api";

interface RoomInfoModalProps {
  roomId: string;
  onClose: () => void;
}

export function RoomInfoModal({ roomId, onClose }: RoomInfoModalProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await apiGet(`/room/${encodeURIComponent(roomId)}`);
      setData(r);
    } catch (e) {
      setData({ error: errMsg(e) });
    } finally {
      setLoading(false);
    }
  }, [roomId]);

  if (loading && data === null) {
    load();
  }

  return (
    <div className="modal-overlay visible" onClick={onClose}>
      <div className="modal" style={{ maxWidth: 400 }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="mh-title">🏠 房间状态</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {loading ? (
            <div className="text-muted">加载中...</div>
          ) : data?.error ? (
            <div className="text-red">{data.error}</div>
          ) : data ? (
            <div className="flex-col" style={{ gap: 8 }}>
              <div className="flex-between">
                <span className="text-xs text-muted">房间号</span>
                <span className="text-sm text-bold">{data.room_id || roomId}</span>
              </div>
              {data.campaign_name && (
                <div className="flex-between">
                  <span className="text-xs text-muted">战役</span>
                  <span className="text-sm">{data.campaign_name}</span>
                </div>
              )}
              <div className="flex-between">
                <span className="text-xs text-muted">人数</span>
                <span className="text-sm">{data.player_count ?? (data.players?.length ?? 0)}/{data.max_players ?? "?"}</span>
              </div>
              {data.has_password !== undefined && (
                <div className="flex-between">
                  <span className="text-xs text-muted">密码</span>
                  <span className="text-sm">{data.has_password ? "🔒 有" : "无"}</span>
                </div>
              )}
              {data.host && (
                <div className="flex-between">
                  <span className="text-xs text-muted">房主</span>
                  <span className="text-sm text-purple">{data.host} 👑</span>
                </div>
              )}
              {data.players && Array.isArray(data.players) && data.players.length > 0 && (
                <div>
                  <div className="text-xs text-muted mb-2">在线玩家</div>
                  <div className="flex-col" style={{ gap: 4 }}>
                    {data.players.map((p: any, i: number) => (
                      <div key={i} className="flex-between" style={{
                        padding: "4px 8px",
                        background: "var(--bg-secondary)",
                        borderRadius: "var(--radius-md)",
                      }}>
                        <span className="text-sm">{typeof p === "string" ? p : p.name}</span>
                        {typeof p === "object" && p.is_dm && <span className="text-xs text-purple">DM</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
