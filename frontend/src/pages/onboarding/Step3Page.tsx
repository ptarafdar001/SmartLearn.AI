import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { onboardingService } from '../../services/onboarding';
import { OnboardingNavbar } from '../../components/onboarding/OnboardingNavbar';
import { OnboardingProgress } from '../../components/onboarding/OnboardingProgress';
import { Alert } from '../../components/common/Alert';
import '../../styles/onboarding.css';

interface LearningStyleOption {
  id: string;
  name: string;
  description: string;
}

const LEARNING_STYLES: LearningStyleOption[] = [
  {
    id: 'Visual Learner',
    name: 'Visual Learner',
    description: 'Video content, interactive 3D diagrams, and graphical mind maps.',
  },
  {
    id: 'Hands-on Practice',
    name: 'Hands-on Practice',
    description: 'Learning by doing — active multiple-choice questions & chapter tests.',
  },
  {
    id: 'Auditory & Talk',
    name: 'Auditory & Talk',
    description: 'Audio lectures, dynamic podcast summaries, and interactive AI text-to-speech.',
  },
  {
    id: 'Reading & Notes',
    name: 'Reading & Notes',
    description: 'Structured revision notes, text summaries, and detailed book chapters.',
  },
];

const STUDY_GOALS: string[] = [
  'Prepare for Board Exams',
  'Competitive Exams (JEE / NEET / CUET prep)',
  'Improve class performance & overall grades',
  'Self-paced learning to build solid foundational skills',
];

