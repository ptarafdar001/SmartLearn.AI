import React, { useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  ChevronRight,
  Clock,
  Video,
  FileText,
  BookOpen,
  HelpCircle,
  Check,
  CheckCircle2,
  ExternalLink,
  Bot,
  AlertCircle,
  Compass,
} from 'lucide-react';
import {
  fetchTopicDetail,
  fetchTopicStudyNotes,
  fetchPracticeQuestions,
  saveTopicProgress,
} from '../../services/learning';
import { TutorDrawer } from '../../components/learning/TutorDrawer';
import { AppLayout } from '../../components/layout/AppLayout';
import { MarkdownRenderer } from '../../components/learning/MarkdownRenderer';
import type {
  LearningResource,
  PracticeQuestion,
  ProgressStatus,
  TopicDetail,
  TopicStudyNotes,
} from '../../types/learning';
import '../../styles/learning.css';

interface StaticQuizQuestion {
  id: number;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

const HIST_TOPIC_44_QUIZ: StaticQuizQuestion[] = [
  {
    id: 1,
    question: 'In which year did the first commercial passenger railway run in colonial India, connecting Bombay to Thane?',
    options: ['1848', '1853', '1857', '1861'],
    correctIndex: 1,
    explanation: 'The first train in India ran between Bombay (Bori Bunder) and Thane on 16 April 1853, covering approximately 21 miles (34 km).',
  },
  {
    id: 2,
    question: 'Under the colonial Guarantee System, what annual rate of return did the British Indian government promise private British railway companies?',
    options: ['2.5% return', '5% guaranteed return from Indian revenues', '10% profit-sharing', 'Zero guaranteed return'],
    correctIndex: 1,
    explanation: 'The British administration guaranteed a minimum 5% annual return on invested capital to private British railway firms, paid directly from Indian tax revenues regardless of operational profit.',
  },
  {
    id: 3,
    question: 'What was the primary imperial motivation underlying the layout and route selection of the colonial railway network?',
    options: [
      'Promoting regional Indian manufacturing and small cottage industries',
      'Connecting interior cotton/wheat hubs to ports and facilitating rapid troop movements',
      'Providing free passenger transport for rural agricultural laborers',
      'Developing indigenous metallurgical and locomotive workshops',
    ],
    correctIndex: 1,
    explanation: 'Railways were designed strategically to dispatch troops rapidly during internal unrest and extract agrarian raw materials from the hinterland to coastal ports for export to Britain.',
  },
];

export const TopicStudyPage: React.FC = () => {
  const { topicId } = useParams<{ topicId: string }>();

  const [topic, setTopic] = useState<TopicDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);
  const [isTutorOpen, setIsTutorOpen] = useState<boolean>(false);

  // Active resource tab ('video' | 'interactive' | 'notes' | 'text' | 'practice')
  const [activeTab, setActiveTab] = useState<string>('video');

