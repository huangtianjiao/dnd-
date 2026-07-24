"use client";

import { useCallback, useEffect, useState } from "react";
import { apiGet, apiPost, errMsg } from "../lib/api";
import type { RoomInfo, RoomJoinResult } from "../lib/types";

interface RoomPanelProps {
  view: "create" | "list";
  defaultName: string;
  /** 由页面根据当前角色创建配置生成角色字段（race/char_class/level/abilities/hp_max/ac/speed） */
  buildCharacter: (name: string) => Record<string, any>;
  onEntered: (r: RoomJoinResult, isHost: boolean, name: string) => void;
  onBack: () => void;
  toast: (msg: string, type?: string) => void;
}

export function RoomPanel({ view, defaultName, buildCharacter, onEntered, onBack, toast }: RoomPanelProps) {
  // ── 创建房间表单 ──
  const [campaignName, setCampaignName] = useState("");
  const [createPassword, setCreatePassword] = useState("");
  const [maxPlayers, setMaxPlayers] = useState(4);

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

  // ── 创建房间：成功后房主自动以 is_host=true 加入 ──
  const createRoom = useCallback(async () => {
    const nm = name.trim() || "冒险者";
    setBusy(true);
    try {
      const room = await apiPost("/room/create", {
        campaign_name: campaignName.trim() || undefined,
        password: createPassword || undefined,
        max_players: maxPlayers,
      });
      const joined: RoomJoinResult = await apiPost("/room/join", {
        room_id: room.room_id,
        password: createPassword || undefined,
        name: nm,
        is_host: true,
        ...buildCharacter(nm),
      });
      toast(`房间 ${room.room_id} 创建成功`, "success");
      onEntered(joined, true, nm);
    } catch (e) {
      toast("创建房间失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [name, campaignName, createPassword, maxPlayers, buildCharacter, onEntered, toast]);

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
      <main className="min-h-screen flex items-center justify-center bg-neutral-900 text-neutral-100 p-4">
        <div className="w-full max-w-md space-y-4">
          <h2 className="text-2xl font-bold text-amber-400">创建房间</h2>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="角色名..." className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded" />
          <input value={campaignName} onChange={(e) => setCampaignName(e.target.value)} placeholder="战役名（可选）..." className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded" />
          <input value={createPassword} onChange={(e) => setCreatePassword(e.target.value)} type="password" placeholder="房间密码（可选）..." className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded" />
          <label className="block text-xs text-neutral-500 space-y-1">
            <span>人数上限</span>
            <input type="number" min={1} max={8} value={maxPlayers} onChange={(e) => setMaxPlayers(Math.max(1, Math.min(8, parseInt(e.target.value) || 4)))} className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded text-neutral-100" />
          </label>
          <div className="flex gap-2">
            <button onClick={createRoom} disabled={busy} className="flex-1 px-6 py-3 bg-amber-400 text-neutral-900 font-bold rounded hover:bg-amber-300 disabled:opacity-40">
              {busy ? "创建中..." : "🏰 创建并进入"}
            </button>
            <button onClick={onBack} className="px-4 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm">
              ← 返回
            </button>
          </div>
        </div>
      </main>
    );
  }

  // ── 视图：房间列表 + 加入表单 ──
  return (
    <main className="min-h-screen flex items-center justify-center bg-neutral-900 text-neutral-100 p-4">
      <div className="w-full max-w-md space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-amber-400">房间列表</h2>
          <button onClick={loadRooms} className="text-xs px-2 py-1 bg-neutral-800 border border-neutral-700 rounded hover:border-amber-400">
            ⟳ 刷新
          </button>
        </div>

        {listLoading ? (
          <p className="text-neutral-500 text-sm">加载中...</p>
        ) : rooms.length === 0 ? (
          <p className="text-neutral-500 text-sm">暂无开放的房间</p>
        ) : (
          <ul className="space-y-2 max-h-64 overflow-y-auto">
            {rooms.map((r) => (
              <li key={r.room_id}>
                <button
                  onClick={() => {
                    setSelectedRoom(r);
                    setJoinRoomId(r.room_id);
                    setJoinPassword("");
                  }}
                  className={`w-full text-left px-4 py-3 bg-neutral-800 border rounded hover:border-amber-400 ${selectedRoom?.room_id === r.room_id ? "border-amber-400" : "border-neutral-700"}`}
                >
                  <div className="font-bold text-amber-400">
                    {r.has_password ? "🔒 " : ""}{r.campaign_name || `房间 ${r.room_id}`}
                  </div>
                  <div className="text-xs text-neutral-500">
                    #{r.room_id} · {r.player_count ?? "?"}/{r.max_players} 人
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}

        {/* 加入表单 */}
        <div className="border-t border-neutral-800 pt-3 space-y-2">
          <div className="text-sm text-neutral-400">加入房间</div>
          <input value={joinRoomId} onChange={(e) => setJoinRoomId(e.target.value)} placeholder="房间号..." className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded" />
          {(!selectedRoom || selectedRoom.has_password) && (
            <input value={joinPassword} onChange={(e) => setJoinPassword(e.target.value)} type="password" placeholder="密码（无则留空）..." className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded" />
          )}
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="角色名..." className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded" />
          <div className="flex gap-2">
            <button onClick={joinRoom} disabled={busy} className="flex-1 px-6 py-3 bg-amber-400 text-neutral-900 font-bold rounded hover:bg-amber-300 disabled:opacity-40">
              {busy ? "加入中..." : "🚪 加入"}
            </button>
            <button onClick={onBack} className="px-4 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm">
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
  /** 当前玩家名（服务端房主校验用 requester_name） */
  myName: string;
  toast: (msg: string, type?: string) => void;
  /** 转让成功后回调（自己不再是房主） */
  onTransferred?: () => void;
}

export function HostControls({ roomId, myName, toast, onTransferred }: HostControlsProps) {
  const [target, setTarget] = useState("");
  const [busy, setBusy] = useState(false);

  const kick = useCallback(async () => {
    const t = target.trim();
    if (!t) {
      toast("请填写目标玩家名", "warn");
      return;
    }
    setBusy(true);
    try {
      await apiPost(`/room/${roomId}/kick`, { target_name: t, requester_name: myName });
      toast(`已将 ${t} 移出房间`, "success");
      setTarget("");
    } catch (e) {
      toast("踢人失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [roomId, target, myName, toast]);

  const transfer = useCallback(async () => {
    const t = target.trim();
    if (!t) {
      toast("请填写目标玩家名", "warn");
      return;
    }
    setBusy(true);
    try {
      await apiPost(`/room/${roomId}/transfer`, { target_name: t, requester_name: myName });
      toast(`已将房主转让给 ${t}`, "success");
      setTarget("");
      onTransferred?.();
    } catch (e) {
      toast("转让失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [roomId, target, myName, toast, onTransferred]);

  return (
    <div className="border-t border-neutral-800 pt-2 space-y-1.5">
      <div className="text-xs text-amber-400">👑 房主管理 (#{roomId})</div>
      <input
        value={target}
        onChange={(e) => setTarget(e.target.value)}
        placeholder="目标玩家名..."
        className="w-full px-2 py-1 bg-neutral-800 border border-neutral-700 rounded text-xs"
      />
      <div className="flex gap-1">
        <button onClick={kick} disabled={busy} className="flex-1 px-2 py-1 bg-red-900 border border-red-700 rounded text-xs hover:bg-red-800 disabled:opacity-40">
          踢出
        </button>
        <button onClick={transfer} disabled={busy} className="flex-1 px-2 py-1 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400 disabled:opacity-40">
          转让房主
        </button>
      </div>
    </div>
  );
}
