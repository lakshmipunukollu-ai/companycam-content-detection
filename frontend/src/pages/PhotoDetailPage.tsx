import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getPhoto, getPhotoResults, analyzePhoto } from '../api/photos.ts';
import AnnotationViewer from '../components/AnnotationViewer.tsx';
import CorrectionTool from '../components/CorrectionTool.tsx';
import type { Photo, PhotoAnalysisResult, Detection } from '../types/index.ts';

export default function PhotoDetailPage() {
  const { photoId } = useParams<{ photoId: string }>();
  const [photo, setPhoto] = useState<Photo | null>(null);
  const [results, setResults] = useState<PhotoAnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [selectedDetection, setSelectedDetection] = useState<Detection | null>(null);

  const fetchData = async () => {
    if (!photoId) return;
    try {
      const p = await getPhoto(photoId);
      setPhoto(p);
      if (p.status === 'completed') {
        const r = await getPhotoResults(photoId);
        setResults(r);
      }
    } catch {
      setError('Failed to load photo');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [photoId]);

  const handleAnalyze = async () => {
    if (!photoId) return;
    setAnalyzing(true);
    setError('');
    try {
      const r = await analyzePhoto(photoId);
      setResults(r);
      setPhoto((prev) => prev ? { ...prev, status: 'completed' } : prev);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Analysis failed';
      setError(msg);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) return <div className="loading">Loading photo...</div>;
  if (!photo) return <div className="error-msg">Photo not found</div>;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to={`/projects/${photo.project_id}`} className="back-link">Back to Project</Link>
          <h1>{photo.filename}</h1>
          <p className="subtitle">Type: {photo.photo_type} | Status: {photo.status}</p>
        </div>
        {photo.status === 'pending' && (
          <button className="btn btn-primary" onClick={handleAnalyze} disabled={analyzing}>
            {analyzing ? 'Analyzing...' : 'Run Analysis'}
          </button>
        )}
      </div>

      {error && <div className="error-msg">{error}</div>}

      {results?.requires_human_review && (
        <div className="warning-msg">
          This photo has low-confidence detections that require human review.
        </div>
      )}

      <div className="photo-detail-layout">
        <div className="photo-viewer-section">
          <AnnotationViewer
            photo={photo}
            detections={results?.detections || []}
            selectedDetection={selectedDetection}
            onSelectDetection={setSelectedDetection}
          />
        </div>

        <div className="photo-sidebar">
          {results && (
            <>
              <div className="card">
                <h3>Detections ({results.detections.length})</h3>
                {results.detections.length === 0 && <p className="muted">No detections found</p>}
                <ul className="detection-list">
                  {results.detections.map((d) => (
                    <li
                      key={d.id}
                      className={`detection-item ${selectedDetection?.id === d.id ? 'selected' : ''}`}
                      onClick={() => setSelectedDetection(d)}
                    >
                      <span className="detection-label">{d.label}</span>
                      <span className="detection-confidence">{(d.confidence * 100).toFixed(1)}%</span>
                      <span className="detection-stage">{d.stage}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="card">
                <h3>Classifications ({results.classifications.length})</h3>
                {results.classifications.map((c) => (
                  <div key={c.id} className="classification-item">
                    <strong>{c.category}</strong>
                    {c.subcategory && <span> / {c.subcategory}</span>}
                    {c.description && <p>{c.description}</p>}
                    {c.quantity_estimate != null && (
                      <p>Quantity: {c.quantity_estimate} {c.unit || ''}</p>
                    )}
                    {c.severity && <p>Severity: <span className={`severity-${c.severity}`}>{c.severity}</span></p>}
                    <p className="muted">Confidence: {(c.confidence * 100).toFixed(1)}%</p>
                    {c.requires_review && <span className="badge badge-warning">Needs Review</span>}
                  </div>
                ))}
              </div>

              {results.damage_assessments.length > 0 && (
                <div className="card">
                  <h3>Damage Assessment</h3>
                  {results.damage_assessments.map((da) => (
                    <div key={da.id} className="damage-item">
                      <p><strong>Type:</strong> {da.damage_type.replace(/_/g, ' ')}</p>
                      <p><strong>Severity:</strong> <span className={`severity-${da.severity}`}>{da.severity}</span></p>
                      {da.affected_area_pct != null && <p><strong>Affected Area:</strong> {da.affected_area_pct}%</p>}
                      {da.repair_urgency && <p><strong>Repair Urgency:</strong> {da.repair_urgency}</p>}
                      {da.location_description && <p><strong>Location:</strong> {da.location_description}</p>}
                    </div>
                  ))}
                </div>
              )}

              {selectedDetection && (
                <CorrectionTool
                  photoId={photo.id}
                  detection={selectedDetection}
                  onCorrectionSubmitted={() => {
                    setSelectedDetection(null);
                    fetchData();
                  }}
                />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
