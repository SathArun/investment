import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { Sidebar } from '@/components/Layout/Sidebar'

// ── store mocks ──────────────────────────────────────────────────────────────
vi.mock('@/store/uiStore')

import { useUIStore } from '@/store/uiStore'

const mockToggleSidebar = vi.fn()

const defaultUIState = {
  isSidebarCollapsed: false,
  toggleSidebar: mockToggleSidebar,
  isClientView: false,
  selectedProduct: null,
  setSelectedProduct: vi.fn(),
  setSidebarCollapsed: vi.fn(),
}

beforeEach(() => {
  vi.clearAllMocks()

  vi.mocked(useUIStore).mockImplementation(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (selector: (s: any) => any) => selector({ ...defaultUIState }),
  )
})

function renderSidebar() {
  return render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <Sidebar />
    </MemoryRouter>,
  )
}

describe('Sidebar', () => {
  it('shows nav labels when not collapsed', () => {
    renderSidebar()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Goal Planner')).toBeInTheDocument()
    expect(screen.getByText('Risk Profiler')).toBeInTheDocument()
    expect(screen.getByText('Scenarios')).toBeInTheDocument()
    expect(screen.getByText('System Health')).toBeInTheDocument()
  })

  it('hides nav labels when collapsed', () => {
    vi.mocked(useUIStore).mockImplementation(
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (selector: (s: any) => any) =>
        selector({ ...defaultUIState, isSidebarCollapsed: true }),
    )

    renderSidebar()

    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument()
    expect(screen.queryByText('Goal Planner')).not.toBeInTheDocument()
    expect(screen.queryByText('Risk Profiler')).not.toBeInTheDocument()
    expect(screen.queryByText('Scenarios')).not.toBeInTheDocument()
    expect(screen.queryByText('System Health')).not.toBeInTheDocument()
  })

  it('shows only Dashboard nav item when isClientView is true', () => {
    vi.mocked(useUIStore).mockImplementation(
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (selector: (s: any) => any) =>
        selector({ ...defaultUIState, isClientView: true }),
    )

    renderSidebar()

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.queryByText('Goal Planner')).not.toBeInTheDocument()
    expect(screen.queryByText('Risk Profiler')).not.toBeInTheDocument()
    expect(screen.queryByText('Scenarios')).not.toBeInTheDocument()
    expect(screen.queryByText('System Health')).not.toBeInTheDocument()
  })

  it('renders the collapse toggle button', () => {
    renderSidebar()
    expect(
      screen.getByRole('button', { name: 'Collapse sidebar' }),
    ).toBeInTheDocument()
  })

  it('calls toggleSidebar when collapse button is clicked', () => {
    renderSidebar()
    fireEvent.click(screen.getByRole('button', { name: 'Collapse sidebar' }))
    expect(mockToggleSidebar).toHaveBeenCalledOnce()
  })

  it('shows expand aria-label when sidebar is collapsed', () => {
    vi.mocked(useUIStore).mockImplementation(
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (selector: (s: any) => any) =>
        selector({ ...defaultUIState, isSidebarCollapsed: true }),
    )

    renderSidebar()

    expect(
      screen.getByRole('button', { name: 'Expand sidebar' }),
    ).toBeInTheDocument()
  })
})
