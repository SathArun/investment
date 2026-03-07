import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { LoginForm } from '@/components/Login/LoginForm'
import { ProtectedRoute } from '@/components/ProtectedRoute'

const mockNavigate = vi.fn()
const mockLogin = vi.fn()
const mockInitFromStorage = vi.fn()
let mockAccessToken: string | null = null

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock('@/store/authStore', () => ({
  useAuthStore: (selector: (s: {
    login: typeof mockLogin
    initFromStorage: typeof mockInitFromStorage
    accessToken: string | null
  }) => unknown) =>
    selector({
      login: mockLogin,
      initFromStorage: mockInitFromStorage,
      get accessToken() {
        return mockAccessToken
      },
    }),
}))

beforeEach(() => {
  localStorage.clear()
  mockNavigate.mockReset()
  mockLogin.mockReset()
  mockInitFromStorage.mockReset()
  mockAccessToken = null
})

describe('LoginForm', () => {
  it('renders login form', () => {
    render(<LoginForm />)
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('shows error on invalid credentials', async () => {
    mockLogin.mockRejectedValueOnce(new Error('Unauthorized'))

    render(<LoginForm />)

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    })
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpassword' },
    })
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Invalid email or password')
    })
  })

  it('navigates to dashboard on success', async () => {
    mockLogin.mockResolvedValueOnce(undefined)

    render(<LoginForm />)

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'advisor@firm.com' },
    })
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'correctpassword' },
    })
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard')
    })
  })
})

describe('ProtectedRoute', () => {
  it('redirects to login when no token', async () => {
    mockAccessToken = null
    // No token in localStorage either

    render(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    )

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login', { replace: true })
    })
  })
})
