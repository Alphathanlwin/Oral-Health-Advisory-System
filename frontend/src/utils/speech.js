// Dr. Ava's voice. Tries the real neural TTS backend first (ElevenLabs, via
// POST /api/v1/tts) and falls back to the browser's built-in SpeechSynthesis
// if that's unavailable (no key configured server-side, network error, etc.)
// — callers only ever see the same onStart/onEnd contract either way.
import apiClient from '../api/auth';

let currentAudio = null;

function pickSystemVoice() {
  if (typeof window === 'undefined' || !window.speechSynthesis) return null;
  const voices = window.speechSynthesis.getVoices();
  return (
    voices.find((v) => /female|zira|samantha|susan|google us english/i.test(v.name)) ||
    voices.find((v) => v.lang?.startsWith('en')) ||
    voices[0] ||
    null
  );
}

function speakWithSystemVoice(text, { onStart, onEnd, rate, pitch, volume }) {
  const hasSpeech = typeof window !== 'undefined' && 'speechSynthesis' in window;

  if (!hasSpeech || !text) {
    onStart?.();
    const duration = Math.max(900, (text || '').split(/\s+/).length * 260);
    const timer = setTimeout(() => onEnd?.(), duration);
    return { cancel: () => clearTimeout(timer) };
  }

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = rate;
  utterance.pitch = pitch;
  utterance.volume = volume;

  const voice = pickSystemVoice();
  if (voice) utterance.voice = voice;

  utterance.onstart = () => onStart?.();
  utterance.onend = () => onEnd?.();
  utterance.onerror = () => onEnd?.();

  window.speechSynthesis.speak(utterance);

  return { cancel: () => window.speechSynthesis.cancel() };
}

export function speak(text, { onStart, onEnd, rate = 1, pitch = 1.05, volume = 1 } = {}) {
  if (!text) {
    onStart?.();
    onEnd?.();
    return { cancel: () => {} };
  }

  let cancelled = false;
  let fallbackHandle = null;

  apiClient
    .post('/tts/', { text }, { responseType: 'blob' })
    .then((response) => {
      if (cancelled) return;

      const url = URL.createObjectURL(response.data);
      const audio = new Audio(url);
      audio.volume = volume;
      currentAudio = audio;

      const cleanup = () => {
        URL.revokeObjectURL(url);
        if (currentAudio === audio) currentAudio = null;
      };

      audio.onplay = () => onStart?.();
      audio.onended = () => {
        onEnd?.();
        cleanup();
      };
      audio.onerror = () => {
        onEnd?.();
        cleanup();
      };

      audio.play().catch(() => {
        onEnd?.();
        cleanup();
      });
    })
    .catch(() => {
      if (!cancelled) fallbackHandle = speakWithSystemVoice(text, { onStart, onEnd, rate, pitch, volume });
    });

  return {
    cancel: () => {
      cancelled = true;
      currentAudio?.pause();
      currentAudio = null;
      fallbackHandle?.cancel();
      if (typeof window !== 'undefined' && window.speechSynthesis) window.speechSynthesis.cancel();
    },
  };
}

export function stopSpeaking() {
  currentAudio?.pause();
  currentAudio = null;
  if (typeof window !== 'undefined' && window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
}
