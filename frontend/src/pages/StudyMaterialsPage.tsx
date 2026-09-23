import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Video, ArrowRight, Check } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { fetchEnrolledSubjects, fetchSubjectDetail } from '../services/learning';
import type { SubjectDetail, SubjectSummary } from '../types/learning';
import { CurriculumStatusCard } from '../components/learning/CurriculumStatusCard';
import { CurriculumReadinessBadge } from '../components/learning/CurriculumReadinessBadge';

export const StudyMaterialsPage: React.FC = () => {
  const [enrolledSubjects, setEnrolledSubjects] = useState<SubjectSummary[]>([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [subject, setSubject] = useState<SubjectDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterType, setFilterType] = useState<string>('all');

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

  const handleSelectSubject = async (subId: number) => {
    if (subId === selectedSubjectId) return;
    try {
      setLoading(true);
      setSelectedSubjectId(subId);
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
    <AppLayout breadcrumbs={[{ label: 'Study Materials & Notes' }]}>
      <div className="page-header-compact">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="page-title-compact">Study Materials &amp; Verified Notes</h1>
            {subject?.curriculum_status && (
              <CurriculumReadinessBadge status={subject.curriculum_status} size="sm" />
            )}
          </div>
          <p className="page-subtitle-compact">
            Curated revision sheets, textbook extracts, and video lectures aligned with {subject?.board || 'official'} {subject?.grade ? `Class ${subject.grade}` : 'curriculum'} standards.
          </p>
        </div>

        {enrolledSubjects.length > 1 && (
          <div className="filter-pills-row" style={{ marginTop: '12px' }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: '#64748b', alignSelf: 'center', marginRight: '6px' }}>
              Subject:
            </span>
            {enrolledSubjects.map((sub) => (
              <button
                key={sub.id}
                type="button"
                className={`filter-pill ${selectedSubjectId === sub.id ? 'active' : ''}`}
                onClick={() => handleSelectSubject(sub.id)}
              >
                {sub.name}
              </button>
            ))}
          </div>
        )}

        <div className="filter-pills-row" style={{ marginTop: enrolledSubjects.length > 1 ? '10px' : '0' }}>
          <button
            type="button"
            className={`filter-pill ${filterType === 'all' ? 'active' : ''}`}
            onClick={() => setFilterType('all')}
          >
            All Resources
          </button>
          <button
            type="button"
            className={`filter-pill ${filterType === 'notes' ? 'active' : ''}`}
            onClick={() => setFilterType('notes')}
          >
            <FileText size={13} />
            <span>Revision Notes</span>
          </button>
          <button
            type="button"
            className={`filter-pill ${filterType === 'video' ? 'active' : ''}`}
            onClick={() => setFilterType('video')}
          >
            <Video size={13} />
            <span>Video Lectures</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="learn-loading-container">
          <div className="learn-spinner" />
          <p>Loading study materials catalog...</p>
        </div>
      ) : chapters.length === 0 ? (
        <div className="py-8">
          <CurriculumStatusCard
            subjectName={subject?.name || 'Selected Subject'}
            board={subject?.board}
            grade={subject?.grade}
            curriculumStatus={subject?.curriculum_status || 'in_preparation'}
            sourceAuthority={subject?.source_authority}
            syllabusVersion={subject?.syllabus_version}
            sourceUrl={subject?.source_url}
            statusMessage={subject?.status_message}
            backUrl="/subjects"
            backLabel="Browse Other Subjects"
          />
        </div>
      ) : (
        <div className="materials-grid">
          {chapters.map((ch) => (
            <div key={ch.id} className="materials-chapter-card">
              <div className="materials-ch-header">
                <span className="chapter-num-badge">Chapter {ch.chapter_number}</span>
                <h3 className="materials-ch-title">{ch.title}</h3>
              </div>

              <div className="materials-topics-list">
                {ch.topics.map((t) => (
                  <div key={t.id} className="materials-topic-row">
                    <div className="materials-topic-info">
                      <div className="materials-badge-verified">
                        <Check size={11} />
                        <span>Official {subject?.board || 'Curriculum'} Syllabus</span>
                      </div>
                      <h4 className="materials-topic-name">{t.topic_number}. {t.title}</h4>
                      <p className="materials-topic-desc">{t.description}</p>
                    </div>

                    <div className="materials-actions">
                      <Link to={`/learning/topics/${t.id}`} className="materials-view-btn">
                        <span>Study Notes &amp; Video</span>
                        <ArrowRight size={13} />
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </AppLayout>
  );
};

