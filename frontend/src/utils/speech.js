// Thin wrapper around the Web Speech API's SpeechSynthesis.
// Falls back to a timed no-op when the browser has no TTS support, so callers
// (talking-mouth animation, auto-advance timers) still get onStart/onEnd.

function pickVoice() {
  if (typeof window === 'undefined' || !window.speechSynthesis) return null;
  const voices = window.speechSynthesis.getVoices();
  return (
    voices.find((v) => /female|zira|samantha|susan|google us english/i.test(v.name)) ||
    voices.find((v) => v.lang?.startsWith('en')) ||
    voices[0] ||
    null
  );
}

export function speak(text, { onStart, onEnd, rate = 1, pitch = 1.05, volume = 1 } = {}) {
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

  const voice = pickVoice();
  if (voice) utterance.voice = voice;

  utterance.onstart = () => onStart?.();
  utterance.onend = () => onEnd?.();
  utterance.onerror = () => onEnd?.();

  window.speechSynthesis.speak(utterance);

  return { cancel: () => window.speechSynthesis.cancel() };
}

export function stopSpeaking() {
  if (typeof window !== 'undefined' && window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
}
