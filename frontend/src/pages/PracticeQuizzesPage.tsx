import React, { useEffect, useState } from 'react';
import {
  CheckCircle,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Sparkles,
  ShieldCheck,
  Send,
  Loader2,
} from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import {
  fetchTopicPYQs,
  fetchPracticeQuestions,
  generatePracticeQuestions,
  submitPracticeAttempt,
} from '../services/learning';
import type { PreviousYearQuestion, PracticeQuestion, PracticeAttemptResponse } from '../types/learning';

export const PracticeQuizzesPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'pyqs' | 'practice'>('pyqs');
  const [topicId] = useState<number>(44); // Seeded ISC Class 11 Topic 44

  // Authentic PYQs State
  const [pyqs, setPyqs] = useState<PreviousYearQuestion[]>([]);
  const [pyqsLoading, setPyqsLoading] = useState<boolean>(true);
  const [expandedSchemes, setExpandedSchemes] = useState<Record<number, boolean>>({});

  // AI Practice State
  const [practiceQuestions, setPracticeQuestions] = useState<PracticeQuestion[]>([]);
  const [practiceLoading, setPracticeLoading] = useState<boolean>(true);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [attemptResults, setAttemptResults] = useState<Record<number, PracticeAttemptResponse>>({});
  const [submittingIds, setSubmittingIds] = useState<Record<number, boolean>>({});
  const [isGenerating, setIsGenerating] = useState<boolean>(false);

  useEffect(() => {
    loadPYQs();
    loadPracticeQuestions();
  }, [topicId]);

  const loadPYQs = async () => {
    try {
      setPyqsLoading(true);
      const data = await fetchTopicPYQs(topicId);
      setPyqs(data);
    } catch (err) {
      console.error('Failed to load PYQs:', err);
    } finally {
      setPyqsLoading(false);
    }
  };

  const loadPracticeQuestions = async () => {
    try {
      setPracticeLoading(true);
      const data = await fetchPracticeQuestions(topicId);
      setPracticeQuestions(data);
    } catch (err) {
      console.error('Failed to load practice questions:', err);
    } finally {
      setPracticeLoading(false);
    }
  };

  const toggleMarkingScheme = (id: number) => {
    setExpandedSchemes((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleSelectOption = (questionId: number, optionId: string) => {
    if (attemptResults[questionId]) return; // locked after attempt
    setSelectedAnswers((prev) => ({ ...prev, [questionId]: optionId }));
  };

  const handleSubmitAttempt = async (questionId: number) => {
    const answer = selectedAnswers[questionId];
    if (!answer) return;

    try {
      setSubmittingIds((prev) => ({ ...prev, [questionId]: true }));
      const result = await submitPracticeAttempt(questionId, answer);
      setAttemptResults((prev) => ({ ...prev, [questionId]: result }));
    } catch (err) {
      console.error('Failed to submit attempt:', err);
    } finally {
      setSubmittingIds((prev) => ({ ...prev, [questionId]: false }));
    }
  };

  const handleGenerateFreshQuestions = async () => {
    try {
      setIsGenerating(true);
      const freshQuestions = await generatePracticeQuestions(topicId);
      setPracticeQuestions(freshQuestions);
      setSelectedAnswers({});
      setAttemptResults({});
    } catch (err) {
      console.error('Failed to generate fresh questions:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <AppLayout breadcrumbs={[{ label: 'Practice & Quizzes' }]}>
      <div className="page-header-compact">
        <div>
          <h1 className="page-title-compact">Practice &amp; Assessment Hub</h1>
          <p className="page-subtitle-compact">
            Official CISCE board examination questions and curriculum-grounded AI practice tests for ISC Class 11 History.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {activeTab === 'practice' && (
            <button
              type="button"
              onClick={handleGenerateFreshQuestions}
              disabled={isGenerating}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-indigo-200 bg-white hover:bg-indigo-50 text-indigo-700 text-xs font-medium transition-colors"
            >
              {isGenerating ? <Loader2 size={13} className="animate-spin" /> : <Sparkles size={13} />}
              <span>{isGenerating ? 'Generating...' : 'Generate AI Practice'}</span>
            </button>
          )}
          <span className="page-count-badge">Topic: Railways &amp; Colonial Infrastructure</span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-200 mb-5">
        <button
          type="button"
          onClick={() => setActiveTab('pyqs')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
            activeTab === 'pyqs'
              ? 'border-indigo-600 text-indigo-700'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <ShieldCheck size={15} />
          <span>Authentic Previous-Year Questions (PYQs)</span>
          <span className="ml-1 px-1.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 text-[10px]">
            {pyqs.length} Official
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('practice')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
            activeTab === 'practice'
              ? 'border-indigo-600 text-indigo-700'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Sparkles size={15} />
          <span>AI-Generated Practice Questions</span>
          <span className="ml-1 px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-700 text-[10px]">
            {practiceQuestions.length} Available
          </span>
        </button>
      </div>

      {/* ── TAB 1: Authentic Previous-Year Questions ────────────────────── */}
      {activeTab === 'pyqs' && (
        <div className="space-y-4">
          <div className="rounded-xl border border-emerald-100 bg-emerald-50/50 p-3.5 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-emerald-800 font-medium">
              <ShieldCheck size={16} className="text-emerald-600 shrink-0" />
              <span>
                These questions are authentic past-year board examination questions with official CISCE paper attribution.
              </span>
            </div>
            <a
              href="https://www.cisce.org/regulations-and-syllabuses-isc/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-emerald-700 font-semibold hover:underline shrink-0 ml-4"
            >
              <span>CISCE Official Regulations</span>
              <ExternalLink size={12} />
            </a>
          </div>

          {pyqsLoading ? (
            <div className="p-8 text-center text-slate-500 text-xs flex items-center justify-center gap-2">
              <Loader2 size={16} className="animate-spin text-indigo-600" />
              <span>Loading authentic previous-year questions...</span>
            </div>
          ) : (
            <div className="grid gap-4">
              {pyqs.map((q) => {
                const isExpanded = expandedSchemes[q.id];

                return (
                  <div key={q.id} className="quiz-card-full">
                    <div className="quiz-card-meta flex-wrap gap-2">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded bg-indigo-50 border border-indigo-200 text-indigo-800 text-[11px] font-bold">
                          {q.board} {q.exam_year}
                        </span>
                        <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px] font-mono">
                          {q.paper_code}
                        </span>
                        <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px] font-medium">
                          {q.question_number}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 ml-auto">
                        <span className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 text-[11px] font-semibold">
                          {q.marks} {q.marks === 1 ? 'Mark' : 'Marks'}
                        </span>
                        <span className="flex items-center gap-1 text-[11px] text-emerald-700 font-medium">
                          <CheckCircle size={13} className="text-emerald-600" />
                          Verified Authentic
                        </span>
                      </div>
                    </div>

                    <h3 className="text-sm font-semibold text-slate-900 mt-2 mb-3 leading-relaxed">
                      {q.question_text}
                    </h3>

                    <div className="flex items-center justify-between border-t border-slate-100 pt-3 mt-3 text-xs">
                      <span className="text-slate-500 text-[11px]">
                        Source: <strong className="text-slate-700 font-medium">{q.source_name}</strong>
                      </span>
                      {q.marking_scheme && (
                        <button
                          type="button"
                          onClick={() => toggleMarkingScheme(q.id)}
                          className="flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-medium transition-colors"
                        >
                          <span>{isExpanded ? 'Hide Marking Scheme' : 'View Official Marking Scheme'}</span>
                          {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                        </button>
                      )}
                    </div>

                    {isExpanded && q.marking_scheme && (
                      <div className="mt-3 p-3.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700">
                        <strong className="block text-slate-900 font-semibold mb-1 text-[11px]">
                          Official Marking Scheme &amp; Key Answer Points:
                        </strong>
                        <p className="whitespace-pre-line leading-relaxed font-sans">{q.marking_scheme}</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ── TAB 2: AI-Generated Practice Questions ──────────────────────── */}
      {activeTab === 'practice' && (
        <div className="space-y-4">
          <div className="rounded-xl border border-indigo-100 bg-indigo-50/40 p-3.5 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-indigo-900 font-medium">
              <Sparkles size={16} className="text-indigo-600 shrink-0" />
              <span>
                These questions are <strong>AI-generated practice questions</strong> synthesized from verified curriculum
                learning objectives. They are not authentic past-year examination questions.
              </span>
            </div>
          </div>

          {practiceLoading ? (
            <div className="p-8 text-center text-slate-500 text-xs flex items-center justify-center gap-2">
              <Loader2 size={16} className="animate-spin text-indigo-600" />
              <span>Loading curriculum practice questions...</span>
            </div>
          ) : (
            <div className="grid gap-4">
              {practiceQuestions.map((q, idx) => {
                const selected = selectedAnswers[q.id];
                const attempt = attemptResults[q.id];
                const isSubmitting = submittingIds[q.id];

                return (
                  <div key={q.id} className="quiz-card-full">
                    <div className="quiz-card-meta flex-wrap gap-2">
                      <div className="flex items-center gap-2">
                        <span className="q-badge">Question {idx + 1}</span>
                        <span className="px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200 text-[10px] font-semibold uppercase tracking-wider">
                          AI-generated practice question
                        </span>
                        <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-[10px] font-medium capitalize">
                          {q.difficulty}
                        </span>
                      </div>
                      {attempt && (
                        <span
                          className={`q-status-badge ${
                            attempt.is_correct ? 'status-correct' : 'status-wrong'
                          }`}
                        >
                          {attempt.is_correct ? 'Correct (+1 Mark)' : 'Incorrect'}
                        </span>
                      )}
                    </div>

                    <h3 className="text-sm font-semibold text-slate-900 mt-2 mb-3 leading-relaxed">
                      {q.question_text}
                    </h3>

                    {/* MCQ Options */}
                    {q.options && (
                      <div className="quiz-options-list">
                        {q.options.map((opt) => {
                          let optClass = 'quiz-opt-row';
                          if (selected === opt.id) optClass += ' selected';
                          if (attempt) {
                            if (opt.id === q.correct_answer) optClass += ' correct';
                            else if (selected === opt.id) optClass += ' wrong';
                          }

                          return (
                            <button
                              key={opt.id}
                              type="button"
                              className={optClass}
                              onClick={() => handleSelectOption(q.id, opt.id)}
                              disabled={!!attempt}
                            >
                              <span className="opt-letter-chip">{opt.id}</span>
                              <span className="opt-label-text">{opt.text}</span>
                            </button>
                          );
                        })}
                      </div>
                    )}

                    {/* Submit Attempt Action */}
                    {!attempt && (
                      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                        <span className="text-[11px] text-slate-500">
                          {selected ? 'Option selected. Click Submit to verify answer.' : 'Select an answer option to submit.'}
                        </span>
                        <button
                          type="button"
                          onClick={() => handleSubmitAttempt(q.id)}
                          disabled={!selected || isSubmitting}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-medium transition-colors"
                        >
                          {isSubmitting ? (
                            <Loader2 size={13} className="animate-spin" />
                          ) : (
                            <Send size={13} />
                          )}
                          <span>{isSubmitting ? 'Evaluating...' : 'Submit Answer'}</span>
                        </button>
                      </div>
                    )}

                    {/* Attempt Feedback */}
                    {attempt && (
                      <div
                        className={`mt-4 p-3.5 rounded-lg text-xs leading-relaxed border ${
                          attempt.is_correct
                            ? 'bg-emerald-50/60 border-emerald-200 text-emerald-900'
                            : 'bg-rose-50/60 border-rose-200 text-rose-900'
                        }`}
                      >
                        <strong className="block font-semibold mb-1">
                          {attempt.is_correct ? 'Correct Analysis:' : 'Pedagogical Explanation:'}
                        </strong>
                        <p>{attempt.explanation}</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </AppLayout>
  );
};
