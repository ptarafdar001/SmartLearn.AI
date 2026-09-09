import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { BrandLogo } from '../common/BrandLogo';

export const OnboardingNavbar: React.FC = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <header className="onboarding-navbar" role="banner">
      <BrandLogo size="md" />
      <div className="onboarding-nav-right">
        <div className="onboarding-support-text">
          Need help?{' '}
          <a
            href="mailto:support@smartlearn.ai"
            className="support-link"
            onClick={(e) => {
              // Non-destructive fallback if mail client not installed
              if (!navigator.onLine) e.preventDefault();
            }}
          >
            Contact Support
          </a>
        </div>
        <div className="onboarding-nav-divider" aria-hidden="true" />
        <button
          type="button"
          className="onboarding-signout-btn"
          onClick={handleSignOut}
          aria-label="Sign Out"
        >
          Sign Out
        </button>
      </div>
    </header>
  );
};
