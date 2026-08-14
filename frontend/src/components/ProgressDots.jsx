function ProgressDots({ total, current }) {
  return (
    <div className="live-dots">
      {Array.from({ length: total }).map((_, i) => (
        <span
          key={i}
          className={`live-dot ${i === current ? 'live-dot--current' : i < current ? 'live-dot--done' : ''}`}
        ></span>
      ))}
    </div>
  );
}

export default ProgressDots;
