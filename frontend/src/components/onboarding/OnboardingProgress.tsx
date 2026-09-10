import React from 'react';

interface OnboardingProgressProps {
  step: number;
  totalSteps?: number;
  stepTitle: string;
  percentage?: number;
}

export const OnboardingProgress: React.FC<OnboardingProgressProps> = ({
  step,
  totalSteps = 4,
  stepTitle,
  percentage = 25,
}) => {
  return (
    <div className="onboarding-progress-container" aria-label={`Step ${step} of ${totalSteps} progress`}>
      <div className="onboarding-progress-header">
        <span className="onboarding-step-label">
          STEP {step} OF {totalSteps}: {stepTitle.toUpperCase()}
        </span>
        <span className="onboarding-percentage-label">{percentage}% Set Up</span>
      </div>
      <div className="onboarding-progress-track" role="progressbar" aria-valuenow={percentage} aria-valuemin={0} aria-valuemax={100}>
        <div
          className="onboarding-progress-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
