"use client";

import type { CharacterSheet } from "../lib/types";

const abbr: Record<string, string> = { str: "力", dex: "敏", con: "体", int: "智", wis: "感", cha: "魅" };

export function CharacterPanel({ character }: { character: CharacterSheet | null }) {
  if (!character) return <div className="text-xs text-neutral-600">加载角色卡...</div>;

  const hpPct = Math.max(0, (character.hp / character.hp_max) * 100);
  const hpColor = (pct: number) => (pct > 50 ? "#22aa22" : pct > 25 ? "#aaaa22" : "#aa2222");

  return (
    <>
      <div className="text-center">
        <div className="text-lg font-bold text-amber-400">{character.name}</div>
        <div className="text-xs text-neutral-500">{character.race} {character.char_class}{character.subclass ? `(${character.subclass})` : ""} Lv{character.level}</div>
        {character.background && (
          <div className="text-[10px] text-neutral-500">背景: {character.background}</div>
        )}
        {character.alignment && (
          <div className="text-[10px] text-neutral-500">阵营: {character.alignment}</div>
        )}
      </div>

      {/* HP 条 */}
      <div>
        <div className="flex justify-between text-xs mb-1">
          <span className="text-neutral-400">HP</span>
          <span className="text-neutral-300">{character.hp}/{character.hp_max}{character.temp_hp ? ` (+${character.temp_hp})` : ""}</span>
        </div>
        <div className="h-2 bg-neutral-800 rounded-full overflow-hidden">
          <div
            className="h-full transition-all duration-400 rounded-full"
            style={{ width: `${hpPct}%`, background: hpColor(hpPct) }}
          />
        </div>
      </div>

      {/* AC / 速度 / 熟练 */}
      <div className="grid grid-cols-3 gap-1 text-center">
        <div className="bg-neutral-800 rounded p-1">
          <div className="text-base font-bold text-amber-400">{character.ac}</div>
          <div className="text-[10px] text-neutral-500">AC</div>
        </div>
        <div className="bg-neutral-800 rounded p-1">
          <div className="text-base font-bold text-amber-400">{character.speed}</div>
          <div className="text-[10px] text-neutral-500">速度</div>
        </div>
        <div className="bg-neutral-800 rounded p-1">
          <div className="text-base font-bold text-amber-400">+{character.proficiency}</div>
          <div className="text-[10px] text-neutral-500">熟练</div>
        </div>
      </div>

      {/* 六维属性 */}
      <div className="grid grid-cols-2 gap-1">
        {Object.entries(character.abilities).map(([k, v]) => (
          <div key={k} className="bg-neutral-800 rounded p-1 text-center">
            <div className="text-[10px] text-neutral-500">{abbr[k] || k}</div>
            <div className="text-sm font-bold">{v.score}</div>
            <div className="text-[10px] text-neutral-400">{v.mod >= 0 ? `+${v.mod}` : v.mod}</div>
          </div>
        ))}
      </div>

      {/* 装备武器 */}
      {character.equipped_weapon && (
        <div className="text-[11px] text-neutral-400">
          🗡️ 武器: <span className="text-amber-400">{character.equipped_weapon}</span>
        </div>
      )}

      {/* 生命骰 */}
      {character.hit_dice_current !== undefined && character.hit_dice_max !== undefined && (
        <div className="text-[11px] text-neutral-400">
          🎲 生命骰: <span className="text-amber-400">{character.hit_dice_current}/{character.hit_dice_max}</span>
        </div>
      )}

      {/* 法术位（施法职业） */}
      {character.spell_slots && Object.keys(character.spell_slots).length > 0 && (
        <div className="text-[11px]">
          <div className="text-neutral-500 mb-1">法术位</div>
          <div className="flex flex-wrap gap-1">
            {Object.entries(character.spell_slots).map(([lvl, rem]) => (
              <span
                key={lvl}
                className={`px-1.5 py-0.5 rounded border ${
                  rem > 0
                    ? "bg-purple-950 border-purple-700 text-purple-300"
                    : "bg-neutral-800 border-neutral-700 text-neutral-600"
                }`}
              >
                {lvl}环:{rem}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* 状态条件 */}
      {character.conditions && character.conditions.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {character.conditions.map((cond, i) => (
            <span key={i} className="text-[10px] px-1.5 py-0.5 bg-neutral-800 rounded border border-neutral-700">
              {cond}
            </span>
          ))}
        </div>
      )}

      {/* 力竭等级 */}
      {character.exhaustion > 0 && (
        <div className="text-xs text-orange-400">力竭等级: {character.exhaustion}/6</div>
      )}

      {/* 死亡豁免追踪器 */}
      {character.hp <= 0 && !character.dead && (
        <div className={`border rounded p-2 text-center ${character.stable ? "bg-green-950 border-green-800" : "bg-red-950 border-red-800"}`}>
          <div className="text-xs text-red-400 mb-1">⚠️ 濒死状态</div>
          {character.stable ? (
            <div className="text-xs text-green-400">已稳定</div>
          ) : (
            <div className="text-xs text-neutral-400">需要死亡豁免检定</div>
          )}
        </div>
      )}

      {character.dead && (
        <div className="bg-red-950 border border-red-800 rounded p-2 text-center">
          <div className="text-sm font-bold text-red-400">💀 角色已死亡</div>
        </div>
      )}
    </>
  );
}
