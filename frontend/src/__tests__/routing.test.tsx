import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { authService } from '../services/auth';
import { onboardingService } from '../services/onboarding';
import { PublicOnlyRoute } from '../routes/PublicOnlyRoute';
import { ProtectedRoute } from '../routes/ProtectedRoute';
import { OnboardingRoute } from '../routes/OnboardingRoute';
import { RegisterPage } from '../pages/RegisterPage';
import { LoginPage } from '../pages/LoginPage';
import { OnboardingNavbar } from '../components/onboarding/OnboardingNavbar';
import { RootRedirect } from '../App';
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
    submitStep1: vi.fn(),
    submitStep2: vi.fn(),
  },
}));

const TestApp = ({ initialPath = '/' }: { initialPath?: string }) => (
  <MemoryRouter initialEntries={[initialPath]}>
    <AuthProvider>
      <Routes>
        {/* Public only routes */}
        <Route element={<PublicOnlyRoute />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>

        {/* Protected onboarding wizard routes */}
        <Route element={<OnboardingRoute />}>
          <Route
            path="/onboarding/step1"
            element={
              <div data-testid="onboarding-step1">
                <OnboardingNavbar />
                <div>Onboarding Step 1 Page</div>
              </div>
            }
          />
          <Route path="/onboarding/step2" element={<div data-testid="onboarding-step2">Onboarding Step 2 Page</div>} />
        </Route>

        {/* Protected authenticated routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<div data-testid="dashboard-page">Student Dashboard Page</div>} />
        </Route>

        {/* Root and fallback */}
        <Route path="/" element={<RootRedirect />} />
        <Route path="*" element={<RootRedirect />} />
      </Routes>
    </AuthProvider>
  </MemoryRouter>
);

describe('Application Routing & Onboarding Redirection Architecture', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('1. New registration + incomplete onboarding navigates to /onboarding/step1', async () => {
    const user = userEvent.setup();

    vi.mocked(authService.register).mockResolvedValueOnce({
      id: 101,
      email: 'newstudent@example.com',
      full_name: 'New Student',
      role: 'student',
      is_active: true,
      is_onboarded: false,
      created_at: new Date().toISOString(),
    });

    vi.mocked(authService.login).mockResolvedValueOnce({
      access_token: 'new-user-token',
      token_type: 'bearer',
    });

    vi.mocked(onboardingService.getOnboardingStatus).mockResolvedValueOnce({
      is_onboarded: false,
      step1_completed: false,
      step2_completed: false,
      step3_completed: false,
      step4_completed: false,
      current_step: 1,
    });

    render(<TestApp initialPath="/register" />);

    // Wait for form to mount
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Create your account' })).toBeInTheDocument();
    });

    // Fill registration form
    await user.type(screen.getByLabelText(/Full Name/i), 'New Student');
    await user.type(screen.getByLabelText(/Email Address/i), 'newstudent@example.com');
    await user.type(screen.getByLabelText('Password'), 'SecurePass123!');
    await user.click(screen.getByRole('checkbox'));

    await user.click(screen.getByRole('button', { name: 'Create Account' }));

    // Must navigate to /onboarding/step1 and NOT /dashboard
    await waitFor(() => {
      expect(screen.getByTestId('onboarding-step1')).toBeInTheDocument();
    });

    expect(screen.queryByTestId('dashboard-page')).not.toBeInTheDocument();
  });

  it('2. Existing authenticated user + incomplete onboarding is redirected to /onboarding/step1 from /dashboard', async () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'incomplete-user-jwt');

    vi.mocked(authService.getMe).mockResolvedValueOnce({
      id: 202,
      email: 'student_incomplete@example.com',
      full_name: 'Incomplete Student',
      role: 'student',
      is_active: true,
      is_onboarded: false,
      created_at: new Date().toISOString(),
    });

    vi.mocked(onboardingService.getOnboardingStatus).mockResolvedValueOnce({
      is_onboarded: false,
      step1_completed: false,
      step2_completed: false,
      step3_completed: false,
      step4_completed: false,
      current_step: 1,
    });

    render(<TestApp initialPath="/dashboard" />);

    await waitFor(() => {
      expect(screen.getByTestId('onboarding-step1')).toBeInTheDocument();
    });

    expect(screen.queryByTestId('dashboard-page')).not.toBeInTheDocument();
  });

  it('3. Authenticated user + completed onboarding is permitted on /dashboard', async () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'onboarded-user-jwt');

    vi.mocked(authService.getMe).mockResolvedValueOnce({
      id: 303,
      email: 'student_complete@example.com',
      full_name: 'Graduated Student',
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

    render(<TestApp initialPath="/dashboard" />);

    await waitFor(() => {
      expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
    });

    expect(screen.queryByTestId('onboarding-step1')).not.toBeInTheDocument();
  });

  it('4. Unauthenticated user visiting /dashboard is redirected to /login', async () => {
    render(<TestApp initialPath="/dashboard" />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Welcome back' })).toBeInTheDocument();
    });
    expect(screen.queryByTestId('dashboard-page')).not.toBeInTheDocument();
  });

  it('5. /register remains accessible when unauthenticated', async () => {
    render(<TestApp initialPath="/register" />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Create your account' })).toBeInTheDocument();
    });
  });

  it('6. No redirect loops: / route directs unauthenticated to /login, incomplete to /onboarding/step1, and complete to /dashboard', async () => {
    // 6a. Unauthenticated visiting /
    const { unmount: unmount1 } = render(<TestApp initialPath="/" />);
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Welcome back' })).toBeInTheDocument();
    });
    unmount1();

    // 6b. Authenticated incomplete visiting /
    localStorage.setItem(TOKEN_STORAGE_KEY, 'token-incomplete');
    vi.mocked(authService.getMe).mockResolvedValueOnce({
      id: 401,
      email: 'partial@example.com',
      full_name: 'Partial Student',
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

    const { unmount: unmount2 } = render(<TestApp initialPath="/" />);
    await waitFor(() => {
      expect(screen.getByTestId('onboarding-step1')).toBeInTheDocument();
    });
    unmount2();

    // 6c. Authenticated complete visiting /
    localStorage.setItem(TOKEN_STORAGE_KEY, 'token-complete');
    vi.mocked(authService.getMe).mockResolvedValueOnce({
      id: 402,
      email: 'finished@example.com',
      full_name: 'Finished Student',
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

    render(<TestApp initialPath="/" />);
    await waitFor(() => {
      expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
    });
  });

  it('7. Displays loading spinner while authentication and onboarding status are being determined', async () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'slow-resolving-token');

    let resolveGetMe: any;
    vi.mocked(authService.getMe).mockReturnValueOnce(
      new Promise((resolve) => {
        resolveGetMe = resolve;
      })
    );

    render(<TestApp initialPath="/dashboard" />);

    // While unresolved, spinner must be displayed and /dashboard should NOT be shown
    expect(document.querySelector('.btn-spinner')).toBeInTheDocument();
    expect(screen.queryByTestId('dashboard-page')).not.toBeInTheDocument();

    vi.mocked(onboardingService.getOnboardingStatus).mockResolvedValueOnce({
      is_onboarded: true,
      step1_completed: true,
      step2_completed: true,
      step3_completed: true,
      step4_completed: true,
      current_step: 5,
    });

    // Resolve auth inside act
    await act(async () => {
      resolveGetMe({
        id: 505,
        email: 'resolved@example.com',
        full_name: 'Resolved Student',
        role: 'student',
        is_active: true,
        is_onboarded: true,
        created_at: new Date().toISOString(),
      });
    });

    await waitFor(() => {
      expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
    });
  });

  it('8. Authenticated user on onboarding page can Sign Out, navigate to /login, and access /login and /register', async () => {
    const user = userEvent.setup();
    localStorage.setItem(TOKEN_STORAGE_KEY, 'user-jwt-onboarding');
    localStorage.setItem('smartlearn_onboarding_step1', JSON.stringify({ board: 'CBSE' }));

    vi.mocked(authService.getMe).mockResolvedValueOnce({
      id: 601,
      email: 'student_signout@example.com',
      full_name: 'Signout Student',
      role: 'student',
      is_active: true,
      is_onboarded: false,
      created_at: new Date().toISOString(),
    });

    vi.mocked(onboardingService.getOnboardingStatus).mockResolvedValueOnce({
      is_onboarded: false,
      step1_completed: false,
      step2_completed: false,
      step3_completed: false,
      step4_completed: false,
      current_step: 1,
    });

    const { unmount } = render(<TestApp initialPath="/onboarding/step1" />);

    // Wait for onboarding page and Sign Out button to appear
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Sign Out/i })).toBeInTheDocument();
    });

    // Click Sign Out
    await user.click(screen.getByRole('button', { name: /Sign Out/i }));

    // Verifications:
    // 1. Token and draft state removed from localStorage
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBeNull();
    expect(localStorage.getItem('smartlearn_onboarding_step1')).toBeNull();

    // 2. Navigated to /login and login screen renders normally
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Welcome back' })).toBeInTheDocument();
    });
    unmount();

    // 3. /register can also be opened normally after logout
    render(<TestApp initialPath="/register" />);
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Create your account' })).toBeInTheDocument();
    });
  });
});
