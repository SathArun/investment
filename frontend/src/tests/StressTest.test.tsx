import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { StressTest } from '@/components/ScenarioPlanner/StressTest'

vi.mock('@/api/client', () => ({ default: { get: vi.fn() } }))

import apiClient from '@/api/client'

// Recharts needs ResizeObserver
class MockResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
;(globalThis as Record<string, unknown>).ResizeObserver = MockResizeObserver

const MOCK_SCENARIOS = [
  {
    id: 'covid_2020',
    name: 'COVID-19 Crash (2020)',
    nifty50_drawdown_pct: -38.1,
    recovery_months: 8,
    description: 'Global pandemic-driven market crash',
  },
  {
    id: 'gfc_2008',
    name: 'Global Financial Crisis (2008-09)',
    nifty50_drawdown_pct: -60.9,
    recovery_months: 32,
    description: 'Lehman Brothers collapse triggered global recession',
  },
  {
    id: 'rate_hike_2022',
    name: 'Global Rate Hike Cycle (2022)',
    nifty50_drawdown_pct: -16.3,
    recovery_months: 5,
    description: 'Aggressive rate hikes by global central banks',
  },
  {
    id: 'demonetization_2016',
    name: 'Demonetisation Shock (2016)',
    nifty50_drawdown_pct: -14.9,
    recovery_months: 3,
    description: 'Sudden demonetisation of high-value currency notes',
  },
]

beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(apiClient.get).mockResolvedValue({ data: MOCK_SCENARIOS })
})

describe('StressTest', () => {
  it('renders loading then scenario cards', async () => {
    render(<StressTest />)

    // Loading state should appear first
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()

    // After loading, scenario cards should appear
    await waitFor(() => {
      expect(screen.getByTestId('scenario-card-covid_2020')).toBeInTheDocument()
    })

    expect(screen.getByTestId('scenario-card-gfc_2008')).toBeInTheDocument()
    expect(screen.getByTestId('scenario-card-rate_hike_2022')).toBeInTheDocument()
    expect(screen.getByTestId('scenario-card-demonetization_2016')).toBeInTheDocument()

    expect(screen.getByText('COVID-19 Crash (2020)')).toBeInTheDocument()
    expect(screen.getByText('Global Financial Crisis (2008-09)')).toBeInTheDocument()
  })

  it('100% equity COVID drawdown is -38.1%', async () => {
    render(<StressTest />)

    await waitFor(() => {
      expect(screen.getByTestId('scenario-card-covid_2020')).toBeInTheDocument()
    })

    // Default: equity=60, debt=30, gold=10
    // Set equity to 100, debt to 0, gold to 0
    const equitySlider = screen.getByLabelText('Equity percentage')
    const debtSlider = screen.getByLabelText('Debt percentage')
    const goldSlider = screen.getByLabelText('Gold percentage')

    fireEvent.change(equitySlider, { target: { value: '100' } })
    fireEvent.change(debtSlider, { target: { value: '0' } })
    fireEvent.change(goldSlider, { target: { value: '0' } })

    // drawdown = (100/100 * -38.1) + (0/100 * -38.1 * 0.2) + (0/100 * -38.1 * -0.1) = -38.1
    const drawdownEl = screen.getByTestId('drawdown-covid_2020')
    expect(drawdownEl.textContent).toBe('-38.1%')
  })

  it('mixed portfolio has lower drawdown than pure equity', async () => {
    render(<StressTest />)

    await waitFor(() => {
      expect(screen.getByTestId('scenario-card-covid_2020')).toBeInTheDocument()
    })

    // Default allocation: equity=60, debt=30, gold=10
    // drawdown = (0.6 * -38.1) + (0.3 * -38.1 * 0.2) + (0.1 * -38.1 * -0.1)
    //           = -22.86 + (-2.286) + 0.381 = -24.765
    // -24.765 > -38.1 (less severe = higher number)
    const drawdownEl = screen.getByTestId('drawdown-covid_2020')
    const drawdownValue = parseFloat(drawdownEl.textContent ?? '0')
    expect(drawdownValue).toBeGreaterThan(-38.1)
  })

  it('shows warning when allocation != 100%', async () => {
    render(<StressTest />)

    await waitFor(() => {
      expect(screen.getByTestId('scenario-card-covid_2020')).toBeInTheDocument()
    })

    // Default total is 60+30+10=100, no warning initially
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()

    // Change equity to 70 (total becomes 70+30+10=110)
    const equitySlider = screen.getByLabelText('Equity percentage')
    fireEvent.change(equitySlider, { target: { value: '70' } })

    // Warning should appear
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(screen.getByRole('alert').textContent).toBe('Allocations must total 100%')
  })

  it('recovery months shown for each scenario', async () => {
    render(<StressTest />)

    await waitFor(() => {
      expect(screen.getByTestId('scenario-card-covid_2020')).toBeInTheDocument()
    })

    // Verify recovery months for each scenario card
    expect(screen.getByTestId('recovery-covid_2020').textContent).toBe('8 months')
    expect(screen.getByTestId('recovery-gfc_2008').textContent).toBe('32 months')
    expect(screen.getByTestId('recovery-rate_hike_2022').textContent).toBe('5 months')
    expect(screen.getByTestId('recovery-demonetization_2016').textContent).toBe('3 months')
  })
})
