import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AiGuide from '../components/AiGuide';
import SymptomVoiceStep from '../components/SymptomVoiceStep';
import GuidedCapture from '../components/GuidedCapture';
import { createAssessment } from '../api/assessment';
import { buildResultSummary } from '../utils/resultSummary';
import { SYMPTOM_QUESTIONS } from '../data/symptomQuestions';
import { CAPTURE_ANGLES } from '../data/captureAngles';

const stripDataUrlPrefix = (dataUrl) => (dataUrl && dataUrl.includes(',') ? dataUrl.split(',')[1] : null);

function LiveScreeningPage() {
  const navigate = useNavigate();

  const [screen, setScreen] = useState('intro');
  const [symptoms, setSymptoms] = useState(null);
  const [photos, setPhotos] = useState(null);
  const [percent, setPercent] = useState(0);
  const [assessment, setAssessment] = useState(null);
  const [submitError, setSubmitError] = useState('');
  const analyzeTimer = useRef(null);

  // --- caption + pose per screen -------------------------------------------------
  let pose = 'idle';
  let caption = '';

  if (screen === 'intro') {
    pose = 'idle';
    caption = "Hi, I'm Dr. Ava. Let's do a quick smile check together.";
  } else if (screen === 'analyzing') {
    pose = 'processing';
    caption = 'Give me a moment while I take a look...';
  } else if (screen === 'reveal') {
    pose = 'reveal';
    caption = buildResultSummary(assessment);
  } else if (screen === 'error') {
    pose = 'sorry';
    caption = "Sorry, something went wrong while I was analyzing your smile. Let's try that again.";
  }

  // --- submit the real assessment once both symptoms + photos are collected ------
  useEffect(() => {
    if (screen !== 'analyzing' || !symptoms || !photos) return undefined;

    let cancelled = false;

    createAssessment({
      symptoms,
      photos: {
        front: stripDataUrlPrefix(photos.front),
        upper: stripDataUrlPrefix(photos.upper),
        lower: stripDataUrlPrefix(photos.lower),
      },
    })
      .then((response) => {
        if (cancelled) return;
        if (response.success && response.data) {
          setAssessment(response.data);
        } else {
          setSubmitError('Something went wrong while analyzing your smile.');
        }
      })
      .catch(() => {
        if (!cancelled) setSubmitError('Something went wrong while analyzing your smile.');
      });

    return () => {
      cancelled = true;
    };
  }, [screen, symptoms, photos]);

  // --- analyzing visual progress: climbs on its own, holds near-done until ------
  // the real API response actually lands (or fails)
  useEffect(() => {
    if (screen !== 'analyzing') return undefined;

    analyzeTimer.current = setInterval(() => {
      setPercent((p) => (p >= 96 ? p : p + 4));
    }, 90);

    return () => clearInterval(analyzeTimer.current);
  }, [screen]);

  useEffect(() => {
    if (screen !== 'analyzing' || (!assessment && !submitError)) return undefined;

    clearInterval(analyzeTimer.current);

    const timeout = setTimeout(() => {
      setPercent(100);
      setScreen(assessment ? 'reveal' : 'error');
    }, 350);

    return () => clearTimeout(timeout);
  }, [screen, assessment, submitError]);

  const handleExit = () => navigate('/');

  const handleStart = () => setScreen('ask_symptoms');

  const handleSymptomsComplete = (collected) => {
    setSymptoms(collected);
    setScreen('capture');
  };

  const handleCaptureComplete = (collected) => {
    setPhotos(collected);
    setScreen('analyzing');
  };

  const handleRetake = () => {
    setScreen('intro');
    setSymptoms(null);
    setPhotos(null);
    setPercent(0);
    setAssessment(null);
    setSubmitError('');
  };

  const handleViewResults = () => {
    navigate(`/assessment/${assessment.id}/result`, { state: { assessment } });
  };

  return (
    <div className="live-screening">
      <button type="button" className="live-exit" onClick={handleExit} aria-label="Exit live screening">
        <XIcon />
      </button>

      {screen === 'intro' && <IntroScreen pose={pose} caption={caption} onStart={handleStart} />}

      {screen === 'ask_symptoms' && <SymptomVoiceStep onComplete={handleSymptomsComplete} />}

      {screen === 'capture' && <GuidedCapture onComplete={handleCaptureComplete} />}

      {screen === 'analyzing' && <AnalyzingScreen pose={pose} caption={caption} percent={percent} photos={photos} />}

      {screen === 'reveal' && (
        <RevealScreen pose={pose} caption={caption} assessment={assessment} onViewResults={handleViewResults} onRetake={handleRetake} />
      )}

      {screen === 'error' && <ErrorScreen pose={pose} caption={caption} onRetry={handleRetake} onExit={handleExit} />}
    </div>
  );
}

