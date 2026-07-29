import { create } from "zustand"
import type { CombatData, Combatant } from "@/app/lib/types"

interface CombatState {
  combat: CombatData | null
  selectedTarget: string | null
  setCombat: (data: CombatData) => void
  clearCombat: () => void
  setSelectedTarget: (name: string | null) => void
  getCurrentTurn: () => Combatant | undefined
  getNextAlly: () => Combatant | undefined
}

export const useCombatStore = create<CombatState>((set, get) => ({
  combat: null,
  selectedTarget: null,

  setCombat: (data) => set({ combat: data }),
  clearCombat: () => set({ combat: null, selectedTarget: null }),
  setSelectedTarget: (name) => set({ selectedTarget: name }),

  getCurrentTurn: () => {
    const { combat } = get()
    if (!combat?.current_turn || !combat.initiative_order) return undefined
    return combat.initiative_order.find((c) => c.name === combat.current_turn)
  },

  getNextAlly: () => {
    const { combat } = get()
    if (!combat?.initiative_order || !combat.current_turn) return undefined
    const order = combat.initiative_order
    const idx = order.findIndex((c) => c.name === combat.current_turn)
    const current = order[idx]
    if (!current) return undefined
    // 找下一个同阵营的参战者
    for (let i = 1; i <= order.length; i++) {
      const next = order[(idx + i) % order.length]
      if (next.side === current.side) return next
    }
    return undefined
  },
}))
