import React from 'react';

interface CheckboxProps {
  id: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  children: React.ReactNode;
  disabled?: boolean;
  error?: string;
}

export const Checkbox: React.FC<CheckboxProps> = ({
  id,
  checked,
  onChange,
  children,
  disabled = false,
  error,
}) => {
  return (
    <div className={`checkbox-container ${error ? 'has-error' : ''}`}>
      <label htmlFor={id} className="checkbox-label">
        <input
          id={id}
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          disabled={disabled}
          className="checkbox-input"
          aria-invalid={!!error}
        />
        <span className={`custom-checkbox ${checked ? 'checked' : ''}`} aria-hidden="true">
          {checked && (
            <svg
              viewBox="0 0 16 16"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="check-icon"
            >
              <polyline points="3.5 8.5 6.5 11.5 12.5 5" />
            </svg>
          )}
        </span>
        <span className="checkbox-text">{children}</span>
      </label>
      {error && (
        <span className="form-error checkbox-error" role="alert">
          {error}
        </span>
      )}
    </div>
  );
};
