import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/common/Button';
import { BrandLogo } from '../components/common/BrandLogo';
import '../styles/auth.css';

export const DashboardPlaceholder: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div className="auth-page-container">
      <div className="auth-card dashboard-placeholder" role="main">
        <BrandLogo size="md" />

        <h1 className="auth-title">Student Dashboard</h1>
        <p className="auth-subtitle">
          Authentication verified successfully. Phase 6A completed!
        </p>

        <div className="dashboard-user-card">
          <div className="user-field">
            <span className="user-field-label">Full Name:</span>
            <span className="user-field-val">{user?.full_name || 'Student'}</span>
          </div>
          <div className="user-field">
            <span className="user-field-label">Email:</span>
            <span className="user-field-val">{user?.email || 'N/A'}</span>
          </div>
          <div className="user-field">
            <span className="user-field-label">Role:</span>
            <span className="user-field-val">{user?.role || 'student'}</span>
          </div>
          <div className="user-field">
            <span className="user-field-label">Onboarding Status:</span>
            <span className="user-field-val">
              {user?.is_onboarded ? 'Completed' : 'Pending Onboarding (Phase 6B)'}
            </span>
          </div>
        </div>

        <Button variant="primary" onClick={logout}>
          Sign Out
        </Button>
      </div>
    </div>
  );
};
