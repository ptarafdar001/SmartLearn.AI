import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import React from 'react';
import { AuthProvider, useAuth } from '../context/AuthContext';
import { authService } from '../services/auth';
import { onboardingService } from '../services/onboarding';
import { TOKEN_STORAGE_KEY } from '../services/api';

vi.mock('../services/auth', () => ({
  authService: {
    register: vi.fn(),
    login: vi.fn(),
    getMe: vi.fn(),
  },
}));

vi.mock('../services/onboarding', () => ({
  onboardingService: {
    getOnboardingStatus: vi.fn(),
  },
}));

describe('AuthContext and useAuth Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <AuthProvider>{children}</AuthProvider>
  );

  it('initializes in unauthenticated state when no token in localStorage', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
  });

  it('restores authenticated user on mount when valid token exists', async () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'stored-jwt-token');

    vi.mocked(authService.getMe).mockResolvedValueOnce({
      id: 42,
      email: 'restored@example.com',
      full_name: 'Restored Student',
      role: 'student',
      is_active: true,
      is_onboarded: true,
      created_at: new Date().toISOString(),
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user?.email).toBe('restored@example.com');
    expect(result.current.token).toBe('stored-jwt-token');
  });

  it('clears token on mount if stored token is invalid/expired', async () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'expired-token');

    vi.mocked(authService.getMe).mockRejectedValueOnce(new Error('Token expired'));

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBeNull();
  });

  it('clears auth state and localStorage on logout', async () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'active-token');

    vi.mocked(authService.getMe).mockResolvedValueOnce({
      id: 1,
      email: 'logout@example.com',
      full_name: 'Logout Student',
      role: 'student',
      is_active: true,
      is_onboarded: false,
      created_at: new Date().toISOString(),
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true);
    });

    act(() => {
      result.current.logout();
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBeNull();
  });

  it('fetches onboarding status from backend on restore when token exists', async () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'valid-token');

    vi.mocked(authService.getMe).mockResolvedValueOnce({
      id: 10,
      email: 'student@example.com',
      full_name: 'Status Student',
      role: 'student',
      is_active: true,
      is_onboarded: false,
      created_at: new Date().toISOString(),
    });

    vi.mocked(onboardingService.getOnboardingStatus).mockResolvedValueOnce({
      is_onboarded: false,
      step1_completed: true,
      step2_completed: false,
      step3_completed: false,
      step4_completed: false,
      current_step: 2,
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.isOnboarded).toBe(false);
    expect(result.current.onboardingStatus?.current_step).toBe(2);
    expect(onboardingService.getOnboardingStatus).toHaveBeenCalled();
  });

  it('sets isOnboarded to true when backend confirms step 4 is completed', async () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'onboarded-token');

    vi.mocked(authService.getMe).mockResolvedValueOnce({
      id: 11,
      email: 'complete@example.com',
      full_name: 'Completed Student',
      role: 'student',
      is_active: true,
      is_onboarded: true,
      created_at: new Date().toISOString(),
    });

    vi.mocked(onboardingService.getOnboardingStatus).mockResolvedValueOnce({
      is_onboarded: true,
      step1_completed: true,
      step2_completed: true,
      step3_completed: true,
      step4_completed: true,
      current_step: 5,
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.isOnboarded).toBe(true);
  });
});
