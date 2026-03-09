import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ProductPins } from '@/components/Presentation/ProductPins'

// Mock ShareWhatsApp to avoid rendering complexity
vi.mock('@/components/Presentation/ShareWhatsApp', () => ({
  ShareWhatsApp: ({ pdfUrl }: { pdfUrl: string }) => (
    <a href={pdfUrl} data-testid="whatsapp-share">Share on WhatsApp</a>
  ),
}))

// Mock ProductPinCard to avoid Radix UI complexity in client-view tests
vi.mock('@/components/Presentation/ProductPinCard', () => ({
  ProductPinCard: ({ product }: { product: { id: string; name: string } }) => (
    <div data-testid={`pin-card-${product.id}`}>{product.name}</div>
  ),
}))

// Mock apiClient
const mockPost = vi.fn()
const mockGet = vi.fn()
vi.mock('@/api/client', () => ({
  default: {
    post: (...args: unknown[]) => mockPost(...args),
    get: (...args: unknown[]) => mockGet(...args),
  },
}))

type Product = { id: string; name: string; advisor_score: number }
type DashboardState = { products: Product[]; pinnedProducts: Set<string | number>; togglePin: (id: number) => void }

// Mock dashboard store
let mockProducts: Product[] = []
let mockPinnedProducts: Set<string | number> = new Set()
const mockTogglePin = vi.fn()
vi.mock('@/store/dashboardStore', () => ({
  useDashboardStore: (selector: (s: DashboardState) => unknown) =>
    selector({
      get products() {
        return mockProducts
      },
      get pinnedProducts() {
        return mockPinnedProducts
      },
      togglePin: mockTogglePin,
    }),
}))

// Mock filter store
let mockTaxBracket = 0.3
type FilterState = { taxBracket: number; timeHorizon: string }
vi.mock('@/store/filterStore', () => ({
  useFilterStore: (selector: (s: FilterState) => unknown) =>
    selector({
      get taxBracket() {
        return mockTaxBracket
      },
      timeHorizon: 'long',
    }),
}))

// Mock uiStore
let mockIsClientView = false
type UIState = { isClientView: boolean }
vi.mock('@/store/uiStore', () => ({
  useUIStore: (selector: (s: UIState) => unknown) =>
    selector({
      get isClientView() {
        return mockIsClientView
      },
    }),
}))

const MOCK_PRODUCTS = [
  { id: 'p1', name: 'SBI Bluechip Fund', advisor_score: 80 },
  { id: 'p2', name: 'HDFC Mid Cap Fund', advisor_score: 75 },
]

function setupStore(pinnedIds: string[] = [], clientView = false) {
  mockProducts = MOCK_PRODUCTS
  mockPinnedProducts = new Set(pinnedIds)
  mockTaxBracket = 0.3
  mockIsClientView = clientView
}

describe('ProductPins', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockProducts = []
    mockPinnedProducts = new Set()
    mockTaxBracket = 0.3
    mockIsClientView = false
    mockGet.mockResolvedValue({ data: { clients: [{ id: 'c1', name: 'Test Client' }] } })
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
    // Wait for the client list to load (useEffect) so the button becomes enabled
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /generate pdf report/i })).not.toBeDisabled()
    })
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
    // Wait for the client list to load (useEffect) so the button becomes enabled
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /generate pdf report/i })).not.toBeDisabled()
    })
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
    // Wait for the client list to load (useEffect) so the button becomes enabled
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /generate pdf report/i })).not.toBeDisabled()
    })
    fireEvent.click(screen.getByRole('button', { name: /generate pdf report/i }))

    await waitFor(() => {
      expect(screen.getByTestId('whatsapp-share')).toBeInTheDocument()
    })
  })

  // ── Client view tests ────────────────────────────────────────────────────

  it('client view: renders ProductPinCard for each pinned product', async () => {
    setupStore(['p1', 'p2'], true)
    render(<ProductPins />)
    await waitFor(() => {
      expect(screen.getByTestId('pin-card-p1')).toBeInTheDocument()
      expect(screen.getByTestId('pin-card-p2')).toBeInTheDocument()
      expect(screen.getByText('SBI Bluechip Fund')).toBeInTheDocument()
      expect(screen.getByText('HDFC Mid Cap Fund')).toBeInTheDocument()
    })
  })

  it('client view: shows empty state when no products are pinned', async () => {
    setupStore([], true)
    render(<ProductPins />)
    await waitFor(() => {
      expect(
        screen.getByText(/Pin products in Advisor View to build your comparison/i)
      ).toBeInTheDocument()
    })
  })

  it('client view: PDF and WhatsApp buttons are always visible (with pinned products)', async () => {
    setupStore(['p1'], true)
    render(<ProductPins />)
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /generate pdf report/i })).toBeInTheDocument()
    })
  })

  it('client view: PDF button is visible even with no pinned products', async () => {
    setupStore([], true)
    render(<ProductPins />)
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /generate pdf report/i })).toBeInTheDocument()
    })
  })

  it('client view: shows no clients warning when client list is empty', async () => {
    mockGet.mockResolvedValueOnce({ data: { clients: [] } })
    setupStore([], true)
    render(<ProductPins />)
    await waitFor(() => {
      expect(
        screen.getByText(/No clients found/i)
      ).toBeInTheDocument()
    })
  })
})
