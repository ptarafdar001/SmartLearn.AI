import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  BookOpen,
  Clock,
  ArrowRight,
  Target,
  Calendar,
  Sparkles,
  Bot,
  PlayCircle,
  LogOut,
  AlertCircle,
  TrendingUp,
} from 'lucide-react';
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
  const overallProgress = overview?.overall_progress_percentage ?? 0;

  return (
    <div className="learn-layout" role="region" aria-label="Student Learning Dashboard">
      {/* Top Navigation */}
      <header className="learn-nav">
        <div className="learn-nav-container">
          <Link to="/dashboard" className="learn-nav-brand" aria-label="SmartLearn.AI Home">
            <BrandLogo size="sm" />
            <span className="learn-brand-text">SmartLearn.AI</span>
          </Link>

          <div className="learn-nav-actions">
            <div className="learn-user-pill" aria-label={`Logged in as ${studentName}`}>
              <div className="learn-user-avatar" aria-hidden="true">
                {studentName.charAt(0).toUpperCase()}
              </div>
              <span className="learn-user-name">{studentName}</span>
              <span className="learn-board-pill">{board} • {grade}</span>
            </div>

            <button
              type="button"
              className="learn-signout-btn"
              onClick={logout}
              aria-label="Sign out of your account"
            >
              <LogOut size={14} />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="learn-container">
        {error && (
          <div className="learn-error-box" role="alert">
            <AlertCircle size={18} className="text-amber-600" />
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
            {/* Hero Greeting Section */}
            <section className="learn-hero" aria-labelledby="hero-greeting">
              <div className="learn-hero-top">
                <div className="learn-hero-badge">
                  <span>{board}</span>
                  <span className="hero-badge-sep">•</span>
                  <span>{grade}</span>
                  {stream && (
                    <>
                      <span className="hero-badge-sep">•</span>
                      <span>{stream}</span>
                    </>
                  )}
                </div>

                <div className="learn-hero-date">
                  <Calendar size={14} />
                  <span>Academic Year 2026–27</span>
                </div>
              </div>

              <h1 id="hero-greeting" className="learn-hero-title">
                Welcome back, {studentName}!
              </h1>

              <p className="learn-hero-subtitle">
                Continue your syllabus-aligned study, explore interactive lesson materials, and test your understanding.
              </p>

              {/* Metrics Grid */}
              <div className="learn-hero-stats">
                <div className="learn-hero-stat-card">
                  <div className="stat-icon-wrap stat-icon-primary">
                    <TrendingUp size={18} />
                  </div>
                  <div>
                    <span className="learn-hero-stat-val">
                      {overallProgress !== null ? `${overallProgress}%` : '0%'}
                    </span>
                    <span className="learn-hero-stat-label">Overall Progress</span>
                  </div>
                </div>

                <div className="learn-hero-stat-card">
                  <div className="stat-icon-wrap stat-icon-info">
                    <BookOpen size={18} />
                  </div>
                  <div>
                    <span className="learn-hero-stat-val">{subjects.length}</span>
                    <span className="learn-hero-stat-label">Enrolled Subjects</span>
                  </div>
                </div>

                {overview?.study_target && (
                  <div className="learn-hero-stat-card">
                    <div className="stat-icon-wrap stat-icon-success">
                      <Clock size={18} />
                    </div>
                    <div>
                      <span className="learn-hero-stat-val">
                        {overview.study_target.daily_target_hours} hrs/day
                      </span>
                      <span className="learn-hero-stat-label">
                        Study Target ({overview.study_target.preferred_slot})
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </section>

            {/* Main Dashboard Grid */}
            <div className="dashboard-columns-layout">
              {/* Left/Main Column: Continue Learning & Enrolled Subjects */}
              <div className="dashboard-main-col">
                {/* Continue Learning Widget */}
                {continueItem && (
                  <section className="learn-section" aria-labelledby="continue-learning-title">
                    <div className="learn-section-header">
                      <h2 id="continue-learning-title" className="learn-section-title">
                        <PlayCircle size={18} className="section-title-icon" />
                        <span>Continue Learning</span>
                      </h2>
                    </div>

                    <div className="continue-card">
                      <div className="continue-card-info">
                        <div className="continue-tags-row">
                          <span className="continue-tag">{continueItem.subject_name}</span>
                          <span className="continue-chapter-tag">{continueItem.chapter_title}</span>
                        </div>

                        <h3 className="continue-title">{continueItem.topic_title}</h3>

                        <div className="continue-meta">
                          <span className="continue-meta-item">
                            <Clock size={13} />
                            <span>Est. {continueItem.estimated_minutes} mins</span>
                          </span>
                          <span className="continue-meta-sep">•</span>
                          <span className="continue-meta-item">
                            <span>Progress: {continueItem.progress_percentage}%</span>
                          </span>
                        </div>

                        <div className="continue-progress-bar">
                          <div
                            className="continue-progress-fill"
                            style={{ width: `${continueItem.progress_percentage}%` }}
                          />
                        </div>
                      </div>

                      <Link
                        to={`/learning/topics/${continueItem.topic_id}`}
                        className="continue-action-btn"
                        aria-label={`Resume learning: ${continueItem.topic_title}`}
                      >
                        <span>Resume Topic →</span>
                      </Link>
                    </div>
                  </section>
                )}

                {/* Enrolled Subjects Section */}
                <section className="learn-section" aria-labelledby="enrolled-subjects-title">
                  <div className="learn-section-header">
                    <h2 id="enrolled-subjects-title" className="learn-section-title">
                      <BookOpen size={18} className="section-title-icon" />
                      <span>Your Enrolled Subjects</span>
                    </h2>
                  </div>

                  {subjects.length === 0 ? (
                    <div className="learn-empty-state">
                      <BookOpen size={32} className="empty-state-icon" />
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
                            <div className="subject-card-body">
                              <div className="subject-card-header">
                                <h3 className="subject-name">{subj.name}</h3>
                                <span className="subject-badge">{subj.board}</span>
                              </div>

                              <p className="subject-desc">
                                {subj.description ||
                                  `Official CISCE curriculum for ${subj.grade} (${subj.board}).`}
                              </p>

                              <div className="progress-container">
                                <div className="progress-header">
                                  <span>Syllabus Completion</span>
                                  <span className="progress-pct-val">{pct}%</span>
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
                              <span className="subject-counts">
                                {subj.total_chapters || subj.chapter_count || 0} Chapters •{' '}
                                {subj.total_topics || subj.topic_count || 0} Topics
                              </span>
                              <span className="subject-explore-link">
                                <span>Explore →</span>
                              </span>
                            </div>
                          </Link>
                        );
                      })}
                    </div>
                  )}
                </section>
              </div>

              {/* Right Sidebar: AI Tutor Callout, Study Schedule & Recommendations */}
              <aside className="dashboard-side-col">
                {/* AI Tutor Feature Spotlight Card */}
                <div className="ai-tutor-spotlight-card">
                  <div className="tutor-spotlight-header">
                    <div className="tutor-spotlight-icon">
                      <Bot size={20} />
                    </div>
                    <div>
                      <h3 className="tutor-spotlight-title">Curriculum AI Tutor</h3>
                      <span className="tutor-spotlight-subtitle">Ready on every topic</span>
                    </div>
                  </div>
                  <p className="tutor-spotlight-desc">
                    Get instant, syllabus-grounded explanations, step-by-step doubt resolution, and conversational voice tutoring.
                  </p>
                  {subjects.length > 0 && (
                    <Link
                      to={`/learning/subjects/${subjects[0].id}`}
                      className="tutor-spotlight-action"
                    >
                      <span>Open Topic & Ask Tutor</span>
                      <ArrowRight size={14} />
                    </Link>
                  )}
                </div>

                {/* Daily Study Commitment Card */}
                {overview?.study_target && (
                  <div className="study-schedule-card">
                    <div className="study-schedule-header">
                      <Target size={16} className="text-indigo-600" />
                      <h3 className="study-schedule-title">Daily Study Commitment</h3>
                    </div>
                    <div className="study-schedule-details">
                      <div className="schedule-detail-row">
                        <span className="schedule-detail-label">Target Study Time:</span>
                        <span className="schedule-detail-val">{overview.study_target.daily_target_hours} Hours</span>
                      </div>
                      <div className="schedule-detail-row">
                        <span className="schedule-detail-label">Preferred Time Slot:</span>
                        <span className="schedule-detail-val capitalize">{overview.study_target.preferred_slot}</span>
                      </div>
                      {overview.study_target.available_days && (
                        <div className="schedule-detail-row">
                          <span className="schedule-detail-label">Active Days:</span>
                          <span className="schedule-detail-val">{overview.study_target.available_days.length} days/week</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Recommendations Section */}
                {recommendations.length > 0 && (
                  <section className="learn-section" aria-labelledby="recommendations-title">
                    <div className="learn-section-header">
                      <h2 id="recommendations-title" className="learn-section-title">
                        <Sparkles size={16} className="section-title-icon text-indigo-600" />
                        <span>Recommended Next Steps</span>
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
              </aside>
            </div>
          </>
        )}
      </main>
    </div>
  );
};
