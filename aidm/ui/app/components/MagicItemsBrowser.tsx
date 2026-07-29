"use client";

import { useState, useCallback, useEffect } from "react";
import { apiGet, errMsg } from "../lib/api";

interface MagicItemsBrowserProps {
  onClose: () => void;
  toast?: (msg: string, type?: string) => void;
}

const RARITIES = ["全部", "普通", "非普通", "稀有", "极稀有", "传说", "神器"];
const RARITY_MAP: Record<string, string> = {
  "全部": "", "普通": "COMMON", "非普通": "UNCOMMON", "稀有": "RARE",
  "极稀有": "VERY_RARE", "传说": "LEGENDARY", "神器": "ARTIFACT",
};
const TYPES = ["全部", "武器", "护甲", "奇物", "戒指", "卷轴", "药水", "法杖", "权杖", "魔杖"];
const TYPE_MAP: Record<string, string> = {
  "全部": "", "武器": "WEAPON", "护甲": "ARMOR", "奇物": "WONDROUS_ITEM",
  "戒指": "RING", "卷轴": "SCROLL", "药水": "POTION",
  "法杖": "STAFF", "权杖": "ROD", "魔杖": "WAND",
};
const RARITY_COLOR: Record<string, string> = {
  COMMON: "var(--text-tertiary)", UNCOMMON: "var(--text-green)", RARE: "var(--text-blue)",
  VERY_RARE: "var(--text-purple)", LEGENDARY: "var(--text-amber)", ARTIFACT: "var(--text-red)",
};

export function MagicItemsBrowser({ onClose, toast }: MagicItemsBrowserProps) {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [rarity, setRarity] = useState("全部");
  const [type, setType] = useState("全部");
  const [cursedOnly, setCursedOnly] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      const r = RARITY_MAP[rarity];
      const t = TYPE_MAP[type];
      if (r) params.set("rarity", r);
      if (t) params.set("item_type", t);
      if (cursedOnly) params.set("cursed_only", "true");
      const url = `/magic-items${params.toString() ? "?" + params.toString() : ""}`;
      const result = await apiGet<{ items: any[]; count: number }>(url);
      setItems(result.items || []);
    } catch (e) {
      setItems([]);
      toast?.("加载魔法物品失败: " + errMsg(e), "error");
    } finally {
      setLoading(false);
    }
  }, [rarity, type, cursedOnly, toast]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="modal-overlay visible" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="mh-title">🔮 魔法物品图鉴</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {/* 筛选器 */}
          <div className="flex-col" style={{ gap: 8, marginBottom: 12 }}>
            <div className="flex-row" style={{ gap: 4, flexWrap: "wrap" }}>
              {RARITIES.map((r) => (
                <button key={r} className={`btn ${rarity === r ? "btn-amber" : "btn-secondary"}`}
                  style={{ padding: "3px 8px", fontSize: 10 }}
                  onClick={() => setRarity(r)}>
                  {r}
                </button>
              ))}
            </div>
            <div className="flex-row" style={{ gap: 4, flexWrap: "wrap" }}>
              {TYPES.map((t) => (
                <button key={t} className={`btn ${type === t ? "btn-amber" : "btn-secondary"}`}
                  style={{ padding: "3px 8px", fontSize: 10 }}
                  onClick={() => setType(t)}>
                  {t}
                </button>
              ))}
            </div>
            <label className="flex-row" style={{ gap: 4, alignItems: "center", cursor: "pointer" }}>
              <input type="checkbox" checked={cursedOnly} onChange={(e) => setCursedOnly(e.target.checked)}
                style={{ accentColor: "var(--text-purple)" }} />
              <span className="text-xs text-muted">仅显示诅咒物品</span>
            </label>
          </div>

          {loading ? (
            <div className="text-muted">加载中...</div>
          ) : items.length === 0 ? (
            <div className="text-muted">无匹配的魔法物品</div>
          ) : (
            <div className="flex-col" style={{ gap: 6 }}>
              {items.map((item, i) => {
                const name = item.name || item.name_en || `物品${i}`;
                const rarity = item.rarity || "";
                const itemType = item.item_type || "";
                const desc = item.description || "";
                const color = RARITY_COLOR[rarity] || "var(--text-primary)";
                return (
                  <div
                    key={`${name}-${i}`}
                    className={`spell-card ${expanded === name ? "expanded" : ""}`}
                    onClick={() => setExpanded(expanded === name ? null : name)}
                    style={{ cursor: "pointer" }}
                  >
                    <div className="sc-header">
                      <span className="sc-name" style={{ color }}>{name}</span>
                      <span className="sc-level">{rarity}</span>
                    </div>
                    <div className="sc-meta">
                      <span>{itemType}</span>
                      {item.value_gp != null && <span>{item.value_gp} gp</span>}
                      {item.requires_attunement && <span style={{ color: "var(--text-purple)" }}>需同调</span>}
                      {item.attuned && <span style={{ color: "var(--text-green)" }}>✓已同调</span>}
                    </div>
                    {desc && <div className="sc-desc">{desc}</div>}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
