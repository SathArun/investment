import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { SidebarFooter } from '@/components/Layout/SidebarFooter'
import type { DataFreshness } from '@/types/product'

// ---------------------------------------------------------------------------
// Mock: react-router-dom
// ---------------------------------------------------------------------------

const mockNavigate = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// ---------------------------------------------------------------------------
// Mock: authStore
// ---------------------------------------------------------------------------

const mockLogout = vi.fn()
let mockAdvisor: { id: string; name: string; email: string } | null = null

vi.mock('@/store/authStore', () => ({
  useAuthStore: (selector: (s: {
    advisor: typeof mockAdvisor
    logout: typeof mockLogout
  }) => unknown) =>
    selector({
      get advisor() {
        return mockAdvisor
      },
      logout: mockLogout,
    }),
}))

// ---------------------------------------------------------------------------
// Mock: dashboardStore
// ---------------------------------------------------------------------------

let mockDataFreshness: DataFreshness | null = null

vi.mock('@/store/dashboardStore', () => ({
  useDashboardStore: (selector: (s: {
    dataFreshness: DataFreshness | null
  }) => unknown) =>
    selector({
      get dataFreshness() {
        return mockDataFreshness
      },
    }),
}))

// ---------------------------------------------------------------------------
// Mock: uiStore
// ---------------------------------------------------------------------------

let mockIsSidebarCollapsed = false

vi.mock('@/store/uiStore', () => ({
  useUIStore: (selector: (s: {
    isSidebarCollapsed: boolean
  }) => unknown) =>
    selector({
      get isSidebarCollapsed() {
        return mockIsSidebarCollapsed
      },
    }),
}))

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

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

beforeEach(() => {
  vi.clearAllMocks()
  mockAdvisor = null
  mockDataFreshness = null
  mockIsSidebarCollapsed = false
})

describe('SidebarFooter', () => {
  it('renders advisor name when advisor is set', () => {
    mockAdvisor = { id: '1', name: 'Priya Sharma', email: 'priya@firm.in' }

    render(<SidebarFooter />)

    expect(screen.getByText('Priya Sharma')).toBeInTheDocument()
    expect(screen.getByText('priya@firm.in')).toBeInTheDocument()
  })

  it('renders "Advisor" fallback when advisor is null', () => {
    mockAdvisor = null

    render(<SidebarFooter />)

    expect(screen.getByText('Advisor')).toBeInTheDocument()
  })

  it('sign out button calls logout and navigates to /login', () => {
    mockAdvisor = { id: '2', name: 'Ravi Kumar', email: 'ravi@firm.in' }

    render(<SidebarFooter />)

    const signOutButton = screen.getByRole('button', { name: /sign out/i })
    fireEvent.click(signOutButton)

    expect(mockLogout).toHaveBeenCalledOnce()
    expect(mockNavigate).toHaveBeenCalledWith('/login')
  })

  it('renders DataFreshnessBar when dataFreshness is non-null and sidebar is not collapsed', () => {
    mockAdvisor = { id: '3', name: 'Anita Desai', email: 'anita@firm.in' }
    mockDataFreshness = makeFreshness()
    mockIsSidebarCollapsed = false

    render(<SidebarFooter />)

    // DataFreshnessBar renders AMFI, Equity, NPS labels
    expect(screen.getByText(/AMFI/)).toBeInTheDocument()
    expect(screen.getByText(/Equity/)).toBeInTheDocument()
    expect(screen.getByText(/NPS/)).toBeInTheDocument()
  })

  it('does not render DataFreshnessBar when sidebar is collapsed', () => {
    mockAdvisor = { id: '4', name: 'Suresh Patel', email: 'suresh@firm.in' }
    mockDataFreshness = makeFreshness()
    mockIsSidebarCollapsed = true

    render(<SidebarFooter />)

    expect(screen.queryByText(/AMFI/)).not.toBeInTheDocument()
  })

  it('does not render DataFreshnessBar when dataFreshness is null', () => {
    mockAdvisor = { id: '5', name: 'Meera Nair', email: 'meera@firm.in' }
    mockDataFreshness = null
    mockIsSidebarCollapsed = false

    render(<SidebarFooter />)

    expect(screen.queryByText(/AMFI/)).not.toBeInTheDocument()
  })

  it('hides advisor name and email text when sidebar is collapsed', () => {
    mockAdvisor = { id: '6', name: 'Deepak Joshi', email: 'deepak@firm.in' }
    mockIsSidebarCollapsed = true

    render(<SidebarFooter />)

    expect(screen.queryByText('Deepak Joshi')).not.toBeInTheDocument()
    expect(screen.queryByText('deepak@firm.in')).not.toBeInTheDocument()
  })
})
