export interface User {
  id: number
  email: string
  name: string
  role: 'admin' | 'leader' | 'manager'
  allowed_tags?: string
  created_at: string
}
