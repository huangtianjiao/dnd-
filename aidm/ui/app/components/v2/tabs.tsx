"use client";

import { useCallback, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { apiGet, apiPost, errMsg } from "../../lib/api";
import type { CharacterSheet } from "../../lib/types";

/* ================================================================
 * 右栏四标签页：CharacterSheetTab / SpellbookTab / InventoryTab / RuleLookupTab
 * （docs/FRONTEND_REDESIGN.md §2 panel/*）
 * ================================================================ */

const AB_NAMES: Record<string, string> = {
  str: "力量",
  dex: "敏捷",
  con: "体质",
  int: "智力",
  wis: "感知",
  cha: "魅力",
};

/* ---------------- 角色卡 ---------------- */

interface CharacterSheetTabProps {
  character: CharacterSheet | null;
  onDeathSaveRoll: () => void;
  featSlot?: ReactNode;
}

export function CharacterSheetTab({ character, onDeathSaveRoll, featSlot }: CharacterSheetTabProps) {
  if (!character) return <div className="v2-panel-loading">加载角色卡…</div>;
  const c = character;
  const hpPct = c.hp_max > 0 ? Math.max(0, Math.min(100, (c.hp / c.hp_max) * 100)) : 0;
  const tempPct = c.temp_hp && c.hp_max > 0 ? Math.max(0, Math.min(100, (c.temp_hp / c.hp_max) * 100)) : 0;
  const dexMod = c.abilities?.dex?.mod ?? 0;
  const wisMod = c.abilities?.wis?.mod ?? 0;
  const slots = Object.entries(c.spell_slots || {}).sort(([a], [b]) => Number(a) - Number(b));
  const hdMax = c.hit_dice_max ?? c.level;
  const hdCur = c.hit_dice_current ?? c.level;
  const attuned = c.attuned_items || [];

  return (
    <>
      <div className="v2-pc-head">
        <div className="avatar">{c.name.charAt(0)}</div>
        <div className="who">
          <h2>{c.name}</h2>
          <div className="sub">
            {c.race} · {c.char_class}
            {c.subclass ? `（${c.subclass}）` : ""} {c.level} 级 · {c.alignment || "无阵营"} · 熟练 +
            {c.proficiency}
          </div>
        </div>
      </div>

      <div className="v2-stat-block">
        <h3>生命</h3>
        <div className="v2-hp-main">
          <span className="big">{c.hp}</span>
          <span className="max">
            / {c.hp_max}
            {c.temp_hp ? `（临时+${c.temp_hp}）` : ""}
          </span>
          <div className="v2-hp-track">
            <i style={{ width: `${hpPct}%` }} />
            {tempPct > 0 && <span className="temp" style={{ width: `${tempPct}%` }} />}
          </div>
        </div>
      </div>

      <div className="v2-def-row">
        <div className="v2-def-cell">
          <div className="v">{c.ac}</div>
          <div className="k">AC</div>
        </div>
        <div className="v2-def-cell">
          <div className="v">{c.speed}</div>
          <div className="k">速度 尺</div>
        </div>
        <div className="v2-def-cell">
          <div className="v">{dexMod >= 0 ? `+${dexMod}` : dexMod}</div>
          <div className="k">先攻</div>
        </div>
        <div className="v2-def-cell">
          <div className="v">{10 + wisMod}</div>
          <div className="k">被动察觉</div>
        </div>
      </div>

      <div className="v2-stat-block">
        <h3>属性</h3>
        <div className="v2-ab-grid">
          {Object.entries(c.abilities).map(([k, v]) => (
            <div key={k} className="v2-ab-cell">
              <div className={`mod ${v.mod < 0 ? "neg" : ""}`}>{v.mod >= 0 ? `+${v.mod}` : v.mod}</div>
              <div className="score">{v.score}</div>
              <div className="nm">{AB_NAMES[k] || k}</div>
            </div>
          ))}
        </div>
      </div>

      {slots.length > 0 && (
        <div className="v2-stat-block">
          <h3>法术位</h3>
          {slots.map(([lvl, left]) => (
            <div key={lvl} className="v2-slot-row">
              <span className="nm">{lvl} 环</span>
              <span>剩余 {left}</span>
            </div>
          ))}
        </div>
      )}

      <div className="v2-stat-block">
        <h3>生命骰 · 死亡豁免</h3>
        <div className="v2-slot-row">
          <span className="nm">生命骰</span>
          <span className="v2-pips hd">
            {Array.from({ length: hdMax }, (_, i) => (
              <i key={i} className={i < hdCur ? "full" : ""} />
            ))}
          </span>
          <span style={{ fontSize: 11 }}>
            {hdCur}/{hdMax}
          </span>
        </div>
        <div className="v2-ds-row" style={{ marginTop: 8 }}>
          <span className="group ok">
            豁免成功{" "}
            {[0, 1, 2].map((i) => (
              <i key={i} className={i < (c.death_successes || 0) ? "full" : ""} />
            ))}
          </span>
          <span className="group bad">
            豁免失败{" "}
            {[0, 1, 2].map((i) => (
              <i key={i} className={i < (c.death_failures || 0) ? "full" : ""} />
            ))}
          </span>
          <span style={{ marginLeft: "auto", color: "var(--v2-ink-faint)" }}>力竭 {c.exhaustion} 级</span>
        </div>
        {c.hp <= 0 && !c.dead && !c.stable && (
          <button className="v2-cast-btn" style={{ marginTop: 8 }} onClick={onDeathSaveRoll}>
            掷死亡豁免
          </button>
        )}
        {c.dead && <div style={{ marginTop: 8, color: "var(--v2-red)" }}>💀 角色已死亡</div>}
        {!c.dead && c.stable && c.hp <= 0 && (
          <div style={{ marginTop: 8, color: "var(--v2-green)" }}>伤势已稳定</div>
        )}
      </div>

      <div className="v2-stat-block">
        <h3>状态 · 同调</h3>
        <div className="v2-cond-list">
          {(c.conditions || []).length === 0 ? (
            <span className="v2-cond-none">无状态异常</span>
          ) : (
            c.conditions.map((cond) => (
              <span key={cond} className="v2-cond-pill">
                {cond}
              </span>
            ))
          )}
        </div>
        <div className="v2-attune-meter" style={{ marginTop: 8 }}>
          同调
          <span className="slots">
            {[0, 1, 2].map((i) => (
              <i key={i} className={i < attuned.length ? "full" : ""} />
            ))}
          </span>
          {attuned.length}/3
        </div>
      </div>

      {featSlot}
    </>
  );
}

/* ---------------- 法术书 ---------------- */

export interface SpellInfo {
  name: string;
  level: number;
  school: string;
  casting_time: string;
  range: string;
  duration: string;
  components: string[];
  description: string;
}

interface SpellbookTabProps {
  character: CharacterSheet | null;
  spells: SpellInfo[];
  onCast: (spellName: string) => void;
}

export function SpellbookTab({ character, spells, onCast }: SpellbookTabProps) {
  const [open, setOpen] = useState<string | null>(null);
  const known = character?.known_spells || [];
  // 拥有性门控：只列已学会的法术（known_spells 为空即未掌握任何法术，
  // 不再旁路展示全量表——与后端 _resolve_cast 校验一致）
  const mine = spells.filter((s) => known.includes(s.name));
  if (mine.length === 0) return <div className="v2-panel-loading">该角色未掌握法术</div>;

  const groups: Record<number, SpellInfo[]> = {};
  mine.forEach((s) => (groups[s.level] = groups[s.level] || []).push(s));
  const slots = character?.spell_slots || {};

  return (
    <>
      {Object.keys(groups)
        .map(Number)
        .sort((a, b) => a - b)
        .map((lvl) => (
          <div key={lvl} className="v2-spell-lvl">
            <div className="lvl-cap">
              <span>{lvl === 0 ? "戏法（不限次）" : `${lvl} 环法术`}</span>
              {lvl > 0 && slots[String(lvl)] != null && <span>剩余 {slots[String(lvl)]}</span>}
            </div>
            {groups[lvl].map((sp) => (
              <div
                key={sp.name}
                className={`v2-spell-item ${open === sp.name ? "open" : ""}`}
                onClick={() => setOpen(open === sp.name ? null : sp.name)}
              >
                <div className="top">
                  <span className="nm">{sp.name}</span>
                  <span className="meta">{sp.school}</span>
                </div>
                <div className="desc">
                  <div>
                    {sp.casting_time} · {sp.range} · {(sp.components || []).join(",")} · {sp.duration}
                  </div>
                  <div style={{ marginTop: 4 }}>{sp.description}</div>
                  <button
                    className="v2-cast-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      onCast(sp.name);
                    }}
                  >
                    以此行动：施展{sp.name}
                  </button>
                </div>
              </div>
            ))}
          </div>
        ))}
    </>
  );
}

