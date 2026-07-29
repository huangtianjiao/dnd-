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
        className="btn btn-secondary w-full"
      >
        🏰 据点系统
      </button>

      {open && (
        <div
          className="modal-overlay visible"
          onClick={() => setOpen(false)}
        >
          <div
            className="modal"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <div className="mh-title">🏰 据点系统</div>
              <button
                onClick={() => setOpen(false)}
                className="modal-close"
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              <div className="flex-col">
                {!created ? (
                  <div className="flex-col" style={{ gap: 6 }}>
                    <div className="text-xs text-muted">
                      DMG第八章 — 角色达到5级时获得据点
                    </div>
                    <label>
                      <span className="form-label">据点名称</span>
                      <input
                        value={strongholdName}
                        onChange={(e) => setStrongholdName(e.target.value)}
                        className="form-input"
                      />
                    </label>
                    <label>
                      <span className="form-label">据点类型</span>
                      <select
                        value={strongholdType}
                        onChange={(e) => setStrongholdType(e.target.value)}
                        className="form-input"
                      >
                        <option value="塔楼">塔楼</option>
                        <option value="城堡">城堡</option>
                        <option value="神殿">神殿</option>
                        <option value="公会会所">公会会所</option>
                        <option value="要塞">要塞</option>
                      </select>
                    </label>
                    <label>
                      <span className="form-label">拥有者等级</span>
                      <input
                        type="number"
                        min={1}
                        max={20}
                        value={ownerLevel}
                        onChange={(e) => setOwnerLevel(Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))}
                        className="form-input"
                      />
                    </label>
                    <button
                      onClick={createStronghold}
                      disabled={busy}
                      className="btn btn-primary w-full"
                    >
                      {busy ? "建立中..." : "🏰 建立据点"}
                    </button>
                  </div>
                ) : (
                  <div className="text-xs text-green">
                    ✓ 据点已建立，可使用据点回合指令
                  </div>
                )}

                {/* 特色设施列表 */}
                {facilities.length > 0 && (
                  <div className="flex-col" style={{ gap: 4, borderTop: "0.5px solid var(--border)", paddingTop: 8, marginTop: 4 }}>
                    <div className="text-xs text-bold text-purple">特色设施</div>
                    {facilities.map((f) => (
                      <div key={f.name} className="text-xs" style={{ border: "0.5px solid var(--border)", borderRadius: "var(--radius-md)", padding: 6 }}>
                        <div className="text-bold text-blue">{f.name} (Lv{f.level})</div>
                        <div className="text-muted">
                          空间: {f.space} · 雇员: {f.hirelings} · 指令: {f.order}
                        </div>
                        {f.description && (
                          <div className="text-muted" style={{ marginTop: 2 }}>{f.description}</div>
                        )}
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
