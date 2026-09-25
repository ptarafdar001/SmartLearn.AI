import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { TutorDrawer } from '../components/learning/TutorDrawer';
import * as tutorService from '../services/tutor';

vi.mock('../services/tutor');

// Mock WebSocket
class MockWebSocket {
  static instances: MockWebSocket[] = [];
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  url: string;
  readyState: number = 0; // CONNECTING
  private _onopen: (() => void) | null = null;
  onmessage: ((ev: { data: string }) => void) | null = null;
  onerror: ((ev: any) => void) | null = null;
  onclose: ((ev: any) => void) | null = null;
  sentData: string[] = [];

  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
    queueMicrotask(() => {
      this.readyState = MockWebSocket.OPEN;
      if (this._onopen) this._onopen();
    });
  }

  get onopen(): (() => void) | null {
    return this._onopen;
  }

  set onopen(cb: (() => void) | null) {
    this._onopen = cb;
    if (this.readyState === MockWebSocket.OPEN && cb) {
      cb();
    }
  }

  send(data: string) {
    this.sentData.push(data);
  }

  close() {
    this.readyState = MockWebSocket.CLOSED;
    if (this.onclose) this.onclose({ wasClean: true });
  }

  simulateServerMessage(msg: object) {
    if (this.onmessage) {
      this.onmessage({ data: JSON.stringify(msg) });
    }
  }
}

class MockAudioContext {
  createAnalyser() {
    return {
      fftSize: 64,
      frequencyBinCount: 32,
      getByteFrequencyData: vi.fn(),
    };
  }
  createMediaStreamSource() {
    return { connect: vi.fn() };
  }
  close() {
    return Promise.resolve();
  }
  state = 'running';
}

class MockSpeechRecognition {
  continuous = true;
  interimResults = true;
  lang = 'en-US';
  start = vi.fn();
  stop = vi.fn();
  onresult = null;
  onerror = null;
  onend = null;
}



