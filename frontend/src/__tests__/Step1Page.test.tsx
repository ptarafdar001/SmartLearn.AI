import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter, MemoryRouter, Routes, Route } from 'react-router-dom';
import { Step1Page } from '../pages/onboarding/Step1Page';
import { OnboardingRoute } from '../routes/OnboardingRoute';
import { AuthProvider } from '../context/AuthContext';
import { onboardingService } from '../services/onboarding';
import { authService } from '../services/auth';

vi.mock('../services/onboarding', () => ({
  onboardingService: {
    submitStep1: vi.fn(),
    getOnboardingStatus: vi.fn(),
  },
}));

vi.mock('../services/auth', () => ({
  authService: {
    getMe: vi.fn(),
    login: vi.fn(),
    register: vi.fn(),
  },
}));

describe('Step1Page Component (Onboarding Step 1 of 4)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  const renderComponent = () =>
    render(
      <BrowserRouter>
        <AuthProvider>
          <Step1Page />
        </AuthProvider>
      </BrowserRouter>
    );

  it('1 & 2. Renders correctly and displays STEP 1 OF 4 progress header', () => {
    renderComponent();

    // Top navbar
    expect(screen.getByText('SmartLearn.AI')).toBeInTheDocument();
    expect(screen.getByText(/Need help\?/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Contact Support' })).toBeInTheDocument();

    // Step progress
    expect(screen.getByText(/STEP 1 OF 4: BOARD & CLASS/i)).toBeInTheDocument();
    expect(screen.getByText('25% Set Up')).toBeInTheDocument();

    // Headings
    expect(
      screen.getByRole('heading', { name: 'What board and class are you in?' })
    ).toBeInTheDocument();
    expect(
      screen.getByText(/We'll customize your syllabus and mock test series/i)
    ).toBeInTheDocument();
  });

  it('3. Initial Board selection is empty, all boards selectable', () => {
    renderComponent();

    expect(screen.getByText('Select Education Board')).toBeInTheDocument();
    const boards = ['CBSE', 'ICSE', 'State Board', 'ISC', 'Other'];
    for (const b of boards) {
      const btn = screen.getByRole('radio', { name: new RegExp(b, 'i') });
      expect(btn).toBeInTheDocument();
      expect(btn).not.toHaveClass('selected');
      expect(btn).toHaveAttribute('aria-checked', 'false');
    }
  });

  it('4. Initial Grade / Class selection is empty, all grades selectable', () => {
    renderComponent();

    expect(screen.getByText('Select Class / Grade')).toBeInTheDocument();
    const grades = [
      'Class 6',
      'Class 7',
      'Class 8',
      'Class 9',
      'Class 10',
      'Class 11',
      'Class 12',
    ];
    for (const g of grades) {
      const btn = screen.getByRole('radio', { name: g });
      expect(btn).toBeInTheDocument();
      expect(btn).not.toHaveClass('selected');
      expect(btn).toHaveAttribute('aria-checked', 'false');
    }
  });

  it('5. Step 1 has no stream selector even when senior secondary (Class 11 or 12) is selected', async () => {
    const user = userEvent.setup();
    renderComponent();

    // With no grade selected, stream selector is not rendered
    expect(screen.queryByText('Select Academic Stream')).not.toBeInTheDocument();

    // Select Class 11 -> stream selector must NOT appear on Step 1
    const class11Btn = screen.getByRole('radio', { name: 'Class 11' });
    await user.click(class11Btn);
    expect(screen.queryByText('Select Academic Stream')).not.toBeInTheDocument();

    // Select Class 12 -> stream selector must NOT appear on Step 1
    const class12Btn = screen.getByRole('radio', { name: 'Class 12' });
    await user.click(class12Btn);
    expect(screen.queryByText('Select Academic Stream')).not.toBeInTheDocument();
  });

  it('6. Validation: Continue cannot submit with empty selections', async () => {
    const user = userEvent.setup();
    renderComponent();

    // Attempt to submit with no selections
    await user.click(screen.getByRole('button', { name: /Continue/i }));
    expect(screen.getByText('Please select your education board.')).toBeInTheDocument();
    expect(onboardingService.submitStep1).not.toHaveBeenCalled();

    // Select a board, but no grade
    await user.click(screen.getByRole('radio', { name: /CBSE/i }));
    await user.click(screen.getByRole('button', { name: /Continue/i }));
    expect(screen.getByText('Please select your class / grade.')).toBeInTheDocument();
    expect(onboardingService.submitStep1).not.toHaveBeenCalled();
  });

  it('7. Submits correct payload to POST /api/v1/users/onboarding/step1 without stream for senior secondary', async () => {
    const user = userEvent.setup();
    vi.mocked(onboardingService.submitStep1).mockResolvedValueOnce({
      id: 1,
      user_id: 1,
      board: 'ICSE',
      grade: 'Class 12',
      academic_stream: null,
      created_at: new Date().toISOString(),
    });

    renderComponent();

    // Select ICSE
    await user.click(screen.getByRole('radio', { name: /ICSE/i }));

    // Select Class 12
    await user.click(screen.getByRole('radio', { name: 'Class 12' }));

    // Click Continue (no stream selection on Step 1)
    await user.click(screen.getByRole('button', { name: /Continue/i }));

    await waitFor(() => {
      expect(onboardingService.submitStep1).toHaveBeenCalledWith({
        board: 'ICSE',
        grade: 'Class 12',
        academic_stream: null,
      });
    });
  });

  it('8. Navigates to Step 2 on successful submission', async () => {
    const user = userEvent.setup();
    vi.mocked(onboardingService.submitStep1).mockResolvedValueOnce({
      id: 1,
      user_id: 1,
      board: 'CBSE',
      grade: 'Class 10',
      academic_stream: null,
      created_at: new Date().toISOString(),
    });

    render(
      <MemoryRouter initialEntries={['/onboarding/step1']}>
        <AuthProvider>
          <Routes>
            <Route path="/onboarding/step1" element={<Step1Page />} />
            <Route path="/onboarding/step2" element={<div>Step 2 Destination</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    // Select CBSE
    await user.click(screen.getByRole('radio', { name: /CBSE/i }));

    // Select Class 10 (no stream required)
    await user.click(screen.getByRole('radio', { name: 'Class 10' }));
    await user.click(screen.getByRole('button', { name: /Continue/i }));

    await waitFor(() => {
      expect(onboardingService.submitStep1).toHaveBeenCalledWith({
        board: 'CBSE',
        grade: 'Class 10',
        academic_stream: null,
      });
      expect(screen.getByText('Step 2 Destination')).toBeInTheDocument();
    });
  });

  it('9. Displays user-facing error message on API failure', async () => {
    const user = userEvent.setup();
    vi.mocked(onboardingService.submitStep1).mockRejectedValueOnce(
      new Error('Failed to connect to backend server.')
    );

    renderComponent();

    // Select CBSE and Class 10 so validation passes
    await user.click(screen.getByRole('radio', { name: /CBSE/i }));
    await user.click(screen.getByRole('radio', { name: 'Class 10' }));

    await user.click(screen.getByRole('button', { name: /Continue/i }));

    await waitFor(() => {
      expect(screen.getByText('Failed to connect to backend server.')).toBeInTheDocument();
    });
  });

  it('10. Protects onboarding route from unauthenticated users', async () => {
    localStorage.clear();

    render(
      <MemoryRouter initialEntries={['/onboarding/step1']}>
        <AuthProvider>
          <Routes>
            <Route element={<OnboardingRoute />}>
              <Route path="/onboarding/step1" element={<Step1Page />} />
            </Route>
            <Route path="/login" element={<div>Login Page Destination</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Login Page Destination')).toBeInTheDocument();
    });
  });

  it('11. Requires state selection when State Board is chosen', async () => {
    const user = userEvent.setup();
    renderComponent();

    // Select State Board
    await user.click(screen.getByRole('radio', { name: /State Board/i }));
    expect(screen.getByLabelText('Select your State')).toBeInTheDocument();

    // Select grade
    await user.click(screen.getByRole('radio', { name: 'Class 10' }));

    // Click Continue without selecting state
    await user.click(screen.getByRole('button', { name: /Continue/i }));
    expect(screen.getByText('Please select your state.')).toBeInTheDocument();
    expect(onboardingService.submitStep1).not.toHaveBeenCalled();

    // Select state
    await user.selectOptions(screen.getByLabelText('Select your State'), 'Maharashtra');
    expect(screen.queryByText('Please select your state.')).not.toBeInTheDocument();
  });

  it('12. Preserves Board and Class from navigation state on Back, with no stream selector', () => {
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/onboarding/step1',
            state: {
              board: 'CBSE',
              grade: 'Class 11',
              academic_stream: 'Science',
              selectedSubjectIds: ['cbse-11-042-physics'],
            },
          },
        ]}
      >
        <AuthProvider>
          <Step1Page />
        </AuthProvider>
      </MemoryRouter>
    );

    // CBSE and Class 11 are pre-selected
    expect(screen.getByRole('radio', { name: /CBSE/i })).toHaveClass('selected');
    expect(screen.getByRole('radio', { name: 'Class 11' })).toHaveClass('selected');

    // No stream selector appears on Step 1
    expect(screen.queryByText('Select Academic Stream')).not.toBeInTheDocument();
    expect(screen.queryByRole('radio', { name: 'Science' })).not.toBeInTheDocument();
  });
});
