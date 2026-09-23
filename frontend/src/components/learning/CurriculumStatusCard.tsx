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
      className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 sm:p-8 text-center max-w-2xl mx-auto shadow-xl backdrop-blur-sm"
      data-testid="curriculum-status-card"
    >
      <div className="flex justify-center mb-4">
        {isNoSelection ? (
          <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <AlertTriangle className="w-7 h-7" />
          </div>
        ) : isVerified ? (
          <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <ShieldCheck className="w-7 h-7" />
          </div>
        ) : (
          <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Clock className="w-7 h-7" />
          </div>
        )}
      </div>

      <div className="mb-3">
        <CurriculumReadinessBadge status={curriculumStatus} />
      </div>

      <h3 className="text-xl sm:text-2xl font-bold text-white mb-2">
        {isNoSelection
          ? 'No Matching Curriculum Selected'
          : `${subjectName} ${isVerified ? 'Curriculum Verified' : 'In Preparation'}`}
      </h3>

      <p className="text-slate-300 text-sm sm:text-base leading-relaxed mb-6">
        {statusMessage ||
          (isVerified
            ? `The curriculum framework for ${subjectName} is verified against official standards. Interactive chapters, multi-modal notes, and practice quizzes are currently being authored.`
            : `Curriculum and learning materials for ${subjectName}${board ? ` (${board}${grade ? ` Class ${grade}` : ''})` : ''} are currently in preparation. Our subject matter team is onboarding authentic syllabi.`)}
      </p>

      {/* Provenance metadata box - shown only when metadata actually exists */}
      {(sourceAuthority || syllabusVersion || sourceUrl) && (
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 mb-6 text-left text-xs sm:text-sm space-y-2">
          <p className="font-semibold text-slate-300 uppercase tracking-wider text-[11px] mb-2 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            Curriculum Grounding Metadata
          </p>
          {sourceAuthority && (
            <div className="flex justify-between items-center text-slate-400">
              <span>Issuing Authority:</span>
              <span className="font-medium text-slate-200">{sourceAuthority}</span>
            </div>
          )}
          {syllabusVersion && (
            <div className="flex justify-between items-center text-slate-400">
              <span>Syllabus Version:</span>
              <span className="font-medium text-slate-200">{syllabusVersion}</span>
            </div>
          )}
          {sourceUrl && (
            <div className="flex justify-between items-center text-slate-400 pt-1 border-t border-slate-800/60">
              <span>Official Reference:</span>
              <a
                href={sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 underline"
              >
                View Syllabus <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          )}
        </div>
      )}

      <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
        <Link
          to={backUrl}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          {backLabel}
        </Link>
        <Link
          to="/dashboard"
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors"
        >
          <BookOpen className="w-4 h-4" />
          Student Dashboard
        </Link>
      </div>
    </div>
  );
};
