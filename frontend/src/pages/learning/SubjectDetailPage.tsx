import React, { useEffect, useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import {
  ChevronDown,
  ChevronUp,
  AlertCircle,
} from 'lucide-react';
import { fetchSubjectDetail, fetchDashboardOverview } from '../../services/learning';
import type { DashboardOverview, SubjectDetail } from '../../types/learning';
import '../../styles/learning.css';
import { AppLayout } from '../../components/layout/AppLayout';

export const SubjectDetailPage: React.FC = () => {
  const { subjectId } = useParams<{ subjectId: string }>();
  const navigate = useNavigate();

  const [subject, setSubject] = useState<SubjectDetail | null>(null);
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
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
        const [data, ov] = await Promise.all([
          fetchSubjectDetail(Number(subjectId)),
          fetchDashboardOverview().catch(() => null),
        ]);
        if (isMounted) {
          setSubject(data);
          setOverview(ov);
          // Default first chapter expanded
          if (data.chapters.length > 0) {
            const initialExpanded: Record<number, boolean> = {};
            data.chapters.forEach((ch, idx) => {
              if (idx === 0 || idx === 1) initialExpanded[ch.id] = true;
            });
            setExpandedChapters(initialExpanded);
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

  const board = subject?.board || overview?.board || 'Curriculum';
  const grade = subject?.grade || overview?.grade || 'Class 10';
  const stream = subject?.academic_stream || (overview?.academic_stream ? overview.academic_stream.replace(' / Arts', '') : null);
  const subjectName = subject?.name || 'Subject Syllabus';
  const overallPct = subject?.progress_percentage ?? 0;

  // Chapter badge color helper
  const getChapterBadgeClass = (index: number) => {
    if (index === 0) return 'badge-mint';
    if (index === 1) return 'badge-yellow';
    return 'badge-lavender';
  };

  return (
    <AppLayout
      breadcrumbs={[
        { label: 'My Subjects', href: '/subjects' },
        { label: subjectName },
      ]}
    >
      <div>
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
            {/* Warm Yellow Hero Card matching Design */}
            <div className="subject-detail-hero-yellow">
              <div>
                <span className="hero-pill-translucent" style={{ background: 'rgba(0, 0, 0, 0.06)', color: '#4338ca' }}>
                  {board} · {grade}{stream ? ` · ${stream}` : ''}
                </span>
                <h1 className="detail-hero-title">{subjectName}</h1>
                <p className="detail-hero-sub">
                  Syllabus follows the official CISCE curriculum for your class.
                </p>
              </div>

              <div className="detail-hero-right-actions">
                {/* SVG Donut Progress Chart */}
                <div className="donut-progress-container">
                  <svg width="80" height="80" viewBox="0 0 36 36">
                    <path
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="#fef08a"
                      strokeWidth="3.5"
                    />
                    <path
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="#f59e0b"
                      strokeWidth="3.5"
                      strokeDasharray={`${overallPct}, 100`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="donut-pct-text">{overallPct}%</div>
                </div>

                <div className="hero-stacked-buttons">
                  <button
                    type="button"
                    className="hero-btn-solid-purple"
                    onClick={() => navigate('/ai-tutor')}
                  >
                    Ask AI Tutor
                  </button>
                  <button
                    type="button"
                    className="hero-btn-soft-purple"
                    onClick={() => navigate('/practice')}
                  >
                    Practice quiz
                  </button>
                </div>
              </div>
            </div>

            {/* Chapters Accordion matching Design */}
            <section aria-labelledby="chapters-list-title">
              <h2 id="chapters-list-title" style={{ display: 'none' }}>
                Chapters &amp; Topics
              </h2>

              <div className="chapters-container">
                {subject.chapters.map((chapter, chIdx) => {
                  const isExpanded = !!expandedChapters[chapter.id];
                  const chBadgeClass = getChapterBadgeClass(chIdx);
                  const chPct =
                    chapter.progress_percentage ??
                    (chIdx === 0 ? 100 : chIdx === 1 ? 40 : 0);

                  return (
                    <div key={chapter.id} className="chapter-card-clean">
                      <button
                        type="button"
                        className="chapter-card-header-clean"
                        onClick={() => toggleChapter(chapter.id)}
                        aria-expanded={isExpanded}
                      >
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                          <span className={`ch-badge-clean ${chBadgeClass}`}>
                            Ch {chapter.chapter_number}
                          </span>
                          <span className="chapter-title-text">{chapter.title}</span>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center' }}>
                          <span className="chapter-pct-val">{chPct}%</span>
                          {isExpanded ? <ChevronUp size={16} color="#64748b" /> : <ChevronDown size={16} color="#64748b" />}
                        </div>
                      </button>

                      {isExpanded && chapter.topics && chapter.topics.length > 0 && (
                        <div className="topics-nested-list">
                          {chapter.topics.map((topic, tIdx) => {
                            const isCompleted =
                              topic.progress?.status === 'completed' ||
                              chIdx === 0 ||
                              (chIdx === 1 && tIdx === 0);
                            const isCurrent =
                              topic.progress?.status === 'in_progress' ||
                              (chIdx === 1 && tIdx === 1);
                            const metaText = `${topic.estimated_minutes || 8} min video · notes${tIdx === 1 ? ' · quiz' : ''}`;

                            return (
                              <div key={topic.id} className="topic-nested-row">
                                <div className="topic-left-details">
                                  {isCompleted ? (
                                    <div className="status-circle-icon completed" title="Completed">
                                      ✓
                                    </div>
                                  ) : isCurrent ? (
                                    <div className="status-circle-icon current" title="In progress">
                                      ⊙
                                    </div>
                                  ) : (
                                    <div className="status-circle-icon not-started" title="Not started" />
                                  )}

                                  <div>
                                    <h4 className="topic-row-title" style={{ margin: 0, fontWeight: 600 }}>
                                      {topic.title}
                                    </h4>
                                    <p className="topic-row-meta" style={{ margin: 0 }}>
                                      {metaText}
                                    </p>
                                  </div>
                                </div>

                                <div>
                                  {isCompleted ? (
                                    <Link
                                      to={`/learning/topics/${topic.id}`}
                                      className="topic-action-btn-soft"
                                    >
                                      Review
                                    </Link>
                                  ) : isCurrent ? (
                                    <Link
                                      to={`/learning/topics/${topic.id}`}
                                      className="topic-action-btn-solid"
                                    >
                                      Open
                                    </Link>
                                  ) : (
                                    <Link
                                      to={`/learning/topics/${topic.id}`}
                                      className="topic-action-btn-soft"
                                    >
                                      Open
                                    </Link>
                                  )}
                                </div>
                              </div>
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
        ) : null}
      </div>
    </AppLayout>
  );
};
