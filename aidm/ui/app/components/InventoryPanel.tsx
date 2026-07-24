"use client";

import { useCallback, useState } from "react";
import { apiGet, apiPost, errMsg } from "../lib/api";

interface MagicItemDetail {
  name: string;
  name_en?: string;
  rarity: string;
  item_type: string;
  value_gp?: number;
  description?: string;
  attuned?: boolean;
  requires_attunement?: boolean;
}

interface InventoryPanelProps {
  characterId: number;
  toast: (msg: string, type?: string) => void;
  onUpdated?: () => void;
}

export function InventoryPanel({ characterId, toast, onUpdated }: InventoryPanelProps) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [inventory, setInventory] = useState<string[]>([]);
  const [attunedItems, setAttunedItems] = useState<string[]>([]);
  const [magicItems, setMagicItems] = useState<MagicItemDetail[]>([]);

  const loadInventory = useCallback(async () => {
    setBusy(true);
    try {
      const data = await apiGet<{
        inventory: string[];
        attuned_items: string[];
        magic_items: MagicItemDetail[];
        gold: number;
      }>(`/character/${characterId}/inventory`);
      setInventory(data.inventory || []);
      setAttunedItems(data.attuned_items || []);
      setMagicItems(data.magic_items || []);
    } catch (e) {
      toast("加载物品栏失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [characterId, toast]);

  const openPanel = useCallback(() => {
    setOpen(true);
    loadInventory();
  }, [loadInventory]);

  const attune = useCallback(async (itemName: string) => {
    setBusy(true);
    try {
      await apiPost(`/character/${characterId}/attune`, { item_name: itemName });
      toast(`已同调 ${itemName}`, "success");
      await loadInventory();
      onUpdated?.();
    } catch (e) {
      toast("同调失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [characterId, toast, loadInventory, onUpdated]);

  const breakAttunement = useCallback(async (itemName: string) => {
    setBusy(true);
    try {
      await apiPost(`/character/${characterId}/break-attunement`, { item_name: itemName });
      toast(`已解除同调 ${itemName}`, "success");
      await loadInventory();
      onUpdated?.();
    } catch (e) {
      toast("解除同调失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [characterId, toast, loadInventory, onUpdated]);

  return (
    <>
      <button
        onClick={openPanel}
        className="w-full px-2 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-xs hover:border-amber-400"
      >
        🎒 物品栏
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
              <div className="text-sm font-bold text-amber-400">🎒 物品栏</div>
              <button
                onClick={() => setOpen(false)}
                className="text-neutral-500 hover:text-neutral-300"
              >
                ✕
              </button>
            </div>

            {busy ? (
              <div className="text-xs text-neutral-500">加载中...</div>
            ) : magicItems.length === 0 ? (
              <div className="text-xs text-neutral-500">物品栏为空</div>
            ) : (
              <div className="space-y-2">
                {magicItems.map((item) => {
                  const isAttuned = attunedItems.includes(item.name);
                  return (
                    <div
                      key={item.name}
                      className="border border-neutral-700 rounded p-2 space-y-1"
                    >
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-bold text-blue-300">
                          {item.name}
                        </span>
                        <span className="text-[10px] text-neutral-500">
                          {item.rarity} · {item.item_type}
                        </span>
                      </div>
                      {item.description && (
                        <div className="text-[10px] text-neutral-400">
                          {item.description}
                        </div>
                      )}
                      <div className="flex gap-1">
                        {item.requires_attunement && !isAttuned && (
                          <button
                            onClick={() => attune(item.name)}
                            disabled={busy}
                            className="px-2 py-0.5 bg-purple-800 border border-purple-600 rounded text-[10px] hover:bg-purple-700 disabled:opacity-40"
                          >
                            同调
                          </button>
                        )}
                        {isAttuned && (
                          <button
                            onClick={() => breakAttunement(item.name)}
                            disabled={busy}
                            className="px-2 py-0.5 bg-red-900 border border-red-700 rounded text-[10px] hover:bg-red-800 disabled:opacity-40"
                          >
                            解除同调
                          </button>
                        )}
                        {isAttuned && (
                          <span className="text-[10px] text-green-400 self-center">
                            ✓ 已同调
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
