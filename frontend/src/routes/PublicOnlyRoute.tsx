import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const PublicOnlyRoute: React.FC = () => {
  const { isAuthenticated, isLoading, isOnboarded, user } = useAuth();


  if (isLoading) {
    return (
      <div className="auth-page-container">
        <div className="btn-spinner" style={{ borderColor: 'rgba(79, 70, 229, 0.3)', borderTopColor: '#4f46e5', width: 36, height: 36 }} />
      </div>
    );
  }

  const isFullyOnboarded = isOnboarded || (user?.is_onboarded ?? false);

  if (isAuthenticated) {
    return <Navigate to={isFullyOnboarded ? '/dashboard' : '/onboarding/step1'} replace />;
  }


  return <Outlet />;
};
