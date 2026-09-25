import React from 'react';
import type { UserRole } from '../../types/auth';

interface RoleSelectorProps {
  selectedRole: UserRole;
  onSelectRole: (role: UserRole) => void;
  disabled?: boolean;
}

export const RoleSelector: React.FC<RoleSelectorProps> = ({
  selectedRole,
  onSelectRole,
  disabled = false,
}) => {
  const roles: { key: UserRole; label: string }[] = [
    { key: 'student', label: 'Student' },
    { key: 'teacher', label: 'Teacher' },
    { key: 'parent', label: 'Parent' },
  ];

  return (
    <div className="role-selector" role="tablist" aria-label="Account Role">
      {roles.map((r) => {
        const isActive = selectedRole === r.key;
        return (
          <button
            key={r.key}
            type="button"
            role="tab"
            aria-selected={isActive}
            className={`role-tab ${isActive ? 'active' : ''}`}
            onClick={() => onSelectRole(r.key)}
            disabled={disabled}
          >
            {r.label}
          </button>
        );
      })}
    </div>
  );
};
