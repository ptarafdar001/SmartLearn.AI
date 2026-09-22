import React, { useState } from 'react';
import {
  Bot,
  Send,
  Image as ImageIcon,
  X,
  AlertCircle,
} from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { MarkdownRenderer } from '../components/learning/MarkdownRenderer';
import { askAITutor } from '../services/tutor';
import type { TutorChatMessage } from '../types/tutor';

const STARTER_PROMPTS = [
  'Explain the 1853 Railway Guarantee System in simple terms',
  'What were Lord Dalhousie’s primary military and economic motives?',
  'How did railway tariffs contribute to Indian de-industrialisation?',
  'Generate 3 high-yield practice questions for my upcoming exam',
];

export const AITutorPage: React.FC = () => {
  const [messages, setMessages] = useState<TutorChatMessage[]>([
    {
      id: 'welcome',
      role: 'tutor',
      content: `Hello! I am your **Curriculum-Aware AI Tutor** for **ISC Class 11 History**.\n\nI am grounded in official CISCE syllabus guidelines and verified learning materials.\n\nYou can:\n- Ask any conceptual doubt or syllabus question.\n- Upload photos of textbook diagrams, maps, or homework exercises.\n- Request high-yield exam takeaways, step-by-step solutions, or revision summaries.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [chatError, setChatError] = useState<string | null>(null);

  const topicId = 44; // Default to Topic 1

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
        topic_id: topicId,
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
      setChatError(err.message || 'Failed to get tutor response.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppLayout breadcrumbs={[{ label: 'AI Tutor' }]}>
      <div className="tutor-page-container">
        {/* Tutor Header Info Bar */}
        <div className="tutor-page-header">
          <div className="tutor-header-left">
            <div className="tutor-page-icon">
              <Bot size={22} />
            </div>
            <div>
              <div className="tutor-title-row">
                <h1 className="tutor-page-title">Curriculum AI Tutor</h1>
                <span className="tutor-badge">Grounded in CISCE Syllabus</span>
              </div>
              <p className="tutor-page-subtitle">
                Context: History • Chapter 1: Emergence of the Colonial Economy • Transport &amp; Communication
              </p>
            </div>
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
                    Consulting CISCE curriculum resources...
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Starter Prompts */}
          {messages.length <= 3 && !isLoading && (
            <div className="tutor-starter-chips">
              <span className="starter-label">Suggested Syllabus Doubts:</span>
              {STARTER_PROMPTS.map((prompt, idx) => (
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
