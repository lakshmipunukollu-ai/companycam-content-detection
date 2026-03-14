import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getProjectReport } from '../api/reports.ts';
import ProjectReportView from '../components/ProjectReport.tsx';
import type { ProjectReport } from '../types/index.ts';

export default function ReportPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [report, setReport] = useState<ProjectReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!projectId) return;
    getProjectReport(projectId)
      .then(setReport)
      .catch(() => setError('Failed to load report'))
      .finally(() => setLoading(false));
  }, [projectId]);

  if (loading) return <div className="loading">Loading report...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to={`/projects/${projectId}`} className="back-link">Back to Project</Link>
          <h1>Project Report</h1>
        </div>
      </div>
      {error && <div className="error-msg">{error}</div>}
      {report && <ProjectReportView report={report} />}
    </div>
  );
}
