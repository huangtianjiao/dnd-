import { create } from "zustand"
import type { CharacterSheet } from "@/app/lib/types"

interface CharacterState {
  character: CharacterSheet | null
  setCharacter: (data: CharacterSheet) => void
  updateHp: (hp: number) => void
  updateAc: (ac: number) => void
  addCondition: (condition: string) => void
  removeCondition: (condition: string) => void
  clearConditions: () => void
  reset: () => void
}

export const useCharacterStore = create<CharacterState>((set) => ({
  character: null,

  setCharacter: (data) => set({ character: data }),

  updateHp: (hp) =>
    set((s) => ({
      character: s.character ? { ...s.character, hp } : null,
    })),

  updateAc: (ac) =>
    set((s) => ({
      character: s.character ? { ...s.character, ac } : null,
    })),

  addCondition: (condition) =>
    set((s) => ({
      character: s.character
        ? { ...s.character, conditions: [...s.character.conditions, condition] }
        : null,
    })),

  removeCondition: (condition) =>
    set((s) => ({
      character: s.character
        ? {
            ...s.character,
            conditions: s.character.conditions.filter((c) => c !== condition),
          }
        : null,
    })),

  clearConditions: () =>
    set((s) => ({
      character: s.character ? { ...s.character, conditions: [] } : null,
    })),

  reset: () => set({ character: null }),
}))
