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

describe('uiStore — sidebar / client view (existing)', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.resetModules()
  })

  it('isClientView defaults to false', async () => {
    const { useUIStore } = await import('../store/uiStore')
    expect(useUIStore.getState().isClientView).toBe(false)
  })

  it('toggleClientView flips isClientView', async () => {
    const { useUIStore } = await import('../store/uiStore')
    useUIStore.getState().toggleClientView()
    expect(useUIStore.getState().isClientView).toBe(true)
    useUIStore.getState().toggleClientView()
    expect(useUIStore.getState().isClientView).toBe(false)
  })

  it('selectedProduct defaults to null', async () => {
    const { useUIStore } = await import('../store/uiStore')
    expect(useUIStore.getState().selectedProduct).toBeNull()
  })
})

describe('uiStore — isDarkMode initial value', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.resetModules()
  })

  it('defaults to true when localStorage has no theme key', async () => {
    const { useUIStore } = await import('../store/uiStore')
    expect(useUIStore.getState().isDarkMode).toBe(true)
  })

  it('defaults to true when localStorage has theme = "dark"', async () => {
    localStorageMock.setItem('theme', 'dark')
    const { useUIStore } = await import('../store/uiStore')
    expect(useUIStore.getState().isDarkMode).toBe(true)
  })

  it('defaults to false when localStorage has theme = "light"', async () => {
    localStorageMock.setItem('theme', 'light')
    const { useUIStore } = await import('../store/uiStore')
    expect(useUIStore.getState().isDarkMode).toBe(false)
  })
})

describe('uiStore — toggleTheme', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.resetModules()
  })

  it('flips isDarkMode from true to false', async () => {
    const { useUIStore } = await import('../store/uiStore')
    useUIStore.setState({ isDarkMode: true })
    useUIStore.getState().toggleTheme()
    expect(useUIStore.getState().isDarkMode).toBe(false)
  })

  it('flips isDarkMode from false to true', async () => {
    const { useUIStore } = await import('../store/uiStore')
    useUIStore.setState({ isDarkMode: false })
    useUIStore.getState().toggleTheme()
    expect(useUIStore.getState().isDarkMode).toBe(true)
  })

  it('writes "light" to localStorage when flipping to light', async () => {
    const { useUIStore } = await import('../store/uiStore')
    useUIStore.setState({ isDarkMode: true })
    useUIStore.getState().toggleTheme()
    expect(localStorageMock.getItem('theme')).toBe('light')
  })

  it('writes "dark" to localStorage when flipping to dark', async () => {
    const { useUIStore } = await import('../store/uiStore')
    useUIStore.setState({ isDarkMode: false })
    useUIStore.getState().toggleTheme()
    expect(localStorageMock.getItem('theme')).toBe('dark')
  })
})
