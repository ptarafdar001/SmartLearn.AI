import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { onboardingService } from '../../services/onboarding';
import { OnboardingNavbar } from '../../components/onboarding/OnboardingNavbar';
import { OnboardingProgress } from '../../components/onboarding/OnboardingProgress';
import { Alert } from '../../components/common/Alert';
import {
  getCurriculumSubjects,
  checkMutualExclusion,
} from '../../data/curriculum';
import '../../styles/onboarding.css';

interface StreamCardMeta {
  id: string;
  name: string;
  description: string;
}

const STREAM_CARDS: StreamCardMeta[] = [
  {
    id: 'Science',
    name: 'Science',
    description: 'Medical or Non-Medical tracks',
  },
  {
    id: 'Commerce',
    name: 'Commerce',
    description: 'Business, Economics & Finance',
  },
  {
    id: 'Humanities / Arts',
    name: 'Arts & Humanities',
    description: 'Literature, History & Social Science',
  },
];

export const Step2Page: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Retrieve Step 1 selections from navigation state or localStorage
  const step1Context = (() => {
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

  const studentBoard = step1Context?.board || 'CBSE';
  const studentGrade = step1Context?.grade || 'Class 11';
  const studentState = step1Context?.state || null;
  const initialStream = step1Context?.academic_stream || '';

  const isSeniorSecondary =
    studentGrade === 'Class 11' || studentGrade === 'Class 12';

  const [selectedStream, setSelectedStream] = useState<string>(
    isSeniorSecondary ? initialStream : ''
  );
  const [selectedSubjectIds, setSelectedSubjectIds] = useState<string[]>(() => {
    const saved = step1Context?.selectedSubjectIds;
    if (Array.isArray(saved) && saved.length > 0) {
      const cur = getCurriculumSubjects({
        board: studentBoard,
        grade: studentGrade,
        stream: isSeniorSecondary ? initialStream : null,
        state: studentState,
      });
      const validSet = new Set(cur.subjects.map((s) => s.id));
      return saved.filter((id: string) => validSet.has(id));
    }
    return [];
  });

  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Derive subjects dynamically from the verified curriculum engine
  const curriculumResult = getCurriculumSubjects({
    board: studentBoard,
    grade: studentGrade,
    stream: isSeniorSecondary ? selectedStream : null,
    state: studentState,
  });

  const availableSubjects = curriculumResult.subjects;

  const handleStreamChange = (streamName: string) => {
    if (selectedStream !== streamName) {
      setSelectedStream(streamName);
      // Derive subjects for the newly selected stream
      const newCurriculum = getCurriculumSubjects({
        board: studentBoard,
        grade: studentGrade,
        stream: streamName,
        state: studentState,
      });
      const validNewIds = new Set(newCurriculum.subjects.map((s) => s.id));
      // Clear previously selected subjects that are no longer valid
      setSelectedSubjectIds((prev) => prev.filter((id) => validNewIds.has(id)));
      setError(null);
    }
  };

  const handleBack = () => {
    navigate('/onboarding/step1', {
      state: {
        board: studentBoard,
        grade: studentGrade,
        state: studentState,
        academic_stream: selectedStream,
        selectedSubjectIds,
      },
    });
  };

  const toggleSubject = (subjectId: string) => {
    setError(null);

    if (selectedSubjectIds.includes(subjectId)) {
      setSelectedSubjectIds((prev) => prev.filter((id) => id !== subjectId));
      return;
    }

    // Enforce mutual exclusion rules (e.g. Math Standard vs Math Basic, Math vs Applied Math)
    const exclusionConflict = checkMutualExclusion(
      subjectId,
      selectedSubjectIds,
      availableSubjects
    );

    if (exclusionConflict) {
      setError(exclusionConflict);
      return;
    }

    setSelectedSubjectIds((prev) => [...prev, subjectId]);
  };

  const validate = (): boolean => {
    if (isSeniorSecondary && !selectedStream) {
      setError('Please select your academic stream.');
      return false;
    }
    if (selectedSubjectIds.length === 0) {
      setError('Please select at least one subject to learn.');
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
      // Map subject IDs to official display names for backend contract
      const subjectNames = selectedSubjectIds
        .map((id) => availableSubjects.find((s) => s.id === id)?.name)
        .filter((name): name is string => Boolean(name));

      await onboardingService.submitStep2({
        academic_stream: isSeniorSecondary ? selectedStream : null,
        subjects: subjectNames,
      });

      // Update localStorage so returning back from Step 3 preserves Step 2 selections
      const step2State = {
        board: studentBoard,
        grade: studentGrade,
        state: studentState,
        academic_stream: selectedStream,
        selectedSubjectIds,
        selectedSubjectNames: subjectNames,
      };

      try {
        const stored = localStorage.getItem('smartlearn_onboarding_step1');
        const prev = stored ? JSON.parse(stored) : {};
        localStorage.setItem(
          'smartlearn_onboarding_step1',
          JSON.stringify({ ...prev, ...step2State })
        );
      } catch {
        // Ignore localStorage error
      }

      // Navigate to Step 3 with state
      navigate('/onboarding/step3', { state: step2State });
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
          step={2}
          totalSteps={4}
          stepTitle="Stream & Subjects"
          percentage={50}
        />

        <h1 className="onboarding-title">
          {isSeniorSecondary
            ? 'Choose your stream and subjects'
            : 'Select your subjects'}
        </h1>
        <p className="onboarding-subtitle">
          {isSeniorSecondary
            ? 'Stream selections help us formulate relevant recommendations for competitive exams like JEE, NEET, or CUET.'
            : `We'll customize your syllabus and mock test series based on ${studentBoard} ${studentGrade} guidelines.`}
        </p>

        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

        {curriculumResult.notice && !error && (
          <div
            style={{
              padding: '10px 16px',
              marginBottom: 20,
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: 8,
              fontSize: 13,
              color: '#64748b',
            }}
          >
            {curriculumResult.notice}
          </div>
        )}

        <form onSubmit={handleContinue} noValidate>
          {/* Section 1: Academic Stream (Only shown for Classes 11 & 12) */}
          {isSeniorSecondary && (
            <div className="selection-section">
              <label className="selection-label" id="stream-label">
                Your Academic Stream
              </label>
              <div
                className="stream-cards-grid"
                role="radiogroup"
                aria-labelledby="stream-label"
              >
                {STREAM_CARDS.map((stream) => {
                  const isSelected = selectedStream === stream.id;
                  return (
                    <button
                      key={stream.id}
                      type="button"
                      role="radio"
                      aria-label={stream.id}
                      aria-checked={isSelected}
                      className={`stream-large-card ${isSelected ? 'selected' : ''}`}
                      onClick={() => handleStreamChange(stream.id)}
                    >
                      <div className="stream-card-badge" aria-hidden="true">
                        {stream.id === 'Science' && (
                          <svg
                            viewBox="0 0 24 24"
                            width="22"
                            height="22"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          >
                            <circle cx="12" cy="12" r="2.5" fill="currentColor" />
                            <ellipse cx="12" cy="12" rx="9" ry="3.5" transform="rotate(30 12 12)" />
                            <ellipse cx="12" cy="12" rx="9" ry="3.5" transform="rotate(90 12 12)" />
                            <ellipse cx="12" cy="12" rx="9" ry="3.5" transform="rotate(150 12 12)" />
                          </svg>
                        )}
                        {stream.id === 'Commerce' && (
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
                            <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
                            <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
                          </svg>
                        )}
                        {stream.id === 'Humanities / Arts' && (
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
                            <path d="M12 2C6.48 2 2 6.48 2 12c0 4.42 2.87 8.17 6.84 9.49.5.17.84-.28.84-.71v-.47c0-1.42 1.15-2.57 2.57-2.57h1.49c4.42 0 8-3.58 8-8 0-5.52-4.48-9.74-9.74-9.74z" />
                            <circle cx="8" cy="10" r="1.5" fill="currentColor" />
                            <circle cx="12" cy="7" r="1.5" fill="currentColor" />
                            <circle cx="16" cy="10" r="1.5" fill="currentColor" />
                          </svg>
                        )}
                      </div>

                      {isSelected && (
                        <svg
                          viewBox="0 0 16 16"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="stream-card-check"
                          aria-hidden="true"
                        >
                          <polyline points="3.5 8.5 6.5 11.5 12.5 5" />
                        </svg>
                      )}

                      <div className="stream-card-title">{stream.name}</div>
                      <p className="stream-card-desc">{stream.description}</p>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Section 2: Select Subjects to Learn */}
          <div className="selection-section">
            <label className="selection-label" id="subjects-label">
              Select Subjects to Learn
            </label>
            {isSeniorSecondary && !selectedStream ? (
              <div
                style={{
                  padding: '24px 20px',
                  borderRadius: '12px',
                  background: '#f8fafc',
                  border: '1px dashed #cbd5e1',
                  color: '#64748b',
                  fontSize: '14px',
                  textAlign: 'center',
                }}
              >
                Please choose your academic stream above to view available subjects.
              </div>
            ) : (
              <div
                className="subjects-pill-grid"
                role="group"
                aria-labelledby="subjects-label"
              >
                {availableSubjects.map((subject) => {
                  const isSelected = selectedSubjectIds.includes(subject.id);
                  return (
                    <button
                      key={subject.id}
                      type="button"
                      role="checkbox"
                      aria-label={subject.name}
                      aria-checked={isSelected}
                      className={`subject-pill-btn ${subject.cssClass || ''} ${
                        isSelected ? 'selected' : ''
                      }`}
                      onClick={() => toggleSubject(subject.id)}
                    >
                      <div className="subject-icon-box" aria-hidden="true">
                        {subject.cssClass === 'subject-math' && (
                          <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2.2">
                            <rect x="2" y="2" width="12" height="12" rx="3" />
                            <line x1="4.5" y1="8" x2="11.5" y2="8" />
                            <line x1="8" y1="4.5" x2="8" y2="11.5" />
                          </svg>
                        )}
                        {subject.cssClass === 'subject-physics' && (
                          <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="8" cy="8" r="2" fill="currentColor" />
                            <ellipse cx="8" cy="8" rx="6" ry="2.5" transform="rotate(45 8 8)" />
                            <ellipse cx="8" cy="8" rx="6" ry="2.5" transform="rotate(-45 8 8)" />
                          </svg>
                        )}
                        {subject.cssClass === 'subject-chem' && (
                          <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M6 2v4.5L2.5 13a1 1 0 0 0 .86 1.5h9.28a1 1 0 0 0 .86-1.5L10 6.5V2" />
                            <line x1="5" y1="2" x2="11" y2="2" />
                            <line x1="4.5" y1="10" x2="11.5" y2="10" />
                          </svg>
                        )}
                        {subject.cssClass === 'subject-bio' && (
                          <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M2 14s3.5-2 6.5-5.5c3-3.5 5.5-2 6.5-7.5-6 2-7.5 4.5-8 7.5-.5 3-5 5.5-5 5.5z" />
                            <line x1="2" y1="14" x2="9" y2="7" />
                          </svg>
                        )}
                        {subject.cssClass === 'subject-english' && (
                          <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2">
                            <rect x="2.5" y="2" width="11" height="12" rx="2" />
                            <line x1="5.5" y1="5.5" x2="10.5" y2="5.5" />
                            <line x1="5.5" y1="8.5" x2="10.5" y2="8.5" />
                            <line x1="5.5" y1="11.5" x2="8.5" y2="11.5" />
                          </svg>
                        )}
                        {subject.cssClass === 'subject-cs' && (
                          <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2">
                            <polyline points="5 5 2 8 5 11" />
                            <polyline points="11 5 14 8 11 11" />
                          </svg>
                        )}
                        {subject.cssClass === 'subject-hindi' && (
                          <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.8">
                            <path d="m3 5 4 5" />
                            <path d="m2 9 4-4 2-2" />
                            <path d="M1 3h9" />
                            <path d="m15 15-3.5-7-3.5 7" />
                            <path d="M9.5 12.5h4" />
                          </svg>
                        )}
                        {!subject.cssClass && (
                          <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="8" cy="8" r="6" />
                            <line x1="8" y1="5" x2="8" y2="11" />
                          </svg>
                        )}
                      </div>
                      <span>{subject.name}</span>
                    </button>
                  );
                })}
              </div>
            )}
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
