import { create } from 'zustand'
import apiClient from '@/api/client'
import type { ProductRow, DataFreshness, TaxBracket, TimeHorizon, RiskFilter } from '@/types/product'

interface DashboardState {
  products: ProductRow[]
  dataFreshness: DataFreshness | null
  isLoading: boolean
  error: string | null
  pinnedProducts: Set<number>
  fetchProducts: (taxBracket: TaxBracket, timeHorizon: TimeHorizon, riskFilter: RiskFilter) => Promise<void>
  togglePin: (id: number) => void
}

export const useDashboardStore = create<DashboardState>((set) => ({
  products: [],
  dataFreshness: null,
  isLoading: false,
  error: null,
  pinnedProducts: new Set<number>(),
  togglePin: (id) =>
    set((state) => {
      const next = new Set(state.pinnedProducts)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return { pinnedProducts: next }
    }),
  fetchProducts: async (taxBracket, timeHorizon, riskFilter) => {
    set({ isLoading: true, error: null })
    try {
      const params: Record<string, string | number> = {
        tax_bracket: taxBracket,
        time_horizon: timeHorizon,
      }
      if (riskFilter !== 'All') {
        params.risk_filter = riskFilter
      }
      const { data } = await apiClient.get('/products', { params })
      set({ products: data.products, dataFreshness: data.data_freshness, isLoading: false })
    } catch {
      set({ error: 'Failed to load products', isLoading: false })
    }
  },
}))
