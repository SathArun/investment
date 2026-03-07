import { create } from 'zustand'
import apiClient from '@/api/client'

interface Question {
  id: string
  text: string
  category: string
  options: { value: number; label: string; score: number }[]
}
interface Client { id: string; name: string }
interface RiskProfile {
  id: string
  risk_score: number
  risk_category: string
  risk_description: string
  retention_until: string
}

interface RiskProfilerState {
  questions: Question[]
  clients: Client[]
  profile: RiskProfile | null
  isLoadingQuestions: boolean
  isSubmitting: boolean
  fetchQuestions: () => Promise<void>
  fetchClients: () => Promise<void>
  createClient: (name: string, age: number) => Promise<Client | null>
  submitProfile: (clientId: string, responses: Record<string, number>, rationale: string) => Promise<void>
}

export const useRiskProfilerStore = create<RiskProfilerState>((set) => ({
  questions: [],
  clients: [],
  profile: null,
  isLoadingQuestions: false,
  isSubmitting: false,
  fetchQuestions: async () => {
    set({ isLoadingQuestions: true })
    try {
      const { data } = await apiClient.get('/risk-profiler/questions')
      set({ questions: data.questions ?? data, isLoadingQuestions: false })
    } catch { set({ isLoadingQuestions: false }) }
  },
  fetchClients: async () => {
    try {
      const { data } = await apiClient.get('/clients')
      set({ clients: data.clients ?? data })
    } catch {
      // silently ignore client fetch errors — non-critical
    }
  },
  createClient: async (name, age) => {
    try {
      const { data } = await apiClient.post('/clients', { name, age })
      set((state) => ({ clients: [...state.clients, data] }))
      return data
    } catch {
      return null
    }
  },
  submitProfile: async (clientId, responses, rationale) => {
    set({ isSubmitting: true })
    try {
      const { data } = await apiClient.post('/risk-profiles', {
        client_id: clientId,
        responses,
        advisor_rationale: rationale,
      })
      set({ profile: data, isSubmitting: false })
    } catch { set({ isSubmitting: false }) }
  },
}))
