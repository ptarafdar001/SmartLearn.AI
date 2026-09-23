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
  let bgClass = 'bg-amber-500/10 text-amber-300 border-amber-500/20';

  if (normalized === 'content_available') {
    label = 'Content Available';
    Icon = BookOpen;
    bgClass = 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20';
  } else if (normalized === 'curriculum_verified') {
    label = 'Curriculum Verified';
    Icon = ShieldCheck;
    bgClass = 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20';
  } else if (normalized === 'no_selection') {
    label = 'No Selection';
    Icon = AlertCircle;
    bgClass = 'bg-slate-500/10 text-slate-300 border-slate-500/20';
  }

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${bgClass} ${sizeClasses} ${className}`}
      data-testid="curriculum-readiness-badge"
    >
      <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      <span>{label}</span>
    </span>
  );
};
