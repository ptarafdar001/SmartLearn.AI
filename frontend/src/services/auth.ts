import { apiClient } from './api';
import type { LoginRequest, RegisterRequest, TokenResponse, User } from '../types/auth';

export const authService = {
  async register(data: RegisterRequest): Promise<User> {
    return apiClient<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
      requiresAuth: false,
    });
  },

  async login(data: LoginRequest): Promise<TokenResponse> {
    return apiClient<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
      requiresAuth: false,
    });
  },

  async getMe(): Promise<User> {
    return apiClient<User>('/auth/me', {
      method: 'GET',
      requiresAuth: true,
    });
  },
};
