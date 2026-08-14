import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AiGuide from '../components/AiGuide';
import ProgressDots from '../components/ProgressDots';
import SymptomVoiceStep from '../components/SymptomVoiceStep';
import { SYMPTOM_QUESTIONS } from '../data/symptomQuestions';

const CAPTURE_ANGLES = [
  { id: 'capture_front', label: 'Front bite', hint: 'Bite together gently and fill the outline', caption: 'Smile wide so I can see your front teeth.', shape: 'bite' },
  { id: 'capture_upper', label: 'Upper arch', hint: 'Open wide and fill the arch outline', caption: 'Tilt your head back and open wide — I need the upper arch.', shape: 'upper' },
  { id: 'capture_lower', label: 'Lower arch', hint: 'Relax your tongue and fill the arch outline', caption: 'Last one — look down and open, so I can see the lower teeth.', shape: 'lower' },
];

const RESULT = {
  riskLevel: 'medium',
  score: 62,
  summary:
    "I spotted early gum inflammation and some plaque along the gumline. Nothing urgent — but worth acting on soon.",
};

function LiveScreeningPage() {
  const navigate = useNavigate();

  const [screen, setScreen] = useState('intro');
  const [symptoms, setSymptoms] = useState(null);
  const [captured, setCaptured] = useState([false, false, false]);
  const [flash, setFlash] = useState(false);
  const [percent, setPercent] = useState(0);
  const analyzeTimer = useRef(null);

  const captureIndex = CAPTURE_ANGLES.findIndex((c) => c.id === screen);

  // --- caption + pose per screen -------------------------------------------------
  let pose = 'idle';
  let caption = '';

  if (screen === 'intro') {
    pose = 'idle';
    caption = "Hi, I'm Dr. Ava. Let's do a quick smile check together.";
  } else if (captureIndex !== -1) {
    pose = 'look_here';
    caption = CAPTURE_ANGLES[captureIndex].caption;
  } else if (screen === 'analyzing') {
    pose = 'processing';
    caption = 'Give me a moment while I take a look...';
  } else if (screen === 'reveal') {
    pose = 'reveal';
    caption = RESULT.summary;
  }

  // Collected here so the exact payload shape (matching NewAssessmentPage's
  // symptoms{}) can be inspected until a later phase wires it to the API.
  useEffect(() => {
    if (symptoms) console.info('[LiveScreening] collected symptoms', symptoms);
  }, [symptoms]);

  // --- analyzing auto-progress ----------------------------------------------------
  useEffect(() => {
    if (screen !== 'analyzing') return undefined;

    analyzeTimer.current = setInterval(() => {
      setPercent((p) => {
        if (p >= 100) {
          clearInterval(analyzeTimer.current);
          setTimeout(() => setScreen('reveal'), 350);
          return 100;
        }
        return p + 4;
      });
    }, 90);

    return () => clearInterval(analyzeTimer.current);
  }, [screen]);

  const handleExit = () => navigate('/');

  const handleStart = () => setScreen('ask_symptoms');

  const handleSymptomsComplete = (collected) => {
    setSymptoms(collected);
    setScreen('capture_front');
  };

  const handleCapture = () => {
    setFlash(true);
    setTimeout(() => setFlash(false), 220);
    setTimeout(() => {
      const next = [...captured];
      next[captureIndex] = true;
      setCaptured(next);
      if (captureIndex < CAPTURE_ANGLES.length - 1) {
        setScreen(CAPTURE_ANGLES[captureIndex + 1].id);
      } else {
        setScreen('analyzing');
      }
    }, 220);
  };

  const handleRetake = () => {
    setScreen('intro');
    setSymptoms(null);
    setCaptured([false, false, false]);
    setPercent(0);
  };

  return (
    <div className="live-screening">
      <button type="button" className="live-exit" onClick={handleExit} aria-label="Exit live screening">
        <XIcon />
      </button>

      {screen === 'intro' && <IntroScreen pose={pose} caption={caption} onStart={handleStart} />}

      {screen === 'ask_symptoms' && <SymptomVoiceStep onComplete={handleSymptomsComplete} />}

      {captureIndex !== -1 && (
        <CaptureScreen
          pose={pose}
          caption={caption}
          angle={CAPTURE_ANGLES[captureIndex]}
          index={captureIndex}
          total={CAPTURE_ANGLES.length}
          flash={flash}
          onCapture={handleCapture}
        />
      )}

      {screen === 'analyzing' && (
        <AnalyzingScreen pose={pose} caption={caption} percent={percent} captured={captured} />
      )}

      {screen === 'reveal' && (
        <RevealScreen pose={pose} caption={caption} onDone={() => navigate('/')} onRetake={handleRetake} />
      )}
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

function CaptureScreen({ pose, caption, angle, index, total, flash, onCapture }) {
  return (
    <div className="live-content live-content--flush">
      <div className="live-camera">
        <div className={`live-camera-flash ${flash ? 'live-camera-flash--active' : ''}`}></div>

        <div className="live-camera-top">
          <span className="live-angle-chip">
            <CameraIcon />
            {angle.label} · {index + 1} of {total}
          </span>
        </div>

        <MouthGuide shape={angle.shape} />
        <p className="live-guide-hint">{angle.hint}</p>

        <div className="live-ava-float">
          <AiGuide state={pose} caption={caption} size="sm" layout="float" />
        </div>
      </div>

      <div className="live-capture-controls">
        <ProgressDots total={total} current={index} />
        <div className="live-capture-row">
          <div className="live-capture-side" aria-hidden="true">
            <ImageIcon />
          </div>
          <button type="button" className="live-shutter" onClick={onCapture} aria-label="Capture photo">
            <span className="live-shutter-core"></span>
          </button>
          <div className="live-capture-side" aria-hidden="true">
            <RefreshIcon />
          </div>
        </div>
        <p className="live-capture-hint">Tap to capture · Hold steady</p>
      </div>
    </div>
  );
}

function AnalyzingScreen({ pose, caption, percent, captured }) {
  const scanIndex = Math.min(2, Math.floor(percent / 34));

  return (
    <div className="live-content live-content--center">
      <AiGuide state={pose} caption={caption} size="md" layout="stage" />

      <h1 className="live-title live-title--sm">Reading your scans</h1>

      <div className="live-thumbs">
        {CAPTURE_ANGLES.map((angle, i) => {
          const status = i < scanIndex ? 'done' : i === scanIndex ? 'scanning' : 'queued';
          return (
            <div className="live-thumb" key={angle.id}>
              <div className={`live-thumb-photo live-thumb-photo--${status}`}>
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

      <p className="live-footnote">{captured.filter(Boolean).length} of 3 photos captured</p>
    </div>
  );
}

function RevealScreen({ pose, caption, onDone, onRetake }) {
  return (
    <div className="live-content live-content--center">
      <div className="live-reveal-stage">
        <AiGuide state={pose} caption={caption} size="md" layout="stage" />
        <div className="live-risk-badge">
          <ShieldIcon />
          {RESULT.riskLevel.toUpperCase()} RISK
        </div>
      </div>

      <h1 className="live-title live-title--sm">Here&apos;s what I found</h1>

      <div className="live-meter">
        <div className="live-meter-head">
          <span>Smile score</span>
          <span className="live-meter-score">{RESULT.score} / 100</span>
        </div>
        <div className="live-meter-segments">
          <span className="live-segment live-segment--low"></span>
          <span className="live-segment live-segment--medium"></span>
          <span className="live-segment live-segment--empty"></span>
        </div>
        <div className="live-meter-legend">
          <span>Low</span>
          <span className="live-meter-legend--active">Medium</span>
          <span>High</span>
        </div>
      </div>

      <button type="button" className="live-btn-primary" onClick={onDone}>
        View full results
        <ArrowIcon />
      </button>
      <button type="button" className="live-link-btn" onClick={onRetake}>
        Retake screening
      </button>
    </div>
  );
}

function MouthGuide({ shape }) {
  const path =
    shape === 'upper'
      ? 'M12 88 C12 26 66 4 110 4 C154 4 208 26 208 88'
      : shape === 'lower'
      ? 'M12 4 C12 66 66 88 110 88 C154 88 208 66 208 4'
      : 'M6 44 C36 8 184 8 214 44 C184 104 36 104 6 44 Z';

  return (
    <svg className="live-mouth-guide" viewBox="0 0 220 108" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d={path} stroke="#0ea5e9" strokeWidth="2.5" strokeLinejoin="round" />
      {[
        [8, 8, 0, 0],
        [198, 8, 1, 0],
        [8, 84, 0, 1],
        [198, 84, 1, 1],
      ].map(([x, y, fx, fy], i) => (
        <path
          key={i}
          d="M0 16 L0 4 Q0 0 4 0 L16 0"
          stroke="#f1f5f9cc"
          strokeWidth="2.5"
          strokeLinecap="round"
          transform={`translate(${x} ${y}) scale(${fx ? -1 : 1} ${fy ? -1 : 1})`}
        />
      ))}
    </svg>
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

function CameraIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 8a2 2 0 0 1 2-2h2l1.5-2h7L17 6h2a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
      <circle cx="12" cy="13" r="3.5" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

function ImageIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="8.5" cy="9.5" r="1.5" stroke="currentColor" strokeWidth="1.5" />
      <path d="M21 15l-5-5-9 9" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    </svg>
  );
}

function RefreshIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 10a9 9 0 0 1 15.3-5.3L21 7M21 4v3.5h-3.5M21 14a9 9 0 0 1-15.3 5.3L3 17M3 20v-3.5h3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
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
