import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { FilterSummary } from '@/components/Dashboard/FilterSummary'
import type { TaxBracket, TimeHorizon, RiskFilter } from '@/types/product'

vi.mock('@/store/filterStore')
vi.mock('@/store/uiStore')

import { useFilterStore } from '@/store/filterStore'
import { useUIStore } from '@/store/uiStore'

const mockSetClientView = vi.fn()

function mockFilterStore(overrides: Partial<{ taxBracket: TaxBracket; timeHorizon: TimeHorizon; riskFilter: RiskFilter }> = {}) {
  const state = {
    taxBracket: 0 as TaxBracket,
    timeHorizon: 'long' as TimeHorizon,
    riskFilter: 'All' as RiskFilter,
    ...overrides,
  }
  vi.mocked(useFilterStore).mockImplementation(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (selector: (s: any) => any) => selector(state),
  )
}

function mockUIStore() {
  vi.mocked(useUIStore).mockImplementation(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (selector: (s: any) => any) => selector({ setClientView: mockSetClientView }),
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockFilterStore()
  mockUIStore()
})

describe('FilterSummary', () => {
  it('shows taxBracket label "0% (No Tax)" when taxBracket is 0', () => {
    mockFilterStore({ taxBracket: 0 })
    render(<FilterSummary />)
    expect(screen.getByText('0% (No Tax)')).toBeInTheDocument()
  })

  it('shows taxBracket label "30%" when taxBracket is 0.3', () => {
    mockFilterStore({ taxBracket: 0.3 as TaxBracket })
    render(<FilterSummary />)
    expect(screen.getByText('30%')).toBeInTheDocument()
  })

  it('shows timeHorizon label "Long (7Y+)" when timeHorizon is "long"', () => {
    mockFilterStore({ timeHorizon: 'long' })
    render(<FilterSummary />)
    expect(screen.getByText('Long (7Y+)')).toBeInTheDocument()
  })

  it('shows timeHorizon label "Short (< 3Y)" when timeHorizon is "short"', () => {
    mockFilterStore({ timeHorizon: 'short' })
    render(<FilterSummary />)
    expect(screen.getByText('Short (< 3Y)')).toBeInTheDocument()
  })

  it('shows timeHorizon label "Medium (3–7Y)" when timeHorizon is "medium"', () => {
    mockFilterStore({ timeHorizon: 'medium' })
    render(<FilterSummary />)
    expect(screen.getByText('Medium (3–7Y)')).toBeInTheDocument()
  })

  it('shows riskFilter text "All"', () => {
    mockFilterStore({ riskFilter: 'All' })
    render(<FilterSummary />)
    expect(screen.getByText('All')).toBeInTheDocument()
  })

  it('shows riskFilter text "Conservative"', () => {
    mockFilterStore({ riskFilter: 'Conservative' })
    render(<FilterSummary />)
    expect(screen.getByText('Conservative')).toBeInTheDocument()
  })

  it('"Change filters" button is in the DOM', () => {
    render(<FilterSummary />)
    expect(screen.getByRole('button', { name: 'Change filters' })).toBeInTheDocument()
  })

  it('clicking "Change filters" calls setClientView(false)', () => {
    render(<FilterSummary />)
    fireEvent.click(screen.getByRole('button', { name: 'Change filters' }))
    expect(mockSetClientView).toHaveBeenCalledOnce()
    expect(mockSetClientView).toHaveBeenCalledWith(false)
  })
})
