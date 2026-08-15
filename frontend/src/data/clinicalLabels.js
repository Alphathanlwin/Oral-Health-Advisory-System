export const CONDITION_LABELS = {
  DENTAL_CAVITY: 'Dental Cavity',
  GINGIVITIS: 'Gingivitis',
  TOOTH_ABSCESS: 'Tooth Abscess',
  ENAMEL_EROSION: 'Enamel Erosion',
  CANKER_SORES: 'Canker Sores',
  TOOTH_SENSITIVITY: 'Tooth Sensitivity',
};

export const URGENCY_LABELS = {
  IMMEDIATE: 'Immediate',
  WITHIN_1_WEEK: 'Within 1 Week',
  WITHIN_1_MONTH: 'Within 1 Month',
  MONITOR_AT_HOME: 'Monitor at Home',
};

export const URGENT_LEVELS = new Set(['IMMEDIATE', 'WITHIN_1_WEEK']);
