import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { BrandLogo } from '../components/common/BrandLogo';
import {
  fetchContinueLearning,
  fetchDashboardOverview,
  fetchEnrolledSubjects,
  fetchRecommendations,
} from '../services/learning';
import type {
  ContinueLearningItem,
  DashboardOverview,
  RecommendationItem,
  SubjectSummary,
} from '../types/learning';
import '../styles/learning.css';

export const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth();

  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [subjects, setSubjects] = useState<SubjectSummary[]>([]);
  const [continueItem, setContinueItem] = useState<ContinueLearningItem | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadDashboardData() {
      try {
        setLoading(true);
        setError(null);

        const [overviewData, subjectsData, continueData, recsData] = await Promise.all([
          fetchDashboardOverview().catch(() => null),
          fetchEnrolledSubjects().catch(() => []),
          fetchContinueLearning().catch(() => null),
          fetchRecommendations().catch(() => ({ recommendations: [] })),
        ]);

        if (isMounted) {
          setOverview(overviewData);
          setSubjects(subjectsData);
          setContinueItem(continueData);
          setRecommendations(recsData?.recommendations || []);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to load dashboard metrics.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadDashboardData();

    return () => {
      isMounted = false;
    };
  }, []);

  const studentName = overview?.full_name || user?.full_name || 'Student';
  const board = overview?.board || 'ISC';
  const grade = overview?.grade || 'Class 11';
  const stream = overview?.academic_stream || 'Humanities';
  const overallProgress = overview?.overall_progress_percentage ?? null;

  return (
    <div className="learn-layout" role="region" aria-label="Student Learning Dashboard">
      {/* Top Navigation */}
      <header className="learn-nav">
        <div className="learn-nav-container">
          <Link to="/dashboard" className="learn-nav-brand" aria-label="SmartLearn.AI Home">
            <BrandLogo size="sm" />
            <span style={{ fontWeight: 700, fontSize: '18px', color: '#0f172a' }}>
              SmartLearn.AI
            </span>
          </Link>
          <div className="learn-nav-actions">
            <div className="learn-user-pill" aria-label={`Logged in as ${studentName}`}>
              <div className="learn-user-avatar" aria-hidden="true">
                {studentName.charAt(0).toUpperCase()}
              </div>
              <span>{studentName}</span>
            </div>
            <button
              type="button"
              className="learn-signout-btn"
              onClick={logout}
              aria-label="Sign out of your account"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="learn-container">
        {error && (
          <div className="learn-error-box" role="alert">
            <span aria-hidden="true">⚠️</span>
            <div>
              <strong>Error Loading Dashboard:</strong> {error}
            </div>
          </div>
        )}

        {loading ? (
          <div className="learn-loading-container" aria-live="polite">
            <div className="learn-spinner" aria-hidden="true" />
            <p>Loading your personalized learning dashboard...</p>
          </div>
        ) : (
          <>
            {/* Hero Greeting */}
            <section className="learn-hero" aria-labelledby="hero-greeting">
              <div className="learn-hero-badge">
                {board} • {grade} {stream ? `• ${stream}` : ''}
              </div>
              <h1 id="hero-greeting" className="learn-hero-title">
                Welcome back, {studentName}!
              </h1>
              <p className="learn-hero-subtitle">
                Continue your learning journey with syllabus-aligned chapters, interactive video
                lessons, and verified study notes.
              </p>

              <div className="learn-hero-stats">
                <div className="learn-hero-stat-card">
                  <span className="learn-hero-stat-val">
                    {overallProgress !== null ? `${overallProgress}%` : '0%'}
                  </span>
                  <span className="learn-hero-stat-label">Overall Progress</span>
                </div>

                <div className="learn-hero-stat-card">
                  <span className="learn-hero-stat-val">{subjects.length}</span>
                  <span className="learn-hero-stat-label">Enrolled Subjects</span>
                </div>

                {overview?.study_target && (
                  <div className="learn-hero-stat-card">
                    <span className="learn-hero-stat-val">
                      {overview.study_target.daily_target_hours} hrs/day
                    </span>
                    <span className="learn-hero-stat-label">
                      Study Target ({overview.study_target.preferred_slot})
                    </span>
                  </div>
                )}
              </div>
            </section>

            {/* Continue Learning Widget */}
            {continueItem && (
              <section className="learn-section" aria-labelledby="continue-learning-title">
                <div className="learn-section-header">
                  <h2 id="continue-learning-title" className="learn-section-title">
                    <span aria-hidden="true">▶️</span> Continue Learning
                  </h2>
                </div>
                <div className="continue-card">
                  <div className="continue-card-info">
                    <span className="continue-tag">{continueItem.subject_name}</span>
                    <h3 className="continue-title">{continueItem.topic_title}</h3>
                    <div className="continue-meta">
                      <span>Chapter: {continueItem.chapter_title}</span>
                      <span>•</span>
                      <span>Progress: {continueItem.progress_percentage}%</span>
                      <span>•</span>
                      <span>Est. {continueItem.estimated_minutes} mins</span>
                    </div>
                  </div>
                  <Link
                    to={`/learning/topics/${continueItem.topic_id}`}
                    className="continue-action-btn"
                    aria-label={`Resume learning: ${continueItem.topic_title}`}
                  >
                    Resume Topic →
                  </Link>
                </div>
              </section>
            )}

            {/* Enrolled Subjects */}
            <section className="learn-section" aria-labelledby="enrolled-subjects-title">
              <div className="learn-section-header">
                <h2 id="enrolled-subjects-title" className="learn-section-title">
                  <span aria-hidden="true">📚</span> Your Enrolled Subjects
                </h2>
              </div>

              {subjects.length === 0 ? (
                <div className="learn-empty-state">
                  <p>No enrolled subjects found. Please complete subject selection.</p>
                </div>
              ) : (
                <div className="subjects-grid">
                  {subjects.map((subj) => {
                    const pct = subj.progress_percentage ?? 0;
                    return (
                      <Link
                        key={subj.id}
                        to={`/learning/subjects/${subj.id}`}
                        className="subject-card"
                        aria-label={`Subject: ${subj.name}, ${pct}% completed, click to view syllabus`}
                      >
                        <div>
                          <div className="subject-card-header">
                            <h3 className="subject-name">{subj.name}</h3>
                            <span className="subject-badge">{subj.board}</span>
                          </div>
                          <p className="subject-desc">
                            {subj.description ||
                              `Official curriculum for ${subj.grade} (${subj.board}).`}
                          </p>

                          <div className="progress-container">
                            <div className="progress-header">
                              <span>Syllabus Completion</span>
                              <span>{pct}%</span>
                            </div>
                            <div
                              className="progress-bar-bg"
                              role="progressbar"
                              aria-valuenow={pct}
                              aria-valuemin={0}
                              aria-valuemax={100}
                              aria-label={`${subj.name} completion: ${pct}%`}
                            >
                              <div className="progress-bar-fill" style={{ width: `${pct}%` }} />
                            </div>
                          </div>
                        </div>

                        <div className="subject-card-footer">
                          <span>
                            {subj.total_chapters || subj.chapter_count || 0} Chapters •{' '}
                            {subj.total_topics || subj.topic_count || 0} Topics
                          </span>
                          <span className="subject-explore-link">Explore →</span>
                        </div>
                      </Link>
                    );
                  })}
                </div>
              )}
            </section>

            {/* Recommendations Section */}
            {recommendations.length > 0 && (
              <section className="learn-section" aria-labelledby="recommendations-title">
                <div className="learn-section-header">
                  <h2 id="recommendations-title" className="learn-section-title">
                    <span aria-hidden="true">💡</span> Recommended Next Steps
                  </h2>
                </div>
                <div className="recs-grid">
                  {recommendations.slice(0, 3).map((rec) => (
                    <div key={rec.id} className="rec-card">
                      <span className="rec-type-badge">
                        {rec.recommendation_type.replace('_', ' ')}
                      </span>
                      <h3 className="rec-title">{rec.title}</h3>
                      <p className="rec-desc">{rec.description}</p>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
};
