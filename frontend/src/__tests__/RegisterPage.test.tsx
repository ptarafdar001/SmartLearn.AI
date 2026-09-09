import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { RegisterPage } from '../pages/RegisterPage';
import { AuthProvider } from '../context/AuthContext';
import { authService } from '../services/auth';

vi.mock('../services/auth', () => ({
  authService: {
    register: vi.fn(),
    login: vi.fn(),
    getMe: vi.fn(),
  },
}));

describe('RegisterPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  const renderComponent = () =>
    render(
      <BrowserRouter>
        <AuthProvider>
          <RegisterPage />
        </AuthProvider>
      </BrowserRouter>
    );

  it('renders the Create your account form matching design elements', () => {
    renderComponent();

    expect(screen.queryByText(/STEP 1 OF 2/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Step 1 of 2 progress/i)).not.toBeInTheDocument();
    expect(screen.getByText('SmartLearn.AI')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Create your account' })).toBeInTheDocument();
    expect(screen.getByText("Get started with SmartLearn.AI's adaptive courses")).toBeInTheDocument();

    expect(screen.getByRole('tab', { name: 'Student' })).toHaveClass('active');
    expect(screen.getByRole('tab', { name: 'Teacher' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Parent' })).toBeInTheDocument();

    expect(screen.getByLabelText(/Full Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(
      screen.getByText(/I agree to the Terms of Service and Privacy Policy/i)
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create Account' })).toBeInTheDocument();
    expect(screen.getByText(/Already have an account\?/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Sign In' })).toHaveAttribute('href', '/login');
  });

  it('validates required fields on submit without input', async () => {
    const user = userEvent.setup();
    renderComponent();

    const submitBtn = screen.getByRole('button', { name: 'Create Account' });
    await user.click(submitBtn);

    expect(screen.getByText('Please enter your full name')).toBeInTheDocument();
    expect(screen.getByText('Please enter your email address')).toBeInTheDocument();
    expect(screen.getByText('Please enter a password')).toBeInTheDocument();
    expect(
      screen.getByText('You must agree to the Terms of Service and Privacy Policy')
    ).toBeInTheDocument();
    expect(authService.register).not.toHaveBeenCalled();
  });

  it('validates password length of at least 8 characters', async () => {
    const user = userEvent.setup();
    renderComponent();

    await user.type(screen.getByLabelText(/Full Name/i), 'Test Student');
    await user.type(screen.getByLabelText(/Email Address/i), 'student@example.com');
    await user.type(screen.getByLabelText('Password'), 'short');
    await user.click(screen.getByRole('checkbox'));

    await user.click(screen.getByRole('button', { name: 'Create Account' }));

    expect(
      screen.getByText('Password must be at least 8 characters long')
    ).toBeInTheDocument();
    expect(authService.register).not.toHaveBeenCalled();
  });

  it('validates invalid email format', async () => {
    const user = userEvent.setup();
    renderComponent();

    await user.type(screen.getByLabelText(/Full Name/i), 'Test Student');
    await user.type(screen.getByLabelText(/Email Address/i), 'invalid-email-format');
    await user.type(screen.getByLabelText('Password'), 'ValidPass123!');
    await user.click(screen.getByRole('checkbox'));

    await user.click(screen.getByRole('button', { name: 'Create Account' }));

    expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
    expect(authService.register).not.toHaveBeenCalled();
  });

  it('shows informational message when non-student role is clicked', async () => {
    const user = userEvent.setup();
    renderComponent();

    const teacherTab = screen.getByRole('tab', { name: 'Teacher' });
    await user.click(teacherTab);

    expect(
      screen.getByText(/Teacher accounts are coming soon/i)
    ).toBeInTheDocument();
  });

  it('submits registration successfully when valid data is provided', async () => {
    const user = userEvent.setup();
    vi.mocked(authService.register).mockResolvedValueOnce({
      id: 1,
      email: 'student@example.com',
      full_name: 'Test Student',
      role: 'student',
      is_active: true,
      is_onboarded: false,
      created_at: new Date().toISOString(),
    });
    vi.mocked(authService.login).mockResolvedValueOnce({
      access_token: 'mock-jwt-token',
      token_type: 'bearer',
    });
    vi.mocked(authService.getMe).mockResolvedValueOnce({
      id: 1,
      email: 'student@example.com',
      full_name: 'Test Student',
      role: 'student',
      is_active: true,
      is_onboarded: false,
      created_at: new Date().toISOString(),
    });

    renderComponent();

    await user.type(screen.getByLabelText(/Full Name/i), 'Test Student');
    await user.type(screen.getByLabelText(/Email Address/i), 'student@example.com');
    await user.type(screen.getByLabelText('Password'), 'ValidPassword123!');
    await user.click(screen.getByRole('checkbox'));

    await user.click(screen.getByRole('button', { name: 'Create Account' }));

    await waitFor(() => {
      expect(authService.register).toHaveBeenCalledWith({
        full_name: 'Test Student',
        email: 'student@example.com',
        password: 'ValidPassword123!',
        role: 'student',
        terms_accepted: true,
      });
    });
  });
});
