import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'

interface Props {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: Props) {
  const navigate = useNavigate()
  const accessToken = useAuthStore((s) => s.accessToken)
  const initFromStorage = useAuthStore((s) => s.initFromStorage)

  useEffect(() => {
    initFromStorage()
  }, [initFromStorage])

  useEffect(() => {
    if (accessToken === null) {
      const token = localStorage.getItem('access_token')
      if (!token) {
        navigate('/login', { replace: true })
      }
    }
  }, [accessToken, navigate])

  const token = accessToken ?? localStorage.getItem('access_token')
  if (!token) return null

  return <>{children}</>
}
