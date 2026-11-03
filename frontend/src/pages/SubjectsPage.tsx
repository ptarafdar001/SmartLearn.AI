import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { fetchDashboardOverview, fetchEnrolledSubjects } from '../services/learning';
import type { DashboardOverview, SubjectSummary } from '../types/learning';

export const SubjectsPage: React.FC = () => {
  const [subjects, setSubjects] = useState<SubjectSummary[]>([]);
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<'all' | 'in_progress' | 'not_started' | 'completed'>('all');

  useEffect(() => {
    async function loadSubjects() {
      try {
        setLoading(true);
        const [data, ov] = await Promise.all([
          fetchEnrolledSubjects(),
          fetchDashboardOverview().catch(() => null),
        ]);
        setSubjects(data);
        setOverview(ov);
      } catch (err: any) {
        setError(err.message || 'Failed to load enrolled subjects.');
      } finally {
        setLoading(false);
      }
    }
    loadSubjects();
  }, []);

  const board = overview?.board || 'ISC';
  const grade = overview?.grade || 'Class 10';

  // Helper for pastel card theme and explore button color
  const getSubjectCardDetails = (index: number, name: string) => {
    const themes = [
      { themeCls: 'theme-yellow', barColor: '#eab308', btnCls: 'btn-orange', displayName: name, fallbackChapters: 4, fallbackTopics: 8, fallbackProgress: 0 },
      { themeCls: 'theme-mint', barColor: '#10b981', btnCls: 'btn-mint', displayName: name, fallbackChapters: 4, fallbackTopics: 8, fallbackProgress: 0 },
      { themeCls: 'theme-peach', barColor: '#f97316', btnCls: 'btn-coral', displayName: name, fallbackChapters: 4, fallbackTopics: 8, fallbackProgress: 0 },
      { themeCls: 'theme-purple', barColor: '#8b5cf6', btnCls: 'btn-purple', displayName: name, fallbackChapters: 4, fallbackTopics: 8, fallbackProgress: 0 },
    ];
    return themes[index % themes.length];
  };

  const filteredSubjects = subjects.filter((s, idx) => {
    const details = getSubjectCardDetails(idx, s.name);
    const pct = s.progress_percentage ?? details.fallbackProgress;
    if (activeFilter === 'in_progress') return pct > 0 && pct < 100;
    if (activeFilter === 'not_started') return pct === 0;
    if (activeFilter === 'completed') return pct === 100;
    return true;
  });

  return (
    <AppLayout breadcrumbs={[{ label: 'My Subjects' }]}>
      {/* Top Header Row matching Design */}
      <div className="subjects-top-header">
        <div>
          <h1 className="subjects-main-title">My Subjects</h1>
          <p className="subjects-main-sub">Pick a subject to see its chapters, notes, videos and quizzes.</p>
        </div>
        <span className="subjects-badge-count">{subjects.length} subjects</span>
      </div>

      {/* Filter Pills matching Design */}
      <div className="filter-pills-row-modern">
        <button
          type="button"
          className={`filter-btn-pill ${activeFilter === 'all' ? 'active' : ''}`}
          onClick={() => setActiveFilter('all')}
        >
          All
        </button>
        <button
          type="button"
          className={`filter-btn-pill ${activeFilter === 'in_progress' ? 'active' : ''}`}
          onClick={() => setActiveFilter('in_progress')}
        >
          In progress
        </button>
        <button
          type="button"
          className={`filter-btn-pill ${activeFilter === 'not_started' ? 'active' : ''}`}
          onClick={() => setActiveFilter('not_started')}
        >
          Not started
        </button>
        <button
          type="button"
          className={`filter-btn-pill ${activeFilter === 'completed' ? 'active' : ''}`}
          onClick={() => setActiveFilter('completed')}
        >
          Completed
        </button>
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
      ) : filteredSubjects.length === 0 ? (
        <div className="learn-empty-state">
          <BookOpen size={32} />
          <p>No subjects found for this filter.</p>
        </div>
      ) : (
        /* 2x2 Subjects Grid matching Design */
        <div className="subjects-grid-2col">
          {filteredSubjects.map((subj, idx) => {
            const details = getSubjectCardDetails(idx, subj.name);
            const pct = subj.progress_percentage ?? details.fallbackProgress;
            const chapters = subj.total_chapters || subj.chapter_count || details.fallbackChapters;
            const topics = subj.total_topics || subj.topic_count || details.fallbackTopics;

            return (
              <div key={subj.id} className={`subject-grid-card ${details.themeCls}`}>
                <div>
                  <div className="subject-card-topbar">
                    <h2 className="subject-title-large">{details.displayName}</h2>
                    <span className="subject-tag-pill">
                      {board} · {grade}
                    </span>
                  </div>

                  <p className="subject-card-desc">
                    {subj.description || `Official curriculum syllabus, chapter by chapter.`}
                  </p>

                  <div>
                    <div className="subject-progress-label-row">
                      <span>Syllabus completion</span>
                      <span>{pct}%</span>
                    </div>
                    <div className="subject-pastel-bar-track">
                      <div
                        className="subject-pastel-bar-fill"
                        style={{ width: `${pct}%`, background: details.barColor }}
                      />
                    </div>
                  </div>
                </div>

                <div className="subject-card-footer-row">
                  <span className="subject-counts-text">
                    {chapters} chapters · {topics} topics
                  </span>
                  <Link
                    to={`/learning/subjects/${subj.id}`}
                    className={`explore-pill-btn ${details.btnCls}`}
                  >
                    Explore
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