/* ---------------- 物品栏 ---------------- */

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

interface Weapon {
  name: string;
  category: string;
  damage: string;
  properties: string[];
  equipped?: boolean;
}

interface InventoryTabProps {
  characterId: number;
  character: CharacterSheet | null;
  toast: (msg: string, type?: string) => void;
  onUpdated: () => void;
  extra?: ReactNode;
}

export function InventoryTab({ characterId, character, toast, onUpdated, extra }: InventoryTabProps) {
  const [busy, setBusy] = useState(false);
  const [attunedItems, setAttunedItems] = useState<string[]>([]);
  const [magicItems, setMagicItems] = useState<MagicItemDetail[]>([]);
  const [weapons, setWeapons] = useState<Weapon[]>([]);
  const [showWeapons, setShowWeapons] = useState(false);

  const load = useCallback(async () => {
    setBusy(true);
    try {
      const data = await apiGet<{
        inventory: string[];
        attuned_items: string[];
        magic_items: MagicItemDetail[];
        weapons: Weapon[];
      }>(`/character/${characterId}/inventory`);
      setAttunedItems(data.attuned_items || []);
      setMagicItems(data.magic_items || []);
      setWeapons(data.weapons || []);
    } catch (e) {
      toast("加载物品栏失败: " + errMsg(e), "error");
    } finally {
      setBusy(false);
    }
  }, [characterId, toast]);

  useEffect(() => {
    load();
  }, [load]);

  const attune = useCallback(
    async (itemName: string) => {
      setBusy(true);
      try {
        await apiPost(`/character/${characterId}/attune`, { item_name: itemName });
        toast(`已同调 ${itemName}`, "success");
        await load();
        onUpdated();
      } catch (e) {
        toast("同调失败: " + errMsg(e), "error");
      } finally {
        setBusy(false);
      }
    },
    [characterId, toast, load, onUpdated]
  );

  const breakAttunement = useCallback(
    async (itemName: string) => {
      setBusy(true);
      try {
        await apiPost(`/character/${characterId}/break-attunement`, { item_name: itemName });
        toast(`已解除同调 ${itemName}`, "success");
        await load();
        onUpdated();
      } catch (e) {
        toast("解除同调失败: " + errMsg(e), "error");
      } finally {
        setBusy(false);
      }
    },
    [characterId, toast, load, onUpdated]
  );

  // 拥有性门控：候选武器来自角色物品栏（load 已取），不再拉全量武器表
  const toggleWeapons = useCallback(() => {
    setShowWeapons((v) => !v);
  }, []);

  const equip = useCallback(
    async (name: string) => {
      try {
        await apiPost(`/character/${characterId}/equip-weapon`, { weapon_name: name });
        toast(`已装备 ${name}`, "success");
        await load();
        onUpdated();
      } catch (e) {
        toast("装备失败: " + errMsg(e), "error");
      }
    },
    [characterId, toast, load, onUpdated]
  );

  const attunedMagic = magicItems.filter((m) => attunedItems.includes(m.name));
  const packMagic = magicItems.filter((m) => !attunedItems.includes(m.name));

  return (
    <>
      <div className="v2-inv-group">
        <div className="cap">装备中</div>
        {character?.equipped_weapon ? (
          <div className="v2-inv-item">
            <span className="ico">🗡</span>
            <span className="nm">{character.equipped_weapon}</span>
            <span className="eq">装备中</span>
          </div>
        ) : (
          <div className="v2-panel-loading">未装备武器</div>
        )}
        {attunedMagic.map((m) => (
          <div key={m.name} className="v2-inv-item">
            <span className="ico">📿</span>
            <span className="nm">
              {m.name}
              <div className="note">{m.rarity} · {m.item_type}</div>
            </span>
            <span className="att" title="同调中">
              ◆
            </span>
          </div>
        ))}
        <button className="v2-cast-btn" style={{ marginTop: 6 }} onClick={toggleWeapons} disabled={busy}>
          {showWeapons ? "收起武器列表" : "🗡 更换武器"}
        </button>
        {showWeapons && (
          <div style={{ marginTop: 6 }}>
            {weapons.length === 0 && <div className="v2-panel-loading">包内没有其他武器</div>}
            {weapons.map((w) => (
              <div key={w.name} className="v2-inv-item" onClick={() => equip(w.name)} style={{ cursor: "pointer" }}>
                <span className="ico">⚔</span>
                <span className="nm">
                  {w.name}
                  <div className="note">
                    {w.damage} · {(w.properties || []).join(",")}
                  </div>
                </span>
                {character?.equipped_weapon === w.name && <span className="eq">装备中</span>}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="v2-inv-group">
        <div className="cap">背包 · 魔法物品</div>
        {busy && magicItems.length === 0 ? (
          <div className="v2-panel-loading">加载中…</div>
        ) : packMagic.length === 0 && attunedMagic.length === 0 ? (
          <div className="v2-panel-loading">暂无魔法物品</div>
        ) : (
          packMagic.map((m) => (
            <div key={m.name} className="v2-inv-item">
              <span className="ico">🎒</span>
              <span className="nm">
                {m.name}
                <div className="note">
                  {m.rarity} · {m.item_type}
                  {m.description ? ` · ${m.description}` : ""}
                </div>
              </span>
              {m.requires_attunement && (
                <button className="v2-cast-btn" disabled={busy} onClick={() => attune(m.name)}>
                  同调
                </button>
              )}
            </div>
          ))
        )}
        {attunedMagic.map((m) => (
          <div key={`brk-${m.name}`} className="v2-inv-item">
            <span className="ico">📿</span>
            <span className="nm">{m.name}</span>
            <button className="v2-cast-btn" disabled={busy} onClick={() => breakAttunement(m.name)}>
              解除同调
            </button>
          </div>
        ))}
      </div>

      <div className="v2-attune-meter">
        同调位
        <span className="slots">
          {[0, 1, 2].map((i) => (
            <i key={i} className={i < attunedItems.length ? "full" : ""} />
          ))}
        </span>
        {attunedItems.length}/3
      </div>

      {extra}
    </>
  );
}

/* ---------------- 规则速查（阶段1：静态规则卡本地检索；阶段2 接 RAG） ---------------- */

interface RuleEntry {
  k: string[];
  t: string;
  src: string;
  b: string;
}

const RULES: RuleEntry[] = [
  { k: ["突袭"], t: "突袭", src: "PHB2024 · 进行游戏", b: "战斗开始时，未察觉敌对者位置的参战者进行先攻检定具有劣势。2024 版突袭不再跳过整轮行动，而是直接体现在先攻劣势上。" },
  { k: ["先攻", "回合"], t: "先攻与回合顺序", src: "PHB2024 · 进行游戏", b: "每位参战者掷 d20+敏捷调整值决定先攻，由高到低行动。每轮约 6 秒。" },
  { k: ["优势", "劣势"], t: "优势与劣势", src: "PHB2024 · 进行游戏", b: "掷两枚 d20 取高（优势）或取低（劣势）。多个优势/劣势不叠加；两者同时存在时互相抵消。" },
  { k: ["借机攻击"], t: "借机攻击", src: "PHB2024 · 战斗", b: "敌对生物自愿离开你的触及范围时，你可以用反应对其发动一次近战攻击。" },
  { k: ["掩蔽"], t: "掩蔽", src: "PHB2024 · 战斗", b: "半掩蔽 AC/敏捷豁免 +2；四分之三掩蔽 +5；全掩蔽无法被直接攻击。" },
  { k: ["擒抱"], t: "擒抱", src: "PHB2024 · 战斗", b: "以近战攻击检定做力量（运动）对抗目标力量或敏捷；成功后目标陷入被擒状态（速度 0）。" },
  { k: ["死亡豁免", "濒死"], t: "死亡豁免", src: "PHB2024 · 战斗", b: "HP 归 0 时昏迷，每回合开始掷 d20：≥10 记 1 次成功，<10 记 1 次失败。成功 3 次伤势稳定；失败 3 次死亡。" },
  { k: ["短休"], t: "短休", src: "PHB2024 · 休整", b: "约 1 小时的休整。可花费任意数量生命骰恢复 HP（每骰+体质调整值）。" },
  { k: ["长休"], t: "长休", src: "PHB2024 · 休整", b: "约 8 小时的睡眠与轻度活动。恢复全部 HP、全部已耗生命骰的一半、法术位；力竭 -1 级。" },
  { k: ["专注"], t: "专注", src: "PHB2024 · 施法", b: "部分法术需要专注维持。受到伤害须通过体质豁免（DC 10 或伤害一半取高），否则法术中断。同时只能专注一个法术。" },
  { k: ["浴血"], t: "浴血（叙述规范）", src: "DMG2024 · 运作游戏", b: "生物 HP 降至一半以下时，DM 应在叙述中体现其伤势：踉跄、流血、攻势放缓——让玩家无需询问即可感知战况。" },
];

export function RuleLookupTab() {
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<RuleEntry[] | null>(null);

  const search = useCallback((query: string) => {
    const s = query.trim();
    if (!s) {
      setHits(null);
      return;
    }
    setHits(RULES.filter((r) => r.t.includes(s) || r.k.some((k) => s.includes(k)) || r.b.includes(s)));
  }, []);

  return (
    <>
      <div className="v2-rule-search">
        <input
          value={q}
          placeholder="查询规则，如：突袭 / 擒抱 / 短休……"
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") search(q);
          }}
        />
        <button onClick={() => search(q)}>检索</button>
      </div>
      <div className="v2-rule-hints">
        {RULES.slice(0, 8).map((r) => (
          <button
            key={r.t}
            onClick={() => {
              setQ(r.t);
              search(r.t);
            }}
          >
            {r.t}
          </button>
        ))}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {hits === null ? (
          <div className="v2-rule-card">
            <div className="rt">
              提示 <span className="src">RAG</span>
            </div>
            <div className="rb">
              输入关键词后，从已入库的《玩家手册2024》《城主指南2024》中检索相关规则段落；当前为内置速查卡，后续接入 RAG 段落级检索（含出处）。
            </div>
          </div>
        ) : hits.length === 0 ? (
          <div className="v2-rule-card">
            <div className="rt">
              未检索到「{q}」 <span className="src">本地</span>
            </div>
            <div className="rb">换个关键词试试，如：突袭 / 掩蔽 / 专注 / 长休。</div>
          </div>
        ) : (
          hits.map((r) => (
            <div key={r.t} className="v2-rule-card">
              <div className="rt">
                {r.t} <span className="src">{r.src}</span>
              </div>
              <div className="rb">{r.b}</div>
            </div>
          ))
        )}
      </div>
    </>
  );
}
