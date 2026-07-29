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
      <button onClick={openPanel} className="btn btn-secondary w-full">
        🎒 物品栏
      </button>

      {open && (
        <div className="modal-overlay visible" onClick={() => setOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="mh-title">🎒 物品栏</div>
              <button onClick={() => setOpen(false)} className="modal-close">
                ✕
              </button>
            </div>

            <div className="modal-body">
              {busy ? (
                <div className="text-sm text-muted">加载中...</div>
              ) : magicItems.length === 0 ? (
                <div className="text-sm text-muted">物品栏为空</div>
              ) : (
                <div className="flex-col">
                  {magicItems.map((item) => {
                    const isAttuned = attunedItems.includes(item.name);
                    return (
                      <div
                        key={item.name}
                        className="flex-col"
                        style={{
                          border: "0.5px solid var(--border)",
                          borderRadius: "var(--radius-md)",
                          background: "var(--bg-secondary)",
                          padding: "10px 12px",
                        }}
                      >
                        <div className="flex-between">
                          <span className="text-sm text-bold text-blue">
                            {item.name}
                          </span>
                          <span className="text-10 text-muted">
                            {item.rarity} · {item.item_type}
                          </span>
                        </div>
                        {item.description && (
                          <div className="text-10 text-muted">
                            {item.description}
                          </div>
                        )}
                        <div className="flex-row">
                          {item.requires_attunement && !isAttuned && (
                            <button
                              onClick={() => attune(item.name)}
                              disabled={busy}
                              className="btn btn-primary"
                            >
                              同调
                            </button>
                          )}
                          {isAttuned && (
                            <button
                              onClick={() => breakAttunement(item.name)}
                              disabled={busy}
                              className="btn"
                              style={{
                                background: "var(--bg-red)",
                                color: "var(--text-red)",
                                border: "0.5px solid #f09595",
                                fontWeight: 500,
                              }}
                            >
                              解除同调
                            </button>
                          )}
                          {isAttuned && (
                            <span
                              className="text-10 text-green"
                              style={{ alignSelf: "center" }}
                            >
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
        </div>
      )}
    </>
  );
}
