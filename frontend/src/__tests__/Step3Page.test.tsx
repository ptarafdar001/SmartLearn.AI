import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter, MemoryRouter, Routes, Route, useLocation } from 'react-router-dom';
import { Step3Page } from '../pages/onboarding/Step3Page';
import { OnboardingRoute } from '../routes/OnboardingRoute';
import { AuthProvider } from '../context/AuthContext';
import { onboardingService } from '../services/onboarding';
import { authService } from '../services/auth';

vi.mock('../services/onboarding', () => ({
  onboardingService: {
    submitStep1: vi.fn(),
    submitStep2: vi.fn(),
    submitStep3: vi.fn(),
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

describe('Step3Page Component (Onboarding Step 3 of 4: Style & Goals)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  const renderComponent = () =>
    render(
      <BrowserRouter>
        <AuthProvider>
          <Step3Page />
        </AuthProvider>
      </BrowserRouter>
    );

  it('1. Renders Step 3 page with correct titles, learning styles, and goal options', () => {
    renderComponent();

    // Top navbar branding and actions
    expect(screen.getByText('SmartLearn.AI')).toBeInTheDocument();
    expect(screen.getByText(/Need help\?/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Contact Support' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign Out/i })).toBeInTheDocument();

    // Headings
    expect(
      screen.getByRole('heading', { name: 'Tell us about your learning preferences' })
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        /SmartLearn.AI matches resources matching your unique learning style/i
      )
    ).toBeInTheDocument();

    // Section 1: Preferred Study Style
    expect(screen.getByText('Preferred Study Style')).toBeInTheDocument();
    const styleOptions = [
      'Visual Learner',
      'Hands-on Practice',
      'Auditory & Talk',
      'Reading & Notes',
    ];
    for (const style of styleOptions) {
      const radio = screen.getByRole('radio', { name: style });
      expect(radio).toBeInTheDocument();
      expect(radio).not.toHaveClass('selected');
      expect(radio).toHaveAttribute('aria-checked', 'false');
    }

    expect(
      screen.getByText(/Video content, interactive 3D diagrams, and graphical mind maps/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        /Learning by doing — active multiple-choice questions & chapter tests/i
      )
    ).toBeInTheDocument();

    // Section 2: Study Goals
    expect(
      screen.getByText('What are your key study goals? (Multi-select)')
    ).toBeInTheDocument();
    const goals = [
      'Prepare for Board Exams',
      'Competitive Exams (JEE / NEET / CUET prep)',
      'Improve class performance & overall grades',
      'Self-paced learning to build solid foundational skills',
    ];
    for (const goal of goals) {
      const checkbox = screen.getByRole('checkbox', { name: goal });
      expect(checkbox).toBeInTheDocument();
      expect(checkbox).not.toHaveClass('selected');
      expect(checkbox).toHaveAttribute('aria-checked', 'false');
    }
  });

  it('2. Progress shows 75% Set Up and STEP 3 OF 4: STYLE & GOALS', () => {
    renderComponent();

    expect(screen.getByText(/STEP 3 OF 4: STYLE & GOALS/i)).toBeInTheDocument();
    expect(screen.getByText('75% Set Up')).toBeInTheDocument();

    const fill = document.querySelector('.onboarding-progress-fill');
    expect(fill).toBeInTheDocument();
    expect(fill).toHaveStyle('width: 75%');
  });

  it('3. Required preference fields are validated before Continue', async () => {
    const user = userEvent.setup();
    renderComponent();

    // Click Continue without selecting anything
    await user.click(screen.getByRole('button', { name: /Continue/i }));
    expect(
      screen.getByText('Please select your preferred study style.')
    ).toBeInTheDocument();
    expect(onboardingService.submitStep3).not.toHaveBeenCalled();
  });

  it('4. Goal fields are validated according to backend requirements', async () => {
    const user = userEvent.setup();
    renderComponent();

    // Select only learning style
    await user.click(screen.getByRole('radio', { name: 'Visual Learner' }));
    expect(screen.queryByText('Please select your preferred study style.')).not.toBeInTheDocument();

    // Click Continue without selecting any goals
    await user.click(screen.getByRole('button', { name: /Continue/i }));
    expect(
      screen.getByText('Please select at least one study goal.')
    ).toBeInTheDocument();
    expect(onboardingService.submitStep3).not.toHaveBeenCalled();
  });

  it('5. User can select the available learning preference options (single select)', async () => {
    const user = userEvent.setup();
    renderComponent();

    const visual = screen.getByRole('radio', { name: 'Visual Learner' });
    const handsOn = screen.getByRole('radio', { name: 'Hands-on Practice' });

    // Select Visual
    await user.click(visual);
    expect(visual).toHaveClass('selected');
    expect(visual).toHaveAttribute('aria-checked', 'true');
    expect(handsOn).not.toHaveClass('selected');
    expect(handsOn).toHaveAttribute('aria-checked', 'false');

    // Switch to Hands-on
    await user.click(handsOn);
    expect(handsOn).toHaveClass('selected');
    expect(handsOn).toHaveAttribute('aria-checked', 'true');
    expect(visual).not.toHaveClass('selected');
    expect(visual).toHaveAttribute('aria-checked', 'false');
  });

  it('6. User can select and toggle the available goals (multi-select)', async () => {
    const user = userEvent.setup();
    renderComponent();

    const boardExam = screen.getByRole('checkbox', {
      name: 'Prepare for Board Exams',
    });
    const competitive = screen.getByRole('checkbox', {
      name: 'Competitive Exams (JEE / NEET / CUET prep)',
    });

    // Select Board Exams
    await user.click(boardExam);
    expect(boardExam).toHaveClass('selected');
    expect(boardExam).toHaveAttribute('aria-checked', 'true');

    // Select Competitive Exams
    await user.click(competitive);
    expect(boardExam).toHaveClass('selected');
    expect(competitive).toHaveClass('selected');

    // Deselect Board Exams
    await user.click(boardExam);
    expect(boardExam).not.toHaveClass('selected');
    expect(boardExam).toHaveAttribute('aria-checked', 'false');
    expect(competitive).toHaveClass('selected');
  });

  it('7 & 8. Continue submits exact Step 3 payload and navigates to Step 4 on success', async () => {
    const user = userEvent.setup();
    vi.mocked(onboardingService.submitStep3).mockResolvedValueOnce({
      learning_preference: {
        id: 1,
        user_id: 1,
        preferred_style: 'Visual Learner',
        created_at: new Date().toISOString(),
      },
      study_goals: [
        {
          id: 1,
          user_id: 1,
          goal_text: 'Competitive Exams (JEE / NEET / CUET prep)',
          created_at: new Date().toISOString(),
        },
        {
          id: 2,
          user_id: 1,
          goal_text: 'Improve class performance & overall grades',
          created_at: new Date().toISOString(),
        },
      ],
    });

    render(
      <MemoryRouter initialEntries={['/onboarding/step3']}>
        <AuthProvider>
          <Routes>
            <Route path="/onboarding/step3" element={<Step3Page />} />
            <Route
              path="/onboarding/step4"
              element={<div>Step 4 Schedule Destination</div>}
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    // Select Style
    await user.click(screen.getByRole('radio', { name: 'Visual Learner' }));

    // Select Goals
    await user.click(
      screen.getByRole('checkbox', {
        name: 'Competitive Exams (JEE / NEET / CUET prep)',
      })
    );
    await user.click(
      screen.getByRole('checkbox', {
        name: 'Improve class performance & overall grades',
      })
    );

    // Submit
    await user.click(screen.getByRole('button', { name: /Continue/i }));

    await waitFor(() => {
      expect(onboardingService.submitStep3).toHaveBeenCalledWith({
        preferred_style: 'Visual Learner',
        goals: [
          'Competitive Exams (JEE / NEET / CUET prep)',
          'Improve class performance & overall grades',
        ],
      });
      expect(
        screen.getByText('Step 4 Schedule Destination')
      ).toBeInTheDocument();
    });
  });

  it('9. Failed API submission displays error message and does not navigate', async () => {
    const user = userEvent.setup();
    vi.mocked(onboardingService.submitStep3).mockRejectedValueOnce(
      new Error('Failed to save study goals.')
    );

    render(
      <MemoryRouter initialEntries={['/onboarding/step3']}>
        <AuthProvider>
          <Routes>
            <Route path="/onboarding/step3" element={<Step3Page />} />
            <Route
              path="/onboarding/step4"
              element={<div>Step 4 Schedule Destination</div>}
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await user.click(screen.getByRole('radio', { name: 'Auditory & Talk' }));
    await user.click(
      screen.getByRole('checkbox', {
        name: 'Prepare for Board Exams',
      })
    );

    await user.click(screen.getByRole('button', { name: /Continue/i }));

    await waitFor(() => {
      expect(screen.getByText('Failed to save study goals.')).toBeInTheDocument();
      expect(
        screen.queryByText('Step 4 Schedule Destination')
      ).not.toBeInTheDocument();
    });
  });

  it('10. Back button navigates to /onboarding/step2 and preserves Step 1/2 context', async () => {
    const user = userEvent.setup();
    let step2LocationState: any = null;

    const DummyStep2 = () => {
      const loc = useLocation();
      step2LocationState = loc.state;
      return <div>Step 2 Destination</div>;
    };

    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/onboarding/step3',
            state: {
              board: 'CBSE',
              grade: 'Class 11',
              academic_stream: 'Science',
              selectedSubjectIds: ['cbse-11-041-math'],
            },
          },
        ]}
      >
        <AuthProvider>
          <Routes>
            <Route path="/onboarding/step2" element={<DummyStep2 />} />
            <Route path="/onboarding/step3" element={<Step3Page />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    // Select a style and goal before going back
    await user.click(screen.getByRole('radio', { name: 'Reading & Notes' }));
    await user.click(
      screen.getByRole('checkbox', {
        name: 'Self-paced learning to build solid foundational skills',
      })
    );

    // Click Back
    await user.click(screen.getByRole('button', { name: /Back/i }));

    await waitFor(() => {
      expect(screen.getByText('Step 2 Destination')).toBeInTheDocument();
      expect(step2LocationState).toEqual(
        expect.objectContaining({
          board: 'CBSE',
          grade: 'Class 11',
          academic_stream: 'Science',
          selectedSubjectIds: ['cbse-11-041-math'],
          preferred_style: 'Reading & Notes',
          goals: ['Self-paced learning to build solid foundational skills'],
        })
      );
    });
  });

  it('11. Preserves existing Step 3 selections from navigation state or localStorage', () => {
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/onboarding/step3',
            state: {
              preferred_style: 'Auditory & Talk',
              goals: [
                'Prepare for Board Exams',
                'Self-paced learning to build solid foundational skills',
              ],
            },
          },
        ]}
      >
        <AuthProvider>
          <Step3Page />
        </AuthProvider>
      </MemoryRouter>
    );

    // Style is pre-selected
    expect(screen.getByRole('radio', { name: 'Auditory & Talk' })).toHaveClass(
      'selected'
    );
    expect(
      screen.getByRole('radio', { name: 'Visual Learner' })
    ).not.toHaveClass('selected');

    // Goals are pre-selected
    expect(
      screen.getByRole('checkbox', { name: 'Prepare for Board Exams' })
    ).toHaveClass('selected');
    expect(
      screen.getByRole('checkbox', {
        name: 'Self-paced learning to build solid foundational skills',
      })
    ).toHaveClass('selected');
    expect(
      screen.getByRole('checkbox', {
        name: 'Competitive Exams (JEE / NEET / CUET prep)',
      })
    ).not.toHaveClass('selected');
  });

  it('12. Protects Step 3 route from unauthenticated users', async () => {
    localStorage.clear();

    render(
      <MemoryRouter initialEntries={['/onboarding/step3']}>
        <AuthProvider>
          <Routes>
            <Route element={<OnboardingRoute />}>
              <Route path="/onboarding/step3" element={<Step3Page />} />
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