function IntroScreen({ pose, caption, onStart }) {
  return (
    <div className="live-content live-content--center">
      <AiGuide state={pose} caption={caption} size="lg" layout="stage" />

      <div className="live-headline">
        <div className="live-eyebrow">Live AI Screening</div>
        <h1 className="live-title">Let&apos;s check your smile</h1>
      </div>

      <button type="button" className="live-btn-primary" onClick={onStart}>
        Start Smile Check
        <ArrowIcon />
      </button>

      <p className="live-footnote">Takes about 2 minutes · {SYMPTOM_QUESTIONS.length} questions · 3 photos</p>
    </div>
  );
}

function AnalyzingScreen({ pose, caption, percent, photos }) {
  const scanIndex = Math.min(2, Math.floor(percent / 34));

  return (
    <div className="live-content live-content--center">
      <AiGuide state={pose} caption={caption} size="md" layout="stage" />

      <h1 className="live-title live-title--sm">Reading your scans</h1>

      <div className="live-thumbs">
        {CAPTURE_ANGLES.map((angle, i) => {
          const status = i < scanIndex ? 'done' : i === scanIndex ? 'scanning' : 'queued';
          const src = photos?.[angle.id];
          return (
            <div className="live-thumb" key={angle.id}>
              <div className={`live-thumb-photo live-thumb-photo--${status}`}>
                {src && <img src={src} alt={angle.label} className="live-thumb-img" />}
                {status !== 'queued' && <div className="live-thumb-scanline"></div>}
              </div>
              <span className={`live-thumb-label ${status === 'queued' ? 'live-thumb-label--dim' : ''}`}>{angle.label}</span>
            </div>
          );
        })}
      </div>

      <div className="live-progress-block">
        <div className="live-progress-head">
          <span>Checking gum tissue</span>
          <span className="live-progress-percent">{percent}%</span>
        </div>
        <div className="live-track">
          <div className="live-track-fill" style={{ width: `${percent}%` }}></div>
        </div>
      </div>

      <p className="live-footnote">
        {Object.values(photos || {}).filter(Boolean).length} of {CAPTURE_ANGLES.length} photos captured
      </p>
    </div>
  );
}

function RevealScreen({ pose, caption, assessment, onViewResults, onRetake }) {
  const riskLevel = (assessment?.risk_level || 'LOW').toUpperCase();
  const diagnosisCount = assessment?.diagnoses?.length || 0;

  return (
    <div className="live-content live-content--center">
      <div className="live-reveal-stage">
        <AiGuide state={pose} caption={caption} size="md" layout="stage" />
        <div className={`live-risk-badge live-risk-badge--${riskLevel.toLowerCase()}`}>
          <ShieldIcon />
          {riskLevel} RISK
        </div>
      </div>

      <h1 className="live-title live-title--sm">Here&apos;s what I found</h1>

      <p className="live-footnote">
        {diagnosisCount === 0
          ? 'No specific conditions detected'
          : `${diagnosisCount} condition${diagnosisCount === 1 ? '' : 's'} detected`}
      </p>

      <button type="button" className="live-btn-primary" onClick={onViewResults}>
        View full results
        <ArrowIcon />
      </button>
      <button type="button" className="live-link-btn" onClick={onRetake}>
        Retake screening
      </button>
    </div>
  );
}

function ErrorScreen({ pose, caption, onRetry, onExit }) {
  return (
    <div className="live-content live-content--center">
      <AiGuide state={pose} caption={caption} size="md" layout="stage" />

      <h1 className="live-title live-title--sm">Let&apos;s try again</h1>

      <button type="button" className="live-btn-primary" onClick={onRetry}>
        Retry Smile Check
        <ArrowIcon />
      </button>
      <button type="button" className="live-link-btn" onClick={onExit}>
        Exit to dashboard
      </button>
    </div>
  );
}

function XIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M2 2l10 10M12 2L2 12" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

function ArrowIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M7 2.5l4.5 4.5L7 11.5M2 7h9.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function ShieldIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 3l7 3v6c0 4.5-3 8-7 9-4-1-7-4.5-7-9V6l7-3z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
      <path d="M9.5 12l1.8 1.8L15 10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default LiveScreeningPage;
