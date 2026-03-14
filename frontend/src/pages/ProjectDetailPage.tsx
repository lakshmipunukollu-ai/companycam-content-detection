import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getProject } from '../api/projects.ts';
import { listPhotos } from '../api/photos.ts';
import PhotoUpload from '../components/PhotoUpload.tsx';
import type { Project, Photo } from '../types/index.ts';

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchData = async () => {
    if (!projectId) return;
    try {
      const [proj, photoList] = await Promise.all([
        getProject(projectId),
        listPhotos(projectId),
      ]);
      setProject(proj);
      setPhotos(photoList);
    } catch {
      setError('Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [projectId]);

  if (loading) return <div className="loading">Loading project...</div>;
  if (!project) return <div className="error-msg">Project not found</div>;

  const statusColor = (s: string) => {
    switch (s) {
      case 'completed': return 'green';
      case 'analyzing': return 'orange';
      case 'failed': return 'red';
      default: return 'gray';
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/" className="back-link">Back to Projects</Link>
          <h1>{project.name}</h1>
          {project.description && <p className="subtitle">{project.description}</p>}
          {project.address && <p className="subtitle">Address: {project.address}</p>}
        </div>
        <Link to={`/projects/${projectId}/report`} className="btn btn-secondary">View Report</Link>
      </div>

      {error && <div className="error-msg">{error}</div>}

      <PhotoUpload projectId={projectId!} onUploaded={fetchData} />

      <h2>Photos ({photos.length})</h2>
      {photos.length === 0 ? (
        <div className="empty-state"><p>No photos uploaded yet. Upload your first photo above.</p></div>
      ) : (
        <div className="photo-grid">
          {photos.map((photo) => (
            <Link key={photo.id} to={`/photos/${photo.id}`} className="photo-card">
              <div className="photo-thumb">
                <img
                  src={`/uploads/${photo.filename}`}
                  alt={photo.filename}
                  onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                />
                <div className="photo-placeholder">{photo.filename}</div>
              </div>
              <div className="photo-info">
                <span className="photo-name">{photo.filename}</span>
                <span className="photo-type">{photo.photo_type}</span>
                <span className="photo-status" style={{ color: statusColor(photo.status) }}>
                  {photo.status}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
