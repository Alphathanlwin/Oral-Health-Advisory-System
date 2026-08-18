import { useEffect, useRef, useState } from 'react';
import { chatExplain } from '../api/chat';
import { speak, stopSpeaking } from '../utils/speech';

function extractErrorMessage(err) {
  return (
    err.response?.data?.error?.message ||
    err.response?.data?.detail ||
    "Dr. Ava's chat assistant is unavailable right now — please try again later."
  );
}

// Chat input on ResultPage (Phase 4): grounded strictly in this assessment's
// own data via /chat/explain. Dr. Ava optionally speaks each answer aloud —
// the speaker toggle lets the user turn that off without losing the chat.
function ChatPanel({ assessmentId }) {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [speakingIndex, setSpeakingIndex] = useState(null);
  const cancelRef = useRef(null);
  const listRef = useRef(null);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [messages, loading]);

  useEffect(
    () => () => {
      cancelRef.current?.cancel();
      stopSpeaking();
    },
    []
  );

  const handleSend = async () => {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    setError('');
    setQuestion('');
    setMessages((prev) => [...prev, { role: 'user', text: trimmed }]);
    setLoading(true);

    try {
      const response = await chatExplain(assessmentId, trimmed);
      const answer = response?.data?.answer || '';

      setMessages((prev) => {
        const next = [...prev, { role: 'assistant', text: answer }];
        if (voiceEnabled && answer) {
          const index = next.length - 1;
          cancelRef.current?.cancel();
          cancelRef.current = speak(answer, {
            onStart: () => setSpeakingIndex(index),
            onEnd: () => setSpeakingIndex((current) => (current === index ? null : current)),
          });
        }
        return next;
      });
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleVoice = () => {
    setVoiceEnabled((prev) => {
      const next = !prev;
      if (!next) {
        cancelRef.current?.cancel();
        stopSpeaking();
        setSpeakingIndex(null);
      }
      return next;
    });
  };

  return (
    <div className="chat-panel">
      <div className="chat-panel-header">
        <span className="chat-panel-title">Ask Dr. Ava about this result</span>
        <button
          type="button"
          className={`chat-voice-toggle ${voiceEnabled ? 'chat-voice-toggle--on' : ''}`}
          onClick={toggleVoice}
          aria-pressed={voiceEnabled}
          title={voiceEnabled ? 'Turn off spoken answers' : 'Turn on spoken answers'}
        >
          {voiceEnabled ? <SpeakerOnIcon /> : <SpeakerOffIcon />}
        </button>
      </div>
      <p className="chat-panel-hint">Answers are limited to this assessment's own results.</p>

      {messages.length > 0 && (
        <div className="chat-messages" ref={listRef}>
          {messages.map((message, i) => (
            <div key={i} className={`chat-message chat-message--${message.role}`}>
              {message.role === 'assistant' && speakingIndex === i && (
                <span className="chat-message-speaking">Dr. Ava is speaking…</span>
              )}
              <p>{message.text}</p>
            </div>
          ))}
          {loading && (
            <div className="chat-message chat-message--assistant chat-message--loading">
              <span className="spinner"></span>
              Dr. Ava is thinking...
            </div>
          )}
        </div>
      )}

      {error && <div className="form-error chat-panel-error">{error}</div>}

      <div className="chat-input-row">
        <textarea
          className="form-input chat-input"
          rows={1}
          placeholder="e.g. Why was I flagged for gingivitis?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          type="button"
          className="btn-primary chat-send-btn"
          onClick={handleSend}
          disabled={loading || !question.trim()}
        >
          {loading ? <span className="spinner"></span> : 'Send'}
        </button>
      </div>
    </div>
  );
}

function SpeakerOnIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M2 6h2.5L8 3v10L4.5 10H2V6z" fill="currentColor" />
      <path
        d="M10.5 5.5c1 .8 1 4.2 0 5M12.3 4c1.8 1.6 1.8 6.4 0 8"
        stroke="currentColor"
        strokeWidth="1.3"
        strokeLinecap="round"
      />
    </svg>
  );
}

function SpeakerOffIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M2 6h2.5L8 3v10L4.5 10H2V6z" fill="currentColor" />
      <path d="M10.5 5.5l4 5M14.5 5.5l-4 5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  );
}

export default ChatPanel;
