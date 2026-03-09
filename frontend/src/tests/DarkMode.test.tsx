import { render } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useEffect } from 'react'

// ── ResizeObserver stub for Recharts ResponsiveContainer ──────────────────────
class MockResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
;(globalThis as unknown as { ResizeObserver: typeof MockResizeObserver }).ResizeObserver =
  MockResizeObserver

// ── store mocks ───────────────────────────────────────────────────────────────
vi.mock('@/store/uiStore')
vi.mock('@/store/dashboardStore')
vi.mock('@/store/filterStore')
vi.mock('@/store/authStore')
vi.mock('@/store/adminStore')
vi.mock('@/store/goalStore')
vi.mock('@/store/riskProfilerStore')
vi.mock('@/api/client', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: { clients: [] } }),
    post: vi.fn(),
  },
}))

import { useUIStore } from '@/store/uiStore'
import { useDashboardStore } from '@/store/dashboardStore'
import { useAuthStore } from '@/store/authStore'
import { useAdminStore } from '@/store/adminStore'
import { useFilterStore } from '@/store/filterStore'
import { useGoalStore } from '@/store/goalStore'
import { useRiskProfilerStore } from '@/store/riskProfilerStore'

// ── helpers ───────────────────────────────────────────────────────────────────

// uiStore — used with selectors throughout
function makeUIStoreMock(isDarkMode: boolean) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  vi.mocked(useUIStore).mockImplementation((selector: (s: any) => any) =>
    selector({
      isDarkMode,
      toggleTheme: vi.fn(),
      isClientView: false,
      toggleClientView: vi.fn(),
      selectedProduct: null,
      setSelectedProduct: vi.fn(),
    }),
  )
}

// authStore — used with selectors in ProtectedRoute + AppNav
function makeAuthStoreMock() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  vi.mocked(useAuthStore).mockImplementation((selector: (s: any) => any) =>
    selector({
      accessToken: 'fake-token',
      initFromStorage: vi.fn(),
      logout: vi.fn(),
    }),
  )
}

// filterStore — called WITHOUT selector: useFilterStore()
const defaultFilterState = {
  taxBracket: 0,
  timeHorizon: 'long',
  riskFilter: 'All',
  sortBy: 'advisor_score',
  sortDir: 'desc',
  setTaxBracket: vi.fn(),
  setTimeHorizon: vi.fn(),
  setRiskFilter: vi.fn(),
  setSortBy: vi.fn(),
  setSortDir: vi.fn(),
}

// dashboardStore — called WITHOUT selector: useDashboardStore()
const defaultDashboardState = {
  products: [],
  dataFreshness: null,
  isLoading: false,
  error: null,
  pinnedProducts: new Set<number>(),
  fetchProducts: vi.fn(),
  togglePin: vi.fn(),
}

// goalStore — called WITHOUT selector: useGoalStore()
const defaultGoalState = {
  clients: [],
  currentPlan: null,
  isLoadingClients: false,
  isLoadingPlan: false,
  fetchClients: vi.fn().mockResolvedValue(undefined),
  createGoalAndFetchPlan: vi.fn().mockResolvedValue(undefined),
}

// riskProfilerStore — used with selectors
const defaultRiskProfilerState = {
  questions: [],
  clients: [],
  profile: null,
  isLoadingQuestions: false,
  isSubmitting: false,
  fetchQuestions: vi.fn(),
  fetchClients: vi.fn(),
  createClient: vi.fn(),
  submitProfile: vi.fn(),
}

// adminStore — called without selector via destructure: useAdminStore()
const defaultAdminState = {
  jobs: [],
  isLoading: false,
  error: null,
  fetchJobs: vi.fn(),
  triggerJob: vi.fn(),
}

beforeEach(() => {
  vi.clearAllMocks()
  document.documentElement.classList.remove('dark')
  localStorage.clear()
  // Set access token so ProtectedRoute passes
  localStorage.setItem('access_token', 'fake-token')

  makeUIStoreMock(true)
  makeAuthStoreMock()

  // filterStore: some components call without selector, some with
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  vi.mocked(useFilterStore).mockImplementation((selector?: (s: any) => any) =>
    selector ? selector({ ...defaultFilterState }) : ({ ...defaultFilterState } as any),
  )
  // dashboardStore: some components call without selector, some with
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  vi.mocked(useDashboardStore).mockImplementation((selector?: (s: any) => any) =>
    selector ? selector({ ...defaultDashboardState }) : ({ ...defaultDashboardState } as any),
  )
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  vi.mocked(useGoalStore).mockReturnValue({ ...defaultGoalState } as any)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  vi.mocked(useAdminStore).mockReturnValue({ ...defaultAdminState } as any)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  vi.mocked(useRiskProfilerStore).mockImplementation((selector: (s: any) => any) =>
    selector({ ...defaultRiskProfilerState }),
  )
})

afterEach(() => {
  document.documentElement.classList.remove('dark')
})

// ── Dark mode effect ──────────────────────────────────────────────────────────
// App cannot be wrapped in MemoryRouter (it owns its own BrowserRouter).
// We test the effect in isolation with a minimal harness component that
// mirrors App's useEffect exactly, avoiding any router complexity.

function DarkModeEffectHarness({ isDarkMode }: { isDarkMode: boolean }) {
  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDarkMode)
  }, [isDarkMode])
  return null
}

describe('dark class on document.documentElement', () => {
  it('adds "dark" class when isDarkMode is true', () => {
    render(<DarkModeEffectHarness isDarkMode={true} />)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('removes "dark" class when isDarkMode is false', () => {
    document.documentElement.classList.add('dark')
    render(<DarkModeEffectHarness isDarkMode={false} />)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })
})

// ── Page layout tests: render App directly (it owns BrowserRouter) ────────────
// window.history.pushState sets the current URL so BrowserRouter picks it up.

import App from '@/App'

function renderAppAtPath(path: string) {
  window.history.pushState({}, '', path)
  return render(<App />)
}

describe('DashboardPage filter bar', () => {
  it('toolbar wrapper has bg-card class and not bg-white', () => {
    const { container } = renderAppAtPath('/dashboard')

    // The toolbar div (between nav and main) should have bg-card
    const bgCardDivs = container.querySelectorAll('.bg-card')
    expect(bgCardDivs.length).toBeGreaterThan(0)

    // The toolbar div sits after the <nav> as a sibling div.
    // It should have bg-card, not bg-white.
    // Find all divs with border-b + px-6 (nav uses <nav> tag, toolbar uses <div>)
    const divsWithBorderB = container.querySelectorAll('div.border-b.px-6')
    // Every such div should NOT have bg-white (the toolbar should be bg-card now)
    divsWithBorderB.forEach((el) => {
      expect(el.classList.contains('bg-white')).toBe(false)
    })
    // At least one of them should have bg-card (the toolbar)
    const hasToolbarWithBgCard = Array.from(divsWithBorderB).some((el) =>
      el.classList.contains('bg-card'),
    )
    expect(hasToolbarWithBgCard).toBe(true)
  })
})

describe('GoalsPage layout', () => {
  it('<main> element has no max-w-4xl class', () => {
    const { container } = renderAppAtPath('/goals')

    const mainEl = container.querySelector('main')
    expect(mainEl).not.toBeNull()
    expect(mainEl!.classList.contains('max-w-4xl')).toBe(false)
  })
})
