"use client";

import { useState, useCallback, useEffect } from "react";
import { apiGet, errMsg } from "../lib/api";

interface FeatsBrowserProps {
  onClose: () => void;
}

const CATEGORIES = ["全部", "起源", "通用", "战斗风格", "传奇恩惠"];

export function FeatsBrowser({ onClose }: FeatsBrowserProps) {
  const [feats, setFeats] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("全部");
  const [expanded, setExpanded] = useState<string | null>(null);

  const load = useCallback(async (cat: string) => {
    setLoading(true);
    try {
      const url = cat === "全部" ? "/feats" : `/feats?category=${encodeURIComponent(cat)}`;
      const r = await apiGet<{ feats: any[]; count: number }>(url);
      setFeats(r.feats || []);
    } catch (e) {
      setFeats([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(category);
  }, [category, load]);

  const featName = (f: any) => typeof f === "string" ? f : f.name || "";
  const featDesc = (f: any) => typeof f === "string" ? "" : f.description || "";
  const featCategory = (f: any) => typeof f === "string" ? "" : f.category || "";
  const featPrereq = (f: any) => typeof f === "string" ? "" : f.prerequisite || "";

  return (
    <div className="modal-overlay visible" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="mh-title">📋 专长参考</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {/* 分类筛选 */}
          <div className="flex-row" style={{ gap: 4, marginBottom: 12, flexWrap: "wrap" }}>
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                className={`btn ${category === cat ? "btn-amber" : "btn-secondary"}`}
                style={{ padding: "4px 10px", fontSize: 11 }}
                onClick={() => setCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>

          {loading ? (
            <div className="text-muted">加载中...</div>
          ) : feats.length === 0 ? (
            <div className="text-muted">无可用专长</div>
          ) : (
            <div className="flex-col" style={{ gap: 6 }}>
              {feats.map((f, i) => {
                const name = featName(f);
                const desc = featDesc(f);
                const cat = featCategory(f);
                const prereq = featPrereq(f);
                return (
                  <div
                    key={`${name}-${i}`}
                    className={`spell-card ${expanded === name ? "expanded" : ""}`}
                    onClick={() => setExpanded(expanded === name ? null : name)}
                    style={{ cursor: "pointer" }}
                  >
                    <div className="sc-header">
                      <span className="sc-name">{name}</span>
                      {cat && <span className="sc-level">{cat}</span>}
                    </div>
                    {(desc || prereq) && (
                      <div className="sc-desc">
                        {prereq && <div style={{ marginBottom: 4, color: "var(--text-amber)" }}>前提: {prereq}</div>}
                        {desc}
                      </div>
                    )}
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
