import { render, screen, fireEvent, act, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { AssetTable, CLIENT_VIEW_COLUMNS } from '@/components/Dashboard/AssetTable'
import type { ProductRow, SortDir, TaxBracket, TimeHorizon, RiskFilter } from '@/types/product'

// ResizeObserver is required by Radix UI Popper (tooltip portal)
class MockResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
;(globalThis as unknown as { ResizeObserver: typeof MockResizeObserver }).ResizeObserver =
  MockResizeObserver

vi.mock('@/store/filterStore')
vi.mock('@/store/dashboardStore')

import { useFilterStore } from '@/store/filterStore'
import { useDashboardStore } from '@/store/dashboardStore'

const mockSetSortBy = vi.fn()
const mockSetSortDir = vi.fn()
const mockTogglePin = vi.fn()
const mockFetchProducts = vi.fn()

function makeProduct(overrides: Partial<ProductRow> = {}): ProductRow {
  return {
    id: 1,
    name: 'Test Fund A',
    asset_class: 'equity',
    sebi_risk_level: 3,
    cagr_1y: 0.12,
    cagr_3y: 0.10,
    cagr_5y: 0.09,
    cagr_10y: 0.11,
    post_tax_return_1y: 0.10,
    post_tax_return_3y: 0.085,
    post_tax_return_5y: 0.078,
    std_dev_3y: 0.15,
    sharpe_3y: 0.8,
    max_drawdown_5y: -0.25,
    expense_ratio: 0.01,
    min_investment_inr: 500,
    liquidity_label: "Same Day",
    advisor_score: 78.5,
    score_breakdown: {
      risk_adjusted: 20,
      tax_yield: 15,
      liquidity: 10,
      expense: 12,
      consistency: 11,
      goal_fit: 10,
    },
    ...overrides,
  }
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
  setSortBy: mockSetSortBy,
  setSortDir: mockSetSortDir,
}

const defaultDashboardState = {
  products: [] as ProductRow[],
  dataFreshness: null,
  isLoading: false,
  error: null,
  pinnedProducts: new Set<number>(),
  fetchProducts: mockFetchProducts,
  togglePin: mockTogglePin,
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(useFilterStore).mockReturnValue({ ...defaultFilterState })
  vi.mocked(useDashboardStore).mockReturnValue({ ...defaultDashboardState })
})