describe('TutorDrawer Component (Text & Real-Time Voice)', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    topicId: 101,
    topicTitle: 'Development of Transport & Communication',
    subjectName: 'History',
    chapterTitle: 'Emergence of the Colonial Economy',
    chapterNumber: 1,
  };

  let mockAudioTrack: { enabled: boolean; stop: () => void };

  beforeEach(() => {
    vi.clearAllMocks();
    MockWebSocket.instances = [];
    window.HTMLElement.prototype.scrollIntoView = vi.fn();

    // Mock WebSocket globally
    vi.stubGlobal('WebSocket', MockWebSocket);

    // Mock Audio Track & MediaStream
    mockAudioTrack = { enabled: true, stop: vi.fn() };
    const mockMediaStream = {
      getTracks: () => [mockAudioTrack],
      getAudioTracks: () => [mockAudioTrack],
    };

    Object.defineProperty(navigator, 'mediaDevices', {
      value: {
        getUserMedia: vi.fn().mockResolvedValue(mockMediaStream),
      },
      configurable: true,
      writable: true,
    });

    // Mock AudioContext
    vi.stubGlobal('AudioContext', MockAudioContext);

    // Mock SpeechRecognition
    vi.stubGlobal('SpeechRecognition', MockSpeechRecognition);
    vi.stubGlobal('webkitSpeechRecognition', MockSpeechRecognition);


    // Mock SpeechSynthesis
    const mockSpeechSynthesis = {
      speak: vi.fn(),
      cancel: vi.fn(),
    };
    Object.defineProperty(window, 'speechSynthesis', {
      value: mockSpeechSynthesis,
      configurable: true,
      writable: true,
    });
    class MockUtterance {
      text: string;
      rate: number = 1.0;
      pitch: number = 1.0;
      onend: (() => void) | null = null;
      onerror: ((err: any) => void) | null = null;
      constructor(text: string) {
        this.text = text;
      }
    }
    (window as any).SpeechSynthesisUtterance = MockUtterance;
    vi.stubGlobal('SpeechSynthesisUtterance', MockUtterance);
  });




  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('renders drawer with curriculum context and mode switcher tabs', () => {
    render(<TutorDrawer {...defaultProps} />);

    expect(screen.getByRole('dialog', { name: /Curriculum AI Tutor/i })).toBeInTheDocument();
    expect(screen.getByText('SmartLearn AI Tutor')).toBeInTheDocument();
    expect(screen.getByText(/History • Development of Transport & Communication/i)).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Chat Doubt-Solving/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Live Voice Tutor/i })).toBeInTheDocument();
  });

  it('submits student question in chat mode and displays tutor reply', async () => {
    vi.mocked(tutorService.askAITutor).mockResolvedValue({
      reply: 'The Railway Guarantee System promised British investors a 5% return guaranteed from Indian taxes.',
      topic_id: 101,
      topic_title: 'Development of Transport & Communication',
      subject_name: 'History',
      board: 'ISC',
      grade: 'Class 11',
      grounded_resource_titles: ['Colonial Transport Infrastructure'],
      is_out_of_scope: false,
    });

    render(<TutorDrawer {...defaultProps} />);

    const textarea = screen.getByPlaceholderText(/Ask a question or explain your doubt/i);
    fireEvent.change(textarea, { target: { value: 'Why was the guarantee system controversial?' } });

    const sendBtn = screen.getByRole('button', { name: /Send message to AI Tutor/i });
    fireEvent.click(sendBtn);

    expect(screen.getByText('Why was the guarantee system controversial?')).toBeInTheDocument();

    await waitFor(() => {
      expect(
        screen.getByText(
          'The Railway Guarantee System promised British investors a 5% return guaranteed from Indian taxes.'
        )
      ).toBeInTheDocument();
    });

    expect(tutorService.askAITutor).toHaveBeenCalledWith(
      expect.objectContaining({
        topic_id: 101,
        message: 'Why was the guarantee system controversial?',
      })
    );
  });

  it('switches to Live Voice mode and starts voice session with mic and WebSocket', async () => {
    vi.mocked(tutorService.createVoiceSession).mockResolvedValue({
      session_id: 'sess-abc-123',
      session_token: 'ephemeral-jwt-token-xyz',
      ws_endpoint: '/api/v1/tutor/voice/ws',
      topic_id: 101,
      topic_title: 'Development of Transport & Communication',
      subject_name: 'History',
      board: 'ISC',
      grade: 'Class 11',
      expires_in_seconds: 900,
    });

    render(<TutorDrawer {...defaultProps} />);

    const voiceTab = screen.getByRole('tab', { name: /Live Voice Tutor/i });
    fireEvent.click(voiceTab);

    // Verify session creation called
    await waitFor(() => {
      expect(tutorService.createVoiceSession).toHaveBeenCalledWith(101);
      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({ audio: true });
    });

    // Verify WebSocket connected
    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBeGreaterThan(0);
      expect(MockWebSocket.instances[0].url).toContain('/api/v1/tutor/voice/ws?token=ephemeral-jwt-token-xyz');
    });

    // Check listening status badge once ws open
    await waitFor(() => {
      expect(screen.getByText(/Listening.../i)).toBeInTheDocument();
    });
  });

  it('handles microphone permission denial gracefully in voice mode', async () => {
    const permError = new Error('Permission denied');
    permError.name = 'NotAllowedError';
    vi.mocked(navigator.mediaDevices.getUserMedia).mockRejectedValueOnce(permError);

    render(<TutorDrawer {...defaultProps} />);

    const voiceTab = screen.getByRole('tab', { name: /Live Voice Tutor/i });
    fireEvent.click(voiceTab);

    await waitFor(() => {
      expect(screen.getByText(/Microphone permission was denied/i)).toBeInTheDocument();
      expect(screen.getByText(/Connection Issue/i)).toBeInTheDocument();
    });
  });

  it('supports muting and unmuting microphone in voice mode', async () => {
    vi.mocked(tutorService.createVoiceSession).mockResolvedValue({
      session_id: 'sess-abc-123',
      session_token: 'ephemeral-jwt-token-xyz',
      ws_endpoint: '/api/v1/tutor/voice/ws',
      topic_id: 101,
      topic_title: 'Development of Transport & Communication',
      subject_name: 'History',
      board: 'ISC',
      grade: 'Class 11',
      expires_in_seconds: 900,
    });

    render(<TutorDrawer {...defaultProps} />);
    fireEvent.click(screen.getByRole('tab', { name: /Live Voice Tutor/i }));

    await screen.findByText(/Listening.../i);

    // Click mute button
    const muteBtn = screen.getByRole('button', { name: /Mute microphone/i });
    fireEvent.click(muteBtn);

    expect(mockAudioTrack.enabled).toBe(false);
    expect(screen.getByText(/Microphone Muted/i)).toBeInTheDocument();

    // Click unmute
    const unmuteBtn = screen.getByRole('button', { name: /Unmute microphone/i });
    fireEvent.click(unmuteBtn);

    expect(mockAudioTrack.enabled).toBe(true);
  });

  it('handles incoming tutor speech and allows interruption', async () => {
    vi.mocked(tutorService.createVoiceSession).mockResolvedValue({
      session_id: 'sess-abc-123',
      session_token: 'ephemeral-jwt-token-xyz',
      ws_endpoint: '/api/v1/tutor/voice/ws',
      topic_id: 101,
      topic_title: 'Development of Transport & Communication',
      subject_name: 'History',
      board: 'ISC',
      grade: 'Class 11',
      expires_in_seconds: 900,
    });

    render(<TutorDrawer {...defaultProps} />);
    fireEvent.click(screen.getByRole('tab', { name: /Live Voice Tutor/i }));

    await screen.findByText(/Listening.../i);

    const wsInstance = MockWebSocket.instances[0];

    // Simulate tutor speaking message from server
    wsInstance.simulateServerMessage({
      type: 'speaking',
      text: 'Lord Dalhousie was the Governor-General who introduced railways in 1853.',
      session_id: 'sess-abc-123',
    });

    await waitFor(() => {
      expect(screen.getByText(/Lord Dalhousie was the Governor-General/i)).toBeInTheDocument();
      expect(screen.getByText(/Speaking.../i)).toBeInTheDocument();
      expect(window.speechSynthesis.speak).toHaveBeenCalled();
    });

    // Check stop voice / interrupt button
    const stopVoiceBtn = screen.getByRole('button', { name: /Stop tutor speaking/i });
    expect(stopVoiceBtn).toBeInTheDocument();

    fireEvent.click(stopVoiceBtn);
    expect(window.speechSynthesis.cancel).toHaveBeenCalled();
    expect(wsInstance.sentData).toContain(JSON.stringify({ type: 'interrupt' }));
  });


  it('closes when close button is clicked', () => {
    render(<TutorDrawer {...defaultProps} />);

    const closeBtn = screen.getByRole('button', { name: /Close AI Tutor/i });
    fireEvent.click(closeBtn);

    expect(defaultProps.onClose).toHaveBeenCalled();
  });
});
