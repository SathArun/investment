import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ScoreBreakdown } from '@/components/Dashboard/ScoreBreakdown'
import type { ProductRow } from '@/types/product'

// Mock the uiStore
vi.mock('@/store/uiStore')

import { useUIStore } from '@/store/uiStore'

const mockSetSelectedProduct = vi.fn()

const mockProduct: ProductRow = {
  id: 1,
  name: 'HDFC Mid-Cap Fund',
  asset_class: 'Equity',
  sebi_risk_level: 4,
  cagr_1y: 15.2,
  cagr_3y: 12.5,
  cagr_5y: 11.8,
  cagr_10y: 10.2,
  post_tax_return_1y: 12.9,
  post_tax_return_3y: 10.6,
  post_tax_return_5y: 10.0,
  std_dev: 18.5,
  sharpe_ratio: 0.82,
  max_drawdown: -22.4,
  expense_ratio: 0.85,
  min_investment: 500,
  liquidity_days: 3,
  advisor_score: 78.5,
  score_breakdown: {
    risk_adjusted: 82,
    tax_yield: 75,
    liquidity: 90,
    expense: 65,
    consistency: 70,
    goal_fit: 80,
  },
}

function mockStoreWith(selectedProduct: ProductRow | null) {
  vi.mocked(useUIStore).mockImplementation(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (selector: (s: any) => any) =>
      selector({
        selectedProduct,
        setSelectedProduct: mockSetSelectedProduct,
        isClientView: false,
        toggleClientView: vi.fn(),
      })
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockStoreWith(null)
})

describe('ScoreBreakdown', () => {
  it('panel closed when no product selected', () => {
    mockStoreWith(null)
    render(<ScoreBreakdown />)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('panel opens when product selected', () => {
    mockStoreWith(mockProduct)
    render(<ScoreBreakdown />)
    expect(screen.getByText('HDFC Mid-Cap Fund')).toBeInTheDocument()
  })

  it('shows all 6 sub-score labels', () => {
    mockStoreWith(mockProduct)
    render(<ScoreBreakdown />)
    expect(screen.getByText('Risk-Adjusted Return')).toBeInTheDocument()
    expect(screen.getByText('Tax Efficiency')).toBeInTheDocument()
    expect(screen.getByText('Liquidity')).toBeInTheDocument()
    expect(screen.getByText('Low Expense')).toBeInTheDocument()
    expect(screen.getByText('Return Consistency')).toBeInTheDocument()
    expect(screen.getByText('Goal Fit')).toBeInTheDocument()
  })

  it('Escape closes panel', () => {
    mockStoreWith(mockProduct)
    render(<ScoreBreakdown />)
    fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' })
    expect(mockSetSelectedProduct).toHaveBeenCalledWith(null)
  })

  it('close button calls setSelectedProduct(null)', () => {
    mockStoreWith(mockProduct)
    render(<ScoreBreakdown />)
    const closeButton = screen.getByRole('button', { name: /close panel/i })
    fireEvent.click(closeButton)
    expect(mockSetSelectedProduct).toHaveBeenCalledWith(null)
  })
})
