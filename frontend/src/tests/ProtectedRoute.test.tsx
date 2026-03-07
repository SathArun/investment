import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ProtectedRoute } from '@/components/ProtectedRoute'

// Mock the auth store
const mockNavigate = vi.fn()
const mockInitFromStorage = vi.fn()
let mockAccessToken: string | null = null

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return { ...actual, useNavigate: () => mockNavigate }
})

type AuthState = { accessToken: string | null; initFromStorage: () => void }

vi.mock('@/store/authStore', () => ({
  useAuthStore: (selector: (s: AuthState) => unknown) =>
    selector({
      get accessToken() {
        return mockAccessToken
      },
      initFromStorage: mockInitFromStorage,
    }),
}))

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    mockAccessToken = null
  })

  it('renders children when accessToken is present in store', () => {
    mockAccessToken = 'valid-token'

    render(
      <MemoryRouter>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </MemoryRouter>
    )

    expect(screen.getByText('Protected Content')).toBeInTheDocument()
  })

  it('renders children when token exists only in localStorage', () => {
    localStorage.setItem('access_token', 'stored-token')
    mockAccessToken = null

    render(
      <MemoryRouter>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </MemoryRouter>
    )

    expect(screen.getByText('Protected Content')).toBeInTheDocument()
  })

  it('renders nothing and navigates to /login when no token anywhere', async () => {
    mockAccessToken = null

    const { container } = render(
      <MemoryRouter>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </MemoryRouter>
    )

    expect(container.firstChild).toBeNull()
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login', { replace: true })
    })
  })

  it('calls initFromStorage on mount', () => {
    mockAccessToken = 'valid-token'

    render(
      <MemoryRouter>
        <ProtectedRoute>
          <div>Content</div>
        </ProtectedRoute>
      </MemoryRouter>
    )

    expect(mockInitFromStorage).toHaveBeenCalled()
  })
})
