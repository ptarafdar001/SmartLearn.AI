import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, ArrowRight } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { fetchEnrolledSubjects } from '../services/learning';
import type { SubjectSummary } from '../types/learning';
import { CurriculumReadinessBadge } from '../components/learning/CurriculumReadinessBadge';

export const SubjectsPage: React.FC = () => {
  const [subjects, setSubjects] = useState<SubjectSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadSubjects() {
      try {
        setLoading(true);
        const data = await fetchEnrolledSubjects();
        setSubjects(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load enrolled subjects.');
      } finally {
        setLoading(false);
      }
    }
    loadSubjects();
  }, []);

  return (
    <AppLayout breadcrumbs={[{ label: 'My Subjects' }]}>
      <div className="page-header-compact">
        <div>
          <h1 className="page-title-compact">My Enrolled Subjects</h1>
          <p className="page-subtitle-compact">
            Official syllabus-aligned curriculum subjects. Select a subject to explore chapters, topics, and verified notes.
          </p>
        </div>
        <span className="page-count-badge">{subjects.length} Subjects Enrolled</span>
      </div>

      {error && (
        <div className="learn-error-box" role="alert">
          <div>{error}</div>
        </div>
      )}

      {loading ? (
        <div className="learn-loading-container">
          <div className="learn-spinner" />
          <p>Loading your curriculum subjects...</p>
        </div>
      ) : subjects.length === 0 ? (
        <div className="learn-empty-state">
          <BookOpen size={32} />
          <p>No enrolled subjects found. Please complete subject onboarding.</p>
        </div>
      ) : (
        <div className="subjects-grid">
          {subjects.map((subj) => {
            const pct = subj.progress_percentage ?? 0;
            return (
              <div key={subj.id} className="subject-card">
                <div className="subject-card-body">
                  <div className="subject-card-header flex items-start justify-between gap-2 flex-wrap">
                    <div>
                      <h3 className="subject-name">{subj.name}</h3>
                      <span className="subject-badge">{subj.board} • {subj.grade}</span>
                    </div>
                    {subj.curriculum_status && (
                      <CurriculumReadinessBadge status={subj.curriculum_status} size="sm" />
                    )}
                  </div>

                  <p className="subject-desc">
                    {subj.description || `Official ${subj.board} ${subj.grade} curriculum for ${subj.name}.`}
                  </p>

                  <div className="progress-container">
                    <div className="progress-header">
                      <span>Syllabus Completion</span>
                      <span className="progress-pct-val">{pct}%</span>
                    </div>
                    <div className="progress-bar-bg" role="progressbar" aria-valuenow={pct}>
                      <div className="progress-bar-fill" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                </div>

                <div className="subject-card-footer">
                  <span className="subject-counts">
                    {subj.total_chapters || subj.chapter_count || 0} Chapters •{' '}
                    {subj.total_topics || subj.topic_count || 0} Topics
                  </span>
                  <Link to={`/learning/subjects/${subj.id}`} className="continue-action-btn" style={{ padding: '6px 12px', fontSize: '12.5px' }}>
                    <span>Explore Syllabus</span>
                    <ArrowRight size={13} />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </AppLayout>
  );
};
