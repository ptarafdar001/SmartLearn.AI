import React, { useEffect, useState } from 'react';
import { TrendingUp, Clock, Target, BookOpen } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { fetchDashboardOverview, fetchEnrolledSubjects, fetchSubjectDetail } from '../services/learning';
import type { DashboardOverview, SubjectDetail, SubjectSummary } from '../types/learning';

export const ProgressAnalyticsPage: React.FC = () => {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [subject, setSubject] = useState<SubjectDetail | null>(null);
  const [enrolledSubjects, setEnrolledSubjects] = useState<SubjectSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [overviewData, subjectsData] = await Promise.all([
          fetchDashboardOverview().catch(() => null),
          fetchEnrolledSubjects().catch(() => []),
        ]);
        setOverview(overviewData);
        setEnrolledSubjects(subjectsData);

        if (subjectsData.length > 0) {
          const defaultSubId = subjectsData[0].id;
          const detail = await fetchSubjectDetail(defaultSubId).catch(() => null);
          setSubject(detail);
        }
      } catch {
        // fallback
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleSelectSubject = async (subId: number) => {
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

  const overall = overview?.overall_progress_percentage ?? 0;
  const chapters = subject?.chapters || [];
  const inProgressCount = chapters.filter(
    (ch) => ch.progress_percentage > 0 && ch.progress_percentage < 100
  ).length;
  const completedCount = chapters.filter((ch) => ch.progress_percentage === 100).length;

  return (
    <AppLayout breadcrumbs={[{ label: 'Progress & Analytics' }]}>
      <div className="page-header-compact">
        <div>
          <h1 className="page-title-compact">Learning Progress &amp; Mastery Analytics</h1>
          <p className="page-subtitle-compact">
            Track syllabus completion, study time allocation, and performance metrics across verified curriculum modules.
          </p>
        </div>
      </div>

      {/* Top 3 Metric Cards */}
      <div className="analytics-metrics-grid">
        <div className="analytics-stat-card">
          <div className="stat-icon-wrap stat-icon-primary">
            <TrendingUp size={20} />
          </div>
          <div>
            <span className="analytics-val">{overall}%</span>
            <span className="analytics-label">Syllabus Completion</span>
          </div>
        </div>

        <div className="analytics-stat-card">
          <div className="stat-icon-wrap stat-icon-success">
            <Clock size={20} />
          </div>
          <div>
            <span className="analytics-val">
              {overview?.study_target ? `${overview.study_target.daily_target_hours} hrs` : '2.0 hrs'}
            </span>
            <span className="analytics-label">Daily Study Target</span>
          </div>
        </div>

        <div className="analytics-stat-card">
          <div className="stat-icon-wrap stat-icon-info">
            <Target size={20} />
          </div>
          <div>
            <span className="analytics-val">
              {chapters.length > 0 ? `${inProgressCount || completedCount} of ${chapters.length}` : '0 of 0'}
            </span>
            <span className="analytics-label">Chapters Active / Done</span>
          </div>
        </div>
      </div>

      {/* Chapter Breakdown Card */}
      <div className="analytics-section-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
          <h2 className="analytics-card-title" style={{ margin: 0 }}>
            {subject ? `${subject.name} (${subject.board} ${subject.grade}): Chapter-wise Mastery` : 'Chapter-wise Syllabus Mastery'}
          </h2>

          {enrolledSubjects.length > 1 && (
            <div className="filter-pills-row" style={{ margin: 0 }}>
              {enrolledSubjects.map((sub) => (
                <button
                  key={sub.id}
                  type="button"
                  className={`filter-pill ${subject?.id === sub.id ? 'active' : ''}`}
                  onClick={() => handleSelectSubject(sub.id)}
                >
                  {sub.name}
                </button>
              ))}
            </div>
          )}
        </div>

        {loading ? (
          <div className="p-6 text-center text-slate-500 text-xs">Loading authentic chapter analytics...</div>
        ) : chapters.length === 0 ? (
          <div className="p-6 text-center text-slate-500 text-xs bg-slate-50 rounded-lg">
            <BookOpen size={24} className="mx-auto mb-2 text-slate-400" />
            <p className="font-medium text-slate-700">No verified chapters found for this subject yet.</p>
          </div>
        ) : (
          <div className="analytics-breakdown-list">
            {chapters.map((ch) => {
              const pct = ch.progress_percentage || 0;
              return (
                <div key={ch.id} className="analytics-row">
                  <div className="analytics-row-info">
                    <span className="analytics-ch-name">
                      Ch {ch.chapter_number}: {ch.title}
                    </span>
                    <span className="analytics-ch-pct">
                      {pct > 0 ? `${pct}% completed` : '0% (Not Started)'}
                    </span>
                  </div>
                  <div className="progress-bar-bg" role="progressbar" aria-valuenow={pct}>
                    <div className="progress-bar-fill" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </AppLayout>
  );
};
