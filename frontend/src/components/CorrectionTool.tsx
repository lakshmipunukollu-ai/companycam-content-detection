import { useState, type FormEvent } from 'react';
import { createCorrection } from '../api/corrections.ts';
import type { Detection } from '../types/index.ts';

interface Props {
  photoId: string;
  detection: Detection;
  onCorrectionSubmitted: () => void;
}

export default function CorrectionTool({ photoId, detection, onCorrectionSubmitted }: Props) {
  const [correctionType, setCorrectionType] = useState('label');
  const [correctedLabel, setCorrectedLabel] = useState(detection.label);
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      await createCorrection(photoId, {
        detection_id: detection.id,
        correction_type: correctionType,
        corrected_label: correctionType === 'label' ? correctedLabel : undefined,
        notes: notes || undefined,
      });
      onCorrectionSubmitted();
    } catch {
      setError('Failed to submit correction');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card correction-tool">
      <h3>Correct Detection</h3>
      <p className="muted">Original: <strong>{detection.label}</strong> ({(detection.confidence * 100).toFixed(1)}%)</p>

      {error && <div className="error-msg">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="corrType">Correction Type</label>
          <select id="corrType" value={correctionType} onChange={(e) => setCorrectionType(e.target.value)}>
            <option value="label">Fix Label</option>
            <option value="delete">Delete (False Positive)</option>
            <option value="bbox">Adjust Bounding Box</option>
          </select>
        </div>

        {correctionType === 'label' && (
          <div className="form-group">
            <label htmlFor="corrLabel">Corrected Label</label>
            <input
              id="corrLabel"
              type="text"
              value={correctedLabel}
              onChange={(e) => setCorrectedLabel(e.target.value)}
              required
            />
          </div>
        )}

        <div className="form-group">
          <label htmlFor="corrNotes">Notes (optional)</label>
          <textarea
            id="corrNotes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Explain the correction..."
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Submitting...' : 'Submit Correction'}
        </button>
      </form>
    </div>
  );
}
