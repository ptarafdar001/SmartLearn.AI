export type UserRole = 'student' | 'teacher' | 'parent';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_onboarded: boolean;
  created_at: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
  terms_accepted: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface ApiErrorResponse {
  detail?: string | { msg?: string }[];
  message?: string;
}
