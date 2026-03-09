import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
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
// Mock: uiStore — includes BOTH isSidebarCollapsed AND isDarkMode/toggleTheme
// ---------------------------------------------------------------------------

let mockIsSidebarCollapsed = false
let mockIsDarkMode = false
let mockToggleTheme = vi.fn()

vi.mock('@/store/uiStore', () => ({
  useUIStore: (selector: (s: {
    isSidebarCollapsed: boolean
    isDarkMode: boolean
    toggleTheme: () => void
  }) => unknown) =>
    selector({
      get isSidebarCollapsed() {
        return mockIsSidebarCollapsed
      },
      get isDarkMode() {
        return mockIsDarkMode
      },
      get toggleTheme() {
        return mockToggleTheme
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

function renderFooter() {
  return render(
    <MemoryRouter>
      <SidebarFooter />
    </MemoryRouter>,
  )
}

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

beforeEach(() => {
  vi.clearAllMocks()
  mockAdvisor = null
  mockDataFreshness = null
  mockIsSidebarCollapsed = false
  mockIsDarkMode = false
  mockToggleTheme = vi.fn()
})

// ---------------------------------------------------------------------------
// Tests — spec 003: advisor name, logout, DataFreshness, collapsed state
// ---------------------------------------------------------------------------

describe('SidebarFooter — advisor display', () => {
  it('renders advisor name when advisor is set', () => {
    mockAdvisor = { id: '1', name: 'Priya Sharma', email: 'priya@firm.in' }

    renderFooter()

    expect(screen.getByText('Priya Sharma')).toBeInTheDocument()
    expect(screen.getByText('priya@firm.in')).toBeInTheDocument()
  })

  it('renders "Advisor" fallback when advisor is null', () => {
    mockAdvisor = null

    renderFooter()

    expect(screen.getByText('Advisor')).toBeInTheDocument()
  })

  it('hides advisor name and email text when sidebar is collapsed', () => {
    mockAdvisor = { id: '6', name: 'Deepak Joshi', email: 'deepak@firm.in' }
    mockIsSidebarCollapsed = true

    renderFooter()

    expect(screen.queryByText('Deepak Joshi')).not.toBeInTheDocument()
    expect(screen.queryByText('deepak@firm.in')).not.toBeInTheDocument()
  })
})

describe('SidebarFooter — logout', () => {
  it('sign out button calls logout and navigates to /login', () => {
    mockAdvisor = { id: '2', name: 'Ravi Kumar', email: 'ravi@firm.in' }

    renderFooter()

    const signOutButton = screen.getByRole('button', { name: /sign out/i })
    fireEvent.click(signOutButton)

    expect(mockLogout).toHaveBeenCalledOnce()
    expect(mockNavigate).toHaveBeenCalledWith('/login')
  })
})

describe('SidebarFooter — DataFreshnessBar', () => {
  it('renders DataFreshnessBar when dataFreshness is non-null and sidebar is not collapsed', () => {
    mockAdvisor = { id: '3', name: 'Anita Desai', email: 'anita@firm.in' }
    mockDataFreshness = makeFreshness()
    mockIsSidebarCollapsed = false

    renderFooter()

    expect(screen.getByText(/AMFI/)).toBeInTheDocument()
    expect(screen.getByText(/Equity/)).toBeInTheDocument()
    expect(screen.getByText(/NPS/)).toBeInTheDocument()
  })

  it('does not render DataFreshnessBar when sidebar is collapsed', () => {
    mockAdvisor = { id: '4', name: 'Suresh Patel', email: 'suresh@firm.in' }
    mockDataFreshness = makeFreshness()
    mockIsSidebarCollapsed = true

    renderFooter()

    expect(screen.queryByText(/AMFI/)).not.toBeInTheDocument()
  })

  it('does not render DataFreshnessBar when dataFreshness is null', () => {
    mockAdvisor = { id: '5', name: 'Meera Nair', email: 'meera@firm.in' }
    mockDataFreshness = null
    mockIsSidebarCollapsed = false

    renderFooter()

    expect(screen.queryByText(/AMFI/)).not.toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// Tests — spec 004: theme toggle icon, aria-label, interaction, collapsed label
// ---------------------------------------------------------------------------

describe('SidebarFooter — theme toggle icon', () => {
  it('renders Moon icon (aria-label contains "light") when isDarkMode=true', () => {
    mockIsDarkMode = true
    renderFooter()
    expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument()
  })

  it('renders Sun icon (aria-label contains "dark") when isDarkMode=false', () => {
    mockIsDarkMode = false
    renderFooter()
    expect(screen.getByRole('button', { name: /switch to dark mode/i })).toBeInTheDocument()
  })
})

describe('SidebarFooter — aria-labels', () => {
  it('button has aria-label "Switch to light mode" when isDarkMode=true', () => {
    mockIsDarkMode = true
    renderFooter()
    const btn = screen.getByRole('button', { name: 'Switch to light mode' })
    expect(btn).toBeInTheDocument()
  })

  it('button has aria-label "Switch to dark mode" when isDarkMode=false', () => {
    mockIsDarkMode = false
    renderFooter()
    const btn = screen.getByRole('button', { name: 'Switch to dark mode' })
    expect(btn).toBeInTheDocument()
  })
})

describe('SidebarFooter — toggleTheme interaction', () => {
  it('clicking the theme button calls toggleTheme()', async () => {
    mockIsDarkMode = true
    renderFooter()
    const btn = screen.getByRole('button', { name: /switch to light mode/i })
    await userEvent.click(btn)
    expect(mockToggleTheme).toHaveBeenCalledOnce()
  })
})

describe('SidebarFooter — collapsed/expanded label', () => {
  it('shows no text label when isSidebarCollapsed=true', () => {
    mockIsDarkMode = true
    mockIsSidebarCollapsed = true
    renderFooter()
    expect(screen.queryByText('Dark')).not.toBeInTheDocument()
    expect(screen.queryByText('Light')).not.toBeInTheDocument()
  })

  it('shows text label "Dark" when isSidebarCollapsed=false and isDarkMode=true', () => {
    mockIsDarkMode = true
    mockIsSidebarCollapsed = false
    renderFooter()
    expect(screen.getByText('Dark')).toBeInTheDocument()
  })

  it('shows text label "Light" when isSidebarCollapsed=false and isDarkMode=false', () => {
    mockIsDarkMode = false
    mockIsSidebarCollapsed = false
    renderFooter()
    expect(screen.getByText('Light')).toBeInTheDocument()
  })
})
