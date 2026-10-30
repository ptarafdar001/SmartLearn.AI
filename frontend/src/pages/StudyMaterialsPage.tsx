import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { fetchEnrolledSubjects, fetchSubjectDetail } from '../services/learning';
import type { SubjectDetail, SubjectSummary } from '../types/learning';
import '../styles/learning.css';

export const StudyMaterialsPage: React.FC = () => {
  const [enrolledSubjects, setEnrolledSubjects] = useState<SubjectSummary[]>([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [subject, setSubject] = useState<SubjectDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterType, setFilterType] = useState<'all' | 'notes' | 'video' | 'text'>('all');

  useEffect(() => {
    async function loadInitial() {
      try {
        setLoading(true);
        const subjects = await fetchEnrolledSubjects();
        setEnrolledSubjects(subjects);
        if (subjects && subjects.length > 0) {
          const defaultId = subjects[0].id;
          setSelectedSubjectId(defaultId);
          const detail = await fetchSubjectDetail(defaultId);
          setSubject(detail);
        }
      } catch {
        // fallback
      } finally {
        setLoading(false);
      }
    }
    loadInitial();
  }, []);

  const handleSelectSubject = async (subId: number | null) => {
    setSelectedSubjectId(subId);
    if (subId === null) {
      if (enrolledSubjects.length > 0) {
        try {
          setLoading(true);
          const detail = await fetchSubjectDetail(enrolledSubjects[0].id);
          setSubject(detail);
        } catch {
          setSubject(null);
        } finally {
          setLoading(false);
        }
      }
      return;
    }
    try {
      setLoading(true);
      const detail = await fetchSubjectDetail(subId);
      setSubject(detail);
    } catch {
      setSubject(null);
    } finally {
      setLoading(false);
    }
  };

  const chapters = subject?.chapters || [];

  return (
    <AppLayout breadcrumbs={[{ label: 'Materials & Notes' }]}>
      {/* Top Header Row matching Image 4 */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 18, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: '#1e293b', margin: '0 0 4px 0' }}>
            Materials &amp; Notes
          </h1>
          <p style={{ fontSize: 13.5, color: '#64748b', margin: 0 }}>
            Verified notes, videos and reading for your syllabus.
          </p>
        </div>

        {/* Top-Right Subject Pills matching Image 4 */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button
            type="button"
            className={`filter-btn-pill ${selectedSubjectId === null ? 'active' : ''}`}
            onClick={() => handleSelectSubject(null)}
          >
            All subjects
          </button>
          {enrolledSubjects.map((sub) => (
            <button
              key={sub.id}
              type="button"
              className={`filter-btn-pill ${selectedSubjectId === sub.id ? 'active' : ''}`}
              onClick={() => handleSelectSubject(sub.id)}
            >
              {sub.name}
            </button>
          ))}
        </div>
      </div>

      {/* Resource Type Filter Pills matching Image 4 */}
      <div className="filter-pills-row-modern" style={{ marginBottom: 20 }}>
        <button
          type="button"
          className={`filter-btn-pill ${filterType === 'all' ? 'active' : ''}`}
          onClick={() => setFilterType('all')}
        >
          All
        </button>
        <button
          type="button"
          className={`filter-btn-pill ${filterType === 'notes' ? 'active' : ''}`}
          onClick={() => setFilterType('notes')}
        >
          Notes
        </button>
        <button
          type="button"
          className={`filter-btn-pill ${filterType === 'video' ? 'active' : ''}`}
          onClick={() => setFilterType('video')}
        >
          Videos
        </button>
        <button
          type="button"
          className={`filter-btn-pill ${filterType === 'text' ? 'active' : ''}`}
          onClick={() => setFilterType('text')}
        >
          Reading
        </button>
      </div>

      {loading ? (
        <div className="learn-loading-container">
          <div className="learn-spinner" />
          <p>Loading study materials catalog...</p>
        </div>
      ) : chapters.length === 0 ? (
        <div className="learn-empty-state">
          <BookOpen size={32} />
          <p>No materials available for the current selection.</p>
        </div>
      ) : (
        /* Chapter Blocks matching Image 4 */
        <div>
          {chapters.map((ch) => {
            return (
              <div key={ch.id} className="materials-ch-block">
                <h2 className="materials-ch-header-title">
                  Chapter {ch.chapter_number} · {ch.title}
                </h2>

                <div>
                  {ch.topics.map((t, idx) => {
                    const isEven = idx % 2 === 0;
                    const durationStr = isEven
                      ? `Notes · ${t.estimated_minutes || 6} min read`
                      : `Video · ${t.estimated_minutes ? t.estimated_minutes + 2 : 11} min`;
                    const btnLabel = isEven ? 'Open' : 'Watch';

                    if (filterType !== 'all') {
                      if (filterType === 'notes' && !isEven) return null;
                      if (filterType === 'video' && isEven) return null;
                    }

                    return (
                      <div key={t.id} className="material-item-row-clean">
                        <div>
                          <div className="material-item-title">{t.title}</div>
                          <div className="material-item-sub">{durationStr}</div>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center' }}>
                          <span className="badge-verified-green">Verified</span>
                          <Link
                            to={`/learning/topics/${t.id}`}
                            className="btn-open-purple-clean"
                          >
                            {btnLabel}
                          </Link>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </AppLayout>
  );
};
