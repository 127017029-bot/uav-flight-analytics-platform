import React, { useState } from 'react';
import './Settings.css';

/** Settings - Platform configuration and user preferences. */
const Settings = () => {
  const [notifications, setNotifications] = useState({
    alerts: true,
    maintenance: true,
    flightComplete: false,
    aiPredictions: true,
  });

  return (
    <div className="settings-page">
      <div className="page-header">
        <div>
          <h1>Settings</h1>
          <p className="page-subtitle">Platform configuration and preferences</p>
        </div>
      </div>

      <div className="settings-grid">
        {/* Profile */}
        <div className="settings-section card">
          <h3>👤 Profile</h3>
          <div className="settings-form">
            <div className="form-group">
              <label>Full Name</label>
              <input type="text" defaultValue="Riswan Ahmed" className="form-input" />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input type="email" defaultValue="riswan@uavplatform.com" className="form-input" />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Role</label>
                <select className="form-input">
                  <option>Fleet Manager</option>
                  <option>Pilot</option>
                  <option>Analyst</option>
                  <option>Admin</option>
                </select>
              </div>
              <div className="form-group">
                <label>Organization</label>
                <input type="text" defaultValue="UAV Analytics Corp" className="form-input" />
              </div>
            </div>
            <button className="btn-primary">Save Profile</button>
          </div>
        </div>

        {/* System */}
        <div className="settings-section card">
          <h3>⚙️ System Configuration</h3>
          <div className="settings-form">
            <div className="form-group">
              <label>API Endpoint</label>
              <input type="text" defaultValue="http://localhost:8000/api" className="form-input mono" />
            </div>
            <div className="form-group">
              <label>WebSocket URL</label>
              <input type="text" defaultValue="ws://localhost:8000/ws" className="form-input mono" />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Telemetry Refresh Rate</label>
                <select className="form-input">
                  <option>1 Hz</option>
                  <option>2 Hz</option>
                  <option>5 Hz</option>
                  <option>10 Hz</option>
                </select>
              </div>
              <div className="form-group">
                <label>Dashboard Refresh</label>
                <select className="form-input">
                  <option>5 seconds</option>
                  <option>10 seconds</option>
                  <option>30 seconds</option>
                  <option>1 minute</option>
                </select>
              </div>
            </div>
            <button className="btn-primary">Save Configuration</button>
          </div>
        </div>

        {/* Notifications */}
        <div className="settings-section card">
          <h3>🔔 Notifications</h3>
          <div className="toggle-list">
            {[
              { key: 'alerts', label: 'Critical Alerts', desc: 'Battery low, motor anomaly, GPS loss' },
              { key: 'maintenance', label: 'Maintenance Reminders', desc: 'Scheduled and predictive maintenance' },
              { key: 'flightComplete', label: 'Flight Completion', desc: 'Notify when flights complete' },
              { key: 'aiPredictions', label: 'AI Predictions', desc: 'ML model prediction alerts' },
            ].map(item => (
              <div key={item.key} className="toggle-item">
                <div className="toggle-info">
                  <span className="toggle-label">{item.label}</span>
                  <span className="toggle-desc">{item.desc}</span>
                </div>
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={notifications[item.key]}
                    onChange={() => setNotifications(prev => ({ ...prev, [item.key]: !prev[item.key] }))}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* About */}
        <div className="settings-section card">
          <h3>ℹ️ About</h3>
          <div className="about-info">
            <div className="about-row"><span>Platform</span><span>AeroGuard UAV Analytics</span></div>
            <div className="about-row"><span>Version</span><span className="mono">1.0.0</span></div>
            <div className="about-row"><span>Backend</span><span className="mono">Django 6.0 + DRF</span></div>
            <div className="about-row"><span>Frontend</span><span className="mono">React 19 + Vite 8</span></div>
            <div className="about-row"><span>Database</span><span className="mono">PostgreSQL 16</span></div>
            <div className="about-row"><span>ML Engine</span><span className="mono">scikit-learn 1.7</span></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
