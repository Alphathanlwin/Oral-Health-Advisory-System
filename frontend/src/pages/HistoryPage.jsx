import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getAssessments } from '../api/assessment';
import RiskBadge from '../components/RiskBadge';

const PAGE_SIZE = 10;

const formatDate = (isoString) =>
  new Date(isoString).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

function HistoryPage() {
  const navigate = useNavigate();
  const [assessments, setAssessments] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    const fetchHistory = async () => {
      setLoading(true);
      setError('');

      try {
        const response = await getAssessments(page, PAGE_SIZE);
        if (!cancelled && response.success && response.data) {
          setAssessments(response.data.items || []);
          setTotal(response.data.total || 0);
        }
      } catch {
        if (!cancelled) {
          setError('Could not load your history right now.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchHistory();
    return () => {
      cancelled = true;
    };
  }, [page]);

  const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="container history-page">
      <div className="page-header">
        <h1 className="page-title">Assessment History</h1>
        <p className="text-muted">Review your recent oral health checks.</p>
      </div>

      <div className="history-card">
        {loading && <div className="history-empty">Loading your assessments…</div>}

        {!loading && error && <div className="history-empty history-empty--error">{error}</div>}

        {!loading && !error && assessments.length === 0 && (
          <div className="history-empty">No assessments yet. Your history will appear here after your first check.</div>
        )}

        {!loading && !error && assessments.length > 0 && (
          <>
            <div className="history-table">
              <div className="history-table-header">
                <span>Date</span>
                <span>Risk</span>
                <span>Conditions</span>
              </div>

              {assessments.map((assessment) => (
                <button
                  key={assessment.id}
                  type="button"
                  className="history-row"
                  onClick={() => navigate(`/assessment/${assessment.id}/result`)}
                >
                  <span>{formatDate(assessment.created_at)}</span>
                  <RiskBadge level={assessment.risk_level} size="sm" />
                  <span>{(assessment.conditions_detected || []).length} detected</span>
                </button>
              ))}
            </div>

            <div className="history-pagination">
              <button type="button" className="btn-secondary" onClick={() => setPage((current) => Math.max(1, current - 1))} disabled={page === 1 || loading}>
                Previous
              </button>
              <span>
                Page {page} of {pageCount}
              </span>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setPage((current) => Math.min(pageCount, current + 1))}
                disabled={page >= pageCount || loading}
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>

      <div className="history-actions">
        <Link to="/" className="btn-secondary history-link">
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}

export default HistoryPage;
