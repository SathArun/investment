import { create } from 'zustand'
import apiClient from '@/api/client'

export interface RunRow {
  id: number
  started_at: string
  finished_at: string | null
  status: 'success' | 'failed' | 'running'
  duration_seconds: number | null
  rows_affected: number | null
  error_msg: string | null
}

export interface AdminJobSummary {
  job_name: string
  latest_status: 'success' | 'failed' | 'running' | 'never_run'
  latest_started_at: string | null
  latest_duration_seconds: number | null
  runs: RunRow[]
}

interface AdminState {
  jobs: AdminJobSummary[]
  isLoading: boolean
  error: string | null
  fetchJobs: () => Promise<void>
  triggerJob: (jobName: string) => Promise<void>
}

export const useAdminStore = create<AdminState>((set) => ({
  jobs: [],
  isLoading: false,
  error: null,
  fetchJobs: async () => {
    set({ isLoading: true })
    try {
      const { data } = await apiClient.get('/admin/jobs')
      set({ jobs: data.jobs, isLoading: false, error: null })
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
        ?? 'Failed to load job status. Is the backend running?'
      set({ isLoading: false, error: msg })
    }
  },
  triggerJob: async (jobName: string) => {
    try {
      await apiClient.post(`/admin/jobs/${jobName}/run`)
      const { data } = await apiClient.get('/admin/jobs')
      set({ jobs: data.jobs })
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } }
      if (axiosErr?.response?.status === 409) {
        set({ error: 'Job already running' })
      } else {
        const msg =
          axiosErr?.response?.data?.detail ?? 'Failed to trigger job'
        set({ error: msg })
      }
    }
  },
}))
