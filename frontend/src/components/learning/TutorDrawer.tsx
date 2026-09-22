import React, { useEffect, useRef, useState } from 'react';
import { askAITutor } from '../../services/tutor';
import type { TutorChatMessage } from '../../types/tutor';

interface TutorDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  topicId: number;
  topicTitle: string;
  subjectName: string;
  chapterTitle: string;
  chapterNumber: number;
}

const STARTER_PROMPTS = [
  'Explain this concept in simple terms 💡',
  'Give me a real-world example from the syllabus 🌍',
  'Quiz me with a practice question ❓',
  'Summarize the high-yield exam takeaways 📌',
];

export const TutorDrawer: React.FC<TutorDrawerProps> = ({
  isOpen,
  onClose,
  topicId,
  topicTitle,
  subjectName,
  chapterTitle,
  chapterNumber,
}) => {
  const [messages, setMessages] = useState<TutorChatMessage[]>([
    {
      id: 'welcome',
      role: 'tutor',
      content: `Hello! I'm your Curriculum AI Tutor for **${subjectName}**.\n\nWe're currently exploring **Chapter ${chapterNumber}: ${chapterTitle}** → **${topicTitle}**.\n\nAsk me any doubt, request simple explanations, or upload a photo of your textbook problem or diagram!`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Auto-scroll on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file (PNG, JPEG, or WEBP).');
      return;
    }

    if (file.size > 7 * 1024 * 1024) {
      setError('Image size exceeds 7MB limit. Please choose a smaller image.');
      return;
    }

    setError(null);
    const reader = new FileReader();
    reader.onload = () => {
      setSelectedImage(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const removeSelectedImage = () => {
    setSelectedImage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || inputMessage).trim();
    if (!query && !selectedImage) return;
    if (isLoading) return;

    setError(null);
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const currentImg = selectedImage;

    const studentMsg: TutorChatMessage = {
      id: `student-${Date.now()}`,
      role: 'student',
      content: query || (currentImg ? 'Uploaded diagram/exercise for doubt solving' : ''),
      timestamp,
      imageUrl: currentImg,
    };

    setMessages((prev) => [...prev, studentMsg]);
    setInputMessage('');
    setSelectedImage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    setIsLoading(true);

    try {
      // Build conversation turns for context
      const historyPayload = messages
        .filter((m) => m.id !== 'welcome')
        .slice(-10)
        .map((m) => ({
          role: m.role as 'student' | 'tutor',
          content: m.content,
        }));

      const resp = await askAITutor({
        topic_id: topicId,
        message: query || 'Analyze this textbook image and guide me through solving it.',
        conversation_history: historyPayload,
        image_base64: currentImg,
      });

      const tutorReply: TutorChatMessage = {
        id: `tutor-${Date.now()}`,
        role: 'tutor',
        content: resp.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, tutorReply]);
    } catch (err: any) {
      const errMsg =
        err.message ||
        'Unable to contact the AI Tutor. Please check your connection or server configuration.';
      setError(errMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="tutor-drawer-backdrop" onClick={onClose} role="presentation">
      <aside
        className="tutor-drawer"
        role="dialog"
        aria-label="Curriculum AI Tutor"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div className="tutor-header">
          <div className="tutor-header-title">
            <div className="tutor-avatar" aria-hidden="true">🤖</div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h2 style={{ fontSize: '16px', fontWeight: 700, margin: 0, color: '#0f172a' }}>
                  SmartLearn AI Tutor
                </h2>
                <span className="tutor-badge">Curriculum-Aware</span>
              </div>
              <p style={{ fontSize: '12px', color: '#64748b', margin: '2px 0 0' }}>
                {subjectName} • {topicTitle}
              </p>
            </div>
          </div>
          <button
            type="button"
            className="tutor-close-btn"
            onClick={onClose}
            aria-label="Close AI Tutor"
          >
            ✕
          </button>
        </div>

        {/* Error Alert Banner */}
        {error && (
          <div className="tutor-error-banner" role="alert">
            <span>⚠️</span>
            <div style={{ flex: 1 }}>{error}</div>
            <button
              type="button"
              style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '13px' }}
              onClick={() => setError(null)}
              aria-label="Dismiss error"
            >
              ✕
            </button>
          </div>
        )}

        {/* Message Thread */}
        <div className="tutor-messages-container" role="log" aria-live="polite">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`tutor-bubble-row ${msg.role === 'student' ? 'student-row' : 'tutor-row'}`}
            >
              {msg.role === 'tutor' && (
                <div className="tutor-bubble-avatar" aria-hidden="true">🤖</div>
              )}

              <div className={`tutor-bubble ${msg.role === 'student' ? 'student-bubble' : 'tutor-bubble-content'}`}>
                {msg.imageUrl && (
                  <div className="tutor-msg-image-wrap">
                    <img src={msg.imageUrl} alt="Student attached doubt" className="tutor-msg-image" />
                  </div>
                )}
                <div style={{ whiteSpace: 'pre-line' }}>{msg.content}</div>
                <div className="tutor-msg-time">{msg.timestamp}</div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="tutor-bubble-row tutor-row">
              <div className="tutor-bubble-avatar" aria-hidden="true">🤖</div>
              <div className="tutor-bubble tutor-bubble-content loading-bubble">
                <div className="tutor-typing-indicator" aria-label="Tutor is thinking">
                  <span />
                  <span />
                  <span />
                </div>
                <span style={{ fontSize: '13px', color: '#64748b', marginLeft: '8px' }}>
                  Analyzing doubt against syllabus...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Starter Prompt Chips */}
        {messages.length <= 3 && !isLoading && (
          <div className="tutor-starter-chips" aria-label="Suggested questions">
            <span style={{ fontSize: '11px', color: '#64748b', fontWeight: 600, width: '100%', marginBottom: '4px' }}>
              Suggested Starter Prompts:
            </span>
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

        {/* Input Area */}
        <div className="tutor-input-section">
          {selectedImage && (
            <div className="tutor-image-preview">
              <img src={selectedImage} alt="Selected attachment preview" />
              <button
                type="button"
                className="tutor-remove-img-btn"
                onClick={removeSelectedImage}
                title="Remove image"
                aria-label="Remove attached image"
              >
                ✕
              </button>
            </div>
          )}

          <div className="tutor-input-row">
            <input
              type="file"
              ref={fileInputRef}
              accept="image/png, image/jpeg, image/webp"
              style={{ display: 'none' }}
              onChange={handleImageSelect}
              id="tutor-file-upload"
            />
            <label
              htmlFor="tutor-file-upload"
              className="tutor-attach-btn"
              title="Upload textbook photo or diagram doubt"
              aria-label="Upload photo or diagram doubt"
            >
              📷
            </label>

            <textarea
              className="tutor-textarea"
              placeholder="Ask a question or explain your doubt..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              aria-label="Tutor message input"
              disabled={isLoading}
            />

            <button
              type="button"
              className="tutor-send-btn"
              onClick={() => handleSend()}
              disabled={(!inputMessage.trim() && !selectedImage) || isLoading}
              aria-label="Send message to AI Tutor"
            >
              ➤
            </button>
          </div>
        </div>
      </aside>
    </div>
  );
};
