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
      <button
        onClick={openPanel}
        className="w-full px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400"
      >
        🗡️ 装备武器{currentWeapon ? `: ${currentWeapon}` : ""}
      </button>

      {open && (
        <div
          className="fixed inset-0 bg-black/60 flex items-center justify-center z-50"
          onClick={() => setOpen(false)}
        >
          <div
            className="bg-neutral-900 border border-neutral-700 rounded-lg p-4 w-full max-w-md max-h-[70vh] overflow-y-auto space-y-3"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center">
              <div className="text-sm font-bold text-amber-400">🗡️ 选择武器</div>
              <button
                onClick={() => setOpen(false)}
                className="text-neutral-500 hover:text-neutral-300"
              >
                ✕
              </button>
            </div>

            {busy ? (
              <div className="text-xs text-neutral-500">加载中...</div>
            ) : (
              <>
                {categories.map((cat) => (
                  <div key={cat} className="space-y-1">
                    <div className="text-[10px] text-neutral-500 uppercase">{cat}</div>
                    {weapons
                      .filter((w) => w.category === cat)
                      .map((w) => (
                        <label
                          key={w.name}
                          className={`flex items-center gap-2 text-xs px-2 py-1 rounded cursor-pointer ${
                            selected === w.name
                              ? "bg-amber-900/50 border border-amber-600"
                              : "bg-neutral-800/50 border border-neutral-700"
                          }`}
                        >
                          <input
                            type="radio"
                            name="weapon"
                            value={w.name}
                            checked={selected === w.name}
                            onChange={(e) => setSelected(e.target.value)}
                            className="accent-amber-400"
                          />
                          <span className="font-bold text-blue-300">{w.name}</span>
                          <span className="text-neutral-500">{w.damage}</span>
                          {w.properties.length > 0 && (
                            <span className="text-neutral-600">[{w.properties.join(",")}]</span>
                          )}
                        </label>
                      ))}
                  </div>
                ))}
                <button
                  onClick={equip}
                  disabled={busy || !selected}
                  className="w-full px-4 py-2 bg-amber-400 text-neutral-900 font-bold rounded text-sm hover:bg-amber-300 disabled:opacity-40"
                >
                  {busy ? "装备中..." : "确认装备"}
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
