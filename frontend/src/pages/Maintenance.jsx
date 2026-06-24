import React from 'react';
import StatusBadge from '../components/common/StatusBadge';
import './Maintenance.css';

/** Maintenance - Predictive and scheduled maintenance management. */
const Maintenance = () => {
  const mockRecords = [
    { id: 1, drone: 'Eagle-1', type: 'predictive', component: 'Motor 3', title: 'Bearing Wear Detected', priority: 'high', status: 'pending', confidence: 0.89, scheduled: '2026-06-22', cost: '$120' },
    { id: 2, drone: 'Falcon-2', type: 'scheduled', component: 'Battery', title: 'Battery Cycle Maintenance', priority: 'medium', status: 'scheduled', confidence: null, scheduled: '2026-06-25', cost: '$85' },
    { id: 3, drone: 'Hawk-3', type: 'corrective', component: 'GPS Module', title: 'GPS Calibration Required', priority: 'critical', status: 'in_progress', confidence: null, scheduled: '2026-06-20', cost: '$200' },
    { id: 4, drone: 'Storm-10', type: 'predictive', component: 'ESC', title: 'ESC Temperature Anomaly', priority: 'high', status: 'pending', confidence: 0.76, scheduled: '2026-06-28', cost: '$150' },
    { id: 5, drone: 'Osprey-4', type: 'scheduled', component: 'Full System', title: 'Quarterly Inspection', priority: 'low', status: 'completed', confidence: null, scheduled: '2026-06-15', cost: '$350' },
  ];

  const priorityColors = { low: '#64748b', medium: '#38bdf8', high: '#fbbf24', critical: '#f87171' };
  const typeIcons = { predictive: '🧠', scheduled: '📅', corrective: '🔧', emergency: '🚨' };

  return (
    <div className="maintenance-page">
      <div className="page-header">
        <div>
          <h1>Maintenance</h1>
          <p className="page-subtitle">Predictive and scheduled maintenance tracking</p>
        </div>
        <button className="btn-primary">+ Schedule Maintenance</button>
      </div>

      <div className="maint-stats">
        {[
          { label: 'Pending', value: '3', color: 'var(--color-warning)' },
          { label: 'In Progress', value: '1', color: 'var(--color-accent)' },
          { label: 'Completed (30d)', value: '12', color: 'var(--color-success)' },
          { label: 'AI-Predicted', value: '5', color: 'var(--color-accent-2)' },
        ].map((s, i) => (
          <div key={i} className="maint-stat card" style={{ animationDelay: `${i * 0.1}s` }}>
            <span className="maint-stat-value" style={{ color: s.color }}>{s.value}</span>
            <span className="maint-stat-label">{s.label}</span>
          </div>
        ))}
      </div>

      <div className="maint-list">
        {mockRecords.map((r, i) => (
          <div key={r.id} className="maint-card card" style={{ animationDelay: `${(i + 4) * 0.08}s` }}>
            <div className="maint-card-left">
              <span className="maint-type-icon">{typeIcons[r.type]}</span>
              <div className="maint-card-info">
                <div className="maint-card-title-row">
                  <h3>{r.title}</h3>
                  <span className="priority-tag" style={{ background: `${priorityColors[r.priority]}20`, color: priorityColors[r.priority] }}>{r.priority}</span>
                </div>
                <div className="maint-meta">
                  <span>{r.drone}</span>
                  <span className="meta-sep">•</span>
                  <span>{r.component}</span>
                  <span className="meta-sep">•</span>
                  <span className="maint-type-label">{r.type}</span>
                  {r.confidence && (
                    <>
                      <span className="meta-sep">•</span>
                      <span className="ai-confidence">AI: {(r.confidence * 100).toFixed(0)}%</span>
                    </>
                  )}
                </div>
              </div>
            </div>
            <div className="maint-card-right">
              <div className="maint-detail">
                <span className="maint-detail-label">Scheduled</span>
                <span>{r.scheduled}</span>
              </div>
              <div className="maint-detail">
                <span className="maint-detail-label">Est. Cost</span>
                <span>{r.cost}</span>
              </div>
              <StatusBadge status={r.status === 'completed' ? 'healthy' : r.status === 'in_progress' ? 'active' : r.status === 'pending' ? 'warning' : 'maintenance'} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Maintenance;
