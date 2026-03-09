import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ViewToggle } from '@/components/Presentation/ViewToggle'

vi.mock('@/store/uiStore')

import { useUIStore } from '@/store/uiStore'

const mockSetClientView = vi.fn()
const mockSetSidebarCollapsed = vi.fn()

function mockStore(isClientView: boolean) {
  vi.mocked(useUIStore).mockImplementation(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (selector: (s: any) => any) =>
      selector({
        isClientView,
        setClientView: mockSetClientView,
        setSidebarCollapsed: mockSetSidebarCollapsed,
      }),
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockStore(false)
})

describe('ViewToggle', () => {
  it('renders "Advisor View" and "Client View" labels', () => {
    render(<ViewToggle />)
    expect(screen.getByText('Advisor View')).toBeInTheDocument()
    expect(screen.getByText('Client View')).toBeInTheDocument()
  })

  it('"Advisor View" radio is checked when isClientView is false', () => {
    mockStore(false)
    render(<ViewToggle />)
    const advisorRadio = screen.getByRole('radio', { name: 'Advisor View' })
    const clientRadio = screen.getByRole('radio', { name: 'Client View' })
    expect(advisorRadio).toBeChecked()
    expect(clientRadio).not.toBeChecked()
  })

  it('"Client View" radio is checked when isClientView is true', () => {
    mockStore(true)
    render(<ViewToggle />)
    const advisorRadio = screen.getByRole('radio', { name: 'Advisor View' })
    const clientRadio = screen.getByRole('radio', { name: 'Client View' })
    expect(clientRadio).toBeChecked()
    expect(advisorRadio).not.toBeChecked()
  })

  it('clicking "Client View" radio calls setClientView(true) AND setSidebarCollapsed(true)', () => {
    mockStore(false)
    render(<ViewToggle />)
    fireEvent.click(screen.getByRole('radio', { name: 'Client View' }))
    expect(mockSetClientView).toHaveBeenCalledWith(true)
    expect(mockSetSidebarCollapsed).toHaveBeenCalledWith(true)
  })

  it('clicking "Advisor View" radio calls setClientView(false) and does NOT call setSidebarCollapsed', () => {
    mockStore(true)
    render(<ViewToggle />)
    fireEvent.click(screen.getByRole('radio', { name: 'Advisor View' }))
    expect(mockSetClientView).toHaveBeenCalledWith(false)
    expect(mockSetSidebarCollapsed).not.toHaveBeenCalled()
  })
})
