import { create } from 'zustand'
import type { ProductRow } from '@/types/product'

interface UIState {
  selectedProduct: ProductRow | null
  setSelectedProduct: (product: ProductRow | null) => void
  isClientView: boolean
  setClientView: (v: boolean) => void
  isSidebarCollapsed: boolean
  toggleSidebar: () => void
  setSidebarCollapsed: (v: boolean) => void
}

export const useUIStore = create<UIState>((set) => ({
  selectedProduct: null,
  setSelectedProduct: (selectedProduct) => set({ selectedProduct }),
  isClientView: false,
  setClientView: (isClientView) => set({ isClientView }),
  isSidebarCollapsed: typeof window !== 'undefined' && localStorage.getItem('sidebar_collapsed') === 'true',
  toggleSidebar: () => set((state) => {
    const next = !state.isSidebarCollapsed
    localStorage.setItem('sidebar_collapsed', String(next))
    return { isSidebarCollapsed: next }
  }),
  setSidebarCollapsed: (v: boolean) => {
    localStorage.setItem('sidebar_collapsed', String(v))
    set({ isSidebarCollapsed: v })
  },
}))
