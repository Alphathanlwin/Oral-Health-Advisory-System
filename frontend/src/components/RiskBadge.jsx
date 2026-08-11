function RiskBadge({ level, size = 'md' }) {
  const normalized = (level || '').toUpperCase();

  return (
    <span className={`risk-badge risk-badge--${normalized.toLowerCase()} risk-badge--${size}`}>
      <span className="risk-badge-dot"></span>
      {normalized}
    </span>
  );
}

export default RiskBadge;
