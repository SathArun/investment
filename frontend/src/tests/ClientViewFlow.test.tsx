import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ViewToggle } from '@/components/Presentation/ViewToggle'
import { FilterBar } from '@/components/Dashboard/FilterBar'
import { FilterSummary } from '@/components/Dashboard/FilterSummary'
import type { TaxBracket, TimeHorizon, RiskFilter, SortDir } from '@/types/product'

// ── store mocks ───────────────────────────────────────────────────────────────
vi.mock('@/store/uiStore')
vi.mock('@/store/filterStore')
vi.mock('@/store/dashboardStore')
vi.mock('@/api/client', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: {} })),
    post: vi.fn(() => Promise.resolve({ data: {} })),
  },
}))

import { useUIStore } from '@/store/uiStore'
import { useFilterStore } from '@/store/filterStore'
import { useDashboardStore } from '@/store/dashboardStore'

// ── shared mock state ─────────────────────────────────────────────────────────
const mockSetClientView = vi.fn()
const mockSetSidebarCollapsed = vi.fn()

// Mutable flag so we can simulate state transitions within a test
const uiState = { isClientView: false }

function setupUIStore() {
  vi.mocked(useUIStore).mockImplementation(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (selector: (s: any) => any) =>
      selector({
        isClientView: uiState.isClientView,
        setClientView: mockSetClientView,
        setSidebarCollapsed: mockSetSidebarCollapsed,
        selectedProduct: null,
        setSelectedProduct: vi.fn(),
        isSidebarCollapsed: false,
        toggleSidebar: vi.fn(),
      }),
  )
}

const defaultFilterState = {
  taxBracket: 0 as TaxBracket,
  timeHorizon: 'long' as TimeHorizon,
  riskFilter: 'All' as RiskFilter,
  sortBy: 'advisor_score',
  sortDir: 'desc' as SortDir,
  setTaxBracket: vi.fn(),
  setTimeHorizon: vi.fn(),
  setRiskFilter: vi.fn(),
  setSortBy: vi.fn(),
  setSortDir: vi.fn(),
}

// ── flexible mock helpers ─────────────────────────────────────────────────────
// FilterBar calls useFilterStore() with NO selector (full destructuring).
// FilterSummary calls useFilterStore((s) => s.field) WITH a selector.
// The mock must handle both: if called with a function, apply it; otherwise
// return the full state object.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function makeFlexibleFilterMock(state: typeof defaultFilterState): (selector?: (s: any) => any) => any {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return (selector?: (s: any) => any) => (typeof selector === 'function' ? selector(state) : state)
}

// useDashboardStore is only called by FilterBar (no selector), so mockReturnValue is fine.
const defaultDashboardState = {
  products: [],
  dataFreshness: null,
  isLoading: false,
  error: null,
  fetchProducts: vi.fn(),
  pinnedProducts: new Set<number>(),
  togglePin: vi.fn(),
}

beforeEach(() => {
  vi.clearAllMocks()
  uiState.isClientView = false
  setupUIStore()

  vi.mocked(useFilterStore).mockImplementation(
    makeFlexibleFilterMock({
      ...defaultFilterState,
      taxBracket: 0 as TaxBracket,
      timeHorizon: 'long' as TimeHorizon,
      riskFilter: 'All' as RiskFilter,
    }),
  )

  vi.mocked(useDashboardStore).mockReturnValue({ ...defaultDashboardState })
})

// ── helper: a minimal composite of the dual-audience feature ─────────────────
function DualAudiencePanel({ isClientView }: { isClientView: boolean }) {
  return (
    <div>
      <ViewToggle />
      {isClientView ? <FilterSummary /> : <FilterBar />}
    </div>
  )
}

