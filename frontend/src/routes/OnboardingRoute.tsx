import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const OnboardingRoute: React.FC = () => {
  const { isAuthenticated, isLoading, user, isOnboarded } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="onboarding-page-container">
        <div
          className="btn-spinner"
          style={{
            borderColor: 'rgba(79, 70, 229, 0.3)',
            borderTopColor: '#4f46e5',
            width: 36,
            height: 36,
            marginTop: '20vh',
          }}
        />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If student is already fully onboarded, navigate them to dashboard
  if (isOnboarded || user?.is_onboarded) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
};
