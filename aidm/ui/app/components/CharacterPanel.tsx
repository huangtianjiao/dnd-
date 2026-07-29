"use client";

import type { CharacterSheet } from "../lib/types";
import { ConditionTracker } from "./ConditionTracker";
import { SpellSlots } from "./SpellSlots";
import { HitDiceTracker } from "./HitDiceTracker";
import { DeathSaveTracker } from "./DeathSaveTracker";

const abbr: Record<string, string> = { str: "STR", dex: "DEX", con: "CON", int: "INT", wis: "WIS", cha: "CHA" };

interface CharacterPanelProps {
  character: CharacterSheet | null;
  onDeathSaveRoll?: () => void;
}

export function CharacterPanel({ character, onDeathSaveRoll }: CharacterPanelProps) {
  if (!character) return <div className="text-muted">加载角色卡...</div>;

  const hpPct = Math.max(0, (character.hp / character.hp_max) * 100);
  const dexMod = character.abilities?.dex?.mod ?? 0;

  return (
    <>
      {/* 角色头像 */}
      <div className="char-portrait">
        <div className="avatar">{character.name.charAt(0)}</div>
        <div className="info">
          <div className="name">{character.name}</div>
          <div className="sub">
            {character.race} {character.char_class}
            {character.subclass ? `(${character.subclass})` : ""} Lv.{character.level}
          </div>
        </div>
      </div>

      {/* HP 条 */}
      <div className="hp-section">
        <div className="label">生命值{character.temp_hp ? ` (临时+${character.temp_hp})` : ""}</div>
        <div className="hp-bar-container">
          <div className="hp-bar-fill" style={{ width: `${hpPct}%` }} />
        </div>
        <div className="hp-text">{character.hp} / {character.hp_max}</div>
      </div>

      {/* AC / 速度 / 先攻 */}
      <div className="ac-speed">
        <div className="stat-box">
          <div className="val">{character.ac}</div>
          <div className="lbl">AC</div>
        </div>
        <div className="stat-box">
          <div className="val">{character.speed}</div>
          <div className="lbl">速度 ft</div>
        </div>
        <div className="stat-box">
          <div className="val">{dexMod >= 0 ? `+${dexMod}` : dexMod}</div>
          <div className="lbl">先攻</div>
        </div>
      </div>

      {/* 六维属性 */}
      <div className="ability-grid">
        {Object.entries(character.abilities).map(([k, v]) => (
          <div key={k} className="ability-box" title={abbr[k] || k}>
            <div className="abi-name">{abbr[k] || k}</div>
            <div className="abi-val">{v.score}</div>
            <div className="abi-mod">{v.mod >= 0 ? `+${v.mod}` : v.mod}</div>
          </div>
        ))}
      </div>

      {/* 死亡豁免追踪器（HP=0 时显示） */}
      {character.hp <= 0 && !character.dead && (
        <DeathSaveTracker
          successes={character.death_successes || 0}
          failures={character.death_failures || 0}
          onRoll={onDeathSaveRoll || (() => {})}
        />
      )}

      {/* 死亡状态 */}
      {character.dead && (
        <div className="death-save-box">
          <div className="ds-title">💀 角色已死亡</div>
        </div>
      )}

      {/* 稳定状态 */}
      {character.hp <= 0 && character.stable && !character.dead && (
        <div className="death-save-box">
          <div className="ds-title">已稳定</div>
        </div>
      )}

      {/* 状态效果（只读） */}
      <div className="panel-section">
        <div className="section-title">状态效果</div>
        <ConditionTracker conditions={character.conditions || []} />
      </div>

      {/* 法术位（施法职业） */}
      {character.spell_slots && Object.keys(character.spell_slots).length > 0 && (
        <div className="panel-section">
          <div className="section-title">法术位</div>
          <SpellSlots slots={character.spell_slots} />
        </div>
      )}

      {/* 装备武器 */}
      {character.equipped_weapon && (
        <div className="panel-section">
          <div className="section-title">装备</div>
          <div className="skill-list">
            <div className="inv-item equipped">
              <span className="inv-name">🗡️ {character.equipped_weapon}</span>
              <span className="inv-qty">主手</span>
            </div>
          </div>
        </div>
      )}

      {/* 生命骰（只读） */}
      {character.hit_dice_current !== undefined && character.hit_dice_max !== undefined && (
        <div className="panel-section">
          <div className="section-title">
            <span>Hit Dice</span>
            <span style={{ fontSize: 10, color: "var(--text-tertiary)" }}>
              {character.hit_dice_current}/{character.hit_dice_max}
            </span>
          </div>
          <HitDiceTracker
            total={character.hit_dice_max || character.level}
            remaining={character.hit_dice_current ?? character.level}
            faces={8}
          />
        </div>
      )}

      {/* 力竭等级 */}
      {character.exhaustion > 0 && (
        <div className="panel-section">
          <div style={{ fontSize: 11, color: "var(--text-amber)" }}>
            力竭等级: {character.exhaustion}/6
          </div>
        </div>
      )}
    </>
  );
}