// ── integration tests ─────────────────────────────────────────────────────────
describe('ClientViewFlow — advisor → client → advisor toggle', () => {
  it('initial state (advisor view): ViewToggle has "Advisor View" selected', () => {
    render(<DualAudiencePanel isClientView={false} />)
    const advisorRadio = screen.getByRole('radio', { name: 'Advisor View' })
    expect(advisorRadio).toBeChecked()
    const clientRadio = screen.getByRole('radio', { name: 'Client View' })
    expect(clientRadio).not.toBeChecked()
  })

  it('initial state (advisor view): FilterBar is rendered, FilterSummary is absent', () => {
    render(<DualAudiencePanel isClientView={false} />)
    // FilterBar renders these labels
    expect(screen.getByText('Tax Bracket')).toBeInTheDocument()
    expect(screen.getByText('Time Horizon')).toBeInTheDocument()
    expect(screen.getByText('Risk Filter')).toBeInTheDocument()
    // FilterSummary "Change filters" button must NOT be present
    expect(screen.queryByRole('button', { name: 'Change filters' })).not.toBeInTheDocument()
  })

  it('clicking "Client View" radio calls setClientView(true) and setSidebarCollapsed(true)', () => {
    render(<DualAudiencePanel isClientView={false} />)
    fireEvent.click(screen.getByRole('radio', { name: 'Client View' }))
    expect(mockSetClientView).toHaveBeenCalledOnce()
    expect(mockSetClientView).toHaveBeenCalledWith(true)
    expect(mockSetSidebarCollapsed).toHaveBeenCalledOnce()
    expect(mockSetSidebarCollapsed).toHaveBeenCalledWith(true)
  })

  it('client view: FilterSummary is rendered, FilterBar is absent', () => {
    // Re-configure store to reflect client view state
    uiState.isClientView = true
    setupUIStore()

    render(<DualAudiencePanel isClientView={true} />)
    // FilterSummary renders this button
    expect(screen.getByRole('button', { name: 'Change filters' })).toBeInTheDocument()
    // FilterBar labels must NOT be present
    expect(screen.queryByText('Tax Bracket')).not.toBeInTheDocument()
    expect(screen.queryByText('Time Horizon')).not.toBeInTheDocument()
    expect(screen.queryByText('Risk Filter')).not.toBeInTheDocument()
  })

  it('client view: ViewToggle shows "Client View" radio as checked', () => {
    uiState.isClientView = true
    setupUIStore()

    render(<DualAudiencePanel isClientView={true} />)
    expect(screen.getByRole('radio', { name: 'Client View' })).toBeChecked()
    expect(screen.getByRole('radio', { name: 'Advisor View' })).not.toBeChecked()
  })

  it('client view: FilterSummary shows current filter values from filterStore', () => {
    uiState.isClientView = true
    setupUIStore()

    vi.mocked(useFilterStore).mockImplementation(
      makeFlexibleFilterMock({
        ...defaultFilterState,
        taxBracket: 0.3 as TaxBracket,
        timeHorizon: 'short' as TimeHorizon,
        riskFilter: 'Conservative' as RiskFilter,
      }),
    )

    render(<DualAudiencePanel isClientView={true} />)
    expect(screen.getByText('30%')).toBeInTheDocument()
    expect(screen.getByText('Short (< 3Y)')).toBeInTheDocument()
    expect(screen.getByText('Conservative')).toBeInTheDocument()
  })

  it('clicking "Change filters" calls setClientView(false) to return to advisor view', () => {
    uiState.isClientView = true
    setupUIStore()

    render(<DualAudiencePanel isClientView={true} />)
    fireEvent.click(screen.getByRole('button', { name: 'Change filters' }))
    expect(mockSetClientView).toHaveBeenCalledOnce()
    expect(mockSetClientView).toHaveBeenCalledWith(false)
  })

  it('after "Change filters": advisor view re-renders FilterBar, FilterSummary gone', () => {
    // First render in client view
    uiState.isClientView = true
    setupUIStore()

    const { rerender } = render(<DualAudiencePanel isClientView={true} />)
    expect(screen.getByRole('button', { name: 'Change filters' })).toBeInTheDocument()

    // Simulate store transition back to advisor view
    uiState.isClientView = false
    setupUIStore()

    rerender(<DualAudiencePanel isClientView={false} />)

    expect(screen.queryByRole('button', { name: 'Change filters' })).not.toBeInTheDocument()
    expect(screen.getByText('Tax Bracket')).toBeInTheDocument()
    expect(screen.getByText('Time Horizon')).toBeInTheDocument()
  })

  it('clicking "Advisor View" radio calls setClientView(false) and does NOT call setSidebarCollapsed', () => {
    uiState.isClientView = true
    setupUIStore()

    render(<DualAudiencePanel isClientView={true} />)
    fireEvent.click(screen.getByRole('radio', { name: 'Advisor View' }))
    expect(mockSetClientView).toHaveBeenCalledWith(false)
    expect(mockSetSidebarCollapsed).not.toHaveBeenCalled()
  })
})
