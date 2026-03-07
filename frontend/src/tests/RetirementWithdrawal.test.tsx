import { describe, it, expect, beforeAll } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { RetirementWithdrawal } from '@/components/ScenarioPlanner/RetirementWithdrawal'
import { simulateWithdrawal } from '@/utils/retirement'

class MockResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
;(globalThis as Record<string, unknown>).ResizeObserver = MockResizeObserver

beforeAll(() => {
  // ResizeObserver already mocked above
})

describe('RetirementWithdrawal', () => {
  it('renders all inputs', () => {
    render(<RetirementWithdrawal />)
    expect(screen.getByLabelText(/Initial Corpus/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Monthly Withdrawal/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Expected Return/i)).toBeInTheDocument()
  })

  it('shows validation error below 10 lakh', async () => {
    const user = userEvent.setup()
    render(<RetirementWithdrawal />)
    const corpusInput = screen.getByLabelText(/Initial Corpus/i)
    await user.clear(corpusInput)
    await user.type(corpusInput, '500000')
    expect(await screen.findByText(/Minimum corpus.*10 lakh/i)).toBeInTheDocument()
  })

  it('1 crore at 50K/month at 8% lasts 35+ years', () => {
    const result = simulateWithdrawal(10_000_000, 50_000, 0.08)
    expect(result.yearsLasted).toBeGreaterThanOrEqual(35)
  })

  it('increasing return rate extends corpus life', () => {
    // At 80K/month: 6% exhausts in ~17 years, 10% lasts the full 50 years
    const low = simulateWithdrawal(10_000_000, 80_000, 0.06)
    const high = simulateWithdrawal(10_000_000, 80_000, 0.10)
    expect(high.yearsLasted).toBeGreaterThan(low.yearsLasted)
  })

  it('100K/month withdrawal exhausts faster than 50K/month', () => {
    const slow = simulateWithdrawal(10_000_000, 50_000, 0.08)
    const fast = simulateWithdrawal(10_000_000, 100_000, 0.08)
    expect(fast.yearsLasted).toBeLessThan(slow.yearsLasted)
  })

  it('shows exhaustion message when corpus runs out', async () => {
    const user = userEvent.setup()
    render(<RetirementWithdrawal />)

    // Set a very high withdrawal (500K/month on 1 crore) to ensure exhaustion
    const withdrawalInput = screen.getByLabelText(/Monthly Withdrawal/i)
    await user.clear(withdrawalInput)
    await user.type(withdrawalInput, '500000')

    const warning = await screen.findByTestId('exhaustion-warning')
    expect(warning).toBeInTheDocument()
    expect(warning.textContent).toMatch(/exhausted/i)
  })
})
