import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { useEffect, useState } from 'react'
import { Spin } from 'antd'

interface ProtectedRouteProps {
  children: React.ReactNode
  allowedRoles?: string[]
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { isAuthenticated, user, loadUser } = useAuthStore()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const init = async () => {
      await loadUser()
      setLoading(false)
    }
    init()
  }, [])

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Проверка роли
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return (
      <div style={{ padding: 50, textAlign: 'center' }}>
        <h1>403 - Доступ запрещен</h1>
        <p>У вас недостаточно прав для просмотра этой страницы</p>
      </div>
    )
  }

  return <>{children}</>
}
