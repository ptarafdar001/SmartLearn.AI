import React, { useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Bot,
  Send,
  Image as ImageIcon,
  X,
  AlertCircle,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
} from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { MarkdownRenderer } from '../components/learning/MarkdownRenderer';
import { askAITutor } from '../services/tutor';
import { fetchEnrolledSubjects, fetchSubjectDetail } from '../services/learning';
import type { TutorChatMessage } from '../types/tutor';

const STARTER_PROMPTS = [
  'Explain this concept in simple terms',
  'What are the 3 main points for board exam?',
  'Give me a clear real-world analogy',
  'Generate high-yield practice questions',
];

interface TopicOption {
  id: number;
  title: string;
  chapterTitle: string;
  subjectName: string;
}

export const AITutorPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialTopicParam = searchParams.get('topicId');

  const [topics, setTopics] = useState<TopicOption[]>([]);
  const [activeTopicId, setActiveTopicId] = useState<number>(
    initialTopicParam ? Number(initialTopicParam) : 1
  );

  const [messages, setMessages] = useState<TutorChatMessage[]>([
    {
      id: 'welcome',
      role: 'tutor',
      content: `Hello! I am your **Curriculum-Aware AI Tutor**.\n\nI am grounded in official board syllabus guidelines and verified learning materials.\n\nYou can:\n- Ask any conceptual doubt or syllabus question.\n- Click the **Microphone** button to speak your doubt aloud!\n- Upload diagrams, math problems, or homework photos.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('gemini-1.5-flash');

  // Dedicated Browser Voice Mode (Web Speech Recognition + Speech Synthesis)
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSpeakingVoice, setIsSpeakingVoice] = useState<boolean>(false);
  const [activeSpeechMsgId, setActiveSpeechMsgId] = useState<string | null>(null);
  const [isAudioMuted, setIsAudioMuted] = useState<boolean>(false);
  const recognitionRef = useRef<any>(null);

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
            setActiveTopicId(availableTopics[0].id);
          }
        }
      } catch {
        // fallback
      }
    }
    loadCurriculumTopics();
  }, [initialTopicParam]);

  // Speech Recognition Setup
  const toggleSpeechRecognition = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setChatError('Speech recognition is not supported in this browser. Please use Chrome, Edge, or Brave.');
      return;
    }

    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-IN';

      recognition.onstart = () => {
        setIsListening(true);
        setChatError(null);
      };

      recognition.onresult = (event: any) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        setInputMessage(transcript);
        if (event.results[0].isFinal) {
          setIsListening(false);
          handleSend(transcript);
        }
      };

      recognition.onerror = (event: any) => {
        setIsListening(false);
        if (event.error !== 'no-speech') {
          setChatError(`Microphone recognition error: ${event.error}`);
        }
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err: any) {
      setIsListening(false);
      setChatError(err.message || 'Could not start microphone.');
    }
  };

  // Text to Speech
  const speakText = (text: string, msgId?: string) => {
    if (!('speechSynthesis' in window)) return;
    if (isAudioMuted) return;

    window.speechSynthesis.cancel();

    // Strip markdown formatting for natural voice reading
    const cleanText = text
      .replace(/[*#_`>]/g, '')
      .replace(/\[(.*?)\]\(.*?\)/g, '$1')
      .replace(/\$(.*?)\$/g, '$1')
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.onstart = () => {
      setIsSpeakingVoice(true);
      if (msgId) setActiveSpeechMsgId(msgId);
    };
    utterance.onend = () => {
      setIsSpeakingVoice(false);
      setActiveSpeechMsgId(null);
    };
    utterance.onerror = () => {
      setIsSpeakingVoice(false);
      setActiveSpeechMsgId(null);
    };
    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeakingVoice(false);
      setActiveSpeechMsgId(null);
    }
  };

  const toggleMute = () => {
    if (!isAudioMuted) {
      stopSpeaking();
      setIsAudioMuted(true);
    } else {
      setIsAudioMuted(false);
    }
  };

  const activeTopic = topics.find((t) => t.id === activeTopicId);

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
        topic_id: activeTopicId,
        model: selectedModel,
        message: query || 'Please analyze this diagram or problem from the syllabus.',
        image_base64: currentImg || undefined,
        conversation_history: nextHistory.slice(-6).map((m) => ({
          role: m.role,
          content: m.content,
        })),
      });

      const tutorMsg: TutorChatMessage = {
        id: `tutor-${Date.now()}`,
        role: 'tutor',
        content: res.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, tutorMsg]);

      // Automatically speak the response if the user asked via voice
      if (textToSend) {
        speakText(res.reply, tutorMsg.id);
      }
    } catch (err: any) {
      setChatError(err.message || 'Failed to connect to AI tutor service.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppLayout breadcrumbs={[{ label: 'AI Tutor' }]}>
      <div className="tutor-page-wrapper">
        <div className="tutor-page-header">
          <div className="tutor-header-left">
            <div className="tutor-page-icon">
              <Bot size={22} />
            </div>
            <div>
              <div className="tutor-title-row">
                <h1 className="tutor-page-title">Curriculum AI Tutor</h1>
                <span className="tutor-badge">Grounded in Official Syllabus</span>
              </div>
              <p className="tutor-page-subtitle">
                {activeTopic ? (
                  <>Context: {activeTopic.subjectName} • {activeTopic.chapterTitle} • {activeTopic.title}</>
                ) : (
                  <>Context: Verified School Curriculum</>
                )}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <select
              aria-label="Select AI Model"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="filter-pill"
              style={{ background: '#fff', border: '1px solid #818cf8', color: '#4338ca', fontWeight: 600, padding: '6px 12px', fontSize: '13px', borderRadius: '8px' }}
            >
              <option value="gemini-1.5-flash">⚡ Gemini Flash (Fast)</option>
              <option value="gemini-2.0-flash">🚀 Gemini Flash Lite (Ultra-Low Latency)</option>
              <option value="gemini-1.5-pro">🧠 Gemini Pro (Deep Reasoning)</option>
            </select>

            {topics.length > 0 && (
              <select
                aria-label="Select Syllabus Topic"
                value={activeTopicId}
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
                    {t.chapterTitle}: {t.title}
                  </option>
                ))}
              </select>
            )}

            {/* Global Speaker Controls: Stop Speaking & Mute/Unmute */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              {isSpeakingVoice && (
                <button
                  type="button"
                  onClick={stopSpeaking}
                  className="filter-pill"
                  style={{
                    background: '#fee2e2',
                    color: '#b91c1c',
                    border: '1px solid #fca5a5',
                    padding: '6px 12px',
                    fontSize: '13px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    cursor: 'pointer',
                    fontWeight: 600,
                  }}
                  title="Click to instantly silence the tutor"
                >
                  <VolumeX size={15} />
                  <span>Stop Speaking</span>
                </button>
              )}

              <button
                type="button"
                onClick={toggleMute}
                className="filter-pill"
                style={{
                  background: isAudioMuted ? '#fef3c7' : '#f1f5f9',
                  color: isAudioMuted ? '#b45309' : '#475569',
                  border: isAudioMuted ? '1px solid #fde68a' : '1px solid #cbd5e1',
                  padding: '6px 12px',
                  fontSize: '13px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  cursor: 'pointer',
                  fontWeight: 600,
                }}
                title={isAudioMuted ? 'Voice output is Muted (Click to Unmute)' : 'Click to Mute Voice Tutor'}
              >
                {isAudioMuted ? <VolumeX size={15} color="#b45309" /> : <Volume2 size={15} color="#475569" />}
                <span>{isAudioMuted ? 'Tutor Muted' : 'Speaker On'}</span>
              </button>
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

          <div className="tutor-chat-messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`tutor-msg-row ${msg.role === 'student' ? 'student-row' : 'tutor-row'}`}>
                {msg.role === 'tutor' && (
                  <div className="tutor-avatar-circle" aria-hidden="true">
                    <Bot size={16} />
                  </div>
                )}
                <div className={`tutor-bubble ${msg.role === 'student' ? 'student-bubble' : 'tutor-bubble-ai'}`}>
                  {msg.imageUrl && (
                    <div className="tutor-msg-image-wrap">
                      <img src={msg.imageUrl} alt="Attached diagram" />
                    </div>
                  )}
                  {msg.role === 'tutor' ? (
                    <MarkdownRenderer content={msg.content} />
                  ) : (
                    <p style={{ margin: 0 }}>{msg.content}</p>
                  )}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
                    <span className="tutor-timestamp">{msg.timestamp}</span>
                    {msg.role === 'tutor' && (
                      <button
                        type="button"
                        onClick={() => {
                          if (isSpeakingVoice && activeSpeechMsgId === msg.id) {
                            stopSpeaking();
                          } else {
                            speakText(msg.content, msg.id);
                          }
                        }}
                        title={
                          isSpeakingVoice && activeSpeechMsgId === msg.id
                            ? 'Stop reading this response'
                            : 'Listen to this explanation'
                        }
                        style={{
                          background: isSpeakingVoice && activeSpeechMsgId === msg.id ? '#fee2e2' : 'none',
                          border: isSpeakingVoice && activeSpeechMsgId === msg.id ? '1px solid #fca5a5' : 'none',
                          borderRadius: 6,
                          cursor: 'pointer',
                          color: isSpeakingVoice && activeSpeechMsgId === msg.id ? '#dc2626' : '#6366f1',
                          padding: '3px 6px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 4,
                          fontSize: 12,
                          fontWeight: 500,
                        }}
                      >
                        {isSpeakingVoice && activeSpeechMsgId === msg.id ? (
                          <>
                            <VolumeX size={14} />
                            <span>Stop</span>
                          </>
                        ) : (
                          <>
                            <Volume2 size={14} />
                            <span>Listen</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="tutor-msg-row tutor-row">
                <div className="tutor-avatar-circle" aria-hidden="true">
                  <Bot size={16} />
                </div>
                <div className="tutor-bubble tutor-bubble-ai">
                  <div className="tutor-typing-dots">
                    <span /><span /><span />
                  </div>
                </div>
              </div>
            )}
          </div>

          {messages.length <= 2 && !isLoading && (
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

          {/* Input Bar with Dedicated Voice Tutor Button */}
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

              {/* Dedicated Voice Tutor Toggle */}
              <button
                type="button"
                onClick={toggleSpeechRecognition}
                className={`tutor-attach-btn ${isListening ? 'listening-active' : ''}`}
                style={{
                  background: isListening ? '#ef4444' : '#eef2ff',
                  color: isListening ? '#ffffff' : '#4f46e5',
                  transition: 'all 0.2s ease',
                  border: isListening ? 'none' : '1px solid #c7d2fe',
                }}
                title={isListening ? 'Listening to your voice... (Click to stop)' : 'Click to Speak (Dedicated Voice Tutor)'}
              >
                {isListening ? <MicOff size={18} /> : <Mic size={18} />}
              </button>

              <textarea
                className="tutor-textarea"
                placeholder={isListening ? 'Listening to your voice... speak your question...' : 'Ask any doubt or request a concept explanation...'}
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