  // Study timer (seconds spent in this session)
  const [sessionSeconds, setSessionSeconds] = useState<number>(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Local progress state
  const [currentStatus, setCurrentStatus] = useState<ProgressStatus>('not_started');
  const [currentPct, setCurrentPct] = useState<number>(0);
  const [dynamicNotes, setDynamicNotes] = useState<TopicStudyNotes | null>(null);

  // Dynamic practice questions from backend
  const [practiceQuestions, setPracticeQuestions] = useState<PracticeQuestion[]>([]);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string | number>>({});
  const [submittedAnswers, setSubmittedAnswers] = useState<Record<number, boolean>>({});

  useEffect(() => {
    let isMounted = true;

    async function loadTopic() {
      if (!topicId) return;

      try {
        setLoading(true);
        setError(null);
        const data = await fetchTopicDetail(Number(topicId));
        if (isMounted) {
          setTopic(data);
          const prog = data.progress || data.user_progress;
          if (prog) {
            setCurrentStatus(prog.status);
            setCurrentPct(prog.progress_percentage);
            setSessionSeconds(prog.time_spent_seconds || 0);
          }

          // Prioritize resource modality tab selection
          if (data.resources.length > 0) {
            const hasInteractive = data.resources.some((r) => r.resource_type === 'interactive');
            const hasVideo = data.resources.some((r) => r.resource_type === 'video');
            const hasNotes = data.resources.some((r) => r.resource_type === 'notes');
            if (hasInteractive) {
              setActiveTab('interactive');
            } else if (hasVideo) {
              setActiveTab('video');
            } else if (hasNotes) {
              setActiveTab('notes');
            } else {
              setActiveTab(data.resources[0].resource_type);
            }
          }
        }

        // Attempt loading dynamic 10-part study notes
        try {
          const notesData = await fetchTopicStudyNotes(Number(topicId));
          if (isMounted) {
            setDynamicNotes(notesData);
          }
        } catch {
          // silent fallback
        }

        // Attempt loading dynamic practice questions
        try {
          const pqs = await fetchPracticeQuestions(Number(topicId));
          if (isMounted && Array.isArray(pqs) && pqs.length > 0) {
            setPracticeQuestions(pqs);
          }
        } catch {
          // silent fallback
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to load topic learning resources.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadTopic();

    // Start session timer
    timerRef.current = setInterval(() => {
      setSessionSeconds((prev) => prev + 1);
    }, 1000);

    return () => {
      isMounted = false;
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [topicId]);

  const handleUpdateProgress = async (newStatus: ProgressStatus, newPct: number) => {
    if (!topicId) return;

    try {
      setSaving(true);
      setSaveSuccess(null);
      setError(null);

      const resp = await saveTopicProgress(Number(topicId), {
        status: newStatus,
        progress_percentage: newPct,
        time_spent_seconds: sessionSeconds,
      });

      setCurrentStatus(resp.status);
      setCurrentPct(resp.progress_percentage);
      setSaveSuccess(
        newStatus === 'completed'
          ? 'Topic marked as completed! 100% saved.'
          : `Progress updated to ${newPct}%.`
      );

      // Auto-clear success message after 4 seconds
      setTimeout(() => {
        setSaveSuccess(null);
      }, 4000);
    } catch (err: any) {
      setError(err.message || 'Failed to save progress.');
    } finally {
      setSaving(false);
    }
  };

  const handleSelectOption = (questionId: number, optionVal: string | number) => {
    setSelectedAnswers((prev) => ({ ...prev, [questionId]: optionVal }));
  };

  const handleCheckAnswer = (questionId: number) => {
    setSubmittedAnswers((prev) => ({ ...prev, [questionId]: true }));
  };

  // Group resources by type
  const activeResources: LearningResource[] =
    topic?.resources.filter((r) => r.resource_type === activeTab) || [];

  return (
    <AppLayout
      breadcrumbs={[
        { label: 'My Subjects', href: '/subjects' },
        { label: topic?.subject_name || 'Subject', href: topic ? `/learning/subjects/${topic.subject_id}` : undefined },
        { label: topic?.title || 'Topic' },
      ]}
    >
      <div className="compact-page-wrapper">
        {/* Breadcrumb Navigation */}
        <nav className="learn-breadcrumbs" aria-label="Breadcrumbs">
          <Link to="/dashboard" className="learn-breadcrumb-link">
            Dashboard
          </Link>
          <ChevronRight size={14} className="learn-breadcrumb-sep" />
          {topic && (
            <>
              <Link
                to={`/learning/subjects/${topic.subject_id}`}
                className="learn-breadcrumb-link"
              >
                {topic.subject_name}
              </Link>
              <ChevronRight size={14} className="learn-breadcrumb-sep" />
              <span className="learn-breadcrumb-link">{topic.chapter_title}</span>
              <ChevronRight size={14} className="learn-breadcrumb-sep" />
            </>
          )}
          <span className="learn-breadcrumb-current">{topic?.title || 'Topic'}</span>
        </nav>

        {error && (
          <div className="learn-error-box" role="alert">
            <AlertCircle size={18} className="text-amber-600" />
            <div>
              <strong>Error:</strong> {error}
            </div>
          </div>
        )}

        {saveSuccess && (
          <div className="learn-success-box" role="status">
            <CheckCircle2 size={18} className="text-emerald-600" />
            <div>{saveSuccess}</div>
          </div>
        )}

        {loading ? (
          <div className="learn-loading-container" aria-live="polite">
            <div className="learn-spinner" aria-hidden="true" />
            <p>Loading lesson and educational resources...</p>
          </div>
        ) : topic ? (
          <>
            {/* Header Card */}
            <div className="study-header">
              <div className="study-badges-row">
                <span className="subject-badge">{topic.subject_name}</span>
                <span className="subject-badge">
                  Chapter {topic.chapter_number}: {topic.chapter_title}
                </span>
                <span className="subject-badge">Topic {topic.topic_number}</span>
              </div>

              <h1 className="study-title">{topic.title}</h1>
              {topic.description && <p className="study-desc">{topic.description}</p>}

              <div className="study-meta-row">
                <div className="study-meta-left">
                  <span className="study-timer-badge">
                    <Clock size={14} />
                    <span>Est. Study Time: {topic.estimated_minutes} mins</span>
                  </span>
                  <span className="study-meta-sep">•</span>
                  <span className="study-session-badge">
                    <Clock size={14} />
                    <span>
                      Session: {Math.floor(sessionSeconds / 60)}m {sessionSeconds % 60}s
                    </span>
                  </span>
                </div>

                <div className="study-meta-right">
                  <button
                    type="button"
                    className="study-tutor-btn"
                    onClick={() => setIsTutorOpen(true)}
                    aria-label="Open AI Tutor to ask doubts"
                  >
                    <Bot size={16} />
                    <span>Ask AI Tutor</span>
                  </button>

                  <span className="study-status-indicator">
                    Status:{' '}
                    <span
                      className={`status-text-${currentStatus}`}
                    >
                      {currentStatus === 'completed'
                        ? 'Completed (100%)'
                        : currentStatus === 'in_progress'
                          ? `In Progress (${currentPct}%)`
                          : 'Not Started'}
                    </span>
                  </span>
                </div>
              </div>
            </div>

            {/* Modality Selection Bar */}
            <div className="modalities-bar" role="tablist" aria-label="Learning modalities">
              {/* Interactive Simulation Tab (Shown if topic has interactive resources) */}
              {topic.resources.some((r) => r.resource_type === 'interactive') && (
                <button
                  type="button"
                  role="tab"
                  aria-selected={activeTab === 'interactive'}
                  className={`modality-tab ${activeTab === 'interactive' ? 'active' : ''}`}
                  onClick={() => setActiveTab('interactive')}
                >
                  <Compass size={16} />
                  <span>Interactive Simulation</span>
                </button>
              )}

              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'video'}
                className={`modality-tab ${activeTab === 'video' ? 'active' : ''}`}
                onClick={() => setActiveTab('video')}
              >
                <Video size={16} />
                <span>Video Lesson</span>
              </button>

              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'notes'}
                className={`modality-tab ${activeTab === 'notes' ? 'active' : ''}`}
                onClick={() => setActiveTab('notes')}
              >
                <FileText size={16} />
                <span>Study Notes &amp; Summary</span>
              </button>

              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'text'}
                className={`modality-tab ${activeTab === 'text' ? 'active' : ''}`}
                onClick={() => setActiveTab('text')}
              >
                <BookOpen size={16} />
                <span>Reading Material</span>
              </button>

              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'practice'}
                className={`modality-tab ${activeTab === 'practice' ? 'active' : ''}`}
                onClick={() => setActiveTab('practice')}
              >
                <HelpCircle size={16} />
                <span>Practice &amp; Quick Quiz</span>
              </button>
            </div>

            {/* Resource Display Area */}
            <div className="resource-viewer" role="tabpanel" aria-labelledby={`tab-${activeTab}`}>
              {/* TAB: INTERACTIVE SIMULATION */}
              {activeTab === 'interactive' && (
                <div className="simulation-viewer-container">
                  {activeResources.length === 0 ? (
                    <div className="learn-empty-state">
                      <p>No interactive simulations available for this topic yet.</p>
                    </div>
                  ) : (
                    activeResources.map((res) => (
                      <div key={res.id} className="resource-item-block">
                        <div className="resource-provenance">
                          <span className="provenance-tag">Provider: {res.provider?.toUpperCase() || 'SmartLearn'}</span>
                          {res.source_name && (
                            <span>
                              Source: <strong>{res.source_name}</strong>
                            </span>
                          )}
                          {res.is_verified && (
                            <span className="verified-badge">
                              <Check size={12} />
                              <span>Official Verified Simulation Lab</span>
                            </span>
                          )}
                        </div>

                        <h2 className="resource-title">{res.title}</h2>
                        {res.text_content && (
                          <p className="text-sm text-slate-600 mb-4">{res.text_content}</p>
                        )}

                        {res.content_url && (
                          <div className="simulation-wrapper">
                            <div
                              className="simulation-container"
                              style={{
                                position: 'relative',
                                width: '100%',
                                height: '580px',
                                borderRadius: '12px',
                                overflow: 'hidden',
                                border: '1px solid #cbd5e1',
                                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
                              }}
                            >
                              <iframe
                                src={res.content_url}
                                title={res.title}
                                style={{ width: '100%', height: '100%', border: 'none' }}
                                allow="fullscreen"
                                sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                              />
                            </div>
                            <div className="youtube-fallback-banner" style={{ marginTop: '12px' }}>
                              <div className="youtube-fallback-info">
                                <span className="youtube-fallback-badge" style={{ backgroundColor: '#1d4ed8' }}>
                                  PhET Simulation
                                </span>
                                <span>Embedding restricted or running on low power mode?</span>
                              </div>
                              <a
                                href={res.source_url || res.content_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="youtube-direct-link"
                                aria-label={`Open ${res.title} directly in browser`}
                              >
                                <span>Open in External Tab</span>
                                <ExternalLink size={13} />
                              </a>
                            </div>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* TAB 1: VIDEO LESSON */}
              {activeTab === 'video' && (
                <>
                  {activeResources.length === 0 ? (
                    <div className="learn-empty-state">
                      <p>No video lessons available for this topic yet.</p>
                    </div>
                  ) : (
                    activeResources.map((res) => (
                      <div key={res.id} className="resource-item-block">
                        <div className="resource-provenance">
                          <span className="provenance-tag">Provider: {res.provider || 'SmartLearn'}</span>
                          {res.source_name && (
                            <span>
                              Source: <strong>{res.source_name}</strong>
                            </span>
                          )}
                          {res.is_verified && (
                            <span className="verified-badge">
                              <Check size={12} />
                              <span>Official Verified Curriculum Resource</span>
                            </span>
                          )}
                        </div>

                        <h2 className="resource-title">{res.title}</h2>

                        {/* YouTube Player with Safe Fallback */}
                        {res.content_url && (
                          <div className="video-wrapper">
                            <div className="video-container">
                              <iframe
                                src={res.content_url}
                                title={res.title}
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen
                                sandbox="allow-scripts allow-same-origin allow-presentation"
                              />
                            </div>
                            <div className="youtube-fallback-banner">
                              <div className="youtube-fallback-info">
                                <span className="youtube-fallback-badge">YouTube</span>
                                <span>Playback issues or embedding restricted?</span>
                              </div>
                              <a
                                href={
                                  res.source_url ||
                                  (res.external_id
                                    ? `https://www.youtube.com/watch?v=${res.external_id}`
                                    : res.content_url)
                                }
                                target="_blank"
                                rel="noopener noreferrer"
                                className="youtube-direct-link"
                                aria-label={`Watch ${res.title} directly on YouTube`}
                              >
                                <span>Watch directly on YouTube</span>
                                <ExternalLink size={13} />
                              </a>
                            </div>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </>
              )}

              {/* TAB 2: STUDY NOTES & RICH ENGAGING VISUALS */}
              {activeTab === 'notes' && (
                <div className="study-notes-enhanced">
                  {dynamicNotes ? (
                    <div className="dynamic-study-notes-wrapper">
                      <div className="flex items-center justify-between p-3.5 bg-indigo-50/70 rounded-xl border border-indigo-100 mb-5">
                        <div className="flex items-center gap-2 text-indigo-950 font-semibold text-xs">
                          <CheckCircle2 size={16} className="text-emerald-600" />
                          <span>10-Part Curriculum Study Notes (Verified {topic?.subject_name || 'Curriculum'} Syllabus)</span>
                        </div>
                        <span className="text-[11px] text-slate-500 font-mono">v{dynamicNotes.version}.0 Verified</span>
                      </div>

                      {dynamicNotes.learning_objectives_json && Array.isArray(dynamicNotes.learning_objectives_json) && (
                        <div className="mb-5 p-3.5 rounded-xl border border-slate-200 bg-slate-50/60">
                          <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-2">
                            Syllabus Learning Objectives
                          </h4>
                          <div className="grid gap-1.5">
                            {dynamicNotes.learning_objectives_json.map((obj, i) => (
                              <div key={i} className="flex items-start gap-2 text-xs text-slate-700">
                                <span className="shrink-0 w-1.5 h-1.5 rounded-full bg-indigo-600 mt-1.5" />
                                <span>{typeof obj === 'string' ? obj : (obj as any).description || JSON.stringify(obj)}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="prose prose-slate max-w-none text-slate-800 text-sm leading-relaxed">
                        <MarkdownRenderer content={dynamicNotes.explanation_markdown} />
                      </div>

                      {/* Dynamic Key Terms & Concept Cards */}
                      {dynamicNotes.key_terms_json && Array.isArray(dynamicNotes.key_terms_json) && dynamicNotes.key_terms_json.length > 0 && (
                        <div className="mt-8">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
                            Key Concepts &amp; Core Definitions
                          </h4>
                          <div className="concept-cards-grid">
                            {dynamicNotes.key_terms_json.map((termItem: any, idx: number) => (
                              <div key={idx} className="concept-card">
                                <div className="concept-card-badge">Concept {idx + 1}</div>
                                <h3 className="concept-card-title">{termItem.term}</h3>
                                <p className="concept-card-text">{termItem.definition}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Dynamic Formulas & Key Milestones */}
                      {dynamicNotes.formulas_and_dates_json && Array.isArray(dynamicNotes.formulas_and_dates_json) && dynamicNotes.formulas_and_dates_json.length > 0 && (
                        <div className="mt-6 p-4 rounded-xl border border-slate-200 bg-slate-50/70">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                            Formulas, Laws &amp; Key Milestones
                          </h4>
                          <div className="grid gap-2 sm:grid-cols-2">
                            {dynamicNotes.formulas_and_dates_json.map((fd: any, idx: number) => (
                              <div key={idx} className="p-3 bg-white rounded-lg border border-slate-200/80 shadow-xs">
                                <div className="text-xs font-semibold text-slate-700">{fd.name || fd.date || fd.event}</div>
                                <div className="text-xs font-mono text-indigo-700 mt-0.5">{fd.formula || fd.event || ''}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Dynamic Common Misconceptions */}
                      {dynamicNotes.common_misconceptions_json && Array.isArray(dynamicNotes.common_misconceptions_json) && dynamicNotes.common_misconceptions_json.length > 0 && (
                        <div className="mt-6 p-4 rounded-xl border border-amber-200 bg-amber-50/60">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-amber-800 mb-2">
                            Common Examination Misconceptions
                          </h4>
                          <div className="space-y-2">
                            {dynamicNotes.common_misconceptions_json.map((cm: any, idx: number) => (
                              <div key={idx} className="text-xs text-amber-950">
                                <strong>Misconception:</strong> {cm.misconception}
                                <br />
                                <strong>Correction:</strong> {cm.correction}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* High-Yield Exam Takeaways */}
                      {dynamicNotes.exam_points_json && Array.isArray(dynamicNotes.exam_points_json) && dynamicNotes.exam_points_json.length > 0 && (
                        <div className="exam-pointers-callout mt-6">
                          <h3 className="exam-pointers-title">High-Yield Exam Takeaways</h3>
                          <ul className="exam-pointers-list">
                            {dynamicNotes.exam_points_json.map((point: string, idx: number) => (
                              <li key={idx}>{point}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {dynamicNotes.source_references_json && Array.isArray(dynamicNotes.source_references_json) && (
                        <div className="mt-8 pt-4 border-t border-slate-200 text-xs text-slate-500 flex flex-wrap items-center gap-3">
                          <span className="font-semibold text-slate-700">Grounded in Verified Sources:</span>
                          {dynamicNotes.source_references_json.map((s, idx) => (
                            <a
                              key={idx}
                              href={s.url || '#'}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-1 text-indigo-600 hover:underline"
                            >
                              <span>{s.title}</span>
                              {s.url && <ExternalLink size={11} />}
                            </a>
                          ))}
                        </div>
                      )}
                    </div>
                  ) : (
                    <>
                      {/* Verified provenance fallback header */}
                      {activeResources.length === 0 ? (
                        <div className="learn-empty-state">
                          <p>Detailed notes are being prepared for this curriculum topic.</p>
                        </div>
                      ) : (
                        activeResources.map((res) => (
                          <div key={res.id} style={{ marginBottom: '20px' }}>
                            <div className="resource-provenance">
                              <span className="provenance-tag">Provider: {res.provider || 'SmartLearn'}</span>
                              {res.is_verified && (
                                <span className="verified-badge">
                                  <Check size={12} />
                                  <span>Official Verified Curriculum Notes</span>
                                </span>
                              )}
                            </div>
                            <h2 className="resource-title">{res.title}</h2>
                            {res.text_content && (
                              <div className="notes-highlight-banner">
                                <MarkdownRenderer content={res.text_content} />
                              </div>
                            )}
                          </div>
                        ))
                      )}

                      {/* Backward-compatibility fallback for ISC Class 11 History Railway Topic (ID 44) */}
                      {topicId === '44' && (
                        <>
                          <div className="concept-cards-grid">
                            <div className="concept-card">
                              <div className="concept-card-badge">Key Concept 1</div>
                              <h3 className="concept-card-title">Lord Dalhousie's Railway Minutes (1853)</h3>
                              <p className="concept-card-text">
                                Governor-General Lord Dalhousie advocated a comprehensive trunk-line railway scheme to link major British administrative presidencies (Calcutta, Bombay, Madras, and Delhi).
                              </p>
                            </div>
                            <div className="concept-card">
                              <div className="concept-card-badge">Key Concept 2</div>
                              <h3 className="concept-card-title">The 5% Guarantee System</h3>
                              <p className="concept-card-text">
                                To attract British private capital without risk, the government pledged free land on 99-year leases and a guaranteed 5% annual dividend on investment, funded through Indian peasant revenues.
                              </p>
                            </div>
                          </div>
                          <div className="exam-pointers-callout mt-6">
                            <h3 className="exam-pointers-title">High-Yield Exam Takeaways:</h3>
                            <ul className="exam-pointers-list">
                              <li><strong>16 April 1853:</strong> First train run from Bombay to Thane under Great Indian Peninsula Railway (GIPR).</li>
                              <li><strong>The Guarantee System:</strong> 5% return guaranteed from Indian taxes, removing investor incentive for economy or efficiency.</li>
                            </ul>
                          </div>
                        </>
                      )}
                    </>
                  )}
                </div>
              )}

              {/* TAB 3: READING MATERIAL */}
              {activeTab === 'text' && (
                <div className="reading-material-container">
                  {activeResources.length === 0 ? (
                    <div className="learn-empty-state">
                      <p>No text resources available for this topic yet.</p>
                    </div>
                  ) : (
                    activeResources.map((res) => (
                      <div key={res.id} className="resource-item-block">
                        <div className="resource-provenance">
                          <span className="provenance-tag">Provider: {res.provider || 'SmartLearn'}</span>
                          {res.is_verified && (
                            <span className="verified-badge">
                              <Check size={12} />
                              <span>Official Verified Textbook Material</span>
                            </span>
                          )}
                        </div>
                        <h2 className="resource-title">{res.title}</h2>
                        {res.text_content && (
                          <div className="text-content-box">
                            <div className="text-article-body">{res.text_content}</div>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* TAB 4: PRACTICE & QUICK QUIZ */}
              {activeTab === 'practice' && (
                <div className="practice-quiz-container">
                  {/* Dynamic Practice Questions from Backend */}
                  {practiceQuestions.length > 0 ? (
                    <>
                      <div className="practice-header">
                        <div>
                          <h2 className="practice-title">Interactive Knowledge Check</h2>
                          <p className="practice-subtitle">
                            Test your mastery of official {topic?.subject_name || 'curriculum'} concepts for this topic.
                          </p>
                        </div>
                        <span className="practice-count-badge">
                          {practiceQuestions.length} Practice {practiceQuestions.length === 1 ? 'Question' : 'Questions'}
                        </span>
                      </div>

                      <div className="quiz-questions-list">
                        {practiceQuestions.map((q, qIndex) => {
                          const selected = selectedAnswers[q.id];
                          const isSubmitted = submittedAnswers[q.id];
                          const isCorrect = String(selected).trim().toUpperCase() === String(q.correct_answer).trim().toUpperCase();

                          const optionsList: { id: string; text: string }[] = Array.isArray(q.options)
                            ? q.options.map((opt: any, idx: number) =>
                                typeof opt === 'string'
                                  ? { id: String.fromCharCode(65 + idx), text: opt }
                                  : { id: opt.id || String.fromCharCode(65 + idx), text: opt.text || String(opt) }
                              )
                            : [];

                          return (
                            <div key={q.id} className="quiz-question-card">
                              <div className="flex items-center justify-between mb-2">
                                <div className="quiz-q-num">
                                  Question {qIndex + 1} of {practiceQuestions.length} • Difficulty: {q.difficulty.toUpperCase()}
                                </div>
                                {q.is_ai_generated && (
                                  <span className="text-[11px] font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
                                    AI Practice
                                  </span>
                                )}
                              </div>
                              <h3 className="quiz-q-text">{q.question_text}</h3>

                              <div className="quiz-options-group">
                                {optionsList.map((opt) => {
                                  const isOptionSelected = selected === opt.id;
                                  let optionClass = 'quiz-opt-btn';

                                  if (isSubmitted) {
                                    if (opt.id === q.correct_answer) {
                                      optionClass += ' correct-opt';
                                    } else if (isOptionSelected) {
                                      optionClass += ' wrong-opt';
                                    }
                                  } else if (isOptionSelected) {
                                    optionClass += ' selected-opt';
                                  }

                                  return (
                                    <button
                                      key={opt.id}
                                      type="button"
                                      className={optionClass}
                                      onClick={() => handleSelectOption(q.id, opt.id)}
                                      disabled={isSubmitted}
                                    >
                                      <span className="opt-letter">{opt.id}</span>
                                      <span className="opt-text">{opt.text}</span>
                                    </button>
                                  );
                                })}
                              </div>

                              {!isSubmitted ? (
                                <button
                                  type="button"
                                  className="quiz-check-btn"
                                  onClick={() => handleCheckAnswer(q.id)}
                                  disabled={selected === undefined}
                                >
                                  Check Answer
                                </button>
                              ) : (
                                <div
                                  className={`quiz-feedback-box ${isCorrect ? 'feedback-correct' : 'feedback-incorrect'}`}
                                >
                                  <div className="feedback-status-row">
                                    {isCorrect ? (
                                      <>
                                        <CheckCircle2 size={16} className="text-emerald-600" />
                                        <span className="feedback-status-text">Correct! Great understanding.</span>
                                      </>
                                    ) : (
                                      <>
                                        <AlertCircle size={16} className="text-amber-600" />
                                        <span className="feedback-status-text">
                                          Incorrect. Correct Answer: {q.correct_answer}
                                        </span>
                                      </>
                                    )}
                                  </div>
                                  <p className="feedback-explanation">{q.explanation}</p>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </>
                  ) : topicId === '44' ? (
                    /* Fallback for ISC Class 11 History Railway topic */
                    <>
                      <div className="practice-header">
                        <div>
                          <h2 className="practice-title">Interactive Knowledge Check</h2>
                          <p className="practice-subtitle">
                            Test your mastery of colonial Indian railway development concepts.
                          </p>
                        </div>
                        <span className="practice-count-badge">{HIST_TOPIC_44_QUIZ.length} Practice Questions</span>
                      </div>

                      <div className="quiz-questions-list">
                        {HIST_TOPIC_44_QUIZ.map((q, qIndex) => {
                          const selected = selectedAnswers[q.id];
                          const isSubmitted = submittedAnswers[q.id];
                          const isCorrect = selected === q.correctIndex;

                          return (
                            <div key={q.id} className="quiz-question-card">
                              <div className="quiz-q-num">Question {qIndex + 1} of {HIST_TOPIC_44_QUIZ.length}</div>
                              <h3 className="quiz-q-text">{q.question}</h3>

                              <div className="quiz-options-group">
                                {q.options.map((opt, optIdx) => {
                                  const isOptionSelected = selected === optIdx;
                                  let optionClass = 'quiz-opt-btn';

                                  if (isSubmitted) {
                                    if (optIdx === q.correctIndex) {
                                      optionClass += ' correct-opt';
                                    } else if (isOptionSelected) {
                                      optionClass += ' wrong-opt';
                                    }
                                  } else if (isOptionSelected) {
                                    optionClass += ' selected-opt';
                                  }

                                  return (
                                    <button
                                      key={optIdx}
                                      type="button"
                                      className={optionClass}
                                      onClick={() => handleSelectOption(q.id, optIdx)}
                                      disabled={isSubmitted}
                                    >
                                      <span className="opt-letter">
                                        {String.fromCharCode(65 + optIdx)}
                                      </span>
                                      <span className="opt-text">{opt}</span>
                                    </button>
                                  );
                                })}
                              </div>

                              {!isSubmitted ? (
                                <button
                                  type="button"
                                  className="quiz-check-btn"
                                  onClick={() => handleCheckAnswer(q.id)}
                                  disabled={selected === undefined}
                                >
                                  Check Answer
                                </button>
                              ) : (
                                <div className={`quiz-feedback-box ${isCorrect ? 'feedback-correct' : 'feedback-incorrect'}`}>
                                  <div className="feedback-status-row">
                                    {isCorrect ? (
                                      <>
                                        <CheckCircle2 size={16} className="text-emerald-600" />
                                        <span className="feedback-status-text">Correct! Great understanding.</span>
                                      </>
                                    ) : (
                                      <>
                                        <AlertCircle size={16} className="text-amber-600" />
                                        <span className="feedback-status-text">Incorrect. Review the syllabus rationale below:</span>
                                      </>
                                    )}
                                  </div>
                                  <p className="feedback-explanation">{q.explanation}</p>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </>
                  ) : (
                    <div className="learn-empty-state">
                      <HelpCircle size={36} className="text-indigo-400 mb-2" />
                      <p className="text-slate-700 font-semibold">No direct quick-quiz questions seeded for this topic yet.</p>
                      <p className="text-xs text-slate-500 max-w-md mx-auto mb-4">
                        You can launch a full curriculum practice quiz or practice with the AI Tutor.
                      </p>
                      <div className="flex justify-center gap-3">
                        <Link
                          to={`/practice?topicId=${topic.id}`}
                          className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-medium hover:bg-indigo-700"
                        >
                          Launch Practice Mode
                        </Link>
                        <button
                          type="button"
                          onClick={() => setIsTutorOpen(true)}
                          className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg text-xs font-medium hover:bg-slate-200"
                        >
                          Ask AI Tutor
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Interactive Progress Tracking Action Bar */}
            <section className="progress-action-bar" aria-label="Topic progress controls">
              <div className="progress-status-indicator">
                <span>Progress:</span>
                <span className="progress-indicator-pct">{currentPct}%</span>
                <span className="progress-indicator-status">({currentStatus.replace('_', ' ')})</span>
              </div>

              <div className="progress-buttons">
                {currentStatus !== 'completed' && (
                  <button
                    type="button"
                    className="btn-progress-toggle"
                    disabled={saving}
                    onClick={() => handleUpdateProgress('in_progress', 50.0)}
                    aria-label="Mark 50% in progress"
                  >
                    {saving ? 'Saving...' : 'Mark In Progress (50%)'}
                  </button>
                )}

                <button
                  type="button"
                  className={`btn-progress-toggle ${currentStatus === 'completed' ? 'completed' : ''}`}
                  disabled={saving}
                  onClick={() =>
                    handleUpdateProgress(
                      currentStatus === 'completed' ? 'in_progress' : 'completed',
                      currentStatus === 'completed' ? 50.0 : 100.0
                    )
                  }
                  aria-label={currentStatus === 'completed' ? 'Mark in progress' : 'Mark topic as completed 100%'}
                >
                  {saving ? 'Saving...' : currentStatus === 'completed' ? 'Mark In Progress' : 'Mark Completed (100%)'}
                </button>
              </div>
            </section>
          </>
        ) : (
          <div className="learn-empty-state">
            <p>Topic not found or access restricted.</p>
          </div>
        )}
      </div>

      {/* Embedded Slide-over AI Tutor Drawer */}
      {topic && (
        <TutorDrawer
          isOpen={isTutorOpen}
          onClose={() => setIsTutorOpen(false)}
          topicId={topic.id}
          topicTitle={topic.title}
          chapterTitle={topic.chapter_title}
          chapterNumber={topic.chapter_number}
          subjectName={topic.subject_name}
        />
      )}
    </AppLayout>
  );
};

export default TopicStudyPage;
