import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { OnboardingNavbar } from '../components/onboarding/OnboardingNavbar';
import { AuthProvider } from '../context/AuthContext';
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

describe('OnboardingNavbar Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders branding, support link, and Sign Out button', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <OnboardingNavbar />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('SmartLearn.AI')).toBeInTheDocument();
    expect(screen.getByText(/Need help\?/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Contact Support' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign Out' })).toBeInTheDocument();
  });

  it('triggers logout and clears localStorage token when Sign Out is clicked', async () => {
    const user = userEvent.setup();
    localStorage.setItem(TOKEN_STORAGE_KEY, 'active-test-jwt');
    localStorage.setItem('smartlearn_onboarding_step1', JSON.stringify({ board: 'ICSE' }));

    render(
      <BrowserRouter>
        <AuthProvider>
          <OnboardingNavbar />
        </AuthProvider>
      </BrowserRouter>
    );

    const signOutBtn = screen.getByRole('button', { name: 'Sign Out' });
    await user.click(signOutBtn);

    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBeNull();
    expect(localStorage.getItem('smartlearn_onboarding_step1')).toBeNull();
  });
});
