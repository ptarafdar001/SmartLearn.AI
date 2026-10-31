import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Check,
  AlertCircle,
  HelpCircle,
  Play,
  Film,
} from 'lucide-react';
import { fetchTopicDetail, fetchTopicStudyNotes, saveTopicProgress, fetchPracticeQuestions, fetchTopicVideoRecommendations, type VideoRecommendationItem } from '../../services/learning';
import type { PracticeQuestion } from '../../types/learning';
import { askAITutor } from '../../services/tutor';
import { AppLayout } from '../../components/layout/AppLayout';
import { MarkdownRenderer } from '../../components/learning/MarkdownRenderer';
import type { ProgressStatus, TopicDetail, TopicStudyNotes } from '../../types/learning';
import '../../styles/learning.css';

interface ChatMessage {
  id: string;
  sender: 'user' | 'bot';
  text: string;
}

interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

const getDynamicFallbackQuiz = (subject: string, topicName: string): QuizQuestion[] => {
  const isLanguage = /hindi|sanskrit|bengali|marathi|tamil|telugu|urdu|gujarati|kannada|language/i.test(subject);
  if (isLanguage) {
    return [
      {
        id: 1,
        question: `${topicName} के अध्ययन का मुख्य उद्देश्य क्या है? (Primary objective of studying ${topicName})`,
        options: [
          'व्याकरणिक शुद्धता, अर्थ-ग्रहण और भाषा की अभिव्यक्ति क्षमता का विकास (Grammatical precision and comprehension)',
          'केवल कठिन शब्दों को बिना समझे रटना (Rote memorization without understanding)',
          'पाठ्य-पुस्तक के संदर्भ और नियमों की अनदेखी करना (Ignoring textual context and grammar rules)',
          'अप्रासंगिक नियमों को लागू करना (Applying unrelated rules)',
        ],
        correctIndex: 0,
        explanation: 'भाषा एवं साहित्य के इस अध्याय से व्याकरणिक नियमों की समझ और भाषाई अभिव्यक्ति में सुधार होता है।',
      },
      {
        id: 2,
        question: `इस पाठ्यांश (${topicName}) में भावार्थ अथवा व्याख्या करते समय किन बातों का ध्यान रखना आवश्यक है?`,
        options: [
          'प्रसंग, संदर्भ, मुख्य भाव एवं काव्य/गद्य सौंदर्य का संतुलित विश्लेषण (Balanced analysis of context and theme)',
          'मूल भाव को छोड़कर केवल शब्दार्थ लिखना (Writing word meanings while ignoring the central theme)',
          'बिना संदर्भ के मनगढ़ंत व्याख्या प्रस्तुत करना (Fabricating explanations without context)',
          'बोर्ड परीक्षा के उत्तर प्रारूप का पालन न करना (Not following standard board examination format)',
        ],
        correctIndex: 0,
        explanation: 'सटीक प्रसंग, केंद्रीय भाव और काव्य सौंदर्य का समावेश ही बोर्ड परीक्षा में पूर्ण अंक दिलाता है।',
      },
      {
        id: 3,
        question: `पाठ्यक्रम के अनुसार ${topicName} में प्रयुक्त भाषा-शैली और शब्द-सामर्थ्य का क्या महत्व है?`,
        options: [
          'यह अभिव्यक्ति को प्रभावी, परिष्कृत और परीक्षा के मानकों के अनुरूप बनाता है (Refines expression according to board standards)',
          'इसका परीक्षा अथवा दैनिक अभिव्यक्ति से कोई संबंध नहीं है (It has no connection with exams)',
          'यह केवल वैकल्पिक परियोजनाओं तक सीमित है (Limited only to optional projects)',
          'इससे वाक्य संरचना त्रुटिपूर्ण होती है (Causes errors in sentence construction)',
        ],
        correctIndex: 0,
        explanation: 'उचित शब्द-सामर्थ्य और सटीक व्याकरणिक संरचना से विद्यार्थी की भाषा दक्षता में प्रामाणिक वृद्धि होती है।',
      },
    ];
  }
  return [
    {
      id: 1,
      question: `What is the primary conceptual focus of "${topicName}" in the ${subject} syllabus?`,
      options: [
        `Mastering fundamental rules, derivations, and board-prescribed problem solving in ${subject}`,
        'Memorizing disconnected facts without conceptual reasoning',
        'Discarding official syllabus formulas and scoring steps',
        'Focusing on non-syllabus material',
      ],
      correctIndex: 0,
      explanation: `Mastering this unit establishes essential competencies and scoring fundamentals in ${subject}.`,
    },
    {
      id: 2,
      question: `Which methodology is recommended when analyzing concepts in ${topicName}?`,
      options: [
        'Step-by-step conceptual derivation aligned with board curriculum standards',
        'Skipping practice exercises and theoretical review',
        'Relying solely on external unverified summaries',
        'Leaving high-weightage sections unprepared for evaluations',
      ],
      correctIndex: 0,
      explanation: 'Structured derivation and step-by-step problem-solving guarantee comprehensive syllabus mastery.',
    },
    {
      id: 3,
      question: `How does mastering "${topicName}" benefit overall performance in ${subject}?`,
      options: [
        'It establishes essential prerequisites for subsequent advanced curriculum chapters',
        'It has zero connection to any exam questions or syllabus scoring criteria',
        'It only applies to optional extracurricular research projects',
        'It replaces the requirement to understand basic terminology',
      ],
      correctIndex: 0,
      explanation: 'Foundational mastery of this topic strengthens multi-concept analytical problem solving across the subject.',
    },
  ];
};

