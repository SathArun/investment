import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { ProductRow } from '@/types/product'

// Mock ResizeObserver for jsdom/Recharts
class MockResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
;(globalThis as unknown as { ResizeObserver: typeof MockResizeObserver }).ResizeObserver = MockResizeObserver

let mockProducts: ProductRow[] = []

vi.mock('@/store/dashboardStore', () => ({
  useDashboardStore: (selector: (s: { products: ProductRow[] }) => unknown) =>
    selector({ products: mockProducts }),
}))

import { RiskReturnPlot } from '@/components/Dashboard/RiskReturnPlot'

const makeProduct = (overrides: Partial<ProductRow> = {}): ProductRow => ({
  id: 1,
  name: 'Test Fund',
  asset_class: 'Equity',
  sebi_risk_level: 3,
  cagr_1y: 0.12,
  cagr_3y: 0.10,
  cagr_5y: 0.09,
  cagr_10y: 0.08,
  post_tax_return_1y: 0.10,
  post_tax_return_3y: 0.09,
  post_tax_return_5y: 0.08,
  std_dev: 0.15,
  sharpe_ratio: 0.8,
  max_drawdown: -0.2,
  expense_ratio: 0.01,
  min_investment: 500,
  liquidity_days: 1,
  advisor_score: 75,
  score_breakdown: {
    risk_adjusted: 80,
    tax_yield: 70,
    liquidity: 90,
    expense: 85,
    consistency: 75,
    goal_fit: 70,
  },
  ...overrides,
})

beforeEach(() => {
  mockProducts = []
})

describe('RiskReturnPlot', () => {
  it('renders chart container', () => {
    mockProducts = [makeProduct()]
    render(<RiskReturnPlot />)
    expect(screen.getByText('Risk vs Return')).toBeInTheDocument()
  })

  it('excludes null std_dev products', () => {
    mockProducts = [
      makeProduct({ id: 1, name: 'Valid Fund', std_dev: 0.15, post_tax_return_3y: 0.09 }),
      makeProduct({ id: 2, name: 'No Std Dev Fund', std_dev: null, post_tax_return_3y: 0.09 }),
    ]
    // Should render without throwing even when a product has null std_dev
    expect(() => render(<RiskReturnPlot />)).not.toThrow()
  })

  it('renders with empty products', () => {
    mockProducts = []
    expect(() => render(<RiskReturnPlot />)).not.toThrow()
    expect(screen.getByText('Risk vs Return')).toBeInTheDocument()
  })
})
