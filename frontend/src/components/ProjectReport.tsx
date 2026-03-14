import type { ProjectReport } from '../types/index.ts';

interface Props {
  report: ProjectReport;
}

export default function ProjectReportView({ report }: Props) {
  return (
    <div className="report">
      <div className="report-header">
        <h2>{report.project_name}</h2>
        <p className="muted">Total Photos: {report.total_photos}</p>
      </div>

      <div className="report-grid">
        <div className="card">
          <h3>Material Summary</h3>
          {report.material_summary.length === 0 ? (
            <p className="muted">No materials detected</p>
          ) : (
            <table className="report-table">
              <thead>
                <tr>
                  <th>Material</th>
                  <th>Count</th>
                  <th>Unit</th>
                </tr>
              </thead>
              <tbody>
                {report.material_summary.map((m, i) => (
                  <tr key={i}>
                    <td>{m.material.replace(/_/g, ' ')}</td>
                    <td>{m.total_count}</td>
                    <td>{m.unit || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="card">
          <h3>Damage Summary</h3>
          {report.damage_summary.length === 0 ? (
            <p className="muted">No damage detected</p>
          ) : (
            <table className="report-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Severity</th>
                  <th>Count</th>
                </tr>
              </thead>
              <tbody>
                {report.damage_summary.map((d, i) => (
                  <tr key={i}>
                    <td>{d.type.replace(/_/g, ' ')}</td>
                    <td><span className={`severity-${d.severity}`}>{d.severity}</span></td>
                    <td>{d.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="card">
          <h3>Detection Accuracy</h3>
          <div className="stats-grid">
            <div className="stat">
              <span className="stat-value">{report.correction_stats.total_detections}</span>
              <span className="stat-label">Total Detections</span>
            </div>
            <div className="stat">
              <span className="stat-value">{report.correction_stats.corrections_made}</span>
              <span className="stat-label">Corrections Made</span>
            </div>
            <div className="stat">
              <span className="stat-value">{(report.correction_stats.accuracy_rate * 100).toFixed(1)}%</span>
              <span className="stat-label">Accuracy Rate</span>
            </div>
          </div>
          <div className="accuracy-bar">
            <div
              className="accuracy-fill"
              style={{ width: `${report.correction_stats.accuracy_rate * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
