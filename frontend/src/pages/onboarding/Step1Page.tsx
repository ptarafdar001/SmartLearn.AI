import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { onboardingService } from '../../services/onboarding';
import { OnboardingNavbar } from '../../components/onboarding/OnboardingNavbar';
import { OnboardingProgress } from '../../components/onboarding/OnboardingProgress';
import { Alert } from '../../components/common/Alert';
import { INDIAN_STATES } from '../../data/curriculum';
import '../../styles/onboarding.css';

const BOARDS = ['CBSE', 'ICSE', 'State Board', 'ISC', 'Other'];
const GRADES = [
  'Class 6',
  'Class 7',
  'Class 8',
  'Class 9',
  'Class 10',
  'Class 11',
  'Class 12',
];

export const Step1Page: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Retrieve existing Step 1 selections if returning via Back navigation or from storage
  const existingStep1 = (() => {
    if (location.state && (location.state.board || location.state.grade)) {
      return location.state;
    }
    try {
      const stored = localStorage.getItem('smartlearn_onboarding_step1');
      if (stored) return JSON.parse(stored);
    } catch {
      // Ignore localStorage errors
    }
    return null;
  })();

  const [selectedBoard, setSelectedBoard] = useState<string>(existingStep1?.board || '');
  const [selectedState, setSelectedState] = useState<string>(existingStep1?.state || '');
  const [selectedGrade, setSelectedGrade] = useState<string>(existingStep1?.grade || '');

  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const validate = (): boolean => {
    if (!selectedBoard) {
      setError('Please select your education board.');
      return false;
    }
    if (selectedBoard === 'State Board' && !selectedState) {
      setError('Please select your state.');
      return false;
    }
    if (!selectedGrade) {
      setError('Please select your class / grade.');
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
      // Step 1 only collects and submits board and grade (academic_stream is null)
      const step1Payload = {
        board: selectedBoard,
        grade: selectedGrade,
        academic_stream: null,
      };

      await onboardingService.submitStep1(step1Payload);

      // Preserve previously selected stream and subjects if returning from Step 2 for Classes 11-12
      const isSenior = selectedGrade === 'Class 11' || selectedGrade === 'Class 12';
      const prevData = (location.state as any) || existingStep1 || {};
      const frontendContext = {
        board: selectedBoard,
        grade: selectedGrade,
        state: selectedBoard === 'State Board' ? selectedState : null,
        academic_stream: isSenior ? prevData.academic_stream || null : null,
        selectedSubjectIds: isSenior ? prevData.selectedSubjectIds || [] : [],
      };

      try {
        localStorage.setItem(
          'smartlearn_onboarding_step1',
          JSON.stringify(frontendContext)
        );
      } catch {
        // Ignore localStorage errors
      }

      // Navigate to Step 2 with state
      navigate('/onboarding/step2', { state: frontendContext });
    } catch (err: any) {
      setError(
        err.message || 'Failed to save your selections. Please try again.'
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
          step={1}
          totalSteps={4}
          stepTitle="Board & Class"
          percentage={25}
        />

        <h1 className="onboarding-title">What board and class are you in?</h1>
        <p className="onboarding-subtitle">
          We'll customize your syllabus and mock test series based on your board guidelines.
        </p>

        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

        <form onSubmit={handleContinue} noValidate>
          {/* Education Board Selection */}
          <div className="selection-section">
            <label className="selection-label" id="board-label">
              Select Education Board
            </label>
            <div
              className="boards-grid"
              role="radiogroup"
              aria-labelledby="board-label"
            >
              {BOARDS.map((board) => {
                const isSelected = selectedBoard === board;
                return (
                  <button
                    key={board}
                    type="button"
                    role="radio"
                    aria-checked={isSelected}
                    className={`board-card-btn ${isSelected ? 'selected' : ''}`}
                    onClick={() => {
                      setSelectedBoard(board);
                      if (board !== 'State Board') {
                        setSelectedState('');
                      }
                      setError(null);
                    }}
                  >
                    <span>{board}</span>
                    {isSelected && (
                      <svg
                        viewBox="0 0 16 16"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="board-check-icon"
                        aria-hidden="true"
                      >
                        <polyline points="3.5 8.5 6.5 11.5 12.5 5" />
                      </svg>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* State Selection (when State Board is selected) */}
          {selectedBoard === 'State Board' && (
            <div className="selection-section">
              <label className="selection-label" htmlFor="state-select">
                Select your State
              </label>
              <select
                id="state-select"
                aria-label="Select your State"
                className="state-select-dropdown"
                value={selectedState}
                onChange={(e) => {
                  setSelectedState(e.target.value);
                  setError(null);
                }}
              >
                <option value="">-- Choose your State --</option>
                {INDIAN_STATES.map((stateName) => (
                  <option key={stateName} value={stateName}>
                    {stateName}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Class / Grade Selection */}
          <div className="selection-section">
            <label className="selection-label" id="grade-label">
              Select Class / Grade
            </label>
            <div
              className="grades-grid"
              role="radiogroup"
              aria-labelledby="grade-label"
            >
              {GRADES.map((grade) => {
                const isSelected = selectedGrade === grade;
                return (
                  <button
                    key={grade}
                    type="button"
                    role="radio"
                    aria-checked={isSelected}
                    className={`grade-pill-btn ${isSelected ? 'selected' : ''}`}
                    onClick={() => {
                      setSelectedGrade(grade);
                      setError(null);
                    }}
                  >
                    {grade}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Footer Action Row */}
          <div className="onboarding-footer-row">
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
