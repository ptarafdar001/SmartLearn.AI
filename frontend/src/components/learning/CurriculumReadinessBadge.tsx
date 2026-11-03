import React from 'react';
import { ShieldCheck, BookOpen, Clock, AlertCircle } from 'lucide-react';
import type { CurriculumReadinessStatus } from '../../types/learning';

interface Props {
  status?: CurriculumReadinessStatus | string | null;
  className?: string;
  size?: 'sm' | 'md';
}

export const CurriculumReadinessBadge: React.FC<Props> = ({
  status,
  className = '',
  size = 'md',
}) => {
  const normalized = status?.toLowerCase() || 'in_preparation';

  let label = 'In Preparation';
  let Icon = Clock;
  let badgeStyle = {
    background: 'rgba(245,158,11,0.10)',
    color: '#f59e0b',
    borderColor: 'rgba(245,158,11,0.25)',
  };

  if (normalized === 'content_available') {
    label = 'Content Available';
    Icon = BookOpen;
    badgeStyle = {
      background: 'rgba(16,185,129,0.10)',
      color: '#10b981',
      borderColor: 'rgba(16,185,129,0.25)',
    };
  } else if (normalized === 'curriculum_verified') {
    label = 'Curriculum Verified';
    Icon = ShieldCheck;
    badgeStyle = {
      background: 'rgba(99,102,241,0.10)',
      color: '#6366f1',
      borderColor: 'rgba(99,102,241,0.25)',
    };
  } else if (normalized === 'no_selection') {
    label = 'No Selection';
    Icon = AlertCircle;
    badgeStyle = {
      background: 'rgba(100,116,139,0.10)',
      color: '#64748b',
      borderColor: 'rgba(100,116,139,0.25)',
    };
  }

  const iconSize = size === 'sm' ? 12 : 14;
  const padding = size === 'sm' ? '2px 8px' : '4px 10px';

  return (
    <span
      className={className}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '5px',
        fontWeight: 600,
        fontSize: '11px',
        borderRadius: '9999px',
        border: '1px solid',
        padding,
        lineHeight: 1.4,
        ...badgeStyle,
      }}
      data-testid="curriculum-readiness-badge"
    >
      <Icon size={iconSize} style={{ flexShrink: 0 }} />
      <span>{label}</span>
    </span>
  );
};
