<<<<<<< HEAD
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getAssessments } from '../api/assessment';
import RiskBadge from '../components/RiskBadge';

const PAGE_SIZE = 10;
=======
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { getAssessments } from '../api/assessment';
import RiskBadge from '../components/RiskBadge';

const PAGE_SIZE = 5;
>>>>>>> 39f3ae3dcfd66e7238098d93c659d13d2826839f

const formatDate = (isoString) =>
  new Date(isoString).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

function HistoryPage() {
<<<<<<< HEAD
  const navigate = useNavigate();
  const [assessments, setAssessments] = useState([]);
  const [page, setPage] = useState(1);
=======
  const [page, setPage] = useState(1);
  const [items, setItems] = useState([]);
>>>>>>> 39f3ae3dcfd66e7238098d93c659d13d2826839f
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
<<<<<<< HEAD
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
=======
        if (!cancelled && response.success) {
          setItems(response.data?.items || []);
          setTotal(response.data?.total || 0);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.response?.data?.error?.message || 'Could not load your assessment history.');
        }
      } finally {
        if (!cancelled) setLoading(false);
>>>>>>> 39f3ae3dcfd66e7238098d93c659d13d2826839f
      }
    };

    fetchHistory();
    return () => {
      cancelled = true;
    };
  }, [page]);

<<<<<<< HEAD
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
=======
  const pageCount = useMemo(() => Math.max(1, Math.ceil(total / PAGE_SIZE)), [total]);

  return (
    <div className="container history-page">
      <div className="page-header history-header">
        <div>
          <h1 className="page-title">History</h1>
          <p className="text-muted">Review past oral health checks and treatment recommendations.</p>
        </div>
        <div className="history-meta">{total} assessments</div>
>>>>>>> 39f3ae3dcfd66e7238098d93c659d13d2826839f
      </div>

      {loading ? (
        <div className="history-empty history-empty--loading">
          <span className="spinner"></span>
          Loading assessment history...
        </div>
      ) : error ? (
        <div className="history-empty history-empty--error">{error}</div>
      ) : items.length === 0 ? (
        <div className="history-empty">No assessments yet. Start your first screening to see history here.</div>
      ) : (
        <>
          <div className="history-list">
            {items.map((assessment) => (
              <Link key={assessment.id} to={`/assessment/${assessment.id}/result`} state={{ assessment }} className="history-item">
                <div className="history-item-header">
                  <div>
                    <div className="history-date">{formatDate(assessment.created_at)}</div>
                    <div className="history-label">Assessment #{assessment.id.slice(0, 8)}</div>
                  </div>
                  <RiskBadge level={assessment.risk_level} size="sm" />
                </div>

                <div className="history-item-body">
                  <span>{(assessment.diagnoses || []).length} condition(s) detected</span>
                  <span>View details →</span>
                </div>
              </Link>
            ))}
          </div>

          <div className="history-pagination">
            <button type="button" className="btn-secondary" disabled={page === 1 || loading} onClick={() => setPage((p) => Math.max(1, p - 1))}>
              Previous
            </button>
            <span className="history-page-indicator">
              Page {page} of {pageCount}
            </span>
            <button type="button" className="btn-secondary" disabled={page >= pageCount || loading} onClick={() => setPage((p) => Math.min(pageCount, p + 1))}>
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default HistoryPage;
