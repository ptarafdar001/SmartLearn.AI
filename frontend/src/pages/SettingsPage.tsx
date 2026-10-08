import React from 'react';
import { User, BookOpen } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { useAuth } from '../context/AuthContext';

export const SettingsPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <AppLayout breadcrumbs={[{ label: 'Settings' }]}>
      <div className="page-header-compact">
        <div>
          <h1 className="page-title-compact">Account &amp; Academic Settings</h1>
          <p className="page-subtitle-compact">
            Review your enrolled profile, verified curriculum settings, and authentication details.
          </p>
        </div>
      </div>

      <div className="settings-stack">
        {/* Student Profile */}
        <div className="analytics-section-card">
          <div className="plan-card-header">
            <User size={18} className="text-indigo-600" />
            <h2 className="analytics-card-title">Student Profile</h2>
          </div>

          <div className="plan-details-list">
            <div className="plan-item-row">
              <span className="plan-item-label">Full Name</span>
              <span className="plan-item-val">{user?.full_name || 'Demo Student'}</span>
            </div>
            <div className="plan-item-row">
              <span className="plan-item-label">Registered Email</span>
              <span className="plan-item-val">{user?.email || 'demo.student@smartlearn.ai'}</span>
            </div>
            <div className="plan-item-row">
              <span className="plan-item-label">Role</span>
              <span className="plan-item-val capitalize">{user?.role || 'student'}</span>
            </div>
            <div className="plan-item-row">
              <span className="plan-item-label">Account Status</span>
              <span className="plan-item-val" style={{ color: '#059669', fontWeight: 600 }}>Active &amp; Fully Onboarded</span>
            </div>
          </div>
        </div>

        {/* Academic Curriculum Settings */}
        <div className="analytics-section-card">
          <div className="plan-card-header">
            <BookOpen size={18} className="text-indigo-600" />
            <h2 className="analytics-card-title">Curriculum &amp; Board Configuration</h2>
          </div>

          <div className="plan-details-list">
            <div className="plan-item-row">
              <span className="plan-item-label">Examination Board</span>
              <span className="plan-item-val">CISCE (ISC)</span>
            </div>
            <div className="plan-item-row">
              <span className="plan-item-label">Class / Grade</span>
              <span className="plan-item-val">Class 11</span>
            </div>
            <div className="plan-item-row">
              <span className="plan-item-label">Academic Stream</span>
              <span className="plan-item-val">Humanities / Arts</span>
            </div>
            <div className="plan-item-row">
              <span className="plan-item-label">Enrolled Subject</span>
              <span className="plan-item-val">History (Code: isc-11-hist)</span>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};