describe('AssetTable', () => {
  it('renders product rows', () => {
    const products = [
      makeProduct({ id: 1, name: 'Fund Alpha' }),
      makeProduct({ id: 2, name: 'Fund Beta' }),
      makeProduct({ id: 3, name: 'Fund Gamma' }),
    ]
    vi.mocked(useDashboardStore).mockReturnValue({
      ...defaultDashboardState,
      products,
    })

    render(<AssetTable />)

    expect(screen.getByText('Fund Alpha')).toBeInTheDocument()
    expect(screen.getByText('Fund Beta')).toBeInTheDocument()
    expect(screen.getByText('Fund Gamma')).toBeInTheDocument()
  })

  it('sorts by clicking column header', () => {
    const products = [makeProduct({ id: 1, name: 'Fund A' })]
    vi.mocked(useDashboardStore).mockReturnValue({
      ...defaultDashboardState,
      products,
    })

    render(<AssetTable />)

    // Click "3Y CAGR" header — different from current sortBy ('advisor_score')
    const header3y = screen.getByText('3Y CAGR')
    fireEvent.click(header3y)

    expect(mockSetSortBy).toHaveBeenCalledWith('cagr_3y')
    expect(mockSetSortDir).toHaveBeenCalledWith('desc')
  })

  it('toggles sortDir when clicking the current sort column', () => {
    vi.mocked(useFilterStore).mockReturnValue({
      ...defaultFilterState,
      sortBy: 'cagr_3y',
      sortDir: 'desc',
    })

    const products = [makeProduct({ id: 1 })]
    vi.mocked(useDashboardStore).mockReturnValue({
      ...defaultDashboardState,
      products,
    })

    render(<AssetTable />)

    const header3y = screen.getByText(/3Y CAGR/)
    fireEvent.click(header3y)

    expect(mockSetSortBy).not.toHaveBeenCalled()
    expect(mockSetSortDir).toHaveBeenCalledWith('asc')
  })

  it('null values render as dash', () => {
    const products = [makeProduct({ id: 1, name: 'Null Fund', cagr_3y: null })]
    vi.mocked(useDashboardStore).mockReturnValue({
      ...defaultDashboardState,
      products,
    })

    render(<AssetTable />)

    // There should be at least one "—" for the null cagr_3y
    const dashes = screen.getAllByText('—')
    expect(dashes.length).toBeGreaterThan(0)
  })

  it('hover tooltip shows extra fields', async () => {
    const products = [
      makeProduct({
        id: 1,
        name: 'Tooltip Fund',
        std_dev_3y: 0.15,
        expense_ratio: 0.01,
        cagr_10y: 0.11,
        max_drawdown_5y: -0.25,
        min_investment_inr: 500,
        liquidity_label: "Same Day",
      }),
    ]
    vi.mocked(useDashboardStore).mockReturnValue({
      ...defaultDashboardState,
      products,
    })

    render(<AssetTable />)

    // Get the Tooltip.Trigger element (the <tr>)
    const row = screen.getByText('Tooltip Fund').closest('tr')
    expect(row).not.toBeNull()

    // Radix Tooltip opens on pointer enter + focus; fire pointer events
    await act(async () => {
      fireEvent.pointerEnter(row!)
      fireEvent.pointerMove(row!)
    })

    // Wait for tooltip to appear (Radix uses a delay)
    await waitFor(
      () => {
        const stdDevElements = screen.getAllByText('Std Dev')
        expect(stdDevElements.length).toBeGreaterThan(0)
      },
      { timeout: 1000 }
    )

    expect(screen.getAllByText('Expense Ratio').length).toBeGreaterThan(0)
    expect(screen.getAllByText('10Y CAGR').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Max Drawdown').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Min Investment').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Liquidity').length).toBeGreaterThan(0)
  })

  it('client view hides score breakdown button', () => {
    const products = [makeProduct({ id: 1, name: 'Fund A' })]
    vi.mocked(useDashboardStore).mockReturnValue({
      ...defaultDashboardState,
      products,
    })

    render(<AssetTable isClientView={true} />)

    expect(screen.queryByRole('button', { name: /score-breakdown/ })).not.toBeInTheDocument()
  })

  it('score breakdown button visible when not client view', () => {
    const products = [makeProduct({ id: 1, name: 'Fund A' })]
    vi.mocked(useDashboardStore).mockReturnValue({
      ...defaultDashboardState,
      products,
    })

    render(<AssetTable isClientView={false} />)

    expect(screen.getByRole('button', { name: /score-breakdown-1/ })).toBeInTheDocument()
  })

  it('pin toggle calls togglePin with product id', () => {
    const products = [makeProduct({ id: 42, name: 'Fund Pin' })]
    vi.mocked(useDashboardStore).mockReturnValue({
      ...defaultDashboardState,
      products,
    })

    render(<AssetTable />)

    const pinButton = screen.getByLabelText('pin-42')
    fireEvent.click(pinButton)

    expect(mockTogglePin).toHaveBeenCalledWith(42)
  })

  it('shows skeleton rows when isLoading=true and products=[]', () => {
    vi.mocked(useDashboardStore).mockReturnValue({
      ...defaultDashboardState,
      isLoading: true,
      products: [],
    })

    render(<AssetTable />)

    // Skeleton elements are divs with the animate-pulse class from skeleton.tsx
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
    expect(screen.queryByText('No products available')).not.toBeInTheDocument()
  })

  it('shows "No products available" when isLoading=false and products=[]', () => {
    vi.mocked(useDashboardStore).mockReturnValue({
      ...defaultDashboardState,
      isLoading: false,
      products: [],
    })

    render(<AssetTable />)

    expect(screen.getByText('No products available')).toBeInTheDocument()
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBe(0)
  })

  it('CLIENT_VIEW_COLUMNS is exported and does not include advisor_score', () => {
    expect(CLIENT_VIEW_COLUMNS).toBeDefined()
    expect((CLIENT_VIEW_COLUMNS as readonly string[]).includes('advisor_score')).toBe(false)
    expect((CLIENT_VIEW_COLUMNS as readonly string[]).includes('name')).toBe(true)
  })

  it('client view hides Advisor Score column header', () => {
    const products = [makeProduct({ id: 1, name: 'Fund A' })]
    vi.mocked(useDashboardStore).mockReturnValue({
      ...defaultDashboardState,
      products,
    })

    render(<AssetTable isClientView={true} />)

    expect(screen.queryByText('Advisor Score')).not.toBeInTheDocument()
  })

  it('advisor view shows Advisor Score column header', () => {
    const products = [makeProduct({ id: 1, name: 'Fund A' })]
    vi.mocked(useDashboardStore).mockReturnValue({
      ...defaultDashboardState,
      products,
    })

    render(<AssetTable isClientView={false} />)

    expect(screen.getByText(/Advisor Score/)).toBeInTheDocument()
  })

  it('client view hides Breakdown column header', () => {
    const products = [makeProduct({ id: 1, name: 'Fund A' })]
    vi.mocked(useDashboardStore).mockReturnValue({
      ...defaultDashboardState,
      products,
    })

    render(<AssetTable isClientView={true} />)

    expect(screen.queryByText('Breakdown')).not.toBeInTheDocument()
  })

  it('advisor view shows Breakdown column header', () => {
    const products = [makeProduct({ id: 1, name: 'Fund A' })]
    vi.mocked(useDashboardStore).mockReturnValue({
      ...defaultDashboardState,
      products,
    })

    render(<AssetTable isClientView={false} />)

    expect(screen.getByText('Breakdown')).toBeInTheDocument()
  })
})
