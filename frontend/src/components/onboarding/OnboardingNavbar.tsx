import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { onboardingService } from '../../services/onboarding';
import { BrandLogo } from '../common/BrandLogo';

export const OnboardingNavbar: React.FC = () => {
  const { logout, refreshUser } = useAuth();
  const navigate = useNavigate();
  const [isSkipping, setIsSkipping] = useState(false);

  const handleSignOut = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const handleSkip = async () => {
    try {
      setIsSkipping(true);
      await onboardingService.skipOnboarding();
      await refreshUser();
      navigate('/dashboard', { replace: true });
    } catch {
      // Fallback navigate to dashboard
      navigate('/dashboard', { replace: true });
    } finally {
      setIsSkipping(false);
    }
  };

  return (
    <header className="onboarding-navbar" role="banner">
      <BrandLogo size="md" />
      <div className="onboarding-nav-right">
        <button
          type="button"
          className="skip-onboarding-btn"
          onClick={handleSkip}
          disabled={isSkipping}
          style={{
            background: 'none',
            border: 'none',
            color: '#6366f1',
            fontWeight: 600,
            fontSize: '14px',
            cursor: 'pointer',
            padding: '6px 12px',
            borderRadius: '6px',
            marginRight: '8px',
          }}
        >
          {isSkipping ? 'Skipping...' : 'Skip for now →'}
        </button>

        <div className="onboarding-support-text">
          Need help?{' '}
          <a
            href="mailto:support@smartlearn.ai"
            className="support-link"
            onClick={(e) => {
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
