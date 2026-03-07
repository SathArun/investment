import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ProductPins } from '@/components/Presentation/ProductPins'

// Mock ShareWhatsApp to avoid rendering complexity
vi.mock('@/components/Presentation/ShareWhatsApp', () => ({
  ShareWhatsApp: ({ pdfUrl }: { pdfUrl: string }) => (
    <a href={pdfUrl} data-testid="whatsapp-share">Share on WhatsApp</a>
  ),
}))

// Mock apiClient
const mockPost = vi.fn()
vi.mock('@/api/client', () => ({
  default: { post: (...args: unknown[]) => mockPost(...args) },
}))

type Product = { id: string; name: string; advisor_score: number }
type DashboardState = { products: Product[]; pinnedProducts: Set<string | number> }

// Mock dashboard store
let mockProducts: Product[] = []
let mockPinnedProducts: Set<string | number> = new Set()
vi.mock('@/store/dashboardStore', () => ({
  useDashboardStore: (selector: (s: DashboardState) => unknown) =>
    selector({
      get products() {
        return mockProducts
      },
      get pinnedProducts() {
        return mockPinnedProducts
      },
    }),
}))

// Mock filter store
let mockTaxBracket = 0.3
type FilterState = { taxBracket: number }
vi.mock('@/store/filterStore', () => ({
  useFilterStore: (selector: (s: FilterState) => unknown) =>
    selector({
      get taxBracket() {
        return mockTaxBracket
      },
    }),
}))

const MOCK_PRODUCTS = [
  { id: 'p1', name: 'SBI Bluechip Fund', advisor_score: 80 },
  { id: 'p2', name: 'HDFC Mid Cap Fund', advisor_score: 75 },
]

function setupStore(pinnedIds: string[] = []) {
  mockProducts = MOCK_PRODUCTS
  mockPinnedProducts = new Set(pinnedIds)
  mockTaxBracket = 0.3
}

describe('ProductPins', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockProducts = []
    mockPinnedProducts = new Set()
    mockTaxBracket = 0.3
    globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
    globalThis.URL.revokeObjectURL = vi.fn()
    globalThis.open = vi.fn()
  })

  it('shows empty state message when nothing is pinned', () => {
    setupStore([])
    render(<ProductPins />)
    expect(screen.getByText(/Pin products from the table/i)).toBeInTheDocument()
  })

  it('shows pinned product names', () => {
    setupStore(['p1', 'p2'])
    render(<ProductPins />)
    expect(screen.getByText('SBI Bluechip Fund')).toBeInTheDocument()
    expect(screen.getByText('HDFC Mid Cap Fund')).toBeInTheDocument()
  })

  it('button is disabled when no products are pinned', () => {
    setupStore([])
    render(<ProductPins />)
    expect(screen.getByRole('button', { name: /generate pdf report/i })).toBeDisabled()
  })

  it('shows warning and disables button when more than 5 products pinned', () => {
    setupStore(['p1', 'p2', 'p3', 'p4', 'p5', 'p6'])
    render(<ProductPins />)
    expect(screen.getByText(/Select 1/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /generate pdf report/i })).toBeDisabled()
  })

  it('shows counter as X/5', () => {
    setupStore(['p1', 'p2'])
    render(<ProductPins />)
    expect(screen.getByText(/Selected Products \(2\/5\)/i)).toBeInTheDocument()
  })

  it('calls apiClient.post and shows success message on PDF generation', async () => {
    setupStore(['p1'])
    const mockBlob = new Blob(['%PDF-fake'], { type: 'application/pdf' })
    mockPost.mockResolvedValueOnce({ data: mockBlob })

    render(<ProductPins />)
    fireEvent.click(screen.getByRole('button', { name: /generate pdf report/i }))

    await waitFor(() => {
      expect(screen.getByRole('status')).toHaveTextContent('PDF generated successfully!')
    })
    expect(mockPost).toHaveBeenCalledWith(
      '/pdf/client-report',
      expect.objectContaining({ product_ids: ['p1'], tax_bracket: 0.3 }),
      expect.objectContaining({ responseType: 'blob' })
    )
  })

  it('shows error message when PDF generation fails', async () => {
    setupStore(['p1'])
    mockPost.mockRejectedValueOnce(new Error('Network error'))

    render(<ProductPins />)
    fireEvent.click(screen.getByRole('button', { name: /generate pdf report/i }))

    await waitFor(() => {
      expect(screen.getByRole('status')).toHaveTextContent('PDF generation failed')
    })
  })

  it('shows WhatsApp share link after successful PDF generation', async () => {
    setupStore(['p1'])
    const mockBlob = new Blob(['%PDF-fake'], { type: 'application/pdf' })
    mockPost.mockResolvedValueOnce({ data: mockBlob })

    render(<ProductPins />)
    fireEvent.click(screen.getByRole('button', { name: /generate pdf report/i }))

    await waitFor(() => {
      expect(screen.getByTestId('whatsapp-share')).toBeInTheDocument()
    })
  })
})
