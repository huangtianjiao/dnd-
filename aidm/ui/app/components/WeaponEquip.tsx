"use client";

import { useCallback, useState } from "react";
import { apiGet, apiPost, errMsg } from "../lib/api";

interface Weapon {
  name: string;
  category: string;
  damage: string;
  properties: string[];
  weight?: number;
  price?: string;
}

interface WeaponEquipProps {
  characterId: number;
  currentWeapon?: string;
  toast: (msg: string, type?: string) => void;
  onEquipped?: () => void;
}

export function WeaponEquip({ characterId, currentWeapon, toast, onEquipped }: WeaponEquipProps) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [weapons, setWeapons] = useState<Weapon[]>([]);
  const [selected, setSelected] = useState<string>("");

  const openPanel = useCallback(async () => {
    setOpen(true);
    setBusy(true);
    try {
      const data = await apiGet<{ weapons: Weapon[] }>("/weapons");
      setWeapons(data.weapons || []);
      setSelected(currentWeapon || "");
    } catch (e) {
      toast("加载武器列表失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [currentWeapon, toast]);

  const equip = useCallback(async () => {
    if (!selected) {
      toast("请选择武器", "warn");
      return;
    }
    setBusy(true);
    try {
      await apiPost(`/character/${characterId}/equip-weapon`, { weapon_name: selected });
      toast(`已装备 ${selected}`, "success");
      onEquipped?.();
      setOpen(false);
    } catch (e) {
      toast("装备失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [selected, characterId, toast, onEquipped]);

  // 按类别分组
  const categories = Array.from(new Set(weapons.map((w) => w.category)));

  return (
    <>
      <button onClick={openPanel} className="btn btn-secondary w-full">
        🗡️ 装备武器{currentWeapon ? `: ${currentWeapon}` : ""}
      </button>

      {open && (
        <div className="modal-overlay visible" onClick={() => setOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="mh-title">🗡️ 选择武器</div>
              <button onClick={() => setOpen(false)} className="modal-close">
                ✕
              </button>
            </div>

            <div className="modal-body">
              {busy ? (
                <div className="text-sm text-muted">加载中...</div>
              ) : (
                <div className="flex-col">
                  {categories.map((cat) => (
                    <div key={cat} className="flex-col">
                      <div
                        className="text-10 text-muted"
                        style={{ textTransform: "uppercase" }}
                      >
                        {cat}
                      </div>
                      {weapons
                        .filter((w) => w.category === cat)
                        .map((w) => (
                          <label
                            key={w.name}
                            className="flex-row text-sm"
                            style={{
                              alignItems: "center",
                              padding: "4px 8px",
                              borderRadius: "var(--radius-md)",
                              cursor: "pointer",
                              background:
                                selected === w.name
                                  ? "var(--bg-amber)"
                                  : "var(--bg-secondary)",
                              border:
                                selected === w.name
                                  ? "0.5px solid #ef9f27"
                                  : "0.5px solid var(--border)",
                            }}
                          >
                            <input
                              type="radio"
                              name="weapon"
                              value={w.name}
                              checked={selected === w.name}
                              onChange={(e) => setSelected(e.target.value)}
                              style={{ accentColor: "var(--text-amber)" }}
                            />
                            <span className="text-bold text-blue">{w.name}</span>
                            <span className="text-muted">{w.damage}</span>
                            {w.properties.length > 0 && (
                              <span className="text-muted">
                                [{w.properties.join(",")}]
                              </span>
                            )}
                          </label>
                        ))}
                    </div>
                  ))}
                  <button
                    onClick={equip}
                    disabled={busy || !selected}
                    className="btn btn-amber w-full"
                  >
                    {busy ? "装备中..." : "确认装备"}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
