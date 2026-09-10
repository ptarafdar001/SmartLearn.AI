import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { onboardingService } from '../../services/onboarding';
import { OnboardingNavbar } from '../../components/onboarding/OnboardingNavbar';
import { OnboardingProgress } from '../../components/onboarding/OnboardingProgress';
import { Alert } from '../../components/common/Alert';
import '../../styles/onboarding.css';

interface DailyTargetOption {
  label: string;
  hours: number;
}

const DAILY_TARGETS: DailyTargetOption[] = [
  { label: '30 min', hours: 0.5 },
  { label: '1 hour', hours: 1.0 },
  { label: '2 hours', hours: 2.0 },
  { label: '3+ hours', hours: 3.0 },
];

interface StudySlotOption {
  id: string;
  name: string;
  timing: string;
}

const STUDY_SLOTS: StudySlotOption[] = [
  { id: 'Morning', name: 'Morning', timing: '6 AM - 12 PM' },
  { id: 'Afternoon', name: 'Afternoon', timing: '12 PM - 5 PM' },
  { id: 'Evening', name: 'Evening', timing: '5 PM - 9 PM' },
  { id: 'Night', name: 'Night', timing: '9 PM - 2 AM' },
];

interface WeekDayOption {
  id: string;
  label: string;
}

const WEEK_DAYS: WeekDayOption[] = [
  { id: 'Monday', label: 'Mon' },
  { id: 'Tuesday', label: 'Tue' },
  { id: 'Wednesday', label: 'Wed' },
  { id: 'Thursday', label: 'Thu' },
  { id: 'Friday', label: 'Fri' },
  { id: 'Saturday', label: 'Sat' },
  { id: 'Sunday', label: 'Sun' },
];

