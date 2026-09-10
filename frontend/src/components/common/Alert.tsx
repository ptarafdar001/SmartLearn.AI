import React from 'react';

interface AlertProps {
  type?: 'error' | 'info' | 'success';
  message: string;
  onClose?: () => void;
}

export const Alert: React.FC<AlertProps> = ({
  type = 'error',
  message,
  onClose,
}) => {
  if (!message) return null;

  return (
    <div className={`alert alert-${type}`} role="alert">
      <div className="alert-content">
        {type === 'error' && (
          <svg
            viewBox="0 0 20 20"
            fill="currentColor"
            className="alert-icon"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        )}
        {type === 'info' && (
          <svg
            viewBox="0 0 20 20"
            fill="currentColor"
            className="alert-icon"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clipRule="evenodd"
            />
          </svg>
        )}
        <span className="alert-message">{message}</span>
      </div>
      {onClose && (
        <button
          type="button"
          className="alert-close-btn"
          onClick={onClose}
          aria-label="Close notification"
        >
          &times;
        </button>
      )}
    </div>
  );
};
