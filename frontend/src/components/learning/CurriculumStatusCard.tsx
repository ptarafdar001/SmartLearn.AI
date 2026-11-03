import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, ExternalLink, ShieldCheck, Sparkles, BookOpen, Clock, AlertTriangle } from 'lucide-react';
import { CurriculumReadinessBadge } from './CurriculumReadinessBadge';

interface Props {
  subjectName?: string;
  board?: string;
  grade?: string;
  curriculumStatus?: string | null;
  sourceAuthority?: string | null;
  syllabusVersion?: string | null;
  sourceUrl?: string | null;
  statusMessage?: string | null;
  backUrl?: string;
  backLabel?: string;
}

export const CurriculumStatusCard: React.FC<Props> = ({
  subjectName = 'This Subject',
  board,
  grade,
  curriculumStatus = 'in_preparation',
  sourceAuthority,
  syllabusVersion,
  sourceUrl,
  statusMessage,
  backUrl = '/learning/subjects',
  backLabel = 'Back to All Subjects',
}) => {
  const isVerified = curriculumStatus === 'curriculum_verified';
  const isNoSelection = curriculumStatus === 'no_selection';

  return (
    <div
      style={{
        background: 'rgba(15,23,42,0.6)',
        border: '1px solid #1e293b',
        borderRadius: '16px',
        padding: '32px 24px',
        textAlign: 'center',
        maxWidth: '640px',
        margin: '0 auto',
        boxShadow: '0 8px 32px rgba(0,0,0,0.18)',
        backdropFilter: 'blur(8px)',
      }}
      data-testid="curriculum-status-card"
    >
      {/* Icon circle */}
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px' }}>
        {isNoSelection ? (
          <div style={{
            width: 56, height: 56, borderRadius: 12,
            background: 'rgba(245,158,11,0.10)', border: '1px solid rgba(245,158,11,0.2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#f59e0b',
          }}>
            <AlertTriangle style={{ width: 28, height: 28 }} />
          </div>
        ) : isVerified ? (
          <div style={{
            width: 56, height: 56, borderRadius: 12,
            background: 'rgba(99,102,241,0.10)', border: '1px solid rgba(99,102,241,0.2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6366f1',
          }}>
            <ShieldCheck style={{ width: 28, height: 28 }} />
          </div>
        ) : (
          <div style={{
            width: 56, height: 56, borderRadius: 12,
            background: 'rgba(245,158,11,0.10)', border: '1px solid rgba(245,158,11,0.2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#f59e0b',
          }}>
            <Clock style={{ width: 28, height: 28 }} />
          </div>
        )}
      </div>

      {/* Readiness badge */}
      <div style={{ marginBottom: '12px' }}>
        <CurriculumReadinessBadge status={curriculumStatus} />
      </div>

      <h3 style={{ fontSize: '20px', fontWeight: 700, color: '#f1f5f9', margin: '0 0 8px' }}>
        {isNoSelection
          ? 'No Matching Curriculum Selected'
          : `${subjectName} ${isVerified ? 'Curriculum Verified' : 'In Preparation'}`}
      </h3>

      <p style={{ color: '#cbd5e1', fontSize: '14px', lineHeight: 1.7, margin: '0 0 24px' }}>
        {statusMessage ||
          (isVerified
            ? `The curriculum framework for ${subjectName} is verified against official standards. Interactive chapters, multi-modal notes, and practice quizzes are currently being authored.`
            : `Curriculum and learning materials for ${subjectName}${board ? ` (${board}${grade ? ` Class ${grade}` : ''})` : ''} are currently in preparation. Our subject matter team is onboarding authentic syllabi.`)}
      </p>

      {/* Provenance metadata box */}
      {(sourceAuthority || syllabusVersion || sourceUrl) && (
        <div style={{
          background: 'rgba(2,6,23,0.6)',
          border: '1px solid rgba(30,41,59,0.8)',
          borderRadius: '10px',
          padding: '14px 16px',
          marginBottom: '24px',
          textAlign: 'left',
        }}>
          <p style={{
            fontWeight: 700,
            color: '#cbd5e1',
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            fontSize: '11px',
            margin: '0 0 10px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}>
            <Sparkles style={{ width: 13, height: 13, color: '#818cf8', flexShrink: 0 }} />
            Curriculum Grounding Metadata
          </p>
          {sourceAuthority && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#94a3b8', fontSize: '13px', marginBottom: '6px' }}>
              <span>Issuing Authority:</span>
              <span style={{ fontWeight: 600, color: '#e2e8f0' }}>{sourceAuthority}</span>
            </div>
          )}
          {syllabusVersion && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#94a3b8', fontSize: '13px', marginBottom: '6px' }}>
              <span>Syllabus Version:</span>
              <span style={{ fontWeight: 600, color: '#e2e8f0' }}>{syllabusVersion}</span>
            </div>
          )}
          {sourceUrl && (
            <div style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              color: '#94a3b8', fontSize: '13px',
              paddingTop: '8px', borderTop: '1px solid rgba(30,41,59,0.6)',
            }}>
              <span>Official Reference:</span>
              <a
                href={sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: '#818cf8',
                  textDecoration: 'underline',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                View Syllabus <ExternalLink style={{ width: 12, height: 12, flexShrink: 0 }} />
              </a>
            </div>
          )}
        </div>
      )}

      {/* Action buttons */}
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
        <Link
          to={backUrl}
          style={{
            display: 'inline-flex', alignItems: 'center', gap: '6px',
            padding: '9px 18px', borderRadius: '10px',
            background: '#1e293b', color: '#e2e8f0',
            fontSize: '13px', fontWeight: 600, textDecoration: 'none',
            transition: 'background 0.15s',
          }}
        >
          <ArrowLeft style={{ width: 15, height: 15, flexShrink: 0 }} />
          {backLabel}
        </Link>
        <Link
          to="/dashboard"
          style={{
            display: 'inline-flex', alignItems: 'center', gap: '6px',
            padding: '9px 18px', borderRadius: '10px',
            background: '#4f46e5', color: '#ffffff',
            fontSize: '13px', fontWeight: 600, textDecoration: 'none',
            transition: 'background 0.15s',
          }}
        >
          <BookOpen style={{ width: 15, height: 15, flexShrink: 0 }} />
          Student Dashboard
        </Link>
      </div>
    </div>
  );
};
