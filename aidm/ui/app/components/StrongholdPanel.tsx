"use client";

import { useCallback, useState } from "react";
import { apiGet, apiPost, errMsg } from "../lib/api";

interface Facility {
  name: string;
  name_en?: string;
  level: number;
  space: string;
  hirelings: number;
  order: string;
  prerequisite?: string;
  description?: string;
  effects?: string[];
  can_enlarge?: boolean;
  multiple_allowed?: boolean;
}

interface StrongholdPanelProps {
  campaignId: number;
  characterId: number;
  toast: (msg: string, type?: string) => void;
}

export function StrongholdPanel({ campaignId, characterId, toast }: StrongholdPanelProps) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [strongholdName, setStrongholdName] = useState("我的据点");
  const [strongholdType, setStrongholdType] = useState("塔楼");
  const [ownerLevel, setOwnerLevel] = useState(5);
  const [created, setCreated] = useState(false);

  const openPanel = useCallback(async () => {
    setOpen(true);
    setBusy(true);
    try {
      const data = await apiGet<{ facilities: Facility[] }>("/strongholds/facilities");
      setFacilities(data.facilities || []);
    } catch (e) {
      toast("加载据点设施失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [toast]);

  const createStronghold = useCallback(async () => {
    setBusy(true);
    try {
      await apiPost("/stronghold/create", {
        campaign_id: campaignId,
        owner_character_id: characterId,
        owner_name: String(characterId),
        owner_level: ownerLevel,
        name: strongholdName,
        stronghold_type: strongholdType,
        initial_gold: 0.0,
      });
      toast(`据点「${strongholdName}」已建立`, "success");
      setCreated(true);
    } catch (e) {
      toast("建立据点失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [campaignId, characterId, strongholdName, strongholdType, ownerLevel, toast]);

  return (
    <>
      <button
        onClick={openPanel}
        className="w-full px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400"
      >
        🏰 据点系统
      </button>

      {open && (
        <div
          className="fixed inset-0 bg-black/60 flex items-center justify-center z-50"
          onClick={() => setOpen(false)}
        >
          <div
            className="bg-neutral-900 border border-neutral-700 rounded-lg p-4 w-full max-w-md max-h-[80vh] overflow-y-auto space-y-3"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center">
              <div className="text-sm font-bold text-amber-400">🏰 据点系统</div>
              <button
                onClick={() => setOpen(false)}
                className="text-neutral-500 hover:text-neutral-300"
              >
                ✕
              </button>
            </div>

            {!created ? (
              <div className="space-y-2">
                <div className="text-xs text-neutral-500">
                  DMG第八章 — 角色达到5级时获得据点
                </div>
                <label className="block text-xs text-neutral-500 space-y-1">
                  <span>据点名称</span>
                  <input
                    value={strongholdName}
                    onChange={(e) => setStrongholdName(e.target.value)}
                    className="w-full px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-sm"
                  />
                </label>
                <label className="block text-xs text-neutral-500 space-y-1">
                  <span>据点类型</span>
                  <select
                    value={strongholdType}
                    onChange={(e) => setStrongholdType(e.target.value)}
                    className="w-full px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-sm"
                  >
                    <option value="塔楼">塔楼</option>
                    <option value="城堡">城堡</option>
                    <option value="神殿">神殿</option>
                    <option value="公会会所">公会会所</option>
                    <option value="要塞">要塞</option>
                  </select>
                </label>
                <label className="block text-xs text-neutral-500 space-y-1">
                  <span>拥有者等级</span>
                  <input
                    type="number"
                    min={1}
                    max={20}
                    value={ownerLevel}
                    onChange={(e) => setOwnerLevel(Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))}
                    className="w-full px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-sm"
                  />
                </label>
                <button
                  onClick={createStronghold}
                  disabled={busy}
                  className="w-full px-4 py-2 bg-amber-400 text-neutral-900 font-bold rounded text-sm hover:bg-amber-300 disabled:opacity-40"
                >
                  {busy ? "建立中..." : "🏰 建立据点"}
                </button>
              </div>
            ) : (
              <div className="text-xs text-green-400">
                ✓ 据点已建立，可使用据点回合指令
              </div>
            )}

            {/* 特色设施列表 */}
            {facilities.length > 0 && (
              <div className="border-t border-neutral-800 pt-2 space-y-1">
                <div className="text-xs font-bold text-neutral-400">特色设施</div>
                {facilities.map((f) => (
                  <div key={f.name} className="text-xs border border-neutral-700 rounded p-1.5">
                    <div className="font-bold text-blue-300">{f.name} (Lv{f.level})</div>
                    <div className="text-neutral-500">
                      空间: {f.space} · 雇员: {f.hirelings} · 指令: {f.order}
                    </div>
                    {f.description && (
                      <div className="text-neutral-600 mt-0.5">{f.description}</div>
                    )}
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
