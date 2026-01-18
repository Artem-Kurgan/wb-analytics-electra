export interface User {
  id: string | number;
  email: string;
  name: string;
  role: 'admin' | 'leader' | 'manager' | string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type?: string;
}
