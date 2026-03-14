import { useState, useRef, type DragEvent, type ChangeEvent } from 'react';
import { uploadPhoto, analyzePhoto } from '../api/photos.ts';

interface Props {
  projectId: string;
  onUploaded: () => void;
}

export default function PhotoUpload({ projectId, onUploaded }: Props) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [photoType, setPhotoType] = useState('general');
  const [autoAnalyze, setAutoAnalyze] = useState(true);
  const [status, setStatus] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    setStatus('');

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      try {
        setStatus(`Uploading ${file.name}...`);
        const photo = await uploadPhoto(file, projectId, photoType);
        if (autoAnalyze) {
          setStatus(`Analyzing ${file.name}...`);
          await analyzePhoto(photo.id);
        }
        setStatus(`${file.name} uploaded successfully`);
      } catch {
        setStatus(`Failed to upload ${file.name}`);
      }
    }

    setUploading(false);
    onUploaded();
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => setDragging(false);

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="upload-section">
      <div className="upload-controls">
        <div className="form-group form-inline">
          <label htmlFor="photoType">Photo Type:</label>
          <select id="photoType" value={photoType} onChange={(e) => setPhotoType(e.target.value)}>
            <option value="general">General</option>
            <option value="roof">Roof</option>
            <option value="delivery">Delivery</option>
            <option value="materials">Materials</option>
          </select>
        </div>
        <label className="checkbox-label">
          <input type="checkbox" checked={autoAnalyze} onChange={(e) => setAutoAnalyze(e.target.checked)} />
          Auto-analyze after upload
        </label>
      </div>

      <div
        className={`dropzone ${dragging ? 'dragging' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        {uploading ? (
          <p>{status}</p>
        ) : (
          <>
            <p className="dropzone-text">Drop photos here or click to browse</p>
            <p className="dropzone-hint">Supports JPG, PNG images</p>
          </>
        )}
      </div>
    </div>
  );
}
