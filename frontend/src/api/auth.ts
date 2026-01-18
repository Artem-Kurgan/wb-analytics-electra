import client from './client'
import { LoginRequest, TokenResponse, User } from '../types/user'

export const authAPI = {
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await client.post<TokenResponse>('/v1/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  logout: async (): Promise<void> => {
    await client.post('/v1/auth/logout')
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await client.get<User>('/v1/auth/me')
    return response.data
  },

  refreshToken: async (): Promise<{ access_token: string }> => {
    const response = await client.post('/v1/auth/refresh')
    return response.data
  }
}