export const Step3Page: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Retrieve existing state from navigation or localStorage
  const existingStep3 = (() => {
    if (location.state && (location.state.preferred_style || location.state.goals)) {
      return location.state;
    }
    try {
      const stored = localStorage.getItem('smartlearn_onboarding_step3');
      if (stored) return JSON.parse(stored);
    } catch {
      // Ignore localStorage error
    }
    return null;
  })();

  const [selectedStyle, setSelectedStyle] = useState<string>(
    existingStep3?.preferred_style || ''
  );
  const [selectedGoals, setSelectedGoals] = useState<string[]>(() => {
    if (Array.isArray(existingStep3?.goals)) {
      return existingStep3.goals;
    }
    return [];
  });

  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const selectStyle = (styleId: string) => {
    setSelectedStyle(styleId);
    setError(null);
  };

  const toggleGoal = (goal: string) => {
    setError(null);
    setSelectedGoals((prev) =>
      prev.includes(goal) ? prev.filter((g) => g !== goal) : [...prev, goal]
    );
  };

  const handleBack = () => {
    // Preserve current Step 3 choices in localStorage
    try {
      localStorage.setItem(
        'smartlearn_onboarding_step3',
        JSON.stringify({
          preferred_style: selectedStyle,
          goals: selectedGoals,
        })
      );
    } catch {
      // Ignore localStorage error
    }

    // Retrieve Step 1 & 2 context if available
    let step2Context = null;
    if (location.state && (location.state.board || location.state.grade)) {
      step2Context = location.state;
    } else {
      try {
        const storedStep1 = localStorage.getItem('smartlearn_onboarding_step1');
        if (storedStep1) step2Context = JSON.parse(storedStep1);
      } catch {
        // Ignore
      }
    }

    navigate('/onboarding/step2', {
      state: {
        ...step2Context,
        preferred_style: selectedStyle,
        goals: selectedGoals,
      },
    });
  };

  const validate = (): boolean => {
    if (!selectedStyle) {
      setError('Please select your preferred study style.');
      return false;
    }
    if (selectedGoals.length === 0) {
      setError('Please select at least one study goal.');
      return false;
    }
    setError(null);
    return true;
  };

  const handleContinue = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsLoading(true);
    setError(null);

    try {
      await onboardingService.submitStep3({
        preferred_style: selectedStyle,
        goals: selectedGoals,
      });

      // Save to localStorage for forward/backward persistence
      try {
        localStorage.setItem(
          'smartlearn_onboarding_step3',
          JSON.stringify({
            preferred_style: selectedStyle,
            goals: selectedGoals,
          })
        );
      } catch {
        // Ignore localStorage error
      }

      // Navigate to Step 4 on successful submission with preserved context
      navigate('/onboarding/step4', {
        state: {
          ...(location.state || {}),
          preferred_style: selectedStyle,
          goals: selectedGoals,
        },
      });
    } catch (err: any) {
      setError(
        err.message || 'Failed to save your preferences. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="onboarding-page-container">
      <OnboardingNavbar />

      <main className="onboarding-card" role="main">
        <OnboardingProgress
          step={3}
          totalSteps={4}
          stepTitle="Style & Goals"
          percentage={75}
        />

        <h1 className="onboarding-title">Tell us about your learning preferences</h1>
        <p className="onboarding-subtitle">
          SmartLearn.AI matches resources matching your unique learning style and targets critical areas to boost score trends.
        </p>

        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

        <form onSubmit={handleContinue} noValidate>
          {/* Section 1: Preferred Study Style */}
          <div className="selection-section">
            <label className="selection-label" id="preferred-style-label">
              Preferred Study Style
            </label>
            <div
              className="style-cards-grid"
              role="radiogroup"
              aria-labelledby="preferred-style-label"
            >
              {LEARNING_STYLES.map((style) => {
                const isSelected = selectedStyle === style.id;
                return (
                  <button
                    key={style.id}
                    type="button"
                    role="radio"
                    aria-label={style.name}
                    aria-checked={isSelected}
                    className={`style-card-btn ${isSelected ? 'selected' : ''}`}
                    onClick={() => selectStyle(style.id)}
                  >
                    <div className="style-card-icon-badge" aria-hidden="true">
                      {style.id === 'Visual Learner' && (
                        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                          <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="2" />
                          <polygon points="10 8 16 12 10 16 10 8" fill="currentColor" />
                        </svg>
                      )}
                      {style.id === 'Hands-on Practice' && (
                        <svg
                          viewBox="0 0 24 24"
                          width="20"
                          height="20"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z" />
                        </svg>
                      )}
                      {style.id === 'Auditory & Talk' && (
                        <svg
                          viewBox="0 0 24 24"
                          width="20"
                          height="20"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                          <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
                          <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
                        </svg>
                      )}
                      {style.id === 'Reading & Notes' && (
                        <svg
                          viewBox="0 0 24 24"
                          width="20"
                          height="20"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                          <polyline points="14 2 14 8 20 8" />
                          <line x1="16" y1="13" x2="8" y2="13" />
                          <line x1="16" y1="17" x2="8" y2="17" />
                        </svg>
                      )}
                    </div>
                    <div className="style-card-title">{style.name}</div>
                    <p className="style-card-desc">{style.description}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Section 2: Study Goals */}
          <div className="selection-section">
            <label className="selection-label" id="study-goals-label">
              What are your key study goals? (Multi-select)
            </label>
            <div
              className="goals-list"
              role="group"
              aria-labelledby="study-goals-label"
            >
              {STUDY_GOALS.map((goal) => {
                const isSelected = selectedGoals.includes(goal);
                return (
                  <button
                    key={goal}
                    type="button"
                    role="checkbox"
                    aria-label={goal}
                    aria-checked={isSelected}
                    className={`goal-row-btn ${isSelected ? 'selected' : ''}`}
                    onClick={() => toggleGoal(goal)}
                  >
                    <div
                      className={`goal-checkbox-box ${isSelected ? 'checked' : ''}`}
                      aria-hidden="true"
                    >
                      {isSelected && (
                        <svg
                          viewBox="0 0 16 16"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="goal-check-icon"
                        >
                          <polyline points="3.5 8.5 6.5 11.5 12.5 5" />
                        </svg>
                      )}
                    </div>
                    <span className="goal-text-label">{goal}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Footer Navigation */}
          <div className="onboarding-footer-row has-back">
            <button
              type="button"
              className="back-btn"
              onClick={handleBack}
            >
              Back
            </button>

            <button
              type="submit"
              className="continue-btn"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="btn-spinner" aria-label="Saving..." />
              ) : (
                <>
                  <span>Continue</span>
                  <span aria-hidden="true">&rarr;</span>
                </>
              )}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
};
