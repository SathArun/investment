import { create } from 'zustand'
import type { ProductRow } from '@/types/product'

interface UIState {
  selectedProduct: ProductRow | null
  setSelectedProduct: (product: ProductRow | null) => void
  isClientView: boolean
  toggleClientView: () => void
}

export const useUIStore = create<UIState>((set) => ({
  selectedProduct: null,
  setSelectedProduct: (selectedProduct) => set({ selectedProduct }),
  isClientView: false,
  toggleClientView: () => set((state) => ({ isClientView: !state.isClientView })),
}))
