import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { LoginPage } from '../pages/LoginPage';
import { AuthProvider } from '../context/AuthContext';
import { authService } from '../services/auth';

vi.mock('../services/auth', () => ({
  authService: {
    register: vi.fn(),
    login: vi.fn(),
    getMe: vi.fn(),
  },
}));

describe('LoginPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  const renderComponent = () =>
    render(
      <BrowserRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </BrowserRouter>
    );

  it('renders Welcome back screen matching visual reference', () => {
    renderComponent();

    expect(screen.getByText('SmartLearn.AI')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Welcome back' })).toBeInTheDocument();
    expect(
      screen.getByText('Please enter your details to sign in to your account')
    ).toBeInTheDocument();

    expect(screen.getByRole('tab', { name: 'Student' })).toHaveClass('active');
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();

    expect(screen.getByText(/Remember me/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Forgot password?' })).toBeInTheDocument();

    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign in with Google/i })).toBeInTheDocument();

    expect(screen.getByText(/Don't have an account\?/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Create account' })).toHaveAttribute('href', '/register');
  });

  it('validates empty inputs on submit', async () => {
    const user = userEvent.setup();
    renderComponent();

    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    expect(screen.getByText('Please enter your email address')).toBeInTheDocument();
    expect(screen.getByText('Please enter your password')).toBeInTheDocument();
    expect(authService.login).not.toHaveBeenCalled();
  });

  it('toggles password visibility when eye button is clicked', async () => {
    const user = userEvent.setup();
    renderComponent();

    const passwordInput = screen.getByLabelText('Password');
    expect(passwordInput).toHaveAttribute('type', 'password');

    const toggleBtn = screen.getByRole('button', { name: /Show password/i });
    await user.click(toggleBtn);

    expect(passwordInput).toHaveAttribute('type', 'text');

    const hideBtn = screen.getByRole('button', { name: /Hide password/i });
    await user.click(hideBtn);

    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  it('shows informative message when Forgot password is clicked', async () => {
    const user = userEvent.setup();
    renderComponent();

    const forgotLink = screen.getByRole('link', { name: 'Forgot password?' });
    await user.click(forgotLink);

    expect(
      screen.getByText(/Self-service password recovery is coming soon/i)
    ).toBeInTheDocument();
  });

  it('shows informative message when Google sign-in is clicked', async () => {
    const user = userEvent.setup();
    renderComponent();

    const googleBtn = screen.getByRole('button', { name: /Sign in with Google/i });
    await user.click(googleBtn);

    expect(
      screen.getByText(/Sign in with Google will be enabled in a future release/i)
    ).toBeInTheDocument();
  });

  it('handles API error correctly and displays friendly alert', async () => {
    const user = userEvent.setup();
    vi.mocked(authService.login).mockRejectedValueOnce(
      new Error('Invalid email or password.')
    );

    renderComponent();

    await user.type(screen.getByLabelText(/Email Address/i), 'student@example.com');
    await user.type(screen.getByLabelText('Password'), 'WrongPassword!');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    await waitFor(() => {
      expect(screen.getByText('Invalid email or password.')).toBeInTheDocument();
    });
  });

  it('successfully logs in with valid credentials', async () => {
    const user = userEvent.setup();
    vi.mocked(authService.login).mockResolvedValueOnce({
      access_token: 'valid-jwt-token',
      token_type: 'bearer',
    });
    vi.mocked(authService.getMe).mockResolvedValueOnce({
      id: 1,
      email: 'student@example.com',
      full_name: 'Smart Student',
      role: 'student',
      is_active: true,
      is_onboarded: false,
      created_at: new Date().toISOString(),
    });

    renderComponent();

    await user.type(screen.getByLabelText(/Email Address/i), 'student@example.com');
    await user.type(screen.getByLabelText('Password'), 'CorrectPassword123!');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith({
        email: 'student@example.com',
        password: 'CorrectPassword123!',
      });
      expect(authService.getMe).toHaveBeenCalled();
    });
  });
});
