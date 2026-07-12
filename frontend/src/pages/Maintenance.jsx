import React, { useState, useEffect } from 'react';
import StatusBadge from '../components/common/StatusBadge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { AlertTriangle } from 'lucide-react';
import { listMaintenance } from '../api/endpoints';
import './Maintenance.css';

/** Maintenance - Predictive and scheduled maintenance management. */
const Maintenance = () => {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadMaintenanceData = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await listMaintenance();
      const mappedRecords = (data || []).map((r) => ({
        id: r.id,
        drone: r.drone_name || `Drone ${r.drone}`,
        type: r.maintenance_type,
        component: r.component_display || r.component,
        title: r.title,
        priority: r.priority,
        status: r.status,
        confidence: r.confidence_score,
        scheduled: r.scheduled_date ? r.scheduled_date.split('T')[0] : 'N/A',
        cost: r.cost_estimate ? `$${Math.round(r.cost_estimate)}` : '$0',
      }));
      setRecords(mappedRecords);
    } catch (err) {
      console.error('Failed to load maintenance records:', err);
      setError(err.message || 'Failed to fetch maintenance registry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMaintenanceData();
  }, []);

  const priorityColors = { low: '#64748b', medium: '#38bdf8', high: '#fbbf24', critical: '#f87171' };
  const typeIcons = { predictive: '🧠', scheduled: '📅', corrective: '🔧', emergency: '🚨' };

  if (loading) {
    return (
      <div className="page-loading" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', gap: 'var(--space-4)' }}>
        <LoadingSpinner size={40} />
        <span style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-base)' }}>Loading maintenance scheduling database...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-error card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '350px', gap: 'var(--space-4)', padding: 'var(--space-8)', textAlign: 'center', border: '1px solid var(--color-danger-border)', background: 'var(--color-danger-bg)' }}>
        <AlertTriangle size={48} style={{ color: 'var(--color-danger)' }} />
        <h3 style={{ color: 'var(--color-text-primary)' }}>Failed to Load Maintenance</h3>
        <p style={{ color: 'var(--color-text-secondary)', maxWidth: '450px' }}>{error}</p>
        <button className="btn btn-primary" onClick={loadMaintenanceData} style={{ marginTop: 'var(--space-2)' }}>Retry Connection</button>
      </div>
    );
  }

  // Calculate stats dynamically from data
  const pendingCount = records.filter(r => r.status === 'pending').length;
  const inProgressCount = records.filter(r => r.status === 'in_progress').length;
  const completedCount = records.filter(r => r.status === 'completed').length;
  const aiPredictedCount = records.filter(r => r.type === 'predictive').length;

  const maintStats = [
    { label: 'Pending', value: pendingCount.toString(), color: 'var(--color-warning)' },
    { label: 'In Progress', value: inProgressCount.toString(), color: 'var(--color-accent)' },
    { label: 'Completed', value: completedCount.toString(), color: 'var(--color-success)' },
    { label: 'AI-Predicted', value: aiPredictedCount.toString(), color: 'var(--color-accent-2)' },
  ];

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
        {maintStats.map((s, i) => (
          <div key={i} className="maint-stat card" style={{ animationDelay: `${i * 0.1}s` }}>
            <span className="maint-stat-value" style={{ color: s.color }}>{s.value}</span>
            <span className="maint-stat-label">{s.label}</span>
          </div>
        ))}
      </div>

      {records.length === 0 ? (
        <div className="page-empty card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '250px', gap: 'var(--space-2)', padding: 'var(--space-8)', textAlign: 'center' }}>
          <span style={{ fontSize: '36px' }}>🔧</span>
          <h3 style={{ color: 'var(--color-text-primary)', marginTop: 'var(--space-2)' }}>No Maintenance Orders</h3>
          <p style={{ color: 'var(--color-text-secondary)', maxWidth: '400px' }}>Your fleet is in pristine condition! No scheduled or corrective work orders found.</p>
        </div>
      ) : (
        <div className="maint-list">
          {records.map((r, i) => (
            <div key={r.id} className="maint-card card" style={{ animationDelay: `${(i + 4) * 0.08}s` }}>
              <div className="maint-card-left">
                <span className="maint-type-icon">{typeIcons[r.type] || '🔧'}</span>
                <div className="maint-card-info">
                  <div className="maint-card-title-row">
                    <h3>{r.title}</h3>
                    <span className="priority-tag" style={{ background: `${priorityColors[r.priority] || '#64748b'}20`, color: priorityColors[r.priority] || '#64748b' }}>{r.priority}</span>
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
      )}
    </div>
  );
};

export default Maintenance;
