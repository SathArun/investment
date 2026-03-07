import { create } from 'zustand'
import type { TaxBracket, TimeHorizon, RiskFilter, SortDir } from '@/types/product'

interface FilterState {
  taxBracket: TaxBracket
  timeHorizon: TimeHorizon
  riskFilter: RiskFilter
  sortBy: string
  sortDir: SortDir
  setTaxBracket: (v: TaxBracket) => void
  setTimeHorizon: (v: TimeHorizon) => void
  setRiskFilter: (v: RiskFilter) => void
  setSortBy: (col: string) => void
  setSortDir: (dir: SortDir) => void
}

export const useFilterStore = create<FilterState>((set) => ({
  taxBracket: 0,
  timeHorizon: 'long',
  riskFilter: 'All',
  sortBy: 'advisor_score',
  sortDir: 'desc',
  setTaxBracket: (taxBracket) => set({ taxBracket }),
  setTimeHorizon: (timeHorizon) => set({ timeHorizon }),
  setRiskFilter: (riskFilter) => set({ riskFilter }),
  setSortBy: (sortBy) => set({ sortBy }),
  setSortDir: (sortDir) => set({ sortDir }),
}))