export const Step4Page: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { refreshUser } = useAuth();

  // Retrieve prior onboarding context from location.state or localStorage
  const prevContext = (() => {
    let context: any = {};
    try {
      const s1 = localStorage.getItem('smartlearn_onboarding_step1');
      if (s1) context = { ...context, ...JSON.parse(s1) };
    } catch {
      // Ignore
    }
    try {
      const s3 = localStorage.getItem('smartlearn_onboarding_step3');
      if (s3) context = { ...context, ...JSON.parse(s3) };
    } catch {
      // Ignore
    }
    try {
      const s4 = localStorage.getItem('smartlearn_onboarding_step4');
      if (s4) context = { ...context, ...JSON.parse(s4) };
    } catch {
      // Ignore
    }
    if (location.state) {
      context = { ...context, ...location.state };
    }
    return context;
  })();

  const [selectedTargetHours, setSelectedTargetHours] = useState<number | null>(
    typeof prevContext?.daily_target_hours === 'number'
      ? prevContext.daily_target_hours
      : null
  );

  const [selectedSlot, setSelectedSlot] = useState<string>(
    prevContext?.preferred_slot || ''
  );

  const [selectedDays, setSelectedDays] = useState<string[]>(() => {
    if (Array.isArray(prevContext?.available_days)) {
      return prevContext.available_days;
    }
    return [];
  });

  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Derived Learning Profile display values
  const studentBoard = prevContext?.board || 'CBSE';
  const studentGrade = prevContext?.grade || 'Class 11';
  const studentStream = prevContext?.academic_stream || null;
  const isSenior = studentGrade === 'Class 11' || studentGrade === 'Class 12';

  const syllabusText = isSenior && studentStream
    ? `${studentBoard} • ${studentGrade} (${studentStream})`
    : `${studentBoard} • ${studentGrade}`;

  const subjectsText = (() => {
    if (Array.isArray(prevContext?.selectedSubjectNames) && prevContext.selectedSubjectNames.length > 0) {
      return prevContext.selectedSubjectNames.join(', ');
    }
    return 'Not specified';
  })();

  const styleText = prevContext?.preferred_style || 'Not specified';

  const weeklyCommitmentText = (() => {
    if (selectedTargetHours && selectedDays.length > 0) {
      const totalWeekly = Math.round(selectedTargetHours * selectedDays.length * 10) / 10;
      const hoursLabel = selectedTargetHours === 1 ? '1 hr' : `${selectedTargetHours} hrs`;
      const daysLabel = `${selectedDays.length} days/wk`;
      return `${totalWeekly} hrs (${hoursLabel} / day, ${daysLabel})`;
    }
    return '--';
  })();

  const toggleDay = (dayId: string) => {
    setError(null);
    setSelectedDays((prev) =>
      prev.includes(dayId) ? prev.filter((d) => d !== dayId) : [...prev, dayId]
    );
  };

  const handleBack = () => {
    // Save Step 4 choices in localStorage
    try {
      localStorage.setItem(
        'smartlearn_onboarding_step4',
        JSON.stringify({
          daily_target_hours: selectedTargetHours,
          preferred_slot: selectedSlot,
          available_days: selectedDays,
        })
      );
    } catch {
      // Ignore
    }

    navigate('/onboarding/step3', {
      state: {
        ...prevContext,
        daily_target_hours: selectedTargetHours,
        preferred_slot: selectedSlot,
        available_days: selectedDays,
      },
    });
  };

  const validate = (): boolean => {
    if (selectedTargetHours === null || selectedTargetHours <= 0) {
      setError('Please select your daily study target.');
      return false;
    }
    if (!selectedSlot) {
      setError('Please select your preferred study slot.');
      return false;
    }
    if (selectedDays.length === 0) {
      setError('Please select at least one day you are available to study.');
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
      await onboardingService.submitStep4({
        daily_target_hours: selectedTargetHours!,
        preferred_slot: selectedSlot,
        available_days: selectedDays,
      });

      // Refresh authentication and onboarding status from backend
      await refreshUser();

      // Clear temporary onboarding storage keys
      try {
        localStorage.removeItem('smartlearn_onboarding_step1');
        localStorage.removeItem('smartlearn_onboarding_step3');
        localStorage.removeItem('smartlearn_onboarding_step4');
      } catch {
        // Ignore
      }

      // Navigate to the student dashboard
      navigate('/dashboard', { replace: true });
    } catch (err: any) {
      setError(
        err.message || 'Failed to complete onboarding. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="onboarding-page-container">
      <OnboardingNavbar />

      <main className="onboarding-card step4-card" role="main">
        <OnboardingProgress
          step={4}
          totalSteps={4}
          stepTitle="Study Schedule"
          percentage={100}
        />

        <h1 className="onboarding-title">Set your study schedule</h1>
        <p className="onboarding-subtitle">
          We'll set reminders and design a consistent habit streak plan based on your daily availability targets.
        </p>

        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

        <form onSubmit={handleContinue} noValidate>
          <div className="step4-layout-grid">
            {/* Left Column: Schedule Selectors */}
            <div className="step4-controls-col">
              {/* Section 1: Daily Study Target */}
              <div className="selection-section">
                <label className="selection-label" id="daily-target-label">
                  Daily Study Target
                </label>
                <div
                  className="daily-targets-grid"
                  role="radiogroup"
                  aria-labelledby="daily-target-label"
                >
                  {DAILY_TARGETS.map((target) => {
                    const isSelected = selectedTargetHours === target.hours;
                    return (
                      <button
                        key={target.label}
                        type="button"
                        role="radio"
                        aria-label={target.label}
                        aria-checked={isSelected}
                        className={`daily-target-btn ${isSelected ? 'selected' : ''}`}
                        onClick={() => {
                          setSelectedTargetHours(target.hours);
                          setError(null);
                        }}
                      >
                        {target.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Section 2: Preferred Study Slot */}
              <div className="selection-section">
                <label className="selection-label" id="study-slot-label">
                  Preferred Study Slot
                </label>
                <div
                  className="slots-grid"
                  role="radiogroup"
                  aria-labelledby="study-slot-label"
                >
                  {STUDY_SLOTS.map((slot) => {
                    const isSelected = selectedSlot === slot.id;
                    return (
                      <button
                        key={slot.id}
                        type="button"
                        role="radio"
                        aria-label={slot.name}
                        aria-checked={isSelected}
                        className={`slot-card-btn ${isSelected ? 'selected' : ''}`}
                        onClick={() => {
                          setSelectedSlot(slot.id);
                          setError(null);
                        }}
                      >
                        <div className="slot-icon-row" aria-hidden="true">
                          {slot.id === 'Morning' && (
                            <svg viewBox="0 0 24 24" className="slot-icon" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <circle cx="12" cy="12" r="5" />
                              <line x1="12" y1="1" x2="12" y2="3" />
                              <line x1="12" y1="21" x2="12" y2="23" />
                              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                              <line x1="1" y1="12" x2="3" y2="12" />
                              <line x1="21" y1="12" x2="23" y2="12" />
                              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                            </svg>
                          )}
                          {slot.id === 'Afternoon' && (
                            <svg viewBox="0 0 24 24" className="slot-icon" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M12 2v2" />
                              <path d="m4.93 4.93 1.41 1.41" />
                              <path d="M20 12h2" />
                              <path d="m19.07 4.93-1.41 1.41" />
                              <path d="M15.94 11.2a5 5 0 0 0-7.88 0A4.5 4.5 0 1 0 7 20h11a3.5 3.5 0 0 0-2.06-8.8Z" />
                            </svg>
                          )}
                          {slot.id === 'Evening' && (
                            <svg viewBox="0 0 24 24" className="slot-icon" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M17 18a5 5 0 0 0-10 0" />
                              <line x1="12" y1="9" x2="12" y2="2" />
                              <line x1="4.22" y1="10.22" x2="5.64" y2="11.64" />
                              <line x1="1" y1="18" x2="3" y2="18" />
                              <line x1="21" y1="18" x2="23" y2="18" />
                              <line x1="18.36" y1="11.64" x2="19.78" y2="10.22" />
                              <line x1="23" y1="22" x2="1" y2="22" />
                              <polyline points="8 6 12 2 16 6" />
                            </svg>
                          )}
                          {slot.id === 'Night' && (
                            <svg viewBox="0 0 24 24" className="slot-icon" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                            </svg>
                          )}
                        </div>
                        <div className="slot-name">{slot.name}</div>
                        <div className="slot-timing">{slot.timing}</div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Section 3: Weekly Availability Calendar (Mon - Sun) */}
              <div className="selection-section">
                <label className="selection-label" id="weekly-days-label">
                  Weekly availability calendar (Mon - Sun)
                </label>
                <div
                  className="days-grid"
                  role="group"
                  aria-labelledby="weekly-days-label"
                >
                  {WEEK_DAYS.map((day) => {
                    const isSelected = selectedDays.includes(day.id);
                    return (
                      <button
                        key={day.id}
                        type="button"
                        role="checkbox"
                        aria-label={day.id}
                        aria-checked={isSelected}
                        className={`day-card-btn ${isSelected ? 'selected' : ''}`}
                        onClick={() => toggleDay(day.id)}
                      >
                        <span className="day-label">{day.label}</span>
                        <div
                          className="day-circle-indicator"
                          aria-hidden="true"
                        />
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Right Column: Learning Profile Side Panel */}
            <div className="learning-profile-col">
              <div className="learning-profile-card">
                <div className="learning-profile-header">
                  <svg viewBox="0 0 24 24" className="profile-sparkle-icon" fill="currentColor" aria-hidden="true">
                    <path d="M12 2l2.4 7.2L21.6 12l-7.2 2.4L12 21.6l-2.4-7.2L2.4 12l7.2-2.4z" />
                  </svg>
                  <span>Learning Profile</span>
                </div>

                <div className="profile-item">
                  <span className="profile-item-label">Syllabus &amp; Stream</span>
                  <span className="profile-item-val">{syllabusText}</span>
                </div>

                <div className="profile-item">
                  <span className="profile-item-label">Selected Subjects</span>
                  <span className="profile-item-val">{subjectsText}</span>
                </div>

                <div className="profile-item">
                  <span className="profile-item-label">Personalization Style</span>
                  <span className="profile-item-val">{styleText}</span>
                </div>

                <div className="profile-item">
                  <span className="profile-item-label">Weekly Commitment</span>
                  <span className="profile-item-val">{weeklyCommitmentText}</span>
                </div>

                <div className="profile-ai-ready-badge" role="status">
                  <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor" aria-hidden="true">
                    <path d="M8 1l1.5 4.5L14 7l-4.5 1.5L8 13l-1.5-4.5L2 7l4.5-1.5z" />
                  </svg>
                  <span>AI Learning engine ready!</span>
                </div>
              </div>
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
                  <span>Start Learning</span>
                  <span aria-hidden="true">&#9889;</span>
                </>
              )}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
};
