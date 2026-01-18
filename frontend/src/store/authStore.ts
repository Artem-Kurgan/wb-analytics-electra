import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authAPI } from '../api/auth'
import { User } from '../types/user'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  loadUser: () => Promise<void>
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        try {
          const response = await authAPI.login({ username: email, password })

          // Сохранить токен
          localStorage.setItem('access_token', response.access_token)

          // Загрузить данные пользователя
          const user = await authAPI.getCurrentUser()

          set({
            user,
            token: response.access_token,
            isAuthenticated: true
          })
        } catch (error) {
          throw error
        }
      },

      logout: async () => {
        try {
          await authAPI.logout()
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          localStorage.removeItem('access_token')
          set({ user: null, token: null, isAuthenticated: false })
        }
      },

      loadUser: async () => {
        const token = localStorage.getItem('access_token')
        if (!token) {
          set({ user: null, isAuthenticated: false })
          return
        }

        try {
          const user = await authAPI.getCurrentUser()
          set({ user, token, isAuthenticated: true })
        } catch (error) {
          localStorage.removeItem('access_token')
          set({ user: null, token: null, isAuthenticated: false })
        }
      },

      setUser: (user: User) => set({ user, isAuthenticated: true })
    }),
    { name: 'electra-auth-storage' }
  )
)
