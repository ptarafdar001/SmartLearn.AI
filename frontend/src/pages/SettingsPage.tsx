import React, { useEffect, useState } from 'react';
import { User, BookOpen, Edit3, ArrowRight, Clock, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { useAuth } from '../context/AuthContext';
import { fetchDashboardOverview } from '../services/learning';
import type { DashboardOverview } from '../types/learning';

export const SettingsPage: React.FC = () => {
  const { user, onboardingSelections, refreshOnboardingSelections } = useAuth();
  const [overview, setOverview] = useState<DashboardOverview | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      try {
        const [ovData] = await Promise.all([
          fetchDashboardOverview().catch(() => null),
          refreshOnboardingSelections().catch(() => null),
        ]);
        if (isMounted) {
          if (ovData) setOverview(ovData);
        }
      } catch {
        // Fallback gracefully
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, []);

  const board = onboardingSelections?.board || overview?.board || 'CBSE';
  const grade = onboardingSelections?.grade || overview?.grade || 'Class 10';
  const isSenior = grade === 'Class 11' || grade === 'Class 12';
  const stream = isSenior ? (onboardingSelections?.academic_stream || overview?.academic_stream || 'General') : null;
  const subjects: string[] = (onboardingSelections?.enrolled_subjects && onboardingSelections.enrolled_subjects.length > 0)
    ? onboardingSelections.enrolled_subjects
    : (overview?.enrolled_subjects || []);

  return (
    <AppLayout breadcrumbs={[{ label: 'Settings' }]}>
      <div className="page-header-compact">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h1 className="page-title-compact">Account &amp; Learning Preferences</h1>
            <p className="page-subtitle-compact">
              Manage your personal student details and update your live curriculum selections anytime.
            </p>
          </div>

          <Link
            to="/onboarding/step-1"
            className="action-btn-primary"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              background: '#4f46e5',
              color: '#ffffff',
              padding: '10px 18px',
              borderRadius: 10,
              fontWeight: 600,
              fontSize: 13.5,
              textDecoration: 'none',
              boxShadow: '0 2px 4px rgba(79, 70, 229, 0.2)',
            }}
          >
            <Edit3 size={16} />
            <span>Edit Learning Preferences &amp; Onboarding</span>
            <ArrowRight size={14} />
          </Link>
        </div>
      </div>

      <div className="settings-stack">
        {/* Quick Re-Personalization Callout Card */}
        <div style={{
          background: 'linear-gradient(135deg, #ede9fe 0%, #e0e7ff 100%)',
          border: '1px solid #c7d2fe',
          borderRadius: 16,
          padding: '20px 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 16,
        }}>
          <div>
            <div style={{ fontSize: 16, fontWeight: 700, color: '#3730a3', display: 'flex', alignItems: 'center', gap: 8 }}>
              <CheckCircle2 size={18} color="#4f46e5" />
              100% Dynamically Synchronized Curriculum
            </div>
            <p style={{ fontSize: 13, color: '#4338ca', margin: '6px 0 0', maxWidth: 650, lineHeight: 1.5 }}>
              Switching your class, board, second language, or enrolled subjects instantly updates your Dashboard,
              Study Materials, AI Tutor, and Video Recommendations across the entire website.
            </p>
          </div>
          <Link
            to="/onboarding/step-1"
            style={{
              background: '#ffffff',
              color: '#4338ca',
              border: '1px solid #a5b4fc',
              padding: '8px 16px',
              borderRadius: 8,
              fontWeight: 700,
              fontSize: 13,
              textDecoration: 'none',
              whiteSpace: 'nowrap',
            }}
          >
            Change Class / Board →
          </Link>
        </div>

        {/* Student Profile Card */}
        <div className="analytics-section-card">
          <div className="plan-card-header">
            <User size={18} className="text-indigo-600" />
            <h2 className="analytics-card-title">Student Profile</h2>
          </div>

          <div className="plan-details-list">
            <div className="plan-item-row">
              <span className="plan-item-label">Full Name</span>
              <span className="plan-item-val">{user?.full_name || 'Active Student'}</span>
            </div>
            <div className="plan-item-row">
              <span className="plan-item-label">Registered Email</span>
              <span className="plan-item-val">{user?.email || 'student@smartlearn.ai'}</span>
            </div>
            <div className="plan-item-row">
              <span className="plan-item-label">Role</span>
              <span className="plan-item-val capitalize">{user?.role || 'student'}</span>
            </div>
            <div className="plan-item-row">
              <span className="plan-item-label">Account Status</span>
              <span className="plan-item-val" style={{ color: '#059669', fontWeight: 600 }}>Active &amp; Fully Synchronized</span>
            </div>
          </div>
        </div>

        {/* Dynamic Curriculum & Board Configuration Card */}
        <div className="analytics-section-card">
          <div className="plan-card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <BookOpen size={18} className="text-indigo-600" />
              <h2 className="analytics-card-title">Curriculum &amp; Board Configuration</h2>
            </div>
            <Link
              to="/onboarding/step-2"
              style={{ fontSize: 13, color: '#4f46e5', fontWeight: 600, textDecoration: 'none' }}
            >
              Modify Subjects
            </Link>
          </div>

          <div className="plan-details-list">
            <div className="plan-item-row">
              <span className="plan-item-label">Examination Board</span>
              <span className="plan-item-val" style={{ fontWeight: 700, color: '#1e293b' }}>{board}</span>
            </div>
            <div className="plan-item-row">
              <span className="plan-item-label">Class / Grade</span>
              <span className="plan-item-val" style={{ fontWeight: 700, color: '#1e293b' }}>{grade}</span>
            </div>
            {stream && (
              <div className="plan-item-row">
                <span className="plan-item-label">Academic Stream</span>
                <span className="plan-item-val">{stream}</span>
              </div>
            )}
            <div className="plan-item-row" style={{ alignItems: 'flex-start' }}>
              <span className="plan-item-label">Enrolled Subjects</span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, justifyContent: 'flex-end', maxWidth: 420 }}>
                {subjects.length > 0 ? (
                  subjects.map((s: string, idx: number) => (
                    <span
                      key={idx}
                      style={{
                        background: '#e0e7ff',
                        color: '#3730a3',
                        fontSize: 12,
                        fontWeight: 600,
                        padding: '3px 10px',
                        borderRadius: 6,
                      }}
                    >
                      {s}
                    </span>
                  ))
                ) : (
                  <span className="plan-item-val">No subjects selected yet</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Study Routine & Target Schedule Card */}
        <div className="analytics-section-card">
          <div className="plan-card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Clock size={18} className="text-indigo-600" />
              <h2 className="analytics-card-title">Study Routine &amp; Schedule</h2>
            </div>
            <Link
              to="/onboarding/step-3"
              style={{ fontSize: 13, color: '#4f46e5', fontWeight: 600, textDecoration: 'none' }}
            >
              Edit Schedule
            </Link>
          </div>

          <div className="plan-details-list">
            <div className="plan-item-row">
              <span className="plan-item-label">Daily Target</span>
              <span className="plan-item-val">{overview?.study_target?.daily_target_hours || 2} Hours / Day</span>
            </div>
            <div className="plan-item-row">
              <span className="plan-item-label">Preferred Time Slot</span>
              <span className="plan-item-val capitalize">{overview?.study_target?.preferred_slot || 'Evening (6 PM - 9 PM)'}</span>
            </div>
            <div className="plan-item-row">
              <span className="plan-item-label">Active Study Days</span>
              <span className="plan-item-val">{overview?.study_target?.available_days?.join(', ') || 'Monday - Friday'}</span>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};
