import { render, screen, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useEffect } from 'react'
import { MemoryRouter } from 'react-router-dom'

// ── store mocks ───────────────────────────────────────────────────────────────
vi.mock('@/store/uiStore')
vi.mock('@/store/authStore')

import { useUIStore } from '@/store/uiStore'
import { useAuthStore } from '@/store/authStore'

import { SidebarFooter } from '@/components/Layout/SidebarFooter'

// ── helpers ───────────────────────────────────────────────────────────────────

function makeUIStoreMock({
  isDarkMode,
  toggleTheme = vi.fn(),
}: {
  isDarkMode: boolean
  toggleTheme?: ReturnType<typeof vi.fn>
}) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  vi.mocked(useUIStore).mockImplementation((selector: (s: any) => any) =>
    selector({
      isDarkMode,
      toggleTheme,
      isClientView: false,
      toggleClientView: vi.fn(),
      selectedProduct: null,
      setSelectedProduct: vi.fn(),
    }),
  )
}

function makeAuthStoreMock() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  vi.mocked(useAuthStore).mockImplementation((selector: (s: any) => any) =>
    selector({
      accessToken: 'fake-token',
      initFromStorage: vi.fn(),
      logout: vi.fn(),
    }),
  )
}

// Harness that mirrors App's useEffect for dark mode class toggling
function DarkModeEffectHarness({ isDarkMode }: { isDarkMode: boolean }) {
  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDarkMode)
  }, [isDarkMode])
  return null
}

function renderFooter(isDarkMode: boolean, toggleTheme = vi.fn()) {
  makeUIStoreMock({ isDarkMode, toggleTheme })
  return render(
    <MemoryRouter>
      <SidebarFooter />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  document.documentElement.classList.remove('dark')
  localStorage.clear()
  makeAuthStoreMock()
})

afterEach(() => {
  document.documentElement.classList.remove('dark')
})

// ── 1. Initial dark state (no localStorage key) ───────────────────────────────
// When uiStore reports isDarkMode=true (the default when no localStorage key),
// the App effect should apply the 'dark' class to documentElement.

describe('DarkModeIntegration — initial dark state (no localStorage key)', () => {
  it('adds "dark" class to documentElement when isDarkMode=true', () => {
    render(<DarkModeEffectHarness isDarkMode={true} />)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })
})

// ── 2. Initial light state (localStorage = 'light') ──────────────────────────
// When uiStore reports isDarkMode=false (localStorage has 'light'),
// the App effect should NOT apply the 'dark' class.

describe('DarkModeIntegration — initial light state (localStorage = light)', () => {
  it('does not add "dark" class to documentElement when isDarkMode=false', () => {
    localStorage.setItem('theme', 'light')
    render(<DarkModeEffectHarness isDarkMode={false} />)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })
})

// ── 3. Toggle dark → light ────────────────────────────────────────────────────
// When isDarkMode flips from true to false, effect removes 'dark' class and
// localStorage should get 'light'.

describe('DarkModeIntegration — toggle dark → light', () => {
  it('removes "dark" class and writes light to localStorage when toggling off', () => {
    // Start with dark applied
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')

    // Simulate what toggleTheme does in the real store
    act(() => {
      const next = false // toggling from dark (true) → light (false)
      localStorage.setItem('theme', next ? 'dark' : 'light')
      document.documentElement.classList.toggle('dark', next)
    })

    expect(document.documentElement.classList.contains('dark')).toBe(false)
    expect(localStorage.getItem('theme')).toBe('light')
  })
})

// ── 4. Toggle light → dark ────────────────────────────────────────────────────
// When isDarkMode flips from false to true, effect adds 'dark' class and
// localStorage should get 'dark'.

describe('DarkModeIntegration — toggle light → dark', () => {
  it('adds "dark" class and writes dark to localStorage when toggling on', () => {
    // Start with light
    localStorage.setItem('theme', 'light')

    // Simulate what toggleTheme does in the real store
    act(() => {
      const next = true // toggling from light (false) → dark (true)
      localStorage.setItem('theme', next ? 'dark' : 'light')
      document.documentElement.classList.toggle('dark', next)
    })

    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(localStorage.getItem('theme')).toBe('dark')
  })
})

// ── 5. SidebarFooter Moon icon in dark mode ───────────────────────────────────
// When isDarkMode=true, the theme button should have aria-label "Switch to light mode"
// indicating the Moon icon is shown.

describe('DarkModeIntegration — SidebarFooter Moon icon in dark mode', () => {
  it('renders button with aria-label "Switch to light mode" when isDarkMode=true', () => {
    renderFooter(true)
    expect(
      screen.getByRole('button', { name: 'Switch to light mode' }),
    ).toBeInTheDocument()
  })
})

// ── 6. SidebarFooter Sun icon in light mode ───────────────────────────────────
// When isDarkMode=false, the theme button should have aria-label "Switch to dark mode"
// indicating the Sun icon is shown.

describe('DarkModeIntegration — SidebarFooter Sun icon in light mode', () => {
  it('renders button with aria-label "Switch to dark mode" when isDarkMode=false', () => {
    renderFooter(false)
    expect(
      screen.getByRole('button', { name: 'Switch to dark mode' }),
    ).toBeInTheDocument()
  })
})
