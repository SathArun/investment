import { create } from 'zustand'
import apiClient from '@/api/client'

interface AllocationItem {
  name: string
  pct: number
}

interface CorpusProjectionRow {
  year: number
  conservative: number
  base: number
  optimistic: number
}

interface CorpusProjection {
  conservative: number[]
  base: number[]
  optimistic: number[]
}

interface GoalPlan {
  inflation_adjusted_target: number
  required_sip: number
  goal_probability: number
  recommended_allocation: AllocationItem[]
  nps_highlight: boolean
  corpus_projection: CorpusProjection
}

interface Client {
  id: string
  name: string
  age: number
  tax_bracket: number
}

interface GoalState {
  clients: Client[]
  currentPlan: GoalPlan | null
  isLoadingClients: boolean
  isLoadingPlan: boolean
  fetchClients: () => Promise<void>
  createClient: (name: string, age: number, taxBracket: number) => Promise<Client | null>
  createGoalAndFetchPlan: (body: GoalFormData) => Promise<void>
}

export interface GoalFormData {
  client_id: string
  name: string
  target_amount_inr: number
  target_date: string // ISO date string
  current_corpus_inr: number
  monthly_sip_inr: number
  annual_stepup_pct: number
  inflation_rate: number
}

export const useGoalStore = create<GoalState>((set) => ({
  clients: [],
  currentPlan: null,
  isLoadingClients: false,
  isLoadingPlan: false,
  fetchClients: async () => {
    set({ isLoadingClients: true })
    try {
      const { data } = await apiClient.get('/clients')
      set({ clients: data.clients ?? data, isLoadingClients: false })
    } catch {
      set({ isLoadingClients: false })
    }
  },
  createClient: async (name, age, taxBracket) => {
    try {
      const { data } = await apiClient.post('/clients', { name, age, tax_bracket: taxBracket })
      set((state) => ({ clients: [...state.clients, data] }))
      return data
    } catch {
      return null
    }
  },
  createGoalAndFetchPlan: async (body) => {
    set({ isLoadingPlan: true, currentPlan: null })
    try {
      const { data: goal } = await apiClient.post('/goals', body)
      const { data: plan } = await apiClient.get(`/goals/${goal.id}/plan`)
      // API returns corpus_projection as array of row objects; reshape to parallel arrays
      const rows: CorpusProjectionRow[] = plan.corpus_projection ?? []
      const corpus_projection: CorpusProjection = {
        conservative: rows.map((r) => r.conservative),
        base: rows.map((r) => r.base),
        optimistic: rows.map((r) => r.optimistic),
      }
      set({ currentPlan: { ...plan, corpus_projection }, isLoadingPlan: false })
    } catch {
      set({ isLoadingPlan: false })
    }
  },
}))
