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
  LogOut,
  ArrowRight,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { BrandLogo } from '../../components/common/BrandLogo';
import { fetchTopicDetail, saveTopicProgress } from '../../services/learning';
import { TutorDrawer } from '../../components/learning/TutorDrawer';
import type { LearningResource, ProgressStatus, TopicDetail } from '../../types/learning';
import '../../styles/learning.css';

interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

const SELF_CHECK_QUIZ: QuizQuestion[] = [
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
  const { user, logout } = useAuth();

  const [topic, setTopic] = useState<TopicDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);
  const [isTutorOpen, setIsTutorOpen] = useState<boolean>(false);

  // Active resource tab ('video' | 'notes' | 'text' | 'practice')
  const [activeTab, setActiveTab] = useState<string>('video');

  // Study timer (seconds spent in this session)
  const [sessionSeconds, setSessionSeconds] = useState<number>(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Local progress state
  const [currentStatus, setCurrentStatus] = useState<ProgressStatus>('not_started');
  const [currentPct, setCurrentPct] = useState<number>(0);

  // Self-assessment interactive quiz state
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
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

          // Select first available resource type if video is not available
          if (data.resources.length > 0) {
            const hasVideo = data.resources.some((r) => r.resource_type === 'video');
            if (hasVideo) {
              setActiveTab('video');
            } else {
              setActiveTab(data.resources[0].resource_type);
            }
          }
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

  const handleSelectOption = (questionId: number, optionIdx: number) => {
    setSelectedAnswers((prev) => ({ ...prev, [questionId]: optionIdx }));
  };

  const handleCheckAnswer = (questionId: number) => {
    setSubmittedAnswers((prev) => ({ ...prev, [questionId]: true }));
  };

  const studentName = user?.full_name || 'Student';

  // Group resources by type
  const activeResources: LearningResource[] =
    topic?.resources.filter((r) => r.resource_type === activeTab) || [];

  return (
    <div className="learn-layout">
      {/* Top Navigation */}
      <header className="learn-nav">
        <div className="learn-nav-container">
          <Link to="/dashboard" className="learn-nav-brand" aria-label="SmartLearn Home">
            <BrandLogo size="sm" />
            <span className="learn-brand-text">SmartLearn.AI</span>
          </Link>

          <div className="learn-nav-actions">
            <div className="learn-user-pill">
              <div className="learn-user-avatar">{studentName.charAt(0).toUpperCase()}</div>
              <span className="learn-user-name">{studentName}</span>
            </div>

            <button type="button" className="learn-signout-btn" onClick={logout} aria-label="Sign out">
              <LogOut size={14} />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="learn-container">
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
                  {/* Verified provenance header */}
                  {activeResources.map((res) => (
                    <div key={res.id} style={{ marginBottom: '20px' }}>
                      <div className="resource-provenance">
                        <span className="provenance-tag">Provider: {res.provider || 'SmartLearn'}</span>
                        {res.is_verified && (
                          <span className="verified-badge">
                            <Check size={12} />
                            <span>Official Verified CISCE Curriculum Notes</span>
                          </span>
                        )}
                      </div>
                      <h2 className="resource-title">{res.title}</h2>
                      {res.text_content && (
                        <div className="notes-highlight-banner">
                          <p>{res.text_content}</p>
                        </div>
                      )}
                    </div>
                  ))}

                  {/* Structured Pedagogical Concept Cards */}
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

                    <div className="concept-card">
                      <div className="concept-card-badge">Key Concept 3</div>
                      <h3 className="concept-card-title">Dual Imperial Objectives</h3>
                      <p className="concept-card-text">
                        Military deployment (swift mobilization of garrison troops) and commercial exploitation (siphoning agrarian raw materials like raw cotton and wheat directly to ports for shipment to British factories).
                      </p>
                    </div>

                    <div className="concept-card">
                      <div className="concept-card-badge">Key Concept 4</div>
                      <h3 className="concept-card-title">Drain of Wealth &amp; De-industrialisation</h3>
                      <p className="concept-card-text">
                        Import tariffs favored machine-made British textiles entering India, while indigenous handloom weavers lost markets, leading to severe rural indebtedness and the drain of capital.
                      </p>
                    </div>
                  </div>

                  {/* Interactive Visual Progression Diagram */}
                  <div className="notes-diagram-box">
                    <div className="diagram-header">
                      <h3 className="diagram-title">Historical &amp; Economic Flow: Colonial Railway Network</h3>
                      <span className="diagram-subtitle">4-stage imperial mechanism</span>
                    </div>

                    <div className="diagram-steps-grid">
                      <div className="diagram-step-card">
                        <div className="step-number">01</div>
                        <h4 className="step-title">1853 Inception</h4>
                        <p className="step-desc">
                          First 21-mile route from Bombay to Thane; Dalhousie's proposal for national trunk lines.
                        </p>
                      </div>

                      <div className="diagram-step-arrow">
                        <ArrowRight size={20} className="text-indigo-400" />
                      </div>

                      <div className="diagram-step-card">
                        <div className="step-number">02</div>
                        <h4 className="step-title">Capital Influx</h4>
                        <p className="step-desc">
                          British joint-stock firms invest with zero risk under the guaranteed 5% dividend system.
                        </p>
                      </div>

                      <div className="diagram-step-arrow">
                        <ArrowRight size={20} className="text-indigo-400" />
                      </div>

                      <div className="diagram-step-card">
                        <div className="step-number">03</div>
                        <h4 className="step-title">Port Feeder Lines</h4>
                        <p className="step-desc">
                          Tracks designed to funnel agricultural crops from rural districts straight to maritime ports.
                        </p>
                      </div>

                      <div className="diagram-step-arrow">
                        <ArrowRight size={20} className="text-indigo-400" />
                      </div>

                      <div className="diagram-step-card">
                        <div className="step-number">04</div>
                        <h4 className="step-title">Drain of Wealth</h4>
                        <p className="step-desc">
                          Guaranteed deficits debited from colonial treasury; domestic cottage artisans lose viability.
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* High-Yield Exam Pointers Callout */}
                  <div className="exam-pointers-callout">
                    <h3 className="exam-pointers-title">High-Yield Exam Takeaways:</h3>
                    <ul className="exam-pointers-list">
                      <li><strong>16 April 1853:</strong> First train run from Bombay to Thane under Great Indian Peninsula Railway (GIPR).</li>
                      <li><strong>The Guarantee System:</strong> 5% return guaranteed from Indian taxes, removing investor incentive for economy or efficiency.</li>
                      <li><strong>Telegraph Network:</strong> Installed simultaneously by Lord Dalhousie along railway alignments to ensure immediate administrative control.</li>
                    </ul>
                  </div>
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
                  <div className="practice-header">
                    <div>
                      <h2 className="practice-title">Interactive Knowledge Check</h2>
                      <p className="practice-subtitle">
                        Test your mastery of official CISCE Class 11 History concepts for this topic.
                      </p>
                    </div>
                    <span className="practice-count-badge">{SELF_CHECK_QUIZ.length} Practice Questions</span>
                  </div>

                  <div className="quiz-questions-list">
                    {SELF_CHECK_QUIZ.map((q, qIndex) => {
                      const selected = selectedAnswers[q.id];
                      const isSubmitted = submittedAnswers[q.id];
                      const isCorrect = selected === q.correctIndex;

                      return (
                        <div key={q.id} className="quiz-question-card">
                          <div className="quiz-q-num">Question {qIndex + 1} of {SELF_CHECK_QUIZ.length}</div>
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
                  aria-label={
                    currentStatus === 'completed'
                      ? 'Mark as incomplete'
                      : 'Mark topic as completed 100%'
                  }
                >
                  {saving
                    ? 'Saving...'
                    : currentStatus === 'completed'
                      ? '✓ Completed (Click to Reset)'
                      : '✓ Mark Complete (100%)'}
                </button>

                <Link
                  to="/dashboard"
                  className="continue-action-btn progress-dashboard-btn"
                  aria-label="Return to Dashboard to see updated metrics"
                >
                  <span>Dashboard →</span>
                </Link>
              </div>
            </section>
          </>
        ) : (
          <div className="learn-empty-state">
            <BookOpen size={32} className="empty-state-icon" />
            <p>Topic not found.</p>
            <Link to="/dashboard" className="continue-action-btn" style={{ marginTop: '16px' }}>
              <span>Return to Dashboard</span>
            </Link>
          </div>
        )}
      </main>

      {/* Floating AI Tutor Trigger Button */}
      {topic && (
        <button
          type="button"
          className="floating-tutor-btn"
          onClick={() => setIsTutorOpen(true)}
          aria-label="Open AI Tutor to ask doubts"
        >
          <span className="floating-tutor-icon" aria-hidden="true">
            <Bot size={20} />
          </span>
          <span>Ask AI Tutor</span>
        </button>
      )}

      {/* AI Tutor Slide-over Drawer */}
      {topic && (
        <TutorDrawer
          isOpen={isTutorOpen}
          onClose={() => setIsTutorOpen(false)}
          topicId={topic.id}
          topicTitle={topic.title}
          subjectName={topic.subject_name}
          chapterTitle={topic.chapter_title}
          chapterNumber={topic.chapter_number}
        />
      )}
    </div>
  );
};
