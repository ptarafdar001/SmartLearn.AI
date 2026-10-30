with open('frontend/src/pages/AITutorPage.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update Lucide imports
old_import = "  Volume2,\n}"
new_import = "  Volume2,\n  VolumeX,\n}"
assert old_import in code, "old_import not found"
code = code.replace(old_import, new_import, 1)

# 2. Add currentlyPlayingMsgId state and autoSpeakEnabled toggle state
old_states = "  const [isSpeakingVoice, setIsSpeakingVoice] = useState<boolean>(false);"
new_states = """  const [isSpeakingVoice, setIsSpeakingVoice] = useState<boolean>(false);
  const [activeSpeechMsgId, setActiveSpeechMsgId] = useState<string | null>(null);
  const [isAudioMuted, setIsAudioMuted] = useState<boolean>(false);"""
assert old_states in code, "old_states not found"
code = code.replace(old_states, new_states, 1)

# 3. Update speakText and stopSpeaking
old_speak = """  // Text to Speech
  const speakText = (text: string) => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();

    // Strip markdown formatting for natural voice reading
    const cleanText = text
      .replace(/[*#_`>]/g, '')
      .replace(/\\[(.*?)\\]\\(.*?\\)/g, '$1')
      .replace(/\\$(.*?)\\$/g, '$1')
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.onstart = () => setIsSpeakingVoice(true);
    utterance.onend = () => setIsSpeakingVoice(false);
    utterance.onerror = () => setIsSpeakingVoice(false);
    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeakingVoice(false);
    }
  };"""

new_speak = """  // Text to Speech
  const speakText = (text: string, msgId?: string) => {
    if (!('speechSynthesis' in window)) return;
    if (isAudioMuted) return;

    window.speechSynthesis.cancel();

    // Strip markdown formatting for natural voice reading
    const cleanText = text
      .replace(/[*#_`>]/g, '')
      .replace(/\\[(.*?)\\]\\(.*?\\)/g, '$1')
      .replace(/\\$(.*?)\\$/g, '$1')
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
  };"""

assert old_speak in code, "old_speak not found"
code = code.replace(old_speak, new_speak, 1)

# 4. In handleSend: speakText(res.reply, tutorMsg.id);
old_send_speak = "speakText(res.reply);"
new_send_speak = "speakText(res.reply, tutorMsg.id);"
assert old_send_speak in code, "old_send_speak not found"
code = code.replace(old_send_speak, new_send_speak, 1)

# 5. Header Bar controls for Speaker
old_header_controls = """            {isSpeakingVoice && (
              <button
                type="button"
                onClick={stopSpeaking}
                className="filter-pill"
                style={{ background: '#fee2e2', color: '#b91c1c', border: '1px solid #fca5a5', padding: '6px 12px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}
              >
                <Volume2 size={14} />
                <span>Stop Speaking</span>
              </button>
            )}"""

new_header_controls = """            {/* Global Speaker Controls: Stop Speaking & Mute/Unmute */}
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
            </div>"""

assert old_header_controls in code, "old_header_controls not found"
code = code.replace(old_header_controls, new_header_controls, 1)

# 6. Message-level Speaker Button (Toggle Play / Stop)
old_msg_speaker = """                    {msg.role === 'tutor' && (
                      <button
                        type="button"
                        onClick={() => speakText(msg.content)}
                        title="Listen to this explanation"
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#6366f1', padding: '2px 4px' }}
                      >
                        <Volume2 size={13} />
                      </button>
                    )}"""

new_msg_speaker = """                    {msg.role === 'tutor' && (
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
                    )}"""

assert old_msg_speaker in code, "old_msg_speaker not found"
code = code.replace(old_msg_speaker, new_msg_speaker, 1)

with open('frontend/src/pages/AITutorPage.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated frontend/src/pages/AITutorPage.tsx successfully")

