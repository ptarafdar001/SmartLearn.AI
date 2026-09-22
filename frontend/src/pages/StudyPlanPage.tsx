import React, { useEffect, useState } from 'react';
import { Clock, Target } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { fetchDashboardOverview } from '../services/learning';
import type { DashboardOverview } from '../types/learning';

export const StudyPlanPage: React.FC = () => {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);

  useEffect(() => {
    fetchDashboardOverview().then(setOverview).catch(() => {});
  }, []);

  const target = overview?.study_target;

  return (
    <AppLayout breadcrumbs={[{ label: 'Study Plan' }]}>
      <div className="page-header-compact">
        <div>
          <h1 className="page-title-compact">Personalized Study Schedule &amp; Goals</h1>
          <p className="page-subtitle-compact">
            Your customized study timetable configured during onboarding to optimize Board examination preparation.
          </p>
        </div>
      </div>

      <div className="study-plan-grid">
        {/* Schedule Summary Card */}
        <div className="analytics-section-card">
          <div className="plan-card-header">
            <Clock size={18} className="text-indigo-600" />
            <h2 className="analytics-card-title">Daily Study Commitment</h2>
          </div>

          <div className="plan-details-list">
            <div className="plan-item-row">
              <span className="plan-item-label">Target Study Time</span>
              <span className="plan-item-val">{target?.daily_target_hours || 2.0} Hours / Day</span>
            </div>

            <div className="plan-item-row">
              <span className="plan-item-label">Preferred Study Slot</span>
              <span className="plan-item-val capitalize">{target?.preferred_slot || 'Evening'} Slot</span>
            </div>

            <div className="plan-item-row">
              <span className="plan-item-label">Weekly Active Days</span>
              <span className="plan-item-val">
                {target?.available_days ? `${target.available_days.length} Days / Week` : '6 Days / Week'}
              </span>
            </div>

            <div className="plan-item-row">
              <span className="plan-item-label">Calculated Weekly Commitment</span>
              <span className="plan-item-val" style={{ color: '#4f46e5', fontWeight: 700 }}>
                {target ? (target.daily_target_hours * (target.available_days?.length || 6)).toFixed(1) : '12.0'} Hours / Week
              </span>
            </div>
          </div>
        </div>

        {/* Academic Goals Card */}
        <div className="analytics-section-card">
          <div className="plan-card-header">
            <Target size={18} className="text-indigo-600" />
            <h2 className="analytics-card-title">Target Board Examination Goals</h2>
          </div>

          <div className="plan-details-list">
            <div className="plan-item-row">
              <span className="plan-item-label">Academic Board</span>
              <span className="plan-item-val">Council for the Indian School Certificate Examinations (CISCE)</span>
            </div>

            <div className="plan-item-row">
              <span className="plan-item-label">Curriculum Level</span>
              <span className="plan-item-val">ISC Class 11 (Humanities / Arts)</span>
            </div>

            <div className="plan-item-row">
              <span className="plan-item-label">Primary Academic Goal</span>
              <span className="plan-item-val">Excel in Board Exams (Target: 95%)</span>
            </div>

            <div className="plan-item-row">
              <span className="plan-item-label">Pedagogical Learning Style</span>
              <span className="plan-item-val">Visual &amp; Conceptual Understanding</span>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};
