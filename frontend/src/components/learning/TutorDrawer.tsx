import React, { useEffect, useRef, useState } from 'react';
import {
  Bot,
  Send,
  Image as ImageIcon,
  X,
  MessageSquare,
  Mic,
  MicOff,
  Square,
  PhoneOff,
  RotateCcw,
  AlertCircle,
  Sparkles,
  Volume2,
  Headphones,
} from 'lucide-react';
import { askAITutor, createVoiceSession } from '../../services/tutor';
import type { TutorChatMessage, VoiceSessionResponse, VoiceState } from '../../types/tutor';
import { MarkdownRenderer } from './MarkdownRenderer';

interface TutorDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  topicId: number;
  topicTitle: string;
  subjectName: string;
  chapterTitle: string;
  chapterNumber: number;
}

interface VoiceTranscriptItem {
  id: string;
  role: 'student' | 'tutor';
  text: string;
  timestamp: string;
}

const STARTER_PROMPTS = [
  'Explain this concept in simple terms',
  'Give me a real-world example from the syllabus',
  'Quiz me with a practice question',
  'Summarize the high-yield exam takeaways',
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
  // Mode: 'chat' or 'voice'
  const [activeTab, setActiveTab] = useState<'chat' | 'voice'>('chat');

  // ── Chat State ─────────────────────────────────────────────────────────────
  const [messages, setMessages] = useState<TutorChatMessage[]>([
    {
      id: 'welcome',
      role: 'tutor',
      content: `Hello! I am your Curriculum AI Tutor for **${subjectName}**.\n\nWe are currently studying **Chapter ${chapterNumber}: ${chapterTitle}** → **${topicTitle}**.\n\nAsk any question, request step-by-step breakdowns, or upload a textbook photo/diagram for guided doubt-solving.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [chatError, setChatError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // ── Voice State ────────────────────────────────────────────────────────────
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [interimSpeech, setInterimSpeech] = useState<string>('');
  const [voiceTranscripts, setVoiceTranscripts] = useState<VoiceTranscriptItem[]>([]);
  const voiceEndRef = useRef<HTMLDivElement | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const recognitionRef = useRef<any | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const activeSessionRef = useRef<VoiceSessionResponse | null>(null);
  const voiceStateRef = useRef<VoiceState>('idle');
  voiceStateRef.current = voiceState;

  // Auto-scroll on new chat message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Auto-scroll on voice transcripts
  useEffect(() => {
    voiceEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [voiceTranscripts, interimSpeech]);

  // Cleanup voice session on unmount or drawer close
  useEffect(() => {
    if (!isOpen) {
      if (voiceStateRef.current !== 'idle') {
        stopVoiceSession();
      }
    }
    return () => {
      stopVoiceSession();
    };
  }, [isOpen]);

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

  // ── Chat Functions ─────────────────────────────────────────────────────────
  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setChatError('Please select a valid image file (PNG, JPEG, or WEBP).');
      return;
    }

    if (file.size > 7 * 1024 * 1024) {
      setChatError('Image size exceeds 7MB limit. Please choose a smaller image.');
      return;
    }

    setChatError(null);
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
    removeSelectedImage();
    setIsLoading(true);

    try {
      const historyPayload = nextHistory
        .filter((m) => m.id !== 'welcome')
        .slice(-6)
        .map((m) => ({
          role: m.role,
          content: m.content,
        }));

      const res = await askAITutor({
        topic_id: topicId,
        message: query || 'Please analyze this diagram or problem from the syllabus.',
        image_base64: currentImg || undefined,
        conversation_history: historyPayload,
      });

      const tutorMsg: TutorChatMessage = {
        id: `tutor-${Date.now()}`,
        role: 'tutor',
        content: res.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, tutorMsg]);
    } catch (err: any) {
      const errMsg = err.message || 'Failed to get tutor response. Please try again.';
      setChatError(errMsg);
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

  // ── Voice Session Lifecycle ────────────────────────────────────────────────
  const startVoiceSession = async () => {
    setVoiceError(null);
    setVoiceState('connecting');
    setInterimSpeech('');

    try {
      // 1. Request Ephemeral Voice Session Token from backend
      const sessionData = await createVoiceSession(topicId);
      activeSessionRef.current = sessionData;

      // 2. Request user microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // 3. Setup Web Audio API Analyser for live frequency spectrum
      setupAudioVisualizer(stream);

      // 4. Initialize WebSocket connection to backend voice gateway
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = window.location.host;
      let endpoint = sessionData.ws_endpoint;

      if (!endpoint.startsWith('ws://') && !endpoint.startsWith('wss://')) {
        if (!endpoint.startsWith('http')) {
          endpoint = `${wsProtocol}//${wsHost}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
        } else {
          endpoint = endpoint.replace(/^http/, 'ws');
        }
      }

      const wsUrl = `${endpoint}?token=${encodeURIComponent(sessionData.session_token)}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setVoiceState('listening');
        initSpeechRecognition();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch {
          // ignore parsing error
        }
      };

      ws.onerror = () => {
        setVoiceError('Voice connection error. Please verify your network and microphone.');
        setVoiceState('error');
      };

      ws.onclose = () => {
        if (voiceStateRef.current !== 'idle') {
          setVoiceState('idle');
        }
      };
    } catch (err: any) {
      const msg =
        err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError'
          ? 'Microphone permission was denied. Please allow microphone access in your browser.'
          : err.message || 'Failed to initialize voice session.';
      setVoiceError(msg);
      setVoiceState('error');
      stopMediaStream();
    }
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'session_ready':
        setVoiceState('listening');
        break;

      case 'speaking':
      case 'tutor_speech':
        setVoiceState('speaking');
        setVoiceTranscripts((prev) => [
          ...prev,
          {
            id: `vtutor-${Date.now()}`,
            role: 'tutor',
            text: data.text,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
        playTextToSpeech(data.text);
        break;

      case 'interrupted':
        if ('speechSynthesis' in window) {
          window.speechSynthesis.cancel();
        }
        setVoiceState('listening');
        break;

      case 'error':
        setVoiceError(data.message || 'Voice error occurred.');
        setVoiceState('error');
        break;

      default:
        break;
    }
  };

  const initSpeechRecognition = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        let interim = '';
        let final = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            final += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }

        if (interim) {
          setInterimSpeech(interim);
          if (voiceStateRef.current === 'speaking') {
            interruptTutor();
          }
        }

        if (final.trim()) {
          setInterimSpeech('');
          const timestamp = new Date().toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          });

          setVoiceTranscripts((prev) => [
            ...prev,
            {
              id: `vstudent-${Date.now()}`,
              role: 'student',
              text: final.trim(),
              timestamp,
            },
          ]);

          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            setVoiceState('thinking');
            wsRef.current.send(
              JSON.stringify({
                type: 'speech_final',
                text: final.trim(),
              })
            );
          }
        }
      };

      recognition.onerror = (e: any) => {
        if (e.error !== 'no-speech') {
          // non-critical error
        }
      };

      recognition.onend = () => {
        if (voiceStateRef.current === 'listening' && !isMuted) {
          try {
            recognition.start();
          } catch {}
        }
      };

      recognition.start();
      recognitionRef.current = recognition;
    } catch {
      // Speech recognition fallback
    }
  };

  const playTextToSpeech = (text: string) => {
    if (!('speechSynthesis' in window)) {
      setVoiceState('listening');
      return;
    }

    window.speechSynthesis.cancel();
    const cleanText = text.replace(/[*_#`~[\]]/g, '').trim();
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    utterance.onend = () => {
      if (voiceStateRef.current === 'speaking') {
        setVoiceState('listening');
      }
    };

    utterance.onerror = () => {
      setVoiceState('listening');
    };

    window.speechSynthesis.speak(utterance);
  };

  const setupAudioVisualizer = (stream: MediaStream) => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      const audioCtx = new AudioCtx();
      audioContextRef.current = audioCtx;

      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 64;
      analyserRef.current = analyser;

      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      drawVisualizerLoop();
    } catch {
      // canvas visualizer fallback
    }
  };

  const drawVisualizerLoop = () => {
    const canvas = canvasRef.current;
    const analyser = analyserRef.current;
    if (!canvas || !analyser) {
      animFrameRef.current = requestAnimationFrame(drawVisualizerLoop);
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      if (analyserRef.current && canvasRef.current) {
        analyserRef.current.getByteFrequencyData(dataArray);
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const barWidth = (canvas.width / bufferLength) * 2.2;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
          const barHeight = (dataArray[i] / 255) * (canvas.height - 4);
          const gradient = ctx.createLinearGradient(0, canvas.height, 0, 0);
          gradient.addColorStop(0, '#4f46e5');
          gradient.addColorStop(1, '#818cf8');

          ctx.fillStyle = isMuted ? '#94a3b8' : gradient;
          ctx.fillRect(x, canvas.height - barHeight - 2, barWidth - 1, barHeight + 2);
          x += barWidth;
        }
      }
      animFrameRef.current = requestAnimationFrame(draw);
    };
    draw();
  };

  const toggleMute = () => {
    if (streamRef.current) {
      const audioTracks = streamRef.current.getAudioTracks();
      const newMutedState = !isMuted;
      audioTracks.forEach((track) => {
        track.enabled = !newMutedState;
      });
      setIsMuted(newMutedState);

      if (recognitionRef.current) {
        if (newMutedState) {
          try {
            recognitionRef.current.stop();
          } catch {}
        } else {
          try {
            recognitionRef.current.start();
          } catch {}
        }
      }
    }
  };

  const interruptTutor = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'interrupt' }));
    }
    setVoiceState('listening');
  };

  const stopMediaStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
  };

  const stopVoiceSession = () => {
    stopMediaStream();

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {}
      recognitionRef.current = null;
    }

    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }

    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch {}
      wsRef.current = null;
    }

    setVoiceState('idle');
    setInterimSpeech('');
    setIsMuted(false);
    activeSessionRef.current = null;
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
            <div className="tutor-avatar" aria-hidden="true">
              <Bot size={18} />
            </div>
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
            <X size={18} />
          </button>
        </div>

        {/* Tab Switcher: Chat vs Live Voice */}
        <div className="tutor-mode-tabs" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'chat'}
            className={`tutor-mode-tab ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            <MessageSquare size={15} />
            <span>Chat Doubt-Solving</span>
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'voice'}
            className={`tutor-mode-tab ${activeTab === 'voice' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('voice');
              if (voiceState === 'idle') {
                startVoiceSession();
              }
            }}
          >
            <Mic size={15} />
            <span>Live Voice Tutor</span>
          </button>
        </div>

        {/* ── TAB 1: TEXT & IMAGE CHAT ────────────────────────────────────── */}
        {activeTab === 'chat' && (
          <>
            {/* Error Alert Banner */}
            {chatError && (
              <div className="tutor-error-banner" role="alert">
                <AlertCircle size={16} className="text-amber-600" />
                <div style={{ flex: 1 }}>{chatError}</div>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
                  onClick={() => setChatError(null)}
                  aria-label="Dismiss error"
                >
                  <X size={14} />
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
                    <div className="tutor-bubble-avatar" aria-hidden="true">
                      <Bot size={16} />
                    </div>
                  )}

                  <div className={`tutor-bubble ${msg.role === 'student' ? 'student-bubble' : 'tutor-bubble-content'}`}>
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
                  <div className="tutor-bubble-avatar" aria-hidden="true">
                    <Bot size={16} />
                  </div>
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
                    <X size={12} />
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
                  <ImageIcon size={18} />
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
                  <Send size={16} />
                </button>
              </div>
            </div>
          </>
        )}

        {/* ── TAB 2: LIVE VOICE TUTOR ─────────────────────────────────────── */}
        {activeTab === 'voice' && (
          <div className="tutor-voice-container">
            {/* Voice Error Banner */}
            {voiceError && (
              <div className="tutor-error-banner" role="alert" style={{ margin: '12px 16px' }}>
                <AlertCircle size={16} className="text-amber-600" />
                <div style={{ flex: 1 }}>{voiceError}</div>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
                  onClick={() => setVoiceError(null)}
                  aria-label="Dismiss error"
                >
                  <X size={14} />
                </button>
              </div>
            )}

            {/* Voice Hero Visualizer Area */}
            <div className="tutor-voice-hero">
              <div className="tutor-voice-orb-container">
                {voiceState === 'listening' && <div className="tutor-voice-pulse-ring" />}
                <div className={`tutor-voice-orb ${voiceState}`}>
                  {voiceState === 'connecting' && <RotateCcw className="spin-icon" size={26} />}
                  {voiceState === 'listening' && (isMuted ? <MicOff size={26} /> : <Mic size={26} />)}
                  {voiceState === 'thinking' && <Sparkles size={26} />}
                  {voiceState === 'speaking' && <Volume2 size={26} />}
                  {voiceState === 'idle' && <Headphones size={26} />}
                  {voiceState === 'error' && <AlertCircle size={26} />}
                </div>
              </div>

              {/* Status Badge */}
              <div className={`tutor-voice-status-badge status-badge-${voiceState}`}>
                {voiceState === 'connecting' && 'Connecting...'}
                {voiceState === 'listening' && (isMuted ? 'Microphone Muted' : 'Listening...')}
                {voiceState === 'thinking' && 'Thinking...'}
                {voiceState === 'speaking' && 'Speaking...'}
                {voiceState === 'idle' && 'Voice Idle'}
                {voiceState === 'error' && 'Connection Issue'}
              </div>

              {/* Guidance text */}
              <p className="tutor-voice-status-text">
                {voiceState === 'listening' && !isMuted && 'Speak naturally! Ask questions or discuss syllabus topics.'}
                {voiceState === 'listening' && isMuted && 'Microphone is currently muted. Click unmute below.'}
                {voiceState === 'thinking' && 'Consulting curriculum learning materials...'}
                {voiceState === 'speaking' && 'AI Tutor is explaining. Interrupt anytime by speaking!'}
                {voiceState === 'connecting' && 'Securing voice session and initializing speech stream...'}
                {voiceState === 'idle' && 'Tap Start to begin conversational voice tutoring.'}
                {voiceState === 'error' && 'Voice session encountered an error. Check permissions or retry.'}
              </p>

              {/* Live Audio Spectrum Canvas */}
              {(voiceState === 'listening' || voiceState === 'speaking') && (
                <canvas
                  ref={canvasRef}
                  width={320}
                  height={48}
                  className="tutor-voice-canvas"
                  aria-label="Audio frequency waveform"
                />
              )}
            </div>

            {/* Live Conversation Transcript Panel */}
            <div className="tutor-voice-transcript-panel" role="log" aria-live="polite">
              {voiceTranscripts.length === 0 && !interimSpeech && (
                <div style={{ textAlign: 'center', color: '#94a3b8', fontSize: '13px', margin: 'auto' }}>
                  Spoken conversation transcript will appear here in real-time.
                </div>
              )}

              {voiceTranscripts.map((t) => (
                <div
                  key={t.id}
                  className={`tutor-bubble-row ${t.role === 'student' ? 'student-row' : 'tutor-row'}`}
                >
                  {t.role === 'tutor' && (
                    <div className="tutor-bubble-avatar" aria-hidden="true">
                      <Bot size={16} />
                    </div>
                  )}
                  <div className={`tutor-bubble ${t.role === 'student' ? 'student-bubble' : 'tutor-bubble-content'}`}>
                    <div>{t.text}</div>
                    <div className="tutor-msg-time">{t.timestamp}</div>
                  </div>
                </div>
              ))}

              {/* Live Interim Student Speech */}
              {interimSpeech && (
                <div className="tutor-bubble-row student-row">
                  <div className="tutor-bubble student-bubble tutor-live-interim">
                    <span>{interimSpeech}...</span>
                  </div>
                </div>
              )}

              <div ref={voiceEndRef} />
            </div>

            {/* Voice Controls Bar */}
            <div className="tutor-voice-controls">
              {voiceState === 'idle' ? (
                <button
                  type="button"
                  className="voice-btn voice-btn-primary"
                  onClick={startVoiceSession}
                  aria-label="Start Voice Conversation"
                >
                  <Mic size={16} />
                  <span>Start Voice Conversation</span>
                </button>
              ) : (
                <>
                  {/* Mute / Unmute Button */}
                  <button
                    type="button"
                    className={`voice-btn voice-btn-circle voice-btn-mute ${isMuted ? 'active' : ''}`}
                    onClick={toggleMute}
                    title={isMuted ? 'Unmute microphone' : 'Mute microphone'}
                    aria-label={isMuted ? 'Unmute microphone' : 'Mute microphone'}
                  >
                    {isMuted ? <MicOff size={18} /> : <Mic size={18} />}
                  </button>

                  {/* Interrupt / Stop Tutor Speaking Button */}
                  {voiceState === 'speaking' && (
                    <button
                      type="button"
                      className="voice-btn voice-btn-interrupt"
                      onClick={interruptTutor}
                      title="Stop speaking (interrupt)"
                      aria-label="Stop tutor speaking"
                    >
                      <Square size={14} fill="currentColor" />
                      <span>Stop Voice</span>
                    </button>
                  )}

                  {/* End Session Button */}
                  <button
                    type="button"
                    className="voice-btn voice-btn-end"
                    onClick={stopVoiceSession}
                    title="End voice session"
                    aria-label="End voice session"
                  >
                    <PhoneOff size={15} />
                    <span>End Call</span>
                  </button>

                  {/* Reconnect Button if error */}
                  {voiceState === 'error' && (
                    <button
                      type="button"
                      className="voice-btn voice-btn-primary"
                      onClick={startVoiceSession}
                      aria-label="Retry Voice Session"
                    >
                      <RotateCcw size={15} />
                      <span>Retry</span>
                    </button>
                  )}
                </>
              )}
            </div>
          </div>
        )}
      </aside>
    </div>
  );
};
