import { describe, it, expect, beforeEach, vi } from 'vitest'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value },
    clear: () => { store = {} },
  }
})()

Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock })

// Need to re-import store fresh for each test due to module caching
// Use vi.resetModules() approach

describe('uiStore sidebar state', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.resetModules()
  })

  it('isSidebarCollapsed defaults to false when localStorage is empty', async () => {
    const { useUIStore } = await import('../store/uiStore')
    const state = useUIStore.getState()
    expect(state.isSidebarCollapsed).toBe(false)
  })

  it('toggleSidebar flips isSidebarCollapsed', async () => {
    const { useUIStore } = await import('../store/uiStore')
    useUIStore.getState().toggleSidebar()
    expect(useUIStore.getState().isSidebarCollapsed).toBe(true)
    useUIStore.getState().toggleSidebar()
    expect(useUIStore.getState().isSidebarCollapsed).toBe(false)
  })

  it('setSidebarCollapsed sets the value', async () => {
    const { useUIStore } = await import('../store/uiStore')
    useUIStore.getState().setSidebarCollapsed(true)
    expect(useUIStore.getState().isSidebarCollapsed).toBe(true)
  })

  it('toggleSidebar writes to localStorage', async () => {
    const { useUIStore } = await import('../store/uiStore')
    useUIStore.getState().toggleSidebar()
    expect(localStorageMock.getItem('sidebar_collapsed')).toBe('true')
  })

  it('isSidebarCollapsed reads from localStorage on init', async () => {
    localStorageMock.setItem('sidebar_collapsed', 'true')
    const { useUIStore } = await import('../store/uiStore')
    expect(useUIStore.getState().isSidebarCollapsed).toBe(true)
  })
})
