import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import type { User, LoginRequest, RegisterRequest } from '../types/auth';
import type { OnboardingStatusResponse } from '../types/onboarding';
import { authService } from '../services/auth';
import { onboardingService } from '../services/onboarding';
import { getStoredToken, setStoredToken, removeStoredToken } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isOnboarded: boolean;
  onboardingStatus: OnboardingStatusResponse | null;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<User>;
  register: (data: RegisterRequest) => Promise<User>;
  logout: () => void;
  refreshUser: () => Promise<User | null>;
  checkOnboardingStatus: () => Promise<OnboardingStatusResponse | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(getStoredToken());
  const [isOnboarded, setIsOnboarded] = useState<boolean>(false);
  const [onboardingStatus, setOnboardingStatus] = useState<OnboardingStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshUser = useCallback(async (): Promise<User | null> => {
    const activeToken = getStoredToken();
    if (!activeToken) {
      setUser(null);
      setToken(null);
      setOnboardingStatus(null);
      setIsOnboarded(false);
      return null;
    }
    try {
      const userData = await authService.getMe();
      setUser(userData);
      setToken(activeToken);

      let onboarded = userData.is_onboarded;
      try {
        const statusData = await onboardingService.getOnboardingStatus();
        setOnboardingStatus(statusData);
        onboarded = statusData.is_onboarded;
      } catch {
        // Graceful fallback to user profile is_onboarded if status endpoint fails
      }
      setIsOnboarded(onboarded);

      return userData;
    } catch {
      removeStoredToken();
      setUser(null);
      setToken(null);
      setOnboardingStatus(null);
      setIsOnboarded(false);
      return null;
    }
  }, []);

  const checkOnboardingStatus = useCallback(async (): Promise<OnboardingStatusResponse | null> => {
    try {
      const statusData = await onboardingService.getOnboardingStatus();
      setOnboardingStatus(statusData);
      setIsOnboarded(statusData.is_onboarded);
      return statusData;
    } catch {
      return null;
    }
  }, []);

  useEffect(() => {
    const initAuth = async () => {
      setIsLoading(true);
      await refreshUser();
      setIsLoading(false);
    };
    initAuth();
  }, [refreshUser]);

  const login = async (credentials: LoginRequest): Promise<User> => {
    const tokenResponse = await authService.login(credentials);
    setStoredToken(tokenResponse.access_token);
    setToken(tokenResponse.access_token);
    const currentUser = await authService.getMe();

    let onboarded = currentUser.is_onboarded;
    try {
      const statusData = await onboardingService.getOnboardingStatus();
      setOnboardingStatus(statusData);
      onboarded = statusData.is_onboarded;
    } catch {
      // Graceful fallback
    }

    setUser(currentUser);
    setIsOnboarded(onboarded);
    return { ...currentUser, is_onboarded: onboarded };
  };

  const register = async (data: RegisterRequest): Promise<User> => {
    const newUser = await authService.register(data);
    // After registration, log the user in to issue a JWT token
    const tokenResponse = await authService.login({
      email: data.email,
      password: data.password,
    });
    setStoredToken(tokenResponse.access_token);
    setToken(tokenResponse.access_token);

    let onboarded = newUser.is_onboarded;
    try {
      const statusData = await onboardingService.getOnboardingStatus();
      setOnboardingStatus(statusData);
      onboarded = statusData.is_onboarded;
    } catch {
      // Graceful fallback
    }

    setUser(newUser);
    setIsOnboarded(onboarded);
    return { ...newUser, is_onboarded: onboarded };
  };

  const logout = () => {
    removeStoredToken();
    try {
      localStorage.removeItem('smartlearn_onboarding_step1');
    } catch {
      // Ignore storage cleanup errors
    }
    setUser(null);
    setToken(null);
    setOnboardingStatus(null);
    setIsOnboarded(false);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isOnboarded,
        onboardingStatus,
        isLoading,
        login,
        register,
        logout,
        refreshUser,
        checkOnboardingStatus,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

