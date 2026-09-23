import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import {
  Bot,
  Send,
  Image as ImageIcon,
  X,
  AlertCircle,
  Mic,
} from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { MarkdownRenderer } from '../components/learning/MarkdownRenderer';
import { askAITutor } from '../services/tutor';
import { fetchEnrolledSubjects, fetchSubjectDetail } from '../services/learning';
import type { TutorChatMessage } from '../types/tutor';

interface TopicOption {
  id: number;
  title: string;
  chapterTitle: string;
  subjectName: string;
  board?: string;
  grade?: string;
}

export const AITutorPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialTopicParam = searchParams.get('topicId');

  const [topics, setTopics] = useState<TopicOption[]>([]);
  const [activeTopicId, setActiveTopicId] = useState<number | null>(
    initialTopicParam ? Number(initialTopicParam) : null
  );
  const [catalogLoading, setCatalogLoading] = useState<boolean>(true);

  const [messages, setMessages] = useState<TutorChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [chatError, setChatError] = useState<string | null>(null);

  useEffect(() => {
    async function loadCurriculumTopics() {
      try {
        setCatalogLoading(true);
        const subjects = await fetchEnrolledSubjects();
        const availableTopics: TopicOption[] = [];
        for (const s of subjects) {
          try {
            const detail = await fetchSubjectDetail(s.id);
            for (const ch of detail.chapters || []) {
              for (const top of ch.topics || []) {
                availableTopics.push({
                  id: top.id,
                  title: top.title,
                  chapterTitle: ch.title,
                  subjectName: s.name,
                  board: s.board,
                  grade: s.grade,
                });
              }
            }
          } catch {
            // continue
          }
        }
        setTopics(availableTopics);
        if (availableTopics.length > 0) {
          if (!initialTopicParam) {
            setActiveTopicId(availableTopics[0].id);
          }
        } else {
          setActiveTopicId(null);
        }
      } catch {
        // fallback
      } finally {
        setCatalogLoading(false);
      }
    }
    loadCurriculumTopics();
  }, [initialTopicParam]);

  const activeTopic = topics.find((t) => t.id === activeTopicId);

  // Initialize or update welcome message whenever activeTopic changes
  useEffect(() => {
    if (activeTopic) {
      setMessages([
        {
          id: `welcome-${activeTopic.id}`,
          role: 'tutor',
          content: `Hello! I am your **Curriculum-Aware AI Tutor** for **${activeTopic.subjectName}** (${activeTopic.board || ''}${activeTopic.grade ? ` Class ${activeTopic.grade}` : ''}).\n\nI am grounded in official syllabus guidelines and learning materials for **${activeTopic.chapterTitle}** • **${activeTopic.title}**.\n\nYou can:\n- Ask conceptual doubts or syllabus questions.\n- Upload photos of diagrams, formulas, or homework exercises.\n- Request high-yield takeaways, step-by-step explanations, or revision summaries.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } else if (!catalogLoading && topics.length === 0) {
      setMessages([
        {
          id: 'welcome-general',
          role: 'tutor',
          content: `Hello! I am your **SmartLearn AI Academic Assistant**.\n\nYour enrolled subjects are currently in preparation. You can ask general academic planning and study methodology questions, but specific syllabus-grounded tutoring requires an active curriculum topic.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    }
  }, [activeTopicId, topics.length, catalogLoading]);

  const starterPrompts = activeTopic
    ? [
        `Explain the core concepts in "${activeTopic.title}" in simple terms`,
        `What are the most important takeaways from ${activeTopic.chapterTitle}?`,
        `How should I approach high-yield exam questions on this topic?`,
        `Summarize key definitions and terms for ${activeTopic.title}`,
      ]
    : [
        'What is an effective daily study routine for board exams?',
        'How can I structure long-form analytical answers effectively?',
        'How do I create concise revision sheets for my subjects?',
        'Give me tips on time management during board examinations',
      ];

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setChatError('Please select a valid image file (PNG, JPEG, or WEBP).');
      return;
    }

    setChatError(null);
    const reader = new FileReader();
    reader.onload = () => {
      setSelectedImage(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || inputMessage).trim();
    if (!query && !selectedImage) return;
    if (isLoading) return;

    if (!activeTopicId) {
      setChatError('Please select a valid curriculum topic to enable grounded AI tutoring.');
      return;
    }

    setChatError(null);
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const currentImg = selectedImage;

    const studentMsg: TutorChatMessage = {
      id: `student-${Date.now()}`,
      role: 'student',
      content: query || 'Analyze attached doubt diagram',
      imageUrl: currentImg || undefined,
      timestamp,
    };

    const nextHistory = [...messages, studentMsg];
    setMessages(nextHistory);
    setInputMessage('');
    setSelectedImage(null);
    setIsLoading(true);

    try {
      const res = await askAITutor({
        topic_id: activeTopicId,
        message: query || 'Please analyze this diagram or problem from the syllabus.',
        image_base64: currentImg || undefined,
        conversation_history: nextHistory.slice(-6).map((m) => ({
          role: m.role,
          content: m.content,
        })),
      });

      setMessages((prev) => [
        ...prev,
        {
          id: `tutor-${Date.now()}`,
          role: 'tutor',
          content: res.reply,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (err: any) {
      const msg = err.message || 'Failed to get tutor response.';
      if (msg.includes('429') || msg.toLowerCase().includes('quota')) {
        setChatError('AI Tutor quota or rate limit reached on provider tier. Please wait a moment before sending another message.');
      } else if (msg.includes('503') || msg.toLowerCase().includes('high demand')) {
        setChatError('AI Tutor provider is temporarily experiencing high demand. Please try again shortly.');
      } else {
        setChatError(msg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppLayout breadcrumbs={[{ label: 'AI Tutor' }]}>
      <div className="tutor-page-container">
        {/* Tutor Header Info Bar */}
        <div className="tutor-page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div className="tutor-header-left">
            <div className="tutor-page-icon">
              <Bot size={22} />
            </div>
            <div>
              <div className="tutor-title-row">
                <h1 className="tutor-page-title">Curriculum AI Tutor</h1>
                <span className="tutor-badge">
                  {activeTopic ? `Grounded in ${activeTopic.board || 'Official'} Curriculum` : 'General Assistance'}
                </span>
              </div>
              <p className="tutor-page-subtitle">
                {activeTopic ? (
                  <>Context: {activeTopic.subjectName} • {activeTopic.chapterTitle} • {activeTopic.title}</>
                ) : (
                  <>Context: No curriculum topic selected</>
                )}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {topics.length > 0 && (
              <select
                aria-label="Select Syllabus Topic"
                value={activeTopicId || ''}
                onChange={(e) => {
                  const newId = Number(e.target.value);
                  setActiveTopicId(newId);
                  setSearchParams({ topicId: String(newId) });
                }}
                className="filter-pill"
                style={{ background: '#fff', border: '1px solid #cbd5e1', padding: '6px 12px', fontSize: '13px', borderRadius: '8px', color: '#1e293b' }}
              >
                {topics.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.subjectName} • {t.title}
                  </option>
                ))}
              </select>
            )}

            {activeTopicId && (
              <Link
                to={`/learning/topics/${activeTopicId}`}
                className="filter-pill"
                style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: '#eef2ff', color: '#4f46e5', textDecoration: 'none', border: '1px solid #c7d2fe', padding: '6px 12px', fontSize: '13px' }}
                title="Practice with interactive spoken voice via browser Web Speech API"
              >
                <Mic size={14} />
                <span>Voice Tutor (Browser STT/TTS)</span>
              </Link>
            )}
          </div>
        </div>

        {/* Chat Thread Container */}
        <div className="tutor-page-chat-card">
          {chatError && (
            <div className="tutor-error-banner" role="alert">
              <AlertCircle size={16} className="text-amber-600" />
              <div style={{ flex: 1 }}>{chatError}</div>
              <button
                type="button"
                onClick={() => setChatError(null)}
                className="error-dismiss-btn"
                aria-label="Dismiss error"
              >
                <X size={14} />
              </button>
            </div>
          )}

          <div className="tutor-page-messages" role="log" aria-live="polite">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`tutor-bubble-row ${msg.role === 'student' ? 'student-row' : 'tutor-row'}`}
              >
                {msg.role === 'tutor' && (
                  <div className="tutor-bubble-avatar">
                    <Bot size={16} />
                  </div>
                )}
                <div
                  className={`tutor-bubble ${msg.role === 'student' ? 'student-bubble' : 'tutor-bubble-content'}`}
                >
                  {msg.imageUrl && (
                    <div className="tutor-msg-image-wrap">
                      <img src={msg.imageUrl} alt="Student attached doubt" className="tutor-msg-image" />
                    </div>
                  )}
                  {msg.role === 'tutor' ? (
                    <MarkdownRenderer content={msg.content} />
                  ) : (
                    <div className="tutor-student-text">{msg.content}</div>
                  )}
                  <div className="tutor-msg-time">{msg.timestamp}</div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="tutor-bubble-row tutor-row">
                <div className="tutor-bubble-avatar">
                  <Bot size={16} />
                </div>
                <div className="tutor-bubble tutor-bubble-content loading-bubble">
                  <div className="tutor-typing-indicator">
                    <span />
                    <span />
                    <span />
                  </div>
                  <span style={{ fontSize: '13px', color: '#64748b', marginLeft: '8px' }}>
                    Consulting {activeTopic?.board || 'curriculum'} learning resources...
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Starter Prompts */}
          {messages.length <= 3 && !isLoading && (
            <div className="tutor-starter-chips">
              <span className="starter-label">Suggested Doubts &amp; Takeaways:</span>
              {starterPrompts.map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  className="tutor-chip"
                  onClick={() => handleSend(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>
          )}

          {/* Input Bar */}
          <div className="tutor-page-input-box">
            {selectedImage && (
              <div className="tutor-image-preview">
                <img src={selectedImage} alt="Attachment preview" />
                <button
                  type="button"
                  className="tutor-remove-img-btn"
                  onClick={() => setSelectedImage(null)}
                >
                  <X size={12} />
                </button>
              </div>
            )}

            <div className="tutor-input-row">
              <input
                type="file"
                id="page-file-upload"
                accept="image/png, image/jpeg, image/webp"
                style={{ display: 'none' }}
                onChange={handleImageSelect}
              />
              <label htmlFor="page-file-upload" className="tutor-attach-btn" title="Upload diagram or problem photo">
                <ImageIcon size={18} />
              </label>

              <textarea
                className="tutor-textarea"
                placeholder="Ask any doubt or request a concept explanation..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                rows={1}
              />

              <button
                type="button"
                className="tutor-send-btn"
                onClick={() => handleSend()}
                disabled={(!inputMessage.trim() && !selectedImage) || isLoading}
                aria-label="Send query to AI Tutor"
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};
