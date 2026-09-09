import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, isLoading, isOnboarded } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="auth-page-container">
        <div className="btn-spinner" style={{ borderColor: 'rgba(79, 70, 229, 0.3)', borderTopColor: '#4f46e5', width: 36, height: 36 }} />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If student onboarding is incomplete, redirect to onboarding wizard Step 1
  if (!isOnboarded) {
    return <Navigate to="/onboarding/step1" replace />;
  }

  return <Outlet />;
};
