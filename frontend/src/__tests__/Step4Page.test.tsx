import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter, MemoryRouter, Routes, Route, useLocation } from 'react-router-dom';
import { Step4Page } from '../pages/onboarding/Step4Page';
import { OnboardingRoute } from '../routes/OnboardingRoute';
import { AuthProvider } from '../context/AuthContext';
import { onboardingService } from '../services/onboarding';
import { authService } from '../services/auth';

vi.mock('../services/onboarding', () => ({
  onboardingService: {
    submitStep1: vi.fn(),
    submitStep2: vi.fn(),
    submitStep3: vi.fn(),
    submitStep4: vi.fn(),
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

describe('Step4Page Component (Onboarding Step 4 of 4: Study Schedule)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  const renderComponent = (initialState: any = null) =>
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/onboarding/step4',
            state: initialState,
          },
        ]}
      >
        <AuthProvider>
          <Step4Page />
        </AuthProvider>
      </MemoryRouter>
    );

  it('1. Step 4 renders correctly with headings and branding', () => {
    renderComponent();

    // Top navbar branding and actions
    expect(screen.getByText('SmartLearn.AI')).toBeInTheDocument();
    expect(screen.getByText(/Need help\?/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Contact Support' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign Out/i })).toBeInTheDocument();

    // Headings
    expect(
      screen.getByRole('heading', { name: 'Set your study schedule' })
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        /We'll set reminders and design a consistent habit streak plan based on your daily availability targets/i
      )
    ).toBeInTheDocument();
  });

  it('2. Progress shows 100% Set Up and STEP 4 OF 4: STUDY SCHEDULE', () => {
    renderComponent();

    expect(screen.getByText(/STEP 4 OF 4: STUDY SCHEDULE/i)).toBeInTheDocument();
    expect(screen.getByText('100% Set Up')).toBeInTheDocument();

    const fill = document.querySelector('.onboarding-progress-fill');
    expect(fill).toBeInTheDocument();
    expect(fill).toHaveStyle('width: 100%');
  });

  it('3. Daily study target options render (30 min, 1 hour, 2 hours, 3+ hours)', () => {
    renderComponent();

    expect(screen.getByText('Daily Study Target')).toBeInTheDocument();
    const targets = ['30 min', '1 hour', '2 hours', '3+ hours'];
    for (const t of targets) {
      const btn = screen.getByRole('radio', { name: t });
      expect(btn).toBeInTheDocument();
      expect(btn).not.toHaveClass('selected');
      expect(btn).toHaveAttribute('aria-checked', 'false');
    }
  });

  it('4. Preferred study slot options render (Morning, Afternoon, Evening, Night)', () => {
    renderComponent();

    expect(screen.getByText('Preferred Study Slot')).toBeInTheDocument();
    const slots = ['Morning', 'Afternoon', 'Evening', 'Night'];
    for (const s of slots) {
      const btn = screen.getByRole('radio', { name: s });
      expect(btn).toBeInTheDocument();
      expect(btn).not.toHaveClass('selected');
      expect(btn).toHaveAttribute('aria-checked', 'false');
    }

    expect(screen.getByText('6 AM - 12 PM')).toBeInTheDocument();
    expect(screen.getByText('12 PM - 5 PM')).toBeInTheDocument();
    expect(screen.getByText('5 PM - 9 PM')).toBeInTheDocument();
    expect(screen.getByText('9 PM - 2 AM')).toBeInTheDocument();
  });

  it('5. Monday–Sunday availability options render', () => {
    renderComponent();

    expect(
      screen.getByText('Weekly availability calendar (Mon - Sun)')
    ).toBeInTheDocument();

    const days = [
      'Monday',
      'Tuesday',
      'Wednesday',
      'Thursday',
      'Friday',
      'Saturday',
      'Sunday',
    ];
    for (const d of days) {
      const btn = screen.getByRole('checkbox', { name: d });
      expect(btn).toBeInTheDocument();
      expect(btn).not.toHaveClass('selected');
      expect(btn).toHaveAttribute('aria-checked', 'false');
    }
  });

  it('6. Daily target is single-select', async () => {
    const user = userEvent.setup();
    renderComponent();

    const t1 = screen.getByRole('radio', { name: '1 hour' });
    const t2 = screen.getByRole('radio', { name: '2 hours' });

    await user.click(t1);
    expect(t1).toHaveClass('selected');
    expect(t1).toHaveAttribute('aria-checked', 'true');
    expect(t2).not.toHaveClass('selected');

    await user.click(t2);
    expect(t2).toHaveClass('selected');
    expect(t2).toHaveAttribute('aria-checked', 'true');
    expect(t1).not.toHaveClass('selected');
    expect(t1).toHaveAttribute('aria-checked', 'false');
  });

  it('7. Study slot is single-select', async () => {
    const user = userEvent.setup();
    renderComponent();

    const morning = screen.getByRole('radio', { name: 'Morning' });
    const evening = screen.getByRole('radio', { name: 'Evening' });

    await user.click(morning);
    expect(morning).toHaveClass('selected');
    expect(evening).not.toHaveClass('selected');

    await user.click(evening);
    expect(evening).toHaveClass('selected');
    expect(morning).not.toHaveClass('selected');
  });

  it('8. Weekly availability supports multiple selections and toggling', async () => {
    const user = userEvent.setup();
    renderComponent();

    const mon = screen.getByRole('checkbox', { name: 'Monday' });
    const tue = screen.getByRole('checkbox', { name: 'Tuesday' });

    await user.click(mon);
    expect(mon).toHaveClass('selected');
    expect(mon).toHaveAttribute('aria-checked', 'true');

    await user.click(tue);
    expect(mon).toHaveClass('selected');
    expect(tue).toHaveClass('selected');

    // Deselect Mon
    await user.click(mon);
    expect(mon).not.toHaveClass('selected');
    expect(mon).toHaveAttribute('aria-checked', 'false');
    expect(tue).toHaveClass('selected');
  });

  it('9. Required validation enforces daily target, study slot, and available days', async () => {
    const user = userEvent.setup();
    renderComponent();

    // 1. Submit with nothing selected
    await user.click(screen.getByRole('button', { name: /Start Learning/i }));
    expect(
      screen.getByText('Please select your daily study target.')
    ).toBeInTheDocument();
    expect(onboardingService.submitStep4).not.toHaveBeenCalled();

    // 2. Select target, but no slot
    await user.click(screen.getByRole('radio', { name: '2 hours' }));
    await user.click(screen.getByRole('button', { name: /Start Learning/i }));
    expect(
      screen.getByText('Please select your preferred study slot.')
    ).toBeInTheDocument();
    expect(onboardingService.submitStep4).not.toHaveBeenCalled();

    // 3. Select slot, but no days
    await user.click(screen.getByRole('radio', { name: 'Evening' }));
    await user.click(screen.getByRole('button', { name: /Start Learning/i }));
    expect(
      screen.getByText(
        'Please select at least one day you are available to study.'
      )
    ).toBeInTheDocument();
    expect(onboardingService.submitStep4).not.toHaveBeenCalled();
  });

  it('10. Learning Profile displays Step 1–3 information correctly', () => {
    renderComponent({
      board: 'CBSE',
      grade: 'Class 11',
      academic_stream: 'Science',
      selectedSubjectNames: ['Mathematics', 'Physics', 'Chemistry', 'English Core'],
      preferred_style: 'Visual Learner',
    });

    expect(screen.getByText('Learning Profile')).toBeInTheDocument();
    expect(screen.getByText('CBSE • Class 11 (Science)')).toBeInTheDocument();
    expect(
      screen.getByText('Mathematics, Physics, Chemistry, English Core')
    ).toBeInTheDocument();
    expect(screen.getByText('Visual Learner')).toBeInTheDocument();
    expect(screen.getByText('AI Learning engine ready!')).toBeInTheDocument();
  });

  it('11. Weekly commitment calculation is dynamically updated', async () => {
    const user = userEvent.setup();
    renderComponent();

    // Initially '--'
    expect(screen.getByText('--')).toBeInTheDocument();

    // Select 2 hours
    await user.click(screen.getByRole('radio', { name: '2 hours' }));

    // Select 6 days (Mon-Sat)
    const days = [
      'Monday',
      'Tuesday',
      'Wednesday',
      'Thursday',
      'Friday',
      'Saturday',
    ];
    for (const d of days) {
      await user.click(screen.getByRole('checkbox', { name: d }));
    }

    // 2 hrs/day * 6 days/wk = 12 hrs
    expect(
      screen.getByText('12 hrs (2 hrs / day, 6 days/wk)')
    ).toBeInTheDocument();

    // Change target to 30 min (0.5 hrs)
    await user.click(screen.getByRole('radio', { name: '30 min' }));
    expect(
      screen.getByText('3 hrs (0.5 hrs / day, 6 days/wk)')
    ).toBeInTheDocument();
  });

  it('12 & 13. Back button navigates to Step 3 and preserves onboarding state', async () => {
    const user = userEvent.setup();
    let step3LocationState: any = null;

    const DummyStep3 = () => {
      const loc = useLocation();
      step3LocationState = loc.state;
      return <div>Step 3 Destination</div>;
    };

    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/onboarding/step4',
            state: {
              board: 'CBSE',
              grade: 'Class 11',
              academic_stream: 'Science',
              preferred_style: 'Visual Learner',
            },
          },
        ]}
      >
        <AuthProvider>
          <Routes>
            <Route path="/onboarding/step3" element={<DummyStep3 />} />
            <Route path="/onboarding/step4" element={<Step4Page />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await user.click(screen.getByRole('radio', { name: '1 hour' }));
    await user.click(screen.getByRole('radio', { name: 'Morning' }));

    const backBtn = screen.getByRole('button', { name: /Back/i });
    await user.click(backBtn);

    await waitFor(() => {
      expect(screen.getByText('Step 3 Destination')).toBeInTheDocument();
      expect(step3LocationState).toEqual(
        expect.objectContaining({
          board: 'CBSE',
          grade: 'Class 11',
          academic_stream: 'Science',
          preferred_style: 'Visual Learner',
          daily_target_hours: 1,
          preferred_slot: 'Morning',
        })
      );
    });
  });

  it('14, 15, 16, 18. Continue submits exact backend payload, updates AuthContext onboarding state, and navigates to dashboard', async () => {
    const user = userEvent.setup();

    vi.mocked(onboardingService.submitStep4).mockResolvedValueOnce({
      id: 1,
      user_id: 1,
      daily_target_hours: 2.0,
      preferred_slot: 'Evening',
      available_days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
      created_at: new Date().toISOString(),
    });

    vi.mocked(authService.getMe).mockResolvedValue({
      id: 1,
      email: 'student@example.com',
      full_name: 'Test Student',
      role: 'student',
      is_active: true,
      is_onboarded: true,
      created_at: new Date().toISOString(),
    });

    vi.mocked(onboardingService.getOnboardingStatus).mockResolvedValue({
      is_onboarded: true,
      step1_completed: true,
      step2_completed: true,
      step3_completed: true,
      step4_completed: true,
      current_step: 5,
    });

    render(
      <MemoryRouter initialEntries={['/onboarding/step4']}>
        <AuthProvider>
          <Routes>
            <Route path="/onboarding/step4" element={<Step4Page />} />
            <Route path="/dashboard" element={<div>Dashboard Success Page</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    // Select 2 hours
    await user.click(screen.getByRole('radio', { name: '2 hours' }));

    // Select Evening
    await user.click(screen.getByRole('radio', { name: 'Evening' }));

    // Select Mon through Sat
    const days = [
      'Monday',
      'Tuesday',
      'Wednesday',
      'Thursday',
      'Friday',
      'Saturday',
    ];
    for (const d of days) {
      await user.click(screen.getByRole('checkbox', { name: d }));
    }

    // Click Start Learning
    await user.click(screen.getByRole('button', { name: /Start Learning/i }));

    await waitFor(() => {
      expect(onboardingService.submitStep4).toHaveBeenCalledWith({
        daily_target_hours: 2.0,
        preferred_slot: 'Evening',
        available_days: [
          'Monday',
          'Tuesday',
          'Wednesday',
          'Thursday',
          'Friday',
          'Saturday',
        ],
      });
      expect(screen.getByText('Dashboard Success Page')).toBeInTheDocument();
    });
  });

  it('17. API failure does not navigate and displays alert', async () => {
    const user = userEvent.setup();
    vi.mocked(onboardingService.submitStep4).mockRejectedValueOnce(
      new Error('Failed to save study schedule.')
    );

    render(
      <MemoryRouter initialEntries={['/onboarding/step4']}>
        <AuthProvider>
          <Routes>
            <Route path="/onboarding/step4" element={<Step4Page />} />
            <Route path="/dashboard" element={<div>Dashboard Success Page</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await user.click(screen.getByRole('radio', { name: '1 hour' }));
    await user.click(screen.getByRole('radio', { name: 'Morning' }));
    await user.click(screen.getByRole('checkbox', { name: 'Monday' }));

    await user.click(screen.getByRole('button', { name: /Start Learning/i }));

    await waitFor(() => {
      expect(screen.getByText('Failed to save study schedule.')).toBeInTheDocument();
      expect(screen.queryByText('Dashboard Success Page')).not.toBeInTheDocument();
    });
  });

  it('protects Step 4 route from unauthenticated users', async () => {
    localStorage.clear();

    render(
      <MemoryRouter initialEntries={['/onboarding/step4']}>
        <AuthProvider>
          <Routes>
            <Route element={<OnboardingRoute />}>
              <Route path="/onboarding/step4" element={<Step4Page />} />
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
});
