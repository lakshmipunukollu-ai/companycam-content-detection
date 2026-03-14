import { useState, useEffect, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { listProjects, createProject, deleteProject } from '../api/projects.ts';
import type { Project } from '../types/index.ts';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [address, setAddress] = useState('');
  const [error, setError] = useState('');

  const fetchProjects = async () => {
    try {
      const data = await listProjects();
      setProjects(data);
    } catch {
      setError('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchProjects(); }, []);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await createProject({ name, description: description || undefined, address: address || undefined });
      setShowCreate(false);
      setName('');
      setDescription('');
      setAddress('');
      fetchProjects();
    } catch {
      setError('Failed to create project');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this project?')) return;
    try {
      await deleteProject(id);
      fetchProjects();
    } catch {
      setError('Failed to delete project');
    }
  };

  if (loading) return <div className="loading">Loading projects...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Projects</h1>
        <button className="btn btn-primary" onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? 'Cancel' : '+ New Project'}
        </button>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {showCreate && (
        <div className="card create-form">
          <h3>Create New Project</h3>
          <form onSubmit={handleCreate}>
            <div className="form-group">
              <label htmlFor="projName">Project Name</label>
              <input id="projName" type="text" value={name} onChange={(e) => setName(e.target.value)} required placeholder="Smith Residence Roof" />
            </div>
            <div className="form-group">
              <label htmlFor="projDesc">Description</label>
              <textarea id="projDesc" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Project description..." />
            </div>
            <div className="form-group">
              <label htmlFor="projAddr">Address</label>
              <input id="projAddr" type="text" value={address} onChange={(e) => setAddress(e.target.value)} placeholder="123 Main St" />
            </div>
            <button type="submit" className="btn btn-primary">Create Project</button>
          </form>
        </div>
      )}

      {projects.length === 0 ? (
        <div className="empty-state">
          <p>No projects yet. Create your first project to get started.</p>
        </div>
      ) : (
        <div className="card-grid">
          {projects.map((p) => (
            <div key={p.id} className="card project-card">
              <div className="card-header">
                <Link to={`/projects/${p.id}`}><h3>{p.name}</h3></Link>
                <span className={`badge badge-${p.status}`}>{p.status}</span>
              </div>
              {p.description && <p className="card-desc">{p.description}</p>}
              {p.address && <p className="card-meta">Address: {p.address}</p>}
              <p className="card-meta">Created: {new Date(p.created_at).toLocaleDateString()}</p>
              <div className="card-actions">
                <Link to={`/projects/${p.id}`} className="btn btn-sm">View</Link>
                <Link to={`/projects/${p.id}/report`} className="btn btn-sm btn-secondary">Report</Link>
                <button className="btn btn-sm btn-danger" onClick={() => handleDelete(p.id)}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