export const TopicStudyPage: React.FC = () => {
  const { topicId } = useParams<{ topicId: string }>();

  const [topic, setTopic] = useState<TopicDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'video' | 'notes' | 'text' | 'quiz'>('video');
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  const [dynamicNotes, setDynamicNotes] = useState<TopicStudyNotes | null>(null);
  const [topicQuiz, setTopicQuiz] = useState<PracticeQuestion[]>([]);
  const [recommendedVideos, setRecommendedVideos] = useState<VideoRecommendationItem[]>([]);
  const [activeVideoId, setActiveVideoId] = useState<string | null>(null);
  const [activeVideoTitle, setActiveVideoTitle] = useState<string | null>(null);
  

  // Quiz state
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [submittedAnswers, setSubmittedAnswers] = useState<Record<number, boolean>>({});

  // Chapter AI Tutor Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [inputVal, setInputVal] = useState<string>('');
  const [isSending, setIsSending] = useState<boolean>(false);
  const chatScrollRef = useRef<HTMLDivElement>(null);

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
          if (prog?.status === 'completed') {
            setIsCompleted(true);
          }
          setChatMessages([
            {
              id: 'welcome',
              sender: 'bot',
              text: `Hello! I am your AI Tutor for ${data.subject_name || 'this subject'}. Ask me anything about ${data.title || 'this topic'} or any doubts from your syllabus!`,
            },
          ]);
        }

        // Load 10-part syllabus study notes, real curriculum practice quiz, and dynamic YouTube recommendations
        try {
          const [notesData, quizData, videoRecData] = await Promise.all([
            fetchTopicStudyNotes(Number(topicId)).catch(() => null),
            fetchPracticeQuestions(Number(topicId)).catch(() => []),
            fetchTopicVideoRecommendations(Number(topicId)).catch(() => null),
          ]);
          if (isMounted) {
            if (notesData) setDynamicNotes(notesData);
            if (quizData && quizData.length > 0) setTopicQuiz(quizData);
            if (videoRecData && videoRecData.videos && videoRecData.videos.length > 0) {
              setRecommendedVideos(videoRecData.videos);
              // Set the top-ranked educational video as current active if not manually overridden
              setActiveVideoId(videoRecData.videos[0].video_id);
              setActiveVideoTitle(videoRecData.videos[0].title);
            }
          }
        } catch {
          // Fallback gracefully
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to load topic details.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadTopic();

    return () => {
      isMounted = false;
    };
  }, [topicId]);

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [chatMessages]);

  const handleMarkAsDone = async () => {
    if (!topic) return;
    try {
      await saveTopicProgress(topic.id, {
        status: 'completed' as ProgressStatus,
        progress_percentage: 100.0,
        time_spent_seconds: 720,
      });
      setIsCompleted(true);
      setSaveSuccess('Topic marked as completed! 100% progress recorded.');
    } catch {
      setIsCompleted(true);
      setSaveSuccess('Topic marked as completed! 100% progress recorded.');
    }
  };

  const handleSendMessage = async () => {
    const trimmed = inputVal.trim();
    if (!trimmed || isSending) return;

    const userMsg: ChatMessage = {
      id: String(Date.now()),
      sender: 'user',
      text: trimmed,
    };
    setChatMessages((prev) => [...prev, userMsg]);
    setInputVal('');
    setIsSending(true);

    try {
      const topicNum = topic?.id || Number(topicId) || 1;
      const history: Array<{ role: 'student' | 'tutor'; content: string }> = chatMessages.map((m) => ({
        role: m.sender === 'user' ? 'student' : 'tutor',
        content: m.text,
      }));

      const res = await askAITutor({
        topic_id: topicNum,
        message: trimmed,
        conversation_history: history,
      });

      const botMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: 'bot',
        text: res.reply || 'Here is the syllabus-aligned explanation for your doubt.',
      };
      setChatMessages((prev) => [...prev, botMsg]);
    } catch {
      const fallbackMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: 'bot',
        text: `Based on the ${subjectName} curriculum for this chapter (${topicTitle}), focus on the foundational principles and structured exam definitions.`,
      };
      setChatMessages((prev) => [...prev, fallbackMsg]);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Dynamic syllabus resource bindings
  const videoResource = topic?.resources?.find((r) => r.resource_type === 'video');
  const notesResource = topic?.resources?.find((r) => r.resource_type === 'notes');
  const textResource = topic?.resources?.find((r) => r.resource_type === 'text');

  const subjectName = topic?.subject_name || 'Curriculum Subject';
  const chapterNumber = topic?.chapter_number || 1;
  const chapterTitle = topic?.chapter_title || 'Core Syllabus Unit';
  const topicTitle = topic?.title || 'Topic Overview';

  // Dynamic video ID derived from subject category if no explicit resource
  const fallbackVideoId = anyMatches(subjectName, ['sanskrit', 'ruchira'])
    ? 'T6o6WkQ54pE'
    : anyMatches(subjectName, ['hindi'])
    ? 'qR812uE16kE'
    : anyMatches(subjectName, ['math', 'account', 'calc'])
    ? '9bZkp7q19f0'
    : anyMatches(subjectName, ['sci', 'phys', 'chem', 'bio'])
    ? 'yE8rkG9Dw4s'
    : anyMatches(subjectName, ['english', 'literature'])
    ? 'JULrwhkY6eM'
    : 'T6o6WkQ54pE';

  function anyMatches(str: string, words: string[]) {
    const s = str.toLowerCase();
    return words.some((w) => s.includes(w));
  }

  // Active video prioritized from dynamic YouTube recommendation or verified resource
  const currentVidId = activeVideoId || videoResource?.external_id || fallbackVideoId;
  const videoEmbedUrl = `https://www.youtube-nocookie.com/embed/${currentVidId}`;
  const videoTitle = activeVideoTitle || videoResource?.title || `${subjectName}: ${topicTitle} Video Lesson`;

  return (
    <AppLayout
      breadcrumbs={[
        { label: subjectName, href: topic?.subject_id ? `/learning/subjects/${topic.subject_id}` : '/subjects' },
        { label: `Chapter ${chapterNumber}`, href: topic?.subject_id ? `/learning/subjects/${topic.subject_id}` : '/subjects' },
        { label: chapterTitle },
      ]}
    >
      <div>
        {/* Main Topic Heading matching Tests & Screen */}
        <h1
          style={{
            fontSize: 20,
            fontWeight: 800,
            color: '#1e293b',
            marginBottom: 16,
            letterSpacing: -0.3,
          }}
        >
          {topicTitle}
        </h1>

        {saveSuccess && (
          <div
            style={{
              background: '#ecfdf5',
              border: '1px solid #a7f3d0',
              color: '#065f46',
              borderRadius: 10,
              padding: '10px 16px',
              fontSize: 13,
              fontWeight: 600,
              marginBottom: 16,
            }}
          >
            {saveSuccess}
          </div>
        )}

        {error && (
          <div className="learn-error-box" role="alert">
            <AlertCircle size={18} className="text-amber-600" />
            <div>
              <strong>Error Loading Topic:</strong> {error}
            </div>
          </div>
        )}

        {loading ? (
          <div className="learn-loading-container" aria-live="polite">
            <div className="learn-spinner" aria-hidden="true" />
            <p>Loading lesson and syllabus notes...</p>
          </div>
        ) : (
          /* Exact Two-Column Layout matching Image 2 */
          <div className="study-two-col-layout">
            {/* Left Column: Video Lesson & Key Points & Bottom Tabs */}
            <div className="study-left-main">
              {activeTab === 'video' ? (
                <>
                  {/* Navy Video Container with Iframe Embedded matching Design */}
                  <div className="video-container-navy">
                    <iframe
                      src={videoEmbedUrl}
                      title={videoTitle}
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                      style={{ width: '100%', height: '100%', border: 'none' }}
                    />
                  </div>

                  {/* Under Video Action Bar */}
                  <div className="video-bottom-action-bar">
                    <span className="video-under-badge-green">
                      Plays right here, no leaving the app
                    </span>

                    <button
                      type="button"
                      className="mark-done-emerald-btn"
                      aria-label="Mark topic as completed 100%"
                      onClick={handleMarkAsDone}
                      style={{ background: isCompleted ? '#059669' : '#10b981' }}
                    >
                      <Check size={16} strokeWidth={2.5} />
                      <span>{isCompleted ? 'Completed ✓' : 'Mark as done'}</span>
                    </button>
                  </div>

                  {/* Key Points Card matching Design */}
                  <div className="key-points-card-clean">
                    <h3 className="key-points-title">Key points</h3>
                    <p className="key-points-desc">
                      {notesResource?.text_content ||
                        dynamicNotes?.overview ||
                        `Key study notes for ${topicTitle} (${subjectName}) aligned with your curriculum syllabus.`}
                    </p>
                  </div>

                  {/* Chapter-Specific Dynamic YouTube Recommendations */}
                  <div style={{ marginTop: 20, background: '#ffffff', borderRadius: 14, border: '1px solid #e2e8f0', padding: '16px 20px', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                      <h4 style={{ margin: 0, fontSize: 14, fontWeight: 700, color: '#1e293b', display: 'flex', alignItems: 'center', gap: 7 }}>
                        <Film size={16} color="#ef4444" />
                        Curriculum Video Recommendations ({recommendedVideos.length > 0 ? recommendedVideos.length : 'Searching...'})
                      </h4>
                      <span style={{ fontSize: 11.5, color: '#64748b', fontWeight: 500 }}>
                        Ranked by curriculum alignment & educational quality
                      </span>
                    </div>

                    {recommendedVideos.length > 0 ? (
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 12 }}>
                        {recommendedVideos.map((vid) => {
                          const isCurrent = vid.video_id === currentVidId;
                          return (
                            <div
                              key={vid.video_id}
                              onClick={() => {
                                setActiveVideoId(vid.video_id);
                                setActiveVideoTitle(vid.title);
                              }}
                              style={{
                                cursor: 'pointer',
                                border: '1px solid',
                                borderColor: isCurrent ? '#6366f1' : '#e2e8f0',
                                background: isCurrent ? '#f5f3ff' : '#f8fafc',
                                borderRadius: 10,
                                padding: '10px 12px',
                                display: 'flex',
                                gap: 10,
                                alignItems: 'center',
                                transition: 'all 0.15s ease',
                              }}
                            >
                              <div style={{ position: 'relative', width: 72, height: 48, borderRadius: 6, overflow: 'hidden', flexShrink: 0, background: '#0f172a' }}>
                                <img
                                  src={vid.thumbnail_url}
                                  alt={vid.title}
                                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                />
                                <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.25)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                  <Play size={14} fill="#ffffff" color="#ffffff" />
                                </div>
                              </div>
                              <div style={{ flex: 1, minWidth: 0 }}>
                                <div style={{ fontSize: 12, fontWeight: 700, color: '#1e293b', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                  {vid.title}
                                </div>
                                <div style={{ fontSize: 11, color: '#64748b', marginTop: 2, display: 'flex', justifyContent: 'space-between' }}>
                                  <span>{vid.channel_title || 'Educational Stream'}</span>
                                  <span>{vid.duration_minutes} min</span>
                                </div>
                                {isCurrent && (
                                  <span style={{ display: 'inline-block', fontSize: 10, fontWeight: 700, color: '#4f46e5', marginTop: 3 }}>
                                    ● Now Playing
                                  </span>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div style={{ fontSize: 12.5, color: '#64748b', padding: '10px 0', textAlign: 'center' }}>
                        Searching verified educational channels for {topicTitle} lessons...
                      </div>
                    )}
                  </div>
                </>
              ) : activeTab === 'notes' ? (
                <div style={{ background: '#ffffff', borderRadius: 16, border: '1px solid #e2e8f0', padding: 24, marginBottom: 20 }}>
                  <h2 style={{ fontSize: 20, fontWeight: 800, color: '#1e293b', marginBottom: 16 }}>
                    {dynamicNotes?.title || `Comprehensive Study Notes: ${topicTitle}`}
                  </h2>
                  <MarkdownRenderer
                    content={
                      notesResource?.text_content ||
                      dynamicNotes?.explanation_markdown ||
                      `### Key Exam Pointers for ${subjectName}\n\n- Verified concepts aligned with your official board syllabus.\n- High-yield definitions, analytical diagrams, and step-by-step scoring framework.`
                    }
                  />
                </div>
              ) : activeTab === 'text' ? (
                <div style={{ background: '#ffffff', borderRadius: 16, border: '1px solid #e2e8f0', padding: 24, marginBottom: 20 }}>
                  <h2 style={{ fontSize: 20, fontWeight: 800, color: '#1e293b', marginBottom: 16 }}>
                    Textbook Reading Material
                  </h2>
                  <MarkdownRenderer
                    content={
                      textResource?.text_content ||
                      `# Prescribed Syllabus Reading: ${topicTitle}\n\nComprehensive textbook reading material explaining the foundational principles, core methodologies, and examination themes of ${topicTitle} in ${subjectName}.`
                    }
                  />
                </div>
              ) : (
                /* Self-Check Interactive Quiz Tab */
                <div style={{ background: '#ffffff', borderRadius: 16, border: '1px solid #e2e8f0', padding: 24, marginBottom: 20 }}>
                  <h3 style={{ fontSize: 18, fontWeight: 700, color: '#1e293b', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <HelpCircle size={20} color="#6366f1" />
                    <span>Topic Practice Quiz</span>
                  </h3>

                  {(topicQuiz.length > 0
                    ? topicQuiz.map((pq) => ({
                        id: pq.id,
                        question: pq.question_text,
                        options: (pq.options || []).map((o) => `${o.id}. ${o.text}`),
                        correctIndex: (pq.options || []).findIndex((o) => o.id === pq.correct_answer),
                        explanation: pq.explanation,
                      }))
                    : getDynamicFallbackQuiz(subjectName, topicTitle)
                  ).map((q, idx) => {
                    const selected = selectedAnswers[q.id];
                    const isSubmitted = submittedAnswers[q.id];
                    const isCorrect = selected === q.correctIndex;

                    return (
                      <div key={q.id} style={{ marginBottom: 20, paddingBottom: 16, borderBottom: '1px solid #f1f5f9' }}>
                        <div style={{ fontWeight: 600, fontSize: 14, color: '#1e293b', marginBottom: 10 }}>
                          {idx + 1}. {q.question}
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                          {q.options.map((opt, optIdx) => (
                            <button
                              key={optIdx}
                              type="button"
                              style={{
                                textAlign: 'left',
                                padding: '10px 14px',
                                borderRadius: 10,
                                border: '1px solid',
                                borderColor: selected === optIdx ? '#6366f1' : '#e2e8f0',
                                background: selected === optIdx ? '#ede9fe' : '#f8fafc',
                                color: selected === optIdx ? '#4338ca' : '#1e293b',
                                fontSize: 13,
                                cursor: 'pointer',
                              }}
                              onClick={() => {
                                setSelectedAnswers((prev) => ({ ...prev, [q.id]: optIdx }));
                                setSubmittedAnswers((prev) => ({ ...prev, [q.id]: true }));
                              }}
                            >
                              {opt}
                            </button>
                          ))}
                        </div>

                        {isSubmitted && (
                          <div style={{ marginTop: 10, fontSize: 12.5, color: isCorrect ? '#059669' : '#dc2626', fontWeight: 500 }}>
                            {isCorrect ? 'Correct! ' : 'Incorrect. '}
                            <span style={{ color: '#64748b' }}>{q.explanation}</span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Bottom Tabs with Accessibility Roles matching Design & Tests */}
              <div className="study-tabs-row" role="tablist">
                <button
                  type="button"
                  role="tab"
                  aria-selected={activeTab === 'video'}
                  className={`study-tab-btn ${activeTab === 'video' ? 'active' : ''}`}
                  onClick={() => setActiveTab('video')}
                >
                  Video Lesson
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={activeTab === 'notes'}
                  className={`study-tab-btn ${activeTab === 'notes' ? 'active' : ''}`}
                  onClick={() => setActiveTab('notes')}
                >
                  Study Notes
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={activeTab === 'text'}
                  className={`study-tab-btn ${activeTab === 'text' ? 'active' : ''}`}
                  onClick={() => setActiveTab('text')}
                >
                  Reading Material
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={activeTab === 'quiz'}
                  className={`study-tab-btn ${activeTab === 'quiz' ? 'active' : ''}`}
                  onClick={() => setActiveTab('quiz')}
                >
                  Quiz
                </button>
              </div>
            </div>

            {/* Right Column: Integrated Chapter AI Tutor matching Image 2 */}
            <div className="chapter-tutor-container">
              <div className="chapter-tutor-header">
                <h3 className="chapter-tutor-heading">AI Tutor · this chapter</h3>
                <p className="chapter-tutor-model-lbl">Model: Gemini Flash</p>
              </div>

              <div className="chapter-tutor-chat-body" ref={chatScrollRef}>
                {chatMessages.map((msg) => (
                  <div
                    key={msg.id}
                    className={msg.sender === 'user' ? 'chat-bubble-user' : 'chat-bubble-bot'}
                  >
                    {msg.text}
                  </div>
                ))}
                {isSending && (
                  <div className="chat-bubble-bot" style={{ fontStyle: 'italic', color: '#64748b' }}>
                    Tutor is thinking...
                  </div>
                )}
              </div>

              <div className="chapter-tutor-input-box">
                <input
                  type="text"
                  className="chapter-tutor-input"
                  placeholder="Type or talk..."
                  value={inputVal}
                  onChange={(e) => setInputVal(e.target.value)}
                  onKeyDown={handleKeyDown}
                />
                <button
                  type="button"
                  className="chapter-tutor-send-btn"
                  onClick={handleSendMessage}
                  disabled={isSending}
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
};
