import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  CheckCircle,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Sparkles,
  ShieldCheck,
  Send,
  Loader2,
  Flame,
  Zap,
  RotateCcw,
  BookOpen,
} from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import {
  fetchTopicPYQs,
  fetchPracticeQuestions,
  generatePracticeQuestions,
  submitPracticeAttempt,
  fetchEnrolledSubjects,
  fetchSubjectDetail,
  fetchRewardsSummary,
} from '../services/learning';
import type { PreviousYearQuestion, PracticeQuestion, PracticeAttemptResponse } from '../types/learning';

interface TopicOption {
  id: number;
  title: string;
  chapterTitle: string;
  subjectName: string;
}

interface RewardStats {
  xp_points: number;
  streak_days: number;
  badges: string[];
  level: number;
  next_level_xp: number;
  level_progress: number;
}

export const PracticeQuizzesPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialTopicParam = searchParams.get('topicId');

  const [activeTab, setActiveTab] = useState<'pyqs' | 'practice'>('pyqs');
  const [topics, setTopics] = useState<TopicOption[]>([]);
  const [topicId, setTopicId] = useState<number>(
    initialTopicParam ? Number(initialTopicParam) : 1
  );

  // Authentic PYQs State
  const [pyqs, setPyqs] = useState<PreviousYearQuestion[]>([]);
  const [pyqsLoading, setPyqsLoading] = useState<boolean>(true);
  const [expandedSchemes, setExpandedSchemes] = useState<Record<number, boolean>>({});

  // Practice State
  const [practiceQuestions, setPracticeQuestions] = useState<PracticeQuestion[]>([]);
  const [practiceLoading, setPracticeLoading] = useState<boolean>(true);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [attemptResults, setAttemptResults] = useState<Record<number, PracticeAttemptResponse>>({});
  const [submittingIds, setSubmittingIds] = useState<Record<number, boolean>>({});
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');

  // Rewards State
  const [rewards, setRewards] = useState<RewardStats>({
    xp_points: 0,
    streak_days: 1,
    badges: ['New Explorer'],
    level: 1,
    next_level_xp: 50,
    level_progress: 0,
  });

  const [celebrationToast, setCelebrationToast] = useState<{
    show: boolean;
    xp: number;
    badge?: string | null;
  }>({ show: false, xp: 0 });

  useEffect(() => {
    async function loadCurriculumTopics() {
      try {
        const subjects = await fetchEnrolledSubjects();
        const availableTopics: TopicOption[] = [];
        for (const s of subjects) {
          try {
            const detail = await fetchSubjectDetail(s.id);
            for (const ch of detail.chapters) {
              for (const top of ch.topics) {
                availableTopics.push({
                  id: top.id,
                  title: top.title,
                  chapterTitle: ch.title,
                  subjectName: s.name,
                });
              }
            }
          } catch {
            // continue
          }
        }
        if (availableTopics.length > 0) {
          setTopics(availableTopics);
          if (!initialTopicParam) {
            setTopicId(availableTopics[0].id);
          }
        }
      } catch {
        // fallback
      }
    }
    loadCurriculumTopics();
    loadRewards();
  }, [initialTopicParam]);

  const loadRewards = async () => {
    try {
      const stats = await fetchRewardsSummary();
      setRewards(stats);
    } catch {
      // quiet fallback
    }
  };

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
      const data = await fetchPracticeQuestions(
        topicId,
        selectedDifficulty === 'all' ? undefined : selectedDifficulty
      );
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
    if (attemptResults[questionId]) return;
    setSelectedAnswers((prev) => ({ ...prev, [questionId]: optionId }));
  };

  const handleSubmitAttempt = async (questionId: number) => {
    const answer = selectedAnswers[questionId];
    if (!answer) return;

    try {
      setSubmittingIds((prev) => ({ ...prev, [questionId]: true }));
      const result: PracticeAttemptResponse = await submitPracticeAttempt(questionId, answer);
      setAttemptResults((prev) => ({ ...prev, [questionId]: result }));

      if (result.xp_earned) {
        setRewards((prev) => {
          const newXp = (prev.xp_points || 0) + result.xp_earned!;
          return {
            ...prev,
            xp_points: newXp,
            streak_days: result.streak_days || prev.streak_days,
            level: Math.floor(newXp / 50) + 1,
            next_level_xp: (Math.floor(newXp / 50) + 1) * 50,
            level_progress: (newXp % 50) * 2,
            badges: result.badge_unlocked
              ? Array.from(new Set([...prev.badges, result.badge_unlocked]))
              : prev.badges,
          };
        });

        setCelebrationToast({
          show: true,
          xp: result.xp_earned,
          badge: result.badge_unlocked,
        });

        setTimeout(() => {
          setCelebrationToast({ show: false, xp: 0 });
        }, 4000);
      }
    } catch (err) {
      console.error('Failed to submit attempt:', err);
    } finally {
      setSubmittingIds((prev) => ({ ...prev, [questionId]: false }));
    }
  };

  const handleGenerateFreshQuestions = async () => {
    try {
      setIsGenerating(true);
      const freshQuestions = await generatePracticeQuestions(
        topicId,
        selectedDifficulty === 'all' ? undefined : selectedDifficulty
      );
      setPracticeQuestions(freshQuestions);
      setSelectedAnswers({});
      setAttemptResults({});
    } catch (err) {
      console.error('Failed to generate fresh questions:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const attemptedCount = Object.keys(attemptResults).length;
  const correctCount = Object.values(attemptResults).filter((r) => r.is_correct).length;
  const currentTopic = topics.find((t) => t.id === topicId);

  return (
    <AppLayout breadcrumbs={[{ label: 'Practice & Quizzes' }]}>
      {/* ── Page Header ────────────────────────────────────────────── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <h1 style={{ fontSize: 24, fontWeight: 800, color: '#1e1b4b', margin: 0 }}>
              Practice &amp; Assessment Hub
            </h1>
            {currentTopic && (
              <span
                style={{
                  background: '#ede9fe',
                  color: '#6366f1',
                  fontSize: 12,
                  fontWeight: 700,
                  padding: '3px 10px',
                  borderRadius: 20,
                }}
              >
                {currentTopic.subjectName}
              </span>
            )}
          </div>
          <p style={{ fontSize: 14, color: '#64748b', marginTop: 4, margin: '4px 0 0 0' }}>
            Official past board examination questions and curriculum-grounded AI practice tests aligned with CBSE &amp; CISCE guidelines.
          </p>
        </div>

        {/* Header Right Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
          {/* Topic Selector */}
          {topics.length > 0 && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                background: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: 12,
                padding: '6px 12px',
                boxShadow: '0 1px 2px rgba(0,0,0,0.03)',
              }}
            >
              <BookOpen size={15} style={{ color: '#64748b' }} />
              <select
                aria-label="Select Syllabus Topic"
                value={topicId}
                onChange={(e) => {
                  const newId = Number(e.target.value);
                  setTopicId(newId);
                  setSearchParams({ topicId: String(newId) });
                  setSelectedAnswers({});
                  setAttemptResults({});
                }}
                style={{
                  border: 'none',
                  background: 'transparent',
                  color: '#1e293b',
                  fontSize: 13,
                  fontWeight: 600,
                  outline: 'none',
                  cursor: 'pointer',
                  maxWidth: 240,
                }}
              >
                {topics.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.subjectName}: {t.title}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Difficulty Dropdown */}
          {activeTab === 'practice' && (
            <select
              aria-label="Filter Difficulty"
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              style={{
                background: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: 12,
                padding: '7px 14px',
                fontSize: 13,
                fontWeight: 600,
                color: '#475569',
                outline: 'none',
                cursor: 'pointer',
              }}
            >
              <option value="all">All Difficulties</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          )}

          {/* Generate More Button */}
          {activeTab === 'practice' && (
            <button
              type="button"
              onClick={handleGenerateFreshQuestions}
              disabled={isGenerating}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                background: '#4f46e5',
                color: '#ffffff',
                border: 'none',
                borderRadius: 12,
                padding: '8px 16px',
                fontSize: 13,
                fontWeight: 700,
                cursor: isGenerating ? 'not-allowed' : 'pointer',
                opacity: isGenerating ? 0.6 : 1,
                boxShadow: '0 2px 4px rgba(79,70,229,0.2)',
                transition: 'background 0.2s',
              }}
            >
              {isGenerating ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
              <span>{isGenerating ? 'Synthesizing...' : 'Generate 3 More'}</span>
            </button>
          )}
        </div>
      </div>

      {/* ── 4 Top KPI Metric Cards (Matching Screenshot 1 & 2 Style) ────────────── */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 16,
          marginBottom: 24,
        }}
      >
        {/* Card 1: Level & Streak */}
        <div style={{ background: '#ffffff', borderRadius: 16, padding: '20px 24px', border: '1px solid #f1f5f9' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
            <span style={{ fontSize: 24, fontWeight: 800, color: '#4f46e5', lineHeight: 1 }}>Level {rewards.level}</span>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 4,
                background: '#fef3c7',
                color: '#92400e',
                fontSize: 11,
                fontWeight: 700,
                padding: '2px 8px',
                borderRadius: 12,
              }}
            >
              <Flame size={12} color="#f59e0b" fill="#f59e0b" /> {rewards.streak_days}-Day Streak
            </span>
          </div>
          <div style={{ fontSize: 13, color: '#64748b', fontWeight: 500 }}>Academic Rank</div>
          <div style={{ width: '100%', height: 4, background: '#f1f5f9', borderRadius: 4, marginTop: 10, overflow: 'hidden' }}>
            <div style={{ width: `${Math.min(100, rewards.level_progress)}%`, height: '100%', background: '#4f46e5', borderRadius: 4 }} />
          </div>
        </div>

        {/* Card 2: Total XP Earned */}
        <div style={{ background: '#ffffff', borderRadius: 16, padding: '20px 24px', border: '1px solid #f1f5f9' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 24, fontWeight: 800, color: '#0f172a', lineHeight: 1 }}>
            <Zap size={20} color="#f59e0b" fill="#f59e0b" />
            <span>{rewards.xp_points} XP</span>
          </div>
          <div style={{ fontSize: 13, color: '#64748b', fontWeight: 500, marginTop: 4 }}>
            {rewards.next_level_xp - rewards.xp_points} XP to Level {rewards.level + 1}
          </div>
          <div style={{ fontSize: 11, color: '#10b981', fontWeight: 600, marginTop: 6 }}>
            +15 XP per correct answer
          </div>
        </div>

        {/* Card 3: Active Unit Questions */}
        <div style={{ background: '#ffffff', borderRadius: 16, padding: '20px 24px', border: '1px solid #f1f5f9' }}>
          <div style={{ fontSize: 24, fontWeight: 800, color: '#0f172a', lineHeight: 1 }}>
            {pyqs.length + practiceQuestions.length}
          </div>
          <div style={{ fontSize: 13, color: '#64748b', fontWeight: 500, marginTop: 4 }}>Total Questions in Unit</div>
          <div style={{ fontSize: 11, color: '#6366f1', fontWeight: 600, marginTop: 6 }}>
            {pyqs.length} Official PYQs • {practiceQuestions.length} Practice
          </div>
        </div>

        {/* Card 4: Session Accuracy */}
        <div style={{ background: '#ffffff', borderRadius: 16, padding: '20px 24px', border: '1px solid #f1f5f9' }}>
          <div style={{ fontSize: 24, fontWeight: 800, color: attemptedCount > 0 ? '#10b981' : '#64748b', lineHeight: 1 }}>
            {attemptedCount > 0 ? `${Math.round((correctCount / attemptedCount) * 100)}%` : 'Ready'}
          </div>
          <div style={{ fontSize: 13, color: '#64748b', fontWeight: 500, marginTop: 4 }}>Quiz Accuracy</div>
          <div style={{ fontSize: 11, color: '#64748b', fontWeight: 500, marginTop: 6 }}>
            {attemptedCount > 0 ? `${correctCount} of ${attemptedCount} answered correctly` : 'Pick a question below to start'}
          </div>
        </div>
      </div>

      {/* Floating Celebration Toast */}
      {celebrationToast.show && (
        <div
          style={{
            position: 'fixed',
            top: 24,
            right: 24,
            zIndex: 100,
            background: '#10b981',
            color: '#ffffff',
            padding: '12px 20px',
            borderRadius: 14,
            boxShadow: '0 10px 25px -5px rgba(16, 185, 129, 0.4)',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            fontWeight: 600,
            fontSize: 14,
          }}
        >
          <Zap size={20} color="#fef08a" fill="#fef08a" />
          <div>
            <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.5, color: '#d1fae5', fontWeight: 800 }}>
              Reward Unlocked!
            </div>
            <div>
              +{celebrationToast.xp} XP Earned! {celebrationToast.badge ? `🎖️ ${celebrationToast.badge} Unlocked!` : 'Keep going!'}
            </div>
          </div>
        </div>
      )}

      {/* ── Segmented Tab Selector (Matching Screenshot 1 Filter Pills) ────────────── */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 6, background: '#f1f5f9', padding: 4, borderRadius: 12 }}>
          <button
            type="button"
            onClick={() => setActiveTab('pyqs')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              background: activeTab === 'pyqs' ? '#4f46e5' : 'transparent',
              color: activeTab === 'pyqs' ? '#ffffff' : '#64748b',
              border: 'none',
              borderRadius: 8,
              padding: '8px 18px',
              fontWeight: 700,
              fontSize: 13,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <ShieldCheck size={16} />
            <span>Authentic Board PYQs</span>
            <span
              style={{
                fontSize: 11,
                padding: '1px 7px',
                borderRadius: 10,
                background: activeTab === 'pyqs' ? 'rgba(255,255,255,0.2)' : '#e2e8f0',
                color: activeTab === 'pyqs' ? '#ffffff' : '#475569',
                fontWeight: 700,
              }}
            >
              {pyqs.length} Official
            </span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('practice')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              background: activeTab === 'practice' ? '#4f46e5' : 'transparent',
              color: activeTab === 'practice' ? '#ffffff' : '#64748b',
              border: 'none',
              borderRadius: 8,
              padding: '8px 18px',
              fontWeight: 700,
              fontSize: 13,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <Sparkles size={16} />
            <span>Curriculum Practice &amp; Quizzes</span>
            <span
              style={{
                fontSize: 11,
                padding: '1px 7px',
                borderRadius: 10,
                background: activeTab === 'practice' ? 'rgba(255,255,255,0.2)' : '#e2e8f0',
                color: activeTab === 'practice' ? '#ffffff' : '#475569',
                fontWeight: 700,
              }}
            >
              {practiceQuestions.length} Questions
            </span>
          </button>
        </div>

        {/* Session reset button */}
        {activeTab === 'practice' && attemptedCount > 0 && (
          <button
            type="button"
            onClick={() => {
              setSelectedAnswers({});
              setAttemptResults({});
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: 'transparent',
              border: '1px solid #e2e8f0',
              borderRadius: 8,
              padding: '6px 12px',
              fontSize: 12,
              fontWeight: 600,
              color: '#64748b',
              cursor: 'pointer',
            }}
          >
            <RotateCcw size={13} />
            <span>Reset Attempt ({correctCount}/{attemptedCount})</span>
          </button>
        )}
      </div>

      {/* ── TAB 1: Authentic Previous-Year Questions ────────────────────── */}
      {activeTab === 'pyqs' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div
            style={{
              background: '#ecfdf5',
              border: '1px solid #a7f3d0',
              borderRadius: 14,
              padding: '14px 18px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: 13,
              color: '#065f46',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <ShieldCheck size={18} color="#059669" />
              <span>
                These questions are authentic past-year board examination questions with official CISCE / CBSE paper attribution and exact marking schemes.
              </span>
            </div>
            <a
              href="https://www.cisce.org/regulations-and-syllabuses-isc/"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 4,
                color: '#047857',
                fontWeight: 700,
                fontSize: 12,
                textDecoration: 'none',
                whiteSpace: 'nowrap',
                marginLeft: 16,
              }}
            >
              <span>Board Guidelines</span>
              <ExternalLink size={12} />
            </a>
          </div>

          {pyqsLoading ? (
            <div style={{ padding: 48, textAlign: 'center', color: '#64748b', fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
              <Loader2 size={18} className="animate-spin" color="#4f46e5" />
              <span>Loading authentic previous-year questions...</span>
            </div>
          ) : pyqs.length === 0 ? (
            <div
              style={{
                background: '#ffffff',
                border: '1px solid #f1f5f9',
                borderRadius: 16,
                padding: '48px 24px',
                textAlign: 'center',
              }}
            >
              <ShieldCheck size={36} color="#94a3b8" style={{ margin: '0 auto 12px auto' }} />
              <div style={{ fontSize: 16, fontWeight: 700, color: '#1e293b', marginBottom: 4 }}>
                No Verified Authentic PYQs For This Topic Yet
              </div>
              <p style={{ fontSize: 13, color: '#64748b', maxWidth: 460, margin: '0 auto 16px auto', lineHeight: 1.5 }}>
                Select another topic from the dropdown above (e.g. <em>The Delhi Sultanate</em> or <em>Insolation &amp; Heat Budget</em>), or test yourself on the <strong>Curriculum Practice &amp; Quizzes</strong> tab.
              </p>
              <button
                type="button"
                onClick={() => setActiveTab('practice')}
                style={{
                  background: '#4f46e5',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: 10,
                  padding: '8px 18px',
                  fontWeight: 700,
                  fontSize: 13,
                  cursor: 'pointer',
                }}
              >
                Go to Practice Questions
              </button>
            </div>
          ) : (
            pyqs.map((q) => {
              const isExpanded = expandedSchemes[q.id];

              return (
                <div
                  key={q.id}
                  style={{
                    background: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: 16,
                    padding: 24,
                    boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                    transition: 'border-color 0.15s ease',
                  }}
                >
                  {/* Question Meta Header */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, flexWrap: 'wrap', gap: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span
                        style={{
                          background: '#ede9fe',
                          color: '#4338ca',
                          fontSize: 12,
                          fontWeight: 700,
                          padding: '3px 10px',
                          borderRadius: 8,
                        }}
                      >
                        {q.board} {q.exam_year}
                      </span>
                      <span
                        style={{
                          background: '#f1f5f9',
                          color: '#475569',
                          fontSize: 12,
                          fontFamily: 'monospace',
                          fontWeight: 600,
                          padding: '3px 10px',
                          borderRadius: 8,
                        }}
                      >
                        {q.paper_code}
                      </span>
                      <span
                        style={{
                          background: '#f8fafc',
                          color: '#334155',
                          fontSize: 12,
                          fontWeight: 600,
                          padding: '3px 10px',
                          borderRadius: 8,
                          border: '1px solid #e2e8f0',
                        }}
                      >
                        Q{q.question_number}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span
                        style={{
                          background: '#fef3c7',
                          color: '#92400e',
                          fontSize: 12,
                          fontWeight: 700,
                          padding: '3px 10px',
                          borderRadius: 20,
                        }}
                      >
                        {q.marks} {q.marks === 1 ? 'Mark' : 'Marks'}
                      </span>
                      <span
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 4,
                          color: '#059669',
                          fontSize: 12,
                          fontWeight: 600,
                        }}
                      >
                        <CheckCircle size={14} /> Verified Official
                      </span>
                    </div>
                  </div>

                  {/* Question Prompt */}
                  <div style={{ fontSize: 15, fontWeight: 600, color: '#0f172a', lineHeight: 1.6, marginBottom: 16 }}>
                    {q.question_text}
                  </div>

                  {/* Source & Marking Scheme Accordion */}
                  <div
                    style={{
                      borderTop: '1px solid #f1f5f9',
                      paddingTop: 14,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: 12,
                    }}
                  >
                    <span style={{ color: '#64748b' }}>
                      Exam Source: <strong style={{ color: '#334155', fontWeight: 600 }}>{q.source_name}</strong>
                    </span>
                    {q.marking_scheme && (
                      <button
                        type="button"
                        onClick={() => toggleMarkingScheme(q.id)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 4,
                          background: 'transparent',
                          border: 'none',
                          color: '#4f46e5',
                          fontWeight: 700,
                          fontSize: 12,
                          cursor: 'pointer',
                          padding: 0,
                        }}
                      >
                        <span>{isExpanded ? 'Hide Official Marking Scheme' : 'View Official Marking Scheme'}</span>
                        {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                      </button>
                    )}
                  </div>

                  {isExpanded && q.marking_scheme && (
                    <div
                      style={{
                        marginTop: 14,
                        background: '#f8fafc',
                        border: '1px solid #e2e8f0',
                        borderRadius: 12,
                        padding: 16,
                        fontSize: 13,
                        lineHeight: 1.6,
                        color: '#334155',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 6,
                          fontWeight: 700,
                          color: '#1e1b4b',
                          marginBottom: 8,
                          fontSize: 12,
                        }}
                      >
                        <CheckCircle size={14} color="#4f46e5" />
                        <span>Official Board Marking Scheme &amp; Key Answer Points:</span>
                      </div>
                      <p style={{ margin: 0, whiteSpace: 'pre-line' }}>{q.marking_scheme}</p>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}

      {/* ── TAB 2: AI-Generated Practice Questions & Quizzes ────────────── */}
      {activeTab === 'practice' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div
            style={{
              background: '#eef2ff',
              border: '1px solid #c7d2fe',
              borderRadius: 14,
              padding: '14px 18px',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: 13,
              color: '#3730a3',
            }}
          >
            <Sparkles size={18} color="#4f46e5" style={{ flexShrink: 0 }} />
            <span>
              Practice questions are synthesized from authentic curriculum objectives. Complete questions to earn <strong>XP points</strong>, unlock badges, and build your study streak!
            </span>
          </div>

          {practiceLoading ? (
            <div style={{ padding: 48, textAlign: 'center', color: '#64748b', fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
              <Loader2 size={18} className="animate-spin" color="#4f46e5" />
              <span>Loading curriculum practice questions...</span>
            </div>
          ) : practiceQuestions.length === 0 ? (
            <div
              style={{
                background: '#ffffff',
                border: '1px solid #f1f5f9',
                borderRadius: 16,
                padding: '48px 24px',
                textAlign: 'center',
              }}
            >
              <Sparkles size={36} color="#818cf8" style={{ margin: '0 auto 12px auto' }} />
              <div style={{ fontSize: 16, fontWeight: 700, color: '#1e293b', marginBottom: 4 }}>
                No Practice Questions for this Topic Yet
              </div>
              <p style={{ fontSize: 13, color: '#64748b', maxWidth: 460, margin: '0 auto 16px auto', lineHeight: 1.5 }}>
                Click below to dynamically generate curriculum-grounded multiple choice practice questions.
              </p>
              <button
                type="button"
                onClick={handleGenerateFreshQuestions}
                disabled={isGenerating}
                style={{
                  background: '#4f46e5',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: 10,
                  padding: '10px 20px',
                  fontWeight: 700,
                  fontSize: 13,
                  cursor: isGenerating ? 'not-allowed' : 'pointer',
                }}
              >
                {isGenerating ? 'Synthesizing...' : 'Generate Practice Questions'}
              </button>
            </div>
          ) : (
            practiceQuestions.map((q, idx) => {
              const selected = selectedAnswers[q.id];
              const attempt = attemptResults[q.id];
              const isSubmitting = submittingIds[q.id];

              return (
                <div
                  key={q.id}
                  style={{
                    background: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: 16,
                    padding: 24,
                    boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                  }}
                >
                  {/* Meta Bar */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, flexWrap: 'wrap', gap: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span
                        style={{
                          background: '#ede9fe',
                          color: '#4338ca',
                          fontSize: 12,
                          fontWeight: 700,
                          padding: '3px 10px',
                          borderRadius: 8,
                        }}
                      >
                        Question {idx + 1}
                      </span>
                      <span
                        style={{
                          background: '#f1f5f9',
                          color: '#475569',
                          fontSize: 11,
                          fontWeight: 700,
                          padding: '3px 10px',
                          borderRadius: 8,
                          textTransform: 'uppercase',
                          letterSpacing: 0.5,
                        }}
                      >
                        Curriculum Aligned
                      </span>
                      <span
                        style={{
                          background: '#f8fafc',
                          color: '#64748b',
                          fontSize: 11,
                          fontWeight: 600,
                          padding: '3px 10px',
                          borderRadius: 8,
                          border: '1px solid #e2e8f0',
                          textTransform: 'capitalize',
                        }}
                      >
                        {q.difficulty}
                      </span>
                    </div>

                    <div>
                      {attempt ? (
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 4,
                            padding: '3px 12px',
                            borderRadius: 20,
                            fontSize: 12,
                            fontWeight: 700,
                            background: attempt.is_correct ? '#ecfdf5' : '#fff1f2',
                            color: attempt.is_correct ? '#065f46' : '#9f1239',
                            border: `1px solid ${attempt.is_correct ? '#a7f3d0' : '#fecdd3'}`,
                          }}
                        >
                          {attempt.is_correct ? (
                            <>
                              <CheckCircle size={14} color="#059669" /> Correct (+15 XP)
                            </>
                          ) : (
                            'Needs Review (+5 XP for effort)'
                          )}
                        </span>
                      ) : (
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 4,
                            background: '#fef3c7',
                            color: '#92400e',
                            fontSize: 11,
                            fontWeight: 700,
                            padding: '3px 10px',
                            borderRadius: 20,
                          }}
                        >
                          <Zap size={12} color="#f59e0b" fill="#f59e0b" /> +15 XP
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Question Text */}
                  <div style={{ fontSize: 15, fontWeight: 600, color: '#0f172a', lineHeight: 1.6, marginBottom: 16 }}>
                    {q.question_text}
                  </div>

                  {/* MCQ Options List */}
                  {q.options && (
                    <div style={{ display: 'grid', gap: 10, marginBottom: 16 }}>
                      {q.options.map((opt) => {
                        const isPicked = selected === opt.id;
                        let bg = '#ffffff';
                        let border = '#e2e8f0';
                        let textColor = '#334155';
                        let chipBg = '#f1f5f9';
                        let chipColor = '#475569';

                        if (isPicked) {
                          bg = '#eef2ff';
                          border = '#6366f1';
                          textColor = '#1e1b4b';
                          chipBg = '#4f46e5';
                          chipColor = '#ffffff';
                        }

                        if (attempt) {
                          if (opt.id === q.correct_answer) {
                            bg = '#ecfdf5';
                            border = '#10b981';
                            textColor = '#065f46';
                            chipBg = '#10b981';
                            chipColor = '#ffffff';
                          } else if (isPicked) {
                            bg = '#fff1f2';
                            border = '#f43f5e';
                            textColor = '#9f1239';
                            chipBg = '#f43f5e';
                            chipColor = '#ffffff';
                          }
                        }

                        return (
                          <button
                            key={opt.id}
                            type="button"
                            onClick={() => handleSelectOption(q.id, opt.id)}
                            disabled={!!attempt}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              textAlign: 'left',
                              gap: 12,
                              padding: '12px 16px',
                              background: bg,
                              border: `1.5px solid ${border}`,
                              borderRadius: 12,
                              cursor: attempt ? 'default' : 'pointer',
                              color: textColor,
                              fontSize: 14,
                              fontWeight: isPicked ? 600 : 500,
                              lineHeight: 1.5,
                              transition: 'all 0.15s ease',
                            }}
                          >
                            <span
                              style={{
                                width: 26,
                                height: 26,
                                borderRadius: 8,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontWeight: 700,
                                fontSize: 12,
                                background: chipBg,
                                color: chipColor,
                                flexShrink: 0,
                              }}
                            >
                              {opt.id}
                            </span>
                            <span>{opt.text}</span>
                          </button>
                        );
                      })}
                    </div>
                  )}

                  {/* Submit Attempt Footer */}
                  {!attempt && (
                    <div
                      style={{
                        borderTop: '1px solid #f1f5f9',
                        paddingTop: 14,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }}
                    >
                      <span style={{ fontSize: 12, color: '#64748b' }}>
                        {selected ? 'Option selected. Click Submit to verify answer.' : 'Select an answer option to submit.'}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleSubmitAttempt(q.id)}
                        disabled={!selected || isSubmitting}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 6,
                          background: '#4f46e5',
                          color: '#ffffff',
                          border: 'none',
                          borderRadius: 10,
                          padding: '8px 18px',
                          fontSize: 13,
                          fontWeight: 700,
                          cursor: (!selected || isSubmitting) ? 'not-allowed' : 'pointer',
                          opacity: (!selected || isSubmitting) ? 0.5 : 1,
                          boxShadow: '0 2px 4px rgba(79,70,229,0.2)',
                        }}
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

                  {/* Feedback Box */}
                  {attempt && (
                    <div
                      style={{
                        marginTop: 14,
                        background: attempt.is_correct ? '#ecfdf5' : '#fff1f2',
                        border: `1px solid ${attempt.is_correct ? '#a7f3d0' : '#fecdd3'}`,
                        borderRadius: 12,
                        padding: 16,
                        fontSize: 13,
                        lineHeight: 1.6,
                        color: attempt.is_correct ? '#065f46' : '#9f1239',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 6,
                          fontWeight: 700,
                          marginBottom: 6,
                          fontSize: 13,
                        }}
                      >
                        {attempt.is_correct ? (
                          <>
                            <CheckCircle size={15} color="#059669" />
                            <span>Correct Explanation:</span>
                          </>
                        ) : (
                          <span>💡 Learning Breakdown:</span>
                        )}
                      </div>
                      <p style={{ margin: 0 }}>{attempt.explanation}</p>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}
    </AppLayout>
  );
};
