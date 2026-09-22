import React, { useEffect, useState } from 'react';
import { TrendingUp, Clock, Target } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { fetchDashboardOverview } from '../services/learning';
import type { DashboardOverview } from '../types/learning';

export const ProgressAnalyticsPage: React.FC = () => {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fetchDashboardOverview();
        setOverview(data);
      } catch {
        // fallback
      }
    }
    loadData();
  }, []);

  const overall = overview?.overall_progress_percentage ?? 40;

  return (
    <AppLayout breadcrumbs={[{ label: 'Progress & Analytics' }]}>
      <div className="page-header-compact">
        <div>
          <h1 className="page-title-compact">Learning Progress &amp; Mastery Analytics</h1>
          <p className="page-subtitle-compact">
            Track syllabus completion, study time allocation, and performance metrics across CISCE Class 11 modules.
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
            <span className="analytics-val">1 of 3</span>
            <span className="analytics-label">Chapters In-Progress</span>
          </div>
        </div>
      </div>

      {/* Chapter Breakdown Card */}
      <div className="analytics-section-card">
        <h2 className="analytics-card-title">ISC History: Chapter-wise Syllabus Mastery</h2>
        <div className="analytics-breakdown-list">
          <div className="analytics-row">
            <div className="analytics-row-info">
              <span className="analytics-ch-name">Ch 1: Emergence of the Colonial Economy</span>
              <span className="analytics-ch-pct">50% completed</span>
            </div>
            <div className="progress-bar-bg">
              <div className="progress-bar-fill" style={{ width: '50%' }} />
            </div>
          </div>

          <div className="analytics-row">
            <div className="analytics-row-info">
              <span className="analytics-ch-name">Ch 2: Social and Cultural Awakening</span>
              <span className="analytics-ch-pct">0% (Scheduled)</span>
            </div>
            <div className="progress-bar-bg">
              <div className="progress-bar-fill" style={{ width: '0%' }} />
            </div>
          </div>

          <div className="analytics-row">
            <div className="analytics-row-info">
              <span className="analytics-ch-name">Ch 3: Early Nationalism &amp; Economic Drain Critique</span>
              <span className="analytics-ch-pct">0% (Scheduled)</span>
            </div>
            <div className="progress-bar-bg">
              <div className="progress-bar-fill" style={{ width: '0%' }} />
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};
