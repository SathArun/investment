import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ProductPins } from '@/components/Presentation/ProductPins'
import { ShareWhatsApp } from '@/components/Presentation/ShareWhatsApp'

// ── store mocks ──────────────────────────────────────────────────────────────
vi.mock('@/store/uiStore')
vi.mock('@/store/dashboardStore')
vi.mock('@/store/filterStore')
vi.mock('@/api/client', () => ({ default: { post: vi.fn(), get: () => Promise.resolve({ data: { clients: [{ id: 1, name: 'Test Client' }] } }) } }))

import { useUIStore } from '@/store/uiStore'
import { useDashboardStore } from '@/store/dashboardStore'
import { useFilterStore } from '@/store/filterStore'
import apiClient from '@/api/client'

const mockIsClientView = { value: false }

const mockProducts = [
  { id: 1, name: 'Nifty 50 Index Fund', asset_class: 'Equity', sebi_risk_level: 5 },
  { id: 2, name: 'HDFC Corporate Bond', asset_class: 'Debt', sebi_risk_level: 3 },
]

const defaultDashboardState = {
  products: mockProducts,
  dataFreshness: null,
  isLoading: false,
  error: null,
  pinnedProducts: new Set<number>(),
  fetchProducts: vi.fn(),
  togglePin: vi.fn(),
}

beforeEach(() => {
  vi.clearAllMocks()
  mockIsClientView.value = false
  globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
  globalThis.URL.revokeObjectURL = vi.fn()

  vi.mocked(useUIStore).mockImplementation(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (selector: (s: any) => any) =>
      selector({
        isClientView: mockIsClientView.value,
        selectedProduct: null,
        setSelectedProduct: vi.fn(),
      }),
  )

  vi.mocked(useDashboardStore).mockImplementation(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (selector: (s: any) => any) =>
      selector({ ...defaultDashboardState }),
  )

  vi.mocked(useFilterStore).mockImplementation(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (selector: (s: any) => any) =>
      selector({ taxBracket: 0.3, timeHorizon: 'long', riskFilter: 'All' }),
  )
})

// ── ProductPins tests ────────────────────────────────────────────────────────
describe('ProductPins', () => {
  it('shows disabled PDF button when no products pinned', () => {
    render(<ProductPins />)
    const btn = screen.getByRole('button', { name: /Generate PDF Report/i })
    expect(btn).toBeDisabled()
  })

  it('shows validation error when > 5 products pinned', () => {
    vi.mocked(useDashboardStore).mockImplementation(
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (selector: (s: any) => any) =>
        selector({ ...defaultDashboardState, pinnedProducts: new Set([1, 2, 3, 4, 5, 6]) }),
    )
    render(<ProductPins />)
    expect(screen.getByText('Select 1–5 products')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Generate PDF Report/i })).toBeDisabled()
  })

  it('calls API with correct params on generate PDF', async () => {
    vi.mocked(useDashboardStore).mockImplementation(
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (selector: (s: any) => any) =>
        selector({
          ...defaultDashboardState,
          products: mockProducts,
          pinnedProducts: new Set([1, 2]),
        }),
    )

    const mockBlob = new Blob(['%PDF-1.4'], { type: 'application/pdf' })
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockBlob })

    // Mock URL.createObjectURL
    const mockUrl = 'blob:http://localhost/fake-pdf'
    globalThis.URL.createObjectURL = vi.fn(() => mockUrl)
    globalThis.open = vi.fn()

    render(<ProductPins />)
    // Wait for the client list to load (useEffect) so the button becomes enabled
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Generate PDF Report/i })).not.toBeDisabled()
    })
    fireEvent.click(screen.getByRole('button', { name: /Generate PDF Report/i }))

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith(
        '/pdf/client-report',
        expect.objectContaining({ client_id: 1, product_ids: expect.arrayContaining(['1', '2']), tax_bracket: 0.3 }),
        { responseType: 'blob' },
      )
    })
  })

  it('shows error message on PDF generation failure', async () => {
    vi.mocked(useDashboardStore).mockImplementation(
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (selector: (s: any) => any) =>
        selector({
          ...defaultDashboardState,
          products: mockProducts,
          pinnedProducts: new Set([1]),
        }),
    )
    vi.mocked(apiClient.post).mockRejectedValueOnce(new Error('Network error'))

    render(<ProductPins />)
    // Wait for the client list to load (useEffect) so the button becomes enabled
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Generate PDF Report/i })).not.toBeDisabled()
    })
    fireEvent.click(screen.getByRole('button', { name: /Generate PDF Report/i }))

    await waitFor(() => {
      expect(screen.getByRole('status')).toHaveTextContent('PDF generation failed')
    })
  })
})

// ── ShareWhatsApp tests ──────────────────────────────────────────────────────
describe('ShareWhatsApp', () => {
  it('constructs correct wa.me URL', () => {
    const pdfUrl = 'https://example.com/report.pdf'
    render(<ShareWhatsApp pdfUrl={pdfUrl} />)
    const link = screen.getByRole('link', { name: /Share via WhatsApp/i })
    expect(link).toHaveAttribute('href', expect.stringContaining('https://wa.me/?text='))
    expect(link).toHaveAttribute('href', expect.stringContaining(encodeURIComponent(pdfUrl)))
  })

  it('opens in a new tab', () => {
    render(<ShareWhatsApp pdfUrl="https://example.com/test.pdf" />)
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('target', '_blank')
  })
})
