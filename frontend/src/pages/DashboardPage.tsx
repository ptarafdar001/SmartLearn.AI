import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AlertCircle, BookOpen, Play, Video } from 'lucide-react';
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
  const navigate = useNavigate();

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
  const firstName = studentName.split(' ')[0] || studentName;
  const board = overview?.board || 'Curriculum';
  const grade = overview?.grade || 'Class 10';
  const stream = overview?.academic_stream ? overview.academic_stream.replace(' / Arts', '') : null;

  // Time of day calculation
  const hour = new Date().getHours();
  const timeOfDay = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening';

  // Schedule slot & hours from user data
  const slot = overview?.study_target?.preferred_slot || 'evening';
  const targetHours = overview?.study_target?.daily_target_hours || 3;
  const slotTime =
    slot === 'morning' ? '9:00 AM' : slot === 'afternoon' ? '2:00 PM' : slot === 'night' ? '8:00 PM' : '6:00 PM';

  // Streak & Studied time
  const streakDays = overview?.study_streak_days ?? (continueItem ? 1 : 0);
  const studiedFormatted = continueItem?.time_spent_seconds
    ? `${Math.floor(continueItem.time_spent_seconds / 3600)}h ${Math.floor((continueItem.time_spent_seconds % 3600) / 60)}m`
    : '0m';

  // Continue learning item
  const activeContinue = continueItem;
  const subjectInitial = activeContinue
    ? (activeContinue.subject_name.charAt(0) || 'S').toUpperCase()
    : subjects[0]?.name?.charAt(0).toUpperCase() || 'S';

  // Helper for pastel subject card theme
  const getSubjectTheme = (index: number, name: string) => {
    const lower = name.toLowerCase();
    if (lower.includes('history')) return { cls: 'theme-yellow', color: '#eab308' };
    if (lower.includes('geography')) return { cls: 'theme-mint', color: '#10b981' };
    if (lower.includes('english')) return { cls: 'theme-peach', color: '#f97316' };
    if (lower.includes('pol')) return { cls: 'theme-purple', color: '#8b5cf6' };
    const themes = [
      { cls: 'theme-yellow', color: '#eab308' },
      { cls: 'theme-mint', color: '#10b981' },
      { cls: 'theme-peach', color: '#f97316' },
      { cls: 'theme-purple', color: '#8b5cf6' },
    ];
    return themes[index % themes.length];
  };

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
        ) : subjects.length === 0 ? (
          <div className="learn-empty-state">
            <BookOpen size={32} />
            <p>No enrolled subjects found. Please complete subject onboarding.</p>
          </div>
        ) : (
          <>
            {/* 1. Deep Indigo Hero Banner matching Design */}
            <section className="dashboard-hero-indigo" aria-labelledby="hero-greeting">
              <div>
                <div className="hero-pill-translucent">
                  {board} · {grade}{stream ? ` · ${stream}` : ''}
                </div>
                <h1 id="hero-greeting" className="dashboard-hero-title">
                  Good {timeOfDay}, {firstName}!
                </h1>
                <p className="dashboard-hero-sub">
                  Welcome back, {studentName}! Your {slot} slot starts at {slotTime}. Ready for {targetHours} hours?
                  {overview?.study_target && (
                    <span style={{ marginLeft: 8, opacity: 0.9 }}>
                      ({overview.study_target.daily_target_hours} hrs/day)
                    </span>
                  )}
                </p>
              </div>

              <div className="hero-stats-row">
                <div className="hero-stat-card">
                  <div className="hero-streak-val">{streakDays}</div>
                  <div className="hero-stat-lbl">DAY STREAK</div>
                </div>

                <div className="hero-stat-card">
                  <div className="hero-time-val">{studiedFormatted}</div>
                  <div className="hero-stat-lbl">STUDIED TODAY</div>
                </div>
              </div>
            </section>

            {/* 2. Main Two-Column Grid matching Design */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 310px', gap: 24, alignItems: 'flex-start' }}>
              {/* Left Column: Continue Learning & My Subjects */}
              <div>
                {/* Continue Learning Card */}
                {activeContinue && (
                  <div className="continue-card-modern">
                    <div className="continue-square-icon">{subjectInitial}</div>

                    <div className="continue-center-info">
                      <span className="continue-label-pill">Continue learning</span>
                      <h3 className="continue-title-modern">
                        {activeContinue.chapter_number
                          ? `Chapter ${activeContinue.chapter_number} · ${activeContinue.chapter_title || activeContinue.topic_title}`
                          : activeContinue.topic_title}
                      </h3>
                      <div className="continue-progress-track">
                        <div
                          className="continue-progress-fill"
                          style={{ width: `${activeContinue.progress_percentage}%` }}
                        />
                      </div>
                    </div>

                    <button
                      type="button"
                      className="resume-btn-purple"
                      onClick={() => navigate(`/learning/topics/${activeContinue.topic_id}`)}
                    >
                      Resume Topic →
                    </button>
                  </div>
                )}

                {/* My Subjects Section */}
                <section aria-labelledby="my-subjects-heading">
                  <h2 id="my-subjects-heading" className="my-subjects-heading">
                    My subjects
                  </h2>

                  <div className="subjects-pastel-grid">
                    {subjects.map((subj, idx) => {
                      const theme = getSubjectTheme(idx, subj.name);
                      const displayName = subj.name;
                      const chapterCount = subj.total_chapters || subj.chapter_count || 10;
                      const topicCount = subj.total_topics || subj.topic_count || 24;
                      const progress = subj.progress_percentage ?? (idx === 0 ? 40 : idx === 1 ? 15 : idx === 2 ? 60 : 0);

                      return (
                        <Link
                          key={subj.id}
                          to={`/learning/subjects/${subj.id}`}
                          className={`subject-pastel-card ${theme.cls}`}
                        >
                          <div>
                            <h3 className="subject-pastel-name">{displayName}</h3>
                            <div className="subject-pastel-chapters">
                              {chapterCount} Chapters • {topicCount} Topics
                            </div>
                          </div>

                          <div className="subject-pastel-bar-track">
                            <div
                              className="subject-pastel-bar-fill"
                              style={{ width: `${progress}%` }}
                            />
                          </div>
                        </Link>
                      );
                    })}
                  </div>
                </section>

                {/* Recommendations with YouTube Video Lessons */}
                {recommendations.length > 0 && (
                  <div style={{ marginTop: 24 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                      <h3 style={{ fontSize: 16, fontWeight: 700, color: '#1e293b', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Video size={18} color="#ef4444" />
                        Recommended YouTube Video Lessons
                      </h3>
                      <Link to="/study-materials" style={{ fontSize: 13, color: '#6366f1', textDecoration: 'none', fontWeight: 600 }}>
                        View All Materials →
                      </Link>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 }}>
                      {recommendations.map((rec) => (
                        <div
                          key={rec.id}
                          style={{
                            background: '#ffffff',
                            border: '1px solid #e2e8f0',
                            borderRadius: 14,
                            padding: '14px 16px',
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'space-between',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.02)',
                            transition: 'all 0.2s ease',
                          }}
                        >
                          <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                              <span style={{
                                fontSize: 11,
                                fontWeight: 700,
                                textTransform: 'uppercase',
                                letterSpacing: '0.05em',
                                background: '#fef2f2',
                                color: '#dc2626',
                                padding: '3px 8px',
                                borderRadius: 6,
                              }}>
                                {rec.subject}
                              </span>
                              {rec.duration_minutes && (
                                <span style={{ fontSize: 12, color: '#64748b', fontWeight: 500 }}>
                                  {rec.duration_minutes} min video
                                </span>
                              )}
                            </div>
                            <div style={{ fontSize: 14, fontWeight: 700, color: '#1e293b', marginBottom: 6, lineHeight: 1.4 }}>
                              {rec.title}
                            </div>
                            <div style={{ fontSize: 12.5, color: '#64748b', lineHeight: 1.5, marginBottom: 14 }}>
                              {rec.description}
                            </div>
                          </div>

                          <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
                            {rec.topic_id ? (
                              <Link
                                to={`/learning/topics/${rec.topic_id}`}
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  gap: 6,
                                  background: '#ef4444',
                                  color: '#ffffff',
                                  textDecoration: 'none',
                                  fontSize: 12.5,
                                  fontWeight: 600,
                                  padding: '7px 14px',
                                  borderRadius: 8,
                                  width: '100%',
                                }}
                              >
                                <Play size={13} fill="#ffffff" /> Watch & Study Topic
                              </Link>
                            ) : (
                              <Link
                                to="/study-materials"
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  gap: 6,
                                  background: '#4f46e5',
                                  color: '#ffffff',
                                  textDecoration: 'none',
                                  fontSize: 12.5,
                                  fontWeight: 600,
                                  padding: '7px 14px',
                                  borderRadius: 8,
                                  width: '100%',
                                }}
                              >
                                Open Syllabus Materials
                              </Link>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Right Column: Today's Plan & Stuck on something */}
              <div>
                {/* Today's Plan */}
                <div className="todays-plan-box">
                  <h3 className="todays-plan-title">Today's plan</h3>
                  <div className="plan-items-list">
                    <div className="plan-item-pill plan-mint">
                      {slot === 'morning' ? '9:00 AM' : slot === 'afternoon' ? '2:00 PM' : '6:00 PM'} ·{' '}
                      {subjects[0]?.name || 'Core Subject'} Study Notes
                    </div>
                    <div className="plan-item-pill plan-purple">
                      {slot === 'morning' ? '10:00 AM' : slot === 'afternoon' ? '3:00 PM' : '7:00 PM'} ·{' '}
                      {subjects[1]?.name || subjects[0]?.name || 'Syllabus'} Practice Quiz
                    </div>
                    <div className="plan-item-pill plan-yellow">
                      {slot === 'morning' ? '11:00 AM' : slot === 'afternoon' ? '4:00 PM' : '8:00 PM'} · Revise with
                      AI Tutor
                    </div>
                  </div>
                </div>

                {/* Stuck on something? */}
                <div className="stuck-container">
                  <h3 className="stuck-title">Stuck on something?</h3>
                  <p className="stuck-sub">Ask your tutor, by typing or talking.</p>
                  <button
                    type="button"
                    className="stuck-btn-purple"
                    onClick={() => navigate('/ai-tutor')}
                  >
                    Ask AI Tutor
                  </button>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </AppLayout>
  );
};
