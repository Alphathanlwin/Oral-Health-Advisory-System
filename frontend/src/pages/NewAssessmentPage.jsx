import { useState, Fragment } from 'react';
import { useNavigate } from 'react-router-dom';
import { createAssessment } from '../api/assessment';
import SymptomToggle from '../components/SymptomToggle';
import PhotoUpload from '../components/PhotoUpload';

const STEPS = [
  {
    id: 1,
    label: 'Pain & Sensitivity',
    title: 'Pain & Sensitivity',
    description: "Let us know about any pain or sensitivity you've been experiencing.",
    symptoms: [
      { key: 'cold_sensitivity', label: 'Cold sensitivity', hint: 'Pain when drinking cold liquids' },
      { key: 'hot_sensitivity', label: 'Hot sensitivity', hint: 'Pain when drinking hot liquids' },
      { key: 'pressure_pain', label: 'Pain when biting', hint: 'Pain when biting or chewing' },
      { key: 'spontaneous_pain', label: 'Spontaneous pain', hint: 'Pain without any trigger' },
    ],
  },
  {
    id: 2,
    label: 'Gum & Appearance',
    title: 'Gum & Appearance',
    description: 'Tell us about your gums and any visible spots, patches or discoloration you have noticed.',
    symptoms: [
      { key: 'bleeding_gums', label: 'Bleeding gums', hint: 'Slight bleeding when brushing' },
      { key: 'swollen_gums', label: 'Swollen gums', hint: 'Puffy or tender gum tissue' },
      { key: 'receding_gums', label: 'Receding gums', hint: 'Gums pulling away from teeth' },
      { key: 'black_spot', label: 'Black or brown spot', hint: 'Visible dark spot on a tooth' },
      { key: 'white_spot', label: 'White spot or patch', hint: 'Chalky white area on enamel' },
      { key: 'yellow_staining', label: 'Yellow staining', hint: 'Surface discoloration' },
    ],
  },
  {
    id: 3,
    label: 'Mouth & Habits',
    title: 'Mouth & Habits',
    description: 'Tell us about your breath, any sores, and how your teeth feel.',
    symptoms: [
      { key: 'bad_breath', label: 'Bad breath', hint: 'Persistent bad breath' },
      { key: 'dry_mouth', label: 'Dry mouth', hint: 'Mouth feels dry most of the time' },
      { key: 'mouth_ulcer', label: 'Mouth ulcer', hint: 'Sore lesion inside mouth' },
      { key: 'burning_sensation', label: 'Burning sensation', hint: 'Burning feeling in mouth' },
      { key: 'loose_tooth', label: 'Loose tooth', hint: 'Tooth feels loose' },
      { key: 'broken_tooth', label: 'Broken tooth', hint: 'Visible crack or broken piece' },
    ],
  },
  {
    id: 4,
    label: 'Hygiene & Photo',
    title: 'Hygiene & Photo',
    description: 'Tell us about your daily hygiene habits. Photo upload is optional.',
    symptoms: [
      { key: 'brushes_twice_daily', label: 'Brushes twice daily', hint: 'Brushes at least twice per day' },
      { key: 'uses_floss', label: 'Uses floss', hint: 'Uses dental floss regularly' },
      { key: 'sugary_diet', label: 'Sugary diet', hint: 'High sugar intake in daily diet' },
      { key: 'acid_exposure', label: 'Acid exposure', hint: 'Frequent consumption of acidic drinks' },
    ],
  },
];

const initialSymptoms = STEPS.reduce((acc, step) => {
  step.symptoms.forEach((s) => {
    acc[s.key] = false;
  });
  return acc;
}, {});

