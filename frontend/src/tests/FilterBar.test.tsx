import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { FilterBar } from '@/components/Dashboard/FilterBar'
import type { TaxBracket, TimeHorizon, RiskFilter, SortDir } from '@/types/product'

// Mock the stores
vi.mock('@/store/filterStore')
vi.mock('@/store/dashboardStore')

import { useFilterStore } from '@/store/filterStore'
import { useDashboardStore } from '@/store/dashboardStore'

const mockFetchProducts = vi.fn()

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

beforeEach(() => {
  vi.clearAllMocks()

  vi.mocked(useFilterStore).mockReturnValue({ ...defaultFilterState })
  vi.mocked(useDashboardStore).mockReturnValue({
    products: [],
    dataFreshness: null,
    isLoading: false,
    error: null,
    fetchProducts: mockFetchProducts,
  })
})

describe('FilterBar', () => {
  it('renders all three filter dropdowns', () => {
    render(<FilterBar />)
    expect(screen.getByText('Tax Bracket')).toBeInTheDocument()
    expect(screen.getByText('Time Horizon')).toBeInTheDocument()
    expect(screen.getByText('Risk Filter')).toBeInTheDocument()
  })

  it('tax bracket change calls fetchProducts', () => {
    const setTaxBracket = vi.fn()
    vi.mocked(useFilterStore).mockReturnValue({
      ...defaultFilterState,
      setTaxBracket,
    })

    render(<FilterBar />)

    // Open the Tax Bracket dropdown trigger
    const triggers = screen.getAllByRole('combobox')
    fireEvent.click(triggers[0])

    // Select 30% option
    const option = screen.getByText('30%')
    fireEvent.click(option)

    expect(setTaxBracket).toHaveBeenCalledWith(0.3)
    expect(mockFetchProducts).toHaveBeenCalledWith(0.3, 'long', 'All')
  })

  it('time horizon change calls fetchProducts', () => {
    const setTimeHorizon = vi.fn()
    vi.mocked(useFilterStore).mockReturnValue({
      ...defaultFilterState,
      setTimeHorizon,
    })

    render(<FilterBar />)

    const triggers = screen.getAllByRole('combobox')
    fireEvent.click(triggers[1])

    const option = screen.getByText('Short (< 3Y)')
    fireEvent.click(option)

    expect(setTimeHorizon).toHaveBeenCalledWith('short')
    expect(mockFetchProducts).toHaveBeenCalledWith(0, 'short', 'All')
  })

  it('risk filter change does NOT call fetchProducts', () => {
    const setRiskFilter = vi.fn()
    vi.mocked(useFilterStore).mockReturnValue({
      ...defaultFilterState,
      setRiskFilter,
    })

    render(<FilterBar />)

    const triggers = screen.getAllByRole('combobox')
    fireEvent.click(triggers[2])

    const option = screen.getByText('Conservative')
    fireEvent.click(option)

    expect(setRiskFilter).toHaveBeenCalledWith('Conservative')
    expect(mockFetchProducts).not.toHaveBeenCalled()
  })

  it('banner visible when taxBracket > 0', () => {
    vi.mocked(useFilterStore).mockReturnValue({
      ...defaultFilterState,
      taxBracket: 0.3 as TaxBracket,
    })

    render(<FilterBar />)

    expect(screen.getByText(/Post-tax returns shown — FY2025-26 tax rules/)).toBeInTheDocument()
  })

  it('banner hidden when taxBracket is 0', () => {
    vi.mocked(useFilterStore).mockReturnValue({
      ...defaultFilterState,
      taxBracket: 0 as TaxBracket,
    })

    render(<FilterBar />)

    expect(screen.queryByText(/Post-tax returns shown/)).not.toBeInTheDocument()
  })
})
