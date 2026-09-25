import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter, MemoryRouter, Routes, Route, useLocation } from 'react-router-dom';
import { Step2Page } from '../pages/onboarding/Step2Page';
import { OnboardingRoute } from '../routes/OnboardingRoute';
import { AuthProvider } from '../context/AuthContext';
import { onboardingService } from '../services/onboarding';
import { authService } from '../services/auth';

vi.mock('../services/onboarding', () => ({
  onboardingService: {
    submitStep1: vi.fn(),
    submitStep2: vi.fn(),
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

describe('Step2Page Component (Onboarding Step 2 of 4)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  const renderComponent = () =>
    render(
      <BrowserRouter>
        <AuthProvider>
          <Step2Page />
        </AuthProvider>
      </BrowserRouter>
    );

  it('1, 2, 3, 4. Renders Step 2 page with 50% progress state', () => {
    renderComponent();

    // Top navbar
    expect(screen.getByText('SmartLearn.AI')).toBeInTheDocument();
    expect(screen.getByText(/Need help\?/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Contact Support' })).toBeInTheDocument();

    // Step progress
    expect(screen.getByText(/STEP 2 OF 4: STREAM & SUBJECTS/i)).toBeInTheDocument();
    expect(screen.getByText('50% Set Up')).toBeInTheDocument();

    // Progress bar fill check
    const fill = document.querySelector('.onboarding-progress-fill');
    expect(fill).toBeInTheDocument();
    expect(fill).toHaveStyle('width: 50%');
  });

  it('5. Renders academic stream options matching specification for Class 11', () => {
    renderComponent();

    expect(screen.getByText('Your Academic Stream')).toBeInTheDocument();

    const streams = ['Science', 'Commerce', 'Humanities / Arts'];
    for (const stream of streams) {
      const card = screen.getByRole('radio', { name: stream });
      expect(card).toBeInTheDocument();
      expect(card).not.toHaveClass('selected');
      expect(card).toHaveAttribute('aria-checked', 'false');
    }

    expect(screen.getByText('Medical or Non-Medical tracks')).toBeInTheDocument();
    expect(screen.getByText('Business, Economics & Finance')).toBeInTheDocument();
    expect(screen.getByText('Literature, History & Social Science')).toBeInTheDocument();
  });

  it('6. Renders subject options matching curriculum when stream is selected', async () => {
    const user = userEvent.setup();
    renderComponent();

    await user.click(screen.getByRole('radio', { name: 'Science' }));
    expect(screen.getByText('Select Subjects to Learn')).toBeInTheDocument();

    const subjects = [
      'Mathematics',
      'Physics',
      'Chemistry',
      'Biology',
      'English Core',
      'Computer Science',
      'Hindi Core',
    ];

    for (const sub of subjects) {
      const btn = screen.getByRole('checkbox', { name: sub });
      expect(btn).toBeInTheDocument();
      expect(btn).not.toHaveClass('selected');
      expect(btn).toHaveAttribute('aria-checked', 'false');
    }
  });

  it('7. Selection states work for stream and multi-select subjects', async () => {
    const user = userEvent.setup();
    renderComponent();

    const scienceBtn = screen.getByRole('radio', { name: 'Science' });
    await user.click(scienceBtn);
    expect(scienceBtn).toHaveClass('selected');
    expect(scienceBtn).toHaveAttribute('aria-checked', 'true');

    // Select subjects: Math & Physics
    const mathBtn = screen.getByRole('checkbox', { name: 'Mathematics' });
    const physicsBtn = screen.getByRole('checkbox', { name: 'Physics' });

    await user.click(mathBtn);
    await user.click(physicsBtn);

    expect(mathBtn).toHaveClass('selected');
    expect(mathBtn).toHaveAttribute('aria-checked', 'true');
    expect(physicsBtn).toHaveClass('selected');
    expect(physicsBtn).toHaveAttribute('aria-checked', 'true');

    // Deselect Physics
    await user.click(physicsBtn);
    expect(physicsBtn).not.toHaveClass('selected');
    expect(physicsBtn).toHaveAttribute('aria-checked', 'false');
  });

  it('8. Validation: Continue cannot submit with missing selections', async () => {
    const user = userEvent.setup();
    renderComponent();

    // 1. Submit with nothing selected
    await user.click(screen.getByRole('button', { name: /Continue/i }));
    expect(screen.getByText('Please select your academic stream.')).toBeInTheDocument();
    expect(onboardingService.submitStep2).not.toHaveBeenCalled();

    // 2. Select stream, but no subjects
    await user.click(screen.getByRole('radio', { name: 'Science' }));
    await user.click(screen.getByRole('button', { name: /Continue/i }));
    expect(screen.getByText('Please select at least one subject to learn.')).toBeInTheDocument();
    expect(onboardingService.submitStep2).not.toHaveBeenCalled();
  });

  it('9 & 10. Submits correct payload to POST /api/v1/users/onboarding/step2 and navigates to Step 3', async () => {
    const user = userEvent.setup();
    vi.mocked(onboardingService.submitStep2).mockResolvedValueOnce([
      { id: 1, user_id: 1, subject_name: 'Mathematics', created_at: new Date().toISOString() },
      { id: 2, user_id: 1, subject_name: 'Physics', created_at: new Date().toISOString() },
      { id: 3, user_id: 1, subject_name: 'Chemistry', created_at: new Date().toISOString() },
      { id: 4, user_id: 1, subject_name: 'English Core', created_at: new Date().toISOString() },
    ]);

    render(
      <MemoryRouter initialEntries={['/onboarding/step2']}>
        <AuthProvider>
          <Routes>
            <Route path="/onboarding/step2" element={<Step2Page />} />
            <Route path="/onboarding/step3" element={<div>Step 3 Destination</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    // Select Science
    await user.click(screen.getByRole('radio', { name: 'Science' }));

    // Select Mathematics, Physics, Chemistry, English Core
    await user.click(screen.getByRole('checkbox', { name: 'Mathematics' }));
    await user.click(screen.getByRole('checkbox', { name: 'Physics' }));
    await user.click(screen.getByRole('checkbox', { name: 'Chemistry' }));
    await user.click(screen.getByRole('checkbox', { name: 'English Core' }));

    // Click Continue
    await user.click(screen.getByRole('button', { name: /Continue/i }));

    await waitFor(() => {
      expect(onboardingService.submitStep2).toHaveBeenCalledWith({
        academic_stream: 'Science',
        subjects: ['Mathematics', 'Physics', 'Chemistry', 'English Core'],
      });
      expect(screen.getByText('Step 3 Destination')).toBeInTheDocument();
    });
  });

  it('11. Displays user-facing error message on API failure', async () => {
    const user = userEvent.setup();
    vi.mocked(onboardingService.submitStep2).mockRejectedValueOnce(
      new Error('Failed to save subject selections.')
    );

    renderComponent();

    // Select valid stream and subject
    await user.click(screen.getByRole('radio', { name: 'Commerce' }));
    await user.click(screen.getByRole('checkbox', { name: 'Accountancy' }));

    await user.click(screen.getByRole('button', { name: /Continue/i }));

    await waitFor(() => {
      expect(screen.getByText('Failed to save subject selections.')).toBeInTheDocument();
    });
  });

  it('12. Back button navigates to /onboarding/step1', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={['/onboarding/step2']}>
        <AuthProvider>
          <Routes>
            <Route path="/onboarding/step1" element={<div>Step 1 Destination</div>} />
            <Route path="/onboarding/step2" element={<Step2Page />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    const backBtn = screen.getByRole('button', { name: /Back/i });
    await user.click(backBtn);

    await waitFor(() => {
      expect(screen.getByText('Step 1 Destination')).toBeInTheDocument();
    });
  });

  it('13. Protects onboarding step 2 route from unauthenticated users', async () => {
    localStorage.clear();

    render(
      <MemoryRouter initialEntries={['/onboarding/step2']}>
        <AuthProvider>
          <Routes>
            <Route element={<OnboardingRoute />}>
              <Route path="/onboarding/step2" element={<Step2Page />} />
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

  it('14. Renders Class 10 secondary curriculum directly without stream selector', () => {
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/onboarding/step2',
            state: { board: 'CBSE', grade: 'Class 10' },
          },
        ]}
      >
        <AuthProvider>
          <Step2Page />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.queryByText('Your Academic Stream')).not.toBeInTheDocument();
    expect(screen.getByText('Select Subjects to Learn')).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: 'Science' })).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: 'Social Science' })).toBeInTheDocument();
  });

  it('15. Enforces mutual exclusion in UI (e.g. Mathematics Standard vs Basic)', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/onboarding/step2',
            state: { board: 'CBSE', grade: 'Class 10' },
          },
        ]}
      >
        <AuthProvider>
          <Step2Page />
        </AuthProvider>
      </MemoryRouter>
    );

    const mathStd = screen.getByRole('checkbox', { name: 'Mathematics Standard' });
    const mathBasic = screen.getByRole('checkbox', { name: 'Mathematics Basic' });

    // Select Mathematics Standard
    await user.click(mathStd);
    expect(mathStd).toHaveClass('selected');

    // Attempt to select Mathematics Basic
    await user.click(mathBasic);
    expect(
      screen.getByText(/Cannot select "Mathematics Basic" together with "Mathematics Standard"/i)
    ).toBeInTheDocument();
    expect(mathBasic).not.toHaveClass('selected');
  });

  it('16. Class 6 Step 2 has no stream selector and displays Class 6 subjects directly', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/onboarding/step2',
            state: { board: 'CBSE', grade: 'Class 6' },
          },
        ]}
      >
        <AuthProvider>
          <Step2Page />
        </AuthProvider>
      </MemoryRouter>
    );

    // No stream selector for Class 6
    expect(screen.queryByText('Your Academic Stream')).not.toBeInTheDocument();
    expect(screen.getByText('Select Subjects to Learn')).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: 'Mathematics' })).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: 'Science' })).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: 'Social Science' })).toBeInTheDocument();

    // Validation requires at least one subject, but does not ask for stream
    await user.click(screen.getByRole('button', { name: /Continue/i }));
    expect(screen.getByText('Please select at least one subject to learn.')).toBeInTheDocument();
    expect(screen.queryByText('Please select your academic stream.')).not.toBeInTheDocument();
  });

  it('17. Class 12 Step 2 shows the stream selector and requires stream before Continue', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/onboarding/step2',
            state: { board: 'CBSE', grade: 'Class 12' },
          },
        ]}
      >
        <AuthProvider>
          <Step2Page />
        </AuthProvider>
      </MemoryRouter>
    );

    // Stream selector must be visible for Class 12
    expect(screen.getByText('Your Academic Stream')).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: 'Science' })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: 'Commerce' })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: 'Humanities / Arts' })).toBeInTheDocument();

    // Validation without stream
    await user.click(screen.getByRole('button', { name: /Continue/i }));
    expect(screen.getByText('Please select your academic stream.')).toBeInTheDocument();
  });

  it('18. Changing Class 11 stream dynamically updates the subject catalogue', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/onboarding/step2',
            state: { board: 'CBSE', grade: 'Class 11' },
          },
        ]}
      >
        <AuthProvider>
          <Step2Page />
        </AuthProvider>
      </MemoryRouter>
    );

    // 1. Select Science
    await user.click(screen.getByRole('radio', { name: 'Science' }));
    expect(screen.getByRole('checkbox', { name: 'Physics' })).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: 'Chemistry' })).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: 'Biology' })).toBeInTheDocument();
    expect(screen.queryByRole('checkbox', { name: 'Accountancy' })).not.toBeInTheDocument();
    expect(screen.queryByRole('checkbox', { name: 'History' })).not.toBeInTheDocument();

    // 2. Switch to Commerce
    await user.click(screen.getByRole('radio', { name: 'Commerce' }));
    expect(screen.getByRole('checkbox', { name: 'Accountancy' })).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: 'Business Studies' })).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: 'Economics' })).toBeInTheDocument();
    expect(screen.queryByRole('checkbox', { name: 'Physics' })).not.toBeInTheDocument();
    expect(screen.queryByRole('checkbox', { name: 'Biology' })).not.toBeInTheDocument();

    // 3. Switch to Humanities / Arts
    await user.click(screen.getByRole('radio', { name: 'Humanities / Arts' }));
    expect(screen.getByRole('checkbox', { name: 'History' })).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: 'Political Science' })).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: 'Geography' })).toBeInTheDocument();
    expect(screen.queryByRole('checkbox', { name: 'Accountancy' })).not.toBeInTheDocument();
    expect(screen.queryByRole('checkbox', { name: 'Physics' })).not.toBeInTheDocument();
  });

  it('19. Changing stream clears incompatible selected subjects', async () => {
    const user = userEvent.setup();
    vi.mocked(onboardingService.submitStep2).mockResolvedValueOnce([
      { id: 1, user_id: 1, subject_name: 'Accountancy', created_at: new Date().toISOString() },
    ]);

    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/onboarding/step2',
            state: { board: 'CBSE', grade: 'Class 11' },
          },
        ]}
      >
        <AuthProvider>
          <Step2Page />
        </AuthProvider>
      </MemoryRouter>
    );

    // Select Science, pick Physics
    await user.click(screen.getByRole('radio', { name: 'Science' }));
    const physicsBtn = screen.getByRole('checkbox', { name: 'Physics' });
    await user.click(physicsBtn);
    expect(physicsBtn).toHaveClass('selected');

    // Switch to Commerce - Physics is not valid in Commerce
    await user.click(screen.getByRole('radio', { name: 'Commerce' }));
    expect(screen.queryByRole('checkbox', { name: 'Physics' })).not.toBeInTheDocument();

    // Select Accountancy in Commerce and submit
    await user.click(screen.getByRole('checkbox', { name: 'Accountancy' }));
    await user.click(screen.getByRole('button', { name: /Continue/i }));

    await waitFor(() => {
      // Must NOT include 'Physics' in submitted subjects
      expect(onboardingService.submitStep2).toHaveBeenCalledWith({
        academic_stream: 'Commerce',
        subjects: ['Accountancy'],
      });
    });
  });

  it('20. Enforces Hindi Course-A vs Hindi Course-B mutual exclusion for Class 10', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/onboarding/step2',
            state: { board: 'CBSE', grade: 'Class 10' },
          },
        ]}
      >
        <AuthProvider>
          <Step2Page />
        </AuthProvider>
      </MemoryRouter>
    );

    const hindiA = screen.getByRole('checkbox', { name: 'Hindi Course-A' });
    const hindiB = screen.getByRole('checkbox', { name: 'Hindi Course-B' });

    // Select Hindi Course-A
    await user.click(hindiA);
    expect(hindiA).toHaveClass('selected');

    // Attempt to select Hindi Course-B
    await user.click(hindiB);
    expect(
      screen.getByText(/Cannot select "Hindi Course-B" together with "Hindi Course-A"/i)
    ).toBeInTheDocument();
    expect(hindiB).not.toHaveClass('selected');
  });

  it('21. Preserves stream and valid subjects when navigating Back and returning to Step 2', async () => {
    const user = userEvent.setup();
    let receivedStateOnStep1: any = null;

    const DummyStep1 = () => {
      const loc = useLocation();
      receivedStateOnStep1 = loc.state;
      return <div>Step 1 Mock Page</div>;
    };

    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/onboarding/step2',
            state: { board: 'CBSE', grade: 'Class 11' },
          },
        ]}
      >
        <AuthProvider>
          <Routes>
            <Route path="/onboarding/step1" element={<DummyStep1 />} />
            <Route path="/onboarding/step2" element={<Step2Page />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    // Select Science and Mathematics
    await user.click(screen.getByRole('radio', { name: 'Science' }));
    await user.click(screen.getByRole('checkbox', { name: 'Mathematics' }));

    // Click Back
    const backBtn = screen.getByRole('button', { name: /Back/i });
    await user.click(backBtn);

    await waitFor(() => {
      expect(screen.getByText('Step 1 Mock Page')).toBeInTheDocument();
      expect(receivedStateOnStep1).toEqual(
        expect.objectContaining({
          board: 'CBSE',
          grade: 'Class 11',
          academic_stream: 'Science',
          selectedSubjectIds: expect.arrayContaining(['cbse-11-041-math']),
        })
      );
    });
  });
});
