import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ProductPinCard } from '@/components/Presentation/ProductPinCard'
import type { ProductRow } from '@/types/product'

const mockProduct: ProductRow = {
  id: 1,
  name: 'SBI Bluechip Fund',
  asset_class: 'Equity',
  sebi_risk_level: 4,
  cagr_1y: 0.152,
  cagr_3y: 0.125,
  cagr_5y: 0.118,
  cagr_10y: 0.102,
  post_tax_return_1y: 0.129,
  post_tax_return_3y: 0.106,
  post_tax_return_5y: 0.10,
  std_dev_3y: 0.185,
  sharpe_3y: 0.82,
  max_drawdown_5y: -0.224,
  expense_ratio: 0.0085,
  min_investment_inr: 500,
  liquidity_label: 'Same Day',
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

describe('ProductPinCard', () => {
  it('renders product name', () => {
    const onUnpin = vi.fn()
    render(<ProductPinCard product={mockProduct} onUnpin={onUnpin} />)
    expect(screen.getAllByText('SBI Bluechip Fund').length).toBeGreaterThan(0)
  })

  it('renders asset_class in a badge', () => {
    const onUnpin = vi.fn()
    render(<ProductPinCard product={mockProduct} onUnpin={onUnpin} />)
    expect(screen.getByText('Equity')).toBeInTheDocument()
  })

  it('shows green badge class for risk level 2 (Low to Moderate)', () => {
    const onUnpin = vi.fn()
    const lowRiskProduct = { ...mockProduct, sebi_risk_level: 2 }
    const { container } = render(<ProductPinCard product={lowRiskProduct} onUnpin={onUnpin} />)
    const riskSpan = container.querySelector('.bg-green-400')
    expect(riskSpan).toBeInTheDocument()
    expect(riskSpan).toHaveTextContent('Low to Moderate')
  })

  it('shows yellow badge class for risk level 3 (Moderate)', () => {
    const onUnpin = vi.fn()
    const moderateProduct = { ...mockProduct, sebi_risk_level: 3 }
    const { container } = render(<ProductPinCard product={moderateProduct} onUnpin={onUnpin} />)
    const riskSpan = container.querySelector('.bg-yellow-400')
    expect(riskSpan).toBeInTheDocument()
    expect(riskSpan).toHaveTextContent('Moderate')
  })

  it('shows orange badge class for risk level 4 (Moderately High)', () => {
    const onUnpin = vi.fn()
    const { container } = render(<ProductPinCard product={mockProduct} onUnpin={onUnpin} />)
    const riskSpan = container.querySelector('.bg-orange-400')
    expect(riskSpan).toBeInTheDocument()
    expect(riskSpan).toHaveTextContent('Moderately High')
  })

  it('shows red badge class for risk level 5 (High)', () => {
    const onUnpin = vi.fn()
    const veryHighProduct = { ...mockProduct, sebi_risk_level: 5 }
    const { container } = render(<ProductPinCard product={veryHighProduct} onUnpin={onUnpin} />)
    const riskSpan = container.querySelector('.bg-red-400')
    expect(riskSpan).toBeInTheDocument()
    expect(riskSpan).toHaveTextContent('High')
  })

  it('renders post_tax_return_3y as formatted percentage', () => {
    const onUnpin = vi.fn()
    render(<ProductPinCard product={mockProduct} onUnpin={onUnpin} />)
    // formatPct(0.106) => "10.60%"
    expect(screen.getByText(/10\.60%/)).toBeInTheDocument()
  })

  it('renders cagr_5y when not null', () => {
    const onUnpin = vi.fn()
    render(<ProductPinCard product={mockProduct} onUnpin={onUnpin} />)
    // formatPct(0.118) => "11.80%"
    expect(screen.getByText(/11\.80%/)).toBeInTheDocument()
  })

  it('does not render cagr_5y row when cagr_5y is null', () => {
    const onUnpin = vi.fn()
    const noFiveYProduct = { ...mockProduct, cagr_5y: null }
    render(<ProductPinCard product={noFiveYProduct} onUnpin={onUnpin} />)
    expect(screen.queryByText(/5Y CAGR/)).not.toBeInTheDocument()
  })

  it('clicking unpin button calls onUnpin with product.id', () => {
    const onUnpin = vi.fn()
    render(<ProductPinCard product={mockProduct} onUnpin={onUnpin} />)
    const unpinBtn = screen.getByRole('button', { name: `unpin-${mockProduct.id}` })
    fireEvent.click(unpinBtn)
    expect(onUnpin).toHaveBeenCalledOnce()
    expect(onUnpin).toHaveBeenCalledWith(mockProduct.id)
  })
})