function NewAssessmentPage() {
  const [stepIndex, setStepIndex] = useState(0);
  const [symptoms, setSymptoms] = useState(initialSymptoms);
  const [photo, setPhoto] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const step = STEPS[stepIndex];
  const stepNumber = stepIndex + 1;
  const isFirstStep = stepIndex === 0;
  const isLastStep = stepIndex === STEPS.length - 1;
  const progressPercent = (stepNumber / STEPS.length) * 100;
  const yesCount = step.symptoms.filter((s) => symptoms[s.key]).length;

  const handleToggle = (key, value) => {
    setSymptoms((prev) => ({ ...prev, [key]: value }));
  };

  const goBack = () => {
    setError('');
    setStepIndex((i) => Math.max(0, i - 1));
  };

  const goNext = () => {
    setError('');
    setStepIndex((i) => Math.min(STEPS.length - 1, i + 1));
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError('');

    try {
      const photoBase64 = photo && photo.includes(',') ? photo.split(',')[1] : null;
      const response = await createAssessment({ symptoms, photo_base64: photoBase64 });
      if (response.success && response.data) {
        navigate(`/assessment/${response.data.id}/result`);
      }
    } catch (err) {
      const message =
        err.response?.data?.error?.message ||
        err.response?.data?.detail ||
        'Could not submit your assessment. Please try again.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="container assessment-page">
      <div className="stepper">
        {STEPS.map((s, idx) => (
          <Fragment key={s.id}>
            <div className="stepper-step">
              <div
                className={`stepper-circle ${
                  idx < stepIndex ? 'stepper-circle--done' : idx === stepIndex ? 'stepper-circle--current' : 'stepper-circle--pending'
                }`}
              >
                {idx < stepIndex ? <CheckIcon /> : <span>{s.id}</span>}
              </div>
              <div className={`stepper-label ${idx <= stepIndex ? 'stepper-label--active' : ''}`}>{s.label}</div>
            </div>
            {idx < STEPS.length - 1 && (
              <div className={`stepper-connector ${idx < stepIndex ? 'stepper-connector--done' : ''}`}></div>
            )}
          </Fragment>
        ))}
      </div>

      <div className="progress-bar">
        <div className="progress-bar-fill" style={{ width: `${progressPercent}%` }}></div>
      </div>

      <div className="step-header">
        <div className="step-count">
          STEP {stepNumber} OF {STEPS.length}
        </div>
        <h1 className="step-title">{step.title}</h1>
        <p className="step-desc">{step.description}</p>
      </div>

      <div className="symptom-grid">
        {step.symptoms.map((s) => (
          <SymptomToggle
            key={s.key}
            label={s.label}
            hint={s.hint}
            value={symptoms[s.key]}
            onChange={(value) => handleToggle(s.key, value)}
          />
        ))}
      </div>

      {isLastStep && <PhotoUpload value={photo} onChange={setPhoto} />}

      {error && <div className="form-error assessment-error">{error}</div>}

      <div className="assessment-footer">
        {!isFirstStep && (
          <button type="button" className="step-nav-btn step-nav-btn--back" onClick={goBack} disabled={submitting}>
            <ArrowLeftIcon />
            Back
          </button>
        )}

        <div className="assessment-footer-spacer"></div>

        <div className="assessment-hint">
          {yesCount} of {step.symptoms.length} marked yes
        </div>

        {isLastStep ? (
          <button type="button" className="step-nav-btn step-nav-btn--next" onClick={handleSubmit} disabled={submitting}>
            {submitting ? (
              <>
                <span className="spinner"></span>
                Submitting...
              </>
            ) : (
              'Submit Assessment'
            )}
          </button>
        ) : (
          <button type="button" className="step-nav-btn step-nav-btn--next" onClick={goNext} disabled={submitting}>
            Next Step
            <ArrowRightIcon />
          </button>
        )}
      </div>
    </div>
  );
}

function CheckIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M2.5 7.5l3 3 6-6.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function ArrowLeftIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M7 11.5L2.5 7 7 2.5M2.5 7h9"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ArrowRightIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M7 2.5l4.5 4.5L7 11.5M2 7h9.5"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default NewAssessmentPage;
