import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  ChevronDown,
  ChevronUp,
  BookOpen,
  Clock,
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
} from 'lucide-react';
import { fetchSubjectDetail } from '../../services/learning';
import type { SubjectDetail } from '../../types/learning';
import '../../styles/learning.css';
import { AppLayout } from '../../components/layout/AppLayout';

export const SubjectDetailPage: React.FC = () => {
  const { subjectId } = useParams<{ subjectId: string }>();

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

  return (
    <AppLayout breadcrumbs={[{ label: 'My Subjects', href: '/subjects' }, { label: subject?.name || 'Subject' }]}>
      <div className="compact-page-wrapper">

        {error && (
          <div className="learn-error-box" role="alert">
            <AlertCircle size={18} className="text-amber-600" />
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
            {/* Subject Hero Header */}
            <div className="subject-hero">
              <div className="subject-hero-info">
                <div className="subject-badges-row">
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

              <div className="subject-hero-progress-box">
                <div className="progress-header">
                  <span>Syllabus Completion</span>
                  <span className="progress-pct-val">{subject.progress_percentage}%</span>
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

                <div className="subject-progress-topics-count">
                  <CheckCircle2 size={13} className="text-indigo-600" />
                  <span>{subject.completed_topics} of {subject.total_topics} topics completed</span>
                </div>
              </div>
            </div>

            {/* Chapters Accordion */}
            <section aria-labelledby="syllabus-title">
              <div className="learn-section-header">
                <h2 id="syllabus-title" className="learn-section-title">
                  <BookOpen size={18} className="section-title-icon" />
                  <span>Chapters &amp; Topics</span>
                </h2>
              </div>

              {subject.chapters.length === 0 ? (
                <div className="learn-empty-state" style={{ padding: '40px 20px', textAlign: 'center', background: '#f8fafc', borderRadius: '12px', border: '1px dashed #cbd5e1' }}>
                  <BookOpen size={36} className="empty-state-icon" style={{ margin: '0 auto 12px', color: '#6366f1' }} />
                  <h3 style={{ fontSize: '17px', fontWeight: 600, color: '#1e293b', marginBottom: '8px' }}>
                    Curriculum In Preparation
                  </h3>
                  <p style={{ maxWidth: 520, margin: '0 auto 16px', color: '#64748b', fontSize: '13.5px', lineHeight: 1.6 }}>
                    Verified syllabus chapters, learning objectives, and authentic previous-year questions for <strong>{subject.name} ({subject.board} {subject.grade})</strong> are currently in editorial curation. Currently, <strong>ISC Class 11 History</strong> is fully seeded with complete verified curriculum intelligence.
                  </p>
                  <Link to="/learning/subjects/43" className="continue-action-btn" style={{ display: 'inline-flex', padding: '8px 16px', fontSize: '13px' }}>
                    <span>Explore Seeded ISC History Syllabus →</span>
                  </Link>
                </div>
              ) : (
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
                                <p className="chapter-desc-text">
                                  {chapter.description}
                                </p>
                              )}
                            </div>
                          </div>

                          <div className="chapter-progress-pill">
                            <span>
                              {chapter.completed_topics}/{chapter.total_topics} Topics
                            </span>
                            <span className="chapter-pct-pill">{chapter.progress_percentage}%</span>
                            <span aria-hidden="true" className="chapter-chevron-icon">
                              {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
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
                                        <span className="topic-meta-time">
                                          <Clock size={12} />
                                          <span>Est. {topic.estimated_minutes} mins</span>
                                        </span>
                                        {topic.progress?.progress_percentage !== undefined && (
                                          <span> • {topic.progress.progress_percentage}% completed</span>
                                        )}
                                      </div>
                                    </div>
                                  </div>

                                  <span className="topic-action-link">
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
              )}
            </section>
          </>
        ) : (
          <div className="learn-empty-state">
            <BookOpen size={32} className="empty-state-icon" />
            <p>Subject not found.</p>
            <Link to="/dashboard" className="continue-action-btn" style={{ marginTop: '16px' }}>
              <ArrowLeft size={14} />
              <span>Return to Dashboard</span>
            </Link>
          </div>
        )}
      </div>
    </AppLayout>
  );
};
