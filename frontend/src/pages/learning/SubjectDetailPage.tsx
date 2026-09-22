import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { BrandLogo } from '../../components/common/BrandLogo';
import { fetchSubjectDetail } from '../../services/learning';
import type { SubjectDetail } from '../../types/learning';
import '../../styles/learning.css';

export const SubjectDetailPage: React.FC = () => {
  const { subjectId } = useParams<{ subjectId: string }>();
  const { user, logout } = useAuth();

  const [subject, setSubject] = useState<SubjectDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedChapters, setExpandedChapters] = useState<Record<number, boolean>>({});

  useEffect(() => {
    let isMounted = true;

    async function loadSubject() {
      if (!subjectId) return;

      try {
        setLoading(true);
        setError(null);
        const data = await fetchSubjectDetail(Number(subjectId));
        if (isMounted) {
          setSubject(data);
          // Default first chapter expanded
          if (data.chapters.length > 0) {
            setExpandedChapters({ [data.chapters[0].id]: true });
          }
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to load subject syllabus.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadSubject();

    return () => {
      isMounted = false;
    };
  }, [subjectId]);

  const toggleChapter = (chapterId: number) => {
    setExpandedChapters((prev) => ({
      ...prev,
      [chapterId]: !prev[chapterId],
    }));
  };

  const studentName = user?.full_name || 'Student';

  return (
    <div className="learn-layout">
      {/* Top Navigation */}
      <header className="learn-nav">
        <div className="learn-nav-container">
          <Link to="/dashboard" className="learn-nav-brand" aria-label="Back to Dashboard">
            <BrandLogo size="sm" />
            <span style={{ fontWeight: 700, fontSize: '18px', color: '#0f172a' }}>
              SmartLearn.AI
            </span>
          </Link>
          <div className="learn-nav-actions">
            <div className="learn-user-pill">
              <div className="learn-user-avatar">{studentName.charAt(0).toUpperCase()}</div>
              <span>{studentName}</span>
            </div>
            <button type="button" className="learn-signout-btn" onClick={logout}>
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="learn-container">
        {/* Breadcrumb Navigation */}
        <nav className="learn-breadcrumbs" aria-label="Breadcrumbs">
          <Link to="/dashboard" className="learn-breadcrumb-link">
            Dashboard
          </Link>
          <span className="learn-breadcrumb-sep">/</span>
          <span className="learn-breadcrumb-current">{subject?.name || 'Subject'}</span>
        </nav>

        {error && (
          <div className="learn-error-box" role="alert">
            <span aria-hidden="true">⚠️</span>
            <div>
              <strong>Error Loading Subject:</strong> {error}
            </div>
          </div>
        )}

        {loading ? (
          <div className="learn-loading-container" aria-live="polite">
            <div className="learn-spinner" aria-hidden="true" />
            <p>Loading syllabus details...</p>
          </div>
        ) : subject ? (
          <>
            {/* Subject Hero */}
            <div className="subject-hero">
              <div className="subject-hero-info">
                <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                  <span className="subject-badge">{subject.board}</span>
                  <span className="subject-badge">{subject.grade}</span>
                  {subject.academic_stream && (
                    <span className="subject-badge">{subject.academic_stream}</span>
                  )}
                </div>
                <h1 className="subject-hero-title">{subject.name}</h1>
                <p className="subject-hero-desc">
                  {subject.description || 'Comprehensive syllabus aligned with official board guidelines.'}
                </p>
              </div>

              <div style={{ minWidth: '220px' }}>
                <div className="progress-header">
                  <span>Syllabus Completion</span>
                  <span>{subject.progress_percentage}%</span>
                </div>
                <div
                  className="progress-bar-bg"
                  role="progressbar"
                  aria-valuenow={subject.progress_percentage}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`Subject completion: ${subject.progress_percentage}%`}
                >
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${subject.progress_percentage}%` }}
                  />
                </div>
                <div style={{ marginTop: '8px', fontSize: '13px', color: '#64748b' }}>
                  {subject.completed_topics} of {subject.total_topics} topics completed
                </div>
              </div>
            </div>

            {/* Chapters Accordion */}
            <section aria-labelledby="syllabus-title">
              <div className="learn-section-header">
                <h2 id="syllabus-title" className="learn-section-title">
                  Chapters &amp; Topics
                </h2>
              </div>

              <div className="chapter-accordion">
                {subject.chapters.map((chapter) => {
                  const isExpanded = !!expandedChapters[chapter.id];
                  return (
                    <div key={chapter.id} className="chapter-item">
                      <button
                        type="button"
                        className="chapter-header"
                        onClick={() => toggleChapter(chapter.id)}
                        aria-expanded={isExpanded}
                        aria-controls={`chapter-topics-${chapter.id}`}
                      >
                        <div className="chapter-title-group">
                          <span className="chapter-num-badge">Ch {chapter.chapter_number}</span>
                          <div>
                            <h3 className="chapter-title">{chapter.title}</h3>
                            {chapter.description && (
                              <p
                                style={{
                                  fontSize: '13px',
                                  color: '#64748b',
                                  margin: '2px 0 0',
                                  fontWeight: 400,
                                }}
                              >
                                {chapter.description}
                              </p>
                            )}
                          </div>
                        </div>

                        <div className="chapter-progress-pill">
                          <span>
                            {chapter.completed_topics}/{chapter.total_topics} Topics
                          </span>
                          <span>{chapter.progress_percentage}%</span>
                          <span aria-hidden="true" style={{ fontSize: '12px' }}>
                            {isExpanded ? '▲' : '▼'}
                          </span>
                        </div>
                      </button>

                      {isExpanded && (
                        <div
                          id={`chapter-topics-${chapter.id}`}
                          className="topic-list"
                          role="region"
                          aria-label={`Topics for chapter ${chapter.chapter_number}`}
                        >
                          {chapter.topics.map((topic) => {
                            const status = topic.progress?.status || 'not_started';
                            return (
                              <Link
                                key={topic.id}
                                to={`/learning/topics/${topic.id}`}
                                className="topic-row"
                                aria-label={`Topic ${topic.topic_number}: ${topic.title}, status: ${status}`}
                              >
                                <div className="topic-info">
                                  <div
                                    className={`topic-status-icon status-${status.replace('_', '-')}`}
                                    aria-hidden="true"
                                  >
                                    {status === 'completed'
                                      ? '✓'
                                      : status === 'in_progress'
                                        ? '◐'
                                        : '○'}
                                  </div>
                                  <div>
                                    <h4 className="topic-title">
                                      {topic.topic_number}. {topic.title}
                                    </h4>
                                    <div className="topic-meta">
                                      <span>Est. {topic.estimated_minutes} mins</span>
                                      {topic.progress?.progress_percentage !== undefined && (
                                        <span> • {topic.progress.progress_percentage}% completed</span>
                                      )}
                                    </div>
                                  </div>
                                </div>

                                <span
                                  style={{
                                    fontSize: '13px',
                                    color: '#4f46e5',
                                    fontWeight: 600,
                                  }}
                                >
                                  {status === 'completed' ? 'Review →' : 'Study →'}
                                </span>
                              </Link>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </section>
          </>
        ) : (
          <div className="learn-empty-state">
            <p>Subject not found.</p>
            <Link to="/dashboard" className="continue-action-btn" style={{ marginTop: '16px' }}>
              Return to Dashboard
            </Link>
          </div>
        )}
      </main>
    </div>
  );
};
