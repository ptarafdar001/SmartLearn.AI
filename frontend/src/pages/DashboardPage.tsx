import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  BookOpen,
  Clock,
  ArrowRight,
  Target,
  Sparkles,
  Bot,
  PlayCircle,
  AlertCircle,
  TrendingUp,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { AppLayout } from '../components/layout/AppLayout';
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
  const { user } = useAuth();

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
    <AppLayout breadcrumbs={[{ label: 'Dashboard' }]}>
      <div className="compact-dashboard" role="region" aria-label="Student Learning Dashboard">
        {error && (
          <div className="learn-error-box" role="alert">
            <AlertCircle size={16} className="text-amber-600" />
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
            {/* 1. Compact Greeting & Key Stats Bar */}
            <section className="compact-hero-card" aria-labelledby="hero-greeting">
              <div className="compact-hero-left">
                <div className="compact-hero-badge">
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

                <h1 id="hero-greeting" className="compact-hero-title">
                  Welcome back, {studentName}!
                </h1>
                <p className="compact-hero-sub">
                  Continue your official CISCE syllabus lessons, study verified notes, and resolve doubts with your AI Tutor.
                </p>
              </div>

              <div className="compact-hero-metrics">
                <div className="compact-metric-pill">
                  <div className="stat-icon-wrap stat-icon-primary" style={{ width: 34, height: 34 }}>
                    <TrendingUp size={16} />
                  </div>
                  <div>
                    <span className="compact-metric-val">
                      {overallProgress !== null ? `${overallProgress}%` : '0%'}
                    </span>
                    <span className="compact-metric-lbl">Overall Progress</span>
                  </div>
                </div>

                <div className="compact-metric-pill">
                  <div className="stat-icon-wrap stat-icon-info" style={{ width: 34, height: 34 }}>
                    <BookOpen size={16} />
                  </div>
                  <div>
                    <span className="compact-metric-val">{subjects.length}</span>
                    <span className="compact-metric-lbl">Enrolled Subjects</span>
                  </div>
                </div>

                {overview?.study_target && (
                  <div className="compact-metric-pill">
                    <div className="stat-icon-wrap stat-icon-success" style={{ width: 34, height: 34 }}>
                      <Clock size={16} />
                    </div>
                    <div>
                      <span className="compact-metric-val">
                        {overview.study_target.daily_target_hours} hrs/day
                      </span>
                      <span className="compact-metric-lbl">
                        Study Target ({overview.study_target.preferred_slot})
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </section>

            {/* 2. Main Dashboard Grid (Fits in One Screen) */}
            <div className="compact-grid-layout">
              {/* Left Column: Continue Learning & Enrolled Subjects */}
              <div className="compact-col-main">
                {/* Continue Learning Card */}
                {continueItem && (
                  <section className="compact-section" aria-labelledby="continue-learning-title">
                    <div className="compact-section-hdr">
                      <h2 id="continue-learning-title" className="compact-section-title">
                        <PlayCircle size={16} className="text-indigo-600" />
                        <span>Continue Learning</span>
                      </h2>
                    </div>

                    <div className="compact-continue-card">
                      <div className="continue-card-info">
                        <div className="continue-tags-row">
                          <span className="continue-tag">{continueItem.subject_name}</span>
                          <span className="continue-chapter-tag">{continueItem.chapter_title}</span>
                        </div>

                        <h3 className="compact-continue-title">{continueItem.topic_title}</h3>

                        <div className="compact-continue-meta">
                          <span className="continue-meta-item">
                            <Clock size={12} />
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

                {/* Enrolled Subjects */}
                <section className="compact-section" aria-labelledby="enrolled-subjects-title">
                  <div className="compact-section-hdr">
                    <h2 id="enrolled-subjects-title" className="compact-section-title">
                      <BookOpen size={16} className="text-indigo-600" />
                      <span>Your Enrolled Subjects</span>
                    </h2>
                    <Link to="/subjects" className="compact-view-all-link">
                      <span>View All</span>
                      <ArrowRight size={12} />
                    </Link>
                  </div>

                  {subjects.length === 0 ? (
                    <div className="learn-empty-state" style={{ padding: '28px 16px' }}>
                      <BookOpen size={24} className="empty-state-icon" />
                      <p>No enrolled subjects found. Please complete subject selection.</p>
                    </div>
                  ) : (
                    <div className="compact-subjects-grid">
                      {subjects.map((subj) => {
                        const pct = subj.progress_percentage ?? 0;
                        return (
                          <Link
                            key={subj.id}
                            to={`/learning/subjects/${subj.id}`}
                            className="compact-subject-card"
                            aria-label={`Subject: ${subj.name}, ${pct}% completed, click to view syllabus`}
                          >
                            <div className="compact-subj-top">
                              <div className="compact-subj-title-wrap">
                                <h3 className="subject-name" style={{ fontSize: 16 }}>{subj.name}</h3>
                                <span className="subject-badge">{subj.board}</span>
                              </div>
                              <span className="compact-subj-pct">{pct}%</span>
                            </div>

                            <p className="compact-subj-desc">
                              {subj.description || `Official CISCE Class 11 curriculum for ${subj.name}.`}
                            </p>

                            <div className="progress-bar-bg" style={{ height: 5 }}>
                              <div className="progress-bar-fill" style={{ width: `${pct}%` }} />
                            </div>

                            <div className="compact-subj-footer">
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
              </div>

              {/* Right Column: Goal & Recommendations */}
              <div className="compact-col-side">
                {/* Today's Study Goal Card */}
                {overview?.study_target && (
                  <div className="compact-goal-card">
                    <div className="compact-card-hdr">
                      <Target size={15} className="text-indigo-600" />
                      <h3 className="compact-card-title">Today's Study Goal</h3>
                    </div>
                    <div className="compact-goal-details">
                      <div className="compact-goal-row">
                        <span>Daily Target:</span>
                        <span className="font-semibold">{overview.study_target.daily_target_hours} Hours</span>
                      </div>
                      <div className="compact-goal-row">
                        <span>Preferred Slot:</span>
                        <span className="capitalize font-semibold">{overview.study_target.preferred_slot}</span>
                      </div>
                      <div className="compact-goal-row">
                        <span>Exam Target:</span>
                        <span className="font-semibold text-emerald-600">ISC 2027 (95%)</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* AI Tutor Callout */}
                <div className="compact-tutor-banner">
                  <div className="compact-tutor-left">
                    <div className="tutor-spotlight-icon" style={{ width: 32, height: 32 }}>
                      <Bot size={18} />
                    </div>
                    <div>
                      <h3 className="compact-tutor-title">Curriculum AI Tutor</h3>
                      <span className="compact-tutor-sub">Ready for text &amp; voice doubts</span>
                    </div>
                  </div>
                  <Link to="/ai-tutor" className="compact-tutor-btn">
                    <span>Ask Tutor</span>
                    <ArrowRight size={13} />
                  </Link>
                </div>

                {/* Recommended Next Step */}
                {recommendations.length > 0 && (
                  <div className="compact-recs-box">
                    <div className="compact-card-hdr">
                      <Sparkles size={15} className="text-indigo-600" />
                      <h3 className="compact-card-title">Recommended Next Step</h3>
                    </div>

                    <div className="compact-rec-item">
                      <span className="rec-type-badge">{recommendations[0].recommendation_type.replace('_', ' ')}</span>
                      <h4 className="compact-rec-title">{recommendations[0].title}</h4>
                      <p className="compact-rec-desc">{recommendations[0].description}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </AppLayout>
  );
};
