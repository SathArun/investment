import { create } from 'zustand'
import apiClient from '@/api/client'

interface Advisor {
  id: string
  name: string
  email: string
}

interface AuthState {
  advisor: Advisor | null
  accessToken: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  initFromStorage: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  advisor: null,
  accessToken: null,
  login: async (email, password) => {
    const { data } = await apiClient.post('/auth/login', { email, password })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    set({ advisor: data.advisor, accessToken: data.access_token })
  },
  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ advisor: null, accessToken: null })
  },
  initFromStorage: () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      set({ accessToken: token })
    }
  },
}))
