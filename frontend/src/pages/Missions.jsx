import React from 'react';
import StatusBadge from '../components/common/StatusBadge';
import './Missions.css';

/** Missions - Mission planning and management page. */
const Missions = () => {
  const mockMissions = [
    { id: 1, name: 'Mission Alpha', type: 'survey', drone: 'Eagle-1', status: 'completed', priority: 'high', distance: '8.2 km', date: '2026-06-18', waypoints: 12 },
    { id: 2, name: 'Mission Bravo', type: 'inspection', drone: 'Falcon-2', status: 'in_progress', priority: 'critical', distance: '3.5 km', date: '2026-06-20', waypoints: 8 },
    { id: 3, name: 'Mission Charlie', type: 'delivery', drone: 'Hawk-3', status: 'planned', priority: 'medium', distance: '12.1 km', date: '2026-06-22', waypoints: 4 },
    { id: 4, name: 'Mission Delta', type: 'surveillance', drone: 'Osprey-4', status: 'draft', priority: 'low', distance: '5.7 km', date: '2026-06-25', waypoints: 6 },
  ];

  const priorityColors = { low: '#64748b', medium: '#38bdf8', high: '#fbbf24', critical: '#f87171' };

  return (
    <div className="missions-page">
      <div className="page-header">
        <div>
          <h1>Mission Planning</h1>
          <p className="page-subtitle">Plan, manage, and track UAV missions</p>
        </div>
        <button className="btn-primary">+ Create Mission</button>
      </div>

      <div className="missions-stats">
        {[
          { label: 'Total Missions', value: '24', icon: '🗺️' },
          { label: 'Active', value: '2', icon: '▶️' },
          { label: 'Completed', value: '18', icon: '✅' },
          { label: 'Success Rate', value: '94%', icon: '📊' },
        ].map((s, i) => (
          <div key={i} className="stat-card card" style={{ animationDelay: `${i * 0.1}s` }}>
            <span className="stat-icon">{s.icon}</span>
            <span className="stat-value">{s.value}</span>
            <span className="stat-label">{s.label}</span>
          </div>
        ))}
      </div>

      <div className="missions-list">
        {mockMissions.map((m, i) => (
          <div key={m.id} className="mission-card card" style={{ animationDelay: `${(i + 4) * 0.08}s` }}>
            <div className="mission-header">
              <div className="mission-title-row">
                <h3>{m.name}</h3>
                <span className="priority-tag" style={{ background: `${priorityColors[m.priority]}20`, color: priorityColors[m.priority] }}>
                  {m.priority}
                </span>
              </div>
              <StatusBadge status={m.status === 'in_progress' ? 'active' : m.status === 'completed' ? 'healthy' : m.status === 'planned' ? 'warning' : 'offline'} />
            </div>
            <div className="mission-details">
              <div className="detail-item">
                <span className="detail-label">Type</span>
                <span className="detail-value">{m.type}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Drone</span>
                <span className="detail-value">{m.drone}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Distance</span>
                <span className="detail-value">{m.distance}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Waypoints</span>
                <span className="detail-value">{m.waypoints}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Date</span>
                <span className="detail-value">{m.date}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Missions;
