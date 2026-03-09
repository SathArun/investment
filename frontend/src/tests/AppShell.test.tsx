import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { AppShell } from '@/components/Layout/AppShell'

vi.mock('@/store/uiStore')

import { useUIStore } from '@/store/uiStore'

function mockUIStore(isSidebarCollapsed: boolean) {
  vi.mocked(useUIStore).mockImplementation(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (selector: (s: any) => any) =>
      selector({
        isSidebarCollapsed,
        toggleSidebar: vi.fn(),
        setSidebarCollapsed: vi.fn(),
        isClientView: false,
        selectedProduct: null,
        setSelectedProduct: vi.fn(),
      }),
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockUIStore(false)
})

describe('AppShell', () => {
  it('renders children in the main slot', () => {
    render(
      <AppShell sidebar={<div>Sidebar Content</div>}>
        <div>Main Content</div>
      </AppShell>,
    )
    expect(screen.getByText('Main Content')).toBeInTheDocument()
  })

  it('renders the sidebar slot', () => {
    render(
      <AppShell sidebar={<div>Sidebar Content</div>}>
        <div>Main Content</div>
      </AppShell>,
    )
    expect(screen.getByText('Sidebar Content')).toBeInTheDocument()
  })

  it('applies w-60 class when isSidebarCollapsed is false', () => {
    mockUIStore(false)
    const { container } = render(
      <AppShell sidebar={<div>Sidebar</div>}>
        <div>Content</div>
      </AppShell>,
    )
    const sidebarDiv = container.querySelector('.w-60')
    expect(sidebarDiv).toBeInTheDocument()
  })

  it('applies w-16 class when isSidebarCollapsed is true', () => {
    mockUIStore(true)
    const { container } = render(
      <AppShell sidebar={<div>Sidebar</div>}>
        <div>Content</div>
      </AppShell>,
    )
    const sidebarDiv = container.querySelector('.w-16')
    expect(sidebarDiv).toBeInTheDocument()
  })

  it('does not apply w-16 when isSidebarCollapsed is false', () => {
    mockUIStore(false)
    const { container } = render(
      <AppShell sidebar={<div>Sidebar</div>}>
        <div>Content</div>
      </AppShell>,
    )
    expect(container.querySelector('.w-16')).not.toBeInTheDocument()
  })

  it('does not apply w-60 when isSidebarCollapsed is true', () => {
    mockUIStore(true)
    const { container } = render(
      <AppShell sidebar={<div>Sidebar</div>}>
        <div>Content</div>
      </AppShell>,
    )
    expect(container.querySelector('.w-60')).not.toBeInTheDocument()
  })

  it('uses transition-[width] class (ADR-2 compliance)', () => {
    const { container } = render(
      <AppShell sidebar={<div>Sidebar</div>}>
        <div>Content</div>
      </AppShell>,
    )
    // transition-[width] renders as a class with brackets — check via className string
    const sidebarDiv = container.querySelector('.bg-gray-900')
    expect(sidebarDiv?.className).toContain('transition-[width]')
    expect(sidebarDiv?.className).not.toContain('transition-all')
  })
})
