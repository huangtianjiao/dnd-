"use client";

import { useCallback, useEffect, useState } from "react";
import { apiGet, apiPost, apiPostAuth, errMsg } from "../lib/api";
import { getHostToken, setHostToken } from "../hooks/useSocket";
import type { RoomInfo, RoomJoinResult } from "../lib/types";

interface RoomPanelProps {
  view: "create" | "list";
  defaultName: string;
  /** 由页面根据当前角色创建配置生成角色字段（race/char_class/level/abilities/hp_max/ac/speed） */
  buildCharacter: (name: string) => Record<string, any>;
  /** setting 仅房主创建时传入，页面据此调 /open 生成开场 */
  onEntered: (r: RoomJoinResult, isHost: boolean, name: string, setting?: string) => void;
  onBack: () => void;
  toast: (msg: string, type?: string) => void;
}

export function RoomPanel({ view, defaultName, buildCharacter, onEntered, onBack, toast }: RoomPanelProps) {
  // ── 创建房间表单 ──
  const [campaignName, setCampaignName] = useState("");
  const [createPassword, setCreatePassword] = useState("");
  const [maxPlayers, setMaxPlayers] = useState(4);
  const [worldSetting, setWorldSetting] = useState("");
  const [genBusy, setGenBusy] = useState(false);

  // ── 房间列表 / 加入表单 ──
  const [rooms, setRooms] = useState<RoomInfo[]>([]);
  const [listLoading, setListLoading] = useState(false);
  const [selectedRoom, setSelectedRoom] = useState<RoomInfo | null>(null);
  const [joinRoomId, setJoinRoomId] = useState("");
  const [joinPassword, setJoinPassword] = useState("");

  const [name, setName] = useState(defaultName);
  const [busy, setBusy] = useState(false);

  const loadRooms = useCallback(async () => {
    setListLoading(true);
    try {
      const data = await apiGet("/rooms");
      setRooms(data.rooms || []);
    } catch (e) {
      toast("加载房间列表失败: " + errMsg(e), "error");
    } finally {
      setListLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    if (view === "list") loadRooms();
  }, [view, loadRooms]);

  // ── 创建房间：成功后房主凭 /room/create 签发的 host_token 加入（P0-01）──
  const createRoom = useCallback(async () => {
    const nm = name.trim() || "冒险者";
    setBusy(true);
    try {
      const room = await apiPost("/room/create", {
        campaign_name: campaignName.trim() || undefined,
        password: createPassword || undefined,
        max_players: maxPlayers,
      });
      // ★ P0-01: 房主身份只能由服务器签发的 host_token 换取，客户端不再提交 is_host
      setHostToken(room.host_token || "");
      const joined: RoomJoinResult = await apiPost("/room/join", {
        room_id: room.room_id,
        password: createPassword || undefined,
        name: nm,
        host_token: room.host_token,
        ...buildCharacter(nm),
      });
      toast(`房间 ${room.room_id} 创建成功`, "success");
      onEntered(joined, true, nm, worldSetting.trim() || undefined);
    } catch (e) {
      toast("创建房间失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [name, campaignName, createPassword, maxPlayers, worldSetting, buildCharacter, onEntered, toast]);

  /** AI 生成世界设定（与单人新游戏同一端点） */
  const generateSetting = useCallback(async () => {
    setGenBusy(true);
    try {
      const r = await apiPost("/generate_setting", {});
      if (r.setting) setWorldSetting(r.setting);
    } catch (e) {
      toast("生成失败: " + errMsg(e), "error");
    } finally {
      setGenBusy(false);
    }
  }, [toast]);

  // ── 加入房间 ──
  const joinRoom = useCallback(async () => {
    const rid = joinRoomId.trim();
    if (!rid) {
      toast("请填写房间号", "warn");
      return;
    }
    const nm = name.trim() || "冒险者";
    setBusy(true);
    try {
      const joined: RoomJoinResult = await apiPost("/room/join", {
        room_id: rid,
        password: joinPassword || undefined,
        name: nm,
        ...buildCharacter(nm),
      });
      toast(`已加入房间 ${rid}`, "success");
      onEntered(joined, false, nm);
    } catch (e) {
      toast("加入房间失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [joinRoomId, joinPassword, name, buildCharacter, onEntered, toast]);

  // ── 视图：创建房间 ──
  if (view === "create") {
    return (
      <main className="screen">
        <div className="screen-card flex-col">
          <h2 className="title-lg">创建房间</h2>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="角色名..." className="form-input" />
          <input value={campaignName} onChange={(e) => setCampaignName(e.target.value)} placeholder="战役名（可选）..." className="form-input" />
          <input value={createPassword} onChange={(e) => setCreatePassword(e.target.value)} type="password" placeholder="房间密码（可选）..." className="form-input" />
          <label>
            <span className="form-label">人数上限</span>
            <input type="number" min={1} max={8} value={maxPlayers} onChange={(e) => setMaxPlayers(Math.max(1, Math.min(8, parseInt(e.target.value) || 4)))} className="form-input" />
          </label>
          <textarea value={worldSetting} onChange={(e) => setWorldSetting(e.target.value)} rows={4}
            placeholder="世界设定（可选：填写后建房即生成 DM 开场叙事）..." className="form-input" style={{ resize: "none" }} />
          <button onClick={generateSetting} disabled={genBusy} className="btn btn-secondary">
            {genBusy ? "生成中..." : "✨ AI 生成世界设定"}
          </button>
          <div className="flex-row">
            <button onClick={createRoom} disabled={busy} className="btn btn-primary" style={{ flex: 1 }}>
              {busy ? "创建中..." : "🏰 创建并进入"}
            </button>
            <button onClick={onBack} className="btn btn-secondary">
              ← 返回
            </button>
          </div>
        </div>
      </main>
    );
  }

  // ── 视图：房间列表 + 加入表单 ──
  return (
    <main className="screen">
      <div className="screen-card flex-col">
        <div className="flex-between mb-2">
          <h2 className="title-lg" style={{ margin: 0 }}>房间列表</h2>
          <button onClick={loadRooms} className="btn btn-secondary text-xs">
            ⟳ 刷新
          </button>
        </div>

        {listLoading ? (
          <p className="text-sm text-muted">加载中...</p>
        ) : rooms.length === 0 ? (
          <p className="text-sm text-muted">暂无开放的房间</p>
        ) : (
          <ul className="flex-col" style={{ gap: 4, maxHeight: 256, overflowY: "auto" }}>
            {rooms.map((r) => (
              <li key={r.room_id}>
                <button
                  onClick={() => {
                    setSelectedRoom(r);
                    setJoinRoomId(r.room_id);
                    setJoinPassword("");
                  }}
                  className="w-full"
                  style={{
                    textAlign: "left",
                    padding: "12px 16px",
                    borderRadius: "var(--radius-md)",
                    border: selectedRoom?.room_id === r.room_id ? "1px solid var(--text-purple)" : "0.5px solid var(--border)",
                    background: selectedRoom?.room_id === r.room_id ? "var(--bg-purple)" : "var(--bg-secondary)",
                  }}
                >
                  <div className="text-bold text-purple">
                    {r.has_password ? "🔒 " : ""}{r.campaign_name || `房间 ${r.room_id}`}
                  </div>
                  <div className="text-xs text-muted">
                    #{r.room_id} · {r.player_count ?? "?"}/{r.max_players} 人
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}

        {/* 加入表单 */}
        <div className="flex-col" style={{ gap: 6, borderTop: "0.5px solid var(--border)", paddingTop: 12, marginTop: 4 }}>
          <div className="text-sm text-bold">加入房间</div>
          <input value={joinRoomId} onChange={(e) => setJoinRoomId(e.target.value)} placeholder="房间号..." className="form-input" />
          {(!selectedRoom || selectedRoom.has_password) && (
            <input value={joinPassword} onChange={(e) => setJoinPassword(e.target.value)} type="password" placeholder="密码（无则留空）..." className="form-input" />
          )}
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="角色名..." className="form-input" />
          <div className="flex-row">
            <button onClick={joinRoom} disabled={busy} className="btn btn-primary" style={{ flex: 1 }}>
              {busy ? "加入中..." : "🚪 加入"}
            </button>
            <button onClick={onBack} className="btn btn-secondary">
              ← 返回
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}

// ──────────────────────────────────────────────────────────────────────────
// 房主管理入口（游戏内，is_host 时展示）
// ──────────────────────────────────────────────────────────────────────────

interface HostControlsProps {
  roomId: string;
  /** 按 character_id 定位目标（来自队伍条 PartyMember） */
  players: { characterId: number; name: string }[];
  toast: (msg: string, type?: string) => void;
  /** 转让成功后回调（自己不再是房主） */
  onTransferred?: () => void;
}

export function HostControls({ roomId, players, toast, onTransferred }: HostControlsProps) {
  const [target, setTarget] = useState("");
  const [busy, setBusy] = useState(false);
  // ★ P0-01/P0-02: 房主令牌模块级持有（/room/create 签发），Bearer 鉴权
  const hostToken = getHostToken();

  const targetCharId = (nm: string) => players.find((p) => p.name.trim() === nm.trim())?.characterId;

  const kick = useCallback(async () => {
    const t = target.trim();
    if (!t) {
      toast("请填写目标玩家名", "warn");
      return;
    }
    const cid = targetCharId(t);
    if (!cid) {
      toast("目标玩家不在房间内", "warn");
      return;
    }
    setBusy(true);
    try {
      // ★ P0-02: 房主身份来自 Bearer 令牌，目标按 character_id 定位（防名字冒充）
      await apiPostAuth(`/room/${roomId}/kick`, { target_character_id: cid }, hostToken);
      toast(`已将 ${t} 移出房间`, "success");
      setTarget("");
    } catch (e) {
      toast("踢人失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [roomId, target, hostToken, players, toast]);

  const transfer = useCallback(async () => {
    const t = target.trim();
    if (!t) {
      toast("请填写目标玩家名", "warn");
      return;
    }
    const cid = targetCharId(t);
    if (!cid) {
      toast("目标玩家不在房间内", "warn");
      return;
    }
    setBusy(true);
    try {
      await apiPostAuth(`/room/${roomId}/transfer`, { target_character_id: cid }, hostToken);
      toast(`已将房主转让给 ${t}`, "success");
      setTarget("");
      onTransferred?.();
    } catch (e) {
      toast("转让失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [roomId, target, hostToken, players, toast, onTransferred]);

  return (
    <div className="flex-col" style={{ gap: 6, borderTop: "0.5px solid var(--border)", paddingTop: 8, marginTop: 4 }}>
      <div className="text-xs text-amber text-bold">👑 房主管理 (#{roomId})</div>
      <input
        value={target}
        onChange={(e) => setTarget(e.target.value)}
        placeholder="目标玩家名..."
        className="form-input"
        style={{ fontSize: 11, padding: "4px 8px" }}
      />
      <div className="flex-row" style={{ gap: 4 }}>
        <button
          onClick={kick}
          disabled={busy}
          className="btn btn-secondary"
          style={{ flex: 1, background: "var(--bg-red)", color: "var(--text-red)", borderColor: "#f09595", fontSize: 11, padding: "4px 8px" }}
        >
          踢出
        </button>
        <button
          onClick={transfer}
          disabled={busy}
          className="btn btn-secondary"
          style={{ flex: 1, fontSize: 11, padding: "4px 8px" }}
        >
          转让房主
        </button>
      </div>
    </div>
  );
}
