import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { DataFreshnessBar } from '@/components/Dashboard/DataFreshness'
import type { DataFreshness } from '@/types/product'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Returns an ISO string 73 hours in the past (always stale: > 48 h threshold). */
function staleTimestamp(): string {
  return new Date(Date.now() - 73 * 60 * 60 * 1000).toISOString()
}

/** Returns an ISO string representing right now (always fresh: < 48 h threshold). */
function freshTimestamp(): string {
  return new Date().toISOString()
}

function makeFreshness(overrides: Partial<DataFreshness> = {}): DataFreshness {
  return {
    amfi: freshTimestamp(),
    equity: freshTimestamp(),
    nps: freshTimestamp(),
    ...overrides,
  }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('DataFreshnessBar', () => {
  it('renders AMFI, Equity, and NPS labels', () => {
    render(<DataFreshnessBar freshness={makeFreshness()} />)
    expect(screen.getByText(/AMFI/)).toBeInTheDocument()
    expect(screen.getByText(/Equity/)).toBeInTheDocument()
    expect(screen.getByText(/NPS/)).toBeInTheDocument()
  })

  it('shows ⚠ stale for a source with timestamp 72 hours ago', () => {
    render(
      <DataFreshnessBar
        freshness={makeFreshness({ amfi: staleTimestamp() })}
      />
    )
    // The component appends ' ⚠ stale' to the label span text when stale
    const amfiSpan = screen.getByText(/AMFI/)
    expect(amfiSpan.textContent).toMatch(/⚠ stale/)
  })

  it('shows no ⚠ stale warning for sources updated within 24 hours', () => {
    render(<DataFreshnessBar freshness={makeFreshness()} />)
    // None of the source spans should contain the stale warning
    const allText = screen.getByText(/AMFI/).closest('div')?.textContent ?? ''
    // Individual checks for each source
    expect(screen.getByText(/AMFI/).textContent).not.toMatch(/⚠ stale/)
    expect(screen.getByText(/Equity/).textContent).not.toMatch(/⚠ stale/)
    expect(screen.getByText(/NPS/).textContent).not.toMatch(/⚠ stale/)
    void allText // used to avoid unused-var lint
  })

  it('shows "N/A" for null timestamps', () => {
    render(
      <DataFreshnessBar
        freshness={{ amfi: null, equity: null, nps: null }}
      />
    )
    const naItems = screen.getAllByText(/N\/A/)
    expect(naItems).toHaveLength(3)
  })
})
